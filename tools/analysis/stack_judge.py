"""STACK — the assembled judge v2, end-to-end (docs/judge_v2_program.md; registered before any call).

Configuration (per registration, J3-R having failed its primary): v1 mechanics + the reasoning
reference (J2-R) + the ANCHOR rubric (the ladder's clean anchor rubrics, induced with the pool of
record withheld; anchor = depth-1 label of the question's routed leaf in the clean bareq512_s42
tree) + dual order + confidence kept. Judge Mistral-Large-3, R3's 1,980 matches, one session.
REGISTERED (all must hold): (1) all-decidable accuracy >= 0.839; (2) top-cluster >= 0.645; (3) top-4
board on the top-cluster matches <= 1 key-order violation; (4) decidable tie rate <= 15%; (5) flip
rate <= 12.8%; (6) long-wrong preference on short-correct top-cluster pairs < v1's (x12 MAIN).

  python tools/analysis/stack_judge.py [--pilot N] [--workers N]
  python tools/analysis/stack_judge.py --analyze
"""
import os, sys, csv, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import judge_free_tests as jf

CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2.db")
LADDER = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_ladder.db")
J2R = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_mistral_reference_grok_reasoning.db")
TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]


def anchor_rubrics():
    c = sqlite3.connect("file:%s?mode=ro" % LADDER, uri=True)
    return {label: (sp, rb) for label, sp, rb in c.execute("SELECT label, system_prompt, rubric FROM rubrics WHERE kind='anchor'")}


def routed_anchor():
    snap = r512.snapshot_id("bareq512_s42"); nodes = r512.load_graph(snap); route = r512.primary_routing("bareq512_s42"); anchor = r512.anchor_fn(nodes)
    return {q: anchor(leaf) for q, leaf in route.items()}


