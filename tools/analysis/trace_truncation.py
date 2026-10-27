"""TRACE-TRUNCATION - is a judge holding an EXACT OUTCOME REFERENCE an outcome judge, or still a reasoning-content judge?
(judged; ceiling 2,184 calls = 360 pairs x 3 arms x 2 orders + the 24-call pilot margin; accepted by the author on
2026-09-23: "the paid tests are fine I accept them", docs/plan_2026-09-15.md Amendment 12).

REGISTERED 2026-09-23 BEFORE ANY CODE OR CALL: docs/judge_v2_program.md L14972-L15011, commit fad9ea2; record
docs/agents/results/TRACE-TRUNCATION.json. The lead is docs/agents/plans/2026-09-17_continual_capability_profile_leads.md
C4 (L181-L185). This file is the RETARGET of tools/analysis/causal_length.py the registration names (L1 / L1-V / L1-V2);
causal_length.py itself is not edited (its three arms are re-implemented here under the registration's definitions,
which differ from L1's: see ARMS below).

  python tools/analysis/trace_truncation.py --selftest            0 calls; synthetic DBs under tempfile.mkdtemp(), an
                                                                  INJECTED FAKE POSTER, a socket guard; opens no DB of record;
                                                                  every criterion / prediction / falsifier branch EXECUTED
                                                                  and the coverage asserted (also run under python -O)
  python tools/analysis/trace_truncation.py --emit-pairs PATH     0 calls: writes the ELIGIBLE PAIR LIST (deterministic text)
                                                                  to PATH, write-once, and prints its sha256 (LF) and blob
                                                                  id. The registrar commits it as
                                                                  docs/agents/results/evidence/TRACE-TRUNCATION_pairs.txt
                                                                  BEFORE ANY CALL; PINNED_PAIRS_SHA256 below is then set to it
  python tools/analysis/trace_truncation.py --dry-run             0 calls: pool first; the pair list re-derived and compared
                                                                  with the evidence and the pin; every payload of every arm
                                                                  assembled; the three identity asserts and the FULL-PAYLOAD
                                                                  pre-call leakage scan on all of them; the payload anchors,
                                                                  the counts, the night total and the ceiling; posts nothing
  python tools/analysis/trace_truncation.py --pilot 12 --go       24 calls: the first 4 pairs x 3 arms (12 dual-order matches)
  python tools/analysis/trace_truncation.py --run --go            the remaining calls; REFUSES unless the pilot's 12 matches are
                                                                  cached and the truncation guard reads <= 5% unusable on them
  python tools/analysis/trace_truncation.py --analyze             paired readout; the outcome of record is WRITE-ONCE (mode "x")
                                                                  and only from a complete cache; otherwise _PILOT / _partial
  python tools/analysis/trace_truncation.py --leakscan            0 calls: the full-payload scan over the POSTED bodies stored
                                                                  in this test's cache (for the post-run review; it does not
                                                                  replace the reviewer's own scan)

THE GATE. --pilot and --run REFUSE, fail-closed and BEFORE any database is opened, unless (1) --go is given, (2)
docs/reviews/READY_trace_truncation.md exists, is tracked by git, carries no uncommitted change, and its FIRST verdict line
(READY / READY-WITH-CONDITIONS, never NOT READY) names TRACE-TRUNCATION and this script's LF sha16, and (3)
PINNED_PAIRS_SHA256 is set and the committed evidence file hashes to it. Guards raise SystemExit (never assert: -O safe).

POPULATION (the registration's "cap-free MATH population"). The union pool of record paeec37aa28063c75 (MATH slice), verified
by pool_guard.assert_pool_of_record (the FIRST printed line) and by every pair's question id being in
pool_guard.eval_ids(paeec37aa28063c75). The frame is STAGE3-MATH-CAPFREE's own schedule, read from
experiment_results/multicorpus/stage3_math_grok_v2_capfree.db (table schedule; 2,996 matches; its meta must read checker
table v2, terminated-only 1, the deployed judge, temperature omitted, pool paeec37aa28063c75); the key is
checker_answers_v2.db :: math_checker_answers_v2.is_correct (the cap-free run's key; provenance row asserted); the traces,
question texts and targets come from multicorpus_cache_v1.db (eval_results.model_output, corpus_questions.text / .target),
exactly the strings stage3_math posted. ELIGIBLE PAIR = a scheduled match whose two contestants differ on the key (one
checker-correct, one checker-wrong; both terminated, asserted) and whose CORRECT trace is longer by >= THR = 300 characters
(L1's THR). One further exclusion, DECLARED by the builder (a choice for the READY): a pair whose correct trace has NO
reasoning before its final-answer span (span start 0: nothing to truncate, the three arms would be identical) is excluded
and counted. If more than N_PAIRS_MAX = 360 pairs remain, a seeded subsample (SELECT_SEED 42, random.Random, printed) is
drawn and sorted by match id; otherwise all are taken. The list is ordered by stage3 match id.

ARMS (the registration's definitions; all three share the schedule's sides, the question, the reference block, the wrong
trace and the system prompt, BYTE FOR BYTE). Let C be the correct trace and s = answer_span_start(C): the FINAL-ANSWER SPAN
is C[s:] (from the start of the line holding the LAST "\\boxed", or of the last non-empty line when there is none; a lead of
more than MAX_LEAD = 200 characters before the marker is cut at the last sentence end ". " / "? " / "! " inside it) and the
MANIPULATED SPAN is C[:s].
  original = C
  truncate = C[s:]                                  (the correct response cut to its final answer)
  pad      = PAD_UNIT * s + C[s:]                   (the truncated response padded back to the original CHARACTER length with
                                                     neutral non-content bytes: PAD_UNIT = one ASCII space, U+0020; a builder's
                                                     choice for the READY - causal_length.py's FILLER is an English sentence,
                                                     i.e. content, and is therefore not used)
Asserted on EVERY payload before any call (SystemExit on failure): (i) the two user turns decompose EXACTLY into the
template's literal fragments and the three slots (question+reference, trace A, trace B), assembled independently of
str.replace; (ii) outside the manipulated span the truncate and pad payloads are BYTE-IDENTICAL to the original's (prefix
before the correct slot, the answer span, and everything after the slot); (iii) the reference block occurs exactly once,
inside the question slot, before both traces, identical in all arms and orders - the truncation never touches it.

REFERENCE. STAGE3-MATH's CHECKER_OUTPUT block, IMPORTED from stage3_math (REF_BLOCK, asserted equal to
"\\n\\n[Verified reference answer]\\n%s"): the pool's raw target, the exact answer the checker scores against, never a
per-response verdict, never a checklist (REF-CHECKLIST closed). System prompt: stage3_math.system_prompt() (prompt_v2
verify-first template + GEN-ARENA's MATH system prompt and rubric + SCHEMA_INSTRUCTION), sha16 pinned below. The ORIGINAL arm
is therefore byte-identical to the payload STAGE3-MATH-CAPFREE posted for the same match (a DRIFT readout compares the two
verdicts; descriptive only).

LEAKAGE. Pre-call, on every assembled payload (the FULL system + user bodies, both orders, all arms): the frame (everything
outside the two trace slots) must be identical across the three arms and the two orders of a pair - so nothing PER-SIDE sits
outside the traces - and the question slot is PROVED equal to the corpus text + the reference block, the two trace slots
equal to their source bytes (the eval output, or its C[s:] / pad form) by (i)-(ii), so no checker-derived text can enter any
slot. A contestant name outside the trace slots REFUSES; a checker-side token (is_correct, checker, answer_norm, answer_canon,
non_terminated, cap_hit, mathfix) or verdict word (PASS, FAIL, CORRECT, INCORRECT) in the user TEMPLATE refuses; the same
strings in the question slot (dataset text, e.g. "checkerboard") and names inside a trace slot (model text) are COUNTED and
printed, never refused. Post-run, --leakscan repeats the scan on the POSTED bodies stored per row. The registration requires the
post-run reviewer's own full-payload scan as well (BFCL-FLIP-RESEED 7ddf59f); an instrument assert is NOT leakage evidence.

JUDGE AND CACHE. grok-4-1-fast-non-reasoning, cap 8192, TEMPERATURE OMITTED (recorded as "omitted"), dual order (order 1
shows model_a first), TIE on flip, INVALID on a parse failure or finish_reason length / content_filter. Every call through
rejudge_reasoning.call_judge_full; the local body copy is asserted equal to rr.payload_body. Deployment fingerprint
"azure:grok-4-1-fast-non-reasoning" fail-closed (the content-filter sentinel is cached as an unusable row, rule 10). Own NEW
cache experiment_results/multicorpus/trace_truncation.db, one row per (match, arm), with per-row PROVENANCE (both posted user
bodies and their sha16, the system sha16, response ids, finish reasons, completion tokens, fingerprints, submission index,
the script's LF sha); run_meta pinned at first launch (judge, cap, temperature, protocol, pair-list sha, system sha, script
sha) and a relaunch differing on any key is REFUSED. Errors are never cached; a cached row is never re-posted.

BUDGET. The night ledger experiment_results/night_calls_2026-09-23.json is read before every posting launch (the cumulative
count plus this launch must stay <= 14,000, plan Amendment 9; this test's own ledger rows plus this launch <= 2,184) and
APPENDED after it in a `finally` with EVERY posted call counted (errored ones included). Refused, never trimmed.
[CORRECTED 2026-09-24 by the registrar's ruling b0b5d0d (programme L15188-L15206, THE ACCOUNTING FILE), insertion only: the
2026-09-23 night ledger is NOT the count of record for later posts. The guard is accepted_tests_ledger.guard: it refuses on (i)
this test's own ceiling 2,184 (its cache and its rows in every ledger, the larger), (ii) the 4,000-match rule, (iii) 4,060 + the
calls posted by BOTH accepted tests (their caches / ledgers) + this launch > 14,000; all three numbers are printed on every
launch and in the outcome; posted calls are appended to experiment_results/day_calls_<posting date>.json, created write-once.]

READOUTS (--analyze; convention A DECIDES - TIE / INVALID / non-terminated = wrong -, convention B printed beside and decides
nothing; every interval = point +- 1.96 x the question-clustered bootstrap SE, B 2,000, seed 42, and C1 / C2 re-read at 20
further seeds 43-62 with the share of seeds that change a verdict). C0 validity FIRST and PRE-EMPTIVE (a failed C0 makes C1
and C2 UNDETERMINED BY VALIDITY and the falsifier is not evaluated): the list sha = the committed evidence = the pin; the
posted bodies = the re-assembly (so the identity asserts hold on 100% of POSTED payloads); the reference intact on 100%; the
pilot's truncation guard (<= 5% unusable). C1 drop = acc(original) - acc(truncate), paired: HELD iff wholly below 0.10,
FAILED iff wholly above, UNDETERMINED iff the interval contains 0.10 (disjoint). C2 acc(truncate) vs 0.70: FAILED iff wholly
below, HELD iff wholly above, else UNDETERMINED. C3 the pad control acc(pad) - acc(original), descriptive; C1's reading is
QUALIFIED as edit-sensitivity iff its interval excludes 0 and |point| > 0.05. C4 the drop beside the PER-MATCH retest floors
of record (CANARY-BASELINE 0.087; DECOMP 0.057; CANARY-EPOCH2-RUNG's within-session d43 if its outcome exists); NO floor is
derived from a pooled per-call rate (TIE-MECHANICS, L14415). SUPPORT: the measured Kish mean cluster size, discordance,
SE, DEFF (bootstrap variance / paired iid variance), n_eff and MDE beside the registered planning values (DEFF 1.18
transported, SE 0.0214 / 0.0193, MDE 0.060 / 0.054; C1 DESCRIPTIVE-ONLY, C2 SCOREABLE). P1-P6 scored HELD / FAILED.

RANDOM STREAMS (the D-1 lesson): (i) selection: deterministic; a subsample only above 360 pairs, SELECT_SEED 42; (ii) the
bootstrap: BOOT_SEED 42, B 2,000, plus seeds 43-62; (iii) the judge's sampling: temperature omitted, not seedable, part of
what is measured; (iv) the posting order: pairs in list order, arms original -> truncate -> pad, order 1 then order 2 within
a job, submitted in that order to the worker pool (the submission index is stored per row; the pool's completion order is
not controlled).
"""
import argparse
import hashlib
import json
import os
import random
import re
import socket
import sys
import tempfile
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sqlite3  # noqa: E402

_TRUE_CONNECT = getattr(sqlite3.connect, "_true_connect", None) or sqlite3.connect

import pool_guard                 # noqa: E402
import rejudge_grok as rj         # noqa: E402
import rejudge_reasoning as rr    # noqa: E402
import stage3_math as s3          # noqa: E402  REF_BLOCK, system_prompt(), PROTOCOL; its DB paths are NOT used
import accepted_tests_ledger as atl  # noqa: E402  the accounting guard ruled at b0b5d0d (the posting-date ledger)

# ----------------------------------------------------------------------------------------------------------------------
# identity of the test and the registered constants
# ----------------------------------------------------------------------------------------------------------------------
TEST = "TRACE-TRUNCATION"
REGISTRATION = ("docs/judge_v2_program.md L14972-L15011 (registered 2026-09-23 at fad9ea2, before any code or call); record "
                "docs/agents/results/TRACE-TRUNCATION.json")
POOL_ID = pool_guard.UNION_POOL                        # paeec37aa28063c75 (its MATH slice)
JUDGE = "grok-4-1-fast-non-reasoning"
MAXTOK = rr.MAX_TOKENS                                 # 8192
TEMPERATURE = None                                     # OMITTED (plan Amendment 1 D2); recorded as "omitted"
EXPECTED_FINGERPRINT = "azure:" + JUDGE
REFUSAL_FINGERPRINT = "azure:refusal"
ARMS = ("original", "truncate", "pad")
THR = 300                                              # the correct trace longer by >= 300 characters (L1's THR)
N_PAIRS_MAX = 360                                      # planning n; a seeded subsample above it
SELECT_SEED = 42
MAX_LEAD = 200                                         # a longer lead before the answer marker is cut at a sentence end
PAD_UNIT = " "                                         # neutral non-content byte (U+0020); a builder's choice for the READY
PILOT_MATCHES = 12                                     # 12 dual-order matches = 4 pairs x 3 arms = 24 calls
CALL_CEILING = 2184                                    # 360 x 3 x 2 + 24
NIGHT_CEILING = 14000                                  # plan Amendment 9
GUARD_RATE = 0.05
BOOT = 2000
BOOT_SEED = 42
EXTRA_SEEDS = tuple(range(43, 63))                     # 20 further seeds
C1_BAR = 0.10
C2_BAR = 0.70
C3_EPS = 0.05
Z = 1.96
FLOORS = (("CANARY-BASELINE pass 1 -> 2 (one week apart), per-match combined verdict", 0.087),
          ("DECOMP (hours apart), per-match", 0.057))
