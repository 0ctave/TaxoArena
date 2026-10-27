"""DEEP-SPLIT-COMPARE (lane r2): holding B0's anchors and depth-2 frontier fixed, does a different label-free split rule below
depth 2 (flat spherical k-means; PCA-GMM) file EVAL better than the vMF construction, and how much of class-conditioned
k-means' edge is label information below depth 2? ZERO calls: no judge, no LLM, no embedding call, no build; no DB is opened by
the readout (the B0-2 pool check, a reader, runs as its own process first).

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-10-02 (before any code or call) — DEEP-SPLIT-COMPARE:
holding B0's anchors and depth-2 frontier fixed, ..." (L23125ff _as_of 00dea46b; draft docs/agents/plans/2026-10-02_deep_split_compare.md
29ea00ea blob:ec62ddef), with the orchestrator's rulings Q2 "A is not rebuilt" and Q3 "C-BIC kept, DESCRIPTIVE-ONLY", and the
registrar's Support (d)/(e) unrounded figures. DEVIATION (the orchestrator's brief, 2026-10-02): the pool check is
g13_breakdown's B0-2 form, not the registration's "pool_guard on pv2_1575de61bb20e977" (pool_guard holds no pv2 pool;
READY_g13_breakdown 7e6858eb D-1). Verdict words printed HELD / REVERSED / UNDETERMINED (the results JSON records REVERSED as
FAILED (REVERSED), the registrar's vocabulary).

OBJECTS (lane r2, commit M 2703f2c2; every path under experiment_results/archv2/rp12_r2/, refused outside it by rp12_lane):
  read through g13_breakdown.load_objects UNCHANGED (its I0 provenance, I2 descent, I3 argmax-vmfMu, I4 structure and I5 support
  checks all run): bundle B0/readouts/g13_bundle_flatleaf.{npz,json} (check_sides: no EVAL or GATE item in any fit), the flatLeaf
  CSVs (an item's leaf = modal leaf_id; MC-EXCLUDE as in G13), the six member snapshots' LAST lines, the eight run manifests.
  The anchor labels are read here from the same six snapshot last lines (member depth 1 = union depth 2).
  Pinned modules (blob, LF), imported unchanged: g13_breakdown.py c29fa1c3, g13_comparator.py 61d83ec7, rp12_pairing.py 35214b3f
  (g13_breakdown checks rp12_lane ac25b152; g13_comparator checks flat_mix_mmlu 555ae3ac).
  POOL: g13_breakdown.pool_check_v2 (the B0-2 form: v2_union_pool.py --dry-run, engine pool file sha256-lf pin, empty -wal /
  -journal), NOT pool_guard.py (the orchestrator's brief; pool_guard holds no pv2 pool).

THE ARMS (52 depth-2 cells = B0's anchors; every EVAL item filed by argmax cos(x, cell centroid) over ALL cells of the arm, no
anchor or source oracle; a cell is NAMED by the TRAIN-majority class (tie: smaller class name) of the TRAIN items the same rule
files into it; a cell with no TRAIN item takes its anchor's class, counted):
  A    B0 as built: P_fl of record (the bundle's eval_fl, the leaves CSV naming); one construction, no seeds.
  B    per split anchor a (k_a >= 2): FM.spherical_kmeans(F-tree(a), k_a, seed s, max_iter 300); unsplit anchors: one cell =
       normalised mean of F-tree(a). F-tree(a) = the TRAIN items whose graft_flatleaf leaf lies under a.
  C    per split anchor: PCA on F-tree(a) (centred, unwhitened; numpy SVD, each axis' largest-|loading| sign made positive) to
       d = 16, then sklearn GaussianMixture(k_a, covariance_type='diag', init_params='k-means++', n_init=1, max_iter=200,
       reg_covar=1e-6, random_state=s); hard partition by maximum responsibility; each non-empty component's centroid =
       normalised 512-d mean of its members (an empty component is dropped and counted); cosine filing as A / B.
  D    KC_s exactly as g13_breakdown.identity_arms computes it (g13_comparator.kc_prototypes, k_c from leaf_major).
  Descriptive (never deciding): B-gt (fit set = TRAIN of a's declared class), B-anc (fit set = TRAIN whose nearest anchor
  vmfMu is a, over the 52 anchors), B-bis (bisecting spherical 2-means, always the largest cell, first on ties, to k_a cells),
  C-32 / C-64 (C at d = 32 / 64), C-BIC (per split anchor k = argmin BIC over 1..2k_a+1, ties to the smaller k; unsplit anchors 1).
  Seeds 0..4 for every seeded arm; s = 0 is the comparator of record; spread = max - min over the five seeds.

IDENTITY PRECONDITIONS (each REFUSES before any new number prints):
  I1 g13_breakdown.check_i1 on g13_breakdown.identity_arms: P_fl 0.8119, P(KC_s) 0.8334 / 0.8394 / 0.8340 / 0.8446 / 0.8413,
     D13 -0.0215 [-0.0301, -0.0125] (plus G13-BREAKDOWN's U-global seeds and NCC 0.8065, which check_i1 also holds); and
     G13-BREAKDOWN's depth-2 numbers: |F(2)| 52 (0 <empty>), k_c(2) = 1 for every class, KC(2)_s = NCC item-wise on every seed,
     P_tree(2) 0.8042, D(2) -0.0023 [-0.0108, +0.0064].
  I2 52 anchors labelled one-to-one with the 52 classes; 133 leaves; k_a and subtree max union depth per anchor = the table;
     k_a summed per source 74 / 36 / 9 / 6 / 5 / 3; internal nodes at union depth >= 2: 79 binary + 1 ternary.
  I3 F-tree covers all 12,334 TRAIN items; per-anchor F-tree, B-anc and class counts = the table (section 4 of the draft).
     [DEFECT handed to the registrar 2026-10-02, see the commit message: the draft's F-tree column counts CSV ROWS, not items
     (it sums to 12,951 over 12,334 items; e.g. GPQA/Chemistry 256 rows / 114 items); the k_a, depth, B-anc and class columns
     match the bundle exactly. CORRECTED 2026-10-02 on the orchestrator's instruction (the registrar bracketing I3 to item
     counts): the F-tree column now holds the item counts (19 anchors changed; sum 12,334).]
  I4 B with k_a = 1 for every anchor reproduces NCC-on-F-tree item-wise (an independent loop; the point printed by --run).
  Also refused: R3's true-anchor strata denominators different from Support (a).

READOUTS: R1 overall, R2 per source (MMLU_PRO_LB scoreable, the others descriptive), R3 per depth (true-anchor subtree depth,
true-anchor k_a bin, A's flatLeaf leaf depth), R4 GMM soft-assignment entropy (C_0; EVAL and TRAIN items filed into a split
anchor; descriptive), R5 fit times (descriptive). Paired differences, whole-component bootstrap (g13_comparator.boot, B 2,000,
seed 20260929) via g13_breakdown.stat; stratum intervals re-index the stratum's components.
CRITERIA: C-AB / C-AC / C-DB: G13's form (interval AND point beyond the comparator's spread; C-DB's bar max(spread_B,
spread_KC)); C-AB-M / C-AC-M / C-DB-M: MMLU_PRO_LB, interval alone, "seed-fragile" appended when |D| < the stratum spread. F-RULE
fires iff the lower ends of BOTH D_AB and D_AC exceed -0.0108. Read separately, no family-wise correction.
IMPLEMENTATION CHOICES (for the READY to confirm or refuse): (i) the R3 strata use the item's TRUE class's anchor; their
denominators are refused unless equal to Support (a); (ii) descriptive arms B-gt / B-anc take the normalised mean of their own
fit set at unsplit anchors; (iii) R4 reads, for each item filed by C_0 into a cell of a split anchor, the responsibilities of
that anchor's GMM at the item's PCA projection (H in nats, H / log k_a, share with max responsibility > 0.9); per source and per
the filed anchor's k_a bin; (iv) R5 times each arm's per-anchor fits (PCA inside C's time) with perf_counter, vectors in memory;
(v) both consequence sentences print when both apply (registered as two independent "if"s); (vi) "within 0.005 of each other"
is scored as max - min over P_A, P(B_0), P(C_0), P(D_0) in the k_a = 1 stratum, band [0, 0.005].
Not applicable (no judge verdicts, no posting): wrong(established), tie conventions A / B, --pilot / truncation guard, a call
cache. Verdict words: HELD / REVERSED / UNDETERMINED; F-RULE FIRES / DOES NOT FIRE.

SELFTEST (--selftest; synthetic lane-r2 layouts written by g13_breakdown._fixture_write with this script's geometry, read through
main(), the real entry point; pool check, machine probe and clock stubbed; a counting clock makes every fit exactly 1.000 s):
  fixture H (12-d axes; MMLU_PRO_LB x (split, leaves unit(e0+e1) and e6), y (unsplit, unit(e2+0.3e8)); BBH u (unit(e3+0.5e9)),
  v (e4); TRAIN x@e0 20, y@e1 12, y@e2 20, x@e8 6, u 20, v 20; EVAL x@e0 20, y@e1 20, y@e2 20, x@e8 30, u 20, v 20,
  v@unit(e4+3e9) 10 = 140 in 70 components), by hand: P_A 0.5714, P(B_s) = P(C_s) 0.7857, P(D_s) 1.0000, D_AB = D_AC -0.2143,
  D_DB +0.2143, D13 -0.4286; MMLU D_AB-M -0.2222, D_DB-M +0.3333 (shares of D_DB 1.0000 / 0.0000, of D13 0.8333 / 0.1667); BBH
  D_AB -0.2000; R3 k_a 1: 90 items D_AB -0.3333, D_DB 0; k_a 2-3: 50 items D_AB 0, D_DB +0.6000; 4-7 / >= 8 empty (n = 0 lines);
  B-gt 1.0000; verdicts C-AB / C-AC REVERSED, C-DB HELD, -M likewise; F-RULE DOES NOT FIRE; "split rule implicated".
  fixture P (A's leaves at the cluster centres e0 / e1, u leaf e3): A = B item-wise, D_AB = 0 exactly, F-RULE FIRES, C-DB HELD,
  "label information" consequence. fixture S (TRAIN x@e6 8, EVAL x@e6 10: three clusters under x at k_a = 2): each seed's B
  partition identified by an oracle k-means, its P computed by hand from the partition (0.6429 / 0.7857 / 0.7143), spread_B
  checked; P(D_s) 1.0000 on every seed.
  summarize: synthetic per-seed vectors (seed 4 / seed 1 carry the extremes and item-wise differences): spreads over all five
  seeds, s = 0 comparator, C-DB's bar max(spread_B, spread_KC) separating HELD from UNDETERMINED, the -M interval-only reading,
  F-RULE on lower ends (lo < -0.0108 < hi), per-source and stratum values, an empty stratum. filing: a tight and a broad cluster
  where cosine and GMM likelihood disagree, run through fit_arms (C files by cosine on every seed); an empty GMM component dropped.
  branches: every verdict / falsifier / consequence branch printed with its values. refusals: lane r1, I1, depth 2 (point, hi),
  I2 (anchors, child counts), I2/I3 table (F-tree, B-anc, k_a), R3 support (k_a, depth), side check (a TRAIN item marked EVAL),
  I4, pool check (its line printed first); no outcome written. pool (2026-10-02, delta for the I3 / B0-2 brackets): the REAL
  g13_breakdown.pool_check_v2 through --dry-run (only v2_union_pool.py's child replaced, its argv asserted): a 7-byte -wal, the
  pin 79d48f4b... missed, child rc 1, a wrong first line, no "every check passed" line each REFUSE with the POOL line first and
  nothing after it; the pass prints both child lines and the "(pinned)" sha and the dry-run reaches I1 / I3.
MUTANTS (--mutants; one in-memory edit each, the targeted selftest subset re-run; 2026-10-02): M00 control SURVIVED (as it must);
  KILLED: M01 EVAL rows in the B fit | M02 B fit set = GT membership | M03 k_a off by one | M04 filing within the true anchor
  (oracle) | M05 C filed by likelihood | M06 naming from EVAL | M07 spread_C over 4 seeds | M08 source stratum leaks | M09 spread
  min<->max | M10 D_DB sign | M11 C-DB bar spread_B only | M12 point clause dropped | M13 -M with the spread clause | M14
  seed-fragile omitted | M15 F-RULE on upper ends | M16 F-RULE with OR | M17 F-RULE silent when not firing | M18 consequence
  omitted | M19 comparator B_1 | M20 empty stratum unhandled | M21 R3 strata from A's output | M22 write-once removed | M23 exists
  check removed | M24 I1 removed | M25 depth-2 removed | M26 I2 child counts removed | M27 I3 table removed | M28 lane guard
  removed | M29 pool refusal removed | M30 dry-run prints a statistic | M31 share over n_s | M32 unsplit cell at the anchor vmfMu
  | M33 I4 removed | M34 pool check not B0-2 | M35 full covariance | M36 primary PCA 32 | M37 side check not passed | M38 R2
  first source only | M39 -M on the overall population | M40 B on the first anchor only | M41 NOT SCORED skipped on NaN | M42
  printed C-DB bar | M43 empty GMM component kept | M44 B0-2 pin overridden | M45 g13 hooks not handed this config | M46 pool
  line not printed before the refusal | M47 pool check on a hard-coded pool id | M48 pool check skipped in --dry-run: 48 of 48 KILLED.

  python tools/analysis/deep_split_compare.py --selftest
  python tools/analysis/deep_split_compare.py --mutants
  python tools/analysis/deep_split_compare.py --dry-run --lane r2   # B0-2 pool check first; pins; I0-I5, I1 + depth-2 (SEEN), I2, I3, I4; NO new statistic
  python tools/analysis/deep_split_compare.py --run --lane r2       # the readout; outcome WRITE-ONCE (mode x)
Output: experiment_results/archv2/rp12_r2/deep_split_compare_outcome.txt (write-once). stdout: run with PYTHONIOENCODING=utf-8.
"""
import os
import sys

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import io            # noqa: E402
import json          # noqa: E402
import time          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import contextlib    # noqa: E402
import warnings      # noqa: E402
from collections import Counter, defaultdict   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[DSC]"
PINS = (("g13_breakdown.py", "c29fa1c3d3b7837ede6c53f1b98bf32dcd97ca40"),
        ("g13_comparator.py", "61d83ec7dfed00b834d5b2e5d0ca355d236520db"),
        ("rp12_pairing.py", "35214b3f11c3ffe4c1174885316f89775442f5c3"))


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import g13_breakdown as GB   # noqa: E402  (checks g13_comparator, rp12_pairing, rp12_lane; g13_comparator checks flat_mix_mmlu)
G, FM, RP, LN = GB.G, GB.FM, GB.RP, GB.LN
SEEDS = G.SEEDS
RES = GB.RES
EMPTY = GB.EMPTY

# ── the registered constants ────────────────────────────────────────────────────────────────────────────────────────────
# anchor (= class) -> (k_a, subtree max union depth, F-tree, B-anc, class TRAIN): the draft's section-4 table, with the F-tree
# column as ITEM counts (12,334) per the registrar's I3 bracket (the draft counted CSV rows, 12,951)
_T = {}


def _rows(src, names, ka, maxd, ft, ba, cl):
    for i, nm in enumerate(names):
        _T["%s/%s" % (src, nm)] = (ka, maxd, ft[i], ba[i], cl[i])


for _nm, _r in (("math", (9, 7, 741, 418, 793)), ("physics", (7, 6, 753, 691, 778)), ("other", (7, 5, 505, 438, 555)),
                ("psychology", (7, 5, 534, 516, 476)), ("economics", (6, 5, 478, 474, 504)), ("biology", (6, 5, 411, 395, 381)),
                ("health", (5, 5, 386, 395, 410)), ("chemistry", (5, 5, 796, 743, 676)), ("computer science", (5, 5, 446, 445, 243)),
                ("law", (5, 5, 551, 557, 578)), ("history", (3, 4, 254, 259, 238)), ("engineering", (3, 4, 429, 424, 580)),
                ("business", (3, 4, 460, 469, 467)), ("philosophy", (3, 4, 291, 278, 298))):
    _T["MMLU_PRO_LB/" + _nm] = _r
_T["IFEVAL/ifeval"] = (5, 4, 296, 290, 325)
_rows("MATH", ["Intermediate Algebra", "Algebra"], 2, 3, [154, 151], [172, 201], [166, 177])
_rows("MATH", ["Precalculus", "Number Theory", "Prealgebra", "Geometry", "Counting & Probability"], 1, 2,
      [69, 121, 72, 126, 102], [88, 153, 167, 140, 192], [80, 91, 110, 80, 69])
