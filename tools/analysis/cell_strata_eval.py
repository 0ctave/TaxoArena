"""cell_strata_eval.py: CELL-STRATA-EVAL -- does AF-U-cell-stratified item sampling estimate a held-out model's EVAL accuracy with
lower error than simple random sampling, source strata or k-means strata, with an IRT-anchor [TS] ceiling beside? ZERO calls: no
judge, no LLM, no embedding call, no construction, no Gradle. A CPU readout of keyed correctness (SQ4, evaluation price).

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CELL-STRATA-EVAL: does AF-U-cell-stratified item
  sampling estimate a held-out model's EVAL accuracy with lower error than simple random sampling, source strata or k-means strata
  ..." L24416-L24428 (_as_of 633255f2): CS1 (DECIDING), CS2 (deciding, vs STRAT-SRC and vs STRAT-K0), Support (a)-(g), P1-P3, F-CS.
  Source: docs/literature/2026-10-04_response_structure.md T-R2. STRAT-AF / STRAT-K0 / STRAT-SRC are [SC] (like with like); RAND
  is a design contrast; IRT-ANCHOR is [TS] (other models' responses), a ceiling, NEVER ranked.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or anywhere with --data-root <main checkout>; POOL READER, rule 7):
  0. python tools/analysis/cell_strata_eval.py --selftest     # synthetic sealed fixture views under E:/TaxoArena_tmp; NO DB of record
     python tools/analysis/cell_strata_eval.py --mutants      # the mutant table, re-run
  1. python tools/analysis/cell_strata_eval.py --dry-run      # POOL line first; pins; policy; cells; denominators; the plan
  2. python tools/analysis/cell_strata_eval.py --run          # ONE TRAIN key read, ONE EVAL key read (B1 marker); outcome WRITE-ONCE:
       experiment_results/archv2/cell_strata_eval/cell_strata_eval_outcome.txt (+ cell_strata_eval.READ_STARTED); never committed
  CPU: about 30-60 min (18 x 4 x 500 draws per arm; 36,000 k-means fits for IRT-ANCHOR). Then the reviewer, the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; write-once paths absent; (2) pins; (3) frozen policy, manifest, AF-U / K0..K4 cells; (4) TRAIN key; EVAL key (B1
  marker; 5,907 / 5,404); (5) B3 + IDENTITY at the point; (6) per held-out model m (18), the TRAIN 3PL on the OTHER 17 models
  and the EVAL item parameters from the other 17 (IRT-ANCHOR / gp-IRT / Neyman use no outcome of m); (7) per (m, n, arm), 500
  draws; absolute errors against m's EVAL accuracy on the 5,907 items; (8) the model-clustered bootstrap at n 100; CS1, CS2, F-CS,
  descriptive table (n 50 / 100 / 200 / 400), predictions, Support; the outcome written (mode "x").

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  CS-R1 Stratified arms (STRAT-AF / K_s / SRC; the strata = the EVAL items' cells): proportional allocation e_h = n N_h / N made
        integer by systematic rounding of the fractional parts (cells in index order, one uniform start; total exactly n; each
        cell's realised n_h is floor(e_h) or floor(e_h) + 1 with E n_h = e_h), simple random sampling without replacement inside
        each cell; the cell-weighted (Horvitz-Thompson) estimator sum_{i in s} y_i / pi_i / N with pi_i = e_h / N_h (= n / N for
        proportional allocation, i.e. the sample mean; unbiased though most AF-U cells get e_h < 1 at n 100 against 123 cells).
        RAND = the same with one stratum (simple random sampling, the sample mean).
        [DELTA D-CS1, READY_resp_structure (BLOCKER), insertion only] The systematic rounding no longer walks the cells in index
        order (AF-U node-id order carries tree adjacency: an unregistered implicit stratification only STRAT-AF got). In EVERY
        stratified arm (STRAT-AF, STRAT-K0..K4, STRAT-SRC, NEYMAN; RAND trivially) and on every draw, the source blocks stay in
        sorted order and the cells inside each block are put in a uniform random order (one rng.permutation per block); the block
        of a cell = the modal stratum source of its EVAL items (ties: the sorted-first source). Stream per draw: the permutations
        FIRST, then the systematic start u, then the N keys; the seed streams of CS-R2 are unchanged. The HT pi is unchanged.
  CS-R2 Seeds: (m, n, arm) -> default_rng(20261004 + index), index = (m_index x 4 + n_index) x 10 + arm_index, arm order RAND 0,
        STRAT-AF 1, STRAT-K0..K4 2-6, STRAT-SRC 7, IRT-ANCHOR 8, NEYMAN 9; 500 draws per stream; STRAT-AF+IRT reuses STRAT-AF's
        samples (index 1). m in the sorted roster order; n in (50, 100, 200, 400).
  CS-R3 IRT for held-out m: theta of the other 17 models from their TRAIN responses (IRT-R1), EVAL item parameters (a_i, b_i) from
        their EVAL responses with that theta fixed (IRT-R2). IRT-ANCHOR (tinyBenchmarks-style): per draw, k-means (scikit-learn
        KMeans, n_clusters = n, n_init 1, random_state = the draw's integer from the stream) on the EVAL items' (a_i, b_i); the anchor
        of a cluster = its member nearest the cluster centre (ties: the smaller position); estimate = sum over non-empty clusters of
        (cluster size / N) x y_anchor,m.
  CS-R4 STRAT-AF+IRT (gp-IRT form; descriptive): on STRAT-AF's sample, theta_m = the MAP (N(0, 1) prior) of m's sampled responses
        under the other-17 item parameters; p_pIRT = (sum_{i in s} y_im + sum_{i not in s} P_i(theta_m)) / N; estimate = lambda x
        p_strat + (1 - lambda) x p_pIRT with lambda = b2 / (b2 + v), v = p_strat (1 - p_strat) / n, b2 = mean over the other 17
        models j of (mean_i P_ij - acc_j)^2 (their EVAL IRT bias, no outcome of m). A stated reading, not tinyBenchmarks' exact
        lambda heuristic (not verified in this pass).
  CS-R5 NEYMAN (descriptive): over AF-U cells, e_h proportional to N_h S_h, S_h = sqrt(mean over the other 17 models of
        p_hj (1 - p_hj)) floored at 0.05, capped at N_h (excess re-allocated in proportion), CS-R1's rounding and HT estimator.
  CS-R6 Metric: MAE over models and draws of |estimate - acc_m|; STRAT-K0's MAE = the mean over s of MAE(K_s) (each seed its own
        draws); spread_K = max - min over the five MAE(K_s) at n 100.
  CS-R7 The interval: B 2,000 two-level bootstrap (default_rng(20261004)): 18 models resampled with replacement, then each sampled
        model's 500 draws resampled with replacement (the same draw indices for every arm of that model); percentile 2.5 / 97.5
        (union_cells_io.pct). CS1 BEATS-RAND iff the ratio MAE(STRAT-AF) / MAE(RAND) < 1 AND its upper end < 1; CS2 per comparator:
        D = MAE(STRAT-AF) - MAE(comparator); AF-BETTER iff the upper end < 0 AND |D| > spread_K; AF-NOT-BETTER iff D >= 0; UNDETERMINED
        otherwise. SE of the log ratio = SD of the replicates' log ratio; MDE80 = 2.8 SE.
  CS-R8 Predictions: "X [lo, hi]" HELD iff lo <= X <= hi (closed); CS1's probability by Brier; P2's three outcome probabilities by the
        multi-category Brier sum_k (p_k - o_k)^2.
  CS-R9 The common hygiene's two-stage bootstrap (B 2,000 over CK-CLOSE components) has no consumer here: the registration's interval
        is the model-clustered one (CS-R7); not run.
  Not applicable (stated): no judge verdict (keyed correctness): no wrong(established), no tie conventions; no call cache, --pilot
  or truncation guard (zero calls).

SELFTEST (--selftest; fixtures on E: through scratch_dir): resp_structure_common's sealed gen / eval fixture views; pool stubbed.
  irt         IRT-R1 / IRT-R2 against scipy
  constants   the REAL registered constants (n grid, n 100 deciding, 500 draws, seeds, B 2,000, floors, arm order)
  sampling    the CS-R1 sampler by value: exact total n, every cell's n_h in {floor, floor + 1} with the right frequencies, HT = the
              sample mean under proportional allocation, unbiasedness on a known population, Neyman capping, KMeans anchors
  e2e         run() on the PLANTED fixture: every arm's MAE at every n, the n-deciding ratio and differences and their bootstrap
              percentiles, spread_K, CS1 / CS2 words against an independent loop oracle (its own sampler loops on the same streams,
              its own LOO IRT, its own bootstrap); F-CS; predictions by value; outcome = printed; a second run refused
  branches    CS1 / CS2 (three words, strict edges) / F-CS / P1-P3 lines by value on synthetic st
  refusals    identity, B3, pool rc 1 (POOL line first), write-once outcome / marker, write_outcome on an existing path; no outcome
  dry_run     POOL line first; denominators; the plan; no key read; nothing written
  branch_cover every print branch registered in BRANCHES was executed
MUTANTS: see MUTANTS at the end (run with --mutants; the table with the result is in the commit message).
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import json          # noqa: E402
import math          # noqa: E402
import argparse      # noqa: E402
import warnings      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _pre(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


if __name__ == "__main__" and _pre(sys.argv[1:]):
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_pre(sys.argv[1:]))
import resp_structure_common as RSC   # noqa: E402

U, V = RSC.U, RSC.V
TAG = "[CELL-STRATA-EVAL]"
TEST_ID = "CELL-STRATA-EVAL"
REG_TXT = ('docs/judge_v2_program.md "## Registered 2026-10-04 (before any code or call) — CELL-STRATA-EVAL: does AF-U-cell-stratified'
           ' item sampling estimate a held-out model\'s EVAL accuracy with lower error ..." L24416-L24428 (_as_of 633255f2)')
RP_ = dict(ns=(50, 100, 200, 400), n_dec=100, draws=500, seed=20261004, B=2000, boot_seed=20261004, s_floor=0.05,
           out_dir="experiment_results/archv2/cell_strata_eval", outcome="cell_strata_eval_outcome.txt", marker="cell_strata_eval.READ_STARTED")
_RP = [RP_]
ARM_IDX = (("RAND", 0), ("STRAT-AF", 1), ("STRAT-K0", 2), ("STRAT-K1", 3), ("STRAT-K2", 4), ("STRAT-K3", 5), ("STRAT-K4", 6),
           ("STRAT-SRC", 7), ("IRT-ANCHOR", 8), ("NEYMAN", 9))
N_ARM_IDX = 10
SHOWN = ("RAND", "STRAT-AF", "STRAT-K0 (mean s0-4)", "STRAT-SRC", "IRT-ANCHOR", "STRAT-AF+IRT", "NEYMAN")
PRED = dict(P1=(0.70, 0.97), P1_prob=0.75, P2={"AF-BETTER": 0.15, "UNDETERMINED": 0.55, "AF-NOT-BETTER": 0.30}, P3=(0.50, 0.90))
HIT = Counter()
BRANCHES = ("CS1.BEATS", "CS1.NOT", "CS2.AF_BETTER", "CS2.NOT_BETTER", "CS2.UNDET", "FCS.FIRED", "FCS.NOT_FIRED", "DRY.DONE", "RUN.DONE")


def hit(name):
    HIT[name] += 1


def R():
    return _RP[0]


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── sampling (CS-R1, CS-R5) ────────────────────────────────────────────────────────────────────────────────────────────
def prop_alloc(Nh, n):
    return n * Nh / Nh.sum()


def neyman_alloc(Nh, Sh, n):
    """CS-R5: e_h proportional to N_h S_h, capped at N_h with the excess re-allocated in proportion."""
    e = np.zeros(len(Nh))
    free = np.ones(len(Nh), dtype=bool)
    left = float(n)
    for _ in range(len(Nh) + 1):
        w = Nh * Sh * free
        if w.sum() <= 0:
            break
        e_try = left * w / w.sum()
        over = free & (e_try > Nh)
        if not over.any():
            e[free] = e_try[free]
            break
        e[over] = Nh[over]
        left -= Nh[over].sum()
        free &= ~over
    return e


def systematic(e, u):
    """CS-R1: integer allocation from e (sum e = n) by systematic rounding of the fractional parts with start u."""
    fl = np.floor(e + 1e-12)
    f = np.clip(e - fl, 0.0, None)
    Rr = int(round(f.sum()))
    alloc = fl.astype(np.int64)
    if Rr > 0:
        C = np.cumsum(f)
        pts = u + np.arange(Rr)
        h = np.minimum(np.searchsorted(C, pts, side="left"), len(e) - 1)
        np.add.at(alloc, h, 1)
    return alloc


def cell_blocks(gE, srcE, H):
    """D-CS1: the source block of every cell = the modal stratum source of its EVAL items (ties: the sorted-first source); block
    ids follow the sorted source names."""
    names = sorted(set(srcE))
    pos = {s_: j for j, s_ in enumerate(names)}
    cnt = np.zeros((H, len(names)), dtype=np.int64)
    np.add.at(cnt, (gE, np.array([pos[s_] for s_ in srcE], dtype=np.int64)), 1)
    return cnt.argmax(axis=1).astype(np.int64)


def cell_order(rng, block):
    """D-CS1: the source blocks in sorted order; inside each block a uniform random permutation of its cells (one
    rng.permutation per block, blocks in sorted order)."""
    out = []
    for b in np.unique(block):
        mem = np.flatnonzero(block == b)
        out.append(mem[rng.permutation(len(mem))])
    return np.concatenate(out)


def strat_draws(rng, gE, e, y, ndraw, block, keep=False):
    """CS-R1 as amended by D-CS1: ndraw stratified draws on the strata gE (0..H-1) with expected allocation e; per draw the
    stream gives the within-source cell permutation FIRST, then the systematic start u, then N keys -> (estimates, selections)."""
    N = len(gE)
    H = len(e)
    Nh = np.bincount(gE, minlength=H).astype(np.float64)
    pi = (e / np.where(Nh > 0, Nh, 1.0))[gE]
    start = np.concatenate([[0], np.cumsum(Nh)[:-1]]).astype(np.int64)
    est = np.empty(ndraw)
    sels = [] if keep else None
    for d in range(ndraw):
        perm = cell_order(rng, block)
        alloc = np.empty(H, dtype=np.int64)
        alloc[perm] = systematic(e[perm], rng.random())
        keys = rng.random(N)
        order = np.lexsort((keys, gE))
        rank = np.arange(N) - start[gE[order]]
        chosen = order[rank < alloc[gE[order]]]
        est[d] = (y[chosen] / pi[chosen]).sum() / N
        if keep:
            sels.append(chosen)
    return est, sels


def kmeans_anchor(X, n, seed):
    """CS-R3: k-means (n clusters) on X; per non-empty cluster the member nearest its centre -> (anchor positions, weights)."""
    from sklearn.cluster import KMeans
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        km = KMeans(n_clusters=n, n_init=1, random_state=int(seed)).fit(X)
    lab = km.labels_
    anc, w = [], []
    for k in range(n):
        mem = np.flatnonzero(lab == k)
        if not len(mem):
            continue
        d = ((X[mem] - km.cluster_centers_[k]) ** 2).sum(axis=1)
        anc.append(int(mem[int(np.argmin(d))]))
        w.append(len(mem) / len(X))
    return np.array(anc, dtype=np.int64), np.array(w)


def theta_map(y, a, b, c, iters=30):
    """CS-R4: MAP of one model's theta from its sampled responses (N(0, 1) prior), Newton with step halving."""
    t = 0.0
    def obj(t_):
        P = np.clip(c + (1 - c) / (1 + np.exp(-a * (t_ - b))), RSC.EPS, 1 - RSC.EPS)
        return (y * np.log(P) + (1 - y) * np.log(1 - P)).sum() - 0.5 * t_ ** 2
    f0 = obj(t)
    for _ in range(iters):
        s = 1 / (1 + np.exp(-a * (t - b)))
        P = np.clip(c + (1 - c) * s, RSC.EPS, 1 - RSC.EPS)
        q = (1 - c) * s * (1 - s)
        g = ((y - P) / (P * (1 - P)) * q * a).sum() - t
        I = ((q * a) ** 2 / (P * (1 - P))).sum() + 1.0
        step = g / I
        for _h in range(30):
            f1 = obj(t + step)
            if f1 >= f0 - 1e-12:
                break
            step *= 0.5
        t, f0 = t + step, f1
        if abs(step) < 1e-9:
            break
    return t


