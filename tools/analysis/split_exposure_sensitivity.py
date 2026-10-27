"""SPLIT-EXPOSURE-SENSITIVITY - how much does the recorded content leak move the recorded readouts it touches, measured
against anchor-matched RANDOM removals of equal size? ZERO judge calls; no DB is written; no tree is built.

REGISTRATION OF RECORD: docs/judge_v2_program.md L14701-L14756 (heading "## Registered 2026-09-23 (before any code or
call) - SPLIT-EXPOSURE-SENSITIVITY: ..."; commit 46889ea); record docs/agents/results/SPLIT-EXPOSURE-SENSITIVITY.json.
The last bracket in the programme file wins over anything restated here.

LAUNCH SEQUENCE (registration FLOW: registration -> engine-coder (build, --selftest, --dry-run) -> adversarial-reviewer
READY -> run-operator (--run in ONE rule-7 window; a pool reader) -> adversarial-reviewer post-run -> registrar):

  python tools/analysis/split_exposure_sensitivity.py --selftest     # synthetic fixtures only; opens NO DB of record
  python tools/analysis/split_exposure_sensitivity.py --dry-run [--workers N]
                                                                     # 0 calls, WRITES NOTHING: pool id, launch pins,
                                                                     # the four exposed sets (count + sha256), input
                                                                     # fingerprints before/after, C0 of every BUILT
                                                                     # cell, measured k, the R removal sets drawn and
                                                                     # checked, the wall time of ONE null replicate,
                                                                     # RAM, the STOPPED cells
  python tools/analysis/split_exposure_sensitivity.py --run [--workers N]
                                                                     # the write-once outcome
                                                                     # experiment_results/split_exposure_sensitivity_outcome.txt

  There is no --pilot and no judge cache: the test posts nothing. --run refuses BEFORE computing if the outcome path
  exists or if ANY registered cell is not BUILT (the outcome of record is written once, complete); the file is opened
  with mode "x".

BUILD STATUS (engine-coder, 2026-09-23). ONE of the 13 registered cells is BUILT: (f) CERT-UNDER-FILTER x E74. The 12
cells of consumers (a)-(e) are STOPPED under the builder's instruction "where an original cannot be imported without side
effects (e.g. it opens a cache read-write, like stack_judge), STOP for that cell and report; do not reimplement
silently": EVERY one of their original analyze() paths opens its verdict cache READ-WRITE (sqlite3.connect(<path>) +
CREATE TABLE IF NOT EXISTS + commit), reads its other DBs mode=ro WITHOUT immutable=1 (the registration's HYGIENE
requires immutable=1), and prints its headline without returning it. They are listed in CONSUMERS below with the exact
lines; a cell becomes BUILT only by a ruling (an in-process read-only redirect of the original, as cert_under_filter's
R3 did for stack_judge, or a read-only fix of the original under its own review) and an adapter here. --run refuses
until then.
[SUPERSEDED 2026-09-23 by the registrar's ruling a4d736a (programme L14867-L14881): ROUTE (A) is ADMITTED and the 12
cells are BUILT through it; all 13 cells are BUILT and --run no longer refuses on that ground. Each original runs,
imported unedited, in ITS OWN SUBPROCESS (tools/analysis/split_exposure_child.py; A5), with sqlite3.connect redirected
for that consumer's calls only (every open file:<abs>?mode=ro&immutable=1 after the -wal / -journal check; A2), so no
write can land (a real write or a missing-table CREATE raises and the cell is UNDETERMINED (BY VALIDITY); a no-op CREATE
TABLE IF NOT EXISTS and commit are admitted; opened files fingerprinted unchanged; A3), with judge credentials stripped
and a socket guard counting and refusing any outbound connection (must be 0; A4), its pinned blob / sha256-lf16 checked at
launch and in the child (A1). The headline is CAPTURED from the original's own printed line, parsed by a pattern pinned
per consumer, exact values from its printed integers or its own locals at return (A6); the removal is applied to the
original's INPUT (an in-memory copy of its verdict cache, made from the immutable URI, the spec's DELETE applied, PRAGMA
query_only). C0 through the redirect is the execution witness (A7); the selftest carries the negative controls.]
[ADDED 2026-09-23 after the READY review f33ca79 (NOT READY at 4934a28), D1-D6: (D1) the child records a connection's
total_changes when the original CLOSES it (RUBRIC-512-SS, -R and LADDER close theirs; the READY's dry-run crashed there);
the synthetic original now closes its connection and uses a helper that opens and closes its own. (D2) READY hazards
(a)-(d) of the evidence (L14829-L14841) print in the header of --dry-run and of the outcome and beside the cells they
touch; (d) is MEASURED per cell (scored qids outside the pool; any makes the cell UNDETERMINED (BY VALIDITY)). (D3) the
child also redirects sqlite3.dbapi2.connect, and an audit hook refuses every sqlite3.connect that is not an immutable URI
or :memory: (direct Connection construction included), every open() / os.open() for writing, and process creation; any
refusal voids the cell even if the original swallows it. (D4) the audit hook refuses socket.connect at the C level (raw
_socket included) and every read of a .env file (load_env's source): the SOCKET GUARD is the enforcing control of zero
calls and the .env refusal the credential control; the environment strip is printed as descriptive. (D5) the 9 local
helper modules of the 7 originals are pinned (HELPER_PINS), checked at launch and against each child's report of the
tools/analysis modules it loaded. (D6) the dry-run prints a C0 SUMMARY and exits NONZERO unless C0 passes on every built
cell; a failure on a removal run is labelled at the REMOVAL stage (never as C0; P6 counts C0-stage failures only); the
A5 pid check runs first on every child report. DOCUMENTED LIMITS (D3): connect() keyword arguments are dropped by the
redirect (C0 is the witness); native-code writes (ctypes, C extensions) and a native socket that raises no audit event
are outside any Python-level control, and the opened-file fingerprints remain the after-the-fact backstop. Grep over the
7 originals and their 9 helpers for dbapi2 / sqlite3.Connection / _sqlite3 / apsw / _socket / subprocess / os.system /
ctypes / open(..., "w"/"a"/"x"): 0 in the 7 originals and in 7 helpers; pool_guard (export_snapshot L300, its selftest
L402-L594) and split_side (L307) carry such paths, which no analyze() path reaches and which the audit hook refuses. Directory creation (os.mkdir) is NOT refused: rubric_512.open_cache calls os.makedirs(exist_ok=True) on an
existing directory. A refused write raises the child's Refused (not an OSError), so a library that retries on
PermissionError (tempfile.mkstemp on Windows) cannot spin; tempfile.gettempdir() is resolved before the guard.]

REUSE (the recorded headline comes from the SAME code path as the original readout):
  (f) CERT-UNDER-FILTER: tools/analysis/cert_under_filter.py blob:f7d59019c3d65128687df46aebdcb798b43c3062 IMPORTED,
      NEVER EDITED (its git blob of the LF rendering is asserted at launch in every mode; a mismatch refuses). Used, by
      name: load_real (the ONE immutable open of the stack cache, its connection log and stack_judge stub stay in
      force), synth_pins, prepare (U discovery, the filter, F and the 20 R draws, gates G1-G3), _arm_job / arm_edges
      (the pinned copy of systematic_budget.build's loop; check_build_pin asserted at launch), connected, wrong_maps,
      c1_stats, c1_verdict, ANCHOR_FLOOR, K_DRAWS, PINS. The C1 composition of cert's readout() (C4's anchor removal,
      the established keys, the wrong maps, c1_stats, c1_verdict; convention A only) is the one place where this script
      composes cert's functions itself; --selftest proves it BIT-IDENTICAL to cert's own _pipeline -> readout on cert's
      synthetic fixtures: the full data, a question-reduced copy, and cert's disconnect + below-floor fixture (the C4
      removal branch).
  (a)-(e): STOPPED (see CONSUMERS: script, blob, the read-write lines).
  [SUPERSEDED 2026-09-23 by ruling a4d736a: (a)-(e) are BUILT by ROUTE (A); per consumer, split_exposure_child.ROUTE_A_SPECS
  names the module, its pinned blob and sha256-lf16, the entry called, the pinned headline patterns, the scored-set probe
  and the removal statements. The recorded outcome texts of RUBRIC-512, -SS, -R, LEAF-POWERED, LADDER, STACK-v2 and J6
  replay through those patterns and C0 to the registered headline in --selftest; STACK v1's text is untracked.]

HYGIENE (registration "HYGIENE"). First printed line: pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
(pool_guard of record blob:6521b51ac0fc). Before anything is opened, every input DB is checked for a NON-EMPTY -wal or
-journal (either REFUSES); every DB is then opened mode=ro&immutable=1 (cert's load_real; pool_guard.open_ro), and the
process connection log (cert's) must hold only immutable URIs, the stack cache exactly once, and never
snapshots_frozen.db. Size, mtime and sha256_16 of every input (DBs, routing CSV, the snapshot log, the pool id file,
the four evidence files) are printed before and after and asserted unchanged; a change refuses the write. No DB is
written. A pool reader: rule 7 (one window, no construction).

THE EXPOSED ID SETS (registration HYGIENE; the data-steward's derivation, committed by the registrar):
docs/agents/results/evidence/SPLIT-EXPOSURE_<set>.txt, one eval question_id (p2dca judgeable) per line, sorted, ASCII.
The pin is sha256 over the LF rendering (sha256-lf, 64 hex; the working tree may render CRLF); counts 28 / 70 / 14 / 74;
every id must be in the pool of record's judgeable EVAL ids (pool_guard.eval_ids). Any failure REFUSES the run: the sets
are fixed before any re-score.

READINGS FIXED BEFORE THE RUN (where the registration leaves a choice; each printed in the outcome):
  (r1) THE NULL'S QUANTILES are numpy.percentile(null, [2.5, 97.5]) with numpy's default "linear" method, over the R
       null shifts ONLY (the observed shift is never in its own null). FLAGGED iff delta < q2.5 or delta > q97.5
       (strict: a delta equal to a quantile is NOT FLAGGED). k = 0 is UNDETERMINED (BY SUPPORT); no null is drawn.
  (r2) THE OBSERVED PERCENTILE (P1, P4) is the mid-rank (#{null < delta} + 0.5 #{null == delta}) / R, exact.
  (r3) THE REMOVAL. The unit is the QUESTION. The universe is the consumer's scored set; a question's anchor is the
       consumer's own anchor (CERT: the bareq512_s42 routed anchor, cert's load_real anchor_q). A draw removes, anchor
       by anchor in sorted order, random.Random(seed).sample(sorted candidates, e_a) where the candidates are the
       anchor's scored questions NOT IN THE SET and e_a the set's scored questions there. The R draws are generated in
       the parent, in order, before any is evaluated; an anchor with fewer candidates than e_a REFUSES. Seed of cell j
       (registry order, 1..13) = NULL_SEED0 + j, printed.
  (r4) CERT END TO END. Removing a question removes its verdict rows before cert's pipeline; U, the edge set, the
       established set and the key direction are RE-DERIVED on the reduced data (the recorded readout re-run). cert's
       G1 / G2 gates are checked against cert.PINS on the full data (C0) and against the reduced data's own counts
       (cert.synth_pins; vacuous there, stated) on a reduced copy. Only convention A's F and 20 R arms are built (C1's;
       each arm_edges call seeds Random(42) itself, so they are the arms run_arms builds).
  (r5) CERT'S SHIFT is exact: Delta_W is a multiple of 1/20; Fraction(round(20 x delta), 20) is asserted within 1e-9
       of c1_stats' float and used for every comparison.
  (r6) C2 FOR CERT is its registered C1 verdict (cert.c1_verdict on the interval) with and without.
  (r7) LEAK DIRECTION (the arm whose induction corpus held the set): RUBRIC-512, -SS, -R, LEAF-POWERED: delta < 0
       (T = cell / leaf arm minus comparator); LADDER: delta > 0 (T = leaf - anchor, E14 = the ANCHOR corpora);
       STACK, STACK-v2: delta < 0 (accuracy of the exposed anchor rubric); J6: UNDEFINED (both of its arms were induced
       from the same exposed anchor corpora); CERT: toward 0 (recorded -7.15), i.e. delta > 0.
  (r8) THE FALSIFIER'S SCOREABLE CLAUSE is applied as written: a FLAG on a DESCRIPTIVE-ONLY cell (CERT among them,
       although the falsifier's parenthesis names CERT's direction) is printed descriptively and fires no [QUALIFIED]
       branch. Reported to the registrar as an ambiguity, not resolved beyond the literal reading.
  (r9) PREDICTIONS: FAILED if any SCORED constituent cell fails its clause; otherwise UNDETERMINED if any constituent is
       unscored (BY SUPPORT, BY VALIDITY, or STOPPED); otherwise HELD. P5 reads FAILED as soon as >= 2 cells FLAG.
  (r10) SUPPORT, MEASURED BESIDE THE REGISTERED LINE: null SD (ddof 1); iid SD = sqrt(k v / ((n - k)(n - 1))), v =
       (b + c) / n - d^2 (paired) or p (1 - p) (accuracy); DEFF = (null SD / iid SD)^2; n_eff = n / DEFF; MDE = 2.80 x
       null SD; Kish m = sum n_q^2 / sum n_q. The REGISTERED support word (SCOREABLE / DESCRIPTIVE-ONLY) stands; the
       measured check Delta* > MDE is printed beside. CERT: no iid form for Delta_W; the registered DEFF 1.636 (605675c)
       is printed.
  (r11) THE BOUND (structural leg): k (1 + |d|) / (n - k) (paired), k max(p, 1 - p) / (n - k) (accuracy); BOUNDED iff
       bound < Delta*. Not defined for CERT's Delta_W.

Every registered criterion, prediction and falsifier line goes through a function that records a branch id; --selftest
executes every one and fails unless all were hit (the TOPIC-PARTITION-20NG D1 / D7 rule). No computed value is
identity-tested: comparisons are wrapped in bool(). Guards raise SystemExit (never assert: python -O).
"""
import argparse, contextlib, ctypes, hashlib, io, json, math, os, pickle, random, socket, sqlite3, subprocess, sys, tempfile, time; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from collections import defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)

# cert_under_filter FIRST among project modules: it installs the process connection log and the refusing stack_judge
# stub, and refuses if a module opened a DB at import. Imported, never edited (its blob is asserted at launch).
import cert_under_filter as cuf                      # noqa: E402
import numpy as np                                   # noqa: E402
import pool_guard                                    # noqa: E402
import rubric_p8 as p8                               # noqa: E402  (already loaded by cert_under_filter)
import rejudge_grok as rj                            # noqa: E402
import rubric_512 as r512                            # noqa: E402
import split_exposure_child as sxc                   # noqa: E402  (specs and pure helpers only; the consumers run in its
                                                     #              subprocess, never here: A5)

# ------------------------------------------------------------------------------------------ constants of record
POOL = pool_guard.MMLU_PRO_POOL
OUT = os.path.join(ROOT, "experiment_results", "split_exposure_sensitivity_outcome.txt")
EVIDENCE_DIR = os.path.join(ROOT, "docs", "agents", "results", "evidence")
CERT_BLOB = "f7d59019c3d65128687df46aebdcb798b43c3062"
CERT_SHA256_LF16 = "0db2026f17b559a1"
# sha256 over the LF rendering (sha256-lf, full hex), relayed by the coordinator from the data-steward's derivation.
SETS = {
    "E28": dict(file="SPLIT-EXPOSURE_E28.txt", n=28, sha256_lf="525aad9a16e6106623cee915f2cb115c5f35a94450710aec61fd58281c287815"),
    "E70": dict(file="SPLIT-EXPOSURE_E70.txt", n=70, sha256_lf="0dfea2fcdf8af2bb35eb7a28e540f2378d5464146ac9442d619533d18a450326"),
    "E14": dict(file="SPLIT-EXPOSURE_E14.txt", n=14, sha256_lf="2b758ed2d955d409b89acb6db64a95cd3507836ee02730176aeea9723f669e6f"),
    "E74": dict(file="SPLIT-EXPOSURE_E74.txt", n=74, sha256_lf="1ca79db5764ba80d62cfabaa8c1d0b6b3980de658a22ff802c580c0b09e91bd1"),
}
R_CELLS = 1000
R_CERT = 200
NULL_SEED0 = 14701
Q_LO, Q_HI = 2.5, 97.5
MDE_K = 2.80
ALPHA_FAMILY = 0.05
CERT_MIN_ANCHORS = cuf.C1_MIN_ANCHORS
CERT_RECORDED = dict(delta="-7.15", WF="17", WR_mean="24.15", n_edges="752", n_anchors="13", interval="[-14.22, -0.08]",
                     se="3.606", verdict="HELD")
CERT_REVIEW_BASIS = ("605675c item 7 (the review's basis: 10 anchor-matched random exclusions of 69 judged qids x 5 arm"
                     " direction streams, shifts averaged over the 5 streams): exposed exclusion +0.96 against controls"
                     " -1.56 +- 1.66 (range -4.37 to +0.06); printed beside, deciding nothing")
CERT_DEFF_REGISTERED = 1.636

STOP_COMMON = ("opens its verdict cache READ-WRITE in analyze() (sqlite3.connect(<path>) + CREATE TABLE IF NOT EXISTS +"
               " commit), reads its other DBs mode=ro WITHOUT immutable=1, and prints its headline without returning it")
