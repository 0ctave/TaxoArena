"""GRANULARITY-GT readout: is the [LF] intent tree right at a coarser gold level (best-cut AMI vs an average-link hierarchy, GR1)
and is its hierarchy better than random arrangements of the same leaves (dendrogram purity vs 200 matched-shape random trees, GR2)?
ZERO LLM / judge calls; no construction; no embedding call; no Gradle; read-only.

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-10-04 (before any code or call) — GRANULARITY-GT: is
the [LF] intent tree right at a coarser gold level (best-cut AMI vs an average-link hierarchy) and is its hierarchy better than
random arrangements of the same leaves (dendrogram purity vs 200 matched-shape random trees)? (zero calls; CPU readout; T5)"
(L24317-L24328, _as_of b66b075d); state docs/agents/results/GRANULARITY-GT.json; provenance docs/literature/
2026-10-04_testing_logic_review.md (bd5ca001) section 3, T5.

DATA OBJECTS. INTENT-TRANSFER-S1's builds as built: M-AF (MASSIVE, slug m_af) and C-AF (CLINC, slug c_af), each read from
snapshots.db by the run log's single "Snapshot ID:" (never the latest row; S1 definition (c)), under --data-root (default
TAXOARENA_DATA_ROOT or this checkout; the S1 builds live in .claude/worktrees/intent-s1-run). Salt-1 sides of the S1 ingest DB;
qwen3 vectors (intent_emb_qwen3.db) at the tree's slice; gold MASSIVE scenario / intent and CLINC domain / intent (coarse / fine),
read for scoring only. Not a union-pool reader. EVAL is read once, after every TRAIN fit (S1's phase guard).

INSTRUMENT (imported, blob-pinned, never edited): tools/analysis/intent_transfer_s1.py blob:4e9d9d05 (LF) (S1: arm_presence,
snapshot_row, tree_of, load_tree_checked, make_arm, side_rows, fit_idx, eval_rows, flat_leaf, load_raw, dendrogram_purity,
tree_parent_restricted, derive_inputs, check_heavy; S1 checks its own pins of intent_transfer_s0.py and g13_comparator.py);
intent_transfer_s0.py (S0: load_corpora, pin_check, codes, comp_weights, pct_ci, kish, skmeans, assign, unit).

READERS' DEFINITIONS (the registered text is silent on these; the builder's readings, each printed in the outcome):
  G1 CUTS. Tree: depth = edges from the root along treeParents (S1 (b)); the depth-d cut maps a leaf to its ancestor at depth d,
     a leaf shallower than d stays itself; d = 1 .. D_max (D_max = the deepest leaf; the D_max cut is the leaf partition).
     k_d = the number of distinct cut nodes over the tree's leaves. Average-link and bisecting k-means are cut at the SAME counts
     k_d (matched-size cuts; a binary dendrogram has no comparable depth). The average-link best over every k in 2..L is printed
     beside, DESCRIPTIVE, never deciding (it searches L - 1 cuts against the tree's D_max).
  G2 FILING. Every EVAL item is filed ONCE at the leaf level and lifted: the tree by flatLeaf (argmax cos to the leaf vmfMu, S1
     definition (a)); average-link and bisecting by argmax cos to their leaf centroids (unit mean of the leaf's TRAIN items at the
     tree's slice). Every hierarchy has L leaves (the tree's leaf count): average-link = the first n - L merges of
     scipy linkage(TRAIN, average, cosine) replayed (union-find), the last L - 1 merges = its hierarchy over those L clusters,
     cut at k = the coarse-to-fine expansion of the last k - 1 merges; bisecting spherical k-means (seeds 0-4) = repeatedly split
     the leaf with the largest spherical inertia sum(1 - cos(x, unit mean)) (ties to the smaller id) by S0.skmeans(., 2, seed x
     1000003 + split index) until L leaves (a split leaving a side empty marks the leaf unsplittable), cut at k = the leaves after
     k - 1 splits. All fits on the arm's TRAIN items (S1.fit_idx: TRAIN only; an EVAL / GATE / OOS / dropped row REFUSES).
  G3 AMI = adjusted mutual information (Vinh, Epps, Bailey 2010), arithmetic normaliser (sklearn's default), exact expected MI
     (hypergeometric), item weights = integer bootstrap multiplicities (copies are distinct items); both labellings with one
     cluster = 1.0. Asserted equal to sklearn.metrics.adjusted_mutual_info_score in the selftest. Best-cut AMI = max over the cuts
     of G1; best depth = the shallowest maximiser.
  G4 GR1. D1 = best-cut AMI(tree, coarse) - best-cut AMI(average-link, coarse) on EVAL; the 95% interval = the PERCENTILE interval
     of D1 over S0.comp_weights draws (CK-CLOSE components, B 2,000, seed 20261004 + corpus offset), the best cut re-chosen in
     every draw; spread_B = max - min over seeds 0-4 of best-cut AMI(bisecting, coarse) (point, EVAL). Per corpus: TREE-BETTER iff
     D1 > spread_B AND lo > 0; AVG-BETTER iff D1 < -spread_B AND hi < 0; NEITHER otherwise. GR1 = TREE-BETTER iff TREE-BETTER on
     both corpora, AVG-BETTER iff AVG-BETTER on both, MIXED otherwise (verbatim: NEITHER on both reads MIXED).
  G5 GR2. DP = Heller-Ghahramani dendrogram purity against the COARSE level over EVAL items filed by flatLeaf (S1 R7,
     S1.dendrogram_purity unchanged), hierarchy = treeParents. Random tree r (r = 1..200, numpy default_rng(20261004) per corpus):
     the tree's shape (parent map) unchanged, the leaf ids permuted over the leaf positions (each EVAL item moves with its leaf).
     p97.5 = numpy.percentile(., 97.5) (linear interpolation). ABOVE-RANDOM iff DP(tree) > p97.5 (strict). GR2 HELD iff
     ABOVE-RANDOM on both corpora, FAILED iff on neither, MIXED otherwise. Monte Carlo SE of p97.5 = SD of p97.5 over 2,000
     resamples of the 200 values (seed 20261005). DP of the average-link and bisecting hierarchies printed, DESCRIPTIVE.
  G6 SUPPORT. Realised n, components G, Kish mean cluster size (the DEFF at ICC = 1), n_eff = n / Kish, SE = the bootstrap SD of
     D1, MDE80 = 2.8 x SE, printed beside the registered DEFF 1.0093 (CLINC carried as a declared assumption), n_eff about 4,900,
     SE 0.0050, MDE80 0.014 and the registered VERDICT LINES.
  G7 PREDICTIONS. Numeric "X [lo, hi]" HELD iff the point lies in the closed interval; probabilities scored by Brier on their event.
     P1's probability clause "GR1 NEITHER 0.6" names no outcome of GR1's overall rule (TREE-BETTER / AVG-BETTER / MIXED): it is
     printed NOT SCORED with the per-corpus words, pending the registrar (registration defect GG-1, handed back; not resolved here).
     P3's event = the coarse best depth < D_max on BOTH corpora.
  Homogeneity / completeness / V at the leaf level (sklearn) for every arm and both levels; the fine-level AMI table: DESCRIPTIVE.

HYGIENE. Reads only: the ingest DB and intent_emb_qwen3.db (S0.pin_check STRICT against experiment_configs/intent_transfer_s0_pins
.json, re-hashed after the readout: a change refuses and nothing is written), snapshots.db (read-only; a non-empty -wal refuses; the
graph JSON sha256 of each tree printed) and the two run dirs. The run manifest's intent_build counts must equal the re-derived build
(S1.load_tree_checked). The census of EVAL (kept, in-scope, salt 1) must be within 5% of the registered MASSIVE 4,946 / 4,923 and
CLINC 6,672 / 6,672, else REFUSE before any statistic. REFUSES while a foreign java / heavy process runs. Threads OMP / OPENBLAS /
MKL = 1. Temp files: tools/analysis/scratch_dir.py is imported first (tempfile on E:/TaxoArena_tmp, removed at exit).

OUTPUT. <out-dir>/granularity_gt_outcome.txt and <out-dir>/SHA256SUMS.txt, both WRITE-ONCE (mode x; an existing path REFUSES
before any read). Default out-dir E:/TaxoArena_backup_<date>_granularity_gt (outputs are never committed). --dry-run writes
nothing and computes no EVAL statistic.

LAUNCH SEQUENCE (zero calls; one heavy process; nothing else reading the S1 DBs is required, rule 7 is not engaged: no pool):
  python tools/analysis/granularity_gt.py --selftest
  python tools/analysis/granularity_gt.py --mutants
  python tools/analysis/granularity_gt.py --dry-run --data-root .claude/worktrees/intent-s1-run
  python tools/analysis/granularity_gt.py --run --data-root .claude/worktrees/intent-s1-run [--out-dir E:/...]   # the file of record

SELFTEST (fixtures only, built under scratch_dir on E:; 201 value checks): ST-AMI (ami == sklearn on 12 random pairs, weighted ==
sklearn on the expanded copies, edge cases, best_cut max and shallowest tie); ST-HIER (hand tree depth cuts and k_d incl. a shallow
leaf, frontier order coarse -> fine, average-link and bisecting recover planted nested groups, the largest-inertia split rule,
matched-shape draws = the explicit permutation, MC SE); ST-VERDICT (every GR1 / GR2 / overall branch and strict boundary, spread_B
over the five seeds, inclusive bands, Brier); ST-RENDER (every GR1 / GR2 / FAILS / F-GR / P1 / P2 / P3 print branch on derived
results, values asserted); ST-E2E (the REAL run() on two on-disk data roots (ingest DB, emb DB, snapshots.db with a decoy later row,
run dirs, manifests, pins): an ALIGNED tree -> GR1 TREE-BETTER on both, GR2 HELD, P2 / P3 TRUE; a SCRAMBLED tree -> NEITHER on both
= GR1 MIXED, GR2 FAILED, F-GR FIRES, FAILS names both; every deciding number (n, components, Kish, n_eff, k_d, tree AMI per depth,
average-link AMI per matched k, D1, DP, random p97.5) asserted against an INDEPENDENT recomputation (sklearn AMI on a parent walk of
the graph JSON, scipy cut_tree, an explicit permutation loop); the printed GR1 / GR2 lines; SHA256SUMS; TRAIN-only fit audit;
dry-run writes nothing and never unlocks EVAL); ST-REFUSE (EVAL before the TRAIN freeze; a fit on EVAL rows; census; pin mismatch;
null pins (before any fit); an outcome planted mid-run is not overwritten; an emb DB changed mid-run refuses at the after-check
and writes nothing; absent build; two Snapshot IDs; manifest counts; non-empty -wal; the instrument pin; write-once).

MUTANTS (2026-10-04, --mutants: in-process source edits, one at a time, against the selftest cases named): 47 of 47 KILLED.
  M01 best cut min | M02 AMI without EMI | M03 AMI max normaliser | M04 GR1 bar 0 | M05 GR1 interval clause dropped | M06 GR1 >=
  spread | M07 GR1 AVG interval dropped | M08 GR1 TREE on either corpus | M09 NEITHER-both reads NEITHER | M10 p95 | M11 GR2 >= |
  M12 GR2 HELD on either | M13 GR2 FAILED unless both | M14 no permutation | M15 random binary trees (shape not matched) | M16
  spread_B seeds 0-3 | M16b spread_B one pair | M17 D1 vs bisecting | M18 EVAL statistic on TRAIN rows | M19 average-link fit on
  TRAIN + EVAL (refusal) | M20 leaf depth cut dropped | M21 shallow leaf to its parent | M22 frontier fine-first (crash) | M23
  bootstrap weights ignored | M24 GR1 on fine | M25 DP on fine | M26 bands exclusive | M27 P2 wrong event | M28 P3 <= D_max | M29
  F-GR on MIXED | M30 FAILS line dropped | M31 mode w | M32 write-once pre-check removed (crash) | M33 census removed | M34 absent
  build admitted | M35 pins not strict | M36 instrument pin unchecked | M37 MDE 1.96 | M38 n_eff from components | M39 bisect by
  size | M40 cut not lifted | M41 MIXED sentence for AVG-BETTER | M42 P1 probability clause scored | M43 root cut dropped | M44
  first cut only | M45 pin after-check removed | M46 one leaf for all. First pass: 36 of 42; survivors fixed by new checks (the
  mid-run race for mode x, duplicate-text components for n_eff, a discriminating inertia fixture, spread_b() refactor with a seed-4
  case, a strict-before-fit null-pin check, render sentences asserted exactly).

HIER-F (PRE-DATA ADDENDUM, docs/judge_v2_program.md L24430-L24441, 633255f2; GRANULARITY-GT's criteria unchanged). Same arms, same
EVAL, same filing (G2), printed after GRANULARITY-GT's block. Builder's readings where the registration is silent:
  H1 HF = sum_c (n_c / n) max over EVERY node v (leaves, internal nodes and the root) of F(c, v) = 2 n_cv / (n_v + n_c), item counts
     of EVAL filed at the leaf level; HF1 and HF2 are read on the FINE gold (HF1's text names fine; HF2 names no level: read on the
     same HF as HF1), the coarse HF DESCRIPTIVE. HF1: D = HF(tree) - HF(average-link); spread_B = the five bisecting seeds' HF range
     (spread_b); the 95% percentile component-bootstrap interval (B as GRANULARITY-GT, seed 20261004 + corpus offset + 10); the word
     rule is GR1's (gr1_corpus), per corpus only (no overall rule is registered). HF2: the SAME 200 matched-shape permutations as GR2
     (default_rng(20261004), one permutation of the L leaves per draw); above_random = HF(tree) > p97.5 strictly; HELD / FAILED /
     MIXED as GR2; F-HF fires iff FAILED.
  H2 taxonomic P / R / F (DESCRIPTIVE): micro hierarchical P / R on label sets; every non-root node carries the TRAIN plurality coarse
     and fine label of the TRAIN items filed under it (the same filing rule on TRAIN; ties to the smaller code; no TRAIN item = no
     label); an EVAL item's predicted set = the labels on its leaf's ancestor path, its gold set = {coarse, fine}.
  H3 ancestor-F1 (DESCRIPTIVE): each gold class sits at its best-F node (H1, coarse and fine); predicted (C, f) iff C's node is an
     ancestor-or-self of f's node (leaf-set containment); gold (C, f) iff f nests in C; F1 over all (coarse, fine) pairs on EVAL.
  H4 Fowlkes-Mallows (DESCRIPTIVE): level-wise at the tree's depth cuts and at the matched k_d for the other arms, against both gold
     levels; the cumulative curve B_k (k = 2..L) against the fine gold for average-link and bisecting seed 0.
  H5 predictions: P1 D band per corpus; "HF1 NEITHER 0.60" scored per corpus (HF1 has per-corpus words only); P2 HF2 HELD 0.75;
     P3 (MMLU-Pro recovery) printed NOT EVALUATED.
  H6 NOT BUILT: the MMLU-Pro re-draw arm (DESCRIPTIVE; a pool reader under rule 7 on four other trees): stated, P3 not scored.
HIER-F selftest: ST-HF (node matrix; HF credits an internal node; HF == brute force; weighted == expanded; draw 0 == the explicit
permutation of GR2's stream; taxonomic P 2/5 R 2/4 hand case; ancestor-F1 1.0 / 0.75 hand cases incl. self; FM == sklearn) +
ST-E2E (HF tree / average-link / D == brute force over explicit node item sets (graph walk; scipy cut_tree clusters at every k); HF
random p97.5 == an explicit permutation loop; FM per depth == sklearn; HF1 / HF2 words; printed lines; HF2 overall) + ST-RENDER
(HF2 MIXED while GR2 HELD, FAILED with F-HF, HELD while GR2 FAILED; HF P1 / P2 / P3 lines) + ST-VERDICT (above_random).
HIER-F mutants (22, all KILLED; 69 of 69 overall): H01 HF leaves only | H02 unweighted class mean | H03 precision only | H04 coarse
gold | H05 D vs bisecting | H06 bar 0 | H07 bootstrap weights ignored | H08 no permutation | H09 HF2 reads GR2's words | H10 F-HF on
MIXED | H11 FAILS line dropped | H12 P1 Brier on TREE-BETTER | H13 P2 wrong event | H14 taxonomic P/R swapped | H15 root labels |
H16 ancestor strict | H17 FM arithmetic mean | H18 another random stream | H19 HF1 interval clause dropped | H20 median for p97.5
(survived first, above_random factored with a between-median-and-p97.5 case) | H21 >= (survived first, equality case added) | H22
HF2 on one draw.

NOT DONE (stated): no run (the operator's, after READY); the readout's real-data runtime estimated, not measured (AMI 0.15 s per
8 cuts at n 6,672; average-link 9 s on 13,487 x 256 synthetic; about 20-30 min for both corpora at B 2,000).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import sys             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
import scratch_dir     # noqa: E402,F401  (temp on E:, removed at exit)

import argparse        # noqa: E402
import contextlib      # noqa: E402
import datetime        # noqa: E402
import hashlib         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import re              # noqa: E402
import sqlite3         # noqa: E402
import tempfile        # noqa: E402

import numpy as np     # noqa: E402
from scipy.special import gammaln  # noqa: E402

import intent_transfer_s1 as S1        # noqa: E402
import intent_transfer_s0 as S0        # noqa: E402
import split_side as SS                # noqa: E402
import intent_ingest as II             # noqa: E402


def _blob(path):
    d = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


PINNED_CODE = {"intent_transfer_s1.py": "4e9d9d05fbdf14d0a85966b4c897cfbfd779186d"}
TAG = "[GRAN-GT]"
REGISTRATION = ("docs/judge_v2_program.md L24317-L24328 (_as_of b66b075d), \"## Registered 2026-10-04 (before any code or call) — "
                "GRANULARITY-GT: ...\"")
ARMS_USED = {"massive": "M-AF", "clinc": "C-AF"}
CORPORA = ("massive", "clinc")
SEEDS_B = (0, 1, 2, 3, 4)
N_RANDOM = 200
SEED_RANDOM = 20261004
SEED_MC = 20261005
SEED_BOOT = 20261004
BOOT_OFF = {"massive": 1, "clinc": 2}
BOOT_B = 2000
MC_B = 2000
Q_RANDOM = 97.5
CENSUS_TOL = 0.05
REGISTERED_N = {"massive": (4946, 4923), "clinc": (6672, 6672)}
REG_SUPPORT = "DEFF 1.0093 (Kish, S0; MASSIVE; carried to CLINC as a declared assumption); n_eff about 4,900; SE of D1 0.0050; MDE80 0.014"
VERDICT_LINES = {"GR1": "DESCRIPTIVE-ONLY at the prediction (-0.01 lies inside 0.014 of 0)",
                 "GR2": "SCOREABLE as a classification (200-draw Monte Carlo SE printed)"}
P1_BAND = (-0.01, -0.05, 0.03)
P1_NEITHER = 0.6
P2_HELD = 0.75
P3_SHALLOW = 0.9
HF_REGISTRATION = ("docs/judge_v2_program.md L24430-L24441 (_as_of 633255f2), \"## Registered 2026-10-04 (before any code or call) - "
                   "HIER-F: (PRE-DATA ADDENDUM TO GRANULARITY-GT ...)\"")
HF_BOOT_OFF = 10
HF_P1_BAND = (0.01, -0.03, 0.05)
HF_P1_NEITHER = 0.60
HF_P2_HELD = 0.75
HF_VERDICT_LINES = {"HF1": "DESCRIPTIVE-ONLY (the prediction +0.01 lies inside the MDE 0.014)", "HF2": "SCOREABLE (a percentile classification)"}
OUTCOME = "granularity_gt_outcome.txt"
SUMS = "SHA256SUMS.txt"


class Refused(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise Refused("%s REFUSED: %s" % (TAG, msg))


def check_code_pins():
    for name, want in PINNED_CODE.items():
        got = _blob(os.path.join(HERE, name))
        if got != want:
            refuse("%s blob %s != the pinned %s (the instrument is imported unchanged)" % (name, got, want))
    S1.check_code_pins()


# ================================================================================================ AMI (G3)
def ami(t, p, w=None):
    """Adjusted mutual information, arithmetic normaliser, exact EMI; integer item weights (bootstrap multiplicities)."""
    t = np.asarray(t, dtype=np.int64)
    p = np.asarray(p, dtype=np.int64)
    w = np.ones(len(t)) if w is None else np.asarray(w, dtype=np.float64)
    kt, kp = int(t.max()) + 1, int(p.max()) + 1
    cont = np.bincount(t * kp + p, weights=w, minlength=kt * kp).reshape(kt, kp)
    cont = np.rint(cont).astype(np.int64)
    cont = cont[cont.sum(1) > 0][:, cont.sum(0) > 0]
    R, C = cont.shape
    if R == C == 1 or R == C == 0:
        return 1.0
    N = int(cont.sum())
    a, b = cont.sum(1), cont.sum(0)
    nz = cont > 0
    nij = cont[nz].astype(np.float64)
    ai = np.broadcast_to(a[:, None], cont.shape)[nz].astype(np.float64)
    bj = np.broadcast_to(b[None, :], cont.shape)[nz].astype(np.float64)
    mi = float((nij / N * (np.log(nij) + np.log(N) - np.log(ai) - np.log(bj))).sum())
    pa, pb = a / N, b / N
    ht = -float((pa * np.log(pa)).sum())
    hp = -float((pb * np.log(pb)).sum())
    # exact expected MI over the hypergeometric (Vinh et al. 2010, eq. 24a), vectorised over (i, j, n_ij)
    A = np.broadcast_to(a[:, None], (R, C)).ravel().astype(np.int64)
    B = np.broadcast_to(b[None, :], (R, C)).ravel().astype(np.int64)
    lo = np.maximum(1, A + B - N)
    hi = np.minimum(A, B)
    cnt = np.maximum(hi - lo + 1, 0)
    tot = int(cnt.sum())
    emi = 0.0
    if tot:
        rep = np.repeat(np.arange(len(A)), cnt)
        off = np.repeat(np.cumsum(cnt) - cnt, cnt)
        n = (lo[rep] + (np.arange(tot) - off)).astype(np.float64)
        Ar, Br = A[rep].astype(np.float64), B[rep].astype(np.float64)
        lg = (gammaln(Ar + 1) + gammaln(Br + 1) + gammaln(N - Ar + 1) + gammaln(N - Br + 1) - gammaln(N + 1.0) - gammaln(n + 1)
              - gammaln(Ar - n + 1) - gammaln(Br - n + 1) - gammaln(N - Ar - Br + n + 1))
        emi = float((n / N * (np.log(N) + np.log(n) - np.log(Ar) - np.log(Br)) * np.exp(lg)).sum())
    norm = (ht + hp) / 2.0
    den = norm - emi
    eps = np.finfo(np.float64).eps
    den = min(den, -eps) if den < 0 else max(den, eps)
    return (mi - emi) / den


def best_cut(truth, labelings, w=None):
    """-> (best AMI, index of the shallowest maximiser) over the cuts (G3)."""
    vals = [ami(truth, lab, w) for lab in labelings]
    j = int(np.argmax(vals))
    return float(vals[j]), j, vals


# ================================================================================================ hierarchies (G1, G2)
def tree_depth_cuts(T):
    """-> [(d, k_d, leaf -> cut code array)] for d = 1 .. D_max; and the leaf depths (G1)."""
    leaves = T["leaves"]
    chains = []
    for lf in leaves:
        ch, x = [lf], lf
        while x in T["tparent"]:
            x = T["tparent"][x]
            ch.append(x)
        chains.append(ch)                     # leaf ... root
    depth = [len(ch) - 1 for ch in chains]
    dmax = max(depth)
    cuts = []
    for d in range(1, dmax + 1):
        node = [ch[dep - d] if dep >= d else ch[0] for ch, dep in zip(chains, depth)]
        _, code = np.unique(np.array(node, dtype=object), return_inverse=True)
        cuts.append((d, int(code.max()) + 1, code.astype(np.int64)))
    return cuts, depth


def frontier_cut(H, k):
    """Leaf -> cut code for the k-cluster cut of an ordered hierarchy H (order = internal nodes coarse -> fine)."""
    k = max(1, min(k, len(H["leaves"])))
    kids = H["kids"]
    front = [H["root"]]
    for node in H["order"][:k - 1]:
        front.remove(node)
        front.extend(kids[node])
    fs = {f: j for j, f in enumerate(sorted(front))}
    code = np.empty(len(H["leaves"]), dtype=np.int64)
    for i, lf in enumerate(H["leaves"]):
        x = lf
        while x not in fs:
            x = H["parent"][x]
        code[i] = fs[x]
    return code


def _kids_of(parent):
    kids = {}
    for c, p in parent.items():
        kids.setdefault(p, []).append(c)
    for p in kids:
        kids[p].sort()
    return kids


def avglink_hierarchy(X, L):
    """G2: average-link (cosine) on the TRAIN rows X; -> H with L leaves, TRAIN leaf labels."""
    from scipy.cluster.hierarchy import linkage
    n = len(X)
    if n < L or L < 1:
        refuse("average-link: %d TRAIN rows < L %d" % (n, L))
    if L == n:
        lab = np.arange(n)
        leaves = ["A%07d" % i for i in range(n)]
        return {"leaves": leaves, "parent": {}, "kids": {}, "order": [], "root": leaves[0]}, lab
    Z = linkage(X, method="average", metric="cosine")
    uf = np.arange(2 * n - 1)
    for j in range(n - L):
        uf[int(Z[j, 0])] = n + j
        uf[int(Z[j, 1])] = n + j

    def find(x):
        r = x
        while uf[r] != r:
            r = uf[r]
        while uf[x] != r:
            uf[x], x = r, uf[x]
        return r
    roots = np.array([find(i) for i in range(n)])
    active = sorted(set(roots.tolist()))
    if len(active) != L:
        refuse("average-link replay left %d clusters, expected %d" % (len(active), L))
    name = {a: "A%07d" % a for a in active}
    for j in range(n - L, n - 1):
        name[n + j] = "a%07d" % j
    parent = {}
    for j in range(n - L, n - 1):
        parent[name[int(Z[j, 0])]] = name[n + j]
        parent[name[int(Z[j, 1])]] = name[n + j]
    leaves = [name[a] for a in active]
    pos = {a: i for i, a in enumerate(active)}
    lab = np.array([pos[r] for r in roots], dtype=np.int64)
    order = [name[n + j] for j in range(n - 2, n - L - 1, -1)]
    return {"leaves": leaves, "parent": parent, "kids": _kids_of(parent), "order": order, "root": name[2 * n - 2]}, lab


def _inertia(Xs):
    m = Xs.mean(0)
    nm = np.linalg.norm(m)
    if nm == 0:
        return float(len(Xs))
    return float((1.0 - Xs @ (m / nm)).sum())


def bisect_hierarchy(X, L, seed):
    """G2: bisecting spherical k-means on the TRAIN rows X (largest spherical inertia first); -> H, TRAIN leaf labels."""
    idx = {"b000000": np.arange(len(X))}
    inert = {"b000000": _inertia(X)}
    parent, order, failed = {}, [], set()
    live = ["b000000"]
    nid = [1]
    while len(live) < L:
        cand = [c for c in live if len(idx[c]) >= 2 and c not in failed]
        if not cand:
            break
        top = max(inert[c] for c in cand)
        c = min(x for x in cand if inert[x] == top)
        sub = idx[c]
        Cm = S0.skmeans(X[sub], 2, seed * 1000003 + len(order))
        lab = S0.assign(X[sub], Cm)
        if lab.min() == lab.max():
            failed.add(c)
            continue
        kids = []
        for s in (0, 1):
            k = "b%06d" % nid[0]
            nid[0] += 1
            idx[k] = sub[lab == s]
            inert[k] = _inertia(X[idx[k]])
            parent[k] = c
            kids.append(k)
        live.remove(c)
        live.extend(kids)
        order.append(c)
    leaves = sorted(live)
    pos = {c: i for i, c in enumerate(leaves)}
    labs = np.empty(len(X), dtype=np.int64)
    for c in leaves:
        labs[idx[c]] = pos[c]
    return {"leaves": leaves, "parent": parent, "kids": _kids_of(parent), "order": order, "root": "b000000"}, labs


def leaf_centroids(X, lab, L):
    return S0.unit(np.vstack([X[lab == j].mean(0) for j in range(L)]))


def random_shape_dps(parent, leaves, leaf_ids, cls, n_random, seed):
    """G5: the tree's shape kept, leaf ids permuted over the leaf positions; -> the DP of every draw."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_random):
        perm = rng.permutation(len(leaves))
        mp = {leaves[j]: leaves[perm[j]] for j in range(len(leaves))}
        out.append(S1.dendrogram_purity(parent, leaves, [mp[x] for x in leaf_ids], cls))
    return out