_rows("MUSR", ["team_allocation", "murder_mysteries", "object_placements"], 2, 3, [150, 148, 156], [150, 149, 156], [150, 148, 156])
_rows("GPQA", ["Biology", "Physics", "Chemistry"], 1, 2, [56, 90, 114], [94, 194, 136], [64, 137, 130])
_rows("BBH", ["tracking_shuffled_objects_seven_objects", "sports_understanding", "temporal_sequences", "logical_deduction_five_objects",
              "formal_fallacies", "date_understanding", "disambiguation_qa", "web_of_lies", "movie_recommendation", "ruin_names",
              "salient_translation_error_detection", "object_counting"], 2, 3,
      [197, 154, 150, 232, 150, 146, 149, 150, 150, 150, 150, 150], [158, 161, 150, 170, 171, 147, 150, 152, 159, 151, 151, 150],
      [160, 149, 150, 170, 150, 142, 148, 150, 150, 150, 150, 150])
_rows("BBH", ["tracking_shuffled_objects_five_objects", "hyperbaton", "geometric_shapes", "boolean_expressions",
              "tracking_shuffled_objects_three_objects", "causal_judgement", "logical_deduction_three_objects",
              "logical_deduction_seven_objects", "snarks", "penguins_in_a_table", "reasoning_about_colored_objects", "navigate"], 1, 2,
      [120, 152, 150, 150, 151, 104, 140, 99, 109, 88, 153, 150], [159, 153, 151, 155, 151, 104, 146, 155, 108, 88, 160, 150],
      [156, 150, 150, 150, 151, 103, 145, 155, 107, 88, 150, 150])
ANCHOR_TABLE = dict(_T)

REG = dict(GB.REG)
REG.update(
    out=RES + "/deep_split_compare_outcome.txt",
    anchors=ANCHOR_TABLE, n_anchors=52, children={2: 79, 3: 1},
    pca=16, pca_sens=(32, 64), gmm_iter=200, reg_covar=1e-6,
    ka_bins=((1, 1), (2, 3), (4, 7), (8, 99)),
    r3_ka={(1, 1): (1215, 1002), (2, 3): (2066, 1834), (4, 7): (2465, 2421), (8, 99): (393, 380)},
    r3_depth={2: 1215, 3: 1284, 4: 944, 5: 1916, 6: 387, 7: 393},
    depth2=dict(n_f2=52, n_empty=0, p_tree2="0.8042", d2="-0.0023", lo2="-0.0108", hi2="+0.0064"),
    frule=-0.0108,
)
_CFG = [REG]


def cfg():
    return _CFG[0]


# Registered Support (d)/(e) [REGISTRAR, unrounded]: (SE, MDE80, planning discordance, transported DEFF) per deciding statistic
SUPPORT_REG = {"C-AB": (0.00418, 0.0117, 0.08, 1.341), "C-AC": (0.00467, 0.0131, 0.10, 1.341), "C-DB": (0.00398, 0.0111, 0.08, 1.214),
               "C-AB-M": (0.00601, 0.0168, 0.12, 1.046), "C-AC-M": (0.00649, 0.0182, 0.14, 1.046), "C-DB-M": (0.00601, 0.0168, 0.12, 1.046)}

PRED = {
    "P(B_0)": (0.815, (0.800, 0.830)), "D_AB": (-0.003, (-0.018, 0.012)), "spread_B": (0.008, (0.004, 0.016)),
    "P(C_0)": (0.808, (0.790, 0.825)), "D_AC": (0.004, (-0.012, 0.020)), "spread_C": (0.012, (0.006, 0.025)),
    "D_DB": (0.018, (0.005, 0.032)),
    "D_AB-M": (-0.005, (-0.030, 0.020)), "D_AC-M": (0.005, (-0.020, 0.030)), "D_DB-M": (0.035, (0.015, 0.055)),
    "P(B-gt_0) - P(D_0)": (-0.003, (-0.010, 0.004)), "P(B-anc_0) - P(B_0)": (-0.020, (-0.050, 0.000)),
    "P(B-bis_0) - P(B_0)": (-0.002, (-0.010, 0.006)), "C-BIC total k": (133, (90, 260)),
    "P(C-BIC_0) - P(C_0)": (0.000, (-0.015, 0.015)), "P(C-32_0) - P(C_0)": (0.000, (-0.010, 0.010)),
    "P(C_0) - P(C-64_0)": (0.005, (-0.005, 0.020)),
    "R3 share of D_DB in the k_a >= 4 strata": (0.8, (0.5, 1.1)),
    "R3 k_a = 1 stratum: max - min of P_A, P(B_0), P(C_0), P(D_0)": (None, (0.0, 0.005)),
    "R4 mean H / log k_a (EVAL)": (0.08, (0.02, 0.25)), "R4 share with max responsibility > 0.9 (EVAL)": (0.80, (0.55, 0.95)),
    "R5 B fit per seed, median (s)": (None, (0.05, 1.0)), "R5 C fit per seed, median (s)": (None, (0.5, 20.0)),
}
PROB = (("C-AB", "HELD 0.10, REVERSED 0.25, UNDETERMINED 0.65"), ("C-AC", "HELD 0.15, REVERSED 0.10"), ("C-DB", "HELD 0.60, REVERSED 0.03"),
        ("C-AB-M", "REVERSED 0.25"), ("C-AC-M", "HELD 0.15, REVERSED 0.15"), ("C-DB-M", "HELD 0.65"), ("F-RULE", "fires 0.45"))

# hooks the selftest swaps (nothing else writes them)
_CLOCK = [time.perf_counter]
_ROOT = [ROOT]
_SIDES = [GB._committed_sides]
_POOL_GUARD = [GB.pool_check_v2]
_MACHINE = [GB._machine_state]


# ── small helpers ───────────────────────────────────────────────────────────────────────────────────────────────────────

def spread(vals):
    vals = [float(v) for v in vals]
    return max(vals) - min(vals)


def unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def timed(fn, *a, **k):
    t0 = _CLOCK[0]()
    r = fn(*a, **k)
    return r, _CLOCK[0]() - t0


def v_spread(d, lo, hi, bar):
    """C-AB / C-AC / C-DB (G13's form): HELD iff wholly above 0 AND d > bar; REVERSED iff wholly below 0 AND d < -bar."""
    if lo > 0 and d > bar:
        return "HELD"
    if hi < 0 and d < -bar:
        return "REVERSED"
    return "UNDETERMINED"


def v_interval(lo, hi):
    """C-AB-M / C-AC-M / C-DB-M (C-a1's form): the interval alone decides."""
    if lo > 0:
        return "HELD"
    if hi < 0:
        return "REVERSED"
    return "UNDETERMINED"


def f_rule(lo_ab, lo_ac, bar):
    """F-RULE fires iff BOTH lower ends lie above the registered bar (-0.0108 = -|D13| / 2)."""
    return bool(lo_ab > bar) and bool(lo_ac > bar)


def ka_bin(k):
    for lo, hi in cfg()["ka_bins"]:
        if lo <= k <= hi:
            return (lo, hi)
    refuse("k_a %d falls in no registered bin" % k)


def bin_name(b):
    lo, hi = b
    return "%d" % lo if lo == hi else (">= %d" % lo if hi >= 99 else "%d-%d" % (lo, hi))


# ── anchors (I2, I3) ────────────────────────────────────────────────────────────────────────────────────────────────────

def load_anchors(o):
    """Anchors = union depth-2 nodes, their labels from the six member snapshots' LAST lines; I2 and I3 refused on any miss."""
    c, root = cfg(), o["root"]
    label = {}
    for mdir, source in c["members"]:
        snap = GB.last_snapshot(GB.P(root, "%s/%s/seed_42/dag_snapshots.jsonl" % (c["b0"], mdir)))
        for n in snap["nodes"]:
            label["%s:%s" % (source, n["id"])] = n["label"]
    nodes, classes = o["nodes"], o["classes"]
    anchors = sorted(u for u, n in nodes.items() if n["depth"] == 2)
    labs = [label[u] for u in anchors]
    if len(anchors) != c["n_anchors"] or sorted(labs) != sorted(classes) or len(set(labs)) != len(labs):
        refuse("I2: %d depth-2 anchors labelled %s, not %d anchors one-to-one with the %d classes"
               % (len(anchors), sorted(labs)[:4], c["n_anchors"], len(classes)))
    ci = {cl: k for k, cl in enumerate(classes)}
    a_cls = np.array([ci[label[u]] for u in anchors])
    a_of = {u: k for k, u in enumerate(anchors)}
    leaf_anchor = {u: a_of[o["anc"][u][2]] for u in o["leaves"] if 2 in o["anc"][u]}
    if len(leaf_anchor) != len(o["leaves"]):
        refuse("I2: %d leaves lie above union depth 2" % (len(o["leaves"]) - len(leaf_anchor)))
    ka = np.zeros(len(anchors), dtype=int)
    maxd = np.zeros(len(anchors), dtype=int)
    for u, a in leaf_anchor.items():
        ka[a] += 1
        maxd[a] = max(maxd[a], nodes[u]["depth"])
    kids = Counter(n["parent"] for n in nodes.values() if n["parent"] is not None)
    hist = Counter(kids[u] for u, n in nodes.items() if n["depth"] >= 2 and not n["leaf"])
    if dict(hist) != dict(c["children"]):
        refuse("I2: internal nodes at union depth >= 2 have child counts %s, not %s" % (dict(sorted(hist.items())), c["children"]))
    ksrc = Counter()
    for a, u in enumerate(anchors):
        ksrc[nodes[u]["src"]] += int(ka[a])
    if dict(ksrc) != dict(c["leaves_by_source"]):
        refuse("I2: k_a summed per source %s, not %s" % (dict(sorted(ksrc.items())), c["leaves_by_source"]))
    # fit sets (I3)
    t_anchor = np.array([leaf_anchor[u] for u in o["tleaf"]])
    amu = np.vstack([nodes[u]["mu"] for u in anchors])
    t_banc = np.argmax(o["Xt"] @ amu.T, axis=1)
    ftree = [np.flatnonzero(t_anchor == a) for a in range(len(anchors))]
    gt = [np.flatnonzero(o["yt"] == a_cls[a]) for a in range(len(anchors))]
    banc = [np.flatnonzero(t_banc == a) for a in range(len(anchors))]
    if sum(len(x) for x in ftree) != len(o["yt"]) or len(o["yt"]) != c["n_train"]:
        refuse("I3: F-tree covers %d of %d TRAIN items (registered %d)" % (sum(len(x) for x in ftree), len(o["yt"]), c["n_train"]))
    bad = []
    for a, u in enumerate(anchors):
        lab = label[u]
        want = c["anchors"].get(lab)
        got = (int(ka[a]), int(maxd[a]), len(ftree[a]), len(banc[a]), len(gt[a]))
        if want is None or tuple(want) != got:
            bad.append("%s %s (registered %s)" % (lab, got, want))
    if bad:
        refuse("I2/I3: %d anchor(s) differ from the registered table (k_a, max depth, F-tree, B-anc, class): %s"
               % (len(bad), "; ".join(bad)))
    e_anchor = np.array([int(np.flatnonzero(a_cls == y)[0]) for y in o["ye"]])
    return dict(anchors=anchors, label=label, a_cls=a_cls, ka=ka, maxd=maxd, ftree=ftree, gt=gt, banc=banc, amu=amu,
                leaf_anchor=leaf_anchor, hist=hist, ksrc=ksrc, e_anchor=e_anchor,
                a_src=np.array([nodes[u]["src"] for u in anchors]))


def check_r3_support(o, A):
    c = cfg()
    ka_e, md_e = A["ka"][A["e_anchor"]], A["maxd"][A["e_anchor"]]
    for b, want in c["r3_ka"].items():
        m = (ka_e >= b[0]) & (ka_e <= b[1])
        got = (int(m.sum()), len(set(o["comp"][m].tolist())))
        if got != tuple(want):
            refuse("R3: true-anchor k_a stratum %s holds %d EVAL items / %d components, not Support (a)'s %d / %d"
                   % ((bin_name(b),) + got + tuple(want)))
    for d, want in c["r3_depth"].items():
        if int((md_e == d).sum()) != want:
            refuse("R3: true-anchor subtree depth %d holds %d EVAL items, not Support (a)'s %d" % (d, int((md_e == d).sum()), want))


# ── the arms ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def bisect_kmeans(X, k, seed):
    clusters = [np.arange(len(X))]
    while len(clusters) < k:
        j = max(range(len(clusters)), key=lambda i: (len(clusters[i]), -i))
        idx = clusters.pop(j)
        r = FM.spherical_kmeans(X[idx], 2, seed, max_iter=G.MAX_ITER)
        a, b = idx[r["labels"] == 0], idx[r["labels"] == 1]
        if len(a) == 0 or len(b) == 0:
            refuse("B-bis: a bisection of %d items left one side empty" % len(idx))
        clusters[j:j] = [a, b]
    return np.vstack([unit(X[c].sum(axis=0)) for c in clusters])


def cells_kmeans(o, A, fitsets, k_of, seed, mode="kmeans"):
    """-> (centers (m, D), cell anchor (m,), fit seconds, dropped). Unsplit anchors: one cell = normalised mean of the fit set."""
    Xt = o["Xt"]
    cents, ca, t_fit = [], [], 0.0
    for a in range(len(A["anchors"])):
        idx = fitsets[a]
        if len(idx) == 0:
            refuse("anchor %s has an empty fit set" % A["label"][A["anchors"][a]])
        X, k = Xt[idx], int(k_of[a])
        if k == 1:
            cents.append(unit(X.sum(axis=0))[None, :])
            ca.append(a)
            continue
        if k > len(idx):
            refuse("anchor %s: k %d exceeds its %d fit items" % (A["label"][A["anchors"][a]], k, len(idx)))
        if mode == "bisect":
            C, t = timed(bisect_kmeans, X, k, seed)
        else:
            r, t = timed(FM.spherical_kmeans, X, k, seed, max_iter=G.MAX_ITER)
            C = r["centers"]
        t_fit += t
        cents.append(C)
        ca.extend([a] * len(C))
    return np.vstack(cents), np.array(ca), t_fit, 0


def pca_fit(X, d):
    if d >= len(X) or d > X.shape[1]:
        refuse("PCA to %d dims on %d items in %d dims" % (d, len(X), X.shape[1]))
    mu = X.mean(axis=0)
    _U, _S, Vt = np.linalg.svd(X - mu, full_matrices=False)
    V = Vt[:d].copy()
    for i in range(d):
        if V[i, np.argmax(np.abs(V[i]))] < 0:
            V[i] = -V[i]
    return mu, V


def gmm_fit(Z, k, seed):
    from sklearn.mixture import GaussianMixture
    gm = GaussianMixture(n_components=k, covariance_type="diag", init_params="k-means++", n_init=1, max_iter=cfg()["gmm_iter"],
                         reg_covar=cfg()["reg_covar"], random_state=seed)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        gm.fit(Z)
    return gm


def _pca_gmm(X, k, seed, d, bic, kmax):
    mu, V = pca_fit(X, d)
    Z = (X - mu) @ V.T
    if bic:
        best = None
        for kk in range(1, kmax + 1):
            if kk > len(X):
                break
            gm = gmm_fit(Z, kk, seed)
            b = gm.bic(Z)
            if best is None or b < best[0]:
                best = (b, gm)
        gm = best[1]
    else:
        gm = gmm_fit(Z, k, seed)
    return mu, V, gm, gm.predict(Z)


def cells_gmm(o, A, fitsets, k_of, seed, d, bic=False):
    """-> (centers, cell anchor, fit seconds, dropped empty components, models {anchor: (mu, V, gm)}, chosen k per anchor)."""
    Xt = o["Xt"]
    cents, ca, t_fit, dropped, models, kch, nconv = [], [], 0.0, 0, {}, {}, 0
    for a in range(len(A["anchors"])):
        idx = fitsets[a]
        if len(idx) == 0:
            refuse("anchor %s has an empty fit set" % A["label"][A["anchors"][a]])
        X, k = Xt[idx], int(k_of[a])
        if k == 1:
            cents.append(unit(X.sum(axis=0))[None, :])
            ca.append(a)
            kch[a] = 1
            continue
        if k > len(idx):
            refuse("anchor %s: k %d exceeds its %d fit items" % (A["label"][A["anchors"][a]], k, len(idx)))
        (mu, V, gm, lab), t = timed(_pca_gmm, X, k, seed, d, bic, 2 * k + 1)
        t_fit += t
        nconv += int(not gm.converged_)
        models[a] = (mu, V, gm)
        kch[a] = int(gm.n_components)
        for j in range(gm.n_components):
            m = lab == j
            if not m.any():
                dropped += 1
                continue
            cents.append(unit(X[m].sum(axis=0))[None, :])
            ca.append(a)
    return np.vstack(cents), np.array(ca), t_fit, dropped, models, kch, nconv


