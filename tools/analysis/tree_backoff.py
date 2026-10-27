"""tree_backoff.py: TREE-BACKOFF -- on the content-closed v2 union split, does the tree's HIERARCHY improve a routing decision: does
empirical-Bayes back-off of each AF-U leaf's per-model TRAIN accuracy toward its ancestors (strength tau chosen on GATE) route EVAL
better than AF-U's flat-leaf policy, with per-source k-means plus a Ward-on-centroids hierarchy beside?
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU reader.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-06 (before any code or call) — TREE-BACKOFF: on the content-closed v2 union split,
  does the tree's HIERARCHY improve a routing decision, ..." (L24814-L24826, _as_of 9bff7e39, parent 4c764a1e): BO1 (the one
  deciding criterion), the secondary D_TK RULED DESCRIPTIVE, Support (a)-(g), P1-P6, F-BO, WILL NOT SHOW. Record: "## Registrar's
  record 2026-10-06 ... four zero-call tests registered at the author's "start 1 to 4" ..." (the section before it).

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form; rule 7: every step below except --selftest / --mutants is a
POOL READER: run `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` first; exit 1 = free, 0 = busy, wait while busy):
  0. python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_backoff.py --selftest   # fixtures only; no DB of record
     python tools/analysis/scratch_dir.py --run -- python tools/analysis/tree_backoff.py --mutants    # the mutant table (sandbox)
  1. python tools/analysis/tree_backoff.py --dry-run   # POOL line first; pins; denominators; cost; B0-2 pool check; the UNION-AF-ROUTE
                                                       #   inputs re-hashed; frozen policy sha; the AF-U and K-WARD hierarchies built;
                                                       #   K_s re-filed = k_cells_s*.tsv; GATE cells; NO key (TRAIN, GATE or EVAL), NO
                                                       #   statistic; writes nothing
  2. python tools/analysis/tree_backoff.py --run       # TRAIN key, GATE key (tau only), ONE EVAL key read (marker first); outcome
       WRITE-ONCE: experiment_results/archv2/tree_backoff/outcome.txt (+ tree_backoff.READ_STARTED). Never committed: pin by sha256
       and back up to E:/TaxoArena_backup_<date>_tree_backoff with SHA256SUMS.txt.
  --data-root <dir> (optional, every mode): the checkout whose experiment_results/, data_v2/ and cache DBs are read; from a worktree:
  --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena. Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; outcome and marker absent (write-once); the B0-2 pool check; AF-U state (D-8, one-cell evidence), the inputs
  manifest (sha256-lf 53021e26...) with every file re-hashed, the AF and K0..K4 cells, the frozen TRAIN policy (sha256 8d68018c...)
  (union_route_common.prepare); (2) STRUCTURE: the AF-U hierarchy from the members' last dag snapshots ([TB-HIER] on a DAG node or a
  cell that is not a leaf); per seed s the K_s centroids recomputed (union_af_route.us_fit, seed s, on the bundle's TRAIN rows), every
  scored item re-filed and compared with k_cells_s<s>.tsv ([TB-KDIFF]), the K-WARD hierarchy (scipy Ward on the renormalised
  centroids within source); the GATE items (escalation_rc.gate_items on the merged validation: modal AF leaf) filed to every K_s;
  (3) the gen view (TRAIN key), the GATE key (escalation_curve.gate_key, between the TRAIN key and the eval view), the eval view, the
  marker mode "x", THE EVAL KEY READ (union_route_common.read_views); [TB-DENOM] 5,907 / 5,404; [B3]; [TB-GATE-DENOM] 1,944 key-
  complete GATE items; [TB-GATE-SIDE] no GATE item among the scored items; (4) tau* per arm on GATE (full-TRAIN fits); (5)
  v2_declared_cells.run_boot (B 2,000, default_rng(42)) with the back-off hook (every node accuracy re-fitted per replicate, tau held
  at tau*); [G3]; [TB-IDENTITY] before any new number; [TB-MIRROR]: the hook's tau = 0 arms equal run_boot's TREE / K_s / best-single
  arms at the point, in every i.i.d. and every two-stage replicate, on every subset; (6) BO1, rule 8, F-BO, the descriptive lines,
  the weak-region arm, predictions; the outcome written mode "x" (a view whose sha changed writes *_VOID.txt instead).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  R1  AF-U hierarchy: every node of each member's LAST dag snapshot named "<SOURCE>:<id>" (the AF cell naming), its parent the
      single parentIds entry (more than one -> [TB-HIER]; the build is tree-only), a member root's parent the union root "<UNION>";
      a one-cell member's cell (declaration) hangs under the union root (it is its own source root). "<no-routing-row>" (2 TRAIN
      items, fitted as their own cell by G14's reader) and "<unrouted>" are pseudo-leaves under the union root.
  R2  K-WARD: per seed s and source, the K_s FILING centroids (us_fit centres, renormalised) -> scipy linkage(method "ward"); the
      top merge is the source root, its parent the union root; a k = 1 source's one cell hangs under the union root.
  R3  Node statistics over the scored TRAIN items (G14's policy-fit set) with the replicate's integer TRAIN weights: n_v and s_v,m
      summed over every leaf below v. p_root,m = s_root,m / n_root; p_v,m = (s_v,m + tau p_parent(v),m) / (n_v + tau), top-down;
      the leaf pick argmax_m p_leaf,m (numpy argmax over the sorted roster = the first model on a tie, as V.fit). tau = 0 IS V.fit:
      argmax s_leaf,m with a leaf of TRAIN mass < 1 -> the best single (argmax s_root,m = V.fit's best single). The support of the
      weights must be TRAIN ([TB-G3]).
  R4  tau* per arm (per seed for K-WARD) = the grid value maximising the number of correct GATE picks (integer counts; ties to the
      smaller tau, i.e. the first maximum on the increasing grid) over the key-complete GATE items, every node fitted on the full
      TRAIN. GATE cell of an item: its modal AF leaf (ESCALATION-RC R5); its K_s cell: nearest K_s centroid among its declared
      source(s) (UNION-AF-ROUTE R3). tau* is held fixed in the bootstrap (GATE selection variance not propagated; stated).
  R5  D_B = acc(TB) - acc(TF) on the 5,907 EVAL items, item-paired inside run_boot's two-stage replicates; the deciding 95% interval
      = point +- 1.96 SE_2stage (G14's reader form, union_route_common.interval); the percentile and the i.i.d. interval are printed
      beside, NOT deciding.
  R6  BO1: HIERARCHY-HELPS iff D_B > 0 AND lo > 0; HIERARCHY-HURTS iff D_B < 0 AND hi < 0; NEITHER otherwise; tau*(AF-U) = 0 ->
      NEITHER with the words 'GATE chose no shrinkage' (D_B = 0 identically, checked). Rule 8: HIERARCHY-HELPS refuted iff lo <= 0 or
      tau* = 0. F-BO fires iff HIERARCHY-HURTS.
  R7  D_TK = acc(TB) - mean_s acc(KB_s) (paired; two-stage interval), seed spread = max - min over s of acc(KB_s); D_KB = mean_s
      acc(KB_s) - mean_s acc(KF_s); D_B - D_KB as one linear contrast. All DESCRIPTIVE (registrar's ruling).
  R8  Cross-source AF-U filing: an EVAL item whose AF leaf's member (union_cells_io.cell_member) differs from its stratum source.
  R9  Picks changed: share of EVAL items whose TB pick differs from the TF pick (point fit), overall and by stratum source. P5 "BBH
      carries more than half of |D_B|": TRUE iff D_B != 0 and (sum over BBH EVAL items of (c_TB - c_TF) / N) / D_B > 0.5.
  R10 Weak regions (optional descriptive arm): per model, nodes ordered by TRAIN accuracy ascending (ties: larger TRAIN count, then
      name), nodes with no TRAIN item skipped, the union root and pseudo-leaves excluded; greedily added unless nested with (ancestor
      or descendant of) a chosen node, until the chosen TRAIN coverage reaches c. AF-U and K-WARD: any depth; KF: K_s leaves only.
      Region EVAL accuracy and its gap to the model's EVAL mean; K arms averaged over the five seeds (nanmean; an empty region n/a).
      P6 reads the TRAIN-chosen best single at c 0.10 and KF's seed mean; an n/a gap scores FAILED / FALSE.
  R11 Predictions "X [lo, hi]" HELD iff the point lies in the closed interval; BO1's probabilities by the three-outcome Brier sum
      (union_route_common.brier); a binary probability p by (p - [event])^2 (the CONSTRUCTION-ARMS convention).
  R12 Not applicable (stated): no judge verdict (key-scored), so no wrong(established) count and no tie convention A / B; no call
      cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; temp on E: via scratch_dir; opens NO DB of record):
  branches      BO1 by VALUE through tb_lines (the outcome prints them verbatim): HELPS / HURTS / NEITHER, lo exactly 0, hi exactly 0,
                tau* = 0 words; rule 8 both reasons; F-BO fired / not; P1-P6 bands inclusive at both ends; every Brier value; the
                i.i.d. interval NOT deciding (a case where it excludes 0 and the two-stage one does not reads NEITHER)
  planted       core() (the deciding path run() calls) on planted union data, values against an independent plain-loop oracle:
                HELPS (tau* > 0, D_B > 0, lower bound > 0), HURTS (F-BO fires), TAU0 (GATE chose no shrinkage), NAIVE (clustered
                EVAL: the i.i.d. interval excludes 0, the two-stage one does not -> NEITHER); the two-stage SE of D_B against a loop
                replay of run_boot's unit draws; weak regions against loops; the [TB-MIRROR] check executed
  hier          af_hier on a hand-written deep snapshot (parents, depth, ancestor matrix), the DAG refusal, the non-leaf cell
                refusal; k_hier against scipy fcluster; picks() against hand values (a zero-mass leaf: tau 0 -> best single,
                tau > 0 -> the parent's pick; three levels); the [TB-G3] refusal
  run_e2e       --run end to end on union_af_route's fixture with a DEEPENED MMLU_PRO tree (root -> 2 mids -> 4 leaves) and GATE planted
                to favour shrinkage: tau* per arm, TF, TB, D_B (point, SE, interval), KB_0, D_TK, share changed and the best single's
                weak-region gap against an INDEPENDENT oracle (snapshot parents by loops, Ward by scipy, back-off by recursion, the
                bootstrap by replaying the unit draws); BO1 / F-BO by the hand rule; a second --run refused, outcome unchanged
  refusals      pool check (POOL line first), manifest pin, policy sha, [TB-DENOM], [TB-IDENTITY], [TB-GATE-DENOM], [B3], [TB-KDIFF],
                [TB-MIRROR], B / seed, marker present; no outcome written by any
  dry_run       POOL first, structure lines, no statistic, nothing written; the REAL constants' lines
  branch_cover  every print / refusal branch executed
MUTANTS (--mutants; the exact edits are the MUTANTS table at the end of this file; each edits the code ABOVE the SELFTEST marker in
memory, on the selftest's sandbox fixtures only): 2026-10-06, 64 of 64 KILLED, control X00 SURVIVED. First pass 60 / 64: X13 (tau 0
without the mass < 1 back-off: equivalent on fixtures whose best single is model 0) killed by a hand case where it is model 1; X36
(nested weak regions: equal region on the planted data) killed by the coverage check; X61 (GATE K cells filed among all sources)
killed by moving the fixture's MATH GATE vectors onto the BBH direction and comparing K0's GATE counts; X43 (rule 8 ignoring tau* =
0) was EQUIVALENT (tau* = 0 forces D_B = 0 identically, hence lo = 0, enforced by the [TB-MIRROR] refusal in core) and was replaced by
X43 (rule 8 ignoring the lower bound), killed. Classes: verdict boundaries and clauses (X01-X06, X42-X44), the naive i.i.d. interval
(X06), sign / wrong arm / wrong population (X07, X08, X27, X29, X31, X34), tau selection (X09-X11, X55, X60, X61), the back-off
recursion (X13-X19: root vs parent, first level only, argmin, denominator, no aggregation), the hierarchies (X20-X23, X62), the hook
and the bootstrap (X24-X26, X56-X58, X63), descriptive values (X28, X30, X32, X33, X35-X39), Brier and skip paths (X40, X41, X45-X48),
every refusal / gate (X12, X49-X54, X59, X64).
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

import json          # noqa: E402
import types         # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc, union_cells_io, union_af_route -> v2_declared_cells)

MY_PINS = (("union_route_common.py", "d54739769d38a3a402e2deaab9e45109cd86de4e"),
           ("union_cells_io.py", "92a04543b9c75eae5f37a76ae86eb189a190a9bd"),
           ("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"),
           ("v2_declared_cells.py", "f0f568057995b5d0231da6e3d0d48755a7cf8386"),
           ("escalation_curve.py", "0acfb0cce8d1c91e3365c3f6099172c6d4ccc929"))
for _name, _pin in MY_PINS:
    if U.blob_lf(os.path.join(HERE, _name)) != _pin:
        raise SystemExit("[TB] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_name, U.blob_lf(os.path.join(HERE, _name)), _pin))
import escalation_curve as EC    # noqa: E402  (gate_key, EC-R7: the GATE key reader of record)
from scipy.cluster.hierarchy import linkage   # noqa: E402

ERC, UAR, V, GB, GC = U.ERC, U.UAR, U.V, U.GB, U.GC
UCI = U.UCI
FM = GC.FM

TAG = "[TB]"
TEST_ID = "TREE-BACKOFF"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-06 (before any code or call) — TREE-BACKOFF: on the content-closed v2'
            ' union split, does the tree\'s HIERARCHY improve a routing decision, ..." L24814-L24826 (_as_of 9bff7e39, parent 4c764a1e)')
OUT = "experiment_results/archv2/tree_backoff"
TAUS = (0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000)
COVS = (0.05, 0.10, 0.20)
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/tree_backoff.READ_STARTED", n_gate_key=1944, n_xsrc=191, taus=TAUS)
FIXTURE_REG = dict(out="res/tb/outcome.txt", marker="res/tb/READ_STARTED")
_REG = [REG]


def reg():
    return _REG[0]


UNION = "<UNION>"
PSEUDO = (V.NO_ROUTING_ROW, UAR.UNROUTED)
SUPPORT = dict(deff=1.302, n_eff=4537, se=0.00255, mde=0.0071)
VERDICT_LINE = ("BO1 DESCRIPTIVE-ONLY at the prediction (D_B +0.30pp lies 0.30pp from the bar 0, short of the MDE80 0.71pp); BO1 is"
                " scored as registered and NEITHER is then the expected word (never 'the hierarchy does not help')")
PRED_TAU = (5, 100)
P_TAU0 = 0.15
PRED_DB = (-0.003, 0.009)
PROB_BO1 = (("HIERARCHY-HELPS", 0.15), ("NEITHER", 0.80), ("HIERARCHY-HURTS", 0.05))
PRED_DKB = (-0.003, 0.009)
PRED_DTK = (-0.014, 0.006)
PRED_SHARE = (0.05, 0.35)
P_BBH = 0.55
PRED_WR = (-0.20, -0.03)
P_WR_NEAR = 0.60
WR_NEAR = 0.03
HIT = Counter()
KNAMES = U.KNAMES
ARMS = ("AF",) + KNAMES


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the hierarchies (R1, R2) ───────────────────────────────────────────────────────────────────────────────────────────────

class Hier:
    """A rooted tree over named nodes: parent index (-1 = the union root), depth, the ancestor-or-self matrix M (M[a, v] = 1 iff a is
    v or an ancestor of v), the depth levels (top-down order) and the set of nodes an item may be filed to (leaves)."""

    def __init__(self, label, names, parents, leaves):
        self.label = label
        self.names = list(names)
        self.idx = {n: i for i, n in enumerate(self.names)}
        if len(self.idx) != len(self.names):
            hit("REFUSE.HIER")
            refuse("[TB-HIER] %s: repeated node names" % label)
        miss = sorted(set(p for p in parents if p is not None and p not in self.idx))
        if miss:
            hit("REFUSE.HIER")
            refuse("[TB-HIER] %s: parent(s) %s are not nodes" % (label, miss[:3]))
        N = len(self.names)
        self.N = N
        self.parent = np.array([-1 if p is None else self.idx[p] for p in parents], dtype=np.int64)
        roots = np.flatnonzero(self.parent < 0)
        if len(roots) != 1:
            hit("REFUSE.HIER")
            refuse("[TB-HIER] %s: %d roots" % (label, len(roots)))
        self.root = int(roots[0])
        self.M = np.zeros((N, N), dtype=np.float64)
        self.depth = np.zeros(N, dtype=np.int64)
        for v in range(N):
            a, d = v, 0
            while a >= 0:
                self.M[a, v] = 1.0
                a = int(self.parent[a])
                d += 1
                if d > N:
                    hit("REFUSE.HIER")
                    refuse("[TB-HIER] %s: a cycle through %s" % (label, self.names[v]))
            self.depth[v] = d - 1
        self.levels = [np.flatnonzero(self.depth == d) for d in range(1, int(self.depth.max()) + 1)]
        self.leaf = np.array([n in leaves for n in self.names], dtype=bool)
        self.pseudo = np.array([n in PSEUDO for n in self.names], dtype=bool)

    def summary(self):
        real = self.leaf & ~self.pseudo
        return "%d nodes, %d filing leaves (+%d pseudo), %d internal (union root included), max depth %d" % (
            self.N, int(real.sum()), int((self.leaf & self.pseudo).sum()), int((~self.leaf).sum()), int(self.depth.max()))


def af_hier(members, afu, single, snap_reader=None):
    """R1: the AF-U hierarchy from every member's LAST dag snapshot (+ one-cell members and the pseudo-leaves)."""
    snap_reader = snap_reader or (lambda m: GB.last_snapshot(U.P("%s/%s/seed_42/dag_snapshots.jsonl" % (afu, m))))
    names, parents, leaves = [UNION], [None], set()
    for m, so in members:
        if so in single:
            cell = single[so]["cell"]
            names.append(cell)
            parents.append(UNION)
            leaves.add(cell)
            continue
        snap = snap_reader(m)
        nroot = 0
        for n in snap["nodes"]:
            pids = n.get("parentIds") or []
            if len(pids) > 1:
                hit("REFUSE.HIER")
                refuse("[TB-HIER] AF-U node %s:%s has %d parents (a DAG; the registration reads the tree as built)" % (so, n["id"], len(pids)))
            names.append("%s:%s" % (so, n["id"]))
            parents.append("%s:%s" % (so, pids[0]) if pids else UNION)
            nroot += 0 if pids else 1
            if n.get("isLeaf"):
                leaves.add("%s:%s" % (so, n["id"]))
        if nroot != 1:
            hit("REFUSE.HIER")
            refuse("[TB-HIER] member %s's last snapshot has %d roots" % (m, nroot))
    for p in PSEUDO:
        names.append(p)
        parents.append(UNION)
        leaves.add(p)
    return Hier("AF-U", names, parents, leaves)