def loo_irt(D, mi):
    """CS-R3: theta of the other models (TRAIN), EVAL item parameters from the other models with that theta fixed."""
    RSC.assert_train(D, D.T)
    keep = [j for j in range(len(D.models)) if j != mi]
    cT = RSC.floors_of([D.src[k] for k in D.T])
    cE = RSC.floors_of([D.src[k] for k in D.E])
    ft = RSC.fit_train(D.A[D.T][:, keep].astype(np.float64), cT)
    if not ft["converged"]:
        refuse("the TRAIN 3PL without %s did not converge" % D.models[mi])
    YE = D.A[D.E].astype(np.float64)
    aE, bE, _i, mx = RSC.fit_items(YE[:, keep], cE, ft["theta"])
    if mx >= 1e-6:
        refuse("the EVAL item fit without %s did not converge" % D.models[mi])
    P = RSC.prob(ft["theta"], aE, bE, cE)
    acc = YE[:, keep].mean(axis=0)
    b2 = float(((P.mean(axis=0) - acc) ** 2).mean())
    return dict(keep=keep, theta=ft["theta"], a=np.exp(aE), alpha=aE, b=bE, c=cE, b2=b2)


def cells_E(D, g):
    _u, inv = np.unique(np.asarray(g)[D.E], return_inverse=True)
    return inv.astype(np.int64), int(inv.max()) + 1


