"""BFCL-JUDGED-PILOT - where does the deployed recipe's agreement with the BFCL CHECKER_OUTPUT sit on the reference
ladder, and is it above 0.75? (judged; expected 1,316 calls, ceiling 3,096). REGISTERED 2026-09-23 BEFORE ANY CODE OR
CALL in docs/judge_v2_program.md L10965-L11146, commit 22c5d5f ("Registered 2026-09-23 ... BFCL-JUDGED-PILOT"); the
night's B1 under plan Amendment 9 (docs/plan_2026-09-15.md L316-L363, hard ceiling 14,000 grok calls).

  python tools/analysis/bfcl_judged_pilot.py --selftest      synthetic corpus in memory; every guard exercised; opens no file of
                                                             record, no network, 0 calls
  python tools/analysis/bfcl_judged_pilot.py --dry-run       the BFCL pool id first; the corpus counts recomputed and printed BESIDE
                                                             the registration's; the schedule; every payload assembled; the artefact
                                                             cap and the non-judgeable class counted; the bill; 0 calls; no cache
  python tools/analysis/bfcl_judged_pilot.py --probe         the item-19 max_tokens PREFLIGHT on the TRACE-SHAPED prompt: 50 matches
                                                             = 100 calls into the `probe` table; NEVER an arm, its rows never enter A
  python tools/analysis/bfcl_judged_pilot.py --pilot 12      the first 12 matches of the headline deck = 24 calls, INSIDE the 922;
                                                             read by the truncation guard (REFUSES above 5% unusable)
  python tools/analysis/bfcl_judged_pilot.py --run           every remaining match of both strata; resume = relaunch
  python tools/analysis/bfcl_judged_pilot.py --analyze       refuses a partial cache; writes the outcome of record write-once

THE GATE (placement_steps.py's rule, verbatim in shape): --probe, --pilot and --run REFUSE, fail-closed and before any
file is opened, unless the environment variable BFCL_GO equals "9" (plan Amendment 9) AND docs/reviews/
READY_bfcl_judged_pilot.md exists, is tracked by git and carries no uncommitted change (the reviewer's READY of record;
Amendment 6 L222-L225, Amendment 9 clause (d)). --selftest, --dry-run and --analyze never post and are never gated.

HYGIENE - WHAT THIS SCRIPT MAY OPEN, AND HOW THE READY CERTIFIES IT BY COMMAND.
There is NO POOL OF RECORD to assert here and pool_guard IS NOT IMPORTED: this test spends only on BFCL episodes and
touches no MMLU-Pro or union row (p2dca21ab5f4ef3ae and paeec37aa28063c75 are never read, never named as a denominator
and never written). The BFCL pool of record p2035adddedd1becb is printed FIRST, read from the FILE NAME of the
write-once experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json (a plain JSON read, no hashing, no
pool_guard), and the 57 EVAL base ids in the corpus DB are asserted IDENTICAL to that file's "BFCL/base" list.
Exactly TWO sqlite files may be opened by this process, enforced at import by a wrapper around sqlite3.connect:
  experiment_results/agent/bfcl_result_2025-12-16.db   READ-ONLY, mode=ro&immutable=1 (the corpus; built write-once by
                                                       tools/ingest/bfcl_ingest.py; never written here)
  experiment_results/agent/bfcl_judged_pilot.db        this test's OWN cache (the only file this script writes to)
Any other database - twenty_newsgroups_cache_v1.db, embeddings_cache.db, snapshots.db, snapshots_frozen.db,
mmlu_pro_dataset_cache_v2.db, multicorpus_cache_v1.db, any verdict cache, board or ratings DB - raises SystemExit from
the wrapper, from this module or from any module it imports, BEFORE the connection is made. Every launch prints, as its
last line, "[DBGUARD] sqlite3.connect: <n> call(s): <paths>", so the READY certifies the claim by reading one printed
line of the dry-run and by one grep:
  grep -n "sqlite3.connect\|_guarded_connect\|pool_guard" tools/analysis/bfcl_judged_pilot.py
Raw files are read READ-ONLY and as text only: experiment_results/agent/bfcl_raw/2025-12-16/dataset/
BFCL_v4_multi_turn_base.json (the task's user turns) and result/<agent>/multi_turn/BFCL_v4_multi_turn_base_result.json
(the decoded call sequence and the final state_info), exactly the files the admission pilot re-read.

INSTRUMENT (registration "Instrument", taken literally).
 JUDGE      grok-4-1-fast-non-reasoning on azure, max_tokens 8192, TEMPERATURE OMITTED from the body (never sent; plan
            Amendment 1 D2; the script REFUSES to post if anything has set rejudge_reasoning.TEMPERATURE), DUAL ORDER
            with TIE ON FLIP and NO THIRD CALL, every call through rejudge_reasoning.call_judge_full (finish_reason,
            completion tokens and the deployment fingerprint recorded per call; an HTTP 400 content_filter is cached as
            an unusable row, never re-posted, never dropped from the guard denominator: CONTEXT rule 10). The local
            body copy post_body() is asserted against the SOURCE of rejudge_reasoning.payload_body (rule 9).
 FINGERPRINT canary_baseline.py's fail-closed rule (added at ea9fbc7) carried over: the 2nd element of call_judge_full
            must be "azure:grok-4-1-fast-non-reasoning" or the run STOPS with a [FINGERPRINT] line and NOTHING is
            cached for that match; the only exemption is rr's deterministic sentinel "azure:refusal" with
            finish_reason content_filter, which rule 10 requires cached as an unusable row. provider1 / provider2 are
            columns of the cache and the fingerprint counter is printed in the GUARD line and in --analyze's header.
 RECIPE     rubric-less in the sense the registration fixes: no induced, anchor, leaf or corpus rubric exists for BFCL
            and none is minted (the rubric line is CLOSED). The system prompt is built exactly as STAGE3-MATH built it
            (stage3_math.system_prompt): prompt_v2.v2_system_template() with the corpus-level SYSTEM_BFCL / RUBRIC_BFCL
            strings in the template's $systemPrompt / $rubric slots + rejudge_grok.SCHEMA_INSTRUCTION; the user turn is
            rejudge_grok.build_user_prompt(task + reference block, artefact A, artefact B). SYSTEM_BFCL / RUBRIC_BFCL
            are the ONLY text this test adds; they are printed in full by --dry-run with the first payload.
 REFERENCE  the PER-TASK EXPECTED OUTCOME, as the ruling BFCL-REF-ORACLE fixed it (programme L11001, commit 6ccf2f7,
            amending the registration by insertion BEFORE the READY and before any call): the corpus's own GROUND-TRUTH
            CALL SEQUENCE for the task, read from experiment_results/agent/bfcl_raw/2025-12-16/dataset/possible_answer/
            BFCL_v4_multi_turn_base.json (one JSON object per line, 'id' + 'ground_truth' = a list of turns, each a list
            of calls). It is rendered ONCE PER TASK, IDENTICAL FOR BOTH SIDES, attached to the TASK STATEMENT and never
            to a trace, so it is ORDER-INVARIANT and this test has NO TRANSPOSITION HAZARD. The block carries NO
            per-side verdict, NO per-side error text, NO error_type, NO PASS / FAIL, NO all_pass, NO statement about
            which side the checker passed, and NOT the 'actual' side of checker_details - this script never reads
            checker_details at all. Its header names it the corpus's ground-truth sequence and says it is ONE correct
            solution and not necessarily the only one (BFCL's own file is named possible_answer and the checker is
            state-based: a different sequence reaching the same final state passes); it does NOT instruct the judge to
            defer to it. A rendered block longer than REFERENCE_TEXT_CAP characters is cut with a marked "[... cut ...]"
            and COUNTED (class CHECKER_TEXT_CUT, amendment item (5)(a)); because the block is per task the cut is
            identical in both orders - symmetry is automatic, not enforced - and ITS DENOMINATOR IS TASKS, NOT SIDES.
            The block sits OUTSIDE the per-episode artefact cap (that cap governs each side's trace) and its rendered
            length is printed per task by --dry-run and in the outcome. THE REJECTED PER-SIDE FORM is FORBIDDEN in this
            test, in the cache, the outcome, the ledger, the thesis and the blog; assert_no_per_side_verdict() checks
            every assembled task statement for it and is the ONLY path on which ORACLE_HAZARD can print - it fires on no
            path this ruling leaves live, and the READY certifies that by command.
 ARTEFACT   per side: the decoded call sequence (handler_log model_response_decoded, in step order) + the final
            `state_info`, re-read from the raw result file exactly as tools/analysis/agent_admission_pilot.artefact_text
            reads it (this module's parts() is ASSERTED to rejoin to that function's output byte for byte).
 CAP        the experiment-manager's reversible choice (i): 2,500 ESTIMATED TOKENS per episode, estimated as chars / 4
            with no tokenizer (the unit the admission pilot measured in: median 453, p95 2,422, max 7,199) = 10,000
            characters. SYMMETRIC: the same cap and the same rule on both sides of a match (the two sides are distinct
            episodes, so the cap is not a shared budget and equal lengths are not imposed). The FINAL state_info IS
            ALWAYS RETAINED IN FULL - it is the outcome the checker reads and may never be the part that is dropped;
            when the state alone exceeds the cap the whole call sequence is dropped and the side is counted in the
            separate class STATE_OVER_CAP. Otherwise whole decoded calls are kept from the FRONT and from the BACK
            (front first, alternating, each within half of the remaining budget, then any leftover budget to the front)
            and the dropped middle is replaced by the MARKER below, so the opening and the closing calls always survive.
            Every truncation is MARKED in the prompt, stored per side in the cache and COUNTED per side and per match in
            the guard line and in the outcome (class ARTEFACT_OVER_CAP; never a silent truncation, never a dropped
            match). The MARKER ITSELF (about 180 characters) is added ON TOP of the capped text (amendment item
            (5)(b)), so a marked artefact may exceed the cap by the marker's length: the cap governs the artefact text
            BEFORE the marker and both lengths are printed. The per-task reference block is NOT inside this cap.
 ROSTER     the experiment-manager's reversible choice (ii): the 8 ingested agents, TERMINATED EPISODES ONLY under
            bfcl_term_v1, no agent excluded by name; grok-4-1-fast-reasoning-FC is held out as a SEPARATE
            SELF-PREFERENCE STRATUM (C3) that never enters the headline A, so the HEADLINE roster is the other 7. A
            NON_TERMINATED (CAP_HIT / ERROR) episode is a class in the denominator of the termination readout, is never
            judged, is never a verdict and is never a tie.
 STRATUM    the BASE stratum alone, EVAL side (57 tasks). miss_func / miss_param / long_context are REFUSED for judged
            cells by AGENT-CORPUS-ADMISSION and are not read here.
 FILTER     the CHECKER-DISAGREEMENT filter (the analogue of the key-decidable filter; MATCH-FILTER / FILTER-BOARD):
            a (task, pair) match is kept iff BOTH episodes are TERMINATED under bfcl_term_v1, BOTH are CHECKER-DECIDED
            (passed, or a failure whose error_type is one of the four state/response types AGENT-CORPUS-ADMISSION fixed)
            and the two checker outcomes DIFFER. The share kept and the count under the weaker reading (pass-differs
            only, without the both-decided clause) are both printed.
 C2 CLASS   the EMPTY / DEGENERATE trace class, declared NON-JUDGEABLE HERE, BEFORE ANY COUNT AND BEFORE ANY CALL, by
            this rule: an episode is NON-JUDGEABLE iff (a) EMPTY - it has ZERO non-blank decoded calls in the whole
            episode (a blank call is "", "[]", "{}" or whitespace); or (b) DEGENERATE - its checker error_type is
            multi_turn:empty_turn_model_response AND its decoded-call text, excluding the final state_info, is blank
            under the same rule (the trace's entire content is the empty-turn failure). A MATCH is non-judgeable iff
            EITHER side is. Non-judgeable matches are JUDGED AND CACHED (they are inside the registered 461 and A is
            reported over all 461 as well) but are EXCLUDED FROM THE DECIDING SUBSET, which is the reading of record
            for C1; their share is printed with its denominator BEFORE A is read. The admission run's 18.3%
            `empty_turn_model_response` share is a DIFFERENT object (an error_type share, not a trace shape) and is
            printed BESIDE the registered class so P5 can be read against both.

COUNTS OF RECORD (the experiment-manager's, from the DB on 2026-09-23; THIS REGISTRATION'S DENOMINATORS). Headline
7-agent roster: 1,113 (task, pair) matches -> 461 after the filter = 922 calls. grok-FC self-preference stratum: 385 ->
147 = 294 calls. Probe 50 matches = 100 calls. Pilot 12 matches = 24 calls, INSIDE the 922. CEILING 3,096, EXPECTED
1,316. The dry-run RECOMPUTES all four from the DB and prints each beside the registered number; a difference is
REPORTED (the recomputed count then being the denominator of record, registration C1) and a difference of more than
COUNT_DELTA_TOL = 5% of the registered number REFUSES every posting launch, naming the count.

PROMPT STRINGS (amendment item (2): APPROVED as a fact of this test). The instrument adds exactly TWO corpus-level
constants, SYSTEM_BFCL and RUBRIC_BFCL, in the v2 template's $systemPrompt / $rubric slots, following STAGE3-MATH. This
reopens no closed line: nothing is INDUCED (no model wrote them, no data was read to write them) and there is no
anchor-level, leaf-level or per-cell rubric - they are the same bytes on every match and in both orders. Neither string
names the checker's verdict, promises that the reference is correct, or tells the judge to defer to it. They are PRINTED
IN FULL by --dry-run, are THE REVIEWER'S TO APPROVE in the READY, are PINNED in run_meta, and a relaunch differing on
them is REFUSED; a change after the first posted call is a DIFFERENT INSTRUMENT and needs a new registration.

GUARDS. The 12-match pilot is read by the truncation guard and the next launch REFUSES above 5% unusable (unparsed +
non-terminated + content_filter) on the DECIDING subset; --analyze refuses a partial cache and writes the outcome of
record ONLY from a complete one (a partial or pilot readout goes to bfcl_judged_pilot_PILOT.txt and never touches the
outcome of record, which is write-once). No cached row is ever re-posted. run_meta is pinned at the first launch (test,
registration, judge, provider, protocol, reference form, max_tokens, temperature "omitted", the two rosters, the
artefact cap, the schedule hash the two prompt strings, the sha256 of the two raw files read, and the script's
LF sha256[:16]) and any later launch differing on a pinned key is REFUSED. THE CUMULATIVE NIGHT CALL COUNT IS PRINTED AT EVERY LAUNCH against the 14,000-call hard ceiling of Amendment 9
and the launch that would cross it is REFUSED, not trimmed: the count is read from the shared night ledger
experiment_results/night_calls_2026-09-23.json when the operator keeps one (a JSON list of {"test", "launch", "calls",
"ts"} objects, appended by this script after every posting launch) and, when there is none, from this test's own cache
alone with the line saying so - the operator's count governs either way (Amendment 9 clause (e)). That file is THE
NIGHT'S COUNT OF RECORD (amendment item (4)): append-only, never rewritten, appended with the calls ACTUALLY POSTED
after every posting launch, read by every instrument before it posts, reconciled by the operator from the cache if a
launch dies, and quoted in the outcome; IFEVAL-RESPONSE-ORACLE's instrument reads and appends to the same file.

READOUT (--analyze, all denominators named): C1 A on the deciding subset and on all 461, under convention A (ties,
INVALID and non-terminated wrong) and convention B (committed verdicts only), each with a Wilson interval AND a
question-clustered bootstrap over the 57 tasks whose SD is the DEFF-inflated SE OF RECORD (~0.024 at 461 matches on 57
tasks). THE INTERVAL OF RECORD for C1 (amendment item (5)(d)) is the point +- 1.96 x that clustered SE, with the
PERCENTILE interval, the bootstrap's B and the cluster unit (the 57 TASKS) printed beside it; IF THE TWO INTERVALS
DISAGREE ABOUT THE 0.75 BAR, C1 IS UNDETERMINED and is recorded as such; the position against the 0.75 bar and against the three ladder rungs NONE 0.738 (PAIR-NOREF, MMLU-Pro) /
CACHED_SOLVE 0.865 (STACK-v2, MMLU-Pro) / MATH-checker 0.958 (STAGE3-MATH-CAPFREE, terminated MATH traces), each rung
named with the test and the corpus that measured it and printed under the registration's CROSS-CORPORA CAVEAT (the
rungs were measured on OTHER corpora under the same recipe: the ladder reading is a POSITIONING ACROSS CORPORA, never a
paired test; the only on-corpus contrast is C3). C2 the non-judgeable class. C3 the self-preference stratum beside, and
never in, the headline. C4 the instrument counts. P1-P8 scored HELD / FAILED / UNDETERMINED explicitly.
"""
import argparse
import hashlib
import json
import os
import random
import re
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):                      # agent traces carry non-cp1252 characters
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ----------------------------------------------------------------------------------------------------------------
# THE DB GUARD (hygiene, enforced at import for this module and every module it imports)
# ----------------------------------------------------------------------------------------------------------------
CORPUS_DB_NAME = "bfcl_result_2025-12-16.db"
CACHE_DB_NAME = "bfcl_judged_pilot.db"
ALLOWED_DB_BASENAMES = {CORPUS_DB_NAME, CACHE_DB_NAME, ":memory:"}
# named explicitly so the refusal message can name them; the rule is a WHITELIST, so this set is documentation
FORBIDDEN_DB_BASENAMES = ("twenty_newsgroups_cache_v1.db", "embeddings_cache.db", "snapshots.db", "snapshots_frozen.db",
                          "mmlu_pro_dataset_cache_v2.db", "multicorpus_cache_v1.db", "ratings.db", "ratings_x12.db")