REG_SUPPORT = dict(n=360, deff=1.18, neff=305, se_c1=0.0214, se_c2=0.0193, mde_c1=0.060, mde_c2=0.054, kish=1.353, disc=0.15)
REF_BLOCK_OF_RECORD = "\n\n[Verified reference answer]\n%s"
REF_HEADER = "[Verified reference answer]\n"

# pins (sha256 of the named rendering; see CONTEXT.md rule 8)
PINNED_SYSTEM_SHA16 = "52889f7100eaa585"               # sha256-utf8[:16] of stage3_math.system_prompt() (computed 2026-09-24, 0 calls)
S3_CACHE_SHA256 = "a2ecd01d6433a1906610e7248c10fcb766593911851a8837353daae91350a627"   # stage3_math_grok_v2_capfree.db (steward listing a2ecd01d6433a190)
CHECKER_SHA256 = "6cfaf74d647829d179c4b0885215b4f33ac16449957b9a47c49373dd565500f7"    # checker_answers_v2.db
PINNED_PAIRS_SHA256 = "08a0f84f61718b323ecaa433b75085784fd2cf62a9025bb855d4fb8b1615d7a0"   # sha256-lf of the evidence file (--emit-pairs 2026-09-24, 360 pairs, blob:928917ea)

# ----------------------------------------------------------------------------------------------------------------------
# paths (DATA_ROOT may differ from the code root, as pool_guard allows; nothing is copied into a worktree)
# ----------------------------------------------------------------------------------------------------------------------
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
MC_DIR = os.path.join(DATA_ROOT, "experiment_results", "multicorpus")
S3_CACHE = os.path.join(MC_DIR, "stage3_math_grok_v2_capfree.db")
CHECKER_DB = os.path.join(MC_DIR, "checker_answers_v2.db")
CHECKER_TABLE, CHECKER_META, CHECKER_SCRIPT = "math_checker_answers_v2", "checker_answer_ingest_v2_meta", "tools/analysis/checker_answer_ingest.py --v2"
CORPUS_DB = os.path.join(DATA_ROOT, "multicorpus_cache_v1.db")
CACHE = os.path.join(MC_DIR, "trace_truncation.db")
OUT = os.path.join(MC_DIR, "trace_truncation_outcome.txt")
OUT_PILOT = os.path.join(MC_DIR, "trace_truncation_outcome_PILOT.txt")
OUT_PARTIAL = os.path.join(MC_DIR, "trace_truncation_outcome_partial.txt")
RUNG_OUT = os.path.join(DATA_ROOT, "experiment_results", "x12_crossdomain", "canary_epoch2_outcome.txt")
LEDGER_DIR = os.path.join(DATA_ROOT, "experiment_results")   # day_calls_<posting date>.json (b0b5d0d) + the closed 09-23 file
CANARY_CACHES = atl.default_caches(DATA_ROOT)["CANARY-EPOCH2-RUNG"]   # read-only, for the combined statement (iii)
EVIDENCE = os.path.join(ROOT, "docs", "agents", "results", "evidence", "TRACE-TRUNCATION_pairs.txt")
READY = os.path.join(ROOT, "docs", "reviews", "READY_trace_truncation.md")
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")

REGISTRATION_PHRASES = ("TRACE-TRUNCATION: is a judge holding an EXACT OUTCOME REFERENCE an outcome judge",
                        "THE INTERVAL DECIDES; the three branches are disjoint",
                        "truncate = the correct response cut to its final answer; pad = the truncated response padded back to the original length with neutral non-content bytes",
                        "ceiling 2,184 calls = 360 pairs x 3 arms x 2 orders (2,160) + the 12-match pilot (24)")

LEAK_TOKENS = ("is_correct", "checker", "answer_norm", "answer_canon", "non_terminated", "cap_hit", "mathfix")
LEAK_WORDS = ("PASS", "FAIL", "CORRECT", "INCORRECT")

# ----------------------------------------------------------------------------------------------------------------------
# branch coverage (every criterion / prediction / falsifier print branch registers its tag; the selftest asserts all)
# ----------------------------------------------------------------------------------------------------------------------
ALL_BRANCHES = frozenset(
    ["C0:PASS", "C0:FAIL",
     "C1:HELD", "C1:FAILED", "C1:UND", "C1:UND_VALIDITY",
     "C2:HELD", "C2:FAILED", "C2:UND", "C2:UND_VALIDITY",
     "C3:QUALIFIED", "C3:NOT_QUALIFIED",
     "C4:BELOW_FLOOR", "C4:ABOVE_FLOOR", "C4:RUNG_READ", "C4:RUNG_ABSENT",
     "FALS:C2_FIRES", "FALS:C1_FIRES", "FALS:NOT_FIRED", "FALS:NOT_EVALUATED",
     "SUPPORT:OK", "SUPPORT:DEGENERATE"]
    + ["%s:%s" % (p, v) for p in ("P1", "P2", "P3", "P4", "P5", "P6") for v in ("HELD", "FAILED")])
BRANCHES_HIT = set()


def hit(tag):
    if tag not in ALL_BRANCHES:
        raise SystemExit("[BRANCH] undeclared branch tag %r" % tag)
    BRANCHES_HIT.add(tag)


# ----------------------------------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------------------------------
def rel(p):
    for base in (ROOT, DATA_ROOT):
        try:
            r = os.path.relpath(p, base)
            if not r.startswith(".."):
                return r
        except ValueError:
            pass
    return p