def model_errors(D, arms, mi, irt, ns):
    """Every arm's absolute errors for held-out model mi -> {n: {arm: array(draws)}}."""
    c = R()
    YE = D.A[D.E].astype(np.float64)
    y = YE[:, mi]
    acc = float(y.mean())
    N = len(y)
    gs = {nm: cells_E(D, arms[nm][0]) for nm in ("AF-U",) + RSC.KNAMES + ("SRC",)}
    srcE = [D.src[k] for k in D.E]
    bl = {nm: cell_blocks(gs[nm][0], srcE, gs[nm][1]) for nm in gs}
    gA, HA = gs["AF-U"]
    others = YE[:, irt["keep"]]
    ph = np.zeros((HA, others.shape[1]))
    np.add.at(ph, gA, others)
    NhA = np.bincount(gA, minlength=HA).astype(np.float64)
    ph /= NhA[:, None]
    Sh = np.maximum(np.sqrt((ph * (1 - ph)).mean(axis=1)), c["s_floor"])
    X = np.column_stack([irt["a"], irt["b"]])
    out = {}
    nis = {n: j for j, n in enumerate(c["ns"])}
    for n in ns:
        ni = nis[n]
        res = {}

        def rng_of(ai):
            return np.random.default_rng(c["seed"] + (mi * len(c["ns"]) + ni) * N_ARM_IDX + ai)
        one = np.zeros(N, dtype=np.int64)
        est, _s = strat_draws(rng_of(0), one, np.array([float(n)]), y, c["draws"], np.zeros(1, dtype=np.int64))
        res["RAND"] = np.abs(est - acc)
        est, sels = strat_draws(rng_of(1), gA, prop_alloc(NhA, n), y, c["draws"], bl["AF-U"], keep=True)
        res["STRAT-AF"] = np.abs(est - acc)
        for s in RSC.KSEEDS:
            g, H = gs["K%d" % s]
            est, _s = strat_draws(rng_of(2 + s), g, prop_alloc(np.bincount(g, minlength=H).astype(np.float64), n), y, c["draws"], bl["K%d" % s])
            res["STRAT-K%d" % s] = np.abs(est - acc)
        g, H = gs["SRC"]
        est, _s = strat_draws(rng_of(7), g, prop_alloc(np.bincount(g, minlength=H).astype(np.float64), n), y, c["draws"], bl["SRC"])
        res["STRAT-SRC"] = np.abs(est - acc)
        rg = rng_of(8)
        e8 = np.empty(c["draws"])
        for d in range(c["draws"]):
            anc, w = kmeans_anchor(X, n, rg.integers(0, 2 ** 31 - 1))
            e8[d] = (w * y[anc]).sum()
        res["IRT-ANCHOR"] = np.abs(e8 - acc)
        est, _s = strat_draws(rng_of(9), gA, neyman_alloc(NhA, Sh, n), y, c["draws"], bl["AF-U"])
        res["NEYMAN"] = np.abs(est - acc)
        # STRAT-AF+IRT on STRAT-AF's samples (CS-R4)
        e6 = np.empty(c["draws"])
        pi = n / N
        for d, ch in enumerate(sels):
            ps = (y[ch] / pi).sum() / N
            t = theta_map(y[ch], irt["a"][ch], irt["b"][ch], irt["c"][ch])
            P = np.clip(irt["c"] + (1 - irt["c"]) / (1 + np.exp(-irt["a"] * (t - irt["b"]))), RSC.EPS, 1 - RSC.EPS)
            mask = np.ones(N, dtype=bool)
            mask[ch] = False
            pirt = (y[ch].sum() + P[mask].sum()) / N
            v = ps * (1 - ps) / n
            lam = irt["b2"] / (irt["b2"] + v) if (irt["b2"] + v) > 0 else 1.0
            e6[d] = lam * ps + (1 - lam) * pirt
        res["STRAT-AF+IRT"] = np.abs(e6 - acc)
        out[n] = res
    return out, acc


def mae_table(errs, n):
    """CS-R6 -> {shown arm: MAE} at n, with the five K_s MAEs."""
    M = {}
    for arm in ("RAND", "STRAT-AF", "STRAT-SRC", "IRT-ANCHOR", "STRAT-AF+IRT", "NEYMAN"):
        M[arm] = float(np.mean([errs[m][n][arm] for m in range(len(errs))]))
    ks = [float(np.mean([errs[m][n]["STRAT-K%d" % s] for m in range(len(errs))])) for s in RSC.KSEEDS]
    M["STRAT-K0 (mean s0-4)"] = float(np.mean(ks))
    return M, ks


def cluster_boot(errs, n):
    """CS-R7: the two-level model-clustered bootstrap at n -> replicate arrays of ratio, D_SRC, D_K0, IRT ratio."""
    c = R()
    rng = np.random.default_rng(c["boot_seed"])
    M = len(errs)
    Dn = c["draws"]
    E = {arm: np.array([errs[m][n][arm] for m in range(M)]) for arm in ("RAND", "STRAT-AF", "STRAT-SRC", "IRT-ANCHOR")}
    EK = [np.array([errs[m][n]["STRAT-K%d" % s] for m in range(M)]) for s in RSC.KSEEDS]
    rat, dsrc, dk, irt = [], [], [], []
    for _b in range(c["B"]):
        mi = rng.integers(0, M, M)
        ji = rng.integers(0, Dn, (M, Dn))
        mae = {arm: float(E[arm][mi[:, None], ji].mean()) for arm in E}
        k0 = float(np.mean([e_[mi[:, None], ji].mean() for e_ in EK]))
        rat.append(mae["STRAT-AF"] / mae["RAND"])
        dsrc.append(mae["STRAT-AF"] - mae["STRAT-SRC"])
        dk.append(mae["STRAT-AF"] - k0)
        irt.append(mae["IRT-ANCHOR"] / mae["RAND"])
    return dict(rat=np.array(rat), dsrc=np.array(dsrc), dk=np.array(dk), irt=np.array(irt))


def ci(x):
    s = sorted(np.asarray(x).tolist())
    return U.pct(s, 0.025), U.pct(s, 0.975)


def cs2_word(D, hi, spread):
    if hi < 0 and abs(D) > spread:
        return "AF-BETTER"
    if D >= 0:
        return "AF-NOT-BETTER"
    return "UNDETERMINED"


def analyze(D, arms, say=None):
    c = R()
    errs, accs = [], []
    for mi, m in enumerate(D.models):
        irt = loo_irt(D, mi)
        e, acc = model_errors(D, arms, mi, irt, c["ns"])
        errs.append(e)
        accs.append(acc)
        if say:
            say("%s held-out %-32s EVAL accuracy %.4f; other-17 IRT bias^2 %.6f; done" % (TAG, m, acc, irt["b2"]))
    st = dict(N=len(D.E), G=D.eval_units["n_units"], M=len(D.models), models=list(D.models), accs=accs)
    st["mae"], st["ks"] = {}, {}
    for n in c["ns"]:
        st["mae"][n], st["ks"][n] = mae_table(errs, n)
    n = c["n_dec"]
    bt = cluster_boot(errs, n)
    M = st["mae"][n]
    st["ratio"] = M["STRAT-AF"] / M["RAND"]
    st["ratio_ci"] = ci(bt["rat"])
    st["dsrc"] = M["STRAT-AF"] - M["STRAT-SRC"]
    st["dsrc_ci"] = ci(bt["dsrc"])
    st["dk"] = M["STRAT-AF"] - M["STRAT-K0 (mean s0-4)"]
    st["dk_ci"] = ci(bt["dk"])
    st["spread"] = float(max(st["ks"][n]) - min(st["ks"][n]))
    st["irt_ratio"] = M["IRT-ANCHOR"] / M["RAND"]
    st["irt_ci"] = ci(bt["irt"])
    st["se_log"] = float(np.std(np.log(bt["rat"]), ddof=1))
    st["mde"] = 2.8 * st["se_log"]
    st["errs"] = errs
    return st


