"""GMM-FIXEDK readout (docs/judge_v2_program.md, "## Registered 2026-10-06 (before any code or call) — GMM-FIXEDK: would a GMM split
better if it could not run BIC to the cap? CONSTRUCTION-ARMS extended with two fixed-k = 2 Gaussian-mixture split rules (bisecting diagonal
GMM; bisecting full-covariance GMM in a node-local PCA subspace, reg_covar regularised) against the engine-like spherical k-means arm 1,
same corpora, matched leaf counts, 5 seeds, same readouts (zero calls; CPU; no Kotlin change; no certificate)", L24856-L24868, _as_of
the registrar's commit 9bff7e39, parent 4c764a1e). ZERO LLM / judge / embedding calls; CPU only; no JVM.

WORDS OF RECORD (carried from CONSTRUCTION-ARMS, printed beside the verdict): every arm is an approximation; arm 1 (ENGINE-LIKE SKM) is NOT
the engine, differences (i)-(vi) stated beside every arm-1 line; a win means 'worth a faithful engine arm', never 'the engine should
change'; a non-win is not parity (no TOST).

LAUNCH SEQUENCE (zero calls; temp only under E: via scratch_dir; one heavy process; the C leg is a POOL READER under rule 7: run the
dry-run and the run only when `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` exits 1, never beside a construction or site null):
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/gmm_fixedk.py --selftest     # fixtures, values asserted
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/gmm_fixedk.py --mutants      # sandbox copies, table printed
  python tools/analysis/gmm_fixedk.py --dry-run [--data-root <S1 root>] [--mmlu-root <main checkout>] [--workers 20]
        # pins, pool line FIRST, census (TRAIN only), L, m_min, the registered denominators (quoted; EVAL locked), root-split timings and
        # the COST ESTIMATE; no EVAL row read; 0 files written
  python tools/analysis/gmm_fixedk.py --run [--data-root ...] [--mmlu-root ...] [--workers 20] [--out <path>]
        # the readout of record: WRITE-ONCE outcome (mode x) + SHA256SUMS.txt, default
        # E:/TaxoArena_backup_<date>_gmm_fixedk/gmm_fixedk_outcome.txt; an existing path REFUSES before any read; NEVER committed
        # (sha256-pin it, back it up); launch detached (Start-Process) if the dry-run's wall estimate exceeds 100 min
  --data-root / --mmlu-root / --workers exactly as construction_arms.py (default data root env TAXOARENA_DATA_ROOT, else
  <main checkout>/.claude/worktrees/intent-s1-run; --workers REFUSES N > 22).

INSTRUMENT (imported UNCHANGED, LF blobs asserted at every entry point; another blob REFUSES): construction_arms.py blob:5d08a5df (and
  through it every blob it pins: granularity_gt bcb4240d, intent_transfer_s1 4e9d9d05, intent_transfer_s0 f662ceb1, stability_vs_kmeans
  a67bbf0a, site_support 4612345c, oos_tree_cells caaced4a, zc_common c912dccf, cert_align_size 80f7bb78). Reused unchanged: the loaders
  (load_world: C leg first, pool line first; unlock_eval: GATE-before-EVAL), identity_check (I1-I3), best_first (the registered expansion
  to exactly L, forced 2-means slot), split_skm2, node_seed, fit_engine (arm 1, F2), fit_bisect (arm 2), fit_gmm (arm 3), fit_readout
  (filing to the renormalised TRAIN leaf centroids; (a) DP_coarse on the F1 common Ward-on-centroids hierarchy, dp_fast asserted equal
  to S1.dendrogram_purity; (c) fine leaf filing accuracy by TRAIN majority), random_shape (GR2), leaf_majority, the triplet helpers
  (clusters_rows, topo_of, conv, sub_rows), spread5, pct, sd1.

ARMS (all fitted on TRAIN only, label-free; seeds 0-4; matched L):
  (1) ENGINE-SKM control = construction_arms.fit_engine, unchanged (re-run with seeds 0-4; IDENTITY PRECONDITION GK-I0 below).
  (6) BISECT-GMM-DIAG: sklearn GaussianMixture(n_components 2, covariance_type 'diag', reg_covar 1e-6, n_init 3, max_iter 200,
      random_state = node_seed(s, c, 2)) on the node's 256-d TRAIN slice; hard assignment by posterior (predict).
  (7) BISECT-GMM-FULL: PCA(n_components p, whiten False, svd_solver 'full') fitted on the node's TRAIN rows, p = 32 when the node has
      >= 10 x 32 = 320 TRAIN rows, else max(2, floor(n / 10)); GaussianMixture(2, 'full', reg_covar 1e-4, n_init 3, max_iter 200,
      random_state = node_seed(s, c, 2)) in that subspace; hard assignment by posterior.
  Both expand through construction_arms.best_first (the largest leaf by TRAIN count is split next, ties to the smaller node id); a split
  whose hard assignment leaves a child with fewer than 2 TRAIN rows is REPLACED by the registered forced spherical 2-means split
  (split_skm2, seed node_seed(s, c, 9)) and COUNTED as forced; convergence failures, per-node p and the minimum component weight are
  printed. A deciding arm or the control short of L REFUSES (matched L).
  (2) BISECT-SKM, (3) GMM-BIC: construction_arms' own fits, re-run (descriptive re-prints; their point D against arm 1 is checked
      against CONSTRUCTION-ARMS' record to the 5th digit and the result printed, descriptive; their intervals use this test's stream).

READOUTS AND CRITERION (registered):
  D_jr = mean over arm j's 5 seeds - mean over arm 1's 5 seeds, j in {BISECT-GMM-DIAG, BISECT-GMM-FULL}, r in {(a), (c)};
  spread_1r = range of arm 1's five seed values (known: (a) 0.04305 / 0.06048, (c) 0.10797 / 0.02323, asserted by GK-I0).
  INTERVAL exactly C-CA's: percentile bootstrap B 2,000, numpy default_rng(20261006), a fresh stream per corpus (MASSIVE then CLINC);
  per replicate the EVAL CK-CLOSE components resampled once (shared by all arms: paired), then 5 seed indices per arm (crossed) in the
  order of GK-R1; bounds np.percentile(., [2.5, 97.5]); the bootstrap SD is the SE reported (seed-corrected SE beside, C-2).
  C-GK (THE ONE DECIDING CRITERION; point AND interval in one clause): GMM-WINS iff some (j, r) has on BOTH MASSIVE and CLINC
  D_jr > spread_1r AND the 95% lower bound > 0 (winning pairs named); NO-GMM-WINS otherwise. FAILS (rule 8) printed for both
  outcomes; F-GK fires iff GMM-WINS.
  SUPPORT per deciding cell: n, components, Kish, SE(D), item-only SD, seed term, seed-corrected SE, DEFF_total = Kish x (SE / SE_item)^2,
  n_eff, MDE80 per corpus = spread + 0.84 SE, joint = spread + 1.25 SE, beside the registered values; the REALISED deciding MDE80 (a
  pair needs both corpora: per pair the max over the two corpora, deciding = the min over pairs) beside the registered 0.076, and the
  max over every deciding cell (CONSTRUCTION-ARMS' W-2 convention) beside; the verdict line (f).
  DESCRIPTIVE: arms 6 / 7 against BISECT-SKM and GMM-BIC (D and interval from the same replicates); (b) seed-pair triplet disagreement
  (all-triplets / resolved-in-both, coverage, unresolved share) and 90%-subsample stability for every arm; (d) CLINC OOS AUROC with
  oos_tree_cells' paired component bootstrap; leaf balance (W-3: distinct TRAIN-majority fine intents over the distinct EVAL fine
  intents) and leaf-size distributions; forced / replaced counts; GMM node diagnostics; GR2 and own-hierarchy DP; the engine rows; the
  C leg (DP vs the MMLU-Pro category, in-sample on C). Arm 1's words beside every arm-1 line.
  IDENTITY PRECONDITIONS (refuse, nothing written): I1-I3 through construction_arms.identity_check right after EVAL is unlocked; GK-I0
  arm 1's mean and range per corpus x readout equal to CONSTRUCTION-ARMS' P1 points and spreads at "%.5f" (DP_coarse 0.63959 / 0.50489,
  spread 0.04305 / 0.06048; (c) 0.76648 / 0.83951, spread 0.10797 / 0.02323), checked after the fits and before the bootstrap.
  PREDICTIONS P1-P6 (bands closed; P3-P6 outcome probabilities by Brier).

BUILDER'S READINGS (printed; the registrar confirms or brackets BEFORE --run):
  GK-R1 seed-draw order per replicate: components, then ENGINE-SKM, BISECT-GMM-DIAG, BISECT-GMM-FULL, BISECT-SKM, GMM-BIC (control, deciding,
    descriptive; KAPPA-SKM is not fitted). One stream cannot reproduce CONSTRUCTION-ARMS' replicates once more arms draw, so the re-print
    intervals of arms 2 / 3 differ from the record by stream; their POINT D is deterministic and is checked against the record.
  GK-R2 node seed node_seed(s, c, 2) for both mixtures (CA-R2 with k = 2); the replacement split uses CA's forced slot 9.
  GK-R3 PCA svd_solver 'full' (sklearn's 'auto' switches to a randomised solver on large nodes, which would make the fit seed-dependent
    outside the registered seed); not whitened, centred (sklearn PCA).
  GK-R4 a mixture fit that raises (ValueError / LinAlgError) is replaced by the forced split exactly as a < 2 child is, counted
    separately as 'fit errors' and printed (the registration names no other path; expected 0).
  GK-R5 forced share for P4 = (best-first forced + replaced) / (all splits), mean over the 5 seeds (CA-R10); scored on MASSIVE and CLINC
    (C printed). P4 / P5 / P6 events as registered; Brier (p - [event])^2.
  GK-R6 leaf balance = the W-3 count of POSTRUN_construction_arms (its recheck.py): distinct non-null TRAIN-majority fine labels over the
    distinct EVAL fine labels.
  GK-R7 p is capped at the slice dimension (min(p, d)); it never binds on the run of record (d 256, p <= 32), only on the 8-d fixtures.

SELFTEST: SELFTEST_DOC below (value checks, end-to-end through main(["--run"]) on planted worlds + the real arms on on-disk fixtures).
MUTANTS: the table is in the commit message of the build and in MUTANT_TABLE below once run.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import argparse        # noqa: E402
import collections     # noqa: E402
import contextlib      # noqa: E402
import datetime        # noqa: E402
import functools       # noqa: E402
import io              # noqa: E402
import math            # noqa: E402
import re              # noqa: E402
import subprocess      # noqa: E402
import sys             # noqa: E402
import time            # noqa: E402
import warnings        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import construction_arms as CAR        # noqa: E402  (imported unchanged; blob asserted)

import numpy as np                     # noqa: E402

GG, S0, S1, SPL, ZC, SVK, OTC = CAR.GG, CAR.S0, CAR.S1, CAR.SPL, CAR.ZC, CAR.SVK, CAR.OTC
scratch_dir = CAR.scratch_dir
SRC = os.path.dirname(os.path.abspath(CAR.__file__))     # the instrument directory (a sandbox copy of this script still checks the real blobs)
TAG = "[GMM-FIXEDK]"
REG = ("docs/judge_v2_program.md L24856-L24868 (registrar's commit 9bff7e39, _as_of parent 4c764a1e), \"## Registered 2026-10-06 (before "
       "any code or call) \u2014 GMM-FIXEDK: would a GMM split better if it could not run BIC to the cap? ...\"")
CAR_BLOB = "5d08a5dfb8c0cb0b5330512259b4732aa4af2dd2"
PINNED_CODE = dict(CAR.PINNED_CODE, **{"construction_arms.py": CAR_BLOB})
CORPORA = ("massive", "clinc")
LEGS = ("massive", "clinc", "mmlu")
SEEDS = (0, 1, 2, 3, 4)
CONTROL = "ENGINE-SKM"
DIAG = "BISECT-GMM-DIAG"
FULL = "BISECT-GMM-FULL"
DECIDING = (DIAG, FULL)
REPRINT = ("BISECT-SKM", "GMM-BIC")
ALL_ARMS = (CONTROL, DIAG, FULL, "BISECT-SKM", "GMM-BIC")
SEED_DRAWS = (CONTROL, DIAG, FULL, "BISECT-SKM", "GMM-BIC")          # GK-R1
READOUTS = ("a", "c")
RNAME = {"a": "(a) DP_coarse (common hierarchy)", "c": "(c) leaf filing accuracy (fine)"}
K_GMM = 2
N_INIT = 3
MAX_ITER = 200
REG_DIAG = 1e-6
REG_FULL = 1e-4
P_FULL = 32
P_ROWS = 10
P_MIN = 2
MIN_CHILD = 2
B_BOOT = 2000
SEED_BOOT = 20261006
N_RANDOM = 200
TRIPLETS = 100_000
MAX_WORKERS = 22
SEED_CORR = len(SEEDS) / float(len(SEEDS) - 1)                       # C-2: 1.25
OUTCOME = "gmm_fixedk_outcome.txt"
# ---------------------------------------------------------------------------------------------- registered numbers (quoted, not re-derived)
ARM1_ID = {("a", "massive"): ("0.63959", "0.04305"), ("a", "clinc"): ("0.50489", "0.06048"),
           ("c", "massive"): ("0.76648", "0.10797"), ("c", "clinc"): ("0.83951", "0.02323")}          # GK-I0: (mean, range)
IDENTITY = dict(CAR.IDENTITY)                                                                          # I1-I3
REG_SE = {("a", "massive"): 0.0160, ("a", "clinc"): 0.0124, ("c", "massive"): 0.0173, ("c", "clinc"): 0.0056}
REG_MDE_JOINT = {("a", "massive"): 0.0631, ("a", "clinc"): 0.0760, ("c", "massive"): 0.1296, ("c", "clinc"): 0.0302}
REG_MDE_PAIR = {"a": 0.076, "c": 0.130}
REG_MDE_DECIDING = 0.076
CA_RECORD_D = {("BISECT-SKM", "a", "massive"): "-0.03802", ("BISECT-SKM", "a", "clinc"): "+0.00056",
               ("GMM-BIC", "a", "massive"): "+0.00423", ("GMM-BIC", "a", "clinc"): "+0.01667",
               ("BISECT-SKM", "c", "massive"): "+0.01290", ("BISECT-SKM", "c", "clinc"): "-0.02119",
               ("GMM-BIC", "c", "massive"): "-0.00142", ("GMM-BIC", "c", "clinc"): "-0.14832"}
REG_SUPPORT = ("registered SUPPORT (quoted): MASSIVE 4,946 EVAL / 4,923 components (Kish 1.0093), CLINC 6,672 / 6,672 (Kish 1.0000), crossed "
               "with 5 seeds per arm; SE(D) transported from CONSTRUCTION-ARMS' realised BISECT-SKM intervals (width / 3.92): (a) 0.0160 / "
               "0.0124, (c) 0.0173 / 0.0056; DEFF_total (a) 5.38 / 14.1, (c) 20.2 / 1.78; n_eff (a) 919 / 473, (c) 245 / 3,748; MDE80 = "
               "spread_1r + 1.25 SE: (a) 0.0631 / 0.0760, (c) 0.1296 / 0.0302; a pair needs both corpora: (a) 0.076, (c) 0.130; deciding "
               "MDE80 0.076 (via (a)); CONSTRUCTION-ARMS' realised joint MDE80 was 0.132 (W-2), the (c) figure here; (g) (c) on MASSIVE is "
               "effectively unreachable (bar 0.108 carried by one arm-1 seed), (a) has a floor of about 0.06 / 0.075 at infinite items")
VERDICT_LINE = ("VERDICT LINE (registered (f)): the largest predicted |D_jr| is 0.02, 0.02 from the bar, below the MDE80 0.076: DESCRIPTIVE-ONLY "
                "at the prediction; C-GK is scored as registered; NO-GMM-WINS is not parity")
ARM1_WORDS = (CAR.ARM1_WORDS + "; (vi) BRANCHING: arm 1 splits 2-, 3- and 4-way in roughly comparable numbers on TRAIN (CONSTRUCTION-ARMS "
              "W-1 bracket: MASSIVE {2:11-30, 3:13-22, 4:9-12}, CLINC {2:28-38, 3:12-23, 4:18-28}), the engine about 90% binary")
ARM1_TAG = " [arm 1 = ENGINE-LIKE SKM, NOT the engine; differences (i)-(vi), WORDS OF RECORD]"
WORDS = ("WORDS OF RECORD (carried from CONSTRUCTION-ARMS): every arm is an approximation; a win means 'worth a faithful engine arm', never "
         "'the engine should change'; a non-win is not parity (no TOST); " + ARM1_WORDS)
NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): anything about the engine's own split rule (arm 1 a stand-in, differences (i)-(vi)); "
            "parity (no TOST); a modality or certificate property of any split; GMM with BIC or any other k-selection; MMLU-Pro EVAL, routing, "
            "judged value, other embedders, slices, draws or leaf counts; a (c) win on MASSIVE below the 0.108 bar.")
P_BANDS = {DIAG: {"a": (-0.02, -0.08, 0.04), "c": (-0.01, -0.06, 0.04)},
           FULL: {"a": (-0.01, -0.07, 0.05), "c": (0.00, -0.05, 0.05)}}
P_ID = {DIAG: "P1", FULL: "P2"}
P3_WIN = 0.05
P4_PROB, P4_MAX = 0.75, 0.10
P5_PROB, P5_MIN = 0.80, -0.06
P6_PROB, P6_BAND = 0.60, (-0.03, 0.03)
F5 = "%+.5f"


class Refused(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise Refused("%s REFUSED: %s" % (TAG, msg))


def f5(x, fmt=F5):
    return "n/a" if x is None or not np.isfinite(x) else fmt % x


def check_code_pins(pinned=None):
    got = {}
    for name, want in sorted((pinned or PINNED_CODE).items()):
        b = ZC.git_blob(os.path.join(SRC, name))
        got[name] = b
        if b != want:
            refuse("%s is blob:%s, the instrument of record is blob:%s (imported unchanged)" % (name, b, want))
    return got


# ================================================================================================ the two registered node rules
def pca_dim(n):
    """(7)'s subspace: p = 32 when the node has >= 10 x 32 TRAIN rows, else floor(n / 10), minimum 2."""
    return P_FULL if n >= P_ROWS * P_FULL else max(P_MIN, n // P_ROWS)


class BisectGmmRule(object):
    """Arms (6) / (7): a k = 2 mixture at every node; a < 2 child (or a fit error, GK-R4) -> the registered forced spherical 2-means
    split, counted. memo / log per node id (best_first calls the rule on the largest leaf; a returned split is always taken)."""

    def __init__(self, full):
        self.full = bool(full)
        self.memo, self.log = {}, {}

    def fit(self, c, Xs, seed):
        from sklearn.mixture import GaussianMixture
        rs = CAR.node_seed(seed, c, K_GMM) % (2 ** 32)
        n = len(Xs)
        whiten, svd = None, None
        if self.full:
            from sklearn.decomposition import PCA
            p = min(pca_dim(n), Xs.shape[1])                    # GK-R7: never binds at the 256-d slice (p <= 32)
            pca = PCA(n_components=p, whiten=False, svd_solver="full")
            Z = pca.fit_transform(Xs)
            whiten, svd = bool(pca.whiten), pca.svd_solver
            gm = GaussianMixture(n_components=K_GMM, covariance_type="full", reg_covar=REG_FULL, n_init=N_INIT, max_iter=MAX_ITER,
                                 random_state=rs)
        else:
            p = Xs.shape[1]
            Z = Xs
            gm = GaussianMixture(n_components=K_GMM, covariance_type="diag", reg_covar=REG_DIAG, n_init=N_INIT, max_iter=MAX_ITER,
                                 random_state=rs)
        rec = dict(n=n, p=int(p), zdim=int(Z.shape[1]), whiten=whiten, svd=svd, rs=int(rs), cov_type=gm.covariance_type,
                   reg=float(gm.reg_covar), n_init=int(gm.n_init), max_iter=int(gm.max_iter), error=None)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                gm.fit(Z)
                lab = gm.predict(Z).astype(np.int64)
            rec.update(converged=bool(gm.converged_), wmin=float(np.min(gm.weights_)))
        except (ValueError, np.linalg.LinAlgError) as e:
            lab = None
            rec.update(converged=False, wmin=float("nan"), error=type(e).__name__)
        return lab, rec

    def __call__(self, c, Xs, cap, seed):
        if c in self.memo:
            return self.memo[c]
        lab, rec = self.fit(c, Xs, seed)
        sizes = None if lab is None else np.bincount(lab, minlength=K_GMM)
        rep = bool(lab is None or int(sizes.min()) < MIN_CHILD)
        fs = CAR.node_seed(seed, c, CAR.FORCE_SLOT)
        if rep:
            lab = CAR.split_skm2(Xs, fs)
            if lab.min() == lab.max():
                lab = None
        rec.update(replaced=rep, force_seed=int(fs) if rep else None, sizes=None if sizes is None else [int(x) for x in sizes])
        self.memo[c], self.log[c] = lab, rec
        return lab


def fit_bisect_gmm(X, L, seed, m_min=None, info=None, full=False):
    rule = BisectGmmRule(full)
    H = CAR.best_first(X, L, seed, rule, FULL if full else DIAG)
    split = sorted(set(int(p[1:]) for p in H["parent"].values()))
    nrep = sum(1 for c in split if rule.memo.get(c) is not None and rule.log[c]["replaced"])
    H["forced"] += nrep
    H["rule_splits"] -= nrep
    H["replaced"] = nrep
    H["gmm"] = [dict(rule.log[c], node=c) for c in split if c in rule.log and rule.memo.get(c) is not None]
    return H


def fit_diag(X, L, seed, m_min=None, info=None):
    return fit_bisect_gmm(X, L, seed, m_min, info, full=False)


def fit_full(X, L, seed, m_min=None, info=None):
    return fit_bisect_gmm(X, L, seed, m_min, info, full=True)


FITS = collections.OrderedDict([(CONTROL, CAR.fit_engine), (DIAG, fit_diag), (FULL, fit_full), ("BISECT-SKM", CAR.fit_bisect),
                                ("GMM-BIC", CAR.fit_gmm)])


# ================================================================================================ fit orchestration
def _fit_job(spec):
    arm, X, L, seed, m_min, info = spec
    t0 = time.time()
    H = FITS[arm](X, L, seed, m_min, info)
    H["secs"] = time.time() - t0
    return H


def fit_jobs(world, legs):
    specs, keys = [], []
    for leg in legs:
        Wc = world[leg]
        X, L, mm = Wc["Xtr"], Wc["L"], Wc["m_min"]
        n = len(X)
        for arm in ALL_ARMS:
            for s in SEEDS:
                specs.append((arm, X, L, s, mm, dict(leg=leg, sub=None, eng=Wc.get("eng"))))
                keys.append((leg, arm, "full", s))
            for s in SEEDS:
                r = CAR.sub_rows(n, s)
                specs.append((arm, X[r], L, s, mm, dict(leg=leg, sub=s, eng=Wc.get("eng"))))
                keys.append((leg, arm, "sub", s))
    order = sorted(range(len(specs)), key=lambda i: -len(specs[i][1]) * (3 if specs[i][0] in ("GMM-BIC", CONTROL) else 1))
    return [specs[i] for i in order], [keys[i] for i in order]


def run_fits(world, legs, workers, out):
    specs, keys = fit_jobs(world, legs)
    t0 = time.time()
    if workers <= 1:
        res = [_fit_job(s) for s in specs]
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(_fit_job, specs, chunksize=1))
    F = dict(zip(keys, res))
    out("FITS: %d fits (%s) in %.1f s wall with %d worker(s); CPU seconds summed %.1f" % (
        len(res), ", ".join(legs), time.time() - t0, workers, sum(h.get("secs", 0.0) for h in res)))
    return F


