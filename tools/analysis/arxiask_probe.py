"""ARXIASK — the clean capability test on the discriminating evidence (registered 2026-09-13).

  python tools/analysis/arxiask_probe.py --judge [--pilot N] [--workers 8]
  python tools/analysis/arxiask_probe.py --analyze

Judge ONLY the 302 pool questions where arx_0314 and iask_pro differ by the key (arx wins 179, iask 123,
0.593 +- 0.028; verified 2026-09-14 - the docstring previously said 301 / 122 / 0.595, one question out). Every match is decidable, so the signal-free pairs that FRONTIER showed carry the inversion
cannot contribute. Both formats, same judge / reference / rubric / mechanics as the campaign.
"""
import os, sys, json, time, sqlite3, argparse, threading, math
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import stack_judge as sj
import pointwise_judge as pt
import prompt_v2

A, B = "arx_0314", "iask_pro"
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "arxiask.db")


def questions():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results") if m in (A, B)}
    qs = sorted(q for q in pool if (q, A) in K and (q, B) in K and K[(q, A)] != K[(q, B)])
    return qs, K


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS pairwise (qid INTEGER PRIMARY KEY, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS grades (qid INTEGER, model TEXT, grade REAL, raw TEXT, PRIMARY KEY (qid, model))")
    con.commit(); return con


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    qs, K = questions()
    if pilot: qs = qs[:pilot]
    evals = rj.load_eval_rows(qs, {A, B})
    con = open_cache()
    dp = {q for (q,) in con.execute("SELECT qid FROM pairwise")}
    dg = {(q, m) for q, m in con.execute("SELECT qid, model FROM grades")}
    jobs = [("pw", q) for q in qs if q not in dp] + [("pt", q, m) for q in qs for m in (A, B) if (q, m) not in dg]
    print("ARXIASK: %d discriminating questions | jobs %d (%d calls) | workers %d"
          % (len(qs), len(jobs), sum(2 if j[0] == "pw" else 1 for j in jobs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        q = job[1]
        ra, rb, ref, anc = evals.get((q, A)), evals.get((q, B)), refs.get(q), anchors.get(q)
        if ra is None or rb is None or ref is None or anc is None: return None
        sp, rbc = rubrics[anc]
        qtext = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        if job[0] == "pw":
            system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rbc) + "\n\n" + rj.SCHEMA_INSTRUCTION
            raw1 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(qtext, ta, tb))[0])
            raw2 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(qtext, tb, ta))[0])
            v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
            w, flip, inv = rj.combine_orders(v1, v2)
            return ("pw", (q, v1, v2, {"Model A": A, "Model B": B}.get(w, w), int(flip), int(inv), raw1, raw2))
        m = job[2]; trace = ta if m == A else tb
        raw = rr.strip_think(rr.call_judge(pt.SYSTEM % (sp, pt.VERIFY_REF, rbc), pt.USER % (qtext, trace))[0])
        g, _ = pt.parse(raw)
        if g is None: return None
        return ("pt", (q, m, g, raw))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: r = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f], str(e)[:110]), flush=True); continue
            if r is None: skip += 1; continue
            with lock:
                if r[0] == "pw": con.execute("INSERT OR REPLACE INTO pairwise VALUES (?,?,?,?,?,?,?,?)", r[1])
                else: con.execute("INSERT OR REPLACE INTO grades VALUES (?,?,?,?)", r[1])
                con.commit()
            ok += 1
            if i % 100 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def binom_p(k, n):
    if n == 0: return 1.0
    from math import comb
    obs = abs(k - n / 2)
    tail = sum(comb(n, i) for i in range(n + 1) if abs(i - n / 2) >= obs)
    return min(1.0, tail / (2 ** n))


def analyze():
    qs, K = questions()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    L = {(q, m): len(o or "") for q, m, o in ev.execute("SELECT question_id, model_name, model_output FROM eval_results") if m in (A, B)}
    con = open_cache()
    PW = {q: (w, inv) for q, w, inv in con.execute("SELECT qid, winner, invalid FROM pairwise")}
    GR = {(q, m): g for q, m, g in con.execute("SELECT qid, model, grade FROM grades")}
    kw = sum(1 for q in qs if K[(q, A)]); n = len(qs)
    print("=== ARXIASK: %d questions where %s and %s differ | key says %s wins %d, %s wins %d (rate %.3f) ===" % (n, A, B, A, kw, B, n - kw, kw / n))
    print("  mean trace length: %s %.0f chars | %s %.0f chars" % (A, sum(L[(q, A)] for q in qs) / n, B, sum(L[(q, B)] for q in qs) / n))
    close = [q for q in qs if min(L[(q, A)], L[(q, B)]) > 0 and abs(L[(q, A)] - L[(q, B)]) / max(L[(q, A)], L[(q, B)]) <= 0.20]
    print("  length-matched subset (within 20%%): %d questions, key rate for %s %.3f\n" % (len(close), A, sum(1 for q in close if K[(q, A)]) / max(1, len(close))))
    for name, verdict in (("pairwise", lambda q: PW[q][0] if q in PW and not PW[q][1] else None),
                          ("pointwise", lambda q: (None if (q, A) not in GR or (q, B) not in GR else ("TIE" if GR[(q, A)] == GR[(q, B)] else (A if GR[(q, A)] > GR[(q, B)] else B))))):
        got = [(q, verdict(q)) for q in qs]; got = [(q, w) for q, w in got if w is not None]
        dec = [(q, w) for q, w in got if w != "TIE"]
        wa = sum(1 for q, w in dec if w == A)
        acc = sum(1 for q, w in got if w == (A if K[(q, A)] else B)) / len(got)
        p = binom_p(wa, len(dec))
        longer = sum(1 for q, w in dec if L[(q, w)] > L[(q, A if w == B else B)]) / max(1, len(dec))
        cl = [(q, w) for q, w in dec if q in set(close)]
        wac = sum(1 for q, w in cl if w == A)
        print("  %-10s judged %d (ties %d) | %s win rate %.3f (binomial p=%.4f) | accuracy vs key %.3f | winner is the LONGER answer %.0f%%"
              % (name, len(got), len(got) - len(dec), A, wa / max(1, len(dec)), p, acc, 100 * longer))
        print("             recovers the key order (%s > %s): %s | length-matched subset n=%d, %s win rate %.3f"
              % (A, B, "YES" if (wa / max(1, len(dec)) > 0.5 and p < 0.05) else "NO", len(cl), A, wac / max(1, len(cl))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze()
