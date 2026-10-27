"""escalation_rc.py: ESCALATION-RC -- does escalating low-margin or OOS queries from the AF-U cell policy to the best single
model beat escalating the same share at random on the union routing data (RC1), with a K_0 (per-source k-means) comparator and
risk-coverage curves? ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU reader.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — ESCALATION-RC: on the union routing data, does
  escalating low-margin, OOS or decision-fragile queries from the AF-U cell policy to the best single model improve routed
  accuracy over escalating the same share at random, with a k-means comparator? (zero calls; CPU readout)" (L23960-L23973,
  _as_of 964511fd, parent b9b67b11): RC1, Support (a)-(g), P1, P2, F-RC, WILL-NOT-SHOW. Record L23939-L23942 (conditional reading)
  and its bracket: CONDITION RESOLVED by OOS-TREE-CELLS OT1 EQUIVALENT (L23975-L23987, _as_of the commit that writes it, parent
  964511fd): the OOS-based legs are read as written. Source note docs/literature/2026-10-03_tree_uses.md (7812c100), use R2.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form; never beside a construction: every step reads the pool):
  0. python tools/analysis/escalation_rc.py --selftest     # synthetic fixtures under tempfile; opens NO DB of record
     python tools/analysis/escalation_rc.py --mutants      # the mutant table below, re-run (each must make the selftest fail)
  1. python tools/analysis/escalation_rc.py --dry-run      # POOL line first; pins; registered denominators; B0-2 pool check; the
                                                           #   UNION-AF-ROUTE inputs re-hashed; the frozen policy's sha; geometry and
                                                           #   filing agreement; GATE thresholds; NO EVAL key, NO statistic, writes nothing
  2. python tools/analysis/escalation_rc.py --run          # ONE EVAL key read (marker first); outcome WRITE-ONCE:
       experiment_results/archv2/escalation_rc/outcome.txt (+ escalation_rc.READ_STARTED). Never committed: pin by sha256 and back
       up to E:/TaxoArena_backup_<date>_escalation_rc with SHA256SUMS.txt (registration HYGIENE).
  --data-root <dir> (optional, every mode): the checkout whose experiment_results/, experiment_configs/, data_v2/ and cache DBs are
  read (sets TAXOARENA_DATA_ROOT and TAXOARENA_RESULTS_ROOT before any import); default = this checkout. From a worktree:
  --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena. Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; outcome and marker absent (write-once); the B0-2 pool check (g13_breakdown.pool_check_v2 through union_af_route);
  (2) the AF-U state (union_af_route.afu_state: D-8 commit, one-cell evidence S1-S6) and the inputs manifest with every pinned file
      re-hashed (union_af_route.load_inputs); the frozen TRAIN policy of UNION-AF-ROUTE (scratch, never committed) equal to its
      registered sha256 8d68018c...; (3) geometry (R2-R4): AF leaf vmfMu from the member snapshots, the one-cell centroid, K_0
      re-fitted (union_af_route.us_fit, seed 0); AF filing agreement >= 99.9% (R4) and K_0 re-filed EQUAL to k_cells_s0.tsv on
      every EVAL item; (4) GATE scores and thresholds per arm (R5); (5) the gen view (TRAIN key, sealed until the policy fit
      stage) and the eval view (route) through v2_declared_cells' guarded openers, the scored-set denominators, [G14-NOROW] for
      both arms, the B1-style marker written mode "x", THE EVAL KEY READ, views' sha after; (6) build_ud with the AF and K_0
      arms; the point policy re-fitted beside EVAL EQUAL to the frozen file (best single, tree_cell, xtree_cell K0) else [B3];
      (7) IDENTITY (R12) before any new number: arm accuracies best single 0.6049, AF-U 0.6201, K_0 0.6271 and G_AF +1.52pp
      [+0.14pp, +2.91pp] (UNION-AF-ROUTE outcome, sha256 e50a8e0f...) and 5,907 / 5,404, else [ERC-IDENTITY] / [ERC-DENOM];
      (8) v2_declared_cells.run_boot (B 2,000, default_rng(42)) with a hook that re-fits each replicate's policy and scores the
      escalation rule; the hook's cell / best-single accuracies must equal run_boot's own arms in every replicate ([ERC-HOOK]);
      (9) RC1, descriptive lines, risk-coverage curves, predictions, F-RC, words; the outcome written mode "x" (a view whose sha
      changed during the read writes *_VOID.txt instead).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  R1  Cells and policies: AF cell = union_af_route's af_cells.tsv (R1 there: modal flatLeaf leaf_id); K_0 cell = k_cells_s0.tsv;
      per-cell models = the frozen TRAIN policy (tree_cell / xtree_cell["K0"]; a cell without TRAIN mass -> the best single).
  R2  Centroids: AF graft leaves = the vmfMu of each member's LAST dag snapshot at sliceDim = the bundle dim 256 (the flatLeaf
      centroids; intent_transfer_s1 R6). A ONE-CELL member (IFEVAL; the author's decision L23660-L23667) has no snapshot: its cell's
      centroid = the unit mean of its TRAIN bundle items (used only for its OOS score). K_0 = union_af_route.us_fit(seed 0) on the
      bundle's TRAIN (the call that wrote k_cells_s0.tsv).
  R3  Candidate set = the cells the item's filing can reach. AF: an item of a one-cell member -> its one cell only (margin +inf,
      never margin-escalated); any other item -> every graft leaf (the one-cell cells excluded, as the graft files). K_0: the
      centroids of the item's declared source(s) (union_af_route R3; a two-source multi-class item searches both). margin =
      intent_transfer_s1.margins (top-1 minus top-2 cos; +inf with one candidate); OOS score = oos_baselines.maxcos (max-cos).
  R4  The margin is geometric; the route is the AF cell of record. REFUSED unless argmax over the AF candidates equals the AF cell
      on >= 99.9% of the scored non-one-cell EVAL items (count printed), and K_0's argmax equals k_cells_s0 on EVERY scored item.
  R5  Thresholds from GATE only: GATE items with a routing row in inputs/validation_merged's held-out file (side GATE); their AF
      cell = modal leaf (R1's rule), their sources = their rows' true_key sources. tau_m = numpy percentile 20 (linear) of GATE
      margins; tau_oos = numpy percentile 5 of GATE OOS scores (TPR 0.95: 95% of GATE items score at or above it); each arm its own.
      Escalate iff margin < tau_m OR OOS < tau_oos (strict). No EVAL value enters a threshold.
  R6  Decision fragility = 1 iff the frozen per-cell models of the item's two nearest candidate cells differ (0 with one
      candidate). DESCRIPTIVE ONLY: the registered rule is margin OR OOS (the orchestrator's brief also named fragility as part of
      the score; the registered text governs and fragility is a risk-coverage ordering and a rate).
  R7  RC1: D_E = acc(rule) - [(1 - e) acc(cells) + e acc(best single)] at the SAME weights inside each replicate (the analytic
      random-escalation expectation moves with e). Two-stage = v2_declared_cells.run_boot (TRAIN resampled by its train_unit,
      every policy re-fitted, EVAL components resampled within stratum); the escalation set is fixed (GATE is not resampled).
      Deciding interval = point +- 1.96 SE_2stage (G14's form, v2_declared_cells.contrast); percentile beside; i.i.d. SE (EVAL
      items i.i.d., policy fixed; run_boot's own draws) -> DEFF, n_eff = N / DEFF, MDE80 = 2.80 SE_2stage. HELD iff lo > 0;
      FAILED iff hi < 0 ("wholly below"); UNDETERMINED otherwise (an end point exactly at 0 is UNDETERMINED).
  R8  The K_0 arm runs the same rule with its own thresholds (descriptive); D_E(AF-U) - D_E(K_0) paired in the same replicates.
  R9  Risk-coverage (descriptive, point, frozen policy): coverage c = 1.00, 0.95, ..., 0.00; n_keep = round(c N); the kept items
      are the most confident (margin descending; OOS descending; fragility: non-fragile first, then margin descending); ties in
      item_id order; escalated items get the best single; the random column is analytic c acc(cells) + (1 - c) acc(best).
  R10 Predictions "X [lo, hi]" HELD iff the point lies in [lo, hi], endpoints inclusive; RC1's probabilities scored by the
      three-outcome Brier sum.
  R11 Not applicable (stated): no judge verdict (key-scored), so no wrong(established) count and no tie convention A / B; no call
      cache, --pilot or truncation guard (zero calls). V2-DECLARED-CELLS' C0 gate is not re-run: the identity R12 reproduces
      UNION-AF-ROUTE's printed arms through the same views, fit and replicates.
  R12 IDENTITY targets (UNION-AF-ROUTE outcome of record): best single 0.6049, AF-U leaf cell 0.6201, K_s K0 0.6271 (4 dp), U1 G_AF
      +1.52pp [+0.14pp, +2.91pp] (two-stage), 5,907 items / 5,404 components; refused otherwise, before any new number is printed.
  R13 This test's own one-read marker (escalation_rc.READ_STARTED) is written before its EVAL key read; UNION-AF-ROUTE's marker is
      neither reused nor touched.

SELFTEST (--selftest; synthetic fixtures; the real entry points run() / dry_run() executed on a complete layout in a temp dir:
union_af_route's own fixture with a ONE-CELL member (BBH), its vmfMu replaced by leaf prototypes, --build-inputs and
union_af_route --run executed to produce the inputs, the frozen policy and the identity digits; the views are v2_declared_cells'
sealed fixture views; the text / vector / side readers and the pool check are stubbed): see CASES at the end of this file.
  branches      RC1 HELD / FAILED / UNDETERMINED (end points exactly 0 -> UNDETERMINED), F-RC fired / not fired, P1 e and D_E and P2
                bands inclusive at both ends, the Brier values (1.0550 / 0.1550 / 1.4550), the verdict line of record, the required lines
  units         cand_scores against plain loops (one candidate -> +inf margin), the GATE percentiles against a hand percentile and the
                non-finite refusal, strict escalation, fragility, esc_stats, the three orderings with ties, rc_curve, interval, --data-root
  run_e2e       --run end to end on the one-cell fixture: GATE thresholds per arm, e per arm, D_E(AF-U) with its two-stage interval and
                SEs, D_E(K_0), the paired difference, the fragility rate and the AF-U risk-coverage rows at 0.50 / 0.80, all against an
                INDEPENDENT oracle (plain-loop policy fits on the fixture's raw rows, the prototypes, direct k-means calls, the same unit
                draws); the RC1 word and F-RC from the printed interval by the hand rule; the planted R4 disagreement counted; a second
                --run refused and the outcome unchanged
  refusals      pool check (POOL line still first), the frozen policy's sha, the R4 agreement floor, K_0 re-filing, [ERC-DENOM],
                [ERC-IDENTITY] (an arm digit; one interval end only; no new number printed before it), [ERC-HOOK], an empty GATE, the
                marker present, [B3]; no outcome written by any; no marker written by a pre-read refusal
  dry_run       POOL first, no EVAL statistic, nothing written; the REAL constants' lines (5907 / 5404, B 2000, default_rng(42), p20 / p5,
                0.999, the identity targets, the verdict line, the registration span)
  branch_cover  every print / refusal branch in BRANCHES executed
MUTANTS (--mutants; X01-X40 + the control X00; each edits the code above the SELFTEST section in memory and runs the selftest on
one layout built by the unedited code): 2026-10-03, 40 of 40 KILLED, control survived. First pass 38 / 40: X21 (written as
"if False and A or B": precedence left the B3 check alive, an ill-formed mutant, rewritten to remove the refusal) and X30 (the
verdict-line label dropped while the line's text stayed; the branches case now asserts the labelled phrase). Classes: verdict
boundaries (X01, X02, X28, X29), falsifier (X03, X31), the rule (X04, X05), wrong split side (X06), threshold arms / quantiles
(X07, X27), min<->max and score form (X08, X37), first-site-only and candidate sets (X09-X11), the D_E formula and denominator
(X12, X13), interval form / SE / pairing / seed (X14-X16, X32), the uncapped fork (X17: policy not re-fitted per replicate), every
refusal or gate (X18-X23, X33, X34, X36, X38-X40), risk-coverage orderings (X24-X26), the one-cell centroid (X35).
NOT DONE HERE: the real --run (the operator's, after READY); no Kotlin / Gradle (zero builds, the brief).
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

import io            # noqa: E402
import re            # noqa: E402
import json          # noqa: E402
import math          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import contextlib    # noqa: E402
from collections import Counter, defaultdict   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[ERC]"
TEST_ID = "ESCALATION-RC"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


PINS = (("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"),
        ("intent_transfer_s1.py", "4e9d9d05fbdf14d0a85966b4c897cfbfd779186d"),
        ("oos_baselines.py", "7e74108dedcb2d921be0da4cf8ddc842deb24d72"))
for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import union_af_route as UAR       # noqa: E402  (checks its own pins: g13_breakdown, g13_comparator, rp12_pairing, v2_declared_cells)
import intent_transfer_s1 as S1    # noqa: E402  (margins: T-C9's m(q))
import oos_baselines as OB         # noqa: E402  (maxcos: S0's C2 / OOS-TREE-CELLS' score)
V, GB, RP, GC = UAR.V, UAR.GB, UAR.RP, UAR.GC
G = V.G
import sqlite3                     # noqa: E402
sqlite3.connect = getattr(sqlite3.connect, "_raw", sqlite3.connect)

REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — ESCALATION-RC: on the union routing'
            ' data, does escalating low-margin, OOS or decision-fragile queries from the AF-U cell policy ..." L23960-L23973'
            ' (_as_of 964511fd, parent b9b67b11)')
COND_TEXT = ('CONDITION RESOLVED (record L23941 bracket; OOS-TREE-CELLS L23975-L23987, POSTRUN b9b67b11): OT1 EQUIVALENT within'
             ' 0.010, and below k-means: the OOS-based legs are read as written')
POOL = "pv2_1575de61bb20e977"
OUT = "experiment_results/archv2/escalation_rc"

REG = dict(
    pool=POOL,
    out=OUT + "/outcome.txt", marker=OUT + "/escalation_rc.READ_STARTED",
    uar_policy_sha="8d68018c013b7a770568b85d408a6fb027bb322f3219dded94e6b3a7d80a82fb",
    uar_outcome_sha="e50a8e0fa267db967981fb03320902c238fff505f00b1088d49c3c3a6596cd08",
    n_route=5907, comp_route=5404,
    identity=dict(best="0.6049", af="0.6201", k0="0.6271", g_af=("+1.52pp", "+0.14pp", "+2.91pp")),
    B=2000, seed=42, q_margin=20.0, q_oos=5.0, agree_min=0.999, kname="K0", kseed=0,
)
_REG = [REG]


def reg():
    return _REG[0]


SUPPORT = dict(se=0.00367, mde=0.0103, deff=1.595, n_eff=3704)
VERDICT_LINE = "RC1 DESCRIPTIVE-ONLY at prediction (SE 0.00367, MDE80 0.0103)"
PRED_E = (0.15, 0.35)
PRED_DE = (-0.003, 0.010)
PRED_DIFF = (-0.006, 0.006)
PROB_RC1 = (("HELD", 0.25), ("UNDETERMINED", 0.70), ("FAILED", 0.05))
GRID = tuple(round(1.0 - 0.05 * j, 2) for j in range(21))
ARMS = ("AF-U", "K_0")
HIT = Counter()


def hit(name):
    HIT[name] += 1


def P(rel):
    return UAR.P(rel)


def pp(x):
    return "%+.2fpp" % (100.0 * x)


def in_band(x, band):
    return bool(band[0] <= x <= band[1])


# ── geometry (R2-R4) ───────────────────────────────────────────────────────────────────────────────────────────────────

class Geo:
    pass


def load_geometry(say, man, single, b, af):
    """AF centroids (graft leaves' vmfMu + one-cell centroids) and K_0 centroids -> Geo."""
    c = UAR.reg()
    dim = int(c["dim"])
    g = Geo()
    names, mus = [], []
    for m, src in c["members"]:
        if src in single:
            continue
        snap = GB.last_snapshot(P("%s/%s/seed_42/dag_snapshots.jsonl" % (c["afu"], m)))
        for n in snap["nodes"]:
            if not n.get("isLeaf"):
                continue
            mu = n.get("vmfMu")
            mu = json.loads(mu) if isinstance(mu, str) else mu
            sd = int(n.get("sliceDim", len(mu)))
            if sd != dim or len(mu) != dim:
                refuse("leaf %s:%s has sliceDim %s / %d coordinates, not the bundle dim %d (R2)" % (src, n["id"], n.get("sliceDim"), len(mu), dim))
            names.append("%s:%s" % (src, n["id"]))
            mus.append(np.asarray(mu, dtype=np.float64))
    g.n_graft = len(names)
    Xt = GC.FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    titems = [str(x) for x in b["train_item"]]
    g.single_cells = {}
    for s, e in sorted(single.items()):
        rows = [j for j, it in enumerate(titems) if af.get(it) == e["cell"]]
        if not rows:
            refuse("one-cell member %s: no TRAIN bundle item in its cell %s (R2)" % (s, e["cell"]))
        mu = Xt[rows].mean(axis=0)
        names.append(e["cell"])
        mus.append(mu / np.linalg.norm(mu))
        g.single_cells[e["cell"]] = (s, len(rows))
    g.af_names = names
    g.af_C = GC.FM.unit_rows(np.vstack(mus))
    g.af_pos = {n: i for i, n in enumerate(names)}
    g.graft_idx = tuple(range(g.n_graft))
    classes = [str(x) for x in b["classes"]]
    tsrc = np.array([UAR.src_of(classes[i]) for i in np.asarray(b["train_y"], dtype=int)])
    C, csrc, cloc, _lab, _f = UAR.us_fit(Xt, tsrc, man["ksrc"], c["sources"], reg()["kseed"])
    g.k_C, g.k_src = C, csrc
    g.k_names = ["%s:%s:%03d" % (reg()["kname"], csrc[j], cloc[j]) for j in range(len(C))]
    g.k_pos = {n: i for i, n in enumerate(g.k_names)}
    g.dim = dim
    hit("GEO.LOADED")
    say("  GEOMETRY (R2): AF %d graft leaves (vmfMu, sliceDim %d) + %d one-cell centroid(s) %s = %d cells; K_0 %d centroids (us_fit seed"
        " %d, k per source %s)" % (g.n_graft, dim, len(g.single_cells), ", ".join("%s (%s, %d TRAIN items)" % (k, v[0], v[1]) for k, v in
                                                                                   sorted(g.single_cells.items())) or "",
                                    len(names), len(C), reg()["kseed"], ", ".join("%s %d" % (s, man["ksrc"][s]) for s in c["sources"])))
    return g


def af_cands(g, cell):
    """R3: a one-cell member's item -> its cell only; any other item -> every graft leaf."""
    if cell in g.single_cells:
        return (g.af_pos[cell],)
    return g.graft_idx


def k_cands(g, srcs):
    """R3: the centroids of the item's declared source(s)."""
    idx = tuple(int(j) for j in np.flatnonzero(np.isin(g.k_src, list(srcs))))
    if not idx:
        refuse("declared source(s) %s have no K_0 centroid" % (list(srcs),))
    return idx


def cand_scores(X, cands, C):
    """-> margin (S1.margins), OOS (OB.maxcos), top-1 and top-2 global centroid indices (-1 when one candidate)."""
    n = len(X)
    m, o = np.empty(n), np.empty(n)
    t1, t2 = np.empty(n, dtype=np.int64), np.full(n, -1, dtype=np.int64)
    groups = defaultdict(list)
    for i, cs in enumerate(cands):
        groups[tuple(cs)].append(i)
    for cs, idx in groups.items():
        idx = np.asarray(idx, dtype=np.int64)
        Cc, Xi = C[list(cs)], X[idx]
        m[idx] = S1.margins(Xi, Cc)
        o[idx] = OB.maxcos(Cc, Xi)
        order = np.argsort(-(Xi @ Cc.T), axis=1, kind="stable")
        arr = np.asarray(cs, dtype=np.int64)
        t1[idx] = arr[order[:, 0]]
        if len(cs) > 1:
            t2[idx] = arr[order[:, 1]]
    return m, o, t1, t2


def thresholds(m_gate, o_gate):
    c = reg()
    with np.errstate(invalid="ignore"):
        tm, to = float(np.percentile(m_gate, c["q_margin"])), float(np.percentile(o_gate, c["q_oos"]))
    if not (math.isfinite(tm) and math.isfinite(to)):
        refuse("a GATE threshold is not finite (tau_m %r, tau_oos %r)" % (tm, to))
    return tm, to


def escalate(m, o, tm, to):
    """R5: escalate iff margin < tau_m OR OOS < tau_oos (strict)."""
    return (m < tm) | (o < to)


def fragility(t1, t2, cell_model):
    """R6: 1 iff the per-cell models of the two nearest candidate cells differ (0 with one candidate)."""
    f = np.zeros(len(t1), dtype=bool)
    two = t2 >= 0
    f[two] = cell_model[t1[two]] != cell_model[t2[two]]
    return f


# ── items, vectors, GATE ──────────────────────────────────────────────────────────────────────────────────────────────

def item_rows(val):
    rows_h = RP.read_rows(os.path.join(P(val), RP.QUERIES))
    rows_t = RP.read_rows(os.path.join(P(val), RP.TRAIN))
    return rows_h, rows_t


def score_items(say, g, items, af_cell, srcs, vec, k_cell=None, label=""):
    """Scores of `items` under both arms -> dict(arm: (m, o, t1, t2)); the R4 agreement counts."""
    X = np.vstack([vec[i] for i in items]) if items else np.zeros((0, g.dim))
    ca = [af_cands(g, af_cell[i]) for i in items]
    ck = [k_cands(g, srcs[i]) for i in items]
    sa = cand_scores(X, ca, g.af_C)
    sk = cand_scores(X, ck, g.k_C)
    multi = [j for j, i in enumerate(items) if af_cell[i] not in g.single_cells]
    agree = sum(1 for j in multi if g.af_names[sa[2][j]] == af_cell[items[j]])
    kdiff = None
    if k_cell is not None:
        kdiff = sum(1 for j, i in enumerate(items) if g.k_names[sk[2][j]] != k_cell.get(i))
    return dict(AF=sa, K=sk, agree=(agree, len(multi)), kdiff=kdiff)


def gate_items(rows_h, side):
    """R5: GATE items with a routing row -> (items sorted, modal AF cell, sources)."""
    lh = GB.item_leaves(rows_h)
    srcs = UAR.item_sources(rows_h)
    its = sorted(i for i in lh if side.get(i, (None, None))[1] == "GATE")
    return its, {i: lh[i][0] for i in its}, srcs


def get_vectors(ids):
    return UAR._TV[0](sorted(ids), int(UAR.reg()["dim"]))


def check_vectors_vs_bundle(vec, b):
    items = [str(x) for x in b["eval_item"]] + [str(x) for x in b["train_item"]]
    X = np.vstack([GC.FM.unit_rows(np.asarray(b["eval_X"], dtype=np.float64)), GC.FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))])
    n = bad = 0
    for j, it in enumerate(items):
        if it in vec:
            n += 1
            bad += int(not np.allclose(vec[it], X[j], atol=1e-9))
    if bad:
        refuse("%d of %d vectors differ from the UNION-AF-ROUTE bundle's" % (bad, n))
    return n


