"""drift_replay.py: DRIFT-REPLAY -- replaying the content-closed v2 union EVAL as SYNTHETIC streams whose source mix shifts by
registered amounts, does a chi-square on cell occupancy detect the shift more often than the GATE-calibrated OOS rate (DR2), and
do AF-U cells detect it differently from matched-k k-means (DR1), at a GATE-calibrated false-alarm rate (DR0)? ZERO calls: no
judge, no LLM, no embedding call (cached vectors READ through rp12_pairing's read-only readers), no construction, no Gradle, NO
KEY COLUMN READ (correctness never enters). A CPU simulation on real items.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-05 (before any code or call) — DRIFT-REPLAY: replaying the content-closed v2
  union EVAL as SYNTHETIC streams whose source mix shifts by registered amounts, ..." (L24639-L24651, _as_of the registrar's commit
  8e681387, parent 07bc237f): DR0, DR2, DR1, Support (a)-(g), P1-P5, F-DR, WILL-NOT-SHOW; record L24618-L24623.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form, or from anywhere with --data-root <main checkout>; never
beside a construction: every step reads the pool; ONE heavy process: the run is CPU-bound, single-threaded BLAS):
  0. python tools/analysis/drift_replay.py --selftest   # synthetic fixtures (temp on E: via scratch_dir); opens NO DB of record
     python tools/analysis/drift_replay.py --mutants    # the mutant table, re-run (each must make the selftest fail)
  1. python tools/analysis/drift_replay.py --dry-run    # POOL line first; pins; denominators; B0-2 pool check; inputs re-hashed;
                                                        #   geometry; KM-U fits; GATE thresholds and the tau identity; a timed
                                                        #   COST ESTIMATE on GATE streams; NO EVAL read, writes nothing
  2. python tools/analysis/drift_replay.py --run        # marker first; the EVAL set (structure only) and vectors; streams;
       outcome WRITE-ONCE: experiment_results/archv2/drift_replay/outcome.txt (+ drift_replay.READ_STARTED). Never committed: pin
       by sha256 and back up to E:/TaxoArena_backup_<date>_drift_replay with SHA256SUMS.txt.
  Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; write-once paths absent; the B0-2 pool check, AF-U state, inputs manifest (53021e26...), AF / K cells and the
      frozen policy file through union_route_common.prepare (the policy file is only the eval view's B3 precondition: no policy
      enters); (2) geometry (escalation_rc.load_geometry); KM-U = g13_breakdown.ukm_fit at k = AF-U's total leaf count (refused
      unless 123), seeds 0-4; (3) GATE (escalation_rc R5's set) scores; the [DR-TAU] identity: ESCALATION-RC's candidate-form AF-U
      tau_oos recomputed on GATE must print 0.540800; per-arm GATE taus (DR-R3); (4) the marker; the EVAL set, structure only
      (eval view, no key column, the tripwire sealed), refused unless 5,907 / 5,404 ([DR-DENOM]) and the members are the six;
      (5) EVAL vectors (refused if any missing or unequal to the bundle's); (6) cells / OOS flags per arm; GATE reference
      occupancy and bins; GATE streams -> alarm levels; EVAL streams -> FAR, DET, delays; the stream bootstrap; the component
      bootstrap at s 0.20; (7) DR0, DR2, DR1, F-DR, descriptive tables, predictions, support; the outcome written mode "x".

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  DR-R1  Items. EVAL = G14's set read STRUCTURALLY from the eval view (side EVAL of mc6, every model with exactly one response:
         UNUSABLE_CELL's structural completeness; no key column named; the tripwire stays sealed): 5,907 items / 5,404 components.
         An item's declared source = the view's stratum_source (one per item; the 17 two-source multi-class items keep it). GATE =
         ESCALATION-RC R5's set (side GATE with a routing row; 2,033), source = the gen view's stratum_source.
  DR-R2  Cells. AF-U: the nearest of ALL 123 AF-U cells (122 graft leaves' vmfMu + the IFEVAL one-cell centroid; flatLeaf over all
         leaves, so filing never reads the declared source, as registered); the agreement with af_cells.tsv on EVAL is printed.
         KM-U seed s: the nearest of all 123 centroids of ukm_fit(bundle TRAIN, 123, s). SOURCE ORACLE: the declared source.
  DR-R3  OOS. Score = max cosine to the arm's cells (the same cells the item is filed among: source-blind); tau = numpy percentile 5
         (linear) of the GATE scores (TPR 0.95), per arm and per seed; OOS iff score < tau (strict). [DR-TAU] identity: ESCALATION-RC's
         operating point (its R3 candidate form: a one-cell item scored against its own cell only) is recomputed on GATE and must
         print 0.540800; the source-blind tau that the detectors use is printed beside it (CONDITION for the registrar: the
         registration names both "max-cos to the arm's cells" and the value 0.540800; they coincide only if the IFEVAL centroid
         never raises a GATE score; the rule is read as deciding, the value as an identity of the geometry).
  DR-R4  Streams. Each stream has its own child generator: numpy default_rng(20261005).spawn(N_EVAL) for EVAL in the order (i) the
         1,200 unshifted streams, (ii) s in (0.05, 0.10, 0.20, 0.40) x member in (BBH, GPQA, IFEVAL, MATH, MMLU_PRO, MUSR) x r in
         0..199; default_rng(20261006).spawn(2,000) for GATE. Per stream: u = g.random(1000); position t takes source
         searchsorted(cumsum(pi), u_t, 'right') with pi = pi_0 for t <= 500 and pi_1 = (1 - s) pi_0 + s e_m after (s = 0: pi_0
         throughout); then j = g.integers(0, n_source) (one array call) and the item = the source's j-th item in item_id order. pi_0
         = EVAL's own source shares; GATE streams use GATE's own source shares in both halves.
  DR-R5  Windows. w 200, evaluated every 10 items: window ends t = 200, 210, ..., 1000 (81 windows), window = items t-199..t.
  DR-R6  OCC-CHI = Pearson X^2 of the window's counts in the bins against w x the GATE reference occupancy of the bins. Reference
         occupancy = the arm's cell shares over the GATE items. Bins: a cell with w p_j >= 5 is its own bin; the others ("rare",
         those with p_j = 0 included) are sorted by (p_j, cell index) ascending and pooled cumulatively, a bin closing as soon as it
         expects >= 5; a leftover tail expecting < 5 joins the last rare bin (or, if no rare bin closed, the smallest non-rare bin).
  DR-R7  Alarm iff the statistic is STRICTLY above h. h = the smallest level at which at most floor(0.05 x 2,000) = 100 GATE streams
         raise any alarm over items 200-1,000 = sorted(max statistic per GATE stream)[n - 100 - 1].
  DR-R8  FALSE ALARM (s = 0 EVAL streams) = any window above h among the 81. For s > 0 only windows ending after item 500 count
         (t = 510, ..., 1,000; an earlier alarm is a false alarm, not a detection); DELAY = t_alarm - 500 (10..500); DET(s) = the
         share of streams with such an alarm; the others are UNDETECTED (censored at 500).
  DR-R9  Stream bootstrap: B 2,000, numpy default_rng(20261007); per replicate, for each member in the order of DR-R4, 200 stream
         indices with replacement (the members FIXED strata), then 5 seed indices with replacement (the seeds crossed with the
         streams; the SCALE-AGREE D-1 lesson); D_det and D_arm recomputed; 95% interval by the g13_comparator percentile rule
         (sorted[int(0.025 B)], sorted[int(0.975 B) - 1]). Per-member DR2 intervals from the same draws. Conditional on this EVAL set.
  DR-R10 Component bootstrap (descriptive, item reuse; its seed is not registered: default_rng(20261008)): B 200; per replicate the
         EVAL components resampled with replacement within each member, the s 0.20 streams regenerated from the SAME children on
         the resampled population (pi_0 = its shares); bins and levels fixed (GATE); DEFF_reuse = Var_comp / Var_stream of D_det
         (and of D_arm) printed beside the registered 1.5 assumption, n_eff = 1,200 / DEFF_reuse.
  DR-R11 Median delay over all streams with an undetected stream at +inf; "censored" when the median is +inf.
  DR-R12 DR0: CALIBRATED iff both AF-U FARs <= 0.10 (POINT; Clopper-Pearson two-sided 95% upper beside); MISCALIBRATED -> DR2 / DR1
         printed with the realised FARs and read UNDETERMINED (Brier not scoreable then). DR2: OCC-BETTER iff lo > 0, OOS-BETTER iff
         hi < 0, NEITHER otherwise; DR1 likewise TREE-BETTER / KM-BETTER / NEITHER (an end exactly 0 reads NEITHER). F-DR fires iff
         DR0 CALIBRATED and DR2 NEITHER or OOS-BETTER. Prediction bands closed; outcome probabilities Brier-summed.
  DR-R13 Not applicable (stated): no key or judge verdict (no wrong(established), no tie convention A / B); no call cache, --pilot
         or truncation guard (zero calls).
  DR-R14 DEVIATION (stated): the registration names union_af_route.py blob bf3f17db and g13_breakdown.py c29fa1c3 (both pinned
         unchanged: g13_breakdown through union_af_route's pin) and imports escalation_rc / union_route_common for the geometry and
         the B0-2 machinery (escalation_rc blob 8f99db7d, its code above the SELFTEST marker byte-identical to a17f6821).

[DELTA 2026-10-05, READY_drift_escalation (ec880315) B-1 / M-1 / C-1; insertion only]
  B-1 fix (a), the orchestrator's choice: DR-R6's REFERENCE OCCUPANCY (and so the bins) is now the arm's cell shares over the
  bundle's 12,334 TRAIN rows (filed by the arm's own nearest rule; SRC: the TRAIN rows' class sources), an object independent of
  both GATE and EVAL, so GATE and EVAL streams stand exchangeably against it; the alarm levels (DR-R7) and taus (DR-R3) stay
  GATE-calibrated. Under the old self-calibration (reference and level from the same GATE items) DR0 failed by construction
  (review emulation: EVAL FAR median 0.438). Selftest case b1_exch emulates it and fails under the old rule. M-1: the outcome
  says "N-bin POOLED occupancy", never "cell occupancy". C-1 confirmed: the source-blind tau rule decides, 0.540800 an identity.
SELFTEST: see the SELFTEST section (CASES); MUTANTS at the end; the table with each result is in the commit message.
NOT DONE HERE: the real --run (the operator's, after READY); no Kotlin / Gradle.
"""
import os
import sys


def _pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _pre_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import re            # noqa: E402
import math          # noqa: E402
import time          # noqa: E402
import types         # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc 8f99db7d, union_cells_io, union_af_route bf3f17db)

TAG = "[DRIFT]"
TEST_ID = "DRIFT-REPLAY"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-05 (before any code or call) — DRIFT-REPLAY: replaying the content-closed'
            ' v2 union EVAL as SYNTHETIC streams whose source mix shifts by registered amounts, ..." L24639-L24651 (_as_of 8e681387,'
            ' parent 07bc237f)')
OUT = "experiment_results/archv2/drift_replay"
REG = dict(pool=U.POOL, n_route=5907, comp_route=5404, uar_policy_sha=U.COMMON["uar_policy_sha"], manifest_sha=U.COMMON["manifest_sha"],
           out=OUT + "/outcome.txt", marker=OUT + "/drift_replay.READ_STARTED", ku_k=123, ku_seeds=(0, 1, 2, 3, 4), tau_rc="0.540800",
           members=("BBH", "GPQA", "IFEVAL", "MATH", "MMLU_PRO", "MUSR"), L=1000, change=500, w=200, step=10,
           s_grid=(0.05, 0.10, 0.20, 0.40), s_dec=0.20, R=200, n0=1200, n_gate=2000, alpha=0.05, far_max=0.10, e_min=5.0,
           rng_eval=20261005, rng_gate=20261006, rng_boot=20261007, B=2000, B_comp=200, rng_comp=20261008, chunk=400)
FIXTURE_REG = dict(out="res/drift/outcome.txt", marker="res/drift/READ_STARTED", members=("BBH", "MATH", "MMLU_PRO"), R=16, n0=48,
                   n_gate=160, B=300, B_comp=6, chunk=64)
_REG = [REG]


def reg():
    return _REG[0]


ERC, UAR, V, GB, GC = U.ERC, U.UAR, U.V, U.GB, U.GC
KU = tuple("KU%d" % s for s in (0, 1, 2, 3, 4))
SUPPORT = dict(deff=1.5, n_eff=800, se_dr2=0.0250, se_dr1=0.0192, se_dr0=0.0077, mde_dr2=0.070, mde_dr1=0.054, mde_dr0=0.019,
               disc_dr2=0.50, disc_dr1=0.15, seed_sd=0.03)
VERDICT = ("DR2 SCOREABLE (prediction +0.45 lies 0.45 from 0 > MDE80 0.070); DR1 DESCRIPTIVE-ONLY at the prediction (0.00 lies 0 from"
           " the bar < MDE80 0.054; still classified as registered); DR0 SCOREABLE (prediction 0.06 lies 0.04 from 0.10 > MDE80 0.019)")
PRED_FAR = (0.03, 0.10)
PROB_DR0 = (("CALIBRATED", 0.80), ("MISCALIBRATED", 0.20))
PRED_DET_OCC = (0.50, 0.95)
PRED_DET_OOS = (0.10, 0.55)
PRED_DDET = (0.20, 0.75)
PROB_DR2 = (("OCC-BETTER", 0.85), ("NEITHER", 0.12), ("OOS-BETTER", 0.03))
PRED_DARM = (-0.05, 0.05)
PROB_DR1 = (("NEITHER", 0.70), ("TREE-BETTER", 0.20), ("KM-BETTER", 0.10))
PRED_DELAY = (30.0, 150.0)
PRED_DET05 = (0.05, 0.30)
PRED_ORACLE = (0.00, 0.30)
HIT = Counter()


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the simulation core (pure numpy; DR-R4 .. DR-R11) ──────────────────────────────────────────────────────────────────

def make_bins(p, w, emin):
    """DR-R6 -> (K x nbins one-hot matrix, bin reference shares, number of rare bins)."""
    p = np.asarray(p, dtype=np.float64)
    K = len(p)
    E = w * p
    bins = [[j] for j in range(K) if E[j] >= emin]
    rare = sorted((j for j in range(K) if E[j] < emin), key=lambda j: (p[j], j))
    rb, cur, acc = [], [], 0.0
    for j in rare:
        cur.append(j)
        acc += E[j]
        if acc >= emin:
            rb.append(cur)
            cur, acc = [], 0.0
    if cur:
        if rb:
            rb[-1].extend(cur)
        elif bins:
            k = min(range(len(bins)), key=lambda i: (E[bins[i][0]], bins[i][0]))
            bins[k].extend(cur)
        else:
            rb.append(cur)
    allb = bins + rb
    M = np.zeros((K, len(allb)))
    for b, cells in enumerate(allb):
        M[cells, b] = 1.0
    return M, M.T @ p, len(rb)


