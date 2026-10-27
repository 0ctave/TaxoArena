"""JV2-RATE-PROBE: at how many concurrent in-flight calls N in {1, 2, 4, 8, 12} does the grok-4-1-fast-non-reasoning
deployment stop buying throughput on the probe day, and is the gain G = rate(N*) / rate(1) worth a parallel writer?

REGISTRATION (governs everything here): docs/judge_v2_program.md L18979-L19094 (registered at bf9d80b, parent 0c10ea2;
the specialist's text block 2/3 verbatim L18984-L19058, sections 1.1-1.13; the registrar's THE ITEM, readings R1-R9,
SUPPORT (a)-(g), open items 1-3); the finding of record GROK-NR-THROUGHPUT L18908-L18977; the author's decisions
L19341-L19376 (C2 superseded for the build decision only; X2 stands); R8 met at 38ec2f3 (the K46 outcome written);
record docs/agents/results/JV2-RATE-PROBE.json. An ENGINEERING measurement of a transport: no board, recipe, reference,
judge or model claim; no verdict is read as data; SYNTHETIC-DEV payloads, no corpus item is posted.

LAUNCH SEQUENCE (run-operator; plain `python`, never `python -O`: rr.load_env relies on assert, so a launch REFUSES -O):
    python tools/analysis/jv2_rate_probe.py --selftest                 # stub HTTP server on 127.0.0.1; 0 real calls
    python -O tools/analysis/jv2_rate_probe.py --selftest              # the same under -O
    python tools/analysis/jv2_rate_probe.py --dry-run                  # 0 calls: preflight, plan, gate, accounting
    python tools/analysis/jv2_rate_probe.py --pilot --expect-plan-sha <dry-run's plan sha>     # S1's first 12
    python tools/analysis/jv2_rate_probe.py --run   --expect-plan-sha <plan sha>               # the ramp and S6
    python tools/analysis/jv2_rate_probe.py --analyze                  # the outcome of record (write-once)
Relaunch (a rollover, an interrupt, a crash): the same --run command; the ramp resumes at the step that stopped.

WHAT IS POSTED (1.2, 1.3). 398 slots, fixed by the plan: S1-S5 at N = 1, 2, 4, 8, 12 with 24 / 36 / 48 / 64 / 76
invocations (slots 1-248), S6 = 150 invocations at N* (slots 249-398) when N* >= 2. Each slot is ONE invocation of
rejudge_reasoning.call_judge_full (rule 9; its internal retry loop runs AS REGISTERED: 6 attempts, sleeps 3/6/12/24/48 s,
Retry-After ignored), single order, temperature OMITTED (payload.configure_rr), cap 8192, model
grok-4-1-fast-non-reasoning, provider azure. The system turn is the K46 recipe's (payload.build_system over
archv2_pilot.pilot.load_generic_rubric: v2 template + GENERIC_SYSTEM + GENERIC_RUBRIC + SCHEMA_INSTRUCTION), its sha256
REQUIRED equal to the K46 launch manifest's system_turn_sha256, and the template / rubric shas equal to the K46 store's
verdict.system_template_sha / rubric_sha. The user turn is rejudge_grok.build_user_prompt(query, trace_1, trace_2) with
query = rejudge_reference.with_reference(stem, (key letter, key option text, None)) (never retyped). The stem is a
seeded 10-option MCQ with a computed key (seed "JV2-RATE-PROBE:bf9d80b0ec59154434503243bbf024c109fca0fd"; kinematics,
unit conversion, arithmetic); the two responses are templated worked solutions (one reaches the key, one a
distractor), padded with computed check lines so the POSTED BODY is EXACTLY the size target. Size targets: the q10 /
q50 / q90 of the K46 run2 store's posted body lengths (zlib-decompressed LENGTHS only; no content read), assigned
cyclically within every step. [BUILDER'S READING, for the registrar: the registration names "user-message byte lengths"
read from "the posted bodies"; the only length readable without reading content is the BODY length, so the target is
the body length and "user bytes" = body bytes - the body bytes of the same system turn with an empty user turn (a
constant, identical for K46 and the probe because the system turn is byte-identical). Both are printed.]

GUARDS (in launch order; each a FAILED PRECONDITION when it refuses, never an outcome):
  -O           a launch refuses sys.flags.optimize > 0 (rr.load_env's check is an assert).
  TRANSPORT    archv2_pilot.pilot.load_transport (rr.load_env on the DATA ROOT's .env) + transport_preflight, IMPORTED,
               BEFORE any probe DB, journal or ledger row, in every launch and in the dry-run. Printed as booleans only
               (endpoint present / https / key present), the deployment name, never the key or the endpoint.
  LIVE GUARD   a non-loopback endpoint is REFUSED (at the launch and at the wire, before a request leaves) while any
               SELFTEST-ONLY setting of this module (TIME_SCALE, MUTANT, CLOCK, PROCESS_LIST, OPTIMIZE, REAL_URLOPEN,
               CORPUS_KEYS, K46_SOURCE, CEILING_OVERRIDE, HOOK), judge_v2.pool's TIME_SCALE / MUTANT switches, or a
               patched rr.time is set.
  X1           the process list (Get-CimInstance Win32_Process) at the launch and at EVERY step boundary: a python
               process running a tools/analysis script other than this process and its launch chain (a --selftest
               or --dry-run is admitted and printed) REFUSES; the K46 run2 journal must show 0 unresolved and its
               outcome file must exist (R8).
  X2           the posting day's ledger must carry NO JUDGEBENCH-REASONING-SIDE row, at the launch and at every step
               boundary; --analyze re-reads every posting day (a JudgeBench row added after the probe FAILS V1).
               ARCH-V2-PILOT-K46 rows on the day are printed, not refused (the registration's 1.2 counts the probe
               on 09-25 after K46: 26 + 5,328 + 400 = 5,754).
  CONTENT GATE split_side.stem_key of every generated stem against every item of the MMLU-Pro universe (p2dca's
               mmlu_pro table) and the union corpus (paeec's corpus_questions), both opened by pool_guard.open_ro:
               0 hits required, printed with the denominators.
  ACCOUNTING   accepted_tests_ledger.guard(JV2-RATE-PROBE, planned) (CEILINGS["JV2-RATE-PROBE"] = 400, added to that
               file by this build) and the day cap (iii) as registered: day total + 400 <= 14,000, read at the launch.
               A write-ahead journal (archv2_pilot.accounting.Journal, JOURNAL v2 at max_inflight 12, cap 400 = the
               ceiling; each step's launch label books its N in launch_bound, so the unresolved bound is the step's N
               at the database level); ACC.reconcile (orphans, ledger catch-up) and ledger == journal at the start and
               the end of every launch; the day-ledger append under judge_v2.pool.LedgerLock (JudgeBench's lock file).
  ROLLOVER     the posting day is fixed at the launch; every reservation and every send re-checks the local date; a
               change is a clean stop (a journaled send-time rollover is RAISED "DAY ROLLOVER: not sent").
  WIRE         a thread-local wrapper of urllib.request.urlopen records EVERY HTTP attempt (slot, attempt number, send
               and end times, status, Retry-After raw and in seconds, the NAMES and VALUES of x-ratelimit-* /
               retry-after* headers, the NAMES only of all response headers, and for a 429 / 5xx the provider's error
               code and the first 160 characters of its message); it never records api-key or authorization; it
               REFUSES a request whose bytes are not the slot's body BEFORE it leaves. rr is not edited.
  STOPS        1.3: the ramp stops at the FIRST INADMISSIBLE step; within a step, no further reservation after 3
               invocations exhausted on 429 or 10 HTTP-429 attempts (the step is then inadmissible; its reserved
               invocations count). A KeyboardInterrupt sets the ABORT flag: no HTTP attempt leaves after it (the
               wrapper raises inside rr, which does not catch it), the in-flight invocations are resolved, the ledger
               is appended.
  PILOT 12     S1's first 12 (--pilot): PASS iff 12 invocations RETURNED, unparsed (judge_v2.writer.classify:
               rj.parse_judge on rr.strip_think) <= 5% of 12 (i.e. 0), no finish_reason length or content_filter,
               no raised (non-200 exhausted) invocation. --run refuses without the PASS file.

ADMISSIBILITY (1.3; R1: at the POINT): (a) HTTP-429 attempts <= 2% of the step's HTTP attempts; (b) 0 invocations
exhausted on 429; (c) p95 of the invocation wall latency (reservation to return) <= min(1.5 x p95(S1), 10 s). p95 is
the NEAREST-RANK p95 (the ceil(0.95 n)-th smallest) [BUILDER'S CHOICE, printed; the registration names no method]. An
aborted step is inadmissible. RATE = the step's journaled invocations over its wall (the sum over the launches that
posted it of last return - first reservation), per minute.
C1: N* = the largest N whose step is admissible AND whose rate >= 1.3 x the previous admissible step's rate (literal);
if none, 1. S6 runs at N* if N* >= 2; if S6 is inadmissible, N* drops to the N of the ramp step immediately before N*'s
step. G = rate(ramp step of N*) / rate(S1); rate(S6) / rate(S1) is printed beside it.
[AMENDED PRE-DATA 2026-09-25 (A2 as REVISED by the orchestrator's ruling on O2, A3, A4, and RC5 (a) on O1), insertion
only; docs/judge_v2_program.md L20222-L20309 (d10e029), section "Registrar's record 2026-09-25 ... JV2-RATE-PROBE BUILT
... PRE-DATA AMENDMENTS A1-A7"; the two paragraphs above are read with this bracket:
  (c) (A2, O2 accepted): p95(step) <= 1.5 x p95(S1) (P95_REL_FACTOR, the registered relative factor KEPT); the absolute
      10 s cap is REMOVED (P95_CAP_S is no longer read); S1 is EXEMPT from (c); S6 is NOT exempt; a non-S1 step with
      p95(S1) unavailable is inadmissible. The falsifier keeps its own FALSIFIER_P95_FACTOR = 1.5 (registered).
  (a) (A3): a step is inadmissible on (a) iff its 429 share > 2% AND it carries more than ONE HTTP 429
      (ADMIT_429_MAX_COUNT = 1): "<= 2% or at most one 429". The falsifier keeps the literal share <= 2%
      (FALSIFIER_429_SHARE). The within-step abort (3 exhausted / 10 HTTP-429) and (b) are unchanged.
  S6 drop (RC5 (a), O1 accepted): on an inadmissible S6, N* drops to the LARGEST ramp step below N*'s step that
      QUALIFIED under C1's 1.3x rule, else S1 (N* = 1); "the previous ramp step" (the build's reading) is retired.
  A4: every HTTP 429 counts for admissibility; the outcome prints, beside N* and G, "N* is measured under rr's retry
      schedule (6 attempts, Retry-After ignored); every HTTP 429 counts for admissibility; it does not transfer as-is
      to a pool that honours Retry-After (A4)"; the provider-error and rate-header readouts are labelled "DESCRIPTIVE
      (A4): quota vs capacity is reported, not decided".]

OUTPUTS: <out>/jv2_rate_probe.db (the probe's own DB: meta pinned at the first launch, refused on mismatch; slot,
invocation, attempt, step_event, x1 tables), <db>.invocations.db (the journal), <db>.pilot_guard.json (PASS) or
<db>.pilot_guard_FAILED.<k>.json, <out>/JV2_RATE_PROBE_PILOT.txt (write-once), <out>/JV2_RATE_PROBE_outcome.txt
(write-once, only from a complete probe; otherwise <out>/JV2_RATE_PROBE_outcome_partial.txt). <out> defaults to the
MAIN checkout's experiment_results/jv2_rate_probe; the ledger directory must be the MAIN checkout's experiment_results.

DEVIATION FROM THE ORCHESTRATOR'S BRIEF (not from the registration): the brief said to reuse judge_v2/pool.py. The
registered instrument measures a FIXED in-flight N with rr's own retry loop running and visible (1.3 "rr is unchanged
and its internal retries run as registered"); pool.PostingPool neutralises rr's retries, paces by --max-rpm and halves
or raises its bound adaptively, so it would measure the pool's configuration, not the deployment. pool.py is therefore
REUSED for its LedgerLock, retry_after_seconds, endpoint_host / is_loopback and live_guard_reasons only, and is not
modified. Pre-data amendments are the registrar's.
"""
import argparse
import collections
import concurrent.futures as cf
import hashlib
import json
import math
import os
import random
import re
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.request
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import accepted_tests_ledger as atl  # noqa: E402
import pool_guard as pg  # noqa: E402
import rejudge_reference as rref  # noqa: E402
import split_side  # noqa: E402
from archv2_pilot import accounting as ACC  # noqa: E402
from archv2_pilot import pilot as PL  # noqa: E402
from judge_v2 import payload as P  # noqa: E402
from judge_v2 import pool as POOL  # noqa: E402
from judge_v2 import writer as W  # noqa: E402
from judge_v2._base import rj, rr  # noqa: E402

REAL_TIME_MODULE = time