# ── the printed readout ─────────────────────────────────────────────────────────────────────────────────────────────────
def verdict_lines(st):
    c = R()
    n = c["n_dec"]
    L = ["", "== CS1 (DECIDING at n %d; the INTERVAL decides) ==" % n]
    lo, hi = st["ratio_ci"]
    L.append("  MAE(STRAT-AF) %.5f / MAE(RAND) %.5f = ratio %.4f; 95%% interval [%.4f, %.4f] (two-level bootstrap over %d models x %d"
             " draws, clustered by model, B %d, default_rng(%d))" % (st["mae"][n]["STRAT-AF"], st["mae"][n]["RAND"], st["ratio"], lo, hi,
                                                                    st["M"], c["draws"], c["B"], c["boot_seed"]))
    beats = bool(st["ratio"] < 1 and hi < 1)
    if beats:
        hit("CS1.BEATS")
        L.append("CS1: BEATS-RAND: AF-U-cell strata estimate a held-out model's EVAL accuracy from %d items with a smaller error than"
                 " simple random sampling; the whole interval lies below 1" % n)
    else:
        hit("CS1.NOT")
        L.append("CS1: NOT-SHOWN: the interval [%.4f, %.4f] reaches 1 (FAILS for BEATS-RAND, rule 8)" % (lo, hi))
    L.append("")
    L.append("== CS2 (deciding at n %d; INTERVAL AND spread_K; like with like, [SC] strata) ==" % n)
    L.append("  spread_K (max - min of the five STRAT-K_s MAEs) %.5f; MAE(K_s) %s" % (st["spread"], " / ".join("%.5f" % x for x in st["ks"][n])))
    words = {}
    for lab, D_, (l2, h2) in (("STRAT-SRC", st["dsrc"], st["dsrc_ci"]), ("STRAT-K0", st["dk"], st["dk_ci"])):
        w = cs2_word(D_, h2, st["spread"])
        words[lab] = w
        L.append("  versus %-9s D = MAE(STRAT-AF) - MAE(%s) = %+.5f; 95%% interval [%+.5f, %+.5f]" % (lab, lab, D_, l2, h2))
        if w == "AF-BETTER":
            hit("CS2.AF_BETTER")
            L.append("CS2 versus %s: AF-BETTER: the interval lies below 0 and |D| %.5f exceeds spread_K %.5f" % (lab, abs(D_), st["spread"]))
        elif w == "AF-NOT-BETTER":
            hit("CS2.NOT_BETTER")
            L.append("CS2 versus %s: AF-NOT-BETTER: D %+.5f >= 0 at the point" % (lab, D_))
        else:
            hit("CS2.UNDET")
            L.append("CS2 versus %s: UNDETERMINED: D %+.5f < 0 but the interval or spread_K %.5f does not separate" % (lab, D_, st["spread"]))
    L.append("")
    if words["STRAT-SRC"] == "AF-NOT-BETTER":
        hit("FCS.FIRED")
        L.append("F-CS: FIRED (CS2 versus STRAT-SRC AF-NOT-BETTER): tree cells add nothing to sampling efficiency beyond source strata;"
                 " an SQ4 'the tree cuts evaluation cost' sentence is off the table")
    else:
        hit("FCS.NOT_FIRED")
        L.append("F-CS: NOT FIRED (CS2 versus STRAT-SRC %s)" % words["STRAT-SRC"])
    L.append("")
    L.append("== DESCRIPTIVE: MAE by arm and n (IRT-ANCHOR is [TS], a ceiling, never ranked) ==")
    L.append("  %-22s %s" % ("arm", "  ".join("n %-9d" % m for m in c["ns"])))
    for arm in SHOWN:
        L.append("  %-22s %s" % (arm, "  ".join("%.5f    " % st["mae"][m][arm] for m in c["ns"])))
    L.append("  ratio to RAND          %s" % "  ".join("%.4f     " % (st["mae"][m]["STRAT-AF"] / st["mae"][m]["RAND"]) for m in c["ns"]))
    L.append("  IRT-ANCHOR / RAND at n %d: %.4f [%.4f, %.4f] ([TS] ceiling)" % (n, st["irt_ratio"], st["irt_ci"][0], st["irt_ci"][1]))
    L.append("")
    L.append("== PREDICTIONS (registrar's priors; bands closed) ==")
    L.append("  P1 MAE ratio STRAT-AF / RAND 0.85 [0.70, 0.97]: %.4f -> %s" % (st["ratio"], RSC.hw(st["ratio"], PRED["P1"])))
    L.append("  P1 CS1 BEATS-RAND 0.75: outcome %s -> Brier %.4f" % ("BEATS-RAND" if beats else "NOT-SHOWN", RSC.brier(PRED["P1_prob"], beats)))
    w = words["STRAT-SRC"]
    b3 = sum((p - (1.0 if k == w else 0.0)) ** 2 for k, p in PRED["P2"].items())
    L.append("  P2 CS2 versus STRAT-SRC: AF-BETTER 0.15, UNDETERMINED 0.55, AF-NOT-BETTER 0.30: outcome %s -> Brier (3 outcomes) %.4f" % (w, b3))
    L.append("  P3 IRT-ANCHOR MAE ratio vs RAND 0.70 [0.50, 0.90] (ceiling, descriptive): %.4f -> %s" % (st["irt_ratio"], RSC.hw(st["irt_ratio"], PRED["P3"])))
    L.append("")
    L.append("== SUPPORT (registered planning numbers; MEASURED beside) ==")
    L.append("  (a) %d held-out models x %d draws at n %d; EVAL %d items / %d components; CLUSTERED BY MODEL: %d clusters" % (
        st["M"], c["draws"], n, st["N"], st["G"], st["M"]))
    L.append("  (b) DEFF not transported; (c) n_eff about %d models (registered about 18)" % st["M"])
    L.append("  (d) SE of the log MAE ratio MEASURED %.4f (planning 0.10 / sqrt(18) = 0.024); (e) MDE80 = 2.8 x SE %.4f (registered 0.066)" % (
        st["se_log"], st["mde"]))
    L.append("  (f) VERDICT LINE (registered): CS1 SCOREABLE (prediction ratio 0.85, log -0.16, beyond the MDE); CS2 versus STRAT-SRC"
             " DESCRIPTIVE-ONLY (prediction ratio 0.97, log -0.03). (g) STRUCTURAL: reachable.")
    L.append("  NOT APPLICABLE: wrong(established) and the tie conventions A / B (keyed correctness); the two-stage bootstrap (CS-R9).")
    L.append("  WHAT THIS RESULT WILL NOT SHOW (registered): a price for judged evaluation; other rosters; a ranking against the [TS] ceiling.")
    return L


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def out_paths(root, out_dir):
    d = out_dir or U.P(root, R()["out_dir"])
    return os.path.join(d, R()["outcome"]), os.path.join(d, R()["marker"])


def planned(say):
    c = R()
    say("%s PLANNED: held-out models x n %s (n %d deciding) x %d draws per arm (default_rng(%d + index), CS-R2); arms %s; bootstrap B %d"
        " (default_rng(%d)); Neyman S_h floor %.2f" % (TAG, "/".join(str(x) for x in c["ns"]), c["n_dec"], c["draws"], c["seed"],
                                                      ", ".join(a for a, _i in ARM_IDX) + ", STRAT-AF+IRT", c["B"], c["boot_seed"], c["s_floor"]))


def dry_run(root, out_dir=None, out=print):
    outp, mark = out_paths(root, out_dir)
    pol, af, kx = RSC.prelude(root, out, TAG, TEST_ID, REG_TXT, [os.path.abspath(__file__)], [outp, mark], True)
    RSC.dry_structure(root, out, TAG, pol, af, kx)
    planned(out)
    out("%s DRY-RUN complete: no key column selected (both tripwires sealed); no statistic; nothing written" % TAG)
    hit("DRY.DONE")


def write_outcome(path, text):
    return U.G.write_once(path, text)


def run(root, out_dir=None, out=print):
    lines = []

    def say(s):
        lines.append(s)
        out(s)
    outp, mark = out_paths(root, out_dir)
    pol, af, kx = RSC.prelude(root, say, TAG, TEST_ID, REG_TXT, [os.path.abspath(__file__)], [outp, mark], False)
    planned(say)
    D = RSC.load_all(root, say, TAG, pol, af, kx, mark, "%s: the EVAL key read started (B1); policy sha256 %s" % (TAG, U.C()["policy_sha"]))
    RSC.b3_identity(D, pol, say, TAG)
    arms = RSC.arms_of(D)
    st = analyze(D, arms, say)
    for ln in verdict_lines(st):
        say(ln)
    text = "\n".join(lines) + "\n"
    write_outcome(outp, text)
    out("%s OUTCOME written write-once: %s" % (TAG, outp))
    hit("RUN.DONE")
    return st, text


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
FX_RP = dict(RP_, ns=(10, 20), n_dec=20, draws=24, B=150)


class _swap:
    def __init__(self, d):
        self.d = d

    def __enter__(self):
        self.old = _RP[0]
        _RP[0] = self.d

    def __exit__(self, *a):
        _RP[0] = self.old


def _o_blocks(cells, srcs, H):
    out = []
    for h in range(H):
        cnt = Counter(s_ for c_, s_ in zip(cells, srcs) if c_ == h)
        top = max(cnt.values())
        out.append(sorted(set(srcs)).index(min(k for k, v in cnt.items() if v == top)))
    return out


def _o_draws(seed, cells, e, y, ndraw, blocks):
    """Oracle sampler by loops on the same stream: the within-block permutations, then u, then N keys per draw."""
    rng = np.random.default_rng(seed)
    N = len(cells)
    H = len(e)
    Nh = [sum(1 for x in cells if x == h) for h in range(H)]
    out, sels = [], []
    for _d in range(ndraw):
        order = []
        for b in sorted(set(blocks)):
            mem = [h for h in range(H) if blocks[h] == b]
            order += [mem[q] for q in rng.permutation(len(mem))]
        u = rng.random()
        fl = [math.floor(e[h] + 1e-12) for h in order]
        fr = [max(e[h] - f, 0.0) for h, f in zip(order, fl)]
        Rr = int(round(sum(fr)))
        alloc = [0] * H
        for h, f in zip(order, fl):
            alloc[h] = f
        cum, acc_ = [], 0.0
        for x in fr:
            acc_ += x
            cum.append(acc_)
        for k in range(Rr):
            t = u + k
            j = next((j for j, cc in enumerate(cum) if t <= cc), H - 1)
            alloc[order[j]] += 1
        keys = rng.random(N)
        chosen = []
        for h in range(H):
            mem = sorted([i for i in range(N) if cells[i] == h], key=lambda i: (keys[i], i))
            chosen += mem[:alloc[h]]
        out.append(sum(y[i] / (e[cells[i]] / Nh[cells[i]]) for i in chosen) / N)
        sels.append(sorted(chosen))
    return out, sels


