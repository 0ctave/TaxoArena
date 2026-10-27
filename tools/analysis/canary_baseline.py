"""CANARY-BASELINE — the frozen 300-match canary set judged twice, one week apart (FRAMEWORK.md item 21; registered by
reference at eaf1dbf; parameters fixed in docs/plan_2026-09-15.md, Block 2 a and g, and Amendment 1 D1/D2).

  python tools/analysis/canary_baseline.py --dry-run [--pass N] [--pilot N]  (zero calls: payloads assembled, nothing posted)
  python tools/analysis/canary_baseline.py --pass 1 [--pilot N] [--workers 8] [--maxtok 8192]
  python tools/analysis/canary_baseline.py --pass 2 ...                    (refused before 2026-09-22 and unless pass 1's record matches)
  python tools/analysis/canary_baseline.py --analyze

WHAT IT MEASURES. Stage 9's canary arm A needs the set's OWN test-retest floor: DECOMP's 0.057 was measured on 299
contested frontier matches under grok and is not the null for a mixed set. This judges 300 matches frozen from the x12
MAIN schedule - 150 CONTESTED (frontier pairs among the top-4, plus pairs inside one key tier at the 0.017 gap) and 150
CROSS-TIER - under the frozen STACK-v2 recipe with grok-4-1-fast-non-reasoning, the DEPLOYED judge (FRAMEWORK.md Stage 3;
Amendment 1 D1), posted through rejudge_reasoning exactly as RECIPE-GROK (stack_judge --judge grok), ARENA-13 and DECOMP
posted it; the prompts are byte-identical to the ones stack_judge.py --prompt v2 posted for the board of record. Pass 1
now; pass 2 is the same script with --pass 2 not before 2026-09-22, in its own cache. The floor is the share of paired
matches whose dual-order verdict differs between the passes; its interval is question-clustered. Criterion (registered):
measured floor and agreement with interval; sets the alarm. Prediction: floor 4-6% on the contested half, lower on the
cross-tier half.

INVARIANTS. pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL) first; questions only from p2dca21ab5f4ef3ae (printed as the first
line); the set of record is canary_set.json, hash 50af669ac6997f9f, committed with Amendment 1 - it is loaded and
verified, NEVER re-frozen by a judged pass or a dry-run (only --freeze-only rebuilds it, and must reproduce the hash);
own cache per pass (canary_baseline_pass{N}.db, never an existing cache); every call through
rejudge_reasoning.call_judge_full so finish_reason and completion_tokens are stored per call; finish_reason == length
is NON_TERMINATED and never a verdict; explicit --maxtok (default 8192 = rejudge_reasoning.MAX_TOKENS, the budget every
grok run of record posted); temperature OMITTED (provider default, Amendment 1 D2), recorded as such in run_meta and the
outcome header; run_meta is pinned at first launch ('started', script sha, protocol, max_tokens, temperature, set hash)
and a relaunch that differs on any of them is REFUSED, resumes are appended; the pilot gate: once cached rows exist the
run refuses to post more when their invalid/non-terminated rate exceeds 5% (--override-guard posts anyway and is
recorded); pass 2 pre-flight: pass 1's cache must hold all 300 verdicts under the same protocol, max_tokens, temperature
and set hash or pass 2 is refused before any call; pilot or incomplete outcomes go to canary_baseline_outcome_partial.txt,
never the outcome of record; the analysis REFUSES a verdict when more than 5% of the deciding subset is unparsed or
non-terminated; Meta-Llama-3-70B-Instruct excluded (asserted absent).
[ADDED 2026-09-22, READY_canary_pass2 defect 1 path A] the deployment fingerprint rejudge_reasoning.call_judge_full returns as its
2nd element ("azure:" + the response's model field, rejudge_reasoning.py:131) is kept per call and stored as provider1 / provider2
(one per order) in the pass cache; after each call it must equal EXPECTED_FINGERPRINT ("azure:grok-4-1-fast-non-reasoning") or the
run STOPS with a [FINGERPRINT] line and nothing is cached for that match (fail-closed; the only exemption is rr's deterministic
content-filter sentinel "azure:refusal" with finish_reason content_filter, which rule 10 requires cached as an unusable row); the
fingerprint set is printed in the GUARD line and in --analyze's header; a cache without the columns (pass 1) reads
"not recorded (pre-rule)" and is never migrated. The posted bytes are unchanged.
[ADDED 2026-09-23, post-run review 2026-09-22 defects 1-4] --analyze writes the outcome in mode "w", so everything of record it must
carry it now prints itself and a re-run on a complete pass-1 + pass-2 pair reproduces the file (only the header's script sha and the MDE
line move): (1) "ALARM STATE: <NO ALARM|ALARM|UNDETERMINED>" FLUSH-LEFT at column 0 immediately after the ALARM line - the consumer
(placement_steps.py:142) tests startswith on the unstripped line - decided by the registered rule (ii) (pre-run bracket 96bd3d7,
programme L3631) on the CONTESTED floor under BOTH conventions: <= 0.114 -> NO ALARM, above -> UNDETERMINED (a third pass); ALARM is not
a permitted state at pass 2 and is live only from the epoch after the floor is set, so this script never emits it; (2) the convention-A
floor line (INVALID or non-terminated in either pass = disagreement, the pair kept, full paired denominators, plus the dropped-pair
count) beside the convention-B floors, per rule (iv); (3) the MDE read from the MEASURED SE (1.96 x SE at n = 300 and at n ~ 1,000 at the
measured DEFF, and the one-sided 3-SE alarm threshold), never from DECOMP's 0.057 literal. The two hand-inserted lines of 4178a7c are
carried VERBATIM as ALARM_STATE_NOTE / CONV_A_NOTE (rule 3, insertion only). Nothing the run posts, no number, no schema, no default and
no prompt path changed.
[CORRECTED 2026-09-23 by READY_canary_analyze_fix_and_leaf.md (ad65d09), insertion only - the four sentences above stand as written, these
correct and complete them] (a) "the consumer (placement_steps.py:142)" overstates it: that reader opens ARM-B-VINTAGE's
ref_remint_outcome.txt, NOT this outcome. The canary's ALARM STATE line has NO programmatic consumer today; all that is claimed is that it
is FORMAT-COMPATIBLE with that reader's pattern (an exact-equality startswith on the unstripped line, hence column 0), so a future consumer
can read it. (b) the degraded paths are now guarded too: five early returns (PROTOCOL GUARD, the refused >5% guard, pass 2 not judged, no
paired valid matches) produce a readout with no ALARM STATE line, and in mode "w" they would still have erased the two verbatim brackets;
write() now REFUSES to touch the outcome of record in that case and diverts to canary_baseline_outcome_partial.txt with a loud
[WRITE-GUARD] line, so NO --analyze invocation in ANY state can lose a line of record. (c) rule (ii) is decided on the floor AS PRINTED, at
3 dp (rule (i) reads the printed floor), so alarm_state() compares float("%.3f" % floor) to the 0.114 bar and cannot diverge from the file
on (0.114, 0.1145]. (d) the verbatim convention-A wording "(pass 1 INVALID %d, pass 2 INVALID %d)" is a DOC DEFECT inherited from 4178a7c:
the two counts are bad_row counts (INVALID or non-terminated), not INVALID counts. It is a recorded sentence and is reproduced unchanged;
it reads 0 / 0 on the pair of record, where the two readings coincide. Convention B, for its part, drops a pair only when either pass is
INVALID - a non-terminated pass-2 row stays in B's denominator - while convention A counts BOTH kinds as a disagreement; that asymmetry is
the script's behaviour of record and is asserted in canary_baseline_selftest.check_conventions_differ.
[ADDED 2026-09-24 by the engine-coder for CANARY-EPOCH2-RUNG (registered 2026-09-23 at fad9ea2, docs/judge_v2_program.md L14931-L14970;
record docs/agents/results/CANARY-EPOCH2-RUNG.json; accepted by the author, plan Amendment 12), insertion only - every sentence above
stands, these extend it; zero calls were made to build it.]
  python tools/analysis/canary_baseline.py --selftest-epoch2                  (0 calls; temp fixtures; an INJECTED FAKE POSTER; socket guard)
  python tools/analysis/canary_baseline.py --dry-run --pass 3|4 [--pilot 12]  (0 calls: payload anchors, counts, ceiling, pins, leak scan)
  python tools/analysis/canary_baseline.py --pass 3 --pilot 12 --go           (24 calls, the first 12 matches of the set in the set's order)
  python tools/analysis/canary_baseline.py --pass 3 --run --go                (the remaining 576; REFUSED unless the pilot is cached and <= 5%)
  python tools/analysis/canary_baseline.py --pass 4 --pilot 12 --go / --run --go   (the RUNG: REFUSED more than 2 h after pass 3's last row)
  python tools/analysis/canary_baseline.py --analyze-epoch2 [--no-rung]       (-> canary_epoch2_outcome.txt, WRITE-ONCE, complete caches only)
(1) POST-RUN REVIEW 2026-09-22 D2, COMPLETED: --analyze no longer opens the outcome of record in mode "w": it is written with mode "x"
only when absent, and an existing outcome is NEVER overwritten (the readout is printed, a [WRITE-ONCE] line says nothing was written);
partial / pilot readouts still go to canary_baseline_outcome_partial.txt, which is not of record. The "ALARM STATE:" line, the convention-A
line and the measured-SE MDE line (the rest of D2, c3d931b / 665a739) are unchanged. (2) PASSES 1 AND 2 ARE CLOSED: posting into
canary_baseline_pass1.db / _pass2.db is REFUSED (their sha256 are pinned below and checked before and after every epoch-2 launch, dry-run
and analysis; a changed cache of record is a refusal, never a warning). (3) THE DB GUARD (epoch-2 modes): every sqlite3.connect in the
process is rewritten to file:<abs>?mode=ro&immutable=1 after the -wal / -journal emptiness check, and the ONLY writable file is the NEW
cache of the pass being posted (canary_baseline_pass3.db or _pass4.db). stack_judge's read-write open_cache() is never called on this
path and would be refused by the guard if it were (queue item STACK-JUDGE-RO-CACHE). (4) PASS 3 pre-flight (read-only): passes 1 and 2
complete under the same protocol and the pass 1 -> 2 floor 26/300 REPRODUCED from the caches (convention A); PASS 4 pre-flight: pass 3
complete, every pass-3 call fingerprinted, and NOW within RUNG_WINDOW_S = 7,200 s of pass 3's last row, else REFUSED (the rung would be
UNDETERMINED BY VALIDITY). (5) THE GATE: posting passes 3 / 4 needs --pilot N or --run, --go, and a COMMITTED
docs/reviews/READY_canary_epoch2_rung.md whose FIRST verdict line names CANARY-EPOCH2-RUNG and this script's LF sha16; --run needs the
pass's 12-match pilot cached and <= 5% unusable. The night ledger experiment_results/night_calls_2026-09-23.json is read before (cumulative
+ this launch <= 14,000; this test's own calls + this launch <= 1,200) and APPENDED after every posting launch in a `finally`, every posted
call counted. (6) PROVENANCE PER ROW (passes 3 / 4 only; the first 26 columns are byte-for-byte pass 2's): response ids, the posted user
bodies and their sha16, the system sha16, the submission index and the script's LF sha. (7) THE PRE-CALL FULL-PAYLOAD LEAKAGE SCAN (every
epoch-2 launch and dry-run, all 600 payloads): each user turn decomposes exactly into the template's fragments and its three slots (question
+ reference, trace A, trace B, assembled independently of str.replace); the frame (everything outside the two trace slots) is identical in
the two orders, i.e. carries nothing per-side; no contestant name and no key-side token is in the frame. The post-run reviewer's own
full-payload scan is still required. (8) POSTING ORDER: the set's order (canary_set.json, the order pass 2 posted and piloted), printed with
its sha16. (9) Temperature omitted, recorded "omitted". (10) --analyze-epoch2 reads the registered C0-C4, P1-P6 and the falsifier; the
machine-readable lines "ALARM STATE: <...>" and "RUNG d43 = <point> [<lo>, <hi>]" are flush-left.
[CORRECTED 2026-09-24 by the registrar's rulings b0b5d0d (programme L15188-L15206), insertion only: (a) THE ACCOUNTING FILE: the
2026-09-23 night ledger in (5) is NOT the count of record for later posts. The guard is accepted_tests_ledger.guard: it refuses on (i)
this test's own ceiling 1,200 (passes 3 + 4: its caches and its rows in every ledger, the larger), (ii) the 4,000-match rule, (iii)
4,060 + the calls posted by BOTH accepted tests (their caches / ledgers) + this launch > 14,000; the three numbers are printed on every
launch and in the epoch-2 outcome; posted calls are appended to experiment_results/day_calls_<posting date>.json, created write-once.
(b) C1 IS DECIDED UNDER CONVENTION A (all 300 matches; an unusable verdict counts as a difference), B printed beside; when A and B
disagree on the ALARM both are recorded and A decides (--analyze-epoch2 prints the B-reading and the disagreement line).]
[CORRECTED 2026-09-24 by the READY review docs/reviews/READY_canary_epoch2_rung.md (7b102ad, NOT READY at e1ed7466917bd8fb), insertion
only - D1-D4, D6-D8 fixed: (D1) once pass 3 is complete, --analyze-epoch2 WRITES THE OUTCOME OF RECORD whatever the state of pass 4:
absent with --no-rung (a declaration, only meaningful when no pass-4 file exists), or present with ANY number of rows (0, a pilot, a
partial run); an incomplete pass 4 reads rung INVALID with its row count printed, C2 UNDETERMINED BY VALIDITY, C1 recorded; a pass-4
cache absent WITHOUT --no-rung stays partial (pass 4 may still run). Once the epoch-2 outcome of record exists, every epoch-2 posting
launch is REFUSED (the record is closed). (D2) the pass-4 2 h window is measured from pass 4's persisted START (run_meta 'started', pinned
at its first launch) when a pass-4 cache exists, and from now only for the first launch. (D4) the set is re-verified by verify_set()
with explicit SystemExit (freeze_set's asserts vanish under -O; freeze_set itself is untouched, it is payload-path code AST-identical to
the pass-2 script 7d9a4e2e), and C0 (a) RECOMPUTES the set hash. (D6) the pilot's guard counts this launch's errored (uncached) matches
as unusable, in its denominator and numerator. (D7) passes 3 / 4: --pilot must be 12 and --override-guard is refused. (D8) the READY
verdict regex no longer lets '^\s*' consume a preceding blank line.]
"""
import os, sys, json, time, random, sqlite3, hashlib, argparse, datetime, threading
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):                       # the prompts carry non-cp1252 characters; a redirected Windows stdout must not crash the run
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import stack_judge as sj
import judge_free_tests as jf
import x20_replications as xr
import accepted_tests_ledger as atl                    # CANARY-EPOCH2-RUNG accounting guard (b0b5d0d)

POOL = pool_guard.FROZEN_POOL_ID                       # p2dca21ab5f4ef3ae
JUDGE = "grok-4-1-fast-non-reasoning"                  # the DEPLOYED judge (FRAMEWORK.md Stage 3; Amendment 1 D1), as stack_judge.py:96 / arena13.py:89 / position_decomp.py:39
REFERENCE = "grok-reasoning"                           # STACK-v2's cached reasoning reference
EXPECTED_FINGERPRINT = "azure:" + JUDGE                # rejudge_reasoning.call_judge_full's 2nd element: "azure:" + response model (rejudge_reasoning.py:131)
REFUSAL_FINGERPRINT = "azure:refusal"                  # rr's sentinel on a deterministic HTTP 400 content_filter (finish_reason content_filter); cached, never a verdict
FINGERPRINT_NOT_RECORDED = "not recorded (pre-rule)"   # what a cache without provider1/provider2 (pass 1) reads as; never migrated
EXCLUDED = {"Meta-Llama-3-70B-Instruct"}
SEED = 42
PER_STRATUM = 150
N_SET = 2 * PER_STRATUM
NOT_BEFORE_PASS2 = datetime.date(2026, 9, 22)
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
SET_JSON = os.path.join(X12DIR, "canary_set.json")
SET_HASH_OF_RECORD = "50af669ac6997f9f"                # Amendment 1 D1: the frozen set committed with the amendment
OUT = os.path.join(X12DIR, "canary_baseline_outcome.txt")
OUT_PARTIAL = os.path.join(X12DIR, "canary_baseline_outcome_partial.txt")
DEFAULT_MAXTOK = rr.MAX_TOKENS                         # 8192, the budget RECIPE-GROK / ARENA-13 / DECOMP posted
MAXTOK = DEFAULT_MAXTOK
TEMPERATURE = None                                     # None = field omitted (provider default): Amendment 1 D2
NPASS = 1
GUARD_RATE = 0.05
CONTESTED_ALARM_BAR = 0.114                            # rule (ii), pre-run bracket 96bd3d7 (programme L3631): contested floor <= 0.114 -> NO ALARM, above -> UNDETERMINED
ALARM_STATES = ("NO ALARM", "ALARM", "UNDETERMINED")   # the permitted states; ALARM is live only from the epoch AFTER the floor is set, so this script (passes 1-2) never emits it
# Record text carried by the script so that a re-run of --analyze cannot lose it (post-run review 2026-09-22 defect 2): the two lines
# below were inserted by hand into canary_baseline_outcome.txt at 4178a7c and are reproduced here VERBATIM, byte for byte. They are a
# recorded sentence (rule 3, insertion only): never reworded here. The set and the two passes are frozen, so their numbers cannot go stale.
ALARM_STATE_NOTE = ('  [INSERTED 2026-09-22 by the post-run review, rule (ii) 96bd3d7: contested floor 0.087 <= 0.114 under both conventions; ALARM is live '
                    'from epoch 2; the MDE literal below is registration text at 0.057: at the measured floor 1.96 x SE = 3.3pp at n = 300 (DEFF 1.09), 1.8pp '
                    'at n ~ 1,000; the one-epoch alarm at 0.138 needs a +5.1pp drift; --analyze rewrites this file in mode "w" and must not be re-run on it '
                    'before the script prints these lines itself]')
CONV_A_NOTE = "  [INSERTED 2026-09-22 by the post-run review, rule (iv) 96bd3d7]"

# ── CANARY-EPOCH2-RUNG (2026-09-24; docs/judge_v2_program.md L14931-L14970, fad9ea2) ──────────────────────────────
TEST_EPOCH2 = "CANARY-EPOCH2-RUNG"
REGISTRATION_EPOCH2 = ("docs/judge_v2_program.md L14931-L14970 (registered 2026-09-23 at fad9ea2, before any code or call); record "
                       "docs/agents/results/CANARY-EPOCH2-RUNG.json")
PASS_CACHE_SHA256 = {1: "5142795bdc8c5a8ec8d09a3a4f9cd6c84de206834aeab7ca11cea4761000690c",   # the record's pin (L3631 (v))
                     2: "9e2f4b7cb2b30b3a2a7abf897c8bb531d5c6c14eebd21668ed6ab3d747132c4e"}   # TIE-MECHANICS' pin 9e2f4b7c
OUT_EPOCH2 = os.path.join(X12DIR, "canary_epoch2_outcome.txt")
OUT_EPOCH2_PILOT = os.path.join(X12DIR, "canary_epoch2_outcome_PILOT.txt")
OUT_EPOCH2_PARTIAL = os.path.join(X12DIR, "canary_epoch2_outcome_partial.txt")
READY_EPOCH2 = os.path.join(ROOT, "docs", "reviews", "READY_canary_epoch2_rung.md")
LEDGER_DIR = os.path.join(ROOT, "experiment_results")   # day_calls_<posting date>.json (b0b5d0d) + the closed 09-23 file
TRACE_CACHES = atl.default_caches(ROOT)["TRACE-TRUNCATION"]   # read-only, for the combined statement (iii)
NIGHT_CEILING = 14000                                  # plan Amendment 9
EPOCH2_CEILING = 1260                                  # passes 3 + 4, the pilots included [1,200 -> 1,248: amendment CANARY-EPOCH2-RUNG-CEILING-1, author-approved 2026-09-24; pass 3 needed 22 HTTP-429 retries] [1,248 -> 1,260: CANARY-EPOCH2-RUNG-CEILING-2, author-approved 2026-09-24; pass 4 needed 20 retries]
EPOCH2_REGISTERED_CALLS = 1200                         # 2 passes x 300 matches x 2 orders: the count P6 reads ("1,200 of 1,200"), NOT the ceiling
EPOCH2_PASSES = (3, 4)
RUNG_WINDOW_S = 7200                                   # pass 4 starts <= 2 h after pass 3's last row
PILOT_N = 12
FLOOR12_OF_RECORD = 26                                 # the pass 1 -> 2 floor 26/300 (convention A = B), C0
ALARM_NUM, ALARM_DEN = 138, 1000                       # ALARM iff d32 >= 0.138; THE POINT DECIDES (integer comparison)
POOLED_BAR_900 = 0.116                                 # C4, descriptive (n = 900)
EPOCH2_BOOT, EPOCH2_SEED, EPOCH2_EXTRA_SEEDS = 2000, 42, tuple(range(43, 63))
EPOCH2_REG_SUPPORT = ("REGISTERED SUPPORT: (a) 300 frozen matches over 279 questions, Kish mean cluster size 1.14 [corrected to 1.160 by "
                      "TIE-MECHANICS' review 64bdecb]; (b) DEFF 1.09 MEASURED on the pass 1 / pass 2 pair; (c) n_eff 275.2; (d) SE 0.0170 "
                      "(match-level disagreement indicator, not per-call arithmetic); SE(Delta) <= 0.034 by the triangle inequality; (e) MDE "
                      "C1 0.0476, C2 <= 0.095; (f) C1 SCOREABLE (thin: 0.051 vs 0.048), C2 DESCRIPTIVE-ONLY; (g) C2 bounded by the frozen set.")
EPOCH2_EXTRA_COLS = ("resp_id1", "resp_id2", "system_sha16", "user1_sha16", "user2_sha16", "user1", "user2", "post_index", "script_sha16_lf")
FRAME_TOKENS = ("is_correct", "checker", "ground_truth", "answer_key")
EPOCH2_BRANCHES = frozenset(
    ["C0:PASS", "C0:FAIL", "RUNG:VALID", "RUNG:INVALID", "RUNG:ABSENT",
     "C1:ALARM", "C1:NO_ALARM", "C1:UND_VALIDITY", "C1:AB_AGREE", "C1:AB_DISAGREE", "C2:READ", "C2:UND_VALIDITY",
     "C3:READ", "C4:READ", "FALS:ALARM_FIRES", "FALS:P3_LOW", "FALS:P3_HIGH", "FALS:P5_FIRES", "FALS:NOT_FIRED", "FALS:NOT_EVALUATED",
     "WRITE:RECORD", "WRITE:PARTIAL", "WRITE:REFUSED_EXISTS"]
    + ["%s:%s" % (p, v) for p in ("P1", "P2", "P3", "P4", "P5", "P6") for v in ("HELD", "FAILED", "UND")])
EPOCH2_HIT = set()


def ehit(tag):
    if tag not in EPOCH2_BRANCHES:
        raise SystemExit("[BRANCH] undeclared branch tag %r" % tag)
    EPOCH2_HIT.add(tag)


def alarm_state(contested_b, contested_a, bar=CONTESTED_ALARM_BAR):
    """Registered rule (ii) (pre-run bracket 96bd3d7, programme L3631): NO ALARM iff the CONTESTED floor is at or below the
    bar under BOTH conventions, else UNDETERMINED (a third pass). The floors are compared AS PRINTED, at 3 dp, because rule
    (i) reads the printed floor; an unrounded comparison would diverge from the file on (0.114, 0.1145]. A missing floor is
    UNDETERMINED, never NO ALARM. ALARM is a permitted state of the enum but is live only from the epoch AFTER the floor is
    set, so this script (passes 1-2) never returns it."""
    fs = [float("%.3f" % f) for f in (contested_b, contested_a) if f is not None]
    return "NO ALARM" if len(fs) == 2 and max(fs) <= bar else "UNDETERMINED"


def cache_path(n=None):
    return os.path.join(X12DIR, "canary_baseline_pass%d.db" % (n or NPASS))


def temp_label():
    return "omitted" if TEMPERATURE is None else repr(TEMPERATURE)


def protocol():
    return ("STACK-v2 | judge %s (azure chat completions via rejudge_reasoning, api-version 2024-05-01-preview) | prompt v2 verify-first + ladder "
            "anchor rubric (bareq512_s42 depth-1 anchor) + schema instruction | reference block = %s cached solve | dual order, "
            "TIE on flip, INVALID if either order unparsed or finish_reason=length | max_tokens %d | temperature %s"
            % (JUDGE, REFERENCE, MAXTOK, "omitted (provider default)" if TEMPERATURE is None else repr(TEMPERATURE)))


def rel(p):
    try: return os.path.relpath(p, ROOT)
    except ValueError: return p


def script_hash():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]


def set_hash(matches):
    canon = "\n".join("%d:%d:%s:%s:%s" % (m["match_id"], m["qid"], m["model_a"], m["model_b"], m["stratum"]) for m in matches)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def configure_rr():
    """Point rejudge_reasoning at the deployed judge exactly as RECIPE-GROK (stack_judge.py:96), ARENA-13 (arena13.py:89) and
    DECOMP (position_decomp.py:39) do. The key is whatever rr.load_env selects (AZURE_GROK_API_KEY, else AZURE_AI_API_KEY);
    no other key override exists (Amendment 1 D1). Reads no env, so the dry-run calls it too."""
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = TEMPERATURE