_OPENED = []
_real_sqlite3_connect = sqlite3.connect


def _db_basename(database):
    s = str(database)
    if s == ":memory:" or s.startswith("file::memory:"):
        return ":memory:"
    if s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
    return os.path.basename(s.replace("\\", "/"))


def _guarded_connect(database, *args, **kwargs):
    """Every sqlite3.connect in this process, from this module or any module it imports, passes here. Only the corpus DB
    and this test's own cache may be opened; anything else is a SystemExit BEFORE the connection is made. Every opened
    path is recorded and printed as the launch's last line so a reviewer certifies the claim by reading one line."""
    base = _db_basename(database)
    if base not in ALLOWED_DB_BASENAMES:
        raise SystemExit("[DBGUARD] REFUSED: %s may open only %s; a connection to %r (%s) was attempted. Nothing of "
                         "record outside the BFCL corpus is read by this test (forbidden by name, among others: %s)."
                         % (os.path.basename(__file__), sorted(ALLOWED_DB_BASENAMES), str(database), base,
                            ", ".join(FORBIDDEN_DB_BASENAMES)))
    _OPENED.append(str(database))
    return _real_sqlite3_connect(database, *args, **kwargs)


sqlite3.connect = _guarded_connect

import agent_admission_pilot as aap   # noqa: E402  the admission pilot's artefact reader (imports split_side only; opens no DB at import)
import rejudge_grok as rj             # noqa: E402  prompt templates, parse_judge, combine_orders (opens no DB at import)
import rejudge_reasoning as rr        # noqa: E402  the judge call of record (rule 9)

# ----------------------------------------------------------------------------------------------------------------
# constants of record
# ----------------------------------------------------------------------------------------------------------------
TEST = "BFCL-JUDGED-PILOT"
REGISTRATION = "docs/judge_v2_program.md L10965-L11146, commit 22c5d5f (registered 2026-09-23, before any code or call)"
BFCL_POOL_ID = "p2035adddedd1becb"
SNAPSHOT = "2025-12-16"
STRATUM = "base"

AGENT_DIR = os.path.join(ROOT, "experiment_results", "agent")
DB = os.path.join(AGENT_DIR, CORPUS_DB_NAME)
CACHE = os.path.join(AGENT_DIR, CACHE_DB_NAME)
RAW_DIR = os.path.join(AGENT_DIR, "bfcl_raw", SNAPSHOT)
POOL_JSON = os.path.join(ROOT, "experiment_configs", "reserved_pool_frozen_bfcl_%s.json" % BFCL_POOL_ID)
OUT = os.path.join(AGENT_DIR, "bfcl_judged_pilot_outcome.txt")          # write-once, only from a complete cache
OUT_PILOT = os.path.join(AGENT_DIR, "bfcl_judged_pilot_PILOT.txt")      # pilot / partial, overwritable
OUT_PROBE = os.path.join(AGENT_DIR, "bfcl_judged_pilot_probe.txt")      # the item-19 preflight, write-once
READY = os.path.join(ROOT, "docs", "reviews", "READY_bfcl_judged_pilot.md")
GO_ENV, GO_VALUE = "BFCL_GO", "9"                                       # plan Amendment 9
NIGHT_LEDGER = os.path.join(ROOT, "experiment_results", "night_calls_2026-09-23.json")
NIGHT_CEILING = 14000

JUDGE_MODEL = "grok-4-1-fast-non-reasoning"
PROVIDER = "azure"
MAXTOK = 8192
TEMPERATURE = None                                                      # OMITTED from the body (Amendment 1 D2)
EXPECTED_FINGERPRINT = "azure:" + JUDGE_MODEL                           # call_judge_full's 2nd element
REFUSAL_FINGERPRINT = "azure:refusal"                                   # rr's deterministic content_filter sentinel
FINGERPRINT_NOT_RECORDED = "not recorded"

SELF_PREF_AGENT = "grok-4-1-fast-reasoning-FC"
ROSTER_ALL = ("DeepSeek-V3.2-Exp-FC", "Qwen_Qwen3-32B-FC", "Salesforce_Llama-xLAM-2-70b-fc-r",
              "claude-sonnet-4-5-20250929-FC", "gemini-2.5-flash-FC", "gpt-5.2-2025-12-11-FC",
              "grok-4-1-fast-reasoning-FC", "meta-llama_Llama-3.3-70B-Instruct-FC")
HEADLINE_ROSTER = tuple(a for a in ROSTER_ALL if a != SELF_PREF_AGENT)  # the 7 of the headline A

# AGENT-CORPUS-ADMISSION's checker-decided rule, copied from agent_admission_pilot.DECIDED_TYPES and asserted equal to it
DECIDED_TYPES = {"multi_turn:instance_state_mismatch", "multi_turn:execution_response_mismatch",
                 "multi_turn:empty_turn_model_response", "multi_turn:method_invoke_order_mismatch"}
EMPTY_TURN_TYPE = "multi_turn:empty_turn_model_response"
BLANK_CALLS = {"", "[]", "{}", '""', "null", "[]\n"}

ARTEFACT_CAP_TOKENS = 2500                                              # the manager's choice (i), reversible
CHARS_PER_TOKEN = 4                                                     # chars / 4, no tokenizer (the admission unit)
ARTEFACT_CAP_CHARS = ARTEFACT_CAP_TOKENS * CHARS_PER_TOKEN              # 10,000
TRUNC_MARKER = ("\n[... %d of %d decoded tool calls omitted from the middle of this trace: the episode exceeded the "
                "per-episode artefact cap of %d estimated tokens (characters / 4). The first and last calls and the "
                "FINAL state are shown in full. ...]\n")
STATE_OVER_CAP_MARKER = ("[The whole decoded call sequence (%d calls) is omitted: the FINAL state alone exceeds the "
                         "per-episode artefact cap of %d estimated tokens (characters / 4). The final state is shown "
                         "in full.]\n")
REFERENCE_TEXT_CAP = 1200                                               # class CHECKER_TEXT_CUT; DENOMINATOR = TASKS (amendment (5)(a))
REFERENCE_CUT_MARKER = "\n[... ground-truth sequence cut at %d characters ...]"

REGISTERED_COUNTS = {"headline_matches": 1113, "headline_filtered": 461, "grok_matches": 385, "grok_filtered": 147}
COUNT_DELTA_TOL = 0.05                                                  # relative; above this every posting launch refuses
PROBE_MATCHES = 50
PILOT_MATCHES = 12
GUARD_RATE = 0.05
MIN_DECIDING = 300                                                      # C1: below this the outcome is UNDETERMINED
BAR = 0.75                                                              # the falsifier bar
SE_OF_RECORD = 0.024                                                    # the registration's DEFF-inflated SE at 461 / 57
LADDER = (("NONE", 0.738, "PAIR-NOREF", "MMLU-Pro"),
          ("CACHED_SOLVE", 0.865, "STACK-v2 (0.849 GROK-CALIB)", "MMLU-Pro"),
          ("CHECKER_OUTPUT (MATH)", 0.958, "STAGE3-MATH-CAPFREE", "terminated MATH traces"))
CROSS_CORPORA_CAVEAT = ("the three rungs were measured on OTHER corpora under the same recipe, so this ladder reading is "
                        "a POSITIONING ACROSS CORPORA, never a paired test; the only on-corpus contrast in this test is "
                        "the C3 self-preference stratum")
# A STANDING WARNING about the REJECTED per-side form (ruling BFCL-REF-ORACLE, programme L11001, commit 6ccf2f7). It is
# printed on exactly ONE path - assert_no_per_side_verdict()'s refusal - and that path is unreachable under the reference
# of record, so it fires on NO live path; the READY certifies that by command (grep ORACLE_HAZARD: one definition, one
# use, inside a SystemExit).
ORACLE_HAZARD = ("[ORACLE-HAZARD] a per-side checker verdict reached the prompt. That is the REJECTED form: FRAMEWORK "
                 "L37, \"putting the key in the reference block is the ORACLE condition (+16.4pp, UPHELD), which is not "
                 "the deployed condition\". The reference of record is the PER-TASK EXPECTED OUTCOME, identical for both "
                 "sides; A must be a BLIND verification rate or it cannot be placed on the ladder at all.")
SEED = 42
BOOT = 2000
MID0_HEADLINE = 700_000_000
MID0_GROK = 700_500_000

# the only prompt text this test adds; the $systemPrompt / $rubric slots of prompt_v2's v2 template, as STAGE3-MATH
# filled them with GEN-ARENA's MATH pair. No induced, anchor, leaf or corpus rubric exists for BFCL and none is minted.
SYSTEM_BFCL = ("You are judging two attempts by tool-using agents at the same multi-turn function-calling task. Each "
               "attempt is shown as its decoded tool-call sequence followed by the final environment state. The task "
               "statement carries the corpus's own ground-truth call sequence for the task: one sequence that solves "
               "it, not necessarily the only one.")
RUBRIC_BFCL = ("Rank by: (1) whether the attempt reaches the outcome the task asks for, read against the ground-truth "
               "sequence and against your own reading of the task; (2) whether the calls are valid and in an order "
               "that could produce that outcome; (3) whether the final environment state is the state the task asks "
               "for. A different sequence that reaches the same final state is as good; an attempt that does not reach "
               "the outcome cannot win on style, on length or on the number of calls.")
# rendered ONCE PER TASK, identical for both sides, attached to the TASK STATEMENT: order-invariant, no per-side verdict
REF_BLOCK = ("\n\n[Ground-truth call sequence for this task, from the corpus's own possible_answer file. It is ONE "
             "correct solution and not necessarily the only one: the task's checker is state-based, so a different "
             "sequence that reaches the same final state also solves the task.]\n%s")
# the material the ruling FORBIDS in the block; assert_no_per_side_verdict() refuses on any of it (fires on no live path)
FORBIDDEN_IN_BLOCK = ("multi_turn:", "all_pass", "[Outcome checker report]")
PROTOCOL = ("BFCL-JUDGED-PILOT: prompt_v2 verify-first system template + corpus-level SYSTEM_BFCL / RUBRIC_BFCL slots + "
            "SCHEMA_INSTRUCTION; reference = the PER-TASK EXPECTED OUTCOME (the corpus's ground-truth call sequence, "
            "possible_answer), rendered once per task, identical for both sides, attached to the task statement and "
            "OUTSIDE the artefact cap, carrying no per-side verdict (ruling BFCL-REF-ORACLE, programme L11001, commit "
            "6ccf2f7); artefact per side = decoded call sequence + final state_info capped at %d estimated tokens "
            "(chars/4) with the final state always retained; dual order, TIE on flip, no third call; INVALID if an "
            "order is unparsed or finish_reason is length or content_filter" % ARTEFACT_CAP_TOKENS)
REFERENCE_FORM = "EXPECTED_OUTCOME (per-task ground-truth call sequence; no per-side verdict)"
# the v2 template's own sentence "The question carries a reference solution (marked as produced independently; it may be
# wrong)" is INHERITED from the frozen recipe (STAGE3-MATH disclosed the same inheritance). It is kept for comparability
# with the rung this test positions itself against, it does not tell the judge to defer, and it is stated in the outcome.
V2_INHERITED_NOTE = ("the v2 template's inherited sentence \"The question carries a reference solution (marked as "
                     "produced independently; it may be wrong)\" is kept verbatim for comparability with STAGE3-MATH's "
                     "0.958 rung, which carried it too; it does not instruct the judge to defer to the reference")

OVERRIDE_GUARD = False
_NIGHT_LINE = None


def rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return p


def script_sha_lf():
    """sha256[:16] of this file with CRLF normalised to LF, so a CRLF checkout pins the same value as an LF one."""
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def script_sha_raw():
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


SCRIPT_SHA = script_sha_lf()


def dbguard_line():
    seen = []
    for p in _OPENED:
        if p not in seen:
            seen.append(p)
    return ("[DBGUARD] sqlite3.connect: %d call(s) in this process: %s | whitelist %s | never opened: %s"
            % (len(_OPENED), ", ".join(rel(p.split("?", 1)[0].replace("file:", "")) for p in seen) or "(none)",
               sorted(ALLOWED_DB_BASENAMES), ", ".join(FORBIDDEN_DB_BASENAMES)))


