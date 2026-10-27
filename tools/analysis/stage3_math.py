"""STAGE3-MATH - a generative arena on the union pool's MATH questions: STACK-v2/grok, dual order, the CHECKER
OUTPUT as the reference and the answer-disagreement filter on checker-normalised answers. FRAMEWORK.md item 23
("Tests to register before shipping"), registered by reference at eaf1dbf; docs/plan_2026-09-15.md Block 2 item f;
<= 3,000 matches, plan approved there.

  python tools/analysis/stage3_math.py --dry-run [--pilot N]           0 calls: every payload assembled, nothing posted
  python tools/analysis/stage3_math.py --judge --pilot 12 --workers 8   the 12-match pilot the plan asks for
  python tools/analysis/stage3_math.py --analyze --pilot 12             truncation guard on the pilot, readouts withheld;
                                                                        EXIT 2 on VERDICT REFUSED or an empty cache, so
                                                                        an && chain into the full run is gated (D7)
  python tools/analysis/stage3_math.py --judge --workers 8              the run (resumes from its own cache)
  python tools/analysis/stage3_math.py --analyze                        registered readouts -> stage3_math_outcome.txt
                                                                        (PARTIAL, no REGISTERED line, while the cache
                                                                        is short of the schedule)

POOL. Questions are the 398 MATH questions of the union pool of record paeec37aa28063c75, addressed BY EXPLICIT ID
from reserved_pool on multicorpus_cache_v1.db by explicit pool id. Two guards run before anything else:
pool_guard.assert_pool_of_record(MMLU_PRO_POOL) (the MMLU-Pro pool of record reproduces by id, the standing rule for
every judged script) and the union DB's active pool must be paeec37aa28063c75. The pool id is the first line printed.

CHECKER. Block 1 item 7 (CHECKER-ANSWER-INGEST, tools/analysis/checker_answer_ingest.py) wrote
experiment_results/multicorpus/checker_answers_v1.db :: math_checker_answers (question_id, model_name, x_raw, x_norm,
x_canon, tier, non_terminated, checker_correct, mathfix_correct). This script reads that table and REFUSES TO RUN when
the file, the table, its columns or its provenance row is absent. Three facts per (question, model) come from it:
x(q, m), the checker-normalised answer that the filter compares; non_terminated(q, m), the NON_TERMINATED rule (a
response that opens <think> and never closes it is NOT an extraction); and k(q, m) = checker_correct, the key that the
readouts score against (identical to eval_results_mathfix; item 7 cross-checked 0 of 23,832 rows differ).

FILTER (FRAMEWORK L63, MatchFilter.kt keep()). A (pair, question) is eligible iff the two checker answers are not
AGREE: DISAGREE (both extracted, x_a != x_b under the Kotlin rule, trimmed case-insensitive string equality on x_norm)
or UNDETERMINED (an extraction missing, kept and carried as its own class). Item 7's VERDICT OF RECORD is reading B
(checker extraction tier 1-3 + the NON_TERMINATED rule): FAIL on the 18-model source row at D_c 0.827 (min domain cell
0.768), a roster property of the two R1 distills; reading C (EXPLICIT, tier 1-2 only, D_c 0.39) is a diagnostic, not
the verdict. On this eight-model roster non_terminated = 0 for every model, so reading B coincides with reading A and
the run's cell is D_c 0.994 (Amendment 1 D7; the dry-run prints D_c per MATH domain beside the source row). --reading
picks the reading (default full = reading B: every non-null x_norm with the NON_TERMINATED rule applied in answer();
explicit = tier 1-2 only, the diagnostic); --compare picks the string (norm = the record's rule, canon = numerically
canonical); --filter disagree drops UNDETERMINED as well. Non-default choices get their own cache; the dry-run prints
the eligibility under every reading so the choice is visible before a call.

SCHEDULE. GEN-ARENA's design (generative_arena.py): the same eight-model roster, all 28 pairs, uniform per pair,
PER_PAIR = 3000 // 28 = 107 questions per pair drawn without replacement (random.Random(42)) from the pair's
ELIGIBLE questions with both traces non-empty, sides randomised. The whole deck is then SHUFFLED ONCE under the same
seed-42 generator BEFORE match ids are assigned from MID0, so a --pilot prefix spans pairs and domains instead of one
pair (Amendment 1 D7). 28 x 107 = 2,996 matches <= the 3,000 cap; x2 orders = 5,992 calls. Meta-Llama-3-70B-Instruct
is not on the roster and is refused if it ever is.

JUDGE. STACK-v2/grok exactly as RECIPE-GROK / ARENA-V2 / GEN-ARENA ran it: grok-4-1-fast-non-reasoning on the Azure
deployment, prompt_v2's verify-first system template with GEN-ARENA's MATH system prompt and rubric in the
$systemPrompt / $rubric slots (the union trees are label-free; no induced anchor rubric exists for MATH; that pair
scored 0.935 on GEN-ARENA), rejudge_grok.SCHEMA_INSTRUCTION appended, the reference block "[Verified reference
answer]\\n<target>" appended to the question byte-identically to GEN-ARENA (CHECKER_OUTPUT, 0 cce, no solve minted),
rejudge_grok.build_user_prompt for the user turn, both orders judged, rejudge_grok.combine_orders (TIE on flip,
INVALID if either order fails to parse), confidence recorded and never gated. Every call goes through
rejudge_reasoning.call_judge_full; finish_reason and completion_tokens are stored per order; finish_reason == length
is NON_TERMINATED (FRAMEWORK L73): the order's vote is set to INVALID, never a verdict and never a tie.
REFERENCE. The block shows the pool's RAW target verbatim under GEN-ARENA's header (part of the 0.935 record): the
checker's normalised form (MATH-FIX) is an internal comparison form ('[01)', '(128)/(3)'; differs from the raw target
on 104 of 398 pool targets) and is never shown to the judge. The v2 template's "marked as produced independently; it
may be wrong" wording is an inherited inconsistency, kept for comparability with GEN-ARENA; stated in the outcome.
TEMPERATURE is OMITTED from the payload (provider default; Amendment 1 D2): every cache this run is compared with
omitted it; recorded in the cache's meta table and printed in every outcome header; judge() refuses to post otherwise.

READOUTS (registered, item 23): (1) key-decidable accuracy under both tie conventions, A ties-as-wrong and B ties
excluded, bar 0.75 each, prediction >= 0.90 (convention A with INVALID matches counted wrong printed beside, the
truncations-wrong figure); (2) the 8-model board's Spearman rho vs checker accuracy over ALL 398 pool questions with
a question-clustered bootstrap CI (B = 2000; the judged-question figure printed beside); (3) the raw wrong-direction
rate among called edges with its upper bound (normal and exact), nominal printed beside every wrong count;
calibration UNDETERMINED by design (28 pairs, nominal < 3 at every threshold). GUARD: the deciding subset is the
key-decidable matches; when more than 5% of it is unparsed or non-terminated the verdict is REFUSED, nothing below
the guard is printed as a result and --analyze EXITS 2 (the overall rate over all judged matches is printed beside).
PARTIAL: while the cache holds fewer verdicts than the schedule (errored calls are never cached), the readouts are
labelled PARTIAL, written to stage3_math_outcome_PARTIAL.txt and carry no REGISTERED line; re-run --judge to resume.

RE-REGISTRATION OPTIONS (2026-09-16, STAGE3-MATH HELD; consequence of CHECKER-ANSWER-INGEST's HIGH finding that the
`<think>` proxy is not the NON_TERMINATED rule: the harness caps MATH generation at 1,024 tokens and 12-19% of the
roster's eval-side rows end at that cap with no marker).
  --checker-table v1|v2   v1 (default; the held registration stays reproducible) = checker_answers_v1.db ::
                          math_checker_answers, non_terminated = the `<think>` proxy. v2 = checker_answers_v2.db ::
                          math_checker_answers_v2 (checker_answer_ingest.py --v2), non_terminated = the CONSISTENT
                          proxy (unclosed <think> OR cl100k >= 960 with an abrupt end); columns are mapped onto the
                          same (x_norm, x_canon, tier, non_terminated, checker_correct) tuple. Cache tag _v2.
  --terminated-only       the "both traces terminated" rule: a (pair, question) is eligible only if NEITHER response
                          is non_terminated under the consistent proxy (requires --checker-table v2; refused on v1,
                          whose column is the `<think>` proxy). Applied BEFORE the answer-disagreement filter, so a
                          cap-hit response is excluded rather than carried as UNDETERMINED. Cache tag _capfree. The
                          schedule is rebuilt under the same seed 42, PER_PAIR and deck shuffle on the smaller
                          population; the dry-run prints the resulting cell's D_c (row and min domain) under reading
                          B with the consistent proxy, the eligible question-pairs, matches, key-decidable count and
                          whether item 7's rule (>= 0.95 on the row AND the min domain cell) is MET.
"""
import os, sys, json, math, time, random, sqlite3, argparse, hashlib, threading, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import judge_free_tests as jf
import prompt_v2
import generative_arena as ga

