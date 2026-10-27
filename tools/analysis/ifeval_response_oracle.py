"""IFEVAL-RESPONSE-ORACLE - does the IFEval judge's INDECISION collapse (COULD-NOT-VERIFY) or persist
(WOULD-NOT-COMMIT) when an EXECUTED per-response constraint-checker vector is attached to each trace?

REGISTERED 2026-09-23 BEFORE any code or call: docs/judge_v2_program.md L11148-L11329, commit 4c8379c. The
instrument is section (6) of the IFEVAL RULING (docs/agents/leads/2026-09-23_ifeval_ruling.md, af116f8,
judge-design-specialist, zero calls). Budget: plan Amendment 9 (docs/plan_2026-09-15.md L316-L363), a HARD
CEILING of 14,000 grok calls for the night of 2026-09-23.

  python tools/analysis/ifeval_response_oracle.py --selftest          (0 calls, no database opened, fixtures only)
  python tools/analysis/ifeval_response_oracle.py --dry-run           (0 calls: population, both arms, both orders, the transposition assertion)
  python tools/analysis/ifeval_response_oracle.py --pilot 12 [--workers 8]   (12 matches x 2 arms x 2 orders = 48 calls, INSIDE the 1,628)
  python tools/analysis/ifeval_response_oracle.py --run [--workers 8]        (the remaining matches; 1,628 calls in total, ceiling 1,700)
  python tools/analysis/ifeval_response_oracle.py --analyze

WHAT IT IS, AND WHAT IT IS NOT. The block attached to each trace is a PER-RESPONSE ORACLE - an ORACLE-CLASS
object stronger than ORACLE's question-level key - not a checker output of the kind MATH has. IFEval's verifier
emits a PREDICATE ON A RESPONSE (prompt_level_strict_acc = all(inst_level_strict_acc), the identity asserted row
by row at tools/analysis/checker_answer_ingest.py L513 / L528), so the ladder's IFEval rung STAYS AT
SPECIFICATION 0.658 permanently whatever this test reads. ANY sentence that places this test's accuracy beside
MATH's checker-repair accuracy or on the reference ladder is FORBIDDEN by the registration, in the outcome, the
ledger, the thesis and the blog, for two independent reasons: the reference objects are not the same kind, and
no IFEval cap-hit proxy exists so the populations differ (checker_answers_v2.db is MATH-only; IFEval's harness
cap is 1,280, programme L3741). The refusal is ENFORCED here, not commented: --compare-math exits non-zero, and
every outcome file is scanned for the forbidden numerals before it is written.

TWO ARMS, INTERLEAVED MATCH BY MATCH IN THE SAME SESSION, over the same population:
  CONTROL   = the GEN-ARENA IFEval prompt reproduced BYTE-IDENTICALLY. The system string is
              generative_arena.SYSTEM_BY_SOURCE["IFEVAL"] (generative_arena.py L35) and the rubric string is
              generative_arena.RUBRIC_BY_SOURCE["IFEVAL"] (L39), IMPORTED, never retyped; the question-appended
              "[Constraints the response must satisfy]" block is GEN-ARENA's own nested reference() function,
              extracted from generative_arena.judge's source and executed (L104-L116). A REWORDED control is a
              rubric-text arm and is refused on that ground alone, so nothing here is a copy that could drift.
  TREATMENT = the same prompt plus the per-response oracle block appended to EACH TRACE, rendered PER POSTED
              ORDER from the pair (trace, strict_vector).
THE ORDER HAZARD is the load-bearing implementation clause: GEN-ARENA's reference is appended to the QUESTION
(generative_arena.py L112, order-invariant); a per-response block is not. --dry-run asserts, on the POSTED bytes
of every assembled treatment match and prints for a sample, that the block shown for Model A in order 1 is
byte-identical to the block shown for Model B in order 2 and vice versa. A failure is a hard SystemExit.

POPULATION AND HYGIENE. GEN-ARENA's own IFEval schedule, unchanged: the key-decidable matches of
experiment_results/multicorpus/gen_arena_grok.db (source='IFEVAL' AND invalid=0), 407 of record, over the
reserved (EVAL) side of the multi-corpus per-(source, domain) 0.30 / seed-42 split. Three databases are opened
READ-ONLY and nothing else may be opened (connect_ro refuses any other path): gen_arena_grok.db (the population
and the DRIFT readout only - it is NEVER written by this test), checker_answers_v1.db :: ifeval_checker_answers
(strict_vector, instruction_ids, n_constraints, non_terminated) and multicorpus_cache_v1.db (corpus_questions,
eval_results, eval_results_mathfix, exactly as GEN-ARENA's correctness() reads them). NO MMLU-Pro row, no board,
no ratings cache, no snapshot, no embedding cache: p2dca21ab5f4ef3ae and paeec37aa28063c75 are untouched, and
pool_guard.assert_pool_of_record is deliberately NOT called because it would open the MMLU-Pro caches the
registration forbids; the population line below takes its place as the first printed line. No tree is built,
nothing is induced, labelled, routed or refitted. The loose fields (inst_level_loose_acc,
prompt_level_loose_acc) are ingested nowhere and are not used.

CONVENTIONS AND GUARDS. Judge grok-4-1-fast-non-reasoning; cap 8192; TEMPERATURE OMITTED (plan Amendment 1 D2);
dual order, TIE on flip, INVALID on parse failure or finish_reason length; every call through
rejudge_reasoning.call_judge_full, and the local payload_body copy asserts against rejudge_reasoning.py's source.
The deployment fingerprint ("azure:" + the response's model field) must equal "azure:grok-4-1-fast-non-reasoning"
on every call or the run STOPS fail-closed (the only exemption is rr's deterministic content-filter sentinel,
cached as an unusable row per rule 10). Own NEW cache with run_meta pinned at first launch (both arms' prompt
hashes, the schedule hash, judge, cap, temperature omitted, protocol, script sha) and a relaunch that differs on
any of them is REFUSED. NON_TERMINATED (checker_answers_v1.non_terminated on a contestant trace) is never a
verdict and never a tie: those rows are excluded from the deciding subset and counted. GATE: a COMMITTED
reviewer READY (docs/reviews/READY_ifeval_response_oracle.md) plus IFEVAL_ORACLE_GO=1628, checked fail-closed
BEFORE any database is opened. BUDGET: the cumulative night count is printed against 14,000 at every launch
(source: docs/agents/queue.json meta.tonight_budget.spent_calls, or --night-spent) and the launch that would
cross it is REFUSED, not trimmed; the same for this test's own ceiling of 1,700. PILOT: 12 matches in BOTH arms
(48 calls), read by the truncation guard, which REFUSES to post more above 5% unusable on the deciding subset.

SCORED (--analyze; both tie conventions always, A = ties / INVALID / non-terminated wrong, B = committed
verdicts only): C1 the OBEDIENCE FLOOR, bar 0.85 under convention A, question-clustered interval; C2 the
DECIDABLE TIE RATE paired control vs treatment (exact McNemar), C3 the FLIP RATE likewise - both SCOREABLE ONLY
AT |delta| >= 10pp, printed with the registered power line; C4 NON_TERMINATED accounting with its recorded
limit; C5 per-contestant agreement and the DRIFT readout. DECLARED NOT SCORED BEFORE THE RUN and printed as
such: GEN-ARENA criteria 2 (rho) and 3 (the BRIDGE), the exploratory router-cost readout, and CONSENSUS-FIT's
signed-contrast logistic (KEY and REF collinear by construction; the reference-wrong stratum is EMPTY BY
CONSTRUCTION, which is why this arm says nothing about the reference ceiling). --analyze exits non-zero on a
partial cache and writes the outcome of record only from a complete one; anything shorter goes to a _PILOT or a
_partial file. The outcome of record is WRITE-ONCE: an existing file is never overwritten.

[BUILD NOTE 2026-09-23, PHASE A, engine-coder; written with ZERO calls and with this script never executed, the
construction chain being live. Three things in the registration could not be implemented literally and are named here
rather than improvised.] (1) The standing convention "pool_guard.assert_pool_of_record(<pool id>) printed first" is
NOT followed, because pool_guard opens the MMLU-Pro caches this registration forbids; population_line() is the first
printed line instead and states explicitly that no MMLU-Pro pool is opened. (2) The registration's power paragraph
names "407 matches over 162 distinct reserved questions". The 162 is GEN-ARENA's whole IFEval schedule (1,200 matches
over 162 questions); the 407 KEY-DECIDABLE matches span 122 distinct questions (counted read-only from
gen_arena_grok.db + multicorpus_cache_v1.db while this script was written). The registered power line and its MDEs are
quoted UNCHANGED and are not re-derived; --dry-run and --analyze print the measured support beside them, and the
question-clustered bootstrap clusters on the questions actually present. (3) NON_TERMINATED: on the data as it stands,
zero of the 407 matches has a non_terminated contestant, so the deciding subset equals the 407; C4 prints the
accounting and its recorded limit regardless, and the exclusion path is live if the checker table ever changes.

[CORRECTED 2026-09-23 by the reviewer's READY (docs/reviews/READY_ifeval_response_oracle.md, 2dea289), defects D1-D4,
BEFORE the first posted call; the paragraphs above stand as written, these correct and complete them.] (D1) The
"SUPPORT AS MEASURED" clause of --analyze computed n_eff as len(dec)/2.0 = 204, arithmetically identical to the
registered 204, and inferred from it that "the registered MDEs are the optimistic end" - a vacuous computation and an
inference that is unsupported and wrong in direction. It is REPLACED by support_readout(), which prints the measured
support (407 matches over 122 distinct questions, 3.336 per question, Kish mean cluster size 4.376 with its size
histogram), states that the registration's descriptive "162 distinct reserved questions (~2.5 per question)" is
GEN-ARENA's whole 1,200-match schedule and is being bracketed by the registrar, states that the registered n_eff = n /
DEFF DOES NOT DEPEND ON THE QUESTION COUNT so the 162 -> 122 correction does not touch it, and brackets the honest DEFF
at the measured clustering (QUERY-SUPPORT's own implied ICC rho 0.072-0.085 at Kish 4.376 -> DEFF 1.24-1.29, n_eff
327-316; the rho = 1 extreme -> DEFF 4.376, n_eff 93, MDEs 9.2 / 13.0 / 15.9pp) - the registered 204 sits inside that
bracket and is conservative at the plausible end, and THE REGISTERED MDEs AND THE 10pp FLOOR ARE UNCHANGED. The clause
now prints in --dry-run as well as in --analyze. (D2) The control strings are imported, so a reword of the rubric
string's TAIL or of reference()'s BODY TEXT changed the posted prompt with no refusal. assert_pins() now recomputes and
REPRINTS three fingerprints at every launch - control system ebaec3a0f4b81f33, reference() on the first match's target
84fff82bc7154bba, schedule hash ba4a0ac8a2364a49 - and a mismatch is a hard refusal, so the fence is in the code and
not only in the READY. (D3) An errored job is not cached and therefore left the truncation guard's denominator;
guard_report(..., uncached_errors=err) now counts this launch's errored jobs into BOTH the denominator and the unusable
numerator, so the guard can only be pessimistic (the operator's condition C3, "done: ok 24, errors 0", still stands).
(D4) night_spent() now reads the registrar's experiment_results/night_calls_2026-09-23.json as well as the queue's
meta.tonight_budget.spent_calls, uses the LARGER when both are readable, names the source(s) it used in the printed
[NIGHT] line, and keeps --night-spent N as the operator's override. D5 (the queue's 838 under the refused single-arm
id) and D7 are not this script's to fix; D6 is why all of this lands before the pilot.
"""
import os, sys, re, json, time, random, sqlite3, hashlib, inspect, textwrap, argparse, subprocess, threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):        # the prompts carry em-dashes; a redirected Windows stdout must not crash the run
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import rejudge_grok as rj
import rejudge_reasoning as rr
import prompt_v2
import generative_arena as ga