def payload_body(system, user):
    """Local copy of the body rejudge_reasoning.call_judge_full posts (rejudge_reasoning.py lines 92-96: model, max_tokens,
    messages, optional temperature). The dry-run asserts the key tuple and the source text so a drift there is caught at zero calls."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None: body["temperature"] = rr.TEMPERATURE
    return body


# ── the frozen set ──────────────────────────────────────────────────────────────

def pool_qids():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    return {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}


def strata_of(models):
    """Frontier = both in the x12 top cluster; key-tie = same key tier at the 0.017 gap (x20_replications.key_tiers on key
    accuracy over the pool of record, as KEY-TIE-DECLINE tiers); contested = frontier or key-tie; else cross-tier."""
    acc, _ = jf.gt_and_lengths(set(models))
    tiers = xr.key_tiers(acc, sorted(models), gap=xr.KEY_GAP)
    tier_of = {m: i for i, t in enumerate(tiers) for m in t}

    def kind(a, b):
        if a in rj.TOP_CLUSTER and b in rj.TOP_CLUSTER: return "frontier"
        if tier_of[a] == tier_of[b]: return "keytie"
        return "cross"
    return kind, tiers, acc


def freeze_set(allow_freeze=False):
    """Load and verify the set of record (hash SET_HASH_OF_RECORD, Amendment 1 D1). Returns (matches, meta).
    Building is allowed only under --freeze-only (allow_freeze=True) and must reproduce the hash of record before anything is
    written; a judged pass or a dry-run REFUSES to re-freeze, so a missing file can never silently produce a different set."""
    pool = pool_qids()
    if os.path.exists(SET_JSON):
        d = json.load(open(SET_JSON, encoding="utf-8"))
        ms = d["matches"]
        assert d["pool_id"] == POOL and set_hash(ms) == d["set_hash"], "canary_set.json does not verify"
        assert d["set_hash"] == SET_HASH_OF_RECORD, "canary_set.json hash %s is not the hash of record %s" % (d["set_hash"], SET_HASH_OF_RECORD)
        assert len(ms) == N_SET, "canary_set.json holds %d matches, not %d" % (len(ms), N_SET)
        assert all(m["qid"] in pool for m in ms), "a frozen match is outside the pool of record"
        assert not ({m["model_a"] for m in ms} | {m["model_b"] for m in ms}) & EXCLUDED
        return ms, d
    if not allow_freeze:
        raise SystemExit("[SET] %s is missing. The set of record (hash %s) is committed with plan Amendment 1: restore it from git. "
                         "A judged pass or a dry-run never re-freezes; --freeze-only rebuilds it and must reproduce the hash of record."
                         % (rel(SET_JSON), SET_HASH_OF_RECORD))
    rref.set_reference(REFERENCE); refs = rref.references()
    anchors = sj.routed_anchor()
    rows = sj.all_x12_matches()                           # id, eval_question_id, model_a, model_b, node_id, winner, is_tie
    models = sorted({r[2] for r in rows} | {r[3] for r in rows})
    assert not set(models) & EXCLUDED, "excluded model present in the x12 schedule"
    kind, tiers, acc = strata_of(models)
    cand = defaultdict(list); dropped = Counter()
    for mid, q, a, b, nid, w, t in rows:
        q = int(q)
        if q not in pool: dropped["outside pool"] += 1; continue
        if q not in refs: dropped["no reference"] += 1; continue
        if q not in anchors: dropped["no anchor"] += 1; continue
        k = kind(a, b)
        cand["contested" if k in ("frontier", "keytie") else "cross"].append(
            dict(match_id=mid, qid=q, model_a=a, model_b=b, node_id=nid, anchor=anchors[q], stratum="contested" if k != "cross" else "cross", pair_kind=k))
    rng = random.Random(SEED); out = []
    for s in ("contested", "cross"):
        lst = sorted(cand[s], key=lambda m: m["match_id"]); rng.shuffle(lst); out.extend(lst[:PER_STRATUM])
    rng.shuffle(out)                                      # so a --pilot prefix spans both strata
    assert len(out) == N_SET
    meta = dict(test="CANARY-BASELINE", pool_id=POOL, source="x12 MAIN match_history, snapshot %s" % rj.SNAP_MAIN, seed=SEED,
                per_stratum=PER_STRATUM, key_gap=xr.KEY_GAP, top_cluster=sorted(rj.TOP_CLUSTER), key_tiers=tiers,
                key_accuracy={m: round(acc[m], 4) for m in models}, candidates={s: len(v) for s, v in cand.items()},
                dropped=dict(dropped), pair_kind_counts=dict(Counter(m["pair_kind"] for m in out)),
                pairs=dict(Counter("%s|%s" % (min(m["model_a"], m["model_b"]), max(m["model_a"], m["model_b"])) for m in out)),
                frozen_at=time.strftime("%Y-%m-%d %H:%M:%S"), set_hash=set_hash(out), matches=out)
    if meta["set_hash"] != SET_HASH_OF_RECORD:
        raise SystemExit("[SET] re-frozen set hash %s != hash of record %s; nothing written (the reference cache or anchors changed)"
                         % (meta["set_hash"], SET_HASH_OF_RECORD))
    json.dump(meta, open(SET_JSON, "w", encoding="utf-8"), indent=1)
    print("[SET] froze %d matches -> %s (hash %s = hash of record)" % (len(out), rel(SET_JSON), meta["set_hash"]))
    return out, meta


# ── payloads ────────────────────────────────────────────────────────────────────

def build_jobs(matches):
    """One job per match: (match dict, ref, system, user_order1, user_order2). Nothing posted."""
    sj.PROMPT = "v2"
    rref.set_reference(REFERENCE); refs = rref.references(); rubrics = sj.anchor_rubrics()
    evals = rj.load_eval_rows([m["qid"] for m in matches], {m["model_a"] for m in matches} | {m["model_b"] for m in matches})
    jobs = []
    for m in matches:
        ra, rb, ref = evals.get((m["qid"], m["model_a"])), evals.get((m["qid"], m["model_b"])), refs.get(m["qid"])
        assert ra is not None and rb is not None and ref is not None, "frozen match %d lost its traces or reference" % m["match_id"]
        q = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = sj.system_for(m["anchor"], rubrics)
        jobs.append((m, ref, system, rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)))
    return jobs


# ── cache ───────────────────────────────────────────────────────────────────────

def open_cache(n=None):
    n = n or NPASS
    if n not in EPOCH2_PASSES + EPOCH3_PASSES:             # CANARY-EPOCH2-RUNG (2): passes 1 and 2 are closed caches of record [2026-10-01: + pass 5, G17-CANARY v1 leg]
        raise SystemExit("[PASS] refusing to open %s for writing: passes 1 and 2 are complete caches of record (sha256 pinned); "
                         "only the NEW epoch-2 caches (passes %s) are ever written." % (rel(cache_path(n)), "/".join(map(str, EPOCH2_PASSES))))
    con = sqlite3.connect(cache_path(n))
    # stack_judge's 18 columns first, byte-for-byte the same names, so the STACK-v2 readers work on this cache; then the
    # per-call provenance the framework requires and the stratum; epoch 2 appends its per-row provenance AFTER pass 2's 26.
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, "
                "finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, stratum TEXT, pair_kind TEXT, provider1 TEXT, provider2 TEXT, "
                "resp_id1 TEXT, resp_id2 TEXT, system_sha16 TEXT, user1_sha16 TEXT, user2_sha16 TEXT, user1 TEXT, user2 TEXT, post_index INTEGER, "
                "script_sha16_lf TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit(); return con


class FingerprintMismatch(Exception):
    """Raised inside a worker when a call's deployment fingerprint is not EXPECTED_FINGERPRINT; run() turns it into a [FINGERPRINT] stop."""


def check_fingerprint(m, order, provider, finish):
    """Fail-closed: the 2nd element of rr.call_judge_full must be EXPECTED_FINGERPRINT. The one exemption is rr's deterministic
    content-filter sentinel (REFUSAL_FINGERPRINT with finish_reason content_filter), which rule 10 requires cached as an unusable row."""
    if provider == EXPECTED_FINGERPRINT: return
    if provider == REFUSAL_FINGERPRINT and finish == "content_filter": return
    raise FingerprintMismatch("match %d order %d: fingerprint %r != expected %r (finish_reason %r)" % (m["match_id"], order, provider, EXPECTED_FINGERPRINT, finish))


def fingerprint_counts(con):
    """Counter of provider1/provider2 over the cached calls, or None when the cache predates the columns (pass 1; never migrated)."""
    cols = {r[1] for r in con.execute("PRAGMA table_info(verdicts)")}
    if not {"provider1", "provider2"} <= cols: return None
    return Counter(dict(con.execute("SELECT COALESCE(p,'(none)'), COUNT(*) FROM (SELECT provider1 p FROM verdicts UNION ALL SELECT provider2 FROM verdicts) GROUP BY 1")))


def fingerprint_label(counts):
    return FINGERPRINT_NOT_RECORDED if counts is None else repr(dict(counts))


def current_meta(meta):
    return dict(test="CANARY-BASELINE", pass_no=str(NPASS), pool_id=POOL, judge=JUDGE, reference=REFERENCE, protocol=protocol(),
                max_tokens=str(MAXTOK), temperature=temp_label(), set_hash=meta["set_hash"])


def pin_meta(con, meta):
    """First launch writes the protocol of record and pins 'started' and the producing script's sha. Every later launch (pilot ->
    full run, resume) must equal the pinned keys or is REFUSED with both sides printed, so two budgets or two protocols can never
    share a cache; a relaunch is appended under 'resumed' and a changed script sha under 'script_sha256_16_relaunch'."""
    now = time.strftime("%Y-%m-%d %H:%M:%S"); cur = current_meta(meta)
    old = dict(con.execute("SELECT key, value FROM run_meta"))
    if old:
        bad = [(k, old.get(k), v) for k, v in cur.items() if old.get(k) != v]
        if bad:
            raise SystemExit("[META] refusing to resume into %s: the cache was produced under a different record\n  %s\n"
                             "  (a different max_tokens / temperature / protocol / set is a new session: move this cache aside and relaunch)"
                             % (rel(cache_path()), "\n  ".join("%s: recorded %r | now %r" % b for b in bad)))
        resumed = json.loads(old.get("resumed") or "[]") + [now]
        con.execute("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)", (json.dumps(resumed),))
        if old.get("script_sha256_16") != script_hash():
            con.execute("INSERT OR REPLACE INTO run_meta VALUES ('script_sha256_16_relaunch', ?)", (script_hash(),))
    else:
        for k, v in cur.items():
            con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v))
        con.execute("INSERT INTO run_meta VALUES ('started', ?)", (now,))
        con.execute("INSERT INTO run_meta VALUES ('script_sha256_16', ?)", (script_hash(),))
    con.commit()


def cached_guard(con):
    """(cached matches, matches invalid or non-terminated) over the rows already in this cache."""
    n = con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
    bad = con.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=1 OR finish1='length' OR finish2='length'").fetchone()[0]
    return n, bad


def preflight_pass2(meta):
    """Amendment 1 D1: pass 2 runs only against pass 1's record. Returns the refusals (empty list = go); reads pass 1 read-only."""
    p1 = cache_path(1)
    if not os.path.exists(p1): return ["pass 1 cache %s is missing" % rel(p1)]
    con = sqlite3.connect("file:%s?mode=ro" % p1, uri=True)
    probs = []
    n = con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
    if n != N_SET: probs.append("pass 1 holds %d of %d verdicts" % (n, N_SET))
    m1 = dict(con.execute("SELECT key, value FROM run_meta"))
    for k, v in current_meta(meta).items():
        if k == "pass_no": continue
        if m1.get(k) != v: probs.append("%s: pass 1 recorded %r | now %r" % (k, m1.get(k), v))
    return probs


# ── CANARY-EPOCH2-RUNG: guards, pins, gate, budget, scan (2026-09-24) ──────────────────────────────────────────

def _sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def script_hash_lf():
    """sha256[:16] of this file with CRLF normalised to LF: the LF rendering, = `git show HEAD:<path> | sha256sum`."""
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def order_sha(ids):
    return _sha16(",".join(str(i) for i in ids))


_TRUE_CONNECT = getattr(sqlite3.connect, "_true_connect", None) or sqlite3.connect
_REAL_CALL_JUDGE_FULL = rr.call_judge_full
_OPENED = []
_WRITABLE = [None]


def _path_of(database):
    s = str(database)
    if s.startswith("file:"):
        s = s[5:].split("?", 1)[0]
    return os.path.normcase(os.path.abspath(s))


def _guarded_connect(database, *args, **kwargs):
    """Every connect: the writable NEW pass cache as asked; anything else read-only + immutable after the sidecar check."""
    s = str(database)
    if s == ":memory:":
        return _TRUE_CONNECT(database, *args, **kwargs)
    p = _path_of(database)
    if _WRITABLE[0] is not None and p == _path_of(_WRITABLE[0]):
        _OPENED.append(("rw" if not s.startswith("file:") else "ro", p))
        return _TRUE_CONNECT(database, *args, **kwargs)
    ro = s.startswith("file:") and kwargs.get("uri") and "mode=ro" in s.split("?", 1)[-1]
    if not ro:
        raise SystemExit("[DBGUARD] REFUSED: a read-write open of %s was attempted; in the epoch-2 modes the ONLY writable file is %s "
                         "(no cache of record is ever opened for writing; stack_judge.open_cache is never called on this path)."
                         % (s, rel(_WRITABLE[0]) if _WRITABLE[0] else "none"))
    if not os.path.isfile(p):
        raise SystemExit("[DBGUARD] %s is missing; nothing is opened and nothing is posted." % p)
    for suf in ("-wal", "-journal"):
        if os.path.exists(p + suf) and os.path.getsize(p + suf) > 0:
            raise SystemExit("[DBGUARD] REFUSED: %s%s is non-empty (%d bytes): an immutable read would hide a live or hot transaction; "
                             "a FAILED PRECONDITION, never an outcome." % (p, suf, os.path.getsize(p + suf)))
    kwargs = dict(kwargs); kwargs["uri"] = True
    _OPENED.append(("ro-immutable", p))
    return _TRUE_CONNECT("file:%s?mode=ro&immutable=1" % p.replace("\\", "/"), *args, **kwargs)


_guarded_connect._true_connect = _TRUE_CONNECT


def install_db_guard(writable=None):
    _WRITABLE[0] = writable
    sqlite3.connect = _guarded_connect


def dbguard_line():
    seen = []
    for x in _OPENED:
        if x not in seen: seen.append(x)
    return "[DBGUARD] %d connect(s): %s" % (len(_OPENED), "; ".join("%s %s" % (m, rel(p)) for m, p in seen) or "(none)")


def pin_old_caches(when):
    """The two caches of record (passes 1, 2): sha256 against the pins, printed on both branches; a mismatch REFUSES."""
    got = {}
    for n in (1, 2):
        p = cache_path(n)
        got[n] = file_sha256(p) if os.path.exists(p) else None
        for suf in ("-wal", "-journal"):
            if os.path.exists(p + suf) and os.path.getsize(p + suf) > 0:
                raise SystemExit("[PIN] %s%s is non-empty: a writer touched a cache of record (%s)" % (rel(p), suf, when))
    ok = all(got[n] == PASS_CACHE_SHA256[n] for n in (1, 2))
    print("[PIN] %s: pass 1 %s (pin %s) | pass 2 %s (pin %s) -> %s"
          % (when, (got[1] or "MISSING")[:16], PASS_CACHE_SHA256[1][:16], (got[2] or "MISSING")[:16], PASS_CACHE_SHA256[2][:16],
             "UNCHANGED" if ok else "MISMATCH"), flush=True)
    if not ok:
        raise SystemExit("[PIN] REFUSED: a cache of record does not hash to its pin (%s); nothing is posted or read." % when)
    return got


def assert_body_source():
    """Rule 9: the local payload_body copy must equal rejudge_reasoning.payload_body (source and output)."""
    import inspect
    src = inspect.getsource(rr.payload_body)
    if not ('payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src):
        raise SystemExit("[BODY] rejudge_reasoning.payload_body changed; update payload_body()")
    if "payload_bytes(system, user)" not in inspect.getsource(_REAL_CALL_JUDGE_FULL):   # the module's own poster (a selftest may inject a fake)
        raise SystemExit("[BODY] call_judge_full no longer posts payload_body's bytes")
    if payload_body("S", "U") != rr.payload_body("S", "U"):
        raise SystemExit("[BODY] local copy %r != rr.payload_body %r" % (payload_body("S", "U"), rr.payload_body("S", "U")))


def _fragments():
    t = rj.USER_TEMPLATE
    if not (t.count("$query") == t.count("$traceA") == t.count("$traceB") == 1 and t.index("$query") < t.index("$traceA") < t.index("$traceB")):
        raise SystemExit("[TEMPLATE] rejudge_grok.USER_TEMPLATE no longer has $query < $traceA < $traceB once each")
    f0, rest = t.split("$query"); f1, rest = rest.split("$traceA"); f2, f3 = rest.split("$traceB")
    return f0, f1, f2, f3


def scan_payloads(jobs, names=None):
    """THE PRE-CALL FULL-PAYLOAD LEAKAGE SCAN over every (match, order) payload about to be posted. For each job the two user turns
    must decompose exactly into the template's literal fragments and three slots (question + reference, trace A, trace B) with the
    two traces swapped between the orders; the frame (fragments + question slot) must be identical in the two orders, so nothing
    per-side sits outside the traces; no contestant name and no key-side token may be in the frame; the body carries no temperature.
    A contestant name INSIDE a trace slot is the model's own output (the slot is proved to be source bytes) and is counted, not refused."""
    f0, f1, f2, f3 = _fragments()
    names = names if names is not None else sorted({m["model_a"] for m, *_ in jobs} | {m["model_b"] for m, *_ in jobs})
    c = Counter()
    for m, ref, system, u1, u2 in jobs:
        frames = []
        traces = []
        for order, u in ((1, u1), (2, u2)):
            if not (u.startswith(f0) and u.endswith(f3)):
                raise SystemExit("[SCAN] match %d order %d: the user turn does not open / close with the template" % (m["match_id"], order))
            mid_ = u[len(f0):len(u) - len(f3)]
            # the question slot ends at the FIRST f1 that is followed by a trace; the reference block precedes it
            qi = mid_.find(f1)
            q = mid_[:qi]
            rest = mid_[qi + len(f1):]
            bi = rest.rfind(f2)
            ta, tb = rest[:bi], rest[bi + len(f2):]
            if f0 + q + f1 + ta + f2 + tb + f3 != u:
                raise SystemExit("[SCAN] match %d order %d: the user turn does not decompose into the template and three slots" % (m["match_id"], order))
            frames.append((q,))
            traces.append((ta, tb))
            c["decomposed"] += 1
            body = payload_body(system, u)
            if tuple(body) != ("model", "max_tokens", "messages") + (("temperature",) if TEMPERATURE is not None else ()) \
                    or body["model"] != JUDGE or body["max_tokens"] != MAXTOK:
                raise SystemExit("[SCAN] match %d order %d: the body is not the protocol's" % (m["match_id"], order))
            c["payloads"] += 1
        if frames[0] != frames[1] or traces[0] != (traces[1][1], traces[1][0]):
            raise SystemExit("[SCAN] match %d: the frame differs between the orders, or the traces are not swapped; a per-side element "
                             "sits outside the trace slots" % m["match_id"])
        c["frame_same"] += 2
        template_txt, qslot = f0 + f1 + f2 + f3, frames[0][0]
        for nm in names:
            if nm in template_txt or nm in qslot or nm in system:
                raise SystemExit("[SCAN] match %d: the contestant name %r is outside the trace slots" % (m["match_id"], nm))
            c["name_in_trace"] += sum(nm in t for t in traces[0])
        for tok in FRAME_TOKENS:                          # the template is constant: a hit there is a code change and refuses;
            if tok in template_txt.lower():               # in the question + reference slot it is dataset / reference text: counted
                raise SystemExit("[SCAN] the key-side token %r is in the user template" % tok)
            c["token_in_question"] += int(tok in qslot.lower())
        c["frame_clean"] += 2
    return c


def git_tracked_clean(path):
    import subprocess
    try:
        t = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        return t, c
    except Exception:
        return False, False


def parse_ready_epoch2(text, sha):
    import re
    body, fence = [], None
    for ln in text.split("\n"):
        st = ln.lstrip()
        if fence is None and (st.startswith("```") or st.startswith("~~~")):
            fence = st[:3]; body.append("")
        elif fence is not None:
            if st.startswith(fence): fence = None
            body.append("")
        else:
            body.append(ln)
    text = "\n".join(body)
    lines = list(re.finditer(r"^[ \t]*#{0,6}[ \t]*\**[ \t]*(NOT READY|READY-WITH-CONDITIONS|READY)\b[ \t]*\**[ \t]*:", text, re.M))
    if not lines:
        return None, ["no verdict line"]
    first = text[lines[0].start():].split("\n", 1)[0]
    reasons = []
    if any(x.group(1) == "NOT READY" for x in lines): reasons.append("a NOT READY verdict")
    if TEST_EPOCH2 not in first: reasons.append("the verdict line does not name %s" % TEST_EPOCH2)
    if sha not in first: reasons.append("the verdict line does not name this script's LF sha16 %s" % sha)
    return lines[0].group(1), reasons


def gate_state_epoch2(go):
    exists = os.path.exists(READY_EPOCH2)
    tracked, clean = git_tracked_clean(READY_EPOCH2) if exists else (False, False)
    verdict, reasons = parse_ready_epoch2(open(READY_EPOCH2, encoding="utf-8").read(), script_hash_lf()) if exists else (None, ["READY missing"])
    ok = bool(go and exists and tracked and clean and not reasons)
    return ok, "--go %s | %s %s (tracked %s, clean %s) | verdict %r%s" % (bool(go), rel(READY_EPOCH2), "exists" if exists else "MISSING",
                                                                           tracked, clean, verdict, "" if not reasons else " | REFUSES: " + "; ".join(reasons))


def go_gate_epoch2(what, go):
    ok, s = gate_state_epoch2(go)
    print("[GATE] %s: %s -> %s" % (what, s, "OPEN" if ok else "REFUSED"), flush=True)
    if not ok:
        raise SystemExit("[GATE] %s REFUSED (0 calls, no database opened): %s" % (what, s))


def acct_caches():
    c = atl.default_caches(ROOT)
    c["CANARY-EPOCH2-RUNG"] = [cache_path(k) for k in EPOCH2_PASSES]
    c["TRACE-TRUNCATION"] = list(TRACE_CACHES)
    return c


def budget_gate_epoch2(planned, what, refuse=True):
    """b0b5d0d: (i) own ceiling 1,200, (ii) the 4,000-match rule, (iii) 4,060 + both accepted tests + this launch <= 14,000;
    printed on both branches, REFUSED (never trimmed) on any breach."""
    return atl.guard(TEST_EPOCH2, planned, acct_caches(), LEDGER_DIR, what, refuse=refuse)


def ledger_append_epoch2(calls, what):
    atl.append(TEST_EPOCH2, what, calls, LEDGER_DIR)


def _rows_of(n):
    """{match_id: row dict} of pass n (read-only), with the ts and the fingerprints; None when the cache is absent."""
    p = cache_path(n)
    if not os.path.exists(p): return None
    con = sqlite3.connect("file:%s?mode=ro" % os.path.abspath(p).replace("\\", "/"), uri=True)
    cols = [r[1] for r in con.execute("PRAGMA table_info(verdicts)")]
    want = ["match_id", "qid", "winner", "invalid", "finish1", "finish2", "stratum", "ts", "vote1", "vote2_raw"] + \
           [c for c in ("provider1", "provider2") if c in cols]
    out = {}
    for r in con.execute("SELECT %s FROM verdicts" % ", ".join(want)):
        d = dict(zip(want, r)); out[d["match_id"]] = d
    meta = dict(con.execute("SELECT key, value FROM run_meta"))
    con.close()
    return out, meta


def _bad(r):
    return bool(r["invalid"] or r["finish1"] in ("length", "content_filter") or r["finish2"] in ("length", "content_filter"))


def disagree_A(ra, rb):
    """Convention A (DECIDES): an unusable row in either pass is a disagreement; else the combined winners differ."""
    return 1 if (_bad(ra) or _bad(rb)) else int(ra["winner"] != rb["winner"])


def verify_set(ms, meta):
    """D4: the checks freeze_set makes with `assert` (gone under -O), made with explicit SystemExit. freeze_set is NOT edited (it is
    payload-path code, AST-identical to the pass-2 script of record)."""
    got = set_hash(ms)
    probs = []
    if got != SET_HASH_OF_RECORD or meta.get("set_hash") != SET_HASH_OF_RECORD:
        probs.append("the set hashes to %s (file says %s), not the hash of record %s" % (got, meta.get("set_hash"), SET_HASH_OF_RECORD))
    if len(ms) != N_SET:
        probs.append("the set holds %d matches, not %d" % (len(ms), N_SET))
    if meta.get("pool_id") != POOL:
        probs.append("the set's pool is %r, not %s" % (meta.get("pool_id"), POOL))
    if ({m["model_a"] for m in ms} | {m["model_b"] for m in ms}) & EXCLUDED:
        probs.append("an excluded model is in the set")
    pool = pool_qids()
    out = [m["match_id"] for m in ms if m["qid"] not in pool]
    if out:
        probs.append("%d matches lie outside the pool of record" % len(out))
    if probs:
        raise SystemExit("[SET] REFUSED: " + "; ".join(probs))
    return got


def pass4_start(now):
    """D2: the rung's START. If a pass-4 cache already exists, its persisted run_meta 'started' (pinned at the first pass-4 launch);
    otherwise now (this launch IS the start). Returns (epoch seconds, label)."""
    p = cache_path(4)
    st = None
    if os.path.exists(p):
        con = sqlite3.connect("file:%s?mode=ro" % os.path.abspath(p).replace("\\", "/"), uri=True)
        try: st = dict(con.execute("SELECT key, value FROM run_meta")).get("started")
        except sqlite3.Error: st = None
        finally: con.close()
    if st:
        return time.mktime(time.strptime(st, "%Y-%m-%d %H:%M:%S")), "pass 4's persisted start %s (run_meta 'started')" % st
    return now, "now (the first pass-4 launch)"


def preflight_epoch2(meta, npass, now=None):
    """Read-only. Pass 3: passes 1 and 2 complete under the same protocol and the 1 -> 2 floor 26/300 reproduced (convention A).
    Pass 4: pass 3 complete, every pass-3 call fingerprinted, and NOW within RUNG_WINDOW_S of pass 3's last row."""
    probs = preflight_pass2(meta)                         # pass 1 complete, same protocol / max_tokens / temperature / set
    got = {k: _rows_of(k) for k in (1, 2, 3)}
    if got[2] is None:
        probs.append("pass 2 cache %s is missing" % rel(cache_path(2)))
    else:
        r2, m2 = got[2]
        if len(r2) != N_SET: probs.append("pass 2 holds %d of %d verdicts" % (len(r2), N_SET))
        for k, v in current_meta(meta).items():
            if k != "pass_no" and m2.get(k) != v: probs.append("%s: pass 2 recorded %r | now %r" % (k, m2.get(k), v))
        if got[1] is not None:
            r1 = got[1][0]
            d12 = sum(disagree_A(r1[k], r2[k]) for k in r1 if k in r2)
            if d12 != FLOOR12_OF_RECORD or len(r1) != N_SET:
                probs.append("the pass 1 -> 2 floor reproduces as %d/%d, not the recorded %d/%d (C0)" % (d12, len(r1), FLOOR12_OF_RECORD, N_SET))
    if npass == 4:
        if got[3] is None:
            probs.append("pass 3 cache %s is missing: the rung follows a COMPLETE pass 3" % rel(cache_path(3)))
        else:
            r3, m3 = got[3]
            if len(r3) != N_SET: probs.append("pass 3 holds %d of %d verdicts" % (len(r3), N_SET))
            fp = Counter(r.get(c) for r in r3.values() for c in ("provider1", "provider2"))
            if set(fp) - {EXPECTED_FINGERPRINT, REFUSAL_FINGERPRINT}:
                probs.append("pass 3 fingerprints %s: trigger (1), every readout UNDETERMINED BY VALIDITY" % dict(fp))
            last3 = max((r["ts"] for r in r3.values()), default=None)
            if last3 is not None and now is not None:
                t0, how = pass4_start(now)
                gap = t0 - last3
                print("[RUNG] pass 3's last row %s | pass 4 start = %s | gap %.0f s against the %d s window -> %s"
                      % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last3)), how,
                         gap, RUNG_WINDOW_S, "WITHIN" if gap <= RUNG_WINDOW_S else "OUTSIDE"), flush=True)
                if gap > RUNG_WINDOW_S:
                    probs.append("pass 4 would start %.0f s after pass 3's last row (> %d s): the rung would be UNDETERMINED BY VALIDITY "
                                 "(not within-session); nothing is posted" % (gap, RUNG_WINDOW_S))
    return probs