def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def script_sha_lf():
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def script_sha_raw():
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def git_blob_id(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def temp_label():
    return "omitted" if TEMPERATURE is None else repr(TEMPERATURE)


def protocol():
    return ("TRACE-TRUNCATION: STAGE3-MATH-CAPFREE payloads (prompt_v2 verify-first + GEN-ARENA MATH system prompt and rubric + "
            "SCHEMA_INSTRUCTION; CHECKER_OUTPUT reference block '[Verified reference answer]' = the pool's raw target) | judge %s "
            "via rejudge_reasoning.call_judge_full | arms original / truncate (C[s:]) / pad (PAD_UNIT x s + C[s:], PAD_UNIT %r) | "
            "dual order, TIE on flip, INVALID on parse failure or finish_reason length / content_filter | max_tokens %d | "
            "temperature %s" % (JUDGE, PAD_UNIT, MAXTOK, temp_label()))


# ----------------------------------------------------------------------------------------------------------------------
# THE DB GUARD: every sqlite3.connect in the process passes here once installed. Reads of the three inputs are rewritten to
# file:<abs>?mode=ro&immutable=1 AFTER the -wal / -journal emptiness check; the ONLY writable file is this test's own cache.
# ----------------------------------------------------------------------------------------------------------------------
_OPENED = []


def _path_of(database):
    s = str(database)
    if s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
    return os.path.normcase(os.path.abspath(s))


def _sidecar_check(path):
    for suf in ("-wal", "-journal"):
        sc = path + suf
        if os.path.exists(sc) and os.path.getsize(sc) > 0:
            raise SystemExit("[DBGUARD] REFUSED: %s is non-empty (%d bytes); an immutable read would hide a live or hot "
                             "transaction. A FAILED PRECONDITION, never an outcome: stop the writer or have the data-steward "
                             "checkpoint it, then re-run." % (sc, os.path.getsize(sc)))


def _readable():
    return {os.path.normcase(os.path.abspath(p)) for p in (S3_CACHE, CHECKER_DB, CORPUS_DB, pool_guard.db_path(POOL_ID), *CANARY_CACHES)}


def _guarded_connect(database, *args, **kwargs):
    s = str(database)
    if s == ":memory:":
        return _TRUE_CONNECT(database, *args, **kwargs)
    p = _path_of(database)
    own = os.path.normcase(os.path.abspath(CACHE))
    if p == own:
        _OPENED.append(("rw" if not s.startswith("file:") else "ro", p))
        return _TRUE_CONNECT(database, *args, **kwargs)
    if p not in _readable():
        raise SystemExit("[DBGUARD] REFUSED: %s may open only its three inputs (read-only, immutable) and its own cache %s; "
                         "a connection to %r was attempted." % (TEST, rel(CACHE), s))
    if not os.path.isfile(p):
        raise SystemExit("[DBGUARD] %s is missing (set TAXOARENA_DATA_ROOT); nothing is opened and nothing is posted." % p)
    _sidecar_check(p)
    uri = "file:%s?mode=ro&immutable=1" % p.replace("\\", "/")
    kwargs = dict(kwargs)
    kwargs["uri"] = True
    _OPENED.append(("ro-immutable", p))
    return _TRUE_CONNECT(uri, *args, **kwargs)


_guarded_connect._true_connect = _TRUE_CONNECT


def install_db_guard():
    sqlite3.connect = _guarded_connect


def dbguard_line():
    seen = []
    for m, p in _OPENED:
        if (m, p) not in seen:
            seen.append((m, p))
    return "[DBGUARD] %d connect(s): %s" % (len(_OPENED), "; ".join("%s %s" % (m, rel(p)) for m, p in seen) or "(none)")


def connect_ro(path):
    return sqlite3.connect("file:%s?mode=ro" % os.path.abspath(path).replace("\\", "/"), uri=True)


# ----------------------------------------------------------------------------------------------------------------------
# the registration, the payload body, the system prompt
# ----------------------------------------------------------------------------------------------------------------------
def assert_registration():
    txt = " ".join(open(PROGRAMME, encoding="utf-8").read().split())
    missing = [p for p in REGISTRATION_PHRASES if " ".join(p.split()) not in txt]
    if missing:
        raise SystemExit("[RECORD] the registration no longer carries %s; this script is not its instrument." % missing)


def configure_rr():
    rr.PROVIDER = "azure"
    rr.JUDGE_MODEL = JUDGE
    rr.MAX_TOKENS = MAXTOK
    rr.TEMPERATURE = TEMPERATURE


def payload_body(system, user):
    """Local copy of rejudge_reasoning.payload_body (model / max_tokens / messages [/ temperature]); asserted equal below."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None:
        body["temperature"] = rr.TEMPERATURE
    return body


def assert_payload_source():
    import inspect
    src = inspect.getsource(rr.payload_body)
    if not ('payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src
            and 'payload_body["temperature"] = TEMPERATURE' in src):
        raise SystemExit("[BODY] rejudge_reasoning.payload_body changed; this script's copy is not verified")
    if "payload_bytes(system, user)" not in inspect.getsource(rr.call_judge_full):
        raise SystemExit("[BODY] call_judge_full no longer posts payload_body's bytes")
    if payload_body("S", "U") != rr.payload_body("S", "U"):
        raise SystemExit("[BODY] local body %r != rr.payload_body %r" % (payload_body("S", "U"), rr.payload_body("S", "U")))
    want = ("model", "max_tokens", "messages") + (("temperature",) if TEMPERATURE is not None else ())
    if tuple(payload_body("S", "U")) != want:
        raise SystemExit("[BODY] key tuple %r != %r" % (tuple(payload_body("S", "U")), want))


def system_prompt():
    sp = s3.system_prompt()
    if s3.REF_BLOCK != REF_BLOCK_OF_RECORD:
        raise SystemExit("[REF] stage3_math.REF_BLOCK %r != the CHECKER_OUTPUT block of record %r" % (s3.REF_BLOCK, REF_BLOCK_OF_RECORD))
    if sha16(sp) != PINNED_SYSTEM_SHA16:
        raise SystemExit("[SYSTEM] stage3_math.system_prompt() sha16 %s != pinned %s: the MATH prompt moved; REFUSED"
                         % (sha16(sp), PINNED_SYSTEM_SHA16))
    return sp


# ----------------------------------------------------------------------------------------------------------------------
# the final-answer span and the three arms
# ----------------------------------------------------------------------------------------------------------------------
def answer_span_start(text):
    """(s, rule): the final-answer span is text[s:]. Anchor = the LAST '\\boxed' (rule 'boxed'), else the start of the last
    non-empty line (rule 'last-line'). s = the start of the anchor's line; when that line's lead before the anchor exceeds
    MAX_LEAD characters (or, for 'last-line', the line itself does), s moves to just after the last sentence end ('. ',
    '? ', '! ') inside the lead ('+sentence'), else to the anchor itself ('+marker'). Deterministic, pure."""
    idx = text.rfind("\\boxed")
    if idx >= 0:
        rule, anchor = "boxed", idx
    else:
        body = text.rstrip()
        rule, anchor = "last-line", body.rfind("\n") + 1
        if len(body) - anchor > MAX_LEAD:                    # a long last line: its last sentence is the answer
            c = max(body.rfind(p, anchor, len(body) - 1) for p in (". ", "? ", "! "))
            return (c + 2, rule + "+sentence") if c >= 0 else (anchor, rule)
        return anchor, rule
    line_start = text.rfind("\n", 0, anchor) + 1
    if anchor - line_start > MAX_LEAD:
        c = max(text.rfind(p, line_start, anchor) for p in (". ", "? ", "! "))
        return (c + 2, rule + "+sentence") if c >= 0 else (anchor, rule + "+marker")
    return line_start, rule


def arm_trace(correct, s, arm):
    if arm == "original":
        return correct
    if arm == "truncate":
        return correct[s:]
    if arm == "pad":
        return PAD_UNIT * s + correct[s:]
    raise SystemExit("[ARM] %r is not one of %s" % (arm, ARMS))


def template_fragments():
    """USER_TEMPLATE split at its three slots, in order; asserted to hold each slot exactly once, $query first."""
    t = rj.USER_TEMPLATE
    if not (t.count("$query") == t.count("$traceA") == t.count("$traceB") == 1
            and t.index("$query") < t.index("$traceA") < t.index("$traceB")):
        raise SystemExit("[TEMPLATE] rejudge_grok.USER_TEMPLATE no longer has $query < $traceA < $traceB once each")
    f0, rest = t.split("$query")
    f1, rest = rest.split("$traceA")
    f2, f3 = rest.split("$traceB")
    return f0, f1, f2, f3


def build_user(q, ta, tb):
    """(user, offsets): the user turn assembled from the template fragments by concatenation (independent of str.replace),
    and the [start, end) offsets of the query, slot A and slot B."""
    f0, f1, f2, f3 = template_fragments()
    parts = [f0, q, f1, ta, f2, tb, f3]
    u = "".join(parts)
    o_q = len(f0)
    o_a = o_q + len(q) + len(f1)
    o_b = o_a + len(ta) + len(f2)
    return u, {"q": (o_q, o_q + len(q)), "A": (o_a, o_a + len(ta)), "B": (o_b, o_b + len(tb))}


def assemble(pair, arm, src):
    """(system, u1, u2, meta) for one (pair, arm). Order 1 shows model_a as Model A; order 2 shows model_b as Model A. The
    correct trace is manipulated; the wrong trace, the question, the reference and the system are never touched."""
    q = src["text"][pair["qid"]] + REF_BLOCK_OF_RECORD % src["target"][pair["qid"]]
    c_raw, w_raw = src["out"][(pair["qid"], pair["correct"])], src["out"][(pair["qid"], pair["wrong"])]
    ct = arm_trace(c_raw, pair["s"], arm)
    ta, tb = (ct, w_raw) if pair["correct"] == pair["model_a"] else (w_raw, ct)
    u1, off1 = build_user(q, ta, tb)
    u2, off2 = build_user(q, tb, ta)
    if u1 != rj.build_user_prompt(q, ta, tb) or u2 != rj.build_user_prompt(q, tb, ta):
        raise SystemExit("[ASSEMBLY] match %d arm %s: concatenation != rejudge_grok.build_user_prompt (a slot carried a template "
                         "placeholder); REFUSED" % (pair["mid"], arm))
    return system_prompt(), u1, u2, dict(q=q, ct=ct, wt=w_raw, off1=off1, off2=off2,
                                         cslot1="A" if pair["correct"] == pair["model_a"] else "B")


def check_pair_payloads(pair, src, names):
    """The three identity asserts and the full-payload pre-call leakage scan for ALL payloads of one pair. Returns the
    assembled {arm: (system, u1, u2, meta)} and a Counter of scan facts. SystemExit on any failure."""
    got = {arm: assemble(pair, arm, src) for arm in ARMS}
    facts = Counter()
    so, uo1, uo2, mo = got["original"]
    s = pair["s"]
    c_raw = src["out"][(pair["qid"], pair["correct"])]
    ans = c_raw[s:]
    frame_ref = None
    for arm in ARMS:
        sy, u1, u2, m = got[arm]
        if sy != so:
            raise SystemExit("[IDENTITY] match %d arm %s: the system prompt differs from the original arm's" % (pair["mid"], arm))
        for order, u, uo, off, offo, cslot in ((1, u1, uo1, m["off1"], mo["off1"], m["cslot1"]),
                                               (2, u2, uo2, m["off2"], mo["off2"], "B" if m["cslot1"] == "A" else "A")):
            wslot = "B" if cslot == "A" else "A"
            c0, c1 = off[cslot]
            o0, o1 = offo[cslot]
            # (i) exact decomposition: slots hold exactly their source bytes
            if u[off["q"][0]:off["q"][1]] != m["q"] or u[c0:c1] != m["ct"] or u[off[wslot][0]:off[wslot][1]] != m["wt"]:
                raise SystemExit("[IDENTITY] match %d arm %s order %d: a slot does not hold its source bytes" % (pair["mid"], arm, order))
            if m["wt"] != src["out"][(pair["qid"], pair["wrong"])]:
                raise SystemExit("[IDENTITY] match %d arm %s: the wrong trace was touched" % (pair["mid"], arm))
            # (ii) byte identity outside the manipulated span C[:s]
            if u[:c0] != uo[:o0] or u[c1:] != uo[o1:]:
                raise SystemExit("[IDENTITY] match %d arm %s order %d: bytes outside the correct slot differ from the original arm"
                                 % (pair["mid"], arm, order))
            if not u[c0:c1].endswith(ans) or uo[o0:o1] != c_raw or not c_raw.endswith(ans):
                raise SystemExit("[IDENTITY] match %d arm %s order %d: the final-answer span is not preserved" % (pair["mid"], arm, order))
            if arm == "pad" and (c1 - c0 != o1 - o0 or u[c0:c0 + s] != PAD_UNIT * s):
                raise SystemExit("[IDENTITY] match %d order %d: the pad arm is not PAD_UNIT x s + C[s:] at the original length"
                                 % (pair["mid"], order))
            if arm == "truncate" and u[c0:c1] != ans:
                raise SystemExit("[IDENTITY] match %d order %d: the truncate arm is not C[s:]" % (pair["mid"], order))
            # (iii) the reference block: once, inside the question slot, before both traces, identical everywhere
            ref = REF_HEADER + src["target"][pair["qid"]]
            r_at = u.find(ref)
            if u.count(REF_HEADER) != 1 + m["ct"].count(REF_HEADER) + m["wt"].count(REF_HEADER) \
                    or not (off["q"][0] <= r_at < off["q"][1]) or r_at >= min(off["A"][0], off["B"][0]):
                raise SystemExit("[REFERENCE] match %d arm %s order %d: the reference block is not intact in the question slot"
                                 % (pair["mid"], arm, order))
            facts["reference_intact"] += 1
            # the frame = everything outside the two trace slots; identical across arms and orders of the pair
            fr = (u[:off["A"][0]], u[off["A"][1]:off["B"][0]], u[off["B"][1]:])
            if frame_ref is None:
                frame_ref = fr
            elif fr != frame_ref:
                raise SystemExit("[LEAK] match %d arm %s order %d: the frame differs across arms / orders" % (pair["mid"], arm, order))
            # regions: the TEMPLATE (constant literal fragments), the QUESTION SLOT (proved = corpus text + the reference block by (i)),
            # the two TRACE SLOTS (proved = source bytes or their C[s:] / pad form by (i)-(ii)). A contestant name outside the traces
            # REFUSES; a checker-side token or verdict word in the TEMPLATE refuses (it would be a code change); in the question slot
            # or a trace slot it is dataset / model text and is COUNTED and printed (e.g. "checkerboard" in a MATH question).
            template_txt = "".join(template_fragments())
            qslot = u[off["q"][0]:off["q"][1]]
            tslots = (u[off["A"][0]:off["A"][1]], u[off["B"][0]:off["B"][1]])
            for nm in names:
                if nm in template_txt or nm in qslot or nm in sy:
                    raise SystemExit("[LEAK] match %d arm %s order %d: the contestant name %r is outside the trace slots" % (pair["mid"], arm, order, nm))
                facts["name_in_trace"] += sum(nm in t for t in tslots)
            for tok in LEAK_TOKENS:
                if tok.lower() in template_txt.lower():
                    raise SystemExit("[LEAK] the checker-side token %r is in the user template" % tok)
                facts["token_in_question"] += int(tok.lower() in qslot.lower())
            for w in LEAK_WORDS:
                if re.search(r"\b%s\b" % w, template_txt):
                    raise SystemExit("[LEAK] the verdict word %r is in the user template" % w)
                facts["word_in_question"] += int(bool(re.search(r"\b%s\b" % w, qslot)))
            body = payload_body(sy, u)
            if "temperature" in body or body["model"] != JUDGE or body["max_tokens"] != MAXTOK:
                raise SystemExit("[BODY] match %d arm %s order %d: %r" % (pair["mid"], arm, order, {k: body[k] for k in body if k != "messages"}))
            facts["payloads"] += 1
            facts["identity_outside_span"] += 1
            facts["frame_clean"] += 1
    return got, facts


# ----------------------------------------------------------------------------------------------------------------------
# the population and the eligible pair list
# ----------------------------------------------------------------------------------------------------------------------
def load_sources():
    """The stage3 cap-free schedule (+ meta), the v2 checker key, the corpus texts / targets / outputs. Read-only."""
    for path, want in ((S3_CACHE, S3_CACHE_SHA256), (CHECKER_DB, CHECKER_SHA256)):
        if not os.path.isfile(path):
            raise SystemExit("[SOURCE] %s is missing (set TAXOARENA_DATA_ROOT); nothing is opened." % path)
        got = file_sha256(path)
        if want is not None and got != want:
            raise SystemExit("[SOURCE] %s sha256 %s != pinned %s: an input of record moved; REFUSED" % (rel(path), got, want))
    s3c = connect_ro(S3_CACHE)
    meta = dict(s3c.execute("SELECT key, value FROM meta"))
    need = {"pool_id": POOL_ID, "judge": JUDGE, "checker_table": "v2", "terminated_only": "1"}
    bad = {k: (meta.get(k), v) for k, v in need.items() if meta.get(k) != v}
    if bad or not str(meta.get("temperature", "")).startswith("omitted"):
        raise SystemExit("[SOURCE] %s meta is not the cap-free run of record: %s temperature %r" % (rel(S3_CACHE), bad, meta.get("temperature")))
    sched = s3c.execute("SELECT match_id, qid, model_a, model_b, domain FROM schedule ORDER BY match_id").fetchall()
    s3v = {r[0]: r[1] for r in s3c.execute("SELECT match_id, winner FROM verdicts")}
    s3c.close()
    ck = connect_ro(CHECKER_DB)
    mt = dict(ck.execute("SELECT key, value FROM %s" % CHECKER_META))
    if mt.get("script") != CHECKER_SCRIPT or mt.get("union_pool") != POOL_ID:
        raise SystemExit("[CHECKER] provenance mismatch: script=%r union_pool=%r" % (mt.get("script"), mt.get("union_pool")))
    key = {(q, m): (None if k is None else int(k), int(nt or 0))
           for q, m, k, nt in ck.execute("SELECT question_id, model_name, is_correct, non_terminated FROM %s" % CHECKER_TABLE)}
    ck.close()
    qids = sorted({r[1] for r in sched})
    co = connect_ro(CORPUS_DB)
    text, target, out = {}, {}, {}
    for i in range(0, len(qids), 500):
        chunk = qids[i:i + 500]
        marks = ",".join("?" * len(chunk))
        for q, t, tg, srcname in co.execute("SELECT question_id, text, target, source FROM corpus_questions WHERE question_id IN (%s)" % marks, chunk):
            if srcname != "MATH":
                raise SystemExit("[SOURCE] question %d is %s, not MATH" % (q, srcname))
            text[q], target[q] = t, tg
        for q, m, o in co.execute("SELECT question_id, model_name, model_output FROM eval_results WHERE question_id IN (%s)" % marks, chunk):
            if (q, m) in out and out[(q, m)] != (o or ""):
                raise SystemExit("[SOURCE] two different eval outputs for (%d, %s)" % (q, m))
            out[(q, m)] = o or ""
    co.close()
    return dict(meta=meta, sched=sched, s3v=s3v, key=key, text=text, target=target, out=out)


def select_pairs(src, pool_eval_ids):
    """The registered selection, deterministic. Returns (pairs, facts)."""
    facts = Counter()
    elig = []
    for mid, qid, a, b, dom in src["sched"]:
        facts["schedule"] += 1
        if qid not in pool_eval_ids:
            raise SystemExit("[POOL] scheduled question %d is not an EVAL id of %s" % (qid, POOL_ID))
        ka, kb = src["key"].get((qid, a)), src["key"].get((qid, b))
        if ka is None or kb is None or ka[0] is None or kb[0] is None or ka[0] == kb[0]:
            continue
        facts["key_decidable"] += 1
        if ka[1] or kb[1]:
            raise SystemExit("[POPULATION] match %d: a non-terminated contestant in the cap-free schedule" % mid)
        c, w = (a, b) if ka[0] else (b, a)
        oc, ow = src["out"].get((qid, c)), src["out"].get((qid, w))
        if not oc or not ow or qid not in src["text"] or qid not in src["target"]:
            raise SystemExit("[POPULATION] match %d: a trace, text or target is missing" % mid)
        if len(oc) - len(ow) < THR:
            continue
        facts["thr"] += 1
        s, rule = answer_span_start(oc)
        if s <= 0:
            facts["excluded_no_cut"] += 1
            continue
        facts["rule:" + rule] += 1
        elig.append(dict(mid=mid, qid=qid, model_a=a, model_b=b, correct=c, wrong=w, side="A" if c == a else "B",
                         lc=len(oc), lw=len(ow), s=s, rule=rule, sha_c=sha16(oc), sha_w=sha16(ow),
                         sha_q=sha16(src["text"][qid] + "\x1f" + src["target"][qid]), domain=dom))
    facts["eligible"] = len(elig)
    if len(elig) > N_PAIRS_MAX:
        rng = random.Random(SELECT_SEED)
        pick = sorted(rng.sample(range(len(elig)), N_PAIRS_MAX))
        elig = [elig[i] for i in pick]
        facts["subsample"] = 1
    facts["selected"] = len(elig)
    return elig, facts


def pairs_text(pairs, facts):
    """The EVIDENCE file's text (LF, no timestamp: a pure function of the inputs)."""
    L = ["# TRACE-TRUNCATION eligible pair list (%s)" % REGISTRATION,
         "# selection: STAGE3-MATH-CAPFREE schedule (stage3_math_grok_v2_capfree.db sha256 %s), key = checker_answers_v2.db "
         "(sha256 %s) math_checker_answers_v2.is_correct; a match is eligible iff its contestants differ on the key and the "
         "CORRECT trace (multicorpus_cache_v1.db eval_results.model_output) is longer by >= %d characters; excluded (declared): "
         "a correct trace whose final-answer span starts at 0 (nothing to truncate); subsample above %d pairs with "
         "random.Random(%d).sample, sorted by match id" % (S3_CACHE_SHA256, CHECKER_SHA256, THR, N_PAIRS_MAX, SELECT_SEED),
         "# span rule: answer_span_start (MAX_LEAD %d; last '\\boxed' line, else the last non-empty line; sentence cut on a long lead)" % MAX_LEAD,
         "# counts: schedule %d | key-decidable %d | THR-eligible %d | excluded no-cut %d | eligible %d | selected %d | subsample %s | span rules %s"
         % (facts["schedule"], facts["key_decidable"], facts["thr"], facts["excluded_no_cut"], facts["eligible"], facts["selected"],
            "seed %d" % SELECT_SEED if facts.get("subsample") else "none",
            json.dumps({k[5:]: v for k, v in sorted(facts.items()) if k.startswith("rule:")}, sort_keys=True)),
         "# columns: match_id qid model_a model_b correct_model wrong_model correct_side len_correct len_wrong span_start span_rule "
         "sha16_correct_output sha16_wrong_output sha16_question_target"]
    for p in pairs:
        L.append("\t".join(str(x) for x in (p["mid"], p["qid"], p["model_a"], p["model_b"], p["correct"], p["wrong"], p["side"],
                                             p["lc"], p["lw"], p["s"], p["rule"], p["sha_c"], p["sha_w"], p["sha_q"])))
    return "\n".join(L) + "\n"


def evidence_state(text):
    """(ok, line) for C0 (a): the regenerated list == the committed evidence (LF) == the pin."""
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if not os.path.exists(EVIDENCE):
        return False, "[EVIDENCE] %s MISSING | regenerated list sha256-lf %s | pin %s" % (rel(EVIDENCE), sha, PINNED_PAIRS_SHA256)
    ev = open(EVIDENCE, "rb").read().replace(b"\r\n", b"\n")
    ev_sha = hashlib.sha256(ev).hexdigest()
    tracked, clean = git_tracked_clean(EVIDENCE)
    ok = bool(ev == text.encode("utf-8") and PINNED_PAIRS_SHA256 is not None and ev_sha == PINNED_PAIRS_SHA256 and tracked and clean)
    return ok, ("[EVIDENCE] %s sha256-lf %s (blob:%s; git tracked %s, clean %s) | regenerated %s | pin %s -> %s"
                % (rel(EVIDENCE), ev_sha, git_blob_id(ev), tracked, clean, sha, PINNED_PAIRS_SHA256, "MATCH" if ok else "NO MATCH"))


def git_tracked_clean(path):
    import subprocess
    try:
        t = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        return t, c
    except Exception:
        return False, False


def population(check_payloads=True):
    """Everything --dry-run, a launch and --analyze share: pool, sources, the pair list, the evidence state, the payload
    checks. Returns (pairs, src, facts, text, ev_ok, ev_line, scan)."""
    src = load_sources()
    pairs, facts = select_pairs(src, pool_guard.eval_ids(POOL_ID))
    text = pairs_text(pairs, facts)
    ev_ok, ev_line = evidence_state(text)
    names = sorted({p[k] for p in pairs for k in ("model_a", "model_b")})
    scan = Counter()
    if check_payloads:
        for p in pairs:
            _got, f = check_pair_payloads(p, src, names)
            scan.update(f)
    return pairs, src, facts, text, ev_ok, ev_line, scan


def jobs_of(pairs):
    """The posting order: pairs in list order, arms original -> truncate -> pad (fixed)."""
    return [(p, arm) for p in pairs for arm in ARMS]


def order_sha(jobs):
    return sha16(",".join("%d:%s" % (p["mid"], a) for p, a in jobs))


# ----------------------------------------------------------------------------------------------------------------------
# the gate and the budget
# ----------------------------------------------------------------------------------------------------------------------
VERDICT_RE = re.compile(r"^\s*#{0,6}\s*\**\s*(NOT READY|READY-WITH-CONDITIONS|READY)\b\s*\**\s*:", re.M)


def parse_ready(text, sha):
    body, fence = [], None
    for ln in text.split("\n"):
        st = ln.lstrip()
        if fence is None and (st.startswith("```") or st.startswith("~~~")):
            fence = st[:3]
            body.append("")
        elif fence is not None:
            if st.startswith(fence):
                fence = None
            body.append("")
        else:
            body.append(ln)
    text = "\n".join(body)
    lines = list(VERDICT_RE.finditer(text))
    if not lines:
        return None, ["no verdict line"]
    verdict = lines[0].group(1)
    first = text[lines[0].start():].split("\n", 1)[0]
    reasons = []
    if verdict == "NOT READY" or any(m.group(1) == "NOT READY" for m in lines):
        reasons.append("a NOT READY verdict")
    if TEST not in first:
        reasons.append("the verdict line does not name %s" % TEST)
    if sha not in first:
        reasons.append("the verdict line does not name this script's LF sha16 %s" % sha)
    return verdict, reasons


def gate_state(go):
    exists = os.path.exists(READY)
    tracked, clean = git_tracked_clean(READY) if exists else (False, False)
    verdict, reasons = parse_ready(open(READY, encoding="utf-8").read(), script_sha_lf()) if exists else (None, ["READY missing"])
    ok = bool(go and exists and tracked and clean and not reasons and PINNED_PAIRS_SHA256 is not None)
    return ok, ("--go %s | %s %s (tracked %s, clean %s) | verdict %r%s | pair-list pin %s"
                % (bool(go), rel(READY), "exists" if exists else "MISSING", tracked, clean, verdict,
                   "" if not reasons else " | REFUSES: " + "; ".join(reasons), PINNED_PAIRS_SHA256 or "UNSET"))


def go_gate(what, go):
    ok, s = gate_state(go)
    print("[GATE] %s: %s -> %s" % (what, s, "OPEN" if ok else "REFUSED"), flush=True)
    if not ok:
        raise SystemExit("[GATE] %s REFUSED (0 calls, no database opened): %s" % (what, s))


def acct_caches():
    c = atl.default_caches(DATA_ROOT)
    c["TRACE-TRUNCATION"] = [CACHE]
    c["CANARY-EPOCH2-RUNG"] = list(CANARY_CACHES)
    return c


def budget_gate(planned, what, refuse=True):
    """b0b5d0d: (i) own ceiling, (ii) the 4,000-match rule, (iii) 4,060 + both tests + this launch <= 14,000; printed on both
    branches, REFUSED (never trimmed) on any breach."""
    return atl.guard(TEST, planned, acct_caches(), LEDGER_DIR, what, refuse=refuse)


def ledger_append(calls, what):
    atl.append(TEST, what, calls, LEDGER_DIR)


# ----------------------------------------------------------------------------------------------------------------------
# the cache
# ----------------------------------------------------------------------------------------------------------------------
COLS = ("match_id", "arm", "qid", "model_a", "model_b", "correct_model", "wrong_model", "vote1", "vote2", "conf1", "conf2",
        "winner", "flip", "invalid", "raw1", "raw2", "finish1", "finish2", "ctok1", "ctok2", "provider1", "provider2",
        "resp_id1", "resp_id2", "system_sha16", "user1_sha16", "user2_sha16", "user1", "user2", "len_correct_slot",
        "len_wrong_slot", "span_start", "post_index", "script_sha16_lf", "ts")


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER NOT NULL, arm TEXT NOT NULL, qid INTEGER, model_a TEXT, "
                "model_b TEXT, correct_model TEXT, wrong_model TEXT, vote1 TEXT, vote2 TEXT, conf1 REAL, conf2 REAL, winner TEXT, "
                "flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, "
                "provider1 TEXT, provider2 TEXT, resp_id1 TEXT, resp_id2 TEXT, system_sha16 TEXT, user1_sha16 TEXT, "
                "user2_sha16 TEXT, user1 TEXT, user2 TEXT, len_correct_slot INTEGER, len_wrong_slot INTEGER, span_start INTEGER, "
                "post_index INTEGER, script_sha16_lf TEXT, ts REAL, PRIMARY KEY (match_id, arm))")
    con.execute("CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit()
    return con


def current_meta(pairs_sha):
    return dict(test=TEST, registration=REGISTRATION, pool_id=POOL_ID, judge=JUDGE, protocol=protocol(), max_tokens=str(MAXTOK),
                temperature=temp_label(), arms="|".join(ARMS), pad_unit=repr(PAD_UNIT), thr=str(THR), max_lead=str(MAX_LEAD),
                pairs_sha256_lf=pairs_sha, system_sha16=PINNED_SYSTEM_SHA16, script_sha16_lf=script_sha_lf())


def pin_meta(con, meta):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    old = dict(con.execute("SELECT key, value FROM run_meta"))
    if old:
        bad = [(k, old.get(k), v) for k, v in meta.items() if old.get(k) != v]
        if bad:
            raise SystemExit("[META] refusing to resume into %s: the cache was produced under a different record\n  %s"
                             % (rel(CACHE), "\n  ".join("%s: recorded %r | now %r" % b for b in bad)))
        con.execute("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)", (json.dumps(json.loads(old.get("resumed") or "[]") + [now]),))
    else:
        for k, v in meta.items():
            con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v))
        con.execute("INSERT INTO run_meta VALUES ('started', ?)", (now,))
    con.commit()