def mc_se_pct(vals, q, B, seed):
    vals = np.asarray(vals, dtype=np.float64)
    if len(vals) < 2:
        return float("nan")
    rng = np.random.default_rng(seed)
    return float(np.std([np.percentile(vals[rng.integers(len(vals), size=len(vals))], q) for _ in range(B)], ddof=1))


# ================================================================================================ HIER-F metrics (H1-H5)
def node_matrix(parent, leaves):
    """-> (node ids, boolean matrix nodes x leaves: node is the leaf or one of its ancestors)."""
    nodes = sorted(set(leaves) | set(parent) | set(parent.values()))
    ix = {n: i for i, n in enumerate(nodes)}
    Am = np.zeros((len(nodes), len(leaves)), dtype=bool)
    for j, lf in enumerate(leaves):
        x = lf
        Am[ix[x], j] = True
        while x in parent:
            x = parent[x]
            Am[ix[x], j] = True
    return nodes, Am


def root_of(parent, leaves):
    x = leaves[0]
    while x in parent:
        x = parent[x]
    return x


def hier_f(Am, leaf_idx, gold, K, w=None):
    """H1: sum over gold classes c of (n_c / n) x max over EVERY node v of F(c, v); F = 2PR / (P + R), P = n_cv / n_v, R = n_cv / n_c.
    -> (HF, the best node index per class (-1 for an absent class))."""
    w = np.ones(len(leaf_idx)) if w is None else np.asarray(w, dtype=np.float64)
    L = Am.shape[1]
    M = np.bincount(np.asarray(leaf_idx) * K + np.asarray(gold), weights=w, minlength=L * K).reshape(L, K)
    N = Am.astype(np.float64) @ M
    nv = N.sum(1)
    nc = M.sum(0)
    n = nc.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        F = np.where(N > 0, 2.0 * N / (nv[:, None] + nc[None, :]), 0.0)
    best = F.max(0)
    arg = np.where(nc > 0, F.argmax(0), -1)
    return (float((nc / n * best).sum()) if n > 0 else float("nan")), arg


def random_shape_hf(Am, leaf_idx, gold, K, n_random, seed):
    """H1 / HF2: the same matched-shape draws as GR2 (default_rng(seed), one permutation of the L leaves per draw)."""
    rng = np.random.default_rng(seed)
    L = Am.shape[1]
    out = []
    for _ in range(n_random):
        perm = rng.permutation(L)
        out.append(hier_f(Am, perm[np.asarray(leaf_idx)], gold, K)[0])
    return out


def tax_prf(Am, nodes, leaf_idx, gc, gf, leaf_idx_tr, gc_tr, gf_tr, Kc, Kf, root):
    """H2 taxonomic P / R / F (micro, Kiritchenko-style on cotopy label sets): every non-root node carries the TRAIN plurality coarse
    and fine label of its TRAIN items (ties to the smaller code; a node without TRAIN items carries none); an EVAL item's predicted
    set = the labels on its leaf's ancestor path (root excluded), its gold set = {coarse, fine}."""
    L = Am.shape[1]
    Af = Am.astype(np.float64)
    Mc = np.bincount(np.asarray(leaf_idx_tr) * Kc + np.asarray(gc_tr), minlength=L * Kc).reshape(L, Kc)
    Mf = np.bincount(np.asarray(leaf_idx_tr) * Kf + np.asarray(gf_tr), minlength=L * Kf).reshape(L, Kf)
    Nc, Nf = Af @ Mc, Af @ Mf
    has = Nc.sum(1) > 0
    lab_c, lab_f = Nc.argmax(1), Nf.argmax(1)
    ri = nodes.index(root)
    pred = []
    for j in range(L):
        s = set()
        for v in np.nonzero(Am[:, j])[0]:
            if v != ri and has[v]:
                s.add(("C", int(lab_c[v])))
                s.add(("F", int(lab_f[v])))
        pred.append(s)
    hit = sum(int(("C", int(c)) in pred[j]) + int(("F", int(f)) in pred[j]) for j, c, f in zip(leaf_idx, gc, gf))
    npred = sum(len(pred[j]) for j in leaf_idx)
    P = hit / npred if npred else float("nan")
    R = hit / (2.0 * len(leaf_idx)) if len(leaf_idx) else float("nan")
    F = 2 * P * R / (P + R) if (np.isfinite(P) and P + R > 0) else 0.0
    return P, R, F


def ancestor_f1(Am, best_c, best_f, f2c, coarse_present, fine_present):
    """H3: each gold class sits at its best-F node (H1); predicted (C, f) iff C's node is an ancestor-or-self of f's node (its leaf set
    contains f's); gold (C, f) iff f nests in C. F1 over every (coarse, fine) pair present on EVAL."""
    pred, gold = set(), set()
    for C_ in coarse_present:
        for f_ in fine_present:
            if f2c[f_] == C_:
                gold.add((C_, f_))
            a, b = Am[best_c[C_]], Am[best_f[f_]]
            if bool(np.all(a >= b)):
                pred.add((C_, f_))
    tp = len(pred & gold)
    if not pred or not gold or tp == 0:
        return 0.0
    P, R = tp / len(pred), tp / len(gold)
    return 2 * P * R / (P + R)


def fm_index(t, p):
    """H4 Fowlkes-Mallows: TP / sqrt((TP + FP)(TP + FN)) on item pairs."""
    t, p = np.asarray(t, dtype=np.int64), np.asarray(p, dtype=np.int64)
    kp = int(p.max()) + 1
    cont = np.bincount(t * kp + p, minlength=(int(t.max()) + 1) * kp).astype(np.float64)
    a = np.bincount(t).astype(np.float64)
    b = np.bincount(p).astype(np.float64)
    tp = (cont * (cont - 1) / 2).sum()
    pa, pb = (a * (a - 1) / 2).sum(), (b * (b - 1) / 2).sum()
    return float(tp / np.sqrt(pa * pb)) if pa > 0 and pb > 0 else 0.0


# ================================================================================================ verdicts (G4, G5, G7)
def spread_b(best_by_seed):
    """G4: max - min of the bisecting best-cut AMI over the five registered seeds (refuses another seed set)."""
    if sorted(best_by_seed) != list(SEEDS_B):
        refuse("spread_B needs seeds %s, got %s" % (list(SEEDS_B), sorted(best_by_seed)))
    v = [best_by_seed[s] for s in SEEDS_B]
    return float(max(v) - min(v))


def gr1_corpus(D1, lo, hi, spread_B):
    if D1 > spread_B and lo > 0:
        return "TREE-BETTER"
    if D1 < -spread_B and hi < 0:
        return "AVG-BETTER"
    return "NEITHER"


def gr1_overall(wm, wc):
    if wm == "TREE-BETTER" and wc == "TREE-BETTER":
        return "TREE-BETTER"
    if wm == "AVG-BETTER" and wc == "AVG-BETTER":
        return "AVG-BETTER"
    return "MIXED"


def gr2_corpus(dp, p975):
    return bool(dp > p975)


def above_random(x, rnd):
    """HF2 per corpus: (p97.5 of the random draws, x > p97.5 strictly)."""
    p = float(np.percentile(rnd, Q_RANDOM)) if len(rnd) else float("nan")
    return p, gr2_corpus(x, p)