def gate_block(say, g, rows_h, side, vec_gate=None):
    its, gcell, gsrc = gate_items(rows_h, side)
    if not its:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: the thresholds are undefined (R5)")
    vec = vec_gate if vec_gate is not None else get_vectors(its)
    nov = [i for i in its if i not in vec]
    if nov:
        refuse("%d GATE item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    sc = score_items(say, g, its, gcell, gsrc, vec)
    th = {}
    for arm, key in (("AF-U", "AF"), ("K_0", "K")):
        th[arm] = thresholds(sc[key][0], sc[key][1])
        say("  GATE THRESHOLDS %-5s (R5; n GATE %d): tau_m = p%g of margin = %.6f | tau_oos = p%g of OOS = %.6f (TPR 0.95) | margin +inf"
            " (one candidate) on %d GATE items" % (arm, len(its), reg()["q_margin"], th[arm][0], reg()["q_oos"], th[arm][1],
                                                  int(np.isinf(sc[key][0]).sum())))
    n_side = sum(1 for _i, (_c, s) in side.items() if s == "GATE")
    say("  GATE side items %d; with a routing row (used) %d; without (not used) %d" % (n_side, len(its), n_side - len(its)))
    hit("GATE.DONE")
    return th, len(its)


# ── statistics ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def esc_stats(cc, cb, f, v):
    """Weighted escalation statistics (R7). cc / cb: per-item correctness of the cell policy / the best single; f: escalated."""
    tot = float(v.sum())
    a_cell, a_best = float(v @ cc) / tot, float(v @ cb) / tot
    a_rule = float(v @ np.where(f, cb, cc)) / tot
    e = float(v @ f.astype(np.float64)) / tot
    return dict(acc_cell=a_cell, acc_best=a_best, acc_rule=a_rule, e=e, d_e=a_rule - ((1.0 - e) * a_cell + e * a_best))


def interval(pt, two, iid, n):
    """G14's deciding form: point +- 1.96 SE_2stage; percentile beside; DEFF = var_2stage / var_iid."""
    v2, vi = V._var(two), V._var(iid)
    se2, sei = math.sqrt(v2), math.sqrt(vi)
    deff = v2 / vi if vi > 0 else float("nan")
    return dict(point=pt, se2=se2, lo=pt - 1.96 * se2, hi=pt + 1.96 * se2, se_iid=sei, deff=deff,
                n_eff=(n / deff) if deff == deff and deff > 0 else float("nan"), mde=2.80 * se2, n=n,
                pct=tuple(float(x) for x in np.nanpercentile(np.asarray(two, dtype=np.float64), [2.5, 97.5])))


def rc1_verdict(st):
    """R7: HELD iff lo > 0; FAILED iff hi < 0; UNDETERMINED otherwise."""
    if st["lo"] > 0:
        return "HELD"
    if st["hi"] < 0:
        return "FAILED"
    return "UNDETERMINED"


def brier(verdict):
    return float(sum((p - (1.0 if k == verdict else 0.0)) ** 2 for k, p in PROB_RC1))


def rc_curve(cc, cb, order, grid=GRID):
    """R9: accuracy when the first round(c N) items of `order` (most confident first) keep the cell policy."""
    n = len(cc)
    out = []
    for c_ in grid:
        k = int(round(c_ * n))
        keep = np.zeros(n, dtype=bool)
        keep[order[:k]] = True
        out.append(float(np.where(keep, cc, cb).mean()))
    return out


def orders(m, o, frag):
    pos = np.arange(len(m))
    return dict(margin=np.lexsort((pos, -m)), oos=np.lexsort((pos, -o)), fragility=np.lexsort((pos, -m, frag.astype(int))))


# ── the readout lines (pure functions of the stats; the selftest drives every branch through them) ──────────────────────

def rc_lines(st):
    L = []
    say = L.append
    c = reg()
    a, k, d = st["AF-U"], st["K_0"], st["diff"]
    say("")
    say("=== ESCALATION-RC (%s) ===" % REG_TEXT)
    say(COND_TEXT)
    say("DENOMINATOR: %d EVAL items in %d components (union EVAL, G14's scored set; Llama excluded); TRAIN %d items (policy fit);"
        " GATE %d items (thresholds only); never joined with any other set" % (a["n"], st["comp"], st["n_train"], st["n_gate"]))
    for arm, s in (("AF-U", a), ("K_0", k)):
        say("  %s: e = %.5f (escalated %d of %d: margin only %d, OOS only %d, both %d); acc(cells) %.5f, acc(best single) %.5f,"
            " acc(rule) %.5f; random-escalation expectation %.5f; decision fragility rate %.5f (escalated %.5f, kept %.5f)" % (
                arm, s["e"], s["n_esc"], s["n"], s["n_m"], s["n_o"], s["n_mo"], s["acc_cell"], s["acc_best"], s["acc_rule"],
                (1 - s["e"]) * s["acc_cell"] + s["e"] * s["acc_best"], s["frag"], s["frag_esc"], s["frag_kept"]))
    say("RC1 (DECIDING; the INTERVAL decides): D_E = acc(rule on AF-U) - [(1 - e) acc(AF-U policy) + e acc(best single)] = %+.5f |"
        " two-stage 95%% [%+.5f, %+.5f] (point +- 1.96 SE_2stage) | percentile [%+.5f, %+.5f]" % (
            a["point"], a["lo"], a["hi"], a["pct"][0], a["pct"][1]))
    say("  support RC1: n %d, SE_2stage %.5f (registered 0.00367), i.i.d. SE %.5f, DEFF %.3f (registered 1.595, UNION-AF-ROUTE U1"
        " tree arm), n_eff %.0f (registered 3,704), MDE80 %.5f (registered 0.0103); verdict line of record: %s" % (
            a["n"], a["se2"], a["se_iid"], a["deff"], a["n_eff"], a["mde"], VERDICT_LINE))
    v = rc1_verdict(a)
    if v == "HELD":
        hit("RC1.HELD")
        say("  RC1 -> HELD (the 95% interval lies wholly above 0): escalating low-margin / OOS items of the AF-U route to the best"
            " single model beats escalating the same share at random, on these cells")
    elif v == "FAILED":
        hit("RC1.FAILED")
        say("  RC1 -> FAILED (the 95% interval lies wholly below 0)")
    else:
        hit("RC1.UNDETERMINED")
        say("  RC1 -> UNDETERMINED (the 95% interval covers 0)")
    if v == "FAILED":
        hit("FRC.FIRED")
        say("FALSIFIER F-RC: FIRED (RC1 FAILED): escalating low-confidence queries to the best single model costs accuracy against"
            " random escalation, so margin / OOS escalation of the route is not a usable safety valve on these cells")
    else:
        hit("FRC.NOT_FIRED")
        say("FALSIFIER F-RC: NOT FIRED (RC1 %s; F-RC fires iff RC1 FAILED)" % v)
    say("DESCRIPTIVE: D_E(K_0) = %+.5f | two-stage 95%% [%+.5f, %+.5f] | percentile [%+.5f, %+.5f] | SE_2stage %.5f, DEFF %.3f" % (
        k["point"], k["lo"], k["hi"], k["pct"][0], k["pct"][1], k["se2"], k["deff"]))
    say("DESCRIPTIVE: D_E(AF-U) - D_E(K_0) = %+.5f | two-stage 95%% [%+.5f, %+.5f] | percentile [%+.5f, %+.5f] (paired replicates;"
        " the like-for-like cell comparator; nothing here is tree-specific)" % (d["point"], d["lo"], d["hi"], d["pct"][0], d["pct"][1]))
    say("STRUCTURAL (registered (g)): |D_E| <= e x |acc gap on the escalated items| ; AF-U e %.5f, acc(best) - acc(cells) on the"
        " escalated items %+.5f" % (a["e"], a["gap_esc"]))
    for arm in ARMS:
        cv = st["curves"][arm]
        say("RISK-COVERAGE %s (descriptive, point, frozen policy; accuracy when the most confident share c keeps its cell and the"
            " rest go to the best single; R9):" % arm)
        say("    coverage   margin    OOS       fragility random")
        for j, c_ in enumerate(GRID):
            say("    %.2f       %.5f   %.5f   %.5f   %.5f" % (c_, cv["margin"][j], cv["oos"][j], cv["fragility"][j], cv["random"][j]))
        say("    the rule's operating point: coverage %.5f" % (1.0 - st[arm]["e"]))
    ok = in_band(a["e"], PRED_E)
    hit("P1E.HELD" if ok else "P1E.FAILED")
    say("PREDICTION P1 e 0.25 [0.15, 0.35]: observed %.5f -> %s" % (a["e"], "HELD" if ok else "FAILED"))
    ok = in_band(a["point"], PRED_DE)
    hit("P1D.HELD" if ok else "P1D.FAILED")
    say("PREDICTION P1 D_E +0.003 [-0.003, +0.010]: observed %+.5f -> %s" % (a["point"], "HELD" if ok else "FAILED"))
    say("PREDICTION P1 RC1 HELD 0.25, UNDETERMINED 0.70, FAILED 0.05: observed %s; Brier %.4f" % (v, brier(v)))
    ok = in_band(d["point"], PRED_DIFF)
    hit("P2.HELD" if ok else "P2.FAILED")
    say("PREDICTION P2 D_E(AF-U) - D_E(K_0) 0.000 [-0.006, +0.006] (descriptive): observed %+.5f -> %s" % (d["point"], "HELD" if ok else "FAILED"))
    say("WORDS: this escalates the ROUTE to the best single model, never to a judge (ESCALATE-LLAMA-LAW untouched); a HELD supports"
        " 'escalate the route on low margin or OOS' for the filing layer, never tree-specific without the k-means arm; key-scored end"
        " to end (no judge verdict: no wrong(established) count, no convention A / B arises); aggregate numbers only, no per-cell"
        " model rows; content-closed under CK-CLOSE-v2 (residual disclosed)")
    say("WILL NOT SHOW (registered): escalation to a judge; judged decisions; real traffic; a tree-specific gain; anything beyond the"
        " union roster and one draw")
    return L, dict(RC1=v, F_RC=(v == "FAILED"))


# ── the views (the key read) ───────────────────────────────────────────────────────────────────────────────────────────

def read_views(cfg, say, dry, af, k0, marker_text=None):
    """The gen view (TRAIN key) and, unless dry, the eval view (EVAL key) through v2_declared_cells' guarded openers."""
    rule = cfg.pre.get("variant_rule")
    say("--- TRAIN (gen_view, open_generation('policy_fit')) ---")
    tw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view", say)
    nc, ni, scope = V.pool_row(tw, cfg.pool_u, cfg.cv_u)
    say("  pool %s (scope %r): %d components, %d items of %s" % (cfg.pool_u, scope, nc, ni, cfg.cv_u))
    if nc != cfg.reg["comp_eval_u"] or ni != cfg.reg["n_eval_u"]:
        refuse("pool counts %d / %d differ from the registration's %d / %d" % (nc, ni, cfg.reg["comp_eval_u"], cfg.reg["n_eval_u"]))
    regm = V.registry(tw, cfg.cv_u)
    models = sorted(m for m, s in regm.items() if s == "ACTIVE")
    say("  roster (ACTIVE, sorted = the argmax tie-break order): %d (registered %d); %s absent: %s" % (
        len(models), cfg.reg["roster_u"], V.EXCLUDED, V.EXCLUDED not in models))
    if len(models) != cfg.reg["roster_u"] or V.EXCLUDED in models:
        refuse("roster check failed")
    train_meta = V.side_items(tw, cfg.cv_u, "TRAIN")
    comp_strata = V.component_strata(tw)
    cc_tr = V.cell_counts(tw, "response_lite", cfg.cv_u, models, train_meta)
    say("  TRAIN items %d; structurally key-complete under %s: %d" % (len(train_meta), rule, len(V.structurally_complete(cc_tr, models, rule))))
    if dry:
        tw.close()
        V.after_sha(cfg.gen_path, gsha, "gen_view", say)
        say("  eval_view %s pinned sha256-bytes %s: NOT opened by --dry-run" % (cfg.eval_path, cfg.eval_sha))
        return None
    tw.unseal("ESCALATION-RC: the TRAIN key for the per-replicate policy fits (the frozen policy is checked beside EVAL)")
    K_tr, kst_tr = V.read_key(tw, "response_lite", cfg.cv_u, models, train_meta, True, rule)
    tw.close()
    ok_g = V.after_sha(cfg.gen_path, gsha, "gen_view", say)
    say("  TRAIN key: cells single %d, multi %d (unusable %d); MATH-FIX overlay rows %d, value changed %d; key rows fetched %d" % (
        kst_tr["single"], kst_tr["multi"], kst_tr["multi_unusable"], kst_tr["overlay_rows"], kst_tr["overlay_changed"], kst_tr["key_rows_fetched"]))
    say("--- EVAL (eval_view, open_eval('route'); after the frozen TRAIN policy file) ---")
    V.b3_guard(cfg)
    tw, esha = V.open_tw("eval", "route", cfg.eval_path, cfg.eval_sha, "eval_view", say)
    nc2, ni2, _ = V.pool_row(tw, cfg.pool_u, cfg.cv_u)
    if (nc2, ni2) != (nc, ni):
        refuse("eval_view pool row differs from gen_view's")
    eval_meta = V.side_items(tw, cfg.cv_u, "EVAL")
    if sorted(m for m, s in V.registry(tw, cfg.cv_u).items() if s == "ACTIVE") != models:
        refuse("eval_view's roster differs from gen_view's")
    cc_ev = V.cell_counts(tw, "response", cfg.cv_u, models, eval_meta)
    pre_ok = V.structurally_complete(cc_ev, models, rule)
    say("  EVAL items %d (%d components); structurally key-complete under %s: %d" % (
        len(eval_meta), len(set(v[0] for v in eval_meta.values())), rule, len(pre_ok)))
    for nm, cells in (("AF-U", af), ("K_0", k0)):
        norow = sorted(i for i in pre_ok if cells.get(i, V.NO_ROUTING_ROW) == V.NO_ROUTING_ROW)
        say("  %s: EVAL items of the scoring set without a cell: %d (must be 0)" % (nm, len(norow)))
        if norow:
            hit("REFUSE.NOROW")
            refuse("[G14-NOROW] %s: %d EVAL item(s) of the scoring set have no cell (first %s); refused before the EVAL key read"
                   % (nm, len(norow), norow[:3]))
    G.read_marker(P(reg()["marker"]), marker_text)
    hit("MARKER.WRITTEN")
    tw.unseal("ESCALATION-RC route read of EVAL (marker %s written)" % reg()["marker"])
    K_ev, kst_ev = V.read_key(tw, "response", cfg.cv_u, models, eval_meta, True, rule)
    tw.close()
    ok_e = V.after_sha(cfg.eval_path, esha, "eval_view", say)
    say("  EVAL key: cells single %d, multi %d (unusable %d); MATH-FIX overlay rows %d, value changed %d; key rows fetched %d" % (
        kst_ev["single"], kst_ev["multi"], kst_ev["multi_unusable"], kst_ev["overlay_rows"], kst_ev["overlay_changed"], kst_ev["key_rows_fetched"]))
    D = V.build_ud(models, train_meta, eval_meta, K_tr, K_ev, comp_strata, cfg.pre["train_unit"], None, cfg.reg["placebo_seed"],
                   tree=af, xtrees={reg()["kname"]: k0})
    D.fit_asserts = 0
    return D, ok_g and ok_e


# ── modes ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def header(say, mode):
    c = reg()
    say("POOL %s (%s; %s; the first line of every mode)" % (c["pool"], TEST_ID, mode))
    say("%s | registration %s" % (TEST_ID, REG_TEXT))
    say("  " + COND_TEXT)
    say("  results root %s; data root %s; calls 0 (zero-call CPU reader; no judge, no LLM, no embedding call, no build)" % (
        UAR._ROOT[0], RP.C.DATA_ROOT))
    for f in [os.path.abspath(__file__)] + [os.path.join(HERE, n) for n, _ in PINS] + [V.__file__]:
        say("  " + G.identity_line(f))
    say("  threads: %s" % ", ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))


def denominators(say):
    c = reg()
    idn = c["identity"]
    say("DENOMINATORS (registered Support (a)): %d EVAL items in %d components (union EVAL, G14's set); DEFF 1.595 (UNION-AF-ROUTE U1"
        " tree arm, two-stage), n_eff 3,704, SE 0.00367, MDE80 0.0103; %s" % (c["n_route"], c["comp_route"], VERDICT_LINE))
    say("PLANNED: B = %d two-stage replicates (default_rng(%d)); tau_m = GATE p%g of margin, tau_oos = GATE p%g of OOS (TPR 0.95); R4"
        " agreement floor %.3f; K_0 = %s (us_fit seed %d)" % (c["B"], c["seed"], c["q_margin"], c["q_oos"], c["agree_min"], c["kname"], c["kseed"]))
    say("IDENTITY TARGETS (R12, UNION-AF-ROUTE outcome sha256 %s): best single %s, AF-U leaf cell %s, K_s K0 %s, G_AF %s [%s, %s]" % (
        c["uar_outcome_sha"][:16], idn["best"], idn["af"], idn["k0"], idn["g_af"][0], idn["g_af"][1], idn["g_af"][2]))


def frozen_policy(say):
    pth = P(UAR.reg()["policy"])
    if not os.path.isfile(pth):
        hit("REFUSE.POLICY_ABSENT")
        refuse("UNION-AF-ROUTE's frozen TRAIN policy %s is absent" % UAR.reg()["policy"])
    sh = sha256_bytes(pth)
    if sh != reg()["uar_policy_sha"]:
        hit("REFUSE.POLICY_SHA")
        refuse("the frozen TRAIN policy %s is sha256 %s, not the registered %s" % (UAR.reg()["policy"], sh, reg()["uar_policy_sha"]))
    pol = json.load(open(pth, encoding="utf-8"))
    say("  frozen TRAIN policy %s sha256 %s (= the registered pin; never committed); best single %s; %d AF cells, %d %s cells" % (
        UAR.reg()["policy"], sh, pol["best_single"], len(pol["tree_cell"]), len(pol["xtree_cell"][reg()["kname"]]), reg()["kname"]))
    return pol


def prepare(say, mode):
    """Everything before the key: pool check, AF-U state, inputs, frozen policy, geometry, GATE thresholds."""
    c, u = reg(), UAR.reg()
    rc, msg = UAR._POOL[0](c["pool"])
    say("POOL CHECK (B0-2): rc %d | %s" % (rc, msg))
    if rc != 0:
        hit("REFUSE.POOL")
        refuse("the B0-2 pool check failed: %s" % msg)
    pairs, val, ksrc, commit, single = UAR.afu_state(say)
    man, _msha = UAR.load_inputs(say)
    if man["ksrc"] != ksrc:
        refuse("the inputs were built at leaf counts %s, the AF-U snapshots now give %s" % (man["ksrc"], ksrc))
    ip = UAR.input_paths()
    af, _d1 = V.load_tree_cells(P(ip["af"]), man["inputs"][ip["af"]])
    k0, _d2 = V.load_tree_cells(P(ip["k"][c["kseed"]]), man["inputs"][ip["k"][c["kseed"]]])
    pol = frozen_policy(say)
    b, _meta = GC.load_bundle(P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    g = load_geometry(say, man, single, b, af)
    side, _smeta = UAR._SIDES[0]()
    rows_h, rows_t = item_rows(ip["merged"] if single else val)
    srcs = UAR.item_sources(rows_h + rows_t)
    th, n_gate = gate_block(say, g, rows_h, side)
    return dict(af=af, k0=k0, pol=pol, b=b, g=g, side=side, srcs=srcs, th=th, n_gate=n_gate, single=single, rows_h=rows_h)


def eval_block(say, S, items, k_check=True):
    """Scores, escalation flags and fragility of the scored EVAL items under both arms (R3-R6)."""
    c = reg()
    g, af, k0, srcs = S["g"], S["af"], S["k0"], S["srcs"]
    miss = [i for i in items if i not in srcs]
    if miss:
        refuse("%d EVAL item(s) have no routing row (first %s)" % (len(miss), miss[:3]))
    vec = get_vectors(items)
    nov = [i for i in items if i not in vec]
    if nov:
        refuse("%d EVAL item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    nb = check_vectors_vs_bundle(vec, S["b"])
    sc = score_items(say, g, items, af, srcs, vec, k_cell=k0)
    ag, nm = sc["agree"]
    share = ag / nm if nm else 1.0
    say("  R4 AF filing agreement: argmax over the candidates = the AF cell of record on %d of %d non-one-cell EVAL items (%.5f; floor"
        " %.3f); vectors equal to the bundle's on %d items" % (ag, nm, share, c["agree_min"], nb))
    if share < c["agree_min"]:
        hit("REFUSE.AGREE")
        refuse("R4: AF filing agreement %.5f < %.3f: the vmfMu geometry does not reproduce the AF cells" % (share, c["agree_min"]))
    if k_check:
        say("  R4 K_0 re-filing: %d of %d EVAL items differ from %s (must be 0)" % (sc["kdiff"], len(items), "k_cells_s%d.tsv" % c["kseed"]))
        if sc["kdiff"]:
            hit("REFUSE.KDIFF")
            refuse("R4: K_0 re-filed differs from k_cells_s%d.tsv on %d item(s)" % (c["kseed"], sc["kdiff"]))
    out = {}
    for arm, key in (("AF-U", "AF"), ("K_0", "K")):
        m, o, t1, t2 = sc[key]
        tm, to = S["th"][arm]
        out[arm] = dict(m=m, o=o, t1=t1, t2=t2, f=escalate(m, o, tm, to), fm=m < tm, fo=o < to)
    return out


def dry_run(out=print):
    say = out
    header(say, "--dry-run")
    denominators(say)
    S = prepare(say, "--dry-run")
    ev_items = sorted(i for i, (_c, s) in S["side"].items() if s == "EVAL" and S["af"].get(i, V.NO_ROUTING_ROW) != V.NO_ROUTING_ROW)
    say("  EVAL side items with an AF cell (before the key-complete filter; no key read): %d" % len(ev_items))
    eval_block(say, S, ev_items, k_check=True)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = P(UAR.reg()["policy"])
    read_views(cfg, say, True, S["af"], S["k0"])
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no EVAL key read; no statistic of EVAL printed.")
    hit("DRY.DONE")
    return 0


def cell_models(pol, names, models, key=None):
    d = pol["tree_cell"] if key is None else pol["xtree_cell"][key]
    gb = models.index(pol["best_single"])
    return np.array([models.index(d[n]) if d.get(n) is not None else gb for n in names], dtype=np.int64)


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    header(say, "--run")
    for p in (c["out"], c["marker"]):
        if os.path.exists(P(p)):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    denominators(say)
    S = prepare(say, "--run")
    ev_all = sorted(i for i, (_c, s_) in S["side"].items() if s_ == "EVAL" and S["af"].get(i, V.NO_ROUTING_ROW) != V.NO_ROUTING_ROW)
    say("  EVAL side items with an AF cell (scored before the key read; the key-complete subset is taken after): %d" % len(ev_all))
    sc_all = eval_block(say, S, ev_all)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = P(UAR.reg()["policy"])
    if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):
        refuse("the reader's B / seed %s / %s are not the registered %s / %s" % (cfg.reg["B"], cfg.reg["seed"], c["B"], c["seed"]))
    D, ok_sha = read_views(cfg, say, False, S["af"], S["k0"],
                           marker_text="ESCALATION-RC: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"])
    n_comp = D.eval_units["n_units"]
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    if (D.n_eval, n_comp) != (c["n_route"], c["comp_route"]):
        hit("REFUSE.DENOM")
        refuse("[ERC-DENOM] the scored set is %d items / %d components, not the registered %d / %d" % (D.n_eval, n_comp, c["n_route"], c["comp_route"]))
    pol = S["pol"]
    P0 = V.fit(D, V.train_full(D))
    pj = V.policy_json(D, P0, cfg, "")
    nn = lambda d: {k: v for k, v in d.items() if v is not None}
    if D.models[P0.gb] != pol["best_single"] or nn(pj["tree_cell"]) != nn(pol["tree_cell"]) or \
            nn(pj["xtree_cell"][c["kname"]]) != nn(pol["xtree_cell"][c["kname"]]):
        hit("REFUSE.B3")
        refuse("[B3] the point policy re-fitted beside EVAL differs from UNION-AF-ROUTE's frozen file")
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s, AF and %s cells)" % (pol["best_single"], c["kname"]))
    items_E = [D.items[k] for k in D.E]
    pos_all = {it: j for j, it in enumerate(ev_all)}
    if any(it not in pos_all for it in items_E):
        refuse("a scored EVAL item was not scored before the key read")
    idx = np.array([pos_all[it] for it in items_E], dtype=np.int64)
    sc = {arm: {k_: v_[idx] for k_, v_ in sc_all[arm].items()} for arm in ARMS}
    g = S["g"]
    AE = D.A[D.E]
    r = np.arange(len(D.E))
    gt, nt = D.groupings["tree"]
    gk, nk = D.groupings["x:" + c["kname"]]
    karm = 6 + sorted(D.xnames).index(c["kname"])
    cm = dict(AF=cell_models(pol, g.af_names, D.models), K=cell_models(pol, g.k_names, D.models, c["kname"]))
    frag = {"AF-U": fragility(sc["AF-U"]["t1"], sc["AF-U"]["t2"], cm["AF"]), "K_0": fragility(sc["K_0"]["t1"], sc["K_0"]["t2"], cm["K"])}
    fl = {arm: sc[arm]["f"] for arm in ARMS}

    def corr(Pp):
        gb = Pp.gb
        def res(key, gg):
            p_ = Pp.pol[key][gg[D.E]]
            return np.where(p_ < 0, gb, p_)
        return AE[r, gb].astype(np.float64), AE[r, res("tree", gt)].astype(np.float64), AE[r, res("x:" + c["kname"], gk)].astype(np.float64)

    rec = dict(two=[], chk=[])

    def hook(D_, wt, v):
        Pp = V.fit(D_, wt)
        cb, ca, ck = corr(Pp)
        v = np.asarray(v, dtype=np.float64)
        sa, sk = esc_stats(ca, cb, fl["AF-U"], v), esc_stats(ck, cb, fl["K_0"], v)
        rec["two"].append((sa["d_e"], sk["d_e"]))
        rec["chk"].append((sa["acc_best"], sa["acc_cell"], sk["acc_cell"]))
    bt = V.run_boot(D, c["B"], c["seed"], hook=hook)
    want = 2 * c["B"] + 2
    if D.fit_asserts != want:
        refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, want))
    chk = np.asarray(rec["chk"])
    ref = np.stack([bt["two"][:, 0, V.BS], bt["two"][:, 0, V.TREE], bt["two"][:, 0, karm]], axis=1)
    if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):
        hit("REFUSE.HOOK")
        refuse("[ERC-HOOK] the hook's re-fitted accuracies differ from run_boot's own arms")
    # IDENTITY (R12) before any new number
    idn = c["identity"]
    got = dict(best="%.4f" % bt["point"][0, V.BS], af="%.4f" % bt["point"][0, V.TREE], k0="%.4f" % bt["point"][0, karm])
    gaf = V.contrast(bt, D, "ALL", V.TREE, V.BS)
    got_g = (pp(gaf["point"]), pp(gaf["lo"]), pp(gaf["hi"]))
    if any(got[k] != idn[k] for k in ("best", "af", "k0")) or got_g != tuple(idn["g_af"]):
        hit("REFUSE.IDENTITY")
        refuse("[ERC-IDENTITY] best / AF-U / K0 %s / %s / %s and G_AF %s [%s, %s] are not UNION-AF-ROUTE's %s / %s / %s and %s [%s, %s]"
               % ((got["best"], got["af"], got["k0"]) + got_g + (idn["best"], idn["af"], idn["k0"]) + tuple(idn["g_af"])))
    say("IDENTITY (R12): best single %s, AF-U leaf cell %s, K_s K0 %s, G_AF %s [%s, %s] -> REPRODUCED (UNION-AF-ROUTE's printed digits)"
        % ((got["best"], got["af"], got["k0"]) + got_g))
    hit("IDENTITY.OK")
    # i.i.d. replicates: run_boot's own draws (default_rng(seed), items i.i.d., policy fixed)
    cb0, ca0, ck0 = corr(bt["P0"])
    rng = np.random.default_rng(c["seed"])
    NE = len(D.E)
    iid = []
    for _b in range(c["B"]):
        v = np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64)
        iid.append((esc_stats(ca0, cb0, fl["AF-U"], v)["d_e"], esc_stats(ck0, cb0, fl["K_0"], v)["d_e"]))
    iid = np.asarray(iid)
    two = np.asarray(rec["two"])
    ones = np.ones(NE)
    st = dict(comp=n_comp, n_train=D.n_train, n_gate=S["n_gate"], curves={})
    for j, (arm, cc) in enumerate((("AF-U", ca0), ("K_0", ck0))):
        p = esc_stats(cc, cb0, fl[arm], ones)
        s = interval(p["d_e"], two[:, j], iid[:, j], NE)
        f, fr = fl[arm], frag[arm]
        s.update(p, n_esc=int(f.sum()), n_m=int((sc[arm]["fm"] & ~sc[arm]["fo"]).sum()), n_o=int((~sc[arm]["fm"] & sc[arm]["fo"]).sum()),
                 n_mo=int((sc[arm]["fm"] & sc[arm]["fo"]).sum()), frag=float(fr.mean()),
                 frag_esc=float(fr[f].mean()) if f.any() else float("nan"), frag_kept=float(fr[~f].mean()) if (~f).any() else float("nan"),
                 gap_esc=float((cb0[f] - cc[f]).mean()) if f.any() else 0.0)
        st[arm] = s
        od = orders(sc[arm]["m"], sc[arm]["o"], fr)
        cv = {k_: rc_curve(cc, cb0, od[k_]) for k_ in ("margin", "oos", "fragility")}
        cv["random"] = [c_ * p["acc_cell"] + (1 - c_) * p["acc_best"] for c_ in GRID]
        st["curves"][arm] = cv
    st["diff"] = interval(st["AF-U"]["point"] - st["K_0"]["point"], two[:, 0] - two[:, 1], iid[:, 0] - iid[:, 1], NE)
    L, words = rc_lines(st)
    for ln in L:
        say(ln)
    text = "\n".join(lines) + "\n"
    if not ok_sha:
        G.write_once(P(c["out"]).replace(".txt", "_VOID.txt"), text + "[VOID] a view's sha differs after the read\n")
        refuse("[PIN] a view's sha256 differs after the read: outcome written to _VOID, not to the file of record")
    G.write_once(P(c["out"]), text)
    out("OUTCOME written write-once: %s (sha256 %s)" % (c["out"], hashlib.sha256(text.encode("utf-8")).hexdigest()))
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, sc=sc, frag=frag, bt=bt)


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