# ── the registration's numbers ─────────────────────────────────────────────────────────────────────────────────────
TEST = "JV2-RATE-PROBE"
REG_COMMIT = "bf9d80b0ec59154434503243bbf024c109fca0fd"
SEED = "JV2-RATE-PROBE:" + REG_COMMIT
RAMP = (("S1", 1, 24), ("S2", 2, 36), ("S3", 4, 48), ("S4", 8, 64), ("S5", 12, 76))
S6_NAME, S6_INVOCATIONS = "S6", 150
PLAN_TOTAL = sum(n for _s, _N, n in RAMP) + S6_INVOCATIONS          # 398
MAX_N = max(N for _s, N, _n in RAMP)                                 # 12
PILOT_N = 12
GAP_S = 60.0
ADMIT_429_SHARE = 0.02
ABORT_EXHAUSTED = 3
ABORT_HTTP_429 = 10
P95_FACTOR, P95_CAP_S = 1.5, 10.0
# [AMENDED PRE-DATA 2026-09-25, A2 as revised (O2) / A3 (d10e029)]: admissibility and the falsifier read SEPARATE
# constants, so an amendment of one cannot leak into the other. P95_FACTOR / P95_CAP_S are kept for disclosure only.
P95_REL_FACTOR = 1.5          # (c): p95(step) <= 1.5 x p95(S1), S1 exempt, no absolute cap
FALSIFIER_P95_FACTOR = 1.5    # the falsifier, as registered
ADMIT_429_MAX_COUNT = 1       # (a): inadmissible iff share > 2% AND more than one HTTP 429
FALSIFIER_429_SHARE = 0.02    # the falsifier, as registered (literal share <= 2%)
QUALIFIER_A4 = ("N* is measured under rr's retry schedule (6 attempts, Retry-After ignored); every HTTP 429 counts for"
                " admissibility; it does not transfer as-is to a pool that honours Retry-After (A4)")
DESCRIPTIVE_A4 = "DESCRIPTIVE (A4): quota vs capacity is reported, not decided"
ADMISSIBILITY_OF_RECORD = ("(a) 429 share <= 2% or <= 1 HTTP 429 (A3); (b) 0 exhausted-429; (c) p95 <= 1.5 x p95(S1),"
                           " S1 exempt, no absolute cap (A2 as revised on O2); registered (a) and (c) superseded pre-data,"
                           " docs/judge_v2_program.md section of 2026-09-25 JV2-RATE-PROBE BUILT (d10e029)")
C1_GAIN, C2_G = 1.3, 1.5
P1_S3_RATE, FALSIFIER_S3_RATE, P2_SHARE = 35.0, 50.0, 0.10
P3_LAT = (3.0, 4.5)
V5_BYTES, V5_TOKENS = 0.10, 0.30
PILOT_UNPARSED_MAX = 0.05
DAY_CAP = 14000
JB_TEST = "JUDGEBENCH-REASONING-SIDE"
JB_MARGIN = "770 / 700 = 10%"
K46_TEST = "ARCH-V2-PILOT-K46"
K46_DIR_REL = os.path.join("experiment_results", "archv2", "pilot_k46")
K46_STORE = "pilot_k46_verdicts_run2.db"
K46_OUTCOME = "archv2_pilot_k46_outcome.txt"
POOL_MMLU, POOL_UNION = "p2dca21ab5f4ef3ae", "paeec37aa28063c75"
RATE_HEADER = re.compile(r"^(x-ratelimit-|retry-after)", re.I)
SECRET_HEADER = re.compile(r"^(api-key|authorization)$", re.I)
DB_NAME = "jv2_rate_probe.db"
OUTCOME_NAME = "JV2_RATE_PROBE_outcome.txt"
PARTIAL_NAME = "JV2_RATE_PROBE_outcome_partial.txt"
PILOT_NAME = "JV2_RATE_PROBE_PILOT.txt"

# ── SELFTEST-ONLY settings (every one is refused by the live guard when not at its default) ────────────────────────
TIME_SCALE = 1.0          # every wall wait of this module x TIME_SCALE
MUTANT = None             # jv2_rate_probe_selftest.py's mutant table
CLOCK = None              # a callable -> "YYYY-MM-DD" (the local date otherwise)
PROCESS_LIST = None       # a callable -> [[pid, name, cmdline], ...] (Get-CimInstance otherwise)
OPTIMIZE = None           # an int standing in for sys.flags.optimize
REAL_URLOPEN = None       # the wire's inner urlopen (a loopback rewrite in the selftest)
CORPUS_KEYS = None        # a callable -> {corpus name: set of stem keys} (the two corpora of record otherwise)
K46_SOURCE = None         # a dict standing in for the K46 store's readings
CEILING_OVERRIDE = None   # an int standing in for CEILINGS[TEST] (the cap test)
HOOK = None               # a callable(event, **kw) (the interrupt test)
SELFTEST_SETTINGS = ("TIME_SCALE", "MUTANT", "CLOCK", "PROCESS_LIST", "OPTIMIZE", "REAL_URLOPEN", "CORPUS_KEYS",
                     "K46_SOURCE", "CEILING_OVERRIDE", "HOOK")
_DEFAULTS = {"TIME_SCALE": 1.0}


def refuse(msg):
    raise SystemExit("[JV2-RATE-PROBE] " + msg)


def need(cond, msg):
    if not cond:
        refuse(msg)


def ceiling():
    return int(CEILING_OVERRIDE) if CEILING_OVERRIDE is not None else int(atl.CEILINGS[TEST])


def local_day():
    return CLOCK() if CLOCK is not None else time.strftime("%Y-%m-%d")


def sleep_scaled(s):
    time.sleep(max(0.0, float(s) * TIME_SCALE))


def settings_set():
    """The SELFTEST-ONLY settings of this module that are not at their default, as 'NAME=value'."""
    mod = sys.modules[__name__]
    bad = []
    for name in SELFTEST_SETTINGS:
        v = getattr(mod, name)
        if v != _DEFAULTS.get(name, None):
            bad.append("%s=%r" % (name, v if not callable(v) else "<callable>"))
    return bad


def live_reasons():
    """Why a LIVE post (a non-loopback endpoint) must be refused: empty = admitted."""
    bad = settings_set() + POOL.live_guard_reasons(1.0)
    if rr.time is not REAL_TIME_MODULE:
        bad.append("rejudge_reasoning.time is patched")
    return bad


def optimize_level():
    return int(OPTIMIZE) if OPTIMIZE is not None else int(sys.flags.optimize)


def refuse_optimize(out=print):
    lvl = optimize_level()
    out("[OPT] python optimisation level %d (a launch requires 0: rejudge_reasoning.load_env checks the .env with"
        " assert) -> %s" % (lvl, "OK" if lvl == 0 else "REFUSED"))
    if lvl != 0 and MUTANT != "optimize_ok":
        refuse("python -O: rejudge_reasoning.load_env relies on assert, which -O removes; launch under plain python")


# ── paths ──────────────────────────────────────────────────────────────────────────────────────────────────────────

def main_root():
    return PL.main_checkout() or os.path.dirname(os.path.dirname(HERE))


def default_out_dir():
    return os.path.join(main_root(), "experiment_results", "jv2_rate_probe")


def default_ledger_dir():
    return os.path.join(main_root(), "experiment_results")


def paths(out_dir):
    db = os.path.join(out_dir, DB_NAME)
    return {"db": db, "journal": db + ".invocations.db", "pilot_pass": db + ".pilot_guard.json",
            "outcome": os.path.join(out_dir, OUTCOME_NAME), "partial": os.path.join(out_dir, PARTIAL_NAME),
            "pilot_txt": os.path.join(out_dir, PILOT_NAME)}


def failed_pilot_path(db):
    k = 1
    while os.path.exists("%s.pilot_guard_FAILED.%d.json" % (db, k)):
        k += 1
    return "%s.pilot_guard_FAILED.%d.json" % (db, k)


