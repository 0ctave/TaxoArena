"""POINTWISE — the thesis's founding hypothesis, tested directly (registered 2026-09-13, docs/judge_v2_program.md).

  python tools/analysis/pointwise_judge.py --judge [--pilot N] [--workers 8]
  python tools/analysis/pointwise_judge.py --analyze

Is an LLM judge more reliable comparing two answers than grading one? Ninety-plus registered tests measure
pairwise judges; none ran a pointwise arm. This changes exactly ONE variable: same judge
(grok-4-1-fast-non-reasoning), same reasoning reference, same clean anchor rubric, same verify-first mechanics,
same R3 matches. Each distinct (question, model) answer is graded ONCE on 0-100; a pair's verdict is the higher
grade, equal grades being a TIE. Comparator: the cached RECIPE-GROK pairwise verdicts on the same matches.
"""
import os, re, sys, json, time, sqlite3, argparse, threading
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import judge_free_tests as jf
import stack_judge as sj

NOREF = False   # --noref: the no-reference cell of the 2x2 (cache pointwise_grok_noref.db)
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "pointwise_grok.db")
PAIRWISE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_grok.db")
PAIRWISE_NOREF = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_grok.db")

VERIFY_REF = " Check it against the reference solution supplied with the question."
VERIFY_NOREF = " Work out for yourself what the correct answer should be, then check the response against it."

SYSTEM = """%s

────────────────────────────────────────
GRADING MECHANICS (non-negotiable)
────────────────────────────────────────
Bias suppression — ignore completely:
• Response length, verbosity, or token count
• Formatting: markdown, LaTeX, bullet points, plain prose — all equal
• Model name, model family, or any identity signal
• Stylistic elegance or fluency unrelated to correctness

Grading order — follow exactly:
1. VERIFY the response's final answer.%s
   A response whose final answer is wrong cannot score above 40, however good its reasoning looks.
2. ASSESS the reasoning that led there against the rubric: correct steps, errors, gaps.
3. GRADE on 0-100, using the full range. Do not anchor on round numbers; small differences in
   quality must produce different grades, because these grades are compared against each other.

Your rubric:
%s

Return ONLY a JSON object, no prose outside it:
{"grade": <integer 0-100>, "confidence": <number 0.0-1.0>}"""

USER = """Question:
%s

Response to grade:
%s"""

GRADE = re.compile(r'"grade"\s*:\s*(-?\d+(?:\.\d+)?)')
CONF = re.compile(r'"confidence"\s*:\s*(-?\d+(?:\.\d+)?)')


def parse(raw):
    g = GRADE.search(raw or ""); c = CONF.search(raw or "")
    if not g: return None, None
    return max(0.0, min(100.0, float(g.group(1)))), (float(c.group(1)) if c else None)


def cache_path():
    return CACHE.replace(".db", "_noref.db") if NOREF else CACHE


def open_cache():
    con = sqlite3.connect(cache_path())
    con.execute("CREATE TABLE IF NOT EXISTS grades (qid INTEGER, model TEXT, anchor TEXT, grade REAL, conf REAL, raw TEXT, ts REAL, PRIMARY KEY (qid, model))")
    con.commit(); return con


