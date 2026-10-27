"""escalation_curve.py: ESCALATION-CURVE -- on the union routing data, the full curve of routed accuracy against coverage (the share
kept on the cell policy) when the lowest-margin and OOS items escalate first to the best single model, and the area between that
curve and random escalation (EC1, one deciding area with an interval), AF-U beside k-means. ZERO calls: no judge, no LLM, no
embedding call (cached vectors READ through rp12_pairing's read-only readers), no construction, no Gradle. A CPU reader.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-05 (before any code or call) — ESCALATION-CURVE: on the union routing data, what
  is the full curve of routed accuracy against coverage ..." (L24653-L24665, _as_of the registrar's commit 8e681387, parent
  07bc237f): EC1, Support (a)-(g), P1-P4, F-EC, WILL-NOT-SHOW; record L24618-L24623 (EXPLORATORY LOOKS DISCLOSED). Extends
  ESCALATION-RC (L23960-L23973; outcome sha256 4dad8268...; POSTRUN 482a0ac2 VALID).

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form, or from anywhere with --data-root <main checkout>; never
beside a construction: every step reads the pool):
  0. python tools/analysis/escalation_curve.py --selftest   # synthetic fixtures (temp on E: via scratch_dir); opens NO DB of record
     python tools/analysis/escalation_curve.py --mutants    # the mutant table, re-run (each must make the selftest fail)
  1. python tools/analysis/escalation_curve.py --dry-run    # POOL line first; pins; denominators; B0-2 pool check; inputs re-hashed;
                                                            #   frozen policy sha; geometry; GATE ECDF sizes; the ESCALATION-RC
                                                            #   outcome's sha; NO key, NO statistic; writes nothing
  2. python tools/analysis/escalation_curve.py --run        # TRAIN key, GATE key (c* only), ONE EVAL key read (marker first);
       outcome WRITE-ONCE: experiment_results/archv2/escalation_curve/outcome.txt (+ escalation_curve.READ_STARTED). Never
       committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_escalation_curve with SHA256SUMS.txt.
  Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; write-once paths absent; the ESCALATION-RC outcome present and sha256 = the pin; the B0-2 pool check, AF-U state,
      inputs manifest (53021e26...), AF / K0..K4 cells and the frozen TRAIN policy (8d68018c...) through union_route_common.prepare;
  (2) geometry (escalation_rc.load_geometry: 122 vmfMu graft leaves + the IFEVAL one-cell centroid; K_0 = us_fit seed 0); KM-U:
      g13_breakdown.ukm_fit at k = AF-U's total leaf count (refused unless the registered 123) on the bundle's TRAIN rows, seeds
      0-4; every routed TRAIN / EVAL item filed to its nearest KM-U centroid (cells KU0..KU4);
  (3) GATE (escalation_rc R5 set): scores of every arm -> the GATE ECDFs of margin and OOS per arm;
  (4) EVAL scores before the key (escalation_rc.score_items; R4 AF agreement >= 0.999 and K_0 re-filing EQUAL, refused otherwise);
  (5) union_route_common.read_views with the K0..K4 and KU0..KU4 arms: the TRAIN key; BETWEEN the TRAIN key and the eval view, the
      GATE key from the gen view (response_lite, UNUSABLE_CELL, MATH-FIX overlay; c* only); the marker; THE EVAL KEY READ;
      [ECURVE-DENOM]; [B3] (the frozen file in every arm it carries);
  (6) run_boot (B 2,000, default_rng(42)) with a hook that re-fits every replicate (V.fit: best single, AF, K0, KU0..KU4) and
      traces every curve on the replicate's EVAL weights; [ECURVE-HOOK] (the hook's best / AF / K0 accuracies = run_boot's arms);
  (7) IDENTITY before any new number: UNION-AF-ROUTE's digits (union_route_common.identity) and the PARITY CHECK (registered):
      the margin-only and OOS-only risk-coverage tables of AF-U and K_0 at the 0.05 grid re-traced by escalation_rc's own orders /
      rc_curve on the frozen policy EQUAL to ESCALATION-RC's printed tables (5 dp), else [ECURVE-PARITY];
  (8) EC1, descriptive lines, predictions, F-EC, support; the outcome written mode "x" (*_VOID.txt if a view's sha moved).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  EC-R1  Cells, policies and the AF-U / K_0 geometry exactly as ESCALATION-RC R1-R4 (its functions, unchanged). KM-U: U-global
         spherical k-means (g13_breakdown.ukm_fit, k-means++, max_iter 300) at k = 123 on the bundle's 12,334 TRAIN unit rows,
         seeds 0-4; an item is filed to the nearest of ALL k centroids (AK1's registered nearest-of-all form; KM-U is a DESCRIPTIVE
         arm, so the C-S1 mirroring is not applied, stated); an item whose AF cell is <no-routing-row> stays so (as k_cells R3);
         per-cell TRAIN policy by V.fit (union_af_route's fitter, unchanged) through the extra-arm hook (names KU0..KU4).
  EC-R2  Scores: margin = top-1 minus top-2 cosine over the arm's candidate set (escalation_rc.cand_scores; +inf with one
         candidate), OOS = max cosine. AF-U and K_0 candidate sets = ESCALATION-RC R3; KM-U: all k centroids.
  EC-R3  ECDF of record: F(x) = #{GATE scores <= x} / n_GATE (right-continuous), per arm and per score; GATE = ESCALATION-RC R5's
         set (side GATE with a routing row; 2,033 at its run). A +inf margin gets F_m = 1 (+inf <= +inf).
  EC-R4  u = min(F_m, F_oos). Order: u descending, ties by the sha256 hex digest of the item id ascending. At coverage c the first
         round(c N) items of the order keep their cell (Python round, half to even: ESCALATION-RC R9's rule), the rest get the
         TRAIN-chosen best single. Grid c = j / 100, j = 0..100.
  EC-R5  D_E(c) = acc_u(c) - [(1 - e) acc(cells) + e acc(best single)], e = the escalated share: (N - k) / N at the point (= 1 - c
         to within 0.5 / N, so the registered random line c acc + (1 - c) acc_best is met to within 0.5 / N x |gap|) and the
         replicate's WEIGHTED escalated share in each replicate (ESCALATION-RC R7's form, the same weights); hence D_E(0) = D_E(1)
         = 0 exactly (Support (g)). A_E = the plain mean of D_E over the 101 grid points.
  EC-R6  EC1 interval = point +- 1.96 SE_2stage (G14's form; run_boot: TRAIN units resampled and every policy re-fitted, EVAL
         components resampled within stratum; the ordering and the GATE ECDFs FIXED); percentile beside; i.i.d. SE from run_boot's
         own i.i.d. draws (union_route_common.iid_weights) -> DEFF, n_eff = N / DEFF, MDE80 = 2.80 SE_2stage. ORDERING-INFORMATIVE
         iff lo > 0; ORDERING-HARMFUL iff hi < 0; UNDETERMINED otherwise (an end point exactly 0 reads UNDETERMINED).
  EC-R7  c* (descriptive): the GATE key read from the gen view between the TRAIN key and the eval view; GATE items = EC-R3's set
         that is key-complete; each GATE item's cell = its modal AF leaf (ESCALATION-RC R5), its model = the frozen tree_cell pick
         (absent -> the best single); GATE u from the same ECDFs; c* = argmax of GATE acc_u(c) on the 0.01 grid, ties to the
         LARGEST coverage (the least escalation). Its EVAL gain over no escalation acc_u(c*) - acc_u(1) carries the two-stage
         interval (c* fixed: GATE not resampled).
  EC-R8  max_c D_E(c) on the 0.01 grid, ties to the largest coverage.
  EC-R9  "Everything again without IFEVAL": EVAL items whose stratum source is IFEVAL removed, each ordering restricted to the rest
         (N = the subset size), A_E per arm, the paired difference, max D_E and the c* gain with c* re-chosen on GATE without
         IFEVAL.
  EC-R10 Prediction bands closed (HELD iff the point lies in [lo, hi]); EC1's probabilities scored by the three-outcome Brier sum,
         printed and not credited as a forecast (registered: informed by the seen component curves).
  EC-R11 Not applicable (stated): no judge verdict (key-scored), so no wrong(established) count and no tie convention A / B; no
         call cache, --pilot or truncation guard (zero calls).
  EC-R12 DEVIATION (stated): the registration names escalation_rc.py blob a17f6821; the file is blob 8f99db7d since f460d72c
         (the scratch-dir switch: two import lines inside selftest() / run_mutants(), BELOW its SELFTEST marker; the code above
         the marker, which this script calls, is byte-identical). It is imported through union_route_common.py (blob d5473976),
         which pins 8f99db7d.

SELFTEST (--selftest; escalation_rc's fixture layout via union_route_common.build_layout, plus escalation_rc --run executed on it
to produce the ESCALATION-RC outcome the parity check reads; the excluded member is the fixture's one-cell member BBH):
  branches      EC1 ORDERING-INFORMATIVE / ORDERING-HARMFUL / UNDETERMINED by value incl. ends exactly 0, F-EC fired / not fired,
                P1-P4 bands inclusive at both ends, the Brier values, the verdict line of record, required lines
  units         ecdf (right-continuous, +inf -> 1), combined u, the sha256 tie-break, curve() against escalation_rc.rc_curve and a
                plain weighted loop (D_E(0) = D_E(1) = 0, the realised share), a subset, argmax ties to the largest c, the parser
  run_e2e       --run end to end: A_E(AF-U) with its two-stage interval and SE, A_E(K_0), A_E(KM-U) mean, A_E(AF-U) - A_E(K_0)
                with interval, max D_E and its coverage, c* and its EVAL gain, A_E without the excluded member, against an
                INDEPENDENT oracle (plain-loop fits on the fixture's raw rows, direct k-means calls, hand ECDFs and sorting, the same
                unit draws); the EC1 word and F-EC by the hand rule; the parity line; a second --run refused, the outcome unchanged
  refusals      pool, manifest, policy sha, ESCALATION-RC outcome sha, [ECURVE-PARITY] (one digit of the RC table), KM-U k,
                R4 agreement, [ECURVE-DENOM], [ECURVE-IDENTITY], [ECURVE-HOOK], an empty GATE, marker present; no outcome written
  dry_run       POOL first, no statistic, nothing written; the REAL constants' lines
  branch_cover  every print / refusal branch executed
MUTANTS: see MUTANTS at the end of this file; the table with each result is in the commit message.
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
import types         # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc 8f99db7d, union_cells_io, union_af_route bf3f17db)

TAG = "[ECURVE]"
TEST_ID = "ESCALATION-CURVE"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-05 (before any code or call) — ESCALATION-CURVE: on the union routing'
            ' data, what is the full curve of routed accuracy against coverage ..." L24653-L24665 (_as_of 8e681387, parent 07bc237f)')
OUT = "experiment_results/archv2/escalation_curve"
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/escalation_curve.READ_STARTED",
           rc_outcome="experiment_results/archv2/escalation_rc/outcome.txt",
           rc_outcome_sha="4dad8268248f63dbf5719e965ec53ea5d21c37d641642b6adb14749cdf00f6cf",
           ku_k=123, ku_seeds=(0, 1, 2, 3, 4), agree_min=0.999, excl="IFEVAL", n_gate=2033)
FIXTURE_REG = dict(out="res/ecurve/outcome.txt", marker="res/ecurve/READ_STARTED", rc_outcome="res/erc/outcome.txt", agree_min=0.95,
                   excl="BBH")
_REG = [REG]


def reg():
    return _REG[0]


GRID = tuple(j / 100.0 for j in range(101))
G05 = tuple(range(0, 101, 5))                      # indices of the 0.05 grid in GRID
SUPPORT = dict(deff=1.302, n_eff=4537, se=0.0036, mde=0.0100)
VERDICT_LINE = ("EC1 DESCRIPTIVE-ONLY at the prediction (+0.008 lies 0.008 from 0 < MDE80 0.0100; still classified as registered)")
PRED_AE = (0.003, 0.013)
PROB_EC1 = (("ORDERING-INFORMATIVE", 0.45), ("UNDETERMINED", 0.55), ("ORDERING-HARMFUL", 0.00))
PRED_DIFF = (-0.006, 0.006)
PRED_MAX = (0.008, 0.020)
PRED_MAXC = (0.35, 0.75)
PRED_CSTAR = (-0.004, 0.012)
HIT = Counter()
ERC, UAR, V, GB, GC = U.ERC, U.UAR, U.V, U.GB, U.GC
KU = tuple("KU%d" % s for s in (0, 1, 2, 3, 4))


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the curve machinery (EC-R3 .. EC-R8) ───────────────────────────────────────────────────────────────────────────────

def ecdf(gate):
    """EC-R3: x -> #{GATE <= x} / n (right-continuous); +inf maps to 1."""
    s = np.sort(np.asarray(gate, dtype=np.float64))
    n = len(s)
    if n == 0:
        refuse("an ECDF over zero GATE scores")

    def F(x):
        return np.searchsorted(s, np.asarray(x, dtype=np.float64), side="right") / float(n)
    return F