CONSUMERS = {
    "RUBRIC-512": dict(
        script="tools/analysis/rubric_512.py", blob="81ae1d3914b0fef5358191a8b2033f9befc142f6", entry="analyze('bareq512_s42')",
        kind="paired", recorded=dict(T_pp="+1.8", b="42", c="25", p="0.0498", n="946"),
        recorded_text="cell vs cached generic, Mistral: +1.8pp, 42:25, McNemar p 0.0498 on 946 key-decidable",
        test="cell > generic AND p8.mcn(b, c) < 0.05", leak_sign=-1,
        stop=None, route="A", rw=STOP_COMMON + ": open_cache(tree) L63-L68 on experiment_results/rubric_512/bareq512_s42.db,"
             " called at L128; rubric_value_contrast.CACHE_DB and rj.EVAL_DB mode=ro only (L72, L130)"),
    "RUBRIC-512-SS": dict(
        script="tools/analysis/rubric_512_ss.py", blob="f401668c0a2014b8d24def7882518565c26e0278", entry="analyze()",
        kind="paired", recorded=dict(T_pp="+1.0", b="35", c="26", p="0.31"),
        recorded_text="cell vs same-session generic: +1.0pp, 35:26, p 0.31",
        test="cell > fresh generic AND p8.mcn(b, c) < 0.05", leak_sign=-1, closure_band_pp=1.0,
        stop=None, route="A", rw=STOP_COMMON + ": open_cache() L31-L36 on experiment_results/rubric_512/generic_ss.db, called at"
             " L77; bareq512_s42.db, rj.EVAL_DB and r512.generic_cached mode=ro only"),
    "RUBRIC-512-R": dict(
        script="tools/analysis/rubric_512_r.py", blob="70b10af1e66f6ca52a35b9d1896d56b72db9cca4", entry="analyze()",
        kind="paired", recorded=dict(pc="0.842", pg="0.842", b="24", c="24", n="946"),
        recorded_text="reasoning judge: 0.842 = 0.842, 24:24 on 946",
        test="cell > generic AND p8.mcn(b, c) < 0.05", leak_sign=-1, closure_band_pp=1.0,
        stop=None, route="A", rw=STOP_COMMON + ": open_cache(arm) L31-L36 on grok_reasoning_cell.db and"
             " grok_reasoning_generic.db, called at L80"),
    "LEAF-POWERED": dict(
        script="tools/analysis/leaf_powered.py", blob="ca46cee930dfdae1fd02eea6d6c04a47a261ebf9", entry="analyze()",
        kind="paired", recorded=dict(T_pp="-0.3", b="9", c="7", n="786"),
        recorded_text="anchor vs leaf rubric, single order: -0.3pp, 9:7 on 786 key-decidable",
        test="leaf - anchor >= 0.02 AND p8.mcn(b, c) < 0.05", leak_sign=-1,
        stop=None, route="A", rw=STOP_COMMON + ": open_cache() L45-L50 on experiment_results/x12_crossdomain/leaf_powered.db,"
             " called at L128; ALSO imports stack_judge at module level (L22), which cert_under_filter's stub refuses in"
             " this process (STACK-JUDGE-RO-CACHE)"),
    "LADDER": dict(
        script="tools/analysis/rubric_ladder.py", blob="d94831fc534eac9cc8bd753f32cb26bb84d844cf", entry="analyze()",
        kind="paired", recorded=dict(T_pp="-0.3", b="35", c="38", p="0.68", n="967"),
        recorded_text="leaf vs anchor 35:38 on 967 fully paired key-decidable: -0.3pp, one-sided p 0.68",
        test="PRIMARY (a) leaf > anchor one-sided exact McNemar p < 0.05 AND (b) monotone; printed (a)/(b)", leak_sign=+1,
        stop=None, route="A", rw=STOP_COMMON + ": open_db() L183-L197 on experiment_results/x12_crossdomain/rubric_ladder.db,"
             " called at L334"),
    "STACK": dict(
        script="tools/analysis/stack_judge.py", blob="6acfc3195d05c160afd5c01648d9f24835703c8e", entry="analyze() PROMPT='v1'",
        kind="accuracy", recorded=dict(acc="0.843", n="944"), recorded_text="accuracy 0.843 on 944 decidable",
        test="(1) all-decidable accuracy >= 0.839", leak_sign=-1,
        stop=None, route="A", rw=STOP_COMMON + ": open_cache() L86-L91 on stack_v2.db, called at L146 (STACK-JUDGE-RO-CACHE);"
             " the module is refused in this process by cert_under_filter's stack_judge stub"),
    "STACK-v2": dict(
        script="tools/analysis/stack_judge.py", blob="6acfc3195d05c160afd5c01648d9f24835703c8e", entry="analyze() PROMPT='v2'",
        kind="accuracy", recorded=dict(acc="0.865", n="944"), recorded_text="accuracy 0.865 on 944",
        test="(1) all-decidable accuracy >= 0.839", leak_sign=-1,
        stop=None, route="A", rw=STOP_COMMON + ": open_cache() L86-L91 on stack_v2_promptv2.db, called at L146"
             " (STACK-JUDGE-RO-CACHE); refused in this process by cert_under_filter's stack_judge stub"),
    "J6": dict(
        script="tools/analysis/j6_rubrics.py", blob="a898515f4184537e4918d515258579222981f3d4", entry="analyze()",
        kind="paired", recorded=dict(T_pp="-1.8", b="23", c="40", p="0.043", n="944"),
        recorded_text="contrastive vs Mistral-induced 23:40 on 944, -1.8pp, p 0.043",
        test="contrastive > mistral_anchor AND p8.mcn(b, c) < 0.05", leak_sign=0,
        stop=None, route="A", rw=STOP_COMMON + ": open_db() L56-L62 on experiment_results/x12_crossdomain/rubric_j6.db, called"
             " at L195"),
    "CERT-UNDER-FILTER": dict(
        script="tools/analysis/cert_under_filter.py", blob=CERT_BLOB,
        entry="load_real / synth_pins / prepare / _arm_job / wrong_maps / c1_stats / c1_verdict (readout's C1 composition,"
              " convention A)",
        kind="cert", recorded=dict(CERT_RECORDED),
        recorded_text="Delta_W = 17 - 24.15 = -7.15 over 752 established edges in 13 anchors; [-14.22, -0.08] (SE 3.606);"
                      " C1 HELD",
        test="C1: 13-anchor cluster-bootstrap interval (B 2000, seed 42) wholly below 0 (cert.c1_verdict)", leak_sign=+1,
        stop=None, route="cert", rw=None),
}

# (id, consumer, set, Delta* (proportion; CERT in edges), registered support, planning bound (pp; CERT None), planning MDE)
CELL_TABLE = [
    ("a-E28", "RUBRIC-512", "E28", 0.0, "DESCRIPTIVE-ONLY", 0.87, 0.24),
    ("a-E70", "RUBRIC-512", "E70", 0.0, "DESCRIPTIVE-ONLY", 2.09, 0.38),
    ("b-E28", "RUBRIC-512-SS", "E28", 0.010, "SCOREABLE", 0.86, 0.23),
    ("b-E70", "RUBRIC-512-SS", "E70", 0.010, "SCOREABLE", 2.07, 0.36),
    ("c-E28", "RUBRIC-512-R", "E28", 0.010, "SCOREABLE", 0.85, 0.21),
    ("c-E70", "RUBRIC-512-R", "E70", 0.010, "SCOREABLE", 2.05, 0.32),
    ("d-E28", "LEAF-POWERED", "E28", 0.020, "SCOREABLE", 0.77, 0.14),
    ("d-E70", "LEAF-POWERED", "E70", 0.020, "SCOREABLE", 2.08, 0.23),
    ("e-LADDER", "LADDER", "E14", 0.020, "SCOREABLE", 0.42, 0.17),
    ("e-STACK", "STACK", "E14", 0.004, "SCOREABLE", 0.36, 0.24),
    ("e-STACKv2", "STACK-v2", "E14", 0.026, "SCOREABLE", 0.37, 0.22),
    ("e-J6", "J6", "E14", 0.001, "DESCRIPTIVE-ONLY", 0.43, 0.17),
    ("f-CERT", "CERT-UNDER-FILTER", "E74", 0.08, "DESCRIPTIVE-ONLY", None, 4.65),
]
CELL_IDS = [c[0] for c in CELL_TABLE]

# ------------------------------------------------------------------------------------------ branch registry
REGISTERED_BRANCHES = (
    "C0.PASS", "C0.UNDETERMINED_BY_VALIDITY", "C1.FLAGGED", "C1.NOT_FLAGGED", "C1.UNDETERMINED_BY_SUPPORT",
    "C1.DIR_LEAK", "C1.DIR_OPPOSITE", "C1.DIR_UNDEFINED", "C2.SAME", "C2.CHANGED", "C2.SETTLED_BY_BOUND",
    "STRUCT.BOUNDED", "STRUCT.REACHABLE", "STRUCT.UNDEFINED", "SUPPORT.SCOREABLE", "SUPPORT.DESCRIPTIVE_ONLY",
    "SUPPORT.MEASURED_AGREES", "SUPPORT.MEASURED_DISAGREES", "SUPPORT.DEFF_UNDEFINED", "CELL.STOPPED", "C3.LINE",
    "P1.HELD", "P1.FAILED", "P1.UNDETERMINED", "P2.HELD", "P2.FAILED", "P2.UNDETERMINED", "P3.HELD", "P3.FAILED",
    "P3.UNDETERMINED", "P4.HELD", "P4.FAILED", "P4.UNDETERMINED", "P5.HELD", "P5.FAILED", "P5.UNDETERMINED",
    "P6.HELD", "P6.FAILED", "P6.UNDETERMINED", "FALS.P5_FIRED", "FALS.P5_NOT_FIRED", "FALS.LEAK_QUALIFIED",
    "FALS.CLOSURE_QUALIFIED", "FALS.DESCRIPTIVE_FLAG", "FALS.NO_CONSUMER_BRANCH", "SETS.PIN_UNSET", "SETS.REFUSED",
    "SIDECAR.REFUSED", "INPUTS.CHANGED", "NULL.REFUSED", "WRITE_ONCE.REFUSED", "RUN.REFUSED_STOPPED", "C0.CERT_PASS",
    "HYGIENE.CONNLOG_REFUSED", "HAZARD.HEADER", "HAZARD.CELL", "HAZARD.D_OUTSIDE", "C0.REMOVAL_INVALID", "A5.REFUSED",
    "C0.ROUTE_PASS", "DRY.C0_SUMMARY_PASS", "DRY.C0_SUMMARY_FAIL",
)
HITS = defaultdict(int)


def hit(branch):
    if branch not in REGISTERED_BRANCHES:
        raise SystemExit("[BRANCH] unregistered branch id %s" % branch)
    HITS[branch] += 1


def need(cond, msg="check failed"):
    """Selftest / guard check: an explicit raise (python -O cannot strip it)."""
    if not bool(cond):
        raise SystemExit("[CHECK] %s" % (msg if isinstance(msg, str) else repr(msg)))


# ------------------------------------------------------------------------------------------ identities and launch pins
def lf_identity(path):
    raw = open(path, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(sha256_lf16=hashlib.sha256(lf).hexdigest()[:16], blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(),
                worktree="LF" if raw == lf else "CRLF (sha256-crlf16:%s)" % hashlib.sha256(raw).hexdigest()[:16])


def identity_lines():
    me = lf_identity(os.path.abspath(__file__)); ce = lf_identity(os.path.abspath(cuf.__file__))
    return ["  script identity: split_exposure_sensitivity.py sha256-lf16:%s blob:%s (LF rendering; working tree %s)"
            % (me["sha256_lf16"], me["blob"], me["worktree"]),
            "  imported instrument: cert_under_filter.py sha256-lf16:%s blob:%s (pinned blob:%s / sha256-lf16:%s; working"
            " tree %s)" % (ce["sha256_lf16"], ce["blob"], CERT_BLOB, CERT_SHA256_LF16, ce["worktree"]),
            "  route (A) child: split_exposure_child.py sha256-lf16:%s blob:%s (LF rendering)"
            % (sxc.lf_identity(CHILD)["sha256_lf16"], sxc.lf_identity(CHILD)["blob"])]


def check_launch():
    """Every mode: the imported cert_under_filter is the pinned, unedited file; its build() pin and scipy's Brent floor."""
    ce = lf_identity(os.path.abspath(cuf.__file__))
    if ce["blob"] != CERT_BLOB or ce["sha256_lf16"] != CERT_SHA256_LF16:
        raise SystemExit("[PIN] cert_under_filter.py is blob:%s / sha256-lf16:%s, pinned blob:%s / sha256-lf16:%s: the"
                         " registration imports the pinned instrument unedited. Refused." % (ce["blob"], ce["sha256_lf16"],
                                                                                           CERT_BLOB, CERT_SHA256_LF16))
    cuf.check_build_pin()
    cuf.check_scipy_brent()
    check_route_pins()


def check_route_pins(specs=None):
    """A1 at launch: every route (A) original is the pinned, unedited file (blob and sha256-lf16 of the LF rendering)."""
    out = []
    for consumer, spec in sorted((specs or sxc.ROUTE_A_SPECS).items()):
        path = os.path.join(spec.get("module_dir") or ORIG_DIR, spec["module"] + ".py")
        ident = sxc.lf_identity(path)
        if ident["blob"] != spec["blob"] or ident["sha256_lf16"] != spec["sha256_lf16"]:
            raise SystemExit("[A1] %s is blob:%s / sha256-lf16:%s, pinned blob:%s / sha256-lf16:%s (consumer %s). Refused."
                             % (_rel(path), ident["blob"], ident["sha256_lf16"], spec["blob"], spec["sha256_lf16"], consumer))
        out.append("  A1 %-14s %s blob:%s / sha256-lf16:%s (pinned; checked at launch)"
                   % (consumer, spec["module"] + ".py", ident["blob"], ident["sha256_lf16"]))
    if specs is None:
        for name, (blob, s16) in sorted(HELPER_PINS.items()):
            ident = sxc.lf_identity(os.path.join(ORIG_DIR, name + ".py"))
            if (ident["blob"], ident["sha256_lf16"]) != (blob, s16):
                raise SystemExit("[D5] helper %s.py is blob:%s / sha256-lf16:%s, pinned blob:%s / sha256-lf16:%s. Refused."
                                 % (name, ident["blob"], ident["sha256_lf16"], blob, s16))
            out.append("  D5 helper %-22s blob:%s / sha256-lf16:%s (pinned; checked at launch and per child)"
                       % (name + ".py", blob, s16))
    return out


# ------------------------------------------------------------------------------------------ the exposed sets
def read_set(path):
    if not os.path.isfile(path):
        hit("SETS.REFUSED")
        raise SystemExit("[SETS] evidence file missing: %s" % path)
    raw = open(path, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    try:
        txt = lf.decode("ascii")
    except UnicodeDecodeError:
        hit("SETS.REFUSED")
        raise SystemExit("[SETS] %s is not ASCII" % path)
    ids = []
    for i, line in enumerate(txt.split("\n"), 1):
        s = line.strip()
        if not s:
            continue
        if not s.isdigit():
            hit("SETS.REFUSED")
            raise SystemExit("[SETS] %s line %d is not one integer id: %r" % (path, i, line))
        ids.append(int(s))
    if len(set(ids)) != len(ids) or ids != sorted(ids):
        hit("SETS.REFUSED")
        raise SystemExit("[SETS] %s: ids must be unique and sorted ascending" % path)
    return frozenset(ids), hashlib.sha256(lf).hexdigest()


def load_sets(spec, evidence_dir, pool_ids, say):
    out = {}
    for name in sorted(spec):
        s = spec[name]
        if s["sha256_lf"] is None:
            hit("SETS.PIN_UNSET")
            raise SystemExit("[SETS] the sha256-lf pin of %s is not set; the sets are fixed and committed before any"
                             " re-score. Refused." % name)
        path = os.path.join(evidence_dir, s["file"])
        ids, sha = read_set(path)
        if len(ids) != s["n"]:
            hit("SETS.REFUSED")
            raise SystemExit("[SETS] %s has %d ids, registered %d. Refused." % (s["file"], len(ids), s["n"]))
        if sha != s["sha256_lf"]:
            hit("SETS.REFUSED")
            raise SystemExit("[SETS] %s sha256-lf %s, pinned %s. Refused." % (s["file"], sha, s["sha256_lf"]))
        outside = sorted(ids - pool_ids)
        if outside:
            hit("SETS.REFUSED")
            raise SystemExit("[SETS] %s: %d id(s) are not judgeable EVAL ids of the pool of record (first %s). Refused."
                             % (s["file"], len(outside), outside[:5]))
        say("  exposed set %s: %s, %d ids (registered %d), sha256-lf %s (pinned): all in the pool's judgeable EVAL ids"
            % (name, _rel(path), len(ids), s["n"], sha))
        out[name] = ids
    return out


# ------------------------------------------------------------------------------------------ inputs: sidecars, fingerprints
def _rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


def check_sidecars(dbs):
    """A NON-EMPTY -wal or -journal beside any input DB refuses (immutable=1 would hide the one and read the other's pages)."""
    for p in dbs:
        for suf in ("-wal", "-journal"):
            s = p + suf
            if os.path.exists(s) and bool(os.path.getsize(s) > 0):
                hit("SIDECAR.REFUSED")
                raise SystemExit("[SIDECAR] REFUSED: %s is non-empty (%d bytes); nothing is read. A failed precondition,"
                                 " never an outcome." % (s, os.path.getsize(s)))
    return [(p, ", ".join("%s %s" % (suf, ("%d bytes" % os.path.getsize(p + suf)) if os.path.exists(p + suf) else "absent")
                          for suf in ("-wal", "-journal"))) for p in dbs]


def fingerprint(paths):
    fp = {}
    for p in paths:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 22), b""):
                h.update(chunk)
        st = os.stat(p)
        fp[p] = (st.st_size, st.st_mtime_ns, h.hexdigest()[:16])
    return fp


def compare_fingerprints(before, after, say):
    changed = [p for p in before if before[p] != after.get(p)]
    for p in sorted(before):
        say("    %-70s size %d mtime_ns %d sha256_16 %s -> %s" % (_rel(p)[:70], before[p][0], before[p][1], before[p][2],
                                                                   "unchanged" if p not in changed else "CHANGED %s" % (after.get(p),)))
    if changed:
        hit("INPUTS.CHANGED")
        raise SystemExit("[INPUTS] %d input(s) changed during the run (%s): nothing is written. Refused."
                         % (len(changed), ", ".join(_rel(p) for p in changed)))


def check_connlog(conns, x12_path):
    """cert's connection log: only immutable URIs, the stack cache exactly once (cert's own check), no snapshots_frozen.db."""
    bad = [c for c in conns if "mode=ro&immutable=1" not in c or "snapshots_frozen" in c]
    if bad:
        hit("HYGIENE.CONNLOG_REFUSED")
        raise SystemExit("[HYGIENE] connection log holds a non-immutable or forbidden open: %s. Refused." % bad)
    return cuf.check_connection_log(conns, x12_path)


def rss_line():
    return sxc.rss_line()


# ------------------------------------------------------------------------------------------ the generic engine (pure)
def draw_removals(universe, exposed, e_a, R, seed):
    """(r3): R anchor-matched random removals of NON-exposed questions, e_a per anchor, anchors in sorted order."""
    rng = random.Random(seed)
    cands = {}
    for a in sorted(e_a):
        c = sorted(q for q in universe[a] if q not in exposed)
        if len(c) < e_a[a]:
            hit("NULL.REFUSED")
            raise SystemExit("[NULL] anchor %s has %d non-exposed scored questions, %d needed: an anchor-matched removal"
                             " of equal size is impossible. Refused." % (a, len(c), e_a[a]))
        cands[a] = c
    draws = []
    for _ in range(R):
        rem = set()
        for a in sorted(e_a):
            if e_a[a]:
                rem.update(rng.sample(cands[a], e_a[a]))
        draws.append(frozenset(rem))
    return draws