def name_and_file(o, A, C, ca):
    """Cells named by the TRAIN items the flatLeaf rule files into them; EVAL filed over ALL cells. -> (ok, names, n_empty, e_cell)."""
    t_cell = np.argmax(o["Xt"] @ C.T, axis=1)
    names = np.empty(len(C), dtype=int)
    n_empty = 0
    for j in range(len(C)):
        m = GB.majority(o["yt"][t_cell == j], o["classes"])
        if m < 0:
            n_empty += 1
            m = int(A["a_cls"][ca[j]])
        names[j] = m
    e_cell = np.argmax(o["Xe"] @ C.T, axis=1)
    ok = (names[e_cell] == o["ye"]).astype(np.int64)
    return ok, names, n_empty, e_cell


def ncc_on_ftree(o, A):
    """I4's independent loop: one cell per anchor at the normalised mean of F-tree(a), named and filed by the common rule."""
    C = np.vstack([unit(o["Xt"][A["ftree"][a]].sum(axis=0)) for a in range(len(A["anchors"]))])
    t_cell = np.argmax(o["Xt"] @ C.T, axis=1)
    names = []
    for j in range(len(C)):
        cnt = Counter(int(y) for y in o["yt"][t_cell == j])
        names.append(min((c for c in cnt if cnt[c] == max(cnt.values())), key=lambda c: o["classes"][c]) if cnt else int(A["a_cls"][j]))
    return (np.array(names)[np.argmax(o["Xe"] @ C.T, axis=1)] == o["ye"]).astype(np.int64)


def check_i4(o, A):
    C, ca, _t, _d = cells_kmeans(o, A, A["ftree"], np.ones(len(A["anchors"]), dtype=int), 0)
    ok = name_and_file(o, A, C, ca)[0]
    ref = ncc_on_ftree(o, A)
    if not np.array_equal(ok, ref):
        refuse("I4: B at k_a = 1 differs from NCC-on-F-tree on %d items" % int((ok != ref).sum()))
    return ok


def depth2_identity(o, ident):
    """G13-BREAKDOWN's depth-2 numbers, recomputed with its own functions; REFUSES on any miss."""
    c = cfg()["depth2"]
    fr, names = GB.frontier_names(o, 2)
    tree2 = np.array([int(names[fr[u]] == o["ye"][i]) for i, u in enumerate(o["eleaf"])], dtype=np.int64)
    kcd = GB.kc_at_depth(o, 2)
    if any(k != 1 for k in kcd.values()):
        refuse("depth 2: k_c(2) is not 1 for every class")
    for s in SEEDS:
        Pm, owner, _t = GB.kc_fit(o["Xt"], o["yt"], kcd, s)
        if not np.array_equal((G.file_nearest(o["Xe"], Pm, owner) == o["ye"]).astype(np.int64), ident["ncc_ok"]):
            refuse("depth 2: KC(2)_%d differs from NCC" % s)
    st = GB.stat(tree2 - ident["ncc_ok"], o["comp"])
    got = dict(n_f2=len(names), n_empty=sum(1 for v in names.values() if v < 0), p_tree2="%.4f" % tree2.mean(),
               d2="%+.4f" % st["d"], lo2="%+.4f" % st["lo"], hi2="%+.4f" % st["hi"])
    want = dict(c)
    for k in ("d2", "lo2", "hi2"):
        want[k] = "%+.4f" % float(want[k])
    bad = [k for k in want if got[k] != want[k]]
    if bad:
        refuse("depth 2 (G13-BREAKDOWN): %s reproduced as %s, recorded %s" % (bad, [got[k] for k in bad], [want[k] for k in bad]))
    return got


ARMS_DECIDING = ("B", "C")
ARMS_DESC = ("B-gt", "B-anc", "B-bis", "C-32", "C-64", "C-BIC")


def fit_arms(o, A):
    """Every seeded arm on TRAIN only -> {arm: {seed: dict(ok, t, empty, dropped, k_total, ...)}}."""
    c = cfg()
    out = {}
    specs = (("B", "km", A["ftree"], None), ("C", "gmm", A["ftree"], c["pca"]),
             ("B-gt", "km", A["gt"], None), ("B-anc", "km", A["banc"], None), ("B-bis", "bisect", A["ftree"], None),
             ("C-32", "gmm", A["ftree"], c["pca_sens"][0]), ("C-64", "gmm", A["ftree"], c["pca_sens"][1]),
             ("C-BIC", "bic", A["ftree"], c["pca"]))
    for arm, kind, fs, d in specs:
        out[arm] = {}
        for s in SEEDS:
            rec = {}
            if kind in ("km", "bisect"):
                C, ca, t, dr = cells_kmeans(o, A, fs, A["ka"], s, mode="bisect" if kind == "bisect" else "kmeans")
            else:
                C, ca, t, dr, models, kch, nconv = cells_gmm(o, A, fs, A["ka"], s, d, bic=(kind == "bic"))
                rec.update(models=models, kch=kch, nconv=nconv)
            ok, names, n_empty, e_cell = name_and_file(o, A, C, ca)
            rec.update(ok=ok, t=t, empty=n_empty, dropped=dr, k_total=len(C), C=C, ca=ca, e_cell=e_cell)
            out[arm][s] = rec
    return out


def entropy_readout(o, A, rec, X, cell_of, src, kbin_of):
    """R4: for items filed into a cell of a split anchor, that anchor's GMM responsibilities at the item's PCA projection."""
    rows = defaultdict(list)
    for i in range(len(X)):
        a = int(rec["ca"][cell_of[i]])
        if a not in rec["models"]:
            continue
        mu, V, gm = rec["models"][a]
        p = gm.predict_proba(((X[i] - mu) @ V.T)[None, :])[0]
        p = p[p > 0]
        h = float(-(p * np.log(p)).sum())
        k = gm.n_components
        rows["all"].append((h, h / np.log(k), float(p.max())))
        rows["src " + src[i]].append((h, h / np.log(k), float(p.max())))
        rows["k_a " + bin_name(kbin_of[a])].append((h, h / np.log(k), float(p.max())))
    res = {}
    for key, v in rows.items():
        arr = np.array(v)
        res[key] = dict(n=len(v), h_mean=float(arr[:, 0].mean()), h_med=float(np.median(arr[:, 0])), hn_mean=float(arr[:, 1].mean()),
                        hn_med=float(np.median(arr[:, 1])), share90=float(np.mean(arr[:, 2] > 0.9)))
    return res


def strata_masks(o, A):
    """R3: (i) true-anchor subtree depth, (ii) true-anchor k_a bin, (iii) A's flatLeaf leaf depth (G13-BREAKDOWN's strata)."""
    c = cfg()
    md_e, ka_e = A["maxd"][A["e_anchor"]], A["ka"][A["e_anchor"]]
    ldep = np.array([o["nodes"][u]["depth"] for u in o["eleaf"]])
    out = []
    for d in sorted(c["r3_depth"]):
        out.append(("(i) true-anchor subtree depth %d" % d, md_e == d))
    for b in c["ka_bins"]:
        out.append(("(ii) true-anchor k_a %s" % bin_name(b), (ka_e >= b[0]) & (ka_e <= b[1])))
    for lo, hi in c["leaf_strata"]:
        out.append(("(iii) A's flatLeaf leaf depth %s" % (str(lo) if lo == hi else ">= %d" % lo), (ldep >= lo) & (ldep <= hi)))
    return out


def contrasts(ok, m=None):
    """The registered paired contrasts on items m (default all): D_AB, D_AC, D_DB, D_DC (descriptive), D13."""
    sel = (lambda v: v) if m is None else (lambda v: v[m])
    A_, B0, C0, D0 = sel(ok["A"]), sel(ok["B"]), sel(ok["C"]), sel(ok["D"])
    return {"D_AB": A_ - B0, "D_AC": A_ - C0, "D_DB": D0 - B0, "D_DC": D0 - C0, "D13": A_ - D0}


def summarize(o, A, arms, ident):
    """Every statistic, spread and verdict from per-seed correctness vectors (no fitting here)."""
    c = cfg()
    comp = o["comp"]
    n = len(o["ye"])
    okA = o["fl"].astype(np.int64)
    okD = {s: ident["kc_ok"][s] for s in SEEDS}
    okB = {s: arms["B"][s]["ok"] for s in SEEDS}
    okC = {s: arms["C"][s]["ok"] for s in SEEDS}
    R = {"n": n, "G": len(set(comp.tolist()))}
    R["P"] = {"A": float(okA.mean()), "B": {s: float(okB[s].mean()) for s in SEEDS}, "C": {s: float(okC[s].mean()) for s in SEEDS},
              "D": {s: float(okD[s].mean()) for s in SEEDS}}
    R["spread_B"], R["spread_C"], R["spread_KC"] = spread(R["P"]["B"].values()), spread(R["P"]["C"].values()), spread(R["P"]["D"].values())
    ok0 = {"A": okA, "B": okB[0], "C": okC[0], "D": okD[0]}
    R["R1"] = {k: GB.stat(v, comp) for k, v in contrasts(ok0).items()}
    # R2 per source
    R["R2"] = {}
    for so in c["sources"]:
        m = o["esrc"] == so
        if not m.any():
            R["R2"][so] = None
            continue
        st = {k: GB.stat(v, comp[m]) for k, v in contrasts(ok0, m).items()}
        sp = {"B": spread(okB[s][m].mean() for s in SEEDS), "C": spread(okC[s][m].mean() for s in SEEDS),
              "KC": spread(okD[s][m].mean() for s in SEEDS)}
        share = {}
        for key in ("D_DB", "D13"):
            tot = n * R["R1"][key]["d"]
            share[key] = (st[key]["n"] * st[key]["d"]) / tot if tot != 0 else float("nan")
        R["R2"][so] = dict(st=st, spread=sp, share=share, n=int(m.sum()), P={k: float(v[m].mean()) for k, v in ok0.items()})
    # R3 strata
    R["R3"] = []
    for name, m in strata_masks(o, A):
        if not m.any():
            R["R3"].append((name, None))
            continue
        R["R3"].append((name, dict(n=int(m.sum()), G=len(set(comp[m].tolist())), P={k: float(v[m].mean()) for k, v in ok0.items()},
                                   st={k: GB.stat(v, comp[m]) for k, v in contrasts(ok0, m).items()})))
    tot_db = float((ok0["D"] - ok0["B"]).sum())
    ka_e = A["ka"][A["e_anchor"]]
    hi_ka = ka_e >= 4
    R["share_db_ka4"] = float((ok0["D"] - ok0["B"])[hi_ka].sum()) / tot_db if tot_db != 0 else float("nan")
    m1 = ka_e == 1
    R["ka1_range"] = spread(v[m1].mean() for v in ok0.values()) if m1.any() else float("nan")
    # criteria
    mm = o["esrc"] == c["scoreable"]
    R["M"] = {}
    for key, cmp_arm, okS in (("C-AB-M", "B", okB), ("C-AC-M", "C", okC), ("C-DB-M", "B", okB)):
        sp_m = spread(okS[s][mm].mean() for s in SEEDS)
        if key == "C-DB-M":
            sp_m = max(sp_m, spread(okD[s][mm].mean() for s in SEEDS))
        R["M"][key] = sp_m
    r2m = R["R2"].get(c["scoreable"])
    R["V"] = {
        "C-AB": v_spread(R["R1"]["D_AB"]["d"], R["R1"]["D_AB"]["lo"], R["R1"]["D_AB"]["hi"], R["spread_B"]),
        "C-AC": v_spread(R["R1"]["D_AC"]["d"], R["R1"]["D_AC"]["lo"], R["R1"]["D_AC"]["hi"], R["spread_C"]),
        "C-DB": v_spread(R["R1"]["D_DB"]["d"], R["R1"]["D_DB"]["lo"], R["R1"]["D_DB"]["hi"], max(R["spread_B"], R["spread_KC"])),
    }
    for key, k2 in (("C-AB-M", "D_AB"), ("C-AC-M", "D_AC"), ("C-DB-M", "D_DB")):
        st = r2m["st"][k2] if r2m else None
        R["V"][key] = v_interval(st["lo"], st["hi"]) if st else "UNDETERMINED"
    R["frule"] = f_rule(R["R1"]["D_AB"]["lo"], R["R1"]["D_AC"]["lo"], c["frule"])
    # descriptive arms
    R["desc"] = {}
    for arm in ARMS_DESC:
        P_s = {s: float(arms[arm][s]["ok"].mean()) for s in SEEDS}
        R["desc"][arm] = dict(P=P_s, spread=spread(P_s.values()), empty={s: arms[arm][s]["empty"] for s in SEEDS},
                              dropped={s: arms[arm][s]["dropped"] for s in SEEDS}, k_total={s: arms[arm][s]["k_total"] for s in SEEDS})
    d0 = {a: arms[a][0]["ok"] for a in ARMS_DESC}
    R["desc_diff"] = {"P(B-gt_0) - P(D_0)": GB.stat(d0["B-gt"] - okD[0], comp), "P(B-anc_0) - P(B_0)": GB.stat(d0["B-anc"] - okB[0], comp),
                      "P(B-bis_0) - P(B_0)": GB.stat(d0["B-bis"] - okB[0], comp), "P(C-BIC_0) - P(C_0)": GB.stat(d0["C-BIC"] - okC[0], comp),
                      "P(C-32_0) - P(C_0)": GB.stat(d0["C-32"] - okC[0], comp), "P(C_0) - P(C-64_0)": GB.stat(okC[0] - d0["C-64"], comp)}
    R["arm_meta"] = {a: {s: dict(empty=arms[a][s]["empty"], dropped=arms[a][s]["dropped"], k_total=arms[a][s]["k_total"],
                                 nconv=arms[a][s].get("nconv", 0)) for s in SEEDS} for a in arms}
    R["times"] = {a: [arms[a][s]["t"] for s in SEEDS] for a in arms}
    R["times"]["D"] = [ident["t_kc"][s] for s in SEEDS]
    return R


def compute(o, A, ident):
    arms = fit_arms(o, A)
    R = summarize(o, A, arms, ident)
    rec0 = arms["C"][0]
    kbin_of = {a: ka_bin(int(A["ka"][a])) for a in range(len(A["anchors"]))}
    t_cell = np.argmax(o["Xt"] @ rec0["C"].T, axis=1)
    R["R4"] = {"EVAL": entropy_readout(o, A, rec0, o["Xe"], rec0["e_cell"], o["esrc"], kbin_of),
               "TRAIN": entropy_readout(o, A, rec0, o["Xt"], t_cell, o["tsrc"], kbin_of)}
    R["C_BIC_k"] = {s: arms["C-BIC"][s]["k_total"] for s in SEEDS}
    return R


# ── rendering ───────────────────────────────────────────────────────────────────────────────────────────────────────────

def fs(st):
    return GB.fs(st)


def support_line(key, st, bar):
    se_r, mde_r, disc_r, deff_r = SUPPORT_REG[key]
    return ("  support %s: SE %.5f (registered %.5f); DEFF %.3f (transported %.3f); n_eff %.0f; MDE80 %.4f (registered %.4f); discordance"
            " %.4f (planning %.2f); effective bar max(MDE80, spread) %.4f" % (key, st["se"], se_r, st["deff"], deff_r, st["n_eff"], st["mde"],
                                                                            mde_r, st["disc"], disc_r, max(st["mde"], bar)))


def pred_line(label, obs):
    pt, band = PRED[label]
    if pt is None:
        head = "%s [%g, %g]" % (label, band[0], band[1])
    elif isinstance(pt, int):
        head = "%s %d [%d, %d]" % (label, pt, band[0], band[1])
    else:
        head = "%s %+.3f [%+.3f, %+.3f]" % (label, pt, band[0], band[1])
    if obs is None or obs != obs:
        return "PREDICTION %s: observed none -> NOT SCORED (no estimate)" % head
    return "PREDICTION %s: observed %+.4f -> %s" % (head, obs, G.in_band(obs, band))


_WHAT = {"C-AB": ("the vMF construction beats flat spherical k-means at matched cells within the same anchors",
                  "flat spherical k-means beats the vMF construction at matched cells within the same anchors", "D_AB", "spread_B"),
         "C-AC": ("the vMF construction beats PCA-GMM at matched cells within the same anchors",
                  "PCA-GMM beats the vMF construction at matched cells within the same anchors", "D_AC", "spread_C"),
         "C-DB": ("label information below depth 2 buys filing over a label-free split at matched cells",
                  "a label-free split at matched cells files better than label information below depth 2", "D_DB", "max(spread_B, spread_KC)")}