def window_counts(cells, K, c):
    """(n, L) cell indices -> (n, nwin, K) counts of the windows ending at t = w, w + step, ..., L (DR-R5)."""
    n, L = cells.shape
    step, w = c["step"], c["w"]
    nb = L // step
    blk = np.arange(L) // step
    idx = (np.arange(n)[:, None] * nb + blk[None, :]) * K + cells
    cnt = np.bincount(idx.ravel(), minlength=n * nb * K).reshape(n, nb, K)
    cs = np.concatenate([np.zeros((n, 1, K), dtype=np.int64), np.cumsum(cnt, axis=1)], axis=1)
    ends = np.arange(w // step, nb + 1)
    return cs[:, ends] - cs[:, ends - w // step]


def chi_stat(cells, M, pb, c):
    """OCC-CHI per window: (n, nwin) Pearson X^2 of the binned window counts against w x pb (DR-R6)."""
    O = window_counts(cells, M.shape[0], c) @ M
    E = c["w"] * pb
    return (((O - E) ** 2) / E).sum(axis=-1)


def oos_stat(flags, c):
    """OOS-RATE per window: (n, nwin) count of OOS flags."""
    return window_counts(flags.astype(np.int64), 2, c)[:, :, 1].astype(np.float64)


def window_ends(c):
    return np.arange(c["w"], c["L"] + 1, c["step"])


def level(gate_max, alpha):
    """DR-R7: the smallest h with #{GATE streams whose max statistic > h} <= floor(alpha n)."""
    s = np.sort(np.asarray(gate_max, dtype=np.float64))
    n = len(s)
    k = int(math.floor(alpha * n + 1e-9))
    return float(s[n - k - 1])


def first_alarm(S, h, c):
    """DR-R8 for shifted streams -> (detected bool (n,), delay (n,), +inf when undetected)."""
    ends = window_ends(c)
    post = ends > c["change"]
    A = S[:, post] > h
    det = A.any(axis=1)
    j = np.argmax(A, axis=1)
    d = np.where(det, ends[post][j] - c["change"], np.inf).astype(np.float64)
    return det, d


def false_alarm(S, h):
    return (S > h).any(axis=1)


def median_delay(d):
    m = float(np.median(np.asarray(d, dtype=np.float64))) if len(d) else float("inf")
    return m


def spawn(seed, n):
    """default_rng(seed).spawn(n)'s children as SeedSequences (a fresh generator per use: the component bootstrap reuses them)."""
    return np.random.SeedSequence(seed).spawn(n)


def draw_streams(children, pools, pi0, pi1, c):
    """DR-R4: one stream per child -> (n, L) population positions. pools: per-member arrays of population positions."""
    L, ch = c["L"], c["change"]
    flat = np.concatenate([np.asarray(p, dtype=np.int64) for p in pools])
    off = np.concatenate([[0], np.cumsum([len(p) for p in pools])[:-1]]).astype(np.int64)
    sizes = np.array([len(p) for p in pools], dtype=np.int64)
    M = len(pools)
    out = np.empty((len(children), L), dtype=np.int64)
    for i, gseed in enumerate(children):
        g = np.random.default_rng(gseed)
        u = g.random(L)
        src = np.empty(L, dtype=np.int64)
        src[:ch] = np.searchsorted(np.cumsum(pi0[i]), u[:ch], side="right")
        src[ch:] = np.searchsorted(np.cumsum(pi1[i]), u[ch:], side="right")
        src = np.minimum(src, M - 1)
        j = g.integers(0, sizes[src])
        out[i] = flat[off[src] + j]
    return out


def stream_plan(c, members, pi0):
    """DR-R4's EVAL order -> list of (s, member index or -1, pi_1)."""
    plan = [(0.0, -1, pi0)] * c["n0"]
    for s in c["s_grid"]:
        for mi in range(len(members)):
            e = np.zeros(len(members))
            e[mi] = 1.0
            plan += [(s, mi, (1.0 - s) * pi0 + s * e)] * c["R"]
    return plan


def stats_for(streams, arms, c):
    """Every arm-detector statistic for a set of streams, in chunks -> {(arm, det): (n, nwin)}."""
    out = {}
    n = len(streams)
    for key, a in arms.items():
        res = []
        for i0 in range(0, n, c["chunk"]):
            cell = a["cell"][streams[i0:i0 + c["chunk"]]]
            if key[1] == "OCC":
                res.append(chi_stat(cell, a["M"], a["pb"], c))
            else:
                res.append(oos_stat(cell, c))
        out[key] = np.vstack(res) if res else np.zeros((0, len(window_ends(c))))
    return out


def pct(xs, q):
    return U.UCI.pct(sorted(float(x) for x in xs), q)


def boot(det, members_idx, seeds_det, c):
    """DR-R9: the stream bootstrap at s_dec. det: {(arm, det): (n,) bool over the s_dec streams}, members_idx: per member the
    positions (R each); seeds_det: [(n,) per KM-U seed]. -> dict of replicate arrays."""
    rng = np.random.default_rng(c["rng_boot"])
    M = len(members_idx)
    ns = len(seeds_det)
    occ, oos = det[("AF-U", "OCC")].astype(np.float64), det[("AF-U", "OOS")].astype(np.float64)
    kus = np.vstack([x.astype(np.float64) for x in seeds_det]) if ns else np.zeros((0, len(occ)))
    rd2, rd1, rpm = [], [], [[] for _ in range(M)]
    for _b in range(c["B"]):
        idx = [members_idx[m][rng.integers(0, len(members_idx[m]), len(members_idx[m]))] for m in range(M)]
        sd = rng.integers(0, ns, ns) if ns else np.zeros(0, dtype=np.int64)
        allx = np.concatenate(idx)
        rd2.append(float(np.mean(occ[allx] - oos[allx])))
        rd1.append(float(np.mean(occ[allx]) - np.mean([np.mean(kus[s][allx]) for s in sd])))
        for m in range(M):
            rpm[m].append(float(np.mean(occ[idx[m]] - oos[idx[m]])))
    return dict(d2=np.array(rd2), d1=np.array(rd1), pm=[np.array(x) for x in rpm])


def interval(pt, reps):
    return dict(point=float(pt), lo=pct(reps, 0.025), hi=pct(reps, 0.975), se=float(np.std(reps, ddof=1)) if len(reps) > 1 else 0.0)


def cp_upper(k, n):
    from scipy.stats import beta
    return 1.0 if k >= n else float(beta.ppf(0.975, k + 1, n - k))


def dr0_word(far_occ, far_oos, far_max):
    return "CALIBRATED" if (far_occ <= far_max and far_oos <= far_max) else "MISCALIBRATED"


def dr2_word(st, calibrated):
    if not calibrated:
        return "UNDETERMINED"
    if st["lo"] > 0:
        return "OCC-BETTER"
    if st["hi"] < 0:
        return "OOS-BETTER"
    return "NEITHER"


def dr1_word(st, calibrated):
    if not calibrated:
        return "UNDETERMINED"
    if st["lo"] > 0:
        return "TREE-BETTER"
    if st["hi"] < 0:
        return "KM-BETTER"
    return "NEITHER"


def simulate(E, Gt, arms_e, arms_g, members, c, say=None):
    """The whole stream readout. E / Gt: dict(src=member index per population position); arms_*: {(arm, det): dict(cell=..., M, pb)}
    over the EVAL / GATE populations. -> st (every number the lines print)."""
    M = len(members)
    pools_e = [np.flatnonzero(E["src"] == m) for m in range(M)]
    pools_g = [np.flatnonzero(Gt["src"] == m) for m in range(M)]
    pi0 = np.array([len(p) for p in pools_e], dtype=np.float64) / len(E["src"])
    pig = np.array([len(p) for p in pools_g], dtype=np.float64) / len(Gt["src"])
    if (pi0 <= 0).any() or (pig <= 0).any():
        refuse("a member has no EVAL or no GATE item (pi_0 %s, GATE %s)" % (pi0.tolist(), pig.tolist()))
    t0 = time.time()
    gch = spawn(c["rng_gate"], c["n_gate"])
    gs = draw_streams(gch, pools_g, [pig] * c["n_gate"], [pig] * c["n_gate"], c)
    Sg = stats_for(gs, arms_g, c)
    lev = {k: level(v.max(axis=1), c["alpha"]) for k, v in Sg.items()}
    gfa = {k: float(np.mean(false_alarm(v, lev[k]))) for k, v in Sg.items()}
    plan = stream_plan(c, members, pi0)
    ech = spawn(c["rng_eval"], len(plan))
    es = draw_streams(ech, pools_e, [pi0] * len(plan), [p[2] for p in plan], c)
    Se = stats_for(es, arms_e, c)
    s_of = np.array([p[0] for p in plan])
    m_of = np.array([p[1] for p in plan])
    st = dict(levels=lev, gate_fa=gfa, pi0=pi0, pig=pig, n_streams=len(plan), far={}, det={}, delay={}, t_sim=0.0)
    z = s_of == 0.0
    for k, S in Se.items():
        fa = false_alarm(S[z], lev[k])
        st["far"][k] = (int(fa.sum()), int(z.sum()))
        for s in c["s_grid"]:
            sel = s_of == s
            d_, dl = first_alarm(S[sel], lev[k], c)
            st["det"][(k, s)] = d_
            st["delay"][(k, s)] = dl
    st["m_of"] = {s: m_of[s_of == s] for s in c["s_grid"]}
    sd = c["s_dec"]
    mo = st["m_of"][sd]
    members_idx = [np.flatnonzero(mo == m) for m in range(M)]
    det = {k: st["det"][(k, sd)] for k in (("AF-U", "OCC"), ("AF-U", "OOS"))}
    seeds_det = [st["det"][((nm, "OCC"), sd)] for nm in KU if (nm, "OCC") in Se]
    bt = boot(det, members_idx, seeds_det, c)
    occ = det[("AF-U", "OCC")].astype(np.float64)
    oos = det[("AF-U", "OOS")].astype(np.float64)
    st["D2"] = interval(np.mean(occ - oos), bt["d2"])
    st["D1"] = interval(np.mean(occ) - np.mean([np.mean(x) for x in seeds_det]), bt["d1"])
    st["D2_m"] = [interval(np.mean(occ[members_idx[m]] - oos[members_idx[m]]), bt["pm"][m]) for m in range(M)]
    st["disc2"] = float(np.mean(occ != oos))
    st["disc1"] = float(np.mean([np.mean(occ != x) for x in seeds_det]))
    st["seed_sd"] = float(np.std([np.mean(x) for x in seeds_det], ddof=1)) if len(seeds_det) > 1 else 0.0
    st["t_sim"] = time.time() - t0
    st["plan_children"] = ech
    st["pools_e"] = pools_e
    return st


def comp_boot(E, arms_e, members, st, c):
    """DR-R10: the component bootstrap at s_dec -> (D_det replicates, D_arm replicates)."""
    M = len(members)
    rng = np.random.default_rng(c["rng_comp"])
    comp = np.asarray(E["comp"])
    plan = stream_plan(c, members, st["pi0"])
    sel = [i for i, p in enumerate(plan) if p[0] == c["s_dec"]]
    ch = [st["plan_children"][i] for i in sel]
    mi = np.array([plan[i][1] for i in sel])
    by_m = []
    for m in range(M):
        cm = sorted(set(comp[E["src"] == m].tolist()))
        by_m.append([np.flatnonzero((comp == x) & (E["src"] == m)) for x in cm])
    keys = [("AF-U", "OCC"), ("AF-U", "OOS")] + [(nm, "OCC") for nm in KU if (nm, "OCC") in arms_e]
    sub = {k: arms_e[k] for k in keys}
    d2, d1 = [], []
    for _b in range(c["B_comp"]):
        pools = []
        for m in range(M):
            dr = rng.integers(0, len(by_m[m]), len(by_m[m]))
            pools.append(np.concatenate([by_m[m][j] for j in dr]))
        pi0 = np.array([len(p) for p in pools], dtype=np.float64)
        pi0 = pi0 / pi0.sum()
        pi1 = []
        for m_ in mi:
            e = np.zeros(M)
            e[m_] = 1.0
            pi1.append((1.0 - c["s_dec"]) * pi0 + c["s_dec"] * e)
        es = draw_streams(ch, pools, [pi0] * len(ch), pi1, c)
        S = stats_for(es, sub, c)
        dd = {k: first_alarm(S[k], st["levels"][k], c)[0].astype(np.float64) for k in keys}
        d2.append(float(np.mean(dd[("AF-U", "OCC")] - dd[("AF-U", "OOS")])))
        kus = [np.mean(dd[k]) for k in keys[2:]]
        d1.append(float(np.mean(dd[("AF-U", "OCC")]) - (np.mean(kus) if kus else 0.0)))
    return np.array(d2), np.array(d1)


# ── readout lines (pure functions of st; the selftest drives every branch through them) ────────────────────────────────

def dr_lines(st):
    c = reg()
    L = []
    say = L.append
    mem = st["members"]
    far_o, far_s = st["far"][("AF-U", "OCC")], st["far"][("AF-U", "OOS")]
    fo, fs = far_o[0] / far_o[1], far_s[0] / far_s[1]
    say("")
    say("=== DRIFT-REPLAY (%s) ===" % REG_TEXT)
    say("DENOMINATOR: EVAL %d items in %d components (Kish mean cluster size %.3f; G14's set, structure only); GATE %d items (levels,"
        " reference occupancy, taus); streams: %d EVAL (%d unshifted + %d shifted = %d s x %d members x %d) and %d GATE, %d items each;"
        " the shift is SYNTHETIC (resampled; no real traffic, no temporal order, no new domain)" % (
            st["n_eval"], st["n_comp"], st["kish"], st["n_gate_items"], st["n_streams"], c["n0"], st["n_streams"] - c["n0"], len(c["s_grid"]),
            len(mem), c["R"], c["n_gate"], c["L"]))
    say("OCC-CHI READS POOLED OCCUPANCY (M-1): Pearson X^2 of the window's counts in the %d-bin POOLED occupancy of AF-U (KM-U %s; SRC"
        " %d bins): rare cells pooled by ascending reference share, mixing cells of different sources; never 'cell occupancy'. Reference"
        " = the bundle's %d TRAIN rows (B-1 fix (a)); alarm levels GATE-calibrated" % (
            st["bins"]["AF-U"], "/".join(str(st["bins"][nm]) for nm in KU), st["bins"]["SRC"], st["n_ref"]))
    say("LIKE WITH LIKE: AF-U [SC] (source-conditioned construction: a TREE-BETTER reads 'source-conditioned cells see a source shift',"
        " never 'discovered structure') vs KM-U [LF] (k %d, seeds 0-4); source oracle [SRC] ceiling only" % c["ku_k"])
    say("pi_0 (EVAL shares): %s | GATE shares: %s" % (", ".join("%s %.4f" % (m, x) for m, x in zip(mem, st["pi0"])),
                                                    ", ".join("%s %.4f" % (m, x) for m, x in zip(mem, st["pig"]))))
    for k in sorted(st["levels"]):
        say("  ALARM LEVEL %-5s %-3s h = %.5f (GATE streams alarming %.4f; DR-R7)" % (k[0], k[1], st["levels"][k], st["gate_fa"][k]))
    say("DR0 (DECIDING precondition; the POINT decides): FAR on %d unshifted EVAL streams, AF-U OCC-CHI %.4f (%d; Clopper-Pearson upper"
        " %.4f), OOS-RATE %.4f (%d; CP upper %.4f); bar %.2f" % (far_o[1], fo, far_o[0], cp_upper(*far_o), fs, far_s[0], cp_upper(*far_s),
                                                                 c["far_max"]))
    w0 = dr0_word(fo, fs, c["far_max"])
    cal = w0 == "CALIBRATED"
    if cal:
        hit("DR0.CALIBRATED")
        say("  DR0 -> CALIBRATED (both AF-U FARs <= %.2f)" % c["far_max"])
    else:
        hit("DR0.MISCALIBRATED")
        say("  DR0 -> MISCALIBRATED: the GATE-to-EVAL transport of the alarm level FAILS (FAR > %.2f on %s); DR2 and DR1 are printed"
            " with the realised FAR and read UNDETERMINED" % (c["far_max"], " and ".join(n_ for n_, f_ in (("OCC-CHI", fo), ("OOS-RATE", fs))
                                                                                       if f_ > c["far_max"])))
    d2 = st["D2"]
    sdec = c["s_dec"]
    det_o = float(np.mean(st["det"][(("AF-U", "OCC"), sdec)]))
    det_s = float(np.mean(st["det"][(("AF-U", "OOS"), sdec)]))
    say("DR2 (DECIDING; the INTERVAL decides): AF-U at s %.2f, D_det = DET(OCC-CHI) %.4f - DET(OOS-RATE) %.4f = %+.4f, stream-paired,"
        " pooled over the %d members | stream bootstrap 95%% [%+.4f, %+.4f] (B %d)%s" % (
            sdec, det_o, det_s, d2["point"], len(mem), d2["lo"], d2["hi"], c["B"], "" if cal else " | realised FAR OCC %.4f / OOS %.4f" % (fo, fs)))
    v2 = dr2_word(d2, cal)
    if v2 == "OCC-BETTER":
        hit("DR2.OCC")
        say("  DR2 -> OCC-BETTER (the 95% interval lies wholly above 0)")
    elif v2 == "OOS-BETTER":
        hit("DR2.OOS")
        say("  DR2 -> OOS-BETTER (the 95% interval lies wholly below 0)")
    elif v2 == "NEITHER":
        hit("DR2.NEITHER")
        say("  DR2 -> NEITHER (the 95% interval covers 0)")
    else:
        hit("DR2.UNDETERMINED")
        say("  DR2 -> UNDETERMINED (DR0 MISCALIBRATED)")
    if d2["lo"] <= 0:
        hit("DR2.REFUTED")
        say("  rule 8: OCC-BETTER is refuted (lower bound %+.4f <= 0)" % d2["lo"])
    else:
        hit("DR2.NOT_REFUTED")
        say("  rule 8: OCC-BETTER is not refuted (lower bound %+.4f > 0)" % d2["lo"])
    d1 = st["D1"]
    det_k = [float(np.mean(st["det"][((nm, "OCC"), sdec)])) for nm in KU]
    say("DR1 (DECIDING; the INTERVAL decides): OCC-CHI at s %.2f, D_arm = DET(AF-U) %.4f - DET(KM-U, mean over seeds %s) %.4f = %+.4f,"
        " stream-paired, seeds crossed | 95%% [%+.4f, %+.4f]%s" % (sdec, det_o, " / ".join("%.4f" % x for x in det_k), float(np.mean(det_k)),
                                                                   d1["point"], d1["lo"], d1["hi"], "" if cal else " | realised FAR OCC %.4f / OOS %.4f" % (fo, fs)))
    v1 = dr1_word(d1, cal)
    if v1 == "TREE-BETTER":
        hit("DR1.TREE")
        say("  DR1 -> TREE-BETTER (the 95% interval lies wholly above 0): source-conditioned cells see a source shift (AF-U [SC])")
    elif v1 == "KM-BETTER":
        hit("DR1.KM")
        say("  DR1 -> KM-BETTER (the 95% interval lies wholly below 0): any drift-monitor claim narrows to 'cells of any kind', not the tree")
    elif v1 == "NEITHER":
        hit("DR1.NEITHER")
        say("  DR1 -> NEITHER (the 95% interval covers 0)")
    else:
        hit("DR1.UNDETERMINED")
        say("  DR1 -> UNDETERMINED (DR0 MISCALIBRATED)")
    if d1["lo"] <= 0:
        hit("DR1.REFUTED")
        say("  rule 8: TREE-BETTER is refuted (lower bound %+.4f <= 0)" % d1["lo"])
    else:
        hit("DR1.NOT_REFUTED")
        say("  rule 8: TREE-BETTER is not refuted (lower bound %+.4f > 0)" % d1["lo"])
    fire = cal and v2 in ("NEITHER", "OOS-BETTER")
    if fire:
        hit("FDR.FIRED")
        say("FALSIFIER F-DR: FIRED (DR0 CALIBRATED and DR2 %s): in-scope source-mix shifts are caught as well by the GATE-calibrated OOS"
            " rate as by pooled occupancy; the cell layer adds no drift signal beyond the OOS trigger the online design already uses; it"
            " overturns any claim that cells serve as a drift monitor for in-scope mix change" % v2)
    else:
        hit("FDR.NOT_FIRED")
        say("FALSIFIER F-DR: NOT FIRED (DR0 %s, DR2 %s; F-DR fires iff DR0 CALIBRATED and DR2 NEITHER or OOS-BETTER)" % (w0, v2))
    say("  per-member DR2 (descriptive; the same draws): " + "; ".join("%s %+.4f [%+.4f, %+.4f]" % (m, x["point"], x["lo"], x["hi"])
                                                                     for m, x in zip(mem, st["D2_m"])))
    say("FAR per arm x detector (DESCRIPTIVE): " + "; ".join("%s %s %.4f" % (k[0], k[1], st["far"][k][0] / st["far"][k][1]) for k in sorted(st["far"])))
    say("DET(s) AND MEDIAN DELAY (descriptive; censored at 500 = UNDETECTED; pooled | per member):")
    for k in sorted(set(k_ for k_, _s in st["det"])):
        for s in c["s_grid"]:
            dd, dl = st["det"][(k, s)], st["delay"][(k, s)]
            mo = st["m_of"][s]
            md = median_delay(dl)
            per = []
            for mi, m in enumerate(mem):
                sel = mo == mi
                mm = median_delay(dl[sel])
                per.append("%s %.3f/%s" % (m, float(np.mean(dd[sel])), "cens" if math.isinf(mm) else "%.0f" % mm))
            say("    %-5s %-3s s %.2f: DET %.4f, median delay %s, censored %.4f | %s" % (
                k[0], k[1], s, float(np.mean(dd)), "censored" if math.isinf(md) else "%.1f" % md, float(np.mean(~dd)), "; ".join(per)))
    orc = float(np.mean(st["det"][(("SRC", "OCC"), sdec)]))
    say("SOURCE ORACLE (ceiling, descriptive): OCC-CHI on the declared-source bins at s %.2f: DET %.4f; minus AF-U OCC-CHI = %+.4f" % (
        sdec, orc, orc - det_o))
    say("STRUCTURAL (registered (g)): EVAL OOS rate per member (AF-U): %s; spread %.4f (equal rates make OOS-RATE blind to a mix shift"
        " by construction)" % (", ".join("%s %.4f" % (m, x) for m, x in zip(mem, st["oos_m"])), max(st["oos_m"]) - min(st["oos_m"])))
    cb = st.get("comp")
    if cb is not None:
        hit("COMP.DONE")
        say("COMPONENT BOOTSTRAP at s %.2f (descriptive, item reuse; DR-R10; B %d): D_det 95%% [%+.4f, %+.4f] (SD %.4f); D_arm 95%% [%+.4f,"
            " %+.4f] (SD %.4f)" % (sdec, cb["B"], cb["d2"]["lo"], cb["d2"]["hi"], cb["d2"]["se"], cb["d1"]["lo"], cb["d1"]["hi"], cb["d1"]["se"]))
    else:
        hit("COMP.SKIPPED")
        say("COMPONENT BOOTSTRAP: not run (B_comp 0)")
    dre = (cb["d2"]["se"] ** 2 / d2["se"] ** 2) if (cb and d2["se"] > 0) else float("nan")
    say("SUPPORT AS REALISED: (a) DR2 / DR1 on %d shifted streams at s %.2f, DR0 on %d unshifted; %d post-change draws (%.1f per EVAL"
        " item); (b) DEFF_reuse (component / stream variance of D_det) %.3f against the registered 1.5 assumption; (c) n_eff %.0f"
        " (registered 800); (d) SE: DR2 stream %.4f (registered 0.0250), DR1 %.4f (registered 0.0192), DR0 sqrt(F(1-F)/n) %.4f"
        " (registered 0.0077); discordance DR2 %.4f (planning 0.50), DR1 %.4f (planning 0.15); between-seed SD of DET %.4f (planning"
        " 0.03; seed SE %.4f); (e) MDE80 DR2 %.4f, DR1 %.4f; verdict line of record: %s" % (
            len(st["m_of"][sdec]), sdec, far_o[1], int(len(st["m_of"][sdec]) * (c["L"] - c["change"])),
            len(st["m_of"][sdec]) * (c["L"] - c["change"]) / float(st["n_eval"]), dre,
            (len(st["m_of"][sdec]) / dre) if dre == dre and dre > 0 else float("nan"), d2["se"], d1["se"],
            math.sqrt(fo * (1 - fo) / far_o[1]), st["disc2"], st["disc1"], st["seed_sd"], st["seed_sd"] / math.sqrt(5),
            2.80 * d2["se"], 2.80 * d1["se"], VERDICT))
    # predictions
    preds = [("P1 FAR AF-U OCC-CHI 0.06 [0.03, 0.10]", fo, PRED_FAR, "%.4f"), ("P1 FAR AF-U OOS-RATE 0.06 [0.03, 0.10]", fs, PRED_FAR, "%.4f"),
             ("P2 DET(OCC-CHI) at s 0.20 0.75 [0.50, 0.95]", det_o, PRED_DET_OCC, "%.4f"),
             ("P2 DET(OOS-RATE) at s 0.20 0.30 [0.10, 0.55]", det_s, PRED_DET_OOS, "%.4f"),
             ("P2 D_det +0.45 [+0.20, +0.75]", d2["point"], PRED_DDET, "%+.4f"), ("P3 D_arm 0.00 [-0.05, +0.05]", d1["point"], PRED_DARM, "%+.4f"),
             ("P4 AF-U OCC-CHI median delay at s 0.40 70 [30, 150] (descriptive)", st["p4_delay"], PRED_DELAY, "%.1f"),
             ("P4 AF-U OCC-CHI DET at s 0.05 0.15 [0.05, 0.30] (descriptive)", st["p4_det"], PRED_DET05, "%.4f"),
             ("P5 source oracle minus AF-U OCC-CHI DET at s 0.20 +0.10 [0.00, +0.30] (descriptive)", orc - det_o, PRED_ORACLE, "%+.4f")]
    for lab, x, band, fmt in preds:
        ok = U.in_band(x, band)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        say("PREDICTION %s: observed %s -> %s" % (lab, "censored" if math.isinf(x) else fmt % x, "HELD" if ok else "FAILED"))
    say("PREDICTION P1 DR0 CALIBRATED 0.80: observed %s; Brier %.4f" % (w0, U.brier(PROB_DR0, w0)))
    for lab, v, probs in (("P2 DR2 OCC-BETTER 0.85, NEITHER 0.12, OOS-BETTER 0.03", v2, PROB_DR2),
                          ("P3 DR1 NEITHER 0.70, TREE-BETTER 0.20, KM-BETTER 0.10", v1, PROB_DR1)):
        if v == "UNDETERMINED":
            hit("BRIER.NOT_SCOREABLE")
            say("PREDICTION %s: observed UNDETERMINED (DR0 MISCALIBRATED); Brier NOT SCOREABLE" % lab)
        else:
            hit("BRIER.SCORED")
            say("PREDICTION %s: observed %s; Brier %.4f" % (lab, v, U.brier(probs, v)))
    say("WORDS: the shift is SYNTHETIC (streams resampled from one EVAL set by a registered mixing rule); AF-U is [SC] and the shift is a"
        " source shift, so a TREE-BETTER never reads 'discovered structure'; no key read (correctness never enters); zero calls")
    say("WILL NOT SHOW (registered): real traffic or real drift; new-domain detection (no member held out); any accuracy or routing"
        " consequence; a discovered-structure advantage; detectors or windows other than these two at w 200; anything beyond one draw,"
        " six sources and these items")
    return L, dict(DR0=w0, DR2=v2, DR1=v1, F_DR=bool(fire))


# ── data path ──────────────────────────────────────────────────────────────────────────────────────────────────────────

def files():
    return [os.path.abspath(__file__), U.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS]


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)): DR2 / DR1 %d members x %d = %d shifted streams at s %.2f (members fixed strata); DR0 %d"
        " unshifted streams; EVAL %d items / %d components (Kish 1.09); DEFF 1.5 (DECLARED pilot assumption, item reuse), n_eff 800;"
        " SE DR2 0.0250, DR1 0.0192, DR0 0.0077; MDE80 DR2 0.070, DR1 0.054, DR0 0.019; %s" % (
            len(c["members"]), c["R"], len(c["members"]) * c["R"], c["s_dec"], c["n0"], c["n_route"], c["comp_route"], VERDICT))
    say("PLANNED: streams of %d items, change after item %d; s in %s; R %d per (s, member); %d unshifted EVAL streams; %d GATE streams;"
        " w %d every %d items; bins expecting >= %g; alarm level at GATE FA %.2f; FAR bar %.2f; rngs EVAL default_rng(%d), GATE"
        " default_rng(%d), bootstrap default_rng(%d) B %d, component bootstrap default_rng(%d) B %d; KM-U k %d seeds %s; tau identity %s" % (
            c["L"], c["change"], "{%s}" % ", ".join("%.2f" % s for s in c["s_grid"]), c["R"], c["n0"], c["n_gate"], c["w"], c["step"],
            c["e_min"], c["alpha"], c["far_max"], c["rng_eval"], c["rng_gate"], c["rng_boot"], c["B"], c["rng_comp"], c["B_comp"], c["ku_k"],
            "-".join(str(s) for s in (c["ku_seeds"][0], c["ku_seeds"][-1])), c["tau_rc"]))
    say("MEMBERS (registered order): %s" % ", ".join(c["members"]))