def script_identity():
    """(git blob of the LF rendering, sha256-lf16, sha256-crlf16, the working tree's rendering): the kinds named."""
    p = os.path.abspath(__file__)
    with open(p, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    blob = hashlib.sha1(b"blob %d\x00" % len(lf) + lf).hexdigest()
    return (blob, hashlib.sha256(lf).hexdigest()[:16], hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()[:16],
            "CRLF" if b"\r\n" in raw else "LF")


# ── the transport ──────────────────────────────────────────────────────────────────────────────────────────────────

def transport(root=None, out=print):
    """load_transport + transport_preflight (IMPORTED from archv2_pilot.pilot), printed as booleans only."""
    P.configure_rr()
    cap = []
    PL.load_transport(root=root, out=cap.append)
    PL.transport_preflight(out=cap.append)          # SystemExit on a missing / empty / non-https endpoint or key
    ep, key = rr.AZURE_ENDPOINT, rr.AZURE_KEY
    host = POOL.endpoint_host(ep)
    line = ("TRANSPORT PREFLIGHT: OK (.env loaded through rejudge_reasoning.load_env: True; endpoint present: %s;"
            " https: %s; endpoint loopback: %s; key present: %s; provider %s; deployment %s; temperature omitted: %s;"
            " values never printed)" % (isinstance(ep, str) and bool(ep.strip()), str(ep).startswith("https://"),
                                        POOL.is_loopback(host), isinstance(key, str) and bool(key.strip()),
                                        rr.PROVIDER, rr.JUDGE_MODEL, rr.TEMPERATURE is None))
    out(line)
    return line


def live_guard(out=print):
    host = POOL.endpoint_host(rr.AZURE_ENDPOINT)
    live = not POOL.is_loopback(host)
    bad = live_reasons()
    out("[LIVE GUARD] endpoint loopback: %s; selftest settings / switches set: %s -> %s" % (
        not live, bad or "none", ("LIVE, REFUSED" if bad else "LIVE, ADMITTED") if live else "not live: admitted"))
    if live and bad:
        refuse("LIVE GUARD: a non-loopback endpoint under %s: refused before any journal row or post" % bad)
    return live


# ── the plan: SYNTHETIC-DEV items ──────────────────────────────────────────────────────────────────────────────────

LETTERS = "ABCDEFGHIJ"


def step_slots():
    """[(step, N or None for S6, [slot idx])] in ramp order; slots 1..398."""
    out, i = [], 1
    for s, N, n in RAMP:
        out.append((s, N, list(range(i, i + n))))
        i += n
    out.append((S6_NAME, None, list(range(i, i + S6_INVOCATIONS))))
    return out


def step_of_slot():
    return {i: s for s, _N, ids in step_slots() for i in ids}


def _rng(tag, i):
    h = hashlib.sha256(("%s|%s|%d" % (SEED, tag, i)).encode("utf-8")).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def _fmt(x, nd):
    return ("%%.%df" % nd) % x


def _options(rng, key, nd, unit, wrongs):
    """10 distinct options: the key, the registered wrong value first among the distractors, then perturbations."""
    vals = [key] + list(wrongs)
    k = 0
    for f in (0.5, 2.0, 0.8, 1.25, 0.9, 1.1, 1.5, 0.667, 3.0, 0.333, 1.75, 0.6, 1.4):
        vals.append(key * f)
        k += 1
    seen, uniq = set(), []
    for v in vals:
        s = _fmt(v, nd)
        if s not in seen and float(s) > 0:
            seen.add(s)
            uniq.append(s)
        if len(uniq) == 10:
            break
    need(len(uniq) == 10, "the option generator produced fewer than 10 distinct options")
    key_s, wrong_s = uniq[0], uniq[1]
    order = uniq[:]
    rng.shuffle(order)
    opts = ["%s %s" % (v, unit) for v in order]
    return opts, LETTERS[order.index(key_s)], LETTERS[order.index(wrong_s)], key_s, wrong_s


def make_item(i):
    """One SYNTHETIC-DEV item: a short stem, 10 options, the key / wrong letters, and the two worked solutions as
    (detail steps, final line); the final line alone is the minimal solution, the steps are added as padding."""
    rng = _rng("item", i)
    fam = rng.randrange(3)
    if fam == 0:
        v0, a, t = rng.randint(0, 25), round(rng.uniform(0.5, 6.0), 1), rng.randint(3, 40)
        key = v0 * t + 0.5 * a * t * t
        wrong = v0 * t + a * t * t
        stem = ("A cart starts at %d m/s and accelerates uniformly at %s m/s^2. How far does it travel in %d s? (item %d)"
                % (v0, _fmt(a, 1), t, i))
        good = ["Under constant acceleration the displacement is d = v0*t + (1/2)*a*t^2.",
                "Given v0 = %d m/s, a = %s m/s^2, t = %d s." % (v0, _fmt(a, 1), t),
                "Step 1: v0*t = %d * %d = %d m." % (v0, t, v0 * t),
                "Step 2: (1/2)*a*t^2 = 0.5 * %s * %d = %s m." % (_fmt(a, 1), t * t, _fmt(0.5 * a * t * t, 2)),
                "Step 3: d = %d + %s = %s m." % (v0 * t, _fmt(0.5 * a * t * t, 2), _fmt(key, 2))]
        bad = ["The distance is speed times time plus acceleration times time squared: d = v0*t + a*t^2.",
               "Given v0 = %d m/s, a = %s m/s^2, t = %d s." % (v0, _fmt(a, 1), t),
               "Step 1: v0*t = %d m." % (v0 * t),
               "Step 2: a*t^2 = %s * %d = %s m." % (_fmt(a, 1), t * t, _fmt(a * t * t, 2)),
               "Step 3: d = %d + %s = %s m." % (v0 * t, _fmt(a * t * t, 2), _fmt(wrong, 2))]
        what, nd, unit = "d", 2, "m"
    elif fam == 1:
        x = rng.randint(12, 400)
        key = x / 3.6
        wrong = x * 3.6
        stem = "A drone flies at %d km/h. What is its speed in m/s? (item %d)" % (x, i)
        good = ["Convert km/h to m/s: 1 km/h = 1000 m / 3600 s = 1/3.6 m/s.",
                "Step 1: %d km/h * (1000 m / 1 km) = %d m per hour." % (x, x * 1000),
                "Step 2: %d m / 3600 s = %s m/s." % (x * 1000, _fmt(key, 3))]
        bad = ["To go from km/h to m/s multiply by 3.6.",
               "Step 1: %d * 3.6 = %s." % (x, _fmt(wrong, 3)),
               "So the speed is %s m/s." % _fmt(wrong, 3)]
        what, nd, unit = "v", 3, "m/s"
    else:
        p, q, r, s = rng.randint(11, 99), rng.randint(11, 99), rng.randint(100, 999), rng.randint(2, 9)
        key = p * q + r / s
        wrong = (p * q + r) / s
        stem = "Evaluate %d * %d + %d / %d using the usual order of operations. (item %d)" % (p, q, r, s, i)
        good = ["Multiplication and division are done before addition.",
                "Step 1: %d * %d = %d." % (p, q, p * q),
                "Step 2: %d / %d = %s." % (r, s, _fmt(r / s, 4)),
                "Step 3: %d + %s = %s." % (p * q, _fmt(r / s, 4), _fmt(key, 4))]
        bad = ["Work from left to right.",
               "Step 1: %d * %d = %d." % (p, q, p * q),
               "Step 2: %d + %d = %d." % (p * q, r, p * q + r),
               "Step 3: %d / %d = %s." % (p * q + r, s, _fmt(wrong, 4))]
        what, nd, unit = "x", 4, ""
    opts, kl, wl, key_s, wrong_s = _options(rng, key, nd, unit, [wrong])
    good_final = "%s = %s, option (%s). The answer is (%s)." % (what, key_s, kl, kl)
    bad_final = "%s = %s, option (%s). The answer is (%s)." % (what, wrong_s, wl, wl)
    return {"idx": i, "family": fam, "stem": stem, "options": [o.strip() for o in opts], "key": kl, "wrong": wl,
            "good": good, "bad": bad, "good_final": good_final, "bad_final": bad_final,
            "correct_first": rng.random() < 0.5}


def _check_line(rng, k):
    a, b = rng.randint(101, 999), rng.randint(11, 99)
    return "Check %d: %d * %d = %d, and %d - %d = %d; the working above is unchanged." % (k, a, b, a * b, a, b, a - b)


FILL = "the arithmetic was re-checked line by line and agrees " * 40


def build_user(item, target, system):
    """The user turn whose posted body is EXACTLY `target` bytes: the minimal solutions (their final lines), then the
    detail steps, then computed check lines, then one filler line (refused when the minimal item is already longer)."""
    query = rref.with_reference(item["stem"], (item["key"], item["options"][LETTERS.index(item["key"])], None))
    rng = _rng("pad", item["idx"])

    def user_of(g, b):
        t1, t2 = "\n".join(g + [item["good_final"]]), "\n".join(b + [item["bad_final"]])
        return rj.build_user_prompt(query, t1, t2) if item["correct_first"] else rj.build_user_prompt(query, t2, t1)

    def size(u):
        return len(rr.payload_bytes(system, u))

    good, bad = [], []
    need(size(user_of(good, bad + ["Note: "])) <= target, "slot %d: the minimal item is %d bytes, above its target %d"
         % (item["idx"], size(user_of(good, bad + ["Note: "])), target))
    queue = []
    for j in range(max(len(item["good"]), len(item["bad"]))):
        if j < len(item["good"]):
            queue.append(("g", item["good"][j]))
        if j < len(item["bad"]):
            queue.append(("b", item["bad"][j]))
    k = 1
    while True:
        if queue:
            side, line = queue[0]
        else:
            side, line = ("g" if k % 2 else "b"), _check_line(rng, k)
        tg, tb = (good + [line], bad) if side == "g" else (good, bad + [line])
        if size(user_of(tg, tb + ["Note: "])) > target - 20:
            break
        good, bad = tg, tb
        if queue:
            queue.pop(0)
        else:
            k += 1
    base = size(user_of(good, bad + ["Note: "]))
    rem = target - base
    need(0 <= rem <= len(FILL), "slot %d: padding remainder %d out of range" % (item["idx"], rem))
    u = user_of(good, bad + ["Note: " + FILL[:rem]])
    need(size(u) == target, "slot %d: body %d bytes, not the target %d" % (item["idx"], size(u), target))
    return u, query


def k46_readings(out=print):
    """The K46 run2 store's lengths and shas (R8: only after the K46 outcome is written): body-length q10 / q50 / q90,
    median completion_tokens, the distinct system_template_sha / rubric_sha, and the launch manifest's system turn."""
    if K46_SOURCE is not None:
        return dict(K46_SOURCE)
    d = os.path.join(main_root(), K46_DIR_REL)
    need(os.path.isfile(os.path.join(d, K46_OUTCOME)), "R8: the K46 outcome file %s is absent: the K46 store is not"
         " opened before the K46 outcome is written" % os.path.join(d, K46_OUTCOME))
    store = os.path.join(d, K46_STORE)
    c = pg.open_ro(store)
    try:
        lens = sorted(len(zlib.decompress(b)) for (b,) in c.execute("SELECT body_zlib FROM verdict"))
        toks = sorted(r[0] for r in c.execute("SELECT completion_tokens FROM verdict WHERE completion_tokens IS NOT NULL"))
        tsha = sorted({r[0] for r in c.execute("SELECT system_template_sha FROM verdict")})
        rsha = sorted({r[0] for r in c.execute("SELECT rubric_sha FROM verdict")})
    finally:
        c.close()
    with open(os.path.join(d, K46_STORE + ".launch.json"), encoding="utf-8") as f:
        man = json.load(f)
    return {"n": len(lens), "q10": quantile_lower(lens, 0.10), "q50": quantile_lower(lens, 0.50),
            "q90": quantile_lower(lens, 0.90), "median_completion_tokens": median(toks),
            "system_template_sha": tsha, "rubric_sha": rsha, "system_turn_sha256": man.get("system_turn_sha256"),
            "store": store}


def quantile_lower(sorted_vals, q):
    """The order statistic at ceil(q n) (1-based): an observed value, no interpolation."""
    n = len(sorted_vals)
    need(n > 0, "a quantile of an empty list")
    return sorted_vals[max(1, int(math.ceil(q * n))) - 1]


def median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def p95(v):
    v = sorted(v)
    if not v:
        return None
    if MUTANT == "p95_is_median":
        return median(v)
    return v[max(1, int(math.ceil(0.95 * len(v)))) - 1]


def build_plan(k46, out=print):
    """The 398 slots: body bytes and shas, size classes, the system turn checked against K46's."""
    P.configure_rr()            # model grok-4-1-fast-non-reasoning, cap 8192, temperature OMITTED (the one builder)
    rub, _label = PL.load_generic_rubric()
    system = P.build_system(rub)
    man = P.recipe_manifest(rub)
    sys_sha = hashlib.sha256(system.encode("utf-8")).hexdigest()
    need(k46.get("system_turn_sha256") == sys_sha, "the system turn sha256 %s differs from the K46 launch manifest's %s"
         % (sys_sha, k46.get("system_turn_sha256")))
    need(k46.get("system_template_sha") == [man["system_template_sha"]], "K46's system_template_sha %s is not the"
         " recipe's %s" % (k46.get("system_template_sha"), man["system_template_sha"]))
    need(k46.get("rubric_sha") == [man["rubric_sha"]], "K46's rubric_sha %s is not the recipe's %s" % (
        k46.get("rubric_sha"), man["rubric_sha"]))
    empty = len(rr.payload_bytes(system, ""))
    targets = {"q10": int(k46["q10"]), "q50": int(k46["q50"]), "q90": int(k46["q90"])}
    slots = []
    for step, _N, ids in step_slots():
        for pos, i in enumerate(ids):
            cls = ("q10", "q50", "q90")[pos % 3]
            item = make_item(i)
            user, query = build_user(item, targets[cls], system)
            body = rr.payload_bytes(system, user)
            P._check_body(body, system, user)       # exactly model / max_tokens / messages; no temperature
            slots.append({"idx": i, "step": step, "cls": cls, "stem": item["stem"], "system": system, "user": user,
                          "body": body, "sha": hashlib.sha256(body).hexdigest(), "body_bytes": len(body),
                          "user_bytes": len(body) - empty, "key": item["key"], "query": query})
    need(len({s["sha"] for s in slots}) == len(slots), "two slots share a body: every user turn must be distinct")
    need(len(slots) == PLAN_TOTAL, "the plan has %d slots, not %d" % (len(slots), PLAN_TOTAL))
    digest = hashlib.sha256(json.dumps([[s["idx"], s["step"], s["cls"], s["sha"]] for s in slots] +
                                       [SEED, targets], sort_keys=True).encode("utf-8")).hexdigest()
    return {"slots": slots, "system": system, "system_sha": sys_sha, "empty_body_bytes": empty, "targets": targets,
            "plan_sha": digest, "manifest": man}


# ── the content gate ───────────────────────────────────────────────────────────────────────────────────────────────

def corpus_keys(out=print):
    """{corpus: set(stem_key)} over the MMLU-Pro universe (p2dca's mmlu_pro) and the union corpus (paeec's
    corpus_questions), read-only (pool_guard.open_ro)."""
    if CORPUS_KEYS is not None:
        return CORPUS_KEYS()
    res = {}
    for name, pool, sql in (("MMLU-Pro (mmlu_pro, %s)" % POOL_MMLU, POOL_MMLU, "SELECT question FROM mmlu_pro"),
                            ("union (corpus_questions, %s)" % POOL_UNION, POOL_UNION, "SELECT text FROM corpus_questions")):
        c = pg.open_ro(os.path.join(os.environ.get("TAXOARENA_DATA_ROOT") or main_root(),
                                    pg.registry_entry(pool)["db"]))
        try:
            rows = [r[0] for r in c.execute(sql)]
        finally:
            c.close()
        res[name] = {split_side.stem_key(t) for t in rows if t and str(t).strip()}
        out("[GATE] %s: %d rows, %d distinct stem keys" % (name, len(rows), len(res[name])))
    return res


def content_gate(plan, out=print):
    keys = corpus_keys(out)
    mine = {}
    for s in plan["slots"]:
        mine.setdefault(split_side.stem_key(s["stem"]), []).append(s["idx"])
    hits = {name: sorted(i for k, ids in mine.items() if k in ks for i in ids) for name, ks in keys.items()}
    n = sum(len(v) for v in hits.values())
    if MUTANT == "gate_off":
        n = 0
    out("[GATE] CONTENT GATE (split_side.stem_key, CK-CLOSE-v1): %d generated stems (%d distinct keys) against %s ->"
        " %d hit(s) %s" % (len(plan["slots"]), len(mine), ", ".join("%s %d keys" % (k, len(v)) for k, v in keys.items()),
                           n, "OK" if n == 0 else "REFUSED: " + json.dumps(hits)))
    return n


# ── exclusivity ────────────────────────────────────────────────────────────────────────────────────────────────────

POSTING_SCRIPT = re.compile(r"tools[\\/]+analysis[\\/]|judgebench|archv2_pilot|judge_v2", re.I)
ADMITTED_FLAGS = ("--selftest", "--dry-run")


def processes():
    if PROCESS_LIST is not None:
        return PROCESS_LIST()
    from data_v2.build import process_snapshot
    return process_snapshot()


def ancestors():
    if PROCESS_LIST is not None:
        return []
    from data_v2.build import ancestor_pids
    return ancestor_pids()


def x1_check(where, out=print, refuse_on=True):
    """X1: no foreign python process running a tools/analysis posting script (this process and its launch chain
    admitted; a --selftest / --dry-run printed and admitted)."""
    me = {os.getpid()} | set(ancestors())
    procs = processes()
    foreign, admitted, other = [], [], []
    for pid, name, cmd in procs:
        if pid in me:
            continue
        if "python" not in str(name).lower():
            other.append([pid, name])
            continue
        if POSTING_SCRIPT.search(cmd or ""):
            (admitted if any(f in (cmd or "") for f in ADMITTED_FLAGS) else foreign).append([pid, (cmd or "")[:160]])
        else:
            other.append([pid, name])
    ok = not foreign or MUTANT == "x1_off"
    out("[X1] %s: %d python/java process(es) besides this one; foreign posting scripts %s; admitted (selftest /"
        " dry-run) %s; others %s -> %s" % (where, len([p for p in procs if p[0] not in me]), foreign or "none",
                                           admitted or "none", [p[0] for p in other] or "none",
                                           "OK" if ok else "REFUSED"))
    if not ok and refuse_on:
        refuse("X1 at %s: foreign posting process(es) %s: the probe runs ALONE on the deployment" % (where, foreign))
    return {"where": where, "ok": bool(ok), "foreign": foreign, "admitted": admitted, "ts": time.time()}


def k46_idle(out=print):
    """X1's K46 clause: the K46 run2 journal shows 0 unresolved (read-only)."""
    if K46_SOURCE is not None:
        n = int(K46_SOURCE.get("unresolved", 0))
    else:
        jp = os.path.join(main_root(), K46_DIR_REL, K46_STORE + ".invocations.db")
        n = len(ACC.read_journal(jp)["unresolved"])
    out("[X1] K46 run2 journal unresolved invocations: %d -> %s" % (n, "OK" if n == 0 else "REFUSED"))
    need(n == 0, "X1: the K46 journal has %d unresolved invocations (its posting has not ended)" % n)


def x2_check(day, ledger_dir, where, out=print, refuse_on=True):
    rows = atl._rows(atl.day_ledger_path(ledger_dir, day))
    jb = sum(int(r["calls"]) for r in rows if r.get("test") == JB_TEST)
    has_jb = any(r.get("test") == JB_TEST for r in rows)
    k46 = sum(int(r["calls"]) for r in rows if r.get("test") == K46_TEST)
    ok = not has_jb or MUTANT == "x2_off"
    out("[X2] %s: day %s ledger: %s rows %s (%d calls); %s rows %d calls (printed, not refused) -> %s" % (
        where, day, JB_TEST, "PRESENT" if has_jb else "none", jb, K46_TEST, k46, "OK" if ok else "REFUSED"))
    if not ok and refuse_on:
        refuse("X2 at %s: day %s is a JudgeBench posting day (%d calls): the probe never shares its day" % (where, day, jb))
    return bool(ok)


# ── accounting ─────────────────────────────────────────────────────────────────────────────────────────────────────

def account(planned, ledger_dir, day, what, refuse_on=True, out=print, own_journal=0):
    """accepted_tests_ledger.guard (the test's ceiling, the 4,000-match rule, the combined statement) and the day cap
    (iii) as registered: day total + the ceiling <= 14,000."""
    need(TEST in atl.CEILINGS, "accepted_tests_ledger.CEILINGS carries no %s entry" % TEST)
    nums = atl.guard(TEST, planned, {}, ledger_dir, what, refuse=False)
    ceil = ceiling()
    own = max(int(nums["own"]), int(own_journal))
    total = ACC.day_total(ledger_dir, day)
    breaches = list(nums["breaches"])
    if own + planned > ceil:
        breaches.append("own %d + planned %d > the ceiling %d" % (own, planned, ceil))
    if total + ceil > DAY_CAP:
        breaches.append("(iii) day %s: %d + the ceiling %d = %d > %d" % (day, total, ceil, total + ceil, DAY_CAP))
    out("[ACCOUNT] %s (%s): own %d (ledgers %d, journal %d) + planned %d = %d of %d | (iii) as registered: day %s total"
        " %d + %d = %d of %d (with the planned only: %d) | ledger of record %s -> %s" % (
            TEST, what, own, nums["own"], own_journal, planned, own + planned, ceil, day, total, ceil, total + ceil,
            DAY_CAP, total + planned, os.path.abspath(atl.day_ledger_path(ledger_dir, day)),
            "OK" if not breaches else "REFUSED: " + "; ".join(breaches)))
    if breaches and refuse_on:
        refuse("[ACCOUNT] REFUSED, not trimmed (0 calls posted): " + "; ".join(breaches))
    return {"own": own, "planned": planned, "day_total": total, "breaches": breaches}


def check_ledger_dir(ledger_dir, record, out=print):
    full = os.path.realpath(os.path.abspath(ledger_dir))
    want = os.path.realpath(default_ledger_dir())
    out("[ACCOUNT] ledger directory %s (the main checkout's %s)" % (full, want))
    if record:
        need(full == want, "the ledger directory is not the MAIN checkout's experiment_results: refused (K9)")


# ── the probe DB ───────────────────────────────────────────────────────────────────────────────────────────────────

DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE launch (k INTEGER PRIMARY KEY, label TEXT NOT NULL, mode TEXT NOT NULL, day TEXT NOT NULL,
    started REAL NOT NULL, script_blob TEXT NOT NULL, gate_hits INTEGER NOT NULL);
CREATE TABLE invocation (idx INTEGER PRIMARY KEY, step TEXT NOT NULL, n_inflight INTEGER NOT NULL, seq INTEGER,
    launch_k INTEGER NOT NULL, label TEXT NOT NULL, t_reserve REAL, t_end REAL,
    outcome TEXT NOT NULL CHECK (outcome IN ('RETURNED', 'RAISED', 'NOT_SENT', 'ORPHAN')),
    final_status INTEGER, error TEXT, exhausted_429 INTEGER NOT NULL, http_attempts INTEGER NOT NULL,
    http_429 INTEGER NOT NULL, finish_reason TEXT, completion_tokens INTEGER, prompt_tokens INTEGER, vote TEXT,
    response_id TEXT, content_zlib BLOB, body_sha TEXT NOT NULL, body_bytes INTEGER NOT NULL, user_bytes INTEGER NOT NULL,
    size_class TEXT NOT NULL);
CREATE TABLE attempt (idx INTEGER NOT NULL, attempt_no INTEGER NOT NULL, t_send REAL NOT NULL, t_end REAL NOT NULL,
    status INTEGER, error TEXT, retry_after TEXT, retry_after_s REAL, rate_headers TEXT, header_names TEXT,
    provider_error TEXT, PRIMARY KEY (idx, attempt_no));
CREATE TABLE step_event (id INTEGER PRIMARY KEY, step TEXT NOT NULL, launch_k INTEGER NOT NULL, event TEXT NOT NULL,
    n_inflight INTEGER, ts REAL NOT NULL, note TEXT);
CREATE TABLE x1 (id INTEGER PRIMARY KEY, launch_k INTEGER NOT NULL, where_ TEXT NOT NULL, ok INTEGER NOT NULL,
    x2_ok INTEGER NOT NULL, detail TEXT NOT NULL, ts REAL NOT NULL);
CREATE TRIGGER invocation_no_update BEFORE UPDATE ON invocation BEGIN SELECT RAISE(ABORT, 'append-only'); END;
CREATE TRIGGER invocation_no_delete BEFORE DELETE ON invocation BEGIN SELECT RAISE(ABORT, 'append-only'); END;
CREATE TRIGGER attempt_no_update BEFORE UPDATE ON attempt BEGIN SELECT RAISE(ABORT, 'append-only'); END;
CREATE TRIGGER meta_no_update BEFORE UPDATE ON meta BEGIN SELECT RAISE(ABORT, 'append-only'); END;
"""


def meta_of(plan, k46, blob):
    return {"test": TEST, "registration_commit": REG_COMMIT, "seed": SEED, "plan_sha": plan["plan_sha"],
            "script_blob": blob, "judge": P.JUDGE_REQUESTED, "provider": P.PROVIDER, "cap": str(P.CAP),
            "temperature": P.TEMPERATURE_LABEL, "system_sha": plan["system_sha"], "targets": json.dumps(plan["targets"]),
            "empty_body_bytes": str(plan["empty_body_bytes"]), "k46_n": str(k46["n"]),
            "k46_median_completion_tokens": str(k46["median_completion_tokens"]), "ceiling": str(ceiling()),
            "max_inflight": str(MAX_N), "ramp": json.dumps(RAMP), "s6": str(S6_INVOCATIONS)}


def open_db(path, meta):
    """Create (meta pinned) or open (meta REQUIRED equal: a changed script, plan or recipe refuses)."""
    exists = os.path.exists(path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    con = sqlite3.connect(os.path.abspath(path))
    con.execute("PRAGMA journal_mode=DELETE")
    if not exists:
        con.executescript(DDL)
        con.executemany("INSERT INTO meta VALUES (?,?)", sorted((k, str(v)) for k, v in meta.items()))
        con.commit()
    got = dict(con.execute("SELECT key, value FROM meta").fetchall())
    diff = sorted(k for k in set(got) | set(meta) if got.get(k) != str(meta.get(k)))
    if diff and MUTANT != "meta_unchecked":
        con.close()
        refuse("the probe DB %s was created under other %s (pinned at the first launch): refused" % (path, diff))
    return con


def db_state(con):
    inv = {r[0]: r for r in con.execute("SELECT idx, step, outcome FROM invocation")}
    aborted = {r[0] for r in con.execute("SELECT DISTINCT step FROM step_event WHERE event='abort'")}
    s6n = con.execute("SELECT n_inflight FROM step_event WHERE step='S6' AND event='begin' ORDER BY id LIMIT 1").fetchone()
    return inv, aborted, (s6n[0] if s6n else None)


# ── the wire ───────────────────────────────────────────────────────────────────────────────────────────────────────

class WireRefused(RuntimeError):
    """A request refused BEFORE it leaves (not the slot's body; a live post under a selftest setting)."""


class ProbeAborted(RuntimeError):
    """The abort flag is set: no HTTP attempt leaves after it (rr does not catch a RuntimeError)."""


class Wire:
    def __init__(self, t0):
        self.tls = threading.local()
        self.lock = threading.Lock()
        self.records = []
        self.abort = threading.Event()
        self.orig = None
        self.real = None
        self.t0 = t0

    def install(self):
        if isinstance(getattr(urllib.request.urlopen, "__self__", None), Wire):
            refuse("a previous probe wire is still installed")
        self.orig = urllib.request.urlopen
        self.real = REAL_URLOPEN or self.orig
        urllib.request.urlopen = self.urlopen

    def uninstall(self):
        if self.orig is not None and urllib.request.urlopen == self.urlopen:
            urllib.request.urlopen = self.orig

    def begin(self, idx, sha):
        self.tls.idx, self.tls.sha, self.tls.n, self.tls.n429 = idx, sha, 0, 0

    def end(self):
        r = (getattr(self.tls, "n", 0), getattr(self.tls, "n429", 0))
        self.tls.sha = None
        return r

    def count_429(self, ids):
        with self.lock:
            return sum(1 for r in self.records if r["idx"] in ids and r["status"] == 429)

    def urlopen(self, req, *a, **k):
        if self.abort.is_set() and MUTANT != "abort_flag_ignored":
            raise ProbeAborted("[WIRE] the abort flag is set: no HTTP attempt leaves after it")
        host = POOL.endpoint_host(getattr(req, "full_url", None) or req)
        if not POOL.is_loopback(host):
            bad = live_reasons()
            if self.real is not self.orig:
                bad.append("the wire's inner urlopen is substituted")
            if bad:
                raise WireRefused("[WIRE] LIVE GUARD: a request to a non-loopback host under %s: refused BEFORE it"
                                  " left" % bad)
        exp = getattr(self.tls, "sha", None)
        data = getattr(req, "data", None)
        if MUTANT != "body_unchecked" and (exp is None or data is None or hashlib.sha256(bytes(data)).hexdigest() != exp):
            raise WireRefused("[WIRE] a request whose bytes are not the slot's body: refused BEFORE it left")
        self.tls.n += 1
        rec = {"idx": getattr(self.tls, "idx", None), "attempt_no": self.tls.n, "t_send": self.t0.now(),
               "status": None, "error": None, "retry_after": None, "retry_after_s": None, "rate_headers": None,
               "header_names": None, "provider_error": None}
        try:
            resp = self.real(req, *a, **k)
        except urllib.error.HTTPError as e:
            rec["status"] = e.code
            self._headers(rec, getattr(e, "headers", None))
            if e.code == 429 or e.code >= 500:
                rec["provider_error"] = self._error_body(e)
            if e.code == 429:
                self.tls.n429 += 1
            rec["t_end"] = self.t0.now()
            with self.lock:
                self.records.append(rec)
            raise
        except BaseException as e:
            rec["error"] = type(e).__name__
            rec["t_end"] = self.t0.now()
            with self.lock:
                self.records.append(rec)
            raise
        rec["status"] = getattr(resp, "status", None) or 200
        self._headers(rec, getattr(resp, "headers", None))
        rec["t_end"] = self.t0.now()
        with self.lock:
            self.records.append(rec)
        return resp

    @staticmethod
    def _headers(rec, headers):
        if headers is None:
            return
        try:
            items = list(headers.items())
        except Exception:  # noqa: BLE001
            return
        rate = {k: v for k, v in items if RATE_HEADER.match(k) and not SECRET_HEADER.match(k)}
        if MUTANT != "retry_after_ignored":
            ra = headers.get("Retry-After")
            rec["retry_after"] = ra
            rec["retry_after_s"] = POOL.retry_after_seconds(headers)
        else:
            rate.pop("Retry-After", None)
            rate.pop("retry-after", None)
        rec["rate_headers"] = json.dumps(rate, sort_keys=True) if rate else None
        rec["header_names"] = json.dumps(sorted({k.lower() for k, _v in items if not SECRET_HEADER.match(k)}))

    @staticmethod
    def _error_body(e):
        """A 429 / 5xx body's error code and the first 160 characters of its message (rr never reads these bodies;
        a 400 body is never touched, so rr's content-filter reading is unchanged)."""
        try:
            raw = e.read(4096)
            d = json.loads(raw.decode("utf-8", "replace"))
            err = d.get("error", d) if isinstance(d, dict) else {}
            return json.dumps({"code": str(err.get("code"))[:60], "message": str(err.get("message"))[:160]},
                              sort_keys=True)
        except Exception as x:  # noqa: BLE001
            return json.dumps({"unreadable": type(x).__name__})


class Clock:
    def __init__(self):
        self.w0, self.p0 = time.time(), time.perf_counter()

    def now(self):
        return self.w0 + (time.perf_counter() - self.p0)


# ── one launch ─────────────────────────────────────────────────────────────────────────────────────────────────────

Ticket = collections.namedtuple("Ticket", "idx seq sha body system user step N slot t_reserve")


def _send(wire, ticket, day):
    """WORKER thread: no sqlite; the local date re-checked; the body asserted; then rr.call_judge_full (rule 9)."""
    if local_day() != day and MUTANT != "rollover_off":
        return ("not_sent", POOL.NOT_SENT, 0, 0, wire.t0.now())
    if rr.payload_bytes(ticket.system, ticket.user) != ticket.body:
        return ("raised", WireRefused("the rebuilt body differs from the reserved body"), 0, 0, wire.t0.now())
    wire.begin(ticket.idx, ticket.sha)
    try:
        r = rr.call_judge_full(ticket.system, ticket.user)
        kind, value = "returned", r
    except Exception as e:  # noqa: BLE001
        kind, value = "raised", e
    finally:
        n, n429 = wire.end()
    return (kind, value, n, n429, wire.t0.now())


class Launch:
    def __init__(self, out_dir, ledger_dir, mode, record, expect_plan_sha=None, data_root=None, out=print):
        need(mode in ("pilot", "run"), "launch mode %r" % (mode,))
        self.out_dir, self.ledger_dir, self.mode, self.record = out_dir, ledger_dir, mode, record
        self.expect, self.data_root, self.out = expect_plan_sha, data_root, out
        self.p = paths(out_dir)
        self.posts = 0
        self.stop = None

    # the main thread's reservation (write-ahead), in this order: rollover, journal PENDING (the cap and the step's
    # bound fire here), posts += 1, submit
    def reserve(self, slot, step, N, label):
        if local_day() != self.day and MUTANT != "rollover_off":
            raise SystemExit(ACC.rollover_message(self.day, local_day()))
        bad = POOL.rr_changed(self.rr0)
        need(not bad, "rejudge_reasoning global(s) %s changed during the launch: refused" % bad)
        if MUTANT == "journal_after_post":
            self.posts += 1
            t = Ticket(slot["idx"], None, slot["sha"], slot["body"], slot["system"], slot["user"], step, N, slot,
                       self.clock.now())
            fut = self.ex.submit(_send, self.wire, t, self.day)
            seq = self.journal.pending(label, "JV2RP-%03d" % slot["idx"], 1, slot["sha"], self.day)
            return t._replace(seq=seq), fut
        seq = self.journal.pending(label, "JV2RP-%03d" % slot["idx"], 1, slot["sha"], self.day)
        self.posts += 1
        t = Ticket(slot["idx"], seq, slot["sha"], slot["body"], slot["system"], slot["user"], step, N, slot,
                   self.clock.now())
        return t, self.ex.submit(_send, self.wire, t, self.day)

    def resolve(self, t, res):
        kind, value, n, n429, t_end = res
        final, err, exh, fin, ctoks, ptoks, vote, rid, content = None, None, 0, None, None, None, None, None, None
        if kind == "returned":
            content, _prov, ctoks, _lat, fin, msg = value
            final = 200
            vote, _raw = W.classify(content, fin, msg)
            rid = (msg or {}).get("_response_id")
            self.journal.resolve(t.seq, "RETURNED", None, n, n429)
            outcome = "RETURNED"
        elif kind == "not_sent":
            self.journal.resolve(t.seq, "RAISED", POOL.NOT_SENT, 0, 0)
            outcome, err = "NOT_SENT", POOL.NOT_SENT
        else:
            final = getattr(value, "code", None)
            err = "%s: %s" % (type(value).__name__, str(value)[:200])
            exh = 1 if final == 429 else 0
            self.journal.resolve(t.seq, "RAISED", err, n, n429)
            outcome = "RAISED"
        with self.wire.lock:
            recs = [r for r in self.wire.records if r["idx"] == t.idx]
        self.con.execute("INSERT INTO invocation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            t.idx, t.step, t.N, t.seq, self.k, self.step_label, t.t_reserve, t_end, outcome, final, err, exh, n, n429,
            fin, ctoks, ptoks, vote, rid, zlib.compress(content.encode("utf-8")) if content else None, t.sha,
            t.slot["body_bytes"], t.slot["user_bytes"], t.slot["cls"]))
        self.con.executemany("INSERT INTO attempt VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
            (r["idx"], r["attempt_no"], r["t_send"], r["t_end"], r["status"], r["error"], r["retry_after"],
             r["retry_after_s"], r["rate_headers"], r["header_names"], r["provider_error"]) for r in recs])
        self.con.commit()
        if HOOK is not None:
            HOOK("resolved", launch=self, idx=t.idx, outcome=outcome)
        return outcome, exh

    def event(self, step, ev, N=None, note=None):
        self.con.execute("INSERT INTO step_event (step, launch_k, event, n_inflight, ts, note) VALUES (?,?,?,?,?,?)",
                         (step, self.k, ev, N, self.clock.now(), note))
        self.con.commit()

    def boundary(self, where):
        """X1 and X2 at a step boundary: recorded FIRST (V1 reads them), then refused on a breach."""
        x1 = x1_check(where, self.out, refuse_on=False)
        x2 = x2_check(self.day, self.ledger_dir, where, self.out, refuse_on=False)
        self.con.execute("INSERT INTO x1 (launch_k, where_, ok, x2_ok, detail, ts) VALUES (?,?,?,?,?,?)",
                         (self.k, where, int(x1["ok"]), int(x2), json.dumps(x1, sort_keys=True), time.time()))
        self.con.commit()
        need(x1["ok"], "X1 at %s: foreign posting process(es) %s: the probe runs ALONE on the deployment" % (
            where, x1["foreign"]))
        need(x2, "X2 at %s: day %s is a JudgeBench posting day: the probe never shares its day" % (where, self.day))

    def run_step(self, step, N, ids):
        """Post the step's pending slots with at most N in flight; the within-step abort; KeyboardInterrupt aborts."""
        inv, aborted, _ = db_state(self.con)
        todo = [i for i in ids if i not in inv]
        if not todo or step in aborted:
            return "complete"
        first = len(todo) == len(ids)
        if first and step != "S1":
            self.out("[STEP] idle gap %.0f s before %s (N = %d)" % (GAP_S, step, N))
            sleep_scaled(GAP_S)
        self.boundary("before %s" % step)
        self.step_label = "%s#%d %s N=%d" % (self.mode, self.k, step, N)
        width = N + 1 if MUTANT == "inflight_over" else N
        self.journal.begin_launch(self.step_label, width, True)
        self.event(step, "begin", N, "%d of %d slots pending" % (len(todo), len(ids)))
        self.out("[STEP] %s: N = %d, %d of %d invocation(s) pending (label %s)" % (step, N, len(todo), len(ids),
                                                                                 self.step_label))
        idset = set(ids)
        exhausted = sum(1 for i in ids if i in inv and inv[i][2] == "RAISED" and
                        self.con.execute("SELECT exhausted_429 FROM invocation WHERE idx=?", (i,)).fetchone()[0])
        self.ex = cf.ThreadPoolExecutor(max_workers=width, thread_name_prefix="jv2-rate-probe")
        inflight = {}
        status = "complete"
        try:
            while todo or inflight:
                while todo and len(inflight) < width and self.stop is None and status == "complete":
                    n429 = self.wire.count_429(idset)
                    if MUTANT != "abort_off" and (exhausted >= ABORT_EXHAUSTED or n429 >= ABORT_HTTP_429):
                        status = "aborted"
                        self.out("[STEP] %s ABORTED: %d exhausted-429 invocation(s), %d HTTP-429 attempt(s) (thresholds"
                                 " %d / %d): no further reservation; %d in flight are recorded" % (
                                     step, exhausted, n429, ABORT_EXHAUSTED, ABORT_HTTP_429, len(inflight)))
                        self.event(step, "abort", N, "exhausted %d, 429 attempts %d" % (exhausted, n429))
                        break
                    if self.mode == "pilot" and self.pilot_budget <= 0:
                        todo = []
                        break
                    i = todo[0]
                    try:
                        t, fut = self.reserve(self.by_idx[i], step, N, self.step_label)
                    except SystemExit as e:
                        self.stop = e
                        self.out("[STOP] at a reservation: %s -- %d in flight are recorded first" % (str(e)[:200],
                                                                                                    len(inflight)))
                        break
                    todo.pop(0)
                    if self.mode == "pilot":
                        self.pilot_budget -= 1
                    inflight[fut] = t
                if not inflight:
                    break
                done, _ = cf.wait(list(inflight), timeout=0.05, return_when=cf.FIRST_COMPLETED)
                for fut in sorted(done, key=lambda f: inflight[f].idx):
                    t = inflight.pop(fut)
                    outcome, exh = self.resolve(t, fut.result())
                    exhausted += exh
                    if outcome == "NOT_SENT" and self.stop is None:
                        self.stop = SystemExit(ACC.rollover_message(self.day, local_day()))
                        self.out("[STOP] DAY ROLLOVER at a send: no further reservation in this launch")
                if self.stop is not None and not inflight:
                    break
        except KeyboardInterrupt:
            self.wire.abort.set()
            self.out("[ABORT] interrupted: the abort flag is set; no HTTP attempt leaves after it; %d in-flight"
                     " invocation(s) are resolved first" % len(inflight))
            self.event(step, "interrupted", N, "%d in flight" % len(inflight))
            for fut in list(inflight):
                t = inflight.pop(fut)
                self.resolve(t, fut.result())
            raise
        finally:
            self.ex.shutdown(wait=True)
        if status == "complete" and self.stop is None and not [i for i in ids if i not in db_state(self.con)[0]]:
            self.event(step, "end", N)
        self.boundary("after %s" % step)
        return status

    def execute(self):
        """The guards in order (module docstring): -O, the TRANSPORT PREFLIGHT (before anything else is read or
        written), the live guard, the plan and the content gate, the day, the ledger directory, K46 / X1 / X2, the
        pilot / run preconditions, the probe DB and the journal, reconcile, the accounting guard; then the steps."""
        out = self.out
        self.clock = Clock()
        refuse_optimize(out)
        if MUTANT != "preflight_after_journal":
            transport(self.data_root, out)
        live_guard(out)
        self.k46 = k46_readings(out)
        self.plan = build_plan(self.k46, out)
        self.by_idx = {s["idx"]: s for s in self.plan["slots"]}
        self.gate_hits = content_gate(self.plan, out)
        self.day = local_day()
        out("[DAY] the posting day is fixed at the launch: %s (every reservation and send re-checks it)" % self.day)
        check_ledger_dir(self.ledger_dir, self.record, out)
        k46_idle(out)
        x1_check("the launch", out)
        x2_check(self.day, self.ledger_dir, "the launch", out)
        need(self.expect is not None or not self.record, "a launch names the dry-run's plan sha (--expect-plan-sha)")
        if self.expect is not None:
            need(self.expect == self.plan["plan_sha"], "the plan sha %s differs from the dry-run's %s" % (
                self.plan["plan_sha"], self.expect))
        need(self.gate_hits == 0, "the content gate found %d hit(s): refused" % self.gate_hits)
        blob = script_identity()[0]
        if MUTANT == "preflight_after_journal":
            os.makedirs(self.out_dir, exist_ok=True)
            ACC.Journal.open(self.p["journal"], cap=ceiling(), create=not os.path.exists(self.p["journal"]),
                             max_inflight=MAX_N if not os.path.exists(self.p["journal"]) else None).close()
            transport(self.data_root, out)
        if self.mode == "pilot":
            need(not os.path.exists(self.p["pilot_pass"]), "the pilot 12 already PASSED (%s): the next launch is --run"
                 % self.p["pilot_pass"])
            need(not [f for f in os.listdir(self.out_dir) if ".pilot_guard_FAILED." in f]
                 if os.path.isdir(self.out_dir) else True,
                 "a pilot guard FAILED file exists: V4 failed; the probe is VOID (re-registered, not re-run)")
        else:
            need(os.path.exists(self.p["pilot_pass"]) or MUTANT == "pilot_guard_off",
                 "the run is refused: no PASSED pilot guard file %s" % self.p["pilot_pass"])
        # the accounting guard, read-only, BEFORE any probe DB or journal exists (re-run exactly after reconcile)
        js0 = ACC.read_journal(self.p["journal"])
        rem0 = PLAN_TOTAL - js0["invocations"]
        account(min(PILOT_N, rem0) if self.mode == "pilot" else rem0, self.ledger_dir, self.day,
                self.mode + " (before any write)", True, out, own_journal=js0["invocations"])
        creating_j = not os.path.exists(self.p["journal"])
        need(os.path.exists(self.p["db"]) or creating_j, "a journal without its probe DB: refused")
        need(not os.path.exists(self.p["db"]) or not creating_j, "a probe DB without its journal: refused")
        self.con = open_db(self.p["db"], meta_of(self.plan, self.k46, blob))
        cap = ACC.AUTHOR_HARD_CAP if MUTANT == "cap_off" else ceiling()
        self.journal = ACC.Journal.open(self.p["journal"], cap=cap, create=creating_j,
                                        max_inflight=MAX_N if creating_j else None)
        need(self.journal.max_inflight == MAX_N, "the journal's max_inflight %d is not %d" % (
            self.journal.max_inflight, MAX_N))
        self.k = (self.con.execute("SELECT COALESCE(MAX(k), 0) FROM launch").fetchone()[0] or 0) + 1
        label = "%s#%d" % (self.mode, self.k)
        self.con.execute("INSERT INTO launch VALUES (?,?,?,?,?,?,?)", (self.k, label, self.mode, self.day, time.time(),
                                                                      blob, int(self.gate_hits)))
        self.con.commit()
        self.rr0 = POOL.rr_snapshot()
        self.wire = Wire(self.clock)
        self.step_label = label
        steps_run = []
        try:
            orphans, caught = ACC.reconcile(TEST, self.journal, self.ledger_dir, out)
            self._consumed_rows()
            js = self.journal.state()
            out("[JOURNAL] %s: invocations %d (orphans resolved now %d, ledger caught up now %d); by outcome %s" % (
                self.p["journal"], js["invocations"], orphans, caught, json.dumps(js["by_outcome"], sort_keys=True)))
            inv, _ab, _ = db_state(self.con)
            planned = PLAN_TOTAL - len(inv) if self.mode == "run" else min(PILOT_N, PLAN_TOTAL - len(inv))
            account(planned, self.ledger_dir, self.day, self.mode, True, out, own_journal=js["invocations"])
            self.wire.install()
            self.pilot_budget = PILOT_N - len([i for i in inv if i <= PILOT_N]) if self.mode == "pilot" else None
            while self.stop is None:
                nxt = next_action(self.con)
                if nxt is None or (self.mode == "pilot" and self.pilot_budget <= 0):
                    break
                step, N, ids = nxt
                if self.mode == "pilot":
                    need(step == "S1", "the pilot posts S1 only")
                    ids = [i for i in ids if i <= PILOT_N]
                st = self.run_step(step, N, ids)
                steps_run.append((step, st))
                if self.mode == "pilot":
                    break
        finally:
            self.wire.uninstall()
            if self.posts and MUTANT != "ledger_skip":
                ACC.append(TEST, label, self.posts, self.ledger_dir, day=self.day)
            jn = self.journal.state()
            self.journal.close()
            self.con.close()
        led = ACC.check_equal(TEST, jn["invocations"], self.ledger_dir, "at the end of the launch")
        need(not jn["unresolved"], "the journal has unresolved invocations %s at the end of the launch" % jn["unresolved"])
        out("[JOURNAL] launch %s: posted %d; journal invocations %d = ledger %d; steps %s" % (
            label, self.posts, jn["invocations"], led, steps_run))
        res = {"posted": self.posts, "journal": jn["invocations"], "ledger": led, "steps": steps_run,
               "stop": str(self.stop) if self.stop else None}
        if self.mode == "pilot" and self.stop is None:
            res["pilot"] = pilot_guard_write(self.p, out)
        if self.stop is not None:
            out("[STOP] %s" % str(self.stop)[:300])
        return res

    def _consumed_rows(self):
        """Every journaled invocation whose slot has no probe row (an ORPHAN of a crash, or a crash between the
        journal's resolution and the probe row) is recorded as consumed: counted, NEVER re-posted (every body stays
        distinct and the plan stays within 398)."""
        inv, _a, _ = db_state(self.con)
        rows = self.journal.conn.execute("SELECT i.seq, i.match_id, i.launch FROM invocation i ORDER BY i.seq").fetchall()
        sos = step_of_slot()
        for seq, mid, lab in rows:
            idx = int(mid.split("-")[1])
            if idx in inv:
                continue
            s = self.by_idx[idx]
            N = int(re.search(r"N=(\d+)", lab).group(1)) if re.search(r"N=(\d+)", lab) else 0
            self.con.execute("INSERT INTO invocation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                idx, sos[idx], N, seq, self.k, lab, None, None, "ORPHAN", None, "posted with no reply recorded", 0, 0,
                0, None, None, None, None, None, None, s["sha"], s["body_bytes"], s["user_bytes"], s["cls"]))
            self.out("[ACCOUNT] slot %d (journal seq %d) was journaled with no probe row (a crash): recorded as ORPHAN,"
                     " counted, not re-posted" % (idx, seq))
        self.con.commit()