def verdict_lines(R):
    """Every registered criterion, the falsifier and the consequence sentences, with their values (render prints these verbatim)."""
    c = cfg()
    L = []
    bars = {"C-AB": R["spread_B"], "C-AC": R["spread_C"], "C-DB": max(R["spread_B"], R["spread_KC"])}
    for key in ("C-AB", "C-AC", "C-DB"):
        held, rev, stat_name, bar_name = _WHAT[key]
        st, v, bar = R["R1"][stat_name], R["V"][key], bars[key]
        vals = "%s %+.4f, interval [%+.4f, %+.4f], %s %.4f" % (stat_name, st["d"], st["lo"], st["hi"], bar_name, bar)
        if v == "HELD":
            L.append("%s: HELD (%s): %s; interval wholly above 0 and %s > %s" % (key, held, vals, stat_name, bar_name))
        elif v == "REVERSED":
            L.append("%s: REVERSED (%s): %s; interval wholly below 0 and %s < -%s" % (key, rev, vals, stat_name, bar_name))
        else:
            L.append("%s: UNDETERMINED: %s; neither clause holds (never read as parity: no TOST registered)" % (key, vals))
        L.append(support_line(key, st, bar))
    r2m = R["R2"].get(c["scoreable"])
    for key, stat_name in (("C-AB-M", "D_AB"), ("C-AC-M", "D_AC"), ("C-DB-M", "D_DB")):
        st = r2m["st"][stat_name] if r2m else None
        if st is None:
            L.append("%s: UNDETERMINED: no %s item (n = 0)" % (key, c["scoreable"]))
            continue
        sp = R["M"][key]
        frag = "; seed-fragile (|%s| %.4f < stratum spread %.4f)" % (stat_name, abs(st["d"]), sp) if abs(st["d"]) < sp else ""
        vals = "%s_M %+.4f, interval [%+.4f, %+.4f] (%s, the interval decides); stratum spread %.4f" % (
            stat_name, st["d"], st["lo"], st["hi"], c["scoreable"], sp)
        v = R["V"][key]
        if v == "HELD":
            L.append("%s: HELD: %s; interval wholly above 0%s" % (key, vals, frag))
        elif v == "REVERSED":
            L.append("%s: REVERSED: %s; interval wholly below 0%s" % (key, vals, frag))
        else:
            L.append("%s: UNDETERMINED: %s; the interval contains 0%s" % (key, vals, frag))
        L.append(support_line(key, st, sp))
    L.append("The six clauses are read separately; no family-wise correction (disclosed).")
    lab, lac = R["R1"]["D_AB"]["lo"], R["R1"]["D_AC"]["lo"]
    if R["frule"]:
        L.append("F-RULE: FIRES (H-RULE \"a better label-free split rule below the anchors closes the G13 gap\" falsified at this n):"
                 " lower ends D_AB %+.4f and D_AC %+.4f both above %+.4f (= -|D13| / 2)" % (lab, lac, c["frule"]))
    else:
        L.append("F-RULE: DOES NOT FIRE: lower ends D_AB %+.4f, D_AC %+.4f; both must lie above %+.4f (= -|D13| / 2)" % (lab, lac, c["frule"]))
    cons = 0
    if R["frule"] and R["V"]["C-DB"] == "HELD":
        cons += 1
        L.append("CONSEQUENCE (F-RULE fired and C-DB HELD): the gap is attributed to label information below depth 2; the split-criterion"
                 " follow-up (SPLIT-VMF) is not worth an engine change.")
    if R["V"]["C-AB"] == "REVERSED" or R["V"]["C-AC"] == "REVERSED":
        cons += 1
        L.append("CONSEQUENCE (C-AB or C-AC REVERSED: C-AB %s, C-AC %s): the split rule is implicated; SPLIT-VMF becomes the next"
                 " registration." % (R["V"]["C-AB"], R["V"]["C-AC"]))
    if cons == 0:
        L.append("CONSEQUENCE: neither registered branch applies (F-RULE %s, C-DB %s, C-AB %s, C-AC %s)."
                 % ("fired" if R["frule"] else "did not fire", R["V"]["C-DB"], R["V"]["C-AB"], R["V"]["C-AC"]))
    elif cons == 2:
        L.append("NOTE: both registered consequence branches apply on these data (printed as registered; the registrar reads them).")
    return L


def _seeds(d):
    return " / ".join("%.4f" % d[s] for s in SEEDS)


def _times(v):
    return "seconds %s; median %.3f, max %.3f" % (" / ".join("%.3f" % x for x in v), float(np.median(v)), max(v))


LABEL_INFO = (
    "LABEL INFORMATION PER ARM (lesson anchored-tree-comparisons):",
    " | arm | depth-2 cells | partition below depth 2 | cell naming | k |",
    " | A | B0's anchors, seeded from TRAIN ground truth | label-free vMF splits | TRAIN majority (leaves CSV) | its own |",
    " | B, C, B-bis, C-32, C-64 | inherited from A (F-tree) | label-free | TRAIN majority | k_a from A |",
    " | C-BIC | inherited from A (F-tree) | label-free | TRAIN majority | BIC over 1..2k_a+1 |",
    " | B-anc | inherited (anchor vmfMu) | label-free | TRAIN majority | k_a from A |",
    " | B-gt | TRAIN class labels | label-free | TRAIN majority | k_a from A |",
    " | D (KC) | TRAIN class labels | TRAIN class labels (one class per prototype) | owned class | k_c from A's leaf names |",
    " All arms inherit the anchors; none uses labels to PARTITION below depth 2 except D; every arm reads TRAIN labels to NAME its"
    " cells. F-tree inherits A's leaf geometry (holding the depth-2 frontier fixed), which favours A if anything.")


def render(R, o, A, ident, d2, i4_ok):
    c = cfg()
    L = ["%s DEEP-SPLIT-COMPARE (lane r2) readout; zero calls; TRAIN-only fits (check_sides passed); seeds %s; comparator of record"
         " s = 0" % (TAG, list(SEEDS))]
    L += list(LABEL_INFO)
    L.append("NOT APPLICABLE: wrong(established), tie conventions A / B, pilot / truncation guard, call cache (no judge verdict here).")
    L.append("== IDENTITY (all PASSED before any new number): I1 %s" % json.dumps(ident["i1_got"], sort_keys=True))
    L.append("  depth 2 (G13-BREAKDOWN): |F(2)| %d (%d <empty>), k_c(2) = 1, KC(2)_s = NCC on every seed; P_tree(2) %s; D(2) %s"
             " [%s, %s]" % (d2["n_f2"], d2["n_empty"], d2["p_tree2"], d2["d2"], d2["lo2"], d2["hi2"]))
    L.append("  I2: %d anchors = the %d classes; %d leaves; k_a per source %s; child counts %s; I3: F-tree covers %d TRAIN items;"
             " table matched" % (len(A["anchors"]), len(o["classes"]), len(o["leaves"]), dict(sorted(A["ksrc"].items())),
                                 dict(sorted(A["hist"].items())), sum(len(x) for x in A["ftree"])))
    L.append("  I4: B with k_a = 1 everywhere = NCC-on-F-tree item-wise; P %.4f" % i4_ok.mean())
    L.append("  I0 / I2 descent / I3 argmax / I4 structure / I5 support (g13_breakdown.load_objects): PASSED; I3 argmax misses %d of %d"
             % (o["i3_miss"], len(o["ye"])))
    L.append("== DENOMINATORS: EVAL %d items in %d CK-CLOSE components; TRAIN %d; split anchors %d holding %d leaves"
             % (R["n"], R["G"], len(o["yt"]), int((A["ka"] > 1).sum()), int(A["ka"][A["ka"] > 1].sum())))
    L.append("== R1 OVERALL")
    L.append("  P_A %.4f (B0 as built; one construction, no seeds)" % R["P"]["A"])
    L.append("  P(B_s) %s; spread_B %.4f" % (_seeds(R["P"]["B"]), R["spread_B"]))
    L.append("  P(C_s) %s; spread_C %.4f" % (_seeds(R["P"]["C"]), R["spread_C"]))
    L.append("  P(D_s) %s; spread_KC %.4f" % (_seeds(R["P"]["D"]), R["spread_KC"]))
    for k, lab in (("D_AB", "D_AB = P_A - P(B_0)"), ("D_AC", "D_AC = P_A - P(C_0)"), ("D_DB", "D_DB = P(D_0) - P(B_0)"),
                   ("D_DC", "D_DC = P(D_0) - P(C_0) (descriptive)"), ("D13", "D13 = P_A - P(D_0) (identity)")):
        L.append("  %-40s %s" % (lab, fs(R["R1"][k])))
    L.append("== R2 PER SOURCE (stratum intervals: the source's components re-indexed)")
    for so in c["sources"]:
        r = R["R2"][so]
        tag = "SCOREABLE" if so == c["scoreable"] else "DESCRIPTIVE-ONLY"
        if r is None:
            L.append("  %-12s %s: n = 0: no EVAL item, no estimate" % (so, tag))
            continue
        L.append("  %-12s %s: n %d; P_A %.4f, P(B_0) %.4f, P(C_0) %.4f, P(D_0) %.4f; seed spreads B %.4f, C %.4f, KC %.4f" % (
            so, tag, r["n"], r["P"]["A"], r["P"]["B"], r["P"]["C"], r["P"]["D"], r["spread"]["B"], r["spread"]["C"], r["spread"]["KC"]))
        for k in ("D_AB", "D_AC", "D_DB", "D_DC", "D13"):
            L.append("    %-5s %s" % (k, fs(r["st"][k])))
        L.append("    share of D_DB %.4f; share of D13 %.4f" % (r["share"]["D_DB"], r["share"]["D13"]))
    L.append("== R3 PER DEPTH (descriptive; (i), (ii) label-defined, (iii) output-defined)")
    for name, r in R["R3"]:
        if r is None:
            L.append("  %s: n = 0: no EVAL item, no estimate" % name)
            continue
        L.append("  %s: n %d, %d components; P_A %.4f, P(B_0) %.4f, P(C_0) %.4f, P(D_0) %.4f" % (
            name, r["n"], r["G"], r["P"]["A"], r["P"]["B"], r["P"]["C"], r["P"]["D"]))
        for k in ("D_AB", "D_AC", "D_DB", "D_DC", "D13"):
            L.append("    %-5s %s" % (k, fs(r["st"][k])))
    L.append("  share of D_DB in the k_a >= 4 strata %.4f; k_a = 1 stratum max - min of P_A, P(B_0), P(C_0), P(D_0) %.4f"
             % (R["share_db_ka4"], R["ka1_range"]))
    L.append("== R4 SOFT-ASSIGNMENT ENTROPY, C_0 (descriptive; items filed into a split anchor)")
    for side in ("EVAL", "TRAIN"):
        r4 = R["R4"][side]
        for key in sorted(r4, key=lambda k: (k != "all", k)):
            x = r4[key]
            L.append("  %-5s %-22s n %d; H mean %.4f, median %.4f nats; H / log k_a mean %.4f, median %.4f; share max resp > 0.9 %.4f" % (
                side, key, x["n"], x["h_mean"], x["h_med"], x["hn_mean"], x["hn_med"], x["share90"]))
        if not r4:
            L.append("  %-5s n = 0: no item filed into a split anchor" % side)
    L.append("== R5 FIT TIME (descriptive; perf_counter around the fits, vectors in memory, 1 thread; an order of magnitude only)")
    for a in ("B", "C", "D") + ARMS_DESC:
        L.append("  %-6s %s" % (a, _times(R["times"][a])))
    man = o["man"]
    mem = sum(man[m]["ms"] for m, _s in c["members"]) / 1000.0
    L.append("  A: members' manifests %.1f s + flatLeaf graft %.1f s (12 JVM threads, end-to-end; copied, not re-timed)"
             % (mem, man["graft_flatleaf"]["ms"] / 1000.0))
    ms = _MACHINE[0]()
    L.append("  machine state: free RAM %s GB; admitted PIDs %s; BLAS threads %s" % (
        "%.1f" % ms["free_ram_gb"] if ms.get("free_ram_gb") is not None else "unknown", ms.get("pids"), ms.get("blas")))
    L.append("== ARM BOOKKEEPING (cells with no TRAIN item take their anchor's class; GMM empty components dropped)")
    for a in ("B", "C") + ARMS_DESC:
        mt = R["arm_meta"][a]
        L.append("  %-6s cells %s; empty-named %s; dropped %s; GMM not converged %s" % (
            a, "/".join(str(mt[s]["k_total"]) for s in SEEDS), "/".join(str(mt[s]["empty"]) for s in SEEDS),
            "/".join(str(mt[s]["dropped"]) for s in SEEDS), "/".join(str(mt[s]["nconv"]) for s in SEEDS)))
    L.append("== DESCRIPTIVE ARMS (never deciding)")
    for a in ARMS_DESC:
        L.append("  P(%s_s) %s; spread %.4f" % (a, _seeds(R["desc"][a]["P"]), R["desc"][a]["spread"]))
    L.append("  C-BIC total k (seeds) %s against 133 at k_a" % " / ".join(str(R["C_BIC_k"][s]) for s in SEEDS))
    for k, st in R["desc_diff"].items():
        L.append("  %-24s %s" % (k, fs(st)))
    L.append("== VERDICTS")
    L += verdict_lines(R)
    L.append("== PREDICTIONS (priors; P_A 0.8119 and P(D_0) 0.8334 seen; a band is HELD iff the point lies in it, endpoints inclusive)")
    r2m = R["R2"].get(c["scoreable"])
    obs = {"P(B_0)": R["P"]["B"][0], "D_AB": R["R1"]["D_AB"]["d"], "spread_B": R["spread_B"], "P(C_0)": R["P"]["C"][0],
           "D_AC": R["R1"]["D_AC"]["d"], "spread_C": R["spread_C"], "D_DB": R["R1"]["D_DB"]["d"],
           "D_AB-M": r2m["st"]["D_AB"]["d"] if r2m else None, "D_AC-M": r2m["st"]["D_AC"]["d"] if r2m else None,
           "D_DB-M": r2m["st"]["D_DB"]["d"] if r2m else None, "C-BIC total k": float(R["C_BIC_k"][0]),
           "R3 share of D_DB in the k_a >= 4 strata": R["share_db_ka4"],
           "R3 k_a = 1 stratum: max - min of P_A, P(B_0), P(C_0), P(D_0)": R["ka1_range"],
           "R4 mean H / log k_a (EVAL)": R["R4"]["EVAL"].get("all", {}).get("hn_mean"),
           "R4 share with max responsibility > 0.9 (EVAL)": R["R4"]["EVAL"].get("all", {}).get("share90"),
           "R5 B fit per seed, median (s)": float(np.median(R["times"]["B"])), "R5 C fit per seed, median (s)": float(np.median(R["times"]["C"]))}
    for k, st in R["desc_diff"].items():
        obs[k] = st["d"]
    for k in PRED:
        L.append(pred_line(k, obs.get(k)))
    for key, txt in PROB:
        word = ("FIRES" if R["frule"] else "DOES NOT FIRE") if key == "F-RULE" else R["V"][key]
        L.append("PREDICTION %s verdict probabilities (%s): observed %s" % (key, txt, word))
    return "\n".join(L) + "\n"


def pins_lines(o):
    o_ = ["%s script %s blob:%s (LF); pinned modules: %s; rp12_lane / flat_mix_mmlu checked by g13_breakdown / g13_comparator" % (
        TAG, os.path.basename(__file__), blob_lf(os.path.abspath(__file__)), ", ".join("%s blob:%s" % (n, p[:8]) for n, p in PINS))]
    o_.append("%s bundle npz sha256 %s; json sha256-lf %s" % (TAG, o["paths"]["bundle_npz_sha256"], o["paths"]["bundle_json_sha256_lf"]))
    for k in sorted(o["paths"]):
        if k.startswith(("flatleaf", "descent")) or k == "pointer_sha256_lf":
            o_.append("%s %s sha256-lf %s" % (TAG, k, o["paths"][k]))
    return o_


def guard_paths(lane, root, out):
    if lane != "r2":
        refuse("DEEP-SPLIT-COMPARE reads lane r2 objects only (--lane r2), not lane %s" % lane)
    c = cfg()
    LN.guard(lane, [("--bundle", GB.P(root, c["bundle"])), ("flatLeaf validation", GB.P(root, c["fl_val"])),
                    ("descent validation", GB.P(root, c["de_val"])), ("--out", out)], root=root)