def judge_full(system, user):
    """rr.call_judge_full, with a provider REFUSAL made visible: an HTTP 400 whose body carries finish_reason=content_filter
    is deterministic (re-posting it forever stalls the run; not caching it makes the match vanish from the guard
    denominator, the class that lost 4389 and 6528 in ARENA-V2). It returns an EMPTY content with finish_reason
    'content_filter', which parses as INVALID and counts against the 5% guard like a truncation. Every other HTTP error
    is still raised and re-posted on resume. Added 2026-09-16 after NEWCOMER-PLACEMENT-LIVE hit one on a History match."""
    try:
        return rr.call_judge_full(system, user)
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode("utf-8", "replace")
        except Exception: pass
        if e.code == 400 and "content_filter" in body:
            return ("", "azure:refusal", 0, 0.0, "content_filter", None)
        raise


try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

POOL_ID = "paeec37aa28063c75"                       # the union pool of record; its MATH slice = 398 questions
DB = os.path.join(ROOT, "multicorpus_cache_v1.db")   # where that pool is recorded and active
OUT_DIR = os.path.join(ROOT, "experiment_results", "multicorpus")
# Block 1 item 7's product (v1, the held registration) and its --v2 extension (the consistent cap proxy). Each entry:
# (db file, table, meta table, provenance 'script' value, column map onto (x_norm, x_canon, tier, non_terminated, checker_correct)).
CHECKER_TABLES = {
    "v1": (os.path.join(OUT_DIR, "checker_answers_v1.db"), "math_checker_answers", "checker_answer_ingest_meta",
           "tools/analysis/checker_answer_ingest.py", ("x_norm", "x_canon", "tier", "non_terminated", "checker_correct")),
    "v2": (os.path.join(OUT_DIR, "checker_answers_v2.db"), "math_checker_answers_v2", "checker_answer_ingest_v2_meta",
           "tools/analysis/checker_answer_ingest.py --v2", ("answer_norm", "answer_canon", "tier", "non_terminated", "is_correct")),
}
CHECKER_DB, CHECKER_TABLE, CHECKER_META, CHECKER_SCRIPT, CHECKER_COLS = CHECKER_TABLES["v1"]
CACHE_BASE = os.path.join(OUT_DIR, "stage3_math_grok.db")       # own cache, never gen_arena_grok.db
OUTCOME = os.path.join(OUT_DIR, "stage3_math_outcome.txt")             # written ONLY by a complete, non-pilot analyze
OUTCOME_PILOT = OUTCOME.replace(".txt", "_pilot.txt")                  # the pilot's truncation-guard read
OUTCOME_PARTIAL = OUTCOME.replace(".txt", "_PARTIAL.txt")              # readouts on an incomplete cache, no REGISTERED line
JUDGE = "grok-4-1-fast-non-reasoning"
PROVIDER = "azure"
PROTOCOL = ("STACK-v2/grok: prompt_v2 verify-first system template + GEN-ARENA MATH system prompt and rubric + "
            "SCHEMA_INSTRUCTION; CHECKER_OUTPUT reference block '[Verified reference answer]'; dual order, TIE on flip, "
            "INVALID on parse failure or finish_reason=length; confidence recorded, never gated")
MAXTOK_DEFAULT = rr.MAX_TOKENS                      # 8192 = rejudge_reasoning's budget, the one GEN-ARENA and ARENA-V2 posted
CAP = 3000                                          # <= 3,000 matches (plan approved), x2 orders = <= 6,000 calls
ROSTER = list(ga.ROSTER)                            # GEN-ARENA's eight, unchanged
EXCLUDED = {"Meta-Llama-3-70B-Instruct", "Meta-Llama-3-70B-Instruct-lb"}
PAIRS = [(ROSTER[i], ROSTER[j]) for i in range(len(ROSTER)) for j in range(i + 1, len(ROSTER))]
PER_PAIR = CAP // len(PAIRS)                        # 107 x 28 = 2,996 matches
SEED = 42
MID0 = 70_000_000
UNPARSED_BAR = 0.05
SYSTEM_MATH = ga.SYSTEM_BY_SOURCE["MATH"]
RUBRIC_MATH = ga.RUBRIC_BY_SOURCE["MATH"]
REF_BLOCK = "\n\n[Verified reference answer]\n%s"   # GEN-ARENA's block, byte-identical

# run parameters (set from the command line)
MAXTOK = MAXTOK_DEFAULT
READING = "full"        # full = every non-null x_norm (tier 1-3); explicit = tier 1-2 only (item 7's hardest reading)
COMPARE = "norm"        # norm = x_norm under the Kotlin rule; canon = x_canon (numerically canonical)
FILTER = "keep"         # keep = not AGREE (DISAGREE + UNDETERMINED, MatchFilter.keep()); disagree = DISAGREE only
CHECKER_VERSION = "v1"  # v1 = the held registration's table (<think> proxy); v2 = the consistent cap proxy
TERMINATED_ONLY = False # the "both traces terminated" rule (requires v2); cache tag _capfree


def script_sha256():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def cache_path():
    """Own cache, named for the run. Any non-default filter reading or completion budget changes the schedule or
    the calls, so it gets its own file (ref_qualify's rule): a voided run stays as evidence, never overwritten."""
    p = CACHE_BASE
    tag = "".join(s for s, on in (("_v2", CHECKER_VERSION == "v2"), ("_capfree", TERMINATED_ONLY),
                                  ("_explicit", READING == "explicit"), ("_canon", COMPARE == "canon"),
                                  ("_disagree", FILTER == "disagree"), ("_mt%d" % MAXTOK, MAXTOK != MAXTOK_DEFAULT)) if on)
    return p.replace(".db", tag + ".db")