# ── the decision rules (pure; shared by the launch and --analyze) ─────────────────────────────────────────────────

def load_rows(con):
    inv = [dict(zip([d[0] for d in con.execute("SELECT * FROM invocation LIMIT 0").description], r))
           for r in con.execute("SELECT * FROM invocation ORDER BY idx")]
    att = [dict(zip([d[0] for d in con.execute("SELECT * FROM attempt LIMIT 0").description], r))
           for r in con.execute("SELECT * FROM attempt ORDER BY idx, attempt_no")]
    ev = con.execute("SELECT step, event, n_inflight, launch_k FROM step_event ORDER BY id").fetchall()
    return inv, att, ev


def step_stats(step, inv, att, ev):
    rows = [r for r in inv if r["step"] == step]
    ids = {r["idx"] for r in rows}
    a = [x for x in att if x["idx"] in ids]
    http = len(a)
    n429 = sum(1 for x in a if x["status"] == 429)
    segs = collections.defaultdict(list)
    for r in rows:
        if r["t_reserve"] is not None and r["t_end"] is not None:
            segs[r["launch_k"]].append(r)
    wall = sum(max(r["t_end"] for r in v) - min(r["t_reserve"] for r in v) for v in segs.values())
    lats = [r["t_end"] - r["t_reserve"] for r in rows if r["outcome"] in ("RETURNED", "RAISED")
            and r["t_reserve"] is not None]
    returned = [r for r in rows if r["outcome"] == "RETURNED"]
    toks = [r["completion_tokens"] for r in returned if r["completion_tokens"] is not None]
    Ns = sorted({r["n_inflight"] for r in rows if r["outcome"] != "ORPHAN"})
    return {"step": step, "N": Ns[0] if len(Ns) == 1 else (Ns or [None])[0], "Ns": Ns, "n": len(rows),
            "http": http, "n429": n429, "share": (n429 / http) if http else None,
            "cp95": cp_upper(n429, http) if http else None,
            "exhausted": sum(1 for r in rows if r["exhausted_429"]), "wall_s": wall,
            "rate": (len(rows) / wall * 60.0) if wall > 0 else None,
            "lat_median": median(lats), "lat_p95": p95(lats), "lat_max": max(lats) if lats else None,
            "tokens_median": median(toks), "user_bytes_median": median([r["user_bytes"] for r in rows]),
            "unparsed": sum(1 for r in returned if r["vote"] == "INVALID"), "returned": len(returned),
            "aborted": any(s == step and e == "abort" for s, e, _n, _k in ev),
            "orphans": sum(1 for r in rows if r["outcome"] == "ORPHAN"),
            "not_sent": sum(1 for r in rows if r["outcome"] == "NOT_SENT"),
            "lengths": sum(1 for r in returned if r["finish_reason"] == "length"),
            "content_filter": sum(1 for r in returned if r["finish_reason"] == "content_filter")}