def k_hier(seed, C, csrc, cloc, sources):
    """R2: K-WARD for seed s: per source, Ward (Euclidean) on the renormalised filing centroids; top merge -> union root."""
    names, parents, leaves = [UNION], [None], set()
    for so in sources:
        rows = np.flatnonzero(np.asarray(csrc) == so)
        k = len(rows)
        lv = ["K%d:%s:%03d" % (seed, so, int(cloc[j])) for j in rows]
        leaves |= set(lv)
        if k == 1:
            names.append(lv[0])
            parents.append(UNION)
            continue
        Z = linkage(FM.unit_rows(np.asarray(C, dtype=np.float64)[rows]), method="ward")
        inner = ["K%d:%s:w%03d" % (seed, so, j) for j in range(k - 1)]
        par = {}
        for j in range(k - 1):
            for ch in (int(Z[j, 0]), int(Z[j, 1])):
                par[ch] = k + j

        def nm(i):
            return lv[i] if i < k else inner[i - k]
        for i in range(2 * k - 1):
            names.append(nm(i))
            parents.append(nm(par[i]) if i in par else UNION)
    for p in PSEUDO:
        names.append(p)
        parents.append(UNION)
        leaves.add(p)
    return Hier("K-WARD K%d" % seed, names, parents, leaves)


class Arm:
    """One back-off arm: a hierarchy, the node of every scored position, the node of every GATE item."""

    def __init__(self, label, h, pos_names, gate_names, m):
        self.label, self.h = label, h
        for what, nn in (("scored item", pos_names), ("GATE item", gate_names)):
            bad = sorted(set(n for n in nn if n not in h.idx or not h.leaf[h.idx[n]]))
            if bad:
                hit("REFUSE.HIER")
                refuse("[TB-HIER] %s: %d %s cell(s) are not filing leaves of the hierarchy (first %s)" % (label, len(bad), what, bad[:3]))
        self.pos = np.array([h.idx[n] for n in pos_names], dtype=np.int64)
        self.gate = np.array([h.idx[n] for n in gate_names], dtype=np.int64)
        self.flat = (self.pos[:, None] * m + np.arange(m)[None, :]).ravel()


def node_stats(D, arm, w):
    """R3: (s_v,m, n_v) over every node from the integer TRAIN weights w (positions); the support must be TRAIN."""
    w = np.asarray(w)
    if D.is_eval[w != 0].any():
        hit("REFUSE.G3")
        refuse("[TB-G3] a node fit received %d EVAL item(s)" % int(D.is_eval[w != 0].sum()))
    N, m = arm.h.N, len(D.models)
    Sd = np.bincount(arm.flat, weights=(D.A * w[:, None]).ravel().astype(np.float64), minlength=N * m).reshape(N, m)
    nd = np.bincount(arm.pos, weights=w.astype(np.float64), minlength=N)
    return arm.h.M @ Sd, arm.h.M @ nd


def picks(h, S, n, tau):
    """R3: the pick of every node at strength tau -> (picks, best single). tau = 0 is V.fit (mass < 1 -> best single)."""
    gb = int(np.argmax(S[h.root]))
    if tau == 0:
        pk = S.argmax(axis=1).astype(np.int64)
        pk[n < 1] = gb
        return pk, gb
    p = np.empty_like(S)
    p[h.root] = S[h.root] / n[h.root]
    for lev in h.levels:
        p[lev] = (S[lev] + tau * p[h.parent[lev]]) / (n[lev] + tau)[:, None]
    return p.argmax(axis=1).astype(np.int64), gb


def choose_tau(D, arm, Kg, taus):
    """R4: tau* = the first maximum of the GATE correct count on the increasing grid -> (tau*, counts)."""
    S, n = node_stats(D, arm, V.train_full(D))
    r = np.arange(len(arm.gate))
    counts = []
    for t in taus:
        pk, _gb = picks(arm.h, S, n, t)
        counts.append(int(Kg[r, pk[arm.gate]].sum()))
    j = int(np.argmax(counts))
    return taus[j], counts


def weak_region(h, S, n, mdl, cov, allowed):
    """R10: greedy non-nested nodes by lowest TRAIN accuracy until TRAIN coverage >= cov -> (chosen nodes, coverage)."""
    ntr = float(n[h.root])
    cand = [int(v) for v in allowed if n[v] > 0]
    acc = {v: S[v, mdl] / n[v] for v in cand}
    order = sorted(cand, key=lambda v: (acc[v], -n[v], h.names[v]))
    chosen, covered = [], 0.0
    for v in order:
        if covered >= cov * ntr:
            break
        if any(h.M[v, u] or h.M[u, v] for u in chosen):
            continue
        chosen.append(v)
        covered += float(n[v])
    return chosen, covered / ntr


def region_gap(D, arm, chosen, mdl):
    """EVAL accuracy of the region (items filed below a chosen node) and its gap to the model's EVAL mean -> (n, acc, gap)."""
    if not chosen:
        return 0, float("nan"), float("nan")
    inreg = arm.h.M[np.asarray(chosen)][:, arm.pos[D.E]].any(axis=0)
    col = D.A[D.E, mdl].astype(np.float64)
    if not inreg.any():
        return 0, float("nan"), float("nan")
    a = float(col[inreg].mean())
    return int(inreg.sum()), a, a - float(col.mean())


# ── the deciding path (run() calls it after every precondition; the planted selftest calls it on planted data) ────────────────

# column order of the hook's arm matrix
TF, TB = 0, 1
KF0, KB0 = 2, 7
BEST = 12
NCOL = 13


def masks_of(D, arm_af):
    """run_boot's subsets (ALL, NON_BBH, SRC:*) + NO_XSRC (R8: EVAL items filed to a leaf of their own source)."""
    own = np.array([UCI.cell_member(arm_af.h.names[arm_af.pos[k]]) == D.src[k] for k in D.E], dtype=bool)
    return list(D.subsets) + [("NO_XSRC", own)], int((~own).sum())


def arm_matrix(D, arms, taus_star, w):
    """Per EVAL position the correctness of TF, TB, KF_s, KB_s (s = 0..4) and the best single, from the TRAIN weights w."""
    rows = np.empty((NCOL, len(D.E)), dtype=np.float64)
    gbs, pk = set(), {}
    for j, nm in enumerate(ARMS):
        a = arms[nm]
        S, n = node_stats(D, a, w)
        p0, gb = picks(a.h, S, n, 0)
        pt, _g = picks(a.h, S, n, taus_star[nm])
        gbs.add(gb)
        e0, et = p0[a.pos[D.E]], pt[a.pos[D.E]]
        pk[nm] = (e0, et)
        c0, ct = (TF, TB) if nm == "AF" else (KF0 + j - 1, KB0 + j - 1)
        rows[c0] = D.A[D.E, e0]
        rows[ct] = D.A[D.E, et]
    if len(gbs) != 1:
        refuse("[TB-MIRROR] the arms disagree on the best single %s" % sorted(gbs))
    rows[BEST] = D.A[D.E, gbs.pop()]
    return rows, pk


def score(CE, v, masks):
    out = np.empty((len(masks), CE.shape[0]))
    for j, (_n, mk) in enumerate(masks):
        vv = v * mk
        out[j] = CE @ vv / vv.sum() if vv.sum() else np.nan
    return out


def mirror_check(D, bt, point, iid, two):
    """[TB-MIRROR]: the hook's tau = 0 arms equal run_boot's TREE / K_s / best-single arms everywhere on run_boot's subsets."""
    ns = len(D.subsets)
    pairs = [(TF, V.TREE), (BEST, V.BS)] + [(KF0 + s, U.karm(D, nm)) for s, nm in enumerate(KNAMES)]
    for mine, theirs in pairs:
        for lab, a, b in (("point", point[:ns, mine], bt["point"][:, theirs]), ("i.i.d.", iid[:, :ns, mine], bt["iid"][:, :, theirs]),
                          ("two-stage", two[:, :ns, mine], bt["two"][:, :, theirs])):
            if a.shape != b.shape or not np.allclose(a, b, rtol=0.0, atol=1e-12, equal_nan=True):
                hit("REFUSE.MIRROR")
                refuse("[TB-MIRROR] the hook's tau = 0 column %d differs from run_boot's arm %d (%s)" % (mine, theirs, lab))


def core(D, arms, Kg, c, after_boot=None):
    """tau* on GATE, run_boot with the back-off hook, the mirror check, every contrast and descriptive -> st (no printing)."""
    taus = {nm: choose_tau(D, arms[nm], Kg, c["taus"]) for nm in ARMS}
    tstar = {nm: taus[nm][0] for nm in ARMS}
    masks, n_xsrc = masks_of(D, arms["AF"])
    two_rows = []

    def hook(D_, wt, v):
        CE, _pk = arm_matrix(D_, arms, tstar, wt)
        two_rows.append(score(CE, v, masks))
    bt = V.run_boot(D, c["B"], c["seed"], hook=hook)
    if after_boot is not None:
        after_boot(bt)
    if len(two_rows) != c["B"]:
        refuse("[TB-HOOK] the back-off hook ran %d times, not B %d" % (len(two_rows), c["B"]))
    NE = len(D.E)
    CE0, pk0 = arm_matrix(D, arms, tstar, V.train_full(D))
    point = score(CE0, np.ones(NE), masks)
    iid = np.stack([score(CE0, vi, masks) for vi in U.iid_weights(c["seed"], NE, c["B"])])
    two = np.stack(two_rows)
    mirror_check(D, bt, point, iid, two)
    names = [nm for nm, _m in masks]

    def lin(wv, sub="ALL"):
        j = names.index(sub)
        n = int(masks[j][1].sum())
        return U.interval(float(point[j] @ wv), two[:, j, :] @ wv, iid[:, j, :] @ wv, n)

    def e(*cols, wts=None):
        wv = np.zeros(NCOL)
        for k_, col in enumerate(cols):
            wv[col] += 1.0 if wts is None else wts[k_]
        return wv
    w_db = e(TB, TF, wts=(1.0, -1.0))
    w_kb = np.zeros(NCOL)
    w_kb[KB0:KB0 + 5] = 0.2
    w_kf = np.zeros(NCOL)
    w_kf[KF0:KF0 + 5] = 0.2
    db = lin(w_db)
    if tstar["AF"] == 0 and (db["point"] != 0.0 or db["se2"] != 0.0):
        refuse("[TB-MIRROR] tau* = 0 but D_B is not identically 0")
    st = dict(n=NE, comp=D.eval_units["n_units"], kish=U.kish_eval(D), n_train=D.n_train, B=c["B"], n_gate=len(Kg), taus=taus,
              tstar=tstar, db=db, db_sub={nm: lin(w_db, nm) for nm in names if nm != "ALL"}, n_xsrc=n_xsrc,
              dtk=lin(e(TB) - w_kb), dkb=lin(w_kb - w_kf), dbmkb=lin(w_db - (w_kb - w_kf)),
              kb_pts=[float(point[0, KB0 + s]) for s in range(5)], kf_pts=[float(point[0, KF0 + s]) for s in range(5)],
              acc={"TF": float(point[0, TF]), "TB": float(point[0, TB]), "BEST": float(point[0, BEST]),
                   "SRC": float(bt["point"][0, V.TSRC])},
              gain={nm: lin(e(col) - e(BEST)) for nm, col in (("TF", TF), ("TB", TB))})
    st["dkb_s"] = [st["kb_pts"][s] - st["kf_pts"][s] for s in range(5)]
    st["spread_kb"] = max(st["kb_pts"]) - min(st["kb_pts"])
    e0, et = pk0["AF"]
    ch = e0 != et
    srcE = np.array([D.src[k] for k in D.E])
    st["share"] = float(ch.mean())
    st["share_src"] = {s: (float(ch[srcE == s].mean()), int((srcE == s).sum())) for s in sorted(set(srcE.tolist()))}
    st["share_k"] = [float((pk0[nm][0] != pk0[nm][1]).mean()) for nm in KNAMES]
    d_item = CE0[TB] - CE0[TF]
    st["contrib_bbh"] = float(d_item[srcE == "BBH"].sum()) / NE
    st["bbh_carries"] = bbh_carries(st["contrib_bbh"], db["point"])
    st["weak"] = weak_regions(D, arms)
    st["best_name"] = D.models[int(np.argmax(node_stats(D, arms["AF"], V.train_full(D))[0][arms["AF"].h.root]))]
    st["bt"] = bt
    return st