def unusable(r):
    return bool(r["invalid"] or r["finish1"] in ("length", "content_filter") or r["finish2"] in ("length", "content_filter"))


def cached_rows(path=None):
    p = path or CACHE
    if not os.path.exists(p):
        return {}, {}
    con = connect_ro(p)
    cols = [c for c in COLS]
    rows = {}
    for r in con.execute("SELECT %s FROM verdicts" % ", ".join(cols)):
        d = dict(zip(cols, r))
        rows[(d["match_id"], d["arm"])] = d
    meta = dict(con.execute("SELECT key, value FROM run_meta"))
    con.close()
    return rows, meta


# ----------------------------------------------------------------------------------------------------------------------
# posting
# ----------------------------------------------------------------------------------------------------------------------
class FingerprintMismatch(Exception):
    pass


def check_fingerprint(tag, provider, finish):
    if provider == EXPECTED_FINGERPRINT:
        return
    if provider == REFUSAL_FINGERPRINT and finish == "content_filter":
        return
    raise FingerprintMismatch("%s: fingerprint %r != %r (finish %r)" % (tag, provider, EXPECTED_FINGERPRINT, finish))


def one_job(job):
    p, arm, idx, system, u1, u2, meta, halt, mismatch = job
    tag = "match %d arm %s" % (p["mid"], arm)
    out = []
    for order, u in ((1, u1), (2, u2)):
        if halt.is_set():
            raise FingerprintMismatch("%s order %d: not posted, the run is stopping" % (tag, order))
        raw, prov, ctok, _lat, fin, msg = rr.call_judge_full(system, u)
        try:
            check_fingerprint("%s order %d" % (tag, order), prov, fin)
        except FingerprintMismatch as e:
            mismatch.append(str(e))
            halt.set()
            raise
        out.append((raw, prov, ctok, fin, (msg or {}).get("_response_id")))
    (raw1, p1, k1, f1, id1), (raw2, p2, k2, f2, id2) = out
    raw1, raw2 = rr.strip_think(raw1 or ""), rr.strip_think(raw2 or "")
    v1, c1 = rj.parse_judge(raw1)
    v2, c2 = rj.parse_judge(raw2)
    if f1 in ("length", "content_filter"):
        v1 = "INVALID"
    if f2 in ("length", "content_filter"):
        v2 = "INVALID"
    w, flip, inv = rj.combine_orders(v1, v2)
    winner = {"Model A": p["model_a"], "Model B": p["model_b"]}.get(w, w)
    cs = meta["off1"][meta["cslot1"]]
    ws = meta["off1"]["B" if meta["cslot1"] == "A" else "A"]
    return (p["mid"], arm, p["qid"], p["model_a"], p["model_b"], p["correct"], p["wrong"], v1, v2, c1, c2, winner, int(flip),
            int(inv), raw1, raw2, f1, f2, k1, k2, p1, p2, id1, id2, sha16(system), sha16(u1), sha16(u2), u1, u2,
            cs[1] - cs[0], ws[1] - ws[0], p["s"], idx, script_sha_lf(), time.time())


def guard_report(rows, keys, label, uncached_errors=0):
    sub = [rows[k] for k in keys if k in rows]
    n = len(sub) + uncached_errors
    bad = sum(1 for r in sub if unusable(r)) + uncached_errors
    rate = bad / max(1, n)
    fr = Counter(f for r in sub for f in (r["finish1"], r["finish2"]))
    fp = Counter(p for r in sub for p in (r["provider1"], r["provider2"]))
    print("[GUARD] %s: %d row(s) (cached %d + %d errored, counted unusable) | unusable %d (%.1f%%) | finish %s | fingerprints %s -> %s"
          % (label, n, len(sub), uncached_errors, bad, 100 * rate, dict(fr), dict(fp),
             "OK" if rate <= GUARD_RATE else "ABOVE 5%: REFUSE to post more"), flush=True)
    return n, bad, rate


def launch(pilot=None, workers=8, go=False):
    what = "--pilot %d" % pilot if pilot else "--run"
    go_gate(what, go)                                        # before any database is opened
    install_db_guard()
    pool_guard.assert_pool_of_record(POOL_ID)
    print("[POOL] %s verified by pool_guard.assert_pool_of_record" % POOL_ID, flush=True)
    assert_registration()
    configure_rr()
    assert_payload_source()
    rr.load_env()
    pairs, src, facts, text, ev_ok, ev_line, scan = population(check_payloads=True)
    print(ev_line, flush=True)
    if not ev_ok:
        raise SystemExit("[EVIDENCE] REFUSED: the eligible list is not the committed, pinned evidence (C0 (a)); nothing is posted.")
    print("[SCAN] pre-call: %d payloads | identity outside the span %d | reference intact %d | frame clean %d | reported, not refused: "
          "names inside trace slots %d, checker tokens / verdict words in the question slot %d / %d -> PASS"
          % (scan["payloads"], scan["identity_outside_span"], scan["reference_intact"], scan["frame_clean"], scan["name_in_trace"],
             scan["token_in_question"], scan["word_in_question"]), flush=True)
    return post(pairs, src, pilot, workers, what)