def check_draws(draws, universe, exposed, e_a, R):
    """Structural: exactly R draws; each removes exactly e_a scored, NON-exposed questions from every anchor."""
    need(len(draws) == R, "the null holds %d draws, registered R = %d" % (len(draws), R))
    anchor_of = {q: a for a, qs in universe.items() for q in qs}
    for i, d in enumerate(draws):
        need(not (d & exposed), "null draw %d removes an exposed question" % i)
        got = defaultdict(int)
        for q in d:
            need(q in anchor_of, "null draw %d removes a question outside the scored set" % i)
            got[anchor_of[q]] += 1
        need(all(got.get(a, 0) == n for a, n in e_a.items()) and all(a in e_a for a in got),
             "null draw %d is not anchor-matched: %s vs %s" % (i, dict(got), e_a))


def quantiles(null):
    lo, hi = np.percentile(np.array([float(v) for v in null], dtype=float), [Q_LO, Q_HI])
    return float(lo), float(hi)


def flag_word(delta, lo, hi):
    """C1 (registration): FLAGGED iff the observed shift lies OUTSIDE the null's central 95%."""
    flagged = bool(float(delta) < lo) or bool(float(delta) > hi)
    return "FLAGGED" if flagged else "NOT FLAGGED"


def midrank(delta, null):
    below = sum(1 for v in null if v < delta); ties = sum(1 for v in null if v == delta)
    return (below + 0.5 * ties) / len(null)


def direction(delta, leak_sign):
    if leak_sign == 0:
        return "UNDEFINED"
    return "LEAK" if bool((delta > 0) == (leak_sign > 0)) and bool(delta != 0) else "OPPOSITE"


def c0_mismatches(cell, st0):
    got = cell["c0"](st0)
    return [(k, got.get(k), v) for k, v in cell["recorded"].items() if got.get(k) != v]


def c0_gate(cell):
    """C0, EVALUATED FIRST, PRE-EMPTING: the recorded headline from the full scored set, to the digit. The one C0 path
    (--dry-run and evaluate_cell both call it)."""
    st0 = cell["stat"](frozenset())
    return st0, c0_mismatches(cell, st0)


def evaluate_cell(cell, exposed, R, seed, say=None):
    """One cell, in the registered order: C0 (pre-empting), k, the observed shift, the null, C1, C2, bound, support."""
    res = dict(id=cell["id"], consumer=cell["consumer"], set=cell["set"], seed=seed, R=R, status=None)
    try:
        st0, mism = c0_gate(cell)
    except CellInvalid as e:                      # route (A): the original could not be run as registered (A1-A6)
        res.update(st0=None, c0=[("validity", str(e), "a clean run of the original")], status="UNDETERMINED (BY VALIDITY)",
                   stage="C0")
        return res
    res["st0"] = st0
    res["c0"] = mism
    if mism:
        res["status"] = "UNDETERMINED (BY VALIDITY)"; res["stage"] = "C0"
        return res
    universe = cell["universe"]
    scored = set(q for qs in universe.values() for q in qs)
    exp_q = frozenset(q for q in scored if q in exposed)
    k = sum(cell["mcount"][q] for q in exp_q)
    e_a = {a: sum(1 for q in qs if q in exp_q) for a, qs in universe.items()}
    e_a = {a: n for a, n in e_a.items() if n}
    res.update(k=k, k_q=len(exp_q), e_a=e_a, n=sum(cell["mcount"][q] for q in scored), n_q=len(scored),
               kish=sum(cell["mcount"][q] ** 2 for q in scored) / max(1, sum(cell["mcount"][q] for q in scored)),
               outside=None if POOL_IDS[0] is None else len(scored - POOL_IDS[0]))
    if res["outside"]:
        res.update(status="UNDETERMINED (BY VALIDITY)", stage="ID-SPACE",
                   c0=[("id space", "%d scored qids outside the pool of record" % res["outside"], "0 (hazard (d))")])
        return res
    if k == 0:
        res["status"] = "UNDETERMINED (BY SUPPORT)"
        return res
    draws = draw_removals(universe, exposed, e_a, R, seed)
    check_draws(draws, universe, exposed, e_a, R)
    try:
        batch = cell["map"](cell["stat"], [exp_q] + draws)     # the observed removal first, then the R null removals
    except CellInvalid as e:
        res.update(removal_error=str(e), status="UNDETERMINED (BY VALIDITY)", stage="REMOVAL")
        return res
    st1, stats = batch[0], batch[1:]
    T0, T1 = cell["scalar"](st0), cell["scalar"](st1)
    delta = T1 - T0
    null = [cell["scalar"](s) - T0 for s in stats]
    need(len(null) == R, "the null holds %d shifts, registered R = %d (the observed shift is never in its own null)" % (len(null), R))
    lo, hi = quantiles(null)
    word = flag_word(delta, lo, hi)
    res.update(st1=st1, T0=T0, T1=T1, delta=delta, draws=draws, null=null, lo=lo, hi=hi, word=word,
               pct=midrank(delta, null), null_mean=float(np.mean([float(v) for v in null])),
               null_sd=float(np.std([float(v) for v in null], ddof=1)) if R > 1 else float("nan"),
               dir=direction(delta, cell["leak_sign"]), v_with=cell["verdict"](st0), v_without=cell["verdict"](st1),
               status=word)
    return res


# ------------------------------------------------------------------------------------------ generic cells (paired / accuracy)
def make_generic_cell(cid, consumer, set_id, kind, rows, recorded, verdict, leak_sign, delta_star, support, plan_bound=None,
                      plan_mde=None, closure_band_pp=None):
    """rows: paired (q, anchor, x_ok, y_ok) with T = mean(x) - mean(y); accuracy (q, anchor, ok) with T = mean(ok).
    Statistics are exact (Fraction); a removal subtracts per-question aggregates."""
    agg = defaultdict(lambda: [0, 0, 0, 0, 0])        # n, x, y, b, c  (accuracy: n, ok, 0, 0, 0)
    universe = defaultdict(set); anchor_seen = {}
    for r in rows:
        q, a = r[0], r[1]
        if anchor_seen.setdefault(q, a) != a:
            raise SystemExit("[CELL] %s: question %s carries two anchors" % (cid, q))
        universe[a].add(q)
        g = agg[q]; g[0] += 1
        if kind == "paired":
            x, y = bool(r[2]), bool(r[3])
            g[1] += x; g[2] += y; g[3] += (x and not y); g[4] += (y and not x)
        else:
            g[1] += bool(r[2])
    tot = [sum(g[i] for g in agg.values()) for i in range(5)]

    def stat(removed):
        t = list(tot)
        for q in removed:
            g = agg[q]
            for i in range(5):
                t[i] -= g[i]
        n = t[0]
        if kind == "paired":
            return dict(n=n, px=Fraction(t[1], n), py=Fraction(t[2], n), b=t[3], c=t[4], T=Fraction(t[3] - t[4], n),
                        p=p8.mcn(t[3], t[4]))
        return dict(n=n, T=Fraction(t[1], n), ok=t[1])

    def c0(st):
        d = dict(n=str(st["n"]))
        if kind == "paired":
            d.update(T_pp="%+.1f" % (100 * float(st["T"])), b=str(st["b"]), c=str(st["c"]), p="%.4f" % st["p"],
                     pc="%.3f" % float(st["px"]), pg="%.3f" % float(st["py"]))
        else:
            d.update(acc="%.3f" % float(st["T"]))
        return d
    return dict(id=cid, consumer=consumer, set=set_id, kind=kind, stat=stat, scalar=lambda st: st["T"], c0=c0,
                recorded=recorded, verdict=verdict, universe={a: sorted(v) for a, v in universe.items()},
                mcount={q: g[0] for q, g in agg.items()}, map=lambda f, xs: [f(x) for x in xs], leak_sign=leak_sign,
                delta_star=delta_star, support=support, plan_bound=plan_bound, plan_mde=plan_mde,
                closure_band_pp=closure_band_pp)


def bound_of(cell, res):
    if cell["kind"] == "paired":
        d = abs(float(res["st0"]["T"]))
        return res["k"] * (1 + d) / (res["n"] - res["k"])
    if cell["kind"] == "accuracy":
        p = float(res["st0"]["T"])
        return res["k"] * max(p, 1 - p) / (res["n"] - res["k"])
    return None


def iid_sd(cell, res):
    n, k = res["n"], res["k"]
    if cell["kind"] == "paired":
        st = res["st0"]; v = (st["b"] + st["c"]) / n - float(st["T"]) ** 2
    elif cell["kind"] == "accuracy":
        p = float(res["st0"]["T"]); v = p * (1 - p)
    else:
        return None
    return math.sqrt(k * v / ((n - k) * (n - 1))) if n > k and n > 1 else None


# ------------------------------------------------------------------------------------------ the CERT cell (imported path)
def _quiet(_s):
    return None


def cert_c1(S, arms, min_anchors):
    """cert_under_filter.readout()'s C1 composition, convention A: C4's anchor removal (disconnected OR below the 200-row
    floor), U's established keys of the remaining anchors, wrong maps per arm (cert.wrong_maps), cert.c1_stats and
    cert.c1_verdict. Proven bit-identical to readout() by --selftest."""
    est_by_anchor = defaultdict(list)
    for e in S["u_edges"]:
        k = (e["anchor"], e["a"], e["b"])
        if k in S["est_keys"]:
            est_by_anchor[e["anchor"]].append(k)
    conn = {}
    for anc in S["anchors"]:
        nodes = {m for r in S["u_rows"][anc] for m in (r[1], r[2])}
        kept = [r for r in S["u_rows"][anc] if r[0] in S["conv"]["A"]["keep"]]
        conn[anc] = bool(cuf.connected(kept, nodes)) and not bool(len(kept) < cuf.ANCHOR_FLOOR)
    anchors_conn = [a for a in S["anchors"] if conn[a]]
    keys_est = [k for a in anchors_conn for k in est_by_anchor[a]]
    wF = cuf.wrong_maps(S, arms["F_A"], keys_est)[0]
    wRs = [cuf.wrong_maps(S, arms["R_A_%02d" % j], keys_est)[0] for j in range(1, cuf.K_DRAWS + 1)]
    wrongR = {k: [w[k] for w in wRs] for k in keys_est}
    st = cuf.c1_stats(anchors_conn, est_by_anchor, wF, wrongR)
    v = cuf.c1_verdict(len(anchors_conn), st["lo"], st["hi"], min_anchors=min_anchors)
    exact = Fraction(int(round(20 * st["delta"])), 20) if cuf.K_DRAWS == 20 else None
    need(exact is not None and abs(float(exact) - st["delta"]) < 1e-9, "Delta_W %r is not a multiple of 1/20" % st["delta"])
    return dict(T=exact, delta=st["delta"], WF=st["WF"], WR_mean=st["WR_mean"], n_edges=st["n_edges"],
                n_anchors=st["n_anchors"], lo=st["lo"], hi=st["hi"], se=st["se"], verdict=v,
                removed_anchors=[a for a in S["anchors"] if not conn[a]], n_rows=sum(len(v_) for v_ in S["u_rows"].values()))


def cert_stat(D, removed, B, min_anchors, pins=None):
    """The recorded readout re-run on D minus the verdict rows of `removed` (reading r4). pins None = the reduced data's
    own counts (cert.synth_pins); the full real data passes cert.PINS (the record's gates)."""
    rows = [r for r in D["rows"] if r[3] not in removed] if removed else D["rows"]
    D2 = dict(D, rows=rows)
    S = cuf.prepare(D2, _quiet, pins=pins if pins is not None else cuf.synth_pins(D2, B), B=B)
    u_min = defaultdict(list)
    for e in S["u_edges"]:
        u_min[e["anchor"]].append((e["a"], e["b"]))
    cv = S["conv"]["A"]
    arms = {}
    for name, keep in [("F_A", cv["keep"])] + [("R_A_%02d" % (k + 1), d) for k, d in enumerate(cv["draws"])]:
        by = {a: [r[1:] for r in S["u_rows"][a] if r[0] in keep] for a in S["anchors"]}
        nm, edges, _ = cuf._arm_job((name, by, S["anchors"], S["models"], dict(u_min), B))
        arms[nm] = edges
    return cert_c1(S, arms, min_anchors)


_W = {}


def _cert_init(D, B, min_anchors):
    _W.update(D=D, B=B, m=min_anchors)


def _cert_job(removed):
    return cert_stat(_W["D"], removed, _W["B"], _W["m"])


def cert_mapper(D, B, min_anchors, workers):
    def m(_f, removals):
        if workers <= 1:
            return [cert_stat(D, r, B, min_anchors) for r in removals]
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers, initializer=_cert_init, initargs=(D, B, min_anchors)) as ex:
            return list(ex.map(_cert_job, removals))
    return m


def cert_c0_fields(st):
    return dict(delta="%+.2f" % st["delta"], WF=str(st["WF"]), WR_mean="%.2f" % st["WR_mean"], n_edges=str(st["n_edges"]),
                n_anchors=str(st["n_anchors"]), interval="[%+.2f, %+.2f]" % (st["lo"], st["hi"]), se="%.3f" % st["se"],
                verdict=st["verdict"])


def make_cert_cell(D, B, min_anchors, workers, recorded, full_pins, delta_star=0.08, support="DESCRIPTIVE-ONLY"):
    """The CERT cell: universe = the verdict rows in U's anchors (cert's routed anchor_q), clustered by question."""
    by = defaultdict(set); mcount = defaultdict(int)
    for r in D["rows"]:
        q = r[3]
        if q in D["anchor_q"]:
            by[D["anchor_q"][q]].add(q); mcount[q] += 1
    floor_anchors = {a for a in by if sum(mcount[q] for q in by[a]) >= cuf.ANCHOR_FLOOR}
    universe = {a: sorted(by[a]) for a in sorted(floor_anchors)}
    full = {}

    def stat(removed):
        if not removed:
            if "st" not in full:
                full["st"] = cert_stat(D, frozenset(), B, min_anchors, pins=full_pins)
            return full["st"]
        return cert_stat(D, removed, B, min_anchors)
    return dict(id="f-CERT", consumer="CERT-UNDER-FILTER", set="E74", kind="cert", stat=stat, scalar=lambda st: st["T"],
                c0=cert_c0_fields, recorded=recorded, verdict=lambda st: st["verdict"], universe=universe,
                mcount={q: mcount[q] for qs in universe.values() for q in qs}, map=cert_mapper(D, B, min_anchors, workers),
                leak_sign=+1, delta_star=delta_star, support=support, plan_bound=None, plan_mde=4.65, closure_band_pp=None)


# ------------------------------------------------------------------------------------------ ROUTE (A) cells (ruling a4d736a)
CHILD = os.path.join(HERE, "split_exposure_child.py")
# D5 (READY f33ca79): the local tools/analysis modules the 7 originals import (their closure, measured one fresh process
# per original), pinned: blob / sha256-lf16 of the LF rendering; checked at launch and against every child's report.
HELPER_PINS = {
    "judge_free_tests": ("9307ca718126af88f8da341dc09fd7989cba7f7d", "b9dfbfbe62a8598b"),
    "pool_guard": ("6521b51ac0fce04063563f9e6dcf42554ad86591", "8ca50c0fba9b8ce3"),
    "prompt_v2": ("52b369657f968b5dde2540fc405ac7f4720ed94c", "878941634b5bfc6b"),
    "rejudge_grok": ("939de7c7e31af6c2e2e1c02c4a37cef3b25366c5", "685aa7584bf09cf1"),
    "rejudge_reasoning": ("1339592ae5205d6d93cdb1f38b8936b819e24d87", "fbe6569f0c05e97e"),
    "rejudge_reference": ("7640f80027f5f06cad8eb7f27c9256029fcf2e19", "e992f299cc32ad6c"),
    "rubric_p8": ("2eda08ff635616e298947579d5c191c5a7b02441", "d8e6a089446ebf45"),
    "rubric_value_contrast": ("9e1541a7bdf1260268c850ccac81db4570c064e4", "adc15a4a89454038"),
    "split_side": ("05224b5a4b76e74353bc3931ec69f0b14f0e340b", "19501df01e3d6285"),
}

# D2 (READY f33ca79): the four READY hazards of the evidence (programme L14829-L14841), printed in the header and beside
# the cells they touch.
HAZARDS = [
    ("a", ("e-LADDER", "e-STACK", "e-STACKv2", "e-J6", "f-CERT"),
     "E14 is a REPRODUCTION of the ladder's 150-per-anchor cap draw (rubric_ladder SEED_CORPUS 556, Random(556) in rowid"
     " order) with NO logged corpus as a witness; the 45 twins before the cap do not depend on the draw"),
    ("b", ("f-CERT",),
     "internal-node labelling was NOT reproduced (seeded, unreproduced): E74 still contains ALL of E70; the internal-node"
     " exposure is not separable"),
    ("c", ("a-E28", "b-E28", "c-E28", "d-E28"),
     "E28 relies on the saved members equalling the members at induction time, witnessed by the 17 / 17 [JUDGE-LEAK] log"
     " lines the corpus model reproduces"),
    ("d", tuple(c[0] for c in CELL_TABLE),
     "any consumer keyed on another id space must CONVERT THROUGH THE OPTIONS KEY, never by question text (CONTEXT.md rule"
     " 6); every consumer here is keyed on eval question_id, and the ids outside the pool are MEASURED per cell (a cell with"
     " any is UNDETERMINED (BY VALIDITY))"),
]
ID_KEY = {"RUBRIC-512": "verdicts.qid (eval question_id)", "RUBRIC-512-SS": "verdicts.qid via match_history (eval question_id)",
          "RUBRIC-512-R": "match_history.eval_question_id", "LEAF-POWERED": "schedule.qid (eval question_id)",
          "LADDER": "match_history.eval_question_id", "STACK": "verdicts.qid (eval question_id)",
          "STACK-v2": "verdicts.qid (eval question_id)", "J6": "verdicts.qid (eval question_id)",
          "CERT-UNDER-FILTER": "verdicts.qid (eval question_id; cert.load_real)"}
POOL_IDS = [None]             # the pool's judgeable EVAL ids, loaded by prepare_real (None in the selftest unless set)


def hazards_header(say):
    hit("HAZARD.HEADER")
    say("  READY HAZARDS of the evidence (programme L14829-L14841; READY f33ca79 D2), carried beside the cells they touch:")
    for h, cells_, text in HAZARDS:
        say("    (%s) %s [cells: %s]" % (h, text, ", ".join(cells_) if h != "d" else "all 13"))


def hazard_lines(say, cell, res):
    for h, cells_, text in HAZARDS:
        if cell["id"] in cells_ and h != "d":
            say("  HAZARD (%s): %s" % (h, text))
    if res.get("outside") is None:
        say("  HAZARD (d): id space %s; ids outside the pool: not measured (no pool loaded)"
            % ID_KEY.get(cell["consumer"], "eval question_id"))
    else:
        say("  HAZARD (d): id space %s; %d of %d scored qids outside the pool of record (joined by eval question_id,"
            " never by text)" % (ID_KEY.get(cell["consumer"], "eval question_id"), res["outside"], res["n_q"]))
    hit("HAZARD.CELL")
