"""BFCL-FINAL-STATE-SWAP - does the INHERITED verify-first block's "final answer" furniture explain the BFCL pilot's
indecision? One arm, four literal strings changed, the TIE RATE as the primary endpoint (judged; 916 calls, 458
matches). REGISTERED 2026-09-23 BEFORE ANY CODE OR CALL in docs/judge_v2_program.md L12315-L12598 (heading L12316),
commit ca3a7cc; record docs/agents/results/BFCL-FINAL-STATE-SWAP.json. CLOSED-LINE RULING of record:
docs/agents/leads/2026-09-23_bfcl_final_state_swap_ruling.md (1470fe8) - OPEN on DENOTATION FAILURE, conditional on the
DANGLING-REFERENT fence F1-F5 and the riders R1 / R2, all BUILT IN below. An INDEPENDENT test: NOT an arm of
BFCL-FLIP-RESEED, not its control, not controlled by it (own cache, own run_meta, own script sha, own outcome file).

  python tools/analysis/bfcl_final_state_swap.py --selftest   synthetic fixtures under tempfile.mkdtemp(); opens no DB of
                                                              record, no network, 0 calls; every criterion, prediction,
                                                              falsifier and rider print branch EXECUTED, coverage asserted
  python tools/analysis/bfcl_final_state_swap.py --dry-run    ZERO CALLS: the pool id first; the 458 re-derived (REFUSES
                                                              unless 458); the FOUR replacements with before / after and
                                                              their match counts; the FULL character diff of the two
                                                              system prompts and the new sha16; the F2 gate over the 916
                                                              user turns; the schedule hash; the SYSTEM_BFCL / RUBRIC_BFCL
                                                              identity assertions; the F1 denotation counts; the night
                                                              total; creates no cache
  python tools/analysis/bfcl_final_state_swap.py --pilot 12   24 calls: the 12 LOWEST mids of the 458; gated
                                                              (READY + BFCL_SWAP_GO=11)
  python tools/analysis/bfcl_final_state_swap.py --run        the remaining 892 calls; REFUSES unless the 24 pilot cells
                                                              are cached and the truncation guard reads <= 5% unusable
  python tools/analysis/bfcl_final_state_swap.py --analyze    refuses a partial cache (writes
                                                              bfcl_final_state_swap_PILOT.txt instead); the outcome of
                                                              record is WRITE-ONCE (open mode "x")

THE GATE: --pilot and --run REFUSE, fail-closed and before any file is opened, unless BFCL_SWAP_GO equals "11" (plan
Amendment 11; clause 3(a) discharged by the ruling at 1470fe8; clause 3(d) keeps the standard flow) AND
docs/reviews/READY_bfcl_final_state_swap.md exists, is tracked by git and carries no uncommitted change.

THE ONE KNOB (registration "THE EXACT PROMPT DELTA", fixed before any code). The object edited is the string returned by
tools/analysis/prompt_v2.v2_system_template(). FOUR LITERAL REPLACEMENTS, IN THIS ORDER, each asserted to match EXACTLY
ONCE (count == 1 each, 4 in total; anything else REFUSES):
 (1) "extract each model's FINAL ANSWER and check it"  -> "extract each model's FINAL STATE and check it"
 (2) "A response whose final answer is wrong cannot win" -> "A response whose final state is wrong cannot win"
 (3) "against a response whose final answer is right, whatever its reasoning looks like."
     -> "against a response whose final state is right, whatever its reasoning looks like."
 (4) "When BOTH final answers are right:" -> "When BOTH final states are right:"
The template is then filled exactly as the parent fills it ($systemPrompt = SYSTEM_BFCL, $rubric = RUBRIC_BFCL, then
"\n\n" + rejudge_grok.SCHEMA_INSTRUCTION). RUBRIC_BFCL and SYSTEM_BFCL are BYTE-IDENTICAL to the pilot's and asserted
against the values pinned in the pilot cache's run_meta. Nothing else in the template is touched.

WHAT THIS SCRIPT IS BUILT ON (reuse, pinned): the parent instrument tools/analysis/bfcl_judged_pilot.py at 95c6d92, LF
sha256[:16] 5e9db53b894eeccb, imported as a module and REFUSED at load time under any other sha (corpus reader, raw
readers, the per-task expected outcome from possible_answer/BFCL_v4_multi_turn_base.json, the artefact cap, the
schedule, assert_no_per_side_verdict, dual, post, configure_rr / post_body / assert_body_copy, clustered, wilson).

HYGIENE: the FIRST PRINTED LINE of every mode is the pool id p2035adddedd1becb; every scheduled task of the 458 is
re-checked EVAL under split_side.tier_b norm-v1 from the corpus DB (a TRAIN / GATE id REFUSES, printed);
[DBGUARD] whitelist = the corpus (mode=ro&immutable=1), the PILOT's cache (ONLY mode=ro&immutable=1; never written) and
this test's own cache experiment_results/agent/bfcl_final_state_swap.db; everything else is a SystemExit; idempotent
wrapper (review D13). No per-side checker verdict ever reaches a prompt; assert_no_per_side_verdict is EXECUTED on ALL
916 re-assembled payloads (one execution per (mid, arm) cell, counted). The grok-FC self-preference stratum is NOT
re-posted and NO DATUM of it is read (no verdict, vote, outcome, checker or result row); its payload BYTES are
re-assembled ONLY to reproduce the schedule-wide payload anchor below, never posted and never in any readout, count or
denominator - PERMITTED by the registrar's ruling D4(f) (7da2ec5) on exactly these three conditions, and the anchor line
PRINTS that it spans all 1,216 payloads INCLUDING the self-preference stratum's.

THE F2 GATE (the ruling's DANGLING-REFERENT fence F2, built exactly as it specifies, printed on every mode):
 (a) user turns equal to the comparator's: for each of the 916 (mid, arm) cells, sha256_16 of THIS script's user turn ==
     the PARENT MODULE'S RE-ASSEMBLY of the same cell (916 of 916; the pilot cache stores no per-cell hash, so this is
     never a comparison with a stored value); that re-assembly is tied to pass 1 ONLY THROUGH the SCHEDULE-WIDE PAYLOAD
     ANCHOR 951ec3a0a063b5a8 over all 1,216 assembled payloads plus the system prompt (sha256 over the 608 schedule rows
     of "<mid>|" + system + user_fwd + user_rev; D1 ruling, 7da2ec5), recomputed here through the parent module;
 (b) a FULL character diff of the two system prompts (difflib opcodes, every non-equal opcode printed), every changed
     character confined to the four FROM spans, the parent prompt with the four replacements applied == the new prompt,
     and the new sha16 printed BESIDE the comparator's: the pilot system prompt's OWN sha16 058faa54f0697ad9 (D1 ruling;
     re-derived through the parent module, pinned, and required);
 (c) exact replacement counts: 1, 1, 1, 1 in order, 4 in total;
 (d) the schedule hash bcf9d1654e68e4ca re-derived from the corpus (and equal to the pilot run_meta's; the 608 cached
     schedule rows reproduce with 0 differences).
D1 (registrar ruling, 7da2ec5): the registration's "system prompt sha 951ec3a0a063b5a8" sites are bracketed; the binding
reading is (a) (the schedule-wide payload anchor) and (b) (the system prompt's own sha16 058faa54f0697ad9).

F1 (the ruling's denotation count, "--dry-run prints the counts"), operationalised HERE (the ruling fixes no regex): over
the 916 artefact sides of the 458 deciding matches, the number of sides whose rendered artefact contains the referent
"final answer" (case-insensitive, `final[ _-]*answers?`) against the number carrying a non-empty final state_info.

CRITERIA (registration READOUTS AND CRITERIA, literally; each has ONE deciding statistic).
 C1 T_swap = the order-flip TIE share on the 458 (LITERAL denominator 458: an unusable match is not a TIE; T over the
    usable matches is printed beside and decides nothing). Deciding statistic: the PAIRED delta, match by match over the
    same 458 mids, of TIE_swap - TIE_pilot (mean = T_swap - 100/458 = T_swap - 0.2183), its task-clustered interval
    point +- 1.96 x the bootstrap SE (49 task clusters, B = 2000, seed 42); percentile interval, B, cluster count, the
    MEASURED delta-DEFF and the exact two-sided McNemar (b, c, p) printed beside. BAR -0.05. HELD iff the interval lies
    wholly below -0.05; FAILED iff wholly above; UNDETERMINED iff it contains -0.05, or fewer than 300 of the 458 yield a
    usable dual-order outcome, or the F2 gate did not pass 916 of 916, or unusable rows exceed 5% of the posted calls.
    REQUIRED COMPANION, never a second deciding clause: a HELD whose McNemar p exceeds 0.01 prints
    "HELD ON THE INTERVAL, NOT CORROBORATED BY THE PAIRED TEST". D2 (registrar ruling, 7da2ec5): THE VALIDITY TRIGGERS
    (usable < 300; the F2 gate short of 916 of 916; unusable rows above 5% of the posted calls) ARE EVALUATED FIRST AND
    PRE-EMPT THE VERDICT: if any fires, C1 is "UNDETERMINED (BY TRIGGER: <trigger, with its value>)", the interval is
    PRINTED but NOT SCORED, the falsifier and the HARM clause are NOT evaluated; only if none fires is the interval read.
    D3 (7da2ec5): P1 is scored on the T_swap form ALONE; the Delta form is printed as its restatement
    ([-0.1183, -0.0183], point -0.0683) and never scored.
 C2 the paired delta of convention-A agreement (A_swap - 0.7402), HELD iff the interval's lower end >= -0.05, FAILED iff
    wholly below -0.05, UNDETERMINED otherwise; convention B with Wilson and clustered intervals beside; the mandatory note
    (never a rung). C3 the paired delta of the wrong-committed rate (W_swap - 0.0415), HELD iff the upper end <= +0.05,
    FAILED iff wholly above +0.05, UNDETERMINED otherwise; the decomposition right + wrong + ties (+ unusable) printed.
 C4 the position signature (first-position rate, the six-class flip table, the per-task tie concentration). C5 the
    instrument counts (a)-(g). P1-P8 scored explicitly. Falsifier printed iff C1 FAILED; the HARM result iff C1 HELD and
    C3 FAILED. SUPPORT: both DEFFs (level, for T_swap; delta, for Delta) measured from the cache's own task clusters
    (bootstrap variance / iid variance), n_eff and MDE printed beside every deciding statistic; "UNDERPOWERED FOR ITS
    OWN BAR" printed beside C1 if the measured delta-DEFF exceeds 3.0.
 RIDERS (ruling section 4): R1 - "reference-wrong stratum EMPTY BY CONSTRUCTION" and the per-contestant agreement with
    the expected outcome printed beside every accuracy, with the assert_no_per_side_verdict count over all 916 payloads;
    R2 - any paired delta whose point lies in [-0.05, 0] is chipped DESCRIPTIVE-ONLY in the printed verdict. The fence
    F3 / F4 / F5 sentences are printed in the outcome.

CACHE, META, LEDGER: as BFCL-FLIP-RESEED's shape - run_meta pinned at the first posting launch (the replacements, the
new and the pilot system-prompt sha16, the anchor, the 458 mids + sha, script_sha256_16 = THIS file's LF-rendered
sha256[:16], ...), a relaunch differing on ANY key (the script sha included) REFUSED; no cached row re-posted; a
content-filter 400 cached as unusable (rule 10); the night ledger read before and appended after every posting launch.
"""
import argparse
import difflib
import hashlib
import json
import math
import os
import random
import re
import statistics
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

# THE DB GUARD: capture the TRUE connect before the parent wraps it, then replace the module attribute (idempotent).
_pm = sys.modules.get("bfcl_judged_pilot")
_TRUE_CONNECT = (getattr(sqlite3.connect, "_true_connect", None)
                 or (_pm._real_sqlite3_connect if _pm is not None else sqlite3.connect))

import bfcl_judged_pilot as P      # noqa: E402
import rejudge_grok as rj          # noqa: E402
import rejudge_reasoning as rr     # noqa: E402
import split_side                  # noqa: E402

TEST = "BFCL-FINAL-STATE-SWAP"
REGISTRATION = ("docs/judge_v2_program.md L12315-L12598 (heading L12316), commit ca3a7cc (registered 2026-09-23, before "
                "any code or call); record docs/agents/results/BFCL-FINAL-STATE-SWAP.json; closed-line ruling "
                "docs/agents/leads/2026-09-23_bfcl_final_state_swap_ruling.md (1470fe8)")
PARENT_SHA_PINNED = "5e9db53b894eeccb"
PARENT_COMMIT = "95c6d92"
if P.SCRIPT_SHA != PARENT_SHA_PINNED:
    raise SystemExit("[PARENT] REFUSED at import: tools/analysis/bfcl_judged_pilot.py has LF sha %s, not the pinned %s "
                     "(%s). The comparator's payload machinery moved; the arm would not be one-knob."
                     % (P.SCRIPT_SHA, PARENT_SHA_PINNED, PARENT_COMMIT))