def _oracle(X):
    """INDEPENDENT: the fixture rows, own LOO IRT, the sampler by loops, the KMeans anchors by loops, the bootstrap by loops."""
    tr, ev, YT, YE = RSC.fx_matrices(X["rows"])
    c = FX_RP
    N = len(ev)
    srcs = [r["src"] for r in ev]
    cT, cE = RSC.floors_of([r["src"] for r in tr]), RSC.floors_of(srcs)

    def remap(keys):
        u = sorted(set(keys))
        return [u.index(k) for k in keys], len(u)
    cellsets = {"AF-U": remap([r["af"] for r in ev]), "SRC": remap(srcs)}
    for s in RSC.KSEEDS:
        cellsets["K%d" % s] = remap([X["kcells"][s][r["id"]] for r in ev])
    errs = []
    for mi, m in enumerate(RSC.FX_MODELS):
        keep = [j for j in range(6) if j != mi]
        ft = RSC.fit_train(YT[:, keep], cT)
        aE, bE, _i, _m = RSC.fit_items(YE[:, keep], cE, ft["theta"])
        a = np.exp(aE)
        Pk = RSC.prob(ft["theta"], aE, bE, cE)
        b2 = float(((Pk.mean(axis=0) - YE[:, keep].mean(axis=0)) ** 2).mean())
        y = YE[:, mi]
        acc = float(y.mean())
        res_n = {}
        for ni, n in enumerate(c["ns"]):
            base = c["seed"] + (mi * len(c["ns"]) + ni) * N_ARM_IDX
            res = {}
            est, _s = _o_draws(base + 0, [0] * N, [float(n)], y, c["draws"], [0])
            res["RAND"] = [abs(x - acc) for x in est]
            cl, H = cellsets["AF-U"]
            Nh = [cl.count(h) for h in range(H)]
            est, sels = _o_draws(base + 1, cl, [n * x / N for x in Nh], y, c["draws"], _o_blocks(cl, srcs, H))
            res["STRAT-AF"] = [abs(x - acc) for x in est]
            for s in RSC.KSEEDS:
                cs, Hs = cellsets["K%d" % s]
                est, _s = _o_draws(base + 2 + s, cs, [n * cs.count(h) / N for h in range(Hs)], y, c["draws"], _o_blocks(cs, srcs, Hs))
                res["STRAT-K%d" % s] = [abs(x - acc) for x in est]
            cs, Hs = cellsets["SRC"]
            est, _s = _o_draws(base + 7, cs, [n * cs.count(h) / N for h in range(Hs)], y, c["draws"], _o_blocks(cs, srcs, Hs))
            res["STRAT-SRC"] = [abs(x - acc) for x in est]
            rg = np.random.default_rng(base + 8)
            Xe = np.column_stack([a, bE])
            e8 = []
            from sklearn.cluster import KMeans
            for _d in range(c["draws"]):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    km = KMeans(n_clusters=n, n_init=1, random_state=int(rg.integers(0, 2 ** 31 - 1))).fit(Xe)
                tot = 0.0
                for k in range(n):
                    mem = [i for i in range(N) if km.labels_[i] == k]
                    if mem:
                        best = min(mem, key=lambda i: (((Xe[i] - km.cluster_centers_[k]) ** 2).sum(), i))
                        tot += len(mem) / N * y[best]
                e8.append(tot)
            res["IRT-ANCHOR"] = [abs(x - acc) for x in e8]
            # NEYMAN: S_h from the other models by loops, floored; neyman_alloc (sampling case) for the capped allocation
            Sh = []
            for h in range(H):
                mem = [i for i in range(N) if cl[i] == h]
                v_ = [np.mean([YE[i, j] for i in mem]) for j in keep]
                Sh.append(max(math.sqrt(float(np.mean([p_ * (1 - p_) for p_ in v_]))), c["s_floor"]))
            eN = neyman_alloc(np.array(Nh, dtype=float), np.array(Sh), n)
            est, _s = _o_draws(base + 9, cl, list(eN), y, c["draws"], _o_blocks(cl, srcs, H))
            res["NEYMAN"] = [abs(x - acc) for x in est]
            e6 = []
            for ch in sels:
                ps = sum(y[i] for i in ch) / n
                t = theta_map(y[ch], a[ch], bE[ch], cE[ch])
                P = np.clip(cE + (1 - cE) / (1 + np.exp(-a * (t - bE))), RSC.EPS, 1 - RSC.EPS)
                pirt = (sum(y[i] for i in ch) + sum(P[i] for i in range(N) if i not in set(ch))) / N
                v = ps * (1 - ps) / n
                lam = b2 / (b2 + v)
                e6.append(abs(lam * ps + (1 - lam) * pirt - acc))
            res["STRAT-AF+IRT"] = e6
            res_n[n] = res
        errs.append(res_n)
    n = c["n_dec"]
    mae = {arm: float(np.mean([np.mean(errs[m][n][arm]) for m in range(6)])) for arm in ("RAND", "STRAT-AF", "STRAT-SRC", "IRT-ANCHOR", "STRAT-AF+IRT", "NEYMAN")}
    ks = [float(np.mean([np.mean(errs[m][n]["STRAT-K%d" % s]) for m in range(6)])) for s in RSC.KSEEDS]
    rng = np.random.default_rng(c["boot_seed"])
    rat, dsrc, dk = [], [], []
    for _b in range(c["B"]):
        mi = rng.integers(0, 6, 6)
        ji = rng.integers(0, c["draws"], (6, c["draws"]))

        def m_(arm):
            return float(np.mean([errs[mi[r]][n][arm][ji[r, q]] for r in range(6) for q in range(c["draws"])]))
        af = m_("STRAT-AF")
        rat.append(af / m_("RAND"))
        dsrc.append(af - m_("STRAT-SRC"))
        dk.append(af - float(np.mean([m_("STRAT-K%d" % s) for s in RSC.KSEEDS])))
    return errs, mae, ks, rat, dsrc, dk


def st_constants():
    assert RP_["ns"] == (50, 100, 200, 400) and RP_["n_dec"] == 100 and RP_["draws"] == 500 and RP_["seed"] == 20261004
    assert RP_["B"] == 2000 and RP_["boot_seed"] == 20261004 and dict(ARM_IDX)["IRT-ANCHOR"] == 8 and N_ARM_IDX == 10
    assert [i for _a, i in ARM_IDX] == list(range(10)) and RSC.LAMBDA == 1.0
    assert PRED["P1"] == (0.70, 0.97) and PRED["P1_prob"] == 0.75 and PRED["P3"] == (0.50, 0.90)
    assert PRED["P2"] == {"AF-BETTER": 0.15, "UNDETERMINED": 0.55, "AF-NOT-BETTER": 0.30}


def st_sampling():
    rng = np.random.default_rng(5)
    g = np.array([0] * 7 + [1] * 13 + [2] * 30 + [3] * 50)
    y = (np.arange(100) % 3 == 0).astype(float)
    e = prop_alloc(np.bincount(g).astype(float), 10)          # 0.7, 1.3, 3.0, 5.0
    cnt = np.zeros(4)
    ests = []
    for _ in range(4000):
        al = systematic(e, rng.random())
        assert al.sum() == 10 and all(np.floor(e[h] + 1e-12) <= al[h] <= np.floor(e[h] + 1e-12) + 1 for h in range(4)), (al, e)
        cnt += al
    assert np.allclose(cnt / 4000, e, atol=0.03), cnt / 4000
    b0 = np.zeros(4, dtype=np.int64)
    est, sels = strat_draws(np.random.default_rng(1), g, e, y, 3000, b0, keep=True)
    for ch in sels[:50]:
        assert len(ch) == 10 and len(set(ch.tolist())) == 10
    assert abs(est[0] - y[sels[0]].mean()) < 1e-12, "HT = the sample mean under proportional allocation"
    assert abs(est.mean() - y.mean()) < 0.01, (est.mean(), y.mean())
    # a non-proportional allocation stays unbiased through pi = e_h / N_h
    e2 = np.array([2.0, 2.0, 3.0, 3.0])
    est2, _s = strat_draws(np.random.default_rng(2), g, e2, y, 6000, b0)
    assert abs(est2.mean() - y.mean()) < 0.01, est2.mean()
    # a cell with e_h < 1 carries weight N_h / e_h: unbiased for a population concentrated in that cell (0.7 expected of 7 items)
    est4, _s = strat_draws(np.random.default_rng(4), g, e, (g == 0).astype(float), 6000, b0)
    assert abs(est4.mean() - 0.07) < 0.005, est4.mean()
    # one stratum = simple random sampling of exactly n
    est3, s3 = strat_draws(np.random.default_rng(3), np.zeros(100, dtype=np.int64), np.array([10.0]), y, 5, np.zeros(1, dtype=np.int64), keep=True)
    assert all(len(ch) == 10 for ch in s3) and abs(est3[1] - y[s3[1]].mean()) < 1e-12
    # Neyman capping and re-allocation
    e4 = neyman_alloc(np.array([2.0, 50.0, 48.0]), np.array([10.0, 0.1, 0.1]), 20)
    assert abs(e4[0] - 2.0) < 1e-12 and abs(e4.sum() - 20) < 1e-9 and abs(e4[1] / e4[2] - 50 / 48) < 1e-9, e4
    # KMeans anchors: three tight groups -> one anchor each, weights = group shares
    X = np.array([[0.0, 0.0], [0.0, 0.1], [5.0, 5.0], [5.1, 5.0], [5.0, 5.1], [10.0, 0.0]])
    anc, w = kmeans_anchor(X, 3, 0)
    assert sorted(np.round(w * 6).astype(int).tolist()) == [1, 2, 3] and abs(w.sum() - 1) < 1e-12
    assert set(anc.tolist()) <= set(range(6)) and 5 in anc.tolist()
    # theta_map: more right answers -> higher theta; the prior keeps an all-right sample finite
    a, b, c0 = np.ones(10), np.zeros(10), np.zeros(10)
    t1, t2 = theta_map(np.array([1.0] * 3 + [0.0] * 7), a, b, c0), theta_map(np.array([1.0] * 7 + [0.0] * 3), a, b, c0)
    assert t1 < 0 < t2 and abs(t1 + t2) < 1e-9 and np.isfinite(theta_map(np.ones(10), a, b, c0))


