"""G13-BREAKDOWN (lane r2): where R2's anchored tree loses filing precision to class-conditional k-means (per member corpus,
per tree depth), whether it beats UNSUPERVISED k-means at matched k, whether the loss survives the filing rule, and what each
method costs in wall-clock. ZERO calls: no judge, no LLM, no embedding call, no build; no DB is opened by the readout (the
pool guard, a reader, runs as its own process first).

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-10-02 (before any code or call) — G13-BREAKDOWN: where
does R2's anchored tree lose filing precision ..." (L22887-L23048 _as_of ffed1d52; draft docs/agents/plans/2026-10-02_g13_breakdown.md
0b4b11a6). Implemented VERBATIM, with the registrar's pre-data insertions: "UNRESOLVED" is printed UNDETERMINED (TERMS);
C-b2's REVERSED is its FAILED; C-M carries the FAILED clause (interval wholly below 0); C-a1's MDE80 is 0.0203 (SE 0.00724);
C-b1 and C-a4 print "point seen before registration".

OBJECTS (lane r2, commit M 2703f2c2; every path under experiment_results/archv2/rp12_r2/, refused outside it by rp12_lane):
  bundle  B0/readouts/g13_bundle_flatleaf.{npz,json} (g13_comparator.load_bundle: pool, the 6,153 / 5,642 before MC-EXCLUDE,
          the 1% bar, check_sides against the committed side export: no EVAL or GATE item in any fit)
  flatLeaf B0/graft_flatleaf/seed_42/validation/MAIN_union_routing_{queries,train_queries,leaves}.csv (rp12_pairing.read_rows /
          item_cells: the item_id column, MC-EXCLUDE's multi-class items set aside exactly as in G13)
  descent B0/graft_descent/seed_42/validation/MAIN_union_routing_queries.csv
  trees   B0/<member>/seed_42/dag_snapshots.jsonl LAST line, six members; union id "<SOURCE>:<member id>", union depth = member
          depth + 1 (depth 1 corpus root, 2 declared-class anchor, >= 3 data-driven)
  timing  B0/<x>/seed_42/diagnostics/run_manifest.json (eight; each LF sha256 must equal the lane r2 pointer
          experiment_configs/rp12_r2/objects_of_record.json and its commit must be M 2703f2c2) and B0/<x>/seed_42/headless_run.log
          (untracked; sha256 printed, its TOTAL TIME lines copied; an absent log prints ABSENT, it never refuses: (d) decides nothing)
  Pinned readers (blob, LF): g13_comparator.py 61d83ec7, rp12_pairing.py 35214b3f, flat_mix_mmlu.py 555ae3ac (checked by g13).

IDENTITY PRECONDITIONS (each REFUSES before any new number prints):
  I0 provenance: eight manifests = the pointer's manifest_sha256_lf, commit 2703f2c2.
  I1 P_fl 0.8119; P(KC_s) 0.8334 / 0.8394 / 0.8340 / 0.8446 / 0.8413; D13 -0.0215 [-0.0301, -0.0125]; U-global seeds 0.7381 /
     0.7381 / 0.7159 / 0.7252 / 0.7573; NCC 0.8065: to the printed digits ("%.4f" strings).
  I2 P_descent 0.7182 on the 6,139 bundle items.
  I3 argmax cos(x, leaf vmfMu) over the 133 snapshot leaves = the CSV leaf_id on >= 99.9% of EVAL items (refused iff
     1000 x misses > n); the miss count printed.
  I4 every CSV leaf_id resolves to a snapshot leaf, the CSV leaf_depth is its union depth, every node has at most one parent
     and its chain reaches its corpus root; the leaves CSV is the snapshot leaf set.
  I5 Support (a): EVAL items / components per source and TRAIN per source equal the registered counts; leaves per source
     74 / 36 / 9 / 6 / 5 / 3.
  Also refused: the CSV's modal leaf disagreeing with rp12_pairing's cell, eval_fl disagreeing with the CSV, a bundle item
  without a CSV row, MC-EXCLUDE's lists differing from the CSVs' multi-class items, KC(2) != NCC (registered "asserted").

IMPLEMENTATION CHOICES (stated, for the READY to confirm or refuse):
  (i)   an item's leaf = the modal leaf_id over its rows (rp12_pairing P1's rule on leaf_id: ties to the smallest id); it must
        name the same cell as rp12_pairing.item_cells (leaf_dominant), item by item.
  (ii)  TRAIN-majority naming (A3 frontier nodes, U arms, KC-relabel): most TRAIN members, tie to the smaller class name
        (g13_comparator's ukm rule); a frontier node / cluster with no TRAIN member is "<empty>" and files wrong (count printed).
  (iii) A2 "the filed cell's source" = the source of the class the method files to (tree: the leaf's leaf_dominant).
  (iv)  stratum intervals (A1 per source, leaf-depth strata, A2 D_within): the stratum's items with their components
        re-indexed (g13_comparator.comp_groups), g13_comparator.boot (B 2,000, seed 20260929). No component crosses sources
        (checked and printed).
  (v)   U-source: the same seed s for every source's fit; its fit time is the sum over the six fits.
  (vi)  (e): margin ties keep item order (stable sort); kept = floor(n x c / 100) (80% of 6,139 = 4,911); the joint bootstrap
        draws whole components (flat_mix_mmlu.twin_boot_indices, default_rng(20260929), B 2,000) and re-selects each method's
        own top c% inside every replicate; never paired, never deciding.
  (vii) (d): every k-means fit is timed by perf_counter around the fit call only; the 12-thread column re-runs the same fits in
        a child process with OMP / OPENBLAS / MKL = 12 (numpy imported after the variables are set). "End-to-end build" in the
        D ratio prediction = the six member manifests + the flatLeaf graft manifest; the members-only ratio printed beside.
  (viii) a prediction "X [lo, hi]" is HELD iff the point lies in [lo, hi], endpoints inclusive (g13_comparator.in_band);
        "D(>= 5) within 0.005 of D13" is scored at each d = 5, 6, 7.
  Not applicable here (no judge verdicts, no posting): wrong(established), tie conventions A / B, --pilot / truncation guard,
  a call cache. Every verdict word: HELD / FAILED / UNDETERMINED (C-b2 and C-b1: HELD / REVERSED (its FAILED) / UNDETERMINED).

SELFTEST (--selftest; synthetic fixtures written as a complete lane-r2 layout in a temp dir and read through main(), the real
entry point; the pool guard, the 12-thread child and the machine probe are stubbed in the e2e cases and executed for real in
"worker"; a counting clock makes every fit time exactly 1.000 s):
  fixture A (12-d orthonormal axes; MMLU_PRO_LB classes x, y; BBH u, v; 130 EVAL in 65 components, 112 TRAIN, 5 leaves): an
  off-centre leaf (x@e6 filed to the y leaf; KC files it right) and a mixed mode under the x anchor (x@e1: leaf named y, anchor
  named x, KC and NCC wrong) give, by hand: P_fl 0.6154, KC_s 0.7692, NCC 0.7692, D13 -0.1538; D13_MMLU -0.2500 (share 1.0000),
  D13_BBH +0.0000; D_src 0, D_within -0.1667 on 120; P_tree(2) 0.7692 = P_NCC so D(2) 0, D(3) = D13; strata depth 2 0 (n 40),
  depth 3 -0.2222 (n 90), depth >= 4 n = 0; Delta -0.1538 (C-a4 HELD), C-a1 HELD; P_descent 0.4615, D13_desc -0.3077;
  KC-desc +0.0000; G_own 0 (C-M UNDETERMINED); P@80 tree 80/104 = 0.7692, KC 84/104 = 0.8077, difference -0.0385 (interval from an
  oracle loop); U-global / U-source / kNN against independent oracles (the fixture separates U-source from its source-oracle form
  and spreads the U seeds); D: 10.0 s members, loop 8.0 s, 15.0x; write-once re-run refused with the file unchanged.
  fixture B (KC's prototype dragged by TRAIN outliers): D13_MMLU +0.3333, C-a1 FAILED; Delta 0, C-a4 UNDETERMINED.
  branches: every C-a1 / C-a4 / C-b2 / C-b1 / C-M / F-GB / F-GB2 branch and the "UNDETERMINED by spread" sub-branch printed with
  its values (verdict_lines, which render uses verbatim). refusals: I0 (pointer), I1, I2, I3 (1 miss of 130), I4, I5 (support,
  leaves), MC-EXCLUDE, lane r1, pool guard rc 3 (its line printed first), KC(2) != NCC, k_c(2) != 1; no outcome written.
  dry_run: pool line first, I0-I5 and I1 (seen numbers), no statistic, no outcome. absent_log: ABSENT / INCOMPLETE lines.
  naming: a leaves-CSV name that is not the TRAIN-filed majority (counted 1; D(5) - D13 FAILED branch). seed: a changed KC_1
  moves only the ladder's KC row (KC_0 is the comparator of record everywhere).
MUTANTS (--mutants; one in-memory edit each, the targeted selftest subset re-run; 2026-10-02 at this commit): M00 control (no-op)
  SURVIVED; KILLED: M01 per-source stratum leaked across sources | M02 D13_s sign | M03 A1 first source only | M04 share over n_s |
  M05 k_c(d) off by one depth | M06 KC(2) != NCC admitted | M07 k_c(2) != 1 admitted | M08 frontier drops leaves shallower than d
  (boundary region) | M09 Delta sign | M10 U-source with a source oracle as primary | M11 U-source fitted and named on EVAL (wrong
  side) | M12 KC-relabel reads EVAL | M13 timing includes the objects load | M14 P@80 difference read as paired | M15 kept = round |
  M16 spread min<->max | M17 interval touching 0 read as below | M18 C-b2/C-b1 without the spread clause | M19 C-M without its
  FAILED clause | M20 C-a1 on the wrong population | M21 C-a1 support line omitted | M22 C-b1 seen-point disclosure omitted |
  M23 F-GB silent when it does not fire | M24 F-GB2 fires on HELD | M25 NOT SCORED line omitted (skip path) | M26 empty stratum
  (zero sites) unhandled | M27 ABSENT log line omitted | M28 comparator of record KC_1 | M29 write-once check removed | M30 check
  removed and mode w | M31 I1 refusal removed | M32 I3 bar at 1% | M33 I2 over every descent item (MC / GATE kept) | M34
  MC-EXCLUDE check removed | M35 I0 check removed | M36 lane guard removed | M37 I5 check removed | M38 dry-run prints a statistic:
  38 of 38 KILLED.

  python tools/analysis/g13_breakdown.py --selftest
  python tools/analysis/g13_breakdown.py --mutants
  [DELTA 2026-10-02 READY_g13_breakdown 7e6858eb D-1 / D-3 / D-4] the pool check is the B0-2 form (pool_check_v2:
  v2_union_pool.py --dry-run rc 0 with "expected pv2_1575de61bb20e977" and "every check passed", the engine pool file's sha256-lf
  79d48f4b36434a55..., 0-byte or absent -wal / -journal of multicorpus_cache_v1.db and corpus_v2_union_mc6.db), not
  pool_guard.py (no pv2 pool in its registry); selftest "guard" runs the REAL check on v2_union_pool's fixture DBs (accept;
  refusals: another pool, the pin, a -journal, a -wal; main refusing through it). D-3: an I1 refusal on hi. D-4: rp12_lane.py
  pinned (blob ac25b152). Mutants M39-M43 added (I1 ignoring lo/hi; the -wal / pin / child-rc checks removed; main not refusing).
  python tools/analysis/g13_breakdown.py --dry-run --lane r2   # B0-2 pool check first; pins; I0-I5 (I1 reprints SEEN numbers only); NO new statistic
  python tools/analysis/g13_breakdown.py --run --lane r2       # the readout; outcome WRITE-ONCE (mode x)
Output: experiment_results/archv2/rp12_r2/g13_breakdown_outcome.txt (write-once).
"""
import os
import sys

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
_THREADS = "1"
if "--time-worker" in sys.argv and "--threads" in sys.argv:          # the (d) 12-thread child only
    _THREADS = str(int(sys.argv[sys.argv.index("--threads") + 1]))
for _v in THREAD_VARS:
    os.environ[_v] = _THREADS

import io
import re
import json
import time
import hashlib
import argparse
import contextlib
import subprocess
from collections import Counter, defaultdict

import numpy as np   # noqa: E402  (imported AFTER the thread variables: g13_comparator's later "1" does not reach a child's BLAS)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