AGENT_DIR = os.path.join(ROOT, "experiment_results", "agent")
CORPUS_DB_NAME = P.CORPUS_DB_NAME
PILOT_DB_NAME = P.CACHE_DB_NAME
CACHE_DB_NAME = "bfcl_final_state_swap.db"
DB = os.path.join(AGENT_DIR, CORPUS_DB_NAME)
PILOT_CACHE = os.path.join(AGENT_DIR, PILOT_DB_NAME)
CACHE = os.path.join(AGENT_DIR, CACHE_DB_NAME)
OUT = os.path.join(AGENT_DIR, "bfcl_final_state_swap_outcome.txt")      # write-once, mode "x"
OUT_PILOT = os.path.join(AGENT_DIR, "bfcl_final_state_swap_PILOT.txt")  # pilot / partial, overwritable
READY = os.path.join(ROOT, "docs", "reviews", "READY_bfcl_final_state_swap.md")
GO_ENV, GO_VALUE = "BFCL_SWAP_GO", "11"
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
        raise SystemExit("[DBGUARD] REFUSED: %s may open only %s; a connection to %r (%s) was attempted (forbidden by "
                         "name, among others: %s)." % (os.path.basename(__file__), sorted(ALLOWED_DB_BASENAMES),
                                                       str(database), base, ", ".join(P.FORBIDDEN_DB_BASENAMES)))
    if base == CORPUS_DB_NAME:                                  # review 5(a): the corpus is read-only too
        s = str(database)
        if not _ro_uri(s, kwargs):
            raise SystemExit("[DBGUARD] REFUSED: the corpus %s may be opened ONLY as a URI with mode=ro&immutable=1 (it "
                             "is of record and never written); attempted %r" % (CORPUS_DB_NAME, s))
    if base == PILOT_DB_NAME:
        s = str(database)
        if not _ro_uri(s, kwargs):
            raise SystemExit("[DBGUARD] REFUSED: the pilot's cache %s may be opened ONLY as a URI with mode=ro&immutable=1 "
                             "(the control of record; never written); attempted %r" % (PILOT_DB_NAME, s))
    _OPENED.append(str(database))
    return _TRUE_CONNECT(database, *args, **kwargs)


_guarded_connect._true_connect = _TRUE_CONNECT
_guarded_connect._owner = __name__
sqlite3.connect = _guarded_connect

# ----------------------------------------------------------------------------------------------------------------
# constants of record
# ----------------------------------------------------------------------------------------------------------------
POOL_ID = P.BFCL_POOL_ID
SCHEDULE_HASH_OF_RECORD = "bcf9d1654e68e4ca"
ALL_PAYLOAD_ANCHOR = "951ec3a0a063b5a8"                     # the SCHEDULE-WIDE PAYLOAD ANCHOR (1,216 payloads + system prompt; D1)
PILOT_SYSTEM_PROMPT_SHA = "058faa54f0697ad9"                # the pilot system prompt's OWN sha16 of record (D1 ruling, 7da2ec5)
N_SCHEDULE_ROWS = 608
N_DECIDING = 458
N_CELLS = 2 * N_DECIDING
N_TASKS_REG = 49
PILOT_COUNTS = dict(ties=100, right=339, wrong=19)          # the pilot's decomposition of the 458, of record
T_PILOT, A_PILOT, W_PILOT = 0.2183, 0.7402, 0.0415           # the registered constants (= 100 / 339 / 19 of 458)
REPLACEMENTS = (("extract each model's FINAL ANSWER and check it", "extract each model's FINAL STATE and check it"),
                ("A response whose final answer is wrong cannot win", "A response whose final state is wrong cannot win"),
                ("against a response whose final answer is right, whatever its reasoning looks like.",
                 "against a response whose final state is right, whatever its reasoning looks like."),
                ("When BOTH final answers are right:", "When BOTH final states are right:"))
SIX = (("Model A", "Model A"), ("Model B", "Model B"), ("TIE", "Model A"), ("Model A", "TIE"), ("TIE", "TIE"),
       ("Model B", "TIE"))
PILOT_SIX = (57, 0, 24, 14, 3, 2)
SEED = 42                                                    # the pilot's; RNG (posting order) and bootstrap
BOOT = 2000
BAR_T = -0.05
BAR_A = -0.05
BAR_W = 0.05
MIN_USABLE = 300
UNUSABLE_MAX = 0.05
MCNEMAR_CORROB = 0.01
DEFF_UNDERPOWER = 3.0
PILOT_MATCHES = 12
GUARD_RATE = 0.05
PAIR_NOREF_W = 0.0930
PILOT_FIRST_POS = (0.5862, 870, 5.09)
F1_RE = re.compile(r"final[ _-]*answers?", re.I)
PROTOCOL = ("BFCL-FINAL-STATE-SWAP: the frozen BFCL-JUDGED-PILOT instrument with FOUR literal replacements in the "
            "prompt_v2 verify-first block ('final answer' -> 'final state', each asserted count == 1, 4 in total) and "
            "NOTHING ELSE; the 458 deciding matches, both orders, user turns byte-identical to the pilot's (gated); "
            "parent protocol: " + P.PROTOCOL)
R1_LINE = ("R1 (ruling section 4): the reference-wrong stratum is EMPTY BY CONSTRUCTION (the reference is the per-task "
           "EXPECTED OUTCOME, the corpus's own ground truth); this arm says NOTHING about the reference ceiling on BFCL "
           "and the CONSENSUS-FIT KEY/REF contrast is NOT ESTIMABLE on it.")
C2_NOTE = ("NOTE OF RECORD (mandatory with this number): A_swap is NOT a rung reading and is NEVER placed on the "
           "reference ladder; the 0.75 bar belongs to BFCL-JUDGED-PILOT's C1 and is not re-litigated here, and nothing "
           "in this test can restore the 'for Agents' bridge as a measured claim.")
FENCE = ("FENCE (ruling section 5): F3 - after this reading, HELD or FAILED, a further template edit on BFCL requires a "
         "DIFFERENT F1-qualifying referent AND a pre-registered argument why this result does not predict the next one; "
         "two readings on one corpus close the template line on that corpus PERMANENTLY. F4 - this edit changes ONE "
         "referent (answer -> state) in four strings; a multi-referent edit would be DESCRIPTIVE-ONLY. F5 - nothing this "
         "arm returns changes the STACK-v2 recipe of record; a HELD C1 licenses a CORPUS-LOCAL variant only; promotion "
         "needs its own registration with an MMLU-Pro NON-INFERIORITY reading.")
IFEVAL_RIDER = ("ruling section 3 riders: the IFEVAL 25.1pp collapse is never quoted as an expectation for this arm (P1, "
                "point -0.07, is the prediction of record); A_swap never goes on the reference ladder.")

_NIGHT_LINE = None

ALL_BRANCHES = frozenset(
    ["C1:HELD", "C1:HELD_QUAL", "C1:FAILED", "C1:UND_INTERVAL",
     "C1:TRIG_USABLE", "C1:TRIG_GATE", "C1:TRIG_UNUSABLE",
     "C1:PREEMPT_USABLE", "C1:PREEMPT_GATE", "C1:PREEMPT_UNUSABLE",
     "R2:CHIP", "R2:NOCHIP", "UNDERPOWER:YES", "UNDERPOWER:NO", "UNDERPOWER:NA",
     "C2:HELD", "C2:FAILED", "C2:UND", "C3:HELD", "C3:FAILED", "C3:UND", "HARM:YES", "HARM:NO", "HARM:NOT_EVALUATED",
     "FALS:FIRES", "FALS:HELD", "FALS:UND", "FALS:NOT_EVALUATED", "C4:HELD", "C4:FAILED", "C5:HELD", "C5:FAILED",
     "P1:HELD", "P1:FAILED", "P2:HELD", "P2:FAILED", "P4ii:HELD", "P4ii:FAILED"]
    + ["%s:%s" % (p, v) for p in ("P3", "P4", "P5", "P6", "P7") for v in ("HELD", "FAILED")]
    + ["P8:HELD", "P8:FAILED", "P8:UND"]
    + ["POWER:TABLE", "POWER:MEASURED_NA", "POWER:REALISED", "POWER:REALISED_NA",
       "USABLE:SAME", "USABLE:DIFFERS", "USABLE:NA"])
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
# the pool, the split, the pilot's cache
# ----------------------------------------------------------------------------------------------------------------
def pool_line():
    """The verified pool line (the FIRST printed line of every mode is the constant pool id, printed by __main__)."""
    if not os.path.exists(P.POOL_JSON):
        raise SystemExit("[POOL] %s REFUSED: %s is missing." % (POOL_ID, rel(P.POOL_JSON)))
    ids = json.load(open(P.POOL_JSON, encoding="utf-8"))
    base = sorted(int(i) for i in ids["BFCL/%s" % P.STRATUM])
    print("[POOL] verified %s - BFCL pool of record, %d EVAL %s tasks (id from the FILE NAME of %s; pool_guard not "
          "imported: no MMLU-Pro / union pool is read)" % (POOL_ID, len(base), P.STRATUM, rel(P.POOL_JSON)), flush=True)
    return base


def split_check(task_ids, db_path=None):
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
    if v is None:
        return None
    return P.unusable_vote(v[0], v[1])


def order_class(votes, mid):
    return (adj(votes.get((mid, "fwd"))), adj(votes.get((mid, "rev"))))


def set_sha(mids):
    return hashlib.sha256(",".join(str(m) for m in sorted(mids)).encode("utf-8")).hexdigest()[:16]


def load_context():
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
        deciding = sorted((r for r in rows if r["stratum"] == "headline" and not r["nj"] and not r["nj_a"] and not r["nj_b"]),
                          key=lambda r: r["mid"])
        votes1 = raw_votes(con_p, "verdicts", [r["mid"] for r in deciding])     # the headline deciding cells only
        D1 = P.dual(con_p, deciding)
    finally:
        con_p.close()
    recomputed = sorted(tuple(r[k] for k in P.SCHEDULE_COLS) for r in rows)
    sched_diffs = sum(1 for a, b in zip(recomputed, cached_sched) if a != b) + abs(len(recomputed) - len(cached_sched))
    return dict(c=c, raws=raws, tasktext=tasktext, refs=refs, rows=rows, deciding=deciding, D1=D1, votes1=votes1,
                meta_p=meta_p, sched_diffs=sched_diffs, sched_hash=P.schedule_hash(rows),
                shas={"dataset": ds_sha, "possible_answer": pa_sha, "dataset_path": ds_path, "possible_answer_path": pa_path})


# ----------------------------------------------------------------------------------------------------------------
# the one knob: the four replacements, the swapped system prompt, the F2 gate
# ----------------------------------------------------------------------------------------------------------------
def apply_replacements(text, where):
    """-> (replaced text, [count per replacement]). REFUSES unless each FROM matches EXACTLY ONCE, in order, 4 in total."""
    counts = []
    for frm, to in REPLACEMENTS:
        n = text.count(frm)
        counts.append(n)
        if n != 1:
            raise SystemExit("[SWAP] REFUSED (0 calls): replacement %r matches %d time(s) in %s, not exactly once; the "
                             "arm would not be the registered one-knob edit." % (frm, n, where))
        text = text.replace(frm, to)
    if sum(counts) != 4:
        raise SystemExit("[SWAP] REFUSED: %d replacements occurred, not exactly 4" % sum(counts))
    return text, counts


def swapped_template():
    import prompt_v2
    return apply_replacements(prompt_v2.v2_system_template(), "prompt_v2.v2_system_template()")


def system_prompt():
    """THIS arm's system prompt: the edited template, filled exactly as the parent fills it."""
    t, _ = swapped_template()
    return t.replace("$systemPrompt", P.SYSTEM_BFCL).replace("$rubric", P.RUBRIC_BFCL) + "\n\n" + rj.SCHEMA_INSTRUCTION


def char_diff(a, b):
    """The full character diff (difflib opcodes, autojunk off): -> list of (tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2])."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return [(tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]


def prompt_gate():
    """(b) and (c) of F2 at zero DB. -> dict."""
    old = P.system_prompt()
    new = system_prompt()
    t, counts = swapped_template()
    reapplied, counts_full = apply_replacements(old, "the parent's filled system prompt")
    spans = [(old.index(frm), old.index(frm) + len(frm)) for frm, _ in REPLACEMENTS]
    ops = char_diff(old, new)
    confined = all(any(s0 <= i1 and i2 <= s1 for s0, s1 in spans) for _, i1, i2, _, _, _, _ in ops)
    slots = bool(new.count(P.SYSTEM_BFCL) == 1 and new.count(P.RUBRIC_BFCL) == 1 and new.endswith(rj.SCHEMA_INSTRUCTION))
    ok = bool(reapplied == new and confined and counts == [1, 1, 1, 1] and counts_full == [1, 1, 1, 1] and slots and ops
              and sha16(old) == PILOT_SYSTEM_PROMPT_SHA)
    return dict(ok=ok, old=old, new=new, old_sha=sha16(old), new_sha=sha16(new), counts=counts, counts_full=counts_full,
                ops=ops, confined=bool(confined), reapplied_equal=bool(reapplied == new), slots=slots,
                residual_final_answer=len(F1_RE.findall(new)), old_final_answer=len(F1_RE.findall(old)))


def assemble_user(row, arm, ctx, counter=None):
    """THIS script's user turn for one (mid, arm) cell; the leakage guard executed once per cell."""
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
    return user


def all_payload_anchor(rows, payload_fn):
    """The review's recipe (docs/reviews/2026-09-23_bfcl_judged_pilot_post.md row 7e)."""
    h = hashlib.sha256()
    for r in rows:
        s, u1, u2 = payload_fn(r)
        h.update(("%d|" % r["mid"]).encode("utf-8"))
        h.update(s.encode("utf-8"))
        h.update(u1.encode("utf-8"))
        h.update(u2.encode("utf-8"))
    return h.hexdigest()[:16]