def post(pairs, src, pilot, workers, what):
    """The posting core (separated so the selftest drives it through the injected fake poster)."""
    alljobs = jobs_of(pairs)
    if pilot is not None:
        if pilot % len(ARMS) or pilot <= 0 or pilot > len(alljobs):
            raise SystemExit("[PILOT] --pilot N must be a positive multiple of %d (whole pairs in all arms), <= %d" % (len(ARMS), len(alljobs)))
        work = alljobs[:pilot]
    else:
        work = alljobs
    pilot_keys = [(p["mid"], a) for p, a in alljobs[:PILOT_MATCHES]]
    con = open_cache()
    pin_meta(con, current_meta(PINNED_PAIRS_SHA256 or "UNSET"))   # a launch has already verified list == evidence == pin
    rows, _m = cached_rows()
    if pilot is None:
        missing = [k for k in pilot_keys if k not in rows]
        if missing:
            raise SystemExit("[RUN] REFUSED: the pilot's %d matches are not all cached (%d missing); run --pilot %d first"
                             % (len(pilot_keys), len(missing), PILOT_MATCHES))
    if rows:
        n, bad, rate = guard_report(rows, list(rows), "before this launch")
        if rate > GUARD_RATE:
            raise SystemExit("[GUARD] REFUSED: %.1f%% of cached rows are unusable (> 5%%); the run is not authorised" % (100 * rate))
    names = sorted({p[k] for p in pairs for k in ("model_a", "model_b")})
    todo = []
    halt, mismatch = threading.Event(), []
    checked = {}
    for idx, (p, arm) in enumerate(work):
        if (p["mid"], arm) in rows:
            continue
        if p["mid"] not in checked:                          # the identity asserts and the pre-call scan, per pair, all arms
            checked[p["mid"]] = check_pair_payloads(p, src, names)[0]
        system, u1, u2, meta = checked[p["mid"]][arm]
        todo.append((p, arm, idx, system, u1, u2, meta, halt, mismatch))
    planned = 2 * len(todo)
    budget_gate(planned, what)
    print("[POST] %s | %d job(s) = %d calls | posting order sha16 %s (pairs in list order; arms %s; order 1 then 2) | workers %d | "
          "cap %d | temperature %s" % (what, len(todo), planned, order_sha(work), " -> ".join(ARMS), workers, MAXTOK, temp_label()), flush=True)
    posted = []
    real = rr.call_judge_full

    def counted(*a, **k):
        posted.append(1)
        return real(*a, **k)
    rr.call_judge_full = counted
    ok = err = 0
    try:
        if todo:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futs = {ex.submit(one_job, j): j for j in todo}
                for f in as_completed(futs):
                    try:
                        row = f.result()
                    except FingerprintMismatch as e:
                        halt.set()
                        ex.shutdown(wait=False, cancel_futures=True)
                        raise SystemExit("[FINGERPRINT] %s: the run STOPS; nothing cached for that row." % (mismatch[0] if mismatch else e))
                    except Exception as e:  # noqa: BLE001
                        err += 1
                        print("  ERROR match %d arm %s: %s" % (futs[f][0]["mid"], futs[f][1], str(e)[:140]), flush=True)
                        continue
                    con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * len(COLS)), row)
                    con.commit()
                    ok += 1
    finally:
        rr.call_judge_full = real
        ledger_append(len(posted), what)
        print("[POST] %s: %d calls posted (cached ok %d, errors %d - errors are posted calls, counted, never cached)"
              % (what, len(posted), ok, err), flush=True)
    rows, _m = cached_rows()
    n, bad, rate = guard_report(rows, pilot_keys if pilot else list(rows), "after this launch", uncached_errors=err)
    if pilot and rate > GUARD_RATE:
        raise SystemExit("[GUARD] the pilot FAILED its truncation guard (%.1f%% > 5%%): the run is REFUSED" % (100 * rate))
    return 0


# ----------------------------------------------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------------------------------------------
def boot_se(byq, B, seed):
    """Question-clustered bootstrap: byq = {qid: [values]}; returns the SE of the mean over resampled questions."""
    qs = sorted(byq)
    if not qs:
        return float("nan")
    S = [sum(byq[q]) for q in qs]
    N = [len(byq[q]) for q in qs]
    rng = random.Random(seed)
    k = len(qs)
    vals = []
    for _ in range(B):
        s = n = 0
        for _j in range(k):
            i = rng.randrange(k)
            s += S[i]
            n += N[i]
        vals.append(s / n)
    m = sum(vals) / B
    return (sum((v - m) ** 2 for v in vals) / (B - 1)) ** 0.5


def interval(point, se):
    return point - Z * se, point + Z * se


def kish(byq):
    sizes = [len(v) for v in byq.values()]
    return sum(s * s for s in sizes) / max(1, sum(sizes))


def c1_verdict(lo, hi):
    if hi < C1_BAR:
        return "HELD"
    if lo > C1_BAR:
        return "FAILED"
    return "UND"


def c2_verdict(lo, hi):
    if hi < C2_BAR:
        return "FAILED"
    if lo > C2_BAR:
        return "HELD"
    return "UND"


def compute(pairs, rows, B=BOOT, seeds=(BOOT_SEED,) + EXTRA_SEEDS):
    """Per-pair indicators under convention A (DECIDES) and B (beside), the paired statistics and their supports."""
    ind = {}
    for p in pairs:
        r = {a: rows.get((p["mid"], a)) for a in ARMS}
        if any(v is None for v in r.values()):
            continue
        ind[p["mid"]] = dict(qid=p["qid"], A={a: int(r[a]["winner"] == p["correct"]) for a in ARMS},
                             committed={a: r[a]["winner"] in (p["model_a"], p["model_b"]) for a in ARMS})
    n = len(ind)
    s = dict(n=n, n_pairs=len(pairs))
    if n == 0:
        return s
    byq = lambda f: _byq(ind, f)
    acc = {a: sum(v["A"][a] for v in ind.values()) / n for a in ARMS}
    accB = {}
    for a in ARMS:
        cm = [v for v in ind.values() if v["committed"][a]]
        accB[a] = (sum(v["A"][a] for v in cm) / len(cm), len(cm)) if cm else (float("nan"), 0)
    drop = acc["original"] - acc["truncate"]
    padd = acc["pad"] - acc["original"]
    se = {}
    reads = []
    for i, sd in enumerate(seeds):
        se_drop = boot_se(byq(lambda v: v["A"]["original"] - v["A"]["truncate"]), B, sd)
        se_t = boot_se(byq(lambda v: v["A"]["truncate"]), B, sd)
        if i == 0:
            se = dict(drop=se_drop, trunc=se_t,
                      pad=boot_se(byq(lambda v: v["A"]["pad"] - v["A"]["original"]), B, sd),
                      orig=boot_se(byq(lambda v: v["A"]["original"]), B, sd),
                      padacc=boot_se(byq(lambda v: v["A"]["pad"]), B, sd))
        reads.append((sd, c1_verdict(*interval(drop, se_drop)), c2_verdict(*interval(acc["truncate"], se_t)), se_drop, se_t))
    bq = byq(lambda v: 1)
    b = sum(1 for v in ind.values() if v["A"]["original"] and not v["A"]["truncate"])
    c = sum(1 for v in ind.values() if v["A"]["truncate"] and not v["A"]["original"])
    disc = (b + c) / n
    iid_drop = (max(0.0, disc - drop ** 2) / n) ** 0.5
    iid_t = (acc["truncate"] * (1 - acc["truncate"]) / n) ** 0.5
    s.update(acc=acc, accB=accB, drop=drop, padd=padd, se=se, reads=reads, b=b, c=c, disc=disc, n_q=len(bq), kish=kish(bq),
             iid_drop=iid_drop, iid_t=iid_t,
             deff_drop=(se["drop"] / iid_drop) ** 2 if iid_drop > 0 else float("nan"),
             deff_t=(se["trunc"] / iid_t) ** 2 if iid_t > 0 else float("nan"))
    return s


def _byq(ind, f):
    d = defaultdict(list)
    for v in ind.values():
        d[v["qid"]].append(f(v))
    return d


def rung_floor():
    """CANARY-EPOCH2-RUNG's within-session floor d43, if its outcome of record exists (read, never written)."""
    if not os.path.exists(RUNG_OUT):
        return None
    m = re.search(r"^RUNG d43 = ([0-9.]+)", open(RUNG_OUT, encoding="utf-8").read(), re.M)
    return float(m.group(1)) if m else None


# ----------------------------------------------------------------------------------------------------------------------
# the readout (pure function of the computed statistics; every branch registers its tag)
# ----------------------------------------------------------------------------------------------------------------------
def readout(s, c0, unusable_calls, posted_calls, rung=None, drift=None):
    L = []
    p = L.append
    p("=== %s | %s ===" % (TEST, REGISTRATION))
    p("  judge %s | cap %d | temperature %s | pool %s | arms %s | THR %d | pad unit %r | script sha256-lf16 %s"
      % (JUDGE, MAXTOK, temp_label(), POOL_ID, " / ".join(ARMS), THR, PAD_UNIT, script_sha_lf()))
    p("")
    p("(C0) VALIDITY, FIRST (pre-emptive):")
    for lab, ok, detail in c0:
        p("     %-58s %s  %s" % (lab, "PASS" if ok else "FAIL", detail))
    valid = all(ok for _l, ok, _d in c0)
    hit("C0:PASS" if valid else "C0:FAIL")
    p("     C0: %s" % ("PASS" if valid else "FAILED - C1 and C2 are UNDETERMINED BY VALIDITY and the falsifier is NOT evaluated"))
    n = s.get("n", 0)
    p("")
    p("DENOMINATOR: %d pairs judged in all three arms (of %d eligible), clustered by MATH question (%d questions, Kish mean "
      "cluster size %.3f). acc = the share of pairs whose dual-order combined verdict names the checker-correct side."
      % (n, s.get("n_pairs", 0), s.get("n_q", 0), s.get("kish", float("nan"))))
    if n == 0:
        p("  no pair is complete in all three arms; nothing is read.")
        hit("SUPPORT:DEGENERATE")
        return "\n".join(L) + "\n", dict(valid=valid)
    acc, se = s["acc"], s["se"]
    for a in ARMS:
        lo, hi = interval(acc[a], se["orig"] if a == "original" else se["trunc"] if a == "truncate" else se["padacc"])
        p("  %-9s convention A %.3f [%.3f, %.3f] | convention B (committed only) %.3f (n=%d)" % (a, acc[a], lo, hi, s["accB"][a][0], s["accB"][a][1]))
    p("")
    lo1, hi1 = interval(s["drop"], se["drop"])
    p("(C1) THE OUTCOME-JUDGE TEST: drop = acc(original) - acc(truncate) = %.3f, 95%% interval [%.3f, %.3f] (SE %.4f, "
      "question-clustered bootstrap B %d, seed %d); bar %.2f; discordant pairs original-only %d / truncate-only %d"
      % (s["drop"], lo1, hi1, se["drop"], BOOT, BOOT_SEED, C1_BAR, s["b"], s["c"]))
    if not valid:
        v1 = "UND_VALIDITY"
        p("     C1: UNDETERMINED BY VALIDITY (C0 failed); the interval is printed and NOT scored")
    else:
        v1 = c1_verdict(lo1, hi1)
        p("     C1: %s" % {"HELD": "HELD - the interval lies wholly BELOW 0.10: an outcome judge under this reference",
                           "FAILED": "FAILED - the interval lies wholly ABOVE 0.10: not an outcome judge under this reference",
                           "UND": "UNDETERMINED - the interval contains 0.10 (DESCRIPTIVE-ONLY by the registered support)"}[v1])
    hit("C1:" + v1)
    lo2, hi2 = interval(acc["truncate"], se["trunc"])
    p("(C2) THE FLOOR: acc(truncate) = %.3f, 95%% interval [%.3f, %.3f] (SE %.4f); bar %.2f" % (acc["truncate"], lo2, hi2, se["trunc"], C2_BAR))
    if not valid:
        v2 = "UND_VALIDITY"
        p("     C2: UNDETERMINED BY VALIDITY (C0 failed); the interval is printed and NOT scored")
    else:
        v2 = c2_verdict(lo2, hi2)
        p("     C2: %s" % {"HELD": "HELD - the interval lies wholly ABOVE 0.70",
                           "FAILED": "FAILED - the interval lies wholly BELOW 0.70",
                           "UND": "UNDETERMINED - the interval contains 0.70"}[v2])
    hit("C2:" + v2)
    changes = sum(1 for sd, a1, a2, _x, _y in s["reads"][1:] if a1 != s["reads"][0][1] or a2 != s["reads"][0][2])
    p("     robustness: C1 / C2 re-read at the 20 further bootstrap seeds %d-%d: %d of 20 change a verdict (%s)"
      % (EXTRA_SEEDS[0], EXTRA_SEEDS[-1], changes, ", ".join("%d:%s/%s" % (sd, a1, a2) for sd, a1, a2, _x, _y in s["reads"][1:])))
    lo3, hi3 = interval(s["padd"], se["pad"])
    qual = (lo3 > 0 or hi3 < 0) and abs(s["padd"]) > C3_EPS
    p("(C3) THE PAD CONTROL, DESCRIPTIVE: acc(pad) - acc(original) = %+.3f [%+.3f, %+.3f] (SE %.4f) -> %s"
      % (s["padd"], lo3, hi3, se["pad"], "C1's reading is QUALIFIED as edit-sensitivity, not content-reading (interval excludes 0 and |point| > 0.05)"
         if qual else "no qualification (the interval contains 0 or |point| <= 0.05)"))
    hit("C3:QUALIFIED" if qual else "C3:NOT_QUALIFIED")
    p("     RECORDED LIMIT (b0b5d0d, choice 2): the pad arm restores BYTE (character) length with ASCII spaces, NOT necessarily TOKEN "
      "length (a tokenizer may collapse runs of spaces); C3 is DESCRIPTIVE and is read as such.")
    p("(C4) THE NOISE-FLOOR READING, DESCRIPTIVE: drop %.3f beside the PER-MATCH retest floors of record:" % s["drop"])
    floors = list(FLOORS)
    if rung is not None:
        floors.append(("CANARY-EPOCH2-RUNG within-session d43 (its outcome of record)", rung))
        hit("C4:RUNG_READ")
    else:
        p("     CANARY-EPOCH2-RUNG's within-session floor: not recorded before this outcome (%s absent or unreadable)" % rel(RUNG_OUT))
        hit("C4:RUNG_ABSENT")
    for lab, f in floors:
        p("     %-72s %.3f -> the drop is %s" % (lab, f, "BELOW this floor: not attributed to truncation" if s["drop"] < f else "at or above this floor"))
    below = any(s["drop"] < f for _l, f in floors)
    hit("C4:BELOW_FLOOR" if below else "C4:ABOVE_FLOOR")
    p("     NO floor is derived from a pooled per-call rate (TIE-MECHANICS, L14415: the 0.098 / 0.057 per-call rates do not give a "
      "match-level floor by independence arithmetic).")
    p("")
    p("SUPPORT (measured beside registered). REGISTERED (planning): n %d, Kish %.3f (POSITION-INDEX-ALL MATH / grok-nr, transported), "
      "DEFF %.2f transported, n_eff %d, declared pilot discordance %.2f, SE C1 %.4f / C2 %.4f, MDE (2.80 x SE) C1 %.3f / C2 %.3f; "
      "C1 DESCRIPTIVE-ONLY (0.03 < 0.060), C2 SCOREABLE (0.17 > 0.054); structural: a finite population, C1 descriptive at any budget."
      % (REG_SUPPORT["n"], REG_SUPPORT["kish"], REG_SUPPORT["deff"], REG_SUPPORT["neff"], REG_SUPPORT["disc"], REG_SUPPORT["se_c1"],
         REG_SUPPORT["se_c2"], REG_SUPPORT["mde_c1"], REG_SUPPORT["mde_c2"]))
    degenerate = not (s["iid_drop"] > 0 and s["iid_t"] > 0)
    hit("SUPPORT:DEGENERATE" if degenerate else "SUPPORT:OK")
    p("  MEASURED: n %d pairs over %d questions, Kish %.3f | discordance (b + c) / n = %.3f | C1: SE_boot %.4f, SE_iid (match-level "
      "paired) %.4f, DEFF %.2f, n_eff %.1f, MDE %.3f | C2: SE_boot %.4f, SE_iid %.4f, DEFF %.2f, n_eff %.1f, MDE %.3f%s"
      % (n, s["n_q"], s["kish"], s["disc"], se["drop"], s["iid_drop"], s["deff_drop"], n / s["deff_drop"] if s["deff_drop"] == s["deff_drop"] and s["deff_drop"] > 0 else float("nan"),
         2.80 * se["drop"], se["trunc"], s["iid_t"], s["deff_t"], n / s["deff_t"] if s["deff_t"] == s["deff_t"] and s["deff_t"] > 0 else float("nan"),
         2.80 * se["trunc"], " (DEGENERATE: a zero iid variance, DEFF undefined)" if degenerate else ""))
    p("")
    p("PREDICTIONS (registered; scored on the convention-A point):")
    preds = [("P1", "acc(original) 0.95 [0.90, 0.98]", 0.90 <= acc["original"] <= 0.98, "%.3f" % acc["original"]),
             ("P2", "acc(truncate) 0.87 [0.80, 0.93]", 0.80 <= acc["truncate"] <= 0.93, "%.3f" % acc["truncate"]),
             ("P3", "drop 0.07 [0.02, 0.12]", 0.02 <= s["drop"] <= 0.12, "%.3f" % s["drop"]),
             ("P4", "acc(pad) - acc(original) 0.00 [-0.03, +0.03]", -0.03 <= s["padd"] <= 0.03, "%+.3f" % s["padd"]),
             ("P5", "C1 reads UNDETERMINED", v1 == "UND", v1),
             ("P6", "unusable <= 1% of the posted calls", unusable_calls <= 0.01 * max(1, posted_calls), "%d / %d" % (unusable_calls, posted_calls))]
    for pid, text, held, val in preds:
        tag = "HELD" if bool(held) else "FAILED"
        hit("%s:%s" % (pid, tag))
        p("  %s %-48s %-12s -> %s" % (pid, text, val, tag))
    p("")
    if not valid:
        hit("FALS:NOT_EVALUATED")
        p("FALSIFIER: NOT EVALUATED (C0 failed).")
    elif v2 == "FAILED":
        hit("FALS:C2_FIRES")
        p("FALSIFIER FIRES (C2 FAILED): \"no trajectory pair with equal outcomes is judgeable without a length control\" - even an "
          "exact outcome reference does not make the deployed judge an outcome judge; the leads' C4 reading (an exact reference "
          "disarms the causal-length vulnerability) is OVERTURNED.")
        if v1 == "FAILED":
            hit("FALS:C1_FIRES")
            p("FALSIFIER FIRES (C1 FAILED): 'outcome judge' is overturned for this judge under this reference.")
    elif v1 == "FAILED":
        hit("FALS:C1_FIRES")
        p("FALSIFIER FIRES (C1 FAILED): 'outcome judge' is overturned for this judge under this reference.")
    else:
        hit("FALS:NOT_FIRED")
        p("FALSIFIER: NOT FIRED (C2 %s, C1 %s).  NOT OVERTURNED in any branch: L1, L1-V, L1-V2, the STACK-v2 recipe of record, H7's closure." % (v2, v1))
    if drift is not None:
        p("")
        p("DRIFT (descriptive, never the comparator of record): the original arm's verdict equals STAGE3-MATH-CAPFREE's cached verdict "
          "on the same match (the same payload bytes) on %d of %d pairs = %.3f" % (drift[0], drift[1], drift[0] / max(1, drift[1])))
    p("")
    p("RANDOM STREAMS: selection deterministic (subsample seed %d only above %d pairs) | bootstrap B %d seed %d, plus seeds %d-%d | "
      "judge sampling not seedable (temperature omitted) | posting order fixed (pairs in list order, arms %s, order 1 then 2)."
      % (SELECT_SEED, N_PAIRS_MAX, BOOT, BOOT_SEED, EXTRA_SEEDS[0], EXTRA_SEEDS[-1], " -> ".join(ARMS)))
    return "\n".join(L) + "\n", dict(valid=valid, v1=v1, v2=v2)