def guard():
    """First thing every entry point does. (1) pool_guard.assert_pool_of_record(MMLU_PRO_POOL): the MMLU-Pro pool of
    record reproduces from its id file and the dataset DB's rows (the standing rule for every judged script).
    (2) The union pool of record reproduces likewise on the union DB. Questions are then drawn by explicit id."""
    dataset_pool = pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)       # verified by id, printed as returned
    pool_guard.assert_pool_of_record(POOL_ID)
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    try:
        union_pool = pool_guard.assert_frozen_pool(con, POOL_ID)
        n = con.execute("SELECT COUNT(*) FROM reserved_pool r JOIN corpus_questions q USING(question_id) "
                        "WHERE r.pool_id=? AND q.source='MATH'", (POOL_ID,)).fetchone()[0]
    finally:
        con.close()
    print("[POOL] %s (union pool of record, verified by id on %s) | MATH questions in the pool: %d | MMLU-Pro dataset DB pool %s"
          % (union_pool, os.path.basename(DB), n, dataset_pool), flush=True)
    assert not (EXCLUDED & set(ROSTER)), "excluded model in the roster"
    assert len(ROSTER) == 8 and len(PAIRS) == 28, "roster is not GEN-ARENA's"


def source_rows():
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    pool = [q for (q,) in con.execute("SELECT r.question_id FROM reserved_pool r JOIN corpus_questions q USING(question_id) "
                                      "WHERE r.pool_id=? AND q.source='MATH' ORDER BY r.question_id", (POOL_ID,))]
    ps = set(pool)
    meta = {q: (t, tg, d) for q, t, tg, d in con.execute("SELECT question_id, text, target, domain FROM corpus_questions WHERE source='MATH'") if q in ps}
    outputs = {(q, m): (o or "") for q, m, o in con.execute("SELECT question_id, model_name, model_output FROM eval_results") if q in ps and m in ROSTER}
    con.close()
    return pool, meta, outputs


def checker_answers(pool):
    """(question_id, model_name) -> (x, k): x = the checker-normalised answer the filter compares (None when not
    extracted under --reading / --compare), k = checker_correct. Read from CHECKER-ANSWER-INGEST's table; REFUSES when
    the file, the table, its columns or its provenance row are missing. There is no fallback: this run needs item 7.
    Also returns R, the raw roster rows (x_norm, x_canon, tier, non_terminated, k), so the dry-run can print every
    reading side by side, and R18, the same rows for ALL corpus models on the pool (item 7's 18-model source row)."""
    if not os.path.exists(CHECKER_DB):
        raise SystemExit("[CHECKER] %s is absent: Block 1 item 7 (CHECKER-ANSWER-INGEST) has not landed; refusing to run" % CHECKER_DB)
    con = sqlite3.connect("file:%s?mode=ro" % CHECKER_DB, uri=True)
    have = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if CHECKER_TABLE not in have or CHECKER_META not in have:
        raise SystemExit("[CHECKER] %s lacks %s / %s (have %s); refusing to run" % (os.path.basename(CHECKER_DB), CHECKER_TABLE, CHECKER_META, sorted(have)))
    cols = {r[1] for r in con.execute("PRAGMA table_info(%s)" % CHECKER_TABLE)}
    need = ("question_id", "model_name") + CHECKER_COLS
    missing = [c for c in need if c not in cols]
    if missing:
        raise SystemExit("[CHECKER] %s lacks columns %s (have %s); refusing to run" % (CHECKER_TABLE, missing, sorted(cols)))
    mt = dict(con.execute("SELECT key, value FROM %s" % CHECKER_META))
    if mt.get("script") != CHECKER_SCRIPT or mt.get("union_pool") != POOL_ID:
        raise SystemExit("[CHECKER] provenance mismatch: script=%r union_pool=%r; refusing to run" % (mt.get("script"), mt.get("union_pool")))
    ps = set(pool); R = {}; R18 = {}; tiers = defaultdict(int); nt_by_model = defaultdict(int)
    for q, m, xn, xc, tier, nt, k in con.execute("SELECT question_id, model_name, %s FROM %s" % (", ".join(CHECKER_COLS), CHECKER_TABLE)):
        if q not in ps or m in EXCLUDED: continue
        row = (xn, xc, int(tier or 0), int(nt or 0), None if k is None else int(k))
        R18[(q, m)] = row
        if m not in ROSTER: continue
        R[(q, m)] = row; tiers[int(tier or 0)] += 1; nt_by_model[m] += int(nt or 0)
    con.close()
    miss = [(q, m) for q in pool for m in ROSTER if (q, m) not in R]
    if miss:
        raise SystemExit("[CHECKER] %d (question, model) rows of the pool x roster are missing from %s; refusing to run" % (len(miss), CHECKER_TABLE))
    X = {qm: (answer(r, READING, COMPARE), r[4]) for qm, r in R.items()}
    src = "%s::%s written %s (reading=%s compare=%s filter=%s%s)" % (os.path.basename(CHECKER_DB), CHECKER_TABLE, mt.get("written_at"), READING, COMPARE, FILTER,
                                                                   " terminated-only" if TERMINATED_ONLY else "")
    print("[CHECKER] %s | non_terminated column = %s | pool x roster rows %d | extraction tier counts %s | NON_TERMINATED rows per roster model %s (total %d of %d)"
          % (src, mt.get("non_terminated"), len(X), dict(sorted(tiers.items())), dict(nt_by_model), sum(nt_by_model.values()), len(X)), flush=True)
    return X, src, R, R18


def answer(r, reading, compare):
    """The checker-normalised answer a reading compares, or None when the reading treats it as not extracted.
    Mirrors item 7's X_A / X_B / X_C (checker_answer_ingest.py): 'checker' = reading A, every row as the checker
    parses it; 'full' = reading B, the VERDICT OF RECORD, A plus the NON_TERMINATED rule (an unclosed <think> is a
    truncation by construction and its fallback number is not an answer); 'explicit' = reading C, tier 1-2 only,
    the fallback treated as a guess, no NON_TERMINATED rule (item 7 applies none to X_C), the diagnostic."""
    xn, xc, tier, nt, _ = r
    x = xc if compare == "canon" else xn
    if x is None or not str(x).strip(): return None
    if reading == "explicit": return str(x) if tier in (1, 2) else None
    if reading == "full" and nt: return None
    return str(x)


def dc_of(A, qs):
    """D_c on a set of questions for an answer map A[(q, m)]: share of question-pairs (all pairs of the models present)
    with two non-blank extracted answers; also the AGREE share under the Kotlin string rule. Item 7's definition."""
    models = sorted({m for (_, m) in A}); pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    det = ag = 0
    for q in qs:
        for a, b in pairs:
            xa, xb = A.get((q, a)), A.get((q, b))
            if xa is None or xb is None: continue
            det += 1; ag += str_eq(xa, xb)
    cells = len(qs) * len(pairs)
    return det / max(1, cells), ag / max(1, cells), cells


def dc_masked(A, R, qs):
    """D_c restricted to the population the --terminated-only rule admits: question-pairs where BOTH responses are
    terminated under R's non_terminated column. Returns (D_c, AGREE share, admitted question-pairs, all question-pairs)."""
    models = sorted({m for (_, m) in A}); pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    det = ag = adm = 0
    for q in qs:
        for a, b in pairs:
            if not (terminated(R, q, a) and terminated(R, q, b)): continue
            adm += 1; xa, xb = A.get((q, a)), A.get((q, b))
            if xa is None or xb is None: continue
            det += 1; ag += str_eq(xa, xb)
    return det / max(1, adm), ag / max(1, adm), adm, len(qs) * len(pairs)


