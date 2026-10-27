"""BFCL-FLIP-RESEED - do the BFCL pilot's 100 ORDER-FLIP TIES reproduce when the SAME 100 matches are posted a second
time, or are they resampling noise at the tie boundary? (judged; 200 calls, 100 matches). REGISTERED 2026-09-23 BEFORE
ANY CODE OR CALL in docs/judge_v2_program.md L12048-L12314 (heading L12049), commit ca3a7cc; record
docs/agents/results/BFCL-FLIP-RESEED.json. An INDEPENDENT test: it is NOT an arm of BFCL-FINAL-STATE-SWAP, it is not
that test's control and that test is not its control (own cache, own run_meta, own script sha, own outcome file).

  python tools/analysis/bfcl_flip_reseed.py --selftest    synthetic fixtures under tempfile.mkdtemp(); opens no DB of
                                                          record, no network, 0 calls; every criterion, prediction and
                                                          falsifier print branch EXECUTED and the coverage asserted
  python tools/analysis/bfcl_flip_reseed.py --dry-run     ZERO CALLS: the pool id first; the 100 mids re-derived from the
                                                          pilot's cache (REFUSES unless exactly 100 and the registered
                                                          partition); mids / tasks / agents / pass-1 votes printed; the
                                                          cluster count; the schedule hash; the byte-identity gate over
                                                          the 200 cells; the night total; creates no cache
  python tools/analysis/bfcl_flip_reseed.py --pilot 12    24 calls: the 12 LOWEST mids of the 100 (deterministic, never
                                                          sampled); gated (READY + BFCL_FLIP_GO=11)
  python tools/analysis/bfcl_flip_reseed.py --run         the remaining 176 calls; REFUSES unless the 24 pilot cells are
                                                          cached and the truncation guard reads <= 5% unusable on them
  python tools/analysis/bfcl_flip_reseed.py --analyze     refuses a partial cache (writes bfcl_flip_reseed_PILOT.txt
                                                          instead); the outcome of record is WRITE-ONCE (open mode "x")

THE GATE: --pilot and --run REFUSE, fail-closed and before any file is opened, unless BFCL_FLIP_GO equals "11" (plan
Amendment 11, the budget; its clause 3(d) keeps the standard flow) AND docs/reviews/READY_bfcl_flip_reseed.md exists, is
tracked by git and carries no uncommitted change. --selftest, --dry-run and --analyze never post and are never gated.

WHAT THIS SCRIPT IS BUILT ON (reuse, pinned). The payload machinery is the PARENT INSTRUMENT's, imported as a module:
tools/analysis/bfcl_judged_pilot.py at 95c6d92, LF sha256[:16] 5e9db53b894eeccb (CRLF->LF normalised bytes). The
import is REFUSED at load time if the module's LF sha is anything else, so a later edit of the parent cannot move this
instrument's prompt silently. Reused from it: the corpus reader (Corpus, mode=ro&immutable=1), the raw-file readers,
read_ground_truth + render_reference (the PER-TASK expected outcome from possible_answer/BFCL_v4_multi_turn_base.json,
identical for both sides, 1,200-char CHECKER_TEXT_CUT), artefact_facts / cap_artefact (2,500 estimated tokens,
symmetric), build_schedule + schedule_hash, system_prompt (prompt_v2 verify-first + SYSTEM_BFCL / RUBRIC_BFCL +
SCHEMA_INSTRUCTION), assert_no_per_side_verdict, dual (TIE on flip), post (call_judge_full, fail-closed fingerprint),
configure_rr / post_body / assert_body_copy (rule 9), clustered (task-clustered bootstrap), wilson.

HYGIENE. The FIRST PRINTED LINE of every mode is the pool id p2035adddedd1becb (read from the FILE NAME of the write-once
experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json, whose EVAL base ids are asserted equal to the
corpus DB's; pool_guard is not imported, as in the parent: there is no MMLU-Pro pool here). Every scheduled task of the
100 is re-checked EVAL under split_side.tier_b norm-v1, recomputed from the corpus DB's tasks.family_id / content_key;
a single TRAIN or GATE side REFUSES, printing the id. [DBGUARD] sqlite3.connect is wrapped at import; the whitelist is
  experiment_results/agent/bfcl_result_2025-12-16.db   the corpus, mode=ro&immutable=1
  experiment_results/agent/bfcl_judged_pilot.db        the PILOT's cache, and ONLY with mode=ro&immutable=1 (any other
                                                       open of it is refused: it is never written)
  experiment_results/agent/bfcl_flip_reseed.db         THIS test's own cache (the only file written)
and every other database raises SystemExit before the connection is made. The wrapper is idempotent (the parent's
review D13: the parent's own wrapper is bypassed, not chained). The last line of every mode is the [DBGUARD] line.
The instrument NEVER reads a per-episode checker verdict INTO A PROMPT: checker outcomes are read only to reproduce the
filter that defined the 458 (inherited from the pilot's schedule) and to score P3; assert_no_per_side_verdict is
executed on ALL 200 re-assembled payloads (one execution per (mid, arm) cell, counted and printed).

THE 100, BY THE PREDICATE OF RECORD. The deciding subset = the pilot schedule's headline rows (both agents on the 7-agent
roster) with nj / nj_a / nj_b clear (458 mids). The set = those whose dual-order aggregation of the pilot's cached fwd /
rev verdicts is TIE under the recipe's TIE-on-flip rule (bfcl_judged_pilot.dual -> rejudge_grok.combine_orders). The
dry-run and every launch REFUSE unless it is exactly 100 mids AND the per-order partition is the registered one:
(Model A, Model A) 57 / (Model B, Model B) 0 / (TIE, Model A) 24 / (Model A, TIE) 14 / (TIE, TIE) 3 / (Model B, TIE) 2
(votes as posted: fwd shows agent_a first, rev shows agent_b first). The partition refusal is STRICTER than the
registration's "prints the registered partition"; it is fail-closed and changes no criterion. The 100 are pinned in
run_meta as a sorted JSON list and its sha256_16; a relaunch on a different set is refused.

SEED 137 is a PROVENANCE LABEL and the BOOTSTRAP SEED of record here, and the seed of the posting-order shuffle (recorded
per cell in the posting_order table). IT IS NOT A JUDGE SEED: the body carries no seed and no temperature (plan
Amendment 1 D2), asserted against rr.payload_body's source.

THE BYTE-IDENTITY GATE, AND WHAT "THE PILOT'S SHA FOR THE CELL" CAN MEAN. The pilot's cache stores NO per-cell payload
hash (verdicts has mid, arm, vote, conf, invalid, raw, ts, finish, ctokens, provider, max_tokens). The pilot's payload
for a cell is therefore defined as the PARENT MODULE's re-assembly (bfcl_judged_pilot.payloads at LF sha
5e9db53b894eeccb), and that re-assembly is tied to pass 1 ONLY THROUGH the SCHEDULE-WIDE PAYLOAD ANCHOR 951ec3a0a063b5a8 (programme D9 bracket
L11927-L11935 and the registrar's D1 ruling, programme section "## Registration defects recorded 2026-09-23 ... BFCL-FLIP-RESEED
and BFCL-FINAL-STATE-SWAP", 7da2ec5): sha256 over all 1,216 assembled payloads plus the system prompt, i.e. over the 608
schedule rows in build_schedule order of "<mid>|" + system + user_fwd + user_rev (utf-8), first 16 hex - the self-preference
stratum's payload BYTES included (hashed only; none of its data is read, none of its payloads posted). The per-cell
comparison (B) is a comparison with the PARENT MODULE'S RE-ASSEMBLY, never with a stored value. The gate, printed on every
mode, is:
  (A) the schedule-wide payload anchor recomputed through the parent module == 951ec3a0a063b5a8;
  (B) for each of the 200 (mid, arm) cells, sha256_16(system + U+001F + user) of THIS script's own assembly == the
      parent module's for the same cell (200 of 200); a single mismatch REFUSES and prints the cell;
  (C) this script's system prompt == the parent module's system_prompt() byte for byte, and its OWN sha16 ==
      058faa54f0697ad9 (the system prompt's hash of record, D1 ruling; printed and pinned);
  (D) SYSTEM_BFCL / RUBRIC_BFCL == the values pinned in the pilot cache's run_meta;
  (E) the schedule hash re-derived from the corpus == bcf9d1654e68e4ca == the pilot run_meta's, and the 608 cached
      schedule rows reproduce with 0 differences.
D1 (registrar ruling, 7da2ec5): the registration's seven "system prompt sha 951ec3a0a063b5a8" sites are bracketed; the
binding reading is (A) + (C) above, and P5 is scored on it.

CRITERIA (registration READOUTS AND CRITERIA, taken literally; each has ONE deciding statistic).
 C1 R = (the number of the 100 whose pass-2 dual-order aggregation is TIE) / 100 - the LITERAL denominator 100 (an
    unusable pass-2 match is therefore NOT a TIE); R over the usable matches is printed beside it and decides nothing.
    The deciding statistic is the task-clustered interval point +- 1.96 x the bootstrap SE (clusters = the distinct tasks
    of the 100, B = 2000, seed 137); percentile interval, B, cluster count and Wilson printed beside. BAR 0.566. HELD iff
    the interval lies wholly above 0.566; FAILED iff wholly below; UNDETERMINED iff it contains 0.566, or fewer than 90
    of the 100 yield a usable dual-order outcome, or the byte-identity gate did not pass 200 of 200. D2 (registrar
    ruling, 7da2ec5): THE VALIDITY TRIGGERS (usable < 90; the gate short of 200 of 200) ARE EVALUATED FIRST AND PRE-EMPT
    THE VERDICT: if any fires, C1 is "UNDETERMINED (BY TRIGGER: <trigger, with its value>)", the interval is PRINTED but
    NOT SCORED, and the falsifier is NOT evaluated; only if none fires is the interval read, with its three disjoint
    outcomes.
 C2 the position signature (a)-(d), descriptive, with denominators and intervals; C3 the exact two-sided McNemar on the
    200 (mid, arm) cells for "named the FIRST-SHOWN side", printed with "selected set, direction not verdict"; C4 the
    instrument counts (a)-(g). P1-P6 scored HELD / FAILED / UNDETERMINED explicitly. The falsifier's consequence is
    printed iff C1 FAILED. The Support section's measured DEFF (bootstrap variance / binomial variance, the definition of
    the pilot's 3.60), n_eff and MDE are printed beside the C1 interval.

CACHE experiment_results/agent/bfcl_flip_reseed.db: run_meta pinned at the first posting launch (test, registration,
judge, provider, cap, temperature "omitted", protocol, reference form, seeds, the 100 mids + sha, schedule hash, the
parent module's sha, the anchor, the system prompt's own sha16, SYSTEM_BFCL / RUBRIC_BFCL, the raw-file sha256s, and
script_sha256_16 = THIS file's LF-rendered sha256[:16]); any later launch differing on ANY pinned key, the script sha
included, is REFUSED. A cached row is never re-posted; a content-filter 400 is cached as an unusable row (rule 10);
errors are never cached. The night ledger experiment_results/night_calls_2026-09-23.json is read before and appended
after every posting launch against the 14,000-call ceiling of plan Amendment 9.
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
import tempfile
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import sqlite3  # noqa: E402

# ----------------------------------------------------------------------------------------------------------------
# THE DB GUARD. The TRUE sqlite3.connect is captured BEFORE the parent module is imported (the parent wraps it at its
# own import with a whitelist that does not name this cache); this module's wrapper then replaces the module attribute,
# so every connect in the process - the parent's Corpus included - passes HERE. Idempotent (review D13).
# ----------------------------------------------------------------------------------------------------------------
_pm = sys.modules.get("bfcl_judged_pilot")
_TRUE_CONNECT = (getattr(sqlite3.connect, "_true_connect", None)
                 or (_pm._real_sqlite3_connect if _pm is not None else sqlite3.connect))

import bfcl_judged_pilot as P      # noqa: E402  the parent instrument (pinned below by its LF sha)
import rejudge_grok as rj          # noqa: E402
import rejudge_reasoning as rr     # noqa: E402
import split_side                  # noqa: E402  norm-v1; imports nothing of record

TEST = "BFCL-FLIP-RESEED"
REGISTRATION = ("docs/judge_v2_program.md L12048-L12314 (heading L12049), commit ca3a7cc (registered 2026-09-23, before "
                "any code or call); record docs/agents/results/BFCL-FLIP-RESEED.json")
PARENT_SHA_PINNED = "5e9db53b894eeccb"          # bfcl_judged_pilot.py at 95c6d92, LF-rendered sha256[:16]
PARENT_COMMIT = "95c6d92"
if P.SCRIPT_SHA != PARENT_SHA_PINNED:
    raise SystemExit("[PARENT] REFUSED at import: tools/analysis/bfcl_judged_pilot.py has LF sha %s, not the pinned %s "
                     "(%s). The payload machinery of record moved; this instrument is not a retest under it."
                     % (P.SCRIPT_SHA, PARENT_SHA_PINNED, PARENT_COMMIT))

AGENT_DIR = os.path.join(ROOT, "experiment_results", "agent")
CORPUS_DB_NAME = P.CORPUS_DB_NAME                      # bfcl_result_2025-12-16.db
PILOT_DB_NAME = P.CACHE_DB_NAME                        # bfcl_judged_pilot.db
CACHE_DB_NAME = "bfcl_flip_reseed.db"
DB = os.path.join(AGENT_DIR, CORPUS_DB_NAME)
PILOT_CACHE = os.path.join(AGENT_DIR, PILOT_DB_NAME)
CACHE = os.path.join(AGENT_DIR, CACHE_DB_NAME)
OUT = os.path.join(AGENT_DIR, "bfcl_flip_reseed_outcome.txt")      # write-once, mode "x", complete cache only
OUT_PILOT = os.path.join(AGENT_DIR, "bfcl_flip_reseed_PILOT.txt")  # pilot / partial readout, overwritable
READY = os.path.join(ROOT, "docs", "reviews", "READY_bfcl_flip_reseed.md")
GO_ENV, GO_VALUE = "BFCL_FLIP_GO", "11"                           # plan Amendment 11 (budget), clause 3(d)
NIGHT_LEDGER = os.path.join(ROOT, "experiment_results", "night_calls_2026-09-23.json")
NIGHT_CEILING = 14000

ALLOWED_DB_BASENAMES = {CORPUS_DB_NAME, PILOT_DB_NAME, CACHE_DB_NAME, ":memory:"}
_OPENED = []


def _db_basename(database):
    s = str(database)
    if s == ":memory:" or s.startswith("file::memory:"):
        return ":memory:"
    if s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
    return os.path.basename(s.replace("\\", "/"))


def _ro_uri(s, kwargs):
    """True iff s is a file: URI opened with uri=True whose query carries exactly mode=ro and immutable=1."""
    from urllib.parse import parse_qs
    if not (s.startswith("file:") and kwargs.get("uri")) or "?" not in s:
        return False
    q = parse_qs(s.split("?", 1)[1])
    return q.get("mode") == ["ro"] and q.get("immutable") == ["1"]


def _guarded_connect(database, *args, **kwargs):
    base = _db_basename(database)
    if base not in ALLOWED_DB_BASENAMES:
        raise SystemExit("[DBGUARD] REFUSED: %s may open only %s; a connection to %r (%s) was attempted. Nothing of "
                         "record outside the BFCL corpus, the pilot's cache (read-only) and this test's own cache is "
                         "read (forbidden by name, among others: %s)."
                         % (os.path.basename(__file__), sorted(ALLOWED_DB_BASENAMES), str(database), base,
                            ", ".join(P.FORBIDDEN_DB_BASENAMES)))
    if base == CORPUS_DB_NAME:                                  # review 5(a): the corpus is read-only too
        s = str(database)
        if not _ro_uri(s, kwargs):
            raise SystemExit("[DBGUARD] REFUSED: the corpus %s may be opened ONLY as a URI with mode=ro&immutable=1 (it "
                             "is of record and never written); attempted %r" % (CORPUS_DB_NAME, s))
    if base == PILOT_DB_NAME:
        s = str(database)
        if not _ro_uri(s, kwargs):
            raise SystemExit("[DBGUARD] REFUSED: the pilot's cache %s may be opened ONLY as a URI with mode=ro&immutable=1 "
                             "(it is the control of record and is never written); attempted %r" % (PILOT_DB_NAME, s))
    _OPENED.append(str(database))
    return _TRUE_CONNECT(database, *args, **kwargs)


_guarded_connect._true_connect = _TRUE_CONNECT
_guarded_connect._owner = __name__
sqlite3.connect = _guarded_connect

# ----------------------------------------------------------------------------------------------------------------
# constants of record (the registration's)
# ----------------------------------------------------------------------------------------------------------------
POOL_ID = P.BFCL_POOL_ID                               # p2035adddedd1becb
SCHEDULE_HASH_OF_RECORD = "bcf9d1654e68e4ca"
ALL_PAYLOAD_ANCHOR = "951ec3a0a063b5a8"               # the SCHEDULE-WIDE PAYLOAD ANCHOR (1,216 payloads + system prompt; D1)
SYSTEM_PROMPT_SHA = "058faa54f0697ad9"                # the system prompt's OWN sha16 of record (D1 ruling, 7da2ec5)
N_SCHEDULE_ROWS = 608
N_DECIDING = 458
N_SET = 100
N_CELLS = 2 * N_SET
REG_PARTITION = ((("Model A", "Model A"), 57), (("Model B", "Model B"), 0), (("TIE", "Model A"), 24),
                 (("Model A", "TIE"), 14), (("TIE", "TIE"), 3), (("Model B", "TIE"), 2))
SEED = 137                                             # provenance label + bootstrap seed + posting-order shuffle; NOT a judge seed
BOOT = 2000
BAR = 0.566
STABLE_ANCHOR = 0.913
NOISE_ANCHOR = 0.2183
MIN_USABLE = 90
PILOT_MATCHES = 12
GUARD_RATE = 0.05
PLANNING_DEFF = (3.60, 5.0)                            # the Support section's planning values (measured 3.60, pessimistic 5.0)
PILOT_FIRST_POS = (0.5862, 870, 5.09)                  # the pilot's marginal first-position rate, non-tie votes, z
SEP = "\x1f"
PROTOCOL = ("BFCL-FLIP-RESEED: a SECOND POSTING of the frozen BFCL-JUDGED-PILOT instrument on the 100 dual-order-TIE "
            "matches of its deciding subset, both orders, byte-identical payloads (gated), new session; parent protocol: "
            + P.PROTOCOL)
ASSUMPTION = ("STATED ASSUMPTION (registration, WHAT THIS RUN WILL NOT SHOW (1)): the 'different 100' leg is answered only "
              "INDIRECTLY, through the noise anchor 0.2183, and that inference rests on the corpus's marginal tie rate being "
              "itself stable across sessions - which this run cannot check.")
TWO_HYP = ("C1 is a TWO-HYPOTHESIS DISCRIMINATION at a pre-set bar (0.913 stable vs 0.2183 noise, bar 0.566); it licenses "
           "no statement of the form 'the flips reproduce at X%' with a tight interval.")
POSITION_INDEX_NOTE = ("STATED DEPENDENCY (registration bracket): POSITION-INDEX-ALL, if it has landed, is quoted in the "
                       "outcome section as CONTEXT and is NEVER folded into R, into C1's bar or into any interval here.")

_NIGHT_LINE = None

# ----------------------------------------------------------------------------------------------------------------
# branch coverage: every criterion / prediction / falsifier print branch registers its tag when it prints
# ----------------------------------------------------------------------------------------------------------------
ALL_BRANCHES = frozenset(
    ["C1:HELD", "C1:FAILED", "C1:UND_INTERVAL",
     "C1:TRIG_USABLE", "C1:TRIG_GATE", "C1:PREEMPT_USABLE", "C1:PREEMPT_GATE",
     "FALS:FIRES", "FALS:HELD", "FALS:UND", "FALS:NOT_EVALUATED",
     "C2:HELD", "C2:FAILED", "C3:HELD", "C3:FAILED", "C4:HELD", "C4:FAILED",
     "SUPPORT:OK", "SUPPORT:DEGENERATE", "USABLE:SAME", "USABLE:DIFFERS", "USABLE:NA"]
    + ["%s:%s" % (p, v) for p in ("P1", "P2", "P3", "P6") for v in ("HELD", "FAILED", "UND")]
    + ["%s:%s" % (p, v) for p in ("P4", "P5") for v in ("HELD", "FAILED")])
BRANCHES_HIT = set()


def hit(tag):
    assert tag in ALL_BRANCHES, "undeclared branch tag %r" % tag
    BRANCHES_HIT.add(tag)


def rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


def script_sha_lf():
    """sha256[:16] of this file with CRLF normalised to LF (the LF rendering; equals `git show HEAD:<path> | sha256sum`)."""
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def script_sha_raw():
    """sha256[:16] of the working-tree bytes as they are (CRLF on a Windows autocrlf checkout)."""
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


SCRIPT_SHA = script_sha_lf()


def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def dbguard_line():
    seen = []
    for p in _OPENED:
        if p not in seen:
            seen.append(p)
    return ("[DBGUARD] sqlite3.connect: %d call(s) in this process: %s | whitelist %s"
            % (len(_OPENED), ", ".join(rel(p.split("?", 1)[0].replace("file:", "")) for p in seen) or "(none)",
               sorted(ALLOWED_DB_BASENAMES)))


# ----------------------------------------------------------------------------------------------------------------
# the READY gate and the night ceiling
# ----------------------------------------------------------------------------------------------------------------
VERDICT_RE = re.compile(r"^\s*#{0,6}\s*\**\s*(NOT READY|READY-WITH-CONDITIONS|READY)\b\s*\**\s*:", re.M)


def parse_ready(text):
    """The READY file's CONTENT (review condition 1): -> (verdict, verdict line, names-this-sha, reasons-to-refuse).
    A verdict line is a line whose first word (after optional markdown '#' / '**') is NOT READY, READY-WITH-CONDITIONS or
    READY, followed by ':'. The FIRST verdict line is the verdict; ANY 'NOT READY' verdict line anywhere refuses; the
    first verdict line must name this test AND this script's LF-rendered sha16 (D-G1); lines inside a fenced block are
    ignored (D-G2), as quote-block and table lines already are (they do not match the verdict pattern)."""
    body, fence = [], None                      # D-G2: a verdict inside a fenced ``` / ~~~ block is not a verdict
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
    lines = [m for m in VERDICT_RE.finditer(text)]
    reasons = []
    if not lines:
        return None, "", bool(SCRIPT_SHA in text), ["no verdict line (READY / READY-WITH-CONDITIONS / NOT READY followed by ':')"]
    verdict = lines[0].group(1)
    first = text[lines[0].start():].split("\n", 1)[0].strip()
    if verdict not in ("READY", "READY-WITH-CONDITIONS"):
        reasons.append("the verdict is %r" % verdict)
    if any(m.group(1) == "NOT READY" for m in lines):
        reasons.append("a NOT READY verdict line is present")
    if TEST not in first:
        reasons.append("the verdict line does not name %s" % TEST)
    named = bool(SCRIPT_SHA in first)            # D-G1: the sha must be ON THE VERDICT LINE, not anywhere in the file
    if not named:
        reasons.append("the verdict line does not name this script's LF sha16 %s" % SCRIPT_SHA)
    return verdict, first, named, reasons


def gate_state():
    have = os.environ.get(GO_ENV)
    exists = os.path.exists(READY)
    tracked, clean, head = P.git_tracked_clean(READY) if exists else (False, False, "")
    verdict, first, named, reasons = (parse_ready(open(READY, encoding="utf-8").read()) if exists
                                      else (None, "", False, ["the READY file is missing"]))
    ok = bool(have == GO_VALUE and exists and tracked and clean and not reasons)
    state = ("MISSING" if not exists else "exists, committed %s" % head if (tracked and clean)
             else "exists, NOT committed (untracked)" if not tracked else "exists, uncommitted change")
    return ok, ("%s=%r (needs %r) | %s %s | parsed verdict %r (line: %r) | names this script's LF sha16 %s: %s%s"
                % (GO_ENV, have, GO_VALUE, rel(READY), state, verdict, first[:120], SCRIPT_SHA, named,
                   "" if not reasons else " | CONTENT REFUSES: " + "; ".join(reasons)))


def go_gate(what):
    """Printed on BOTH branches (guard 22 / rule 11): the parsed verdict and whether this script's sha is named."""
    ok, s = gate_state()
    if not ok:
        raise SystemExit("[READY] %s refused (0 calls, nothing opened): %s. Nothing is posted - the pilot included - until "
                         "the reviewer's READY for THIS script sha is committed (plan Amendment 11 clause 3(d))." % (what, s))
    print("[READY] %s OPEN: %s" % (what, s))


