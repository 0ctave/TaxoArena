"""tree_cut_granularity.py: TREE-CUT-GRANULARITY (TC1 per tree, TC across the three trees) and NESTING (NV1 per tree-depth cell, NV
across the six cells) on the three content-closed qwen3 anchor-free MMLU-Pro re-draw trees Q_e1sd1-3. ZERO calls: no judge, no LLM,
no embedding call, no construction, no Gradle. A CPU readout; a POOL READER (rule 7).

REGISTRATIONS OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — TREE-CUT-GRANULARITY: on three content-closed
  MMLU-Pro re-draw trees not used in the pilot (Q_e1sd1-3), is the anchor-free tree cut at each depth a worse partition of its own
  held-out than a dedicated flat spherical k-means at the same cell count ..." (L25002-L25014, written at e83b59d5, parent d8ab39fa):
  TC1, TC, rule 8, Support (a)-(g), P1-P5, F-TC, WILL NOT SHOW.
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — NESTING: are two independently fitted flat
  spherical k-means partitions, at a coarse and at a fine cell count, nested ..." (L25016-L25027, same commit): NV1, NV, rule 8,
  Support (a)-(g), P1-P2, F-NV, IDENTITY. Record: "## Registrar's record 2026-10-08 ... six zero-call tests registered ..." (L24950).
  PILOT DISCLOSURE (both registrations): the 2026-10-07 exploratory numbers were SEEN (pilot role only, never evidence):
  E:/TaxoArena_tmp/hier_tests/granularity_free (results.json sha256 2fc8ba3a99b8dc54..., review/review_results.json dcfb3b0b...),
  E:/TaxoArena_tmp/hier_tests/nesting (results.json cb5a74cf0d870081..., review/recheck.json 432255bd...), and also
  E:/TaxoArena_tmp/hier_tests/test3_fair_backoff, E:/TaxoArena_tmp/cert_split, E:/TaxoArena_tmp/scpb/review_v3_synthesis.md. The
  three deciding trees Q_e1sd1-3 were NOT read by the pilot; af_clean_s42 (pilot-seen) is re-printed DESCRIPTIVE only.

LAUNCH SEQUENCE (the run-operator; zero calls; ONE single-threaded python process; never inside a construction or site null; run
`powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` first (exit 1 = free); from the MAIN checkout, or with
TAXOARENA_DATA_ROOT=<main checkout> from a worktree):
  0. python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_cut_granularity.py --selftest  # fixtures; no DB
     python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_cut_granularity.py --mutants   # the mutant table
  1. python tools/analysis/tree_cut_granularity.py --dry-run   # POOL lines first (the three e1sd pools, then p2dca for the
                                    # descriptive af_clean_s42); pins; splits re-derived byte-equal; run dirs checked; graphs pinned;
                                    # [EMB-GUARD] own ADMIT + permuted REFUSE; hygiene; structure (L_d, depths used, NESTING cells);
                                    # keyed COUNTS only; the fit plan and cost; NO fit, NO statistic, nothing written
  2. python tools/analysis/tree_cut_granularity.py --run       # the fits, TC1 / TC and NV1 / NV, every criterion / prediction /
                                    # falsifier line; outcome WRITE-ONCE (open mode "x"; refused before any read if it exists):
       experiment_results/tree_cut_granularity/tree_cut_granularity_outcome.txt (never committed: pin sha256, back up to
       E:/TaxoArena_backup_<date>_tree_cut_granularity with SHA256SUMS.txt). Expected CPU: 3 trees x (7 / 7 / 6 cell counts x 5 seeds
       x 10 restarts) spherical k-means on ~8,200 x 256 (timed 2-8 s per count and seed on synthetic data of that shape) + 5 bisecting
       fits per count (~2 s) + the descriptive af_clean_s42 tree: about 15-25 min on one thread, plus the [EMB-GUARD] and the 3PL
       (four fits).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  TC-R1 TREE: the run dir's last dag snapshot (anchor_free_readout.load_tree); a node with more than one parent REFUSES; depth =
        parent-chain length (the root 0), checked against the snapshot's depth field; C_d = the nodes at depth d plus every leaf
        shallower than d; L_d = |C_d| (printed); depths d = 1..D_max (D_max = the deepest leaf). Held-out (and fit) filing to a cut:
        flatLeaf (flat_mix_mmlu.nearest_assign on the leaf vmfMu, 256 slice) then the leaf's depth-d ancestor (itself if shallower).
  TC-R2 FIT SET = the tree's root region (flat_mix_mmlu.region_query_ids on the snapshots.db graph) resolved q_ + sha256(text)[:16]
        -> the split's TRAIN texts (E1-SPLIT-DRAWS' 8,171 / 8,247 / 8,269; REFUSED otherwise); hygiene by e1_split_draws.hygiene
        (fit texts not TRAIN of the split / held-out in the fit / sharing a held-out stem_key: all 0 or REFUSE). Held-out = the
        split's EVAL texts (e1sd_split_draw.draw + distinct; 3,598 / 3,522 / 3,500; REFUSED otherwise).
  TC-R3 M1 = flat_mix_mmlu.m1_block -> anchor_free_readout.score_cells (unchanged): the majority category of each cell over the FIT
        SET's texts filed by the same rule (ties to the first-seen category in fit order); a held-out text scores 1 iff its category
        equals its cell's majority (a cell with no fit text scores 0). KM: construction_arms.skm_best(X_fit, L_d, s, n_init=10)
        (k-means++, best of 10 restarts by sum of max cosine; restart r seeds s x 16 + r), every text filed to the nearest centroid.
        BKM: stability_vs_kmeans.fit_bisecting(X_fit, L_d, s) (largest cluster split first), cell centroid = normalised mean of its
        fit members, held-out to the nearest centroid.
  TC-R4 D_cut = mean over the depths d >= 2 with 4 <= L_d < L_max of [M1(tree cut d) - mean_s M1(KM_s at L_d)]; spread_KM = max -
        min over s of the depth-averaged M1(KM_s) (POINT, full held-out). INTERVAL: paired percentile bootstrap (numpy percentile,
        linear) over held-out stem_key groups (flat_mix_mmlu.twin_groups), B 1,000, default_rng(20261008): per replicate the G
        groups are drawn with replacement (rng.integers(0, G, G)), an item's weight = its group's draw count; every arm, depth and
        measure on the SAME weights; majorities, centroids and cell means are held fixed (only the held-out is resampled).
  TC-R5 TC1's bar = max(MDE80, spread_KM) with MDE80 the REGISTERED 0.0083 (Support (e)); the realised bootstrap SE and 2.8 x SE
        are printed beside and never decide. CUT-WORSE iff hi < 0 AND |D_cut| > bar; CUT-BETTER iff lo > 0 AND |D_cut| > bar;
        NEITHER otherwise. TC = the word holding on >= 2 of 3 trees (at most one can), MIXED if none. Rule 8: CUT-WORSE refuted iff
        >= 2 trees have hi >= 0 or |D_cut| <= bar. F-TC fires iff TC = CUT-BETTER.
  TC-R6 NMI (held-out category vs cell; 2 I / (H_cat + H_cell), natural log, weighted by the bootstrap weights) and R2_int in the
        same form (tree minus mean_s KM_s, depth-averaged, paired interval): DESCRIPTIVE. R2_int = resp_profile_info's statistic
        (cell_means with shrink 20, terms; unchanged) on the MMLU-Pro key of record (free_tests_f4_f7.keyed_questions: eval_results,
        the OPTIONS-key join, Meta-Llama-3-70B-Instruct excluded, key-complete questions): the 3PL (resp_structure_common.fit_train,
        guessing floor 0.10) fitted on the key-complete FIT texts; held-out item parameters with theta fixed (fit_items); cell means
        from the fit residuals; R2_int on the key-complete held-out texts (count printed). The 3PL is not re-fitted per replicate.
  TC-R7 Predictions: "X [lo, hi]" HELD iff lo <= X <= hi; P2 by the four-outcome Brier sum; P3 / P4 / P5 events by (p - event)^2;
        P4 NOT SCOREABLE when a tree has no keyed held-out text.
  NV-R1 Per tree and d in {2, 3}: k_coarse = L_d, k_fine = L_max; KM_coarse = KM_s at L_d and KM_fine = KM_s at L_max, both
        skm_best seed s (the TC fits; "seed s for both"); labels on the FIT SET = nearest centroid. V90 = share of fit items lying in
        fine clusters whose largest coarse share is < 0.90; H(coarse | fine) in bits and the off-majority share DESCRIPTIVE.
        IDENTITY: the tree (fit item's PRIMARY leaf = the leaf listing it with the largest queryWeights, ties to the smallest leaf id;
        coarse = that leaf's depth-d ancestor) and BKM (fit_bisecting at L_d vs at L_max, same seed) must read V90 = 0 exactly in
        every seed; the run REFUSES otherwise. NV1: NON-NESTED iff V90 > 0.10 on 5 of 5 seeds; NESTED iff <= 0.10 on 5 of 5; MIXED
        otherwise. NV: NON-NESTED iff >= 5 of the 6 cells NON-NESTED; NESTED iff >= 5 NESTED; MIXED otherwise. Rule 8: NON-NESTED
        refuted iff >= 2 cells are not NON-NESTED. F-NV fires iff NV = NESTED.
  NOT APPLICABLE (stated): no judge verdict (no wrong(established) count, no tie convention A / B); no call cache, --pilot or
        truncation guard (zero calls).
  DEVIATION (for the READY / registrar): TC's DESCRIPTIVE re-print of the pilot trees covers af_clean_s42 only (its p2dca held-out
        and 8,125 fit texts, FLAT-MIX-MMLU's objects); the AF-U per-benchmark re-print is NOT DONE here (it needs the union TRAIN key
        path of a different tool family; descriptive only, no criterion reads it). The [EMB-GUARD] of each tree is e1_split_draws.
        guard_tree on the tree's own qwen3 vectors (ADMIT) and on a permuted member -> text map (must REFUSE); the other-arm (nomic)
        discriminator of E1-SPLIT-DRAWS is not repeated (the nomic trees are not read here).

SELFTEST / MUTANTS: see selftest() (every deciding path EXECUTED through run() / dry_run() on fixture worlds with known answers,
VALUE asserts against an independent loop oracle) and MUTANTS (the table with results is in the commit message).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import io            # noqa: E402
import sys           # noqa: E402
import json          # noqa: E402
import math          # noqa: E402
import time          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import contextlib    # noqa: E402
import subprocess    # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import scratch_dir   # noqa: E402,F401  (temp on E:, removed at exit)
import pool_guard    # noqa: E402

TAG = "[TREE-CUT]"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def pins_of(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest(), lf16=hashlib.sha256(d).hexdigest()[:16],
                crlf16=hashlib.sha256(d.replace(b"\n", b"\r\n")).hexdigest()[:16])


# the imported instrument is the pinned one, or nothing runs (LF git blobs)
IMPORT_PINS = {"e1_split_draws.py": "0414b8fa6816ba0cf11765cad1ce5b2bc260400c",      # pins e1_readout, e1sd_split_draw, e1sd_launch
               "flat_mix_mmlu.py": "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2",       # M1 (m1_block), nearest_assign, twin_groups
               "anchor_free_readout.py": "514e74daebb5a631f65e3ed586a856a791fb5a60",  # score_cells, load_tree, corpus
               "resp_profile_info.py": "1817ec8ad607bb3b3d0abfb0116b5b2c27dd2d02",    # R2_int: cell_means, terms, shrink
               "resp_structure_common.py": "ba67f78f1580996093f020c7c348a2e704669a3c",  # the 3PL
               "construction_arms.py": "5d08a5dfb8c0cb0b5330512259b4732aa4af2dd2",    # skm_best
               "stability_vs_kmeans.py": "a67bbf0a673cffabd7dccdced95b23b11a4ac01b",  # fit_bisecting
               "intent_transfer_s0.py": "f662ceb19738f515972871f5963f5dcfc764a271",   # skmeans (under skm_best / fit_bisecting)
               "free_tests_f4_f7.py": "f0749d6133e030422671d15af69b6cff94ea1298"}     # keyed_questions
for _f, _b in IMPORT_PINS.items():
    if blob_lf(os.path.join(HERE, _f)) != _b:
        refuse("pin mismatch on tools/analysis/%s: blob:%s, pinned blob:%s" % (_f, blob_lf(os.path.join(HERE, _f)), _b))
import e1_split_draws as E1SD        # noqa: E402
import construction_arms as CA       # noqa: E402
import stability_vs_kmeans as SVK    # noqa: E402
import resp_profile_info as RPI      # noqa: E402
from scipy import sparse             # noqa: E402

FM, AF, E1R, SD, LA = E1SD.FM, E1SD.AF, E1SD.E1R, E1SD.SD, E1SD.LA
RSC = RPI.RSC
P2DCA = "p2dca21ab5f4ef3ae"

REG_TC = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — TREE-CUT-GRANULARITY: on three content-closed'
          ' MMLU-Pro re-draw trees not used in the pilot (Q_e1sd1-3), ..." L25002-L25014 (written at e83b59d5, parent d8ab39fa)')
REG_NV = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — NESTING: are two independently fitted flat'
          ' spherical k-means partitions ... nested ..." L25016-L25027 (written at e83b59d5, parent d8ab39fa)')
PILOT_SEEN = ("PILOT DISCLOSURE (registered): the 2026-10-07 exploratory numbers were SEEN, pilot role only, never evidence:"
              " E:/TaxoArena_tmp/hier_tests/granularity_free (results.json sha256 2fc8ba3a99b8dc54...), hier_tests/nesting (results.json"
              " cb5a74cf0d870081...), hier_tests/test3_fair_backoff, E:/TaxoArena_tmp/cert_split, E:/TaxoArena_tmp/scpb/"
              "review_v3_synthesis.md; the deciding trees Q_e1sd1-3 were not read by the pilot")
TREES = (dict(name="Q_e1sd1", k=1, snapshot="20261003_164959_Headless_Run_Auto_ge", pool="p5fb86f1075d76e34", leaves=80,
              heldout=3598, fit=8171, graph16="4cf9ae9803cd9911"),
         dict(name="Q_e1sd2", k=2, snapshot="20261003_165319_Headless_Run_Auto_ge", pool="p6d15d913354f256d", leaves=87,
              heldout=3522, fit=8247, graph16="f0a28baa4b632c32"),
         dict(name="Q_e1sd3", k=3, snapshot="20261003_165646_Headless_Run_Auto_ge", pool="p69d2762ac6223d93", leaves=72,
              heldout=3500, fit=8269, graph16="770780128e6852e2"))
REG = dict(trees=TREES, seeds=(0, 1, 2, 3, 4), n_init=10, B=1000, boot_seed=20261008, mde80=0.0083, se_plan=0.0030,
           spread_plan=0.010, l_min=4, v90_bar=0.10, maj=0.90, nest_depths=(2, 3), floor=0.10,
           out_dir=os.path.join("experiment_results", "tree_cut_granularity"), outcome="tree_cut_granularity_outcome.txt",
           desc=dict(name="af_clean_s42", fit=8125, leaves=82))
_REG = [REG]


def R():
    return _REG[0]


VERDICT_TC = ("(f) VERDICT LINE (registered): the predicted D_cut -0.025 lies 0.025 from 0 and 0.015 beyond max(0.0083, 0.010):"
              " SCOREABLE")
VERDICT_NV = ("(f) VERDICT LINE (registered): the predicted V90 about 0.40 lies 0.30 above 0.10, beyond the MDE80 0.056: SCOREABLE")
P_TC = dict(P1=(-0.045, -0.008), P2=(("CUT-WORSE", 0.75), ("NEITHER", 0.12), ("MIXED", 0.10), ("CUT-BETTER", 0.03)), P3=0.75,
            P4=0.70, P4_THR=0.0025, P5=0.70)
P_NV = dict(P1={2: (0.25, 0.55), 3: (0.40, 0.70)}, P2=(("NON-NESTED", 0.95), ("MIXED", 0.04), ("NESTED", 0.01)))
FTC_FIRES = ("FALSIFIER F-TC: FIRES (TC CUT-BETTER): the tree's coarse cuts are better partitions than flat k-means at the same"
             " granularity; the reading (the pilot's, and FLAT-MIX-MMLU's at the leaves) that the greedy top-down cuts cost partition"
             " quality against a flat fit at matched count is overturned")
FNV_FIRES = ("FALSIFIER F-NV: FIRES (NV NESTED): independently fitted flat k-means at these granularities nest on their own; the reading"
             " that 'flat at every granularity' needs a reconciliation step to serve as a hierarchy is overturned, and the tree's nesting"
             " does not distinguish it from flat refits")
WNS_TC = ("WILL NOT SHOW (registered): any routing, EVAL or judged quantity; anything about af_clean_s42 or AF-U (pilot-seen;"
          " descriptive); that k-means is a better taxonomy (k-means at two granularities need not nest: NESTING); other embedders or"
          " corpora; the leaf level (FLAT-MIX-MMLU, GAP-FIX-CC)")
WNS_NV = ("WILL NOT SHOW (registered): that nesting has routing or evaluation value (a property, not a value); held-out quality"
          " (TREE-CUT-GRANULARITY); that bisecting k-means is worse (it nests too); other corpora or embedders")


def say(L, s=""):
    print(s, flush=True)
    L.append(s)


def data_path(rel):
    return os.path.join(pool_guard.DATA_ROOT, rel)


def qid(text):
    return "q_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def unit_rows(M):
    M = np.asarray(M, dtype=np.float64)
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return M / n


# ── structure (TC-R1) ────────────────────────────────────────────────────────────────────────────────────────────────────
def structure(tree, label):
    """-> dict(par, depth, root, leaves, Dmax, L {d: L_d}); REFUSES a DAG node, a depth mismatch, a leaf with children."""
    byid = tree["byid"]
    par = {}
    for nid, n in byid.items():
        p = list(n.get("parentIds") or [])
        if len(p) > 1:
            refuse("%s: node %s has %d parents (a DAG; the cuts read the tree as built)" % (label, nid, len(p)))
        if p:
            if p[0] not in byid:
                refuse("%s: node %s's parent %s is not a node" % (label, nid, p[0]))
            par[nid] = p[0]
    roots = [nid for nid in byid if nid not in par]
    if len(roots) != 1:
        refuse("%s: %d roots" % (label, len(roots)))
    depth = {}
    for nid in byid:
        d, x = 0, nid
        while x in par:
            x, d = par[x], d + 1
            if d > len(byid):
                refuse("%s: a cycle through %s" % (label, nid))
        depth[nid] = d
    bad = [nid for nid, n in byid.items() if n.get("depth") is not None and int(n["depth"]) != depth[nid]]
    if bad:
        refuse("%s: %d node(s) whose depth field differs from the parent chain (first %s)" % (label, len(bad), bad[:3]))
    leaves = list(tree["leaf_ids"])
    inner = set(par.values())
    if set(leaves) & inner or set(byid) - inner != set(leaves):
        refuse("%s: the leaves are not exactly the childless nodes" % label)
    Dmax = max(depth[x] for x in leaves)
    L = {d: sum(1 for x in byid if depth[x] == d) + sum(1 for x in leaves if depth[x] < d) for d in range(1, Dmax + 1)}
    if L[Dmax] != len(leaves):
        refuse("%s: L_Dmax %d != %d leaves" % (label, L[Dmax], len(leaves)))
    return dict(par=par, depth=depth, root=roots[0], leaves=leaves, Dmax=Dmax, L=L)


def anc(S, leaf, d):
    x = leaf
    while S["depth"][x] > d:
        x = S["par"][x]
    return x


def cut_map(S, d):
    cm = {x: anc(S, x, d) for x in S["leaves"]}
    if len(set(cm.values())) != S["L"][d]:
        refuse("cut at depth %d has %d cells, L_d %d" % (d, len(set(cm.values())), S["L"][d]))
    return cm


def used_depths(S, l_min):
    Lmax = S["L"][S["Dmax"]]
    return [d for d in range(2, S["Dmax"] + 1) if l_min <= S["L"][d] < Lmax]


# ── fits and assignment rules (TC-R3) ────────────────────────────────────────────────────────────────────────────────────
def fit_km(X, k, s, n_init):
    lab, C = CA.skm_best(X, k, s, n_init=n_init)
    return dict(C=np.asarray(C, dtype=np.float64), lab=np.asarray(FM.nearest_assign(X, C), dtype=np.int64))


def fit_bkm(X, k, s):
    h = SVK.fit_bisecting(X, k, s)
    lab = np.asarray(h["lab"], dtype=np.int64)
    C = unit_rows(np.stack([X[lab == j].sum(axis=0) for j in range(int(h["L"]))]))
    return dict(C=C, lab=lab, L=int(h["L"]))


def tree_cut_fn(tree, cm):
    ids, mu = tree["leaf_ids"], tree["leaf_mu"]
    return lambda Q: [cm[ids[i]] for i in FM.nearest_assign(Q, mu)]


def cent_fn(C, tag):
    return lambda Q: ["%s%03d" % (tag, i) for i in FM.nearest_assign(Q, C)]


# ── measures ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def boot_weights(texts, B, seed):
    """TC-R4: stem_key twin groups resampled whole; -> (W (B, n) item weights, groups, G, Kish m-bar)."""
    groups, G = FM.twin_groups(texts)
    rng = np.random.default_rng(seed)
    W = np.empty((B, len(texts)), dtype=np.float64)
    for b in range(B):
        cnt = np.bincount(rng.integers(0, G, G), minlength=G).astype(np.float64)
        W[b] = cnt[groups]
    return W, groups, G, FM.kish_mbar(groups)


def nmi_w(Wb, cells, cats):
    """TC-R6: NMI = 2 I / (H_cat + H_cell) of the weighted contingency, per row of Wb (B, n) -> (B,)."""
    _u, ci = np.unique(np.asarray(cells), return_inverse=True)
    _v, gi = np.unique(np.asarray(cats), return_inverse=True)
    nc, ng = int(ci.max()) + 1, int(gi.max()) + 1
    n = len(ci)
    oh = sparse.csr_matrix((np.ones(n), (np.arange(n), ci * ng + gi)), shape=(n, nc * ng))
    M = np.asarray(oh.T.dot(np.asarray(Wb).T).T).reshape(-1, nc, ng)
    tot = M.sum(axis=(1, 2))[:, None, None]
    P = M / tot
    pr, pc = P.sum(axis=2), P.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        outer = pr[:, :, None] * pc[:, None, :]
        I = np.where(P > 0, P * np.log(P / outer), 0.0).sum(axis=(1, 2))
        H1 = -np.where(pr > 0, pr * np.log(pr), 0.0).sum(axis=1)
        H2 = -np.where(pc > 0, pc * np.log(pc), 0.0).sum(axis=1)
        out = np.where(H1 + H2 > 0, 2.0 * I / (H1 + H2), 0.0)
    return out


def irt_resid(K):
    """TC-R6: the 3PL on the key-complete fit texts; held-out item parameters with theta fixed -> (eT, eE, info)."""
    Yf, Yh = K["Yf"].astype(np.float64), K["Yh"].astype(np.float64)
    cf, ch = np.full(len(Yf), R()["floor"]), np.full(len(Yh), R()["floor"])
    ft = RSC.fit_train(Yf, cf)
    aE, bE, _it, mx = RSC.fit_items(Yh, ch, ft["theta"])
    eT = RSC.resid(Yf, RSC.prob(ft["theta"], ft["alpha"], ft["b"], cf))
    eE = RSC.resid(Yh, RSC.prob(ft["theta"], aE, bE, ch))
    return eT, eE, dict(converged=bool(ft["converged"]), iters=int(ft["iters"]))


def r2_terms(eT, eE, cells_f, cells_h):
    """resp_profile_info's R2_int pieces (cell_means with shrink, terms) -> (S_i, T_i) on the keyed held-out."""
    names = sorted(set(cells_f) | set(cells_h))
    ix = {c: j for j, c in enumerate(names)}
    gT = np.array([ix[c] for c in cells_f], dtype=np.int64)
    gE = np.array([ix[c] for c in cells_h], dtype=np.int64)
    eb = RPI.cell_means(eT, gT, len(names), np.ones(len(gT)), RPI.R()["shrink"])
    return RPI.terms(eE, gE, eb)