def combined_u(m, o, Fm, Fo):
    """EC-R4: u = min(F_m(margin), F_oos(OOS))."""
    return np.minimum(Fm(m), Fo(o))


def sha_rank(items):
    """The tie-break key: the rank of each item's sha256 hex digest (ascending)."""
    h = [hashlib.sha256(str(i).encode("utf-8")).hexdigest() for i in items]
    r = np.empty(len(h), dtype=np.int64)
    r[np.argsort(np.array(h), kind="stable")] = np.arange(len(h))
    return r


def order_u(u, rank):
    """u descending, ties by the sha rank ascending -> positions, the most confident (kept) first."""
    return np.lexsort((rank, -np.asarray(u, dtype=np.float64)))


def keep_counts(n, grid=GRID):
    return np.array([int(round(c_ * n)) for c_ in grid], dtype=np.int64)


def curve(cc, cb, order, v, grid=GRID):
    """EC-R4 / EC-R5 on the positions in `order` (a subset allowed): -> (acc_u(c), D_E(c)) over the grid, weights v."""
    o = np.asarray(order, dtype=np.int64)
    n = len(o)
    vo = np.asarray(v, dtype=np.float64)[o]
    S_v = np.concatenate([[0.0], np.cumsum(vo)])
    S_c = np.concatenate([[0.0], np.cumsum(vo * np.asarray(cc, dtype=np.float64)[o])])
    S_b = np.concatenate([[0.0], np.cumsum(vo * np.asarray(cb, dtype=np.float64)[o])])
    tot, tc, tb = S_v[-1], S_c[-1], S_b[-1]
    k = keep_counts(n, grid)
    acc = (S_c[k] + (tb - S_b[k])) / tot
    e = (tot - S_v[k]) / tot
    de = acc - ((1.0 - e) * (tc / tot) + e * (tb / tot))
    return acc, de


def argmax_last(x):
    """Argmax with ties to the LAST index (the largest coverage): EC-R7 / EC-R8."""
    x = np.asarray(x, dtype=np.float64)
    return int(len(x) - 1 - np.argmax(x[::-1]))


def ec1_verdict(st):
    """EC-R6: ORDERING-INFORMATIVE iff lo > 0; ORDERING-HARMFUL iff hi < 0; UNDETERMINED otherwise."""
    if st["lo"] > 0:
        return "ORDERING-INFORMATIVE"
    if st["hi"] < 0:
        return "ORDERING-HARMFUL"
    return "UNDETERMINED"


RC_ROW = re.compile(r"^    (\d\.\d\d)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$")


def parse_rc_tables(text):
    """ESCALATION-RC's printed RISK-COVERAGE tables -> {arm: {coverage string: (margin, OOS) strings}}."""
    out = {}
    for arm, nxt in (("AF-U", "RISK-COVERAGE K_0"), ("K_0", "PREDICTION P1")):
        if ("RISK-COVERAGE %s " % arm) not in text:
            refuse("[ECURVE-PARITY] the ESCALATION-RC outcome carries no RISK-COVERAGE %s table" % arm)
        blk = text.split("RISK-COVERAGE %s " % arm, 1)[1].split(nxt, 1)[0]
        rows = {}
        for ln in blk.splitlines():
            m_ = RC_ROW.match(ln)
            if m_:
                rows[m_.group(1)] = (m_.group(2), m_.group(3))
        if len(rows) != 21:
            refuse("[ECURVE-PARITY] the ESCALATION-RC %s table has %d rows, not 21" % (arm, len(rows)))
        out[arm] = rows
    return out


# ── KM-U (EC-R1) ───────────────────────────────────────────────────────────────────────────────────────────────────────

def ku_fit(Xt, k, seeds):
    """-> {name: unit centroids} for KU0..KU4 (g13_breakdown.ukm_fit on the bundle TRAIN rows)."""
    out = {}
    for s in seeds:
        fit, _t = GB.ukm_fit(Xt, k, s)
        out["KU%d" % s] = GC.FM.unit_rows(np.asarray(fit["centers"], dtype=np.float64))
    return out


def ku_cells(cents, af, vec):
    """{arm: {item: 'KU<s>:<j>'}} over the AF cells' items (<no-routing-row> kept)."""
    items = sorted(i for i, cl in af.items() if cl != UAR.NO_ROW)
    miss = [i for i in items if i not in vec]
    if miss:
        refuse("%d routed item(s) have no vector for the KM-U filing (first %s)" % (len(miss), miss[:3]))
    X = np.vstack([vec[i] for i in items]) if items else np.zeros((0, 1))
    out = {}
    for nm, C in sorted(cents.items()):
        g = np.argmax(X @ C.T, axis=1) if items else np.zeros(0, dtype=np.int64)
        d = {i: "%s:%03d" % (nm, int(j)) for i, j in zip(items, g)}
        for i, cl in af.items():
            if cl == UAR.NO_ROW:
                d[i] = UAR.NO_ROW
        out[nm] = d
    return out


def all_cands(n, k):
    return [tuple(range(k))] * n


# ── readout lines (pure functions of the stats; the selftest drives every branch through them) ─────────────────────────

def ec_lines(st):
    L = []
    say = L.append
    c = reg()
    a = st["A"]["AF-U"]
    say("")
    say("=== ESCALATION-CURVE (%s) ===" % REG_TEXT)
    say("DENOMINATOR: %d EVAL items in %d components (Kish mean cluster size %.3f; union EVAL, G14's scored set; Llama excluded);"
        " TRAIN %d items (policy fit); GATE %d items (ECDFs; c* on %d key-complete GATE items); never joined" % (
            a["n"], st["comp"], st["kish"], st["n_train"], st["n_gate"], st["n_gate_key"]))
    say("LIKE WITH LIKE: AF-U (deciding) [SC] vs random escalation on the SAME cells; K_0 [SC] (files by declared source: ESCALATION-RC"
        " D-2, not like with like) and KM-U [LF] (U-global k-means, k %d, seeds 0-4) DESCRIPTIVE" % c["ku_k"])
    say("ORDERING (fixed, EC-R4): u = min(F_m(margin), F_oos(OOS)), the arm's GATE ECDFs; ties by sha256(item id); one-candidate items"
        " (margin +inf, F_m = 1): AF-U %d EVAL items (u = F_oos)" % st["n_inf"])
    say("EC1 (DECIDING; the INTERVAL decides): A_E(AF-U) = mean over the 101-point grid of D_E(c) = %+.5f | two-stage 95%% [%+.5f, %+.5f]"
        " (point +- 1.96 SE_2stage) | percentile [%+.5f, %+.5f]" % (a["point"], a["lo"], a["hi"], a["pct"][0], a["pct"][1]))
    say("  support EC1: n %d, SE_2stage %.5f (registered upper bound 0.0036), i.i.d. SE %.5f, DEFF %.3f (registered 1.302, ESCALATION-RC"
        " transported), n_eff %.0f (registered 4,537), MDE80 %.5f (registered 0.0100); verdict line of record: %s" % (
            a["n"], a["se2"], a["se_iid"], a["deff"], a["n_eff"], a["mde"], VERDICT_LINE))
    v = ec1_verdict(a)
    if v == "ORDERING-INFORMATIVE":
        hit("EC1.INFORMATIVE")
        say("  EC1 -> ORDERING-INFORMATIVE (the 95% interval lies wholly above 0): escalating the lowest-u items first beats random"
            " escalation across the coverage range, on these cells")
    elif v == "ORDERING-HARMFUL":
        hit("EC1.HARMFUL")
        say("  EC1 -> ORDERING-HARMFUL (the 95% interval lies wholly below 0)")
    else:
        hit("EC1.UNDETERMINED")
        say("  EC1 -> UNDETERMINED (the 95% interval covers 0, an end exactly at 0 included)")
    if a["lo"] <= 0:
        hit("RULE8.REFUTED")
        say("  rule 8: ORDERING-INFORMATIVE is refuted at the planned n (lower bound %+.5f <= 0)" % a["lo"])
    else:
        hit("RULE8.NOT")
        say("  rule 8: ORDERING-INFORMATIVE is not refuted (lower bound %+.5f > 0)" % a["lo"])
    if v == "ORDERING-HARMFUL":
        hit("FEC.FIRED")
        say("FALSIFIER F-EC: FIRED (EC1 ORDERING-HARMFUL): escalating the lowest-margin and OOS items first is worse than random"
            " escalation across the coverage range; it overturns ESCALATION-RC's words that the rule 'avoids the cost of random"
            " escalation' and closes margin / OOS ordering as a route safety valve on these cells")
    else:
        hit("FEC.NOT_FIRED")
        say("FALSIFIER F-EC: NOT FIRED (EC1 %s; F-EC fires iff EC1 ORDERING-HARMFUL)" % v)
    say("CURVE AF-U (combined ordering; pointwise two-stage 95%; frozen-policy points at the 0.05 grid):")
    say("    coverage   acc_u(c)  [95%]                D_E(c)     [95%]                  gain over no escalation")
    for j in G05:
        r = st["pw"][j]
        say("    %.2f       %.5f   [%.5f, %.5f]   %+.5f   [%+.5f, %+.5f]   %+.5f" % (GRID[j], r["acc"], r["acc_lo"], r["acc_hi"], r["de"],
                                                                                 r["de_lo"], r["de_hi"], r["gain"]))
    say("DESCRIPTIVE: max_c D_E(c) (AF-U, 0.01 grid, ties to the largest coverage) = %+.5f at coverage %.2f" % (st["max_de"], st["max_c"]))
    say("DESCRIPTIVE: A_E(K_0) = %+.5f | two-stage 95%% [%+.5f, %+.5f] | SE_2stage %.5f" % (
        st["A"]["K_0"]["point"], st["A"]["K_0"]["lo"], st["A"]["K_0"]["hi"], st["A"]["K_0"]["se2"]))
    say("DESCRIPTIVE: A_E(KM-U) mean over seeds 0-4 = %+.5f | two-stage 95%% [%+.5f, %+.5f]; per seed %s" % (
        st["A"]["KM-U"]["point"], st["A"]["KM-U"]["lo"], st["A"]["KM-U"]["hi"], " / ".join("%+.5f" % x for x in st["ku_pts"])))
    d = st["A"]["diff"]
    say("DESCRIPTIVE: A_E(AF-U) - A_E(K_0) = %+.5f | two-stage 95%% [%+.5f, %+.5f] | percentile [%+.5f, %+.5f] (paired replicates)" % (
        d["point"], d["lo"], d["hi"], d["pct"][0], d["pct"][1]))
    say("DESCRIPTIVE (curves already seen in ESCALATION-RC; no fresh test): component-ordering areas A_E: AF-U margin %+.5f, OOS %+.5f,"
        " fragility %+.5f | K_0 margin %+.5f, OOS %+.5f, fragility %+.5f" % tuple(st["comp_area"][k] for k in (
            "AF-U margin", "AF-U oos", "AF-U fragility", "K_0 margin", "K_0 oos", "K_0 fragility")))
    cs = st["cstar"]
    say("DESCRIPTIVE: GATE-chosen operating point c* = %.2f (argmax of GATE acc_u(c) %.5f on %d key-complete GATE items, ties to the"
        " largest coverage); EVAL gain over no escalation acc_u(c*) - acc_u(1) = %+.5f | two-stage 95%% [%+.5f, %+.5f]" % (
            cs["c"], cs["gate_acc"], st["n_gate_key"], cs["point"], cs["lo"], cs["hi"]))
    nx = st["noex"]
    say("WITHOUT %s (EC-R9; %d EVAL items): A_E(AF-U) %+.5f [%+.5f, %+.5f]; A_E(K_0) %+.5f; A_E(KM-U) %+.5f; A_E(AF-U) - A_E(K_0)"
        " %+.5f [%+.5f, %+.5f]; max_c D_E %+.5f at %.2f; c* %.2f (GATE without %s), EVAL gain %+.5f [%+.5f, %+.5f]" % (
            c["excl"], nx["n"], nx["AF-U"]["point"], nx["AF-U"]["lo"], nx["AF-U"]["hi"], nx["K_0"]["point"], nx["KM-U"]["point"],
            nx["diff"]["point"], nx["diff"]["lo"], nx["diff"]["hi"], nx["max_de"], nx["max_c"], nx["cstar"]["c"], c["excl"],
            nx["cstar"]["point"], nx["cstar"]["lo"], nx["cstar"]["hi"]))
    say("STRUCTURAL (registered (g)): D_E(0) = %+.5f and D_E(1) = %+.5f (pinned at 0 by construction)" % (st["pw"][0]["de"], st["pw"][100]["de"]))
    ok = U.in_band(a["point"], PRED_AE)
    hit("P1.HELD" if ok else "P1.FAILED")
    say("PREDICTION P1 A_E(AF-U) +0.008 [+0.003, +0.013]: observed %+.5f -> %s" % (a["point"], "HELD" if ok else "FAILED"))
    say("PREDICTION P1 EC1 ORDERING-INFORMATIVE 0.45, UNDETERMINED 0.55, ORDERING-HARMFUL 0.00: observed %s; Brier %.4f (printed, not"
        " credited as a forecast: informed by the seen component curves)" % (v, U.brier(PROB_EC1, v)))
    ok = U.in_band(d["point"], PRED_DIFF)
    hit("P2.HELD" if ok else "P2.FAILED")
    say("PREDICTION P2 A_E(AF-U) - A_E(K_0) 0.000 [-0.006, +0.006] (descriptive): observed %+.5f -> %s" % (d["point"], "HELD" if ok else "FAILED"))
    ok = U.in_band(st["max_de"], PRED_MAX)
    hit("P3.HELD" if ok else "P3.FAILED")
    say("PREDICTION P3 max_c D_E(c) +0.013 [+0.008, +0.020] (descriptive): observed %+.5f -> %s" % (st["max_de"], "HELD" if ok else "FAILED"))
    ok = U.in_band(st["max_c"], PRED_MAXC)
    hit("P3C.HELD" if ok else "P3C.FAILED")
    say("PREDICTION P3 its coverage 0.55 [0.35, 0.75] (descriptive): observed %.2f -> %s" % (st["max_c"], "HELD" if ok else "FAILED"))
    ok = U.in_band(cs["point"], PRED_CSTAR)
    hit("P4.HELD" if ok else "P4.FAILED")
    say("PREDICTION P4 GATE-chosen c* EVAL gain over no escalation +0.004 [-0.004, +0.012] (descriptive): observed %+.5f -> %s" % (
        cs["point"], "HELD" if ok else "FAILED"))
    say("WORDS: this escalates the ROUTE to the best single model, never to a judge (ESCALATE-LLAMA-LAW untouched); AF-U is [SC] and K_0"
        " files by source, so nothing here is tree-specific; the margin-only, OOS-only and fragility curves and the fragility peak were"
        " SEEN in ESCALATION-RC (no fresh test of them); key-scored end to end (no judge verdict: no wrong(established) count, no"
        " convention A / B); content-closed under CK-CLOSE-v2 (residual disclosed)")
    say("WILL NOT SHOW (registered): escalation to a judge; a fresh test of the fragility peak or of either seen component curve; a"
        " tree-specific gain; an operating point chosen on EVAL; judged decisions or real traffic; anything beyond the union roster"
        " and one draw")
    return L, dict(EC1=v, F_EC=(v == "ORDERING-HARMFUL"))