TAG = "[G13B]"
PINS = (("g13_comparator.py", "61d83ec7dfed00b834d5b2e5d0ca355d236520db"),
        ("rp12_pairing.py", "35214b3f11c3ffe4c1174885316f89775442f5c3"),
        ("rp12_lane.py", "ac25b15214a925ba45e2f53d23daf24710b393a3"))


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_lf(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        refuse("%s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import g13_comparator as G   # noqa: E402  (checks flat_mix_mmlu's pin itself)
import rp12_pairing as RP    # noqa: E402
import rp12_lane as LN       # noqa: E402
FM = G.FM

BOOT_B, BOOT_SEED, SEEDS = G.BOOT_B, G.BOOT_SEED, G.SEEDS
EMPTY = "<empty>"
RES = "experiment_results/archv2/rp12_r2"

# ── the registered constants (one dict; the selftest swaps in its fixture's; nothing else writes _CFG) ─────────────────────
REG = dict(
    pool=G.POOL_UNION, expect=(G.POOL_UNION, G.N_EVAL, G.N_COMP), commit="2703f2c2",
    members=(("bbh", "BBH"), ("gpqa", "GPQA"), ("ifeval", "IFEVAL"), ("math", "MATH"), ("mmlu_pro_lb", "MMLU_PRO_LB"), ("musr", "MUSR")),
    grafts=("graft_flatleaf", "graft_descent"),
    scoreable="MMLU_PRO_LB",
    sources=("MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA"),
    support_eval={"MMLU_PRO_LB": (3478, 3386), "BBH": (1718, 1408), "MATH": (390, 382), "MUSR": (229, 129), "IFEVAL": (162, 162),
                  "GPQA": (162, 161)},
    support_train={"MMLU_PRO_LB": 6977, "BBH": 3474, "MATH": 773, "MUSR": 454, "GPQA": 331, "IFEVAL": 325},
    leaves_by_source={"MMLU_PRO_LB": 74, "BBH": 36, "MATH": 9, "MUSR": 6, "IFEVAL": 5, "GPQA": 3},
    n_eval=6139, n_comp=5628, n_train=12334, n_leaves=133,
    depths=(2, 3, 4, 5, 6, 7), leaf_strata=((2, 2), (3, 3), (4, 4), (5, 5), (6, 99)),
    i1=dict(p_fl="0.8119", p_kc=("0.8334", "0.8394", "0.8340", "0.8446", "0.8413"), d13="-0.0215", lo="-0.0301", hi="-0.0125",
            ukm=("0.7381", "0.7381", "0.7159", "0.7252", "0.7573"), ncc="0.8065"),
    i2="0.7182",
    bundle=RES + "/B0/readouts/g13_bundle_flatleaf",
    fl_val=RES + "/B0/graft_flatleaf/seed_42/validation", de_val=RES + "/B0/graft_descent/seed_42/validation",
    b0=RES + "/B0", pointer="experiment_configs/rp12_r2/objects_of_record.json",
    out=RES + "/g13_breakdown_outcome.txt",
    # B0-2 (programme L22165; READY_g13_breakdown D-1): the pv2 pool check that replaces pool_guard.py
    pool_file="experiment_configs/engine_pool_pv2_1575de61bb20e977.json",
    pool_file_sha256_lf="79d48f4b36434a551d3e706618a6a5e0cad9b0174d8e711bfeeb27f601b0f5a6",
    guard_args=(),
    guard_dbs=(os.path.join(RP.C.DATA_ROOT, "multicorpus_cache_v1.db"),
               os.path.join(RP.C.DATA_ROOT, "data_v2", RP.EP.SPLIT_LABEL, "corpus_v2_union_mc6.db")),
)
_CFG = [REG]


def cfg():
    return _CFG[0]


# Registered Support (d)/(e) [REGISTRAR 2026-10-02 unrounded]: SE / MDE80 per deciding statistic; planning discordance (c)
SUPPORT_REG = {"C-a1": (0.00724, 0.0203, 0.15), "C-a4": (0.00466, 0.0131, 0.11), "C-b2": (0.00629, 0.0176, 0.20),
               "C-M": (0.00199, 0.0056, 0.02)}

# Registered PREDICTIONS (priors), interval form "X [lo, hi]"
PRED = {
    "A1 D13_MMLU": (-0.030, (-0.050, -0.010)), "A1 share MMLU_PRO_LB": (0.75, (0.45, 1.10)),
    "A1 D13_MATH": (-0.04, (-0.12, 0.04)), "A1 D13_GPQA": (-0.02, (-0.10, 0.06)), "A1 D13_IFEVAL": (-0.03, (-0.10, 0.04)),
    "A1 D13_BBH": (0.000, (-0.010, 0.010)), "A1 D13_MUSR": (0.000, (-0.010, 0.000)),
    "A2 D_src": (-0.005, (-0.015, 0.005)), "A2 D_within": (-0.018, (-0.030, -0.006)),
    "A3 D(2)": (-0.002, (-0.008, 0.004)), "A3 D(3)": (-0.010, (-0.020, 0.000)), "A3 D(4)": (-0.016, (-0.026, -0.006)),
    "A4 Delta": (-0.019, (-0.030, -0.008)),
    "B1 D_U": (0.074, (0.060, 0.090)),
    "B2 P(US_0)": (0.77, (0.74, 0.80)), "B2 D_Us": (0.040, (0.015, 0.070)), "B2 spread_US": (0.020, (0.010, 0.040)),
    "C D13_desc": (-0.115, (-0.130, -0.100)), "C D_U,desc": (-0.017, (-0.040, 0.010)), "C P(KC-desc) - P(KC_0)": (-0.010, (-0.025, 0.000)),
    "E P@80 tree": (0.87, (0.84, 0.90)), "E P@80 KC_0": (0.89, (0.86, 0.92)), "E P@80 U-global_0": (0.80, (0.76, 0.84)),
    "M G_own": (0.012, (0.004, 0.022)), "M P_fl - P(KC-relabel_0)": (-0.010, (-0.020, 0.000)),
    "D KC 5-seed median (s, 1 thread)": (None, (1.0, 10.0)), "D U-global 5-seed median (s, 1 thread)": (None, (20.0, 120.0)),
    "D tree end-to-end / KC median (1 thread)": (None, (10.0, 100.0)),
}
PROB = {"C-a1": "HELD 0.75", "C-a4": "HELD 0.85 (point-informed)", "C-b1": "HELD 0.80", "C-b2": "HELD 0.60, REVERSED 0.05",
        "C-M": "HELD 0.70"}

# hooks the selftest swaps (nothing else writes them)
_CLOCK = [time.perf_counter]


def _committed_sides():
    return G._committed_sides()


_SIDES = [_committed_sides]


def pool_check_v2(pool):
    """The B0-2 form (programme L22165; READY_g13_breakdown D-1), replacing pool_guard.py (which holds no pv2 pool), in this
    order: (1) every -wal / -journal of the DBs v2_union_pool reads absent or 0 bytes (checked here before the child opens them);
    (2) the engine pool file's sha256-lf = the pin (79d48f4b...); (3) tools/analysis/v2_union_pool.py --dry-run, rc 0, its first
    line "[UNION-POOL] pool <pool> recomputed ...; expected <pool>" and its line "... every check passed ...". -> (0, summary) or (1, the first failure); main REFUSES on 1."""
    c = cfg()
    side = []
    for db in c["guard_dbs"]:
        for suf in ("-wal", "-journal"):
            sp = db + suf
            if os.path.exists(sp) and os.path.getsize(sp) > 0:
                return 1, "%s is %d bytes (a writer is open on %s): a failed precondition" % (sp, os.path.getsize(sp), os.path.basename(db))
            side.append("%s%s %s" % (os.path.basename(db), suf, "0 bytes" if os.path.exists(sp) else "absent"))
    pf = P(_ROOT[0], c["pool_file"])
    if not os.path.isfile(pf):
        return 1, "engine pool file %s is missing" % pf
    got = sha256_lf(pf)
    if got != c["pool_file_sha256_lf"]:
        return 1, "engine pool file %s sha256-lf %s, not the pinned %s" % (pf, got, c["pool_file_sha256_lf"])
    pr = subprocess.run([sys.executable, os.path.join(HERE, "v2_union_pool.py"), "--dry-run", "--pool", pool] + list(c["guard_args"]),
                        capture_output=True, text=True, cwd=ROOT)
    lines = (pr.stdout or "").splitlines()
    if pr.returncode != 0:
        return 1, "v2_union_pool.py --dry-run rc %d: %s" % (pr.returncode, ((pr.stderr or "") + (pr.stdout or "")).strip()[-600:])
    want = "[UNION-POOL] pool %s recomputed" % pool
    if not lines or not lines[0].startswith(want) or not lines[0].endswith("expected %s" % pool):
        return 1, "v2_union_pool.py --dry-run first line is %r, not \"%s ...; expected %s\"" % (lines[0] if lines else "", want, pool)
    if not any("every check passed" in ln for ln in lines):
        return 1, "v2_union_pool.py --dry-run printed no \"every check passed\" line"
    return 0, "%s | %s | engine pool file sha256-lf %s (pinned) | %s" % (lines[0], [ln for ln in lines if "every check passed" in ln][0],
                                                                         got[:16], "; ".join(side))


_pool_guard_proc = pool_check_v2


_POOL_GUARD = [_pool_guard_proc]


# ── small helpers ───────────────────────────────────────────────────────────────────────────────────────────────────────

def src_of(name):
    return str(name).split("/", 1)[0]


def majority(labels, classes):
    """TRAIN-majority class index of `labels` (tie: the smaller class name); -1 (<empty>) when there is none."""
    labels = np.asarray(labels, dtype=int)
    if len(labels) == 0:
        return -1
    cnt = np.bincount(labels, minlength=len(classes))
    top = np.flatnonzero(cnt == cnt.max())
    return int(min(top, key=lambda c: classes[c]))


_LOAD_T0 = [0.0]


def timed(fn, *a, **k):
    t0 = _CLOCK[0]()
    r = fn(*a, **k)
    return r, _CLOCK[0]() - t0


def stat(diff, comp):
    """Paired mean with the G13 machinery: whole-component bootstrap (g13_comparator.boot), SE, DEFF, n_eff, MDE80, discordance."""
    diff = np.asarray(diff, dtype=np.float64)
    n = len(diff)
    if n == 0:
        return None
    groups = G.comp_groups(comp)
    lo, hi, se = G.boot(diff, groups)
    var_iid = float(diff.var(ddof=1)) / n if n > 1 else 0.0
    deff = se ** 2 / var_iid if var_iid > 0 else float("nan")
    return dict(d=float(diff.mean()), lo=lo, hi=hi, se=se, deff=deff, n=n, G=int(groups.max()) + 1,
                n_eff=n / deff if deff == deff and deff > 0 else float("nan"), mde=2.80 * se, disc=float(np.mean(diff != 0)))


def v_below(lo, hi):
    """C-a1 / C-a4: HELD iff the interval lies wholly below 0; FAILED iff wholly above 0."""
    if hi < 0:
        return "HELD"
    if lo > 0:
        return "FAILED"
    return "UNDETERMINED"


def v_above(lo, hi):
    """C-M: HELD iff wholly above 0; FAILED iff wholly below 0 (registrar's pre-data clause)."""
    if lo > 0:
        return "HELD"
    if hi < 0:
        return "FAILED"
    return "UNDETERMINED"


def v_spread(d, lo, hi, spread):
    """C-b2 / C-b1 (G13's form): HELD iff wholly above 0 AND d > spread; REVERSED iff wholly below 0 AND d < -spread."""
    if lo > 0 and d > spread:
        return "HELD"
    if hi < 0 and d < -spread:
        return "REVERSED"
    return "UNDETERMINED"


def spread_of(vals):
    vals = list(vals)
    return max(vals) - min(vals)


# ── loading the objects ─────────────────────────────────────────────────────────────────────────────────────────────────

def P(root, rel):
    return os.path.join(root, *rel.split("/"))


def last_snapshot(path):
    last = None
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                last = ln
    if last is None:
        refuse("%s is empty" % path)
    return json.loads(last)


def load_trees(root, dim):
    """I4 (structure) -> {uid: node} with union depth, parent uid, source, isLeaf, unit mu."""
    nodes = {}
    for mdir, source in cfg()["members"]:
        snap = last_snapshot(P(root, "%s/%s/seed_42/dag_snapshots.jsonl" % (cfg()["b0"], mdir)))
        ns = snap["nodes"]
        roots = [n for n in ns if not n["parentIds"]]
        if len(roots) != 1 or roots[0]["label"] != source:
            refuse("member %s: %d root(s) %s, not one root labelled %s" % (mdir, len(roots), [r["label"] for r in roots], source))
        for n in ns:
            if len(n["parentIds"]) > 1:
                refuse("node %s:%s has %d parents: the ancestor at a depth is ambiguous" % (source, n["id"], len(n["parentIds"])))
            mu = np.asarray(n["vmfMu"], dtype=np.float64)
            if len(mu) != dim:
                refuse("node %s:%s vmfMu has %d components, not %d" % (source, n["id"], len(mu), dim))
            nodes["%s:%s" % (source, n["id"])] = dict(uid="%s:%s" % (source, n["id"]), src=source, depth=int(n["depth"]) + 1,
                                                      parent=("%s:%s" % (source, n["parentIds"][0])) if n["parentIds"] else None,
                                                      leaf=bool(n["isLeaf"]), mu=mu / (np.linalg.norm(mu) or 1.0))
    for u, n in nodes.items():
        if n["parent"] is not None:
            if n["parent"] not in nodes:
                refuse("node %s's parent %s is not in its member snapshot" % (u, n["parent"]))
            if nodes[n["parent"]]["depth"] != n["depth"] - 1:
                refuse("node %s at union depth %d under a parent at depth %d" % (u, n["depth"], nodes[n["parent"]]["depth"]))
        elif n["depth"] != 1:
            refuse("corpus root %s is at union depth %d, not 1" % (u, n["depth"]))
    return nodes


def ancestors(nodes, uid):
    """{union depth: ancestor uid} from the corpus root (depth 1) down to uid itself."""
    chain, u, seen = {}, uid, set()
    while u is not None:
        if u in seen:
            refuse("cycle at %s" % u)
        seen.add(u)
        chain[nodes[u]["depth"]] = u
        u = nodes[u]["parent"]
    if 1 not in chain:
        refuse("node %s's ancestor chain does not reach a corpus root" % uid)
    return chain


def _modal_leaf(rs):
    """rp12_pairing P1's rule on leaf_id (ties to the smallest id; an unrouted row counts as <unrouted>)."""
    cells = Counter(r["leaf_id"] or RP.UNROUTED for r in rs)
    top = max(cells.values())
    return min(c for c, k in cells.items() if k == top)


def item_leaves(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["item_id"]].append(r)
    return {it: (_modal_leaf(rs), rs[0].get("leaf_depth")) for it, rs in by.items()}


def read_csv(path):
    import csv
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_objects(root):
    """Every object, I0 and I2-I5 checked (I1 needs the fits: identity_arms + check_i1). Refuses on any miss."""
    c = cfg()
    o = {"root": root, "paths": {}}
    stem = P(root, c["bundle"])
    b, meta = G.load_bundle(stem, expect=c["expect"], sides=_SIDES[0]() if _SIDES[0] else None)
    o["b"], o["meta"] = b, meta
    # I0 provenance + (d) inputs
    ptr = json.load(open(P(root, c["pointer"]), encoding="utf-8"))
    o["paths"]["pointer_sha256_lf"] = sha256_lf(P(root, c["pointer"]))
    man = {}
    for x in [m for m, _s in c["members"]] + list(c["grafts"]):
        mp = P(root, "%s/%s/seed_42/diagnostics/run_manifest.json" % (c["b0"], x))
        ent = ptr.get("entries", {}).get("B0/%s" % x)
        if ent is None or ent.get("manifest_sha256_lf") != sha256_lf(mp):
            refuse("I0: %s's LF sha256 %s is not the lane r2 pointer's %s" % (mp, sha256_lf(mp), (ent or {}).get("manifest_sha256_lf")))
        mj = json.load(open(mp, encoding="utf-8"))
        if not str(mj.get("commit", "")).startswith(c["commit"]):
            refuse("I0: %s was built at commit %s, not M %s" % (mp, mj.get("commit"), c["commit"]))
        lp = P(root, "%s/%s/seed_42/headless_run.log" % (c["b0"], x))
        if os.path.isfile(lp):
            with open(lp, encoding="utf-8", errors="replace") as f:
                tl = [ln.rstrip("\n") for ln in f if "TOTAL TIME" in ln]
            log = dict(sha256=sha256_bytes(lp), lines=tl,
                       ms=[int(re.sub(r"[^0-9]", "", ln.split(":", 1)[1].split("ms")[0])) for ln in tl])
        else:
            log = None
        man[x] = dict(ms=int(mj["duration_ms"]), log=log)
    o["man"] = man
    o["paths"]["bundle_npz_sha256"] = sha256_bytes(stem + ".npz")
    o["paths"]["bundle_json_sha256_lf"] = sha256_lf(stem + ".json")
    classes = [str(x) for x in b["classes"]]
    o["classes"] = classes
    o["Xe"], o["ye"] = FM.unit_rows(np.asarray(b["eval_X"], dtype=np.float64)), np.asarray(b["eval_y"], dtype=int)
    o["Xt"], o["yt"] = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64)), np.asarray(b["train_y"], dtype=int)
    o["comp"] = np.asarray(b["eval_comp"])
    o["fl"] = np.asarray(b["eval_fl"], dtype=np.int64)
    o["esrc"] = np.array([src_of(classes[i]) for i in o["ye"]])
    o["tsrc"] = np.array([src_of(classes[i]) for i in o["yt"]])
    eitems, titems = [str(x) for x in b["eval_item"]], [str(x) for x in b["train_item"]]
    n_e, n_t = len(eitems), len(titems)
    # I5 Support (a)
    if (n_e, len(set(o["comp"].tolist())), n_t) != (c["n_eval"], c["n_comp"], c["n_train"]):
        refuse("bundle holds EVAL %d / %d components / TRAIN %d, not Support (a)'s %d / %d / %d"
               % (n_e, len(set(o["comp"].tolist())), n_t, c["n_eval"], c["n_comp"], c["n_train"]))
    for s in c["sources"]:
        m = o["esrc"] == s
        got = (int(m.sum()), len(set(o["comp"][m].tolist())), int((o["tsrc"] == s).sum()))
        want = c["support_eval"][s] + (c["support_train"][s],)
        if got != want:
            refuse("source %s: EVAL %d / components %d / TRAIN %d, not Support (a)'s %d / %d / %d" % ((s,) + got + want))
    extra = sorted(set(o["esrc"].tolist()) - set(c["sources"]))
    if extra:
        refuse("EVAL items of unregistered source(s) %s" % extra)
    cross = defaultdict(set)
    for s, k in zip(o["esrc"].tolist(), o["comp"].tolist()):
        cross[k].add(s)
    o["cross_source_components"] = sum(1 for v in cross.values() if len(v) > 1)
    # trees (I4)
    nodes = load_trees(root, o["Xe"].shape[1])
    o["nodes"] = nodes
    leaves = sorted(u for u, n in nodes.items() if n["leaf"])
    o["leaves"] = leaves
    o["leaf_mu"] = np.vstack([nodes[u]["mu"] for u in leaves])
    o["anc"] = {u: ancestors(nodes, u) for u in leaves}
    by_src = Counter(nodes[u]["src"] for u in leaves)
    if dict(by_src) != dict(c["leaves_by_source"]) or len(leaves) != c["n_leaves"]:
        refuse("snapshot leaves per source %s (total %d), not the registered %s (%d)" % (dict(sorted(by_src.items())), len(leaves),
                                                                                       c["leaves_by_source"], c["n_leaves"]))
    # flatLeaf CSVs
    flv = P(root, c["fl_val"])
    for nm in (RP.QUERIES, RP.TRAIN, RP.LEAVES):
        o["paths"]["flatleaf " + nm] = sha256_lf(os.path.join(flv, nm))
    lrows = read_csv(os.path.join(flv, RP.LEAVES))
    leaf_dom = {}
    for r in lrows:
        u = r["leaf_id"]
        if u not in nodes or not nodes[u]["leaf"]:
            refuse("leaves CSV leaf_id %s is not a snapshot leaf" % u)
        if int(r["leaf_depth"]) != nodes[u]["depth"]:
            refuse("leaves CSV %s depth %s is not its union depth %d" % (u, r["leaf_depth"], nodes[u]["depth"]))
        leaf_dom[u] = r["leaf_dominant"] if int(r["profile_size"]) > 0 and r["leaf_dominant"] else EMPTY
    if set(leaf_dom) != set(leaves):
        refuse("leaves CSV covers %d leaves, the snapshots %d (sets differ by %d)" % (len(leaf_dom), len(leaves),
                                                                                     len(set(leaf_dom) ^ set(leaves))))
    o["leaf_dom"] = leaf_dom
    qrows, trows = RP.read_rows(os.path.join(flv, RP.QUERIES)), RP.read_rows(os.path.join(flv, RP.TRAIN))
    cells_q, _d1, _u1, multi_q = RP.item_cells(qrows)
    cells_t, _d2, _u2, multi_t = RP.item_cells(trows)
    ex = G.exclusions(meta)
    if set(multi_q) != set(ex["EVAL"]) | set(ex["GATE"]) or set(multi_t) != set(ex["TRAIN"]):
        refuse("MC-EXCLUDE: the CSVs' multi-class items (held-out %d, TRAIN %d) are not the bundle's lists (EVAL+GATE %d, TRAIN %d)"
               % (len(multi_q), len(multi_t), len(ex["EVAL"]) + len(ex["GATE"]), len(ex["TRAIN"])))
    o["mc"] = (len(ex["EVAL"]), len(ex["GATE"]), len(ex["TRAIN"]))
    lq, lt = item_leaves(qrows), item_leaves(trows)
    for r in qrows + trows:
        u = r["leaf_id"]
        if u and (u not in nodes or not nodes[u]["leaf"]):
            refuse("CSV leaf_id %s is not a snapshot leaf (I4)" % u)
        if u and int(r["leaf_depth"]) != nodes[u]["depth"]:
            refuse("CSV leaf_depth %s of %s is not its union depth %d (I4)" % (r["leaf_depth"], u, nodes[u]["depth"]))
    eleaf, tleaf = [], []
    for i, it in enumerate(eitems):
        if it not in lq or it not in cells_q:
            refuse("bundle EVAL item %s has no flatLeaf row" % it)
        u = lq[it][0]
        if u == RP.UNROUTED:
            refuse("bundle EVAL item %s is unrouted in the flatLeaf CSV" % it)
        cell, key, _n = cells_q[it]
        if key != classes[o["ye"][i]] or cell != leaf_dom[u]:
            refuse("EVAL item %s: CSV class %s / cell %s vs bundle class %s / leaf %s named %s" % (it, key, cell, classes[o["ye"][i]],
                                                                                              u, leaf_dom[u]))
        if int(cell == key) != int(o["fl"][i]):
            refuse("EVAL item %s: eval_fl %d disagrees with the CSV filing" % (it, o["fl"][i]))
        eleaf.append(u)
    for j, it in enumerate(titems):
        if it not in lt or it not in cells_t:
            refuse("bundle TRAIN item %s has no flatLeaf TRAIN row" % it)
        if cells_t[it][1] != classes[o["yt"][j]]:
            refuse("TRAIN item %s: CSV class %s vs bundle %s" % (it, cells_t[it][1], classes[o["yt"][j]]))
        u = lt[it][0]
        if u == RP.UNROUTED:
            refuse("bundle TRAIN item %s is unrouted in the flatLeaf TRAIN CSV" % it)
        tleaf.append(u)
    o["eleaf"], o["tleaf"] = eleaf, tleaf
    # I3
    li = {u: k for k, u in enumerate(leaves)}
    am = np.argmax(o["Xe"] @ o["leaf_mu"].T, axis=1)
    o["i3_miss"] = int(sum(1 for k, u in zip(am.tolist(), eleaf) if leaves[k] != u))
    if 1000 * o["i3_miss"] > n_e:
        refuse("I3: argmax cos(x, leaf vmfMu) differs from the CSV leaf on %d of %d EVAL items (> 0.1%%)" % (o["i3_miss"], n_e))
    o["eleaf_idx"] = np.array([li[u] for u in eleaf])
    # descent (I2)
    dev = P(root, c["de_val"])
    o["paths"]["descent " + RP.QUERIES] = sha256_lf(os.path.join(dev, RP.QUERIES))
    cells_d, _d3, _u3, multi_d = RP.item_cells(RP.read_rows(os.path.join(dev, RP.QUERIES)))
    dok = []
    for i, it in enumerate(eitems):
        if it not in cells_d:
            refuse("bundle EVAL item %s has no descent row%s" % (it, " (multi-class there)" if it in multi_d else ""))
        cell, key, _n = cells_d[it]
        if key != classes[o["ye"][i]]:
            refuse("EVAL item %s: descent class %s vs bundle %s" % (it, key, classes[o["ye"][i]]))
        dok.append(int(cell == key))
    o["desc"] = np.array(dok, dtype=np.int64)
    o["i2"] = "%.4f" % o["desc"].mean()
    if o["i2"] != c["i2"]:
        refuse("I2: P_descent on the %d bundle items is %s, not the recorded %s" % (n_e, o["i2"], c["i2"]))
    return o


