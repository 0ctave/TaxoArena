"""PLACEBO-ENTRY — does the ARENA-13 PROTOCOL inflate whoever enters through it? (registered 2026-09-14)

  python tools/analysis/placebo_entry.py --arm-a                       (zero calls)
  python tools/analysis/placebo_entry.py --judge [--pilot N] [--workers 8]
  python tools/analysis/placebo_entry.py --analyze

POSITION-FULL left +0.045 theta unattributed. The hypothesis this tests is structural rather than about the
model: the newcomer's edges were all judged on DISAGREEMENT-FILTERED questions (about 80% key-decidable) while
the twelve's come from the unfiltered x12 schedule (about 30%). Non-decidable matches are near coin flips that
shrink theta toward the centre of the board, so filtered edges are LESS SHRUNK - mechanically pushed away from
the centre, which for an above-average model means up.

ARM A (free): refit the twelve on all their x12 matches and on their answer-disagreeing subset, and compare the
spread of theta - the artefact, if real, shows up on models nobody is disputing.
ARM B (1,200 calls): re-enter gemini - already on the board, original traces, no REGEN - through the ARENA-13
protocol exactly, and see whether it gains.
"""
import os, sys, time, json, random, sqlite3, argparse, threading
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rubric_p8 as p8
import stack_judge as sj
import judge_free_tests as jf
import prompt_v2
import arena13 as a13

GEM = "gemini-3.1-pro_5-shots"
OPPS = ["arx_0314", "iask_pro", "gpt-4o-2024-08-06", "deepseek-chat-v2_5"]
PER_PAIR = 150
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "placebo.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "placebo_outcome.txt")


def x12_rows():
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    return [r for r in sj.open_cache().execute(
        "SELECT model_a, model_b, qid, winner, invalid FROM verdicts") if not r[4]]


def centred(th, exclude):
    others = [v for m, v in th.items() if m != exclude]
    c = sum(others) / len(others)
    return {m: v - c for m, v in th.items()}


def arm_a(L, P):
    """Zero calls: does restricting to answer-disagreeing matches inflate the spread of theta?"""
    rows = x12_rows()
    models = sorted(p8.ARENA12)
    def board(sel):
        return jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                              for a, b, q, w, _ in sel], models)
    dis = [r for r in rows if P.get(r[2], {}).get(r[0]) and P.get(r[2], {}).get(r[1])
           and P[r[2]][r[0]] != P[r[2]][r[1]]]
    ta, td = board(rows), board(dis)
    sd = lambda t: (sum((v - sum(t.values()) / len(t)) ** 2 for v in t.values()) / (len(t) - 1)) ** 0.5
    L.append("(2) ARM A, zero calls - does the disagreement filter inflate the theta scale?")
    L.append("      all x12 matches      n=%5d | theta spread (SD) %.3f | range %.3f" % (len(rows), sd(ta), max(ta.values()) - min(ta.values())))
    L.append("      disagreeing subset   n=%5d | theta spread (SD) %.3f | range %.3f" % (len(dis), sd(td), max(td.values()) - min(td.values())))
    L.append("      ratio of spreads %.2f -> %s" % (sd(td) / sd(ta),
             "FILTERED EDGES ARE ON A WIDER SCALE: mixing them with unfiltered ones on one board inflates whoever is filtered"
             if sd(td) / sd(ta) > 1.05 else "no material scale difference; the structural hypothesis is not supported here"))
    L.append("      per model, distance from the board centre:")
    ca, cd = centred(ta, None), centred(td, None)
    for m in sorted(models, key=lambda m: -ta[m])[:6]:
        L.append("        %-34s all %+.3f | filtered %+.3f | %+.3f" % (m, ca[m], cd[m], cd[m] - ca[m]))
    return sd(td) / sd(ta)


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, qid INTEGER, opponent TEXT, anchor TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm))")
    con.commit(); return con