def st_e2e(tmp):
    root, X = RSC.build_fixture(tmp)
    od = os.path.join(tmp, "out")
    errs, mae, ks, rat, dsrc, dk = _oracle(X)
    with _swap(FX_RP), RSC.patched(X):
        (st, text), printed = RSC.capture(run, root, od)
        outp, mk = out_paths(root, od)
        assert open(outp, encoding="utf-8").read() == text and os.path.isfile(mk)
        assert printed.split("\n")[0].startswith(TAG + " POOL pv_fx")
        n = FX_RP["n_dec"]
        for mi in range(6):
            for nn in FX_RP["ns"]:
                for arm in errs[mi][nn]:
                    assert np.allclose(st["errs"][mi][nn][arm], errs[mi][nn][arm], atol=1e-10, rtol=0), (mi, nn, arm)
        for arm in ("RAND", "STRAT-AF", "STRAT-SRC", "IRT-ANCHOR", "STRAT-AF+IRT", "NEYMAN"):
            assert ("%.5f" % mae[arm]) in RSC.line_with(text, "  %-22s " % arm), arm
        RSC.need(RSC.line_with(text, "  %-22s " % "STRAT-K0 (mean s0-4)"), "%.5f" % float(np.mean(ks)))
        ratio = mae["STRAT-AF"] / mae["RAND"]
        lo, hi = sorted(rat)[int(0.025 * len(rat))], sorted(rat)[int(0.975 * len(rat)) - 1]
        RSC.need(text, "= ratio %.4f; 95%% interval [%.4f, %.4f]" % (ratio, lo, hi))
        w1 = "BEATS-RAND" if (ratio < 1 and hi < 1) else "NOT-SHOWN"
        RSC.need(text, "CS1: %s" % w1, "P1 CS1 BEATS-RAND 0.75: outcome %s -> Brier %.4f" % (w1, (0.75 - (w1 == "BEATS-RAND")) ** 2),
                 "P1 MAE ratio STRAT-AF / RAND 0.85 [0.70, 0.97]: %.4f -> %s" % (ratio, "HELD" if 0.70 <= ratio <= 0.97 else "FAILED"))
        spread = max(ks) - min(ks)
        RSC.need(text, "spread_K (max - min of the five STRAT-K_s MAEs) %.5f" % spread)
        words = {}
        for lab, Dv, reps in (("STRAT-SRC", mae["STRAT-AF"] - mae["STRAT-SRC"], dsrc), ("STRAT-K0", mae["STRAT-AF"] - float(np.mean(ks)), dk)):
            l2, h2 = sorted(reps)[int(0.025 * len(reps))], sorted(reps)[int(0.975 * len(reps)) - 1]
            RSC.need(text, "versus %-9s D = MAE(STRAT-AF) - MAE(%s) = %+.5f; 95%% interval [%+.5f, %+.5f]" % (lab, lab, Dv, l2, h2))
            w = "AF-BETTER" if (h2 < 0 and abs(Dv) > spread) else ("AF-NOT-BETTER" if Dv >= 0 else "UNDETERMINED")
            words[lab] = w
            RSC.need(text, "CS2 versus %s: %s" % (lab, w))
        RSC.need(text, "F-CS: FIRED" if words["STRAT-SRC"] == "AF-NOT-BETTER" else "F-CS: NOT FIRED (CS2 versus STRAT-SRC %s)" % words["STRAT-SRC"])
        b3 = sum((p - (1.0 if k == words["STRAT-SRC"] else 0.0)) ** 2 for k, p in PRED["P2"].items())
        RSC.need(text, "outcome %s -> Brier (3 outcomes) %.4f" % (words["STRAT-SRC"], b3))
        RSC.need(text, "IRT-ANCHOR / RAND at n %d: %.4f" % (n, mae["IRT-ANCHOR"] / mae["RAND"]))
        se = float(np.std(np.log(rat), ddof=1))
        RSC.need(text, "SE of the log MAE ratio MEASURED %.4f" % se, "MDE80 = 2.8 x SE %.4f" % (2.8 * se))
        try:
            RSC.capture(run, root, od)
            raise AssertionError("second run not refused")
        except SystemExit as e:
            assert "write-once" in str(e), e
        assert open(outp, encoding="utf-8").read() == text


def _syn(ratio=0.85, lo=0.80, hi=0.95, dsrc=-0.002, dsrc_ci=(-0.004, -0.001), dk=-0.001, dk_ci=(-0.003, 0.001), spread=0.001, irt=0.7):
    mae = {n: {a: 0.04 for a in SHOWN} for n in RP_["ns"]}
    return dict(N=5907, G=5404, M=18, models=[], accs=[], mae=mae, ks={n: [0.04] * 5 for n in RP_["ns"]}, ratio=ratio, ratio_ci=(lo, hi),
                dsrc=dsrc, dsrc_ci=dsrc_ci, dk=dk, dk_ci=dk_ci, spread=spread, irt_ratio=irt, irt_ci=(0.6, 0.8), se_log=0.03, mde=0.084)


def st_branches():
    J = lambda st: "\n".join(verdict_lines(st))           # noqa: E731
    RSC.need(J(_syn()), "CS1: BEATS-RAND", "P1 CS1 BEATS-RAND 0.75: outcome BEATS-RAND -> Brier 0.0625", "0.8500 -> HELD")
    RSC.need(J(_syn(hi=1.0)), "CS1: NOT-SHOWN", "Brier 0.5625")                 # an interval reaching 1
    RSC.need(J(_syn(ratio=1.0, hi=0.99)), "CS1: NOT-SHOWN")
    RSC.need(J(_syn(dsrc=-0.002, dsrc_ci=(-0.004, -0.001), spread=0.001)), "CS2 versus STRAT-SRC: AF-BETTER", "F-CS: NOT FIRED (CS2 versus STRAT-SRC AF-BETTER)",
             "outcome AF-BETTER -> Brier (3 outcomes) %.4f" % (0.85 ** 2 + 0.55 ** 2 + 0.30 ** 2))
    RSC.need(J(_syn(dsrc=-0.002, dsrc_ci=(-0.004, 0.0), spread=0.001)), "CS2 versus STRAT-SRC: UNDETERMINED")       # upper end 0 not below
    RSC.need(J(_syn(dsrc=-0.001, dsrc_ci=(-0.004, -0.0005), spread=0.001)), "CS2 versus STRAT-SRC: UNDETERMINED")   # |D| = spread
    RSC.need(J(_syn(dsrc=0.0, dsrc_ci=(-0.001, 0.001))), "CS2 versus STRAT-SRC: AF-NOT-BETTER", "F-CS: FIRED (CS2 versus STRAT-SRC AF-NOT-BETTER)",
             "outcome AF-NOT-BETTER -> Brier (3 outcomes) %.4f" % (0.15 ** 2 + 0.55 ** 2 + 0.70 ** 2))
    RSC.need(J(_syn(dk=0.001, dk_ci=(0.0, 0.002))), "CS2 versus STRAT-K0: AF-NOT-BETTER", "F-CS: NOT FIRED")
    RSC.need(J(_syn(dk=-0.003, dk_ci=(-0.004, -0.002), spread=0.001)), "CS2 versus STRAT-K0: AF-BETTER")
    RSC.need(J(_syn(dsrc=-0.0005, dsrc_ci=(-0.002, 0.001))), "outcome UNDETERMINED -> Brier (3 outcomes) %.4f" % (0.15 ** 2 + 0.45 ** 2 + 0.30 ** 2))
    RSC.need(J(_syn(ratio=0.70)), "0.7000 -> HELD")
    RSC.need(J(_syn(ratio=0.97, hi=0.98)), "0.9700 -> HELD")
    RSC.need(J(_syn(ratio=0.6999)), "0.6999 -> FAILED")
    RSC.need(J(_syn(irt=0.9)), "(ceiling, descriptive): 0.9000 -> HELD")
    RSC.need(J(_syn(irt=0.9001)), "(ceiling, descriptive): 0.9001 -> FAILED")
    assert cs2_word(np.float64(-0.002), np.float64(-0.001), np.float64(0.001)) == "AF-BETTER"