def c_exempt(st):
    """A2 (as revised): S1 is exempt from (c); S6 is NOT."""
    if MUTANT == "s1_not_exempt" and st.get("step") == "S1":
        return False
    return st.get("step") == "S1" or (MUTANT == "s6_exempt" and st.get("step") == S6_NAME)


def admissible(st, p95_s1):
    """1.3 (a)-(c) at the point (R1), AS AMENDED PRE-DATA (A2 as revised, A3; module docstring bracket); an aborted step
    is inadmissible. -> (bool, reasons)."""
    why = []
    if st["aborted"]:
        why.append("aborted")
    max_n = 2 if MUTANT == "a_count_bound_2" else ADMIT_429_MAX_COUNT
    if st["share"] is None:
        why.append("no HTTP attempt")
    else:
        over_share, over_count = st["share"] > ADMIT_429_SHARE, st["n429"] > max_n
        if MUTANT == "a_or_dropped":
            bad_a = over_share
        elif MUTANT == "a_or_as_and":
            bad_a = over_share or over_count
        else:
            bad_a = over_share and over_count
        if bad_a:
            why.append("(a) 429 share %.4f > 0.02 and 429 count %d > %d (A3)" % (st["share"], st["n429"], max_n))
    if st["exhausted"] != 0:
        why.append("(b) %d exhausted-429 invocation(s)" % st["exhausted"])
    if not c_exempt(st):
        f = 2.0 if MUTANT == "p95_factor_2" else P95_REL_FACTOR
        bar = f * p95_s1 if p95_s1 is not None else None
        if MUTANT == "p95_cap_restored" and bar is not None:
            bar = min(bar, P95_CAP_S)
        if st["lat_p95"] is None or bar is None or st["lat_p95"] > bar:
            why.append("(c) p95 %s > %.1f x p95(S1) = %s (A2)" % (_s(st["lat_p95"]), f, _s(bar)))
    return (not why), why


