"""ARENA-V3-COMPILED — the paper's board from the interventions that survived (registered 2026-09-14)

  python tools/analysis/arena_v3_compiled.py --judge [--pilot N] [--workers 8]
  python tools/analysis/arena_v3_compiled.py --analyze

Supersedes the withdrawn ARENA-V3 (18.3k calls to deploy the RK-1b data card). Three boards, one judge
(Mistral-Large-3, the x12 MAIN judge):
  A  ARENA-V2 as published: all 9,142 dual-order verdicts
  B  + the answer-disagreement filter: 5,276 matches, zero new calls
  C  + AGGREGATE's replicate tie-break on B's 625 ties: 1,250 calls
Everything is reported with bootstrap CIs, and decisive-and-correct is reported separately from
correct-given-committed, because PAIR-NOREF / RK-1b / AGGREGATE show most measured "accuracy" is decisiveness.
"""
import os, sys, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8
import stack_judge as sj
import judge_free_tests as jf
import prompt_v2

CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "arenav3.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "arenav3_outcome.txt")


def base():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    P = defaultdict(dict); K = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12: P[q][m] = (pr or "").strip().upper()[:1]; K[q][m] = int(c or 0)
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute(
        "SELECT match_id, model_a, model_b, qid, anchor, vote1, vote2_raw, winner, invalid FROM verdicts") if not r[8]]
    return P, K, rows