def st_refusals(tmp):
    def expect(needle, pool=(0, "stub"), pre=None, existed=False, kmut=None):
        sub = os.path.join(tmp, "r%d" % len(os.listdir(tmp)))
        os.makedirs(sub)
        root, X = RSC.build_fixture(sub)
        if kmut:
            X["kconst"] = dict(X["kconst"], **kmut)
        od = os.path.join(root, "out")
        if pre:
            pre(root, od, X)
        buf = []
        with _swap(dict(FX_RP, draws=2, B=4, ns=(10,), n_dec=10)), RSC.patched(X, pool):
            try:
                run(root, od, out=buf.append)
                raise AssertionError("not refused: %s" % needle)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e)[:300])
        op = os.path.join(od, R()["outcome"])
        if existed:
            assert open(op, encoding="utf-8").read() == "kept"
        else:
            assert not os.path.exists(op)
        return buf
    expect("[IDENTITY] C1", kmut=dict(c1="+9.99pp"))
    expect("[IDENTITY] C1", kmut=dict(af="0.0001"))
    buf = expect("B0-2 pool check failed", pool=(1, "stub failure"))
    assert buf[0].startswith(TAG + " POOL")

    def mk(name, txt):
        def f(root, od, X):
            os.makedirs(od, exist_ok=True)
            with open(os.path.join(od, name), "w", encoding="utf-8") as fh:
                fh.write(txt)
        return f
    expect("write-once output(s) exist", pre=mk(RP_["marker"], ""))
    expect("write-once output(s) exist", pre=mk(RP_["outcome"], "kept"), existed=True)

    def b3(root, od, X):
        pp_ = U.P(root, U.CONST["policy_rel"])
        pol = json.load(open(pp_, encoding="utf-8"))
        pol["best_single"] = "m0"
        with open(pp_, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
        X["const"]["policy_sha"] = RSC.sha256_bytes(pp_)
    expect("[B3] the point policy", pre=b3)
    wp = os.path.join(tmp, "existing.txt")
    with open(wp, "w", encoding="utf-8") as fh:
        fh.write("kept")
    try:
        write_outcome(wp, "new")
        raise AssertionError("write_outcome overwrote")
    except SystemExit as e:
        assert "write-once" in str(e)
    assert open(wp, encoding="utf-8").read() == "kept"


def st_dry(tmp):
    root, X = RSC.build_fixture(tmp)
    od = os.path.join(tmp, "out")

    def files():
        return sorted(os.path.join(a, f_) for a, _d, fs in os.walk(tmp) for f_ in fs)
    before = files()
    with _swap(FX_RP), RSC.patched(X):
        _r, text = RSC.capture(dry_run, root, od)
    assert files() == before and text.split("\n")[0].startswith(TAG + " POOL pv_fx")
    assert "TRAIN key:" not in text and "key cells single" not in text
    RSC.need(text, "TRAIN SET (gen view", "EVAL SET (G14's", "DENOMINATOR AF-U  12 distinct cells", "PLANNED: held-out models x n 10/20 (n 20 deciding)",
             "DRY-RUN complete", "PIN tools/analysis/cell_strata_eval.py blob:")
    assert "CS1:" not in text and "MAE" not in text


def st_order():
    """D-CS1: the cell index order no longer changes the estimate's distribution; source blocks stay whole."""
    # one source, 20 cells of 5 items, e_h = 0.5 at n 10; y = 1 on 10 of the cells
    g = np.repeat(np.arange(20), 5)
    e = prop_alloc(np.bincount(g).astype(float), 10)
    b = np.zeros(20, dtype=np.int64)
    asc = (g >= 10).astype(float)                    # the high cells contiguous in index order
    inter = (g % 2 == 1).astype(float)               # the high cells alternating in index order
    va = strat_draws(np.random.default_rng(11), g, e, asc, 4000, b)[0]
    vi = strat_draws(np.random.default_rng(12), g, e, inter, 4000, b)[0]
    assert abs(va.mean() - 0.5) < 0.01 and abs(vi.mean() - 0.5) < 0.01
    assert va.var() > 0.01 and vi.var() > 0.01, (va.var(), vi.var())      # index order would give 0 and 0.25
    assert abs(va.var() - vi.var()) < 0.15 * max(va.var(), vi.var()), (va.var(), vi.var())
    # two sources of 4 cells each (e_h 0.5, n 4): the blocks stay in sorted order, so every draw takes 2 cells of each
    g2 = np.repeat(np.arange(8), 5)
    b2 = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    _e, sels = strat_draws(np.random.default_rng(13), g2, prop_alloc(np.bincount(g2).astype(float), 4), np.zeros(40), 300, b2, keep=True)
    assert all(int((g2[ch] < 4).sum()) == 2 for ch in sels), "source blocks kept whole"
    # the block of a cell: modal source, ties to the sorted-first
    assert cell_blocks(np.array([0, 0, 0, 1, 1, 2]), ["A", "B", "B", "A", "B", "C"], 3).tolist() == [1, 0, 2]
    # stream discipline: the permutation first, then u, then the keys
    r1, r2 = np.random.default_rng(7), np.random.default_rng(7)
    _x, s1 = strat_draws(r1, g, e, asc, 1, b, keep=True)
    perm = r2.permutation(20)
    al = np.empty(20, dtype=np.int64)
    al[perm] = systematic(e[perm], r2.random())
    keys = r2.random(100)
    want = sorted(i for h in range(20) for i in sorted(np.flatnonzero(g == h), key=lambda i: keys[i])[:al[h]])
    assert sorted(s1[0].tolist()) == want


CASES = (("irt", RSC.irt_selfcheck, "plain"), ("constants", st_constants, "plain"), ("sampling", st_sampling, "plain"),
         ("order", st_order, "plain"),
         ("branches", st_branches, "plain"), ("e2e", st_e2e, "tmp"), ("refusals", st_refusals, "tmp"), ("dry_run", st_dry, "tmp"))


def selftest(only=None, quiet=False):
    return RSC.run_cases(TAG, CASES, HIT, BRANCHES, only, quiet)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=U.ROOT)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(set(a.only) if a.only else None)
        return 0
    if a.mutants:
        return RSC.run_mutants(os.path.abspath(__file__), "cell_strata_eval", MUTANTS, TAG, a.only)
    if a.dry_run:
        dry_run(os.path.abspath(a.data_root), a.out_dir)
        return 0
    run(os.path.abspath(a.data_root), a.out_dir)
    return 0