# ── the arms ────────────────────────────────────────────────────────────────────────────────────────────────────────────

def kc_fit(Xt, yt, kc, seed):
    (Pm, owner), t = timed(G.kc_prototypes, Xt, yt, kc, seed)
    return Pm, owner, t


def ukm_fit(X, k, seed):
    r, t = timed(FM.spherical_kmeans, X, k, seed, max_iter=G.MAX_ITER)
    return r, t


def name_clusters(labels, k, y, classes):
    return np.array([majority(y[labels == j], classes) for j in range(k)], dtype=int)


def frontier_of(o, d):
    """F(d): the flatLeaf leaf's ancestor at depth d, or the leaf itself when it is shallower than d -> {leaf uid: node uid}."""
    return {u: (o["anc"][u][d] if o["nodes"][u]["depth"] >= d else u) for u in o["leaves"]}


def frontier_names(o, d):
    """{F(d) node: TRAIN-majority class index (-1 <empty>)} from the TRAIN items filed (flatLeaf) into its subtree."""
    fr = frontier_of(o, d)
    members = defaultdict(list)
    for j, u in enumerate(o["tleaf"]):
        members[fr[u]].append(o["yt"][j])
    fnodes = sorted(set(fr.values()))
    return fr, {v: majority(members.get(v, []), o["classes"]) for v in fnodes}


def kc_at_depth(o, d):
    """k_c(d) = max(1, #F(d) nodes whose TRAIN majority is c) (g13_comparator.k_per_class on the F(d) names)."""
    _fr, names = frontier_names(o, d)
    return G.k_per_class(o["classes"], o["yt"], [o["classes"][v] for v in names.values() if v >= 0])


def margins(S, names):
    """Class margin: cos to the best cell minus cos to the best cell named with a different class (+inf if none)."""
    best = np.argmax(S, axis=1)
    bc = S[np.arange(len(S)), best]
    other = np.where(names[None, :] != names[best][:, None], S, -np.inf)
    return bc - other.max(axis=1)


def kept_precision(margin, correct, c):
    k = len(margin) * c // 100
    order = np.argsort(-margin, kind="stable")
    return float(np.asarray(correct)[order[:k]].mean()) if k else float("nan"), k


def selective(o, arms, cov=(50, 60, 70, 80, 90, 100)):
    groups = G.comp_groups(o["comp"])
    curve = {m: {c: kept_precision(arms[m][0], arms[m][1], c) for c in cov} for m in arms}
    members = FM.group_members(groups)
    rng = np.random.default_rng(BOOT_SEED)
    reps = {m: [] for m in arms}
    for _ in range(BOOT_B):
        idx = FM.twin_boot_indices(groups, rng, members)
        for m in arms:
            reps[m].append(kept_precision(arms[m][0][idx], arms[m][1][idx], 80)[0])
    reps = {m: np.array(v) for m, v in reps.items()}

    def ci(v):
        bs = sorted(float(x) for x in v)
        return bs[int(0.025 * BOOT_B)], bs[int(0.975 * BOOT_B) - 1]
    out = {"curve": curve, "ci": {m: ci(reps[m]) for m in arms}}
    out["diff"] = {m: (curve["tree"][80][0] - curve[m][80][0], ci(reps["tree"] - reps[m])) for m in arms if m != "tree"}
    return out


def identity_arms(o):
    """I1 arms (KC_s, U-global_s, NCC, P_fl, D13) -> dict; check_i1 REFUSES on a miss before anything new is computed."""
    classes, Xt, yt, Xe, ye = o["classes"], o["Xt"], o["yt"], o["Xe"], o["ye"]
    kc = G.k_per_class(classes, yt, [str(x) for x in o["b"]["leaf_major"]])
    r = {"kc": kc, "kc_P": {}, "kc_ok": {}, "t_kc": {}, "ug": {}, "ug_ok": {}, "t_ug": {}}
    for s in SEEDS:
        Pm, owner, t = kc_fit(Xt, yt, kc, s)
        r["kc_P"][s], r["t_kc"][s] = (Pm, owner), t
        r["kc_ok"][s] = (G.file_nearest(Xe, Pm, owner) == ye).astype(np.int64)
    L = len(o["b"]["leaf_major"])
    r["L"] = L
    for s in SEEDS:
        fit, t = ukm_fit(Xt, L, s)
        lab = name_clusters(fit["labels"], L, yt, classes)
        r["ug"][s], r["t_ug"][s] = (fit["centers"], lab), t
        r["ug_ok"][s] = (lab[np.argmax(Xe @ fit["centers"].T, axis=1)] == ye).astype(np.int64)
    r["ncc_ok"] = G.ncc_correct(Xt, yt, Xe, ye)
    diff = o["fl"] - r["kc_ok"][0]
    r["d13"] = stat(diff, o["comp"])
    r["i1_got"] = dict(p_fl="%.4f" % o["fl"].mean(), p_kc=tuple("%.4f" % r["kc_ok"][s].mean() for s in SEEDS),
                       d13="%+.4f" % r["d13"]["d"], lo="%+.4f" % r["d13"]["lo"], hi="%+.4f" % r["d13"]["hi"],
                       ukm=tuple("%.4f" % r["ug_ok"][s].mean() for s in SEEDS), ncc="%.4f" % r["ncc_ok"].mean())
    return r


def check_i1(r):
    """I1: G13's recorded numbers reproduced to the printed digits; REFUSES on any miss."""
    got = r["i1_got"]
    want = dict(cfg()["i1"])
    for k in ("d13", "lo", "hi"):
        want[k] = "%+.4f" % float(want[k])
    want["p_kc"], want["ukm"] = tuple(want["p_kc"]), tuple(want["ukm"])
    bad = [k for k in want if got[k] != want[k]]
    if bad:
        refuse("I1: %s reproduced as %s, recorded %s" % (bad, [got[k] for k in bad], [want[k] for k in bad]))
    return r


def compute(o, ident, timing12=None):
    """Every readout (A1-A4, B1-B2, C, D, E, M) on loaded objects whose identity passed."""
    c = cfg()
    classes, Xt, yt, Xe, ye, comp, fl = o["classes"], o["Xt"], o["yt"], o["Xe"], o["ye"], o["comp"], o["fl"]
    n = len(ye)
    R = {"n": n, "G": len(set(comp.tolist())), "ident": ident}
    kc0 = ident["kc_ok"][0]
    p_kc = {s: float(ident["kc_ok"][s].mean()) for s in SEEDS}
    R["p_fl"], R["p_kc"], R["spread_kc"] = float(fl.mean()), p_kc, spread_of(p_kc.values())
    R["d13"] = ident["d13"]
    # A1 per source
    R["A1"] = {}
    for s in c["sources"]:
        m = o["esrc"] == s
        st = stat(fl[m] - kc0[m], comp[m])
        if st is not None:
            st["share"] = (st["n"] * st["d"]) / (n * R["d13"]["d"]) if R["d13"]["d"] != 0 else float("nan")
            st["p_fl"], st["p_kc"] = float(fl[m].mean()), float(kc0[m].mean())
        R["A1"][s] = st
    tot = sum(st["n"] * st["d"] for st in R["A1"].values() if st is not None)
    if abs(tot - n * R["d13"]["d"]) > 1e-9:
        refuse("A1: the strata's n_s D13_s sum to %.6f, not n D13 = %.6f (shares must sum to 1 by construction)" % (tot, n * R["d13"]["d"]))
    # A2 stagewise
    P0, own0 = ident["kc_P"][0]
    kc_pred = own0[np.argmax(Xe @ P0.T, axis=1)]
    true_src = o["esrc"]
    tree_src = np.array([src_of(o["leaf_dom"][u]) for u in o["eleaf"]])
    kc_src = np.array([src_of(classes[k]) for k in kc_pred])
    st_tree, st_kc = (tree_src == true_src).astype(np.int64), (kc_src == true_src).astype(np.int64)
    both = (st_tree == 1) & (st_kc == 1)
    R["A2"] = dict(src_tree=float(st_tree.mean()), src_kc=float(st_kc.mean()), d_src=stat(st_tree - st_kc, comp),
                   n_both=int(both.sum()), within_tree=float(fl[both].mean()) if both.any() else float("nan"),
                   within_kc=float(kc0[both].mean()) if both.any() else float("nan"), d_within=stat(fl[both] - kc0[both], comp[both]))
    # A3 depth curve
    R["A3"] = {"d1_tree_src": float(np.mean([o["nodes"][o["anc"][u][1]]["src"] == s for u, s in zip(o["eleaf"], true_src)]))}
    R["A3"]["d1_kc_src"] = float(st_kc.mean())
    curve = {}
    for d in c["depths"]:
        fr, names = frontier_names(o, d)
        tree_ok = np.array([int(names[fr[u]] == ye[i]) for i, u in enumerate(o["eleaf"])], dtype=np.int64)
        kcd = kc_at_depth(o, d)
        oks, ts = {}, {}
        for s in SEEDS:
            Pm, owner, t = kc_fit(Xt, yt, kcd, s)
            oks[s], ts[s] = (G.file_nearest(Xe, Pm, owner) == ye).astype(np.int64), t
        if d == 2:
            if any(k != 1 for k in kcd.values()):
                refuse("A3: k_c(2) is not 1 for every class (%s): KC(2) = NCC cannot hold as registered"
                       % {classes[k]: v for k, v in kcd.items() if v != 1})
            for s in SEEDS:
                if not np.array_equal(oks[s], ident["ncc_ok"]):
                    refuse("A3: KC(2)_%d differs from NCC on %d items (registered: KC(2) = NCC exactly)" % (s, int((oks[s] != ident["ncc_ok"]).sum())))
            R["tree2_ok"] = tree_ok
        curve[d] = dict(n_nodes=len(names), n_empty=sum(1 for v in names.values() if v < 0), p_tree=float(tree_ok.mean()),
                        p_kcd={s: float(oks[s].mean()) for s in SEEDS}, st=stat(tree_ok - oks[0], comp),
                        kc_total=sum(kcd.values()))
    R["A3"]["curve"] = curve
    _fr_all, names_all = frontier_names(o, max(o["nodes"][u]["depth"] for u in o["leaves"]))
    R["A3"]["leaf_naming_differs"] = sum(1 for u in o["leaves"]
                                         if (classes[names_all[u]] if names_all[u] >= 0 else EMPTY) != o["leaf_dom"][u])
    strata = {}
    ldep = np.array([o["nodes"][u]["depth"] for u in o["eleaf"]])
    for lo_, hi_ in c["leaf_strata"]:
        m = (ldep >= lo_) & (ldep <= hi_)
        strata[(lo_, hi_)] = stat(fl[m] - kc0[m], comp[m])
    R["A3"]["strata"] = strata
    # A4
    R["A4"] = stat((fl - kc0) - (R["tree2_ok"] - ident["ncc_ok"]), comp)
    # B1 U-global
    ug_ok = ident["ug_ok"]
    R["p_ug"] = {s: float(ug_ok[s].mean()) for s in SEEDS}
    R["spread_ug"] = spread_of(R["p_ug"].values())
    R["B1"] = stat(fl - ug_ok[0], comp)
    # B2 U-source
    ksrc = {s: c["leaves_by_source"][s] for s in c["sources"]}
    us_ok, us_in_ok, t_us, us_fit0 = {}, {}, {}, None
    for s in SEEDS:
        cents, labs, srcs, tsum = [], [], [], 0.0
        for so in c["sources"]:
            m = o["tsrc"] == so
            if ksrc[so] > int(m.sum()):
                refuse("U-source %s: k %d exceeds its %d TRAIN items" % (so, ksrc[so], int(m.sum())))
            fit, t = ukm_fit(Xt[m], ksrc[so], s)
            tsum += t
            cents.append(fit["centers"])
            labs.append(name_clusters(fit["labels"], ksrc[so], yt[m], classes))
            srcs.extend([so] * ksrc[so])
        C_, lab_, srcs = np.vstack(cents), np.concatenate(labs), np.array(srcs)
        S = Xe @ C_.T
        us_ok[s] = (lab_[np.argmax(S, axis=1)] == ye).astype(np.int64)
        Sin = np.where(srcs[None, :] == o["esrc"][:, None], S, -np.inf)
        us_in_ok[s] = (lab_[np.argmax(Sin, axis=1)] == ye).astype(np.int64)
        t_us[s] = tsum
    R["p_us"] = {s: float(us_ok[s].mean()) for s in SEEDS}
    R["p_us_in"] = {s: float(us_in_ok[s].mean()) for s in SEEDS}
    R["spread_us"] = spread_of(R["p_us"].values())
    R["B2"] = stat(fl - us_ok[0], comp)
    R["ksrc"] = ksrc
    # C filing rule
    R["p_desc"] = float(o["desc"].mean())
    R["C"] = dict(d13_desc=stat(o["desc"] - kc0, comp), du_desc=stat(o["desc"] - ug_ok[0], comp), by_source={})
    for so in c["sources"]:
        m = o["esrc"] == so
        R["C"]["by_source"][so] = (stat(o["desc"][m] - kc0[m], comp[m]), stat(o["desc"][m] - ug_ok[0][m], comp[m]))
    srcs_sorted = sorted(set(o["tsrc"].tolist()))
    SC = FM.unit_rows(np.vstack([Xt[o["tsrc"] == so].sum(axis=0) for so in srcs_sorted]))
    hat = np.array(srcs_sorted)[np.argmax(Xe @ SC.T, axis=1)]
    psrc = np.array([src_of(classes[k]) for k in own0])
    Sk = np.where(psrc[None, :] == hat[:, None], Xe @ P0.T, -np.inf)
    kcdesc_ok = (own0[np.argmax(Sk, axis=1)] == ye).astype(np.int64)
    R["C"]["kc_desc"] = stat(kcdesc_ok - kc0, comp)
    R["C"]["p_kc_desc"] = float(kcdesc_ok.mean())
    # M mechanism
    rel_ok, kept = {}, {}
    for s in SEEDS:
        Pm, owner = ident["kc_P"][s]
        near = np.argmax(Xt @ Pm.T, axis=1)
        new = owner.copy()
        k0 = 0
        for j in range(len(owner)):
            mj = majority(yt[near == j], classes)
            if mj < 0:
                k0 += 1
            else:
                new[j] = mj
        rel_ok[s] = (new[np.argmax(Xe @ Pm.T, axis=1)] == ye).astype(np.int64)
        kept[s] = k0
    R["M"] = dict(g_own=stat(kc0 - rel_ok[0], comp), fl_rel=stat(fl - rel_ok[0], comp),
                  p_rel={s: float(rel_ok[s].mean()) for s in SEEDS}, kept=kept)
    # E selective
    names_leaf = np.array([o["leaf_dom"][u] for u in o["leaves"]])
    Cu, labu = ident["ug"][0]
    arms = {"tree": (margins(Xe @ o["leaf_mu"].T, names_leaf), fl),
            "KC_0": (margins(Xe @ P0.T, own0), kc0),
            "U-global_0": (margins(Xe @ Cu.T, labu), ug_ok[0])}
    R["E"] = selective(o, arms)
    # ladder
    R["knn"] = float(G.knn_correct(Xt, yt, Xe, ye, classes).mean())
    R["p_ncc"] = float(ident["ncc_ok"].mean())
    # D timing
    R["D"] = dict(kc=dict(ident["t_kc"]), ug=dict(ident["t_ug"]), us=t_us, t12=timing12, man=o["man"])
    return R


# ── (d) timing child, machine state ─────────────────────────────────────────────────────────────────────────────────────

def time_worker(stem, spec_path):
    """The 12-thread column: the same fits in this child process (thread variables set before numpy); prints one JSON line."""
    b, _m = G.load_bundle(stem, expect=None)
    Xt, yt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64)), np.asarray(b["train_y"], dtype=int)
    spec = json.load(open(spec_path, encoding="utf-8"))
    classes = [str(x) for x in b["classes"]]
    tsrc = np.array([src_of(classes[i]) for i in yt])
    kc = {int(k): v for k, v in spec["kc"].items()}
    out = {"threads": _THREADS, "blas": blas_threads(), "kc": [], "ug": [], "us": []}
    for s in spec["seeds"]:
        out["kc"].append(kc_fit(Xt, yt, kc, s)[2])
        out["ug"].append(ukm_fit(Xt, spec["L"], s)[1])
        out["us"].append(sum(ukm_fit(Xt[tsrc == so], k, s)[1] for so, k in spec["ksrc"]))
    print("TIMING12 " + json.dumps(out))
    return 0


def blas_threads():
    """The BLAS pool size actually in force in this process (threadpoolctl), or "unknown"."""
    try:
        from threadpoolctl import threadpool_info
        info = [d.get("num_threads") for d in threadpool_info() if d.get("user_api") == "blas"]
        return ",".join(str(x) for x in info) if info else "none"
    except Exception:
        return "unknown"


def _timing12_proc(stem, spec):
    import tempfile
    fd, sp = tempfile.mkstemp(suffix=".json", prefix="g13b_spec_")
    with os.fdopen(fd, "w") as f:
        json.dump(spec, f)
    try:
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--time-worker", "--threads", "12", "--bundle", stem,
                            "--spec", sp], capture_output=True, text=True)
    finally:
        os.remove(sp)
    for ln in p.stdout.splitlines():
        if ln.startswith("TIMING12 "):
            return json.loads(ln[len("TIMING12 "):])
    return {"error": "rc %d: %s" % (p.returncode, (p.stderr or p.stdout)[-300:])}


_TIMING12 = [_timing12_proc]


def _machine_state():
    free = None
    try:
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong), ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
        ms = MS()
        ms.dwLength = ctypes.sizeof(MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
            free = ms.ullAvailPhys / 2 ** 30
    except Exception:
        free = None
    pids = []
    try:
        p = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True)
        for ln in p.stdout.splitlines():
            f = [x.strip('"') for x in ln.split('","')]
            if f and f[0].lower().startswith(("java", "python", "ollama")):
                pids.append("%s:%s" % (f[0], f[1]))
    except Exception:
        pids = ["<tasklist unavailable>"]
    return {"free_ram_gb": free, "pids": pids, "blas": blas_threads()}


_MACHINE = [_machine_state]


# ── rendering ───────────────────────────────────────────────────────────────────────────────────────────────────────────

def fs(st):
    if st is None:
        return "n = 0: no EVAL item, no estimate"
    return "%+.4f  95%% [%+.4f, %+.4f] (n %d, %d components; SE %.5f, DEFF %.3f, n_eff %.0f, MDE80 %.4f, discordance %.4f)" % (
        st["d"], st["lo"], st["hi"], st["n"], st["G"], st["se"], st["deff"], st["n_eff"], st["mde"], st["disc"])


