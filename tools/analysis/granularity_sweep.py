"""granularity_sweep.py: GRANULARITY-SWEEP -- on the content-closed v2 union split, does the routing gain of per-source k-means
cells, merged by Ward within source to about 25 / 50 / 100 / 200 / 400 cells, peak at an interior granularity chosen on GATE, with
model-profile information (R2_int) and per-cell support beside and the AF-U tree cut to the counts it can reach?
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU reader of keyed correctness.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-06 (before any code or call) — GRANULARITY-SWEEP: on the content-closed v2 union
  split, is there a best granularity for cell-level capability profiles: ..." (L24828-L24840, _as_of 9bff7e39, parent 4c764a1e):
  GS1 (THE ONE DECIDING CRITERION), FAILS (rule 8), DESCRIPTIVE, ESTIMATION-NOISE DISCLOSURE, Support (a)-(g), P1-P6, F-GS,
  WILL-NOT-SHOW. Data objects and IDENTITY PRECONDITION as TREE-BACKOFF (L24814-L24826). Registrar's record L24808-L24812.
  Results record docs/agents/results/GRANULARITY-SWEEP.json. Every arm is [SC] (filed through the source); none is label-free.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or anywhere with --data-root <main checkout>; never beside a
construction: --dry-run and --run are POOL READERS, rule 7; check `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` exits 1):
  0. python tools/analysis/granularity_sweep.py --selftest    # synthetic fixtures under E:/TaxoArena_tmp (scratch_dir); NO DB of record
     python tools/analysis/granularity_sweep.py --mutants     # the mutant table below, re-run (each must make the selftest fail)
  1. python tools/analysis/granularity_sweep.py --dry-run     # POOL line first; pins; denominators; AF-U profile; the allocation
                                                              #   table; the planned fits and cost; NO key (TRAIN, GATE or EVAL)
                                                              #   read, NO statistic, nothing written
  2. python tools/analysis/granularity_sweep.py --run         # LAUNCH DETACHED (Start-Process; CPU about 1.5-2.5 h: the k-means
       fits (5 seeds x KW at 400 + KF at 25 / 50 / 100 / 200, n_init 5), the K0 re-derivation, B 2,000 two-stage replicates each
       re-fitting the TRAIN 3PL for R2_int); TRAIN key, GATE key, ONE EVAL key read (marker first); outcome WRITE-ONCE:
       experiment_results/archv2/granularity_sweep/granularity_sweep_outcome.txt (+ granularity_sweep.READ_STARTED). Never
       committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_granularity_sweep with SHA256SUMS.txt.
  Then the adversarial-reviewer (numbers), the registrar.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; outcome and marker absent (write-once); (2) union_route_common.prepare: the B0-2 pool check, AF-U state (D-8,
  one-cell evidence), the inputs manifest (sha256-lf 53021e26...) with every file re-hashed, the AF and K0..K4 cells, the frozen
  TRAIN policy (sha256 8d68018c...); [GSWEEP-PROFILE] AF-U's per-source leaf counts and one-cell member equal the registered
  profile; (3) the AF-U bundle (the K_s fit slice), the routing rows, the vectors (checked equal to the bundle's), the GATE items;
  [GSWEEP-K0] K0 re-derived with union_af_route's own K_s code (us_fit / k_cells, seed 0) equals k_cells_s0.tsv on every item
  (the slice, vectors, sources and filing are K_s's); (4) the cells: KW (k-means at the top allocation, Ward within source, cut to
  every coarser allocation), KF (k-means at each grid k), TC (AF-U cut best-first), the KW GATE cells; (5) the TRAIN key;
  [GSWEEP-TRAIN] the scored TRAIN counts per source equal the registered ones and floor(count / 5) the registered caps; the GATE
  key (gen view) [GSWEEP-GATE] 1,944 key-complete GATE items; (6) the marker, THE EVAL KEY READ (union_route_common.read_views),
  [GSWEEP-DENOM] 5,907 / 5,404, [B3] the frozen policy re-fitted; (7) the TRAIN 3PL (resp_structure_common.irt_point) and
  v2_declared_cells.run_boot (B 2,000, default_rng(42)) with the R2_int hook; [G3] B + 2 fit checks; [GSWEEP-IDENTITY] C1 +2.67pp
  [+1.46, +3.89], G_AF +1.52pp [+0.14, +2.91], best single 0.6049, TRUE source 0.6150, AF-U 0.6201, K0 0.6271;
  [GSWEEP-TC-IDENTITY] TC at AF-U's own count equals AF-U's leaf arm; (8) k* on GATE, GS1, F-GS, descriptive lines, support,
  predictions; the outcome written mode "x" (a view whose sha changed during the read writes *_VOID.txt instead).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  GS-R1  ALLOCATION (registered "fixed now"): the one-cell source (IFEVAL) is one cell at every k; the other k - 1 cells go to the
         five other sources in proportion to AF-U's leaf profile (MMLU_PRO_LB 69, BBH 36, MATH 10, MUSR 3, GPQA 4 of 122) by largest
         remainder (quota q_s = (k - 1) w_s / 122; floors; the remaining cells to the largest fractional parts, ties by the
         registered source order MMLU_PRO_LB, BBH, MATH, MUSR, GPQA); then max(1, .) per source; then min(., cap_s), cap_s =
         floor(scored TRAIN count / 5) (GPQA 11, MUSR 90, MATH 154, BBH 694, MMLU_PRO_LB 1,351); capped surplus is not re-allocated.
         Realised: 25 -> 25, 50 -> 50, 100 -> 100, 123 -> 123 (= AF-U's profile), 200 -> 200, 400 -> 398 (GPQA 13 -> 11).
  GS-R2  K-MEANS: "spherical k-means (n_init 5, seed s; intent_transfer_s0.skmeans)" = construction_arms.skm_best (blob 5d08a5df,
         unchanged): intent_transfer_s0.skmeans restarts r = 0..4 seeded s x 16 + r, the best by the sum of max-cos; fitted per
         source on the AF-U bundle's TRAIN rows of that source (the slice K_s was fitted on: 256-d unit rows, MC-EXCLUDE'd, a row's
         source = its declared class's source). Cell centroid = the renormalised mean of the cell's fit rows (the fit's own centre
         where a cell holds no row).
  GS-R3  FILING (KW, KF; mirrored, as K_s in UNION-AF-ROUTE R3 / B-4): every routed item (TRAIN, EVAL, GATE) goes to the nearest
         centroid (argmax cosine) among the centroids of its declared source(s) read from its routing rows
         (union_af_route.file_by_source); an item with no routing row keeps <no-routing-row> (TRAIN only).
  GS-R4  KW NESTING: per source and seed, scipy Ward linkage (Euclidean) on the top-allocation centroids, cut to the coarser
         allocation by replaying the first n - k_s merges (construction_arms.fit_ward on the centroids); an item's KW cell at k = the
         group of its top cell. KW at the top k IS the k-means at the top allocation (no merge); KF at the top k is the same fit
         (reused, printed). KW is also cut at AF-U's own count 123 (descriptive: TC minus KW at 123).
  GS-R5  TC: per source, start from the source root; while the cut holds fewer nodes than the source's allocation and an internal
         node remains, replace the internal node with the largest TRAIN count (TRAIN items of af_cells.tsv on the TRAIN side whose
         leaf lies under it; ties by the smaller node id) by its children; the realised count can exceed the allocation by the
         children of the last expansion (printed). Capped at the source's own leaves (the loop ends when no internal node is
         left). The one-cell member stays one cell. EVAL items are filed by AF-U's flatLeaf cell (the cell of record), then up to
         the cut; an item whose AF leaf belongs to another source's tree is counted as a cross-source filing. Available at the grid k
         not above AF-U's 123 leaves and at 123 itself; at 123 the cut is the whole tree and TC must equal AF-U's leaf arm.
  GS-R6  G(k) = routed EVAL accuracy minus the best single (V.fit, unchanged: argmax over the sorted roster, a cell with TRAIN
         mass < 1 backs off to the best single), each arm one extra grouping of G14's reader. mean_s over the five seeds for KW / KF.
  GS-R7  k* = the grid k (25, 50, 100, 200, 400; never 123) maximising mean_s G_KW(k) on the key-complete GATE items, the policy
         fitted on the full TRAIN (= run_boot's P0); a GATE cell no scored item reaches gets the best single; ties to the smaller k
         (the first strict maximum in ascending k).
  GS-R8  INTERVAL: run_boot's two-stage replicates (TRAIN units re-drawn and every policy re-fitted; EVAL components within stratum;
         default_rng(42)); the SEEDS are resampled jointly with the units: replicate b draws five seed indices with replacement
         from a second stream default_rng(20261006) (one (B, 5) draw, in replicate order), and every seed-mean quantity of the
         replicate (G_KW(k), D_lo, D_hi, F-GS, TC - KW, R2_int) averages over the SAME drawn seeds (paired across k). The 95%
         interval = point +- 1.96 SE_2stage (G14's reader form), SE_2stage = SD (ddof 1) of the replicates; percentile beside.
         i.i.d. SE: run_boot's i.i.d. replicates (policy fixed, EVAL items i.i.d., seeds fixed) -> DEFF = Var_2stage / Var_iid,
         n_eff = 5,907 / DEFF, MDE80 = 2.80 SE_2stage (one contrast), 3.21 SE_2stage (both jointly; Support (e)).
  GS-R9  GS1 = INTERIOR-MAX iff k* in {50, 100, 200} AND D_lo = G_KW(k*) - G_KW(25) > 0 AND its lo > 0 AND D_hi = G_KW(k*) -
         G_KW(400) > 0 AND its lo > 0; NOT-SHOWN otherwise, with the sub-reason (EDGE: k* at an end; else which D's point or lower
         bound is <= 0). Rule 8: INTERIOR-MAX REFUTED iff NOT-SHOWN. F-GS fires iff G_KW(25) - G_KW(100) > 0 AND its lo > 0.
  GS-R10 R2_int(k) = RESP-PROFILE-INFO's out-of-sample interaction R^2 (resp_profile_info.arm_r2 unchanged: RP-R1 cell means
         shrunk by n_c / (n_c + 20), RP-R2) on the 3PL residuals of resp_structure_common.irt_point; the interval from the same
         run_boot (the hook re-fits the TRAIN 3PL, the EVAL items and every cell mean per replicate, as RESP-PROFILE-INFO's RP2 hook;
         non-converged replicate fits counted, not dropped). Descriptive.
  GS-R11 SUPPORT per arm and k: over the arm's cells holding at least one scored item: TRAIN and EVAL items per cell (median, p10,
         numpy linear), the share of cells and of EVAL items in cells whose scored TRAIN count reaches n* = ceil(1.311 x 2.8^2 x
         0.30 / 0.10^2) = ceil(308.34) = 309, the share of cells whose policy falls back (TRAIN mass < 1); KW / KF: means over seeds.
  GS-R12 TRAIN in-sample G(k): the same full-TRAIN policy scored on the scored TRAIN items (the overfit gap beside EVAL).
  GS-R13 Predictions "X [lo, hi]" HELD iff lo <= X <= hi (closed); outcome probabilities by the multi-outcome Brier sum.
  Not applicable (stated): no judge verdict enters (keyed correctness): no wrong(established) count, no tie conventions A / B; no
  call cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; union_af_route's fixture with a one-cell member, built through escalation_rc's layout steps (UNION-AF-ROUTE
--build-inputs and --run executed on v2_declared_cells' sealed fixture views; stubbed text / vector / side readers and pool check);
temp on E: via scratch_dir; opens NO DB of record). Cases:
  constants     the REAL registered constants: grid, interior, profile, one-cell, caps (= floor(train counts / 5)), the allocation
                table at 25..400 (hand values, 398 at 400), n* 309, Support numbers, prediction bands, B 2,000, seed 42, seed draws
  alloc         allocation against an independent loop oracle and hand cases (cap hit, surplus not re-allocated, min 1, ties)
  tc_ward       the best-first cut on a hand tree (largest count first, tie to the smaller id, overshoot, cap at own leaves); the
                Ward nesting against scipy cut_tree (independent cut) and nestedness across k
  branches      GS1 by value: INTERIOR-MAX; EDGE at 25 and at 400; each D's point <= 0 and lower bound exactly 0 / < 0; F-GS fired /
                not (lo exactly 0); rule 8; the seed-joint interval against hand replicates; TWO NAIVE-INTERVAL CASES that decide
                wrongly (a unit-only interval with the seeds fixed, and the i.i.d. interval, both put D's lower bound above 0 where
                the registered two-stage seed-joint interval does not: NOT-SHOWN); k* ties to the smaller k and never 123; P1-P6
                bands inclusive at both ends, the Brier values; every required line (SKIP / NOT-SCOREABLE paths included)
  run_present   --run end to end on the fixture whose responses carry a strong per-stratum winner (coarse cells merge strata, the
                finest cells hold a few TRAIN items each): every arm's G printed to 5 dp, the GATE curve, k*, D_lo, D_hi (point, SE,
                interval) and F-GS equal an INDEPENDENT oracle (plain-loop allocation, skmeans restarts, filing, scipy cut_tree
                Ward cut, plain-loop policy fits on the fixture's raw rows, the same unit and seed draws); GS1 == INTERIOR-MAX by
                the hand rule; the outcome equals the printed text; a second --run refused, the outcome unchanged
  run_absent    --run on the NULL fixture (every response Bernoulli(0.6), no model-by-item structure): GS1 NOT-SHOWN with the
                sub-reason, F-GS NOT FIRED, values against the same oracle
  refusals      pool check (POOL line still first), manifest pin, policy sha, profile, K0 re-derivation, TRAIN counts (marker not
                written), GATE count, DENOM, IDENTITY (an arm digit; a C1 / G_AF end), B3, TC identity, B / seed, marker present;
                no outcome written by any of them
  dry_run       POOL line first; no key read, no statistic, nothing written; the REAL constants' lines
  branch_cover  every print / refusal branch registered in BRANCHES executed
MUTANTS (--mutants; each edits the code ABOVE the SELFTEST marker in memory, re-executes it and runs the selftest on layouts built
by the unedited code, one process per mutant, 4 at a time, temp under E:/TaxoArena_tmp; KILLED iff the selftest fails; X00 control
must survive). 2026-10-06, code identical to the committed blob but for this docstring paragraph: 52 of 52 KILLED, control SURVIVED.
  GS1 clauses X01-X04, X47 (EDGE removed; lo >= 0; point clause; D_hi never checked = first site only; interior = whole grid) KILLED
  wrong arm / population X05, X06, X29, X45 (D_hi vs 25; D_lo vs 400; G vs placebo; D_lo on NON_BBH)                         KILLED
  k* X07-X09 (ties to the larger k; argmin = min<->max; chosen on EVAL = wrong split side)                                 KILLED
  interval X10-X12, X30, X49 (seeds fixed; i.i.d. as two-stage; seed 0 only; sign; seed draws on the unit seed)            KILLED
  F-GS / rule 8 X13-X16 (lo >= 0; reversed; NOT FIRED line dropped; 'not refuted' line dropped = skip paths)               KILLED
  allocation X17-X20 (no min 1; cap ignored; remainder to the smallest; one-cell not subtracted)                          KILLED
  cells X21-X24, X51, X52 (Ward -> truncation; filing ignores the source; centroids not renormalised; n_init 1; KW seed 0
  only; KF at the top allocation)                                                                                          KILLED
  tree cut X25-X27 (smallest first = min<->max; tie to the larger id; counts from EVAL = wrong split side)                 KILLED
  GATE X28, X46, X48 (no-mass cell -> model 0; no best-single baseline; empty GATE refusal removed = zero sites)           KILLED
  refusals X31-X38, X44, X50 (identity, TC identity, TRAIN counts, caps clause, GATE count, profile, K0, write-once, TC
  availability, G3)                                                                                                        KILLED
  support / predictions X39-X43 (TRAIN > n* boundary; P1 first band; P2 fixed Brier; P4 direction; P6 skip line)          KILLED
DRY-RUN OF RECORD (2026-10-06, worktree, --data-root the main checkout, busy.ps1 exit 1 = free; rc 0; nothing written): POOL first;
  B0-2 pool check rc 0; AF-U commit 1075b506, 123 leaves (MMLU_PRO_LB 69, BBH 36, MATH 10, MUSR 3, IFEVAL 1 one-cell, GPQA 4) = the
  registered profile; inputs manifest 53021e26... with 18 AF-U files and 11 inputs equal to their pins; frozen policy 8d68018c...;
  allocation 25 / 50 / 100 / 123 / 200 / 398 (GPQA capped at 400); K_s fit slice 12,334 bundle TRAIN rows (MMLU_PRO_LB 6,977, BBH
  3,474, MATH 773, MUSR 454, IFEVAL 325, GPQA 331: GPQA's cells are fitted on 331 rows while its cap is floor(57 scored / 5) = 11,
  as registered; its per-cell scored support is printed); 18,502 routed TRAIN / EVAL items (vectors equal to the bundle's on 18,473);
  2,033 GATE items with a routing row; TRAIN 12,351 side items, 11,841 structurally key-complete (= the registration); eval view
  NOT opened. CPU: one real-size skmeans restart (k 225, n 6,977, 256-d) 0.3 s on synthetic rows; the bootstrap (B 2,000, each
  re-fitting the TRAIN 3PL and 59 arms' cell means) dominates: about 1.5-3 h in all, LAUNCH --run DETACHED.
NOT DONE HERE: the real --run (the operator's, after READY; detached); no Kotlin / Gradle change.
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

import math          # noqa: E402
import types         # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
from collections import Counter   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scratch_dir   # noqa: E402,F401  (tempfile -> E:/TaxoArena_tmp/py_<pid>_..., removed at exit)


def _blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


# the registered instrument's imports, blob-pinned (git blobs, LF) at parent 4c764a1e; each pins its own dependencies
PINS = (("union_route_common.py", "d54739769d38a3a402e2deaab9e45109cd86de4e"),
        ("union_cells_io.py", "92a04543b9c75eae5f37a76ae86eb189a190a9bd"),
        ("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"),
        ("v2_declared_cells.py", "f0f568057995b5d0231da6e3d0d48755a7cf8386"),
        ("resp_profile_info.py", "1817ec8ad607bb3b3d0abfb0116b5b2c27dd2d02"),
        ("construction_arms.py", "5d08a5dfb8c0cb0b5330512259b4732aa4af2dd2"))
for _name, _pin in PINS:
    if _blob_lf(os.path.join(HERE, _name)) != _pin:
        raise SystemExit("[GSWEEP] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_name, _blob_lf(os.path.join(HERE, _name)), _pin))
import union_route_common as U    # noqa: E402  (pins escalation_rc, union_cells_io, union_af_route)
import construction_arms as CA    # noqa: E402  (skm_best, fit_ward; pins intent_transfer_s0 and its other inputs)
import resp_profile_info as RPI   # noqa: E402  (arm_r2: R2_int unchanged; its resp_structure_common: the 3PL)

RSC = RPI.RSC
V, UAR, ERC, GC, GB = U.V, U.UAR, U.ERC, U.GC, U.GB

TAG = "[GSWEEP]"
TEST_ID = "GRANULARITY-SWEEP"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-06 (before any code or call) — GRANULARITY-SWEEP: on the content-closed'
            ' v2 union split, is there a best granularity for cell-level capability profiles: ..." L24828-L24840 (_as_of 9bff7e39)')
OUT = "experiment_results/archv2/granularity_sweep"
REG = dict(U.COMMON, out=OUT + "/granularity_sweep_outcome.txt", marker=OUT + "/granularity_sweep.READ_STARTED",
           grid=(25, 50, 100, 200, 400), interior=(50, 100, 200), k_lo=25, k_hi=400, k_mid=100, k_own=123,
           profile={"MMLU_PRO_LB": 69, "BBH": 36, "MATH": 10, "MUSR": 3, "GPQA": 4}, one_cell=("IFEVAL",),
           caps={"MMLU_PRO_LB": 1351, "BBH": 694, "MATH": 154, "MUSR": 90, "GPQA": 11}, cap_div=5,
           train_counts={"MMLU_PRO": 6759, "BBH": 3473, "MATH": 773, "MUSR": 454, "IFEVAL": 325, "GPQA": 57},
           n_gate_key=1944, n_star=309, kish_plan=1.311, disc=0.30, delta=0.10, seed_draw=20261006, nseeds=5,
           tc_k=(25, 50, 100, 123))
FIXTURE_REG = dict(out="res/gs/outcome.txt", marker="res/gs/READ_STARTED", grid=(3, 6, 11, 41, 300), interior=(6, 11, 41), k_lo=3,
                   k_hi=300, cap_div=2, k_mid=11, k_own=6, profile={"MMLU_PRO": 4, "MATH": 1}, one_cell=("BBH",), tc_k=(3, 6))
_REG = [REG]


def reg():
    return _REG[0]


SEEDS = (0, 1, 2, 3, 4)
SUPPORT = dict(deff=1.847, se=0.00620, se_seed=0.00158, n_eff=3198, mde1=0.0174, mde2=0.0199, gate_se=0.0105)
VERDICT_LINE = ("GS1 DESCRIPTIVE-ONLY at the prediction (the predicted D_lo and D_hi, +0.4pp each, lie 0.4pp from the bar, short of the"
                " joint MDE80 1.99pp); GS1 is scored as registered and NOT-SHOWN is then the expected word (never 'there is no best"
                " granularity')")
PRED_P1 = ((0.005, 0.025), (0.008, 0.028), (0.009, 0.029), (0.007, 0.027), (0.003, 0.025))   # by grid position (25 .. 400)
PRED_P1_TXT = ("+1.5pp [+0.5, +2.5]", "+1.8pp [+0.8, +2.8]", "+1.9pp [+0.9, +2.9]", "+1.7pp [+0.7, +2.7]", "+1.5pp [+0.3, +2.5]")
PROB_P2 = (("INTERIOR", 0.60), ("EDGE", 0.40))
PROB_GS1 = (("INTERIOR-MAX", 0.07), ("NOT-SHOWN", 0.93))
PRED_P4 = (0.045, 0.065)
PROB_P4B = (("LOWER", 0.60), ("NOT-LOWER", 0.40))
PRED_P5_LO = (0.65, 1.00)
PRED_P5_HI = (0.00, 0.15)
PRED_P6 = (-0.015, 0.009)
HIT = Counter()


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def pp(x):
    return U.pp(x)


def stratum(src):
    """AF-U's member source -> the view's stratum source (MMLU_PRO_LB is the MMLU_PRO stratum)."""
    return src[:-3] if src.endswith("_LB") else src


def order_of(src):
    """The registered source order (union_af_route REG["sources"]: MMLU_PRO_LB, BBH, MATH, MUSR, IFEVAL, GPQA): the largest-remainder
    tie order and the centroid stacking order (the filing tie order, as K_s)."""
    so = tuple(UAR.reg()["sources"])
    return (so.index(src), src) if src in so else (len(so), src)


# ── GS-R1: the allocation ───────────────────────────────────────────────────────────────────────────────────────────────
def allocate(k, profile, one_cell, caps):
    """-> (allocation {source: cells}, quotas {source: q}); one-cell sources get 1; the rest by largest remainder, min 1, capped."""
    n = k - len(one_cell)
    W = float(sum(profile.values()))
    q = {s: n * profile[s] / W for s in profile}
    fl = {s: int(math.floor(q[s])) for s in profile}
    rem = n - sum(fl.values())
    for s in sorted(profile, key=lambda s_: (-(q[s_] - fl[s_]), order_of(s_)))[:max(0, rem)]:
        fl[s] += 1
    out = {s: min(max(1, fl[s]), int(caps[s])) for s in profile}
    for s in one_cell:
        out[s] = 1
    return out, q


def alloc_text(a):
    return ", ".join("%s %d" % (s, a[s]) for s in sorted(a, key=order_of)) + " (total %d)" % sum(a.values())


# ── GS-R2..GS-R4: k-means, centroids, filing, Ward nesting ──────────────────────────────────────────────────────────────
def fit_centroids(Xs, k, seed):
    """GS-R2: construction_arms.skm_best (n_init 5) -> filing centroids (renormalised member means; the fit's centre if empty)."""
    lab, Cm = CA.skm_best(Xs, k, seed)
    C = np.array(Cm, dtype=np.float64, copy=True)
    for j in range(k):
        m = lab == j
        if m.any():
            s = Xs[m].sum(axis=0)
            C[j] = s / np.linalg.norm(s)
    return C


def ward_groups(C, kk):
    """GS-R4: top-centroid index -> group index at kk groups (Ward on the centroids, the first n - kk merges replayed)."""
    n = len(C)
    if kk > n:
        refuse("[GSWEEP-NEST] a coarser allocation %d exceeds the top allocation %d (the cells could not be nested)" % (kk, n))
    if kk == n:
        return np.arange(n, dtype=np.int64)
    if kk == 1:
        return np.zeros(n, dtype=np.int64)
    return np.asarray(CA.fit_ward(C, kk)["lab"], dtype=np.int64)


def source_fit(Xt, tsrc, alloc, seed):
    """-> {source: centroids (k_s, d)} for every allocated source (the one-cell source fitted at k = 1)."""
    out = {}
    for so in sorted(alloc, key=order_of):
        m = tsrc == so
        k = int(alloc[so])
        if k < 1 or k > int(m.sum()):
            refuse("source %s: k %d is outside 1..%d TRAIN rows" % (so, k, int(m.sum())))
        out[so] = fit_centroids(Xt[m], k, seed)
    return out


def stack(cents):
    srcs = sorted(cents, key=order_of)
    C = np.vstack([cents[s] for s in srcs])
    csrc = np.array(sum([[s] * len(cents[s]) for s in srcs], []))
    cloc = np.concatenate([np.arange(len(cents[s])) for s in srcs])
    return C, csrc, cloc


def file_all(items, vec, srcs, C, csrc):
    """GS-R3: {item: global centroid index} by union_af_route.file_by_source (nearest among the item's declared source(s))."""
    return {it: UAR.file_by_source(vec[it], srcs[it], C, csrc) for it in items}


# ── GS-R5: the tree cut ─────────────────────────────────────────────────────────────────────────────────────────────────
def load_trees(single):
    """{source: dict(root, children {node: [child]}, leaves set)} from each split member's LAST snapshot (node ids "SRC:id")."""
    c = UAR.reg()
    trees = {}
    for m, src in c["members"]:
        if src in single:
            continue
        snap = GB.last_snapshot(UAR.P("%s/%s/seed_42/dag_snapshots.jsonl" % (c["afu"], m)))
        ch, roots, leaves = {}, [], set()
        for n in snap["nodes"]:
            u = "%s:%s" % (src, n["id"])
            ps = n.get("parentIds") or []
            if len(ps) > 1:
                refuse("node %s has %d parents (the cut needs a tree)" % (u, len(ps)))
            if ps:
                ch.setdefault("%s:%s" % (src, ps[0]), []).append(u)
            else:
                roots.append(u)
            if n.get("isLeaf"):
                leaves.add(u)
        if len(roots) != 1:
            refuse("member %s has %d roots" % (m, len(roots)))
        trees[src] = dict(root=roots[0], children={k: sorted(v) for k, v in ch.items()}, leaves=leaves)
    return trees


def tc_cut(tree, counts, alloc):
    """GS-R5: best-first expansion -> (leaf -> cut node, the cut node list). counts: {node: TRAIN count of its subtree}."""
    cut = [tree["root"]]
    while len(cut) < alloc:
        inner = [u for u in cut if tree["children"].get(u)]
        if not inner:
            break
        u = sorted(inner, key=lambda x: (-counts.get(x, 0), x))[0]
        i = cut.index(u)
        cut = cut[:i] + list(tree["children"][u]) + cut[i + 1:]
    up = {}
    for top in cut:
        stack_ = [top]
        while stack_:
            x = stack_.pop()
            kids = tree["children"].get(x) or []
            if not kids:
                up[x] = top
            stack_.extend(kids)
    return up, sorted(cut)


def tc_train_counts(af, side):
    """GS-R5: {AF cell: number of TRAIN-side items of af_cells.tsv filed to it} (structure only, before any key)."""
    return Counter(v for it, v in af.items() if side.get(it, (None, None))[1] == "TRAIN")


def subtree_counts(tree, leaf_count):
    out = {}

    def rec(u):
        kids = tree["children"].get(u) or []
        out[u] = leaf_count.get(u, 0) if not kids else sum(rec(x) for x in kids)
        return out[u]
    rec(tree["root"])
    return out


# ── the cells of every arm ──────────────────────────────────────────────────────────────────────────────────────────────
def arm_name(kind, k, s=None):
    return "%s%03d" % (kind, k) + ("_s%d" % s if s is not None else "")


def build_cells(say, P_):
    """KW / KF / TC cells over every AF-cell item, and the KW GATE cells -> dict(x={arm: {item: cell}}, gate={arm: {item: cell}},
    info)."""
    c = reg()
    NO = UAR.NO_ROW
    af, vec, srcs, Xt, tsrc = P_["af"], P_["vec"], P_["srcs"], P_["Xt"], P_["tsrc"]
    routed = sorted(i for i, v in af.items() if v != NO)
    allocs = P_["allocs"]
    ktop = c["k_hi"]
    kw_ks = sorted(set(c["grid"]) | {c["k_own"]})
    x, gate, info = {}, {}, dict(kw={}, kf={}, tc={})
    for s in SEEDS:
        cents = source_fit(Xt, tsrc, allocs[ktop], s)
        C, csrc, cloc = stack(cents)
        g_all = file_all(routed, vec, srcs, C, csrc)
        g_gate = file_all(P_["gits"], P_["gvec"], P_["gsrc"], C, csrc)
        for k in kw_ks:
            grp = {so: ward_groups(cents[so], allocs[k][so]) for so in cents}
            nm = arm_name("KW", k, s)

            def cell(gi):
                so = csrc[gi]
                return "%s:%s:%03d" % (nm, so, grp[so][cloc[gi]])
            x[nm] = {it: (NO if af[it] == NO else cell(g_all[it])) for it in af}
            gate[nm] = {it: cell(g_gate[it]) for it in P_["gits"]}
            info["kw"][nm] = len(set(v for v in x[nm].values() if v != NO))
        x[arm_name("KF", ktop, s)] = {it: v.replace(arm_name("KW", ktop, s), arm_name("KF", ktop, s)) for it, v in x[arm_name("KW", ktop, s)].items()}
        for k in c["grid"]:
            if k == ktop:
                continue
            cf = source_fit(Xt, tsrc, allocs[k], s)
            Cf, csf, clf = stack(cf)
            gf = file_all(routed, vec, srcs, Cf, csf)
            nm = arm_name("KF", k, s)
            x[nm] = {it: (NO if af[it] == NO else "%s:%s:%03d" % (nm, csf[gf[it]], clf[gf[it]])) for it in af}
        say("  seed %d: KW at the top allocation (%d cells) cut by Ward to %s; KF fitted at %s (KF at %d = KW's top fit)" % (
            s, sum(allocs[ktop].values()), ", ".join(str(k) for k in kw_ks if k != ktop), ", ".join(str(k) for k in c["grid"] if k != ktop), ktop))
    # TC
    trees, single = P_["trees"], P_["single"]
    lc = tc_train_counts(af, P_["side"])
    own = sum(len(t["leaves"]) for t in trees.values()) + len(single)
    tcs = [k for k in sorted(set(c["grid"]) | {c["k_own"]}) if k <= own]
    leaf_src = {lf: so for so, t in trees.items() for lf in t["leaves"]}
    for k in tcs:
        up = {}
        realised = {}
        for so, t in trees.items():
            cnt = subtree_counts(t, lc)
            u, cut = tc_cut(t, cnt, allocs[k][so])
            up.update(u)
            realised[so] = len(cut)
        nm = arm_name("TC", k)
        x[nm] = {it: ("%s:%s" % (nm, up[v]) if v in up else v) for it, v in af.items()}
        info["tc"][k] = dict(realised=realised, total=sum(realised.values()) + len(single))
    if tuple(tcs) != tuple(c["tc_k"]):
        refuse("[GSWEEP-TC] the tree cut is available at %s, not the registered %s (AF-U has %d leaves)" % (tcs, list(c["tc_k"]), own))
    info["tc_ks"], info["own"], info["leaf_src"] = tcs, own, leaf_src
    return dict(x=x, gate=gate, info=info)


# ── data before the key ─────────────────────────────────────────────────────────────────────────────────────────────────
def files():
    return [os.path.abspath(__file__)] + [os.path.join(HERE, n) for n, _ in PINS]


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)): %d EVAL items in %d CK-CLOSE components (Kish %.3f); x %d KW seeds (paired across k);"
        " GATE %d key-complete items (k* only); TRAIN scored per source %s" % (
            c["n_route"], c["comp_route"], c["kish_plan"], c["nseeds"], c["n_gate_key"],
            ", ".join("%s %d" % kv for kv in sorted(c["train_counts"].items()))))
    say("SUPPORT (registered): DEFF %.3f (ROUTE-SOURCE-NULL D_S two-stage, transported), seed term %.3fpp (UNION-AF-ROUTE spread_K"
        " 0.58pp / 2.326 x sqrt(2/5)), SE(D) %.3fpp, n_eff %d, MDE80 one contrast %.2fpp, both jointly %.2fpp; GATE SE of G about"
        " %.2fpp; %s" % (SUPPORT["deff"], 100 * SUPPORT["se_seed"], 100 * SUPPORT["se"], SUPPORT["n_eff"], 100 * SUPPORT["mde1"],
                         100 * SUPPORT["mde2"], 100 * SUPPORT["gate_se"], VERDICT_LINE))
    say("PLANNED: grid k %s (interior %s; k* on GATE over the grid only); KW, KF seeds %s; TC at %s; B = %d two-stage replicates"
        " (default_rng(%d)), seeds resampled jointly (default_rng(%d)); n* = ceil(%.3f x 2.8^2 x %.2f / %.2f^2) = %d" % (
            list(c["grid"]), list(c["interior"]), list(SEEDS), list(c["tc_k"]), c["B"], c["seed"], c["seed_draw"], c["kish_plan"],
            c["disc"], c["delta"], c["n_star"]))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(c["identity"])))