BRANCHES = ("RC1.HELD", "RC1.FAILED", "RC1.UNDETERMINED", "FRC.FIRED", "FRC.NOT_FIRED", "P1E.HELD", "P1E.FAILED", "P1D.HELD",
            "P1D.FAILED", "P2.HELD", "P2.FAILED", "IDENTITY.OK", "RUN.DONE", "DRY.DONE", "MARKER.WRITTEN", "GATE.DONE", "GEO.LOADED",
            "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.POLICY_SHA", "REFUSE.AGREE", "REFUSE.KDIFF", "REFUSE.DENOM", "REFUSE.IDENTITY",
            "REFUSE.B3", "REFUSE.HOOK", "REFUSE.GATE_EMPTY")
FX_NOISE = 0.45


class _Lay:
    pass


def _fx_vectors(fx, rs):
    """Leaf prototypes (one-hot) and item vectors whose argmax over the graft prototypes is their filed leaf (rejection sampling);
    the multi-class EVAL item is planted near MMLU_PRO:L0 while its route is its MATH leaf (one R4 disagreement)."""
    leaves = ["%s:%s" % (so, lid) for so, lid, _d in UAR.FX_LEAVES]
    proto = {lf: np.eye(UAR.FX_DIM)[j] for j, lf in enumerate(leaves)}
    graft = [lf for lf in leaves if lf.split(":")[0] != fx.single]
    Cg = np.vstack([proto[lf] for lf in graft])
    for it in sorted(fx.vec):
        lf = fx.filed.get(it) or ""
        src = fx.strata[it][0]
        target = "MMLU_PRO:L0" if it == fx.mc else (lf if lf in proto else None)
        while True:
            base = proto[target] if target else np.zeros(UAR.FX_DIM)
            v = base + FX_NOISE * rs.normal(0, 1, UAR.FX_DIM)
            v = v / np.linalg.norm(v)
            if target is None or src == fx.single or graft[int(np.argmax(Cg @ v))] == target:
                break
        fx.vec[it] = v
    return proto, graft


