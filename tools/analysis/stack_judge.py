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
import os, sys, csv, math, time, sqlite3, argparse, threading
import numpy as np
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

PROMPT = "v1"   # --prompt v2 = STACK-v2 (v2 mechanics on the anchor rubric); separate cache
JUDGE = "mistral"   # --judge grok = RECIPE-GROK (grok-4-1-fast-non-reasoning with the same recipe)
ALL_X12 = False     # --all-x12 = ARENA-V2 (every x12 MAIN match instead of the R3 sample)
DATACARD = False    # --datacard = ARENA-V3: STACK-v2 + the data-only leaf card (RK-1b), cache suffix _card
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2.db")


def cache_path():
    p = CACHE if PROMPT == "v1" else CACHE.replace("stack_v2.db", "stack_v2_promptv2.db")
    if JUDGE == "grok": p = p.replace(".db", "_grok.db")
    if ALL_X12: p = p.replace(".db", "_x12all.db")
    if DATACARD: p = p.replace(".db", "_card.db")
    return p


def load_cards(sample):
    """leaf -> data card text (RK-1b kit, zero induction calls) + routing question -> leaf; leakage audit vs the judged sample."""
    import rubric_kit2 as rk2, rubric_kit as rk
    kcon = rk2.open_kit(); cards = {l: t for l, t in kcon.execute("SELECT leaf, text FROM datacard")}; kcon.close()
    route = r512.primary_routing("bareq512_s42")
    assert rk.leakage_audit({(l, "datacard"): t for l, t in cards.items()}, sample), "data card leaks option text"
    return cards, route


def judge_call(system, user):
    if JUDGE == "grok":
        import rejudge_reasoning as rr
        return rr.strip_think(rr.call_judge(system, user)[0])
    return p8.call(system, user)


def all_x12_matches():
    con = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    rows = con.execute("SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie FROM match_history WHERE condition='MAIN' AND snapshot_id=? ORDER BY id", (rj.SNAP_MAIN,)).fetchall()
    con.close(); return rows
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
    if PROMPT == "v2":
        import prompt_v2
        return prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rb) + "\n\n" + rj.SCHEMA_INSTRUCTION
    return rj.SYSTEM_TEMPLATE.replace("$systemPrompt", sp).replace("$rubric", rb) + "\n\n" + rj.SCHEMA_INSTRUCTION


def open_cache():
    con = sqlite3.connect(cache_path())
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit()
    return con


def run(pilot, workers):
    p8.load_env()
    if JUDGE == "grok":
        import rejudge_reasoning as rr
        rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = anchor_rubrics(); anchors = routed_anchor()
    missing = [a for a in set(anchors.values()) if a not in rubrics]
    assert not missing, "no anchor rubric for %s" % missing
    sample = all_x12_matches() if ALL_X12 else rj.sample_matches()
    cards, route = load_cards(sample) if DATACARD else ({}, {})
    if pilot: sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    print("STACK [judge=%s, %s]: sample %d | jobs %d (%d calls) | anchors %d | workers %d" % (JUDGE, "all x12" if ALL_X12 else "R3", len(sample), len(todo), 2 * len(todo), len(rubrics), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m):
        mid, qid, a, b, nid, *_ = m; qid = int(qid)
        ra, rb, ref, anc = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid)
        if ra is None or rb is None or anc is None: return None
        if ref is None and not ALL_X12: return None
        q = rref.with_reference(ra[0], ref) if ref is not None else ra[0]   # ARENA-V2: the 13 filtered questions are judged without a reference
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = system_for(anc, rubrics)
        if DATACARD:
            leaf = route.get(qid)
            if leaf in cards:
                system = system.replace("\n\n" + rj.SCHEMA_INSTRUCTION, "\n\nSubdomain data card (measured on training questions of this cell):\n" + cards[leaf] + "\n\n" + rj.SCHEMA_INSTRUCTION)
        raw1 = judge_call(system, rj.build_user_prompt(q, ta, tb)); raw2 = judge_call(system, rj.build_user_prompt(q, tb, ta))
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, nid, qid, anc, ref[0] if ref else "", int(ref[2]) if ref else -1, v1, v2, c1, c2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
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
    print("=== STACK%s (reference + %s mechanics + anchor rubric), Mistral, %d judged (%d invalid), %d key-decidable ===" % ("-v2" if PROMPT == "v2" else "", PROMPT, len(st), len(st) - len(valid), n))
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


def _decidable_rows(st, G):
    rows = {}
    for mid, r in st.items():
        if r[6]: continue
        _, a, b, q, w, fl, _, refc = r[:8]
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        rows[mid] = {"a": a, "b": b, "q": q, "w": w, "d": a if ca else b, "top": a in TOP4 and b in TOP4}
    return rows


