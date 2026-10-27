"""STABILITY-VS-KMEANS readout (docs/judge_v2_program.md, "## Registered 2026-10-05 (before any code or call) -- STABILITY-VS-KMEANS:
on the 2,772 common items of the four anchor-free MMLU-Pro re-draw trees, do the trees disagree with one another less (sampled
triplet distance) than matched-leaf-count hierarchical k-means baselines, fitted on the same re-draw member sets and
shape-matched, disagree with one another ...", L24625-L24637, registration commit 8e681387; the registrar's record L24618-L24623).
ZERO LLM calls; CPU only; labels never read; no EVAL item read.

POOL READER (rule 7): through site_support.load_all it reads the reserved_pool rows of p2dca21ab5f4ef3ae
(pool_guard.assert_pool_of_record, printed FIRST after the header), pd610c9ad05255f16, p19d9f473b5a610a0 and p8a29d8f3ff75aa55
(rows hashed to their ids), and embeddings_cache.db. Run it in a pool slot, never inside a construction or site-null window.
Three of the four draws are id-disjoint only (scope word).

LAUNCH SEQUENCE (zero calls; temp only under E: via scratch_dir; every DB is COPIED (db + -wal) into the process's scratch dir
before it is read: zc_common.stage_db):
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/stability_vs_kmeans.py --selftest   # fixtures, values asserted
  python tools/analysis/scratch_dir.py --run -- python tools/analysis/stability_vs_kmeans.py --mutants    # mutant table (sandbox copies)
  python tools/analysis/stability_vs_kmeans.py --dry-run   # pool line first, pins, staged copies, |C|, M_r, k_r, m_r, vectors,
                                                           # the IDENTITY CHECK, timing fits and the cost estimate; no D_b
  python tools/analysis/stability_vs_kmeans.py --run       # the readout of record; WRITE-ONCE outcome on E: (+ SHA256SUMS.txt)
      --out <path>      default E:/TaxoArena_backup_<date>_stability_vs_kmeans/stability_vs_kmeans_outcome.txt; REFUSES an
                        existing path (before any read); the outcome is NEVER committed (sha256-pin it, back it up)
      --data-root <dir> snapshots.db / mmlu_pro_dataset_cache_v2.db / embeddings_cache.db / site-null CSVs / intent_emb_qwen3.db
                        (default: the checkout holding this script)
      --s1-root <dir>   INTENT-TRANSFER-S1's build root (snapshots.db, intent_s1_build/, experiment_results/intent_transfer/s1/);
                        default <data-root>/.claude/worktrees/intent-s1-run

INPUTS (read-only; DBs through staged copies).
  * MMLU-Pro (deciding): site_support.load_all unchanged (pool guard, the four trees af_clean_s42, af_s137, af_s2048, af_s42_o1
    from snapshots.db, members verified on their pool's TRAIN side, site-null CSVs blob-checked). M_r = tree r's member set (the
    union of its leaves' queryIds; an item placed in several leaves counts once: SVK-R7); C = the intersection of the four M_r
    (SS-R1 of record, 2,772). Vectors: embeddings_cache.db (qwen3), the first 256 coordinates (the trees' sliceDim, read from the
    root vmfMu; 256 asserted) renormalised; a member without a vector REFUSES.
  * MASSIVE (DESCRIPTIVE ONLY): M-AF (slug m_af) and M-AF-s2 (slug m_af_s2) of INTENT-TRANSFER-S1: the snapshot named by the run
    log's single "Snapshot ID:", the build DB (intent_corpus.question / side ONLY; category / fine never selected), every member
    REFUSED unless it is a TRAIN row of its own build; vectors intent_emb_qwen3.db (sha256 must equal the registrar's pin in
    experiment_configs/intent_transfer_s0_pins.json emb.qwen3 AND both run manifests' embedding_cache_source_sha256), first 256
    coordinates renormalised. C_M = the intersection of the two member sets.

INSTRUMENT (registration, implemented as written).
  BASELINES per re-draw r on M_r at k_r = tree r's leaf count, seeds 0-4:
    BKM   bisecting spherical k-means: repeatedly split the LARGEST live cluster (member count; ties: earliest created) by
          spherical 2-means (intent_transfer_s0.skmeans(X_sub, 2, seed * 1000003 + t), t = splits done so far: SVK-R4) until
          k_r leaves; a split leaving one side empty marks the cluster unsplittable.
    KM-AL flat spherical k-means at k_r (intent_transfer_s0.skmeans, seed s) + average-link (cosine) on the used centroids:
          site_support.kmeans_hierarchies' construction (its full-binary C form is asserted equal to it at the identity check).
  SHAPE MATCH (deciding): restricted to C, each baseline keeps its leaf clusters and is collapsed to m_r = tree r's number of
    internal clusters on C (distinct (node & C) of non-leaf non-root nodes with 2 <= size < |C|, minus the leaf sets: SVK-R3)
    by contracting its lowest internal edges first (KM-AL: smallest merge heights, ties by merge index; BKM: latest bisections).
  TRIPLETS: numpy RandomState(20261004), 100,000 x rs.choice(|C|, 3, replace=False) on the sorted C list: the FIRST draw, the
    sample of site_support's "DESCRIPTIVE tree pairs on C" line (SVK-R1); topology ab|c, ac|b, bc|a, unresolved
    (site_support.triplet_topo); disagreement = share of triplets whose topology differs.
  D_b = mean over the 6 tree pairs of disagreement(tree r, tree r') - mean over the same 6 pairs and their 25 crossed seed pairs.
  INTERVAL: percentile bootstrap, B 2,000, numpy default_rng(20261005); per replicate, in this order: (i) 4 re-draws drawn with
    replacement (rng.integers), redrawn while < 2 distinct; shared by both arms (paired); a pair of two copies of one re-draw is
    dropped; (ii) for each baseline (BKM then KM-AL) and each re-draw r = 0..3, its 5 seeds resampled with replacement (seed
    counts; per re-draw, shared by its copies: SVK-R2); (iii) the 100,000 triplets resampled with replacement (counts). Bounds
    = np.percentile(.., [2.5, 97.5]). Beside: the four leave-one-re-draw-out values; a triplets-only bootstrap (descriptive,
    the "naive" interval) and the realised design effect (registered SD / triplets-only SD)^2.
  IDENTITY CHECK (REFUSES on mismatch, before any deciding number): the C-only full-binary KM-AL form at k 81 (seeds 0-4) on
    site_support's second triplet draw reproduces its outcome line (sha256 60d4cb39...): tree pairs mean 0.0684, k-means seed
    pairs mean 0.3243, and the six tree pairs on the first draw 0.0787 / 0.0883 / 0.1000 / 0.0481 / 0.0593 / 0.0357.

CRITERIA (registered; every branch printed and executed by the selftest).
  ST1 (DECIDING; the interval decides): MORE-STABLE iff the 95% upper bound of D_b < 0 for BOTH BKM and KM-AL; LESS-STABLE iff
    the 95% lower bound of D_b > 0 for at least one; NEITHER otherwise. FAILS (rule 8): MORE-STABLE refuted iff an upper bound
    >= 0 against either baseline.
  ST1 AS BRACKETED (READY_stability_vs_kmeans.md B-1, fix (a), the coordinator's relay of the registrar's bracket, 2026-10-05):
    MORE-STABLE additionally needs the 95% upper bound of D_b^RB < 0 for BOTH baselines, where D_b^RB is D_b with each pair's
    disagreement counted only over the triplets resolved in BOTH hierarchies of the pair (sum w (a != b, both resolved) /
    sum w (both resolved), on the same replicate's triplet weights, re-draws and seed counts: one bootstrap, three
    conventions). LESS-STABLE and NEITHER are as registered (on D_b); FAILS lists each refuting bound (D_b and D_b^RB). The
    trees leave 8-10% of triplets unresolved, the collapsed baselines almost none, and both-unresolved scores as agreement
    (about +0.07 in the trees' favour; SVK-R7's multi-leaf items are about half of it). Printed beside, DESCRIPTIVE: option (b),
    D_b with both-unresolved counted as agreement (= the registered D_b) and as disagreement (strict), with intervals; the
    unresolved share of every hierarchy (trees; baselines per re-draw, mean over seeds) and the both-unresolved shares.
  F-ST fires iff ST1 is not MORE-STABLE; LESS-STABLE adds its own sentence.
  P1 KM-AL baseline mean in [0.18, 0.40]; D_KM-AL in [-0.33, -0.10]. P2 BKM baseline mean in [0.10, 0.35]; D_BKM in
  [-0.28, -0.03]. P3 MORE 0.65 / NEITHER 0.30 / LESS 0.05, Brier over the three outcomes. P4 |KM-AL collapsed mean - full-binary
  mean| in [0.00, 0.05]. P5 MASSIVE tree disagreement in [0.03, 0.20]; D_KM-AL in [-0.30, 0.00]. Bands HELD iff the point lies
  in the closed interval.
SUPPORT (registered (a)-(g) quoted): 4 re-draws -> 6 pairs, DEFF 3.0 DECLARED, n_eff 2, SE 0.0333, MDE80 0.093, floor 0.049,
  SCOREABLE at the predictions. The readout prints beside the deciding statistic: the realised tree-pair SD, the baseline SDs
  over the 6 re-draw-pair means and over the 150 crossed values, SE = sqrt(sd_t^2/2 + sd_b^2/2), MDE80 = 2.80 x SE, the
  bootstrap SD (the SE reported), the triplets-only SD and the realised design effect.

BUILDER'S READINGS (printed; the registrar confirms or brackets BEFORE --run):
  SVK-R1 "site_support's sample of record on C ... the same index list" = the FIRST 100,000-triplet draw of RandomState(20261004)
         (the six per-pair values of the registration's Support (b) come from it); the identity check replays site_support's
         descriptive k-means line, which used the SECOND draw of the same stream (it is the line that printed 0.3243).
  SVK-R2 seeds are resampled per re-draw (all four, every replicate), shared by the copies of a re-draw in the multiset.
  SVK-R3 m_r as defined above (internal clusters of tree r on C, distinct, leaf sets excluded); a baseline with fewer distinct
         internal clusters on C than m_r keeps all of them (the shortfall printed).
  SVK-R4 BKM's split seed is seed * 1000003 + t (granularity_gt's convention); "largest" = member count.
  SVK-R5 MASSIVE vectors = intent_emb_qwen3.db (the S1 builds' embedding source, sha256 pinned); bootstrap beside with a fresh
         default_rng(20261005), seeds and triplets resampled, the one pair fixed ('conditional on the one pair').
  SVK-R6 the k-means k of the C-only forms = k_r (per re-draw); the identity form uses k 81 (the median leaf count).
  SVK-R7 a member set is the union of the leaves' queryIds (the trees place some items in several leaves).

EXTENSION SEAM (CONSTRUCTION-ARMS, not implemented): a baseline is an entry of BASELINES = {name: BaselineSpec(fit, contraction)}
  whose fit(X, k, seed) returns a Hier (leaf label per row, internal nodes as (leaf-index set, rank); rank ascending = contracted
  first). Bisecting arms take a pluggable split rule: fit_bisecting(X, k, seed, split=split_rule) with split_rule(X_sub, seed_int)
  -> labels in {0, 1} (spherical 2-means now; GMM-2 / Ward-2 / spherical-k plug in here). Flat+link arms supply their own fit.
  DECIDING fixes the registered pair (BKM, KM-AL); any added arm is DESCRIPTIVE until a registration names it. Nothing here
  changes when an arm is added: topologies, collapse, bootstrap and printing iterate over BASELINES.

SELFTEST (99 value-asserting checks, pinned): units on st1_decide (bounds at exactly 0, numpy scalars, one-vs-both, the RB
  conjunct alone), brier3,
  band, fit_bisecting (largest-first order, ranks), on_C (highest merges kept; planted super-groups kept at m = 2, independent of
  the rank code), the code pins; N, the planted crossed design (three identical trees + one outlier, constant baselines) where
  the triplets-only ("naive") interval reads MORE-STABLE and the registered paired, crossed interval reads NEITHER, with the
  point, the copy-pair drop and the crossed seed weighting checked by hand; three END-TO-END worlds through main(["--run"])
  (site_support's fixture world + embeddings + an S1 root for MASSIVE): E1 MORE-STABLE (identical trees, isotropic vectors;
  k_r 9/9/9/10), E2 LESS-STABLE (random trees, planted vectors), E3 NEITHER (three planted trees + one random: the point and the
  naive interval clear 0 on the positive side, the registered lower bound does not). Every D_b, interval and leave-one-out
  value is asserted against an INDEPENDENT reference (pure-set topologies, own collapse, own bootstrap loop on the same RNG
  stream; it shares only the registered fit functions); the identity values come from site_support's OWN descriptive_lines on
  the fixture. Also: ST1 / FAILS / F-ST / LESS sentence / P1-P5 / Support lines by value, write-once, the dry-run, and the
  refusals (identity: each of the three clauses alone; a MASSIVE member off TRAIN; the emb pin; a manifest's source sha; the
  slice).
SELFTEST MUTANTS (2026-10-05; `--mutants`: copies in a scratch sandbox with TMP/TEMP/TMPDIR inside it, the file never edited;
  a no-op control C0 must SURVIVE first, proving the sandbox selftest runs): 57 / 57 KILLED, C0 survived (after the B-1 / M-1
  fix; the RB fixture: trees jointly unresolved on 70% and random on the rest vs fully resolved baselines, where D_b clears 0
  and D_b^RB does not; E1 now carries a refined tree, m_r 2/2/4/2, so the reviewer's R5 dies).
  X1 MORE with ub <= 0; X2 MORE on one baseline; X3 LESS with lb >= 0; X4 LESS needs both; X5 re-draws not resampled; X6 seeds not
  resampled; X7 triplets not resampled; X8 copy pairs kept (crash); X9 seed draws shared by the baselines; X10 seeds paired, not
  crossed; X11 < 2 distinct re-draws not redrawn; X12 shape match off; X13 contraction reversed; X14 BKM keeps the latest
  bisections; X15 m_r counts leaf sets; X16 percentiles 5/95; X17 D sign flipped; X18 baselines fitted on C (crash); X19 one k
  for all re-draws; X20 bisect the smallest; X21 identity not refused; X22/X44/X45 an identity clause ignored; X23 F-ST FIRED
  unprinted; X24 LESS sentence unprinted; X25 FAILS unprinted; X26 write-once dropped; X27 binary Brier; X28 open bands; X29 LOO
  keeps all; X30 second triplet draw decides; X31 C_M = union (crash); X32 MASSIVE TRAIN check dropped; X33 emb pin unchecked; X34
  code pins unchecked; X35 first pair only; X36 no renormalisation; X37 slice check dropped; X38 P5 on BKM; X39 MASSIVE not
  shape-matched; X40 SE without the baseline term; X41 B 1000; X42 bootstrap seed + 1; X43 KM-AL ranks by merge index reversed;
  X46 manifest sha unchecked; X47 READY R5 (every re-draw collapsed to tree 0's m_r); X48 RB conjunct dropped; X49 RB on one
  baseline; X50 RB ub <= 0; X51 RB without the division; X52 RB denominator = resolved in either; X53 RB numerator with
  one-unresolved differences; X54 RB interval from the D_b replicates; X55 strict = registered; X56 unresolved share counts
  topology 0; X57 RB replicates on the point weights.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import collections
import datetime
import json
import re
import sqlite3
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import zc_common as ZC          # noqa: E402  (imports scratch_dir: temp on E:, removed at exit)
import scratch_dir              # noqa: E402
import cert_align_size as CA    # noqa: E402
import site_support as SS       # noqa: E402

import numpy as np              # noqa: E402

ROOT = ZC.ROOT
SRC = os.path.dirname(os.path.abspath(SS.__file__))   # the imported instruments' dir (== HERE except in a mutant sandbox)
TAG = "[STABILITY-VS-KMEANS]"
REG = "docs/judge_v2_program.md L24625-L24637 (registration commit 8e681387; registrar's record L24618-L24623)"
SEED_TRIP = 20261004
SEED_BOOT = 20261005
B_BOOT = 2000
TRIPLETS = 100_000
SEEDS = (0, 1, 2, 3, 4)
DIM = 256
PINNED_CODE = {"site_support.py": "4612345ce9c5fbc39bfaf9f520127ccf683e1591",
               "intent_transfer_s0.py": "f662ceb19738f515972871f5963f5dcfc764a271"}
IDENTITY = dict(k=81, tree_mean="0.0684", km_mean="0.3243",
                pairs=["0.0787", "0.0883", "0.1000", "0.0481", "0.0593", "0.0357"],
                source="E:/TaxoArena_backup_2026-10-04_site_support/site_support_outcome.txt sha256 60d4cb396f917be0")
DEFF = 3.0
Z80 = 2.80
SD_TREE_REG, SD_BASE_DECL, SE_REG, MDE_REG, FLOOR_REG = 0.0248, 0.040, 0.0333, 0.093, 0.049
P1_BASE, P1_D = (0.18, 0.40), (-0.33, -0.10)
P2_BASE, P2_D = (0.10, 0.35), (-0.28, -0.03)
P3_PROB = collections.OrderedDict([("MORE-STABLE", 0.65), ("NEITHER", 0.30), ("LESS-STABLE", 0.05)])
P4_BAND = (0.00, 0.05)
P5_TREE, P5_D = (0.03, 0.20), (-0.30, 0.00)
PRED_D = {"BKM": -0.15, "KM-AL": -0.22}
MASSIVE = [("M-AF", "m_af"), ("M-AF-s2", "m_af_s2")]
S1_REL = os.path.join(".claude", "worktrees", "intent-s1-run")
PINS_JSON = os.path.join("experiment_configs", "intent_transfer_s0_pins.json")
SELFTEST_CHECKS = 99


# ----------------------------------------------------------------------------------------------- hierarchies (the seam)
def split_spherical_2means(Xs, seed_int):
    """The registered BKM split rule: spherical 2-means (intent_transfer_s0.skmeans, unchanged); -> labels in {0, 1}."""
    import intent_transfer_s0 as ITS
    Cm = ITS.skmeans(Xs, 2, seed_int)
    return np.argmax(Xs @ Cm.T, axis=1)


def fit_bisecting(X, k, seed, split=split_spherical_2means):
    """BKM: split the LARGEST live cluster (count; ties: earliest created) until k leaves. -> Hier."""
    n = len(X)
    rows = {0: np.arange(n)}
    live, failed, kids, step = [0], set(), {}, {}
    nid = 1
    while len(live) < k:
        cand = [c for c in live if len(rows[c]) >= 2 and c not in failed]
        if not cand:
            break
        top = max(len(rows[c]) for c in cand)
        c = min(x for x in cand if len(rows[x]) == top)
        sub = rows[c]
        lab = split(X[sub], seed * 1000003 + len(step))
        if lab.min() == lab.max():
            failed.add(c)
            continue
        kids[c] = []
        for s in (0, 1):
            rows[nid] = sub[lab == s]
            kids[c].append(nid)
            nid += 1
        step[c] = len(step)
        live.remove(c)
        live.extend(kids[c])
    leaves = sorted(live)
    pos = {c: i for i, c in enumerate(leaves)}
    lab = np.empty(n, dtype=np.int64)
    for c in leaves:
        lab[rows[c]] = pos[c]

    def under(c):
        return [pos[c]] if c in pos else [x for ch in kids[c] for x in under(ch)]
    internal = [(frozenset(under(c)), (-step[c],)) for c in step if c != 0]
    return dict(lab=lab, L=len(leaves), internal=internal, kind="BKM")


def fit_kmal(X, k, seed):
    """KM-AL: spherical k-means at k + average-link (cosine) on the used centroids (kmeans_hierarchies' construction)."""
    import intent_transfer_s0 as ITS
    from scipy.cluster.hierarchy import linkage
    Cn = ITS.skmeans(X, k, seed)
    lab0 = np.argmax(X @ Cn.T, axis=1)
    used = sorted(set(lab0.tolist()))
    remap = {u: i for i, u in enumerate(used)}
    lab = np.array([remap[v] for v in lab0.tolist()], dtype=np.int64)
    internal = []
    if len(used) > 1:
        Z = linkage(Cn[used], method="average", metric="cosine")
        members = [frozenset([i]) for i in range(len(used))]
        for j, row in enumerate(Z):
            m = members[int(row[0])] | members[int(row[1])]
            members.append(m)
            if j < len(Z) - 1:
                internal.append((m, (float(row[2]), j)))
    return dict(lab=lab, L=len(used), internal=internal, kind="KM-AL")


BaselineSpec = collections.namedtuple("BaselineSpec", "name fit contraction")
BASELINES = collections.OrderedDict([
    ("BKM", BaselineSpec("BKM", fit_bisecting, "latest bisections contracted first")),
    ("KM-AL", BaselineSpec("KM-AL", fit_kmal, "smallest average-link merge heights contracted first")),
])
DECIDING = ("BKM", "KM-AL")


def on_C(h, cpos, C_list, m=None):
    """Hier h restricted to C (cpos: the fit row of each C item, C order): leaf clusters plus the m highest-ranked distinct
    internal clusters (all of them when m is None). -> (set of frozensets, kept, available)."""
    nC = len(C_list)
    lab_c = h["lab"][cpos]
    leafsets = {}
    for i, j in enumerate(lab_c.tolist()):
        leafsets.setdefault(j, set()).add(C_list[i])
    leafsets = {j: frozenset(s) for j, s in leafsets.items()}
    leaf_cl = {s for s in leafsets.values() if 2 <= len(s) < nC}
    seen, kept = set(), []
    for ls, _rank in sorted(h["internal"], key=lambda x: x[1], reverse=True):
        S = frozenset().union(*[leafsets.get(j, frozenset()) for j in ls])
        if 2 <= len(S) < nC and S not in leaf_cl and S not in seen:
            seen.add(S)
            if m is None or len(kept) < m:
                kept.append(S)
    return leaf_cl | set(kept), len(kept), len(seen)


def tree_internal_count(g, Cset):
    nC = len(Cset)
    leaves = [i for i, n in g["byid"].items() if not (n.get("childIds") or [])]
    leafsets = {frozenset(g["mem"][i] & Cset) for i in leaves}
    leafsets = {s for s in leafsets if 2 <= len(s) < nC}
    inner = {frozenset(g["mem"][i] & Cset) for i, n in g["byid"].items() if (n.get("childIds") or []) and i != g["root"]}
    return len({s for s in inner if 2 <= len(s) < nC} - leafsets)


def draw_triplets(n, count, rs):
    return np.array([rs.choice(n, 3, replace=False) for _ in range(count)]) if n >= 3 else np.zeros((0, 3), dtype=int)


def topo(cl, idx, trip):
    return SS.triplet_topo(sorted(cl, key=lambda c: sorted(c)), idx, trip).astype(np.int8)


def resolve_depth(cl, idx, trip, tp, chunk=20000):
    """Containment depth (1 + number of clusters strictly containing it) of the deepest cluster resolving each triplet; 0 if
    unresolved."""
    cl = sorted(cl, key=lambda c: sorted(c))
    out = np.zeros(len(trip), dtype=np.int16)
    if not cl:
        return out
    M = np.zeros((len(cl), len(idx)), dtype=bool)
    for r, c in enumerate(cl):
        for q in c:
            M[r, idx[q]] = True
    Mi = M.astype(np.int32)
    inter = Mi @ Mi.T
    size = M.sum(axis=1)
    cont = (inter == size[None, :]) & (size[:, None] > size[None, :])
    D = (1 + cont.sum(axis=0)).astype(np.int16)
    for s in range(0, len(trip), chunk):
        t = trip[s:s + chunk]
        a, b, c = M[:, t[:, 0]], M[:, t[:, 1]], M[:, t[:, 2]]
        tt = tp[s:s + chunk][None, :]
        P = np.where(tt == 0, a & b & ~c, np.where(tt == 1, a & c & ~b, np.where(tt == 2, b & c & ~a, False)))
        out[s:s + chunk] = np.max(np.where(P, D[:, None], 0), axis=0)
    return out


# ----------------------------------------------------------------------------------------------- bootstrap core
def pair_vectors(tt, bt, R, names):
    """tt: [R topologies]; bt: {b: [R][S] topologies}. -> (V float32, layout). V stacks three blocks of n rows (one row per
    hierarchy pair): NUM = differ AND resolved in both; DEN = resolved in both; BU = unresolved in both. The registered
    disagreement is NUM + (1 - DEN - BU) (a pair differs iff both resolved and different, or exactly one unresolved)."""
    pairs = [(r, q) for r in range(R) for q in range(r + 1, R)]
    lay = {"pairs": pairs, "T": {}, "B": {b: {} for b in names}}
    prs = []
    for (r, q) in pairs:
        lay["T"][(r, q)] = len(prs)
        prs.append((tt[r], tt[q]))
    for b in names:
        S = len(bt[b][0])
        for (r, q) in pairs:
            lay["B"][b][(r, q)] = len(prs)
            for s in range(S):
                for t in range(S):
                    prs.append((bt[b][r][s], bt[b][q][t]))
    lay["S"] = len(bt[names[0]][0]) if names else 0
    lay["n"] = len(prs)
    num = [(a != c) & (a != 3) & (c != 3) for a, c in prs]
    den = [(a != 3) & (c != 3) for a, c in prs]
    bu = [(a == 3) & (c == 3) for a, c in prs]
    return np.array(num + den + bu, dtype=np.float32), lay


def conventions(col, n):
    """col: one replicate's weighted means over V's 3n rows. -> per-pair vectors of the three conventions:
    'all' (registered: both-unresolved = agreement), 'rb' (resolved in both: NUM / DEN, bracket fix (a)), 'strict'
    (both-unresolved = disagreement, option (b))."""
    col = np.asarray(col, dtype=np.float64)
    num, den, bu = col[:n], col[n:2 * n], col[2 * n:3 * n]
    dis = num + (1.0 - den - bu)
    with np.errstate(invalid="ignore", divide="ignore"):
        rb = np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
    return {"all": dis, "rb": rb, "strict": num + (1.0 - den)}


CONVS = ("all", "rb", "strict")


def combine(dis, lay, pos, cnt, names):
    """One replicate's D_b from the pair disagreements dis (1-d, one value per pair row). pos: drawn re-draws; cnt[b][r]:
    seed counts."""
    S = lay["S"]
    P = [(pos[i], pos[j]) for i in range(len(pos)) for j in range(i + 1, len(pos)) if pos[i] != pos[j]]
    tree = float(np.mean([dis[lay["T"][(min(r, q), max(r, q))]] for r, q in P]))
    base = {}
    for b in names:
        vals = []
        for r, q in P:
            lo, hi = min(r, q), max(r, q)
            Mx = dis[lay["B"][b][(lo, hi)]: lay["B"][b][(lo, hi)] + S * S].reshape(S, S)
            if r > q:
                Mx = Mx.T
            vals.append(float(cnt[b][r] @ Mx @ cnt[b][q]) / float(S * S))
        base[b] = float(np.mean(vals))
    return tree, base, {b: tree - base[b] for b in names}


def bootstrap(V, lay, R, names, B, seed, resample_redraws=True, resample_seeds=True, resample_triplets=True, chunk=50,
              fixed_pos=None):
    """The registered paired, crossed bootstrap; every replicate scores the three conventions on the SAME weights, re-draws and
    seed counts. -> dict(point, reps {b: array}, tree_reps, base_reps) for 'all' (the registered D_b), plus conv[c] = dict(point,
    reps) for c in CONVS."""
    N = V.shape[1]
    n = lay["n"]
    S = lay["S"]
    ones = {b: [np.ones(S) for _ in range(R)] for b in names}
    pos0 = list(fixed_pos) if fixed_pos is not None else list(range(R))
    cv0 = conventions(V.mean(axis=1, dtype=np.float64), n)
    conv = {c: dict(point=combine(cv0[c], lay, pos0, ones, names), reps={b: [] for b in names}) for c in CONVS}
    rng = np.random.default_rng(seed)
    tree_reps, base_reps = [], {b: [] for b in names}
    done = 0
    while done < B:
        c = min(chunk, B - done)
        W = np.empty((N, c), dtype=np.float32)
        draws = []
        for j in range(c):
            if resample_redraws:
                pos = rng.integers(0, R, R).tolist()
                while len(set(pos)) < 2:
                    pos = rng.integers(0, R, R).tolist()
            else:
                pos = list(pos0)
            if resample_seeds:
                cnt = {b: [np.bincount(rng.integers(0, S, S), minlength=S).astype(np.float64) for _ in range(R)] for b in names}
            else:
                cnt = ones
            W[:, j] = np.bincount(rng.integers(0, N, N), minlength=N) if resample_triplets else 1.0
            draws.append((pos, cnt))
        M = (V @ W).astype(np.float64) / float(N)          # integer sums < 2^24: exact in float32, divided in float64
        for j, (pos, cnt) in enumerate(draws):
            cv = conventions(M[:, j], n)
            for cname in CONVS:
                t, bs, d = combine(cv[cname], lay, pos, cnt, names)
                for b in names:
                    conv[cname]["reps"][b].append(d[b])
                if cname == "all":
                    tree_reps.append(t)
                    for b in names:
                        base_reps[b].append(bs[b])
        done += c
    for cname in CONVS:
        conv[cname]["reps"] = {b: np.array(v) for b, v in conv[cname]["reps"].items()}
    return dict(point=conv["all"]["point"], reps=conv["all"]["reps"], tree_reps=np.array(tree_reps),
                base_reps={b: np.array(v) for b, v in base_reps.items()}, conv=conv)


def interval(x):
    lo, hi = np.percentile(x, [2.5, 97.5])
    return float(lo), float(hi)


def st1_decide(lo, hi, hi_rb):
    """ST1 as bracketed (fix (a), READY B-1): MORE-STABLE iff the upper bound < 0 for BOTH baselines on the all-triplets D_b AND
    on the resolved-in-both D_b^RB; LESS-STABLE iff the all-triplets lower bound > 0 for at least one; NEITHER otherwise."""
    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):
        return "MORE-STABLE"
    if any(bool(float(lo[b]) > 0) for b in DECIDING):
        return "LESS-STABLE"
    return "NEITHER"