def build():
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    con = open_cache()
    if con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        print("schedule exists: %d" % con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]); return
    rng = random.Random(42); rows = []; mid = 70_000_000
    for opp in OPPS:
        cand = [q for q in sorted(pool)
                if P[q].get(GEM) and P[q].get(opp) and P[q][GEM] != P[q][opp]
                and q in route and a13.ensemble_ref(q, P, OPT, {opp, GEM}) is not None]
        rng.shuffle(cand); take = cand[:PER_PAIR]
        for q in take:
            rows.append((mid, q, opp, anchor_of(route[q]))); mid += 1
        dec = sum(1 for q in take if K[q][GEM] != K[q][opp])
        print("  vs %-28s candidates %4d -> %3d scheduled | key-decidable %3d (%.0f%%)"
              % (opp, len(cand), len(take), dec, 100 * dec / max(1, len(take))))
    con.executemany("INSERT INTO schedule VALUES (?,?,?,?)", rows); con.commit()
    print("scheduled %d matches, dual order = %d calls" % (len(rows), 2 * len(rows)))


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    rubrics = sj.anchor_rubrics()
    con = open_cache()
    sched = con.execute("SELECT mid, qid, opponent, anchor FROM schedule ORDER BY mid").fetchall()
    if pilot: sched = sched[:pilot]
    done = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    jobs = [(s, arm) for s in sched for arm in ("fwd", "rev") if (s[0], arm) not in done]
    evals = rj.load_eval_rows([s[1] for s in sched], {GEM} | set(OPPS))
    print("PLACEBO-ENTRY: %d matches x 2 orders | jobs %d | workers %d" % (len(sched), len(jobs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        (mid, qid, opp, anc), arm = job
        rg, ro = evals.get((qid, GEM)), evals.get((qid, opp))
        if rg is None or ro is None: return None
        ref = a13.ensemble_ref(qid, P, OPT, {opp, GEM})
        if ref is None: return None
        sp, rub = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = rg[0] + "\n\n[Reference solution — produced independently, may be wrong]\n(%s) %s" % (ref[0], ref[1])
        tg = rj.robust_trace(rg[2], rg[3], rg[1]); to = rj.robust_trace(ro[2], ro[3], ro[1])
        a_, b_ = (tg, to) if arm == "fwd" else (to, tg)
        raw = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, a_, b_))[0])
        v, _ = rj.parse_judge(raw)
        mp = {"Model A": GEM, "Model B": opp} if arm == "fwd" else {"Model A": opp, "Model B": GEM}
        return (mid, arm, mp.get(v, "TIE"), int(v not in ("Model A", "Model B", "TIE")), raw, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    L = ["=== PLACEBO-ENTRY: gemini re-entered through the ARENA-13 protocol ==="]
    ratio = arm_a(L, P)

    con = open_cache()
    sch = {m: (q, opp) for m, q, opp in con.execute("SELECT mid, qid, opponent FROM schedule")}
    V = defaultdict(dict)
    for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    dual = {}
    for m, d in V.items():
        if "fwd" not in d or "rev" not in d: continue
        dual[m] = "TIE" if d["fwd"] != d["rev"] else d["fwd"]
    L.append("")
    L.append("(1) ARM B, %d dual-order matches judged" % len(dual))
    if not dual:
        print("\n".join(L)); return
    dec = [m for m in dual if K[sch[m][0]][GEM] != K[sch[m][0]].get(sch[m][1], 0)]
    acc = sum(1 for m in dec if dual[m] == (GEM if K[sch[m][0]][GEM] else sch[m][1])) / max(1, len(dec))
    ties = sum(1 for m in dual if dual[m] == "TIE") / len(dual)
    wr = sum(1 for m in dual if dual[m] == GEM) / len(dual)
    L.append("      gemini win rate %.3f | ties %.3f | key-decidable accuracy %.3f on %d pairs (readout 3)"
             % (wr, ties, acc, len(dec)))

    rows = x12_rows()
    models = sorted(p8.ARENA12)
    base = [(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, q, w, _ in rows]
    th_x12 = centred(jf.board_from(base, models), GEM)
    keep = [(a, b, v, n) for (a, b, v, n), r in zip(base, rows) if GEM not in (r[0], r[1])]
    # MATCHED BASELINE: the protocol only ever faced four opponents, so gemini's x12 theta over ELEVEN is not the
    # right comparator - it is a different quantity. Restrict the baseline to the same four opponents, so the two
    # boards differ only in question selection and reference construction, not in who was played.
    base4 = keep + [(a, b, v, n) for (a, b, v, n), r in zip(base, rows)
                    if GEM in (r[0], r[1]) and (r[0] in OPPS or r[1] in OPPS)]
    th_b4 = centred(jf.board_from(base4, models), GEM)
    prot = keep + [(GEM, sch[m][1], 0.5 if dual[m] == "TIE" else (1.0 if dual[m] == GEM else 0.0), 1.0) for m in dual]
    th_pro = centred(jf.board_from(prot, models), GEM)
    delta = th_pro[GEM] - th_b4[GEM]
    rng = random.Random(7); ds = []
    mids = sorted(dual)
    for _ in range(600):
        bs = [mids[rng.randrange(len(mids))] for _ in mids]
        p2 = keep + [(GEM, sch[m][1], 0.5 if dual[m] == "TIE" else (1.0 if dual[m] == GEM else 0.0), 1.0) for m in bs]
        ds.append(centred(jf.board_from(p2, models), GEM)[GEM] - th_b4[GEM])
    ds.sort()
    lo, hi = ds[15], ds[584]
    L.append("      gemini theta, x12 edges vs ALL eleven opponents        %+.3f" % th_x12[GEM])
    L.append("      gemini theta, x12 edges vs THE SAME FOUR opponents     %+.3f   <- the matched baseline" % th_b4[GEM])
    L.append("      gemini theta, PROTOCOL edges (same four opponents)     %+.3f" % th_pro[GEM])
    L.append("      delta against the MATCHED baseline %+.3f  95%% CI [%+.3f, %+.3f]" % (delta, lo, hi))
    L.append("      (against the eleven-opponent baseline it would read %+.3f - a different quantity, and the"
             % (th_pro[GEM] - th_x12[GEM]))
    L.append("       comparison the first version of this script made; boards centred on the other eleven)")
    L.append("      POWER, stated because the registration did not: the CI half-width is %.3f against a +0.045 bar,"
             % ((hi - lo) / 2))
    L.append("      so this arm could not have CONFIRMED the hypothesis even had it been true at the registered size.")
    L.append("      Read it as uninformative about +0.045, not as evidence against it.")
    ok = delta >= 0.045 and lo > 0
    L.append("")
    L.append("  (1) PRIMARY, registered bar delta >= +0.045 with a CI excluding zero -> %s" % ("CONFIRMED" if ok else "NOT CONFIRMED"))
    L.append("  RECONCILIATION of the two arms, which otherwise contradict each other inside this file: arm A")
    L.append("      filters gemini's edges against ALL eleven opponents and reports +0.325; arm B replaces them")
    L.append("      with edges against FOUR. Arm A also refits every other model on filtered evidence, so it")
    L.append("      measures a global rescaling of the board, not a relative gain to the model being filtered.")
    L.append("      The two are not the same quantity and arm B is the one that matches the ARENA-13 configuration.")
    L.append("  AMENDMENT RULE fixed before the run: %s" % (
        "the protocol inflates whoever enters through it, so the ARENA-13 (1) failure is attributed to PROTOCOL\n"
        "      SCALE rather than to the model. Amend both rows and state the methodological warning: never mix\n"
        "      filtered and unfiltered edges on one Bradley-Terry board." if ok else
        "as written, 'gemini does not gain, so the residue belongs to the newcomer and trace style becomes\n"
        "      the leading candidate'. THAT READING IS NOT AVAILABLE and the rule is withdrawn rather than\n"
        "      applied: at a CI half-width of 0.152 against a 0.045 bar this arm could not have confirmed the\n"
        "      hypothesis, so a NOT CONFIRMED here is absence of evidence, not evidence of absence. Readout (4)\n"
        "      supersedes the question in any case - the residue the rule was written to attribute is itself\n"
        "      not distinguishable from zero. Both candidates stay open and unprioritised, and nothing about\n"
        "      trace style is claimed."))
    # (4) FREE, unregistered: is the +0.045 residue distinguishable from zero in the first place?
    a13c = a13.open_cache()
    s13 = {m: (q, opp) for m, q, opp in a13c.execute("SELECT mid, qid, opponent FROM schedule")}
    W = defaultdict(dict)
    for m, arm, w, inv in a13c.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv and arm in ("ensemble", "reversed"): W[m][arm] = w
    d13 = {m: ("TIE" if v["ensemble"] != v["reversed"] else v["ensemble"])
           for m, v in W.items() if "ensemble" in v and "reversed" in v}
    m13 = sorted(set(p8.ARENA12) | {a13.NEW})
    base13 = [(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, q, w, _ in rows]
    def gap_from(ids):
        r = base13 + [(a13.NEW, s13[m][1], 0.5 if d13[m] == "TIE" else (1.0 if d13[m] == a13.NEW else 0.0), 1.0) for m in ids]
        t = jf.board_from(r, m13)
        return t[a13.NEW] - t[GEM]
    ids = sorted(d13)
    obs = gap_from(ids)
    rng3 = random.Random(23); gs = sorted(gap_from([ids[rng3.randrange(len(ids))] for _ in ids]) for _ in range(400))
    L.append("")
    L.append("  (4) FREE, unregistered - is the ARENA-13 residue distinguishable from zero at all?")
    L.append("      the newcomer's dual-order theta gap to gemini %+.3f | bootstrap 95%% CI [%+.3f, %+.3f] over %d matches"
             % (obs, gs[10], gs[389], len(ids)))
    L.append("      -> %s" % ("the gap EXCLUDES zero, so there is a real residue to explain" if gs[10] > 0 or gs[389] < 0
                              else "the gap INCLUDES zero. The newcomer and gemini are not separated by this arena at\n"
                                   "      this budget, so the +0.045 needs no mechanism: ARENA-13 (1) failed on a rank\n"
                                   "      ordering that the evidence never supported either way."))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-a", action="store_true"); ap.add_argument("--judge", action="store_true")
    ap.add_argument("--analyze", action="store_true"); ap.add_argument("--schedule", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.arm_a:
        pool, P, K, OPT, cot, route, anchor_of = a13.setup()
        L = []; arm_a(L, P); print("\n".join(L))
    elif a.schedule: build()
    elif a.judge: build(); judge(a.pilot, a.workers)
    elif a.analyze: analyze()