def analyze_grok():
    """RECIPE-GROK (registered 2026-09-10 13:55): the STACK-v2 recipe on grok-4-1-fast-non-reasoning vs R3's cached
    grok verdicts (v1 cell rubric, no reference). REGISTERED: all-decidable gain > 0 at p < 0.05 AND top cluster > 0.618."""
    st = {r[0]: r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, flip, invalid, ref_correct FROM verdicts")}
    base = {r[0]: r for r in sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_grok.db"), uri=True)
            .execute("SELECT match_id, grok_winner, grok_invalid, model_a, model_b FROM verdicts")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = _decidable_rows(st, G)
    n_inv = sum(1 for r in st.values() if r[6])
    for mid, r in rows.items():
        b = base.get(mid); r["base"] = None if (b is None or b[2]) else (b[1] == r["d"])
    keys = list(rows); n = len(keys)
    acc = sum(rows[k]["w"] == rows[k]["d"] for k in keys) / n
    top = [k for k in keys if rows[k]["top"]]; acc_top = sum(rows[k]["w"] == rows[k]["d"] for k in top) / max(1, len(top))
    pk = [k for k in keys if rows[k]["base"] is not None]
    acc_b = sum(rows[k]["base"] for k in pk) / len(pk); acc_r = sum(rows[k]["w"] == rows[k]["d"] for k in pk) / len(pk)
    bb = sum((rows[k]["w"] == rows[k]["d"]) and not rows[k]["base"] for k in pk); cc = sum(rows[k]["base"] and not (rows[k]["w"] == rows[k]["d"]) for k in pk)
    ptop = [k for k in top if rows[k]["base"] is not None]
    acc_bt = sum(rows[k]["base"] for k in ptop) / max(1, len(ptop))
    p = p8.mcn(bb, cc)
    ties = sum(rows[k]["w"] == "TIE" for k in keys) / n
    print("=== RECIPE-GROK: STACK-v2 recipe on grok-4-1-fast-non-reasoning, %d judged (%d invalid), %d key-decidable ===" % (len(st), n_inv, n))
    print("  all-decidable: recipe %.3f vs cached grok v1 %.3f (paired n=%d) | %d:%d | p=%.4f" % (acc_r, acc_b, len(pk), bb, cc, p))
    print("  top cluster (n=%d): recipe %.3f vs cached grok v1 %.3f | registered bar 0.618" % (len(top), acc_top, acc_bt))
    print("  decidable tie rate %.3f" % ties)
    accK, _ = jf.gt_and_lengths(set(TOP4)); gt_order = sorted(TOP4, key=lambda m: -accK[m])
    topm = [r for r in st.values() if not r[6] and r[1] in TOP4 and r[2] in TOP4]
    th = jf.board_from(((r[1], r[2], 0.5 if r[4] == "TIE" else (1.0 if r[4] == r[1] else 0.0), 1.0) for r in topm), TOP4)
    order, pv, _ = jf.violations(th, gt_order)
    print("  top-4 board: %s vs key %s (%d violations)" % (" > ".join(order), " > ".join(gt_order), pv))
    ok1 = (acc_r > acc_b) and p < 0.05; ok2 = acc_top > 0.618
    print("  REGISTERED: gain>0 at p<0.05: %s | top cluster > 0.618: %s -> %s" % ("OK" if ok1 else "FAIL", "OK" if ok2 else "FAIL", "PASS" if ok1 and ok2 else "FAIL"))


def analyze_arena(nperm=1000):
    """ARENA-V2 (registered 2026-09-10 13:55): STACK-v2 on every x12 MAIN match vs x12's own v1 verdicts.
    (1) 12-model BT board Spearman rho vs key accuracy >= x12's; (2) top-4 violations <= 1; (3) anchor-level
    model x anchor interaction LRT survives question-level permutation p < 0.05; (4) key-decidable accuracy >= 0.85.
    The same statistics are computed on x12's own verdicts with the same code (like for like)."""
    import random
    st = {r[0]: r for r in open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, flip, invalid, ref_correct, node_id FROM verdicts")}
    x12 = {r[0]: r for r in all_x12_matches()}   # id, qid, a, b, nid, winner, is_tie
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    models = sorted({r[2] for r in x12.values()} | {r[3] for r in x12.values()})
    acc, _ = jf.gt_and_lengths(set(models)); gt_order = sorted(TOP4, key=lambda m: -acc[m])
    nodes = rj.load_nodes(); parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}

    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]

    def v1_rows():
        return [dict(q=int(r[1]), a=r[2], b=r[3], w=("TIE" if r[6] else ({"Model A": r[2], "Model B": r[3]}.get(r[5], r[5]))), g=anchor_of(r[4])) for r in x12.values()]

    def v2_rows():
        return [dict(q=int(r[3]), a=r[1], b=r[2], w=r[4], g=anchor_of(x12[mid][4])) for mid, r in st.items() if not r[6] and mid in x12]

    def ll(rows_, th):
        s = 0.0
        for r in rows_:
            pr = 1 / (1 + math.exp(-max(-30, min(30, th[r["a"]] - th[r["b"]])))); pr = min(max(pr, 1e-9), 1 - 1e-9)
            s += 0.5 * (math.log(pr) + math.log(1 - pr)) if r["w"] == "TIE" else (math.log(pr) if r["w"] == r["a"] else math.log(1 - pr))
        return s

    def lrt(rows_):
        th0 = jf.board_from(jf.current_votes(rows_), models); l0 = ll(rows_, th0); l1 = 0.0
        by = defaultdict(list)
        for r in rows_: by[r["g"]].append(r)
        for g, sub in by.items():
            l1 += ll(sub, th0) if len(sub) < 50 else ll(sub, jf.board_from(jf.current_votes(sub), models))
        return 2 * (l1 - l0)
    out = {}
    arms = [("x12 v1 (production)", v1_rows()), ("ARENA-V2 (STACK-v2)", v2_rows())]
    if DATACARD:
        base = sqlite3.connect("file:%s?mode=ro" % cache_path().replace("_card.db", ".db"), uri=True)
        stb = {r[0]: r for r in base.execute("SELECT match_id, model_a, model_b, qid, winner, flip, invalid, ref_correct, node_id FROM verdicts")}
        arms = [("x12 v1 (production)", v1_rows()), ("ARENA-V2 (STACK-v2)", [dict(q=int(r[3]), a=r[1], b=r[2], w=r[4], g=anchor_of(x12[mid][4])) for mid, r in stb.items() if not r[6] and mid in x12]),
                ("ARENA-V3 (STACK-v2 + card)", v2_rows())]
    for tag, rows in arms:
        th = jf.board_from(jf.current_votes(rows), models)
        rho = jf.rho(th, acc, models); order_g, pv_g, _ = jf.violations(th, gt_order)
        # registered convention (STACK, STACK-v2, BOARD-W; the comparator "v1: 2"): top-4 board fit on the top-cluster matches
        th4 = jf.board_from(jf.current_votes([r for r in rows if r["a"] in TOP4 and r["b"] in TOP4]), TOP4)
        order, pv, _ = jf.violations(th4, gt_order)
        print("  %-22s top-4 from the 12-model global fit: %s (viol %d)" % (tag, " > ".join(order_g), pv_g))
        dec = [r for r in rows if G.get((r["q"], r["a"])) is not None and G.get((r["q"], r["b"])) is not None and G[(r["q"], r["a"])] != G[(r["q"], r["b"])]]
        accd = sum(r["w"] == (r["a"] if G[(r["q"], r["a"])] else r["b"]) for r in dec) / max(1, len(dec))
        obs = lrt(rows); rng = random.Random(42)
        qs = sorted({r["q"] for r in rows}); qg = {r["q"]: r["g"] for r in rows}; labels = [qg[q] for q in qs]; null = []
        for _ in range(nperm):
            rng.shuffle(labels); m = dict(zip(qs, labels))
            for r in rows: r["g"] = m[r["q"]]
            null.append(lrt(rows))
        p = (sum(1 for v in null if v >= obs) + 1) / (nperm + 1)
        out[tag] = dict(rho=rho, pv=pv, order=order, acc=accd, ndec=len(dec), lrt=obs, p=p, n=len(rows))
        print("  %-22s n=%5d | rho %.4f | top-4 %s (viol %d) | key-decidable acc %.3f (n=%d) | anchor LRT %.2f null p95 %.2f p_perm=%.3f"
              % (tag, len(rows), rho, " > ".join(order), pv, accd, len(dec), obs, float(np.percentile(null, 95)), p), flush=True)
    v = out["ARENA-V3 (STACK-v2 + card)" if DATACARD else "ARENA-V2 (STACK-v2)"]; b = out["x12 v1 (production)"]
    if DATACARD:
        s2 = out["ARENA-V2 (STACK-v2)"]
        print("  ARENA-V3 vs ARENA-V2: rho %.4f vs %.4f | acc %.3f vs %.3f | top-4 viol %d vs %d" % (v["rho"], s2["rho"], v["acc"], s2["acc"], v["pv"], s2["pv"]))
    checks = [("(1) rho >= x12's %.4f" % b["rho"], v["rho"] >= b["rho"]), ("(2) top-4 violations <= 1", v["pv"] <= 1),
              ("(3) anchor LRT p_perm < 0.05", v["p"] < 0.05), ("(4) key-decidable accuracy >= 0.85", v["acc"] >= 0.85)]
    for lab, ok in checks: print("  %-40s %s" % (lab, "OK" if ok else "FAIL"))
    print("  ARENA-V2 REGISTERED: %s  (key order %s)" % ("PASS" if all(c[1] for c in checks) else "FAIL", " > ".join(gt_order)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--prompt", choices=["v1", "v2"], default="v1")
    ap.add_argument("--judge", choices=["mistral", "grok"], default="mistral")
    ap.add_argument("--all-x12", action="store_true")
    ap.add_argument("--datacard", action="store_true")
    a = ap.parse_args()
    PROMPT = a.prompt; JUDGE = a.judge; ALL_X12 = a.all_x12; DATACARD = a.datacard
    az = analyze_arena if ALL_X12 else (analyze_grok if JUDGE == "grok" else analyze)
    if a.analyze: az()
    else: run(a.pilot, a.workers); az()