def support_line(key, st):
    if key not in SUPPORT_REG:
        return ("  support %s: SE %.5f; DEFF %.3f; n_eff %.0f; MDE80 %.4f; discordance %.4f (no registered Support figure: a seen point,"
                " its spread clause decides beside the interval)" % (key, st["se"], st["deff"], st["n_eff"], st["mde"], st["disc"]))
    se_r, mde_r, disc_r = SUPPORT_REG[key]
    return ("  support %s: SE %.5f (registered %.5f); DEFF %.3f (registered 1.214); n_eff %.0f; MDE80 %.4f (registered %.4f);"
            " discordance %.4f (planning %.2f)" % (key, st["se"], se_r, st["deff"], st["n_eff"], st["mde"], mde_r, st["disc"], disc_r))


def pred_line(label, obs):
    pt, band = PRED[label]
    head = ("%s %+.3f [%+.3f, %+.3f]" % (label, pt, band[0], band[1])) if pt is not None else ("%s [%g, %g]" % (label, band[0], band[1]))
    if obs is None or obs != obs:
        return "PREDICTION %s: observed none -> NOT SCORED (no estimate)" % head
    return "PREDICTION %s: observed %+.4f -> %s" % (head, obs, G.in_band(obs, band))


def verdict_lines(R):
    """The five criteria and the two falsifiers, each branch printed (the selftest executes every one)."""
    o = []
    a1 = R["A1"][cfg()["scoreable"]]
    if a1 is None:
        o.append("C-a1: UNDETERMINED: no %s EVAL item" % cfg()["scoreable"])
        v1 = "UNDETERMINED"
    else:
        v1 = v_below(a1["lo"], a1["hi"])
        if v1 == "HELD":
            o.append("C-a1: HELD (the tree loses on %s): D13_MMLU %+.4f, interval [%+.4f, %+.4f] wholly below 0"
                     % (cfg()["scoreable"], a1["d"], a1["lo"], a1["hi"]))
        elif v1 == "FAILED":
            o.append("C-a1: FAILED: D13_MMLU %+.4f, interval [%+.4f, %+.4f] wholly above 0" % (a1["d"], a1["lo"], a1["hi"]))
        else:
            o.append("C-a1: UNDETERMINED: D13_MMLU %+.4f, interval [%+.4f, %+.4f] contains 0 (neither a loss nor parity is shown)"
                     % (a1["d"], a1["lo"], a1["hi"]))
        o.append(support_line("C-a1", a1))
    a4 = R["A4"]
    v4 = v_below(a4["lo"], a4["hi"])
    seen = "point seen before registration (domain_ok P_fl 0.8042, NCC 0.8065 printed in g13_outcome.txt blob:ff8fa439)"
    if v4 == "HELD":
        o.append("C-a4: HELD (the loss opens below the anchors): Delta %+.4f, interval [%+.4f, %+.4f] wholly below 0; %s"
                 % (a4["d"], a4["lo"], a4["hi"], seen))
    elif v4 == "FAILED":
        o.append("C-a4: FAILED: Delta %+.4f, interval [%+.4f, %+.4f] wholly above 0; %s" % (a4["d"], a4["lo"], a4["hi"], seen))
    else:
        o.append("C-a4: UNDETERMINED: Delta %+.4f, interval [%+.4f, %+.4f] contains 0; %s" % (a4["d"], a4["lo"], a4["hi"], seen))
    o.append(support_line("C-a4", a4))
    b2 = R["B2"]
    vb2 = v_spread(b2["d"], b2["lo"], b2["hi"], R["spread_us"])
    if vb2 == "HELD":
        o.append("C-b2: HELD (the tree beats source-aware unsupervised k-means): D_Us %+.4f, interval [%+.4f, %+.4f] wholly above 0"
                 " AND D_Us > spread_US %.4f" % (b2["d"], b2["lo"], b2["hi"], R["spread_us"]))
    elif vb2 == "REVERSED":
        o.append("C-b2: REVERSED (its FAILED): D_Us %+.4f, interval [%+.4f, %+.4f] wholly below 0 AND D_Us < -spread_US %.4f"
                 % (b2["d"], b2["lo"], b2["hi"], -R["spread_us"]))
    else:
        o.append("C-b2: UNDETERMINED: D_Us %+.4f, interval [%+.4f, %+.4f], spread_US %.4f%s" % (
            b2["d"], b2["lo"], b2["hi"], R["spread_us"], " (UNDETERMINED by spread: spread_US exceeds 0.040)" if R["spread_us"] > 0.040 else ""))
    o.append(support_line("C-b2", b2))
    b1 = R["B1"]
    vb1 = v_spread(b1["d"], b1["lo"], b1["hi"], R["spread_ug"])
    seen1 = "point seen before registration (U-global seeds 0.7159-0.7573, seed 0 0.7381, printed in g13_outcome.txt blob:ff8fa439)"
    if vb1 == "HELD":
        o.append("C-b1: HELD: D_U %+.4f, interval [%+.4f, %+.4f] wholly above 0 AND D_U > spread_U %.4f; %s"
                 % (b1["d"], b1["lo"], b1["hi"], R["spread_ug"], seen1))
    elif vb1 == "REVERSED":
        o.append("C-b1: REVERSED (its FAILED): D_U %+.4f, interval [%+.4f, %+.4f] wholly below 0 AND D_U < -spread_U %.4f; %s"
                 % (b1["d"], b1["lo"], b1["hi"], -R["spread_ug"], seen1))
    else:
        o.append("C-b1: UNDETERMINED: D_U %+.4f, interval [%+.4f, %+.4f], spread_U %.4f; %s" % (b1["d"], b1["lo"], b1["hi"],
                                                                                              R["spread_ug"], seen1))
    o.append(support_line("C-b1", b1))
    gm = R["M"]["g_own"]
    vm = v_above(gm["lo"], gm["hi"])
    if vm == "HELD":
        o.append("C-M: HELD (KC's edge is label ownership): G_own %+.4f, interval [%+.4f, %+.4f] wholly above 0" % (gm["d"], gm["lo"], gm["hi"]))
    elif vm == "FAILED":
        o.append("C-M: FAILED: G_own %+.4f, interval [%+.4f, %+.4f] wholly below 0" % (gm["d"], gm["lo"], gm["hi"]))
    else:
        o.append("C-M: UNDETERMINED: G_own %+.4f, interval [%+.4f, %+.4f] contains 0" % (gm["d"], gm["lo"], gm["hi"]))
    o.append(support_line("C-M", gm))
    o.append("No UNDETERMINED or FAILED is read as parity (no TOST registered).")
    o.append("F-GB (fires iff C-b2 REVERSED): %s" % ("FIRES: the anchored tree files worse than source-aware label-free k-means at"
                                                     " matched counts" if vb2 == "REVERSED" else "does not fire (C-b2 %s)" % vb2))
    o.append("F-GB2 (fires iff C-a4 FAILED): %s" % ("FIRES: the loss sits at the anchors, not below them" if v4 == "FAILED"
                                                    else "does not fire (C-a4 %s)" % v4))
    for k, v in (("C-a1", v1), ("C-a4", v4), ("C-b1", vb1), ("C-b2", vb2), ("C-M", vm)):
        o.append("PREDICTION %s verdict probabilities (%s): observed %s" % (k, PROB[k], v))
    return o, dict(C_a1=v1, C_a4=v4, C_b2=vb2, C_b1=vb1, C_M=vm)


def render(R, o):
    c = cfg()
    L = []
    say = L.append
    say("%s G13-BREAKDOWN (lane r2; registration ffed1d52 L22887-L23048). ZERO calls; no build." % TAG)
    say("%s union EVAL %d items in %d CK-CLOSE components (after MC-EXCLUDE: EVAL %d, GATE %d, TRAIN %d excluded, as in G13);"
        " TRAIN %d; components crossing sources %d" % (TAG, R["n"], R["G"], o["mc"][0], o["mc"][1], o["mc"][2], len(o["yt"]),
                                                       o["cross_source_components"]))
    say("%s I0-I5 PASSED: I1 %s; I2 P_descent %s; I3 misses %d of %d; I4 %d leaves, depth <= %d"
        % (TAG, json.dumps(R["ident"]["i1_got"], sort_keys=True), o["i2"], o["i3_miss"], R["n"], len(o["leaves"]),
           max(o["nodes"][u]["depth"] for u in o["leaves"])))
    say("")
    say("== (a) A1 PER SOURCE: D13_s = P_fl,s - P(KC_0),s (stratum components); share = n_s D13_s / (n D13), D13 = %+.4f" % R["d13"]["d"])
    shares = 0.0
    for s in c["sources"]:
        st = R["A1"][s]
        tagw = "SCOREABLE (C-a1)" if s == c["scoreable"] else "DESCRIPTIVE-ONLY"
        if st is None:
            say("  %-12s %s: %s" % (s, tagw, fs(st)))
            continue
        shares += st["share"]
        say("  %-12s %s: P_fl %.4f, P(KC_0) %.4f, D13_s %s; share %.4f" % (s, tagw, st["p_fl"], st["p_kc"], fs(st), st["share"]))
    say("  shares sum to %.4f" % shares)
    a2 = R["A2"]
    say("== A2 STAGEWISE (DESCRIPTIVE-ONLY): source accuracy tree %.4f, KC_0 %.4f; D_src %s" % (a2["src_tree"], a2["src_kc"], fs(a2["d_src"])))
    say("  within-source class accuracy on the %d items BOTH file to the true source: tree %.4f, KC_0 %.4f; D_within %s"
        % (a2["n_both"], a2["within_tree"], a2["within_kc"], fs(a2["d_within"])))
    a3 = R["A3"]
    say("== A3 DEPTH CURVE (DESCRIPTIVE-ONLY): d = 1 source accuracy only: tree %.4f, KC_0 %.4f" % (a3["d1_tree_src"], a3["d1_kc_src"]))
    for d, cv in sorted(a3["curve"].items()):
        say("  d = %d: |F(d)| %d (%d <empty>), sum k_c(d) %d; P_tree(d) %.4f; P(KC(d)_s) %s; D(d) %s" % (
            d, cv["n_nodes"], cv["n_empty"], cv["kc_total"], cv["p_tree"], " / ".join("%.4f" % cv["p_kcd"][s] for s in SEEDS),
            fs(cv["st"])))
    say("  KC(2) = NCC exactly: asserted on every seed (P_NCC %.4f); leaves whose subtree TRAIN majority differs from the leaves"
        " CSV leaf_dominant: %d" % (R["p_ncc"], a3["leaf_naming_differs"]))
    for (lo_, hi_), st in sorted(a3["strata"].items()):
        say("  D13 at flatLeaf-leaf depth %s: %s" % ("%d" % lo_ if lo_ == hi_ else ">= %d" % lo_, fs(st)))
    say("== A4 Delta = D13 - [P_tree(2) - P_NCC] (paired): %s" % fs(R["A4"]))
    say("")
    say("== (b) B1 U-global (k = %d, TRAIN-majority naming): P(U_s) %s; spread_U %.4f; D_U = P_fl - P(U_0) %s"
        % (R["ident"]["L"], " / ".join("%.4f" % R["p_ug"][s] for s in SEEDS), R["spread_ug"], fs(R["B1"])))
    say("== B2 U-source (k per source %s): P(US_s) %s; spread_US %.4f; D_Us = P_fl - P(US_0) %s" % (
        ", ".join("%s %d" % (s, R["ksrc"][s]) for s in c["sources"]), " / ".join("%.4f" % R["p_us"][s] for s in SEEDS),
        R["spread_us"], fs(R["B2"])))
    say("  printed beside (UNION-AF-ROUTE K_s form, EVAL filed within its TRUE source; never deciding): %s"
        % " / ".join("%.4f" % R["p_us_in"][s] for s in SEEDS))
    say("== LABEL LADDER (points; seeds 0-4; spread)")
    rows = [("U-global", "TRAIN labels at naming only", R["p_ug"]), ("U-source", "TRAIN source in the partition, labels at naming", R["p_us"]),
            ("tree flatLeaf", "GT-seeded anchors + TRAIN naming", None), ("NCC", "TRAIN class of every member", None),
            ("KC", "TRAIN class of every prototype", R["p_kc"]), ("kNN-15", "TRAIN class of every neighbour", None)]
    for nm, lab, ps in rows:
        pt = {"tree flatLeaf": R["p_fl"], "NCC": R["p_ncc"], "kNN-15": R["knn"]}.get(nm)
        if ps is not None:
            say("  %-14s %.4f  seeds %s  spread %.4f   reads: %s" % (nm, ps[0], " / ".join("%.4f" % ps[s] for s in SEEDS), spread_of(ps.values()), lab))
        else:
            say("  %-14s %.4f  (deterministic)                   reads: %s" % (nm, pt, lab))
    say("")
    cc = R["C"]
    say("== (c) FILING RULE (DESCRIPTIVE-ONLY): P_descent %.4f; D13_desc = P_descent - P(KC_0) %s" % (R["p_desc"], fs(cc["d13_desc"])))
    say("  D_U,desc = P_descent - P(U_0) %s" % fs(cc["du_desc"]))
    for s in c["sources"]:
        a, b_ = cc["by_source"][s]
        say("  %-12s D13_desc %s | D_U,desc %s" % (s, fs(a), fs(b_)))
    say("  KC-descent (nearest TRAIN source centroid, then nearest KC_0 prototype within it): P %.4f; P(KC-desc) - P(KC_0) %s"
        % (cc["p_kc_desc"], fs(cc["kc_desc"])))
    say("")
    m = R["M"]
    say("== (M) MECHANISM: KC-relabel_s P %s (prototypes with no TRAIN item keep their class: %s)" % (
        " / ".join("%.4f" % m["p_rel"][s] for s in SEEDS), " / ".join("%d" % m["kept"][s] for s in SEEDS)))
    say("  G_own = P(KC_0) - P(KC-relabel_0) %s" % fs(m["g_own"]))
    say("  P_fl - P(KC-relabel_0) %s" % fs(m["fl_rel"]))
    say("")
    D = R["D"]
    say("== (d) WALL-CLOCK (DESCRIPTIVE ONLY: no criterion; different languages, threads and scope)")
    msum = sum(D["man"][x]["ms"] for x, _s in c["members"]) / 1000.0
    loop = []
    for x in [mm for mm, _s in c["members"]] + list(c["grafts"]):
        mm = D["man"][x]
        if mm["log"] is None:
            say("  %-15s manifest duration_ms %d; headless_run.log ABSENT (no TOTAL TIME line copied)" % (x, mm["ms"]))
        else:
            say("  %-15s manifest duration_ms %d; log sha256 %s; TOTAL TIME lines: %s" % (x, mm["ms"], mm["log"]["sha256"],
                                                                                     " | ".join(l.strip() for l in mm["log"]["lines"])))
            if x not in c["grafts"] and mm["log"]["ms"]:
                loop.append(mm["log"]["ms"][0])
    say("  objects load (bundle, CSVs, snapshots) %.3f s: outside every fit time" % o.get("t_load", float("nan")))
    say("  tree members' manifest sum %.1f s; engine loop sum (first TOTAL TIME per member log) %s; grafts flatLeaf %.1f s / descent %.1f s"
        % (msum, ("%.1f s" % (sum(loop) / 1000.0)) if len(loop) == len(c["members"]) else "INCOMPLETE (%d of %d logs)" % (len(loop), len(c["members"])),
           D["man"]["graft_flatleaf"]["ms"] / 1000.0, D["man"]["graft_descent"]["ms"] / 1000.0))
    med = {}
    for k, nm in (("kc", "KC (all classes)"), ("ug", "U-global"), ("us", "U-source (six fits)")):
        v = [D[k][s] for s in SEEDS]
        med[k] = float(np.median(v))
        say("  k-means fit, 1 thread, %-20s seconds %s; median %.3f, max %.3f" % (nm, " / ".join("%.3f" % x for x in v), med[k], max(v)))
    t12 = D["t12"]
    if not t12 or "error" in t12:
        say("  k-means fit, 12 threads: NOT MEASURED (%s)" % ((t12 or {}).get("error", "no child run")))
    else:
        for k, nm in (("kc", "KC (all classes)"), ("ug", "U-global"), ("us", "U-source (six fits)")):
            v = t12[k]
            say("  k-means fit, %s threads (BLAS %s), %-17s seconds %s; median %.3f, max %.3f" % (t12["threads"], t12.get("blas", "?"), nm, " / ".join("%.3f" % x for x in v),
                                                                                    float(np.median(v)), max(v)))
    ms = D.get("machine") or {}
    say("  machine state: free RAM %s; admitted PIDs %s; BLAS threads in this process %s" % (
        ("%.1f GB" % ms["free_ram_gb"]) if ms.get("free_ram_gb") is not None else "unknown", ms.get("pids"), ms.get("blas", "unknown")))
    e2e = msum + D["man"]["graft_flatleaf"]["ms"] / 1000.0
    ratio = e2e / med["kc"] if med["kc"] > 0 else float("nan")
    say("  tree end-to-end (members + flatLeaf graft) %.1f s / KC median %.3f s = %.1fx; members only %.1fx" % (
        e2e, med["kc"], ratio, msum / med["kc"] if med["kc"] > 0 else float("nan")))
    R["_d_obs"] = (med["kc"], med["ug"], ratio, msum, sum(loop) / 1000.0 if loop else float("nan"))
    say("")
    E = R["E"]
    say("== (e) SELECTIVE FILING (DESCRIPTIVE ONLY; never paired, never deciding): each method's own top c% by class margin")
    for mname in ("tree", "KC_0", "U-global_0"):
        say("  %-11s %s" % (mname, "  ".join("%d%%: %.4f (kept %d)" % (cv, E["curve"][mname][cv][0], E["curve"][mname][cv][1])
                                             for cv in sorted(E["curve"][mname]))))
    for mname in ("tree", "KC_0", "U-global_0"):
        lo_, hi_ = E["ci"][mname]
        say("  P@80 %-11s %.4f  95%% [%.4f, %.4f] (kept %d of %d)" % (mname, E["curve"][mname][80][0], lo_, hi_, E["curve"][mname][80][1], R["n"]))
    for mname in ("KC_0", "U-global_0"):
        d_, (lo_, hi_) = E["diff"][mname]
        say("  P@80 tree - %s %+.4f  95%% [%+.4f, %+.4f] (jointly bootstrapped; different subsets)" % (mname, d_, lo_, hi_))
    say("")
    say("== CRITERIA")
    vl, verd = verdict_lines(R)
    L.extend(vl)
    R["verdicts"] = verd
    say("")
    say("== PREDICTIONS (priors; HELD iff the point lies in [lo, hi], endpoints inclusive)")
    A1 = R["A1"]
    g = lambda st: None if st is None else st["d"]   # noqa: E731
    say(pred_line("A1 D13_MMLU", g(A1.get("MMLU_PRO_LB"))))
    say(pred_line("A1 share MMLU_PRO_LB", None if A1.get("MMLU_PRO_LB") is None else A1["MMLU_PRO_LB"]["share"]))
    for s in ("MATH", "GPQA", "IFEVAL", "BBH", "MUSR"):
        say(pred_line("A1 D13_%s" % s, g(A1.get(s))))
    say(pred_line("A2 D_src", g(a2["d_src"])))
    say(pred_line("A2 D_within", g(a2["d_within"])))
    for d in (2, 3, 4):
        say(pred_line("A3 D(%d)" % d, g(a3["curve"][d]["st"]) if d in a3["curve"] else None))
    for d in sorted(a3["curve"]):
        if d >= 5:
            dd = a3["curve"][d]["st"]["d"] - R["d13"]["d"]
            say("PREDICTION A3 D(%d) within 0.005 of D13: observed D(%d) - D13 = %+.4f -> %s" % (d, d, dd, "HELD" if abs(dd) <= 0.005 else "FAILED"))
    say(pred_line("A4 Delta", R["A4"]["d"]))
    say(pred_line("B1 D_U", R["B1"]["d"]))
    say(pred_line("B2 P(US_0)", R["p_us"][0]))
    say(pred_line("B2 D_Us", R["B2"]["d"]))
    say(pred_line("B2 spread_US", R["spread_us"]))
    say(pred_line("C D13_desc", cc["d13_desc"]["d"]))
    say(pred_line("C D_U,desc", cc["du_desc"]["d"]))
    say(pred_line("C P(KC-desc) - P(KC_0)", cc["kc_desc"]["d"]))
    d_kc, d_ug, d_ratio, d_msum, d_loop = R["_d_obs"]
    say("PREDICTION D tree members' manifest sum 155.0 s (seen): observed %.1f s; loop sum 112.5 s (seen): observed %.1f s;"
        " grafts 77.7 / 113.6 s (seen): observed %.1f / %.1f s (seen points: not scored)" % (
            d_msum, d_loop, D["man"]["graft_flatleaf"]["ms"] / 1000.0, D["man"]["graft_descent"]["ms"] / 1000.0))
    say(pred_line("D KC 5-seed median (s, 1 thread)", d_kc))
    say(pred_line("D U-global 5-seed median (s, 1 thread)", d_ug))
    say(pred_line("D tree end-to-end / KC median (1 thread)", d_ratio))
    say(pred_line("E P@80 tree", E["curve"]["tree"][80][0]))
    say(pred_line("E P@80 KC_0", E["curve"]["KC_0"][80][0]))
    say(pred_line("E P@80 U-global_0", E["curve"]["U-global_0"][80][0]))
    gap = E["diff"]["KC_0"][0] - R["d13"]["d"]
    say("PREDICTION E tree - KC gap at 80%% within 0.01 of D13: observed gap - D13 = %+.4f -> %s" % (gap, "HELD" if abs(gap) <= 0.01 else "FAILED"))
    say(pred_line("M G_own", m["g_own"]["d"]))
    say(pred_line("M P_fl - P(KC-relabel_0)", m["fl_rel"]["d"]))
    say("")
    say("WHAT THIS RESULT WILL NOT SHOW (fixed before data): that the tree is needed for filing (G13 FAILED stands); parity with any"
        " comparator (no TOST); anything on capability text; anything for another draw, recipe, embedder or slice; any certificate;"
        " any routing value; that a wall-clock ratio generalises beyond this machine, thread count and language; a held-out claim"
        " beyond CK-CLOSE-v2's content-closure. Selective filing (e) never decides anything.")
    return "\n".join(L) + "\n"


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def pins_lines(o):
    o_ = ["%s script %s blob:%s (LF); pinned readers: %s; flat_mix_mmlu blob:%s (checked by g13_comparator)" % (
        TAG, os.path.basename(__file__), blob_lf(os.path.abspath(__file__)),
        ", ".join("%s blob:%s" % (n, p[:8]) for n, p in PINS), G.FLAT_MIX_PIN[1][:8])]
    o_.append("%s bundle npz sha256 %s; json sha256-lf %s" % (TAG, o["paths"]["bundle_npz_sha256"], o["paths"]["bundle_json_sha256_lf"]))
    for k in sorted(o["paths"]):
        if k.startswith(("flatleaf", "descent")) or k == "pointer_sha256_lf":
            o_.append("%s %s sha256-lf %s" % (TAG, k, o["paths"][k]))
    return o_


