"""CERT-DIRECTION-STREAM - integrated over the arm direction stream, how often does CERT-UNDER-FILTER's C1 hold, and what
is its two-stage interval? DESCRIPTIVE; ZERO judge calls; no DB is written; no tree is built. IT CANNOT CHANGE C1'S
RECORDED VERDICT (CERT-UNDER-FILTER C1 HELD, as registered, at the registered streams); every number is printed BESIDE it.

REGISTRATION OF RECORD: docs/judge_v2_program.md L14758-L14792 (heading "## Registered 2026-09-23 (before any code or
call) - CERT-DIRECTION-STREAM: ..."; commit 46889ea); record docs/agents/results/CERT-DIRECTION-STREAM.json. The last
bracket in the programme file wins over anything restated here.

LAUNCH SEQUENCE (registration FLOW: registration -> engine-coder -> adversarial-reviewer READY -> run-operator ->
post-run review -> registrar):

  python tools/analysis/cert_direction_stream.py --selftest     # synthetic fixtures only; opens NO DB of record; the pool
                                                                # guard is not called; every registered print branch is
                                                                # executed and listed; passes under python and python -O
  python tools/analysis/cert_direction_stream.py --dry-run [--workers N]
                                                                # 0 calls, WRITES NOTHING: pool id, pins, DB fingerprints,
                                                                # G1-G3 (CERT's prepare), the denominators, stream 42 in
                                                                # full (22 arm builds) and its C0 leg, the measured wall
                                                                # time and the extrapolation to 200 streams, RAM per worker
                                                                # [READY 751cf57 D2, 2026-09-23: the dry-run builds s = 1
                                                                # AND 42 (DRY_STREAMS), prints the review's s = 1 row and
                                                                # runs SEED-PATH (2) on 2 streams; at 1 stream (2) prints
                                                                # NOT TESTED. D1: --run prints each stream's 13 d_a.]
  python tools/analysis/cert_direction_stream.py --run [--workers N]   # N = 8 in the registration's estimate
                                                                # the write-once outcome
                                                                # experiment_results/x12_crossdomain/cert_direction_stream_outcome.txt

  There is no --pilot and no judge cache (nothing is posted). --run refuses BEFORE computing if the outcome exists and
  opens it with mode "x"; any exception, gate or refusal writes nothing. It is a pool reader (rule 7): one window.
  The run is NOT resumable (as CERT's --run): an interrupted run is relaunched from the start; nothing partial is written.

THE PINNED INSTRUMENT, IMPORTED UNEDITED. tools/analysis/cert_under_filter.py, blob:f7d59019c3d65128687df46aebdcb798b43c3062
/ sha256-lf16:0db2026f17b559a1 (merged 4610a17; the main working tree holds the CRLF rendering,
sha256-crlf16:b144a7d4377acfd3, printed beside when present). The file is hashed BEFORE it is imported (a mismatch
refuses before any of its code runs), the imported module's __file__ must be that file, and it is hashed again after the
import; __file__ and both pins are printed in every mode (the execution witness). Its build() copy is checked by CERT's
own check_build_pin() (systematic_budget.build LF source sha16 128baa007a44a219) at launch in every mode.
NOTHING OF CERT IS ASSIGNED, WRAPPED OR REPLACED BY THIS SCRIPT (no monkeypatch): CERT's own import-time machinery (the
sqlite3.connect log, the stack_judge stub, systematic_budget.main disabled) runs exactly as in CERT, because this script
imports CERT before any other module that could open a DB.

HOW THE ONE KNOB IS REACHED (the registration: "the arm question-bootstrap seed s, which replaces Random(42) for EVERY
arm build (U, F_A and each of the 20 R draws) jointly"). CERT's arm board builder is the public function
    cert_under_filter.arm_edges(by_anchor, anchors, models, K=None, P1=None, u_edges=None, B=BOOT_B, seed=42)
whose first statement is `rng = random.Random(seed)`: the seed IS A PARAMETER. CERT's own callers never pass it
(prepare() calls arm_edges in discovery mode, _arm_job in fixed mode, both at the default 42), so this script does not
use them for the stream arms: its worker _stream_job calls cert_under_filter.arm_edges(rowset, anchors, models,
u_edges=U's edge list, B=300, seed=s) - fixed mode, exactly CERT's _arm_job call with the one keyword added. The arm row
sets are built as CERT's run_arms builds them (U: every routed row of U's anchors; F_A: CERT's convention-A keep set;
R_A_k: CERT's k-th convention-A draw, Random(1000 + k), from prepare()). Two execution proofs, both refusals on failure:
  [SEED-PATH 1] at s = 42 the fixed-mode U rebuilt here equals prepare()'s discovery-mode U (p, m, s, point) bit for bit,
                so the seed path reproduces CERT's default; (the selftest additionally proves, on a fixture, that this
                script's F_A and R_A arms at s = 42 equal CERT's own run_arms() bit for bit);
  [SEED-PATH 2] for EVERY one of the 22 arms (U, F_A, R_A_01..R_A_20), the bootstrap-mean vector differs between every
                pair of streams (all fingerprints distinct), so the knob provably moved in every arm build jointly.

THE CONNECTION LOG AND THE WORKERS (CERT's R3 (iii) as re-ruled, 8bbe6ce: the stack cache is opened EXACTLY ONCE per
process, by load_real, as file:<path>?mode=ro&immutable=1). load_real runs ONCE, in the parent. CERT's own workers
(_arm_job under ProcessPoolExecutor) never open a DB: they receive their rows by pickling; each spawned worker imports
the module afresh (its own, empty connection log; CERT's import-time guard refuses a DB opened at import), and CERT's
connection_log() inspects the PARENT's log only. This script does the same (rows are handed to each worker once, through
the pool initializer) and ADDS a worker witness: every job returns its process's connection-log length and stack-cache
open count before and after the build; any open in a job, or any non-empty log in a spawned worker, REFUSES the run
([WORKER-OPEN]). The parent's log is checked by CERT's connection_log() at the end (the stack cache exactly once).

HYGIENE (registration "HYGIENE"). First printed line: pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL). The
three inputs of record (experiment_results/x12_crossdomain/stack_v2_promptv2_x12all.db, mmlu_pro_dataset_cache_v2.db,
snapshots.db) are read through CERT's load_real only (mode=ro&immutable=1); BEFORE anything opens them a non-empty -wal
(CERT's check_wal) or a non-empty -journal (this script) REFUSES; sha256_16, size and mtime of each are printed before
and after and asserted unchanged ([DB-CHANGED] refuses the write). Routing bareq512_s42 (20260909_212117), as recorded
(CERT's r512.primary_routing; the anchor map is id-disjoint only - CERT's chip carries it).

WHAT IS COMPUTED PER STREAM s (registration "STREAMS"). Everything else as registered and as CERT computes it: convention
A; the 13 remaining anchors (Business below the 200-row floor under F_A; the removal rule is CERT's readout() C4 rule,
copied in denominators() - it is seed-free and computed once); U's 752 established edges (fixed from U by exact McNemar,
seed-free); the key direction from U (seed-free); direction = build()'s majority rule p > 0.5 (cert_under_filter.
wrong_maps); C1's statistic by cert_under_filter.c1_stats (13-anchor cluster bootstrap, B 2,000, numpy seed 42, point
+- 1.96 x SE) and cert_under_filter.c1_verdict (support trigger at 12 anchors). Per stream: W_U, W_F, mean W_R, Delta_W,
SE, the interval and its upper end, HELD iff c1_verdict reads HELD (the upper end < 0; the trigger cannot fire, the
anchor set being seed-free).

READINGS FIXED HERE, where the registration leaves a choice (each printed in the outcome):
  (d1) STREAMS. "s = 1..200 (200 streams), plus s = 42 as the reference": 42 lies inside 1..200, so the reference IS one
       of the 200; it is built once and counted once; h's denominator is 200 (the review's 6 of 21 included 42 once).
  (d2) U is rebuilt at every s (the registration names U among the arm builds): only W_U moves with s (printed); the
       edge set, the established set, the key direction and the anchor removal are fixed once from prepare().
  (d3) C0's second leg decides on the registration's words: over the review's 20 streams (s = 1..20, the ARMSEED values
       its recompute_seed.py loop used; printed) min / max W_F = 16 / 19, min / max Delta_W = -8.05 / -4.75 at the
       printed 2 dp, and exactly 15 of 20 upper ends >= 0. The review's per-stream table (armseed.out, embedded below,
       sha256 8210a64e465c3097...) is compared digit by digit and printed BESIDE (a mismatch there is printed, it does not
       decide C0). The first leg (stream 42) is to the digit of the outcome of record, every field.
  (d4) sd with ddof = 1 (ddof = 0 printed beside); percentiles numpy's default (linear); the between-stream variance in
       the mixture SE with ddof = 1.
  (d5) C3's two-stage RNG: numpy.random.default_rng(42); the 20,000 stream indices are drawn first, then the 20,000 x 13
       anchor indices; replicate r = sum of stream[r]'s d_a at the drawn anchors. The percentile interval is C3's
       interval; point +- 1.96 x mixture SE and the replicates' own sd are printed beside.
  (d6) C1 band edges and P1 are compared in INTEGER arithmetic on (held count k, 200), never on a float h.
  (d7) P1: HELD iff 0.18 <= h < 0.45, FAILED iff h >= 0.45 or h < 0.18 (the FALSIFIER's words), EXCEPT at h = 0.45
       exactly (k = 90), where the prediction's bracket [0.18, 0.45] reads HELD and the falsifier reads FAILED: that
       branch prints BOTH readings and "registrar ruling owed" (P1.CONFLICT), scoring neither.
       [RULED 2026-09-23 by the registrar (60ddf85, programme L14843-L14865, ruling (1)): at h = 0.45 exactly the
       falsifier's strict words govern: P1 HELD iff 36 <= k < 90 of 200, FAILED iff k >= 90 or k < 36 (p1_held()); the
       former P1.CONFLICT branch is REPLACED by this rule. Ruling (2): P5 NOT SCORED, as built. Ruling (3): d1-d9
       CONFIRMED; P3's upper end is C3's PERCENTILE interval's (p3_score()); point + 1.96 x mixture SE is printed beside
       and decides nothing.] P2 is the conjunction of
       its three brackets, each printed; P3 the conjunction of the mixture-SE bracket and the percentile upper end's
       bracket (the lower end is registered as "about" and is printed, not scored). P5 registers no interval ("about
       320"): it is printed at the prediction's premise h = 0.30 and at the measured h, NOT SCORED (P5.NOT_SCORED).
  (d8) C4: the Monte-Carlo SE of h = sqrt(h (1 - h) / 200); the stream count = the smallest integer n whose Wilson 95%
       half-width at p = the measured h is <= 0.05 (printed also at p = 0.30 and 0.50).
  (d9) Validity first: if C0 is not HELD, every readout prints its numbers labelled UNDETERMINED (BY VALIDITY), P1-P3 and
       P5 are UNDETERMINED (BY VALIDITY), P4 FAILED, the falsifier is not evaluated.

GUARDS are raise SystemExit / need(); never `assert` (python -O). Every criterion, prediction and falsifier line goes
through say_branch(), which records a registered branch id; --selftest executes every one and fails otherwise. No
computed value is identity-tested; every comparison is wrapped in bool().
"""
import argparse, hashlib, math, os, sys, tempfile, time; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)

# ------------------------------------------------------------------------------------------ the pinned instrument
CUB_PATH = os.path.join(HERE, "cert_under_filter.py")
CUB_BLOB = "f7d59019c3d65128687df46aebdcb798b43c3062"     # git blob of the LF rendering (merged 4610a17)
CUB_LF16 = "0db2026f17b559a1"                             # sha256-lf16 of the LF rendering
CUB_CRLF16 = "b144a7d4377acfd3"                           # sha256-crlf16 (the main working tree's rendering), beside