# ----------------------------------------------------------------------------------------------------------------
# the gate (placement_steps.py's shape)
# ----------------------------------------------------------------------------------------------------------------
def git_tracked_clean(path):
    try:
        t = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        h = subprocess.run(["git", "log", "-1", "--format=%h", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception as e:                                   # noqa: BLE001
        return False, False, "git unavailable: %s" % e
    return t, c, h


def gate_state():
    have = os.environ.get(GO_ENV)
    exists = os.path.exists(READY)
    tracked, clean, head = git_tracked_clean(READY) if exists else (False, False, "")
    ok = have == GO_VALUE and exists and tracked and clean
    if not exists:
        state = "MISSING"
    elif tracked and clean:
        state = "exists, committed %s" % head
    elif not tracked:
        state = "exists, NOT committed (untracked)"
    else:
        state = "exists, uncommitted change"
    return ok, "%s=%r (needs %r) | %s %s" % (GO_ENV, have, GO_VALUE, rel(READY), state)


def go_gate(what):
    ok, s = gate_state()
    if not ok:
        raise SystemExit("[READY] %s refused (0 calls, nothing opened): %s. Nothing is posted - the probe and the pilot "
                         "included - until the reviewer's READY is committed (plan Amendment 6 L222-L225; Amendment 9 "
                         "clause (d))." % (what, s))
    print("[READY] %s" % s)


# ----------------------------------------------------------------------------------------------------------------
# the night's ceiling (Amendment 9 clause (e))
# ----------------------------------------------------------------------------------------------------------------
def night_ledger_read():
    """(calls already counted tonight, source sentence). Fail-closed on a malformed ledger."""
    if not os.path.exists(NIGHT_LEDGER):
        return None, "no shared night ledger at %s" % rel(NIGHT_LEDGER)
    try:
        rows = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
        total = sum(int(r["calls"]) for r in rows)
    except Exception as e:                                   # noqa: BLE001
        raise SystemExit("[NIGHT] REFUSED: %s is unreadable (%s: %s); the cumulative count against the %d-call ceiling "
                         "cannot be formed, so nothing is posted." % (rel(NIGHT_LEDGER), type(e).__name__, str(e)[:120], NIGHT_CEILING))
    return total, "%s (%d launch rows)" % (rel(NIGHT_LEDGER), len(rows))


def own_posted_calls():
    if not os.path.exists(CACHE):
        return 0
    con = open_cache_ro()
    n = 0
    for t in ("verdicts", "probe"):
        try:
            n += con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
        except sqlite3.Error:
            pass
    con.close()
    return n


def night_line(planned, what):
    """Printed at EVERY launch; the launch that would cross the ceiling is REFUSED, not trimmed."""
    global _NIGHT_LINE
    ledger, src = night_ledger_read()
    own = own_posted_calls()
    if ledger is None:
        cum, how = own, "%s; counting THIS TEST'S OWN posted calls only (%d cached rows) - the operator's count governs" % (src, own)
    else:
        cum, how = ledger, "%s; this test's own cache holds %d posted rows" % (src, own)
    line = ("[NIGHT] cumulative grok calls tonight %d of %d (Amendment 9 hard ceiling; the COUNT OF RECORD is the night "
            "ledger %s, amendment item (4): append-only, appended with the calls ACTUALLY posted after every posting "
            "launch, read before posting) | this launch (%s) would post at most %d -> %d | source: %s"
            % (cum, NIGHT_CEILING, rel(NIGHT_LEDGER), what, planned, cum + planned, how))
    _NIGHT_LINE = line
    print(line, flush=True)
    if cum + planned > NIGHT_CEILING:
        raise SystemExit("[NIGHT] REFUSED, not trimmed (Amendment 9 clause (e)): %d + %d = %d would cross the %d-call "
                         "ceiling. A refused launch is recorded as refused with the count that refused it; it is never "
                         "silently re-scoped." % (cum, planned, cum + planned, NIGHT_CEILING))
    return cum


def night_ledger_append(calls, what):
    rows = []
    if os.path.exists(NIGHT_LEDGER):
        try:
            rows = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
        except Exception:                                    # noqa: BLE001
            return                                           # night_line already refused on a malformed ledger
    rows.append({"test": TEST, "launch": what, "calls": int(calls), "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
    tmp = NIGHT_LEDGER + ".tmp"
    os.makedirs(os.path.dirname(NIGHT_LEDGER), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1)
    os.replace(tmp, NIGHT_LEDGER)
    print("[NIGHT] appended %d posted calls for %s to %s" % (calls, what, rel(NIGHT_LEDGER)), flush=True)


# ----------------------------------------------------------------------------------------------------------------
# the corpus (mode=ro&immutable=1) and the BFCL pool id
# ----------------------------------------------------------------------------------------------------------------
def pool_line():
    """The FIRST line of every launch. No pool_guard: there is no pool of record to assert here."""
    if not os.path.exists(POOL_JSON):
        raise SystemExit("[POOL] REFUSED: %s is missing; the BFCL EVAL side of record cannot be certified." % rel(POOL_JSON))
    ids = json.load(open(POOL_JSON, encoding="utf-8"))
    base = sorted(int(i) for i in ids["BFCL/%s" % STRATUM])
    print("[POOL] BFCL pool of record %s: %d EVAL %s tasks, id read from the FILE NAME of %s (no hashing, pool_guard NOT "
          "imported: this test has no MMLU-Pro pool of record and touches no p2dca21ab5f4ef3ae / paeec37aa28063c75 row)"
          % (BFCL_POOL_ID, len(base), STRATUM, rel(POOL_JSON)))
    return base


class Corpus:
    """The BFCL ingest DB, mode=ro&immutable=1. Nothing else of record is opened."""

    def __init__(self, db_path=DB, pool_base_ids=None):
        if not os.path.exists(db_path):
            raise SystemExit("[CORPUS] REFUSED: %s is missing (it is untracked and lives only in the main checkout; run "
                             "this from there)." % rel(db_path))
        uri = "file:%s?mode=ro&immutable=1" % db_path.replace("\\", "/")
        con = sqlite3.connect(uri, uri=True)
        try:
            self.meta = dict(con.execute("SELECT key, value FROM meta"))
            self.agents = [r[0] for r in con.execute("SELECT agent FROM agents ORDER BY agent")]
            self.tasks = {r[0]: {"category": r[1], "family_id": r[2], "side": r[3], "turns": r[4], "involved": r[5]}
                          for r in con.execute("SELECT task_id, category, family_id, side, turns, involved_classes FROM tasks")}
            self.eps = {}
            for r in con.execute("SELECT task_id, agent, passed, checker_output, error_type, bfcl_term_v1, "
                                 "termination_class, checker_sha FROM episodes"):
                self.eps[(r[0], r[1])] = {"task_id": r[0], "agent": r[1], "passed": r[2], "checker_output": r[3],
                                          "error_type": r[4], "bfcl_term_v1": r[5], "termination_class": r[6],
                                          "checker_sha": r[7]}
        finally:
            con.close()
        self.db_path = db_path
        missing = [a for a in ROSTER_ALL if a not in self.agents]
        if missing:
            raise SystemExit("[CORPUS] REFUSED: the registered roster names agents the corpus does not carry: %s" % missing)
        self.eval_base = sorted(t for t, v in self.tasks.items() if v["category"] == STRATUM and v["side"] == "EVAL")
        if pool_base_ids is not None:
            got = sorted(int(t.rsplit("_", 1)[1]) for t in self.eval_base)
            if got != sorted(pool_base_ids):
                raise SystemExit("[POOL] REFUSED: the corpus's EVAL %s ids (%d) are not the pool file's (%d); the split "
                                 "of record is not reproduced." % (STRATUM, len(got), len(pool_base_ids)))

    def terminated(self, e):
        return e["bfcl_term_v1"] == "TERMINATED"

    def decided(self, e):
        return e["passed"] == 1 or e["error_type"] in DECIDED_TYPES


# ----------------------------------------------------------------------------------------------------------------
# the artefact: decoded call sequence + final state_info, and the cap
# ----------------------------------------------------------------------------------------------------------------
def parts(entry):
    """(list of decoded calls, final state text) for one raw result entry, ASSERTED to rejoin byte for byte to
    agent_admission_pilot.artefact_text(entry) - the admission pilot's reading of the same artefact."""
    calls = []
    final_state = ""
    log = entry.get("inference_log")
    if not isinstance(log, list):
        return None, None
    for turn in log:
        if isinstance(turn, dict):
            for k in sorted((kk for kk in turn if kk.startswith("step_")), key=lambda s: int(s.split("_")[1])):
                for msg in turn[k]:
                    if isinstance(msg, dict) and msg.get("role") == "handler_log" and "model_response_decoded" in msg:
                        calls.append(json.dumps(msg["model_response_decoded"], ensure_ascii=False))
        elif isinstance(turn, list):
            final_state = json.dumps(turn, ensure_ascii=False, sort_keys=True)
    joined = "\n".join(calls) + "\n" + final_state
    ref = aap.artefact_text(entry)
    assert joined == ref, "parts() no longer rejoins to agent_admission_pilot.artefact_text; the artefact of record moved"
    return calls, final_state


def nonblank(calls):
    return [c for c in calls if c is not None and c.strip() not in BLANK_CALLS and c.strip() != ""]


def nonjudgeable_reason(calls, error_type):
    """The C2 rule, fixed in the header BEFORE any count and any call. -> 'EMPTY' | 'DEGENERATE' | None."""
    if calls is None:
        return "EMPTY"
    if len(nonblank(calls)) == 0:
        return "EMPTY"
    if error_type == EMPTY_TURN_TYPE and len("".join(nonblank(calls)).strip()) == 0:
        return "DEGENERATE"
    return None


def cap_artefact(calls, final_state, cap_chars=ARTEFACT_CAP_CHARS):
    """-> (text, truncated 0/1, kept, total, state_over_cap 0/1, chars_before, chars_after). The FINAL state is always
    retained in full; whole calls are kept from the front and the back (front first, alternating), the dropped middle
    is replaced by the marker. Symmetric: the identical rule and cap on both sides of a match."""
    calls = list(calls or [])
    final_state = final_state or ""
    full = "\n".join(calls) + ("\n" if calls else "") + final_state
    before = len(full)
    if before <= cap_chars:
        return full, 0, len(calls), len(calls), 0, before, before
    budget = cap_chars - len(final_state) - 1
    if budget <= 0:                                           # the final state alone exceeds the cap: keep it, drop the calls
        text = (STATE_OVER_CAP_MARKER % (len(calls), ARTEFACT_CAP_TOKENS)) + final_state
        return text, 1, 0, len(calls), 1, before, len(text)
    head, tail, used = [], [], 0
    i, j = 0, len(calls) - 1
    take_front = True
    while i <= j:
        c = calls[i] if take_front else calls[j]
        half = budget // 2
        room = (half - sum(len(x) + 1 for x in head)) if take_front else (budget - half - sum(len(x) + 1 for x in tail))
        if len(c) + 1 <= room:
            if take_front:
                head.append(c)
                i += 1
            else:
                tail.insert(0, c)
                j -= 1
            used += len(c) + 1
            take_front = not take_front
            continue
        # this side is full; try the other, and stop when neither takes anything
        if take_front and (budget - used) >= 0 and j >= i and len(calls[j]) + 1 <= (budget - used):
            tail.insert(0, calls[j])
            used += len(calls[j]) + 1
            j -= 1
            continue
        if (not take_front) and j >= i and len(calls[i]) + 1 <= (budget - used):
            head.append(calls[i])
            used += len(calls[i]) + 1
            i += 1
            continue
        break
    dropped = len(calls) - len(head) - len(tail)
    marker = TRUNC_MARKER % (dropped, len(calls), ARTEFACT_CAP_TOKENS)
    text = "\n".join(head) + marker + "\n".join(tail) + "\n" + final_state
    return text, 1, len(head) + len(tail), len(calls), 0, before, len(text)


def read_raw_episodes(agents, task_ids, raw_dir=RAW_DIR, category=STRATUM):
    """-> {(task_id, agent): {'calls', 'state'}} read from the raw result files (text, read-only)."""
    out = {}
    want = set(task_ids)
    for agent in agents:
        path = os.path.join(raw_dir, "result", agent, "multi_turn", "BFCL_v4_multi_turn_%s_result.json" % category)
        if not os.path.exists(path):
            raise SystemExit("[RAW] REFUSED: %s is missing; the artefact of record cannot be read for %s." % (rel(path), agent))
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                if e.get("id") in want:
                    calls, state = parts(e)
                    out[(e["id"], agent)] = {"calls": calls, "state": state}
    return out


def read_task_text(task_ids, raw_dir=RAW_DIR, category=STRATUM):
    """-> {task_id: the task's user turns as the judge sees them}. The dataset file, read-only."""
    path = os.path.join(raw_dir, "dataset", "BFCL_v4_multi_turn_%s.json" % category)
    if not os.path.exists(path):
        raise SystemExit("[RAW] REFUSED: %s is missing; the task text of record cannot be read." % rel(path))
    want = set(task_ids)
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get("id") not in want:
                continue
            turns = []
            for k, turn in enumerate(e["question"]):
                for m in turn:
                    if m.get("role") == "user":
                        c = m.get("content")
                        if isinstance(c, list):
                            c = " ".join(b.get("text", "") for b in c if isinstance(b, dict))
                        turns.append("User turn %d: %s" % (k + 1, str(c).strip()))
            out[e["id"]] = "\n".join(turns)
    missing = want - set(out)
    if missing:
        raise SystemExit("[RAW] REFUSED: %d task ids absent from %s (%s)" % (len(missing), rel(path), sorted(missing)[:3]))
    return out, path, file_sha256(path)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_ground_truth(task_ids, raw_dir=RAW_DIR, category=STRATUM):
    """-> ({task_id: [[call, ...] per turn]}, path, sha256) from the corpus's possible_answer file (read-only).
    This is the REFERENCE OF RECORD after the ruling BFCL-REF-ORACLE: per TASK, never per episode."""
    path = os.path.join(raw_dir, "dataset", "possible_answer", "BFCL_v4_multi_turn_%s.json" % category)
    if not os.path.exists(path):
        raise SystemExit("[RAW] REFUSED: %s is missing; the per-task expected outcome of record cannot be read." % rel(path))
    want = set(task_ids)
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get("id") in want:
                out[e["id"]] = e["ground_truth"]
    missing = want - set(out)
    if missing:
        raise SystemExit("[RAW] REFUSED: %d task ids absent from %s (%s)" % (len(missing), rel(path), sorted(missing)[:3]))
    return out, path, file_sha256(path)


def render_reference(ground_truth):
    """The per-task reference block: (text, cut 0/1). Identical for both sides and both orders by construction."""
    lines = []
    for k, turn in enumerate(ground_truth or []):
        calls = turn if isinstance(turn, list) else [turn]
        lines.append("Turn %d: %s" % (k + 1, " ; ".join(str(c) for c in calls)))
    body = "\n".join(lines)
    cut = 0
    if len(body) > REFERENCE_TEXT_CAP:
        body = body[:REFERENCE_TEXT_CAP] + REFERENCE_CUT_MARKER % REFERENCE_TEXT_CAP
        cut = 1
    return REF_BLOCK % body, cut


def assert_no_per_side_verdict(task_statement, ea, eb):
    """The ruling's guard: the assembled TASK STATEMENT (task text + per-task reference block) may carry no per-side
    verdict, no per-side error text, no error_type, no PASS / FAIL and no all_pass. This is the ONLY path on which
    ORACLE_HAZARD can print, and it fires on no path the ruling leaves live."""
    bad = []
    for tag, e in (("Model A", ea), ("Model B", eb)):
        co = (e.get("checker_output") or "").strip()
        if len(co) > 3 and co in task_statement:
            bad.append("%s's checker_output appears in the task statement" % tag)
        et = (e.get("error_type") or "").strip()
        if et and et in task_statement:
            bad.append("%s's error_type %r appears in the task statement" % (tag, et))
    for tok in FORBIDDEN_IN_BLOCK:
        if tok in task_statement:
            bad.append("the forbidden token %r appears in the task statement" % tok)
    for w in ("PASS", "FAIL"):
        if re.search(r"\b%s\b" % w, task_statement):
            bad.append("the forbidden word %r appears in the task statement" % w)
    if bad:
        raise SystemExit("%s\n[RULING] REFUSED (0 calls): the reference of record is the PER-TASK EXPECTED OUTCOME and "
                         "the per-side form is FORBIDDEN (programme L11001, commit 6ccf2f7): %s"
                         % (ORACLE_HAZARD, "; ".join(bad)))


# ----------------------------------------------------------------------------------------------------------------
# the schedule
# ----------------------------------------------------------------------------------------------------------------
def pairs_of(roster):
    r = sorted(roster)
    return [(r[i], r[j]) for i in range(len(r)) for j in range(i + 1, len(r))]


def stratum_matches(c, roster, cross_with=None):
    """All (task, pair) matches of one stratum, with every count the registration names.
    cross_with = the self-preference agent: pairs are (that agent, each of the roster)."""
    pairs = [(SELF_PREF_AGENT, a) for a in sorted(roster)] if cross_with else pairs_of(roster)
    both_term = []
    n_both_present = n_pass_differs = 0
    for t in c.eval_base:
        for a, b in pairs:
            ea, eb = c.eps.get((t, a)), c.eps.get((t, b))
            if ea is None or eb is None:
                continue
            n_both_present += 1
            if not (c.terminated(ea) and c.terminated(eb)):
                continue
            both_term.append((t, a, b, ea, eb))
            if ea["passed"] != eb["passed"]:
                n_pass_differs += 1
    kept = [(t, a, b, ea, eb) for (t, a, b, ea, eb) in both_term
            if c.decided(ea) and c.decided(eb) and ea["passed"] != eb["passed"]]
    return dict(both_present=n_both_present, terminated=len(both_term), pass_differs=n_pass_differs,
                kept=kept, n_kept=len(kept), rows_terminated=both_term)


def build_schedule(c, raws):
    """The fixed deck: headline first (mids from MID0_HEADLINE), then the self-preference stratum (MID0_GROK). Each
    stratum's sides are randomised and the deck shuffled ONCE under seed 42 before ids are assigned, so a --pilot or
    --probe prefix spans tasks and pairs (the design of record: GEN-ARENA / STAGE3-MATH / rejudge_grok)."""
    H = stratum_matches(c, HEADLINE_ROSTER)
    G = stratum_matches(c, HEADLINE_ROSTER, cross_with=SELF_PREF_AGENT)
    rows = []
    for tag, S, mid0 in (("headline", H, MID0_HEADLINE), ("selfpref", G, MID0_GROK)):
        rng = random.Random("%d:%s" % (SEED, tag))
        deck = []
        for t, a, b, ea, eb in sorted(S["kept"]):
            x, y = (a, b) if rng.random() < 0.5 else (b, a)
            deck.append((t, x, y))
        rng.shuffle(deck)
        for i, (t, x, y) in enumerate(deck):
            ea, eb = c.eps[(t, x)], c.eps[(t, y)]
            win = x if ea["passed"] == 1 else y
            ra, rb = raws.get((t, x)), raws.get((t, y))
            fa = artefact_facts(ra, ea)
            fb = artefact_facts(rb, eb)
            nj = fa["nj"] or fb["nj"]
            rows.append(dict(mid=mid0 + i, stratum=tag, task_id=t, agent_a=x, agent_b=y, checker_winner=win,
                             nj=nj or "", nj_a=fa["nj"] or "", nj_b=fb["nj"] or "",
                             trunc_a=fa["trunc"], trunc_b=fb["trunc"], state_over_a=fa["state_over"], state_over_b=fb["state_over"],
                             calls_a=fa["total"], calls_b=fb["total"], kept_a=fa["kept"], kept_b=fb["kept"],
                             chars_a=fa["after"], chars_b=fb["after"], raw_chars_a=fa["before"], raw_chars_b=fb["before"]))
    return rows, H, G


def artefact_facts(raw, ep):
    """Everything about one side that the schedule, the guard line and the outcome need; deterministic, no call."""
    calls = raw["calls"] if raw else None
    state = raw["state"] if raw else ""
    nj = nonjudgeable_reason(calls, ep["error_type"])
    text, trunc, kept, total, state_over, before, after = cap_artefact(calls or [], state)
    return dict(text=text, nj=nj, trunc=trunc, kept=kept, total=total, state_over=state_over,
                before=before, after=after)


def schedule_hash(rows):
    canon = "\n".join("%s:%s:%s:%s" % (r["stratum"], r["task_id"], r["agent_a"], r["agent_b"]) for r in rows)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def count_report(H, G):
    """The registration's denominators beside the recomputed ones. -> (lines, refuse_reason or None)."""
    got = {"headline_matches": H["terminated"], "headline_filtered": H["n_kept"],
           "grok_matches": G["terminated"], "grok_filtered": G["n_kept"]}
    L = ["COUNTS OF RECORD (registration 22c5d5f) beside the DRY-RUN's recomputation from %s (mode=ro&immutable=1):" % rel(DB)]
    bad = []
    for k in ("headline_matches", "headline_filtered", "grok_matches", "grok_filtered"):
        reg, now = REGISTERED_COUNTS[k], got[k]
        d = now - reg
        flag = "" if d == 0 else "   <- DIFFERS by %+d (%.1f%%); the recomputed count is the denominator of record (C1)" % (d, 100.0 * d / reg)
        L.append("  %-18s registered %5d | recomputed %5d%s" % (k, reg, now, flag))
        if abs(d) > COUNT_DELTA_TOL * reg:
            bad.append("%s: registered %d, recomputed %d (%.1f%% > %.0f%%)" % (k, reg, now, 100.0 * abs(d) / reg, 100 * COUNT_DELTA_TOL))
    L.append("  both-present pairs before the termination rule: headline %d, self-preference %d | pass-differs WITHOUT the "
             "both-decided clause: headline %d, self-preference %d (the filter of record adds that clause)"
             % (H["both_present"], G["both_present"], H["pass_differs"], G["pass_differs"]))
    return L, ("; ".join(bad) if bad else None)


# ----------------------------------------------------------------------------------------------------------------
# payloads
# ----------------------------------------------------------------------------------------------------------------
def system_prompt():
    import prompt_v2                                        # imported here, as STAGE3-MATH does; opens no DB
    return (prompt_v2.v2_system_template().replace("$systemPrompt", SYSTEM_BFCL).replace("$rubric", RUBRIC_BFCL)
            + "\n\n" + rj.SCHEMA_INSTRUCTION)


def payloads(row, c, raws, tasktext, refs):
    """(system, user order 1, user order 2) for one match. The reference is PER TASK and identical in both orders: the
    two user turns differ ONLY in the order of the two traces (order-invariance, the ruling's transposition property)."""
    t, a, b = row["task_id"], row["agent_a"], row["agent_b"]
    ea, eb = c.eps[(t, a)], c.eps[(t, b)]
    ta = artefact_facts(raws.get((t, a)), ea)["text"]
    tb = artefact_facts(raws.get((t, b)), eb)["text"]
    q = tasktext[t] + refs[t][0]
    assert_no_per_side_verdict(q, ea, eb)
    return system_prompt(), rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)


def configure_rr():
    rr.PROVIDER = PROVIDER
    rr.JUDGE_MODEL = JUDGE_MODEL
    rr.MAX_TOKENS = MAXTOK
    if rr.TEMPERATURE is not None:
        raise SystemExit("[D2] rejudge_reasoning.TEMPERATURE is %r; Amendment 1 D2 fixes the payload's temperature as "
                         "OMITTED (never sent)" % (rr.TEMPERATURE,))


def post_body(system, user):
    """LOCAL COPY of the body rejudge_reasoning.call_judge_full posts, so the dry-run can print the model field of the
    body that WILL be posted. assert_body_copy() checks it against the SOURCE of rr.payload_body (rule 9)."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None:
        body["temperature"] = rr.TEMPERATURE
    return body


def assert_body_copy(body):
    import inspect
    src = inspect.getsource(rr.payload_body)
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full), "call_judge_full no longer posts payload_body's bytes"
    assert 'payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src \
        and '{"role": "system", "content": system}' in src and '{"role": "user", "content": user}' in src, \
        "rejudge_reasoning.payload_body no longer builds the body post_body() copies; re-verify the copy"
    want = ("model", "max_tokens", "messages") + (("temperature",) if rr.TEMPERATURE is not None else ())
    assert tuple(body) == want, "body key tuple %r != %r" % (tuple(body), want)
    assert TEMPERATURE is None and "temperature" not in body, "the temperature field must never be sent (Amendment 1 D2)"


# ----------------------------------------------------------------------------------------------------------------
# the cache
# ----------------------------------------------------------------------------------------------------------------
def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, stratum TEXT, task_id TEXT, agent_a TEXT, "
                "agent_b TEXT, checker_winner TEXT, nj TEXT, nj_a TEXT, nj_b TEXT, trunc_a INTEGER, trunc_b INTEGER, "
                "state_over_a INTEGER, state_over_b INTEGER, calls_a INTEGER, calls_b INTEGER, kept_a INTEGER, "
                "kept_b INTEGER, chars_a INTEGER, chars_b INTEGER, raw_chars_a INTEGER, raw_chars_b INTEGER)")
    for t in ("verdicts", "probe"):
        con.execute("CREATE TABLE IF NOT EXISTS %s (mid INTEGER, arm TEXT, vote TEXT, conf REAL, invalid INTEGER, raw TEXT, "
                    "ts REAL, finish TEXT, ctokens INTEGER, provider TEXT, max_tokens INTEGER, PRIMARY KEY (mid, arm))" % t)
    con.commit()
    return con


def open_cache_ro():
    return sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)


SCHEDULE_COLS = ("mid", "stratum", "task_id", "agent_a", "agent_b", "checker_winner", "nj", "nj_a", "nj_b", "trunc_a",
                 "trunc_b", "state_over_a", "state_over_b", "calls_a", "calls_b", "kept_a", "kept_b", "chars_a",
                 "chars_b", "raw_chars_a", "raw_chars_b")


def current_meta(sched_hash, n_matches, shas):
    return {"test": TEST, "registration": REGISTRATION, "pool_id": BFCL_POOL_ID, "corpus": os.path.basename(DB),
            "judge_model": JUDGE_MODEL, "provider": PROVIDER, "protocol": PROTOCOL, "reference": REFERENCE_FORM,
            "max_tokens": str(MAXTOK), "temperature": "omitted", "stratum": STRATUM,
            "roster_headline": json.dumps(list(HEADLINE_ROSTER)), "roster_selfpref": json.dumps([SELF_PREF_AGENT]),
            "artefact_cap_tokens": str(ARTEFACT_CAP_TOKENS), "reference_text_cap": str(REFERENCE_TEXT_CAP),
            "schedule_hash": sched_hash, "n_matches": str(n_matches), "seed": str(SEED),
            "system_bfcl": SYSTEM_BFCL, "rubric_bfcl": RUBRIC_BFCL,
            "dataset_sha256": shas.get("dataset", ""), "possible_answer_sha256": shas.get("possible_answer", ""),
            "script_sha256_16_lf": SCRIPT_SHA}


def pin_meta(con, sched_hash, n_matches, shas):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    cur = current_meta(sched_hash, n_matches, shas)
    old = dict(con.execute("SELECT key, value FROM run_meta"))
    if old:
        bad = [(k, old.get(k), v) for k, v in cur.items() if k != "script_sha256_16_lf" and old.get(k) != v]
        if bad:
            raise SystemExit("[META] REFUSED: %s was pinned under a different record:\n  %s\n  (a changed cap, protocol, "
                             "roster, reference form or schedule is a NEW session: move the cache aside and relaunch)"
                             % (rel(CACHE), "\n  ".join("%s: pinned %r | now %r" % b for b in bad)))
        resumed = json.loads(old.get("resumed") or "[]") + [now]
        con.execute("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)", (json.dumps(resumed),))
        if old.get("script_sha256_16_lf") != SCRIPT_SHA:
            con.execute("INSERT OR REPLACE INTO run_meta VALUES ('script_sha256_16_lf_relaunch', ?)", (SCRIPT_SHA,))
            print("  NOTE: cache first produced by script LF sha %s; this script is %s (resume recorded)"
                  % (old.get("script_sha256_16_lf"), SCRIPT_SHA))
    else:
        for k, v in cur.items():
            con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v))
        con.execute("INSERT INTO run_meta VALUES ('started', ?)", (now,))
    con.commit()


def write_schedule(con, rows):
    have = con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]
    tup = [tuple(r[k] for k in SCHEDULE_COLS) for r in rows]
    if have == 0:
        con.executemany("INSERT INTO schedule VALUES (%s)" % ",".join("?" * len(SCHEDULE_COLS)), tup)
        con.commit()
        return
    cached = [tuple(r) for r in con.execute("SELECT %s FROM schedule ORDER BY mid" % ",".join(SCHEDULE_COLS))]
    if cached != sorted(tup):
        raise SystemExit("[SCHEDULE] REFUSED: the cached schedule (%d rows) differs from the recomputed one (%d rows); "
                         "the corpus, the filter or the cap moved under the cache." % (len(cached), len(tup)))


class FingerprintMismatch(Exception):
    """Raised in a worker when a call's deployment fingerprint is not EXPECTED_FINGERPRINT (canary_baseline's rule)."""


def check_fingerprint(mid, arm, provider, finish):
    if provider == EXPECTED_FINGERPRINT:
        return
    if provider == REFUSAL_FINGERPRINT and finish == "content_filter":
        return
    raise FingerprintMismatch("match %d order %s: fingerprint %r != expected %r (finish_reason %r)"
                              % (mid, arm, provider, EXPECTED_FINGERPRINT, finish))


def fingerprint_counts(con, table="verdicts"):
    return Counter(dict(con.execute("SELECT COALESCE(provider,'(none)'), COUNT(*) FROM %s GROUP BY 1" % table)))


# ----------------------------------------------------------------------------------------------------------------
# verdicts and the guard
# ----------------------------------------------------------------------------------------------------------------
def unusable_vote(vote, finish):
    """NON_TERMINATED (finish_reason length) and a content-filter refusal are never a verdict and never a tie."""
    if finish in ("length", "content_filter"):
        return "INVALID"
    return vote


def dual(con, rows, table="verdicts"):
    """-> {mid: dict(winner, flip, invalid, pending, f1, f2)} over the given schedule rows."""
    V = defaultdict(dict)
    mids = [r["mid"] for r in rows]
    for i in range(0, len(mids), 400):
        chunk = mids[i:i + 400]
        q = "SELECT mid, arm, vote, finish FROM %s WHERE mid IN (%s)" % (table, ",".join("?" * len(chunk)))
        for mid, arm, vote, finish in con.execute(q, chunk):
            V[mid][arm] = (vote, finish)
    out = {}
    by_mid = {r["mid"]: r for r in rows}
    for mid in mids:
        d = V.get(mid, {})
        if "fwd" not in d or "rev" not in d:
            out[mid] = dict(winner=None, flip=0, invalid=0, pending=1, f1=d.get("fwd", (None, None))[1], f2=d.get("rev", (None, None))[1])
            continue
        v1 = unusable_vote(*d["fwd"])
        v2 = unusable_vote(*d["rev"])
        w, flip, inv = rj.combine_orders(v1, v2)
        r = by_mid[mid]
        name = {"Model A": r["agent_a"], "Model B": r["agent_b"]}.get(w, w)
        out[mid] = dict(winner=name, flip=int(flip), invalid=int(inv), pending=0, f1=d["fwd"][1], f2=d["rev"][1])
    return out


def guard_numbers(con, rows, table="verdicts"):
    """(n both orders, n unusable, rate, finish counter) on the DECIDING subset (non-judgeable matches removed)."""
    deciding = [r for r in rows if not r["nj"]]
    D = dual(con, deciding, table)
    both = [m for m, v in D.items() if not v["pending"]]
    unus = sum(1 for m in both if D[m]["invalid"])
    fins = Counter()
    mids = [r["mid"] for r in rows]
    for i in range(0, len(mids), 400):
        chunk = mids[i:i + 400]
        for (f,) in con.execute("SELECT COALESCE(finish,'(none)') FROM %s WHERE mid IN (%s)" % (table, ",".join("?" * len(chunk))), chunk):
            fins[f] += 1
    return len(both), unus, (unus / len(both) if both else 0.0), fins


def guard_line(con, rows, what, table="verdicts", refs=None):
    n_both, unus, rate, fins = guard_numbers(con, rows, table)
    deciding = [r for r in rows if not r["nj"]]
    tr_sides = sum(r["trunc_a"] + r["trunc_b"] for r in rows)
    tr_matches = sum(1 for r in rows if r["trunc_a"] or r["trunc_b"])
    so = sum(r["state_over_a"] + r["state_over_b"] for r in rows)
    tasks = {r["task_id"] for r in rows}
    cut = sum(refs[t][1] for t in tasks) if refs else 0
    nj = sum(1 for r in rows if r["nj"])
    line = ("[GUARD] %s %s: matches with both orders %d of %d | unusable %d (%.1f%%) on the DECIDING subset "
            "(denominator %d matches, the %d non-judgeable removed) | finish_reason %s | fingerprint %s | truncated "
            "sides %d of %d (%.1f%%), truncated matches %d of %d, state-over-cap sides %d, per-task reference blocks "
            "cut %d of %d TASKS | non-judgeable %d of %d (%.3f) -> %s"
            % (TEST, what, n_both, len(deciding), unus, 100 * rate, len(deciding), nj, dict(fins),
               dict(fingerprint_counts(con, table)), tr_sides, 2 * len(rows), 100.0 * tr_sides / max(1, 2 * len(rows)),
               tr_matches, len(rows), so, cut, len(tasks), nj, len(rows), nj / max(1, len(rows)),
               "OK (<= 5%)" if rate <= GUARD_RATE else "ABOVE 5%: the next launch REFUSES to post more and the verdict will be REFUSED"))
    print(line, flush=True)
    return n_both, unus, rate, fins


# ----------------------------------------------------------------------------------------------------------------
# statistics
# ----------------------------------------------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def clustered(by_task, B=BOOT, seed=SEED):
    """Question-clustered bootstrap over TASKS of the mean of the pooled per-match values.
    -> (point, lo, hi, sd) with lo/hi the 2.5 / 97.5 percentiles."""
    keys = sorted(by_task)
    vals = [v for k in keys for v in by_task[k]]
    if not vals:
        return float("nan"), float("nan"), float("nan"), float("nan")
    point = sum(vals) / len(vals)
    rng = random.Random(seed)
    draws = []
    for _ in range(B):
        acc, n = 0.0, 0
        for _ in range(len(keys)):
            k = keys[rng.randrange(len(keys))]
            acc += sum(by_task[k])
            n += len(by_task[k])
        draws.append(acc / n if n else float("nan"))
    draws.sort()
    lo = draws[int(0.025 * B)]
    hi = draws[min(B - 1, int(0.975 * B))]
    sd = statistics.pstdev(draws) if len(draws) > 1 else float("nan")
    return point, lo, hi, sd


def agreement(rows, D, convention):
    """-> (k, n, by_task) for the given matches. Convention A: ties / INVALID / pending counted WRONG, full denominator.
    Convention B: committed verdicts only."""
    by_task = defaultdict(list)
    k = n = 0
    for r in rows:
        v = D[r["mid"]]
        committed = (not v["pending"]) and (not v["invalid"]) and v["winner"] not in (None, "TIE", "INVALID")
        if convention == "B" and not committed:
            continue
        ok = 1 if (committed and v["winner"] == r["checker_winner"]) else 0
        by_task[r["task_id"]].append(ok)
        k += ok
        n += 1
    return k, n, by_task


def ladder_position(point, lo, hi):
    out = []
    for name, rung, test, corpus in LADDER:
        if lo > rung:
            rel_ = "REACHED (the interval lies above it)"
        elif hi < rung:
            rel_ = "BELOW (the interval lies under it)"
        else:
            rel_ = "not distinguished from it"
        out.append("      %-24s %.3f  (%s, measured on %s): A %.3f [%.3f, %.3f] is %s" % (name, rung, test, corpus, point, lo, hi, rel_))
    return out


# ----------------------------------------------------------------------------------------------------------------
# the launches
# ----------------------------------------------------------------------------------------------------------------
def load_all():
    base_ids = pool_line()
    c = Corpus(DB, base_ids)
    assert aap.DECIDED_TYPES == DECIDED_TYPES, "the checker-decided rule moved in agent_admission_pilot"
    raws = read_raw_episodes(ROSTER_ALL, c.eval_base)
    tasktext, ds_path, ds_sha = read_task_text(c.eval_base)
    gt, pa_path, pa_sha = read_ground_truth(c.eval_base)
    refs = {t: render_reference(gt[t]) for t in c.eval_base}
    shas = {"dataset": ds_sha, "possible_answer": pa_sha, "dataset_path": ds_path, "possible_answer_path": pa_path}
    rows, H, G = build_schedule(c, raws)
    return c, raws, tasktext, refs, shas, rows, H, G


def dry_run(show_payload=True):
    c, raws, tasktext, refs, shas, rows, H, G = load_all()
    print("corpus %s snapshot %s archive_sha %s | agents %d | %s-stratum EVAL tasks %d | episodes %d (mode=ro&immutable=1)"
          % (c.meta.get("corpus"), c.meta.get("snapshot"), (c.meta.get("archive_sha") or "")[:12], len(c.agents),
             STRATUM, len(c.eval_base), len(c.eps)))
    print("roster: HEADLINE %d agents %s | SELF-PREFERENCE stratum (C3, never in the headline A): %s"
          % (len(HEADLINE_ROSTER), ", ".join(HEADLINE_ROSTER), SELF_PREF_AGENT))
    for line in count_report(H, G)[0]:
        print(line)
    # termination and the C2 class, printed BEFORE any agreement number can exist
    term = Counter()
    for t in c.eval_base:
        for a in ROSTER_ALL:
            e = c.eps.get((t, a))
            if e:
                term[(a, e["bfcl_term_v1"])] += 1
    print("TERMINATION (rule (c), bfcl_term_v1) per agent over its %d base-stratum EVAL episodes:" % len(c.eval_base))
    for a in ROSTER_ALL:
        tot = sum(term[(a, k)] for k in ("TERMINATED", "CAP_HIT", "ERROR"))
        print("  %-40s TERMINATED %3d | CAP_HIT %3d | ERROR %3d  (of %d)%s"
              % (a, term[(a, "TERMINATED")], term[(a, "CAP_HIT")], term[(a, "ERROR")], tot,
                 "   <- self-preference stratum" if a == SELF_PREF_AGENT else ""))
    nj_ep = Counter()
    emptyturn = 0
    n_ep = 0
    for t in c.eval_base:
        for a in HEADLINE_ROSTER:
            e = c.eps.get((t, a))
            if not e or e["bfcl_term_v1"] != "TERMINATED":
                continue
            n_ep += 1
            r = nonjudgeable_reason((raws.get((t, a)) or {}).get("calls"), e["error_type"])
            if r:
                nj_ep[r] += 1
            if e["error_type"] == EMPTY_TURN_TYPE:
                emptyturn += 1
    nj_matches = sum(1 for r in rows if r["stratum"] == "headline" and r["nj"])
    print("C2 NON-JUDGEABLE CLASS (declared in the header before any count): EMPTY %d + DEGENERATE %d = %d of %d "
          "base-stratum EVAL TERMINATED episodes of the 7-agent roster (%.3f); matches removed from the deciding subset "
          "%d of %d (%.3f). BESIDE IT (a different object, the admission's 18.3%%): episodes whose error_type is %s: "
          "%d of %d (%.3f)"
          % (nj_ep["EMPTY"], nj_ep["DEGENERATE"], sum(nj_ep.values()), n_ep, sum(nj_ep.values()) / max(1, n_ep),
             nj_matches, H["n_kept"], nj_matches / max(1, H["n_kept"]), EMPTY_TURN_TYPE, emptyturn, n_ep,
             emptyturn / max(1, n_ep)))
    # the per-task reference of record (the ruling), then the artefact cap
    ref_lens = sorted(len(refs[t][0]) for t in c.eval_base)
    ref_cuts = sum(refs[t][1] for t in c.eval_base)
    print("REFERENCE OF RECORD (ruling BFCL-REF-ORACLE, programme L11001, commit 6ccf2f7): the PER-TASK expected outcome, "
          "rendered ONCE PER TASK from %s (sha256 %s), identical for both sides, attached to the TASK STATEMENT, OUTSIDE "
          "the artefact cap; no per-side verdict, error text, error_type, PASS / FAIL or all_pass anywhere in it "
          "(assert_no_per_side_verdict checks every assembled statement)." % (rel(shas["possible_answer_path"]), shas["possible_answer"][:16]))
    print("  rendered block length over the %d tasks: min %d, median %d, p95 %d, max %d characters (= %d estimated "
          "tokens at the max) | CHECKER_TEXT_CUT at %d characters: %d of %d TASKS (denominator TASKS, not sides)"
          % (len(ref_lens), ref_lens[0], statistics.median(ref_lens), ref_lens[int(0.95 * (len(ref_lens) - 1))],
             ref_lens[-1], ref_lens[-1] // CHARS_PER_TOKEN, REFERENCE_TEXT_CAP, ref_cuts, len(ref_lens)))
    print("  task statement read from %s (sha256 %s), both raw files opened READ-ONLY and pinned in run_meta"
          % (rel(shas["dataset_path"]), shas["dataset"][:16]))
    # the artefact cap
    est = sorted((r["raw_chars_a"] + 0) // CHARS_PER_TOKEN for r in rows) + sorted((r["raw_chars_b"]) // CHARS_PER_TOKEN for r in rows)
    est.sort()
    tr_sides = sum(r["trunc_a"] + r["trunc_b"] for r in rows)
    print("ARTEFACT CAP %d estimated tokens (chars/%d; the manager's reversible choice (i)): per-side estimated tokens "
          "median %d p95 %d max %d | truncated sides %d of %d (%.3f) | truncated matches %d of %d | state-over-cap sides %d"
          % (ARTEFACT_CAP_TOKENS, CHARS_PER_TOKEN, statistics.median(est), est[int(0.95 * (len(est) - 1))], max(est),
             tr_sides, 2 * len(rows), tr_sides / max(1, 2 * len(rows)),
             sum(1 for r in rows if r["trunc_a"] or r["trunc_b"]), len(rows),
             sum(r["state_over_a"] + r["state_over_b"] for r in rows)))
    # payloads
    configure_rr()
    n_pay = 0
    first = None
    for r in rows:
        s, u1, u2 = payloads(r, c, raws, tasktext, refs)
        n_pay += 2
        if first is None:
            first = (r, s, u1, u2)
    body = post_body(first[1], first[2])
    assert_body_copy(body)
    sh = schedule_hash(rows)
    nh = sum(1 for r in rows if r["stratum"] == "headline")
    ng = len(rows) - nh
    print("SCHEDULE fixed at this dry-run (seed %d; hash %s): headline %d matches + self-preference %d = %d; "
          "probe %d matches (preflight, never an arm) + pilot %d matches inside the headline count" % (SEED, sh, nh, ng, len(rows), PROBE_MATCHES, PILOT_MATCHES))
    print("BILL: %d payloads assembled, 0 posted | --probe %d calls, --pilot %d calls (inside the %d), --run %d calls "
          "remaining at most | registration: probe 100 + headline 922 + self-preference 294 = 1,316 expected, ceiling 3,096"
          % (n_pay, 2 * PROBE_MATCHES, 2 * PILOT_MATCHES, 2 * nh, 2 * len(rows)))
    print("protocol: %s" % PROTOCOL)
    print("judge: %s on %s | max_tokens %d | temperature %s | body keys %s | first payload body model=%s max_tokens=%d"
          % (JUDGE_MODEL, PROVIDER, MAXTOK, "OMITTED (never sent)", tuple(body.keys()), body["model"], body["max_tokens"]))
    print("reference form: %s | the two prompt strings are pinned in run_meta and are THE REVIEWER'S TO APPROVE "
          "(amendment item (2)); neither names the checker's verdict, promises the reference is correct or tells the "
          "judge to defer to it" % REFERENCE_FORM)
    print("  SYSTEM_BFCL: %s" % SYSTEM_BFCL)
    print("  RUBRIC_BFCL: %s" % RUBRIC_BFCL)
    print("  recipe note: %s" % V2_INHERITED_NOTE)
    print("cache: %s%s (the dry-run creates none) | outcome %s (write-once) | pilot %s | probe %s"
          % (rel(CACHE), " (EXISTS)" if os.path.exists(CACHE) else " (new)", rel(OUT), rel(OUT_PILOT), rel(OUT_PROBE)))
    ok, s = gate_state()
    print("READY gate (not enforced by --dry-run): %s -> %s" % (s, "OPEN" if ok else "CLOSED (nothing may be posted)"))
    bad = count_report(H, G)[1]
    print("count check: %s" % ("OK (every recomputed denominator within %.0f%% of the registered one)" % (100 * COUNT_DELTA_TOL)
                               if not bad else "REFUSES every posting launch: %s" % bad))
    print("script sha256[:16] LF %s | raw-bytes %s" % (SCRIPT_SHA, script_sha_raw()))
    night_line(0, "--dry-run (0 calls)")
    if show_payload:
        r, system, u1, _ = first
        print("\n(the per-task reference block appears at the END of the task statement, before the two traces, and is "
              "byte-identical in the reversed order: the two orders differ only in the trace order)")
        print("\n===== FIRST PAYLOAD: %s, %s (Model A) vs %s (Model B), checker winner %s, order fwd ====="
              % (r["task_id"], r["agent_a"], r["agent_b"], r["checker_winner"]))
        print("----- system -----")
        print(system)
        print("----- user -----")
        print(u1)
        print("===== END FIRST PAYLOAD =====")
    print("dry run OK: 0 calls posted, no cache created")
    print(dbguard_line())


def post(con, jobs, workers, table):
    """Post (mid, arm, system, user) jobs; fail-closed on the deployment fingerprint; one row per (match, order)."""
    lock = threading.Lock()
    ok = err = 0
    fins = Counter()
    halt = threading.Event()
    mismatch = []

    def one(job):
        mid, arm, system, user = job
        if halt.is_set():
            raise FingerprintMismatch("match %d %s: not posted, the run is stopping on a fingerprint mismatch" % (mid, arm))
        raw, provider, ctok, _lat, finish, _msg = rr.call_judge_full(system, user)
        try:
            check_fingerprint(mid, arm, provider, finish)
        except FingerprintMismatch as e:
            mismatch.append(str(e))
            halt.set()
            raise
        clean = rr.strip_think(raw or "")
        vote, conf = rj.parse_judge(clean)
        vote = unusable_vote(vote, finish)
        return (mid, arm, vote, conf, int(vote == "INVALID"), clean, time.time(), finish, ctok, provider, MAXTOK)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except FingerprintMismatch as e:
                halt.set()
                ex.shutdown(wait=False, cancel_futures=True)
                raise SystemExit("[FINGERPRINT] %s\n  the run STOPS: nothing is cached for that call and the remaining "
                                 "calls are not posted (cached so far: ok %d, errors %d). The deployed judge of record "
                                 "is %s; a different deployment is a different judge and never enters this cache."
                                 % (mismatch[0] if mismatch else e, ok, err, JUDGE_MODEL))
            except Exception as e:                            # noqa: BLE001
                err += 1
                print("  ERROR %s: %s" % (futs[f][:2], str(e)[:140]), flush=True)
                continue
            with lock:
                con.execute("INSERT OR REPLACE INTO %s VALUES (%s)" % (table, ",".join("?" * 11)), row)
                con.commit()
            ok += 1
            fins[row[7]] += 1
            if i % 25 == 0 or i == len(jobs):
                print("  %d/%d (ok %d, err %d) | finish_reason %s" % (i, len(jobs), ok, err, dict(fins)), flush=True)
    return ok, err, fins


def cli_launch_shapes(pilot_n=12, workers=8):
    """The argument shapes the CLI actually passes to launch(), READ FROM THIS FILE'S __main__ DISPATCH (never
    hard-coded): every launch(...) call in the dispatch block is parsed and its arguments are evaluated against a
    namespace holding the values argparse would carry (--probe / --pilot <n> / --run). A future change to a call shape
    - e.g. passing a.pilot where None went - changes what --selftest drives, so the selftest breaks instead of the run.
    This exists because the run branch passes n=None and an eager "--pilot %d" % n crashed launch() before go_gate."""
    import argparse as _argparse
    import ast as _ast
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    tree = _ast.parse(src)
    mains = [nd for nd in tree.body if isinstance(nd, _ast.If) and "__main__" in _ast.dump(nd.test)]
    assert len(mains) == 1, "the __main__ dispatch block could not be located"
    ns = _argparse.Namespace(selftest=False, dry_run=False, probe=True, pilot=pilot_n, run=True, analyze=False,
                             workers=workers, draws=BOOT, no_payload=False, override_guard=False)
    out = []
    for nd in _ast.walk(mains[0]):
        if isinstance(nd, _ast.Call) and isinstance(nd.func, _ast.Name) and nd.func.id == "launch":
            out.append(tuple(eval(compile(_ast.Expression(arg), "<cli-dispatch>", "eval"), globals(), {"a": ns})
                             for arg in nd.args))
    return out


def launch(mode, n, workers):
    """mode in {'probe', 'pilot', 'run'}. Gated, counted against the night's ceiling, guarded."""
    what = {"probe": "--probe (item-19 preflight)", "run": "--run"}.get(mode) or ("--pilot %d" % n)
    go_gate(what)
    c, raws, tasktext, refs, shas, rows, H, G = load_all()
    bad = count_report(H, G)[1]
    if bad:
        raise SystemExit("[COUNTS] REFUSED (0 calls): the recomputed denominators differ from the registration's by more "
                         "than %.0f%%: %s. The registrar amends the registration before anything is posted."
                         % (100 * COUNT_DELTA_TOL, bad))
    configure_rr()
    assert_body_copy(post_body("s", "u"))
    rr.load_env()
    sh = schedule_hash(rows)
    headline = [r for r in rows if r["stratum"] == "headline"]
    target = headline[:PROBE_MATCHES] if mode == "probe" else (headline[:n] if mode == "pilot" else rows)
    table = "probe" if mode == "probe" else "verdicts"
    con = open_cache()
    pin_meta(con, sh, len(rows), shas)
    write_schedule(con, rows)
    have = {(m, a) for m, a in con.execute("SELECT mid, arm FROM %s" % table)}
    todo = [(r, a) for r in target for a in ("fwd", "rev") if (r["mid"], a) not in have]
    night_line(len(todo), what)
    print("%s %s: judge %s | max_tokens %d | temperature OMITTED | reference %s | schedule %d matches (hash %s) | "
          "targeted %d | to post %d calls | workers %d | cache %s"
          % (TEST, what, JUDGE_MODEL, MAXTOK, REFERENCE_FORM, len(rows), sh, len(target), len(todo), workers, rel(CACHE)), flush=True)
    if mode != "probe":
        n_both, unus, rate, _ = guard_numbers(con, rows)
        if n_both and rate > GUARD_RATE and not OVERRIDE_GUARD:
            raise SystemExit("[GUARD] REFUSED: %d of %d cached matches (%.1f%%) are unusable on the deciding subset "
                             "(> 5%%); nothing more is posted (--override-guard posts anyway and is recorded in run_meta)."
                             % (unus, n_both, 100 * rate))
    jobs = []
    for r, arm in todo:
        system, u1, u2 = payloads(r, c, raws, tasktext, refs)
        jobs.append((r["mid"], arm, system, u1 if arm == "fwd" else u2))
    ok, err, fins = post(con, jobs, workers, table) if jobs else (0, 0, Counter())
    night_ledger_append(ok, what)
    guard_line(con, target, what, table, refs)
    if mode == "probe":
        probe_report(con, target)
    print("done: ok %d, errors %d. --analyze for the readout (refuses a partial cache)." % (ok, err), flush=True)
    print(dbguard_line())


def probe_report(con, rows):
    """Item 19 (FRAMEWORK L372): the per-model max_tokens probe on the TRACE-SHAPED prompt. A PREFLIGHT, never an arm:
    these rows live in the `probe` table and are never read by --analyze's A."""
    mids = [r["mid"] for r in rows]
    got = [(f, t) for m in mids for f, t in con.execute("SELECT COALESCE(finish,'(none)'), COALESCE(ctokens,-1) FROM probe WHERE mid=?", (m,))]
    fins = Counter(f for f, _ in got)
    toks = sorted(t for _, t in got if t >= 0)
    n = len(got)
    lengths = fins.get("length", 0)
    L = ["=== %s: item-19 max_tokens PROBE on the TRACE-SHAPED prompt (PREFLIGHT, never an arm; rows in table `probe`, "
         "never read by --analyze's A) ===" % TEST,
         "  registration %s | judge %s | cap %d | temperature OMITTED | %d calls on %d matches" % (REGISTRATION, JUDGE_MODEL, MAXTOK, n, len(rows)),
         "  finish_reason %s | completion tokens: median %s p95 %s max %s of the %d cap | at-cap (finish_reason length) %d of %d (%.3f)"
         % (dict(fins), statistics.median(toks) if toks else "n/a", (toks[int(0.95 * (len(toks) - 1))] if toks else "n/a"),
            (max(toks) if toks else "n/a"), MAXTOK, lengths, n, lengths / max(1, n)),
         "  item-19 criterion (no cell above 5%% length): %s" % ("MET" if lengths <= 0.05 * max(1, n) else "NOT MET: the cap is too small for this prompt shape; the run is not launched on it"),
         "  reference of record: the PER-TASK expected outcome (ruling BFCL-REF-ORACLE); no per-side verdict is in any "
         "prompt this probe posted."]
    txt = "\n".join(L)
    print(txt)
    if os.path.exists(OUT_PROBE):
        print("  (%s exists; write-once, not overwritten)" % rel(OUT_PROBE))
    else:
        open(OUT_PROBE, "w", encoding="utf-8").write(txt + "\n")
        print("  written: %s" % rel(OUT_PROBE))


# ----------------------------------------------------------------------------------------------------------------
# --analyze
# ----------------------------------------------------------------------------------------------------------------
def analyze(boot=BOOT):
    c, raws, tasktext, refs, shas, rows, H, G = load_all()
    if not os.path.exists(CACHE):
        raise SystemExit("no cache at %s: nothing judged, nothing written" % rel(CACHE))
    con = open_cache_ro()
    night_line(0, "--analyze (0 calls)")
    meta = dict(con.execute("SELECT key, value FROM run_meta"))
    sh = schedule_hash(rows)
    headline = [r for r in rows if r["stratum"] == "headline"]
    selfpref = [r for r in rows if r["stratum"] == "selfpref"]
    D = dual(con, rows)
    problems = []
    if meta.get("schedule_hash") != sh:
        problems.append("the cached schedule hash %s is not the recomputed %s" % (meta.get("schedule_hash"), sh))
    pending = sum(1 for r in rows if D[r["mid"]]["pending"])
    if pending:
        problems.append("PARTIAL: %d of %d matches are not judged in both orders" % (pending, len(rows)))
    n_both, unus, rate, fins = guard_numbers(con, rows)
    if rate > GUARD_RATE:
        problems.append("VERDICT REFUSED: %.1f%% unusable on the deciding subset (> 5%%)" % (100 * rate))

    L = ["=== %s: the deployed recipe against the BFCL CHECKER_OUTPUT on the base stratum ===" % TEST,
         "  registration %s" % REGISTRATION,
         "  pool %s (%d EVAL %s tasks) | corpus %s mode=ro&immutable=1 | judge %s | cap %s | temperature %s | reference %s"
         % (BFCL_POOL_ID, len(c.eval_base), STRATUM, os.path.basename(DB), meta.get("judge_model"), meta.get("max_tokens"),
            meta.get("temperature"), meta.get("reference")),
         "  protocol: %s" % meta.get("protocol"),
         "  cache %s (mode=ro) | producing script LF sha %s | this script %s%s | started %s | resumed %s"
         % (rel(CACHE), meta.get("script_sha256_16_lf"), SCRIPT_SHA, "" if meta.get("script_sha256_16_lf") == SCRIPT_SHA else " (DIFFERS)",
            meta.get("started"), meta.get("resumed", "-")),
         "  deployment fingerprint over the posted calls (expected %s): %s" % (EXPECTED_FINGERPRINT, dict(fingerprint_counts(con))),
         "  rosters: HEADLINE %s | SELF-PREFERENCE (C3, never in the headline) %s" % (", ".join(HEADLINE_ROSTER), SELF_PREF_AGENT),
         "  reference of record (ruling BFCL-REF-ORACLE, programme L11001, commit 6ccf2f7): the PER-TASK EXPECTED "
         "OUTCOME, rendered once per task from %s (sha256 %s), identical for both sides, attached to the task "
         "statement, OUTSIDE the artefact cap; no per-side verdict, error text, error_type, PASS / FAIL or all_pass "
         "is in any prompt this cache was built from (assert_no_per_side_verdict checked every assembled statement). "
         "A is therefore a BLIND verification rate, which is what makes the ladder positioning legitimate."
         % (rel(shas["possible_answer_path"]), shas["possible_answer"][:16]),
         "  task statement from %s (sha256 %s); pinned in run_meta as %s / %s" % (rel(shas["dataset_path"]), shas["dataset"][:16],
                                                                                  (meta.get("dataset_sha256") or "")[:16], (meta.get("possible_answer_sha256") or "")[:16]),
         "  prompt strings pinned in run_meta (amendment item (2)) | SYSTEM_BFCL: %s | RUBRIC_BFCL: %s" % (meta.get("system_bfcl"), meta.get("rubric_bfcl")),
         "  recipe note: %s" % V2_INHERITED_NOTE]
    L += ["  " + s for s in count_report(H, G)[0]]
    L.append("  cache rows: %d of %d calls | matches with both orders %d of %d | unusable %d (%.1f%%) | finish_reason %s"
             % (con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0], 2 * len(rows), n_both, len(rows), unus, 100 * rate, dict(fins)))
    for p in problems:
        L.append("  " + p)

    # ---- C2 first: the class is declared, counted and printed BEFORE A is read
    nj_h = [r for r in headline if r["nj"]]
    deciding = [r for r in headline if not r["nj"]]
    nj_ep = Counter()
    n_ep = emptyturn = 0
    for t in c.eval_base:
        for a in HEADLINE_ROSTER:
            e = c.eps.get((t, a))
            if not e or e["bfcl_term_v1"] != "TERMINATED":
                continue
            n_ep += 1
            r_ = nonjudgeable_reason((raws.get((t, a)) or {}).get("calls"), e["error_type"])
            if r_:
                nj_ep[r_] += 1
            if e["error_type"] == EMPTY_TURN_TYPE:
                emptyturn += 1
    L += ["", "=== C2 THE EMPTY / DEGENERATE CLASS, NON-JUDGEABLE BY THE REGISTRATION, COUNTED BEFORE A ===",
          "  rule (fixed in this script's header before any call): EMPTY = zero non-blank decoded calls; DEGENERATE = "
          "error_type %s AND a blank decoded-call text; a MATCH is non-judgeable iff EITHER side is." % EMPTY_TURN_TYPE,
          "  episodes: EMPTY %d + DEGENERATE %d = %d of %d base-stratum EVAL TERMINATED episodes of the 7-agent roster = %.4f"
          % (nj_ep["EMPTY"], nj_ep["DEGENERATE"], sum(nj_ep.values()), n_ep, sum(nj_ep.values()) / max(1, n_ep)),
          "  matches: %d of the %d checker-disagreeing headline matches (%.4f) removed -> DECIDING SUBSET %d matches on %d tasks"
          % (len(nj_h), len(headline), len(nj_h) / max(1, len(headline)), len(deciding), len({r["task_id"] for r in deciding})),
          "  beside it (a DIFFERENT object: the admission run's 18.3%% error_type share): episodes with error_type %s: %d of %d = %.4f"
          % (EMPTY_TURN_TYPE, emptyturn, n_ep, emptyturn / max(1, n_ep)),
          "  C2: %s (declared before any call, counted and printed with its denominator BEFORE A; A is reported BOTH "
          "ways below, the deciding-subset reading being the reading of record for C1; partition check %d + %d = %d)"
          % ("HELD" if len(deciding) + len(nj_h) == len(headline) else "FAILED", len(deciding), len(nj_h), len(headline))]

    # ---- C1
    L += ["", "=== C1 A, THE HEADLINE AGREEMENT WITH THE CHECKER, AND ITS LADDER POSITION ==="]
    res = {}
    for subset_name, subset in (("deciding subset (READING OF RECORD)", deciding), ("all checker-disagreeing headline matches", headline)):
        for conv in ("A", "B"):
            k, n, by_task = agreement(subset, D, conv)
            point, lo, hi, sd = clustered(by_task, boot)
            wlo, whi = wilson(k, n)
            res[(subset_name, conv)] = dict(k=k, n=n, point=(k / n if n else float("nan")), lo=lo, hi=hi, sd=sd,
                                            nlo=(k / n - 1.96 * sd) if n else float("nan"), nhi=(k / n + 1.96 * sd) if n else float("nan"),
                                            q=len(by_task), wlo=wlo, whi=whi)
            r_ = res[(subset_name, conv)]
            L.append("  [convention %s] %-42s A = %d / %d = %.4f on %d tasks | Wilson [%.4f, %.4f] | question-clustered "
                     "bootstrap (B=%d, seed %d) SE %.4f -> percentile [%.4f, %.4f], normal [%.4f, %.4f]"
                     % (conv, subset_name, k, n, r_["point"], r_["q"], wlo, whi, boot, SEED, sd, lo, hi, r_["nlo"], r_["nhi"]))
    L.append("  convention A = ties, INVALID and non-terminated counted WRONG on the full denominator; convention B = "
             "committed verdicts only. The SE OF RECORD for C1 is the question-clustered (DEFF-inflated) SE; the "
             "registration's expectation at 461 matches on 57 tasks is ~%.3f." % SE_OF_RECORD)
    rec = res[("deciding subset (READING OF RECORD)", "A")]
    L.append("  LADDER POSITION of A (deciding subset, convention A) against the three rungs; CROSS-CORPORA CAVEAT: %s." % CROSS_CORPORA_CAVEAT)
    L += ladder_position(rec["point"], rec["nlo"], rec["nhi"])
    L.append("  INTERVAL OF RECORD for C1 (amendment item (5)(d)): the point +- 1.96 x the clustered SE = [%.4f, %.4f]; "
             "the PERCENTILE interval [%.4f, %.4f] is printed beside it (B = %d, cluster unit = the %d TASKS). If the "
             "two disagree about the %.2f bar, C1 is UNDETERMINED."
             % (rec["nlo"], rec["nhi"], rec["lo"], rec["hi"], boot, rec["q"], BAR))
    normal_says = "above" if rec["nlo"] > BAR else ("below" if rec["nhi"] < BAR else "straddles")
    pct_says = "above" if rec["lo"] > BAR else ("below" if rec["hi"] < BAR else "straddles")
    if rec["n"] < MIN_DECIDING:
        c1 = "UNDETERMINED (the deciding subset is %d matches, below the registered floor of %d)" % (rec["n"], MIN_DECIDING)
    elif normal_says != pct_says:
        c1 = ("UNDETERMINED (amendment item (5)(d)): the interval of record %s the %.2f bar while the percentile "
              "interval %s it" % (normal_says, BAR, pct_says))
    elif rec["nlo"] > BAR:
        c1 = "HELD (the lower end of the DEFF-inflated interval of record, %.4f, is above %.2f, and the percentile interval agrees)" % (rec["nlo"], BAR)
    elif rec["point"] <= BAR:
        c1 = "FAILED - THE FALSIFIER FIRES (the point %.4f is at or below %.2f)" % (rec["point"], BAR)
    else:
        c1 = "UNDETERMINED (the interval of record [%.4f, %.4f] straddles %.2f)" % (rec["nlo"], rec["nhi"], BAR)
    L.append("  C1: %s" % c1)
    if c1.startswith("FAILED"):
        L.append("  FALSIFIER READING (registration): on a real agentic artefact with a real outcome checker the deployed "
                 "recipe verifies no better than a NO-REFERENCE judge does on MMLU-Pro (PAIR-NOREF 0.738); the \"for "
                 "Agents\" bridge may then be written only as motivation, never as a measured claim, ON THIS CORPUS. It "
                 "overturns no BFCL number, no board, no profile, no tier and no MMLU-Pro result.")

    # ---- C3
    L += ["", "=== C3 THE SELF-PREFERENCE STRATUM, BESIDE AND NEVER IN THE HEADLINE ==="]
    sp_deciding = [r for r in selfpref if not r["nj"]]
    kg, ng, bt_g = agreement(sp_deciding, D, "A")
    pg, glo, ghi, gsd = clustered(bt_g, boot)
    L.append("  A_grok = %d / %d = %.4f (convention A, deciding subset of the stratum; %d matches before the C2 removal) "
             "| clustered SE %.4f -> [%.4f, %.4f]: a DIRECTION, not a number"
             % (kg, ng, (kg / ng if ng else float("nan")), len(selfpref), gsd, pg - 1.96 * gsd, pg + 1.96 * gsd))
    shared = {r["task_id"] for r in sp_deciding} & {r["task_id"] for r in deciding}
    d_by_task = defaultdict(list)
    for r in sp_deciding:
        if r["task_id"] in shared:
            v = D[r["mid"]]
            d_by_task[r["task_id"]].append(1 if (not v["pending"] and not v["invalid"] and v["winner"] == r["checker_winner"]) else 0)
    h_by_task = defaultdict(list)
    for r in deciding:
        if r["task_id"] in shared:
            v = D[r["mid"]]
            h_by_task[r["task_id"]].append(1 if (not v["pending"] and not v["invalid"] and v["winner"] == r["checker_winner"]) else 0)
    rng = random.Random(SEED)
    keys = sorted(shared)
    deltas = []
    for _ in range(boot):
        num1 = den1 = num2 = den2 = 0
        for _ in range(len(keys)):
            k_ = keys[rng.randrange(len(keys))]
            num1 += sum(d_by_task[k_]); den1 += len(d_by_task[k_])
            num2 += sum(h_by_task[k_]); den2 += len(h_by_task[k_])
        if den1 and den2:
            deltas.append(num1 / den1 - num2 / den2)
    deltas.sort()
    d_point = ((sum(v for vs in d_by_task.values() for v in vs) / max(1, sum(len(v) for v in d_by_task.values())))
               - (sum(v for vs in h_by_task.values() for v in vs) / max(1, sum(len(v) for v in h_by_task.values())))) if shared else float("nan")
    d_lo = deltas[int(0.025 * len(deltas))] if deltas else float("nan")
    d_hi = deltas[min(len(deltas) - 1, int(0.975 * len(deltas)))] if deltas else float("nan")
    L.append("  A_grok - A_headline on the %d tasks that appear in both strata: %+.4f, paired-by-task bootstrap [%+.4f, %+.4f]"
             % (len(shared), d_point, d_lo, d_hi))
    winshare = pass_share = 0.0
    nsp = len([r for r in sp_deciding if not D[r["mid"]]["pending"] and not D[r["mid"]]["invalid"]])
    if nsp:
        winshare = sum(1 for r in sp_deciding if D[r["mid"]]["winner"] == SELF_PREF_AGENT) / nsp
    if sp_deciding:
        pass_share = sum(1 for r in sp_deciding if r["checker_winner"] == SELF_PREF_AGENT) / len(sp_deciding)
    L.append("  the %s side: judge win-share %.4f (of %d committed matches) beside its checker pass-share %.4f (of %d matches)"
             % (SELF_PREF_AGENT, winshare, nsp, pass_share, len(sp_deciding)))
    head_has_grok = any(SELF_PREF_AGENT in (r["agent_a"], r["agent_b"]) for r in headline)
    L.append("  C3: %s (the stratum is computed, printed and kept out of every headline figure; grok-FC matches inside "
             "the headline set: %d)" % ("FAILED" if head_has_grok else "HELD", sum(1 for r in headline if SELF_PREF_AGENT in (r["agent_a"], r["agent_b"]))))

    # ---- C4
    tr_sides = sum(r["trunc_a"] + r["trunc_b"] for r in headline)
    tr_matches = sum(1 for r in headline if r["trunc_a"] or r["trunc_b"])
    ties = sum(1 for r in deciding if D[r["mid"]]["winner"] == "TIE")
    judged = sum(1 for r in deciding if not D[r["mid"]]["pending"] and not D[r["mid"]]["invalid"])
    n_calls = con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
    n_unusable_rows = con.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=1 OR finish IN ('length','content_filter')").fetchone()[0]
    ref_cuts = sum(refs[t][1] for t in c.eval_base)
    ref_lens = sorted(len(refs[t][0]) for t in c.eval_base)
    L += ["", "=== C4 INSTRUMENT COUNTS (printed, no bar) ===",
          "  truncated sides %d of %d headline sides (%.4f); truncated matches %d of %d (%.4f); state-over-cap sides %d"
          % (tr_sides, 2 * len(headline), tr_sides / max(1, 2 * len(headline)), tr_matches,
             len(headline), tr_matches / max(1, len(headline)),
             sum(r["state_over_a"] + r["state_over_b"] for r in headline)),
          "  per-task reference block: median %d, max %d characters; CHECKER_TEXT_CUT %d of %d TASKS (denominator TASKS, "
          "not sides: the block is per task, so the cut is identical in both orders)"
          % (statistics.median(ref_lens), ref_lens[-1], ref_cuts, len(ref_lens))]
    for a in ROSTER_ALL:
        cnt = Counter(c.eps[(t, a)]["bfcl_term_v1"] for t in c.eval_base if (t, a) in c.eps)
        L.append("  %-40s NON_TERMINATED excluded by rule (c): CAP_HIT %3d + ERROR %3d of %3d base-stratum EVAL episodes "
                 "(TERMINATED %3d)%s" % (a, cnt["CAP_HIT"], cnt["ERROR"], sum(cnt.values()), cnt["TERMINATED"],
                                         "   [self-preference stratum]" if a == SELF_PREF_AGENT else ""))
    L += ["  unusable rows (content_filter + length + unparsed) %d of %d posted calls (%.4f)" % (n_unusable_rows, n_calls, n_unusable_rows / max(1, n_calls)),
          "  order-flip TIE share %d of %d judged matches on the deciding subset (%.4f)" % (ties, judged, ties / max(1, judged)),
          "  " + (_NIGHT_LINE or "[NIGHT] (not computed in this launch)")]

    # ---- predictions
    recB = res[("deciding subset (READING OF RECORD)", "B")]
    tie_share = ties / max(1, judged)
    trunc_share = tr_sides / max(1, 2 * len(headline))
    nj_share = sum(nj_ep.values()) / max(1, n_ep)
    unus_share = n_unusable_rows / max(1, n_calls)

    def band(x, lo, hi):
        return "HELD" if (x == x and lo <= x <= hi) else "FAILED"

    L += ["", "=== predictions (registered before any code; scored explicitly) ===",
          "  P1 A deciding subset, convention A, in [0.78, 0.90] (point 0.85): %.4f -> %s" % (rec["point"], band(rec["point"], 0.78, 0.90)),
          "  P2 A under convention B in [0.85, 0.95] (4-8pp above convention A): %.4f (delta %+.4f) -> %s"
          % (recB["point"], recB["point"] - rec["point"], band(recB["point"], 0.85, 0.95)),
          "  P3 order-flip TIE share in [0.08, 0.25] of the judged matches: %.4f -> %s" % (tie_share, band(tie_share, 0.08, 0.25)),
          "  P4 truncated-side share in [0.04, 0.12] of the headline sides: %.4f -> %s" % (trunc_share, band(trunc_share, 0.04, 0.12)),
          "  P5 the C2 empty / degenerate class in [0.10, 0.25] of the roster's base-stratum EVAL TERMINATED episodes: "
          "%.4f -> %s   (the admission's 18.3%% is the error_type share %.4f, printed beside: a different object)"
          % (nj_share, band(nj_share, 0.10, 0.25), emptyturn / max(1, n_ep)),
          "  P6 A_grok - A_headline in [-0.05, +0.10], scored as a BAND with 'undecidable at this support' allowed: "
          "%+.4f [%+.4f, %+.4f] -> %s" % (d_point, d_lo, d_hi, "%s%s" % (band(d_point, -0.05, 0.10), "" if (d_hi - d_lo) < 0.15 else " (UNDECIDABLE at this support: the interval is wider than the band)")),
          "  P7 unusable rows <= 1%% of the posted calls: %.4f -> %s" % (unus_share, "HELD" if unus_share <= 0.01 else "FAILED"),
          "  P8 A's DEFF-inflated interval EXCLUDES 0.958: [%.4f, %.4f] -> %s" % (rec["nlo"], rec["nhi"], "HELD" if not (rec["nlo"] <= 0.958 <= rec["nhi"]) else "FAILED")]
    L += ["", "=== what this outcome does and does not license ===",
          "  it licenses ONE measured sentence for the \"for Agents\" bridge, with its interval and its ladder position, "
          "and a CALIBRATION / CANARY object on an agent corpus.",
          "  it licenses NO profile cell (57 EVAL tasks against the 120-question support rule, FRAMEWORK L117), NO agent "
          "ranking, NO per-trajectory claim and NO process statement, now or later, without a new registration.",
          "  the REJECTED per-side form (the per-episode checker verdict in the block) is forbidden in this test, its "
          "cache, this outcome, the ledger, the thesis and the blog; a number measured under it is never placed beside "
          "0.958 or on the ladder (ruling BFCL-REF-ORACLE)."]
    if problems:
        L.append("  NO VERDICT (refused: %s)" % "; ".join(problems))
    txt = "\n".join(L)
    print(txt)
    if problems:
        open(OUT_PILOT, "w", encoding="utf-8").write(txt + "\n")
        print("PARTIAL / PILOT readout (%s): written to %s; the outcome file of record is untouched" % ("; ".join(problems), rel(OUT_PILOT)))
    elif os.path.exists(OUT):
        print("COMPLETE, but %s exists: the outcome of record is WRITE-ONCE and is not overwritten." % rel(OUT))
    else:
        open(OUT, "w", encoding="utf-8").write(txt + "\n")
        print("written: %s" % rel(OUT))
    print(dbguard_line())