def analyze(boot=BOOT):
    install_db_guard()
    pool_guard.assert_pool_of_record(POOL_ID)
    print("[POOL] %s verified by pool_guard.assert_pool_of_record" % POOL_ID, flush=True)
    if not os.path.exists(CACHE):
        raise SystemExit("[ANALYZE] %s does not exist: nothing has been posted." % rel(CACHE))
    configure_rr()
    pairs, src, facts, text, ev_ok, ev_line, scan = population(check_payloads=False)
    rows, meta = cached_rows()
    return analyze_core(pairs, src, rows, meta, ev_ok, ev_line, boot)


def analyze_core(pairs, src, rows, meta, ev_ok, ev_line, boot=BOOT):
    names = sorted({p[k] for p in pairs for k in ("model_a", "model_b")})
    posted_match = identity_ok = ref_ok = 0
    n_rows = 0
    for p in pairs:
        got = None
        for arm in ARMS:
            r = rows.get((p["mid"], arm))
            if r is None:
                continue
            n_rows += 1
            if got is None:
                got, f = check_pair_payloads(p, src, names)        # SystemExit on any identity / reference / leak failure
            sy, u1, u2, _m = got[arm]
            if r["user1"] == u1 and r["user2"] == u2 and r["system_sha16"] == sha16(sy):
                posted_match += 1
            identity_ok += 1
            ref_ok += 1
    complete = all((p["mid"], a) in rows for p in pairs for a in ARMS)
    pilot_keys = [(p["mid"], a) for p, a in jobs_of(pairs)[:PILOT_MATCHES]]
    pk = [rows[k] for k in pilot_keys if k in rows]
    pilot_rate = sum(1 for r in pk if unusable(r)) / max(1, len(pk))
    c0 = [("(a) eligible list = committed evidence = pin", ev_ok, ev_line),
          ("(b) posted bodies = re-assembly (identity outside span)", posted_match == n_rows and n_rows > 0,
           "%d of %d posted rows" % (posted_match, n_rows)),
          ("(c) reference block intact", ref_ok == n_rows and n_rows > 0, "%d of %d rows" % (ref_ok, n_rows)),
          ("(d) pilot truncation guard (<= 5% unusable)", len(pk) == PILOT_MATCHES and pilot_rate <= GUARD_RATE,
           "%d of %d pilot rows cached, unusable %.1f%%" % (len(pk), PILOT_MATCHES, 100 * pilot_rate)),
          ("(e) fingerprints", all(r["provider1"] in (EXPECTED_FINGERPRINT, REFUSAL_FINGERPRINT) and r["provider2"] in (EXPECTED_FINGERPRINT, REFUSAL_FINGERPRINT) for r in rows.values()),
           dict(Counter(pp for r in rows.values() for pp in (r["provider1"], r["provider2"]))))]
    s = compute(pairs, rows, B=boot)
    unusable_calls = sum(int(r["finish1"] in ("length", "content_filter") or r["vote1"] == "INVALID")
                         + int(r["finish2"] in ("length", "content_filter") or r["vote2"] == "INVALID") for r in rows.values())
    s3v = src.get("s3v", {})
    dr = [(rows[(p["mid"], "original")]["winner"] == s3v.get(p["mid"])) for p in pairs if (p["mid"], "original") in rows and p["mid"] in s3v]
    text, res = readout(s, c0, unusable_calls, 2 * len(rows), rung_floor(), (sum(dr), len(dr)) if dr else None)
    header = ("HEADER: %s | cache %s (%d rows, run_meta started %s, pinned script sha %s) | written %s\n"
              % (TEST, rel(CACHE), len(rows), meta.get("started"), meta.get("script_sha16_lf"), time.strftime("%Y-%m-%d %H:%M:%S")))
    text = text + atl.summary_line(TEST, acct_caches(), LEDGER_DIR) + "\n" + header
    print(text, flush=True)
    return write_outcome(text, complete, len(rows), 3 * len(pairs))