def brier3(word):
    return sum((p - (1.0 if w == word else 0.0)) ** 2 for w, p in P3_PROB.items())


def band(x, bd):
    return "HELD" if ZC.in_band(x, bd) else "FAILED"


def f4(x):
    return "n/a" if x is None else "%+.4f" % x


# ----------------------------------------------------------------------------------------------- context, pins, loading
class Ctx(object):
    def __init__(self, data_root=ROOT, s1_root=None, B=B_BOOT, triplets=TRIPLETS, ss_ctx=None, identity=None, dim=DIM,
                 check_blobs=True, emb_pin=None, pins_json=None):
        self.data_root = data_root
        self.s1_root = s1_root or os.path.join(data_root, S1_REL)
        self.B, self.triplets, self.dim = B, triplets, dim
        self.ss = ss_ctx or SS.Ctx(data_root=data_root, triplets=triplets, kmeans=True)
        self.identity = identity or IDENTITY
        self.check_blobs = check_blobs
        self.emb_pin = emb_pin
        self.pins_json = pins_json or os.path.join(data_root, PINS_JSON)
        self.s1_staged = {}
        self.s1_dir = None

    def stage_abs(self, path, key):
        if key not in self.s1_staged:
            if self.s1_dir is None:
                self.s1_dir = scratch_dir.mkdtemp(prefix="svk_stage_")
            sub = os.path.join(self.s1_dir, "%02d" % len(self.s1_staged))
            self.s1_staged[key] = ZC.stage_db(path, sub, TAG)
        return self.s1_staged[key]


def check_code_pins(pinned=None):
    pinned = pinned or PINNED_CODE
    got = {}
    for name, want in sorted(pinned.items()):
        b = ZC.git_blob(os.path.join(SRC, name))
        got[name] = b
        if b != want:
            ZC.refuse(TAG, "%s is blob:%s, the instrument of record is blob:%s (imported unchanged)" % (name, b, want))
    return got