def system_for(anchor, rubrics):
    sp, rb = rubrics[anchor]
    return rj.SYSTEM_TEMPLATE.replace("$systemPrompt", sp).replace("$rubric", rb) + "\n\n" + rj.SCHEMA_INSTRUCTION


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    p8.load_env()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = anchor_rubrics(); anchors = routed_anchor()
    missing = [a for a in set(anchors.values()) if a not in rubrics]
    assert not missing, "no anchor rubric for %s" % missing
    sample = rj.sample_matches()
    if pilot: sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    print("STACK: sample %d | jobs %d (%d calls) | anchors %d | workers %d" % (len(sample), len(todo), 2 * len(todo), len(rubrics), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, nid, *_ = m; qid = int(qid)
        ra, rb, ref, anc = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid)
        if ra is None or rb is None or ref is None or anc is None: return None
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = system_for(anc, rubrics)
        raw1 = p8.call(system, rj.build_user_prompt(q, ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(q, tb, ta))
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, anc, ref[0], int(ref[2]), v1, v2, c1, c2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 18), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    st = {r[0]: r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, flip, invalid, ref_correct FROM verdicts")}
    j2 = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % J2R, uri=True).execute("SELECT match_id, ref_winner, invalid, mistral_winner, flip FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    L = {(q, m): len(o or "") for q, m, o in ev.execute("SELECT question_id, model_name, model_output FROM eval_results")}
    valid = [r for r in st.values() if not r[6]]
    flip_rate = sum(r[5] for r in valid) / max(1, len(valid))
    rows = {}
    for mid, r in st.items():
        if r[6]: continue
        _, a, b, q, w, fl, _, refc = r
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b; wrong = b if ca else a
        rows[mid] = {"st": w == d, "tie": w == "TIE", "top": a in TOP4 and b in TOP4, "short_correct": L[(q, d)] < L[(q, wrong)], "w": w, "wrong": wrong,
                     "j2r": (j2[mid][1] == d) if (mid in j2 and not j2[mid][2]) else None, "v1": (j2[mid][3] == d) if mid in j2 else None,
                     "j2rw": j2[mid][1] if mid in j2 else None, "v1w": j2[mid][3] if mid in j2 else None}
    keys = list(rows); n = len(keys)
    acc = sum(rows[k]["st"] for k in keys) / n
    top = [k for k in keys if rows[k]["top"]]; acc_top = sum(rows[k]["st"] for k in top) / max(1, len(top))
    ties = sum(rows[k]["tie"] for k in keys) / n
    print("=== STACK (reference + v1 mechanics + anchor rubric), Mistral, %d judged (%d invalid), %d key-decidable ===" % (len(st), len(st) - len(valid), n))
    checks = []
    checks.append(("(1) all-decidable accuracy >= 0.839", acc, acc >= 0.839))
    checks.append(("(2) top-cluster accuracy >= 0.645 (n=%d)" % len(top), acc_top, acc_top >= 0.645))
    accK, _ = jf.gt_and_lengths(set(TOP4)); gt_order = sorted(TOP4, key=lambda m: -accK[m])
    topm = [r for r in valid if r[1] in TOP4 and r[2] in TOP4]
    th = jf.board_from(((r[1], r[2], 0.5 if r[4] == "TIE" else (1.0 if r[4] == r[1] else 0.0), 1.0) for r in topm), TOP4)
    order, pv, _ = jf.violations(th, gt_order)
    checks.append(("(3) top-4 board violations <= 1 [%s vs key %s]" % (" > ".join(order), " > ".join(gt_order)), pv, pv <= 1))
    checks.append(("(4) decidable tie rate <= 0.15", ties, ties <= 0.15))
    checks.append(("(5) flip rate <= 0.128", flip_rate, flip_rate <= 0.128))
    sc = [k for k in top if rows[k]["short_correct"]]
    lw_st = sum(rows[k]["w"] == rows[k]["wrong"] for k in sc) / max(1, len(sc))
    lw_v1 = sum(rows[k]["v1w"] == rows[k]["wrong"] for k in sc if rows[k]["v1w"] is not None) / max(1, sum(1 for k in sc if rows[k]["v1w"] is not None))
    lw_j2 = sum(rows[k]["j2rw"] == rows[k]["wrong"] for k in sc if rows[k]["j2rw"] is not None) / max(1, sum(1 for k in sc if rows[k]["j2rw"] is not None))
    checks.append(("(6) long-wrong preference (short-correct top pairs, n=%d) < v1's %.3f [J2-R %.3f]" % (len(sc), lw_v1, lw_j2), lw_st, lw_st < lw_v1))
    for lab, val, ok in checks:
        print("  %-80s %.3f -> %s" % (lab, val, "OK" if ok else "FAIL"))
    print("  STACK REGISTERED: %s" % ("PASS" if all(c[2] for c in checks) else "FAIL"))
    pj = [k for k in keys if rows[k]["j2r"] is not None]; b = sum(rows[k]["st"] and not rows[k]["j2r"] for k in pj); c = sum(rows[k]["j2r"] and not rows[k]["st"] for k in pj)
    print("  paired vs J2-R (cell rubric + reference): stack %.3f vs J2-R %.3f | %d:%d | p=%.4f  (anchor-vs-cell rubric under the reference)"
          % (sum(rows[k]["st"] for k in pj) / len(pj), sum(rows[k]["j2r"] for k in pj) / len(pj), b, c, p8.mcn(b, c)))
    pv1 = [k for k in keys if rows[k]["v1"] is not None]; b = sum(rows[k]["st"] and not rows[k]["v1"] for k in pv1); c = sum(rows[k]["v1"] and not rows[k]["st"] for k in pv1)
    print("  paired vs production v1 (x12 MAIN, no reference):  stack %.3f vs v1 %.3f | %d:%d | p=%.4f"
          % (sum(rows[k]["st"] for k in pv1) / len(pv1), sum(rows[k]["v1"] for k in pv1) / len(pv1), b, c, p8.mcn(b, c)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