def write_outcome(text, complete, n_rows, n_want):
    if not complete:
        target = OUT_PILOT if n_rows <= PILOT_MATCHES else OUT_PARTIAL
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write("NOT OF RECORD - the cache holds %d of %d rows; no line below is a registered reading. The outcome of record is "
                    "written only from a complete cache, to %s.\n\n" % (n_rows, n_want, rel(OUT)) + text)
        print("[ANALYZE] partial cache (%d of %d rows): wrote %s; NO outcome of record." % (n_rows, n_want, rel(target)), flush=True)
        return 2
    try:
        with open(OUT, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        print("[ANALYZE] REFUSED: the outcome of record %s already exists and is WRITE-ONCE; nothing was overwritten." % rel(OUT), flush=True)
        return 3
    print("[ANALYZE] complete cache: wrote %s (write-once)" % rel(OUT), flush=True)
    return 0


# ----------------------------------------------------------------------------------------------------------------------
# dry run, emit, leakscan
# ----------------------------------------------------------------------------------------------------------------------
def dry_run(pilot=None):
    install_db_guard()
    pool_guard.assert_pool_of_record(POOL_ID)
    print("[POOL] %s verified by pool_guard.assert_pool_of_record" % POOL_ID, flush=True)
    assert_registration()
    configure_rr()
    assert_payload_source()
    pairs, src, facts, text, ev_ok, ev_line, scan = population(check_payloads=True)
    jobs = jobs_of(pairs)
    print("[POPULATION] schedule %d | key-decidable %d | THR-eligible %d | excluded no-cut %d | eligible %d | selected %d | "
          "subsample %s | span rules %s | questions %d"
          % (facts["schedule"], facts["key_decidable"], facts["thr"], facts["excluded_no_cut"], facts["eligible"], facts["selected"],
             "seed %d" % SELECT_SEED if facts.get("subsample") else "none",
             {k[5:]: v for k, v in facts.items() if k.startswith("rule:")}, len({p["qid"] for p in pairs})), flush=True)
    print("[LIST] regenerated sha256-lf %s (%d bytes)" % (hashlib.sha256(text.encode("utf-8")).hexdigest(), len(text.encode("utf-8"))), flush=True)
    print(ev_line, flush=True)
    print("[SCAN] pre-call full-payload scan: %d payloads (%d pairs x 3 arms x 2 orders) | identity outside the span %d | "
          "reference intact %d | frame clean (identical across arms and orders; no contestant name outside the traces; no checker token "
          "or verdict word in the template) %d | reported, not refused: names inside trace slots %d, checker tokens / verdict words in the "
          "question slot (dataset text) %d / %d -> PASS"
          % (scan["payloads"], len(pairs), scan["identity_outside_span"], scan["reference_intact"], scan["frame_clean"],
             scan["name_in_trace"], scan["token_in_question"], scan["word_in_question"]), flush=True)
    anchor = hashlib.sha256()
    for p, arm in jobs:
        sy, u1, u2, _m = assemble(p, arm, src)
        anchor.update(("%d|%s|" % (p["mid"], arm)).encode("utf-8") + sy.encode("utf-8") + u1.encode("utf-8") + u2.encode("utf-8"))
    print("[ANCHOR] system sha16 %s (pinned %s) | all-payload anchor sha16 %s over %d jobs | posting order sha16 %s"
          % (sha16(system_prompt()), PINNED_SYSTEM_SHA16, anchor.hexdigest()[:16], len(jobs), order_sha(jobs)), flush=True)
    n_calls = 2 * len(jobs)
    print("[COUNTS] %d pairs x %d arms x 2 orders = %d calls | pilot %d matches = %d calls INSIDE the count | ceiling %d"
          % (len(pairs), len(ARMS), n_calls, PILOT_MATCHES, 2 * PILOT_MATCHES, CALL_CEILING), flush=True)
    budget_gate(n_calls, "--dry-run (a full launch, 0 posted)", refuse=False)
    ok, gs = gate_state(False)
    print("[GATE] (a dry run is never gated) %s" % gs, flush=True)
    p0, a0 = jobs[0]
    sy, u1, u2, _m = assemble(p0, "truncate", src)
    print("[DRY-RUN] first pair: match %d qid %d | correct %s (side %s) vs wrong %s | len %d vs %d | span start %d (%s)"
          % (p0["mid"], p0["qid"], p0["correct"], p0["side"], p0["wrong"], p0["lc"], p0["lw"], p0["s"], p0["rule"]))
    print("----- TRUNCATE / ORDER 1 / USER -----")
    print(u1)
    print("----- END -----")
    print("[DRY-RUN] %d payloads assembled and scanned, 0 posted. %s" % (scan["payloads"], dbguard_line()), flush=True)
    return 0


def emit_pairs(path):
    install_db_guard()
    pool_guard.assert_pool_of_record(POOL_ID)
    print("[POOL] %s verified by pool_guard.assert_pool_of_record" % POOL_ID, flush=True)
    src = load_sources()
    pairs, facts = select_pairs(src, pool_guard.eval_ids(POOL_ID))
    text = pairs_text(pairs, facts)
    b = text.encode("utf-8")
    try:
        with open(path, "xb") as f:
            f.write(b)
    except FileExistsError:
        raise SystemExit("[EMIT] %s exists; the list is write-once. Nothing written." % path)
    print("[EMIT] %s | %d pairs | sha256-lf %s | sha256-lf16 %s | blob:%s | %d bytes (LF; the rendering of record)"
          % (path, len(pairs), hashlib.sha256(b).hexdigest(), hashlib.sha256(b).hexdigest()[:16], git_blob_id(b), len(b)), flush=True)
    print(dbguard_line(), flush=True)
    return 0


def leakscan():
    install_db_guard()
    rows, _m = cached_rows()
    if not rows:
        raise SystemExit("[LEAKSCAN] no posted rows in %s" % rel(CACHE))
    names = sorted({r[k] for r in rows.values() for k in ("model_a", "model_b")})
    hits = Counter()
    for r in rows.values():
        for u in (r["user1"], r["user2"]):
            for nm in names:
                if nm in u:
                    hits["name:" + nm] += 1
            for tok in LEAK_TOKENS:
                if tok.lower() in u.lower():
                    hits["token:" + tok] += 1
            for w in LEAK_WORDS:
                if re.search(r"\b%s\b" % w, u):
                    hits["word:" + w] += 1
    print("[LEAKSCAN] %d posted rows, %d user bodies scanned in FULL (question, reference, both traces, template) | hits %s "
          "(a hit inside a trace slot is the model's own output, proved equal to its source by --analyze's C0 (b); a hit in the "
          "frame is a leak)" % (len(rows), 2 * len(rows), dict(hits) or "none"), flush=True)
    return 0


# ----------------------------------------------------------------------------------------------------------------------
# the selftest (0 calls; synthetic DBs in a temp dir; the injected fake poster; a socket guard)
# ----------------------------------------------------------------------------------------------------------------------
def _fixture(tmp, n_q=24):
    """Synthetic stage3 cache, checker DB and corpus DB under tmp; returns the module path overrides."""
    roster = ["Alpha-7B", "Beta-13B", "Gamma-70B"]
    s3p, ckp, cop = os.path.join(tmp, "stage3_math_grok_v2_capfree.db"), os.path.join(tmp, "checker_answers_v2.db"), os.path.join(tmp, "multicorpus_cache_v1.db")
    c = _TRUE_CONNECT(s3p)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("CREATE TABLE schedule (match_id INTEGER PRIMARY KEY, source TEXT, qid INTEGER, model_a TEXT, model_b TEXT, filter_verdict TEXT, domain TEXT)")
    c.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, winner TEXT)")
    c.executemany("INSERT INTO meta VALUES (?,?)", [("pool_id", POOL_ID), ("judge", JUDGE), ("checker_table", "v2"), ("terminated_only", "1"),
                                                    ("temperature", "omitted (provider default)")])
    k = _TRUE_CONNECT(ckp)
    k.execute("CREATE TABLE %s (question_id INTEGER, model_name TEXT, is_correct INTEGER, non_terminated INTEGER)" % CHECKER_TABLE)
    k.execute("CREATE TABLE %s (key TEXT PRIMARY KEY, value TEXT)" % CHECKER_META)
    k.executemany("INSERT INTO %s VALUES (?,?)" % CHECKER_META, [("script", CHECKER_SCRIPT), ("union_pool", POOL_ID)])
    o = _TRUE_CONNECT(cop)
    o.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, text TEXT, target TEXT, source TEXT)")
    o.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, model_output TEXT)")
    mid = 70_000_000
    qids = []
    for i in range(n_q):
        q = 5000 + i
        qids.append(q)
        o.execute("INSERT INTO corpus_questions VALUES (?,?,?,?)", (q, "Compute $x$ for problem %d." % i, str(i + 2), "MATH"))
        long_ = ("Step: we expand the expression carefully and simplify. " * (8 + i % 5)) + "\nTherefore the answer is $\\boxed{%d}$." % (i + 2)
        short = "The answer is $\\boxed{%d}$." % (i + 3)
        mid_len = ("Some work. " * 3) + "\\boxed{%d}" % (i + 3)
        outs = {roster[0]: long_, roster[1]: short, roster[2]: mid_len}
        cor = {roster[0]: 1, roster[1]: 0, roster[2]: 0 if i % 4 else 1}
        for m in roster:
            o.execute("INSERT INTO eval_results VALUES (?,?,?)", (q, m, outs[m]))
            k.execute("INSERT INTO %s VALUES (?,?,?,?)" % CHECKER_TABLE, (q, m, cor[m], 0))
        for a, b in ((roster[0], roster[1]), (roster[2], roster[0]), (roster[1], roster[2])):
            c.execute("INSERT INTO schedule VALUES (?,?,?,?,?,?,?)", (mid, "MATH", q, a, b, "DISAGREE", "Algebra"))
            c.execute("INSERT INTO verdicts VALUES (?,?)", (mid, a))
            mid += 1
    for x in (c, k, o):
        x.commit()
        x.close()
    return dict(S3_CACHE=s3p, CHECKER_DB=ckp, CORPUS_DB=cop, qids=qids, roster=roster)


def _fake_poster(rule):
    """An INJECTED fake for rr.call_judge_full: returns a verdict JSON chosen by rule(user) -> 'Model A' / 'Model B' / 'TIE'
    / 'INVALID' / 'FP' (a foreign fingerprint). Never touches the network."""
    calls = []

    def fake(system, user, retries=6):
        calls.append(user)
        v = rule(user)
        if v == "FP":
            return ('{"winner": "Model A", "confidence": 0.9}', "azure:some-other-model", 12, 0.0, "stop", {"_response_id": "x"})
        if v == "INVALID":
            return ("no json here", EXPECTED_FINGERPRINT, 12, 0.0, "stop", {"_response_id": "r%d" % len(calls)})
        return ('{"winner": "%s", "confidence": 0.8}' % v, EXPECTED_FINGERPRINT, 12, 0.0, "stop", {"_response_id": "r%d" % len(calls)})
    return fake, calls