def str_eq(a, b):
    """MatchFilter.kt: trimmed, case-insensitive string equality."""
    return a.strip().lower() == b.strip().lower()


def filter_verdict(X, q, a, b):
    xa, xb = X[(q, a)][0], X[(q, b)][0]
    if xa is None or xb is None: return "UNDETERMINED"
    return "AGREE" if str_eq(xa, xb) else "DISAGREE"


def terminated(R, q, m):
    """True when the response is not NON_TERMINATED under the checker table's column (the consistent proxy on v2)."""
    return not R[(q, m)][3]


def eligible(X, outputs, q, a, b, R=None):
    if TERMINATED_ONLY:
        assert R is not None, "--terminated-only needs the raw checker rows; build_schedule must be called with R"
        if not (terminated(R, q, a) and terminated(R, q, b)): return None   # both traces terminated, else excluded
    v = filter_verdict(X, q, a, b)
    if v == "AGREE": return None
    if FILTER == "disagree" and v != "DISAGREE": return None
    if not outputs.get((q, a), "").strip() or not outputs.get((q, b), "").strip(): return None   # an empty trace cannot be judged
    return v


def build_schedule(pool, X, outputs, meta, R=None):
    """GEN-ARENA's design with the disagreement filter: PER_PAIR matches per pair, questions drawn without
    replacement from the pair's eligible questions (seed 42), sides randomised. The whole deck is then SHUFFLED
    ONCE under the same generator BEFORE match ids are assigned from MID0 (Amendment 1 D7; GEN-ARENA and
    rejudge_grok.sample_matches shuffle their decks the same way), so a --pilot prefix spans pairs and domains
    instead of the first pair. Deterministic under seed 42. Rows carry the filter verdict and the domain."""
    rng = random.Random(SEED); deck = []; stats = []
    for a, b in PAIRS:
        elig = [(q, v) for q in pool for v in [eligible(X, outputs, q, a, b, R)] if v]
        take = list(elig); rng.shuffle(take); take = sorted(take[:PER_PAIR])
        for q, v in take:
            x, y = (a, b) if rng.random() < 0.5 else (b, a)
            deck.append((q, x, y, v, meta[q][2]))
        stats.append((a, b, len(elig), len(take)))
    rng.shuffle(deck)                                   # once, whole deck, before ids
    rows = [(MID0 + i, "MATH", q, x, y, v, dom) for i, (q, x, y, v, dom) in enumerate(deck)]
    return rows, stats


def system_prompt():
    return (prompt_v2.v2_system_template().replace("$systemPrompt", SYSTEM_MATH).replace("$rubric", RUBRIC_MATH)
            + "\n\n" + rj.SCHEMA_INSTRUCTION)


def payloads(m, meta, outputs):
    """(system, user order 1, user order 2) for one match."""
    mid, source, qid, a, b = m[:5]
    text, target, _ = meta[qid]
    ta, tb = outputs[(qid, a)], outputs[(qid, b)]
    q = text + REF_BLOCK % target
    return system_prompt(), rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)


def configure_rr():
    """Point rejudge_reasoning at this run's judge exactly as judge() posts it (no env, no network). D2: the
    temperature field is OMITTED from the payload; refuse to proceed if anything has set rr.TEMPERATURE."""
    rr.PROVIDER = PROVIDER; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK
    if rr.TEMPERATURE is not None:
        raise SystemExit("[D2] rejudge_reasoning.TEMPERATURE is %r; Amendment 1 D2 fixes the payload's temperature as OMITTED" % (rr.TEMPERATURE,))


def post_body(system, user):
    """LOCAL COPY of the request body rejudge_reasoning.call_judge_full assembles (rejudge_reasoning.py lines 92-96:
    payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS, "messages": [system, user]}; "temperature" only
    when TEMPERATURE is not None). Kept here so the dry-run can print the model field of the body that WILL be
    posted; assert_body_copy() checks the source lines and the key tuple so a later change to call_judge_full
    cannot make the printed body differ silently from the posted one (that module is not edited by this script)."""
    body = {"model": rr.JUDGE_MODEL, "max_tokens": rr.MAX_TOKENS,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if rr.TEMPERATURE is not None: body["temperature"] = rr.TEMPERATURE
    return body


def assert_body_copy(body):
    import inspect
    src = inspect.getsource(rr.payload_body)   # 2026-09-16: the body builder was factored out of call_judge_full (JUDGE-WIRING), bytes unchanged
    assert "payload_bytes(system, user)" in inspect.getsource(rr.call_judge_full), "call_judge_full no longer posts payload_body's bytes"
    assert 'payload_body = {"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,' in src and 'payload_body["temperature"] = TEMPERATURE' in src \
        and '{"role": "system", "content": system}' in src and '{"role": "user", "content": user}' in src, \
        "rejudge_reasoning.call_judge_full no longer builds the body post_body() copies; re-verify the copy"
    want = ("model", "max_tokens", "messages") + (("temperature",) if rr.TEMPERATURE is not None else ())
    assert tuple(body) == want, "body key tuple %r != %r" % (tuple(body), want)
    assert body["model"] == JUDGE and body["max_tokens"] == MAXTOK, "body carries a judge or budget this run did not set"


def open_cache():
    p = cache_path()
    assert os.path.abspath(p) != os.path.abspath(ga.CACHE), "cache must not be GEN-ARENA's"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS schedule (match_id INTEGER PRIMARY KEY, source TEXT, qid INTEGER, model_a TEXT, model_b TEXT, "
                "filter_verdict TEXT, domain TEXT)")
    # GEN-ARENA's verdicts columns in GEN-ARENA's order, then the per-order finish_reason and completion tokens.
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, source TEXT, qid INTEGER, model_a TEXT, model_b TEXT, "
                "vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, "
                "finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER)")
    con.commit(); return con


def run_params(checker_src):
    return {"pool_id": POOL_ID, "judge": JUDGE, "provider": PROVIDER, "protocol": PROTOCOL, "max_tokens": str(MAXTOK),
            "temperature": "omitted (provider default)" if rr.TEMPERATURE is None else str(rr.TEMPERATURE),
            "cap_matches": str(CAP), "per_pair": str(PER_PAIR), "seed": str(SEED), "reading": READING, "compare": COMPARE,
            "filter": FILTER, "checker_table": CHECKER_VERSION, "terminated_only": str(int(TERMINATED_ONLY)),
            "checker_source": checker_src, "roster": json.dumps(ROSTER), "script_sha256": script_sha256()}


def stamp(con, checker_src):
    want = run_params(checker_src)
    have = dict(con.execute("SELECT key, value FROM meta"))
    if have:
        fixed = ("pool_id", "judge", "provider", "protocol", "max_tokens", "temperature", "reading", "compare", "filter", "checker_table", "terminated_only", "checker_source", "roster")
        diff = {k: (have.get(k), want[k]) for k in fixed if have.get(k) != want[k]}
        if diff: raise SystemExit("[CACHE] %s was written under different parameters %s; use a fresh cache" % (cache_path(), diff))
        # 'created' and the producing script's sha are pinned at first launch; every resume is APPENDED, never overwritten
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("resumed:%s" % time.strftime("%Y-%m-%d %H:%M:%S"), script_sha256())); con.commit()
        return
    con.executemany("INSERT INTO meta VALUES (?,?)", list(want.items()) + [("created", time.strftime("%Y-%m-%d %H:%M:%S"))]); con.commit()