def own_posted_calls():
    if not os.path.exists(CACHE):
        return 0
    con = sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)
    try:
        return con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
    except sqlite3.Error:
        return 0
    finally:
        con.close()


def night_ledger_read():
    if not os.path.exists(NIGHT_LEDGER):
        return None, "no shared night ledger at %s" % rel(NIGHT_LEDGER)
    try:
        rows = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
        total = sum(int(r["calls"]) for r in rows)
    except Exception as e:                                   # noqa: BLE001
        raise SystemExit("[NIGHT] REFUSED: %s is unreadable (%s: %s); nothing is posted."
                         % (rel(NIGHT_LEDGER), type(e).__name__, str(e)[:120]))
    return total, "%s (%d launch rows)" % (rel(NIGHT_LEDGER), len(rows))


def night_line(planned, what):
    """Printed at EVERY launch; the launch that would cross the ceiling is REFUSED, not trimmed."""
    global _NIGHT_LINE
    ledger, src = night_ledger_read()
    own = own_posted_calls()
    cum, how = ((own, "%s; counting THIS TEST'S OWN posted calls only (%d rows) - the operator's count governs" % (src, own))
                if ledger is None else (ledger, "%s; this test's own cache holds %d posted rows" % (src, own)))
    line = ("[NIGHT] cumulative grok calls tonight %d of %d (plan Amendment 9 hard ceiling; count of record %s) | this "
            "launch (%s) would post at most %d -> %d | source: %s" % (cum, NIGHT_CEILING, rel(NIGHT_LEDGER), what, planned,
                                                                   cum + planned, how))
    _NIGHT_LINE = line
    print(line, flush=True)
    if cum + planned > NIGHT_CEILING:
        raise SystemExit("[NIGHT] REFUSED, not trimmed: %d + %d = %d would cross the %d-call ceiling."
                         % (cum, planned, cum + planned, NIGHT_CEILING))
    return cum