@contextlib.contextmanager
def _gb_hooks():
    """g13_breakdown's readers read its own hooks: they are pointed at this script's for the call and restored after."""
    saved = (GB._CFG[0], GB._ROOT[0], GB._SIDES[0], GB._CLOCK[0])
    GB._CFG[0], GB._ROOT[0], GB._SIDES[0], GB._CLOCK[0] = cfg(), _ROOT[0], _SIDES[0], _CLOCK[0]
    try:
        yield
    finally:
        GB._CFG[0], GB._ROOT[0], GB._SIDES[0], GB._CLOCK[0] = saved


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--run"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--out", default=None)
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        print("pool %s (selftest: synthetic fixtures only; the pool is not read)" % REG["pool"])
        print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
        print("[SCRIPT] %s blob:%s (LF)" % (os.path.basename(__file__), blob_lf(os.path.abspath(__file__))))
        try:
            selftest()
        except AssertionError:
            return 1
        return 0
    if a.mutants:
        return run_mutants()
    root = _ROOT[0]
    outp = a.out or GB.P(root, cfg()["out"])
    guard_paths(a.lane, root, outp)
    with _gb_hooks():
        rc, txt = _POOL_GUARD[0](cfg()["pool"])
        first = "POOL %s (B0-2 pool check rc %d): %s" % (cfg()["pool"], rc, txt.replace("\n", " | "))
        out(first)
        if rc != 0:
            refuse("the B0-2 pool check of %s failed: %s" % (cfg()["pool"], txt))
        if a.run and os.path.exists(outp):
            refuse("%s exists; the outcome is write-once" % outp)
        out("%s cost: 0 calls, 0 builds; CPU estimate 10-30 min single thread (8 seeded arms x 5 seeds; ~140 bootstraps of B %d)"
            % (TAG, G.BOOT_B))
        o = GB.load_objects(root)
        A = load_anchors(o)
        check_r3_support(o, A)
        ident = GB.check_i1(GB.identity_arms(o))
        d2 = depth2_identity(o, ident)
        i4_ok = check_i4(o, A)
        if a.dry_run:
            for ln in pins_lines(o):
                out(ln)
            c = cfg()
            out("%s DENOMINATORS: EVAL %d / %d components; TRAIN %d; per source %s" % (
                TAG, len(o["ye"]), len(set(o["comp"].tolist())), len(o["yt"]),
                ", ".join("%s %d/%d/%d" % ((s,) + c["support_eval"][s] + (c["support_train"][s],)) for s in c["sources"])))
            out("%s R3 strata denominators = Support (a): k_a %s; depth %s" % (
                TAG, {bin_name(b): v for b, v in c["r3_ka"].items()}, c["r3_depth"]))
            out("%s I0-I5 (g13_breakdown) PASSED; I1 PASSED (SEEN): %s" % (TAG, json.dumps(ident["i1_got"], sort_keys=True)))
            out("%s depth 2 PASSED (SEEN): %s" % (TAG, json.dumps(d2, sort_keys=True)))
            out("%s I2 PASSED: %d anchors, %d leaves, k_a per source %s, child counts %s; I3 PASSED: F-tree / B-anc / class counts ="
                " the table; I4 PASSED (item-wise; its point is printed by --run)" % (
                    TAG, len(A["anchors"]), len(o["leaves"]), dict(sorted(A["ksrc"].items())), dict(sorted(A["hist"].items()))))
            out("%s dry-run: NO new statistic computed or printed" % TAG)
            return 0
        R = compute(o, A, ident)
        body = "\n".join(pins_lines(o)) + "\n" + render(R, o, A, ident, d2, i4_ok)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    with open(outp, "x", encoding="utf-8", newline="\n") as f:
        f.write(first + "\n" + body)
    out(body.rstrip("\n"))
    out("%s wrote %s (write-once)" % (TAG, outp))
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _u(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def _dsc_spec(variant="H", dim=12):
    """Hand-built geometry (g13_breakdown fixture format); every expected value is derived in the module docstring / the tests."""
    e = np.eye(dim)
    if variant == "P":
        l4, l5, lu = e[0], e[1], e[3]
    else:
        l4, l5, lu = _u(e[0] + e[1]), e[6], (_u(e[3] + 0.5 * e[9]) if variant == "H" else e[3])
    mm = [("n00000001", 0, None, False, _u(e[0] + e[1] + e[2] + e[6]), "MMLU_PRO_LB"),
          ("n00000002", 1, "n00000001", False, _u(e[0] + e[1] + e[6]), "MMLU_PRO_LB/x"),
          ("n00000003", 1, "n00000001", True, _u(e[2] + 0.3 * e[8]), "MMLU_PRO_LB/y"),
          ("n00000004", 2, "n00000002", True, l4, "Emergent #1"),
          ("n00000005", 2, "n00000002", True, l5, "Emergent #2")]
    bbh = [("n00000001", 0, None, False, _u(e[3] + e[4]), "BBH"),
           ("n00000002", 1, "n00000001", True, lu, "BBH/u"),
           ("n00000003", 1, "n00000001", True, e[4], "BBH/v")]
    train = [("MMLU_PRO_LB/x", e[0], 20), ("MMLU_PRO_LB/y", e[1], 12), ("MMLU_PRO_LB/y", e[2], 20), ("MMLU_PRO_LB/x", e[8], 6)]
    evals = [("MMLU_PRO_LB/x", e[0], 20), ("MMLU_PRO_LB/y", e[1], 20), ("MMLU_PRO_LB/y", e[2], 20), ("MMLU_PRO_LB/x", e[8], 30)]
    if variant == "S":                # three clusters under x with strict pairwise preferences: a = e0, b, c (cos ab 0.24, bc 0.10, ac 0)
        b, c = _u(e[1] + 0.25 * e[0]), _u(e[6] + 0.1 * e[1])
        train = [train[0], ("MMLU_PRO_LB/y", b, 12)] + train[2:] + [("MMLU_PRO_LB/x", c, 8)]
        evals = [evals[0], ("MMLU_PRO_LB/y", b, 20)] + evals[2:] + [("MMLU_PRO_LB/x", c, 10)]
    train += [("BBH/u", e[3], 20), ("BBH/v", e[4], 20)]
    evals += [("BBH/u", e[3], 20), ("BBH/v", e[4], 20)]
    if variant == "H":
        evals.append(("BBH/v", _u(e[4] + 3.0 * e[9]), 10))
    return dict(members={"mmlu_pro_lb": ("MMLU_PRO_LB", mm), "bbh": ("BBH", bbh)}, train=train, evals=evals, descent_wrong={},
                noise=0.02, dim=dim)


# hand-derived: EVAL groups each arm files WRONG (group index = position in evals), per variant
_WRONG = {"H": {"A": [1, 3, 6], "B": [3], "D": [], "tree2": [1, 3, 6]},
          "P": {"A": [3], "B": [3], "D": [], "tree2": [1, 3]},
          "S": {"A": [1, 3], "D": [], "tree2": [1, 3]}}
_TABLES = {"H": {"MMLU_PRO_LB/x": (2, 3, 32, 32, 26), "MMLU_PRO_LB/y": (1, 2, 26, 26, 32), "BBH/u": (1, 2, 20, 20, 20),
                 "BBH/v": (1, 2, 20, 20, 20)}}
_TABLES["P"] = dict(_TABLES["H"])
_TABLES["S"] = dict(_TABLES["H"], **{"MMLU_PRO_LB/x": (2, 3, 40, 40, 34)})


def _ok_from(g, wrong):
    return (~np.isin(g, wrong)).astype(np.int64)


def _patch(variant):
    """The fixture's registered constants: I1 / depth 2 from the hand-known filings (U-global from g13_breakdown's oracle)."""
    def p(fc, tr):
        g = tr["egrp"]
        kc = _ok_from(g, _WRONG[variant]["D"])
        diff = tr["fl"] - kc
        lo, hi, _ = G.boot(diff, G.comp_groups(tr["ecomp"]))
        ukm = []
        Xt, Xe = FM.unit_rows(tr["Xt"]), FM.unit_rows(tr["Xe"])
        L = len([u for u in tr["leaves"] if tr["dom"][u]])
        for s in SEEDS:
            C_, lab = GB._oracle_u(Xt, tr["yt"], Xe, tr["ye"], L, s, tr["classes"])
            ukm.append("%.4f" % (lab[np.argmax(Xe @ C_.T, axis=1)] == tr["ye"]).mean())
        fc["i1"] = dict(p_fl="%.4f" % tr["fl"].mean(), p_kc=tuple(["%.4f" % kc.mean()] * 5), d13="%+.4f" % diff.mean(),
                        lo="%+.4f" % lo, hi="%+.4f" % hi, ukm=tuple(ukm), ncc="%.4f" % kc.mean())
        fc["i2"] = "%.4f" % tr["fl"].mean()
        t2 = _ok_from(g, _WRONG[variant]["tree2"])
        lo2, hi2, _ = G.boot(t2 - kc, G.comp_groups(tr["ecomp"]))
        fc["depth2"] = dict(n_f2=4, n_empty=0, p_tree2="%.4f" % t2.mean(), d2="%+.4f" % (t2 - kc).mean(), lo2="%+.4f" % lo2, hi2="%+.4f" % hi2)
        fc.update(anchors=_TABLES[variant], n_anchors=4, children={2: 1}, pca=2, pca_sens=(3, 4),
                  leaf_strata=((2, 2), (3, 99)), out=RES + "/deep_split_compare_outcome.txt")
        x_ev = int(np.isin(g, [0, 3, 4] if variant == "S" else [0, 3]).sum())
        comps = lambda m: len(set(tr["ecomp"][m].tolist()))    # noqa: E731
        mx = np.array([tr["classes"][y] == "MMLU_PRO_LB/x" for y in tr["ye"]])
        fc["r3_ka"] = {(1, 1): (int((~mx).sum()), comps(~mx)), (2, 3): (x_ev, comps(mx)), (4, 7): (0, 0), (8, 99): (0, 0)}
        fc["r3_depth"] = {2: int((~mx).sum()), 3: x_ev}
        if variant == "H":            # a registered source with no item: the zero-site path of R2
            fc.update(sources=tuple(fc["sources"]) + ("MATH",), support_eval=dict(fc["support_eval"], MATH=(0, 0)),
                      support_train=dict(fc["support_train"], MATH=0))
    return p


def _run(tmp, variant="H", argv=None, expect_refusal=None, patch_extra=None, sides_patch=None, pool=None):
    """Writes fixture `variant` with g13_breakdown's writer (this script's geometry) and executes main(), the real entry point."""
    saved_spec = GB._fixture_spec
    GB._fixture_spec = lambda v, dim=12: _dsc_spec(variant, dim)
    try:
        fc, sides, tr = GB._fixture_write(tmp, variant)
    finally:
        GB._fixture_spec = saved_spec
    fcd = dict(REG)
    fcd.update({k: v for k, v in fc.items() if k not in REG or k in ("pool", "expect", "members", "sources", "support_eval",
                                                                      "support_train", "leaves_by_source", "n_eval", "n_comp",
                                                                      "n_train", "n_leaves", "depths", "leaf_strata")})
    _patch(variant)(fcd, tr)
    if patch_extra:
        patch_extra(fcd, tr)
    if sides_patch:
        sides_patch(sides, tr)
    saved = (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0], _MACHINE[0], _CLOCK[0])
    _CFG[0], _ROOT[0], _SIDES[0] = fcd, tmp, (lambda: sides)
    _POOL_GUARD[0] = pool if pool is not None else (lambda pool: (0, "[B0-2 stub] %s OK" % pool))
    _MACHINE[0] = lambda: {"free_ram_gb": 32.0, "pids": ["python.exe:4242"], "blas": "1"}
    _CLOCK[0] = GB._counting_clock()
    buf = []
    try:
        res = main(argv or ["--run", "--lane", "r2"], out=buf.append)
    except SystemExit as e:
        res = str(e)
        if expect_refusal is None:
            raise
    finally:
        (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0], _MACHINE[0], _CLOCK[0]) = saved
    if expect_refusal is not None:
        assert isinstance(res, str) and expect_refusal in res, (expect_refusal, res)
    return res, "\n".join(buf), fcd, tr


def _need(text, *needles):
    for nd in needles:
        assert nd in text, "missing: %r" % nd


def _st(tr, diff):
    diff = np.asarray(diff, dtype=np.float64)
    lo, hi, _ = G.boot(diff, G.comp_groups(tr["ecomp"]))
    return "%+.4f  95%% [%+.4f, %+.4f]" % (float(diff.mean()), lo, hi)


def st_e2e_H(tmp):
    """--run on fixture H: every deciding value by hand; R2 / R3 / descriptive arms; write-once."""
    res, text, fc, tr = _run(tmp, "H")
    assert res == 0, res
    outp = GB.P(tmp, fc["out"])
    filed = open(outp, encoding="utf-8").read()
    assert filed.splitlines()[0] == "POOL pv2_fixture (B0-2 pool check rc 0): [B0-2 stub] pv2_fixture OK", filed.splitlines()[0]
    g = tr["egrp"]
    okA, okB, okD = _ok_from(g, [1, 3, 6]), _ok_from(g, [3]), _ok_from(g, [])
    assert np.array_equal(okA, tr["fl"]), "fixture H: A's hand filing disagrees with the writer's"
    mm = tr["esrc"] == "MMLU_PRO_LB"
    _need(filed,
          "== DENOMINATORS: EVAL 140 items in 70 CK-CLOSE components; TRAIN 98; split anchors 1 holding 2 leaves",
          "  P_A 0.5714 (B0 as built",
          "  P(B_s) 0.7857 / 0.7857 / 0.7857 / 0.7857 / 0.7857; spread_B 0.0000",
          "  P(C_s) 0.7857 / 0.7857 / 0.7857 / 0.7857 / 0.7857; spread_C 0.0000",
          "  P(D_s) 1.0000 / 1.0000 / 1.0000 / 1.0000 / 1.0000; spread_KC 0.0000",
          "  %-40s %s" % ("D_AB = P_A - P(B_0)", _st(tr, okA - okB)),
          "  %-40s %s" % ("D_AC = P_A - P(C_0)", _st(tr, okA - okB)),
          "  %-40s %s" % ("D_DB = P(D_0) - P(B_0)", _st(tr, okD - okB)),
          "  %-40s %s" % ("D13 = P_A - P(D_0) (identity)", _st(tr, okA - okD)),
          "  I4: B with k_a = 1 everywhere = NCC-on-F-tree item-wise; P 0.6429",   # wrong y@e1, x@e8 (the x cell is unit(20e0+12e1), named x)
          "  MMLU_PRO_LB  SCOREABLE: n 90; P_A 0.4444, P(B_0) 0.6667, P(C_0) 0.6667, P(D_0) 1.0000",
          "    D_AB  -0.2222  95% [", "(n 90, 45 components;",
          "    D_DB  +0.3333  95% [",
          "    share of D_DB 1.0000; share of D13 0.8333",
          "  BBH          DESCRIPTIVE-ONLY: n 50; P_A 0.8000, P(B_0) 1.0000, P(C_0) 1.0000, P(D_0) 1.0000",
          "    D_AB  -0.2000  95% [",
          "    share of D_DB 0.0000; share of D13 0.1667",
          "  MATH         DESCRIPTIVE-ONLY: n = 0: no EVAL item, no estimate",
          "  (ii) true-anchor k_a 1: n 90, 45 components; P_A 0.6667, P(B_0) 1.0000, P(C_0) 1.0000, P(D_0) 1.0000",
          "  (ii) true-anchor k_a 2-3: n 50, 25 components; P_A 0.4000, P(B_0) 0.4000, P(C_0) 0.4000, P(D_0) 1.0000",
          "    D_DB  +0.6000  95% [",
          "  (ii) true-anchor k_a 4-7: n = 0: no EVAL item, no estimate",
          "  (ii) true-anchor k_a >= 8: n = 0: no EVAL item, no estimate",
          "  (i) true-anchor subtree depth 2: n 90, 45 components;", "  (i) true-anchor subtree depth 3: n 50, 25 components;",
          "  (iii) A's flatLeaf leaf depth 2: n 100, 50 components;", "  (iii) A's flatLeaf leaf depth >= 3: n 40, 20 components;",
          "  share of D_DB in the k_a >= 4 strata 0.0000; k_a = 1 stratum max - min of P_A, P(B_0), P(C_0), P(D_0) 0.3333",
          "  %-5s %-22s n 40;" % ("EVAL", "all"), "share max resp > 0.9 1.0000",
          "  %-5s %-22s n 32;" % ("TRAIN", "all"),
          "  B      seconds 1.000 / 1.000 / 1.000 / 1.000 / 1.000; median 1.000, max 1.000",
          "  A: members' manifests 10.0 s + flatLeaf graft 5.0 s",
          "  P(B-gt_s) 1.0000 / 1.0000 / 1.0000 / 1.0000 / 1.0000; spread 0.0000",
          "  P(B-anc_s) 0.7857 /", "  P(B-bis_s) 0.7857 /", "  P(C-32_s) 0.7857 /", "  P(C-64_s) 0.7857 /",
          "  C-BIC total k (seeds) 5 / 5 / 5 / 5 / 5 against 133 at k_a",
          "C-AB: REVERSED (flat spherical k-means beats the vMF construction at matched cells within the same anchors): D_AB -0.2143",
          "C-AC: REVERSED (PCA-GMM beats the vMF construction", "C-DB: HELD (label information below depth 2 buys filing",
          "D_DB +0.2143", "max(spread_B, spread_KC) 0.0000",
          "C-AB-M: REVERSED: D_AB_M -0.2222", "C-DB-M: HELD: D_DB_M +0.3333",
          "F-RULE: DOES NOT FIRE: lower ends D_AB",
          "CONSEQUENCE (C-AB or C-AC REVERSED: C-AB REVERSED, C-AC REVERSED): the split rule is implicated; SPLIT-VMF becomes the next registration.",
          "The six clauses are read separately; no family-wise correction (disclosed).",
          "  support C-AB: SE ", "  support C-DB-M: SE ",
          "PREDICTION P(B_0) +0.815 [+0.800, +0.830]: observed +0.7857 -> FAILED",
          "PREDICTION D_DB +0.018 [+0.005, +0.032]: observed +0.2143 -> FAILED",
          "PREDICTION spread_B +0.008 [+0.004, +0.016]: observed +0.0000 -> FAILED",
          "PREDICTION P(C-BIC_0) - P(C_0) +0.000 [-0.015, +0.015]: observed +0.0000 -> HELD",
          "PREDICTION C-BIC total k 133 [90, 260]: observed +5.0000 -> FAILED",
          "PREDICTION P(B-gt_0) - P(D_0) -0.003 [-0.010, +0.004]: observed +0.0000 -> HELD",
          "PREDICTION R3 share of D_DB in the k_a >= 4 strata +0.800 [+0.500, +1.100]: observed +0.0000 -> FAILED",
          "PREDICTION R4 share with max responsibility > 0.9 (EVAL) +0.800 [+0.550, +0.950]: observed +1.0000 -> FAILED",
          "PREDICTION R5 B fit per seed, median (s) [0.05, 1]: observed +1.0000 -> HELD",
          "PREDICTION C-AB verdict probabilities (HELD 0.10, REVERSED 0.25, UNDETERMINED 0.65): observed REVERSED",
          "PREDICTION F-RULE verdict probabilities (fires 0.45): observed DOES NOT FIRE")
    st_m = GB.stat((okA - okB)[mm], tr["ecomp"][mm])
    _need(filed, "C-AB-M: REVERSED: D_AB_M -0.2222, interval [%+.4f, %+.4f]" % (st_m["lo"], st_m["hi"]))
    assert "seed-fragile" not in filed
    assert "C-AB-M: REVERSED" in filed and "stratum spread 0.0000" in filed
    # write-once: a second --run refuses and leaves the file as it was
    _run(tmp, "H", expect_refusal="exists; the outcome is write-once")
    assert open(outp, encoding="utf-8").read() == filed
    return text