def nesting(coarse, fine, maj):
    """NV-R1: V90 (share of items in fine clusters whose largest coarse share is < maj), H(coarse | fine) bits, off-majority."""
    coarse, fine = np.asarray(coarse), np.asarray(fine)
    n = len(fine)
    viol = mis = 0
    H = 0.0
    for f in np.unique(fine):
        m = fine == f
        cnt = Counter(coarse[m].tolist())
        s = int(m.sum())
        top = max(cnt.values())
        if top / s < maj:
            viol += s
        mis += s - top
        H += s / n * -sum(v / s * math.log2(v / s) for v in cnt.values())
    return dict(v90=viol / n, H=H, off=mis / n)


def tc1_word(D, lo, hi, bar):
    big = bool(abs(D) > bar)
    if hi < 0 and big:
        return "CUT-WORSE"
    if lo > 0 and big:
        return "CUT-BETTER"
    return "NEITHER"


def tc_word(words):
    for w in ("CUT-WORSE", "CUT-BETTER", "NEITHER"):
        if sum(1 for x in words if x == w) >= 2:
            return w
    return "MIXED"


def nv1_word(v90s, bar):
    if all(v > bar for v in v90s):
        return "NON-NESTED"
    if all(v <= bar for v in v90s):
        return "NESTED"
    return "MIXED"


def nv_word(words):
    if sum(1 for w in words if w == "NON-NESTED") >= 5:
        return "NON-NESTED"
    if sum(1 for w in words if w == "NESTED") >= 5:
        return "NESTED"
    return "MIXED"