def night_ledger_append(calls, what):
    rows = []
    if os.path.exists(NIGHT_LEDGER):
        rows = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
    rows.append({"test": TEST, "launch": what, "calls": int(calls), "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
    tmp = NIGHT_LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    os.replace(tmp, NIGHT_LEDGER)
    print("[NIGHT] appended %d posted calls for %s to %s" % (calls, what, rel(NIGHT_LEDGER)), flush=True)


# ----------------------------------------------------------------------------------------------------------------
# the pool (first line), the split, the pilot's cache
# ----------------------------------------------------------------------------------------------------------------
def pool_line():
    """The verified pool line (the FIRST printed line of every mode is the constant pool id, printed by __main__ before
    anything else; this line re-reads the pool file and the corpus asserts its EVAL ids equal to it)."""
    if not os.path.exists(P.POOL_JSON):
        raise SystemExit("[POOL] %s REFUSED: %s is missing." % (POOL_ID, rel(P.POOL_JSON)))
    ids = json.load(open(P.POOL_JSON, encoding="utf-8"))
    base = sorted(int(i) for i in ids["BFCL/%s" % P.STRATUM])
    print("[POOL] verified %s - BFCL pool of record, %d EVAL %s tasks (id from the FILE NAME of %s; pool_guard not imported: no "
          "MMLU-Pro / union pool is read)" % (POOL_ID, len(base), P.STRATUM, rel(P.POOL_JSON)), flush=True)
    return base


def split_check(task_ids, db_path=None):
    """Every scheduled task EVAL under split_side.tier_b norm-v1, recomputed from the corpus DB (mode=ro&immutable=1).
    -> (n_checked, list of refusals)."""
    db_path = db_path or DB
    con = sqlite3.connect("file:%s?mode=ro&immutable=1" % db_path.replace("\\", "/"), uri=True)
    try:
        rows = {r[0]: r[1:] for r in con.execute("SELECT task_id, family_id, content_key, side FROM tasks")}
    finally:
        con.close()
    bad = []
    for t in sorted(set(task_ids)):
        if t not in rows:
            bad.append("%s absent from the corpus" % t)
            continue
        fam, ck, side = rows[t]
        re_side = split_side.tier_b(fam, ck)
        if re_side != split_side.EVAL or side != split_side.EVAL:
            bad.append("%s: stored side %s, recomputed %s (%s)" % (t, side, re_side, split_side.NORMALISER_VERSION))
    return len(set(task_ids)), bad


def open_pilot_ro(path=None):
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % (path or PILOT_CACHE).replace("\\", "/"), uri=True)


def raw_votes(con, table, mids):
    """-> {(mid, arm): (vote, finish, ctokens, provider)} as cached."""
    out = {}
    mids = list(mids)
    for i in range(0, len(mids), 400):
        chunk = mids[i:i + 400]
        q = ("SELECT mid, arm, vote, finish, ctokens, provider FROM %s WHERE mid IN (%s)"
             % (table, ",".join("?" * len(chunk))))
        for mid, arm, vote, finish, ctok, prov in con.execute(q, chunk):
            out[(mid, arm)] = (vote, finish, ctok, prov)
    return out


def adj(v):
    """The per-order vote after the unusable rule (finish length / content_filter -> INVALID); None when not cached."""
    if v is None:
        return None
    return P.unusable_vote(v[0], v[1])


def order_class(votes, mid):
    return (adj(votes.get((mid, "fwd"))), adj(votes.get((mid, "rev"))))


def load_context():
    """Everything the dry-run, the launches and --analyze need, read-only. Refusals are raised by refusals(ctx)."""
    base_ids = pool_line()
    c = P.Corpus(P.DB, base_ids)
    assert P.aap.DECIDED_TYPES == P.DECIDED_TYPES, "the checker-decided rule moved in agent_admission_pilot"
    raws = P.read_raw_episodes(P.ROSTER_ALL, c.eval_base)
    tasktext, ds_path, ds_sha = P.read_task_text(c.eval_base)
    gt, pa_path, pa_sha = P.read_ground_truth(c.eval_base)
    refs = {t: P.render_reference(gt[t]) for t in c.eval_base}
    rows, H, G = P.build_schedule(c, raws)
    if not os.path.exists(PILOT_CACHE):
        raise SystemExit("[PILOT] REFUSED: %s is missing (untracked; it lives in the main checkout)." % rel(PILOT_CACHE))
    con_p = open_pilot_ro()
    try:
        meta_p = dict(con_p.execute("SELECT key, value FROM run_meta"))
        cached_sched = [tuple(r) for r in con_p.execute("SELECT %s FROM schedule ORDER BY mid" % ",".join(P.SCHEDULE_COLS))]
        deciding = [r for r in rows if r["stratum"] == "headline" and not r["nj"] and not r["nj_a"] and not r["nj_b"]]
        D1 = P.dual(con_p, deciding)
        set_rows = sorted((r for r in deciding if D1[r["mid"]]["winner"] == "TIE"), key=lambda r: r["mid"])
        votes1 = raw_votes(con_p, "verdicts", [r["mid"] for r in deciding])     # the headline deciding cells only
        pilot_nontie_first = pilot_first_position(con_p, [r["mid"] for r in deciding])
    finally:
        con_p.close()
    recomputed = sorted(tuple(r[k] for k in P.SCHEDULE_COLS) for r in rows)
    sched_diffs = sum(1 for a, b in zip(recomputed, cached_sched) if a != b) + abs(len(recomputed) - len(cached_sched))
    return dict(c=c, raws=raws, tasktext=tasktext, refs=refs, rows=rows, deciding=deciding, D1=D1, set_rows=set_rows,
                votes1=votes1, meta_p=meta_p, sched_diffs=sched_diffs, sched_hash=P.schedule_hash(rows),
                shas={"dataset": ds_sha, "possible_answer": pa_sha, "dataset_path": ds_path, "possible_answer_path": pa_path},
                pilot_first=pilot_nontie_first)


def pilot_first_position(con, mids):
    """(first-shown votes, non-tie votes) over the pilot's cached cells of the deciding subset (the 0.5862 of 870)."""
    v = raw_votes(con, "verdicts", mids)
    adjv = [adj(x) for x in v.values()]
    nontie = [x for x in adjv if x in ("Model A", "Model B")]
    return sum(1 for x in nontie if x == "Model A"), len(nontie)


def outcome_class(v):
    """A dual-order outcome as a class: PENDING / INVALID / TIE / COMMITTED (a named winner)."""
    if v["pending"]:
        return "PENDING"
    if v["invalid"] or v["winner"] == "INVALID":
        return "INVALID"
    return "TIE" if v["winner"] == "TIE" else "COMMITTED"


def partition(set_rows, votes):
    cnt = Counter(order_class(votes, r["mid"]) for r in set_rows)
    return cnt


def set_sha(mids):
    return hashlib.sha256(",".join(str(m) for m in sorted(mids)).encode("utf-8")).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------------------------
# assembly and the byte-identity gate
# ----------------------------------------------------------------------------------------------------------------
def system_prompt():
    """THIS instrument's system prompt: the parent's, unchanged (gate (C) asserts byte identity)."""
    import prompt_v2
    return (prompt_v2.v2_system_template().replace("$systemPrompt", P.SYSTEM_BFCL).replace("$rubric", P.RUBRIC_BFCL)
            + "\n\n" + rj.SCHEMA_INSTRUCTION)


def assemble(row, arm, ctx, counter=None):
    """THIS instrument's own assembly of one (mid, arm) cell -> (system, user). The ruling's leakage guard is executed
    once per cell (the task statement is the same in both orders; it is asserted to occur exactly once in the turn)."""
    c, raws, tasktext, refs = ctx["c"], ctx["raws"], ctx["tasktext"], ctx["refs"]
    t, a, b = row["task_id"], row["agent_a"], row["agent_b"]
    ea, eb = c.eps[(t, a)], c.eps[(t, b)]
    q = tasktext[t] + refs[t][0]
    P.assert_no_per_side_verdict(q, ea, eb)
    if counter is not None:
        counter["leak_checks"] += 1
    ta = P.artefact_facts(raws.get((t, a)), ea)["text"]
    tb = P.artefact_facts(raws.get((t, b)), eb)["text"]
    user = rj.build_user_prompt(q, ta, tb) if arm == "fwd" else rj.build_user_prompt(q, tb, ta)
    assert user.count(q) == 1, "the checked task statement must occur exactly once in the user turn"
    return system_prompt(), user


def cell_sha(system, user):
    return sha16(system + SEP + user)


def all_payload_anchor(rows, payload_fn):
    """The review's recipe (docs/reviews/2026-09-23_bfcl_judged_pilot_post.md row 7e): sha256 over the schedule rows in
    build_schedule order of '<mid>|' + system + user_fwd + user_rev, utf-8, first 16 hex."""
    h = hashlib.sha256()
    for r in rows:
        s, u1, u2 = payload_fn(r)
        h.update(("%d|" % r["mid"]).encode("utf-8"))
        h.update(s.encode("utf-8"))
        h.update(u1.encode("utf-8"))
        h.update(u2.encode("utf-8"))
    return h.hexdigest()[:16]


def byte_gate(ctx, target_rows=None):
    """Gates (A)-(E) of the docstring. -> dict; never raises (refusals() raises)."""
    rows = ctx["rows"]
    target_rows = ctx["set_rows"] if target_rows is None else target_rows
    parent = {}

    def parent_payload(r):
        if r["mid"] not in parent:
            parent[r["mid"]] = P.payloads(r, ctx["c"], ctx["raws"], ctx["tasktext"], ctx["refs"])
        return parent[r["mid"]]
    anchor = all_payload_anchor(rows, parent_payload)
    counter = Counter()
    mism = []
    cells = []
    n_eq = 0
    for r in target_rows:
        ps, pu1, pu2 = parent_payload(r)
        for arm, pu in (("fwd", pu1), ("rev", pu2)):
            s, u = assemble(r, arm, ctx, counter)
            own, par = cell_sha(s, u), cell_sha(ps, pu)
            cells.append((r["mid"], arm, own, par))
            if own == par:
                n_eq += 1
            else:
                mism.append("mid %d %s: own %s != parent %s" % (r["mid"], arm, own, par))
    own_sys, par_sys = system_prompt(), P.system_prompt()
    meta_p = ctx["meta_p"]
    slots_ok = bool(meta_p.get("system_bfcl") == P.SYSTEM_BFCL and meta_p.get("rubric_bfcl") == P.RUBRIC_BFCL)
    sched_ok = bool(ctx["sched_hash"] == SCHEDULE_HASH_OF_RECORD == meta_p.get("schedule_hash") and ctx["sched_diffs"] == 0
                    and len(rows) == N_SCHEDULE_ROWS)
    n_cells = 2 * len(target_rows)
    ok = bool(anchor == ALL_PAYLOAD_ANCHOR and n_eq == n_cells and not mism and own_sys == par_sys
              and sha16(own_sys) == SYSTEM_PROMPT_SHA and slots_ok and sched_ok)
    return dict(ok=ok, anchor=anchor, n_eq=n_eq, n_cells=n_cells, mism=mism, cells=cells, sys_equal=bool(own_sys == par_sys),
                sys_sha=sha16(own_sys), slots_ok=slots_ok, sched_ok=sched_ok, leak_checks=counter["leak_checks"])


def gate_lines(g):
    return ["[BYTE-GATE] (A) SCHEDULE-WIDE PAYLOAD ANCHOR over all 1,216 assembled payloads plus the system prompt (608 "
            "schedule rows, the self-preference stratum's payload BYTES INCLUDED - hashed only, none of its data read, none "
            "posted), recomputed through the parent module: %s vs of record %s -> %s"
            % (g["anchor"], ALL_PAYLOAD_ANCHOR, "MATCH" if g["anchor"] == ALL_PAYLOAD_ANCHOR else "MISMATCH"),
            "[BYTE-GATE] (B) (mid, arm) cells whose own-assembly sha16 equals the PARENT MODULE'S RE-ASSEMBLY of the same cell "
            "(the pilot cache stores no per-cell hash; tied to pass 1 only through (A)): %d of %d%s"
            % (g["n_eq"], g["n_cells"], "" if not g["mism"] else " | FIRST MISMATCH: %s" % g["mism"][0]),
            "[BYTE-GATE] (C) system prompt byte-identical to the parent's system_prompt(): %s | its OWN sha16 %s vs of record "
            "%s -> %s" % (g["sys_equal"], g["sys_sha"], SYSTEM_PROMPT_SHA,
                          "MATCH" if g["sys_sha"] == SYSTEM_PROMPT_SHA else "MISMATCH"),
            "[BYTE-GATE] (D) SYSTEM_BFCL / RUBRIC_BFCL equal to the pilot run_meta's pinned values: %s | (E) schedule "
            "hash %s re-derived, 608 cached rows reproduce with 0 differences: %s"
            % (g["slots_ok"], SCHEDULE_HASH_OF_RECORD, g["sched_ok"]),
            "[BYTE-GATE] assert_no_per_side_verdict executed on %d of %d re-assembled payloads (one per cell) -> %s"
            % (g["leak_checks"], g["n_cells"], "PASS (every gate)" if g["ok"] else "REFUSED")]


def post_counted(con, jobs, workers, what):
    """P.post with EVERY posted call counted - errored ones included - and the night-ledger append in a `finally`, so a
    crash mid-run (a fingerprint stop, an exception) still records what was posted (review 5(c)). The count is the number
    of rejudge_reasoning.call_judge_full invocations, read by wrapping the module attribute P.post calls through."""
    posted = []                                 # list.append is atomic across the worker threads (no lost count)
    real = rr.call_judge_full

    def counted(*a, **k):
        posted.append(1)
        return real(*a, **k)
    rr.call_judge_full = counted
    ok_n = err = 0
    fins = Counter()
    try:
        if jobs:
            ok_n, err, fins = P.post(con, jobs, workers, "verdicts")
    finally:
        rr.call_judge_full = real
        night_ledger_append(len(posted), what)
        print("[NIGHT] %s: %d calls posted (cached ok %d, errors %d - errors are posted calls and are counted, never "
              "cached)" % (what, len(posted), ok_n, err), flush=True)
    return ok_n, err, fins


def refusals(ctx, g, db_path=None):
    """Every fail-closed condition of the registration; -> list (empty = clear)."""
    bad = []
    if len(ctx["deciding"]) != N_DECIDING:
        bad.append("the deciding subset is %d mids, not %d" % (len(ctx["deciding"]), N_DECIDING))
    if len(ctx["set_rows"]) != N_SET:
        bad.append("the predicate yields %d mids, not EXACTLY %d" % (len(ctx["set_rows"]), N_SET))
    part = partition(ctx["set_rows"], ctx["votes1"])
    for cls, n in REG_PARTITION:
        if part.get(cls, 0) != n:
            bad.append("partition class %s is %d, registered %d" % (cls, part.get(cls, 0), n))
    other = sum(v for k, v in part.items() if k not in dict(REG_PARTITION))
    if other:
        bad.append("%d of the set fall outside the six registered classes" % other)
    for r in ctx["set_rows"]:
        if r["agent_a"] not in P.HEADLINE_ROSTER or r["agent_b"] not in P.HEADLINE_ROSTER:
            bad.append("mid %d carries an agent off the 7-agent headline roster" % r["mid"])
    n_chk, split_bad = split_check(db_path=db_path, task_ids=[r["task_id"] for r in ctx["set_rows"]])
    bad += ["SPLIT: " + s for s in split_bad]
    if not g["ok"]:
        bad.append("the byte-identity gate did not pass (see the [BYTE-GATE] lines)")
    mp = ctx["meta_p"]
    for k, want in (("judge_model", P.JUDGE_MODEL), ("max_tokens", str(P.MAXTOK)), ("temperature", "omitted"),
                    ("seed", "42"), ("pool_id", POOL_ID)):
        if mp.get(k) != want:
            bad.append("pilot run_meta %s is %r, expected %r" % (k, mp.get(k), want))
    return bad


# ----------------------------------------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------------------------------------
def mcnemar_exact(b, c):
    """Exact two-sided McNemar, integer arithmetic (systematic_budget.mcnemar_edge's form)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n))


def rate_with_intervals(by_task, boot, seed):
    """-> dict(k, n, point, lo_n, hi_n (point +- 1.96 SE), lo_p, hi_p (percentile), sd, wlo, whi, q)."""
    vals = [v for vs in by_task.values() for v in vs]
    n, k = len(vals), sum(vals)
    if n == 0:
        nan = float("nan")
        return dict(k=0, n=0, point=nan, lo_n=nan, hi_n=nan, lo_p=nan, hi_p=nan, sd=nan, wlo=nan, whi=nan, q=0)
    point, lo, hi, sd = P.clustered(by_task, boot, seed)
    wlo, whi = P.wilson(k, n)
    return dict(k=k, n=n, point=point, lo_n=point - 1.96 * sd, hi_n=point + 1.96 * sd, lo_p=lo, hi_p=hi, sd=sd,
                wlo=wlo, whi=whi, q=len(by_task))


def fmt_rate(name, r, denom_label, boot, seed):
    return ("%s = %d / %d = %.4f (%s; %d task clusters) | interval of record point +- 1.96 x clustered SE %.4f = [%.4f, "
            "%.4f] | percentile [%.4f, %.4f] (B = %d, seed %d) | Wilson [%.4f, %.4f]"
            % (name, r["k"], r["n"], r["point"], denom_label, r["q"], r["sd"], r["lo_n"], r["hi_n"], r["lo_p"], r["hi_p"],
               boot, seed, r["wlo"], r["whi"]))


def support(r):
    """Measured DEFF = clustered bootstrap variance / binomial variance (the definition behind the pilot's 3.60);
    n_eff = n / DEFF; MDE at 80% power / alpha .05 two-sided = 2.80 x SE (at R = 0.5 as the registration plans it, and
    at the measured SE)."""
    n, p, sd = r["n"], r["point"], r["sd"]
    if n == 0 or not (0.0 < p < 1.0) or not (sd == sd):
        return dict(deff=float("nan"), neff=float("nan"), mde_plan=float("nan"), mde_meas=2.80 * sd if sd == sd else float("nan"))
    naive = p * (1 - p) / n
    deff = (sd * sd) / naive
    neff = n / deff if deff > 0 else float("nan")
    return dict(deff=deff, neff=neff, mde_plan=2.80 * math.sqrt(0.25 / neff) if neff == neff and neff > 0 else float("nan"),
                mde_meas=2.80 * sd)


def cluster_sizes(rows):
    sizes = Counter(Counter(r["task_id"] for r in rows).values())
    n = sum(s * c for s, c in sizes.items())
    kish = sum(s * s * c for s, c in sizes.items()) / max(1, n)
    return sizes, kish


def compute(set_rows, votes1, votes2, D2, g, posted, boot=BOOT, seed=SEED):
    """Every number the readout prints, from the set's rows, the pass-1 and pass-2 raw votes and the pass-2 dual
    aggregation. Pure: the selftest drives it on synthetic data."""
    s = dict(boot=boot, seed=seed, gate=g, posted=posted)
    by_task = defaultdict(list)
    usable = 0
    pending = 0
    for r in set_rows:
        v = D2[r["mid"]]
        by_task[r["task_id"]].append(1 if (not v["pending"] and v["winner"] == "TIE") else 0)
        usable += int((not v["pending"]) and (not v["invalid"]))
        pending += int(bool(v["pending"]))
    s["n_set"], s["usable"], s["pending"] = len(set_rows), usable, pending
    s["R"] = rate_with_intervals(by_task, boot, seed)
    s["R_usable"] = (sum(1 for r in set_rows if D2[r["mid"]]["winner"] == "TIE") / usable) if usable else float("nan")
    by_task_u = defaultdict(list)                # the usable-only R with its interval (D-G5): usable pass-2 matches only
    for r in set_rows:
        v = D2[r["mid"]]
        if (not v["pending"]) and (not v["invalid"]):
            by_task_u[r["task_id"]].append(1 if v["winner"] == "TIE" else 0)
    s["R_u"] = rate_with_intervals(by_task_u, boot, seed)
    s["sizes"], s["kish"] = cluster_sizes(set_rows)
    s["support"] = support(s["R"])
    part1 = partition(set_rows, votes1)
    part2 = partition(set_rows, votes2)
    s["part1"], s["part2"] = part1, part2
    # C2 (a), (b): the (Model A, Model A) subclass
    aa = [r for r in set_rows if order_class(votes1, r["mid"]) == ("Model A", "Model A")]
    a_bt, b_bt = defaultdict(list), defaultdict(list)
    for r in aa:
        a_bt[r["task_id"]].append(1 if order_class(votes2, r["mid"]) == ("Model A", "Model A") else 0)
        b_bt[r["task_id"]].append(1 if D2[r["mid"]]["winner"] == "TIE" else 0)
    s["c2a"] = rate_with_intervals(a_bt, boot, seed)
    s["c2b"] = rate_with_intervals(b_bt, boot, seed)
    # C2 (c): pass-2 first-position rate over the pass-2 non-tie votes of the 200 cells
    c_bt = defaultdict(list)
    for r in set_rows:
        for arm in ("fwd", "rev"):
            v = adj(votes2.get((r["mid"], arm)))
            if v in ("Model A", "Model B"):
                c_bt[r["task_id"]].append(1 if v == "Model A" else 0)
    s["c2c"] = rate_with_intervals(c_bt, boot, seed)
    # C2 (d): the (TIE, TIE) and (Model B, TIE) subclasses, their pass-2 outcomes
    s["c2d"] = {}
    for cls in (("TIE", "TIE"), ("Model B", "TIE")):
        members = [r for r in set_rows if order_class(votes1, r["mid"]) == cls]
        s["c2d"][cls] = (len(members), Counter(outcome_class(D2[r["mid"]]) for r in members))
    # C3: paired per-order McNemar, "named the FIRST-SHOWN side", 200 cells
    b = c = 0
    cells = 0
    inval2 = 0
    for r in set_rows:
        for arm in ("fwd", "rev"):
            cells += 1
            v1 = adj(votes1.get((r["mid"], arm)))
            v2 = adj(votes2.get((r["mid"], arm)))
            inval2 += int(v2 in (None, "INVALID"))
            f1, f2 = int(v1 == "Model A"), int(v2 == "Model A")
            if f1 and not f2:
                b += 1
            elif f2 and not f1:
                c += 1
    s["c3"] = dict(b=b, c=c, p=mcnemar_exact(b, c), cells=cells, inval2=inval2)
    # P3: convention-B agreement with the checker on the matches that COMMIT in pass 2 (and convention A beside)
    kB = nB = kA = 0
    for r in set_rows:
        v = D2[r["mid"]]
        committed = (not v["pending"]) and (not v["invalid"]) and v["winner"] not in (None, "TIE", "INVALID")
        ok = int(committed and v["winner"] == r["checker_winner"])
        kA += ok
        if committed:
            nB += 1
            kB += ok
    s["p3"] = dict(kB=kB, nB=nB, kA=kA, nA=len(set_rows))
    # C4 counts over the posted pass-2 cells
    fins = Counter(v[1] or "(none)" for v in votes2.values())
    provs = Counter(v[3] or "(none)" for v in votes2.values())
    unus = sum(1 for v in votes2.values() if adj(v) == "INVALID")
    ctoks = [v[2] for v in votes2.values() if v[2] is not None and v[2] >= 0]
    s["c4"] = dict(posted=len(votes2), unusable=unus, fins=dict(fins), provs=dict(provs),
                   max_ctok=(max(ctoks) if ctoks else None),
                   trunc_sides=sum(r["trunc_a"] + r["trunc_b"] for r in set_rows),
                   state_over=sum(r["state_over_a"] + r["state_over_b"] for r in set_rows))
    return s


# ----------------------------------------------------------------------------------------------------------------
# scoring and the readout (every branch registers its tag; the selftest asserts full coverage)
# ----------------------------------------------------------------------------------------------------------------
def score_c1(s):
    """-> (key, sentence). D2 ruling (7da2ec5): the VALIDITY TRIGGERS are evaluated FIRST and PRE-EMPT the verdict; if
    any fires, C1 is UNDETERMINED (BY TRIGGER), the interval is printed but NOT scored, the falsifier is NOT evaluated.
    Only if none fires is the ONE deciding statistic (the clustered interval of R) read."""
    R = s["R"]
    lo, hi = R["lo_n"], R["hi_n"]
    if not (lo == lo and hi == hi):
        interval = "UND"
    elif lo > BAR:
        interval = "HELD"
    elif hi < BAR:
        interval = "FAILED"
    else:
        interval = "UND"
    triggers = []
    if s["usable"] < MIN_USABLE:
        triggers.append(("USABLE", "fewer than %d of the 100 yield a usable dual-order outcome: %d usable"
                         % (MIN_USABLE, s["usable"])))
    g = s["gate"]
    if not (g["ok"] and g["n_eq"] == N_CELLS and g["n_cells"] == N_CELLS):
        triggers.append(("GATE", "the byte-identity gate did not pass %d of %d: %d of %d cells equal, gate ok %s"
                         % (N_CELLS, N_CELLS, g["n_eq"], g["n_cells"], bool(g["ok"]))))
    if triggers:
        for name, _ in triggers:
            hit("C1:TRIG_%s" % name)
            if interval in ("HELD", "FAILED"):
                hit("C1:PREEMPT_%s" % name)
        return "UND_TRIGGER", ("UNDETERMINED (BY TRIGGER: %s). The trigger PRE-EMPTS the verdict (registrar ruling D2, "
                               "7da2ec5): the interval [%.4f, %.4f] is PRINTED BUT NOT SCORED%s; the falsifier is NOT "
                               "evaluated." % ("; ".join(t for _, t in triggers), lo, hi,
                                               " (it lies wholly %s %.3f; that reading is pre-empted)"
                                               % ("above" if interval == "HELD" else "below", BAR)
                                               if interval in ("HELD", "FAILED") else ""))
    if interval == "HELD":
        hit("C1:HELD")
        return "HELD", ("HELD - the flips REPRODUCE: the clustered interval [%.4f, %.4f] lies wholly above %.3f; the 0.2183 "
                        "is a stable per-match property, not boundary noise" % (lo, hi, BAR))
    if interval == "FAILED":
        hit("C1:FAILED")
        return "FAILED", ("FAILED - the flips DO NOT reproduce: the clustered interval [%.4f, %.4f] lies wholly below %.3f; "
                          "the flip set is not a stable object" % (lo, hi, BAR))
    hit("C1:UND_INTERVAL")
    return "UNDETERMINED", "UNDETERMINED (the clustered interval [%.4f, %.4f] contains %.3f)" % (lo, hi, BAR)


def falsifier_lines(c1_key, s):
    if c1_key == "FAILED":
        hit("FALS:FIRES")
        return ["FALSIFIER FIRES: the reading that the pilot's 100 order-flip ties and their one-sided (57 / 0) signature are "
                "a STABLE PER-MATCH PROPERTY of the deployed recipe on this corpus IS OVERTURNED. The 0.2183 tie rate is "
                "recorded as a MARGINAL rate generated at a noisy decision boundary; the flip SET is not a stable object. "
                "STANDING CONSEQUENCE (adopted by insertion): NO LATER TEST ON THIS CORPUS MAY RE-POST A SELECTED MATCH SET "
                "AND READ THE RESULT AS A PER-MATCH MEASUREMENT. BFCL-FINAL-STATE-SWAP's reading is tightened by insertion "
                "(a tie-rate move there is a move in a marginal rate, never in a per-match property).",
                "WHAT IT DOES NOT OVERTURN: no number of BFCL-JUDGED-PILOT (A = 0.7402, A = 0.9469, the 19 wrong-committed "
                "0.0415, the tie rate 0.2183, the marginal first-position rate 0.5862 of 870, z = 5.09 are all MARGINAL); no "
                "board, profile, tier, rung or MMLU-Pro result; not CANARY-BASELINE pass 2's 0.087 or DECOMP's 5.7%."]
    if c1_key == "HELD":
        hit("FALS:HELD")
        return ["falsifier does not fire (C1 HELD). C1 HELD overturns nothing: it establishes that the flips are "
                "reproducible and NOT that position bias (rather than template mis-fit) causes them - a stable effect is "
                "consistent with BOTH; separating them is BFCL-FINAL-STATE-SWAP's job. The record gains ONE sentence and "
                "BFCL-JUDGED-PILOT's does_not_show item on reproducibility is amended by insertion; no fidelity number."]
    if c1_key == "UNDETERMINED":
        hit("FALS:UND")
        sp = s["support"]
        return ["falsifier does not fire (C1 UNDETERMINED, a registered outcome): recorded with the measured DEFF %.3f, "
                "n_eff %.1f and MDE +-%.3f (80%% power, at R = 0.5); no further calls are bought on this question without "
                "a new registration that names a design with more support." % (sp["deff"], sp["neff"], sp["mde_plan"])]
    hit("FALS:NOT_EVALUATED")
    sp = s["support"]
    return ["falsifier NOT EVALUATED: C1 is UNDETERMINED BY TRIGGER (registrar ruling D2: a fired validity trigger pre-empts "
            "the verdict and the falsifier). Recorded as UNDETERMINED with the measured DEFF %.3f, n_eff %.1f and MDE +-%.3f."
            % (sp["deff"], sp["neff"], sp["mde_plan"])]


def band3(tag, x, lo, hi):
    if not (x == x):
        hit("%s:UND" % tag)
        return "UNDETERMINED (not estimable on this data)"
    if lo <= x <= hi:
        hit("%s:HELD" % tag)
        return "HELD"
    hit("%s:FAILED" % tag)
    return "FAILED"


def c2_lines(s):
    a, b, c = s["c2a"], s["c2b"], s["c2c"]
    L = ["  (a) " + fmt_rate("the (Model A, Model A) subclass again (Model A, Model A) in pass 2", a,
                             "denominator the 57 pass-1 (Model A, Model A) matches", s["boot"], s["seed"]),
         "  (b) " + fmt_rate("the (Model A, Model A) subclass a dual-order TIE again by any route", b,
                             "denominator the 57", s["boot"], s["seed"]),
         "  (c) " + fmt_rate("pass-2 first-position rate", c, "denominator the pass-2 NON-TIE votes of the %d cells" % N_CELLS,
                             s["boot"], s["seed"])
         + " | beside the pilot's MARGINAL %.4f of %d non-tie votes (z = %.2f; recomputed from the pilot cache %s) - NOTE OF "
           "RECORD: on this SELECTED subset the pass-1 value is 1.0 for 57 of the 100 BY CONSTRUCTION, so (c) is a "
           "REGRESSION readout and never a replication of z = 5.09"
         % (PILOT_FIRST_POS[0], PILOT_FIRST_POS[1], PILOT_FIRST_POS[2], s.get("pilot_first_str", "n/a"))]
    for cls, (n, cnt) in s["c2d"].items():
        L.append("  (d) pass-1 %s subclass: %d match(es), counted separately; pass-2 dual-order outcomes %s"
                 % (cls, n, dict(cnt)))
    ok = bool(a["n"] > 0 and b["n"] > 0 and c["n"] > 0 and len(s["c2d"]) == 2)
    if ok:
        hit("C2:HELD")
        L.append("  C2: HELD ((a)-(d) computed and printed with their denominators and intervals; NO BAR on any of them: at "
                 "n = 57 and DEFF ~3.6, n_eff ~16 and the MDE ~+-0.35)")
    else:
        hit("C2:FAILED")
        L.append("  C2: FAILED (a readout has an empty denominator: (a) n=%d, (b) n=%d, (c) n=%d; it cannot be printed with an "
                 "interval)" % (a["n"], b["n"], c["n"]))
    return L


def c3_lines(s):
    c3 = s["c3"]
    L = ["  exact two-sided McNemar on the %d (mid, arm) cells, outcome 'named the FIRST-SHOWN side' (pass 1 -> pass 2): "
         "b (first-shown in pass 1, not in pass 2) = %d, c (not -> first-shown) = %d, exact p = %.4g; pass-2 cells "
         "unusable or missing counted as not first-shown: %d | selected set, direction not verdict"
         % (c3["cells"], c3["b"], c3["c"], c3["p"], c3["inval2"])]
    if c3["cells"] == N_CELLS:
        hit("C3:HELD")
        L.append("  C3: HELD (b, c and the exact p computed and printed on the %d-cell denominator; selected set, direction "
                 "not verdict)" % N_CELLS)
    else:
        hit("C3:FAILED")
        L.append("  C3: FAILED (the cell denominator is %d, not %d)" % (c3["cells"], N_CELLS))
    return L


def c4_lines(s):
    c4, g, sp = s["c4"], s["gate"], s["support"]
    L = gate_lines(g)
    L += ["  (b) unusable rows (content_filter + length + unparsed) %d of %d posted calls (%.4f)"
          % (c4["unusable"], c4["posted"], c4["unusable"] / max(1, c4["posted"])),
          "  (c) finish_reason %s | provider fingerprint %s (expected %s)" % (c4["fins"], c4["provs"], P.EXPECTED_FINGERPRINT),
          "  (d) max completion tokens %s of the %d cap" % (c4["max_ctok"], P.MAXTOK),
          "  (e) truncated sides %d of %d, state-over-cap sides %d (expected 0 by inheritance)"
          % (c4["trunc_sides"], 2 * s["n_set"], c4["state_over"]),
          "  (f) measured DEFF for R %.3f, n_eff %.1f (beside every C1 interval above)" % (sp["deff"], sp["neff"]),
          "  (g) " + (s.get("night") or "[NIGHT] not computed")]
    ok = bool(c4["posted"] > 0 and c4["max_ctok"] is not None and s.get("night"))
    if ok:
        hit("C4:HELD")
        L.append("  C4: HELD ((a)-(g) printed)")
    else:
        hit("C4:FAILED")
        L.append("  C4: FAILED (a count could not be printed: posted %d, max completion tokens %s, night line %s)"
                 % (c4["posted"], c4["max_ctok"], "present" if s.get("night") else "absent"))
    return L


def _iv_reading(lo, hi):
    if not (lo == lo and hi == hi):
        return "not estimable"
    return "HELD-side (wholly above %.3f)" % BAR if lo > BAR else ("FAILED-side (wholly below %.3f)" % BAR if hi < BAR
                                                                 else "UNDETERMINED (contains %.3f)" % BAR)


def usable_line(s):
    """D-G5 / launch condition (E): the usable-only R WITH ITS INTERVAL beside the literal one, and whether the interval
    reading differs. Printed; decides nothing (the literal R decides, confirmed reading D4(a))."""
    u, R = s["R_u"], s["R"]
    lit, usa = _iv_reading(R["lo_n"], R["hi_n"]), _iv_reading(u["lo_n"], u["hi_n"])
    if u["n"] == 0:
        hit("USABLE:NA")
        tail = "no usable pass-2 match: the usable-only interval is not estimable"
    elif lit != usa:
        hit("USABLE:DIFFERS")
        tail = ("the usable-only interval reads %s, the literal one %s: THE READING DIFFERS - the difference is carried by "
                "the %d unusable match(es)" % (usa, lit, s["n_set"] - s["usable"]))
    else:
        hit("USABLE:SAME")
        tail = "the usable-only interval reads %s, the same as the literal one" % usa
    return ("  USABLE-ONLY ESTIMATE beside the literal one (printed, DECIDES NOTHING; the literal R decides, confirmed reading "
            "D4(a)): R_usable = %d / %d = %.4f (%d task clusters) | interval point +- 1.96 x clustered SE %.4f = [%.4f, %.4f] "
            "| percentile [%.4f, %.4f] | Wilson [%.4f, %.4f] | literal %.4f - usable-only %.4f = %+.4f is what unusable rows "
            "contribute | pending %d | %s"
            % (u["k"], u["n"], u["point"], u["q"], u["sd"], u["lo_n"], u["hi_n"], u["lo_p"], u["hi_p"], u["wlo"], u["whi"],
               R["point"], u["point"], (R["point"] - u["point"]) if u["n"] else float("nan"), s["pending"], tail))


def support_lines(s):
    sp = s["support"]
    sizes = "/".join("%d:%d" % (k, s["sizes"][k]) for k in sorted(s["sizes"]))
    if sp["deff"] == sp["deff"]:
        hit("SUPPORT:OK")
        head = ("SUPPORT AS MEASURED (beside the deciding statistic): %d matches over %d task clusters (cluster sizes "
                "size:count %s, Kish mean %.2f) | MEASURED DEFF %.3f (clustered bootstrap variance / binomial variance, the "
                "pilot's 3.60 definition) | n_eff %.1f | MDE at 80%% power, alpha .05 two-sided: +-%.3f at R = 0.5 (the "
                "registration's planning form) and +-%.3f at the measured SE"
                % (s["n_set"], s["R"]["q"], sizes, s["kish"], sp["deff"], sp["neff"],
                   sp["mde_plan"], sp["mde_meas"]))
    else:
        hit("SUPPORT:DEGENERATE")
        head = ("SUPPORT AS MEASURED: %d matches over %d task clusters (sizes %s, Kish %.2f) | DEFF NOT ESTIMABLE (R = %.4f "
                "is at the boundary, binomial variance 0) | measured MDE +-%.3f"
                % (s["n_set"], s["R"]["q"], sizes, s["kish"], s["R"]["point"], sp["mde_meas"]))
    return [head, "  planning values of record (registration SUPPORT AND MDE): DEFF %.2f -> n_eff 27.8, MDE +-0.265; "
                  "pessimistic DEFF %.1f -> n_eff 20.0, MDE +-0.313; anchors 0.695 apart" % PLANNING_DEFF]


def prediction_lines(s):
    R = s["R"]
    sp = s["support"]
    p3 = s["p3"]
    c4 = s["c4"]
    g = s["gate"]
    p3v = (p3["kB"] / p3["nB"]) if p3["nB"] else float("nan")
    unus = c4["unusable"] / max(1, c4["posted"])
    L = ["  P1 R in [0.75, 0.95] (point 0.88): %.4f -> %s" % (R["point"], band3("P1", R["point"], 0.75, 0.95)),
         "  P2 C2(a) in [0.60, 0.90] (point 0.75): %.4f of %d -> %s" % (s["c2a"]["point"], s["c2a"]["n"],
                                                                      band3("P2", s["c2a"]["point"], 0.60, 0.90)),
         "  P3 pass-2 convention-B agreement with the checker on the matches that commit in pass 2, in [0.55, 0.90] "
         "(point 0.72; DESCRIPTIVE): %d / %d = %.4f (convention A beside: %d / %d) -> %s"
         % (p3["kB"], p3["nB"], p3v, p3["kA"], p3["nA"], band3("P3", p3v, 0.55, 0.90))]
    if unus <= 0.01:
        hit("P4:HELD")
        p4 = "HELD"
    else:
        hit("P4:FAILED")
        p4 = "FAILED"
    L.append("  P4 unusable rows <= 1%% of the posted calls: %d of %d = %.4f -> %s" % (c4["unusable"], c4["posted"], unus, p4))
    p5_ok = bool(g["n_eq"] == N_CELLS and g["n_cells"] == N_CELLS and g["anchor"] == ALL_PAYLOAD_ANCHOR and g["sys_equal"]
                 and g["sys_sha"] == SYSTEM_PROMPT_SHA)
    if p5_ok:
        hit("P5:HELD")
    else:
        hit("P5:FAILED")
    L.append("  P5 the byte-identity gate passes 200 of 200 (as read under the D1 ruling: the schedule-wide payload anchor "
             "equals 951ec3a0a063b5a8 and the system prompt is byte-identical to the parent's with its own sha16 %s): %d of %d "
             "cells, anchor %s, system prompt byte-identical %s, own sha16 %s -> %s"
             % (SYSTEM_PROMPT_SHA, g["n_eq"], g["n_cells"], g["anchor"], g["sys_equal"], g["sys_sha"],
                "HELD" if p5_ok else "FAILED"))
    L.append("  P6 measured task-clustered DEFF for R in [2.5, 6.0] (point 3.8): %.3f -> %s"
             % (sp["deff"], band3("P6", sp["deff"], 2.5, 6.0)))
    return L


def readout(s):
    """-> (lines, c1_key). The text of the outcome file."""
    R = s["R"]
    L = ["=== %s: do the BFCL pilot's 100 order-flip ties reproduce on a second posting? ===" % TEST,
         "  registration %s" % REGISTRATION,
         "  pool %s | judge %s on %s | cap %d | temperature OMITTED | seed %d (provenance label + bootstrap + posting "
         "order; NOT a judge seed) | protocol: %s" % (POOL_ID, P.JUDGE_MODEL, P.PROVIDER, P.MAXTOK, SEED, PROTOCOL),
         "  %s" % s.get("provenance", "(provenance not recorded: selftest)"),
         "  pass-1 partition of the 100 (fwd vote, rev vote): %s | registered %s"
         % (dict(s["part1"]), dict(REG_PARTITION)),
         "  pass-2 partition of the 100: %s" % dict(s["part2"]),
         "",
         "=== C1 THE REPRODUCTION RATE R (primary; ONE deciding statistic: the task-clustered interval) ===",
         "  " + fmt_rate("R", R, "LITERAL denominator the 100; an unusable pass-2 match is not a TIE", s["boot"], s["seed"]),
         usable_line(s),
         "  anchors: STABLE %.3f (1 - CANARY-BASELINE pass 2's 0.087) | NOISE %.4f (the corpus's marginal tie rate) | BAR %.3f"
         % (STABLE_ANCHOR, NOISE_ANCHOR, BAR)]
    L += ["  " + x for x in support_lines(s)]
    key, sentence = score_c1(s)
    L += ["  C1: %s" % sentence,
          "  point estimate %.4f is printed and DECIDES NOTHING." % R["point"],
          "  " + TWO_HYP, "  " + ASSUMPTION, "  " + POSITION_INDEX_NOTE]
    L += ["", "=== FALSIFIER ==="] + ["  " + x for x in falsifier_lines(key, s)]
    L += ["", "=== C2 THE POSITION SIGNATURE (descriptive, no bar) ==="] + c2_lines(s)
    L += ["", "=== C3 THE PAIRED PER-ORDER STATISTIC (no bar) ==="] + c3_lines(s)
    L += ["", "=== C4 INSTRUMENT COUNTS AND THE BYTE-IDENTITY GATE ==="] + c4_lines(s)
    L += ["", "=== PREDICTIONS (registered before any code; scored explicitly) ==="] + prediction_lines(s)
    L += ["", "=== WHAT THIS RUN DOES NOT SHOW (registered) ===",
          "  (1) no 'different 100' is observed (no decisive-in-pass-1 match is re-posted); (2) nothing about WHY a flip "
          "happens (position bias, template mis-fit and corpus difficulty all predict reproduction); (3) no fidelity, no "
          "rung, no ladder, no 0.75 bar, no 'for Agents' bridge; (4) no profile cell, agent ranking, per-trajectory or "
          "process claim (57 EVAL tasks against the 120-question support rule); (5) not a calibration of the judge."]
    return L, key


# ----------------------------------------------------------------------------------------------------------------
# the cache
# ----------------------------------------------------------------------------------------------------------------
def open_cache(path=None):
    con = sqlite3.connect(path or CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, "
                "ts REAL, finish TEXT, ctokens INTEGER, provider TEXT, max_tokens INTEGER, PRIMARY KEY (mid, arm))")
    con.execute("CREATE TABLE IF NOT EXISTS posting_order (launch TEXT, seq INTEGER, mid INTEGER, arm TEXT, "
                "PRIMARY KEY (launch, seq))")
    con.commit()
    return con


def current_meta(ctx, g):
    mids = [r["mid"] for r in ctx["set_rows"]]
    return {"test": TEST, "registration": REGISTRATION, "pool_id": POOL_ID, "judge_model": P.JUDGE_MODEL,
            "provider": P.PROVIDER, "max_tokens": str(P.MAXTOK), "temperature": "omitted", "protocol": PROTOCOL,
            "reference": P.REFERENCE_FORM, "seed": str(SEED), "boot": str(BOOT), "bar": str(BAR),
            "set_mids": json.dumps(sorted(mids)), "set_sha256_16": set_sha(mids), "n_set": str(len(mids)),
            "schedule_hash": ctx["sched_hash"], "parent_module": "tools/analysis/bfcl_judged_pilot.py",
            "parent_sha256_16_lf": P.SCRIPT_SHA, "all_payload_anchor": g["anchor"], "system_prompt_sha16": g["sys_sha"],
            "system_bfcl": P.SYSTEM_BFCL, "rubric_bfcl": P.RUBRIC_BFCL,
            "dataset_sha256": ctx["shas"]["dataset"], "possible_answer_sha256": ctx["shas"]["possible_answer"],
            "script_sha256_16": SCRIPT_SHA,
            "script_sha256_16_rendering": "LF (sha256 of the file bytes with CRLF normalised to LF, first 16 hex)"}


def pin_meta(con, cur):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    old = dict(con.execute("SELECT key, value FROM run_meta"))
    if old:
        bad = [(k, old.get(k), v) for k, v in cur.items() if old.get(k) != v]
        if bad:
            raise SystemExit("[META] REFUSED: the cache was pinned under a different record (the script sha included):\n  %s"
                             % "\n  ".join("%s: pinned %r | now %r" % (k, str(a)[:80], str(b)[:80]) for k, a, b in bad))
        resumed = json.loads(old.get("resumed") or "[]") + [now]
        con.execute("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)", (json.dumps(resumed),))
    else:
        for k, v in cur.items():
            con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v))
        con.execute("INSERT INTO run_meta VALUES ('started', ?)", (now,))
    con.commit()


def truncation_guard(votes, what):
    """Refuses above 5% unusable, at the CALL level (unusable rows / posted cells) and at the MATCH level."""
    posted = len(votes)
    unus = sum(1 for v in votes.values() if adj(v) == "INVALID")
    mids = {m for m, _ in votes}
    bad_m = {m for (m, _), v in votes.items() if adj(v) == "INVALID"}
    rc, rm = unus / max(1, posted), len(bad_m) / max(1, len(mids))
    line = ("[GUARD] %s %s: unusable %d of %d posted calls (%.1f%%), %d of %d matches (%.1f%%) -> %s"
            % (TEST, what, unus, posted, 100 * rc, len(bad_m), len(mids), 100 * rm,
               "OK (<= 5%)" if (rc <= GUARD_RATE and rm <= GUARD_RATE) else "ABOVE 5%"))
    print(line, flush=True)
    return bool(rc <= GUARD_RATE and rm <= GUARD_RATE), line


# ----------------------------------------------------------------------------------------------------------------
# the modes
# ----------------------------------------------------------------------------------------------------------------
def dry_run():
    ctx = load_context()
    g = byte_gate(ctx)
    part = partition(ctx["set_rows"], ctx["votes1"])
    print("corpus %s | EVAL %s tasks %d | pilot cache %s (mode=ro&immutable=1) | pilot run_meta schedule_hash %s, seed %s"
          % (rel(P.DB), P.STRATUM, len(ctx["c"].eval_base), rel(PILOT_CACHE), ctx["meta_p"].get("schedule_hash"),
             ctx["meta_p"].get("seed")))
    print("SCHEDULE re-derived from the corpus: %d rows, hash %s (of record %s; pilot run_meta %s) | cached rows differing "
          "from the recomputation: %d" % (len(ctx["rows"]), ctx["sched_hash"], SCHEDULE_HASH_OF_RECORD,
                                          ctx["meta_p"].get("schedule_hash"), ctx["sched_diffs"]))
    print("DECIDING SUBSET (headline rows, 7-agent roster, nj / nj_a / nj_b clear): %d mids (registered %d)"
          % (len(ctx["deciding"]), N_DECIDING))
    print("THE SET (dual-order aggregation of the pilot's cached fwd / rev is TIE): %d mids (registered EXACTLY %d) | set "
          "sha256_16 %s" % (len(ctx["set_rows"]), N_SET, set_sha([r["mid"] for r in ctx["set_rows"]])))
    print("PARTITION (fwd vote, rev vote as posted) beside the registered one:")
    for cls, n in REG_PARTITION:
        print("  %-24s recomputed %3d | registered %3d%s" % (cls, part.get(cls, 0), n, "" if part.get(cls, 0) == n else "  <- DIFFERS"))
    other = {k: v for k, v in part.items() if k not in dict(REG_PARTITION)}
    print("  outside the six classes: %s | genuine order disagreements %d, double-TIEs %d"
          % (other or "none", len(ctx["set_rows"]) - part.get(("TIE", "TIE"), 0), part.get(("TIE", "TIE"), 0)))
    sizes, kish = cluster_sizes(ctx["set_rows"])
    tasks = sorted({r["task_id"] for r in ctx["set_rows"]})
    print("CLUSTERS: %d distinct tasks carry the 100 (the cluster unit of C1) | sizes size:count %s | Kish mean %.2f"
          % (len(tasks), "/".join("%d:%d" % (k, sizes[k]) for k in sorted(sizes)), kish))
    n_chk, split_bad = split_check([r["task_id"] for r in ctx["set_rows"]])
    print("SPLIT: %d scheduled tasks recomputed under split_side.tier_b %s -> %s"
          % (n_chk, split_side.NORMALISER_VERSION, "all EVAL" if not split_bad else "REFUSED: %s" % split_bad[:3]))
    print("THE 100 (mid, task, agent_a [shown first in fwd], agent_b, pass-1 fwd vote, pass-1 rev vote):")
    for r in ctx["set_rows"]:
        cls = order_class(ctx["votes1"], r["mid"])
        print("  %d  %-22s %-38s %-38s %-8s %-8s" % (r["mid"], r["task_id"], r["agent_a"], r["agent_b"], cls[0], cls[1]))
    print("PAYLOAD SHAS, cell by cell (mid, arm, this script's sha16(system + U+001F + user), the parent module's):")
    for mid, arm, own, par in g["cells"]:
        print("  %d %s %s %s %s" % (mid, arm, own, par, "=" if own == par else "MISMATCH"))
    for line in gate_lines(g):
        print(line)
    P.configure_rr()
    body = P.post_body(*assemble(ctx["set_rows"][0], "fwd", ctx)) if ctx["set_rows"] else P.post_body("s", "u")
    P.assert_body_copy(body)
    print("judge %s on %s | max_tokens %d | temperature OMITTED (body keys %s) | seed %d is NOT sent (provenance + "
          "bootstrap + posting order only)" % (P.JUDGE_MODEL, P.PROVIDER, P.MAXTOK, tuple(body), SEED))
    print("BILL: %d payloads assembled, 0 posted | --pilot %d = %d calls (the %d LOWEST mids) | --run the remaining %d | "
          "ceiling %d = expected" % (2 * len(ctx["set_rows"]), PILOT_MATCHES, 2 * PILOT_MATCHES, PILOT_MATCHES,
                                     N_CELLS - 2 * PILOT_MATCHES, N_CELLS))
    print("cache %s%s (the dry-run creates none) | outcome %s (write-once, mode x) | pilot readout %s"
          % (rel(CACHE), " (EXISTS)" if os.path.exists(CACHE) else " (new)", rel(OUT), rel(OUT_PILOT)))
    ok, st = gate_state()
    print("READY gate (not enforced by --dry-run): %s -> %s" % (st, "OPEN" if ok else "CLOSED (nothing may be posted)"))
    bad = refusals(ctx, g)
    print("REFUSALS: %s" % ("none - a posting launch would be admitted by the instrument" if not bad else "; ".join(bad)))
    print("script sha256[:16] LF-rendered %s | working-tree bytes (CRLF on this checkout) %s | parent LF %s (pinned %s)"
          % (SCRIPT_SHA, script_sha_raw(), P.SCRIPT_SHA, PARENT_SHA_PINNED))
    night_line(0, "--dry-run (0 calls)")
    print("dry run %s: 0 calls posted, no cache created" % ("OK" if not bad else "REFUSES"))
    print(dbguard_line())
    if bad:
        raise SystemExit(1)


def launch(mode, n, workers):
    """mode in {'pilot', 'run'}. Gated FIRST (nothing opened before go_gate), counted, guarded."""
    what = "--run" if mode == "run" else "--pilot %s" % n
    go_gate(what)
    if mode == "pilot" and n != PILOT_MATCHES:
        raise SystemExit("[PILOT] REFUSED: the registered pilot is --pilot %d (the %d lowest mids); got %r"
                         % (PILOT_MATCHES, PILOT_MATCHES, n))
    ctx = load_context()
    g = byte_gate(ctx)
    for line in gate_lines(g):
        print(line)
    bad = refusals(ctx, g)
    if bad:
        raise SystemExit("[REFUSED] 0 calls: %s" % "; ".join(bad))
    P.configure_rr()
    P.assert_body_copy(P.post_body("s", "u"))
    rr.load_env()
    con = open_cache()
    pin_meta(con, current_meta(ctx, g))
    set_rows = ctx["set_rows"]
    pilot_rows = set_rows[:PILOT_MATCHES]
    have = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    if mode == "run":
        pilot_cells = {(r["mid"], a) for r in pilot_rows for a in ("fwd", "rev")}
        if not pilot_cells <= have:
            raise SystemExit("[GUARD] REFUSED: --run needs the %d pilot cells cached and read by the truncation guard first "
                             "(%d of %d cached)" % (len(pilot_cells), len(pilot_cells & have), len(pilot_cells)))
        ok, _ = truncation_guard(raw_votes(con, "verdicts", [r["mid"] for r in set_rows]), "cached before --run")
        if not ok:
            raise SystemExit("[GUARD] REFUSED: above 5% unusable; nothing more is posted.")
    target = pilot_rows if mode == "pilot" else set_rows
    todo = [(r, a) for r in target for a in ("fwd", "rev") if (r["mid"], a) not in have]
    random.Random("%d:%s" % (SEED, what)).shuffle(todo)                 # posting order: seed 137, recorded
    stamp = "%s %s" % (what, time.strftime("%Y-%m-%d %H:%M:%S"))
    con.executemany("INSERT INTO posting_order VALUES (?,?,?,?)", [(stamp, i, r["mid"], a) for i, (r, a) in enumerate(todo)])
    con.commit()
    night_line(len(todo), what)
    jobs = []
    for r, arm in todo:
        s, u = assemble(r, arm, ctx)
        jobs.append((r["mid"], arm, s, u))
    print("%s %s: %d calls to post (target %d matches; %d cells already cached) | workers %d | cache %s"
          % (TEST, what, len(jobs), len(target), 2 * len(target) - len(todo), workers, rel(CACHE)), flush=True)
    ok_n, err, fins = post_counted(con, jobs, workers, what)
    truncation_guard(raw_votes(con, "verdicts", [r["mid"] for r in target]), what)
    print("done: ok %d, errors %d (errors are never cached). --analyze for the readout." % (ok_n, err), flush=True)
    print(dbguard_line())


def analyze(boot=BOOT):
    ctx = load_context()
    if not os.path.exists(CACHE):
        raise SystemExit("no cache at %s: nothing judged, nothing written" % rel(CACHE))
    g = byte_gate(ctx)
    con = sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)
    try:
        meta = dict(con.execute("SELECT key, value FROM run_meta"))
        mids = [r["mid"] for r in ctx["set_rows"]]
        votes2 = raw_votes(con, "verdicts", mids)
        D2 = P.dual(con, ctx["set_rows"])
    finally:
        con.close()
    night_line(0, "--analyze (0 calls)")
    problems = []
    if meta.get("set_sha256_16") != set_sha(mids):
        problems.append("the cache's pinned set %s is not the re-derived %s" % (meta.get("set_sha256_16"), set_sha(mids)))
    if meta.get("script_sha256_16") != SCRIPT_SHA:
        problems.append("the cache was produced by script LF sha %s, this script is %s" % (meta.get("script_sha256_16"), SCRIPT_SHA))
    missing = N_CELLS - len(votes2)
    if missing:
        problems.append("PARTIAL: %d of %d cells not cached" % (missing, N_CELLS))
    s = compute(ctx["set_rows"], ctx["votes1"], votes2, D2, g, len(votes2), boot, SEED)
    s["night"] = _NIGHT_LINE
    s["pilot_first_str"] = "%d / %d = %.4f" % (ctx["pilot_first"][0], ctx["pilot_first"][1],
                                                ctx["pilot_first"][0] / max(1, ctx["pilot_first"][1]))
    s["provenance"] = ("cache %s (mode=ro) | run_meta script_sha256_16 %s (LF) | this script LF %s / working-tree %s | "
                       "parent LF %s | started %s | resumed %s" % (rel(CACHE), meta.get("script_sha256_16"), SCRIPT_SHA,
                                                                   script_sha_raw(), P.SCRIPT_SHA, meta.get("started"),
                                                                   meta.get("resumed", "-")))
    L, _ = readout(s)
    if problems:
        L.append("  NO OUTCOME OF RECORD (refused: %s)" % "; ".join(problems))
    txt = "\n".join(L) + "\n"
    print(txt)
    write_outcome(txt, problems)
    print(dbguard_line())


def write_outcome(txt, problems, out=None, out_pilot=None):
    out, out_pilot = out or OUT, out_pilot or OUT_PILOT
    if problems:
        with open(out_pilot, "w", encoding="utf-8") as f:
            f.write(txt)
        print("PARTIAL / PILOT readout written to %s; the outcome of record is untouched" % rel(out_pilot))
        return "pilot"
    try:
        with open(out, "x", encoding="utf-8") as f:                    # WRITE-ONCE: mode x, never "w"
            f.write(txt)
    except FileExistsError:
        print("REFUSED: %s exists; the outcome of record is WRITE-ONCE and is not overwritten." % rel(out))
        return "exists"
    print("written (write-once): %s" % rel(out))
    return "written"


def cli_launch_shapes(pilot_n=12, workers=8):
    """The argument shapes the CLI passes to launch(), READ FROM THIS FILE'S __main__ DISPATCH with ast."""
    import ast as _ast
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    tree = _ast.parse(src)
    mains = [nd for nd in tree.body if isinstance(nd, _ast.If) and "__main__" in _ast.dump(nd.test)]
    assert len(mains) == 1, "the __main__ dispatch block could not be located"
    ns = argparse.Namespace(selftest=False, dry_run=False, pilot=pilot_n, run=True, analyze=False, workers=workers,
                            draws=BOOT)
    out = []
    for nd in _ast.walk(mains[0]):
        if isinstance(nd, _ast.Call) and isinstance(nd.func, _ast.Name) and nd.func.id == "launch":
            out.append(tuple(eval(compile(_ast.Expression(arg), "<cli-dispatch>", "eval"), globals(), {"a": ns})
                             for arg in nd.args))
    return out


# ----------------------------------------------------------------------------------------------------------------
# --selftest: synthetic fixtures under tempfile.mkdtemp(); no DB of record, no network, 0 calls
# ----------------------------------------------------------------------------------------------------------------
def _synthetic(n_tasks, p2_rule, tmp, seed=1):
    """A synthetic 100-match set with the registered pass-1 partition, a synthetic pass-1 table and a pass-2 table filled
    by p2_rule(i, row) -> (fwd vote, rev vote, finish). Written to <tmp>/bfcl_flip_reseed.db (a whitelisted basename)."""
    classes = [c for c, n in REG_PARTITION for _ in range(n)]
    rows = []
    for i in range(N_SET):
        rows.append(dict(mid=700_000_000 + i, task_id="multi_turn_base_%d" % (i % n_tasks), agent_a="a%d" % (i % 3),
                         agent_b="b%d" % (i % 4), checker_winner=("a%d" % (i % 3)) if i % 2 else ("b%d" % (i % 4)),
                         nj="", nj_a="", nj_b="", trunc_a=0, trunc_b=0, state_over_a=0, state_over_b=0))
    path = os.path.join(tmp, CACHE_DB_NAME)
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    for t in ("p1", "verdicts"):
        con.execute("CREATE TABLE %s (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, ts REAL, "
                    "finish TEXT, ctokens INTEGER, provider TEXT, max_tokens INTEGER, PRIMARY KEY (mid, arm))" % t)
    for i, r in enumerate(rows):
        f, v = classes[i]
        for arm, vote in (("fwd", f), ("rev", v)):
            con.execute("INSERT INTO p1 VALUES (?,?,?,?,?,?,?,?,?,?,?)", (r["mid"], arm, vote, 0.8, 0, "", 0, "stop", 300,
                                                                        P.EXPECTED_FINGERPRINT, P.MAXTOK))
        out = p2_rule(i, r)
        if out is None:
            continue
        fv, rv, fin = out
        for arm, vote in (("fwd", fv), ("rev", rv)):
            con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?,?)", (r["mid"], arm, vote, 0.8, int(vote == "INVALID"),
                                                                              "", 0, fin, 350, P.EXPECTED_FINGERPRINT, P.MAXTOK))
    con.commit()
    return rows, con