# ================================================================================================ statistics
def clears(s):
    return bool(s["D"] > s["spread"]) and bool(s["lo"] > 0)


def ahead(s):
    return bool(s["D"] < -s["spread"]) and bool(s["hi"] < 0)


def gk_decide(stats):
    """stats[(j, r)][corpus] = dict(D, spread, lo, hi), j in DECIDING. -> (word, winners, fails {(j, r): [(corpus, reasons)]})."""
    winners, fails = [], collections.OrderedDict()
    for j in DECIDING:
        for r in READOUTS:
            per = stats[(j, r)]
            ok = [clears(per[c]) for c in CORPORA]
            if all(ok):
                winners.append((j, r))
            else:
                why = []
                for c in CORPORA:
                    s = per[c]
                    rs = []
                    if not bool(s["D"] > s["spread"]):
                        rs.append("D <= spread")
                    if not bool(s["lo"] > 0):
                        rs.append("lower bound <= 0")
                    if rs:
                        why.append((c, rs))
                fails[(j, r)] = why
    return ("GMM-WINS" if winners else "NO-GMM-WINS"), winners, fails


def bootstrap_means(vals_w_fn, comp, B, seed):
    """The registered crossed / paired bootstrap (GK-R1 order). vals_w_fn(w) -> {r: {arm: array over the 5 seeds}}.
    -> M {(arm, r): per-replicate mean over the arm's resampled seeds}, Mi {(arm, r): per-replicate mean over all 5 seeds (item-only)}."""
    rng = np.random.default_rng(seed)
    _u, cc = np.unique(comp, return_inverse=True)
    G = int(cc.max()) + 1
    M = {(a, r): np.empty(B) for a in ALL_ARMS for r in READOUTS}
    Mi = {(a, r): np.empty(B) for a in ALL_ARMS for r in READOUTS}
    for b in range(B):
        w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)
        idx = {a: rng.integers(0, len(SEEDS), size=len(SEEDS)) for a in SEED_DRAWS}
        v = vals_w_fn(w)
        for r in READOUTS:
            for a in ALL_ARMS:
                M[(a, r)][b] = float(v[r][a][idx[a]].mean())
                Mi[(a, r)][b] = float(v[r][a].mean())
    return M, Mi


def contrast(vals, M, Mi, r, j, k, spread):
    vj, vk = vals[r][j], vals[r][k]
    D = float(vj.mean() - vk.mean())
    x = M[(j, r)] - M[(k, r)]
    lo, hi = CAR.pct(x)
    se, si = CAR.sd1(x), CAR.sd1(Mi[(j, r)] - Mi[(k, r)])
    seed_term = math.sqrt(np.var(vj, ddof=1) / len(vj) + np.var(vk, ddof=1) / len(vk))
    se_corr = math.sqrt(si ** 2 + max(0.0, se ** 2 - si ** 2) * SEED_CORR) if np.isfinite(se) and np.isfinite(si) else float("nan")
    return dict(D=D, spread=spread, lo=lo, hi=hi, se=se, se_item=si, se_corr=se_corr, seed_term=seed_term)


def arm1_identity(R, ident):
    """GK-I0: arm 1's mean and range (%.5f) per readout x corpus against CONSTRUCTION-ARMS' record. -> (lines, bad)."""
    bad, parts = [], []
    for r in READOUTS:
        for c in CORPORA:
            v = R[c]["vals"][r][CONTROL]
            got = ("%.5f" % float(np.mean(v)), "%.5f" % CAR.spread5(v))
            want = ident[(r, c)]
            parts.append("%s %s mean %s (of record %s) range %s (of record %s)" % (r, c, got[0], want[0], got[1], want[1]))
            if got != want:
                bad.append("%s %s %s / %s != %s / %s" % (r, c, got[0], got[1], want[0], want[1]))
    return "ARM-1 IDENTITY (GK-I0; arm 1 re-run with seeds 0-4): %s: %s" % ("; ".join(parts), "REPRODUCED" if not bad else "MISMATCH"), bad


# ================================================================================================ readouts
def leaf_balance(Wc, H):
    maj = CAR.leaf_majority(H, Wc["tr_fine"])
    return len(set(m for m in maj if m is not None)), int(len(np.unique(Wc["ev_fine"])))


def corpus_fits(Wc, F):
    leg = Wc["name"]
    fr = {a: [CAR.fit_readout(Wc, F[(leg, a, "full", s)]) for s in SEEDS] for a in ALL_ARMS}
    for a in (CONTROL,) + DECIDING:
        for x in fr[a]:
            if x["H"]["nL"] != Wc["L"]:
                refuse("%s on %s reached %d leaves, not the registered L = %d (matched leaf count)" % (a, leg, x["H"]["nL"], Wc["L"]))
    vals = {r: {a: np.array([x["dp" if r == "a" else "fa"] for x in fr[a]]) for a in ALL_ARMS} for r in READOUTS}
    return dict(name=leg, n=len(Wc["ev_coarse"]), G=int(len(np.unique(Wc["comp"]))), kish=S0.kish(Wc["comp"]), L=Wc["L"], fr=fr, vals=vals,
                spread={r: CAR.spread5(vals[r][CONTROL]) for r in READOUTS})


def corpus_stats(Wc, Rc, B, n_random, boot_seed):
    fr, vals = Rc["fr"], Rc["vals"]

    def vals_w(w):
        o = {r: {} for r in READOUTS}
        for a in ALL_ARMS:
            da, dc = [], []
            for x in fr[a]:
                ok = x["ok"]
                da.append(CAR.dp_fast(x["st"], x["filed"][ok], Wc["ev_coarse"][ok], Wc["Kc"], w[ok]) if ok.any() else np.nan)
                dc.append(float((w * x["correct"]).sum() / w.sum()))
            o["a"][a], o["c"][a] = np.array(da), np.array(dc)
        return o
    M, Mi = bootstrap_means(vals_w, Wc["comp"], B, boot_seed)
    Rc["stats"] = {(j, r): contrast(vals, M, Mi, r, j, CONTROL, Rc["spread"][r]) for j in DECIDING + REPRINT for r in READOUTS}
    Rc["vs"] = {(j, k, r): contrast(vals, M, Mi, r, j, k, float("nan")) for j in DECIDING for k in REPRINT for r in READOUTS}
    Rc["random"] = {a: [CAR.random_shape(Wc, x, n_random) for x in fr[a]] for a in ALL_ARMS}
    Rc["random_own"] = {a: [CAR.random_shape_own(Wc, x, n_random) for x in fr[a]] for a in ALL_ARMS}
    Rc["balance"] = {a: [leaf_balance(Wc, x["H"]) for x in fr[a]] for a in ALL_ARMS}
    Rc["engine"] = Wc["engine"]
    if Wc.get("Xoos") is not None:
        Rc["oos"] = oos_block(Wc, fr, B)
    return Rc


def oos_block(Wc, fr, B):
    names, sc = [], {}
    for a in ALL_ARMS:
        for i, x in enumerate(fr[a]):
            if "A" in x and np.isfinite(x["A"]):
                k = "%s#%d" % (a, i)
                names.append(k)
                sc[k] = {"in": x["s_in"], "oos": x["s_oos"]}
    A = {a: np.array([x.get("A", np.nan) for x in fr[a]]) for a in ALL_ARMS}
    out = {"A": A, "D": {}, "ci": {}, "n_in": len(Wc["ev_rows"]), "n_oos": len(Wc["oos_rows"])}
    if not np.all(np.isfinite(A[CONTROL])):
        return out
    draws = OTC.paired_boot(Wc["C"], {"in": Wc["ev_rows"], "oos": Wc["oos_rows"]}, sc, names, B)
    d1 = np.mean(np.vstack([draws["%s#%d" % (CONTROL, i)] for i in range(len(SEEDS))]), axis=0)
    for a in ALL_ARMS:
        if a == CONTROL or not np.all(np.isfinite(A[a])):
            continue
        da = np.mean(np.vstack([draws["%s#%d" % (a, i)] for i in range(len(SEEDS))]), axis=0)
        out["D"][a] = float(A[a].mean() - A[CONTROL].mean())
        out["ci"][a] = CAR.pct(da - d1)
    return out