def brier_multi(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def brier(p, event):
    return (p - (1.0 if event else 0.0)) ** 2


def inside(x, band):
    return bool(band[0] <= x <= band[1])


def pct(x, q):
    return float(np.percentile(np.asarray(x, dtype=np.float64), q))


# ── the deciding path (compute) ──────────────────────────────────────────────────────────────────────────────────────────
def fit_plan(S, c):
    """The cell counts KM / BKM are fitted at: every TC depth's L_d, every NESTING depth's L_d, and L_max (NESTING's fine)."""
    depths = used_depths(S, c["l_min"])
    ks = sorted(set([S["L"][d] for d in depths] + [S["L"][d] for d in c["nest_depths"]] + [S["L"][S["Dmax"]]]))
    return depths, ks


def compute_tree(T, c):
    """One tree: every arm, depth and measure; TC1; the NESTING cells. -> res dict (no printing)."""
    tree, label = T["tree"], T["name"]
    S = structure(tree, label)
    depths, ks = fit_plan(S, c)
    if not depths:
        refuse("%s: no depth d >= 2 with %d <= L_d < L_max (L_d %s)" % (label, c["l_min"], S["L"]))
    Lmax = S["L"][S["Dmax"]]
    for d in c["nest_depths"]:
        if d > S["Dmax"] or not (2 <= S["L"][d] < Lmax):
            refuse("%s: NESTING depth %d undefined (L_d %s, L_max %d)" % (label, d, S["L"].get(d), Lmax))
    Xf, Xh, fit, held = T["Xf"], T["Xh"], T["fit"], T["held"]
    seeds = c["seeds"]
    km = {(k, s): fit_km(Xf, k, s, c["n_init"]) for k in ks for s in seeds}
    bkm = {(k, s): fit_bkm(Xf, k, s) for k in ks for s in seeds}
    Wb, groups, G, kish = boot_weights([t for t, _ in held], c["B"], c["boot_seed"])
    cats_h = [x for _, x in held]
    K = T.get("key")
    if K is not None and len(K["hpos"]) and len(K["fpos"]):
        eT, eE, irt = irt_resid(K)
        Tk = (eE ** 2).sum(axis=1)
        Wk = Wb[:, K["hpos"]]
    else:
        K, irt = None, None
    n = len(held)
    ones = np.ones((1, n))
    rows = []

    def arm_measures(fn):
        sc, hits, kh = FM.m1_block(fn, Xf, Xh, fit, held)
        out = dict(m1=float(hits.mean()), m1_b=(Wb @ hits) / Wb.sum(axis=1), nmi=float(nmi_w(ones, kh, cats_h)[0]),
                   nmi_b=nmi_w(Wb, kh, cats_h), cells_h=kh, untrained=sc["cells_heldout_untrained"])
        if K is not None:
            kf = fn(Xf[K["fpos"]])
            Si, _Ti = r2_terms(eT, eE, kf, [kh[j] for j in K["hpos"]])
            out["r2"] = float(1.0 - Si.sum() / Tk.sum())
            out["r2_b"] = 1.0 - (Wk @ Si) / (Wk @ Tk)
        return out
    for d in depths:
        L_d = S["L"][d]
        cm = cut_map(S, d)
        tr = arm_measures(tree_cut_fn(tree, cm))
        kms = [arm_measures(cent_fn(km[(L_d, s)]["C"], "K")) for s in seeds]
        bks = [arm_measures(cent_fn(bkm[(L_d, s)]["C"], "B")) for s in seeds]
        row = dict(d=d, L=L_d, tree=tr, km=kms, bkm=bks, bkm_L=[bkm[(L_d, s)]["L"] for s in seeds])
        for meas in ("m1", "nmi", "r2"):
            if meas == "r2" and K is None:
                continue
            row["D_" + meas] = tr[meas] - float(np.mean([x[meas] for x in kms]))
            row["D_" + meas + "_b"] = tr[meas + "_b"] - np.mean([x[meas + "_b"] for x in kms], axis=0)
            row["DB_" + meas] = tr[meas] - float(np.mean([x[meas] for x in bks]))
            row["DB_" + meas + "_b"] = tr[meas + "_b"] - np.mean([x[meas + "_b"] for x in bks], axis=0)
        rows.append(row)
    res = dict(name=label, S=S, depths=depths, ks=ks, rows=rows, n=n, G=G, kish=kish, n_fit=len(fit),
               n_keyed_h=(len(K["hpos"]) if K is not None else 0), n_keyed_f=(len(K["fpos"]) if K is not None else 0), irt=irt)
    for meas in ("m1", "nmi", "r2"):
        if meas == "r2" and K is None:
            continue
        for pre in ("D_", "DB_"):
            pt = float(np.mean([r[pre + meas] for r in rows]))
            bt = np.mean([r[pre + meas + "_b"] for r in rows], axis=0)
            res[pre + meas] = dict(pt=pt, lo=pct(bt, 2.5), hi=pct(bt, 97.5), se=float(np.std(bt, ddof=1)))
    km_avg = [float(np.mean([r["km"][j]["m1"] for r in rows])) for j in range(len(seeds))]
    res["km_avg"] = km_avg
    res["spread_km"] = float(max(km_avg) - min(km_avg))
    res["bar"] = float(max(c["mde80"], res["spread_km"]))
    dc = res["D_m1"]
    res["tc1"] = tc1_word(dc["pt"], dc["lo"], dc["hi"], res["bar"])
    res["mde_real"] = 2.8 * dc["se"]
    # NESTING (NV-R1)
    prim = T["prim"]
    nv = []
    for d in c["nest_depths"]:
        kc = S["L"][d]
        cm = cut_map(S, d)
        fine_t = [prim[j] for j in range(len(fit)) if prim[j] is not None]
        stray = sorted(set(fine_t) - set(cm))
        if stray:
            refuse("%s: %d primary leaf id(s) are not leaves of the tree as built (first %s)" % (label, len(stray), stray[:3]))
        ident_t = nesting([cm[x] for x in fine_t], fine_t, c["maj"])
        ident_b = [nesting(bkm[(kc, s)]["lab"], bkm[(Lmax, s)]["lab"], c["maj"]) for s in seeds]
        kmn = [nesting(km[(kc, s)]["lab"], km[(Lmax, s)]["lab"], c["maj"]) for s in seeds]
        v90 = [x["v90"] for x in kmn]
        nv.append(dict(d=d, kc=kc, kf=Lmax, km=kmn, v90=v90, word=nv1_word(v90, c["v90_bar"]), tree=ident_t, bkm=ident_b,
                       n_prim=len(fine_t)))
    res["nv"] = nv
    return res


def identity_check(results):
    """NV IDENTITY: the tree (primary leaf) and BKM read V90 = 0 exactly, every cell and seed; REFUSES otherwise."""
    for r in results:
        for cell in r["nv"]:
            bad = [("tree", cell["tree"]["v90"])] if cell["tree"]["v90"] != 0.0 else []
            bad += [("BKM s%d" % j, x["v90"]) for j, x in enumerate(cell["bkm"]) if x["v90"] != 0.0]
            if bad:
                refuse("[NV-IDENTITY] %s depth %d: %s read V90 != 0 (nested by construction): %s" % (r["name"], cell["d"],
                                                                                                 ", ".join(b for b, _ in bad), bad))


def compute(W, c):
    res = dict(trees=[compute_tree(T, c) for T in W["trees"]])
    res["desc"] = compute_tree(W["desc"], c) if W.get("desc") is not None else None
    identity_check(res["trees"] + ([res["desc"]] if res["desc"] is not None else []))
    return summarize(res)


def summarize(res):
    """TC, rule 8 (TC), F-TC, NV, rule 8 (NV), F-NV from the per-tree results (the selftest's synthetic results go through it too)."""
    tr = res["trees"]
    res["tc"] = tc_word([r["tc1"] for r in tr])
    res["rule8_tc_n"] = sum(1 for r in tr if r["D_m1"]["hi"] >= 0 or abs(r["D_m1"]["pt"]) <= r["bar"])
    res["ftc"] = bool(res["tc"] == "CUT-BETTER")
    cells = [cell for r in tr for cell in r["nv"]]
    res["nv"] = nv_word([cell["word"] for cell in cells])
    res["n_cells"] = len(cells)
    res["rule8_nv_n"] = sum(1 for cell in cells if cell["word"] != "NON-NESTED")
    res["fnv"] = bool(res["nv"] == "NESTED")
    return res


# ── render (every criterion, prediction and falsifier line; every branch EXECUTED by the selftest) ─────────────────────────
def f5(x):
    return "%+.5f" % x


def render(res, c):
    L = []
    L.append("=== TREE-CUT-GRANULARITY (%s) ===" % REG_TC)
    L.append(PILOT_SEEN)
    L.append("LIKE WITH LIKE: TREE = the anchor-free tree cut at depth d (flatLeaf then the depth-d ancestor; label-free) | KM = flat"
             " spherical k-means at k = L_d, seeds %s, %d restarts (label-free) | BKM = bisecting spherical k-means to L_d (descriptive);"
             " every arm fitted on the tree's own fit set in the 256 slice, scored on the tree's own held-out; labels only in the scorer"
             % ("/".join(str(s) for s in c["seeds"]), c["n_init"]))
    for r in res["trees"]:
        L.extend(tree_lines(r, c, deciding=True))
    words = [r["tc1"] for r in res["trees"]]
    L.append("TC (DECIDING; the TC1 word holding on >= 2 of 3 trees; MIXED if none): %s (TC1 words %s)" % (
        res["tc"], ", ".join("%s %s" % (r["name"], r["tc1"]) for r in res["trees"])))
    if res["rule8_tc_n"] >= 2:
        L.append("RULE 8: CUT-WORSE is REFUTED at the planned n (%d of 3 trees with UB(D_cut) >= 0 or |D_cut| <= the bar)" % res["rule8_tc_n"])
    else:
        L.append("RULE 8: CUT-WORSE is not refuted (%d of 3 trees with UB(D_cut) >= 0 or |D_cut| <= the bar; refuted at >= 2)"
                 % res["rule8_tc_n"])
    L.append(FTC_FIRES if res["ftc"] else "FALSIFIER F-TC: NOT FIRED (TC %s; F-TC fires iff TC = CUT-BETTER)" % res["tc"])
    # predictions
    for r in res["trees"]:
        ok = inside(r["D_m1"]["pt"], P_TC["P1"])
        L.append("PREDICTION P1 %s D_cut -0.025 [-0.045, -0.008]: observed %s -> %s" % (r["name"], f5(r["D_m1"]["pt"]), "HELD" if ok else "FAILED"))
    L.append("PREDICTION P2 TC CUT-WORSE 0.75, NEITHER 0.12, MIXED 0.10, CUT-BETTER 0.03: observed %s; Brier %.4f" % (
        res["tc"], brier_multi(P_TC["P2"], res["tc"])))
    e3 = bool(all(r["D_nmi"]["pt"] < 0 for r in res["trees"]))
    L.append("PREDICTION P3 (descriptive) NMI difference < 0 on 3 of 3 trees (probability 0.75): %s -> %s; Brier %.4f" % (
        ", ".join("%s %s" % (r["name"], f5(r["D_nmi"]["pt"])) for r in res["trees"]), "TRUE" if e3 else "FALSE", brier(P_TC["P3"], e3)))
    if all("D_r2" in r for r in res["trees"]):
        e4 = bool(all(abs(r["D_r2"]["pt"]) < P_TC["P4_THR"] for r in res["trees"]))
        L.append("PREDICTION P4 (descriptive) |R2_int difference| < 0.0025 on 3 of 3 trees (probability 0.70): %s -> %s; Brier %.4f" % (
            ", ".join("%s %s" % (r["name"], f5(r["D_r2"]["pt"])) for r in res["trees"]), "TRUE" if e4 else "FALSE", brier(P_TC["P4"], e4)))
    else:
        L.append("PREDICTION P4 (descriptive) |R2_int difference| < 0.0025 on 3 of 3 trees: NOT SCOREABLE (a tree has no keyed held-out text)")
    n5 = sum(1 for r in res["trees"] if r["DB_m1"]["pt"] > 0)
    e5 = bool(n5 >= 2)
    L.append("PREDICTION P5 (descriptive) tree minus BKM purity > 0 on >= 2 of 3 trees (probability 0.70): %s (%d of 3) -> %s; Brier %.4f" % (
        ", ".join("%s %s" % (r["name"], f5(r["DB_m1"]["pt"])) for r in res["trees"]), n5, "TRUE" if e5 else "FALSE", brier(P_TC["P5"], e5)))
    if res["desc"] is not None:
        L.append("DESCRIPTIVE (pilot-seen, never deciding): the pilot tree af_clean_s42 re-printed by this tool on its p2dca held-out")
        L.extend(tree_lines(res["desc"], c, deciding=False))
    L.append("DESCRIPTIVE NOT DONE: the AF-U per-benchmark re-print (declared deviation; no criterion reads it)")
    L.append("WORDS: key-scored R2_int and label-scored M1 / NMI only; no judge verdict (no wrong(established) count, no tie convention"
             " A / B); one recipe (af_clean_s42's), one corpus (MMLU-Pro), one embedder (qwen3)")
    L.append(WNS_TC)
    # NESTING
    L.append("=== NESTING (%s) ===" % REG_NV)
    L.append("SUPPORT: (a) %d tree-depth cells x %d seeds; fit items %s; (b) DEFF does not apply (V90 is deterministic given the fit set and"
             " the seed; declared); (c) n_eff = %d seeds per cell; (d) planning SE of a 5-seed mean 0.020; (e) MDE80 0.056 against the bar"
             " %.2f; %s" % (res["n_cells"], len(c["seeds"]), " / ".join("%s %d" % (r["name"], r["n_fit"]) for r in res["trees"]),
                            len(c["seeds"]), c["v90_bar"], VERDICT_NV))
    for r in res["trees"]:
        for cell in r["nv"]:
            v = cell["v90"]
            L.append("NV1 %s depth %d (k_coarse %d, k_fine %d): V90 per seed %s (mean %.4f [%.4f, %.4f]; across-seed SD %.4f) | H(coarse |"
                     " fine) bits %s | off-majority %s -> %s" % (
                         r["name"], cell["d"], cell["kc"], cell["kf"], " / ".join("%.4f" % x for x in v), float(np.mean(v)), min(v), max(v),
                         float(np.std(v, ddof=1)) if len(v) > 1 else 0.0, " / ".join("%.3f" % x["H"] for x in cell["km"]),
                         " / ".join("%.4f" % x["off"] for x in cell["km"]), cell["word"]))
            L.append("  IDENTITY %s depth %d: tree (primary leaf, %d fit items) V90 %.4f; BKM V90 %s -> nested by construction (never a"
                     " finding)" % (r["name"], cell["d"], cell["n_prim"], cell["tree"]["v90"], " / ".join("%.4f" % x["v90"] for x in cell["bkm"])))
    cw = [cell["word"] for r in res["trees"] for cell in r["nv"]]
    L.append("NV (DECIDING; over the %d tree-depth cells): %s (NON-NESTED %d, NESTED %d, MIXED %d)" % (
        res["n_cells"], res["nv"], cw.count("NON-NESTED"), cw.count("NESTED"), cw.count("MIXED")))
    if res["rule8_nv_n"] >= 2:
        L.append("RULE 8: NON-NESTED is REFUTED (%d cells not NON-NESTED; refuted at >= 2)" % res["rule8_nv_n"])
    else:
        L.append("RULE 8: NON-NESTED is not refuted (%d cells not NON-NESTED; refuted at >= 2)" % res["rule8_nv_n"])
    L.append(FNV_FIRES if res["fnv"] else "FALSIFIER F-NV: NOT FIRED (NV %s; F-NV fires iff NV = NESTED)" % res["nv"])
    for r in res["trees"]:
        for cell in r["nv"]:
            band = P_NV["P1"].get(cell["d"])
            m = float(np.mean(cell["v90"]))
            if band is None:
                L.append("PREDICTION P1 %s depth %d: no registered band" % (r["name"], cell["d"]))
                continue
            ok = inside(m, band)
            L.append("PREDICTION P1 %s depth %d V90 seed mean in [%.2f, %.2f]: observed %.4f -> %s" % (
                r["name"], cell["d"], band[0], band[1], m, "HELD" if ok else "FAILED"))
    L.append("PREDICTION P2 NV NON-NESTED 0.95, MIXED 0.04, NESTED 0.01: observed %s; Brier %.4f" % (res["nv"], brier_multi(P_NV["P2"], res["nv"])))
    if res["desc"] is not None:
        for cell in res["desc"]["nv"]:
            L.append("DESCRIPTIVE (pilot-seen) af_clean_s42 depth %d (k_coarse %d, k_fine %d): V90 per seed %s -> %s" % (
                cell["d"], cell["kc"], cell["kf"], " / ".join("%.4f" % x for x in cell["v90"]), cell["word"]))
    L.append(WNS_NV)
    return L


def tree_lines(r, c, deciding):
    L = []
    S = r["S"]
    L.append("%s %s: %d leaves, D_max %d, L_d %s; depths used (d >= 2, %d <= L_d < L_max) %s; fit %d texts; held-out %d texts in %d stem_key"
             " groups (Kish m-bar %.4f, n_eff %.0f); keyed (R2_int) fit %d / held-out %d%s" % (
                 "TREE" if deciding else "DESCRIPTIVE TREE", r["name"], len(S["leaves"]), S["Dmax"],
                 " ".join("d%d:%d" % (d, S["L"][d]) for d in sorted(S["L"])), c["l_min"], r["depths"], r["n_fit"], r["n"], r["G"],
                 r["kish"], r["n"] / r["kish"], r["n_keyed_f"], r["n_keyed_h"],
                 ("; 3PL converged %s in %d iterations" % (r["irt"]["converged"], r["irt"]["iters"])) if r["irt"] else ""))
    for row in r["rows"]:
        L.append("  %s d%d L %d | M1 tree %.5f | KM_s %s | BKM_s %s | D_m1 %s [%s, %s] | NMI tree %.4f D %s | R2_int D %s | BKM leaves %s" % (
            r["name"], row["d"], row["L"], row["tree"]["m1"], " / ".join("%.5f" % x["m1"] for x in row["km"]),
            " / ".join("%.5f" % x["m1"] for x in row["bkm"]), f5(row["D_m1"]), f5(pct(row["D_m1_b"], 2.5)),
            f5(pct(row["D_m1_b"], 97.5)), row["tree"]["nmi"], f5(row["D_nmi"]), f5(row["D_r2"]) if "D_r2" in row else "n/a",
            "/".join(str(x) for x in row["bkm_L"])))
    dc = r["D_m1"]
    L.append("  SUPPORT %s: n %d held-out (registered Support (a)), Kish %.4f (DEFF registered 1.0), n_eff %.0f; realised SE(D_cut) %.5f"
             " (registered 0.0030), realised MDE80 %.5f (registered 0.0083 decides); spread_KM %.5f (planning 0.010)%s" % (
                 r["name"], r["n"], r["kish"], r["n"] / r["kish"], dc["se"], r["mde_real"], r["spread_km"],
                 ("; " + VERDICT_TC) if deciding else ""))
    for meas, lab in (("nmi", "NMI"), ("r2", "R2_int")):
        if "D_" + meas in r:
            x, y = r["D_" + meas], r["DB_" + meas]
            L.append("  DESCRIPTIVE %s %s (depth-averaged): tree - mean_s KM_s %s [%s, %s] | tree - mean_s BKM_s %s [%s, %s]" % (
                r["name"], lab, f5(x["pt"]), f5(x["lo"]), f5(x["hi"]), f5(y["pt"]), f5(y["lo"]), f5(y["hi"])))
    y = r["DB_m1"]
    L.append("  DESCRIPTIVE %s M1 tree - mean_s BKM_s (depth-averaged) %s [%s, %s]" % (r["name"], f5(y["pt"]), f5(y["lo"]), f5(y["hi"])))
    head = "TC1" if deciding else "DESCRIPTIVE TC1-form"
    L.append("%s %s (point and 95%% interval jointly): D_cut = %s | 95%% [%s, %s] | |D_cut| %.5f vs bar max(MDE80 %.4f, spread_KM %.5f) ="
             " %.5f -> %s" % (head, r["name"], f5(dc["pt"]), f5(dc["lo"]), f5(dc["hi"]), abs(dc["pt"]), c["mde80"], r["spread_km"],
                              r["bar"], r["tc1"]))
    return L


# ── the real loader (pool lines first; every precondition) ──────────────────────────────────────────────────────────────
def guard_pair(label, byid, root, id2text, blobs):
    """[EMB-GUARD] (e1_split_draws.guard_tree, the record's arithmetic): own qwen3 vectors -> (ok, line); permuted map -> ok."""
    ok, _out, mline, err = E1SD.guard_tree(label, "Q", byid, id2text, blobs)
    ids = sorted(set(FM.region_query_ids(root, byid)))
    perm = list(np.random.default_rng(12345).permutation(len(ids)))
    shuffled = {ids[i]: id2text[ids[j]] for i, j in zip(range(len(ids)), perm)}
    ok_p, _o, ml_p, _e = E1SD.guard_tree(label + " x PERMUTED map", "Q", byid, shuffled, blobs)
    return ok, ok_p, "%s | permuted %s" % (mline, ml_p), err


def primary_leaf(gbyid):
    """NV-R1: fit qid -> the leaf listing it with the largest queryWeights (ties: the smallest leaf id)."""
    best = {}
    for nid in sorted(gbyid):
        n = gbyid[nid]
        if n.get("childIds"):
            continue
        w = n.get("queryWeights") or {}
        for q in n.get("queryIds") or []:
            x = float(w.get(q, 1.0))
            if q not in best or x > best[q][0]:
                best[q] = (x, nid)
    return {q: v[1] for q, v in best.items()}


def keyed_index(texts_f, texts_h, keyed):
    """The MMLU-Pro key of record (free_tests_f4_f7.keyed_questions) on the fit and held-out texts -> K dict (or None)."""
    models, G, _cat, text, qs = keyed
    by_text = {}
    for q in qs:
        by_text.setdefault(text[q], []).append(q)
    fpos = [j for j, t in enumerate(texts_f) if t in by_text]
    hpos = [j for j, t in enumerate(texts_h) if t in by_text]
    multi = sum(1 for t in set(texts_f) | set(texts_h) if len(by_text.get(t, [])) > 1)
    Yf = np.array([[G[m][sorted(by_text[texts_f[j]])[0]] for m in models] for j in fpos], dtype=np.int64).reshape(len(fpos), len(models))
    Yh = np.array([[G[m][sorted(by_text[texts_h[j]])[0]] for m in models] for j in hpos], dtype=np.int64).reshape(len(hpos), len(models))
    return dict(fpos=np.array(fpos, dtype=np.int64), hpos=np.array(hpos, dtype=np.int64), Yf=Yf, Yh=Yh, models=list(models), multi=multi)


def admit(W, L, c):
    """Shared by the real and the fixture worlds: registered counts, run-dir leaves == graph leaves, the guard (own ADMIT, permuted
    REFUSE), hygiene. REFUSES on any finding."""
    for T, spec in zip(W["trees"], c["trees"]):
        lab = T["name"]
        if lab != spec["name"]:
            refuse("tree order: %s where %s is registered" % (lab, spec["name"]))
        got = dict(leaves=len(T["tree"]["leaf_ids"]), heldout=len(T["held"]), fit=len(T["fit"]))
        want = dict(leaves=spec["leaves"], heldout=spec["heldout"], fit=spec["fit"])
        if got != want:
            refuse("%s: %s, registered / E1-SPLIT-DRAWS build facts %s" % (lab, got, want))
        gl = {k: n for k, n in T["graph"]["byid"].items() if not n.get("childIds")}
        if set(gl) != set(T["tree"]["leaf_ids"]):
            refuse("%s: snapshot graph leaves != run dir leaves (%d vs %d)" % (lab, len(gl), len(T["tree"]["leaf_ids"])))
        ok, ok_p, line, err = T["guard"]()
        say(L, "[EMB-GUARD] %s: own qwen3 vectors %s; permuted member->text map %s (%s)" % (
            lab, "ADMIT" if ok else "REFUSE", "REFUSE (expected)" if not ok_p else "ADMIT", line))
        if not ok:
            refuse("[EMB-GUARD] %s on its own qwen3 vectors: %s" % (lab, err))
        if ok_p:
            refuse("[EMB-GUARD] %s: the permuted-map discriminator was ADMITTED: the guard does not discriminate" % lab)
        E1SD.hygiene(lab, set(t for t, _ in T["fit"]), T["split_train"], T["held"], L)
        miss = sum(1 for p in T["prim"] if p is None)
        say(L, "STRUCTURE %s: fit texts without a primary leaf %d (NESTING's tree identity reads the others)" % (lab, miss))


def load_real(L):
    c = R()
    corpus_db = data_path(SD.CORPUS_DB)
    for spec in c["trees"]:
        sp = os.path.join(ROOT, *(SD.SPLIT_REL % spec["k"]).split("/"))
        pid = pool_guard.assert_pool_of_record(spec["pool"], db=corpus_db, id_file=sp)
        say(L, "POOL %s (split e1sd%d, %s; pool_guard.assert_pool_of_record passed; NEVER a pool of record; TREE-CUT-GRANULARITY /"
               " NESTING)" % (pid, spec["k"], spec["name"]))
    pid = pool_guard.assert_pool_of_record(P2DCA)
    say(L, "POOL %s (af_clean_s42's held-out, the DESCRIPTIVE pilot tree only)" % pid)
    say(L, "[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    p = pins_of(os.path.abspath(__file__))
    say(L, "[SCRIPT] tools/analysis/tree_cut_granularity.py blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (p["blob"], p["lf16"], p["crlf16"]))
    for f_ in IMPORT_PINS:
        say(L, "[PIN] tools/analysis/%s blob:%s (verified)" % (f_, IMPORT_PINS[f_]))
    say(L, "[DATA] DATA_ROOT %s; calls 0" % pool_guard.DATA_ROOT)
    con = pool_guard.open_ro(corpus_db)
    try:
        rows = SD.corpus_rows(con)
    finally:
        con.close()
    texts = sorted(set(r["text"] for r in rows))
    id2text = {qid(t): t for t in texts}
    W = dict(trees=[], desc=None)
    vec, blobs, _miss, info = E1R.load_space("qwen3_raw", set(texts), L)
    E1R.point_eval_db(corpus_db)
    keyed = FM.F.keyed_questions()
    say(L, "KEY (R2_int only; free_tests_f4_f7.keyed_questions on %s): %d models (Meta-Llama-3-70B-Instruct excluded), %d key-complete"
           " questions" % (SD.CORPUS_DB, len(keyed[0]), len(keyed[4])))
    for spec in c["trees"]:
        k = spec["k"]
        d = SD.draw(rows, SD.SALTS[k - 1])
        sp = os.path.join(ROOT, *(SD.SPLIT_REL % k).split("/"))
        if blob_lf(sp) != LA.SPLIT_BLOBS[k] or d["pool"] != spec["pool"] or d["pool"] != LA.SPLIT_POOLS[k]:
            refuse("split %d: file / re-derived pool %s differ from the declared blob / pool %s" % (k, d["pool"], spec["pool"]))
        with open(sp, "rb") as f:
            if f.read().replace(b"\r\n", b"\n") != SD.file_bytes(d["ids"]):
                refuse("split %d: the committed file is not the re-derived split" % k)
        train, held = SD.distinct(d["train"]), SD.distinct(d["held"])
        rd = SD.run_dir_of("Q", k, pool_guard.DATA_ROOT)
        got = SD.check_run_dir(rd, "Q", k, d, LA.DECLARED[spec["name"]])
        if got["snapshot"] != spec["snapshot"]:
            refuse("%s: snapshot %s, registered %s" % (spec["name"], got["snapshot"], spec["snapshot"]))
        tree = AF.load_tree(rd)
        if tree["dim"] != E1SD.DIM:
            refuse("%s: slice %d" % (spec["name"], tree["dim"]))
        graph = FM.load_snapshot_graph(spec["snapshot"])
        if graph["sha"][:16] != spec["graph16"]:
            refuse("%s: snapshot graph sha256 %s, E1-SPLIT-DRAWS printed %s" % (spec["name"], graph["sha"][:16], spec["graph16"]))
        fit_ids = FM.region_query_ids(graph["root"], graph["byid"])
        un = [q for q in fit_ids if q not in id2text]
        if un:
            refuse("%s: %d member id(s) resolve to no corpus text (first %s)" % (spec["name"], len(un), un[:3]))
        cat_tr = dict(train)
        fit_texts = sorted(set(id2text[q] for q in fit_ids))
        out_tr = [t for t in fit_texts if t not in cat_tr]
        fit = [(t, cat_tr.get(t, "")) for t in fit_texts]
        pl = primary_leaf(graph["byid"])
        prim = [pl.get(qid(t)) for t in fit_texts]
        say(L, "TREE %s: run dir %s | snapshot %s (graph sha256-16 %s) | %d leaves | fit %d texts (%d not TRAIN of the split) | held-out %d"
            % (spec["name"], rd, spec["snapshot"], graph["sha"][:16], len(tree["leaf_ids"]), len(fit), len(out_tr), len(held)))
        T = dict(name=spec["name"], tree=tree, graph=graph, fit=fit, held=held, split_train=train, prim=prim,
                 Xf=E1R.mat(vec, fit_texts), Xh=E1R.mat(vec, [t for t, _ in held]),
                 key=keyed_index(fit_texts, [t for t, _ in held], keyed),
                 guard=(lambda g=graph, lab=spec["name"]: guard_pair(lab, g["byid"], g["root"], id2text, blobs)))
        W["trees"].append(T)
    # the descriptive pilot tree (af_clean_s42; FLAT-MIX-MMLU's objects)
    E1R.point_eval_db(corpus_db)
    atrain, aheld, _cs = AF.corpus(P2DCA)
    atree = FM.load_T("T")
    agraph = FM.load_snapshot_graph(FM.T_SNAPSHOT)
    afit_texts = sorted(set(id2text[q] for q in FM.region_query_ids(agraph["root"], agraph["byid"]) if q in id2text))
    FM.assert_fit_count(len(afit_texts), c["desc"]["fit"])
    acat = dict(atrain)
    E1SD.hygiene("af_clean_s42 (descriptive)", set(afit_texts), atrain, aheld, L)
    apl = primary_leaf(agraph["byid"])
    W["desc"] = dict(name="af_clean_s42", tree=atree, graph=agraph, fit=[(t, acat.get(t, "")) for t in afit_texts], held=aheld,
                     prim=[apl.get(qid(t)) for t in afit_texts], Xf=E1R.mat(vec, afit_texts), Xh=E1R.mat(vec, [t for t, _ in aheld]),
                     key=keyed_index(afit_texts, [t for t, _ in aheld], keyed))
    say(L, "DESCRIPTIVE TREE af_clean_s42 (snapshot %s): %d leaves, fit %d, held-out %d (p2dca)" % (
        FM.T_SNAPSHOT, len(atree["leaf_ids"]), len(afit_texts), len(aheld)))
    return W


# ── modes ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def plan_lines(W, L, c):
    nfit = 0
    for T in W["trees"] + ([W["desc"]] if W.get("desc") else []):
        S = structure(T["tree"], T["name"])
        depths, ks = fit_plan(S, c)
        nfit += len(ks) * len(c["seeds"])
        K = T.get("key")
        say(L, "PLAN %s: L_d %s | TC depths %s (L %s) | NESTING cells %s | KM / BKM at k %s x seeds %s | keyed fit %d / held-out %d" % (
            T["name"], " ".join("d%d:%d" % (d, S["L"][d]) for d in sorted(S["L"])), depths, [S["L"][d] for d in depths],
            ["d%d %d vs %d" % (d, S["L"][d], S["L"][S["Dmax"]]) for d in c["nest_depths"]], ks,
            "/".join(str(s) for s in c["seeds"]), len(K["fpos"]) if K else 0, len(K["hpos"]) if K else 0))
    say(L, "COST: 0 calls; %d spherical k-means fits x %d restarts + %d bisecting fits + %d 3PL fits + B %d bootstrap; CPU on one thread"
        % (nfit, c["n_init"], nfit, len(W["trees"]) + (1 if W.get("desc") else 0), c["B"]))


def dry_run(loader, L=None):
    c = R()
    L = [] if L is None else L
    W = loader(L)
    admit(W, L, c)
    plan_lines(W, L, c)
    say(L, "[MODE] --dry-run: pools, pins, splits, run dirs, graphs, guards, hygiene, structure, keyed counts; NO fit, NO statistic;"
           " nothing written")
    return 0


def write_once(path, text):
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def run(loader, out_dir, L=None):
    c = R()
    L = [] if L is None else L
    oc = os.path.join(out_dir, c["outcome"])
    if os.path.exists(oc):
        refuse("%s exists: the outcome of record is write-once" % oc)
    t0 = time.process_time()
    W = loader(L)
    admit(W, L, c)
    plan_lines(W, L, c)
    res = compute(W, c)
    for line in render(res, c):
        say(L, line)
    say(L, "%s CPU %.1f s; zero calls" % (TAG, time.process_time() - t0))
    os.makedirs(out_dir, exist_ok=True)
    write_once(oc, "\n".join(L) + "\n")
    say(L, "%s outcome written (write-once): %s (sha256 %s; never committed: back up to E: with SHA256SUMS.txt)" % (TAG, oc, _sha_file(oc)))
    return res


def _sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(quiet=a.quiet)
    if a.mutants:
        return run_mutants()
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    try:
        if a.dry_run:
            return dry_run(load_real)
        run(load_real, data_path(R()["out_dir"]))
        return 0
    except SystemExit as e:
        if isinstance(e.code, int):
            return e.code
        return 2


# ══ SELFTEST ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════
# Fixture worlds (no DB of record): three synthetic trees per world on the 16-d sphere. 4 categories x 2 subclusters x 2 leaves =
# 16 leaves; depth 1: 2 nodes, depth 2: 4 nodes, depth 3: 8 subclusters, depth 4: 16 leaves (L_d 2 / 4 / 8 / 16; TC depths 2, 3;
# NESTING cells d2 (4 vs 16) and d3 (8 vs 16)). Geometry NEAR: a category's two subclusters sit together; FAR: each spatial group
# holds subcluster 0 of category g and subcluster 1 of category g + 1. Kinds: "bad" (NEAR, depth-2 nodes cross categories: the cut
# is impure where k-means at 4 is pure -> CUT-WORSE), "good" (NEAR, depth-2 = categories -> NEITHER), "better" (FAR, depth-2 =
# categories where k-means at 4 finds the spatial groups -> CUT-BETTER), "diffuse" (random leaf directions, wide noise, random
# categories; k-means boundaries at 4 / 8 and 16 disagree -> NON-NESTED; restarts and seeds matter).
import tempfile      # noqa: E402
import shutil        # noqa: E402
import split_side    # noqa: E402

FX_DIM = 16
FX_MODELS = ["m0", "m1", "m2", "m3", "m4", "m5"]
_FXC = {}


def _e(i):
    v = np.zeros(FX_DIM)
    v[i] = 1.0
    return v


def _fx_tree(kind, tag, seed, n_fit=30, n_held=12, twins=3, keyed=False):
    key = (kind, tag, seed, n_fit, n_held, twins, keyed)
    if key in _FXC:
        return _FXC[key]
    rng = np.random.default_rng(seed)
    leaf_c, leaf_cat, sub_of = [], [], []
    for sc in range(8):
        k, j = sc // 2, sc % 2
        if kind in ("bad", "good"):
            sub = _e(k) + 0.6 * _e(4 + sc)
        elif kind == "better":
            g = k if j == 0 else (k - 1) % 4
            sub = _e(g) + 0.6 * _e(4 + sc)
        else:
            sub = rng.normal(size=FX_DIM)
        sub = sub / np.linalg.norm(sub)
        for i in (0, 1):
            lc = (sub + (0.3 if i == 0 else -0.3) * _e(12 + sc % 4)) if kind != "diffuse" else rng.normal(size=FX_DIM)
            leaf_c.append(lc / np.linalg.norm(lc))
            leaf_cat.append("cat%d" % k)
            sub_of.append(sc)
    if kind == "bad":
        d2 = {sc: (sc // 2 if sc % 2 == 0 else ((sc // 2) - 1) % 4) for sc in range(8)}     # sub 0 of cat k with sub 1 of cat k - 1
    else:
        d2 = {sc: sc // 2 for sc in range(8)}
    nodes = [dict(id="root", parentIds=[], childIds=["a0", "a1"], depth=0, isLeaf=False)]
    nodes += [dict(id="a%d" % a, parentIds=["root"], childIds=["b%d" % b for b in range(4) if b // 2 == a], depth=1, isLeaf=False)
              for a in (0, 1)]
    nodes += [dict(id="b%d" % b, parentIds=["a%d" % (b // 2)], childIds=["c%d" % sc for sc in range(8) if d2[sc] == b], depth=2,
                   isLeaf=False) for b in range(4)]
    nodes += [dict(id="c%d" % sc, parentIds=["b%d" % d2[sc]], childIds=["l%02d" % (2 * sc), "l%02d" % (2 * sc + 1)], depth=3,
                   isLeaf=False) for sc in range(8)]
    nodes += [dict(id="l%02d" % lf, parentIds=["c%d" % sub_of[lf]], childIds=[], depth=4, isLeaf=True, vmfMu=leaf_c[lf].tolist())
              for lf in range(16)]
    byid = {n["id"]: n for n in nodes}
    leaf_ids = ["l%02d" % lf for lf in range(16)]
    tree = dict(byid=byid, leaf_ids=leaf_ids, leaf_mu=unit_rows(np.stack(leaf_c)), dim=FX_DIM, leaves=[byid[x] for x in leaf_ids])
    noise = 0.05 if kind != "diffuse" else 0.6

    def cat_of(lf):
        return leaf_cat[lf] if kind != "diffuse" else "cat%d" % int(rng.integers(0, 4))

    def pts(lf, n):
        return unit_rows(leaf_c[lf][None, :] + noise * rng.normal(size=(n, FX_DIM)))
    fit, held, Xf, Xh, fleaf = [], [], [], [], []
    for lf in range(16):
        P = pts(lf, n_fit)
        for i in range(n_fit):
            fit.append(("fit %s %s leaf %d item %d" % (tag, kind, lf, i), cat_of(lf)))
            Xf.append(P[i])
            fleaf.append(lf)
        Q = pts(lf, n_held)
        hc = [cat_of(lf) for _ in range(n_held)]
        for i in range(n_held):
            held.append(("held %s %s leaf %d item %d" % (tag, kind, lf, i), hc[i]))
            Xh.append(Q[i])
        for i in range(min(twins, n_held)):          # stem_key twins: the same text with a doubled space (one group of 2)
            held.append(("held  %s %s leaf %d item %d" % (tag, kind, lf, i), hc[i]))
            Xh.append(Q[i])
    order = sorted(range(len(fit)), key=lambda j: fit[j][0])
    fit = [fit[j] for j in order]
    Xf = np.stack([Xf[j] for j in order])
    fleaf = [fleaf[j] for j in order]
    Xh = np.stack(Xh)
    # graph: every fit text listed in its generating leaf (weight 1.0); every 7th also in the sibling leaf (weight 0.4)
    gby = {k: dict(v, queryIds=[], queryWeights={}) for k, v in byid.items()}
    for j, (t, _c) in enumerate(fit):
        q = qid(t)
        lf = "l%02d" % fleaf[j]
        gby[lf]["queryIds"].append(q)
        gby[lf]["queryWeights"][q] = 1.0
        if j % 7 == 0:
            sib = "l%02d" % (fleaf[j] ^ 1)
            gby[sib]["queryIds"].append(q)
            gby[sib]["queryWeights"][q] = 0.4
    graph = dict(byid=gby, root="root", sha="0" * 64)
    pl = primary_leaf(gby)
    T = dict(name=tag, tree=tree, graph=graph, fit=fit, held=held, split_train=list(fit), Xf=Xf, Xh=Xh,
             prim=[pl.get(qid(t)) for t, _ in fit], gen=dict(fleaf=fleaf, d2=d2, sub_of=sub_of),
             guard=lambda: (True, False, "stub own ADMIT / permuted REFUSE", None), key=None)
    if keyed:
        th = np.linspace(-1.2, 1.2, len(FX_MODELS))

        def ycat(cat, r):
            k = int(cat[3:])
            return [int(r.random() < 0.1 + 0.9 / (1 + math.exp(-(th[m] + (2.0 if m == k + 1 else 0.0) - 0.3))))
                    for m in range(len(FX_MODELS))]
        r2 = np.random.default_rng(seed + 99)
        fpos = np.array([j for j in range(len(fit)) if j % 5 != 0], dtype=np.int64)
        hpos = np.array([j for j in range(len(held)) if j % 4 != 0], dtype=np.int64)
        T["key"] = dict(fpos=fpos, hpos=hpos, Yf=np.array([ycat(fit[j][1], r2) for j in fpos], dtype=np.int64),
                        Yh=np.array([ycat(held[j][1], r2) for j in hpos], dtype=np.int64), models=FX_MODELS, multi=0)
    _FXC[key] = T
    return T


def _world(kinds, keyed=(False, False, False), base_seed=11):
    return dict(trees=[dict(_fx_tree(kind, "FX%d" % (i + 1), base_seed + 7 * i, keyed=keyed[i])) for i, kind in enumerate(kinds)],
                desc=None)


def _fx_reg(W, **over):
    trees = tuple(dict(name=T["name"], k=i + 1, snapshot="s", pool="p", leaves=len(T["tree"]["leaf_ids"]), heldout=len(T["held"]),
                       fit=len(T["fit"]), graph16="g") for i, T in enumerate(W["trees"]))
    return dict(REG, trees=trees, desc=None, **over)


@contextlib.contextmanager
def _reg(c):
    saved = _REG[0]
    _REG[0] = c
    try:
        yield
    finally:
        _REG[0] = saved


def _go(fn):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = fn()
        return r, buf.getvalue(), ""
    except SystemExit as e:
        return "REFUSED", buf.getvalue(), str(e)


# ── the independent oracle (plain loops; the generator's own ancestry, never structure()) ─────────────────────────────────
def _o_cells_tree(T, X, d):
    gen = T["gen"]
    mu = T["tree"]["leaf_mu"]
    out = []
    for x in X:
        sims = [float(np.dot(x, mu[j])) for j in range(len(mu))]
        lf = max(range(len(sims)), key=lambda j: (sims[j], -j))
        sc = gen["sub_of"][lf]
        out.append({1: "a%d" % (gen["d2"][sc] // 2), 2: "b%d" % gen["d2"][sc], 3: "c%d" % sc, 4: "l%02d" % lf}[d])
    return out


def _o_cells_cent(C, X):
    Cn = [C[j] / (np.linalg.norm(C[j]) or 1.0) for j in range(len(C))]
    return [max(range(len(Cn)), key=lambda j: (float(np.dot(x, Cn[j])), -j)) for x in X]


def _o_major(cells_f, fit):
    cnt, first = {}, {}
    for (t, c_), k in zip(fit, cells_f):
        cnt.setdefault(k, {})
        if c_ not in cnt[k]:
            cnt[k][c_] = 0
            first.setdefault(k, []).append(c_)
        cnt[k][c_] += 1
    return {k: max(first[k], key=lambda c_: (cnt[k][c_], -first[k].index(c_))) for k in cnt}


def _o_hits(cells_f, cells_h, fit, held):
    maj = _o_major(cells_f, fit)
    return np.array([1.0 if maj.get(k) == c_ else 0.0 for k, (_t, c_) in zip(cells_h, held)])


def _o_weights(held, B, seed):
    keys = [split_side.stem_key(t) for t, _ in held]
    gid = {}
    groups = [gid.setdefault(k, len(gid)) for k in keys]
    G = len(gid)
    rng = np.random.default_rng(seed)
    Wb = []
    for _b in range(B):
        draws = rng.integers(0, G, G)
        cnt = [0] * G
        for g in draws:
            cnt[int(g)] += 1
        Wb.append([cnt[g] for g in groups])
    sizes = list(Counter(groups).values())
    kish = sum(s * s for s in sizes) / sum(sizes)
    return np.array(Wb, dtype=np.float64), G, kish


def _o_nmi(cells, cats, w):
    tot = float(sum(w))
    joint, pr, pc = {}, {}, {}
    for a, b, x in zip(cells, cats, w):
        joint[(a, b)] = joint.get((a, b), 0.0) + x
        pr[a] = pr.get(a, 0.0) + x
        pc[b] = pc.get(b, 0.0) + x
    I = sum((v / tot) * math.log((v / tot) / ((pr[a] / tot) * (pc[b] / tot))) for (a, b), v in joint.items() if v > 0)
    H1 = -sum((v / tot) * math.log(v / tot) for v in pr.values() if v > 0)
    H2 = -sum((v / tot) * math.log(v / tot) for v in pc.values() if v > 0)
    return 2 * I / (H1 + H2) if H1 + H2 > 0 else 0.0


def _o_v90(coarse, fine, maj=0.90):
    by = {}
    for a, b in zip(coarse, fine):
        by.setdefault(b, []).append(a)
    viol = 0
    for b, cs in by.items():
        if max(Counter(cs).values()) / len(cs) < maj:
            viol += len(cs)
    return viol / len(fine)


def _oracle(W, c):
    """Per tree: D_cut point and 95% interval, SE, spread_KM, bar, TC1; NMI D; BKM D; R2_int D; V90 per cell and seed; TC / NV."""
    out = []
    for T in W["trees"]:
        fit, held, Xf, Xh = T["fit"], T["held"], T["Xf"], T["Xh"]
        Wb, G, kish = _o_weights(held, c["B"], c["boot_seed"])
        kms = {(k, s): CA.skm_best(Xf, k, s, n_init=c["n_init"])[1] for k in (4, 8, 16) for s in c["seeds"]}
        bk = {}
        for k in (4, 8):
            for s in c["seeds"]:
                lab = np.asarray(SVK.fit_bisecting(Xf, k, s)["lab"])
                bk[(k, s)] = np.stack([Xf[lab == j].sum(axis=0) for j in range(int(lab.max()) + 1)])
        cats = [x for _, x in held]
        per = {}
        for d, k in ((2, 4), (3, 8)):
            cells_t = _o_cells_tree(T, Xh, d)
            per[d] = dict(t=_o_hits(_o_cells_tree(T, Xf, d), cells_t, fit, held),
                          k=[_o_hits(_o_cells_cent(kms[(k, s)], Xf), _o_cells_cent(kms[(k, s)], Xh), fit, held) for s in c["seeds"]],
                          b=[_o_hits(_o_cells_cent(bk[(k, s)], Xf), _o_cells_cent(bk[(k, s)], Xh), fit, held) for s in c["seeds"]],
                          nmi_t=_o_nmi(cells_t, cats, [1.0] * len(cats)),
                          nmi_k=[_o_nmi(_o_cells_cent(kms[(k, s)], Xh), cats, [1.0] * len(cats)) for s in c["seeds"]])
        pt = float(np.mean([per[d]["t"].mean() - np.mean([h.mean() for h in per[d]["k"]]) for d in (2, 3)]))
        reps = []
        for b in range(c["B"]):
            w = Wb[b]
            reps.append(np.mean([float(w @ per[d]["t"]) / w.sum() - np.mean([float(w @ h) / w.sum() for h in per[d]["k"]]) for d in (2, 3)]))
        lo, hi = float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))
        km_avg = [np.mean([per[d]["k"][j].mean() for d in (2, 3)]) for j in range(len(c["seeds"]))]
        spread = float(max(km_avg) - min(km_avg))
        bar = max(c["mde80"], spread)
        big = abs(pt) > bar
        word = "CUT-WORSE" if (hi < 0 and big) else ("CUT-BETTER" if (lo > 0 and big) else "NEITHER")
        r = dict(name=T["name"], D=pt, lo=lo, hi=hi, se=float(np.std(reps, ddof=1)), spread=spread, bar=bar, word=word,
                 dnmi=float(np.mean([per[d]["nmi_t"] - np.mean(per[d]["nmi_k"]) for d in (2, 3)])),
                 dbkm=float(np.mean([per[d]["t"].mean() - np.mean([h.mean() for h in per[d]["b"]]) for d in (2, 3)])), G=G, kish=kish)
        if T["key"] is not None:
            K = T["key"]
            Yf, Yh = K["Yf"].astype(float), K["Yh"].astype(float)
            cf, ch = np.full(len(Yf), 0.10), np.full(len(Yh), 0.10)
            ft = RSC.fit_train(Yf, cf)
            aE, bE, _i, _m = RSC.fit_items(Yh, ch, ft["theta"])
            eT = RSC.resid(Yf, RSC.prob(ft["theta"], ft["alpha"], ft["b"], cf))
            eE = RSC.resid(Yh, RSC.prob(ft["theta"], aE, bE, ch))

            def r2(cf_, chh):
                sums, cnt = {}, {}
                for row, cc in zip(eT, cf_):
                    sums[cc] = sums.get(cc, 0.0) + row
                    cnt[cc] = cnt.get(cc, 0) + 1
                num = den = 0.0
                for row, cc in zip(eE, chh):
                    eb = sums[cc] / (cnt[cc] + 20.0) if cc in sums else np.zeros(len(row))
                    num += float(((row - eb) ** 2).sum())
                    den += float((row ** 2).sum())
                return 1.0 - num / den
            dr = []
            for d, k in ((2, 4), (3, 8)):
                rt = r2(_o_cells_tree(T, Xf[K["fpos"]], d), _o_cells_tree(T, Xh[K["hpos"]], d))
                rk = [r2(_o_cells_cent(kms[(k, s)], Xf[K["fpos"]]), _o_cells_cent(kms[(k, s)], Xh[K["hpos"]])) for s in c["seeds"]]
                dr.append(rt - np.mean(rk))
            r["dr2"] = float(np.mean(dr))
        nv = []
        for d, kc in ((2, 4), (3, 8)):
            v = [_o_v90(_o_cells_cent(kms[(kc, s)], Xf), _o_cells_cent(kms[(16, s)], Xf)) for s in c["seeds"]]
            nv.append(dict(d=d, v90=v, word="NON-NESTED" if all(x > 0.10 for x in v) else ("NESTED" if all(x <= 0.10 for x in v) else "MIXED")))
        r["nv"] = nv
        out.append(r)
    words = [r["word"] for r in out]
    tc = next((w for w in ("CUT-WORSE", "CUT-BETTER", "NEITHER") if words.count(w) >= 2), "MIXED")
    cw = [x["word"] for r in out for x in r["nv"]]
    nvw = "NON-NESTED" if cw.count("NON-NESTED") >= 5 else ("NESTED" if cw.count("NESTED") >= 5 else "MIXED")
    return dict(trees=out, tc=tc, nv=nvw, r8tc=sum(1 for r in out if r["hi"] >= 0 or abs(r["D"]) <= r["bar"]),
                r8nv=sum(1 for w in cw if w != "NON-NESTED"))


def _num(text, pat):
    import re
    m = re.search(pat, text)
    if not m:
        raise AssertionError("no line %r" % pat)
    return [float(x) for x in m.groups()]


def _need(text, *needles):
    for n in needles:
        if n not in text:
            raise AssertionError("missing %r" % n[:200])


BRIER_TC = {"CUT-WORSE": 0.25 ** 2 + 0.12 ** 2 + 0.10 ** 2 + 0.03 ** 2, "NEITHER": 0.75 ** 2 + 0.88 ** 2 + 0.10 ** 2 + 0.03 ** 2,
            "MIXED": 0.75 ** 2 + 0.12 ** 2 + 0.90 ** 2 + 0.03 ** 2, "CUT-BETTER": 0.75 ** 2 + 0.12 ** 2 + 0.10 ** 2 + 0.97 ** 2}
BRIER_NV = {"NON-NESTED": 0.05 ** 2 + 0.04 ** 2 + 0.01 ** 2, "MIXED": 0.95 ** 2 + 0.96 ** 2 + 0.01 ** 2,
            "NESTED": 0.95 ** 2 + 0.04 ** 2 + 0.99 ** 2}


def _e2e(kinds, keyed=(False, False, False), expect_tc=None, expect_nv=None):
    """run() on a fixture world; every deciding number against the oracle, the words against the oracle AND the design."""
    W = _world(kinds, keyed)
    c = _fx_reg(W)
    td = tempfile.mkdtemp(prefix="tcg_st_")
    try:
        with _reg(c):
            res, text, err = _go(lambda: run(lambda L: W, td))
        assert err == "", err
        oc = os.path.join(td, c["outcome"])
        out = open(oc, encoding="utf-8").read()
        o = _oracle(W, c)
        for r in o["trees"]:
            p_, lo, hi = _num(out, r"\nTC1 %s \(point and 95%% interval jointly\): D_cut = ([+-][0-9.]+) \| 95%% \[([+-][0-9.]+), ([+-][0-9.]+)\]"
                              % r["name"])
            assert abs(p_ - r["D"]) < 6e-6 and abs(lo - r["lo"]) < 6e-6 and abs(hi - r["hi"]) < 6e-6, (r["name"], p_, lo, hi, r)
            sp, bar = _num(out, r"\nTC1 %s .*spread_KM ([0-9.]+)\) = ([0-9.]+) ->" % r["name"])
            assert abs(sp - r["spread"]) < 6e-6 and abs(bar - r["bar"]) < 6e-6, (sp, bar, r)
            line = [x for x in out.splitlines() if x.startswith("TC1 %s " % r["name"])][0]
            assert line.endswith("-> " + r["word"]), (line, r["word"])
            se, = _num(out, r"SUPPORT %s: .*realised SE\(D_cut\) ([0-9.]+) " % r["name"])
            assert abs(se - r["se"]) < 6e-6, (se, r["se"])
            g_, kish = _num(out, r"\nTREE %s: .* in (\d+) stem_key groups \(Kish m-bar ([0-9.]+)," % r["name"])
            assert int(g_) == r["G"] and abs(kish - r["kish"]) < 6e-5, (g_, kish, r)
            dn, = _num(out, r"DESCRIPTIVE %s NMI \(depth-averaged\): tree - mean_s KM_s ([+-][0-9.]+) " % r["name"])
            assert abs(dn - r["dnmi"]) < 6e-6, (dn, r["dnmi"])
            db, = _num(out, r"DESCRIPTIVE %s M1 tree - mean_s BKM_s \(depth-averaged\) ([+-][0-9.]+) " % r["name"])
            assert abs(db - r["dbkm"]) < 6e-6, (db, r["dbkm"])
            if "dr2" in r:
                d2, = _num(out, r"DESCRIPTIVE %s R2_int \(depth-averaged\): tree - mean_s KM_s ([+-][0-9.]+) " % r["name"])
                assert abs(d2 - r["dr2"]) < 6e-6, (d2, r["dr2"])
            for cell in r["nv"]:
                line = [x for x in out.splitlines() if x.startswith("NV1 %s depth %d " % (r["name"], cell["d"]))][0]
                got = [float(x) for x in line.split("V90 per seed ")[1].split(" (mean")[0].split(" / ")]
                assert len(got) == len(cell["v90"]) and all(abs(a - b) < 6e-5 for a, b in zip(got, cell["v90"])), (line, cell)
                assert line.endswith("-> " + cell["word"]), (line, cell)
        _need(out, "TC (DECIDING; the TC1 word holding on >= 2 of 3 trees; MIXED if none): %s (" % o["tc"],
              "NV (DECIDING; over the 6 tree-depth cells): %s (" % o["nv"])
        if expect_tc is not None:
            assert o["tc"] == expect_tc, ("design", o["tc"], expect_tc, [r["word"] for r in o["trees"]])
        if expect_nv is not None:
            assert o["nv"] == expect_nv, ("design", o["nv"], expect_nv, [x["v90"] for r in o["trees"] for x in r["nv"]])
        _need(out, ("RULE 8: CUT-WORSE is REFUTED at the planned n (%d of 3" if o["r8tc"] >= 2 else "RULE 8: CUT-WORSE is not refuted (%d of 3")
              % o["r8tc"])
        _need(out, ("RULE 8: NON-NESTED is REFUTED (%d cells" if o["r8nv"] >= 2 else "RULE 8: NON-NESTED is not refuted (%d cells") % o["r8nv"])
        _need(out, FTC_FIRES if o["tc"] == "CUT-BETTER" else "FALSIFIER F-TC: NOT FIRED (TC %s;" % o["tc"])
        _need(out, FNV_FIRES if o["nv"] == "NESTED" else "FALSIFIER F-NV: NOT FIRED (NV %s;" % o["nv"])
        assert (FTC_FIRES in out) == (o["tc"] == "CUT-BETTER") and (FNV_FIRES in out) == (o["nv"] == "NESTED")
        _need(out, "PREDICTION P2 TC CUT-WORSE 0.75, NEITHER 0.12, MIXED 0.10, CUT-BETTER 0.03: observed %s; Brier %.4f" % (o["tc"], BRIER_TC[o["tc"]]))
        for r in o["trees"]:
            _need(out, "PREDICTION P1 %s D_cut -0.025 [-0.045, -0.008]: observed %+.5f -> %s" % (
                r["name"], r["D"], "HELD" if -0.045 <= r["D"] <= -0.008 else "FAILED"))
        e3 = all(r["dnmi"] < 0 for r in o["trees"])
        _need(out, "PREDICTION P3 (descriptive) NMI difference < 0 on 3 of 3 trees (probability 0.75): ")
        _need(out, "-> %s; Brier %.4f" % ("TRUE" if e3 else "FALSE", (0.75 - float(e3)) ** 2))
        n5 = sum(1 for r in o["trees"] if r["dbkm"] > 0)
        _need(out, "(%d of 3) -> %s; Brier %.4f" % (n5, "TRUE" if n5 >= 2 else "FALSE", (0.70 - float(n5 >= 2)) ** 2))
        if all("dr2" in r for r in o["trees"]):
            e4 = all(abs(r["dr2"]) < 0.0025 for r in o["trees"])
            _need(out, "-> %s; Brier %.4f" % ("TRUE" if e4 else "FALSE", (0.70 - float(e4)) ** 2))
        else:
            _need(out, "PREDICTION P4 (descriptive) |R2_int difference| < 0.0025 on 3 of 3 trees: NOT SCOREABLE")
        for r in o["trees"]:
            for cell in r["nv"]:
                band = {2: (0.25, 0.55), 3: (0.40, 0.70)}[cell["d"]]
                m = float(np.mean(cell["v90"]))
                _need(out, "PREDICTION P1 %s depth %d V90 seed mean in [%.2f, %.2f]: observed %.4f -> %s" % (
                    r["name"], cell["d"], band[0], band[1], m, "HELD" if band[0] <= m <= band[1] else "FAILED"))
        _need(out, "PREDICTION P2 NV NON-NESTED 0.95, MIXED 0.04, NESTED 0.01: observed %s; Brier %.4f" % (o["nv"], BRIER_NV[o["nv"]]))
        _need(out, PILOT_SEEN, WNS_TC, WNS_NV, "IDENTITY FX1 depth 2: tree (primary leaf,")
        for T in W["trees"]:
            _need(out, "[EMB-GUARD] %s: own qwen3 vectors ADMIT; permuted member->text map REFUSE (expected)" % T["name"],
                  "HYGIENE %s: fit texts %d; not TRAIN texts of the split 0; held-out texts in the fit 0;" % (T["name"], len(T["fit"])))
        with _reg(c):
            r2_, _t2, e2 = _go(lambda: run(lambda L: (_ for _ in ()).throw(AssertionError("loader called")), td))
        assert r2_ == "REFUSED" and "write-once" in e2, e2
        assert open(oc, encoding="utf-8").read() == out
        return o, out
    finally:
        shutil.rmtree(td, ignore_errors=True)


def _refuses(W, c, needle, mode="run"):
    td = tempfile.mkdtemp(prefix="tcg_rf_")
    try:
        with _reg(c):
            fn = (lambda: run(lambda L: W, td)) if mode == "run" else (lambda: dry_run(lambda L: W))
            r, _text, err = _go(fn)
        assert r == "REFUSED" and needle in err, (needle, err[:300])
        assert not os.path.exists(os.path.join(td, c["outcome"])), "an outcome was written by a refusal"
    finally:
        shutil.rmtree(td, ignore_errors=True)


def _syn_tree(name, D, lo, hi, spread=0.002, mde=0.0083, dn=-0.01, db=0.01, dr=0.001, v90s=((0.4,) * 5, (0.6,) * 5), keyed=True):
    S = dict(leaves=list(range(16)), Dmax=4, L={1: 2, 2: 4, 3: 8, 4: 16})
    row = dict(d=2, L=4, tree=dict(m1=0.5, nmi=0.3), km=[dict(m1=0.5)] * 5, bkm=[dict(m1=0.5)] * 5, bkm_L=[4] * 5,
               D_m1=D, D_m1_b=np.array([lo, hi]), D_nmi=dn)
    r = dict(name=name, S=S, depths=[2], rows=[row], n=100, G=90, kish=1.1, n_fit=200, n_keyed_f=0, n_keyed_h=0, irt=None,
             D_m1=dict(pt=D, lo=lo, hi=hi, se=0.003), DB_m1=dict(pt=db, lo=db, hi=db, se=0.0), D_nmi=dict(pt=dn, lo=dn, hi=dn, se=0.0),
             DB_nmi=dict(pt=0.0, lo=0.0, hi=0.0, se=0.0), spread_km=spread, bar=max(mde, spread), mde_real=0.0084)
    if keyed:
        r["D_r2"] = dict(pt=dr, lo=dr, hi=dr, se=0.0)
        r["DB_r2"] = dict(pt=dr, lo=dr, hi=dr, se=0.0)
    r["tc1"] = tc1_word(D, lo, hi, r["bar"])
    r["nv"] = [dict(d=2 + j, kc=4 * (j + 1), kf=16, km=[dict(H=0.1, off=0.01)] * 5, v90=list(v), word=nv1_word(list(v), 0.10),
                    tree=dict(v90=0.0), bkm=[dict(v90=0.0)] * 5, n_prim=200) for j, v in enumerate(v90s)]
    return r


def _syn_res(trees):
    return summarize(dict(trees=trees, desc=None))


def selftest(quiet=False):
    """Every deciding path EXECUTED through run() / dry_run() on fixture worlds (VALUE asserts against _oracle: own argmax filing,
    own majority, own stem_key groups and bootstrap replay, own NMI, own R2_int cell means, own V90), plus branch and refusal cases:
    E1 CUT-WORSE  [bad, bad, good], tree 1 keyed: TC CUT-WORSE (rule 8 not refuted; F-TC not fired); R2_int value; P4 NOT SCOREABLE
                  (two trees unkeyed); NV NESTED (clean clusters nest) -> F-NV FIRES.
    E2 NEITHER    [bad, good, good]: TC NEITHER (a first-tree-only TC reads CUT-WORSE); rule 8 REFUTED (2 of 3).
    E3 CUT-BETTER [better, better, good], all keyed: F-TC FIRES; P4 scored.
    E4 MIXED      [bad, good, better]: TC MIXED.
    E5 NON-NESTED [diffuse x 3]: NV NON-NESTED, F-NV not fired; restarts / seeds / bootstrap values matter here.
    E6 NV MIXED   [good, good, diffuse]: 4 NESTED + 2 NON-NESTED cells -> NV MIXED; rule 8 REFUTED.
    B  branches   TC1 boundaries (hi exactly 0, lo exactly 0, |D| exactly the bar, the bar's spread term), the word rules (V90 = 0.10
                  NESTED; 5 of 6 vs 4 of 6), render() on synthetic results: P1 / NV P1 bands inclusive, P3 / P4 / P5 events and every
                  Brier value, P4 NOT SCOREABLE, NV / F-NV / rule 8 lines.
    R  refusals   write-once (before the loader), registered counts, graph leaves, own guard, permuted guard, hygiene (a held-out
                  text in the fit), a DAG node, a depth field, no TC depth, an undefined NESTING depth, NV IDENTITY (tree, BKM);
                  no outcome written by any.
    D  dry-run    PLAN values (L_d, depths, NESTING cells, k list), no statistic line, nothing written."""
    n = [0]
    t0 = time.time()

    def ok(name):
        n[0] += 1
        if not quiet:
            print("  ok   %s (%.0fs)" % (name, time.time() - t0), flush=True)
    o1, out1 = _e2e(("bad", "bad", "good"), keyed=(True, False, False), expect_tc="CUT-WORSE", expect_nv="NESTED")
    assert o1["trees"][0]["D"] < -0.15 and o1["trees"][2]["word"] == "NEITHER" and "dr2" in o1["trees"][0], o1["trees"]
    ok("E1 CUT-WORSE (2 of 3 trees; R2_int value on the keyed tree; P4 NOT SCOREABLE; NV NESTED -> F-NV fires)")
    o2, _ = _e2e(("bad", "good", "good"), expect_tc="NEITHER")
    assert o2["r8tc"] == 2 and o2["trees"][0]["word"] == "CUT-WORSE"
    ok("E2 NEITHER (the first tree reads CUT-WORSE; rule 8 REFUTED)")
    o3, _ = _e2e(("better", "better", "good"), keyed=(True, True, True), expect_tc="CUT-BETTER")
    assert all("dr2" in r for r in o3["trees"])
    ok("E3 CUT-BETTER (F-TC fires; P4 scored on three keyed trees)")
    _e2e(("bad", "good", "better"), expect_tc="MIXED")
    ok("E4 MIXED")
    _e2e(("diffuse", "diffuse", "diffuse"), expect_nv="NON-NESTED")
    ok("E5 NON-NESTED (diffuse; F-NV not fired)")
    o6, _ = _e2e(("good", "good", "diffuse"), expect_nv="MIXED")
    assert o6["r8nv"] >= 2
    ok("E6 NV MIXED (rule 8 REFUTED)")
    c = dict(REG)
    for lab, args, want in (("hi exactly 0", (-0.05, -0.09, 0.0), "NEITHER"), ("hi below 0", (-0.05, -0.09, -1e-9), "CUT-WORSE"),
                            ("lo exactly 0", (0.05, 0.0, 0.09), "NEITHER"), ("lo above 0", (0.05, 1e-9, 0.09), "CUT-BETTER"),
                            ("|D| == bar", (-0.0083, -0.02, -0.001), "NEITHER"), ("|D| above bar", (-0.00831, -0.02, -0.001), "CUT-WORSE"),
                            ("+|D| == bar", (0.0083, 0.001, 0.02), "NEITHER"), ("+|D| above bar", (0.00831, 0.001, 0.02), "CUT-BETTER")):
        r = _syn_tree("S", *args)
        assert r["tc1"] == want, (lab, r["tc1"], want)
    r = _syn_tree("S", -0.02, -0.03, -0.01, spread=0.025)
    assert r["bar"] == 0.025 and r["tc1"] == "NEITHER", r["bar"]
    assert _syn_tree("S", -0.03, -0.04, -0.01, spread=0.025)["tc1"] == "CUT-WORSE"
    ok("B1 TC1 boundaries (hi = 0, lo = 0, |D| = bar strict, the spread term of the bar)")
    assert tc_word(["CUT-WORSE", "NEITHER", "CUT-WORSE"]) == "CUT-WORSE" and tc_word(["CUT-WORSE", "NEITHER", "CUT-BETTER"]) == "MIXED"
    assert tc_word(["NEITHER", "CUT-BETTER", "CUT-BETTER"]) == "CUT-BETTER" and tc_word(["CUT-WORSE", "NEITHER", "NEITHER"]) == "NEITHER"
    assert nv1_word([0.11] * 5, 0.10) == "NON-NESTED" and nv1_word([0.10] * 5, 0.10) == "NESTED"
    assert nv1_word([0.11] * 4 + [0.10], 0.10) == "MIXED" and nv1_word([0.10] + [0.11] * 4, 0.10) == "MIXED"
    assert nv_word(["NON-NESTED"] * 5 + ["MIXED"]) == "NON-NESTED" and nv_word(["NON-NESTED"] * 4 + ["MIXED"] * 2) == "MIXED"
    assert nv_word(["NESTED"] * 5 + ["NON-NESTED"]) == "NESTED" and nv_word(["NESTED"] * 4 + ["NON-NESTED"] * 2) == "MIXED"
    assert nesting([0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0] * 10, 0.90)["v90"] == 0.0
    assert abs(nesting([0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0] * 10, 0.90)["v90"] - 1.0) < 1e-12
    assert used_depths(dict(Dmax=4, L={1: 5, 2: 3, 3: 6, 4: 10}), 4) == [3] and used_depths(dict(Dmax=3, L={1: 4, 2: 9, 3: 9}), 4) == []
    assert used_depths(dict(Dmax=4, L={1: 2, 2: 4, 3: 8, 4: 16}), 4) == [2, 3]
    sm = _syn_res([_syn_tree("A", -0.02, -0.03, 0.0), _syn_tree("B", -0.0083, -0.02, -0.001), _syn_tree("C", -0.02, -0.03, -0.01)])
    assert sm["rule8_tc_n"] == 2 and sm["tc"] == "NEITHER", (sm["rule8_tc_n"], sm["tc"])
    sm = _syn_res([_syn_tree("A", -0.02, -0.03, -1e-9), _syn_tree("B", -0.00831, -0.02, -0.001), _syn_tree("C", 0.02, 0.01, 0.03)])
    assert sm["rule8_tc_n"] == 1 and sm["tc"] == "CUT-WORSE" and not sm["ftc"], (sm["rule8_tc_n"], sm["tc"])
    ok("B2 word rules (V90 = 0.10 NESTED; 5 of 6 vs 4 of 6; first-seed-only MIXED), the V90 0.90 boundary, used depths (d >= 2,"
       " L_d >= 4, L_d < L_max), rule 8 at hi = 0 and |D| = bar")
    trees = [_syn_tree("S1", -0.045, -0.05, -0.04), _syn_tree("S2", -0.008, -0.012, -0.004, dn=0.01, db=-0.01),
             _syn_tree("S3", -0.0451, -0.05, -0.04, dr=0.0025, v90s=((0.25,) * 5, (0.70,) * 5))]
    t = "\n".join(render(_syn_res(trees), c))
    _need(t, "PREDICTION P1 S1 D_cut -0.025 [-0.045, -0.008]: observed -0.04500 -> HELD",
          "PREDICTION P1 S2 D_cut -0.025 [-0.045, -0.008]: observed -0.00800 -> HELD",
          "PREDICTION P1 S3 D_cut -0.025 [-0.045, -0.008]: observed -0.04510 -> FAILED",
          "TC (DECIDING; the TC1 word holding on >= 2 of 3 trees; MIXED if none): CUT-WORSE (TC1 words S1 CUT-WORSE, S2 NEITHER, S3 CUT-WORSE)",
          "RULE 8: CUT-WORSE is not refuted (1 of 3 trees",
          "PREDICTION P2 TC CUT-WORSE 0.75, NEITHER 0.12, MIXED 0.10, CUT-BETTER 0.03: observed CUT-WORSE; Brier 0.0878",
          "PREDICTION P3 (descriptive) NMI difference < 0 on 3 of 3 trees (probability 0.75): S1 -0.01000, S2 +0.01000, S3 -0.01000 -> FALSE;"
          " Brier 0.5625",
          "PREDICTION P4 (descriptive) |R2_int difference| < 0.0025 on 3 of 3 trees (probability 0.70): S1 +0.00100, S2 +0.00100, S3 +0.00250"
          " -> FALSE; Brier 0.4900",
          "PREDICTION P5 (descriptive) tree minus BKM purity > 0 on >= 2 of 3 trees (probability 0.70): S1 +0.01000, S2 -0.01000, S3 +0.01000"
          " (2 of 3) -> TRUE; Brier 0.0900",
          "PREDICTION P1 S3 depth 2 V90 seed mean in [0.25, 0.55]: observed 0.2500 -> HELD",
          "PREDICTION P1 S3 depth 3 V90 seed mean in [0.40, 0.70]: observed 0.7000 -> HELD",
          "PREDICTION P1 S1 depth 3 V90 seed mean in [0.40, 0.70]: observed 0.6000 -> HELD",
          "NV (DECIDING; over the 6 tree-depth cells): NON-NESTED (NON-NESTED 6, NESTED 0, MIXED 0)",
          "RULE 8: NON-NESTED is not refuted (0 cells", "FALSIFIER F-NV: NOT FIRED (NV NON-NESTED;",
          "PREDICTION P2 NV NON-NESTED 0.95, MIXED 0.04, NESTED 0.01: observed NON-NESTED; Brier 0.0042",
          "FALSIFIER F-TC: NOT FIRED (TC CUT-WORSE;", "DESCRIPTIVE NOT DONE: the AF-U per-benchmark re-print")
    trees = [_syn_tree("S1", -0.02, -0.03, -0.01, dr=0.0024, v90s=((0.1,) * 5, (0.05,) * 5)),
             _syn_tree("S2", -0.02, -0.03, -0.01, db=-0.01, keyed=False, v90s=((0.1,) * 5, (0.0,) * 5)),
             _syn_tree("S3", 0.02, 0.01, 0.03, db=0.0, v90s=((0.2,) * 5, (0.0,) * 5))]
    t = "\n".join(render(_syn_res(trees), c))
    _need(t, "PREDICTION P4 (descriptive) |R2_int difference| < 0.0025 on 3 of 3 trees: NOT SCOREABLE",
          "NV (DECIDING; over the 6 tree-depth cells): NESTED (NON-NESTED 1, NESTED 5, MIXED 0)", FNV_FIRES,
          "RULE 8: NON-NESTED is REFUTED (5 cells", "PREDICTION P2 NV NON-NESTED 0.95, MIXED 0.04, NESTED 0.01: observed NESTED; Brier 1.8842",
          "PREDICTION P1 S1 depth 2 V90 seed mean in [0.25, 0.55]: observed 0.1000 -> FAILED",
          "(1 of 3) -> FALSE; Brier 0.4900", "TC1 S3 (point and 95% interval jointly): D_cut = +0.02000 | 95% [+0.01000, +0.03000]")
    trees = [_syn_tree("S1", -0.02, -0.03, -0.01, dr=0.0024), _syn_tree("S2", -0.02, -0.03, -0.01, dr=-0.0024),
             _syn_tree("S3", 0.02, 0.01, 0.03, dr=0.0)]
    t = "\n".join(render(_syn_res(trees), c))
    _need(t, "S1 +0.00240, S2 -0.00240, S3 +0.00000 -> TRUE; Brier 0.0900")
    ok("B3 render(): P1 bands inclusive, P3 / P4 / P5 events and Brier values, P4 NOT SCOREABLE, NV / F-NV / rule 8 lines")
    W = _world(("bad", "good", "good"))
    cR = _fx_reg(W)
    td = tempfile.mkdtemp(prefix="tcg_wo_")
    try:
        open(os.path.join(td, cR["outcome"]), "w").close()
        called = []
        with _reg(cR):
            r_, _t, e_ = _go(lambda: run(lambda L: called.append(1) or W, td))
        assert r_ == "REFUSED" and "write-once" in e_ and not called, e_
    finally:
        shutil.rmtree(td, ignore_errors=True)
    _refuses(W, dict(cR, trees=(dict(cR["trees"][0], heldout=cR["trees"][0]["heldout"] + 1),) + cR["trees"][1:]),
             "registered / E1-SPLIT-DRAWS build facts")
    _refuses(W, dict(cR, trees=cR["trees"][:2] + (dict(cR["trees"][2], fit=cR["trees"][2]["fit"] - 1),)), "registered / E1-SPLIT-DRAWS build facts")
    W2 = dict(W, trees=[dict(W["trees"][0], graph=dict(W["trees"][0]["graph"], byid={k: v for k, v in W["trees"][0]["graph"]["byid"].items()
                                                                                      if k != "l15"}))] + W["trees"][1:])
    _refuses(W2, cR, "snapshot graph leaves != run dir leaves")
    _refuses(dict(W, trees=W["trees"][:1] + [dict(W["trees"][1], guard=lambda: (False, False, "x", "own refused"))] + W["trees"][2:]), cR,
             "[EMB-GUARD] FX2 on its own qwen3 vectors")
    _refuses(dict(W, trees=W["trees"][:2] + [dict(W["trees"][2], guard=lambda: (True, True, "x", None))]), cR,
             "the permuted-map discriminator was ADMITTED")
    T5 = dict(W["trees"][2])
    T5["fit"] = T5["fit"][:-1] + [T5["held"][0]]
    _refuses(dict(W, trees=W["trees"][:2] + [T5]), cR, "held-out content reaches the tree")
    T6 = dict(W["trees"][1])
    by6 = {k: dict(v) for k, v in T6["tree"]["byid"].items()}
    by6["c0"]["parentIds"] = ["b0", "b1"]
    T6["tree"] = dict(T6["tree"], byid=by6)
    _refuses(dict(W, trees=W["trees"][:1] + [T6] + W["trees"][2:]), cR, "has 2 parents")
    T7 = dict(W["trees"][1])
    by7 = {k: dict(v) for k, v in T7["tree"]["byid"].items()}
    by7["c3"]["depth"] = 2
    T7["tree"] = dict(T7["tree"], byid=by7)
    _refuses(dict(W, trees=W["trees"][:1] + [T7] + W["trees"][2:]), cR, "depth field differs")
    T8 = dict(W["trees"][2])
    T8["prim"] = ["b0"] + list(T8["prim"][1:])
    _refuses(dict(W, trees=W["trees"][:2] + [T8]), cR, "primary leaf id(s) are not leaves of the tree as built")
    _refuses(W, dict(cR, l_min=9), "no depth d >= 2 with 9 <= L_d < L_max")
    _refuses(W, dict(cR, nest_depths=(2, 4)), "NESTING depth 4 undefined")
    for nv_, needle in (([dict(d=2, tree=dict(v90=0.01), bkm=[dict(v90=0.0)] * 5)], "[NV-IDENTITY] X depth 2: tree"),
                        ([dict(d=3, tree=dict(v90=0.0), bkm=[dict(v90=0.0)] * 4 + [dict(v90=0.2)])], "[NV-IDENTITY] X depth 3: BKM s4")):
        r_, _t, e_ = _go(lambda: identity_check([dict(name="X", nv=nv_)]))
        assert r_ == "REFUSED" and needle in e_, e_
    ok("R refusals (write-once before the loader, counts, graph leaves, own / permuted guard, hygiene, DAG, depth, no TC depth,"
       " NESTING depth, NV identity tree / BKM); no outcome written by any")
    with _reg(cR):
        r_, t_, e_ = _go(lambda: dry_run(lambda L: W))
    assert r_ == 0 and e_ == "", e_
    _need(t_, "PLAN FX1: L_d d1:2 d2:4 d3:8 d4:16 | TC depths [2, 3] (L [4, 8]) | NESTING cells ['d2 4 vs 16', 'd3 8 vs 16'] | KM / BKM at"
              " k [4, 8, 16] x seeds 0/1/2/3/4 | keyed fit 0 / held-out 0", "[MODE] --dry-run:", "COST: 0 calls; 45 spherical k-means fits x 10",
          "[EMB-GUARD] FX3: own qwen3 vectors ADMIT", "HYGIENE FX2: fit texts")
    assert "TC1 " not in t_ and "D_cut" not in t_ and "NV1 " not in t_
    ok("D dry-run (PLAN values; no statistic; nothing written)")
    keyed = (["ma", "mb"], {"ma": {"q1": 1, "q2": 0, "q3": 1, "q9": 1}, "mb": {"q1": 0, "q2": 1, "q3": 1, "q9": 0}}, {},
             {"q1": "t1", "q2": "t2", "q3": "t3", "q9": "t2"}, ["q1", "q2", "q3", "q9"])
    K = keyed_index(["t0", "t1", "t2"], ["t3", "t4", "t2"], keyed)
    assert K["fpos"].tolist() == [1, 2] and K["hpos"].tolist() == [0, 2] and K["multi"] == 1, K
    assert K["Yf"].tolist() == [[1, 0], [0, 1]] and K["Yh"].tolist() == [[1, 1], [0, 1]], K
    ok("K keyed_index (texts without a key skipped, a text with two keyed ids reads the smaller id, multi counted)")
    print("%s SELFTEST PASSED (%d checks, %.0fs)" % (TAG, n[0], time.time() - t0))
    return 0


MUTANTS = (
    ("X00 control (no edit)", "", ""),
    ("X01 TC1 CUT-WORSE hi < 0 -> hi <= 0", '    if hi < 0 and big:', '    if hi <= 0 and big:'),
    ("X02 TC1 |D| > bar -> >=", '    big = bool(abs(D) > bar)', '    big = bool(abs(D) >= bar)'),
    ("X03 TC1 CUT-BETTER lo > 0 -> lo >= 0", '    if lo > 0 and big:', '    if lo >= 0 and big:'),
    ("X04 bar max -> min", '    res["bar"] = float(max(c["mde80"], res["spread_km"]))', '    res["bar"] = float(min(c["mde80"], res["spread_km"]))'),
    ("X05 spread_KM min <-> max", '    res["spread_km"] = float(max(km_avg) - min(km_avg))', '    res["spread_km"] = float(min(km_avg) - max(km_avg))'),
    ("X06 bar on the planning SE, not the registered MDE80", '    res["bar"] = float(max(c["mde80"], res["spread_km"]))',
     '    res["bar"] = float(max(c["se_plan"], res["spread_km"]))'),
    ("X07 TC >= 2 of 3 -> >= 1", '        if sum(1 for x in words if x == w) >= 2:', '        if sum(1 for x in words if x == w) >= 1:'),
    ("X08 TC from the first tree only", '    res["tc"] = tc_word([r["tc1"] for r in tr])', '    res["tc"] = tr[0]["tc1"]'),
    ("X09 depths from d >= 1", '    return [d for d in range(2, S["Dmax"] + 1) if l_min <= S["L"][d] < Lmax]',
     '    return [d for d in range(1, S["Dmax"] + 1) if l_min <= S["L"][d] < Lmax]'),
    ("X10 depths include the leaf level (<= L_max)", '    return [d for d in range(2, S["Dmax"] + 1) if l_min <= S["L"][d] < Lmax]',
     '    return [d for d in range(2, S["Dmax"] + 1) if l_min <= S["L"][d] <= Lmax]'),
    ("X11 the L_d >= 4 clause dropped", '    return [d for d in range(2, S["Dmax"] + 1) if l_min <= S["L"][d] < Lmax]',
     '    return [d for d in range(2, S["Dmax"] + 1) if S["L"][d] < Lmax]'),
    ("X12 majority from the held-out (wrong population)", '        sc, hits, kh = FM.m1_block(fn, Xf, Xh, fit, held)',
     '        sc, hits, kh = FM.m1_block(fn, Xh, Xh, held, held)'),
    ("X13 held-out filed as the fit (scores the fit set)", '        sc, hits, kh = FM.m1_block(fn, Xf, Xh, fit, held)',
     '        sc, hits, kh = FM.m1_block(fn, Xf, Xf, fit, fit[:len(held)] + fit[len(held):len(held)])'),
    ("X14 bootstrap per item, not per stem_key group", '        W[b] = cnt[groups]',
     '        W[b] = np.bincount(rng.integers(0, len(texts), len(texts)), minlength=len(texts)).astype(np.float64)'),
    ("X15 bootstrap seed + 1", '    rng = np.random.default_rng(seed)\n    W = np.empty', '    rng = np.random.default_rng(seed + 1)\n    W = np.empty'),
    ("X16 95% interval -> 90%", '            res[pre + meas] = dict(pt=pt, lo=pct(bt, 2.5), hi=pct(bt, 97.5), se=float(np.std(bt, ddof=1)))',
     '            res[pre + meas] = dict(pt=pt, lo=pct(bt, 5), hi=pct(bt, 95), se=float(np.std(bt, ddof=1)))'),
    ("X17 KM arm: first seed only", '        kms = [arm_measures(cent_fn(km[(L_d, s)]["C"], "K")) for s in seeds]',
     '        kms = [arm_measures(cent_fn(km[(L_d, s)]["C"], "K")) for s in seeds[:1]]'),
    ("X18 KM restarts 10 -> 1", '    lab, C = CA.skm_best(X, k, s, n_init=n_init)', '    lab, C = CA.skm_best(X, k, s, n_init=1)'),
    ("X19 KM seed s -> s + 1", '    km = {(k, s): fit_km(Xf, k, s, c["n_init"]) for k in ks for s in seeds}',
     '    km = {(k, s): fit_km(Xf, k, s + 1, c["n_init"]) for k in ks for s in seeds}'),
    ("X20 V90 < 0.90 -> <=", '        if top / s < maj:', '        if top / s <= maj:'),
    ("X21 NESTING coarse / fine swapped", '        kmn = [nesting(km[(kc, s)]["lab"], km[(Lmax, s)]["lab"], c["maj"]) for s in seeds]',
     '        kmn = [nesting(km[(Lmax, s)]["lab"], km[(kc, s)]["lab"], c["maj"]) for s in seeds]'),
    ("X22 NESTING fine fitted at another seed", '        kmn = [nesting(km[(kc, s)]["lab"], km[(Lmax, s)]["lab"], c["maj"]) for s in seeds]',
     '        kmn = [nesting(km[(kc, s)]["lab"], km[(Lmax, seeds[(seeds.index(s) + 1) % len(seeds)])]["lab"], c["maj"]) for s in seeds]'),
    ("X23 NV1 all -> any (NON-NESTED)", '    if all(v > bar for v in v90s):', '    if any(v > bar for v in v90s):'),
    ("X24 NV1 NESTED all -> any", '    if all(v <= bar for v in v90s):', '    if any(v <= bar for v in v90s):'),
    ("X25 NV >= 5 of 6 -> >= 4", '    if sum(1 for w in words if w == "NON-NESTED") >= 5:', '    if sum(1 for w in words if w == "NON-NESTED") >= 4:'),
    ("X26 NV NESTED >= 5 -> >= 4", '    if sum(1 for w in words if w == "NESTED") >= 5:', '    if sum(1 for w in words if w == "NESTED") >= 4:'),
    ("X27 NV IDENTITY not enforced", '            if bad:\n                refuse("[NV-IDENTITY]', '            if False:\n                refuse("[NV-IDENTITY]'),
    ("X28 rule 8 (TC) hi >= 0 -> hi > 0", '    res["rule8_tc_n"] = sum(1 for r in tr if r["D_m1"]["hi"] >= 0 or',
     '    res["rule8_tc_n"] = sum(1 for r in tr if r["D_m1"]["hi"] > 0 or'),
    ("X29 rule 8 (TC) |D| <= bar -> <", 'abs(r["D_m1"]["pt"]) <= r["bar"])', 'abs(r["D_m1"]["pt"]) < r["bar"])'),
    ("X30 rule 8 (NV) counts MIXED only", '    res["rule8_nv_n"] = sum(1 for cell in cells if cell["word"] != "NON-NESTED")',
     '    res["rule8_nv_n"] = sum(1 for cell in cells if cell["word"] == "MIXED")'),
    ("X31 F-TC fires on CUT-WORSE", '    res["ftc"] = bool(res["tc"] == "CUT-BETTER")', '    res["ftc"] = bool(res["tc"] == "CUT-WORSE")'),
    ("X32 F-NV fires on NON-NESTED", '    res["fnv"] = bool(res["nv"] == "NESTED")', '    res["fnv"] = bool(res["nv"] == "NON-NESTED")'),
    ("X33 outcome not write-once", '    if os.path.exists(oc):\n        refuse(', '    if False:\n        refuse('),
    ("X34 hygiene skipped", '        E1SD.hygiene(lab, set(t for t, _ in T["fit"]), T["split_train"], T["held"], L)', '        pass'),
    ("X35 permuted-map discriminator not enforced", '        if ok_p:\n            refuse(', '        if False:\n            refuse('),
    ("X36 own-vector guard not enforced", '        if not ok:\n            refuse("[EMB-GUARD]', '        if False:\n            refuse("[EMB-GUARD]'),
    ("X37 registered counts not enforced", '        if got != want:', '        if False:'),
    ("X38 graph leaves not checked", '        if set(gl) != set(T["tree"]["leaf_ids"]):', '        if False:'),
    ("X39 run skips admit", '    W = loader(L)\n    admit(W, L, c)\n    plan_lines(W, L, c)\n    res = compute(W, c)',
     '    W = loader(L)\n    plan_lines(W, L, c)\n    res = compute(W, c)'),
    ("X40 R2_int cell means unshrunk", '    eb = RPI.cell_means(eT, gT, len(names), np.ones(len(gT)), RPI.R()["shrink"])',
     '    eb = RPI.cell_means(eT, gT, len(names), np.ones(len(gT)), 0.0)'),
    ("X41 NMI normalised by H_cell only", '        out = np.where(H1 + H2 > 0, 2.0 * I / (H1 + H2), 0.0)', '        out = np.where(H1 > 0, I / H1, 0.0)'),
    ("X42 BKM arm: first seed only", '        bks = [arm_measures(cent_fn(bkm[(L_d, s)]["C"], "B")) for s in seeds]',
     '        bks = [arm_measures(cent_fn(bkm[(L_d, s)]["C"], "B")) for s in seeds[:1]]'),
    ("X43 cut ancestor one level too high", '    while S["depth"][x] > d:', '    while S["depth"][x] >= d and x in S["par"]:'),
    ("X44 TC1 on the BKM contrast (wrong arm)", '    dc = res["D_m1"]\n    res["tc1"]', '    dc = res["DB_m1"]\n    res["tc1"]'),
    ("X45 P2 Brier on the observed outcome only", '    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))',
     '    return float(sum((1.0 - p) ** 2 for o, p in probs if o == observed))'),
    ("X46 P5 >= 2 of 3 -> >= 3", '    e5 = bool(n5 >= 2)', '    e5 = bool(n5 >= 3)'),
    ("X47 P3 all -> any", '    e3 = bool(all(r["D_nmi"]["pt"] < 0 for r in res["trees"]))', '    e3 = bool(any(r["D_nmi"]["pt"] < 0 for r in res["trees"]))'),
    ("X48 P4 < 0.0025 -> <=", '        e4 = bool(all(abs(r["D_r2"]["pt"]) < P_TC["P4_THR"] for r in res["trees"]))',
     '        e4 = bool(all(abs(r["D_r2"]["pt"]) <= P_TC["P4_THR"] for r in res["trees"]))'),
    ("X49 prediction bands open", '    return bool(band[0] <= x <= band[1])', '    return bool(band[0] < x < band[1])'),
    ("X50 F-TC fired line dropped", '    L.append(FTC_FIRES if res["ftc"] else', '    L.append("" if res["ftc"] else'),
    ("X51 F-NV fired line dropped", '    L.append(FNV_FIRES if res["fnv"] else', '    L.append("" if res["fnv"] else'),
    ("X52 rule 8 (TC) REFUTED at >= 1", '    if res["rule8_tc_n"] >= 2:', '    if res["rule8_tc_n"] >= 1:'),
    ("X53 P4 NOT SCOREABLE branch scored as FALSE", '    if all("D_r2" in r for r in res["trees"]):', '    if True:'),
    ("X54 NV P1 band of depth 2 for every depth", '            band = P_NV["P1"].get(cell["d"])', '            band = P_NV["P1"].get(2)'),
    ("X55 depth-1 NESTING allowed undefined (refusal removed)",
     '        if d > S["Dmax"] or not (2 <= S["L"][d] < Lmax):', '        if d > S["Dmax"]:'),
    ("X56 a DAG node accepted", '        if len(p) > 1:\n            refuse(', '        if False:\n            refuse('),
    ("X57 depth field not checked", '    if bad:\n        refuse("%s: %d node(s) whose depth field', '    if False:\n        refuse("%s: %d node(s) whose depth field'),
    ("X59 keyed: a text with two ids reads the larger id", "    Yf = np.array([[G[m][sorted(by_text[texts_f[j]])[0]] for m in models]",
     "    Yf = np.array([[G[m][sorted(by_text[texts_f[j]])[-1]] for m in models]"),
    ("X60 keyed held-out positions searched in the fit texts", "    hpos = [j for j, t in enumerate(texts_h) if t in by_text]",
     "    hpos = [j for j, t in enumerate(texts_f) if t in by_text]"),
    ("X61 a primary leaf that is not a tree leaf accepted", "        if stray:\n            refuse(", "        if False:\n            refuse("),
    ("X58 dry-run computes and prints the statistic", '    plan_lines(W, L, c)\n    say(L, "[MODE] --dry-run:',
     '    plan_lines(W, L, c)\n    [say(L, x) for x in render(compute(W, c), c)]\n    say(L, "[MODE] --dry-run:'),
)


def run_mutants(only=None):
    """Each mutant edits the code ABOVE the SELFTEST marker in memory, executes the edited module and runs its selftest; KILLED iff
    the selftest fails. The control X00 must survive. No file is written (in-process exec)."""
    import types
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    mark = "\n# " + chr(0x2550) * 2 + " SELFTEST"
    cut = src.index(mark)
    head, tail_ = src[:cut], src[cut:]
    rows, bad = [], []
    for name, old, new in MUTANTS:
        if only and not any(name.startswith(o) for o in only):
            continue
        if old and head.count(old) != 1:
            bad.append(name)
            print("%s MUTANT %-62s NOT APPLIED (%d matches)" % (TAG, name, head.count(old)), flush=True)
            continue
        mod = types.ModuleType("tree_cut_granularity_mutant")
        mod.__file__ = os.path.abspath(__file__)
        try:
            exec(compile((head.replace(old, new) if old else head) + tail_, mod.__file__, "exec"), mod.__dict__)
            with contextlib.redirect_stdout(io.StringIO()):
                mod.selftest(quiet=True)
            res = "SURVIVED"
        except BaseException as e:   # noqa: B902
            res = "KILLED (%s: %s)" % (type(e).__name__, str(e)[:90].replace("\n", " "))
        rows.append((name, res))
        print("%s MUTANT %-62s %s" % (TAG, name, res), flush=True)
    ctrl = [r for nm, r in rows if nm.startswith("X00")]
    surv = [nm for nm, r in rows if r == "SURVIVED" and not nm.startswith("X00")]
    killed = sum(1 for nm, r in rows if r.startswith("KILLED") and not nm.startswith("X00"))
    total = sum(1 for nm, _r in rows if not nm.startswith("X00"))
    print("%s MUTANTS %d of %d KILLED; control %s; survivors %s; not applied %s" % (TAG, killed, total, ctrl[0] if ctrl else "not run",
                                                                                  surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


if __name__ == "__main__":
    sys.exit(main())