# ── modes ──────────────────────────────────────────────────────────────────────────────────────────────────────────────

def files():
    return [os.path.abspath(__file__), U.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS]


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)): %d EVAL items in %d components (Kish 1.09); DEFF 1.302 (ESCALATION-RC, measured, transported),"
        " n_eff 4,537, SE(A_E) <= 0.0036, MDE80 0.0100; %s" % (c["n_route"], c["comp_route"], VERDICT_LINE))
    say("PLANNED: B = %d two-stage replicates (default_rng(%d)); grid c = 0.00, 0.01, ..., 1.00 (101 points); KM-U k %d seeds %s; R4"
        " agreement floor %.3f; GATE %d items (ECDFs); without %s; ESCALATION-RC outcome %s sha256 %s (the parity check)" % (
            c["B"], c["seed"], c["ku_k"], "-".join(str(s) for s in (c["ku_seeds"][0], c["ku_seeds"][-1])), c["agree_min"], c["n_gate"],
            c["excl"], c["rc_outcome"], c["rc_outcome_sha"][:16]))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(c["identity"])))


def rc_outcome(say):
    c = reg()
    p = U.P(c["rc_outcome"])
    if not os.path.isfile(p):
        hit("REFUSE.RC_ABSENT")
        refuse("the ESCALATION-RC outcome %s is absent (the parity check needs it)" % c["rc_outcome"])
    sh = U.sha256_bytes(p)
    if sh != c["rc_outcome_sha"]:
        hit("REFUSE.RC_SHA")
        refuse("the ESCALATION-RC outcome %s is sha256 %s, not the pinned %s" % (c["rc_outcome"], sh, c["rc_outcome_sha"]))
    say("  ESCALATION-RC outcome %s sha256 %s (= the pin)" % (c["rc_outcome"], sh))
    return parse_rc_tables(open(p, encoding="utf-8").read())