def plan(pilot):
    """Everything --dry-run and --judge share, at zero calls: pool, checker answers, schedule, per-pair stats."""
    pool, meta, outputs = source_rows()
    X, checker_src, R, R18 = checker_answers(pool)
    cells = len(pool) * len(PAIRS)
    # Item 7's three readings on this run's cell (the 8-model roster x the 398 pool questions), the verdict-of-record
    # reading B marked; then B's D_c per MATH domain stratum (item 7's cell rule = source row AND min domain cell)
    # beside the 18-model source row recomputed from the same table.
    for label, rd, cp in (("A checker every row / norm      ", "checker", "norm"), ("B + NON_TERMINATED / norm [RECORD]", "full", "norm"),
                          ("B + NON_TERMINATED / canon      ", "full", "canon"), ("C explicit tier 1-2 / norm      ", "explicit", "norm")):
        A = {qm: answer(r, rd, cp) for qm, r in R.items()}
        dc, ag, _ = dc_of(A, pool)
        print("[CHECKER] reading %s: D_c %.3f | AGREE %.3f | offered (not AGREE) %.3f | DISAGREE %.3f | UNDETERMINED %.3f%s"
              % (label, dc, ag, 1 - ag, dc - ag, 1 - dc, "   <- this run" if (rd, cp) == (READING, COMPARE) else ""), flush=True)
    A_run = {qm: answer(r, READING, COMPARE) for qm, r in R.items()}
    by_dom = defaultdict(list)
    for q in pool: by_dom[meta[q][2]].append(q)
    per_dom = {d: dc_of(A_run, qs)[0] for d, qs in by_dom.items()}
    mn = min(per_dom, key=per_dom.get)
    A18 = {qm: answer(r, "full", "norm") for qm, r in R18.items()}
    n18 = len({m for (_, m) in A18}); src18 = dc_of(A18, pool)[0]; src18_dom = {d: dc_of(A18, qs)[0] for d, qs in by_dom.items()}
    mn18 = min(src18_dom, key=src18_dom.get)
    print("[CHECKER] D_c per MATH domain, this run's cell (reading=%s compare=%s, %d models): %s | min cell %.3f at %s -> item 7 rule (>= 0.95 on the row AND the min cell): %s"
          % (READING, COMPARE, len(ROSTER), ", ".join("%s %.3f (q=%d)" % (d, per_dom[d], len(by_dom[d])) for d in sorted(per_dom)), per_dom[mn], mn,
             "MET" if min(dc_of(A_run, pool)[0], per_dom[mn]) >= 0.95 else "NOT MET"), flush=True)
    print("[CHECKER] beside: item 7's %d-model source row under reading B from the same table: D_c %.3f | min domain cell %.3f at %s (item 7 recorded 0.827 / 0.768 on the <think> proxy; CHECKER-ANSWER-INGEST's checker 0.670 on the consistent proxy)"
          % (n18, src18, src18_dom[mn18], mn18), flush=True)
    if TERMINATED_ONLY:
        # the RESULTING cell: question-pairs where both responses are terminated under the consistent proxy (the
        # population the schedule is drawn from); item 7's rule read on it, the unfiltered cell printed above it
        A_B = {qm: answer(r, READING, COMPARE) for qm, r in R.items()}  # the schedule's own reading/compare [checker 2026-09-16]
        row = dc_masked(A_B, R, pool); per = {d: dc_masked(A_B, R, qs) for d, qs in by_dom.items()}
        mnt = min(per, key=lambda d: per[d][0])
        print("[CHECKER] --terminated-only: the RESULTING cell = question-pairs with BOTH responses terminated under the consistent proxy: %d of %d question-pairs admitted (%.1f%%); "
              "reading B / norm on it: D_c %.4f (row) | per domain %s | min cell %.4f at %s -> item 7 rule (>= 0.95 on the row AND the min cell): %s"
              % (row[2], row[3], 100 * row[2] / row[3], row[0], ", ".join("%s %.3f (%d/%d)" % (d, per[d][0], per[d][2], per[d][3]) for d in sorted(per)),
                 per[mnt][0], mnt, "MET" if min(row[0], per[mnt][0]) >= 0.95 else "NOT MET"), flush=True)
        print("[CHECKER] --terminated-only: residual blanks on the admitted population are extraction-tier-0 responses (no boxed / 'final answer' / trailing number), not truncations; "
              "the unfiltered 8-model cell above (D_c %.3f, min %.3f) is what the cap costs the registration as scheduled" % (dc_of(A_run, pool)[0], per_dom[mn]), flush=True)
    rows, stats = build_schedule(pool, X, outputs, meta, R)
    offered = sum(e for _, _, e, _ in stats)
    by_v = defaultdict(int)
    for r in rows: by_v[r[5]] += 1
    K = {(q, m): X[(q, m)][1] for q in pool for m in ROSTER}
    dec = sum(1 for r in rows if K[(r[2], r[3])] is not None and K[(r[2], r[4])] is not None and K[(r[2], r[3])] != K[(r[2], r[4])])
    print("[SCHEDULE] %d pairs x %d per pair | eligible question-pairs %d of %d (%.1f%%, both traces non-empty) | %d matches over %d distinct questions | "
          "filter verdicts %s | expected key-decidable %d (%.1f%%)"
          % (len(PAIRS), PER_PAIR, offered, cells, 100 * offered / cells, len(rows), len({r[2] for r in rows}), dict(by_v), dec, 100 * dec / max(1, len(rows))), flush=True)
    for a, b, e, t in stats:
        if t < PER_PAIR: print("  EXHAUSTED %s vs %s: %d eligible < %d" % (a, b, e, PER_PAIR), flush=True)
    assert len(rows) <= CAP, "schedule exceeds the cap"
    assert [r[0] for r in rows] == list(range(MID0, MID0 + len(rows))), "match ids must be contiguous from MID0 after the deck shuffle"
    if pilot:
        rows = rows[:pilot]
        pd = defaultdict(int)
        for r in rows: pd[r[6]] += 1
        print("[PILOT] first %d matches of the shuffled deck span %d pairs and %d domains %s | key-decidable %d"
              % (len(rows), len({frozenset((r[3], r[4])) for r in rows}), len(pd), dict(sorted(pd.items())),
                 sum(1 for r in rows if K[(r[2], r[3])] is not None and K[(r[2], r[4])] is not None and K[(r[2], r[3])] != K[(r[2], r[4])])), flush=True)
    return pool, meta, outputs, X, checker_src, rows, R