ORIG_DIR = os.path.dirname(os.path.abspath(cuf.__file__))   # the originals of record live beside cert_under_filter.py


class CellInvalid(Exception):
    """A route (A) cell cannot be scored: a refused write, a call attempt, a headline not captured, a removal that did not
    act exactly on the scored set, an anchor ambiguity. The cell is UNDETERMINED (BY VALIDITY); the others proceed."""


def spawn_children(consumer, spec, set_chunks, probe, tmp, socket_guard=True):
    """A5: one subprocess per consumer job (chunks of the same consumer may run in parallel, each its own process); A4:
    the child's environment has every judge credential removed. Returns the child reports in chunk order."""
    procs = []
    env = sxc.clean_env(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    for i, sets in enumerate(set_chunks):
        tag = "%s_%d_%d_%d" % (consumer.replace("-", "_"), os.getpid(), int(time.time() * 1e6) % 10 ** 9, i)
        jf = os.path.join(tmp, "job_%s.json" % tag); of = os.path.join(tmp, "res_%s.json" % tag)
        with open(jf, "w", encoding="utf-8") as f:
            json.dump(dict(consumer=consumer, spec=spec, sets=sets, probe=probe, socket_guard=socket_guard,
                           helper_dir=ORIG_DIR), f)
        procs.append((_launch(jf, of, env), of))
    out = []
    for p, of in procs:
        so, se = p.communicate()
        if p.returncode != 0 or not os.path.exists(of):
            raise CellInvalid("the consumer child exited %d: %s" % (p.returncode, (se or so)[-600:]))
        res = json.load(open(of, encoding="utf-8"))
        if bool(res["pid"] == os.getpid()):                  # A5, checked FIRST, before anything the report says
            hit("A5.REFUSED")
            raise SystemExit("[A5] the consumer %s ran in the parent process (pid %d); refused" % (consumer, res["pid"]))
        out.append(res)
    for res in out:
        if res.get("sidecar"):
            hit("SIDECAR.REFUSED")
            raise SystemExit("%s (consumer %s). Refused: a failed precondition, never an outcome." % (res["sidecar"], consumer))
    return out


def _launch(jf, of, env):
    """A5: the consumer child is a separate interpreter process."""
    return subprocess.Popen([sys.executable, CHILD, "--job", jf, "--out", of], env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)


def check_local_modules(mods):
    """D5: every tools/analysis module loaded in a child is a pinned original or a pinned helper, unchanged."""
    pins = dict(HELPER_PINS)
    pins.update({sp["module"]: (sp["blob"], sp["sha256_lf16"]) for sp in sxc.ROUTE_A_SPECS.values()})
    bad = []
    for name, ident in sorted(mods.items()):
        if name not in pins:
            bad.append("%s (unpinned)" % name)
        elif (ident["blob"], ident["sha256_lf16"]) != pins[name]:
            bad.append("%s (blob:%s / sha256-lf16:%s, pinned %s / %s)" % (name, ident["blob"], ident["sha256_lf16"],
                                                                          pins[name][0], pins[name][1]))
    return bad


def validate_child(res, n_sets):
    """A1-A4 and A6 on one child report: any failure makes the cell UNDETERMINED (BY VALIDITY)."""
    if res.get("error"):
        raise CellInvalid(res["error"])
    if res["secrets_left"]:
        raise CellInvalid("[A4] credentials in the child's environment: %s" % res["secrets_left"])
    if bool(res["attempts"] != 0):
        raise CellInvalid("[A4] %d outbound connection attempt(s) refused in the child: %s" % (res["attempts"], res["attempt_log"]))
    if res.get("refusals"):
        raise CellInvalid("[A3/A4] %d operation(s) refused in the child (even if the original swallowed them): %s"
                          % (len(res["refusals"]), res["refusals"][:4]))
    bad = check_local_modules(res.get("local_modules") or {})
    if bad:
        raise CellInvalid("[A1/D5] local modules loaded in the child are not the pinned files: %s" % bad)
    if res["fp_changed"]:
        raise CellInvalid("[A3] opened files changed during the consumer's call: %s" % res["fp_changed"])
    if bool(len(res["results"]) != n_sets):
        raise CellInvalid("the child returned %d results for %d removal sets" % (len(res["results"]), n_sets))
    for r in res["results"]:
        if r["error"]:
            raise CellInvalid(r["error"])


def route_stat(spec, r):
    """The statistic from the ORIGINAL's captured headline (A6): a paired difference sign x (b - c) / n from its printed
    integers (the printed difference is rounded; b, c, n are exact); an accuracy from the original's own local `acc` at
    its return, cross-checked against the printed value."""
    p = r["parsed"]
    verdict = "/".join(p[v] for v in spec["verdict"])
    if spec["kind"] == "paired":
        b, c, n = int(p[spec["stat"]["b"]]), int(p[spec["stat"]["c"]]), int(p[spec["stat"]["n"]])
        return dict(T=Fraction(spec["stat"]["sign"] * (b - c), n), n=n, b=b, c=c, p=float(p["p"]) if "p" in p else None,
                    parsed=p, verdict=verdict, removed_rows=r.get("removed_rows"))
    acc, n = r["ret"].get(spec["stat"]["acc_local"]), r["ret"].get(spec["stat"]["n_local"])
    if acc is None or n is None:
        raise CellInvalid("[A6] the original's locals %s / %s were not captured at its return" % (spec["stat"]["acc_local"], spec["stat"]["n_local"]))
    k = int(round(acc * n))
    if bool(abs(k / n - acc) > 1e-12) or "%.3f" % acc != p["acc"] or bool(int(p["n"]) != n):
        raise CellInvalid("[A6] captured acc %r / n %r disagree with the printed headline %s / %s" % (acc, n, p["acc"], p["n"]))
    return dict(T=Fraction(k, n), n=n, ok=k, parsed=p, verdict=verdict, removed_rows=r.get("removed_rows"))


def _tpp(st):
    return "%+.1f" % (100 * float(st["T"]))


C0_ROUTE = {
    "RUBRIC-512": lambda st: dict(T_pp=_tpp(st), b=str(st["b"]), c=str(st["c"]), p=st["parsed"]["p"], n=str(st["n"])),
    "RUBRIC-512-SS": lambda st: dict(T_pp=_tpp(st), b=str(st["b"]), c=str(st["c"]), p="%.2f" % st["p"], n=str(st["n"])),
    "RUBRIC-512-R": lambda st: dict(pc=st["parsed"]["pc"], pg=st["parsed"]["pg"], b=str(st["b"]), c=str(st["c"]), n=str(st["n"])),
    "LEAF-POWERED": lambda st: dict(T_pp=_tpp(st), b=str(st["b"]), c=str(st["c"]), n=str(st["n"])),
    "LADDER": lambda st: dict(T_pp=_tpp(st), b=str(st["b"]), c=str(st["c"]), p="%.2f" % st["p"], n=str(st["n"])),
    "STACK": lambda st: dict(acc="%.3f" % float(st["T"]), n=str(st["n"])),
    "STACK-v2": lambda st: dict(acc="%.3f" % float(st["T"]), n=str(st["n"])),
    "J6": lambda st: dict(T_pp=_tpp(st), b=str(st["b"]), c=str(st["c"]), p="%.3f" % st["p"], n=str(st["n"])),
}

_FULL = {}                    # (consumer, spec id) -> the full run's (stat, universe, mcount, qmids, report); per process


def make_route_cell(cid, consumer, set_id, delta_star, support, plan_bound, plan_mde, workers, tmp, spec=None,
                    recorded=None, c0fn=None, kind=None, leak_sign=None, socket_guard=True):
    """A route (A) cell: the original runs in its own subprocess under the read-only redirect; the full run (C0, with the
    scored-set probe) is shared by the consumer's cells; removal runs are batched per chunk of draws."""
    spec = spec if spec is not None else dict(sxc.ROUTE_A_SPECS[consumer], module_dir=ORIG_DIR)
    key = (consumer, json.dumps(spec, sort_keys=True))
    cell = dict(id=cid, consumer=consumer, set=set_id, kind=kind or spec["kind"], recorded=recorded or CONSUMERS[consumer]["recorded"],
                c0=c0fn or C0_ROUTE[consumer], verdict=lambda st: st["verdict"], scalar=lambda st: st["T"],
                leak_sign=CONSUMERS[consumer]["leak_sign"] if leak_sign is None else leak_sign, delta_star=delta_star,
                support=support, plan_bound=plan_bound, plan_mde=plan_mde,
                closure_band_pp=CONSUMERS.get(consumer, {}).get("closure_band_pp"), route=spec, reports=[], universe=None,
                mcount=None)

    def full():
        if key not in _FULL:
            rep_ = spawn_children(consumer, spec, [[dict(ids=[], mids=[])]], True, tmp, socket_guard)[0]
            cell["reports"].append(rep_)
            validate_child(rep_, 1)
            st = route_stat(spec, rep_["results"][0])
            probe = rep_["probe"] or []
            amap = rep_.get("anchors") or {}
            seen = {}
            for mid, q, anc in probe:
                if mid in seen:
                    continue                          # a multi-line statement can raise its line event twice
                seen[mid] = (int(q), anc if anc is not None else amap.get(str(mid)))
            if bool(len(seen) != st["n"]):
                raise CellInvalid("[A6] the probe's scored set holds %d matches, the original's headline n = %d" % (len(seen), st["n"]))
            anchor_of, mcount, qmids = {}, defaultdict(int), defaultdict(list)
            for mid, (q, anc) in seen.items():
                if anc is None:
                    raise CellInvalid("[A6] no anchor for scored match %s" % mid)
                if anchor_of.setdefault(q, anc) != anc:
                    raise CellInvalid("question %s carries two anchors (%s, %s): an anchor-matched removal is undefined"
                                      % (q, anchor_of[q], anc))
                mcount[q] += 1; qmids[q].append(int(mid))
            universe = defaultdict(list)
            for q, a in anchor_of.items():
                universe[a].append(q)
            _FULL[key] = (st, {a: sorted(v) for a, v in universe.items()}, dict(mcount), dict(qmids), rep_)
        st, universe, mcount, qmids, rep_ = _FULL[key]
        cell["universe"], cell["mcount"], cell["qmids"] = universe, mcount, qmids
        if rep_ not in cell["reports"]:
            cell["reports"].append(rep_)
        return st

    def stat(removed):
        if removed:
            return mapper(None, [removed])[0]
        return full()

    def mapper(_f, removals):
        st0 = full()
        qmids = cell["qmids"]
        sets = [dict(ids=sorted(int(q) for q in r), mids=sorted(m for q in r for m in qmids.get(q, []))) for r in removals]
        w = max(1, min(workers, len(sets)))
        chunks = [sets[i::w] for i in range(w)]
        reps = spawn_children(consumer, spec, chunks, False, tmp, socket_guard)
        out = [None] * len(sets)
        for ci, (ch, rep_) in enumerate(zip(chunks, reps)):
            cell["reports"].append(rep_)
            validate_child(rep_, len(ch))
            for j, r in enumerate(rep_["results"]):
                out[ci + j * w] = route_stat(spec, r)
        for r, st in zip(removals, out):
            expect = st0["n"] - sum(cell["mcount"].get(q, 0) for q in r)
            if bool(st["n"] != expect):
                raise CellInvalid("[A6] a removal did not act exactly on the scored set: n %d, expected %d" % (st["n"], expect))
        return out
    cell["stat"] = stat
    cell["map"] = mapper
    return cell


def route_lines(say, cell):
    """A1-A6 per consumer, printed: pid(s), the pinned identity, the connection log, import-time opens, call count,
    credentials left, files unchanged, memory and time; and HOW the headline was captured."""
    spec = cell.get("route")
    if not spec or not cell["reports"]:
        return
    reps = cell["reports"]
    r0 = reps[0]
    say("  ROUTE (A) (ruling a4d736a): %s imported unedited in %d subprocess(es) (pids %s; the parent is %d), identity"
        " blob:%s / sha256-lf16:%s (pinned %s / %s)" % (spec["module"] + ".py", len(reps), ",".join(str(r["pid"]) for r in reps[:6])
                                                       + ("..." if len(reps) > 6 else ""), os.getpid(),
                                                       (r0.get("identity") or {}).get("blob"), (r0.get("identity") or {}).get("sha256_lf16"),
                                                       spec["blob"], spec["sha256_lf16"]))
    agg = {}
    for r in reps:
        for p, e in r["connlog"].items():
            a = agg.setdefault(p, dict(count=0, kinds=set(), uri=e["uri"]))
            a["count"] += e["count"]; a["kinds"].update(e["kinds"])
    say("    connection log (every open redirected to file:<abs>?mode=ro&immutable=1 after the -wal/-journal check):")
    for p in sorted(agg):
        say("      %-66s opens %5d | %s" % (_rel(p)[-66:], agg[p]["count"], "; ".join(sorted(agg[p]["kinds"]))))
    say("    import-time opens %s | ZERO CALLS, ENFORCED BY the socket guard (Python socket + audit hook socket.connect):"
        " outbound connection attempts %d (must be 0) | .env reads refused %d (the credentials' only source) | other refused"
        " operations %d | environment credentials stripped (descriptive only) %d left | opened files unchanged (sha256_16,"
        " size, mtime): %s | local modules pinned: %d | child memory %s | child wall %s s"
        % (r0["import_opens"] or "none", sum(r["attempts"] for r in reps), sum(len(r.get("env_reads_refused") or []) for r in reps),
           sum(len(r.get("refusals") or []) for r in reps), sum(len(r["secrets_left"]) for r in reps),
           "yes" if not any(r["fp_changed"] for r in reps) else "NO", len(r0.get("local_modules") or {}), r0.get("rss"),
           "/".join("%.1f" % r["t"] for r in reps[:4])))
    say("    capture (A6): the original's own %s(%s) with stdout captured; headline line(s) pinned: %s; T %s; scored set by %s"
        % (spec["entry"], ", ".join(repr(a) for a in spec.get("args", [])), ", ".join(p["name"] for p in spec["patterns"]),
           ("= %+d x (b - c) / n from the printed integers" % spec["stat"]["sign"]) if spec["kind"] == "paired"
           else "= the original's local acc x n at its return (cross-checked with the printed value)",
           ("the pinned line %r, expr %s" % (spec["probe"]["line"][:70], spec["probe"]["expr"])) if spec["probe"]["mode"] == "line"
           else "its locals at return, expr %s" % spec["probe"]["expr"]))


# ------------------------------------------------------------------------------------------ readout (print branches)
def pp(x):
    return 100.0 * float(x)


def cell_lines(say, cell, res):
    unit = "edges" if cell["kind"] == "cert" else "pp"
    f = (lambda x: "%+.2f" % float(x)) if cell["kind"] == "cert" else (lambda x: "%+.3f" % pp(x))
    say("")
    say("--- CELL %s: %s x %s [registered support: %s] ---" % (cell["id"], cell["consumer"], cell["set"], cell["support"]))
    c = CONSUMERS[cell["consumer"]]
    say("  reuses %s blob:%s, %s; recorded headline: %s" % (c["script"], c["blob"], c["entry"], c["recorded_text"]))
    route_lines(say, cell)
    if cell["kind"] == "cert":
        say("  cert's G1 / G2 gates are checked on the FULL data in C0 (cert.PINS); on a reduced copy they compare against the"
            " reduced data's own counts and CHECK NOTHING (reading r4: U, the edge set, the established set and the key"
            " direction are RE-DERIVED on every removal, observed and null alike).")
    if res.get("stage") == "C0":
        hit("C0.UNDETERMINED_BY_VALIDITY")
        say("  C0: the recorded headline does NOT reproduce to the digit: %s" % "; ".join("%s got %s recorded %s" % m for m in res["c0"]))
        say("  -> UNDETERMINED (BY VALIDITY): the consumer is excluded on all its cells and listed; no removal was scored.")
        return
    hit("C0.PASS")
    say("  C0: recorded headline reproduced to the digit from the same code path: %s"
        % ", ".join("%s %s" % (k, v) for k, v in sorted(cell["recorded"].items())))
    say("  scored set: n = %d matches on %d questions (Kish mean cluster size %.3f); k = %d matches on %d exposed questions"
        " (per anchor: %s)" % (res["n"], res["n_q"], res["kish"], res["k"], res["k_q"],
                              ", ".join("%s %d" % (a, n) for a, n in sorted(res["e_a"].items())) or "none"))
    hazard_lines(say, cell, res)
    if res.get("stage") == "ID-SPACE":
        hit("HAZARD.D_OUTSIDE")
        say("  -> UNDETERMINED (BY VALIDITY): %d scored qids lie outside the pool of record's eval ids (hazard (d)); nothing"
            " is scored." % res["outside"])
        return
    if res.get("stage") == "REMOVAL":
        hit("C0.REMOVAL_INVALID")
        say("  C0 PASSED; a REMOVAL run of the original could not be completed as registered: %s" % res["removal_error"])
        say("  -> UNDETERMINED (BY VALIDITY) at the removal stage (not a C0 failure); nothing is scored.")
        return
    if res["status"] == "UNDETERMINED (BY SUPPORT)":
        hit("C1.UNDETERMINED_BY_SUPPORT")
        say("  C1: k = 0 -> UNDETERMINED (BY SUPPORT): the set touches none of this consumer's scored questions.")
        return
    say("  T with = %s | T without = %s | observed shift delta = %s %s" % (_fmtT(cell, res["T0"]), _fmtT(cell, res["T1"]), f(res["delta"]), unit))
    say("  NULL: R = %d anchor-matched random removals of the same number of NON-exposed scored questions per anchor (whole"
        " questions), random.Random(%d); shifts: mean %s, SD %s %s; central 95%% (numpy.percentile linear, observed excluded):"
        " [%s, %s]; observed mid-rank percentile %.3f" % (res["R"], res["seed"], f(res["null_mean"]),
                                                          "%.3f" % (res["null_sd"] * (1 if cell["kind"] == "cert" else 100)),
                                                          unit, f(res["lo"] if cell["kind"] == "cert" else res["lo"]),
                                                          f(res["hi"]), res["pct"]))
    if res["word"] == "FLAGGED":
        hit("C1.FLAGGED")
        d = res["dir"]
        hit({"LEAK": "C1.DIR_LEAK", "OPPOSITE": "C1.DIR_OPPOSITE", "UNDEFINED": "C1.DIR_UNDEFINED"}[d])
        say("  C1: FLAGGED - the observed shift lies outside the null's central 95%%; direction %s (reading r7)%s."
            % (d, "; J6 is TWO-SIDED and DESCRIPTIVE ONLY (ruling a4d736a)" if d == "UNDEFINED" else ""))
    else:
        hit("C1.NOT_FLAGGED")
        say("  C1: NOT FLAGGED - the observed shift lies within the null's central 95%.")
    b = bound_of(cell, res)
    if b is None:
        hit("STRUCT.UNDEFINED")
        say("  STRUCTURAL LEG: the registration's BOUND is defined for a paired difference or an accuracy, not for Delta_W;"
            " not printed (reading r11). Delta* %.2f edges (registered)." % cell["delta_star"])
        bounded = False
    else:
        bounded = bool(b < cell["delta_star"])
        say("  BOUND: removing k = %d matches can move T by at most %.3f pp (planning %.2f pp); Delta* %.2f pp"
            % (res["k"], pp(b), cell["plan_bound"] if cell["plan_bound"] is not None else float("nan"), pp(cell["delta_star"])))
        if bounded:
            hit("STRUCT.BOUNDED")
            say("  STRUCTURAL LEG: BOUNDED - the consequential shift is UNREACHABLE at any draw at the measured k.")
        else:
            hit("STRUCT.REACHABLE")
            say("  STRUCTURAL LEG: reachable - the bound %.3f pp is not below Delta* %.2f pp." % (pp(b), pp(cell["delta_star"])))
    same = bool(res["v_with"] == res["v_without"])
    if same:
        hit("C2.SAME")
    else:
        hit("C2.CHANGED")
    say("  C2 (DESCRIPTIVE-ONLY): the recorded verdict [%s] with the exposed questions %s, without %s -> %s"
        % (CONSUMERS[cell["consumer"]]["test"], res["v_with"], res["v_without"], "SAME" if same else "CHANGED"))
    if bounded:
        hit("C2.SETTLED_BY_BOUND")
        say("    C2 is SETTLED BY THE BOUND (registration (g)): exposure of this size cannot change what the record says.")
    if cell["kind"] == "cert":
        say("  beside, deciding nothing: %s" % CERT_REVIEW_BASIS)
        st1 = res["st1"]
        say("  beside: without the exposed questions W_F %d, mean W_R %.2f, %d established edges in %d anchors, interval"
            " [%+.2f, %+.2f] (SE %.3f), anchors removed %s" % (st1["WF"], st1["WR_mean"], st1["n_edges"], st1["n_anchors"],
                                                             st1["lo"], st1["hi"], st1["se"], ", ".join(st1["removed_anchors"]) or "none"))
    support_block(say, cell, res)


def _fmtT(cell, T):
    if cell["kind"] == "cert":
        return "%+.2f edges" % float(T)
    if cell["kind"] == "paired":
        return "%+.3f pp" % pp(T)
    return "%.4f" % float(T)


def support_block(say, cell, res):
    word = cell["support"]
    hit("SUPPORT.SCOREABLE" if word == "SCOREABLE" else "SUPPORT.DESCRIPTIVE_ONLY")
    sd = res["null_sd"]
    scale = 1.0 if cell["kind"] == "cert" else 100.0
    unit = "edges" if cell["kind"] == "cert" else "pp"
    mde = MDE_K * sd
    iid = iid_sd(cell, res)
    if iid is None or not bool(iid > 0):
        hit("SUPPORT.DEFF_UNDEFINED")
        say("  SUPPORT: registered %s (Delta* %.2f %s against the planned MDE %.2f %s). Measured: null SD %.4f %s; MDE (2.80 x"
            " null SD) %.3f %s; DEFF %s" % (word, cell["delta_star"] * (1 if cell["kind"] == "cert" else 100), unit,
                                           cell["plan_mde"], unit, sd * scale, unit, mde * scale, unit,
                                           "registered %.3f (605675c; no iid form for Delta_W)" % CERT_DEFF_REGISTERED
                                           if cell["kind"] == "cert" else "undefined (iid SD 0)"))
    else:
        deff = (sd / iid) ** 2
        say("  SUPPORT: registered %s (Delta* %.2f %s against the planned MDE %.2f %s). Measured: null SD %.4f %s; iid SD"
            " %.4f %s; DEFF %.3f (declared pilot 1.2); n_eff %.1f; MDE (2.80 x null SD) %.3f %s"
            % (word, pp(cell["delta_star"]), unit, cell["plan_mde"], unit, sd * scale, unit, iid * scale, unit, deff,
               res["n"] / deff if deff > 0 else float("nan"), mde * scale, unit))
    measured = "SCOREABLE" if bool(cell["delta_star"] > mde) else "DESCRIPTIVE-ONLY"
    if measured == word:
        hit("SUPPORT.MEASURED_AGREES")
        say("    measured check Delta* > MDE: %s, as registered." % measured)
    else:
        hit("SUPPORT.MEASURED_DISAGREES")
        say("    measured check Delta* > MDE reads %s, NOT the registered %s; the registered support line stands (reading"
            " r10); flagged for the READY." % (measured, word))


def stopped_lines(say, cid, consumer, set_id, support):
    hit("CELL.STOPPED")
    c = CONSUMERS[consumer]
    say("")
    say("--- CELL %s: %s x %s [registered support: %s] ---" % (cid, consumer, set_id, support))
    say("  NOT BUILT. reuses %s blob:%s %s; %s" % (c["script"], c["blob"], c["entry"], c["stop"]))


def scored(res):
    return res is not None and res.get("status") in ("FLAGGED", "NOT FLAGGED")


def c3_lines(say, results):
    sc = [cid for cid in CELL_IDS if scored(results.get(cid))]
    fl = [cid for cid in sc if results[cid]["status"] == "FLAGGED"]
    m = len(sc); x = len(fl)
    tail = sum(math.comb(m, j) * ALPHA_FAMILY ** j * (1 - ALPHA_FAMILY) ** (m - j) for j in range(x, m + 1)) if m else float("nan")
    hit("C3.LINE")
    say("")
    say("=== C3: THE FAMILY READING ===")
    say("  FLAGGED %d of %d cells scored (of 13 registered); expected under the global null %.2f; P(X >= %d | %d, 0.05) = %.4f"
        % (x, m, ALPHA_FAMILY * m, x, m, tail))
    say("  registered reference at 13 cells: 0.65 expected, P(>= 2) = 0.14, P(>= 3) = 0.026. A single FLAG is not evidence"
        " of a leak effect by itself.")
    say("  directions: %s" % (", ".join("%s %s" % (cid, results[cid]["dir"]) for cid in fl) or "none flagged"))
    return x, m


def _score(say, pid, clause, parts, ok_fn):
    """(r9): FAILED if any SCORED constituent fails; else UNDETERMINED if any is unscored; else HELD."""
    failed = [cid for cid, r in parts if scored(r) and not bool(ok_fn(r))]
    unscored = [cid for cid, r in parts if not scored(r)]
    word = "FAILED" if failed else ("UNDETERMINED" if unscored else "HELD")
    hit("%s.%s" % (pid, word))
    say("  %s %-78s -> %s%s" % (pid, clause, word, (" (failed: %s)" % ", ".join(failed)) if failed else
                                 ((" (unscored: %s)" % ", ".join(unscored)) if unscored else "")))
    return word


def predictions(say, results):
    say("")
    say("=== PREDICTIONS (the registrar's; scored HELD / FAILED / UNDETERMINED by reading r9) ===")
    R_ = lambda ids: [(cid, results.get(cid)) for cid in ids]
    w = {}
    w["P1"] = _score(say, "P1", "RUBRIC-512/-SS/-R x E28, E70: NOT FLAGGED, delta in [-0.30, +0.25]pp, pct in [0.05, 0.95]",
                     R_(["a-E28", "a-E70", "b-E28", "b-E70", "c-E28", "c-E70"]),
                     lambda r: r["status"] == "NOT FLAGGED" and -0.30 <= pp(r["delta"]) <= 0.25 and 0.05 <= r["pct"] <= 0.95)
    w["P2"] = _score(say, "P2", "LEAF-POWERED x E28, E70: NOT FLAGGED, delta in [-0.20, +0.20]pp",
                     R_(["d-E28", "d-E70"]), lambda r: r["status"] == "NOT FLAGGED" and -0.20 <= pp(r["delta"]) <= 0.20)
    w["P3"] = _score(say, "P3", "ladder cells x E14: NOT FLAGGED, delta in [-0.15, +0.15]pp",
                     R_(["e-LADDER", "e-STACK", "e-STACKv2", "e-J6"]),
                     lambda r: r["status"] == "NOT FLAGGED" and -0.15 <= pp(r["delta"]) <= 0.15)
    w["P4"] = _score(say, "P4", "CERT-UNDER-FILTER x E74: NOT FLAGGED, percentile in [0.80, 0.99]",
                     R_(["f-CERT"]), lambda r: r["status"] == "NOT FLAGGED" and 0.80 <= r["pct"] <= 0.99)
    sc = [cid for cid in CELL_IDS if scored(results.get(cid))]
    nfl = sum(1 for cid in sc if results[cid]["status"] == "FLAGGED")
    scoreable = {c[0] for c in CELL_TABLE if c[4] == "SCOREABLE"}
    c2_changed = [cid for cid in sc if cid in scoreable and bool(results[cid]["v_with"] != results[cid]["v_without"])]
    if bool(nfl >= 2) or c2_changed:
        w5 = "FAILED"
    elif len(sc) < len(CELL_IDS):
        w5 = "UNDETERMINED"
    else:
        w5 = "HELD"
    hit("P5.%s" % w5)
    say("  P5 %-78s -> %s (FLAGGED %d of %d scored; C2 changed on SCOREABLE: %s)"
        % ("0 FLAGGED of 13 [0, 1] AND C2 unchanged on every SCOREABLE cell", w5, nfl, len(sc), ", ".join(c2_changed) or "none"))
    w["P5"] = w5
    c0_fail = [cid for cid in CELL_IDS if results.get(cid) is not None and results[cid].get("stage") == "C0"]
    sup70 = [cid for cid in CELL_IDS if results.get(cid) is not None and results[cid]["set"] == "E70"
             and results[cid].get("status") == "UNDETERMINED (BY SUPPORT)"]
    sup14 = [cid for cid in CELL_IDS if results.get(cid) is not None and results[cid]["set"] == "E14"
             and results[cid].get("status") == "UNDETERMINED (BY SUPPORT)"]
    missing = [cid for cid in CELL_IDS if results.get(cid) is None]
    if c0_fail or sup70 or bool(len(sup14) > 3):
        w6 = "FAILED"
    elif missing:
        w6 = "UNDETERMINED"
    else:
        w6 = "HELD"
    hit("P6.%s" % w6)
    say("  P6 %-78s -> %s (C0 failed: %s; E70 by support: %s; E14 by support: %d; not built: %s)"
        % ("C0 reproduces everywhere; 0 BY SUPPORT at E70; <= 3 at E14", w6, ", ".join(c0_fail) or "none",
           ", ".join(sup70) or "none", len(sup14), ", ".join(missing) or "none"))
    w["P6"] = w6
    return w


def falsifier_lines(say, results, cells):
    say("")
    say("=== FALSIFIER ===")
    sc = [cid for cid in CELL_IDS if scored(results.get(cid))]
    nfl = sum(1 for cid in sc if results[cid]["status"] == "FLAGGED")
    if bool(nfl >= 2):
        hit("FALS.P5_FIRED")
        say("  FIRED: %d cells FLAG (>= 2): P5 fails." % nfl)
    else:
        hit("FALS.P5_NOT_FIRED")
        say("  NOT FIRED: %d cell(s) FLAG (< 2)." % nfl)
    any_branch = False
    for cid in sc:
        r = results[cid]; cell = cells[cid]
        if r["status"] != "FLAGGED":
            continue
        if cell["support"] != "SCOREABLE":
            hit("FALS.DESCRIPTIVE_FLAG")
            say("  %s FLAGGED (direction %s) on a DESCRIPTIVE-ONLY cell: printed descriptively; no [QUALIFIED] branch fires"
                " (reading r8, confirmed a4d736a); it COUNTS toward C3 and P5%s." % (cid, r["dir"],
                "; added to the author's rebuild-or-disclose item as a descriptive note" if cid == "f-CERT" else ""))
            any_branch = True
            continue
        if r["dir"] == "LEAK":
            hit("FALS.LEAK_QUALIFIED")
            say("  %s FLAGGED IN THE LEAK DIRECTION on a SCOREABLE cell: a [QUALIFIED] bracket is owed against %s (its number"
                " as recorded stands; the exposure-sensitive reading is added); to the author's rebuild-or-disclose item; it"
                " OVERTURNS the reading 'the leak is too small to matter' for %s." % (cid, cell["consumer"], cell["consumer"]))
            any_branch = True
        elif r["dir"] == "OPPOSITE" and cell.get("closure_band_pp") is not None and bool(pp(r["T1"]) > cell["closure_band_pp"]):
            hit("FALS.CLOSURE_QUALIFIED")
            say("  %s FLAGGED IN THE OPPOSITE DIRECTION on a SCOREABLE rubric cell, de-exposed estimate %+.3f pp above +%.1f pp:"
                " qualifies the closure sentence 'induced cell rubrics are worth 0 to +1pp' by insertion; re-opening the"
                " line needs its own registration." % (cid, pp(r["T1"]), cell["closure_band_pp"]))
            any_branch = True
    if not any_branch:
        hit("FALS.NO_CONSUMER_BRANCH")
        say("  no consumer-level falsifier branch fired.")
    say("  NOT OVERTURNED in any branch: any recorded verdict (C2 is descriptive), the pools of record, the trees of record,"
        " any board.")


def readings_lines(say):
    say("  readings fixed before the run (docstring r1-r11): quantiles numpy.percentile linear over the R null shifts only;"
        " FLAGGED iff delta < q2.5 or > q97.5 (strict); mid-rank percentile; removal = whole questions, anchor-matched,"
        " random.Random(NULL_SEED0 + j) with NULL_SEED0 = %d, anchors sorted; CERT re-run end to end on the reduced data;"
        " C2 of CERT = its C1 verdict; leak directions (r7); the falsifier's SCOREABLE clause literal (r8)." % NULL_SEED0)


def readout(say, results, cells, stopped):
    for cid, consumer, set_id, _ds, support, _pb, _pm in CELL_TABLE:
        if cid in stopped:
            stopped_lines(say, cid, consumer, set_id, support)
        else:
            cell_lines(say, cells[cid], results[cid])
    x, m = c3_lines(say, results)
    w = predictions(say, results)
    falsifier_lines(say, results, cells)
    return dict(flagged=x, scored=m, predictions=w)


# ------------------------------------------------------------------------------------------ write-once
def write_once(path, text):
    if os.path.exists(path):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; an outcome of record is never overwritten. Refused." % path)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------------------------------------ real-data modes
def input_paths():
    dbs = [cuf.X12_CACHE, rj.EVAL_DB, r512.SNAP_DB]
    files = [os.path.join(r512.PROMOTED, "bareq512_s42_reserved_leaf_assignments.csv"),
             os.path.join(r512.PROMOTED, "bareq512_s42", "seed_42", "headless_run.log"),
             pool_guard.id_file_path(POOL)] + [os.path.join(EVIDENCE_DIR, SETS[s]["file"]) for s in sorted(SETS)]
    return dbs, files


def stopped_cells():
    return {cid for cid, consumer, *_ in CELL_TABLE if CONSUMERS[consumer]["stop"] is not None}


def header(say):
    say("=== SPLIT-EXPOSURE-SENSITIVITY (registered 2026-09-23, commit 46889ea; docs/judge_v2_program.md L14701-L14756;"
        " route (A) ruled a4d736a, L14867-L14881) ===")
    for l in identity_lines():
        say(l)
    for l in check_route_pins():
        say(l)
    say("  ZERO judge calls (route (A) children: credentials stripped, socket guard, call count printed per consumer); no DB"
        " written; cert_under_filter imported unedited in THIS process (its connection log and stack_judge stub in force),"
        " every other consumer in its own subprocess (A5); systematic_budget.build LF source sha16 %s (cert's pin)"
        % cuf.check_build_pin())
    readings_lines(say)
    hazards_header(say)


def prepare_real(say, workers):
    dbs, files = input_paths()
    for p, s_ in check_sidecars(dbs):
        say("  read-only source %s (mode=ro&immutable=1): %s (a non-empty -wal or -journal refuses)" % (_rel(p), s_))
    before = fingerprint(dbs + files)
    pool_ids = pool_guard.eval_ids(POOL)
    POOL_IDS[0] = frozenset(pool_ids)
    sets = load_sets(SETS, EVIDENCE_DIR, pool_ids, say)
    D = cuf.load_real(say)
    return dbs, files, before, sets, D


def build_cells(D, workers, say, tmp):
    cells = {}
    for cid, consumer, set_id, dstar, support, pbound, pmde in CELL_TABLE:
        if CONSUMERS[consumer]["route"] == "A":
            cells[cid] = make_route_cell(cid, consumer, set_id, dstar, support, pbound, pmde, workers, tmp)
    cells["f-CERT"] = make_cert_cell(D, cuf.BOOT_B, CERT_MIN_ANCHORS, workers, CERT_RECORDED, cuf.PINS)
    return cells


def route_files_unchanged(cells, say):
    """A3 across the whole run: every file a route (A) child opened is re-fingerprinted by the parent at the end and
    compared with the child's fingerprint at first open."""
    first = {}
    for cell in cells.values():
        for r in cell.get("reports") or []:
            for p, fp in (r.get("fp") or {}).items():
                first.setdefault(p, tuple(fp))
    now = {p: tuple(v) for p, v in fingerprint(list(first)).items()}
    changed = [p for p in first if first[p] != now[p]]
    say("  route (A) files opened by the consumer children: %d; unchanged at the end of the run: %s"
        % (len(first), "yes" if not changed else "NO %s" % changed))
    if changed:
        hit("INPUTS.CHANGED")
        raise SystemExit("[INPUTS] route (A) files changed during the run: %s. Nothing is written. Refused." % changed)


def main_dry(workers):
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL), flush=True)
    L = []; say = lambda s_: (L.append(s_), print(s_, flush=True))
    header(say)
    say("  --dry-run: zero calls, WRITES NOTHING.")
    dbs, files, before, sets, D = prepare_real(say, workers)
    say("  RAM after load: %s; pickled D (sent once per CERT worker) %.1f MB" % (rss_line(), len(pickle.dumps(D)) / 2 ** 20))
    tmp = tempfile.mkdtemp(prefix="ses_jobs_")
    cells = build_cells(D, workers, say, tmp)
    stopped = stopped_cells()
    c0_pass, c0_fail, removal_fail = [], [], []
    for j, (cid, consumer, set_id, *_r) in enumerate(CELL_TABLE, 1):
        if cid in stopped:
            stopped_lines(say, cid, consumer, set_id, _r[1])
            continue
        cell = cells[cid]
        t0 = time.time()
        try:
            st0, mism = c0_gate(cell)
        except CellInvalid as e:
            say("  C0 %s: UNDETERMINED (BY VALIDITY): %s" % (cid, e))
            route_lines(say, cell)
            c0_fail.append((cid, str(e)[:200]))
            continue
        say("  C0 %s: %s (%.0f s)" % (cid, "PASS: " + ", ".join("%s %s" % kv for kv in sorted(cell["c0"](st0).items()))
                                      if not mism else "MISMATCH %s" % mism, time.time() - t0))
        route_lines(say, cell)
        if mism:
            c0_fail.append((cid, str(mism)[:200]))
            continue
        hit("C0.CERT_PASS" if cell["kind"] == "cert" else "C0.ROUTE_PASS")
        c0_pass.append(cid)
        E = sets[set_id]
        scored_q = {q for qs in cell["universe"].values() for q in qs}
        exp_q = frozenset(q for q in scored_q if q in E)
        e_a = {a: sum(1 for q in qs if q in exp_q) for a, qs in cell["universe"].items()}
        e_a = {a: n for a, n in e_a.items() if n}
        k = sum(cell["mcount"][q] for q in exp_q)
        R = R_CERT if cell["kind"] == "cert" else R_CELLS
        say("  %s: n = %d scored matches on %d questions; k = %d matches on %d of %d exposed questions (per anchor %s)"
            % (cid, sum(cell["mcount"].values()), len(scored_q), k, len(exp_q), len(E), e_a))
        outside = None if POOL_IDS[0] is None else len(scored_q - POOL_IDS[0])
        hazard_lines(say, cell, dict(outside=outside, n_q=len(scored_q)))
        if outside:
            c0_fail.append((cid, "hazard (d): %d scored qids outside the pool" % outside))
            continue
        if k:
            draws = draw_removals(cell["universe"], E, e_a, R, NULL_SEED0 + j)
            check_draws(draws, cell["universe"], E, e_a, R)
            say("  %s: %d anchor-matched removal sets drawn (random.Random(%d)) and checked; none holds an exposed question"
                % (cid, R, NULL_SEED0 + j))
            t0 = time.time()
            try:
                cell["map"](cell["stat"], [exp_q] + draws[:2])
            except CellInvalid as e:
                say("  %s: C0 PASSED; a REMOVAL run is UNDETERMINED (BY VALIDITY) (removal stage, not C0): %s" % (cid, e))
                removal_fail.append((cid, str(e)[:200]))
                continue
            dt = time.time() - t0
            if cell["kind"] == "cert":
                per = dt / 3.0
                say("  %s: 3 replicates %.1f s wall (%.1f s each) -> observed + %d null = %.1f CPU-hours; %.1f h wall at %d"
                    " worker(s)" % (cid, dt, per, R, per * (R + 1) / 3600.0, per * (R + 1) / 3600.0 / max(1, workers), workers))
            else:
                rep_ = cell["reports"][-1]
                ts = [x["t"] for x in rep_["results"]]
                per = sum(ts[1:]) / max(1, len(ts) - 1)
                say("  %s: one child, 3 removal runs: child wall %.1f s (start-up and first run %.1f s, then %.1f s per run);"
                    " memory %s -> observed + %d null about %.1f CPU-hours; %.2f h wall at %d worker(s)"
                    % (cid, rep_["t"], ts[0], per, rep_.get("rss"), R, (ts[0] + per * R) / 3600.0,
                       (ts[0] + per * R / max(1, workers)) / 3600.0, workers))
    route_files_unchanged(cells, say)
    after = fingerprint(dbs + files)
    say("  inputs before / after:")
    compare_fingerprints(before, after, say)
    check_connlog(cuf.CONNECTIONS, cuf.X12_CACHE)
    cuf.connection_log(say)
    say("  RAM at end: %s" % rss_line())
    say("  DRY-RUN COMPLETE: nothing written. STOPPED cells: %d of 13." % len(stopped))
    dry_summary(say, c0_pass, c0_fail, removal_fail, len(CELL_TABLE) - len(stopped))