def _run_synthetic(rows, con, gate_ok=True, night="[NIGHT] selftest"):
    mids = [r["mid"] for r in rows]
    v1 = raw_votes(con, "p1", mids)
    v2 = raw_votes(con, "verdicts", mids)
    D1 = P.dual(con, rows, "p1")
    assert all(D1[m]["winner"] == "TIE" for m in mids), "the synthetic pass 1 must be all dual-order TIE"
    D2 = P.dual(con, rows, "verdicts")
    g = dict(ok=gate_ok, anchor=ALL_PAYLOAD_ANCHOR if gate_ok else "0" * 16, n_eq=N_CELLS if gate_ok else N_CELLS - 1,
             n_cells=N_CELLS, mism=[] if gate_ok else ["mid 1 fwd: synthetic"], sys_equal=True, sys_sha=SYSTEM_PROMPT_SHA,
             slots_ok=True, sched_ok=True, leak_checks=N_CELLS)
    s = compute(rows, v1, v2, D2, g, len(v2), 400, SEED)
    s["night"] = night
    return s


# ----------------------------------------------------------------------------------------------------------------
# selftest helpers for the READY review's conditions (fdd6a99 / a45cdd8): the go gate's CONTENT check, refusals(),
# the read-only corpus, the counted night ledger. Fixtures only under the selftest's temp dir.
# ----------------------------------------------------------------------------------------------------------------
def _fixture_corpus(tmp, task_ids, train=()):
    """A synthetic corpus DB (tasks table only) under tmp; every task EVAL under split_side.tier_b unless in `train`.
    Created with the TRUE connect (a fixture write, asserted inside tmp); read back ONLY through the guard."""
    path = os.path.join(tmp, CORPUS_DB_NAME)
    assert os.path.abspath(path).startswith(os.path.abspath(tmp))
    if os.path.exists(path):
        os.remove(path)
    con = _TRUE_CONNECT(path)
    con.execute("CREATE TABLE tasks (task_id TEXT, family_id TEXT, content_key TEXT, side TEXT)")
    k = 0
    for t in sorted(set(task_ids)):
        while split_side.tier_b("fam%d" % k, "") != split_side.EVAL:
            k += 1
        con.execute("INSERT INTO tasks VALUES (?,?,?,?)", (t, "fam%d" % k, "", "TRAIN" if t in train else "EVAL"))
        k += 1
    con.commit()
    con.close()
    return path


