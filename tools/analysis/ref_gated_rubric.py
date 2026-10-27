"""REF-GATED-RUBRIC — is rubric value conditional on the reference being right? (registered 2026-09-14)

  python tools/analysis/ref_gated_rubric.py --schedule
  python tools/analysis/ref_gated_rubric.py --judge [--pilot N] [--workers 8]
  python tools/analysis/ref_gated_rubric.py --analyze

RUBRIC-STRATA (post-hoc) found the RK-1b data card worth +1.5 to +2.0pp where the reference is CORRECT and
exactly 0.000 where it is WRONG, on both judge families - but at n=127 on the stratum carrying the claim, where
the minimum detectable effect is ~5.4pp. This is the powered 2x2, run fresh in one session so that no arm is a
cached control from another session (the defect the ledger audit found behind the RK-1/RK-1b PASS-FAIL split).
"""
import os, sys, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import rubric_kit2 as rk2
import prompt_v2
import pool_guard

PER_STRATUM = 900
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "refgated.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "refgated_outcome.txt")


def setup():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = defaultdict(dict); P = defaultdict(dict)
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12: K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    rref.set_reference("grok-reasoning")
    return pool, K, P, rref.references()


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, stratum TEXT, qid INTEGER, model_a TEXT, model_b TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm))")
    con.commit(); return con


def build():
    pool, K, P, refs = setup()
    con = open_cache()
    if con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        print("schedule exists: %d" % con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]); return
    models = sorted(p8.ARENA12)
    pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    rng = random.Random(42); rows = []; mid = 80_000_000
    for stratum, want_correct in (("ref_wrong", False), ("ref_correct", True)):
        cand = []
        for q in sorted(pool):
            r = refs.get(q)
            if r is None or bool(r[2]) != want_correct: continue
            for a, b in pairs:
                if K[q].get(a) is None or K[q].get(b) is None or K[q][a] == K[q][b]: continue
                pa, pb = P[q].get(a), P[q].get(b)
                if pa and pb and pa != pb: cand.append((q, a, b))
        rng.shuffle(cand)
        for q, a, b in cand[:PER_STRATUM]:
            rows.append((mid, stratum, q, a, b)); mid += 1
        print("  %-12s candidates %5d -> scheduled %d" % (stratum, len(cand), min(len(cand), PER_STRATUM)))
    con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?)", rows); con.commit()
    print("scheduled %d matches x 2 arms = %d calls (single order)" % (len(rows), 2 * len(rows)))


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    pool, K, P, refs = setup()
    rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    route = r512.primary_routing("bareq512_s42")
    cards = {l: t for l, t in rk2.open_kit().execute("SELECT leaf, text FROM datacard")}
    con = open_cache()
    sched = con.execute("SELECT mid, stratum, qid, model_a, model_b FROM schedule ORDER BY mid").fetchall()
    if pilot: sched = sched[:pilot]
    done = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    jobs = [(s, arm) for s in sched for arm in ("base", "card") if (s[0], arm) not in done]
    evals = rj.load_eval_rows([s[2] for s in sched], set(p8.ARENA12))
    print("REF-GATED-RUBRIC: %d matches x 2 arms | jobs %d | cards for %d leaves | workers %d"
          % (len(sched), len(jobs), len(cards), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        (mid, stratum, qid, a, b), arm = job
        ra, rb, ref, anc = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid)
        leaf = route.get(qid)
        if ra is None or rb is None or ref is None or anc is None: return None
        sp, rub = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub)
        if arm == "card":
            if leaf not in cards: return None
            system += "\n\nSubdomain data card (measured on training questions of this cell):\n" + cards[leaf]
        system += "\n\n" + rj.SCHEMA_INSTRUCTION
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, ta, tb))[0])
        v, _ = rj.parse_judge(raw)
        w = {"Model A": a, "Model B": b}.get(v, "TIE")
        return (mid, arm, w, int(v not in ("Model A", "Model B", "TIE")), raw, time.time())
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
            if i % 200 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    pool, K, P, refs = setup()
    con = open_cache()
    sch = {m: (st, q, a, b) for m, st, q, a, b in con.execute("SELECT mid, stratum, qid, model_a, model_b FROM schedule")}
    V = defaultdict(dict)
    for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    rows = {"ref_wrong": [], "ref_correct": []}
    for m, d in V.items():
        if "base" not in d or "card" not in d: continue
        st, q, a, b = sch[m]
        truth = a if K[q][a] else b
        rows[st].append((truth, d["base"], d["card"]))
    L = ["=== REF-GATED-RUBRIC: is the data card's value conditional on the reference being right? ==="]
    eff = {}
    for st in ("ref_correct", "ref_wrong"):
        s = rows[st]
        if not s: continue
        ab = sum(1 for t, x, y in s if x == t) / len(s); ac = sum(1 for t, x, y in s if y == t) / len(s)
        b_ = sum(1 for t, x, y in s if x == t and y != t); c_ = sum(1 for t, x, y in s if y == t and x != t)
        cb = [(t, x, y) for t, x, y in s if x != "TIE"]; cc = [(t, x, y) for t, x, y in s if y != "TIE"]
        eff[st] = ac - ab
        L.append("")
        L.append("  %-12s n=%4d | no card %.3f | + card %.3f | %+.3f | %d:%d | McNemar p=%.4g"
                 % (st, len(s), ab, ac, ac - ab, b_, c_, p8.mcn(b_, c_)))
        L.append("      ties: no card %.3f -> card %.3f | correct-given-committed %.3f -> %.3f"
                 % (sum(1 for t, x, y in s if x == "TIE") / len(s), sum(1 for t, x, y in s if y == "TIE") / len(s),
                    sum(1 for t, x, y in cb if x == t) / max(1, len(cb)), sum(1 for t, x, y in cc if y == t) / max(1, len(cc))))
    if len(eff) == 2:
        inter = eff["ref_correct"] - eff["ref_wrong"]
        rng = random.Random(7); ds = []
        for _ in range(2000):
            e = {}
            for st in ("ref_correct", "ref_wrong"):
                s = rows[st]; bs = [s[rng.randrange(len(s))] for _ in s]
                e[st] = sum(1 for t, x, y in bs if y == t) / len(bs) - sum(1 for t, x, y in bs if x == t) / len(bs)
            ds.append(e["ref_correct"] - e["ref_wrong"])
        ds.sort()
        L.append("")
        L.append("  (1) PRIMARY, the INTERACTION: card effect where the reference is right minus where it is wrong")
        L.append("      %+.3f  bootstrap 95%% CI [%+.3f, %+.3f] -> %s"
                 % (inter, ds[50], ds[1949],
                    "CONFIRMED: rubric value is CONDITIONAL on the reference being right"
                    if ds[50] > 0 else "NOT CONFIRMED: RUBRIC-STRATA does not survive powering"))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", action="store_true"); ap.add_argument("--judge", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.schedule: build()
    elif a.judge: build(); judge(a.pilot, a.workers)
    elif a.analyze: analyze()