def file_pins(path):
    """blob = git's blob id of the LF rendering; sha256-lf16 of the LF bytes; sha256-crlf16 of the working-tree bytes when
    they are not LF (None otherwise)."""
    raw = open(path, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(), lf16=hashlib.sha256(lf).hexdigest()[:16],
                crlf16=None if raw == lf else hashlib.sha256(raw).hexdigest()[:16])


def check_cub_pins(path, blob=CUB_BLOB, lf16=CUB_LF16):
    p = file_pins(path)
    if not bool(p["blob"] == blob and p["lf16"] == lf16):
        h = globals().get("hit")
        if h is not None:
            h("PIN.REFUSED")
        raise SystemExit("[PIN] %s is blob:%s / sha256-lf16:%s; pinned blob:%s / sha256-lf16:%s (CERT-DIRECTION-STREAM "
                         "imports the pinned CERT instrument UNEDITED). Refused." % (path, p["blob"], p["lf16"], blob, lf16))
    return p


CUB_PRE = check_cub_pins(CUB_PATH)                        # BEFORE the import: none of a mismatched file's code runs
import cert_under_filter as cub                           # noqa: E402  (installs CERT's connection log and stub first)

if not bool(os.path.normcase(os.path.abspath(cub.__file__)) == os.path.normcase(os.path.abspath(CUB_PATH))):
    raise SystemExit("[PIN] the imported cert_under_filter is %s, not %s. Refused." % (cub.__file__, CUB_PATH))
CUB_POST = check_cub_pins(cub.__file__)
if not bool(CUB_POST == CUB_PRE):
    raise SystemExit("[PIN] cert_under_filter.py changed during the import. Refused.")

import numpy as np                                        # noqa: E402

need = cub.need

# ------------------------------------------------------------------------------------------ constants of record
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "cert_direction_stream_outcome.txt")
N_STREAMS = 200
STREAMS = tuple(range(1, N_STREAMS + 1))                  # reading (d1): 42 is inside; built and counted once
REF_STREAM = 42
REVIEW_STREAMS = tuple(range(1, 21))                      # recompute_seed.py: ARMSEED = 1..20 (armseed.out)
ARM_NAMES = ("U", "F_A") + tuple("R_A_%02d" % k for k in range(1, cub.K_DRAWS + 1))
TWO_STAGE_REPS = 20000
TWO_STAGE_SEED = 42
Z = 1.96
HALF_WIDTH_TARGET = 0.05
MIN_ANCHORS = cub.C1_MIN_ANCHORS                          # 12 (CERT's ruling R2 (b)); the fixture passes its own

# C0 leg 1: the outcome of record (experiment_results/x12_crossdomain/cert_under_filter_outcome.txt, b4b1688, L92-L99)
RECORD_42 = dict(W_U="26", W_F="17", WR="24.15", delta="-7.15", se="3.606", lo="-14.22", hi="-0.08", n_edges="752",
                 n_anchors="13", verdict="HELD")
# C0 leg 2: the review's 20 streams (docs/reviews/2026-09-23_cert_under_filter_post.md, 605675c; scratch cert_post/
# armseed.out sha256 8210a64e465c30976f58d8c3d228e8f2c469353d0b554df97e9336488c5cfdc4, recompute_seed.py sha256
# d70fca6a638439f7baa9632dd46aa02b15b99ea2a6cc752b2d85e13cf0cef4d0). Per stream: W_F, mean W_R, Delta, SE, lo, hi, verdict.
REVIEW_TABLE = {
    1: ("19", "24.00", "-5.00", "3.859", "-12.56", "+2.56", "UNDETERMINED"),
    2: ("17", "24.15", "-7.15", "3.769", "-14.54", "+0.24", "UNDETERMINED"),
    3: ("17", "23.90", "-6.90", "3.566", "-13.89", "+0.09", "UNDETERMINED"),
    4: ("19", "23.95", "-4.95", "3.934", "-12.66", "+2.76", "UNDETERMINED"),
    5: ("16", "23.90", "-7.90", "3.416", "-14.60", "-1.20", "HELD"),
    6: ("18", "24.05", "-6.05", "3.850", "-13.60", "+1.50", "UNDETERMINED"),
    7: ("19", "23.75", "-4.75", "3.696", "-11.99", "+2.49", "UNDETERMINED"),
    8: ("18", "23.85", "-5.85", "3.924", "-13.54", "+1.84", "UNDETERMINED"),
    9: ("16", "24.05", "-8.05", "3.534", "-14.98", "-1.12", "HELD"),
    10: ("17", "24.20", "-7.20", "3.745", "-14.54", "+0.14", "UNDETERMINED"),
    11: ("17", "24.20", "-7.20", "3.862", "-14.77", "+0.37", "UNDETERMINED"),
    12: ("18", "24.15", "-6.15", "3.932", "-13.86", "+1.56", "UNDETERMINED"),
    13: ("19", "24.10", "-5.10", "3.862", "-12.67", "+2.47", "UNDETERMINED"),
    14: ("18", "24.15", "-6.15", "3.774", "-13.55", "+1.25", "UNDETERMINED"),
    15: ("17", "24.50", "-7.50", "3.780", "-14.91", "-0.09", "HELD"),
    16: ("17", "24.00", "-7.00", "3.623", "-14.10", "+0.10", "UNDETERMINED"),
    17: ("16", "23.85", "-7.85", "3.345", "-14.41", "-1.29", "HELD"),
    18: ("19", "24.25", "-5.25", "4.054", "-13.20", "+2.70", "UNDETERMINED"),
    19: ("17", "24.35", "-7.35", "3.799", "-14.80", "+0.10", "UNDETERMINED"),
    20: ("17", "24.20", "-7.20", "3.493", "-14.05", "-0.35", "HELD"),
}
REVIEW_SUMMARY = dict(wf_min=16, wf_max=19, delta_min="-8.05", delta_max="-4.75", cross=15)

# the registration's SUPPORT section (a)-(g), printed beside the measured figures
SUPPORT_REG = dict(edges=752, clusters=13, kish=57.99, deff=1.636, deff_ratio=1.558, icc=0.0112, n_eff=459.5, se_iid=2.889,
                   se=3.695, mde=10.35, bar_gap=7.15, h_mc_se=0.032)

# ------------------------------------------------------------------------------------------ branch registry
REGISTERED_BRANCHES = (
    "C0.HELD", "C0.UNDETERMINED_BY_VALIDITY",
    "C1.BAND_ROBUST", "C1.BAND_MARGINAL", "C1.BAND_ONE_STREAM", "C1.BY_VALIDITY", "C1.RECORD_UNMOVED",
    "C2.PRINTED", "C2.BY_VALIDITY",
    "C3.TWO_STAGE_CROSSES_0", "C3.TWO_STAGE_BELOW_0", "C3.TWO_STAGE_ABOVE_0", "C3.BY_VALIDITY",
    "C4.PRINTED", "C4.BY_VALIDITY",
    "P1.HELD", "P1.FAILED", "P1.BY_VALIDITY",
    "P2.HELD", "P2.FAILED", "P2.BY_VALIDITY",
    "P3.HELD", "P3.FAILED", "P3.BY_VALIDITY",
    "P4.HELD", "P4.FAILED",
    "P5.NOT_SCORED", "P5.BY_VALIDITY",
    "FALSIFIER.P1_FIRED", "FALSIFIER.P1_NOT_FIRED",
    "FALSIFIER.QUALIFY", "FALSIFIER.STRENGTHEN", "FALSIFIER.NO_INSERTION", "FALSIFIER.NOT_EVALUATED",
    "PIN.REFUSED", "JOURNAL.REFUSED", "DB_CHANGED.REFUSED", "SEEDPATH.REFUSED", "WORKER_OPEN.REFUSED",
    "WRITE_ONCE.REFUSED", "STREAMS.REFUSED",
)
HITS = defaultdict(int)


def hit(branch):
    if branch not in REGISTERED_BRANCHES:
        raise SystemExit("[BRANCH] unregistered branch id %s" % branch)
    HITS[branch] += 1


def say_branch(say, branch, text):
    hit(branch)
    for line in text.split("\n"):
        say(line)


RECORD_UNMOVED = ("CERT-UNDER-FILTER C1's RECORDED VERDICT DOES NOT MOVE: C1 is HELD as registered at the registered "
                  "streams; this readout is DESCRIPTIVE and sizes its qualifier only (registration L14758-L14792).")


def record_unmoved(say):
    say_branch(say, "C1.RECORD_UNMOVED", "  " + RECORD_UNMOVED)


# ------------------------------------------------------------------------------------------ identity lines
def self_pins():
    return file_pins(os.path.abspath(__file__))


def identity_lines():
    me = self_pins(); c = CUB_POST
    return ["  script identity: cert_direction_stream.py blob:%s / sha256-lf16:%s (LF rendering; working tree %s)"
            % (me["blob"], me["lf16"], "LF" if me["crlf16"] is None else "CRLF sha256-crlf16:%s" % me["crlf16"]),
            "  EXECUTION WITNESS (imported instrument): cert_under_filter.__file__ = %s" % cub.__file__,
            "    blob:%s / sha256-lf16:%s (pinned blob:%s / sha256-lf16:%s: MATCH, hashed before and after the import);"
            " working tree %s" % (c["blob"], c["lf16"], CUB_BLOB, CUB_LF16,
                                  "LF" if c["crlf16"] is None else "CRLF sha256-crlf16:%s (record: %s)" % (c["crlf16"], CUB_CRLF16)),
            "  systematic_budget.build LF source sha16 %s (CERT's check_build_pin, pinned 128baa007a44a219)"
            % cub.check_build_pin()]


# ------------------------------------------------------------------------------------------ hygiene of the inputs
def check_journal(paths):
    for p in paths:
        j = p + "-journal"
        if os.path.exists(j) and bool(os.path.getsize(j) > 0):
            hit("JOURNAL.REFUSED")
            raise SystemExit("[JOURNAL] REFUSED: %s is non-empty (%d bytes): a hot journal means an uncommitted or "
                             "unrolled-back write; nothing is read." % (j, os.path.getsize(j)))


def fingerprint(paths):
    out = {}
    for p in paths:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 22), b""):
                h.update(chunk)
        st = os.stat(p)
        out[p] = (h.hexdigest()[:16], st.st_size, st.st_mtime_ns)
    return out


def fingerprint_lines(fp, when):
    return ["  %s: %s sha256_16 %s size %d mtime_ns %d" % (when, cub._rel(p), v[0], v[1], v[2]) for p, v in fp.items()]


def check_unchanged(before, after):
    if not bool(before == after):
        hit("DB_CHANGED.REFUSED")
        raise SystemExit("[DB-CHANGED] an input DB changed during the run: before %s after %s. Nothing is written."
                         % (before, after))


# ------------------------------------------------------------------------------------------ streams and arms
def stream_plan(streams=STREAMS):
    """The streams of record, validated: 1..200, 42 among them, each once."""
    s = tuple(streams)
    if not bool(s == tuple(range(1, N_STREAMS + 1)) and REF_STREAM in s and len(set(s)) == N_STREAMS):
        hit("STREAMS.REFUSED")
        raise SystemExit("[STREAMS] the stream plan must be s = 1..%d (the reference %d inside it, each once); got %d "
                         "streams (%s...). Refused." % (N_STREAMS, REF_STREAM, len(s), list(s)[:5]))
    return s


def arm_rowsets(S):
    """The 22 convention-A arm row sets, exactly as CERT builds them: U = prepare()'s routed rows of U's anchors (as passed
    to arm_edges in prepare()); F_A and R_A_k = run_arms()'s `by` for convention A."""
    anchors = S["anchors"]
    sets = {"U": {a: [r[1:] for r in S["u_rows"][a]] for a in anchors}}
    cv = S["conv"]["A"]
    named = [("F_A", cv["keep"])] + [("R_A_%02d" % (k + 1), d) for k, d in enumerate(cv["draws"])]
    for name, keep in named:
        sets[name] = {a: [r[1:] for r in S["u_rows"][a] if r[0] in keep] for a in anchors}
    need(tuple(sorted(sets)) == tuple(sorted(ARM_NAMES)), "arm names %s" % sorted(sets))
    return sets