def _s(x, nd=3):
    return "n/a" if x is None else ("%.*f" % (nd, x))


def ramp_complete(step, inv_ids, aborted):
    s = dict((a, (N, ids)) for a, N, ids in step_slots())[step]
    return step in aborted or all(i in inv_ids for i in s[1])


def decide(stats):
    """stats: {step: step_stats} of the COMPLETE steps. -> the ramp's decisions (C1, S6, the drop, G, knee)."""
    s1 = stats.get("S1")
    p95_s1 = s1["lat_p95"] if s1 else None
    ramp, stopped_at = [], None
    for step, N, _n in RAMP:
        if step not in stats:
            break
        ok, why = admissible(stats[step], p95_s1)
        ramp.append((step, N, ok, why))
        if not ok and MUTANT != "stop_rule_off":
            stopped_at = step
            break
    nstar, prev_rate, nstar_step = 1, None, "S1"
    qualified = []                      # the ramp steps (N >= 2) that qualified under C1's 1.3x rule, in order
    for step, N, ok, _why in ramp:
        if not ok:
            break
        r = stats[step]["rate"]
        if N >= 2 and prev_rate is not None and r is not None and (r >= C1_GAIN * prev_rate or MUTANT == "c1_no_gain"):
            nstar, nstar_step = N, step
            qualified.append(step)
        prev_rate = r
    ramp_done = stopped_at is not None or len(ramp) == len(RAMP)
    s6 = None
    nstar_final, final_step = nstar, nstar_step
    if ramp_done and nstar >= 2 and S6_NAME in stats:
        ok6, why6 = admissible(stats[S6_NAME], p95_s1)
        s6 = (ok6, why6)
        if not ok6 and MUTANT != "s6_no_drop":
            order = [r[0] for r in ramp]
            j = order.index(nstar_step)
            if MUTANT == "s6_drop_previous":        # the build's retired reading (the previous ramp step)
                final_step = order[j - 1]
            else:                                   # RC5 (a): the largest step below N*'s that qualified under C1
                below = [x for x in qualified if order.index(x) < j]
                final_step = below[-1] if below else "S1"
            nstar_final = dict((a, N) for a, N, _n in RAMP)[final_step]
    rate1 = s1["rate"] if s1 else None
    G = (stats[final_step]["rate"] / rate1) if (rate1 and final_step in stats and stats[final_step]["rate"]) else None
    G6 = (stats[S6_NAME]["rate"] / rate1) if (rate1 and S6_NAME in stats and stats[S6_NAME]["rate"]) else None
    knee = None
    for (a, Na, oka, _w), (b, Nb, okb, _w2) in zip(ramp, ramp[1:]):
        if not (oka and okb):
            break
        ra, rb = stats[a]["rate"], stats[b]["rate"]
        if ra and rb is not None and rb < C1_GAIN * ra:
            knee = (a, b, rb / ra, "a doubling" if Nb == 2 * Na else "x%.1f in N, not a doubling" % (Nb / Na))
            break
    need_s6 = ramp_done and nstar >= 2 and S6_NAME not in stats
    return {"ramp": ramp, "stopped_at": stopped_at, "ramp_done": ramp_done, "nstar": nstar, "nstar_step": nstar_step,
            "s6": s6, "nstar_final": nstar_final, "final_step": final_step, "G": G, "G6": G6, "knee": knee,
            "need_s6": need_s6, "p95_s1": p95_s1, "complete": ramp_done and not need_s6}