# -- identity of the test -------------------------------------------------------
TEST = "IFEVAL-RESPONSE-ORACLE"
REGISTRATION = ("docs/judge_v2_program.md L11148-L11329 (commit 4c8379c); the instrument is section (6) of "
                "docs/agents/leads/2026-09-23_ifeval_ruling.md (af116f8)")
CORPUS = "IFEVAL"
JUDGE = "grok-4-1-fast-non-reasoning"                  # the deployed judge (Amendment 1 D1), as GEN-ARENA posted it
MAXTOK = rr.MAX_TOKENS                                 # 8192
TEMPERATURE = None                                     # None = the field is OMITTED (plan Amendment 1 D2)
EXPECTED_FINGERPRINT = "azure:" + JUDGE                # rejudge_reasoning.call_judge_full's 2nd element (rejudge_reasoning.py:131)
REFUSAL_FINGERPRINT = "azure:refusal"                  # rr's sentinel on a deterministic HTTP 400 content_filter
ARMS = ("control", "treatment")                        # posted INTERLEAVED, match by match, in the SAME session
SEED = 42

N_MATCHES_OF_RECORD = 407                              # key-decidable IFEval matches (registration; recomputed and asserted)
N_QUESTIONS_SCHEDULE = 162                             # distinct reserved questions in GEN-ARENA's IFEval schedule (all 1,200 matches)
PILOT_MATCHES = 12                                     # 12 matches x 2 arms x 2 orders = 48 calls, INSIDE the count
TOTAL_CALLS = 4 * N_MATCHES_OF_RECORD                  # 1,628
CALL_CEILING = 1700                                    # the registration's ceiling for this test
NIGHT_CEILING = 14000                                  # plan Amendment 9, the night of 2026-09-23
GUARD_RATE = 0.05                                      # the truncation guard on the deciding subset
C1_BAR = 0.85                                          # C1 HELD iff >= 0.85 under convention A
SCOREABLE_DELTA = 0.10                                 # C2 / C3 are scoreable only at |delta| >= 10pp
BOOT = 2000                                            # question-clustered bootstrap replicates

# The three prompt / schedule fingerprints PINNED by the reviewer's READY (docs/reviews/READY_ifeval_response_oracle.md,
# 2dea289, defect D2 / condition C2). They are recomputed and REPRINTED at every launch and a mismatch is a hard refusal:
# the control arm's strings are IMPORTED from generative_arena.py, so a reword of the rubric string's tail or of
# reference()'s body text would otherwise change the posted prompt silently. The fence is here, not only in the READY.
PINNED_SYSTEM_SHA = "ebaec3a0f4b81f33"                 # sha256[:16] of the assembled control system prompt
PINNED_REFERENCE_SHA = "84fff82bc7154bba"              # sha256[:16] of reference('IFEVAL', <first match's target>)
PINNED_SCHEDULE_HASH = "ba4a0ac8a2364a49"              # schedule_hash over the 407 matches with both strict vectors

# QUERY-SUPPORT's own implied intra-cluster correlations, used ONLY to bracket the design effect at the measured
# clustering (never to re-derive the registered power line): DEFF 2.0 at R2's mean reuse 12.8 -> rho = 1.0/11.8;
# worst 3.68 at reuse 38 -> rho = 2.68/37.
ICC_MEDIAN = (2.0 - 1.0) / (12.8 - 1.0)
ICC_WORST = (3.68 - 1.0) / (38.0 - 1.0)
REGISTERED_NEFF = 204                                  # 407 / DEFF 2.0, the registration's own figure (worst case 110)

# -- the files (all read-only; connect_ro refuses anything else) -----------------
# The DATA root may differ from the CODE root, exactly as pool_guard.py:38 allows, so that a reviewer or an engine-coder
# can --selftest / --dry-run this file from a git worktree against the data of record WITHOUT copying a database into the
# worktree. It defaults to ROOT, so the operator's run from the main checkout is unchanged; when it differs it is printed.
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
GEN_DB = os.path.join(DATA_ROOT, "experiment_results", "multicorpus", "gen_arena_grok.db")
CHECKER_DB = os.path.join(DATA_ROOT, "experiment_results", "multicorpus", "checker_answers_v1.db")
CORPUS_DB = os.path.join(DATA_ROOT, "multicorpus_cache_v1.db")
ALLOWED_DBS = (GEN_DB, CHECKER_DB, CORPUS_DB)
OUTDIR = os.path.join(DATA_ROOT, "experiment_results", "multicorpus")
CACHE = os.path.join(OUTDIR, "ifeval_response_oracle.db")      # a NEW cache; gen_arena_grok.db is never written
OUT = os.path.join(OUTDIR, "ifeval_response_oracle_outcome.txt")
OUT_PARTIAL = os.path.join(OUTDIR, "ifeval_response_oracle_outcome_partial.txt")
OUT_PILOT = os.path.join(OUTDIR, "ifeval_response_oracle_outcome_PILOT.txt")
NIGHT_LEDGER = os.path.join(DATA_ROOT, "experiment_results", "night_calls_2026-09-23.json")
RULING = os.path.join(ROOT, "docs", "agents", "leads", "2026-09-23_ifeval_ruling.md")
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
QUEUE_JSON = os.path.join(ROOT, "docs", "agents", "queue.json")
READY = os.path.join(ROOT, "docs", "reviews", "READY_ifeval_response_oracle.md")
GO_ENV, GO_VALUE = "IFEVAL_ORACLE_GO", "1628"

# -- the per-response oracle block (the ruling's section (6), verbatim shape) ----
BLOCK_HEADER = "[Instruction checker output for this response — produced by executed checker code, not by a model]"
BLOCK_DASH = " — "                                # the em-dash between the constraint line and PASS / FAIL

# -- record text quoted verbatim; asserted against its source file before use ----
POWER_LINE = ("POWER OF RECORD (fixed before the run; the ruling's section 4). 407 matches over 162 distinct reserved questions "
              "(~2.5 decidable matches per question); the record's design-effect rule is a median 2.0x and worst 3.7x understatement "
              "of match-level SEs, so n_eff = 204 (worst case 110).")
MDE_LINE = ("Paired difference SE = sqrt(d / n_eff): 2.2pp at discordance 0.10, 3.1pp at 0.20, 3.8pp at 0.30. MDE at 80% power, "
            "two-sided 0.05 (2.80 x SE): 6.2 / 8.8 / 10.7pp, and 8.5 / 12.0 / 14.7pp at DEFF 3.7.")
SCOREABILITY_LINE = ("SCOREABLE ONLY AT |delta| >= 10pp (the power paragraph below): a smaller move is recorded UNDETERMINED by "
                     "support, never as \"no change\".")
NULL_LINE = ("A NULL ON DECISIVENESS IS REPORTABLE ONLY AS \"the tie rate did not move by more than about 9pp\", NEVER AS \"the tie "
             "rate did not move\".")
QUOTED_FROM_REGISTRATION = (POWER_LINE, MDE_LINE, SCOREABILITY_LINE, NULL_LINE)

NOT_SCORED = [
    ("GEN-ARENA CRITERION 2 (per-corpus board Spearman rho >= 0.85)",
     "(i) VACUOUS - under a per-response vector the judged board is a noisy transcription of the key board, so rho measures obedience, "
     "not recovery of a key ordering; (ii) NOT COMPUTABLE - this schedule judges only the key-decidable matches, while the GEN-ARENA "
     "IFEval board was fitted on all 1,200, and a BT fit on a correctness-selected subset is a biased board."),
    ("GEN-ARENA CRITERION 3, THE BRIDGE (judged argmax == key argmax)",
     "vacuous and not computable for the same two reasons, AND CLOSED ON THE MERITS - ORACLE established that a perfect reference buys "
     "16.4pp and still misses the frontier order, and CONTEXT section 5 closes the frontier order (FRONTIER, AGGREGATE, ORACLE). The "
     "IFEval bridge broke at a judged top-two gap of 0.040 logits, the third independent appearance of the frontier near-tie."),
    ("THE EXPLORATORY ROUTER-COST READOUT (IFEval -0.6pp +- 3.8)",
     "not scored, same mechanism; no router claim is produced by this schedule, now or later."),
    ("CONSENSUS-FIT's KEY / REF SIGNED-CONTRAST LOGISTIC",
     "NOT ESTIMABLE here - the reference and the key coincide by construction, the two regressors are collinear and no REF coefficient "
     "exists. The standing strata-by-reference-correctness requirement is met by REPORTING THAT THE REFERENCE-WRONG STRATUM IS EMPTY BY "
     "CONSTRUCTION, which is itself the reason this arm says nothing whatever about the reference ceiling."),
]
C4_LIMIT = ("RECORDED LIMIT: IFEval's only non-termination proxy is the unclosed-<think> one "
            "(checker_answers_v1.ifeval_checker_answers.non_terminated). No cl100k cap-hit proxy exists for this corpus - "
            "checker_answers_v2.db is MATH-ONLY - and IFEval's harness cap is 1,280 (programme L3741, the Block-1 checker finding (3)).")
FORBIDDEN_NOTE = ("FORBIDDEN BY THE REGISTRATION: no sentence in this outcome, the ledger, the thesis or the blog may place this "
                  "accuracy beside the MATH checker-repair accuracy, or on the reference ladder, for two independent reasons - the "
                  "reference objects are not the same kind (a question-level canonical answer against a per-response predicate), and no "
                  "IFEval cap-hit proxy exists, so the populations differ. The ladder's IFEval rung stays at SPECIFICATION 0.658.")
FORBIDDEN_TOKENS = ("0.958", "0.993", "STAGE3-MATH-CAPFREE", "reference ladder", "CHECKER_OUTPUT (MATH)")


# -- refusals that are code, not comments ---------------------------------------

def refuse_math_comparison(what):
    """The registration forbids the comparison in terms. It is refused here, not annotated."""
    raise SystemExit("[REFUSED] %s. The registration forbids in terms any comparison of this test's accuracy with MATH's "
                     "checker-repair accuracy, and any placement of it on the reference ladder. %s" % (what, FORBIDDEN_NOTE))


def scrub(text, label):
    """No outcome text leaves this script carrying the forbidden comparison. FORBIDDEN_NOTE itself is removed before the scan."""
    probe = text.replace(FORBIDDEN_NOTE, "")
    hit = [t for t in FORBIDDEN_TOKENS if t in probe]
    if hit:
        raise SystemExit("[REFUSED] %s carries the forbidden MATH-ladder comparison (%s). Nothing is written. %s"
                         % (label, ", ".join(repr(h) for h in hit), FORBIDDEN_NOTE))
    return text


def rel(p):
    for base in (ROOT, DATA_ROOT):
        try:
            r = os.path.relpath(p, base)
            if not r.startswith(".."): return r
        except ValueError: pass
    return p


def connect_ro(path):
    """The ONLY way this script opens a database. Anything outside ALLOWED_DBS is a hygiene breach and is refused."""
    if os.path.abspath(path) not in [os.path.abspath(p) for p in ALLOWED_DBS]:
        raise SystemExit("[HYGIENE] refusing to open %s: the registration names three readable databases and no other "
                         "(gen_arena_grok.db, checker_answers_v1.db, multicorpus_cache_v1.db). No MMLU-Pro row, board, ratings, "
                         "snapshot or embedding cache is opened by this test." % path)
    if not os.path.exists(path):
        raise SystemExit("[HYGIENE] %s is missing; nothing is opened and nothing is posted." % rel(path))
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