def targets():
    """The 3,689 distinct (question, model) answers behind R3's 1,980 matches."""
    s = rj.sample_matches()
    out = sorted({(int(m[1]), m[2]) for m in s} | {(int(m[1]), m[3]) for m in s})
    return s, out


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    sample, tgt = targets()
    evals = rj.load_eval_rows([q for q, _ in tgt], {m for _, m in tgt})
    con = open_cache()
    done = {(q, m) for q, m in con.execute("SELECT qid, model FROM grades")}
    todo = [t for t in tgt if t not in done]
    if pilot: todo = todo[:pilot]
    print("POINTWISE [%s]: %d matches -> %d distinct answers | jobs %d (1 call each) | workers %d"
          % ("no reference" if NOREF else "reference", len(sample), len(tgt), len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(t):
        qid, model = t
        row, ref, anc = evals.get((qid, model)), refs.get(qid), anchors.get(qid)
        if row is None or ref is None or anc is None: return None
        sp, rb = rubrics[anc]
        q = row[0] if NOREF else rref.with_reference(row[0], ref)
        trace = rj.robust_trace(row[2], row[3], row[1])
        raw = rr.strip_think(rr.call_judge(SYSTEM % (sp, VERIFY_NOREF if NOREF else VERIFY_REF, rb), USER % (q, trace))[0])
        g, c = parse(raw)
        if g is None: return None
        return (qid, model, anc, g, c, raw, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, t): t for t in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f], str(e)[:110]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 200 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    sample, tgt = targets()
    con = open_cache()
    Gr = {(q, m): (g, c) for q, m, g, c in con.execute("SELECT qid, model, grade, conf FROM grades")}
    if NOREF:
        pw = {r[0]: (r[0], r[1], r[2], None, r[3], r[4]) for r in sqlite3.connect("file:%s?mode=ro" % PAIRWISE_NOREF, uri=True).execute("SELECT match_id, model_a, model_b, grok_winner, grok_invalid FROM verdicts")}
    else:
        pw = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % PAIRWISE, uri=True).execute("SELECT match_id, model_a, model_b, qid, winner, invalid FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    TOP4 = sj.TOP4
    rows = {}
    for m in sample:
        mid, qid, a, b = m[0], int(m[1]), m[2], m[3]
        p = pw.get(mid)
        if p is None or p[5]: continue
        ga, gb = Gr.get((qid, a)), Gr.get((qid, b))
        if ga is None or gb is None: continue
        ca, cb = K.get((qid, a)), K.get((qid, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        pt = "TIE" if ga[0] == gb[0] else (a if ga[0] > gb[0] else b)
        rows[mid] = dict(a=a, b=b, q=qid, d=d, pt=pt, pw=p[4], top=(a in TOP4 and b in TOP4))
    ks = list(rows); n = len(ks)
    acc_pt = sum(rows[k]["pt"] == rows[k]["d"] for k in ks) / n
    acc_pw = sum(rows[k]["pw"] == rows[k]["d"] for k in ks) / n
    b = sum(rows[k]["pw"] == rows[k]["d"] and rows[k]["pt"] != rows[k]["d"] for k in ks)
    c_ = sum(rows[k]["pt"] == rows[k]["d"] and rows[k]["pw"] != rows[k]["d"] for k in ks)
    p = p8.mcn(b, c_)
    print("=== POINTWISE vs PAIRWISE [%s] (same judge, rubric, matches; only the format differs) ===" % ("NO REFERENCE" if NOREF else "with reference"))
    print("  graded answers %d of %d | key-decidable pairs compared %d" % (len(Gr), len(tgt), n))
    print("  (1) PRIMARY  pairwise %.3f vs pointwise %.3f (%+.3f) | pairwise-only %d : pointwise-only %d | McNemar p=%.4g"
          % (acc_pw, acc_pt, acc_pt - acc_pw, b, c_, p))
    verdict = ("SUPPORTED: pairwise wins" if (acc_pw > acc_pt and p < 0.05) else
               ("REFUTED: pointwise >= pairwise" if acc_pt >= acc_pw else "NOT RESOLVED: pairwise ahead but p >= 0.05"))
    print("      founding hypothesis -> %s" % verdict)
    top = [k for k in ks if rows[k]["top"]]
    print("  top cluster (n=%d): pairwise %.3f vs pointwise %.3f (%+.3f)"
          % (len(top), sum(rows[k]["pw"] == rows[k]["d"] for k in top) / max(1, len(top)),
             sum(rows[k]["pt"] == rows[k]["d"] for k in top) / max(1, len(top)),
             (sum(rows[k]["pt"] == rows[k]["d"] for k in top) - sum(rows[k]["pw"] == rows[k]["d"] for k in top)) / max(1, len(top))))
    t_pt = sum(rows[k]["pt"] == "TIE" for k in ks) / n; t_pw = sum(rows[k]["pw"] == "TIE" for k in ks) / n
    print("  (3) TIES     pointwise %.3f vs pairwise %.3f" % (t_pt, t_pw))
    models = sorted({m for _, m in tgt})
    acck, _ = jf.gt_and_lengths(set(models))
    allm = [m for m in sample if pw.get(m[0]) and not pw[m[0]][5] and (int(m[1]), m[2]) in Gr and (int(m[1]), m[3]) in Gr]
    def board(fn):
        th = jf.board_from(((m[2], m[3], fn(m), 1.0) for m in allm), models)
        return rj.spearman([th[x] for x in models], [acck[x] for x in models]), th
    r_pt, th_pt = board(lambda m: 0.5 if Gr[(int(m[1]), m[2])][0] == Gr[(int(m[1]), m[3])][0] else (1.0 if Gr[(int(m[1]), m[2])][0] > Gr[(int(m[1]), m[3])][0] else 0.0))
    r_pw, th_pw = board(lambda m: 0.5 if pw[m[0]][4] == "TIE" else (1.0 if pw[m[0]][4] == m[2] else 0.0))
    mean_g = {x: sum(Gr[(q, mm)][0] for (q, mm) in Gr if mm == x) / max(1, sum(1 for (q, mm) in Gr if mm == x)) for x in models}
    r_mean = rj.spearman([mean_g[x] for x in models], [acck[x] for x in models])
    print("  (2) BOARD    rho vs key accuracy: pointwise-derived %.4f | pairwise %.4f | raw mean grade %.4f (n=%d matches)"
          % (r_pt, r_pw, r_mean, len(allm)))
    for x in sorted(models, key=lambda x: -th_pt[x])[:6]:
        print("      %-30s pointwise theta %+.3f | pairwise %+.3f | mean grade %5.1f | key %.3f" % (x, th_pt[x], th_pw[x], mean_g[x], acck[x]))
    print("  (4) COST     pointwise %d calls for %d matches = %.2f/match | pairwise %d = %.2f/match (question reuse %.2fx)"
          % (len(Gr), len(sample), len(Gr) / len(sample), 2 * len(sample), 2.0, len(tgt) / max(1, len({q for q, _ in tgt}))))
    vals = Counter(int(g) for (g, _) in Gr.values())
    print("  DESCRIPTIVE  distinct grades used %d | most common: %s" % (len(vals), vals.most_common(6)))
    pos = [g for (q, m), (g, _) in Gr.items() if K.get((q, m))]; neg = [g for (q, m), (g, _) in Gr.items() if K.get((q, m)) is False]
    auc = sum((1.0 if x > y else 0.5 if x == y else 0.0) for x in pos for y in neg) / max(1, len(pos) * len(neg))
    print("               grade AUC vs key correctness %.3f (mean grade correct %.1f vs wrong %.1f)"
          % (auc, sum(pos) / max(1, len(pos)), sum(neg) / max(1, len(neg))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--noref", action="store_true")
    a = ap.parse_args(); NOREF = a.noref
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze()