def f2_gate(ctx):
    pg = prompt_gate()
    parent = {}

    def parent_payload(r):
        if r["mid"] not in parent:
            parent[r["mid"]] = P.payloads(r, ctx["c"], ctx["raws"], ctx["tasktext"], ctx["refs"])
        return parent[r["mid"]]
    anchor = all_payload_anchor(ctx["rows"], parent_payload)
    counter = Counter()
    mism, cells = [], []
    n_eq = 0
    for r in ctx["deciding"]:
        _, pu1, pu2 = parent_payload(r)
        for arm, pu in (("fwd", pu1), ("rev", pu2)):
            u = assemble_user(r, arm, ctx, counter)
            own, par = sha16(u), sha16(pu)
            cells.append((r["mid"], arm, own, par))
            if own == par:
                n_eq += 1
            else:
                mism.append("mid %d %s: own %s != parent %s" % (r["mid"], arm, own, par))
    meta_p = ctx["meta_p"]
    slots_ok = bool(meta_p.get("system_bfcl") == P.SYSTEM_BFCL and meta_p.get("rubric_bfcl") == P.RUBRIC_BFCL)
    sched_ok = bool(ctx["sched_hash"] == SCHEDULE_HASH_OF_RECORD == meta_p.get("schedule_hash") and ctx["sched_diffs"] == 0
                    and len(ctx["rows"]) == N_SCHEDULE_ROWS)
    n_cells = 2 * len(ctx["deciding"])
    ok = bool(pg["ok"] and anchor == ALL_PAYLOAD_ANCHOR and n_eq == n_cells and not mism and slots_ok and sched_ok)
    return dict(ok=ok, pg=pg, anchor=anchor, n_eq=n_eq, n_cells=n_cells, mism=mism, cells=cells, slots_ok=slots_ok,
                sched_ok=sched_ok, leak_checks=counter["leak_checks"])


def f2_lines(g, full_diff=True):
    pg = g["pg"]
    L = ["[F2 GATE] (a) user turns equal to the comparator's (the parent module's re-assembly): %d of %d (mid, arm) cells%s"
         % (g["n_eq"], g["n_cells"], "" if not g["mism"] else " | FIRST MISMATCH: %s" % g["mism"][0]),
         "[F2 GATE] (a) the comparator tied to pass 1 through the SCHEDULE-WIDE PAYLOAD ANCHOR over all 1,216 assembled payloads "
         "plus the system prompt - the anchor spans the self-preference stratum's payloads TOO (their bytes are hashed only: "
         "no datum of that stratum is read, none of its payloads is posted or enters any readout; ruling D4(f)) - recomputed "
         "through the parent module: %s vs of record %s -> %s"
         % (g["anchor"], ALL_PAYLOAD_ANCHOR, "MATCH" if g["anchor"] == ALL_PAYLOAD_ANCHOR else "MISMATCH"),
         "[F2 GATE] (b) NEW system prompt sha16 %s BESIDE the comparator's: the pilot system prompt's OWN sha16 %s (re-derived "
         "through the parent module) vs of record %s -> %s" % (pg["new_sha"], pg["old_sha"], PILOT_SYSTEM_PROMPT_SHA,
                                                             "MATCH" if pg["old_sha"] == PILOT_SYSTEM_PROMPT_SHA else "MISMATCH"),
         "[F2 GATE] (b) the parent's filled prompt with the four replacements applied == the new prompt: %s | every changed "
         "character inside one of the four FROM spans: %s | SYSTEM_BFCL / RUBRIC_BFCL / SCHEMA_INSTRUCTION present once and "
         "unchanged: %s | 'final answer' referents: %d in the pilot's prompt, %d in the new one"
         % (pg["reapplied_equal"], pg["confined"], pg["slots"], pg["old_final_answer"], pg["residual_final_answer"])]
    if full_diff:
        L.append("[F2 GATE] (b) FULL CHARACTER DIFF, pilot system prompt (%d chars) -> new (%d chars), %d non-equal opcodes:"
                 % (len(pg["old"]), len(pg["new"]), len(pg["ops"])))
        for tag, i1, i2, j1, j2, x, y in pg["ops"]:
            L.append("    %-7s old[%d:%d] %r -> new[%d:%d] %r   (context: ...%r...)"
                     % (tag, i1, i2, x, j1, j2, y, pg["old"][max(0, i1 - 30):i2 + 30]))
        L.append("[F2 GATE] (b) the same diff by LINE (unified, zero context), for the reader:")
        L += ["    " + x for x in difflib.unified_diff(pg["old"].split("\n"), pg["new"].split("\n"), "pilot system prompt",
                                                       "swapped system prompt", n=0, lineterm="")]
    L += ["[F2 GATE] (c) replacement counts in order %s in the template and %s in the filled prompt (each must be 1; total 4)"
          % (pg["counts"], pg["counts_full"])]
    for k, (frm, to) in enumerate(REPLACEMENTS, 1):
        L.append("    (%d) %r -> %r : matched %d" % (k, frm, to, pg["counts"][k - 1]))
    L += ["[F2 GATE] (d) schedule hash %s re-derived from the corpus, equal to the pilot run_meta's, 608 cached rows "
          "reproduce with 0 differences: %s | SYSTEM_BFCL / RUBRIC_BFCL == the pilot run_meta's pinned values: %s"
          % (SCHEDULE_HASH_OF_RECORD, g["sched_ok"], g["slots_ok"]),
          "[F2 GATE] assert_no_per_side_verdict executed on %d of %d re-assembled payloads (one per cell) -> %s"
          % (g["leak_checks"], g["n_cells"], "PASS (one knob, byte-proved)" if g["ok"] else "REFUSED (not one-knob)")]
    return L


def f1_counts(ctx):
    """The ruling's F1: the 'final answer' referent against the final state, over the 916 deciding artefact sides."""
    fa = fs = n = 0
    for r in ctx["deciding"]:
        for ag in (r["agent_a"], r["agent_b"]):
            raw = ctx["raws"].get((r["task_id"], ag))
            txt = P.artefact_facts(raw, ctx["c"].eps[(r["task_id"], ag)])["text"]
            n += 1
            fa += int(bool(F1_RE.search(txt)))
            fs += int(bool(raw and (raw.get("state") or "").strip() not in ("", "[]")))
    return fa, fs, n


def pilot_decomposition(rows, D1):
    ties = sum(1 for r in rows if D1[r["mid"]]["winner"] == "TIE")
    right = sum(1 for r in rows if D1[r["mid"]]["winner"] == r["checker_winner"])
    inval = sum(1 for r in rows if D1[r["mid"]]["invalid"] or D1[r["mid"]]["pending"])
    return dict(ties=ties, right=right, wrong=len(rows) - ties - right - inval, invalid=inval)


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
    bad = []
    if len(ctx["deciding"]) != N_DECIDING:
        bad.append("the deciding subset is %d mids, not %d" % (len(ctx["deciding"]), N_DECIDING))
    ntask = len({r["task_id"] for r in ctx["deciding"]})
    if ntask != N_TASKS_REG:
        bad.append("the 458 occupy %d tasks, not %d" % (ntask, N_TASKS_REG))
    dec = pilot_decomposition(ctx["deciding"], ctx["D1"])
    for k in ("ties", "right", "wrong"):
        if dec[k] != PILOT_COUNTS[k]:
            bad.append("the pilot's %s on the 458 is %d, of record %d" % (k, dec[k], PILOT_COUNTS[k]))
    for r in ctx["deciding"]:
        if r["agent_a"] not in P.HEADLINE_ROSTER or r["agent_b"] not in P.HEADLINE_ROSTER:
            bad.append("mid %d carries an agent off the 7-agent headline roster" % r["mid"])
    n_chk, split_bad = split_check(db_path=db_path, task_ids=[r["task_id"] for r in ctx["deciding"]])
    bad += ["SPLIT: " + s for s in split_bad]
    if not g["ok"]:
        bad.append("the F2 gate did not pass (see the [F2 GATE] lines)")
    mp = ctx["meta_p"]
    for k, want in (("judge_model", P.JUDGE_MODEL), ("max_tokens", str(P.MAXTOK)), ("temperature", "omitted"),
                    ("seed", str(SEED)), ("pool_id", POOL_ID)):
        if mp.get(k) != want:
            bad.append("pilot run_meta %s is %r, expected %r" % (k, mp.get(k), want))
    return bad


# ----------------------------------------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------------------------------------
def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n))


def clustered_mean(by_task, boot, seed):
    """-> dict(point, sd, lo_n, hi_n, lo_p, hi_p, n, q) for the pooled mean of per-match values (0/1 or -1/0/1)."""
    vals = [v for vs in by_task.values() for v in vs]
    nan = float("nan")
    if not vals:
        return dict(point=nan, sd=nan, lo_n=nan, hi_n=nan, lo_p=nan, hi_p=nan, n=0, q=0, k=0, iid_var=nan)
    point, lo, hi, sd = P.clustered(by_task, boot, seed)
    iid_var = statistics.pvariance(vals) / len(vals) if len(vals) > 1 else nan
    return dict(point=point, sd=sd, lo_n=point - 1.96 * sd, hi_n=point + 1.96 * sd, lo_p=lo, hi_p=hi, n=len(vals),
                q=len(by_task), k=sum(vals), iid_var=iid_var)


def deff_of(r):
    """Measured DEFF = clustered bootstrap variance / iid variance of the per-match values; n_eff; MDE (80% / 50%)."""
    if not (r["iid_var"] == r["iid_var"]) or r["iid_var"] <= 0 or not (r["sd"] == r["sd"]):
        return dict(deff=float("nan"), neff=float("nan"), mde80=2.80 * r["sd"] if r["sd"] == r["sd"] else float("nan"),
                    mde50=1.96 * r["sd"] if r["sd"] == r["sd"] else float("nan"))
    deff = r["sd"] ** 2 / r["iid_var"]
    return dict(deff=deff, neff=(r["n"] / deff if deff > 0 else float("nan")), mde80=2.80 * r["sd"], mde50=1.96 * r["sd"])


def per_match(D, r):
    """-> (tie, ok (convention A), wrong_committed, usable, committed) for one match's dual outcome."""
    v = D[r["mid"]]
    usable = int((not v["pending"]) and (not v["invalid"]))
    tie = int(usable and v["winner"] == "TIE")
    committed = int(usable and v["winner"] not in (None, "TIE", "INVALID"))
    ok = int(committed and v["winner"] == r["checker_winner"])
    return tie, ok, int(committed and not ok), usable, committed


def first_position(rows, votes, boot, seed):
    bt = defaultdict(list)
    for r in rows:
        for arm in ("fwd", "rev"):
            v = adj(votes.get((r["mid"], arm)))
            if v in ("Model A", "Model B"):
                bt[r["task_id"]].append(1 if v == "Model A" else 0)
    res = clustered_mean(bt, boot, seed)
    res["wlo"], res["whi"] = P.wilson(res["k"], res["n"]) if res["n"] else (float("nan"), float("nan"))
    res["z"] = (res["point"] - 0.5) / math.sqrt(0.25 / res["n"]) if res["n"] else float("nan")
    return res


def tie_concentration(rows, D):
    per = defaultdict(lambda: [0, 0])
    for r in rows:
        per[r["task_id"]][1] += 1
        per[r["task_id"]][0] += int(D[r["mid"]]["winner"] == "TIE" and not D[r["mid"]]["pending"])
    ties = sum(t for t, _ in per.values())
    ge50 = sum(1 for t, n in per.values() if n and t / n >= 0.5)
    top5 = sum(sorted((t for t, _ in per.values()), reverse=True)[:5])
    return dict(tasks=len(per), ge50=ge50, top5=top5, ties=ties)