def _selftest_go_gate(tmp):
    """Condition 1: the gate PARSES the READY file. Pass and refusal branches both executed; the parsed verdict and the
    sha are printed on both."""
    import contextlib
    import io
    global READY
    saved_ready, saved_git, saved_env = READY, P.git_tracked_clean, os.environ.get(GO_ENV)
    try:
        P.git_tracked_clean = lambda path: (True, True, "selftest")
        os.environ[GO_ENV] = GO_VALUE
        READY = os.path.join(tmp, "READY_selftest.md")
        good = ("# READY-WITH-CONDITIONS: %s instrument LF %s (selftest)\n\nbody\n" % (TEST, SCRIPT_SHA),
                "**READY**: %s, script LF sha16 %s\n" % (TEST, SCRIPT_SHA))
        for text in good:
            open(READY, "w", encoding="utf-8").write(text)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                go_gate("selftest")
            out = buf.getvalue()
            assert "OPEN" in out and "parsed verdict" in out and SCRIPT_SHA in out and "True" in out, out
        bad = (("# NOT READY: %s instrument LF %s\n" % (TEST, SCRIPT_SHA), "the verdict is 'NOT READY'"),
               ("# READY: %s instrument LF %s\n" % (TEST, "0" * 16), "does not name this script's LF sha16"),
               ("# READY: SOME-OTHER-TEST instrument LF %s\n" % SCRIPT_SHA, "does not name %s" % TEST),
               ("# READY: %s LF %s\n\n## NOT READY: a later verdict\n" % (TEST, SCRIPT_SHA), "a NOT READY verdict line"),
               ("A review of %s at %s with no verdict line.\n" % (TEST, SCRIPT_SHA), "no verdict line"),
               # D-G1: the OLD sha on the verdict line, the NEW sha only in the body
               ("# READY: %s instrument LF %s\n\nthe new sha %s is mentioned here\n" % (TEST, "0" * 16, SCRIPT_SHA),
                "the verdict line does not name this script's LF sha16"),
               # D-G2: a verdict only inside a fenced block
               ("Quoted from an earlier review:\n```\n# READY: %s instrument LF %s\n```\n" % (TEST, SCRIPT_SHA),
                "no verdict line"),
               ("~~~markdown\n**READY**: %s, LF %s\n~~~\n" % (TEST, SCRIPT_SHA), "no verdict line"))
        for text, why in bad:
            open(READY, "w", encoding="utf-8").write(text)
            try:
                go_gate("selftest")
                raise AssertionError("the go gate opened on %r" % text[:60])
            except SystemExit as e:
                assert "[READY]" in str(e) and "CONTENT REFUSES" in str(e) and why in str(e) and "parsed verdict" in str(e), str(e)
        return len(good), len(bad)
    finally:
        READY, P.git_tracked_clean = saved_ready, saved_git
        if saved_env is None:
            os.environ.pop(GO_ENV, None)
        else:
            os.environ[GO_ENV] = saved_env