def st_e2e_P(tmp):
    """--run on fixture P: A = B item-wise; F-RULE FIRES; the label-information consequence."""
    res, text, fc, tr = _run(tmp, "P")
    assert res == 0, res
    filed = open(GB.P(tmp, fc["out"]), encoding="utf-8").read()
    _need(filed, "  P_A 0.7692 (B0", "  P(B_s) 0.7692 / 0.7692 / 0.7692 / 0.7692 / 0.7692; spread_B 0.0000",
          "  %-40s %s" % ("D_AB = P_A - P(B_0)", "+0.0000  95% [+0.0000, +0.0000]"),
          "C-AB: UNDETERMINED: D_AB +0.0000, interval [+0.0000, +0.0000]",
          "C-DB: HELD", "D_DB +0.2308",
          "F-RULE: FIRES (H-RULE \"a better label-free split rule below the anchors closes the G13 gap\" falsified at this n): lower ends"
          " D_AB +0.0000 and D_AC +0.0000 both above -0.0108",
          "CONSEQUENCE (F-RULE fired and C-DB HELD): the gap is attributed to label information below depth 2; the split-criterion"
          " follow-up (SPLIT-VMF) is not worth an engine change.",
          "C-AB-M: UNDETERMINED: D_AB_M +0.0000", "PREDICTION F-RULE verdict probabilities (fires 0.45): observed FIRES")
    assert "the split rule is implicated" not in filed
    return text


def st_e2e_S(tmp):
    """--run on fixture S: per-seed B partitions (oracle-identified, P by hand), spread_B; D constant."""
    res, text, fc, tr = _run(tmp, "S")
    assert res == 0, res
    filed = open(GB.P(tmp, fc["out"]), encoding="utf-8").read()
    Xt = FM.unit_rows(tr["Xt"])
    LM = np.vstack([_dsc_spec("S")["members"]["mmlu_pro_lb"][1][k][4] for k in (2, 3, 4)])  # y leaf, n4, n5
    leafk = np.argmax(Xt @ LM.T, axis=1)
    src_m = tr["tsrc"] == "MMLU_PRO_LB"
    idx = np.flatnonzero(src_m & np.isin(leafk, [1, 2]))
    hand = {32: 90 / 140, 28: 110 / 140, 20: 100 / 140}        # merged-cluster size -> P by hand: (i) e0+e1, (ii) e0+e6, (iii) e1+e6
    ps = []
    for s in SEEDS:
        r = FM.spherical_kmeans(Xt[idx], 2, s, max_iter=G.MAX_ITER)
        big = int(max(np.bincount(r["labels"], minlength=2)))
        assert big in hand, "fixture S: seed %d merged %d items, not a whole-cluster merge" % (s, big)
        ps.append(hand[big])
    assert max(ps) - min(ps) > 0, "fixture S must spread the B seeds"
    _need(filed, "  P(B_s) %s; spread_B %.4f" % (" / ".join("%.4f" % p for p in ps), max(ps) - min(ps)),
          "  P(D_s) 1.0000 / 1.0000 / 1.0000 / 1.0000 / 1.0000; spread_KC 0.0000", "  P_A 0.6429 (B0")
    line = [ln for ln in filed.splitlines() if ln.startswith("  P(C_s) ")][0]
    pc = [float(x) for x in line.split(";")[0][len("  P(C_s) "):].split(" / ")]
    assert len(pc) == 5 and all(round(p, 4) in {round(v, 4) for v in hand.values()} for p in pc), line
    assert line.endswith("spread_C %.4f" % (max(pc) - min(pc))), line
    return text


def st_dry_run(tmp):
    res, text, fc, tr = _run(tmp, "H", argv=["--dry-run", "--lane", "r2"])
    assert res == 0, res
    lines = text.splitlines()
    assert lines[0].startswith("POOL pv2_fixture (B0-2 pool check rc 0)"), lines[0]
    _need(text, "I1 PASSED (SEEN)", "depth 2 PASSED (SEEN)", "I2 PASSED: 4 anchors, 5 leaves", "I3 PASSED", "I4 PASSED",
          "R3 strata denominators = Support (a)", "dry-run: NO new statistic computed or printed", "cost: 0 calls")
    for bad in ("P(B_s)", "D_AB", "C-AB:", "F-RULE", "PREDICTION", "I4: B with k_a = 1 everywhere = NCC-on-F-tree item-wise; P"):
        assert bad not in text, bad
    assert not os.path.exists(GB.P(tmp, fc["out"]))
    return text


def st_refusals(factory):
    """Every refusal on the --run path, by its message; no outcome written."""
    cases = [
        (dict(argv=["--run", "--lane", "r1"]), "reads lane r2 objects only"),
        (dict(patch_extra=lambda fc, tr: fc.update(i1=dict(fc["i1"], p_fl="0.1234"))), "I1:"),
        (dict(patch_extra=lambda fc, tr: fc.update(depth2=dict(fc["depth2"], p_tree2="0.1234"))), "depth 2 (G13-BREAKDOWN)"),
        (dict(patch_extra=lambda fc, tr: fc.update(depth2=dict(fc["depth2"], hi2="+0.9999"))), "depth 2 (G13-BREAKDOWN)"),
        (dict(patch_extra=lambda fc, tr: fc.update(children={2: 2})), "I2: internal nodes"),
        (dict(patch_extra=lambda fc, tr: fc.update(n_anchors=5)), "I2: 4 depth-2 anchors"),
        (dict(patch_extra=lambda fc, tr: fc.update(anchors=dict(fc["anchors"], **{"MMLU_PRO_LB/x": (2, 3, 31, 32, 26)}))), "I2/I3: 1 anchor"),
        (dict(patch_extra=lambda fc, tr: fc.update(anchors=dict(fc["anchors"], **{"BBH/u": (1, 2, 20, 19, 20)}))), "I2/I3: 1 anchor"),
        (dict(patch_extra=lambda fc, tr: fc.update(anchors=dict(fc["anchors"], **{"MMLU_PRO_LB/y": (2, 2, 26, 26, 32)}))), "I2/I3: 1 anchor"),
        (dict(patch_extra=lambda fc, tr: fc.update(r3_ka={**fc["r3_ka"], (1, 1): (89, 45)})), "R3: true-anchor k_a stratum 1"),
        (dict(patch_extra=lambda fc, tr: fc.update(r3_depth={**fc["r3_depth"], 3: 49})), "R3: true-anchor subtree depth 3"),
        (dict(sides_patch=lambda sides, tr: sides.update({sorted(k for k, v in sides.items() if v == "TRAIN")[0]: "EVAL"})), "not TRAIN"),
    ]
    for kw, needle in cases:
        tmp = factory()
        res, text, fc, tr = _run(tmp, "H", expect_refusal=needle, **kw)
        assert not os.path.exists(GB.P(tmp, fc["out"])), needle
    # I4: B at k_a = 1 differing from the independent NCC-on-F-tree loop refuses
    g = globals()
    saved_ncc = g["ncc_on_ftree"]
    g["ncc_on_ftree"] = lambda o, A: 1 - saved_ncc(o, A)
    try:
        tmp = factory()
        _run(tmp, "H", expect_refusal="I4: B at k_a = 1 differs")
    finally:
        g["ncc_on_ftree"] = saved_ncc
    # the pool check: its line printed FIRST, then the refusal
    tmp = factory()
    buf = []
    saved = (_CFG[0], _ROOT[0], _POOL_GUARD[0])
    _CFG[0], _ROOT[0] = dict(REG), tmp
    _POOL_GUARD[0] = lambda pool: (1, "stub failure")
    try:
        try:
            main(["--run", "--lane", "r2"], out=buf.append)
            raise AssertionError("pool failure not refused")
        except SystemExit as e:
            assert "the B0-2 pool check" in str(e), str(e)
    finally:
        _CFG[0], _ROOT[0], _POOL_GUARD[0] = saved
    assert buf and buf[0].startswith("POOL pv2_1575de61bb20e977 (B0-2 pool check rc 1): stub failure"), buf
    return True


def st_pool(factory):
    """The REAL B0-2 pool check (GB.pool_check_v2, not a stub) executed through main() under this script's hooks, on fixture
    side files and a fixture engine pool file; only v2_union_pool.py's child process is replaced (its argv is asserted), so no pool
    or production DB is read. Each failure refuses with its own message, the POOL line printed FIRST; the pass prints the child's
    "expected <pool>" and "every check passed" lines and the "(pinned)" sha, then the dry-run continues to its identities."""
    import types
    calls = []

    def child(rc, lines):
        def fake(argv, **kw):
            calls.append(list(argv))
            return types.SimpleNamespace(returncode=rc, stdout="\n".join(lines) + "\n", stderr="child stderr" if rc else "")
        return types.SimpleNamespace(run=fake)

    good = ["[UNION-POOL] pool pv2_fixture recomputed from 3 DBs; expected pv2_fixture", "[UNION-POOL] every check passed (fixture)"]
    body = b'{"pool": "pv2_fixture"}\n'

    def setup(tmp, wal=0, pin="file"):
        db = os.path.join(tmp, "side_fixture.db")
        open(db, "wb").close()
        if wal:
            with open(db + "-wal", "wb") as f:
                f.write(b"x" * wal)
        with open(os.path.join(tmp, "engine_pool_fixture.json"), "wb") as f:
            f.write(body)
        sha = hashlib.sha256(body).hexdigest()

        def patch(fc, tr):
            fc.update(guard_dbs=(db,), pool_file="engine_pool_fixture.json",
                      pool_file_sha256_lf=sha if pin == "file" else REG["pool_file_sha256_lf"])
        return patch

    cases = [  # (wal bytes, pin, child, refusal substring)
        (7, "file", child(0, good), "side_fixture.db-wal is 7 bytes"),
        (0, "reg", child(0, good), "not the pinned 79d48f4b36434a551d3e706618a6a5e0cad9b0174d8e711bfeeb27f601b0f5a6"),
        (0, "file", child(1, good), "v2_union_pool.py --dry-run rc 1"),
        (0, "file", child(0, ["[UNION-POOL] pool pv2_other recomputed; expected pv2_fixture"] + good[1:]), "first line is"),
        (0, "file", child(0, good[:1]), "no \"every check passed\" line"),
    ]
    saved_sp = GB.subprocess
    try:
        for wal, pin, ch, want in cases:
            tmp = factory()
            GB.subprocess = ch
            n0 = len(calls)
            res, text, fc, tr = _run(tmp, "H", argv=["--dry-run", "--lane", "r2"], expect_refusal="the B0-2 pool check of pv2_fixture failed",
                                     patch_extra=setup(tmp, wal, pin), pool=GB.pool_check_v2)
            assert want in res, (want, res)
            first = text.splitlines()[0]
            assert first.startswith("POOL pv2_fixture (B0-2 pool check rc 1): ") and want in first, first
            assert len(text.splitlines()) == 1, text         # nothing after the refusal
            assert (len(calls) - n0) == (0 if (wal or pin == "reg") else 1), "child order: side files and pin are checked first"
            assert not os.path.exists(GB.P(tmp, fc["out"]))
        tmp = factory()
        GB.subprocess = child(0, good)
        n0 = len(calls)
        res, text, fc, tr = _run(tmp, "H", argv=["--dry-run", "--lane", "r2"], patch_extra=setup(tmp, 0, "file"), pool=GB.pool_check_v2)
    finally:
        GB.subprocess = saved_sp
    assert res == 0, res
    assert len(calls) - n0 == 1 and calls[-1][1].endswith("v2_union_pool.py") and calls[-1][2:5] == ["--dry-run", "--pool", "pv2_fixture"], calls[-1]
    first = text.splitlines()[0]
    assert first.startswith("POOL pv2_fixture (B0-2 pool check rc 0): " + good[0] + " | " + good[1]), first
    assert ("engine pool file sha256-lf %s (pinned)" % hashlib.sha256(body).hexdigest()[:16]) in first and "side_fixture.db-wal absent" in first, first
    _need(text, "I1 PASSED (SEEN)", "I3 PASSED", "dry-run: NO new statistic computed or printed")
    return True


def _synthetic_R(ab=(-0.003, -0.012, 0.006), ac=(0.004, -0.010, 0.018), db=(0.018, 0.006, 0.030), sp_b=0.008, sp_c=0.012, sp_kc=0.0112,
                 abm=(-0.005, -0.02, 0.01), acm=(0.005, -0.01, 0.02), dbm=(0.035, 0.015, 0.055), spm=(0.004, 0.006, 0.01)):
    def st(t):
        return dict(d=t[0], lo=t[1], hi=t[2], se=0.0042, deff=1.3, n=6139, G=5628, n_eff=4700.0, mde=0.0118, disc=0.08)
    R = {"R1": {"D_AB": st(ab), "D_AC": st(ac), "D_DB": st(db)}, "spread_B": sp_b, "spread_C": sp_c, "spread_KC": sp_kc,
         "R2": {"MMLU_PRO_LB": {"st": {"D_AB": st(abm), "D_AC": st(acm), "D_DB": st(dbm)}}},
         "M": {"C-AB-M": spm[0], "C-AC-M": spm[1], "C-DB-M": spm[2]}}
    R["V"] = {"C-AB": v_spread(ab[0], ab[1], ab[2], sp_b), "C-AC": v_spread(ac[0], ac[1], ac[2], sp_c),
              "C-DB": v_spread(db[0], db[1], db[2], max(sp_b, sp_kc)),
              "C-AB-M": v_interval(abm[1], abm[2]), "C-AC-M": v_interval(acm[1], acm[2]), "C-DB-M": v_interval(dbm[1], dbm[2])}
    R["frule"] = f_rule(ab[1], ac[1], -0.0108)
    return R