def prepare(say):
    c = reg()
    S = U.prepare(say, c, refuse, hit)
    prof = {s: int(S["ksrc"][s]) for s in S["ksrc"] if s not in S["single"]}
    if prof != dict(c["profile"]) or tuple(sorted(S["single"])) != tuple(sorted(c["one_cell"])):
        hit("REFUSE.PROFILE")
        refuse("[GSWEEP-PROFILE] AF-U's leaf profile %s with one-cell member(s) %s is not the registered %s with %s" % (
            prof, sorted(S["single"]), dict(c["profile"]), list(c["one_cell"])))
    say("  AF-U profile (the allocation weights): %s; one-cell: %s (= the registration)" % (
        ", ".join("%s %d" % (s, prof[s]) for s in sorted(prof, key=order_of)), ", ".join(sorted(S["single"]))))
    allocs = {}
    for k in sorted(set(c["grid"]) | {c["k_own"]}):
        allocs[k], q = allocate(k, c["profile"], c["one_cell"], c["caps"])
        capped = [s for s in c["profile"] if allocs[k][s] < max(1, int(math.floor(q[s])))]
        say("  ALLOCATION k %d: %s%s" % (k, alloc_text(allocs[k]), "; capped: %s" % ", ".join(sorted(capped)) if capped else ""))
    for k in c["grid"]:
        if any(allocs[k][s] > allocs[c["k_hi"]][s] for s in allocs[k]):
            refuse("[GSWEEP-NEST] the allocation at %d exceeds the top allocation in a source" % k)
    u = UAR.reg()
    ip = UAR.input_paths()
    b, _meta = GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    classes = [str(x) for x in b["classes"]]
    Xt, yt, _Xe, _ye = UAR.unit_bundle(b)
    tsrc = np.array([UAR.src_of(classes[i]) for i in yt])
    titems = [str(x) for x in b["train_item"]]
    say("  K_s fit slice (the AF-U bundle's TRAIN rows): %d rows; per source %s" % (
        len(titems), ", ".join("%s %d" % (s, int((tsrc == s).sum())) for s in sorted(set(tsrc.tolist()), key=order_of))))
    side, _sm = UAR._SIDES[0]()
    val = UAR.afu_paths(S["single"])[1]
    rows_h, rows_t = ERC.item_rows(ip["merged"] if S["single"] else val)
    srcs = UAR.item_sources(rows_h + rows_t)
    af = S["af"]
    routed = sorted(i for i, v in af.items() if v != UAR.NO_ROW)
    vec = ERC.get_vectors(routed)
    nov = [i for i in routed if i not in vec or i not in srcs]
    if nov:
        refuse("%d routed item(s) have no vector or no declared source (first %s)" % (len(nov), nov[:3]))
    nb = ERC.check_vectors_vs_bundle(vec, b)
    gits, _gcell, gsrc = ERC.gate_items(rows_h, side)
    if not gits:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: k* is undefined")
    gvec = ERC.get_vectors(gits)
    nog = [i for i in gits if i not in gvec]
    if nog:
        refuse("%d GATE item(s) have no vector (first %s)" % (len(nog), nog[:3]))
    say("  routed TRAIN / EVAL items %d (vectors equal to the bundle's on %d); GATE items with a routing row %d" % (len(routed), nb, len(gits)))
    trees = load_trees(S["single"])
    return dict(S, allocs=allocs, b=b, Xt=Xt, tsrc=tsrc, titems=titems, side=side, srcs=srcs, vec=vec, gits=gits, gsrc=gsrc,
                gvec=gvec, trees=trees, rows_h=rows_h)