# ── dry run ─────────────────────────────────────────────────────────────────────

def dry_run(pilot):
    if NPASS in EPOCH3_PASSES:                            # [2026-10-01] G17-CANARY v1 leg: pass 5 has its own dry run
        return dry_run_epoch3(pilot)
    epoch2 = NPASS in EPOCH2_PASSES
    if epoch2:                                            # CANARY-EPOCH2-RUNG: no file is writable in a dry run; the pins first
        install_db_guard(writable=None)
        pin_old_caches("dry-run --pass %d" % NPASS)
    matches, meta = freeze_set()
    if epoch2: verify_set(matches, meta)
    all_ms = matches
    if pilot: matches = matches[:pilot]
    configure_rr()                                        # what run() posts through; no env read, no cache opened
    src = open(rr.__file__, encoding="utf-8").read()      # the local payload_body copy must track rejudge_reasoning.py lines 92-96
    assert '"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src, \
        "rejudge_reasoning.call_judge_full's body changed; update payload_body()"
    jobs = build_jobs(matches)
    payloads = []
    for m, ref, system, u1, u2 in jobs:
        for u in (u1, u2):
            body = payload_body(system, u)
            assert tuple(body) == ("model", "max_tokens", "messages") + (("temperature",) if TEMPERATURE is not None else ()), tuple(body)
            assert body["model"] == JUDGE and body["max_tokens"] == MAXTOK, (body["model"], body["max_tokens"])
            assert body.get("temperature") == TEMPERATURE, body.get("temperature")   # None = omitted (D2)
            payloads.append(body)
    print("[DRY-RUN] pass %d | matches %d (%s) | calls %d (dual order) | cap %d calls per pass, %s for both passes"
          % (NPASS, len(matches), ", ".join("%s %d" % (s, n) for s, n in sorted(Counter(m["stratum"] for m in matches).items())), len(payloads), 2 * N_SET, "{:,}".format(4 * N_SET)))
    print("[DRY-RUN] protocol: %s" % protocol())
    print("[DRY-RUN] judge %s | max_tokens %d | temperature %s (Amendment 1 D2) | key: rr.load_env (AZURE_GROK_API_KEY, else AZURE_AI_API_KEY), no override"
          % (JUDGE, MAXTOK, temp_label()))
    print("[DRY-RUN] cache: %s (exists: %s) | set: %s (hash %s = hash of record %s)"
          % (rel(cache_path()), os.path.exists(cache_path()), rel(SET_JSON), meta["set_hash"], SET_HASH_OF_RECORD))
    print("[DRY-RUN] pass 2 allowed from %s | script sha256[:16] %s" % (NOT_BEFORE_PASS2, script_hash()))
    if NPASS == 2:
        probs = preflight_pass2(meta)
        print("[DRY-RUN] pass-2 pre-flight (read-only): %s" % ("would GO" if not probs else "would REFUSE: " + "; ".join(probs)))
    if epoch2:
        assert_body_source()
        probs = preflight_epoch2(meta, NPASS, now=time.time())
        print("[DRY-RUN] pass-%d pre-flight (read-only; C0: the 1 -> 2 floor %d/%d reproduced%s): %s"
              % (NPASS, FLOOR12_OF_RECORD, N_SET, "; pass 3 complete and the 2 h rung window" if NPASS == 4 else "",
                 "would GO" if not probs else "would REFUSE: " + "; ".join(probs)))
        scan = scan_payloads(jobs)
        print("[SCAN] pre-call full-payload scan over %d payloads: decomposition %d | frame identical across orders %d | frame clean %d | "
              "reported, not refused: contestant names inside trace slots %d, key-side tokens in the question + reference slot %d -> PASS"
              % (scan["payloads"], scan["decomposed"], scan["frame_same"], scan["frame_clean"], scan["name_in_trace"], scan["token_in_question"]))
        anchor = hashlib.sha256()
        for m, ref, system, u1, u2 in jobs:
            anchor.update(("%d|" % m["match_id"]).encode("utf-8") + system.encode("utf-8") + u1.encode("utf-8") + u2.encode("utf-8"))
        print("[ANCHOR] payload anchor sha16 %s over %d matches (match id | system | user order 1 | user order 2, the set's order) | "
              "first payload sha16 %s | system prompts %d distinct | posting order sha16 %s (the set's order = pass 2's; first ids %s)"
              % (anchor.hexdigest()[:16], len(jobs), _sha16(jobs[0][3]), len({j[2] for j in jobs}),
                 order_sha([m["match_id"] for m in matches]), [m["match_id"] for m in matches[:3]]))
        print("[CEILING] this pass: %d matches x 2 orders = %d calls (pilot %d matches = %d calls INSIDE it) | %s ceiling %d (passes 3 + 4)"
              % (len(all_ms), 2 * len(all_ms), PILOT_N, 2 * PILOT_N, TEST_EPOCH2, EPOCH2_CEILING))
        budget_gate_epoch2(2 * len(all_ms), "--dry-run --pass %d (a full pass, 0 posted)" % NPASS, refuse=False)
        ok, gs = gate_state_epoch2(False)
        print("[GATE] (a dry run is never gated; a posting launch needs --go and the committed READY) %s" % gs)
    m0 = jobs[0][0]
    print("[DRY-RUN] first payload: match %d | qid %d | %s vs %s | anchor %s | %s/%s | order 1 | model field %r | max_tokens %d | keys %s"
          % (m0["match_id"], m0["qid"], m0["model_a"], m0["model_b"], m0["anchor"], m0["stratum"], m0["pair_kind"],
             payloads[0]["model"], payloads[0]["max_tokens"], list(payloads[0])))
    print("----- SYSTEM -----"); print(payloads[0]["messages"][0]["content"])
    print("----- USER -----"); print(payloads[0]["messages"][1]["content"])
    print("----- END -----")
    print("[DRY-RUN] first payload model field: %s" % payloads[0]["model"])
    print("[DRY-RUN] %d payloads assembled, 0 posted" % len(payloads))
    if epoch2:
        pin_old_caches("end of dry-run --pass %d" % NPASS)
        print(dbguard_line())
    return 0


# ── judge ───────────────────────────────────────────────────────────────────────

def run(pilot, workers, override_guard=False, go=False, full=False, budget=None):
    """CANARY-EPOCH2-RUNG: posts pass 3 or pass 4 only (passes 1 and 2 are closed). Order of refusals: the pass, the mode, the
    gate (before any database), the DB guard, the old caches' pins, the pre-flight, the payload scan, the pilot rule, the guard,
    the budget; then the posting, counted, with the night-ledger append in a `finally`; then the pins again."""
    if NPASS in EPOCH3_PASSES:                            # [2026-10-01] G17-CANARY v1 leg: pass 5 (budget is read only there)
        return run_epoch3(pilot, workers, override_guard, go=go, full=full, budget=budget)
    if NPASS not in EPOCH2_PASSES:
        raise SystemExit("[PASS] --pass %d REFUSED: passes 1 and 2 are complete caches of record; epoch 2 posts pass 3 and the rung "
                         "pass 4 only (CANARY-EPOCH2-RUNG)." % NPASS)
    if not pilot and not full:
        raise SystemExit("[MODE] a posting launch needs --pilot N or --run (and --go)")
    if pilot and pilot != PILOT_N:
        raise SystemExit("[MODE] --pilot %d REFUSED: the registered pilot is %d matches" % (pilot, PILOT_N))
    if override_guard:
        raise SystemExit("[MODE] --override-guard is REFUSED on passes 3 / 4 (READY D7): a pilot above the guard stops the epoch")
    if os.path.exists(OUT_EPOCH2):
        raise SystemExit("[RECORD] %s exists: the epoch-2 outcome of record is written and closed; nothing more is posted." % rel(OUT_EPOCH2))
    what = "--pass %d %s" % (NPASS, "--pilot %d" % pilot if pilot else "--run")
    go_gate_epoch2(what, go)                              # fail-closed BEFORE any database is opened
    install_db_guard(writable=cache_path(NPASS))
    pins_before = pin_old_caches("before " + what)
    matches, meta = freeze_set()                          # refuses when canary_set.json is missing; never re-freezes here
    verify_set(matches, meta)                             # D4: explicit, -O-proof
    probs = preflight_epoch2(meta, NPASS, now=time.time())
    if probs:
        raise SystemExit("[PASS-%d PRE-FLIGHT] REFUSED before any call:\n  %s" % (NPASS, "\n  ".join(probs)))
    print("[PASS-%d PRE-FLIGHT] read-only: go" % NPASS, flush=True)
    configure_rr(); assert_body_source(); rr.load_env()   # the key rr.load_env selects; no other override (Amendment 1 D1)
    all_ms = matches
    if pilot: matches = matches[:pilot]
    con = open_cache(); pin_meta(con, meta)               # refuses a relaunch under a different record
    try:
        done = {r[0] for r in con.execute("SELECT match_id FROM verdicts")}
        if full:
            miss = [m["match_id"] for m in all_ms[:PILOT_N] if m["match_id"] not in done]
            if miss:
                raise SystemExit("[RUN] REFUSED: the pass-%d pilot (the first %d matches of the set) is not cached (%d missing): run "
                                 "--pass %d --pilot %d first and read its guard." % (NPASS, PILOT_N, len(miss), NPASS, PILOT_N))
        todo = [m for m in matches if m["match_id"] not in done]
        if done:                                              # the pilot gate: the cached rows decide whether more is posted
            n, bad = cached_guard(con); rate = bad / n
            print("[GUARD] cached %d | invalid or non-terminated %d (%.1f%%) -> %s" % (n, bad, 100 * rate, "OK" if rate <= GUARD_RATE else "ABOVE 5%"), flush=True)
            if rate > GUARD_RATE and todo:
                if not override_guard:
                    raise SystemExit("[GUARD] refusing to post the remaining %d matches: %d of %d cached matches are invalid or non-terminated (%.1f%% > 5%%)."
                                     % (len(todo), bad, n, 100 * rate))
                con.execute("INSERT OR REPLACE INTO run_meta VALUES ('guard_override', ?)",
                            ("%s: %d of %d cached invalid/non-terminated, posted anyway" % (time.strftime("%Y-%m-%d %H:%M:%S"), bad, n),)); con.commit()
                print("[GUARD] --override-guard: posting anyway; recorded in run_meta", flush=True)
        jobs = build_jobs(todo)
        scan = scan_payloads(jobs)                            # the pre-call full-payload leakage scan; SystemExit on any failure
        print("[SCAN] pre-call full-payload scan over %d payloads: decomposition %d | frame identical across orders %d | frame clean %d | "
              "reported, not refused: contestant names inside trace slots %d, key-side tokens in the question + reference slot %d -> PASS"
              % (scan["payloads"], scan["decomposed"], scan["frame_same"], scan["frame_clean"], scan["name_in_trace"], scan["token_in_question"]), flush=True)
        budget_gate_epoch2(2 * len(jobs), what)
        print("CANARY-EPOCH2-RUNG pass %d [%s]: set %d | cached %d | to judge %d (%d calls) | workers %d | maxtok %d | temperature %s | "
              "posting order = the set's order (pass 2's), sha16 %s"
              % (NPASS, JUDGE, len(all_ms), len(matches) - len(todo), len(todo), 2 * len(todo), workers, MAXTOK, temp_label(),
                 order_sha([m["match_id"] for m in matches])), flush=True)
        lock = threading.Lock(); ok = err = 0; finishes = Counter(); halt = threading.Event(); mismatch = []
        index = {m["match_id"]: i for i, m in enumerate(all_ms)}
        posted = []
        real_post = rr.call_judge_full

        def counted(*a, **k):
            posted.append(1)
            return real_post(*a, **k)

        def one(job):
            m, ref, system, u1, u2 = job
            if halt.is_set(): raise FingerprintMismatch("match %d: not posted, the run is stopping on a fingerprint mismatch" % m["match_id"])
            raw1, p1, k1, _, f1, msg1 = rr.call_judge_full(system, u1)
            try: check_fingerprint(m, 1, p1, f1)              # fail-closed: a foreign deployment stops the run; this match is never cached
            except FingerprintMismatch as e: mismatch.append(str(e)); halt.set(); raise
            if halt.is_set(): raise FingerprintMismatch("match %d: order 2 not posted, the run is stopping on a fingerprint mismatch" % m["match_id"])
            raw2, p2, k2, _, f2, msg2 = rr.call_judge_full(system, u2)
            try: check_fingerprint(m, 2, p2, f2)
            except FingerprintMismatch as e: mismatch.append(str(e)); halt.set(); raise
            raw1, raw2 = rr.strip_think(raw1 or ""), rr.strip_think(raw2 or "")
            v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
            if f1 in ("length", "content_filter"): v1 = "INVALID"   # NON_TERMINATED / a refusal is never a verdict and never a tie
            if f2 in ("length", "content_filter"): v2 = "INVALID"
            w, flip, inv = rj.combine_orders(v1, v2)
            return (m["match_id"], m["model_a"], m["model_b"], m["node_id"], m["qid"], m["anchor"], ref[0], int(ref[2]), v1, v2, c1, c2,
                    {"Model A": m["model_a"], "Model B": m["model_b"]}.get(w, w), int(flip), int(inv), raw1, raw2, time.time(),
                    f1, f2, k1, k2, m["stratum"], m["pair_kind"], p1, p2,
                    (msg1 or {}).get("_response_id"), (msg2 or {}).get("_response_id"), _sha16(system), _sha16(u1), _sha16(u2), u1, u2,
                    index[m["match_id"]], script_hash_lf())
        rr.call_judge_full = counted
        try:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futs = {ex.submit(one, j): j for j in jobs}
                for i, f in enumerate(as_completed(futs), 1):
                    try: row = f.result()
                    except FingerprintMismatch as e:
                        halt.set(); ex.shutdown(wait=False, cancel_futures=True)   # in-flight workers see halt before their next post
                        raise SystemExit("[FINGERPRINT] %s\n  the run STOPS: nothing cached for this match, the remaining matches are not posted "
                                         "(cached so far: ok %d, errors %d). The deployed judge of record is %s; a different deployment is a "
                                         "different judge and never enters this cache." % (mismatch[0] if mismatch else e, ok, err, JUDGE))
                    except Exception as e:
                        err += 1; print("  ERROR match %s: %s" % (futs[f][0]["match_id"], str(e)[:120]), flush=True); continue
                    with lock:
                        con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 35), row); con.commit()
                    ok += 1; finishes[row[18]] += 1; finishes[row[19]] += 1
                    if i % 25 == 0 or i == len(jobs):
                        print("  %d/%d (ok %d, err %d) | finish_reason %s" % (i, len(jobs), ok, err, dict(finishes)), flush=True)
        finally:
            rr.call_judge_full = real_post
            ledger_append_epoch2(len(posted), what)
            print("done: ok %d, errors %d | %d calls posted (errors are posted calls, counted, never cached)%s"
                  % (ok, err, len(posted), " (errored matches are not cached; relaunch to resume them)" if err else ""), flush=True)
        truncation_report(con)
        pins_after = pin_old_caches("after " + what)
        if pins_after != pins_before:
            raise SystemExit("[PIN] a cache of record CHANGED during %s: %r -> %r" % (what, pins_before, pins_after))
        if pilot:
            n, bad = cached_guard(con)
            n += err; bad += err                          # D6: this launch's errored (uncached) matches count as unusable
            if bad > GUARD_RATE * max(1, n):
                raise SystemExit("[GUARD] the pass-%d pilot FAILED its truncation guard (%d of %d unusable > 5%%): --run is refused" % (NPASS, bad, n))
    finally:
        con.close()                                       # a refusal or a stop never leaves the new cache open
    return 0


def truncation_report(con):
    """The pilot's guard, printed at the end of every launch; the next launch enforces it (run() refuses above 5%)."""
    n, bad = cached_guard(con)
    inv = con.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=1").fetchone()[0]
    fr = dict(con.execute("SELECT COALESCE(f,'(none)'), COUNT(*) FROM (SELECT finish1 f FROM verdicts UNION ALL SELECT finish2 FROM verdicts) GROUP BY 1"))
    print("[GUARD] pass %d: %d judged | %d invalid, %d invalid or non-terminated (%.1f%%) | finish_reason over %d calls: %s | fingerprint: %s -> %s"
          % (NPASS, n, inv, bad, 100.0 * bad / max(1, n), 2 * n, fr, fingerprint_label(fingerprint_counts(con)),
             "OK" if bad <= GUARD_RATE * max(1, n) else "ABOVE 5%: the next launch REFUSES to post more and the verdict will be REFUSED"))


# ── analysis ────────────────────────────────────────────────────────────────────

def load_pass(n):
    if not os.path.exists(cache_path(n)): return None, {}
    con = sqlite3.connect("file:%s?mode=ro" % cache_path(n), uri=True)
    rows = {r[0]: dict(mid=r[0], a=r[1], b=r[2], q=r[3], w=r[4], flip=r[5], inv=r[6], v1=r[7], v2=r[8], f1=r[9], f2=r[10], s=r[11], k=r[12])
            for r in con.execute("SELECT match_id, model_a, model_b, qid, winner, flip, invalid, vote1, vote2_raw, finish1, finish2, stratum, pair_kind FROM verdicts")}
    mm = dict(con.execute("SELECT key, value FROM run_meta"))
    mm["_fingerprints"] = fingerprint_label(fingerprint_counts(con))   # read from the cache columns, not run_meta; pass 1 reads "not recorded (pre-rule)"
    return rows, mm


def clustered(vals_by_q, stat, B=2000, seed=SEED):
    """Question-clustered bootstrap of stat(list of per-match values): resample questions with replacement."""
    qs = sorted(vals_by_q); rng = random.Random(seed); out = []
    for _ in range(B):
        bs = [v for _ in qs for v in vals_by_q[qs[rng.randrange(len(qs))]]]
        out.append(stat(bs))
    out.sort()
    mean = sum(out) / B; sd = (sum((x - mean) ** 2 for x in out) / (B - 1)) ** 0.5
    return out[int(0.025 * B)], out[int(0.975 * B) - 1], sd


def analyze(pilot=None):
    matches, meta = freeze_set()
    p1, m1 = load_pass(1); p2, m2 = load_pass(2)
    if not p1:
        print("=== CANARY-BASELINE: pass 1 not judged yet (%s) ===" % ("no cache" if p1 is None else "cache holds no verdicts")); return
    # pilot or incomplete outcomes never overwrite the outcome of record (Amendment 1, every script)
    partial = bool(pilot) or any(len(p) != len(matches) for p in (p1, p2) if p)
    out_path = OUT_PARTIAL if partial else OUT
    L = ["=== CANARY-BASELINE: the frozen 300-match canary set (hash %s) judged under STACK-v2 / %s, dual order ===" % (meta["set_hash"], JUDGE),
         "  pool %s | set %s | script sha256[:16] %s | pass 1 cache %s | pass 2 cache %s"
         % (POOL, rel(SET_JSON), script_hash(), os.path.basename(cache_path(1)), os.path.basename(cache_path(2)) if p2 else "(not run)"),
         "  temperature of record: omitted (provider default; plan Amendment 1 D2) | max_tokens of record: %d | judge of record: %s (deployed, D1)" % (DEFAULT_MAXTOK, JUDGE)]
    if partial:
        L.append("  PARTIAL%s: written to %s, never the outcome of record" % (" (pilot %d)" % pilot if pilot else " (incomplete cache)", rel(out_path)))

    def write():
        """The outcome of record is opened in mode "w", so a readout that does not carry everything of record must never
        touch it (post-run review 2026-09-22 defect 2; READY ad65d09 defect 2). Five early returns - PROTOCOL GUARD, the
        refused >5% guard, pass 2 not judged, no paired valid matches, and an empty deciding subset - produce a readout with
        no "ALARM STATE:" line; those are DIVERTED to the partial file, loudly, and the outcome of record is left untouched.
        The complete readout always carries the line, so the happy path is unaffected."""
        nonlocal out_path
        txt = "\n".join(L)
        if out_path == OUT and not any(l.startswith("ALARM STATE:") for l in L):
            print("[WRITE-GUARD] REFUSING to write %s: this readout carries no 'ALARM STATE:' line (degraded or incomplete state), and "
                  "mode \"w\" would erase the machine-readable state line and the two verbatim brackets of 4178a7c. Diverted to %s; the "
                  "outcome of record is untouched." % (rel(OUT), rel(OUT_PARTIAL)), flush=True)
            L.append("  [WRITE-GUARD] no ALARM STATE line in this readout (degraded or incomplete state): written to %s, the outcome of "
                     "record %s was NOT overwritten." % (rel(OUT_PARTIAL), rel(OUT)))
            txt = "\n".join(L); out_path = OUT_PARTIAL
        print(txt)
        if out_path == OUT:                               # post-run review 2026-09-22 D2 (CANARY-EPOCH2-RUNG build): WRITE-ONCE, mode "x"
            try:
                with open(OUT, "x", encoding="utf-8") as f: f.write(txt + "\n")
            except FileExistsError:
                print("[WRITE-ONCE] %s exists and is an outcome of record: NOTHING was written (the readout above is printed only). "
                      "--analyze never opens it in mode \"w\" (post-run review 2026-09-22 D2)." % rel(OUT), flush=True)
            return
        open(out_path, "w", encoding="utf-8").write(txt + "\n")   # the partial / pilot file: not of record
    for n, (p, mm) in ((1, (p1, m1)), (2, (p2, m2))):
        if p is None: continue
        L.append("  pass %d: %d of %d judged | protocol of record: %s | max_tokens %s | temperature %s | started %s | resumed %s | script sha %s%s%s"
                 % (n, len(p), len(matches), mm.get("protocol", "?")[:64] + "...", mm.get("max_tokens"), mm.get("temperature"), mm.get("started"),
                    len(json.loads(mm.get("resumed") or "[]")), mm.get("script_sha256_16"),
                    " (relaunched under %s)" % mm["script_sha256_16_relaunch"] if mm.get("script_sha256_16_relaunch") else "",
                    " | GUARD OVERRIDDEN: %s" % mm["guard_override"] if mm.get("guard_override") else ""))
        L.append("  pass %d deployment fingerprint over %d calls (expected %s): %s" % (n, 2 * len(p), EXPECTED_FINGERPRINT, mm.get("_fingerprints", FINGERPRINT_NOT_RECORDED)))
    if p2 and any(m1.get(k) != m2.get(k) for k in ("protocol", "max_tokens", "temperature", "set_hash", "judge")):
        L.append("  PROTOCOL GUARD: the two passes were not posted under the same (protocol, judge, max_tokens, temperature, set); they are NOT comparable.")
        write(); return

    # ---- refusing guard: > 5% unparsed / non-terminated on the deciding subset; an empty subset is refused, not OK ----
    def bad_row(r):
        """A row that carries no committed verdict: INVALID (either order unparsed) or non-terminated (finish_reason=length)."""
        return bool(r["inv"] or r["f1"] == "length" or r["f2"] == "length")

    def unparsed(rows):
        return sum(1 for r in rows if bad_row(r))
    deciding = {"pass 1": list(p1.values())}
    if p2:
        deciding["pass 2"] = list(p2.values())
        deciding["paired (both passes)"] = [p1[k] for k in p1 if k in p2] + [p2[k] for k in p1 if k in p2]
    refused = False
    for tag, rows in deciding.items():
        if not rows:
            L.append("  GUARD %-22s EMPTY deciding subset -> REFUSED" % tag); refused = True; continue
        u = unparsed(rows); rate = u / len(rows)
        L.append("  GUARD %-22s %d of %d verdicts unparsed or non-terminated (%.1f%%) -> %s" % (tag, u, len(rows), 100 * rate, "OK" if rate <= GUARD_RATE else "ABOVE 5%"))
        refused |= rate > GUARD_RATE
    if refused:
        L.append("  VERDICT REFUSED: more than 5%% of a deciding subset is unparsed or non-terminated, or a deciding subset is empty. finish_reason counts: %s"
                 % dict(Counter(f for rows in deciding.values() for r in rows for f in (r["f1"], r["f2"]))))
        L.append("  Re-run with a larger --maxtok in a new cache, or record non-termination as a property of the judge; no floor is read.")
        write(); return

    # ---- pass-level descriptives (each pass on its own) ----
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    for n, p in ((1, p1), (2, p2)):
        if not p: continue
        L.append(""); L.append("  PASS %d descriptives (valid verdicts only):" % n)
        for s in ("contested", "cross", "all"):
            rows = [r for r in p.values() if not r["inv"] and (s == "all" or r["s"] == s)]
            if not rows: continue
            ties = sum(r["w"] == "TIE" for r in rows) / len(rows); flips = sum(r["flip"] for r in rows) / len(rows)
            dec = [(r, r["a"] if G[(r["q"], r["a"])] else r["b"]) for r in rows if G.get((r["q"], r["a"])) is not None and G.get((r["q"], r["b"])) is not None and G[(r["q"], r["a"])] != G[(r["q"], r["b"])]]
            acc_tw = sum(r["w"] == d for r, d in dec) / max(1, len(dec)); acc_th = sum(1.0 if r["w"] == d else (0.5 if r["w"] == "TIE" else 0.0) for r, d in dec) / max(1, len(dec))
            L.append("    %-9s n=%3d | tie %.3f | flip %.3f | key-decidable n=%3d: accuracy ties-wrong %.3f, ties-half %.3f"
                     % (s, len(rows), ties, flips, len(dec), acc_tw, acc_th))

    # ---- the floor: pass 1 vs pass 2 on the same match ----
    L.append("")
    if not p2:
        L.append("  FLOOR: pass 2 not judged yet (allowed from %s). The floor and its interval are read when both passes exist." % NOT_BEFORE_PASS2)
        L.append("  Prediction on record: floor 4-6% on the contested half, lower on the cross-tier half (DECOMP 0.057 on contested frontier matches under grok).")
        write(); return
    paired = [(p1[k], p2[k]) for k in sorted(p1) if k in p2 and not p1[k]["inv"] and not p2[k]["inv"]]
    L.append("  FLOOR = share of paired matches whose dual-order verdict (TIE on flip) differs between the passes; 95% interval and SE from a")
    L.append("  question-clustered bootstrap (%d draws, seed %d); DEFF = clustered variance / binomial variance." % (2000, SEED))
    res = {}
    for s in ("contested", "cross", "all"):
        sub = [(r1, r2) for r1, r2 in paired if s == "all" or r1["s"] == s]
        if not sub: continue
        byq = defaultdict(list)
        for r1, r2 in sub: byq[r1["q"]].append(int(r1["w"] != r2["w"]))
        f = sum(v for vs in byq.values() for v in vs) / len(sub)
        lo, hi, sd = clustered(byq, lambda xs: sum(xs) / len(xs))
        bino = (f * (1 - f) / len(sub)) ** 0.5; deff = (sd / bino) ** 2 if bino > 0 else float("nan")
        dec2 = [(r1, r2) for r1, r2 in sub if r1["w"] != "TIE" and r2["w"] != "TIE"]
        dis_dec = sum(r1["w"] != r2["w"] for r1, r2 in dec2) / max(1, len(dec2))
        raw = sum(int(r1["v1"] != r2["v1"]) + int(r1["v2"] != r2["v2"]) for r1, r2 in sub) / (2 * len(sub))
        res[s] = dict(n=len(sub), q=len(byq), floor=f, lo=lo, hi=hi, sd=sd, deff=deff)
        L.append("    %-9s n=%3d matches on %3d questions | floor %.3f  95%% CI [%.3f, %.3f]  SE %.4f  DEFF %.2f | agreement %.3f | decisive-only disagreement %.3f (n=%d) | per-order raw vote disagreement %.3f"
                 % (s, len(sub), len(byq), f, lo, hi, sd, deff, 1 - f, dis_dec, len(dec2), raw))
    # ---- convention A beside convention B (rule (iv), pre-run bracket 96bd3d7): INVALID or non-terminated in EITHER pass counts as a
    #      disagreement and the pair is kept, so the denominators are the full paired strata; convention B (printed above) drops those
    #      pairs and reads committed verdicts only. Both conventions are always reported.
    pairedA = [(p1[k], p2[k]) for k in sorted(p1) if k in p2]
    resA = {}
    for s in ("contested", "cross", "all"):
        sub = [(r1, r2) for r1, r2 in pairedA if s == "all" or r1["s"] == s]
        if not sub: continue
        d = sum(1 if (bad_row(r1) or bad_row(r2)) else int(r1["w"] != r2["w"]) for r1, r2 in sub)
        resA[s] = dict(n=len(sub), d=d, floor=d / len(sub))
    order = [s for s in ("contested", "cross", "all") if s in resA]
    if order:
        L.append("    CONVENTION A (INVALID or non-terminated in either pass = disagreement; denominators %s): %s; pairs dropped by the script %d "
                 "(pass 1 INVALID %d, pass 2 INVALID %d); convention B as printed above.%s"
                 % (" / ".join(str(resA[s]["n"]) for s in order),
                    ", ".join("%s %d/%d = %.3f" % (s, resA[s]["d"], resA[s]["n"], resA[s]["floor"]) for s in order),
                    len(pairedA) - len(paired), sum(bad_row(r1) for r1, _ in pairedA), sum(bad_row(r2) for _, r2 in pairedA), CONV_A_NOTE))
    if "all" not in res:
        L.append("  no paired valid matches between the passes; floor not read")
        write(); return
    a = res["all"]
    c, x = res.get("contested"), res.get("cross")
    se1000 = ((a["floor"] * (1 - a["floor"]) / 1000) ** 0.5) * (a["deff"] ** 0.5)   # the same clustered SE rescaled to n ~ 1,000 at the measured DEFF
    thr300 = a["floor"] + 3 * a["sd"]
    L.append("")
    L.append("  ALARM (Stage 9 arm A, one-sided at 3 SE against the measured floor): floor %.3f | at n=%d (one epoch) threshold %.3f | at n~1,000 (three epochs pooled, same DEFF) threshold %.3f"
             % (a["floor"], a["n"], thr300, a["floor"] + 3 * ((a["floor"] * (1 - a["floor"]) / 1000) ** 0.5) * (a["deff"] ** 0.5)))
    # rule (ii) (pre-run bracket 96bd3d7, programme L3631), decided on the CONTESTED floor under BOTH conventions, at 3 dp.
    # Flush-left at column 0: there is NO consumer of this line today (placement_steps.py:142 reads ARM-B's
    # ref_remint_outcome.txt, not this file); column 0 only makes it format-compatible with that reader's exact-equality
    # startswith on the unstripped line, so a future consumer can read it.
    state = alarm_state(c["floor"] if c else None, resA["contested"]["floor"] if "contested" in resA else None)
    assert state in ALARM_STATES
    L.append("ALARM STATE: %s" % state)
    L.append(ALARM_STATE_NOTE)
    L.append("  CRITERION (registered): measured floor and agreement with interval -> %s" % ("READ" if a else "NOT READ"))
    if c and x:
        L.append("  PREDICTION: contested floor 4-6%% -> %.3f, %s; cross-tier lower than contested -> %.3f vs %.3f, %s"
                 % (c["floor"], "inside" if 0.04 <= c["floor"] <= 0.06 else "outside", x["floor"], c["floor"], "holds" if x["floor"] < c["floor"] else "does not hold"))
        # the MDE is read from the MEASURED SE, never from DECOMP's 0.057 literal (post-run review 2026-09-22 defect 4); registered wording kept around it
        L.append("  (a single pass pair of %d has MDE 1.96 x SE = %.1fpp at the measured floor %.3f, and %.1fpp at n ~ 1,000 at the same DEFF; the one-sided "
                 "3-SE alarm at n=%d fires at %.3f, a +%.1fpp drift; the strata compare at n=%d each and are descriptive, not a test)"
                 % (a["n"], 196 * a["sd"], a["floor"], 196 * se1000, a["n"], thr300, 100 * (thr300 - a["floor"]), c["n"]))
    write()