def _selftest_corpus_ro(tmp):
    """Condition 5(a): the corpus basename is admitted ONLY as mode=ro&immutable=1."""
    p = os.path.join(tmp, CORPUS_DB_NAME).replace("\\", "/")
    n = 0
    for args, kw in (((p,), {}), (("file:%s?mode=rwc" % p,), dict(uri=True)), (("file:%s?mode=ro" % p,), dict(uri=True)),
                     (("file:%s?mode=ro&immutable=1&mode=rw" % p,), dict(uri=True)), (("file:%s?mode=ro&immutable=1" % p,), {})):
        try:
            sqlite3.connect(*args, **kw)
            raise AssertionError("the DB guard admitted the corpus as %r %r" % (args, kw))
        except SystemExit as e:
            assert "[DBGUARD] REFUSED" in str(e) and "corpus" in str(e), str(e)
            n += 1
    return n


def _selftest_post_counted(tmp):
    """Condition 5(c): errored calls are counted and the ledger row is written in a `finally`, even on a crash."""
    global NIGHT_LEDGER
    saved_ledger, real = NIGHT_LEDGER, rr.call_judge_full
    NIGHT_LEDGER = os.path.join(tmp, "night_posted.json")
    cpath = os.path.join(tmp, CACHE_DB_NAME)
    if os.path.exists(cpath):
        os.remove(cpath)
    con = open_cache(cpath)

    def fake(system, user, retries=6):
        if "boom" in user:
            raise RuntimeError("synthetic transport failure after posting")
        return ('{"winner": "TIE", "confidence": 0.7}', P.EXPECTED_FINGERPRINT, 12, 0.0, "stop", None)

    def fake_wrong_fp(system, user, retries=6):
        return ('{"winner": "TIE", "confidence": 0.7}', "azure:some-other-deployment", 12, 0.0, "stop", None)
    try:
        rr.call_judge_full = fake
        ok_n, err, _ = post_counted(con, [(1, "fwd", "s", "u1"), (1, "rev", "s", "u2"), (2, "fwd", "s", "boom")], 2, "st-post")
        rows = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
        assert (ok_n, err) == (2, 1) and rows[-1]["launch"] == "st-post" and rows[-1]["calls"] == 3, (ok_n, err, rows)
        assert rr.call_judge_full is fake, "post_counted must restore the call it wrapped"
        rr.call_judge_full = fake_wrong_fp
        try:
            post_counted(con, [(3, "fwd", "s", "u3")], 1, "st-crash")
            raise AssertionError("a fingerprint mismatch did not stop the run")
        except SystemExit as e:
            assert "[FINGERPRINT]" in str(e), str(e)[:200]
        rows = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
        assert rows[-1]["launch"] == "st-crash" and rows[-1]["calls"] == 1, rows
        assert con.execute("SELECT COUNT(*) FROM verdicts WHERE mid = 3").fetchone()[0] == 0
    finally:
        rr.call_judge_full = real
        NIGHT_LEDGER = saved_ledger
        con.close()
        os.remove(cpath)
    return 2