def triplet_block(Wc, F):
    """(b): seed pairs (full fits) and 90%-subsample pairs, every arm, both conventions, coverage and unresolved shares."""
    leg = Wc["name"]
    n = len(Wc["Xtr"])
    trip = Wc["trip"]
    allrows = np.arange(n)
    out = {"seed": {}, "sub": {}, "unres": {}, "unres_sub": {}}
    for a in ALL_ARMS:
        tp = [CAR.topo_of(CAR.clusters_rows(F[(leg, a, "full", s)], allrows, n), n, trip) for s in SEEDS]
        prs = [CAR.conv(tp[i], tp[k]) for i in range(5) for k in range(i + 1, 5)]
        out["seed"][a] = (float(np.mean([p[0] for p in prs])), float(np.nanmean([p[1] for p in prs])), float(np.mean([p[2] for p in prs])))
        out["unres"][a] = float(np.mean([np.mean(t == 3) for t in tp]))
        tps, ins = [], []
        for s in SEEDS:
            r = CAR.sub_rows(n, s)
            tps.append(CAR.topo_of(CAR.clusters_rows(F[(leg, a, "sub", s)], r, n), n, trip))
            m = np.zeros(n, dtype=bool)
            m[r] = True
            ins.append(m[trip].all(axis=1))
        prs = [CAR.conv(tps[i], tps[k], ins[i] & ins[k]) for i in range(5) for k in range(i + 1, 5)]
        out["sub"][a] = (float(np.mean([p[0] for p in prs])), float(np.nanmean([p[1] for p in prs])), float(np.mean([p[2] for p in prs])))
        out["unres_sub"][a] = float(np.mean([np.mean(t[m] == 3) for t, m in zip(tps, ins)]))
    return out


def mmlu_block(Wm, F):
    out = {"dp": {}, "engine": {}}
    for a in ALL_ARMS:
        vals = []
        for s in SEEDS:
            H = F[("mmlu", a, "full", s)]
            vals.append(CAR.dp_s1(H, H["lab"], Wm["cat"]))
        out["dp"][a] = np.array(vals)
    for t, e in Wm["engines"].items():
        fl = np.argmax(Wm["Xtr"] @ e["leaf_mu"].T, axis=1)
        out["engine"][t] = (S1.dendrogram_purity(e["parent"], e["leaves"], [e["leaves"][j] for j in fl], list(Wm["cat"])), len(e["leaves"]))
    return out


def fit_summary(F, leg):
    rows = {}
    for a in ALL_ARMS:
        hs = [F[(leg, a, "full", s)] for s in SEEDS]
        sh = [h["forced"] / float(h["forced"] + h["rule_splits"]) if (h["forced"] + h["rule_splits"]) else 0.0 for h in hs]
        szs = [np.bincount(h["lab"], minlength=h["nL"]) for h in hs]
        allsz = np.concatenate(szs)
        nodes = [g for h in hs for g in (h.get("gmm") or [])]
        rows[a] = dict(leaves=[h["nL"] for h in hs], forced=[h["forced"] for h in hs], rule=[h["rule_splits"] for h in hs],
                       replaced=[h.get("replaced") for h in hs], share=float(np.mean(sh)),
                       sizes=(int(allsz.min()), float(np.median(allsz)), int(allsz.max())),
                       small=[int((z < 10).sum()) for z in szs], big=[int((z >= 200).sum()) for z in szs],
                       nodes=nodes, has_log=any("gmm" in h for h in hs))
    return rows


def compute(world, F, B, n_random, ident1):
    R = {"corpora": {}, "trip": {}, "fits": {}}
    for c in CORPORA:
        R["corpora"][c] = corpus_fits(world[c], F)
    idline, bad = arm1_identity(R["corpora"], ident1)
    R["id1"] = idline
    if bad:
        print(idline)
        refuse("ARM-1 IDENTITY PRECONDITION GK-I0 FAILED (%s): arm 1 does not reproduce CONSTRUCTION-ARMS; no readout is written" % "; ".join(bad))
    for c in CORPORA:
        corpus_stats(world[c], R["corpora"][c], B, n_random, SEED_BOOT)
    for leg in LEGS:
        R["trip"][leg] = triplet_block(world[leg], F)
        R["fits"][leg] = fit_summary(F, leg)
    R["mmlu"] = mmlu_block(world["mmlu"], F)
    R["mmlu"].update(m_min=world["mmlu"]["m_min"], L=world["mmlu"]["L"], nC=world["mmlu"]["nC"])
    R["stats"] = {(j, r): {c: R["corpora"][c]["stats"][(j, r)] for c in CORPORA} for j in DECIDING for r in READOUTS}
    R["word"], R["winners"], R["fails"] = gk_decide(R["stats"])
    R["B"], R["n_random"] = B, n_random
    return R


# ================================================================================================ render
def band(x, b):
    return GG.band(x, b[1], b[2])


def support_lines(R):
    L = [REG_SUPPORT]
    pair = {}
    cells = []
    for j in DECIDING:
        for r in READOUTS:
            mj = []
            for c in CORPORA:
                Rc = R["corpora"][c]
                s = Rc["stats"][(j, r)]
                deff = Rc["kish"] * (s["se"] / s["se_item"]) ** 2 if np.isfinite(s["se_item"]) and s["se_item"] > 0 else float("nan")
                mde1 = s["spread"] + 0.84 * s["se"]
                mdej = s["spread"] + 1.25 * s["se"]
                mj.append(mdej)
                cells.append(mdej)
                L.append("SUPPORT %s %s %-15s n %d, components %d, Kish %.4f; SE(D) %s (registered %.4f); seed-corrected SE %s (seed variance x "
                         "n/(n-1) = 1.25; the percentile interval is anti-conservative on the seed axis); item-only SD %s; seed term %s; "
                         "DEFF_total %s; n_eff %s; MDE80 per corpus %s; joint %s (registered %.4f)%s" % (
                             c, r, j, Rc["n"], Rc["G"], Rc["kish"], f5(s["se"], "%.5f"), REG_SE[(r, c)], f5(s["se_corr"], "%.5f"),
                             f5(s["se_item"], "%.5f"), f5(s["seed_term"], "%.5f"), f5(deff, "%.2f"),
                             f5(Rc["n"] / deff if np.isfinite(deff) and deff > 0 else float("nan"), "%.0f"), f5(mde1, "%.4f"), f5(mdej, "%.4f"),
                             REG_MDE_JOINT[(r, c)], ARM1_TAG))
            pair[(j, r)] = max(mj)
    for (j, r), v in pair.items():
        L.append("MDE80 PAIR %s %s (both corpora: the max of the two joint MDE80) %s (registered %s %.3f)" % (j, r, f5(v, "%.4f"), r,
                                                                                                         REG_MDE_PAIR[r]))
    dec = min(pair.values())
    L.append("REALISED DECIDING MDE80 (the easiest pair: min over pairs) %s against %.3f registered; max over every deciding cell %s "
             "(CONSTRUCTION-ARMS' W-2 convention; its realised figure was 0.132)" % (f5(dec, "%.4f"), REG_MDE_DECIDING, f5(max(cells), "%.4f")))
    L.append(VERDICT_LINE)
    return L


def render(R, meta):
    L = []
    L.append("GMM-FIXEDK readout (%s); mode --run; %s; date %s; ZERO calls; 0 CCE" % (REG, meta["pins"], datetime.date.today().isoformat()))
    if meta.get("fixture"):
        L.append("FIXTURE PARAMETERS (selftest; NOT OF RECORD): %s" % meta["fixture"])
    for k in ("imports", "pool", "data", "census", "mmin", "audit", "identity"):
        L += list(meta.get(k) or [])
    L.append(R["id1"])
    L.append("BUILDER'S READINGS (GK-R1..GK-R6, the script docstring; the registrar confirms or brackets): GK-R1 one default_rng(%d) per "
             "corpus, draw order components -> ENGINE-SKM / BISECT-GMM-DIAG / BISECT-GMM-FULL / BISECT-SKM / GMM-BIC seed indices; GK-R2 node "
             "seed s x 1000003 + 17 c + 2, replacement slot 9; GK-R3 PCA svd_solver full; GK-R4 fit errors replaced and counted; GK-R5 forced "
             "share = (forced + replaced) / splits; GK-R6 leaf balance = W-3's count" % SEED_BOOT)
    L.append("INTERVAL: percentile bootstrap B %d, crossed (seeds resampled per arm) and paired (EVAL components shared)" % R["B"])
    for leg in LEGS:
        for a in ALL_ARMS:
            fs = R["fits"][leg][a]
            L.append("FITS %s %-15s leaves %s; forced splits %s (of which replaced < 2 child / fit error: %s); rule splits %s; forced share "
                     "%.4f; leaf sizes min %d / median %.1f / max %d; leaves < 10 rows %s; leaves >= 200 rows %s%s" % (
                         leg, a, fs["leaves"], fs["forced"], fs["replaced"] if a in DECIDING else "-", fs["rule"], fs["share"],
                         fs["sizes"][0], fs["sizes"][1], fs["sizes"][2], fs["small"], fs["big"], ARM1_TAG if a == CONTROL else ""))
        for a in DECIDING:
            fs = R["fits"][leg][a]
            nd = fs["nodes"]
            if not fs["has_log"]:
                L.append("GMM NODES %s %-15s n/a (no node log on these fits)" % (leg, a))
                continue
            ps = np.array([g["p"] for g in nd]) if nd else np.zeros(0)
            wm = np.array([g["wmin"] for g in nd if np.isfinite(g["wmin"])])
            L.append("GMM NODES %s %-15s split nodes %d over 5 seeds; convergence failures %d; fit errors %d; replaced (< 2 child) %d; p min %s / "
                     "median %s / max %s, nodes with p < 32: %d; minimum component weight min %s / median %s" % (
                         leg, a, len(nd), sum(1 for g in nd if not g["converged"]), sum(1 for g in nd if g["error"]),
                         sum(1 for g in nd if g["replaced"]), ("%d" % ps.min()) if len(ps) else "n/a", ("%.1f" % np.median(ps)) if len(ps) else "n/a",
                         ("%d" % ps.max()) if len(ps) else "n/a", int((ps < P_FULL).sum()), f5(wm.min() if len(wm) else float("nan"), "%.5f"),
                         f5(float(np.median(wm)) if len(wm) else float("nan"), "%.5f")))
    for c in CORPORA:
        Rc = R["corpora"][c]
        for r in READOUTS:
            for a in ALL_ARMS:
                L.append("READOUT %s %s %-15s per seed %s mean %s%s" % (
                    c, RNAME[r], a, " / ".join(f5(x, "%.5f") for x in Rc["vals"][r][a]), f5(float(np.mean(Rc["vals"][r][a])), "%.5f"),
                    (" spread_1 %s%s" % (f5(Rc["spread"][r], "%.5f"), ARM1_TAG)) if a == CONTROL else
                    (" [descriptive re-print]" if a in REPRINT else "")))
    for (j, r), per in R["stats"].items():
        for c in CORPORA:
            s = per[c]
            L.append("D %s %s %-15s D %s 95%% [%s, %s] spread_1 %s SE %s -> %s%s" % (
                c, RNAME[r], j, f5(s["D"]), f5(s["lo"]), f5(s["hi"]), f5(s["spread"], "%.5f"), f5(s["se"], "%.5f"),
                "CLEARS both conjuncts" if clears(s) else "fails", ARM1_TAG))
    L.append("C-GK (THE ONE DECIDING CRITERION; point AND interval in one clause): %s%s" % (
        R["word"], ("; winning (j, r): " + ", ".join("%s %s" % (j, RNAME[r]) for j, r in R["winners"])) if R["winners"] else ""))
    if R["word"] == "GMM-WINS":
        L.append("FAILS (rule 8): NO-GMM-WINS is refuted by %s (both conjuncts on both corpora)" % ", ".join("%s %s" % (j, r) for j, r in R["winners"]))
        L.append("F-GK FIRES: a fixed-k mixture split beats the engine-like spherical control at matched leaves on both intent corpora by more "
                 "than the control's seed spread; it overturns, for this approximation and these corpora, CONSTRUCTION-ARMS' working reading "
                 "extended to mixtures: the split rule does matter once the mixture is held at k = 2; consequence: a faithful engine GMM split "
                 "(Kotlin knob, site null, certificate) becomes a candidate for a NEW registration with its own go; never an engine change from "
                 "this result")
    else:
        L.append("FAILS (rule 8): GMM-WINS is refuted at the planned n: for every (j, r) at least one corpus fails a conjunct: %s" % "; ".join(
            "%s %s: %s" % (j, r, ", ".join("%s (%s)" % (c, " and ".join(rs)) for c, rs in why)) for (j, r), why in R["fails"].items()))
        L.append("F-GK NOT FIRED (C-GK NO-GMM-WINS; not parity)")
    L.append(WORDS)
    for (j, r), per in R["stats"].items():
        for c in CORPORA:
            if ahead(per[c]):
                L.append("ARM-1-AHEAD (descriptive): %s %s %s (D %s < -spread %s, upper bound %s < 0)%s" % (
                    j, RNAME[r], c, f5(per[c]["D"]), f5(per[c]["spread"], "%.5f"), f5(per[c]["hi"]), ARM1_TAG))
    L += support_lines(R)
    # descriptive
    for c in CORPORA:
        Rc = R["corpora"][c]
        for j in REPRINT:
            for r in READOUTS:
                s = Rc["stats"][(j, r)]
                rec = CA_RECORD_D.get((j, r, c))
                got = f5(s["D"])
                L.append("DESCRIPTIVE RE-PRINT %s %s %-10s vs arm 1: D %s [%s, %s] (this stream); CONSTRUCTION-ARMS' point %s: %s" % (
                    c, RNAME[r], j, got, f5(s["lo"]), f5(s["hi"]), rec, "point REPRODUCED" if got == rec else "point DIFFERS"))
        for (j, k, r), s in Rc["vs"].items():
            L.append("DESCRIPTIVE %s %s %s minus %s: D %s [%s, %s] (same replicates; never in C-GK)" % (c, RNAME[r], j, k, f5(s["D"]), f5(s["lo"]),
                                                                                                    f5(s["hi"])))
        for a in ALL_ARMS:
            L.append("DESCRIPTIVE GR2 %s %-15s common-hierarchy DP vs %d matched-shape random trees: %s" % (c, a, R["n_random"], "; ".join(
                CAR.gr2_text(x["dp"], p, nd) for x, (p, _m, nd) in zip(Rc["fr"][a], Rc["random"][a]))))
            L.append("DESCRIPTIVE (a-own) %s %-15s own-hierarchy DP vs its GR2: %s; children histogram %s; mean leaf depth %s" % (
                c, a, "; ".join(CAR.gr2_text(x["dp_own"], p, nd) for x, (p, _m, nd) in zip(Rc["fr"][a], Rc["random_own"][a])),
                " | ".join(str(x["shape"][0]) for x in Rc["fr"][a]), " / ".join("%.2f" % x["shape"][1] for x in Rc["fr"][a])))
            L.append("DESCRIPTIVE LEAF BALANCE (W-3) %s %-15s fine intents owning a leaf (TRAIN majority) per seed: %s" % (
                c, a, " / ".join("%d of %d" % b for b in Rc["balance"][a])))
        e = Rc["engine"]
        L.append("ENGINE ROW %s (%s, descriptive; filed by leaf vmfMu, L-1): DP_coarse own tree %.5f, on the common hierarchy %.5f, leaf filing "
                 "accuracy %.5f, %d leaves%s" % (c, CAR.ENGINE[c], e["dp"], e["dp_common"], e["fa"], e["L"],
                                                 (", OOS AUROC %.5f" % e["A"]) if "A" in e else ""))
    oo = R["corpora"]["clinc"].get("oos")
    if oo and oo["D"]:
        L.append("DESCRIPTIVE (d) CLINC OOS AUROC (in-scope EVAL %d vs OOS %d): %s" % (oo["n_in"], oo["n_oos"], "; ".join(
            "%s %s" % (a, f5(float(np.mean(oo["A"][a])), "%.5f")) for a in ALL_ARMS)))
        L.append("DESCRIPTIVE (d) D_AUROC vs arm 1 (paired stratified component bootstrap): %s" % "; ".join(
            "%s %s [%s, %s]" % (a, f5(d), f5(oo["ci"][a][0]), f5(oo["ci"][a][1])) for a, d in oo["D"].items()))
    else:
        L.append("DESCRIPTIVE (d) NOT SCORED: no CLINC OOS rows")
    for leg in LEGS:
        T = R["trip"][leg]
        L.append("DESCRIPTIVE (b) %s seed pairs (all-triplets / resolved-in-both [joint both-resolved coverage]; unresolved share): %s" % (
            leg, "; ".join("%s %s / %s [cov %.4f] (unres %.4f)" % (a, f5(T["seed"][a][0], "%.4f"), f5(T["seed"][a][1], "%.4f"), T["seed"][a][2],
                                                                   T["unres"][a]) for a in ALL_ARMS)))
        L.append("DESCRIPTIVE (b) %s 90%%-subsample pairs (all-triplets / resolved-in-both [joint both-resolved coverage]; unresolved share): %s" % (
            leg, "; ".join("%s %s / %s [cov %.4f] (unres %.4f)" % (a, f5(T["sub"][a][0], "%.4f"), f5(T["sub"][a][1], "%.4f"), T["sub"][a][2],
                                                                   T["unres_sub"][a]) for a in ALL_ARMS)))
    M = R["mmlu"]
    L.append("DESCRIPTIVE C leg (MMLU-Pro C |C| %d, L %d, m_min %d; in-sample, DP vs category; no EVAL; pool reader, id-disjoint scope): %s" % (
        M["nC"], M["L"], M["m_min"], "; ".join("%s %s" % (a, " / ".join(f5(x, "%.4f") for x in M["dp"][a])) for a in ALL_ARMS)))
    L.append("DESCRIPTIVE C leg engine rows (flatLeaf on C): %s" % "; ".join("%s DP %.4f (%d leaves)" % (t, v[0], v[1]) for t, v in M["engine"].items()))
    L += prediction_lines(R)
    L.append(NOT_SHOW)
    return L