MUTANTS = (
    ("C00 control (no-op edit)", "    return n * Nh / Nh.sum()", "    return n * Nh / Nh.sum()", ["sampling"], "self"),
    ("Z01 STRAT-AF sampled without strata (= RAND)", '        est, sels = strat_draws(rng_of(1), gA, prop_alloc(NhA, n), y, c["draws"], bl["AF-U"], keep=True)',
     '        est, sels = strat_draws(rng_of(1), np.zeros(N, dtype=np.int64), np.array([float(n)]), y, c["draws"], np.zeros(1, dtype=np.int64), keep=True)', ["e2e"], "self"),
    # D-CS1 (the within-source cell shuffle)
    ("Z40 no cell shuffle (index order, the pre-D-CS1 design)", "        out.append(mem[rng.permutation(len(mem))])", "        rng.permutation(len(mem))\n        out.append(mem)",
     ["order", "e2e"], "self"),
    ("Z41 one global shuffle across sources (blocks not kept whole)", "    out = []\n    for b in np.unique(block):\n        mem = np.flatnonzero(block == b)\n        out.append(mem[rng.permutation(len(mem))])\n    return np.concatenate(out)",
     "    return rng.permutation(len(block))", ["order"], "self"),
    ("Z42 shuffle only for STRAT-AF (K_s in index order)", '            est, _s = strat_draws(rng_of(2 + s), g, prop_alloc(np.bincount(g, minlength=H).astype(np.float64), n), y, c["draws"], bl["K%d" % s])',
     '            est, _s = strat_draws(rng_of(2 + s), g, prop_alloc(np.bincount(g, minlength=H).astype(np.float64), n), y, c["draws"], np.arange(H))',
     ["e2e"], "self"),
    ("Z43 stream order: u before the permutation", "        perm = cell_order(rng, block)\n        alloc = np.empty(H, dtype=np.int64)\n        alloc[perm] = systematic(e[perm], rng.random())",
     "        u_ = rng.random()\n        perm = cell_order(rng, block)\n        alloc = np.empty(H, dtype=np.int64)\n        alloc[perm] = systematic(e[perm], u_)", ["order", "e2e"], "self"),
    ("Z44 block = the first item's source (not the modal one)", "    return cnt.argmax(axis=1).astype(np.int64)",
     "    first = {}\n    for h_, s_ in zip(gE.tolist(), srcE):\n        first.setdefault(h_, pos[s_])\n    return np.array([first[h_] for h_ in range(H)], dtype=np.int64)", ["order"], "self"),
    ("Z45 allocation not mapped back through the permutation", "        alloc[perm] = systematic(e[perm], rng.random())", "        alloc[:] = systematic(e[perm], rng.random())",
     ["order", "e2e"], "self"),
    ("Z02 HT weights from floor(e_h) (not E n_h)", "    pi = (e / np.where(Nh > 0, Nh, 1.0))[gE]", "    pi = (np.maximum(np.floor(e), 1.0) / np.where(Nh > 0, Nh, 1.0))[gE]",
     ["sampling"], "self"),
    ("Z03 no systematic rounding (floor only; total < n)", "    if Rr > 0:", "    if False:", ["sampling"], "self"),
    ("Z04 deterministic largest-remainder rounding", '        h = np.minimum(np.searchsorted(C, pts, side="left"), len(e) - 1)', "        h = np.argsort(-f, kind='stable')[:Rr]",
     ["sampling"], "self"),
    ("Z05 seed index without the held-out model", '            return np.random.default_rng(c["seed"] + (mi * len(c["ns"]) + ni) * N_ARM_IDX + ai)',
     '            return np.random.default_rng(c["seed"] + ni * N_ARM_IDX + ai)', ["e2e"], "self"),
    ("Z06 STRAT-K0 MAE from seed 0 only", '    M["STRAT-K0 (mean s0-4)"] = float(np.mean(ks))', '    M["STRAT-K0 (mean s0-4)"] = ks[0]', ["e2e"], "self"),
    ("Z07 spread_K = max", '    st["spread"] = float(max(st["ks"][n]) - min(st["ks"][n]))', '    st["spread"] = float(max(st["ks"][n]))', ["e2e"], "self"),
    ("Z08 CS1 without the interval clause", '    beats = bool(st["ratio"] < 1 and hi < 1)', '    beats = bool(st["ratio"] < 1)', ["branches"], "self"),
    ("Z09 CS1 upper end <= 1", '    beats = bool(st["ratio"] < 1 and hi < 1)', '    beats = bool(st["ratio"] < 1 and hi <= 1)', ["branches"], "self"),
    ("Z10 CS2 AF-BETTER without the spread clause", "    if hi < 0 and abs(D) > spread:", "    if hi < 0:", ["branches"], "self"),
    ("Z11 CS2 AF-BETTER with upper end <= 0", "    if hi < 0 and abs(D) > spread:", "    if hi <= 0 and abs(D) > spread:", ["branches"], "self"),
    ("Z12 AF-NOT-BETTER only for D > 0", "    if D >= 0:\n        return \"AF-NOT-BETTER\"", "    if D > 0:\n        return \"AF-NOT-BETTER\"", ["branches"], "self"),
    ("Z13 F-CS keyed on the K0 comparison", '    if words["STRAT-SRC"] == "AF-NOT-BETTER":', '    if words["STRAT-K0"] == "AF-NOT-BETTER":', ["branches"], "self"),
    ("Z14 bootstrap not clustered by model", "        mi = rng.integers(0, M, M)", "        mi = np.arange(M)", ["e2e"], "self"),
    ("Z15 bootstrap draws not resampled", "        ji = rng.integers(0, Dn, (M, Dn))", "        ji = np.tile(np.arange(Dn), (M, 1))", ["e2e"], "self"),
    ("Z16 interval 5 / 95 (not 2.5 / 97.5)", "    return U.pct(s, 0.025), U.pct(s, 0.975)", "    return U.pct(s, 0.05), U.pct(s, 0.95)", ["e2e"], "self"),
    ("Z17 IRT from all 18 models (the held-out one included)", "    keep = [j for j in range(len(D.models)) if j != mi]", "    keep = list(range(len(D.models)))",
     ["e2e"], "self"),
    ("Z18 LOO theta fitted on EVAL (wrong side)", "    ft = RSC.fit_train(D.A[D.T][:, keep].astype(np.float64), cT)",
     "    ft = RSC.fit_train(D.A[D.E][:, keep].astype(np.float64), cE)", ["e2e"], "self"),
    ("Z19 anchor = the cluster's first member", "        anc.append(int(mem[int(np.argmin(d))]))", "        anc.append(int(mem[0]))", ["sampling", "e2e"], "self"),
    ("Z20 anchor weights uniform", "        w.append(len(mem) / len(X))", "        w.append(1.0 / n)", ["sampling", "e2e"], "self"),
    ("Z21 gp-IRT lambda inverted", '            lam = irt["b2"] / (irt["b2"] + v) if (irt["b2"] + v) > 0 else 1.0',
     '            lam = v / (irt["b2"] + v) if (irt["b2"] + v) > 0 else 1.0', ["e2e"], "self"),
    ("Z22 p_pIRT ignores the observed responses", "            pirt = (y[ch].sum() + P[mask].sum()) / N", "            pirt = P.sum() / N", ["e2e"], "self"),
    ("Z23 Neyman S_h floor dropped", '    Sh = np.maximum(np.sqrt((ph * (1 - ph)).mean(axis=1)), c["s_floor"])', "    Sh = np.sqrt((ph * (1 - ph)).mean(axis=1)) + 1e-9",
     ["e2e"], "self"),
    ("Z24 Neyman allocation uncapped", "        over = free & (e_try > Nh)", "        over = free & (e_try > Nh + 1e9)", ["sampling"], "self"),
    ("Z25 Neyman S_h from all models (m included)", '    others = YE[:, irt["keep"]]', "    others = YE", ["e2e"], "self"),
    ("Z26 P1 Brier against 1 - p", 'RSC.brier(PRED["P1_prob"], beats)', 'RSC.brier(1 - PRED["P1_prob"], beats)', ["branches"], "self"),
    ("Z27 P2 Brier on the observed outcome only", '    b3 = sum((p - (1.0 if k == w else 0.0)) ** 2 for k, p in PRED["P2"].items())', '    b3 = (1 - PRED["P2"][w]) ** 2',
     ["branches"], "self"),
    ("Z28 bands open at the ends", "    return bool(band[0] <= x <= band[1])", "    return bool(band[0] < x < band[1])", ["branches"], "common"),
    ("Z29 outcome opened 'w'", "def write_outcome(path, text):\n    return U.G.write_once(path, text)",
     "def write_outcome(path, text):\n    open(path, 'w', encoding='utf-8').write(text)\n    return path", ["refusals"], "self"),
    ("Z30 identity (point) check off", '    if any(got[x] != k[x] for x in ("c1", "gaf", "best", "tdom", "af")):', "    if False:", ["refusals"], "common"),
    ("Z31 B3 check off", '        refuse(tag, "[B3] the point policy', '        (lambda *a: None)(tag, "[B3] the point policy', ["refusals"], "common"),
    ("Z32 dry-run reads the EVAL key", '    E = U.eval_set(root, say, tag, roster=pol["roster"], key=False)',
     '    E = U.eval_set(root, say, tag, roster=pol["roster"], key=True, marker=os.path.join(root, "mk"))', ["dry_run"], "common"),
    ("Z33 registered n grid changed", "RP_ = dict(ns=(50, 100, 200, 400), n_dec=100,", "RP_ = dict(ns=(50, 100, 200, 300), n_dec=100,", ["constants"], "self"),
    ("Z34 500 -> 100 draws", "n_dec=100, draws=500,", "n_dec=100, draws=100,", ["constants"], "self"),
    ("Z35 SE of the ratio, not of its log", '    st["se_log"] = float(np.std(np.log(bt["rat"]), ddof=1))', '    st["se_log"] = float(np.std(bt["rat"], ddof=1))', ["e2e"], "self"),
    ("Z36 target accuracy from TRAIN (wrong side)", "    acc = float(y.mean())\n    N = len(y)", "    acc = float(D.A[D.T][:, mi].mean())\n    N = len(y)", ["e2e"], "self"),
    ("Z37 CS1 / CS2 read at the first n (not the deciding n)", '    n = c["n_dec"]\n    bt = cluster_boot(errs, n)', '    n = c["ns"][0]\n    bt = cluster_boot(errs, n)',
     ["e2e"], "self"),
    ("Z38 STRAT-SRC sampled on the AF-U cells", '        g, H = gs["SRC"]', '        g, H = gs["AF-U"]', ["e2e"], "self"),
    ("Z39 theta_map without the prior", "        g = ((y - P) / (P * (1 - P)) * q * a).sum() - t", "        g = ((y - P) / (P * (1 - P)) * q * a).sum()", ["sampling"], "self"),
)

if __name__ == "__main__":
    sys.exit(main())