def gate_scores(say, g, rows_h, side, cents):
    """EC-R3: the GATE items (ESCALATION-RC R5) and every arm's GATE margin / OOS scores."""
    its, gcell, gsrc = ERC.gate_items(rows_h, side)
    if not its:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: the ECDFs are undefined (EC-R3)")
    vec = ERC.get_vectors(its)
    nov = [i for i in its if i not in vec]
    if nov:
        refuse("%d GATE item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    sc = ERC.score_items(say, g, its, gcell, gsrc, vec)
    out = {"AF-U": sc["AF"], "K_0": sc["K"]}
    Xg = np.vstack([vec[i] for i in its])
    for nm, C in sorted(cents.items()):
        out[nm] = ERC.cand_scores(Xg, all_cands(len(its), len(C)), C)
    say("  GATE (EC-R3): %d items with a routing row; ECDFs per arm (AF-U, K_0, %s); margin +inf (one candidate) on %d AF-U GATE items" % (
        len(its), ", ".join(sorted(cents)), int(np.isinf(sc["AF"][0]).sum())))
    hit("GATE.DONE")
    return its, gcell, out


def prepare(say):
    c = reg()
    S = U.prepare(say, c, refuse, hit)
    u = UAR.reg()
    ip = UAR.input_paths()
    b, _meta = GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    g = ERC.load_geometry(say, S["man"], S["single"], b, S["af"])
    L = int(sum(int(v) for v in S["ksrc"].values()))
    if L != int(c["ku_k"]):
        hit("REFUSE.KU_K")
        refuse("AF-U's total leaf count is %d, not the registered matched k %d" % (L, c["ku_k"]))
    Xt = GC.FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    cents = ku_fit(Xt, L, c["ku_seeds"])
    say("  KM-U (EC-R1): ukm_fit k %d on %d bundle TRAIN rows, seeds %s" % (L, len(Xt), ", ".join(str(s) for s in c["ku_seeds"])))
    side, _smeta = UAR._SIDES[0]()
    val = UAR.afu_paths(S["single"])[1]
    rows_h, rows_t = ERC.item_rows(ip["merged"] if S["single"] else val)
    srcs = UAR.item_sources(rows_h + rows_t)
    gits, gcell, gsc = gate_scores(say, g, rows_h, side, cents)
    return dict(S, b=b, g=g, cents=cents, side=side, srcs=srcs, rows_h=rows_h, gits=gits, gcell=gcell, gsc=gsc)


def eval_scores(say, P_, items):
    """EVAL scores of every arm (EC-R2) and the R4 checks (AF agreement; K_0 re-filed = k_cells_s0.tsv)."""
    c = reg()
    g, af, k0, srcs = P_["g"], P_["af"], P_["kx"]["K0"], P_["srcs"]
    miss = [i for i in items if i not in srcs]
    if miss:
        refuse("%d EVAL item(s) have no routing row (first %s)" % (len(miss), miss[:3]))
    vec = ERC.get_vectors(items)
    nov = [i for i in items if i not in vec]
    if nov:
        refuse("%d EVAL item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    nb = ERC.check_vectors_vs_bundle(vec, P_["b"])
    sc = ERC.score_items(say, g, items, af, srcs, vec, k_cell=k0)
    ag, nm = sc["agree"]
    share = ag / nm if nm else 1.0
    say("  R4 AF filing agreement: argmax over the candidates = the AF cell of record on %d of %d non-one-cell EVAL items (%.5f; floor"
        " %.3f); vectors equal to the bundle's on %d items" % (ag, nm, share, c["agree_min"], nb))
    if share < c["agree_min"]:
        hit("REFUSE.AGREE")
        refuse("R4: AF filing agreement %.5f < %.3f" % (share, c["agree_min"]))
    say("  R4 K_0 re-filing: %d of %d EVAL items differ from k_cells_s0.tsv (must be 0)" % (sc["kdiff"], len(items)))
    if sc["kdiff"]:
        hit("REFUSE.KDIFF")
        refuse("R4: K_0 re-filed differs from k_cells_s0.tsv on %d item(s)" % sc["kdiff"])
    out = {"AF-U": sc["AF"], "K_0": sc["K"]}
    X = np.vstack([vec[i] for i in items])
    for nm_, C in sorted(P_["cents"].items()):
        out[nm_] = ERC.cand_scores(X, all_cands(len(items), len(C)), C)
    return out


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, files())
    denominators(say)
    rc_outcome(say)
    P_ = prepare(say)
    ev = sorted(i for i, (_c, s) in P_["side"].items() if s == "EVAL" and P_["af"].get(i, V.NO_ROUTING_ROW) != V.NO_ROUTING_ROW)
    say("  EVAL side items with an AF cell (no key read): %d" % len(ev))
    eval_scores(say, P_, ev)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    U.read_views(cfg, say, True, P_["af"], P_["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no key read (TRAIN, GATE or EVAL); no statistic of EVAL printed.")
    hit("DRY.DONE")
    return 0


def gate_key(cfg, say, models, gits):
    """EC-R7: the GATE key (gen view, response_lite, the reader's variant rule, MATH-FIX overlay) -> {item: {model: 0/1}}."""
    rule = cfg.pre.get("variant_rule")
    tw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view(GATE)", say)
    try:
        meta = V.side_items(tw, cfg.cv_u, "GATE")
        want = {i: meta[i] for i in gits if i in meta}
        tw.unseal("%s: the GATE key for c* only (EC-R7), after the TRAIN key and before the eval view" % TEST_ID)
        K, kst = V.read_key(tw, "response_lite", cfg.cv_u, models, want, True, rule)
    finally:
        tw.close()
    ok = V.after_sha(cfg.gen_path, gsha, "gen_view(GATE)", say)
    if not ok:
        refuse("[PIN] the gen view's sha moved during the GATE key read")
    comp = V.complete_items(K, models)
    say("  GATE key (EC-R7): %d GATE items of the R5 set in the view; key-complete %d (cells single %d, multi %d unusable %d)" % (
        len(want), len(comp), kst["single"], kst["multi"], kst["multi_unusable"]))
    return K, comp, want


def cstar_on_gate(P_, Kg, comp, models, keep_mask=None):
    """EC-R7: c* on GATE (frozen policy; AF-U combined ordering) -> (c*, GATE acc at c*, index)."""
    pol = P_["pol"]
    pos = {it: j for j, it in enumerate(P_["gits"])}
    its = [it for it in comp if it in pos and (keep_mask is None or keep_mask(it))]
    if not its:
        refuse("no key-complete GATE item for c*")
    gb = pol["best_single"]
    m, o = P_["gsc"]["AF-U"][0], P_["gsc"]["AF-U"][1]
    idx = np.array([pos[i] for i in its], dtype=np.int64)
    u = combined_u(m[idx], o[idx], P_["F"]["AF-U"][0], P_["F"]["AF-U"][1])
    cc = np.array([Kg[i][pol["tree_cell"].get(P_["gcell"][i]) or gb] for i in its], dtype=np.float64)
    cb = np.array([Kg[i][gb] for i in its], dtype=np.float64)
    acc, _de = curve(cc, cb, order_u(u, sha_rank(its)), np.ones(len(its)))
    j = argmax_last(acc)
    return GRID[j], float(acc[j]), j, len(its)


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
    rc_tab = rc_outcome(say)
    P_ = prepare(say)
    P_["F"] = {arm: (ecdf(P_["gsc"][arm][0]), ecdf(P_["gsc"][arm][1])) for arm in ["AF-U", "K_0"] + sorted(P_["cents"])}
    ev_all = sorted(i for i, (_c, s_) in P_["side"].items() if s_ == "EVAL" and P_["af"].get(i, V.NO_ROUTING_ROW) != V.NO_ROUTING_ROW)
    say("  EVAL side items with an AF cell (scored before the key read; the key-complete subset is taken after): %d" % len(ev_all))
    sc_all = eval_scores(say, P_, ev_all)
    ids_all = sorted(i for i, cl in P_["af"].items() if cl != UAR.NO_ROW)
    vec_all = ERC.get_vectors(ids_all)
    nb = ERC.check_vectors_vs_bundle(vec_all, P_["b"])
    kuc = ku_cells(P_["cents"], P_["af"], vec_all)
    say("  KM-U cells (EC-R1): %d routed TRAIN / EVAL items filed to the nearest of all %d centroids per seed (vectors equal to the bundle's"
        " on %d items)" % (len(ids_all), c["ku_k"], nb))
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):
        refuse("the reader's B / seed %s / %s are not the registered %s / %s" % (cfg.reg["B"], cfg.reg["seed"], c["B"], c["seed"]))
    gk = {}

    def between(K_tr, train_meta, models):
        gk["K"], gk["comp"], gk["meta"] = gate_key(cfg, say, models, P_["gits"])
        gk["models"] = models
    D, ok_sha = U.read_views(cfg, say, False, P_["af"], dict(P_["kx"], **kuc), c["marker"],
                             "ESCALATION-CURVE: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit,
                             between=between, tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "ECURVE")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    U.b3_check(D, cfg, P_["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s; AF, K0..K4, TRUE source, TRUE source/domain)"
        % P_["pol"]["best_single"])
    items_E = [D.items[k] for k in D.E]
    pos_all = {it: j for j, it in enumerate(ev_all)}
    if any(it not in pos_all for it in items_E):
        refuse("a scored EVAL item was not scored before the key read")
    idx = np.array([pos_all[it] for it in items_E], dtype=np.int64)
    sc = {arm: tuple(np.asarray(x)[idx] for x in v_) for arm, v_ in sc_all.items()}
    NE = len(items_E)
    rank = sha_rank(items_E)
    keep = np.array([D.src[k] != c["excl"] for k in D.E], dtype=bool)
    g = P_["g"]
    cm_af = ERC.cell_models(P_["pol"], g.af_names, D.models)
    cm_k = ERC.cell_models(P_["pol"], g.k_names, D.models, "K0")
    frag = {"AF-U": ERC.fragility(sc["AF-U"][2], sc["AF-U"][3], cm_af), "K_0": ERC.fragility(sc["K_0"][2], sc["K_0"][3], cm_k)}
    orders = {}
    for arm in ["AF-U", "K_0"] + list(KU):
        Fm, Fo = P_["F"][arm]
        orders[("comb", arm)] = order_u(combined_u(sc[arm][0], sc[arm][1], Fm, Fo), rank)
    for arm in ("AF-U", "K_0"):
        od = ERC.orders(sc[arm][0], sc[arm][1], frag[arm])
        for nm in ("margin", "oos", "fragility"):
            orders[(nm, arm)] = od[nm]
    arm_of = {o_: o_[1] for o_ in orders}
    subs = {"all": None, "noex": keep}

    def ordered(o_, sub):
        return orders[o_] if sub is None else orders[o_][sub[orders[o_]]]
    AE = D.A[D.E]
    r = np.arange(NE)
    gt = D.groupings["tree"][0]

    def corr(Pp):
        gb = Pp.gb

        def res(key, gg):
            p_ = Pp.pol[key][gg[D.E]]
            return AE[r, np.where(p_ < 0, gb, p_)].astype(np.float64)
        out_ = {"best": AE[r, gb].astype(np.float64), "AF-U": res("tree", gt), "K_0": res("x:K0", D.groupings["x:K0"][0])}
        for nm in KU:
            out_[nm] = res("x:" + nm, D.groupings["x:" + nm][0])
        return out_

    def trace(cr, v):
        res_ = {}
        for o_ in orders:
            for sk, sub in subs.items():
                res_[(o_, sk)] = curve(cr[arm_of[o_]], cr["best"], ordered(o_, sub), v)
        return res_
    rec = dict(two=[], chk=[])

    def hook(D_, wt, v):
        Pp = V.fit(D_, wt)
        cr = corr(Pp)
        rec["two"].append(trace(cr, np.asarray(v, dtype=np.float64)))
        rec["chk"].append((float(np.asarray(v) @ cr["best"]) / float(np.sum(v)), float(np.asarray(v) @ cr["AF-U"]) / float(np.sum(v)),
                           float(np.asarray(v) @ cr["K_0"]) / float(np.sum(v))))
    bt = V.run_boot(D, c["B"], c["seed"], hook=hook)
    if D.fit_asserts != 2 * c["B"] + 2:
        refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, 2 * c["B"] + 2))
    chk = np.asarray(rec["chk"])
    ref = np.stack([bt["two"][:, 0, V.BS], bt["two"][:, 0, V.TREE], bt["two"][:, 0, U.karm(D, "K0")]], axis=1)
    if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):
        hit("REFUSE.HOOK")
        refuse("[ECURVE-HOOK] the hook's re-fitted accuracies differ from run_boot's own arms")
    ok, got = U.identity(bt, D, c["identity"])
    if not ok:
        hit("REFUSE.IDENTITY")
        refuse("[ECURVE-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
    say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
    hit("IDENTITY.OK")
    cr0 = corr(bt["P0"])
    bad = []
    for arm in ("AF-U", "K_0"):
        od = ERC.orders(sc[arm][0], sc[arm][1], frag[arm])
        cm_ = ERC.rc_curve(cr0[arm], cr0["best"], od["margin"])
        co_ = ERC.rc_curve(cr0[arm], cr0["best"], od["oos"])
        for j, c_ in enumerate(ERC.GRID):
            want = rc_tab[arm].get("%.2f" % c_)
            if want is None or ("%.5f" % cm_[j], "%.5f" % co_[j]) != want:
                bad.append("%s %.2f: %s / %s vs printed %s" % (arm, c_, "%.5f" % cm_[j], "%.5f" % co_[j], want))
    if bad:
        hit("REFUSE.PARITY")
        refuse("[ECURVE-PARITY] %d risk-coverage point(s) differ from ESCALATION-RC's printed tables (first %s)" % (len(bad), bad[:2]))
    say("PARITY (registered IDENTITY CHECK): the margin-only and OOS-only risk-coverage tables of AF-U and K_0 at the 0.05 grid (2 x 2"
        " x 21 points) -> REPRODUCED (ESCALATION-RC's printed digits)")
    hit("PARITY.OK")
    # points, i.i.d. replicates, two-stage replicates
    pt = trace(cr0, np.ones(NE))
    iid = [trace(cr0, v_) for v_ in U.iid_weights(c["seed"], NE, c["B"])]
    two = rec["two"]

    def area(tr, o_, sk):
        return float(np.mean(tr[(o_, sk)][1]))

    def stat(fn):
        return U.interval(fn(pt), [fn(t) for t in two], [fn(t) for t in iid], NE)

    def ku_mean(sk):
        return lambda t: float(np.mean([area(t, ("comb", nm), sk) for nm in KU]))
    A = {"AF-U": stat(lambda t: area(t, ("comb", "AF-U"), "all")), "K_0": stat(lambda t: area(t, ("comb", "K_0"), "all")),
         "KM-U": stat(ku_mean("all")),
         "diff": stat(lambda t: area(t, ("comb", "AF-U"), "all") - area(t, ("comb", "K_0"), "all"))}
    pw = {}
    main = (("comb", "AF-U"), "all")
    for j in range(101):
        a_ = U.interval(float(pt[main][0][j]), [t[main][0][j] for t in two], [t[main][0][j] for t in iid], NE)
        d_ = U.interval(float(pt[main][1][j]), [t[main][1][j] for t in two], [t[main][1][j] for t in iid], NE)
        pw[j] = dict(acc=a_["point"], acc_lo=a_["lo"], acc_hi=a_["hi"], de=d_["point"], de_lo=d_["lo"], de_hi=d_["hi"],
                     gain=float(pt[main][0][j] - pt[main][0][100]))
    jm = argmax_last(pt[main][1])
    Kg, gcomp = gk["K"], gk["comp"]
    cst, gacc, jc, n_gk = cstar_on_gate(P_, Kg, gcomp, gk["models"])

    def gain_at(j_, sk):
        mm = (("comb", "AF-U"), sk)
        return lambda t: float(t[mm][0][j_] - t[mm][0][100])
    cs = dict(stat(gain_at(jc, "all")), c=cst, gate_acc=gacc)
    cst_x, _gx, jcx, _n = cstar_on_gate(P_, Kg, gcomp, gk["models"], keep_mask=lambda it: gk["meta"][it][1] != c["excl"])
    mx = (("comb", "AF-U"), "noex")
    jmx = argmax_last(pt[mx][1])
    noex = dict(n=int(keep.sum()), **{"AF-U": stat(lambda t: area(t, ("comb", "AF-U"), "noex")),
                                      "K_0": stat(lambda t: area(t, ("comb", "K_0"), "noex")), "KM-U": stat(ku_mean("noex")),
                                      "diff": stat(lambda t: area(t, ("comb", "AF-U"), "noex") - area(t, ("comb", "K_0"), "noex"))},
                max_de=float(pt[mx][1][jmx]), max_c=GRID[jmx], cstar=dict(stat(gain_at(jcx, "noex")), c=cst_x))
    st = dict(A=A, pw=pw, comp=n_comp, kish=U.kish_eval(D), n_train=D.n_train, n_gate=len(P_["gits"]), n_gate_key=n_gk,
              n_inf=int(np.isinf(sc["AF-U"][0]).sum()), max_de=float(pt[main][1][jm]), max_c=GRID[jm], cstar=cs,
              ku_pts=[area(pt, ("comb", nm), "all") for nm in KU], noex=noex,
              comp_area={"%s %s" % (arm, nm): area(pt, (nm, arm), "all") for arm in ("AF-U", "K_0") for nm in ("margin", "oos", "fragility")})
    L, words = ec_lines(st)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, bt=bt, sc=sc, pt=pt, cstar=(cst, jc), cstar_x=(cst_x, jcx))


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
        return U.run_mutants(os.path.abspath(__file__), "escalation_curve", MUTANTS, TAG, only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

BRANCHES = ("EC1.INFORMATIVE", "EC1.HARMFUL", "EC1.UNDETERMINED", "RULE8.REFUTED", "RULE8.NOT", "FEC.FIRED", "FEC.NOT_FIRED", "P1.HELD",
            "P1.FAILED", "P2.HELD", "P2.FAILED", "P3.HELD", "P3.FAILED", "P3C.HELD", "P3C.FAILED", "P4.HELD", "P4.FAILED", "IDENTITY.OK",
            "PARITY.OK", "RUN.DONE", "DRY.DONE", "MARKER.WRITTEN", "GATE.DONE", "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.POLICY_SHA",
            "REFUSE.MANIFEST", "REFUSE.RC_SHA", "REFUSE.PARITY", "REFUSE.KU_K", "REFUSE.AGREE", "REFUSE.KDIFF", "REFUSE.DENOM",
            "REFUSE.IDENTITY", "REFUSE.HOOK", "REFUSE.GATE_EMPTY")
need = U.need
NUM = r"([+-]?[0-9.]+)"


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _ready(base):
    """The ESCALATION-RC outcome the parity check reads: escalation_rc --run executed once on the shared layout (unedited code)."""
    if getattr(base, "ec_ready", False):
        return base
    p = os.path.join(base.tmp, "res", "erc", "outcome.txt")
    if not os.path.isfile(p):
        _t, err, _r = ERC._cap(ERC.run, base)
        if err:
            raise AssertionError("fixture escalation_rc --run refused: %s" % err)
    base.common = dict(base.common, rc_outcome_sha=U.sha256_bytes(p), ku_k=int(sum(base.fx.ksrc.values())),
                       n_gate=sum(1 for it in base.fx.spec["items"] if it["side"] == "GATE"))
    base.ec_ready = True
    return base


def _iv(pt, lo, hi, n=5907):
    se = (hi - lo) / 3.92
    return dict(point=pt, lo=lo, hi=hi, pct=(lo, hi), se2=se, se_iid=se / 1.2, deff=1.44, n_eff=n / 1.44, mde=2.8 * se, n=n)


def _syn(pt=0.004, lo=0.001, hi=0.007, diff=0.0, mx=0.013, mc=0.55, cg=0.004):
    pw = {j: dict(acc=0.62, acc_lo=0.61, acc_hi=0.63, de=0.0, de_lo=-0.001, de_hi=0.001, gain=0.0) for j in range(101)}
    A = {"AF-U": _iv(pt, lo, hi), "K_0": _iv(0.003, -0.002, 0.008), "KM-U": _iv(0.002, -0.003, 0.007), "diff": _iv(diff, diff - 0.005, diff + 0.005)}
    noex = dict(n=5745, max_de=0.01, max_c=0.5, cstar=dict(_iv(0.001, -0.002, 0.004), c=0.8), **{k: dict(v) for k, v in A.items()})
    return dict(A=A, pw=pw, comp=5404, kish=1.09, n_train=11841, n_gate=2033, n_gate_key=2000, n_inf=162, max_de=mx, max_c=mc,
                cstar=dict(_iv(cg, cg - 0.004, cg + 0.004), c=0.7, gate_acc=0.62), ku_pts=[0.001] * 5, noex=noex,
                comp_area={"%s %s" % (a_, n_): 0.001 for a_ in ("AF-U", "K_0") for n_ in ("margin", "oos", "fragility")})


def st_branches():
    cases = [((0.004, 0.001, 0.007), "ORDERING-INFORMATIVE"), ((-0.004, -0.007, -0.001), "ORDERING-HARMFUL"),
             ((0.001, -0.002, 0.004), "UNDETERMINED"), ((0.003, 0.0, 0.006), "UNDETERMINED"), ((-0.003, -0.006, 0.0), "UNDETERMINED"),
             ((0.003, 1e-12, 0.006), "ORDERING-INFORMATIVE"), ((-0.003, -0.006, -1e-12), "ORDERING-HARMFUL")]
    bri = {"ORDERING-INFORMATIVE": 0.605, "UNDETERMINED": 0.405, "ORDERING-HARMFUL": 1.505}
    saved = _REG[0]
    _REG[0] = REG
    try:
        for (p_, l_, h_), want in cases:
            L, w = ec_lines(_syn(p_, l_, h_))
            t = "\n".join(L)
            assert w["EC1"] == want, (p_, l_, h_, w)
            need(t, "  EC1 -> %s" % want, "verdict line of record: " + VERDICT_LINE,
                 "A_E(AF-U) = mean over the 101-point grid of D_E(c) = %+.5f | two-stage 95%% [%+.5f, %+.5f]" % (p_, l_, h_),
                 "PREDICTION P1 EC1 ORDERING-INFORMATIVE 0.45, UNDETERMINED 0.55, ORDERING-HARMFUL 0.00: observed %s; Brier %.4f" % (want, bri[want]),
                 "WILL NOT SHOW (registered)", "DENOMINATOR: 5907 EVAL items in 5404 components", "support EC1: n 5907")
            if want == "ORDERING-HARMFUL":
                assert w["F_EC"] is True
                need(t, "FALSIFIER F-EC: FIRED (EC1 ORDERING-HARMFUL)")
                assert "F-EC: NOT FIRED" not in t
            else:
                assert w["F_EC"] is False
                need(t, "FALSIFIER F-EC: NOT FIRED (EC1 %s; F-EC fires iff EC1 ORDERING-HARMFUL)" % want)
            if l_ <= 0:
                need(t, "rule 8: ORDERING-INFORMATIVE is refuted at the planned n (lower bound %+.5f <= 0)" % l_)
            else:
                need(t, "rule 8: ORDERING-INFORMATIVE is not refuted (lower bound %+.5f > 0)" % l_)
        for x, want in ((0.003, "HELD"), (0.013, "HELD"), (0.0029, "FAILED"), (0.0131, "FAILED")):
            need("\n".join(ec_lines(_syn(x, x - 0.004, x + 0.004))[0]), "PREDICTION P1 A_E(AF-U) +0.008 [+0.003, +0.013]: observed %+.5f -> %s" % (x, want))
        for x, want in ((-0.006, "HELD"), (0.006, "HELD"), (-0.0061, "FAILED"), (0.0061, "FAILED")):
            need("\n".join(ec_lines(_syn(diff=x))[0]), "PREDICTION P2 A_E(AF-U) - A_E(K_0) 0.000 [-0.006, +0.006] (descriptive): observed %+.5f -> %s" % (x, want))
        for x, want in ((0.008, "HELD"), (0.020, "HELD"), (0.0079, "FAILED"), (0.0201, "FAILED")):
            need("\n".join(ec_lines(_syn(mx=x))[0]), "PREDICTION P3 max_c D_E(c) +0.013 [+0.008, +0.020] (descriptive): observed %+.5f -> %s" % (x, want))
        for x, want in ((0.35, "HELD"), (0.75, "HELD"), (0.34, "FAILED"), (0.76, "FAILED")):
            need("\n".join(ec_lines(_syn(mc=x))[0]), "PREDICTION P3 its coverage 0.55 [0.35, 0.75] (descriptive): observed %.2f -> %s" % (x, want))
        for x, want in ((-0.004, "HELD"), (0.012, "HELD"), (-0.0041, "FAILED"), (0.0121, "FAILED")):
            need("\n".join(ec_lines(_syn(cg=x))[0]), "PREDICTION P4 GATE-chosen c* EVAL gain over no escalation +0.004 [-0.004, +0.012] (descriptive):"
                 " observed %+.5f -> %s" % (x, want))
        t = "\n".join(ec_lines(_syn())[0])
    finally:
        _REG[0] = saved
    rows = [ln for ln in t.splitlines() if re.match(r"^    [01]\.\d\d       0\.62000", ln)]
    assert len(rows) == 21, "the 0.05-grid curve table must carry 21 rows (%d)" % len(rows)
    need(t, "WITHOUT IFEVAL (EC-R9; 5745 EVAL items)", "STRUCTURAL (registered (g)): D_E(0) = +0.00000 and D_E(1) = +0.00000",
         "DESCRIPTIVE: A_E(AF-U) - A_E(K_0) = +0.00000", "c* = 0.70")


def _plain_curve(cc, cb, order, v, grid=GRID):
    n = len(order)
    tot = sum(v[i] for i in order)
    tc = sum(v[i] * cc[i] for i in order)
    tb = sum(v[i] * cb[i] for i in order)
    acc, de = [], []
    for c_ in grid:
        k = int(round(c_ * n))
        a_ = (sum(v[i] * cc[i] for i in order[:k]) + sum(v[i] * cb[i] for i in order[k:])) / tot
        e = sum(v[i] for i in order[k:]) / tot
        acc.append(a_)
        de.append(a_ - ((1 - e) * tc / tot + e * tb / tot))
    return acc, de


def st_units():
    F = ecdf([0.1, 0.2, 0.2, float("inf")])
    assert F(0.2) == 0.75 and F(0.19) == 0.25 and F(float("inf")) == 1.0 and F(0.05) == 0.0 and F(0.1) == 0.25
    Fm, Fo = ecdf([0.0, 1.0, float("inf")]), ecdf([0.5, 0.6, 0.7, 0.8])
    u = combined_u(np.array([float("inf"), 0.5, 2.0]), np.array([0.65, 0.9, 0.55]), Fm, Fo)
    assert np.allclose(u, [0.5, 1 / 3, 0.25]), u
    items = ["i:%03d" % j for j in range(9)]
    rk = sha_rank(items)
    hx = [hashlib.sha256(i.encode()).hexdigest() for i in items]
    assert [items[j] for j in np.argsort(rk)] == [items[j] for j in sorted(range(9), key=lambda j: hx[j])]
    uu = np.array([0.5, 0.9, 0.5, 0.1, 0.9, 0.5, 0.2, 0.2, 0.7])
    o = order_u(uu, rk)
    want = sorted(range(9), key=lambda j: (-uu[j], hx[j]))
    assert o.tolist() == want, (o, want)
    assert want != sorted(range(9), key=lambda j: (-uu[j], j)), "the sha256 tie-break must differ from the item order here"
    rs = np.random.RandomState(4)
    n = 37
    cc, cb = rs.randint(0, 2, n).astype(float), rs.randint(0, 2, n).astype(float)
    od = rs.permutation(n)
    acc, de = curve(cc, cb, od, np.ones(n), grid=ERC.GRID)
    assert np.allclose(acc, ERC.rc_curve(cc, cb, od), atol=1e-15)
    v = rs.randint(0, 4, n).astype(float)
    v[od[0]] = 2.0
    a1, d1 = curve(cc, cb, od, v)
    a2, d2 = _plain_curve(cc, cb, list(od), v)
    assert np.allclose(a1, a2, atol=1e-12) and np.allclose(d1, d2, atol=1e-12)
    assert abs(d1[0]) < 1e-12 and abs(d1[-1]) < 1e-12 and max(abs(x) for x in d1) > 1e-3
    sub = od[od % 3 != 0]
    a3, d3 = curve(cc, cb, sub, v)
    a4, d4 = _plain_curve(cc, cb, list(sub), v)
    assert np.allclose(a3, a4, atol=1e-12) and np.allclose(d3, d4, atol=1e-12)
    assert keep_counts(5, (0.5, 0.3, 0.1)).tolist() == [2, 2, 0] and keep_counts(7, (0.5, 0.29)).tolist() == [4, 2]
    assert argmax_last([0.1, 0.3, 0.3, 0.2]) == 2 and argmax_last([0.5, 0.1, 0.5]) == 2 and argmax_last([0.9, 0.1]) == 0
    rows = "".join("    %.2f       0.%05d   0.%05d   0.60000   0.60000\n" % (round(1 - 0.05 * j, 2), 60000 + j, 61000 + j) for j in range(21))
    txt = "RISK-COVERAGE AF-U (x):\n" + rows + "RISK-COVERAGE K_0 (x):\n" + rows + "PREDICTION P1 e\n"
    tab = parse_rc_tables(txt)
    assert tab["AF-U"]["0.50"] == ("0.60010", "0.61010") and tab["K_0"]["1.00"] == ("0.60000", "0.61000") and len(tab["K_0"]) == 21
    try:
        parse_rc_tables(txt.replace("    0.00       0.60020", "    x", 1))
        raise AssertionError("a 20-row table was not refused")
    except SystemExit as e:
        assert "20 rows" in str(e)
    # c* on GATE: a synthetic layout whose GATE accuracy peaks at an interior coverage (and ties to the larger one)
    gits = ["g%d" % j for j in range(10)]
    m = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
    P_ = dict(pol=dict(best_single="B", tree_cell={"c1": "A"}), gits=gits, gcell={g_: "c1" for g_ in gits},
              gsc={"AF-U": (m, m)}, F={"AF-U": (ecdf(m), ecdf(m))})
    Kg = {g_: {"A": int(j < 4), "B": int(j >= 4)} for j, g_ in enumerate(gits)}
    c_, acc_, j_, n_ = cstar_on_gate(P_, Kg, gits, ["A", "B"])
    want_c = max(x for x in GRID if int(round(x * 10)) == 4)
    assert (c_, acc_, n_) == (want_c, 1.0, 10) and GRID[j_] == c_ and 0.4 <= c_ < 0.5, (c_, acc_, n_)
    Kg2 = {g_: {"A": 1, "B": 1} for g_ in gits}
    assert cstar_on_gate(P_, Kg2, gits, ["A", "B"])[0] == 1.0
    c5 = cstar_on_gate(P_, Kg, gits, ["A", "B"], keep_mask=lambda g_: g_ not in ("g0", "g1"))
    assert c5[0] == max(x for x in GRID if int(round(x * 8)) == 2) and c5[3] == 8, c5


def _o_ecdf(gs):
    n = len(gs)
    return lambda x: sum(1 for g_ in gs if g_ <= x) / n


def _o_sha(it):
    return hashlib.sha256(str(it).encode("utf-8")).hexdigest()


def _o_curve(order, cc, cb, v):
    """Plain prefix sums over the ordered items -> (acc list, D_E list) on GRID."""
    import itertools
    n = len(order)
    pv = [0.0] + list(itertools.accumulate(v[i] for i in order))
    pc = [0.0] + list(itertools.accumulate(v[i] * cc[i] for i in order))
    pb = [0.0] + list(itertools.accumulate(v[i] * cb[i] for i in order))
    tot, tc, tb = pv[-1], pc[-1], pb[-1]
    acc, de = [], []
    for c_ in GRID:
        k = int(round(c_ * n))
        a_ = (pc[k] + tb - pb[k]) / tot
        e = (tot - pv[k]) / tot
        acc.append(a_)
        de.append(a_ - ((1 - e) * tc / tot + e * tb / tot))
    return acc, de


def _o_geometry(lay):
    """Independent geometry: AF centroids (graft prototypes + the one-cell TRAIN mean), K_0 per source, KM-U per seed, by direct
    FM.spherical_kmeans calls; GATE rows; the scorer by plain loops."""
    import json
    fx, tmp = lay.fx, lay.tmp
    man = json.load(open(os.path.join(tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    k0, _ = V.load_tree_cells(os.path.join(tmp, "res", "inputs", "k_cells_s0.tsv"), man["inputs"]["res/inputs/k_cells_s0.tsv"])
    z = np.load(os.path.join(tmp, "res", "inputs", "af_u_bundle_256.npz"))
    titems = [str(x) for x in z["train_item"]]
    classes = [str(x) for x in z["classes"]]
    sc_ = sorted(v for v in set(af.values()) if v.startswith(fx.single + ":"))[0]
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
        r_ = GC.FM.spherical_kmeans(Xt[idx], fx.ksrc[so], 0, max_iter=300)
        for j in range(fx.ksrc[so]):
            k_cent.append(("K0:%s:%03d" % (so, j), so, r_["centers"][j]))
    L = int(sum(fx.ksrc.values()))
    ku = {}
    for s in (0, 1, 2, 3, 4):
        C = GC.FM.spherical_kmeans(Xt, L, s, max_iter=300)["centers"]
        ku["KU%d" % s] = [("KU%d:%03d" % (s, j), C[j] / np.linalg.norm(C[j])) for j in range(L)]
    vm = os.path.join(tmp, "res", "inputs", "validation_merged")
    rows_h = ERC._o_csv(os.path.join(vm, "MAIN_union_routing_queries.csv"))
    srcs = {}
    for row in rows_h + ERC._o_csv(os.path.join(vm, "MAIN_union_routing_train_queries.csv")):
        srcs.setdefault(row["item_id"], set()).add(row["true_key"].split("/")[0])
    gcell = {row["item_id"]: row["leaf_id"] for row in rows_h if fx.side[row["item_id"]][1] == "GATE"}

    def cands(it, arm, cell):
        if arm == "AF-U":
            return [(sc_, af_cent[-1][1])] if cell == sc_ else [(lf, v) for lf, v in af_cent[:-1]]
        if arm == "K_0":
            return [(nm, v) for nm, so, v in k_cent if so in srcs[it]]
        return ku[arm]
    return dict(af=af, k0=k0, sc=sc_, ku=ku, cands=cands, gcell=gcell, gate=sorted(gcell), L=L)


def _o_gate(lay, geo):
    """GATE scores and ECDFs per arm, by plain loops."""
    sco, F = {}, {}
    for arm in ["AF-U", "K_0"] + list(KU):
        ms, os_ = [], []
        for it in geo["gate"]:
            m_, o_, _a, _b = ERC._o_scores(lay.fx.vec[it], geo["cands"](it, arm, geo["gcell"][it]))
            ms.append(m_)
            os_.append(o_)
        sco[arm] = (ms, os_)
        F[arm] = (_o_ecdf(ms), _o_ecdf(os_))
    return sco, F


def _tweak_gate(lay):
    """Plant GATE correctness so that c* is interior: the top 40% of GATE items by AF-U u: every model correct except the best
    single; the rest: only the best single correct. (GATE responses enter only c*; nothing else reads them.)"""
    import copy
    import json
    geo = _o_geometry(lay)
    sco, F = _o_gate(lay, geo)
    u = {it: min(F["AF-U"][0](sco["AF-U"][0][j]), F["AF-U"][1](sco["AF-U"][1][j])) for j, it in enumerate(geo["gate"])}
    srt = sorted(geo["gate"], key=lambda it: (-u[it], _o_sha(it)))
    top = set(srt[:int(0.4 * len(srt))])
    best = json.load(open(os.path.join(lay.tmp, "res", "scratch", "pol.json"), encoding="utf-8"))["best_single"]
    spec = copy.deepcopy(lay.fx.spec)
    for r_ in spec["responses"]:
        if r_["side"] == "GATE" and r_["item"] in u:
            r_["mf"] = None
            r_["c"] = int((r_["model"] != best) if r_["item"] in top else (r_["model"] == best))
    lay.fx.spec = spec
    return lay


def _oracle(lay, D):
    """Everything the run prints that decides or is predicted, recomputed by plain loops from the fixture's raw rows and vectors."""
    import json
    c = reg()
    fx = lay.fx
    geo = _o_geometry(lay)
    mu, val = U.o_key(fx.spec)
    gval = {}
    for r_ in fx.spec["responses"]:
        if r_["cv"] == "mc6" and r_["side"] == "GATE":
            gval.setdefault((r_["item"], r_["model"]), []).append(r_["mf"] if r_["mf"] is not None else r_["c"])
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]
    cells = {"AF-U": geo["af"], "K_0": geo["k0"]}
    for nm in KU:
        d = {}
        for it in tr + ev:
            if geo["af"].get(it) == UAR.NO_ROW:
                d[it] = UAR.NO_ROW
            else:
                d[it] = max(geo["ku"][nm], key=lambda t: (float(np.dot(fx.vec[it], t[1])), -int(t[0].split(":")[1])))[0]
        cells[nm] = d
    sco_g, F = _o_gate(lay, geo)
    u = {}
    for arm in cells:
        u[arm] = {}
        for it in ev:
            m_, o_, _a, _b = ERC._o_scores(fx.vec[it], geo["cands"](it, arm, geo["af"][it]))
            u[arm][it] = min(F[arm][0](m_), F[arm][1](o_))
    src = {D.items[k]: D.src[k] for k in D.E}
    orders = {(arm, sk): sorted([it for it in ev if sk == "all" or src[it] != c["excl"]], key=lambda it: (-u[arm][it], _o_sha(it)))
              for arm in cells for sk in ("all", "noex")}

    def areas(w, wv):
        best, pols = None, {}
        for arm in cells:
            b_, p_ = U.o_fit(tr, cells[arm], val, mu, w)
            best, pols[arm] = b_, p_
        cb = {i: val[(i, best)] for i in ev}
        out = {}
        for arm in cells:
            cc = {i: val[(i, pols[arm].get(cells[arm][i], best))] for i in ev}
            for sk in ("all", "noex"):
                out[(arm, sk)] = _o_curve(orders[(arm, sk)], cc, cb, wv)
        return out, best, pols
    pt, best0, pol0 = areas({i: 1 for i in tr}, {i: 1.0 for i in ev})
    rng = np.random.default_rng(c["seed"])
    two = []
    for _b in range(c["B"]):
        wt = V.draw_units(rng, D.train_units)
        w = {D.items[D.T[j]]: int(wt[j]) for j in range(len(D.T))}
        vv = V.draw_units(rng, D.eval_units)
        two.append(areas(w, {D.items[D.E[j]]: float(vv[j]) for j in range(len(D.E))})[0])
    rng = np.random.default_rng(c["seed"])
    iid = []
    cb0 = {i: val[(i, best0)] for i in ev}
    cc0 = {i: val[(i, pol0["AF-U"].get(geo["af"][i], best0))] for i in ev}
    for _b in range(c["B"]):
        cnt = np.bincount(rng.integers(0, len(ev), len(ev)), minlength=len(ev))
        iid.append(_o_curve(orders[("AF-U", "all")], cc0, cb0, {D.items[D.E[j]]: float(cnt[j]) for j in range(len(ev))}))

    def sd(xs):
        mb = sum(xs) / len(xs)
        return math.sqrt(sum((x - mb) ** 2 for x in xs) / (len(xs) - 1))

    def A(tr_, arm, sk):
        return sum(tr_[(arm, sk)][1]) / len(GRID)

    def km(tr_, sk):
        return sum(A(tr_, nm, sk) for nm in KU) / len(KU)

    def iv(fn):
        p_ = fn(pt)
        s_ = sd([fn(t) for t in two])
        return dict(point=p_, lo=p_ - 1.96 * s_, hi=p_ + 1.96 * s_, se2=s_)
    res = dict(AF=iv(lambda t: A(t, "AF-U", "all")), K0=iv(lambda t: A(t, "K_0", "all")), KU=iv(lambda t: km(t, "all")),
               diff=iv(lambda t: A(t, "AF-U", "all") - A(t, "K_0", "all")), ku_pts=[A(pt, nm, "all") for nm in KU],
               nAF=iv(lambda t: A(t, "AF-U", "noex")), nK0=A(pt, "K_0", "noex"), nKU=km(pt, "noex"),
               ndiff=iv(lambda t: A(t, "AF-U", "noex") - A(t, "K_0", "noex")))
    res["AF"]["se_iid"] = sd([sum(x[1]) / len(GRID) for x in iid])
    de = pt[("AF-U", "all")][1]
    jm = max(range(101), key=lambda j: (de[j], j))
    res["max"] = (de[jm], GRID[jm])
    dex = pt[("AF-U", "noex")][1]
    jx = max(range(101), key=lambda j: (dex[j], j))
    res["nmax"] = (dex[jx], GRID[jx])
    pol = json.load(open(os.path.join(lay.tmp, "res", "scratch", "pol.json"), encoding="utf-8"))
    gb = pol["best_single"]
    gmeta = {it["id"]: it["src"] for it in fx.spec["items"] if it["side"] == "GATE"}
    gcomp = [it for it in geo["gate"] if all(len(gval.get((it, m_), [])) == 1 for m_ in mu)]
    jpos = {it: j for j, it in enumerate(geo["gate"])}

    def cstar(keepf):
        its = [it for it in gcomp if keepf(it)]
        ug = {it: min(F["AF-U"][0](sco_g["AF-U"][0][jpos[it]]), F["AF-U"][1](sco_g["AF-U"][1][jpos[it]])) for it in its}
        od = sorted(its, key=lambda it: (-ug[it], _o_sha(it)))
        cc = {it: gval[(it, pol["tree_cell"].get(geo["gcell"][it]) or gb)][0] for it in its}
        cb = {it: gval[(it, gb)][0] for it in its}
        acc, _d = _o_curve(od, cc, cb, {it: 1.0 for it in its})
        j = max(range(101), key=lambda j_: (acc[j_], j_))
        return j, acc[j], len(its)
    jc, gacc, ngk = cstar(lambda it: True)
    jcx, _ga, _n = cstar(lambda it: gmeta[it] != c["excl"])
    res["cstar"] = dict(iv(lambda t: t[("AF-U", "all")][0][jc] - t[("AF-U", "all")][0][100]), c=GRID[jc], gate_acc=gacc, n=ngk)
    res["ncstar"] = dict(iv(lambda t: t[("AF-U", "noex")][0][jcx] - t[("AF-U", "noex")][0][100]), c=GRID[jcx])
    res["pw50"] = (pt[("AF-U", "all")][0][50], de[50], iv(lambda t: t[("AF-U", "all")][1][50]))
    res["n_noex"] = sum(1 for it in ev if src[it] != c["excl"])
    return res


def _close(a, b, tol=6e-6):
    return abs(a - b) < tol


def st_run_e2e(base, mk):
    base = _ready(base)
    lay = _tweak_gate(U.clone(base, mk()))
    text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, *FIXTURE_REG["out"].split("/"))
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (ESCALATION-CURVE; --run" % U.POOL)
    with U.mine(_me(), lay):
        o = _oracle(lay, res["D"])
    p_, lo, hi = U.num(out, r"EC1 \(DECIDING; the INTERVAL decides\): A_E\(AF-U\) = .*? = %s \| two-stage 95%% \[%s, %s\]" % (NUM, NUM, NUM))
    assert _close(p_, o["AF"]["point"]) and _close(lo, o["AF"]["lo"]) and _close(hi, o["AF"]["hi"]), (p_, lo, hi, o["AF"])
    assert abs(o["AF"]["point"]) > 1e-4, "A_E(AF-U) ~ 0 on the fixture: the readout would not discriminate"
    se2, sei = U.num(out, r"support EC1: n \d+, SE_2stage ([0-9.]+) \(registered upper bound 0.0036\), i.i.d. SE ([0-9.]+)")
    assert _close(se2, o["AF"]["se2"]) and _close(sei, o["AF"]["se_iid"]), (se2, sei, o["AF"])
    kp, klo, khi = U.num(out, r"DESCRIPTIVE: A_E\(K_0\) = %s \| two-stage 95%% \[%s, %s\]" % (NUM, NUM, NUM))
    assert _close(kp, o["K0"]["point"]) and _close(klo, o["K0"]["lo"]) and _close(khi, o["K0"]["hi"]), (kp, o["K0"])
    assert abs(o["AF"]["point"] - o["K0"]["point"]) > 1e-4, "AF-U and K_0 agree: the arms would not discriminate"
    up, ulo, uhi = U.num(out, r"A_E\(KM-U\) mean over seeds 0-4 = %s \| two-stage 95%% \[%s, %s\]" % (NUM, NUM, NUM))
    assert _close(up, o["KU"]["point"]) and _close(ulo, o["KU"]["lo"]) and _close(uhi, o["KU"]["hi"]), (up, o["KU"])
    seeds = U.num(out, r"per seed %s / %s / %s / %s / %s" % ((NUM,) * 5))
    assert all(_close(a_, b_) for a_, b_ in zip(seeds, o["ku_pts"])) and len(set("%.5f" % x for x in o["ku_pts"])) > 1, (seeds, o["ku_pts"])
    dp, dlo, dhi = U.num(out, r"DESCRIPTIVE: A_E\(AF-U\) - A_E\(K_0\) = %s \| two-stage 95%% \[%s, %s\]" % (NUM, NUM, NUM))
    assert _close(dp, o["diff"]["point"]) and _close(dlo, o["diff"]["lo"]) and _close(dhi, o["diff"]["hi"]), (dp, o["diff"])
    mx, mc = U.num(out, r"max_c D_E\(c\) \(AF-U, 0.01 grid, ties to the largest coverage\) = %s at coverage ([0-9.]+)" % NUM)
    assert _close(mx, o["max"][0]) and _close(mc, o["max"][1], 1e-9) and 0 < o["max"][1] < 1, (mx, mc, o["max"])
    cs, ga, cg, clo, chi = U.num(out, r"c\* = ([0-9.]+) \(argmax of GATE acc_u\(c\) ([0-9.]+) on \d+ key-complete GATE items, ties to the"
                                      r" largest coverage\); EVAL gain over no escalation acc_u\(c\*\) - acc_u\(1\) = %s \| two-stage 95%% \[%s, %s\]" % (NUM, NUM, NUM))
    assert _close(cs, o["cstar"]["c"], 1e-9) and _close(ga, o["cstar"]["gate_acc"]) and 0 < cs < 1, (cs, ga, o["cstar"])
    assert _close(cg, o["cstar"]["point"]) and _close(clo, o["cstar"]["lo"]) and _close(chi, o["cstar"]["hi"]) and abs(cg) > 1e-4, (cg, o["cstar"])
    blk = out.split("WITHOUT BBH (EC-R9; ")[1]
    nx = U.num(blk, r"^(\d+) EVAL items\): A_E\(AF-U\) %s \[%s, %s\]; A_E\(K_0\) %s; A_E\(KM-U\) %s; A_E\(AF-U\) - A_E\(K_0\) %s \[%s, %s\]; max_c D_E"
                    r" %s at ([0-9.]+); c\* ([0-9.]+) \(GATE without BBH\), EVAL gain %s \[%s, %s\]" % ((NUM,) * 9 + (NUM, NUM, NUM)))
    assert int(nx[0]) == o["n_noex"] < len(res["D"].E), (nx[0], o["n_noex"])
    exp = [o["nAF"]["point"], o["nAF"]["lo"], o["nAF"]["hi"], o["nK0"], o["nKU"], o["ndiff"]["point"], o["ndiff"]["lo"], o["ndiff"]["hi"],
           o["nmax"][0], o["nmax"][1], o["ncstar"]["c"], o["ncstar"]["point"], o["ncstar"]["lo"], o["ncstar"]["hi"]]
    for j, (a_, b_) in enumerate(zip(nx[1:], exp)):
        assert _close(a_, b_), ("noex field", j, a_, b_)
    assert abs(o["nAF"]["point"] - o["AF"]["point"]) > 1e-4 and o["ncstar"]["c"] != o["cstar"]["c"], "the subset must move the readouts"
    row = U.num(out, r"\n    0.50       ([0-9.]+)   \[[0-9.]+, [0-9.]+\]   %s   \[%s, %s\]" % (NUM, NUM, NUM))
    assert _close(row[0], o["pw50"][0]) and _close(row[1], o["pw50"][1]) and _close(row[2], o["pw50"][2]["lo"]) and _close(row[3], o["pw50"][2]["hi"])
    want = "ORDERING-INFORMATIVE" if lo > 0 else "ORDERING-HARMFUL" if hi < 0 else "UNDETERMINED"
    need(out, "  EC1 -> %s" % want, "FALSIFIER F-EC: %s" % ("FIRED" if want == "ORDERING-HARMFUL" else "NOT FIRED"),
         "PARITY (registered IDENTITY CHECK): the margin-only and OOS-only risk-coverage tables of AF-U and K_0 at the 0.05 grid (2 x 2"
         " x 21 points) -> REPRODUCED", "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]),
         "GATE key (EC-R7)", "R4 K_0 re-filing: 0 of")
    need(out, "PREDICTION P1 A_E(AF-U) +0.008 [+0.003, +0.013]: observed %+.5f -> %s" % (p_, "HELD" if PRED_AE[0] <= p_ <= PRED_AE[1] else "FAILED"))
    assert "OUTCOME written write-once" in text
    _t2, err2, _r = U.cap(_me(), run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


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
                      (dict(rc_outcome_sha="0" * 64), "ESCALATION-RC outcome"), (dict(ku_k=lay.common["ku_k"] + 1), "matched k"),
                      (dict(agree_min=1.0), "R4: AF filing agreement")):
        _t, err, _r = U.cap(_me(), run, lay, **over)
        assert err and msg in err, (over, err)
        _no_outcome(lay)
        assert not os.path.exists(_mk_path(lay)), "a pre-read refusal wrote the marker"
    real = UAR.us_fit

    def swapped(*a, **k):
        C, csrc, cloc, lab, f = real(*a, **k)
        j = [i for i in range(len(csrc)) if csrc[i] == "MMLU_PRO"][:2]
        C = C.copy()
        C[[j[0], j[1]]] = C[[j[1], j[0]]]
        return C, csrc, cloc, lab, f
    UAR.us_fit = swapped
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        UAR.us_fit = real
    assert err and "K_0 re-filed differs" in err, err
    _no_outcome(lay)
    real_gi = ERC.gate_items
    ERC.gate_items = lambda rows_h, side: ([], {}, {})
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        ERC.gate_items = real_gi
    assert err and "no GATE item" in err, err
    _no_outcome(lay)
    _t, err, _r = U.cap(_me(), run, lay, n_route=lay.common["n_route"] + 1)
    assert err and "[ECURVE-DENOM]" in err, err
    _no_outcome(lay)
    assert os.path.exists(_mk_path(lay))
    os.remove(_mk_path(lay))
    idn = lay.common["identity"]
    t_, err, _r = U.cap(_me(), run, lay, identity=dict(idn, af="0.0001"))
    assert err and "[ECURVE-IDENTITY]" in err, err
    assert "EC1 (DECIDING" not in t_ and "A_E(" not in t_ and "PARITY (" not in t_, "a new number was printed before the identity check"
    _no_outcome(lay)
    os.remove(_mk_path(lay))
    real_rb = V.run_boot

    def skewed(*a, **k):
        bt_ = real_rb(*a, **k)
        bt_["two"][:, 0, V.TREE] += 1e-6
        return bt_
    V.run_boot = skewed
    try:
        _t, err, _r = U.cap(_me(), run, lay)
    finally:
        V.run_boot = real_rb
    assert err and "[ECURVE-HOOK]" in err, err
    _no_outcome(lay)
    os.remove(_mk_path(lay))
    rcp = os.path.join(lay.tmp, *FIXTURE_REG["rc_outcome"].split("/"))
    txt = open(rcp, encoding="utf-8").read()
    blk = txt.split("RISK-COVERAGE AF-U ")[1]
    m_ = re.search(r"\n    0\.50       ([0-9.]+)   ", blk)
    old = m_.group(0)
    new = old.replace(m_.group(1), "%.5f" % (float(m_.group(1)) + 0.00001))
    i0 = txt.index("RISK-COVERAGE AF-U ")
    txt2 = txt[:i0] + txt[i0:].replace(old, new, 1)
    assert txt2 != txt
    with open(rcp, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt2)
    t_, err, _r = U.cap(_me(), run, lay, rc_outcome_sha=U.sha256_bytes(rcp))
    assert err and "[ECURVE-PARITY]" in err and "AF-U 0.50" in err, err
    assert "EC1 (DECIDING" not in t_ and "A_E(" not in t_, "a new number was printed before the parity check"
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
    assert ls[0].startswith("POOL %s (ESCALATION-CURVE; --dry-run" % U.POOL), ls[0]
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key read", "GATE (EC-R3):", "R4 K_0 re-filing: 0 of",
         "KM-U (EC-R1): ukm_fit k %d" % lay.common["ku_k"], "ESCALATION-RC outcome res/erc/outcome.txt sha256")
    for bad in ("EC1 (DECIDING", "A_E(", "IDENTITY:", "PARITY (", "PREDICTION", "GATE key (EC-R7)"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "ecurve")), "the dry-run wrote under res/ecurve"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (ESCALATION-CURVE; --dry-run"), L[0]
    need(t, "5907 EVAL items in 5404 components", "DEFF 1.302", "n_eff 4,537", "SE(A_E) <= 0.0036", "MDE80 0.0100", VERDICT_LINE,
         "B = 2000 two-stage replicates (default_rng(42))", "101 points", "KM-U k 123 seeds 0-4", "agreement floor 0.999",
         "GATE 2033 items", "without IFEVAL", "sha256 4dad8268248f63db", "best single 0.6049", "L24653-L24665", "calls 0")
    assert REG["out"] == "experiment_results/archv2/escalation_curve/outcome.txt" and REG["uar_policy_sha"].startswith("8d68018c")


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "EC1 words by value incl. ends at 0, rule 8, F-EC, P1-P4 bands inclusive, Brier, required lines", "plain"),
         ("units", "ecdf, combined u, sha tie-break, curve vs rc_curve / weighted loops / subset, rounding, argmax ties, parser, c*", "plain"),
         ("run_e2e", "--run end to end (GATE planted for an interior c*): A_E per arm with intervals, max, c*, without-member vs an"
                     " independent oracle; EC1 by hand; parity; write-once", "base"),
         ("refusals", "pool, manifest, policy sha, RC sha, KU k, R4, K_0 re-filing, GATE empty, DENOM, IDENTITY, HOOK, PARITY, marker", "base"),
         ("dry_run", "--dry-run: POOL first, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "units": st_units, "run_e2e": st_run_e2e, "refusals": st_refusals, "dry_run": st_dry_run,
       "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    return U.run_selftest(TAG, CASES, _FN, HIT, only=only, quiet=quiet, base=base)


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "S", "", ""),
    ("X01 EC1 INFORMATIVE at lo >= 0 (boundary)", "S", '    if st["lo"] > 0:' + NL + '        return "ORDERING-INFORMATIVE"', '    if st["lo"] >= 0:' + NL + '        return "ORDERING-INFORMATIVE"'),
    ("X02 EC1 HARMFUL at hi <= 0 (boundary)", "S", '    if st["hi"] < 0:' + NL + '        return "ORDERING-HARMFUL"', '    if st["hi"] <= 0:' + NL + '        return "ORDERING-HARMFUL"'),
    ("X03 F-EC fires on any non-INFORMATIVE", "S", '    if v == "ORDERING-HARMFUL":' + NL + '        hit("FEC.FIRED")', '    if v != "ORDERING-INFORMATIVE":' + NL + '        hit("FEC.FIRED")'),
    ("X04 combined u = max (min<->max)", "S", "    return np.minimum(Fm(m), Fo(o))", "    return np.maximum(Fm(m), Fo(o))"),
    ("X05 ECDF left-continuous (<)", "S", 'side="right") / float(n)', 'side="left") / float(n)'),
    ("X06 order ascending (least confident kept)", "S", "    return np.lexsort((rank, -np.asarray(u, dtype=np.float64)))", "    return np.lexsort((rank, np.asarray(u, dtype=np.float64)))"),
    ("X07 ties by item order, not sha256", "S", '    r[np.argsort(np.array(h), kind="stable")] = np.arange(len(h))', "    r[:] = np.arange(len(h))"),
    ("X08 keep count floor (not round)", "S", "    return np.array([int(round(c_ * n)) for c_ in grid], dtype=np.int64)", "    return np.array([int(c_ * n) for c_ in grid], dtype=np.int64)"),
    ("X09 random line at the nominal share (unweighted)", "S", "    e = (tot - S_v[k]) / tot", "    e = 1.0 - k / float(n)"),
    ("X10 D_E without the random line (acc minus acc(cells))", "S", "    de = acc - ((1.0 - e) * (tc / tot) + e * (tb / tot))", "    de = acc - tc / tot"),
    ("X11 A_E = the 0.05-grid mean (wrong grid)", "S", "        return float(np.mean(tr[(o_, sk)][1]))", "        return float(np.mean(np.asarray(tr[(o_, sk)][1])[list(G05)]))"),
    ("X12 ECDFs from EVAL (wrong split side)", "S", '    sc_all = eval_scores(say, P_, ev_all)' + NL,
     '    sc_all = eval_scores(say, P_, ev_all)' + NL + '    P_["F"] = {arm: (ecdf(sc_all[arm][0]), ecdf(sc_all[arm][1])) for arm in sc_all}' + NL),
    ("X13 K_0 ordered with AF-U's ECDFs (wrong arm)", "S", '        Fm, Fo = P_["F"][arm]' + NL + '        orders[("comb", arm)]', '        Fm, Fo = P_["F"]["AF-U"]' + NL + '        orders[("comb", arm)]'),
    ("X14 replicate policy not re-fitted (uncapped fork)", "S", "        Pp = V.fit(D_, wt)", "        Pp = V.fit(D_, V.train_full(D_))"),
    ("X15 interval z 1.645 (script-side)", "S", "        return U.interval(fn(pt), [fn(t) for t in two], [fn(t) for t in iid], NE)", "        return U.interval(fn(pt), [fn(t) for t in two], [fn(t) for t in iid], NE, z=1.645)"),
    ("X16 interval from the i.i.d. replicates", "S", "        return U.interval(fn(pt), [fn(t) for t in two], [fn(t) for t in iid], NE)", "        return U.interval(fn(pt), [fn(t) for t in iid], [fn(t) for t in iid], NE)"),
    ("X17 diff not paired (K_0 at its point)", "S", '         "diff": stat(lambda t: area(t, ("comb", "AF-U"), "all") - area(t, ("comb", "K_0"), "all"))}',
     '         "diff": stat(lambda t: area(t, ("comb", "AF-U"), "all") - area(pt, ("comb", "K_0"), "all"))}'),
    ("X18 KM-U = seed 0 only", "S", '        return lambda t: float(np.mean([area(t, ("comb", nm), sk) for nm in KU]))', '        return lambda t: float(area(t, ("comb", "KU0"), sk))'),
    ("X19 KM-U candidates = all but the last centroid", "S", "def all_cands(n, k):" + NL + "    return [tuple(range(k))] * n", "def all_cands(n, k):" + NL + "    return [tuple(range(max(1, k - 1)))] * n"),
    ("X20 KM-U at k - 1", "S", '    cents = ku_fit(Xt, L, c["ku_seeds"])', '    cents = ku_fit(Xt, L - 1, c["ku_seeds"])'),
    ("X21 argmax ties to the smallest coverage", "S", "    return int(len(x) - 1 - np.argmax(x[::-1]))", "    return int(np.argmax(x))"),
    ("X22 c* chosen on EVAL (wrong split side)", "S", '    cs = dict(stat(gain_at(jc, "all")), c=cst, gate_acc=gacc)', '    jc = argmax_last(pt[main][0])' + NL + '    cs = dict(stat(gain_at(jc, "all")), c=GRID[jc], gate_acc=gacc)'),
    ("X23 c* gain against coverage 0 (wrong reference)", "S", "        return lambda t: float(t[mm][0][j_] - t[mm][0][100])", "        return lambda t: float(t[mm][0][j_] - t[mm][0][0])"),
    ("X24 GATE c* cell model = best single always", "S", '    cc = np.array([Kg[i][pol["tree_cell"].get(P_["gcell"][i]) or gb] for i in its], dtype=np.float64)', '    cc = np.array([Kg[i][gb] for i in its], dtype=np.float64)'),
    ("X25 without-member subset ignored (all items)", "S", '    keep = np.array([D.src[k] != c["excl"] for k in D.E], dtype=bool)', '    keep = np.ones(len(D.E), dtype=bool)'),
    ("X26 without-member c* from the full GATE", "S", 'keep_mask=lambda it: gk["meta"][it][1] != c["excl"])', 'keep_mask=None)'),
    ("X27 max D_E read on acc_u (wrong curve)", "S", "    jm = argmax_last(pt[main][1])", "    jm = argmax_last(pt[main][0])"),
    ("X28 prediction bands exclusive", "C", '    return bool(band[0] <= x <= band[1])', '    return bool(band[0] < x < band[1])'),
    ("X29 P3 coverage read against the value band", "S", '    ok = U.in_band(st["max_c"], PRED_MAXC)', '    ok = U.in_band(st["max_c"], PRED_MAX)'),
    ("X30 Brier on a fixed outcome", "S", "U.brier(PROB_EC1, v)", 'U.brier(PROB_EC1, "UNDETERMINED")'),
    ("X31 verdict line of record dropped", "S", 'MDE80 %.5f (registered 0.0100); verdict line of record: %s', 'MDE80 %.5f (registered 0.0100); %s'),
    ("X32 F-EC NOT FIRED line dropped (skip path)", "S", '        say("FALSIFIER F-EC: NOT FIRED (EC1 %s; F-EC fires iff EC1 ORDERING-HARMFUL)" % v)', '        pass'),
    ("X33 rule-8 line dropped on the refuted path", "S", '        say("  rule 8: ORDERING-INFORMATIVE is refuted at the planned n (lower bound %+.5f <= 0)" % a["lo"])', '        pass'),
    ("X34 parity check skipped", "S", "    if bad:" + NL + '        hit("REFUSE.PARITY")', "    if False:" + NL + '        hit("REFUSE.PARITY")'),
    ("X35 RC outcome sha not checked", "S", '    if sh != c["rc_outcome_sha"]:', '    if False:'),
    ("X36 identity refusal removed", "S", "    if not ok:" + NL + '        hit("REFUSE.IDENTITY")', "    if False:" + NL + '        hit("REFUSE.IDENTITY")'),
    ("X37 hook check skipped", "S", 'if chk.shape != ref.shape or not np.allclose(chk, ref, atol=1e-12, rtol=0):', 'if False:'),
    ("X38 KU k check removed", "S", '    if L != int(c["ku_k"]):', '    if False:'),
    ("X39 pre-read write-once check removed", "S", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X40 GATE-empty guard removed", "S", '    if not its:' + NL + '        hit("REFUSE.GATE_EMPTY")', '    if False:' + NL + '        hit("REFUSE.GATE_EMPTY")'),
    ("X41 R4 agreement floor not enforced", "S", '    if share < c["agree_min"]:', '    if share < 0:'),
    ("X42 K_0 re-filing check skipped", "S", '    if sc["kdiff"]:', '    if False:'),
    ("X43 GATE key read on the TRAIN side (wrong side)", "S", '        meta = V.side_items(tw, cfg.cv_u, "GATE")', '        meta = V.side_items(tw, cfg.cv_u, "TRAIN")'),
    ("X44 KM-U GATE scores against negated centroids", "S", "        out[nm] = ERC.cand_scores(Xg, all_cands(len(its), len(C)), C)", "        out[nm] = ERC.cand_scores(Xg, all_cands(len(its), len(C)), -C)"),
    ("X45 pointwise D_E interval from acc (wrong curve)", "S", "        d_ = U.interval(float(pt[main][1][j]), [t[main][1][j] for t in two], [t[main][1][j] for t in iid], NE)",
     "        d_ = U.interval(float(pt[main][1][j]), [t[main][0][j] for t in two], [t[main][1][j] for t in iid], NE)"),
    ("X46 subset keep counts on the full EVAL size (denominator changed)", "S", "    k = keep_counts(n, grid)" + NL + "    acc = ", "    k = keep_counts(len(cc), grid)" + NL + "    acc = "),
    ("X47 subset orders ignore the subset (all items)", "S", "        return orders[o_] if sub is None else orders[o_][sub[orders[o_]]]", "        return orders[o_]"),
    ("C46 identity: arm digits not compared", "C", 'ok = all(got[k] == idn[k] for k in ("best", "tsrc", "af", "k0")) and', 'ok = True and'),
    ("C47 i.i.d. draws halved", "C", '        yield np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64)', '        yield np.bincount(rng.integers(0, NE, NE // 2), minlength=NE).astype(np.float64)'),
    ("C48 interval z 1.645 (common)", "C", 'lo=pt - z * se2, hi=pt + z * se2', 'lo=pt - 1.645 * se2, hi=pt + 1.645 * se2'),
)


if __name__ == "__main__":
    sys.exit(main())