# -- small helpers ---------------------------------------------------------------

def _sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def script_hash():
    return _sha16(open(os.path.abspath(__file__), "rb").read())


def script_hash_lf():
    """Newline-normalised, so the sha pinned in run_meta is the same in a CRLF checkout and in the committed blob."""
    return _sha16(open(os.path.abspath(__file__), "rb").read().replace(b"\r\n", b"\n"))


def norm(s):
    return " ".join(s.split())


def temp_label():
    return "omitted (provider default)" if TEMPERATURE is None else repr(TEMPERATURE)


def protocol():
    return ("GEN-ARENA IFEval prompt, system generative_arena.py L35 / rubric L39 imported verbatim | judge %s (azure chat completions "
            "via rejudge_reasoning, api-version 2024-05-01-preview) | CONTROL byte-identical to GEN-ARENA; TREATMENT identical plus the "
            "per-response oracle block appended to each trace, rendered per posted order | dual order, TIE on flip, INVALID if either "
            "order is unparsed or finish_reason=length | max_tokens %d | temperature %s" % (JUDGE, MAXTOK, temp_label()))


def configure_rr():
    """Point rejudge_reasoning at the deployed judge exactly as GEN-ARENA did (generative_arena.py:92). Reads no env,
    so the dry-run calls it too."""
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = TEMPERATURE


def payload_body(system, user):
    """Local copy of the body rejudge_reasoning.call_judge_full posts (rejudge_reasoning.py payload_body, lines 99-104:
    model, max_tokens, messages, optional temperature). assert_payload_source() checks the source text so a drift there
    is caught at zero calls, and the dry-run compares this body key for key with rr.payload_body's own output."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None: body["temperature"] = rr.TEMPERATURE
    return body


def assert_payload_source():
    src = open(rr.__file__, encoding="utf-8").read()
    assert '"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src, \
        "rejudge_reasoning.call_judge_full's body changed; update payload_body()"
    probe = payload_body("S", "U")
    assert probe == rr.payload_body("S", "U"), (probe, rr.payload_body("S", "U"))


# -- the CONTROL arm: GEN-ARENA's own strings and GEN-ARENA's own code ------------

def gen_reference_fn():
    """GEN-ARENA's nested reference(source, target), EXTRACTED FROM ITS SOURCE and executed here, so the control's
    question-appended '[Constraints the response must satisfy]' block cannot drift from generative_arena.py L104-L116.
    A copy would be a reworded control; this is the same code."""
    src = inspect.getsource(ga.judge)
    m = re.search(r"\n(    def reference\(source, target\):\n.*?)\n    def one\(m\):", src, re.S)
    if not m:
        raise SystemExit("[CONTROL] generative_arena.judge no longer contains the nested reference(source, target) between "
                         "its definition and 'def one(m):'. The control arm cannot be proved byte-identical; nothing is posted.")
    ns = {"json": json}
    exec(textwrap.dedent(m.group(1)), ns)                       # noqa: S102 - GEN-ARENA's own code, read from its own file
    fn = ns["reference"]
    assert fn("MATH", "x") == "\n\n[Verified reference answer]\nx", "extracted the wrong function from generative_arena.judge"
    return fn


GEN_REFERENCE = None            # set by control_assets()
CONTROL_SYSTEM = None


def control_assets():
    """(system prompt, reference function) for the control arm, both taken from generative_arena itself.

    The system prompt is assembled exactly as generative_arena.py L124-L125 assembles it; the assembly line is asserted
    against that file's source, and the two strings are IMPORTED (ga.SYSTEM_BY_SOURCE / ga.RUBRIC_BY_SOURCE), never retyped."""
    global GEN_REFERENCE, CONTROL_SYSTEM
    if CONTROL_SYSTEM is not None: return CONTROL_SYSTEM, GEN_REFERENCE
    gsrc = open(ga.__file__, encoding="utf-8").read()
    assert 'prompt_v2.v2_system_template().replace("$systemPrompt", SYSTEM_BY_SOURCE[source]).replace("$rubric", RUBRIC_BY_SOURCE[source])' in gsrc \
        and '+ "\\n\\n" + rj.SCHEMA_INSTRUCTION' in gsrc, \
        "generative_arena's system assembly changed; the control arm is no longer byte-identical and is refused"
    assert 'q = text + reference(source, target)' in gsrc, "generative_arena no longer appends the reference to the QUESTION"
    sysstr, rubstr = ga.SYSTEM_BY_SOURCE[CORPUS], ga.RUBRIC_BY_SOURCE[CORPUS]
    assert sysstr.startswith("You are judging two responses to an instruction-following prompt."), sysstr[:60]
    assert rubstr.startswith("Rank by: (1) how many of the listed constraints"), rubstr[:60]
    CONTROL_SYSTEM = (prompt_v2.v2_system_template().replace("$systemPrompt", sysstr).replace("$rubric", rubstr)
                      + "\n\n" + rj.SCHEMA_INSTRUCTION)
    GEN_REFERENCE = gen_reference_fn()
    return CONTROL_SYSTEM, GEN_REFERENCE


# -- the TREATMENT arm: the per-response oracle block ----------------------------

def oracle_block(instruction_ids, kwargs_list, strict_vector):
    """The ruling's section (6), verbatim shape: the header, then one line per entry of instruction_ids IN THE CHECKER'S
    OWN ORDER - the constraint id verbatim, its NON-NULL kwargs slots in parentheses in the stored order as 'key: value',
    an em-dash, and PASS or FAIL from the corresponding element of strict_vector. NO aggregate line, NO '3 of 3', NO
    all_pass_strict, NO overall verdict, NO loose field, NO comparison between the two responses and NO instruction to
    the judge about what to do with the block."""
    if not (len(instruction_ids) == len(strict_vector) == len(kwargs_list)):
        raise SystemExit("[BLOCK] ids %d / vector %d / kwargs %d disagree; the block is not assembled and nothing is posted"
                         % (len(instruction_ids), len(strict_vector), len(kwargs_list)))
    lines = [BLOCK_HEADER]
    for cid, kw, ok in zip(instruction_ids, kwargs_list, strict_vector):
        args = [(k, v) for k, v in (kw or {}).items() if v is not None]
        argtxt = (" (" + ", ".join("%s: %s" % (k, v) for k, v in args) + ")") if args else ""
        lines.append("- %s%s%s%s" % (cid, argtxt, BLOCK_DASH, "PASS" if int(ok) else "FAIL"))
    return "\n".join(lines)


def assert_block_shape_against_ruling():
    """The block's header and line shape are a recorded sentence: assert them against the ruling's own section (6)
    (docs/agents/leads/2026-09-23_ifeval_ruling.md) rather than trusting the constant in this file."""
    txt = open(RULING, encoding="utf-8").read()
    if BLOCK_HEADER not in txt:
        raise SystemExit("[BLOCK] the header is not byte-identical to the one in %s section (6); nothing is posted." % rel(RULING))
    sample = oracle_block(["punctuation:no_comma", "detectable_format:number_highlighted_sections", "length_constraints:number_words"],
                          [{"num_highlights": None}, {"num_highlights": 3}, {"relation": "at least", "num_words": 300}],
                          [1, 0, 1])
    for line in sample.split("\n"):
        if line.strip() and line not in txt:
            raise SystemExit("[BLOCK] the rendered line %r is not in %s section (6); the shape drifted and nothing is posted."
                             % (line, rel(RULING)))
    return sample


def assert_registration_quotes():
    """Every sentence this script prints as the record's own is checked against the registration, whitespace-normalised."""
    txt = norm(open(PROGRAMME, encoding="utf-8").read())
    missing = [q for q in QUOTED_FROM_REGISTRATION if norm(q) not in txt]
    if missing:
        raise SystemExit("[RECORD] %d quoted registration sentence(s) are not in %s verbatim: %s"
                         % (len(missing), rel(PROGRAMME), " | ".join(q[:60] + "..." for q in missing)))
    for phrase in ("FORBIDDEN BY THIS REGISTRATION", "PER-RESPONSE ORACLE", "TWO ARMS, INTERLEAVED MATCH BY MATCH"):
        if phrase not in open(PROGRAMME, encoding="utf-8").read():
            raise SystemExit("[RECORD] the registration no longer carries %r; this script is not its instrument." % phrase)


# -- the population --------------------------------------------------------------

def key_correctness(con):
    """GEN-ARENA's correctness(), restricted to IFEval (the mathfix table touches no IFEval row, and is read only so the
    reading is literally GEN-ARENA's)."""
    G = defaultdict(dict)
    for q, m, c in con.execute("SELECT e.question_id, e.model_name, e.is_correct FROM eval_results e JOIN corpus_questions q "
                               "USING(question_id) WHERE q.source='IFEVAL'"):
        G[q][m] = int(c)
    return G


def population(strict=True):
    """The 407 key-decidable IFEval matches, each with both traces, both strict vectors and the key winner.

    gen_arena_grok.db is opened READ-ONLY and is never written. Fail-closed on every join: a missing checker row, an
    instruction_ids that disagrees with corpus_questions.target, a vector whose all() disagrees with the key, or a count
    other than the registered 407 stops the script before anything is posted."""
    gen = connect_ro(GEN_DB); src = connect_ro(CORPUS_DB); ck = connect_ro(CHECKER_DB)
    G = key_correctness(src)
    meta = {q: (t, tg) for q, t, tg in src.execute("SELECT question_id, text, target FROM corpus_questions WHERE source='IFEVAL'")}
    outputs = {(q, m): o for q, m, o in src.execute("SELECT e.question_id, e.model_name, e.model_output FROM eval_results e "
                                                    "JOIN corpus_questions q USING(question_id) WHERE q.source='IFEVAL'")}
    chk = {(q, m): (json.loads(i), json.loads(v), int(n), int(nt), int(ap))
           for q, m, i, v, n, nt, ap in ck.execute("SELECT question_id, model_name, instruction_ids, strict_vector, n_constraints, "
                                                   "non_terminated, all_pass_strict FROM ifeval_checker_answers")}
    rows = gen.execute("SELECT match_id, qid, model_a, model_b, winner, flip FROM verdicts WHERE source='IFEVAL' AND invalid=0 "
                       "ORDER BY match_id").fetchall()
    n_all, n_q_all = gen.execute("SELECT COUNT(*), COUNT(DISTINCT qid) FROM verdicts WHERE source='IFEVAL'").fetchone()
    out = []
    for mid, qid, a, b, cache_winner, cache_flip in rows:
        ka, kb = G.get(qid, {}).get(a), G.get(qid, {}).get(b)
        if ka is None or kb is None or ka == kb: continue
        tgt = json.loads(meta[qid][1]); ids_t = tgt.get("instruction_id_list") or []; kws = tgt.get("kwargs") or []
        rec = {}
        for who in (a, b):
            c = chk.get((qid, who))
            if c is None:
                raise SystemExit("[POPULATION] no checker row for (%d, %s); the deciding subset cannot be built." % (qid, who))
            ids, vec, n_c, nt, ap = c
            if ids != ids_t:
                raise SystemExit("[POPULATION] (%d, %s): checker instruction_ids differ from corpus_questions.target's "
                                 "instruction_id_list; the kwargs could not be aligned and nothing is posted." % (qid, who))
            if not (len(vec) == n_c == len(ids)):
                raise SystemExit("[POPULATION] (%d, %s): strict_vector %d / n_constraints %d / ids %d disagree."
                                 % (qid, who, len(vec), n_c, len(ids)))
            key = G[qid][who]
            if int(all(vec)) != key or ap != key:
                raise SystemExit("[POPULATION] (%d, %s): all(strict_vector)=%s, all_pass_strict=%s, key=%s. The identity "
                                 "prompt_level_strict_acc = all(inst_level_strict_acc) (checker_answer_ingest.py L513/L528) does not "
                                 "hold here; nothing is posted." % (qid, who, int(all(vec)), ap, key))
            trace = outputs.get((qid, who)) or ""
            if not trace.strip():
                raise SystemExit("[POPULATION] (%d, %s) has an empty trace but a GEN-ARENA verdict; refusing." % (qid, who))
            rec[who] = dict(vec=vec, nt=nt, trace=trace)
        kwargs_list = [(kws[i] if i < len(kws) and isinstance(kws[i], dict) else {}) for i in range(len(ids_t))]
        out.append(dict(match_id=mid, qid=qid, model_a=a, model_b=b, key_winner=(a if ka else b),
                        text=meta[qid][0], target=meta[qid][1], ids=ids_t, kwargs=kwargs_list,
                        vec_a=rec[a]["vec"], vec_b=rec[b]["vec"], nt_a=rec[a]["nt"], nt_b=rec[b]["nt"],
                        trace_a=rec[a]["trace"], trace_b=rec[b]["trace"],
                        cache_winner=cache_winner, cache_flip=int(cache_flip)))
    if strict and len(out) != N_MATCHES_OF_RECORD:
        raise SystemExit("[POPULATION] %d key-decidable IFEval matches, not the registered %d. The population of record moved; "
                         "nothing is posted." % (len(out), N_MATCHES_OF_RECORD))
    facts = dict(n_ifeval_verdicts=n_all, n_questions_schedule=n_q_all, n_decidable=len(out),
                 n_questions_decidable=len({m["qid"] for m in out}),
                 n_nonterminated=sum(1 for m in out if m["nt_a"] or m["nt_b"]))
    return out, facts


