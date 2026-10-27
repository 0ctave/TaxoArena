"""K-RECONCILE - FRAMEWORK.md item 10 (docs/design/FRAMEWORK.md, "Tests to register before shipping",
registered by reference at eaf1dbf). Zero calls.

The item, verbatim:

    10. K-RECONCILE. k per (anchor, model) cell under both estimators on ratings_x12.db; declare the
        framework's. Prediction: per-cell 2.06-class values; the per-anchor clustered 4.84 reflects
        cross-model correlation. 0 calls.

The record it cites (FRAMEWORK.md L85 / L207 / L312 "Stage 5 k contested ... UNDETERMINED 2.06 vs 4.84"):
  * the STRESS estimator (docs/design/RESOLVE_stress_statistics.md section 1; scratchpad cellse.py, its
    per-cell pickle cells.pkl): ratings_x12.db match_history, anchor = mmlu_pro.category through
    eval_question_link, an unpenalised BT MM fit (120 iterations from theta = 0, mean-centred), a 400-draw
    question-clustered bootstrap (numpy default_rng(137)), k = q * SE^2 per (anchor, model) cell over all
    168 cells -> median 4.84 (p25 4.01, p75 6.80).
  * the RESOLVE-CALIB estimator (tools/analysis/resolve_calibration.py section A, ledger RESOLVE-CALIB):
    the STACK-v2 re-judged verdicts of the same x12 schedule (stack_v2_promptv2_x12all.db), anchor = the
    bareq512_s42 tree anchor of the question's primary routing, jf.board_from -> rj.mm_fit (a 0.5-win
    pseudo-match PRIOR per observed pair, iterated to 1e-12), a 300-draw question-clustered bootstrap
    (random.Random(42)), anchors with >= 200 matches, cells with q > 10 -> median 2.06 (p10 1.33, p90 3.02).

The item asks for both estimators ON ratings_x12.db, so the verdict source is held at ratings_x12.db and
the two procedures are run as registered (their own fit, draw count, seed, anchor mapping and filters).
Because the two records also differ in verdict source and anchor mapping, the gap is then decomposed one
factor at a time: verdict source (x12 judge vs STACK-v2), anchor mapping (category vs tree anchor), fit
(unpenalised MM at 120 iterations / converged / with the 0.5 pseudo-match prior), and the clustering term.

"Cross-model correlation" is read in the hardest way for the programme: it is the within-question
correlation of verdicts across model pairs that a question-clustered resample carries and a match-level
resample does not, i.e. DEFF = SE_q^2 / SE_match^2 per cell; the off-diagonal correlation of the (B x M)
draw matrix is printed beside it. The prediction that the 4.84 "reflects cross-model correlation" PASSES
only if that clustering term carries the majority of log(4.84 / k_framework); if the majority sits in the
fit's prior (a theta-scale change) or in the mapping, the mechanism named by the prediction is FALSIFIED
even if the 2.06-class value stands.

Criteria (the item states a prediction only; these are the readings applied, stated before the run):
  C1 reproduction: the STRESS procedure on x12/category returns median k within 0.10 of 4.84 and the
     RESOLVE-CALIB procedure on STACK-v2/tree within 0.10 of 2.06 (deterministic seeds).
  C2 "per-cell 2.06-class values": the framework's estimator (jf.board_from + question bootstrap, the
     fit every committed helper uses: systematic_budget, key_tie_decline, budget_transfer,
     profile_reliability, x20_merged) ON ratings_x12.db gives a median k inside RESOLVE-CALIB's own
     p10-p90 band [1.33, 3.02] AND below the design constant 3 (so "k = 3 is conservative" survives on the
     item's DB). Both sub-conditions or FAIL.
  C3 "the 4.84 reflects cross-model correlation": share of log(k_STRESS / k_R_same_data) carried by the
     clustering term log(DEFF) exceeds 0.5. Otherwise the named mechanism fails and the factor that does
     carry the gap is named.
  C4 declaration: which k the framework carries, with its theta scale stated (the pseudo-match prior is
     not declared in FRAMEWORK.md L85, and it shrinks theta; k = q * SE^2 is scale-dependent, so the
     scale-free k_std = q * (SE / SD_cell)^2 is printed beside it under both fits).

Key denominator: 168 = 14 anchors x 12 models (anchor, model) cells; q = distinct judged questions of
ratings_x12.db in the cell (9,144 matches, 2,812 distinct questions). No wrong-direction counts are
produced by this test, so the McNemar-established clause does not apply here (stated, not skipped).
Meta-Llama-3-70B-Instruct is asserted absent. Pool of record p2dca21ab5f4ef3ae asserted first.

  python tools/analysis/k_reconcile.py
  -> experiment_results/x12_crossdomain/k_reconcile.txt
"""
import os, sys, math, random, sqlite3, pickle, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import rejudge_grok as rj
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "k_reconcile.txt")
X12_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "ratings_x12.db")
SCRATCH = r"C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\block1"
CACHE = os.path.join(SCRATCH, "k_reconcile_cache.pkl")
STRESS_PKL = os.path.join(os.path.dirname(SCRATCH), "cells.pkl")   # the stress pass's own per-cell output
EXCLUDED = "Meta-Llama-3-70B-Instruct"
K_STRESS_RECORD, K_RESOLVE_RECORD = 4.84, 2.06
BAND = (1.33, 3.02)