def gr2_overall(am, ac):
    if am and ac:
        return "HELD"
    if not am and not ac:
        return "FAILED"
    return "MIXED"


def band(x, lo, hi):
    return "HELD" if (x is not None and np.isfinite(x) and lo <= x <= hi) else "FAILED"


def brier(p, event):
    return (p - (1.0 if event else 0.0)) ** 2


# ================================================================================================ loading
def presence(snap_db, data_root):
    pres = S1.arm_presence(snap_db, data_root)
    return {n: pres[n] for n in ARMS_USED.values()}


def load_all(data_root, pins_file, snap_db, out=print):
    """Pins (strict), corpora, census, the two trees (checked against the re-derived build), vectors at the tree slice."""
    db = os.path.join(data_root, II.DB_NAME)
    emb = os.path.join(data_root, "intent_emb_qwen3.db")
    pres = presence(snap_db, data_root)
    for n, p in pres.items():
        out("%s arm %-5s %s %s%s" % (TAG, n, "PRESENT" if p["present"] else "ABSENT", p["sid"] or "-", (" (%s)" % p["why"]) if p["why"] else ""))
    absent = [n for n, p in pres.items() if not p["present"]]
    if absent:
        refuse("builds ABSENT: %s (the readout reads only complete builds)" % ", ".join(absent))
    pins = {"ingest": S0.pin_check(db, "ingest_db", True, pins_file=pins_file, label="ingest"),
            "emb_qwen3": S0.pin_check(emb, "emb", True, sub="qwen3", pins_file=pins_file, label="intent_emb_qwen3.db")}
    CS = S0.load_corpora(db)
    cen, bad = census(CS)
    out("%s census (EVAL kept in-scope, salt 1): %s" % (TAG, "; ".join("%s %d / %d" % (k, v[0], v[1]) for k, v in cen.items())))
    if bad:
        refuse("census off by more than 5%%: %s (re-state by bracket before any read)" % "; ".join(bad))
    con = II.open_db_ro(db)
    try:
        items = II.rows_from_db(con)
    finally:
        con.close()
    D_ex = S1.EX.derive(items)
    trees, gsha = {}, {}
    for c, n in ARMS_USED.items():
        T, g = S1.load_tree_checked(n, pres[n], snap_db, D_ex, {"qwen3": pins["emb_qwen3"]})
        trees[n] = (T, pres[n]["sid"])
        gsha[n] = hashlib.sha256(json.dumps(g, sort_keys=True).encode("utf-8")).hexdigest()
        out("%s %s: snapshot %s, %d nodes, %d leaves, slice %d, multi-parent %d, graph sha256 %s" % (
            TAG, n, pres[n]["sid"], len(T["nodes"]), len(T["leaves"]), T["d"], T["multi_parent"], gsha[n]))
    dim = max(T["d"] for T, _ in trees.values())
    texts = set()
    for c in CORPORA:
        C = CS[c]
        texts.update(C.text[i] for i in np.nonzero(C.kept & ~C.oos)[0])
    vecs = S1.load_raw(emb, texts, dim)
    W = {"CS": CS, "vecs": {"qwen3": vecs}}
    return {"W": W, "trees": trees, "pins": pins, "census": cen, "gsha": gsha, "db": db, "emb": emb, "pres": pres}


def census(CS):
    out, bad = {}, []
    for c in CORPORA:
        C = CS[c]
        m = C.kept & (~C.oos) & (C.side == SS.EVAL)
        n, g = int(m.sum()), int(len(np.unique(C.comp[m])))
        out[c] = (n, g)
        rn, rg = REGISTERED_N[c]
        if abs(n - rn) > CENSUS_TOL * rn or abs(g - rg) > CENSUS_TOL * rg:
            bad.append("%s %d / %d vs registered %d / %d" % (c, n, g, rn, rg))
    return out, bad


# ================================================================================================ compute
def train_phase(A, seeds=SEEDS_B):
    """Every fit on TRAIN (S1.fit_idx), before any EVAL row is read."""
    C, X, T = A["C"], A["X"], A["T"]
    tr = S1.fit_idx(C, A["side"], S1.side_rows(C, A["side"], A["have"], SS.TRAIN), (SS.TRAIN,), "%s TRAIN" % A["name"])
    L = A["L"]
    Xtr = X[tr]
    cuts, depth = tree_depth_cuts(T)
    Ha, lab_a = avglink_hierarchy(Xtr, L)
    hiers = {"avg": (Ha, leaf_centroids(Xtr, lab_a, len(Ha["leaves"])))}
    tr_lab = {"tree": S1.flat_leaf(T, Xtr), "avg": lab_a}
    for s in seeds:
        Hb, lab_b = bisect_hierarchy(Xtr, L, s)
        hiers["bis%d" % s] = (Hb, leaf_centroids(Xtr, lab_b, len(Hb["leaves"])))
        tr_lab["bis%d" % s] = lab_b
    return {"tr": tr, "n_train": int(len(tr)), "cuts": cuts, "depth": depth, "hiers": hiers, "tr_lab": tr_lab}


def eval_phase(A, P, boot_b, n_random, seed_boot, seed_random, seeds=SEEDS_B):
    from sklearn.metrics import homogeneity_completeness_v_measure as hcv
    C, X, T = A["C"], A["X"], A["T"]
    ev = S1.eval_rows(A)
    Xev = X[ev]
    tc, tf = S0.codes(C.coarse[ev]), S0.codes(C.fine[ev])
    comp = C.comp[ev]
    fl = S1.flat_leaf(T, Xev)
    ks = [k for _d, k, _c in P["cuts"]]
    tree_labs = [code[fl] for _d, _k, code in P["cuts"]]
    filed, labs = {}, {}
    for name, (H, cent) in P["hiers"].items():
        lf = np.argmax(Xev @ cent.T, axis=1)
        filed[name] = lf
        labs[name] = [frontier_cut(H, k)[lf] for k in ks]
    r = {"n": int(len(ev)), "G": int(len(np.unique(comp))), "kish": S0.kish(comp), "L": A["L"], "ks": ks,
         "depths": [d for d, _k, _c in P["cuts"]], "dmax": max(P["depth"]), "n_train": P["n_train"],
         "leaf_depths": {int(d): int(sum(1 for x in P["depth"] if x == d)) for d in sorted(set(P["depth"]))}}
    r["neff"] = r["n"] / r["kish"]
    r["tree_c"], r["tree_best_j"], r["tree_ami_c"] = best_cut(tc, tree_labs)
    r["tree_f"], r["tree_best_jf"], r["tree_ami_f"] = best_cut(tf, tree_labs)
    r["best_depth_c"] = r["depths"][r["tree_best_j"]]
    r["best_depth_f"] = r["depths"][r["tree_best_jf"]]
    r["avg_c"], r["avg_best_j"], r["avg_ami_c"] = best_cut(tc, labs["avg"])
    r["avg_f"], _j, r["avg_ami_f"] = best_cut(tf, labs["avg"])
    r["bis_c"] = {}
    r["bis_ami_c"] = {}
    r["bis_f"] = {}
    for s in seeds:
        b, _j, v = best_cut(tc, labs["bis%d" % s])
        r["bis_c"][s], r["bis_ami_c"][s] = b, v
        r["bis_f"][s] = best_cut(tf, labs["bis%d" % s])[0]
    r["spread_B"] = spread_b(r["bis_c"])
    r["D1"] = r["tree_c"] - r["avg_c"]

    def d1(w):
        return best_cut(tc, tree_labs, w)[0] - best_cut(tc, labs["avg"], w)[0]
    draws = [d1(w) for w in S0.comp_weights(comp, boot_b, np.random.default_rng(seed_boot))]
    r["lo"], r["hi"] = S0.pct_ci(draws)
    r["se"] = float(np.std(draws, ddof=1)) if len(draws) > 1 else float("nan")
    r["mde"] = 2.8 * r["se"]
    r["gr1"] = gr1_corpus(r["D1"], r["lo"], r["hi"], r["spread_B"])
    # descriptive: average-link over every k in 2..L
    Ha = P["hiers"]["avg"][0]
    allk = [ami(tc, frontier_cut(Ha, k)[filed["avg"]]) for k in range(2, len(Ha["leaves"]) + 1)]
    r["avg_any_c"], r["avg_any_k"] = (float(max(allk)), int(np.argmax(allk)) + 2) if allk else (float("nan"), 0)
    # GR2: DP vs matched-shape random trees (coarse level)
    leaf_ids = [T["leaves"][j] for j in fl]
    cls = C.coarse[ev].tolist()
    tp = S1.tree_parent_restricted(T)
    r["dp_tree"] = S1.dendrogram_purity(tp, T["leaves"], leaf_ids, cls)
    rnd = random_shape_dps(tp, T["leaves"], leaf_ids, cls, n_random, seed_random)
    r["rnd_p975"] = float(np.percentile(rnd, Q_RANDOM)) if rnd else float("nan")
    r["rnd_med"] = float(np.median(rnd)) if rnd else float("nan")
    r["rnd_ge"] = int(sum(1 for x in rnd if x >= r["dp_tree"]))
    r["n_random"] = len(rnd)
    r["rnd_mc_se"] = mc_se_pct(rnd, Q_RANDOM, MC_B, SEED_MC)
    r["gr2_above"] = gr2_corpus(r["dp_tree"], r["rnd_p975"])
    r["dp_h"] = {}
    for name, (H, _c) in P["hiers"].items():
        r["dp_h"][name] = S1.dendrogram_purity(H["parent"], H["leaves"], [H["leaves"][j] for j in filed[name]], cls)
    # homogeneity / completeness / V at the leaf level
    r["hcv"] = {"tree": {"coarse": hcv(tc, fl), "fine": hcv(tf, fl)}}
    for name in P["hiers"]:
        r["hcv"][name] = {"coarse": hcv(tc, filed[name]), "fine": hcv(tf, filed[name])}
    r["bis_leaves"] = {s: len(P["hiers"]["bis%d" % s][0]["leaves"]) for s in seeds}
    r["hf"] = hierf_phase(A, P, ev, fl, filed, comp, boot_b, n_random, seed_boot + HF_BOOT_OFF, seed_random, seeds)
    return r


def hierf_phase(A, P, ev, fl, filed, comp, boot_b, n_random, seed_boot, seed_random, seeds=SEEDS_B):
    """HIER-F (prog L24430-L24441): node-level hierarchical F, taxonomic P/R/F, ancestor-F1, Fowlkes-Mallows; same arms, same EVAL."""
    C, T = A["C"], A["T"]
    tr = P["tr"]
    allc = np.concatenate([C.coarse[ev], C.coarse[tr]]).astype(str)
    allf = np.concatenate([C.fine[ev], C.fine[tr]]).astype(str)
    uc, cc = np.unique(allc, return_inverse=True)
    uf, ff = np.unique(allf, return_inverse=True)
    ne = len(ev)
    gc, gf, gc_tr, gf_tr = cc[:ne], ff[:ne], cc[ne:], ff[ne:]
    Kc, Kf = len(uc), len(uf)
    f2c = {}
    for f_, c_ in zip(gf, gc):
        f2c.setdefault(int(f_), set()).add(int(c_))
    f2c = {k: min(v) for k, v in f2c.items()}
    arms = {"tree": (S1.tree_parent_restricted(T), T["leaves"], fl, P["tr_lab"]["tree"])}
    for name, (H, _c) in P["hiers"].items():
        arms[name] = (H["parent"], H["leaves"], filed[name], P["tr_lab"][name])
    h = {"arms": {}}
    mats = {}
    for name, (par, leaves, lidx, lidx_tr) in arms.items():
        nodes, Am = node_matrix(par, leaves)
        mats[name] = (Am, lidx)
        hf_f, best_f = hier_f(Am, lidx, gf, Kf)
        hf_c, best_c = hier_f(Am, lidx, gc, Kc)
        tp_, tr_, tf_ = tax_prf(Am, nodes, lidx, gc, gf, lidx_tr, gc_tr, gf_tr, Kc, Kf, root_of(par, leaves))
        af = ancestor_f1(Am, best_c, best_f, f2c, sorted(set(gc.tolist())), sorted(set(gf.tolist())))
        h["arms"][name] = {"hf_f": hf_f, "hf_c": hf_c, "tax": (tp_, tr_, tf_), "anc_f1": af}
    a = h["arms"]
    h["hf_tree"], h["hf_avg"] = a["tree"]["hf_f"], a["avg"]["hf_f"]
    h["bis_hf"] = {s: a["bis%d" % s]["hf_f"] for s in seeds}
    h["spread_B"] = spread_b(h["bis_hf"])
    h["D"] = h["hf_tree"] - h["hf_avg"]
    (At, lt), (Aa, la) = mats["tree"], mats["avg"]

    def dfun(w):
        return hier_f(At, lt, gf, Kf, w)[0] - hier_f(Aa, la, gf, Kf, w)[0]
    draws = [dfun(w) for w in S0.comp_weights(comp, boot_b, np.random.default_rng(seed_boot))]
    h["lo"], h["hi"] = S0.pct_ci(draws)
    h["se"] = float(np.std(draws, ddof=1)) if len(draws) > 1 else float("nan")
    h["mde"] = 2.8 * h["se"]
    h["hf1"] = gr1_corpus(h["D"], h["lo"], h["hi"], h["spread_B"])
    rnd = random_shape_hf(At, lt, gf, Kf, n_random, seed_random)
    h["rnd_p975"], h["hf2_above"] = above_random(h["hf_tree"], rnd)
    h["rnd_med"] = float(np.median(rnd)) if rnd else float("nan")
    h["rnd_ge"] = int(sum(1 for x in rnd if x >= h["hf_tree"]))
    h["n_random"] = len(rnd)
    h["rnd_mc_se"] = mc_se_pct(rnd, Q_RANDOM, MC_B, SEED_MC)
    # Fowlkes-Mallows, level-wise: the tree's depth cuts and the other arms at the matched k_d, against both gold levels;
    # the average-link and bisecting (seed 0) curves B_k over every k in 2..L against the fine gold
    ks = [k for _d, k, _c in P["cuts"]]
    h["fm_tree"] = {lv: [fm_index(g, code[fl]) for _d, _k, code in P["cuts"]] for lv, g in (("coarse", gc), ("fine", gf))}
    h["fm_k"] = {}
    for name, (H, _c) in P["hiers"].items():
        h["fm_k"][name] = {lv: [fm_index(g, frontier_cut(H, k)[filed[name]]) for k in ks] for lv, g in (("coarse", gc), ("fine", gf))}
    h["bk"] = {}
    for name in ("avg", "bis%d" % seeds[0]):
        H = P["hiers"][name][0]
        h["bk"][name] = [fm_index(gf, frontier_cut(H, k)[filed[name]]) for k in range(2, len(H["leaves"]) + 1)]
    return h


def compute(L, boot_b=BOOT_B, n_random=N_RANDOM, out=print):
    W, trees = L["W"], L["trees"]
    arms = {}
    S1.STATE["gate_frozen"] = False
    P = {}
    for c, n in ARMS_USED.items():
        A = S1.make_arm(W, n, *trees[n])
        arms[c] = A
        P[c] = train_phase(A)
        out("%s TRAIN phase %s: %d TRAIN rows; L %d; depths 1..%d; k_d %s" % (TAG, n, P[c]["n_train"], A["L"], max(P[c]["depth"]),
                                                                          [k for _d, k, _c in P[c]["cuts"]]))
    S1.STATE["gate_frozen"] = True
    R = {"corpora": {}}
    for c in CORPORA:
        R["corpora"][c] = eval_phase(arms[c], P[c], boot_b, n_random, SEED_BOOT + BOOT_OFF[c], SEED_RANDOM)
    m, k = R["corpora"]["massive"], R["corpora"]["clinc"]
    R["GR1"] = gr1_overall(m["gr1"], k["gr1"])
    R["GR2"] = gr2_overall(m["gr2_above"], k["gr2_above"])
    R["HF2"] = gr2_overall(m["hf"]["hf2_above"], k["hf"]["hf2_above"])
    R["boot_b"], R["n_random"] = boot_b, n_random
    return R


# ================================================================================================ render
def f(x, fmt="%+.5f"):
    return "n/a" if x is None or not np.isfinite(x) else fmt % x