def _fx_snapshots(fx, proto):
    afu = os.path.join(fx.tmp, *fx.afu.split("/"))
    for m, so in UAR.FX_MEMBERS:
        if so == fx.single:
            continue
        p = os.path.join(afu, m, "seed_42", "dag_snapshots.jsonl")
        snaps = [json.loads(x) for x in open(p, encoding="utf-8").read().splitlines() if x.strip()]
        for n in snaps[-1]["nodes"]:
            if n.get("isLeaf"):
                n["vmfMu"] = [float(x) for x in proto["%s:%s" % (so, n["id"])]]
                n["sliceDim"] = UAR.FX_DIM
        with open(p, "w", encoding="utf-8") as f:
            f.write("".join(json.dumps(x) + "\n" for x in snaps))


def _uar_identity(text):
    num = lambda lab: re.search(r"^    %s\s+([0-9.]+)\s" % re.escape(lab), text, re.M).group(1)
    m = re.search(r"U1: G_AF = .*? = ([+-][0-9.]+pp) \(.*?\) \| two-stage \[([+-][0-9.]+pp), ([+-][0-9.]+pp)\]", text)
    return dict(best=num("best single"), af=num("AF-U leaf cell"), k0=num("K_s K0"), g_af=(m.group(1), m.group(2), m.group(3)))