def st_branches():
    """Every criterion / falsifier / consequence branch printed with its values (verdict_lines, which render uses verbatim)."""
    L = "\n".join(verdict_lines(_synthetic_R()))
    _need(L, "C-AB: UNDETERMINED: D_AB -0.0030, interval [-0.0120, +0.0060], spread_B 0.0080; neither clause holds",
          "C-AC: UNDETERMINED: D_AC +0.0040", "C-DB: HELD (label information below depth 2 buys filing over a label-free split at matched"
          " cells): D_DB +0.0180, interval [+0.0060, +0.0300], max(spread_B, spread_KC) 0.0112",
          "C-AB-M: UNDETERMINED: D_AB_M -0.0050, interval [-0.0200, +0.0100] (MMLU_PRO_LB, the interval decides); stratum spread 0.0040;"
          " the interval contains 0",
          "C-DB-M: HELD: D_DB_M +0.0350, interval [+0.0150, +0.0550] (MMLU_PRO_LB, the interval decides); stratum spread 0.0100;"
          " interval wholly above 0",
          "F-RULE: DOES NOT FIRE: lower ends D_AB -0.0120, D_AC -0.0100; both must lie above -0.0108",
          "CONSEQUENCE: neither registered branch applies (F-RULE did not fire, C-DB HELD, C-AB UNDETERMINED, C-AC UNDETERMINED).",
          "  support C-DB: SE 0.00420 (registered 0.00398); DEFF 1.300 (transported 1.214); n_eff 4700; MDE80 0.0118 (registered 0.0111);"
          " discordance 0.0800 (planning 0.08); effective bar max(MDE80, spread) 0.0118")
    # C-DB bar is the LARGER of spread_B and spread_KC: d between them is UNDETERMINED
    L = "\n".join(verdict_lines(_synthetic_R(db=(0.010, 0.002, 0.018), sp_b=0.008, sp_kc=0.0112)))
    _need(L, "C-DB: UNDETERMINED: D_DB +0.0100")
    # F-RULE fires + C-DB HELD
    L = "\n".join(verdict_lines(_synthetic_R(ab=(0.0, -0.008, 0.008), ac=(0.001, -0.007, 0.009))))
    _need(L, "F-RULE: FIRES", "lower ends D_AB -0.0080 and D_AC -0.0070 both above -0.0108",
          "CONSEQUENCE (F-RULE fired and C-DB HELD): the gap is attributed to label information below depth 2")
    # F-RULE needs BOTH: only D_AB above
    L = "\n".join(verdict_lines(_synthetic_R(ab=(0.0, -0.008, 0.008), ac=(-0.01, -0.02, 0.0))))
    _need(L, "F-RULE: DOES NOT FIRE: lower ends D_AB -0.0080, D_AC -0.0200")
    # C-AB HELD / REVERSED; C-AC REVERSED; both consequences
    L = "\n".join(verdict_lines(_synthetic_R(ab=(0.02, 0.01, 0.03))))
    _need(L, "C-AB: HELD (the vMF construction beats flat spherical k-means at matched cells within the same anchors): D_AB +0.0200,"
             " interval [+0.0100, +0.0300], spread_B 0.0080; interval wholly above 0 and D_AB > spread_B")
    L = "\n".join(verdict_lines(_synthetic_R(ab=(-0.02, -0.03, -0.01), ac=(-0.02, -0.03, -0.01))))
    _need(L, "C-AB: REVERSED (flat spherical k-means beats", "interval wholly below 0 and D_AB < -spread_B",
          "C-AC: REVERSED (PCA-GMM beats", "CONSEQUENCE (C-AB or C-AC REVERSED: C-AB REVERSED, C-AC REVERSED): the split rule is implicated")
    L = "\n".join(verdict_lines(_synthetic_R(ab=(-0.005, -0.009, -0.001), ac=(0.0, -0.005, 0.005), sp_b=0.001)))
    _need(L, "C-AB: REVERSED", "F-RULE: FIRES", "CONSEQUENCE (F-RULE fired and C-DB HELD)", "the split rule is implicated",
          "NOTE: both registered consequence branches apply")
    # a point inside the spread with the interval clear of 0: UNDETERMINED (the spread clause), and -M seed-fragile
    L = "\n".join(verdict_lines(_synthetic_R(ab=(0.005, 0.001, 0.009), abm=(0.003, 0.001, 0.005), spm=(0.004, 0.006, 0.01))))
    _need(L, "C-AB: UNDETERMINED: D_AB +0.0050", "C-AB-M: HELD: D_AB_M +0.0030", "; seed-fragile (|D_AB| 0.0030 < stratum spread 0.0040)")
    L = "\n".join(verdict_lines(_synthetic_R(acm=(-0.03, -0.05, -0.01))))
    _need(L, "C-AC-M: REVERSED: D_AC_M -0.0300", "interval wholly below 0")
    return True


def st_boundaries():
    assert v_spread(0.01, 0.0, 0.02, 0.0) == "UNDETERMINED"          # lo == 0 is not wholly above
    assert v_spread(0.008, 0.001, 0.02, 0.008) == "UNDETERMINED"     # d == bar is not beyond it
    assert v_spread(0.0081, 0.001, 0.02, 0.008) == "HELD"
    assert v_spread(-0.0081, -0.02, -0.001, 0.008) == "REVERSED"
    assert v_spread(-0.01, -0.02, 0.0, 0.0) == "UNDETERMINED"        # hi == 0 is not wholly below
    assert v_interval(0.0, 0.1) == "UNDETERMINED" and v_interval(1e-9, 0.1) == "HELD" and v_interval(-0.1, -1e-9) == "REVERSED"
    assert f_rule(-0.0108, 0.0, -0.0108) is False and f_rule(-0.0107, -0.0107, -0.0108) is True
    assert f_rule(np.float64(0.0), np.float64(0.0), -0.0108) is True    # a numpy value gives a python bool
    assert spread([0.1, 0.3, 0.2, 0.25, 0.05]) == 0.3 - 0.05
    assert G.in_band(0.005, (0.0, 0.005)) == "HELD" and G.in_band(0.0051, (0.0, 0.005)) == "FAILED"
    assert bin_name((8, 99)) == ">= 8" and bin_name((2, 3)) == "2-3" and bin_name((1, 1)) == "1"
    # registered constants
    assert REG["pca"] == 16 and REG["pca_sens"] == (32, 64) and REG["gmm_iter"] == 200 and REG["reg_covar"] == 1e-6
    assert tuple(SEEDS) == (0, 1, 2, 3, 4) and G.BOOT_B == 2000 and G.BOOT_SEED == 20260929 and REG["frule"] == -0.0108
    assert REG["out"].endswith("rp12_r2/deep_split_compare_outcome.txt") and REG["pool"] == "pv2_1575de61bb20e977"
    assert _POOL_GUARD[0] is GB.pool_check_v2, "the pool check must be g13_breakdown's B0-2 form"
    assert REG["pool_file"] == "experiment_configs/engine_pool_pv2_1575de61bb20e977.json" and REG["guard_args"] == ()
    assert REG["pool_file_sha256_lf"] == "79d48f4b36434a551d3e706618a6a5e0cad9b0174d8e711bfeeb27f601b0f5a6", "B0-2 pin 79d48f4b"
    assert len(REG["guard_dbs"]) >= 1 and all(os.path.isabs(d) for d in REG["guard_dbs"])
    assert len(ANCHOR_TABLE) == 52 and sum(v[0] for v in ANCHOR_TABLE.values()) == 133
    ks = Counter()
    for k, v in ANCHOR_TABLE.items():
        ks[k.split("/")[0]] += v[0]
    assert dict(ks) == {"MMLU_PRO_LB": 74, "BBH": 36, "MATH": 9, "MUSR": 6, "IFEVAL": 5, "GPQA": 3}, ks
    assert sum(v[4] for v in ANCHOR_TABLE.values()) == 12334 and sum(v[3] for v in ANCHOR_TABLE.values()) == 12334
    assert sum(v[2] for v in ANCHOR_TABLE.values()) == 12334, "I3: F-tree is a partition of the TRAIN items"
    assert sum(1 for v in ANCHOR_TABLE.values() if v[0] > 1) == 32
    gm = gmm_fit(np.random.default_rng(4).standard_normal((30, 2)), 2, 0)
    assert (gm.covariance_type, gm.init_params, gm.n_init, gm.max_iter, gm.reg_covar, gm.random_state) == ("diag", "k-means++", 1, 200, 1e-6, 0)
    assert "NOT SCORED" in pred_line("D_AB", None) and "NOT SCORED" in pred_line("D_AB", float("nan"))
    assert pred_line("D_AB", -0.003).endswith("-> HELD") and pred_line("D_AB", 0.0121).endswith("-> FAILED")
    # PCA sign rule is deterministic under a sign flip of the data axes' SVD
    X = np.random.default_rng(3).standard_normal((40, 6))
    mu, V = pca_fit(X, 3)
    assert all(V[i, np.argmax(np.abs(V[i]))] > 0 for i in range(3))
    return True


def st_filing():
    """C files by COSINE to its cells' 512-d centroids over all cells, never by GMM likelihood; naming from TRAIN only."""
    rng = np.random.default_rng(5)
    d = 8
    e = np.eye(d)
    # one split anchor: a tight cluster at e0 (class 0) and a cluster spread along e0 around e1 (class 1)
    tight = [_u(e[0] + 0.01 * rng.standard_normal(d)) for _ in range(30)]
    broad = [_u(e[1] + t * e[0] + 0.01 * rng.standard_normal(d)) for t in np.linspace(-0.6, 0.6, 30)]
    Xt = np.vstack(tight + broad)
    yt = np.array([0] * 30 + [1] * 30)
    q = _u(e[0] + 0.55 * e[1])                       # cosine: nearer the tight centroid; likelihood: the broad component
    Xe = np.vstack([q, q])
    ye = np.array([1, 1])
    o = {"Xt": Xt, "yt": yt, "Xe": Xe, "ye": ye, "classes": ["a", "b"]}
    A = {"anchors": ["S:n1"], "label": {"S:n1": "a"}, "a_cls": np.array([0]), "ftree": [np.arange(60)]}
    saved = _CFG[0]
    _CFG[0] = dict(REG, pca=2)
    try:
        A.update(gt=A["ftree"], banc=A["ftree"], ka=np.array([2]))
        _CFG[0]["pca_sens"] = (3, 4)
        arms = fit_arms(o, A)                            # the path main() takes
        assert all(arms["C"][s]["ok"].tolist() == [0, 0] for s in SEEDS), [arms["C"][s]["ok"] for s in SEEDS]
        C, ca, _t, dr, models, kch, _nc = cells_gmm(o, A, A["ftree"], np.array([2]), 0, 2)
        ok, names, _ne, e_cell = name_and_file(o, A, C, ca)
        mu, V, gm = models[0]
        lik = gm.predict(((Xe - mu) @ V.T))
        comp_of_cell = [int(gm.predict(((C[j][None, :] - mu) @ V.T))[0]) for j in range(len(C))]
    finally:
        _CFG[0] = saved
    assert dr == 0 and len(C) == 2 and sorted(names.tolist()) == [0, 1]
    # an EMPTY component (no item has it as maximum responsibility) is dropped and counted, never kept as a cell
    class _GM:
        n_components, converged_ = 3, True
    g = globals()
    saved_pg = g["_pca_gmm"]
    g["_pca_gmm"] = lambda X, k, seed, d, bic, kmax: (X.mean(axis=0), np.eye(2, X.shape[1]), _GM(), np.array([0] * 30 + [1] * 30))
    try:
        C3, ca3, _t3, dr3, _m3, kch3, _n3 = cells_gmm(o, A, A["ftree"], np.array([3]), 0, 2)
    finally:
        g["_pca_gmm"] = saved_pg
    assert dr3 == 1 and len(C3) == 2 and kch3[0] == 3 and np.allclose(np.linalg.norm(C3, axis=1), 1.0), (dr3, len(C3))
    assert names[e_cell[0]] == 0 and ok.tolist() == [0, 0], "cosine filing must send q to the tight (class 0) cell"
    assert comp_of_cell[e_cell[0]] != int(lik[0]), "the fixture must separate cosine from likelihood filing"
    return True


def _synthetic_arms(bbh_bad=False):
    """40 items in 20 components (30 MMLU_PRO_LB, 10 BBH); anchors 0 (k_a 2, depth 3; items 0-19) and 1 (k_a 1, depth 2; 20-39).
    A wrong 0-5 (and 30-39 with bbh_bad); B_s wrong {0,2,4,6} (+8 for s = 1, 4: seeds differ item-wise); C_s = B_s, C_4 all right;
    D_s right except D_1 item 39 and D_4 MMLU items 10-29 (KC's MMLU spread 20/30 > |D_DB_M|)."""
    n = 40
    comp = np.arange(n) // 2
    esrc = np.array(["MMLU_PRO_LB"] * 30 + ["BBH"] * 10)
    okA = np.ones(n, dtype=np.int64)
    okA[:6] = 0
    if bbh_bad:
        okA[30:] = 0
    B = {s: np.ones(n, dtype=np.int64) for s in SEEDS}
    for s in SEEDS:
        B[s][[0, 2, 4, 6]] = 0
    B[1][8] = 0
    B[4][8] = 0
    C = {s: B[s].copy() for s in SEEDS}
    C[4][:] = 1
    D = {s: np.ones(n, dtype=np.int64) for s in SEEDS}
    D[1][39] = 0
    D[4][10:30] = 0
    ident = {"kc_ok": D, "t_kc": {s: 1.0 for s in SEEDS}}
    arms = {a: {s: dict(ok=(C if a.startswith("C") else B)[s], t=1.0, empty=0, dropped=0, k_total=3) for s in SEEDS}
            for a in ARMS_DECIDING + ARMS_DESC}
    o = {"comp": comp, "ye": np.zeros(n, dtype=int), "fl": okA, "esrc": esrc, "nodes": {"L:1": {"depth": 3}, "L:2": {"depth": 2}},
         "eleaf": ["L:1"] * 20 + ["L:2"] * 20}
    A = {"maxd": np.array([3, 2]), "ka": np.array([2, 1]), "e_anchor": np.array([0] * 20 + [1] * 20)}
    saved = _CFG[0]
    _CFG[0] = dict(REG, r3_depth={2: 20, 3: 20}, leaf_strata=((2, 2), (3, 99)), sources=("MMLU_PRO_LB", "BBH"))
    try:
        return summarize(o, A, arms, ident)
    finally:
        _CFG[0] = saved


def st_summarize():
    """summarize() on synthetic per-seed vectors: all five seeds enter the spreads (seed 4 carries extremes); s = 0 compares; the
    C-DB bar is max(spread_B, spread_KC); the -M clauses read MMLU_PRO_LB items with the interval alone; F-RULE reads lower ends."""
    R = _synthetic_arms()
    eq = lambda a, b: abs(a - b) < 1e-12          # noqa: E731
    assert eq(R["spread_B"], 0.9 - 0.875) and eq(R["spread_C"], 1.0 - 0.875) and eq(R["spread_KC"], 1.0 - 0.5), R
    assert eq(R["P"]["B"][0], 0.9) and eq(R["R1"]["D_AB"]["d"], -0.05)            # s = 0 is the comparator (B_1 gives -0.025)
    assert eq(R["R1"]["D_DB"]["d"], 0.10) and eq(R["R1"]["D13"]["d"], -0.15)       # D_0 (D_1 gives 0.075)
    assert eq(R["M"]["C-AB-M"], 26 / 30 - 25 / 30) and eq(R["M"]["C-DB-M"], 1.0 - 10 / 30)
    assert eq(R["R2"]["MMLU_PRO_LB"]["st"]["D_AB"]["d"], -2 / 30) and eq(R["R2"]["BBH"]["st"]["D_AB"]["d"], 0.0)
    assert eq(R["R2"]["MMLU_PRO_LB"]["share"]["D_DB"], 1.0) and eq(R["R2"]["BBH"]["share"]["D_DB"], 0.0)
    assert R["R1"]["D_DB"]["lo"] > 0 and R["R1"]["D_DB"]["d"] > R["spread_B"], "fixture must separate the C-DB bars"
    assert R["V"]["C-DB"] == "UNDETERMINED", R["V"]                               # 0.10 < max(0.025, 0.5)
    st_m = R["R2"]["MMLU_PRO_LB"]["st"]["D_DB"]
    assert st_m["lo"] > 0 and abs(st_m["d"]) < R["M"]["C-DB-M"], "fixture must separate interval-only from the spread form"
    assert R["V"]["C-DB-M"] == "HELD", R["V"]                                     # the interval alone decides
    assert R["R1"]["D_AB"]["lo"] < -0.0108 < R["R1"]["D_AB"]["hi"] and R["frule"] is False
    names = [nm for nm, _r in R["R3"]]
    assert "(ii) true-anchor k_a 4-7" in names and dict(R["R3"])["(ii) true-anchor k_a 4-7"] is None
    r_ka1 = dict(R["R3"])["(ii) true-anchor k_a 1"]
    assert r_ka1["n"] == 20 and eq(r_ka1["st"]["D_AB"]["d"], 0.0)
    r_ka2 = dict(R["R3"])["(ii) true-anchor k_a 2-3"]
    assert eq(r_ka2["st"]["D_DB"]["d"], 0.2) and eq(R["share_db_ka4"], 0.0) and eq(R["ka1_range"], 0.0)
    # BBH all wrong for A: overall D_AB wholly below 0, MMLU's interval contains 0 -> C-AB-M is MMLU's word
    R2 = _synthetic_arms(bbh_bad=True)
    assert R2["R1"]["D_AB"]["hi"] < 0 and R2["R2"]["MMLU_PRO_LB"]["st"]["D_AB"]["lo"] <= 0 <= R2["R2"]["MMLU_PRO_LB"]["st"]["D_AB"]["hi"]
    assert R2["V"]["C-AB-M"] == "UNDETERMINED", R2["V"]
    return True