def guard_paths(lane, root, out):
    if lane != "r2":
        refuse("G13-BREAKDOWN reads lane r2 objects only (--lane r2), not lane %s" % lane)
    c = cfg()
    named = [("--bundle", P(root, c["bundle"])), ("flatLeaf validation", P(root, c["fl_val"])), ("descent validation", P(root, c["de_val"])),
             ("--out", out)]
    LN.guard(lane, named, root=root)


_ROOT = [ROOT]


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--run", "--time-worker"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--bundle", default=None, help="--time-worker only")
    ap.add_argument("--spec", default=None, help="--time-worker only")
    ap.add_argument("--threads", type=int, default=None, help="--time-worker only")
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
    if a.time_worker:
        return time_worker(a.bundle, a.spec)
    root = _ROOT[0]
    outp = a.out or P(root, cfg()["out"])
    guard_paths(a.lane, root, outp)
    rc, txt = _POOL_GUARD[0](cfg()["pool"])
    first = "POOL %s (B0-2 pool check rc %d): %s" % (cfg()["pool"], rc, txt.replace("\n", " | "))
    out(first)
    if rc != 0:
        refuse("the B0-2 pool check of %s failed: %s" % (cfg()["pool"], txt))
    if a.run and os.path.exists(outp):
        refuse("%s exists; the outcome is write-once" % outp)
    _LOAD_T0[0] = _CLOCK[0]()
    o = load_objects(root)
    o["t_load"] = _CLOCK[0]() - _LOAD_T0[0]
    if a.dry_run:
        for ln in pins_lines(o):
            out(ln)
        c = cfg()
        out("%s DENOMINATORS (Support (a), I5 PASSED): EVAL %d / %d components; TRAIN %d; per source %s" % (
            TAG, len(o["ye"]), len(set(o["comp"].tolist())), len(o["yt"]),
            ", ".join("%s %d/%d/%d" % ((s,) + c["support_eval"][s] + (c["support_train"][s],)) for s in c["sources"])))
        out("%s MC-EXCLUDE as in G13: EVAL %d, GATE %d, TRAIN %d (lists = the CSVs' multi-class items)" % ((TAG,) + o["mc"]))
        out("%s I0 PASSED (eight manifests = lane r2 pointer, commit %s); I4 PASSED (%d leaves; per source %s); I3 misses %d of %d;"
            " I2 P_descent %s (recorded %s)" % (TAG, c["commit"], len(o["leaves"]), c["leaves_by_source"], o["i3_miss"], len(o["ye"]),
                                               o["i2"], c["i2"]))
        for d in c["depths"]:
            fr, names = frontier_names(o, d)
            kcd = kc_at_depth(o, d)
            out("%s F(%d): %d nodes (%d <empty>); sum k_c(%d) %d; classes with k_c > 1: %d" % (
                TAG, d, len(names), sum(1 for v in names.values() if v < 0), d, sum(kcd.values()), sum(1 for v in kcd.values() if v > 1)))
        ident = check_i1(identity_arms(o))
        out("%s I1 PASSED (SEEN numbers reproduced): %s" % (TAG, json.dumps(ident["i1_got"], sort_keys=True)))
        out("%s dry-run: NO new statistic computed or printed" % TAG)
        return 0
    ident = check_i1(identity_arms(o))
    stem = P(root, cfg()["bundle"])
    spec = {"kc": {str(k): v for k, v in ident["kc"].items()}, "L": ident["L"], "seeds": list(SEEDS),
            "ksrc": [[s, cfg()["leaves_by_source"][s]] for s in cfg()["sources"]]}
    R = compute(o, ident)
    R["D"]["t12"] = _TIMING12[0](stem, spec)
    R["D"]["machine"] = _MACHINE[0]()
    body = "\n".join(pins_lines(o)) + "\n" + render(R, o)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    with open(outp, "x", encoding="utf-8", newline="\n") as f:
        f.write(first + "\n" + body)
    out(body.rstrip("\n"))
    out("%s wrote %s (write-once)" % (TAG, outp))
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────────
# (the fixture builder, the cases and the mutant harness follow)

def _unit(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def _fixture_spec(variant="A", dim=12):
    """Hand-built geometry on orthonormal axes (see the selftest docstring for every expected value)."""
    e = np.eye(dim)
    if variant == "A":
        mm = [("n00000001", 0, None, False, _unit(e[0] + e[1] + e[2] + e[6]), "MMLU_PRO_LB"),
              ("n00000002", 1, "n00000001", False, _unit(e[0] + e[1]), "MMLU_PRO_LB/x"),
              ("n00000003", 1, "n00000001", False, e[2], "MMLU_PRO_LB/y"),
              ("n00000004", 2, "n00000002", True, e[0], "Emergent #1"),
              ("n00000005", 2, "n00000002", True, e[1], "Emergent #2"),
              ("n00000006", 2, "n00000003", True, _unit(e[2] + 0.5 * e[6]), "Emergent #3")]
        train = [("MMLU_PRO_LB/x", e[0], 20), ("MMLU_PRO_LB/x", e[1], 10), ("MMLU_PRO_LB/y", e[1], 14), ("MMLU_PRO_LB/y", e[2], 20),
                 ("MMLU_PRO_LB/x", e[6], 8), ("BBH/u", e[3], 20), ("BBH/v", e[4], 20)]
        evals = [("MMLU_PRO_LB/x", e[0], 20), ("MMLU_PRO_LB/x", e[1], 20), ("MMLU_PRO_LB/x", e[6], 20), ("MMLU_PRO_LB/y", e[2], 20),
                 ("BBH/u", e[3], 20), ("BBH/v", e[4], 20), ("BBH/u", _unit(e[3] + 1.5 * e[0]), 10)]
        descent_wrong = {5: "BBH/u"}          # eval group 5 (v at e4) descends to the u cell
        noise = 0.02
    else:                                    # "B": KC's prototype dragged by TRAIN outliers -> the tree wins on MMLU
        mm = [("n00000001", 0, None, False, _unit(e[0] + e[2]), "MMLU_PRO_LB"),
              ("n00000002", 1, "n00000001", True, e[0], "MMLU_PRO_LB/x"),
              ("n00000003", 1, "n00000001", True, e[2], "MMLU_PRO_LB/y")]
        train = [("MMLU_PRO_LB/x", e[0], 20), ("MMLU_PRO_LB/y", e[2], 20), ("MMLU_PRO_LB/y", _unit(0.3 * e[2] + e[7]), 15),
                 ("BBH/u", e[3], 20), ("BBH/v", e[4], 20)]
        evals = [("MMLU_PRO_LB/x", e[0], 20), ("MMLU_PRO_LB/y", _unit(e[2] + 0.95 * e[0]), 20), ("MMLU_PRO_LB/y", e[2], 20),
                 ("BBH/u", e[3], 20), ("BBH/v", e[4], 20)]
        descent_wrong = {}
        noise = 0.005
    bbh = [("n00000001", 0, None, False, _unit(e[3] + e[4]), "BBH"),
           ("n00000002", 1, "n00000001", True, e[3], "BBH/u"),
           ("n00000003", 1, "n00000001", True, e[4], "BBH/v")]
    return dict(members={"mmlu_pro_lb": ("MMLU_PRO_LB", mm), "bbh": ("BBH", bbh)}, train=train, evals=evals,
                descent_wrong=descent_wrong, noise=noise, dim=dim)


Q_HEAD = ["true_key", "true_source", "rule", "leaf_id", "leaf_label", "leaf_depth", "leaf_dominant", "leaf_purity", "routed_source",
          "routed_domain", "top1", "source_ok", "domain_ok", "item_id"]


def _write_csv(path, head, rows):
    import csv
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(head)
        for r in rows:
            w.writerow(r)


def _fixture_write(tmp, variant="A", drop_log=None, mc_list=None, i3_break=False, bad_leaf=False, seed=11):
    """Writes a complete lane-r2 layout under tmp; returns (cfg, sides, truth) with truth = the generated arrays."""
    sp = _fixture_spec(variant)
    rng = np.random.default_rng(seed)
    dim = sp["dim"]
    classes = sorted({c for c, _v, _n in sp["train"]} | {c for c, _v, _n in sp["evals"]})
    ci = {c: k for k, c in enumerate(classes)}

    def draw(specs, prefix, pair):
        X, y, items, comp, grp = [], [], [], [], []
        cnum = 0
        for g, (c, v, n) in enumerate(specs):
            for k in range(n):
                X.append(_unit(v + sp["noise"] * rng.standard_normal(dim)))
                y.append(ci[c])
                items.append("i:%s%03d" % (prefix, len(items)))
                grp.append(g)
                comp.append(cnum + k // 2 if pair else len(comp))
            cnum += (n + 1) // 2
        return np.array(X), np.array(y), items, np.array(comp), np.array(grp)
    Xt, yt, titems, _tc, tgrp = draw(sp["train"], "t", False)
    Xe, ye, eitems, ecomp, egrp = draw(sp["evals"], "e", True)
    nodes = {}
    for mdir, (src, ns) in sp["members"].items():
        for (nid, dep, par, leaf, mu, lab) in ns:
            nodes["%s:%s" % (src, nid)] = dict(src=src, depth=dep + 1, leaf=leaf, mu=mu, label=lab, mdir=mdir)
    leaves = sorted(u for u, n in nodes.items() if n["leaf"])
    LM = np.vstack([nodes[u]["mu"] for u in leaves])
    tleaf = [leaves[k] for k in np.argmax(Xt @ LM.T, axis=1)]
    eleaf = [leaves[k] for k in np.argmax(Xe @ LM.T, axis=1)]
    dom = {}
    for u in leaves:
        ys = [classes[yt[j]] for j in range(len(yt)) if tleaf[j] == u]
        cnt = Counter(ys)
        dom[u] = min((c for c in cnt if cnt[c] == max(cnt.values())), default="")
    fl = np.array([int(dom[eleaf[i]] == classes[ye[i]]) for i in range(len(ye))])
    base = os.path.join(tmp, *RES.split("/"), "B0")
    val = os.path.join(base, "graft_flatleaf", "seed_42", "validation")
    dval = os.path.join(base, "graft_descent", "seed_42", "validation")

    def qrow(key, u, item, cell=None):
        cell = dom[u] if cell is None else cell
        return [key, src_of(key), "flatLeaf", u, nodes[u]["label"], nodes[u]["depth"], cell, "1.0000", src_of(cell), cell,
                int(cell == key), int(src_of(cell) == src_of(key)), int(cell == key), item]
    qe = [qrow(classes[ye[i]], eleaf[i], it) for i, it in enumerate(eitems)]
    if i3_break:                       # one EVAL row filed to a leaf that is not its argmax (and not changing its cell)
        i = next(k for k in range(len(eitems)) if any(u != eleaf[k] and dom[u] == dom[eleaf[k]] for u in leaves))
        alt = [u for u in leaves if u != eleaf[i] and dom[u] == dom[eleaf[i]]]
        qe[i] = qrow(classes[ye[i]], alt[0], eitems[i])
    if bad_leaf:
        qe[1] = qe[1][:3] + ["MMLU_PRO_LB:n99999999"] + qe[1][4:]
    mc_rows = [qrow("MMLU_PRO_LB/x", leaves[0], "i:emc"), qrow("BBH/u", leaves[0], "i:emc")]
    gate_rows = [qrow(classes[ye[0]], eleaf[0], "i:g1")]
    _write_csv(os.path.join(val, RP.QUERIES), Q_HEAD, qe + mc_rows + gate_rows)
    _write_csv(os.path.join(val, RP.TRAIN), Q_HEAD, [qrow(classes[yt[j]], tleaf[j], it) for j, it in enumerate(titems)])
    _write_csv(os.path.join(val, RP.LEAVES), ["leaf_id", "leaf_label", "leaf_depth", "profile_size", "leaf_dominant", "leaf_purity"],
               [[u, nodes[u]["label"], nodes[u]["depth"], sum(1 for x in tleaf if x == u), dom[u], "1.0000"] for u in leaves])
    de = []
    for i, it in enumerate(eitems):
        de.append(qrow(classes[ye[i]], eleaf[i], it, cell=sp["descent_wrong"].get(int(egrp[i]))))
    _write_csv(os.path.join(dval, RP.QUERIES), Q_HEAD, de + mc_rows + gate_rows)
    for mdir, (src, ns) in sp["members"].items():
        d = os.path.join(base, mdir, "seed_42")
        os.makedirs(d, exist_ok=True)
        js = []
        for (nid, dep, par, leaf, mu, lab) in ns:
            js.append({"id": nid, "label": lab, "depth": dep, "isLeaf": leaf, "isBridge": False, "parentIds": [par] if par else [],
                       "childIds": [x[0] for x in ns if x[2] == nid], "vmfMu": [float(x) for x in mu]})
        with open(os.path.join(d, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"iteration": 0, "nodes": js[:1]}) + "\n")         # an earlier line: only the LAST is read
            f.write(json.dumps({"iteration": 5, "nodes": js}) + "\n")
    durations = {"mmlu_pro_lb": 8000, "bbh": 2000, "graft_flatleaf": 5000, "graft_descent": 7000}
    loops = {"mmlu_pro_lb": (6500, 7900), "bbh": (1500, 1900), "graft_flatleaf": (4800,), "graft_descent": (6800,)}
    ptr = {"format": "fixture", "entries": {}}
    for x, ms in durations.items():
        d = os.path.join(base, x, "seed_42")
        os.makedirs(os.path.join(d, "diagnostics"), exist_ok=True)
        mp = os.path.join(d, "diagnostics", "run_manifest.json")
        with open(mp, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"commit": "2703f2c25807393605f863345c3dc0c8bd132849", "duration_ms": ms}, f)
        ptr["entries"]["B0/%s" % x] = {"manifest_sha256_lf": sha256_lf(mp)}
        if x != drop_log:
            with open(os.path.join(d, "headless_run.log"), "w", encoding="utf-8") as f:
                for t in loops[x]:
                    f.write("Top-Level Roll-Up:\n  TOTAL TIME       :  %s ms (100.0%%)\n" % "{:,}".format(t).replace(",", " "))
    pp = os.path.join(tmp, "experiment_configs", "rp12_r2", "objects_of_record.json")
    os.makedirs(os.path.dirname(pp), exist_ok=True)
    with open(pp, "w", encoding="utf-8") as f:
        json.dump(ptr, f)
    stem = os.path.join(base, "readouts", "g13_bundle_flatleaf")
    os.makedirs(os.path.dirname(stem), exist_ok=True)
    np.savez(stem + ".npz", eval_X=Xe, eval_y=ye, eval_comp=ecomp, eval_fl=fl, train_X=Xt, train_y=yt, classes=np.array(classes),
             leaf_major=np.array([dom[u] for u in leaves if dom[u]]), eval_item=np.array(eitems), train_item=np.array(titems))
    n_c = len(set(ecomp.tolist()))
    mcl = {"EVAL": {"i:emc": ["BBH/u", "MMLU_PRO_LB/x"]}, "GATE": {}, "TRAIN": {}} if mc_list is None else mc_list
    with open(stem + ".json", "w", encoding="utf-8") as f:
        json.dump({"pool_id": "pv2_fixture", "dim": dim, "n_eval": len(ye), "n_components": n_c,
                   "n_eval_before_exclusion": len(ye) + 1, "n_components_before_exclusion": n_c + 1, "multiclass_excluded": mcl}, f)
    sides = dict([(i, "EVAL") for i in eitems] + [(i, "TRAIN") for i in titems] + [("i:g1", "GATE"), ("i:emc", "EVAL")])
    esrc = np.array([src_of(classes[k]) for k in ye])
    tsrc = np.array([src_of(classes[k]) for k in yt])
    srcs = ("MMLU_PRO_LB", "BBH")
    fc = dict(REG)
    fc.update(pool="pv2_fixture", expect=("pv2_fixture", len(ye) + 1, n_c + 1),
              members=(("bbh", "BBH"), ("mmlu_pro_lb", "MMLU_PRO_LB")), sources=srcs,
              support_eval={s: (int((esrc == s).sum()), len(set(ecomp[esrc == s].tolist()))) for s in srcs},
              support_train={s: int((tsrc == s).sum()) for s in srcs},
              leaves_by_source=dict(Counter(nodes[u]["src"] for u in leaves)), n_eval=len(ye), n_comp=n_c, n_train=len(yt),
              n_leaves=len(leaves), depths=(2, 3, 4, 5), leaf_strata=((2, 2), (3, 3), (4, 99)))
    truth = dict(Xt=Xt, yt=yt, Xe=Xe, ye=ye, ecomp=ecomp, egrp=egrp, classes=classes, fl=fl, eleaf=eleaf, dom=dom, leaves=leaves,
                 esrc=esrc, tsrc=tsrc)
    return fc, sides, truth