def schedule_hash(matches):
    canon = "\n".join("%d:%d:%s:%s:%s:%s" % (m["match_id"], m["qid"], m["model_a"], m["model_b"],
                                             "".join(str(int(x)) for x in m["vec_a"]), "".join(str(int(x)) for x in m["vec_b"]))
                      for m in matches)
    return _sha16(canon.encode("utf-8"))


def assert_pins(matches):
    """READY condition C2 (defect D2): recompute and REPRINT the three pinned fingerprints at every launch; a mismatch
    means generative_arena.py or the population moved and the CONTROL arm is no longer the GEN-ARENA prompt. Hard refusal."""
    system, ref = control_assets()
    got = dict(system=_sha16(system.encode("utf-8")),
               reference=_sha16(ref(CORPUS, matches[0]["target"]).encode("utf-8")),
               schedule=schedule_hash(matches))
    want = dict(system=PINNED_SYSTEM_SHA, reference=PINNED_REFERENCE_SHA, schedule=PINNED_SCHEDULE_HASH)
    bad = [(k, want[k], got[k]) for k in want if want[k] != got[k]]
    print("[PINS] control system %s | reference(first target) %s | schedule %s -> %s (pinned by "
          "docs/reviews/READY_ifeval_response_oracle.md, 2dea289, condition C2)"
          % (got["system"], got["reference"], got["schedule"], "MATCH" if not bad else "MISMATCH"), flush=True)
    if bad:
        raise SystemExit("[PINS] REFUSED, nothing is posted: %s. A rubric-tail or reference()-body reword changes the posted prompt "
                         "without changing any assertion the arm makes about itself; the pinned value is the GEN-ARENA-era one. "
                         "Stop and re-review." % "; ".join("%s pinned %s, computed %s" % b for b in bad))
    return got


def support_readout(dec):
    """READY defect D1: the measured support of the JUDGED population, the honest DEFF bracket, and the statement that the
    registered n_eff and MDEs are unchanged. Nothing here re-derives the registered power line; it is quoted separately and
    verbatim. n_eff = n / DEFF does not depend on the question count, so the 162 -> 122 correction does not touch it."""
    sizes = Counter(Counter(m["qid"] for m in dec).values())
    n = len(dec); nq = sum(sizes.values())
    per_q = n / max(1, nq)
    kish = sum(s * s * c for s, c in sizes.items()) / max(1, sum(s * c for s, c in sizes.items()))   # sum n_i^2 / sum n_i
    deff_lo = 1 + ICC_WORST * (kish - 1); deff_hi = 1 + ICC_MEDIAN * (kish - 1)
    mde = lambda ne: tuple(2.80 * (d / ne) ** 0.5 for d in (0.10, 0.20, 0.30))
    m_max = mde(n / kish)
    return ("SUPPORT AS MEASURED (the registered power and MDE lines above are quoted VERBATIM and are NOT re-derived here): the "
            "judged population is %d matches over %d distinct questions, %.3f matches per question, Kish mean cluster size %.3f "
            "(cluster sizes %s). The registration's descriptive \"%d distinct reserved questions (~2.5 decidable matches per "
            "question)\" is GEN-ARENA's WHOLE 1,200-match IFEval schedule and is wrong for the judged population; the registrar is "
            "bracketing both numbers. The registered n_eff = %d is n / DEFF at QUERY-SUPPORT's median variance-ratio DEFF 2.0 and "
            "DOES NOT DEPEND ON THE QUESTION COUNT, so the %d -> %d correction does not touch it. Honest DEFF bracket at the "
            "measured clustering: transporting QUERY-SUPPORT's own implied ICC (rho %.3f-%.3f) to Kish %.3f gives DEFF %.2f-%.2f, "
            "n_eff %d-%d; the rho = 1 extreme gives DEFF %.3f, n_eff %d, MDEs %.1f / %.1f / %.1fpp at discordance 0.10 / 0.20 / 0.30. "
            "The registered n_eff %d sits INSIDE that bracket and is conservative at the plausible end. THE REGISTERED MDEs AND THE "
            "10pp SCOREABILITY FLOOR ARE UNCHANGED."
            % (n, nq, per_q, kish, "/".join("%d:%d" % (s, sizes[s]) for s in sorted(sizes)),
               N_QUESTIONS_SCHEDULE, REGISTERED_NEFF, N_QUESTIONS_SCHEDULE, nq,
               ICC_WORST, ICC_MEDIAN, kish, deff_lo, deff_hi, int(round(n / deff_lo)), int(round(n / deff_hi)),
               kish, int(round(n / kish)), 100 * m_max[0], 100 * m_max[1], 100 * m_max[2], REGISTERED_NEFF))


def deciding_subset(matches):
    """Rule 10: a match whose contestant trace is non_terminated is never a verdict and never a tie."""
    return [m for m in matches if not (m["nt_a"] or m["nt_b"])]


# -- assembly: the two user prompts of one (match, arm), per POSTED order ---------

def assemble(m, arm):
    """(system, user_order1, user_order2). Order 1 shows model_a as Model A; order 2 shows model_b as Model A.

    CONTROL: the reference is appended to the QUESTION by GEN-ARENA's own function and is therefore order-invariant.
    TREATMENT: the per-response block is appended to EACH TRACE, so the A/B labelling is re-derived FROM THE ORDER
    ACTUALLY POSTED - the pair (trace, vector) travels together and is never indexed by slot."""
    if arm not in ARMS:
        raise SystemExit("[ARM] %r is not one of %s" % (arm, ARMS))
    system, ref = control_assets()
    q = m["text"] + ref(CORPUS, m["target"])
    pair_a = (m["trace_a"], m["vec_a"])                      # (trace, vector) of model_a - always together
    pair_b = (m["trace_b"], m["vec_b"])                      # (trace, vector) of model_b

    def slot(pair):
        trace, vec = pair
        if arm == "control": return trace
        return trace + "\n\n" + oracle_block(m["ids"], m["kwargs"], vec)
    u1 = rj.build_user_prompt(q, slot(pair_a), slot(pair_b))
    u2 = rj.build_user_prompt(q, slot(pair_b), slot(pair_a))
    return system, u1, u2


def extract_blocks(user):
    """The oracle blocks as they appear in the POSTED bytes, in order of appearance (slot A first, then slot B)."""
    out = []
    for mt in re.finditer(re.escape(BLOCK_HEADER), user):
        lines = user[mt.start():].split("\n")
        block = [lines[0]]
        for line in lines[1:]:
            if line.startswith("- "): block.append(line)
            else: break
        out.append("\n".join(block))
    return out


def assert_transposition(m, u1, u2):
    """THE ORDER HAZARD, asserted on the posted bytes: the block shown for Model A in order 1 must be byte-identical to
    the block shown for Model B in order 2, and vice versa. A transposition here produces swapped vectors in the second
    order and an artefact indistinguishable from a catastrophic position effect. HARD FAILURE, never a warning."""
    b1, b2 = extract_blocks(u1), extract_blocks(u2)
    if len(b1) != 2 or len(b2) != 2:
        raise SystemExit("[TRANSPOSITION] match %d: found %d block(s) in order 1 and %d in order 2, expected 2 and 2. "
                         "REFUSED, nothing is posted." % (m["match_id"], len(b1), len(b2)))
    if not (b1[0] == b2[1] and b1[1] == b2[0]):
        raise SystemExit("[TRANSPOSITION] match %d FAILED: the vector attached to Model A in order 1 is not the vector attached to "
                         "Model B in order 2. This is the load-bearing implementation clause of the registration. REFUSED, nothing "
                         "is posted." % m["match_id"])
    if b1[0] == b1[1] and m["vec_a"] != m["vec_b"]:
        raise SystemExit("[TRANSPOSITION] match %d: the two slots carry the same block although the two strict vectors differ. "
                         "REFUSED." % m["match_id"])
    return b1, b2


# -- the gate, the budget --------------------------------------------------------