def header(ctx, out, mode):
    out.append("STABILITY-VS-KMEANS readout (%s); mode %s; %s; imports site_support blob:%s, intent_transfer_s0 blob:%s, zc_common "
               "blob:%s; date %s; ZERO calls" % (REG, mode, ZC.pins_line(os.path.abspath(__file__)),
                                                 ZC.git_blob(os.path.join(SRC, "site_support.py")),
                                                 ZC.git_blob(os.path.join(SRC, "intent_transfer_s0.py")),
                                                 ZC.git_blob(os.path.join(SRC, "zc_common.py")), datetime.date.today().isoformat()))


def unit_rows(V):
    V = np.asarray(V, dtype=np.float64)
    return V / np.linalg.norm(V, axis=1, keepdims=True)


def load_mmlu(ctx, out):
    T, C_list, _C_pool = SS.load_all(ctx.ss, out)
    trees = list(T)
    Cset = frozenset(C_list)
    g0 = T[trees[0]]["g"]
    dim = len(g0["byid"][g0["root"]].get("vmfMu") or []) or DIM
    if dim != ctx.dim:
        ZC.refuse(TAG, "the trees' slice is %d, the registered slice is %d" % (dim, ctx.dim))
    allm = frozenset().union(*[T[t]["root_mem"] for t in trees])
    emb = ctx.ss.stage("embeddings_cache.db")
    texts = SS.text_of_qid(ctx.ss, set(allm))
    vec = CA.load_vectors(ctx.ss, [texts[q] for q in allm if q in texts])
    miss = sorted(q for q in allm if q not in texts or texts[q] not in vec)
    if miss:
        ZC.refuse(TAG, "%d members have no vector in embeddings_cache.db (first %s): a baseline cannot place them" % (len(miss), miss[:3]))
    Xq = {q: np.asarray(vec[texts[q]][:dim], dtype=np.float64) for q in allm}
    W = dict(T=T, trees=trees, C=C_list, Cset=Cset, idx={q: j for j, q in enumerate(C_list)}, dim=dim, emb=emb, Xq=Xq)
    W["M"] = {t: sorted(T[t]["root_mem"]) for t in trees}
    W["X"] = {t: unit_rows([Xq[q] for q in W["M"][t]]) for t in trees}
    W["cpos"] = {}
    for t in trees:
        p = {q: i for i, q in enumerate(W["M"][t])}
        W["cpos"][t] = np.array([p[q] for q in C_list], dtype=np.int64)
    W["XC"] = unit_rows([Xq[q] for q in C_list])
    W["k"] = {t: T[t]["leaves"] for t in trees}
    W["m"] = {t: tree_internal_count(T[t]["g"], Cset) for t in trees}
    W["cl"] = {t: SS.clusters_on(T[t]["g"], Cset) for t in trees}
    out.append("DENOMINATOR: |C| = %d (SS-R1 of record: the intersection of the four member sets); vectors embeddings_cache.db sha256 %s, "
               "first %d coordinates renormalised; every member has a vector" % (len(C_list), emb["sha256"][:16], dim))
    out.append("  re-draws: %s" % "; ".join("%s |M_r| %d, k_r %d leaves, m_r %d internal clusters on C (of %d clusters on C)"
                                            % (t, len(W["M"][t]), W["k"][t], W["m"][t], len(W["cl"][t])) for t in trees))
    return W


def identity_check(ctx, W, out):
    """SITE-SUPPORT's descriptive line replayed: REFUSES on mismatch. Returns the deciding (first) triplet draw."""
    idn = ctx.identity
    C_list, idx, trees = W["C"], W["idx"], W["trees"]
    rs = np.random.RandomState(SEED_TRIP)
    trip = draw_triplets(len(C_list), ctx.triplets, rs)
    tv = draw_triplets(len(C_list), ctx.triplets, rs)
    pairs = [(a, b) for i, a in enumerate(trees) for b in trees[i + 1:]]
    tt1 = {t: topo(W["cl"][t], idx, trip) for t in trees}
    six = ["%.4f" % float(np.mean(tt1[a] != tt1[b])) for a, b in pairs]
    ttv = {t: topo(W["cl"][t], idx, tv) for t in trees}
    tree_mean = "%.4f" % float(np.mean([np.mean(ttv[a] != ttv[b]) for a, b in pairs]))
    km = SS.kmeans_hierarchies(ctx.ss, C_list, W["XC"], idn["k"])
    allpos = np.arange(len(C_list))
    for s, ref in zip(SEEDS, km):
        mine, _, _ = on_C(fit_kmal(W["XC"], idn["k"], s), allpos, C_list, None)
        if mine != ref:
            ZC.refuse(TAG, "KM-AL replay (seed %d) != site_support.kmeans_hierarchies: %d vs %d clusters" % (s, len(mine), len(ref)))
    kt = [topo(c, idx, tv) for c in km]
    km_mean = "%.4f" % float(np.mean([np.mean(kt[i] != kt[j]) for i in range(len(kt)) for j in range(i + 1, len(kt))]))
    ok = (tree_mean == idn["tree_mean"] and km_mean == idn["km_mean"] and six == list(idn["pairs"]))
    out.append("IDENTITY CHECK (refuse on mismatch; %s): C-only full-binary KM-AL at k %d, seeds 0-4 (cluster sets equal to "
               "site_support.kmeans_hierarchies), second draw: tree pairs mean %s (pinned %s), k-means seed pairs mean %s (pinned %s); "
               "six tree pairs on the first draw %s (pinned %s): %s"
               % (idn["source"], idn["k"], tree_mean, idn["tree_mean"], km_mean, idn["km_mean"], "/".join(six), "/".join(idn["pairs"]),
                  "OK" if ok else "MISMATCH"))
    if not ok:
        ZC.refuse(TAG, "IDENTITY CHECK failed: the instrument does not reproduce SITE-SUPPORT's descriptive line")
    return trip


# ----------------------------------------------------------------------------------------------- fits and topologies
def fit_set(X, k, names=None):
    names = names or list(BASELINES)
    return {b: [BASELINES[b].fit(X, k, s) for s in SEEDS] for b in names}


def topologies(W, F, trip):
    """Deciding (collapsed) and full-binary topologies per baseline / re-draw / seed; the trees'."""
    idx, C_list, trees = W["idx"], W["C"], W["trees"]
    tt = [topo(W["cl"][t], idx, trip) for t in trees]
    col, full, cls, info = {}, {}, {}, {}
    for b in BASELINES:
        col[b], full[b], cls[b] = [], [], []
        for t in trees:
            rc, rf, rcl = [], [], []
            for s_i, h in enumerate(F[t][b]):
                cl_c, kept, avail = on_C(h, W["cpos"][t], C_list, W["m"][t])
                cl_f, _, _ = on_C(h, W["cpos"][t], C_list, None)
                rc.append(topo(cl_c, idx, trip)); rf.append(topo(cl_f, idx, trip)); rcl.append(cl_c)
                info[(b, t, s_i)] = (h["L"], kept, avail)
            col[b].append(rc); full[b].append(rf); cls[b].append(rcl)
    return tt, col, full, cls, info


# ----------------------------------------------------------------------------------------------- MASSIVE
SID_RE = re.compile(r"Snapshot ID:\s*(\S+)")


class _SnapCtx(object):
    def __init__(self, p):
        self.p = p

    def path(self, rel):
        return self.p


def emb_pin(ctx):
    if ctx.emb_pin is not None:
        return ctx.emb_pin
    pins = json.load(open(ctx.pins_json, encoding="utf-8"))
    v = (pins.get("emb") or {}).get("qwen3")
    if not v:
        ZC.refuse(TAG, "%s carries no emb.qwen3 pin" % ctx.pins_json)
    return v