def _counting_clock():
    t = [0.0]

    def clk():
        t[0] += 1.0
        return t[0]
    return clk


def _oracle_u(Xt, yt, Xe, ye, k, s, classes):
    """Independent naming for the U arms: FM's k-means, majority with the smaller-name tie written out here."""
    r = FM.spherical_kmeans(Xt, k, s, max_iter=G.MAX_ITER)
    lab = []
    for j in range(k):
        cnt = Counter(int(x) for x in yt[r["labels"] == j])
        lab.append(min((c for c in cnt if cnt[c] == max(cnt.values())), key=lambda c: classes[c]) if cnt else -1)
    return r["centers"], np.array(lab)


def _oracle_sel(margin_by_m, correct_by_m, groups):
    members = FM.group_members(groups)
    rng = np.random.default_rng(BOOT_SEED)
    reps = {m: [] for m in margin_by_m}
    for _ in range(BOOT_B):
        idx = FM.twin_boot_indices(groups, rng, members)
        for m in margin_by_m:
            mm, cc = margin_by_m[m][idx], correct_by_m[m][idx]
            k = len(idx) * 80 // 100
            reps[m].append(cc[np.argsort(-mm, kind="stable")[:k]].mean())
    d = np.array(reps["tree"]) - np.array(reps["KC_0"])
    bs = sorted(float(x) for x in d)
    return bs[int(0.025 * BOOT_B)], bs[int(0.975 * BOOT_B) - 1]


def _run_fixture(tmp, variant="A", argv_extra=(), expect_refusal=None, cfg_patch=None, **kw):
    """Executes main() (the real entry point) on a written fixture; returns (rc or refusal text, printed text, cfg, truth)."""
    fc, sides, truth = _fixture_write(tmp, variant, **kw)
    if cfg_patch:
        cfg_patch(fc, truth)
    saved = (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0], _TIMING12[0], _MACHINE[0], _CLOCK[0])
    _CFG[0], _ROOT[0], _SIDES[0] = fc, tmp, (lambda: sides)
    _POOL_GUARD[0] = lambda pool: (0, "[POOL-GUARD stub] %s OK" % pool)
    _TIMING12[0] = lambda stem, spec: {"threads": "12", "blas": "12", "kc": [0.5] * 5, "ug": [0.25] * 5, "us": [0.75] * 5}
    _MACHINE[0] = lambda: {"free_ram_gb": 32.0, "pids": ["python.exe:4242"], "blas": "1"}
    _CLOCK[0] = _counting_clock()
    buf = []
    try:
        res = main(list(argv_extra) or ["--run", "--lane", "r2"], out=buf.append)
    except SystemExit as e:
        res = str(e)
        if expect_refusal is None:
            raise
    finally:
        (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0], _TIMING12[0], _MACHINE[0], _CLOCK[0]) = saved
    if expect_refusal is not None:
        assert isinstance(res, str) and expect_refusal in res, (expect_refusal, res)
    return res, "\n".join(buf), fc, truth


def _expected_i1(fc, truth, variant="A"):
    """I1 strings for a fixture from the hand-known filings (KC_s and NCC by construction; U-global from the oracle)."""
    ye, classes = truth["ye"], truth["classes"]
    Xt, yt = FM.unit_rows(truth["Xt"]), truth["yt"]
    Xe = FM.unit_rows(truth["Xe"])
    g = truth["egrp"]
    if variant == "A":
        kc_ok = (~np.isin(g, [1, 6])).astype(np.int64)        # KC wrong on x@e1 (group 1) and u' (group 6)
    else:
        kc_ok = (g != 1).astype(np.int64)                      # KC wrong on the shifted y items (group 1)
    diff = truth["fl"] - kc_ok
    lo, hi, _se = G.boot(diff, G.comp_groups(truth["ecomp"]))
    ukm = []
    for s in SEEDS:
        C_, lab = _oracle_u(Xt, yt, Xe, ye, len(truth["leaves"]), s, classes)
        ukm.append("%.4f" % (lab[np.argmax(Xe @ C_.T, axis=1)] == ye).mean())
    return dict(p_fl="%.4f" % truth["fl"].mean(), p_kc=tuple(["%.4f" % kc_ok.mean()] * 5), d13="%+.4f" % diff.mean(),
                lo="%+.4f" % lo, hi="%+.4f" % hi, ukm=tuple(ukm), ncc="%.4f" % kc_ok.mean()), kc_ok


def _patch_i1(variant="A"):
    def p(fc, truth):
        fc["i1"] = _expected_i1(fc, truth, variant)[0]
        fc["i2"] = "%.4f" % ((truth["fl"] == 1) & ~np.isin(truth["egrp"], [5] if variant == "A" else [])).mean()
    return p


def _fx_stats(truth, diff):
    lo, hi, _se = G.boot(np.asarray(diff, dtype=np.float64), G.comp_groups(truth["ecomp"]))
    return "%+.4f  95%% [%+.4f, %+.4f]" % (float(np.mean(diff)), lo, hi)


def _need(text, *needles):
    for nd in needles:
        assert nd in text, "missing: %r" % nd


def st_e2e_A(tmp):
    """--run end to end on fixture A: every readout's VALUE (hand-derived; U arms, kNN and (e)'s interval from oracles)."""
    res, text, fc, tr = _run_fixture(tmp, "A", cfg_patch=_patch_i1("A"))
    assert res == 0, res
    outp = P(tmp, fc["out"])
    filed = open(outp, encoding="utf-8").read()
    assert filed.splitlines()[0] == "POOL pv2_fixture (B0-2 pool check rc 0): [POOL-GUARD stub] pv2_fixture OK", filed.splitlines()[0]
    g, fl = tr["egrp"], tr["fl"]
    _i1, kc_ok = _expected_i1(fc, tr, "A")
    tree2 = (~np.isin(g, [2, 6])).astype(np.int64)                     # anchors: x@e6 under the y anchor, u' under x
    ncc = kc_ok
    _need(filed,
          "[G13B] union EVAL 130 items in 65 CK-CLOSE components (after MC-EXCLUDE: EVAL 1, GATE 0, TRAIN 0 excluded, as in G13); TRAIN 112",
          "MMLU_PRO_LB  SCOREABLE (C-a1): P_fl 0.5000, P(KC_0) 0.7500, D13_s -0.2500  95% [",
          "(n 80, 40 components;", "share 1.0000", "BBH          DESCRIPTIVE-ONLY: P_fl 0.8000, P(KC_0) 0.8000, D13_s +0.0000  95% [+0.0000, +0.0000] (n 50, 25 components;",
          "  shares sum to 1.0000",
          "source accuracy tree 0.9231, KC_0 0.9231; D_src +0.0000  95% [+0.0000, +0.0000] (n 130,",
          "within-source class accuracy on the 120 items BOTH file to the true source: tree 0.6667, KC_0 0.8333; D_within -0.1667",
          "d = 1 source accuracy only: tree 0.9231, KC_0 0.9231",
          "  d = 2: |F(d)| 4 (0 <empty>), sum k_c(d) 4; P_tree(d) 0.7692; P(KC(d)_s) 0.7692 / 0.7692 / 0.7692 / 0.7692 / 0.7692; D(d) " + _fx_stats(tr, tree2 - ncc),
          "  d = 3: |F(d)| 5 (0 <empty>), sum k_c(d) 5; P_tree(d) 0.6154; P(KC(d)_s) 0.7692 / 0.7692 / 0.7692 / 0.7692 / 0.7692; D(d) " + _fx_stats(tr, fl - kc_ok),
          "  d = 5: |F(d)| 5 (0 <empty>), sum k_c(d) 5; P_tree(d) 0.6154;",
          "KC(2) = NCC exactly: asserted on every seed (P_NCC 0.7692); leaves whose subtree TRAIN majority differs from the leaves CSV leaf_dominant: 0",
          "  D13 at flatLeaf-leaf depth 2: +0.0000  95% [+0.0000, +0.0000] (n 40, 20 components;",
          "  D13 at flatLeaf-leaf depth 3: -0.2222  95% [", "(n 90, 45 components;",
          "  D13 at flatLeaf-leaf depth >= 4: n = 0: no EVAL item, no estimate",
          "== A4 Delta = D13 - [P_tree(2) - P_NCC] (paired): " + _fx_stats(tr, (fl - kc_ok) - (tree2 - ncc)),
          "P_descent 0.4615; D13_desc = P_descent - P(KC_0) -0.3077",
          "  MMLU_PRO_LB  D13_desc -0.2500", "  BBH          D13_desc -0.4000",
          "KC-descent (nearest TRAIN source centroid, then nearest KC_0 prototype within it): P 0.7692; P(KC-desc) - P(KC_0) +0.0000",
          "== (M) MECHANISM: KC-relabel_s P 0.7692 / 0.7692 / 0.7692 / 0.7692 / 0.7692 (prototypes with no TRAIN item keep their class: 0 / 0 / 0 / 0 / 0)",
          "  G_own = P(KC_0) - P(KC-relabel_0) +0.0000  95% [+0.0000, +0.0000]",
          "  P_fl - P(KC-relabel_0) " + _fx_stats(tr, fl - kc_ok),
          "  objects load (bundle, CSVs, snapshots) 1.000 s: outside every fit time",
          "  k-means fit, 1 thread, KC (all classes)     seconds 1.000 / 1.000 / 1.000 / 1.000 / 1.000; median 1.000, max 1.000",
          "  k-means fit, 1 thread, U-global             seconds 1.000 / 1.000 / 1.000 / 1.000 / 1.000; median 1.000, max 1.000",
          "  k-means fit, 1 thread, U-source (six fits)  seconds 2.000 / 2.000 / 2.000 / 2.000 / 2.000; median 2.000, max 2.000",
          "  k-means fit, 12 threads (BLAS 12), KC (all classes)  seconds 0.500 / 0.500 / 0.500 / 0.500 / 0.500; median 0.500, max 0.500",
          "  tree members' manifest sum 10.0 s; engine loop sum (first TOTAL TIME per member log) 8.0 s; grafts flatLeaf 5.0 s / descent 7.0 s",
          "  machine state: free RAM 32.0 GB; admitted PIDs ['python.exe:4242']; BLAS threads in this process 1",
          "  tree end-to-end (members + flatLeaf graft) 15.0 s / KC median 1.000 s = 15.0x; members only 10.0x",
          "80%: 0.7692 (kept 104)", "  P@80 KC_0        0.8077  95% [",
          "C-a1: HELD (the tree loses on MMLU_PRO_LB): D13_MMLU -0.2500, interval [",
          "C-a4: HELD (the loss opens below the anchors): Delta -0.1538, interval [",
          "point seen before registration (domain_ok P_fl 0.8042, NCC 0.8065",
          "C-M: UNDETERMINED: G_own +0.0000, interval [+0.0000, +0.0000] contains 0",
          "F-GB2 (fires iff C-a4 FAILED): does not fire (C-a4 HELD)",
          "PREDICTION A1 D13_MMLU -0.030 [-0.050, -0.010]: observed -0.2500 -> FAILED",
          "PREDICTION A1 share MMLU_PRO_LB +0.750 [+0.450, +1.100]: observed +1.0000 -> HELD",
          "PREDICTION A1 D13_BBH +0.000 [-0.010, +0.010]: observed +0.0000 -> HELD",
          "PREDICTION A1 D13_MATH -0.040 [-0.120, +0.040]: observed none -> NOT SCORED (no estimate)",
          "PREDICTION A3 D(2) -0.002 [-0.008, +0.004]: observed +0.0000 -> HELD",
          "PREDICTION A3 D(4) -0.016 [-0.026, -0.006]: observed -0.1538 -> FAILED",
          "PREDICTION A3 D(5) within 0.005 of D13: observed D(5) - D13 = +0.0000 -> HELD",
          "PREDICTION A4 Delta -0.019 [-0.030, -0.008]: observed -0.1538 -> FAILED",
          "PREDICTION C D13_desc -0.115 [-0.130, -0.100]: observed -0.3077 -> FAILED",
          "PREDICTION C P(KC-desc) - P(KC_0) -0.010 [-0.025, +0.000]: observed +0.0000 -> HELD",
          "PREDICTION D KC 5-seed median (s, 1 thread) [1, 10]: observed +1.0000 -> HELD",
          "PREDICTION D U-global 5-seed median (s, 1 thread) [20, 120]: observed +1.0000 -> FAILED",
          "PREDICTION D tree end-to-end / KC median (1 thread) [10, 100]: observed +15.0000 -> HELD",
          "PREDICTION E P@80 tree +0.870 [+0.840, +0.900]: observed +0.7692 -> FAILED",
          "PREDICTION E tree - KC gap at 80% within 0.01 of D13: observed gap - D13 = +0.1154 -> FAILED",
          "PREDICTION M G_own +0.012 [+0.004, +0.022]: observed +0.0000 -> FAILED",
          "PREDICTION C-a1 verdict probabilities (HELD 0.75): observed HELD")
    # the U arms against an independent oracle (TRAIN fits only; U-source: all 5 leaves' centroids decide, the true source never)
    Xt, yt, Xe, ye, cl = FM.unit_rows(tr["Xt"]), tr["yt"], FM.unit_rows(tr["Xe"]), tr["ye"], tr["classes"]
    pu, us, usin, u0 = [], [], [], None
    for s in SEEDS:
        C_, lab = _oracle_u(Xt, yt, Xe, ye, 5, s, cl)
        ok = (lab[np.argmax(Xe @ C_.T, axis=1)] == ye).astype(np.int64)
        pu.append(ok.mean())
        u0 = ok if s == 0 else u0
        cs, ls, ss = [], [], []
        for so, k in (("MMLU_PRO_LB", 3), ("BBH", 2)):
            m = tr["tsrc"] == so
            c2, l2 = _oracle_u(Xt[m], yt[m], Xe, ye, k, s, cl)
            cs.append(c2); ls.append(l2); ss += [so] * k
        Cs, Ls, Ss = np.vstack(cs), np.concatenate(ls), np.array(ss)
        S = Xe @ Cs.T
        oks = (Ls[np.argmax(S, axis=1)] == ye).astype(np.int64)
        us.append(oks.mean())
        usin.append((Ls[np.argmax(np.where(Ss[None, :] == tr["esrc"][:, None], S, -np.inf), axis=1)] == ye).mean())
        if s == 0:
            us0 = oks
    assert us != usin, "fixture A must separate U-source from its source-oracle form"
    assert max(pu) - min(pu) > 0 and max(us) - min(us) > 0, "fixture A must spread the U seeds"
    sp_u, sp_us = max(pu) - min(pu), max(us) - min(us)
    _need(filed, "P(U_s) %s; spread_U %.4f; D_U = P_fl - P(U_0) %s" % (" / ".join("%.4f" % x for x in pu), sp_u, _fx_stats(tr, fl - u0)),
          "P(US_s) %s; spread_US %.4f; D_Us = P_fl - P(US_0) %s" % (" / ".join("%.4f" % x for x in us), sp_us, _fx_stats(tr, fl - us0)),
          "EVAL filed within its TRUE source; never deciding): %s" % " / ".join("%.4f" % x for x in usin),
          "  kNN-15         %.4f  (deterministic)" % G.knn_correct(Xt, yt, Xe, ye, cl).mean())
    d_us = float(np.mean(fl - us0))
    lo, hi, _ = G.boot(fl - us0, G.comp_groups(tr["ecomp"]))
    vb2 = v_spread(d_us, lo, hi, sp_us)
    _need(filed, "C-b2: %s" % vb2, "F-GB (fires iff C-b2 REVERSED): %s" % ("FIRES" if vb2 == "REVERSED" else "does not fire (C-b2 %s)" % vb2),
          "C-b1: %s" % v_spread(float(np.mean(fl - u0)), *G.boot(fl - u0, G.comp_groups(tr["ecomp"]))[:2], sp_u),
          "point seen before registration (U-global seeds 0.7159-0.7573")
    # (e): the joint bootstrap of the two methods' own top 80% against an oracle loop
    o = load_objects_for_test(tmp, fc)
    P0, own0 = o["_kcP0"]
    names_leaf = np.array([tr["dom"][u] for u in tr["leaves"]])
    LM = np.vstack([o["nodes"][u]["mu"] for u in tr["leaves"]])
    lo_e, hi_e = _oracle_sel({"tree": margins(Xe @ LM.T, names_leaf), "KC_0": margins(Xe @ P0.T, own0)}, {"tree": fl, "KC_0": kc_ok},
                             G.comp_groups(tr["ecomp"]))
    _need(filed, "  P@80 tree - KC_0 -0.0385  95%% [%+.4f, %+.4f] (jointly bootstrapped; different subsets)" % (lo_e, hi_e))
    # write-once: a second --run on the same layout refuses and leaves the file as it was
    _run_fixture(tmp, "A", cfg_patch=_patch_i1("A"), expect_refusal="exists; the outcome is write-once")
    assert open(outp, encoding="utf-8").read() == filed
    return text