def dry_run(pilot):
    pool, meta, outputs, X, checker_src, rows, R = plan(pilot)
    configure_rr()                                       # what judge() sets before posting; no env, no network
    built = [(m, payloads(m, meta, outputs)) for m in rows]
    bodies = [post_body(s, u) for _, (s, u1, u2) in built for u in (u1, u2)]
    for b in bodies: assert_body_copy(b)
    print("\n=== STAGE3-MATH DRY-RUN: nothing posted ===")
    print("  pool of record      %s (MATH slice, %d questions, drawn by explicit id)" % (POOL_ID, len(pool)))
    print("  protocol            %s" % PROTOCOL)
    print("  judge               %s | provider %s | max_tokens %d | temperature %s" % (JUDGE, PROVIDER, MAXTOK, "omitted (provider default)" if rr.TEMPERATURE is None else rr.TEMPERATURE))
    print("  temperature (D2)    OMITTED from the payload by Amendment 1 D2: recorded in meta as 'omitted (provider default)', printed in every outcome header")
    print("  cap                 %d matches = %d calls (plan approved); scheduled %d matches%s" % (CAP, 2 * CAP, len(rows), " (pilot)" if pilot else ""))
    print("  calls this run      %d matches x 2 orders = %d calls" % (len(built), 2 * len(built)))
    print("  max_tokens          %d (%s)" % (MAXTOK, "default = rejudge_reasoning.MAX_TOKENS" if MAXTOK == MAXTOK_DEFAULT else "non-default; own cache"))
    print("  cache               %s" % cache_path())
    print("  checker source      %s" % checker_src)
    print("  filter              reading=%s compare=%s filter=%s (eligible = not AGREE%s)%s" % (READING, COMPARE, FILTER, "; UNDETERMINED dropped" if FILTER == "disagree" else ", UNDETERMINED kept",
          "; --terminated-only: a question-pair with either response NON_TERMINATED under the consistent proxy is EXCLUDED before the filter" if TERMINATED_ONLY else ""))
    print("  checker table       %s = %s::%s (non_terminated = %s)" % (CHECKER_VERSION, os.path.basename(CHECKER_DB), CHECKER_TABLE, "the consistent cap proxy" if CHECKER_VERSION == "v2" else "the <think> proxy of the held registration"))
    print("  reference           the pool's RAW target verbatim under GEN-ARENA's header '[Verified reference answer]' (CHECKER_OUTPUT; the checker's normalised form is an internal comparison form, never shown)")
    print("  roster              %s" % ", ".join(ROSTER))
    print("  excluded            %s" % ", ".join(sorted(EXCLUDED)))
    print("  script sha256       %s" % script_sha256())
    if built:
        (mid, _, qid, a, b, fv, dom), (system, u1, u2) = built[0]
        print("\n--- first payload: match %d, question %d (%s, filter %s), order 1 = %s (A) vs %s (B); order 2 swaps the traces ---" % (mid, qid, dom, fv, a, b))
        print("--- BODY (as rejudge_reasoning.call_judge_full posts it; local copy asserted against its source) ---")
        print("    model %s | max_tokens %d | keys %s | messages [system %d chars, user %d chars]"
              % (bodies[0]["model"], bodies[0]["max_tokens"], tuple(bodies[0]), len(system), len(u1)))
        print("--- SYSTEM ---"); print(system)
        print("--- USER (order 1) ---"); print(u1)
        print("--- end of first payload ---")
    print("\nDRY-RUN OK: %d payloads assembled for %d matches (body model field %s on every one), 0 posted"
          % (len(bodies), len(built), sorted({b["model"] for b in bodies})))


def judge(pilot, workers):
    pool, meta, outputs, X, checker_src, rows, R = plan(pilot)
    configure_rr(); rr.load_env()
    assert_body_copy(post_body("s", "u"))                # the posted body is the one the dry-run printed
    cache = open_cache(); stamp(cache, checker_src)
    if not cache.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        full, _ = build_schedule(pool, X, outputs, meta, R)
        cache.executemany("INSERT INTO schedule VALUES (?,?,?,?,?,?,?)", full); cache.commit()
    sched = cache.execute("SELECT match_id, source, qid, model_a, model_b, filter_verdict, domain FROM schedule ORDER BY match_id").fetchall()
    if pilot: sched = sched[:pilot]
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [s for s in sched if s[0] not in done]
    print("STAGE3-MATH [%s, max_tokens %d]: schedule %d | cached %d | jobs %d (%d calls) | workers %d | cache %s"
          % (JUDGE, MAXTOK, len(sched), len(sched) - len(todo), len(todo), 2 * len(todo), workers, cache_path()), flush=True)
    lock = threading.Lock(); ok = err = 0

    def one(m):
        system, u1, u2 = payloads(m, meta, outputs)
        c1, _, k1, _, f1, _ = judge_full(system, u1)
        c2, _, k2, _, f2, _ = judge_full(system, u2)
        raw1, raw2 = rr.strip_think(c1 or ""), rr.strip_think(c2 or "")
        v1, cf1 = rj.parse_judge(raw1); v2, cf2 = rj.parse_judge(raw2)
        if f1 == "length": v1 = "INVALID"       # NON_TERMINATED: never a verdict, never a tie (FRAMEWORK L73)
        if f2 == "length": v2 = "INVALID"
        w, flip, inv = rj.combine_orders(v1, v2)
        mid, source, qid, a, b = m[:5]
        return (mid, source, qid, a, b, v1, v2, cf1, cf2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time(), f1, f2, k1, k2)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:110]), flush=True); continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 19), row); cache.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    print("done: ok %d, errors %d | cache %s" % (ok, err, cache_path()), flush=True)


def mcnemar_pair(K, qs, a, b):
    """Exact two-sided McNemar on the two models' checker correctness over the judged questions (integer
    arithmetic, as systematic_budget.mcnemar_edge). Returns (p, b, c)."""
    b_ = c_ = 0
    for q in qs:
        ka, kb = K.get((q, a)), K.get((q, b))
        if ka is None or kb is None or ka == kb: continue
        if ka > kb: b_ += 1
        else: c_ += 1
    n = b_ + c_
    if n == 0: return 1.0, 0, 0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(b_, c_) + 1)) / (2 ** n)), b_, c_


def cp_upper(k, n, conf=0.95):
    """One-sided Clopper-Pearson upper bound for k of n (exact; the normal bound is printed beside it)."""
    if n == 0: return float("nan")
    if k >= n: return 1.0
    lo, hi = k / n, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        tail = sum(math.comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(0, k + 1))
        if tail > 1 - conf: lo = mid
        else: hi = mid
    return hi


def open_cache_ro():
    """--analyze never creates or writes the cache: read-only URI; None when the file is absent."""
    p = cache_path()
    if not os.path.exists(p): return None
    return sqlite3.connect("file:%s?mode=ro" % p, uri=True)