def compute(rows, votes1, votes2, D1, D2, g, extra, boot=BOOT, seed=SEED):
    """Every number the readout prints. Pure: the selftest drives it on synthetic data."""
    s = dict(boot=boot, seed=seed, gate=g, n=len(rows))
    bt = {k: defaultdict(list) for k in ("tie2", "dT", "ok2", "dA", "w2", "dW", "okB2")}
    usable2 = 0
    disc_b = disc_c = 0
    for r in rows:
        t1, o1, w1, _, _ = per_match(D1, r)
        t2, o2, w2, u2, c2 = per_match(D2, r)
        usable2 += u2
        k = r["task_id"]
        bt["tie2"][k].append(t2); bt["dT"][k].append(t2 - t1)
        bt["ok2"][k].append(o2); bt["dA"][k].append(o2 - o1)
        bt["w2"][k].append(w2); bt["dW"][k].append(w2 - w1)
        if c2:
            bt["okB2"][k].append(o2)
        if t1 and not t2:
            disc_b += 1
        elif t2 and not t1:
            disc_c += 1
    s["usable"] = usable2
    du = [per_match(D2, r)[0] - per_match(D1, r)[0] for r in rows if per_match(D2, r)[3]]
    s["dT_usable"] = (sum(du) / len(du)) if du else float("nan")
    bt_u = defaultdict(list)                     # the usable-only Delta with its interval (D-G5)
    for r in rows:
        if per_match(D2, r)[3]:
            bt_u[r["task_id"]].append(per_match(D2, r)[0] - per_match(D1, r)[0])
    for k in bt:
        s[k] = clustered_mean(bt[k], boot, seed)
    s["dTu"] = clustered_mean(bt_u, boot, seed)
    s["T1"] = sum(per_match(D1, r)[0] for r in rows) / max(1, len(rows))
    s["A1"] = sum(per_match(D1, r)[1] for r in rows) / max(1, len(rows))
    s["W1"] = sum(per_match(D1, r)[2] for r in rows) / max(1, len(rows))
    s["T2_usable"] = (s["tie2"]["k"] / usable2) if usable2 else float("nan")
    s["mcn"] = dict(b=disc_b, c=disc_c, p=mcnemar_exact(disc_b, disc_c))
    s["deff_T"], s["deff_dT"] = deff_of(s["tie2"]), deff_of(s["dT"])
    s["deff_A"], s["deff_dA"] = deff_of(s["ok2"]), deff_of(s["dA"])
    s["deff_W"], s["deff_dW"] = deff_of(s["w2"]), deff_of(s["dW"])
    for k in ("okB2", "ok2", "tie2", "w2"):
        s[k]["wlo"], s[k]["whi"] = P.wilson(s[k]["k"], s[k]["n"]) if s[k]["n"] else (float("nan"),) * 2
    dec = Counter()
    for r in rows:
        t2, o2, w2, u2, _ = per_match(D2, r)
        dec["right" if o2 else "wrong" if w2 else "tie" if t2 else "unusable"] += 1
    s["decomp"] = dict(dec)
    # R1: per contestant
    pc = {}
    for ag in sorted({r["agent_a"] for r in rows} | {r["agent_b"] for r in rows}):
        mine = [r for r in rows if ag in (r["agent_a"], r["agent_b"])]
        passed = sum(1 for r in mine if r["checker_winner"] == ag)
        pc[ag] = dict(n=len(mine), passed=passed, judge_A2=sum(per_match(D2, r)[1] for r in mine),
                      judge_A1=sum(per_match(D1, r)[1] for r in mine))
    s["per_contestant"] = pc
    # C4
    s["fp2"] = first_position(rows, votes2, boot, seed)
    s["fp1"] = first_position(rows, votes1, boot, seed)
    s["six2"] = Counter(order_class(votes2, r["mid"]) for r in rows if D2[r["mid"]]["winner"] == "TIE")
    s["six1"] = Counter(order_class(votes1, r["mid"]) for r in rows if D1[r["mid"]]["winner"] == "TIE")
    s["conc2"], s["conc1"] = tie_concentration(rows, D2), tie_concentration(rows, D1)
    # C5
    fins = Counter(v[1] or "(none)" for v in votes2.values())
    provs = Counter(v[3] or "(none)" for v in votes2.values())
    unus = sum(1 for v in votes2.values() if adj(v) == "INVALID")
    ctoks = [v[2] for v in votes2.values() if v[2] is not None and v[2] >= 0]
    s["c5"] = dict(posted=len(votes2), unusable=unus, fins=dict(fins), provs=dict(provs),
                   max_ctok=(max(ctoks) if ctoks else None),
                   trunc_sides=sum(r["trunc_a"] + r["trunc_b"] for r in rows),
                   trunc_matches=sum(1 for r in rows if r["trunc_a"] or r["trunc_b"]),
                   state_over=sum(r["state_over_a"] + r["state_over_b"] for r in rows),
                   cut_tasks=extra.get("cut_tasks", 0), sched_tasks=len({r["task_id"] for r in rows}))
    return s


# ----------------------------------------------------------------------------------------------------------------
# scoring and the readout (every print branch registers its tag; the selftest asserts full coverage)
# ----------------------------------------------------------------------------------------------------------------
def r2_chip(point):
    """Ruling R2: any delta whose point lies in [-0.05, 0] is DESCRIPTIVE-ONLY, whatever its interval."""
    if point == point and -0.05 <= point <= 0.0:
        hit("R2:CHIP")
        return " [R2: DESCRIPTIVE-ONLY - a delta in [-0.05, 0] sits inside the session floor (CANARY pass 2 0.087 " \
               "[0.056, 0.122]; DECOMP 5.7%) and is NEVER narrated as a move]"
    hit("R2:NOCHIP")
    return ""


def fmt_delta(name, r, d, boot, seed, bar):
    return ("%s = %+.4f (paired, match by match; denominator %d matches, %d task clusters) | interval of record point +- "
            "1.96 x clustered SE %.4f = [%+.4f, %+.4f] | percentile [%+.4f, %+.4f] (B = %d, seed %d) | bar %+.2f | "
            "MEASURED delta-DEFF %.3f, n_eff %.1f, MDE +-%.3f at 80%% power (+-%.3f at 50%%)"
            % (name, r["point"], r["n"], r["q"], r["sd"], r["lo_n"], r["hi_n"], r["lo_p"], r["hi_p"], boot, seed, bar,
               d["deff"], d["neff"], d["mde80"], d["mde50"]))


def fmt_level(name, r, d, extra=""):
    return ("%s = %d / %d = %.4f (%d task clusters) | clustered SE %.4f -> [%.4f, %.4f] | Wilson [%.4f, %.4f] | MEASURED "
            "level-DEFF %.3f, n_eff %.1f%s" % (name, r["k"], r["n"], r["point"], r["q"], r["sd"], r["lo_n"], r["hi_n"],
                                              r.get("wlo", float("nan")), r.get("whi", float("nan")), d["deff"], d["neff"],
                                              extra))


def score_c1(s):
    d = s["dT"]
    lo, hi = d["lo_n"], d["hi_n"]
    interval = "UND" if not (lo == lo and hi == hi) else ("HELD" if hi < BAR_T else "FAILED" if lo > BAR_T else "UND")
    # D2 ruling (7da2ec5): the VALIDITY TRIGGERS are evaluated FIRST and PRE-EMPT the verdict expression.
    triggers = []
    if s["usable"] < MIN_USABLE:
        triggers.append(("USABLE", "fewer than %d of the 458 yield a usable dual-order outcome: %d usable"
                         % (MIN_USABLE, s["usable"])))
    g = s["gate"]
    if not (g["ok"] and g["n_eq"] == N_CELLS and g["n_cells"] == N_CELLS):
        triggers.append(("GATE", "the F2 byte-identity gate did not pass %d of %d: %d of %d user turns equal, gate ok %s"
                         % (N_CELLS, N_CELLS, g["n_eq"], g["n_cells"], bool(g["ok"]))))
    c5 = s["c5"]
    if c5["unusable"] > UNUSABLE_MAX * max(1, c5["posted"]):
        triggers.append(("UNUSABLE", "unusable rows exceed 5%% of the posted calls: %d of %d = %.4f"
                         % (c5["unusable"], c5["posted"], c5["unusable"] / max(1, c5["posted"]))))
    if triggers:
        for name, _ in triggers:
            hit("C1:TRIG_%s" % name)
            if interval in ("HELD", "FAILED"):
                hit("C1:PREEMPT_%s" % name)
        return "UND_TRIGGER", ("UNDETERMINED (BY TRIGGER: %s). The trigger PRE-EMPTS the verdict (registrar ruling D2, "
                               "7da2ec5): the interval [%+.4f, %+.4f] is PRINTED BUT NOT SCORED%s; the falsifier and the "
                               "HARM clause are NOT evaluated."
                               % ("; ".join(t for _, t in triggers), lo, hi,
                                  " (it lies wholly %s %+.2f; that reading is pre-empted)"
                                  % ("below" if interval == "HELD" else "above", BAR_T)
                                  if interval in ("HELD", "FAILED") else ""))
    if interval == "HELD":
        if s["mcn"]["p"] > MCNEMAR_CORROB:
            hit("C1:HELD_QUAL")
            return "HELD_QUAL", ("HELD ON THE INTERVAL, NOT CORROBORATED BY THE PAIRED TEST (interval [%+.4f, %+.4f] wholly "
                                 "below %+.2f; exact McNemar p = %.4g > 0.01) - a QUALIFIED HELD, chipped with its "
                                 "qualification and never silently upgraded" % (lo, hi, BAR_T, s["mcn"]["p"]))
        hit("C1:HELD")
        return "HELD", ("HELD - the four strings EXPLAIN a material part of the indecision: the clustered interval [%+.4f, "
                        "%+.4f] lies wholly below %+.2f (exact McNemar p = %.4g, the required companion, <= 0.01)"
                        % (lo, hi, BAR_T, s["mcn"]["p"]))
    if interval == "FAILED":
        hit("C1:FAILED")
        return "FAILED", ("FAILED - the four strings do NOT explain the indecision: the clustered interval [%+.4f, %+.4f] "
                          "lies wholly above %+.2f" % (lo, hi, BAR_T))
    hit("C1:UND_INTERVAL")
    return "UNDETERMINED", "UNDETERMINED (the clustered interval [%+.4f, %+.4f] contains %+.2f)" % (lo, hi, BAR_T)


C1_RESTATED = ("SCOREABLE for a large template effect (true \u0394 <= \u22120.133, 80% power); at the registered prediction "
               "P1 (\u0394 \u2248 \u22120.07) the design is DESCRIPTIVE-ONLY and will read UNDETERMINED about 90% of the time.")
PLANNING_SE = 0.02955
Z80 = 0.8416212335729143


def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def power_at(delta, se):
    """Normal approximation, two-sided 95% interval against the bar -0.05: -> (P(HELD), P(FAILED), P(UND), held_thr,
    failed_thr, d80_held, d80_failed)."""
    held_thr, failed_thr = BAR_T - 1.96 * se, BAR_T + 1.96 * se
    ph = _phi((held_thr - delta) / se)
    pf = 1.0 - _phi((failed_thr - delta) / se)
    return ph, pf, 1.0 - ph - pf, held_thr, failed_thr, held_thr - Z80 * se, failed_thr + Z80 * se


def power_lines(s):
    """D-G5 (registrar 9b046c4, sections (B), (C), (E)): the outcome is SELF-CONTAINED on its power - the restated C1
    line VERBATIM, the power-against-the-bar table at the planning SE and at the MEASURED SE, and the realised
    P(UNDETERMINED) at the observed Delta and the measured SE."""
    hit("POWER:TABLE")
    L = ["  C1 UNDER THE SUPPORT RULE (registrar 9b046c4 section (C), quoted verbatim): " + C1_RESTATED,
         "  POWER AGAINST THE BAR -0.05 OF RECORD (registrar 9b046c4 section (B); planning SE 0.02955 = sqrt(0.20 / 458 x 2.0)): "
         "HELD needs Delta-hat < -0.1079, FAILED needs Delta-hat > +0.0079 | at P1 (Delta -0.0683): P(HELD) 0.090, "
         "P(FAILED) 0.005, P(UND) 0.905 | at Delta = 0: P(FAILED) 0.394 | 80% power at Delta <= -0.1328 or >= +0.0328"]
    for label, se in (("PLANNING SE %.5f (recomputed)" % PLANNING_SE, PLANNING_SE), ("MEASURED SE %.5f" % s["dT"]["sd"], s["dT"]["sd"])):
        if not (se == se) or se <= 0:
            hit("POWER:MEASURED_NA")
            L.append("  %s: the power table is NOT COMPUTABLE (SE not positive on this data)" % label)
            continue
        h1, f1, u1, ht, ft, d80h, d80f = power_at(-0.0683, se)
        h0, f0, u0, _, _, _, _ = power_at(0.0, se)
        L.append("  %s: HELD needs Delta-hat < %+.4f, FAILED needs Delta-hat > %+.4f | at P1 (Delta -0.0683): P(HELD) %.3f, "
                 "P(FAILED) %.3f, P(UND) %.3f | at Delta = 0: P(FAILED) %.3f, P(UND) %.3f, P(HELD) %.3f | 80%% power at "
                 "Delta <= %+.4f or >= %+.4f" % (label, ht, ft, h1, f1, u1, f0, u0, h0, d80h, d80f))
    se, d = s["dT"]["sd"], s["dT"]["point"]
    if se == se and se > 0 and d == d:
        hit("POWER:REALISED")
        ph, pf, pu, _, _, _, _ = power_at(d, se)
        L.append("  REALISED: at the observed Delta-hat %+.4f and the MEASURED SE %.5f (measured delta-DEFF %.3f), a "
                 "re-run of this design would read P(HELD) %.3f, P(FAILED) %.3f, P(UNDETERMINED) %.3f"
                 % (d, se, s["deff_dT"]["deff"], ph, pf, pu))
    else:
        hit("POWER:REALISED_NA")
        L.append("  REALISED P(UNDETERMINED): NOT COMPUTABLE on this data (measured SE %.5f, Delta-hat %+.4f)" % (se, d))
    return L


def _iv_reading(lo, hi):
    if not (lo == lo and hi == hi):
        return "not estimable"
    return "HELD-side (wholly below %+.2f)" % BAR_T if hi < BAR_T else ("FAILED-side (wholly above %+.2f)" % BAR_T
                                                                       if lo > BAR_T else "UNDETERMINED (contains %+.2f)" % BAR_T)