def load_objects_for_test(tmp, fc):
    saved = (_CFG[0], _SIDES[0])
    _CFG[0] = fc
    _SIDES[0] = None
    try:
        o = load_objects(tmp)
    finally:
        _CFG[0], _SIDES[0] = saved
    kc = G.k_per_class(o["classes"], o["yt"], [str(x) for x in o["b"]["leaf_major"]])
    o["_kcP0"] = G.kc_prototypes(o["Xt"], o["yt"], kc, 0)
    return o


def st_e2e_B(tmp):
    """Fixture B: KC's prototype dragged by TRAIN outliers -> C-a1 FAILED with D13_MMLU +0.3333; C-a4 UNDETERMINED (Delta 0)."""
    res, text, fc, tr = _run_fixture(tmp, "B", cfg_patch=_patch_i1("B"))
    assert res == 0
    filed = open(P(tmp, fc["out"]), encoding="utf-8").read()
    _need(filed, "MMLU_PRO_LB  SCOREABLE (C-a1): P_fl 1.0000, P(KC_0) 0.6667, D13_s +0.3333  95% [",
          "C-a1: FAILED: D13_MMLU +0.3333, interval [",
          "C-a4: UNDETERMINED: Delta +0.0000, interval [+0.0000, +0.0000] contains 0; point seen before registration",
          "F-GB2 (fires iff C-a4 FAILED): does not fire (C-a4 UNDETERMINED)",
          "PREDICTION C-a1 verdict probabilities (HELD 0.75): observed FAILED",
          "  BBH          DESCRIPTIVE-ONLY: P_fl 1.0000, P(KC_0) 1.0000, D13_s +0.0000")
    a1 = [l for l in filed.splitlines() if l.startswith("C-a1: FAILED")][0]
    lo = float(a1.split("interval [")[1].split(",")[0])
    assert lo > 0, a1


def _synthetic_R(a1=(-0.03, -0.05, -0.01), a4=(-0.02, -0.03, -0.01), b2=(0.05, 0.02, 0.08), sp_us=0.02, b1=(0.07, 0.05, 0.09),
                 sp_u=0.04, gm=(0.01, 0.004, 0.02)):
    def st(t):
        return dict(d=t[0], lo=t[1], hi=t[2], se=0.007, deff=1.2, n=100, G=90, n_eff=83, mde=0.0196, disc=0.1)
    return {"A1": {cfg()["scoreable"]: st(a1)}, "A4": st(a4), "B2": st(b2), "spread_us": sp_us, "B1": st(b1), "spread_ug": sp_u,
            "M": {"g_own": st(gm)}}


def st_branches():
    """Every printed branch of the five criteria and two falsifiers, executed through verdict_lines (used verbatim by render)."""
    cases = [
        (dict(), {"C-a1: HELD (the tree loses on MMLU_PRO_LB): D13_MMLU -0.0300, interval [-0.0500, -0.0100] wholly below 0",
                  "C-a4: HELD (the loss opens below the anchors): Delta -0.0200, interval [-0.0300, -0.0100] wholly below 0; point seen",
                  "C-b2: HELD (the tree beats source-aware unsupervised k-means): D_Us +0.0500, interval [+0.0200, +0.0800] wholly above 0 AND D_Us > spread_US 0.0200",
                  "C-b1: HELD: D_U +0.0700, interval [+0.0500, +0.0900] wholly above 0 AND D_U > spread_U 0.0400; point seen before registration",
                  "C-M: HELD (KC's edge is label ownership): G_own +0.0100, interval [+0.0040, +0.0200] wholly above 0",
                  "F-GB (fires iff C-b2 REVERSED): does not fire (C-b2 HELD)", "F-GB2 (fires iff C-a4 FAILED): does not fire (C-a4 HELD)",
                  "  support C-a1: SE 0.00700 (registered 0.00724); DEFF 1.200 (registered 1.214); n_eff 83; MDE80 0.0196 (registered 0.0203)",
                  "  support C-b1: SE 0.00700; DEFF 1.200; n_eff 83; MDE80 0.0196; discordance 0.1000 (no registered Support figure"}),
        (dict(a1=(0.03, 0.01, 0.05), a4=(0.02, 0.01, 0.03), b2=(-0.05, -0.08, -0.02), b1=(-0.07, -0.09, -0.05), gm=(-0.01, -0.02, -0.004)),
         {"C-a1: FAILED: D13_MMLU +0.0300, interval [+0.0100, +0.0500] wholly above 0",
          "C-a4: FAILED: Delta +0.0200, interval [+0.0100, +0.0300] wholly above 0; point seen before registration",
          "C-b2: REVERSED (its FAILED): D_Us -0.0500, interval [-0.0800, -0.0200] wholly below 0 AND D_Us < -spread_US -0.0200",
          "C-b1: REVERSED (its FAILED): D_U -0.0700, interval [-0.0900, -0.0500] wholly below 0 AND D_U < -spread_U -0.0400; point seen",
          "C-M: FAILED: G_own -0.0100, interval [-0.0200, -0.0040] wholly below 0",
          "F-GB (fires iff C-b2 REVERSED): FIRES: the anchored tree files worse than source-aware label-free k-means at matched counts",
          "F-GB2 (fires iff C-a4 FAILED): FIRES: the loss sits at the anchors, not below them",
          "PREDICTION C-b2 verdict probabilities (HELD 0.60, REVERSED 0.05): observed REVERSED"}),
        (dict(a1=(-0.01, -0.03, 0.0), a4=(0.0, -0.01, 0.01), b2=(0.03, 0.01, 0.05), sp_us=0.05, b1=(0.03, 0.01, 0.05), gm=(0.0, -0.01, 0.01)),
         {"C-a1: UNDETERMINED: D13_MMLU -0.0100, interval [-0.0300, +0.0000] contains 0 (neither a loss nor parity is shown)",
          "C-a4: UNDETERMINED: Delta +0.0000, interval [-0.0100, +0.0100] contains 0; point seen before registration",
          "C-b2: UNDETERMINED: D_Us +0.0300, interval [+0.0100, +0.0500], spread_US 0.0500 (UNDETERMINED by spread: spread_US exceeds 0.040)",
          "C-b1: UNDETERMINED: D_U +0.0300, interval [+0.0100, +0.0500], spread_U 0.0400; point seen before registration",
          "C-M: UNDETERMINED: G_own +0.0000, interval [-0.0100, +0.0100] contains 0",
          "F-GB (fires iff C-b2 REVERSED): does not fire (C-b2 UNDETERMINED)",
          "F-GB2 (fires iff C-a4 FAILED): does not fire (C-a4 UNDETERMINED)"}),
        (dict(b2=(0.03, 0.01, 0.05), sp_us=0.035), {"C-b2: UNDETERMINED: D_Us +0.0300, interval [+0.0100, +0.0500], spread_US 0.0350"}),
    ]
    for kw, needles in cases:
        lines, _v = verdict_lines(_synthetic_R(**kw))
        text = "\n".join(lines)
        for nd in needles:
            assert nd in text, "missing %r in\n%s" % (nd, text)
    lines, _v = verdict_lines(_synthetic_R(b2=(0.03, 0.01, 0.05), sp_us=0.035))
    assert [l for l in lines if l.startswith("C-b2")] == ["C-b2: UNDETERMINED: D_Us +0.0300, interval [+0.0100, +0.0500], spread_US 0.0350"]


def st_boundaries():
    assert v_below(-0.02, -0.001) == "HELD" and v_below(-0.02, 0.0) == "UNDETERMINED" and v_below(0.0, 0.02) == "UNDETERMINED"
    assert v_below(0.001, 0.02) == "FAILED"
    assert v_above(0.001, 0.02) == "HELD" and v_above(0.0, 0.02) == "UNDETERMINED" and v_above(-0.02, 0.0) == "UNDETERMINED"
    assert v_above(-0.02, -0.001) == "FAILED" and v_above(-0.01, 0.02) == "UNDETERMINED"
    assert v_spread(0.03, 0.001, 0.05, 0.02) == "HELD" and v_spread(0.02, 0.001, 0.05, 0.02) == "UNDETERMINED"
    assert v_spread(0.01, 0.001, 0.02, 0.02) == "UNDETERMINED" and v_spread(0.03, 0.0, 0.05, 0.02) == "UNDETERMINED"
    assert v_spread(-0.03, -0.05, -0.001, 0.02) == "REVERSED" and v_spread(-0.02, -0.05, -0.001, 0.02) == "UNDETERMINED"
    assert spread_of([0.70, 0.74, 0.72]) == 0.74 - 0.70
    assert pred_line("A1 D13_BBH", 0.010).endswith("-> HELD") and pred_line("A1 D13_BBH", 0.0101).endswith("-> FAILED")
    assert majority([2, 1, 2, 1], ["c", "b", "a"]) == 2 and majority([], ["a"]) == -1          # tie to the smaller NAME
    m = margins(np.array([[0.9, 0.8, 0.1], [0.5, 0.2, 0.4]]), np.array(["a", "a", "b"]))
    assert np.allclose(m, [0.8, 0.1]), m
    assert kept_precision(np.array([3.0, 1.0, 2.0, 2.0, 0.0]), np.array([1, 0, 0, 1, 1]), 80) == (0.5, 4)   # stable ties
    assert kept_precision(np.arange(7.0), np.ones(7), 50)[1] == 3                                           # floor, not round


def st_dry_run(tmp):
    res, text, fc, tr = _run_fixture(tmp, "A", argv_extra=["--dry-run", "--lane", "r2"], cfg_patch=_patch_i1("A"))
    assert res == 0
    lines = text.splitlines()
    assert lines[0] == "POOL pv2_fixture (B0-2 pool check rc 0): [POOL-GUARD stub] pv2_fixture OK", lines[0]
    _need(text, "[G13B] DENOMINATORS (Support (a), I5 PASSED): EVAL 130 / 65 components; TRAIN 112; per source MMLU_PRO_LB 80/40/72, BBH 50/25/40",
          "[G13B] MC-EXCLUDE as in G13: EVAL 1, GATE 0, TRAIN 0", "I3 misses 0 of 130; I2 P_descent 0.4615 (recorded 0.4615)",
          "[G13B] F(2): 4 nodes (0 <empty>); sum k_c(2) 4; classes with k_c > 1: 0", "[G13B] I1 PASSED (SEEN numbers reproduced):",
          "[G13B] dry-run: NO new statistic computed or printed")
    assert not any(l.startswith(("C-a1", "C-b2", "C-M", "== (a)", "PREDICTION")) for l in lines), text
    assert not os.path.exists(P(tmp, fc["out"]))


def st_absent_log(tmp):
    res, text, fc, tr = _run_fixture(tmp, "A", cfg_patch=_patch_i1("A"), drop_log="bbh")
    filed = open(P(tmp, fc["out"]), encoding="utf-8").read()
    _need(filed, "  bbh             manifest duration_ms 2000; headless_run.log ABSENT (no TOTAL TIME line copied)",
          "engine loop sum (first TOTAL TIME per member log) INCOMPLETE (1 of 2 logs)")


def st_naming_differs(tmp):
    """A leaves-CSV leaf_dominant that is not the TRAIN-filed majority: counted, and D(d >= 5) departs from D13 (FAILED branch)."""
    fc, sides, tr = _fixture_write(tmp, "A")
    val = P(tmp, fc["fl_val"])
    lp = os.path.join(val, RP.LEAVES)
    rows = read_csv(lp)
    for r in rows:
        if r["leaf_id"] == "BBH:n00000003":
            r["leaf_dominant"] = "BBH/u"                       # v's leaf renamed u in the engine's table
    _write_csv(lp, list(rows[0].keys()), [list(r.values()) for r in rows])
    # the flatLeaf rows and the bundle follow the engine's table (v items now file wrong)
    qp = os.path.join(val, RP.QUERIES)
    q = read_csv(qp)
    for r in q:
        if r["leaf_id"] == "BBH:n00000003":
            r["leaf_dominant"] = "BBH/u"
    _write_csv(qp, Q_HEAD, [[r[k] for k in Q_HEAD] for r in q])
    stem = P(tmp, fc["bundle"])
    z = dict(np.load(stem + ".npz", allow_pickle=False))
    v = tr["classes"].index("BBH/v")
    z["eval_fl"] = np.where(z["eval_y"] == v, 0, z["eval_fl"])
    z["leaf_major"] = np.array([("BBH/u" if u == "BBH:n00000003" else tr["dom"][u]) for u in tr["leaves"]])
    np.savez(stem + ".npz", **z)
    _patch_i1("A")(fc, tr)
    saved = (_CFG[0], _SIDES[0])
    _CFG[0], _SIDES[0] = fc, None
    try:
        o = load_objects(tmp)
        fc["i1"] = identity_arms(o)["i1_got"]               # the I1 strings of this modified layout (check_i1 then passes)
        _CLOCK[0], ck = _counting_clock(), _CLOCK[0]
        try:
            ident = check_i1(identity_arms(o))
            R = compute(o, ident)
            R["D"]["t12"], R["D"]["machine"] = None, {}
            text = render(R, o)
        finally:
            _CLOCK[0] = ck
    finally:
        _CFG[0], _SIDES[0] = saved
    _need(text, "leaves whose subtree TRAIN majority differs from the leaves CSV leaf_dominant: 1",
          "  k-means fit, 12 threads: NOT MEASURED (no child run)", "machine state: free RAM unknown; admitted PIDs None; BLAS threads in this process unknown")
    line = [l for l in text.splitlines() if l.startswith("PREDICTION A3 D(5) within 0.005 of D13")][0]
    assert line.endswith("-> FAILED"), line


def st_refusals(tmp_factory):
    """Every refusal on the --run path, by its message (each on a fresh layout)."""
    def tamper_pointer(fc, tr):
        _patch_i1("A")(fc, tr)
        pp = P(_ROOT_T[0], fc["pointer"])
        d = json.load(open(pp))
        d["entries"]["B0/bbh"]["manifest_sha256_lf"] = "0" * 64
        json.dump(d, open(pp, "w"))

    def wrong_i1(fc, tr):
        _patch_i1("A")(fc, tr)
        fc["i1"] = dict(fc["i1"], ncc="0.1234")

    def wrong_hi(fc, tr):
        _patch_i1("A")(fc, tr)
        fc["i1"] = dict(fc["i1"], hi="+0.9999")

    def wrong_i2(fc, tr):
        _patch_i1("A")(fc, tr)
        fc["i2"] = "0.9999"

    def wrong_support(fc, tr):
        _patch_i1("A")(fc, tr)
        fc["support_eval"] = dict(fc["support_eval"], BBH=(51, 25))

    def wrong_leaves(fc, tr):
        _patch_i1("A")(fc, tr)
        fc["leaves_by_source"] = dict(fc["leaves_by_source"], BBH=3)
    for name, kw, needle in (
            ("I0 pointer", dict(cfg_patch=tamper_pointer), "is not the lane r2 pointer's " + "0" * 64),
            ("I1", dict(cfg_patch=wrong_i1), "I1: ['ncc'] reproduced as ['0.7692'], recorded ['0.1234']"),
            ("I1 hi", dict(cfg_patch=wrong_hi), "I1: ['hi'] reproduced as ['-0.0769'], recorded ['+0.9999']"),
            ("I2", dict(cfg_patch=wrong_i2), "I2: P_descent on the 130 bundle items is 0.4615, not the recorded 0.9999"),
            ("I3", dict(cfg_patch=_patch_i1("A"), i3_break=True), "I3: argmax cos(x, leaf vmfMu) differs from the CSV leaf on 1 of 130"),
            ("I4", dict(cfg_patch=_patch_i1("A"), bad_leaf=True), "MMLU_PRO_LB:n99999999 is not a snapshot leaf"),
            ("I5 support", dict(cfg_patch=wrong_support), "source BBH: EVAL 50 / components 25 / TRAIN 40, not Support (a)'s 51 / 25 / 40"),
            ("I5 leaves", dict(cfg_patch=wrong_leaves), "snapshot leaves per source"),
            ("MC-EXCLUDE", dict(cfg_patch=_patch_i1("A"), mc_list={"EVAL": {"i:emc": ["a", "b"]}, "GATE": {"i:g1": ["a", "b"]}, "TRAIN": {}}),
             "MC-EXCLUDE: the CSVs' multi-class items (held-out 1, TRAIN 0) are not the bundle's lists (EVAL+GATE 2, TRAIN 0)"),
            ("lane", dict(cfg_patch=_patch_i1("A"), argv_extra=["--run", "--lane", "r1"]), "reads lane r2 objects only (--lane r2), not lane r1")):
        tmp = tmp_factory()
        _ROOT_T[0] = tmp
        _run_fixture(tmp, "A", expect_refusal=needle, **kw)
        fc_out = P(tmp, REG["out"])
        assert not os.path.exists(fc_out), "%s: an outcome was written" % name
    # pool guard rc != 0
    tmp = tmp_factory()
    fc, sides, tr = _fixture_write(tmp, "A")
    _patch_i1("A")(fc, tr)
    saved = (_CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0])
    _CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0] = fc, tmp, (lambda: sides), (lambda pool: (1, "[POOL-GUARD] mismatch"))
    buf = []
    try:
        try:
            main(["--run", "--lane", "r2"], out=buf.append)
            raise AssertionError("pool guard rc 3 not refused")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: the B0-2 pool check of pv2_fixture failed: [POOL-GUARD] mismatch" % TAG, e
        assert buf == ["POOL pv2_fixture (B0-2 pool check rc 1): [POOL-GUARD] mismatch"], buf
        # KC(2) != NCC and k_c(2) != 1, on loaded objects
        _POOL_GUARD[0] = saved[3]
        o = load_objects(tmp)
        ident = check_i1(identity_arms(o))
        bad = dict(ident)
        bad["ncc_ok"] = ident["ncc_ok"].copy()
        bad["ncc_ok"][0] = 1 - bad["ncc_ok"][0]
        try:
            compute(o, bad)
            raise AssertionError("KC(2) != NCC admitted")
        except SystemExit as e:
            assert "A3: KC(2)_0 differs from NCC on 1 items" in str(e), e
        v = tr["classes"].index("BBH/v")
        o2 = dict(o)
        u = tr["classes"].index("BBH/u")
        o2["yt"] = np.where(o["yt"] == v, u, o["yt"])            # every BBH TRAIN item u: both depth-2 BBH nodes named u
        try:
            compute(o2, ident)
            raise AssertionError("k_c(2) = 2 admitted")
        except SystemExit as e:
            assert "A3: k_c(2) is not 1 for every class ({'BBH/u': 2})" in str(e), e
    finally:
        _CFG[0], _ROOT[0], _SIDES[0], _POOL_GUARD[0] = saved