def u_min(S):
    um = defaultdict(list)
    for e in S["u_edges"]:
        um[e["anchor"]].append((e["a"], e["b"]))
    return dict(um)


_W = {}


def _init_worker(rowsets, anchors, models, umin, B):
    _W.clear()
    _W.update(rowsets=rowsets, anchors=anchors, models=models, umin=umin, B=B)


def _stream_job(job):
    """One arm at one stream: CERT's arm_edges in fixed mode with the ONE knob, seed = s. Returns the conn-log witness."""
    s, name = job
    n0, o0 = len(cub.CONNECTIONS), len(cub.STACK_OPENS)
    t0 = time.time()
    edges, _ = cub.arm_edges(_W["rowsets"][name], _W["anchors"], _W["models"], u_edges=_W["umin"], B=_W["B"], seed=s)
    dt = time.time() - t0
    return (s, name, edges, dt, dict(dt=dt, pid=os.getpid(), conn_before=n0, conn_after=len(cub.CONNECTIONS),
                                                  stack_before=o0, stack_after=len(cub.STACK_OPENS), rss=_peak_rss()))


def _peak_rss():
    """Peak working set of this process in bytes (Windows psapi), or ru_maxrss on POSIX; None if unavailable."""
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
            pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            f = k32.K32GetProcessMemoryInfo
            f.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
            f.restype = wintypes.BOOL
            if f(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
                return int(pmc.PeakWorkingSetSize)
            return None
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except Exception:
        return None


def check_worker_witness(w, parent_pid):
    bad = (w["conn_after"] != w["conn_before"]) or (w["stack_after"] != w["stack_before"])
    if w["pid"] != parent_pid:
        bad = bad or w["conn_before"] != 0 or w["stack_before"] != 0
    if bool(bad):
        hit("WORKER_OPEN.REFUSED")
        raise SystemExit("[WORKER-OPEN] an arm job opened a DB or ran in a worker whose connection log is not empty: %s "
                         "(CERT's R3 (iii): the stack cache is opened exactly once, by load_real, in the parent). Refused."
                         % w)


def denominators(S):
    """Convention A's C1 denominators, by CERT's readout() C4 rule (copied: an anchor leaves if its F_A comparison graph
    disconnects or its kept rows fall below the 200-row floor). Seed-free: computed once."""
    keep = S["conv"]["A"]["keep"]
    conn = []
    for anc in S["anchors"]:
        nodes = {m for r in S["u_rows"][anc] for m in (r[1], r[2])}
        kept = [r for r in S["u_rows"][anc] if r[0] in keep]
        if bool(cub.connected(kept, nodes)) and not bool(len(kept) < cub.ANCHOR_FLOOR):
            conn.append(anc)
    est_by_anchor = defaultdict(list)
    for e in S["u_edges"]:
        k = (e["anchor"], e["a"], e["b"])
        if k in S["est_keys"]:
            est_by_anchor[e["anchor"]].append(k)
    keys_est = [k for a in conn for k in est_by_anchor[a]]
    return dict(anchors_conn=conn, est_by_anchor=dict(est_by_anchor), keys_est=keys_est,
                removed=[a for a in S["anchors"] if a not in conn])


def icc_deff(d_e_by_anchor):
    """One-way ANOVA ICC of d_e over the anchor clusters, Kish mean cluster size, DEFF = 1 + (m - 1) ICC (605675c L-d)."""
    groups = [np.asarray(v, dtype=float) for v in d_e_by_anchor if len(v)]
    k = len(groups); N = sum(len(g) for g in groups)
    if k < 2 or N <= k:
        return dict(icc=float("nan"), kish=float("nan"), deff=float("nan"))
    grand = float(np.concatenate(groups).mean())
    msb = sum(len(g) * (float(g.mean()) - grand) ** 2 for g in groups) / (k - 1)
    msw = sum(float(((g - g.mean()) ** 2).sum()) for g in groups) / (N - k)
    n0 = (N - sum(len(g) ** 2 for g in groups) / N) / (k - 1)
    den = msb + (n0 - 1) * msw
    icc = (msb - msw) / den if den > 0 else float("nan")
    kish = sum(len(g) ** 2 for g in groups) / N
    return dict(icc=icc, kish=kish, deff=1 + (kish - 1) * icc)


def stream_stats(S, den, arms, s, min_anchors=MIN_ANCHORS):
    """C1's statistic at one stream, by CERT's functions (wrong_maps, c1_stats, c1_verdict)."""
    keys = den["keys_est"]
    wm = {name: cub.wrong_maps(S, arms[name], keys) for name in ARM_NAMES}
    wrongF = wm["F_A"][0]
    wrongR = {k: [wm["R_A_%02d" % j][0][k] for j in range(1, cub.K_DRAWS + 1)] for k in keys}
    st = cub.c1_stats(den["anchors_conn"], den["est_by_anchor"], wrongF, wrongR, B=cub.CLUSTER_B, seed=cub.CLUSTER_SEED)
    v = cub.c1_verdict(len(den["anchors_conn"]), st["lo"], st["hi"], min_anchors=min_anchors)
    tiesF = wm["F_A"][3]
    d_e_by_anchor = [[(1.0 if wrongF[k] else 0.0) - sum(wrongR[k]) / cub.K_DRAWS for k in den["est_by_anchor"].get(a, [])]
                     for a in den["anchors_conn"]]
    need(abs(sum(sum(x) for x in d_e_by_anchor) - st["delta"]) < 1e-9, "sum d_e != Delta_W")
    need(abs(math.sqrt(sum(x * x for g in d_e_by_anchor for x in g)) - st["se_iid"]) < 1e-9, "SE_iid differs from CERT's")
    return dict(s=s, W_U=sum(1 for k in keys if wm["U"][0][k]), W_F=int(st["WF"]), WR=float(st["WR_mean"]),
                delta=float(st["delta"]), se=float(st["se"]), lo=float(st["lo"]), hi=float(st["hi"]), plo=float(st["plo"]),
                phi=float(st["phi"]), d_a=[float(x) for x in st["d_a"]], verdict=v, held=bool(v == "HELD"),
                n_edges=int(st["n_edges"]), n_anchors=int(st["n_anchors"]), se_iid=float(st["se_iid"]),
                deff_ratio=float(st["deff"]), ties_F=len(tiesF),
                W_F_ties_wrong=sum(1 for k in keys if wrongF[k] or k in tiesF),
                W_F_ties_excl=sum(1 for k in keys if wrongF[k] and k not in tiesF),
                ties_R_mean=float(np.mean([len(wm["R_A_%02d" % j][3]) for j in range(1, cub.K_DRAWS + 1)])),
                arm_fp={name: hashlib.sha256(repr(sorted((k, v_[1]) for k, v_ in arms[name].items())).encode()).hexdigest()[:16]
                        for name in ARM_NAMES},
                d_e_by_anchor=d_e_by_anchor)


def build_streams(S, den, streams, workers, B, min_anchors=MIN_ANCHORS, keep_arms=(REF_STREAM,), progress=True):
    """Every arm at every stream. Returns (results by stream, arms of the streams in keep_arms, worker witnesses)."""
    rowsets = arm_rowsets(S)
    umin = u_min(S)
    jobs = [(s, name) for s in streams for name in ARM_NAMES]
    parent = os.getpid()
    results, kept, pending, wit = {}, {}, defaultdict(dict), []
    t0 = time.time()

    def consume(item):
        s, name, edges, dt, w = item
        check_worker_witness(w, parent)
        wit.append(w)
        pending[s][name] = edges
        if len(pending[s]) == len(ARM_NAMES):
            arms = pending.pop(s)
            results[s] = stream_stats(S, den, arms, s, min_anchors=min_anchors)
            if s in keep_arms:
                kept[s] = arms
            if progress:
                print("    stream %3d: W_F %d mean W_R %.2f Delta_W %+.2f hi %+.2f %s (%d of %d; elapsed %.0f s)"
                      % (s, results[s]["W_F"], results[s]["WR"], results[s]["delta"], results[s]["hi"], results[s]["verdict"],
                         len(results), len(streams), time.time() - t0), file=sys.stderr, flush=True)
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                                 initargs=(rowsets, S["anchors"], S["models"], umin, B)) as ex:
            for item in ex.map(_stream_job, jobs, chunksize=1):
                consume(item)
    else:
        _init_worker(rowsets, S["anchors"], S["models"], umin, B)
        try:
            for j in jobs:
                consume(_stream_job(j))
        finally:
            _W.clear()
    need(not pending and set(results) == set(streams), "incomplete streams: %s" % sorted(set(streams) - set(results)))
    return results, kept, wit, time.time() - t0


def check_seed_path(S, kept_ref, results, streams):
    """[SEED-PATH 1] fixed-mode U at s = 42 == prepare()'s discovery U, bit for bit; [SEED-PATH 2] for EVERY one of the 22
    arms, the bootstrap-mean fingerprint is distinct across every stream (the knob moved, jointly, in every arm build)."""
    u42 = kept_ref["U"]
    disc = {(e["anchor"], e["a"], e["b"]): (e["p"], e["m"], e["s"], e["pt"]) for e in S["u_edges"]}
    same = bool(set(u42) == set(disc) and all(u42[k] == disc[k] for k in disc))
    distinct = {name: len({results[s]["arm_fp"][name] for s in streams}) for name in ARM_NAMES}
    stuck = [name for name in ARM_NAMES if distinct[name] != len(streams)]
    if not same or stuck:
        hit("SEEDPATH.REFUSED")
        raise SystemExit("[SEED-PATH] %s. Refused." % ("fixed-mode U at s = 42 differs from CERT's discovery U" if not same
                                                         else "arm(s) %s repeat across streams (distinct %s of %d): the seed did "
                                                              "not reach arm_edges in every arm build"
                                                              % (stuck, [distinct[n_] for n_ in stuck], len(streams))))
    two = ("(2) NOT TESTED at 1 stream (distinctness needs >= 2 streams)" if len(streams) < 2 else
           "(2) every one of the %d arms has a distinct bootstrap-mean fingerprint on each of the %d streams (the knob moved"
           " in every arm build)" % (len(ARM_NAMES), len(streams)))
    return ("  SEED-PATH: (1) U rebuilt at s = %d in fixed mode equals prepare()'s discovery U on all %d edges (p, m, s, point) "
            "bit for bit; %s." % (REF_STREAM, len(disc), two))


# ------------------------------------------------------------------------------------------ readout arithmetic (pure)
def fmt_stream(r):
    return dict(W_U="%d" % r["W_U"], W_F="%d" % r["W_F"], WR="%.2f" % r["WR"], delta="%+.2f" % r["delta"], se="%.3f" % r["se"],
                lo="%+.2f" % r["lo"], hi="%+.2f" % r["hi"], n_edges="%d" % r["n_edges"], n_anchors="%d" % r["n_anchors"],
                verdict=r["verdict"])


def d_a_text(r):
    """The stream's per-anchor d_a at %.2f. Each d_a = W_F,a - (sum of 20 integers) / 20 is a multiple of 0.05, so %.2f is
    EXACT; this is checked, and a value that is not refuses the print (the outcome must let C3 be recomputed)."""
    out = []
    for x in r["d_a"]:
        t = "%+.2f" % x
        need(abs(float(t) - x) < 1e-9, "d_a %r is not exact at %%.2f" % x)
        out.append(t)
    return " ".join(out)


def _nz(x):
    """The review printed Delta as %.2f (no forced sign); normalise to %+.2f for the digit comparison."""
    return x if x.startswith(("+", "-")) else "+" + x