def _selftest_refusals(tmp):
    """Condition 2: refusals() EXECUTED on the registered context ([]) and on each refusing context."""
    roster = P.HEADLINE_ROSTER
    deciding = [dict(mid=700_000_000 + i, task_id="multi_turn_base_%d" % (i % 49), agent_a=roster[i % 7],
                     agent_b=roster[(i + 1) % 7], checker_winner=roster[i % 7], nj="", nj_a="", nj_b="")
                for i in range(N_DECIDING)]
    classes = [c for c, n in REG_PARTITION for _ in range(n)]
    set_rows = deciding[:N_SET]
    votes1 = {(r["mid"], arm): (v, "stop", 1, P.EXPECTED_FINGERPRINT)
              for r, cls in zip(set_rows, classes) for arm, v in zip(("fwd", "rev"), cls)}
    meta_p = dict(judge_model=P.JUDGE_MODEL, max_tokens=str(P.MAXTOK), temperature="omitted", seed="42", pool_id=POOL_ID)
    ctx = dict(deciding=deciding, set_rows=set_rows, votes1=votes1, meta_p=meta_p)
    db = _fixture_corpus(tmp, [r["task_id"] for r in deciding])
    ok_g = dict(ok=True)
    assert refusals(ctx, ok_g, db) == [], refusals(ctx, ok_g, db)
    aa = [r for r, cls in zip(set_rows, classes) if cls == ("Model A", "Model A")][0]
    v5601 = dict(votes1)
    v5601[(aa["mid"], "fwd")] = ("Model B", "stop", 1, "")
    v5601[(aa["mid"], "rev")] = ("Model B", "stop", 1, "")
    off = [dict(r) for r in set_rows]
    off[0]["agent_a"] = P.SELF_PREF_AGENT
    cases = ((dict(ctx, set_rows=set_rows[:99]), ok_g, "yields 99 mids"),
             (dict(ctx, votes1=v5601), ok_g, "partition class"),
             (dict(ctx, deciding=deciding[:-1]), ok_g, "deciding subset is 457"),
             (ctx, dict(ok=False), "byte-identity gate did not pass"),
             (dict(ctx, meta_p=dict(meta_p, seed="137")), ok_g, "pilot run_meta seed"),
             (dict(ctx, set_rows=off), ok_g, "off the 7-agent headline roster"))
    for c, g, why in cases:
        bad = refusals(c, g, db)
        assert any(why in b for b in bad), (why, bad)
    db = _fixture_corpus(tmp, [r["task_id"] for r in deciding], train={set_rows[5]["task_id"]})
    assert any(b.startswith("SPLIT:") for b in refusals(ctx, ok_g, db)), "a TRAIN-side task must refuse"
    os.remove(db)
    return 1 + len(cases) + 1