L = []
def say(s=""):
    L.append(s); print(s, flush=True)


# ----------------------------------------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------------------------------------
def load_x12():
    """ratings_x12.db match_history -> list of (match_id, a, b, score_a, qid)."""
    c = sqlite3.connect("file:%s?mode=ro" % X12_DB, uri=True)
    rows = c.execute("SELECT id, model_a, model_b, winner, is_tie, eval_question_id FROM match_history").fetchall()
    out = []
    for mid, a, b, w, t, q in rows:
        assert EXCLUDED not in (a, b)
        s = 0.5 if int(t or 0) else (1.0 if w == a else 0.0)
        out.append((int(mid), a, b, s, int(q)))
    return out


def load_stack_v2():
    """STACK-v2 re-judged verdicts of the same schedule, keyed by match_id -> (a, b, score_a, qid, anchor)."""
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    con = sj.open_cache()
    out = {}
    for mid, a, b, q, anc, w, inv in con.execute("SELECT match_id, model_a, model_b, qid, anchor, winner, invalid FROM verdicts"):
        if inv: continue
        out[int(mid)] = (a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), int(q), anc)
    return out


def category_map():
    m = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    link = dict(m.execute("SELECT question_id, mmlu_pro_row_id FROM eval_question_link WHERE mmlu_pro_row_id IS NOT NULL"))
    rowcat = dict(m.execute("SELECT id, category FROM mmlu_pro"))
    def f(q):
        rid = link.get(q)
        d = rowcat.get(rid) if rid is not None else None
        return d[:1].upper() + d[1:] if d else None
    return f


def tree_map():
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    def f(q):
        return anchor_of(route[q]) if q in route else None
    return f


# ----------------------------------------------------------------------------------------------------------
# fits
# ----------------------------------------------------------------------------------------------------------
def fit_np(ia, ib, sa, sb, M, iters=120, prior=0.0):
    """Hunter MM for BT with fractional wins. prior > 0 adds one pseudo-match of `prior` wins to each side of
    every OBSERVED pair (rj.mm_fit's PRIOR). iters=120 from theta=0 is the stress pass's fit."""
    if prior > 0:
        pairs = np.unique(np.stack([np.minimum(ia, ib), np.maximum(ia, ib)], 1), axis=0)
        ia = np.concatenate([ia, pairs[:, 0]]); ib = np.concatenate([ib, pairs[:, 1]])
        sa = np.concatenate([sa, np.full(len(pairs), prior)]); sb = np.concatenate([sb, np.full(len(pairs), prior)])
    th = np.zeros(M)
    W = np.bincount(ia, weights=sa, minlength=M) + np.bincount(ib, weights=sb, minlength=M)
    n = sa + sb
    for it in range(iters):
        p = np.exp(th); den = p[ia] + p[ib]
        d = np.bincount(ia, weights=n / den, minlength=M) + np.bincount(ib, weights=n / den, minlength=M)
        newp = np.where(d > 0, W / np.maximum(d, 1e-12), p); newp = np.maximum(newp, 1e-9)
        new = np.log(newp); new -= new.mean()
        if iters > 1000 and np.max(np.abs(new - th)) < 1e-9:
            th = new; break
        th = new
    return th