def dry_summary(say, c0_pass, c0_fail, removal_fail, n_built):
    """D6: the dry-run's verdict line; ANY C0 or removal-stage failure exits NONZERO (a failed precondition of --run)."""
    say("  C0 SUMMARY: PASS %d of %d built cells; C0 UNDETERMINED (BY VALIDITY) %d%s; removal-stage failures %d%s"
        % (len(c0_pass), n_built, len(c0_fail), (" (%s)" % "; ".join("%s: %s" % f for f in c0_fail)) if c0_fail else "",
           len(removal_fail), (" (%s)" % "; ".join("%s: %s" % f for f in removal_fail)) if removal_fail else ""))
    if c0_fail or removal_fail or len(c0_pass) != n_built:
        hit("DRY.C0_SUMMARY_FAIL")
        raise SystemExit("[DRY-RUN] C0 is not PASS on every built cell (%d of %d): --run must not be launched."
                         % (len(c0_pass), n_built))
    hit("DRY.C0_SUMMARY_PASS")


def main_run(workers):
    if os.path.exists(OUT):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; refused before computing." % OUT)
    stopped = stopped_cells()
    if stopped:
        hit("RUN.REFUSED_STOPPED")
        raise SystemExit("[STOPPED] %d of 13 registered cells are not BUILT (%s): the outcome of record is written once,"
                         " complete. Refused before computing." % (len(stopped), ", ".join(sorted(stopped))))
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(POOL), flush=True)
    L = ["reserved_pool_id=%s" % POOL]; say = lambda s_: (L.append(s_), print(s_, flush=True))
    header(say)
    say("  run started %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    dbs, files, before, sets, D = prepare_real(say, workers)
    tmp = tempfile.mkdtemp(prefix="ses_jobs_")
    cells = build_cells(D, workers, say, tmp)
    results = {}
    for j, (cid, consumer, set_id, *_r) in enumerate(CELL_TABLE, 1):
        cell = cells[cid]
        R = R_CERT if cell["kind"] == "cert" else R_CELLS
        results[cid] = evaluate_cell(cell, sets[set_id], R, NULL_SEED0 + j)
        print("[run] %s %s (%s)" % (cid, results[cid]["status"], time.strftime("%H:%M:%S")), file=sys.stderr, flush=True)
    readout(say, results, cells, set())
    say("")
    route_files_unchanged(cells, say)
    after = fingerprint(dbs + files)
    say("  inputs before / after:")
    compare_fingerprints(before, after, say)
    check_connlog(cuf.CONNECTIONS, cuf.X12_CACHE)
    cuf.connection_log(say)
    say("  run finished %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    write_once(OUT, "\n".join(L) + "\n")
    print("[SPLIT-EXPOSURE-SENSITIVITY] outcome written once: %s" % OUT, file=sys.stderr)


# ------------------------------------------------------------------------------------------ selftest fixtures
def _expect_exit(fn, prefix, what):
    try:
        fn()
    except SystemExit as e:
        need(str(e).startswith(prefix), "%s refused with %r, expected prefix %s" % (what, str(e), prefix))
        return str(e)
    raise SystemExit("[CHECK] %s did not refuse" % what)


def synth_paired_rows(seed=7, n1=120, n2=400, plus1=36, minus2=40):
    """Anchor A1: n1 questions, `plus1` of them all-(1, 0) (cell right, comparator wrong), the rest all-(1, 1); anchor A2:
    n2 questions, `minus2` all-(0, 1), the rest all-(0, 0). 1-3 matches per question (q mod 3)."""
    rng = random.Random(seed)
    rows = []; kinds = {}
    a1 = list(range(1000, 1000 + n1)); a2 = list(range(5000, 5000 + n2))
    p1 = set(rng.sample(a1, plus1)); m2 = set(rng.sample(a2, minus2))
    for q in a1:
        kinds[q] = "+" if q in p1 else "0"
        for _ in range(1 + q % 3):
            rows.append((q, "A1", 1, 0) if q in p1 else (q, "A1", 1, 1))
    for q in a2:
        kinds[q] = "-" if q in m2 else "0"
        for _ in range(1 + q % 3):
            rows.append((q, "A2", 0, 1) if q in m2 else (q, "A2", 0, 0))
    return rows, kinds


def _paired_verdict(st):
    return "PASS" if (st["T"] > 0 and st["p"] < 0.05) else "FAIL"


def _mk(cid, consumer, set_id, rows, recorded=None, kind="paired", leak_sign=-1, delta_star=0.01, support="SCOREABLE",
        verdict=None, closure_band_pp=None):
    tmp = make_generic_cell(cid, consumer, set_id, kind, rows, {}, verdict or _paired_verdict, leak_sign, delta_star, support)
    st0 = tmp["stat"](frozenset())
    rec = recorded if recorded is not None else {k: v for k, v in tmp["c0"](st0).items()
                                                 if k in (("T_pp", "b", "c", "p", "n") if kind == "paired" else ("acc", "n"))}
    return make_generic_cell(cid, consumer, set_id, kind, rows, rec, verdict or _paired_verdict, leak_sign, delta_star, support,
                             plan_bound=1.0, plan_mde=0.2, closure_band_pp=closure_band_pp)


def _pick(kinds, anchor_pref, kind_counts, seed):
    rng = random.Random(seed); out = []
    for kd, n in kind_counts:
        pool = sorted(q for q, k in kinds.items() if k == kd and (q < 5000) == (anchor_pref == "A1"))
        out += rng.sample(pool, n)
    return frozenset(out)


def selftest_engine(say):
    rows, kinds = synth_paired_rows()
    cell = _mk("a-E28", "RUBRIC-512", "E28", rows)
    R = 1000
    # (1) LEAK-direction shift -> FLAGGED: 20 exposed A1 questions, all (1, 0) (the cell arm inflated on them)
    E_leak = _pick(kinds, "A1", [("+", 20)], 1)
    r1 = evaluate_cell(cell, E_leak, R, 101)
    need(r1["status"] == "FLAGGED" and r1["dir"] == "LEAK", ("leak fixture", r1["status"], r1.get("dir")))
    need(bool(r1["delta"] < 0) and bool(float(r1["delta"]) < r1["lo"]), "the leak shift must fall below the null's 2.5th percentile")
    say("[selftest] fixture LEAK      : delta %+.3f pp, null [%+.3f, %+.3f] pp -> %s (%s)"
        % (pp(r1["delta"]), 100 * r1["lo"], 100 * r1["hi"], r1["status"], r1["dir"]))
    # (2) NULL-SIZED shift -> NOT FLAGGED: 20 exposed A1 questions at A1's own rate (6 of 20 '+'); the anchors differ,
    #     so a removal that is not anchor-matched would move the null away from the observed shift
    E_typ = _pick(kinds, "A1", [("+", 6), ("0", 14)], 2)
    r2 = evaluate_cell(cell, E_typ, R, 102)
    need(r2["status"] == "NOT FLAGGED", ("null-sized fixture", r2["status"], pp(r2["delta"]), r2["lo"], r2["hi"]))
    need(0.05 <= r2["pct"] <= 0.95, ("null-sized percentile", r2["pct"]))
    say("[selftest] fixture NULL-SIZE : delta %+.3f pp, null [%+.3f, %+.3f] pp, percentile %.3f -> %s"
        % (pp(r2["delta"]), 100 * r2["lo"], 100 * r2["hi"], r2["pct"], r2["status"]))
    # (3) OPPOSITE-direction shift in the UPPER tail -> FLAGGED (a one-sided lower test would miss it)
    E_opp = _pick(kinds, "A2", [("-", 20)], 3)
    r3 = evaluate_cell(cell, E_opp, R, 103)
    need(r3["status"] == "FLAGGED" and r3["dir"] == "OPPOSITE" and bool(float(r3["delta"]) > r3["hi"]), ("opposite fixture", r3["status"]))
    say("[selftest] fixture OPPOSITE  : delta %+.3f pp, null [%+.3f, %+.3f] pp -> %s (%s)"
        % (pp(r3["delta"]), 100 * r3["lo"], 100 * r3["hi"], r3["status"], r3["dir"]))
    # (4) k = 0 -> UNDETERMINED (BY SUPPORT), no null drawn
    r4 = evaluate_cell(cell, frozenset({9999991, 9999992}), R, 104)
    need(r4["status"] == "UNDETERMINED (BY SUPPORT)" and r4["k"] == 0 and "null" not in r4, ("k=0 fixture", r4["status"]))
    say("[selftest] fixture K=0       : k %d -> %s (no null drawn)" % (r4["k"], r4["status"]))
    # (5) C0 mismatch -> refused (UNDETERMINED BY VALIDITY), before any removal
    bad = _mk("b-E28", "RUBRIC-512-SS", "E28", rows, recorded=dict(T_pp="+1.0", b="35", c="26", p="0.31"))
    r5 = evaluate_cell(bad, E_leak, R, 105)
    need(r5["status"] == "UNDETERMINED (BY VALIDITY)" and r5["c0"] and "null" not in r5 and "k" not in r5, ("C0 fixture", r5["status"]))
    say("[selftest] fixture C0        : recorded +1.0pp 35:26 against the cache's own %s -> %s (no removal scored)"
        % (cell["c0"](r5["st0"])["T_pp"], r5["status"]))
    # (6) the decision rule on a crafted null: central 95%, strict, two-sided
    null = [Fraction(i, 1000) for i in range(1000)]
    lo, hi = quantiles(null)
    need(flag_word(Fraction(35, 1000), lo, hi) == "NOT FLAGGED", "a shift at the 3.5th percentile must NOT flag (central 95%)")
    need(flag_word(Fraction(965, 1000), lo, hi) == "NOT FLAGGED", "a shift at the 96.5th percentile must NOT flag")
    need(flag_word(Fraction(10, 1000), lo, hi) == "FLAGGED" and flag_word(Fraction(990, 1000), lo, hi) == "FLAGGED",
         "both tails must flag")
    need(flag_word(lo, lo, hi) == "NOT FLAGGED" and flag_word(hi, lo, hi) == "NOT FLAGGED", "a shift equal to a quantile must NOT flag")
    say("[selftest] decision rule     : crafted null 0..0.999: q2.5 %.5f q97.5 %.5f; 0.035 / 0.965 NOT FLAGGED, 0.010 / 0.990"
        " FLAGGED, equality NOT FLAGGED" % (lo, hi))
    # (7) the null is exactly R draws, anchor-matched, exposed-free, and each shift recomputes from its removal set
    for r, E_ in ((r1, E_leak), (r2, E_typ), (r3, E_opp)):
        check_draws(r["draws"], cell["universe"], E_, r["e_a"], R)
        need(len(r["null"]) == R, "null length")
        for i in (0, R // 2, R - 1):
            need(cell["scalar"](cell["stat"](r["draws"][i])) - r["T0"] == r["null"][i], "null shift %d does not recompute" % i)
    say("[selftest] null structure    : %d draws per fixture, anchor-matched (per-anchor counts equal), no exposed question,"
        " shifts recompute exactly from their removal sets" % R)
    # (8) refusal: an anchor with too few non-exposed questions
    small = _mk("a-E70", "RUBRIC-512", "E70", [(1, "S", 1, 0), (2, "S", 0, 0), (3, "T", 1, 1)] + rows)
    _expect_exit(lambda: evaluate_cell(small, frozenset({1, 2}), 10, 1), "[NULL]", "anchor-matched removal impossible")
    # determinism
    r1b = evaluate_cell(cell, E_leak, R, 101)
    need(r1b["null"] == r1["null"] and r1b["draws"] == r1["draws"], "the null is not deterministic at a fixed seed")
    say("[selftest] refusal [NULL] on an anchor with too few candidates; the null is deterministic at a fixed seed")
    return cell, rows, kinds, dict(leak=r1, typical=r2, opposite=r3, k0=r4, c0=r5), dict(leak=E_leak, typ=E_typ, opp=E_opp)


def selftest_sets(tmp, say):
    ev = os.path.join(tmp, "evidence"); os.makedirs(ev)
    pool_ids = frozenset(range(1, 200))
    spec = {}
    for name, n in (("E28", 28), ("E70", 70), ("E14", 14), ("E74", 74)):
        ids = sorted(random.Random(n).sample(range(1, 200), n))
        body = "".join("%d\n" % q for q in ids).encode("ascii")
        with open(os.path.join(ev, "SPLIT-EXPOSURE_%s.txt" % name), "wb") as f:
            f.write(body.replace(b"\n", b"\r\n") if name == "E14" else body)       # E14 rendered CRLF: pinned as LF
        spec[name] = dict(file="SPLIT-EXPOSURE_%s.txt" % name, n=n, sha256_lf=hashlib.sha256(body).hexdigest())
    got = load_sets(spec, ev, pool_ids, _quiet)
    need(all(len(got[k]) == spec[k]["n"] for k in spec), "set counts")
    bad = {k: dict(v) for k, v in spec.items()}; bad["E28"]["sha256_lf"] = None
    _expect_exit(lambda: load_sets(bad, ev, pool_ids, _quiet), "[SETS] the sha256-lf pin", "unset pin")
    bad = {k: dict(v) for k, v in spec.items()}; bad["E70"]["sha256_lf"] = "0" * 64
    _expect_exit(lambda: load_sets(bad, ev, pool_ids, _quiet), "[SETS] SPLIT-EXPOSURE_E70.txt sha256-lf", "sha mismatch")
    bad = {k: dict(v) for k, v in spec.items()}; bad["E74"]["n"] = 75
    _expect_exit(lambda: load_sets(bad, ev, pool_ids, _quiet), "[SETS] SPLIT-EXPOSURE_E74.txt has 74 ids", "count mismatch")
    _expect_exit(lambda: load_sets(spec, ev, frozenset(range(1, 100)), _quiet), "[SETS] SPLIT-EXPOSURE_E", "id outside the pool")
    with open(os.path.join(ev, "unsorted.txt"), "w") as f:
        f.write("5\n3\n")
    _expect_exit(lambda: read_set(os.path.join(ev, "unsorted.txt")), "[SETS]", "unsorted set file")
    with open(os.path.join(ev, "junk.txt"), "w") as f:
        f.write("5\nx7\n")
    _expect_exit(lambda: read_set(os.path.join(ev, "junk.txt")), "[SETS]", "non-integer line")
    say("[selftest] exposed sets: synthetic E28/E70/E14/E74 load (E14 rendered CRLF hashes as LF); unset pin, sha mismatch,"
        " count mismatch, an id outside the pool, unsorted and non-integer files all REFUSE")
    # sidecars, fingerprints, write-once, connection log
    db = os.path.join(tmp, "x.db")
    with open(db, "wb") as f:
        f.write(b"SQLite format 3\0" + b"\0" * 100)
    check_sidecars([db])
    open(db + "-wal", "wb").close(); check_sidecars([db])
    with open(db + "-journal", "wb") as f:
        f.write(b"x" * 8)
    _expect_exit(lambda: check_sidecars([db]), "[SIDECAR]", "non-empty -journal")
    os.remove(db + "-journal")
    with open(db + "-wal", "wb") as f:
        f.write(b"x" * 32)
    _expect_exit(lambda: check_sidecars([db]), "[SIDECAR]", "non-empty -wal")
    os.remove(db + "-wal")
    fp1 = fingerprint([db]); compare_fingerprints(fp1, fingerprint([db]), _quiet)
    with open(db, "ab") as f:
        f.write(b"!")
    _expect_exit(lambda: compare_fingerprints(fp1, fingerprint([db]), _quiet), "[INPUTS]", "changed input")
    out = os.path.join(tmp, "outcome.txt")
    write_once(out, "a\n")
    _expect_exit(lambda: write_once(out, "b\n"), "[WRITE-ONCE]", "second write")
    need(open(out).read() == "a\n", "write-once overwrote")
    _expect_exit(lambda: check_connlog(["file:/x/y.db?mode=ro"], "/x/stack_v2_promptv2_x12all.db"), "[HYGIENE]", "non-immutable open")
    _expect_exit(lambda: check_connlog(["file:/x/snapshots_frozen.db?mode=ro&immutable=1"], "/x/s.db"), "[HYGIENE]", "snapshots_frozen")
    say("[selftest] hygiene: -wal / -journal non-empty REFUSE (empty admitted); a changed input REFUSES the write; the outcome"
        " is write-once (mode x; a second write refused, content intact); the connection log refuses a non-immutable open"
        " and snapshots_frozen.db")


def selftest_cert(say, workers_check=True):
    """The imported CERT path on cert_under_filter's own synthetic fixture: readout()'s C1 composition is bit-identical
    to cert's _pipeline -> readout, on the full data and on a question-reduced copy; the CERT cell's null is
    deterministic across worker counts; its C0 passes and refuses."""
    B = 40
    D = cuf.synth("adverse", n_q=110, seed=5)
    err = io.StringIO()
    t0 = time.time()
    with contextlib.redirect_stderr(err):
        S, pins, res, arms = cuf._pipeline(D, [].append, B, min_anchors=2)
    mine = cert_stat(D, frozenset(), B, 2)
    ref = res["st"]
    fields = ("delta", "WF", "WR_mean", "n_edges", "n_anchors", "lo", "hi", "se")
    need(all(mine[f] == ref[f] for f in fields) and mine["verdict"] == res["c1"],
         ("cert composition differs from readout", {f: (mine[f], ref[f]) for f in fields}, mine["verdict"], res["c1"]))
    qs = sorted({r[3] for r in D["rows"]})
    removed = frozenset(random.Random(3).sample(qs, 15))
    D_red = dict(D, rows=[r for r in D["rows"] if r[3] not in removed])
    with contextlib.redirect_stderr(err):
        S2, pins2, res2, arms2 = cuf._pipeline(D_red, [].append, B, min_anchors=2)
    mine2 = cert_stat(D, removed, B, 2)
    need(all(mine2[f] == res2["st"][f] for f in fields) and mine2["verdict"] == res2["c1"],
         ("cert composition differs on the reduced copy", {f: (mine2[f], res2["st"][f]) for f in fields}))
    need(bool(mine2["delta"] != mine["delta"]) or bool(mine2["WF"] != mine["WF"]) or bool(mine2["WR_mean"] != mine["WR_mean"]),
         "the reduced copy did not change the readout (vacuous fidelity check)")
    # cert's C4 branch: an anchor that disconnects (Gamma) and one below the 200-row floor under F (Delta) leave C1
    D3 = cuf.synth("adverse", gamma_disconnect=True, delta_floor=True)
    with contextlib.redirect_stderr(err):
        S3, pins3, res3, arms3 = cuf._pipeline(D3, [].append, B, min_anchors=2)
    mine3 = cert_stat(D3, frozenset(), B, 2)
    need(all(mine3[f] == res3["st"][f] for f in fields) and mine3["verdict"] == res3["c1"],
         ("cert composition differs on the disconnect/floor fixture", {f: (mine3[f], res3["st"][f]) for f in fields}))
    need(sorted(mine3["removed_anchors"]) == ["Delta", "Gamma"], ("C4 removal", mine3["removed_anchors"]))
    say("[selftest] CERT composition on cert's disconnect + floor fixture: anchors removed %s (Gamma disconnects, Delta below"
        " the 200-row floor), Delta_W %+.2f over %d anchors: BIT-IDENTICAL to readout" % (mine3["removed_anchors"],
                                                                                    mine3["delta"], mine3["n_anchors"]))
    say("[selftest] CERT composition: cert_c1 vs cert's own _pipeline -> readout (B %d, 2 anchors): full data Delta_W %+.2f"
        " [%+.2f, %+.2f] %s, reduced copy (15 questions removed) Delta_W %+.2f [%+.2f, %+.2f] %s: every field (%s) and the"
        " verdict BIT-IDENTICAL (%.0f s)" % (B, mine["delta"], mine["lo"], mine["hi"], mine["verdict"], mine2["delta"],
                                            mine2["lo"], mine2["hi"], mine2["verdict"], ", ".join(fields), time.time() - t0))
    # the CERT cell end to end with a small null; C0 recorded from the full stat itself (pins = the fixture's own)
    rec = cert_c0_fields(mine)
    exposed = frozenset(q for q in qs if q % 17 == 0)
    R = 6
    c1 = make_cert_cell(D, B, 2, 1, rec, None)
    rc1 = evaluate_cell(c1, exposed, R, NULL_SEED0 + 13)
    need(rc1["status"] in ("FLAGGED", "NOT FLAGGED") and len(rc1["null"]) == R, ("cert cell", rc1["status"]))
    if workers_check:
        c2 = make_cert_cell(D, B, 2, 2, rec, None)
        with contextlib.redirect_stderr(err):
            rc2 = evaluate_cell(c2, exposed, R, NULL_SEED0 + 13)
        need(rc2["null"] == rc1["null"] and rc2["delta"] == rc1["delta"], "the CERT null differs between 1 and 2 workers")
    badrec = dict(rec, delta="-7.15")
    rc3 = evaluate_cell(make_cert_cell(D, B, 2, 1, badrec, None), exposed, R, 1)
    need(rc3["status"] == "UNDETERMINED (BY VALIDITY)" and "null" not in rc3, "CERT C0 mismatch did not refuse")
    say("[selftest] CERT cell: k %d rows on %d exposed questions; delta %+.2f edges, null (R %d) [%+.2f, %+.2f] -> %s; identical"
        " at 1 and 2 workers; a recorded -7.15 against the fixture's %s -> %s"
        % (rc1["k"], rc1["k_q"], float(rc1["delta"]), R, rc1["lo"], rc1["hi"], rc1["status"], rec["delta"], rc3["status"]))
    return c1, rc1


def selftest_readout(say, engine, cert_cell, cert_res):
    """Every registered print branch executed through readout()/predictions()/falsifier_lines() - the functions --run uses."""
    cell, rows, kinds, fx, Es = engine
    results, cells = {}, {}
    # a scored, flagged, SCOREABLE leak cell; a closure-qualifying opposite cell; bounded / reachable; descriptive cells
    spec = {
        "a-E28": ("RUBRIC-512", "E28", Es["typ"], "DESCRIPTIVE-ONLY", 0.0),
        "a-E70": ("RUBRIC-512", "E70", Es["leak"], "DESCRIPTIVE-ONLY", 0.0),
        "b-E28": ("RUBRIC-512-SS", "E28", Es["leak"], "SCOREABLE", 0.010),
        "b-E70": ("RUBRIC-512-SS", "E70", Es["opp"], "SCOREABLE", 0.010),
        "c-E28": ("RUBRIC-512-R", "E28", Es["typ"], "SCOREABLE", 0.50),
        "c-E70": ("RUBRIC-512-R", "E70", Es["typ"], "SCOREABLE", 0.010),
        "d-E28": ("LEAF-POWERED", "E28", frozenset({424242}), "SCOREABLE", 0.020),
        "d-E70": ("LEAF-POWERED", "E70", Es["typ"], "SCOREABLE", 0.020),
        "e-LADDER": ("LADDER", "E14", Es["typ"], "SCOREABLE", 0.020),
        "e-STACK": ("STACK", "E14", Es["typ"], "SCOREABLE", 0.004),
        "e-STACKv2": ("STACK-v2", "E14", Es["typ"], "SCOREABLE", 0.026),
        "e-J6": ("J6", "E14", Es["leak"], "DESCRIPTIVE-ONLY", 0.001),
    }
    R = 300
    for j, (cid, (consumer, set_id, E, support, dstar)) in enumerate(sorted(spec.items()), 1):
        kind = CONSUMERS[consumer]["kind"]
        if kind == "accuracy":
            rws = [(q, a, x) for q, a, x, _y in rows]
            c = _mk(cid, consumer, set_id, rws, kind="accuracy", leak_sign=CONSUMERS[consumer]["leak_sign"], delta_star=dstar,
                    support=support, verdict=lambda st: "OK" if st["T"] >= Fraction(839, 1000) else "FAIL")
        else:
            c = _mk(cid, consumer, set_id, rows, leak_sign=CONSUMERS[consumer]["leak_sign"], delta_star=dstar, support=support,
                    closure_band_pp=CONSUMERS[consumer].get("closure_band_pp"))
        if cid == "c-E70":
            c = dict(c, recorded=dict(c["recorded"], T_pp="+9.9"))        # a C0 failure inside the family
        cells[cid] = c
        results[cid] = evaluate_cell(c, E, R, 500 + j)
    cells["f-CERT"] = cert_cell; results["f-CERT"] = cert_res
    L = []
    w = readout(L.append, results, cells, stopped=set())
    L2 = []
    readout(L2.append, results, cells, stopped={"e-J6"})
    # crafted prediction outcomes: HELD / FAILED / UNDETERMINED for every prediction
    def fake(cid, status, delta=Fraction(0), pct=0.5, same=True, set_id=None):
        return dict(id=cid, set=set_id or [c[2] for c in CELL_TABLE if c[0] == cid][0], status=status, delta=delta, pct=pct,
                    v_with="X", v_without="X" if same else "Y", dir="LEAK", T1=Fraction(0))
    allnf = {cid: fake(cid, "NOT FLAGGED", pct=0.9) for cid in CELL_IDS}
    predictions(_quiet, allnf)                                                          # all HELD
    f2 = dict(allnf); f2["a-E28"] = fake("a-E28", "FLAGGED"); f2["d-E28"] = fake("d-E28", "FLAGGED")
    f2["e-STACK"] = fake("e-STACK", "FLAGGED"); f2["f-CERT"] = fake("f-CERT", "FLAGGED")
    f2["b-E70"] = fake("b-E70", "UNDETERMINED (BY SUPPORT)")
    f2["e-J6"] = fake("e-J6", "UNDETERMINED (BY SUPPORT)"); f2["e-LADDER"] = fake("e-LADDER", "UNDETERMINED (BY SUPPORT)")
    f2["e-STACKv2"] = fake("e-STACKv2", "UNDETERMINED (BY SUPPORT)")
    predictions(_quiet, f2)                                                             # FAILED
    f3 = {cid: v for cid, v in allnf.items() if cid in ("f-CERT",)}
    f3.update({cid: fake(cid, "UNDETERMINED (BY VALIDITY)") for cid in ("a-E28",)})
    predictions(_quiet, f3)                                                             # UNDETERMINED
    f4 = dict(allnf); f4["f-CERT"] = fake("f-CERT", "UNDETERMINED (BY SUPPORT)")
    for cid in ("a-E70", "d-E70", "e-J6"):
        f4[cid] = fake(cid, "UNDETERMINED (BY SUPPORT)")
    predictions(_quiet, f4)                                                             # P1-P4, P5 UNDETERMINED
    predictions(_quiet, {"f-CERT": fake("f-CERT", "NOT FLAGGED", pct=0.9)})             # P6 UNDETERMINED (not built)
    # the P5 C2-change branch and the falsifier's descriptive-flag branch on a crafted family
    f5 = dict(allnf); f5["b-E28"] = fake("b-E28", "NOT FLAGGED", same=False)
    predictions(_quiet, f5)
    # a family where nothing flags: the no-consumer-branch falsifier line
    falsifier_lines(_quiet, allnf, cells)
    # the support-measured-disagrees branch (a DESCRIPTIVE-ONLY cell whose measured MDE is below Delta*)
    dcell = dict(cells["a-E28"], delta_star=0.5, support="DESCRIPTIVE-ONLY")
    support_block(_quiet, dcell, results["a-E28"])
    txt = "\n".join(L)
    need("-> FAILED" in txt or "-> HELD" in txt or "-> UNDETERMINED" in txt, "no prediction line printed")
    need(any("CELL e-J6" in s and "NOT BUILT" in L2[i + 1] for i, s in enumerate(L2[:-1])), "the STOPPED print branch")
    return w, L


# ------------------------------------------------------------------------------------------ route (A) selftest
SYN_ORIG = """import os, sqlite3
import syn_helper
DB = %(db)r
QUIRK = %(quirk)r
MODE = %(mode)r
PORT = %(port)d
SIDE = %(side)r
ENVF = %(envf)r
TOTAL = %(total)d


def analyze():
    if os.environ.get("AZURE_AI_API_KEY"):
        raise RuntimeError("a judge credential is visible to the consumer")
    if MODE == "stackuser":
        import stack_judge                      # the REAL module: only possible outside cert_under_filter's process (A5)
        _ = stack_judge.PROMPT
    con = sqlite3.connect(DB)                   # a plain read-write open, as the originals do
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, qid INTEGER, anchor TEXT, x INTEGER, y INTEGER)")
    con.commit()
    total = con.execute("SELECT count(*) FROM verdicts").fetchone()[0]
    if MODE == "removal_fail" and total < TOTAL:
        raise RuntimeError("this original fails only on a reduced input")
    if MODE == "writer":
        con.execute("INSERT INTO verdicts VALUES (0, 0, 'A1', 1, 1)")
        con.commit()
    if MODE == "create":
        con.execute("CREATE TABLE IF NOT EXISTS brand_new (a INTEGER)")
        con.commit()
    if MODE == "socket":
        import socket
        sk = socket.create_connection(("127.0.0.1", PORT), timeout=2)
        sk.close()
    if MODE == "dbapi2":
        from sqlite3 import dbapi2
        w = dbapi2.connect(DB)
        w.execute("CREATE TABLE IF NOT EXISTS pwned (a INTEGER)")
        w.commit()
        w.close()
    if MODE == "subclass":
        class C(sqlite3.Connection):
            pass
        w = C(DB)
        w.execute("CREATE TABLE IF NOT EXISTS pwned2 (a INTEGER)")
        w.commit()
        w.close()
    if MODE == "open_write":
        with open(SIDE, "w") as f:
            f.write("an original that writes a file")
    if MODE == "raw_socket":
        import _socket
        rs = _socket.socket()
        rs.settimeout(2)
        try:
            rs.connect(("127.0.0.1", PORT))
        except Exception:
            pass                                # swallowed: the refusal must still void the cell
        rs.close()
    if MODE == "unpinned_helper":
        import results_index                    # a tools/analysis module that is NOT in the helper pins (D5)
        _ = results_index.REQUIRED
    if MODE == "dotenv":
        try:
            open(ENVF).read()
        except Exception:
            pass                                # swallowed: the refusal must still void the cell
    skip = syn_helper.quirk_ids(QUIRK)          # a helper that opens AND CLOSES its own connection (D1)
    rows = {}
    for mid, q, anc, x, y in con.execute("SELECT mid, qid, anchor, x, y FROM verdicts ORDER BY mid"):
        if q in skip:
            continue
        rows[mid] = (x, y, anc)
    con.close()                                 # the original closes its connection before printing (D1)
    n = len(rows)
    b = sum(1 for v in rows.values() if v[0] and not v[1])
    c = sum(1 for v in rows.values() if v[1] and not v[0])
    print("=== SYN: %%d scored matches ===" %% n)
    print("  PRIMARY %%d:%%d p=%%.4f -> %%s" %% (b, c, 0.5, "PASS" if b > c else "FAIL"))
"""

SYN_HELPER = """import sqlite3


def quirk_ids(path):
    ev = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
    try:
        return {q for (q,) in ev.execute("SELECT qid FROM quirk")}
    finally:
        ev.close()
"""


def _syn_module(moddir, name, db, quirk, mode, port=0, side="", envf="", total=0):
    with open(os.path.join(moddir, "syn_helper.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(SYN_HELPER)
    path = os.path.join(moddir, name + ".py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(SYN_ORIG % dict(db=db, quirk=quirk, mode=mode, port=port, side=side, envf=envf, total=total))
    ident = sxc.lf_identity(path)
    return dict(module=name, module_dir=moddir, blob=ident["blob"], sha256_lf16=ident["sha256_lf16"], setup=[], entry="analyze",
                args=[], kind="paired",
                patterns=[dict(name="header", re=r"^=== SYN: (?P<n>\d+) scored matches ===$"),
                          dict(name="primary", re=r"^  PRIMARY (?P<b>\d+):(?P<c>\d+) p=(?P<p>\d\.\d{4}) -> (?P<v>PASS|FAIL)$")],
                stat=dict(b="b", c="c", n="n", sign=1), verdict=["v"],
                removal={os.path.basename(db): ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
                probe=dict(mode="line", func="analyze", line="rows[mid] = (x, y, anc)", expr="(mid, q, anc)"),
                anchor_sql=None, ret_locals=[])


def _syn_db(path, rows, quirk_path=None, quirk=()):
    c = sqlite3.connect(path)
    c.execute("CREATE TABLE verdicts (mid INTEGER, qid INTEGER, anchor TEXT, x INTEGER, y INTEGER)")
    c.executemany("INSERT INTO verdicts VALUES (?,?,?,?,?)", [(i + 1, q, a, x, y) for i, (q, a, x, y) in enumerate(rows)])
    c.commit(); c.close()
    if quirk_path:
        c = sqlite3.connect(quirk_path)
        c.execute("CREATE TABLE quirk (qid INTEGER)")
        c.executemany("INSERT INTO quirk VALUES (?)", [(q,) for q in sorted(quirk)])
        c.commit(); c.close()


def selftest_route(tmp, say, engine):
    """Route (A) BY EXECUTION on synthetic originals, each run in its own subprocess by the same code --run uses."""
    cell_g, rows, kinds, fx, Es = engine
    moddir = os.path.join(tmp, "originals"); os.makedirs(moddir)
    db = os.path.join(tmp, "syn_verdicts.db"); qdb = os.path.join(tmp, "syn_quirk.db")
    quirk = {q for q, _a, _x, _y in rows if q % 29 == 0}
    _syn_db(db, rows, qdb, quirk)
    kept = [r for r in rows if r[0] not in quirk]
    b0 = sum(1 for r in kept if r[2] and not r[3]); c0_ = sum(1 for r in kept if r[3] and not r[2]); n0 = len(kept)
    rec = dict(T_pp="%+.1f" % (100.0 * (b0 - c0_) / n0), b=str(b0), c=str(c0_), n=str(n0))
    c0fn = lambda st: dict(T_pp=_tpp(st), b=str(st["b"]), c=str(st["c"]), n=str(st["n"]))
    fp0 = fingerprint([db, qdb])
    saved_key = os.environ.get("AZURE_AI_API_KEY")
    os.environ["AZURE_AI_API_KEY"] = "selftest-placeholder-not-a-key"          # A4: the child must never see it
    lsock = socket.socket(); lsock.bind(("127.0.0.1", 0)); lsock.listen(4); lsock.setblocking(False)
    port = lsock.getsockname()[1]
    try:
        spec = _syn_module(moddir, "syn_orig_clean", db, qdb, "stackuser")
        cell = make_route_cell("a-E28", "SYN", "E28", 0.01, "SCOREABLE", 1.0, 0.2, 2, tmp, spec=spec, recorded=rec, c0fn=c0fn,
                               kind="paired", leak_sign=-1)
        R = 40
        rr_ = evaluate_cell(cell, Es["leak"], R, 777)
        need(rr_["status"] in ("FLAGGED", "NOT FLAGGED"), ("route (A) synthetic cell", rr_["status"], rr_.get("c0")))
        # the same statistic through the generic engine on the same (quirk-filtered) rows: identical null, identical shift
        gcell = make_generic_cell("a-E28", "SYN", "E28", "paired", kept, rec, _paired_verdict, -1, 0.01, "SCOREABLE")
        gcell["c0"] = c0fn
        gr = evaluate_cell(gcell, Es["leak"], R, 777)
        need(gr["null"] == rr_["null"] and gr["delta"] == rr_["delta"] and gr["status"] == rr_["status"]
             and gr["draws"] == rr_["draws"], "the route (A) null differs from the same statistic computed on the same rows")
        reps = cell["reports"]
        need(all(r["pid"] != os.getpid() for r in reps) and len({r["pid"] for r in reps}) == len(reps),
             "A5: a consumer job did not run in its own subprocess")
        need(all(r["attempts"] == 0 and not r["secrets_left"] and not r["fp_changed"] and not r["refusals"] for r in reps),
             "A3/A4 on the clean original")
        need(all(set(r["local_modules"]) >= {"stack_judge", "rejudge_grok"} for r in reps), "D5: local modules not reported")
        kinds_seen = {k for r in reps for e in r["connlog"].values() for k in e["kinds"]}
        need("immutable" in kinds_seen and any(k.startswith("in-memory copy") for k in kinds_seen),
             ("A2 kinds", kinds_seen))
        need(all(e["uri"].endswith("?mode=ro&immutable=1") for r in reps for p, e in r["connlog"].items() if p != ":memory:"),
             "A2: an open was not redirected to the immutable URI")
        need(all(set(r2["removed_rows"]) == {"syn_verdicts.db"} for r in reps[1:] for r2 in r["results"]),
             "the removal was not applied to the original's input")
        say("[selftest] ROUTE (A) synthetic original (plain read-write connect + no-op CREATE IF NOT EXISTS + commit, a quirk"
            " table the engine cannot see, the REAL stack_judge imported): C0 %s; %d child processes (none the parent), every"
            " open redirected (%s), 0 outbound attempts, the credential stripped; delta %+.3f pp, null (R %d, 2 chunks)"
            " IDENTICAL to the same statistic computed on the same rows -> %s"
            % ("PASS" if not rr_["c0"] else rr_["c0"], len(reps), "; ".join(sorted(kinds_seen)), pp(rr_["delta"]), R, rr_["status"]))
        CONSUMERS["SYN"] = dict(CONSUMERS["RUBRIC-512"], script="(synthetic original)", recorded_text="(synthetic)")
        try:
            LL = []
            cell_lines(LL.append, cell, rr_)
        finally:
            CONSUMERS.pop("SYN", None)
        for l in LL[1:9]:
            say("[selftest]   | " + l)
        txt = "\n".join(LL)
        need("ROUTE (A)" in txt and "connection log" in txt and "outbound connection attempts 0" in txt and "capture (A6)" in txt,
             "the route (A) print block")
        # A7 NEGATIVE CONTROLS: a real write, a missing-table CREATE, an outbound call, and the bypass paths of the READY
        # review (D3 / D4): sqlite3.dbapi2.connect, direct sqlite3.Connection construction, open() for writing, a raw
        # _socket connect (swallowed), a .env read (swallowed) -> UNDETERMINED (BY VALIDITY), nothing lands
        side = os.path.join(tmp, "side_effect.txt"); envf = os.path.join(tmp, ".env")
        with open(envf, "w") as f:
            f.write("AZURE_GROK_API_KEY=selftest-placeholder-not-a-key\n")
        for mode, marker in (("writer", "readonly"), ("create", "readonly"), ("socket", "[A4]"), ("dbapi2", "readonly"),
                             ("subclass", "refused in the child"), ("open_write", "open for writing"), ("raw_socket", "[A4]"),
                             ("dotenv", "open .env"), ("unpinned_helper", "[A1/D5]")):
            sp = _syn_module(moddir, "syn_orig_%s" % mode, db, qdb, mode, port, side=side, envf=envf)
            nc = make_route_cell("a-E70", "SYN-%s" % mode, "E70", 0.01, "SCOREABLE", 1.0, 0.2, 1, tmp, spec=sp, recorded=rec,
                                 c0fn=c0fn, kind="paired", leak_sign=-1)
            r_ = evaluate_cell(nc, Es["leak"], 5, 1)
            why = " ".join(str(m) for m in r_["c0"])
            need(r_["status"] == "UNDETERMINED (BY VALIDITY)" and marker in why, ("negative control %s" % mode, r_["status"], why))
            say("[selftest] NEGATIVE CONTROL %-7s -> %s (%s)" % (mode, r_["status"], why[:150]))
        try:
            conn_, _ = lsock.accept()
            conn_.close()
            accepted = True
        except (BlockingIOError, OSError):
            accepted = False
        need(not accepted, "A4: the socket original reached the listener")
        need(fingerprint([db, qdb]) == fp0, "A3: a synthetic cache changed (a write landed)")
        need(not os.path.exists(side), "A3: an original wrote a file")
        say("[selftest] A3 / A4: the listener received 0 connections; both synthetic caches unchanged (sha256_16, size, mtime);"
            " no side file written")
        # a failure that occurs only on a REMOVAL run is labelled at the removal stage, never as a C0 failure (D6)
        spr = _syn_module(moddir, "syn_orig_removal_fail", db, qdb, "removal_fail", total=len(rows))
        rrf = evaluate_cell(make_route_cell("a-E28", "SYN-rf", "E28", 0.01, "SCOREABLE", 1.0, 0.2, 1, tmp, spec=spr,
                                            recorded=rec, c0fn=c0fn, kind="paired", leak_sign=-1), Es["leak"], 5, 1)
        need(rrf["status"] == "UNDETERMINED (BY VALIDITY)" and rrf.get("stage") == "REMOVAL" and not rrf["c0"],
             ("removal-stage failure", rrf.get("stage"), rrf["c0"]))
        LLr = []
        CONSUMERS["SYN-rf"] = dict(CONSUMERS["RUBRIC-512"], script="(synthetic original)", recorded_text="(synthetic)")
        try:
            cell_lines(LLr.append, dict(cell, id="a-E28", consumer="SYN-rf", reports=[]), rrf)
        finally:
            CONSUMERS.pop("SYN-rf", None)
        need(any("C0 PASSED; a REMOVAL run" in l for l in LLr) and not any("does NOT reproduce" in l for l in LLr),
             "a removal-stage failure printed as a C0 failure")
        p6 = []
        predictions(p6.append, {"a-E28": rrf})
        need(any(l.lstrip().startswith("P6") and "C0 failed: none" in l for l in p6), "P6 counted a removal-stage failure as C0")
        say("[selftest] a failure on REMOVAL runs only -> UNDETERMINED (BY VALIDITY) at the removal stage; printed and counted"
            " as such, never as C0 (P6 'C0 failed: none')")
        # hazard (d): a scored qid outside the pool of record voids the cell
        POOL_IDS[0] = frozenset(q for q, *_ in kept if q % 31 != 0)
        try:
            rid = evaluate_cell(gcell, Es["leak"], 5, 1)
        finally:
            POOL_IDS[0] = None
        need(rid["status"] == "UNDETERMINED (BY VALIDITY)" and rid.get("stage") == "ID-SPACE" and rid["outside"] > 0,
             ("hazard (d)", rid.get("stage")))
        LLd = []
        cell_lines(LLd.append, dict(gcell, consumer="RUBRIC-512"), rid)
        need(any("outside the pool of record" in l for l in LLd), "hazard (d) print")
        say("[selftest] hazard (d): %d scored qids outside a pool -> UNDETERMINED (BY VALIDITY), printed" % rid["outside"])
        # A1: a wrong pin refuses (at launch, and in the child)
        bad = dict(spec, blob="0" * 40)
        _expect_exit(lambda: check_route_pins({"SYN": bad}), "[A1]", "wrong route pin at launch")
        rb = evaluate_cell(make_route_cell("a-E28", "SYN-pin", "E28", 0.01, "SCOREABLE", 1.0, 0.2, 1, tmp, spec=bad,
                                           recorded=rec, c0fn=c0fn, kind="paired", leak_sign=-1), Es["leak"], 5, 1)
        need(rb["status"] == "UNDETERMINED (BY VALIDITY)" and "[A1]" in " ".join(str(m) for m in rb["c0"]), ("A1 child", rb["c0"]))
        # a non-empty -wal beside an input is a failed precondition of the run
        wdb = os.path.join(tmp, "syn_walled.db"); _syn_db(wdb, rows[:50])
        with open(wdb + "-wal", "wb") as f:
            f.write(b"x" * 64)
        sw = _syn_module(moddir, "syn_orig_walled", wdb, qdb, "plain")
        _expect_exit(lambda: evaluate_cell(make_route_cell("a-E28", "SYN-wal", "E28", 0.01, "SCOREABLE", 1.0, 0.2, 1, tmp,
                                                           spec=sw, recorded=rec, c0fn=c0fn, kind="paired", leak_sign=-1),
                                           Es["leak"], 5, 1), "[SIDECAR]", "a non-empty -wal in a route (A) child")
        say("[selftest] A1: a wrong pin refuses at launch and in the child; a non-empty -wal beside a consumer's input REFUSES"
            " the run ([SIDECAR], a failed precondition)")
        return cell, rr_
    finally:
        lsock.close()
        if saved_key is None:
            os.environ.pop("AZURE_AI_API_KEY", None)
        else:
            os.environ["AZURE_AI_API_KEY"] = saved_key


def _func_lines(path, func):
    import ast
    src = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    for node in ast.parse(src).body:
        if isinstance(node, ast.FunctionDef) and node.name == func:
            return src.splitlines()[node.lineno - 1:node.end_lineno]
    raise SystemExit("[CHECK] %s has no function %s" % (path, func))


def _str_constants(path):
    import ast
    src = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    return [n.value for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


RECORDED_OUTCOMES = {
    "RUBRIC-512": "experiment_results/rubric_512/outcome.txt",
    "RUBRIC-512-SS": "experiment_results/rubric_512/generic_ss_outcome.txt",
    "RUBRIC-512-R": "experiment_results/rubric_512/grok_reasoning_outcome.txt",
    "LEAF-POWERED": "experiment_results/x12_crossdomain/leaf_powered_outcome.txt",
    "LADDER": "experiment_results/x12_crossdomain/rubric_ladder_outcome.txt",
    "STACK-v2": "experiment_results/x12_crossdomain/stack_v2_outcome.txt",
    "J6": "experiment_results/x12_crossdomain/j6_outcome.txt",
}


def selftest_route_static(say):
    """The 12 real route (A) cells, WITHOUT running them: A1 pins; each probe line pinned exactly once in its function;
    each headline pattern parses the format literal of the original's own source; and the tracked recorded outcome
    texts replay through the pinned patterns and C0 to the registered headline, to the digit."""
    lines = check_route_pins()
    need(sum(1 for l in lines if l.startswith("  A1 ")) == 8 and sum(1 for l in lines if l.startswith("  D5 ")) == len(HELPER_PINS) and set(sxc.ROUTE_A_SPECS) == {c for c in CONSUMERS if CONSUMERS[c]["route"] == "A"}, "route specs")
    for consumer, spec in sorted(sxc.ROUTE_A_SPECS.items()):
        path = os.path.join(ORIG_DIR, spec["module"] + ".py")
        if spec["probe"]["mode"] == "line":
            fl = _func_lines(path, spec["probe"]["func"])
            need(sum(1 for l in fl if l.strip() == spec["probe"]["line"]) == 1, "probe line of %s" % consumer)
    import re
    for consumer, pname, lead, dummy in sxc.FORMAT_PINS:
        spec = sxc.ROUTE_A_SPECS[consumer]
        consts = [c for c in _str_constants(os.path.join(ORIG_DIR, spec["module"] + ".py")) if c.startswith(lead)]
        need(len(consts) == 1, "format literal %r of %s: %d candidates" % (lead, consumer, len(consts)))
        line = consts[0] % dummy
        pat = [p for p in spec["patterns"] if p["name"] == pname][0]
        need(re.match(pat["re"], line), "pattern %s/%s does not parse the original's own format: %r" % (consumer, pname, line))
    replayed = []
    for consumer, rel in sorted(RECORDED_OUTCOMES.items()):
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        text = open(path, "rb").read().decode("utf-8", errors="replace")
        spec = sxc.ROUTE_A_SPECS[consumer]
        try:
            parsed = sxc.parse_headline(spec["patterns"], text)
        except sxc.Refused as e:
            raise SystemExit("[CHECK] recorded outcome %s: %s" % (rel, e))
        if spec["kind"] == "paired":
            st = route_stat(spec, dict(parsed=parsed, ret={}))
        else:
            n = int(parsed["n"])
            st = dict(T=Fraction(int(round(float(parsed["acc"]) * n)), n), n=n)
        mism = c0_mismatches(dict(c0=lambda s_: C0_ROUTE[consumer](s_), recorded=CONSUMERS[consumer]["recorded"]), st)
        need(not mism, ("C0 replay of %s" % rel, mism))
        replayed.append(consumer)
    say("[selftest] route (A) static: A1 pins of the 7 originals (8 consumers) checked; 7 probe lines pinned exactly once;"
        " %d headline patterns parse the originals' own format literals; the recorded outcome texts of %d consumers (%s)"
        " replay through the pinned patterns and C0 to the registered headline, to the digit (STACK v1's text is not"
        " tracked: its C0 is left to the dry-run)" % (len(sxc.FORMAT_PINS), len(replayed), ", ".join(replayed)))
    return replayed


REQUIRED_BRANCHES = tuple(b for b in REGISTERED_BRANCHES if b not in ("C0.CERT_PASS", "C0.ROUTE_PASS", "RUN.REFUSED_STOPPED",
                                                                      "A5.REFUSED"))


def selftest():
    global OUT
    tmp = tempfile.mkdtemp(prefix="ses_selftest_")
    OUT = os.path.join(tmp, "split_exposure_sensitivity_outcome.txt")
    t0 = time.time()
    real_connect = sqlite3.connect

    def guarded(db, *a, **k):
        p_ = str(db).replace("\\", "/")
        if p_ != ":memory:" and tmp.replace("\\", "/") not in p_:
            raise SystemExit("[selftest] refused to open %s: only the tempdir and :memory: are allowed" % db)
        return real_connect(db, *a, **k)
    sqlite3.connect = guarded
    try:
        say = lambda s: print(s, flush=True)
        for l in identity_lines():
            say("[selftest]" + l)
        say("[selftest] tempdir %s; NO DB of record is opened; the pool guard is not called; python -O flag %d"
            % (tmp, sys.flags.optimize))
        try:
            need(False, "probe")
        except SystemExit:
            pass
        else:
            raise RuntimeError("need(False) did not raise")
        engine = selftest_engine(say)
        selftest_sets(tmp, say)
        cert_cell, cert_res = selftest_cert(say)
        selftest_route_static(say)
        selftest_route(tmp, say, engine)
        HH = []
        hazards_header(HH.append)
        need(sum(1 for l in HH if l.lstrip().startswith(("(a)", "(b)", "(c)", "(d)"))) == 4, "the four hazards in the header")
        dry_summary(_quiet, ["a", "b"], [], [], 2)
        _expect_exit(lambda: dry_summary(_quiet, ["a"], [("b", "x")], [], 2), "[DRY-RUN]", "dry-run with a C0 failure")
        _expect_exit(lambda: dry_summary(_quiet, ["a"], [], [("b", "x")], 2), "[DRY-RUN]", "dry-run with a removal failure")
        need(check_local_modules({"rejudge_grok": dict(blob=HELPER_PINS["rejudge_grok"][0], sha256_lf16=HELPER_PINS["rejudge_grok"][1])}) == []
             and check_local_modules({"not_pinned_helper": dict(blob="x", sha256_lf16="y")}) != []
             and check_local_modules({"rubric_p8": dict(blob="0" * 40, sha256_lf16="0" * 16)}) != [], "D5 helper check")
        say("[selftest] D2: the four hazards print in the header; D6: the dry-run summary exits NONZERO on a C0 or removal"
            " failure; D5: an unpinned or changed helper is refused (launch pins: %d helpers)" % len(HELPER_PINS))
        w, L = selftest_readout(say, engine, cert_cell, cert_res)
        # the write path: the readout text written once to the tempdir outcome, then refused
        write_once(OUT, "\n".join(L) + "\n")
        _expect_exit(lambda: write_once(OUT, "x"), "[WRITE-ONCE]", "outcome rewrite")
        # every registered cell is BUILT (route (A) or CERT); --run refuses before computing when the outcome exists
        need(not stopped_cells(), ("stopped cells", sorted(stopped_cells())))
        _expect_exit(lambda: main_run(1), "[WRITE-ONCE]", "--run with an existing outcome")
        missing = [b for b in REQUIRED_BRANCHES if not HITS.get(b)]
        say("[selftest] registered print branches executed: %d of %d required (%s)"
            % (len(REQUIRED_BRANCHES) - len(missing), len(REQUIRED_BRANCHES), "all" if not missing else "MISSING %s" % missing))
        need(not missing, "branches never executed: %s" % missing)
        say("[selftest] predictions on the synthetic family: %s" % ", ".join("%s %s" % kv for kv in sorted(w["predictions"].items())))
        say("[selftest] SELFTEST PASSED in %.0f s (python -O flag %d)" % (time.time() - t0, sys.flags.optimize))
    finally:
        sqlite3.connect = real_connect


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=1, help="processes for the CERT null replicates (deterministic)")
    a = ap.parse_args(argv)
    if a.workers < 1:
        raise SystemExit("--workers must be >= 1")
    return a


if __name__ == "__main__":
    A_ = parse_args()
    check_launch()
    if A_.selftest:
        selftest()
    elif A_.dry_run:
        main_dry(A_.workers)
    else:
        main_run(A_.workers)