def load_massive(ctx, out):
    pin = emb_pin(ctx)
    snap = ctx.stage_abs(os.path.join(ctx.s1_root, "snapshots.db"), "s1_snapshots")
    embs = ctx.stage_abs(os.path.join(ctx.data_root, "intent_emb_qwen3.db"), "intent_emb_qwen3")
    if embs["sha256"] != pin:
        ZC.refuse(TAG, "intent_emb_qwen3.db sha256 %s != the registrar's pin %s" % (embs["sha256"], pin))
    G = {}
    for name, slug in MASSIVE:
        rd = os.path.join(ctx.s1_root, "experiment_results", "intent_transfer", "s1", slug, "seed_42")
        log = os.path.join(rd, "headless_run.log")
        if not os.path.isfile(log):
            ZC.refuse(TAG, "%s: %s absent" % (name, log))
        sids = sorted(set(SID_RE.findall(open(log, encoding="utf-8", errors="replace").read())))
        if len(sids) != 1:
            ZC.refuse(TAG, "%s: %d distinct Snapshot ID lines (exactly one required)" % (name, len(sids)))
        man = json.load(open(os.path.join(rd, "diagnostics", "run_manifest.json"), encoding="utf-8"))
        if (man.get("intent_build") or {}).get("arm") != name:
            ZC.refuse(TAG, "%s: run manifest intent_build.arm %r" % (name, (man.get("intent_build") or {}).get("arm")))
        if man.get("embedding_cache_source_sha256") != pin:
            ZC.refuse(TAG, "%s: the build's embedding source sha %s != the pin %s" % (name, man.get("embedding_cache_source_sha256"), pin))
        bd = ctx.stage_abs(os.path.join(ctx.s1_root, "intent_s1_build", "%s.db" % slug), "build_" + slug)
        con = ZC.open_ro(bd["path"], TAG)
        try:
            meta = dict(con.execute("SELECT key, value FROM intent_build_meta"))
            rows = con.execute("SELECT question, side FROM intent_corpus").fetchall()
        finally:
            con.close()
        if meta.get("arm") != name:
            ZC.refuse(TAG, "%s: build DB meta arm %r" % (name, meta.get("arm")))
        side = {CA.qid(t): (t, sd) for t, sd in rows}
        g = CA.load_graph(_SnapCtx(snap["path"]), sids[0])
        mem = g["mem"][g["root"]]
        bad = sorted(q for q in mem if q not in side or side[q][1] != "TRAIN")
        if bad:
            ZC.refuse(TAG, "%s: %d members are not TRAIN rows of %s.db (first %s): a split breach" % (name, len(bad), slug, bad[:3]))
        leaves = sum(1 for n in g["byid"].values() if not (n.get("childIds") or []))
        G[name] = dict(g=g, mem=mem, text={q: side[q][0] for q in mem}, sid=sids[0], leaves=leaves, build_sha=bd["sha256"])
    names = [n for n, _ in MASSIVE]
    C_M = sorted(frozenset.intersection(*[G[n]["mem"] for n in names]))
    want = {G[n]["text"][q] for n in names for q in G[n]["mem"]}
    con = ZC.open_ro(embs["path"], TAG)
    vec = {}
    try:
        for t, blob in con.execute("SELECT query, vector FROM embeddings"):
            if t in want:
                if len(blob) // 4 < ctx.dim:
                    ZC.refuse(TAG, "intent_emb_qwen3.db: a %d-d vector < the slice %d" % (len(blob) // 4, ctx.dim))
                vec[t] = np.frombuffer(blob, dtype=">f4", count=ctx.dim).astype(np.float64)
    finally:
        con.close()
    miss = len(want - set(vec))
    if miss:
        ZC.refuse(TAG, "intent_emb_qwen3.db: %d MASSIVE member texts have no vector" % miss)
    Cset = frozenset(C_M)
    MW = dict(names=names, G=G, C=C_M, Cset=Cset, idx={q: j for j, q in enumerate(C_M)}, emb=embs, snap=snap)
    MW["M"] = {n: sorted(G[n]["mem"]) for n in names}
    MW["X"] = {n: unit_rows([vec[G[n]["text"][q]] for q in MW["M"][n]]) for n in names}
    MW["cpos"] = {}
    for n in names:
        p = {q: i for i, q in enumerate(MW["M"][n])}
        MW["cpos"][n] = np.array([p[q] for q in C_M], dtype=np.int64)
    MW["k"] = {n: G[n]["leaves"] for n in names}
    MW["m"] = {n: tree_internal_count(G[n]["g"], Cset) for n in names}
    MW["cl"] = {n: SS.clusters_on(G[n]["g"], Cset) for n in names}
    out.append("MASSIVE (DESCRIPTIVE ONLY; one pair): s1 snapshots.db sha256 %s, intent_emb_qwen3.db sha256 %s (= the pin and both manifests); %s; "
               "|C_M| = %d (intersection of the two member sets)"
               % (snap["sha256"][:16], embs["sha256"][:16],
                  "; ".join("%s snapshot %s, |M| %d (all TRAIN rows of its build, sha256 %s), k %d leaves, m %d internal on C_M"
                            % (n, G[n]["sid"], len(G[n]["mem"]), G[n]["build_sha"][:16], MW["k"][n], MW["m"][n]) for n in names), len(C_M)))
    return MW


def massive_block(ctx, MW, out):
    names = MW["names"]
    rs = np.random.RandomState(SEED_TRIP)
    trip = draw_triplets(len(MW["C"]), ctx.triplets, rs)
    tt = [topo(MW["cl"][n], MW["idx"], trip) for n in names]
    bt = {b: [] for b in BASELINES}
    for n in names:
        F = fit_set(MW["X"][n], MW["k"][n])
        for b in BASELINES:
            bt[b].append([topo(on_C(h, MW["cpos"][n], MW["C"], MW["m"][n])[0], MW["idx"], trip) for h in F[b]])
    V, lay = pair_vectors(tt, bt, 2, list(BASELINES))
    bs = bootstrap(V, lay, 2, list(BASELINES), ctx.B, SEED_BOOT, resample_redraws=False)
    tree, base, D = bs["point"]
    rbp = bs["conv"]["rb"]["point"]
    lines = []
    for b in BASELINES:
        lo, hi = interval(bs["reps"][b])
        rlo, rhi = interval(bs["conv"]["rb"]["reps"][b])
        lines.append("%s baseline mean %.4f, D %s [%s, %s] (bootstrap SD %.4f), D_RB %s [%s, %s]" % (
            b, base[b], f4(D[b]), f4(lo), f4(hi), float(np.std(bs["reps"][b], ddof=1)), f4(rbp[2][b]), f4(rlo), f4(rhi)))
    lines.append("unresolved shares: trees %s; unresolved in both trees %.4f" % (
        "/".join("%.4f" % float(np.mean(x == 3)) for x in tt), float(np.mean((tt[0] == 3) & (tt[1] == 3)))))
    out.append("DESCRIPTIVE MASSIVE pair (conditional on the one pair; seeds and triplets resampled, B %d, default_rng(%d) fresh; no interval over re-draws): "
               "tree disagreement %.4f; %s" % (ctx.B, SEED_BOOT, tree, "; ".join(lines)))
    out.append("P5 (descriptive) MASSIVE tree disagreement %.4f in [0.03, 0.20]: %s; D_KM-AL %s in [-0.30, 0.00]: %s"
               % (tree, band(tree, P5_TREE), f4(D["KM-AL"]), band(D["KM-AL"], P5_D)))
    return dict(tree=tree, D=D, base=base)


# ----------------------------------------------------------------------------------------------- analysis
def mean_pair(tt):
    R = len(tt)
    return float(np.mean([np.mean(tt[r] != tt[q]) for r in range(R) for q in range(r + 1, R)]))


def crossed_values(bt_b, R):
    return [[float(np.mean(bt_b[r][s] != bt_b[q][t])) for s in range(len(bt_b[r])) for t in range(len(bt_b[q]))]
            for r in range(R) for q in range(r + 1, R)]


def resolved_both(a, b):
    m = (a != 3) & (b != 3)
    return float(np.mean(a[m] != b[m])) if m.any() else float("nan")


def depth_profile(pairs_ab):
    """pairs_ab: [(depth vector of A, disagreement vector)] -> 'bin: share (n)' over the pooled pairs."""
    acc = collections.OrderedDict((k, [0, 0]) for k in ("1", "2", "3", ">=4", "U"))
    for dep, dis in pairs_ab:
        keys = np.where(dep == 0, 4, np.minimum(dep, 4) - 1)
        for i, k in enumerate(acc):
            m = keys == i
            acc[k][0] += int(dis[m].sum()); acc[k][1] += int(m.sum())
    return ", ".join("%s %.4f (n %d)" % (k, (v[0] / v[1]) if v[1] else float("nan"), v[1]) for k, v in acc.items())


def analyse(ctx):
    out = []
    header(ctx, out, "--run")
    if ctx.check_blobs:
        check_code_pins()
    W = load_mmlu(ctx, out)
    trip = identity_check(ctx, W, out)
    out.append("BUILDER'S READINGS (the registrar confirms or brackets): SVK-R1 deciding triplets = the first RandomState(20261004) draw; "
               "SVK-R2 seeds resampled per re-draw; SVK-R3 m_r = distinct internal clusters on C, leaf sets excluded; SVK-R4 BKM split seed "
               "seed*1000003+t, largest = count; SVK-R5 MASSIVE vectors intent_emb_qwen3.db, bootstrap conditional on the pair; SVK-R6 C-only k = k_r; "
               "SVK-R7 member set = union of the leaves' queryIds")
    trees, R, names = W["trees"], len(W["trees"]), list(BASELINES)
    F = {t: fit_set(W["X"][t], W["k"][t]) for t in trees}
    tt, col, full, cls, info = topologies(W, F, trip)
    out.append("FITS (matched data M_r, matched leaf count k_r, seeds 0-4): %s" % "; ".join(
        "%s/%s leaves %s, internal kept/available on C %s (m_r %d)" % (
            b, t, ",".join(str(info[(b, t, s)][0]) for s in range(len(SEEDS))),
            ",".join("%d/%d" % info[(b, t, s)][1:] for s in range(len(SEEDS))), W["m"][t]) for b in names for t in trees))
    V, lay = pair_vectors(tt, col, R, names)
    bs = bootstrap(V, lay, R, names, ctx.B, SEED_BOOT)
    nv = bootstrap(V, lay, R, names, ctx.B, SEED_BOOT, resample_redraws=False, resample_seeds=False)
    tree_pt, base_pt, D_pt = bs["point"]
    lo, hi = {}, {}
    for b in names:
        lo[b], hi[b] = interval(bs["reps"][b])
    loo = {b: [] for b in names}
    for drop in range(R):
        keep = [r for r in range(R) if r != drop]
        ones = {b: [np.ones(lay["S"]) for _ in range(R)] for b in names}
        _t, _bs, d = combine(conventions(V.mean(axis=1, dtype=np.float64), lay["n"])["all"], lay, keep, ones, names)
        for b in names:
            loo[b].append(d[b])
    rbc, stc = bs["conv"]["rb"], bs["conv"]["strict"]
    tree_rb, base_rb, D_rb = rbc["point"]
    lo_rb, hi_rb = {}, {}
    for b in names:
        lo_rb[b], hi_rb[b] = interval(rbc["reps"][b])
    un_t = [float(np.mean(x == 3)) for x in tt]
    un_b = {b: [float(np.mean([np.mean(x == 3) for x in col[b][r]])) for r in range(R)] for b in names}
    bu_t = float(np.mean([np.mean((tt[r] == 3) & (tt[q] == 3)) for r in range(R) for q in range(r + 1, R)]))
    bu_b = {b: float(np.mean([np.mean((col[b][r][s] == 3) & (col[b][q][u] == 3)) for r in range(R) for q in range(r + 1, R)
                              for s in range(len(SEEDS)) for u in range(len(SEEDS))])) for b in names}
    out.append("UNRESOLVED SHARES (READY B-1; deciding triplets): trees %s; %s; unresolved in BOTH hierarchies of a pair: tree pairs mean %.4f, %s"
               % (", ".join("%s %.4f" % (t, u) for t, u in zip(trees, un_t)),
                  "; ".join("%s (mean over seeds, shape-matched) %s" % (b, ", ".join("%s %.4f" % (t, u) for t, u in zip(trees, un_b[b]))) for b in names),
                  bu_t, ", ".join("%s crossed pairs mean %.4f" % (b, bu_b[b]) for b in names)))
    # support as realised
    tpairs = [float(np.mean(tt[r] != tt[q])) for r in range(R) for q in range(r + 1, R)]
    sd_t = float(np.std(tpairs, ddof=1))
    out.append("SUPPORT AS REGISTERED (quoted, not re-derived): 4 re-draws -> 6 pairs (each re-draw in 3 pairs, Kish 3), 150 crossed seed pairs "
               "per baseline from 20 fits, %d triplets on %d items; DEFF 3.0 DECLARED; tree SD 0.0248 (SITE-SUPPORT), baseline SD 0.040 DECLARED; "
               "n_eff 2; SE 0.0333; MDE80 0.093; floor 0.049; SCOREABLE at the predictions" % (V.shape[1], len(W["C"])))
    for b in names:
        cv = crossed_values(col[b], R)
        sd_pm = float(np.std([np.mean(v) for v in cv], ddof=1))
        sd_150 = float(np.std([x for v in cv for x in v], ddof=1))
        se = (sd_t ** 2 / 2.0 + sd_150 ** 2 / 2.0) ** 0.5
        sd_boot = float(np.std(bs["reps"][b], ddof=1)); sd_naive = float(np.std(nv["reps"][b], ddof=1))
        deff = (sd_boot / sd_naive) ** 2 if sd_naive > 0 else float("nan")
        out.append("SUPPORT AS REALISED %s: tree-pair SD %.4f (6 pairs); baseline SD over the 6 re-draw-pair means %.4f, over the 150 crossed values %.4f; "
                   "SE = sqrt(%.4f^2/2 + %.4f^2/2) = %.4f; MDE80 = 2.80 x SE = %.4f (prediction %+.2f: %s); bootstrap SD of D (the SE reported) %.4f; "
                   "triplets-only SD %.4f; realised design effect (SD ratio)^2 %.2f; structural floor 2.80 x SD_tree/sqrt(2) = %.4f"
                   % (b, sd_t, sd_pm, sd_150, sd_t, sd_150, se, Z80 * se, PRED_D[b],
                      "beyond the MDE" if abs(PRED_D[b]) > Z80 * se else "inside the MDE", sd_boot, sd_naive, deff, Z80 * sd_t / 2 ** 0.5))
    for b in names:
        nlo, nhi = interval(nv["reps"][b])
        out.append("ST1 INPUT %s: tree mean %.4f (6 pairs); baseline mean %.4f (6 pairs x 25 crossed seed pairs, shape-matched); D_%s = %s; "
                   "95%% percentile interval [%s, %s] (B %d, default_rng(%d); re-draws paired, seeds crossed, triplets); bootstrap SD %.4f; "
                   "leave-one-re-draw-out %s; triplets-only interval [%s, %s] (descriptive, not deciding)"
                   % (b, tree_pt, base_pt[b], b, f4(D_pt[b]), f4(lo[b]), f4(hi[b]), ctx.B, SEED_BOOT, float(np.std(bs["reps"][b], ddof=1)),
                      "/".join(f4(x) for x in loo[b]), f4(nlo), f4(nhi)))
    for b in names:
        out.append("ST1-RB INPUT %s (bracket fix (a): per pair, disagreement among triplets resolved in BOTH hierarchies, on the same replicate's "
                   "weights, re-draws and seed counts): tree mean %.4f; baseline mean %.4f; D_RB_%s = %s; 95%% percentile interval [%s, %s]; bootstrap SD %.4f"
                   % (b, tree_rb, base_rb[b], b, f4(D_rb[b]), f4(lo_rb[b]), f4(hi_rb[b]), float(np.std(rbc["reps"][b], ddof=1))))
    for b in names:
        slo, shi = interval(stc["reps"][b])
        out.append("DESCRIPTIVE option (b) %s (not deciding): both-unresolved counted as agreement (the registered D) %s [%s, %s]; counted as "
                   "disagreement: tree mean %.4f, baseline mean %.4f, D %s [%s, %s]"
                   % (b, f4(D_pt[b]), f4(lo[b]), f4(hi[b]), stc["point"][0], stc["point"][1][b], f4(stc["point"][2][b]), f4(slo), f4(shi)))
    v = st1_decide(lo, hi, hi_rb)
    out.append("CRITERIA AND PREDICTIONS")
    detail = "; ".join("%s D %s [%s, %s], D_RB %s [%s, %s]" % (b, f4(D_pt[b]), f4(lo[b]), f4(hi[b]), f4(D_rb[b]), f4(lo_rb[b]), f4(hi_rb[b]))
                       for b in DECIDING)
    head = ("ST1 (DECIDING; MORE-STABLE iff the 95%% upper bound < 0 for BOTH BKM and KM-AL on D_b AND on D_b^RB (resolved in both; "
            "bracket fix (a)); LESS-STABLE iff a lower bound of D_b > 0): ")
    ref_all = [b for b in DECIDING if not bool(hi[b] < 0)]
    ref_rb = [b for b in DECIDING if not bool(hi_rb[b] < 0)]
    if v == "MORE-STABLE":
        out.append(head + "MORE-STABLE -- %s" % detail)
    elif v == "LESS-STABLE":
        out.append(head + "LESS-STABLE -- lower bound > 0 for %s; %s" % ("/".join(b for b in DECIDING if bool(lo[b] > 0)), detail))
    else:
        out.append(head + "NEITHER -- upper bound >= 0 for %s (D_b) and %s (D_b^RB), no lower bound > 0; %s"
                   % ("/".join(ref_all) or "none", "/".join(ref_rb) or "none", detail))
    refuted = ["%s (D_b)" % b for b in ref_all] + ["%s (D_b^RB)" % b for b in ref_rb]
    out.append("FAILS (rule 8): MORE-STABLE refuted at the planned n: %s" % (
        ("yes -- upper bound >= 0 against %s" % "/".join(refuted)) if refuted else "no"))
    if v == "MORE-STABLE":
        out.append("F-ST (fires iff ST1 is not MORE-STABLE): NOT FIRED")
    else:
        out.append("F-ST (fires iff ST1 is not MORE-STABLE): FIRED -- the re-draw trees are not shown more stable than generic hierarchies given "
                   "the same data perturbation, leaf count and shape; SITE-SUPPORT's 0.0684 vs 0.3243 is attributed to the unlike data and shape "
                   "of that comparison, not read as a tree property")
    if v == "LESS-STABLE":
        out.append("F-ST (LESS-STABLE): a bisecting or centroid-linkage hierarchy is the more reproducible object at this granularity")
    out.append("P1 KM-AL baseline mean %.4f in [0.18, 0.40]: %s; D_KM-AL %s in [-0.33, -0.10]: %s"
               % (base_pt["KM-AL"], band(base_pt["KM-AL"], P1_BASE), f4(D_pt["KM-AL"]), band(D_pt["KM-AL"], P1_D)))
    out.append("P2 BKM baseline mean %.4f in [0.10, 0.35]: %s; D_BKM %s in [-0.28, -0.03]: %s"
               % (base_pt["BKM"], band(base_pt["BKM"], P2_BASE), f4(D_pt["BKM"]), band(D_pt["BKM"], P2_D)))
    out.append("P3 ST1 predicted MORE-STABLE 0.65 / NEITHER 0.30 / LESS-STABLE 0.05; occurred %s; Brier (three outcomes) %.4f" % (v, brier3(v)))
    full_mean = {b: float(np.mean([x for vv in crossed_values(full[b], R) for x in vv])) for b in names}
    shift = abs(base_pt["KM-AL"] - full_mean["KM-AL"])
    out.append("P4 (descriptive) shape matching moves the KM-AL baseline mean by %.4f (collapsed %.4f vs full binary %.4f) in [0.00, 0.05]: %s"
               % (shift, base_pt["KM-AL"], full_mean["KM-AL"], band(shift, P4_BAND)))
    # descriptive
    Fc = {}
    for t in trees:
        k = W["k"][t]
        if k not in Fc:
            Fc[k] = fit_set(W["XC"], k)
    allpos = np.arange(len(W["C"]))
    conly = {b: [[topo(on_C(h, allpos, W["C"], None)[0], W["idx"], trip) for h in Fc[W["k"][t]][b]] for t in trees] for b in names}
    out.append("DESCRIPTIVE forms (points): %s" % "; ".join(
        "%s full-binary baseline mean %.4f (D %s), C-only binary baseline mean %.4f (D %s)"
        % (b, full_mean[b], f4(tree_pt - full_mean[b]), float(np.mean([x for vv in crossed_values(conly[b], R) for x in vv])),
           f4(tree_pt - float(np.mean([x for vv in crossed_values(conly[b], R) for x in vv])))) for b in names))
    rb_t = float(np.mean([resolved_both(tt[r], tt[q]) for r in range(R) for q in range(r + 1, R)]))
    rb_b = {b: float(np.mean([resolved_both(col[b][r][s], col[b][q][u]) for r in range(R) for q in range(r + 1, R)
                              for s in range(len(SEEDS)) for u in range(len(SEEDS))])) for b in names}
    rf_t = float(np.mean([SS.nrf(W["cl"][trees[r]], W["cl"][trees[q]]) for r in range(R) for q in range(r + 1, R)]))
    rf_b = {b: float(np.mean([SS.nrf(cls[b][r][s], cls[b][q][u]) for r in range(R) for q in range(r + 1, R)
                              for s in range(len(SEEDS)) for u in range(len(SEEDS))])) for b in names}
    out.append("DESCRIPTIVE resolved-in-both disagreement: trees %.4f; %s. Normalised RF (exact clusters on C): trees %.4f; %s"
               % (rb_t, "; ".join("%s %.4f" % (b, rb_b[b]) for b in names), rf_t, "; ".join("%s %.4f" % (b, rf_b[b]) for b in names)))
    dep_t = [resolve_depth(W["cl"][t], W["idx"], trip, tt[i]) for i, t in enumerate(trees)]
    prof_t = depth_profile([(dep_t[r], (tt[r] != tt[q]).astype(np.int64)) for r in range(R) for q in range(r + 1, R)])
    prof_b = {}
    for b in names:
        dep_b = [[resolve_depth(cls[b][r][s], W["idx"], trip, col[b][r][s]) for s in range(len(SEEDS))] for r in range(R)]
        prof_b[b] = depth_profile([(dep_b[r][s], (col[b][r][s] != col[b][q][u]).astype(np.int64)) for r in range(R) for q in range(r + 1, R)
                                   for s in range(len(SEEDS)) for u in range(len(SEEDS))])
    out.append("DESCRIPTIVE disagreement by depth of the resolving node in the first hierarchy of each pair (containment depth on C; U = unresolved): "
               "trees %s; %s" % (prof_t, "; ".join("%s %s" % (b, prof_b[b]) for b in names)))
    MW = load_massive(ctx, out)
    mres = massive_block(ctx, MW, out)
    out.append("WHAT THIS RESULT WILL NOT SHOW (registered): correctness (stability is not correctness); any EVAL, routing or filing quantity; the "
               "certificate's value (SITE-SUPPORT's F-SS untouched); content-closed re-draws (three are id-only); a population of re-draws beyond "
               "these four; other embedders; CLINC; a deciding MASSIVE result (one pair).")
    return out, dict(st1=v, D=D_pt, lo=lo, hi=hi, tree=tree_pt, base=base_pt, loo=loo, naive={b: interval(nv["reps"][b]) for b in names},
                     full=full_mean, massive=mres, W=W, trip=trip, tt=tt, col=col)


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


def dry_run(ctx):
    out = []
    header(ctx, out, "--dry-run")
    if ctx.check_blobs:
        check_code_pins()
    t0 = time.time()
    W = load_mmlu(ctx, out)
    t_load = time.time() - t0
    t0 = time.time()
    identity_check(ctx, W, out)
    t_id = time.time() - t0
    t0_ = W["trees"][0]
    tb = time.time(); fit_bisecting(W["X"][t0_], W["k"][t0_], 0); tb = time.time() - tb
    tk = time.time(); fit_kmal(W["X"][t0_], W["k"][t0_], 0); tk = time.time() - tk
    N = ctx.triplets
    Vs = (np.random.default_rng(0).random((3 * (6 + 2 * 150), N)) < 0.3).astype(np.float32)
    tbo = time.time()
    Wc = np.ones((N, 20), dtype=np.float32)
    _ = Vs @ Wc
    tbo = (time.time() - tbo) / 20.0
    t0 = time.time()
    MW = load_massive(ctx, out)
    t_m = time.time() - t0
    nM = float(np.mean([len(MW["M"][n]) for n in MW["names"]])); nR = float(np.mean([len(W["M"][t]) for t in W["trees"]]))
    fits = 20 * (tb + tk) + 20 * (tb + tk) * len(W["C"]) / nR + 10 * (tb + tk) * nM / nR
    topo_n = 4 + 40 * 2 + 40 + 2 + 20
    est = t_load + t_m + t_id + fits + topo_n * 0.5 + 3 * ctx.B * (tbo + 0.002)
    out.append("TIMING (this machine): staging + loading %.0f s (MMLU) + %.0f s (MASSIVE); identity check %.0f s; one BKM fit %.1f s, one KM-AL fit %.1f s "
               "on %s (|M| %d, k %d); bootstrap matmul %.3f s per replicate" % (t_load, t_m, t_id, tb, tk, t0_, len(W["M"][t0_]), W["k"][t0_], tbo))
    out.append("COST ESTIMATE --run: about %.0f min CPU (single thread), 0 calls; 40 matched fits + 40 C-only fits + 20 MASSIVE fits; about %d topologies on "
               "%d triplets; 2 x B %d MMLU bootstrap replicates (registered + triplets-only) + B %d MASSIVE; POOL READER for the whole run" % (est / 60.0, topo_n, N, ctx.B, ctx.B))
    out.append("--dry-run: no D_b printed, nothing written.")
    print("\n".join(out))
    return 0


# ----------------------------------------------------------------------------------------------- selftest fixtures
NC_FIX, PRIV, DIM_FIX = 120, 10, 24


def _planted_vectors(rng, kind):
    """kind 'planted': 8 subclusters of 15 (axes e10..e17, weight 1) in 4 pairs (e6..e9, weight 4) in two super-groups (A = subs
    0-3 on e0, B = subs 4-7 on e1, weight 10) + per-tree private clusters on e2..e5; 'iso': isotropic noise. Average-link heights
    separate: sub pairs ~0.009 < groups ~0.145 < super ~1."""
    X = np.zeros((NC_FIX + 4 * PRIV, DIM_FIX))
    if kind == "iso":
        return rng.standard_normal(X.shape)
    for j in range(NC_FIX):
        sub = j // 15
        v = np.zeros(DIM_FIX)
        v[0 if sub < 4 else 1] = 10.0
        v[6 + sub // 2] = 4.0
        v[10 + sub] = 1.0
        X[j] = v + 0.01 * rng.standard_normal(DIM_FIX)
    for t in range(4):
        for j in range(PRIV):
            v = np.zeros(DIM_FIX); v[2 + t] = 10.0
            X[NC_FIX + PRIV * t + j] = v + 0.01 * rng.standard_normal(DIM_FIX)
    return X


def _tree_spec(t, leaves, groups, split_private=False):
    """leaves: list of item lists on C; groups: list of leaf-index lists (internal nodes under the root); the tree's private
    docs form one more leaf under the root."""
    spec, nid = {}, [1]

    def new():
        nid[0] += 1
        return "n%08d" % nid[0]
    kids_root = []

    def node(grp, depth, cert):                                     # grp: a leaf index or a (nested) list of them
        if not isinstance(grp, list):
            lf = new()
            spec[lf] = dict(depth=depth, items=sorted(leaves[grp]))
            return lf
        g = new()
        spec[g] = dict(depth=depth, kids=[node(x, depth + 1, False) for x in grp], cert=cert)
        return g
    for gi, grp in enumerate(groups):
        kids_root.append(node(grp, 1, bool(gi == 0)))
    priv = list(range(NC_FIX + PRIV * t, NC_FIX + PRIV * (t + 1)))
    for part in ((priv[:PRIV // 2], priv[PRIV // 2:]) if split_private else (priv,)):
        pv = new()
        spec[pv] = dict(depth=1, items=part)
        kids_root.append(pv)
    spec["n00000001"] = dict(depth=0, kids=kids_root, cert=False)
    return spec


def _planted_tree(t, split_private=False, refine=False):
    """refine: group A carries two more internal nodes ({0, 1}, {2, 3}): m_r 4 instead of 2 (READY M-1)."""
    g = [[[0, 1], [2, 3]], [4, 5, 6, 7]] if refine else [[0, 1, 2, 3], [4, 5, 6, 7]]
    return _tree_spec(t, [list(range(15 * s, 15 * s + 15)) for s in range(8)], g, split_private)


def _random_tree(t, seed):
    rng = np.random.RandomState(seed)
    perm = rng.permutation(NC_FIX)
    return _tree_spec(t, [sorted(perm[15 * s:15 * s + 15].tolist()) for s in range(8)], [[0, 1, 2, 3], [4, 5, 6, 7]])


def _write_emb(path, universe, X, table="embeddings"):
    e = sqlite3.connect(path)
    e.execute("CREATE TABLE %s (query TEXT, vector BLOB)" % table)
    for t, v in zip(universe, X):
        e.execute("INSERT INTO %s VALUES (?,?)" % table, (t, struct.pack(">%df" % len(v), *[float(x) for x in v])))
    e.commit(); e.close()


def _fix_world(root, trees, X, triplets=3000, B=200, identity=None, massive_from=(0, 1)):
    """A complete fixture data root: site_support's world (snapshots.db, mmlu DB, pools, site nulls) with 16-d vmfMu, an
    embeddings_cache.db with X, and an S1 root (MASSIVE = two of the trees as builds) with intent_emb_qwen3.db."""
    universe = ["doc %d" % j for j in range(NC_FIX + 4 * PRIV)]
    pools = [list(range(NC_FIX + PRIV * ((t + 1) % 4), NC_FIX + PRIV * ((t + 1) % 4 + 1))) for t in range(4)]
    ssx = SS._world(root, trees, pools, universe)
    con = sqlite3.connect(os.path.join(root, "snapshots.db"))
    for sid, gj in con.execute("SELECT id, graph FROM snapshots").fetchall():
        g = json.loads(gj)
        for n in g["nodes"]:
            n["vmfMu"] = [1.0] + [0.0] * (DIM_FIX - 1)
        con.execute("UPDATE snapshots SET graph = ? WHERE id = ?", (json.dumps(g), sid))
    con.commit(); con.close()
    _write_emb(os.path.join(root, "embeddings_cache.db"), universe, X)
    _write_emb(os.path.join(root, "intent_emb_qwen3.db"), universe, X)
    pin = ZC.sha256_file(os.path.join(root, "intent_emb_qwen3.db"))
    s1 = os.path.join(root, "s1")
    os.makedirs(os.path.join(s1, "intent_s1_build"))
    sc = sqlite3.connect(os.path.join(s1, "snapshots.db"))
    sc.execute("CREATE TABLE snapshots (id TEXT, graph TEXT, settings TEXT)")
    for (name, slug), ti in zip(MASSIVE, massive_from):
        spec = trees[ti]
        sid = "2026_fix_%s" % slug
        nodes = [dict(id=i, depth=n["depth"], childIds=list(n.get("kids", [])), queryIds=[CA.qid(universe[j]) for j in n.get("items", [])],
                      vmfMu=[1.0] + [0.0] * (DIM_FIX - 1)) for i, n in sorted(spec.items())]
        sc.execute("INSERT INTO snapshots VALUES (?,?,?)", (sid, json.dumps(dict(rootId="n00000001", nodes=nodes)), "{}"))
        sc.execute("INSERT INTO snapshots VALUES (?,?,?)", ("2099_decoy_%s" % slug, json.dumps(dict(rootId="n00000001", nodes=[])), "{}"))
        rd = os.path.join(s1, "experiment_results", "intent_transfer", "s1", slug, "seed_42")
        os.makedirs(os.path.join(rd, "diagnostics"))
        open(os.path.join(rd, "headless_run.log"), "w", encoding="utf-8").write("x\nINFO Snapshot ID: %s\n" % sid)
        json.dump({"intent_build": {"arm": name}, "embedding_cache_source_sha256": pin}, open(os.path.join(rd, "diagnostics", "run_manifest.json"), "w"))
        bd = sqlite3.connect(os.path.join(s1, "intent_s1_build", "%s.db" % slug))
        bd.execute("CREATE TABLE intent_corpus (id INTEGER PRIMARY KEY, question TEXT, category TEXT, side TEXT, fine TEXT)")
        bd.execute("CREATE TABLE intent_build_meta (key TEXT PRIMARY KEY, value TEXT)")
        bd.execute("INSERT INTO intent_build_meta VALUES ('arm', ?)", (name,))
        for j, t in enumerate(universe):
            bd.execute("INSERT INTO intent_corpus (question, category, side, fine) VALUES (?,?,?,?)", (t, "lbl", "TRAIN", "f"))
        bd.commit(); bd.close()
    sc.commit(); sc.close()
    ssx.triplets = triplets
    ctx = Ctx(data_root=root, s1_root=s1, B=B, triplets=triplets, ss_ctx=ssx, dim=DIM_FIX, check_blobs=False, emb_pin=pin,
              identity=identity or dict(IDENTITY, k=9))
    return ctx, universe


def _expected_identity(ctx, k):
    """The identity values from site_support's OWN descriptive_lines on the fixture (independent of this script's replay)."""
    o = []
    T, C, _ = SS.load_all(ctx.ss, o)
    ctx.ss.kmeans, ctx.ss.km_k = True, k
    o2 = []
    SS.descriptive_lines(ctx.ss, T, C, None, o2)
    tl = [l for l in o2 if l.startswith("DESCRIPTIVE tree pairs on C")][0]
    kl = [l for l in o2 if l.startswith("DESCRIPTIVE vs spherical")][0]
    pairs = re.findall(r"trip (\d\.\d{4})", tl)
    m = re.search(r"tree pairs mean nRF [\d.]+, mean triplet (\d\.\d{4}); k-means seed pairs mean nRF [\d.]+, mean triplet (\d\.\d{4})", kl)
    return dict(k=k, tree_mean=m.group(1), km_mean=m.group(2), pairs=pairs, source="fixture (site_support.descriptive_lines)")


# ---- independent reference (sets and loops; shares only the registered fit functions and the RNG stream)
def _ref_topo(cl, C_list, trip):
    mem = [set(c) for c in cl]
    out = []
    for a, b, c in trip:
        qa, qb, qc = C_list[a], C_list[b], C_list[c]
        ab = any(qa in m and qb in m and qc not in m for m in mem)
        ac = any(qa in m and qc in m and qb not in m for m in mem)
        bc = any(qb in m and qc in m and qa not in m for m in mem)
        n = ab + ac + bc
        out.append(3 if n != 1 else (0 if ab else (1 if ac else 2)))
    return np.array(out)


def _ref_collapse(h, rows_of_C, C_list, m):
    leaf = collections.defaultdict(set)
    for q, r in zip(C_list, rows_of_C):
        leaf[int(h["lab"][r])].add(q)
    nC = len(C_list)
    leaves = [frozenset(s) for s in leaf.values() if 2 <= len(s) < nC]
    order = sorted(h["internal"], key=lambda x: x[1])            # ascending rank: contracted first
    sets = []
    for ls, _r in order[::-1]:
        S = frozenset(q for j in ls for q in leaf.get(j, ()))
        if 2 <= len(S) < nC and S not in leaves and S not in sets:
            sets.append(S)
    return set(leaves) | set(sets[:m])


def _reference(ctx, trees, X, universe):
    qid = lambda j: CA.qid(universe[j])

    def mem(spec, i):
        n = spec[i]
        return set(qid(j) for j in n.get("items", [])) if not n.get("kids") else set().union(*(mem(spec, k) for k in n["kids"]))
    Ms = [sorted(mem(sp, "n00000001")) for sp in trees]
    C = sorted(set.intersection(*[set(m) for m in Ms]))
    Cs = set(C)
    vec = {qid(j): X[j][:DIM_FIX] / np.linalg.norm(X[j][:DIM_FIX]) for j in range(len(universe))}
    rs = np.random.RandomState(SEED_TRIP)
    trip = [tuple(rs.choice(len(C), 3, replace=False)) for _ in range(ctx.triplets)]
    tcl, mint, kk = [], [], []
    for sp in trees:
        allc = set()
        leafc, innc = set(), set()
        for i, n in sp.items():
            S = frozenset(mem(sp, i) & Cs)
            if 2 <= len(S) < len(C):
                allc.add(S)
                (innc if n.get("kids") and i != "n00000001" else leafc if not n.get("kids") else set()).add(S)
        tcl.append(allc); mint.append(len(innc - leafc)); kk.append(sum(1 for n in sp.values() if not n.get("kids")))
    tt = [_ref_topo(c, C, trip) for c in tcl]
    bt, bf = {}, {}
    for b in BASELINES:
        bt[b], bf[b] = [], []
        for r in range(4):
            Xr = np.array([vec[q] for q in Ms[r]])
            rows = [Ms[r].index(q) for q in C]
            hs = [BASELINES[b].fit(Xr, kk[r], s) for s in SEEDS]
            bt[b].append([_ref_topo(_ref_collapse(h, rows, C, mint[r]), C, trip) for h in hs])
            bf[b].append([_ref_topo(_ref_collapse(h, rows, C, None), C, trip) for h in hs])
    pairs = [(r, q) for r in range(4) for q in range(r + 1, 4)]
    N = len(trip)
    full = {b: float(np.mean([np.mean(bf[b][r][s] != bf[b][q][u]) for r, q in pairs for s in range(5) for u in range(5)])) for b in BASELINES}
    pm = {b: {(r, q): float(np.mean([np.mean(bt[b][r][s] != bt[b][q][u]) for s in range(5) for u in range(5)])) for r, q in pairs} for b in BASELINES}
    sd150 = {b: float(np.std([np.mean(bt[b][r][s] != bt[b][q][u]) for r, q in pairs for s in range(5) for u in range(5)], ddof=1)) for b in BASELINES}
    sd_t = float(np.std([np.mean(tt[r] != tt[q]) for r, q in pairs], ddof=1))

    def pv(w, x, y):                                                # one pair under the three conventions (independent form)
        both = (x != 3) & (y != 3)
        num = float(np.sum(w * ((x != y) & both))); den = float(np.sum(w * both))
        dis = float(np.sum(w * (x != y))); bu = float(np.sum(w * ((x == 3) & (y == 3))))
        return {"all": dis / N, "rb": num / den, "strict": (dis + bu) / N}

    def stat(w, pos, cnt):
        P = [(pos[i], pos[j]) for i in range(len(pos)) for j in range(i + 1, len(pos)) if pos[i] != pos[j]]
        res = {}
        tp = [pv(w, tt[r], tt[q]) for r, q in P]
        bp = {b: [[[pv(w, bt[b][r][s], bt[b][q][u]) for u in range(5)] for s in range(5)] for r, q in P] for b in BASELINES}
        for c in ("all", "rb", "strict"):
            tr = sum(x[c] for x in tp) / len(P)
            out = {}
            for b in BASELINES:
                acc = 0.0
                for k, (r, q) in enumerate(P):
                    acc += sum(cnt[b][r][s] * cnt[b][q][u] * bp[b][k][s][u][c] for s in range(5) for u in range(5)) / 25.0
                out[b] = tr - acc / len(P)
            res[c] = (out, tr)
        return res
    ones = {b: [[1] * 5 for _ in range(4)] for b in BASELINES}
    P0 = stat(np.ones(N), [0, 1, 2, 3], ones)
    point, tree_pt = P0["all"]
    rng = np.random.default_rng(SEED_BOOT)
    reps = {c: {b: [] for b in BASELINES} for c in ("all", "rb", "strict")}
    for _ in range(ctx.B):
        pos = rng.integers(0, 4, 4).tolist()
        while len(set(pos)) < 2:
            pos = rng.integers(0, 4, 4).tolist()
        cnt = {b: [np.bincount(rng.integers(0, 5, 5), minlength=5) for _ in range(4)] for b in BASELINES}
        w = np.bincount(rng.integers(0, N, N), minlength=N)
        st = stat(w, pos, cnt)
        for c in reps:
            for b in BASELINES:
                reps[c][b].append(st[c][0][b])
    ivs = {c: {b: tuple(np.percentile(reps[c][b], [2.5, 97.5])) for b in BASELINES} for c in reps}
    iv = ivs["all"]
    loo = {b: [] for b in BASELINES}
    for drop in range(4):
        d, _t = stat(np.ones(N), [r for r in range(4) if r != drop], ones)["all"]
        for b in BASELINES:
            loo[b].append(d[b])
    unres = [float(np.mean(x == 3)) for x in tt]
    return dict(C=C, point=point, tree=tree_pt, iv=iv, loo=loo, m=mint, k=kk, pairs=pairs, full=full, pm=pm, sd150=sd150, sd_t=sd_t,
                rb=P0["rb"], strict=P0["strict"], rb_iv=ivs["rb"], st_iv=ivs["strict"], unres=unres)


def _num(line, key):
    return float(re.search(re.escape(key) + r" ([+-]?\d+\.\d+)", line).group(1))


def _iv(line, b):
    m = re.search(r"D_%s = ([+-]\d\.\d{4}); 95%% percentile interval \[([+-]\d\.\d{4}), ([+-]\d\.\d{4})\]" % re.escape(b), line)
    return float(m.group(1)), float(m.group(2)), float(m.group(3))


def _exp_refuted(ref):
    ra = [b for b in DECIDING if not ref["iv"][b][1] < 0]
    rr = [b for b in DECIDING if not ref["rb_iv"][b][1] < 0]
    return "/".join(["%s (D_b)" % b for b in ra] + ["%s (D_b^RB)" % b for b in rr])


def _close(line, pattern, want):
    """The numbers captured by pattern in line, each within half a printed unit (+1e-9) of the reference (a float tie at the
    4th decimal may round either way)."""
    m = re.search(pattern, line)
    assert m, (pattern, line)
    got = [float(x) for x in m.groups()]
    assert len(got) == len(want) and all(abs(g - w) <= 5e-5 + 1e-9 for g, w in zip(got, want)), (line, got, want)


F = r"([+-]?\d+\.\d{4})"


def _rb_checks(txt, ref):
    """The ST1-RB, option (b) and unresolved-share lines against the independent reference (4 dp)."""
    for b in BASELINES:
        _close(ZC.line(txt, "ST1-RB INPUT %s " % b),
               r"tree mean %s; baseline mean %s; D_RB_%s = %s; 95%% percentile interval \[%s, %s\]" % (F, F, re.escape(b), F, F, F),
               [ref["rb"][1], ref["rb"][1] - ref["rb"][0][b], ref["rb"][0][b], ref["rb_iv"][b][0], ref["rb_iv"][b][1]])
        _close(ZC.line(txt, "DESCRIPTIVE option (b) %s " % b),
               r"counted as disagreement: tree mean %s, baseline mean %s, D %s \[%s, %s\]" % (F, F, F, F, F),
               [ref["strict"][1], ref["strict"][1] - ref["strict"][0][b], ref["strict"][0][b], ref["st_iv"][b][0], ref["st_iv"][b][1]])
    _close(ZC.line(txt, "UNRESOLVED SHARES"), r"trees " + ", ".join("%s %s" % (t, F) for t in SS.TREES) + ";", ref["unres"])
    return True

def selftest():
    checks = 0
    with scratch_dir.scratch("svk_selftest") as tmp:
        # ---------------- U: units on the deciding helpers (boundaries, numpy scalars, the seam)
        NEG = {"BKM": -1.0, "KM-AL": -1.0}
        assert st1_decide({"BKM": -0.3, "KM-AL": -0.2}, {"BKM": -1e-9, "KM-AL": -0.01}, NEG) == "MORE-STABLE"; checks += 1
        assert st1_decide({"BKM": -0.3, "KM-AL": -0.2}, {"BKM": 0.0, "KM-AL": -0.01}, NEG) == "NEITHER"; checks += 1          # ub = 0 is not < 0
        assert st1_decide({"BKM": 0.0, "KM-AL": -0.2}, {"BKM": 0.1, "KM-AL": 0.1}, NEG) == "NEITHER"; checks += 1             # lb = 0 is not > 0
        assert st1_decide({"BKM": -0.1, "KM-AL": np.float64(1e-9)}, {"BKM": 0.1, "KM-AL": 0.2}, NEG) == "LESS-STABLE"; checks += 1   # one suffices
        assert st1_decide({"BKM": np.float64(-0.3), "KM-AL": np.float64(-0.2)}, {"BKM": np.float64(-0.1), "KM-AL": np.float64(0.05)}, NEG) == "NEITHER"; checks += 1  # both needed
        # the bracketed RB conjunct (fix (a)): all-triplets clears 0 but RB does not -> NEITHER; RB at exactly 0 is not < 0; numpy scalars
        assert st1_decide({"BKM": -0.3, "KM-AL": -0.2}, {"BKM": -0.1, "KM-AL": -0.1}, {"BKM": -0.1, "KM-AL": np.float64(0.02)}) == "NEITHER"; checks += 1
        assert st1_decide({"BKM": -0.3, "KM-AL": -0.2}, {"BKM": -0.1, "KM-AL": -0.1}, {"BKM": np.float64(0.0), "KM-AL": -0.1}) == "NEITHER"; checks += 1
        assert st1_decide({"BKM": -0.3, "KM-AL": -0.2}, {"BKM": -0.1, "KM-AL": -0.1}, {"BKM": np.float64(-1e-9), "KM-AL": -0.1}) == "MORE-STABLE"; checks += 1
        assert abs(brier3("MORE-STABLE") - (0.35 ** 2 + 0.30 ** 2 + 0.05 ** 2)) < 1e-12 and abs(brier3("LESS-STABLE") - (0.65 ** 2 + 0.30 ** 2 + 0.95 ** 2)) < 1e-12; checks += 1
        assert band(0.18, P1_BASE) == "HELD" and band(0.40, P1_BASE) == "HELD" and band(0.4001, P1_BASE) == "FAILED" and band(0.0, P4_BAND) == "HELD"; checks += 1
        # bisecting: largest-first on 3 groups of sizes 40 / 20 / 20 (planted, far apart): leaves of the planted sizes, root split first
        rg = np.random.RandomState(4)
        Xb = np.vstack([np.eye(DIM_FIX)[i] * 10 + 0.01 * rg.standard_normal((n, DIM_FIX)) for i, n in ((0, 20), (1, 20), (2, 20), (3, 20))])
        Xb = unit_rows(Xb)
        hb = fit_bisecting(Xb, 4, 0)
        assert sorted(collections.Counter(hb["lab"].tolist()).values()) == [20, 20, 20, 20] and hb["L"] == 4; checks += 1
        hb3 = fit_bisecting(Xb, 3, 0)
        assert sorted(collections.Counter(hb3["lab"].tolist()).values()) == [20, 20, 40] and len(hb3["internal"]) == 1; checks += 1  # 2 splits, root excluded
        # the split order: the largest cluster is split (a fake split rule records the sizes it is handed)
        seen = []

        def rec_split(Xs, s):
            seen.append(len(Xs)); lab = np.zeros(len(Xs), dtype=int); lab[: max(1, len(Xs) // 3)] = 1; return lab
        hs = fit_bisecting(np.ones((30, 2)), 4, 0, split=rec_split)
        assert seen == [30, 20, 14] and hs["L"] == 4; checks += 1                         # 30 -> 10+20; 20 -> 6+14; 14: largest first
        assert [r for _, r in sorted(hs["internal"], key=lambda x: x[1], reverse=True)] == [(-1,), (-2,)]; checks += 1   # earliest bisection ranks highest
        # collapse: a KM-AL hierarchy on C keeps its m highest merges; the reference collapse agrees
        hk = fit_kmal(Xb, 4, 1)
        Cq = ["c%d" % i for i in range(len(Xb))]
        full_, kf, af = on_C(hk, np.arange(len(Xb)), Cq, None)
        c1, k1, a1 = on_C(hk, np.arange(len(Xb)), Cq, 1)
        assert (kf, af, k1, a1) == (2, 2, 1, 2) and c1 == _ref_collapse(hk, list(range(len(Xb))), Cq, 1) and len(full_) == 6; checks += 1
        hi_merge = max(hk["internal"], key=lambda x: x[1])[0]
        assert frozenset(q for i, q in enumerate(Cq) if hk["lab"][i] in hi_merge) in c1; checks += 1     # the HIGHEST merge kept
        # independent of the rank code: on the planted C (8 subclusters, 4 pairs, 2 super-groups with separated average-link
        # heights) KM-AL collapsed to 2 internal clusters keeps exactly the two planted super-groups
        Xp = unit_rows(_planted_vectors(np.random.RandomState(5), "planted")[:NC_FIX])
        Cp = ["p%03d" % i for i in range(NC_FIX)]
        cpl, kpl, apl = on_C(fit_kmal(Xp, 8, 0), np.arange(NC_FIX), Cp, 2)
        assert (kpl, apl) == (2, 6) and cpl - {frozenset(Cp[15 * s_:15 * s_ + 15]) for s_ in range(8)} == {frozenset(Cp[:60]), frozenset(Cp[60:])}, (kpl, apl); checks += 1
        # code pins refuse a different instrument
        rc, txt = ZC.capture(check_code_pins, {"site_support.py": "0" * 40})
        assert rc == ("refused", 2) and "instrument of record" in txt; checks += 1
        got = check_code_pins()
        assert got == PINNED_CODE; checks += 1

        # ---------------- N: the planted crossed design where the NAIVE interval wrongly clears 0 (core, exact values)
        # three identical trees + one outlier; both baselines constant 0.30 on every crossed pair: D point < 0, the triplets-only
        # interval clears 0, the registered interval does not (re-draw multisets heavy in the outlier put the tree mean above 0.30)
        N = 4000
        rgn = np.random.RandomState(8)
        base_t = rgn.randint(0, 3, N).astype(np.int8)                  # fully resolved here: the RB conjunct equals D_b (tested apart below)
        out_t = base_t.copy(); flip = rgn.rand(N) < 0.55; out_t[flip] = (out_t[flip] + 1) % 3
        tt = [base_t, base_t.copy(), base_t.copy(), out_t]
        bt = {}
        for b in BASELINES:
            bt[b] = []
            for r in range(4):
                row = []
                for s in range(5):
                    v = base_t.copy(); f = rgn.rand(N) < 0.18; v[f] = (v[f] + 1 + r % 2) % 3; row.append(v)
                bt[b].append(row)
        V, lay = pair_vectors(tt, bt, 4, list(BASELINES))
        bsn = bootstrap(V, lay, 4, list(BASELINES), 400, SEED_BOOT)
        nvn = bootstrap(V, lay, 4, list(BASELINES), 400, SEED_BOOT, resample_redraws=False, resample_seeds=False)
        d_pt = bsn["point"][2]
        lo_r = {b: interval(bsn["reps"][b])[0] for b in BASELINES}; hi_r = {b: interval(bsn["reps"][b])[1] for b in BASELINES}
        hi_n = {b: interval(nvn["reps"][b])[1] for b in BASELINES}; lo_n = {b: interval(nvn["reps"][b])[0] for b in BASELINES}
        assert all(d_pt[b] < -0.01 for b in BASELINES), d_pt; checks += 1
        hrb_n = {b: interval(nvn["conv"]["rb"]["reps"][b])[1] for b in BASELINES}; hrb_r = {b: interval(bsn["conv"]["rb"]["reps"][b])[1] for b in BASELINES}
        assert st1_decide(lo_n, hi_n, hrb_n) == "MORE-STABLE", (lo_n, hi_n, hrb_n); checks += 1         # the naive interval clears 0
        assert st1_decide(lo_r, hi_r, hrb_r) == "NEITHER" and all(hi_r[b] > 0 for b in BASELINES), (lo_r, hi_r); checks += 1
        # exact point by hand: tree mean = 3 outlier pairs of 6; baseline mean = mean over the 150 crossed values
        tp = 3 * float(np.mean(base_t != out_t)) / 6
        assert abs(bsn["point"][0] - tp) < 1e-6; checks += 1
        bm = float(np.mean([np.mean(bt["BKM"][r][s] != bt["BKM"][q][u]) for r in range(4) for q in range(r + 1, 4) for s in range(5) for u in range(5)]))
        assert abs(bsn["point"][1]["BKM"] - bm) < 1e-6; checks += 1
        # a replicate holding two copies of one re-draw drops that pair (combine on a hand multiset) and seeds are crossed
        ones = {b: [np.ones(5) for _ in range(4)] for b in BASELINES}
        t_, b_, d_ = combine(conventions(V.mean(axis=1, dtype=np.float64), lay["n"])["all"], lay, [3, 3, 0, 1], ones, list(BASELINES))
        want_t = (4 * float(np.mean(base_t != out_t)) + 0.0) / 5                                  # pairs 3-0 x2, 3-1 x2, 0-1
        assert abs(t_ - want_t) < 1e-6; checks += 1
        cnt = {b: [np.array([5., 0, 0, 0, 0]), np.array([0, 5., 0, 0, 0]), np.ones(5), np.ones(5)] for b in BASELINES}
        _t2, b2, _d2 = combine(conventions(V.mean(axis=1, dtype=np.float64), lay["n"])["all"], lay, [0, 1], cnt, list(BASELINES))
        assert abs(b2["KM-AL"] - float(np.mean(bt["KM-AL"][0][0] != bt["KM-AL"][1][1]))) < 1e-6; checks += 1   # seed 0 of r0 x seed 1 of r1
        _t3, b3, _d3 = combine(conventions(V.mean(axis=1, dtype=np.float64), lay["n"])["all"], lay, [1, 0], cnt, list(BASELINES))
        assert abs(b3["KM-AL"] - b2["KM-AL"]) < 1e-12; checks += 1                                # order of a pair does not matter
        # ---------------- RB: the B-1 design. Trees jointly unresolved on 70% of triplets and random (pairwise disagreement 2/3) on the
        # rest; baselines fully resolved, crossed disagreement about 0.34. All-triplets D about -0.14 clears 0 (the bias B-1 names);
        # the resolved-in-both D^RB about +0.33 does not -> NEITHER, not MORE-STABLE. Points by hand.
        rgb = np.random.RandomState(12)
        U = rgb.rand(N) < 0.70
        ttb = []
        for r in range(4):
            v = rgb.randint(0, 3, N).astype(np.int8); v[U] = 3; ttb.append(v)
        common = rgb.randint(0, 3, N).astype(np.int8)
        btb = {}
        for b in BASELINES:
            btb[b] = []
            for r in range(4):
                row = []
                for s in range(5):
                    v = common.copy(); f = rgb.rand(N) < 0.30; v[f] = rgb.randint(0, 3, int(f.sum())); row.append(v)
                btb[b].append(row)
        Vb, layb = pair_vectors(ttb, btb, 4, list(BASELINES))
        bsb = bootstrap(Vb, layb, 4, list(BASELINES), 300, SEED_BOOT)
        lob = {b: interval(bsb["reps"][b])[0] for b in BASELINES}; hib = {b: interval(bsb["reps"][b])[1] for b in BASELINES}
        hrbb = {b: interval(bsb["conv"]["rb"]["reps"][b])[1] for b in BASELINES}
        assert all(hib[b] < 0 for b in BASELINES) and all(hrbb[b] > 0 for b in BASELINES), (hib, hrbb); checks += 1
        assert st1_decide(lob, hib, hrbb) == "NEITHER"; checks += 1
        prs = [(r, q) for r in range(4) for q in range(r + 1, 4)]
        rb_hand = float(np.mean([np.sum((ttb[r] != ttb[q]) & ~U) / np.sum(~U) for r, q in prs]))
        st_hand = float(np.mean([np.mean((ttb[r] != ttb[q]) | U) for r, q in prs]))
        assert abs(bsb["conv"]["rb"]["point"][0] - rb_hand) < 1e-9 and abs(bsb["conv"]["strict"]["point"][0] - st_hand) < 1e-9; checks += 1
        bk_rb = float(np.mean([np.mean(btb["BKM"][r][s] != btb["BKM"][q][u]) for r, q in prs for s in range(5) for u in range(5)]))
        assert abs(bsb["conv"]["rb"]["point"][1]["BKM"] - bk_rb) < 1e-6; checks += 1               # fully resolved: RB = all
        # per-baseline seed draws are independent (the two baselines' replicate SDs differ on identical inputs)
        bt2 = {"BKM": bt["BKM"], "KM-AL": bt["BKM"]}
        V2, lay2 = pair_vectors(tt, bt2, 4, list(BASELINES))
        bs2 = bootstrap(V2, lay2, 4, list(BASELINES), 50, SEED_BOOT)
        assert float(np.max(np.abs(bs2["reps"]["BKM"] - bs2["reps"]["KM-AL"]))) > 1e-4; checks += 1

        # ---------------- E1: MORE-STABLE end to end (identical trees; isotropic vectors -> unstable baselines)
        trees1 = [_planted_tree(0), _planted_tree(1), _planted_tree(2, refine=True), _planted_tree(3, split_private=True)]   # k_r 9/9/9/10, m_r 2/2/4/2
        X1 = _planted_vectors(np.random.RandomState(1), "iso")
        ctx1, uni = _fix_world(os.path.join(tmp, "e1"), trees1, X1)
        ctx1.identity = _expected_identity(_fix_world(os.path.join(tmp, "e1i"), trees1, X1)[0], 9)
        ref1 = _reference(ctx1, trees1, X1, uni)
        outp = os.path.join(tmp, "e1_out", "o.txt")
        rc, txt = ZC.capture(main, ["--run", "--out", outp], ctx1)
        assert rc == 0, txt[-3000:]; checks += 1
        L = txt.splitlines()
        assert L[1].startswith("POOL READER (rule 7): pool_guard.assert_pool_of_record(%s) OK" % ctx1.ss.por[0]), L[1]; checks += 1
        assert ZC.line(txt, "DENOMINATOR: |C| = ").startswith("DENOMINATOR: |C| = 120 (SS-R1"); checks += 1
        rl = ZC.line(txt, "  re-draws: ")
        assert rl.count("|M_r| 130, k_r 9 leaves, m_r 2 internal clusters on C") == 2 and "af_s2048 |M_r| 130, k_r 9 leaves, m_r 4 internal clusters on C (of 12" in rl and rl.endswith("af_s42_o1 |M_r| 130, k_r 10 leaves, m_r 2 internal clusters on C (of 10 clusters on C)"), rl; checks += 1
        assert ref1["m"] == [2, 2, 4, 2] and ref1["k"] == [9, 9, 9, 10]; checks += 1
        assert ZC.line(txt, "IDENTITY CHECK").endswith(": OK"); checks += 1
        for b in BASELINES:
            d, lo, hi = _iv(ZC.line(txt, "ST1 INPUT %s:" % b), b)
            assert abs(d - round(ref1["point"][b], 4)) < 1e-9, (b, d, ref1["point"][b]); checks += 1
            assert abs(lo - round(ref1["iv"][b][0], 4)) < 1e-9 and abs(hi - round(ref1["iv"][b][1], 4)) < 1e-9, (b, lo, hi, ref1["iv"][b]); checks += 1
            assert hi < 0; checks += 1
            loo_s = ZC.line(txt, "ST1 INPUT %s:" % b).split("leave-one-re-draw-out ")[1].split(";")[0]
            assert loo_s == "/".join("%+.4f" % x for x in ref1["loo"][b]), (loo_s, ref1["loo"][b]); checks += 1
        assert ref1["tree"] > 0.0 and "tree mean %.4f (6 pairs)" % ref1["tree"] in ZC.line(txt, "ST1 INPUT BKM:"); checks += 1
        _rb_checks(txt, ref1); checks += 1
        assert ref1["rb"][1] == 0.0; checks += 1                         # the refinement never contradicts a resolved triplet: tree RB 0
        assert ZC.line(txt, "ST1 (DECIDING").split("): ")[1].startswith("MORE-STABLE -- BKM D %+.4f" % ref1["point"]["BKM"]); checks += 1
        assert ZC.line(txt, "FAILS (rule 8)") == "FAILS (rule 8): MORE-STABLE refuted at the planned n: no"; checks += 1
        assert ZC.line(txt, "F-ST ") == "F-ST (fires iff ST1 is not MORE-STABLE): NOT FIRED" and "F-ST (LESS-STABLE)" not in txt; checks += 1
        assert ZC.line(txt, "P3 ") == "P3 ST1 predicted MORE-STABLE 0.65 / NEITHER 0.30 / LESS-STABLE 0.05; occurred MORE-STABLE; Brier (three outcomes) 0.2150"; checks += 1
        p1 = ZC.line(txt, "P1 ")
        km_base = ref1["tree"] - ref1["point"]["KM-AL"]
        assert p1 == "P1 KM-AL baseline mean %.4f in [0.18, 0.40]: %s; D_KM-AL %+.4f in [-0.33, -0.10]: %s" % (
            km_base, band(km_base, P1_BASE), ref1["point"]["KM-AL"], band(ref1["point"]["KM-AL"], P1_D)), p1; checks += 1
        bk_base = ref1["tree"] - ref1["point"]["BKM"]
        assert ZC.line(txt, "P2 ") == "P2 BKM baseline mean %.4f in [0.10, 0.35]: %s; D_BKM %+.4f in [-0.28, -0.03]: %s" % (
            bk_base, band(bk_base, P2_BASE), ref1["point"]["BKM"], band(ref1["point"]["BKM"], P2_D)); checks += 1
        dm = -ref1["pm"]["KM-AL"][(0, 1)]                 # MASSIVE = trees 0, 1 on the same items, vectors and triplets: the r0 x r1 crossed mean
        assert ZC.line(txt, "P5 ") == "P5 (descriptive) MASSIVE tree disagreement 0.0000 in [0.03, 0.20]: FAILED; D_KM-AL %+.4f in [-0.30, 0.00]: %s" % (
            dm, band(dm, P5_D)), (ZC.line(txt, "P5 "), dm); checks += 1
        assert "BKM baseline mean %.4f, D %+.4f [" % (ref1["pm"]["BKM"][(0, 1)], -ref1["pm"]["BKM"][(0, 1)]) in ZC.line(txt, "DESCRIPTIVE MASSIVE pair"); checks += 1
        assert "|C_M| = 130" not in txt and "|C_M| = 120 (intersection" in ZC.line(txt, "MASSIVE (DESCRIPTIVE ONLY"); checks += 1
        assert open(outp, encoding="utf-8").read().rstrip().splitlines()[-1].startswith("WHAT THIS RESULT WILL NOT SHOW (registered): correctness"); checks += 1
        for b in BASELINES:
            sup = ZC.line(txt, "SUPPORT AS REALISED %s" % b)
            se = (ref1["sd_t"] ** 2 / 2 + ref1["sd150"][b] ** 2 / 2) ** 0.5
            want = "over the 150 crossed values %.4f; SE = sqrt(%.4f^2/2 + %.4f^2/2) = %.4f; MDE80 = 2.80 x SE = %.4f" % (ref1["sd150"][b], ref1["sd_t"], ref1["sd150"][b], se, 2.80 * se)
            assert want in sup and "tree-pair SD %.4f (6 pairs)" % ref1["sd_t"] in sup and ref1["sd_t"] > 0, (sup, want); checks += 1
        # write-once
        body = open(outp, encoding="utf-8").read()
        assert ZC.line(body, "ST1 (DECIDING") == ZC.line(txt, "ST1 (DECIDING"); checks += 1
        rc2, txt2 = ZC.capture(main, ["--run", "--out", outp], ctx1)
        assert rc2 == ("refused", 2) and "WRITE-ONCE" in txt2 and open(outp, encoding="utf-8").read() == body; checks += 1
        # dry-run on the same world
        ctxd, _ = _fix_world(os.path.join(tmp, "e1d"), trees1, X1, identity=ctx1.identity)
        rc3, txt3 = ZC.capture(main, ["--dry-run"], ctxd)
        assert rc3 == 0 and txt3.splitlines()[1].startswith("POOL READER (rule 7)") and "ST1" not in txt3 and "D_BKM" not in txt3, txt3[-1500:]; checks += 1
        assert ZC.line(txt3, "IDENTITY CHECK").endswith(": OK") and ZC.line(txt3, "COST ESTIMATE --run: about ").count(" min CPU") == 1; checks += 1
        assert txt3.rstrip().endswith("--dry-run: no D_b printed, nothing written."); checks += 1

        # ---------------- E2: LESS-STABLE end to end (random trees; planted hierarchical vectors -> identical baselines)
        trees2 = [_random_tree(t, 100 + t) for t in range(4)]
        X2 = _planted_vectors(np.random.RandomState(2), "planted")
        ctx2, uni2 = _fix_world(os.path.join(tmp, "e2"), trees2, X2)
        ctx2.identity = _expected_identity(_fix_world(os.path.join(tmp, "e2i"), trees2, X2)[0], 9)
        ref2 = _reference(ctx2, trees2, X2, uni2)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "e2_out", "o.txt")], ctx2)
        assert rc == 0, txt[-3000:]; checks += 1
        for b in BASELINES:
            d, lo, hi = _iv(ZC.line(txt, "ST1 INPUT %s:" % b), b)
            assert abs(d - round(ref2["point"][b], 4)) < 1e-9 and abs(lo - round(ref2["iv"][b][0], 4)) < 1e-9 and abs(hi - round(ref2["iv"][b][1], 4)) < 1e-9, (b, d, lo, hi, ref2); checks += 1
        assert "tree mean %.4f (6 pairs)" % ref2["tree"] in ZC.line(txt, "ST1 INPUT KM-AL:") and ref2["tree"] > 0.3, ref2["tree"]; checks += 1
        assert ZC.line(txt, "ST1 (DECIDING").split("): ")[1].startswith("LESS-STABLE -- lower bound > 0 for BKM/KM-AL;"); checks += 1
        assert ZC.line(txt, "FAILS (rule 8)") == "FAILS (rule 8): MORE-STABLE refuted at the planned n: yes -- upper bound >= 0 against " + _exp_refuted(ref2), ZC.line(txt, "FAILS"); checks += 1
        _rb_checks(txt, ref2); checks += 1
        assert ZC.line(txt, "F-ST (fires").startswith("F-ST (fires iff ST1 is not MORE-STABLE): FIRED -- the re-draw trees are not shown"); checks += 1
        assert ZC.line(txt, "F-ST (LESS-STABLE)") == "F-ST (LESS-STABLE): a bisecting or centroid-linkage hierarchy is the more reproducible object at this granularity"; checks += 1
        assert ZC.line(txt, "P3 ").endswith("occurred LESS-STABLE; Brier (three outcomes) 1.4150"); checks += 1
        # P4 on a planted world: collapsed (leaves + A, B) vs full binary differs; value against an independent recount
        kb2 = ref2["tree"] - ref2["point"]["KM-AL"]
        sh2 = abs(kb2 - ref2["full"]["KM-AL"])
        assert ZC.line(txt, "P4 ") == "P4 (descriptive) shape matching moves the KM-AL baseline mean by %.4f (collapsed %.4f vs full binary %.4f) in [0.00, 0.05]: %s" % (
            sh2, kb2, ref2["full"]["KM-AL"], band(sh2, P4_BAND)), (ZC.line(txt, "P4 "), sh2, ref2["full"]); checks += 1
        assert ref2["full"]["KM-AL"] != kb2; checks += 1                                        # collapse moved the mean (non-vacuous)

        # ---------------- E3: NEITHER end to end (three planted trees + one random; baselines 0): point > 0, naive interval
        # clears 0 (LESS), registered lower bound exactly 0 -> NEITHER; F-ST FIRED without the LESS sentence
        trees3 = [_planted_tree(t) for t in range(3)] + [_random_tree(3, 77)]
        ctx3, uni3 = _fix_world(os.path.join(tmp, "e3"), trees3, X2)
        ctx3.identity = _expected_identity(_fix_world(os.path.join(tmp, "e3i"), trees3, X2)[0], 9)
        ref3 = _reference(ctx3, trees3, X2, uni3)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "e3_out", "o.txt")], ctx3)
        assert rc == 0, txt[-3000:]; checks += 1
        for b in BASELINES:
            line_b = ZC.line(txt, "ST1 INPUT %s:" % b)
            d, lo, hi = _iv(line_b, b)
            assert d > 0 and lo <= 0.0 < hi and abs(hi - round(ref3["iv"][b][1], 4)) < 1e-9 and abs(lo - round(ref3["iv"][b][0], 4)) < 1e-9, (b, d, lo, hi, ref3["iv"][b]); checks += 1
            nlo = float(line_b.split("triplets-only interval [")[1].split(",")[0])
            assert nlo > 0, line_b; checks += 1                                                  # the naive interval clears 0
        rr3 = "/".join(b for b in DECIDING if not ref3["rb_iv"][b][1] < 0) or "none"
        assert ZC.line(txt, "ST1 (DECIDING").split("): ")[1].startswith("NEITHER -- upper bound >= 0 for BKM/KM-AL (D_b) and %s (D_b^RB), no lower bound > 0;" % rr3), ZC.line(txt, "ST1 (DECIDING"); checks += 1
        assert ZC.line(txt, "FAILS (rule 8)") == "FAILS (rule 8): MORE-STABLE refuted at the planned n: yes -- upper bound >= 0 against " + _exp_refuted(ref3); checks += 1
        _rb_checks(txt, ref3); checks += 1
        assert ZC.line(txt, "F-ST (fires").startswith("F-ST (fires iff ST1 is not MORE-STABLE): FIRED") and "F-ST (LESS-STABLE)" not in txt; checks += 1
        assert ZC.line(txt, "P3 ").endswith("occurred NEITHER; Brier (three outcomes) 0.9150"); checks += 1
        assert abs(_num(ZC.line(txt, "P5 "), "MASSIVE tree disagreement") - 0.0) < 1e-12; checks += 1        # MASSIVE = trees 0, 1 (identical)

        # ---------------- registered constants; identity clauses each refuse alone
        assert (B_BOOT, TRIPLETS, SEED_BOOT, SEED_TRIP, SEEDS, DIM) == (2000, 100000, 20261005, 20261004, (0, 1, 2, 3, 4), 256) and Ctx().B == 2000 and Ctx().triplets == 100000; checks += 1
        assert IDENTITY["k"] == 81 and IDENTITY["tree_mean"] == "0.0684" and IDENTITY["km_mean"] == "0.3243" and IDENTITY["pairs"] == ["0.0787", "0.0883", "0.1000", "0.0481", "0.0593", "0.0357"]; checks += 1
        ctxi, _ = _fix_world(os.path.join(tmp, "idc"), trees1, X1, identity=ctx1.identity)
        Wi = load_mmlu(ctxi, [])
        for bad in (dict(tree_mean="0.9999"), dict(pairs=["0.9999"] + list(ctx1.identity["pairs"][1:])), dict(km_mean="0.0001")):
            ctxi.identity = dict(ctx1.identity, **bad)
            rc, txt = ZC.capture(identity_check, ctxi, Wi, [])
            assert isinstance(rc, tuple) and rc == ("refused", 2) and "IDENTITY CHECK failed" in txt, (bad, txt[-300:]); checks += 1
        # ---------------- refusals: identity mismatch, a MASSIVE member off TRAIN, the emb pin, slice
        ctx4, _ = _fix_world(os.path.join(tmp, "r1"), trees1, X1, identity=dict(ctx1.identity, km_mean="0.9999"))
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "r1_out", "o.txt")], ctx4)
        assert isinstance(rc, tuple) and rc == ("refused", 2) and "IDENTITY CHECK failed" in txt and "ST1" not in txt and not os.path.exists(os.path.join(tmp, "r1_out", "o.txt")); checks += 1
        ctx5, _ = _fix_world(os.path.join(tmp, "r2"), trees1, X1, identity=ctx1.identity)
        bd = sqlite3.connect(os.path.join(ctx5.s1_root, "intent_s1_build", "m_af_s2.db"))
        bd.execute("UPDATE intent_corpus SET side = 'GATE' WHERE question = 'doc 5'"); bd.commit(); bd.close()
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "r2_out", "o.txt")], ctx5)
        assert rc == ("refused", 2) and "M-AF-s2: 1 members are not TRAIN rows of m_af_s2.db" in txt; checks += 1
        ctx6, _ = _fix_world(os.path.join(tmp, "r3"), trees1, X1, identity=ctx1.identity)
        ctx6.emb_pin = "0" * 64
        rc, txt = ZC.capture(main, ["--dry-run"], ctx6)
        assert rc == ("refused", 2) and "intent_emb_qwen3.db sha256" in txt and "the registrar's pin" in txt; checks += 1
        ctx7, _ = _fix_world(os.path.join(tmp, "r4"), trees1, X1, identity=ctx1.identity)
        ctx7.dim = 256
        rc, txt = ZC.capture(main, ["--dry-run"], ctx7)
        assert rc == ("refused", 2) and "the registered slice is 256" in txt; checks += 1
        ctx8, _ = _fix_world(os.path.join(tmp, "r5"), trees1, X1, identity=ctx1.identity)
        mp = os.path.join(ctx8.s1_root, "experiment_results", "intent_transfer", "s1", "m_af", "seed_42", "diagnostics", "run_manifest.json")
        mj = json.load(open(mp)); mj["embedding_cache_source_sha256"] = "1" * 64; json.dump(mj, open(mp, "w"))
        rc, txt = ZC.capture(main, ["--dry-run"], ctx8)
        assert rc == ("refused", 2) and "M-AF: the build's embedding source sha 1111" in txt; checks += 1
    assert checks == SELFTEST_CHECKS, "selftest ran %d checks, pinned %d" % (checks, SELFTEST_CHECKS)
    print("%s SELFTEST OK: %d value-asserting checks (pinned %d)" % (TAG, checks, SELFTEST_CHECKS))
    return 0