_ROOT_T = [None]


def st_worker(tmp):
    """The real 12-thread child on the fixture bundle (thread variables set before numpy; one JSON line back)."""
    fc, sides, tr = _fixture_write(tmp, "A")
    r = _timing12_proc(P(tmp, fc["bundle"]), {"kc": {"0": 1, "1": 1, "2": 1, "3": 2}, "L": 5, "seeds": [0, 1],
                                                "ksrc": [["MMLU_PRO_LB", 3], ["BBH", 2]]})
    assert r.get("threads") == "12" and (r.get("blas", "").split(",")[0] == "12" or r.get("blas") in ("unknown", "none")) and len(r["kc"]) == 2 and len(r["ug"]) == 2 and len(r["us"]) == 2, r
    assert all(x >= 0 for x in r["kc"] + r["ug"] + r["us"]), r
    ms = _machine_state()
    assert set(ms) == {"free_ram_gb", "pids", "blas"} and (set(ms["blas"].split(",")) == {"1"} or ms["blas"] in ("unknown", "none")), ms


def st_seed_of_record(tmp):
    """KC_0 is the comparator of record everywhere: a changed KC_1 moves only the ladder's KC row (and the spread it prints)."""
    fc, sides, tr = _fixture_write(tmp, "A")
    _patch_i1("A")(fc, tr)
    saved = (_CFG[0], _SIDES[0], _CLOCK[0])
    _CFG[0], _SIDES[0] = fc, None
    try:
        o = load_objects(tmp)
        ident = check_i1(identity_arms(o))
        texts = []
        for tamper in (False, True):
            idn = dict(ident)
            idn["kc_ok"] = dict(ident["kc_ok"])
            if tamper:
                k1 = ident["kc_ok"][1].copy()
                k1[:7] = 1 - k1[:7]
                idn["kc_ok"][1] = k1
            _CLOCK[0] = _counting_clock()
            R = compute(o, idn)
            R["D"]["t12"], R["D"]["machine"] = None, {}
            texts.append(render(R, o))
    finally:
        _CFG[0], _SIDES[0], _CLOCK[0] = saved
    a, b = texts[0].splitlines(), texts[1].splitlines()
    moved = [x for x, y in zip(a, b) if x != y]
    assert len(a) == len(b) and moved, "the tamper changed nothing"
    assert all(m.lstrip().startswith("KC  ") for m in moved), moved


def st_guard(tmp_factory):
    """The REAL B0-2 pool check (pool_check_v2: the v2_union_pool.py --dry-run child process, the pool-file pin, -wal / -journal)
    on v2_union_pool's own fixture DBs (never a DB of record); accept, then each refusal, and main() refusing through it."""
    tmp = tmp_factory()
    # the fixture DBs are written by v2_union_pool's own _fixture in a child process (flat_mix_mmlu guards sqlite3 in this one)
    code = "import sys, json; sys.path.insert(0, %r); import v2_union_pool as VU; print(json.dumps(VU._fixture(%r)))" % (HERE, tmp)
    pr = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=ROOT)
    assert pr.returncode == 0, pr.stderr[-400:]
    side, src, cdb, pool = json.loads(pr.stdout.strip().splitlines()[-1])
    pf_rel = "experiment_configs/engine_pool_fixture.json"
    pf = P(tmp, pf_rel)
    os.makedirs(os.path.dirname(pf), exist_ok=True)
    with open(pf, "w", encoding="utf-8", newline="\n") as f:
        f.write('{"pool_id": "%s"}\n' % pool)
    fc = dict(REG)
    fc.update(pool=pool, pool_file=pf_rel, pool_file_sha256_lf=sha256_lf(pf), guard_args=("--side", side, "--source-db", src, "--corpus-db", cdb),
              guard_dbs=(src, cdb))
    saved = (_CFG[0], _ROOT[0])
    _CFG[0], _ROOT[0] = fc, tmp
    try:
        open(src + "-wal", "wb").close()                                   # a 0-byte -wal passes
        rc, txt = pool_check_v2(pool)
        assert rc == 0, txt
        assert txt.startswith("[UNION-POOL] pool %s recomputed from the side export (3 EVAL components with a member in mc6-2026-09-11);"
                              " expected %s | [UNION-POOL] DRY RUN: every check passed" % (pool, pool)), txt
        assert ("engine pool file sha256-lf %s (pinned) | mc.db-wal 0 bytes; mc.db-journal absent; corpus.db-wal absent;"
                " corpus.db-journal absent" % fc["pool_file_sha256_lf"][:16]) in txt, txt
        # refusals: another pool (the child's S2 refusal, rc 1), the pool-file pin, a non-empty -wal / -journal
        rc, txt = pool_check_v2("pv2_1575de61bb20e977")
        assert rc == 1 and txt.startswith("v2_union_pool.py --dry-run rc 1:") and "S2: the side export's mc6-2026-09-11 pool is %s" % pool in txt, txt
        fc["pool_file_sha256_lf"] = "0" * 64
        rc, txt = pool_check_v2(pool)
        assert rc == 1 and txt == "engine pool file %s sha256-lf %s, not the pinned %s" % (pf, sha256_lf(pf), "0" * 64), txt
        fc["pool_file_sha256_lf"] = sha256_lf(pf)
        with open(cdb + "-journal", "wb") as f:
            f.write(b"x" * 5)
        rc, txt = pool_check_v2(pool)
        assert rc == 1 and txt == "%s-journal is 5 bytes (a writer is open on corpus.db): a failed precondition" % cdb, txt
        os.remove(cdb + "-journal")
        with open(src + "-wal", "wb") as f:
            f.write(b"y" * 3)
        rc, txt = pool_check_v2(pool)
        assert rc == 1 and txt == "%s-wal is 3 bytes (a writer is open on mc.db): a failed precondition" % src, txt
        # main() through the real check: refused before any object is read, the check's line printed first
        buf = []
        assert _POOL_GUARD[0] is pool_check_v2
        try:
            main(["--dry-run", "--lane", "r2"], out=buf.append)
            raise AssertionError("main accepted a failed pool check")
        except SystemExit as e:
            assert str(e) == "%s REFUSED: the B0-2 pool check of %s failed: %s-wal is 3 bytes (a writer is open on mc.db): a failed" \
                " precondition" % (TAG, pool, src), e
        assert buf == ["POOL %s (B0-2 pool check rc 1): %s-wal is 3 bytes (a writer is open on mc.db): a failed precondition" % (pool, src)], buf
    finally:
        _CFG[0], _ROOT[0] = saved


CASES = (("boundaries", "verdict functions at their boundaries; prediction bands; majority tie; margins; stable kept set", "plain"),
         ("branches", "every C-a1 / C-a4 / C-b2 / C-b1 / C-M / F-GB / F-GB2 branch printed with its values", "plain"),
         ("e2e_A", "--run end to end, fixture A: every readout value, U oracles, (e) oracle interval, write-once", "tmp"),
         ("e2e_B", "--run end to end, fixture B: C-a1 FAILED, C-a4 UNDETERMINED", "tmp"),
         ("dry_run", "--dry-run: pool line first, I0-I5, no statistic, no outcome", "tmp"),
         ("absent_log", "(d) with a missing log: ABSENT and INCOMPLETE printed", "tmp"),
         ("naming", "leaf naming differs: counted; D(5) FAILED branch; t12 / machine fallbacks", "tmp"),
         ("refusals", "I0-I5, MC-EXCLUDE, lane, pool guard, KC(2) != NCC, k_c(2) != 1", "factory"),
         ("worker", "the real 12-thread child process and the machine probe", "tmp"),
         ("seed", "KC_0 is the comparator of record (a changed KC_1 moves only the ladder's KC row)", "tmp"),
         ("guard", "the REAL B0-2 pool check on v2_union_pool fixture DBs: accept, 4 refusals, main refusing through it", "factory"))
_FN = {"boundaries": st_boundaries, "branches": st_branches, "e2e_A": st_e2e_A, "e2e_B": st_e2e_B, "dry_run": st_dry_run,
       "absent_log": st_absent_log, "naming": st_naming_differs, "refusals": st_refusals, "worker": st_worker,
       "seed": st_seed_of_record, "guard": st_guard}


def selftest(only=None, quiet=False):
    import tempfile
    import shutil
    made, fails, ran = [], [], 0

    def factory():
        d = tempfile.mkdtemp(prefix="g13b_")
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
            print("  %-48s tests %-22s original %-4s control %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "SURVIVED (as it must)" if control_ok else "KILLED (harness broken)"))
            continue
        killed += int(k)
        print("  %-48s tests %-22s original %-4s mutant %-8s %s" % (name, ",".join(tests), "PASS" if base[key] is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:90]), flush=True)
    n_real = sum(1 for m in MUTANTS if not m[0].startswith("M00"))
    print("MUTANTS: %d of %d KILLED; control %s" % (killed, n_real, "survived" if control_ok else "KILLED"))
    return 0 if killed == n_real and control_ok else 1


def _exec_selftest(src, tests):
    ns = {"__name__": "g13_breakdown_mutant", "__file__": os.path.abspath(__file__)}
    try:
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:160])


NL = chr(10)
MUTANTS = (
    ("M00 control (no-op edit)", [("    return max(vals) - min(vals)", "    return max(vals) - min(vals)")], ["boundaries", "e2e_A"]),
    ("M01 per-source stratum leaked across sources", [("st = stat(fl[m] - kc0[m], comp[m])", "st = stat(fl - kc0, comp)")], ["e2e_A"]),
    ("M02 D13_s sign flipped", [("st = stat(fl[m] - kc0[m], comp[m])", "st = stat(kc0[m] - fl[m], comp[m])")], ["e2e_A"]),
    ("M03 A1 first source only", [('    for s in c["sources"]:' + NL + '        m = o["esrc"] == s' + NL + '        st = stat',
                                   '    for s in c["sources"][:1]:' + NL + '        m = o["esrc"] == s' + NL + '        st = stat')], ["e2e_A"]),
    ("M04 share over n_s (registered n D13)", [('st["share"] = (st["n"] * st["d"]) / (n * R["d13"]["d"])',
                                                'st["share"] = (st["n"] * st["d"]) / (st["n"] * R["d13"]["d"])')], ["e2e_A"]),
    ("M05 k_c(d) off by one depth", [("        kcd = kc_at_depth(o, d)" + NL + "        oks, ts", "        kcd = kc_at_depth(o, d + 1)" + NL + "        oks, ts")],
     ["e2e_A"]),
    ("M06 KC(2) != NCC admitted", [('                if not np.array_equal(oks[s], ident["ncc_ok"]):', "                if False:")], ["refusals"]),
    ("M07 k_c(2) != 1 admitted", [("            if any(k != 1 for k in kcd.values()):", "            if False:")], ["refusals"]),
    ("M08 frontier drops leaves shallower than d", [('return {u: (o["anc"][u][d] if o["nodes"][u]["depth"] >= d else u) for u in o["leaves"]}',
                                                     'return {u: o["anc"][u].get(d) for u in o["leaves"]}')], ["e2e_A"]),
    ("M09 A4 Delta sign flipped", [('R["A4"] = stat((fl - kc0) - (R["tree2_ok"] - ident["ncc_ok"]), comp)',
                                    'R["A4"] = stat((R["tree2_ok"] - ident["ncc_ok"]) - (fl - kc0), comp)')], ["e2e_A"]),
    ("M10 U-source with a source oracle as primary", [('us_ok[s] = (lab_[np.argmax(S, axis=1)] == ye).astype(np.int64)',
                                                       'us_ok[s] = (lab_[np.argmax(np.where(srcs[None, :] == o["esrc"][:, None], S, -np.inf), axis=1)] == ye).astype(np.int64)')],
     ["e2e_A"]),
    ("M11 U-source fitted and named on EVAL", [('            fit, t = ukm_fit(Xt[m], ksrc[so], s)' + NL + '            tsum += t' + NL + '            cents.append(fit["centers"])' + NL +
                                                '            labs.append(name_clusters(fit["labels"], ksrc[so], yt[m], classes))',
                                                '            me = o["esrc"] == so' + NL + '            fit, t = ukm_fit(Xe[me], ksrc[so], s)' + NL + '            tsum += t' + NL +
                                                '            cents.append(fit["centers"])' + NL + '            labs.append(name_clusters(fit["labels"], ksrc[so], ye[me], classes))')],
     ["e2e_A"]),
    ("M12 KC-relabel reads EVAL", [("            mj = majority(yt[near == j], classes)", "            mj = majority(ye[np.argmax(Xe @ Pm.T, axis=1) == j], classes)")],
     ["e2e_A"]),
    ("M13 timing includes the objects load", [("    t0 = _CLOCK[0]()" + NL + "    r = fn(*a, **k)", "    t0 = _LOAD_T0[0]" + NL + "    r = fn(*a, **k)")], ["e2e_A"]),
    ("M14 P@80 difference read as paired", [('ci(reps["tree"] - reps[m])) for m in arms if m != "tree"}',
                                             'G.boot(arms["tree"][1] - arms[m][1], groups)[:2]) for m in arms if m != "tree"}')], ["e2e_A"]),
    ("M15 kept = round, not floor", [("    k = len(margin) * c // 100", "    k = int(round(len(margin) * c / 100))")], ["boundaries"]),
    ("M16 spread min<->max", [("    return max(vals) - min(vals)", "    return min(vals) - min(vals)")], ["boundaries", "e2e_A"]),
    ("M17 C-a1/C-a4 interval touching 0 read as below", [('    if hi < 0:' + NL + '        return "HELD"', '    if hi <= 0:' + NL + '        return "HELD"')],
     ["boundaries"]),
    ("M18 C-b2/C-b1 without the spread clause", [("    if lo > 0 and d > spread:", "    if lo > 0:")], ["boundaries", "branches"]),
    ("M19 C-M without its FAILED clause", [('    if hi < 0:' + NL + '        return "FAILED"' + NL + '    return "UNDETERMINED"' + NL + NL + NL + 'def v_spread',
                                            '    return "UNDETERMINED"' + NL + NL + NL + 'def v_spread')], ["boundaries", "branches"]),
    ("M20 C-a1 read on the wrong population (BBH)", [('    a1 = R["A1"][cfg()["scoreable"]]', '    a1 = R["A1"]["BBH"]')], ["e2e_A"]),
    ("M21 C-a1 support line omitted", [('        o.append(support_line("C-a1", a1))', "        pass")], ["branches"]),
    ("M22 C-b1 seen-point disclosure omitted", [('    seen1 = "point seen before registration (U-global', '    seen1 = "(U-global')],
     ["e2e_A", "branches"]),
    ("M23 F-GB silent when it does not fire", [('else "does not fire (C-b2 %s)" % vb2))', 'else ""))')], ["branches"]),
    ("M24 F-GB2 fires on HELD", [('"FIRES: the loss sits at the anchors, not below them" if v4 == "FAILED"',
                                  '"FIRES: the loss sits at the anchors, not below them" if v4 == "HELD"')], ["e2e_A"]),
    ("M25 NOT SCORED line omitted", [('        return "PREDICTION %s: observed none -> NOT SCORED (no estimate)" % head', '        return ""')],
     ["e2e_A"]),
    ("M26 empty stratum not handled", [("    if n == 0:" + NL + "        return None" + NL, "")], ["e2e_A"]),
    ("M27 ABSENT log line omitted", [('            say("  %-15s manifest duration_ms %d; headless_run.log ABSENT (no TOTAL TIME line copied)" % (x, mm["ms"]))',
                                      "            pass")], ["absent_log"]),
    ("M28 comparator of record KC_1", [('    kc0 = ident["kc_ok"][0]', '    kc0 = ident["kc_ok"][1]')], ["seed"]),
    ("M29 write-once check removed", [("    if a.run and os.path.exists(outp):", "    if False:")], ["e2e_A"]),
    ("M30 write-once: check removed and mode w", [("    if a.run and os.path.exists(outp):", "    if False:"),
                                                   ('    with open(outp, "x", encoding="utf-8", newline=', '    with open(outp, "w", encoding="utf-8", newline=')],
     ["e2e_A"]),
    ("M31 I1 refusal removed", [("    if bad:" + NL + '        refuse("I1:', "    if False:" + NL + '        refuse("I1:')], ["refusals"]),
    ("M32 I3 bar at 1% (registered 0.1%)", [('    if 1000 * o["i3_miss"] > n_e:', '    if 100 * o["i3_miss"] > n_e:')], ["refusals"]),
    ("M33 I2 over every descent item (MC/GATE kept)", [('    o["i2"] = "%.4f" % o["desc"].mean()',
                                                        '    o["i2"] = "%.4f" % np.mean([int(cc == kk) for cc, kk, _n in cells_d.values()])')], ["e2e_A"]),
    ("M34 MC-EXCLUDE list check removed", [('    if set(multi_q) != set(ex["EVAL"]) | set(ex["GATE"]) or set(multi_t) != set(ex["TRAIN"]):', "    if False:")],
     ["refusals"]),
    ("M35 I0 pointer check removed", [('        if ent is None or ent.get("manifest_sha256_lf") != sha256_lf(mp):', "        if False:")], ["refusals"]),
    ("M36 lane guard removed", [('    if lane != "r2":', "    if False:")], ["refusals"]),
    ("M37 I5 per-source support check removed", [("        if got != want:" + NL + '            refuse("source %s', "        if False:" + NL + '            refuse("source %s')],
     ["refusals"]),
    ("M39 I1 ignores lo / hi", [("    bad = [k for k in want if got[k] != want[k]]", '    bad = [k for k in want if k not in ("lo", "hi") and got[k] != want[k]]')],
     ["refusals"]),
    ("M40 B0-2: -wal / -journal size not checked", [("            if os.path.exists(sp) and os.path.getsize(sp) > 0:", "            if False:")], ["guard"]),
    ("M41 B0-2: pool-file pin not checked", [('    if got != c["pool_file_sha256_lf"]:', "    if False:")], ["guard"]),
    ("M42 B0-2: child rc ignored", [("    if pr.returncode != 0:" + NL + '        return 1, "v2_union_pool.py', "    if False:" + NL + '        return 1, "v2_union_pool.py')],
     ["guard"]),
    ("M43 B0-2: main does not refuse on a failed check", [("    if rc != 0:" + NL + '        refuse("the B0-2 pool check', "    if False:" + NL + '        refuse("the B0-2 pool check')],
     ["guard", "refusals"]),
    ("M38 dry-run prints a statistic", [('        out("%s dry-run: NO new statistic computed or printed" % TAG)',
                                         '        out(render(compute(o, ident), o))')], ["dry_run"]),
)


if __name__ == "__main__":
    sys.exit(main())