def c0_check(results, record42=RECORD_42, review_table=REVIEW_TABLE, review_summary=REVIEW_SUMMARY, review_streams=REVIEW_STREAMS,
             ref=REF_STREAM):
    need(ref in results, "the reference stream %d is not among the results" % ref)
    f = fmt_stream(results[ref])
    leg1 = {k: (f[k], record42[k]) for k in record42}
    ok1 = bool(all(a == b for a, b in leg1.values()))
    rv = [results[s] for s in review_streams]
    wf_min = min(r["W_F"] for r in rv); wf_max = max(r["W_F"] for r in rv)
    d_min = "%+.2f" % min(r["delta"] for r in rv); d_max = "%+.2f" % max(r["delta"] for r in rv)
    cross = sum(1 for r in rv if bool(r["hi"] >= 0))
    ok2 = bool(wf_min == review_summary["wf_min"] and wf_max == review_summary["wf_max"]
               and d_min == _nz(review_summary["delta_min"]) and d_max == _nz(review_summary["delta_max"])
               and cross == review_summary["cross"])
    per = {}
    for s in review_streams:
        g = fmt_stream(results[s])
        mine = (g["W_F"], g["WR"], g["delta"], g["se"], g["lo"], g["hi"], g["verdict"])
        theirs = review_table[s]
        theirs = (theirs[0], theirs[1], _nz(theirs[2]), theirs[3], theirs[4], theirs[5], theirs[6])
        per[s] = (mine, theirs, bool(mine == theirs))
    return dict(ok=bool(ok1 and ok2), ok1=ok1, ok2=ok2, leg1=leg1, summary=(wf_min, wf_max, d_min, d_max, cross), per=per)


def held_share(results, streams):
    need(set(results) >= set(streams), "results missing streams %s" % sorted(set(streams) - set(results))[:5])
    k = sum(1 for s in streams if bool(results[s]["held"]))
    n = len(streams)
    return k, n, k / n


def wilson(k, n, z=Z):
    """Wilson score interval for k of n (95% at z = 1.96)."""
    p = k / n
    den = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / den
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / den
    return centre - half, centre + half


def wilson_half_width(p, n, z=Z):
    den = 1.0 + z * z / n
    return z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / den


def streams_for_half_width(p, target=HALF_WIDTH_TARGET, z=Z, n_max=10 ** 6):
    for n in range(1, n_max + 1):
        if bool(wilson_half_width(p, n, z) <= target):
            return n
    return None


def band(k, n):
    """C1's sizing band, integer arithmetic: h >= 0.80 robust; 0.20 <= h < 0.80 marginal; h < 0.20 one stream only."""
    if bool(100 * k >= 80 * n):
        return "ROBUST"
    if bool(100 * k >= 20 * n):
        return "MARGINAL"
    return "ONE_STREAM"


def dist(xs):
    a = np.asarray(xs, dtype=float)
    return dict(mean=float(a.mean()), sd=float(a.std(ddof=1)) if len(a) > 1 else float("nan"), sd0=float(a.std(ddof=0)),
                p025=float(np.percentile(a, 2.5)), p50=float(np.percentile(a, 50)), p975=float(np.percentile(a, 97.5)),
                lo=float(a.min()), hi=float(a.max()))


def two_stage(results, streams, reps=TWO_STAGE_REPS, seed=TWO_STAGE_SEED):
    Dm = np.array([results[s]["d_a"] for s in streams], dtype=float)
    ns, na = Dm.shape
    rng = np.random.default_rng(seed)
    si = rng.integers(0, ns, reps)
    ai = rng.integers(0, na, (reps, na))
    rep = Dm[si[:, None], ai].sum(axis=1)
    deltas = np.array([results[s]["delta"] for s in streams], dtype=float)
    need(bool(np.allclose(Dm.sum(axis=1), deltas, atol=1e-9)), "d_a rows do not sum to Delta_W")
    ses = np.array([results[s]["se"] for s in streams], dtype=float)
    within = float((ses ** 2).mean())
    between = float(deltas.var(ddof=1)) if ns > 1 else 0.0
    mix = math.sqrt(within + between)
    point = float(deltas.mean())
    return dict(point=point, plo=float(np.percentile(rep, 2.5)), phi=float(np.percentile(rep, 97.5)), mix_se=mix,
                within=within, between=between, between0=float(deltas.var(ddof=0)), rep_sd=float(rep.std(ddof=1)),
                zlo=point - Z * mix, zhi=point + Z * mix, reps=reps, seed=seed, n_streams=ns, n_anchors=na)


def in_closed(x, lo, hi):
    return bool(lo <= x <= hi)


def p1_held(k, n):
    """P1 as ruled (60ddf85, ruling (1)): HELD iff 0.18 <= h < 0.45, in integers 18 n <= 100 k < 45 n (36 <= k < 90 of
    200); FAILED otherwise, including h = 0.45 exactly (the falsifier's strict words)."""
    return bool(18 * n <= 100 * k) and bool(100 * k < 45 * n)


def p3_score(ts):
    """P3 as ruled (60ddf85, ruling (3), d7): mixture SE in [3.65, 3.90] AND the upper end of C3's PERCENTILE interval in
    [+0.2, +1.5]. point + 1.96 x mixture SE (ts["zhi"]) is printed beside and decides nothing."""
    return (in_closed(ts["mix_se"], 3.65, 3.90), in_closed(ts["phi"], 0.2, 1.5))