MUTANTS = [
    ("X1", "ST1 MORE-STABLE with upper bound <= 0", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n", "    if all(bool(float(hi[b]) <= 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n"),
    ("X2", "ST1 MORE-STABLE needs one baseline (any for all)", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n", "    if any(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n"),
    ("X47", "READY R5: every re-draw collapsed to tree 0's m_r (M-1)", "                cl_c, kept, avail = on_C(h, W[\"cpos\"][t], C_list, W[\"m\"][t])\n", "                cl_c, kept, avail = on_C(h, W[\"cpos\"][t], C_list, W[\"m\"][trees[0]])\n"),
    ("X48", "the RB conjunct dropped from MORE-STABLE (fix (a) not applied)", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n", "    if all(bool(float(hi[b]) < 0) for b in DECIDING):\n"),
    ("X49", "RB conjunct on one baseline only (any for all)", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and any(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n"),
    ("X50", "RB conjunct with upper bound <= 0", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) < 0) for b in DECIDING):\n", "    if all(bool(float(hi[b]) < 0) for b in DECIDING) and all(bool(float(hi_rb[b]) <= 0) for b in DECIDING):\n"),
    ("X51", "RB = differ share over ALL triplets (no division by the both-resolved share)", "        rb = np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)\n", "        rb = num\n"),
    ("X52", "RB denominator counts triplets resolved in either (not both)", "    den = [(a != 3) & (c != 3) for a, c in prs]\n", "    den = [(a != 3) | (c != 3) for a, c in prs]\n"),
    ("X53", "RB numerator counts one-unresolved differences", "    num = [(a != c) & (a != 3) & (c != 3) for a, c in prs]\n", "    num = [(a != c) for a, c in prs]\n"),
    ("X54", "RB interval from the all-triplets replicates", "        lo_rb[b], hi_rb[b] = interval(rbc[\"reps\"][b])\n", "        lo_rb[b], hi_rb[b] = interval(bs[\"reps\"][b])\n"),
    ("X55", "option (b) strict convention = the registered one (both-unresolved not added)", "    return {\"all\": dis, \"rb\": rb, \"strict\": num + (1.0 - den)}\n", "    return {\"all\": dis, \"rb\": rb, \"strict\": dis}\n"),
    ("X56", "unresolved share of the trees counts topology 0 instead of 3", "    un_t = [float(np.mean(x == 3)) for x in tt]\n", "    un_t = [float(np.mean(x == 0)) for x in tt]\n"),
    ("X57", "RB replicates scored on the point weights (triplets not resampled for RB)", "            cv = conventions(M[:, j], n)\n", "            cv = dict(conventions(M[:, j], n), rb=cv0[\"rb\"])\n"),
    ("X3", "ST1 LESS-STABLE with lower bound >= 0", "    if any(bool(float(lo[b]) > 0) for b in DECIDING):\n", "    if any(bool(float(lo[b]) >= 0) for b in DECIDING):\n"),
    ("X4", "ST1 LESS-STABLE needs both baselines (all for any)", "    if any(bool(float(lo[b]) > 0) for b in DECIDING):\n", "    if all(bool(float(lo[b]) > 0) for b in DECIDING):\n"),
    ("X5", "re-draws not resampled (the naive interval decides)", "def bootstrap(V, lay, R, names, B, seed, resample_redraws=True, resample_seeds=True, resample_triplets=True, chunk=50,\n", "def bootstrap(V, lay, R, names, B, seed, resample_redraws=False, resample_seeds=True, resample_triplets=True, chunk=50,\n"),
    ("X6", "seeds not resampled", "def bootstrap(V, lay, R, names, B, seed, resample_redraws=True, resample_seeds=True, resample_triplets=True, chunk=50,\n", "def bootstrap(V, lay, R, names, B, seed, resample_redraws=True, resample_seeds=False, resample_triplets=True, chunk=50,\n"),
    ("X7", "triplets not resampled", "def bootstrap(V, lay, R, names, B, seed, resample_redraws=True, resample_seeds=True, resample_triplets=True, chunk=50,\n", "def bootstrap(V, lay, R, names, B, seed, resample_redraws=True, resample_seeds=True, resample_triplets=False, chunk=50,\n"),
    ("X8", "a pair of two copies of one re-draw kept", "\n    P = [(pos[i], pos[j]) for i in range(len(pos)) for j in range(i + 1, len(pos)) if pos[i] != pos[j]]\n", "\n    P = [(pos[i], pos[j]) for i in range(len(pos)) for j in range(i + 1, len(pos))]\n"),
    ("X9", "seed resamples shared by both baselines", "                cnt = {b: [np.bincount(rng.integers(0, S, S), minlength=S).astype(np.float64) for _ in range(R)] for b in names}\n",
     "                _c = [np.bincount(rng.integers(0, S, S), minlength=S).astype(np.float64) for _ in range(R)]; cnt = {b: _c for b in names}\n"),
    ("X10", "seed pairs paired (diagonal) instead of crossed", "            vals.append(float(cnt[b][r] @ Mx @ cnt[b][q]) / float(S * S))\n", "            vals.append(float(np.diag(Mx) @ cnt[b][r]) / float(S))\n"),
    ("X11", "a replicate with < 2 distinct re-draws not redrawn", "                while len(set(pos)) < 2:\n                    pos = rng.integers(0, R, R).tolist()\n", "                while False:\n                    pos = rng.integers(0, R, R).tolist()\n"),
    ("X12", "shape match off in the deciding form (full binary decides)", "                cl_c, kept, avail = on_C(h, W[\"cpos\"][t], C_list, W[\"m\"][t])\n", "                cl_c, kept, avail = on_C(h, W[\"cpos\"][t], C_list, None)\n"),
    ("X13", "contraction reversed (highest internal edges contracted first)", "    for ls, _rank in sorted(h[\"internal\"], key=lambda x: x[1], reverse=True):\n", "    for ls, _rank in sorted(h[\"internal\"], key=lambda x: x[1], reverse=False):\n"),
    ("X14", "BKM keeps the latest bisections", "    internal = [(frozenset(under(c)), (-step[c],)) for c in step if c != 0]\n", "    internal = [(frozenset(under(c)), (step[c],)) for c in step if c != 0]\n"),
    ("X15", "m_r counts the leaf sets too", "    return len({s for s in inner if 2 <= len(s) < nC} - leafsets)\n", "    return len({s for s in inner if 2 <= len(s) < nC} | leafsets)\n"),
    ("X16", "percentile 5 / 95 instead of 2.5 / 97.5", "    lo, hi = np.percentile(x, [2.5, 97.5])\n", "    lo, hi = np.percentile(x, [5.0, 95.0])\n"),
    ("X17", "D_b sign flipped (baseline - tree)", "    return tree, base, {b: tree - base[b] for b in names}\n", "    return tree, base, {b: base[b] - tree for b in names}\n"),
    ("X18", "baselines fitted on C (wrong population) instead of M_r", "    F = {t: fit_set(W[\"X\"][t], W[\"k\"][t]) for t in trees}\n", "    F = {t: fit_set(W[\"XC\"], W[\"k\"][t]) for t in trees}\n"),
    ("X19", "one k (the median leaf count) for every re-draw", "    F = {t: fit_set(W[\"X\"][t], W[\"k\"][t]) for t in trees}\n", "    F = {t: fit_set(W[\"X\"][t], int(np.median(list(W[\"k\"].values())))) for t in trees}\n"),
    ("X20", "bisecting splits the smallest cluster (max -> min)", "        top = max(len(rows[c]) for c in cand)\n", "        top = min(len(rows[c]) for c in cand)\n"),
    ("X21", "identity mismatch not refused", "    if not ok:\n        ZC.refuse(TAG, \"IDENTITY CHECK failed", "    if False:\n        ZC.refuse(TAG, \"IDENTITY CHECK failed"),
    ("X22", "identity check ignores the six per-pair values", "    ok = (tree_mean == idn[\"tree_mean\"] and km_mean == idn[\"km_mean\"] and six == list(idn[\"pairs\"]))\n", "    ok = (tree_mean == idn[\"tree_mean\"] and km_mean == idn[\"km_mean\"])\n"),
    ("X23", "F-ST FIRED line not printed", "        out.append(\"F-ST (fires iff ST1 is not MORE-STABLE): FIRED", "        0 and out.append(\"F-ST (fires iff ST1 is not MORE-STABLE): FIRED"),
    ("X24", "LESS-STABLE sentence not printed", "    if v == \"LESS-STABLE\":\n        out.append(\"F-ST (LESS-STABLE)", "    if False:\n        out.append(\"F-ST (LESS-STABLE)"),
    ("X25", "FAILS line not printed", "    out.append(\"FAILS (rule 8): MORE-STABLE refuted", "    0 and out.append(\"FAILS (rule 8): MORE-STABLE refuted"),
    ("X26", "write-once dropped (pre-check and mode x gone)",
     "            ZC.refuse(TAG, \"%s exists: the outcome of record is WRITE-ONCE (refused before any read)\" % p)\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    ZC.write_once(out_path, text, TAG)\n",
     "            pass\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)\n    open(out_path, \"w\", encoding=\"utf-8\").write(text)\n"),
    ("X27", "P3 Brier on the MORE-STABLE outcome only", "    return sum((p - (1.0 if w == word else 0.0)) ** 2 for w, p in P3_PROB.items())\n", "    return (P3_PROB[\"MORE-STABLE\"] - (1.0 if word == \"MORE-STABLE\" else 0.0)) ** 2\n"),
    ("X28", "prediction bands read as open intervals", "    return \"HELD\" if ZC.in_band(x, bd) else \"FAILED\"\n", "    return \"HELD\" if (x is not None and bd[0] < x < bd[1]) else \"FAILED\"\n"),
    ("X29", "leave-one-out keeps every re-draw", "        keep = [r for r in range(R) if r != drop]\n", "        keep = list(range(R))\n"),
    ("X30", "deciding triplets = the second draw", "    return trip\n\n\n# ----------------------------------------------------------------------------------------------- fits", "    return tv\n\n\n# ----------------------------------------------------------------------------------------------- fits"),
    ("X31", "MASSIVE C_M = union instead of intersection", "    C_M = sorted(frozenset.intersection(*[G[n][\"mem\"] for n in names]))\n", "    C_M = sorted(frozenset.union(*[G[n][\"mem\"] for n in names]))\n"),
    ("X32", "MASSIVE member off TRAIN not refused (wrong split side)", "        bad = sorted(q for q in mem if q not in side or side[q][1] != \"TRAIN\")\n", "        bad = sorted(q for q in mem if q not in side)\n"),
    ("X33", "intent_emb_qwen3.db pin not checked", "    if embs[\"sha256\"] != pin:\n", "    if False:\n"),
    ("X34", "instrument blobs not checked", "        if b != want:\n            ZC.refuse(TAG, \"%s is blob", "        if False:\n            ZC.refuse(TAG, \"%s is blob"),
    ("X35", "tree mean from the first pair only (first-site-only)", "    tree = float(np.mean([dis[lay[\"T\"][(min(r, q), max(r, q))]] for r, q in P]))\n", "    tree = float(np.mean([dis[lay[\"T\"][(min(r, q), max(r, q))]] for r, q in P[:1]]))\n"),
    ("X36", "vectors not renormalised after slicing", "    V = np.asarray(V, dtype=np.float64)\n    return V / np.linalg.norm(V, axis=1, keepdims=True)\n", "    V = np.asarray(V, dtype=np.float64)\n    return V\n"),
    ("X37", "slice check dropped", "    if dim != ctx.dim:\n", "    if False:\n"),
    ("X38", "P5 scored on BKM instead of KM-AL", "               % (tree, band(tree, P5_TREE), f4(D[\"KM-AL\"]), band(D[\"KM-AL\"], P5_D)))\n", "               % (tree, band(tree, P5_TREE), f4(D[\"BKM\"]), band(D[\"BKM\"], P5_D)))\n"),
    ("X39", "MASSIVE baselines not shape-matched", "            bt[b].append([topo(on_C(h, MW[\"cpos\"][n], MW[\"C\"], MW[\"m\"][n])[0], MW[\"idx\"], trip) for h in F[b]])\n", "            bt[b].append([topo(on_C(h, MW[\"cpos\"][n], MW[\"C\"], None)[0], MW[\"idx\"], trip) for h in F[b]])\n"),
    ("X40", "realised SE without the baseline term (support readout)", "        se = (sd_t ** 2 / 2.0 + sd_150 ** 2 / 2.0) ** 0.5\n", "        se = (sd_t ** 2 / 2.0) ** 0.5\n"),
    ("X41", "bootstrap B of record changed (2000 -> 1000)", "B_BOOT = 2000\n", "B_BOOT = 1000\n"),
    ("X42", "bootstrap seed of record changed", "    bs = bootstrap(V, lay, R, names, ctx.B, SEED_BOOT)\n", "    bs = bootstrap(V, lay, R, names, ctx.B, SEED_BOOT + 1)\n"),
    ("X44", "identity check ignores the tree-pair mean", "    ok = (tree_mean == idn[\"tree_mean\"] and km_mean ==", "    ok = (True and km_mean =="),
    ("X45", "identity check ignores the k-means seed-pair mean", " and km_mean == idn[\"km_mean\"] and six ==", " and True and six =="),
    ("X46", "the manifests' embedding source sha not checked", "        if man.get(\"embedding_cache_source_sha256\") != pin:\n", "        if False:\n"),
    ("X43", "KM-AL internal ranks by merge index only (heights ignored)", "                internal.append((m, (float(row[2]), j)))\n", "                internal.append((m, (0.0, -j)))\n"),
]


CONTROL = ("C0", "no-op control (a comment changed): must SURVIVE", "# ----------------------------------------------------------------------------------------------- main\n", "# ---------------------------------------------------------------------------------------------- main (control)\n")


# ----------------------------------------------------------------------------------------------- main
def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="STABILITY-VS-KMEANS readout (zero calls; POOL READER)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--data-root", default=None)
    ap.add_argument("--s1-root", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        ctl = ZC.run_mutants(os.path.abspath(__file__), [CONTROL])          # non-vacuity: an untouched selftest must pass in the sandbox
        res = ZC.run_mutants(os.path.abspath(__file__), MUTANTS)
        return 0 if ctl[0][2] == "SURVIVED" and all(r[2] == "killed" for r in res) else 1
    if ctx is None:
        dr = os.path.abspath(a.data_root) if a.data_root else ROOT
        ctx = Ctx(data_root=dr, s1_root=os.path.abspath(a.s1_root) if a.s1_root else None)
    if a.dry_run:
        return dry_run(ctx)
    return run(ctx, a.out or ZC.default_out("stability_vs_kmeans", "stability_vs_kmeans_outcome.txt"))


if __name__ == "__main__":
    sys.exit(main())
