"""FORMAT — style perturbation (docs/judge_v2_program.md; registered before any call).

Key-decidable R3 pairs where exactly one trace carries MARKDOWN markers (bold, headers, list
bullets, code fences; LaTeX is left untouched because rewriting it can change meaning). Arm:
the formatted trace with its markdown stripped (content and answer line intact), the other trace
unchanged; v1 prompt, frozen-tree cell system prompt, Mistral, dual order. Comparator: the cached
x12 MAIN verdict on the same match (original formatting).
REGISTERED: a format bias exists iff the correct-verdict rate changes by > 3pp with paired
McNemar p < 0.05; also reported: the flip rate toward the unformatted side. Prediction: no effect.
Runs only if >= 150 eligible pairs exist (prevalence recorded at launch).

  python tools/analysis/format_perturbation.py [--pilot N] [--workers N]
  python tools/analysis/format_perturbation.py --analyze
"""
import os, sys, re, time, sqlite3, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8

CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_format_stripped.db")
MD = re.compile(r"(\*\*|__|^#{1,6}\s+|^\s*[-*•]\s+|^\s*\d+\.\s+|```[a-zA-Z]*)", re.M)


def is_md(t): return bool(MD.search(t))


def strip_md(t):
    t = re.sub(r"```[a-zA-Z]*\n?", "", t)
    t = t.replace("**", "").replace("__", "")
    t = re.sub(r"^#{1,6}\s+", "", t, flags=re.M)
    t = re.sub(r"^(\s*)[-*•]\s+", r"\1", t, flags=re.M)
    t = re.sub(r"^(\s*)\d+\.\s+", r"\1", t, flags=re.M)
    return t


def eligible(sample, evals, G):
    out = []
    for m in sample:
        mid, qid, a, b, nid, *_ = m; qid = int(qid)
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None: continue
        ca, cb = G.get((qid, a)), G.get((qid, b))
        if ca is None or cb is None or ca == cb: continue
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        fa, fb = is_md(ta), is_md(tb)
        if fa != fb: out.append((m, "a" if fa else "b"))
    return out


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, formatted TEXT, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    p8.load_env()
    nodes = rj.load_nodes(); sample = rj.sample_matches()
    evals = rj.load_eval_rows([int(m[1]) for m in sample], {m[2] for m in sample} | {m[3] for m in sample})
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    elig = eligible(sample, evals, G)
    print("FORMAT: key-decidable pairs with exactly one markdown-formatted trace: %d" % len(elig), flush=True)
    if len(elig) < 150 and not pilot:
        print("below the registered 150-pair floor; not run"); return
    if pilot: elig = elig[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [(m, side) for m, side in elig if m[0] not in done]
    print("  jobs %d (%d calls) | workers %d" % (len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = 0

    def one(m, side):
        mid, qid, a, b, nid, *_ = m; qid = int(qid)
        ra, rb = evals[(qid, a)], evals[(qid, b)]
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        if side == "a": ta = strip_md(ta)
        else: tb = strip_md(tb)
        system = rj.build_system_prompt(nodes[nid])
        raw1 = p8.call(system, rj.build_user_prompt(ra[0], ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, a if side == "a" else b, v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m, s): m for m, s in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 14), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)


def analyze():
    st = {r[0]: r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, formatted, winner, invalid FROM verdicts")}
    x12 = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    base = {r[0]: ("TIE" if r[2] else r[1]) for r in x12.execute("SELECT id, winner, is_tie FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = []
    for mid, r in st.items():
        if r[6] or mid not in base: continue
        _, a, b, q, fm, w, _ = r
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b; unf = b if fm == a else a
        rows.append((w == d, base[mid] == d, base[mid] == fm and w == unf, fm == d))
    n = len(rows); ps = sum(r[0] for r in rows) / max(1, n); pb = sum(r[1] for r in rows) / max(1, n)
    b = sum(r[0] and not r[1] for r in rows); c = sum(r[1] and not r[0] for r in rows); p = p8.mcn(b, c)
    print("=== FORMAT: markdown stripped from the formatted trace vs original (cached x12 MAIN), Mistral, %d key-decidable pairs ===" % n)
    print("  correct-verdict rate stripped %.3f vs original %.3f (%+.3f) | %d:%d | p=%.4f -> format bias %s (registered: |delta| > 3pp and p < 0.05)"
          % (ps, pb, ps - pb, b, c, p, "PRESENT" if (abs(ps - pb) > 0.03 and p < 0.05) else "ABSENT"))
    print("  flips from the formatted side to the unformatted side after stripping: %d (%.1f%%) | pairs where the formatted trace is the correct one: %.0f%%"
          % (sum(r[2] for r in rows), 100 * sum(r[2] for r in rows) / max(1, n), 100 * sum(r[3] for r in rows) / max(1, n)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