def bbh_carries(contrib, d_b):
    """R9: P5's event: D_B != 0 and BBH's contribution is more than half of D_B (same sign)."""
    return bool(d_b != 0.0 and contrib / d_b > 0.5)


def weak_regions(D, arms):
    """R10 for every model and coverage: AF-U any depth; K-WARD any depth and KF leaves only (seed means)."""
    w = V.train_full(D)
    stats = {nm: node_stats(D, arms[nm], w) for nm in ARMS}

    def allowed(h, leaves_only):
        ok = ~h.pseudo & (np.arange(h.N) != h.root)
        if leaves_only:
            ok &= h.leaf
        return np.flatnonzero(ok)
    out = {}
    for mdl in range(len(D.models)):
        for cov in COVS:
            S, n = stats["AF"]
            ch, cv = weak_region(arms["AF"].h, S, n, mdl, cov, allowed(arms["AF"].h, False))
            n_af, a_af, g_af = region_gap(D, arms["AF"], ch, mdl)
            kw, kf = [], []
            for nm in KNAMES:
                S, n = stats[nm]
                h = arms[nm].h
                chw, _c = weak_region(h, S, n, mdl, cov, allowed(h, False))
                chf, _c = weak_region(h, S, n, mdl, cov, allowed(h, True))
                kw.append(region_gap(D, arms[nm], chw, mdl)[2])
                kf.append(region_gap(D, arms[nm], chf, mdl)[2])
            out[(mdl, cov)] = dict(af=(len(ch), cv, n_af, a_af, g_af), kw=_nanmean(kw), kf=_nanmean(kf))
    return out


def _nanmean(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


# ── the verdict and every printed line ────────────────────────────────────────────────────────────────────────────────

def bo1_verdict(db, tau_af):
    if tau_af == 0:
        return "NEITHER", True
    helps = db["point"] > 0 and db["lo"] > 0
    hurts = db["point"] < 0 and db["hi"] < 0
    if helps and hurts:
        refuse("[BO1-OVERLAP] both words fire on the same data (registration defect; for the registrar)")
    if helps:
        return "HIERARCHY-HELPS", False
    if hurts:
        return "HIERARCHY-HURTS", False
    return "NEITHER", False


def _f(x, fmt="%+.4f"):
    return "n/a" if x != x else fmt % x


def tb_lines(st, models):
    """Every line of the outcome after the identity (the outcome prints them verbatim); -> (lines, words)."""
    L = []
    db, ts = st["db"], st["tstar"]
    L.append("=== TREE-BACKOFF BO1 (%s) ===" % REG_TEXT)
    L.append("DENOMINATOR: %d EVAL items in %d components (Kish mean cluster size %.3f; Support (a) 5907 / 5404); TRAIN %d scored items"
             " (G14's policy-fit set; every node accuracy); GATE %d key-complete items (tau only; registered 1944); B %d two-stage"
             " replicates" % (db["n"], st["comp"], st["kish"], st["n_train"], st["n_gate"], st["B"]))
    L.append("LIKE WITH LIKE: TF / TB AF-U cells, hierarchy none / AF-U's own [SC] | KF / KB per-source k-means K_s, none / Ward on"
             " centroids within source [SC] | SRC 6 sources [SC] | BEST one cell (n/a); TB vs TF is like with like (same cells, same"
             " filing; only the use of the hierarchy differs); every arm [SC], none label-free")
    for nm in ARMS:
        t, cnt = st["taus"][nm]
        L.append("TAU (GATE, R4) %-3s tau* = %s | GATE correct counts over the grid %s: %s" % (
            nm, t, "/".join(str(x) for x in reg()["taus"]), " ".join(str(x) for x in cnt)))
    a = st["acc"]
    L.append("ARMS (EVAL accuracy, point): BEST %.5f | SRC %.5f | TF %.5f | TB %.5f | KF_s %s | KB_s %s" % (
        a["BEST"], a["SRC"], a["TF"], a["TB"], " / ".join("%.5f" % x for x in st["kf_pts"]), " / ".join("%.5f" % x for x in st["kb_pts"])))
    for nm in ("TF", "TB"):
        g = st["gain"][nm]
        L.append("  G_%s = acc(%s) - acc(BEST) = %s (%+.5f) | two-stage 95%% [%s, %s]" % (nm, nm, U.pp(g["point"]), g["point"], U.pp(g["lo"]), U.pp(g["hi"])))
    L.append("BO1 (THE ONE DECIDING CRITERION; point and interval jointly): D_B = acc(TB) - acc(TF) = %s (%+.5f) | two-stage 95%% [%s, %s]"
             " (%+.5f, %+.5f) | percentile [%s, %s] | i.i.d. 95%% [%+.5f, %+.5f] (beside, NOT deciding)" % (
                 U.pp(db["point"]), db["point"], U.pp(db["lo"]), U.pp(db["hi"]), db["lo"], db["hi"], U.pp(db["pct"][0]), U.pp(db["pct"][1]),
                 db["point"] - 1.96 * db["se_iid"], db["point"] + 1.96 * db["se_iid"]))
    L.append("  support D_B: n %d, SE_2stage %.5f (registered 0.00255), i.i.d. SE %.5f, DEFF %s (registered 1.302, transported from"
             " ESCALATION-RC RC1), n_eff %s (registered 4537), MDE80 %s (registered +0.71pp); verdict line of record: %s" % (
                 db["n"], db["se2"], db["se_iid"], _f(db["deff"], "%.3f"), _f(db["n_eff"], "%.0f"), U.pp(db["mde"]), VERDICT_LINE))
    v, tau0 = bo1_verdict(db, ts["AF"])
    if tau0:
        hit("BO1.TAU0")
        L.append("  BO1 -> NEITHER (GATE chose no shrinkage: tau*(AF-U) = 0, D_B = 0 identically)")
    elif v == "HIERARCHY-HELPS":
        hit("BO1.HELPS")
        L.append("  BO1 -> HIERARCHY-HELPS (D_B %+.5f > 0 AND its 95%% two-stage lower bound %+.5f > 0)" % (db["point"], db["lo"]))
    elif v == "HIERARCHY-HURTS":
        hit("BO1.HURTS")
        L.append("  BO1 -> HIERARCHY-HURTS (D_B %+.5f < 0 AND its 95%% two-stage upper bound %+.5f < 0)" % (db["point"], db["hi"]))
    else:
        hit("BO1.NEITHER")
        L.append("  BO1 -> NEITHER (neither HIERARCHY-HELPS: D_B > 0 and lower bound > 0; nor HIERARCHY-HURTS: D_B < 0 and upper bound"
                 " < 0; below the MDE, never 'no value')")
    if ts["AF"] == 0 or db["lo"] <= 0:
        hit("RULE8.REFUTED")
        L.append("RULE 8: HIERARCHY-HELPS is REFUTED at the planned n (%s)" % (
            "tau* = 0" if ts["AF"] == 0 else "the lower bound %+.5f <= 0" % db["lo"]))
    else:
        hit("RULE8.NOT")
        L.append("RULE 8: HIERARCHY-HELPS is not refuted (lower bound %+.5f > 0, tau* %s > 0)" % (db["lo"], ts["AF"]))
    if v == "HIERARCHY-HURTS":
        hit("FBO.FIRED")
        L.append("FALSIFIER F-BO: FIRES (BO1 HIERARCHY-HURTS): shrinking leaf accuracies toward the tree's ancestors routes worse than"
                 " the leaves alone; the working premise of the hierarchy-use line (docs/literature/2026-10-03_tree_uses.md) is overturned"
                 " for this roster, split and tree; every 'the hierarchy helps routing' sentence is withdrawn")
    else:
        hit("FBO.NOT")
        L.append("FALSIFIER F-BO: NOT FIRED (BO1 %s; F-BO fires iff HIERARCHY-HURTS)" % v)
    dtk = st["dtk"]
    L.append("SECONDARY (RULED DESCRIPTIVE by the registrar): D_TK = acc(TB) - mean_s acc(KB_s) = %s (%+.5f) | two-stage 95%% [%s, %s] |"
             " seed spread of KB_s %.5f" % (U.pp(dtk["point"]), dtk["point"], U.pp(dtk["lo"]), U.pp(dtk["hi"]), st["spread_kb"]))
    dkb, dm = st["dkb"], st["dbmkb"]
    L.append("DESCRIPTIVE: D_KB = mean_s acc(KB_s) - mean_s acc(KF_s) = %s (%+.5f) | two-stage 95%% [%s, %s]; per seed %s" % (
        U.pp(dkb["point"]), dkb["point"], U.pp(dkb["lo"]), U.pp(dkb["hi"]), " / ".join("%+.5f" % x for x in st["dkb_s"])))
    L.append("DESCRIPTIVE: D_B - D_KB (hierarchy dividend, AF-U minus K-WARD) = %s (%+.5f) | two-stage 95%% [%s, %s]" % (
        U.pp(dm["point"]), dm["point"], U.pp(dm["lo"]), U.pp(dm["hi"])))
    L.append("DESCRIPTIVE: tau* per arm AF-U %s | K-WARD K0..K4 %s" % (ts["AF"], " / ".join(str(ts[nm]) for nm in KNAMES)))
    L.append("DESCRIPTIVE: EVAL picks changed under TB %.5f (%s); K-WARD per seed %s; Support (g): |D_B| %.5f <= share %.5f: %s" % (
        st["share"], ", ".join("%s %.5f of %d" % (s, x, n) for s, (x, n) in sorted(st["share_src"].items())),
        " / ".join("%.5f" % x for x in st["share_k"]), abs(db["point"]), st["share"], "yes" if abs(db["point"]) <= st["share"] + 1e-12 else "NO"))
    for nm in sorted(st["db_sub"]):
        d = st["db_sub"][nm]
        L.append("DESCRIPTIVE: D_B on %-14s n %4d: %s (%+.5f) | two-stage 95%% [%s, %s]" % (nm, d["n"], U.pp(d["point"]), d["point"], U.pp(d["lo"]), U.pp(d["hi"])))
    L.append("  NO_XSRC drops the %d EVAL items AF-U files into another source's leaf (registered 191; KEY-INFO-V2 R-KI1)" % st["n_xsrc"])
    L.append("BBH DISCLOSURE: the union routing gains of record are BBH-dominated (CELL-FLIPS: 5 of 7 BH-surviving flips are BBH task cells"
             " won by internlm2_5-20b-chat; RESP-PROFILE-INFO P4: BBH carries the largest share of R2_int); BBH contributes %+.5f of D_B"
             " %+.5f; every D above is printed per source and without BBH (NON_BBH)" % (st["contrib_bbh"], db["point"]))
    L.append("WEAK REGIONS (optional descriptive arm, never deciding; R10): per model and TRAIN coverage c, the EVAL gap of the TRAIN-chosen"
             " weakest region (EVAL accuracy minus the model's EVAL mean; more negative = a weakness found on TRAIN and held on EVAL)")
    for cov in COVS:
        for mdl, name in enumerate(models):
            w = st["weak"][(mdl, cov)]
            k_, cv, n_, a_, g_ = w["af"]
            L.append("  c %.2f | %-34s | AF-U any depth: %d nodes, TRAIN cov %.4f, EVAL n %d, acc %s, gap %s | K-WARD any depth gap %s |"
                     " KF flat gap %s (K seed means)" % (cov, name + (" (best single)" if name == st["best_name"] else ""), k_, cv, n_,
                                                        _f(a_, "%.4f"), _f(g_), _f(w["kw"]), _f(w["kf"])))
    L.extend(pred_lines(st, v, models))
    L.append("WORDS: every arm is SOURCE-CONDITIONED [SC] (federated per source), never label-free; key-scored end to end, no judge"
             " verdict (no wrong(established) count, no tie convention A / B arises); tau* held at its GATE choice (GATE selection"
             " variance not propagated); one tree, one draw, one roster")
    L.append("WILL NOT SHOW (registered): a label-free gain (every arm [SC]); that the tree's hierarchy beats k-means' hierarchy (D_TK"
             " descriptive); judged decisions; other rosters, draws, embedders or splits; a gain outside BBH if BBH carries it; any"
             " sub-anchor profile (no per-leaf board, interval or row is published)")
    words = dict(BO1=v, TAU0=tau0, F_BO=(v == "HIERARCHY-HURTS"), RULE8=bool(ts["AF"] == 0 or db["lo"] <= 0))
    return L, words


def pred_lines(st, v, models):
    L = []
    t = st["tstar"]["AF"]
    for lab, x, band in (("P1 tau*(AF-U) in [5, 100]", t, PRED_TAU), ("P2 D_B +0.30pp [-0.30, +0.90]", st["db"]["point"], PRED_DB),
                         ("P4 D_KB +0.30pp [-0.30, +0.90]", st["dkb"]["point"], PRED_DKB),
                         ("P4 D_TK -0.40pp [-1.40, +0.60]", st["dtk"]["point"], PRED_DTK),
                         ("P5 share of EVAL picks changed 0.15 [0.05, 0.35]", st["share"], PRED_SHARE)):
        ok = U.in_band(x, band)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION %s: observed %s -> %s" % (lab, ("%+.5f" % x) if isinstance(x, float) else str(x), "HELD" if ok else "FAILED"))
    z = bool(t == 0)
    L.append("PREDICTION P1 P(tau* = 0) 0.15: observed tau* = %s (tau* = 0: %s); Brier %.4f" % (t, "yes" if z else "no", (P_TAU0 - float(z)) ** 2))
    L.append("PREDICTION P3 BO1 HIERARCHY-HELPS 0.15, NEITHER 0.80, HIERARCHY-HURTS 0.05: observed %s; Brier %.4f" % (v, U.brier(PROB_BO1, v)))
    bc = bool(st["bbh_carries"])
    hit("P5BBH.TRUE" if bc else "P5BBH.FALSE")
    L.append("PREDICTION P5 BBH carries more than half of |D_B| (probability 0.55): BBH %+.5f of D_B %+.5f -> %s; Brier %.4f" % (
        st["contrib_bbh"], st["db"]["point"], "TRUE" if bc else "FALSE", (P_BBH - float(bc)) ** 2))
    bi = models.index(st["best_name"])
    w = st["weak"][(bi, 0.10)]
    g_af, g_kf = w["af"][4], w["kf"]
    ok = bool(g_af == g_af and U.in_band(g_af, PRED_WR))
    hit("PRED.HELD" if ok else "PRED.FAILED")
    L.append("PREDICTION P6 (descriptive; weak regions, c 0.10, best single %s) AF-U any-depth EVAL gap -0.10 [-0.20, -0.03]: observed %s -> %s"
             % (st["best_name"], _f(g_af, "%+.5f"), "HELD" if ok else "FAILED"))
    near = bool(g_af == g_af and g_kf == g_kf and abs(g_af - g_kf) <= WR_NEAR)
    hit("P6NEAR.TRUE" if near else "P6NEAR.FALSE")
    L.append("PREDICTION P6 within 0.03 of the KF flat region's gap (probability 0.60): KF %s, |difference| %s -> %s; Brier %.4f" % (
        _f(g_kf, "%+.5f"), _f(abs(g_af - g_kf), "%.5f"), "TRUE" if near else "FALSE", (P_WR_NEAR - float(near)) ** 2))
    return L


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def files():
    return [os.path.abspath(__file__), U.__file__, EC.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS]


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)-(e)): %d EVAL items in %d CK-CLOSE components (Kish 1.311); DEFF 1.302 (ESCALATION-RC RC1,"
        " measured two-stage, transported), n_eff 4,537, SE(D_B) 0.255pp, MDE80 0.71pp; %s" % (c["n_route"], c["comp_route"], VERDICT_LINE))
    say("PLANNED: B = %d two-stage replicates (default_rng(%d)); tau grid %s chosen per arm on the %d key-complete GATE items; arms TF, TB,"
        " KF_s, KB_s (s = 0..4), SRC, BEST; weak-region coverages %s" % (c["B"], c["seed"], "/".join(str(t) for t in c["taus"]),
                                                                           c["n_gate_key"], "/".join("%.2f" % x for x in COVS)))
    say("COST: 0 calls, 0 CCE; CPU: %d GATE fits (11 tau x 6 arms) + %d back-off fits in the bootstrap (6 arms x (B + 1)) beside run_boot's"
        " own; minutes on one thread" % (len(c["taus"]) * 6, 6 * (c["B"] + 1)))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(c["identity"])))