def selftest():
    tmp = tempfile.mkdtemp(prefix="bfcl_flip_reseed_selftest_")
    n_opened_before = len(_OPENED)
    BRANCHES_HIT.clear()
    # 1. the DB guard: forbidden names, a foreign verdict cache, the pilot cache opened writable or without immutable
    for bad_db in P.FORBIDDEN_DB_BASENAMES + ("rejudge_grok.db",):
        try:
            sqlite3.connect(os.path.join(tmp, bad_db))
            raise AssertionError("the DB guard allowed %s" % bad_db)
        except SystemExit as e:
            assert "[DBGUARD]" in str(e)
    for bad_open in ((os.path.join(tmp, PILOT_DB_NAME),), ("file:%s?mode=ro" % os.path.join(tmp, PILOT_DB_NAME).replace("\\", "/"),)):
        try:
            sqlite3.connect(*bad_open, uri=True)
            raise AssertionError("the DB guard allowed the pilot cache as %r" % (bad_open,))
        except SystemExit as e:
            assert "mode=ro&immutable=1" in str(e)
    assert sqlite3.connect is _guarded_connect and getattr(sqlite3.connect, "_true_connect", None) is _TRUE_CONNECT
    # 2. the parent pin, the body copy, the omitted temperature
    assert P.SCRIPT_SHA == PARENT_SHA_PINNED
    P.configure_rr()
    b = P.post_body("s", "u")
    P.assert_body_copy(b)
    assert "temperature" not in b and "seed" not in b and rr.payload_body("s", "u") == b
    # 3. the system prompt is the parent's, byte for byte (zero DB: prompt_v2 + the two slot constants)
    assert system_prompt() == P.system_prompt() and sha16(system_prompt()) == SYSTEM_PROMPT_SHA, sha16(system_prompt())
    # 4. the all-payload anchor reproduces the review's recipe (docs/reviews/..._post.md row 7e) on synthetic payloads
    fake_rows = [dict(mid=5), dict(mid=9)]
    pay = {5: ("S", "u1", "u2"), 9: ("S", "v1", "v2")}
    h = hashlib.sha256()
    for r in fake_rows:
        s_, a_, b_ = pay[r["mid"]]
        h.update(("%d|" % r["mid"]).encode("utf-8")); h.update(s_.encode("utf-8"))
        h.update(a_.encode("utf-8")); h.update(b_.encode("utf-8"))
    assert all_payload_anchor(fake_rows, lambda r: pay[r["mid"]]) == h.hexdigest()[:16]
    assert all_payload_anchor(fake_rows, lambda r: pay[r["mid"]]) != all_payload_anchor(fake_rows[::-1], lambda r: pay[r["mid"]])
    # 5. McNemar exact, Wilson, the set sha
    assert mcnemar_exact(0, 0) == 1.0 and abs(mcnemar_exact(10, 0) - 2 / 1024) < 1e-12 and abs(mcnemar_exact(5, 5) - 1.0) < 1e-12
    assert abs(mcnemar_exact(42, 14) - 2 * sum(math.comb(56, i) for i in range(15)) / 2 ** 56) < 1e-15
    assert set_sha([3, 1, 2]) == set_sha([1, 2, 3])
    # 6. write-once: the second write REFUSES, the pilot readout is overwritable
    out, outp = os.path.join(tmp, "outcome.txt"), os.path.join(tmp, "pilot.txt")
    assert write_outcome("one\n", [], out, outp) == "written"
    assert write_outcome("two\n", [], out, outp) == "exists" and open(out, encoding="utf-8").read() == "one\n"
    assert write_outcome("p\n", ["partial"], out, outp) == "pilot" and write_outcome("q\n", ["partial"], out, outp) == "pilot"
    # 7. run_meta pinning refuses ANY changed key, the script sha included
    con = open_cache(os.path.join(tmp, CACHE_DB_NAME))
    pin_meta(con, {"a": "1", "script_sha256_16": "x"})
    pin_meta(con, {"a": "1", "script_sha256_16": "x"})
    for changed in ({"a": "2", "script_sha256_16": "x"}, {"a": "1", "script_sha256_16": "y"}):
        try:
            pin_meta(con, changed)
            raise AssertionError("pin_meta accepted %r" % changed)
        except SystemExit as e:
            assert "[META] REFUSED" in str(e)
    con.close()
    os.remove(os.path.join(tmp, CACHE_DB_NAME))
    # 8. the truncation guard, both branches
    okv = {(1, "fwd"): ("TIE", "stop", 1, ""), (1, "rev"): ("Model A", "stop", 1, "")}
    badv = dict(okv); badv[(2, "fwd")] = ("INVALID", "stop", 1, ""); badv[(2, "rev")] = ("Model A", "length", 1, "")
    assert bool(truncation_guard(okv, "selftest")[0])
    assert not bool(truncation_guard(badv, "selftest")[0])
    # 9. the READY gate and the night ceiling
    global NIGHT_LEDGER, CACHE
    saved = os.environ.pop(GO_ENV, None)
    sl, sc = NIGHT_LEDGER, CACHE
    try:
        try:
            go_gate("selftest")
            raise AssertionError("the gate did not refuse without %s" % GO_ENV)
        except SystemExit as e:
            assert "[READY]" in str(e) and "refused" in str(e)
        NIGHT_LEDGER = os.path.join(tmp, "night.json")
        CACHE = os.path.join(tmp, CACHE_DB_NAME)
        json.dump([{"test": "x", "launch": "y", "calls": 13990, "ts": "t"}], open(NIGHT_LEDGER, "w", encoding="utf-8"))
        night_line(10, "selftest")
        try:
            night_line(11, "selftest")
            raise AssertionError("the night ceiling did not refuse")
        except SystemExit as e:
            assert "[NIGHT] REFUSED" in str(e)
        # 10. every CLI launch shape reaches go_gate FIRST and is refused there with its label
        shapes = cli_launch_shapes(pilot_n=12, workers=8)
        assert sorted(sh[0] for sh in shapes) == ["pilot", "run"], shapes
        for sh in shapes:
            try:
                launch(*sh)
                raise AssertionError("launch%r was not refused by go_gate" % (sh,))
            except SystemExit as e:
                label = "--run" if sh[0] == "run" else "--pilot %s" % sh[1]
                assert "[READY]" in str(e) and label in str(e), str(e)[:160]
    finally:
        NIGHT_LEDGER, CACHE = sl, sc
        if saved is not None:
            os.environ[GO_ENV] = saved
    # 11. END-TO-END readouts on synthetic caches: every C1 branch, the falsifier, C2-C4, the predictions
    texts = {}
    scen = {
        "held": (lambda i, r: ("Model A", "Model A", "stop")),                                   # all TIE again
        "failed": (lambda i, r: ("Model A", "Model B", "stop")),                                 # none TIE (consistent)
        "und_interval": (lambda i, r: ("Model A", "Model A", "stop") if i % 7 < 4 else ("Model B", "Model A", "stop")),
        "und_trigger": (lambda i, r: ("INVALID", "Model A", "stop") if i % 7 == 0 else          # 15 unusable -> 85 < 90
                        (("Model A", "Model A", "stop") if i % 7 < 5 else ("Model B", "Model A", "stop"))),
        "overlap": (lambda i, r: ("INVALID", "Model A", "stop") if i < 15 else ("Model A", "Model A", "stop")),
        "partial": (lambda i, r: None if i >= 12 else ("Model A", "Model A", "stop")),
    }
    for name, rule in scen.items():
        rows, con = _synthetic(20, rule, tmp)
        s = _run_synthetic(rows, con, night=None if name == "partial" else "[NIGHT] selftest line")
        con.close()
        L, key = readout(s)
        texts[name] = (key, "\n".join(L), s)
    assert texts["held"][0] == "HELD" and "FALSIFIER" in texts["held"][1] and "falsifier does not fire (C1 HELD)" in texts["held"][1]
    assert texts["failed"][0] == "FAILED" and "FALSIFIER FIRES" in texts["failed"][1]
    assert "NO LATER TEST ON THIS CORPUS MAY RE-POST A SELECTED MATCH SET" in texts["failed"][1]
    assert texts["und_interval"][0] == "UNDETERMINED" and "contains 0.566" in texts["und_interval"][1]
    assert texts["und_trigger"][0] == "UND_TRIGGER" and "BY TRIGGER: fewer than 90" in texts["und_trigger"][1]
    assert "falsifier NOT EVALUATED" in texts["und_trigger"][1] and "FALSIFIER FIRES" not in texts["und_trigger"][1]
    # the usable trigger PRE-EMPTS an interval wholly ABOVE the bar (R = 0.85 on 85 usable)
    assert texts["overlap"][0] == "UND_TRIGGER" and "wholly above 0.566; that reading is pre-empted" in texts["overlap"][1]
    assert "falsifier NOT EVALUATED" in texts["overlap"][1] and "C1: HELD" not in texts["overlap"][1]
    # the usable trigger PRE-EMPTS an interval wholly BELOW the bar (the partial cache: R = 0.12 on 12 usable)
    assert texts["partial"][0] == "UND_TRIGGER" and "wholly below 0.566; that reading is pre-empted" in texts["partial"][1]
    assert "FALSIFIER FIRES" not in texts["partial"][1]
    assert texts["held"][2]["R"]["point"] == 1.0 and texts["failed"][2]["R"]["point"] == 0.0
    for key_, txt, s in texts.values():
        for must in (TWO_HYP, ASSUMPTION, POSITION_INDEX_NOTE, "selected set, direction not verdict", "SUPPORT AS MEASURED",
                     "REGRESSION readout", "[BYTE-GATE] (A)", "P6 measured", "USABLE-ONLY ESTIMATE"):
            assert must in txt, "the readout lost the sentence of record %r" % must[:60]
    # gate failure with an interval that straddles -> UNDETERMINED by trigger; with an interval above -> still UNDETERMINED
    # by trigger (pre-empted), never HELD
    rows, con = _synthetic(20, scen["und_interval"], tmp)
    s = _run_synthetic(rows, con, gate_ok=False)
    con.close()
    assert readout(s)[1] == "UND_TRIGGER" and "BY TRIGGER: the byte-identity gate did not pass" in "\n".join(readout(s)[0])
    rows, con = _synthetic(20, scen["held"], tmp)
    s = _run_synthetic(rows, con, gate_ok=False)
    con.close()
    txt = "\n".join(readout(s)[0])
    assert readout(s)[1] == "UND_TRIGGER" and "wholly above 0.566; that reading is pre-empted" in txt   # the gate pre-empts HELD
    assert "falsifier NOT EVALUATED" in txt
    #    EACH trigger pre-empts an interval wholly on EACH side of the bar (D2), on crafted numbers through score_c1
    base0 = texts["und_interval"][2]
    for iv, side in ((dict(base0["R"], lo_n=0.80, hi_n=0.95), "above"), (dict(base0["R"], lo_n=0.10, hi_n=0.30), "below")):
        for trig in (dict(usable=80), dict(gate=dict(base0["gate"], ok=False, n_eq=N_CELLS - 1))):
            t = dict(base0, R=iv)
            t.update(trig)
            k, sentence = score_c1(t)
            assert k == "UND_TRIGGER" and "BY TRIGGER" in sentence and "wholly %s 0.566; that reading is pre-empted" % side \
                in sentence, sentence
            assert falsifier_lines(k, t)[0].startswith("falsifier NOT EVALUATED")
    # 12. the remaining prediction / support branches by direct scoring on crafted numbers (the same functions readout uses)
    base = texts["und_interval"][2]
    for p1 in (0.88, 0.10, float("nan")):
        band3("P1", p1, 0.75, 0.95)
    for p in (0.75, 0.2, float("nan")):
        band3("P2", p, 0.60, 0.90)
        band3("P3", p, 0.55, 0.90)
    for d in (3.8, 9.0, float("nan")):
        band3("P6", d, 2.5, 6.0)
    s_bad = dict(base, c4=dict(base["c4"], unusable=50, posted=200))
    prediction_lines(s_bad)
    s_c = dict(base, c2a=dict(base["c2a"], n=0), c3=dict(base["c3"], cells=24), night=None)
    c2_lines(s_c); c3_lines(s_c); c4_lines(s_c)
    #    D-G5: the usable-only line, each branch, on crafted numbers (the same function readout uses)
    iv = lambda lo, hi, n: dict(base["R"], lo_n=lo, hi_n=hi, n=n, k=n, point=(lo + hi) / 2)          # noqa: E731
    assert "THE READING DIFFERS" in usable_line(dict(base, R=iv(0.40, 0.70, 100), R_u=iv(0.60, 0.80, 85), usable=85))
    assert "the same as the literal one" in usable_line(dict(base, R=iv(0.60, 0.90, 100), R_u=iv(0.70, 0.95, 90)))
    assert "not estimable" in usable_line(dict(base, R_u=dict(base["R_u"], n=0)))
    n_gate_ok, n_gate_bad = _selftest_go_gate(tmp)
    n_ref = _selftest_refusals(tmp)
    n_ro = _selftest_corpus_ro(tmp)
    n_post = _selftest_post_counted(tmp)
    print("selftest review conditions: go gate %d opening READY texts + %d refusing ones (NOT READY, an older sha, another "
          "test, a later NOT READY line, no verdict line, the old sha on the verdict line with the new one in the body, "
          "a verdict only inside a ``` / ~~~ fence) | refusals() on the registered context + %d refusing contexts | "
          "the corpus refused in %d non-read-only forms | the night ledger counted with errors and on a crash (%d cases)"
          % (n_gate_ok, n_gate_bad, n_ref - 1, n_ro, n_post))
    missing = sorted(ALL_BRANCHES - BRANCHES_HIT)
    assert not missing, "print branches never executed by the selftest: %s" % missing
    # 13. the selftest opened nothing but its own temp fixtures
    opened = _OPENED[n_opened_before:]
    tmp_norm = os.path.normcase(os.path.abspath(tmp)).replace("\\", "/")
    for p in opened:
        pp = os.path.normcase(os.path.abspath(p.split("?", 1)[0].replace("file:", ""))).replace("\\", "/")
        assert p == ":memory:" or pp.startswith(tmp_norm), "the selftest opened a path outside its temp dir: %s" % p
    print("selftest OK: %d of %d declared print branches EXECUTED (criteria C1-C4, the falsifier, P1-P6, support), "
          "coverage asserted complete | DB guard (forbidden names, the pilot cache refused without mode=ro&immutable=1, "
          "idempotent wrapper) | parent pin %s | body copy vs rr.payload_body, no temperature, no seed | system prompt == "
          "parent's | the review's all-payload recipe | exact McNemar | write-once (mode x) refuses a second write | "
          "run_meta refuses any changed key incl. the script sha | truncation guard both branches | READY gate | night "
          "ceiling | CLI shapes %s each refused at go_gate | %d sqlite opens, all inside %s | 0 calls"
          % (len(BRANCHES_HIT), len(ALL_BRANCHES), PARENT_SHA_PINNED, ", ".join("launch%r" % (sh,) for sh in shapes),
             len(opened), tmp))
    print(dbguard_line())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="%s - %s" % (TEST, REGISTRATION))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="post the %d LOWEST mids of the 100 (%d calls); gated" % (PILOT_MATCHES, 2 * PILOT_MATCHES))
    ap.add_argument("--run", action="store_true", help="post every remaining cell; gated; needs the pilot cached")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--draws", type=int, default=BOOT)
    a = ap.parse_args()
    print("[POOL] %s - BFCL pool of record (%s; verified against the pool file and the corpus by every mode that reads "
          "data; --selftest reads no file of record)" % (POOL_ID, TEST), flush=True)
    if a.selftest:
        selftest()
    elif a.dry_run:
        dry_run()
    elif a.pilot is not None:
        launch("pilot", a.pilot, a.workers)
    elif a.run:
        launch("run", None, a.workers)
    elif a.analyze:
        analyze(a.draws)
    else:
        ap.print_help()