def fit_R(recs, models):
    return jf.board_from([(a, b, s, 1.0) for a, b, s, _ in recs], models)


# ----------------------------------------------------------------------------------------------------------
# the two estimators, each as registered
# ----------------------------------------------------------------------------------------------------------
def estimator_STRESS(by_anchor, models, B=400, seed=137, fit_kind="np120"):
    """cellse.py verbatim in structure: all anchors, all cells, numpy rng, question AND match bootstrap.
    fit_kind: np120 (the stress fit) | npconv (same, converged) | npprior (converged, PRIOR 0.5 = mm_fit)."""
    rng = np.random.default_rng(seed)
    M = len(models); mi = {m: i for i, m in enumerate(models)}
    cells = []; per_anchor = {}
    for anc in sorted(by_anchor):
        recs = by_anchor[anc]
        ia = np.array([mi[r[0]] for r in recs], dtype=np.int64); ib = np.array([mi[r[1]] for r in recs], dtype=np.int64)
        sa = np.array([r[2] for r in recs], dtype=float); sb = 1.0 - sa
        qs = np.array([r[3] for r in recs]); uq, qidx = np.unique(qs, return_inverse=True)
        qgroups = [np.where(qidx == k)[0] for k in range(len(uq))]
        cellq = {i: len(np.unique(qs[(ia == i) | (ib == i)])) for i in range(M)}
        kw = dict(np120=dict(iters=120), npconv=dict(iters=3000), npprior=dict(iters=3000, prior=0.5))[fit_kind]
        th0 = fit_np(ia, ib, sa, sb, M, **(dict(iters=200) if fit_kind == "np120" else kw))
        boots = np.zeros((B, M)); mboots = np.zeros((B, M))
        for b in range(B):
            pick = rng.integers(0, len(uq), len(uq))
            sel = np.concatenate([qgroups[p] for p in pick])
            boots[b] = fit_np(ia[sel], ib[sel], sa[sel], sb[sel], M, **kw)
            sel2 = rng.integers(0, len(recs), len(recs))
            mboots[b] = fit_np(ia[sel2], ib[sel2], sa[sel2], sb[sel2], M, **kw)
        se_q = boots.std(axis=0, ddof=1); se_m = mboots.std(axis=0, ddof=1)
        sd = th0.std(ddof=1)
        corr = np.corrcoef(boots.T); off = corr[~np.eye(M, dtype=bool)]
        per_anchor[anc] = dict(n=len(recs), sd=sd, offcorr=float(off.mean()), B=B)
        for i, m in enumerate(models):
            cells.append(dict(anchor=anc, model=m, q=cellq[i], theta=th0[i], se=se_q[i], se_m=se_m[i],
                              k=se_q[i] ** 2 * cellq[i], deff=(se_q[i] / se_m[i]) ** 2, sd=sd,
                              kstd=cellq[i] * (se_q[i] / sd) ** 2))
    return cells, per_anchor