def prepare(say):
    """Everything before any key: union_route_common.prepare, the hierarchies, K_s re-filing, the GATE cells."""
    c = reg()
    S = U.prepare(say, c, refuse, hit)
    u = UAR.reg()
    ip = UAR.input_paths()
    b, _meta = GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    Xt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    classes = [str(x) for x in b["classes"]]
    tsrc = np.array([UAR.src_of(classes[i]) for i in np.asarray(b["train_y"], dtype=int)])
    side, _smeta = UAR._SIDES[0]()
    val = UAR.afu_paths(S["single"])[1]
    rows_h, rows_t = ERC.item_rows(ip["merged"] if S["single"] else val)
    srcs = UAR.item_sources(rows_h + rows_t)
    gits, gcell, _gs = ERC.gate_items(rows_h, side)
    if not gits:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: tau* is undefined (R4)")
    H_af = af_hier(u["members"], u["afu"], S["single"])
    say("  AF-U HIERARCHY (R1): %s" % H_af.summary())
    ids = sorted(set(i for i, cl in S["af"].items() if cl != V.NO_ROUTING_ROW) | set(gits))
    vec = ERC.get_vectors(ids)
    nov = [i for i in ids if i not in vec]
    if nov:
        refuse("%d item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    nb = ERC.check_vectors_vs_bundle(vec, b)
    H_k, gk = {}, {}
    for s in U.SEEDS:
        C, csrc, cloc, _lab, _f = UAR.us_fit(Xt, tsrc, S["man"]["ksrc"], u["sources"], s)
        name = lambda g: "K%d:%s:%03d" % (s, csrc[g], cloc[g])
        diff = sum(1 for it, cl in S["kx"]["K%d" % s].items() if cl != V.NO_ROUTING_ROW and name(UAR.file_by_source(vec[it], srcs[it], C, csrc)) != cl)
        if diff:
            hit("REFUSE.KDIFF")
            refuse("[TB-KDIFF] K%d re-filed differs from k_cells_s%d.tsv on %d item(s)" % (s, s, diff))
        H_k[s] = k_hier(s, C, csrc, cloc, u["sources"])
        gk[s] = {it: name(UAR.file_by_source(vec[it], srcs[it], C, csrc)) for it in gits}
        say("  K-WARD K%d (R2): %s; every scored item re-filed = k_cells_s%d.tsv" % (s, H_k[s].summary(), s))
    say("  vectors equal to the bundle's on %d items; GATE items with a routing row %d (modal AF leaf; K_s cells by source)" % (nb, len(gits)))
    return dict(S, H_af=H_af, H_k=H_k, gits=gits, gcell=gcell, gk=gk)


def make_arms(D, P_, gitems):
    m = len(D.models)
    arms = {"AF": Arm("AF-U", P_["H_af"], [D.tree_keys[g] for g in D.g_tree], [P_["gcell"][i] for i in gitems], m)}
    for s, nm in enumerate(KNAMES):
        g = D.groupings["x:" + nm][0]
        arms[nm] = Arm("K-WARD " + nm, P_["H_k"][s], [D.xkeys[nm][j] for j in g], [P_["gk"][s][i] for i in gitems], m)
    return arms


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, files())
    denominators(say)
    P_ = prepare(say)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    U.read_views(cfg, say, True, P_["af"], P_["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no key read (TRAIN, GATE or EVAL); no statistic of EVAL printed.")
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
    P_ = prepare(say)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):
        refuse("the reader's B / seed %s / %s are not the registered %s / %s" % (cfg.reg["B"], cfg.reg["seed"], c["B"], c["seed"]))
    gk = {}

    def between(K_tr, train_meta, models):
        gk["K"], gk["comp"], gk["meta"] = EC.gate_key(cfg, say, models, P_["gits"])
    D, ok_sha = U.read_views(cfg, say, False, P_["af"], P_["kx"], c["marker"],
                             "TREE-BACKOFF: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit,
                             between=between, tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "TB")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    U.b3_check(D, cfg, P_["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s; AF, K0..K4, TRUE source, TRUE source/domain)"
        % P_["pol"]["best_single"])
    gitems = sorted(i for i in gk["comp"] if i in P_["gcell"])
    if len(gitems) != int(c["n_gate_key"]):
        hit("REFUSE.GATE_DENOM")
        refuse("[TB-GATE-DENOM] %d key-complete GATE items with a cell, not the registered %d" % (len(gitems), c["n_gate_key"]))
    if set(gitems) & set(D.items):
        hit("REFUSE.GATE_SIDE")
        refuse("[TB-GATE-SIDE] %d GATE item(s) are among the scored TRAIN / EVAL items" % len(set(gitems) & set(D.items)))
    Kg = np.array([[gk["K"][i][m] for m in D.models] for i in gitems], dtype=np.int64)
    say("  GATE (R4): %d key-complete GATE items with a cell (registered %d); never among the scored items" % (len(gitems), c["n_gate_key"]))
    arms = make_arms(D, P_, gitems)

    def after_boot(bt):
        if D.fit_asserts != c["B"] + 2:
            refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, c["B"] + 2))
        ok, got = U.identity(bt, D, c["identity"])
        if not ok:
            hit("REFUSE.IDENTITY")
            refuse("[TB-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
        say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
        hit("IDENTITY.OK")
    st = core(D, arms, Kg, c, after_boot=after_boot)
    say("  MIRROR (R3): the hook's tau = 0 arms equal run_boot's TREE / K_s / best-single arms at the point and in every replicate")
    L, words = tb_lines(st, D.models)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, arms=arms, Kg=Kg, gitems=gitems)


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
        return run_mutants(only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

import io            # noqa: E402
import re            # noqa: E402
import copy          # noqa: E402
import csv           # noqa: E402
import contextlib    # noqa: E402

BRANCHES = ("BO1.HELPS", "BO1.HURTS", "BO1.NEITHER", "BO1.TAU0", "RULE8.REFUTED", "RULE8.NOT", "FBO.FIRED", "FBO.NOT", "PRED.HELD",
            "PRED.FAILED", "P5BBH.TRUE", "P5BBH.FALSE", "P6NEAR.TRUE", "P6NEAR.FALSE", "IDENTITY.OK", "RUN.DONE", "DRY.DONE",
            "MARKER.WRITTEN", "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.POLICY_SHA", "REFUSE.MANIFEST", "REFUSE.DENOM",
            "REFUSE.IDENTITY", "REFUSE.B3", "REFUSE.GATE_DENOM", "REFUSE.GATE_SIDE", "REFUSE.KDIFF", "REFUSE.MIRROR", "REFUSE.G3", "REFUSE.HIER")
need = U.need


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _ci(pt, lo, hi, se_iid=0.0015, n=5907):
    return dict(point=pt, lo=lo, hi=hi, pct=(lo, hi), se2=(hi - lo) / 3.92, se_iid=se_iid, deff=1.3, n_eff=4540.0, mde=0.0071, n=n)


SYN_MODELS = ["Qwen2.5-72B-Instruct", "internlm2_5-20b-chat", "m3"]


def _syn(db=(0.003, -0.002, 0.008), tau=20, dkb=0.002, dtk=-0.004, share=0.15, contrib=0.001, g_af=-0.10, g_kf=-0.08, se_iid=0.0015):
    weak = {(m, cv): dict(af=(3, cv + 0.001, 50, 0.5, g_af if (m == 0 and cv == 0.10) else -0.05), kw=-0.09,
                          kf=g_kf if (m == 0 and cv == 0.10) else -0.04) for m in range(3) for cv in COVS}
    ts = {nm: tau for nm in ARMS}
    return dict(n=5907, comp=5404, kish=1.311, n_train=11841, B=2000, n_gate=1944, taus={nm: (tau, [10] * 11) for nm in ARMS}, tstar=ts,
                db=_ci(*db, se_iid=se_iid), db_sub={"NON_BBH": _ci(0.001, -0.004, 0.006, n=4000), "NO_XSRC": _ci(0.002, -0.003, 0.007, n=5716)},
                n_xsrc=191, dtk=_ci(dtk, dtk - 0.008, dtk + 0.008), dkb=_ci(dkb, dkb - 0.004, dkb + 0.004),
                dbmkb=_ci(db[0] - dkb, -0.01, 0.01), kb_pts=[0.62, 0.63, 0.625, 0.628, 0.621], kf_pts=[0.62, 0.627, 0.62, 0.626, 0.62],
                acc=dict(TF=0.6201, TB=0.6231, BEST=0.6049, SRC=0.6150), gain={"TF": _ci(0.0152, 0.0014, 0.0291), "TB": _ci(0.0182, 0.004, 0.032)},
                dkb_s=[0.0, 0.003, 0.005, 0.002, 0.001], spread_kb=0.01, share=share, share_src={"BBH": (0.3, 1500), "MATH": (0.1, 900)},
                share_k=[0.1] * 5, contrib_bbh=contrib, bbh_carries=bbh_carries(contrib, db[0]), weak=weak,
                best_name=SYN_MODELS[0])


def st_branches():
    B3 = {"HIERARCHY-HELPS": 0.7225 + 0.64 + 0.0025, "NEITHER": 0.0225 + 0.04 + 0.0025, "HIERARCHY-HURTS": 0.0225 + 0.64 + 0.9025}
    cases = [(dict(db=(0.004, 0.0001, 0.008)), "HIERARCHY-HELPS"),
             (dict(db=(0.004, 0.0, 0.008)), "NEITHER"),                 # lower bound exactly 0: not wholly above
             (dict(db=(-0.004, -0.008, -0.0001)), "HIERARCHY-HURTS"),
             (dict(db=(-0.004, -0.008, 0.0)), "NEITHER"),               # upper bound exactly 0
             (dict(db=(0.003, -0.002, 0.008)), "NEITHER"),
             (dict(db=(0.003, -0.002, 0.008), se_iid=0.0005), "NEITHER"),   # the i.i.d. interval excludes 0; it does not decide
             (dict(db=(0.0, 0.0, 0.0), tau=0), "NEITHER"),
             (dict(db=(0.0, 0.001, 0.002)), "NEITHER")]                 # point 0 with lo > 0 (degenerate): not HELPS
    for kw, want in cases:
        st = _syn(**kw)
        L, w = tb_lines(st, SYN_MODELS)
        t = "\n".join(L)
        assert w["BO1"] == want, (kw, w)
        tau0 = kw.get("tau", 20) == 0
        if tau0:
            need(t, "  BO1 -> NEITHER (GATE chose no shrinkage: tau*(AF-U) = 0, D_B = 0 identically)")
            assert w["TAU0"] is True
        else:
            need(t, "  BO1 -> %s (" % want)
            assert "GATE chose no shrinkage" not in t
        db = kw["db"]
        need(t, "D_B = acc(TB) - acc(TF) = %s (%+.5f) | two-stage 95%% [%s, %s] (%+.5f, %+.5f)" % (U.pp(db[0]), db[0], U.pp(db[1]), U.pp(db[2]), db[1], db[2]),
             "verdict line of record: " + VERDICT_LINE, "(beside, NOT deciding)", "WILL NOT SHOW (registered)", "BBH DISCLOSURE", "[SC]",
             "LIKE WITH LIKE", "DENOMINATOR: 5907 EVAL items in 5404 components", "support D_B: n 5907",
             "PREDICTION P3 BO1 HIERARCHY-HELPS 0.15, NEITHER 0.80, HIERARCHY-HURTS 0.05: observed %s; Brier %.4f" % (want, B3[want]),
             "SECONDARY (RULED DESCRIPTIVE by the registrar): D_TK", "NO_XSRC drops the 191 EVAL items")
        refuted = tau0 or db[1] <= 0
        assert w["RULE8"] is refuted
        if tau0:
            need(t, "RULE 8: HIERARCHY-HELPS is REFUTED at the planned n (tau* = 0)")
        elif refuted:
            need(t, "RULE 8: HIERARCHY-HELPS is REFUTED at the planned n (the lower bound %+.5f <= 0)" % db[1])
        else:
            need(t, "RULE 8: HIERARCHY-HELPS is not refuted (lower bound %+.5f > 0, tau* 20 > 0)" % db[1])
        if want == "HIERARCHY-HURTS":
            assert w["F_BO"] is True
            need(t, "FALSIFIER F-BO: FIRES (BO1 HIERARCHY-HURTS)")
        else:
            assert w["F_BO"] is False
            need(t, "FALSIFIER F-BO: NOT FIRED (BO1 %s; F-BO fires iff HIERARCHY-HURTS)" % want)
    for tau, want in ((5, "HELD"), (100, "HELD"), (2, "FAILED"), (200, "FAILED")):
        need("\n".join(tb_lines(_syn(tau=tau), SYN_MODELS)[0]), "PREDICTION P1 tau*(AF-U) in [5, 100]: observed %d -> %s" % (tau, want))
    t0 = "\n".join(tb_lines(_syn(tau=0, db=(0.0, 0.0, 0.0)), SYN_MODELS)[0])
    need(t0, "PREDICTION P1 P(tau* = 0) 0.15: observed tau* = 0 (tau* = 0: yes); Brier 0.7225")
    need("\n".join(tb_lines(_syn(), SYN_MODELS)[0]), "PREDICTION P1 P(tau* = 0) 0.15: observed tau* = 20 (tau* = 0: no); Brier 0.0225")
    for d_, want in ((-0.003, "HELD"), (0.009, "HELD"), (-0.0031, "FAILED"), (0.0091, "FAILED")):
        need("\n".join(tb_lines(_syn(db=(d_, d_ - 0.005, d_ + 0.005)), SYN_MODELS)[0]), "PREDICTION P2 D_B +0.30pp [-0.30, +0.90]: observed %+.5f -> %s" % (d_, want))
    for d_, want in ((-0.003, "HELD"), (0.009, "HELD"), (-0.0031, "FAILED"), (0.0091, "FAILED")):
        need("\n".join(tb_lines(_syn(dkb=d_), SYN_MODELS)[0]), "PREDICTION P4 D_KB +0.30pp [-0.30, +0.90]: observed %+.5f -> %s" % (d_, want))
    for d_, want in ((-0.014, "HELD"), (0.006, "HELD"), (-0.0141, "FAILED"), (0.0061, "FAILED")):
        need("\n".join(tb_lines(_syn(dtk=d_), SYN_MODELS)[0]), "PREDICTION P4 D_TK -0.40pp [-1.40, +0.60]: observed %+.5f -> %s" % (d_, want))
    for d_, want in ((0.05, "HELD"), (0.35, "HELD"), (0.0499, "FAILED"), (0.3501, "FAILED")):
        need("\n".join(tb_lines(_syn(share=d_), SYN_MODELS)[0]), "PREDICTION P5 share of EVAL picks changed 0.15 [0.05, 0.35]: observed %+.5f -> %s" % (d_, want))
    for contrib, db, want, br in ((0.0016, 0.003, "TRUE", 0.2025), (0.0015, 0.003, "FALSE", 0.3025), (-0.002, -0.003, "TRUE", 0.2025),
                                  (0.002, -0.003, "FALSE", 0.3025), (0.001, 0.0, "FALSE", 0.3025)):
        t = "\n".join(tb_lines(_syn(db=(db, db - 0.004, db + 0.004), contrib=contrib), SYN_MODELS)[0])
        need(t, "PREDICTION P5 BBH carries more than half of |D_B| (probability 0.55): BBH %+.5f of D_B %+.5f -> %s; Brier %.4f" % (contrib, db, want, br))
    for g_af, g_kf, held, near in ((-0.20, -0.17, "HELD", "TRUE"), (-0.03, -0.0601, "HELD", "FALSE"), (-0.2001, -0.2001, "FAILED", "TRUE"),
                                   (-0.0299, -0.0299, "FAILED", "TRUE"), (float("nan"), -0.05, "FAILED", "FALSE")):
        t = "\n".join(tb_lines(_syn(g_af=g_af, g_kf=g_kf), SYN_MODELS)[0])
        need(t, "best single Qwen2.5-72B-Instruct) AF-U any-depth EVAL gap -0.10 [-0.20, -0.03]: observed %s -> %s" % (_f(g_af, "%+.5f"), held),
             "within 0.03 of the KF flat region's gap (probability 0.60): KF %+.5f, |difference| %s -> %s; Brier %.4f" % (
                 g_kf, _f(abs(g_af - g_kf), "%.5f"), near, (0.6 - (near == "TRUE")) ** 2))
    t = "\n".join(tb_lines(_syn(), SYN_MODELS)[0])
    need(t, "  c 0.10 | Qwen2.5-72B-Instruct (best single)", "Support (g): |D_B| 0.00300 <= share 0.15000: yes",
         "DESCRIPTIVE: D_B on NO_XSRC        n 5716: +0.20pp", "seed spread of KB_s 0.01000", "i.i.d. 95% [+0.00006, +0.00594]")
    assert abs(U.brier(PROB_BO1, "NEITHER") - B3["NEITHER"]) < 1e-12
    for contrib, d_b, want in ((0.0015, 0.003, False), (0.00150001, 0.003, True), (-0.0016, -0.003, True), (0.0016, -0.003, False),
                               (0.001, 0.0, False), (0.004, 0.003, True)):
        assert bbh_carries(contrib, d_b) is want, (contrib, d_b)


# ── planted union data for the deciding path (core) ────────────────────────────────────────────────────────────────────────

PL_MODELS = ["m0", "m1", "m2"]


def _plant(kind, G=5, seed=3):
    """Planted union data -> (D, arms, Kg, oracle dict). Source MMLU_PRO: G mids, each with a fat leaf (TRAIN 60) and a thin leaf
    (TRAIN 4, where the wrong model looks best); BBH: two fat leaves. EVAL / GATE in the thin leaves follow the planted kind."""
    rs = np.random.RandomState(seed)
    mods = PL_MODELS
    tr_meta, ev_meta, Ktr, Kev, cs, cells, gate = {}, {}, {}, {}, {}, {}, []
    nid = [0]

    def add(side, src, dom, leaf, corr, comp=None):
        nid[0] += 1
        it = "%s:%05d" % ("t" if side == "TRAIN" else ("e" if side == "EVAL" else "g"), nid[0])
        cid = comp or "c:" + it
        if side == "GATE":
            gate.append((it, leaf, dict(zip(mods, corr))))
            return it
        (tr_meta if side == "TRAIN" else ev_meta)[it] = (cid, src, dom)
        (Ktr if side == "TRAIN" else Kev)[it] = dict(zip(mods, corr))
        cs.setdefault(cid, (src, dom, side))
        cells[it] = leaf
        return it

    def draw(best):
        return [int(rs.rand() < (0.90 if mm == best else 0.20)) for mm in mods]
    nfat_e = 150 if kind == "NAIVE" else 20
    winners = set(range(3))
    for g in range(G):
        tb, wr = mods[g % 3], mods[(g + 1) % 3]
        fat, thin = "MMLU_PRO:g%dF" % g, "MMLU_PRO:g%dT" % g
        for _ in range(60):
            add("TRAIN", "MMLU_PRO", "f%d" % g, fat, draw(tb))
        for _ in range(4):
            add("TRAIN", "MMLU_PRO", "t%d" % g, thin, [int(mm == wr) for mm in mods])
        for _ in range(nfat_e):
            add("EVAL", "MMLU_PRO", "f%d" % g, fat, draw(tb))
        for _ in range(10):
            add("GATE", "MMLU_PRO", "f%d" % g, fat, [int(mm == tb) for mm in mods])
        comp = "c:thin%d" % g if kind == "NAIVE" else None
        for _ in range(40 if kind == "NAIVE" else 20):
            if kind in ("HELPS", "TAU0") or (kind == "NAIVE" and g in winners):
                corr = [int(mm == tb) for mm in mods]
            else:
                corr = [int(mm == wr) for mm in mods]
            add("EVAL", "MMLU_PRO", "thinpool" if kind == "NAIVE" else "t%d" % g, thin, corr, comp=comp)
        for _ in range(10):
            add("GATE", "MMLU_PRO", "t%d" % g, thin, [int(mm == (wr if kind == "TAU0" else tb)) for mm in mods])
    for j in range(2):
        leaf = "BBH:b%d" % j
        for _ in range(60):
            add("TRAIN", "BBH", "b%d" % j, leaf, draw("m0"))
        for _ in range(nfat_e):
            add("EVAL", "BBH", "b%d" % j, leaf, draw("m0"))
        for _ in range(10):
            add("GATE", "BBH", "b%d" % j, leaf, [int(mm == "m0") for mm in mods])
    for _ in range(4):                                      # a thin BBH leaf: m1 looks best on TRAIN; EVAL / GATE follow the kind
        add("TRAIN", "BBH", "bT", "BBH:bT", [int(mm == "m1") for mm in mods])
    for _ in range(20):
        add("EVAL", "BBH", "bT", "BBH:bT", [int(mm == ("m1" if kind == "HURTS" else "m0")) for mm in mods])
    for _ in range(10):
        add("GATE", "BBH", "bT", "BBH:bT", [int(mm == ("m1" if kind == "TAU0" else "m0")) for mm in mods])
    for _ in range(3):                                      # three BBH EVAL items filed into an MMLU_PRO leaf (cross-source, R8)
        add("EVAL", "BBH", "b0", "MMLU_PRO:g0F", draw("m0"))
    # hierarchies: AF-U deep; K arms: even seeds flat (leaves under the source node), odd seeds the AF grouping
    names, parents, leaves = [UNION, "MMLU_PRO:r", "BBH:r"], [None, UNION, UNION], set()
    for g in range(G):
        names += ["MMLU_PRO:g%d" % g, "MMLU_PRO:g%dF" % g, "MMLU_PRO:g%dT" % g]
        parents += ["MMLU_PRO:r", "MMLU_PRO:g%d" % g, "MMLU_PRO:g%d" % g]
        leaves |= {"MMLU_PRO:g%dF" % g, "MMLU_PRO:g%dT" % g}
    names += ["BBH:b0", "BBH:b1", "BBH:bT"] + list(PSEUDO)
    parents += ["BBH:r", "BBH:r", "BBH:r", UNION, UNION]
    leaves |= {"BBH:b0", "BBH:b1", "BBH:bT"} | set(PSEUDO)
    H_af = Hier("AF-U", names, parents, leaves)
    kmap = {lf: "K%%d:%s:%03d" % (lf.split(":")[0], j) for j, lf in enumerate(sorted(x for x in leaves if x not in PSEUDO))}
    H_k, xtrees, kpar = {}, {}, {}
    for s in range(5):
        kn = {lf: v % s for lf, v in kmap.items()}
        nm2, pa2 = [UNION, "K%d:MMLU_PRO:w" % s, "K%d:BBH:w" % s], [None, UNION, UNION]
        if s % 2:
            for g in range(G):
                nm2 += ["K%d:MMLU_PRO:m%d" % (s, g), kn["MMLU_PRO:g%dF" % g], kn["MMLU_PRO:g%dT" % g]]
                pa2 += ["K%d:MMLU_PRO:w" % s, "K%d:MMLU_PRO:m%d" % (s, g), "K%d:MMLU_PRO:m%d" % (s, g)]
        else:
            for g in range(G):
                nm2 += [kn["MMLU_PRO:g%dF" % g], kn["MMLU_PRO:g%dT" % g]]
                pa2 += ["K%d:MMLU_PRO:w" % s] * 2
        nm2 += [kn["BBH:b0"], kn["BBH:b1"], kn["BBH:bT"]] + list(PSEUDO)
        pa2 += ["K%d:BBH:w" % s] * 3 + [UNION, UNION]
        H_k[s] = Hier("K%d" % s, nm2, pa2, set(kn.values()) | set(PSEUDO))
        kpar[s] = dict(zip(nm2, pa2))
        xtrees["K%d" % s] = {it: kn[cl] for it, cl in cells.items()}
    D = V.build_ud(mods, tr_meta, ev_meta, Ktr, Kev, cs, "component", None, 7, tree=dict(cells), xtrees=xtrees)
    D.fit_asserts = 0
    gitems = [g_[0] for g_ in gate]
    Kg = np.array([[g_[2][mm] for mm in mods] for g_ in gate], dtype=np.int64)
    m = len(mods)
    arms = {"AF": Arm("AF-U", H_af, [D.tree_keys[g_] for g_ in D.g_tree], [g_[1] for g_ in gate], m)}
    for s, nm in enumerate(KNAMES):
        g_ = D.groupings["x:" + nm][0]
        arms[nm] = Arm(nm, H_k[s], [D.xkeys[nm][j] for j in g_], [kmap[x[1]] % s for x in gate], m)
    par = dict(zip(names, parents))
    return D, arms, Kg, dict(par=par, cells=cells, gate=gate, tr=sorted(tr_meta), ev=sorted(ev_meta), Ktr=Ktr, Kev=Kev, mods=mods,
                             kpar=kpar, kcells={s: xtrees["K%d" % s] for s in range(5)},
                             kgate={s: [(x[0], kmap[x[1]] % s, x[2]) for x in gate] for s in range(5)}, src={**tr_meta, **ev_meta})


def _o_backoff(par, cells, K, items, w, mods, tau):
    """Plain-loop back-off: {leaf: pick} for every leaf named in `par` that is a cell, and the best single."""
    kids = {}
    for v, p in par.items():
        kids.setdefault(p, []).append(v)

    def under(v):
        out, st = set(), [v]
        while st:
            x = st.pop()
            out.add(x)
            st.extend(kids.get(x, []))
        return out
    memo = {}
    tot = {mm: sum(w.get(i, 0) * K[i][mm] for i in items) for mm in mods}
    best = max(mods, key=lambda mm: (tot[mm], -mods.index(mm)))
    root = [v for v, p in par.items() if p is None][0]

    def stat(v):
        sub = under(v)
        n = sum(w.get(i, 0) for i in items if cells[i] in sub)
        s = {mm: sum(w.get(i, 0) * K[i][mm] for i in items if cells[i] in sub) for mm in mods}
        return n, s

    def p(v):
        if v in memo:
            return memo[v]
        n, s = stat(v)
        if par[v] is None:
            r = {mm: s[mm] / n for mm in mods}
        else:
            pp_ = p(par[v])
            r = {mm: (s[mm] + tau * pp_[mm]) / (n + tau) for mm in mods}
        memo[v] = r
        return r

    def pick(leaf):
        if tau == 0:
            n, s = stat(leaf)
            return best if n < 1 else max(mods, key=lambda mm: (s[mm], -mods.index(mm)))
        r = p(leaf)
        return max(mods, key=lambda mm: (r[mm], -mods.index(mm)))
    del root
    return pick, best


def _o_tau(par, cells, K, tr, gate, mods, taus):
    counts = []
    w = {i: 1 for i in tr}
    for t in taus:
        pick, _b = _o_backoff(par, cells, K, tr, w, mods, t)
        counts.append(sum(g_[2][pick(g_[1])] for g_ in gate))
    best = max(counts)
    return taus[counts.index(best)], counts


def st_planted():
    c = dict(B=200, seed=42, taus=TAUS)
    for kind, want in (("HELPS", "HIERARCHY-HELPS"), ("HURTS", "HIERARCHY-HURTS"), ("TAU0", "NEITHER"), ("NAIVE", "NEITHER")):
        D, arms, Kg, o = _plant(kind)
        st = core(D, arms, Kg, c)
        L, w = tb_lines(st, D.models)
        t = "\n".join(L)
        assert w["BO1"] == want, (kind, w, st["db"])
        tau_o, cnt_o = _o_tau(o["par"], o["cells"], o["Ktr"], o["tr"], o["gate"], o["mods"], TAUS)
        assert st["taus"]["AF"] == (tau_o, cnt_o), (kind, st["taus"]["AF"], tau_o, cnt_o)
        w1 = {i: 1 for i in o["tr"]}
        pk0, _b = _o_backoff(o["par"], o["cells"], o["Ktr"], o["tr"], w1, o["mods"], 0)
        pkt, _b = _o_backoff(o["par"], o["cells"], o["Ktr"], o["tr"], w1, o["mods"], tau_o)
        a0 = sum(o["Kev"][i][pk0(o["cells"][i])] for i in o["ev"]) / len(o["ev"])
        at = sum(o["Kev"][i][pkt(o["cells"][i])] for i in o["ev"]) / len(o["ev"])
        assert abs(st["db"]["point"] - (at - a0)) < 1e-12 and abs(st["acc"]["TF"] - a0) < 1e-12, (kind, st["db"]["point"], at - a0)
        need(t, "D_B = acc(TB) - acc(TF) = %s (%+.5f)" % (U.pp(at - a0), at - a0))
        if kind == "HELPS":
            assert tau_o > 0 and st["db"]["lo"] > 0, (tau_o, st["db"])
            need(t, "  BO1 -> HIERARCHY-HELPS", "RULE 8: HIERARCHY-HELPS is not refuted", "FALSIFIER F-BO: NOT FIRED")
            _o_twostage(D, o, tau_o, c, st)
            _o_weak(D, arms, st, o)
            assert st["n_xsrc"] == 3, st["n_xsrc"]
            ch = [i for i in o["ev"] if pk0(o["cells"][i]) != pkt(o["cells"][i])]
            assert len(ch) > 0 and abs(st["share"] - len(ch) / len(o["ev"])) < 1e-12, st["share"]
            cb = sum(o["Kev"][i][pkt(o["cells"][i])] - o["Kev"][i][pk0(o["cells"][i])] for i in o["ev"] if o["src"][i][1] == "BBH") / len(o["ev"])
            assert cb > 0 and abs(st["contrib_bbh"] - cb) < 1e-12 and st["bbh_carries"] is (cb / (at - a0) > 0.5), (st["contrib_bbh"], cb)
        elif kind == "HURTS":
            assert st["db"]["hi"] < 0 and w["F_BO"] is True
            need(t, "FALSIFIER F-BO: FIRES (BO1 HIERARCHY-HURTS)")
        elif kind == "TAU0":
            assert tau_o == 0 and st["db"]["point"] == 0.0 and w["TAU0"] is True
            need(t, "GATE chose no shrinkage", "RULE 8: HIERARCHY-HELPS is REFUTED at the planned n (tau* = 0)")
        else:
            db = st["db"]
            lo_iid = db["point"] - 1.96 * db["se_iid"]
            assert db["point"] > 0 and lo_iid > 0 and db["lo"] <= 0, (db, lo_iid)
            need(t, "  BO1 -> NEITHER (neither HIERARCHY-HELPS", "RULE 8: HIERARCHY-HELPS is REFUTED at the planned n (the lower bound")
        kb, kf = [], []
        for s in range(5):
            tau_k, cnt_k = _o_tau(o["kpar"][s], o["kcells"][s], o["Ktr"], o["tr"], o["kgate"][s], o["mods"], TAUS)
            assert st["taus"]["K%d" % s] == (tau_k, cnt_k), (kind, s, st["taus"]["K%d" % s], tau_k)
            for t_, acc in ((tau_k, kb), (0, kf)):
                pkk, _b = _o_backoff(o["kpar"][s], o["kcells"][s], o["Ktr"], o["tr"], w1, o["mods"], t_)
                acc.append(sum(o["Kev"][i][pkk(o["kcells"][s][i])] for i in o["ev"]) / len(o["ev"]))
        assert max(abs(x - y) for x, y in zip(st["kb_pts"], kb)) < 1e-12 and max(abs(x - y) for x, y in zip(st["kf_pts"], kf)) < 1e-12, kind
        assert abs(st["dtk"]["point"] - (at - float(np.mean(kb)))) < 1e-12 and abs(st["dkb"]["point"] - (float(np.mean(kb)) - float(np.mean(kf)))) < 1e-12
        assert abs(st["spread_kb"] - (max(kb) - min(kb))) < 1e-12 and abs(st["dbmkb"]["point"] - ((at - a0) - (np.mean(kb) - np.mean(kf)))) < 1e-12
        assert kind != "HELPS" or len(set(round(x, 9) for x in kb)) > 1, "the planted K arms do not differ across seeds"


def _o_twostage(D, o, tau, c, st):
    """The two-stage SE of D_B replayed by loops on run_boot's unit draws (default_rng(seed): TRAIN units then EVAL units)."""
    rng = np.random.default_rng(c["seed"])
    reps = []
    for _b in range(c["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = V.draw_units(rng, D.train_units)
        v = V.draw_units(rng, D.eval_units)
        w = {D.items[k]: int(wt[k]) for k in D.T}
        vv = {D.items[k]: float(v[j]) for j, k in enumerate(D.E)}
        p0, _x = _o_backoff(o["par"], o["cells"], o["Ktr"], o["tr"], w, o["mods"], 0)
        pt, _x = _o_backoff(o["par"], o["cells"], o["Ktr"], o["tr"], w, o["mods"], tau)
        tot = sum(vv.values())
        reps.append(sum(vv[i] * (o["Kev"][i][pt(o["cells"][i])] - o["Kev"][i][p0(o["cells"][i])]) for i in o["ev"]) / tot)
    se = float(np.std(reps, ddof=1))
    assert abs(se - st["db"]["se2"]) < 1e-9 and abs(st["db"]["lo"] - (st["db"]["point"] - 1.96 * se)) < 1e-9, (se, st["db"])


def _o_weak(D, arms, st, o):
    """R10 by loops for the best single at c 0.10 on AF-U."""
    mods = o["mods"]
    mdl = mods.index(st["best_name"])
    kids = {}
    for v, p_ in o["par"].items():
        kids.setdefault(p_, []).append(v)

    def under(v):
        out, s_ = set(), [v]
        while s_:
            x = s_.pop()
            out.add(x)
            s_.extend(kids.get(x, []))
        return out
    stats = {}
    for v in o["par"]:
        if o["par"][v] is None or v in PSEUDO:
            continue
        sub = under(v)
        its = [i for i in o["tr"] if o["cells"][i] in sub]
        if its:
            stats[v] = (sum(o["Ktr"][i][mods[mdl]] for i in its) / len(its), len(its), sub)
    order = sorted(stats, key=lambda v: (stats[v][0], -stats[v][1], v))
    chosen, cov = [], 0
    for v in order:
        if cov >= 0.10 * len(o["tr"]):
            break
        if any(v in stats[u][2] or u in stats[v][2] for u in chosen):
            continue
        chosen.append(v)
        cov += stats[v][1]
    reg_items = [i for i in o["ev"] if any(o["cells"][i] in stats[u][2] for u in chosen)]
    acc = sum(o["Kev"][i][mods[mdl]] for i in reg_items) / len(reg_items)
    mean = sum(o["Kev"][i][mods[mdl]] for i in o["ev"]) / len(o["ev"])
    got = st["weak"][(mdl, 0.10)]["af"]
    assert got[0] == len(chosen) and got[2] == len(reg_items) and abs(got[4] - (acc - mean)) < 1e-12, (got, len(chosen), acc - mean)
    assert abs(got[1] - cov / len(o["tr"])) < 1e-12, (got[1], cov / len(o["tr"]))


# ── hierarchy and back-off units ───────────────────────────────────────────────────────────────────────────────────────

def st_hier():
    snap = {"mm": dict(nodes=[dict(id="r", parentIds=[], isLeaf=False), dict(id="a", parentIds=["r"], isLeaf=False),
                              dict(id="l1", parentIds=["a"], isLeaf=True), dict(id="l2", parentIds=["a"], isLeaf=True),
                              dict(id="l3", parentIds=["r"], isLeaf=True)])}
    h = af_hier((("mm", "SRC"), ("one", "ONE")), "x", {"ONE": dict(cell="ONE:r")}, snap_reader=lambda m: snap[m])
    par = {h.names[v]: (h.names[h.parent[v]] if h.parent[v] >= 0 else None) for v in range(h.N)}
    assert par == {UNION: None, "SRC:r": UNION, "SRC:a": "SRC:r", "SRC:l1": "SRC:a", "SRC:l2": "SRC:a", "SRC:l3": "SRC:r",
                   "ONE:r": UNION, V.NO_ROUTING_ROW: UNION, UAR.UNROUTED: UNION}, par
    assert int(h.depth[h.idx["SRC:l1"]]) == 3 and h.M[h.idx["SRC:r"], h.idx["SRC:l2"]] == 1 and h.M[h.idx["SRC:l3"], h.idx["SRC:a"]] == 0
    assert set(h.names[v] for v in np.flatnonzero(h.leaf)) == {"SRC:l1", "SRC:l2", "SRC:l3", "ONE:r"} | set(PSEUDO)
    bad = copy.deepcopy(snap)
    bad["mm"]["nodes"][2]["parentIds"] = ["a", "r"]
    try:
        af_hier((("mm", "SRC"),), "x", {}, snap_reader=lambda m: bad[m])
        raise AssertionError("a DAG node was accepted")
    except SystemExit as e:
        assert "[TB-HIER]" in str(e) and "2 parents" in str(e)
    try:
        Arm("x", h, ["SRC:a"], [], 2)
        raise AssertionError("an internal node was accepted as a cell")
    except SystemExit as e:
        assert "[TB-HIER]" in str(e)
    # k_hier vs scipy fcluster: the 2-cluster cut of the Ward tree = the top merge's two subtrees
    from scipy.cluster.hierarchy import fcluster
    rs = np.random.RandomState(1)
    C = FM.unit_rows(rs.normal(0, 1, (6, 4)) + np.repeat(np.eye(4)[:2] * 3, 3, axis=0))
    hk = k_hier(0, np.vstack([C, C[:1]]), np.array(["A"] * 6 + ["B"]), np.array(list(range(6)) + [0]), ("A", "B"))
    top = [v for v in range(hk.N) if hk.parent[v] == hk.root and hk.names[v].startswith("K0:A:w")]
    assert len(top) == 1 and hk.names[hk.parent[hk.idx["K0:B:000"]]] == UNION
    kids = [v for v in range(hk.N) if hk.parent[v] == top[0]]
    sets = sorted(tuple(sorted(int(hk.names[x].split(":")[2]) for x in range(hk.N) if hk.M[k_, x] and hk.leaf[x] and not hk.pseudo[x])) for k_ in kids)
    fc = fcluster(linkage(C, "ward"), 2, "maxclust")
    want = sorted(tuple(sorted(j for j in range(6) if fc[j] == q)) for q in set(fc))
    assert sets == want, (sets, want)
    assert int((~hk.leaf).sum()) == 1 + 5, "Ward: k - 1 internal merges + the union root"
    # picks: hand values on a three-level tree; leaf z has no TRAIN mass
    names = [UNION, "s", "a", "x", "y", "z"]
    parents = [None, UNION, "s", "a", "a", "s"]
    h3 = Hier("h3", names, parents, {"x", "y", "z"})
    S = np.zeros((6, 2))
    n = np.zeros(6)
    S[3], n[3] = (1, 3), 4          # x: model 1 better
    S[4], n[4] = (9, 2), 10         # y: model 0
    for v in (2, 1, 0):
        S[v] = S[3] + S[4]
        n[v] = n[3] + n[4]
    pk0, gb = picks(h3, S, n, 0)
    assert gb == 0 and list(pk0[[3, 4, 5]]) == [1, 0, 0], pk0          # z: mass 0 -> best single
    pk, _g = picks(h3, S, n, 10)
    # p_root = (10/14, 5/14); s, a equal to root (same items); x: (1 + 10 * 10/14) / 14 vs (3 + 10 * 5/14) / 14 -> model 0
    assert list(pk[[3, 4, 5]]) == [0, 0, 0], pk
    pk2, _g = picks(h3, S, n, 1)
    assert pk2[3] == 1, "tau 1: x keeps its own pick (3 + 5/14 > 1 + 10/14)"
    S2 = S.copy()
    S2[0], S2[1] = (5, 9), (5, 9)   # an artificial upper level preferring model 1: z (mass 0, tau > 0) takes s's pick, not a's
    S2[2] = (10, 5)
    n2 = n.copy()
    pkz, gbz = picks(h3, S2, n2, 5)
    assert gbz == 1 and pkz[5] == 1 and pkz[2] == 0, (pkz, gbz)
    pz0, _g = picks(h3, S2, n2, 0)
    assert pz0[5] == 1, "tau 0: a mass-0 leaf takes the best single (model 1), not model 0"
    D, arms, _Kg, _o = _plant("HELPS")
    w = V.train_full(D)
    w[D.E[0]] = 1
    try:
        node_stats(D, arms["AF"], w)
        raise AssertionError("an EVAL weight was accepted")
    except SystemExit as e:
        assert "[TB-G3]" in str(e)


# ── the fixture layout with a deeper AF-U tree and GATE planted toward shrinkage ─────────────────────────────────────────────

def _deep_fixture(real):
    def wrapped(tmp, *a, **kw):
        fx = real(tmp, *a, **kw)
        p = os.path.join(tmp, *fx.afu.split("/"), "mmlu", "seed_42", "dag_snapshots.jsonl")
        snaps = [json.loads(x) for x in open(p, encoding="utf-8").read().splitlines() if x.strip()]
        nodes = snaps[-1]["nodes"]
        for n in nodes:
            if n["id"] in ("L0", "L1"):
                n["parentIds"], n["depth"] = ["mA"], 2
            elif n["id"] in ("L2", "L9"):
                n["parentIds"], n["depth"] = ["mB"], 2
        nodes += [dict(id="mA", parentIds=["root"], isLeaf=False, label="mA", depth=1, vmfMu=[0.0] * UAR.FX_DIM),
                  dict(id="mB", parentIds=["root"], isLeaf=False, label="mB", depth=1, vmfMu=[0.0] * UAR.FX_DIM)]
        with open(p, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(x) + "\n" for x in snaps))
        return fx
    return wrapped


def _o_gate_key(spec, gitems):
    vals = {}
    for r in spec["responses"]:
        if r["cv"] == "mc6" and r["side"] == "GATE":
            vals.setdefault((r["item"], r["model"]), []).append(r["mf"] if r["mf"] is not None else r["c"])
    mu = sorted(spec["models_u"])
    out = {}
    for i in gitems:
        if all(len(vals.get((i, m), [])) == 1 for m in mu):
            out[i] = {m: vals[(i, m)][0] for m in mu}
    return out


def _o_gate_cells(tmp):
    rows = list(csv.DictReader(open(os.path.join(tmp, "res", "inputs", "validation_merged", U.UAR.RP.QUERIES), encoding="utf-8")))
    side = U.UAR._SIDES[0]()[0]
    cnt = {}
    for r in rows:
        if side.get(r["item_id"], (None, None))[1] == "GATE":
            cnt.setdefault(r["item_id"], Counter())[r["leaf_id"] or UAR.UNROUTED] += 1
    return {i: min(k for k, v in c_.items() if v == max(c_.values())) for i, c_ in cnt.items()}


def _o_af(lay):
    """By loops from the fixture's files: AF-U parents (snapshots; one-cell and pseudo cells under the union root), AF cells, the
    keyed TRAIN / EVAL values and the scored TRAIN items (key-complete, with a cell)."""
    fx = lay.fx
    mu, val = U.o_key(fx.spec)
    K = val_k(val, mu)
    man = json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    par = {UNION: None, V.NO_ROUTING_ROW: UNION, UAR.UNROUTED: UNION}
    for m, so in fx.reg["members"]:
        p = os.path.join(lay.tmp, "res", "AF-U", m, "seed_42", "dag_snapshots.jsonl")
        if not os.path.exists(p):
            continue
        last = [json.loads(x) for x in open(p, encoding="utf-8").read().splitlines() if x.strip()][-1]
        for n in last["nodes"]:
            par["%s:%s" % (so, n["id"])] = ("%s:%s" % (so, n["parentIds"][0])) if n["parentIds"] else UNION
    for i, cl in af.items():
        par.setdefault(cl, UNION)                     # the one-cell member's cell
    tr = sorted(i for i in K if fx.side.get(i, (None, None))[1] == "TRAIN" and i in af)
    return mu, K, man, af, par, tr


def build_base(tmp):
    """union_route_common.build_layout with the deepened MMLU_PRO tree; GATE planted toward shrinkage: a GATE item is correct for
    exactly the model the AF-U back-off picks for its cell at tau 200 (computed by the loop oracle on the fixture's TRAIN)."""
    real = UAR._fixture
    UAR._fixture = _deep_fixture(real)
    try:
        lay = U.build_layout(tmp)
    finally:
        UAR._fixture = real
    pol = json.load(open(os.path.join(lay.tmp, "res", "scratch", "pol.json"), encoding="utf-8"))
    with UAR._patched(lay.fx):
        gc = _o_gate_cells(lay.tmp)
    mu, K, _man, af, par, tr = _o_af(lay)
    pick200, _b = _o_backoff(par, af, K, tr, {i: 1 for i in tr}, mu, 200)
    # the MATH GATE items' vectors moved onto the BBH direction: filed by declared source they stay in MATH's cell (UNION-AF-ROUTE
    # R3); a filing among all sources would move them to BBH's (kills X61)
    bbh = np.mean([lay.fx.vec[i] for i, (_c, s_) in lay.fx.side.items() if s_ == "TRAIN" and lay.fx.strata[i][0] == "BBH"], axis=0)
    for i in gc:
        if lay.fx.strata[i][0] == "MATH":
            lay.fx.vec[i] = bbh / np.linalg.norm(bbh)
    lay.fx.spec = copy.deepcopy(lay.fx.spec)
    for r in lay.fx.spec["responses"]:
        if r["side"] == "GATE" and r["item"] in gc:
            r["c"], r["mf"] = int(r["model"] == pick200(gc[r["item"]])), None
    lay.gate_cells = gc
    lay.common["n_gate_key"] = len(_o_gate_key(lay.fx.spec, sorted(gc)))
    lay.best = pol["best_single"]
    return lay


def clone(lay, dest):
    new = U.clone(lay, dest)
    new.fx.spec = lay.fx.spec
    new.gate_cells, new.best = lay.gate_cells, lay.best
    return new


def _oracle(lay, res):
    """Independent recomputation from the fixture's raw rows, snapshots and bundle: tau*, TF, TB, D_B (+ two-stage SE), KB_0, share."""
    fx, D = lay.fx, res["D"]
    mu, K, man, af, par, tr_o = _o_af(lay)
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]
    assert tr == tr_o, "the scored TRAIN set differs from the loop reader's"
    assert par["MMLU_PRO:L0"] == "MMLU_PRO:mA" and par["MMLU_PRO:mA"] == "MMLU_PRO:root", "the deepened tree is not in place"
    gk = _o_gate_key(fx.spec, sorted(lay.gate_cells))
    gate = [(i, lay.gate_cells[i], gk[i]) for i in sorted(gk)]
    tau, counts = _o_tau(par, af, K, tr, gate, mu, TAUS)
    w1 = {i: 1 for i in tr}
    p0, _b = _o_backoff(par, af, K, tr, w1, mu, 0)
    pt, _b = _o_backoff(par, af, K, tr, w1, mu, tau)
    a0 = sum(K[i][p0(af[i])] for i in ev) / len(ev)
    at = sum(K[i][pt(af[i])] for i in ev) / len(ev)
    share = sum(1 for i in ev if p0(af[i]) != pt(af[i])) / len(ev)
    rng = np.random.default_rng(lay.common["seed"])
    reps = []
    for _b in range(lay.common["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = V.draw_units(rng, D.train_units)
        v = V.draw_units(rng, D.eval_units)
        w = {D.items[k]: int(wt[k]) for k in D.T}
        vv = {D.items[k]: float(v[j]) for j, k in enumerate(D.E)}
        q0, _x = _o_backoff(par, af, K, tr, w, mu, 0)
        qt, _x = _o_backoff(par, af, K, tr, w, mu, tau)
        reps.append(sum(vv[i] * (K[i][qt(af[i])] - K[i][q0(af[i])]) for i in ev) / sum(vv.values()))
    # K_0 with Ward on the recomputed filing centroids (scipy linkage; parents by loops)
    b, _m = GC.load_bundle(os.path.join(lay.tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    Xt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    classes = [str(x) for x in b["classes"]]
    tsrc = np.array([UAR.src_of(classes[i]) for i in np.asarray(b["train_y"], dtype=int)])
    C, csrc, cloc, _l, _f = UAR.us_fit(Xt, tsrc, man["ksrc"], fx.reg["sources"], 0)
    kpar = {UNION: None, V.NO_ROUTING_ROW: UNION, UAR.UNROUTED: UNION}
    for so in fx.reg["sources"]:
        rows = [j for j in range(len(C)) if csrc[j] == so]
        lv = ["K0:%s:%03d" % (so, cloc[j]) for j in rows]
        if len(rows) == 1:
            kpar[lv[0]] = UNION
            continue
        Z = linkage(FM.unit_rows(C[rows]), "ward")
        nm = lambda q: lv[q] if q < len(rows) else "W%s%d" % (so, q)
        for j in range(len(rows) - 1):
            kpar[nm(int(Z[j, 0]))] = nm(len(rows) + j)
            kpar[nm(int(Z[j, 1]))] = nm(len(rows) + j)
        kpar[nm(2 * len(rows) - 2)] = UNION
    k0, _ = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "k_cells_s0.tsv"), man["inputs"]["res/inputs/k_cells_s0.tsv"])
    vec = {i: fx.vec[i] for i in lay.gate_cells}
    srcs = UAR.item_sources(ERC.item_rows("res/inputs/validation_merged")[0])
    gk0 = {}
    for i in lay.gate_cells:
        cand = [j for j in range(len(C)) if csrc[j] in srcs[i]]
        jb = max(cand, key=lambda j: (float(np.dot(vec[i], C[j])), -j))
        gk0[i] = "K0:%s:%03d" % (csrc[jb], cloc[jb])
    gate_k = [(i, gk0[i], gk[i]) for i in sorted(gk)]
    tau_k, ck = _o_tau(kpar, k0, K, tr, gate_k, mu, TAUS)
    pkk, _b = _o_backoff(kpar, k0, K, tr, w1, mu, tau_k)
    kb0 = sum(K[i][pkk(k0[i])] for i in ev) / len(ev)
    return dict(tau=tau, counts=counts, a0=a0, at=at, db=at - a0, se=float(np.std(reps, ddof=1)), share=share, tau_k=tau_k, kb0=kb0, ck=ck,
                n_gate=len(gate))


def val_k(val, mu):
    out = {}
    for (i, m), x in val.items():
        out.setdefault(i, {})[m] = x
    return {i: d for i, d in out.items() if all(m in d for m in mu)}


def st_run_e2e(base, mk):
    lay = clone(base, mk())
    text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "tb", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (TREE-BACKOFF; --run" % U.POOL)
    assert os.path.isfile(os.path.join(lay.tmp, "res", "tb", "READ_STARTED"))
    with UAR._patched(lay.fx):
        o = _oracle(lay, res)
    assert o["tau"] > 0, "the fixture does not exercise shrinkage (tau* = 0)"
    assert abs(o["db"]) > 1e-4 and o["share"] > 0, "the fixture does not discriminate TB from TF"
    tau, = U.num(out, r"TAU \(GATE, R4\) AF  tau\* = (\d+) ")
    assert int(tau) == o["tau"], (tau, o["tau"])
    need(out, "TAU (GATE, R4) AF  tau* = %d | GATE correct counts over the grid 0/1/2/5/10/20/50/100/200/500/1000: %s" % (
        o["tau"], " ".join(str(x) for x in o["counts"])))
    taukk, = U.num(out, r"TAU \(GATE, R4\) K0  tau\* = (\d+) ")
    assert int(taukk) == o["tau_k"], (taukk, o["tau_k"])
    need(out, "TAU (GATE, R4) K0  tau* = %d | GATE correct counts over the grid 0/1/2/5/10/20/50/100/200/500/1000: %s" % (
        o["tau_k"], " ".join(str(x) for x in o["ck"])))
    tf, tb = U.num(out, r"ARMS \(EVAL accuracy, point\): BEST [0-9.]+ \| SRC [0-9.]+ \| TF ([0-9.]+) \| TB ([0-9.]+) ")
    assert abs(tf - o["a0"]) < 6e-6 and abs(tb - o["at"]) < 6e-6, (tf, tb, o)
    kb0, = U.num(out, r"\| KB_s ([0-9.]+) / ")
    assert abs(kb0 - o["kb0"]) < 6e-6, (kb0, o["kb0"])
    p_, lo, hi = U.num(out, r"D_B = acc\(TB\) - acc\(TF\) = \S+ \(([+-][0-9.]+)\) \| two-stage 95% \[\S+, \S+\] \(([+-][0-9.]+), ([+-][0-9.]+)\)")
    se2, = U.num(out, r"support D_B: n \d+, SE_2stage ([0-9.]+) ")
    assert abs(p_ - o["db"]) < 6e-6 and abs(se2 - o["se"]) < 6e-6, (p_, se2, o)
    assert abs(lo - (o["db"] - 1.96 * o["se"])) < 2e-5 and abs(hi - (o["db"] + 1.96 * o["se"])) < 2e-5
    sh, = U.num(out, r"DESCRIPTIVE: EVAL picks changed under TB ([0-9.]+) ")
    assert abs(sh - o["share"]) < 6e-6
    need(out, "GATE %d key-complete items" % o["n_gate"])
    want = "HIERARCHY-HELPS" if (p_ > 0 and lo > 0) else ("HIERARCHY-HURTS" if (p_ < 0 and hi < 0) else "NEITHER")
    need(out, "  BO1 -> %s (" % want, "FALSIFIER F-BO: %s" % ("FIRES" if want == "HIERARCHY-HURTS" else "NOT FIRED"),
         "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]), "MIRROR (R3)", "B3: the point policy re-fitted",
         "GATE key (EC-R7)")
    assert res["words"]["BO1"] == want
    assert out.index("IDENTITY:") < out.index("TAU (GATE, R4)"), "a new number printed before the identity"
    t2, err2, _r = U.cap(_me(), run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "tb", "outcome.txt")), "an outcome was written by a refusal"


def st_refusals(base, mk):
    lay = clone(base, mk())
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
    assert err and "B0-2 pool check failed" in err, err
    assert buf.getvalue().splitlines()[0].startswith("POOL "), "the POOL line is not first"
    _no_outcome(lay)
    for over, needle in ((dict(uar_policy_sha="0" * 64), "frozen TRAIN policy"), (dict(manifest_sha="0" * 64), "inputs manifest is sha256")):
        lay = clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, **over)
        assert err and needle in err, (over, err)
        assert not os.path.exists(os.path.join(lay.tmp, "res", "tb", "READ_STARTED"))
        _no_outcome(lay)
    lay = clone(base, mk())
    _t, err, _r = U.cap(_me(), run, lay, n_route=lay.common["n_route"] + 1)
    assert err and "[TB-DENOM]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    _t, err, _r = U.cap(_me(), run, lay, n_gate_key=lay.common["n_gate_key"] + 1)
    assert err and "[TB-GATE-DENOM]" in err, err
    _no_outcome(lay)
    idn = lay.common["identity"]
    bump = lambda s: s[:-1] + str((int(s[-1]) + 1) % 10)
    for k in ("af", "k0"):
        lay = clone(base, mk())
        _t, err, _r = U.cap(_me(), run, lay, identity=dict(idn, **{k: bump(idn[k])}))
        assert err and "[TB-IDENTITY]" in err, (k, err)
        assert "TAU (GATE" not in _t and "BO1 (THE ONE" not in _t, "a new number was printed before the identity refusal"
        _no_outcome(lay)
    lay = clone(base, mk())
    pol_p = os.path.join(lay.tmp, "res", "scratch", "pol.json")
    pol = json.load(open(pol_p, encoding="utf-8"))
    key = sorted(k for k in pol["tree_cell"] if pol["tree_cell"][k] is not None)[0]
    pol["tree_cell"][key] = sorted(set(pol["roster"]) - {pol["tree_cell"][key]})[0]
    with open(pol_p, "w", encoding="utf-8") as f:
        json.dump(pol, f)
    _t, err, _r = U.cap(_me(), run, lay, uar_policy_sha=U.sha256_bytes(pol_p))
    assert err and "[B3]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    real_fit = UAR.us_fit

    def fit_bad(Xt, tsrc, ksrc, sources, seed):
        return real_fit(Xt, tsrc, ksrc, sources, seed + 7)
    UAR.us_fit = fit_bad
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        UAR.us_fit = real_fit
    assert err and "[TB-KDIFF]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    g = globals()
    real_picks = g["picks"]

    def picks_bad(h, S, n, tau):
        pk, gb = real_picks(h, S, n, tau)
        if tau == 0:
            pk = pk.copy()
            v0 = [v for v in range(h.N) if h.leaf[v] and n[v] >= 1][0]
            pk[v0] = (pk[v0] + 1) % S.shape[1]
        return pk, gb
    g["picks"] = picks_bad
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        g["picks"] = real_picks
    assert err and "[TB-MIRROR]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    real_gi, real_gk = ERC.gate_items, EC.gate_key
    intruder = sorted(i for i, (_c, s_) in lay.fx.side.items() if s_ == "TRAIN" and i in lay.fx.filed and lay.fx.filed[i])[0]

    def gi_bad(rows_h, side):
        its, gcell, gsrc = real_gi(rows_h, side)
        return sorted(its + [intruder]), dict(gcell, **{intruder: lay.fx.filed[intruder]}), gsrc

    def gk_bad(cfg, say, models, gits):
        K, comp, want = real_gk(cfg, say, models, [g_ for g_ in gits if g_ != intruder])
        return dict(K, **{intruder: {m: 0 for m in models}}), sorted(comp + [intruder]), want
    ERC.gate_items, EC.gate_key = gi_bad, gk_bad
    try:
        _t, err, _r = U.cap(_me(), run, lay, n_gate_key=lay.common["n_gate_key"] + 1)
    finally:
        ERC.gate_items, EC.gate_key = real_gi, real_gk
    assert err and "[TB-GATE-SIDE]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    real_after = V.after_sha
    V.after_sha = lambda path, before, label, say: (real_after(path, before, label, say) and label != "eval_view")
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        V.after_sha = real_after
    assert err and "[PIN]" in err, err
    _no_outcome(lay)
    assert os.path.isfile(os.path.join(lay.tmp, "res", "tb", "outcome_VOID.txt")), "a void read did not write *_VOID.txt"
    lay = clone(base, mk())
    _t, err, _r = U.cap(_me(), run, lay, B=lay.common["B"] + 1)
    assert err and "B / seed" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    os.makedirs(os.path.join(lay.tmp, "res", "tb"), exist_ok=True)
    open(os.path.join(lay.tmp, "res", "tb", "READ_STARTED"), "w").close()
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_dry_run(base, mk):
    lay = clone(base, mk())
    text, err, _r = U.cap(_me(), dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (TREE-BACKOFF; --dry-run" % U.POOL), ls[0]
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key read", "POOL CHECK (B0-2): rc 0", "AF-U HIERARCHY (R1):",
         "K-WARD K4 (R2):", "every scored item re-filed = k_cells_s0.tsv", "COST: 0 calls")
    m = re.search(r"AF-U HIERARCHY \(R1\): (\d+) nodes, (\d+) filing leaves \(\+2 pseudo\), (\d+) internal", text)
    assert m and (int(m.group(2)), int(m.group(3))) == (6, 5), m and m.groups()   # leaves MMLU_PRO L0-L2, L9, MATH L0, BBH one cell;
    #                                                                                  internal: union, MMLU_PRO root, mA, mB, MATH root
    for bad in ("BO1 (THE ONE", "D_B =", "IDENTITY:", "TAU (GATE", "PREDICTION", "GATE key (EC-R7)"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "tb")), "the dry-run wrote under res/tb"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (TREE-BACKOFF; --dry-run"), L[0]
    need(t, "5907 EVAL items in 5404 CK-CLOSE components", "DEFF 1.302", "n_eff 4,537", "SE(D_B) 0.255pp", "MDE80 0.71pp", VERDICT_LINE,
         "B = 2000 two-stage replicates (default_rng(42))", "tau grid 0/1/2/5/10/20/50/100/200/500/1000", "on the 1944 key-complete GATE items",
         "best single 0.6049, TRUE source 0.6150, AF-U leaf cell 0.6201, K_s K0 0.6271; C1 +2.67pp [+1.46pp, +3.89pp]; G_AF +1.52pp [+0.14pp, +2.91pp]",
         "e50a8e0fa267db96", "L24814-L24826", "calls 0", "66 GATE fits", "12006 back-off fits")
    assert REG["out"] == "experiment_results/archv2/tree_backoff/outcome.txt" and REG["uar_policy_sha"].startswith("8d68018c")
    assert REG["manifest_sha"].startswith("53021e26") and REG["B"] == 2000 and REG["n_gate_key"] == 1944 and REG["taus"] == TAUS


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "BO1 three words, lo / hi exactly 0, tau* = 0, rule 8, F-BO, P1-P6 bands inclusive, every Brier", "plain"),
         ("planted", "core() on planted data: HELPS / HURTS / TAU0 / NAIVE by value vs loops; two-stage SE replay; weak regions", "plain"),
         ("hier", "af_hier, DAG refusal, non-leaf cell, k_hier vs fcluster, picks() hand values, [TB-G3]", "plain"),
         ("run_e2e", "--run end to end on the deepened fixture: tau*, TF, TB, D_B (point, SE, interval), KB_0, share vs an oracle", "base"),
         ("refusals", "pool, manifest, policy sha, DENOM, GATE-DENOM, IDENTITY, B3, KDIFF, MIRROR, B / seed, marker; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, structure, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "planted": st_planted, "hier": st_hier, "run_e2e": st_run_e2e, "refusals": st_refusals,
       "dry_run": st_dry_run, "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    import tempfile
    import scratch_dir   # noqa: F401  TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def mk():
        d = tempfile.mkdtemp(prefix="tb_")
        made.append(d)
        return os.path.join(d, "lay")
    HIT.clear()
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                if kind == "base" and base is None:
                    with contextlib.redirect_stdout(io.StringIO()):
                        base = build_base(mk())
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(base, mk)
                if not quiet:
                    print("  ok   %-13s %s" % (name, desc), flush=True)
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    import traceback
                    print("  FAIL %-13s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:600]), flush=True)
                    traceback.print_exc()
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(only=None):
    """union_route_common.run_mutants' procedure with this script's deepened base: each mutant edits the code ABOVE the SELFTEST
    marker in memory, executes the edited module and runs its selftest; KILLED iff the selftest fails. X00 must survive."""
    import tempfile
    import scratch_dir   # noqa: F401
    import shutil
    NL = chr(10)
    mark = NL + "# " + chr(0x2550) * 2 + " SELFTEST"
    path = os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    cut = src.index(mark)
    d = tempfile.mkdtemp(prefix="tb_mut_")
    rows, bad = [], []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            base = build_base(os.path.join(d, "lay"))
        for name, old, new in MUTANTS:
            if only and not any(name.startswith(o) for o in only):
                continue
            head = src[:cut]
            if old and head.count(old) != 1:
                bad.append(name)
                rows.append((name, "NOT APPLIED (%d matches)" % head.count(old)))
                print("  %-74s NOT APPLIED (%d matches)" % (name, head.count(old)), flush=True)
                continue
            try:
                mod = types.ModuleType("tree_backoff_mutant")
                mod.__file__ = path
                exec(compile((head.replace(old, new) if old else head) + src[cut:], path, "exec"), mod.__dict__)
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.selftest(quiet=True, base=base)
                res = "SURVIVED"
            except BaseException as e:   # noqa: B902
                res = "KILLED (%s)" % type(e).__name__
            rows.append((name, res))
            print("  %-74s %s" % (name, res), flush=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied %s" % (
        TAG, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "", ""),
    ("X01 BO1 HELPS at lo >= 0 (boundary)", 'helps = db["point"] > 0 and db["lo"] > 0', 'helps = db["point"] > 0 and db["lo"] >= 0'),
    ("X02 BO1 HELPS without the point clause", 'helps = db["point"] > 0 and db["lo"] > 0', 'helps = db["lo"] > 0'),
    ("X03 BO1 HURTS at hi <= 0 (boundary)", 'hurts = db["point"] < 0 and db["hi"] < 0', 'hurts = db["point"] < 0 and db["hi"] <= 0'),
    ("X04 BO1 HURTS without the interval clause", 'hurts = db["point"] < 0 and db["hi"] < 0', 'hurts = db["point"] < 0'),
    ("X05 tau* = 0 branch removed", '    if tau_af == 0:' + NL + '        return "NEITHER", True', '    if False:' + NL + '        return "NEITHER", True'),
    ("X06 BO1 decided on the i.i.d. interval (naive)", '    db = lin(w_db)' + NL, '    db = lin(w_db)' + NL + '    db = dict(db, lo=db["point"] - 1.96 * db["se_iid"], hi=db["point"] + 1.96 * db["se_iid"])' + NL),
    ("X07 D_B sign reversed", 'w_db = e(TB, TF, wts=(1.0, -1.0))', 'w_db = e(TB, TF, wts=(-1.0, 1.0))'),
    ("X08 D_B against BEST instead of TF (wrong arm)", 'w_db = e(TB, TF, wts=(1.0, -1.0))', 'w_db = e(TB, BEST, wts=(1.0, -1.0))'),
    ("X09 tau ties to the larger", '    j = int(np.argmax(counts))', '    j = len(counts) - 1 - int(np.argmax(counts[::-1]))'),
    ("X10 tau = GATE argmin (min<->max)", '    j = int(np.argmax(counts))', '    j = int(np.argmin(counts))'),
    ("X11 GATE fit with EVAL weight (uncapped fit)", '    S, n = node_stats(D, arm, V.train_full(D))' + NL + '    r = np.arange(len(arm.gate))', '    S, n = node_stats(D, arm, np.ones(D.n, dtype=np.int64))' + NL + '    r = np.arange(len(arm.gate))'),
    ("X12 node-fit G3 guard removed", '    if D.is_eval[w != 0].any():', '    if False:'),
    ("X13 tau 0: mass < 1 not backed off to the best single", '        pk[n < 1] = gb' + NL, '        pass' + NL),
    ("X14 shrink toward the root, not the parent (one level)", 'p[lev] = (S[lev] + tau * p[h.parent[lev]])', 'p[lev] = (S[lev] + tau * p[h.root])'),
    ("X15 only the first level processed (first site only)", '    for lev in h.levels:' + NL + '        p[lev]', '    for lev in h.levels[:1]:' + NL + '        p[lev]'),
    ("X16 p_root not the TRAIN accuracy", '    p[h.root] = S[h.root] / n[h.root]', '    p[h.root] = S[h.root] * 0.0 + 0.5'),
    ("X17 leaf pick argmin (min<->max)", '    return p.argmax(axis=1).astype(np.int64), gb', '    return p.argmin(axis=1).astype(np.int64), gb'),
    ("X18 denominator n + 1 instead of n + tau", '/ (n[lev] + tau)[:, None]', '/ (n[lev] + 1.0)[:, None]'),
    ("X19 node statistics without aggregation (leaves only)", '    return arm.h.M @ Sd, arm.h.M @ nd', '    return Sd, nd'),
    ("X20 AF-U flattened (every node under the union root)", '            parents.append("%s:%s" % (so, pids[0]) if pids else UNION)', '            parents.append(UNION)'),
    ("X21 AF-U DAG refusal removed", '            if len(pids) > 1:' + NL + '                hit("REFUSE.HIER")', '            if False:' + NL + '                hit("REFUSE.HIER")'),
    ("X22 K-WARD average link", 'Z = linkage(FM.unit_rows(np.asarray(C, dtype=np.float64)[rows]), method="ward")', 'Z = linkage(FM.unit_rows(np.asarray(C, dtype=np.float64)[rows]), method="average")'),
    ("X23 K-WARD flattened (Ward tree ignored)", '            parents.append(nm(par[i]) if i in par else UNION)', '            parents.append(UNION)'),
    ("X24 TB column carries the tau 0 picks", '        rows[ct] = D.A[D.E, et]', '        rows[ct] = D.A[D.E, e0]'),
    ("X25 BEST column from the wrong model", '    rows[BEST] = D.A[D.E, gbs.pop()]', '    rows[BEST] = D.A[D.E, (gbs.pop() + 1) % len(D.models)]'),
    ("X26 mirror check removed", '            if a.shape != b.shape or not np.allclose(a, b, rtol=0.0, atol=1e-12, equal_nan=True):', '            if False:'),
    ("X27 D_TK against mean KF (wrong population)", 'dtk=lin(e(TB) - w_kb)', 'dtk=lin(e(TB) - w_kf)'),
    ("X28 seed spread = SD", 'st["spread_kb"] = max(st["kb_pts"]) - min(st["kb_pts"])', 'st["spread_kb"] = float(np.std(st["kb_pts"]))'),
    ("X29 D_KB sign reversed", 'dkb=lin(w_kb - w_kf)', 'dkb=lin(w_kf - w_kb)'),
    ("X30 share = unchanged picks", '    ch = e0 != et' + NL, '    ch = e0 == et' + NL),
    ("X31 BBH contribution from the other sources (wrong population)", 'float(d_item[srcE == "BBH"].sum()) / NE', 'float(d_item[srcE != "BBH"].sum()) / NE'),
    ("X32 P5 threshold 0.25", '    return bool(d_b != 0.0 and contrib / d_b > 0.5)', '    return bool(d_b != 0.0 and contrib / d_b > 0.25)'),
    ("X33 P5 by |contribution| (sign ignored)", '    return bool(d_b != 0.0 and contrib / d_b > 0.5)', '    return bool(d_b != 0.0 and abs(contrib / d_b) > 0.5)'),
    ("X34 NO_XSRC keeps the cross-source items", '== D.src[k] for k in D.E], dtype=bool)', '!= D.src[k] for k in D.E], dtype=bool)'),
    ("X35 weak region by highest TRAIN accuracy (min<->max)", 'order = sorted(cand, key=lambda v: (acc[v], -n[v], h.names[v]))', 'order = sorted(cand, key=lambda v: (-acc[v], -n[v], h.names[v]))'),
    ("X36 weak region allows nested nodes", '        if any(h.M[v, u] or h.M[u, v] for u in chosen):' + NL + '            continue', '        if False:' + NL + '            continue'),
    ("X37 weak-region gap without the model mean", '    return int(inreg.sum()), a, a - float(col.mean())', '    return int(inreg.sum()), a, a'),
    ("X38 P6 read at c 0.05", '    w = st["weak"][(bi, 0.10)]', '    w = st["weak"][(bi, 0.05)]'),
    ("X39 P6 read for the wrong model", '    bi = models.index(st["best_name"])', '    bi = (models.index(st["best_name"]) + 1) % len(models)'),
    ("X40 P3 Brier on a fixed outcome", 'U.brier(PROB_BO1, v)', 'U.brier(PROB_BO1, "NEITHER")'),
    ("X41 P1 Brier indicator inverted", '(P_TAU0 - float(z)) ** 2', '(P_TAU0 - float(not z)) ** 2'),
    ("X42 rule 8 strict (lo exactly 0 not a refutation)", '    if ts["AF"] == 0 or db["lo"] <= 0:' + NL + '        hit("RULE8.REFUTED")', '    if ts["AF"] == 0 or db["lo"] < 0:' + NL + '        hit("RULE8.REFUTED")'),
    ("X43 rule 8 ignores the lower bound (tau* only)", '    if ts["AF"] == 0 or db["lo"] <= 0:' + NL + '        hit("RULE8.REFUTED")', '    if ts["AF"] == 0:' + NL + '        hit("RULE8.REFUTED")'),
    ("X44 F-BO fires on NEITHER", '    if v == "HIERARCHY-HURTS":' + NL + '        hit("FBO.FIRED")', '    if v != "HIERARCHY-HELPS":' + NL + '        hit("FBO.FIRED")'),
    ("X45 F-BO NOT FIRED line dropped (skip path)", '        L.append("FALSIFIER F-BO: NOT FIRED (BO1 %s; F-BO fires iff HIERARCHY-HURTS)" % v)', '        pass'),
    ("X46 rule-8 not-refuted line dropped (skip path)", '        L.append("RULE 8: HIERARCHY-HELPS is not refuted (lower bound %+.5f > 0, tau* %s > 0)" % (db["lo"], ts["AF"]))', '        pass'),
    ("X47 tau* = 0 words dropped (skip path)", '        L.append("  BO1 -> NEITHER (GATE chose no shrinkage: tau*(AF-U) = 0, D_B = 0 identically)")', '        L.append("  BO1 -> NEITHER")'),
    ("X48 verdict line of record dropped", 'verdict line of record: %s" % (', '%s" % ('),
    ("X49 identity refusal removed", '        if not ok:' + NL + '            hit("REFUSE.IDENTITY")', '        if False:' + NL + '            hit("REFUSE.IDENTITY")'),
    ("X50 pre-read write-once check removed", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X51 GATE denominator check removed", '    if len(gitems) != int(c["n_gate_key"]):', '    if False:'),
    ("X52 GATE-side check removed", '    if set(gitems) & set(D.items):', '    if False:'),
    ("X53 K re-filing check removed", '        if diff:' + NL + '            hit("REFUSE.KDIFF")', '        if False:' + NL + '            hit("REFUSE.KDIFF")'),
    ("X54 B / seed check removed", 'if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):', 'if False:'),
    ("X55 every K arm at tau*(AF-U)", '        pt, _g = picks(a.h, S, n, taus_star[nm])', '        pt, _g = picks(a.h, S, n, taus_star["AF"])'),
    ("X56 hook ignores the TRAIN resample", '        CE, _pk = arm_matrix(D_, arms, tstar, wt)', '        CE, _pk = arm_matrix(D_, arms, tstar, V.train_full(D_))'),
    ("X57 hook ignores the EVAL resample", '        two_rows.append(score(CE, v, masks))', '        two_rows.append(score(CE, np.ones_like(v), masks))'),
    ("X58 i.i.d. draws on another seed", 'U.iid_weights(c["seed"], NE, c["B"])', 'U.iid_weights(c["seed"] + 1, NE, c["B"])'),
    ("X59 dry-run reads the keys", '    U.read_views(cfg, say, True, P_["af"], P_["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)', '    U.read_views(cfg, say, False, P_["af"], P_["kx"], reg()["marker"], "x", refuse, hit, tag=TEST_ID)'),
    ("X60 GATE counts on the wrong items' cells", '        counts.append(int(Kg[r, pk[arm.gate]].sum()))', '        counts.append(int(Kg[r, pk[arm.gate[::-1]]].sum()))'),
    ("X61 GATE K cells filed among all sources (no source filter)", '        gk[s] = {it: name(UAR.file_by_source(vec[it], srcs[it], C, csrc)) for it in gits}', '        gk[s] = {it: name(UAR.file_by_source(vec[it], sorted(set(csrc)), C, csrc)) for it in gits}'),
    ("X62 one-cell member's cell dropped from AF-U", '            names.append(cell)' + NL + '            parents.append(UNION)' + NL + '            leaves.add(cell)', '            pass'),
    ("X63 TF picks at tau 1 instead of tau 0", '        p0, gb = picks(a.h, S, n, 0)', '        p0, gb = picks(a.h, S, n, 1)'),
    ("X64 outcome written despite a void view sha", '    U.write_outcome(c["out"], "\\n".join(lines) + "\\n", ok_sha, refuse, out)', '    U.write_outcome(c["out"], "\\n".join(lines) + "\\n", True, refuse, out)'),
)


if __name__ == "__main__":
    sys.exit(main())