def ku_fit(Xt, k, seeds):
    out = {}
    for s in seeds:
        fit, _t = GB.ukm_fit(Xt, k, s)
        out["KU%d" % s] = GC.FM.unit_rows(np.asarray(fit["centers"], dtype=np.float64))
    return out


def nearest(X, C):
    S = X @ C.T
    return np.argmax(S, axis=1), S.max(axis=1)


def gate_meta(cfg, say):
    """{GATE item: (component, stratum_source, domain)} from the gen view (structure only; the key never named)."""
    tw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view", say)
    try:
        meta = V.side_items(tw, cfg.cv_u, "GATE")
    finally:
        tw.close()
    if not V.after_sha(cfg.gen_path, gsha, "gen_view", say):
        refuse("[PIN] the gen view's sha moved during the GATE read")
    return meta


def eval_structure(cfg, say):
    """DR-R1: G14's EVAL set from the eval view, STRUCTURE ONLY (no key column; the tripwire stays sealed)."""
    rule = cfg.pre.get("variant_rule")
    V.b3_guard(cfg)
    tw, esha = V.open_tw("eval", "route", cfg.eval_path, cfg.eval_sha, "eval_view", say)
    try:
        nc, ni, scope = V.pool_row(tw, cfg.pool_u, cfg.cv_u)
        if nc != cfg.reg["comp_eval_u"] or ni != cfg.reg["n_eval_u"]:
            refuse("pool counts %d / %d differ from the registration's %d / %d" % (nc, ni, cfg.reg["comp_eval_u"], cfg.reg["n_eval_u"]))
        models = sorted(m for m, s in V.registry(tw, cfg.cv_u).items() if s == "ACTIVE")
        if len(models) != cfg.reg["roster_u"] or V.EXCLUDED in models:
            refuse("roster check failed")
        meta = V.side_items(tw, cfg.cv_u, "EVAL")
        cc = V.cell_counts(tw, "response", cfg.cv_u, models, meta)
        items = sorted(V.structurally_complete(cc, models, rule))
        sealed = bool(getattr(tw, "sealed", True))
    finally:
        tw.close()
    if not V.after_sha(cfg.eval_path, esha, "eval_view", say):
        refuse("[PIN] the eval view's sha moved during the structural read")
    say("  EVAL SET (DR-R1; structure only, tripwire sealed %s): eval view pool %s (scope %r) %d items / %d components; %d models;"
        " structurally complete under %s: %d items / %d components" % (sealed, cfg.pool_u, scope, ni, nc, len(models), rule, len(items),
                                                                       len(set(meta[i][0] for i in items))))
    return items, meta, sealed


def arms_from(Xe, Xg, Xt, src_e, src_g, src_t, g, cents, members, c, say=None):
    """DR-R2 / DR-R3 / DR-R6 (B-1 fix (a)): cells and OOS flags over the EVAL and GATE populations; tau from GATE; the reference
    occupancy and the bins from the bundle's TRAIN rows (Xt / src_t), an object independent of both GATE and EVAL."""
    info = {}
    arms_e, arms_g = {}, {}
    geos = [("AF-U", g.af_C)] + sorted(cents.items())
    for nm, C in geos:
        ce, oe = nearest(Xe, C)
        cg, og = nearest(Xg, C)
        ct, _ot = nearest(Xt, C)
        tau = float(np.percentile(og, 5.0))
        p = np.bincount(ct, minlength=len(C)).astype(np.float64) / len(ct)
        Mb, pb, nrare = make_bins(p, c["w"], c["e_min"])
        arms_e[(nm, "OCC")] = dict(cell=ce, M=Mb, pb=pb)
        arms_g[(nm, "OCC")] = dict(cell=cg, M=Mb, pb=pb)
        arms_e[(nm, "OOS")] = dict(cell=(oe < tau).astype(np.int64))
        arms_g[(nm, "OOS")] = dict(cell=(og < tau).astype(np.int64))
        info[nm] = dict(tau=tau, tpr=float(np.mean(og >= tau)), oos_e=float(np.mean(oe < tau)), cells=len(C), bins=Mb.shape[1], rare=nrare,
                        cell_e=ce, oos_flags=(oe < tau))
    p = np.bincount(src_t, minlength=len(members)).astype(np.float64) / len(src_t)
    Mb, pb, nrare = make_bins(p, c["w"], c["e_min"])
    arms_e[("SRC", "OCC")] = dict(cell=np.asarray(src_e, dtype=np.int64), M=Mb, pb=pb)
    arms_g[("SRC", "OCC")] = dict(cell=np.asarray(src_g, dtype=np.int64), M=Mb, pb=pb)
    info["SRC"] = dict(cells=len(members), bins=Mb.shape[1], rare=nrare)
    return arms_e, arms_g, info