def analyze(B, pilot):
    pool, meta, outputs = source_rows()
    X, checker_src, _, _ = checker_answers(pool)
    K = {(q, m): k for (q, m), (_, k) in X.items()}
    cache = open_cache_ro()
    if cache is None:
        print("[CACHE] no cache at %s: nothing judged yet (run --judge first); exit 2" % cache_path()); raise SystemExit(2)
    mt = dict(cache.execute("SELECT key, value FROM meta"))
    sched = [r[0] for r in cache.execute("SELECT match_id FROM schedule ORDER BY match_id")]
    if pilot: sched = sched[:pilot]
    want = set(sched)
    V = [r for r in cache.execute("SELECT match_id, qid, model_a, model_b, winner, flip, invalid, finish1, finish2 FROM verdicts") if r[0] in want]
    short = len(sched) - len(V)                          # matches scheduled but not cached (errored calls are never cached)
    partial = short > 0
    stale = mt.get("script_sha256") != script_sha256()
    L = ["=== STAGE3-MATH%s: %d judged of %d scheduled%s | judge %s | max_tokens %s | temperature %s | pool %s | cache %s%s ==="
         % (" PARTIAL" if partial else "", len(V), len(sched), " (pilot)" if pilot else "", mt.get("judge"), mt.get("max_tokens"), mt.get("temperature"), mt.get("pool_id"),
            os.path.basename(cache_path()), " | STALE: script hash differs from the producing run's" if stale else ""),
         "  protocol %s" % mt.get("protocol"), "  checker  %s" % mt.get("checker_source"),
         "  reference: the pool's raw target verbatim under GEN-ARENA's header '[Verified reference answer]' (the checker's normalised form is an internal comparison form, never shown; the v2 template's 'may be wrong' wording is inherited from GEN-ARENA's 0.935 record)",
         "  temperature: %s (Amendment 1 D2: omitted from the payload, as every compared cache was)" % mt.get("temperature"),
         "  board convention: TIE = 1/2, question-clustered bootstrap B=%d, Bradley-Terry (rejudge_grok.mm_fit) on the 8-model roster" % B]
    if partial:
        L.append("  PARTIAL: %d of %d scheduled matches are not in the cache (calls that raised after retries are never cached); "
                 "no REGISTERED line is written; re-run --judge to resume, then --analyze again." % (short, len(sched)))
    if not V:
        L.append("  nothing judged yet; exit 2"); txt = "\n".join(L); print(txt); raise SystemExit(2)
    # DECIDING SUBSET = key-decidable matches (checker says exactly one side is correct). GUARD: unparsed or
    # non-terminated (finish_reason=length forces INVALID at judge time) above 5% -> VERDICT REFUSED, exit 2.
    dec = [r for r in V if K[(r[1], r[2])] is not None and K[(r[1], r[3])] is not None and K[(r[1], r[2])] != K[(r[1], r[3])]]
    unp = [r for r in dec if r[6]]
    rate = len(unp) / max(1, len(dec))
    unp_all = sum(1 for r in V if r[6]); rate_all = unp_all / max(1, len(V))
    fr = defaultdict(int)
    for r in unp: fr["%s/%s" % (r[7] or "(none)", r[8] or "(none)")] += 1
    nlen = sum(1 for r in V if r[7] == "length" or r[8] == "length")
    L.append("  GUARD: deciding subset = %d key-decidable of %d judged (%.0f%%) | unparsed or non-terminated %d (%.1f%%) [bar %.0f%%] | "
             "overall, all judged matches: %d (%.1f%%) | finish_reason pairs among the deciding unparsed %s | finish_reason=length in any order over all judged %d"
             % (len(dec), len(V), 100 * len(dec) / max(1, len(V)), len(unp), 100 * rate, 100 * UNPARSED_BAR, unp_all, 100 * rate_all, dict(fr) or "-", nlen))
    if rate > UNPARSED_BAR:
        L += ["  VERDICT REFUSED: more than 5% of the deciding subset is unparsed or non-terminated; an unparsed match scores as",
              "  wrong, so every readout would be a floor. Re-run with a larger --maxtok (own cache) before reading anything. Exit 2."]
        txt = "\n".join(L); print(txt)
        open(OUTCOME_PILOT if pilot else (OUTCOME_PARTIAL if partial else OUTCOME), "w", encoding="utf-8").write(txt + "\n")
        raise SystemExit(2)
    L.append("  GUARD PASSED (%.1f%% <= %.0f%% on the deciding subset; %.1f%% overall)" % (100 * rate, 100 * UNPARSED_BAR, 100 * rate_all))
    if pilot:
        L.append("  PILOT: truncation guard read on the first %d matches; the registered readouts are withheld until the run completes." % pilot)
        txt = "\n".join(L); print(txt); open(OUTCOME_PILOT, "w", encoding="utf-8").write(txt + "\n"); return
    valid = [r for r in V if not r[6]]; dv = [r for r in dec if not r[6]]
    right = sum(1 for r in dv if r[4] == (r[2] if K[(r[1], r[2])] else r[3]))
    ties = sum(1 for r in dv if r[4] == "TIE")
    acc_a = right / max(1, len(dv)); acc_b = right / max(1, len(dv) - ties)
    acc_a_inv = right / max(1, len(dec))                 # convention A with INVALID (unparsed / non-terminated) counted WRONG
    flip = sum(r[5] for r in valid) / max(1, len(valid))
    L.append("  (1) key-decidable accuracy, convention A (ties wrong):    %.3f (n=%d) -> bar 0.75 %s | prediction >= 0.90 %s"
             % (acc_a, len(dv), "OK" if acc_a >= 0.75 else "FAIL", "held" if acc_a >= 0.90 else "not held"))
    L.append("      key-decidable accuracy, convention B (ties excluded): %.3f (n=%d) -> bar 0.75 %s | prediction >= 0.90 %s"
             % (acc_b, len(dv) - ties, "OK" if acc_b >= 0.75 else "FAIL", "held" if acc_b >= 0.90 else "not held"))
    L.append("      convention A with INVALID counted wrong (truncations-wrong figure): %.3f (n=%d, %d invalid scored wrong) -> bar 0.75 %s"
             % (acc_a_inv, len(dec), len(dec) - len(dv), "OK" if acc_a_inv >= 0.75 else "FAIL"))
    L.append("      decidable tie rate %.3f | flip rate over all valid %.3f | wrong-direction matches %d | invalid excluded from A/B %d"
             % (ties / max(1, len(dv)), flip, len(dv) - right - ties, len(dec) - len(dv)))
    fvs = dict(cache.execute("SELECT match_id, filter_verdict FROM schedule"))
    for fv in ("DISAGREE", "UNDETERMINED"):
        sub = [r for r in dv if fvs.get(r[0]) == fv]
        if sub:
            rr_ = sum(1 for r in sub if r[4] == (r[2] if K[(r[1], r[2])] else r[3])); tt = sum(1 for r in sub if r[4] == "TIE")
            L.append("      by filter verdict %-12s n=%4d | A %.3f | B %.3f (descriptive)" % (fv, len(sub), rr_ / len(sub), rr_ / max(1, len(sub) - tt)))
    # (2) board and rho with a question-clustered bootstrap CI. Key accuracy = checker_correct over ALL 398 pool
    # questions (FRAMEWORK Stage 3: A over the eval-side questions; the judged-question figure is biased under a
    # filtered schedule and is printed beside, descriptive).
    qs = sorted({r[1] for r in valid}); byq = defaultdict(list)
    for r in valid: byq[r[1]].append(r)
    def key_over(qset): return {m: sum(K[(q, m)] for q in qset if K[(q, m)] is not None) / max(1, sum(1 for q in qset if K[(q, m)] is not None)) for m in ROSTER}
    key = key_over(pool); key_j = key_over(qs)
    votes = lambda rs: [(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for _, _, a, b, w, *_ in rs]
    th = jf.board_from(votes(valid), ROSTER)
    rho = rj.spearman([th[m] for m in ROSTER], [key[m] for m in ROSTER])
    rho_j = rj.spearman([th[m] for m in ROSTER], [key_j[m] for m in ROSTER])
    rng = random.Random(SEED); draws = []; rhos = []
    for _ in range(B):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        d = jf.board_from(votes([r for q in pick for r in byq[q]]), ROSTER); draws.append(d)
        rhos.append(rj.spearman([d[m] for m in ROSTER], [key[m] for m in ROSTER]))
    rhos.sort(); lo, hi = rhos[int(0.025 * B)], rhos[min(B - 1, int(0.975 * B))]
    L.append("  (2) 8-model board over %d valid matches / %d questions: rho vs checker accuracy over all %d pool questions = %.3f, question-bootstrap 95%% CI [%.3f, %.3f] (B=%d)"
             % (len(valid), len(qs), len(pool), rho, lo, hi, B))
    L.append("      beside: rho vs checker accuracy over the %d judged questions = %.3f (descriptive; biased under a filtered schedule)" % (len(qs), rho_j))
    for m in sorted(ROSTER, key=lambda m: -th[m]):
        se = (sum((d[m] - th[m]) ** 2 for d in draws) / B) ** 0.5
        L.append("      %-30s theta %+.3f (SE %.3f) | checker accuracy all %d q %.3f | judged %d q %.3f" % (m, th[m], se, len(pool), key[m], len(qs), key_j[m]))
    jb, kb = max(ROSTER, key=lambda m: th[m]), max(ROSTER, key=lambda m: key[m])
    L.append("      judged argmax %s | key argmax %s -> %s (descriptive, not registered)" % (jb, kb, "same" if jb == kb else "differ"))
    # (3) raw wrong-direction rate with UB. Edges = pairs whose key direction is ESTABLISHED (exact McNemar p < 0.05
    # on checker correctness; DENOMINATOR = the judged questions, not the 398-question pool); judged direction =
    # the bootstrap certificate c_raw = P(theta_a > theta_b); nominal expected wrong calls printed beside every wrong count.
    edges = []
    for a, b in PAIRS:
        p, bb, cc = mcnemar_pair(K, qs, a, b)
        if p >= 0.05: continue
        craw = sum(1 for d in draws if d[a] > d[b]) / B
        edges.append((a, b, craw, bb > cc, (th[a] > th[b]) == (bb > cc), p))
    n = len(edges); wrong_sign = sum(1 for e in edges if not e[4])
    L.append("  (3) raw wrong-direction rate: %d of %d pairs have an ESTABLISHED key direction (exact McNemar p < 0.05; denominator = the %d judged questions, not the %d-question pool); all(established) = %d"
             % (n, len(PAIRS), len(qs), len(pool), n))
    r0 = wrong_sign / max(1, n)
    L.append("      point-estimate sign vs key: wrong %d of %d = %.3f | 95%% UB normal %.3f | exact one-sided 95%% UB %.3f"
             % (wrong_sign, n, r0, r0 + 1.96 * math.sqrt(max(r0 * (1 - r0), 1e-9) / max(1, n)), cp_upper(wrong_sign, n)))
    L.append("      %10s %8s %10s %16s %12s %12s %10s" % ("threshold", "called", "declined", "wrong-direction", "UB normal", "UB exact", "nominal"))
    for thr in (0.90, 0.95, 0.975, 0.99):
        called = [e for e in edges if e[2] >= thr or e[2] <= 1 - thr]
        if not called: L.append("      %10.3f %8d %10d %16s" % (thr, 0, n, "-")); continue
        wrong = sum(1 for e in called if (e[2] > 0.5) != e[3]); r_ = wrong / len(called)
        nominal = sum(1 - max(e[2], 1 - e[2]) for e in called)
        L.append("      %10.3f %8d %10d %9d (%.3f) %12.3f %12.3f %10.2f" % (thr, len(called), n - len(called), wrong, r_,
                 r_ + 1.96 * math.sqrt(max(r_ * (1 - r_), 1e-9) / len(called)), cp_upper(wrong, len(called)), nominal))
    L.append("      calibration status: UNDETERMINED by design (28 pairs; nominal expected wrong calls < 3 at every threshold; the power rule)")
    for a, b, craw, kd, ok, p in edges:
        if not ok or not (craw >= 0.975 or craw <= 0.025):
            L.append("      %-28s vs %-28s c_raw %.3f key says %s (McNemar p=%.4f) %s" % (a, b, craw, "A" if kd else "B", p, "" if ok else "<- wrong sign"))
    if partial:
        L.append("  STAGE3-MATH PARTIAL: %d of %d scheduled matches judged; the REGISTERED line is withheld until the cache holds the whole schedule (re-run --judge to resume)"
                 % (len(V), len(sched)))
        out = OUTCOME_PARTIAL
    else:
        L.append("  STAGE3-MATH REGISTERED: accuracy bar 0.75 under both conventions %s | prediction >= 0.90 %s | calibration UNDETERMINED by design"
                 % ("PASS" if (acc_a >= 0.75 and acc_b >= 0.75) else "FAIL", "held" if (acc_a >= 0.90 and acc_b >= 0.90) else "not held"))
        out = OUTCOME
    L.append("  producing script sha256 %s | outcome written %s" % (mt.get("script_sha256"), time.strftime("%Y-%m-%d %H:%M:%S")))
    txt = "\n".join(L); print(txt); open(out, "w", encoding="utf-8").write(txt + "\n"); print("-> " + out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="STAGE3-MATH (FRAMEWORK item 23)")
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first one verbatim, post nothing")
    ap.add_argument("--judge", action="store_true", help="post the calls (resumes from the run's own cache)")
    ap.add_argument("--analyze", action="store_true", help="truncation guard, then the registered readouts")
    ap.add_argument("--pilot", type=int, default=None, help="first N matches of the schedule only (the plan's pilot is 12)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=MAXTOK_DEFAULT, help="completion budget per call (default %d = rejudge_reasoning.MAX_TOKENS); non-default gets its own cache" % MAXTOK_DEFAULT)
    ap.add_argument("--reading", choices=["full", "explicit"], default="full", help="which checker extractions count as answers: full = tier 1-3 (default), explicit = tier 1-2")
    ap.add_argument("--compare", choices=["norm", "canon"], default="norm", help="string the filter compares: x_norm under the Kotlin rule (default) or x_canon")
    ap.add_argument("--filter", choices=["keep", "disagree"], default="keep", help="keep = not AGREE (default, MatchFilter.keep()); disagree = drop UNDETERMINED too")
    ap.add_argument("--bootstrap", type=int, default=2000)
    ap.add_argument("--checker-table", choices=["v1", "v2"], default="v1", help="v1 = checker_answers_v1.db (default, the held registration; <think> proxy); v2 = checker_answers_v2.db (consistent cap proxy); own cache tag")
    ap.add_argument("--terminated-only", action="store_true", help="exclude every question-pair with a NON_TERMINATED response under the consistent proxy (requires --checker-table v2); cache tag _capfree")
    a = ap.parse_args()
    MAXTOK = a.maxtok; READING = a.reading; COMPARE = a.compare; FILTER = a.filter
    CHECKER_VERSION = a.checker_table; TERMINATED_ONLY = a.terminated_only
    CHECKER_DB, CHECKER_TABLE, CHECKER_META, CHECKER_SCRIPT, CHECKER_COLS = CHECKER_TABLES[CHECKER_VERSION]
    if TERMINATED_ONLY and CHECKER_VERSION != "v2":
        ap.error("--terminated-only is defined on the consistent proxy; it requires --checker-table v2 (v1's non_terminated column is the <think> proxy only)")
    if sum(bool(x) for x in (a.dry_run, a.judge, a.analyze)) != 1: ap.error("exactly one of --dry-run, --judge, --analyze")
    guard()
    if a.dry_run: dry_run(a.pilot)
    elif a.judge: judge(a.pilot, a.workers)
    else: analyze(a.bootstrap, a.pilot)