def prediction_lines(R):
    L = []
    for j in DECIDING:
        for r in READOUTS:
            b = P_BANDS[j][r]
            for c in CORPORA:
                x = R["stats"][(j, r)][c]["D"]
                L.append("%s %s D_%s %s %s in [%+.2f, %+.2f] (point %+.2f): %s" % (P_ID[j], j, r, c, f5(x), b[1], b[2], b[0], band(x, b)))
    win = bool(R["word"] == "GMM-WINS")
    bs = GG.brier(P3_WIN, win)
    L.append("P3 C-GK GMM-WINS %.2f / NO-GMM-WINS %.2f: outcome %s; Brier (p_GMM-WINS - [GMM-WINS])^2 = %.4f (two-outcome sum %.4f)" % (
        P3_WIN, 1 - P3_WIN, R["word"], bs, 2 * bs))
    sh = {(j, c): R["fits"][c][j]["share"] for j in DECIDING for c in CORPORA}
    e4 = all(bool(v <= P4_MAX) for v in sh.values())
    L.append("P4 (descriptive) forced-split share <= %.2f for both new arms on MASSIVE and CLINC: %s (C printed, not scored: %s): %s; Brier "
             "(%.2f - [event])^2 = %.4f" % (P4_MAX, ", ".join("%s %s %.4f" % (j, c, v) for (j, c), v in sh.items()),
                                            ", ".join("%s %.4f" % (j, R["fits"]["mmlu"][j]["share"]) for j in DECIDING),
                                            "TRUE" if e4 else "FALSE", P4_PROB, GG.brier(P4_PROB, e4)))
    d5 = {j: R["stats"][(j, "c")]["clinc"]["D"] for j in DECIDING}
    e5 = all(bool(v > P5_MIN) for v in d5.values())
    L.append("P5 (descriptive) D_c CLINC > %.2f for both new arms: %s: %s; Brier (%.2f - [event])^2 = %.4f" % (
        P5_MIN, ", ".join("%s %s" % (j, f5(v)) for j, v in d5.items()), "TRUE" if e5 else "FALSE", P5_PROB, GG.brier(P5_PROB, e5)))
    d6 = {c: R["corpora"][c]["vs"][(FULL, "BISECT-SKM", "c")]["D"] for c in CORPORA}
    e6 = all(bool(P6_BAND[0] <= v <= P6_BAND[1]) for v in d6.values())
    L.append("P6 (descriptive) BISECT-GMM-FULL minus BISECT-SKM on (c) within [%+.2f, %+.2f] on both corpora: %s: %s; Brier (%.2f - [event])^2 "
             "= %.4f" % (P6_BAND[0], P6_BAND[1], ", ".join("%s %s" % (c, f5(v)) for c, v in d6.items()), "TRUE" if e6 else "FALSE", P6_PROB,
                         GG.brier(P6_PROB, e6)))
    return L


# ================================================================================================ modes
_LOAD = {"world": CAR.load_world, "unlock": CAR.unlock_eval}


def default_out():
    return ZC.default_out("gmm_fixedk", OUTCOME)


def resolve_args(ns, ov=None):
    ov = dict(ov or {})
    mc = CAR.main_checkout()
    a = dict(data_root=os.path.abspath(ns.data_root or os.environ.get("TAXOARENA_DATA_ROOT") or os.path.join(mc, ".claude", "worktrees", "intent-s1-run")),
             mmlu_root=os.path.abspath(ns.mmlu_root or mc), workers=int(ns.workers or 1), out=ns.out or default_out(),
             cfg_root=ZC.ROOT, identity=IDENTITY, arm1_identity=ARM1_ID, B=B_BOOT, n_random=N_RANDOM, triplets=TRIPLETS)
    a.update(ov)
    if a["workers"] < 1 or a["workers"] > MAX_WORKERS:
        refuse("--workers %d outside 1..%d (the author's machine cap)" % (a["workers"], MAX_WORKERS))
    return a


def run(args, out=print):
    path = args["out"]
    sums = os.path.join(os.path.dirname(os.path.abspath(path)), "SHA256SUMS.txt")
    for p in (path, sums):
        if os.path.lexists(p):
            refuse("%s exists: the outcome of record is WRITE-ONCE" % p)
    pins = check_code_pins(args.get("pinned"))
    if not args.get("skip_heavy"):
        S1.check_heavy()
    del S1.FIT_LOG[:]
    meta_lines = []
    world = _LOAD["world"](args, meta_lines, out)
    _LOAD["unlock"](world, out)
    idl = []
    CAR.identity_check(world, args["identity"], idl.append)
    for ln in idl:
        out(ln)
    F = run_fits(world, LEGS, args["workers"], out)
    R = compute(world, F, args["B"], args["n_random"], args["arm1_identity"])
    out(R["id1"])
    Ld = world.get("_Ld")
    if Ld is not None:
        S0.pin_check(Ld["db"], "ingest_db", True, pins_file=args.get("pins_file"), label="ingest (after)")
        S0.pin_check(Ld["emb"], "emb", True, sub="qwen3", pins_file=args.get("pins_file"), label="intent_emb_qwen3.db (after)")
    meta = {"pins": ZC.pins_line(os.path.abspath(__file__)),
            "imports": ["IMPORTS (LF blobs asserted): " + ", ".join("%s blob:%s" % kv for kv in sorted(pins.items()))],
            "pool": list(meta_lines),
            "data": ["DATA: S1 root %s; MMLU root %s" % (args["data_root"], args["mmlu_root"])],
            "census": ["CENSUS %s: EVAL n %d in %d components (Kish %.4f); TRAIN %d; L %d; OOS rows %s" % (
                c, len(world[c]["ev_rows"]), len(np.unique(world[c]["comp"])), S0.kish(world[c]["comp"]), len(world[c]["Xtr"]), world[c]["L"],
                len(world[c]["oos_rows"]) if c == "clinc" else "-") for c in CORPORA] +
                      ["CENSUS mmlu: |C| %d, categories %d (conflicting duplicates %d), L %d" % (
                          world["mmlu"]["nC"], world["mmlu"]["ncat"], world["mmlu"]["nconf"], world["mmlu"]["L"])],
            "mmin": ["m_min (minClusterSize from the build TOMLs; arm 1 only): massive %d, clinc %d, mmlu %d" % (
                world["massive"]["m_min"], world["clinc"]["m_min"], world["mmlu"]["m_min"])] +
                    ["ARM 1 ENGINE KNOBS (from the build TOMLs): %s" % "; ".join(
                        "%s %s" % (leg, CAR.eng_text(dict(CAR.ENGINE_DEFAULTS, **(world[leg].get("eng") or {})))) for leg in LEGS)],
            "audit": ["TRAIN-ONLY fit audit (S1.fit_idx): " + "; ".join("%s %d rows sides %s" % (w, n, "/".join(s)) for w, _c, n, s in S1.FIT_LOG)],
            "identity": idl, "fixture": args.get("fixture")}
    lines = render(R, meta)
    h, _s = ZC.write_once(path, "\n".join(lines) + "\n", TAG)
    for ln in lines:
        out(ln)
    out("%s outcome written: %s (sha256 %s); WRITE-ONCE, never committed" % (TAG, path, h))
    return R, lines, path


def root_timings(Wc):
    X = Wc["Xtr"]
    t = {}
    e = dict(CAR.ENGINE_DEFAULTS, **(Wc.get("eng") or {}))
    t0 = time.time()
    CAR.EngineRule(Wc["m_min"], kmax=e["maxK"]).table(0, X, 0)
    t[CONTROL] = time.time() - t0
    for a, full in ((DIAG, False), (FULL, True)):
        t0 = time.time()
        BisectGmmRule(full).fit(0, X, 0)
        t[a] = time.time() - t0
    t0 = time.time()
    CAR.split_skm2(X, 0)
    t["BISECT-SKM"] = time.time() - t0
    t0 = time.time()
    CAR.GmmRule().table(0, X, CAR.KMAX, 0)
    t["GMM-BIC"] = time.time() - t0
    return t


def cost_estimate(world, workers, out, timings=None):
    tot = 0.0
    for leg in LEGS:
        Wc = world[leg]
        t = timings[leg] if timings else root_timings(Wc)
        lev = math.ceil(math.log2(max(2, Wc["L"]))) + 1
        per = {a: t[a] * lev * 1.5 for a in ALL_ARMS}
        legsum = sum(per[a] * (5 + 5 * CAR.SUB_FRAC) for a in ALL_ARMS)
        tot += legsum
        out("COST %s: n_TRAIN %d, L %d, root timings (s) %s; per fit estimate (s) %s; leg CPU about %.0f s" % (
            leg, len(Wc["Xtr"]), Wc["L"], ", ".join("%s %.2f" % kv for kv in t.items()), ", ".join("%s %.0f" % kv for kv in per.items()), legsum))
    n_fits = len(LEGS) * len(ALL_ARMS) * 10
    readout = 2 * 25 * N_RANDOM * 0.03 * 2 + 2 * 25 * B_BOOT * 0.0005 + 3 * 50 * 2.0
    wall = tot / max(1, min(workers, n_fits)) + readout
    out("COST ESTIMATE: 0 judge / LLM / embedding calls, 0 CCE; %d fits; fits about %.0f CPU-s (%.1f CPU-h) single-threaded; readout (GR2, "
        "bootstrap B %d, triplets) about %.0f s; wall about %.0f min with %d worker(s) (%.0f min with 20)%s" % (
            n_fits, tot, tot / 3600.0, B_BOOT, readout, wall / 60.0, workers, (tot / min(20, n_fits) + readout) / 60.0,
            "; > 100 min: LAUNCH DETACHED (Start-Process) and poll" if wall > 6000 else ""))
    return tot, wall


def dry_run(args, out=print):
    out("%s DRY RUN: zero calls; nothing written; no EVAL row read. %s" % (TAG, REG))
    out(ZC.pins_line(os.path.abspath(__file__)))
    pins = check_code_pins(args.get("pinned"))
    out("IMPORTS (LF blobs asserted): " + ", ".join("%s blob:%s" % kv for kv in sorted(pins.items())))
    if not args.get("skip_heavy"):
        S1.check_heavy()
    world = _LOAD["world"](args, [], out)
    out("I3 |C| = %d (of record %d): OK" % (world["mmlu"]["nC"], args["identity"]["C"]))
    for c in CORPORA:
        out("%s: TRAIN %d rows (EVAL locked), L %d, m_min %d (arm 1), engine %s %d leaves slice %d" % (
            c, len(world[c]["Xtr"]), world[c]["L"], world[c]["m_min"], CAR.ENGINE[c], len(world[c]["T"]["leaves"]), world[c]["T"]["d"]))
    out("mmlu: |C| %d, categories %d, L %d, m_min %d, engine rows %s" % (
        world["mmlu"]["nC"], world["mmlu"]["ncat"], world["mmlu"]["L"], world["mmlu"]["m_min"],
        ", ".join("%s %d leaves" % (t, len(e["leaves"])) for t, e in world["mmlu"]["engines"].items())))
    out("DENOMINATORS (registered, quoted; EVAL locked in the dry run): MASSIVE 4,946 EVAL items / 4,923 components (Kish 1.0093); CLINC "
        "6,672 / 6,672 (Kish 1.0000); x 5 seeds per arm, crossed; B %d; arm-1 identity GK-I0 %s" % (
            args["B"], "; ".join("%s %s %s / %s" % (r, c, v[0], v[1]) for (r, c), v in sorted(args["arm1_identity"].items()))))
    out("ARMS: %s (deciding %s; descriptive re-prints %s); node rules: DIAG k 2 diag reg %.0e n_init %d max_iter %d; FULL k 2 full reg %.0e in "
        "PCA p = %d (rows >= %d) else max(%d, n // %d)" % (", ".join(ALL_ARMS), "/".join(DECIDING), "/".join(REPRINT), REG_DIAG, N_INIT,
                                                          MAX_ITER, REG_FULL, P_FULL, P_ROWS * P_FULL, P_MIN, P_ROWS))
    if bool(S1.STATE.get("gate_frozen")):
        refuse("dry run: EVAL was unlocked (must not happen)")
    cost_estimate(world, args["workers"], out, args.get("timings"))
    out("%s DRY RUN complete: no EVAL row read; 0 files written" % TAG)
    return 0


# ================================================================================================ selftest
SELFTEST_DOC = """SELFTEST (value-asserting; fixtures under scratch_dir on E:):
  U-units: pca_dim at 2 / 19 / 20 / 319 / 320 rows; BisectGmmRule DIAG == an independent sklearn fit with the registered parameters (labels,
  seed, reg, n_init, max_iter, covariance type logged) and beats a spherical mixture on a planted anisotropic pair; FULL == independent
  PCA(svd full) + full mixture, recovers a planted tilted pair (>= 0.99) where diag-in-PCA does not; the < 2 child replacement (a 1-row
  child replaced by split_skm2 at slot 9 and counted by fit_bisect_gmm; a 2-row child kept); fit errors replaced; matched L through the
  real best_first; gk_decide every branch (numpy bools, == boundaries, one corpus, mixed pairs, two winners); bootstrap_means == an
  independent loop on the literal stream and the GK-R1 draw order; arm1_identity both outcomes; prediction lines both events.
  E2E (main(["--run"]) on planted worlds, FITS patched with construction_arms' oracle fits whose (c) is known in closed form):
  G1 GMM-WINS (DIAG (c) named, FULL not; F-GK FIRES; FAILS refuted-by; P4 FALSE by a planted forced share; D, spread, bounds, SE against an
  independent loop); G2 NO-GMM-WINS where the NAIVE item-only interval (seeds fixed) has a lower bound > 0 but the registered crossed one
  does not (checked independently), FULL clears MASSIVE only, P5 / P6 FALSE, ARM-1-AHEAD for FULL on CLINC; G3 lower bound > 0 but D <=
  spread -> NO-GMM-WINS on the spread conjunct (+ the no-OOS skip line); G7 D < -spread with upper bound 0 -> no ARM-1-AHEAD; G8 I1 refusal; G4 DIAG short of L and the control short of L -> REFUSED, nothing written; G5 GK-I0 mismatch ->
  REFUSED, nothing written; G6 write-once refusal before any load. E5 the REAL arms and REAL loaders on construction_arms' on-disk fixture
  roots: I1-I3 and GK-I0 (computed independently by refit + brute-force DP) reproduced, D(a) and D(c) of both new arms == brute force,
  GMM node log printed, dry run writes nothing and never unlocks EVAL, pool == serial fits; refusals: code pin of construction_arms.py,
  workers > 22."""


class _Fail(Exception):
    pass


def _chk(cond, msg):
    if not bool(cond):
        raise _Fail(msg)


def _line(buf, prefix):
    ls = [ln for ln in buf if ln.startswith(prefix)]
    _chk(len(ls) == 1, "expected one line %r, got %d" % (prefix, len(ls)))
    return ls[0]


def _dline(buf, c, r, j):
    ln = _line(buf, "D %s %s %-15s" % (c, RNAME[r], j))
    m = re.search(r"D ([+-]\d\.\d{5}) 95% \[([+-]\d\.\d{5}|n/a), ([+-]\d\.\d{5}|n/a)\] spread_1 (\d\.\d{5}) SE (\d\.\d{5})", ln)
    _chk(m, "unparsed D line %r" % ln)
    return float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), ln


def _acc(F, m):
    return 1.0 - m / float(F)