def estimator_RESOLVE(by_anchor, models, B=300, seed=42, min_matches=200, min_q=10):
    """resolve_calibration.py section (A) verbatim in structure: random.Random(seed), anchors >= 200 matches
    in size order, jf.board_from, cells with q > 10 and se > 0. A match bootstrap is added for DEFF."""
    rng = random.Random(seed)
    cells = []; per_anchor = {}
    M = len(models)
    for anc in sorted(by_anchor, key=lambda a: -len(by_anchor[a])):
        rs = by_anchor[anc]
        if len(rs) < min_matches: continue
        qs = sorted({r[3] for r in rs})
        byq = defaultdict(list)
        for r in rs: byq[r[3]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(fit_R(sub, models))
        mrng = random.Random(seed + 1)
        mdraws = [fit_R([rs[mrng.randrange(len(rs))] for _ in rs], models) for _ in range(B)]
        th0 = fit_R(rs, models)
        supp = defaultdict(set)
        for a, b, _, q in rs: supp[a].add(q); supp[b].add(q)
        mat = np.array([[d[m] for m in models] for d in draws]); mmat = np.array([[d[m] for m in models] for d in mdraws])
        sd = np.std([th0[m] for m in models], ddof=1)
        corr = np.corrcoef(mat.T); off = corr[~np.eye(M, dtype=bool)]
        per_anchor[anc] = dict(n=len(rs), sd=sd, offcorr=float(off.mean()), B=B)
        for j, m in enumerate(models):
            se = mat[:, j].std(ddof=1); se_m = mmat[:, j].std(ddof=1); qn = len(supp[m])
            if qn > min_q and se > 0:
                cells.append(dict(anchor=anc, model=m, q=qn, theta=th0[m], se=se, se_m=se_m, k=qn * se * se,
                                  deff=(se / se_m) ** 2 if se_m > 0 else float("nan"), sd=sd, kstd=qn * (se / sd) ** 2))
    return cells, per_anchor


# ----------------------------------------------------------------------------------------------------------
def q(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]

def med(v):
    v = sorted(v); return v[len(v) // 2]

def summarise(cells, key="k"):
    v = [c[key] for c in cells if not math.isnan(c[key])]
    return dict(n=len(v), med=med(v), p10=q(v, 0.10), p25=q(v, 0.25), p75=q(v, 0.75), p90=q(v, 0.90))


def group(recs_by_mid, mapping, verdicts=None):
    """recs_by_mid: x12 rows. verdicts: optional STACK-v2 dict overriding the score. -> {anchor: [(a,b,s,q)]}"""
    by = defaultdict(list); dropped = 0
    for mid, a, b, s, qid in recs_by_mid:
        if verdicts is not None:
            v = verdicts.get(mid)
            if v is None: dropped += 1; continue
            assert v[0] == a and v[1] == b and v[3] == qid, (mid, v, a, b, qid)
            s = v[2]
        anc = mapping(qid)
        if anc is None: dropped += 1; continue
        by[anc].append((a, b, s, qid))
    return by, dropped


def run_cached(name, fn):
    cache = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}
    if name in cache: return cache[name]
    t = time.time(); res = fn(); cache = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}
    cache[name] = res; pickle.dump(cache, open(CACHE, "wb"))
    print("  [%s: %.0fs]" % (name, time.time() - t), flush=True)
    return res


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    models = sorted(p8.ARENA12); assert EXCLUDED not in models and len(models) == 12
    x12 = load_x12(); sv2 = load_stack_v2()
    cat = category_map(); tree = tree_map()
    nq = len({r[4] for r in x12})
    say("K-RECONCILE (FRAMEWORK.md item 10) - zero calls; pool of record %s asserted" % pool_guard.FROZEN_POOL_ID)
    say("ratings_x12.db: %d matches, %d distinct questions, %d models (%s absent, asserted)" % (len(x12), nq, len(models), EXCLUDED))
    say("STACK-v2 re-judge cache: %d valid verdicts on the same match ids" % len(sv2))
    say("Key denominator: (anchor, model) cells = 14 x 12 = 168; q = distinct judged questions of ratings_x12.db in the cell.")
    say("No wrong-direction counts are produced here; the McNemar-established clause is not applicable to this item.")
    say()

    # anchor mappings and their agreement
    by_cat, d_cat = group(x12, cat); by_tree, d_tree = group(x12, tree)
    agree = sum(1 for r in x12 if cat(r[4]) is not None and tree(r[4]) is not None and cat(r[4]) == tree(r[4]))
    say("=== 0. The two records' anchor mappings on ratings_x12.db ===")
    say("  category (mmlu_pro.category via eval_question_link; the stress pass): %d matches mapped, %d dropped" % (sum(map(len, by_cat.values())), d_cat))
    say("  tree anchor (bareq512_s42 primary routing; RESOLVE-CALIB):           %d matches mapped, %d dropped" % (sum(map(len, by_tree.values())), d_tree))
    say("  matches whose two anchors agree: %d of %d (%.1f%%)" % (agree, len(x12), 100.0 * agree / len(x12)))
    cache_anchor_agree = sum(1 for r in x12 if r[0] in sv2 and tree(r[4]) == sv2[r[0]][4])
    say("  tree anchor == the STACK-v2 cache's own anchor column: %d of %d" % (cache_anchor_agree, len(sv2)))
    say("  %-18s %8s %8s" % ("anchor", "category", "tree"))
    for anc in sorted(set(by_cat) | set(by_tree)):
        say("  %-18s %8d %8d" % (anc, len(by_cat.get(anc, [])), len(by_tree.get(anc, []))))
    say()

    # ---- fit equivalence check: numpy prior fit == rj.mm_fit
    recs = by_tree["Business"]; mi = {m: i for i, m in enumerate(models)}
    ia = np.array([mi[r[0]] for r in recs]); ib = np.array([mi[r[1]] for r in recs]); sa = np.array([r[2] for r in recs])
    a_np = fit_np(ia, ib, sa, 1 - sa, 12, iters=3000, prior=0.5); a_R = fit_R(recs, models)
    dev = max(abs(a_np[i] - a_R[m]) for i, m in enumerate(models))
    say("fit check: numpy MM with PRIOR 0.5 vs rj.mm_fit on tree/Business, max |dtheta| = %.2e (must be < 1e-6)" % dev)
    assert dev < 1e-6
    say()

    # ---- the grid
    configs = [
        ("1 STRESS  | x12 verdicts | category | np120 B400 s137", lambda: estimator_STRESS(by_cat, models)),
        ("2 RESOLVE | x12 verdicts | category | mm_fit B300 s42", lambda: estimator_RESOLVE(by_cat, models)),
        ("3 STRESS  | x12 verdicts | tree     | np120 B400 s137", lambda: estimator_STRESS(by_tree, models)),
        ("4 RESOLVE | x12 verdicts | tree     | mm_fit B300 s42", lambda: estimator_RESOLVE(by_tree, models)),
    ]
    by_sv2_tree, d_sv2 = group(x12, tree, sv2)
    by_sv2_cat, _ = group(x12, cat, sv2)
    configs += [
        ("5 STRESS  | STACK-v2     | tree     | np120 B400 s137", lambda: estimator_STRESS(by_sv2_tree, models)),
        ("6 RESOLVE | STACK-v2     | tree     | mm_fit B300 s42", lambda: estimator_RESOLVE(by_sv2_tree, models)),
        ("7 RESOLVE | STACK-v2     | category | mm_fit B300 s42", lambda: estimator_RESOLVE(by_sv2_cat, models)),
    ]
    # fit-factor isolation on the stress pass's own resamples (x12 verdicts, category, B400 s137)
    configs += [
        ("8 STRESS-fit converged   | x12 | category | npconv B400 s137", lambda: estimator_STRESS(by_cat, models, fit_kind="npconv")),
        ("9 STRESS-fit + PRIOR 0.5 | x12 | category | npprior B400 s137", lambda: estimator_STRESS(by_cat, models, fit_kind="npprior")),
    ]
    R = {}
    for name, fn in configs:
        R[name] = run_cached(name, fn)

    say("=== 1. k = q * SE^2 per (anchor, model) cell: both estimators, and each factor swapped ===")
    say("  %-64s %5s %6s %6s %6s %6s %6s | %6s %6s %6s | %6s %7s" % ("configuration", "cells", "k_med", "k_p10", "k_p25", "k_p75", "k_p90", "SE_med", "SD_med", "kstd", "DEFF", "offcor"))
    S = {}
    for name, _ in configs:
        cells, pa = R[name]
        s = summarise(cells); S[name] = s
        say("  %-64s %5d %6.2f %6.2f %6.2f %6.2f %6.2f | %6.3f %6.3f %6.2f | %6.2f %7.3f" % (
            name, s["n"], s["med"], s["p10"], s["p25"], s["p75"], s["p90"], med([c["se"] for c in cells]),
            med([c["sd"] for c in cells]), summarise(cells, "kstd")["med"], summarise(cells, "deff")["med"], med([v["offcorr"] for v in pa.values()])))
    say("  SE_med = median question-clustered bootstrap SE; SD_med = median across cells of the anchor's theta SD (12 models, point fit);")
    say("  kstd = q * (SE / SD_anchor)^2, scale-free; DEFF = SE_q^2 / SE_match^2 (question-clustered vs match resample) per cell,")
    say("  median; offcor = mean off-diagonal correlation of the (B x 12) mean-centred draw matrix, median over anchors")
    say("  (the centring alone induces -1/11 = -0.091).")
    say()

    # ---- C1 reproduction
    k1 = S[configs[0][0]]["med"]; k6 = S[configs[5][0]]["med"]
    stress_pkl = None
    if os.path.exists(STRESS_PKL):
        try:
            import statistics as _st
            sp = pickle.load(open(STRESS_PKL, "rb")); stress_pkl = _st.median([o[6] for o in sp])
        except Exception: stress_pkl = None
    say("=== 2. C1 reproduction ===")
    say("  Median convention: the stress pass used statistics.median (mean of the two middle cells of 168); resolve_calibration")
    say("  used ks[len // 2] (the upper middle cell). Tables above use the upper middle; each record is compared in its own convention.")
    import statistics
    k1s = statistics.median([c["k"] for c in R[configs[0][0]][0]])
    say("  STRESS procedure on x12/category: median k %.2f (statistics.median %.3f; record 4.84%s)" % (
        k1, k1s, "; the stress pass's own cells.pkl re-read: %.3f" % stress_pkl if stress_pkl else ""))
    say("  RESOLVE-CALIB procedure on STACK-v2/tree: median k %.2f (record 2.06)" % k6)
    c1 = abs(k1s - K_STRESS_RECORD) <= 0.10 and abs(k6 - K_RESOLVE_RECORD) <= 0.10
    say("  C1: %s" % ("PASS" if c1 else "FAIL"))
    say()

    # ---- per-anchor table under both estimators on ratings_x12.db (the item's literal ask)
    say("=== 3. Per anchor, both estimators ON ratings_x12.db (configs 1 and 4; 2 and 3 are the mapping swaps) ===")
    say("  %-18s | %7s %6s %6s %6s | %7s %6s %6s %6s | %7s %6s %6s" % ("anchor", "STR n", "q_med", "k_med", "kstd", "RES n", "q_med", "k_med", "kstd", "RESc n", "k_med", "kstd"))
    c1c, _ = R[configs[0][0]]; c4c, _ = R[configs[3][0]]; c2c, _ = R[configs[1][0]]
    def row(cells, anc):
        cc = [c for c in cells if c["anchor"] == anc]
        if not cc: return None
        return (len(cc), med([c["q"] for c in cc]), med([c["k"] for c in cc]), med([c["kstd"] for c in cc]))
    for anc in sorted(set(c["anchor"] for c in c1c) | set(c["anchor"] for c in c4c)):
        r1 = row(c1c, anc); r4 = row(c4c, anc); r2 = row(c2c, anc)
        f = lambda r, n: ("%7d %6d %6.2f %6.2f" % (n, r[1], r[2], r[3])) if r else "%7s %6s %6s %6s" % ("-", "-", "-", "-")
        say("  %-18s | %s | %s | %s" % (anc, f(r1, len(by_cat.get(anc, []))), f(r4, len(by_tree.get(anc, []))),
                                        ("%7d %6.2f %6.2f" % (len(by_cat.get(anc, [])), r2[2], r2[3])) if r2 else "%7s %6s %6s" % ("-", "-", "-")))
    say("  STR = STRESS estimator, category anchors; RES = RESOLVE-CALIB estimator, tree anchors; RESc = RESOLVE-CALIB estimator, category anchors.")
    say()

    # ---- per-cell listing for the framework's estimator on x12 (config 4)
    say("=== 4. Per-cell k under the framework's estimator on ratings_x12.db (config 4), sorted by k ===")
    say("  %-18s %-28s %5s %7s %7s %6s %6s %6s" % ("anchor", "model", "q", "theta", "SE", "k", "kstd", "DEFF"))
    for c in sorted(c4c, key=lambda c: c["k"]):
        say("  %-18s %-28s %5d %7.3f %7.3f %6.2f %6.2f %6.2f" % (c["anchor"], c["model"], c["q"], c["theta"], c["se"], c["k"], c["kstd"], c["deff"]))
    say()

    # ---- decomposition
    say("=== 5. Decomposition of log(4.84 / 2.06) into factors (medians of k; each step changes ONE thing) ===")
    k = {n: S[n]["med"] for n, _ in configs}
    n1, n2, n3, n4, n5, n6, n7, n8, n9 = [n for n, _ in configs]
    total = math.log(k[n1] / k[n6])
    steps = [
        ("fit: np120 -> converged (same resamples, x12/category)", k[n1], k[n8]),
        ("fit: converged -> + PRIOR 0.5 pseudo-match (= mm_fit)", k[n8], k[n9]),
        ("procedure: npprior/B400/s137/all cells -> mm_fit/B300/s42/q>10 (x12/category)", k[n9], k[n2]),
        ("anchor mapping: category -> tree (RESOLVE procedure, x12 verdicts)", k[n2], k[n4]),
        ("verdict source: x12 judge -> STACK-v2 (RESOLVE procedure, tree)", k[n4], k[n6]),
    ]
    say("  %-84s %6s %6s %8s %6s" % ("step", "from", "to", "log-gap", "share"))
    for lab, a, b in steps:
        say("  %-84s %6.2f %6.2f %+8.3f %5.0f%%" % (lab, a, b, math.log(a / b), 100 * math.log(a / b) / total))
    say("  %-84s %6.2f %6.2f %+8.3f %5.0f%%" % ("TOTAL", k[n1], k[n6], total, 100))
    alt = [("verdict source first: x12 -> STACK-v2 (RESOLVE, category)", k[n2], k[n7]), ("then mapping: category -> tree (RESOLVE, STACK-v2)", k[n7], k[n6])]
    say("  order check (mapping and verdict source swapped):")
    for lab, a, b in alt:
        say("  %-84s %6.2f %6.2f %+8.3f %5.0f%%" % (lab, a, b, math.log(a / b), 100 * math.log(a / b) / total))
    say()

    # ---- C2
    say("=== 6. C2 - 'per-cell 2.06-class values' under the framework's estimator on ratings_x12.db ===")
    kR = k[n4]; s4 = S[n4]
    say("  config 4 (RESOLVE-CALIB procedure, x12 verdicts, tree anchors): k median %.2f, p10 %.2f, p90 %.2f over %d cells" % (kR, s4["p10"], s4["p90"], s4["n"]))
    say("  config 2 (same procedure, category anchors):                       k median %.2f, p10 %.2f, p90 %.2f" % (k[n2], S[n2]["p10"], S[n2]["p90"]))
    in_band = BAND[0] <= kR <= BAND[1]; below3 = kR < 3.0
    say("  inside RESOLVE-CALIB's p10-p90 band [%.2f, %.2f]: %s; below the design constant 3: %s" % (BAND[0], BAND[1], in_band, below3))
    c2 = in_band and below3
    say("  hardest reading: the same holds for the category mapping too: %s" % (BAND[0] <= k[n2] <= BAND[1] and k[n2] < 3))
    say("  C2: %s" % ("PASS" if c2 else "FAIL"))
    say()

    # ---- C3
    say("=== 7. C3 - does the 4.84 'reflect cross-model correlation'? ===")
    deff1 = summarise(R[n1][0], "deff")["med"]; deff4 = summarise(R[n4][0], "deff")["med"]; deff6 = summarise(R[n6][0], "deff")["med"]
    off1 = med([v["offcorr"] for v in R[n1][1].values()]); off6 = med([v["offcorr"] for v in R[n6][1].values()])
    same_data_gap = math.log(k[n1] / k[n2])
    share_cluster = math.log(deff1) / same_data_gap if same_data_gap > 0 else float("nan")
    share_fit = math.log(k[n1] / k[n9]) / same_data_gap if same_data_gap > 0 else float("nan")
    say("  The clustering term: DEFF = (question-clustered SE / match-resampled SE)^2, per cell, median:")
    say("    STRESS estimator, x12/category (config 1): DEFF %.2f; mean off-diagonal draw correlation %+.3f (centring baseline -0.091)" % (deff1, off1))
    say("    RESOLVE estimator, x12/tree (config 4):    DEFF %.2f" % deff4)
    say("    RESOLVE estimator, STACK-v2/tree (config 6): DEFF %.2f; off-diagonal %+.3f" % (deff6, off6))
    say("  Under the STRESS estimator, removing the clustering entirely (match resample) would give k %.2f, not 2.06." % (k[n1] / deff1))
    say("  Same-data gap, STRESS -> RESOLVE procedure on x12/category: log(%.2f / %.2f) = %.3f" % (k[n1], k[n2], same_data_gap))
    say("    share carried by the clustering term log(DEFF):      %5.0f%%" % (100 * share_cluster))
    say("    share carried by the fit (np120 -> mm_fit prior):    %5.0f%%" % (100 * share_fit))
    say("    theta SD, STRESS fit vs prior fit (median over anchors): %.3f vs %.3f (ratio %.2f); scale-free kstd: %.2f vs %.2f" % (
        med([v["sd"] for v in R[n1][1].values()]), med([v["sd"] for v in R[n9][1].values()]),
        med([v["sd"] for v in R[n1][1].values()]) / med([v["sd"] for v in R[n9][1].values()]),
        summarise(R[n1][0], "kstd")["med"], summarise(R[n9][0], "kstd")["med"]))
    c3 = share_cluster > 0.5
    say("  C3 (clustering term carries > 50%% of the gap): %s" % ("PASS" if c3 else "FAIL"))
    say()

    # ---- C4 declaration
    say("=== 8. C4 - the framework's k ===")
    say("  Every committed helper the certificate rests on (systematic_budget, key_tie_decline, budget_transfer,")
    say("  profile_reliability, x20_merged) fits boards with jf.board_from -> rj.mm_fit, i.e. the RESOLVE-CALIB fit:")
    say("  a 0.5-win pseudo-match on each side of every observed pair, iterated to convergence, mean-centred; the")
    say("  question-clustered bootstrap is the SE. That is the framework's estimator, and FRAMEWORK.md L85 does not")
    say("  declare the pseudo-match. Its k on the item's DB (ratings_x12.db, tree anchors): median %.2f [p10 %.2f, p90 %.2f];" % (kR, s4["p10"], s4["p90"]))
    say("  on the STACK-v2 verdicts the certificate actually uses: %.2f [%.2f, %.2f]." % (k6, S[n6]["p10"], S[n6]["p90"]))
    say("  The unpenalised fit's %.2f is the same data on a wider theta scale (SD ratio %.2f): k = q * SE^2 is not scale-free," % (
        k[n1], med([v["sd"] for v in R[n1][1].values()]) / med([v["sd"] for v in R[n9][1].values()])))
    say("  and the two records' k values are not the same quantity. The range [2.06, 4.84] carried at FRAMEWORK.md L207 mixes scales.")
    say("  DECLARED: k_framework = q * SE^2 under jf.board_from + question-clustered bootstrap, per cell, on the judge of")
    say("  record's verdicts, with the pseudo-match prior stated; forecast range on ratings_x12.db = [p10, p90] of config 4 =")
    say("  [%.2f, %.2f]; the scale-free companion kstd = q * (SE / SD_anchor)^2, median %.2f (STRESS fit) vs %.2f (framework fit)." % (
        s4["p10"], s4["p90"], summarise(R[n1][0], "kstd")["med"], summarise(R[n4][0], "kstd")["med"]))
    say()

    say("=== VERDICTS ===")
    say("  C1 reproduction of both records:                 %s  (%.3f vs 4.84; %.2f vs 2.06)" % ("PASS" if c1 else "FAIL", k1s, k6))
    say("  C2 2.06-class under the framework's k on x12:    %s  (median %.2f; band [1.33, 3.02]; < 3)" % ("PASS" if c2 else "FAIL", kR))
    say("  C3 4.84 reflects cross-model correlation:        %s  (clustering share %.0f%%; fit share %.0f%%; DEFF %.2f)" % ("PASS" if c3 else "FAIL", 100 * share_cluster, 100 * share_fit, deff1))
    say("  C4 framework's k declared:                       DECLARED (jf.board_from fit + question bootstrap; prior stated; range [%.2f, %.2f] on x12)" % (s4["p10"], s4["p90"]))
    say("  Prediction as registered: %s" % ("PASS" if (c2 and c3) else ("PARTIAL - the value class holds, the mechanism does not" if c2 else "FAIL")))
    open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("-> %s" % OUT)


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    main()