def render(R, meta):
    L = []
    a = L.append
    a("%s GRANULARITY-GT outcome (zero calls). %s" % (TAG, REGISTRATION))
    for k, v in meta.items():
        a("%s %s: %s" % (TAG, k, v))
    a("%s READERS' DEFINITIONS G1-G7 (module docstring of the pinned script): matched-size cuts at the tree's k_d; leaf-level filing "
      "then lift; AMI arithmetic, exact EMI; percentile component-bootstrap interval, B %d; DP coarse, %d matched-shape random trees, "
      "p97.5 strict" % (TAG, R["boot_b"], R["n_random"]))
    for c in CORPORA:
        r = R["corpora"][c]
        a("")
        a("%s === %s (%s) ===" % (TAG, c.upper(), ARMS_USED[c]))
        a("%s %s n EVAL %d, components %d, Kish %.4f, n_eff %.0f; TRAIN rows %d; L %d; leaf depths %s" % (
            TAG, c, r["n"], r["G"], r["kish"], r["neff"], r["n_train"], r["L"], json.dumps(r["leaf_depths"], sort_keys=True)))
        a("%s %s level-wise AMI (depth d, k_d | tree coarse / fine | avg-link coarse / fine | bisecting coarse mean over seeds 0-4):" % (TAG, c))
        for j, (d, kk) in enumerate(zip(r["depths"], r["ks"])):
            a("%s   d %d k %3d | %.5f / %.5f | %.5f / %.5f | %.5f" % (TAG, d, kk, r["tree_ami_c"][j], r["tree_ami_f"][j], r["avg_ami_c"][j],
                                                                   r["avg_ami_f"][j], float(np.mean([r["bis_ami_c"][s][j] for s in r["bis_ami_c"]]))))
        a("%s %s best-cut AMI coarse: tree %.5f at depth %d (k %d; D_max %d); average-link %.5f at k %d; bisecting by seed %s; spread_B %.5f" % (
            TAG, c, r["tree_c"], r["best_depth_c"], r["ks"][r["tree_best_j"]], r["dmax"], r["avg_c"], r["ks"][r["avg_best_j"]],
            ", ".join("%d: %.5f" % (s, v) for s, v in sorted(r["bis_c"].items())), r["spread_B"]))
        a("%s %s best-cut AMI fine (DESCRIPTIVE): tree %.5f at depth %d; average-link %.5f; bisecting mean %.5f" % (
            TAG, c, r["tree_f"], r["best_depth_f"], r["avg_f"], float(np.mean(list(r["bis_f"].values())))))
        a("%s %s average-link best over every k in 2..L (DESCRIPTIVE, never deciding): %.5f at k %d" % (TAG, c, r["avg_any_c"], r["avg_any_k"]))
        a("%s %s GR1 D1 = %s, 95%% [%s, %s] (percentile, components), spread_B %.5f -> %s" % (
            TAG, c, f(r["D1"]), f(r["lo"]), f(r["hi"]), r["spread_B"], r["gr1"]))
        a("%s %s SUPPORT: realised n %d / %d components, DEFF(Kish) %.4f, n_eff %.0f, SE(D1) %s, MDE80 %s | registered: %s | VERDICT LINE GR1: %s" % (
            TAG, c, r["n"], r["G"], r["kish"], r["neff"], f(r["se"], "%.5f"), f(r["mde"], "%.5f"), REG_SUPPORT, VERDICT_LINES["GR1"]))
        a("%s %s GR2 DP(tree, coarse) %.5f vs %d matched-shape random trees: p97.5 %.5f (MC SE %s), median %.5f, %d of %d >= DP(tree) -> %s" % (
            TAG, c, r["dp_tree"], r["n_random"], r["rnd_p975"], f(r["rnd_mc_se"], "%.5f"), r["rnd_med"], r["rnd_ge"], r["n_random"],
            "ABOVE-RANDOM" if r["gr2_above"] else "NOT ABOVE-RANDOM"))
        a("%s %s DP DESCRIPTIVE: average-link %.5f; bisecting %s" % (
            TAG, c, r["dp_h"]["avg"], ", ".join("%s %.5f" % (k[3:], v) for k, v in sorted(r["dp_h"].items()) if k.startswith("bis"))))
        for arm in ["tree", "avg"] + sorted(k for k in r["hcv"] if k.startswith("bis")):
            h = r["hcv"][arm]
            a("%s %s leaf level h / c / V (DESCRIPTIVE) %-5s coarse %.4f / %.4f / %.4f; fine %.4f / %.4f / %.4f" % (
                TAG, c, arm, h["coarse"][0], h["coarse"][1], h["coarse"][2], h["fine"][0], h["fine"][1], h["fine"][2]))
        if any(v != r["L"] for v in r["bis_leaves"].values()):
            a("%s %s NOTE: a bisecting seed stopped short of L leaves: %s" % (TAG, c, r["bis_leaves"]))
    m, k = R["corpora"]["massive"], R["corpora"]["clinc"]
    a("")
    a("%s === CRITERIA ===" % TAG)
    a("%s GR1 (DECIDING): MASSIVE %s, CLINC %s -> GR1 %s" % (TAG, m["gr1"], k["gr1"], R["GR1"]))
    if R["GR1"] == "TREE-BETTER":
        a("%s GR1 TREE-BETTER: the tree's best cut agrees with the coarse gold better than average-link's on both corpora; 'right at a "
          "different granularity' may be written (best-cut AMI, matched-size cuts, one draw)" % TAG)
    elif R["GR1"] == "AVG-BETTER":
        a("%s GR1 AVG-BETTER: average-link's best cut agrees with the coarse gold better than the tree's on both corpora; 'right at a "
          "different granularity' is NOT written" % TAG)
    else:
        a("%s GR1 MIXED: no common word on the two corpora; 'right at a different granularity' is NOT written as a general claim" % TAG)
    a("%s GR2 (DECIDING): MASSIVE %s, CLINC %s -> GR2 %s" % (TAG, "ABOVE-RANDOM" if m["gr2_above"] else "NOT ABOVE-RANDOM",
                                                         "ABOVE-RANDOM" if k["gr2_above"] else "NOT ABOVE-RANDOM", R["GR2"]))
    refuted = [c for c in CORPORA if not R["corpora"][c]["gr2_above"]]
    if refuted:
        a("%s FAILS (rule 8): GR2 HELD is REFUTED: DP(tree) <= the random p97.5 on %s" % (TAG, ", ".join(refuted)))
    else:
        a("%s FAILS (rule 8): GR2 HELD is not refuted (DP(tree) > the random p97.5 on both corpora)" % TAG)
    if R["GR2"] == "FAILED":
        a("%s F-GR FIRES: the hierarchy is no better than a random arrangement of the same leaves on either corpus; P3 / D6's "
          "hierarchy wording is falsified" % TAG)
    else:
        a("%s F-GR does not fire (GR2 %s)" % (TAG, R["GR2"]))
    a("%s VERDICT LINES (registered): GR1 %s; GR2 %s" % (TAG, VERDICT_LINES["GR1"], VERDICT_LINES["GR2"]))
    a("")
    a("%s === PREDICTIONS ===" % TAG)
    pt, lo, hi = P1_BAND
    for c in CORPORA:
        a("%s P1 D1 %s %s vs %+.2f [%+.2f, %+.2f]: %s" % (TAG, c.upper(), f(R["corpora"][c]["D1"]), pt, lo, hi, band(R["corpora"][c]["D1"], lo, hi)))
    a("%s P1 'GR1 NEITHER 0.6': NOT SCORED (registration defect GG-1: NEITHER is not an outcome of GR1's overall rule TREE-BETTER / "
      "AVG-BETTER / MIXED; per-corpus words MASSIVE %s, CLINC %s; overall %s; the registrar's bracket decides the event)" % (TAG, m["gr1"], k["gr1"], R["GR1"]))
    ev2 = R["GR2"] == "HELD"
    a("%s P2 GR2 HELD 0.75: event %s, Brier %.4f" % (TAG, "TRUE" if ev2 else "FALSE", brier(P2_HELD, ev2)))
    ev3 = bool(m["best_depth_c"] < m["dmax"] and k["best_depth_c"] < k["dmax"])
    a("%s P3 coarse best depth shallower than the leaves on both corpora 0.9 (DESCRIPTIVE): MASSIVE %d of %d, CLINC %d of %d: event %s, Brier %.4f" % (
        TAG, m["best_depth_c"], m["dmax"], k["best_depth_c"], k["dmax"], "TRUE" if ev3 else "FALSE", brier(P3_SHALLOW, ev3)))
    a("%s WHAT THIS RESULT WILL NOT SHOW: routing value; MMLU-Pro; that the tree's leaves are better (T-C1 governs leaves); "
      "profile-Mantel (row 6, not registered); T-C2 (SEEN) is not re-scored" % TAG)
    L.extend(render_hf(R))
    return L


def render_hf(R):
    L = []
    a = L.append
    a("")
    a("%s === HIER-F (pre-data addendum; %s) ===" % (TAG, HF_REGISTRATION))
    a("%s HIER-F READERS' DEFINITIONS H1-H6 (module docstring): HF over every node incl. leaves and root; HF1 / HF2 on the FINE gold; "
      "the same matched-shape permutations as GR2; taxonomic P/R/F micro on TRAIN-plurality node labels; ancestor-F1 on best-F nodes; "
      "FM level-wise at the tree's k_d" % TAG)
    for c in CORPORA:
        h = R["corpora"][c]["hf"]
        A_ = h["arms"]
        a("%s %s HF fine / coarse: tree %.5f / %.5f; average-link %.5f / %.5f; bisecting fine by seed %s" % (
            TAG, c, A_["tree"]["hf_f"], A_["tree"]["hf_c"], A_["avg"]["hf_f"], A_["avg"]["hf_c"],
            ", ".join("%d: %.5f" % (s, v) for s, v in sorted(h["bis_hf"].items()))))
        a("%s %s HF1 D = %s, 95%% [%s, %s] (percentile, components), spread_B(HF) %.5f, SE %s, MDE80 %s -> %s | VERDICT LINE HF1: %s" % (
            TAG, c, f(h["D"]), f(h["lo"]), f(h["hi"]), h["spread_B"], f(h["se"], "%.5f"), f(h["mde"], "%.5f"), h["hf1"], HF_VERDICT_LINES["HF1"]))
        a("%s %s HF2 HF(tree, fine) %.5f vs %d matched-shape random trees: p97.5 %.5f (MC SE %s), median %.5f, %d of %d >= HF(tree) -> %s" % (
            TAG, c, h["hf_tree"], h["n_random"], h["rnd_p975"], f(h["rnd_mc_se"], "%.5f"), h["rnd_med"], h["rnd_ge"], h["n_random"],
            "ABOVE-RANDOM" if h["hf2_above"] else "NOT ABOVE-RANDOM"))
        for arm in ["tree", "avg"] + sorted(k for k in A_ if k.startswith("bis")):
            x = A_[arm]
            a("%s %s DESCRIPTIVE %-5s taxonomic P / R / F %.4f / %.4f / %.4f; ancestor-F1 %.4f" % (TAG, c, arm, x["tax"][0], x["tax"][1], x["tax"][2], x["anc_f1"]))
        for lv in ("coarse", "fine"):
            a("%s %s DESCRIPTIVE FM vs %s at k_d %s: tree %s; average-link %s; bisecting mean %s" % (
                TAG, c, lv, R["corpora"][c]["ks"], " ".join("%.4f" % v for v in h["fm_tree"][lv]),
                " ".join("%.4f" % v for v in h["fm_k"]["avg"][lv]),
                " ".join("%.4f" % float(np.mean([h["fm_k"][k][lv][j] for k in h["fm_k"] if k.startswith("bis")])) for j in range(len(h["fm_tree"][lv])))))
        for name, curve in sorted(h["bk"].items()):
            a("%s %s DESCRIPTIVE B_k vs fine, %s, k = 2..%d: %s" % (TAG, c, name, len(curve) + 1, " ".join("%.3f" % v for v in curve)))
    m, k = R["corpora"]["massive"]["hf"], R["corpora"]["clinc"]["hf"]
    a("%s HF1 (DECIDING, per corpus): MASSIVE %s, CLINC %s" % (TAG, m["hf1"], k["hf1"]))
    a("%s HF2 (DECIDING): MASSIVE %s, CLINC %s -> HF2 %s" % (TAG, "ABOVE-RANDOM" if m["hf2_above"] else "NOT ABOVE-RANDOM",
                                                         "ABOVE-RANDOM" if k["hf2_above"] else "NOT ABOVE-RANDOM", R["HF2"]))
    refuted = [c for c in CORPORA if not R["corpora"][c]["hf"]["hf2_above"]]
    if refuted:
        a("%s FAILS (rule 8): HF2 HELD is REFUTED: HF(tree) <= the random p97.5 on %s" % (TAG, ", ".join(refuted)))
    else:
        a("%s FAILS (rule 8): HF2 HELD is not refuted (HF(tree) > the random p97.5 on both corpora)" % TAG)
    if R["HF2"] == "FAILED":
        a("%s F-HF FIRES: 'the tree carries the gold hierarchy beyond its leaves' is false under node-level credit" % TAG)
    else:
        a("%s F-HF does not fire (HF2 %s)" % (TAG, R["HF2"]))
    a("%s VERDICT LINES (registered): HF1 %s; HF2 %s" % (TAG, HF_VERDICT_LINES["HF1"], HF_VERDICT_LINES["HF2"]))
    pt, lo, hi = HF_P1_BAND
    for c in CORPORA:
        h = R["corpora"][c]["hf"]
        a("%s HF P1 D %s %s vs %+.2f [%+.2f, %+.2f]: %s; HF1 NEITHER 0.60 (per corpus): event %s, Brier %.4f" % (
            TAG, c.upper(), f(h["D"]), pt, lo, hi, band(h["D"], lo, hi), "TRUE" if h["hf1"] == "NEITHER" else "FALSE",
            brier(HF_P1_NEITHER, h["hf1"] == "NEITHER")))
    ev2 = R["HF2"] == "HELD"
    a("%s HF P2 HF2 HELD 0.75: event %s, Brier %.4f" % (TAG, "TRUE" if ev2 else "FALSE", brier(HF_P2_HELD, ev2)))
    a("%s HF P3 (MMLU-Pro recovery, DESCRIPTIVE): NOT EVALUATED (the MMLU-Pro re-draw arm is a pool reader under rule 7 and is not built "
      "in this readout)" % TAG)
    a("%s HIER-F WILL NOT SHOW: routing value; that the leaves are better (T-C1 governs); MMLU-Pro as decisive" % TAG)
    return L


# ================================================================================================ dry-run / run
def default_out_dir():
    return "E:/TaxoArena_backup_%s_granularity_gt" % datetime.date.today().isoformat()


def dry_run(data_root=None, pins_file=None, snap_db=None, out=print, skip_heavy=False):
    data_root = os.path.abspath(data_root or S1.DATA_ROOT)
    out("%s DRY RUN: zero calls; nothing written; no EVAL statistic. %s" % (TAG, REGISTRATION))
    out("%s data root %s" % (TAG, data_root))
    check_code_pins()
    if not skip_heavy:
        S1.check_heavy()
    snap_db = snap_db or os.path.join(data_root, "snapshots.db")
    Ld = load_all(data_root, pins_file, snap_db, out=out)
    for c, n in ARMS_USED.items():
        T = Ld["trees"][n][0]
        cuts, depth = tree_depth_cuts(T)
        A = S1.make_arm(Ld["W"], n, *Ld["trees"][n])
        tr = S1.side_rows(A["C"], A["side"], A["have"], SS.TRAIN)
        out("%s %s: TRAIN rows %d (pdist %.0f MB for average-link), depths 1..%d, k_d %s" % (
            TAG, n, len(tr), len(tr) * (len(tr) - 1) / 2 * 8 / 1e6, max(depth), [k for _d, k, _c in cuts]))
    out("%s DRY RUN complete: no EVAL row read; 0 files written" % TAG)
    return 0