# ── CANARY-EPOCH2-RUNG: the analysis (registered C0-C4, P1-P6, falsifier) ──────────────────────────────────────

def _boot_se(byq, B, seed):
    """Question-clustered bootstrap SE of the mean of per-match values (resample questions with replacement)."""
    qs = sorted(byq)
    if not qs: return float("nan")
    S = [sum(byq[q]) for q in qs]; N = [len(byq[q]) for q in qs]
    rng = random.Random(seed); k = len(qs); vals = []
    for _ in range(B):
        s = n = 0
        for _j in range(k):
            i = rng.randrange(k); s += S[i]; n += N[i]
        vals.append(s / n)
    mu = sum(vals) / B
    return (sum((v - mu) ** 2 for v in vals) / (B - 1)) ** 0.5


def _decisive(r):
    return (not _bad(r)) and r["winner"] not in ("TIE", "INVALID")


def epoch2_compute(set_ms, P, meta_of, B=EPOCH2_BOOT, seeds=(EPOCH2_SEED,) + EPOCH2_EXTRA_SEEDS, no_rung=False):
    """Everything the readout prints, from the four passes' rows (P[n] = {match_id: row} or None). Pure."""
    ids = [m["match_id"] for m in set_ms]
    qid = {m["match_id"]: m["qid"] for m in set_ms}
    strat = {m["match_id"]: m["stratum"] for m in set_ms}
    s = dict(n_set=len(ids), n_q=len(set(qid.values())), no_rung=no_rung)
    sizes = Counter(qid.values())
    s["kish"] = sum(v * v for v in sizes.values()) / max(1, sum(sizes.values()))

    def pair(a, b):
        if P.get(a) is None or P.get(b) is None: return None
        common = [i for i in ids if i in P[a] and i in P[b]]
        dA = {i: disagree_A(P[a][i], P[b][i]) for i in common}
        okB = [i for i in common if not _bad(P[a][i]) and not _bad(P[b][i])]
        dB = sum(int(P[a][i]["winner"] != P[b][i]["winner"]) for i in okB)
        dec = [i for i in common if _decisive(P[a][i]) and _decisive(P[b][i])]
        rev = sum(1 for i in dec if P[a][i]["winner"] != P[b][i]["winner"])
        return dict(n=len(common), D=sum(dA.values()), d=sum(dA.values()) / max(1, len(common)), dA=dA, nB=len(okB), DB=dB,
                    dB=dB / max(1, len(okB)), n_dec=len(dec), rev=rev,
                    half={h: (sum(dA[i] for i in common if strat[i] == h), sum(1 for i in common if strat[i] == h)) for h in ("contested", "cross")})
    s["p12"], s["p23"], s["p34"] = pair(1, 2), pair(2, 3), pair(3, 4)
    # C0 core validity
    r3 = P.get(3)
    fp = Counter()
    for k in (3, 4):
        if P.get(k): fp.update(r.get(c) for r in P[k].values() for c in ("provider1", "provider2"))
    s["fp"] = dict(fp)
    s["foreign_fp"] = sorted(str(x) for x in set(fp) - {EXPECTED_FINGERPRINT, REFUSAL_FINGERPRINT})
    pilot_ids = ids[:PILOT_N]
    s["pilot3"] = (sum(1 for i in pilot_ids if r3 and i in r3 and _bad(r3[i])), sum(1 for i in pilot_ids if r3 and i in r3))
    h = set_hash(set_ms)
    c0 = [("(a) set hash %s" % SET_HASH_OF_RECORD, h == SET_HASH_OF_RECORD, "recomputed %s" % h),
          ("(b) the pass 1 -> 2 floor %d/%d reproduced from the caches" % (FLOOR12_OF_RECORD, N_SET),
           bool(s["p12"] and s["p12"]["D"] == FLOOR12_OF_RECORD and s["p12"]["n"] == N_SET),
           "%s/%s" % (s["p12"]["D"] if s["p12"] else "-", s["p12"]["n"] if s["p12"] else "-")),
          ("(c) every pass 3 / pass 4 call fingerprinted %s" % EXPECTED_FINGERPRINT, not s["foreign_fp"], "%s" % s["fp"]),
          ("(d) pass 3 complete", bool(r3 and len(r3) == N_SET), "%d of %d" % (len(r3) if r3 else 0, N_SET)),
          ("(e) the pass-3 pilot's truncation guard (<= 5%)", s["pilot3"][1] == PILOT_N and s["pilot3"][0] <= GUARD_RATE * PILOT_N,
           "%d of %d unusable" % s["pilot3"])]
    s["c0"] = c0
    s["valid"] = all(ok for _l, ok, _d in c0)
    # the rung's validity
    r4 = P.get(4)
    if r4 is None:
        s["rung"] = "ABSENT"; s["rung_detail"] = "pass 4 not run%s" % (" (--no-rung declared)" if no_rung else "")
    elif not r4:
        s["rung"] = "INVALID"
        s["rung_detail"] = ("pass 4 cache EXISTS with 0 of %d rows (started %s): not within-session evidence; C2 UNDETERMINED BY VALIDITY"
                            % (N_SET, meta_of.get(4, {}).get("started")))
    else:
        last3 = max(r["ts"] for r in r3.values()) if r3 else None
        first4 = min(r["ts"] for r in r4.values())
        started4 = meta_of.get(4, {}).get("started")
        st4 = time.mktime(time.strptime(started4, "%Y-%m-%d %H:%M:%S")) if started4 else first4
        gap = (max(first4, st4) - last3) if last3 is not None else float("inf")
        p4 = (sum(1 for i in pilot_ids if i in r4 and _bad(r4[i])), sum(1 for i in pilot_ids if i in r4))
        ok = bool(len(r4) == N_SET and gap <= RUNG_WINDOW_S and p4[1] == PILOT_N and p4[0] <= GUARD_RATE * PILOT_N)
        s["rung"] = "VALID" if ok else "INVALID"
        s["rung_detail"] = ("pass 4 %d of %d | started %s, first row %.0f s and launch %.0f s after pass 3's last row (window %d s) -> %s | pass-4 "
                            "pilot %d of %d unusable" % (len(r4), N_SET, started4, first4 - last3 if last3 else float("nan"),
                                                         st4 - last3 if last3 else float("nan"), RUNG_WINDOW_S,
                                                         "within-session" if gap <= RUNG_WINDOW_S else "NOT within-session", p4[0], p4[1]))
    # intervals (question-clustered, point +- 1.96 SE)
    reads = []
    for j, sd in enumerate(seeds):
        row = {}
        for key, a, b in (("d32", "p23", None), ("d43", "p34", None), ("Delta", "p23", "p34")):
            pa, pb = s.get(a), (s.get(b) if b else None)
            if pa is None or (b and pb is None):
                row[key] = None; continue
            byq = defaultdict(list)
            for i, v in pa["dA"].items():
                if b:
                    if i in pb["dA"]: byq[qid[i]].append(v - pb["dA"][i])
                else:
                    byq[qid[i]].append(v)
            row[key] = _boot_se(byq, B, sd)
        reads.append((sd, row))
    s["se"] = reads[0][1]; s["reads"] = reads
    if s["p23"] and s["p34"]:
        both = [i for i in s["p23"]["dA"] if i in s["p34"]["dA"]]
        s["Delta"] = sum(s["p23"]["dA"][i] - s["p34"]["dA"][i] for i in both) / max(1, len(both))
    else:
        s["Delta"] = None
    if s["p23"]:
        d, n = s["p23"]["d"], s["p23"]["n"]
        bino = (d * (1 - d) / max(1, n)) ** 0.5
        s["deff32"] = (s["se"]["d32"] / bino) ** 2 if bino > 0 else float("nan")
    # completeness
    # D1: with pass 3 complete the outcome of record is written whatever pass 4's state (present with any row count, or absent and
    # declared by --no-rung); only an absent, undeclared pass 4 (it may still run) keeps the readout partial.
    s["pass4_rows"] = None if r4 is None else len(r4)
    s["complete"] = bool(r3 and len(r3) == N_SET and (r4 is not None or no_rung))
    unusable = sum(int(r["finish1"] in ("length", "content_filter") or r["vote1"] == "INVALID")
                   + int(r["finish2"] in ("length", "content_filter") or r["vote2_raw"] == "INVALID")
                   for k in (3, 4) if P.get(k) for r in P[k].values())
    s["unusable_calls"] = unusable
    s["calls"] = sum(2 * len(P[k]) for k in (3, 4) if P.get(k))
    return s


def _iv(point, se):
    return point - 1.96 * se, point + 1.96 * se


def epoch2_readout(s):
    """The outcome text; every registered branch registers its tag. Pure function of epoch2_compute's dict."""
    L = []; p = L.append
    p("=== %s | %s ===" % (TEST_EPOCH2, REGISTRATION_EPOCH2))
    p("  set %s (%d matches over %d questions, Kish %.3f) | judge %s | max_tokens %d | temperature %s | dual order, TIE on flip | "
      "convention A DECIDES (an unusable row in either pass = a disagreement; denominator the 300), B beside (pairs usable in both) | "
      "script sha256-lf16 %s" % (SET_HASH_OF_RECORD, s["n_set"], s["n_q"], s["kish"], JUDGE, MAXTOK, temp_label(), script_hash_lf()))
    p("")
    p("(C0) VALIDITY, FIRST:")
    for lab, ok, det in s["c0"]:
        p("     %-66s %s  %s" % (lab, "PASS" if ok else "FAIL", det))
    ehit("C0:PASS" if s["valid"] else "C0:FAIL")
    p("     rung: %s - %s" % (s["rung"], s["rung_detail"]))
    ehit("RUNG:" + s["rung"])
    p23, p34, p12 = s["p23"], s["p34"], s["p12"]
    p("")
    if p23 is None:
        p("(C1) pass 3 absent: nothing is read.")
        ehit("C1:UND_VALIDITY"); p("ALARM STATE: UNDETERMINED")
        return "\n".join(L) + "\n", dict(state="UNDETERMINED")
    lo, hi = _iv(p23["d"], s["se"]["d32"])
    p("(C1) THE ALARM (registered at L9983): d32 = the share of the %d matches whose combined dual-order verdict differs between pass 2 "
      "and pass 3 = %d/%d = %.4f (convention A); convention B %d/%d = %.4f (%d pairs unusable in either pass dropped); question-clustered "
      "interval [%.3f, %.3f] (SE %.4f, B %d, seed %d; printed, NOT deciding: THE POINT DECIDES)"
      % (p23["n"], p23["D"], p23["n"], p23["d"], p23["DB"], p23["nB"], p23["dB"], p23["n"] - p23["nB"], lo, hi, s["se"]["d32"], EPOCH2_BOOT, EPOCH2_SEED))
    alarm = p23["D"] * ALARM_DEN >= ALARM_NUM * p23["n"]           # integer comparison: d32 >= 0.138
    if (float("%.3f" % p23["d"]) >= ALARM_NUM / ALARM_DEN) != alarm:
        p("     NOTE: the 3-dp reading differs from the exact reading here; the EXACT comparison is the one applied")
    alarm_b = p23["nB"] > 0 and p23["DB"] * ALARM_DEN >= ALARM_NUM * p23["nB"]   # convention B, printed beside, deciding nothing
    if not s["valid"]:
        state = "UNDETERMINED"; ehit("C1:UND_VALIDITY")
        p("     C1: UNDETERMINED BY VALIDITY (C0 failed); the point is printed and NOT scored")
    else:
        state = "ALARM" if alarm else "NO ALARM"; ehit("C1:ALARM" if alarm else "C1:NO_ALARM")
        p("     C1 (CONVENTION A DECIDES, b0b5d0d): %s (d32_A %d/%d = %.4f %s 0.138 = floor 0.087 + 3 SE at n = 300; one-sided)"
          % (state, p23["D"], p23["n"], p23["d"], ">=" if alarm else "<"))
        p("     beside, deciding nothing: convention B would read %s (d32_B %d/%d = %.4f)"
          % ("ALARM" if alarm_b else "NO ALARM", p23["DB"], p23["nB"], p23["dB"]))
        if alarm_b != alarm:
            ehit("C1:AB_DISAGREE")
            p("     A AND B DISAGREE ON THE ALARM: both are recorded (A %s, B %s) and CONVENTION A DECIDES: %s"
              % ("ALARM" if alarm else "NO ALARM", "ALARM" if alarm_b else "NO ALARM", state))
        else:
            ehit("C1:AB_AGREE")
            p("     A and B agree on the alarm.")
    p("ALARM STATE: %s" % state)
    p("     halves (descriptive): contested %d/%d, cross-tier %d/%d" % (p23["half"]["contested"] + p23["half"]["cross"]))
    p("")
    if p34 is None or s["rung"] != "VALID":
        ehit("C2:UND_VALIDITY")
        p("(C2) THE RUNG, DESCRIPTIVE-ONLY: UNDETERMINED BY VALIDITY (%s; pass-4 rows %s)%s" % (s["rung"], s.get("pass4_rows"), "" if p34 is None else
          "; d43 = %d/%d = %.4f printed, not read" % (p34["D"], p34["n"], p34["d"])))
    else:
        ehit("C2:READ")
        l4, h4 = _iv(p34["d"], s["se"]["d43"])
        ld, hd = _iv(s["Delta"], s["se"]["Delta"])
        p("(C2) THE RUNG, DESCRIPTIVE-ONLY: d43 (pass 3 vs pass 4, same session) = %d/%d = %.4f [%.3f, %.3f] (SE %.4f); convention B "
          "%d/%d = %.4f | Delta = d32 - d43 = %+.4f [%+.3f, %+.3f] (SE %.4f, paired on the same matches, question-clustered)"
          % (p34["D"], p34["n"], p34["d"], l4, h4, s["se"]["d43"], p34["DB"], p34["nB"], p34["dB"], s["Delta"], ld, hd, s["se"]["Delta"]))
        p("     halves: contested %d/%d, cross-tier %d/%d" % (p34["half"]["contested"] + p34["half"]["cross"]))
        p("RUNG d43 = %.4f [%.4f, %.4f]" % (p34["d"], l4, h4))
    p("     bootstrap seeds %d-%d (C1's point does not depend on them): %s"
      % (EPOCH2_EXTRA_SEEDS[0], EPOCH2_EXTRA_SEEDS[-1],
         ", ".join("%d:%s" % (sd, "/".join("%s %.4f" % (k, v) for k, v in row.items() if v is not None)) for sd, row in s["reads"][1:])))
    p("")
    ehit("C3:READ")
    p("(C3) REVERSALS (decisive in both passes, opposite winners): (1, 2) %d of %d [record: 0 of 215] | (2, 3) %d of %d | (3, 4) %s"
      % (p12["rev"] if p12 else -1, p12["n_dec"] if p12 else 0, p23["rev"], p23["n_dec"],
         "%d of %d" % (p34["rev"], p34["n_dec"]) if p34 else "not run"))
    ehit("C4:READ")
    parts = [x for x in (p12, p23, p34) if x]
    D = sum(x["D"] for x in parts); n = sum(x["n"] for x in parts)
    p("(C4) THE POOLED LINE, DESCRIPTIVE: %d pass pair(s) pooled: %d/%d = %.4f beside %.3f at n = 900 (not an alarm rule: its pooling rule is "
      "not registered)%s" % (len(parts), D, n, D / max(1, n), POOLED_BAR_900, "" if len(parts) == 3 else " - FEWER THAN THREE PAIRS"))
    p("")
    p("SUPPORT. " + EPOCH2_REG_SUPPORT)
    p("  MEASURED: d32 SE %.4f (question-clustered), binomial %.4f, DEFF %.2f, n_eff %.1f, MDE (2.80 x SE) %.4f; Kish %.3f over %d questions"
      % (s["se"]["d32"], (p23["d"] * (1 - p23["d"]) / p23["n"]) ** 0.5, s.get("deff32", float("nan")),
         p23["n"] / s["deff32"] if s.get("deff32") and s["deff32"] == s["deff32"] and s["deff32"] > 0 else float("nan"),
         2.80 * s["se"]["d32"], s["kish"], s["n_q"]))
    p("")
    p("PREDICTIONS (registered; scored on the points):")
    rv = s["valid"]; rungv = rv and s["rung"] == "VALID"
    preds = [("P1", "d32 = 0.087 [0.050, 0.125]", rv, lambda: 0.050 <= p23["d"] <= 0.125, "%.4f" % p23["d"]),
             ("P2", "C1 NO ALARM", rv, lambda: not alarm, state),
             ("P3", "d43 = 0.080 [0.045, 0.120]", rungv, lambda: 0.045 <= p34["d"] <= 0.120, "%.4f" % p34["d"] if p34 else "-"),
             ("P4", "Delta = +0.007 [-0.040, +0.050]", rungv, lambda: -0.040 <= s["Delta"] <= 0.050, "%+.4f" % s["Delta"] if s["Delta"] is not None else "-"),
             ("P5", "reversals 0 [0, 2] in each of (2, 3) and (3, 4)", rungv, lambda: p23["rev"] <= 2 and p34["rev"] <= 2,
              "%d / %s" % (p23["rev"], p34["rev"] if p34 else "-")),
             ("P6", "fingerprint on 1,200 of 1,200; INVALID or unusable 0 [0, 3]", rungv,
              lambda: not s["foreign_fp"] and s["calls"] == EPOCH2_REGISTERED_CALLS and s["unusable_calls"] <= 3,
              "%d calls, foreign %s, unusable %d" % (s["calls"], s["foreign_fp"] or "none", s["unusable_calls"]))]
    for pid, text, scoreable, test, val in preds:
        tag = ("HELD" if bool(test()) else "FAILED") if scoreable else "UND"
        ehit("%s:%s" % (pid, tag))
        p("  %s %-62s %-28s -> %s" % (pid, text, val, tag if tag != "UND" else "UNDETERMINED BY VALIDITY"))
    p("")
    fired = False
    if not rv:
        ehit("FALS:NOT_EVALUATED"); p("FALSIFIER: NOT EVALUATED (C0 failed)."); fired = True
    else:
        if alarm:
            ehit("FALS:ALARM_FIRES"); fired = True
            p("FALSIFIER FIRES: C1 ALARM (d32 >= 0.138) fires plan Amendment 4 trigger (3) and OVERTURNS the standing reading that the deployed "
              "judge's verdict floor is stable since 2026-09-22: every judged number recorded after pass 2 is flagged for re-read by insertion.")
        if rungv and p34["d"] < 0.045:
            ehit("FALS:P3_LOW"); fired = True
            p("P3 FAILS LOW (d43 < 0.045): a within-session floor well below the week-apart one means session drift carries part of the 0.087, "
              "and a same-session paired design's floor is lower than the record uses.")
        if rungv and p34["d"] > 0.120:
            ehit("FALS:P3_HIGH"); fired = True
            p("P3 FAILS HIGH (d43 > 0.120).")
        if (p23["rev"] >= 3) or (rungv and p34["rev"] >= 3):
            ehit("FALS:P5_FIRES"); fired = True
            p("P5 FAILS (>= 3 reversals in a pair): the reading 'churn lives only at the tie boundary' (CANARY-BASELINE pass 2) fails.")
    if not fired:
        ehit("FALS:NOT_FIRED"); p("FALSIFIER: NOT FIRED.")
    return "\n".join(L) + "\n", dict(state=state)