def next_action(con):
    """-> (step, N, ids) to post next, or None when the probe is complete by its own rule."""
    inv, aborted, s6n = db_state(con)
    ids_of = dict((a, (N, ids)) for a, N, ids in step_slots())
    rows, att, ev = load_rows(con)
    stats = {}
    for step, N, _n in RAMP:
        if not ramp_complete(step, inv, aborted):
            return step, N, ids_of[step][1]
        stats[step] = step_stats(step, rows, att, ev)
        ok, _why = admissible(stats[step], stats["S1"]["lat_p95"])
        if not ok and MUTANT != "stop_rule_off":
            break
    d = decide(stats)
    if d["nstar"] >= 2:
        if S6_NAME in {r["step"] for r in rows} and ramp_complete(S6_NAME, inv, aborted):
            return None
        N6 = s6n if s6n is not None else d["nstar"]
        need(N6 == d["nstar"], "S6 began at N = %s but the ramp now reads N* = %d" % (s6n, d["nstar"]))
        return S6_NAME, N6, ids_of[S6_NAME][1]
    return None


# ── the pilot guard ────────────────────────────────────────────────────────────────────────────────────────────────

def pilot_guard(con):
    rows = [r for r in load_rows(con)[0] if r["idx"] <= PILOT_N]
    returned = [r for r in rows if r["outcome"] == "RETURNED"]
    unparsed = sum(1 for r in returned if r["vote"] == "INVALID")
    length = sum(1 for r in returned if r["finish_reason"] == "length")
    cfilter = sum(1 for r in returned if r["finish_reason"] == "content_filter" or r["vote"] == "CONTENT_FILTER")
    raised = sum(1 for r in rows if r["outcome"] in ("RAISED", "ORPHAN"))
    share = unparsed / PILOT_N
    ok = (len(returned) == PILOT_N and share <= PILOT_UNPARSED_MAX and length == 0 and cfilter == 0 and raised == 0)
    if MUTANT == "pilot_guard_off":
        ok = True
    return {"pass": bool(ok), "pilot": PILOT_N, "resolved": len(rows), "returned": len(returned),
            "unparsed": unparsed, "unparsed_share": share, "finish_length": length, "content_filter": cfilter,
            "raised_or_orphan": raised, "rule": "PASS iff 12 RETURNED, unparsed <= 5%, no length / content_filter,"
                                                " no raised invocation"}


def pilot_guard_write(p, out=print):
    con = sqlite3.connect(os.path.abspath(p["db"]))
    try:
        rows = [r for r in load_rows(con)[0] if r["idx"] <= PILOT_N]
        if len(rows) < PILOT_N:
            out("[PILOT-GUARD] %d of %d pilot invocations resolved: no verdict yet (relaunch --pilot)" % (len(rows),
                                                                                                        PILOT_N))
            return None
        g = pilot_guard(con)
        inv, att, ev = load_rows(con)
    finally:
        con.close()
    line = ("[PILOT-GUARD] %s: %d of %d RETURNED, unparsed %d (%.1f%%, bound 5%%), finish length %d, content_filter %d,"
            " raised or orphan %d" % ("PASS" if g["pass"] else "FAIL (V4: the probe is VOID; the run is refused)",
                                      g["returned"], PILOT_N, g["unparsed"], 100 * g["unparsed_share"],
                                      g["finish_length"], g["content_filter"], g["raised_or_orphan"]))
    out(line)
    path = p["pilot_pass"] if g["pass"] else failed_pilot_path(p["db"])
    with open(path, "x", encoding="utf-8") as f:
        json.dump(g, f, indent=1, sort_keys=True)
    st = step_stats("S1", [r for r in inv if r["idx"] <= PILOT_N], att, ev)
    txt = [line, "[PILOT] S1's first 12 (N = 1): HTTP attempts %d, 429 attempts %d, exhausted %d, median latency %s s,"
                 " p95 %s s, calls/min %s, median completion tokens %s, median user bytes %s" % (
                     st["http"], st["n429"], st["exhausted"], _s(st["lat_median"]), _s(st["lat_p95"]),
                     _s(st["rate"], 2), st["tokens_median"], st["user_bytes_median"]),
           "[PILOT] this file is the pilot's (_PILOT); it is not the outcome of record."]
    with open(p["pilot_txt"], "x", encoding="utf-8") as f:
        f.write("\n".join(txt) + "\n")
    need(g["pass"], "the pilot-12 guard FAILED: the run is refused (%s)" % json.dumps(g, sort_keys=True))
    return g


# ── the readouts and the scoring (pure: the selftest executes every branch) ──────────────────────────────────────