# ------------------------------------------------------------------------------------------ the readout (prints)
def readout(say, results, streams, S_support=None, record42=RECORD_42, review_table=REVIEW_TABLE,
            review_summary=REVIEW_SUMMARY, review_streams=REVIEW_STREAMS, ref=REF_STREAM, n_expected=N_STREAMS):
    """C0 first (pre-empting), then C1-C4, the Support lines, the predictions and the falsifier. Returns a summary."""
    need(len(streams) == n_expected and ref in streams, "readout on %d streams (expected %d, %d inside)" % (len(streams), n_expected, ref))
    c0 = c0_check(results, record42, review_table, review_summary, review_streams, ref)
    valid = c0["ok"]
    say("")
    say("=== C0: VALIDITY (first; pre-empting) ===")
    for k_, (mine, rec) in c0["leg1"].items():
        say("  stream %d %-9s %-8s (record %s)%s" % (ref, k_, mine, rec, "" if mine == rec else "   <-- DIFFERS"))
    wf_min, wf_max, d_min, d_max, cross = c0["summary"]
    say("  the review's %d streams (s = %s, recompute_seed.py ARMSEED; armseed.out): W_F %d-%d (review %d-%d); Delta_W %s to %s"
        " (review %s to %s); upper end >= 0 on %d of %d (review %d)"
        % (len(review_streams), ",".join(str(s) for s in review_streams), wf_min, wf_max, review_summary["wf_min"],
           review_summary["wf_max"], d_min, d_max, _nz(review_summary["delta_min"]), _nz(review_summary["delta_max"]), cross,
           len(review_streams), review_summary["cross"]))
    say("  beside (decides nothing, reading d3): the review's table digit by digit (W_F, mean W_R, Delta_W, SE, lo, hi, verdict):")
    for s in review_streams:
        mine, theirs, same = c0["per"][s]
        say("    s %3d  mine %s | review %s  %s" % (s, " ".join(mine), " ".join(theirs), "MATCH" if same else "DIFFERS"))
    say("  per-stream digit match: %d of %d" % (sum(1 for v in c0["per"].values() if v[2]), len(review_streams)))
    if valid:
        say_branch(say, "C0.HELD", "  -> C0 HELD: stream %d reproduces the outcome of record to the digit and the review's %d "
                                    "streams reproduce its summary." % (ref, len(review_streams)))
    else:
        say_branch(say, "C0.UNDETERMINED_BY_VALIDITY",
                   "  -> C0 NOT HELD (leg 1 %s, leg 2 %s): EVERY READOUT BELOW IS UNDETERMINED (BY VALIDITY); its numbers are\n"
                   "     printed and not read." % ("PASS" if c0["ok1"] else "FAIL", "PASS" if c0["ok2"] else "FAIL"))
    tag = "" if valid else "  [UNDETERMINED (BY VALIDITY): printed, not read]"

    # ---- C1
    k, n, h = held_share(results, streams)
    lo, hi = wilson(k, n)
    mc_se = math.sqrt(h * (1 - h) / n)
    b = band(k, n)
    say("")
    say("=== C1: THE HELD SHARE h over the %d direction streams (DESCRIPTIVE; beside CERT's C1, never replacing it)%s ===" % (n, tag))
    say("  denominator: %d streams (s = %d..%d; the reference %d is one of them, counted once; reading d1). HELD at a stream"
        % (n, min(streams), max(streams), ref))
    say("  = CERT's c1_verdict HELD (the 13-anchor interval's upper end < 0).")
    say("  h = %d / %d = %.4f | Wilson 95%% interval [%.4f, %.4f] (Monte-Carlo only: the streams are draws on the SAME data)"
        " | Monte-Carlo SE %.4f" % (k, n, h, lo, hi, mc_se))
    say("  streams HELD: %s" % (" ".join(str(s) for s in streams if results[s]["held"]) or "none"))
    if not valid:
        say_branch(say, "C1.BY_VALIDITY", "  -> band NOT READ (C0 not held): the band would be %s." % b)
    elif b == "ROBUST":
        say_branch(say, "C1.BAND_ROBUST", "  -> SIZING BAND: h >= 0.80, \"HELD, robust to the direction stream\" (the qualifier\n"
                                           "     \"MARGINAL: FLIPS ON 15/20 DIRECTION STREAMS\" was not about the stream).")
    elif b == "MARGINAL":
        say_branch(say, "C1.BAND_MARGINAL", "  -> SIZING BAND: 0.20 <= h < 0.80, \"HELD at the registered stream, MARGINAL over the "
                                             "direction stream\".")
    else:
        say_branch(say, "C1.BAND_ONE_STREAM", "  -> SIZING BAND: h < 0.20, \"HELD AT ONE STREAM ONLY\".")
    record_unmoved(say)

    # ---- C2
    dd = dist([results[s]["delta"] for s in streams]); du = dist([results[s]["hi"] for s in streams])
    dwf = dist([results[s]["W_F"] for s in streams]); dwr = dist([results[s]["WR"] for s in streams])
    dwu = dist([results[s]["W_U"] for s in streams])
    say("")
    say("=== C2: THE DISTRIBUTIONS over the %d streams (DESCRIPTIVE)%s ===" % (n, tag))
    for lab, d in (("Delta_W", dd), ("upper end", du), ("W_F", dwf), ("mean W_R", dwr), ("W_U", dwu)):
        say("  %-10s mean %+8.3f | sd %.3f (ddof 1; ddof 0 %.3f) | 2.5 / 50 / 97.5 %% %+.2f / %+.2f / %+.2f | range [%+.2f, %+.2f]"
            % (lab, d["mean"], d["sd"], d["sd0"], d["p025"], d["p50"], d["p975"], d["lo"], d["hi"]))
    say("  every W is a wrong(established) count by construction (U's established set); W_F under the tie conventions (reading"
        " r2 of CERT): ties-as-wrong mean %.2f, ties-excluded mean %.2f; F_A edges at p = 0.5 exactly: mean %.2f per stream;"
        " R: mean %.2f" % (np.mean([results[s]["W_F_ties_wrong"] for s in streams]),
                           np.mean([results[s]["W_F_ties_excl"] for s in streams]),
                           np.mean([results[s]["ties_F"] for s in streams]), np.mean([results[s]["ties_R_mean"] for s in streams])))
    say_branch(say, "C2.PRINTED" if valid else "C2.BY_VALIDITY",
               "  -> C2 printed%s." % ("" if valid else " (UNDETERMINED (BY VALIDITY))"))

    # ---- C3
    ts = two_stage(results, streams)
    say("")
    say("=== C3: THE TWO-STAGE INTERVAL (stream x %d-anchor cluster bootstrap; DESCRIPTIVE)%s ===" % (ts["n_anchors"], tag))
    say("  %d replicates (numpy default_rng(%d): a stream uniformly from the %d, then one %d-anchor cluster-bootstrap replicate"
        " of its d_a; reading d5)" % (ts["reps"], ts["seed"], ts["n_streams"], ts["n_anchors"]))
    say("  point (mean Delta_W over streams) %+.3f | percentile interval [%+.2f, %+.2f] | mixture SE = sqrt(mean within %.3f +"
        " between %.3f (ddof 1; ddof 0 %.3f)) = %.3f | beside: point +- 1.96 x mixture SE [%+.2f, %+.2f]; replicate sd %.3f"
        % (ts["point"], ts["plo"], ts["phi"], ts["within"], ts["between"], ts["between0"], ts["mix_se"], ts["zlo"], ts["zhi"],
           ts["rep_sd"]))
    if not valid:
        say_branch(say, "C3.BY_VALIDITY", "  -> C3 UNDETERMINED (BY VALIDITY): printed, not read.")
    elif bool(ts["phi"] < 0):
        say_branch(say, "C3.TWO_STAGE_BELOW_0", "  -> the two-stage percentile interval lies wholly below 0 (descriptive).")
    elif bool(ts["plo"] > 0):
        say_branch(say, "C3.TWO_STAGE_ABOVE_0", "  -> the two-stage percentile interval lies wholly above 0 (descriptive).")
    else:
        say_branch(say, "C3.TWO_STAGE_CROSSES_0", "  -> the two-stage percentile interval CONTAINS 0 (descriptive).")

    # ---- C4
    n_meas = streams_for_half_width(h)
    n_03 = streams_for_half_width(0.30); n_05 = streams_for_half_width(0.50)
    say("")
    say("=== C4: THE REFERENCE FOR FUTURE REGISTRATIONS (DESCRIPTIVE)%s ===" % tag)
    say("  Monte-Carlo SE of h = sqrt(h (1 - h) / %d) = %.4f | streams for a Wilson 95%% half-width <= %.2f: %s at the measured"
        " h %.4f; %s at h = 0.30; %s at h = 0.50 (reading d8)"
        % (n, mc_se, HALF_WIDTH_TARGET, n_meas, h, n_03, n_05))
    say("  PROPOSED (NOT ADOPTED HERE; adoption is a separate ruling): a registration whose decision counts majority signs over")
    say("  a bootstrap either integrates over >= 200 streams or pins the stream and prints h beside.")
    say_branch(say, "C4.PRINTED" if valid else "C4.BY_VALIDITY", "  -> C4 printed%s." % ("" if valid else " (UNDETERMINED (BY VALIDITY))"))

    # ---- Support
    say("")
    say("=== SUPPORT (registration (a)-(g); measured at stream %d beside the registered figures) ===" % ref)
    r42 = results[ref]
    ic = icc_deff(r42["d_e_by_anchor"])
    se_icc = r42["se_iid"] * math.sqrt(ic["deff"]) if ic["deff"] == ic["deff"] else float("nan")
    say("  (a) deciding denominator of C1 of record: %d established edges in %d anchor clusters (registered %d / %d); Kish mean"
        " cluster size %.2f (registered %.2f). The %d streams are a Monte-Carlo size on the SAME data, not new data."
        % (r42["n_edges"], r42["n_anchors"], SUPPORT_REG["edges"], SUPPORT_REG["clusters"], ic["kish"], SUPPORT_REG["kish"], n))
    say("  (b) DEFF from the cluster sizes: ANOVA ICC of d_e %.4f -> DEFF %.3f (registered ICC %.4f, DEFF %.3f); ratio form"
        " (CERT's SE^2 / SE_iid^2) %.3f (registered %.3f)" % (ic["icc"], ic["deff"], SUPPORT_REG["icc"], SUPPORT_REG["deff"],
                                                             r42["deff_ratio"], SUPPORT_REG["deff_ratio"]))
    say("  (c) n_eff = %d / %.3f = %.1f (registered %.1f)" % (r42["n_edges"], ic["deff"], r42["n_edges"] / ic["deff"], SUPPORT_REG["n_eff"]))
    say("  (d) SE_iid %.3f (registered %.3f) x sqrt(DEFF) = %.3f edges (registered %.3f); for h, the Monte-Carlo SE %.4f"
        " (registered at h = 0.30: %.3f)" % (r42["se_iid"], SUPPORT_REG["se_iid"], se_icc, SUPPORT_REG["se"], mc_se, SUPPORT_REG["h_mc_se"]))
    say("  (e) MDE at 80%% power = 2.80 x %.3f = %.2f edges against the C1 bar 0 (registered %.2f)"
        % (se_icc, 2.80 * se_icc, SUPPORT_REG["mde"]))
    say("  (f) VERDICT LINE: the recorded |Delta_W| %.2f lies %.2f from the bar, below the MDE: the direction question is"
        " DESCRIPTIVE-ONLY at this support (registered)." % (SUPPORT_REG["bar_gap"], SUPPORT_REG["bar_gap"]))
    say("  (g) STRUCTURAL: more streams shrink only the Monte-Carlo error of h and of the two-stage point; the %d-cluster"
        " sampling variance stays; DESCRIPTIVE-ONLY at any number of streams." % r42["n_anchors"])

    # ---- predictions
    say("")
    say("=== PREDICTIONS (the registrar's; scored HELD / FAILED explicitly) ===")
    if not valid:
        for pid in ("P1", "P2", "P3"):
            say_branch(say, pid + ".BY_VALIDITY", "  %s: UNDETERMINED (BY VALIDITY) - C0 not held." % pid)
    else:
        rule = "HELD iff 0.18 <= h < 0.45, i.e. %d <= k < %d of %d (registrar's ruling (1), 60ddf85)" % (
            -(-18 * n // 100), -(-45 * n // 100), n)
        if p1_held(k, n):
            say_branch(say, "P1.HELD", "  P1 h = 0.30 [0.18, 0.45]: observed %d/%d = %.4f -> HELD (%s)" % (k, n, h, rule))
        else:
            say_branch(say, "P1.FAILED", "  P1 h = 0.30 [0.18, 0.45]: observed %d/%d = %.4f -> FAILED (%s)" % (k, n, h, rule))
        p2 = (in_closed(dd["mean"], -7.0, -6.1), in_closed(dd["sd"], 0.8, 1.4), in_closed(du["p50"], -0.1, 0.9))
        sd0_same = bool(in_closed(dd["sd0"], 0.8, 1.4) == p2[1])
        txt = ("  P2 mean Delta_W %+.3f in [-7.0, -6.1]: %s | sd %.3f (ddof 1) in [0.8, 1.4]: %s%s | median upper end %+.3f in"
               " [-0.1, +0.9]: %s -> %s" % (dd["mean"], "yes" if p2[0] else "NO", dd["sd"], "yes" if p2[1] else "NO",
                                            "" if sd0_same else " (ddof 0 %.3f reads the other way: CONVENTION-SENSITIVE)" % dd["sd0"],
                                            du["p50"], "yes" if p2[2] else "NO", "HELD" if all(p2) else "FAILED"))
        say_branch(say, "P2.HELD" if all(p2) else "P2.FAILED", txt)
        p3 = p3_score(ts)
        say_branch(say, "P3.HELD" if all(p3) else "P3.FAILED",
                   "  P3 mixture SE %.3f in [3.65, 3.90]: %s | two-stage PERCENTILE upper end %+.3f in [+0.2, +1.5]: %s (lower end"
                   " %+.2f, about -13.9, printed not scored; beside, deciding nothing: point + 1.96 x mixture SE %+.3f) -> %s"
                   % (ts["mix_se"], "yes" if p3[0] else "NO", ts["phi"], "yes" if p3[1] else "NO", ts["plo"], ts["zhi"],
                      "HELD" if all(p3) else "FAILED"))
    say_branch(say, "P4.HELD" if valid else "P4.FAILED", "  P4 C0 HELD: %s" % ("HELD" if valid else "FAILED"))
    if valid:
        say_branch(say, "P5.NOT_SCORED", "  P5 streams for a Wilson half-width <= 0.05 at h near 0.3: about 320 -> %s at h = 0.30, %s at the"
                                          " measured h; NO INTERVAL REGISTERED: printed, NOT SCORED (reading d7)." % (n_03, n_meas))
    else:
        say_branch(say, "P5.BY_VALIDITY", "  P5: UNDETERMINED (BY VALIDITY) - C0 not held.")

    # ---- falsifier
    say("")
    say("=== FALSIFIER ===")
    if not valid:
        say_branch(say, "FALSIFIER.NOT_EVALUATED", "  NOT EVALUATED: C0 is not held; every readout is UNDETERMINED (BY VALIDITY).")
    else:
        if not p1_held(k, n):
            say_branch(say, "FALSIFIER.P1_FIRED", "  P1 FAILS (h %s): FIRED." % (">= 0.45" if 100 * k >= 45 * n else "< 0.18"))
        else:
            say_branch(say, "FALSIFIER.P1_NOT_FIRED", "  P1's falsifier (h >= 0.45 or h < 0.18): NOT FIRED.")
        if b == "ROBUST":
            say_branch(say, "FALSIFIER.QUALIFY", "  h >= 0.80: the recorded qualifier \"MARGINAL: FLIPS ON 15/20 DIRECTION STREAMS\" is\n"
                                                  "  QUALIFIED by insertion (the 20 were an unrepresentative subset).")
        elif b == "ONE_STREAM":
            say_branch(say, "FALSIFIER.STRENGTHEN", "  h < 0.20: the qualifier is STRENGTHENED to \"HELD AT ONE STREAM ONLY\" by insertion.")
        else:
            say_branch(say, "FALSIFIER.NO_INSERTION", "  0.20 <= h < 0.80: the recorded qualifier stands; no insertion is owed by this band.")
    say("  IN NO BRANCH does C1's recorded verdict, CERT's falsifier reading, or the L95 precondition's status change; the")
    say("  author's decision on the filtered default is informed, not taken.")
    record_unmoved(say)
    return dict(valid=valid, k=k, n=n, h=h, wilson=(lo, hi), band=b, ts=ts, dd=dd, du=du, c0=c0)


# ------------------------------------------------------------------------------------------ write-once
def write_once(path, text):
    if os.path.exists(path):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; an outcome of record is never overwritten. Refused." % path)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def header(say):
    say("=== CERT-DIRECTION-STREAM (registered 2026-09-23, commit 46889ea; docs/judge_v2_program.md L14758-L14792) ===")
    for line in identity_lines():
        say(line)
    say("  ZERO judge calls; no DB written; CERT imported UNEDITED (no attribute of it assigned); the one knob = the seed")
    say("  keyword of cert_under_filter.arm_edges, passed for U, F_A and R_A_01..R_A_%02d jointly at every stream." % cub.K_DRAWS)
    say("  readings d1-d9 (docstring): streams 1..%d with the reference %d inside (counted once); convention A only; C0 leg 2"
        " on the registration's summary; ddof 1; two-stage rng default_rng(%d); integer band edges; P1 HELD iff 36 <= k < 90"
        " of 200 and P5 NOT SCORED (registrar's rulings 60ddf85)." % (N_STREAMS, REF_STREAM, TWO_STAGE_SEED))


# ------------------------------------------------------------------------------------------ modes
def _pre_open(paths):
    cub.check_wal(paths)                       # CERT's R6: a non-empty -wal refuses before anything is opened
    check_journal(paths)                       # a non-empty -journal refuses too


def _load_and_prepare(say):
    D = cub.load_real(say)                     # the ONE open of the stack cache (mode=ro&immutable=1), in the parent
    S = cub.prepare(D, say)                    # G1-G3, U discovery at CERT's default, the R draws (Random(1000 + k))
    den = denominators(S)
    say("")
    say("--- DENOMINATORS (convention A; CERT's C4 rule, seed-free) ---")
    say("  anchors removed: %s; remaining %d of %d; established edges in C1's denominator %d"
        % (", ".join(den["removed"]) or "none", len(den["anchors_conn"]), len(S["anchors"]), len(den["keys_est"])))
    return D, S, den


def main_dry(workers):
    paths = list(cub.INPUT_DBS())
    _pre_open(paths)
    fp0 = fingerprint(paths)
    print("reserved_pool_id=%s" % cub.pool_guard.assert_pool_of_record(cub.pool_guard.MMLU_PRO_POOL), flush=True)
    L = []; say = lambda s: (L.append(s), print(s, flush=True))
    header(say)
    dry = DRY_STREAMS
    say("  --dry-run: zero calls, WRITES NOTHING; builds streams %s in full (22 arms each), reads C0's first leg (s = %d),"
        " the review's row for s = %d, and SEED-PATH (2) on 2 streams." % (", ".join(str(x) for x in dry), REF_STREAM, dry[0]))
    for line in fingerprint_lines(fp0, "before"):
        say(line)
    D, S, den = _load_and_prepare(say)
    results, kept, wit, wall = build_streams(S, den, dry, workers, S["B"])
    say("")
    say(check_seed_path(S, kept[REF_STREAM], results, dry))
    f = fmt_stream(results[REF_STREAM])
    say("  C0 leg 1 (stream %d vs the outcome of record): %s" % (REF_STREAM, "; ".join(
        "%s %s (record %s)%s" % (k_, f[k_], RECORD_42[k_], "" if f[k_] == RECORD_42[k_] else " DIFFERS") for k_ in RECORD_42)))
    g = fmt_stream(results[dry[0]])
    mine = (g["W_F"], g["WR"], g["delta"], g["se"], g["lo"], g["hi"], g["verdict"])
    t_ = REVIEW_TABLE[dry[0]]
    theirs = (t_[0], t_[1], _nz(t_[2]), t_[3], t_[4], t_[5], t_[6])
    say("  C0 leg 2, the review's row s = %d (W_F, mean W_R, Delta_W, SE, lo, hi, verdict): mine %s | review %s  %s"
        % (dry[0], " ".join(mine), " ".join(theirs), "MATCH" if mine == theirs else "DIFFERS"))
    say("  d_a at s = %d (anchor order %s): %s" % (REF_STREAM, ", ".join(den["anchors_conn"]), d_a_text(results[REF_STREAM])))
    wall = wall / len(dry)                          # per stream
    per_arm = float(np.mean([w["dt"] for w in wit]))
    n_jobs = N_STREAMS * len(ARM_NAMES)
    cpu_h = per_arm * n_jobs / 3600.0
    say("  MEASURED: %d streams x %d arm builds, %.1f s wall per stream at %d worker(s); mean %.1f s per arm build"
        " (registration's planning figure 14.4 s)." % (len(dry), len(ARM_NAMES), wall, workers, per_arm))
    say("  EXTRAPOLATION: %d streams x %d arms = %d arm builds = %.1f CPU-h; about %.2f h wall at %d worker(s) (the measured"
        " stream wall x %d: %.2f h); plus seconds for the readout." % (N_STREAMS, len(ARM_NAMES), n_jobs, cpu_h,
                                                                       cpu_h / workers, workers, N_STREAMS, wall * N_STREAMS / 3600.0))
    peaks = {}
    for w in wit:
        if w["rss"]:
            peaks[w["pid"]] = max(peaks.get(w["pid"], 0), w["rss"])
    say("  peak working set per process (RAM per worker; rule 7 needs >= 12 GB free for the window): %s"
        % (", ".join("pid %d %.0f MB" % (pid, v / 2 ** 20) for pid, v in sorted(peaks.items())) or "unavailable"))
    say("  worker witness: %d jobs, every job 0 new connections and 0 stack-cache opens; spawned workers' logs empty." % len(wit))
    cub.connection_log(say)
    fp1 = fingerprint(paths)
    for line in fingerprint_lines(fp1, "after"):
        say(line)
    check_unchanged(fp0, fp1)
    say("  DRY-RUN COMPLETE: nothing written.")


def main_run(workers):
    if os.path.exists(OUT):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; refused before computing." % OUT)
    streams = stream_plan()
    paths = list(cub.INPUT_DBS())
    _pre_open(paths)
    fp0 = fingerprint(paths)
    print("reserved_pool_id=%s" % cub.pool_guard.assert_pool_of_record(cub.pool_guard.MMLU_PRO_POOL), flush=True)
    L = ["reserved_pool_id=%s" % cub.POOL]; say = lambda s: (L.append(s), print(s, flush=True))
    header(say)
    say("  run started %s; %d worker(s)" % (time.strftime("%Y-%m-%d %H:%M:%S"), workers))
    for line in fingerprint_lines(fp0, "before"):
        say(line)
    D, S, den = _load_and_prepare(say)
    results, kept, wit, wall = build_streams(S, den, streams, workers, S["B"])
    say("")
    say("  %d streams x %d arms = %d arm builds in %.0f s wall" % (len(streams), len(ARM_NAMES), len(wit), wall))
    say(check_seed_path(S, kept[REF_STREAM], results, streams))
    say("  worker witness: %d jobs in %d process(es), every job 0 new connections and 0 stack-cache opens."
        % (len(wit), len({w["pid"] for w in wit})))
    readout(say, results, streams)
    say("")
    say("--- PER STREAM (s: W_U W_F mean_W_R Delta_W SE lo hi verdict | d_a per anchor, %.2f, exact) ---")
    say("  d_a anchor order (the %d remaining anchors, the order of c1_stats and of C3's two-stage bootstrap): %s"
        % (len(den["anchors_conn"]), ", ".join(den["anchors_conn"])))
    for s in streams:
        f = fmt_stream(results[s])
        say("  %3d: %s %s %s %s %s %s %s %s | %s" % (s, f["W_U"], f["W_F"], f["WR"], f["delta"], f["se"], f["lo"], f["hi"],
                                                   f["verdict"], d_a_text(results[s])))
    cub.connection_log(say)
    fp1 = fingerprint(paths)
    for line in fingerprint_lines(fp1, "after"):
        say(line)
    check_unchanged(fp0, fp1)
    say("  run finished %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    write_once(OUT, "\n".join(L) + "\n")
    print("[CERT-DIRECTION-STREAM] outcome written once: %s" % OUT, file=sys.stderr)


# ------------------------------------------------------------------------------------------ selftest
FIX_MODELS = ["m1_best", "m2_good", "m3_fair", "m4_poor"]
FIX_ACC = {"m1_best": 0.85, "m2_good": 0.65, "m3_fair": 0.45, "m4_poor": 0.25}
FIX = dict(seed=7, anchors=5, n_q=75, keep_tilt=0.10, agree_tilt=0.06, B=40, min_anchors=2)
FIX_STREAMS = (1, 2, 3, 4, 5, 6, 42)
FIX_REVIEW = (1, 2, 3)
# pinned fixture expectations (W_U, W_F, mean W_R, Delta_W, upper end, verdict) per stream, from the first development run
# (regenerated only by a reviewed change). Stream 42 is UNDETERMINED here while 5 of the 6 others are HELD: excluding 42
# moves h from 5/7 to 5/6, and an unvaried seed makes all 7 streams identical.
FIX_EXPECT = {1: (0, 1, "3.10", "-2.10", "-1.77", "HELD"), 2: (1, 0, "3.55", "-3.55", "-1.60", "HELD"),
              3: (0, 1, "2.40", "-1.40", "-0.68", "HELD"), 4: (2, 0, "2.55", "-2.55", "-0.93", "HELD"),
              5: (0, 0, "3.25", "-3.25", "-2.03", "HELD"), 6: (0, 1, "2.80", "-1.80", "+0.14", "UNDETERMINED"),
              42: (1, 1, "2.35", "-1.35", "+0.11", "UNDETERMINED")}
FIX_HELD = (5, 7)
DRY_STREAMS = (1, REF_STREAM)                             # the dry-run's streams (D2 of READY 751cf57): s = 1 and 42
# a two-stage fixture whose streams DIFFER in their d_a profile (READY 751cf57 D1): pinned outputs of two_stage() and dist()
TS_PIN = dict(plo=-5.200000000000001, phi=3.8500000000000005, point=0.4624999999999999, mix_se=2.092639349538324,
              between=2.9191394472361814, between0=2.90454375, rep_sd=2.0629831073130007, sd=1.7085489303020214,
              sd0=1.7042722053709614)                     # first development run; the stream-mean mutant gives [-0.55, +0.99]


def fixture(seed, anchors, n_q, keep_tilt, agree_tilt):
    """A synthetic 4-model board whose edges are near-ties: a verdict goes to the key-better model with probability
    0.5 + keep_tilt when the two predictions DISAGREE (or one is missing: the filter keeps it) and 0.5 - agree_tilt when
    they AGREE (the filter drops it). F therefore leans toward the key and R does not, by a margin comparable to the
    direction noise, so the stream decides the verdict on some streams (the flip the selftest requires)."""
    import random as _r
    rng = _r.Random(seed)
    K = defaultdict(dict); P1 = defaultdict(dict); Praw = defaultdict(dict); anchor_q = {}; pool = set(); rows = []
    mid = 0
    pairs = [(a, b) for i, a in enumerate(FIX_MODELS) for b in FIX_MODELS[i + 1:]]
    for ai in range(anchors):
        anc = "Anc%02d" % ai
        for i in range(n_q + 20):
            q = 10000 * (ai + 1) + i
            anchor_q[q] = anc; pool.add(q)
            for m in FIX_MODELS:
                ok = rng.random() < FIX_ACC[m]
                pred = "A" if ok else rng.choice("BCD")
                if rng.random() < 0.03:
                    pred = ""
                K[q][m] = int(ok); Praw[q][m] = pred; P1[q][m] = (pred or "").strip().upper()[:1]
            if i >= n_q:
                continue
            for a, b in pairs:
                mid += 1
                better, worse = (a, b) if FIX_ACC[a] > FIX_ACC[b] else (b, a)
                pa, pb = Praw[q][a], Praw[q][b]
                agree = bool(pa) and bool(pb) and pa == pb
                pbet = 0.5 - agree_tilt if agree else 0.5 + keep_tilt
                rows.append((mid, a, b, q, better if rng.random() < pbet else worse))
    return dict(models=list(FIX_MODELS), rows=rows, K=K, P1=P1, Praw=Praw, anchor_q=anchor_q, pool=pool)


def fixture_state(quiet=True):
    D = fixture(FIX["seed"], FIX["anchors"], FIX["n_q"], FIX["keep_tilt"], FIX["agree_tilt"])
    pins = cub.synth_pins(D, FIX["B"])
    sink = [].append
    S = cub.prepare(D, sink if quiet else print, pins=pins, B=FIX["B"])
    return D, S, denominators(S)


def _expect_exit(fn, prefix, what):
    try:
        fn()
    except SystemExit as e:
        need(str(e).startswith(prefix), (what, str(e)))
        return str(e)
    raise cub.CheckFailed("%s did not refuse" % what)


def _synthetic_results(k_held, n=N_STREAMS, ref=REF_STREAM, d_a_scale=1.0):
    """Hand-made per-stream results for the readout branches: the first k_held streams in a fixed order that STARTS with
    the reference are HELD. Values chosen so leg 1 / leg 2 of C0 read against the matching record dicts below."""
    order = [ref] + [s for s in range(1, n + 1) if s != ref]
    held = set(order[:k_held])
    res = {}
    for s in range(1, n + 1):
        hs = s in held
        base = -7.0 if hs else -5.0
        d_a = [base / 4.0 * d_a_scale] * 4
        se = 2.0
        delta = sum(d_a)
        res[s] = dict(s=s, W_U=26, W_F=17 if hs else 19, WR=24.0, delta=delta, se=se, lo=delta - Z * se,
                      hi=(-0.5 if hs else 0.5), plo=delta - 4, phi=delta + 4, d_a=d_a,
                      verdict="HELD" if hs else "UNDETERMINED", held=hs, n_edges=40, n_anchors=4, se_iid=1.5, deff_ratio=1.2,
                      ties_F=0, W_F_ties_wrong=17, W_F_ties_excl=17, ties_R_mean=0.0, arm_fp={nm: "%s-%d" % (nm, s) for nm in ARM_NAMES},
                      d_e_by_anchor=[[-0.5, 0.25, 0.0, -0.1], [0.1, -0.3, 0.0], [0.2, -0.2, -0.4], [0.0, 0.1, -0.6]])
    return res


def _two_stage_fixture():
    """200 streams, 13 anchors, each stream with its OWN d_a profile (so resampling from the stream-mean profile, or
    from one stream, gives a different interval): d_a_j(s) = 0.05 x (((13 s + 7 j + s j) mod 23) - 11 + (s mod 4)), SE
    1.0 + 0.1 (s mod 5)."""
    res = _synthetic_results(60)
    for s_ in res:
        d_a = [0.05 * (((13 * s_ + 7 * j + s_ * j) % 23) - 11 + (s_ % 4)) for j in range(13)]
        res[s_]["d_a"] = d_a; res[s_]["delta"] = sum(d_a); res[s_]["se"] = 1.0 + 0.1 * (s_ % 5)
    return res


def _records_for(res, review_streams, ref=REF_STREAM):
    f = fmt_stream(res[ref])
    rec = {k: f[k] for k in RECORD_42}
    table = {}
    for s in review_streams:
        g = fmt_stream(res[s])
        table[s] = (g["W_F"], g["WR"], g["delta"], g["se"], g["lo"], g["hi"], g["verdict"])
    rv = [res[s] for s in review_streams]
    summ = dict(wf_min=min(r["W_F"] for r in rv), wf_max=max(r["W_F"] for r in rv), delta_min="%+.2f" % min(r["delta"] for r in rv),
                delta_max="%+.2f" % max(r["delta"] for r in rv), cross=sum(1 for r in rv if r["hi"] >= 0))
    return rec, table, summ


def _readout_on(res, review_streams=REVIEW_STREAMS, spoil=False):
    rec, table, summ = _records_for(res, review_streams)
    if spoil:
        rec = dict(rec, W_F="99")
    L = []
    out = readout(L.append, res, tuple(range(1, N_STREAMS + 1)), record42=rec, review_table=table, review_summary=summ,
                  review_streams=review_streams)
    return out, L


def selftest():
    global OUT
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="cds_selftest_")
    OUT = os.path.join(tmp, "cert_direction_stream_outcome.txt")         # never the file of record
    real_connect = cub.sqlite3.connect
    print("[selftest] python -O: sys.flags.optimize = %d; tempdir %s; NO DB of record opened; pool guard not called"
          % (sys.flags.optimize, tmp), flush=True)
    for line in identity_lines():
        print("[selftest]" + line, flush=True)
    n_conn0 = len(cub.CONNECTIONS)

    # ---- need() raises (explicit, survives -O)
    try:
        need(False, "probe")
    except cub.CheckFailed:
        pass
    else:
        raise RuntimeError("[selftest] need(False) did not raise")

    # ---- the pins refuse a modified copy of CERT; CERT is not assigned to by this module
    cp = os.path.join(tmp, "cert_under_filter.py")
    with open(CUB_PATH, "rb") as f:
        raw = f.read()
    with open(cp, "wb") as f:
        f.write(raw + b"\n# one byte more\n")
    msg = _expect_exit(lambda: check_cub_pins(cp), "[PIN]", "a modified CERT copy")
    need(check_cub_pins(CUB_PATH) == CUB_PRE, "the real CERT file no longer matches its pins")
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    import re as _re
    assigned = _re.findall(r"^\s*cub\.[A-Za-z_][A-Za-z0-9_]*(?:\[[^\]]*\])?\s*=(?!=)", src, flags=_re.M)
    need(not assigned, "this script assigns to CERT's namespace: %s" % assigned)
    need(("setattr(" + "cub") not in src.replace(" ", ""), "setattr on CERT")
    print("[selftest] PIN: a one-line-longer CERT copy refused (%s...); the real file matches blob:%s / sha256-lf16:%s; this"
          " script assigns NO attribute of cert_under_filter (source scan: 0 assignments)" % (msg[:40], CUB_BLOB, CUB_LF16), flush=True)

    # ---- the stream plan: 1..200, 42 inside, counted once
    need(stream_plan() == tuple(range(1, 201)), "stream plan")
    need(REF_STREAM in stream_plan() and len(stream_plan()) == 200, "the reference stream is not in the plan")
    _expect_exit(lambda: stream_plan(tuple(s for s in range(1, 201) if s != 42)), "[STREAMS]", "plan without 42")
    _expect_exit(lambda: stream_plan(tuple(range(1, 202))), "[STREAMS]", "201 streams")
    print("[selftest] STREAMS: the plan is s = 1..200 with 42 inside; a plan without 42 and a 201-stream plan are refused", flush=True)

    # ---- the Wilson interval (not Wald), h's denominator, the band edges in integers
    lo, hi = wilson(60, 200)
    need(abs(lo - 0.240746) < 5e-6 and abs(hi - 0.366792) < 5e-6, "wilson(60, 200) = %r (Wald: [0.2365, 0.3635])" % ((lo, hi),))
    lo0, hi0 = wilson(0, 200)
    need(lo0 == 0.0 or abs(lo0) < 1e-12, "wilson(0, 200) lower %r" % lo0)
    need(abs(hi0 - 0.018846) < 5e-6, "wilson(0, 200) upper %r (a Wald interval would give 0)" % hi0)
    lo6, hi6 = wilson(6, 21)
    need(abs(lo6 - 0.1381) < 5e-4 and abs(hi6 - 0.4996) < 5e-4, "wilson(6, 21) = %r (the registration's [0.14, 0.50])" % ((lo6, hi6),))
    need(abs(wilson_half_width(0.3, 200) - (hi - lo) / 2) < 1e-12, "half width")
    n03 = streams_for_half_width(0.30)
    need(n03 is not None and 300 <= n03 <= 330 and wilson_half_width(0.3, n03) <= 0.05 < wilson_half_width(0.3, n03 - 1), "n* %r" % n03)
    res_only42 = _synthetic_results(1)
    k1, n1, h1 = held_share(res_only42, STREAMS)
    need(k1 == 1 and n1 == 200 and abs(h1 - 0.005) < 1e-15, "only stream 42 HELD must read h = 1/200, got %r" % ((k1, n1, h1),))
    k60, n60, h60 = held_share(_synthetic_results(60), STREAMS)
    need(k60 == 60 and n60 == 200 and abs(h60 - 0.30) < 1e-15, "h for 60 of 200: %r" % ((k60, n60, h60),))
    need([p1_held(k_, 200) for k_ in (35, 36, 89, 90)] == [False, True, True, False], "p1_held edges 35/36/89/90")
    need(all(in_closed(x, 0.2, 1.5) for x in (0.2, 1.5)), "P3 bracket closed")
    need(p3_score(dict(mix_se=3.7, phi=0.5, zhi=2.0)) == (True, True), "P3 must read the percentile upper end (in)")
    need(p3_score(dict(mix_se=3.7, phi=2.0, zhi=0.5)) == (True, False), "P3 must read the percentile upper end (out)")
    # D1 (READY 751cf57): the two-stage interval pinned on streams with different d_a profiles; ddof-1 values pinned (D3)
    tsr = _two_stage_fixture()
    ts_ = two_stage(tsr, STREAMS)
    dd_ = dist([tsr[s_]["delta"] for s_ in STREAMS])
    got_ts = dict(plo=ts_["plo"], phi=ts_["phi"], point=ts_["point"], mix_se=ts_["mix_se"], between=ts_["between"],
                  between0=ts_["between0"], rep_sd=ts_["rep_sd"], sd=dd_["sd"], sd0=dd_["sd0"])
    need(TS_PIN is not None and set(got_ts) == set(TS_PIN) and all(abs(got_ts[k_] - TS_PIN[k_]) < 1e-9 for k_ in TS_PIN),
         "two-stage fixture differs from the pin:\n got %r\n pin %r" % (got_ts, TS_PIN))
    need(abs(got_ts["between"] - got_ts["between0"]) > 1e-3 and abs(got_ts["sd"] - got_ts["sd0"]) > 1e-4, "ddof 1 vs 0 separable")
    print("[selftest] TWO-STAGE PIN: streams with distinct d_a profiles -> percentile [%+.6f, %+.6f], point %+.6f, mixture SE"
          " %.6f, between (ddof 1) %.6f (ddof 0 %.6f), sd (ddof 1) %.6f (ddof 0 %.6f): all equal the pin"
          % (got_ts["plo"], got_ts["phi"], got_ts["point"], got_ts["mix_se"], got_ts["between"], got_ts["between0"],
             got_ts["sd"], got_ts["sd0"]), flush=True)
    # D3: a review stream whose upper end is 0.0 exactly counts as CROSSING in C0 leg 2
    z0 = _synthetic_results(60)
    z0[2]["hi"] = 0.0; z0[2]["held"] = False; z0[2]["verdict"] = "UNDETERMINED"
    rz, tz, sz = _records_for(z0, (1, 2, 3))
    c0z = c0_check(z0, rz, tz, sz, (1, 2, 3))
    need(c0z["summary"][4] == sum(1 for s_ in (1, 2, 3) if z0[s_]["hi"] >= 0) and z0[2]["hi"] == 0.0
         and c0z["summary"][4] == 1, "an upper end of 0.0 must count as crossing: %r" % (c0z["summary"],))
    print("[selftest] HI == 0: a review stream with upper end 0.0 exactly counts as crossing (1 of 3: streams 1 and 3 at"
          " -0.50, stream 2 at 0.00)", flush=True)
    print("[selftest] RULING 60ddf85: p1_held at k = 35 / 36 / 89 / 90 of 200 -> FAILED / HELD / HELD / FAILED; P3 reads the"
          " PERCENTILE upper end (phi 0.5 in with zhi 2.0 out -> in; phi 2.0 out with zhi 0.5 in -> out)", flush=True)
    need(band(160, 200) == "ROBUST" and band(159, 200) == "MARGINAL" and band(40, 200) == "MARGINAL" and band(39, 200) == "ONE_STREAM",
         "band edges")
    print("[selftest] WILSON: [%.6f, %.6f] for 60/200, [0, %.6f] for 0/200 (Wald would give [0, 0]), [%.4f, %.4f] for 6/21;"
          " n* at h 0.30 = %d; h = 1/200 when only stream 42 is HELD; 60/200 = 0.30; band edges 160/159/40/39 exact"
          % (lo, hi, hi0, lo6, hi6, n03), flush=True)

    # ---- the readout branches on hand-made results: every band, P1 conflict, C0 failure; the record line in every branch
    cases = [("ROBUST", 170, False), ("MARGINAL", 60, False), ("ONE_STREAM", 10, False), ("P1 edge k = 90", 90, False),
             ("P1 edge k = 89", 89, False), ("P1 edge k = 36", 36, False), ("P1 edge k = 35", 35, False),
             ("P1 FAILED low", 30, False), ("validity failure", 60, True)]
    for label, kk, spoil in cases:
        out, L = _readout_on(_synthetic_results(kk), review_streams=(1, 2, 3), spoil=spoil)
        text = "\n".join(L)
        need(text.count(RECORD_UNMOVED) >= 2, "%s: the record-unmoved sentence printed %d times" % (label, text.count(RECORD_UNMOVED)))
        need(out["k"] == kk and out["n"] == 200, "%s: k/n %r" % (label, (out["k"], out["n"])))
        need(bool(out["valid"]) == (not spoil), "%s: validity %r" % (label, out["valid"]))
        if spoil:
            need("UNDETERMINED (BY VALIDITY)" in text and "P4 C0 HELD: FAILED" in text, label)
        if kk == 90 and not spoil:
            need("observed 90/200 = 0.4500 -> FAILED" in text and "P1 FAILS (h >= 0.45): FIRED." in text, label)
        if kk in (89, 36) and not spoil:
            need(("observed %d/200" % kk) in text and "-> HELD (HELD iff 0.18 <= h < 0.45, i.e. 36 <= k < 90" in text
                 and "NOT FIRED" in text, label)
        if kk == 35 and not spoil:
            need("observed 35/200 = 0.1750 -> FAILED" in text and "P1 FAILS (h < 0.18): FIRED." in text, label)
        print("[selftest] readout %-24s: k %3d/200, band %-10s, valid %s, record-unmoved sentence printed %d times"
              % (label, kk, out["band"], out["valid"], text.count(RECORD_UNMOVED)), flush=True)
    # a two-stage interval wholly below / above 0 (C3's other branches), and the P3 / P2 HELD branches
    below = _synthetic_results(60, d_a_scale=3.0)
    for s in below:
        below[s]["se"] = 0.1
    _readout_on(below, review_streams=(1, 2, 3))
    above = _synthetic_results(60, d_a_scale=-1.0)
    _readout_on(above, review_streams=(1, 2, 3))
    fit = _synthetic_results(60)
    for i, s in enumerate(sorted(fit)):
        dl = -6.56 + (1.06 * (1 if i % 2 else -1))
        fit[s]["d_a"] = [dl / 4.0] * 4; fit[s]["delta"] = dl; fit[s]["se"] = 3.6
        fit[s]["hi"] = 0.4 + (0.3 if i % 2 else -0.3)
    for s in fit:
        fit[s]["d_a"] = [fit[s]["delta"] / 13.0 + 0.27 * (j - 6) for j in range(13)]
    out_fit, L_fit = _readout_on(fit, review_streams=(1, 2, 3))
    print("[selftest] readout two-stage below / above 0 executed; a P2-shaped fixture: P2 %s, P3 %s"
          % ("HELD" if HITS["P2.HELD"] else "not held", "HELD" if HITS["P3.HELD"] else "not held"), flush=True)
    try:
        readout([].append, _synthetic_results(60), tuple(range(1, 201))[:-1])
    except cub.CheckFailed:
        pass
    else:
        raise cub.CheckFailed("a readout on 199 streams was admitted")

    # ---- write-once, journal, DB-changed, worker witness guards
    p = os.path.join(tmp, "x.txt")
    write_once(p, "a")
    _expect_exit(lambda: write_once(p, "b"), "[WRITE-ONCE]", "second write")
    need(open(p).read() == "a", "write-once overwrote")
    jp = os.path.join(tmp, "db.sqlite")
    open(jp, "wb").write(b"x"); open(jp + "-journal", "wb").write(b"hot")
    _expect_exit(lambda: check_journal([jp]), "[JOURNAL]", "a non-empty -journal")
    fpa = fingerprint([jp]); open(jp, "ab").write(b"y")
    _expect_exit(lambda: check_unchanged(fpa, fingerprint([jp])), "[DB-CHANGED]", "a changed DB")
    fpb = fingerprint([jp]); stb = os.stat(jp)
    open(jp, "wb").write(b"zz")                                   # same size (2 bytes), different content
    os.utime(jp, ns=(stb.st_atime_ns, stb.st_mtime_ns))           # mtime restored: only the sha can see it
    need(os.path.getsize(jp) == stb.st_size and os.stat(jp).st_mtime_ns == stb.st_mtime_ns, "rewrite fixture")
    _expect_exit(lambda: check_unchanged(fpb, fingerprint([jp])), "[DB-CHANGED]", "a same-size rewrite, mtime restored")
    fpc = fingerprint([jp]); stc = os.stat(jp)
    os.utime(jp, ns=(stc.st_atime_ns, stc.st_mtime_ns + 10 ** 9))  # touch only: same bytes, only the mtime moves
    _expect_exit(lambda: check_unchanged(fpc, fingerprint([jp])), "[DB-CHANGED]", "a touch-only change")
    _expect_exit(lambda: check_worker_witness(dict(pid=1, conn_before=0, conn_after=1, stack_before=0, stack_after=0, rss=None), 2),
                 "[WORKER-OPEN]", "a job that opened a DB")
    _expect_exit(lambda: check_worker_witness(dict(pid=1, conn_before=3, conn_after=3, stack_before=1, stack_after=1, rss=None), 2),
                 "[WORKER-OPEN]", "a worker with a non-empty log")
    check_worker_witness(dict(pid=2, conn_before=3, conn_after=3, stack_before=1, stack_after=1, rss=None), 2)
    print("[selftest] DB-CHANGED: an appended byte, a same-size rewrite with the mtime restored (sha) and a touch-only"
          " change (mtime) are each refused", flush=True)
    print("[selftest] GUARDS: write-once, -journal, DB-changed, worker open (job and spawned log) refused; parent admitted", flush=True)

    # ---- the integrated fixture: CERT's prepare() on a synthetic board, the arms at 7 streams through CERT's arm_edges
    D, S, den = fixture_state()
    need(len(den["anchors_conn"]) >= FIX["min_anchors"], "fixture anchors %r" % den)
    res1, kept1, wit1, wall1 = build_streams(S, den, FIX_STREAMS, 1, FIX["B"], min_anchors=FIX["min_anchors"], progress=False,
                                             keep_arms=FIX_STREAMS)
    # (a) this script's arms at s = 42 are CERT's own run_arms() arms, bit for bit (the job construction is CERT's)
    cert_arms = cub.run_arms(S, 1, [].append, B=FIX["B"])
    same = all(kept1[REF_STREAM][nm] == cert_arms[nm] for nm in ARM_NAMES if nm != "U")
    need(same, "this script's F_A / R_A arms at s = 42 differ from CERT's run_arms()")
    msg_seed = check_seed_path(S, kept1[REF_STREAM], res1, FIX_STREAMS)
    trig = stream_stats(S, den, kept1[1], 1, min_anchors=len(den["anchors_conn"]) + 1)
    need(bool(trig["hi"] < 0), "fixture precondition: stream 1's upper end %r must be < 0" % trig["hi"])
    need(trig["verdict"] == cub.TRIGGER_C1 and not bool(trig["held"]),
         "a stream with hi %r < 0 under the support trigger read held=%r (HELD must be c1_verdict's)" % (trig["hi"], trig["held"]))
    print("[selftest] HELD = c1_verdict: stream 1 of the fixture with hi %+.2f < 0 under the support trigger reads %s, held False"
          % (trig["hi"], trig["verdict"]), flush=True)
    # (b) the verdict flips between streams (the fixture is built for it), and the knob moved
    verdicts = {s: res1[s]["verdict"] for s in FIX_STREAMS}
    nh = sum(1 for s in FIX_STREAMS if res1[s]["held"])
    need(0 < nh < len(FIX_STREAMS), "the fixture's verdict does not flip between streams: %s" % verdicts)
    need(len({(res1[s]["W_F"], round(res1[s]["delta"], 9)) for s in FIX_STREAMS}) > 1, "every stream gives the same W_F / Delta_W")
    # (c) the pinned fixture values (regression pin)
    got = {s: (res1[s]["W_U"], res1[s]["W_F"], "%.2f" % res1[s]["WR"], "%+.2f" % res1[s]["delta"], "%+.2f" % res1[s]["hi"],
               res1[s]["verdict"]) for s in FIX_STREAMS}
    need(got == FIX_EXPECT, "fixture values differ from the pin:\n got %r\n pin %r" % (got, FIX_EXPECT))
    for s_ in FIX_STREAMS:
        need(len(d_a_text(res1[s_]).split()) == len(den["anchors_conn"]), "d_a print")
    _expect_exit_check = False
    try:
        d_a_text(dict(d_a=[0.123]))
    except cub.CheckFailed:
        _expect_exit_check = True
    need(_expect_exit_check, "a d_a not exact at %.2f was printed")
    print("[selftest] D_A PRINT: every fixture stream prints %d exact d_a values (%s at s = 42); a non-exact value refuses"
          % (len(den["anchors_conn"]), d_a_text(res1[REF_STREAM])), flush=True)
    kf, nf, hf = held_share(res1, FIX_STREAMS)
    need((kf, nf) == FIX_HELD and abs(hf - FIX_HELD[0] / FIX_HELD[1]) < 1e-15, "fixture h %r, pinned %r" % ((kf, nf), FIX_HELD))
    rec_f, tab_f, sum_f = _records_for(res1, FIX_REVIEW)
    Lf = []
    out_f = readout(Lf.append, res1, FIX_STREAMS, record42=rec_f, review_table=tab_f, review_summary=sum_f,
                    review_streams=FIX_REVIEW, n_expected=len(FIX_STREAMS))
    need(out_f["valid"] and (out_f["k"], out_f["n"]) == FIX_HELD and "\n".join(Lf).count(RECORD_UNMOVED) >= 2,
         "fixture readout %r" % ((out_f["valid"], out_f["k"], out_f["n"]),))
    print("[selftest] FIXTURE: h = %d / %d through held_share and the full readout (C0 on the fixture's own record);"
          " Wilson [%.4f, %.4f]" % (out_f["k"], out_f["n"], out_f["wilson"][0], out_f["wilson"][1]), flush=True)
    for s in FIX_STREAMS:
        print("[selftest] fixture stream %3d: W_U %d W_F %d mean W_R %s Delta_W %s hi %s %s" % ((s,) + got[s]), flush=True)
    print("[selftest] FIXTURE: %s; %d of %d streams HELD (the verdict flips); F_A and R_A_01..20 at s = 42 == CERT's run_arms()"
          " bit for bit; %d arm builds in %.1f s" % (msg_seed.strip(), nh, len(FIX_STREAMS), len(wit1), wall1), flush=True)
    # (d) the same fixture through 2 spawned workers: identical results; the workers' logs are empty (witness)
    res2, _, wit2, wall2 = build_streams(S, den, FIX_STREAMS, 2, FIX["B"], min_anchors=FIX["min_anchors"], progress=False)
    need(all(fmt_stream(res1[s]) == fmt_stream(res2[s]) and res1[s]["d_a"] == res2[s]["d_a"] for s in FIX_STREAMS),
         "2-worker results differ from 1-worker results")
    pids = {w["pid"] for w in wit2}
    need(os.getpid() not in pids and all(w["conn_before"] == 0 and w["stack_before"] == 0 for w in wit2),
         "worker witness (spawned): %s" % wit2[:2])
    print("[selftest] WORKERS: 2 spawned processes (%d pids), %d jobs, every log empty before and after; results identical to"
          " 1 worker (%.1f s)" % (len(pids), len(wit2), wall2), flush=True)
    # (e) a changed knob is caught: identical U across streams refuses [SEED-PATH]
    fake = {s: dict(res1[s], arm_fp=dict(res1[s]["arm_fp"], F_A="same")) for s in FIX_STREAMS}
    _expect_exit(lambda: check_seed_path(S, kept1[REF_STREAM], fake, FIX_STREAMS), "[SEED-PATH]", "F_A identical across streams")
    wrongU = dict(kept1[REF_STREAM]); kk_ = next(iter(wrongU["U"]))
    wrongU["U"] = dict(wrongU["U"]); wrongU["U"][kk_] = (0.123,) + tuple(wrongU["U"][kk_][1:])
    _expect_exit(lambda: check_seed_path(S, wrongU, res1, FIX_STREAMS), "[SEED-PATH]", "U at 42 differing from discovery")
    print("[selftest] SEED-PATH refusals executed: F_A identical across streams (U varied); U at 42 != discovery U", flush=True)

    # ---- no DB opened anywhere in the selftest
    need(len(cub.CONNECTIONS) == n_conn0 and not cub.STACK_OPENS, "the selftest opened a DB: %s" % cub.CONNECTIONS[n_conn0:])
    need(cub.sqlite3.connect is real_connect, "sqlite3.connect was replaced during the selftest")

    missing = [b_ for b_ in REGISTERED_BRANCHES if not HITS.get(b_)]
    print("[selftest] branch execution (registered id: times executed):")
    for b_ in REGISTERED_BRANCHES:
        print("    %-30s %d" % (b_, HITS.get(b_, 0)))
    if missing:
        raise SystemExit("[selftest] FAILED: registered branches never executed: %s" % missing)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("[selftest] PASS: %d of %d registered branches executed; tempdir removed; %.0f s"
          % (len(REGISTERED_BRANCHES), len(REGISTERED_BRANCHES), time.time() - t0), flush=True)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=1, help="processes for the arm builds (deterministic per arm and stream)")
    a = ap.parse_args(argv)
    if a.workers < 1:
        raise SystemExit("--workers must be >= 1")
    return a


if __name__ == "__main__":
    A_ = parse_args()
    cub.check_build_pin()                     # CERT's R4 (a), at launch in every mode
    if A_.selftest:
        selftest()
    elif A_.dry_run:
        main_dry(A_.workers)
    else:
        main_run(A_.workers)