def _planted_world(n_ev=60, oos=40):
    rng = np.random.default_rng(5)
    W = {"massive": CAR._planted_corpus(rng, "massive", 5, 2, 30, n_ev, 24),
         "clinc": CAR._planted_corpus(rng, "clinc", 6, 2, 30, n_ev, 24, oos=oos)}
    mm = CAR._planted_corpus(rng, "mmlu", 2, 2, 25, 1, 24)
    W["mmlu"] = dict(name="mmlu", nC=len(mm["Xtr"]), C=list(range(len(mm["Xtr"]))), Xtr=mm["Xtr"], cat=(mm["tr_fine"] // 2).astype(np.int64),
                     ncat=2, nconf=0, engines={"t0": dict(parent=mm["T"]["tparent"], leaves=mm["T"]["leaves"], leaf_mu=mm["T"]["leaf_mu"])},
                     L=4, m_min=3)
    for leg in LEGS:
        W[leg]["trip"] = SVK.draw_triplets(len(W[leg]["Xtr"]), 3000, np.random.RandomState(CAR.SEED_TRIP))
    for c in CORPORA:
        W[c]["engine"] = CAR.engine_readout(W[c])
    return W


def _ident1_closed(W, merges):
    """GK-I0 strings for a plant, in closed form: (a) DP 1 (one coarse class), (c) mean 1 - m / F, range (max m - min m) / F."""
    out = {}
    for c in CORPORA:
        F = int(W[c]["ev_fine"].max()) + 1
        ms = merges[c][CONTROL]
        out[("a", c)] = ("1.00000", "0.00000")
        out[("c", c)] = ("%.5f" % np.mean([_acc(F, m) for m in ms]), "%.5f" % ((max(ms) - min(ms)) / float(F)))
    return out


_LOADS = []


def _run_planted(merges, td, tag, forced=None, B=300, ident1=None, oos=40, ident_patch=None):
    W = _planted_world(oos=oos)
    ident = dict(dp_massive="%.5f" % W["massive"]["engine"]["dp"], dp_clinc="%.5f" % W["clinc"]["engine"]["dp"],
                 A_T=("%.5f" % W["clinc"]["engine"]["A"]) if "A" in W["clinc"]["engine"] else "n/a", C=W["mmlu"]["nC"])
    ident.update(ident_patch or {})
    for leg, d in merges.items():
        for arm, m in d.items():
            CAR._ORACLE[(leg, arm)] = dict(merges=m, forced=(forced or {}).get((leg, arm), (0, 1)))
    saved = (dict(FITS), dict(_LOAD))
    FITS.clear()
    for a in ALL_ARMS:
        FITS[a] = functools.partial(CAR._oracle_fit, arm=a)

    def loader(args, ml, out):
        _LOADS.append(tag)
        return W
    _LOAD["world"] = loader
    _LOAD["unlock"] = lambda world, out: None
    try:
        out = os.path.join(td, tag, OUTCOME)
        buf = []
        rc = main(["--run", "--out", out], _ov=dict(B=B, n_random=20, identity=ident, skip_heavy=True, fixture="planted %s" % tag,
                                                    arm1_identity=ident1 if ident1 is not None else _ident1_closed(W, merges)),
                  _out=buf.append)
        return rc, buf, out, W
    finally:
        FITS.clear()
        FITS.update(saved[0])
        _LOAD.clear()
        _LOAD.update(saved[1])


def _corr(g, m):
    """Oracle correctness per EVAL item for m merges: wrong iff the class is a dropped (odd) member of a merged pair."""
    return np.array([not (x < 2 * m and x % 2 == 1) for x in g], dtype=np.float64)


def _indep_boot(W, c, merges, B, pair=(DIAG, CONTROL), naive=False):
    """Independent re-implementation of the registered (c) bootstrap on the literal stream and the GK-R1 order. naive=True: the seeds
    are NOT resampled (item-only interval, the wrong design) -> (lo, hi, sd)."""
    rng = np.random.default_rng(20261006)
    comp = W[c]["comp"]
    _u, cc = np.unique(comp, return_inverse=True)
    G = int(cc.max()) + 1
    g = W[c]["ev_fine"]
    order = ("ENGINE-SKM", "BISECT-GMM-DIAG", "BISECT-GMM-FULL", "BISECT-SKM", "GMM-BIC")
    out = []
    for _b in range(B):
        w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)
        ix = {a: rng.integers(0, 5, size=5) for a in order}
        mean = {}
        for a in pair:
            ms = merges[a]
            pick = range(5) if naive else ix[a]
            mean[a] = np.mean([float((w * _corr(g, ms[s])).sum() / w.sum()) for s in pick])
        out.append(mean[pair[0]] - mean[pair[1]])
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi), float(np.std(out, ddof=1))


