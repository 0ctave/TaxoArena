"""J3-R — prompt v2 (correctness-first, verify against the reference) on top of J2-R's setup
(docs/judge_improvement_proposals.md "Launch records 2026-09-09 (late)"; registered before any call).

v2 is derived from the v1 SYSTEM template by two exact replacements (asserted): the embedded
Kotlin comment block is removed, and the both-correct depth/scope ranking block is replaced by a
verify-final-answer policy. Everything else (bias list, evaluation order, rubric slot, user
template, schema instruction) is byte-identical. Judge = Mistral-Large-3, matches = R3's 1,980,
reference = grok-reasoning's S1 answer (J2-R), system prompt = frozen-tree cell prompt as in J2-R.

  python tools/analysis/prompt_v2.py [--pilot N] [--workers N]
  python tools/analysis/prompt_v2.py --analyze
"""
import os, sys, re, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8

CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_v2_refgrok.db")
J2R_CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_reference_grok_reasoning.db")

OLD_BLOCK = """For responses where BOTH models give factually correct answers:
You MUST still choose the better model. A tie is only valid when responses are
word-for-word equivalent OR when one model's single factual error exactly
cancels the other model's structural advantage and you cannot determine a net winner.

Ranking criteria when both are correct (apply in order):
1. Mechanistic depth — prefer the response explaining the underlying mechanism, not just the result
2. Edge-case handling — prefer the response that addresses boundary conditions or exceptions
3. Quantitative precision — prefer the response with correctly applied formulas/numbers
4. Scope accuracy — prefer the response that correctly scopes uncertainty

Reserve TIE for: identical responses, or responses where criterion 1–4 are all equal."""

NEW_BLOCK = """Correctness first — verify before you compare:
The question carries a reference solution (marked as produced independently; it may be wrong).
Before critiquing, extract each model's FINAL ANSWER and check it against the reference and
against your own reading of the question. A response whose final answer is wrong cannot win
against a response whose final answer is right, whatever its reasoning looks like.

When BOTH final answers are right:
Prefer the response with fewer errors or unsupported steps in its reasoning. If neither has
any, output TIE. Depth, breadth, scope, edge cases and elaboration are NOT criteria — a short
correct response ties a long correct response."""


def v2_system_template():
    t = rj.SYSTEM_TEMPLATE
    lines = t.split("\n")
    kept = [l for l in lines if not l.lstrip().startswith("// ")]
    assert len(lines) - len(kept) >= 8, "embedded comment block not found in v1"
    t = "\n".join(kept)
    # v1 carries trailing spaces on some lines; locate the block by its first and last line and
    # check it equals the expected text modulo whitespace before replacing it.
    m = list(re.finditer(r"For responses where BOTH models give factually correct answers:.*?criterion 1–4 are all equal\.", t, re.S))
    assert len(m) == 1, "v1 both-correct block not found exactly once"
    found = m[0].group(0)
    assert " ".join(found.split()) == " ".join(OLD_BLOCK.split()), "v1 both-correct block differs beyond whitespace"
    return t.replace(found, NEW_BLOCK)


def build_system_prompt_v2(node):
    sp = node.get("judgePrompt") or ("You are an expert academic evaluator in the domain: %s." % (node.get("label") or "General Science"))
    rubric = node.get("judgeRubric") or "Grade the response based on domain correctness, precision, and logical reasoning."
    return v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rubric) + "\n\n" + rj.SCHEMA_INSTRUCTION


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    p8.load_env()
    rref.set_reference("grok-reasoning")
    nodes = rj.load_nodes(); sample = rj.sample_matches()
    if pilot: sample = sample[:pilot]
    refs = rref.references()
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    print("J3-R: sample %d | jobs %d (%d calls) | references %d | workers %d" % (len(sample), len(todo), 2 * len(todo), len(refs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, nid, *_ = m; qid = int(qid)
        ra, rb, ref = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid)
        if ra is None or rb is None or ref is None: return None
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = build_system_prompt_v2(nodes[nid])
        raw1 = p8.call(system, rj.build_user_prompt(q, ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(q, tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, ref[0], int(ref[2]), v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 15), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    v2 = {r[0]: r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, ref_correct, winner, invalid FROM verdicts")}
    j2 = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % J2R_CACHE, uri=True).execute("SELECT match_id, ref_winner, invalid FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    L = {(q, m): len(o or "") for q, m, o in ev.execute("SELECT question_id, model_name, model_output FROM eval_results")}
    rows = {}
    for mid, r in v2.items():
        if mid not in j2 or r[6] or j2[mid][2]: continue
        _, a, b, q, refc, w2, _ = r
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b; wrong = b if ca else a
        rows[mid] = {"v2": w2 == d, "j2r": j2[mid][1] == d, "top": a in rj.TOP_CLUSTER and b in rj.TOP_CLUSTER, "refc": bool(refc),
                     "short_correct": L[(q, d)] < L[(q, wrong)], "v2w": w2, "j2w": j2[mid][1], "d": d, "wrong": wrong}
    def stats(keys):
        n = len(keys); p2 = sum(rows[k]["v2"] for k in keys) / max(1, n); pj = sum(rows[k]["j2r"] for k in keys) / max(1, n)
        b = sum(rows[k]["v2"] and not rows[k]["j2r"] for k in keys); c = sum(rows[k]["j2r"] and not rows[k]["v2"] for k in keys)
        return n, p2, pj, b, c, p8.mcn(b, c)
    keys = list(rows); n, p2, pj, b, c, p = stats(keys)
    ties2 = sum(1 for r in v2.values() if not r[6] and r[5] == "TIE") / max(1, sum(1 for r in v2.values() if not r[6]))
    print("=== J3-R: prompt v2 + reasoning reference vs J2-R (v1 + same reference), Mistral, %d key-decidable paired matches | v2 tie rate %.1f%% ===" % (n, 100 * ties2))
    print("  ALL decidable       v2 %.3f vs v1 %.3f (%+.3f) | %d:%d | p=%.4f -> PRIMARY %s" % (p2, pj, p2 - pj, b, c, p, "PASS" if (p2 > pj and p < 0.05) else "FAIL"))
    top = [k for k in keys if rows[k]["top"]]; n, p2, pj, b, c, p = stats(top)
    g1 = p2 >= pj - 0.02
    print("  TOP-CLUSTER         v2 %.3f vs v1 %.3f (%+.3f) | %d:%d | p=%.4f -> guard (>= v1 - 2pp) %s" % (p2, pj, p2 - pj, b, c, p, "OK" if g1 else "FAIL"))
    for lab, keys_ in (("reference CORRECT", [k for k in keys if rows[k]["refc"]]), ("reference WRONG", [k for k in keys if not rows[k]["refc"]])):
        n, p2, pj, b, c, p = stats(keys_)
        extra = "" if "WRONG" not in lab else " -> guard (>= v1 - 5pp) %s" % ("OK" if p2 >= pj - 0.05 else "FAIL")
        print("  %-19s v2 %.3f vs v1 %.3f (%+.3f) | %d:%d | p=%.4f%s" % (lab, p2, pj, p2 - pj, b, c, p, extra))
    sc = [k for k in top if rows[k]["short_correct"]]
    if sc:
        lw2 = sum(rows[k]["v2w"] == rows[k]["wrong"] for k in sc) / len(sc); lwj = sum(rows[k]["j2w"] == rows[k]["wrong"] for k in sc) / len(sc)
        print("  long-wrong preference on top-cluster pairs where the SHORTER answer is correct (n=%d): v2 %.3f vs v1 %.3f" % (len(sc), lw2, lwj))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()
    if a.show: print(v2_system_template())
    elif a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