def analyze_epoch2(no_rung=False, boot=EPOCH2_BOOT):
    install_db_guard(writable=None)
    pins = pin_old_caches("--analyze-epoch2 (start)")
    matches, meta = freeze_set()
    P, M = {}, {}
    for k in (1, 2, 3, 4):
        got = _rows_of(k)
        P[k], M[k] = (got[0], got[1]) if got else (None, {})
    if P[4] is not None and no_rung:
        print("[RUNG] --no-rung is a declaration for an ABSENT pass 4; a pass-4 cache exists (%d rows), so its state is read from the cache "
              "(READY D1)." % len(P[4]), flush=True)
    s = epoch2_compute(matches, P, M, B=boot, no_rung=no_rung)
    text, res = epoch2_readout(s)
    text += atl.summary_line(TEST_EPOCH2, acct_caches(), LEDGER_DIR) + "\n"
    text += ("HEADER: %s | caches %s | pass 3 meta started %s / pass 4 %s | old-cache pins %s | written %s\n"
             % (TEST_EPOCH2, ", ".join("%d:%s" % (k, "present" if P[k] is not None else "absent") for k in (1, 2, 3, 4)),
                M[3].get("started"), M[4].get("started"), {k: v[:16] for k, v in pins.items()}, time.strftime("%Y-%m-%d %H:%M:%S")))
    print(text, flush=True)
    rc = write_epoch2(text, s["complete"], len(P[3] or {}))
    if pin_old_caches("--analyze-epoch2 (end)") != pins:
        raise SystemExit("[PIN] a cache of record CHANGED during --analyze-epoch2")
    print(dbguard_line())
    return rc