def disagrees(P, r):
    pa, pb = P[r[3]].get(r[1]), P[r[3]].get(r[2])
    return bool(pa and pb and pa != pb)


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS rep (match_id INTEGER PRIMARY KEY, vote1 TEXT, vote2 TEXT, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit(); return con


def judge(pilot, workers):
    # The board is Mistral's (the x12 MAIN judge), so the tie-break must be Mistral too - mixing judges on one
    # Bradley-Terry board is exactly the defect the audit found in ARENA-13.
    p8.load_env()
    call = lambda sysp, usr: p8.call(sysp, usr)
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics()
    P, K, rows = base()
    todo_all = [r for r in rows if disagrees(P, r) and r[7] == "TIE"]
    con = open_cache()
    done = {m for (m,) in con.execute("SELECT match_id FROM rep")}
    todo = [r for r in todo_all if r[0] not in done]
    if pilot: todo = todo[:pilot]
    evals = rj.load_eval_rows([r[3] for r in todo_all], set(p8.ARENA12))
    print("ARENA-V3-COMPILED tie-break: %d filtered ties | to do %d (%d calls) | workers %d"
          % (len(todo_all), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(r):
        mid, a, b, qid, anc = r[0], r[1], r[2], r[3], r[4]
        ra, rb, ref = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid)
        if ra is None or rb is None or ref is None or anc not in rubrics: return None
        sp, rub = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        r1 = call(system, rj.build_user_prompt(q, ta, tb))
        r2 = call(system, rj.build_user_prompt(q, tb, ta))
        v1, _ = rj.parse_judge(r1); v2, _ = rj.parse_judge(r2)
        return (mid, v1, v2, r1, r2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, r): r for r in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO rep VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    P, K, rows = base()
    acc, _ = jf.gt_and_lengths(set(p8.ARENA12))
    models = sorted(p8.ARENA12); gt4 = sorted(sj.TOP4, key=lambda m: -acc[m])
    REP = {m: (v1, v2) for m, v1, v2 in open_cache().execute("SELECT match_id, vote1, vote2 FROM rep")}

    def canon(v, a, b, order):
        mp = {"Model A": a, "Model B": b} if order == 1 else {"Model A": b, "Model B": a}
        return mp.get(v)

    def verdict_C(r):
        if r[7] != "TIE": return r[7]
        rp = REP.get(r[0])
        if not rp: return "TIE"
        votes = [canon(r[5], r[1], r[2], 1), canon(r[6], r[1], r[2], 2),
                 canon(rp[0], r[1], r[2], 1), canon(rp[1], r[1], r[2], 2)]
        votes = [v for v in votes if v]
        na, nb = votes.count(r[1]), votes.count(r[2])
        return r[1] if na > nb else (r[2] if nb > na else "TIE")

    boards = [("A  ARENA-V2, all matches", rows, lambda r: r[7], 2 * len(rows)),
              ("B  + disagreement filter", [r for r in rows if disagrees(P, r)], lambda r: r[7], None),
              ("C  + replicate tie-break", [r for r in rows if disagrees(P, r)], verdict_C, None)]
    L = ["=== ARENA-V3-COMPILED: the paper's board from the interventions that survived ==="]
    L.append("  judge Mistral-Large-3 (the x12 MAIN judge), reasoning reference, v2 mechanics, anchor rubric, dual order")
    L.append("")
    L.append("  %-26s %7s %8s %9s %20s %24s" % ("board", "matches", "calls", "ties", "decisive-and-correct", "correct-given-committed"))
    rng = random.Random(42); stats = {}
    for name, sel, vf, calls in boards:
        if calls is None:
            calls = 2 * len(sel) + (2 * sum(1 for r in sel if r[7] == "TIE") if "tie-break" in name else 0)
        vs = [(r, vf(r)) for r in sel]
        dec = [(r, w) for r, w in vs if K[r[3]].get(r[1]) is not None and K[r[3]].get(r[2]) is not None
               and K[r[3]][r[1]] != K[r[3]][r[2]]]
        truth = lambda r: r[1] if K[r[3]][r[1]] else r[2]
        dc = sum(1 for r, w in dec if w == truth(r)) / len(dec)
        com = [(r, w) for r, w in dec if w != "TIE"]
        cgc = sum(1 for r, w in com if w == truth(r)) / max(1, len(com))
        ties = sum(1 for r, w in vs if w == "TIE") / len(vs)
        th = jf.board_from([(r[1], r[2], 0.5 if w == "TIE" else (1.0 if w == r[1] else 0.0), 1.0) for r, w in vs], models)
        rho = jf.rho(th, acc, models)
        _, pv, _ = jf.violations({m: th[m] for m in sj.TOP4}, gt4)
        # bootstrap over matches: rho, violations, both accuracies
        rs = []; vv = []; d1 = []; d2 = []
        for _ in range(300):
            bs = [vs[rng.randrange(len(vs))] for _ in range(len(vs))]
            t = jf.board_from([(r[1], r[2], 0.5 if w == "TIE" else (1.0 if w == r[1] else 0.0), 1.0) for r, w in bs], models)
            rs.append(jf.rho(t, acc, models)); vv.append(jf.violations({m: t[m] for m in sj.TOP4}, gt4)[1])
            bd = [(r, w) for r, w in bs if K[r[3]].get(r[1]) is not None and K[r[3]].get(r[2]) is not None and K[r[3]][r[1]] != K[r[3]][r[2]]]
            if bd:
                d1.append(sum(1 for r, w in bd if w == truth(r)) / len(bd))
                bc = [(r, w) for r, w in bd if w != "TIE"]
                if bc: d2.append(sum(1 for r, w in bc if w == truth(r)) / len(bc))
        q = lambda v: (sorted(v)[7], sorted(v)[292]) if v else (float('nan'), float('nan'))
        stats[name] = dict(rho=rho, rci=q(rs), pv=pv, vci=q(vv), dc=dc, dci=q(d1), cgc=cgc, cci=q(d2),
                           calls=calls, n=len(sel), dec=dec, vs=dict((r[0], w) for r, w in vs))
        L.append("  %-26s %7d %8d %9.3f   %.3f [%.3f, %.3f]      %.3f [%.3f, %.3f]"
                 % (name, len(sel), calls, ties, dc, q(d1)[0], q(d1)[1], cgc, q(d2)[0], q(d2)[1]))
    L.append("")
    L.append("  %-26s %10s %22s %12s %14s" % ("board", "rho", "rho 95% CI", "top-4 viol", "viol 95% CI"))
    for name in stats:
        st = stats[name]
        L.append("  %-26s %10.4f %10.4f-%.4f %12d %10d-%d"
                 % (name, st["rho"], st["rci"][0], st["rci"][1], st["pv"], st["vci"][0], st["vci"][1]))
    L.append("  (ORACLE-BOARD, the key as verdict on the same schedule: rho 1.0000, 0 violations)")

    A, B, C = [stats[k] for k in stats]
    common = [r for r, w in C["dec"]]
    truth = lambda r: r[1] if K[r[3]][r[1]] else r[2]
    b = sum(1 for r in common if A["vs"].get(r[0]) == truth(r) and C["vs"].get(r[0]) != truth(r))
    c = sum(1 for r in common if C["vs"].get(r[0]) == truth(r) and A["vs"].get(r[0]) != truth(r))
    L.append("")
    # Both rates must come from the SAME matches: A's headline 0.852 is over its own (larger) decidable set,
    # and quoting it against C's filtered rate would be the population mismatch this campaign keeps making.
    a_common = sum(1 for r in common if A["vs"].get(r[0]) == truth(r)) / len(common)
    c_common = sum(1 for r in common if C["vs"].get(r[0]) == truth(r)) / len(common)
    L.append("  (1) PRIMARY, both rates on the SAME %d common decidable matches: C %.3f vs A %.3f (%+.3f)"
             % (len(common), c_common, a_common, c_common - a_common))
    L.append("      (for reference, each board's rate on its own decidable set: A %.3f over all matches, C %.3f"
             % (A["dc"], C["dc"]))
    L.append("       over the filtered ones - different denominators, not comparable directly)")
    L.append("      discordant %d:%d | McNemar p=%.4g | registered bar: +3pp and p<0.05 -> %s"
             % (b, c, p8.mcn(b, c), "PASS" if (c_common - a_common >= 0.03 and p8.mcn(b, c) < 0.05) else "FAIL"))
    L.append("  (2) BOARD: rho %.4f (bar 0.967) and %d top-4 violations (bar <=1) -> %s"
             % (C["rho"], C["pv"], "PASS" if (C["rho"] >= 0.967 and C["pv"] <= 1) else "FAIL"))
    L.append("  (3) COST: %d calls against %d for the unfiltered dual-order board = %.0f%% (bar <=70%%) -> %s"
             % (C["calls"], A["calls"], 100 * C["calls"] / A["calls"], "PASS" if C["calls"] <= 0.70 * A["calls"] else "FAIL"))
    flat = abs(C["cgc"] - A["cgc"]) < 0.02
    L.append("  (4) DUAL REPORTING: decisive-and-correct %.3f -> %.3f (%+.3f) while correct-given-committed"
             % (A["dc"], C["dc"], C["dc"] - A["dc"]))
    L.append("      %.3f -> %.3f (%+.3f) -> %s" % (A["cgc"], C["cgc"], C["cgc"] - A["cgc"],
             "the gain is DECISIVENESS, not discrimination - the abstention finding stated as cleanly as it can be"
             if flat else "correct-given-committed moves too: the filter and tie-break improve DISCRIMINATION as well,"
                          "\n      and the abstention framing is too strong (registered falsifier)"))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze()