def run(data_root=None, pins_file=None, snap_db=None, out_dir=None, boot_b=BOOT_B, n_random=N_RANDOM, skip_heavy=False, out=print):
    data_root = os.path.abspath(data_root or S1.DATA_ROOT)
    out_dir = out_dir or default_out_dir()
    path, spath = os.path.join(out_dir, OUTCOME), os.path.join(out_dir, SUMS)
    for p in (path, spath):
        if os.path.lexists(p):
            refuse("%s exists: the outcome is write-once" % p)
    check_code_pins()
    if not skip_heavy:
        S1.check_heavy()
    snap_db = snap_db or os.path.join(data_root, "snapshots.db")
    del S1.FIT_LOG[:]
    Ld = load_all(data_root, pins_file, snap_db, out=out)
    R = compute(Ld, boot_b=boot_b, n_random=n_random, out=out)
    S0.pin_check(Ld["db"], "ingest_db", True, pins_file=pins_file, label="ingest (after)")
    S0.pin_check(Ld["emb"], "emb", True, sub="qwen3", pins_file=pins_file, label="intent_emb_qwen3.db (after)")
    me = os.path.abspath(__file__)
    meta = {"script": "tools/analysis/granularity_gt.py blob:%s (LF); working-tree bytes sha256 %s" % (_blob(me), _sha256(me)),
            "instrument": ", ".join("%s blob:%s (LF)" % kv for kv in PINNED_CODE.items()),
            "data root": data_root, "snapshots": json.dumps({n: Ld["pres"][n]["sid"] for n in ARMS_USED.values()}, sort_keys=True),
            "graph sha256 (json sort_keys)": json.dumps(Ld["gsha"], sort_keys=True),
            "pins (sha256-bytes)": json.dumps(Ld["pins"], sort_keys=True), "census": json.dumps(Ld["census"], sort_keys=True),
            "TRAIN-ONLY fit audit": "; ".join("%s %d rows sides %s" % (w, n, "/".join(s)) for w, _c, n, s in S1.FIT_LOG)}
    lines = render(R, meta)
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(spath, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("%s  %s\n" % (_sha256(path), OUTCOME))
    for ln in lines:
        out(ln)
    out("%s outcome written: %s (sha256 %s)" % (TAG, path, _sha256(path)))
    return R, lines, path


# ================================================================================================ selftest
SELFTEST_CASES = ("ST-AMI", "ST-HIER", "ST-HF", "ST-VERDICT", "ST-RENDER", "ST-E2E", "ST-REFUSE")


def _fx_rows(rng, name, n_coarse, n_fine, n_per, dim, sep=0.6):
    rows, vecs, k = [], {}, 0
    for ci in range(n_coarse):
        cv = rng.normal(size=dim) * sep
        for fi in range(n_fine):
            fv = cv + rng.normal(size=dim)
            for j in range(n_per):
                text = "%s fixture c%d f%d item %d" % (name, ci, fi, j)
                sk = SS.stem_key(text)
                side = SS.side_of_hash(SS.side_hash(sk))
                rows.append({"item_id": "%s:x:%05d" % (name, k), "corpus": name, "orig_split": "train", "orig_idx": str(k), "text": text,
                             "coarse": "c%d" % ci, "fine": "c%d_f%d" % (ci, fi), "is_oos": 0, "annot": None, "stem_key": sk,
                             "hash_side": side, "side": side, "drop_reason": None})
                vecs[text] = (fv + 0.6 * rng.normal(size=dim)).astype(np.float32)
                k += 1
                if j % 7 == 0:                        # an exact duplicate text: same stem, same side (components < items)
                    rows.append(dict(rows[-1], item_id="%s:x:%05d" % (name, k), orig_idx=str(k)))
                    k += 1
    return rows, vecs


def _fx_graph(C, X, side, d, scrambled=False, seed=0):
    """root -> coarse groups (or, scrambled, groups mixing every coarse) -> one node per fine label -> 2 leaves for even fine labels
    (2-means on TRAIN), the fine node itself a leaf for odd ones (leaf depths 2 and 3)."""
    tr = np.nonzero(C.kept & ~C.oos & (side == SS.TRAIN))[0]
    fines = sorted(set(C.fine[tr].tolist()))
    nodes, nid = [], [2]

    def new():
        i = "n%08d" % nid[0]
        nid[0] += 1
        return i

    def node(i, kids, mem, par):
        qids = ["q_%s" % hashlib.sha256(C.text[j].encode()).hexdigest()[:16] for j in mem] if not kids else []
        nodes.append({"id": i, "childIds": kids, "parentIds": [par] if par else [], "sliceDim": d,
                      "vmfMu": S0.unit(X[mem].mean(0)[None, :])[0].tolist(), "vmfKappa": 20.0, "queryIds": qids,
                      "queryWeights": {q: 1.0 for q in qids}})
    root = "n00000001"
    if scrambled:
        groups = {}
        for fn in fines:
            groups.setdefault(fn.split("_")[1], []).append(fn)        # f0 of every coarse together, ...
    else:
        groups = {}
        for fn in fines:
            groups.setdefault(fn.split("_")[0], []).append(fn)
    gids = []
    for gname in sorted(groups):
        gid = new()
        gids.append(gid)
        fids = []
        gmem = tr[np.isin(C.fine[tr], groups[gname])]
        for fn in groups[gname]:
            fid = new()
            fids.append(fid)
            mem = tr[C.fine[tr] == fn]
            if int(fn.split("_f")[1]) % 2 == 0 and len(mem) >= 4:
                Cm = S0.skmeans(X[mem], 2, seed)
                lab = S0.assign(X[mem], Cm)
                if lab.min() == lab.max():
                    lab = np.arange(len(mem)) % 2
                lids = []
                for s in (0, 1):
                    lid = new()
                    lids.append(lid)
                    node(lid, [], mem[lab == s], fid)
                node(fid, lids, mem, gid)
            else:
                node(fid, [], mem, gid)
        node(gid, fids, gmem, root)
    node(root, gids, tr, None)
    settings = {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
    return {"rootId": root, "nodes": nodes}, settings


def build_fixture_root(td, scrambled=False, dim=16):
    """A complete on-disk data root: ingest DB, intent_emb_qwen3.db, snapshots.db, the two run dirs, a pins file."""
    rng = np.random.default_rng(11)
    rows_m, vm = _fx_rows(rng, "massive", 3, 4, 24, dim)
    rows_c, vc = _fx_rows(rng, "clinc", 4, 3, 22, dim)
    vecs = dict(vm)
    vecs.update(vc)
    os.makedirs(td, exist_ok=True)
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows_m + rows_c, [])
    emb = os.path.join(td, "intent_emb_qwen3.db")
    con = sqlite3.connect(emb)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, v.astype(">f4").tobytes()) for t, v in sorted(vecs.items())])
    con.commit()
    con.close()
    CS = S0.load_corpora(db)
    con = II.open_db_ro(db)
    items = II.rows_from_db(con)
    con.close()
    D_ex = S1.EX.derive(items)
    snap = os.path.join(td, "snapshots.db")
    con = sqlite3.connect(snap)
    con.execute("PRAGMA journal_mode=DELETE")
    con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT, settings TEXT)")
    graphs = {}
    for c, n in ARMS_USED.items():
        a = S1.ARMS[n]
        C = CS[c]
        side = S1.arm_sides(C, 1)
        R, have = S1.raw_matrix(C, vecs, dim)
        X = S1.sliced(R, 8)
        g, s = _fx_graph(C, X, side, 8, scrambled=scrambled)
        graphs[n] = g
        sid = "fx_%s_%s" % (a["slug"], "scr" if scrambled else "al")
        con.execute("INSERT INTO snapshots VALUES (?, ?, ?)", (sid, json.dumps(g), json.dumps(s)))
        con.execute("INSERT INTO snapshots VALUES (?, ?, ?)", (sid + "_later", json.dumps({"rootId": "x", "nodes": []}), json.dumps(s)))
        rd = S1.run_dir(a["slug"], td)
        os.makedirs(os.path.join(rd, "validation"), exist_ok=True)
        os.makedirs(os.path.join(rd, "diagnostics"), exist_ok=True)
        open(os.path.join(rd, "headless_run.log"), "w").write("x - Successfully generated and saved snapshot. Snapshot ID: %s\n" % sid)
        open(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt"), "w").write("")
        T = S1.tree_of(g, s)
        open(os.path.join(rd, "dag_snapshots.jsonl"), "w").write(json.dumps({"nodes": [{"id": i, "isLeaf": i in T["leaves"]} for i in T["nodes"]]}) + "\n")
        d = D_ex[(c, 1)]
        man = {"intent_build": {"arm": n, "n_train": sum(1 for r in d["rows"] if r["side"] == SS.TRAIN),
                                "n_gate": sum(1 for r in d["rows"] if r["side"] == SS.GATE)}}
        json.dump(man, open(os.path.join(rd, "diagnostics", "run_manifest.json"), "w"))
    con.commit()
    con.close()
    pins = os.path.join(td, "pins.json")
    json.dump({"schema": II.PINS_SCHEMA, "raw": {}, "ingest_db": II.file_sha(db), "emb": {"qwen3": II.file_sha(emb)}}, open(pins, "w"))
    cen, _bad = census(CS)
    return {"root": td, "pins": pins, "CS": CS, "vecs": vecs, "graphs": graphs, "census": cen, "snap": snap}


def _indep_expected(fx, c, n):
    """Independent recomputation of the deciding numbers of one corpus: sklearn AMI, scipy cut_tree, a parent walk on the graph JSON,
    an explicit permutation loop for the random trees."""
    from sklearn.metrics import adjusted_mutual_info_score as AMI
    from scipy.cluster.hierarchy import linkage, cut_tree
    C = fx["CS"][c]
    g = fx["graphs"][n]
    nodes = {x["id"]: x for x in g["nodes"]}
    par = {}
    for x in g["nodes"]:
        for k in x["childIds"]:
            par[k] = x["id"]
    leaves = sorted(i for i, x in nodes.items() if not x["childIds"])
    mu = np.array([nodes[i]["vmfMu"] for i in leaves])
    R = np.array([fx["vecs"][t][:8] for t in C.text], dtype=np.float64)
    X = R / np.linalg.norm(R, axis=1, keepdims=True)
    ok = C.kept & ~C.oos
    ev = np.nonzero(ok & (C.side == SS.EVAL))[0]
    tr = np.nonzero(ok & (C.side == SS.TRAIN))[0]
    fl = np.argmax(X[ev] @ mu.T, axis=1)

    def anc(lf, d):
        ch = [lf]
        while ch[-1] in par:
            ch.append(par[ch[-1]])
        dep = len(ch) - 1
        return ch[dep - d] if dep >= d else lf
    depths = {}
    for lf in leaves:
        k, x = 0, lf
        while x in par:
            x = par[x]
            k += 1
        depths[lf] = k
    dmax = max(depths.values())
    truth = [str(v) for v in C.coarse[ev]]
    tree_amis, ks = [], []
    for d in range(1, dmax + 1):
        lab = [anc(leaves[j], d) for j in fl]
        ks.append(len(set(anc(lf, d) for lf in leaves)))
        tree_amis.append(AMI(truth, lab))
    Lc = len(leaves)
    Z = linkage(X[tr], method="average", metric="cosine")
    lab_L = cut_tree(Z, n_clusters=Lc).ravel()
    cent = np.array([X[tr][lab_L == j].mean(0) for j in range(Lc)])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    fe = np.argmax(X[ev] @ cent.T, axis=1)
    avg_amis = []
    for kk in ks:
        lab_k = cut_tree(Z, n_clusters=kk).ravel()
        lift = {}
        for a_, b_ in zip(lab_L, lab_k):
            lift.setdefault(int(a_), set()).add(int(b_))
        assert all(len(v) == 1 for v in lift.values())
        avg_amis.append(AMI(truth, [next(iter(lift[int(j)])) for j in fe]))
    # DP and its random draws (explicit permutations, same generator stream)
    tp = {k: v for k, v in par.items()}
    leaf_ids = [leaves[j] for j in fl]
    cls = list(C.coarse[ev])
    dp = S1.dendrogram_purity(tp, leaves, leaf_ids, cls)
    rng = np.random.default_rng(SEED_RANDOM)
    rnd = []
    for _ in range(N_RANDOM):
        p = rng.permutation(Lc)
        rnd.append(S1.dendrogram_purity(tp, leaves, [leaves[p[leaves.index(x)]] for x in leaf_ids], cls))
    _u, mcount = np.unique(np.array([C.stem[i] for i in ev], dtype=object), return_counts=True)
    return {"n": len(ev), "G": len(mcount), "kish": float((mcount ** 2).sum()) / mcount.sum(), "ks": ks, "tree_best": max(tree_amis), "best_depth": int(np.argmax(tree_amis)) + 1, "dmax": dmax,
            "avg_best": max(avg_amis), "D1": max(tree_amis) - max(avg_amis), "dp": dp, "p975": float(np.percentile(rnd, 97.5)),
            "tree_amis": tree_amis, "avg_amis": avg_amis, **_indep_hf(C, ev, fl, fe, leaves, par, nodes, Z, lab_L, Lc, ks, anc)}


def _indep_hf(C, ev, fl, fe, leaves, par, nodes, Z, lab_L, Lc, ks, anc):
    """HIER-F, independently: explicit item sets per node (graph JSON walk / scipy cut_tree clusters at every k), brute-force F."""
    from scipy.cluster.hierarchy import cut_tree
    from sklearn.metrics import fowlkes_mallows_score as FMS
    gold = [str(v) for v in C.fine[ev]]
    classes = sorted(set(gold))

    def hf_of(node_sets, item_leaf):
        tot = 0.0
        for c in classes:
            ic = {i for i, g in enumerate(gold) if g == c}
            best = 0.0
            for ls in node_sets:
                iv = {i for i, lf in enumerate(item_leaf) if lf in ls}
                k = len(ic & iv)
                if k:
                    best = max(best, 2.0 * k / (len(iv) + len(ic)))
            tot += len(ic) / len(gold) * best
        return tot

    def leafset(n):
        if not nodes[n]["childIds"]:
            return {n}
        out = set()
        for k in nodes[n]["childIds"]:
            out |= leafset(k)
        return out
    tsets = [frozenset(leafset(n)) for n in nodes]
    hf_t = hf_of(tsets, [leaves[j] for j in fl])
    asets = set()
    for k in range(1, Lc + 1):
        lab_k = cut_tree(Z, n_clusters=k).ravel()
        for q in set(lab_k.tolist()):
            asets.add(frozenset(int(x) for x in set(lab_L[lab_k == q].tolist())))
    hf_a = hf_of(list(asets), [int(j) for j in fe])
    rng = np.random.default_rng(SEED_RANDOM)
    rnd = []
    for _ in range(N_RANDOM):
        p = rng.permutation(Lc)
        rnd.append(hf_of(tsets, [leaves[p[j]] for j in fl]))
    fm_f = [FMS(gold, [anc(leaves[j], d) for j in fl]) for d in range(1, len(ks) + 1)]
    return {"hf_tree": hf_t, "hf_avg": hf_a, "hf_D": hf_t - hf_a, "hf_p975": float(np.percentile(rnd, 97.5)), "fm_tree_fine": fm_f}


def selftest(only=None, quiet=False):
    sel = set(only or SELFTEST_CASES)
    n_ok = [0]

    def check(cond, what):
        if not cond:
            raise AssertionError("SELFTEST FAILED: " + what)
        n_ok[0] += 1

    def refused(fn, needle):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
        except SystemExit as e:
            check(needle in str(e), "refusal %r carries %r" % (str(e)[:240], needle))
            return
        raise AssertionError("SELFTEST FAILED: expected a refusal containing %r" % needle)

    td = tempfile.mkdtemp(prefix="gran_gt_st_")
    saved_n = dict(REGISTERED_N)
    try:
        if "ST-AMI" in sel:
            from sklearn.metrics import adjusted_mutual_info_score as AMI
            rng = np.random.default_rng(5)
            for trial in range(12):
                n = int(rng.integers(30, 400))
                t = rng.integers(0, int(rng.integers(2, 12)), size=n)
                p = (t * int(rng.integers(0, 2)) + rng.integers(0, int(rng.integers(2, 30)), size=n)) % 40
                check(abs(ami(t, p) - AMI(t, p)) < 1e-9, "AMI == sklearn (trial %d: %.12f vs %.12f)" % (trial, ami(t, p), AMI(t, p)))
                w = rng.integers(0, 3, size=n).astype(float)
                rep = np.repeat(np.arange(n), w.astype(int))
                if len(set(t[rep])) > 0 and len(rep) > 1:
                    check(abs(ami(t, p, w) - AMI(t[rep], p[rep])) < 1e-9, "weighted AMI == sklearn on the expanded copies (trial %d)" % trial)
            check(ami([0, 0, 0], [1, 1, 1]) == 1.0, "one cluster both sides = 1.0")
            check(abs(ami([0, 1, 0, 1], [0, 0, 0, 0])) < 1e-12, "one predicted cluster against two classes = 0")
            check(abs(ami([0, 0, 1, 1, 2, 2], [5, 5, 3, 3, 1, 1]) - 1.0) < 1e-12, "a relabelled identical partition = 1")
            b, j, v = best_cut(np.array([0, 0, 1, 1]), [np.array([0, 0, 0, 0]), np.array([0, 0, 1, 1]), np.array([0, 1, 2, 3])])
            check(j == 1 and abs(b - 1.0) < 1e-12, "best_cut takes the MAX (index 1, AMI 1)")
            b2, j2, _ = best_cut(np.array([0, 0, 1, 1]), [np.array([0, 0, 1, 1]), np.array([0, 0, 1, 1])])
            check(j2 == 0, "best_cut ties go to the shallowest cut")
        if "ST-HIER" in sel:
            par = {"l1": "a", "l2": "a", "l3": "b", "a": "r", "b": "r", "l4": "c", "c": "b", "l5": "c"}
            T = {"leaves": ["l1", "l2", "l3", "l4", "l5"], "tparent": par}
            cuts, depth = tree_depth_cuts(T)
            check(depth == [2, 2, 2, 3, 3], "leaf depths %s" % depth)
            check([k for _d, k, _c in cuts] == [2, 4, 5], "k_d per depth %s (depth 1: a, b; depth 2: l1 l2 l3 c; depth 3: all leaves)" % [k for _d, k, _c in cuts])
            c1 = cuts[0][2]
            check(c1[0] == c1[1] and c1[2] == c1[3] == c1[4] and c1[0] != c1[2], "depth-1 cut groups {l1,l2} and {l3,l4,l5}")
            c2 = cuts[1][2]
            check(c2[3] == c2[4] and len(set(c2[:3].tolist())) == 3 and c2[2] != c2[3], "depth-2 cut: l3 stays itself, l4/l5 under c")
            H = {"leaves": ["x1", "x2", "x3", "x4"], "parent": {"x1": "p", "x2": "p", "x3": "q", "x4": "q", "p": "r", "q": "r"},
                 "order": ["r", "q", "p"], "root": "r"}
            H["kids"] = _kids_of(H["parent"])
            check(frontier_cut(H, 1).tolist() == [0, 0, 0, 0], "k 1 = one cluster")
            k2 = frontier_cut(H, 2)
            check(k2[0] == k2[1] and k2[2] == k2[3] and k2[0] != k2[2], "k 2 = {x1,x2} {x3,x4}")
            k3 = frontier_cut(H, 3)
            check(k3[0] == k3[1] and k3[2] != k3[3], "k 3 expands q before p (order coarse -> fine)")
            check(len(set(frontier_cut(H, 4).tolist())) == 4, "k 4 = the leaves")
            # planted data: average-link and bisecting recover 4 well-separated groups (2 x 2 nested)
            rng = np.random.default_rng(3)
            top = [rng.normal(size=6) * 4 for _ in range(2)]
            cen = [t + rng.normal(size=6) * 1.5 for t in top for _ in range(2)]
            Xp = S0.unit(np.vstack([c + 0.05 * rng.normal(size=(30, 6)) for c in cen]))
            gold = np.repeat(np.arange(4), 30)
            Ha, la = avglink_hierarchy(Xp, 4)
            check(len(Ha["leaves"]) == 4 and abs(ami(gold, la) - 1.0) < 1e-12, "average-link at L 4 recovers the planted groups")
            check(len(Ha["order"]) == 3 and Ha["root"] not in Ha["parent"], "average-link hierarchy: L - 1 internal nodes, a root")
            for s in (0, 1):
                Hb, lb = bisect_hierarchy(Xp, 4, s)
                check(len(Hb["leaves"]) == 4 and abs(ami(gold, lb) - 1.0) < 1e-12, "bisecting seed %d recovers the planted groups" % s)
                check(len(Hb["order"]) == 3, "bisecting: L - 1 splits")
            # largest-inertia rule: one tight big cluster vs one loose small cluster: the loose one is split first
            Xi = S0.unit(np.vstack([np.array([1, 0, 0, 0]) + 0.005 * rng.normal(size=(50, 4)),
                                    np.array([0, 1, 0, 0.3]) + 0.005 * rng.normal(size=(5, 4)), np.array([0, 1, 0, -0.3]) + 0.005 * rng.normal(size=(5, 4))]))
            for s in (0, 1, 2):
                Hi, li = bisect_hierarchy(Xi, 3, s)
                check(sorted(np.bincount(li).tolist()) == [5, 5, 50], "seed %d: the second split goes to the loose small cluster (largest "
                      "inertia), not the big tight one (%s)" % (s, sorted(np.bincount(li).tolist())))
            # random matched-shape: the parent map is unchanged, each draw is a permutation of leaf ids
            leaves = ["l1", "l2", "l3", "l4", "l5"]
            items = ["l1", "l1", "l2", "l3", "l4", "l5", "l5"]
            cls = ["A", "A", "A", "B", "B", "B", "B"]
            par_copy = dict(par)
            dps = random_shape_dps(par, leaves, items, cls, 50, 1)
            check(par == par_copy and len(dps) == 50, "random draws keep the tree's parent map")
            rng2 = np.random.default_rng(1)
            p0 = rng2.permutation(5)
            mp = {leaves[j]: leaves[p0[j]] for j in range(5)}
            check(abs(dps[0] - S1.dendrogram_purity(par, leaves, [mp[x] for x in items], cls)) < 1e-12, "draw 0 = the explicit permutation")
            check(len(set(np.round(dps, 9))) > 1, "random draws differ")
            check(abs(mc_se_pct([1.0] * 10, 97.5, 50, 0)) < 1e-12 and mc_se_pct(list(range(200)), 97.5, 200, 0) > 0, "MC SE of p97.5")
        if "ST-HF" in sel:
            from sklearn.metrics import fowlkes_mallows_score as FMS
            par = {"l1": "a", "l2": "a", "l3": "b", "a": "r", "b": "r"}
            leaves = ["l1", "l2", "l3"]
            nodes, Am = node_matrix(par, leaves)
            check(nodes == ["a", "b", "l1", "l2", "l3", "r"] and Am.sum() == 3 + 3 + 2 + 1 - 0 and Am[nodes.index("r")].all(), "node matrix")
            lidx = np.array([0, 0, 1, 1, 2, 2, 2])
            gold = np.array([0, 0, 0, 0, 1, 1, 1])
            hf, arg = hier_f(Am, lidx, gold, 2)
            check(abs(hf - 1.0) < 1e-12 and nodes[arg[0]] == "a", "HF credits class 0 at the internal node a (F 1), not at a leaf (HF 1.0)")
            hf2, _ = hier_f(Am, np.array([0, 1, 1, 2, 2, 2, 0]), np.array([0, 0, 1, 1, 1, 0, 1]), 2)
            # brute force: class 0 = items {0,1,5} (leaves l1,l2,l3), class 1 = {2,3,4,6}
            sets = {"a": {0, 1, 2, 6}, "b": {3, 4, 5}, "l1": {0, 6}, "l2": {1, 2}, "l3": {3, 4, 5}, "r": set(range(7))}
            bf = 0.0
            for cset in ({0, 1, 5}, {2, 3, 4, 6}):
                bf += len(cset) / 7.0 * max(2.0 * len(cset & s_) / (len(cset) + len(s_)) for s_ in sets.values())
            check(abs(hf2 - bf) < 1e-12, "HF == brute force (%.6f vs %.6f)" % (hf2, bf))
            rng = np.random.default_rng(9)
            li, gi = rng.integers(0, 3, 40), rng.integers(0, 4, 40)
            w = rng.integers(0, 3, 40).astype(float)
            rep = np.repeat(np.arange(40), w.astype(int))
            check(abs(hier_f(Am, li, gi, 4, w)[0] - hier_f(Am, li[rep], gi[rep], 4)[0]) < 1e-12, "weighted HF == HF on the expanded copies")
            dr = random_shape_hf(Am, li, gi, 4, 20, 3)
            p0 = np.random.default_rng(3).permutation(3)
            check(abs(dr[0] - hier_f(Am, p0[li], gi, 4)[0]) < 1e-12 and len(dr) == 20, "HF random draw 0 = the explicit permutation (GR2's stream)")
            # taxonomic P / R / F: TRAIN l1 f0 x2, l2 f2 x3 (both C0), l3 f1 (C1); EVAL item at l1 gold (C0, f0), item at l3 gold (C0, f0)
            P_, R_, F_ = tax_prf(Am, nodes, np.array([0, 2]), np.array([0, 0]), np.array([0, 0]), np.array([0, 0, 1, 1, 1, 2]),
                                 np.array([0, 0, 0, 0, 0, 1]), np.array([0, 0, 2, 2, 2, 1]), 2, 3, "r")
            check(abs(P_ - 0.4) < 1e-12 and abs(R_ - 0.5) < 1e-12 and abs(F_ - 2 * 0.4 * 0.5 / 0.9) < 1e-12,
                  "taxonomic P 2/5, R 2/4 (root excluded; a carries f2) (%.4f, %.4f)" % (P_, R_))
            ix = {n_: i for i, n_ in enumerate(nodes)}
            f2c = {0: 0, 1: 1, 2: 0}
            bc = np.array([ix["a"], ix["b"]])
            bfn = np.array([ix["l1"], ix["b"], ix["l2"]])
            check(abs(ancestor_f1(Am, bc, bfn, f2c, [0, 1], [0, 1, 2]) - 1.0) < 1e-12, "ancestor-F1 1.0 (ancestor-OR-SELF: C1 and f1 both at b)")
            bc2 = np.array([ix["a"], ix["r"]])
            check(abs(ancestor_f1(Am, bc2, bfn, f2c, [0, 1], [0, 1, 2]) - 0.75) < 1e-12, "ancestor-F1 0.75 when C1 sits at the root (P 3/5, R 1)")
            for _ in range(6):
                t_, p_ = rng.integers(0, 5, 60), rng.integers(0, 7, 60)
                check(abs(fm_index(t_, p_) - FMS(t_, p_)) < 1e-12, "FM == sklearn")
        if "ST-VERDICT" in sel:
            check(gr1_corpus(0.05, 0.01, 0.09, 0.02) == "TREE-BETTER", "GR1 TREE-BETTER")
            check(gr1_corpus(0.05, -0.01, 0.09, 0.02) == "NEITHER", "GR1 interval clause binds")
            check(gr1_corpus(0.015, 0.001, 0.03, 0.02) == "NEITHER", "GR1 spread clause binds (D1 <= spread_B)")
            check(gr1_corpus(0.02, 0.001, 0.03, 0.02) == "NEITHER", "GR1 D1 == spread_B is not > (strict)")
            check(gr1_corpus(0.05, 0.0, 0.09, 0.02) == "NEITHER", "GR1 lo == 0 is not > 0")
            check(gr1_corpus(-0.05, -0.09, -0.01, 0.02) == "AVG-BETTER", "GR1 AVG-BETTER")
            check(gr1_corpus(-0.05, -0.09, 0.0, 0.02) == "NEITHER", "GR1 hi == 0 is not < 0")
            check(gr1_corpus(-0.015, -0.03, -0.001, 0.02) == "NEITHER", "GR1 AVG spread clause binds")
            check(gr1_overall("TREE-BETTER", "TREE-BETTER") == "TREE-BETTER", "GR1 overall needs both (tree)")
            check(gr1_overall("TREE-BETTER", "NEITHER") == "MIXED", "GR1 overall: one corpus is MIXED")
            check(gr1_overall("AVG-BETTER", "AVG-BETTER") == "AVG-BETTER", "GR1 overall needs both (avg)")
            check(gr1_overall("NEITHER", "AVG-BETTER") == "MIXED", "GR1 overall: avg on one only")
            check(gr1_overall("NEITHER", "NEITHER") == "MIXED", "GR1 overall: NEITHER on both reads MIXED (verbatim)")
            check(abs(spread_b({0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.5}) - 0.4) < 1e-12, "spread_B reads seed 4")
            check(abs(spread_b({0: 0.3, 1: 0.3, 2: 0.1, 3: 0.2, 4: 0.3}) - 0.2) < 1e-12, "spread_B = max - min over all five")
            refused(lambda: spread_b({0: 0.1, 1: 0.2}), "spread_B needs seeds")
            check(gr2_corpus(0.81, 0.80) is True and gr2_corpus(0.80, 0.80) is False, "GR2 strict >")
            pa_, ab_ = above_random(0.9, list(np.linspace(0.0, 1.0, 201)))
            check(abs(pa_ - 0.975) < 1e-12 and ab_ is False and above_random(0.98, list(np.linspace(0.0, 1.0, 201)))[1] is True,
                  "above_random: p97.5 of the draws (0.9 lies above the median and below p97.5: NOT above)")
            check(above_random(pa_, list(np.linspace(0.0, 1.0, 201)))[1] is False, "above_random: equal to p97.5 is NOT above (strict)")
            check(gr2_overall(True, True) == "HELD" and gr2_overall(False, False) == "FAILED", "GR2 HELD / FAILED")
            check(gr2_overall(True, False) == "MIXED" and gr2_overall(False, True) == "MIXED", "GR2 MIXED")
            check(band(-0.05, -0.05, 0.03) == "HELD" and band(0.03, -0.05, 0.03) == "HELD" and band(0.031, -0.05, 0.03) == "FAILED", "bands inclusive")
            check(band(float("nan"), -1, 1) == "FAILED", "a NaN point FAILS its band")
            check(abs(brier(0.75, True) - 0.0625) < 1e-12 and abs(brier(0.75, False) - 0.5625) < 1e-12, "Brier")
        if "ST-RENDER" in sel:
            def mkhf(D, lo, hi, sp, above):
                arm = {"hf_f": 0.6, "hf_c": 0.7, "tax": (0.5, 0.4, 0.4444), "anc_f1": 0.8}
                return {"arms": {"tree": arm, "avg": arm, "bis0": arm}, "hf_tree": 0.6, "hf_avg": 0.6 - D, "bis_hf": {s: 0.5 for s in SEEDS_B},
                        "spread_B": sp, "D": D, "lo": lo, "hi": hi, "se": 0.01, "mde": 0.028, "hf1": gr1_corpus(D, lo, hi, sp),
                        "rnd_p975": 0.5 if above else 0.65, "rnd_med": 0.4, "rnd_ge": 0 if above else 40, "n_random": 200, "rnd_mc_se": 0.002,
                        "hf2_above": above, "fm_tree": {"coarse": [0.5, 0.4, 0.3], "fine": [0.2, 0.3, 0.4]},
                        "fm_k": {"avg": {"coarse": [0.5, 0.4, 0.3], "fine": [0.2, 0.3, 0.4]}, "bis0": {"coarse": [0.5, 0.4, 0.3], "fine": [0.2, 0.3, 0.4]}},
                        "bk": {"avg": [0.1] * 8}}

            def mk(D1, lo, hi, sp, above, bd, dmax, hf=None):
                ks = [2, 5, 9]
                r = {"n": 100, "G": 98, "kish": 1.02, "neff": 98.0, "n_train": 300, "L": 9, "leaf_depths": {"2": 3, "3": 6}, "ks": ks,
                     "depths": [1, 2, 3], "dmax": dmax, "tree_ami_c": [0.5, 0.4, 0.3], "tree_ami_f": [0.2, 0.3, 0.4],
                     "avg_ami_c": [0.4, 0.4, 0.3], "avg_ami_f": [0.2, 0.3, 0.4], "bis_ami_c": {s: [0.4, 0.3, 0.2] for s in SEEDS_B},
                     "tree_c": 0.5, "best_depth_c": bd, "tree_best_j": bd - 1, "avg_c": 0.4, "avg_best_j": 0,
                     "bis_c": {s: 0.4 + 0.001 * s for s in SEEDS_B}, "spread_B": sp, "tree_f": 0.4, "best_depth_f": 3, "avg_f": 0.4,
                     "bis_f": {s: 0.3 for s in SEEDS_B}, "avg_any_c": 0.45, "avg_any_k": 4, "D1": D1, "lo": lo, "hi": hi, "se": 0.01,
                     "mde": 0.028, "gr1": gr1_corpus(D1, lo, hi, sp), "dp_tree": 0.7, "n_random": 200, "rnd_p975": 0.6 if above else 0.75,
                     "rnd_mc_se": 0.003, "rnd_med": 0.5, "rnd_ge": 0 if above else 30, "gr2_above": above, "dp_h": {"avg": 0.6, "bis0": 0.6},
                     "hcv": {"tree": {"coarse": (1, 1, 1), "fine": (1, 1, 1)}, "avg": {"coarse": (1, 1, 1), "fine": (1, 1, 1)}},
                     "bis_leaves": {s: 9 for s in SEEDS_B}}
                r["hf"] = mkhf(*(hf or (D1, lo, hi, sp, above)))
                return r

            def rr(m, k):
                R = {"corpora": {"massive": m, "clinc": k}, "boot_b": 10, "n_random": 200}
                R["GR1"] = gr1_overall(m["gr1"], k["gr1"])
                R["GR2"] = gr2_overall(m["gr2_above"], k["gr2_above"])
                R["HF2"] = gr2_overall(m["hf"]["hf2_above"], k["hf"]["hf2_above"])
                return "\n".join(render(R, {"x": "y"}))
            t = rr(mk(0.05, 0.01, 0.09, 0.004, True, 1, 3), mk(0.06, 0.02, 0.1, 0.004, True, 2, 3))
            check("GR1 (DECIDING): MASSIVE TREE-BETTER, CLINC TREE-BETTER -> GR1 TREE-BETTER" in t, "render GR1 TREE-BETTER")
            check("'right at a different granularity' may be written" in t, "render TREE-BETTER sentence")
            check("-> GR2 HELD" in t and "GR2 HELD is not refuted" in t and "F-GR does not fire (GR2 HELD)" in t, "render GR2 HELD branch")
            check("P2 GR2 HELD 0.75: event TRUE, Brier 0.0625" in t, "P2 TRUE Brier")
            check("P3 coarse best depth shallower than the leaves on both corpora 0.9 (DESCRIPTIVE): MASSIVE 1 of 3, CLINC 2 of 3: event TRUE, Brier 0.0100" in t, "P3 TRUE")
            check("P1 D1 MASSIVE +0.05000 vs -0.01 [-0.05, +0.03]: FAILED" in t, "P1 MASSIVE FAILED outside the band")
            check("P1 'GR1 NEITHER 0.6': NOT SCORED (registration defect GG-1" in t and "overall TREE-BETTER" in t, "P1 probability clause NOT SCORED")
            check(sum(1 for ln in t.splitlines() if "'GR1 NEITHER 0.6'" in ln) == 1 and "NEITHER 0.6': Brier" not in t, "P1 probability clause never scored")
            check("massive GR1 D1 = +0.05000, 95% [+0.01000, +0.09000] (percentile, components), spread_B 0.00400 -> TREE-BETTER" in t, "per-corpus GR1 line")
            check("SUPPORT: realised n 100 / 98 components, DEFF(Kish) 1.0200, n_eff 98, SE(D1) 0.01000, MDE80 0.02800" in t, "support line")
            check("VERDICT LINE GR1: DESCRIPTIVE-ONLY at the prediction" in t, "registered verdict line printed")
            t = rr(mk(-0.05, -0.09, -0.01, 0.004, False, 3, 3), mk(-0.06, -0.1, -0.02, 0.004, False, 3, 3))
            check("-> GR1 AVG-BETTER" in t and "GR1 AVG-BETTER: average-link's best cut agrees with the coarse gold better than the tree's on both corpora" in t
                  and "GR1 MIXED: no common word" not in t, "render GR1 AVG-BETTER")
            check("-> GR2 FAILED" in t and "GR2 HELD is REFUTED: DP(tree) <= the random p97.5 on massive, clinc" in t, "render FAILS line both")
            check("F-GR FIRES" in t, "render F-GR fires")
            check("P2 GR2 HELD 0.75: event FALSE, Brier 0.5625" in t, "P2 FALSE Brier")
            check("event FALSE, Brier 0.8100" in t, "P3 FALSE when best depth = D_max")
            check("P1 D1 CLINC -0.06000 vs -0.01 [-0.05, +0.03]: FAILED" in t and "P1 D1 MASSIVE -0.05000 vs -0.01 [-0.05, +0.03]: HELD" in t, "P1 bands")
            t = rr(mk(0.0, -0.02, 0.02, 0.004, True, 1, 3), mk(0.0, -0.02, 0.02, 0.004, False, 1, 3))
            check("MASSIVE NEITHER, CLINC NEITHER -> GR1 MIXED" in t and "GR1 MIXED: no common word" in t, "render GR1 MIXED (NEITHER both)")
            check("-> GR2 MIXED" in t and "REFUTED: DP(tree) <= the random p97.5 on clinc" in t and "F-GR does not fire (GR2 MIXED)" in t, "render GR2 MIXED")
            check("NOT ABOVE-RANDOM" in t, "render NOT ABOVE-RANDOM word")
            # HIER-F branches, read from the hf dicts (diverging from GR on purpose)
            t = rr(mk(0.05, 0.01, 0.09, 0.004, True, 1, 3, hf=(0.04, 0.01, 0.07, 0.01, True)),
                   mk(0.06, 0.02, 0.1, 0.004, True, 2, 3, hf=(0.0, -0.02, 0.02, 0.01, False)))
            check("-> GR2 HELD" in t and "-> HF2 MIXED" in t and "F-HF does not fire (HF2 MIXED)" in t, "render HF2 MIXED from the hf dicts (GR2 HELD)")
            check("HF2 HELD is REFUTED: HF(tree) <= the random p97.5 on clinc" in t, "render HF FAILS line names clinc")
            check("HF1 (DECIDING, per corpus): MASSIVE TREE-BETTER, CLINC NEITHER" in t, "render HF1 per-corpus words")
            check("HF P1 D MASSIVE +0.04000 vs +0.01 [-0.03, +0.05]: HELD; HF1 NEITHER 0.60 (per corpus): event FALSE, Brier 0.3600" in t
                  and "HF P1 D CLINC +0.00000 vs +0.01 [-0.03, +0.05]: HELD; HF1 NEITHER 0.60 (per corpus): event TRUE, Brier 0.1600" in t, "render HF P1 lines")
            check("HF P2 HF2 HELD 0.75: event FALSE, Brier 0.5625" in t, "render HF P2 FALSE on MIXED")
            check("massive HF1 D = +0.04000, 95% [+0.01000, +0.07000] (percentile, components), spread_B(HF) 0.01000, SE 0.01000, MDE80 0.02800 -> TREE-BETTER" in t,
                  "render HF1 line")
            check("HF P3 (MMLU-Pro recovery, DESCRIPTIVE): NOT EVALUATED" in t, "render HF P3")
            t = rr(mk(0.05, 0.01, 0.09, 0.004, True, 1, 3, hf=(-0.05, -0.09, -0.01, 0.01, False)),
                   mk(0.06, 0.02, 0.1, 0.004, True, 2, 3, hf=(0.07, 0.02, 0.1, 0.01, False)))
            check("-> HF2 FAILED" in t and "F-HF FIRES" in t and "HF2 HELD is REFUTED: HF(tree) <= the random p97.5 on massive, clinc" in t,
                  "render HF2 FAILED, F-HF fires")
            check("HF1 (DECIDING, per corpus): MASSIVE AVG-BETTER, CLINC TREE-BETTER" in t, "render HF1 AVG-BETTER")
            check("HF P1 D CLINC +0.07000 vs +0.01 [-0.03, +0.05]: FAILED" in t, "render HF P1 FAILED outside the band")
            t = rr(mk(0.05, 0.01, 0.09, 0.004, False, 1, 3, hf=(0.04, 0.01, 0.07, 0.01, True)),
                   mk(0.06, 0.02, 0.1, 0.004, False, 2, 3, hf=(0.04, 0.01, 0.07, 0.01, True)))
            check("-> GR2 FAILED" in t and "-> HF2 HELD" in t and "HF2 HELD is not refuted" in t and "F-HF does not fire (HF2 HELD)" in t
                  and "HF P2 HF2 HELD 0.75: event TRUE, Brier 0.0625" in t, "render HF2 HELD while GR2 FAILED")
        if "ST-E2E" in sel or "ST-REFUSE" in sel:
            fa = build_fixture_root(os.path.join(td, "al"))
            fs = build_fixture_root(os.path.join(td, "scr"), scrambled=True)
            for k_ in CORPORA:
                REGISTERED_N[k_] = fa["census"][k_]
        if "ST-E2E" in sel:
            for fx, scr in ((fa, False), (fs, True)):
                od = os.path.join(td, "out_scr" if scr else "out_al")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    R, lines, path = run(data_root=fx["root"], pins_file=fx["pins"], out_dir=od, boot_b=60, n_random=N_RANDOM,
                                         skip_heavy=True, out=lambda s: None)
                txt = open(path, encoding="utf-8").read()
                check(txt == "\n".join(lines) + "\n", "the file of record carries the rendered lines")
                sums = open(os.path.join(od, SUMS), encoding="utf-8").read()
                check(sums.split()[0] == _sha256(path), "SHA256SUMS carries the outcome's sha256")
                for c, n in ARMS_USED.items():
                    e = _indep_expected(fx, c, n)
                    r = R["corpora"][c]
                    tag = "%s %s" % ("scr" if scr else "al", c)
                    check(r["n"] == e["n"] == fx["census"][c][0], "%s: n EVAL %d == independent %d (EVAL side)" % (tag, r["n"], e["n"]))
                    check(r["G"] == e["G"] < r["n"] and abs(r["kish"] - e["kish"]) < 1e-12 and abs(r["neff"] - e["n"] / e["kish"]) < 1e-9,
                          "%s: components %d < n, Kish %.4f, n_eff = n / Kish (independent)" % (tag, r["G"], r["kish"]))
                    check(r["ks"] == e["ks"], "%s: k_d %s == independent %s" % (tag, r["ks"], e["ks"]))
                    check(np.allclose(r["tree_ami_c"], e["tree_amis"], atol=1e-9), "%s: tree AMI per depth == sklearn on a parent walk" % tag)
                    check(np.allclose(r["avg_ami_c"], e["avg_amis"], atol=1e-9), "%s: average-link AMI per matched k == scipy cut_tree + sklearn" % tag)
                    check(abs(r["tree_c"] - e["tree_best"]) < 1e-9 and r["best_depth_c"] == e["best_depth"], "%s: best-cut tree AMI and depth" % tag)
                    check(abs(r["D1"] - e["D1"]) < 1e-9, "%s: D1 %.6f == independent %.6f" % (tag, r["D1"], e["D1"]))
                    check(abs(r["dp_tree"] - e["dp"]) < 1e-12 and abs(r["rnd_p975"] - e["p975"]) < 1e-12,
                          "%s: DP %.6f and random p97.5 %.6f == the explicit permutation loop (%.6f, %.6f)" % (tag, r["dp_tree"], r["rnd_p975"], e["dp"], e["p975"]))
                    check(r["dmax"] == e["dmax"] == 3, "%s: D_max 3" % tag)
                    check(r["se"] > 0, "%s: the bootstrap moves (SE %.5f)" % (tag, r["se"]))
                    check(r["lo"] < r["hi"], "%s: a non-degenerate interval" % tag)
                    check(abs(r["spread_B"] - (max(r["bis_c"].values()) - min(r["bis_c"].values()))) < 1e-12 and len(r["bis_c"]) == 5,
                          "%s: spread_B over the five seeds" % tag)
                    check(abs(r["mde"] - 2.8 * r["se"]) < 1e-12 and abs(r["neff"] - r["n"] / r["kish"]) < 1e-9, "%s: MDE80 = 2.8 SE, n_eff = n / Kish" % tag)
                    check(r["gr1"] == gr1_corpus(r["D1"], r["lo"], r["hi"], r["spread_B"]), "%s: GR1 word from the printed numbers" % tag)
                    want = "%s %s GR1 D1 = %s, 95%% [%s, %s]" % (TAG, c, f(e["D1"]), f(r["lo"]), f(r["hi"]))
                    check(want in txt, "%s: the printed GR1 line carries the independent D1 (%s)" % (tag, want))
                    check(("%s %s GR2 DP(tree, coarse) %.5f" % (TAG, c, e["dp"])) in txt and ("p97.5 %.5f" % e["p975"]) in txt, "%s: printed DP and p97.5" % tag)
                    h = r["hf"]
                    check(abs(h["hf_tree"] - e["hf_tree"]) < 1e-12 and abs(h["hf_avg"] - e["hf_avg"]) < 1e-12 and abs(h["D"] - e["hf_D"]) < 1e-12,
                          "%s: HF tree %.6f / average-link %.6f / D == brute force on explicit node item sets (%.6f / %.6f)" % (
                              tag, h["hf_tree"], h["hf_avg"], e["hf_tree"], e["hf_avg"]))
                    check(abs(h["rnd_p975"] - e["hf_p975"]) < 1e-12, "%s: HF random p97.5 %.6f == the explicit permutation loop %.6f" % (tag, h["rnd_p975"], e["hf_p975"]))
                    check(np.allclose(h["fm_tree"]["fine"], e["fm_tree_fine"], atol=1e-12), "%s: FM per depth == sklearn fowlkes_mallows_score" % tag)
                    check(h["se"] > 0 and h["lo"] < h["hi"] and abs(h["mde"] - 2.8 * h["se"]) < 1e-12, "%s: HF bootstrap moves; MDE80 = 2.8 SE" % tag)
                    check(abs(h["spread_B"] - spread_b(h["bis_hf"])) < 1e-12 and h["hf1"] == gr1_corpus(h["D"], h["lo"], h["hi"], h["spread_B"]),
                          "%s: HF1 word from the printed numbers" % tag)
                    check(h["hf2_above"] is bool(e["hf_tree"] > e["hf_p975"]), "%s: HF2 word from the independent numbers" % tag)
                    check(("%s %s HF1 D = %s, 95%% [%s, %s]" % (TAG, c, f(e["hf_D"]), f(h["lo"]), f(h["hi"]))) in txt
                          and ("HF2 HF(tree, fine) %.5f" % e["hf_tree"]) in txt and ("p97.5 %.5f" % e["hf_p975"]) in txt, "%s: printed HF1 / HF2 lines" % tag)
                    check(0 <= h["arms"]["tree"]["tax"][2] <= 1 and 0 <= h["arms"]["tree"]["anc_f1"] <= 1, "%s: taxonomic F and ancestor-F1 in [0, 1]" % tag)
                    check(r["gr2_above"] is (not scr),"%s: GR2 %s" % (tag, "NOT ABOVE (scrambled hierarchy)" if scr else "ABOVE-RANDOM (aligned hierarchy)"))
                    check(r["best_depth_c"] == 1 if not scr else True, "%s: aligned tree's coarse best cut is depth 1" % tag)
                if not scr:
                    check([R["corpora"][c]["gr1"] for c in CORPORA] == ["TREE-BETTER", "TREE-BETTER"] and R["GR1"] == "TREE-BETTER"
                          and "-> GR1 TREE-BETTER" in txt, "aligned: GR1 TREE-BETTER on both corpora (D1 well above spread_B, interval > 0)")
                    check(R["GR2"] == "HELD" and "-> GR2 HELD" in txt and "F-GR does not fire (GR2 HELD)" in txt, "aligned: GR2 HELD printed")
                    check("P2 GR2 HELD 0.75: event TRUE, Brier 0.0625" in txt, "aligned: P2 TRUE")
                    check("event TRUE, Brier 0.0100" in txt, "aligned: P3 TRUE (best depth 1 < 3 on both)")
                else:
                    check([R["corpora"][c]["gr1"] for c in CORPORA] == ["NEITHER", "NEITHER"] and R["GR1"] == "MIXED"
                          and "MASSIVE NEITHER, CLINC NEITHER -> GR1 MIXED" in txt, "scrambled: NEITHER on both reads GR1 MIXED")
                    check(R["GR2"] == "FAILED" and "F-GR FIRES" in txt and "GR2 HELD is REFUTED: DP(tree) <= the random p97.5 on massive, clinc" in txt,
                          "scrambled: GR2 FAILED, F-GR fires, FAILS line names both")
                    check("P2 GR2 HELD 0.75: event FALSE, Brier 0.5625" in txt, "scrambled: P2 FALSE")
                hw = gr2_overall(*[bool(_indep_expected(fx, c, n)["hf_tree"] > R["corpora"][c]["hf"]["rnd_p975"]) for c, n in ARMS_USED.items()])
                check(R["HF2"] == hw and ("-> HF2 %s" % hw) in txt, "HF2 overall %s == the independent words (%s)" % (R["HF2"], hw))
                check("HF P3 (MMLU-Pro recovery, DESCRIPTIVE): NOT EVALUATED" in txt, "HF P3 printed NOT EVALUATED")
                check(("-> GR1 %s" % R["GR1"]) in txt and R["GR1"] == gr1_overall(R["corpora"]["massive"]["gr1"], R["corpora"]["clinc"]["gr1"]), "GR1 overall printed")
                check("TRAIN-ONLY fit audit: M-AF TRAIN" in txt and "sides TRAIN;" in txt and "EVAL" not in txt.split("TRAIN-ONLY fit audit:")[1].split("\n")[0],
                      "the fit audit lists TRAIN only")
                # write-once: the second run refuses before any read
                refused(lambda: run(data_root=fx["root"], pins_file=fx["pins"], out_dir=od, boot_b=10, n_random=5, skip_heavy=True, out=lambda s: None),
                        "write-once")
            # dry-run: nothing written, k_d printed, no EVAL
            od = os.path.join(td, "dry")
            buf = []
            S1.STATE["gate_frozen"] = False
            with contextlib.redirect_stdout(io.StringIO()):
                dry_run(data_root=fa["root"], pins_file=fa["pins"], out=buf.append, skip_heavy=True)
            txt = "\n".join(buf)
            e = _indep_expected(fa, "massive", "M-AF")
            check(("k_d %s" % e["ks"]) in txt and "DRY RUN complete: no EVAL row read; 0 files written" in txt, "dry-run prints k_d and writes nothing")
            check(not os.path.exists(od) and S1.STATE["gate_frozen"] is False, "dry-run: no output dir, EVAL never unlocked")
        if "ST-REFUSE" in sel:
            od = os.path.join(td, "out_ref")
            kw = dict(pins_file=fa["pins"], out_dir=od, boot_b=10, n_random=5, skip_heavy=True, out=lambda s: None)
            # EVAL before the TRAIN phase is frozen
            S1.STATE["gate_frozen"] = False
            CS = fa["CS"]
            A = {"C": CS["massive"], "side": S1.arm_sides(CS["massive"], 1), "have": np.ones(len(CS["massive"].ids), dtype=bool)}
            refused(lambda: S1.eval_rows(A), "GATE-before-EVAL")
            # a fit on EVAL rows refuses (TRAIN-ONLY)
            evi = np.nonzero(CS["massive"].side == SS.EVAL)[0]
            refused(lambda: S1.fit_idx(CS["massive"], A["side"], evi, (SS.TRAIN,), "probe"), "TRAIN-ONLY")
            # census off by more than 5%
            REGISTERED_N["massive"] = (fa["census"]["massive"][0] * 2, fa["census"]["massive"][1])
            refused(lambda: run(data_root=fa["root"], **kw), "census off by more than 5%")
            REGISTERED_N["massive"] = fa["census"]["massive"]
            check(not os.path.exists(os.path.join(od, OUTCOME)), "a refused run writes nothing")
            # pin mismatch
            bad = os.path.join(td, "badpins.json")
            pj = json.load(open(fa["pins"]))
            pj["emb"]["qwen3"] = "0" * 64
            json.dump(pj, open(bad, "w"))
            refused(lambda: run(data_root=fa["root"], pins_file=bad, out_dir=od, boot_b=10, n_random=5, skip_heavy=True, out=lambda s: None), "sha256")
            # a null pin (strict)
            pj["emb"]["qwen3"] = None
            json.dump(pj, open(bad, "w"))
            refused(lambda: run(data_root=fa["root"], pins_file=bad, out_dir=od, boot_b=10, n_random=5, skip_heavy=True, out=lambda s: None), "UNPINNED")
            pj = json.load(open(fa["pins"]))
            pj["ingest_db"] = None
            json.dump(pj, open(bad, "w"))
            seen = []
            refused(lambda: run(data_root=fa["root"], pins_file=bad, out_dir=od, boot_b=10, n_random=5, skip_heavy=True, out=seen.append), "UNPINNED")
            check(not any("TRAIN phase" in x for x in seen), "a null pin refuses BEFORE any fit or statistic (strict at load)")
            # a file of record appearing during the run is never overwritten (mode x)
            odr = os.path.join(td, "out_race")

            def plant(line):
                if "TRAIN phase C-AF" in line:
                    os.makedirs(odr, exist_ok=True)
                    open(os.path.join(odr, OUTCOME), "w").write("PLANTED")
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    run(data_root=fa["root"], pins_file=fa["pins"], out_dir=odr, boot_b=10, n_random=5, skip_heavy=True, out=plant)
                raised = False
            except (FileExistsError, SystemExit):
                raised = True
            check(raised and open(os.path.join(odr, OUTCOME)).read() == "PLANTED", "an outcome planted mid-run is not overwritten (mode x)")
            # the embedding DB changing during the run refuses at the after-check; nothing written
            import shutil
            fb = os.path.join(td, "al_copy")
            shutil.copytree(fa["root"], fb)
            pj = json.load(open(fa["pins"]))
            json.dump(pj, open(os.path.join(fb, "pins.json"), "w"))
            odc = os.path.join(td, "out_change")

            def touch(line):
                if "TRAIN phase C-AF" in line:
                    open(os.path.join(fb, "intent_emb_qwen3.db"), "ab").write(b"x" * 512)
            refused(lambda: run(data_root=fb, pins_file=os.path.join(fb, "pins.json"), out_dir=odc, boot_b=10, n_random=5, skip_heavy=True, out=touch),
                    "sha256")
            check(not os.path.exists(os.path.join(odc, OUTCOME)), "a pin change during the run writes nothing")
            # an absent build
            rd = S1.run_dir("c_af", fa["root"])
            os.rename(os.path.join(rd, "headless_run.log"), os.path.join(rd, "headless_run.log.off"))
            refused(lambda: run(data_root=fa["root"], **kw), "builds ABSENT: C-AF")
            refused(lambda: dry_run(data_root=fa["root"], pins_file=fa["pins"], skip_heavy=True, out=lambda s: None), "builds ABSENT: C-AF")
            os.rename(os.path.join(rd, "headless_run.log.off"), os.path.join(rd, "headless_run.log"))
            # two Snapshot IDs in the log
            lp = os.path.join(rd, "headless_run.log")
            keep = open(lp).read()
            open(lp, "a").write("Snapshot ID: another_one\n")
            refused(lambda: run(data_root=fa["root"], **kw), "builds ABSENT: C-AF")
            open(lp, "w").write(keep)
            # the manifest's build counts differ from the re-derived build
            mp = os.path.join(rd, "diagnostics", "run_manifest.json")
            man = json.load(open(mp))
            man["intent_build"]["n_train"] += 1
            json.dump(man, open(mp, "w"))
            refused(lambda: run(data_root=fa["root"], **kw), "intent_build")
            man["intent_build"]["n_train"] -= 1
            json.dump(man, open(mp, "w"))
            # a non-empty snapshots.db-wal refuses
            open(fa["snap"] + "-wal", "wb").write(b"x")
            refused(lambda: run(data_root=fa["root"], **kw), "-wal")
            os.remove(fa["snap"] + "-wal")
            # the instrument pin
            PINNED_CODE["intent_transfer_s1.py"], keep_pin = "0" * 40, PINNED_CODE["intent_transfer_s1.py"]
            try:
                refused(lambda: run(data_root=fa["root"], **kw), "the instrument is imported unchanged")
            finally:
                PINNED_CODE["intent_transfer_s1.py"] = keep_pin
            check(not os.path.exists(os.path.join(od, OUTCOME)), "no refused run wrote the outcome")
    finally:
        REGISTERED_N.clear()
        REGISTERED_N.update(saved_n)
        S1.STATE["gate_frozen"] = False
        scratch_dir.rmtree_robust(td)
    if not quiet:
        print("%s SELFTEST OK: %d value checks (%s)" % (TAG, n_ok[0], ", ".join(c for c in SELFTEST_CASES if c in sel)))
    return 0


MUTANTS = (
    ("M01 best cut min instead of max", "    j = int(np.argmax(vals))\n", "    j = int(np.argmin(vals))\n", ("ST-AMI",)),
    ("M02 AMI without the EMI term", "    den = norm - emi\n", "    den = norm; emi = 0.0\n", ("ST-AMI",)),
    ("M03 AMI max normaliser", "    norm = (ht + hp) / 2.0\n", "    norm = max(ht, hp)\n", ("ST-AMI",)),
    ("M04 GR1 spread clause dropped (bar 0)", "    if D1 > spread_B and lo > 0:\n", "    if D1 > 0 and lo > 0:\n", ("ST-VERDICT",)),
    ("M05 GR1 interval clause dropped", "    if D1 > spread_B and lo > 0:\n", "    if D1 > spread_B:\n", ("ST-VERDICT",)),
    ("M06 GR1 >= spread (boundary)", "    if D1 > spread_B and lo > 0:\n", "    if D1 >= spread_B and lo > 0:\n", ("ST-VERDICT",)),
    ("M07 GR1 AVG interval clause dropped", "    if D1 < -spread_B and hi < 0:\n", "    if D1 < -spread_B:\n", ("ST-VERDICT",)),
    ("M08 GR1 overall TREE on either corpus", "    if wm == \"TREE-BETTER\" and wc == \"TREE-BETTER\":\n", "    if wm == \"TREE-BETTER\" or wc == \"TREE-BETTER\":\n", ("ST-VERDICT",)),
    ("M09 GR1 overall NEITHER-both reads NEITHER", "    return \"MIXED\"\n\n\ndef gr2_corpus", "    return \"NEITHER\" if wm == wc == \"NEITHER\" else \"MIXED\"\n\n\ndef gr2_corpus", ("ST-VERDICT",)),
    ("M10 GR2 p95 instead of p97.5", "Q_RANDOM = 97.5\n", "Q_RANDOM = 95.0\n", ("ST-E2E",)),
    ("M11 GR2 >= instead of >", "    return bool(dp > p975)\n", "    return bool(dp >= p975)\n", ("ST-VERDICT",)),
    ("M12 GR2 HELD on either corpus", "    if am and ac:\n        return \"HELD\"\n", "    if am or ac:\n        return \"HELD\"\n", ("ST-VERDICT",)),
    ("M13 GR2 FAILED unless both", "    if not am and not ac:\n        return \"FAILED\"\n", "    if not am or not ac:\n        return \"FAILED\"\n", ("ST-VERDICT",)),
    ("M14 random trees: no permutation", "        perm = rng.permutation(len(leaves))\n", "        perm = np.arange(len(leaves)); rng.permutation(len(leaves))\n", ("ST-E2E",)),
    ("M15 random trees: random binary (shape not matched)",
     "    rnd = random_shape_dps(tp, T[\"leaves\"], leaf_ids, cls, n_random, seed_random)\n",
     "    _rg = np.random.default_rng(seed_random); rnd = [S1.dendrogram_purity(S1.random_parent(T[\"leaves\"], _rg), T[\"leaves\"], leaf_ids, cls) for _ in range(n_random)]\n", ("ST-E2E",)),
    ("M16 spread_B over seeds 0-3", "    v = [best_by_seed[s] for s in SEEDS_B]\n", "    v = [best_by_seed[s] for s in SEEDS_B[:4]]\n", ("ST-VERDICT", "ST-E2E")),
    ("M16b spread_B from one seed pair (0, 1)", "    return float(max(v) - min(v))\n", "    return float(abs(v[1] - v[0]))\n", ("ST-VERDICT", "ST-E2E")),
    ("M17 D1 against bisecting seed 0", "    r[\"D1\"] = r[\"tree_c\"] - r[\"avg_c\"]\n", "    r[\"D1\"] = r[\"tree_c\"] - r[\"bis_c\"][0]\n", ("ST-E2E",)),
    ("M18 EVAL statistic on TRAIN rows", "    ev = S1.eval_rows(A)\n", "    ev = P[\"tr\"]\n", ("ST-E2E",)),
    ("M19 average-link fitted on TRAIN + EVAL",
     "    tr = S1.fit_idx(C, A[\"side\"], S1.side_rows(C, A[\"side\"], A[\"have\"], SS.TRAIN), (SS.TRAIN,), \"%s TRAIN\" % A[\"name\"])\n",
     "    tr = S1.fit_idx(C, A[\"side\"], np.nonzero(C.kept & ~C.oos & A[\"have\"] & (A[\"side\"] != SS.GATE))[0], (SS.TRAIN,), \"%s TRAIN\" % A[\"name\"])\n", ("ST-E2E",)),
    ("M20 tree cuts drop the leaf depth", "    for d in range(1, dmax + 1):\n        node = ", "    for d in range(1, dmax):\n        node = ", ("ST-HIER",)),
    ("M21 shallow leaf mapped to its parent", "        node = [ch[dep - d] if dep >= d else ch[0] for ch, dep in zip(chains, depth)]\n",
     "        node = [ch[dep - d] if dep >= d else ch[min(1, len(ch) - 1)] for ch, dep in zip(chains, depth)]\n", ("ST-HIER",)),
    ("M22 frontier expands fine first", "    for node in H[\"order\"][:k - 1]:\n", "    for node in H[\"order\"][::-1][:k - 1]:\n", ("ST-HIER",)),
    ("M23 bootstrap weights ignored", "    def d1(w):\n        return best_cut(tc, tree_labs, w)[0] - best_cut(tc, labs[\"avg\"], w)[0]\n",
     "    def d1(w):\n        return best_cut(tc, tree_labs)[0] - best_cut(tc, labs[\"avg\"])[0]\n", ("ST-E2E",)),
    ("M24 GR1 scored on the fine level", "    r[\"D1\"] = r[\"tree_c\"] - r[\"avg_c\"]\n", "    r[\"D1\"] = r[\"tree_f\"] - r[\"avg_f\"]\n", ("ST-E2E",)),
    ("M25 DP against the fine level", "    cls = C.coarse[ev].tolist()\n", "    cls = C.fine[ev].tolist()\n", ("ST-E2E",)),
    ("M26 P1 band exclusive", "lo <= x <= hi) else \"FAILED\"", "lo < x < hi) else \"FAILED\"", ("ST-VERDICT",)),
    ("M27 P2 event = GR2 FAILED", "    ev2 = R[\"GR2\"] == \"HELD\"\n", "    ev2 = R[\"GR2\"] == \"FAILED\"\n", ("ST-RENDER",)),
    ("M28 P3 event <= D_max", "    ev3 = bool(m[\"best_depth_c\"] < m[\"dmax\"] and k[\"best_depth_c\"] < k[\"dmax\"])\n",
     "    ev3 = bool(m[\"best_depth_c\"] <= m[\"dmax\"] and k[\"best_depth_c\"] <= k[\"dmax\"])\n", ("ST-RENDER",)),
    ("M29 F-GR fires on MIXED", "    if R[\"GR2\"] == \"FAILED\":\n", "    if R[\"GR2\"] != \"HELD\":\n", ("ST-RENDER",)),
    ("M30 FAILS (rule 8) line dropped", "        a(\"%s FAILS (rule 8): GR2 HELD is REFUTED: DP(tree) <= the random p97.5 on %s\" % (TAG, \", \".join(refuted)))\n",
     "        pass\n", ("ST-RENDER",)),
    ("M31 not write-once (mode w)", "    with open(path, \"x\", encoding=\"utf-8\", newline=\"\\n\") as fh:\n        fh.write(\"\\n\".join(lines)",
     "    with open(path, \"w\", encoding=\"utf-8\", newline=\"\\n\") as fh:\n        fh.write(\"\\n\".join(lines)", ("ST-E2E", "ST-REFUSE")),
    ("M32 write-once pre-check removed", "        if os.path.lexists(p):\n            refuse(\"%s exists: the outcome is write-once\" % p)\n",
     "        if False:\n            refuse(\"%s exists: the outcome is write-once\" % p)\n", ("ST-E2E",)),
    ("M33 census check removed", "    if bad:\n        refuse(\"census off by more than 5%%: %s (re-state by bracket before any read)\" % \"; \".join(bad))\n",
     "    if False:\n        refuse(\"census off by more than 5%%: %s (re-state by bracket before any read)\" % \"; \".join(bad))\n", ("ST-REFUSE",)),
    ("M34 absent build admitted", "    if absent:\n        refuse(\"builds ABSENT: %s (the readout reads only complete builds)\" % \", \".join(absent))\n",
     "    if False:\n        refuse(\"builds ABSENT: %s (the readout reads only complete builds)\" % \", \".join(absent))\n", ("ST-REFUSE",)),
    ("M35 pins not strict", "    pins = {\"ingest\": S0.pin_check(db, \"ingest_db\", True,", "    pins = {\"ingest\": S0.pin_check(db, \"ingest_db\", False,", ("ST-REFUSE",)),
    ("M36 instrument pin not checked", "        if got != want:\n            refuse(\"%s blob %s != the pinned %s (the instrument is imported unchanged)\"",
     "        if False:\n            refuse(\"%s blob %s != the pinned %s (the instrument is imported unchanged)\"", ("ST-REFUSE",)),
    ("M37 MDE80 at 1.96 SE", "    r[\"mde\"] = 2.8 * r[\"se\"]\n", "    r[\"mde\"] = 1.96 * r[\"se\"]\n", ("ST-E2E",)),
    ("M38 n_eff from components", "    r[\"neff\"] = r[\"n\"] / r[\"kish\"]\n", "    r[\"neff\"] = r[\"G\"] / r[\"kish\"]\n", ("ST-E2E",)),
    ("M39 bisecting splits the largest cluster by size", "        top = max(inert[c] for c in cand)\n        c = min(x for x in cand if inert[x] == top)\n",
     "        top = max(len(idx[c]) for c in cand)\n        c = min(x for x in cand if len(idx[x]) == top)\n", ("ST-HIER",)),
    ("M40 average-link filed by nearest TRAIN leaf at k (not lifted)", "        labs[name] = [frontier_cut(H, k)[lf] for k in ks]\n",
     "        labs[name] = [frontier_cut(H, min(k + 1, len(H[\"leaves\"])))[lf] for k in ks]\n", ("ST-E2E",)),
    ("M41 MIXED sentence printed for AVG-BETTER", "    elif R[\"GR1\"] == \"AVG-BETTER\":\n", "    elif False:\n", ("ST-RENDER",)),
    ("M43 root cut (depth 1) dropped", "    for d in range(1, dmax + 1):\n        node = ", "    for d in range(2, dmax + 1):\n        node = ", ("ST-HIER",)),
    ("M44 best cut = the first cut only", "    vals = [ami(truth, lab, w) for lab in labelings]\n", "    vals = [ami(truth, lab, w) for lab in labelings[:1]]\n", ("ST-AMI",)),
    ("M45 pin after-check removed", "    S0.pin_check(Ld[\"emb\"], \"emb\", True, sub=\"qwen3\", pins_file=pins_file, label=\"intent_emb_qwen3.db (after)\")\n", "", ("ST-REFUSE",)),
    ("M46 every EVAL item filed to one leaf", "    fl = S1.flat_leaf(T, Xev)\n", "    fl = S1.flat_leaf(T, Xev) * 0\n", ("ST-E2E",)),
    # HIER-F
    ("H01 HF over leaves only", "    N = Am.astype(np.float64) @ M\n", "    N = (Am & (Am.sum(1) == 1)[:, None]).astype(np.float64) @ M\n", ("ST-HF",)),
    ("H02 HF unweighted class mean", "    return (float((nc / n * best).sum()) if n > 0", "    return (float(best[nc > 0].mean()) if n > 0", ("ST-HF",)),
    ("H03 HF precision only", "        F = np.where(N > 0, 2.0 * N / (nv[:, None] + nc[None, :]), 0.0)\n", "        F = np.where(N > 0, N / nv[:, None], 0.0)\n", ("ST-HF",)),
    ("H04 HF1 / HF2 on the coarse gold", "    h[\"hf_tree\"], h[\"hf_avg\"] = a[\"tree\"][\"hf_f\"], a[\"avg\"][\"hf_f\"]\n",
     "    h[\"hf_tree\"], h[\"hf_avg\"] = a[\"tree\"][\"hf_c\"], a[\"avg\"][\"hf_c\"]\n", ("ST-E2E",)),
    ("H05 HF D against bisecting seed 0", "    h[\"D\"] = h[\"hf_tree\"] - h[\"hf_avg\"]\n", "    h[\"D\"] = h[\"hf_tree\"] - h[\"bis_hf\"][0]\n", ("ST-E2E",)),
    ("H06 HF spread_B dropped (bar 0)", "    h[\"spread_B\"] = spread_b(h[\"bis_hf\"])\n", "    h[\"spread_B\"] = 0.0\n", ("ST-E2E",)),
    ("H07 HF bootstrap weights ignored", "        return hier_f(At, lt, gf, Kf, w)[0] - hier_f(Aa, la, gf, Kf, w)[0]\n",
     "        return hier_f(At, lt, gf, Kf)[0] - hier_f(Aa, la, gf, Kf)[0]\n", ("ST-E2E",)),
    ("H08 HF random trees: no permutation", "        out.append(hier_f(Am, perm[np.asarray(leaf_idx)], gold, K)[0])\n",
     "        out.append(hier_f(Am, np.asarray(leaf_idx), gold, K)[0])\n", ("ST-HF", "ST-E2E")),
    ("H09 HF2 reads GR2's words", "    R[\"HF2\"] = gr2_overall(m[\"hf\"][\"hf2_above\"], k[\"hf\"][\"hf2_above\"])\n    R[\"boot_b\"]",
     "    R[\"HF2\"] = gr2_overall(m[\"gr2_above\"], k[\"gr2_above\"])\n    R[\"boot_b\"]", ("ST-E2E",)),
    ("H10 F-HF fires on MIXED", "    if R[\"HF2\"] == \"FAILED\":\n", "    if R[\"HF2\"] != \"HELD\":\n", ("ST-RENDER",)),
    ("H11 HF FAILS line dropped", "        a(\"%s FAILS (rule 8): HF2 HELD is REFUTED: HF(tree) <= the random p97.5 on %s\" % (TAG, \", \".join(refuted)))\n",
     "        pass\n", ("ST-RENDER",)),
    ("H12 HF P1 Brier on TREE-BETTER", "            brier(HF_P1_NEITHER, h[\"hf1\"] == \"NEITHER\")))\n", "            brier(HF_P1_NEITHER, h[\"hf1\"] == \"TREE-BETTER\")))\n", ("ST-RENDER",)),
    ("H13 HF P2 event = HF2 FAILED", "    ev2 = R[\"HF2\"] == \"HELD\"\n", "    ev2 = R[\"HF2\"] == \"FAILED\"\n", ("ST-RENDER",)),
    ("H14 taxonomic P / R swapped", "    return P, R, F\n", "    return R, P, F\n", ("ST-HF",)),
    ("H15 taxonomic labels include the root", "            if v != ri and has[v]:\n", "            if has[v]:\n", ("ST-HF",)),
    ("H16 ancestor-F1 strict ancestor (self excluded)", "            if bool(np.all(a >= b)):\n", "            if bool(np.all(a >= b)) and not np.array_equal(a, b):\n", ("ST-HF",)),
    ("H17 FM arithmetic mean denominator", "    return float(tp / np.sqrt(pa * pb)) if pa > 0", "    return float(tp / ((pa + pb) / 2)) if pa > 0", ("ST-HF",)),
    ("H18 HF random draws not GR2's stream", "    rng = np.random.default_rng(seed)\n    L = Am.shape[1]\n", "    rng = np.random.default_rng(seed + 1)\n    L = Am.shape[1]\n", ("ST-HF", "ST-E2E")),
    ("H19 HF1 interval clause dropped (HF path)", "    h[\"hf1\"] = gr1_corpus(h[\"D\"], h[\"lo\"], h[\"hi\"], h[\"spread_B\"])\n",
     "    h[\"hf1\"] = gr1_corpus(h[\"D\"], -1.0, 1.0, h[\"spread_B\"])\n", ("ST-E2E",)),
    ("H20 HF2 p97.5 replaced by the median", "    p = float(np.percentile(rnd, Q_RANDOM)) if len(rnd)", "    p = float(np.percentile(rnd, 50.0)) if len(rnd)", ("ST-VERDICT", "ST-E2E")),
    ("H21 HF2 compares >= (not strict)", "    return p, gr2_corpus(x, p)\n", "    return p, bool(x >= p)\n", ("ST-VERDICT", "ST-E2E")),
    ("H22 HF2 path bypasses above_random (p97.5 of nothing)", "    h[\"rnd_p975\"], h[\"hf2_above\"] = above_random(h[\"hf_tree\"], rnd)\n",
     "    h[\"rnd_p975\"], h[\"hf2_above\"] = above_random(h[\"hf_tree\"], rnd[:1])\n", ("ST-E2E",)),
    ("M42 P1 probability clause scored as NEITHER-on-either", "    a(\"%s P1 'GR1 NEITHER 0.6': NOT SCORED",
     "    a(\"%s P1 'GR1 NEITHER 0.6': Brier %.4f\" % (TAG, brier(0.6, m[\"gr1\"] == \"NEITHER\" or k[\"gr1\"] == \"NEITHER\")))\n    a(\"%s P1 'GR1 NEITHER 0.6': NOT SCORED", ("ST-RENDER",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read().replace("\r\n", "\n")
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    killed = 0
    rows = []
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "gran_gt_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(head.replace(old, new), "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        finally:
            S1.STATE["gate_frozen"] = False
        killed += res.startswith("KILLED")
        rows.append((name, res))
        print("  %-58s %s" % (name, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="GRANULARITY-GT readout (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root", default=None, help="the root holding the S1 builds, snapshots.db and the S1 DBs (default TAXOARENA_DATA_ROOT or this checkout)")
    ap.add_argument("--pins-file", default=None, help="default experiment_configs/intent_transfer_s0_pins.json of this checkout")
    ap.add_argument("--snapshot-db", default=None)
    ap.add_argument("--out-dir", default=None, help="default E:/TaxoArena_backup_<date>_granularity_gt")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(data_root=a.data_root, pins_file=a.pins_file, snap_db=a.snapshot_db)
    run(data_root=a.data_root, pins_file=a.pins_file, snap_db=a.snapshot_db, out_dir=a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