def _build_layout(tmp, single="BBH", seed=23):
    """union_af_route's fixture with a one-cell member, real centroids, its --build-inputs and --run -> _Lay."""
    fx = UAR._fixture(tmp, single=single)
    proto, graft = _fx_vectors(fx, np.random.RandomState(seed))
    _fx_snapshots(fx, proto)
    with UAR._patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            UAR.build_inputs(out=lambda s: None)
    b, _m = GC.load_bundle(os.path.join(tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    o = UAR._oracle_ak(fx, b, sum(fx.ksrc_b0.values()), fx.ksrc_b0)
    fx.reg["ak_identity"] = dict(d_u="%+.4f" % o["d_u"], d_us="%+.4f" % o["d_us"], spread_u="%.4f" % o["spread_u"], spread_us="%.4f" % o["spread_us"])
    UAR._fx_vdc_plain(fx)
    lines, err = UAR._capture(UAR.run, fx)
    if err:
        raise AssertionError("fixture union_af_route --run refused: %s" % err)
    lay = _Lay()
    lay.fx, lay.proto, lay.graft, lay.tmp = fx, proto, graft, tmp
    lay.uar_out = open(os.path.join(tmp, "res", "outcome.txt"), encoding="utf-8").read()
    pol_p = os.path.join(tmp, "res", "scratch", "pol.json")
    lay.reg = dict(REG, out="res/erc/outcome.txt", marker="res/erc/READ_STARTED", uar_policy_sha=sha256_bytes(pol_p),
                   uar_outcome_sha=hashlib.sha256(lay.uar_out.encode("utf-8")).hexdigest(), n_route=fx.reg["n_route"],
                   comp_route=fx.reg["comp_route"], identity=_uar_identity(lay.uar_out), B=int(fx.spec["reg"]["B"]),
                   seed=int(fx.spec["reg"]["seed"]), agree_min=0.95)
    return lay


def _clone(lay, dest):
    """A fresh copy of the layout (the views are rebuilt per cfg by the factory, under dest)."""
    import copy
    import shutil
    shutil.copytree(lay.tmp, dest)
    new = copy.copy(lay)
    fx = copy.copy(lay.fx)
    fx.tmp = dest
    k = [0]

    def factory():
        k[0] += 1
        return V._fixture_cfg(dest, fx.spec, "erc_%d" % k[0])
    fx.cfg_factory = factory
    new.fx, new.tmp, new.reg = fx, dest, dict(lay.reg)
    return new


@contextlib.contextmanager
def _mine(lay, **over):
    saved = _REG[0]
    _REG[0] = dict(lay.reg, **over)
    try:
        with UAR._patched(lay.fx):
            yield
    finally:
        _REG[0] = saved


def _cap(fn, lay, **over):
    buf = io.StringIO()
    with _mine(lay, **over):
        with contextlib.redirect_stdout(buf):
            try:
                res = fn(out=lambda s: print(s, flush=True))
                err = None
            except SystemExit as e:
                res, err = None, str(e)
    return buf.getvalue(), err, res


def _need(text, *needles):
    for n in needles:
        if n not in text:
            raise AssertionError("missing %r" % n[:200])


# ── the independent oracle (plain loops; numpy only for dot products, the k-means call and the unit draws) ─────────────

def _o_key(spec):
    mu = sorted(spec["models_u"])
    vals = defaultdict(list)
    for r in spec["responses"]:
        if r["cv"] != "mc6" or r["side"] == "GATE":
            continue
        vals[(r["item"], r["model"])].append(r["mf"] if r["mf"] is not None else r["c"])
    val = {k: v[0] for k, v in vals.items() if len(v) == 1}
    return mu, val


def _o_pct(xs, q):
    s = sorted(xs)
    pos = q / 100.0 * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo) if hi != lo else s[lo]


def _o_scores(x, cands):
    sims = sorted(((float(np.dot(x, cv)), j) for j, cv in cands), key=lambda t: -t[0])
    m = sims[0][0] - sims[1][0] if len(sims) > 1 else float("inf")
    return m, sims[0][0], sims[0][1], (sims[1][1] if len(sims) > 1 else None)


def _o_csv(path):
    import csv
    return list(csv.DictReader(open(path, encoding="utf-8")))


def _oracle(lay, D):
    """Everything the outcome prints, recomputed from the fixture's raw rows and prototypes by plain loops."""
    fx, c = lay.fx, lay.reg
    tmp = lay.tmp
    mu, val = _o_key(fx.spec)
    man = json.load(open(os.path.join(tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    k0, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "k_cells_s0.tsv"), man["inputs"]["res/inputs/k_cells_s0.tsv"])
    z = np.load(os.path.join(tmp, "res", "inputs", "af_u_bundle_256.npz"))
    titems = [str(x) for x in z["train_item"]]
    classes = [str(x) for x in z["classes"]]
    single_cell = sorted(v for v in set(af.values()) if v.startswith(fx.single + ":"))
    assert len(single_cell) == 1
    sc_ = single_cell[0]
    acc = np.zeros(UAR.FX_DIM)
    for j, it in enumerate(titems):
        if af.get(it) == sc_:
            acc += z["train_X"][j] / np.linalg.norm(z["train_X"][j])
    af_cent = [(lf, lay.proto[lf]) for lf in lay.graft] + [(sc_, acc / np.linalg.norm(acc))]
    Xt = np.asarray(z["train_X"], float)
    Xt = Xt / np.linalg.norm(Xt, axis=1, keepdims=True)
    tsrc = [UAR.src_of(classes[int(y)]) for y in z["train_y"]]
    k_cent = []
    for so in fx.reg["sources"]:
        idx = [i for i in range(len(tsrc)) if tsrc[i] == so]
        r = GC.FM.spherical_kmeans(Xt[idx], fx.ksrc[so], 0, max_iter=300)
        for j in range(fx.ksrc[so]):
            k_cent.append(("K0:%s:%03d" % (so, j), so, r["centers"][j]))
    vm = os.path.join(tmp, "res", "inputs", "validation_merged")
    srcs = defaultdict(set)
    rows_h = _o_csv(os.path.join(vm, "MAIN_union_routing_queries.csv"))
    for row in rows_h + _o_csv(os.path.join(vm, "MAIN_union_routing_train_queries.csv")):
        srcs[row["item_id"]].add(row["true_key"].split("/")[0])
    side = fx.side

    def cands(it, arm, cell):
        if arm == "AF":
            return [(sc_, af_cent[-1][1])] if cell == sc_ else [(lf, v) for lf, v in af_cent[:-1]]
        return [(nm, v) for nm, so, v in k_cent if so in srcs[it]]
    gcell = {}
    for row in rows_h:
        if side[row["item_id"]][1] == "GATE":
            assert row["item_id"] not in gcell, "a GATE item with two rows in the fixture"
            gcell[row["item_id"]] = row["leaf_id"]
    gate = sorted(gcell)
    th = {}
    for arm in ("AF", "K"):
        ms, os_ = [], []
        for it in gate:
            m, o, _t1, _t2 = _o_scores(fx.vec[it], cands(it, arm, gcell[it]))
            ms.append(m)
            os_.append(o)
        th[arm] = (_o_pct(ms, c["q_margin"]), _o_pct(os_, c["q_oos"]))
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]

    def fit_w(w):
        tot = {m: sum(w[i] * val[(i, m)] for i in tr) for m in mu}
        best = max(mu, key=lambda m: (tot[m], -mu.index(m)))
        pols = {}
        for arm, cells in (("AF", af), ("K", k0)):
            per = defaultdict(lambda: defaultdict(float))
            mass = defaultdict(float)
            for i in tr:
                if w[i]:
                    mass[cells[i]] += w[i]
                    for m in mu:
                        per[cells[i]][m] += w[i] * val[(i, m)]
            pols[arm] = {k_: max(mu, key=lambda m: (d_[m], -mu.index(m))) for k_, d_ in per.items() if mass[k_] >= 1}
        return best, pols
    sco = {arm: {} for arm in ("AF", "K")}
    for it in ev:
        for arm, cells in (("AF", af), ("K", k0)):
            sco[arm][it] = _o_scores(fx.vec[it], cands(it, arm, cells[it]))
    flags = {arm: {it: (sco[arm][it][0] < th[arm][0]) or (sco[arm][it][1] < th[arm][1]) for it in ev} for arm in ("AF", "K")}

    def de(best, pols, wv):
        out = {}
        tot = sum(wv[i] for i in ev)
        for arm, cells in (("AF", af), ("K", k0)):
            cc = {i: val[(i, pols[arm].get(cells[i], best))] for i in ev}
            cb = {i: val[(i, best)] for i in ev}
            e = sum(wv[i] for i in ev if flags[arm][i]) / tot
            a_c = sum(wv[i] * cc[i] for i in ev) / tot
            a_b = sum(wv[i] * cb[i] for i in ev) / tot
            a_r = sum(wv[i] * (cb[i] if flags[arm][i] else cc[i]) for i in ev) / tot
            out[arm] = dict(e=e, acc_cell=a_c, acc_best=a_b, acc_rule=a_r, d_e=a_r - ((1 - e) * a_c + e * a_b), cc=cc, cb=cb)
        return out
    best0, pol0 = fit_w({i: 1 for i in tr})
    pt = de(best0, pol0, {i: 1 for i in ev})
    rng = np.random.default_rng(c["seed"])
    two = {"AF": [], "K": []}
    for _b in range(c["B"]):
        wt = V.draw_units(rng, D.train_units)
        w = {D.items[D.T[j]]: int(wt[j]) for j in range(len(D.T))}
        vv = V.draw_units(rng, D.eval_units)
        wv = {D.items[D.E[j]]: float(vv[j]) for j in range(len(D.E))}
        best, pols = fit_w(w)
        r_ = de(best, pols, wv)
        for arm in two:
            two[arm].append(r_[arm]["d_e"])
    rng = np.random.default_rng(c["seed"])
    iid = {"AF": [], "K": []}
    NE = len(ev)
    for _b in range(c["B"]):
        cnt = np.bincount(rng.integers(0, NE, NE), minlength=NE)
        r_ = de(best0, pol0, {D.items[D.E[j]]: float(cnt[j]) for j in range(NE)})
        for arm in iid:
            iid[arm].append(r_[arm]["d_e"])

    def sd(xs):
        mbar = sum(xs) / len(xs)
        return math.sqrt(sum((x - mbar) ** 2 for x in xs) / (len(xs) - 1))
    res = dict(th=th, pt=pt, flags=flags, sco=sco)
    for arm in ("AF", "K"):
        s2 = sd(two[arm])
        res[arm] = dict(point=pt[arm]["d_e"], lo=pt[arm]["d_e"] - 1.96 * s2, hi=pt[arm]["d_e"] + 1.96 * s2, se2=s2, se_iid=sd(iid[arm]))
    dd = [a - b for a, b in zip(two["AF"], two["K"])]
    dpt = pt["AF"]["d_e"] - pt["K"]["d_e"]
    res["diff"] = dict(point=dpt, lo=dpt - 1.96 * sd(dd), hi=dpt + 1.96 * sd(dd))
    cm = {}
    for it in ev:
        m, o, t1, t2 = sco["AF"][it]
        p1 = pol0["AF"].get(t1, best0)
        cm[it] = int(t2 is not None and p1 != pol0["AF"].get(t2, best0))
    res["frag_rate"] = sum(cm.values()) / len(ev)
    pos = {it: j for j, it in enumerate(ev)}
    keys = dict(margin=lambda it: (-sco["AF"][it][0], pos[it]), oos=lambda it: (-sco["AF"][it][1], pos[it]),
                fragility=lambda it: (cm[it], -sco["AF"][it][0], pos[it]))
    res["curve"] = {}
    for nm, kf in keys.items():
        srt = sorted(ev, key=kf)
        for c_ in (0.5, 0.8):
            keep = set(srt[:int(round(c_ * len(ev)))])
            res["curve"][(nm, c_)] = sum(pt["AF"]["cc"][i] if i in keep else pt["AF"]["cb"][i] for i in ev) / len(ev)
    res["n_esc"] = sum(flags["AF"].values())
    res["n_single_ev"] = sum(1 for it in ev if af[it] == sc_)
    return res


# ── cases ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _syn(point=0.004, lo=0.001, hi=0.007, e=0.25, dk=0.001, dlo=-0.002, dhi=0.004):
    def arm(pt_, lo_, hi_, e_):
        return dict(point=pt_, lo=lo_, hi=hi_, pct=(lo_, hi_), se2=0.002, se_iid=0.0015, deff=1.7, n_eff=3000.0, mde=0.0056, n=5907,
                    e=e_, n_esc=10, n_m=5, n_o=3, n_mo=2, acc_cell=0.62, acc_best=0.60, acc_rule=0.62, frag=0.1, frag_esc=0.2,
                    frag_kept=0.05, gap_esc=-0.01)
    st = {"AF-U": arm(point, lo, hi, e), "K_0": arm(dk, -0.003, 0.005, 0.24), "comp": 5404, "n_train": 11841, "n_gate": 2033,
          "diff": dict(point=point - dk, lo=dlo, hi=dhi, pct=(dlo, dhi))}
    st["curves"] = {a: {k: [0.6] * len(GRID) for k in ("margin", "oos", "fragility", "random")} for a in ARMS}
    return st


def st_branches():
    cases = [((0.004, 0.001, 0.007), "HELD"), ((-0.004, -0.007, -0.001), "FAILED"), ((0.001, -0.002, 0.004), "UNDETERMINED"),
             ((0.003, 0.0, 0.006), "UNDETERMINED"), ((-0.003, -0.006, 0.0), "UNDETERMINED"), ((0.003, 1e-12, 0.006), "HELD"),
             ((-0.003, -0.006, -1e-12), "FAILED")]
    for (p_, l_, h_), want in cases:
        L, w = rc_lines(_syn(p_, l_, h_))
        t = "\n".join(L)
        assert w["RC1"] == want, (p_, l_, h_, w)
        _need(t, "  RC1 -> %s" % want, "verdict line of record: " + VERDICT_LINE, "D_E = acc(rule on AF-U) - [(1 - e) acc(AF-U policy) + e acc(best single)] = %+.5f |"
              " two-stage 95%% [%+.5f, %+.5f]" % (p_, l_, h_), "PREDICTION P1 RC1 HELD 0.25, UNDETERMINED 0.70, FAILED 0.05: observed %s; Brier %.4f"
              % (want, {"HELD": 1.055, "UNDETERMINED": 0.155, "FAILED": 1.455}[want]), "WILL NOT SHOW (registered)", COND_TEXT,
              "DENOMINATOR: 5907 EVAL items in 5404 components", "support RC1: n 5907")
        if want == "FAILED":
            assert w["F_RC"] is True
            _need(t, "FALSIFIER F-RC: FIRED (RC1 FAILED)")
            assert "NOT FIRED" not in t
        else:
            assert w["F_RC"] is False
            _need(t, "FALSIFIER F-RC: NOT FIRED (RC1 %s; F-RC fires iff RC1 FAILED)" % want)
    for e_, want in ((0.15, "HELD"), (0.35, "HELD"), (0.1499, "FAILED"), (0.3501, "FAILED"), (0.25, "HELD")):
        t = "\n".join(rc_lines(_syn(e=e_))[0])
        _need(t, "PREDICTION P1 e 0.25 [0.15, 0.35]: observed %.5f -> %s" % (e_, want))
    for d_, want in ((-0.003, "HELD"), (0.010, "HELD"), (-0.0031, "FAILED"), (0.0101, "FAILED")):
        t = "\n".join(rc_lines(_syn(point=d_, lo=d_ - 0.003, hi=d_ + 0.003))[0])
        _need(t, "PREDICTION P1 D_E +0.003 [-0.003, +0.010]: observed %+.5f -> %s" % (d_, want))
    for dk, want in ((-0.002, "HELD"), (0.010, "HELD"), (-0.0021, "FAILED"), (0.0101, "FAILED")):
        t = "\n".join(rc_lines(_syn(dk=dk))[0])
        _need(t, "PREDICTION P2 D_E(AF-U) - D_E(K_0) 0.000 [-0.006, +0.006] (descriptive): observed %+.5f -> %s" % (0.004 - dk, want))
    t = "\n".join(rc_lines(_syn())[0])
    assert t.count("RISK-COVERAGE") == 2 and t.count("    1.00       ") == 2 and t.count("    0.00       ") == 2
    _need(t, "DESCRIPTIVE: D_E(K_0) = +0.00100", "DESCRIPTIVE: D_E(AF-U) - D_E(K_0) = +0.00300 | two-stage 95% [-0.00200, +0.00400]",
          "  AF-U: e = 0.25000 (escalated 10 of 5907: margin only 5, OOS only 3, both 2)")
    assert abs(brier("HELD") - 1.055) < 1e-12 and abs(brier("UNDETERMINED") - 0.155) < 1e-12 and abs(brier("FAILED") - 1.455) < 1e-12


def st_units():
    rs = np.random.RandomState(3)
    C = GC.FM.unit_rows(rs.normal(size=(6, 5)))
    X = GC.FM.unit_rows(rs.normal(size=(40, 5)))
    cands = [(0, 1, 2) if i % 3 == 0 else (4,) if i % 3 == 1 else (1, 3, 4, 5) for i in range(40)]
    m, o, t1, t2 = cand_scores(X, cands, C)
    for i in range(40):
        om, oo, ot1, ot2 = _o_scores(X[i], [(j, C[j]) for j in cands[i]])
        assert (m[i] == om) if math.isinf(om) else abs(m[i] - om) < 1e-12, (i, m[i], om)
        assert abs(o[i] - oo) < 1e-12 and t1[i] == ot1 and (t2[i] == -1 if ot2 is None else t2[i] == ot2), i
    assert np.isinf(m[1::3]).all() and (t2[1::3] == -1).all()
    saved = _REG[0]
    try:
        _REG[0] = dict(REG)
        xs = list(rs.normal(size=37))
        ys = list(rs.normal(size=37))
        tm, to = thresholds(np.array(xs), np.array(ys))
        assert abs(tm - _o_pct(xs, 20)) < 1e-12 and abs(to - _o_pct(ys, 5)) < 1e-12
        try:
            thresholds(np.array([np.inf] * 5), np.array(ys[:5]))
            raise AssertionError("an infinite threshold was not refused")
        except SystemExit as e:
            assert "not finite" in str(e)
    finally:
        _REG[0] = saved
    f = escalate(np.array([0.1, 0.2, 0.3, 0.2, np.inf]), np.array([0.9, 0.9, 0.5, 0.4, 0.4]), 0.2, 0.5)
    assert f.tolist() == [True, False, False, True, True], f
    fr = fragility(np.array([0, 1, 2, 3]), np.array([1, -1, 3, 0]), np.array([5, 5, 6, 7]))
    assert fr.tolist() == [False, False, True, True]
    cc = np.array([1, 0, 1, 1, 0], float)
    cb = np.array([0, 1, 1, 0, 1], float)
    fl = np.array([False, True, False, False, True])
    v = np.array([1, 2, 0, 1, 3], float)
    s = esc_stats(cc, cb, fl, v)
    assert abs(s["acc_cell"] - 2 / 7) < 1e-12 and abs(s["acc_best"] - 5 / 7) < 1e-12 and abs(s["acc_rule"] - 7 / 7) < 1e-12, s
    assert abs(s["e"] - 5 / 7) < 1e-12 and abs(s["d_e"] - (7 / 7 - (2 / 7 * 2 / 7 + 5 / 7 * 5 / 7))) < 1e-12
    od = orders(np.array([0.3, 0.1, 0.3, np.inf]), np.array([0.5, 0.9, 0.2, 0.1]), np.array([True, False, False, False]))
    assert od["margin"].tolist() == [3, 0, 2, 1] and od["oos"].tolist() == [1, 0, 2, 3] and od["fragility"].tolist() == [3, 2, 1, 0], od
    cc4, cb4 = np.array([1, 0, 1, 0], float), np.array([0, 1, 0, 1], float)
    cur = rc_curve(cc4, cb4, np.array([2, 0, 1, 3]), grid=(1.0, 0.5, 0.25, 0.0))
    assert cur == [0.5, 1.0, 0.75, 0.5], cur
    two = rs.normal(0.01, 0.003, 200)
    iid = rs.normal(0.01, 0.002, 200)
    it = interval(0.01, two, iid, 1000)
    sd2 = float(np.std(two, ddof=1))
    assert abs(it["lo"] - (0.01 - 1.96 * sd2)) < 1e-12 and abs(it["hi"] - (0.01 + 1.96 * sd2)) < 1e-12
    assert abs(it["deff"] - (sd2 ** 2 / float(np.var(iid, ddof=1)))) < 1e-12 and abs(it["mde"] - 2.8 * sd2) < 1e-12
    assert abs(it["n_eff"] - 1000 / it["deff"]) < 1e-9
    assert _pre_root(["--run", "--data-root", "Z:/x"]) == "Z:/x" and _pre_root(["--data-root=Y", "--dry-run"]) == "Y" and _pre_root(["--run"]) is None


def _num(text, pat):
    m = re.search(pat, text)
    if not m:
        raise AssertionError("no line %r" % pat)
    return [float(x) for x in m.groups()]


def st_run_e2e(base, mk):
    lay = _clone(base, mk())
    text, err, res = _cap(run, lay)
    assert err is None, err
    out = open(os.path.join(lay.tmp, "res", "erc", "outcome.txt"), encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (ESCALATION-RC; --run" % POOL)
    assert os.path.isfile(os.path.join(lay.tmp, "res", "erc", "READ_STARTED"))
    o = _oracle(lay, res["D"])
    assert o["n_single_ev"] > 0, "the fixture scores no one-cell EVAL item"
    for arm, k in (("AF-U", "AF"), ("K_0", "K")):
        tm, to = _num(out, r"GATE THRESHOLDS %s\s+\(R5; n GATE \d+\): tau_m = p20 of margin = ([0-9.]+) \| tau_oos = p5 of OOS = ([0-9.]+)" % re.escape(arm))
        assert abs(tm - o["th"][k][0]) < 6e-7 and abs(to - o["th"][k][1]) < 6e-7, (arm, tm, to, o["th"][k])
        e_, = _num(out, r"  %s: e = ([0-9.]+) \(escalated" % re.escape(arm))
        assert abs(e_ - o["pt"][k]["e"]) < 6e-6, (arm, e_, o["pt"][k]["e"])
    assert 0 < o["n_esc"] < len(res["D"].E), o["n_esc"]
    p_, lo, hi = _num(out, r"RC1 \(DECIDING; the INTERVAL decides\): D_E = .*? = ([+-][0-9.]+) \| two-stage 95% \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    assert abs(p_ - o["AF"]["point"]) < 6e-6 and abs(lo - o["AF"]["lo"]) < 6e-6 and abs(hi - o["AF"]["hi"]) < 6e-6, (p_, lo, hi, o["AF"])
    assert abs(o["AF"]["point"]) > 1e-4, "the fixture's D_E is ~0: the readout would not discriminate"
    se2, sei = _num(out, r"support RC1: n \d+, SE_2stage ([0-9.]+) \(registered 0.00367\), i.i.d. SE ([0-9.]+)")
    assert abs(se2 - o["AF"]["se2"]) < 6e-6 and abs(sei - o["AF"]["se_iid"]) < 6e-6
    kp, klo, khi = _num(out, r"DESCRIPTIVE: D_E\(K_0\) = ([+-][0-9.]+) \| two-stage 95% \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    assert abs(kp - o["K"]["point"]) < 6e-6 and abs(klo - o["K"]["lo"]) < 6e-6 and abs(khi - o["K"]["hi"]) < 6e-6
    assert abs(o["AF"]["point"] - o["K"]["point"]) > 1e-4, "AF-U and K_0 agree on the fixture: the arms would not discriminate"
    dp, dlo, dhi = _num(out, r"DESCRIPTIVE: D_E\(AF-U\) - D_E\(K_0\) = ([+-][0-9.]+) \| two-stage 95% \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    assert abs(dp - o["diff"]["point"]) < 6e-6 and abs(dlo - o["diff"]["lo"]) < 6e-6 and abs(dhi - o["diff"]["hi"]) < 6e-6
    fr, = _num(out, r"  AF-U: e = .*?decision fragility rate ([0-9.]+) ")
    assert abs(fr - o["frag_rate"]) < 6e-6 and 0 < o["frag_rate"] < 1, (fr, o["frag_rate"])
    want = "HELD" if lo > 0 else "FAILED" if hi < 0 else "UNDETERMINED"
    _need(out, "  RC1 -> %s" % want, "FALSIFIER F-RC: %s" % ("FIRED" if want == "FAILED" else "NOT FIRED"))
    _need(out, "PREDICTION P1 e 0.25 [0.15, 0.35]: observed %.5f -> %s" % (o["pt"]["AF"]["e"], "HELD" if 0.15 <= o["pt"]["AF"]["e"] <= 0.35 else "FAILED"))
    blk = out.split("RISK-COVERAGE AF-U")[1].split("RISK-COVERAGE K_0")[0]
    for c_ in (0.5, 0.8):
        vals = _num(blk, r"\n    %.2f       ([0-9.]+)   ([0-9.]+)   ([0-9.]+)   ([0-9.]+)" % c_)
        for j, nm in enumerate(("margin", "oos", "fragility")):
            assert abs(vals[j] - o["curve"][(nm, c_)]) < 6e-6, (c_, nm, vals[j], o["curve"][(nm, c_)])
    idn = lay.reg["identity"]
    _need(out, "IDENTITY (R12): best single %s, AF-U leaf cell %s, K_s K0 %s, G_AF %s [%s, %s]" % ((idn["best"], idn["af"], idn["k0"]) + tuple(idn["g_af"])),
          "R4 K_0 re-filing: 0 of", "B3: the point policy re-fitted beside EVAL equals the frozen file",
          "frozen TRAIN policy res/scratch/pol.json sha256 %s" % lay.reg["uar_policy_sha"])
    ag, n_ = _num(out, r"R4 AF filing agreement: argmax over the candidates = the AF cell of record on (\d+) of (\d+)")
    assert ag == n_ - 1, (ag, n_)
    t2, err2, _r = _cap(run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(os.path.join(lay.tmp, "res", "erc", "outcome.txt"), encoding="utf-8").read() == out


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "erc", "outcome.txt")), "an outcome was written by a refusal"


def st_refusals(base, mk):
    lay = _clone(base, mk())
    saved = UAR._POOL[0]
    buf = io.StringIO()
    with _mine(lay):
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
    _t, err, _r = _cap(run, lay, uar_policy_sha="0" * 64)
    assert err and "not the registered" in err, err
    _no_outcome(lay)
    _t, err, _r = _cap(run, lay, agree_min=1.0)
    assert err and "R4: AF filing agreement" in err, err
    _no_outcome(lay)
    real = UAR.us_fit

    def swapped(*a, **k):
        C, csrc, cloc, lab, f = real(*a, **k)
        j = [i for i in range(len(csrc)) if csrc[i] == "MMLU_PRO"][:2]
        C = C.copy()
        C[[j[0], j[1]]] = C[[j[1], j[0]]]
        return C, csrc, cloc, lab, f
    UAR.us_fit = swapped
    try:
        _t, err, _r = _cap(run, lay)
    finally:
        UAR.us_fit = real
    assert err and "K_0 re-filed differs" in err, err
    _no_outcome(lay)
    mk_path = os.path.join(lay.tmp, "res", "erc", "READ_STARTED")
    assert not os.path.exists(mk_path), "a pre-read refusal wrote the marker"
    _t, err, _r = _cap(run, lay, n_route=lay.reg["n_route"] + 1)
    assert err and "[ERC-DENOM]" in err, err
    _no_outcome(lay)
    assert os.path.exists(mk_path)
    os.remove(mk_path)
    g0 = lay.reg["identity"]["g_af"]
    for over in (dict(identity=dict(lay.reg["identity"], af="0.0001")), dict(identity=dict(lay.reg["identity"], g_af=(g0[0], g0[1], "+99.99pp")))):
        t_, err, _r = _cap(run, lay, **over)
        assert err and "[ERC-IDENTITY]" in err, err
        assert "RC1 (DECIDING" not in t_ and "D_E =" not in t_, "a new number was printed before the identity check"
        _no_outcome(lay)
        os.remove(mk_path)
    real_rb = V.run_boot

    def skewed(*a, **k):
        bt_ = real_rb(*a, **k)
        bt_["two"][:, 0, V.TREE] += 1e-6
        return bt_
    V.run_boot = skewed
    try:
        _t, err, _r = _cap(run, lay)
    finally:
        V.run_boot = real_rb
    assert err and "[ERC-HOOK]" in err, err
    _no_outcome(lay)
    os.remove(mk_path)
    real_gi = gate_items
    globals()["gate_items"] = lambda rows_h, side: ([], {}, {})
    try:
        _t, err, _r = _cap(run, lay)
    finally:
        globals()["gate_items"] = real_gi
    assert err and "no GATE item" in err, err
    _no_outcome(lay)
    open(mk_path, "w").close()
    _t, err, _r = _cap(run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)
    os.remove(mk_path)
    pol_p = os.path.join(lay.tmp, "res", "scratch", "pol.json")
    pol = json.load(open(pol_p, encoding="utf-8"))
    k_ = sorted(x for x in pol["tree_cell"] if pol["tree_cell"][x])[0]
    pol["tree_cell"][k_] = [m for m in pol["roster"] if m != pol["tree_cell"][k_]][0]
    with open(pol_p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(pol, sort_keys=True, indent=1) + "\n")
    _t, err, _r = _cap(run, lay, uar_policy_sha=sha256_bytes(pol_p))
    assert err and "[B3]" in err, err
    _no_outcome(lay)


def st_dry_run(base, mk):
    lay = _clone(base, mk())
    text, err, _r = _cap(dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (ESCALATION-RC; --dry-run" % POOL), ls[0]
    _need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no EVAL key read", "GATE THRESHOLDS AF-U", "GATE THRESHOLDS K_0",
          "R4 K_0 re-filing: 0 of", "GEOMETRY (R2): AF 5 graft leaves (vmfMu, sliceDim 8) + 1 one-cell centroid(s) BBH:")
    for bad in ("RC1 (DECIDING", "D_E =", "IDENTITY (R12)", "RISK-COVERAGE", "PREDICTION"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "erc")), "the dry-run wrote under res/erc"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        header(L.append, "--dry-run")
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (ESCALATION-RC; --dry-run"), L[0]
    _need(t, "5907 EVAL items in 5404 components", "DEFF 1.595", "n_eff 3,704", "SE 0.00367", "MDE80 0.0103", VERDICT_LINE,
          "B = 2000 two-stage replicates (default_rng(42))", "tau_m = GATE p20 of margin, tau_oos = GATE p5 of OOS (TPR 0.95)",
          "R4 agreement floor 0.999", "K_0 = K0 (us_fit seed 0)",
          "best single 0.6049, AF-U leaf cell 0.6201, K_s K0 0.6271, G_AF +1.52pp [+0.14pp, +2.91pp]", "e50a8e0fa267db96", "L23960-L23973",
          "OT1 EQUIVALENT", "calls 0")
    assert REG["uar_policy_sha"].startswith("8d68018c") and REG["out"] == "experiment_results/archv2/escalation_rc/outcome.txt"


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "RC1 HELD / FAILED / UNDETERMINED incl. end points at 0, F-RC, P1 / P2 bands inclusive, Brier, required lines", "plain"),
         ("units", "cand_scores vs loops (one candidate: inf), percentile thresholds, strict escalation, fragility, esc_stats, orders, rc_curve, interval", "plain"),
         ("run_e2e", "--run end to end (one-cell member): thresholds, e, D_E and interval, K_0, diff, fragility, curves vs an independent oracle; verdict by hand; write-once", "base"),
         ("refusals", "pool check, policy sha, R4 agreement, K_0 re-filing, DENOM, IDENTITY (arm / one end), ERC-HOOK, GATE empty, marker exists, B3; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, no EVAL statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "units": st_units, "run_e2e": st_run_e2e, "refusals": st_refusals, "dry_run": st_dry_run,
       "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def mk():
        d = tempfile.mkdtemp(prefix="erc_")
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
                        base = _build_layout(mk())
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(base, mk)
                if not quiet:
                    print("  ok   %-13s %s" % (name, desc), flush=True)
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    import traceback
                    print("  FAIL %-13s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:400]), flush=True)
                    traceback.print_exc()
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "", ""),
    ("X01 RC1 HELD at lo >= 0 (boundary)", 'if st["lo"] > 0:', 'if st["lo"] >= 0:'),
    ("X02 RC1 FAILED at hi <= 0 (boundary)", 'if st["hi"] < 0:', 'if st["hi"] <= 0:'),
    ("X03 F-RC fires on any non-HELD", '    if v == "FAILED":' + NL + '        hit("FRC.FIRED")', '    if v != "HELD":' + NL + '        hit("FRC.FIRED")'),
    ("X04 rule margin AND OOS", "return (m < tm) | (o < to)", "return (m < tm) & (o < to)"),
    ("X05 rule non-strict <=", "return (m < tm) | (o < to)", "return (m <= tm) | (o <= to)"),
    ("X06 thresholds on EVAL (wrong split side)", 'side.get(i, (None, None))[1] == "GATE")', 'side.get(i, (None, None))[1] == "EVAL")'),
    ("X07 percentiles swapped (q_oos for margin)", 'np.percentile(m_gate, c["q_margin"])), float(np.percentile(o_gate, c["q_oos"]))',
     'np.percentile(m_gate, c["q_oos"])), float(np.percentile(o_gate, c["q_margin"]))'),
    ("X08 OOS min over candidates (min<->max)", "o[idx] = OB.maxcos(Cc, Xi)", "o[idx] = (Xi @ Cc.T).min(1)"),
    ("X09 AF candidates = first leaf only (first-site-only)", "    return g.graft_idx" + NL, "    return g.graft_idx[:1]" + NL),
    ("X10 one-cell items searched among the graft leaves (R3)", "    if cell in g.single_cells:", "    if False and cell in g.single_cells:"),
    ("X11 K_0 candidates = all centroids (no source filing)", "np.isin(g.k_src, list(srcs))", "np.isin(g.k_src, list(g.k_src))"),
    ("X12 D_E baseline without the e term", "d_e=a_rule - ((1.0 - e) * a_cell + e * a_best)", "d_e=a_rule - a_cell"),
    ("X13 e unweighted (denominator changed)", "e = float(v @ f.astype(np.float64)) / tot", "e = float(f.mean())"),
    ("X14 interval z 1.645", "lo=pt - 1.96 * se2, hi=pt + 1.96 * se2", "lo=pt - 1.645 * se2, hi=pt + 1.645 * se2"),
    ("X15 interval from the i.i.d. SE", "    v2, vi = V._var(two), V._var(iid)", "    v2, vi = V._var(iid), V._var(iid)"),
    ("X16 diff not paired (AF replicates only)", "two[:, 0] - two[:, 1], iid[:, 0] - iid[:, 1], NE)", "two[:, 0], iid[:, 0] - iid[:, 1], NE)"),
    ("X17 replicate policy not re-fitted (P0 reused)", "        Pp = V.fit(D_, wt)", "        Pp = V.fit(D_, V.train_full(D_))"),
    ("X18 identity: arm digits not compared", 'if any(got[k] != idn[k] for k in ("best", "af", "k0")) or', 'if False and any(got[k] != idn[k] for k in ("best", "af", "k0")) or'),
    ("X19 identity on the arms only (G_AF interval not compared)", ' or got_g != tuple(idn["g_af"]):', ':'),
    ("X20 denominator check skipped", 'if (D.n_eval, n_comp) != (c["n_route"], c["comp_route"]):', 'if False:'),
    ("X21 B3 frozen-policy refusal removed", '        refuse("[B3] the point policy', '        pass  # refuse("[B3] the point policy'),
    ("X22 marker not written before the read", '    G.read_marker(P(reg()["marker"]), marker_text)' + NL, '    pass' + NL),
    ("X23 ERC-HOOK check skipped", 'if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):', 'if False:'),
    ("X24 fragility: fragile kept first", "fragility=np.lexsort((pos, -m, frag.astype(int)))", "fragility=np.lexsort((pos, -m, -frag.astype(int)))"),
    ("X25 risk-coverage keeps the least confident", "        keep[order[:k]] = True", "        keep[order[len(order) - k:]] = True"),
    ("X26 fragility compares top-1 with itself", "f[two] = cell_model[t1[two]] != cell_model[t2[two]]", "f[two] = cell_model[t1[two]] != cell_model[t1[two]]"),
    ("X27 K_0 read with the AF-U thresholds (wrong arm)", '        tm, to = S["th"][arm]', '        tm, to = S["th"]["AF-U"]'),
    ("X28 prediction bands exclusive", "    return bool(band[0] <= x <= band[1])", "    return bool(band[0] < x < band[1])"),
    ("X29 P2 read against P1's band", 'ok = in_band(d["point"], PRED_DIFF)', 'ok = in_band(d["point"], PRED_DE)'),
    ("X30 verdict line of record dropped", "MDE80 %.5f (registered 0.0103); verdict line of record: %s", "MDE80 %.5f (registered 0.0103); %s"),
    ("X31 F-RC NOT FIRED line dropped (skip path)", '        say("FALSIFIER F-RC: NOT FIRED (RC1 %s; F-RC fires iff RC1 FAILED)" % v)', '        pass'),
    ("X32 i.i.d. replicates on another seed", '    rng = np.random.default_rng(c["seed"])' + NL + '    NE = len(D.E)', '    rng = np.random.default_rng(c["seed"] + 1)' + NL + '    NE = len(D.E)'),
    ("X33 pool check ignored", '    if rc != 0:' + NL + '        hit("REFUSE.POOL")', '    if rc < 0:' + NL + '        hit("REFUSE.POOL")'),
    ("X34 frozen policy sha not checked", 'if sh != reg()["uar_policy_sha"]:', 'if False:'),
    ("X35 one-cell centroid = its first TRAIN item", "        mu = Xt[rows].mean(axis=0)", "        mu = Xt[rows[0]]"),
    ("X36 R4 agreement floor not enforced", 'if share < c["agree_min"]:', 'if share < 0:'),
    ("X37 OOS = second-nearest cos", "o[idx] = OB.maxcos(Cc, Xi)", "o[idx] = np.sort(Xi @ Cc.T, axis=1)[:, -2] if len(cs) > 1 else OB.maxcos(Cc, Xi)"),
    ("X38 GATE-empty guard removed", '    if not its:' + NL + '        hit("REFUSE.GATE_EMPTY")', '    if False:' + NL + '        hit("REFUSE.GATE_EMPTY")'),
    ("X39 pre-read write-once check removed", '        if os.path.exists(P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X40 K_0 re-filing check skipped", '        if sc["kdiff"]:', '        if False:'),
)


def run_mutants(only=None):
    """Each mutant edits THIS file's code above the SELFTEST section in memory, executes the edited module and runs its selftest on
    one fixture layout built by the unedited code; KILLED iff the selftest fails. The control X00 must survive."""
    import types
    import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(NL + "# " + chr(0x2550) * 2 + " SELFTEST")
    head, tail = src[:cut], src[cut:]
    d = tempfile.mkdtemp(prefix="erc_mut_")
    rows, bad = [], []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            base = _build_layout(os.path.join(d, "lay"))
        for name, old, new in MUTANTS:
            if only and not any(name.startswith(o) for o in only):
                continue
            if old and head.count(old) != 1:
                bad.append(name)
                rows.append((name, "NOT APPLIED (%d matches)" % head.count(old)))
                continue
            mod = types.ModuleType("escalation_rc_mutant")
            mod.__file__ = os.path.abspath(__file__)
            code = (head.replace(old, new) if old else head) + tail
            try:
                exec(compile(code, mod.__file__, "exec"), mod.__dict__)
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.selftest(quiet=True, base=base)
                res = "SURVIVED"
            except BaseException as e:   # noqa: B902
                res = "KILLED (%s)" % type(e).__name__
            rows.append((name, res))
            print("  %-64s %s" % (name, res), flush=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied %s" % (
        TAG, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


if __name__ == "__main__":
    sys.exit(main())