def k0_rederive(say, P_):
    """[GSWEEP-K0]: union_af_route's own K_s code (seed 0) re-derives k_cells_s0.tsv on every item."""
    kc, ki = UAR.k_cells(0, P_["Xt"], P_["tsrc"], P_["titems"], P_["ksrc"], UAR.reg()["sources"], P_["vec"], P_["srcs"], P_["af"])
    k0 = P_["kx"]["K0"]
    diff = sorted(i for i in k0 if kc.get(i) != k0[i])
    say("  K0 RE-DERIVATION (union_af_route.k_cells, seed 0): %d of %d items differ from k_cells_s0.tsv (must be 0)" % (len(diff), len(k0)))
    if diff or set(kc) != set(k0):
        hit("REFUSE.K0")
        refuse("[GSWEEP-K0] K0 re-derived differs from k_cells_s0.tsv on %d item(s) (first %s): not K_s's slice / vectors / filing" % (
            len(diff), diff[:3]))


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, files())
    denominators(say)
    P_ = prepare(say)
    c = reg()
    nfit = len(SEEDS) * len(c["grid"])
    say("  COST (planned): %d k-means fits (n_init 5 each: KW at %d and KF at %s, seeds %s); the K0 re-derivation (one K_s fit);"
        " %d extra groupings in run_boot (KW %d, KF %d, TC up to %d); B %d replicates, each re-fitting the TRAIN 3PL (R2_int); about"
        " 1.5-2.5 h CPU single-threaded: LAUNCH --run DETACHED and poll" % (
            nfit, c["k_hi"], [k for k in c["grid"] if k != c["k_hi"]], list(SEEDS),
            len(SEEDS) * (len(c["grid"]) + 1 + len(c["grid"])) + len(c["tc_k"]), len(SEEDS) * (len(c["grid"]) + 1),
            len(SEEDS) * len(c["grid"]), len(c["tc_k"]), c["B"]))
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    U.read_views(cfg, say, True, P_["af"], P_["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no key read (TRAIN, GATE or EVAL); no k-means fit; no statistic printed.")
    hit("DRY.DONE")
    return 0


def gate_key(cfg, say, models, gits):
    """The GATE key (gen view, response_lite, the reader's variant rule, MATH-FIX overlay; escalation_curve EC-R7's read)."""
    rule = cfg.pre.get("variant_rule")
    tw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view(GATE)", say)
    try:
        meta = V.side_items(tw, cfg.cv_u, "GATE")
        want = {i: meta[i] for i in gits if i in meta}
        tw.unseal("%s: the GATE key for k* only, after the TRAIN key and before the eval view" % TEST_ID)
        K, kst = V.read_key(tw, "response_lite", cfg.cv_u, models, want, True, rule)
    finally:
        tw.close()
    if not V.after_sha(cfg.gen_path, gsha, "gen_view(GATE)", say):
        refuse("[PIN] the gen view's sha moved during the GATE key read")
    comp = V.complete_items(K, models)
    say("  GATE key: %d GATE items with a routing row in the view; key-complete %d (cells single %d, multi %d unusable %d)" % (
        len(want), len(comp), kst["single"], kst["multi"], kst["multi_unusable"]))
    return K, comp


# ── statistics ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def seed_draws(B, seed, nseeds):
    return np.random.default_rng(seed).integers(0, nseeds, size=(B, nseeds))


def seed_stat(pt, two, iid, terms, SD, n):
    """GS-R8: a seed-mean linear quantity. terms: per seed a list of (arm column, coefficient) (the same for every seed if the arm is
    seed-free). pt [NA], two / iid [B, NA] -> U.interval (point = mean over the seeds; replicate b = mean over the drawn seeds
    SD[b]; i.i.d. = mean over all seeds, policy fixed)."""
    ns = len(terms)

    def val(row, sel):
        return float(np.mean([sum(cf * row[a] for a, cf in terms[s]) for s in sel]))
    point = val(pt, range(ns))
    t2 = [val(two[b], SD[b]) for b in range(len(two))]
    ti = [val(iid[b], range(ns)) for b in range(len(iid))]
    return U.interval(point, t2, ti, n)


def gs1_verdict(kstar, interior, dlo, dhi):
    """GS-R9 -> (word, sub-reason)."""
    if kstar not in interior:
        return "NOT-SHOWN", "EDGE: k* = %d is an end of the grid" % kstar
    bad = []
    for nm, d in (("D_lo", dlo), ("D_hi", dhi)):
        if not d["point"] > 0:
            bad.append("%s's point %+.5f <= 0" % (nm, d["point"]))
        elif not d["lo"] > 0:
            bad.append("%s's 95%% lower bound %+.5f <= 0" % (nm, d["lo"]))
    if bad:
        return "NOT-SHOWN", "; ".join(bad)
    return "INTERIOR-MAX", "k* = %d interior; D_lo and D_hi > 0 with lower bounds > 0" % kstar


def kstar_of(gate_mean, grid):
    """GS-R7: the first strict maximum in ascending k (ties to the smaller k)."""
    best = None
    for k in sorted(grid):
        if best is None or gate_mean[k] > gate_mean[best]:
            best = k
    return best


def gate_gain(P0, D, nm, gcells, Kg, comp):
    """mean over the key-complete GATE items of acc(routed by the full-TRAIN policy) - acc(best single)."""
    keys = {k: j for j, k in enumerate(D.xkeys[nm])}
    pol = P0.pol["x:" + nm]
    gb = P0.gb
    r, b_ = [], []
    for it in comp:
        j = keys.get(gcells[it])
        q = pol[j] if j is not None else -1
        q = gb if q < 0 else q
        r.append(Kg[it][D.models[q]])
        b_.append(Kg[it][D.models[gb]])
    return float(np.mean(r)) - float(np.mean(b_))


def support_of(D, P0, nm, n_star):
    g = D.groupings["x:" + nm][0]
    ng = D.groupings["x:" + nm][1]
    ntr = np.bincount(g[D.T], minlength=ng)
    nev = np.bincount(g[D.E], minlength=ng)
    m = (ntr + nev) > 0
    pol = P0.pol["x:" + nm]
    big = ntr >= n_star
    return dict(cells=int(m.sum()), tr_med=float(np.percentile(ntr[m], 50)), tr_p10=float(np.percentile(ntr[m], 10)),
                ev_med=float(np.percentile(nev[m], 50)), ev_p10=float(np.percentile(nev[m], 10)),
                share_cells=float((big & m).sum()) / float(m.sum()), share_eval=float(nev[big].sum()) / float(nev.sum()),
                fallback=float(((pol < 0) & m).sum()) / float(m.sum()))


def train_gain(D, P0, nm):
    g = D.groupings["x:" + nm][0]
    p = P0.pol["x:" + nm][g[D.T]]
    AT = D.A[D.T]
    r = np.arange(len(D.T))
    return float(AT[r, np.where(p < 0, P0.gb, p)].mean() - AT[:, P0.gb].mean())


def r2_hook(D, I, arms, rec):
    """GS-R10: per replicate the TRAIN 3PL (multiplicities), the EVAL items (theta fixed) and every cell mean re-fitted."""
    T, E = D.T, D.E
    cT, cE, YT, YE = I["cT"], I["cE"], I["YT"], I["YE"]

    def hook(D_, wt, v):
        w = wt[T].astype(np.float64)
        RSC.assert_train(D_, T[w > 0])
        sel = w > 0
        ft = RSC.fit_train(YT[sel], cT[sel], w=w[sel], theta=I["theta"], alpha=I["aT"][sel], b=I["bT"][sel])
        rec["fits"] += 1
        rec["nonconv"] += int(not ft["converged"])
        aE, bE, _i, _m = RSC.fit_items(YE, cE, ft["theta"], alpha=I["aE"], b=I["bE"])
        eT = RSC.resid(YT[sel], RSC.prob(ft["theta"], ft["alpha"], ft["b"], cT[sel]))
        eE = RSC.resid(YE, RSC.prob(ft["theta"], aE, bE, cE))
        vv = np.asarray(v, dtype=np.float64)
        rec["r2"].append({nm: RPI.arm_r2(eT, eE, g[T][sel], g[E], ng, w=w[sel], v=vv) for nm, (g, ng) in arms.items()})
    return hook


def analyze(D, bt, cells, Kg, comp, I, rec, n_comp):
    c = reg()
    grid, kw_ks = list(c["grid"]), sorted(set(c["grid"]) | {c["k_own"]})
    B = int(bt["B"])
    SD = seed_draws(B, c["seed_draw"], len(SEEDS))
    subs = [n for n, _ in D.subsets]
    col = lambda nm: U.karm(D, nm)     # noqa: E731
    P0 = bt["P0"]

    def st_sub(sub, terms):
        j = subs.index(sub)
        return seed_stat(bt["point"][j], bt["two"][:, j, :], bt["iid"][:, j, :], terms, SD, int(D.subsets[j][1].sum()))

    def g_terms(kind, k):
        if kind == "TC":
            return [[(col(arm_name("TC", k)), 1.0), (V.BS, -1.0)]] * len(SEEDS)
        return [[(col(arm_name(kind, k, s)), 1.0), (V.BS, -1.0)] for s in SEEDS]

    def d_terms(kind_a, ka, kind_b, kb):
        ta, tb = g_terms(kind_a, ka), g_terms(kind_b, kb)
        return [[ta[s][0], (tb[s][0][0], -1.0)] for s in range(len(SEEDS))]
    st = dict(n=D.n_eval, comp=n_comp, kish=U.kish_eval(D), n_train=D.n_train, B=B, n_gate=len(comp), grid=grid, kw_ks=kw_ks)
    st["G"] = {("KW", k): st_sub("ALL", g_terms("KW", k)) for k in kw_ks}
    st["G"].update({("KF", k): st_sub("ALL", g_terms("KF", k)) for k in grid})
    st["tc_ks"] = cells["info"]["tc_ks"]
    st["G"].update({("TC", k): st_sub("ALL", g_terms("TC", k)) for k in st["tc_ks"]})
    st["Gs"] = {k: [float(bt["point"][0, col(arm_name("KW", k, s))] - bt["point"][0, V.BS]) for s in SEEDS] for k in kw_ks}
    st["gate"] = {k: [gate_gain(P0, D, arm_name("KW", k, s), cells["gate"][arm_name("KW", k, s)], Kg, comp) for s in SEEDS] for k in grid}
    st["gate_mean"] = {k: float(np.mean(st["gate"][k])) for k in grid}
    st["kstar"] = kstar_of(st["gate_mean"], grid)
    ks = st["kstar"]
    st["dlo"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_lo"]))
    st["dhi"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_hi"]))
    st["fgs"] = st_sub("ALL", d_terms("KW", c["k_lo"], "KW", c["k_mid"]))
    st["eval_argmax"] = max(grid, key=lambda k: (st["G"][("KW", k)]["point"], -k))
    st["tc_kw"] = {k: st_sub("ALL", d_terms("TC", k, "KW", k)) for k in st["tc_ks"] if k in kw_ks}
    st["per_src"] = {}
    for sub in subs:
        if sub.startswith("SRC:") or sub == "NON_BBH":
            st["per_src"][sub] = {k: st_sub(sub, g_terms("KW", k))["point"] for k in grid}
    st["nobbh_d"] = (st_sub("NON_BBH", d_terms("KW", ks, "KW", c["k_lo"])), st_sub("NON_BBH", d_terms("KW", ks, "KW", c["k_hi"])))
    st["train_g"] = {("KW", k): float(np.mean([train_gain(D, P0, arm_name("KW", k, s)) for s in SEEDS])) for k in kw_ks}
    st["train_g"].update({("KF", k): float(np.mean([train_gain(D, P0, arm_name("KF", k, s)) for s in SEEDS])) for k in grid})
    st["train_g"].update({("TC", k): train_gain(D, P0, arm_name("TC", k)) for k in st["tc_ks"]})
    st["sup"] = {}
    for kind, kk in (("KW", kw_ks), ("KF", grid)):
        for k in kk:
            rows = [support_of(D, P0, arm_name(kind, k, s), c["n_star"]) for s in SEEDS]
            st["sup"][(kind, k)] = {f: float(np.mean([r[f] for r in rows])) for f in rows[0]}
    for k in st["tc_ks"]:
        st["sup"][("TC", k)] = support_of(D, P0, arm_name("TC", k), c["n_star"])
    # R2_int: points and seed-joint replicates
    arms = rec["arms"]
    pt_r2 = {nm: RPI.arm_r2(I["eT"], I["eE"], g[D.T], g[D.E], ng) for nm, (g, ng) in arms.items()}
    reps = rec["r2"]

    def r2_stat(kind, k):
        names = [arm_name("TC", k)] * len(SEEDS) if kind == "TC" else [arm_name(kind, k, s) for s in SEEDS]
        point = float(np.mean([pt_r2[n_] for n_ in names]))
        two = [float(np.mean([reps[b][names[j]] for j in SD[b]])) for b in range(len(reps))]
        se = math.sqrt(V._var(two)) if len(two) > 1 else float("nan")
        return dict(point=point, se2=se, lo=point - 1.96 * se, hi=point + 1.96 * se, seeds=[pt_r2[n_] for n_ in names])
    st["R2"] = {("KW", k): r2_stat("KW", k) for k in kw_ks}
    st["R2"].update({("KF", k): r2_stat("KF", k) for k in grid})
    st["R2"].update({("TC", k): r2_stat("TC", k) for k in st["tc_ks"]})
    st["r2_nonconv"], st["r2_fits"] = rec["nonconv"], rec["fits"]
    # TC cross-source filings (scored EVAL items whose AF leaf lies in another source's tree)
    ls = cells["info"]["leaf_src"]
    st["cross"] = sum(1 for k in D.E if D.items[k] in cells["af"] and cells["af"][D.items[k]] in ls
                      and stratum(ls[cells["af"][D.items[k]]]) != D.src[k])
    st["tc_info"] = cells["info"]["tc"]
    st["own"] = cells["info"]["own"]
    return st


# ── the printed readout (every branch registered) ───────────────────────────────────────────────────────────────────────
def iv(x):
    return "%s (%+.5f) | two-stage 95%% [%s, %s] (%+.5f, %+.5f) | percentile [%s, %s]" % (
        pp(x["point"]), x["point"], pp(x["lo"]), pp(x["hi"]), x["lo"], x["hi"], pp(x["pct"][0]), pp(x["pct"][1]))


def gs_lines(st):
    """Every line of the GS1 block (the outcome prints them verbatim); -> (lines, words)."""
    c = reg()
    L = []
    grid, ks = st["grid"], st["kstar"]
    L.append("=== GRANULARITY-SWEEP (%s) ===" % REG_TEXT)
    L.append("DENOMINATOR: %d EVAL items in %d CK-CLOSE components (Kish mean cluster size %.3f; Support (a) 5907 / 5404, Kish 1.311);"
             " x %d KW seeds, paired across k; TRAIN %d scored items (the policy-fit set of G14's reader); GATE %d key-complete items"
             " (k* only); B %d two-stage replicates, seeds resampled jointly" % (st["n"], st["comp"], st["kish"], len(SEEDS), st["n_train"],
                                                                                st["n_gate"], st["B"]))
    L.append("LIKE WITH LIKE: KW (per-source k-means at %d + Ward within source; nested across k) [SC] DECIDING | KF (per-source k-means"
             " at each k; not nested) [SC] | TC (AF-U cut best-first; nested) [SC]; every arm files through the source (known at query"
             " time); none is label-free" % c["k_hi"])
    L.append("GATE CURVE (k* selection; full-TRAIN policy; mean over seeds of G_KW on GATE): %s" % " | ".join(
        "k %d %s (seeds %s)" % (k, pp(st["gate_mean"][k]), "/".join(pp(x) for x in st["gate"][k])) for k in grid))
    L.append("k* = %d (argmax of mean_s G_KW(k) on GATE over the grid %s, ties to the smaller k; registered GATE SE of G about 1.05pp:"
             " the choice is noisy)" % (ks, grid))
    for k in st["kw_ks"]:
        g = st["G"][("KW", k)]
        L.append("G_KW(%d) EVAL = %s; seeds %s%s" % (k, iv(g), " / ".join(pp(x) for x in st["Gs"][k]),
                                                    "" if k in grid else " (descriptive: AF-U's own count, not in the grid)"))
    dlo, dhi = st["dlo"], st["dhi"]
    L.append("GS1 D_lo = G_KW(k*=%d) - G_KW(%d) = %s" % (ks, c["k_lo"], iv(dlo)))
    L.append("GS1 D_hi = G_KW(k*=%d) - G_KW(%d) = %s" % (ks, c["k_hi"], iv(dhi)))
    for nm, d in (("D_lo", dlo), ("D_hi", dhi)):
        L.append("  support %s: n %d, SE_2stage %.5f (registered %.5f), i.i.d. SE %.5f, DEFF %.3f (registered %.3f, transported), n_eff"
                 " %.0f (registered %d), MDE80 one contrast %s (registered %s), both jointly %s (registered %s)" % (
                     nm, d["n"], d["se2"], SUPPORT["se"], d["se_iid"], d["deff"], SUPPORT["deff"], d["n_eff"], SUPPORT["n_eff"],
                     pp(2.80 * d["se2"]), pp(SUPPORT["mde1"]), pp(3.21 * d["se2"]), pp(SUPPORT["mde2"])))
    L.append("  verdict line of record: %s" % VERDICT_LINE)
    word, why = gs1_verdict(ks, c["interior"], dlo, dhi)
    if word == "INTERIOR-MAX":
        hit("GS1.INTERIOR")
        L.append("GS1 -> INTERIOR-MAX (%s)" % why)
    elif ks not in c["interior"]:
        hit("GS1.EDGE")
        L.append("GS1 -> NOT-SHOWN (%s)" % why)
    else:
        hit("GS1.BOUND")
        L.append("GS1 -> NOT-SHOWN (%s)" % why)
    if word == "NOT-SHOWN":
        hit("RULE8.REFUTED")
        L.append("RULE 8: INTERIOR-MAX is REFUTED at the planned n (%s)" % why)
    else:
        hit("RULE8.NOT")
        L.append("RULE 8: INTERIOR-MAX is not refuted (k* interior and both lower bounds > 0)")
    f = st["fgs"]
    fired = bool(f["point"] > 0 and f["lo"] > 0)
    L.append("F-GS: G_KW(%d) - G_KW(%d) = %s" % (c["k_lo"], c["k_mid"], iv(f)))
    if fired:
        hit("FGS.FIRED")
        L.append("FALSIFIER F-GS: FIRES (coarse cells route better than cells at the tree's own scale: the union routing gain is read"
                 " as a coarse-cell property and every 123-cell routing number as over-split)")
    else:
        hit("FGS.NOT")
        L.append("FALSIFIER F-GS: NOT FIRED (F-GS fires iff G_KW(%d) - G_KW(%d) > 0 with its 95%% lower bound > 0)" % (c["k_lo"], c["k_mid"]))
    L.append("DESCRIPTIVE: EVAL-argmax k of mean_s G_KW over the grid = %d (post hoc, no interval)" % st["eval_argmax"])
    for k in grid:
        L.append("DESCRIPTIVE: G_KF(%d) EVAL = %s" % (k, iv(st["G"][("KF", k)])))
    for k in sorted(set(grid) | {c["k_own"]}):
        if k in st["tc_ks"]:
            ti = st["tc_info"][k]
            L.append("DESCRIPTIVE: G_TC(%d) EVAL = %s; realised cut %d cells (%s)" % (
                k, iv(st["G"][("TC", k)]), ti["total"], ", ".join("%s %d" % kv for kv in sorted(ti["realised"].items(), key=lambda t: order_of(t[0])))))
        else:
            hit("TC.NA")
            L.append("DESCRIPTIVE: G_TC(%d) NOT AVAILABLE (the tree has %d leaves)" % (k, st["own"]))
    for k in sorted(st["tc_kw"]):
        L.append("DESCRIPTIVE: TC - KW at %d = %s" % (k, iv(st["tc_kw"][k])))
    L.append("DESCRIPTIVE: TC filings across sources (scored EVAL items whose AF-U leaf lies in another source's tree): %d" % st["cross"])
    for kind in ("KW", "KF", "TC"):
        kk = st["kw_ks"] if kind == "KW" else (grid if kind == "KF" else st["tc_ks"])
        for k in kk:
            r = st["R2"][(kind, k)]
            L.append("DESCRIPTIVE: R2_int_%s(%d) = %+.6f | two-stage 95%% [%+.6f, %+.6f]%s" % (
                kind, k, r["point"], r["lo"], r["hi"], "" if kind == "TC" else "; seeds %s" % " / ".join("%+.6f" % x for x in r["seeds"])))
    L.append("  R2_int replicates: %d TRAIN 3PL re-fits, %d not converged (counted, not dropped)" % (st["r2_fits"], st["r2_nonconv"]))
    for kind in ("KW", "KF", "TC"):
        kk = st["kw_ks"] if kind == "KW" else (grid if kind == "KF" else st["tc_ks"])
        for k in kk:
            s = st["sup"][(kind, k)]
            L.append("SUPPORT %s(%d)%s: cells with a scored item %.1f; TRAIN items per cell median %.1f, p10 %.1f; EVAL median %.1f, p10"
                     " %.1f; share of cells with TRAIN >= n* %d: %.4f; share of EVAL items in them: %.4f; cells falling back (mass < 1):"
                     " %.4f" % (kind, k, "" if kind == "TC" else " (mean over seeds)", s["cells"], s["tr_med"], s["tr_p10"], s["ev_med"],
                                s["ev_p10"], c["n_star"], s["share_cells"], s["share_eval"], s["fallback"]))
    for kind in ("KW", "KF", "TC"):
        kk = st["kw_ks"] if kind == "KW" else (grid if kind == "KF" else st["tc_ks"])
        L.append("OVERFIT GAP %s: TRAIN in-sample G | EVAL G: %s" % (kind, " | ".join(
            "k %d %s | %s" % (k, pp(st["train_g"][(kind, k)]), pp(st["G"][(kind, k)]["point"])) for k in kk)))
    L.append("ESTIMATION-NOISE DISCLOSURE: at fine k every cell's per-model accuracy rests on fewer TRAIN items, so a falling G or R2_int at"
             " the fine end is estimation noise as much as a property of granularity; the TRAIN in-sample G beside the EVAL G above shows"
             " the overfit gap")
    for sub in sorted(st["per_src"]):
        L.append("BBH DISCLOSURE / PER SOURCE: mean_s G_KW on %s: %s" % (sub, " | ".join(
            "k %d %s" % (k, pp(st["per_src"][sub][k])) for k in grid)))
    L.append("BBH DISCLOSURE: without BBH, D_lo = %s; D_hi = %s (descriptive)" % (iv(st["nobbh_d"][0]), iv(st["nobbh_d"][1])))
    # predictions
    for j, k in enumerate(grid):
        x = st["G"][("KW", k)]["point"]
        ok = U.in_band(x, PRED_P1[j])
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION P1 mean_s G_KW(%d) %s: observed %+.5f -> %s" % (k, PRED_P1_TXT[j], x, "HELD" if ok else "FAILED"))
    p2 = "INTERIOR" if ks in c["interior"] else "EDGE"
    L.append("PREDICTION P2 k* in %s, probability 0.60: observed k* %d (%s); Brier %.4f" % (list(c["interior"]), ks, p2, U.brier(PROB_P2, p2)))
    L.append("PREDICTION P3 GS1 INTERIOR-MAX 0.07, NOT-SHOWN 0.93: observed %s; Brier %.4f" % (word, U.brier(PROB_GS1, word)))
    r_mid, r_hi = st["R2"][("KW", c["k_mid"])]["point"], st["R2"][("KW", c["k_hi"])]["point"]
    ok = U.in_band(r_mid, PRED_P4)
    hit("PRED.HELD" if ok else "PRED.FAILED")
    L.append("PREDICTION P4 R2_int_KW(%d) [+0.045, +0.065]: observed %+.6f -> %s" % (c["k_mid"], r_mid, "HELD" if ok else "FAILED"))
    p4b = "LOWER" if r_hi < r_mid else "NOT-LOWER"
    L.append("PREDICTION P4 R2_int_KW lower at %d than at %d, probability 0.60: observed %+.6f vs %+.6f (%s); Brier %.4f" % (
        c["k_hi"], c["k_mid"], r_hi, r_mid, p4b, U.brier(PROB_P4B, p4b)))
    for k, band, txt in ((c["k_lo"], PRED_P5_LO, "0.85 [0.65, 1.00]"), (c["k_hi"], PRED_P5_HI, "0.03 [0.00, 0.15]")):
        x = st["sup"][("KW", k)]["share_eval"]
        ok = U.in_band(x, band)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION P5 share of EVAL items in KW cells with TRAIN >= %d at k %d %s: observed %.4f -> %s" % (
            c["n_star"], k, txt, x, "HELD" if ok else "FAILED"))
    if c["k_mid"] in st["tc_kw"]:
        x = st["tc_kw"][c["k_mid"]]["point"]
        ok = U.in_band(x, PRED_P6)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION P6 TC - KW at %d -0.3pp [-1.5, +0.9]: observed %+.5f -> %s" % (c["k_mid"], x, "HELD" if ok else "FAILED"))
    else:
        hit("P6.NOT_SCOREABLE")
        L.append("PREDICTION P6 TC - KW at %d -0.3pp [-1.5, +0.9]: NOT SCOREABLE (TC not available at %d)" % (c["k_mid"], c["k_mid"]))
    L.append("WORDS: every arm is SOURCE-CONDITIONED [SC] (filed through the source), never label-free; key-scored end to end, no judge"
             " verdict (no wrong(established) count, no tie convention A / B arises); one draw, one roster, one embedder")
    L.append("WILL NOT SHOW (registered): a best granularity for any other roster, corpus, embedder or split; sub-anchor profile rows (no"
             " per-cell profile is published); a label-free result (all [SC]); the tree beyond its 123 leaves; that k* is optimal"
             " (selected on 1,944 GATE items); judged decisions")
    return L, dict(GS1=word, why=why, F_GS=fired, RULE8=(word == "NOT-SHOWN"), kstar=ks)


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
    k0_rederive(say, P_)
    cells = build_cells(say, P_)
    cells["af"] = P_["af"]
    gk = {}

    def between(K_tr, train_meta, models):
        comp_tr = V.complete_items(K_tr, models)
        cnt = Counter(train_meta[i][1] for i in comp_tr)
        say("  scored TRAIN per source: %s; floor(count / %d): %s" % (", ".join("%s %d" % kv for kv in sorted(cnt.items())), c["cap_div"],
                                                                      ", ".join("%s %d" % (s, cnt[s] // c["cap_div"]) for s in sorted(cnt))))
        caps = {stratum(s): v for s, v in c["caps"].items()}
        if dict(cnt) != dict(c["train_counts"]) or any(cnt[s] // c["cap_div"] != caps[s] for s in caps):
            hit("REFUSE.TRAIN")
            refuse("[GSWEEP-TRAIN] the scored TRAIN counts %s are not the registered %s (or the caps no longer floor(count / %d))" % (
                dict(cnt), dict(c["train_counts"]), c["cap_div"]))
        gk["K"], gk["comp"] = gate_key(cfg, say, models, P_["gits"])
        if len(gk["comp"]) != int(c["n_gate_key"]):
            hit("REFUSE.GATE")
            refuse("[GSWEEP-GATE] %d key-complete GATE items, not the registered %d" % (len(gk["comp"]), c["n_gate_key"]))
    D, ok_sha = U.read_views(cfg, say, False, P_["af"], dict(P_["kx"], **cells["x"]), c["marker"],
                             "GRANULARITY-SWEEP: the EVAL key read started. frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit,
                             between=between, tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "GSWEEP")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    U.b3_check(D, cfg, P_["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file (best single %s; AF, K0..K4, TRUE source, TRUE source/domain)"
        % P_["pol"]["best_single"])
    I = RSC.irt_point(D, say, TAG)
    arms = {nm: D.groupings["x:" + nm] for nm in cells["x"]}
    rec = dict(r2=[], fits=0, nonconv=0, arms=arms)
    bt = V.run_boot(D, c["B"], c["seed"], hook=r2_hook(D, I, arms, rec))
    if D.fit_asserts != c["B"] + 2:
        refuse("[G3] %d fit checks executed, not %d" % (D.fit_asserts, c["B"] + 2))
    ok, got = U.identity(bt, D, c["identity"])
    if not ok:
        hit("REFUSE.IDENTITY")
        refuse("[GSWEEP-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
    say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
    hit("IDENTITY.OK")
    tco = cells["info"]["own"] if c["k_own"] in cells["info"]["tc_ks"] else None
    a_tc = float(bt["point"][0, U.karm(D, arm_name("TC", c["k_own"]))]) if tco else float("nan")
    if not (tco and abs(a_tc - float(bt["point"][0, V.TREE])) < 1e-12):
        hit("REFUSE.TC")
        refuse("[GSWEEP-TC-IDENTITY] TC at AF-U's own count %d is %.6f, not AF-U's leaf arm %.6f" % (
            c["k_own"], a_tc, float(bt["point"][0, V.TREE])))
    say("TC IDENTITY: TC at AF-U's own count %d = AF-U's leaf arm (%.4f) -> REPRODUCED" % (c["k_own"], a_tc))
    st = analyze(D, bt, cells, gk["K"], gk["comp"], I, rec, n_comp)
    L, words = gs_lines(st)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, bt=bt, cells=cells, P=P_)


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
import contextlib    # noqa: E402

BRANCHES = ("GS1.INTERIOR", "GS1.EDGE", "GS1.BOUND", "RULE8.REFUTED", "RULE8.NOT", "FGS.FIRED", "FGS.NOT", "TC.NA", "PRED.HELD",
            "PRED.FAILED", "P6.NOT_SCOREABLE", "IDENTITY.OK", "RUN.DONE", "DRY.DONE", "MARKER.WRITTEN", "REFUSE.WRITE_ONCE",
            "REFUSE.POOL", "REFUSE.POLICY_SHA", "REFUSE.MANIFEST", "REFUSE.PROFILE", "REFUSE.K0", "REFUSE.TRAIN", "REFUSE.GATE",
            "REFUSE.DENOM", "REFUSE.IDENTITY", "REFUSE.B3", "REFUSE.TC", "REFUSE.NOROW")
FX_WINNER = {"x0": "u03", "x1": "u06", "x2": "u01", "z0": "u05", "tiny": "u02"}    # the planted per-stratum specialists
FX_GENERALIST = "u00"                                                              # first in the sorted roster: wins the ties
FX_P = (0.97, 0.6, 0.0)                                                            # specialist, generalist, others


def _plant(fx, variant, seed=101):
    """Rewrite the fixture's mc6 responses IN PLACE (the view factory reads fx.spec). present: in the split sources' strata the
    stratum's specialist is correct with p 0.97, the generalist u00 (first in the sorted roster) with p 0.6 everywhere, every
    other model never (TRAIN, EVAL and GATE): a cell merging two strata picks the generalist (0.6 > (0.97 + 0) / 2), a pure cell
    the specialist, and the finest cells (one or two TRAIN items; fixture cap_div 2) tie between the correct models and the tie
    goes to u00, so both ends lose against the middle; null: every response
    Bernoulli(0.6), no model-by-item structure. The MATH-FIX overlay is cleared (mf None); multi-response cells stay multi."""
    rs = np.random.RandomState(seed)
    dom = {it["id"]: (it["src"], it["dom"]) for it in fx.spec["items"]}
    for r_ in fx.spec["responses"]:
        if r_["cv"] != "mc6":
            continue
        so, d = dom[r_["item"]]
        if variant == "present":
            if so == fx.single:
                continue
            p = FX_P[0] if r_["model"] == FX_WINNER[d] else (FX_P[1] if r_["model"] == FX_GENERALIST else FX_P[2])
        else:
            p = 0.6
        r_["c"] = int(rs.rand() < p)
        r_["mf"] = None


def _layout(tmp, variant="present", seed=23):
    """escalation_rc._build_layout's steps (union_af_route's fixture with the one-cell member BBH, real centroids, its
    --build-inputs and --run) with the response plant before the UNION-AF-ROUTE run; then union_route_common.build_layout's
    identity strings and this test's fixture constants (scored TRAIN counts, caps, GATE count) from the fixture's raw rows."""
    fx = UAR._fixture(tmp, single="BBH")
    proto, graft = ERC._fx_vectors(fx, np.random.RandomState(seed))
    ERC._fx_snapshots(fx, proto)
    _plant(fx, variant)
    with UAR._patched(fx):
        with contextlib.redirect_stdout(io.StringIO()):
            UAR.build_inputs(out=lambda s: None)
    b, _m = GC.load_bundle(os.path.join(tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    o = UAR._oracle_ak(fx, b, sum(fx.ksrc_b0.values()), fx.ksrc_b0)
    fx.reg["ak_identity"] = dict(d_u="%+.4f" % o["d_u"], d_us="%+.4f" % o["d_us"], spread_u="%.4f" % o["spread_u"], spread_us="%.4f" % o["spread_us"])
    UAR._fx_vdc_plain(fx)
    _lines, err = UAR._capture(UAR.run, fx)
    if err:
        raise AssertionError("fixture union_af_route --run refused: %s" % err)
    lay = ERC._Lay()
    lay.fx, lay.proto, lay.graft, lay.tmp, lay.variant = fx, proto, graft, tmp, variant
    t = open(os.path.join(tmp, "res", "outcome.txt"), encoding="utf-8").read()
    lay.uar_out = t
    pol_p = os.path.join(tmp, "res", "scratch", "pol.json")
    m = re.search(r"IDENTITY PRECONDITION: the declared arm C1 = ([+-][0-9.]+pp) \[([+-][0-9.]+pp), ([+-][0-9.]+pp)\]", t)
    ts = re.search(r"^    TRUE source\s+([0-9.]+)\s", t, re.M).group(1)
    idn = dict(ERC._uar_identity(t), tsrc=ts, c1=(m.group(1), m.group(2), m.group(3)))
    mu, val = U.o_key(fx.spec)
    side = {it["id"]: it for it in fx.spec["items"]}
    tr_ok = [i for i in set(k_[0] for k_ in val) if side[i]["side"] == "TRAIN" and all((i, m_) in val for m_ in mu)]
    tcnt = dict(Counter(side[i]["src"] for i in tr_ok))
    gv = {}
    for r_ in fx.spec["responses"]:
        if r_["cv"] == "mc6" and r_["side"] == "GATE":
            gv.setdefault((r_["item"], r_["model"]), []).append(r_["mf"] if r_["mf"] is not None else r_["c"])
    gate_ok = sorted(set(i for (i, _m_) in gv if all(len(gv.get((i, m_), [])) == 1 for m_ in mu)))
    lay.common = dict(U.COMMON, n_route=fx.reg["n_route"], comp_route=fx.reg["comp_route"], B=int(fx.spec["reg"]["B"]),
                      seed=int(fx.spec["reg"]["seed"]), uar_policy_sha=U.sha256_bytes(pol_p),
                      uar_outcome_sha=hashlib.sha256(t.encode("utf-8")).hexdigest(),
                      manifest_sha=UAR.sha256_lf(os.path.join(tmp, "res", "inputs", "inputs_manifest.json")), identity=idn, rws_n=40,
                      train_counts=tcnt, caps={s: tcnt[s] // FIXTURE_REG["cap_div"] for s in FIXTURE_REG["profile"]}, n_gate_key=len(gate_ok),
                      n_star=tcnt[FIXTURE_REG["one_cell"][0]])     # n* = the one-cell cell's exact TRAIN count (the >= edge)
    lay.gate_ok = gate_ok
    lay.reg = dict(lay.common)
    return lay


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


def _clone(lay, dest):
    new = U.clone(lay, dest)
    new.variant, new.gate_ok = lay.variant, lay.gate_ok
    return new


need = U.need


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "gs", "outcome.txt")), "an outcome was written by a refusal"


def _no_marker(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "gs", "READ_STARTED")), "the marker was written before the refusal"


# ── independent oracle (plain loops; the registered definitions written again) ──────────────────────────────────────────
FX_ORDER = ("MMLU_PRO", "BBH", "MATH")          # the fixture's union_af_route REG["sources"]


def _o_alloc(k, profile, one_cell, caps, order):
    n = k - len(one_cell)
    tot = float(sum(profile.values()))
    base, frac = {}, []
    for s in order:
        if s in profile:
            q = n * profile[s] / tot
            base[s] = int(q)
            frac.append((q - int(q), order.index(s), s))
    frac.sort(key=lambda t: (-t[0], t[1]))
    for j in range(n - sum(base.values())):
        base[frac[j][2]] += 1
    out = {}
    for s, v in base.items():
        v = 1 if v < 1 else v
        out[s] = caps[s] if v > caps[s] else v
    for s in one_cell:
        out[s] = 1
    return out


def _o_fit(Xs, k, s):
    best = None
    for r in range(5):
        Cm = CA.S0.skmeans(Xs, k, s * 16 + r)
        obj = float((Xs @ Cm.T).max(axis=1).sum())
        if best is None or obj > best[0]:
            best = (obj, Cm)
    Cm = best[1]
    lab = np.argmax(Xs @ Cm.T, axis=1)
    out = []
    for j in range(k):
        mem = Xs[lab == j]
        out.append(mem.sum(axis=0) / np.linalg.norm(mem.sum(axis=0)) if len(mem) else Cm[j])
    return out


def _o_file(x, allowed, cents, order):
    best = None
    for so in order:
        if so not in allowed or so not in cents:
            continue
        for j, cv in enumerate(cents[so]):
            sc = float(np.dot(x, cv))
            if best is None or sc > best[0]:
                best = (sc, so, j)
    return best[1], best[2]


def _o_ward(cents, kk):
    """scipy's own cut of the Ward tree (cut_tree; Ward heights are monotone), not the merge replay."""
    from scipy.cluster.hierarchy import linkage, cut_tree
    n = len(cents)
    if kk >= n:
        return list(range(n))
    if kk == 1:
        return [0] * n
    return [int(x) for x in cut_tree(linkage(np.vstack(cents), "ward"), n_clusters=kk).ravel()]


def _oracle(lay, res):
    """Every deciding number of the run recomputed from the fixture's raw rows and vectors."""
    c = dict(REG, **dict(lay.common, **FIXTURE_REG))
    fx, D = lay.fx, res["D"]
    order = list(FX_ORDER)
    mu, val = U.o_key(fx.spec)
    tr = [D.items[k] for k in D.T]
    ev = [D.items[k] for k in D.E]
    b, _m = GC.load_bundle(os.path.join(lay.tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    classes = [str(x) for x in b["classes"]]
    Xt = GC.FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    tsrc = [classes[i].split("/", 1)[0] for i in np.asarray(b["train_y"], dtype=int)]
    man = U.json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _d = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    rows = []
    for nm in ("MAIN_union_routing_queries.csv", "MAIN_union_routing_train_queries.csv"):
        rows += GB.read_csv(os.path.join(lay.tmp, "res", "inputs", "validation_merged", nm))
    srcs = {}
    for r_ in rows:
        srcs.setdefault(r_["item_id"], set()).add(str(r_["true_key"]).split("/", 1)[0])
    gits = sorted(i for i in srcs if fx.side[i][1] == "GATE")
    gval = {}
    for r_ in fx.spec["responses"]:
        if r_["cv"] == "mc6" and r_["side"] == "GATE":
            gval.setdefault((r_["item"], r_["model"]), []).append(r_["mf"] if r_["mf"] is not None else r_["c"])
    gok = [i for i in gits if all(len(gval.get((i, m_), [])) == 1 for m_ in mu)]
    kw_ks = sorted(set(c["grid"]) | {c["k_own"]})
    allocs = {k: _o_alloc(k, c["profile"], c["one_cell"], c["caps"], order) for k in kw_ks}
    cells = {}
    for s in SEEDS:
        top = {so: _o_fit(Xt[np.array([t == so for t in tsrc])], allocs[c["k_hi"]][so], s) for so in allocs[c["k_hi"]]}
        filed = {it: _o_file(fx.vec[it], srcs[it], top, order) for it in srcs if (it in af and af[it] != UAR.NO_ROW) or it in gits}
        for k in kw_ks:
            grp = {so: _o_ward(top[so], allocs[k][so]) for so in top}
            cells[("KW", k, s)] = {it: (so, grp[so][j]) for it, (so, j) in filed.items()}
        for k in c["grid"]:
            if k == c["k_hi"]:
                cells[("KF", k, s)] = cells[("KW", k, s)]
                continue
            cf = {so: _o_fit(Xt[np.array([t == so for t in tsrc])], allocs[k][so], s) for so in allocs[k]}
            cells[("KF", k, s)] = {it: _o_file(fx.vec[it], srcs[it], cf, order) for it in filed}
    for k in c["tc_k"]:
        cells[("TC", k, None)] = dict(af)          # the fixture's member trees are one level deep: every cut is the leaves
    o = dict(G={}, gate={})
    best_full, _p = U.o_fit(tr, af, val, mu)
    abest = U.o_acc(ev, af, val, best_full, {})
    pols = {}
    for key, cl in cells.items():
        bst, pol = U.o_fit(tr, cl, val, mu)
        pols[key] = (bst, pol)
        o["G"][key] = U.o_acc(ev, cl, val, bst, pol) - abest
    for k in c["grid"]:
        per = []
        for s in SEEDS:
            bst, pol = pols[("KW", k, s)]
            cl = cells[("KW", k, s)]
            per.append(float(np.mean([gval[(i, pol.get(cl[i], bst))][0] - gval[(i, bst)][0] for i in gok])))
        o["gate"][k] = float(np.mean(per))
    ks = None
    for k in sorted(c["grid"]):
        if ks is None or o["gate"][k] > o["gate"][ks]:
            ks = k
    o["kstar"] = ks

    def mean_g(kind, k):
        return float(np.mean([o["G"][(kind, k, s)] for s in SEEDS]))
    o["Gm"] = {(kind, k): mean_g(kind, k) for kind, kk in (("KW", kw_ks), ("KF", c["grid"])) for k in kk}
    o["Gm"].update({("TC", k): o["G"][("TC", k, None)] for k in c["tc_k"]})
    o["dlo"] = mean_g("KW", ks) - mean_g("KW", c["k_lo"])
    o["dhi"] = mean_g("KW", ks) - mean_g("KW", c["k_hi"])
    o["fgs"] = mean_g("KW", c["k_lo"]) - mean_g("KW", c["k_mid"])
    sh = []
    for s in SEEDS:
        cl = cells[("KW", c["k_lo"], s)]
        ntr = Counter(cl[i] for i in tr)
        sh.append(sum(1 for i in ev if ntr.get(cl[i], 0) >= c["n_star"]) / float(len(ev)))
    o["p5_lo"] = float(np.mean(sh))
    rng = np.random.default_rng(c["seed"])
    SD = np.random.default_rng(c["seed_draw"]).integers(0, 5, size=(c["B"], 5))
    reps = dict(dlo=[], dhi=[], fgs=[])
    for bb in range(c["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = V.draw_units(rng, D.train_units)
        v = V.draw_units(rng, D.eval_units)
        w = {D.items[k]: int(wt[k]) for k in D.T}
        vv = {D.items[k]: float(v[j]) for j, k in enumerate(D.E)}
        acc = {}
        for k in set([ks, c["k_lo"], c["k_hi"], c["k_mid"]]):
            for s in SEEDS:
                bst, pol = U.o_fit(tr, cells[("KW", k, s)], val, mu, w)
                acc[(k, s)] = U.o_acc(ev, cells[("KW", k, s)], val, bst, pol, vv)
        sel = [int(x) for x in SD[bb]]
        reps["dlo"].append(float(np.mean([acc[(ks, s)] - acc[(c["k_lo"], s)] for s in sel])))
        reps["dhi"].append(float(np.mean([acc[(ks, s)] - acc[(c["k_hi"], s)] for s in sel])))
        reps["fgs"].append(float(np.mean([acc[(c["k_lo"], s)] - acc[(c["k_mid"], s)] for s in sel])))
    o["se"] = {k_: float(np.std(v_, ddof=1)) for k_, v_ in reps.items()}
    return o


def _iv_num(text, label):
    m = re.search(re.escape(label) + r" = \S+ \(([+-][0-9.]+)\) \| two-stage 95% \[\S+, \S+\] \(([+-][0-9.]+), ([+-][0-9.]+)\)", text)
    if not m:
        raise AssertionError("no interval line %r" % label)
    return [float(x) for x in m.groups()]


def _check_e2e(lay, text, res, want):
    c = dict(REG, **dict(lay.common, **FIXTURE_REG))
    o = _oracle(lay, res)
    kw_ks = sorted(set(c["grid"]) | {c["k_own"]})
    for k in kw_ks:
        x = _iv_num(text, "G_KW(%d) EVAL" % k)[0]
        assert abs(x - o["Gm"][("KW", k)]) < 6e-6, ("KW", k, x, o["Gm"][("KW", k)])
    for k in c["grid"]:
        x = _iv_num(text, "DESCRIPTIVE: G_KF(%d) EVAL" % k)[0]
        assert abs(x - o["Gm"][("KF", k)]) < 6e-6, ("KF", k, x, o["Gm"][("KF", k)])
    for k in c["tc_k"]:
        x = _iv_num(text, "DESCRIPTIVE: G_TC(%d) EVAL" % k)[0]
        assert abs(x - o["Gm"][("TC", k)]) < 6e-6, ("TC", k, x, o["Gm"][("TC", k)])
    for k in c["grid"]:
        need(text, "k %d %s (seeds" % (k, pp(o["gate"][k])))
    need(text, "k* = %d (argmax" % o["kstar"])
    for key, txt in (("dlo", "GS1 D_lo = G_KW(k*=%d) - G_KW(%d)" % (o["kstar"], c["k_lo"])),
                     ("dhi", "GS1 D_hi = G_KW(k*=%d) - G_KW(%d)" % (o["kstar"], c["k_hi"])),
                     ("fgs", "F-GS: G_KW(%d) - G_KW(%d)" % (c["k_lo"], c["k_mid"]))):
        p_, lo, hi = _iv_num(text, txt)
        assert abs(p_ - o[key]) < 6e-6, (key, p_, o[key])
        assert abs(lo - (o[key] - 1.96 * o["se"][key])) < 2e-5 and abs(hi - (o[key] + 1.96 * o["se"][key])) < 2e-5, (key, lo, hi, o["se"][key])
    se_lo, = U.num(text, r"support D_lo: n \d+, SE_2stage ([0-9.]+) ")
    assert abs(se_lo - o["se"]["dlo"]) < 6e-6, (se_lo, o["se"]["dlo"])
    p5, = U.num(text, r"PREDICTION P5 share of EVAL items in KW cells with TRAIN >= \d+ at k %d [^:]*: observed ([0-9.]+)" % c["k_lo"])
    assert abs(p5 - o["p5_lo"]) < 6e-5, (p5, o["p5_lo"])
    dlo, lo_lo, _h = _iv_num(text, "GS1 D_lo = G_KW(k*=%d) - G_KW(%d)" % (o["kstar"], c["k_lo"]))
    dhi, lo_hi, _h = _iv_num(text, "GS1 D_hi = G_KW(k*=%d) - G_KW(%d)" % (o["kstar"], c["k_hi"]))
    hand = "INTERIOR-MAX" if (o["kstar"] in c["interior"] and dlo > 0 and lo_lo > 0 and dhi > 0 and lo_hi > 0) else "NOT-SHOWN"
    assert hand == want, (hand, want)
    need(text, "GS1 -> %s" % want)
    fp, flo, _fh = _iv_num(text, "F-GS: G_KW(%d) - G_KW(%d)" % (c["k_lo"], c["k_mid"]))
    need(text, "FALSIFIER F-GS: %s" % ("FIRES" if (fp > 0 and flo > 0) else "NOT FIRED"))
    return o


def st_run_present(lays, mk):
    lay = _clone(lays["present"], mk())
    text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "gs", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (GRANULARITY-SWEEP; --run" % U.POOL), out.splitlines()[0]
    assert os.path.isfile(os.path.join(lay.tmp, "res", "gs", "READ_STARTED"))
    o = _check_e2e(lay, out, res, "INTERIOR-MAX")
    assert o["kstar"] in FIXTURE_REG["interior"] and o["dlo"] > 0.01 and o["dhi"] > 0.01, "the present fixture does not discriminate"
    assert res["words"]["GS1"] == "INTERIOR-MAX" and res["words"]["RULE8"] is False
    need(out, "RULE 8: INTERIOR-MAX is not refuted", "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]),
         "TC IDENTITY: TC at AF-U's own count 6 = AF-U's leaf arm", "K0 RE-DERIVATION (union_af_route.k_cells, seed 0): 0 of",
         "B3: the point policy re-fitted beside EVAL equals",
         "PREDICTION P3 GS1 INTERIOR-MAX 0.07, NOT-SHOWN 0.93: observed INTERIOR-MAX; Brier %.4f" % U.brier(PROB_GS1, "INTERIOR-MAX"),
         "DESCRIPTIVE: G_TC(11) NOT AVAILABLE (the tree has 6 leaves)", "PREDICTION P6 TC - KW at 11 -0.3pp [-1.5, +0.9]: NOT SCOREABLE",
         "ESTIMATION-NOISE DISCLOSURE", "WILL NOT SHOW (registered)", "verdict line of record: " + VERDICT_LINE,
         "R2_int replicates: %d TRAIN 3PL re-fits" % lay.common["B"])
    g1 = _iv_num(out, "G_KW(%d) EVAL" % FIXTURE_REG["k_hi"])[0]
    g2 = _iv_num(out, "DESCRIPTIVE: G_KF(%d) EVAL" % FIXTURE_REG["k_hi"])[0]
    assert g1 == g2, ("KW at the top k is the KF fit", g1, g2)
    assert text.startswith(out), "the outcome is not the printed text"
    _t2, err2, _r = U.cap(_me(), run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


def st_run_absent(lays, mk):
    lay = _clone(lays["absent"], mk())
    _text, err, res = U.cap(_me(), run, lay)
    assert err is None, err
    out = open(os.path.join(lay.tmp, "res", "gs", "outcome.txt"), encoding="utf-8").read()
    _check_e2e(lay, out, res, "NOT-SHOWN")
    assert res["words"]["GS1"] == "NOT-SHOWN" and res["words"]["RULE8"] is True and res["words"]["F_GS"] is False
    need(out, "RULE 8: INTERIOR-MAX is REFUTED at the planned n (", "FALSIFIER F-GS: NOT FIRED")
    assert re.search(r"GS1 -> NOT-SHOWN \((EDGE: k\* = \d+ is an end of the grid|D_(lo|hi)'s (point|95% lower bound) [+-][0-9.]+ <= 0)", out)


# ── synthetic stats through gs_lines (the printed block of record) ─────────────────────────────────────────────────────
def _ci(pt, lo=None, hi=None, se=0.006):
    lo = pt - 1.96 * se if lo is None else lo
    hi = pt + 1.96 * se if hi is None else hi
    return dict(point=pt, lo=lo, hi=hi, pct=(lo, hi), se2=se, se_iid=se / 1.36, deff=1.85, n_eff=3193.0, mde=2.8 * se, n=5907)


def _syn(kstar=100, dlo=(0.01, 0.002), dhi=(0.01, 0.002), fgs=(-0.004, -0.012), g=None, r2=(0.055, 0.050), p5=(0.85, 0.03),
         tc_mid=-0.003, tc_ks=(25, 50, 100, 123)):
    grid = [25, 50, 100, 200, 400]
    kw_ks = sorted(set(grid) | {123})
    g0 = {25: 0.015, 50: 0.018, 100: 0.019, 123: 0.0197, 200: 0.017, 400: 0.015}
    g0.update(g or {})
    g = g0
    st = dict(n=5907, comp=5404, kish=1.311, n_train=11841, n_gate=1944, B=2000, grid=grid, kw_ks=kw_ks, kstar=kstar,
              gate={k: [0.01] * 5 for k in grid}, gate_mean={k: 0.01 for k in grid}, eval_argmax=100, tc_ks=list(tc_ks), own=123,
              cross=191, r2_fits=2000, r2_nonconv=0)
    st["G"] = {("KW", k): _ci(g[k]) for k in kw_ks}
    st["G"].update({("KF", k): _ci(g[k] - 0.001) for k in grid})
    st["G"].update({("TC", k): _ci(g.get(k, 0.015) - 0.003) for k in tc_ks})
    st["Gs"] = {k: [g[k]] * 5 for k in kw_ks}
    st["dlo"], st["dhi"], st["fgs"] = _ci(dlo[0], dlo[1]), _ci(dhi[0], dhi[1]), _ci(fgs[0], fgs[1])
    st["tc_kw"] = {k: _ci(tc_mid if k == 100 else -0.002) for k in tc_ks if k in kw_ks}
    st["tc_info"] = {k: dict(realised={"MMLU_PRO_LB": 13, "BBH": 7}, total=k) for k in tc_ks}
    r2m = {k: 0.05 for k in kw_ks}
    r2m[100], r2m[400] = r2
    st["R2"] = {(kind, k): dict(point=r2m.get(k, 0.05), lo=0.04, hi=0.06, seeds=[r2m.get(k, 0.05)] * 5)
                for kind, kk in (("KW", kw_ks), ("KF", grid), ("TC", tc_ks)) for k in kk}
    sup = dict(cells=25.0, tr_med=400.0, tr_p10=120.0, ev_med=200.0, ev_p10=60.0, share_cells=0.5, share_eval=0.5, fallback=0.0)
    st["sup"] = {(kind, k): dict(sup) for kind, kk in (("KW", kw_ks), ("KF", grid), ("TC", tc_ks)) for k in kk}
    st["sup"][("KW", 25)]["share_eval"], st["sup"][("KW", 400)]["share_eval"] = p5
    st["train_g"] = {key: 0.03 for key in st["G"]}
    st["per_src"] = {s: {k: 0.01 for k in grid} for s in ("NON_BBH", "SRC:BBH", "SRC:MMLU_PRO")}
    st["nobbh_d"] = (_ci(0.004), _ci(0.003))
    return st


def _lines(**kw):
    saved = _REG[0]
    _REG[0] = REG
    try:
        L, w = gs_lines(_syn(**kw))
    finally:
        _REG[0] = saved
    return "\n".join(L), w


def st_branches():
    cases = [(dict(), "INTERIOR-MAX", "GS1 -> INTERIOR-MAX (k* = 100 interior; D_lo and D_hi > 0 with lower bounds > 0)"),
             (dict(dlo=(0.01, 1e-12), dhi=(0.01, 1e-12)), "INTERIOR-MAX", "GS1 -> INTERIOR-MAX (k* = 100"),
             (dict(kstar=50), "INTERIOR-MAX", "GS1 -> INTERIOR-MAX (k* = 50"),
             (dict(kstar=200), "INTERIOR-MAX", "GS1 -> INTERIOR-MAX (k* = 200"),
             (dict(kstar=25), "NOT-SHOWN", "GS1 -> NOT-SHOWN (EDGE: k* = 25 is an end of the grid)"),
             (dict(kstar=400), "NOT-SHOWN", "GS1 -> NOT-SHOWN (EDGE: k* = 400 is an end of the grid)"),
             (dict(dlo=(0.01, 0.0)), "NOT-SHOWN", "GS1 -> NOT-SHOWN (D_lo's 95% lower bound +0.00000 <= 0)"),
             (dict(dhi=(0.01, 0.0)), "NOT-SHOWN", "GS1 -> NOT-SHOWN (D_hi's 95% lower bound +0.00000 <= 0)"),
             (dict(dhi=(0.01, -0.001)), "NOT-SHOWN", "GS1 -> NOT-SHOWN (D_hi's 95% lower bound -0.00100 <= 0)"),
             (dict(dlo=(0.0, -0.01)), "NOT-SHOWN", "GS1 -> NOT-SHOWN (D_lo's point +0.00000 <= 0)"),
             (dict(dlo=(-0.002, -0.01), dhi=(0.004, -0.001)), "NOT-SHOWN",
              "GS1 -> NOT-SHOWN (D_lo's point -0.00200 <= 0; D_hi's 95% lower bound -0.00100 <= 0)")]
    for kw, want, line in cases:
        t, w = _lines(**kw)
        assert w["GS1"] == want, (kw, w)
        need(t, line, "verdict line of record: " + VERDICT_LINE, "WILL NOT SHOW (registered)", "DENOMINATOR: 5907 EVAL items in 5404",
             "LIKE WITH LIKE", "[SC]", "ESTIMATION-NOISE DISCLOSURE", "BBH DISCLOSURE: without BBH",
             "PREDICTION P3 GS1 INTERIOR-MAX 0.07, NOT-SHOWN 0.93: observed %s; Brier %.4f" % (want, {"INTERIOR-MAX": 1.7298, "NOT-SHOWN": 0.0098}[want]),
             "DESCRIPTIVE: G_TC(200) NOT AVAILABLE (the tree has 123 leaves)", "DESCRIPTIVE: G_TC(400) NOT AVAILABLE (the tree has 123 leaves)",
             "support D_lo: n 5907", "support D_hi: n 5907")
        if want == "NOT-SHOWN":
            need(t, "RULE 8: INTERIOR-MAX is REFUTED at the planned n (")
            assert w["RULE8"] is True
        else:
            need(t, "RULE 8: INTERIOR-MAX is not refuted (k* interior and both lower bounds > 0)")
            assert w["RULE8"] is False
        p2 = "INTERIOR" if kw.get("kstar", 100) in (50, 100, 200) else "EDGE"
        need(t, "observed k* %d (%s); Brier %.4f" % (kw.get("kstar", 100), p2, {"INTERIOR": 0.32, "EDGE": 0.72}[p2]))
    for f, want in (((0.01, 0.001), True), ((0.01, 1e-12), True), ((0.01, 0.0), False), ((0.01, -0.002), False), ((-0.01, -0.02), False)):
        t, w = _lines(fgs=f)
        assert w["F_GS"] is want, (f, w)
        need(t, "FALSIFIER F-GS: FIRES" if want else "FALSIFIER F-GS: NOT FIRED (F-GS fires iff G_KW(25) - G_KW(100) > 0 with its 95% lower bound > 0)")
    bands = ((0.005, 0.025), (0.008, 0.028), (0.009, 0.029), (0.007, 0.027), (0.003, 0.025))
    for j, k in enumerate((25, 50, 100, 200, 400)):
        for x, want in ((bands[j][0], "HELD"), (bands[j][1], "HELD"), (bands[j][0] - 1e-4, "FAILED"), (bands[j][1] + 1e-4, "FAILED")):
            t, _w = _lines(g={k: x})
            need(t, "PREDICTION P1 mean_s G_KW(%d) %s: observed %+.5f -> %s" % (k, PRED_P1_TXT[j], x, want))
    for x, want in ((0.045, "HELD"), (0.065, "HELD"), (0.0449, "FAILED"), (0.0651, "FAILED")):
        t, _w = _lines(r2=(x, 0.01))
        need(t, "PREDICTION P4 R2_int_KW(100) [+0.045, +0.065]: observed %+.6f -> %s" % (x, want))
    t, _w = _lines(r2=(0.05, 0.049))
    need(t, "PREDICTION P4 R2_int_KW lower at 400 than at 100, probability 0.60: observed +0.049000 vs +0.050000 (LOWER); Brier 0.3200")
    t, _w = _lines(r2=(0.05, 0.05))
    need(t, "observed +0.050000 vs +0.050000 (NOT-LOWER); Brier 0.7200")
    for p5, wl, wh in (((0.65, 0.0), "HELD", "HELD"), ((1.0, 0.15), "HELD", "HELD"), ((0.6499, 0.1501), "FAILED", "FAILED")):
        t, _w = _lines(p5=p5)
        need(t, "at k 25 0.85 [0.65, 1.00]: observed %.4f -> %s" % (p5[0], wl), "at k 400 0.03 [0.00, 0.15]: observed %.4f -> %s" % (p5[1], wh))
    for x, want in ((-0.015, "HELD"), (0.009, "HELD"), (-0.0151, "FAILED"), (0.0091, "FAILED")):
        t, _w = _lines(tc_mid=x)
        need(t, "PREDICTION P6 TC - KW at 100 -0.3pp [-1.5, +0.9]: observed %+.5f -> %s" % (x, want))
    t, _w = _lines(tc_ks=(25, 50, 123))
    need(t, "PREDICTION P6 TC - KW at 100 -0.3pp [-1.5, +0.9]: NOT SCOREABLE (TC not available at 100)",
         "DESCRIPTIVE: G_TC(100) NOT AVAILABLE (the tree has 123 leaves)")
    # the seed-joint interval against hand replicates
    pt = np.array([0.1, 0.3, 0.0])
    two = np.array([[0.1, 0.3, 0.0], [0.2, 0.2, 0.0], [0.0, 0.4, 0.0]])
    iid = np.array([[0.1, 0.3, 0.0], [0.1, 0.3, 0.0], [0.1, 0.3, 0.0]])
    r = seed_stat(pt, two, iid, [[(0, 1.0), (2, -1.0)], [(1, 1.0), (2, -1.0)]], np.array([[0, 0], [1, 1], [0, 1]]), 3)
    sd = float(np.std([0.1, 0.2, 0.2], ddof=1))
    assert abs(r["point"] - 0.2) < 1e-12 and abs(r["se2"] - sd) < 1e-12 and abs(r["lo"] - (0.2 - 1.96 * sd)) < 1e-12, r
    # NAIVE INTERVAL 1: seeds fixed (unit-only) would decide; the registered seed-joint interval does not
    rs = np.random.default_rng(5)
    d = [0.06, 0.06, -0.05, 0.06, -0.05]
    pt = np.array(d + [0.0] * 5)
    Bn = 400
    two = pt[None, :] + 1e-4 * rs.normal(size=(Bn, 10))
    iid = pt[None, :] + 1e-4 * rs.normal(size=(Bn, 10))
    terms = [[(s, 1.0), (5 + s, -1.0)] for s in range(5)]
    good = _ci(0.02, 0.01)
    naive = seed_stat(pt, two, iid, terms, np.tile(np.arange(5), (Bn, 1)), 5907)
    joint = seed_stat(pt, two, iid, terms, seed_draws(Bn, REG["seed_draw"], 5), 5907)
    assert naive["lo"] > 0 and joint["lo"] < 0 < joint["point"], (naive["lo"], joint["lo"])
    assert gs1_verdict(100, REG["interior"], naive, good)[0] == "INTERIOR-MAX"
    assert gs1_verdict(100, REG["interior"], joint, good) == ("NOT-SHOWN", "D_lo's 95%% lower bound %+.5f <= 0" % joint["lo"])
    # NAIVE INTERVAL 2: the i.i.d. interval (policy fixed) would decide; the two-stage one does not
    pt = np.array([0.02] * 5 + [0.0] * 5)
    two = pt[None, :] + 0.02 * rs.normal(size=(Bn, 10))
    iid = pt[None, :] + 0.002 * rs.normal(size=(Bn, 10))
    r = seed_stat(pt, two, iid, terms, seed_draws(Bn, REG["seed_draw"], 5), 5907)
    assert r["point"] - 1.96 * r["se_iid"] > 0 and r["lo"] <= 0 and r["deff"] > 10, r
    assert gs1_verdict(100, REG["interior"], good, r)[0] == "NOT-SHOWN"
    # k*: ties to the smaller k; first strict maximum
    assert kstar_of({25: 0.01, 50: 0.02, 100: 0.02, 200: 0.0, 400: 0.02}, REG["grid"]) == 50
    assert kstar_of({25: 0.03, 50: 0.02, 100: 0.02, 200: 0.0, 400: 0.031}, REG["grid"]) == 400
    assert U.in_band(0.005, PRED_P1[0]) is True and U.in_band(0.0049, PRED_P1[0]) is False


def st_constants():
    c = REG
    assert tuple(c["grid"]) == (25, 50, 100, 200, 400) and tuple(c["interior"]) == (50, 100, 200)
    assert (c["k_lo"], c["k_hi"], c["k_mid"], c["k_own"]) == (25, 400, 100, 123) and tuple(c["tc_k"]) == (25, 50, 100, 123)
    assert c["profile"] == {"MMLU_PRO_LB": 69, "BBH": 36, "MATH": 10, "MUSR": 3, "GPQA": 4} and tuple(c["one_cell"]) == ("IFEVAL",)
    assert c["train_counts"] == {"MMLU_PRO": 6759, "BBH": 3473, "MATH": 773, "MUSR": 454, "IFEVAL": 325, "GPQA": 57}
    assert sum(c["train_counts"].values()) == 11841
    assert c["caps"] == {s: c["train_counts"][stratum(s)] // c["cap_div"] for s in c["profile"]} and c["cap_div"] == 5
    assert c["caps"] == {"MMLU_PRO_LB": 1351, "BBH": 694, "MATH": 154, "MUSR": 90, "GPQA": 11}
    assert c["n_star"] == int(math.ceil(1.311 * 2.8 ** 2 * 0.30 / 0.10 ** 2)) == 309
    assert (c["B"], c["seed"], c["seed_draw"], c["n_route"], c["comp_route"], c["n_gate_key"]) == (2000, 42, 20261006, 5907, 5404, 1944)
    assert c["out"] == "experiment_results/archv2/granularity_sweep/granularity_sweep_outcome.txt"
    assert c["uar_policy_sha"].startswith("8d68018c") and c["manifest_sha"].startswith("53021e26")
    assert abs(math.sqrt(0.599 ** 2 + 0.158 ** 2) - 0.620) < 6e-4 and abs(SUPPORT["se"] - 0.0062) < 1e-12
    assert abs(2.8 * 0.620 - 1.74) < 0.005 and abs(3.21 * 0.620 - 1.99) < 0.005 and abs(5907 / 1.847 - 3198) < 1
    want = {25: (13, 7, 2, 1, 1, 1, 25), 50: (28, 14, 4, 1, 1, 2, 50), 100: (56, 29, 8, 3, 1, 3, 100), 123: (69, 36, 10, 3, 1, 4, 123),
            200: (113, 59, 16, 5, 1, 6, 200), 400: (225, 118, 33, 10, 1, 11, 398)}
    srcs = ("MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA")
    saved = UAR._REG[0]
    UAR._REG[0] = UAR.REG
    try:
        assert tuple(UAR.reg()["sources"]) == srcs
        for k, w in want.items():
            a, _q = allocate(k, c["profile"], c["one_cell"], c["caps"])
            assert tuple(a[s] for s in srcs) + (sum(a.values()),) == w, (k, a)
            assert a == _o_alloc(k, c["profile"], c["one_cell"], c["caps"], list(srcs)), k
    finally:
        UAR._REG[0] = saved
    assert PRED_P1 == ((0.005, 0.025), (0.008, 0.028), (0.009, 0.029), (0.007, 0.027), (0.003, 0.025))
    assert PRED_P4 == (0.045, 0.065) and PRED_P5_LO == (0.65, 1.00) and PRED_P5_HI == (0.00, 0.15) and PRED_P6 == (-0.015, 0.009)
    assert dict(PROB_P2) == {"INTERIOR": 0.60, "EDGE": 0.40} and dict(PROB_GS1) == {"INTERIOR-MAX": 0.07, "NOT-SHOWN": 0.93}


def st_alloc():
    saved = UAR._REG[0]
    UAR._REG[0] = UAR.REG
    try:
        order = list(UAR.reg()["sources"])
        assert allocate(3, {"MMLU_PRO_LB": 1, "BBH": 1}, (), {"MMLU_PRO_LB": 9, "BBH": 9})[0] == {"MMLU_PRO_LB": 2, "BBH": 1}
        assert allocate(3, {"BBH": 1, "MMLU_PRO_LB": 1}, (), {"MMLU_PRO_LB": 9, "BBH": 9})[0] == {"MMLU_PRO_LB": 2, "BBH": 1}
        a = allocate(20, {"MMLU_PRO_LB": 10, "GPQA": 10}, (), {"MMLU_PRO_LB": 99, "GPQA": 2})[0]
        assert a == {"MMLU_PRO_LB": 10, "GPQA": 2}, a                          # capped surplus not re-allocated
        a = allocate(5, {"MMLU_PRO_LB": 100, "GPQA": 1}, (), {"MMLU_PRO_LB": 99, "GPQA": 9})[0]
        assert a == {"MMLU_PRO_LB": 5, "GPQA": 1}, a                           # at least one per source (realised 6 > k 5: printed)
        a = allocate(6, {"MMLU_PRO_LB": 3, "BBH": 1}, ("IFEVAL",), {"MMLU_PRO_LB": 99, "BBH": 99})[0]
        assert a == {"MMLU_PRO_LB": 4, "BBH": 1, "IFEVAL": 1}, a               # 5 to the split sources: 3.75 / 1.25
        rs = np.random.RandomState(3)
        srcs = ["MMLU_PRO_LB", "BBH", "MATH", "MUSR", "GPQA"]
        for _t in range(300):
            prof = {s: int(rs.randint(1, 60)) for s in srcs if rs.rand() < 0.8} or {"BBH": 3}
            caps = {s: int(rs.randint(1, 80)) for s in prof}
            k = int(rs.randint(len(prof) + 1, 300))
            assert allocate(k, prof, ("IFEVAL",), caps)[0] == _o_alloc(k, prof, ("IFEVAL",), caps, order), (k, prof, caps)
    finally:
        UAR._REG[0] = saved


def st_tc_ward():
    tree = dict(root="R", children={"R": ["A", "B"], "A": ["A1", "A2", "A3"], "B": ["B1", "B2"], "A2": ["A2a", "A2b"]},
                leaves={"A1", "A2a", "A2b", "A3", "B1", "B2"})
    lc = {"A1": 10, "A2a": 5, "A2b": 5, "A3": 10, "B1": 20, "B2": 25}
    cnt = subtree_counts(tree, lc)
    assert (cnt["R"], cnt["A"], cnt["B"], cnt["A2"]) == (75, 30, 45, 10), cnt
    want = {1: ["R"], 2: ["A", "B"], 3: ["A", "B1", "B2"], 4: ["A1", "A2", "A3", "B1", "B2"], 5: ["A1", "A2", "A3", "B1", "B2"],
            6: ["A1", "A2a", "A2b", "A3", "B1", "B2"], 10: ["A1", "A2a", "A2b", "A3", "B1", "B2"]}
    for k, cut in want.items():
        up, got = tc_cut(tree, cnt, k)
        assert got == sorted(cut), (k, got)
        assert set(up) == tree["leaves"] and set(up.values()) == set(cut), (k, up)
    up, _c = tc_cut(tree, cnt, 3)
    assert up["A2a"] == "A" and up["B1"] == "B1"
    af_ = {"t1": "A1", "t2": "A1", "e1": "A1", "e2": "B1", "e3": "B1", "g1": "B2", "t3": "B2"}
    side_ = {"t1": ("c", "TRAIN"), "t2": ("c", "TRAIN"), "t3": ("c", "TRAIN"), "e1": ("c", "EVAL"), "e2": ("c", "EVAL"),
             "e3": ("c", "EVAL"), "g1": ("c", "GATE")}
    assert dict(tc_train_counts(af_, side_)) == {"A1": 2, "B2": 1}
    lc2 = {"A1": 15, "A2a": 5, "A2b": 5, "A3": 20, "B1": 20, "B2": 25}          # A = B = 45: the tie goes to the smaller id A
    assert tc_cut(tree, subtree_counts(tree, lc2), 3)[1] == sorted(["A1", "A2", "A3", "B"])
    rs = np.random.RandomState(2)
    C = rs.normal(size=(12, 4))
    C /= np.linalg.norm(C, axis=1, keepdims=True)
    prev = None
    for kk in range(12, 0, -1):
        g = ward_groups(C, kk)
        o = _o_ward(list(C), kk)
        assert len(set(g.tolist())) == kk
        part = lambda lab: sorted(sorted(np.flatnonzero(np.asarray(lab) == v).tolist()) for v in set(lab))    # noqa: E731
        assert part(g.tolist()) == part(o), (kk, g, o)
        if prev is not None:                                                    # nested: every finer group inside one coarser group
            for v in set(prev.tolist()):
                assert len(set(g[prev == v].tolist())) == 1, kk
        prev = g
    try:
        ward_groups(C, 13)
        raise AssertionError("a coarser allocation above the top was not refused")
    except SystemExit as e:
        assert "[GSWEEP-NEST]" in str(e)


# ── refusals ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _refuse_case(lays, mk, needle, marker_ok=True, patch=None, **over):
    lay = _clone(lays["present"], mk())
    undo = patch(lay) if patch else None
    try:
        t, err, _r = U.cap(_me(), run, lay, **over)
    finally:
        if undo:
            undo()
    assert err and needle in err, (needle, err)
    for bad in ("GS1 ->", "k* =", "G_KW(", "FALSIFIER F-GS"):
        assert bad not in t, (needle, bad)
    _no_outcome(lay)
    if not marker_ok:
        _no_marker(lay)
    return t


def st_refusals(lays, mk):
    lay = _clone(lays["present"], mk())
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
    _refuse_case(lays, mk, "inputs manifest is sha256", False, manifest_sha="0" * 64)
    _refuse_case(lays, mk, "frozen TRAIN policy", False, uar_policy_sha="0" * 64)
    _refuse_case(lays, mk, "[GSWEEP-PROFILE]", False, profile={"MMLU_PRO": 3, "MATH": 1})
    _refuse_case(lays, mk, "[GSWEEP-PROFILE]", False, one_cell=("MATH",))
    real_k = UAR.k_cells

    def k_patch(lay_):
        def bad(*a, **k):
            kc, ki = real_k(*a, **k)
            it = sorted(i for i in kc if kc[i] != UAR.NO_ROW)[0]
            kc[it] = kc[it] + "x"
            return kc, ki
        UAR.k_cells = bad

        def undo():
            UAR.k_cells = real_k
        return undo
    _refuse_case(lays, mk, "[GSWEEP-K0]", False, patch=k_patch)
    c0 = dict(lays["present"].common)
    tcb = dict(c0["train_counts"])
    tcb["MATH"] += 1
    _refuse_case(lays, mk, "[GSWEEP-TRAIN]", False, train_counts=tcb)
    capb = dict(c0["caps"])
    capb["MMLU_PRO"] -= 1
    _refuse_case(lays, mk, "[GSWEEP-TRAIN]", False, caps=capb)
    _refuse_case(lays, mk, "[GSWEEP-GATE]", False, n_gate_key=c0["n_gate_key"] + 1)
    real_g = ERC.gate_items

    def g_patch(lay_):
        ERC.gate_items = lambda rows_h, side: ([], {}, {})

        def undo():
            ERC.gate_items = real_g
        return undo
    _refuse_case(lays, mk, "no GATE item has a routing row", False, patch=g_patch)
    _refuse_case(lays, mk, "[GSWEEP-TC]", False, tc_k=(3,))
    _refuse_case(lays, mk, "B / seed", False, B=c0["B"] + 1)
    _refuse_case(lays, mk, "[GSWEEP-DENOM]", n_route=c0["n_route"] + 1)
    idn = c0["identity"]
    bump = lambda s: s[:-1] + str((int(s[-1]) + 1) % 10)      # noqa: E731
    _refuse_case(lays, mk, "[GSWEEP-IDENTITY]", identity=dict(idn, best=bump(idn["best"])))
    t_ = list(idn["g_af"])
    t_[1] = t_[1].replace("pp", "") + "1pp"
    _refuse_case(lays, mk, "[GSWEEP-IDENTITY]", identity=dict(idn, g_af=tuple(t_)))
    g = globals()
    real_tc = g["tc_cut"]

    def tc_patch(lay_):
        g["tc_cut"] = lambda tree, counts, alloc: ({lf: tree["root"] for lf in tree["leaves"]}, [tree["root"]])

        def undo():
            g["tc_cut"] = real_tc
        return undo
    _refuse_case(lays, mk, "[GSWEEP-TC-IDENTITY]", patch=tc_patch)
    real_hook = g["r2_hook"]

    def g3_patch(lay_):
        def hook2(D, I, arms, rec):
            h = real_hook(D, I, arms, rec)

            def h2(D_, wt, v):
                V.fit(D_, wt)                    # one extra policy fit per replicate: B + 2 checks no longer hold
                return h(D_, wt, v)
            return h2
        g["r2_hook"] = hook2

        def undo():
            g["r2_hook"] = real_hook
        return undo
    _refuse_case(lays, mk, "[G3]", patch=g3_patch)

    def b3_patch(lay_):
        pol_p = os.path.join(lay_.tmp, "res", "scratch", "pol.json")
        pol = U.json.load(open(pol_p, encoding="utf-8"))
        key = sorted(k for k in pol["tree_cell"] if pol["tree_cell"][k] is not None)[0]
        pol["tree_cell"][key] = sorted(set(pol["roster"]) - {pol["tree_cell"][key]})[0]
        with open(pol_p, "w", encoding="utf-8") as f:
            U.json.dump(pol, f)
        lay_.common = dict(lay_.common, uar_policy_sha=U.sha256_bytes(pol_p))
        return None
    _refuse_case(lays, mk, "[B3]", patch=b3_patch)
    real_bc = g["build_cells"]

    def drop_patch(lay_):
        def bc_drop(say, P_):                    # after the K0 re-derivation: one scored EVAL item loses its AF cell
            ev = sorted(i for i, (_c, s_) in lay_.fx.side.items() if s_ == "EVAL" and i in P_["af"] and P_["af"][i] != UAR.NO_ROW)
            P_["af"] = {k: v for k, v in P_["af"].items() if k != ev[0]}
            return real_bc(say, P_)
        g["build_cells"] = bc_drop

        def undo():
            g["build_cells"] = real_bc
        return undo
    _refuse_case(lays, mk, "[G14-NOROW] AF-U", False, patch=drop_patch)
    lay = _clone(lays["present"], mk())
    os.makedirs(os.path.join(lay.tmp, "res", "gs"), exist_ok=True)
    open(os.path.join(lay.tmp, "res", "gs", "READ_STARTED"), "w").close()
    _t, err, _r = U.cap(_me(), run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_dry_run(lays, mk):
    lay = _clone(lays["present"], mk())
    text, err, _r = U.cap(_me(), dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (GRANULARITY-SWEEP; --dry-run" % U.POOL), ls[0]
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key read (TRAIN, GATE or EVAL)", "POOL CHECK (B0-2): rc 0",
         "ALLOCATION k 300: MMLU_PRO 208, BBH 1, MATH 60 (total 269); capped: MMLU_PRO", "COST (planned): 25 k-means fits")
    for bad in ("GS1 ->", "k* =", "G_KW(", "IDENTITY:", "PREDICTION", "GATE key:", "K0 RE-DERIVATION", "seed 0: KW", "D_lo ="):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "gs")), "the dry-run wrote under res/gs"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (GRANULARITY-SWEEP; --dry-run"), L[0]
    need(t, "5907 EVAL items in 5404 CK-CLOSE components (Kish 1.311)", "GATE 1944 key-complete items", "DEFF 1.847", "n_eff 3198",
         "SE(D) 0.620pp", "MDE80 one contrast 1.74pp, both jointly 1.99pp", VERDICT_LINE, "B = 2000 two-stage replicates (default_rng(42))",
         "default_rng(20261006)", "n* = ceil(1.311 x 2.8^2 x 0.30 / 0.10^2) = 309", "grid k [25, 50, 100, 200, 400] (interior [50, 100, 200]",
         "best single 0.6049, TRUE source 0.6150, AF-U leaf cell 0.6201, K_s K0 0.6271; C1 +2.67pp [+1.46pp, +3.89pp]; G_AF +1.52pp [+0.14pp, +2.91pp]",
         "L24828-L24840", "calls 0", "MMLU_PRO 6759", "GPQA 57")


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("constants", "the REAL registered constants, the allocation table 25..400 (398 at 400), n* 309, Support, bands", "plain"),
         ("alloc", "allocation vs an independent loop oracle; cap, surplus not re-allocated, min 1, the tie order", "plain"),
         ("tc_ward", "best-first cut (largest first, tie to the smaller id, overshoot, cap); Ward vs scipy cut_tree; nesting", "plain"),
         ("branches", "GS1 words / sub-reasons by value incl. lo = 0 and point = 0; F-GS; rule 8; seed-joint interval by hand; two NAIVE"
                      " intervals that decide wrongly; k* ties; P1-P6 bands inclusive; Brier", "plain"),
         ("run_present", "--run on the planted fixture: every G, the GATE curve, k*, D_lo / D_hi / F-GS (point, SE, interval) vs an"
                         " independent oracle; GS1 INTERIOR-MAX by the hand rule; write-once", "base"),
         ("run_absent", "--run on the null fixture: values vs the oracle; GS1 NOT-SHOWN with its sub-reason; F-GS NOT FIRED", "base"),
         ("refusals", "pool, manifest, policy sha, profile, K0, TRAIN counts / caps, GATE count / empty, TC availability, B / seed, DENOM,"
                      " IDENTITY, TC identity, B3, NOROW, marker; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, no key, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"constants": st_constants, "alloc": st_alloc, "tc_ward": st_tc_ward, "branches": st_branches, "run_present": st_run_present,
       "run_absent": st_run_absent, "refusals": st_refusals, "dry_run": st_dry_run, "branch_cover": st_branch_cover}


def build_layouts(tmpdir):
    with contextlib.redirect_stdout(io.StringIO()):
        return {"present": _layout(os.path.join(tmpdir, "present"), "present"), "absent": _layout(os.path.join(tmpdir, "absent"), "null")}


def selftest(only=None, quiet=False, base=None):
    import tempfile
    import shutil
    made, fails, ran = [], [], 0

    def mk():
        d = tempfile.mkdtemp(prefix="gs_")
        made.append(d)
        return os.path.join(d, "lay")
    HIT.clear()
    try:
        lays = base
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                if kind == "base" and lays is None:
                    d0 = tempfile.mkdtemp(prefix="gs_lay_")
                    made.append(d0)
                    lays = build_layouts(d0)
                with contextlib.redirect_stdout(io.StringIO()):
                    _FN[name]() if kind == "plain" else _FN[name](lays, mk)
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


def _mutant_one(args):
    """One mutant in a fresh process (sandbox temp via scratch_dir): edit the code ABOVE the SELFTEST marker in memory, execute it,
    run the selftest on layouts built by the UNEDITED module; KILLED iff the selftest fails."""
    name, old, new = args
    import tempfile
    import shutil
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    mark = "\n# " + chr(0x2550) * 2 + " SELFTEST"
    cut = src.index(mark)
    head = src[:cut]
    if old and head.count(old) != 1:
        return name, "NOT APPLIED (%d matches)" % head.count(old)
    d = tempfile.mkdtemp(prefix="gs_mut_")
    try:
        lays = build_layouts(d)
        mod = types.ModuleType("granularity_sweep_mutant")
        mod.__file__ = os.path.abspath(__file__)
        exec(compile((head.replace(old, new) if old else head) + src[cut:], mod.__file__, "exec"), mod.__dict__)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                mod.selftest(quiet=True, base=lays)
            res = "SURVIVED"
        except BaseException as e:   # noqa: B902
            res = "KILLED (%s)" % type(e).__name__
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return name, res


def run_mutants(only=None, workers=4):
    import subprocess
    todo = [m for m in MUTANTS if not only or any(m[0].startswith(o) for o in only)]
    rows = []
    procs = []
    code = ("import sys, json; sys.path.insert(0, %r); import granularity_sweep as G; "
            "m = [x for x in G.MUTANTS if x[0] == sys.argv[1]][0]; print('RESULT ' + json.dumps(G._mutant_one(m)))") % HERE
    pending = list(todo)
    while pending or procs:
        while pending and len(procs) < workers:
            m = pending.pop(0)
            procs.append((m[0], subprocess.Popen([sys.executable, "-c", code, m[0]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                 env=dict(os.environ))))
        still = []
        for nm, p in procs:
            if p.poll() is None:
                still.append((nm, p))
                continue
            outp = p.stdout.read().decode("utf-8", "replace")
            mm = [ln for ln in outp.splitlines() if ln.startswith("RESULT ")]
            res = U.json.loads(mm[-1][7:])[1] if mm else "ERROR (%s)" % outp.strip().splitlines()[-1:]
            rows.append((nm, res))
            print("  %-78s %s" % (nm, res), flush=True)
        procs = still
        if procs:
            import time
            time.sleep(1)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    bad = [n for n, r in rows if not (r.startswith("KILLED") or r == "SURVIVED")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied / errors %s" % (
        TAG, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "", ""),
    ("X01 GS1: EDGE clause removed (k* at an end can decide)", "    if kstar not in interior:", "    if False:"),
    ("X02 GS1: D lower bound >= 0 (boundary)", 'elif not d["lo"] > 0:', 'elif not d["lo"] >= 0:'),
    ("X03 GS1: D point clause removed", '        if not d["point"] > 0:' + NL + '            bad.append', '        if False:' + NL + '            bad.append'),
    ("X04 GS1: D_hi never checked (first site only)", 'for nm, d in (("D_lo", dlo), ("D_hi", dhi)):' + NL + '        if not d["point"] > 0:',
     'for nm, d in (("D_lo", dlo),):' + NL + '        if not d["point"] > 0:'),
    ("X05 D_hi against k_lo (wrong arm)", 'st["dhi"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_hi"]))', 'st["dhi"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_lo"]))'),
    ("X06 D_lo against k_hi (wrong arm)", 'st["dlo"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_lo"]))', 'st["dlo"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_hi"]))'),
    ("X07 k*: ties to the larger k", "if best is None or gate_mean[k] > gate_mean[best]:", "if best is None or gate_mean[k] >= gate_mean[best]:"),
    ("X08 k*: argmin (min<->max)", "if best is None or gate_mean[k] > gate_mean[best]:", "if best is None or gate_mean[k] < gate_mean[best]:"),
    ("X09 k* chosen on EVAL (wrong split side)", 'st["kstar"] = kstar_of(st["gate_mean"], grid)', 'st["kstar"] = kstar_of({k: st["G"][("KW", k)]["point"] for k in grid}, grid)'),
    ("X10 interval: seeds fixed (unit-only)", "t2 = [val(two[b], SD[b]) for b in range(len(two))]", "t2 = [val(two[b], range(ns)) for b in range(len(two))]"),
    ("X11 interval: i.i.d. replicates as two-stage", "return U.interval(point, t2, ti, n)", "return U.interval(point, ti, ti, n)"),
    ("X12 point: seed 0 only", "point = val(pt, range(ns))", "point = val(pt, [0])"),
    ("X13 F-GS: lo >= 0 (boundary)", 'fired = bool(f["point"] > 0 and f["lo"] > 0)', 'fired = bool(f["point"] > 0 and f["lo"] >= 0)'),
    ("X14 F-GS: direction reversed", 'st["fgs"] = st_sub("ALL", d_terms("KW", c["k_lo"], "KW", c["k_mid"]))', 'st["fgs"] = st_sub("ALL", d_terms("KW", c["k_mid"], "KW", c["k_lo"]))'),
    ("X15 F-GS NOT FIRED line dropped (skip path)",
     '        L.append("FALSIFIER F-GS: NOT FIRED (F-GS fires iff G_KW(%d) - G_KW(%d) > 0 with its 95%% lower bound > 0)" % (c["k_lo"], c["k_mid"]))', "        pass"),
    ("X16 rule-8 'not refuted' line dropped (skip path)", '        L.append("RULE 8: INTERIOR-MAX is not refuted (k* interior and both lower bounds > 0)")', "        pass"),
    ("X17 allocation: no minimum of 1", "min(max(1, fl[s]), int(caps[s]))", "min(fl[s], int(caps[s]))"),
    ("X18 allocation: cap ignored", "min(max(1, fl[s]), int(caps[s]))", "max(1, fl[s])"),
    ("X19 allocation: remainder to the smallest fractions", "-(q[s_] - fl[s_])", "(q[s_] - fl[s_])"),
    ("X20 allocation: one-cell source not subtracted", "    n = k - len(one_cell)", "    n = k"),
    ("X21 Ward cut replaced by index truncation", 'return np.asarray(CA.fit_ward(C, kk)["lab"], dtype=np.int64)', "return np.minimum(np.arange(n), kk - 1).astype(np.int64)"),
    ("X22 filing ignores the source (nearest of all centroids)", "return {it: UAR.file_by_source(vec[it], srcs[it], C, csrc) for it in items}",
     "return {it: int(np.argmax(C @ vec[it])) for it in items}"),
    ("X23 centroids not renormalised", "C[j] = s / np.linalg.norm(s)", "C[j] = s / float(m.sum())"),
    ("X24 k-means n_init 1", "lab, Cm = CA.skm_best(Xs, k, seed)", "lab, Cm = CA.skm_best(Xs, k, seed, 1)"),
    ("X25 TC: smallest count expanded first (min<->max)", "-counts.get(x, 0), x", "counts.get(x, 0), x"),
    ("X26 TC: tie to the larger node id", "u = sorted(inner, key=lambda x: (-counts.get(x, 0), x))[0]", "u = max(inner, key=lambda x: (counts.get(x, 0), x))"),
    ("X27 TC counts from the EVAL side (wrong split side)", 'side.get(it, (None, None))[1] == "TRAIN")', 'side.get(it, (None, None))[1] == "EVAL")'),
    ("X28 GATE: a cell without TRAIN mass picks model 0", "q = gb if q < 0 else q", "q = 0 if q < 0 else q"),
    ("X29 G against the placebo (wrong baseline)", "[[(col(arm_name(kind, k, s)), 1.0), (V.BS, -1.0)] for s in SEEDS]",
     "[[(col(arm_name(kind, k, s)), 1.0), (V.PLAC, -1.0)] for s in SEEDS]"),
    ("X30 D: difference sign flipped", "(tb[s][0][0], -1.0)", "(tb[s][0][0], 1.0)"),
    ("X31 identity refusal removed", '    if not ok:' + NL + '        hit("REFUSE.IDENTITY")', '    if False:' + NL + '        hit("REFUSE.IDENTITY")'),
    ("X32 TC identity refusal removed", 'if not (tco and abs(a_tc - float(bt["point"][0, V.TREE])) < 1e-12):', "if False:"),
    ("X33 TRAIN-count refusal removed", 'if dict(cnt) != dict(c["train_counts"]) or any(cnt[s] // c["cap_div"] != caps[s] for s in caps):', "if False:"),
    ("X34 caps clause dropped from the TRAIN check", 'if dict(cnt) != dict(c["train_counts"]) or any(cnt[s] // c["cap_div"] != caps[s] for s in caps):',
     'if dict(cnt) != dict(c["train_counts"]):'),
    ("X35 GATE-count refusal removed", 'if len(gk["comp"]) != int(c["n_gate_key"]):', "if False:"),
    ("X36 profile refusal removed", 'if prof != dict(c["profile"]) or tuple(sorted(S["single"])) != tuple(sorted(c["one_cell"])):', "if False:"),
    ("X37 K0 re-derivation refusal removed", "if diff or set(kc) != set(k0):", "if False:"),
    ("X38 pre-read write-once check removed", '        if os.path.exists(U.P(p)):' + NL + '            hit("REFUSE.WRITE_ONCE")', '        if False:' + NL + '            hit("REFUSE.WRITE_ONCE")'),
    ("X39 support: TRAIN > n* (boundary)", "big = ntr >= n_star", "big = ntr > n_star"),
    ("X40 P1 read against the first band at every k", "ok = U.in_band(x, PRED_P1[j])", "ok = U.in_band(x, PRED_P1[0])"),
    ("X41 P2 Brier on a fixed outcome", "U.brier(PROB_P2, p2)", 'U.brier(PROB_P2, "INTERIOR")'),
    ("X42 P4 'lower at 400' direction reversed", 'p4b = "LOWER" if r_hi < r_mid else "NOT-LOWER"', 'p4b = "LOWER" if r_hi > r_mid else "NOT-LOWER"'),
    ("X43 P6 NOT SCOREABLE line dropped (skip path)",
     '        L.append("PREDICTION P6 TC - KW at %d -0.3pp [-1.5, +0.9]: NOT SCOREABLE (TC not available at %d)" % (c["k_mid"], c["k_mid"]))', "        pass"),
    ("X44 TC availability refusal removed", 'if tuple(tcs) != tuple(c["tc_k"]):', "if False:"),
    ("X45 D_lo on NON_BBH (wrong population)", 'st["dlo"] = st_sub("ALL", d_terms("KW", ks, "KW", c["k_lo"]))', 'st["dlo"] = st_sub("NON_BBH", d_terms("KW", ks, "KW", c["k_lo"]))'),
    ("X46 GATE gain without the best-single baseline", "return float(np.mean(r)) - float(np.mean(b_))", "return float(np.mean(r))"),
    ("X47 GS1 interior set = the whole grid", 'word, why = gs1_verdict(ks, c["interior"], dlo, dhi)', 'word, why = gs1_verdict(ks, c["grid"], dlo, dhi)'),
    ("X48 empty GATE refusal removed (zero sites)", '    if not gits:' + NL + '        hit("REFUSE.GATE_EMPTY")', '    if False:' + NL + '        hit("REFUSE.GATE_EMPTY")'),
    ("X49 seed draws on the unit stream's seed", 'SD = seed_draws(B, c["seed_draw"], len(SEEDS))', 'SD = seed_draws(B, c["seed"], len(SEEDS))'),
    ("X50 G3 fit-count refusal removed", 'if D.fit_asserts != c["B"] + 2:', "if False:"),
    ("X51 KW top fit at seed 0 for every seed (seed-0-only)", "cents = source_fit(Xt, tsrc, allocs[ktop], s)", "cents = source_fit(Xt, tsrc, allocs[ktop], 0)"),
    ("X52 KF fits at the top allocation (k ignored)", "cf = source_fit(Xt, tsrc, allocs[k], s)", "cf = source_fit(Xt, tsrc, allocs[ktop], s)"),
)


if __name__ == "__main__":
    sys.exit(main())