def selftest():
    global S3_CACHE, CHECKER_DB, CORPUS_DB, CACHE, OUT, OUT_PILOT, OUT_PARTIAL, LEDGER_DIR, CANARY_CACHES, EVIDENCE, RUNG_OUT, PINNED_PAIRS_SHA256, S3_CACHE_SHA256, CHECKER_SHA256
    fails = []

    def check(name, cond, detail=""):
        ok = bool(cond)
        print("  %-78s %s%s" % (name, "OK" if ok else "FAIL", "" if ok else "  " + str(detail)[:200]))
        if not ok:
            fails.append(name)

    print("[POOL] %s (selftest: synthetic fixtures; pool_guard's DB is NOT opened)" % POOL_ID)
    print("[SELFTEST] %s | script sha256-lf16 %s (working tree %s) | 0 calls | python -O: %s" % (TEST, script_sha_lf(), script_sha_raw(), not __debug__))
    saved = dict(S3_CACHE=S3_CACHE, CHECKER_DB=CHECKER_DB, CORPUS_DB=CORPUS_DB, CACHE=CACHE, OUT=OUT, OUT_PILOT=OUT_PILOT,
                 OUT_PARTIAL=OUT_PARTIAL, LEDGER_DIR=LEDGER_DIR, CANARY_CACHES=CANARY_CACHES, EVIDENCE=EVIDENCE, RUNG_OUT=RUNG_OUT,
                 PINNED_PAIRS_SHA256=PINNED_PAIRS_SHA256, S3_CACHE_SHA256=S3_CACHE_SHA256, CHECKER_SHA256=CHECKER_SHA256)
    saved_eval_ids, saved_db_path, saved_post = pool_guard.eval_ids, pool_guard.db_path, rr.call_judge_full
    saved_connect = socket.socket.connect
    tmp = tempfile.mkdtemp(prefix="trace_truncation_selftest_")

    def no_net(*a, **k):
        raise SystemExit("[SELFTEST] a network connection was attempted")
    socket.socket.connect = no_net
    try:
        # 0. the pure pieces ------------------------------------------------------------------------------------------
        assert_registration()
        check("the registration's phrases are in the programme", True)
        configure_rr()
        assert_payload_source()
        body = payload_body("S", "U")
        check("payload body == rr.payload_body; temperature OMITTED", body == rr.payload_body("S", "U") and "temperature" not in body)
        check("cap 8192, deployed judge", body["max_tokens"] == 8192 and body["model"] == JUDGE)
        check("system prompt sha16 == pin %s" % PINNED_SYSTEM_SHA16, sha16(system_prompt()) == PINNED_SYSTEM_SHA16)
        check("REF_BLOCK imported from stage3_math is the CHECKER_OUTPUT block", s3.REF_BLOCK == REF_BLOCK_OF_RECORD)
        t1 = "Work line one.\nWork line two.\nSo the answer is $\\boxed{7}$."
        s_, r_ = answer_span_start(t1)
        check("span: last \\boxed line", t1[s_:] == "So the answer is $\\boxed{7}$." and r_ == "boxed", (t1[s_:], r_))
        t2 = "x" * 250 + ". Hence we get " + "y" * 210 + " \\boxed{3}."
        s_, r_ = answer_span_start(t2)
        check("span: long lead cut at the last sentence end", t2[s_:].startswith("Hence we get") and r_ == "boxed+sentence", (t2[s_:40], r_))
        t3 = "z" * 260 + "\\boxed{3}"
        s_, r_ = answer_span_start(t3)
        check("span: long lead without a sentence end starts at the marker", t3[s_:] == "\\boxed{3}" and r_ == "boxed+marker", r_)
        t4 = "Reasoning para.\n\nThe final answer is 12.\n\n"
        s_, r_ = answer_span_start(t4)
        check("span: no \\boxed -> the last non-empty line", t4[s_:].startswith("The final answer is 12.") and r_ == "last-line", (t4[s_:], r_))
        t5 = "a" * 150 + ". b" * 40 + ". The answer is 4."
        s_, r_ = answer_span_start(t5)
        check("span: a single long last line -> its last sentence", t5[s_:] == "The answer is 4." and r_ == "last-line+sentence", (t5[s_:], r_))
        s_, r_ = answer_span_start("\\boxed{1}")
        check("span: nothing before the answer -> start 0 (excluded by the list)", s_ == 0)
        ct = "R" * 40 + "ANSWER"
        check("arms: truncate = C[s:], pad = PAD_UNIT x s + C[s:] at the original length",
              arm_trace(ct, 40, "truncate") == "ANSWER" and arm_trace(ct, 40, "pad") == " " * 40 + "ANSWER"
              and len(arm_trace(ct, 40, "pad")) == len(ct) and arm_trace(ct, 40, "original") == ct)
        u, off = build_user("Q?" + REF_BLOCK_OF_RECORD % "5", "TA", "TB")
        check("assembly by concatenation == rejudge_grok.build_user_prompt",
              u == rj.build_user_prompt("Q?" + REF_BLOCK_OF_RECORD % "5", "TA", "TB") and u[off["A"][0]:off["A"][1]] == "TA")
        try:
            assemble_bad = build_user("Q", "$traceB inside", "TB")[0] == rj.build_user_prompt("Q", "$traceB inside", "TB")
        except SystemExit:
            assemble_bad = False
        check("a trace holding a template placeholder is detectable (concatenation != replace)", not assemble_bad)
        check("C1 branches are disjoint and exhaustive", [c1_verdict(0.0, 0.09), c1_verdict(0.11, 0.2), c1_verdict(0.05, 0.10), c1_verdict(0.10, 0.2)] == ["HELD", "FAILED", "UND", "UND"])
        check("C2 branches are disjoint and exhaustive", [c2_verdict(0.5, 0.69), c2_verdict(0.71, 0.9), c2_verdict(0.6, 0.8), c2_verdict(0.70, 0.9)] == ["FAILED", "HELD", "UND", "UND"])
        check("parse_ready: needs the test name and the LF sha on the FIRST verdict line",
              parse_ready("READY: %s %s\n" % (TEST, "abc"), "abc")[1] == [] and parse_ready("READY: other abc\n", "abc")[1]
              and parse_ready("READY: %s abc\nNOT READY: x\n" % TEST, "abc")[1] and parse_ready("```\nREADY: %s abc\n```\n" % TEST, "abc")[0] is None)

        # 1. fixtures, the population, the list, the scan ---------------------------------------------------------------
        fx = _fixture(tmp)
        S3_CACHE, CHECKER_DB, CORPUS_DB = fx["S3_CACHE"], fx["CHECKER_DB"], fx["CORPUS_DB"]
        S3_CACHE_SHA256, CHECKER_SHA256 = file_sha256(S3_CACHE), file_sha256(CHECKER_DB)
        CACHE = os.path.join(tmp, "trace_truncation.db")
        OUT, OUT_PILOT, OUT_PARTIAL = (os.path.join(tmp, n) for n in ("out.txt", "out_PILOT.txt", "out_partial.txt"))
        LEDGER_DIR = tmp
        CANARY_CACHES = [os.path.join(tmp, "canary_pass3.db"), os.path.join(tmp, "canary_pass4.db")]
        EVIDENCE = os.path.join(tmp, "pairs.txt")
        RUNG_OUT = os.path.join(tmp, "rung.txt")
        json.dump([{"test": "OTHER", "launch": "x", "calls": 4060, "ts": "t"}], open(os.path.join(tmp, atl.NIGHT_FILE), "w"))
        cc = _TRUE_CONNECT(CANARY_CACHES[0])                     # the OTHER accepted test's cache: 100 posted rows = 200 calls
        cc.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY)")
        cc.executemany("INSERT INTO verdicts VALUES (?)", [(i,) for i in range(100)])
        cc.commit(); cc.close()
        day_path = atl.day_ledger_path(LEDGER_DIR)
        pool_guard.eval_ids = lambda pid: frozenset(fx["qids"])
        pool_guard.db_path = lambda pid: fx["CORPUS_DB"]
        install_db_guard()
        try:
            sqlite3.connect(os.path.join(ROOT, "snapshots_frozen.db"))
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("DBGUARD refuses a database outside the three inputs and the own cache", bool(refused) and '[DBGUARD] REFUSED' in str(refused), refused)
        wal = S3_CACHE + "-wal"
        open(wal, "wb").write(b"x")
        try:
            connect_ro(S3_CACHE)
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        os.remove(wal)
        check("DBGUARD refuses an input with a non-empty -wal (failed precondition)", bool(refused) and '-wal is non-empty' in str(refused), refused)
        src = load_sources()
        check("inputs opened read-only immutable", all(m == "ro-immutable" for m, _p in _OPENED), _OPENED[-3:])
        pairs, facts = select_pairs(src, pool_guard.eval_ids(POOL_ID))
        check("selection: key-decidable and THR-eligible pairs only, sorted by match id",
              len(pairs) > 0 and all(p["lc"] - p["lw"] >= THR for p in pairs) and [p["mid"] for p in pairs] == sorted(p["mid"] for p in pairs),
              facts)
        text = pairs_text(pairs, facts)
        check("the list text is a pure function (two renders byte-identical, LF only)", text == pairs_text(*select_pairs(src, pool_guard.eval_ids(POOL_ID))) and "\r" not in text)
        try:
            select_pairs(src, frozenset())
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("a scheduled question outside the pool's EVAL ids REFUSES", bool(refused) and '[POOL]' in str(refused), refused)
        ok, line = evidence_state(text)
        check("evidence MISSING -> C0 (a) fails", not ok and "MISSING" in line)
        open(EVIDENCE, "w", encoding="utf-8", newline="\n").write(text)
        PINNED_PAIRS_SHA256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        names = sorted({p[k] for p in pairs for k in ("model_a", "model_b")})
        scan = Counter()
        for p in pairs:
            scan.update(check_pair_payloads(p, src, names)[1])
        check("pre-call scan: 6 payloads per pair, identity / reference / frame on all",
              scan["payloads"] == 6 * len(pairs) == scan["identity_outside_span"] == scan["reference_intact"] == scan["frame_clean"], scan)
        p0 = pairs[0]
        bad_src = dict(src, text=dict(src["text"]))
        bad_src["text"][p0["qid"]] = src["text"][p0["qid"]] + " (%s is_correct)" % p0["correct"]
        try:
            check_pair_payloads(p0, bad_src, names)
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("LEAK: a contestant name / checker token in the frame REFUSES", bool(refused) and 'outside the trace slots' in str(refused), refused)
        bad_src2 = dict(src, text=dict(src["text"]))
        bad_src2["text"][p0["qid"]] = src["text"][p0["qid"]] + " a checkerboard is CORRECT"
        f2_ = check_pair_payloads(p0, bad_src2, names)[1]
        check("a checker token / verdict word in the QUESTION (dataset text) is counted, not refused",
              f2_["token_in_question"] == 6 and f2_["word_in_question"] == 6, f2_)
        saved_tpl = rj.USER_TEMPLATE
        rj.USER_TEMPLATE = saved_tpl.replace("[Model A's Response]", "[Model A's Response - PASS]")
        try:
            check_pair_payloads(p0, src, names)
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        rj.USER_TEMPLATE = saved_tpl
        check("LEAK: a verdict word in the user TEMPLATE REFUSES", bool(refused) and 'verdict word' in str(refused), refused)
        saved_arm = globals()["arm_trace"]

        def bad_arm(c, s, arm):
            return saved_arm(c, s, arm) + (" extra" if arm == "pad" else "")
        globals()["arm_trace"] = bad_arm
        try:
            check_pair_payloads(p0, src, names)
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        globals()["arm_trace"] = saved_arm
        check("IDENTITY: a pad arm that is not PAD_UNIT x s + C[s:] REFUSES", bool(refused) and '[IDENTITY]' in str(refused), refused)

        # 2. the gate and the budget ------------------------------------------------------------------------------------
        try:
            go_gate("--pilot 12", False)
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("GATE: no --go (and no committed READY) REFUSES before any DB", bool(refused) and '[GATE]' in str(refused), refused)
        def acct_refusal(planned, **patch):
            saved_ = {k: getattr(atl, k) for k in patch}
            try:
                for k, v in patch.items(): setattr(atl, k, v)
                budget_gate(planned, "probe")
                return False
            except SystemExit as e_:
                return str(e_)
            finally:
                for k, v in saved_.items(): setattr(atl, k, v)
        n0 = budget_gate(0, "probe", refuse=False)
        check("ACCOUNT: the other accepted test's cache is counted in (iii) (CANARY 200 calls)",
              n0["both"]["CANARY-EPOCH2-RUNG"] == 200 and n0["combined"] == 4060 + 200, n0)
        r = acct_refusal(CALL_CEILING + 2)
        check("ACCOUNT (i): above the test's own ceiling 2,184 REFUSES", r and "(i) " in r and "(ii)" not in r and "(iii)" not in r, r)
        r = acct_refusal(8004, CEILINGS=dict(atl.CEILINGS, **{TEST: 10 ** 6}))
        check("ACCOUNT (ii): above the 4,000-match rule REFUSES", r and "(ii)" in r and "(i) " not in r and "(iii)" not in r, r)
        r = acct_refusal(12, CLOSED_NIGHT_TOTAL=13790)
        check("ACCOUNT (iii): 13,790 + CANARY 200 + 12 > 14,000 REFUSES", r and "(iii)" in r and "(i) " not in r, r)

        # 3. posting through the INJECTED FAKE POSTER ------------------------------------------------------------------
        def rule(user):
            # names the side whose trace is longer, TIE when the correct trace is the bare answer: an 'elaboration judge'
            a0 = user.index("[Model A's Response]")
            b0 = user.index("[Model B's Response]")
            la, lb = b0 - a0, user.index("\n\n─", b0) - b0
            return "Model A" if la > lb else "Model B"
        fake, calls = _fake_poster(rule)
        rr.call_judge_full = fake
        try:
            post(pairs, src, None, 2, "--run")
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("--run before the pilot REFUSES", bool(refused) and "[RUN]" in str(refused) and not calls, refused)
        post(pairs, src, PILOT_MATCHES, 2, "--pilot %d" % PILOT_MATCHES)
        check("pilot posted exactly 24 calls through the fake poster", len(calls) == 2 * PILOT_MATCHES, len(calls))
        led = json.load(open(day_path))
        check("the POSTING-DATE ledger was created write-once and holds the posted count", led[-1]["calls"] == 24 and led[-1]["test"] == TEST
              and not json.load(open(os.path.join(tmp, atl.NIGHT_FILE)))[-1].get("test") == TEST, led[-1])
        rows, meta = cached_rows()
        check("the cache holds one row per (match, arm) with provenance (bodies, shas, fingerprints, ids, order index)",
              len(rows) == 12 and all(r["user1"] and r["user1_sha16"] == sha16(r["user1"]) and r["provider1"] == EXPECTED_FINGERPRINT
                                       and r["resp_id1"] and r["post_index"] is not None and r["script_sha16_lf"] == script_sha_lf() for r in rows.values()))
        check("run_meta pinned: temperature 'omitted', pair-list sha, system sha, script sha",
              meta.get("temperature") == "omitted" and meta.get("pairs_sha256_lf") == PINNED_PAIRS_SHA256
              and meta.get("system_sha16") == PINNED_SYSTEM_SHA16 and meta.get("script_sha16_lf") == script_sha_lf(), meta)
        rc = analyze_core(pairs, src, rows, meta, True, "[EVIDENCE] fixture", boot=50)
        check("a partial cache writes the PILOT file, never the outcome of record", rc == 2 and os.path.exists(OUT_PILOT) and not os.path.exists(OUT))
        n_before = len(calls)
        post(pairs, src, None, 2, "--run")
        check("--run posted the remainder only (cached rows never re-posted)", len(calls) - n_before == 2 * (3 * len(pairs) - PILOT_MATCHES), len(calls))
        rows, meta = cached_rows()
        rc = analyze_core(pairs, src, rows, meta, True, "[EVIDENCE] fixture", boot=50)
        check("a complete cache writes the outcome of record (mode x)", rc == 0 and os.path.exists(OUT))
        first = open(OUT, "rb").read()
        rc = analyze_core(pairs, src, rows, meta, True, "[EVIDENCE] fixture", boot=50)
        check("a second --analyze REFUSES to overwrite (write-once)", rc == 3 and open(OUT, "rb").read() == first)
        # a foreign fingerprint stops the run and caches nothing for that row
        fake2, calls2 = _fake_poster(lambda u: "FP")
        rr.call_judge_full = fake2
        CACHE = os.path.join(tmp, "trace_truncation_fp.db")
        try:
            post(pairs, src, 3, 1, "--pilot 3")
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        r_fp, _ = cached_rows()
        check("a foreign fingerprint STOPS the run, nothing cached, the ledger still appended", bool(refused) and "[FINGERPRINT]" in str(refused) and not r_fp and json.load(open(day_path))[-1]["calls"] >= 1, refused)
        # a pilot above the guard refuses the run
        fake3, calls3 = _fake_poster(lambda u: "INVALID")
        rr.call_judge_full = fake3
        CACHE = os.path.join(tmp, "trace_truncation_inv.db")
        try:
            post(pairs, src, PILOT_MATCHES, 2, "--pilot 12")
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("a pilot above 5% unusable FAILS its truncation guard", bool(refused) and '[GUARD]' in str(refused), refused)
        try:
            post(pairs, src, None, 2, "--run")
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("... and the run is then REFUSED", bool(refused) and '[GUARD]' in str(refused), refused)
        try:
            post(pairs, src, 5, 2, "--pilot 5")
            refused = False
        except SystemExit as _e:
            refused = str(_e) or "(empty SystemExit)"
        check("--pilot N that is not whole pairs REFUSES", bool(refused) and '[PILOT]' in str(refused), refused)
        rr.call_judge_full = saved_post

        # 4. every criterion / prediction / falsifier branch EXECUTED -----------------------------------------------------
        def synth(o, t, pd, n=60, q_per=2, seed=3):
            rng = random.Random(seed)
            ps, rs = [], {}
            for i in range(n):
                p = dict(mid=i, qid=i // q_per, model_a="Alpha", model_b="Beta", correct="Alpha" if i % 2 else "Beta")
                ps.append(p)
                for arm, pr in (("original", o), ("truncate", t), ("pad", pd)):
                    win = p["correct"] if rng.random() < pr else ("TIE" if rng.random() < 0.5 else ("Beta" if p["correct"] == "Alpha" else "Alpha"))
                    rs[(i, arm)] = dict(winner=win)
            return ps, rs
        good_c0 = [("(a) fixture", True, "")]
        bad_c0 = [("(a) fixture", False, "")]
        scenarios = [(1.0, 1.0, 1.0, good_c0, None), (1.0, 0.55, 0.9, good_c0, 0.2), (0.96, 0.9, 0.96, good_c0, None),
                     (1.0, 0.99, 0.5, good_c0, 0.001), (0.95, 0.5, 0.95, bad_c0, None), (0.9, 0.62, 0.95, good_c0, None),
                     (0.5, 0.5, 0.5, good_c0, None), (0.92, 0.75, 0.9, good_c0, None), (1.0, 0.84, 0.99, good_c0, None)]
        for o, t, pd, c0, rung in scenarios:
            for n in (60, 400):
                ps, rs = synth(o, t, pd, n=n)
                s = compute(ps, rs, B=40, seeds=(BOOT_SEED, 43, 44))
                readout(s, c0, 0 if o > 0.9 else 50, 1000, rung, (5, 6))
        ps, rs = synth(1.0, 1.0, 1.0)
        readout(compute(ps, {}, B=40), good_c0, 0, 0)
        missing = sorted(ALL_BRANCHES - BRANCHES_HIT)
        check("every criterion / prediction / falsifier branch executed (%d of %d)" % (len(BRANCHES_HIT & ALL_BRANCHES), len(ALL_BRANCHES)),
              not missing, missing)
        open(RUNG_OUT, "w").write("RUNG d43 = 0.071 [0.04, 0.10]\n")
        check("the rung floor is read from CANARY-EPOCH2-RUNG's outcome when present", rung_floor() == 0.071)
    finally:
        sqlite3.connect = _TRUE_CONNECT
        socket.socket.connect = saved_connect
        pool_guard.eval_ids, pool_guard.db_path, rr.call_judge_full = saved_eval_ids, saved_db_path, saved_post
        for k, v in saved.items():
            globals()[k] = v
    print("[SELFTEST] %s" % ("%d check(s) FAILED: %s" % (len(fails), fails) if fails else "all checks passed; 0 calls, no database of record opened, tmp %s" % tmp))
    print(dbguard_line())
    return 1 if fails else 0


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("[POOL] %s (union pool of record, MATH slice; verified by pool_guard.assert_pool_of_record in every DB-reading mode)" % POOL_ID, flush=True)
    ap = argparse.ArgumentParser(description="%s - %s" % (TEST, REGISTRATION))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--emit-pairs", metavar="PATH")
    ap.add_argument("--pilot", type=int)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--go", action="store_true", help="required for --pilot / --run (with a committed READY)")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--leakscan", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.emit_pairs:
        sys.exit(emit_pairs(a.emit_pairs))
    if a.dry_run:
        sys.exit(dry_run(a.pilot))
    if a.pilot is not None:
        sys.exit(launch(pilot=a.pilot, workers=a.workers, go=a.go))
    if a.run:
        sys.exit(launch(pilot=None, workers=a.workers, go=a.go))
    if a.analyze:
        sys.exit(analyze())
    if a.leakscan:
        sys.exit(leakscan())
    ap.error("one of --selftest / --emit-pairs PATH / --dry-run / --pilot N / --run / --analyze / --leakscan is required")