def cp_upper(k, n, alpha=0.05):
    """The exact one-sided Clopper-Pearson upper bound: p with P(X <= k | n, p) = alpha (1 - alpha^(1/n) at k = 0)."""
    if n <= 0:
        return None
    if k >= n:
        return 1.0

    def cdf(p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if cdf(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


def score(stats, d, v, k46):
    """-> (lines, verdicts). v: the C0 inputs {V1, V2, V3, V4, V5_bytes, V5_tokens, ...}."""
    L, V = [], {}
    c0 = bool(v["V1"]) and bool(v["V2"]) and bool(v["V3"]) and bool(v["V4"])
    V["C0"] = "HELD" if c0 else "FAILED"
    if c0:
        L.append("C0 VALIDITY: HELD (V1 exclusivity %s; V2 content gate %s; V3 ledger == journal and <= 400 %s; V4 pilot"
                 " guard %s)" % tuple("held" for _ in range(4)))
    else:
        failed = [k for k in ("V1", "V2", "V3", "V4") if not v[k]]
        L.append("C0 VALIDITY: FAILED (%s): the probe is VOID; it is re-registered, not re-read" % ", ".join(failed))
    v5 = bool(v["V5_bytes"]) and bool(v["V5_tokens"])
    V["V5"] = "HELD" if v5 else "FAILED"
    if v5:
        L.append("V5 REALISM: HELD (median user bytes and median completion tokens inside their bands)")
    else:
        L.append("V5 REALISM: FAILED: the numbers below are DESCRIPTIVE, with the size caveat beside N* (it does not"
                 " void)")
    L.append("C1 DECISION (readout of record): N* = %d (ramp N* %d at %s%s)" % (
        d["nstar_final"], d["nstar"], d["nstar_step"],
        "" if d["s6"] is None else ("; S6 admissible" if d["s6"][0] else "; S6 INADMISSIBLE (%s): N* dropped to the"
                                    " largest lower N that qualified under C1, else 1 (RC5 (a)): N = %d" % (
                                        "; ".join(d["s6"][1]), d["nstar_final"]))))
    if not v5:
        L.append("  [SIZE CAVEAT] V5 failed: N* is read with the realism caveat")
    Gs = "n/a" if d["G"] is None else "%.3f" % d["G"]
    if d["G"] is not None and d["G"] >= C2_G:
        V["C2"] = "build"
        L.append("C2 VALUE (readout of record): G = %s >= 1.5 -> \"build JV2-PARALLEL-POSTING\"" % Gs)
    else:
        V["C2"] = "deferred"
        L.append("C2 VALUE (readout of record): G = %s < 1.5 -> \"the parallel writer buys < 1.5x on this deployment"
                 " today; build DEFERRED unless the author decides otherwise\"" % Gs)
    L.append("  [C2 SUPERSEDED FOR THE BUILD DECISION ONLY by the author's override (plan Amendment 24): the build is"
             " not deferred whatever G reads; G informs gate (3) and the quota question]; rate(S6) / rate(S1) = %s" % (
                 "n/a" if d["G6"] is None else "%.3f" % d["G6"]))
    s3 = stats.get("S3")
    if s3 is not None and s3["n"]:
        L.append("C3 JUDGEBENCH NOTE (informational): S3 HTTP overhead (attempts - invocations) / invocations = (%d -"
                 " %d) / %d = %.3f, beside JudgeBench's HTTP margin %s" % (s3["http"], s3["n"], s3["n"],
                                                                         (s3["http"] - s3["n"]) / s3["n"], JB_MARGIN))
    else:
        L.append("C3 JUDGEBENCH NOTE: S3 NOT POSTED (the ramp stopped earlier): NOT OBSERVED")
    # P1
    c1i = d["nstar_final"] in (1, 2)
    if s3 is not None and s3["rate"] is not None:
        c1ii = s3["rate"] < P1_S3_RATE
        p1 = c1i and c1ii
        V["P1"] = "HELD" if p1 else "FAILED"
        L.append("P1: %s ((i) N* = %d in {1, 2}: %s; (ii) rate(S3) = %.2f calls/min < 35: %s)" % (
            V["P1"], d["nstar_final"], c1i, s3["rate"], c1ii))
    else:
        V["P1"] = "HELD" if c1i else "FAILED"
        L.append("P1: %s on (i) only ((i) N* = %d in {1, 2}: %s; (ii) NOT OBSERVED: S3 not posted)" % (
            V["P1"], d["nstar_final"], c1i))
    # P2
    first_bad = None
    for step, _N, ok, _why in d["ramp"]:
        if not ok:
            first_bad = step
            break
    if first_bad is None and d["s6"] is not None and not d["s6"][0]:
        first_bad = S6_NAME
    if first_bad is None:
        V["P2"] = "UNDETERMINED"
        L.append("P2: UNDETERMINED (no inadmissible step)")
    else:
        sh = stats[first_bad]["share"]
        V["P2"] = "HELD" if (sh is not None and sh >= P2_SHARE) else "FAILED"
        L.append("P2: %s (first inadmissible step %s: HTTP-429 share %s, bar >= 0.10)" % (V["P2"], first_bad, _s(sh, 4)))
    # P3
    s1 = stats["S1"]
    p3 = (s1["lat_median"] is not None and P3_LAT[0] <= s1["lat_median"] <= P3_LAT[1] and s1["exhausted"] == 0)
    V["P3"] = "HELD" if p3 else "FAILED"
    L.append("P3: %s (S1 median invocation latency %s s in [3.0, 4.5]; S1 exhausted-429 %d, bar 0)" % (
        V["P3"], _s(s1["lat_median"]), s1["exhausted"]))
    V["P4"] = "READOUT"
    L.append("P4 (readout, not scored): rate headers returned: %s%s" % (
        "yes" if v.get("rate_header_names") else "no",
        (" (%s)" % ", ".join(v["rate_header_names"])) if v.get("rate_header_names") else ""))
    V["P5"] = V["V5"]
    L.append("P5: %s (= V5: median user bytes %s vs K46 q50 %s +-10%%; median completion tokens %s vs K46 %s +-30%%)" % (
        V["P5"], v.get("user_bytes_median"), v.get("k46_user_q50"), v.get("tokens_median"),
        k46.get("median_completion_tokens")))
    # the falsifier
    fired = False
    if s3 is not None and s3["rate"] is not None and s3["share"] is not None and s1["lat_p95"] is not None:
        share_ok = (admissible(s3, s1["lat_p95"])[0] if MUTANT == "falsifier_reads_or"
                    else s3["share"] <= FALSIFIER_429_SHARE)
        fired = (s3["rate"] >= FALSIFIER_S3_RATE and share_ok and s3["exhausted"] == 0 and
                 s3["lat_p95"] is not None and s3["lat_p95"] <= FALSIFIER_P95_FACTOR * s1["lat_p95"])
    V["FALSIFIER"] = "FIRED" if fired else "NOT FIRED"
    if fired:
        L.append("FALSIFIER: FIRED: S3 ran at %.2f calls/min >= 50 with 429 share %.4f <= 2%%, 0 exhausted, p95 %.3f <= 1.5"
                 " x p95(S1): the 09-16 regime is back; P1 FALSIFIED; C2 reads build" % (
                     s3["rate"], s3["share"], s3["lat_p95"]))
    else:
        L.append("FALSIFIER: NOT FIRED%s" % ("" if s3 is not None else " (S3 not posted)"))
    L.append("P1 and the falsifier, joined (R6): P1 %s, falsifier %s" % (V["P1"], V["FALSIFIER"]))
    return L, V


def support_lines(stats):
    L = ["SUPPORT (the registration's (a)-(g)): deciding denominators = the per-step invocations (registered 24 / 36 /"
         " 48 / 64 / 76, S6 150) and their HTTP attempts; observed: %s." % ", ".join(
             "%s %d inv / %d att" % (s, stats[s]["n"], stats[s]["http"]) for s in sorted(stats)),
         "  cluster structure temporal (one limiter window); Kish NOT DEFINED; DEFF NO SOURCE: declared DEFF = n per"
         " step, n_eff = 1 per step for any inference about the regime; SE none reported.",
         "  exact CP 95%% upper bounds of the 429 share (DESCRIPTIVE, R1; they decide nothing): %s." % ", ".join(
             "%s %d/%d -> %s" % (s, stats[s]["n429"], stats[s]["http"], _s(stats[s]["cp95"], 4)) for s in sorted(stats)),
         "  MDE: at n = 48, P(<= 1 of 48 | p = 0.10) = 0.0403; a step cannot certify a 429 share <= 2% (the bar is a"
         " screening threshold); the regimes differ >= 2x in rate per doubling against a timing spread 1.31.",
         "  SCOREABLE: C0, P1, P2, P3, P5 and the falsifier on the observed points; DESCRIPTIVE-ONLY: the 429 share at"
         " the 2% bar and any inference beyond the probe day (X3: consumers outside this machine are not seen)."]
    return L


def bins(att, width=10.0):
    if not att:
        return []
    t0 = min(a["t_send"] for a in att)
    b = collections.defaultdict(lambda: [0, 0])
    for a in att:
        k = int((a["t_send"] - t0) // width)
        b[k][0] += 1
        b[k][1] += 1 if a["status"] == 429 else 0
    return [(k * width, b[k][0], b[k][1]) for k in sorted(b)]


def analyze(out_dir, ledger_dir, out=print, write=True):
    """The outcome of record: write-once (mode x) from a complete probe; otherwise the _partial file."""
    p = paths(out_dir)
    need(os.path.exists(p["db"]), "no probe DB at %s" % p["db"])
    con = pg.open_ro(p["db"])
    try:
        meta = dict(con.execute("SELECT key, value FROM meta").fetchall())
        inv, att, ev = load_rows(con)
        x1rows = con.execute("SELECT where_, ok, x2_ok FROM x1 ORDER BY id").fetchall()
        gate_rows = con.execute("SELECT gate_hits FROM launch ORDER BY k").fetchall()
        steps_present = sorted({r["step"] for r in inv}, key=lambda s: [a for a, _N, _ids in step_slots()].index(s))
        stats = {s: step_stats(s, inv, att, ev) for s in steps_present}
        invids = {r["idx"] for r in inv}
        aborted = {s for s, e, _n, _k in ev if e == "abort"}
        complete_steps = {s: stats[s] for s in steps_present if ramp_complete(s, invids, aborted)}
    finally:
        con.close()
    need("S1" in complete_steps, "S1 is not complete: nothing to analyse")
    d = decide(complete_steps)
    js = ACC.read_journal(p["journal"])
    led = atl.ledger_calls(TEST, ledger_dir)
    days = sorted(js["per_day"])
    jb_days = [dd for dd in days if any(r.get("test") == JB_TEST for r in atl._rows(atl.day_ledger_path(ledger_dir, dd)))]
    k46 = {"median_completion_tokens": float(meta["k46_median_completion_tokens"])}
    targets = json.loads(meta["targets"])
    k46_user_q50 = targets["q50"] - int(meta["empty_body_bytes"])
    ub = median([r["user_bytes"] for r in inv])
    tk = median([r["completion_tokens"] for r in inv if r["outcome"] == "RETURNED" and r["completion_tokens"] is not None])
    pilot_ok = os.path.exists(p["pilot_pass"])
    v = {"V1": bool(x1rows) and all(o and x2 for _w, o, x2 in x1rows) and not jb_days,
         "V2": bool(gate_rows) and all(h == 0 for (h,) in gate_rows), "V3": led == js["invocations"] and js["invocations"] <= int(meta["ceiling"]) and not js["unresolved"],
         "V4": pilot_ok,
         "V5_bytes": ub is not None and abs(ub - k46_user_q50) <= V5_BYTES * k46_user_q50,
         "V5_tokens": tk is not None and abs(tk - k46["median_completion_tokens"]) <= V5_TOKENS *
         k46["median_completion_tokens"],
         "user_bytes_median": ub, "k46_user_q50": k46_user_q50, "tokens_median": tk,
         "rate_header_names": sorted({k for a in att if a["rate_headers"] for k in json.loads(a["rate_headers"])})}
    lines, verdicts = score(complete_steps, d, v, k46)
    head = ["JV2-RATE-PROBE outcome (registration docs/judge_v2_program.md L18979-L19094, bf9d80b; script blob %s)" %
            meta["script_blob"],
            "NOT READ: accuracy, ties, leakage. There is no key of record, no reference of record and no contestant, so"
            " the 5.7% test-retest floor, both tie conventions and the CONSENSUS-FIT REF coefficient do not apply.",
            "judge %s, provider %s, cap %s, temperature %s; single order; SYNTHETIC-DEV payloads (seed %s); system sha256"
            " %s = K46's" % (meta["judge"], meta["provider"], meta["cap"], meta["temperature"], meta["seed"],
                             meta["system_sha"]),
            "ACCOUNTING: journal invocations %d (unresolved %d; by outcome %s) | ledgers %d | ceiling %s | posting days %s"
            " | JudgeBench rows on a posting day: %s" % (js["invocations"], len(js["unresolved"]),
                                                         json.dumps(js["by_outcome"], sort_keys=True), led,
                                                         meta["ceiling"], json.dumps(js["per_day"], sort_keys=True),
                                                         jb_days or "none"),
            "X1 / X2 at every step boundary: %d sample(s), all OK: %s" % (len(x1rows), all(o and x2 for _w, o, x2 in
                                                                                           x1rows)),
            "ADMISSIBILITY OF RECORD: " + ADMISSIBILITY_OF_RECORD,
            "PER STEP (latency = reservation to return, rr's backoff included; p95 nearest-rank; rate = invocations over"
            " the step's wall per minute; admissibility as amended pre-data: " + ADMISSIBILITY_OF_RECORD + "):"]
    for s in steps_present:
        st = stats[s]
        ok = admissible(st, d["p95_s1"]) if s in complete_steps else (None, ["incomplete"])
        head.append("  %s N=%s: inv %d, HTTP %d, 429 %d (share %s, CP95 %s), exhausted %d, orphans %d, not sent %d,"
                    " %s calls/min, latency median %s / p95 %s / max %s s, median completion tokens %s, median user"
                    " bytes %s, unparsed %d of %d returned%s -> %s%s" % (
                        s, st["Ns"], st["n"], st["http"], st["n429"], _s(st["share"], 4), _s(st["cp95"], 4),
                        st["exhausted"], st["orphans"], st["not_sent"], _s(st["rate"], 2), _s(st["lat_median"]),
                        _s(st["lat_p95"]), _s(st["lat_max"]), st["tokens_median"], st["user_bytes_median"],
                        st["unparsed"], st["returned"], " [ABORTED]" if st["aborted"] else "",
                        "ADMISSIBLE" if ok[0] else "INADMISSIBLE", "" if ok[0] else " (%s)" % "; ".join(ok[1])) +
                    (" [(c) exempt (A2)]" if c_exempt(st) else ""))
    head.append("N* = %d, G = %s, knee: %s" % (d["nstar_final"], _s(d["G"]), "none" if d["knee"] is None else
                                               "%s -> %s bought x%.3f (< 1.3; %s)" % d["knee"]))
    head.append(QUALIFIER_A4)
    head.append("REALISM: probe median user bytes %s vs K46 q50 user bytes %d (+-10%%); probe median completion tokens %s"
                " vs K46 %s (+-30%%)" % (ub, k46_user_q50, tk, k46["median_completion_tokens"]))
    provider_errors = collections.Counter(a["provider_error"] for a in att if a["provider_error"])
    head.append("429 / 5xx provider error codes, %s: %s" % (DESCRIPTIVE_A4, dict(provider_errors) or "none"))
    head.append("RATE HEADERS (names; x-ratelimit-remaining-* among them), %s: %s" % (
        DESCRIPTIVE_A4, v["rate_header_names"] or "none"))
    head.append("10-s BINS (t from the first send, sends, 429s): %s" % bins(att))
    body = head + ["", "SCORING:"] + ["  " + x for x in lines] + [""] + support_lines(complete_steps) + [
        "", "WHAT THIS DOES NOT SHOW: the limit on any other day (N* is a snapshot); the reasoning deployment; whether"
            " concurrency changes verdicts; whether synthetic items are judged like real ones; consumers outside this"
            " machine (X3)."]
    complete = d["complete"] and not js["unresolved"]
    text = "\n".join(body) + "\n"
    for x in body:
        out(x)
    if not write:
        return verdicts, text
    if complete:
        if MUTANT == "outcome_overwrite":
            mode = "w"
        else:
            mode = "x"
        try:
            with open(p["outcome"], mode, encoding="utf-8") as f:
                f.write(text)
        except FileExistsError:
            refuse("the outcome of record %s exists: write-once, never rewritten" % p["outcome"])
        out("[OUTCOME] written (write-once): %s" % p["outcome"])
    else:
        with open(p["partial"], "w", encoding="utf-8") as f:
            f.write("PARTIAL (the probe is not complete by its own rule; NOT the outcome of record)\n" + text)
        out("[OUTCOME] the probe is not complete: %s written instead (not of record)" % p["partial"])
    return verdicts, text


# ── the dry-run and the CLI ────────────────────────────────────────────────────────────────────────────────────────

def dry_run(out_dir, ledger_dir, data_root=None, out=print):
    calls = {"n": 0}
    real = urllib.request.urlopen

    def tripwire(*a, **k):
        calls["n"] += 1
        raise RuntimeError("the dry-run posts nothing")
    urllib.request.urlopen = tripwire
    try:
        transport(data_root, out)
        out("pool: none (SYNTHETIC-DEV payloads; no pool item is posted; the corpora are read once by the content gate)")
        live_guard(out)
        blob, lf16, crlf16, wt = script_identity()
        out("script: tools/analysis/jv2_rate_probe.py blob:%s / sha256-lf16:%s / sha256-crlf16:%s (the working tree is"
            " the %s rendering; the LF rendering is of record)" % (blob, lf16, crlf16, wt))
        out("[OPT] python optimisation level %d -> %s" % (optimize_level(), "a launch is admitted" if optimize_level()
                                                            == 0 else "a launch would be REFUSED (the dry-run continues)"))
        day = local_day()
        k46 = k46_readings(out)
        out("[K46] run2 store (R8: outcome written): %d posted bodies; body bytes q10 / q50 / q90 = %d / %d / %d; median"
            " completion tokens %s; system_template_sha %s; rubric_sha %s; system turn sha256 %s" % (
                k46["n"], k46["q10"], k46["q50"], k46["q90"], k46["median_completion_tokens"], k46["system_template_sha"],
                k46["rubric_sha"], k46["system_turn_sha256"]))
        plan = build_plan(k46, out)
        e = plan["empty_body_bytes"]
        out("[PLAN] system turn sha256 %s = K46's launch manifest: True; template / rubric shas = K46's: True" %
            plan["system_sha"])
        out("[PLAN] size targets (posted BODY bytes; user bytes = body - %d): q10 %d (%d), q50 %d (%d), q90 %d (%d)" % (
            e, plan["targets"]["q10"], plan["targets"]["q10"] - e, plan["targets"]["q50"], plan["targets"]["q50"] - e,
            plan["targets"]["q90"], plan["targets"]["q90"] - e))
        hits = content_gate(plan, out)
        k46_idle(out)
        x1_check("the dry-run", out, refuse_on=False)
        x2_check(day, ledger_dir, "the dry-run (day %s)" % day, out, refuse_on=False)
        out("[PLAN] STEPS (the ramp stops at the first inadmissible step; S6 only if N* >= 2):")
        for s, N, ids in step_slots():
            out("  %s N=%s: %d invocation(s), slots %d-%d, %s" % (s, N if N else "N*", len(ids), ids[0], ids[-1],
                                                                  "60 s idle gap before" if s != "S1" else
                                                                  "the first 12 = the PILOT 12"))
        out("[PLAN] TOTAL REAL-CALL BUDGET: at most %d invocations (ramp %d + S6 %d), ceiling %d (journal cap), 1 cce each"
            " = <= %d cce; HTTP attempts per invocation <= 6 (rr's retries; not the ledger unit)" % (
                PLAN_TOTAL, PLAN_TOTAL - S6_INVOCATIONS, S6_INVOCATIONS, ceiling(), PLAN_TOTAL))
        p = paths(out_dir)
        js = ACC.read_journal(p["journal"])
        account(PLAN_TOTAL - js["invocations"], ledger_dir, day, "dry-run (the whole remaining plan)", False, out,
                own_journal=js["invocations"])
        out("[PLAN] probe DB %s (exists: %s); journal %s (invocations %d, unresolved %d)" % (
            p["db"], os.path.exists(p["db"]), p["journal"], js["invocations"], len(js["unresolved"])))
        out("[PLAN] plan sha256 %s (the launch's --expect-plan-sha)" % plan["plan_sha"])
        out("[DRY-RUN] 0 calls: urlopen invoked %d time(s); nothing written; content gate hits %d" % (calls["n"], hits))
        need(calls["n"] == 0, "the dry-run touched the network")
        return {"plan_sha": plan["plan_sha"], "hits": hits, "calls": calls["n"]}
    finally:
        urllib.request.urlopen = real


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--pilot", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--analyze", action="store_true")
    g.add_argument("--selftest", action="store_true")
    ap.add_argument("--expect-plan-sha", default=None)
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        import jv2_rate_probe_selftest as T
        return T.main()
    out_dir = a.out_dir or default_out_dir()
    ledger_dir = default_ledger_dir()
    if a.dry_run:
        dry_run(out_dir, ledger_dir)
        return 0
    if a.analyze:
        analyze(out_dir, ledger_dir)
        return 0
    need(a.out_dir is None or os.path.realpath(a.out_dir) == os.path.realpath(default_out_dir()),
         "a record launch writes to %s only" % default_out_dir())
    Launch(out_dir, ledger_dir, "pilot" if a.pilot else "run", True, a.expect_plan_sha).execute()
    return 0


if __name__ == "__main__":
    sys.exit(main())