def git_state(path):
    try:
        t = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        c = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, capture_output=True, text=True).returncode == 0
        h = subprocess.run(["git", "log", "-1", "--format=%h", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return t, c, h
    except Exception as e:
        return False, False, "git unavailable: %s" % e


def gate_state():
    have = os.environ.get(GO_ENV); exists = os.path.exists(READY)
    t, c, h = git_state(READY) if exists else (False, False, "")
    if not exists: st = "MISSING"
    elif t and c: st = "exists, committed %s" % h
    elif not t: st = "exists, NOT committed (untracked)"
    else: st = "exists, uncommitted change"
    ok = (have == GO_VALUE) and exists and t and c
    return ok, "%s=%r (needs %r) | %s %s" % (GO_ENV, have, GO_VALUE, rel(READY), st)


def go_gate(what):
    """Fail-closed BEFORE anything is opened: a COMMITTED reviewer READY plus the env token."""
    ok, s = gate_state()
    if not ok:
        raise SystemExit("[READY] %s refused (0 calls, no database opened): %s. Nothing is posted, including the 48-call pilot, until "
                         "the reviewer's READY is COMMITTED and %s=%s is exported." % (what, s, GO_ENV, GO_VALUE))
    print("[READY] %s" % s, flush=True)


def night_spent(override=None):
    """The night's cumulative count of record: docs/agents/queue.json meta.tonight_budget.spent_calls (the
    experiment-manager's key; this script never writes it), unless the operator supplies --night-spent."""
    qval, lval, ceiling, why = None, None, NIGHT_CEILING, []
    try:
        d = json.load(open(QUEUE_JSON, encoding="utf-8"))
        tb = d.get("meta", {}).get("tonight_budget", {})
        qval = int(tb.get("spent_calls"))
        ceiling = int(tb.get("ceiling_calls", NIGHT_CEILING))
    except Exception as e:
        why.append("%s unreadable (%s)" % (rel(QUEUE_JSON), e))
    try:                                                    # the registrar's night ledger, adopted 2026-09-23 (READY D4)
        j = json.load(open(NIGHT_LEDGER, encoding="utf-8"))
        if isinstance(j, dict): lval = int(j.get("spent_calls", sum(int(e.get("calls", 0)) for e in j.get("entries", []))))
        else: lval = sum(int(e if isinstance(e, (int, float)) else (e or {}).get("calls", 0)) for e in j)
    except Exception as e:
        why.append("%s unreadable (%s)" % (rel(NIGHT_LEDGER), e))
    if qval is not None and ceiling != NIGHT_CEILING:
        raise SystemExit("[NIGHT] the queue records a ceiling of %d, this script knows %d (plan Amendment 9). REFUSED."
                         % (ceiling, NIGHT_CEILING))
    seen = [(n, v) for n, v in (("queue.json meta.tonight_budget.spent_calls", qval), (rel(NIGHT_LEDGER), lval)) if v is not None]
    if override is not None:
        return int(override), ("--night-spent (operator-supplied; %s)"
                               % ("; ".join("%s says %d" % s for s in seen) if seen else "; ".join(why)))
    if not seen:
        raise SystemExit("[NIGHT] cannot read the night's spend: %s. The launch is REFUSED: plan Amendment 9 (e) requires the "
                         "cumulative count against %d to be reported before every judged launch; pass --night-spent N to supply it."
                         % ("; ".join(why), NIGHT_CEILING))
    val = max(v for _n, v in seen)                          # the conservative reading when two ledgers disagree
    return val, ("%s%s" % (", ".join("%s = %d" % s for s in seen), "" if len(seen) < 2 else " -> the larger is used"))


def budget_gate(planned, posted_here, override=None):
    """Printed at every launch; the launch that would cross a ceiling is REFUSED, not trimmed."""
    spent, src = night_spent(override)
    total = spent + planned
    print("[NIGHT] cumulative %d + this launch %d = %d against the HARD CEILING of %d (plan Amendment 9) | source: %s"
          % (spent, planned, total, NIGHT_CEILING, src), flush=True)
    print("[BUDGET] this test: %d call(s) already posted into %s + %d planned = %d against its ceiling of %d (registered total %d)"
          % (posted_here, rel(CACHE), planned, posted_here + planned, CALL_CEILING, TOTAL_CALLS), flush=True)
    if total > NIGHT_CEILING:
        raise SystemExit("[NIGHT] REFUSED, not trimmed: this launch would take the night to %d, above the hard ceiling of %d "
                         "(plan Amendment 9 (e)). Record the refusal with this cumulative count." % (total, NIGHT_CEILING))
    if posted_here + planned > CALL_CEILING:
        raise SystemExit("[BUDGET] REFUSED, not trimmed: this launch would take the test to %d calls, above its registered ceiling of "
                         "%d." % (posted_here + planned, CALL_CEILING))


# -- the cache -------------------------------------------------------------------

def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts ("
                "match_id INTEGER NOT NULL, arm TEXT NOT NULL, qid INTEGER, model_a TEXT, model_b TEXT, key_winner TEXT, "
                "vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
                "raw1 TEXT, raw2 TEXT, finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, provider1 TEXT, provider2 TEXT, "
                "nt_a INTEGER, nt_b INTEGER, n_constraints INTEGER, ts REAL, "
                "PRIMARY KEY (match_id, arm))")
    con.execute("CREATE TABLE IF NOT EXISTS run_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.commit(); return con


def current_meta(matches, control_system, sample_blocks):
    return dict(test=TEST, registration=REGISTRATION, corpus=CORPUS, judge=JUDGE, protocol=protocol(),
                max_tokens=str(MAXTOK), temperature=temp_label(), arms="|".join(ARMS),
                schedule_hash=schedule_hash(matches), n_matches=str(len(matches)),
                control_system_sha16=_sha16(control_system.encode("utf-8")),
                control_reference_sha16=_sha16(control_assets()[1](CORPUS, matches[0]["target"]).encode("utf-8")),
                treatment_block_header_sha16=_sha16(BLOCK_HEADER.encode("utf-8")),
                treatment_sample_block_sha16=_sha16(sample_blocks.encode("utf-8")),
                script_sha256_16_lf=script_hash_lf())


def pin_meta(con, meta):
    """First launch pins the record; every later launch (pilot -> run, resume) must equal it or is REFUSED with both
    sides printed, so two protocols, two arms' texts or two schedules can never share a cache."""
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    old = dict(con.execute("SELECT key, value FROM run_meta"))
    if old:
        bad = [(k, old.get(k), v) for k, v in meta.items() if old.get(k) != v]
        if bad:
            raise SystemExit("[META] refusing to resume into %s: the cache was produced under a different record\n  %s\n"
                             "  (a different cap, temperature, protocol, arm text or schedule is a NEW session: move this cache aside "
                             "and relaunch)" % (rel(CACHE), "\n  ".join("%s: recorded %r | now %r" % b for b in bad)))
        con.execute("INSERT OR REPLACE INTO run_meta VALUES ('resumed', ?)",
                    (json.dumps(json.loads(old.get("resumed") or "[]") + [now]),))
        if old.get("script_sha256_16") != script_hash():
            con.execute("INSERT OR REPLACE INTO run_meta VALUES ('script_sha256_16_relaunch', ?)", (script_hash(),))
    else:
        for k, v in meta.items(): con.execute("INSERT INTO run_meta VALUES (?,?)", (k, v))
        con.execute("INSERT INTO run_meta VALUES ('started', ?)", (now,))
        con.execute("INSERT INTO run_meta VALUES ('script_sha256_16', ?)", (script_hash(),))
    con.commit()


def cached_rows(con):
    return {(r[0], r[1]) for r in con.execute("SELECT match_id, arm FROM verdicts")}


def unusable_counts(con, deciding_ids):
    """(rows, unusable rows) over the cached rows that belong to the DECIDING subset. Unusable = INVALID, a
    finish_reason of length (NON_TERMINATED output), or a provider content_filter refusal."""
    n = bad = 0
    for mid, arm, inv, f1, f2 in con.execute("SELECT match_id, arm, invalid, finish1, finish2 FROM verdicts"):
        if mid not in deciding_ids: continue
        n += 1
        if inv or f1 in ("length", "content_filter") or f2 in ("length", "content_filter"): bad += 1
    return n, bad


def guard_report(con, deciding_ids, label, uncached_errors=0):
    """READY defect D3: an errored job is not cached, so it would otherwise leave the guard's denominator and let a pilot
    with silent errors pass on a shrunken one. Errored jobs of THIS launch are counted into BOTH the denominator and the
    unusable numerator, so the guard can only be pessimistic."""
    n, bad = unusable_counts(con, deciding_ids)
    n += uncached_errors; bad += uncached_errors
    rate = bad / max(1, n)
    fr = dict(con.execute("SELECT COALESCE(f,'(none)'), COUNT(*) FROM (SELECT finish1 f FROM verdicts UNION ALL "
                          "SELECT finish2 FROM verdicts) GROUP BY 1"))
    fp = dict(con.execute("SELECT COALESCE(p,'(none)'), COUNT(*) FROM (SELECT provider1 p FROM verdicts UNION ALL "
                          "SELECT provider2 FROM verdicts) GROUP BY 1"))
    print("[GUARD] %s: %d row(s) on the deciding subset (cached %d + %d errored-and-not-cached, counted unusable) | %d unusable "
          "(%.1f%%) | finish_reason %s | fingerprints %s -> %s"
          % (label, n, n - uncached_errors, uncached_errors, bad, 100 * rate, fr, fp,
             "OK" if rate <= GUARD_RATE else "ABOVE 5%: the next launch REFUSES to post more"), flush=True)
    return n, bad, rate


class FingerprintMismatch(Exception):
    """Raised inside a worker when a call's deployment fingerprint is not EXPECTED_FINGERPRINT; run() turns it into a stop."""


def check_fingerprint(mid, arm, order, provider, finish):
    if provider == EXPECTED_FINGERPRINT: return
    if provider == REFUSAL_FINGERPRINT and finish == "content_filter": return
    raise FingerprintMismatch("match %d arm %s order %d: fingerprint %r != expected %r (finish_reason %r)"
                              % (mid, arm, order, provider, EXPECTED_FINGERPRINT, finish))


# -- the dry run (0 calls) --------------------------------------------------------

def data_root_line():
    return ("" if os.path.abspath(DATA_ROOT) == os.path.abspath(ROOT) else
            " | DATA ROOT %s (TAXOARENA_DATA_ROOT; the code root is %s - a worktree read of the data of record, nothing copied)"
            % (DATA_ROOT, ROOT))


def population_line(facts, matches):
    return ("[POPULATION] %s | %s | IFEval reserved (EVAL) side of the multi-corpus per-(source, domain) 0.30 / seed-42 split, "
            "GEN-ARENA's own schedule unchanged: %d IFEval verdicts over %d distinct questions -> %d KEY-DECIDABLE matches over %d "
            "distinct questions (registered %d); deciding subset %d after %d NON_TERMINATED exclusion(s); schedule hash %s. "
            "NO MMLU-Pro pool is opened: p2dca21ab5f4ef3ae and paeec37aa28063c75 are untouched, and gen_arena_grok.db is READ-ONLY "
            "(mode=ro) and is never written by this test.%s"
            % (TEST, REGISTRATION, facts["n_ifeval_verdicts"], facts["n_questions_schedule"], facts["n_decidable"],
               facts["n_questions_decidable"], N_MATCHES_OF_RECORD, len(deciding_subset(matches)), facts["n_nonterminated"],
               schedule_hash(matches), data_root_line()))


def dry_run(pilot=None, show=None):
    assert_registration_quotes()
    sample_shape = assert_block_shape_against_ruling()
    configure_rr(); assert_payload_source()
    matches, facts = population()
    print(population_line(facts, matches), flush=True)
    assert_pins(matches)
    print("[POWER] %s" % POWER_LINE, flush=True)
    print("[POWER] %s" % MDE_LINE, flush=True)
    print("[POWER] %s" % support_readout(deciding_subset(matches)), flush=True)
    work = matches[:pilot] if pilot else matches
    target_mid = show or work[0]["match_id"]
    if target_mid not in {m["match_id"] for m in work}:
        raise SystemExit("[DRY-RUN] --show-match %s is not in the assembled population." % target_mid)
    n_payload = 0; probe = {}
    for m in work:
        for arm in ARMS:
            system, u1, u2 = assemble(m, arm)
            if arm == "treatment": assert_transposition(m, u1, u2)
            elif extract_blocks(u1) or extract_blocks(u2):
                raise SystemExit("[CONTROL] match %d: an oracle block leaked into the CONTROL arm. REFUSED." % m["match_id"])
            for u in (u1, u2):
                body = payload_body(system, u)
                assert tuple(body) == ("model", "max_tokens", "messages") + (("temperature",) if TEMPERATURE is not None else ()), tuple(body)
                assert body["model"] == JUDGE and body["max_tokens"] == MAXTOK, (body["model"], body["max_tokens"])
                assert body.get("temperature") == TEMPERATURE, body.get("temperature")
                n_payload += 1
            if m["match_id"] == target_mid: probe[arm] = (m, system, u1, u2)
    print("[DRY-RUN] arms %s INTERLEAVED match by match in the SAME session | matches %d | %d payloads assembled, 0 posted "
          "(full schedule = %d matches x 2 arms x 2 orders = %d calls; pilot %d matches = %d calls, INSIDE the count; ceiling %d)"
          % (" + ".join(ARMS), len(work), n_payload, len(matches), 4 * len(matches), PILOT_MATCHES, 4 * PILOT_MATCHES, CALL_CEILING), flush=True)
    print("[DRY-RUN] protocol: %s" % protocol(), flush=True)
    print("[DRY-RUN] judge %s | max_tokens %d | temperature %s (plan Amendment 1 D2) | cache %s (exists: %s) | script sha256[:16] %s (LF %s)"
          % (JUDGE, MAXTOK, temp_label(), rel(CACHE), os.path.exists(CACHE), script_hash(), script_hash_lf()), flush=True)
    ok, gs = gate_state()
    print("[DRY-RUN] gate (not required for a dry run, required for every judged launch): %s -> %s"
          % (gs, "GO" if ok else "would REFUSE a judged launch"), flush=True)
    try:
        spent, src = night_spent(None)
        print("[NIGHT] cumulative %d against the HARD CEILING of %d (plan Amendment 9); a judged launch of this test would add up to "
              "%d calls (ceiling %d) -> %d | source: %s"
              % (spent, NIGHT_CEILING, TOTAL_CALLS, CALL_CEILING, spent + TOTAL_CALLS, src), flush=True)
    except SystemExit as e:
        print("[NIGHT] %s" % e, flush=True)
    print("[DRY-RUN] control arm: system generative_arena.SYSTEM_BY_SOURCE['IFEVAL'] (L35) and rubric RUBRIC_BY_SOURCE['IFEVAL'] (L39) "
          "IMPORTED verbatim; the question-appended block is generative_arena.judge's own nested reference(), extracted and executed "
          "(L104-L116). sha256[:16] system %s | reference(sample question) %s"
          % (_sha16(control_assets()[0].encode("utf-8")), _sha16(control_assets()[1](CORPUS, work[0]["target"]).encode("utf-8"))), flush=True)
    print("[DRY-RUN] treatment block shape verified line by line against %s section (6):\n%s" % (rel(RULING), sample_shape), flush=True)

    m, system, u1, u2 = probe["treatment"]
    b1, b2 = assert_transposition(m, u1, u2)
    print("\n===== TRANSPOSITION ASSERTION (match %d, qid %d, A=%s B=%s) =====" % (m["match_id"], m["qid"], m["model_a"], m["model_b"]), flush=True)
    print("order 1, slot 'Model A' (contestant %s):\n%s" % (m["model_a"], b1[0]))
    print("order 2, slot 'Model B' (contestant %s, the SAME contestant):\n%s" % (m["model_a"], b2[1]))
    print("order 1, slot 'Model B' (contestant %s):\n%s" % (m["model_b"], b1[1]))
    print("order 2, slot 'Model A' (contestant %s, the SAME contestant):\n%s" % (m["model_b"], b2[0]))
    print("[TRANSPOSITION] order1(A) == order2(B): %s | order1(B) == order2(A): %s | vectors differ between contestants: %s"
          % (b1[0] == b2[1], b1[1] == b2[0], m["vec_a"] != m["vec_b"]))
    print("[TRANSPOSITION] PASS for the sample match and for ALL %d assembled treatment matches (a failure is a hard refusal, "
          "never a warning)." % len(work), flush=True)
    for arm in ARMS:
        m, system, u1, u2 = probe[arm]
        for lab, u in (("ORDER 1", u1), ("ORDER 2", u2)):
            print("\n===== %s / %s : SYSTEM =====" % (arm.upper(), lab)); print(system)
            print("===== %s / %s : USER =====" % (arm.upper(), lab)); print(u)
    print("\n===== END =====")
    print("[DRY-RUN] %d payloads assembled, 0 posted." % n_payload, flush=True)
    return 0


# -- the judged launch ------------------------------------------------------------

def one_job(job):
    m, arm, system, u1, u2, halt, mismatch = job
    if halt.is_set(): raise FingerprintMismatch("match %d arm %s: not posted, the run is stopping" % (m["match_id"], arm))
    raw1, p1, k1, _, f1, _ = rr.call_judge_full(system, u1)
    try: check_fingerprint(m["match_id"], arm, 1, p1, f1)
    except FingerprintMismatch as e: mismatch.append(str(e)); halt.set(); raise
    if halt.is_set(): raise FingerprintMismatch("match %d arm %s: order 2 not posted, the run is stopping" % (m["match_id"], arm))
    raw2, p2, k2, _, f2, _ = rr.call_judge_full(system, u2)
    try: check_fingerprint(m["match_id"], arm, 2, p2, f2)
    except FingerprintMismatch as e: mismatch.append(str(e)); halt.set(); raise
    raw1, raw2 = rr.strip_think(raw1), rr.strip_think(raw2)
    v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
    if f1 in ("length", "content_filter"): v1 = "INVALID"          # NON_TERMINATED / a refusal is never a verdict and never a tie
    if f2 in ("length", "content_filter"): v2 = "INVALID"
    w, flip, inv = rj.combine_orders(v1, v2)
    return (m["match_id"], arm, m["qid"], m["model_a"], m["model_b"], m["key_winner"], v1, v2, c1, c2,
            {"Model A": m["model_a"], "Model B": m["model_b"]}.get(w, w), int(flip), int(inv), raw1, raw2,
            f1, f2, k1, k2, p1, p2, int(m["nt_a"]), int(m["nt_b"]), len(m["ids"]), time.time())


def run(pilot=None, workers=8, night_override=None):
    what = "the %d-match interleaved pilot (%d calls)" % (pilot, 4 * pilot) if pilot else "the full run"
    go_gate(what)                                            # fail-closed BEFORE anything is opened
    assert_registration_quotes(); assert_block_shape_against_ruling()
    configure_rr(); assert_payload_source()
    rr.load_env()                                            # the key rr.load_env selects (AZURE_GROK_API_KEY, else AZURE_AI_API_KEY)
    matches, facts = population()
    print(population_line(facts, matches), flush=True)
    assert_pins(matches)                                     # READY condition C2: reprinted and refused fail-closed
    dec_ids = {m["match_id"] for m in deciding_subset(matches)}
    work = matches[:pilot] if pilot else matches
    _sys0, _u1, _u2 = assemble(work[0], "treatment")
    con = open_cache()
    pin_meta(con, current_meta(matches, control_assets()[0], extract_blocks(_u1)[0]))
    done = cached_rows(con)
    if done:
        n, bad, rate = guard_report(con, dec_ids, "before this launch")
        if rate > GUARD_RATE:
            raise SystemExit("[GUARD] REFUSING to post more: %d of %d cached rows on the deciding subset are unusable (%.1f%% > 5%%). "
                             "Read finish1/finish2 in %s; the pilot has failed its truncation guard and the run is not authorised."
                             % (bad, n, 100 * rate, rel(CACHE)))
    jobs = []
    halt = threading.Event(); mismatch = []
    for m in work:                                           # INTERLEAVED: control then treatment, match by match
        for arm in ARMS:
            if (m["match_id"], arm) in done: continue
            system, u1, u2 = assemble(m, arm)
            if arm == "treatment": assert_transposition(m, u1, u2)
            elif extract_blocks(u1) or extract_blocks(u2):
                raise SystemExit("[CONTROL] match %d: an oracle block leaked into the CONTROL arm. REFUSED." % m["match_id"])
            jobs.append((m, arm, system, u1, u2, halt, mismatch))
    posted_here = 2 * len(done)
    budget_gate(2 * len(jobs), posted_here, night_override)
    print("%s: schedule %d matches x %d arms | cached %d row(s) | to post %d row(s) = %d calls | workers %d | cap %d | temperature %s"
          % (TEST, len(matches), len(ARMS), len(done), len(jobs), 2 * len(jobs), workers, MAXTOK, temp_label()), flush=True)
    if not jobs:
        guard_report(con, dec_ids, "nothing to post"); return 0
    lock = threading.Lock(); ok = err = 0; finishes = Counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one_job, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except FingerprintMismatch as e:
                halt.set(); ex.shutdown(wait=False, cancel_futures=True)
                raise SystemExit("[FINGERPRINT] %s\n  the run STOPS: nothing cached for that row, the remaining rows are not posted "
                                 "(cached so far: ok %d, errors %d). The deployed judge of record is %s; a different deployment is a "
                                 "different judge and never enters this cache." % (mismatch[0] if mismatch else e, ok, err, JUDGE))
            except Exception as e:
                err += 1; print("  ERROR match %s arm %s: %s" % (futs[f][0]["match_id"], futs[f][1], str(e)[:140]), flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 25), row); con.commit()
            ok += 1; finishes[row[15]] += 1; finishes[row[16]] += 1
            if i % 25 == 0 or i == len(jobs):
                print("  %d/%d (ok %d, err %d) | finish_reason %s" % (i, len(jobs), ok, err, dict(finishes)), flush=True)
    print("done: ok %d, errors %d%s" % (ok, err, " (errored rows are not cached; relaunch to resume them)" if err else ""), flush=True)
    n, bad, rate = guard_report(con, dec_ids, "after this launch", uncached_errors=err)
    if pilot and rate > GUARD_RATE:
        raise SystemExit("[GUARD] the %d-match pilot FAILED its truncation guard: %d of %d rows on the deciding subset are unusable "
                         "(%.1f%% > 5%%). The run is REFUSED; report the pilot and stop." % (pilot, bad, n, 100 * rate))
    if pilot:
        print("[GUARD] the pilot passes: %.1f%% unusable on the deciding subset (<= 5%%). The full run may be launched with --run."
              % (100 * rate), flush=True)
    return 0


# -- statistics -------------------------------------------------------------------

def clustered(vals_by_q, stat, B=BOOT, seed=SEED):
    """Question-clustered bootstrap of stat(list of per-match values): resample QUESTIONS with replacement."""
    qs = sorted(vals_by_q)
    if not qs: return (float("nan"), float("nan"), float("nan"))
    rng = random.Random(seed); out = []
    for _ in range(B):
        bs = [v for _ in qs for v in vals_by_q[qs[rng.randrange(len(qs))]]]
        out.append(stat(bs))
    out.sort(); mean = sum(out) / B
    sd = (sum((x - mean) ** 2 for x in out) / (B - 1)) ** 0.5
    return out[int(0.025 * B)], out[int(0.975 * B) - 1], sd


def by_q(rows, f):
    d = defaultdict(list)
    for r in rows: d[r["qid"]].append(f(r))
    return d


def rate(vals):
    return sum(vals) / len(vals) if vals else float("nan")


# -- the analysis ------------------------------------------------------------------

def load_cache(matches):
    con = sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)
    by_key = {}
    for r in con.execute("SELECT match_id, arm, qid, model_a, model_b, key_winner, winner, flip, invalid, finish1, finish2, "
                         "nt_a, nt_b FROM verdicts"):
        by_key[(r[0], r[1])] = dict(match_id=r[0], arm=r[1], qid=r[2], model_a=r[3], model_b=r[4], key_winner=r[5],
                                    winner=r[6], flip=r[7], invalid=r[8], f1=r[9], f2=r[10], nt_a=r[11], nt_b=r[12])
    meta = dict(con.execute("SELECT key, value FROM run_meta"))
    return by_key, meta


def arm_rows(by_key, arm, dec):
    return [by_key[(m["match_id"], arm)] for m in dec if (m["match_id"], arm) in by_key]


def committed(r):
    return r["winner"] in (r["model_a"], r["model_b"])


def analyze():
    assert_registration_quotes()
    if not os.path.exists(CACHE):
        raise SystemExit("[ANALYZE] %s does not exist: nothing has been posted." % rel(CACHE))
    matches, facts = population()
    dec = deciding_subset(matches)
    by_key, meta = load_cache(matches)
    L = []
    def p(s=""):
        L.append(s); print(s, flush=True)

    p(population_line(facts, matches))
    pins = assert_pins(matches)
    p("[PINS] control system %s | reference(first target) %s | schedule %s (pinned by docs/reviews/"
      "READY_ifeval_response_oracle.md, 2dea289, condition C2) -> MATCH" % (pins["system"], pins["reference"], pins["schedule"]))
    complete = all((m["match_id"], a) in by_key for m in matches for a in ARMS)
    n_rows = len(by_key)
    p("[CACHE] %s | %d of %d rows (%d matches x %d arms) | schedule hash %s (pinned %s) | judge %s | cap %s | temperature %s | "
      "script sha (LF) pinned %s, now %s"
      % (rel(CACHE), n_rows, len(matches) * len(ARMS), len(matches), len(ARMS), schedule_hash(matches),
         meta.get("schedule_hash"), meta.get("judge"), meta.get("max_tokens"), meta.get("temperature"),
         meta.get("script_sha256_16_lf"), script_hash_lf()))
    if not meta:
        raise SystemExit("[ANALYZE] %s carries no run_meta: no launch has pinned this cache and nothing has been posted." % rel(CACHE))
    if meta.get("schedule_hash") != schedule_hash(matches):
        raise SystemExit("[ANALYZE] the cache was written against schedule %s, the population now hashes to %s. REFUSED."
                         % (meta.get("schedule_hash"), schedule_hash(matches)))
    p("[ARMS] %s, posted INTERLEAVED match by match in the SAME session (the GEN-ARENA cache is a DRIFT READOUT only, never the "
      "comparator of record)." % " + ".join(ARMS))

    res = {}
    for arm in ARMS:
        rows = arm_rows(by_key, arm, dec)
        n = len(rows)
        corr = [1 if r["winner"] == r["key_winner"] else 0 for r in rows]             # convention A: ties / INVALID wrong
        accA = rate(corr)
        comm = [r for r in rows if committed(r)]
        accB = rate([1 if r["winner"] == r["key_winner"] else 0 for r in comm])
        ties = [1 if r["winner"] == "TIE" else 0 for r in rows]
        inval = sum(1 for r in rows if r["invalid"])
        parsed = [r for r in rows if not r["invalid"]]
        tieA = rate(ties)
        tieB = rate([1 if r["winner"] == "TIE" else 0 for r in parsed])
        flipA = rate([r["flip"] for r in rows])
        flipB = rate([r["flip"] for r in parsed])
        loA, hiA, sdA = clustered(by_q(rows, lambda r: 1 if r["winner"] == r["key_winner"] else 0), rate)
        res[arm] = dict(n=n, accA=accA, accB=accB, nB=len(comm), tieA=tieA, tieB=tieB, nparsed=len(parsed),
                        flipA=flipA, flipB=flipB, inval=inval, ciA=(loA, hiA, sdA), rows={r["match_id"]: r for r in rows})
        p("  %-9s n=%d | accuracy A %.3f [%.3f, %.3f] SE %.3f (question-clustered over %d questions) | accuracy B %.3f (n=%d) | "
          "ties A %.3f / B %.3f | flips A %.3f / B %.3f | INVALID %d"
          % (arm, n, accA, loA, hiA, sdA, len({r["qid"] for r in rows}), accB, len(comm), tieA, tieB, flipA, flipB, inval))

    # -- C1 ------------------------------------------------------------------------
    t = res["treatment"]
    p("")
    p("(C1) THE OBEDIENCE FLOOR - the share of key-decidable matches on which the judge commits to the contestant that a correct, "
      "per-response reference names. Denominator = the %d key-decidable matches less the %d NON_TERMINATED exclusion(s) = %d "
      "(the deciding subset)." % (facts["n_decidable"], facts["n_nonterminated"], len(dec)))
    p("     convention A (ties / INVALID / non-terminated wrong): %.3f [%.3f, %.3f] | convention B (committed verdicts only, n=%d): %.3f"
      % (t["accA"], t["ciA"][0], t["ciA"][1], t["nB"], t["accB"]))
    p("     DISOBEDIENCE RATE (its complement, convention A): %.3f - the judge's irreducible error under the strongest reference "
      "that can exist." % (1 - t["accA"]))
    p("     C1 (bar %.2f under convention A): %s" % (C1_BAR, "HELD" if t["accA"] >= C1_BAR else "FAILED"))
    p("     " + FORBIDDEN_NOTE)

    # -- C2 / C3 -------------------------------------------------------------------
    def paired(field):
        """(b, c, n_pairs) for treatment vs control on the same matches; b = treatment-only, c = control-only. The
        denominator is the deciding subset under convention A, so a pair in which either arm is INVALID is kept and
        counted (its count is printed separately)."""
        b = c = n = 0
        for m in dec:
            rc = by_key.get((m["match_id"], "control")); rt = by_key.get((m["match_id"], "treatment"))
            if rc is None or rt is None: continue
            n += 1
            xc, xt = field(rc), field(rt)
            if xt and not xc: b += 1
            elif xc and not xt: c += 1
        return b, c, n

    n_inv_pair = sum(1 for m in dec
                     if (by_key.get((m["match_id"], "control")) or {}).get("invalid")
                     or (by_key.get((m["match_id"], "treatment")) or {}).get("invalid"))

    p("")
    p("(C2) DECISIVENESS - the DECIDABLE TIE RATE, control vs treatment, PAIRED on the same matches.")
    b, c, npair = paired(lambda r: r["winner"] == "TIE")
    d_tie = res["treatment"]["tieA"] - res["control"]["tieA"]
    pval = rr.mcnemar_p(b, c)
    p("     control %.3f -> treatment %.3f | delta %+.3f (%+.1fpp) | discordant: treatment-only ties %d, control-only ties %d over "
      "%d paired matches | exact McNemar p = %.4f (rejudge_reasoning.mcnemar_p)"
      % (res["control"]["tieA"], res["treatment"]["tieA"], d_tie, 100 * d_tie, b, c, npair, pval))
    p("     pairs in which either arm is INVALID (kept, convention A): %d of %d" % (n_inv_pair, npair))
    p("     SCOREABILITY, declared before the run: %s" % SCOREABILITY_LINE)
    p("     %s" % POWER_LINE)
    p("     %s" % MDE_LINE)
    p("     " + support_readout(dec))
    scoreable = abs(d_tie) >= SCOREABLE_DELTA
    p("     C2: %s" % ("HELD (COULD-NOT-VERIFY): the tie rate falls by >= 10pp with p < 0.05"
                       if (d_tie <= -SCOREABLE_DELTA and pval < 0.05) else
                       ("FAILED: |delta| >= 10pp but the McNemar test does not reject" if scoreable else
                        "UNDETERMINED BY SUPPORT (|delta| = %.1fpp < 10pp)" % abs(100 * d_tie))))
    if not scoreable: p("     %s" % NULL_LINE)

    p("")
    p("(C3) THE FLIP RATE, same pairing, same denominator, same McNemar treatment and the same 10pp scoreability floor.")
    bf, cf, npf = paired(lambda r: bool(r["flip"]))
    d_flip = res["treatment"]["flipA"] - res["control"]["flipA"]
    pf = rr.mcnemar_p(bf, cf)
    p("     control %.3f -> treatment %.3f | delta %+.3f (%+.1fpp) | discordant: treatment-only flips %d, control-only flips %d over "
      "%d paired matches | exact McNemar p = %.4f" % (res["control"]["flipA"], res["treatment"]["flipA"], d_flip, 100 * d_flip,
                                                      bf, cf, npf, pf))
    p("     SCOREABILITY, declared before the run: %s" % SCOREABILITY_LINE)
    p("     C3: %s" % ("HELD: the flip rate falls by >= 10pp with p < 0.05" if (d_flip <= -SCOREABLE_DELTA and pf < 0.05) else
                       ("FAILED: |delta| >= 10pp but the McNemar test does not reject" if abs(d_flip) >= SCOREABLE_DELTA else
                        "UNDETERMINED BY SUPPORT (|delta| = %.1fpp < 10pp)" % abs(100 * d_flip))))

    # -- C4 ---------------------------------------------------------------------------
    p("")
    p("(C4) NON_TERMINATED ACCOUNTING (rule 10: never a verdict, never a tie).")
    per = Counter()
    for m in matches:
        if m["nt_a"]: per[m["model_a"]] += 1
        if m["nt_b"]: per[m["model_b"]] += 1
    p("     excluded matches %d of %d (%.1f%%) | per contestant: %s"
      % (facts["n_nonterminated"], len(matches), 100.0 * facts["n_nonterminated"] / max(1, len(matches)),
         dict(per) if per else "none"))
    p("     " + C4_LIMIT)

    # -- C5 ---------------------------------------------------------------------------
    p("")
    p("(C5) THE LEAKAGE READOUT, PRINTED, NO BAR.")
    for arm in ARMS:
        rows = arm_rows(by_key, arm, dec)
        agree = defaultdict(lambda: [0, 0])
        for r in rows:
            if not committed(r): continue
            a = agree[r["key_winner"]]
            a[1] += 1; a[0] += 1 if r["winner"] == r["key_winner"] else 0
        pooled_ok = sum(v[0] for v in agree.values()); pooled_n = sum(v[1] for v in agree.values())
        p("     %-9s per-contestant agreement (share of COMMITTED verdicts that follow the all-pass contestant, by that contestant):"
          % arm)
        for m_name in sorted(agree, key=lambda k: -agree[k][1]):
            ok_, n_ = agree[m_name]
            p("       %-32s %3d / %3d = %.3f" % (m_name, ok_, n_, ok_ / max(1, n_)))
        p("       %-32s %3d / %3d = %.3f" % ("POOLED", pooled_ok, pooled_n, pooled_ok / max(1, pooled_n)))
    cache_rows = {m["match_id"]: m["cache_winner"] for m in dec}
    ctrl = arm_rows(by_key, "control", dec)
    same = sum(1 for r in ctrl if cache_rows.get(r["match_id"]) == r["winner"])
    p("     DRIFT readout (control-vs-cache agreement on the same matches; the 2026-09-13 GEN-ARENA cache is a READOUT, never the "
      "comparator of record): %d / %d = %.3f" % (same, len(ctrl), same / max(1, len(ctrl))))

    # -- declared not scored -----------------------------------------------------------
    p("")
    p("DECLARED NOT SCORED, BEFORE THE RUN, AND WHY (nothing in the outcome may quote them):")
    for name, why in NOT_SCORED:
        p("  - %s: %s" % (name, why))

    p("")
    p("PREDICTIONS (registered before any code): P1 C1 in [0.88, 0.96] under convention A; P2 treatment decidable tie rate below "
      "0.10; P3 treatment flip rate below 0.25; P4 the CONTROL arm reproduces GEN-ARENA within the session floor (accuracy "
      "0.658 +- 0.07, ties 0.256 +- 0.09, flips 0.380 +- 0.09); P5 drift >= 0.85; P6 NON_TERMINATED exclusions <= 5%% of %d; "
      "P7 unusable rows <= 1%% of the posted calls." % len(matches))
    con = sqlite3.connect("file:%s?mode=ro" % CACHE.replace("\\", "/"), uri=True)
    n_g, bad_g = unusable_counts(con, {m["match_id"] for m in dec})
    preds = [
        ("P1 C1 in [0.88, 0.96] (convention A)", 0.88 <= t["accA"] <= 0.96, "%.3f" % t["accA"]),
        ("P2 treatment tie rate < 0.10", t["tieA"] < 0.10, "%.3f" % t["tieA"]),
        ("P3 treatment flip rate < 0.25", t["flipA"] < 0.25, "%.3f" % t["flipA"]),
        ("P4 control accuracy 0.658 +- 0.07", abs(res["control"]["accA"] - 0.658) <= 0.07, "%.3f" % res["control"]["accA"]),
        ("P4 control tie rate 0.256 +- 0.09", abs(res["control"]["tieA"] - 0.256) <= 0.09, "%.3f" % res["control"]["tieA"]),
        ("P4 control flip rate 0.380 +- 0.09", abs(res["control"]["flipA"] - 0.380) <= 0.09, "%.3f" % res["control"]["flipA"]),
        ("P5 drift >= 0.85", (same / max(1, len(ctrl))) >= 0.85, "%.3f" % (same / max(1, len(ctrl)))),
        ("P6 NON_TERMINATED <= 5%", facts["n_nonterminated"] <= 0.05 * len(matches), "%d" % facts["n_nonterminated"]),
        ("P7 unusable rows <= 1%", bad_g <= 0.01 * max(1, n_g), "%d / %d" % (bad_g, n_g)),
    ]
    for lab, held, val in preds:
        p("  %-42s %-12s -> %s" % (lab, val, "HELD" if held else "FAILED"))

    p("")
    p("FALSIFIER (registered): IF THE TIE RATE DOES NOT FALL BY MORE THAN THE MDE WHILE ACCURACY RISES ABOVE 0.88, the IFEval failure "
      "is WOULD-NOT-COMMIT: the abstention and order-instability line owns it, no reference of any strength repairs the rung, and "
      "GEN-ARENA finding 2's MECHANISM is overturned while its numbers stand. Reading here: tie delta %+.1fpp, treatment accuracy "
      "%.3f -> %s." % (100 * d_tie, t["accA"],
                       "WOULD-NOT-COMMIT" if (abs(d_tie) < SCOREABLE_DELTA and t["accA"] > 0.88) else
                       ("COULD-NOT-VERIFY" if (d_tie <= -SCOREABLE_DELTA and pval < 0.05) else "UNDETERMINED")))
    p("")
    p("HEADER: %s | judge %s | cap %d | temperature %s | script sha256[:16] (LF) %s | written %s"
      % (TEST, JUDGE, MAXTOK, temp_label(), script_hash_lf(), time.strftime("%Y-%m-%d %H:%M:%S")))

    text = scrub("\n".join(L) + "\n", "the outcome text")
    if not complete:
        target = OUT_PILOT if n_rows <= 2 * PILOT_MATCHES else OUT_PARTIAL
        banner = ("NOT OF RECORD - the cache holds %d of %d rows, short of the schedule. NO line in this file is a REGISTERED line: "
                  "every criterion below is a running readout on a partial cache and none of them is scored. The outcome of record is "
                  "written only from a complete cache, to %s.\n\n" % (n_rows, len(matches) * len(ARMS), rel(OUT)))
        open(target, "w", encoding="utf-8").write(banner + text)
        print("\n[ANALYZE] the cache holds %d of %d rows: NO REGISTERED LINE is written. Wrote %s."
              % (n_rows, len(matches) * len(ARMS), rel(target)), flush=True)
        raise SystemExit(2)
    if os.path.exists(OUT):
        print("\n[ANALYZE] the outcome of record %s already exists and this analysis is WRITE-ONCE: nothing was overwritten. "
              "Move it aside if it must be regenerated." % rel(OUT), flush=True)
        return 0
    open(OUT, "w", encoding="utf-8").write(text)
    print("\n[ANALYZE] complete cache (%d rows): wrote %s" % (n_rows, rel(OUT)), flush=True)
    return 0


# -- the selftest (0 calls, no database opened) -------------------------------------

def selftest():
    fails = []

    def check(name, cond, detail=""):
        print("  %-58s %s%s" % (name, "OK" if cond else "FAIL", ("  " + detail) if detail and not cond else ""))
        if not cond: fails.append(name)

    print("[SELFTEST] %s | script sha256[:16] %s (LF %s) | 0 calls, no database opened" % (TEST, script_hash(), script_hash_lf()))
    shape = assert_block_shape_against_ruling()
    check("block shape verified line by line against the ruling (6)", shape.startswith(BLOCK_HEADER))
    print(shape)
    assert_registration_quotes()
    check("every quoted registration sentence is verbatim", True)
    ids = ["punctuation:no_comma", "detectable_format:number_highlighted_sections", "length_constraints:number_words"]
    kws = [{"num_highlights": None, "keywords": None}, {"num_highlights": 3}, {"relation": "at least", "num_words": 300}]
    blk = oracle_block(ids, kws, [1, 0, 1])
    check("no aggregate line, no all_pass, no loose field, no verdict",
          len(blk.split("\n")) == 4 and "all_pass" not in blk and "loose" not in blk and " of " not in blk)
    check("null kwargs slots are dropped", "- punctuation:no_comma — PASS" in blk, blk)
    check("non-null kwargs render as 'key: value' in the stored order",
          "- length_constraints:number_words (relation: at least, num_words: 300) — PASS" in blk, blk)
    check("PASS / FAIL come from strict_vector element-wise",
          blk.count("— PASS") == 2 and blk.count("— FAIL") == 1)
    check("the STACK-v2 'may be wrong' wrapper is NOT reused", "may be wrong" not in blk and "Reference solution" not in blk)

    system, ref = control_assets()
    check("control system carries GEN-ARENA's L35 system string", ga.SYSTEM_BY_SOURCE[CORPUS] in system)
    check("control system carries GEN-ARENA's L39 rubric string", ga.RUBRIC_BY_SOURCE[CORPUS] in system)
    check("control system ends with the schema instruction", system.endswith(rj.SCHEMA_INSTRUCTION))
    check("control system sha == the READY's pin %s" % PINNED_SYSTEM_SHA, _sha16(system.encode("utf-8")) == PINNED_SYSTEM_SHA,
          _sha16(system.encode("utf-8")))
    target = json.dumps({"instruction_id_list": ids, "kwargs": kws})
    refblk = ref(CORPUS, target)
    check("control question block is GEN-ARENA's own reference()", refblk.startswith("\n\n[Constraints the response must satisfy]"), refblk[:60])

    m = dict(match_id=1, qid=7, model_a="A-model", model_b="B-model", key_winner="A-model", text="Q?", target=target,
             ids=ids, kwargs=kws, vec_a=[1, 1, 1], vec_b=[1, 0, 1], nt_a=0, nt_b=0,
             trace_a="TRACE-A", trace_b="TRACE-B", cache_winner="A-model", cache_flip=0)
    s_c, c1, c2 = assemble(m, "control")
    check("control arm carries no oracle block", not extract_blocks(c1) and not extract_blocks(c2))
    check("control orders differ only by the trace swap",
          c1.replace("TRACE-A", "\x00").replace("TRACE-B", "\x01") == c2.replace("TRACE-B", "\x00").replace("TRACE-A", "\x01"))
    s_t, t1, t2 = assemble(m, "treatment")
    b1, b2 = assert_transposition(m, t1, t2)
    check("TRANSPOSITION: order1(A) == order2(B)", b1[0] == b2[1])
    check("TRANSPOSITION: order1(B) == order2(A)", b1[1] == b2[0])
    check("the two contestants' blocks differ when their vectors differ", b1[0] != b1[1])
    check("the block travels with its trace, order 1", t1.index("TRACE-A") < t1.index(b1[0]) < t1.index("TRACE-B"))
    check("the block travels with its trace, order 2", t2.index("TRACE-B") < t2.index(b2[0]) < t2.index("TRACE-A"))
    check("treatment system is byte-identical to control system", s_t == s_c)
    # the regression test that matters: a DELIBERATELY transposed order 2 (the block stays in slot A while the traces swap)
    # must be refused. This is the artefact the registration calls indistinguishable from a catastrophic position effect.
    blk_a = oracle_block(m["ids"], m["kwargs"], m["vec_a"]); blk_b = oracle_block(m["ids"], m["kwargs"], m["vec_b"])
    q = m["text"] + ref(CORPUS, m["target"])
    bad2 = rj.build_user_prompt(q, m["trace_b"] + "\n\n" + blk_a, m["trace_a"] + "\n\n" + blk_b)
    try:
        assert_transposition(m, t1, bad2); ok = False
    except SystemExit:
        ok = True
    check("a TRANSPOSED order 2 is REFUSED (hard failure, not a warning)", ok)
    same_vec = dict(m); same_vec["vec_b"] = m["vec_a"]
    _s, e1, e2 = assemble(same_vec, "treatment")
    check("two all-pass contestants render identical blocks and still transpose cleanly",
          extract_blocks(e1)[0] == extract_blocks(e2)[1])

    configure_rr(); assert_payload_source()
    body = payload_body("S", "U")
    check("payload body == rejudge_reasoning.payload_body", body == rr.payload_body("S", "U"))
    check("temperature is OMITTED (Amendment 1 D2)", "temperature" not in body)
    check("cap is 8192", body["max_tokens"] == 8192)
    check("judge is the deployed grok", body["model"] == JUDGE)

    try:
        scrub("the accuracy 0.958 sits beside it", "a probe")
        ok = False
    except SystemExit:
        ok = True
    check("the MATH-ladder comparison is REFUSED, not commented", ok)
    try:
        refuse_math_comparison("a probe"); ok = False
    except SystemExit:
        ok = True
    check("refuse_math_comparison exits non-zero", ok)
    try:
        connect_ro(os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")); ok = False
    except SystemExit:
        ok = True
    check("connect_ro refuses a database outside the three of record", ok)
    check("exact McNemar is rejudge_reasoning's", abs(rr.mcnemar_p(10, 0) - 2 * 0.5 ** 10) < 1e-12)
    # D1: the support clause must carry the measured support and must NOT carry the struck inference
    fake = [dict(qid=i // 3) for i in range(12)]
    sr = support_readout(fake)
    check("support readout states the measured Kish size and the DEFF bracket", "Kish mean cluster size 3.000" in sr and "DEFF" in sr, sr)
    check("the struck 'optimistic end' inference is gone", "optimistic" not in sr and "rather than" not in sr)
    check("the registered MDEs and the 10pp floor are declared unchanged", "ARE UNCHANGED" in sr)
    lo, hi, sd = clustered({1: [1, 1], 2: [0, 1], 3: [1, 0]}, rate)
    check("question-clustered bootstrap runs", 0 <= lo <= hi <= 1 and sd > 0)
    ok, gs = gate_state()
    print("  gate: %s -> %s" % (gs, "GO" if ok else "would REFUSE a judged launch"))
    print("[SELFTEST] %d check(s) failed." % len(fails) if fails else "[SELFTEST] all checks passed; 0 calls, no database opened.")
    return 1 if fails else 0


# -- CLI ------------------------------------------------------------------------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="%s - %s" % (TEST, REGISTRATION))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="post N matches in BOTH arms (registered pilot: 12 matches = 48 calls)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--show-match", type=int, default=None, help="--dry-run: print this match's four payloads instead of the first")
    ap.add_argument("--night-spent", type=int, default=None, help="the night's cumulative call count if the queue's key is stale")
    ap.add_argument("--compare-math", action="store_true", help="REFUSED by the registration; the flag exists only to refuse")
    a = ap.parse_args()
    if a.compare_math:
        refuse_math_comparison("--compare-math")
    if a.selftest: sys.exit(selftest())
    if a.dry_run: sys.exit(dry_run(pilot=a.pilot, show=a.show_match))
    if a.pilot: sys.exit(run(pilot=a.pilot, workers=a.workers, night_override=a.night_spent))
    if a.run: sys.exit(run(pilot=None, workers=a.workers, night_override=a.night_spent))
    if a.analyze: sys.exit(analyze())
    ap.error("one of --selftest / --dry-run / --pilot N / --run / --analyze is required")