def write_epoch2(text, complete, n3):
    if not complete:
        ehit("WRITE:PARTIAL")
        target = OUT_EPOCH2_PILOT if n3 <= PILOT_N else OUT_EPOCH2_PARTIAL
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write("NOT OF RECORD - pass 3 holds %d of %d, or pass 4 is absent and not declared (--no-rung); no line below is a registered "
                    "reading.\n\n" % (n3, N_SET) + text)
        print("[ANALYZE-EPOCH2] incomplete: wrote %s; NO outcome of record." % rel(target), flush=True)
        return 2
    try:
        with open(OUT_EPOCH2, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        ehit("WRITE:REFUSED_EXISTS")
        print("[ANALYZE-EPOCH2] REFUSED: %s exists and is WRITE-ONCE; nothing was overwritten." % rel(OUT_EPOCH2), flush=True)
        return 3
    ehit("WRITE:RECORD")
    print("[ANALYZE-EPOCH2] wrote %s (write-once)" % rel(OUT_EPOCH2), flush=True)
    return 0


# ── CANARY-EPOCH2-RUNG: the selftest (0 calls; temp fixtures; an INJECTED FAKE POSTER; a socket guard) ─────────

def selftest_epoch2():
    import socket, shutil, tempfile
    global NPASS, OUT_EPOCH2, OUT_EPOCH2_PILOT, OUT_EPOCH2_PARTIAL, LEDGER_DIR, TRACE_CACHES, PASS_CACHE_SHA256, READY_EPOCH2
    fails = []

    def check(name, cond, detail=""):
        ok = bool(cond)
        print("  %-86s %s%s" % (name, "OK" if ok else "FAIL", "" if ok else "  " + str(detail)[:240]))
        if not ok: fails.append(name)

    def refuses(fn, *a, _want=None, **k):
        """True iff fn raises SystemExit (and, when _want is given, its message names the reason: a refusal for the WRONG reason is
        a vacuous test and counts as a failure)."""
        try:
            fn(*a, **k); return False
        except SystemExit as e:
            return _want is None or _want in str(e)

    print("[POOL] %s (selftest: synthetic fixtures; pool_guard is NOT called and no DB of record is opened)" % POOL)
    print("[SELFTEST-EPOCH2] %s | script sha256-lf16 %s | 0 calls | python -O: %s" % (TEST_EPOCH2, script_hash_lf(), not __debug__))
    g = globals()
    saved = {k: g[k] for k in ("NPASS", "OUT_EPOCH2", "OUT_EPOCH2_PILOT", "OUT_EPOCH2_PARTIAL", "LEDGER_DIR", "TRACE_CACHES", "PASS_CACHE_SHA256",
                               "READY_EPOCH2", "cache_path", "freeze_set", "build_jobs", "go_gate_epoch2", "SET_HASH_OF_RECORD", "pool_qids")}
    saved_rr = (rr.call_judge_full, rr.load_env)
    saved_sock = socket.socket.connect
    tmp = tempfile.mkdtemp(prefix="canary_epoch2_selftest_")

    def no_net(*a, **k):
        raise SystemExit("[SELFTEST] a network connection was attempted")
    socket.socket.connect = no_net
    try:
        # the frozen set: 300 matches over 279 questions (21 questions carry 2 matches), half contested
        ms = []
        for i in range(N_SET):
            q = 90000 + (i if i < 258 else 258 + (i - 258) // 2)
            ms.append(dict(match_id=500000 + i, qid=q, model_a="Model-Alpha", model_b="Model-Beta", node_id="n0", anchor="anchorX",
                           stratum="contested" if i % 2 else "cross", pair_kind="frontier" if i % 2 else "cross"))
        g["SET_HASH_OF_RECORD"] = set_hash(ms)                                 # the fixture's own set hash: C0 (a) and verify_set RECOMPUTE it
        g["pool_qids"] = lambda: {m["qid"] for m in ms}
        cdir = [tmp]                                                            # the directory the pass caches live in (scenarios switch it)
        g["cache_path"] = lambda n=None: os.path.join(cdir[0], "pass%d.db" % (n or NPASS))
        g["freeze_set"] = lambda allow_freeze=False: (ms, dict(set_hash=SET_HASH_OF_RECORD, pool_id=POOL, matches=ms))
        OUT_EPOCH2, OUT_EPOCH2_PILOT, OUT_EPOCH2_PARTIAL = (os.path.join(tmp, x) for x in ("e2.txt", "e2_PILOT.txt", "e2_partial.txt"))
        LEDGER_DIR = tmp
        json.dump([{"test": "OTHER", "launch": "x", "calls": 4060, "ts": "t"}], open(os.path.join(tmp, atl.NIGHT_FILE), "w"))
        TRACE_CACHES = [os.path.join(tmp, "trace_truncation.db")]           # the OTHER accepted test: 150 rows = 300 calls
        tc = _TRUE_CONNECT(TRACE_CACHES[0])
        tc.execute("CREATE TABLE verdicts (match_id INTEGER, arm TEXT)")
        tc.executemany("INSERT INTO verdicts VALUES (?, 'original')", [(i,) for i in range(150)])
        tc.commit(); tc.close()
        day_path = atl.day_ledger_path(LEDGER_DIR)

        def write_pass(n, winners, ts0=None):
            con = _TRUE_CONNECT(cache_path(n))
            con.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                        "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
                        "raw1 TEXT, raw2 TEXT, ts REAL, finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, stratum TEXT, pair_kind TEXT"
                        + (", provider1 TEXT, provider2 TEXT" if n == 2 else "") + ")")
            con.execute("CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT)")
            for m, w in zip(ms, winners):
                vals = [m["match_id"], m["model_a"], m["model_b"], m["node_id"], m["qid"], m["anchor"], "A", 1, "Model A", "Model B", 0.8, 0.8,
                        w, int(w == "TIE"), 0, "", "", ts0 or 0.0, "stop", "stop", 10, 10, m["stratum"], m["pair_kind"]]
                if n == 2: vals += [EXPECTED_FINGERPRINT, EXPECTED_FINGERPRINT]
                con.execute("INSERT INTO verdicts VALUES (%s)" % ",".join("?" * len(vals)), vals)
            for k, v in current_meta(dict(set_hash=SET_HASH_OF_RECORD)).items():
                con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v if k != "pass_no" else str(n)))
            con.commit(); con.close()
        w1 = ["Model-Alpha"] * N_SET
        w2 = ["TIE" if i < 26 else "Model-Alpha" for i in range(N_SET)]        # 26 disagreements, all at the tie boundary
        write_pass(1, w1); write_pass(2, w2)
        PASS_CACHE_SHA256 = {1: file_sha256(cache_path(1)), 2: file_sha256(cache_path(2))}
        f0, f1, f2, f3 = _fragments()

        def fake_jobs(todo):
            return [(m, ("B", "ref text", 1), "SYSTEM PROMPT %s" % m["anchor"],
                     f0 + "Question %d?\n\n[Reference solution]\n(B) ref" % m["qid"] + f1 + "trace alpha %d" % m["match_id"] + f2 + "trace beta" + f3,
                     f0 + "Question %d?\n\n[Reference solution]\n(B) ref" % m["qid"] + f1 + "trace beta" + f2 + "trace alpha %d" % m["match_id"] + f3)
                    for m in todo]
        g["build_jobs"] = fake_jobs
        rr.load_env = lambda: None
        mode = {"tie_below": 0, "fp": EXPECTED_FINGERPRINT, "inv_below": 0, "err_below": 0}

        def fake_post(system, user, retries=6):
            mid = int(user.split("trace alpha ")[1].split("\n")[0].split()[0].strip().rstrip("\n")[:6])
            if (mid - 500000) < mode["err_below"]:
                raise RuntimeError("fake transport error for match %d" % mid)
            if (mid - 500000) < mode["inv_below"]:
                return ("no json here", mode["fp"], 20, 0.0, "stop", {"_response_id": "fake-%d" % mid})
            alpha_first = user.index("trace alpha") < user.index("trace beta")
            v = "TIE" if (mid - 500000) < mode["tie_below"] else ("Model A" if alpha_first else "Model B")
            return ('{"winner": "%s", "confidence": 0.9}' % v, mode["fp"], 20, 0.0, "stop", {"_response_id": "fake-%d" % mid})
        rr.call_judge_full = fake_post
        configure_rr()

        # 1. refusals before anything is posted
        NPASS = 2
        check("posting pass 2 (a closed cache of record) is REFUSED", refuses(run, 12, 2, go=True, _want="[PASS]"))
        NPASS = 1
        check("posting pass 1 is REFUSED", refuses(run, None, 2, go=True, full=True, _want="[PASS]"))
        NPASS = 3
        check("a launch without --pilot / --run is REFUSED", refuses(run, None, 2, go=True, _want="[MODE]"))
        check("the gate REFUSES without --go and a committed READY (before any DB)", refuses(go_gate_epoch2, "probe", False, _want="[GATE]"))
        READY_EPOCH2 = os.path.join(tmp, "READY.md")
        open(READY_EPOCH2, "w").write("READY: %s %s\n" % (TEST_EPOCH2, script_hash_lf()))
        check("an untracked READY file does not open the gate", refuses(go_gate_epoch2, "probe", True, _want="tracked False"))
        check("parse_ready (D8): a verdict line after a blank line is read (the regex no longer eats the blank line)",
              parse_ready_epoch2("# Title\n\nREADY: %s abc\n" % TEST_EPOCH2, "abc")[1] == [], parse_ready_epoch2("# Title\n\nREADY: %s abc\n" % TEST_EPOCH2, "abc"))
        check("parse_ready: the first verdict line must name the test and the LF sha",
              parse_ready_epoch2("READY: %s abc\n" % TEST_EPOCH2, "abc")[1] == [] and parse_ready_epoch2("READY: X abc\n", "abc")[1]
              and parse_ready_epoch2("READY: %s abc\nNOT READY: y\n" % TEST_EPOCH2, "abc")[1])
        g["go_gate_epoch2"] = lambda what, go: print("[GATE] (selftest) %s OPEN" % what)
        install_db_guard(writable=cache_path(3))
        check("DBGUARD: a read-write open of the pass-1 cache of record is REFUSED", refuses(sqlite3.connect, cache_path(1), _want="read-write open"))
        con = sqlite3.connect("file:%s?mode=ro" % cache_path(1).replace("\\", "/"), uri=True); con.close()
        check("DBGUARD: a read of the pass-1 cache is rewritten to mode=ro&immutable=1", _OPENED and _OPENED[-1][0] == "ro-immutable")
        open(cache_path(2) + "-wal", "wb").write(b"x")
        check("DBGUARD: a non-empty -wal beside a cache is a refused precondition",
              refuses(sqlite3.connect, "file:%s?mode=ro" % cache_path(2).replace("\\", "/"), uri=True, _want="-wal is non-empty"))
        os.remove(cache_path(2) + "-wal")
        check("open_cache refuses passes 1 and 2", refuses(open_cache, 1, _want="[PASS]") and refuses(open_cache, 2, _want="[PASS]"))
        j0 = fake_jobs(ms[:3])
        sc = scan_payloads(j0)
        check("scan: 6 payloads decomposed, frame identical across orders, clean", sc["payloads"] == 6 == sc["decomposed"] == sc["frame_same"] == sc["frame_clean"], sc)
        m_, r_, sy_, u1_, u2_ = j0[0]
        check("scan: a contestant name in the question slot REFUSES",
              refuses(scan_payloads, [(m_, r_, sy_, u1_.replace("?\n\n[Reference solution]", " Model-Alpha?\n\n[Reference solution]"),
                                       u2_.replace("?\n\n[Reference solution]", " Model-Alpha?\n\n[Reference solution]"))], _want="outside the trace slots"))
        check("scan: a per-side element outside the traces (the frame differs between orders) REFUSES",
              refuses(scan_payloads, [(m_, r_, sy_, u1_.replace("(B) ref", "(B) ref [A wins]"), u2_)], _want="frame differs"))
        check("scan: a key-side token in the question slot (dataset text) is counted, not refused",
              scan_payloads([(m_, r_, sy_, u1_.replace("?\n\n[Reference solution]", " checkerboard?\n\n[Reference solution]"),
                              u2_.replace("?\n\n[Reference solution]", " checkerboard?\n\n[Reference solution]"))])["token_in_question"] == 1)
        check("--run before the pass-3 pilot is REFUSED", refuses(run, None, 2, go=True, full=True, _want="[RUN]"))
        check("D7: --pilot other than 12 is REFUSED", refuses(run, 5, 2, go=True, _want="[MODE] --pilot 5"))
        check("D7: --override-guard is REFUSED on passes 3 / 4", refuses(run, PILOT_N, 2, True, go=True, _want="--override-guard is REFUSED"))
        check("D4: verify_set passes the fixture set (hash recomputed)", verify_set(ms, dict(set_hash=SET_HASH_OF_RECORD, pool_id=POOL)) == SET_HASH_OF_RECORD)
        ms_t = [dict(m) for m in ms]; ms_t[0]["model_b"] = "Model-Gamma"
        check("D4: a tampered set REFUSES in verify_set (explicit SystemExit, -O-proof)",
              refuses(verify_set, ms_t, dict(set_hash=SET_HASH_OF_RECORD, pool_id=POOL), _want="[SET] REFUSED"))
        tpl = rj.USER_TEMPLATE
        try:
            rj.USER_TEMPLATE = tpl.replace("Your task", "Your checker task", 1)
            ff = _fragments()
            jt = [(m_, r_, sy_, ff[0] + "Q?" + ff[1] + "trace alpha 1" + ff[2] + "trace beta" + ff[3],
                   ff[0] + "Q?" + ff[1] + "trace beta" + ff[2] + "trace alpha 1" + ff[3])]
            check("scan (M7c): a key-side token in the user TEMPLATE REFUSES", "Your checker task" in rj.USER_TEMPLATE
                  and refuses(scan_payloads, jt, _want="in the user template"))
        finally:
            rj.USER_TEMPLATE = tpl
        # M17 / D6: a failing pass-3 PILOT refuses, in a scenario directory with copies of the two caches of record
        pdir = os.path.join(tmp, "pilotfail"); os.makedirs(pdir)
        for k in (1, 2): shutil.copy(cache_path(k), os.path.join(pdir, "pass%d.db" % k))
        cdir[0] = pdir
        LEDGER_DIR = os.path.join(pdir, "ledger"); os.makedirs(LEDGER_DIR)     # the scenario's posts never reach the main fixture's ledger
        mode["inv_below"] = 2
        check("M17: a pass-3 pilot with 2 of 12 INVALID FAILS its truncation guard", refuses(run, PILOT_N, 2, go=True, _want="[GUARD] the pass-3 pilot FAILED"))
        check("... and --run is then REFUSED", refuses(run, None, 2, go=True, full=True, _want="[GUARD] refusing to post the remaining"))
        mode["inv_below"] = 0
        os.remove(os.path.join(pdir, "pass3.db"))
        mode["err_below"] = 1
        check("D6: a pilot with 1 of 12 ERRORED (uncached) FAILS its guard (the error is counted)",
              refuses(run, PILOT_N, 2, go=True, _want="[GUARD] the pass-3 pilot FAILED"))
        nl_ = budget_gate_epoch2(0, "probe", refuse=False)
        check("M12: the errored call is in the ledger, not the cache: (i) counts the LARGER (the ledger)",
              nl_["own_ledger"] > nl_["own_cache"] and nl_["own"] == nl_["own_ledger"], {k: nl_[k] for k in ("own", "own_cache", "own_ledger")})
        mode["err_below"] = 0
        cdir[0] = tmp; LEDGER_DIR = tmp
        def acct_refusal(planned, **patch):
            saved_ = {k: getattr(atl, k) for k in patch}
            try:
                for k, v in patch.items(): setattr(atl, k, v)
                budget_gate_epoch2(planned, "probe")
                return False
            except SystemExit as e_:
                return str(e_)
            finally:
                for k, v in saved_.items(): setattr(atl, k, v)
        n0 = budget_gate_epoch2(0, "probe", refuse=False)
        check("ACCOUNT: the other accepted test's cache is counted in (iii) (TRACE 300 calls)",
              n0["both"]["TRACE-TRUNCATION"] == 300 and n0["combined"] == 4060 + 300, n0)
        r = acct_refusal(1262)
        check("ACCOUNT (i): 1,262 > the test's own ceiling 1,260 REFUSES", r and "(i) " in r and "(ii)" not in r and "(iii)" not in r, r)
        r = acct_refusal(8004, CEILINGS=dict(atl.CEILINGS, **{TEST_EPOCH2: 10 ** 6}))
        check("ACCOUNT (ii): above the 4,000-match rule REFUSES", r and "(ii)" in r and "(i) " not in r and "(iii)" not in r, r)
        r = acct_refusal(24, CLOSED_NIGHT_TOTAL=13690)
        check("ACCOUNT (iii): 13,690 + TRACE 300 + 24 > 14,000 REFUSES", r and "(iii)" in r and "(i) " not in r, r)
        mode["tie_below"] = 30                         # pass 3: 30 TIEs, 26 of them where pass 2 tied -> d32 = 4/300
        _m2 = dict(set_hash=SET_HASH_OF_RECORD)
        check("pre-flight 3: the pass 1 -> 2 floor 26/300 reproduces", preflight_epoch2(_m2, 3, now=time.time()) == [],
              preflight_epoch2(_m2, 3, now=time.time()))

        # 2. pass 3 through the fake poster: pilot, then run
        run(PILOT_N, 2, go=True)
        led = json.load(open(day_path))
        check("pass-3 pilot: 24 calls posted and appended to the POSTING-DATE ledger (created write-once)",
              led[-1]["calls"] == 24 and led[-1]["test"] == TEST_EPOCH2 and len(led) == 1, led)
        run(None, 2, go=True, full=True)
        r3, m3 = _rows_of(3)
        check("pass 3: 300 rows, provenance per row (ids, bodies, shas, order index, script sha), temperature 'omitted'",
              len(r3) == N_SET and m3.get("temperature") == "omitted")
        con = sqlite3.connect("file:%s?mode=ro" % cache_path(3).replace("\\", "/"), uri=True)
        x = con.execute("SELECT resp_id1, user1, user1_sha16, system_sha16, post_index, script_sha16_lf FROM verdicts LIMIT 1").fetchone()
        con.close()
        check("... the stored user body hashes to its stored sha16", x[0] and x[2] == _sha16(x[1]) and x[4] is not None and x[5] == script_hash_lf(), x[:1])
        check("pins unchanged after pass 3 (both caches of record)", pin_old_caches("selftest after pass 3") == PASS_CACHE_SHA256)
        check("pre-flight 4 REFUSES more than 2 h after pass 3's last row",
              any("UNDETERMINED BY VALIDITY" in pr for pr in preflight_epoch2(_m2, 4, now=time.time() + RUNG_WINDOW_S + 1)))
        # 3. pass 4 (the rung), within the window
        NPASS = 4
        mode["tie_below"] = 20
        run(PILOT_N, 2, go=True); run(None, 2, go=True, full=True)
        rc = analyze_epoch2(boot=60)
        txt = open(OUT_EPOCH2, encoding="utf-8").read() if os.path.exists(OUT_EPOCH2) else ""
        check("--analyze-epoch2 on complete caches writes the outcome of record", rc == 0 and "ALARM STATE: NO ALARM" in txt.split("\n"))
        check("the machine-readable lines are flush-left", any(l.startswith("RUNG d43 = ") for l in txt.split("\n")))
        check("C1 read with the integer rule: d32 = 4/300 here", "= 4/300 = 0.0133" in txt, [l for l in txt.split("\n") if l.startswith("(C1)")])
        first = open(OUT_EPOCH2, "rb").read()
        check("a second --analyze-epoch2 REFUSES to overwrite (write-once)", analyze_epoch2(boot=60) == 3 and open(OUT_EPOCH2, "rb").read() == first)
        led = json.load(open(day_path))
        own = sum(r["calls"] for r in led if r["test"] == TEST_EPOCH2)
        check("the ledger counts exactly 1,200 calls for the two passes", own == 1200, own)
        check("a further launch is refused by the test ceiling (1,200 + 62 > 1,260)", refuses(budget_gate_epoch2, 62, "probe", _want="(i) "))
        check("D1: once the epoch-2 outcome of record exists, posting is REFUSED (the record is closed)", refuses(run, PILOT_N, 2, go=True, _want="[RECORD]"))
        OUT_EPOCH2 = os.path.join(tmp, "e2_after.txt")
        # 4. a foreign fingerprint stops the run and caches nothing
        mode["fp"] = "azure:some-other-model"
        os.rename(cache_path(4), cache_path(4) + ".bak")
        LEDGER_DIR = os.path.join(tmp, "ledger2"); os.makedirs(LEDGER_DIR)   # a fresh ledger dir, so (i) counts the caches only
        day_path = atl.day_ledger_path(LEDGER_DIR)
        check("a foreign fingerprint STOPS the run", refuses(run, PILOT_N, 1, go=True, _want="[FINGERPRINT]"))
        check("... nothing is cached for it and the posted call is still counted in the ledger",
              _rows_of(4)[0] == {} and json.load(open(day_path))[-1]["calls"] >= 1)
        mode["fp"] = EXPECTED_FINGERPRINT
        os.remove(cache_path(4)); os.rename(cache_path(4) + ".bak", cache_path(4))
        # D1: the C1 outcome of record is written WHATEVER the state of pass 4 (the reviewer's cb_partial_rung.py scenarios, plus absent)
        def scenario(tag, k, no_rung):
            d = os.path.join(tmp, "rung_" + tag); os.makedirs(d)
            for n in (1, 2, 3): shutil.copy(os.path.join(tmp, "pass%d.db" % n), os.path.join(d, "pass%d.db" % n))
            if k is not None:
                shutil.copy(os.path.join(tmp, "pass4.db"), os.path.join(d, "pass4.db"))
                c_ = _TRUE_CONNECT(os.path.join(d, "pass4.db"))
                keep = [m["match_id"] for m in ms[:k]]
                c_.execute("DELETE FROM verdicts WHERE match_id NOT IN (%s)" % (",".join(str(x) for x in keep) or "-1")); c_.commit(); c_.close()
            cdir[0] = d
            g["OUT_EPOCH2"], g["OUT_EPOCH2_PILOT"], g["OUT_EPOCH2_PARTIAL"] = (os.path.join(d, x) for x in ("e2.txt", "e2_PILOT.txt", "e2_partial.txt"))
            try:
                rc_ = analyze_epoch2(no_rung=no_rung, boot=30)
            except SystemExit as e_:
                rc_ = "SystemExit: %s" % e_
            txt_ = open(OUT_EPOCH2, encoding="utf-8").read() if os.path.exists(OUT_EPOCH2) else ""
            cdir[0] = tmp
            return rc_, txt_
        for tag, k, nr in (("partial12", 12, False), ("partial12_norung", 12, True), ("empty0", 0, False), ("empty0_norung", 0, True)):
            rc_, txt_ = scenario(tag, k, nr)
            check("D1: pass 4 %s rows, --no-rung %s -> the outcome of record is WRITTEN: C1 read, rung INVALID, C2 UNDETERMINED BY VALIDITY"
                  % (k, nr), rc_ == 0 and "ALARM STATE: NO ALARM" in txt_.split("\n") and "rung: INVALID" in txt_
                  and "UNDETERMINED BY VALIDITY (INVALID; pass-4 rows %d)" % k in txt_ and not any(l.startswith("RUNG d43") for l in txt_.split("\n")),
                  (rc_, [l for l in txt_.split("\n") if "rung" in l.lower()][:3]))
        rc_, txt_ = scenario("absent", None, False)
        check("D1: pass 4 ABSENT without --no-rung stays partial (pass 4 may still run): rc 2, no outcome of record", rc_ == 2 and not txt_, rc_)
        rc_, txt_ = scenario("absent_norung", None, True)
        check("D1: pass 4 ABSENT with --no-rung (the declaration) writes the outcome: rung ABSENT, C2 UND",
              rc_ == 0 and "rung: ABSENT" in txt_ and "ALARM STATE: NO ALARM" in txt_.split("\n"), rc_)
        OUT_EPOCH2 = os.path.join(tmp, "e2_after.txt"); OUT_EPOCH2_PILOT = os.path.join(tmp, "e2_PILOT.txt"); OUT_EPOCH2_PARTIAL = os.path.join(tmp, "e2_partial.txt")
        # D2: the pass-4 window is measured from pass 4's PERSISTED start once a pass-4 cache exists, not from now
        r3_, _m3 = _rows_of(3)
        last3 = max(r["ts"] for r in r3_.values())
        ddir = os.path.join(tmp, "window"); os.makedirs(ddir)
        for n in (1, 2, 3): shutil.copy(os.path.join(tmp, "pass%d.db" % n), os.path.join(ddir, "pass%d.db" % n))
        cdir[0] = ddir
        late = time.time() + RUNG_WINDOW_S + 600
        check("D2: no pass-4 cache -> measured from now: a launch 2 h 10 m after pass 3 REFUSES",
              any("UNDETERMINED BY VALIDITY" in pr for pr in preflight_epoch2(_m2, 4, now=late)))
        c_ = _TRUE_CONNECT(os.path.join(ddir, "pass4.db"))
        c_.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, ts REAL)"); c_.execute("CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT)")
        c_.execute("INSERT INTO run_meta VALUES ('started', ?)", (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last3 + 100)),)); c_.commit(); c_.close()
        check("D2: pass 4 STARTED 100 s after pass 3 -> a relaunch 2 h 10 m later is still WITHIN (measured from the persisted start)",
              not any("UNDETERMINED BY VALIDITY" in pr for pr in preflight_epoch2(_m2, 4, now=late)), preflight_epoch2(_m2, 4, now=late))
        cdir[0] = tmp
        # M5b: the ANALYSIS reads the rung gap from pass 4's start: 7,201 s -> INVALID, 7,199 s -> VALID
        P_ = {k: _rows_of(k)[0] for k in (1, 2, 3, 4)}
        for off, want in ((RUNG_WINDOW_S + 1, "INVALID"), (RUNG_WINDOW_S - 1, "VALID")):
            st = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(last3) + off))
            got_ = epoch2_compute(ms, P_, {4: {"started": st}}, B=10, seeds=(42,))["rung"]
            check("M5b: pass 4 started %d s after pass 3's last row -> rung %s" % (off, want), got_ == want, got_)
        # M10: convention A counts an unusable row as a difference even when the combined winners agree
        bad_r = dict(P_[3][ms[40]["match_id"]]); bad_r["invalid"] = 1
        check("M10: disagree_A(unusable, same winner) == 1 (convention A)", disagree_A(bad_r, P_[2][ms[40]["match_id"]]) == 1)
        P3u = dict(P_[3])
        for m in ms[40:45]:
            rr_ = dict(P3u[m["match_id"]]); rr_["finish1"] = "length"; P3u[m["match_id"]] = rr_
        su = epoch2_compute(ms, {**P_, 3: P3u}, {}, B=10, seeds=(42,))
        check("M10: 5 unusable pass-3 rows: A counts them (4 + 5 = 9/300), B drops them (4/295)",
              su["p23"]["D"] == 9 and su["p23"]["n"] == 300 and su["p23"]["DB"] == 4 and su["p23"]["nB"] == 295, (su["p23"]["D"], su["p23"]["DB"], su["p23"]["nB"]))
        # M15: C0 (b) - the pass 1 -> 2 floor must reproduce 26/300 in the analysis
        P2f = dict(P_[2]); r_ = dict(P2f[ms[100]["match_id"]]); r_["winner"] = "TIE"; P2f[ms[100]["match_id"]] = r_
        sf = epoch2_compute(ms, {**P_, 2: P2f}, {}, B=10, seeds=(42,))
        check("M15: a 27/300 pass 1 -> 2 floor FAILS C0 (b) and voids C1", not sf["valid"] and not sf["c0"][1][1], sf["c0"][1])
        # D4: C0 (a) recomputes the set hash
        sa = epoch2_compute(ms_t, P_, {}, B=10, seeds=(42,))
        check("D4: C0 (a) recomputes the hash: a tampered set FAILS it", not sa["c0"][0][1] and not sa["valid"], sa["c0"][0])
        # 5. every registered branch EXECUTED on synthetic statistics
        base = epoch2_compute(ms, {1: _rows_of(1)[0], 2: _rows_of(2)[0], 3: _rows_of(3)[0], 4: None}, {}, B=30, seeds=(42, 43))
        epoch2_readout(base)                                                    # rung ABSENT, P3-P6 UND
        def variant(**kw):
            v = dict(base); v.update(kw); return v
        mk = lambda D, n=300, rev=0: dict(n=n, D=D, d=D / n, dA={}, nB=n, DB=D, dB=D / n, n_dec=200, rev=rev, half={"contested": (D // 2, 150), "cross": (D - D // 2, 150)})
        se = {"d32": 0.017, "d43": 0.017, "Delta": 0.02}
        for d32, d43, rev, valid, rung, unus in ((45, 10, 0, True, "VALID", 0), (20, 40, 3, True, "VALID", 0), (20, 25, 0, True, "VALID", 0),
                                                 (20, 25, 0, False, "VALID", 9), (20, 25, 0, True, "INVALID", 0), (60, 5, 4, True, "VALID", 0),
                                                 (20, 25, 0, True, "VALID", 9)):
            v = variant(p23=mk(d32, rev=rev), p34=mk(d43, rev=rev), se=se, Delta=(d32 - d43) / 300, valid=valid, rung=rung,
                        rung_detail="synthetic", calls=1200, unusable_calls=unus, foreign_fp=[] if valid else ["azure:x"])
            epoch2_readout(v)
        epoch2_readout(variant(p23=None))
        ab = mk(42)                                                             # A: 42/300 = 0.140 -> ALARM
        ab.update(nB=290, DB=32, dB=32 / 290)                                   # B: 32/290 = 0.110 -> NO ALARM (10 unusable pairs)
        txt_ab, res_ab = epoch2_readout(variant(p23=ab, p34=mk(25), se=se, Delta=17 / 300, valid=True, rung="VALID",
                                                rung_detail="synthetic", calls=1200, unusable_calls=10, foreign_fp=[]))
        check("A and B DISAGREE on the alarm: both recorded, A decides (ALARM)",
              res_ab["state"] == "ALARM" and "ALARM STATE: ALARM" in txt_ab.split("\n") and "A AND B DISAGREE ON THE ALARM" in txt_ab
              and "convention B would read NO ALARM" in txt_ab, [l for l in txt_ab.split("\n") if "C1" in l or "DISAGREE" in l])
        write_epoch2("x\n", False, 12)
        # 6. a tampered cache of record is refused (last: it breaks the fixture file)
        open(cache_path(2), "ab").write(b"\0")
        check("a cache of record that no longer hashes to its pin REFUSES", refuses(pin_old_caches, "selftest tamper", _want="[PIN]"))
        missing = sorted(EPOCH2_BRANCHES - EPOCH2_HIT)
        check("every criterion / prediction / falsifier / write branch executed (%d of %d)" % (len(EPOCH2_HIT & EPOCH2_BRANCHES), len(EPOCH2_BRANCHES)),
              not missing, missing)
    finally:
        sqlite3.connect = _TRUE_CONNECT
        socket.socket.connect = saved_sock
        rr.call_judge_full, rr.load_env = saved_rr
        for k, v in saved.items(): g[k] = v
    print("[SELFTEST-EPOCH2] %s" % ("%d check(s) FAILED: %s" % (len(fails), fails) if fails else
                                    "all checks passed; 0 calls, nothing of record opened, tmp %s" % tmp))
    return 1 if fails else 0


# ── G17-CANARY (RP21), the v1 leg: epoch 3 = pass 5 (2026-10-01 build; zero calls) ─────────────────────────────────────
# [ADDED 2026-10-01 by the engine-coder, insertion only: every sentence and every pass-1..4 code path above is unchanged; the four
# dispatch lines (open_cache's admitted passes, dry_run, run, the CLI) route --pass 5 here and nowhere else.]
# BUILT TO the registrable draft docs/agents/plans/2026-10-02_rp21_rp20_drafts.md section 1 (commit 41cd5cbd), its INSTRUMENT
# "v1 leg" and section 3 row "v1 epoch-3 code" items (1)-(11). RP21 IS NOT REGISTERED at build time: the registered text binds,
# and any difference is a delta of this code before its READY (READY_canary_epoch3.md, which C3 of
# docs/reviews/READY_canary_analyze_fix_delta.md requires: new pass ids are new code).
#   python tools/analysis/canary_baseline.py --selftest-epoch3                 (0 calls; temp fixtures; a FAKE POSTER; socket guard)
#   python tools/analysis/canary_baseline.py --mutants-epoch3                  (each mutant below run against the selftest)
#   python tools/analysis/canary_baseline.py --dry-run --pass 5 [--pilot 12]   (0 calls: pins, pre-flight, TRANSPORT PREFLIGHT, scan,
#                                                                              anchors, the day-ledger budget printed)
#   python tools/analysis/canary_baseline.py --pass 5 --pilot 12 --go --budget 24      (not before 2026-10-08; the committed READY)
#   python tools/analysis/canary_baseline.py --pass 5 --run --go --budget 576          (REFUSED unless the pilot is cached and <= 5%)
#   python tools/analysis/canary_baseline.py --analyze-epoch3                  (-> canary_epoch3_outcome.txt, WRITE-ONCE, complete only)
# (1) EPOCH3_PASSES = (5,). (2) Passes 3 and 4 are CLOSED caches of record, sha256 = their blobs at a1d27e9 (the CANARY-EPOCH2-RUNG
# outcome commit): pass 3 a45e966d..., pass 4 4612ee6a...; passes 1 / 2 keep their pins; all four are checked before and after
# every epoch-3 launch, dry-run and analysis. (3) PRE-FLIGHT (read-only): passes 1-4 complete under the protocol of record and the
# three floors REPRODUCED from the caches under convention A: 26/300 (1->2), 21/300 (2->3), 28/300 (3->4); every pass-4 call
# fingerprinted. (4) DATE GATE: no pass-5 post before NOT_BEFORE_PASS5 = 2026-10-08 (local date). (5) CEILING 630 calls (pass 5,
# the pilot inside; transport margin 5%) against the REGISTERED 600 (P6). (6) THE BUDGET reads the POSTING-DAY ledger
# experiment_results/day_calls_<today>.json (every test's rows) instead of the 4,060 night constant: refused, never trimmed, on
# (i) own calls (the larger of the pass-5 cache x 2 and this test's rows in every day ledger) + this launch > 630; (ii) the
# 4,000-match rule; (iii) THE DAY CAP: today's ledger total + this launch > 14,000; (iv) --go without an explicit --budget, or this
# launch's planned calls > --budget. Printed on both branches. The --budget is also a HARD CAP inside the poster (the post that
# would exceed it is never made) and a local-date change stops the launch (the 64ff708 rollover class). (7) --analyze-epoch3: C0,
# C1-v1 (THE ALARM: d53 = pass 3 vs pass 5, convention A, the POINT decides, integer rule D x 1000 >= 138 x n), d54 / pairwise
# d(1..5) / reversals DESCRIPTIVE, P5, P6, the falsifier; write-once canary_epoch3_outcome.txt (mode "x"); incomplete readouts go to
# a TIMESTAMPED *_PILOT / *_partial file, never overwritten (READY_canary_analyze_fix_delta D3). (8) The DB guard: the ONLY writable
# file is canary_baseline_pass5.db. (9) The RP32a transport preflight (archv2_pilot.pilot.load_transport + transport_preflight,
# imported, not retyped) runs inside --dry-run and before any post, and REFUSES. (10) READY gate: docs/reviews/READY_canary_epoch3.md,
# committed and clean, whose FIRST verdict line names G17-CANARY-V1E3 and this script's LF sha16. (11) --selftest-epoch3.
# MUTANT TABLE (--mutants-epoch3; KILLED = the selftest exits non-zero with a FAIL line; the run of record is in the commit message):
#   alarm_strict (> for >=) | d53_from_p4 (C1 read on pass 4 vs 5) | conv_b_decides | no_date_gate | day_cap_off | budget_cap_off
#   (the hard cap not enforced in the poster) | preflight_skipped (no transport preflight in the dry-run) | floors_off (pre-flight
#   floors not checked) | write_mode_w (the outcome of record opened "w") | p5_range_wide (P5 read on [0.05, 0.138]) | c0_date_off
#   (C0 (f) the start-date check dropped) | falsifier_silent (ALARM prints no falsifier line)
TEST_EPOCH3 = "G17-CANARY-V1E3"
REGISTRATION_EPOCH3 = ("RP21 G17-CANARY v1 leg (C0, C1-v1, P5, P6, falsifier): NOT REGISTERED at build time; built to the draft "
                       "docs/agents/plans/2026-10-02_rp21_rp20_drafts.md section 1 (41cd5cbd)")
EPOCH3_PASSES = (5,)
CLOSED_CACHE_SHA256_E3 = {3: "a45e966d2fc1f7e0df85a7c2bed9cf35efa2d3ffbc7ada7ca22076b4e74ea347",   # blob at a1d27e9 (pass 3 of record)
                          4: "4612ee6a4466918bbecb242903d3a9ea15ed6508437b6a96bd2814f3294aaa4a"}   # blob at a1d27e9 (pass 4 of record)
FLOORS_E3 = {(1, 2): 26, (2, 3): 21, (3, 4): 28}       # convention A, the record (CANARY-BASELINE; CANARY-EPOCH2-RUNG d32, d43)
NOT_BEFORE_PASS5 = datetime.date(2026, 10, 8)
EPOCH3_CEILING = 630
EPOCH3_REGISTERED_CALLS = 600
DAY_CAP = 14000
MATCH_RULE_E3 = 4000
P5_RANGE = (0.050, 0.125)
P6_UNUSABLE_MAX = 3
OUT_EPOCH3 = os.path.join(X12DIR, "canary_epoch3_outcome.txt")
OUT_EPOCH3_STEM = os.path.join(X12DIR, "canary_epoch3_outcome")
READY_EPOCH3 = os.path.join(ROOT, "docs", "reviews", "READY_canary_epoch3.md")
EPOCH3_REG_SUPPORT = ("REGISTERED SUPPORT (draft): 300 matches over 279 questions; DEFF 1.169 (measured, CANARY-EPOCH2-RUNG); n_eff 256.6; "
                      "SE 0.01759 at 0.087; MDE80 0.0493; prediction 0.087 to the bar 0.138 = 0.051 > 0.0493: SCOREABLE (thin, 0.2pp).")
E3_MUTANT = os.environ.get("CANARY_E3_MUTANT") or None
E3_MUTANTS = ("alarm_strict", "d53_from_p4", "conv_b_decides", "no_date_gate", "day_cap_off", "budget_cap_off", "preflight_skipped",
              "floors_off", "write_mode_w", "p5_range_wide", "c0_date_off", "falsifier_silent")
EPOCH3_BRANCHES = frozenset(
    ["C0:PASS", "C0:FAIL", "C1:ALARM", "C1:NO_ALARM", "C1:UND_VALIDITY", "C1:AB_AGREE", "C1:AB_DISAGREE",
     "P5:HELD", "P5:FAILED", "P5:UND", "P6:HELD", "P6:FAILED", "P6:UND",
     "FALS:ALARM_FIRES", "FALS:NOT_FIRED", "FALS:NOT_EVALUATED", "WRITE:RECORD", "WRITE:PARTIAL", "WRITE:REFUSED_EXISTS"])
EPOCH3_HIT = set()


def e3hit(tag):
    if tag not in EPOCH3_BRANCHES:
        raise SystemExit("[BRANCH] undeclared epoch-3 branch tag %r" % tag)
    EPOCH3_HIT.add(tag)


def today_e3():
    """The posting date (local). The selftest replaces this function; nothing else reads the clock for the date gate."""
    return datetime.date.today()


def day_str_e3():
    return today_e3().strftime("%Y-%m-%d")


def closed_pins_e3():
    out = dict(PASS_CACHE_SHA256)
    out.update(CLOSED_CACHE_SHA256_E3)
    return out


def pin_caches_e3(when):
    """Passes 1-4 (all closed caches of record at epoch 3): sha256 against the pins, printed on both branches; a mismatch or a
    non-empty -wal / -journal REFUSES."""
    pins = closed_pins_e3()
    got = {}
    for n in (1, 2, 3, 4):
        p = cache_path(n)
        got[n] = file_sha256(p) if os.path.exists(p) else None
        for suf in ("-wal", "-journal"):
            if os.path.exists(p + suf) and os.path.getsize(p + suf) > 0:
                raise SystemExit("[PIN-E3] %s%s is non-empty: a writer touched a cache of record (%s)" % (rel(p), suf, when))
    ok = all(got[n] == pins[n] for n in (1, 2, 3, 4))
    print("[PIN-E3] %s: %s -> %s" % (when, " | ".join("pass %d %s (pin %s)" % (n, (got[n] or "MISSING")[:16], pins[n][:16])
                                                     for n in (1, 2, 3, 4)), "UNCHANGED" if ok else "MISMATCH"), flush=True)
    if not ok:
        raise SystemExit("[PIN-E3] REFUSED: a cache of record does not hash to its pin (%s); nothing is posted or read." % when)
    return got


def _pair_e3(P, a, b, ids, strat):
    if P.get(a) is None or P.get(b) is None:
        return None
    common = [i for i in ids if i in P[a] and i in P[b]]
    dA = {i: disagree_A(P[a][i], P[b][i]) for i in common}
    okB = [i for i in common if not _bad(P[a][i]) and not _bad(P[b][i])]
    dB = sum(int(P[a][i]["winner"] != P[b][i]["winner"]) for i in okB)
    dec = [i for i in common if _decisive(P[a][i]) and _decisive(P[b][i])]
    rev = sum(1 for i in dec if P[a][i]["winner"] != P[b][i]["winner"])
    return dict(n=len(common), D=sum(dA.values()), d=sum(dA.values()) / max(1, len(common)), dA=dA, nB=len(okB), DB=dB,
                dB=dB / max(1, len(okB)), n_dec=len(dec), rev=rev,
                half={h: (sum(dA[i] for i in common if strat[i] == h), sum(1 for i in common if strat[i] == h)) for h in ("contested", "cross")})


def preflight_epoch3(meta):
    """Read-only. Passes 1-4 complete under the protocol of record; the three floors REPRODUCED (convention A); every pass-4 call
    fingerprinted. Returns the refusals (empty list = go)."""
    probs = preflight_pass2(meta)                         # pass 1 complete under the same protocol / max_tokens / temperature / set
    P = {}
    for k in (1, 2, 3, 4):
        got = _rows_of(k)
        if got is None:
            probs.append("pass %d cache %s is missing" % (k, rel(cache_path(k))))
            continue
        P[k] = got[0]
        if len(got[0]) != N_SET:
            probs.append("pass %d holds %d of %d verdicts" % (k, len(got[0]), N_SET))
        if k >= 2:
            for key, v in current_meta(meta).items():
                if key != "pass_no" and got[1].get(key) != v:
                    probs.append("%s: pass %d recorded %r | now %r" % (key, k, got[1].get(key), v))
    ids = sorted(set().union(*[set(v) for v in P.values()])) if P else []
    for (a, b), want in sorted(FLOORS_E3.items()):
        if a in P and b in P:
            d = sum(disagree_A(P[a][i], P[b][i]) for i in P[a] if i in P[b])
            n = sum(1 for i in P[a] if i in P[b])
            print("[FLOOR-E3] pass %d -> %d: %d/%d (record %d/%d) -> %s" % (a, b, d, n, want, N_SET,
                                                                           "REPRODUCED" if (d, n) == (want, N_SET) else "DIFFERS"), flush=True)
            if (d, n) != (want, N_SET) and E3_MUTANT != "floors_off":
                probs.append("the pass %d -> %d floor reproduces as %d/%d, not the recorded %d/%d (C0)" % (a, b, d, n, want, N_SET))
    if 4 in P:
        fp = Counter(r.get(c) for r in P[4].values() for c in ("provider1", "provider2"))
        if set(fp) - {EXPECTED_FINGERPRINT, REFUSAL_FINGERPRINT}:
            probs.append("pass 4 fingerprints %s are not all %s" % (dict(fp), EXPECTED_FINGERPRINT))
    del ids
    return probs


def date_gate_e3():
    """(ok, line): no pass-5 post before NOT_BEFORE_PASS5 (local date)."""
    t = today_e3()
    ok = t >= NOT_BEFORE_PASS5 or E3_MUTANT == "no_date_gate"
    return ok, "[DATE-E3] today %s | pass 5 allowed from %s -> %s" % (t, NOT_BEFORE_PASS5, "OPEN" if ok else "REFUSED (too early)")


def _parse_ready(text, sha, test):
    """parse_ready_epoch2's rule for any test id: the FIRST verdict line names the test and the LF sha16; no NOT READY anywhere."""
    import re
    body, fence = [], None
    for ln in text.split("\n"):
        st = ln.lstrip()
        if fence is None and (st.startswith("```") or st.startswith("~~~")):
            fence = st[:3]; body.append("")
        elif fence is not None:
            if st.startswith(fence): fence = None
            body.append("")
        else:
            body.append(ln)
    text = "\n".join(body)
    lines = list(re.finditer(r"^[ \t]*#{0,6}[ \t]*\**[ \t]*(NOT READY|READY-WITH-CONDITIONS|READY)\b[ \t]*\**[ \t]*:", text, re.M))
    if not lines:
        return None, ["no verdict line"]
    first = text[lines[0].start():].split("\n", 1)[0]
    reasons = []
    if any(x.group(1) == "NOT READY" for x in lines): reasons.append("a NOT READY verdict")
    if test not in first: reasons.append("the verdict line does not name %s" % test)
    if sha not in first: reasons.append("the verdict line does not name this script's LF sha16 %s" % sha)
    return lines[0].group(1), reasons


def gate_state_epoch3(go):
    exists = os.path.exists(READY_EPOCH3)
    tracked, clean = git_tracked_clean(READY_EPOCH3) if exists else (False, False)
    verdict, reasons = (_parse_ready(open(READY_EPOCH3, encoding="utf-8").read(), script_hash_lf(), TEST_EPOCH3) if exists
                        else (None, ["READY missing"]))
    ok = bool(go and exists and tracked and clean and not reasons)
    return ok, "--go %s | %s %s (tracked %s, clean %s) | verdict %r%s" % (bool(go), rel(READY_EPOCH3), "exists" if exists else "MISSING",
                                                                           tracked, clean, verdict, "" if not reasons else " | REFUSES: " + "; ".join(reasons))


def go_gate_epoch3(what, go):
    ok, s = gate_state_epoch3(go)
    print("[GATE-E3] %s: %s -> %s" % (what, s, "OPEN" if ok else "REFUSED"), flush=True)
    if not ok:
        raise SystemExit("[GATE-E3] %s REFUSED (0 calls, no database opened): %s" % (what, s))


def budget_gate_epoch3(planned, what, budget=None, refuse=True):
    """(i) own ceiling 630 (pass-5 cache x 2 vs this test's rows in every day ledger, the larger); (ii) the 4,000-match rule; (iii) THE
    DAY CAP: today's POSTING-DAY ledger (all tests) + this launch <= 14,000; (iv) a posting launch needs --budget and planned <= it.
    Printed on both branches; REFUSED, never trimmed."""
    own_c = 0
    p5 = _rows_of(5)
    if p5 is not None:
        own_c = 2 * len(p5[0])
    own_l = atl.ledger_calls(TEST_EPOCH3, LEDGER_DIR)
    own = max(own_c, own_l)
    day = day_str_e3()
    day_path = atl.day_ledger_path(LEDGER_DIR, day)
    day_total = sum(int(r["calls"]) for r in atl._rows(day_path))
    after = own + planned
    breaches = []
    if after > EPOCH3_CEILING:
        breaches.append("(i) %s would reach %d calls > its ceiling %d" % (TEST_EPOCH3, after, EPOCH3_CEILING))
    if (after + 1) // 2 > MATCH_RULE_E3:
        breaches.append("(ii) %d matches > the %d-match rule" % ((after + 1) // 2, MATCH_RULE_E3))
    if day_total + planned > DAY_CAP and E3_MUTANT != "day_cap_off":
        breaches.append("(iii) the day cap: %s holds %d calls + this launch %d = %d > %d" % (os.path.basename(day_path), day_total, planned,
                                                                                           day_total + planned, DAY_CAP))
    if refuse and planned > 0:
        if budget is None:
            breaches.append("(iv) a posting launch needs an explicit --budget (calls)")
        elif planned > budget:
            breaches.append("(iv) this launch plans %d calls > --budget %d" % (planned, budget))
    print("[ACCOUNT-E3] %s (%s): (i) own %d (cache %d, ledgers %d) + %d = %d of %d | (ii) matches %d of %d | (iii) day %s: %d + %d = %d of %d "
          "| (iv) budget %s -> %s" % (TEST_EPOCH3, what, own, own_c, own_l, planned, after, EPOCH3_CEILING, (after + 1) // 2, MATCH_RULE_E3,
                                     day, day_total, planned, day_total + planned, DAY_CAP, budget, "OK" if not breaches else "REFUSED: " + "; ".join(breaches)),
          flush=True)
    if breaches and refuse:
        raise SystemExit("[ACCOUNT-E3] REFUSED, not trimmed (0 calls posted): " + "; ".join(breaches))
    return dict(own=own, own_cache=own_c, own_ledger=own_l, day_total=day_total, day=day, breaches=breaches)


def transport_e3(out=print):
    """RP32a: archv2_pilot.pilot.load_transport (rejudge_reasoning.load_env against the data root's .env) then transport_preflight,
    IMPORTED (not retyped); a failure is a SystemExit before any cache, post or ledger row."""
    if E3_MUTANT == "preflight_skipped":
        return None
    from archv2_pilot import pilot as PL
    PL.load_transport(out=out)
    return PL.transport_preflight(out=out)


class _BudgetStop(Exception):
    pass


def _post_epoch3(jobs, con, all_ms, workers, budget, day, what):
    """Post the jobs through rr.call_judge_full (counted); a FOREIGN fingerprint stops the run (nothing cached for that match); the
    --budget is a hard cap (the post that would exceed it is never made); a local-date change stops the launch. The ledger append is
    in the CALLER's finally. Returns (ok, err, posted list, stop reason)."""
    lock = threading.Lock(); ok = err = 0; finishes = Counter(); halt = threading.Event(); mismatch = []; stop = []
    index = {m["match_id"]: i for i, m in enumerate(all_ms)}
    posted = []
    real_post = rr.call_judge_full

    def counted(*a, **k):
        with lock:
            if len(posted) >= budget and E3_MUTANT != "budget_cap_off":
                raise _BudgetStop("the --budget %d is reached: this post is NOT made" % budget)
            if day_str_e3() != day:
                raise _BudgetStop("the local date changed (%s -> %s): the launch stops; relaunch on the new day under its own guard"
                                  % (day, day_str_e3()))
            posted.append(1)
        return real_post(*a, **k)

    def one(job):
        m, ref, system, u1, u2 = job
        if halt.is_set(): raise FingerprintMismatch("match %d: not posted, the run is stopping" % m["match_id"])
        raw1, p1, k1, _, f1, msg1 = rr.call_judge_full(system, u1)
        try: check_fingerprint(m, 1, p1, f1)
        except FingerprintMismatch as e: mismatch.append(str(e)); halt.set(); raise
        if halt.is_set(): raise FingerprintMismatch("match %d: order 2 not posted, the run is stopping" % m["match_id"])
        raw2, p2, k2, _, f2, msg2 = rr.call_judge_full(system, u2)
        try: check_fingerprint(m, 2, p2, f2)
        except FingerprintMismatch as e: mismatch.append(str(e)); halt.set(); raise
        raw1, raw2 = rr.strip_think(raw1 or ""), rr.strip_think(raw2 or "")
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        if f1 in ("length", "content_filter"): v1 = "INVALID"
        if f2 in ("length", "content_filter"): v2 = "INVALID"
        w, flip, inv = rj.combine_orders(v1, v2)
        return (m["match_id"], m["model_a"], m["model_b"], m["node_id"], m["qid"], m["anchor"], ref[0], int(ref[2]), v1, v2, c1, c2,
                {"Model A": m["model_a"], "Model B": m["model_b"]}.get(w, w), int(flip), int(inv), raw1, raw2, time.time(),
                f1, f2, k1, k2, m["stratum"], m["pair_kind"], p1, p2,
                (msg1 or {}).get("_response_id"), (msg2 or {}).get("_response_id"), _sha16(system), _sha16(u1), _sha16(u2), u1, u2,
                index[m["match_id"]], script_hash_lf())
    rr.call_judge_full = counted
    try:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(one, j): j for j in jobs}
            for i, f in enumerate(as_completed(futs), 1):
                try: row = f.result()
                except FingerprintMismatch as e:
                    halt.set(); ex.shutdown(wait=False, cancel_futures=True)
                    stop.append("[FINGERPRINT] %s" % (mismatch[0] if mismatch else e)); break
                except _BudgetStop as e:
                    halt.set(); ex.shutdown(wait=False, cancel_futures=True)
                    stop.append("[BUDGET-STOP] %s" % e); break
                except Exception as e:
                    err += 1; print("  ERROR match %s: %s" % (futs[f][0]["match_id"], str(e)[:120]), flush=True); continue
                with lock:
                    con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 35), row); con.commit()
                ok += 1; finishes[row[18]] += 1; finishes[row[19]] += 1
                if i % 25 == 0 or i == len(jobs):
                    print("  %d/%d (ok %d, err %d) | finish_reason %s" % (i, len(jobs), ok, err, dict(finishes)), flush=True)
    finally:
        rr.call_judge_full = real_post
    return ok, err, posted, stop


def run_epoch3(pilot, workers, override_guard=False, go=False, full=False, budget=None):
    """Pass 5. Order of refusals: the mode, the date gate, the record, the gate (before any database), --budget, the DB guard, the pins,
    the set, the pre-flight, the body source, THE TRANSPORT PREFLIGHT, the cache's run_meta, the pilot rule, the guard, the scan, the
    budget (the day ledger); then the posting (hard cap, rollover stop), the ledger append in a `finally`, the pins again."""
    if NPASS not in EPOCH3_PASSES:
        raise SystemExit("[PASS] run_epoch3 called for pass %d" % NPASS)
    if not pilot and not full:
        raise SystemExit("[MODE] a posting launch needs --pilot 12 or --run (and --go, --budget)")
    if pilot and pilot != PILOT_N:
        raise SystemExit("[MODE] --pilot %d REFUSED: the registered pilot is %d matches" % (pilot, PILOT_N))
    if override_guard:
        raise SystemExit("[MODE] --override-guard is REFUSED on pass 5")
    ok_date, dline = date_gate_e3()
    print(dline, flush=True)
    if not ok_date:
        raise SystemExit("[DATE-E3] REFUSED: pass 5 is not posted before %s (0 calls, no database opened)" % NOT_BEFORE_PASS5)
    if os.path.exists(OUT_EPOCH3):
        raise SystemExit("[RECORD] %s exists: the epoch-3 outcome of record is written and closed; nothing more is posted." % rel(OUT_EPOCH3))
    what = "--pass 5 %s" % ("--pilot %d" % pilot if pilot else "--run")
    go_gate_epoch3(what, go)
    if budget is None:
        raise SystemExit("[ACCOUNT-E3] REFUSED: a posting launch needs an explicit --budget (calls); 0 calls posted")
    install_db_guard(writable=cache_path(5))
    pins_before = pin_caches_e3("before " + what)
    matches, meta = freeze_set()
    verify_set(matches, meta)
    probs = preflight_epoch3(meta)
    if probs:
        raise SystemExit("[PASS-5 PRE-FLIGHT] REFUSED before any call:\n  %s" % "\n  ".join(probs))
    print("[PASS-5 PRE-FLIGHT] read-only: go", flush=True)
    configure_rr(); assert_body_source()
    transport_e3()                                        # RP32a: refuses before any cache, post or ledger row
    day = day_str_e3()
    all_ms = matches
    if pilot: matches = matches[:pilot]
    con = open_cache(5); pin_meta(con, meta)
    try:
        done = {r[0] for r in con.execute("SELECT match_id FROM verdicts")}
        if full:
            miss = [m["match_id"] for m in all_ms[:PILOT_N] if m["match_id"] not in done]
            if miss:
                raise SystemExit("[RUN] REFUSED: the pass-5 pilot (the first %d matches of the set) is not cached (%d missing)" % (PILOT_N, len(miss)))
        todo = [m for m in matches if m["match_id"] not in done]
        if done:
            n, bad = cached_guard(con); rate = bad / n
            print("[GUARD] cached %d | invalid or non-terminated %d (%.1f%%) -> %s" % (n, bad, 100 * rate, "OK" if rate <= GUARD_RATE else "ABOVE 5%"), flush=True)
            if rate > GUARD_RATE and todo:
                raise SystemExit("[GUARD] refusing to post the remaining %d matches: %d of %d cached matches are invalid or non-terminated (%.1f%% > 5%%)."
                                 % (len(todo), bad, n, 100 * rate))
        jobs = build_jobs(todo)
        scan = scan_payloads(jobs)
        print("[SCAN] pre-call full-payload scan over %d payloads -> PASS (decomposition %d, frame identical %d, clean %d)"
              % (scan["payloads"], scan["decomposed"], scan["frame_same"], scan["frame_clean"]), flush=True)
        planned = 2 * len(jobs)
        budget_gate_epoch3(planned, what, budget=budget)
        print("[PLAN-E3] %s: matches to post %d | calls %d (dual order) | cached %d | budget %d (hard cap) | posting day %s | order sha16 %s"
              % (what, len(jobs), planned, len(matches) - len(todo), budget, day, order_sha([m["match_id"] for m in matches])), flush=True)
        posted = []
        stop = []
        err = 0
        try:
            ok, err, posted, stop = _post_epoch3(jobs, con, all_ms, workers, budget, day, what)
        finally:
            atl.append(TEST_EPOCH3, what, len(posted), LEDGER_DIR, day=day)
            print("done: %d calls posted (errors are posted calls, counted, never cached)%s" % (len(posted), " | STOPPED: " + stop[0] if stop else ""),
                  flush=True)
        truncation_report(con)
        if pin_caches_e3("after " + what) != pins_before:
            raise SystemExit("[PIN-E3] a cache of record CHANGED during %s" % what)
        if stop:
            raise SystemExit(stop[0])
        if pilot:
            n, bad = cached_guard(con)
            n += err; bad += err
            if bad > GUARD_RATE * max(1, n):
                raise SystemExit("[GUARD] the pass-5 pilot FAILED its truncation guard (%d of %d unusable > 5%%): --run is refused" % (bad, n))
    finally:
        con.close()
    return 0


def dry_run_epoch3(pilot):
    """0 calls, nothing written: the pins, the set, the pre-flight (printed), the date gate (printed), the body source, THE TRANSPORT
    PREFLIGHT (refuses), the scan, the anchor, the ceiling, the day-ledger budget (printed), the READY gate (printed)."""
    install_db_guard(writable=None)
    pin_caches_e3("dry-run --pass 5")
    matches, meta = freeze_set()
    verify_set(matches, meta)
    all_ms = matches
    if pilot: matches = matches[:pilot]
    configure_rr(); assert_body_source()
    line = transport_e3()
    print("[DRY-RUN-E3] transport: %s" % (line or "NO PREFLIGHT RUN"), flush=True)
    probs = preflight_epoch3(meta)
    print("[DRY-RUN-E3] pass-5 pre-flight (read-only; passes 1-4 complete, floors 26/21/28 reproduced): %s"
          % ("would GO" if not probs else "would REFUSE: " + "; ".join(probs)), flush=True)
    print(date_gate_e3()[1], flush=True)
    jobs = build_jobs(matches)
    scan = scan_payloads(jobs)
    anchor = hashlib.sha256()
    for m, ref, system, u1, u2 in jobs:
        anchor.update(("%d|" % m["match_id"]).encode("utf-8") + system.encode("utf-8") + u1.encode("utf-8") + u2.encode("utf-8"))
    print("[ANCHOR-E3] payload anchor sha16 %s over %d matches | posting order sha16 %s | scan payloads %d -> PASS"
          % (anchor.hexdigest()[:16], len(jobs), order_sha([m["match_id"] for m in matches]), scan["payloads"]), flush=True)
    print("[CEILING-E3] pass 5: %d matches x 2 orders = %d calls registered (pilot %d matches = %d calls INSIDE it) | ceiling %d"
          % (len(all_ms), 2 * len(all_ms), PILOT_N, 2 * PILOT_N, EPOCH3_CEILING), flush=True)
    budget_gate_epoch3(2 * len(all_ms), "--dry-run --pass 5 (a full pass, 0 posted)", budget=None, refuse=False)
    print("[GATE-E3] (a dry run is never gated; a posting launch needs --go, --budget and the committed READY) %s" % gate_state_epoch3(False)[1])
    pin_caches_e3("end of dry-run --pass 5")
    print(dbguard_line())
    print("[DRY-RUN-E3] %d payloads assembled, 0 posted" % (2 * len(jobs)))
    return 0


def epoch3_compute(set_ms, P, meta_of, B=EPOCH2_BOOT, seeds=(EPOCH2_SEED,) + EPOCH2_EXTRA_SEEDS):
    ids = [m["match_id"] for m in set_ms]
    qid = {m["match_id"]: m["qid"] for m in set_ms}
    strat = {m["match_id"]: m["stratum"] for m in set_ms}
    s = dict(n_set=len(ids), n_q=len(set(qid.values())))
    sizes = Counter(qid.values())
    s["kish"] = sum(v * v for v in sizes.values()) / max(1, sum(sizes.values()))
    s["pairs"] = {(a, b): _pair_e3(P, a, b, ids, strat) for a in (1, 2, 3, 4, 5) for b in (1, 2, 3, 4, 5) if a < b}
    s["p35"] = s["pairs"][(4, 5)] if E3_MUTANT == "d53_from_p4" else s["pairs"][(3, 5)]
    s["p45"] = s["pairs"][(4, 5)]
    r5 = P.get(5)
    fp = Counter(r.get(c) for r in (r5 or {}).values() for c in ("provider1", "provider2"))
    s["fp"] = dict(fp)
    s["foreign_fp"] = sorted(str(x) for x in set(fp) - {EXPECTED_FINGERPRINT, REFUSAL_FINGERPRINT})
    pilot_ids = ids[:PILOT_N]
    s["pilot5"] = (sum(1 for i in pilot_ids if r5 and i in r5 and _bad(r5[i])), sum(1 for i in pilot_ids if r5 and i in r5))
    started = (meta_of.get(5) or {}).get("started")
    try:
        st_date = datetime.datetime.strptime(started, "%Y-%m-%d %H:%M:%S").date() if started else None
    except ValueError:
        st_date = None
    h = set_hash(set_ms)
    floors = []
    for (a, b), want in sorted(FLOORS_E3.items()):
        pr = s["pairs"][(a, b)]
        floors.append(bool(pr and pr["D"] == want and pr["n"] == N_SET))
    c0 = [("(a) set hash %s" % SET_HASH_OF_RECORD, h == SET_HASH_OF_RECORD, "recomputed %s" % h),
          ("(b) floors 26/300 (1->2), 21/300 (2->3), 28/300 (3->4) reproduced", all(floors),
           ", ".join("%s/%s" % ((s["pairs"][k]["D"], s["pairs"][k]["n"]) if s["pairs"][k] else ("-", "-")) for k in sorted(FLOORS_E3))),
          ("(c) every pass-5 call fingerprinted %s" % EXPECTED_FINGERPRINT, bool(r5) and not s["foreign_fp"], "%s" % s["fp"]),
          ("(d) pass 5 complete", bool(r5 and len(r5) == N_SET), "%d of %d" % (len(r5) if r5 else 0, N_SET)),
          ("(e) the pass-5 pilot's truncation guard (<= 5%)", s["pilot5"][1] == PILOT_N and s["pilot5"][0] <= GUARD_RATE * PILOT_N,
           "%d of %d unusable" % s["pilot5"]),
          ("(f) pass 5 started on or after %s" % NOT_BEFORE_PASS5, E3_MUTANT == "c0_date_off" or bool(st_date and st_date >= NOT_BEFORE_PASS5),
           "started %s" % started)]
    s["c0"] = c0
    s["valid"] = all(ok for _l, ok, _d in c0)
    reads = []
    for sd in seeds:
        row = {}
        for key, pr in (("d53", s["p35"]), ("d54", s["p45"])):
            if pr is None:
                row[key] = None; continue
            byq = defaultdict(list)
            for i, v in pr["dA"].items():
                byq[qid[i]].append(v)
            row[key] = _boot_se(byq, B, sd)
        reads.append((sd, row))
    s["se"] = reads[0][1]; s["reads"] = reads
    if s["p35"]:
        d, n = s["p35"]["d"], s["p35"]["n"]
        bino = (d * (1 - d) / max(1, n)) ** 0.5
        s["deff53"] = (s["se"]["d53"] / bino) ** 2 if bino > 0 else float("nan")
    s["complete"] = bool(r5 and len(r5) == N_SET)
    s["calls"] = 2 * len(r5) if r5 else 0
    s["unusable_calls"] = sum(int(r["finish1"] in ("length", "content_filter") or r["vote1"] == "INVALID")
                              + int(r["finish2"] in ("length", "content_filter") or r["vote2_raw"] == "INVALID") for r in (r5 or {}).values())
    return s


def alarm_e3(D, n):
    """THE ALARM (registered rule, prog L9983 / L14931ff, RP21 C1-v1): d >= 0.138, THE POINT DECIDES, integer comparison."""
    if E3_MUTANT == "alarm_strict":
        return D * ALARM_DEN > ALARM_NUM * n
    return D * ALARM_DEN >= ALARM_NUM * n


def epoch3_readout(s):
    L = []; p = L.append
    p("=== %s | %s ===" % (TEST_EPOCH3, REGISTRATION_EPOCH3))
    p("  set %s (%d matches over %d questions, Kish %.3f) | judge %s | max_tokens %d | temperature %s | dual order, TIE on flip | "
      "convention A DECIDES (an unusable row in either pass = a disagreement; denominator the 300), B beside | script sha256-lf16 %s"
      % (SET_HASH_OF_RECORD, s["n_set"], s["n_q"], s["kish"], JUDGE, MAXTOK, temp_label(), script_hash_lf()))
    p("  [P-FAM] every number below is on pool %s (id-disjoint only): operational log / alarm only (RULING_w0_p2dca_family.md L176)" % POOL)
    p("")
    p("(C0) VALIDITY, FIRST:")
    for lab, ok, det in s["c0"]:
        p("     %-70s %s  %s" % (lab, "PASS" if ok else "FAIL", det))
    e3hit("C0:PASS" if s["valid"] else "C0:FAIL")
    p35 = s["p35"]
    p("")
    if p35 is None:
        e3hit("C1:UND_VALIDITY")
        p("(C1-v1) pass 5 absent: nothing is read.")
        p("ALARM STATE: UNDETERMINED")
        state = "UNDETERMINED"; alarm = False
    else:
        se = s["se"]["d53"]
        p("(C1-v1) THE ALARM: d53 = the share of the %d matches whose combined dual-order verdict differs between pass 3 and pass 5 = "
          "%d/%d = %.4f (convention A); convention B %d/%d = %.4f (%d pairs unusable in either pass dropped); question-clustered interval "
          "[%.3f, %.3f] (SE %.4f, B %d, seed %d; printed, NOT deciding: THE POINT DECIDES)"
          % (p35["n"], p35["D"], p35["n"], p35["d"], p35["DB"], p35["nB"], p35["dB"], p35["n"] - p35["nB"], p35["d"] - 1.96 * se,
             p35["d"] + 1.96 * se, se, EPOCH2_BOOT, EPOCH2_SEED))
        if E3_MUTANT == "conv_b_decides":
            alarm = p35["nB"] > 0 and alarm_e3(p35["DB"], p35["nB"])
        else:
            alarm = alarm_e3(p35["D"], p35["n"])
        alarm_b = p35["nB"] > 0 and alarm_e3(p35["DB"], p35["nB"])
        if not s["valid"]:
            state = "UNDETERMINED"; e3hit("C1:UND_VALIDITY")
            p("     C1-v1: UNDETERMINED BY VALIDITY (C0 failed); the point is printed and NOT scored")
        else:
            state = "ALARM" if alarm else "NO ALARM"; e3hit("C1:ALARM" if alarm else "C1:NO_ALARM")
            p("     C1-v1 (CONVENTION A DECIDES): %s (d53_A %d/%d = %.4f %s 0.138; one-sided; the point decides)"
              % (state, p35["D"], p35["n"], p35["d"], ">=" if alarm else "<"))
            p("     beside, deciding nothing: convention B would read %s (d53_B %d/%d = %.4f)"
              % ("ALARM" if alarm_b else "NO ALARM", p35["DB"], p35["nB"], p35["dB"]))
            if alarm_b != alarm:
                e3hit("C1:AB_DISAGREE")
                p("     A AND B DISAGREE ON THE ALARM: both are recorded (A %s, B %s) and CONVENTION A DECIDES: %s"
                  % ("ALARM" if alarm else "NO ALARM", "ALARM" if alarm_b else "NO ALARM", state))
            else:
                e3hit("C1:AB_AGREE")
                p("     A and B agree on the alarm.")
        p("ALARM STATE: %s" % state)
        p("     halves (descriptive): contested %d/%d, cross-tier %d/%d" % (p35["half"]["contested"] + p35["half"]["cross"]))
    p("")
    p("(DESCRIPTIVE) d54 (pass 4 vs pass 5) = %s | pairwise d(a, b) over passes 1-5 (convention A): %s"
      % ("%d/%d = %.4f (SE %.4f)" % (s["p45"]["D"], s["p45"]["n"], s["p45"]["d"], s["se"]["d54"]) if s["p45"] else "not read",
         ", ".join("d%d%d %s" % (b, a, "%d/%d" % (pr["D"], pr["n"]) if pr else "-") for (a, b), pr in sorted(s["pairs"].items()))))
    p("(DESCRIPTIVE) reversals (decisive in both, opposite winners): %s"
      % ", ".join("(%d, %d) %s" % (a, b, "%d of %d" % (pr["rev"], pr["n_dec"]) if pr else "-") for (a, b), pr in sorted(s["pairs"].items())))
    p("     bootstrap seeds %d-%d (C1-v1's point does not depend on them): %s"
      % (EPOCH2_EXTRA_SEEDS[0], EPOCH2_EXTRA_SEEDS[-1],
         ", ".join("%d:%s" % (sd, "/".join("%s %.4f" % (k, v) for k, v in row.items() if v is not None)) for sd, row in s["reads"][1:])))
    p("")
    p("SUPPORT. " + EPOCH3_REG_SUPPORT)
    if p35:
        de = s.get("deff53", float("nan"))
        p("  MEASURED: d53 SE %.4f (question-clustered), binomial %.4f, DEFF %.3f, n_eff %.1f, MDE80 (2.80 x SE) %.4f; distance of the point "
          "to the bar %.4f; Kish %.3f over %d questions"
          % (s["se"]["d53"], (p35["d"] * (1 - p35["d"]) / p35["n"]) ** 0.5, de, p35["n"] / de if de == de and de > 0 else float("nan"),
             2.80 * s["se"]["d53"], 0.138 - p35["d"], s["kish"], s["n_q"]))
    p("")
    p("PREDICTIONS (registered draft; scored on the points):")
    rv = s["valid"] and p35 is not None
    lo, hi = (P5_RANGE[0], 0.138) if E3_MUTANT == "p5_range_wide" else P5_RANGE
    preds = [("P5", "d53 = 0.085 [0.050, 0.125]", rv, lambda: lo <= p35["d"] <= hi, "%.4f" % p35["d"] if p35 else "-"),
             ("P6", "fingerprint on 600 of 600 (v1 leg); unusable 0 [0, 3]", rv,
              lambda: not s["foreign_fp"] and s["calls"] == EPOCH3_REGISTERED_CALLS and s["unusable_calls"] <= P6_UNUSABLE_MAX,
              "%d calls, foreign %s, unusable %d" % (s["calls"], s["foreign_fp"] or "none", s["unusable_calls"]))]
    for pid, text, scoreable, test, val in preds:
        tag = ("HELD" if bool(test()) else "FAILED") if scoreable else "UND"
        e3hit("%s:%s" % (pid, tag))
        p("  %s %-58s %-34s -> %s" % (pid, text, val, tag if tag != "UND" else "UNDETERMINED BY VALIDITY"))
    p("")
    if not (s["valid"] and p35 is not None):
        e3hit("FALS:NOT_EVALUATED"); p("FALSIFIER: NOT EVALUATED (C0 failed or pass 5 absent).")
    elif alarm:
        e3hit("FALS:ALARM_FIRES")
        if E3_MUTANT != "falsifier_silent":
            p("FALSIFIER FIRES: C1-v1 ALARM (d53 >= 0.138) fires plan Amendment 4 trigger (3); the standing reading \"the deployed judge's "
              "verdict floor is stable since 2026-09-22\" is OVERTURNED, and every judged number after pass 4 is flagged for re-read by insertion.")
    else:
        e3hit("FALS:NOT_FIRED"); p("FALSIFIER: NOT FIRED.")
    return "\n".join(L) + "\n", dict(state=state)


def write_epoch3(text, complete, n5):
    if not complete:
        e3hit("WRITE:PARTIAL")
        target = "%s_%s_%s.txt" % (OUT_EPOCH3_STEM, "PILOT" if n5 <= PILOT_N else "partial", time.strftime("%Y%m%d_%H%M%S"))
        k = 0
        while os.path.exists(target):
            k += 1; target = target[:-4] + "_%d.txt" % k
        with open(target, "x", encoding="utf-8", newline="\n") as f:
            f.write("NOT OF RECORD - pass 5 holds %d of %d; no line below is a registered reading.\n\n" % (n5, N_SET) + text)
        print("[ANALYZE-EPOCH3] incomplete: wrote %s; NO outcome of record." % rel(target), flush=True)
        return 2
    try:
        with open(OUT_EPOCH3, "w" if E3_MUTANT == "write_mode_w" else "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        e3hit("WRITE:REFUSED_EXISTS")
        print("[ANALYZE-EPOCH3] REFUSED: %s exists and is WRITE-ONCE; nothing was overwritten." % rel(OUT_EPOCH3), flush=True)
        return 3
    e3hit("WRITE:RECORD")
    print("[ANALYZE-EPOCH3] wrote %s (write-once)" % rel(OUT_EPOCH3), flush=True)
    return 0


def analyze_epoch3(boot=EPOCH2_BOOT):
    install_db_guard(writable=None)
    pins = pin_caches_e3("--analyze-epoch3 (start)")
    matches, meta = freeze_set()
    P, M = {}, {}
    for k in (1, 2, 3, 4, 5):
        got = _rows_of(k)
        P[k], M[k] = (got[0], got[1]) if got else (None, {})
    s = epoch3_compute(matches, P, M, B=boot)
    text, res = epoch3_readout(s)
    acc = budget_gate_epoch3(0, "outcome", refuse=False)
    text += ("ACCOUNTING (day ledger): %s %d of %d calls (cache %d, ledgers %d) | registered %d\n"
             % (TEST_EPOCH3, acc["own"], EPOCH3_CEILING, acc["own_cache"], acc["own_ledger"], EPOCH3_REGISTERED_CALLS))
    text += ("HEADER: %s | caches %s | pass 5 started %s | closed-cache pins %s | written %s\n"
             % (TEST_EPOCH3, ", ".join("%d:%s" % (k, "present" if P[k] is not None else "absent") for k in (1, 2, 3, 4, 5)),
                M[5].get("started"), {k: v[:16] for k, v in pins.items()}, time.strftime("%Y-%m-%d %H:%M:%S")))
    print(text, flush=True)
    rc = write_epoch3(text, s["complete"], len(P[5] or {}))
    if pin_caches_e3("--analyze-epoch3 (end)") != pins:
        raise SystemExit("[PIN-E3] a cache of record CHANGED during --analyze-epoch3")
    print(dbguard_line())
    return rc


def selftest_epoch3():
    """0 calls. Temp fixtures (passes 1-4 built with the floors 26 / 21 / 28 of record), the REAL transport loader on a fake .env,
    an injected FAKE poster, a socket guard. Every deciding path asserted by VALUE."""
    import socket, shutil, tempfile
    global NPASS, OUT_EPOCH3, OUT_EPOCH3_STEM, LEDGER_DIR, PASS_CACHE_SHA256, CLOSED_CACHE_SHA256_E3, READY_EPOCH3
    fails = []

    def check(name, cond, detail=""):
        ok = bool(cond)
        print("  %-100s %s%s" % (name, "OK" if ok else "FAIL", "" if ok else "  " + str(detail)[:260]), flush=True)
        if not ok: fails.append(name)

    def refuses(fn, *a, _want=None, **k):
        try:
            fn(*a, **k); return False
        except SystemExit as e:
            return _want is None or _want in str(e)

    print("[POOL] %s (selftest: synthetic fixtures; pool_guard is NOT called and no DB of record is opened)" % POOL)
    print("[SELFTEST-EPOCH3] %s | mutant %s | script sha256-lf16 %s | 0 calls | python -O: %s"
          % (TEST_EPOCH3, E3_MUTANT or "none", script_hash_lf(), not __debug__))
    g = globals()
    saved = {k: g[k] for k in ("NPASS", "OUT_EPOCH3", "OUT_EPOCH3_STEM", "LEDGER_DIR", "PASS_CACHE_SHA256", "CLOSED_CACHE_SHA256_E3",
                               "READY_EPOCH3", "cache_path", "freeze_set", "build_jobs", "go_gate_epoch3", "SET_HASH_OF_RECORD",
                               "pool_qids", "today_e3")}
    saved_rr = (rr.call_judge_full, rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE)
    saved_env = os.environ.get("TAXOARENA_DATA_ROOT")
    saved_sock = socket.socket.connect
    tmp = tempfile.mkdtemp(prefix="canary_epoch3_selftest_")

    def no_net(*a, **k):
        raise SystemExit("[SELFTEST] a network connection was attempted")
    socket.socket.connect = no_net
    try:
        ms = []
        for i in range(N_SET):
            q = 90000 + (i if i < 258 else 258 + (i - 258) // 2)
            ms.append(dict(match_id=500000 + i, qid=q, model_a="Model-Alpha", model_b="Model-Beta", node_id="n0", anchor="anchorX",
                           stratum="contested" if i % 2 else "cross", pair_kind="frontier" if i % 2 else "cross"))
        g["SET_HASH_OF_RECORD"] = set_hash(ms)
        g["pool_qids"] = lambda: {m["qid"] for m in ms}
        cdir = [tmp]
        g["cache_path"] = lambda n=None: os.path.join(cdir[0], "pass%d.db" % (n or NPASS))
        g["freeze_set"] = lambda allow_freeze=False: (ms, dict(set_hash=SET_HASH_OF_RECORD, pool_id=POOL, matches=ms))
        OUT_EPOCH3 = os.path.join(tmp, "e3.txt"); OUT_EPOCH3_STEM = os.path.join(tmp, "e3")
        LEDGER_DIR = os.path.join(tmp, "ledger"); os.makedirs(LEDGER_DIR)
        clock = [datetime.date(2026, 10, 8)]
        g["today_e3"] = lambda: clock[0]

        def write_pass(n, ties, ts0=1.0e9, started="2026-09-24 12:00:00"):
            con = _TRUE_CONNECT(cache_path(n))
            con.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
                        "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
                        "raw1 TEXT, raw2 TEXT, ts REAL, finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, stratum TEXT, pair_kind TEXT"
                        + (", provider1 TEXT, provider2 TEXT" if n >= 2 else "") + ")")
            con.execute("CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT)")
            for i, m in enumerate(ms):
                w = "TIE" if i in ties else "Model-Alpha"
                vals = [m["match_id"], m["model_a"], m["model_b"], m["node_id"], m["qid"], m["anchor"], "A", 1, "Model A", "Model B", 0.8, 0.8,
                        w, int(w == "TIE"), 0, "", "", ts0, "stop", "stop", 10, 10, m["stratum"], m["pair_kind"]]
                if n >= 2: vals += [EXPECTED_FINGERPRINT, EXPECTED_FINGERPRINT]
                con.execute("INSERT INTO verdicts VALUES (%s)" % ",".join("?" * len(vals)), vals)
            for k, v in current_meta(dict(set_hash=SET_HASH_OF_RECORD)).items():
                con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v if k != "pass_no" else str(n)))
            con.execute("INSERT INTO run_meta VALUES ('started', ?)", (started,))
            con.commit(); con.close()
        T1, T2 = set(), set(range(26))
        T3 = set(range(21, 26))                                      # |T2 ^ T3| = 21
        T4 = T3 | set(range(100, 128))                               # |T3 ^ T4| = 28
        for n, T in ((1, T1), (2, T2), (3, T3), (4, T4)):
            write_pass(n, T)
        PASS_CACHE_SHA256 = {1: file_sha256(cache_path(1)), 2: file_sha256(cache_path(2))}
        CLOSED_CACHE_SHA256_E3 = {3: file_sha256(cache_path(3)), 4: file_sha256(cache_path(4))}
        f0, f1, f2, f3 = _fragments()

        def fake_jobs(todo):
            return [(m, ("B", "ref text", 1), "SYSTEM PROMPT %s" % m["anchor"],
                     f0 + "Question %d?\n\n[Reference solution]\n(B) ref" % m["qid"] + f1 + "trace alpha %d" % m["match_id"] + f2 + "trace beta" + f3,
                     f0 + "Question %d?\n\n[Reference solution]\n(B) ref" % m["qid"] + f1 + "trace beta" + f2 + "trace alpha %d" % m["match_id"] + f3)
                    for m in todo]
        g["build_jobs"] = fake_jobs
        mode = {"ties": set(T3), "fp": EXPECTED_FINGERPRINT, "inv": set()}

        def fake_post(system, user, retries=6):
            mid = int(user.split("trace alpha ")[1].split("\n")[0].split()[0][:6])
            i = mid - 500000
            if i in mode["inv"]:
                return ("no json here", mode["fp"], 20, 0.0, "stop", {"_response_id": "fake-%d" % mid})
            alpha_first = user.index("trace alpha") < user.index("trace beta")
            v = "TIE" if i in mode["ties"] else ("Model A" if alpha_first else "Model B")
            return ('{"winner": "%s", "confidence": 0.9}' % v, mode["fp"], 20, 0.0, "stop", {"_response_id": "fake-%d" % mid})
        rr.call_judge_full = fake_post
        configure_rr()
        envroot = os.path.join(tmp, "envroot"); os.makedirs(envroot)
        open(os.path.join(envroot, ".env"), "w").write("AZURE_AI_ENDPOINT=https://selftest-e3.invalid\nAZURE_GROK_API_KEY=fake\n")
        noenv = os.path.join(tmp, "noenv"); os.makedirs(noenv)
        open(os.path.join(noenv, ".env"), "w").write("AZURE_AI_ENDPOINT=https://selftest-e3.invalid\n")
        os.environ["TAXOARENA_DATA_ROOT"] = envroot
        NPASS = 5

        # 1. gates before any database
        clock[0] = datetime.date(2026, 10, 7)
        check("DATE: a pass-5 launch on 2026-10-07 is REFUSED (0 calls)", refuses(run, PILOT_N, 2, go=True, budget=24, _want="[DATE-E3] REFUSED"))
        clock[0] = datetime.date(2026, 10, 8)
        check("GATE: without --go and a committed READY the launch is REFUSED", refuses(run, PILOT_N, 2, go=False, budget=24, _want="[GATE-E3]"))
        check("READY parse: the first verdict line must name G17-CANARY-V1E3 and the LF sha",
              _parse_ready("# t\n\nREADY: %s %s\n" % (TEST_EPOCH3, "abc"), "abc", TEST_EPOCH3)[1] == []
              and _parse_ready("READY: CANARY-EPOCH2-RUNG abc\n", "abc", TEST_EPOCH3)[1]
              and _parse_ready("READY: %s abc\nNOT READY: x\n" % TEST_EPOCH3, "abc", TEST_EPOCH3)[1])
        g["go_gate_epoch3"] = lambda what, go: print("[GATE-E3] (selftest) %s OPEN" % what)
        check("BUDGET: --go without --budget is REFUSED", refuses(run, PILOT_N, 2, go=True, budget=None, _want="explicit --budget"))
        # 2. the pre-flight: floors
        _m = dict(set_hash=SET_HASH_OF_RECORD)
        install_db_guard(writable=cache_path(5))
        check("PRE-FLIGHT: passes 1-4 complete, floors 26 / 21 / 28 REPRODUCED -> go", preflight_epoch3(_m) == [], preflight_epoch3(_m))
        bad = os.path.join(tmp, "badfloor"); os.makedirs(bad)
        for n in (1, 2, 3, 4): shutil.copy(cache_path(n), os.path.join(bad, "pass%d.db" % n))
        cdir[0] = bad
        c_ = _TRUE_CONNECT(cache_path(3)); c_.execute("UPDATE verdicts SET winner='TIE' WHERE match_id=500200"); c_.commit(); c_.close()
        pf = preflight_epoch3(_m)
        check("PRE-FLIGHT: a pass-3 cache with one changed verdict breaks 21/300 and 28/300 -> REFUSED",
              any("pass 2 -> 3 floor reproduces as 22/300" in x for x in pf) and any("pass 3 -> 4 floor reproduces as 29/300" in x for x in pf), pf)
        cdir[0] = tmp
        # 3. the dry-run: transport preflight executed (OK on the fake .env, REFUSED without a key)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dry_run(PILOT_N)
        dtxt = buf.getvalue()
        print(dtxt[-600:])
        check("DRY-RUN: prints 'TRANSPORT PREFLIGHT: OK (endpoint host=selftest-e3.invalid' (the real loader read the data root's .env)",
              any(l.startswith("TRANSPORT PREFLIGHT: OK (endpoint host=selftest-e3.invalid") for l in dtxt.split("\n")))
        check("DRY-RUN: the budget line names the DAY ledger and 600 planned of 630, 0 posted",
              "(iii) day 2026-10-08: 0 + 600 = 600 of 14000" in dtxt and "[DRY-RUN-E3] 24 payloads assembled, 0 posted" in dtxt, dtxt[-400:])
        os.environ["TAXOARENA_DATA_ROOT"] = noenv
        rr.AZURE_KEY = None
        check("DRY-RUN: with no key in the data root's .env the TRANSPORT preflight REFUSES the dry-run",
              refuses(dry_run, PILOT_N, _want="TRANSPORT"))
        check("RUN: with no key the posting launch REFUSES before any cache or ledger row",
              refuses(run, PILOT_N, 2, go=True, budget=24, _want="TRANSPORT") and not os.path.exists(cache_path(5))
              and not os.path.exists(atl.day_ledger_path(LEDGER_DIR, "2026-10-08")))
        os.environ["TAXOARENA_DATA_ROOT"] = envroot
        # 4. the day cap and the budget
        json.dump([{"test": "OTHER", "launch": "x", "calls": 13990, "ts": "t"}], open(atl.day_ledger_path(LEDGER_DIR, "2026-10-08"), "w"))
        check("DAY CAP: today's ledger 13,990 + this launch 24 > 14,000 is REFUSED, not trimmed",
              refuses(run, PILOT_N, 2, go=True, budget=24, _want="(iii) the day cap"))
        os.remove(atl.day_ledger_path(LEDGER_DIR, "2026-10-08"))
        check("BUDGET: planned 24 > --budget 20 is REFUSED", refuses(run, PILOT_N, 2, go=True, budget=20, _want="(iv) this launch plans 24"))
        # 5. the pilot, then the run, through the fake poster (pass 5 ties = T3 except 20 new -> d53 = 20/300)
        mode["ties"] = set(T3) | set(range(200, 220))
        clock[0] = datetime.date(2026, 10, 9)
        run(PILOT_N, 2, go=True, budget=24)
        led = json.load(open(atl.day_ledger_path(LEDGER_DIR, "2026-10-09")))
        check("PILOT: 24 calls posted and appended to the POSTING-DAY ledger day_calls_2026-10-09.json",
              led[-1]["calls"] == 24 and led[-1]["test"] == TEST_EPOCH3, led)
        check("RUN: --budget 100 < the 576 planned is REFUSED", refuses(run, None, 2, go=True, full=True, budget=100, _want="(iv) this launch plans 576"))
        # the hard cap inside the poster: a budget large enough for the gate but a cap hit mid-run is exercised on a scratch copy
        cap = os.path.join(tmp, "cap"); os.makedirs(cap)
        for n in (1, 2, 3, 4, 5): shutil.copy(cache_path(n), os.path.join(cap, "pass%d.db" % n))
        cdir[0] = cap; LEDGER_DIR = os.path.join(cap, "ledger"); os.makedirs(LEDGER_DIR)
        jobs = fake_jobs(ms[12:40]); con_ = _TRUE_CONNECT(cache_path(5))
        okc, errc, postedc, stopc = _post_epoch3(jobs, con_, ms, 1, 10, day_str_e3(), "probe")
        con_.close()
        check("HARD CAP: --budget 10 inside the poster stops at exactly 10 posted calls (5 matches cached), the 11th is never made",
              len(postedc) == 10 and okc == 5 and stopc and "[BUDGET-STOP]" in stopc[0], (len(postedc), okc, stopc))
        con_ = _TRUE_CONNECT(cache_path(5))
        clock_day = day_str_e3()
        g["today_e3"] = lambda: datetime.date(2026, 10, 10) if len(rr_calls) >= 4 else clock[0]
        rr_calls = []
        real_fake = rr.call_judge_full
        rr.call_judge_full = lambda s, u, retries=6: (rr_calls.append(1), real_fake(s, u))[1]
        okr, errr, postedr, stopr = _post_epoch3(fake_jobs(ms[40:60]), con_, ms, 1, 1000, clock_day, "probe")
        rr.call_judge_full = real_fake
        g["today_e3"] = lambda: clock[0]
        con_.close()
        check("ROLLOVER: a local-date change stops the launch after the 4th post (2 matches cached)",
              len(postedr) == 4 and okr == 2 and stopr and "local date changed" in stopr[0], (len(postedr), okr, stopr))
        cdir[0] = tmp; LEDGER_DIR = os.path.join(tmp, "ledger")
        run(None, 2, go=True, full=True, budget=576)
        r5, m5 = _rows_of(5)
        check("RUN: pass 5 holds 300 rows; the ledger counts 600 calls for G17-CANARY-V1E3",
              len(r5) == N_SET and atl.ledger_calls(TEST_EPOCH3, LEDGER_DIR) == 600, (len(r5), atl.ledger_calls(TEST_EPOCH3, LEDGER_DIR)))
        check("CEILING: a further 32-call launch is refused (600 + 32 > 630)", refuses(budget_gate_epoch3, 32, "probe", budget=32, _want="(i) "))
        # 6. the analysis of record
        c_ = _TRUE_CONNECT(cache_path(5)); c_.execute("UPDATE run_meta SET value='2026-10-09 10:00:00' WHERE key='started'"); c_.commit(); c_.close()
        rc = analyze_epoch3(boot=60)
        txt = open(OUT_EPOCH3, encoding="utf-8").read() if os.path.exists(OUT_EPOCH3) else ""
        ls = txt.split("\n")
        check("ANALYZE: writes the outcome of record (rc 0) with 'ALARM STATE: NO ALARM' flush-left", rc == 0 and "ALARM STATE: NO ALARM" in ls, rc)
        check("ANALYZE: C1-v1 reads d53 = 20/300 = 0.0667 (pass 3 vs pass 5, convention A)",
              any(l.startswith("(C1-v1) THE ALARM") and "= 20/300 = 0.0667 (convention A)" in l for l in ls),
              [l[:160] for l in ls if l.startswith("(C1-v1)")])
        check("ANALYZE: d54 = |T4 ^ T5| = 48/300 printed descriptive", "d54 (pass 4 vs pass 5) = 48/300 = 0.1600" in txt,
              [l[:120] for l in ls if "d54" in l])
        check("ANALYZE: P5 HELD (0.0667 in [0.050, 0.125]) and P6 HELD (600 calls, unusable 0)",
              any(l.strip().startswith("P5 ") and l.endswith("-> HELD") for l in ls) and any(l.strip().startswith("P6 ") and l.endswith("-> HELD") for l in ls),
              [l for l in ls if l.strip().startswith(("P5", "P6"))])
        check("ANALYZE: C0 (b) prints the floors 26/300, 21/300, 28/300 PASS", "26/300, 21/300, 28/300" in txt and "FALSIFIER: NOT FIRED." in ls)
        first = open(OUT_EPOCH3, "rb").read()
        check("WRITE-ONCE: a second --analyze-epoch3 returns 3 and leaves the file byte-identical",
              analyze_epoch3(boot=30) == 3 and open(OUT_EPOCH3, "rb").read() == first)
        check("RECORD: once the epoch-3 outcome exists, posting pass 5 is REFUSED", refuses(run, PILOT_N, 2, go=True, budget=24, _want="[RECORD]"))
        # 7. pure-readout value checks: the bar, A vs B, validity, P5 bounds, the start date
        P_ = {k: _rows_of(k)[0] for k in (1, 2, 3, 4, 5)}
        M_ = {5: {"started": "2026-10-09 10:00:00"}}
        base = epoch3_compute(ms, P_, M_, B=20, seeds=(42,))
        mk = lambda D, n=300, DB=None, nB=None: dict(n=n, D=D, d=D / n, dA={}, nB=nB if nB is not None else n, DB=DB if DB is not None else D,
                                                    dB=(DB if DB is not None else D) / (nB if nB is not None else n), n_dec=200, rev=0,
                                                    half={"contested": (D // 2, n // 2), "cross": (D - D // 2, n - n // 2)})

        def state_of(**kw):
            v = dict(base); v.update(kw); v.setdefault("se", {"d53": 0.017, "d54": 0.017})
            return epoch3_readout(v)
        t_, r_ = state_of(p35=mk(69, n=500))
        check("BAR: d53 = 69/500 = 0.138 exactly -> ALARM (the bar is inclusive, integer rule)", r_["state"] == "ALARM" and "ALARM STATE: ALARM" in t_.split("\n"), r_)
        t_, r_ = state_of(p35=mk(68, n=500))
        check("BAR: 68/500 = 0.136 -> NO ALARM", r_["state"] == "NO ALARM", r_)
        t_, r_ = state_of(p35=mk(42))
        check("ALARM: 42/300 = 0.140 -> ALARM, the falsifier line printed (Amendment 4 trigger (3))",
              r_["state"] == "ALARM" and any(l.startswith("FALSIFIER FIRES: C1-v1 ALARM") for l in t_.split("\n")), r_)
        t_, r_ = state_of(p35=mk(42, DB=30, nB=290))
        check("A vs B: A 42/300 ALARM while B 30/290 = 0.103 NO ALARM -> both recorded, A decides ALARM",
              r_["state"] == "ALARM" and "A AND B DISAGREE ON THE ALARM" in t_ and "convention B would read NO ALARM" in t_, r_)
        t_, r_ = state_of(p35=mk(30, DB=42, nB=290))
        check("A vs B: A 30/300 NO ALARM while B 42/290 ALARM -> A decides NO ALARM", r_["state"] == "NO ALARM" and "A AND B DISAGREE" in t_, r_)
        t_, r_ = state_of(p35=mk(42), valid=False)
        check("VALIDITY: C0 failed -> UNDETERMINED BY VALIDITY, ALARM STATE: UNDETERMINED, falsifier NOT EVALUATED",
              r_["state"] == "UNDETERMINED" and "ALARM STATE: UNDETERMINED" in t_.split("\n") and "FALSIFIER: NOT EVALUATED" in t_, r_)
        for D, want in ((15, "HELD"), (14, "FAILED"), (37, "HELD"), (38, "FAILED")):
            t_, r_ = state_of(p35=mk(D))
            check("P5: d53 = %d/300 = %.4f -> %s ([0.050, 0.125])" % (D, D / 300, want),
                  any(l.strip().startswith("P5 ") and l.endswith("-> " + want) for l in t_.split("\n")), [l for l in t_.split("\n") if "P5 " in l])
        t_, r_ = state_of(p35=mk(20), calls=598)
        check("P6: 598 calls (not 600 of 600) -> FAILED", any(l.strip().startswith("P6 ") and l.endswith("-> FAILED") for l in t_.split("\n")))
        t_, r_ = state_of(p35=None)
        check("ABSENT: pass 5 absent -> 'ALARM STATE: UNDETERMINED', P5/P6 UNDETERMINED BY VALIDITY",
              "ALARM STATE: UNDETERMINED" in t_.split("\n") and "UNDETERMINED BY VALIDITY" in t_, r_)
        sd = epoch3_compute(ms, P_, {5: {"started": "2026-10-07 23:00:00"}}, B=10, seeds=(42,))
        check("C0 (f): a pass 5 started 2026-10-07 FAILS validity", not sd["valid"] and not sd["c0"][5][1], sd["c0"][5])
        P3x = dict(P_[3]); rx = dict(P3x[ms[250]["match_id"]]); rx["winner"] = "TIE"; P3x[ms[250]["match_id"]] = rx
        sx = epoch3_compute(ms, {**P_, 3: P3x}, M_, B=10, seeds=(42,))
        check("C0 (b): a pass-3 row changed (22/300) FAILS validity in the analysis too", not sx["valid"] and not sx["c0"][1][1], sx["c0"][1])
        P5u = dict(P_[5])
        for m in ms[60:65]:
            x = dict(P5u[m["match_id"]]); x["finish1"] = "length"; P5u[m["match_id"]] = x
        su = epoch3_compute(ms, {**P_, 5: P5u}, M_, B=10, seeds=(42,))
        check("CONVENTION A: 5 unusable pass-5 rows count as differences (20 + 5 = 25/300); B drops them (20/295)",
              su["p35"]["D"] == 25 and su["p35"]["n"] == 300 and su["p35"]["DB"] == 20 and su["p35"]["nB"] == 295,
              (su["p35"]["D"], su["p35"]["DB"], su["p35"]["nB"]))
        # 8. a partial readout goes to a timestamped file and never to the record
        part = os.path.join(tmp, "part"); os.makedirs(part)
        for n in (1, 2, 3, 4, 5): shutil.copy(os.path.join(tmp, "pass%d.db" % n), os.path.join(part, "pass%d.db" % n))
        c_ = _TRUE_CONNECT(os.path.join(part, "pass5.db")); c_.execute("DELETE FROM verdicts WHERE match_id >= %d" % (500000 + PILOT_N)); c_.commit(); c_.close()
        cdir[0] = part; OUT_EPOCH3 = os.path.join(part, "e3.txt"); OUT_EPOCH3_STEM = os.path.join(part, "e3")
        rcp = analyze_epoch3(boot=10)
        made = [f for f in os.listdir(part) if f.startswith("e3_PILOT_")]
        check("PARTIAL: a 12-row pass 5 writes e3_PILOT_<ts>.txt (rc 2), never the outcome of record", rcp == 2 and made and not os.path.exists(OUT_EPOCH3), (rcp, made))
        check("PARTIAL: a second partial readout writes a NEW file (never overwrites; D3)", analyze_epoch3(boot=10) == 2
              and len([f for f in os.listdir(part) if f.startswith("e3_PILOT_")]) == 2)
        cdir[0] = tmp
        # 9. pins
        open(cache_path(4), "ab").write(b"\0")
        check("PINS: a pass-4 cache that no longer hashes to its pin REFUSES", refuses(pin_caches_e3, "selftest tamper", _want="[PIN-E3]"))
        missing = sorted(EPOCH3_BRANCHES - EPOCH3_HIT)
        check("BRANCHES: every C0 / C1 / P5 / P6 / falsifier / write branch executed (%d of %d)" % (len(EPOCH3_HIT & EPOCH3_BRANCHES), len(EPOCH3_BRANCHES)),
              not missing, missing)
    finally:
        sqlite3.connect = _TRUE_CONNECT
        socket.socket.connect = saved_sock
        (rr.call_judge_full, rr.AZURE_ENDPOINT, rr.AZURE_KEY, rr.PROVIDER, rr.JUDGE_MODEL, rr.MAX_TOKENS, rr.TEMPERATURE) = saved_rr
        if saved_env is None: os.environ.pop("TAXOARENA_DATA_ROOT", None)
        else: os.environ["TAXOARENA_DATA_ROOT"] = saved_env
        for k, v in saved.items(): g[k] = v
    print("[SELFTEST-EPOCH3] %s" % ("%d check(s) FAILED: %s" % (len(fails), fails) if fails else
                                    "all checks passed; 0 calls, nothing of record opened, tmp %s" % tmp))
    return 1 if fails else 0


def mutants_epoch3():
    import subprocess
    rows = []
    for m in E3_MUTANTS:
        env = dict(os.environ, CANARY_E3_MUTANT=m, PYTHONIOENCODING="utf-8")
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "--selftest-epoch3"], env=env, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        failed = [l.strip() for l in (p.stdout or "").split("\n") if l.rstrip().endswith("FAIL") or " FAIL  " in l]
        rows.append((m, "KILLED" if p.returncode != 0 else "SURVIVED", failed[0][:110] if failed else (p.stdout or "")[-200:].replace("\n", " ")))
    print("MUTANT TABLE (--mutants-epoch3):")
    for m, st, first in rows:
        print("  %-18s %-9s %s" % (m, st, first))
    k = sum(1 for r in rows if r[1] == "KILLED")
    print("KILLED %d of %d" % (k, len(rows)))
    return 0 if k == len(rows) else 1


if __name__ == "__main__":
    if "--selftest-epoch3" in sys.argv[1:]:              # G17-CANARY v1 leg (2026-10-01): fixtures only
        sys.exit(selftest_epoch3())
    if "--mutants-epoch3" in sys.argv[1:]:
        sys.exit(mutants_epoch3())
    if "--selftest-epoch2" in sys.argv[1:]:               # fixtures only: no pool read, no DB of record opened
        sys.exit(selftest_epoch2())
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    print("[POOL] %s (pool of record; active pool verified by pool_guard)" % POOL, flush=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first payload, post nothing")
    ap.add_argument("--pass", dest="npass", type=int, choices=[1, 2, 3, 4, 5], default=1)
    ap.add_argument("--budget", type=int, default=None, help="G17-CANARY v1 leg (pass 5): the explicit call budget of a posting launch (hard cap)")
    ap.add_argument("--analyze-epoch3", action="store_true", help="G17-CANARY v1 leg readout -> canary_epoch3_outcome.txt (write-once)")
    ap.add_argument("--selftest-epoch3", action="store_true")
    ap.add_argument("--mutants-epoch3", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="limit to the first N matches of the frozen set")
    ap.add_argument("--run", action="store_true", help="CANARY-EPOCH2-RUNG: post the whole pass (after its pilot)")
    ap.add_argument("--go", action="store_true", help="CANARY-EPOCH2-RUNG: required for --pilot / --run, with the committed READY")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=DEFAULT_MAXTOK, help="completion budget per call (default %d = rejudge_reasoning.MAX_TOKENS, the grok budget of record)" % DEFAULT_MAXTOK)
    ap.add_argument("--temperature", type=float, default=None, help="explicit temperature literal; default omits the field (provider default, Amendment 1 D2)")
    ap.add_argument("--override-guard", action="store_true", help="post beyond a cached invalid/non-terminated rate above 5%% (recorded in run_meta)")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--analyze-epoch2", action="store_true", help="CANARY-EPOCH2-RUNG readout -> canary_epoch2_outcome.txt (write-once)")
    ap.add_argument("--no-rung", action="store_true", help="--analyze-epoch2: declare that pass 4 was not run (the rung UNDETERMINED BY VALIDITY)")
    ap.add_argument("--selftest-epoch2", action="store_true")
    ap.add_argument("--freeze-only", action="store_true", help="rebuild the set only (zero calls); must reproduce the hash of record")
    a = ap.parse_args()
    NPASS = a.npass; MAXTOK = a.maxtok; TEMPERATURE = a.temperature
    if a.dry_run: sys.exit(dry_run(a.pilot))
    elif a.freeze_only: freeze_set(allow_freeze=True)
    elif a.analyze_epoch2: sys.exit(analyze_epoch2(no_rung=a.no_rung))
    elif a.analyze_epoch3: sys.exit(analyze_epoch3())
    elif a.analyze: analyze()
    else: sys.exit(run(a.pilot, a.workers, a.override_guard, go=a.go, full=a.run, budget=a.budget))