def usable_line(s):
    """D-G5 / launch condition (E): the usable-only Delta WITH ITS INTERVAL beside the literal one, and whether the
    interval reading differs. Printed; decides nothing (the literal Delta decides, confirmed reading D4(a))."""
    u, dT = s["dTu"], s["dT"]
    lit, usa = _iv_reading(dT["lo_n"], dT["hi_n"]), _iv_reading(u["lo_n"], u["hi_n"])
    if u["n"] == 0:
        hit("USABLE:NA")
        tail = "no usable match: the usable-only interval is not estimable"
    elif lit != usa:
        hit("USABLE:DIFFERS")
        tail = ("the usable-only interval reads %s, the literal one %s: THE READING DIFFERS - the difference is carried by "
                "the %d unusable match(es), counted not-TIE under the literal denominator" % (usa, lit, s["n"] - s["usable"]))
    else:
        hit("USABLE:SAME")
        tail = "the usable-only interval reads %s, the same as the literal one" % usa
    return ("  USABLE-ONLY ESTIMATE beside the literal one (printed, DECIDES NOTHING; the literal Delta decides, confirmed "
            "reading D4(a)): Delta over the %d usable matches = %+.4f (%d task clusters) | interval point +- 1.96 x "
            "clustered SE %.4f = [%+.4f, %+.4f] | percentile [%+.4f, %+.4f] | literal %+.4f - usable-only %+.4f = %+.4f is "
            "what unusable rows (counted not-TIE) contribute toward HELD | %s"
            % (u["n"], u["point"], u["q"], u["sd"], u["lo_n"], u["hi_n"], u["lo_p"], u["hi_p"], dT["point"], u["point"],
               (dT["point"] - u["point"]) if u["n"] else float("nan"), tail))


def underpower_line(s):
    dd = s["deff_dT"]["deff"]
    if not (dd == dd):
        hit("UNDERPOWER:NA")
        return "measured delta-DEFF for Delta NOT ESTIMABLE on this data (iid variance 0); the power statement cannot be made"
    if dd > DEFF_UNDERPOWER:
        hit("UNDERPOWER:YES")
        return ("UNDERPOWERED FOR ITS OWN BAR: the measured delta-DEFF %.3f exceeds %.1f (registration P8 / SUPPORT; the D10 "
                "bracket on this corpus) - recorded beside whatever C1 reads" % (dd, DEFF_UNDERPOWER))
    hit("UNDERPOWER:NO")
    return "measured delta-DEFF %.3f <= %.1f: not underpowered by the registration's own test" % (dd, DEFF_UNDERPOWER)


def score_c2(r):
    lo, hi = r["lo_n"], r["hi_n"]
    if lo == lo and lo >= BAR_A:
        hit("C2:HELD")
        return "HELD", "HELD (no fidelity harm: the interval's lower end %+.4f is at or above %+.2f)" % (lo, BAR_A)
    if hi == hi and hi < BAR_A:
        hit("C2:FAILED")
        return "FAILED", "FAILED (fidelity harm: the interval [%+.4f, %+.4f] lies wholly below %+.2f)" % (lo, hi, BAR_A)
    hit("C2:UND")
    return "UNDETERMINED", "UNDETERMINED (the interval [%+.4f, %+.4f] straddles %+.2f)" % (lo, hi, BAR_A)


def score_c3(r):
    lo, hi = r["lo_n"], r["hi_n"]
    if hi == hi and hi <= BAR_W:
        hit("C3:HELD")
        return "HELD", ("HELD (decisiveness was not bought with errors: the interval's upper end %+.4f is at or below %+.2f)"
                        % (hi, BAR_W))
    if lo == lo and lo > BAR_W:
        hit("C3:FAILED")
        return "FAILED", "FAILED (the interval [%+.4f, %+.4f] lies wholly above %+.2f)" % (lo, hi, BAR_W)
    hit("C3:UND")
    return "UNDETERMINED", "UNDETERMINED (the interval [%+.4f, %+.4f] straddles %+.2f)" % (lo, hi, BAR_W)


def r1_block(s, which="swap"):
    L = ["    " + R1_LINE,
         "    R1 per-contestant agreement with the expected outcome (the contestant's checker pass-share on its sides of the "
         "458; in a checker-disagreeing match exactly one side passes) | the judge's convention-A agreement on the matches "
         "involving it, pilot -> swap:"]
    for ag, d in s["per_contestant"].items():
        L.append("      %-40s passed %3d of %3d = %.4f | judge conv-A pilot %3d / %3d = %.4f -> swap %3d / %3d = %.4f"
                 % (ag, d["passed"], d["n"], d["passed"] / max(1, d["n"]), d["judge_A1"], d["n"],
                    d["judge_A1"] / max(1, d["n"]), d["judge_A2"], d["n"], d["judge_A2"] / max(1, d["n"])))
    L.append("    R1 leakage: assert_no_per_side_verdict executed on %d of %d re-assembled payloads"
             % (s["gate"]["leak_checks"], s["gate"]["n_cells"]))
    return L


def falsifier_lines(c1_key, c3_key, s):
    L = []
    if c1_key == "FAILED":
        hit("FALS:FIRES")
        L += ["FALSIFIER FIRES: THE TEMPLATE-MIS-FIT HYPOTHESIS IS OVERTURNED AT THE GRANULARITY THIS TEST EXAMINES: naming "
              "the FINAL STATE instead of the FINAL ANSWER in the inherited verify-first block does NOT explain the BFCL "
              "pilot's indecision. Consequences adopted BY INSERTION with the outcome: (a) BFCL-JUDGED-PILOT's paragraph "
              "'THE THIRD HYPOTHESIS, WHICH THE OUTCOME FILE NEVER NAMES' and its does_not_show item on template mis-fit are "
              "BRACKETED (the answer / state slot was TESTED AND DOES NOT CARRY THE EFFECT; no number moves); (b) TWO "
              "HYPOTHESES SURVIVE - POSITION BIAS AND CORPUS DIFFICULTY - and the 0.2183 stands as an UNEXPLAINED "
              "DECISIVENESS COLLAPSE; (c) NO FURTHER PROMPT-EDIT SEPARATOR IS BOUGHT ON THIS CORPUS WITHOUT A NEW "
              "REGISTRATION THAT NAMES A MECHANISM THE RECORD HAS NOT SEEN.",
              "(d) A NULL RESULT DOES NOT CLEAR TEMPLATE MIS-FIT IN GENERAL; it clears THESE FOUR STRINGS. It does not show "
              "that the template is well fitted - the rest of the MMLU-Pro furniture ('the question', 'the response', 'its "
              "reasoning') was deliberately left standing - only that THESE FOUR STRINGS do not carry the effect."]
    elif c1_key in ("HELD", "HELD_QUAL"):
        hit("FALS:HELD")
        L += ["falsifier does not fire (C1 %s). What is established is that PART of the indecision is template-borne; it "
              "does NOT establish how much of the REST is position bias, it does NOT restore the 'for Agents' bridge, it "
              "moves NO rung and overturns no rubric result, board, profile, tier or MMLU-Pro number." % c1_key]
    elif c1_key == "UNDETERMINED":
        hit("FALS:UND")
        L += ["falsifier does not fire (C1 UNDETERMINED, a registered outcome): recorded with the measured level-DEFF %.3f "
              "and delta-DEFF %.3f, n_eff %.1f and MDE +-%.3f; no further calls are bought on this question without a "
              "registration that names a design with more support."
              % (s["deff_T"]["deff"], s["deff_dT"]["deff"], s["deff_dT"]["neff"], s["deff_dT"]["mde80"])]
    else:
        hit("FALS:NOT_EVALUATED")
        L += ["falsifier NOT EVALUATED: C1 is UNDETERMINED BY TRIGGER (registrar ruling D2: a fired validity trigger pre-empts "
              "the verdict and the falsifier). Recorded as UNDETERMINED with the measured level-DEFF %.3f and delta-DEFF %.3f, "
              "n_eff %.1f and MDE +-%.3f." % (s["deff_T"]["deff"], s["deff_dT"]["deff"], s["deff_dT"]["neff"],
                                             s["deff_dT"]["mde80"])]
    if c1_key in ("HELD", "HELD_QUAL") and c3_key == "FAILED":
        hit("HARM:YES")
        L.append("HARM RESULT: a HELD C1 WITH A FAILED C3 - decisiveness bought with wrong verdicts. Recorded as a HARM "
                 "result; THE SWAPPED PROMPT IS NOT PROPOSED FOR ANY FUTURE ARM.")
    elif c1_key == "UND_TRIGGER":
        hit("HARM:NOT_EVALUATED")
        L.append("harm clause (C1 HELD with C3 FAILED) NOT EVALUATED: C1 is UNDETERMINED BY TRIGGER (registrar ruling D2)")
    else:
        hit("HARM:NO")
        L.append("harm clause (C1 HELD with C3 FAILED) does not fire: C1 %s, C3 %s" % (c1_key, c3_key))
    return L


def c4_lines(s):
    fp1, fp2 = s["fp1"], s["fp2"]
    L = ["  first-position rate over the swapped arm's non-tie votes: %d / %d = %.4f (Wilson [%.4f, %.4f]; clustered SE %.4f "
         "-> [%.4f, %.4f]; z vs 0.5 = %.2f) | beside the pilot's %d / %d = %.4f (z = %.2f; registered %.4f of %d, z = %.2f)"
         % (fp2["k"], fp2["n"], fp2["point"], fp2["wlo"], fp2["whi"], fp2["sd"], fp2["lo_n"], fp2["hi_n"], fp2["z"],
            fp1["k"], fp1["n"], fp1["point"], fp1["z"], PILOT_FIRST_POS[0], PILOT_FIRST_POS[1], PILOT_FIRST_POS[2]),
         "  flip table over the dual-order TIEs, (fwd vote, rev vote) as posted, swapped arm -> pilot (registered pilot "
         "57 / 0 / 24 / 14 / 3 / 2):"]
    for cls, reg in zip(SIX, PILOT_SIX):
        L.append("    %-24s swap %3d | pilot %3d (registered %d)" % (cls, s["six2"].get(cls, 0), s["six1"].get(cls, 0), reg))
    other2 = {k: v for k, v in s["six2"].items() if k not in SIX}
    L.append("    outside the six classes: swap %s" % (other2 or "none"))
    c2, c1 = s["conc2"], s["conc1"]
    L.append("  per-task tie concentration: swap %d of %d tasks at or above 50%% ties, the top 5 tasks carry %d of %d ties | "
             "pilot %d of %d, top 5 carry %d of %d (registered '11 of 49 tasks, 5 tasks carrying 32 of the 100')"
             % (c2["ge50"], c2["tasks"], c2["top5"], c2["ties"], c1["ge50"], c1["tasks"], c1["top5"], c1["ties"]))
    L.append("  NO BAR: if the swap removes the mis-fit and the first-position rate STAYS near 0.586, position bias is the "
             "surviving explanation - a DIRECTION this design can print but not adjudicate.")
    ok = bool(fp2["n"] > 0 and c2["tasks"] > 0)
    if ok:
        hit("C4:HELD")
        L.append("  C4: HELD (all three computed and printed with their denominators)")
    else:
        hit("C4:FAILED")
        L.append("  C4: FAILED (a readout has an empty denominator: non-tie votes %d, tasks %d)" % (fp2["n"], c2["tasks"]))
    return L


def c5_lines(s):
    c5 = s["c5"]
    L = f2_lines(s["gate"], full_diff=False)
    L += ["  (b) unusable rows (content_filter + length + unparsed) %d of %d posted calls (%.4f)"
          % (c5["unusable"], c5["posted"], c5["unusable"] / max(1, c5["posted"])),
          "  (c) finish_reason %s | provider fingerprint %s (expected %s)" % (c5["fins"], c5["provs"], P.EXPECTED_FINGERPRINT),
          "  (d) max completion tokens %s of the %d cap" % (c5["max_ctok"], P.MAXTOK),
          "  (e) truncated sides %d of %d, truncated matches %d of %d, state-over-cap sides %d | CHECKER_TEXT_CUT %d of %d "
          "SCHEDULED TASKS (denominator TASKS, the scheduled ones, not the 57 in the pool: the pilot's D11 fixed)"
          % (c5["trunc_sides"], 2 * s["n"], c5["trunc_matches"], s["n"], c5["state_over"], c5["cut_tasks"], c5["sched_tasks"]),
          "  (f) the leakage assertion executed on %d of %d re-assembled payloads" % (s["gate"]["leak_checks"], s["gate"]["n_cells"]),
          "  (g) " + (s.get("night") or "[NIGHT] not computed")]
    ok = bool(c5["posted"] > 0 and c5["max_ctok"] is not None and s.get("night"))
    if ok:
        hit("C5:HELD")
        L.append("  C5: HELD ((a)-(g) printed)")
    else:
        hit("C5:FAILED")
        L.append("  C5: FAILED (a count could not be printed: posted %d, max completion tokens %s, night line %s)"
                 % (c5["posted"], c5["max_ctok"], "present" if s.get("night") else "absent"))
    return L


def band(tag, x, lo, hi, und=False):
    if not (x == x):
        if und:
            hit("%s:UND" % tag)
            return "UNDETERMINED (not estimable on this data)"
        hit("%s:FAILED" % tag)
        return "FAILED (not computable)"
    if lo <= x <= hi:
        hit("%s:HELD" % tag)
        return "HELD"
    hit("%s:FAILED" % tag)
    return "FAILED"