def _st_units(ok):
    from sklearn.mixture import GaussianMixture
    from sklearn.decomposition import PCA
    # pca_dim boundaries
    _chk([pca_dim(n) for n in (2, 19, 20, 29, 150, 319, 320, 5000)] == [2, 2, 2, 2, 15, 31, 32, 32], "pca_dim boundaries")
    ok()
    # DIAG rule == independent sklearn fit; logged parameters; beats a spherical mixture on an anisotropic pair
    rng = np.random.default_rng(3)
    n = 300
    A = 0.1 * rng.standard_normal((n, 5))
    Bm = 0.1 * rng.standard_normal((n, 5))
    Bm[:, 0] = 2.0 + rng.standard_normal(n)
    X = np.vstack([A, Bm])
    y = np.r_[np.zeros(n), np.ones(n)]
    rule = BisectGmmRule(False)
    lab = rule(7, X, 2, 3)
    rs = (3 * 1000003 + 17 * 7 + 2) % (2 ** 32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ind = GaussianMixture(2, covariance_type="diag", reg_covar=1e-6, n_init=3, max_iter=200, random_state=rs).fit(X).predict(X)
        sph = GaussianMixture(2, covariance_type="spherical", reg_covar=1e-6, n_init=3, max_iter=200, random_state=rs).fit(X).predict(X)
    lg = rule.log[7]
    _chk(np.array_equal(lab, ind) and lg["rs"] == rs and lg["reg"] == 1e-6 and lg["n_init"] == 3 and lg["max_iter"] == 200 and
         lg["cov_type"] == "diag" and lg["p"] == 5 and lg["zdim"] == 5 and lg["whiten"] is None and not lg["replaced"],
         "DIAG rule == independent fit, parameters logged %s" % lg)
    ok()
    acc_d = max(np.mean(lab == y), np.mean(lab != y))
    acc_s = max(np.mean(sph == y), np.mean(sph != y))
    _chk(acc_d >= acc_s + 0.01 and acc_d > 0.97, "DIAG beats spherical on the anisotropic pair (%.3f vs %.3f)" % (acc_d, acc_s))
    ok()
    # FULL rule == PCA(full) + full mixture; recovers a tilted pair where diag-in-PCA does not
    rng = np.random.default_rng(1)
    n = 200
    u, v = np.array([1.0, 1.0]) / np.sqrt(2), np.array([1.0, -1.0]) / np.sqrt(2)

    def cl(cx):
        return np.array([cx, 0.0]) + rng.normal(0, 2, n)[:, None] * u + rng.normal(0, 0.1, n)[:, None] * v
    X2 = np.vstack([cl(-2.0), cl(2.0)])
    X2 = np.c_[X2, 0.01 * rng.standard_normal((2 * n, 3))]
    y2 = np.r_[np.zeros(n), np.ones(n)]
    rule = BisectGmmRule(True)
    lab = rule(4, X2, 2, 1)
    rs = (1 * 1000003 + 17 * 4 + 2) % (2 ** 32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        Z = PCA(n_components=min(32 if len(X2) >= 320 else max(2, len(X2) // 10), X2.shape[1]), svd_solver="full").fit_transform(X2)
        ind = GaussianMixture(2, covariance_type="full", reg_covar=1e-4, n_init=3, max_iter=200, random_state=rs).fit(Z).predict(Z)
        dg = GaussianMixture(2, covariance_type="diag", reg_covar=1e-4, n_init=3, max_iter=200, random_state=rs).fit(Z[:, :2]).predict(Z[:, :2])
    lg = rule.log[4]
    _chk(np.array_equal(lab, ind) and lg["cov_type"] == "full" and lg["reg"] == 1e-4 and lg["p"] == 5 and lg["rs"] == rs and lg["n_init"] == 3
         and lg["max_iter"] == 200 and lg["whiten"] is False and lg["svd"] == "full" and lg["zdim"] == 5,
         "FULL rule == independent PCA + full mixture, parameters logged %s" % lg)
    ok()
    acc_f = max(np.mean(lab == y2), np.mean(lab != y2))
    acc_g = max(np.mean(dg == y2), np.mean(dg != y2))
    _chk(acc_f >= 0.99 and acc_g < 0.9, "FULL recovers the tilted pair (%.3f) where diag-in-PCA does not (%.3f)" % (acc_f, acc_g))
    ok()
    # FULL at a small node: p = floor(n / 10), minimum 2, logged
    rule = BisectGmmRule(True)
    rule(9, X2[:150], 2, 0)
    rule(10, X2[:12], 2, 0)
    _chk(rule.log[9]["p"] == 5 and rule.log[10]["p"] == 2, "FULL small-node p logged (%d, %d)" % (rule.log[9]["p"], rule.log[10]["p"]))
    ok()
    # FULL in a reducing subspace: d 40, n 150 -> the mixture sees p = 15 coordinates (the PCA projection, not the raw slice)
    X6 = S0.unit(np.random.default_rng(6).standard_normal((150, 40)))
    rule = BisectGmmRule(True)
    rule(2, X6, 2, 0)
    _chk(rule.log[2]["p"] == 15 and rule.log[2]["zdim"] == 15 and not rule.log[2]["error"], "FULL sees the 15-d PCA subspace (%s)" % rule.log[2])
    ok()
    # < 2 child replacement: 40 tight rows + 1 far row -> GMM isolates it -> replaced by split_skm2 at slot 9; a 2-row child is kept
    rng = np.random.default_rng(2)
    base = S0.unit(np.eye(6)[0] + 0.02 * rng.standard_normal((40, 6)))
    far1 = S0.unit(np.eye(6)[3][None, :] + 0.001 * rng.standard_normal((1, 6)))
    X3 = np.vstack([base, far1])
    rule = BisectGmmRule(False)
    lab = rule(5, X3, 2, 0)
    _chk(rule.log[5]["replaced"] and rule.log[5]["sizes"] is not None and min(rule.log[5]["sizes"]) < 2 and
         rule.log[5]["force_seed"] == 17 * 5 + 9 and np.array_equal(lab, CAR.split_skm2(X3, CAR.node_seed(0, 5, 9))),
         "1-row child replaced by the forced split at slot 9 (%s)" % rule.log[5])
    ok()
    far2 = S0.unit(np.eye(6)[3][None, :] + 0.001 * rng.standard_normal((2, 6)))
    X4 = np.vstack([base, far2])
    rule = BisectGmmRule(False)
    lab = rule(5, X4, 2, 0)
    _chk(not rule.log[5]["replaced"] and sorted(rule.log[5]["sizes"]) == [2, 40] and sorted(np.bincount(lab).tolist()) == [2, 40],
         "2-row child kept (%s)" % rule.log[5])
    ok()
    # fit_bisect_gmm counts the replacement as forced (one split at the root, L = 2)
    H = fit_diag(X3, 2, 0)
    H2 = fit_diag(X4, 2, 0)
    _chk(H["nL"] == 2 and H["forced"] == 1 and H["rule_splits"] == 0 and H["replaced"] == 1 and H2["forced"] == 0 and H2["rule_splits"] == 1
         and H2["replaced"] == 0, "replacement counted as forced (H %d/%d, H2 %d/%d)" % (H["forced"], H["rule_splits"], H2["forced"], H2["rule_splits"]))
    ok()
    # the replacement REPLACES the mixture's labels: a fit returning a 1-row child at row 0 (a tight-cluster row) must give way to the
    # forced split (which isolates the far row 40), never be returned as is
    rule = BisectGmmRule(False)
    fake = np.zeros(len(X3), dtype=np.int64)
    fake[0] = 1

    def one_row(c, Xs, seed):
        return fake.copy(), dict(n=len(Xs), p=6, rs=0, cov_type="diag", reg=1e-6, n_init=3, max_iter=200, error=None, converged=True, wmin=0.02)
    rule.fit = one_row
    lab = rule(5, X3, 2, 0)
    fl = CAR.split_skm2(X3, CAR.node_seed(0, 5, 9))
    _chk(rule.log[5]["replaced"] and not np.array_equal(fl, fake) and np.array_equal(lab, fl), "a 1-row child's labels are replaced, not returned")
    ok()
    # a fit error is replaced (GK-R4): a rule whose fit raises
    rule = BisectGmmRule(False)

    def boom(c, Xs, seed):
        return None, dict(n=len(Xs), p=0, rs=0, cov_type="diag", reg=0, n_init=0, max_iter=0, error="ValueError", converged=False, wmin=float("nan"))
    rule.fit = boom
    lab = rule(3, X4, 2, 0)
    _chk(rule.log[3]["replaced"] and lab is not None and np.array_equal(lab, CAR.split_skm2(X4, CAR.node_seed(0, 3, 9))), "fit error replaced")
    ok()
    # matched L through the real best_first; every row in a leaf; the largest leaf split next (sizes non-increasing at the split)
    rng = np.random.default_rng(4)
    X5 = S0.unit(np.vstack([np.eye(8)[i % 8] + 0.2 * rng.standard_normal((25, 8)) for i in range(8)]))
    for fn in (fit_diag, fit_full):
        H = fn(X5, 8, 1)
        _chk(H["nL"] == 8 and len(H["lab"]) == 200 and np.bincount(H["lab"]).min() >= 1 and H["forced"] + H["rule_splits"] == 7 and
             len(H["gmm"]) == H["rule_splits"] + H["replaced"], "%s reaches L = 8" % H["kind"])
        ok()
    # gk_decide: every branch, numpy bools, boundaries
    def S(D, sp, lo):
        return dict(D=np.float64(D), spread=np.float64(sp), lo=np.float64(lo), hi=np.float64(D + 1))

    def stats_of(cells):
        st = {(j, r): {c: S(-1, 0.1, -1) for c in CORPORA} for j in DECIDING for r in READOUTS}
        for (j, r, c), v in cells.items():
            st[(j, r)][c] = S(*v)
        return st
    w, win, fl = gk_decide(stats_of({(DIAG, "c", "massive"): (0.2, 0.1, 0.01), (DIAG, "c", "clinc"): (0.2, 0.1, 0.01)}))
    _chk(w == "GMM-WINS" and win == [(DIAG, "c")] and len(fl) == 3, "gk_decide one winner")
    ok()
    w, win, fl = gk_decide(stats_of({(DIAG, "c", "massive"): (0.2, 0.1, 0.01), (DIAG, "c", "clinc"): (0.2, 0.1, 0.01),
                                     (FULL, "a", "massive"): (0.3, 0.1, 0.02), (FULL, "a", "clinc"): (0.3, 0.1, 0.02)}))
    _chk(w == "GMM-WINS" and win == [(DIAG, "c"), (FULL, "a")], "gk_decide two winners named")
    ok()
    w, win, fl = gk_decide(stats_of({(DIAG, "c", "massive"): (0.2, 0.1, 0.01)}))
    _chk(w == "NO-GMM-WINS" and fl[(DIAG, "c")] == [("clinc", ["D <= spread", "lower bound <= 0"])], "gk_decide one corpus only")
    ok()
    w, win, fl = gk_decide(stats_of({(DIAG, "c", "massive"): (0.1, 0.1, 0.01), (DIAG, "c", "clinc"): (0.2, 0.1, 0.01)}))
    _chk(w == "NO-GMM-WINS" and fl[(DIAG, "c")] == [("massive", ["D <= spread"])], "gk_decide D == spread fails")
    ok()
    w, win, fl = gk_decide(stats_of({(DIAG, "c", "massive"): (0.2, 0.1, 0.0), (DIAG, "c", "clinc"): (0.2, 0.1, 0.01)}))
    _chk(w == "NO-GMM-WINS" and fl[(DIAG, "c")] == [("massive", ["lower bound <= 0"])], "gk_decide lower bound == 0 fails")
    ok()
    w, win, fl = gk_decide(stats_of({(DIAG, "a", "massive"): (0.2, 0.1, 0.01), (FULL, "a", "clinc"): (0.2, 0.1, 0.01),
                                     (DIAG, "c", "clinc"): (0.2, 0.1, 0.01), (FULL, "c", "massive"): (0.2, 0.1, 0.01)}))
    _chk(w == "NO-GMM-WINS" and not win, "gk_decide mixed pairs never combine")
    ok()
    _chk(type(clears(S(0.2, 0.1, 0.01))) is bool and clears(S(0.2, 0.1, 0.01)) is True, "clears returns a python bool")
    ok()
    # bootstrap_means == an independent loop on the literal stream and the GK-R1 order
    rng = np.random.default_rng(9)
    comp = np.repeat(np.arange(30), 2)[:50]
    vals = {r: {a: rng.random(5) + (0.1 * k) for k, a in enumerate(ALL_ARMS)} for r in READOUTS}
    M, Mi = bootstrap_means(lambda w: {r: {a: vals[r][a] * (1 + 0 * w.sum()) for a in ALL_ARMS} for r in READOUTS}, comp, 50, 20261006)
    rr = np.random.default_rng(20261006)
    _u, cc = np.unique(comp, return_inverse=True)
    ok_ = True
    for b in range(50):
        rr.integers(int(cc.max()) + 1, size=int(cc.max()) + 1)
        ix = [rr.integers(0, 5, size=5) for _a in range(5)]
        for k, a in enumerate(("ENGINE-SKM", "BISECT-GMM-DIAG", "BISECT-GMM-FULL", "BISECT-SKM", "GMM-BIC")):
            for r in READOUTS:
                ok_ &= abs(M[(a, r)][b] - vals[r][a][ix[k]].mean()) < 1e-12 and abs(Mi[(a, r)][b] - vals[r][a].mean()) < 1e-12
    _chk(ok_, "bootstrap_means == independent loop (stream, GK-R1 order, item-only means)")
    ok()
    # arm1_identity both outcomes
    Rc = {c: {"vals": {r: {CONTROL: np.array([0.1, 0.2, 0.3, 0.4, 0.5])} for r in READOUTS}} for c in CORPORA}
    good = {(r, c): ("0.30000", "0.40000") for r in READOUTS for c in CORPORA}
    ln, bad = arm1_identity(Rc, good)
    _chk(not bad and ln.endswith("REPRODUCED"), "GK-I0 reproduced")
    ok()
    ln, bad = arm1_identity(Rc, {**good, ("c", "clinc"): ("0.30000", "0.40001")})
    _chk(len(bad) == 1 and ln.endswith("MISMATCH") and "c clinc" in bad[0], "GK-I0 mismatch on the range alone")
    ok()


def _st_predlines(ok):
    def R_of(word, dd, shares, d6):
        st = {(j, r): {c: dict(D=dd[(j, r, c)]) for c in CORPORA} for j in DECIDING for r in READOUTS}
        fits = {leg: {j: dict(share=shares.get((j, leg), 0.0)) for j in DECIDING} for leg in LEGS}
        corp = {c: {"vs": {(FULL, "BISECT-SKM", "c"): dict(D=d6[c])}} for c in CORPORA}
        return dict(word=word, stats=st, fits=fits, corpora=corp)
    dd = {(j, r, c): 0.0 for j in DECIDING for r in READOUTS for c in CORPORA}
    dd[(DIAG, "a", "massive")] = 0.04
    dd[(DIAG, "a", "clinc")] = 0.0401
    dd[(FULL, "c", "clinc")] = -0.06
    L = prediction_lines(R_of("NO-GMM-WINS", dd, {(DIAG, "massive"): 0.10}, {"massive": 0.03, "clinc": -0.03}))
    _chk(_line(L, "P1 BISECT-GMM-DIAG D_a massive").endswith(": HELD") and _line(L, "P1 BISECT-GMM-DIAG D_a clinc").endswith(": FAILED"),
         "P1 closed band at the upper edge")
    ok()
    _chk("outcome NO-GMM-WINS" in _line(L, "P3 ") and "= %.4f (two-outcome sum %.4f)" % (0.05 ** 2, 2 * 0.05 ** 2) in _line(L, "P3 "), "P3 Brier NO")
    ok()
    _chk(": TRUE; Brier (0.75 - [event])^2 = %.4f" % (0.25 ** 2) in _line(L, "P4 "), "P4 TRUE at share == 0.10")
    ok()
    _chk(": FALSE; Brier (0.80 - [event])^2 = %.4f" % (0.8 ** 2) in _line(L, "P5 "), "P5 FALSE at D == -0.06 (strict >)")
    ok()
    _chk(": TRUE; Brier (0.60 - [event])^2 = %.4f" % (0.4 ** 2) in _line(L, "P6 "), "P6 TRUE at the closed edges")
    ok()
    L = prediction_lines(R_of("GMM-WINS", dd, {(FULL, "clinc"): 0.1001}, {"massive": 0.0301, "clinc": 0.0}))
    _chk("outcome GMM-WINS" in _line(L, "P3 ") and "= %.4f" % (0.95 ** 2) in _line(L, "P3 "), "P3 Brier on GMM-WINS")
    ok()
    _chk(": FALSE; Brier" in _line(L, "P4 ") and ": FALSE; Brier" in _line(L, "P6 "), "P4 / P6 FALSE")
    ok()
    L = prediction_lines(R_of("NO-GMM-WINS", {**dd, (FULL, "c", "clinc"): -0.0599}, {(DIAG, "mmlu"): 0.9}, {"massive": 0.0, "clinc": 0.0}))
    _chk(": TRUE; Brier (0.80" in _line(L, "P5 ") and ": TRUE; Brier (0.75" in _line(L, "P4 "), "P5 TRUE; P4 ignores the C leg")
    ok()


def _st_e2e_planted(ok, td):
    KAP = [1, 1, 2, 1, 1]
    # ---- G1: DIAG wins on (c) on both corpora; FULL a clone of arm 1; P4 FALSE (planted forced share 0.2 on massive)
    mer = {leg: {CONTROL: KAP, DIAG: [0] * 5, FULL: KAP, "BISECT-SKM": KAP, "GMM-BIC": KAP} for leg in LEGS}
    rc, buf, out, W = _run_planted(mer, td, "G1", forced={("massive", DIAG): (2, 8)})
    _chk(rc == 0 and os.path.isfile(out), "G1 ran and wrote the outcome (%s)" % buf[-3:])
    ok()
    txt = open(out, encoding="utf-8").read().splitlines()
    for c in CORPORA:
        F = int(W[c]["ev_fine"].max()) + 1
        D, lo, hi, sp, se, ln = _dline(txt, c, "c", DIAG)
        expD = _acc(F, 0) - np.mean([_acc(F, m) for m in KAP])
        _chk(abs(D - expD) < 1e-5 and abs(sp - 1.0 / F) < 1e-5 and ln.endswith("CLEARS both conjuncts" + ARM1_TAG),
             "G1 %s D(c) %.5f vs closed form %.5f; spread %.5f" % (c, D, expD, sp))
        ok()
        elo, ehi, esd = _indep_boot(W, c, mer[c], 300)
        _chk(abs(lo - elo) < 1e-5 and abs(hi - ehi) < 1e-5 and abs(se - esd) < 1e-5 and lo > 0, "G1 %s interval / SE == independent loop" % c)
        ok()
        _nlo, _nhi, nsd = _indep_boot(W, c, mer[c], 300, naive=True)
        si = re.search(r"item-only SD (\d\.\d{5})", _line(txt, "SUPPORT %s c %-15s" % (c, DIAG)))
        _chk(si and abs(float(si.group(1)) - nsd) < 1e-5, "G1 %s item-only SD %s == independent seeds-fixed SD %.5f" % (c, si and si.group(1), nsd))
        ok()
        Df = _dline(txt, c, "c", FULL)[0]
        _chk(abs(Df) < 1e-12, "G1 %s FULL clone D 0" % c)
        ok()
        Da, loa, _h, spa, _s, lna = _dline(txt, c, "a", DIAG)
        _chk(Da == 0 and spa == 0 and lna.endswith("fails" + ARM1_TAG), "G1 %s (a) D 0 fails (one coarse class)" % c)
        ok()
    cg = _line(txt, "C-GK (THE ONE DECIDING CRITERION")
    _chk(cg.split(": ", 1)[1] == "GMM-WINS; winning (j, r): BISECT-GMM-DIAG (c) leaf filing accuracy (fine)", "G1 C-GK GMM-WINS naming DIAG (c): %s" % cg)
    ok()
    _chk(_line(txt, "F-GK ").startswith("F-GK FIRES") and _line(txt, "FAILS (rule 8)").startswith("FAILS (rule 8): NO-GMM-WINS is refuted by "
                                                                                                   "BISECT-GMM-DIAG c"), "G1 F-GK FIRES / FAILS")
    ok()
    _chk(_line(txt, "ARM-1 IDENTITY (GK-I0").endswith("REPRODUCED") and _line(txt, "IDENTITY PRECONDITIONS").endswith("REPRODUCED"), "G1 identities")
    ok()
    p3 = _line(txt, "P3 ")
    _chk("outcome GMM-WINS" in p3 and "= %.4f" % (0.95 ** 2) in p3, "G1 P3 Brier on GMM-WINS")
    ok()
    p4 = _line(txt, "P4 ")
    _chk("BISECT-GMM-DIAG massive 0.2000" in p4 and ": FALSE; Brier" in p4, "G1 P4 FALSE by the planted forced share: %s" % p4)
    ok()
    _chk("forced splits [2, 2, 2, 2, 2]" in _line(txt, "FITS massive BISECT-GMM-DIAG") and "forced share 0.2000" in _line(txt, "FITS massive BISECT-GMM-DIAG"),
         "G1 forced counts printed")
    ok()
    for c in CORPORA:
        F = int(W[c]["ev_fine"].max()) + 1
        x = _acc(F, 0) - np.mean([_acc(F, m) for m in KAP])
        ln = _line(txt, "P1 BISECT-GMM-DIAG D_c %s" % c)
        _chk(("%+.5f" % x) in ln and ln.endswith(GG.band(x, -0.06, 0.04)), "G1 P1 D_c %s by value: %s" % (c, ln))
        ok()
    _chk(": TRUE; Brier" in _line(txt, "P5 "), "G1 P5 TRUE")
    ok()
    _chk(": TRUE; Brier" in _line(txt, "P6 "), "G1 P6 TRUE (FULL == BISECT-SKM)")
    ok()
    for c in CORPORA:
        for j in DECIDING:
            for r in READOUTS:
                sl = _line(txt, "SUPPORT %s %s %-15s" % (c, r, j))
                m_ = re.search(r"SE\(D\) (\d\.\d{5}) .*seed-corrected SE (\d\.\d{5}) .*item-only SD (\d\.\d{5}).*joint (\d\.\d{4}|n/a)", sl)
                _chk(m_, "support line parsed %s" % sl)
                se_, sc_, si_ = float(m_.group(1)), float(m_.group(2)), float(m_.group(3))
                _chk(abs(sc_ - math.sqrt(si_ ** 2 + max(0.0, se_ ** 2 - si_ ** 2) * 1.25)) < 2e-5, "C-2 seed-corrected SE %s %s %s" % (c, r, j))
        ok()
    # realised deciding MDE: per pair max over corpora, min over pairs (recomputed from the printed D lines)
    pair = {}
    for j in DECIDING:
        for r in READOUTS:
            pair[(j, r)] = max(_dline(txt, c, r, j)[3] + 1.25 * _dline(txt, c, r, j)[4] for c in CORPORA)
    for (j, r), v in pair.items():
        pl = _line(txt, "MDE80 PAIR %s %s " % (j, r))
        _chk((") %.4f (registered" % v) in pl, "MDE80 pair %s %s = max over corpora %.4f: %s" % (j, r, v, pl))
    ok()
    mde = _line(txt, "REALISED DECIDING MDE80")
    _chk(("%.4f against" % min(pair.values())) in mde and ("cell %.4f" % max(pair.values())) in mde, "realised MDE80 min-max: %s vs %s" % (mde, pair))
    ok()
    _chk(any(ln.startswith("VERDICT LINE (registered (f))") for ln in txt) and any(ln.startswith("WORDS OF RECORD") and "(vi) BRANCHING" in ln for ln in txt),
         "G1 verdict line and words (vi)")
    ok()
    _chk("point DIFFERS" in _line(txt, "DESCRIPTIVE RE-PRINT massive (c) leaf filing accuracy (fine) BISECT-SKM"), "G1 re-print point check by value")
    ok()
    # (b) by brute-force topology on the oracle fits (control, seed pairs)
    for c in CORPORA:
        Wc = W[c]
        n = len(Wc["Xtr"])
        tp = [CAR._brute_topo(CAR._oracle_fit(Wc["Xtr"], Wc["L"], s, info=dict(leg=c, sub=None), arm=CONTROL), np.arange(n), Wc["trip"]) for s in SEEDS]
        un = np.mean([np.mean(t == 3) for t in tp])
        dis = np.mean([np.mean(tp[i] != tp[k]) for i in range(5) for k in range(i + 1, 5)])
        ln = _line(txt, "DESCRIPTIVE (b) %s seed pairs" % c)
        seg = ln.split("ENGINE-SKM", 1)[1].split(";")[0]
        _chk(dis > 0 and seg.startswith(" %.4f / " % dis) and ("(unres %.4f)" % un) in seg,
             "G1 %s (b) arm-1 seed pairs by brute force (%.4f, %.4f): %s" % (c, dis, un, seg))
        ok()
    del _LOADS[:]
    rc2, buf2, _o, _W = _run_planted(mer, td, "G1")
    _chk(rc2 != 0 and any("WRITE-ONCE" in ln for ln in buf2) and not _LOADS, "G6 write-once refusal BEFORE any read (loads %s)" % _LOADS)
    ok()
    # ---- G2: the naive item-only interval would decide GMM-WINS for DIAG (c); the registered crossed one does not
    K1 = [1] * 5
    mer2 = {leg: {CONTROL: K1, DIAG: [0, 0, 0, 0, 3], FULL: K1, "BISECT-SKM": K1, "GMM-BIC": [3] * 5} for leg in LEGS}
    mer2["massive"][FULL] = [0] * 5
    mer2["clinc"][FULL] = [3] * 5
    rc, buf, out, W = _run_planted(mer2, td, "G2")
    _chk(rc == 0, "G2 ran (%s)" % buf[-3:])
    txt = open(out, encoding="utf-8").read().splitlines()
    for c in CORPORA:
        F = int(W[c]["ev_fine"].max()) + 1
        D, lo, hi, sp, se, ln = _dline(txt, c, "c", DIAG)
        nlo, nhi, _nsd = _indep_boot(W, c, mer2[c], 300, naive=True)
        elo, ehi, _esd = _indep_boot(W, c, mer2[c], 300)
        _chk(abs(D - 0.4 / F) < 1e-5 and sp == 0 and D > sp and nlo > 0 and lo <= 0 and abs(lo - elo) < 1e-5 and ln.endswith("fails" + ARM1_TAG),
             "G2 %s naive lb %.5f > 0 but crossed lb %.5f <= 0 (D %.5f > spread 0)" % (c, nlo, lo, D))
        ok()
    _chk(_line(txt, "C-GK (THE ONE DECIDING CRITERION").endswith(": NO-GMM-WINS") and _line(txt, "F-GK ").startswith("F-GK NOT FIRED"),
         "G2 NO-GMM-WINS, F-GK NOT FIRED")
    ok()
    fl = _line(txt, "FAILS (rule 8)")
    _chk("GMM-WINS is refuted at the planned n" in fl and "BISECT-GMM-DIAG c: massive (lower bound <= 0), clinc (lower bound <= 0)" in fl and
         "BISECT-GMM-FULL c: clinc (D <= spread and lower bound <= 0)" in fl, "G2 FAILS names every (j, r): %s" % fl)
    ok()
    _chk(_dline(txt, "massive", "c", FULL)[5].endswith("CLEARS both conjuncts" + ARM1_TAG), "G2 FULL clears massive only")
    ok()
    _chk(any(ln.startswith("ARM-1-AHEAD (descriptive): BISECT-GMM-FULL (c) leaf filing accuracy (fine) clinc") for ln in txt) and
         not any(ln.startswith("ARM-1-AHEAD (descriptive): BISECT-GMM-DIAG") for ln in txt), "G2 ARM-1-AHEAD for FULL clinc only")
    ok()
    _chk(": FALSE; Brier" in _line(txt, "P5 ") and ": FALSE; Brier" in _line(txt, "P6 ") and ": TRUE; Brier" in _line(txt, "P4 "), "G2 P5 / P6 FALSE, P4 TRUE")
    ok()
    _chk("outcome NO-GMM-WINS" in _line(txt, "P3 ") and ("= %.4f" % (0.05 ** 2)) in _line(txt, "P3 "), "G2 P3 Brier on NO-GMM-WINS")
    ok()
    gm = _line(txt, "DESCRIPTIVE massive (c) leaf filing accuracy (fine) BISECT-GMM-FULL minus GMM-BIC")
    F = int(W["massive"]["ev_fine"].max()) + 1
    _chk(("D %+.5f" % (3.0 / F)) in gm, "G2 descriptive FULL minus GMM-BIC by value: %s" % gm)
    ok()
    # ---- G3: lower bound > 0 but D <= spread
    K4 = [1, 1, 1, 1, 3]
    mer3 = {leg: {CONTROL: K4, DIAG: [0] * 5, FULL: K4, "BISECT-SKM": K4, "GMM-BIC": K4} for leg in LEGS}
    rc, buf, out, W = _run_planted(mer3, td, "G3", oos=0)
    txt = open(out, encoding="utf-8").read().splitlines()
    _chk(_line(txt, "DESCRIPTIVE (d) ") == "DESCRIPTIVE (d) NOT SCORED: no CLINC OOS rows" and "I2 A(C-AF) n/a" in _line(txt, "IDENTITY"),
         "G3 no-OOS skip path printed")
    ok()
    for c in CORPORA:
        F = int(W[c]["ev_fine"].max()) + 1
        D, lo, hi, sp, se, ln = _dline(txt, c, "c", DIAG)
        _chk(lo > 0 and D <= sp and abs(sp - 2.0 / F) < 1e-5 and abs(D - 1.4 / F) < 1e-5, "G3 %s lb > 0, D <= spread" % c)
        ok()
    _chk(_line(txt, "C-GK (THE ONE DECIDING CRITERION").endswith(": NO-GMM-WINS") and
         "BISECT-GMM-DIAG c: massive (D <= spread), clinc (D <= spread)" in _line(txt, "FAILS"), "G3 NO-GMM-WINS on the spread conjunct alone")
    ok()
    # ---- G4: DIAG short of L, then the control short of L
    mer4 = {leg: {CONTROL: KAP, DIAG: [3] * 5, FULL: KAP, "BISECT-SKM": KAP, "GMM-BIC": KAP} for leg in LEGS}
    mer4["massive"][DIAG] = [4] * 5
    rc, buf, out, W = _run_planted(mer4, td, "G4")
    _chk(rc != 0 and not os.path.exists(out) and any("BISECT-GMM-DIAG on massive reached 8 leaves" in ln for ln in buf), "G4 DIAG matched-L refusal")
    ok()
    mer4b = {leg: {CONTROL: [4] * 5, DIAG: KAP, FULL: KAP, "BISECT-SKM": KAP, "GMM-BIC": KAP} for leg in LEGS}
    rc, buf, out, W = _run_planted(mer4b, td, "G4b", ident1={k: ("x", "x") for k in ARM1_ID})
    _chk(rc != 0 and not os.path.exists(out) and any("ENGINE-SKM on massive reached 8 leaves" in ln for ln in buf), "G4 control matched-L refusal")
    ok()
    mer4c = {leg: {CONTROL: KAP, DIAG: KAP, FULL: [4] * 5, "BISECT-SKM": KAP, "GMM-BIC": KAP} for leg in LEGS}
    rc, buf, out, W = _run_planted(mer4c, td, "G4c")
    _chk(rc != 0 and not os.path.exists(out) and any("BISECT-GMM-FULL on massive reached 8 leaves" in ln for ln in buf), "G4 FULL matched-L refusal")
    ok()
    # ---- G7: D < -spread but the upper bound is 0 -> no ARM-1-AHEAD (the interval conjunct of the descriptive flag)
    mer7 = {leg: {CONTROL: [0] * 5, DIAG: [0, 0, 0, 0, 3], FULL: [3] * 5, "BISECT-SKM": [0] * 5, "GMM-BIC": [0] * 5} for leg in LEGS}
    rc, buf, out, W = _run_planted(mer7, td, "G7")
    txt = open(out, encoding="utf-8").read().splitlines()
    D, lo, hi, sp, se, ln = _dline(txt, "massive", "c", DIAG)
    _chk(D < -sp and hi == 0 and not any(x.startswith("ARM-1-AHEAD (descriptive): BISECT-GMM-DIAG") for x in txt) and
         any(x.startswith("ARM-1-AHEAD (descriptive): BISECT-GMM-FULL (c) leaf filing accuracy (fine) massive") for x in txt),
         "G7 ARM-1-AHEAD needs the upper bound < 0 (DIAG D %.5f, hi %.5f)" % (D, hi))
    ok()
    # ---- G8: I1 mismatch -> REFUSED through construction_arms.identity_check, nothing written
    rc, buf, out, W = _run_planted(mer, td, "G8", ident_patch=dict(dp_massive="0.00000"))
    _chk(rc != 0 and not os.path.exists(out) and any("IDENTITY PRECONDITION FAILED" in x and "I1" in x for x in buf), "G8 I1 refusal")
    ok()
    # ---- G5: GK-I0 mismatch (the range of (c) clinc off by one in the 5th digit)
    W0 = _planted_world()
    bad = _ident1_closed(W0, mer)
    v = bad[("c", "clinc")]
    bad[("c", "clinc")] = (v[0], "%.5f" % (float(v[1]) + 1e-5))
    rc, buf, out, W = _run_planted(mer, td, "G5", ident1=bad)
    _chk(rc != 0 and not os.path.exists(out) and any("GK-I0 FAILED" in ln and "c clinc" in ln for ln in buf), "G5 GK-I0 refusal, nothing written")
    ok()


def _st_e2e_real(ok, td):
    saved_n = dict(GG.REGISTERED_N)
    try:
        fx = CAR._fx_intent_root(os.path.join(td, "s1"))
        for k_ in CORPORA:
            GG.REGISTERED_N[k_] = fx["census"][k_]
        mctx, cfg = CAR._fx_mmlu_root(os.path.join(td, "mm"))
        Ld = GG.load_all(fx["root"], fx["pins"], os.path.join(fx["root"], "snapshots.db"), out=lambda s: None)
        Rg = GG.compute(Ld, boot_b=5, n_random=3, out=lambda s: None)
        Cc = fx["CS"]["clinc"]
        T = Ld["trees"]["C-AF"][0]
        ins = np.nonzero(Cc.kept & ~Cc.oos & (Cc.side == SPL.EVAL))[0]
        oos = np.nonzero(Cc.kept & Cc.oos & (Cc.side == SPL.EVAL))[0]

        def vx(i):
            return S0.unit(np.array([fx["vecs"][Cc.text[i]][:8]], dtype=np.float64))[0]
        a_t = S0.auroc([float(np.max(T["leaf_mu"] @ vx(i))) for i in ins], [float(np.max(T["leaf_mu"] @ vx(i))) for i in oos])
        ident = dict(dp_massive="%.5f" % Rg["corpora"]["massive"]["dp_tree"], dp_clinc="%.5f" % Rg["corpora"]["clinc"]["dp_tree"],
                     A_T="%.5f" % a_t, C=SVK.NC_FIX)
        ov = dict(B=60, n_random=5, triplets=2000, identity=ident, skip_heavy=True, fixture="real-arms fixture roots", dim=8,
                  L={"massive": fx["leaves"]["massive"], "clinc": fx["leaves"]["clinc"], "mmlu": 6}, svk_ctx=mctx, ss_ctx=mctx.ss,
                  cfg_root=cfg, pins_file=fx["pins"])
        argv = ["--data-root", fx["root"], "--mmlu-root", os.path.join(td, "mm")]
        # independent world + brute-force scoring of every arm needed (refits are deterministic)
        world = CAR.load_world(dict(resolve_args(_ns(["--run"] + argv), ov)), [], lambda s: None)
        CAR.unlock_eval(world, lambda s: None)
        from scipy.cluster.hierarchy import linkage as _lk
        brute = {}
        for c in CORPORA:
            Wc = world[c]
            for a, fn in ((CONTROL, CAR.fit_engine), (DIAG, fit_diag), (FULL, fit_full)):
                va, vc = [], []
                for s in SEEDS:
                    H = fn(Wc["Xtr"], Wc["L"], s, Wc["m_min"], dict(eng=Wc.get("eng")))
                    mu = np.vstack([Wc["Xtr"][H["lab"] == j].mean(0) for j in range(H["nL"])])
                    mu = mu / np.linalg.norm(mu, axis=1, keepdims=True)
                    fl = np.argmax(Wc["Xev"] @ mu.T, axis=1)
                    Z = _lk(mu, method="ward")
                    nm = ["x%d" % j for j in range(H["nL"])] + ["z%d" % t for t in range(H["nL"] - 1)]
                    par = {}
                    for t, row in enumerate(Z):
                        par[nm[int(row[0])]] = nm[H["nL"] + t]
                        par[nm[int(row[1])]] = nm[H["nL"] + t]
                    va.append(CAR._brute_dp(par, nm[:H["nL"]], [nm[j] for j in fl], list(Wc["ev_coarse"])))
                    maj = []
                    for j in range(H["nL"]):
                        cnt = collections.Counter(Wc["tr_fine"][H["lab"] == j].tolist())
                        top = max(cnt.values())
                        maj.append(min(k for k, v in cnt.items() if v == top))
                    vc.append(float(np.mean([maj[f] == g for f, g in zip(fl, Wc["ev_fine"])])))
                brute[(c, a)] = (np.array(va), np.array(vc))
        ident1 = {}
        for c in CORPORA:
            va, vc = brute[(c, CONTROL)]
            ident1[("a", c)] = ("%.5f" % va.mean(), "%.5f" % (va.max() - va.min()))
            ident1[("c", c)] = ("%.5f" % vc.mean(), "%.5f" % (vc.max() - vc.min()))
        ov["arm1_identity"] = ident1
        # dry run: writes nothing, never unlocks EVAL, pool line before the intent census, cost printed
        buf = []
        before = set(os.listdir(td))
        S1.STATE["gate_frozen"] = False
        rc = main(["--dry-run"] + argv, _ov=dict(ov, timings={leg: {a: 0.01 for a in ALL_ARMS} for leg in LEGS}), _out=buf.append)
        _chk(rc == 0 and set(os.listdir(td)) == before and not S1.STATE["gate_frozen"], "dry run: 0 files, EVAL locked (%s)" % buf[-3:])
        ok()
        _chk(any(ln.startswith("COST ESTIMATE: 0 judge") for ln in buf) and any(ln.startswith("POOL READER") for ln in buf) and
             any(ln.startswith("DENOMINATORS (registered") for ln in buf), "dry run cost + pool + denominators")
        ok()
        pidx = [i for i, ln in enumerate(buf) if ln.startswith("POOL READER")][0]
        cidx = [i for i, ln in enumerate(buf) if "census" in ln][0]
        _chk(pidx < cidx, "dry run: the pool line precedes the intent loading")
        ok()
        buf = []
        rc = main(["--dry-run"] + argv, _ov=ov, _out=buf.append)
        _chk(rc == 0 and len([ln for ln in buf if ln.startswith("COST ")]) == 4, "dry run with live root timings of the five arms")
        ok()
        out = os.path.join(td, "E5", OUTCOME)
        buf = []
        rc = main(["--run", "--out", out] + argv, _ov=ov, _out=buf.append)
        _chk(rc == 0 and os.path.isfile(out), "E5 real arms ran (rc %r): %s" % (rc, buf[-4:]))
        ok()
        txt = open(out, encoding="utf-8").read().splitlines()
        _chk(_line(txt, "IDENTITY PRECONDITIONS").endswith("REPRODUCED") and _line(txt, "ARM-1 IDENTITY (GK-I0").endswith("REPRODUCED"),
             "E5 I1-I3 and GK-I0 (brute force) reproduced through the real loaders")
        ok()
        for c in CORPORA:
            for j in DECIDING:
                for r, k in (("a", 0), ("c", 1)):
                    D, _lo, _hi, sp, _se, _ln = _dline(txt, c, r, j)
                    eD = brute[(c, j)][k].mean() - brute[(c, CONTROL)][k].mean()
                    esp = brute[(c, CONTROL)][k].max() - brute[(c, CONTROL)][k].min()
                    _chk(abs(D - eD) < 1e-5 and abs(sp - esp) < 1e-5, "E5 %s %s %s D %.5f == brute %.5f; spread %.5f == %.5f" % (c, r, j, D, eD, sp, esp))
            ok()
        g = _line(txt, "GMM NODES massive BISECT-GMM-FULL")
        m_ = re.search(r"split nodes (\d+) .*p min (\d+) / median [\d.]+ / max (\d+), nodes with p < 32: (\d+)", g)
        _chk(m_ and int(m_.group(1)) > 0 and int(m_.group(3)) < 32 and int(m_.group(4)) == int(m_.group(1)), "E5 FULL node log (small nodes, p < 32): %s" % g)
        ok()
        gd = _line(txt, "GMM NODES clinc BISECT-GMM-DIAG")
        _chk(re.search(r"p min 8 / median 8\.0 / max 8", gd), "E5 DIAG node log p = the slice (8): %s" % gd)
        ok()
        w = _line(txt, "C-GK (THE ONE DECIDING CRITERION").split(": ", 1)[1]
        _chk(w.startswith("GMM-WINS") or w == "NO-GMM-WINS", "E5 one of the two words")
        ok()
        # the process pool equals the serial fits (real rules)
        F1 = run_fits({"mmlu": world["mmlu"]}, ("mmlu",), 1, lambda s: None)
        F2 = run_fits({"mmlu": world["mmlu"]}, ("mmlu",), 2, lambda s: None)
        _chk(all(np.array_equal(F1[k]["lab"], F2[k]["lab"]) and F1[k]["parent"] == F2[k]["parent"] for k in F1), "pool == serial fits")
        ok()
        b5 = []
        rc = main(["--run", "--out", os.path.join(td, "RP", OUTCOME)] + argv, _ov=dict(ov, pinned=dict(PINNED_CODE, **{"construction_arms.py": "0" * 40})),
                  _out=b5.append)
        _chk(rc != 0 and any("construction_arms.py" in ln and "instrument of record" in ln for ln in b5) and not os.path.exists(os.path.join(td, "RP")),
             "code pin refusal (construction_arms.py)")
        ok()
        b6 = []
        rc = main(["--run", "--workers", "23", "--out", os.path.join(td, "RW", OUTCOME)] + argv, _ov=ov, _out=b6.append)
        _chk(rc != 0 and any("machine cap" in ln for ln in b6), "workers > 22 refusal")
        ok()
        _chk(check_code_pins()["construction_arms.py"] == CAR_BLOB, "construction_arms.py is blob:5d08a5df")
        ok()
    finally:
        GG.REGISTERED_N.clear()
        GG.REGISTERED_N.update(saved_n)
        S1.STATE["gate_frozen"] = False


def _ns(argv):
    return build_parser().parse_args(argv)


def selftest():
    n = [0]

    def ok():
        n[0] += 1
    t0 = time.time()
    with scratch_dir.scratch("gmm_fixedk_st") as td:
        try:
            _st_units(ok)
            _st_predlines(ok)
            _st_e2e_planted(ok, td)
            _st_e2e_real(ok, td)
        except _Fail as e:
            print("%s SELFTEST FAILED after %d checks: %s" % (TAG, n[0], e))
            return 1
    print("%s SELFTEST OK: %d value checks in %.1f s" % (TAG, n[0], time.time() - t0))
    return 0


# ================================================================================================ mutants (sandbox copies only)
MUTANTS = [
    ("M01", "C-GK on either corpus (any)", "            ok = [clears(per[c]) for c in CORPORA]\n            if all(ok):",
     "            ok = [clears(per[c]) for c in CORPORA]\n            if any(ok):"),
    ("M02", "C-GK D >= spread", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] >= s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead"),
    ("M03", "C-GK lower bound >= 0", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] >= 0)\n\n\ndef ahead"),
    ("M04", "C-GK spread conjunct dropped", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] > 0) and bool(s[\"lo\"] > 0)\n\n\ndef ahead"),
    ("M05", "C-GK interval conjunct dropped", "    return bool(s[\"D\"] > s[\"spread\"]) and bool(s[\"lo\"] > 0)\n\n\ndef ahead",
     "    return bool(s[\"D\"] > s[\"spread\"])\n\n\ndef ahead"),
    ("M06", "C-GK first winner only", "                winners.append((j, r))\n", "                winners.append((j, r)) if not winners else None\n"),
    ("M07", "C-GK deciding set DIAG only", "DECIDING = (DIAG, FULL)", "DECIDING = (DIAG,)"),
    ("M08", "D sign flipped", "    D = float(vj.mean() - vk.mean())", "    D = float(vk.mean() - vj.mean())"),
    ("M09", "spread = SD", "                spread={r: CAR.spread5(vals[r][CONTROL]) for r in READOUTS})",
     "                spread={r: float(np.std(vals[r][CONTROL], ddof=1)) for r in READOUTS})"),
    ("M10", "spread from the deciding arm (wrong population)", "                spread={r: CAR.spread5(vals[r][CONTROL]) for r in READOUTS})",
     "                spread={r: CAR.spread5(vals[r][DIAG]) for r in READOUTS})"),
    ("M11", "seeds paired (arm j reuses arm 1's draw)", "                M[(a, r)][b] = float(v[r][a][idx[a]].mean())",
     "                M[(a, r)][b] = float(v[r][a][idx[CONTROL]].mean())"),
    ("M12", "seeds not resampled (naive item-only interval)", "                M[(a, r)][b] = float(v[r][a][idx[a]].mean())",
     "                M[(a, r)][b] = float(v[r][a].mean())"),
    ("M13", "components not resampled", "        w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)\n        idx",
     "        w = np.ones(len(cc)) + 0 * np.bincount(rng.integers(G, size=G), minlength=G)[cc]\n        idx"),
    ("M14", "bootstrap seed + 1", "SEED_BOOT = 20261006", "SEED_BOOT = 20261007"),
    ("M15", "seed draw order (FULL before DIAG)", "SEED_DRAWS = (CONTROL, DIAG, FULL, \"BISECT-SKM\", \"GMM-BIC\")",
     "SEED_DRAWS = (CONTROL, FULL, DIAG, \"BISECT-SKM\", \"GMM-BIC\")"),
    ("M16", "item-only SD from the crossed replicates", "    se, si = CAR.sd1(x), CAR.sd1(Mi[(j, r)] - Mi[(k, r)])",
     "    se, si = CAR.sd1(x), CAR.sd1(x)"),
    ("M17", "DIAG covariance spherical", "            gm = GaussianMixture(n_components=K_GMM, covariance_type=\"diag\"",
     "            gm = GaussianMixture(n_components=K_GMM, covariance_type=\"spherical\""),
    ("M18", "FULL covariance diag (in PCA)", "            gm = GaussianMixture(n_components=K_GMM, covariance_type=\"full\"",
     "            gm = GaussianMixture(n_components=K_GMM, covariance_type=\"diag\""),
    ("M19", "DIAG reg_covar 1e-4", "REG_DIAG = 1e-6", "REG_DIAG = 1e-4"),
    ("M20", "FULL reg_covar 1e-6", "REG_FULL = 1e-4", "REG_FULL = 1e-6"),
    ("M21", "n_init 1", "N_INIT = 3", "N_INIT = 1"),
    ("M22", "max_iter 100", "MAX_ITER = 200", "MAX_ITER = 100"),
    ("M23", "PCA p 64", "P_FULL = 32", "P_FULL = 64"),
    ("M24", "PCA min p 1", "P_MIN = 2", "P_MIN = 1"),
    ("M25", "PCA small-node p without the /10", "    return P_FULL if n >= P_ROWS * P_FULL else max(P_MIN, n // P_ROWS)",
     "    return P_FULL if n >= P_ROWS * P_FULL else max(P_MIN, min(n, P_FULL))"),
    ("M26", "PCA whitened", "            pca = PCA(n_components=p, whiten=False, svd_solver=\"full\")",
     "            pca = PCA(n_components=p, whiten=True, svd_solver=\"full\")"),
    ("M27", "FULL without PCA (raw slice)", "            Z = pca.fit_transform(Xs)", "            Z = Xs"),
    ("M66", "PCA svd_solver auto (randomised on large nodes)", "            pca = PCA(n_components=p, whiten=False, svd_solver=\"full\")",
     "            pca = PCA(n_components=p, whiten=False, svd_solver=\"auto\")"),
    ("M67", "no-OOS skip line dropped", "        L.append(\"DESCRIPTIVE (d) NOT SCORED: no CLINC OOS rows\")", "        pass"),
    ("M68", "p not capped at the slice dimension", "            p = min(pca_dim(n), Xs.shape[1])", "            p = pca_dim(n)"),
    ("M28", "replacement threshold < 3", "MIN_CHILD = 2", "MIN_CHILD = 3"),
    ("M29", "replacement threshold < 1 (empty child only)", "MIN_CHILD = 2", "MIN_CHILD = 1"),
    ("M30", "replacement not counted as forced", "    H[\"forced\"] += nrep\n", "    H[\"forced\"] += 0\n"),
    ("M31", "replacement seed slot k instead of 9", "        fs = CAR.node_seed(seed, c, CAR.FORCE_SLOT)", "        fs = CAR.node_seed(seed, c, K_GMM)"),
    ("M32", "node seed k = 1", "        rs = CAR.node_seed(seed, c, K_GMM) % (2 ** 32)", "        rs = CAR.node_seed(seed, c, 1) % (2 ** 32)"),
    ("M33", "fit error not replaced (None returned)", "        rep = bool(lab is None or int(sizes.min()) < MIN_CHILD)",
     "        rep = bool(lab is not None and int(sizes.min()) < MIN_CHILD)"),
    ("M34", "GK-I0 not refused", "    if bad:\n        print(idline)\n        refuse(", "    if False:\n        print(idline)\n        refuse("),
    ("M35", "GK-I0 range not compared", "            if got != want:", "            if got[0] != want[0]:"),
    ("M36", "I1-I3 identity check skipped", "    CAR.identity_check(world, args[\"identity\"], idl.append)", "    pass"),
    ("M37", "write-once pre-check dropped", "        if os.path.lexists(p):\n            refuse(\"%s exists: the outcome of record is WRITE-ONCE\" % p)",
     "        if False:\n            refuse(\"%s exists: the outcome of record is WRITE-ONCE\" % p)"),
    ("M38", "matched-L refusal for the deciding arms dropped", "    for a in (CONTROL,) + DECIDING:\n        for x in fr[a]:",
     "    for a in (CONTROL,):\n        for x in fr[a]:"),
    ("M39", "matched-L refusal for the control dropped", "    for a in (CONTROL,) + DECIDING:\n        for x in fr[a]:",
     "    for a in DECIDING:\n        for x in fr[a]:"),
    ("M40", "F-GK FIRES unprinted", "        L.append(\"F-GK FIRES: a fixed-k", "        0 and L.append(\"F-GK FIRES: a fixed-k"),
    ("M41", "FAILS unprinted on NO-GMM-WINS", "        L.append(\"FAILS (rule 8): GMM-WINS is refuted", "        0 and L.append(\"FAILS (rule 8): GMM-WINS is refuted"),
    ("M42", "F-GK NOT FIRED unprinted", "        L.append(\"F-GK NOT FIRED", "        0 and L.append(\"F-GK NOT FIRED"),
    ("M43", "P3 Brier on the wrong event", "    bs = GG.brier(P3_WIN, win)", "    bs = GG.brier(P3_WIN, not win)"),
    ("M44", "bands open", "    return GG.band(x, b[1], b[2])", "    return \"HELD\" if (b[1] < x < b[2]) else \"FAILED\""),
    ("M45", "P4 strict <", "    e4 = all(bool(v <= P4_MAX) for v in sh.values())", "    e4 = all(bool(v < P4_MAX) for v in sh.values())"),
    ("M46", "P5 >=", "    e5 = all(bool(v > P5_MIN) for v in d5.values())", "    e5 = all(bool(v >= P5_MIN) for v in d5.values())"),
    ("M47", "P5 on MASSIVE (wrong corpus)", "    d5 = {j: R[\"stats\"][(j, \"c\")][\"clinc\"][\"D\"] for j in DECIDING}",
     "    d5 = {j: R[\"stats\"][(j, \"c\")][\"massive\"][\"D\"] for j in DECIDING}"),
    ("M48", "P6 any corpus", "    e6 = all(bool(P6_BAND[0] <= v <= P6_BAND[1]) for v in d6.values())",
     "    e6 = any(bool(P6_BAND[0] <= v <= P6_BAND[1]) for v in d6.values())"),
    ("M49", "P4 scores the C leg", "    sh = {(j, c): R[\"fits\"][c][j][\"share\"] for j in DECIDING for c in CORPORA}",
     "    sh = {(j, c): R[\"fits\"][c][j][\"share\"] for j in DECIDING for c in LEGS}"),
    ("M50", "realised MDE max instead of min over pairs", "    dec = min(pair.values())", "    dec = max(pair.values())"),
    ("M51", "MDE pair min over corpora", "            pair[(j, r)] = max(mj)", "            pair[(j, r)] = min(mj)"),
    ("M52", "joint MDE z 0.84", "                mdej = s[\"spread\"] + 1.25 * s[\"se\"]", "                mdej = s[\"spread\"] + 0.84 * s[\"se\"]"),
    ("M53", "seed correction 1.0", "SEED_CORR = len(SEEDS) / float(len(SEEDS) - 1)", "SEED_CORR = 1.0"),
    ("M54", "percentiles 5 / 95 (through pct: contrast uses its own)", "    lo, hi = CAR.pct(x)", "    lo, hi = (lambda q: (float(q[0]), float(q[1])))(np.percentile(x, [5, 95]))"),
    ("M55", "ARM-1-AHEAD without the interval", "    return bool(s[\"D\"] < -s[\"spread\"]) and bool(s[\"hi\"] < 0)", "    return bool(s[\"D\"] < -s[\"spread\"])"),
    ("M56", "workers cap removed", "    if a[\"workers\"] < 1 or a[\"workers\"] > MAX_WORKERS:", "    if a[\"workers\"] < 1:"),
    ("M57", "code pins unchecked", "        if b != want:\n            refuse(\"%s is blob:%s", "        if False:\n            refuse(\"%s is blob:%s"),
    ("M58", "dry run unlocks EVAL", "    if bool(S1.STATE.get(\"gate_frozen\")):\n        refuse(\"dry run", "    _LOAD[\"unlock\"](world, out)\n    if False:\n        refuse(\"dry run"),
    ("M59", "arms fitted on EVAL (wrong split side)", "        X, L, mm = Wc[\"Xtr\"], Wc[\"L\"], Wc[\"m_min\"]",
     "        X, L, mm = Wc.get(\"Xev\", Wc[\"Xtr\"]), Wc[\"L\"], Wc[\"m_min\"]"),
    ("M60", "support on the first corpus only", "            for c in CORPORA:\n                Rc = R[\"corpora\"][c]\n                s = Rc[\"stats\"][(j, r)]",
     "            for c in CORPORA[:1]:\n                Rc = R[\"corpora\"][c]\n                s = Rc[\"stats\"][(j, r)]"),
    ("M61", "(b) seed pairs first pair only", "        prs = [CAR.conv(tp[i], tp[k]) for i in range(5) for k in range(i + 1, 5)]",
     "        prs = [CAR.conv(tp[i], tp[k]) for i in range(5) for k in range(i + 1, 5)][:1]"),
    ("M62", "(b) unresolved share = topology 0", "        out[\"unres\"][a] = float(np.mean([np.mean(t == 3) for t in tp]))",
     "        out[\"unres\"][a] = float(np.mean([np.mean(t == 0) for t in tp]))"),
    ("M63", "P6 vs GMM-BIC (wrong comparator)", "    d6 = {c: R[\"corpora\"][c][\"vs\"][(FULL, \"BISECT-SKM\", \"c\")][\"D\"] for c in CORPORA}",
     "    d6 = {c: R[\"corpora\"][c][\"vs\"][(FULL, \"GMM-BIC\", \"c\")][\"D\"] for c in CORPORA}"),
    ("M64", "contrast vs arm 1 uses GMM-BIC as control", "    Rc[\"stats\"] = {(j, r): contrast(vals, M, Mi, r, j, CONTROL, Rc[\"spread\"][r])",
     "    Rc[\"stats\"] = {(j, r): contrast(vals, M, Mi, r, j, \"GMM-BIC\", Rc[\"spread\"][r])"),
    ("M65", "replacement accepted when GMM gives a 1-row child (no replace)", "        if rep:\n            lab = CAR.split_skm2(",
     "        if rep and lab is None:\n            lab = CAR.split_skm2("),
]


def run_mutants(jobs=8, out=print):
    """Every mutant: a copy of this script with one replacement (above the MUTANTS list only) in a scratch sandbox (TMP / TEMP / TMPDIR /
    TAXOARENA_TMP inside it), its --selftest run in a subprocess; KILLED iff rc != 0. The no-op control C0 must SURVIVE."""
    from concurrent.futures import ThreadPoolExecutor
    me = os.path.abspath(__file__)
    src = open(me, encoding="utf-8").read()
    cut = src.index("\nMUTANTS = [")
    head, rest = src[:cut], src[cut:]
    allm = [("C0", "no-op control (must survive)", "TAG = \"[GMM-FIXEDK]\"", "TAG = \"[GMM-FIXEDK]\"")] + MUTANTS
    res = {}
    with scratch_dir.scratch("gmm_fixedk_mutants") as box:
        def one(m):
            mid, desc, old, new = m
            cnt = head.count(old)
            if cnt != 1:
                return mid, desc, "NOT APPLIED (%d occurrences)" % cnt, ""
            d = os.path.join(box, mid)
            os.makedirs(os.path.join(d, "tmp"))
            p = os.path.join(d, os.path.basename(me))
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(head.replace(old, new) + rest)
            env = dict(os.environ)
            env["PYTHONPATH"] = HERE + os.pathsep + env.get("PYTHONPATH", "")
            env["ZC_REPO_ROOT"] = ZC.ROOT
            for v in ("TMP", "TEMP", "TMPDIR", "TAXOARENA_TMP"):
                env[v] = os.path.join(d, "tmp")
            try:
                cp = subprocess.run([sys.executable, p, "--selftest"], env=env, capture_output=True, text=True, timeout=3600,
                                    encoding="utf-8", errors="replace")
                rc, tail = cp.returncode, ((cp.stdout + cp.stderr).strip().splitlines() or [""])[-1]
            except subprocess.TimeoutExpired:
                rc, tail = "timeout", "timeout"
            return mid, desc, ("killed" if rc != 0 else "SURVIVED"), tail[:150]
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            for mid, desc, v, tail in ex.map(one, allm):
                res[mid] = (desc, v, tail)
                out("  %-4s %-62s %s  (%s)" % (mid, desc[:62], v, tail[:110]))
    k = sum(1 for m in MUTANTS if res[m[0]][1] == "killed")
    out("MUTANTS: %d / %d killed; control C0 %s" % (k, len(MUTANTS), res["C0"][1]))
    return 0 if (k == len(MUTANTS) and res["C0"][1] == "SURVIVED") else 1


# ================================================================================================ main
def build_parser():
    ap = argparse.ArgumentParser(description="GMM-FIXEDK readout (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--data-root")
    ap.add_argument("--mmlu-root")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=8)
    return ap


def main(argv=None, _ov=None, _out=None):
    ns = build_parser().parse_args(argv)
    if ns.selftest:
        return selftest()
    if ns.mutants:
        return run_mutants(ns.jobs)
    if _out is None:
        args = resolve_args(ns, _ov)
        if ns.dry_run:
            return dry_run(args)
        run(args)
        return 0
    buf = io.StringIO()
    rc = 0
    with contextlib.redirect_stdout(buf):
        try:
            args = resolve_args(ns, _ov)
            if ns.dry_run:
                rc = dry_run(args, _out)
            else:
                run(args, _out)
        except SystemExit as e:
            _out("%s REFUSED (exit): %s" % (TAG, e))
            rc = 2
    for ln in buf.getvalue().splitlines():
        _out(ln)
    return rc


if __name__ == "__main__":
    sys.exit(main())