def prepare(say, c):
    S = U.prepare(say, c, refuse, hit)
    u = UAR.reg()
    ip = UAR.input_paths()
    b, _meta = GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    g = ERC.load_geometry(say, S["man"], S["single"], b, S["af"])
    Lk = int(sum(int(v) for v in S["ksrc"].values()))
    if Lk != int(c["ku_k"]):
        hit("REFUSE.KU_K")
        refuse("AF-U's total leaf count is %d, not the registered matched k %d" % (Lk, c["ku_k"]))
    Xt = GC.FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    t0 = time.time()
    cents = ku_fit(Xt, Lk, c["ku_seeds"])
    say("  KM-U (DR-R2): ukm_fit k %d on %d bundle TRAIN rows, seeds %s (%.1f s)" % (Lk, len(Xt), ", ".join(str(s) for s in c["ku_seeds"]),
                                                                                    time.time() - t0))
    side, _smeta = UAR._SIDES[0]()
    val = UAR.afu_paths(S["single"])[1]
    rows_h, _rows_t = ERC.item_rows(ip["merged"] if S["single"] else val)
    gits, gcell, gsrc = ERC.gate_items(rows_h, side)
    if not gits:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: the levels and taus are undefined")
    vg = ERC.get_vectors(gits)
    nov = [i for i in gits if i not in vg]
    if nov:
        refuse("%d GATE item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    sc = ERC.score_items(say, g, gits, gcell, gsrc, vg)
    _tm, to = ERC.thresholds(sc["AF"][0], sc["AF"][1])
    say("  [DR-TAU] ESCALATION-RC's candidate-form AF-U tau_oos on %d GATE items: %.6f (registered identity %s)" % (len(gits), to, c["tau_rc"]))
    if "%.6f" % to != c["tau_rc"]:
        hit("REFUSE.TAU")
        refuse("[DR-TAU] ESCALATION-RC's AF-U operating point recomputes to %.6f, not %s: the geometry is not ESCALATION-RC's" % (to, c["tau_rc"]))
    hit("TAU.OK")
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    gm = gate_meta(cfg, say)
    miss = [i for i in gits if i not in gm]
    if miss:
        refuse("%d GATE item(s) of the R5 set are not GATE items of the gen view (first %s)" % (len(miss), miss[:3]))
    classes = [str(x) for x in b["classes"]]
    tsrc = [U.UCI.member(classes[int(y)]) for y in np.asarray(b["train_y"], dtype=int)]
    say("  REFERENCE OCCUPANCY (DR-R6, B-1 fix (a)): the bundle's %d TRAIN rows (independent of GATE and EVAL); alarm levels and"
        " taus stay GATE-calibrated" % len(Xt))
    return dict(S, b=b, g=g, cents=cents, gits=gits, vg=vg, gm=gm, cfg=cfg, af=S["af"], Xt=Xt, tsrc=tsrc)


def members_index(srcs, members, what):
    bad = sorted(set(srcs) - set(members))
    if bad or set(srcs) != set(members):
        hit("REFUSE.MEMBERS")
        refuse("[DR-MEMBERS] the %s sources %s are not the registered members %s" % (what, sorted(set(srcs)), list(members)))
    pos = {m: j for j, m in enumerate(members)}
    return np.array([pos[s] for s in srcs], dtype=np.int64)


def cost_line(say, P_, c):
    """A timed estimate on GATE streams (no EVAL): seconds per stream over every arm-detector, extrapolated."""
    members = list(c["members"])
    src_g = members_index([P_["gm"][i][1] for i in P_["gits"]], members, "GATE")
    src_t = members_index(P_["tsrc"], members, "TRAIN")
    Xg = np.vstack([P_["vg"][i] for i in P_["gits"]])
    _ae, ag, info = arms_from(Xg, Xg, P_["Xt"], src_g, src_g, src_t, P_["g"], P_["cents"], members, c)
    say("  GATE-ONLY (no EVAL): source-blind tau_oos = GATE p5 of max-cos (DR-R3) per arm: %s; bins per arm %s; ESCALATION-RC's"
        " candidate-form AF-U value %s (the [DR-TAU] identity above)" % (
            ", ".join("%s %.6f" % (nm, info[nm]["tau"]) for nm in ["AF-U"] + sorted(P_["cents"])),
            ", ".join("%s %d" % (nm, info[nm]["bins"]) for nm in ["AF-U"] + sorted(P_["cents"]) + ["SRC"]), c["tau_rc"]))
    pools = [np.flatnonzero(src_g == m) for m in range(len(members))]
    pig = np.array([len(p) for p in pools], dtype=np.float64) / len(src_g)
    n = min(100, c["n_gate"])
    t0 = time.time()
    st_ = draw_streams(spawn(c["rng_gate"], n), pools, [pig] * n, [pig] * n, c)
    stats_for(st_, ag, c)
    per = (time.time() - t0) / n
    n_main = c["n_gate"] + c["n0"] + len(c["s_grid"]) * len(members) * c["R"]
    n_comp = c["B_comp"] * len(members) * c["R"] * (2 + len(KU)) / float(len(ag))
    say("COST ESTIMATE (timed on %d GATE streams over all %d arm-detectors: %.4f s per stream): main %d streams ~ %.1f min; component"
        " bootstrap %d x %d streams on %d of %d arm-detectors ~ %.1f min; bootstrap B %d (cheap); total ~ %.1f min single-threaded" % (
            n, len(ag), per, n_main, per * n_main / 60.0, c["B_comp"], len(members) * c["R"], 2 + len(KU), len(ag),
            per * n_comp / 60.0, c["B"], per * (n_main + n_comp) / 60.0))
    return per


def dry_run(out=print):
    say = out
    c = reg()
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, files())
    denominators(say)
    P_ = prepare(say, c)
    say("  eval view %s: NOT opened by --dry-run (no EVAL read; the marker is not written)" % P_["cfg"].eval_path)
    cost_line(say, P_, c)
    say("OUTPUTS (write-once, never committed): %s, %s" % (c["out"], c["marker"]))
    say("DRY-RUN: nothing written; no key column; no EVAL statistic printed.")
    hit("DRY.DONE")
    return 0


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    U.header(say, TEST_ID, "--run", REG_TEXT, files())
    for p in (c["out"], c["marker"]):
        if os.path.exists(U.P(p)):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    denominators(say)
    P_ = prepare(say, c)
    members = list(c["members"])
    V.G.read_marker(U.P(c["marker"]), "%s: the EVAL set read (structure + cached vectors; no key) started" % TEST_ID)
    hit("MARKER.WRITTEN")
    items, meta, sealed = eval_structure(P_["cfg"], say)
    comps = sorted(set(meta[i][0] for i in items))
    if (len(items), len(comps)) != (c["n_route"], c["comp_route"]):
        hit("REFUSE.DENOM")
        refuse("[DR-DENOM] the EVAL set is %d items / %d components, not the registered %d / %d" % (len(items), len(comps), c["n_route"], c["comp_route"]))
    if not sealed:
        refuse("the eval view's tripwire was unsealed: a key could have been read")
    src_e = members_index([meta[i][1] for i in items], members, "EVAL")
    src_g = members_index([P_["gm"][i][1] for i in P_["gits"]], members, "GATE")
    ve = ERC.get_vectors(items)
    nov = [i for i in items if i not in ve]
    if nov:
        hit("REFUSE.NOVEC")
        refuse("%d EVAL item(s) of the set have no vector (first %s)" % (len(nov), nov[:3]))
    nb = ERC.check_vectors_vs_bundle(ve, P_["b"])
    Xe = np.vstack([ve[i] for i in items])
    Xg = np.vstack([P_["vg"][i] for i in P_["gits"]])
    src_t = members_index(P_["tsrc"], members, "TRAIN")
    arms_e, arms_g, info = arms_from(Xe, Xg, P_["Xt"], src_e, src_g, src_t, P_["g"], P_["cents"], members, c)
    agree = sum(1 for j, it in enumerate(items) if P_["g"].af_names[info["AF-U"]["cell_e"][j]] == P_["af"].get(it))
    say("  vectors: %d EVAL items (equal to the bundle's on %d), %d GATE items" % (len(items), nb, len(P_["gits"])))
    say("  AF-U all-leaf filing (DR-R2) equals af_cells.tsv on %d of %d EVAL items" % (agree, len(items)))
    for nm in ["AF-U"] + sorted(P_["cents"]):
        x = info[nm]
        say("  ARM %-4s: %d cells -> %d bins (%d rare bins); source-blind tau_oos = GATE p5 of max-cos = %.6f (GATE TPR %.4f); EVAL OOS"
            " rate %.4f" % (nm, x["cells"], x["bins"], x["rare"], x["tau"], x["tpr"], x["oos_e"]))
    say("  ARM SRC : %d sources -> %d bins (%d rare bins)" % (info["SRC"]["cells"], info["SRC"]["bins"], info["SRC"]["rare"]))
    E = dict(src=src_e, comp=np.array([meta[i][0] for i in items], dtype=object))
    Gt = dict(src=src_g)
    st = simulate(E, Gt, arms_e, arms_g, members, c)
    t0 = time.time()
    if c["B_comp"] > 0:
        d2c, d1c = comp_boot(E, arms_e, members, st, c)
        st["comp"] = dict(B=c["B_comp"], d2=interval(st["D2"]["point"], d2c), d1=interval(st["D1"]["point"], d1c))
    else:
        st["comp"] = None
    say("  simulation %.1f s; component bootstrap %.1f s" % (st["t_sim"], time.time() - t0))
    oo = info["AF-U"]["oos_flags"]
    st.update(members=members, n_eval=len(items), n_comp=len(comps), kish=U.UCI.kish(Counter(meta[i][0] for i in items).values()),
              n_gate_items=len(P_["gits"]), bins={k: v["bins"] for k, v in info.items()}, n_ref=len(P_["Xt"]), oos_m=[float(np.mean(oo[src_e == m])) for m in range(len(members))],
              p4_delay=median_delay(st["delay"][(("AF-U", "OCC"), c["s_grid"][-1])]),
              p4_det=float(np.mean(st["det"][(("AF-U", "OCC"), c["s_grid"][0])])))
    L, words = dr_lines(st)
    for ln in L:
        say(ln)
    text = "\n".join(lines) + "\n"
    V.G.write_once(U.P(c["out"]), text)
    out("OUTCOME written write-once: %s (sha256 %s; never committed: back up to E:/TaxoArena_backup_<date>_drift_replay with"
        " SHA256SUMS.txt)" % (c["out"], __import__("hashlib").sha256(text.encode("utf-8")).hexdigest()))
    hit("RUN.DONE")
    return dict(st=st, words=words, items=items, info=info, src_e=src_e, src_g=src_g, arms_e=arms_e)


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=None, help="the checkout whose results / views / caches are read (set before any import)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=a.only)
        return 0
    if a.mutants:
        return U.run_mutants(os.path.abspath(__file__), "drift_replay", MUTANTS, TAG, only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

BRANCHES = ("DR0.CALIBRATED", "DR0.MISCALIBRATED", "DR2.OCC", "DR2.OOS", "DR2.NEITHER", "DR2.UNDETERMINED", "DR2.REFUTED",
            "DR2.NOT_REFUTED", "DR1.TREE", "DR1.KM", "DR1.NEITHER", "DR1.UNDETERMINED", "DR1.REFUTED", "DR1.NOT_REFUTED", "FDR.FIRED",
            "FDR.NOT_FIRED", "COMP.DONE", "COMP.SKIPPED", "PRED.HELD", "PRED.FAILED", "BRIER.SCORED", "BRIER.NOT_SCOREABLE", "TAU.OK",
            "MARKER.WRITTEN", "RUN.DONE", "DRY.DONE", "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.MANIFEST", "REFUSE.POLICY_SHA",
            "REFUSE.KU_K", "REFUSE.TAU", "REFUSE.DENOM", "REFUSE.MEMBERS", "REFUSE.NOVEC", "REFUSE.GATE_EMPTY")
need = U.need
NUM = r"([+-]?[0-9.]+)"


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _ready(base):
    """The fixture's ESCALATION-RC operating point (the [DR-TAU] identity): escalation_rc --run executed once on the shared layout
    (unedited code); its printed AF-U tau_oos and AF-U's total leaf count become the fixture's constants."""
    if getattr(base, "dr_ready", False):
        return base
    p = os.path.join(base.tmp, "res", "erc", "outcome.txt")
    if not os.path.isfile(p):
        _t, err, _r = ERC._cap(ERC.run, base)
        if err:
            raise AssertionError("fixture escalation_rc --run refused: %s" % err)
    tau = re.search(r"GATE THRESHOLDS AF-U .*? tau_oos = p5 of OOS = ([0-9.]+)", open(p, encoding="utf-8").read()).group(1)
    base.common = dict(base.common, tau_rc=tau, ku_k=int(sum(base.fx.ksrc.values())))
    base.dr_ready = True
    return base


# ── the independent oracle of the simulation (plain loops; numpy only for per-window bincounts and the generators) ─────────

def _o_bins(p, w, emin):
    """DR-R6 by a second, plain implementation -> (bin of each cell, bin shares)."""
    K = len(p)
    E = [w * x for x in p]
    of = [None] * K
    nb = 0
    for j in range(K):
        if E[j] >= emin:
            of[j] = nb
            nb += 1
    big = [j for j in range(K) if of[j] is not None]
    rare = sorted([j for j in range(K) if of[j] is None], key=lambda j: (p[j], j))
    groups, cur, acc = [], [], 0.0
    for j in rare:
        cur.append(j)
        acc += E[j]
        if acc >= emin:
            groups.append(cur)
            cur, acc = [], 0.0
    if cur:
        if groups:
            groups[-1] = groups[-1] + cur
        elif big:
            tgt = min(big, key=lambda j: (E[j], j))
            for j in cur:
                of[j] = of[tgt]
            cur = []
        else:
            groups.append(cur)
    for gr in groups:
        for j in gr:
            of[j] = nb
        nb += 1
    pb = [0.0] * nb
    for j in range(K):
        pb[of[j]] += p[j]
    return of, pb


def _o_streams(seed, n, pools, pi0s, pi1s, c):
    out = []
    for i, ss in enumerate(np.random.SeedSequence(seed).spawn(n)):
        g = np.random.default_rng(ss)
        u = g.random(c["L"])
        srcs = []
        for t in range(c["L"]):
            pi = pi0s[i] if t < c["change"] else pi1s[i]
            acc, s_ = 0.0, len(pools) - 1
            for m, x in enumerate(pi):
                acc += x
                if u[t] < acc:
                    s_ = m
                    break
            srcs.append(s_)
        j = g.integers(0, np.array([len(pools[s_]) for s_ in srcs]))
        out.append([pools[s_][jj] for s_, jj in zip(srcs, j)])
    return out


def _o_stats(stream, arm, c):
    ends = list(range(c["w"], c["L"] + 1, c["step"]))
    vals = []
    if "of" in arm:
        cb = np.array([arm["of"][x] for x in arm["cell"]], dtype=np.int64)
        nb = len(arm["pb"])
        for t in ends:
            O = np.bincount(cb[stream[t - c["w"]:t]], minlength=nb)
            vals.append(sum((O[b] - c["w"] * arm["pb"][b]) ** 2 / (c["w"] * arm["pb"][b]) for b in range(nb)))
    else:
        fl = np.asarray(arm["cell"], dtype=np.int64)
        sa = np.asarray(stream, dtype=np.int64)
        for t in ends:
            vals.append(float(int(fl[sa[t - c["w"]:t]].sum())))
    return ends, vals


def _o_level(mx, alpha):
    s = sorted(mx)
    allowed = int(math.floor(alpha * len(s) + 1e-9))
    for v in s:
        if sum(1 for x in s if x > v) <= allowed:
            return v
    return s[-1]


def _o_pct(xs, q):
    s = sorted(xs)
    B = len(s)
    return s[int(q * B)] if q < 0.5 else s[int(q * B) - 1]


def _o_sim(E, Gt, arms_e, arms_g, members, c):
    """Every deciding number of simulate(), by plain loops: streams, statistics, levels, FAR, DET, delays, D_det, D_arm and their
    stream-bootstrap intervals (the same rng protocol, re-drawn by loops)."""
    M = len(members)
    pools_e = [[i for i in range(len(E["src"])) if E["src"][i] == m] for m in range(M)]
    pools_g = [[i for i in range(len(Gt["src"])) if Gt["src"][i] == m] for m in range(M)]
    pi0 = [len(p) / float(len(E["src"])) for p in pools_e]
    pig = [len(p) / float(len(Gt["src"])) for p in pools_g]
    gst = _o_streams(c["rng_gate"], c["n_gate"], pools_g, [pig] * c["n_gate"], [pig] * c["n_gate"], c)
    lev = {}
    for k, a in arms_g.items():
        mx = [max(_o_stats(st_, a, c)[1]) for st_ in gst]
        lev[k] = _o_level(mx, c["alpha"])
    plan = []
    for _r in range(c["n0"]):
        plan.append((0.0, -1, pi0))
    for s in c["s_grid"]:
        for mi in range(M):
            p1 = [(1.0 - s) * x + (s if j == mi else 0.0) for j, x in enumerate(pi0)]
            for _r in range(c["R"]):
                plan.append((s, mi, p1))
    est = _o_streams(c["rng_eval"], len(plan), pools_e, [pi0] * len(plan), [p[2] for p in plan], c)
    far, det, dly = {}, {}, {}
    for k, a in arms_e.items():
        fa, dd, dl = [], {s: [] for s in c["s_grid"]}, {s: [] for s in c["s_grid"]}
        for (s, mi, _p), st_ in zip(plan, est):
            ends, vals = _o_stats(st_, a, c)
            if s == 0.0:
                fa.append(any(v > lev[k] for v in vals))
            else:
                hitt = [t for t, v in zip(ends, vals) if t > c["change"] and v > lev[k]]
                dd[s].append(bool(hitt))
                dl[s].append(hitt[0] - c["change"] if hitt else float("inf"))
        far[k] = (sum(fa), len(fa))
        det[k], dly[k] = dd, dl
    sd = c["s_dec"]
    mo = [mi for (s, mi, _p) in plan if s == sd]
    midx = [[j for j, x in enumerate(mo) if x == m] for m in range(M)]
    occ = [float(x) for x in det[("AF-U", "OCC")][sd]]
    oos = [float(x) for x in det[("AF-U", "OOS")][sd]]
    kus = [[float(x) for x in det[(nm, "OCC")][sd]] for nm in KU if (nm, "OCC") in arms_e]
    mean = lambda xs: sum(xs) / len(xs)
    rng = np.random.default_rng(c["rng_boot"])
    r2, r1 = [], []
    rpm = [[] for _ in range(M)]
    for _b in range(c["B"]):
        idx = []
        for m in range(M):
            draw = rng.integers(0, len(midx[m]), len(midx[m]))
            idx.append([midx[m][int(j)] for j in draw])
        sds = rng.integers(0, len(kus), len(kus))
        allx = [j for part in idx for j in part]
        r2.append(mean([occ[j] - oos[j] for j in allx]))
        r1.append(mean([occ[j] for j in allx]) - mean([mean([kus[int(s_)][j] for j in allx]) for s_ in sds]))
        for m in range(M):
            rpm[m].append(mean([occ[j] - oos[j] for j in idx[m]]))
    d2 = mean([a - b for a, b in zip(occ, oos)])
    d1 = mean(occ) - mean([mean(x) for x in kus])
    return dict(lev=lev, far=far, det=det, dly=dly, D2=(d2, _o_pct(r2, 0.025), _o_pct(r2, 0.975)), D1=(d1, _o_pct(r1, 0.025), _o_pct(r1, 0.975)),
                D2_m=[(mean([occ[j] - oos[j] for j in midx[m]]), _o_pct(rpm[m], 0.025), _o_pct(rpm[m], 0.975)) for m in range(M)], plan=plan,
                est=est, pools_e=pools_e)


def _syn_pop(seed=11):
    """A synthetic three-member population: member-specific cell distributions (AF-U, five KM-U maps), member-dependent OOS rates."""
    rs = np.random.RandomState(seed)
    sizes_e, sizes_g = (70, 50, 60), (45, 35, 40)
    K = 10
    home = {0: (0, 1, 2, 3), 1: (3, 4, 5, 6), 2: (6, 7, 8, 9)}
    rates = (0.30, 0.05, 0.10)

    def pop(sizes):
        src = np.concatenate([np.full(n, m) for m, n in enumerate(sizes)])
        cell = np.array([rs.choice(home[m]) if rs.rand() < 0.85 else rs.randint(K) for m in src])
        oos = np.array([int(rs.rand() < rates[m]) for m in src])
        ku = [np.array([(x + sd + (1 if rs.rand() < 0.2 else 0)) % K for x in cell]) for sd in range(5)]
        return src, cell, oos, ku
    se, ce, oe, ke = pop(sizes_e)
    sg, cg, og, kg = se.copy(), ce.copy(), oe.copy(), [x.copy() for x in ke]   # GATE = the EVAL population: transport exact
    c = dict(REG, R=12, n0=30, n_gate=120, B=200, chunk=37)
    arms_e, arms_g, o_arms_e, o_arms_g = {}, {}, {}, {}

    def add(key, cel_e, cel_g, K_):
        p = np.bincount(cel_g, minlength=K_).astype(float) / len(cel_g)
        Mb, pb, _r = make_bins(p, c["w"], c["e_min"])
        of, opb = _o_bins(list(p), c["w"], c["e_min"])
        arms_e[key], arms_g[key] = dict(cell=cel_e, M=Mb, pb=pb), dict(cell=cel_g, M=Mb, pb=pb)
        o_arms_e[key], o_arms_g[key] = dict(cell=list(cel_e), of=of, pb=opb), dict(cell=list(cel_g), of=of, pb=opb)
    add(("AF-U", "OCC"), ce, cg, K)
    arms_e[("AF-U", "OOS")], arms_g[("AF-U", "OOS")] = dict(cell=oe), dict(cell=og)
    o_arms_e[("AF-U", "OOS")], o_arms_g[("AF-U", "OOS")] = dict(cell=list(oe)), dict(cell=list(og))
    for j, nm in enumerate(KU):
        add((nm, "OCC"), ke[j], kg[j], K)
    add(("SRC", "OCC"), se, sg, 3)
    return dict(E=dict(src=se, comp=np.array(["c%03d" % (i // 2) for i in range(len(se))], dtype=object)), Gt=dict(src=sg), arms_e=arms_e,
                arms_g=arms_g, o_arms_e=o_arms_e, o_arms_g=o_arms_g, c=c, members=["A", "B", "C"])


def _cmp_sim(st, o, c, members):
    for k in o["lev"]:
        assert abs(st["levels"][k] - o["lev"][k]) < 1e-9, ("level", k, st["levels"][k], o["lev"][k])
        assert tuple(st["far"][k]) == tuple(o["far"][k]), ("far", k, st["far"][k], o["far"][k])
        for s in c["s_grid"]:
            assert st["det"][(k, s)].tolist() == o["det"][k][s], ("det", k, s)
            assert st["delay"][(k, s)].tolist() == o["dly"][k][s], ("delay", k, s)
    for nm, x in (("D2", st["D2"]), ("D1", st["D1"])):
        assert abs(x["point"] - o[nm][0]) < 1e-12 and abs(x["lo"] - o[nm][1]) < 1e-12 and abs(x["hi"] - o[nm][2]) < 1e-12, (nm, x, o[nm])
    for m in range(len(members)):
        x = st["D2_m"][m]
        assert abs(x["point"] - o["D2_m"][m][0]) < 1e-12 and abs(x["lo"] - o["D2_m"][m][1]) < 1e-12 and abs(x["hi"] - o["D2_m"][m][2]) < 1e-12


def st_sim():
    """simulate() on a planted three-member population against the plain-loop oracle, value by value (levels, FAR, DET and
    delay of every stream, D_det / D_arm and their bootstrap intervals, per-member D_det); non-degeneracy asserted."""
    P = _syn_pop()
    c = P["c"]
    saved = _REG[0]
    _REG[0] = c
    try:
        st = simulate(P["E"], P["Gt"], P["arms_e"], P["arms_g"], P["members"], c)
    finally:
        _REG[0] = saved
    o = _o_sim(P["E"], P["Gt"], P["o_arms_e"], P["o_arms_g"], P["members"], c)
    _cmp_sim(st, o, c, P["members"])
    sd = c["s_dec"]
    for k in (("AF-U", "OCC"), ("AF-U", "OOS")):
        d = float(np.mean(st["det"][(k, sd)]))
        assert 0.0 < d < 1.0, ("degenerate DET", k, d)
    fins = [x for s in c["s_grid"] for x in st["delay"][(("AF-U", "OCC"), s)].tolist() if not math.isinf(x)]
    assert len(set(fins)) > 3 and max(fins) > 200, "the delays must spread"
    assert st["far"][("AF-U", "OCC")][0] > 0 and st["far"][("AF-U", "OOS")][0] > 0, "the FARs must be positive"
    assert st["D2"]["lo"] < st["D2"]["hi"] and st["D1"]["lo"] < st["D1"]["hi"]
    # the census of the streams: the shifted share of member m after item 500 matches pi_1 in expectation (a loose check)
    est = o["est"]
    pos_src = P["E"]["src"]
    shifted = [i for i, p in enumerate(o["plan"]) if p[0] == c["s_grid"][-1] and p[1] == 0]
    share = np.mean([pos_src[x] == 0 for i in shifted for x in est[i][c["change"]:]])
    want = (1 - c["s_grid"][-1]) * (70 / 180.0) + c["s_grid"][-1]
    assert abs(share - want) < 0.04, (share, want)
    return st


def st_units():
    Mb, pb, nr = make_bins([0.5, 0.3, 0.01, 0.0, 0.02, 0.17], 200, 5.0)
    of, opb = _o_bins([0.5, 0.3, 0.01, 0.0, 0.02, 0.17], 200, 5.0)
    assert Mb.argmax(axis=1).tolist() == [0, 1, 3, 3, 3, 2] and nr == 1 and np.allclose(pb, [0.5, 0.3, 0.17, 0.03]), (Mb, pb)
    assert of == Mb.argmax(axis=1).tolist() and np.allclose(opb, pb)
    Mb, pb, nr = make_bins([0.01, 0.015, 0.02, 0.005, 0.95], 200, 5.0)       # rare: 0.005, 0.01 | 0.015 (5 -> closes) ...
    assert Mb.argmax(axis=1).tolist() == [1, 1, 1, 1, 0] and nr == 1, Mb.argmax(axis=1).tolist()
    Mb, pb, nr = make_bins([0.0125, 0.0125, 0.95, 0.025], 200, 5.0)            # the rare pair reaches exactly 5 -> it closes
    assert Mb.argmax(axis=1).tolist() == [2, 2, 0, 1] and nr == 1, Mb.argmax(axis=1).tolist()
    Mb, pb, nr = make_bins([0.005, 0.005, 0.02, 0.02, 0.02, 0.93], 200, 5.0)    # ascending pooling: {0, 1, 2}, {3, 4}
    assert Mb.argmax(axis=1).tolist() == [1, 1, 1, 2, 2, 0] and nr == 2, Mb.argmax(axis=1).tolist()
    assert _o_bins([0.005, 0.005, 0.02, 0.02, 0.02, 0.93], 200, 5.0)[0] == [1, 1, 1, 2, 2, 0]
    Mb, pb, nr = make_bins([0.99, 0.01], 200, 5.0)                            # leftover 2 < 5 with no rare bin -> the smallest big bin
    assert Mb.shape[1] == 1 and nr == 0 and np.allclose(pb, [1.0])
    Mb, pb, nr = make_bins([0.4, 0.4, 0.2], 200, 5.0)
    assert Mb.shape[1] == 3 and nr == 0
    assert level([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.2) == 8.0 and level([5, 5, 5, 5, 5, 5, 5, 5, 6, 7], 0.2) == 5.0
    assert level([3] * 10, 0.05) == 3.0 and _o_level([5, 5, 5, 5, 5, 5, 5, 5, 6, 7], 0.2) == 5
    c = dict(REG)
    rs = np.random.RandomState(2)
    cells = rs.randint(0, 4, size=(3, c["L"]))
    W = window_counts(cells, 4, c)
    ends = window_ends(c)
    assert W.shape == (3, 81, 4) and ends[0] == 200 and ends[-1] == 1000
    for i in range(3):
        for wj in (0, 7, 80):
            t = ends[wj]
            assert W[i, wj].tolist() == np.bincount(cells[i, t - 200:t], minlength=4).tolist()
    S = np.array([[0.0] * 31 + [5.0] + [0.0] * 49, [9.0] + [0.0] * 80, [2.0] * 81])
    S3 = np.zeros((1, 81))
    S3[0, 30] = 5.0
    assert first_alarm(S3, 2.0, c)[0].tolist() == [False], "an alarm at t = 500 is not a detection"
    det, d = first_alarm(S, 2.0, c)
    assert det.tolist() == [True, False, False] and d.tolist()[0] == 10.0 and math.isinf(d[1]) and math.isinf(d[2])
    assert ends[30] == 500 and ends[31] == 510
    S2 = np.zeros((1, 81))
    S2[0, 31] = 3.0
    assert first_alarm(S2, 2.0, c)[1].tolist() == [10.0]
    S2[0, 31], S2[0, 80] = 0.0, 3.0
    assert first_alarm(S2, 2.0, c)[1].tolist() == [500.0]
    assert false_alarm(S, 2.0).tolist() == [True, True, False]
    assert median_delay([10.0, float("inf"), float("inf")]) == float("inf") and median_delay([10.0, 20.0, float("inf")]) == 20.0
    assert abs(cp_upper(6, 100) - 0.12603) < 2e-5 and cp_upper(5, 5) == 1.0
    pools = [np.array([0, 2, 4]), np.array([1, 3]), np.array([5, 6, 7, 8])]
    pi0, pi1 = np.array([0.5, 0.2, 0.3]), np.array([0.1, 0.1, 0.8])
    ch = spawn(99, 4)
    got = draw_streams(ch, pools, [pi0] * 4, [pi1] * 4, c)
    want = _o_streams(99, 4, [list(p) for p in pools], [list(pi0)] * 4, [list(pi1)] * 4, c)
    assert got.tolist() == want
    assert abs(np.mean(np.isin(got[:, c["change"]:], pools[2])) - 0.8) < 0.04 and abs(np.mean(np.isin(got[:, :c["change"]], pools[0])) - 0.5) < 0.04
    a = [g_.random() for g_ in np.random.default_rng(20261005).spawn(3)]
    b = [np.random.default_rng(s_).random() for s_ in spawn(20261005, 3)]
    assert a == b, "spawn() must give default_rng(seed).spawn(n)'s children"
    plan = stream_plan(dict(c, n0=2, R=1, s_grid=(0.1, 0.4)), ["A", "B"], np.array([0.6, 0.4]))
    assert [(p[0], p[1]) for p in plan] == [(0.0, -1), (0.0, -1), (0.1, 0), (0.1, 1), (0.4, 0), (0.4, 1)]
    assert np.allclose(plan[5][2], [0.36, 0.64]) and np.allclose(plan[2][2], [0.64, 0.36])
    # arms_from: nearest cell, source-blind max-cos, tau = GATE p5 (linear), OOS iff score < tau STRICTLY (a planted tie)
    ang = np.linspace(0.05, 1.2, 21)
    Xg = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    Cg = types.SimpleNamespace(af_C=np.array([[1.0, 0.0], [0.0, 1.0]]))
    sg = np.sort((Xg @ Cg.af_C.T).max(axis=1))
    j_tie = int(np.argsort((Xg @ Cg.af_C.T).max(axis=1))[1])
    Xe = np.vstack([Xg[j_tie], [np.cos(0.7854), np.sin(0.7854)], [1.0, 0.0]])
    ae, ag, info = arms_from(Xe, Xg, Xg, np.zeros(3, dtype=np.int64), np.zeros(21, dtype=np.int64), np.zeros(21, dtype=np.int64), Cg, {},
                             ["A"], dict(REG))
    assert abs(info["AF-U"]["tau"] - sg[1]) < 1e-15, (info["AF-U"]["tau"], sg[:3])
    assert ae[("AF-U", "OOS")]["cell"].tolist() == [0, 1, 0], ae[("AF-U", "OOS")]["cell"].tolist()
    assert ae[("AF-U", "OCC")]["cell"].tolist()[2] == 0 and ag[("AF-U", "OOS")]["cell"].sum() == 1
    assert dr0_word(0.10, 0.10, 0.10) == "CALIBRATED" and dr0_word(0.1001, 0.0, 0.10) == "MISCALIBRATED" and dr0_word(0.0, 0.11, 0.10) == "MISCALIBRATED"
    assert U.UCI.pct(list(range(2000)), 0.025) == 50 and U.UCI.pct(list(range(2000)), 0.975) == 1949


def _syn_st(far=(5, 5), d2=(0.4, 0.2, 0.6), d1=(0.0, -0.03, 0.03), det_o=0.75, det_s=0.30, delay=70.0, det05=0.15, orc=0.85, comp=True):
    c = reg()
    mem = list(c["members"])
    n = len(mem) * c["R"]
    ends = {}

    def arr(p_):
        k = int(round(p_ * n))
        return np.array([True] * k + [False] * (n - k))
    det, dly = {}, {}
    keys = [("AF-U", "OCC"), ("AF-U", "OOS"), ("SRC", "OCC")] + [(nm, d_) for nm in KU for d_ in ("OCC", "OOS")]
    for k in keys:
        for s in c["s_grid"]:
            p_ = det_o if k == ("AF-U", "OCC") else det_s if k == ("AF-U", "OOS") else orc if k[0] == "SRC" else 0.5
            if k == ("AF-U", "OCC") and s == c["s_grid"][0]:
                p_ = det05
            det[(k, s)] = arr(p_)
            dly[(k, s)] = np.where(det[(k, s)], 40.0, np.inf)
    mo = np.repeat(np.arange(len(mem)), c["R"])
    iv = lambda x: dict(point=x[0], lo=x[1], hi=x[2], se=(x[2] - x[1]) / 3.92)
    st = dict(members=mem, n_eval=5907, n_comp=5404, kish=1.09, n_gate_items=2033, n_streams=c["n0"] + len(c["s_grid"]) * n,
              pi0=np.full(len(mem), 1.0 / len(mem)), pig=np.full(len(mem), 1.0 / len(mem)), levels={k: 1.0 for k in keys},
              gate_fa={k: 0.05 for k in keys}, far={k: (far[0] if k == ("AF-U", "OCC") else far[1] if k == ("AF-U", "OOS") else 3, c["n0"]) for k in keys},
              det=det, delay=dly, m_of={s: mo for s in c["s_grid"]}, D2=iv(d2), D1=iv(d1), D2_m=[iv(d2)] * len(mem), disc2=0.5, disc1=0.15,
              seed_sd=0.03, oos_m=[0.05] * len(mem), p4_delay=delay, p4_det=det05, n_ref=12334,
              bins={"AF-U": 35, "KU0": 34, "KU1": 34, "KU2": 34, "KU3": 34, "KU4": 34, "SRC": 6},
              comp=dict(B=200, d2=iv(d2), d1=iv(d1)) if comp else None)
    return st


def st_branches():
    saved = _REG[0]
    _REG[0] = REG
    try:
        n0 = REG["n0"]
        cases = [((60, 60), (0.40, 0.20, 0.60), "CALIBRATED", "OCC-BETTER"), ((60, 60), (-0.30, -0.50, -0.10), "CALIBRATED", "OOS-BETTER"),
                 ((60, 60), (0.05, -0.02, 0.12), "CALIBRATED", "NEITHER"), ((60, 60), (0.05, 0.0, 0.12), "CALIBRATED", "NEITHER"),
                 ((60, 60), (-0.05, -0.12, 0.0), "CALIBRATED", "NEITHER"), ((120, 120), (0.40, 0.20, 0.60), "CALIBRATED", "OCC-BETTER"),
                 ((121, 60), (0.40, 0.20, 0.60), "MISCALIBRATED", "UNDETERMINED"), ((60, 121), (-0.3, -0.5, -0.1), "MISCALIBRATED", "UNDETERMINED")]
        for far, d2, w0, w2 in cases:
            L, w = dr_lines(_syn_st(far=far, d2=d2))
            t = "\n".join(L)
            assert (w["DR0"], w["DR2"]) == (w0, w2), (far, d2, w)
            need(t, "  DR0 -> %s" % w0, "  DR2 -> %s" % w2, "verdict line of record: " + VERDICT, "WILL NOT SHOW (registered)",
                 "D_det = DET(OCC-CHI) 0.7500 - DET(OOS-RATE) 0.3000 = %+.4f" % d2[0], "| stream bootstrap 95%% [%+.4f, %+.4f]" % (d2[1], d2[2]),
                 "FAR on %d unshifted EVAL streams, AF-U OCC-CHI %.4f (%d;" % (n0, far[0] / float(n0), far[0]))
            fire = w0 == "CALIBRATED" and w2 in ("NEITHER", "OOS-BETTER")
            assert w["F_DR"] is fire
            if fire:
                need(t, "FALSIFIER F-DR: FIRED (DR0 CALIBRATED and DR2 %s)" % w2)
            else:
                need(t, "FALSIFIER F-DR: NOT FIRED (DR0 %s, DR2 %s; F-DR fires iff DR0 CALIBRATED and DR2 NEITHER or OOS-BETTER)" % (w0, w2))
            need(t, "rule 8: OCC-BETTER is %s (lower bound %+.4f %s 0)" % (("refuted", d2[1], "<=") if d2[1] <= 0 else ("not refuted", d2[1], ">")))
            if w0 == "MISCALIBRATED":
                need(t, "DR0 -> MISCALIBRATED: the GATE-to-EVAL transport of the alarm level FAILS", "realised FAR OCC",
                     "observed UNDETERMINED (DR0 MISCALIBRATED); Brier NOT SCOREABLE")
                assert "PREDICTION P2 DR2 OCC-BETTER 0.85, NEITHER 0.12, OOS-BETTER 0.03: observed UNDETERMINED (DR0 MISCALIBRATED); Brier NOT SCOREABLE" in t
            else:
                need(t, "PREDICTION P2 DR2 OCC-BETTER 0.85, NEITHER 0.12, OOS-BETTER 0.03: observed %s; Brier %.4f" % (
                    w2, {"OCC-BETTER": 0.0378, "NEITHER": 1.4978, "OOS-BETTER": 1.6778}[w2]))
            need(t, "PREDICTION P1 DR0 CALIBRATED 0.80: observed %s; Brier %.4f" % (w0, {"CALIBRATED": 0.08, "MISCALIBRATED": 1.28}[w0]))
        for d1, w1 in (((0.08, 0.02, 0.14), "TREE-BETTER"), ((-0.08, -0.14, -0.02), "KM-BETTER"), ((0.0, -0.03, 0.03), "NEITHER"),
                       ((0.03, 0.0, 0.06), "NEITHER"), ((-0.03, -0.06, 0.0), "NEITHER"), ((0.03, 1e-12, 0.06), "TREE-BETTER")):
            L, w = dr_lines(_syn_st(d1=d1))
            t = "\n".join(L)
            assert w["DR1"] == w1, (d1, w)
            need(t, "  DR1 -> %s" % w1, "= %+.4f, stream-paired, seeds crossed | 95%% [%+.4f, %+.4f]" % d1,
                 "PREDICTION P3 DR1 NEITHER 0.70, TREE-BETTER 0.20, KM-BETTER 0.10: observed %s; Brier %.4f" % (
                     w1, {"NEITHER": 0.14, "TREE-BETTER": 1.14, "KM-BETTER": 1.34}[w1]),
                 "rule 8: TREE-BETTER is %s" % ("refuted" if d1[1] <= 0 else "not refuted"))
            if w1 == "KM-BETTER":
                need(t, "narrows to 'cells of any kind', not the tree")
        tf = "\n".join(dr_lines(_syn_st(far=(60, 60), d2=(0.05, -0.02, 0.12)))[0])
        need(tf, "in-scope source-mix shifts are caught as well by the GATE-calibrated OOS rate as by pooled occupancy")
        L, w = dr_lines(_syn_st(far=(121, 0), d1=(0.08, 0.02, 0.14)))
        assert w["DR1"] == "UNDETERMINED" and w["F_DR"] is False
        t = "\n".join(L)
        need(t, "  DR1 -> UNDETERMINED (DR0 MISCALIBRATED)", "PREDICTION P3 DR1 NEITHER 0.70, TREE-BETTER 0.20, KM-BETTER 0.10: observed UNDETERMINED")
        for kw, lab, fmt, lo, hi in (("det_o", "P2 DET(OCC-CHI) at s 0.20 0.75 [0.50, 0.95]", "%.4f", 0.50, 0.95),
                                     ("det_s", "P2 DET(OOS-RATE) at s 0.20 0.30 [0.10, 0.55]", "%.4f", 0.10, 0.55)):
            n = len(REG["members"]) * REG["R"]
            for x, want in ((lo, "HELD"), (hi, "HELD"), (lo - 1.0 / n, "FAILED"), (hi + 1.0 / n, "FAILED")):
                t = "\n".join(dr_lines(_syn_st(**{kw: x}))[0])
                need(t, "PREDICTION %s: observed %s -> %s" % (lab, fmt % (round(x * n) / n), want))
        for d2v, want in ((0.20, "HELD"), (0.75, "HELD"), (0.1999, "FAILED"), (0.7501, "FAILED")):
            need("\n".join(dr_lines(_syn_st(d2=(d2v, d2v - 0.1, d2v + 0.1)))[0]), "PREDICTION P2 D_det +0.45 [+0.20, +0.75]: observed %+.4f -> %s" % (d2v, want))
        for d1v, want in ((-0.05, "HELD"), (0.05, "HELD"), (-0.0501, "FAILED"), (0.0501, "FAILED")):
            need("\n".join(dr_lines(_syn_st(d1=(d1v, d1v - 0.1, d1v + 0.1)))[0]), "PREDICTION P3 D_arm 0.00 [-0.05, +0.05]: observed %+.4f -> %s" % (d1v, want))
        for dl, want in ((30.0, "HELD"), (150.0, "HELD"), (29.9, "FAILED"), (150.1, "FAILED"), (float("inf"), "FAILED")):
            need("\n".join(dr_lines(_syn_st(delay=dl))[0]), "PREDICTION P4 AF-U OCC-CHI median delay at s 0.40 70 [30, 150] (descriptive): observed %s -> %s" % (
                "censored" if math.isinf(dl) else "%.1f" % dl, want))
        for x, want in ((0.05, "HELD"), (0.30, "HELD"), (0.0499, "FAILED"), (0.3001, "FAILED")):
            need("\n".join(dr_lines(_syn_st(det05=x))[0]), "PREDICTION P4 AF-U OCC-CHI DET at s 0.05 0.15 [0.05, 0.30] (descriptive): observed %.4f -> %s" % (x, want))
        n = len(REG["members"]) * REG["R"]
        for orc, want in ((0.75, "HELD"), (0.75 + 0.30, "FAILED"), (0.75 - 1.0 / n, "FAILED")):
            t = "\n".join(dr_lines(_syn_st(orc=min(orc, 1.0)))[0])
            o_ = round(min(orc, 1.0) * n) / n
            need(t, "PREDICTION P5 source oracle minus AF-U OCC-CHI DET at s 0.20 +0.10 [0.00, +0.30] (descriptive): observed %+.4f -> %s" % (
                o_ - 0.75, "HELD" if 0.0 <= round(o_ - 0.75, 12) <= 0.30 else "FAILED"))
        t = "\n".join(dr_lines(_syn_st(comp=False))[0])
        need(t, "COMPONENT BOOTSTRAP: not run (B_comp 0)")
        t = "\n".join(dr_lines(_syn_st())[0])
        need(t, "OCC-CHI READS POOLED OCCUPANCY (M-1): Pearson X^2 of the window's counts in the 35-bin POOLED occupancy of AF-U (KM-U"
             " 34/34/34/34/34; SRC 6 bins)", "never 'cell occupancy'", "Reference = the bundle's 12334 TRAIN rows (B-1 fix (a))")
        assert "cell occupancy;" not in t and " by cell occupancy" not in t
        need(t, "COMPONENT BOOTSTRAP at s 0.20", "SOURCE ORACLE (ceiling, descriptive)", "per-member DR2 (descriptive; the same draws): BBH",
             "DET(s) AND MEDIAN DELAY", "SUPPORT AS REALISED: (a) DR2 / DR1 on 1200 shifted streams at s 0.20, DR0 on 1200 unshifted")
    finally:
        _REG[0] = saved


def st_b1_exch():
    """B-1 (READY_drift_escalation ec880315): TRAIN (12,334), GATE (2,033) and EVAL (5,907) cell populations drawn multinomially from
    ONE skewed 60-cell occupancy (one-hot vectors: nearest cell exact). Through arms_from + simulate (the deciding code), the s = 0
    EVAL FAR of AF-U OCC-CHI must be <= 0.10 with the bundle-TRAIN reference (fix (a)); the old self-calibration (reference from the
    same GATE items as the level, i.e. Xt := Xg) must give > 0.10 here, so the case discriminates."""
    rs = np.random.RandomState(20261005)
    K = 60
    q = 1.0 / (np.arange(K) + 1.0) ** 1.1
    q /= q.sum()
    eye = np.eye(K)

    def pop(n):
        cell = rs.choice(K, size=n, p=q)
        return eye[cell], rs.randint(0, 2, n)
    Xt, st_ = pop(12334)
    Xg, sg = pop(2033)
    Xe, se = pop(5907)
    G = types.SimpleNamespace(af_C=eye)
    c = dict(REG, members=("A", "B"), n0=300, n_gate=400, R=2, s_grid=(0.2,), s_dec=0.2, B=20, chunk=100)
    far = {}
    for lab, ref, rsrc in (("new", Xt, st_), ("old", Xg, sg)):
        ae, ag, info = arms_from(Xe, Xg, ref, se, sg, rsrc, G, {"KU0": eye}, ["A", "B"], c)
        want = np.bincount(rsrc, minlength=2) / float(len(rsrc))
        assert np.allclose(ae[("SRC", "OCC")]["pb"], want, atol=1e-15) and np.allclose(ag[("SRC", "OCC")]["pb"], want, atol=1e-15), (lab, "SRC reference")
        assert not np.allclose(np.bincount(st_, minlength=2) / 12334.0, np.bincount(sg, minlength=2) / 2033.0, atol=1e-6)
        st = simulate(dict(src=se), dict(src=sg), ae, ag, ["A", "B"], c)
        k_, n_ = st["far"][("AF-U", "OCC")]
        far[lab] = k_ / float(n_)
    assert far["new"] <= 0.10, ("B-1: EVAL FAR with the TRAIN reference", far)
    assert far["old"] > 0.10, ("the old GATE self-reference must miscalibrate here (non-vacuous)", far)
    return far


def _o_fixture(lay, res):
    """The data path by plain loops: cells, taus, reference occupancy and bins per arm (AF-U from the prototypes + the one-cell
    TRAIN mean, KM-U by direct spherical k-means calls), the declared sources from the fixture spec."""
    c = reg()
    fx = lay.fx
    import json
    man = json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    z = np.load(os.path.join(lay.tmp, "res", "inputs", "af_u_bundle_256.npz"))
    titems = [str(x) for x in z["train_item"]]
    sc_ = sorted(v for v in set(af.values()) if v.startswith(fx.single + ":"))[0]
    acc = np.zeros(UAR.FX_DIM)
    for j, it in enumerate(titems):
        if af.get(it) == sc_:
            acc += z["train_X"][j] / np.linalg.norm(z["train_X"][j])
    cents = {"AF-U": [lay.proto[lf] for lf in lay.graft] + [acc / np.linalg.norm(acc)]}
    Xt = np.asarray(z["train_X"], float)
    Xt = Xt / np.linalg.norm(Xt, axis=1, keepdims=True)
    L = int(sum(fx.ksrc.values()))
    for s in (0, 1, 2, 3, 4):
        C = GC.FM.spherical_kmeans(Xt, L, s, max_iter=300)["centers"]
        cents["KU%d" % s] = [C[j] / np.linalg.norm(C[j]) for j in range(L)]
    vm = os.path.join(lay.tmp, "res", "inputs", "validation_merged")
    gits = sorted(row["item_id"] for row in ERC._o_csv(os.path.join(vm, "MAIN_union_routing_queries.csv")) if fx.side[row["item_id"]][1] == "GATE")
    srcm = {it["id"]: it["src"] for it in fx.spec["items"]}
    mem = list(c["members"])
    items = res["items"]
    src_e = [mem.index(srcm[i]) for i in items]
    src_g = [mem.index(srcm[i]) for i in gits]
    o_e, o_g = {}, {}
    info = {}
    for nm, C in sorted(cents.items()):
        def score(it):
            sims = [float(np.dot(fx.vec[it], v)) for v in C]
            b = max(range(len(sims)), key=lambda j: (sims[j], -j))
            return b, sims[b]
        se_ = [score(i) for i in items]
        sg_ = [score(i) for i in gits]
        tau = ERC._o_pct([x[1] for x in sg_], 5.0)
        tcell = [max(range(len(C)), key=lambda j: (float(np.dot(x, C[j])), -j)) for x in Xt]
        p = [tcell.count(j) / float(len(tcell)) for j in range(len(C))]
        of, pb = _o_bins(p, c["w"], c["e_min"])
        o_e[(nm, "OCC")] = dict(cell=[x[0] for x in se_], of=of, pb=pb)
        o_g[(nm, "OCC")] = dict(cell=[x[0] for x in sg_], of=of, pb=pb)
        o_e[(nm, "OOS")] = dict(cell=[int(x[1] < tau) for x in se_])
        o_g[(nm, "OOS")] = dict(cell=[int(x[1] < tau) for x in sg_])
        info[nm] = dict(tau=tau, oos_e=sum(int(x[1] < tau) for x in se_) / float(len(items)))
    alias = {"MMLU_PRO_LB": "MMLU_PRO"}
    tsrc = [mem.index(alias.get(str(z["classes"][int(y)]).split("/")[0], str(z["classes"][int(y)]).split("/")[0])) for y in z["train_y"]]
    p = [tsrc.count(m) / float(len(tsrc)) for m in range(len(mem))]
    of, pb = _o_bins(p, c["w"], c["e_min"])
    o_e[("SRC", "OCC")] = dict(cell=src_e, of=of, pb=pb)
    o_g[("SRC", "OCC")] = dict(cell=src_g, of=of, pb=pb)
    compm = {it["id"]: it["comp"] for it in fx.spec["items"]}
    return dict(o_e=o_e, o_g=o_g, info=info, src_e=np.array(src_e), src_g=np.array(src_g), gits=gits, comp=[compm[i] for i in items])


def _e2e_one(base, mk, **over):
    lay = U.clone(base, mk())
    text, err, res = U.cap(_me(), run, lay, **over)
    assert err is None, err
    outp = os.path.join(lay.tmp, *FIXTURE_REG["out"].split("/"))
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (DRIFT-REPLAY; --run" % U.POOL)
    with U.mine(_me(), lay, **over):
        c = reg()
        assert len(res["items"]) == lay.common["n_route"]
        of = _o_fixture(lay, res)
        for nm in ["AF-U"] + list(KU):
            tau, = U.num(out, r"ARM %-4s: .*?source-blind tau_oos = GATE p5 of max-cos = ([0-9.]+)" % re.escape(nm))
            assert abs(tau - of["info"][nm]["tau"]) < 6e-7, (nm, tau, of["info"][nm]["tau"])
            oe, = U.num(out, r"ARM %-4s: .*?EVAL OOS rate ([0-9.]+)" % re.escape(nm))
            assert abs(oe - of["info"][nm]["oos_e"]) < 6e-5, (nm, oe, of["info"][nm])
        o = _o_sim(dict(src=of["src_e"]), dict(src=of["src_g"]), of["o_e"], of["o_g"], list(c["members"]), c)
        _cmp_sim(res["st"], o, c, list(c["members"]))
        far = o["far"][("AF-U", "OCC")]
        fo, = U.num(out, r"FAR on \d+ unshifted EVAL streams, AF-U OCC-CHI ([0-9.]+)")
        assert abs(fo - far[0] / float(far[1])) < 6e-5
        d2 = o["D2"]
        got = U.num(out, r"= %s, stream-paired, pooled over the \d+ members \| stream bootstrap 95%% \[%s, %s\]" % (NUM, NUM, NUM))
        assert all(abs(a_ - b_) < 6e-5 for a_, b_ in zip(got, d2)), (got, d2)
        got1 = U.num(out, r"= %s, stream-paired, seeds crossed \| 95%% \[%s, %s\]" % (NUM, NUM, NUM))
        assert all(abs(a_ - b_) < 6e-5 for a_, b_ in zip(got1, o["D1"])), (got1, o["D1"])
        fo_s = o["far"][("AF-U", "OOS")]
        cal = far[0] / float(far[1]) <= c["far_max"] and fo_s[0] / float(fo_s[1]) <= c["far_max"]
        w0 = "CALIBRATED" if cal else "MISCALIBRATED"
        w2 = "UNDETERMINED" if not cal else "OCC-BETTER" if got[1] > 0 else "OOS-BETTER" if got[2] < 0 else "NEITHER"
        w1 = "UNDETERMINED" if not cal else "TREE-BETTER" if got1[1] > 0 else "KM-BETTER" if got1[2] < 0 else "NEITHER"
        need(out, "  DR0 -> %s" % w0, "  DR2 -> %s" % w2, "  DR1 -> %s" % w1,
             "FALSIFIER F-DR: %s" % ("FIRED" if (cal and w2 in ("NEITHER", "OOS-BETTER")) else "NOT FIRED"), "[DR-TAU]", "tripwire sealed True")
        sd_, n_ = c["s_dec"], len(c["members"]) * c["R"]
        mean = lambda xs: sum(xs) / float(len(xs))
        fs_ = o["far"][("AF-U", "OOS")]
        dl = sorted(o["dly"][("AF-U", "OCC")][c["s_grid"][-1]])
        med = dl[len(dl) // 2] if len(dl) % 2 else (dl[len(dl) // 2 - 1] + dl[len(dl) // 2]) / 2.0
        exp_ = [("P1 FAR AF-U OCC-CHI 0.06 [0.03, 0.10]", "%.4f" % (far[0] / float(far[1]))), ("P1 FAR AF-U OOS-RATE 0.06 [0.03, 0.10]", "%.4f" % (fs_[0] / float(fs_[1]))),
                ("P2 DET(OCC-CHI) at s 0.20 0.75 [0.50, 0.95]", "%.4f" % mean(o["det"][("AF-U", "OCC")][sd_])),
                ("P2 DET(OOS-RATE) at s 0.20 0.30 [0.10, 0.55]", "%.4f" % mean(o["det"][("AF-U", "OOS")][sd_])),
                ("P2 D_det +0.45 [+0.20, +0.75]", "%+.4f" % o["D2"][0]), ("P3 D_arm 0.00 [-0.05, +0.05]", "%+.4f" % o["D1"][0]),
                ("P4 AF-U OCC-CHI median delay at s 0.40 70 [30, 150] (descriptive)", "censored" if math.isinf(med) else "%.1f" % med),
                ("P4 AF-U OCC-CHI DET at s 0.05 0.15 [0.05, 0.30] (descriptive)", "%.4f" % mean(o["det"][("AF-U", "OCC")][c["s_grid"][0]])),
                ("P5 source oracle minus AF-U OCC-CHI DET at s 0.20 +0.10 [0.00, +0.30] (descriptive)",
                 "%+.4f" % (mean(o["det"][("SRC", "OCC")][sd_]) - mean(o["det"][("AF-U", "OCC")][sd_])))]
        for lab, val in exp_:
            need(out, "PREDICTION %s: observed %s -> " % (lab, val))
        assert n_ == len(o["det"][("AF-U", "OCC")][sd_])
        if c["B_comp"] > 0:
            d2c, d1c = _o_comp(of, o, c)
            gc = U.num(out, r"COMPONENT BOOTSTRAP at s [0-9.]+ .*?: D_det 95%% \[%s, %s\] \(SD ([0-9.]+)\); D_arm 95%% \[%s, %s\]" % (NUM, NUM, NUM, NUM))
            assert abs(gc[0] - _o_pct(d2c, 0.025)) < 6e-5 and abs(gc[1] - _o_pct(d2c, 0.975)) < 6e-5 and abs(gc[3] - _o_pct(d1c, 0.025)) < 6e-5, (gc, d2c, d1c)
            assert len(set(d2c)) > 1, "the component bootstrap must move D_det"
    _t2, err2, _r = U.cap(_me(), run, lay, **over)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out
    return out, res, o


def _o_comp(of, o, c):
    """DR-R10 by plain loops (the same rng protocol): components resampled within member, the s_dec streams re-drawn from the
    same children on the resampled population."""
    M = len(c["members"])
    rng = np.random.default_rng(c["rng_comp"])
    E_src = list(of["src_e"])
    comp = list(of["comp"])
    by_m = []
    for m in range(M):
        cm = sorted(set(comp[i] for i in range(len(comp)) if E_src[i] == m))
        by_m.append([[i for i in range(len(comp)) if comp[i] == x and E_src[i] == m] for x in cm])
    sel = [i for i, p in enumerate(o["plan"]) if p[0] == c["s_dec"]]
    allch = np.random.SeedSequence(c["rng_eval"]).spawn(len(o["plan"]))
    ch = [allch[i] for i in sel]
    mi = [o["plan"][i][1] for i in sel]
    keys = [("AF-U", "OCC"), ("AF-U", "OOS")] + [(nm, "OCC") for nm in KU]
    d2, d1 = [], []
    for _b in range(c["B_comp"]):
        pools = []
        for m in range(M):
            dr = rng.integers(0, len(by_m[m]), len(by_m[m]))
            pools.append([i for j in dr for i in by_m[m][int(j)]])
        tot = float(sum(len(p) for p in pools))
        pi0 = [len(p) / tot for p in pools]
        dd = {k: [] for k in keys}
        for ss, m_ in zip(ch, mi):
            p1 = [(1 - c["s_dec"]) * x + (c["s_dec"] if j == m_ else 0.0) for j, x in enumerate(pi0)]
            g = np.random.default_rng(ss)
            u = g.random(c["L"])
            srcs = []
            for t in range(c["L"]):
                pi = pi0 if t < c["change"] else p1
                acc, s_ = 0.0, M - 1
                for mm, x in enumerate(pi):
                    acc += x
                    if u[t] < acc:
                        s_ = mm
                        break
                srcs.append(s_)
            jj = g.integers(0, np.array([len(pools[s_]) for s_ in srcs]))
            stream = [pools[s_][j] for s_, j in zip(srcs, jj)]
            for k in keys:
                ends, vals = _o_stats(stream, of["o_e"][k], c)
                dd[k].append(float(any(t > c["change"] and v > o["lev"][k] for t, v in zip(ends, vals))))
        mean = lambda xs: sum(xs) / len(xs)
        d2.append(mean([a - b for a, b in zip(dd[keys[0]], dd[keys[1]])]))
        d1.append(mean(dd[keys[0]]) - mean([mean(dd[k]) for k in keys[2:]]))
    return d2, d1


def st_run_e2e(base, mk):
    """--run end to end twice on the fixture: the registered bar (DR0 MISCALIBRATED on the fixture's 80-item GATE: DR2 / DR1
    UNDETERMINED) and far_max 1.0 (DR0 CALIBRATED: DR2 / DR1 words from the printed intervals), every number against the oracle."""
    base = _ready(base)
    out1, res1, o1 = _e2e_one(base, mk, far_max=-1.0)
    assert res1["words"]["DR0"] == "MISCALIBRATED" and res1["words"]["DR2"] == "UNDETERMINED"
    need(out1, "REFERENCE OCCUPANCY (DR-R6, B-1 fix (a)): the bundle's", "OCC-CHI READS POOLED OCCUPANCY (M-1)")
    out2, res2, o2 = _e2e_one(base, mk, far_max=1.0)
    assert res2["words"]["DR0"] == "CALIBRATED" and res2["words"]["DR2"] != "UNDETERMINED"
    st = res2["st"]
    sd = REG["s_dec"]
    d_ = float(np.mean(st["det"][(("AF-U", "OCC"), sd)]))
    assert 0.0 < d_ < 1.0, "the fixture's AF-U OCC-CHI DET at s_dec must be interior (%r)" % d_


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, *FIXTURE_REG["out"].split("/"))), "an outcome was written by a refusal"


def _mk_path(lay):
    return os.path.join(lay.tmp, *FIXTURE_REG["marker"].split("/"))


def st_refusals(base, mk):
    import io
    import contextlib
    base = _ready(base)
    lay = U.clone(base, mk())
    saved = UAR._POOL[0]
    buf = io.StringIO()
    with U.mine(_me(), lay):
        UAR._POOL[0] = lambda pool: (1, "stub failure")
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    run(out=lambda s: print(s))
                    err = None
                except SystemExit as e:
                    err = str(e)
        finally:
            UAR._POOL[0] = saved
    assert err and "B0-2 pool check failed" in err and buf.getvalue().splitlines()[0].startswith("POOL "), err
    _no_outcome(lay)
    for over, msg in ((dict(manifest_sha="0" * 64), "inputs manifest"), (dict(uar_policy_sha="0" * 64), "not the registered"),
                      (dict(ku_k=lay.common["ku_k"] + 1), "matched k"), (dict(tau_rc="0.999999"), "[DR-TAU]")):
        _t, err, _r = U.cap(_me(), run, lay, **over)
        assert err and msg in err, (over, err)
        _no_outcome(lay)
        assert not os.path.exists(_mk_path(lay)), "a pre-read refusal wrote the marker"
    real_gi = ERC.gate_items
    ERC.gate_items = lambda rows_h, side: ([], {}, {})
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        ERC.gate_items = real_gi
    assert err and "no GATE item" in err, err
    _no_outcome(lay)
    _t, err, _r = U.cap(_me(), run, lay, n_route=lay.common["n_route"] + 1)
    assert err and "[DR-DENOM]" in err, err
    _no_outcome(lay)
    assert os.path.exists(_mk_path(lay))
    os.remove(_mk_path(lay))
    _t, err, _r = U.cap(_me(), run, lay, members=("BBH", "GPQA", "MATH", "MMLU_PRO"))
    assert err and "[DR-MEMBERS]" in err, err
    _no_outcome(lay)
    os.remove(_mk_path(lay))
    real_gv = ERC.get_vectors
    victim = {}

    def drop(ids):
        v_ = real_gv(ids)
        ev = [i for i in ids if lay.fx.side.get(i, (None, None))[1] == "EVAL"]
        if ev:
            victim["id"] = ev[0]
            v_.pop(ev[0], None)
        return v_
    ERC.get_vectors = drop
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        ERC.get_vectors = real_gv
    assert err and "have no vector" in err and victim, err
    _no_outcome(lay)
    os.remove(_mk_path(lay))
    open(_mk_path(lay), "w").close()
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_dry_run(base, mk):
    base = _ready(base)
    lay = U.clone(base, mk())
    text, err, _r = U.cap(_me(), dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (DRIFT-REPLAY; --dry-run" % U.POOL), ls[0]
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key column", "[DR-TAU] ESCALATION-RC's candidate-form AF-U tau_oos",
         "COST ESTIMATE (timed on", "KM-U (DR-R2): ukm_fit k %d" % lay.common["ku_k"], "GATE-ONLY (no EVAL): source-blind tau_oos")
    for bad in ("DR0 (", "DR2 (", "DR1 (", "PREDICTION", "EVAL SET (DR-R1", "FAR on"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "drift")), "the dry-run wrote under res/drift"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (DRIFT-REPLAY; --dry-run"), L[0]
    need(t, "6 members x 200 = 1200 shifted streams at s 0.20", "DR0 1200 unshifted streams", "EVAL 5907 items / 5404 components",
         "DEFF 1.5", "n_eff 800", "SE DR2 0.0250, DR1 0.0192, DR0 0.0077", "MDE80 DR2 0.070, DR1 0.054, DR0 0.019", VERDICT,
         "streams of 1000 items, change after item 500", "s in {0.05, 0.10, 0.20, 0.40}", "R 200 per (s, member)", "2000 GATE streams",
         "w 200 every 10 items", "bins expecting >= 5", "alarm level at GATE FA 0.05", "FAR bar 0.10", "default_rng(20261005)",
         "default_rng(20261006)", "default_rng(20261007) B 2000", "default_rng(20261008) B 200", "KM-U k 123 seeds 0-4", "tau identity 0.540800",
         "MEMBERS (registered order): BBH, GPQA, IFEVAL, MATH, MMLU_PRO, MUSR", "L24639-L24651", "calls 0")
    assert REG["out"] == "experiment_results/archv2/drift_replay/outcome.txt"


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "DR0 / DR2 / DR1 words by value incl. ends at 0 and the bar, MISCALIBRATED -> UNDETERMINED, F-DR, rule 8,"
                      " P1-P5 bands inclusive, Brier / NOT SCOREABLE, required lines", "plain"),
         ("units", "bins (leftover, zero share), level (ties), windows vs bincount, first alarm after 500 / censoring, FAR, median,"
                   " CP, stream draws vs a plain loop, spawn, plan, percentile rule", "plain"),
         ("sim", "simulate() on a planted population vs the plain-loop oracle: levels, FAR, DET and delay per stream, D_det / D_arm"
                 " and intervals, per member", "plain"),
         ("b1_exch", "B-1: GATE / EVAL / TRAIN drawn from one occupancy; EVAL FAR <= 0.10 with the TRAIN reference (fix (a)) and > 0.10"
                     " with the old GATE self-reference (discriminator)", "plain"),
         ("run_e2e", "--run end to end with DR0 forced MISCALIBRATED (far_max -1) and CALIBRATED (far_max 1): taus, OOS rates,"
                     " every stream number, intervals, component bootstrap vs the oracle; words by hand; write-once", "base"),
         ("refusals", "pool, manifest, policy sha, KU k, DR-TAU, GATE empty, DENOM, MEMBERS, missing vector, marker; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, no EVAL read, nothing written, COST ESTIMATE; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "units": st_units, "sim": st_sim, "b1_exch": st_b1_exch, "run_e2e": st_run_e2e, "refusals": st_refusals, "dry_run": st_dry_run,
       "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    return U.run_selftest(TAG, CASES, _FN, HIT, only=only, quiet=quiet, base=base)


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "S", "", ""),
    ("X01 DR0 at FAR < bar (boundary)", "S", "(far_occ <= far_max and far_oos <= far_max)", "(far_occ < far_max and far_oos < far_max)"),
    ("X02 DR0 on OCC-CHI only", "S", "(far_occ <= far_max and far_oos <= far_max)", "(far_occ <= far_max)"),
    ("X03 DR2 OCC-BETTER at lo >= 0", "S", '    if st["lo"] > 0:' + NL + '        return "OCC-BETTER"', '    if st["lo"] >= 0:' + NL + '        return "OCC-BETTER"'),
    ("X04 DR2 OOS-BETTER at hi <= 0", "S", '    if st["hi"] < 0:' + NL + '        return "OOS-BETTER"', '    if st["hi"] <= 0:' + NL + '        return "OOS-BETTER"'),
    ("X05 DR1 TREE-BETTER at lo >= 0", "S", '    if st["lo"] > 0:' + NL + '        return "TREE-BETTER"', '    if st["lo"] >= 0:' + NL + '        return "TREE-BETTER"'),
    ("X06 DR1 KM-BETTER at hi <= 0", "S", '    if st["hi"] < 0:' + NL + '        return "KM-BETTER"', '    if st["hi"] <= 0:' + NL + '        return "KM-BETTER"'),
    ("X07 DR2 read despite MISCALIBRATED", "S", "def dr2_word(st, calibrated):" + NL + "    if not calibrated:", "def dr2_word(st, calibrated):" + NL + "    if False:"),
    ("X08 DR1 read despite MISCALIBRATED", "S", "def dr1_word(st, calibrated):" + NL + "    if not calibrated:", "def dr1_word(st, calibrated):" + NL + "    if False:"),
    ("X09 F-DR fires without DR0", "S", 'fire = cal and v2 in ("NEITHER", "OOS-BETTER")', 'fire = v2 in ("NEITHER", "OOS-BETTER", "UNDETERMINED")'),
    ("X10 F-DR without the OOS-BETTER branch", "S", 'fire = cal and v2 in ("NEITHER", "OOS-BETTER")', 'fire = cal and v2 == "NEITHER"'),
    ("X11 detection alarm at >= h", "S", "    A = S[:, post] > h", "    A = S[:, post] >= h"),
    ("X12 false alarm at >= h", "S", "    return (S > h).any(axis=1)", "    return (S >= h).any(axis=1)"),
    ("X13 alarm level one order statistic lower", "S", "    return float(s[n - k - 1])", "    return float(s[n - k - 2])"),
    ("X14 GATE streams drawn from EVAL (wrong split side)", "S", 'gs = draw_streams(gch, pools_g, [pig] * c["n_gate"], [pig] * c["n_gate"], c)',
     'gs = draw_streams(gch, pools_e, [pi0] * c["n_gate"], [pi0] * c["n_gate"], c)'),
    ("X15 reference occupancy from EVAL (wrong split side)", "S", "        p = np.bincount(ct, minlength=len(C)).astype(np.float64) / len(ct)",
     "        p = np.bincount(ce, minlength=len(C)).astype(np.float64) / len(ce)"),
    ("X57 reference occupancy from GATE (the old self-calibration, B-1)", "S", "        p = np.bincount(ct, minlength=len(C)).astype(np.float64) / len(ct)",
     "        p = np.bincount(cg, minlength=len(C)).astype(np.float64) / len(cg)"),
    ("X58 reference = the TRAIN rows filed to the first cell only", "S", "        ct, _ot = nearest(Xt, C)", "        ct, _ot = np.zeros(len(Xt), dtype=np.int64), None"),
    ("X59 OCC-CHI words back to 'cell occupancy' (M-1)", "S", "rate as by pooled occupancy; the cell layer", "rate as by cell occupancy; the cell layer"),
    ("X60 pooled-occupancy line dropped (M-1)", "S", '    say("OCC-CHI READS POOLED OCCUPANCY (M-1)', '    (lambda *a: None)("OCC-CHI READS POOLED OCCUPANCY (M-1)'),
    ("X16 tau from EVAL (wrong split side)", "S", "        tau = float(np.percentile(og, 5.0))", "        tau = float(np.percentile(oe, 5.0))"),
    ("X17 EVAL OOS flag non-strict", "S", '        arms_e[(nm, "OOS")] = dict(cell=(oe < tau).astype(np.int64))', '        arms_e[(nm, "OOS")] = dict(cell=(oe <= tau).astype(np.int64))'),
    ("X18 an alarm at t = 500 counts as a detection", "S", '    post = ends > c["change"]', '    post = ends >= c["change"]'),
    ("X19 delay not relative to the change", "S", 'ends[post][j] - c["change"]', 'ends[post][j]'),
    ("X20 window of w / 2", "S", "    return cs[:, ends] - cs[:, ends - w // step]", "    return cs[:, ends] - cs[:, ends - w // step // 2]"),
    ("X21 rare cells pooled in descending share", "S", "key=lambda j: (p[j], j))" + NL + "    rb, cur", "key=lambda j: (-p[j], j))" + NL + "    rb, cur"),
    ("X22 rare bin closes only above 5", "S", "        if acc >= emin:" + NL + "            rb.append(cur)", "        if acc > emin:" + NL + "            rb.append(cur)"),
    ("X23 leftover tail becomes its own bin", "S", "            rb[-1].extend(cur)", "            rb.append(cur)"),
    ("X24 Neyman chi-square (O in the denominator)", "S", "    return (((O - E) ** 2) / E).sum(axis=-1)", "    return (((O - E) ** 2) / np.maximum(O, 1)).sum(axis=-1)"),
    ("X25 false alarms read on the second half only (first-site-only)", "S", "    return (S > h).any(axis=1)", "    return (S[:, S.shape[1] // 2:] > h).any(axis=1)"),
    ("X26 shifted mix also before the change", "S", 'src[:ch] = np.searchsorted(np.cumsum(pi0[i]), u[:ch], side="right")', 'src[:ch] = np.searchsorted(np.cumsum(pi1[i]), u[:ch], side="right")'),
    ("X27 pi_1 without the (1 - s) factor", "S", 'plan += [(s, mi, (1.0 - s) * pi0 + s * e)] * c["R"]', 'plan += [(s, mi, pi0 + s * e)] * c["R"]'),
    ("X28 stream bootstrap not stratified by member", "S", "        idx = [members_idx[m][rng.integers(0, len(members_idx[m]), len(members_idx[m]))] for m in range(M)]",
     "        allm = np.concatenate(members_idx); idx = [allm[rng.integers(0, len(allm), len(members_idx[m]))] for m in range(M)]"),
    ("X29 seeds not resampled (not crossed)", "S", "        sd = rng.integers(0, ns, ns) if ns else np.zeros(0, dtype=np.int64)", "        sd = np.arange(ns)"),
    ("X30 D_arm point against seed 0 only", "S", 'st["D1"] = interval(np.mean(occ) - np.mean([np.mean(x) for x in seeds_det]), bt["d1"])',
     'st["D1"] = interval(np.mean(occ) - np.mean(seeds_det[0]), bt["d1"])'),
    ("X31 DR1 on the KM-U OOS detector (wrong detector)", "S", 'seeds_det = [st["det"][((nm, "OCC"), sd)] for nm in KU if (nm, "OCC") in Se]',
     'seeds_det = [st["det"][((nm, "OOS"), sd)] for nm in KU if (nm, "OCC") in Se]'),
    ("X32 deciding s read from the first grid value", "S", '    sd = c["s_dec"]' + NL + '    mo = st["m_of"][sd]', '    sd = c["s_grid"][0]' + NL + '    mo = st["m_of"][sd]'),
    ("X33 per-member intervals from the pooled replicates", "S", 'interval(np.mean(occ[members_idx[m]] - oos[members_idx[m]]), bt["pm"][m])',
     'interval(np.mean(occ[members_idx[m]] - oos[members_idx[m]]), bt["d2"])'),
    ("X34 lower bound at the 5th percentile", "S", "lo=pct(reps, 0.025), hi=pct(reps, 0.975)", "lo=pct(reps, 0.05), hi=pct(reps, 0.975)"),
    ("X35 P4 delay read at s 0.05", "S", 'p4_delay=median_delay(st["delay"][(("AF-U", "OCC"), c["s_grid"][-1])]),', 'p4_delay=median_delay(st["delay"][(("AF-U", "OCC"), c["s_grid"][0])]),'),
    ("X36 source oracle read on the OOS detector", "S", 'orc = float(np.mean(st["det"][(("SRC", "OCC"), sdec)]))', 'orc = float(np.mean(st["det"][(("AF-U", "OOS"), sdec)]))'),
    ("X37 NOT SCOREABLE path prints a Brier", "S", '            say("PREDICTION %s: observed UNDETERMINED (DR0 MISCALIBRATED); Brier NOT SCOREABLE" % lab)',
     '            say("PREDICTION %s: observed %s; Brier %.4f" % (lab, v, U.brier(probs, "NEITHER")))'),
    ("X38 F-DR NOT FIRED line dropped (skip path)", "S", '        say("FALSIFIER F-DR: NOT FIRED (DR0 %s, DR2 %s; F-DR fires iff DR0 CALIBRATED and DR2 NEITHER or OOS-BETTER)" % (w0, v2))', '        pass'),
    ("X39 verdict line of record dropped", "S", 'verdict line of record: %s" % (', '%s" % ('),
    ("X40 tau identity removed", "S", '    if "%.6f" % to != c["tau_rc"]:', '    if False:'),
    ("X41 EVAL denominator check removed", "S", '    if (len(items), len(comps)) != (c["n_route"], c["comp_route"]):', '    if False:'),
    ("X42 members check removed", "S", "    if bad or set(srcs) != set(members):", "    if False:"),
    ("X43 pre-read write-once check removed", "S", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X44 marker not written before the EVAL read", "S", '    V.G.read_marker(U.P(c["marker"]), ', '    str(U.P(c["marker"]), '),
    ("X45 GATE-empty guard removed", "S", '    if not gits:' + NL + '        hit("REFUSE.GATE_EMPTY")', '    if False:' + NL + '        hit("REFUSE.GATE_EMPTY")'),
    ("X46 missing-vector refusal removed", "S", '    if nov:' + NL + '        hit("REFUSE.NOVEC")', '    if False:' + NL + '        hit("REFUSE.NOVEC")'),
    ("X47 KU k check removed", "S", '    if Lk != int(c["ku_k"]):', '    if False:'),
    ("X48 component bootstrap resamples nothing", "S", "            pools.append(np.concatenate([by_m[m][j] for j in dr]))", "            pools.append(np.concatenate(by_m[m]))"),
    ("X49 median delay over the detected streams only", "S", '    m = float(np.median(np.asarray(d, dtype=np.float64))) if len(d) else float("inf")',
     '    d = np.asarray(d, dtype=np.float64); m = float(np.median(d[np.isfinite(d)])) if np.isfinite(d).any() else float("inf")'),
    ("X50 AF-U filed without the one-cell centroid", "S", '    geos = [("AF-U", g.af_C)] + sorted(cents.items())', '    geos = [("AF-U", g.af_C[:g.n_graft])] + sorted(cents.items())'),
    ("X51 every KM-U seed = seed 0", "S", "        fit, _t = GB.ukm_fit(Xt, k, s)" + NL + '        out["KU%d" % s]', "        fit, _t = GB.ukm_fit(Xt, k, seeds[0])" + NL + '        out["KU%d" % s]'),
    ("X61 source-oracle reference from GATE (old self-calibration)", "S", "    p = np.bincount(src_t, minlength=len(members)).astype(np.float64) / len(src_t)",
     "    p = np.bincount(src_g, minlength=len(members)).astype(np.float64) / len(src_g)"),
    ("X52 source-oracle reference from EVAL", "S", "    p = np.bincount(src_t, minlength=len(members)).astype(np.float64) / len(src_t)",
     "    p = np.bincount(src_e, minlength=len(members)).astype(np.float64) / len(src_e)"),
    ("X53 tau at the 95th percentile (wrong tail)", "S", "        tau = float(np.percentile(og, 5.0))", "        tau = float(np.percentile(og, 95.0))"),
    ("X54 D_det replicates unpaired", "S", "        rd2.append(float(np.mean(occ[allx] - oos[allx])))",
     "        rd2.append(float(np.mean(occ[allx]) - np.mean(oos[np.sort(allx)[::-1]][:len(allx) // 2])))"),
    ("X55 level allows alpha n + 1 alarms", "S", "    k = int(math.floor(alpha * n + 1e-9))", "    k = int(math.floor(alpha * n + 1e-9)) + 1"),
    ("C56 prediction bands exclusive", "C", '    return bool(band[0] <= x <= band[1])', '    return bool(band[0] < x < band[1])'),
)


if __name__ == "__main__":
    sys.exit(main())