# ----------------------------------------------------------------------------------------------------------------
# --selftest (synthetic; opens no file of record, no network, 0 calls)
# ----------------------------------------------------------------------------------------------------------------
def selftest():
    # 1. the artefact cap: under the cap, over the cap (middle dropped, head and tail kept, final state whole),
    #    and the state-over-cap class
    calls = ["c%03d %s" % (i, "x" * 90) for i in range(200)]
    state = "S" * 500
    text, tr, kept, total, so, before, after = cap_artefact(calls, state)
    assert tr == 1 and so == 0 and total == 200 and 0 < kept < 200, (tr, kept, total)
    assert text.endswith(state) and state in text, "the final state must always be retained in full"
    assert text.startswith("c000") and ("c199" in text), "head and tail calls must survive the middle drop"
    assert after <= ARTEFACT_CAP_CHARS + len(TRUNC_MARKER % (0, 0, 0)) + 10, after
    t2, tr2, kept2, total2, so2, _, _ = cap_artefact(calls, "S" * (ARTEFACT_CAP_CHARS + 100))
    assert (tr2, kept2, so2) == (1, 0, 1) and t2.endswith("S" * (ARTEFACT_CAP_CHARS + 100)), (tr2, kept2, so2)
    small = ["a", "b"]
    t3, tr3, kept3, total3, so3, b3, a3 = cap_artefact(small, "state")
    assert (tr3, kept3, total3, so3) == (0, 2, 2, 0) and t3 == "a\nb\nstate", t3
    # the cap is symmetric: the same rule and cap on both sides
    assert cap_artefact(calls, state)[0] == cap_artefact(list(calls), state)[0]
    # 2. the C2 rule
    assert nonjudgeable_reason([], None) == "EMPTY"
    assert nonjudgeable_reason(None, None) == "EMPTY"
    assert nonjudgeable_reason(["[]", "  ", '""'], None) == "EMPTY"
    assert nonjudgeable_reason(["[]"], EMPTY_TURN_TYPE) == "EMPTY"
    assert nonjudgeable_reason(['["f(x)"]'], EMPTY_TURN_TYPE) is None
    assert nonjudgeable_reason(['["f(x)"]'], None) is None
    # 3. parts() against the admission pilot's artefact_text
    entry = {"id": "multi_turn_base_4", "inference_log": [
        {"step_0": [{"role": "handler_log", "model_response_decoded": ["f(a=1)"]}],
         "step_1": [{"role": "handler_log", "model_response_decoded": ["g(b=2)"]}, {"role": "tool", "content": "ok"}]},
        [{"GorillaFileSystem": {"cwd": "/"}}]]}
    cs, st = parts(entry)
    assert cs == ['["f(a=1)"]', '["g(b=2)"]'] and st.startswith("["), (cs, st)
    assert "\n".join(cs) + "\n" + st == aap.artefact_text(entry)
    # 4. the filter, the checker winner and the schedule, on a synthetic corpus
    class C:
        eval_base = ["multi_turn_base_%d" % i for i in range(4)]
        eps = {}

        def terminated(self, e):
            return e["bfcl_term_v1"] == "TERMINATED"

        def decided(self, e):
            return e["passed"] == 1 or e["error_type"] in DECIDED_TYPES
    c = C()
    roster = ("a1", "a2", "a3")
    for t in c.eval_base:
        for i, a in enumerate(roster):
            passed = 1 if (int(t[-1]) + i) % 2 == 0 else 0
            term = "CAP_HIT" if (t == "multi_turn_base_3" and a == "a3") else "TERMINATED"
            et = None if passed else ("multi_turn:instance_state_mismatch" if a != "a2" else "multi_turn:force_terminated")
            c.eps[(t, a)] = {"task_id": t, "agent": a, "passed": passed, "checker_output": "PASS" if passed else "%s: x" % et,
                             "error_type": et, "bfcl_term_v1": term, "termination_class": "terminated", "checker_sha": "x"}
    S = stratum_matches(c, roster)
    assert S["both_present"] == 12 and S["terminated"] == 10, (S["both_present"], S["terminated"])
    assert all(c.eps[(t, a)]["passed"] != c.eps[(t, b)]["passed"] for t, a, b, _, _ in S["kept"])
    assert all(c.decided(ea) and c.decided(eb) for _, _, _, ea, eb in S["kept"])
    assert S["n_kept"] <= S["pass_differs"], (S["n_kept"], S["pass_differs"])   # the both-decided clause only removes
    # 5. the conventions, the clustered bootstrap and the ladder reading, on planted verdicts
    rows = [dict(mid=i, task_id="t%d" % (i % 5), agent_a="a1", agent_b="a2", checker_winner="a1", nj="", stratum="headline",
                 trunc_a=0, trunc_b=0, state_over_a=0, state_over_b=0) for i in range(100)]
    D = {}
    for i, r in enumerate(rows):
        w = "a1" if i % 10 else ("TIE" if i % 20 == 0 else "a2")
        D[r["mid"]] = dict(winner=w, flip=0, invalid=int(w == "INVALID"), pending=0, f1="stop", f2="stop")
    kA, nA, btA = agreement(rows, D, "A")
    kB, nB, btB = agreement(rows, D, "B")
    assert nA == 100 and nB == 95 and kA == kB == 90, (kA, nA, kB, nB)
    pt, lo, hi, sd = clustered(btA, 400)
    assert abs(pt - 0.90) < 1e-9 and 0 < sd < 0.2 and lo <= pt <= hi, (pt, lo, hi, sd)
    lines = ladder_position(0.90, 0.87, 0.93)
    assert "REACHED" in lines[0] and "REACHED" in lines[1] and "BELOW" in lines[2], lines
    lines = ladder_position(0.86, 0.83, 0.89)
    assert "not distinguished from it" in lines[1], lines
    # 6. wilson
    lo_, hi_ = wilson(90, 100)
    assert 0.82 < lo_ < 0.86 and 0.94 < hi_ < 0.96, (lo_, hi_)
    # 7. unusable votes
    assert unusable_vote("Model A", "length") == "INVALID" and unusable_vote("Model A", "content_filter") == "INVALID"
    assert unusable_vote("TIE", "stop") == "TIE"
    # 8. the count check
    H = dict(both_present=1197, terminated=1113, pass_differs=470, kept=[], n_kept=461, rows_terminated=[])
    G = dict(both_present=399, terminated=385, pass_differs=150, kept=[], n_kept=147, rows_terminated=[])
    assert count_report(H, G)[1] is None
    G_bad = dict(G, n_kept=100)
    assert count_report(H, G_bad)[1] is not None
    # 9. the fingerprint rule (canary_baseline's, fail-closed)
    check_fingerprint(1, "fwd", EXPECTED_FINGERPRINT, "stop")
    check_fingerprint(1, "fwd", REFUSAL_FINGERPRINT, "content_filter")
    for prov, fin in (("azure:grok-4-1-fast-reasoning", "stop"), (REFUSAL_FINGERPRINT, "stop"), ("", None)):
        try:
            check_fingerprint(1, "fwd", prov, fin)
            raise AssertionError("the fingerprint guard accepted %r / %r" % (prov, fin))
        except FingerprintMismatch:
            pass
    # 10. the body copy and the omitted temperature
    configure_rr()
    b = post_body("s", "u")
    assert_body_copy(b)
    assert "temperature" not in b and tuple(b) == ("model", "max_tokens", "messages")
    assert rr.payload_body("s", "u") == b, "the local body copy is not rr.payload_body's body"
    # 11. the DB guard
    for bad_db in FORBIDDEN_DB_BASENAMES:
        try:
            sqlite3.connect(os.path.join(ROOT, bad_db))
            raise AssertionError("the DB guard allowed %s" % bad_db)
        except SystemExit as e:
            assert "[DBGUARD]" in str(e)
    try:
        sqlite3.connect("file:%s/experiment_results/x12_crossdomain/rejudge_grok.db?mode=ro" % ROOT, uri=True)
        raise AssertionError("the DB guard allowed a foreign verdict cache")
    except SystemExit:
        pass
    con = sqlite3.connect(":memory:")                       # allowed
    con.close()
    # 12. the READY gate and the night ceiling
    saved = os.environ.pop(GO_ENV, None)
    try:
        try:
            go_gate("selftest")
            raise AssertionError("the gate did not refuse without %s" % GO_ENV)
        except SystemExit as e:
            assert "[READY]" in str(e) and "refused" in str(e)
        os.environ[GO_ENV] = GO_VALUE
        if not os.path.exists(READY):
            try:
                go_gate("selftest")
                raise AssertionError("the gate did not refuse without the READY file")
            except SystemExit as e:
                assert "MISSING" in str(e)
    finally:
        if saved is None:
            os.environ.pop(GO_ENV, None)
        else:
            os.environ[GO_ENV] = saved
    global NIGHT_LEDGER, CACHE
    sl, sc = NIGHT_LEDGER, CACHE
    try:
        NIGHT_LEDGER = os.path.join(ROOT, "no_such_night_ledger.json")
        CACHE = os.path.join(ROOT, "no_such_cache_" + CACHE_DB_NAME)
        night_line(10, "selftest")                           # no ledger, no cache: 0 + 10 <= ceiling
        try:
            night_line(NIGHT_CEILING + 1, "selftest")
            raise AssertionError("the night ceiling did not refuse")
        except SystemExit as e:
            assert "[NIGHT] REFUSED" in str(e)
    finally:
        NIGHT_LEDGER, CACHE = sl, sc
    # 13. the prompt and the PER-TASK reference of record (ruling BFCL-REF-ORACLE)
    s = system_prompt()
    assert SYSTEM_BFCL in s and RUBRIC_BFCL in s and "$systemPrompt" not in s and "$rubric" not in s
    assert "MEASURED: this instruction does not work" not in s, "v2 must not carry the v1 comment block"
    for name, txt in (("SYSTEM_BFCL", SYSTEM_BFCL), ("RUBRIC_BFCL", RUBRIC_BFCL)):
        low = txt.lower()
        for forbidden in ("verdict", "defer", "all_pass", "the checker says", "is correct", "error_type"):
            assert forbidden not in low, "%s names %r; amendment item (2) forbids it" % (name, forbidden)
        for w in ("pass", "passed", "fail", "failed"):
            assert not re.search(r"\b%s\b" % w, low), "%s names %r; amendment item (2) forbids it" % (name, w)
    ref, cut = render_reference([["cd(folder='x')", "ls()"], ["mv(a='1',b='2')"]])
    assert cut == 0 and "Turn 1: cd(folder='x') ; ls()" in ref and "Turn 2: mv(a='1',b='2')" in ref
    assert "not necessarily the only one" in ref and "state-based" in ref
    big, cut2 = render_reference([["f(x='%s')" % ("y" * 3000)]])
    assert cut2 == 1 and big.endswith(REFERENCE_CUT_MARKER % REFERENCE_TEXT_CAP)
    # order-invariance: the task statement (and therefore the reference) is byte-identical in both orders
    q = "task statement" + ref
    u1 = rj.build_user_prompt(q, "TA", "TB")
    u2 = rj.build_user_prompt(q, "TB", "TA")
    assert u1 != u2 and u1.count(ref) == 1 and u2.count(ref) == 1, "the reference must appear once, identically, in both orders"
    # the ruling's guard: it passes on the reference of record and REFUSES the rejected per-side form
    ea = {"checker_output": "PASS", "error_type": None}
    eb = {"checker_output": "multi_turn:instance_state_mismatch: the state differs", "error_type": "multi_turn:instance_state_mismatch"}
    assert_no_per_side_verdict(q, ea, eb)
    for leak in ("\n[Outcome checker report]\nModel A - PASS", "\nModel B - multi_turn:instance_state_mismatch: the state differs",
                 "\nall_pass: true", "\nthe checker returned PASS for the first attempt"):
        try:
            assert_no_per_side_verdict(q + leak, ea, eb)
            raise AssertionError("the ruling's guard accepted a per-side leak: %r" % leak)
        except SystemExit as e:
            assert "[ORACLE-HAZARD]" in str(e) and "[RULING] REFUSED" in str(e)
    # 14. EVERY MODE THROUGH THE CLI'S OWN ARGUMENT SHAPE: each must reach go_gate - the FIRST statement of launch() -
    #     and be refused there, and none may raise anything else first (the run branch passes n=None: the 66aaaf7
    #     defect, a TypeError one line before the gate, would surface here and not in a live launch).
    shapes = cli_launch_shapes(pilot_n=12, workers=8)
    modes = [sh[0] for sh in shapes]
    assert sorted(modes) == ["pilot", "probe", "run"], "the CLI dispatch no longer drives exactly probe / pilot / run: %r" % (shapes,)
    saved_go = os.environ.pop(GO_ENV, None)
    try:
        for sh in shapes:
            mode = sh[0]
            try:
                launch(*sh)
                raise AssertionError("launch%r was not refused by go_gate" % (sh,))
            except SystemExit as e:
                assert "[READY]" in str(e) and "refused" in str(e), "launch%r did not stop at go_gate: %s" % (sh, str(e)[:160])
                label = {"probe": "--probe", "run": "--run"}.get(mode) or ("--pilot %d" % sh[1])
                assert label in str(e), "launch%r reached the gate with the wrong label: %s" % (sh, str(e)[:160])
    finally:
        if saved_go is None:
            os.environ.pop(GO_ENV, None)
        else:
            os.environ[GO_ENV] = saved_go
    print("selftest OK: cap (middle-drop, head+tail kept, final state always whole, state-over-cap class), the C2 rule, "
          "parts() == agent_admission_pilot.artefact_text, the checker-disagreement filter, conventions A/B, the "
          "clustered bootstrap and the ladder reading, Wilson, NON_TERMINATED / content_filter never a verdict, the "
          "count-delta refusal, the fail-closed fingerprint, the body copy asserted against rr.payload_body with the "
          "temperature omitted, the DB guard on %d forbidden names, the READY gate, the night ceiling, the PER-TASK "
          "reference of record with its cut and its order-invariance, the two prompt strings against amendment item "
          "(2), and the ruling guard refusing every per-side leak (opens no file of record, 0 calls)"
          % len(FORBIDDEN_DB_BASENAMES))
    print("selftest OK: 14 cases | case 14, the CLI's own argument shapes read from this file's __main__ dispatch and "
          "each driven into launch(): %s -> all three reached go_gate and were REFUSED there with the right label "
          "(nothing raised before the gate; 0 calls, no cache, no ledger row)"
          % ", ".join("launch%r" % (sh,) for sh in shapes))
    print(dbguard_line())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="%s - %s" % (TEST, REGISTRATION))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--probe", action="store_true", help="the item-19 max_tokens preflight: %d matches = %d calls; never an arm" % (PROBE_MATCHES, 2 * PROBE_MATCHES))
    ap.add_argument("--pilot", type=int, default=None, help="post the first N matches of the headline deck (2N calls); gated")
    ap.add_argument("--run", action="store_true", help="post every remaining match of both strata; gated")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--draws", type=int, default=BOOT)
    ap.add_argument("--no-payload", action="store_true", help="--dry-run without the first payload dump")
    ap.add_argument("--override-guard", action="store_true", help="post past the 5%% guard (recorded in run_meta)")
    a = ap.parse_args()
    OVERRIDE_GUARD = a.override_guard
    if a.selftest:
        selftest()
    elif a.dry_run:
        dry_run(show_payload=not a.no_payload)
    elif a.probe:
        launch("probe", PROBE_MATCHES, a.workers)
    elif a.pilot is not None:
        launch("pilot", a.pilot, a.workers)
    elif a.run:
        launch("run", None, a.workers)
    elif a.analyze:
        analyze(a.draws)
    else:
        ap.print_help()
