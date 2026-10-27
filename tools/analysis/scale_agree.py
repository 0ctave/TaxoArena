"""SCALE-AGREE readout (docs/judge_v2_program.md, "## Registered 2026-10-04 (before any code or call) -- SCALE-AGREE: do embedders
agree at coarse k and diverge at fine k, label-free, with each pair's agreement curve scaled by the qwen3 q4-vs-q8 copy?",
L24375-L24386, registration commit 633255f2; docs/agents/results/SCALE-AGREE.json). ZERO LLM calls; CPU only; labels never read
(SC2 compares k* with the gold class COUNTS only, constants below).

POOL: the intent arms (--run, the readout of record) read NO pool: the six intent_emb_*.db and intent_transfer_corpora_v1.db only
(rule 7 does not bind). The MMLU-Pro arm (--mmlu, DESCRIPTIVE, its own write-once file) IS A POOL READER under rule 7 (it reads
embeddings_cache.db); run it in a pool slot only.

LAUNCH SEQUENCE (zero calls; temp only under E: via scratch_dir; every DB is COPIED (db + -wal) into the process's scratch dir
before it is read: zc_common.stage_db):
  python tools/analysis/scale_agree.py --selftest          # fixture worlds; value-asserting; independent recomputation
  python tools/analysis/scale_agree.py --mutants           # the mutant table (copies in a sandbox; the file is never edited)
  python tools/analysis/scale_agree.py --dry-run           # pins, staged copies, census, a timed k = 256 fit, price
  python tools/analysis/scale_agree.py --run               # the readout of record (intent arms); WRITE-ONCE outcome on E:
  python tools/analysis/scale_agree.py --dry-run --mmlu    # MMLU-Pro descriptive arm (POOL READER)
  python tools/analysis/scale_agree.py --run --mmlu        # MMLU-Pro descriptive file (write-once, separate path)
      --out <path>        default E:/TaxoArena_backup_<date>_scale_agree[_mmlu]/scale_agree[_mmlu]_outcome.txt; an existing path REFUSES
      --data-root <dir>   where the DBs live (default: the checkout holding this script)

INPUTS (read-only; staged copies; sha256 against the registrar's pins, a mismatch REFUSES; the pins and readers are tree_like's):
  the six intent_emb_*.db and intent_transfer_corpora_v1.db; rows = MASSIVE / CLINC, side TRAIN, kept, in-scope (SA-R1).
  --mmlu: embeddings_cache.db (qwen3), experiment_results/embedder_cross/embeddings_cache_{embeddinggemma,nomic-embed-text}_latest.db
  (RAW; pins embedder_cross_arm_pins.json), on the texts the three DBs share that are mmlu_pro questions (all sides, as registered:
  "11,687 texts"; the TRAIN / GATE / EVAL composition of the v2 side export is printed, S3).

INSTRUMENT (registration, verbatim in the code). Per pair of arms on the same rows, per width (native; 256 = first 256 coordinates,
renormalised): AMI (sklearn, arithmetic) between spherical k-means partitions (intent_transfer_s0.skmeans: k-means++, n_init 1,
max_iter 300; labels = nearest centroid) at k in {2, 4, 8, 16, 32, 64, 128, 256}, 5 seeds per side (20261004 + s, s = 0..4),
all 25 seed pairs; mutual kNN overlap at k in {10, 50, 200, 1000} (cosine, self excluded; mean over rows of |N_A cap N_B| / k);
debiased linear CKA (the unbiased HSIC estimator, Song et al. 2012, in feature form).
NORMALISATION: den(k) = the mean over the 25 seed pairs of AMI(qwen3 q4, qwen3 q8) at k; normalised AMI_st(k) = AMI_st(k) / den(k).
SC1 statistic per corpus: rho = Spearman(mean over seed pairs of normalised AMI(qwen3, gemma), k) over the 8 k; slope_st = OLS
slope of normalised AMI_st(k) on log2 k (per seed pair); its 95% interval = mean +/- t(0.975, 24) x SD(ddof 1) / sqrt(25)
(SA-R4; the normal-quantile interval is printed beside, NOT of record). [CORRECTED 2026-10-04 by the engine-coder on READY
_zero_call_trio D-1 (10a5aa3d): the 25 slopes form a CROSSED 5 x 5 seed design and are not independent; the DECIDING interval
is now the crossed-seed bootstrap (seed_boot: the qwen3 seeds, tied across numerator and den(k), the gemma seeds and the q8
seeds resampled independently with replacement, B 2,000, RandomState(20261004), percentile 95%); the t(24) interval is printed
beside, NOT of record, with the crossed-ANOVA interval (MS_A + MS_B - MS_E) / 25, t(4) (crossed_anova; registrar
 bracket 5312852a). SA-R4 is withdrawn.]

CRITERIA (registered; every branch printed and executed by the selftest).
  SC1 (DECIDING; native width, SA-R3): per corpus DECREASES iff rho <= -0.7 AND the slope interval lies wholly below 0;
      SC1 = HELD iff DECREASES on both MASSIVE and CLINC; FAILED iff on neither; MIXED otherwise.  F-SC fires iff SC1 reads FAILED.
  P1 mean slope in [-0.08, 0.00] per log2 k on each corpus (HELD iff both); SC1 HELD at 0.60 (Brier).
  P2 (descriptive) k*(qwen3, gemma) (the smallest k with mean normalised AMI < 0.8) within [coarse, fine] gold counts (MASSIVE 18 /
      60, CLINC 10 / 150) on both corpora at 0.55 (Brier).  P3 (descriptive) SC3 holds at 0.70 (Brier).
SUPPORT (registered (a)-(f) quoted): 8 k x 25 seed pairs per corpus; DEFF 1.0; n_eff 25 seed pairs per k; planning SD of the slope
  0.02 -> SE 0.004, MDE80 0.011; SCOREABLE at the prediction -0.04. Printed beside: the realised SD, SE = SD / 5, MDE80 = 2.8 SE.
DESCRIPTIVE: SC2 k* per pair; SC3 (prompt pairs qwen3-qwen3_card and gemma-gemma_card above every embedder pair qwen3-gemma,
  qwen3-nomic, gemma-nomic at every k, both corpora); kNN overlap and CKA per pair; normaliser values above 1 (structural); the
  256-d width; MMLU-Pro (--mmlu, raw AMI curves: no q8 copy exists there).

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets BEFORE --run):
  SA-R1 rows = TRAIN, kept, in-scope (the registration names the corpora, not the side; TRAIN-only is rule 1's safe side and
        TREE-LIKE's set; OOS rows never enter a fit).
  SA-R2 "seed base 20261004": side seeds 20261004 + s, s = 0..4, the same five for every arm.
  SA-R3 SC1's width is not stated in the registration: NATIVE is deciding (TREE-LIKE TL1's convention); 256-d is printed beside
        with its own SC1 words, NOT of record. (A registration gap: the registrar brackets the width before --run.)
  SA-R4 [WITHDRAWN 2026-10-04, READY D-1] the t(24) interval (25 "independent" pairs); now printed beside only; the deciding
        interval is the crossed-seed bootstrap (see INSTRUMENT).
  SA-R5 "the q4-vs-q8 curve at the same k" = the mean over its 25 seed pairs (the per-seed-pair ratio is printed beside).

SELFTEST MUTANTS (2026-10-04; `--mutants`; copies in a scratch sandbox, the file never edited): the 18 mutants in MUTANTS below
(S1-S18: the rho and interval boundaries, either-corpus HELD, no normaliser, slope on k, no t quantile, the wrong pair, the 256
width, (s, s) seed pairs only, F-SC unprinted, write-once dropped, k* <=, every side read, reversed Spearman, the self-normaliser,
biased CKA, self in kNN, P1 on the corpus mean; D-1 delta: S5b, S19 decision reverted to t(24), S20-S23 bootstrap q8 / tie /
gemma / percentile, S24-S25 crossed ANOVA t(24) / no -MS_E): 26 / 26 KILLED on this code (delta run 2026-10-04).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import datetime
import math
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import zc_common as ZC          # noqa: E402
import scratch_dir              # noqa: E402
import tree_like as TL          # noqa: E402  (pins, the intent loaders, the staged-copy reader; no identity check is run here)

import numpy as np              # noqa: E402

ROOT = ZC.ROOT
TAG = "[SCALE-AGREE]"
REG = "docs/judge_v2_program.md L24375-L24386 (registration commit 633255f2)"
SEED = 20261004
SEEDS = 5
K_GRID = (2, 4, 8, 16, 32, 64, 128, 256)
KNN_K = (10, 50, 200, 1000)
WIDTH = 256
CORPORA = ("massive", "clinc")
ARMS = ("qwen3", "qwen3_q8", "qwen3_card", "gemma", "gemma_card", "nomic")
NORM_PAIR = ("qwen3", "qwen3_q8")
DECIDING_PAIR = ("qwen3", "gemma")
EMB_PAIRS = (("qwen3", "gemma"), ("qwen3", "nomic"), ("gemma", "nomic"))
PROMPT_PAIRS = (("qwen3", "qwen3_card"), ("gemma", "gemma_card"))
PAIRS = (NORM_PAIR,) + EMB_PAIRS + PROMPT_PAIRS
RHO_BAR = -0.7
KSTAR_BAR = 0.8
T24 = 2.0638985616280205          # scipy.stats.t.ppf(0.975, 24)
BOOT_B = 2000                     # D-1 (READY_zero_call_trio 10a5aa3d): crossed seed bootstrap, B and seed fixed here
BOOT_SEED = 20261004
T4 = 2.7764451051977987            # scipy.stats.t.ppf(0.975, 4): the crossed-ANOVA interval (descriptive)
GOLD = {"massive": (18, 60), "clinc": (10, 150)}
P1_BAND = (-0.08, 0.00); P1_PROB = 0.60
P2_PROB = 0.55
P3_PROB = 0.70
PLAN = "8 k x 25 seed pairs per corpus; DEFF 1.0; n_eff 25; planning SD of the slope 0.02 -> SE 0.004, MDE80 0.011; SCOREABLE at -0.04"
MMLU_ARMS = ("qwen3", "gemma", "nomic")
MMLU_PAIRS = (("qwen3", "gemma"), ("qwen3", "nomic"), ("gemma", "nomic"))
SELFTEST_CHECKS = 33

MUTANTS = [
    ("S1", "Spearman bar read as < -0.7", "    return bool(rho <= RHO_BAR) and bool(ci_hi < 0)\n", "    return bool(rho < RHO_BAR) and bool(ci_hi < 0)\n"),
    ("S2", "slope interval bound read as <= 0", "    return bool(rho <= RHO_BAR) and bool(ci_hi < 0)\n", "    return bool(rho <= RHO_BAR) and bool(ci_hi <= 0)\n"),
    ("S3", "SC1 HELD on either corpus", "    if all(per.values()):\n        return \"HELD\"\n", "    if any(per.values()):\n        return \"HELD\"\n"),
    ("S4", "no normalisation (raw AMI)", "    return {k: ami[k] / den[k] for k in ami}\n", "    return {k: ami[k] for k in ami}\n"),
    ("S5", "slope on k instead of log2 k (per-pair slopes)", "    x = np.log2(np.asarray(ks, dtype=np.float64))\n    return float(np.polyfit", "    x = np.asarray(ks, dtype=np.float64)\n    return float(np.polyfit"),
    ("S5b", "bootstrap slope on k instead of log2 k", "    x = np.log2(np.asarray(ks, dtype=np.float64))\n    xc = ", "    x = np.asarray(ks, dtype=np.float64)\n    xc = "),
    ("S6", "interval half-width without the t quantile", "    half = T24 * sd / math.sqrt(len(slopes))\n", "    half = sd / math.sqrt(len(slopes))\n"),
    ("S7", "deciding pair qwen3-nomic (wrong population)", "DECIDING_PAIR = (\"qwen3\", \"gemma\")\n", "DECIDING_PAIR = (\"qwen3\", \"nomic\")\n"),
    ("S8", "deciding width 256", "    dec = res[\"native\"]\n", "    dec = res[\"w%d\" % ctx.width]\n"),
    ("S9", "seed pairs (s, s) only, not all 25", "    return [(s, t) for s in range(n) for t in range(n)]\n", "    return [(s, s) for s in range(n)]\n"),
    ("S10", "F-SC line not printed on the FAILED branch", "        out.append(\"F-SC (fires iff SC1 FAILED): FIRED", "        0 and out.append(\"F-SC (fires iff SC1 FAILED): FIRED"),
    ("S11", "write-once dropped (pre-check and mode x both gone)",
     "        if os.path.exists(p):\n            ZC.refuse(TAG, \"%s exists: the outcome of record is WRITE-ONCE (refused before any read)\" % p)\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    ZC.write_once(out_path, text, TAG)\n",
     "        pass\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)\n    open(out_path, \"w\", encoding=\"utf-8\").write(text)\n"),
    ("S12", "k* uses <= 0.8", "        if bool(v < KSTAR_BAR):\n", "        if bool(v <= KSTAR_BAR):\n"),
    ("S13", "every side read (TRAIN filter dropped)", "        rows = C.idx(TL.SIDE_TRAIN)\n", "        rows = np.nonzero(C.kept & ~C.oos)[0]\n"),
    ("S14", "Spearman against the reversed k order", "    rho = spearman(curve, ks)\n", "    rho = spearman(curve, ks[::-1])\n"),
    ("S15", "the normaliser taken from the deciding pair itself", "    den = {k: float(np.mean(list(ami_pairs[NORM_PAIR][k].values()))) for k in ks}\n", "    den = {k: float(np.mean(list(ami_pairs[DECIDING_PAIR][k].values()))) for k in ks}\n"),
    ("S16", "CKA without the diagonal removal (biased HSIC)", "    kd, ld = (X * X).sum(1), (Y * Y).sum(1)\n", "    kd, ld = 0.0 * (X * X).sum(1), 0.0 * (Y * Y).sum(1)\n"),
    ("S17", "kNN includes the row itself", "        S[np.arange(len(S)), np.arange(a, b)] = -np.inf\n", "        pass\n"),
    ("S19", "D-1 reverted: the decision reads the t(24) interval", "dec=decreases(rho, bhi), curve=curve)\n", "dec=decreases(rho, hi), curve=curve)\n"),
    ("S20", "bootstrap: q8 seeds not resampled (den over the fixed q8 seeds)", "        c = rng.randint(0, nseeds, nseeds)\n", "        c = np.arange(nseeds)\n"),
    ("S21", "bootstrap: den's qwen3 seeds drawn apart from the numerator's (tie broken)", "        den = Nm[:, a][:, :, c].reshape(K, -1).mean(axis=1)\n", "        den = Nm[:, rng.randint(0, nseeds, nseeds)][:, :, c].reshape(K, -1).mean(axis=1)\n"),
    ("S24", "crossed-ANOVA interval with t(24) instead of t(4)", "    return float(g - T4 * se), float(g + T4 * se), se\n", "    return float(g - T24 * se), float(g + T24 * se), se\n"),
    ("S25", "crossed-ANOVA variance without the - MS_E term", "    se = math.sqrt(max(0.0, ms_a + ms_b - ms_e) / (n * n))\n", "    se = math.sqrt(max(0.0, ms_a + ms_b) / (n * n))\n"),
    ("S22", "bootstrap: gemma seeds not resampled", "        b = rng.randint(0, nseeds, nseeds)\n", "        b = np.arange(nseeds)\n"),
    ("S23", "bootstrap interval read at 95.0 instead of 97.5", "    lo, hi = np.percentile(out, [2.5, 97.5])\n", "    lo, hi = np.percentile(out, [2.5, 95.0])\n"),
    ("S18", "P1 band read on the mean of the two corpora (not on each)", "    p1 = all(ZC.in_band(s, P1_BAND) for s in slopes_by_corpus.values())\n", "    p1 = ZC.in_band(float(np.mean(list(slopes_by_corpus.values()))), P1_BAND)\n"),
]


class Ctx(object):
    def __init__(self, data_root=ROOT, k_grid=K_GRID, knn_k=KNN_K, seeds=SEEDS, width=WIDTH, native=None, check_pins=True,
                 arms=ARMS, mmlu=False, gold=None):
        self.data_root, self.k_grid, self.knn_k, self.seeds, self.width = data_root, tuple(k_grid), tuple(knn_k), seeds, width
        self.native = native or dict(TL.NATIVE)
        self.check_pins = check_pins
        self.arms = arms
        self.mmlu = mmlu
        self.gold = gold or dict(GOLD)
        self.staged = {}
        self.stage_dir = None

    def stage(self, rel):
        if rel not in self.staged:
            if self.stage_dir is None:
                self.stage_dir = scratch_dir.mkdtemp(prefix="scale_agree_stage_")
            d = os.path.join(self.stage_dir, str(len(self.staged)))
            self.staged[rel] = ZC.stage_db(os.path.join(self.data_root, rel), d, TAG)
        return self.staged[rel]


# ----------------------------------------------------------------------------------------------- statistics
def seed_pairs(n):
    return [(s, t) for s in range(n) for t in range(n)]


def spearman(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b).correlation)


def ami(a, b):
    from sklearn.metrics import adjusted_mutual_info_score
    return float(adjusted_mutual_info_score(a, b, average_method="arithmetic"))


def partitions(X, ks, seeds):
    """labels[k][s] for spherical k-means (intent_transfer_s0.skmeans) at each k and side seed 20261004 + s."""
    ITS = TL.its_module()
    out = {}
    for k in ks:
        out[k] = {}
        for s in range(seeds):
            C = ITS.skmeans(X, k, SEED + s)
            out[k][s] = np.argmax(X @ C.T, axis=1)
    return out


def knn_lists(X, kmax, block=1024):
    """Top-kmax neighbours by cosine, self excluded, most similar first (ties: lower index first)."""
    n = len(X)
    kmax = min(kmax, n - 1)
    out = np.empty((n, kmax), dtype=np.int64)
    for a in range(0, n, block):
        b = min(n, a + block)
        S = X[a:b] @ X.T
        S[np.arange(len(S)), np.arange(a, b)] = -np.inf
        part = np.argpartition(-S, kmax - 1, axis=1)[:, :kmax]
        vals = np.take_along_axis(S, part, axis=1)
        order = np.lexsort((part, -vals), axis=1)
        out[a:b] = np.take_along_axis(part, order, axis=1)
    return out


def knn_overlap(NA, NB, k):
    A, B = NA[:, :k], NB[:, :k]
    M = np.sort(np.concatenate([A, B], axis=1), axis=1)
    return float(np.mean((M[:, 1:] == M[:, :-1]).sum(axis=1) / float(k)))


def hsic_u(X, Y):
    """Unbiased HSIC (Song et al. 2012) of the linear kernels K = X X^T, L = Y Y^T in feature form (no n x n matrix)."""
    n = len(X)
    kd, ld = (X * X).sum(1), (Y * Y).sum(1)
    trKL = float(np.sum((X.T @ Y) ** 2)) - float(kd @ ld)
    k1 = X @ (X.T @ np.ones(n)) - kd
    l1 = Y @ (Y.T @ np.ones(n)) - ld
    sK, sL = float(k1.sum()), float(l1.sum())
    return (trKL + sK * sL / ((n - 1) * (n - 2)) - 2.0 / (n - 2) * float(k1 @ l1)) / (n * (n - 3))


def cka_debiased(X, Y):
    return hsic_u(X, Y) / math.sqrt(hsic_u(X, X) * hsic_u(Y, Y))


def normalise(ami, den):
    return {k: ami[k] / den[k] for k in ami}


def slope_on_log2k(ks, ys):
    x = np.log2(np.asarray(ks, dtype=np.float64))
    return float(np.polyfit(x, np.asarray(ys, dtype=np.float64), 1)[0])


def slope_interval(slopes):
    m = float(np.mean(slopes))
    sd = float(np.std(slopes, ddof=1))
    half = T24 * sd / math.sqrt(len(slopes))
    return m, sd, m - half, m + half, 1.959963984540054 * sd / math.sqrt(len(slopes))


def seed_boot(ks, ami_dec, ami_norm, nseeds, B=BOOT_B, seed=BOOT_SEED):
    """D-1 fix (READY_zero_call_trio 10a5aa3d): the 25 slopes come from a CROSSED 5 x 5 design (pair (s, t) shares qwen3 seed
    s with four pairs and gemma seed t with four, and the q4 seed s also enters den(k)), so they are not 25 independent draws.
    Each bootstrap draw resamples, independently and with replacement, the qwen3 seeds a (used in the numerator AND in den, so
    tied), the gemma seeds b and the q8 seeds c; den*(k) = mean over (a_i, c_j) of AMI(q4, q8); the mean normalised curve is
    mean over (a_i, b_j) of AMI(qwen3, gemma) / den*(k); its OLS slope on log2 k (= the mean of the per-pair slopes). numpy
    RandomState(BOOT_SEED), draws in the order a, b, c; B = 2,000; percentile 95% interval. -> (lo, hi, bootstrap SD)."""
    K = len(ks)
    A = np.array([[[ami_dec[k][(s, t)] for t in range(nseeds)] for s in range(nseeds)] for k in ks])
    Nm = np.array([[[ami_norm[k][(s, c)] for c in range(nseeds)] for s in range(nseeds)] for k in ks])
    x = np.log2(np.asarray(ks, dtype=np.float64))
    xc = x - x.mean()
    rng = np.random.RandomState(seed)
    out = np.empty(B)
    for r in range(B):
        a = rng.randint(0, nseeds, nseeds)
        b = rng.randint(0, nseeds, nseeds)
        c = rng.randint(0, nseeds, nseeds)
        den = Nm[:, a][:, :, c].reshape(K, -1).mean(axis=1)
        num = A[:, a][:, :, b].reshape(K, -1).mean(axis=1)
        y = num / den
        out[r] = float(xc @ (y - y.mean()) / (xc @ xc))
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi), float(np.std(out, ddof=1))


def crossed_anova(slopes, n):
    """DESCRIPTIVE (registrar bracket 5312852a, NOT of record): two-way crossed ANOVA without replication on the n x n slope
    matrix (rows = qwen3 seeds, columns = gemma seeds); Var(mean) = (MS_A + MS_B - MS_E) / n^2 (floored at 0); interval
    mean +/- t(0.975, n - 1) x SE (t(4) at n = 5). -> (lo, hi, se)."""
    M = np.asarray(slopes, dtype=np.float64).reshape(n, n)
    g = M.mean()
    ra, cb = M.mean(axis=1), M.mean(axis=0)
    ms_a = n * float(((ra - g) ** 2).sum()) / (n - 1)
    ms_b = n * float(((cb - g) ** 2).sum()) / (n - 1)
    ms_e = float(((M - ra[:, None] - cb[None, :] + g) ** 2).sum()) / ((n - 1) * (n - 1))
    se = math.sqrt(max(0.0, ms_a + ms_b - ms_e) / (n * n))
    return float(g - T4 * se), float(g + T4 * se), se


def decreases(rho, ci_hi):
    """SC1 per corpus (registered): DECREASES iff rho <= -0.7 AND the 95% slope interval lies wholly below 0."""
    return bool(rho <= RHO_BAR) and bool(ci_hi < 0)


def sc1_decide(per):
    if all(per.values()):
        return "HELD"
    if not any(per.values()):
        return "FAILED"
    return "MIXED"


def kstar(ks, curve):
    for k, v in zip(ks, curve):
        if bool(v < KSTAR_BAR):
            return k
    return None


# ----------------------------------------------------------------------------------------------- per corpus x width
def corpus_width(ctx, Xs, label, out, pairs, norm=True):
    """Xs: arm -> unit matrix (same rows). -> dict with AMI tables, normalised curves, slopes, kNN, CKA."""
    ks = list(ctx.k_grid)
    t0 = time.time()
    labs = {a: partitions(X, ks, ctx.seeds) for a, X in Xs.items()}
    kmax = max(ctx.knn_k)
    nbr = {a: knn_lists(X, kmax) for a, X in Xs.items()}
    sp = seed_pairs(ctx.seeds)
    ami_pairs = {}
    for p in pairs:
        ami_pairs[p] = {k: {(s, t): ami(labs[p[0]][k][s], labs[p[1]][k][t]) for (s, t) in sp} for k in ks}
    res = dict(ks=ks, ami=ami_pairs, curves={}, slopes={}, knn={}, cka={}, nseeds=ctx.seeds)
    if norm:
        den = {k: float(np.mean(list(ami_pairs[NORM_PAIR][k].values()))) for k in ks}
    else:
        den = {k: 1.0 for k in ks}
    res["den"] = den
    for p in pairs:
        per_k = {k: normalise({st: ami_pairs[p][k][st] for st in sp}, {st: den[k] for st in sp}) for k in ks}
        res["curves"][p] = [float(np.mean(list(per_k[k].values()))) for k in ks]
        res["slopes"][p] = [slope_on_log2k(ks, [per_k[k][st] for k in ks]) for st in sp]
        res["knn"][p] = [knn_overlap(nbr[p[0]], nbr[p[1]], k) for k in ctx.knn_k if k < len(Xs[p[0]])]
        res["cka"][p] = cka_debiased(Xs[p[0]], Xs[p[1]])
    out.append("  [%s] fits and pairs computed in %.0f s; den(k) (q4-q8 mean AMI over %d seed pairs): [%s]"
               % (label, time.time() - t0, len(sp), ", ".join("%.4f" % den[k] for k in ks)) if norm else
               "  [%s] fits and pairs computed in %.0f s; RAW AMI (no normaliser)" % (label, time.time() - t0))
    for p in pairs:
        m, sd, lo, hi, zh = slope_interval(res["slopes"][p])
        out.append("  [%s] %s-%s: %s AMI by k [%s]; slope %+.4f per log2 k (95%% t-interval [%+.4f, %+.4f]; normal [%+.4f, %+.4f]); rho %+.3f; k* %s; kNN overlap@%s [%s]; debiased CKA %.4f"
                   % (label, p[0], p[1], "normalised" if norm else "raw", ", ".join("%.4f" % v for v in res["curves"][p]), m, lo, hi,
                      m - zh, m + zh, spearman(res["curves"][p], ks), kstar(ks, res["curves"][p]),
                      "/".join(str(k) for k in ctx.knn_k), ", ".join("%.4f" % v for v in res["knn"][p]), res["cka"][p]))
    if norm:
        above = {"%s-%s" % p: sum(1 for v in res["curves"][p] if v > 1.0) for p in pairs if p != NORM_PAIR}
        out.append("  [%s] normalised AMI above 1 (k values per pair; structural, printed): %s" % (label, above))
    return res


def sc1_corpus(ctx, res):
    ks = res["ks"]
    curve = res["curves"][DECIDING_PAIR]
    rho = spearman(curve, ks)
    m, sd, lo, hi, zh = slope_interval(res["slopes"][DECIDING_PAIR])
    blo, bhi, bsd = seed_boot(ks, res["ami"][DECIDING_PAIR], res["ami"][NORM_PAIR], res["nseeds"])
    alo, ahi, ase = crossed_anova(res["slopes"][DECIDING_PAIR], res["nseeds"])
    return dict(rho=rho, mean=m, sd=sd, lo=lo, hi=hi, blo=blo, bhi=bhi, bsd=bsd, alo=alo, ahi=ahi, ase=ase, dec=decreases(rho, bhi), curve=curve)


# ----------------------------------------------------------------------------------------------- data
def intent_matrices(ctx, out):
    """-> {corpus: {arm: unit matrix of all TRAIN rows (native)}}."""
    ITS = TL.its_module()
    ing = ctx.stage("intent_transfer_corpora_v1.db")
    if ctx.check_pins and ing["sha256"] != TL.INGEST_PIN:
        ZC.refuse(TAG, "intent_transfer_corpora_v1.db sha256 %s != the pin %s" % (ing["sha256"], TL.INGEST_PIN))
    CS = ITS.load_corpora(ing["path"])
    texts = {}
    for c in CORPORA:
        C = CS[c]
        rows = C.idx(TL.SIDE_TRAIN)
        texts[c] = [C.text[j] for j in rows]
        out.append("  census %s: %d TRAIN rows (kept, in-scope; ingest sides TRAIN %d / GATE %d / EVAL %d)"
                   % (c, len(rows), len(C.idx("TRAIN")), len(C.idx("GATE")), len(C.idx("EVAL"))))
    out.append("  ingest sha256 %s (%s)" % (ing["sha256"][:16], "PIN OK" if ing["sha256"] == TL.INGEST_PIN else "unpinned fixture"))
    mats = {c: {} for c in CORPORA}
    for a in ctx.arms:
        rel = "intent_emb_%s.db" % a
        st = ctx.stage(rel)
        pin = TL.PINS.get(a)
        if ctx.check_pins and st["sha256"] != pin:
            ZC.refuse(TAG, "%s sha256 %s != the registrar's pin %s" % (rel, st["sha256"], pin))
        allt = sorted({t for c in CORPORA for t in texts[c]})
        vec = TL.read_vectors(st["path"], allt, ctx.native[a])
        out.append("  arm %-10s %s sha256 %s (%s); %d-d" % (a, rel, st["sha256"][:16], "PIN OK" if st["sha256"] == pin else "unpinned fixture", ctx.native[a]))
        for c in CORPORA:
            mats[c][a] = np.array([vec[t] for t in texts[c]], dtype=np.float32)
        del vec
    return mats


def mmlu_matrices(ctx, out):
    import split_side as SSD
    import v2_engine_pool as EP
    items, meta = EP.read_side(os.path.join(ROOT, EP.DEFAULT_SIDE))
    got, _ = EP.pool_of(items, "mmlu-pro-v2")
    out.append("  pool %s recomputed from the side export %s (sha256-lf %s): split words of the texts below are printed" % (got, meta["path"], meta["sha256_lf"][:16]))
    mm = ctx.stage("mmlu_pro_dataset_cache_v2.db")
    con = ZC.open_ro(mm["path"], TAG)
    try:
        qs = {t for (t,) in con.execute("SELECT question FROM mmlu_pro") if t}
    finally:
        con.close()
    vecs = {}
    have = None
    for a in MMLU_ARMS:
        st = ctx.stage(TL.MMLU_FILES[a])
        pin = TL.mmlu_pins().get(a)
        if ctx.check_pins and pin is not None and st["sha256"] != pin:
            ZC.refuse(TAG, "%s sha256 %s != the registrar's pin %s" % (TL.MMLU_FILES[a], st["sha256"], pin))
        con = ZC.open_ro(st["path"], TAG)
        try:
            v = {}
            for t, bl in con.execute("SELECT query, vector FROM embeddings"):
                if t in qs and bl is not None and len(bl) == 4 * TL.MMLU_NATIVE[a]:
                    v[t] = bl
        finally:
            con.close()
        vecs[a] = v
        have = set(v) if have is None else (have & set(v))
        out.append("  arm %-6s %s sha256 %s (%s); %d mmlu_pro texts with a %d-d vector" % (a, TL.MMLU_FILES[a], st["sha256"][:16], "PIN OK" if pin and st["sha256"] == pin else "no pin (sha256 printed)", len(v), TL.MMLU_NATIVE[a]))
    texts = sorted(have)
    sides = {}
    for t in texts:
        s = items.get("i:" + SSD.stem_key(t), (None, "NOT IN EXPORT"))[1]
        sides[s] = sides.get(s, 0) + 1
    out.append("  MMLU-Pro common texts: %d (registered planning 11,687); split words: %s (all sides, as registered; DESCRIPTIVE)" % (len(texts), dict(sorted(sides.items()))))
    return {"mmlu": {a: np.array([np.frombuffer(vecs[a][t], dtype=">f4") for t in texts], dtype=np.float32) for a in MMLU_ARMS}}


# ----------------------------------------------------------------------------------------------- run
def header(ctx, out, mode):
    out.append("SCALE-AGREE readout (%s); mode %s; %s; zc_common blob:%s; tree_like blob:%s; intent_transfer_s0 blob:%s (pinned); date %s; ZERO calls"
               % (REG, mode, ZC.pins_line(os.path.abspath(__file__)), ZC.git_blob(ZC.__file__.replace(".pyc", ".py")),
                  ZC.git_blob(TL.__file__.replace(".pyc", ".py")), TL.ITS_BLOB, datetime.date.today().isoformat()))
    if ctx.mmlu:
        out.append("POOL READER (rule 7; --mmlu, DESCRIPTIVE): reads embeddings_cache.db (and the v2 side export for the split words)")
    else:
        out.append("POOL: none read (intent DBs and the intent ingest only; rule 7 does not bind). TRAIN rows only; labels never read.")


def width_views(ctx, M):
    """native and w<width>: unit matrices (float64)."""
    v = {}
    v["native"] = {a: TL.unit(X) for a, X in M.items()}
    v["w%d" % ctx.width] = {a: TL.unit(X[:, :ctx.width]) for a, X in M.items()}
    return v


def analyse(ctx):
    out = []
    header(ctx, out, "--run" + (" --mmlu" if ctx.mmlu else ""))
    if ctx.mmlu:
        mats = mmlu_matrices(ctx, out)
        for wkey, Xs in width_views(ctx, mats["mmlu"]).items():
            corpus_width(ctx, Xs, "mmlu %s" % wkey, out, MMLU_PAIRS, norm=False)
        out.append("WHAT THIS RESULT DOES NOT SHOW (registered): which embedder is better (D3 the author's); any partition's correctness; MMLU-Pro as decisive.")
        return out, {}
    if ctx.check_pins:
        TL.config_pins()
    mats = intent_matrices(ctx, out)
    allres = {}
    for c in CORPORA:
        views = width_views(ctx, mats[c])
        pairs = [p for p in PAIRS if p[0] in views["native"] and p[1] in views["native"]]
        allres[c] = {wkey: corpus_width(ctx, Xs, "%s %s" % (c, wkey), out, pairs) for wkey, Xs in views.items()}
        mats[c] = None
    return verdicts(ctx, allres, out)


def verdicts(ctx, allres, out):
    sc = {}
    for c in CORPORA:
        res = allres[c]
        dec = res["native"]
        sc[c] = sc1_corpus(ctx, dec)
        sc[c]["w"] = sc1_corpus(ctx, res["w%d" % ctx.width])
    per = {c: sc[c]["dec"] for c in CORPORA}
    v = sc1_decide(per)
    sds = [sc[c]["sd"] for c in CORPORA]
    out.append("SUPPORT (registered (a)-(f) quoted: %s; D-1: (b) 'DEFF 1.0, seed pairs independent' is false for the crossed 5 x 5 grid, the registrar brackets (b)-(d)): realised crossed-seed bootstrap SE of the mean slope %s (naive SD / sqrt(25) beside: %s); MDE80 = 2.8 x bootstrap SE = %s; realised design effect (bootstrap SE / naive SE)^2 %s; prediction -0.04 vs MDE80: %s"
               % (PLAN, ", ".join("%s %.4f" % (c, sc[c]["bsd"]) for c in CORPORA), ", ".join("%s %.4f" % (c, sc[c]["sd"] / 5.0) for c in CORPORA),
                  ", ".join("%s %.4f" % (c, 2.8 * sc[c]["bsd"]) for c in CORPORA),
                  ", ".join("%s %.2f" % (c, (sc[c]["bsd"] / (sc[c]["sd"] / 5.0)) ** 2 if sc[c]["sd"] > 0 else float("nan")) for c in CORPORA),
                  "beyond the MDE" if all(0.04 > 2.8 * sc[c]["bsd"] for c in CORPORA) else "NOT beyond the MDE on every corpus"))
    out.append("BUILDER'S READINGS (the registrar confirms or brackets): SA-R1 TRAIN rows; SA-R2 seeds 20261004 + s; SA-R3 SC1 width NATIVE (registration gap); D-1 crossed-seed bootstrap interval (t(24) beside, not of record); SA-R5 den = mean over the q4-q8 seed pairs")
    out.append("CRITERIA AND PREDICTIONS")
    for c in CORPORA:
        s = sc[c]
        out.append("SC1 %s (native; DECREASES iff rho <= -0.7 AND the 95%% slope interval < 0): %s -- rho %+.3f; mean slope %+.4f per log2 k, 95%% crossed-seed bootstrap interval [%+.4f, %+.4f] (B %d, seed %d; bootstrap SD %.4f); beside, DESCRIPTIVE, NOT of record: crossed-ANOVA t(4)-interval [%+.4f, %+.4f] (SE %.4f); t(24)-interval (treats the 5 x 5 grid as 25 independent pairs) [%+.4f, %+.4f]; normalised AMI(qwen3, gemma) by k [%s]"
                   % (c, "DECREASES" if s["dec"] else "does not decrease", s["rho"], s["mean"], s["blo"], s["bhi"], BOOT_B, BOOT_SEED, s["bsd"], s["alo"], s["ahi"], s["ase"], s["lo"], s["hi"], ", ".join("%.4f" % x for x in s["curve"])))
    out.append("SC1 (DECIDING; HELD iff DECREASES on both MASSIVE and CLINC; FAILED iff on neither; MIXED otherwise): %s -- massive %s, clinc %s"
               % (v, "DECREASES" if per["massive"] else "no", "DECREASES" if per["clinc"] else "no"))
    if v == "FAILED":
        out.append("F-SC (fires iff SC1 FAILED): FIRED -- the record's 'coarse holds, fine diverges' reconciliation has no label-free support")
    else:
        out.append("F-SC (fires iff SC1 FAILED): NOT FIRED")
    wper = {c: sc[c]["w"]["dec"] for c in CORPORA}
    out.append("SC1 at 256-d (SA-R3 alternative, NOT of record): %s -- massive rho %+.3f hi %+.4f, clinc rho %+.3f hi %+.4f"
               % (sc1_decide(wper), sc["massive"]["w"]["rho"], sc["massive"]["w"]["bhi"], sc["clinc"]["w"]["rho"], sc["clinc"]["w"]["bhi"]))
    slopes_by_corpus = {c: sc[c]["mean"] for c in CORPORA}
    p1 = all(ZC.in_band(s, P1_BAND) for s in slopes_by_corpus.values())
    out.append("P1 mean slope in [-0.08, 0.00] on each corpus (massive %+.4f, clinc %+.4f): %s; SC1 HELD predicted at 0.60, occurred: %s, Brier %.4f"
               % (slopes_by_corpus["massive"], slopes_by_corpus["clinc"], "HELD" if p1 else "FAILED", "yes" if v == "HELD" else "no", ZC.brier(P1_PROB, v == "HELD")))
    ks = list(ctx.k_grid)
    kst = {c: kstar(ks, sc[c]["curve"]) for c in CORPORA}
    inb = all(kst[c] is not None and ctx.gold[c][0] <= kst[c] <= ctx.gold[c][1] for c in CORPORA)
    out.append("SC2 (DESCRIPTIVE) k* (smallest k with normalised AMI < 0.8) per pair: %s"
               % "; ".join("%s %s" % (c, ", ".join("%s-%s %s" % (p[0], p[1], kstar(ks, allres[c]["native"]["curves"][p])) for p in allres[c]["native"]["curves"] if p != NORM_PAIR)) for c in CORPORA))
    out.append("P2 (descriptive) k*(qwen3, gemma) within [coarse, fine] gold counts on both corpora (massive %s in %s, clinc %s in %s): %s; predicted at 0.55, Brier %.4f"
               % (kst["massive"], list(ctx.gold["massive"]), kst["clinc"], list(ctx.gold["clinc"]), "yes" if inb else "no", ZC.brier(P2_PROB, inb)))
    sc3 = {}
    for c in CORPORA:
        cv = allres[c]["native"]["curves"]
        if all(p in cv for p in PROMPT_PAIRS + EMB_PAIRS):
            sc3[c] = all(min(cv[p][j] for p in PROMPT_PAIRS) > max(cv[p][j] for p in EMB_PAIRS) for j in range(len(ks)))
        else:
            sc3[c] = None
    s3 = bool(all(x is True for x in sc3.values()))
    out.append("SC3 (DESCRIPTIVE) prompt pairs above every embedder pair at every k: massive %s, clinc %s -> %s; P3 predicted at 0.70, Brier %.4f"
               % (sc3["massive"], sc3["clinc"], "HOLDS" if s3 else "does not hold", ZC.brier(P3_PROB, s3)))
    out.append("WHAT THIS RESULT DOES NOT SHOW (registered): which embedder is better (D3 the author's); any partition's correctness; MMLU-Pro as decisive.")
    return out, dict(v=v, sc=sc, per=per)


def dry_run(ctx):
    out = []
    header(ctx, out, "--dry-run" + (" --mmlu" if ctx.mmlu else ""))
    if ctx.mmlu:
        mats = mmlu_matrices(ctx, out)
    else:
        if ctx.check_pins:
            TL.config_pins()
        mats = intent_matrices(ctx, out)
    ITS = TL.its_module()
    total = 0.0
    for c, M in mats.items():
        for a, X in M.items():
            for wkey, Xw in (("native", TL.unit(X)), ("w%d" % ctx.width, TL.unit(X[:, :ctx.width]))):
                k = max(ctx.k_grid)
                t0 = time.time(); ITS.skmeans(Xw, k, SEED); dt = time.time() - t0
                est = dt * 2.0 * ctx.seeds                       # sum over the k grid ~ 2 x the largest k
                total += est
                out.append("  timed: %s %s %s one k = %d fit %.1f s -> about %.0f min for the grid x %d seeds" % (c, a, wkey, k, dt, est / 60.0, ctx.seeds))
            break
        break
    n_cells = sum(len(M) for M in mats.values()) * 2
    out.append("PRICE: about %.1f h CPU single-threaded for %d arm x width x corpus cells (extrapolated from the first arm; AMI, kNN and CKA add minutes); zero calls" % (total / 2.0 * n_cells / 3600.0, n_cells))
    out.append("--dry-run: no AMI computed, nothing written.")
    print("\n".join(out))
    return 0


def run(ctx, out_path):
    sums = os.path.join(os.path.dirname(os.path.abspath(out_path)), "SHA256SUMS.txt")
    for p in (out_path, sums):
        if os.path.exists(p):
            ZC.refuse(TAG, "%s exists: the outcome of record is WRITE-ONCE (refused before any read)" % p)
    lines, _ = analyse(ctx)
    text = "\n".join(lines) + "\n"
    print(text, end="")
    ZC.write_once(out_path, text, TAG)
    print("%s wrote %s (write-once; never committed)" % (TAG, out_path.replace("\\", "/")))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
FIX_NATIVE = {"qwen3": 16, "qwen3_q8": 16, "qwen3_card": 16, "gemma": 16, "gemma_card": 16, "nomic": 16}
FIX_GRID = (2, 4, 8, 16, 32)


def _world_vectors(rng, n, kind):
    """kind 'split': 2 coarse groups x 16 fine subgroups (2 coarse: den(2) stable, D-1 re-pin). qwen3 / q8 / qwen3_card: coarse centre + fine offset (q8, card: + tiny
    noise); gemma: the SAME coarse centre with the fine labels re-drawn at random (coarse agrees, fine diverges); gemma_card =
    gemma + tiny noise; nomic: coarse + its own random fine. kind 'same': gemma = qwen3 + tiny noise (agreement flat in k).
    Coordinates 0-7 carry the coarse centres, 8-15 the fine offsets (the first-8 slice keeps only coarse structure)."""
    coarse = np.arange(n) % 2
    fine = rng.integers(0, 16, size=n)
    Cc = rng.standard_normal((2, 8)) * 3.0
    Fo = rng.standard_normal((2, 16, 8)) * 1.0
    def emb(cl, fl, noise):
        X = np.zeros((n, 16))
        X[:, :8] = Cc[cl] + 0.3 * rng.standard_normal((n, 8))
        X[:, 8:] = Fo[cl, fl] + noise * rng.standard_normal((n, 8))
        return X
    q = emb(coarse, fine, 0.15)
    V = {"qwen3": q, "qwen3_q8": q + 0.02 * rng.standard_normal(q.shape), "qwen3_card": q + 0.03 * rng.standard_normal(q.shape)}
    if kind == "split":
        g = emb(coarse, rng.integers(0, 16, size=n), 0.15)
    else:
        g = q + 0.02 * rng.standard_normal(q.shape)
    V["gemma"] = g
    V["gemma_card"] = g + 0.03 * rng.standard_normal(q.shape)
    V["nomic"] = emb(coarse, rng.integers(0, 16, size=n), 0.15)
    return V


def _fixture(root, kind):
    """Intent ingest + six arm DBs; TRAIN rows (kept, in-scope) carry the world; GATE / EVAL / dropped / OOS rows carry vectors
    of the opposite kind, so reading them changes the answer (S13)."""
    TL.its_module()
    import intent_ingest as II
    os.makedirs(root, exist_ok=True)
    rng = np.random.default_rng(11)
    con = sqlite3.connect(os.path.join(root, "intent_transfer_corpora_v1.db"))
    for d in II.DDL:
        con.execute(d)
    vecs = {a: {} for a in ARMS}
    for c in CORPORA:
        n_tr, n_ot = 320, 160
        W = {"TRAIN": _world_vectors(rng, n_tr, kind[c]), "OTHER": _world_vectors(rng, n_ot, "same" if kind[c] == "split" else "split")}
        rows = []
        for side in ("TRAIN", "OTHER"):
            n = n_tr if side == "TRAIN" else n_ot
            for j in range(n):
                t = "%s %s %d" % (c, side, j)
                real = "TRAIN" if side == "TRAIN" else ("EVAL", "GATE", "TRAIN")[j % 3]
                drop = "dup" if (side == "OTHER" and real == "TRAIN") else None
                rows.append(("%s-%s-%04d" % (c, side, j), c, "train", str(j), t, "x", "y", 0, None, "k%s%d" % (side, j), real, real, drop))
                for a in ARMS:
                    vecs[a][t] = W[side][a][j]
        con.executemany("INSERT INTO items VALUES (%s)" % ",".join("?" * 13), rows)
    con.commit(); con.close()
    for a in ARMS:
        e = sqlite3.connect(os.path.join(root, "intent_emb_%s.db" % a))
        e.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        e.executemany("INSERT INTO embeddings VALUES (?,?)", [(t, np.asarray(v, dtype=">f4").tobytes()) for t, v in vecs[a].items()])
        e.commit(); e.close()


def _fctx(root):
    return Ctx(data_root=root, k_grid=FIX_GRID, knn_k=(5, 20), seeds=5, width=8, native=dict(FIX_NATIVE), check_pins=False,
               gold={"massive": (4, 32), "clinc": (4, 32)})


def _ref_sc1(root, corpus):
    """Independent recomputation of SC1's statistics for (qwen3, gemma) native on one corpus: TRAIN rows read with sqlite directly,
    labels by intent_transfer_s0.skmeans, AMI by sklearn, then the normalisation, scipy linregress slopes, the t interval, and the
    Spearman of the mean curve computed here."""
    from scipy.stats import linregress, spearmanr, t as tdist
    from sklearn.metrics import adjusted_mutual_info_score as AMI
    ITS = TL.its_module()
    con = sqlite3.connect(os.path.join(root, "intent_transfer_corpora_v1.db"))
    tr = [t for (t,) in con.execute("SELECT text FROM items WHERE corpus = ? AND side = 'TRAIN' AND drop_reason IS NULL AND is_oos = 0 ORDER BY item_id", (corpus,))]
    con.close()
    X = {}
    for a in ("qwen3", "qwen3_q8", "gemma"):
        e = sqlite3.connect(os.path.join(root, "intent_emb_%s.db" % a))
        V = {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in e.execute("SELECT query, vector FROM embeddings")}
        e.close()
        M = np.array([V[t] for t in tr])
        X[a] = M / np.linalg.norm(M, axis=1, keepdims=True)
    lab = {a: {k: [np.argmax(X[a] @ ITS.skmeans(X[a], k, SEED + s).T, axis=1) for s in range(5)] for k in FIX_GRID} for a in X}
    den = {k: np.mean([AMI(lab["qwen3"][k][s], lab["qwen3_q8"][k][t], average_method="arithmetic") for s in range(5) for t in range(5)]) for k in FIX_GRID}
    N = {(s, t): [AMI(lab["qwen3"][k][s], lab["gemma"][k][t], average_method="arithmetic") / den[k] for k in FIX_GRID] for s in range(5) for t in range(5)}
    curve = [np.mean([N[st][j] for st in N]) for j in range(len(FIX_GRID))]
    slopes = [linregress(np.log2(FIX_GRID), N[st]).slope for st in N]
    m, sd = float(np.mean(slopes)), float(np.std(slopes, ddof=1))
    hi = m + tdist.ppf(0.975, 24) * sd / 5.0
    aq4 = {k: {(s, c): AMI(lab["qwen3"][k][s], lab["qwen3_q8"][k][c], average_method="arithmetic") for s in range(5) for c in range(5)} for k in FIX_GRID}
    aqg = {k: {(s, t): AMI(lab["qwen3"][k][s], lab["gemma"][k][t], average_method="arithmetic") for s in range(5) for t in range(5)} for k in FIX_GRID}
    bhi = _ref_boot_hi(FIX_GRID, aqg, aq4)
    return dict(rho=float(spearmanr(curve, FIX_GRID).correlation), mean=m, hi=hi, bhi=bhi, curve=curve)


def _ref_boot_hi(ks, aqg, aq4, n=5):
    """The crossed-seed bootstrap's 97.5 percentile by explicit loops and scipy linregress (independent of seed_boot's arrays)."""
    from scipy.stats import linregress
    rng = np.random.RandomState(BOOT_SEED)
    vals = []
    for _ in range(BOOT_B):
        a = rng.randint(0, n, n); b = rng.randint(0, n, n); c = rng.randint(0, n, n)
        y = []
        for k in ks:
            den = sum(aq4[k][(a[i], c[j])] for i in range(n) for j in range(n)) / (n * n)
            y.append(sum(aqg[k][(a[i], b[j])] / den for i in range(n) for j in range(n)) / (n * n))
        vals.append(linregress(np.log2(ks), y).slope)
    return float(np.percentile(vals, 97.5))


def _grid_tables(ks, slope, n=5):
    """Synthetic AMI tables: AMI(qwen3_s, gemma_t)(k) = 0.9 + slope[s][t] x (log2 k - 1); AMI(q4_s, q8_c) = 1 (den 1)."""
    dec = {k: {(s, t): 0.9 + slope[s][t] * (math.log2(k) - 1.0) for s in range(n) for t in range(n)} for k in ks}
    norm = {k: {(s, c): 1.0 for s in range(n) for c in range(n)} for k in ks}
    return dec, norm


def _brute_cka(X, Y):
    n = len(X)
    K, L = X @ X.T, Y @ Y.T
    np.fill_diagonal(K, 0.0); np.fill_diagonal(L, 0.0)
    def h(A, B):
        one = np.ones(n)
        return (np.trace(A @ B) + (one @ A @ one) * (one @ B @ one) / ((n - 1) * (n - 2)) - 2.0 / (n - 2) * (one @ A @ B @ one)) / (n * (n - 3))
    return h(K, L) / math.sqrt(h(K, K) * h(L, L))


def selftest():
    checks = 0
    with scratch_dir.scratch("scale_agree_selftest") as tmp:
        # unit: CKA (feature form) vs the O(n^2) definition (S16); kNN self-exclusion (S17); T24
        rng = np.random.default_rng(1)
        A = rng.standard_normal((60, 7)); Bm = A @ rng.standard_normal((7, 5)) + 0.5 * rng.standard_normal((60, 5))
        assert abs(cka_debiased(A, Bm) - _brute_cka(A, Bm)) < 1e-10; checks += 1
        U = TL.unit(rng.standard_normal((50, 4)))
        nb = knn_lists(U, 10)
        assert not np.any(nb == np.arange(50)[:, None]) and nb.shape == (50, 10); checks += 1
        from scipy.stats import t as tdist
        assert abs(T24 - tdist.ppf(0.975, 24)) < 1e-12; checks += 1
        # ---------------- F1: split on both corpora -> HELD; numbers vs the independent recomputation
        r1 = os.path.join(tmp, "f1")
        _fixture(r1, {"massive": "split", "clinc": "split"})
        outp = os.path.join(tmp, "f1_out", "o.txt")
        rc, txt = ZC.capture(main, ["--run", "--out", outp], _fctx(r1))
        assert rc == 0, txt[-3000:]; checks += 1
        assert txt.splitlines()[1].startswith("POOL: none read"); checks += 1
        for c in CORPORA:
            ref = _ref_sc1(r1, c)
            ln = ZC.line(txt, "SC1 %s " % c)
            want = "rho %+.3f; mean slope %+.4f per log2 k, 95%% crossed-seed bootstrap interval [" % (ref["rho"], ref["mean"])
            assert want in ln and (", %+.4f] (B 2000" % ref["bhi"]) in ln and (", %+.4f]; normalised" % ref["hi"]) in ln, (ln, ref); checks += 1   # S4-S6 S9 S13-S15 S20-S23
            assert ln.split("): ")[1].startswith("DECREASES"), ln; checks += 1
        sc1 = ZC.line(txt, "SC1 (DECIDING")
        assert sc1.endswith("): HELD -- massive DECREASES, clinc DECREASES"), sc1; checks += 1
        assert ZC.line(txt, "F-SC ") == "F-SC (fires iff SC1 FAILED): NOT FIRED"; checks += 1
        p1 = ZC.line(txt, "P1 ")
        assert p1.endswith("SC1 HELD predicted at 0.60, occurred: yes, Brier 0.1600"), p1; checks += 1
        wl = ZC.line(txt, "SC1 at 256-d")
        w_hi = float(wl.split("massive rho ")[1].split(" hi ")[1].split(",")[0])
        n_hi = float(ZC.line(txt, "SC1 massive ").split("95% crossed-seed bootstrap interval [")[1].split(", ")[1].split("]")[0])
        assert abs(w_hi - n_hi) > 1e-4, (wl, n_hi); checks += 1                                  # the slice is its own computation
        # write-once (S11)
        body = open(outp, encoding="utf-8").read()
        assert ZC.line(body, "SC1 (DECIDING") == sc1; checks += 1
        rc2, txt2 = ZC.capture(main, ["--run", "--out", outp], _fctx(r1))
        assert rc2 == ("refused", 2) and "WRITE-ONCE" in txt2 and open(outp, encoding="utf-8").read() == body; checks += 1
        # dry-run
        rc3, txt3 = ZC.capture(main, ["--dry-run"], _fctx(r1))
        assert rc3 == 0 and txt3.rstrip().endswith("--dry-run: no AMI computed, nothing written.") and "census massive: 320 TRAIN rows" in txt3, txt3[-1500:]; checks += 1
        # ---------------- F2: same on both -> FAILED, F-SC FIRED (S10), P1 Brier
        r2 = os.path.join(tmp, "f2")
        _fixture(r2, {"massive": "same", "clinc": "same"})
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f2_out", "o.txt")], _fctx(r2))
        assert rc == 0, txt[-2000:]; checks += 1
        assert ZC.line(txt, "SC1 (DECIDING").endswith("): FAILED -- massive no, clinc no"), ZC.line(txt, "SC1 (DECIDING"); checks += 1
        assert ZC.line(txt, "F-SC ").startswith("F-SC (fires iff SC1 FAILED): FIRED -- the record's 'coarse holds, fine diverges'"); checks += 1
        assert ZC.line(txt, "P1 ").endswith("occurred: no, Brier 0.3600"); checks += 1
        # ---------------- F3: split MASSIVE, same CLINC -> MIXED (S3)
        r3 = os.path.join(tmp, "f3")
        _fixture(r3, {"massive": "split", "clinc": "same"})
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f3_out", "o.txt")], _fctx(r3))
        assert rc == 0, txt[-2000:]; checks += 1
        assert ZC.line(txt, "SC1 (DECIDING").endswith("): MIXED -- massive DECREASES, clinc no"), ZC.line(txt, "SC1 (DECIDING"); checks += 1
        assert ZC.line(txt, "F-SC ") == "F-SC (fires iff SC1 FAILED): NOT FIRED"; checks += 1
        # ---------------- decide-path boundaries (S1 S2 S12) and P1 per corpus (S18)
        assert decreases(-0.7, -1e-9) is True and decreases(-0.69, -1.0) is False and decreases(-0.9, 0.0) is False; checks += 1
        assert decreases(np.float64(-0.7), np.float64(-0.001)) is True; checks += 1
        assert kstar([2, 4, 8], [0.9, 0.8, 0.7]) == 8 and kstar([2, 4], [0.81, 0.85]) is None; checks += 1
        out = []
        fake = {c: {"native": None, "w8": None} for c in CORPORA}
        def mk(slopes):
            sl = [[slopes[5 * s + t] for t in range(5)] for s in range(5)]
            dec, norm = _grid_tables(FIX_GRID, sl)
            curve = [float(np.mean([dec[k][st] for st in dec[k]])) for k in FIX_GRID]
            return dict(ks=list(FIX_GRID), curves={DECIDING_PAIR: curve}, slopes={DECIDING_PAIR: slopes},
                        ami={DECIDING_PAIR: dec, NORM_PAIR: norm}, nseeds=5)
        fake["massive"]["native"] = fake["massive"]["w8"] = mk([-0.10 + 0.001 * i for i in range(25)])
        fake["clinc"]["native"] = fake["clinc"]["w8"] = mk([-0.01 + 0.0001 * i for i in range(25)])
        Cx = _fctx(r1)
        _, vv = verdicts(Cx, fake, out)
        p1l = [l for l in out if l.startswith("P1 ")][0]
        assert vv["v"] == "HELD" and "massive -0.0880, clinc -0.0088): FAILED" in p1l, p1l; checks += 1      # each corpus, not the mean (-0.048)
        # ---------------- D-1: seed main effects dominate (qwen3 seed effect e_s, small gemma effect): the naive t(24) interval
        # lies below 0 (DECREASES under the withdrawn reading) but the crossed-seed bootstrap reaches above 0 -> does not decrease
        e = [-0.06, -0.03, 0.0, 0.03, 0.06]; f = [-0.004, -0.002, 0.0, 0.002, 0.004]
        sl = [[-0.02 + e[s] + f[t] for t in range(5)] for s in range(5)]
        dec, norm = _grid_tables(FIX_GRID, sl)
        flat = [sl[s][t] for s in range(5) for t in range(5)]
        m_, sd_, lo_, hi_, _ = slope_interval(flat)
        blo_, bhi_, bsd_ = seed_boot(FIX_GRID, dec, norm, 5)
        assert hi_ < 0 and bhi_ > 0 and bsd_ > 1.8 * sd_ / 5.0, (hi_, bhi_, bsd_, sd_); checks += 1
        assert abs(bhi_ - _ref_boot_hi(FIX_GRID, dec, norm)) < 1e-12; checks += 1
        # crossed ANOVA on the additive grid -0.02 + e_s + f_t: MS_E = 0, MS_A = 5 var(e), MS_B = 5 var(f) (ddof 1)
        from scipy.stats import t as tdist4
        va, vb = float(np.var(e, ddof=1)), float(np.var(f, ddof=1))
        se_hand = math.sqrt((5 * va + 5 * vb) / 25.0)
        alo_, ahi_, ase_ = crossed_anova(flat, 5)
        assert abs(ase_ - se_hand) < 1e-12 and abs(ahi_ - (-0.02 + tdist4.ppf(0.975, 4) * se_hand)) < 1e-12 and ahi_ > 0, (ase_, se_hand, ahi_); checks += 1
        noisy = [x + (0.003 if (i * 7) % 3 == 0 else -0.0015) for i, x in enumerate(flat)]
        Mn = np.array(noisy).reshape(5, 5); gm = Mn.mean(); ra = Mn.mean(1); cb = Mn.mean(0)
        mse = sum((Mn[i, j] - ra[i] - cb[j] + gm) ** 2 for i in range(5) for j in range(5)) / 16.0
        se_n = math.sqrt((5 * float(np.var(ra, ddof=1)) + 5 * float(np.var(cb, ddof=1)) - mse) / 25.0)
        assert mse > 0 and abs(crossed_anova(noisy, 5)[2] - se_n) < 1e-12; checks += 1
        g = {c: {"native": None, "w8": None} for c in CORPORA}
        curve = [float(np.mean([dec[k][st] for st in dec[k]])) for k in FIX_GRID]
        for c in CORPORA:
            g[c]["native"] = g[c]["w8"] = dict(ks=list(FIX_GRID), curves={DECIDING_PAIR: curve}, slopes={DECIDING_PAIR: flat},
                                               ami={DECIDING_PAIR: dec, NORM_PAIR: norm}, nseeds=5)
        out2 = []
        _, v2 = verdicts(Cx, g, out2)
        l2 = [l for l in out2 if l.startswith("SC1 massive ")][0]
        assert v2["v"] == "FAILED" and "): does not decrease -- rho -1.000;" in l2 and ("bootstrap interval [%+.4f, %+.4f]" % (blo_, bhi_)) in l2 and ("crossed-ANOVA t(4)-interval [%+.4f, %+.4f]" % (alo_, ahi_)) in l2 and ("t(24)-interval (treats the 5 x 5 grid as 25 independent pairs) [%+.4f, %+.4f]" % (lo_, hi_)) in l2, l2; checks += 1   # S19 S24
        assert [l for l in out2 if l.startswith("F-SC ")][0].startswith("F-SC (fires iff SC1 FAILED): FIRED"); checks += 1
    assert checks == SELFTEST_CHECKS, "selftest ran %d checks, pinned %d" % (checks, SELFTEST_CHECKS)
    print("%s SELFTEST OK: %d value-asserting checks (pinned %d)" % (TAG, checks, SELFTEST_CHECKS))
    return 0


# ----------------------------------------------------------------------------------------------- main
def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="SCALE-AGREE readout (zero calls; the intent arms read no pool; --mmlu is a pool reader)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--mmlu", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--data-root", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        res = ZC.run_mutants(os.path.abspath(__file__), MUTANTS)
        return 0 if all(r[2] == "killed" for r in res) else 1
    if ctx is None:
        ctx = Ctx(data_root=os.path.abspath(a.data_root) if a.data_root else ROOT, mmlu=a.mmlu)
    if a.dry_run:
        return dry_run(ctx)
    tag = "scale_agree_mmlu" if ctx.mmlu else "scale_agree"
    return run(ctx, a.out or ZC.default_out(tag, tag + "_outcome.txt"))


if __name__ == "__main__":
    sys.exit(main())