CASES = (("boundaries", "verdict functions at their boundaries; registered constants; the table's sums; PCA sign rule", "plain"),
         ("branches", "every C-AB / C-AC / C-DB / -M / F-RULE / consequence branch printed with its values", "plain"),
         ("summarize", "spreads over all five seeds, s = 0 comparator, per-source / stratum values, empty stratum", "plain"),
         ("filing", "C files by cosine over all cells (not GMM likelihood); TRAIN naming", "plain"),
         ("e2e_H", "--run, fixture H: every deciding value by hand; write-once", "tmp"),
         ("e2e_P", "--run, fixture P: A = B, F-RULE FIRES, label-information consequence", "tmp"),
         ("e2e_S", "--run, fixture S: per-seed partitions, spread_B, D constant", "tmp"),
         ("dry_run", "--dry-run: pool line first, identities, no statistic, no outcome", "tmp"),
         ("refusals", "lane, I1, depth 2, I2, I3, R3 support, side check, pool check (line first)", "factory"),
         ("pool", "the REAL B0-2 pool check through --dry-run: -wal, pin 79d48f4b, child rc, first line, every check passed; pass", "factory"))
_FN = {"boundaries": st_boundaries, "branches": st_branches, "summarize": st_summarize, "filing": st_filing, "e2e_H": st_e2e_H,
       "e2e_P": st_e2e_P, "e2e_S": st_e2e_S, "dry_run": st_dry_run, "refusals": st_refusals, "pool": st_pool}


def selftest(only=None, quiet=False):
    import tempfile
    import shutil
    made, fails, ran = [], [], 0

    def factory():
        d = tempfile.mkdtemp(prefix="dsc_")
        made.append(d)
        return d
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(factory()) if kind == "tmp" else fn(factory)
                if not quiet:
                    print("  ok   %-11s %s" % (name, desc))
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    print("  FAIL %-11s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:400]))
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    print("MUTANTS (%d): one temporary edit each (in memory); KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed, base, control_ok = 0, {}, True
    for name, edits, tests in MUTANTS:
        mut = head
        for old, new in edits:
            if mut.count(old) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times (must be exactly 1): %r" % (TAG, name, mut.count(old), old[:80]))
            mut = mut.replace(old, new)
        key = tuple(sorted(tests))
        if key not in base:
            base[key] = _exec_selftest(src, tests)
        res = _exec_selftest(mut + tail, tests)
        k = res is not True and base[key] is True
        if name.startswith("M00"):
            control_ok = res is True and base[key] is True
            print("  %-52s tests %-20s original %-4s control %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "SURVIVED (as it must)" if control_ok else "KILLED (harness broken)"))
            continue
        killed += int(k)
        print("  %-52s tests %-20s original %-4s mutant %-8s %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:90]), flush=True)
    n_real = sum(1 for m in MUTANTS if not m[0].startswith("M00"))
    print("MUTANTS: %d of %d KILLED; control %s" % (killed, n_real, "survived" if control_ok else "KILLED"))
    return 0 if killed == n_real and control_ok else 1


def _exec_selftest(src, tests):
    ns = {"__name__": "deep_split_compare_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])


NL = chr(10)
MUTANTS = (
    ("M00 control (no-op edit)", [("    return max(vals) - min(vals)", "    return max(vals) - min(vals)")], ["boundaries", "e2e_H"]),
    ("M01 EVAL rows enter the B fit (wrong side)", [("            r, t = timed(FM.spherical_kmeans, X, k, seed, max_iter=G.MAX_ITER)",
                                                    '            r, t = timed(FM.spherical_kmeans, np.vstack([X, o["Xe"]]), k, seed, max_iter=G.MAX_ITER)')],
     ["e2e_H"]),
    ("M02 B fit set = GT class membership, not F-tree", [('specs = (("B", "km", A["ftree"], None),', 'specs = (("B", "km", A["gt"], None),')], ["e2e_H"]),
    ("M03 k_a off by one", [('C, ca, t, dr = cells_kmeans(o, A, fs, A["ka"], s,', 'C, ca, t, dr = cells_kmeans(o, A, fs, A["ka"] + 1, s,')], ["e2e_H"]),
    ("M04 EVAL filed within its TRUE anchor (oracle)", [('    e_cell = np.argmax(o["Xe"] @ C.T, axis=1)' + NL + "    ok = (names[e_cell]",
                                                       '    e_cell = np.argmax(np.where(ca[None, :] == A["e_anchor"][:, None], o["Xe"] @ C.T, -np.inf), axis=1)' + NL
                                                       + "    ok = (names[e_cell]")], ["e2e_H"]),
    ("M05 C filed by GMM likelihood, not cosine", [("            ok, names, n_empty, e_cell = name_and_file(o, A, C, ca)" + NL,
                                                   "            ok, names, n_empty, e_cell = name_and_file(o, A, C, ca)" + NL
                                                   + '            if kind == "gmm":' + NL
                                                   + "                for i in range(len(ok)):" + NL
                                                   + "                    a = int(ca[e_cell[i]])" + NL
                                                   + '                    if a in rec["models"]:' + NL
                                                   + '                        mu, V, gm = rec["models"][a]' + NL
                                                   + '                        j = int(gm.predict(((o["Xe"][i] - mu) @ V.T)[None, :])[0])' + NL
                                                   + "                        cells = np.flatnonzero(ca == a)" + NL
                                                   + '                        ok[i] = int(names[cells[min(j, len(cells) - 1)]] == o["ye"][i])' + NL)],
     ["filing"]),
    ("M06 cells named from EVAL (wrong side)", [('    t_cell = np.argmax(o["Xt"] @ C.T, axis=1)' + NL + "    names = np.empty(len(C), dtype=int)",
                                               '    t_cell = np.argmax(o["Xe"] @ C.T, axis=1)' + NL + "    names = np.empty(len(C), dtype=int)"),
                                              ('        m = GB.majority(o["yt"][t_cell == j], o["classes"])', '        m = GB.majority(o["ye"][t_cell == j], o["classes"])')],
     ["e2e_H"]),
    ("M07 spread_C over the first four seeds", [('spread(R["P"]["C"].values())', 'spread(list(R["P"]["C"].values())[:4])')], ["summarize"]),
    ("M08 per-source stratum leaks across sources", [("        st = {k: GB.stat(v, comp[m]) for k, v in contrasts(ok0, m).items()}" + NL + "        sp = ",
                                                     "        st = {k: GB.stat(v, comp) for k, v in contrasts(ok0).items()}" + NL + "        sp = ")],
     ["summarize"]),
    ("M09 spread min<->max", [("    return max(vals) - min(vals)", "    return min(vals) - max(vals)")], ["summarize", "boundaries"]),
    ("M10 D_DB sign flipped", [('"D_DB": D0 - B0', '"D_DB": B0 - D0')], ["e2e_H"]),
    ("M11 C-DB bar = spread_B only", [('R["R1"]["D_DB"]["hi"], max(R["spread_B"], R["spread_KC"])),', 'R["R1"]["D_DB"]["hi"], R["spread_B"]),')],
     ["summarize"]),
    ("M12 v_spread without the point clause", [("    if lo > 0 and d > bar:", "    if lo > 0:")], ["boundaries"]),
    ("M13 -M clauses read with the spread clause", [('R["V"][key] = v_interval(st["lo"], st["hi"]) if st else "UNDETERMINED"',
                                                    'R["V"][key] = v_spread(st["d"], st["lo"], st["hi"], R["M"][key]) if st else "UNDETERMINED"')],
     ["summarize"]),
    ("M14 seed-fragile word omitted", [('if abs(st["d"]) < sp else ""', 'if False else ""')], ["branches"]),
    ("M15 F-RULE reads the upper ends", [('R["frule"] = f_rule(R["R1"]["D_AB"]["lo"], R["R1"]["D_AC"]["lo"], c["frule"])',
                                         'R["frule"] = f_rule(R["R1"]["D_AB"]["hi"], R["R1"]["D_AC"]["hi"], c["frule"])')], ["summarize"]),
    ("M16 F-RULE with OR", [("    return bool(lo_ab > bar) and bool(lo_ac > bar)", "    return bool(lo_ab > bar) or bool(lo_ac > bar)")], ["boundaries"]),
    ("M17 F-RULE silent when it does not fire",
     [('        L.append("F-RULE: DOES NOT FIRE: lower ends D_AB %+.4f, D_AC %+.4f; both must lie above %+.4f (= -|D13| / 2)" % (lab, lac, c["frule"]))',
       "        pass")], ["branches", "e2e_H"]),
    ("M18 split-rule consequence omitted", [('    if R["V"]["C-AB"] == "REVERSED" or R["V"]["C-AC"] == "REVERSED":', "    if False:")], ["branches", "e2e_H"]),
    ("M19 comparator of record B_1", [('ok0 = {"A": okA, "B": okB[0], "C": okC[0], "D": okD[0]}', 'ok0 = {"A": okA, "B": okB[1], "C": okC[0], "D": okD[0]}')],
     ["summarize"]),
    ("M20 empty stratum not handled (zero sites)", [('            R["R3"].append((name, None))' + NL + "            continue" + NL, "            pass" + NL)],
     ["summarize", "e2e_H"]),
    ("M21 R3 strata from A's output, not the true anchor",
     [('    md_e, ka_e = A["maxd"][A["e_anchor"]], A["ka"][A["e_anchor"]]' + NL + '    ldep =',
       '    _fa = [A["leaf_anchor"][u] for u in o["eleaf"]]' + NL + '    md_e, ka_e = A["maxd"][_fa], A["ka"][_fa]' + NL + '    ldep =')],
     ["e2e_H"]),
    ("M22 write-once removed (check and mode x)", [("        if a.run and os.path.exists(outp):", "        if False:"), ('with open(outp, "x"', 'with open(outp, "w"')],
     ["e2e_H"]),
    ("M23 write-once check removed (mode x kept)", [("        if a.run and os.path.exists(outp):", "        if False:")], ["e2e_H"]),
    ("M24 I1 check removed", [("        ident = GB.check_i1(GB.identity_arms(o))", "        ident = GB.identity_arms(o)")], ["refusals"]),
    ("M25 depth-2 check removed", [("    bad = [k for k in want if got[k] != want[k]]" + NL + "    if bad:" + NL + '        refuse("depth 2',
                                    "    bad = []" + NL + "    if bad:" + NL + '        refuse("depth 2')], ["refusals"]),
    ("M26 I2 child-count check removed", [('    if dict(hist) != dict(c["children"]):', "    if False:")], ["refusals"]),
    ("M27 I3 table check removed", [("        if want is None or tuple(want) != got:", "        if False:")], ["refusals"]),
    ("M28 lane guard removed", [('    if lane != "r2":' + NL + '        refuse("DEEP-SPLIT-COMPARE', "    if False:" + NL + '        refuse("DEEP-SPLIT-COMPARE')], ["refusals"]),
    ("M29 pool refusal removed", [("        if rc != 0:" + NL + '            refuse("the B0-2 pool check', "        if False:" + NL + '            refuse("the B0-2 pool check')],
     ["refusals"]),
    ("M30 dry-run prints a statistic", [('            out("%s dry-run: NO new statistic computed or printed" % TAG)',
                                         "            out(render(compute(o, A, ident), o, A, ident, d2, i4_ok))")], ["dry_run"]),
    ("M31 share over n_s (registered n D)", [('share[key] = (st[key]["n"] * st[key]["d"]) / tot if tot != 0 else float("nan")',
                                              'share[key] = (st[key]["n"] * st[key]["d"]) / (st[key]["n"] * R["R1"][key]["d"]) if tot != 0 else float("nan")')],
     ["e2e_H"]),
    ("M32 unsplit cell = anchor vmfMu, not the F-tree mean",
     [("            cents.append(unit(X.sum(axis=0))[None, :])" + NL + "            ca.append(a)" + NL + "            continue" + NL,
       '            cents.append(A["amu"][a][None, :])' + NL + "            ca.append(a)" + NL + "            continue" + NL)],
     ["e2e_H"]),
    ("M33 I4 check removed", [("    if not np.array_equal(ok, ref):" + NL + '        refuse("I4', "    if False:" + NL + '        refuse("I4')], ["refusals"]),
    ("M34 pool check is not g13_breakdown's B0-2 form", [("_POOL_GUARD = [GB.pool_check_v2]", '_POOL_GUARD = [lambda pool: (0, "pool_guard")]')], ["boundaries"]),
    ("M35 GMM full covariance", [('covariance_type="diag"', 'covariance_type="full"')], ["boundaries"]),
    ("M36 primary PCA at 32 dims", [("    pca=16, pca_sens=(32, 64),", "    pca=32, pca_sens=(32, 64),")], ["boundaries"]),
    ("M37 side check not handed to g13_breakdown", [("= cfg(), _ROOT[0], _SIDES[0], _CLOCK[0]", "= cfg(), _ROOT[0], None, _CLOCK[0]")], ["refusals"]),
    ("M38 R2 first source only", [('    for so in c["sources"]:' + NL + '        m = o["esrc"] == so' + NL + "        if not m.any():",
                                   '    for so in c["sources"][:1]:' + NL + '        m = o["esrc"] == so' + NL + "        if not m.any():")], ["e2e_H"]),
    ("M39 -M clauses on the overall population", [('    r2m = R["R2"].get(c["scoreable"])' + NL + '    R["V"] = {',
                                                  '    r2m = {"st": R["R1"]}' + NL + '    R["V"] = {')], ["summarize"]),
    ("M40 B on the first anchor only", [("    cents, ca, t_fit = [], [], 0.0" + NL + '    for a in range(len(A["anchors"])):',
                                         "    cents, ca, t_fit = [], [], 0.0" + NL + "    for a in range(1):")], ["e2e_H"]),
    ("M41 NOT SCORED skipped on a NaN", [("    if obs is None or obs != obs:" + NL + '        return "PREDICTION %s: observed none',
                                          "    if obs is None:" + NL + '        return "PREDICTION %s: observed none')], ["boundaries"]),
    ("M42 C-DB printed bar = spread_B", [('bars = {"C-AB": R["spread_B"], "C-AC": R["spread_C"], "C-DB": max(R["spread_B"], R["spread_KC"])}',
                                          'bars = {"C-AB": R["spread_B"], "C-AC": R["spread_C"], "C-DB": R["spread_B"]}')], ["branches"]),
    ("M43 an empty GMM component kept, not dropped", [("            if not m.any():" + NL + "                dropped += 1" + NL + "                continue" + NL,
                                                       "            if not m.any():" + NL + "                dropped += 1" + NL)], ["filing", "e2e_H"]),
    ("M44 B0-2 pin overridden in this script's REG", [("    pca=16, pca_sens=(32, 64),", '    pool_file_sha256_lf="0" * 64, pca=16, pca_sens=(32, 64),')],
     ["boundaries", "pool"]),
    ("M45 g13 hooks keep g13's own config", [("    GB._CFG[0], GB._ROOT[0], GB._SIDES[0], GB._CLOCK[0] = cfg(), _ROOT[0], _SIDES[0], _CLOCK[0]",
                                              "    GB._CFG[0], GB._ROOT[0], GB._SIDES[0], GB._CLOCK[0] = GB._CFG[0], _ROOT[0], _SIDES[0], _CLOCK[0]")], ["pool"]),
    ("M46 pool line not printed before the refusal", [("        out(first)" + NL + "        if rc != 0:" + NL,
                                                       "        if rc != 0:" + NL + "            refuse(txt)" + NL + "        out(first)" + NL + "        if rc != 0:" + NL)],
     ["pool"]),
    ("M47 pool check on a hard-coded pool id", [('        rc, txt = _POOL_GUARD[0](cfg()["pool"])', '        rc, txt = _POOL_GUARD[0]("pv2_1575de61bb20e977")')], ["pool"]),
    ("M48 pool check skipped in --dry-run", [('        rc, txt = _POOL_GUARD[0](cfg()["pool"])',
                                             '        rc, txt = _POOL_GUARD[0](cfg()["pool"]) if a.run else (0, "skipped")')], ["pool"]),
)

if __name__ == "__main__":
    sys.exit(main())