def prediction_lines(s):
    T2 = s["tie2"]["point"]
    dT = s["dT"]["point"]
    in_T = bool(T2 == T2 and 0.10 <= T2 <= 0.20)                  # D3: the prediction of record is the T_swap form ALONE
    hit("P1:HELD" if in_T else "P1:FAILED")
    p1 = "HELD" if in_T else "FAILED"
    m = s["mcn"]
    p2_ok = bool(m["p"] < 0.01 and 60 <= m["b"] + m["c"] <= 140)
    hit("P2:HELD" if p2_ok else "P2:FAILED")
    dA, dW = s["dA"]["point"], s["dW"]["point"]
    W2 = s["w2"]["point"]
    c5 = s["c5"]
    unus = c5["unusable"] / max(1, c5["posted"])
    pg = s["gate"]["pg"]
    p7_ok = bool(s["gate"]["n_eq"] == N_CELLS and s["gate"]["n_cells"] == N_CELLS and pg["counts"] == [1, 1, 1, 1]
                 and c5["trunc_sides"] == 0)
    hit("P7:HELD" if p7_ok else "P7:FAILED")
    p4ii = bool(W2 == W2 and W2 < PAIR_NOREF_W)
    hit("P4ii:HELD" if p4ii else "P4ii:FAILED")
    p6_ok = bool(unus <= 0.01)
    hit("P6:HELD" if p6_ok else "P6:FAILED")
    return ["  P1 T_swap in [0.10, 0.20] (point 0.15), THE PREDICTION OF RECORD (D3 ruling, 7da2ec5): T_swap %.4f -> %s | "
            "restatement, printed and NEVER scored: Delta in [-0.1183, -0.0183] (point -0.0683): Delta %+.4f"
            % (T2, p1, dT),
            "  P2 exact McNemar p < 0.01 with b + c in [60, 140] (point 95): p = %.4g, b + c = %d -> %s"
            % (m["p"], m["b"] + m["c"], "HELD" if p2_ok else "FAILED"),
            "  P3 A_swap - 0.7402 in [-0.02, +0.10] (point +0.04): %+.4f -> %s" % (dA, band("P3", dA, -0.02, 0.10)),
            "  P4 W_swap - 0.0415 in [0.00, +0.04] (point +0.015): %+.4f -> %s | P4(ii) W_swap below PAIR-NOREF's 0.0930: "
            "%.4f -> %s" % (dW, band("P4", dW, 0.0, 0.04), W2, "HELD" if p4ii else "FAILED"),
            "  P5 first-position rate over the swapped arm's non-tie votes in [0.53, 0.62] (point 0.57): %.4f -> %s"
            % (s["fp2"]["point"], band("P5", s["fp2"]["point"], 0.53, 0.62)),
            "  P6 unusable rows <= 1%% of the 916 posted calls: %d of %d = %.4f -> %s"
            % (c5["unusable"], c5["posted"], unus, "HELD" if p6_ok else "FAILED"),
            "  P7 the F2 gate passes 916 of 916 user turns with exactly 4 replacements, and truncated sides 0 of 916: %d of %d, "
            "counts %s, truncated sides %d -> %s" % (s["gate"]["n_eq"], s["gate"]["n_cells"], pg["counts"], c5["trunc_sides"],
                                                      "HELD" if p7_ok else "FAILED"),
            "  P8 the MEASURED task-clustered DEFF for the paired Delta in [1.2, 3.0] (point 1.9): %.3f -> %s"
            % (s["deff_dT"]["deff"], band("P8", s["deff_dT"]["deff"], 1.2, 3.0, und=True))]


def readout(s):
    dT, dA, dW = s["dT"], s["dA"], s["dW"]
    L = ["=== %s: does the inherited 'final answer' furniture explain the BFCL pilot's indecision? ===" % TEST,
         "  registration %s" % REGISTRATION,
         "  pool %s | judge %s on %s | cap %d | temperature OMITTED | seed %d (the pilot's; bootstrap + posting order) | "
         "protocol: %s" % (POOL_ID, P.JUDGE_MODEL, P.PROVIDER, P.MAXTOK, SEED, PROTOCOL),
         "  %s" % s.get("provenance", "(provenance not recorded: selftest)"),
         "  the pilot on the same %d matches (recomputed from its cache): T %.4f, A %.4f, W %.4f | registered constants "
         "T %.4f, A %.4f, W %.4f" % (s["n"], s["T1"], s["A1"], s["W1"], T_PILOT, A_PILOT, W_PILOT),
         "",
         "=== C1 THE TIE RATE (primary; ONE deciding statistic: the paired delta's task-clustered interval) ===",
         "  " + fmt_level("T_swap", s["tie2"], s["deff_T"], " | LITERAL denominator 458 (an unusable match is not a TIE); "
                          "T over the %d usable matches %.4f, printed, decides nothing" % (s["usable"], s["T2_usable"])),
         "  " + fmt_delta("Delta = T_swap - T_pilot", dT, s["deff_dT"], s["boot"], s["seed"], BAR_T) + r2_chip(dT["point"]),
         usable_line(s),
         "  REQUIRED COMPANION (not a deciding clause): exact two-sided McNemar on the %d paired TIE / not-TIE outcomes: b "
         "(TIE in the pilot, not in the swap) = %d, c (not -> TIE) = %d, exact p = %.4g"
         % (s["n"], s["mcn"]["b"], s["mcn"]["c"], s["mcn"]["p"]),
         "  " + underpower_line(s),
         "  SUPPORT planning values of record: unpaired MDE +-0.102 at the level-DEFF 3.60; paired d = 0.20, delta-DEFF 2.0 -> "
         "SE 0.0295, MDE +-0.083 (80%) / +-0.058 (50%); C1 is scored against the MEASURED delta-DEFF above."]
    L += power_lines(s)
    c1_key, c1_sentence = score_c1(s)
    L += ["  C1: %s%s" % (c1_sentence, r2_chip(dT["point"])),
          "  the point %+.4f is printed and DECIDES NOTHING; the session is a confound bounded (not removed) by the record's "
          "retest floors, which is why the bar is -0.05." % dT["point"]]
    L += ["", "=== C2 CONVENTION-A AGREEMENT (secondary; harm bar; ONE deciding statistic: the paired delta's interval) ==="]
    L += ["  " + fmt_level("A_swap (convention A: ties / INVALID wrong)", s["ok2"], s["deff_A"])]
    L += r1_block(s)
    L += ["  " + fmt_level("A_swap (convention B: committed verdicts only)", s["okB2"], deff_of(s["okB2"]))]
    L += r1_block(s)
    c2_key, c2_sentence = score_c2(dA)
    L += ["  " + fmt_delta("A_swap - A_pilot", dA, s["deff_dA"], s["boot"], s["seed"], BAR_A) + r2_chip(dA["point"]),
          "  C2: %s%s" % (c2_sentence, r2_chip(dA["point"])), "  " + C2_NOTE]
    L += ["", "=== C3 THE WRONG-COMMITTED RATE (secondary; harm bar; ONE deciding statistic) ===",
          "  " + fmt_level("W_swap", s["w2"], s["deff_W"]),
          "  DECOMPOSITION of the swapped arm's %d: right %d + wrong-committed %d + ties %d + unusable %d"
          % (s["n"], s["decomp"].get("right", 0), s["decomp"].get("wrong", 0), s["decomp"].get("tie", 0),
             s["decomp"].get("unusable", 0))]
    L += r1_block(s)
    c3_key, c3_sentence = score_c3(dW)
    L += ["  " + fmt_delta("W_swap - W_pilot", dW, s["deff_dW"], s["boot"], s["seed"], BAR_W) + r2_chip(dW["point"]),
          "  C3: %s%s" % (c3_sentence, r2_chip(dW["point"]))]
    L += ["", "=== FALSIFIER AND THE HARM CLAUSE ==="] + ["  " + x for x in falsifier_lines(c1_key, c3_key, s)]
    L += ["", "=== C4 THE POSITION SIGNATURE (descriptive, no bar) ==="] + c4_lines(s)
    L += ["", "=== C5 INSTRUMENT COUNTS AND GATES ==="] + c5_lines(s)
    L += ["", "=== PREDICTIONS (registered before any code; scored explicitly) ==="] + prediction_lines(s)
    L += ["", "=== THE RULING'S FENCE AND RIDERS; WHAT THIS RUN WILL NOT SHOW (registered) ===",
          "  " + R1_LINE, "  " + FENCE, "  " + IFEVAL_RIDER,
          "  (1) it does not separate position bias from corpus difficulty; (2) it is not a same-session control; (3) no "
          "rung, no ladder position, no 0.75-bar reading; (4) no profile cell, agent ranking, per-trajectory or process "
          "claim; (5) nothing about miss_func / miss_param / long_context, NON_TERMINATED episodes or the grok-FC stratum; "
          "(6) nothing about any other corpus: no MMLU-Pro or MATH result is touched, questioned or re-read."]
    return L, c1_key


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
    mids = [r["mid"] for r in ctx["deciding"]]
    return {"test": TEST, "registration": REGISTRATION, "pool_id": POOL_ID, "judge_model": P.JUDGE_MODEL,
            "provider": P.PROVIDER, "max_tokens": str(P.MAXTOK), "temperature": "omitted", "protocol": PROTOCOL,
            "reference": P.REFERENCE_FORM, "seed": str(SEED), "boot": str(BOOT), "bar_t": str(BAR_T),
            "replacements": json.dumps(REPLACEMENTS), "system_prompt_sha16_new": g["pg"]["new_sha"],
            "system_prompt_sha16_pilot": g["pg"]["old_sha"], "all_payload_anchor": g["anchor"],
            "set_mids": json.dumps(sorted(mids)), "set_sha256_16": set_sha(mids), "n_set": str(len(mids)),
            "schedule_hash": ctx["sched_hash"], "parent_module": "tools/analysis/bfcl_judged_pilot.py",
            "parent_sha256_16_lf": P.SCRIPT_SHA, "system_bfcl": P.SYSTEM_BFCL, "rubric_bfcl": P.RUBRIC_BFCL,
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
    posted = len(votes)
    unus = sum(1 for v in votes.values() if adj(v) == "INVALID")
    mids = {m for m, _ in votes}
    bad_m = {m for (m, _), v in votes.items() if adj(v) == "INVALID"}
    rc, rm = unus / max(1, posted), len(bad_m) / max(1, len(mids))
    ok = bool(rc <= GUARD_RATE and rm <= GUARD_RATE)
    print("[GUARD] %s %s: unusable %d of %d posted calls (%.1f%%), %d of %d matches (%.1f%%) -> %s"
          % (TEST, what, unus, posted, 100 * rc, len(bad_m), len(mids), 100 * rm, "OK (<= 5%)" if ok else "ABOVE 5%"), flush=True)
    return ok


# ----------------------------------------------------------------------------------------------------------------
# the modes
# ----------------------------------------------------------------------------------------------------------------
def dry_run():
    ctx = load_context()
    g = f2_gate(ctx)
    dec = pilot_decomposition(ctx["deciding"], ctx["D1"])
    tasks = sorted({r["task_id"] for r in ctx["deciding"]})
    print("corpus %s | pilot cache %s (mode=ro&immutable=1) | pilot run_meta schedule_hash %s, seed %s"
          % (rel(P.DB), rel(PILOT_CACHE), ctx["meta_p"].get("schedule_hash"), ctx["meta_p"].get("seed")))
    print("DECIDING SUBSET (headline rows, 7-agent roster, nj / nj_a / nj_b clear): %d mids over %d tasks (registered %d / %d) "
          "| set sha256_16 %s" % (len(ctx["deciding"]), len(tasks), N_DECIDING, N_TASKS_REG,
                                  set_sha([r["mid"] for r in ctx["deciding"]])))
    print("THE PILOT ON THE 458 (the control of record, recomputed): ties %d, right %d, wrong-committed %d, unusable %d | "
          "of record 100 / 339 / 19 -> T %.4f A %.4f W %.4f" % (dec["ties"], dec["right"], dec["wrong"], dec["invalid"],
                                                                 dec["ties"] / N_DECIDING, dec["right"] / N_DECIDING,
                                                                 dec["wrong"] / N_DECIDING))
    n_chk, split_bad = split_check([r["task_id"] for r in ctx["deciding"]])
    print("SPLIT: %d scheduled tasks recomputed under split_side.tier_b %s -> %s"
          % (n_chk, split_side.NORMALISER_VERSION, "all EVAL" if not split_bad else "REFUSED: %s" % split_bad[:3]))
    fa, fs, n = f1_counts(ctx)
    print("F1 (ruling section 5; the regex is this instrument's operationalisation): artefact sides naming a 'final answer' "
          "(%s) %d of %d | sides carrying a non-empty final state_info %d of %d -> the object 'FINAL ANSWER' %s"
          % (F1_RE.pattern, fa, n, fs, n, "HAS NO REFERENT in any deciding artefact" if fa == 0 else
             "DOES appear in %d artefact(s): denotation failure is NOT total" % fa))
    print("THE FOUR REPLACEMENTS (in order; each must match exactly once):")
    for line in f2_lines(g, full_diff=True):
        print(line)
    print("CELL-BY-CELL user-turn sha16 (mid, arm, this script's, the parent module's):")
    for mid, arm, own, par in g["cells"]:
        print("  %d %s %s %s %s" % (mid, arm, own, par, "=" if own == par else "MISMATCH"))
    P.configure_rr()
    body = P.post_body(system_prompt(), assemble_user(ctx["deciding"][0], "fwd", ctx)) if ctx["deciding"] else P.post_body("s", "u")
    P.assert_body_copy(body)
    print("judge %s on %s | max_tokens %d | temperature OMITTED (body keys %s)" % (P.JUDGE_MODEL, P.PROVIDER, P.MAXTOK, tuple(body)))
    print("BILL: %d user turns assembled, 0 posted | --pilot %d = %d calls (the %d LOWEST mids of the 458) | --run the "
          "remaining %d | ceiling %d = expected" % (2 * len(ctx["deciding"]), PILOT_MATCHES, 2 * PILOT_MATCHES, PILOT_MATCHES,
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
    what = "--run" if mode == "run" else "--pilot %s" % n
    go_gate(what)
    if mode == "pilot" and n != PILOT_MATCHES:
        raise SystemExit("[PILOT] REFUSED: the registered pilot is --pilot %d (the %d lowest mids); got %r"
                         % (PILOT_MATCHES, PILOT_MATCHES, n))
    ctx = load_context()
    g = f2_gate(ctx)
    for line in f2_lines(g, full_diff=False):
        print(line)
    bad = refusals(ctx, g)
    if bad:
        raise SystemExit("[REFUSED] 0 calls: %s" % "; ".join(bad))
    P.configure_rr()
    P.assert_body_copy(P.post_body("s", "u"))
    rr.load_env()
    con = open_cache()
    pin_meta(con, current_meta(ctx, g))
    rows = ctx["deciding"]
    pilot_rows = rows[:PILOT_MATCHES]
    have = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    if mode == "run":
        pilot_cells = {(r["mid"], a) for r in pilot_rows for a in ("fwd", "rev")}
        if not pilot_cells <= have:
            raise SystemExit("[GUARD] REFUSED: --run needs the %d pilot cells cached and read by the truncation guard first "
                             "(%d of %d cached)" % (len(pilot_cells), len(pilot_cells & have), len(pilot_cells)))
        if not truncation_guard(raw_votes(con, "verdicts", [r["mid"] for r in rows]), "cached before --run"):
            raise SystemExit("[GUARD] REFUSED: above 5% unusable; nothing more is posted.")
    target = pilot_rows if mode == "pilot" else rows
    todo = [(r, a) for r in target for a in ("fwd", "rev") if (r["mid"], a) not in have]
    random.Random("%d:%s" % (SEED, what)).shuffle(todo)
    stamp = "%s %s" % (what, time.strftime("%Y-%m-%d %H:%M:%S"))
    con.executemany("INSERT INTO posting_order VALUES (?,?,?,?)", [(stamp, i, r["mid"], a) for i, (r, a) in enumerate(todo)])
    con.commit()
    night_line(len(todo), what)
    system = system_prompt()
    jobs = [(r["mid"], arm, system, assemble_user(r, arm, ctx)) for r, arm in todo]
    print("%s %s: %d calls to post (target %d matches) | workers %d | cache %s" % (TEST, what, len(jobs), len(target),
                                                                                 workers, rel(CACHE)), flush=True)
    ok_n, err, fins = post_counted(con, jobs, workers, what)
    truncation_guard(raw_votes(con, "verdicts", [r["mid"] for r in target]), what)
    print("done: ok %d, errors %d (errors are never cached). --analyze for the readout." % (ok_n, err), flush=True)
    print(dbguard_line())


def analyze(boot=BOOT):
    ctx = load_context()
    if not os.path.exists(CACHE):
        raise SystemExit("no cache at %s: nothing judged, nothing written" % rel(CACHE))
    g = f2_gate(ctx)
    rows = ctx["deciding"]
    con = sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)
    try:
        meta = dict(con.execute("SELECT key, value FROM run_meta"))
        votes2 = raw_votes(con, "verdicts", [r["mid"] for r in rows])
        D2 = P.dual(con, rows)
    finally:
        con.close()
    night_line(0, "--analyze (0 calls)")
    problems = []
    if meta.get("set_sha256_16") != set_sha([r["mid"] for r in rows]):
        problems.append("the cache's pinned set is not the re-derived one")
    if meta.get("script_sha256_16") != SCRIPT_SHA:
        problems.append("the cache was produced by script LF sha %s, this script is %s" % (meta.get("script_sha256_16"), SCRIPT_SHA))
    if len(votes2) < N_CELLS:
        problems.append("PARTIAL: %d of %d cells not cached" % (N_CELLS - len(votes2), N_CELLS))
    cut = sum(ctx["refs"][t][1] for t in {r["task_id"] for r in rows})
    s = compute(rows, ctx["votes1"], votes2, ctx["D1"], D2, g, dict(cut_tasks=cut), boot, SEED)
    s["night"] = _NIGHT_LINE
    s["provenance"] = ("cache %s (mode=ro) | run_meta script_sha256_16 %s (LF) | this script LF %s / working-tree %s | "
                       "parent LF %s | new system prompt sha16 %s (pilot's %s) | started %s | resumed %s"
                       % (rel(CACHE), meta.get("script_sha256_16"), SCRIPT_SHA, script_sha_raw(), P.SCRIPT_SHA,
                          g["pg"]["new_sha"], g["pg"]["old_sha"], meta.get("started"), meta.get("resumed", "-")))
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
def _right(r):
    return ("Model A", "Model B") if r["checker_winner"] == r["agent_a"] else ("Model B", "Model A")


def _wrong(r):
    return ("Model B", "Model A") if r["checker_winner"] == r["agent_a"] else ("Model A", "Model B")


def _synthetic(p2_rule, tmp):
    """458 synthetic matches over 49 tasks whose synthetic pilot (table p1) has the pilot's decomposition of record
    (100 ties in the registered six classes, 339 right, 19 wrong); pass 2 (table verdicts) from p2_rule(i, row)."""
    classes = [c for c, n in zip(SIX, PILOT_SIX) for _ in range(n)]
    roster = ["ag%d" % k for k in range(7)]
    rows = []
    for i in range(N_DECIDING):
        a, b = roster[i % 7], roster[(i // 7 + i + 1) % 7] if roster[(i // 7 + i + 1) % 7] != roster[i % 7] else roster[(i + 3) % 7]
        rows.append(dict(mid=700_000_000 + i, task_id="multi_turn_base_%d" % (i % N_TASKS_REG), agent_a=a, agent_b=b,
                         checker_winner=a if i % 2 else b, nj="", nj_a="", nj_b="", trunc_a=0, trunc_b=0,
                         state_over_a=0, state_over_b=0))
    path = os.path.join(tmp, CACHE_DB_NAME)
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    for t in ("p1", "verdicts"):
        con.execute("CREATE TABLE %s (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, ts REAL, "
                    "finish TEXT, ctokens INTEGER, provider TEXT, max_tokens INTEGER, PRIMARY KEY (mid, arm))" % t)
    for i, r in enumerate(rows):
        v1 = classes[i] if i < 100 else (_right(r) if i < 439 else _wrong(r))
        for arm, vote in zip(("fwd", "rev"), v1):
            con.execute("INSERT INTO p1 VALUES (?,?,?,?,?,?,?,?,?,?,?)", (r["mid"], arm, vote, 0.8, 0, "", 0, "stop", 300,
                                                                        P.EXPECTED_FINGERPRINT, P.MAXTOK))
        out = p2_rule(i, r, v1)
        if out is None:
            continue
        fv, rv, fin = out
        for arm, vote in (("fwd", fv), ("rev", rv)):
            con.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?,?)", (r["mid"], arm, vote, 0.8, int(vote == "INVALID"),
                                                                              "", 0, fin, 350, P.EXPECTED_FINGERPRINT, P.MAXTOK))
    con.commit()
    return rows, con


def _synthetic_gate(ok=True):
    pg = dict(ok=True, counts=[1, 1, 1, 1], counts_full=[1, 1, 1, 1], new_sha="n" * 16, old_sha=PILOT_SYSTEM_PROMPT_SHA, ops=[],
              confined=True, reapplied_equal=True, slots=True, residual_final_answer=0, old_final_answer=4, old="", new="")
    return dict(ok=ok, pg=pg, anchor=ALL_PAYLOAD_ANCHOR, n_eq=N_CELLS if ok else N_CELLS - 1, n_cells=N_CELLS,
                mism=[] if ok else ["mid 1 fwd: synthetic"], cells=[], slots_ok=True, sched_ok=True, leak_checks=N_CELLS)


def _run_synthetic(rows, con, gate_ok=True, night="[NIGHT] selftest line"):
    mids = [r["mid"] for r in rows]
    v1, v2 = raw_votes(con, "p1", mids), raw_votes(con, "verdicts", mids)
    D1, D2 = P.dual(con, rows, "p1"), P.dual(con, rows, "verdicts")
    dec = pilot_decomposition(rows, D1)
    assert (dec["ties"], dec["right"], dec["wrong"]) == (100, 339, 19), dec
    s = compute(rows, v1, v2, D1, D2, _synthetic_gate(gate_ok), dict(cut_tasks=0), 300, SEED)
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
    deciding = [dict(mid=700_000_000 + i, task_id="multi_turn_base_%d" % (i % N_TASKS_REG), agent_a=roster[i % 7],
                     agent_b=roster[(i + 1) % 7], checker_winner=roster[i % 7], nj="", nj_a="", nj_b="")
                for i in range(N_DECIDING)]
    D1 = {}
    for i, r in enumerate(deciding):
        w = "TIE" if i < 100 else (r["checker_winner"] if i < 439 else r["agent_b"])
        D1[r["mid"]] = dict(winner=w, flip=int(w == "TIE"), invalid=0, pending=0)
    meta_p = dict(judge_model=P.JUDGE_MODEL, max_tokens=str(P.MAXTOK), temperature="omitted", seed="42", pool_id=POOL_ID)
    ctx = dict(deciding=deciding, D1=D1, meta_p=meta_p)
    db = _fixture_corpus(tmp, [r["task_id"] for r in deciding])
    ok_g = dict(ok=True)
    assert refusals(ctx, ok_g, db) == [], refusals(ctx, ok_g, db)
    d99 = dict(D1)
    d99[deciding[0]["mid"]] = dict(D1[deciding[0]["mid"]], winner=deciding[0]["checker_winner"], flip=0)
    t48 = [dict(r, task_id="multi_turn_base_0") if r["task_id"] == "multi_turn_base_48" else r for r in deciding]
    off = [dict(r) for r in deciding]
    off[0]["agent_b"] = P.SELF_PREF_AGENT
    cases = ((dict(ctx, deciding=deciding[:-1]), ok_g, "deciding subset is 457"),
             (dict(ctx, D1=d99), ok_g, "the pilot's ties on the 458 is 99"),
             (dict(ctx, D1=d99), ok_g, "the pilot's right on the 458 is 340"),
             (dict(ctx, deciding=t48), ok_g, "occupy 48 tasks"),
             (ctx, dict(ok=False), "the F2 gate did not pass"),
             (dict(ctx, meta_p=dict(meta_p, seed="137")), ok_g, "pilot run_meta seed"),
             (dict(ctx, deciding=off), ok_g, "off the 7-agent headline roster"))
    for c, g, why in cases:
        bad = refusals(c, g, db)
        assert any(why in b for b in bad), (why, bad)
    db = _fixture_corpus(tmp, [r["task_id"] for r in deciding], train={"multi_turn_base_7"})
    assert any(b.startswith("SPLIT:") for b in refusals(ctx, ok_g, db)), "a TRAIN-side task must refuse"
    os.remove(db)
    return 1 + len(cases) + 1


def selftest():
    tmp = tempfile.mkdtemp(prefix="bfcl_final_state_swap_selftest_")
    n_opened_before = len(_OPENED)
    BRANCHES_HIT.clear()
    # 1. the DB guard
    for bad_db in P.FORBIDDEN_DB_BASENAMES + ("rejudge_grok.db", "bfcl_flip_reseed.db"):
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
    assert "temperature" not in b and rr.payload_body("s", "u") == b
    # 3. THE ONE KNOB on the REAL template (zero DB): counts 1/1/1/1, the diff confined to the four spans, slots intact
    pg = prompt_gate()
    assert bool(pg["ok"]) and pg["counts"] == [1, 1, 1, 1] and pg["counts_full"] == [1, 1, 1, 1], pg["counts"]
    assert bool(pg["confined"]) and bool(pg["reapplied_equal"]) and bool(pg["slots"]) and pg["old_sha"] != pg["new_sha"]
    assert pg["old_sha"] == PILOT_SYSTEM_PROMPT_SHA, pg["old_sha"]
    assert pg["residual_final_answer"] == 0 and pg["old_final_answer"] == 4, (pg["residual_final_answer"], pg["old_final_answer"])
    assert P.RUBRIC_BFCL in pg["new"] and P.SYSTEM_BFCL in pg["new"]
    back = pg["new"]
    for frm, to in REPLACEMENTS:                                    # the inverse edit, each TO exactly once
        assert back.count(to) == 1, to
        back = back.replace(to, frm)
    assert back == pg["old"], "the edit is not exactly the four strings"
    #    the refusals: a FROM string absent (0) or doubled (2) REFUSES
    for broken in (pg["old"].replace(REPLACEMENTS[0][0], "X"), pg["old"] + "\n" + REPLACEMENTS[3][0]):
        try:
            apply_replacements(broken, "selftest")
            raise AssertionError("apply_replacements accepted a count != 1")
        except SystemExit as e:
            assert "[SWAP] REFUSED" in str(e)
    #    a stray edit outside the four spans is caught by the confinement test
    ops = char_diff(pg["old"], pg["new"].replace("Bias suppression", "Bias supression"))
    spans = [(pg["old"].index(f), pg["old"].index(f) + len(f)) for f, _ in REPLACEMENTS]
    assert not all(any(s0 <= i1 and i2 <= s1 for s0, s1 in spans) for _, i1, i2, _, _, _, _ in ops)
    # 4. the all-payload anchor is the review's recipe
    pay = {5: ("S", "u1", "u2"), 9: ("S", "v1", "v2")}
    h = hashlib.sha256()
    for m in (5, 9):
        s_, a_, b_ = pay[m]
        h.update(("%d|" % m).encode("utf-8")); h.update(s_.encode("utf-8")); h.update(a_.encode("utf-8")); h.update(b_.encode("utf-8"))
    assert all_payload_anchor([dict(mid=5), dict(mid=9)], lambda r: pay[r["mid"]]) == h.hexdigest()[:16]
    # 5. McNemar exact, write-once, meta pinning, the guard, the READY gate, the night ceiling, the CLI shapes
    assert mcnemar_exact(0, 0) == 1.0 and abs(mcnemar_exact(10, 0) - 2 / 1024) < 1e-12
    out, outp = os.path.join(tmp, "outcome.txt"), os.path.join(tmp, "pilot.txt")
    assert write_outcome("one\n", [], out, outp) == "written"
    assert write_outcome("two\n", [], out, outp) == "exists" and open(out, encoding="utf-8").read() == "one\n"
    assert write_outcome("p\n", ["partial"], out, outp) == "pilot"
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
    okv = {(1, "fwd"): ("TIE", "stop", 1, ""), (1, "rev"): ("Model A", "stop", 1, "")}
    badv = dict(okv); badv[(2, "fwd")] = ("INVALID", "stop", 1, "")
    assert bool(truncation_guard(okv, "selftest")) and not bool(truncation_guard(badv, "selftest"))
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
    # 6. END-TO-END readouts on synthetic caches
    same = lambda i, r, v1: (v1[0], v1[1], "stop")                                                   # noqa: E731
    scen = {
        # every tie converted to the RIGHT verdict: T 0, Delta -0.218, C2 HELD (A up), C3 HELD
        "held": lambda i, r, v1: (_right(r) + ("stop",)) if i < 100 else same(i, r, v1),
        # nothing moves: Delta 0 -> FAILED, the R2 chip, the falsifier
        "failed": same,
        # 23 of the 100 ties converted: Delta ~ -0.05 -> the interval contains the bar
        "und_interval": lambda i, r, v1: (_right(r) + ("stop",)) if i < 23 else same(i, r, v1),
        # 50 non-tie matches unusable in BOTH orders (100 rows, > 5% of calls) with a straddling interval -> UNDETERMINED
        "und_trigger": lambda i, r, v1: ("INVALID", "INVALID", "stop") if 150 <= i < 200 else
                                        ((_right(r) + ("stop",)) if i < 23 else same(i, r, v1)),
        # 80 of the 100 ties turned UNUSABLE: counted not-TIE, Delta wholly below the bar, AND the 5% trigger -> the trigger
        # PRE-EMPTS the one-sided interval: UNDETERMINED (BY TRIGGER), never HELD
        "overlap": lambda i, r, v1: ("INVALID", "Model A", "stop") if i < 80 else same(i, r, v1),
        # every tie committed WRONG: C1 HELD and C3 FAILED -> the HARM clause
        "harm": lambda i, r, v1: (_wrong(r) + ("stop",)) if i < 100 else same(i, r, v1),
        # C2 FAILED: 60 right verdicts turned wrong
        "c2fail": lambda i, r, v1: (_wrong(r) + ("stop",)) if 100 <= i < 160 else same(i, r, v1),
        # the pilot launch only
        "partial": lambda i, r, v1: None if i >= 12 else same(i, r, v1),
    }
    texts = {}
    for name, rule in scen.items():
        rows, con = _synthetic(rule, tmp)
        s = _run_synthetic(rows, con, night=None if name == "partial" else "[NIGHT] selftest line")
        con.close()
        L, key = readout(s)
        texts[name] = (key, "\n".join(L), s)
    assert texts["held"][0] == "HELD" and "falsifier does not fire (C1 HELD)" in texts["held"][1], texts["held"][0]
    assert texts["failed"][0] == "FAILED" and "FALSIFIER FIRES" in texts["failed"][1]
    assert "A NULL RESULT DOES NOT CLEAR TEMPLATE MIS-FIT IN GENERAL; it clears THESE FOUR STRINGS" in texts["failed"][1]
    assert "R2: DESCRIPTIVE-ONLY" in texts["failed"][1]
    assert texts["und_interval"][0] == "UNDETERMINED" and "contains -0.05" in texts["und_interval"][1], texts["und_interval"][1][:3000]
    assert texts["und_trigger"][0] == "UND_TRIGGER" and "BY TRIGGER: unusable rows exceed 5%" in texts["und_trigger"][1]
    assert texts["overlap"][0] == "UND_TRIGGER" and "wholly below -0.05; that reading is pre-empted" in texts["overlap"][1]
    assert "falsifier NOT EVALUATED" in texts["overlap"][1] and "C1: HELD" not in texts["overlap"][1]
    assert "HARM RESULT" not in texts["overlap"][1] and "FALSIFIER FIRES" not in texts["und_trigger"][1]
    assert "harm clause (C1 HELD with C3 FAILED) NOT EVALUATED" in texts["overlap"][1]
    assert "HARM RESULT" in texts["harm"][1] and "C3: FAILED" in texts["harm"][1]
    assert "C2: FAILED" in texts["c2fail"][1]
    for key_, txt, s in texts.values():
        for must in (R1_LINE, "reference-wrong stratum is EMPTY BY CONSTRUCTION", C2_NOTE, FENCE, "REQUIRED COMPANION",
                     "MEASURED delta-DEFF", "MEASURED level-DEFF", "[F2 GATE] (a)", "R1 per-contestant agreement",
                     "DECOMPOSITION", "USABLE-ONLY ESTIMATE", C1_RESTATED, "POWER AGAINST THE BAR -0.05 OF RECORD",
                     "PLANNING SE 0.02955 (recomputed)", "MEASURED SE"):
            assert must in txt, "the readout lost the sentence of record %r" % must[:70]
        assert txt.count("R1 per-contestant agreement") == 3, "R1 must sit beside EVERY accuracy (conv A, conv B, W)"
    # 7. the branches no natural dataset reaches, by the SAME scoring functions readout uses, on crafted numbers
    base = texts["und_interval"][2]
    qual = dict(base, dT=dict(base["dT"], lo_n=-0.20, hi_n=-0.10, point=-0.15), mcn=dict(b=10, c=5, p=0.30))
    assert score_c1(qual)[0] == "HELD_QUAL" and "HELD ON THE INTERVAL, NOT CORROBORATED BY THE PAIRED TEST" in score_c1(qual)[1]
    falsifier_lines("HELD_QUAL", "FAILED", qual)
    gate_fail = dict(base, gate=_synthetic_gate(False))
    assert score_c1(gate_fail)[0] == "UND_TRIGGER"
    #    EACH trigger pre-empts an interval wholly on EACH side of the bar (D2): never HELD / FAILED when a trigger fires
    held_iv = dict(base["dT"], lo_n=-0.20, hi_n=-0.10, point=-0.15)
    failed_iv = dict(base["dT"], lo_n=-0.01, hi_n=0.01, point=0.0)
    for iv, side in ((held_iv, "below"), (failed_iv, "above")):
        for trig in (dict(usable=250), dict(gate=_synthetic_gate(False)),
                     dict(c5=dict(base["c5"], unusable=60, posted=916))):
            t = dict(base, dT=iv, mcn=dict(b=100, c=0, p=1e-9))
            t.update(trig)
            k, sentence = score_c1(t)
            assert k == "UND_TRIGGER" and "BY TRIGGER" in sentence and "wholly %s -0.05; that reading is pre-empted" % side \
                in sentence, sentence
            assert falsifier_lines(k, "FAILED", t)[0].startswith("falsifier NOT EVALUATED")
    assert score_c3(dict(lo_n=-0.01, hi_n=0.08, point=0.03))[0] == "UNDETERMINED"
    assert score_c2(dict(lo_n=-0.08, hi_n=0.01, point=-0.03))[0] == "UNDETERMINED"
    for dd in (5.0, 2.0, float("nan")):
        underpower_line(dict(base, deff_dT=dict(base["deff_dT"], deff=dd)))
    #    P1 on T_swap ALONE (D3), at both edges of [0.10, 0.20] and just outside them; the Delta form never decides
    for T2, want in ((0.10, "HELD"), (0.20, "HELD"), (0.0999, "FAILED"), (0.2001, "FAILED"), (0.15, "HELD"), (0.30, "FAILED")):
        line = prediction_lines(dict(base, tie2=dict(base["tie2"], point=T2), dT=dict(base["dT"], point=T2 - 0.2183)))[0]
        assert ("-> %s |" % want) in line and "NEVER scored" in line, line
    for p, bc, dA, dW, fp, un, dd in ((0.001, 95, 0.04, 0.015, 0.57, 0, 1.9), (0.5, 10, -0.5, 0.5, 0.9, 50, 9.0),
                                      (0.5, 10, -0.5, 0.5, 0.9, 50, float("nan"))):
        prediction_lines(dict(base, mcn=dict(b=bc, c=0, p=p), dA=dict(base["dA"], point=dA), dW=dict(base["dW"], point=dW),
                              w2=dict(base["w2"], point=0.2 if dW > 0.1 else 0.05), fp2=dict(base["fp2"], point=fp),
                              c5=dict(base["c5"], unusable=un, posted=916, trunc_sides=0 if un == 0 else 3),
                              gate=_synthetic_gate(un == 0), deff_dT=dict(base["deff_dT"], deff=dd)))
    c4_lines(dict(base, fp2=dict(base["fp2"], n=0), conc2=dict(base["conc2"], tasks=0)))
    #    D-G5: the power block reproduces the registrar's table at the planning SE (section (B)), to the printed digit
    ph, pf, pu, ht, ft, d80h, d80f = power_at(-0.0683, PLANNING_SE)
    assert (round(ht, 4), round(ft, 4), round(ph, 3), round(pf, 3), round(pu, 3)) == (-0.1079, 0.0079, 0.090, 0.005, 0.905)
    assert (round(1 - _phi((ft - 0.0) / PLANNING_SE), 3), round(d80h, 4), round(d80f, 4)) == (0.394, -0.1328, 0.0328)
    #    each branch of the power and usable-only lines, on crafted numbers (the same functions readout uses)
    power_lines(dict(base, dT=dict(base["dT"], sd=0.0)))
    power_lines(dict(base, dT=dict(base["dT"], sd=0.03, point=-0.06)))
    ivd = lambda lo, hi, n: dict(base["dT"], lo_n=lo, hi_n=hi, n=n, point=(lo + hi) / 2)          # noqa: E731
    assert "THE READING DIFFERS" in usable_line(dict(base, dT=ivd(-0.20, -0.10, 458), dTu=ivd(-0.08, 0.02, 400)))
    assert "the same as the literal one" in usable_line(dict(base, dT=ivd(-0.02, 0.02, 458), dTu=ivd(-0.01, 0.03, 450)))
    assert "not estimable" in usable_line(dict(base, dTu=dict(base["dTu"], n=0)))
    c5_lines(dict(base, night=None))
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
    opened = _OPENED[n_opened_before:]
    tmp_norm = os.path.normcase(os.path.abspath(tmp)).replace("\\", "/")
    for p in opened:
        pp = os.path.normcase(os.path.abspath(p.split("?", 1)[0].replace("file:", ""))).replace("\\", "/")
        assert p == ":memory:" or pp.startswith(tmp_norm), "the selftest opened a path outside its temp dir: %s" % p
    print("selftest OK: %d of %d declared print branches EXECUTED (C1 incl. the qualified HELD and each of the three "
          "validity triggers PRE-EMPTING an interval wholly on either side of the bar, R2, UNDERPOWERED, C2-C5, the "
          "falsifier incl. NOT EVALUATED, the HARM clause, P1-P8 with P1 on T_swap at both edges), "
          "coverage asserted complete | THE ONE KNOB on the real template: counts %s, diff confined to the four spans, "
          "pilot system prompt sha16 %s -> new %s, 'final answer' 4 -> 0 | the count refusals (0 and 2 matches) | a stray "
          "edit caught by the confinement test | DB guard (forbidden names, the pilot cache refused without "
          "mode=ro&immutable=1) | parent pin %s | body copy vs rr.payload_body, no temperature | the review's all-payload "
          "recipe | exact McNemar | write-once (mode x) | run_meta refuses any changed key incl. the script sha | "
          "truncation guard | READY gate | night ceiling | CLI shapes %s each refused at go_gate | %d sqlite opens, all "
          "inside %s | 0 calls"
          % (len(BRANCHES_HIT), len(ALL_BRANCHES), pg["counts"], pg["old_sha"], pg["new_sha"], PARENT_SHA_PINNED,
             ", ".join("launch%r" % (sh,) for sh in shapes), len(opened), tmp))
    print(dbguard_line())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="%s - %s" % (TEST, REGISTRATION))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="post the %d LOWEST mids of the 458 (%d calls); gated" % (PILOT_MATCHES, 2 * PILOT_MATCHES))
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
