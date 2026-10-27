"""MODEL-VINTAGE-CANARY -- when may a row still be called by a contestant's name? (docs/judge_v2_program.md, registered
2026-09-18 "MODEL-VINTAGE-CANARY", ~L5984-6084; plan A9; bill docs/agents/plans/2026-09-19_queue_bills.md item 7).
Zero judge calls in every mode, now and in any pass. Contestant generation is the author's cost and is NOT launched here.

  python tools/analysis/model_vintage_canary.py --selftest             (synthetic rows; touches no DB but the pool guard's)
  python tools/analysis/model_vintage_canary.py --dry-run              (pool id, roster, set hash, row counts, what would be computed; writes nothing)
  python tools/analysis/model_vintage_canary.py --precheck --run       (instrument step 0: extract-v1 on the cached rows; C1; write-once)
  python tools/analysis/model_vintage_canary.py --stamp-harness --dry-run  (step 0b, amendment (a): the assignment table, the three variant regex sets, the
                                                                        3 x 12 canary and full-table tables, what would be written; writes NOTHING)
  python tools/analysis/model_vintage_canary.py --stamp-harness --run  (step 0b: writes the write-once sidecar model_vintage_v0_harness.json + .txt)
  python tools/analysis/model_vintage_canary.py --ingest ...           (steps 1-2, the author's generation pass: REFUSES until the sidecar validates, then
                                                                        REFUSES as not implemented under this registration)
  python tools/analysis/model_vintage_canary.py --analyze              (step 3: REFUSES until an ingest exists)

STEP 0b: THE HARNESS STAMP (amendment (a), docs/judge_v2_program.md L9687-L9799, commit bec7402; plan Amendment 7). The precheck
(step 0) showed the cached pred column is the union of at least three submitter harnesses, so C1 (12 of 12 under ONE extractor)
is FAILED of record and stays so. The author chose (a): stamp vintage v0 with a per-model harness_id and score C1 and F_cache
PER HARNESS, extract-v1 fixed. The three harness families are DEFINED by their disagreement signature in
model_vintage_extractor_check.txt and their membership is FIXED IN THIS FILE BEFORE THE RUN (FAMILY_ASSIGNMENT below, verbatim
from the amendment's (1)): H-tier1-blank (variant tier1-blank: tier 1, else blank), H-constantG (variant three-tier-G: the
three tiers, else the constant "G"), H-threetier (variant three-tier = extract-v1 itself). The run scores every model under
ITS ASSIGNED family's variant and may FAIL it: a model under 0.99 under its assigned variant is stamped harness_id =
UNASSIGNED, refused = true, EXCLUDED from the null and the alarm, and NEVER re-assigned to a better-fitting variant (the
falsifier, (4)); three or more exclusions overturn the amendment's premise (printed; the choice returns to the author). The
assignment rule ("the variant in {tier1-blank, three-tier, three-tier-G} that best reproduces the pred column on the canary,
ties to the simplest") is printed BESIDE the fixed assignment as a CHECK (does the best variant agree?), never used to assign;
arx_0314's stated exception (a canary tie between tier1-blank and three-tier, broken by the full-table reading toward
three-tier) is named in ASSIGNMENT_EXCEPTIONS and checked as such; any contradiction is PRINTED and RECORDED in the sidecar
and the membership is NOT changed in this pass. The 3-variant x 12-model canary table is the criterion's; the 3-variant x
12-model full-table reproduction (every eval_results row of the model) is DESCRIPTIVE only.
  (A1) the sidecar exists, validates, carries 12 models with the memberships of (1) exactly: HELD / FAILED.
  (C1-H) every model reproduces its pred column at >= 0.99 under ITS OWN family's variant (12 of 12; strict both-blank =
         agree / one-blank = disagree): HELD / FAILED. C1 as registered stays FAILED of record beside it.
  (A2) the count of REFUSED (UNASSIGNED) models: printed; 0 expected.   (A3) residual rows per model by qid: printed.
Outputs (write-once, O_EXCL, LF; both refused if either exists): experiment_results/x12_crossdomain/model_vintage_v0_harness.json
= {meta: {script LF sha, extract-v1 sha, variant shas, set hash, pool id, date, assignment_rule as text, families}, models:
{model_name: {harness_id, extractor_variant, n, reproduction (agree / n, rate, Wilson 95%), canary_table, fulltable
(descriptive), residual_qids, refused, rule_check}}, criteria} and the companion .txt (the outcome file of this step). The
stamp lives in the sidecar and is joined by model_name at --ingest / --analyze time: eval_results, the two DBs and every
file of record are untouched. --ingest keeps refusing until the sidecar exists and validates (12 models, 0 UNASSIGNED
unless recorded by insertion, RECORDED_EXCLUSIONS below).

WHAT THE PRECHECK COMPUTES (registration, "Definition" and "Instrument (0)"). The extractor is ONE versioned function,
extract-v1, applied to BOTH the cached eval_results.model_output (vintage v0) and any new output (vintage v1). Before any
generation it must reproduce the cached pred column at >= 0.99 per model on the 279 canary questions (the zero-cost
pre-check; if it does not, the extractor, not the model, is the object: the CHECKER-ANSWER-INGEST lesson of three
readings of one table). extract-v1 = the TIGER-Lab MMLU-Pro evaluate_from_* three-tier letter extractor, verbatim regexes:
tier 1 r"answer is \\(?([A-J])\\)?" ; tier 2 r".*[aA]nswer:\\s*([A-J])" ; tier 3 r"\\b[A-J]\\b(?!.*\\b[A-J]\\b)" (the last
standalone letter, DOTALL); blank when none matches. Reproduction per model = share of the model's canary rows on which
extract-v1(model_output) == pred (both blank counts as agreement; a blank on one side only is a disagreement; a letter on
both sides that differs is a disagreement). The disagreement classes, the tier counts and the committed-rows agreement
(letter on both sides) are printed as description so an amendment by insertion can name what it changes.
  (C1) extract-v1 reproduces the cached pred at >= 0.99 per model on the 279 (12 of 12 models); the registrar's blind
       addition: C1 HELD for >= 10 of 12 models. Both are scored HELD / FAILED; the outcome names both.
Denominator: the model's rows on the 279 canary questions (279 per model, 278 for iask_pro), asserted at load.
NON_TERMINATED is UNSTAMPED on vintage v0 (eval_results carries no finish_reason); the >5% per-model refusal (rule 10)
is implemented here (nonterm_guard) for the ingest of v1 rows and exercised by --selftest.

HYGIENE (registration "Hygiene"; CONTEXT.md section 4). pool_guard.assert_pool_of_record(p2dca21ab5f4ef3ae) is the first
statement and the pool id the first printed line (the precheck is a POOL READER: never while a construction or a site
null runs). The canary set is loaded from experiment_results/x12_crossdomain/canary_set.json and hash-verified
(50af669ac6997f9f, 300 matches / 279 questions / 12 roster models), never re-frozen; the 300 match ids are re-read from
the x12 cache (ratings_x12.db match_history, condition MAIN) and must agree on (eval_question_id, model_a, model_b,
node_id). Every DB is opened mode=ro&immutable=1 (mmlu_pro_dataset_cache_v2.db, ratings_x12.db). eval_results rows are
keyed by (question_id, model_name) = the canary qid; the question identity ACROSS the 12 model files and against the
mmlu_pro table is checked by the OPTIONS key (json-normalised, whitespace-stripped option list), NEVER by question_text
(the eval id-space repair). Meta-Llama-3-70B-Instruct excluded (asserted absent from the roster and never loaded). The
precheck outcome experiment_results/x12_crossdomain/model_vintage_extractor_check.txt (the registration's name for
instrument step 0) is WRITE-ONCE: written only by --precheck --run, refused if it exists. --dry-run writes nothing.
No judge call exists in this file; nothing imports rejudge_reasoning. Every output header carries the script's LF sha
(sha256 of the file bytes with CRLF normalised to LF: the blob git stores under core.autocrlf).
"""
import os, re, sys, json, math, time, hashlib, argparse, tempfile, inspect, sqlite3; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):                       # model outputs carry non-cp1252 characters; a redirected Windows stdout must not crash
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import pool_guard

TEST_ID = "MODEL-VINTAGE-CANARY"
POOL = pool_guard.MMLU_PRO_POOL                         # p2dca21ab5f4ef3ae
EXCLUDED = "Meta-Llama-3-70B-Instruct"
X12DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
SET_JSON = os.path.join(X12DIR, "canary_set.json")
SET_HASH_OF_RECORD = "50af669ac6997f9f"                  # CANARY-BASELINE set of record (plan Amendment 1 D1)
N_MATCHES = 300
N_QUESTIONS = 279
ROSTER_SIZE = 12
EVAL_DB = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
X12_DB = os.path.join(X12DIR, "ratings_x12.db")
SNAP_MAIN = "20260727_042523_Headless_Run_Auto_ge_MAIN"  # rejudge_grok.SNAP_MAIN; the canary set's source
PRECHECK_OUT = os.path.join(X12DIR, "model_vintage_extractor_check.txt")   # registration "Instrument (0)"
V1_CACHE = os.path.join(X12DIR, "model_vintage_v1.db")   # new generations only; never eval_results (registration "Hygiene")
PASS1_OUT = os.path.join(X12DIR, "model_vintage_canary_pass1.txt")
FIXED_CHECKPOINTS = ("Llama-2-7b-hf", "Llama-2-13b-hf", "Meta-Llama-3_1-8B", "Meta-Llama-3_1-70B-Instruct",
                     "Qwen1.5-72B-Chat", "Yi-6b-Chat", "c4ai-command-r-v01")   # published weights: the null's checkpoints
EXTRACTOR_VERSION = "extract-v1"
C1_THRESHOLD = 0.99
C1_MODELS_REGISTERED = 12                                # "12 of 12 models"
C1_MODELS_REGISTRAR = 10                                 # the registrar's blind addition: HELD for >= 10 of 12
NONTERM_RATE = 0.05                                      # rule 10: a model above 5% NON_TERMINATED is refused
ALARM_Z = 3.0                                            # "a_m < F - 3 x sqrt(F(1-F)/n_m)"
LETTERS = "ABCDEFGHIJ"

_T1 = re.compile(r"answer is \(?([A-J])\)?")
_T2 = re.compile(r".*[aA]nswer:\s*([A-J])")
_T3 = re.compile(r"\b[A-J]\b(?!.*\b[A-J]\b)", re.DOTALL)

# ── step 0b: the harness stamp (amendment (a), L9687-L9799, bec7402) ────────────
STAMP_JSON = os.path.join(X12DIR, "model_vintage_v0_harness.json")  # the sidecar (write-once); joined by model_name at ingest
STAMP_TXT = os.path.join(X12DIR, "model_vintage_v0_harness.txt")    # the outcome file of step 0b (write-once)
AMENDMENT_REF = "docs/judge_v2_program.md 'Registered 2026-09-22 ... MODEL-VINTAGE-CANARY amendment (a)' (L9687-L9799, bec7402)"
UNASSIGNED = "UNASSIGNED"
CONSTANT_G = "G"
VARIANT_ORDER = ("tier1-blank", "three-tier", "three-tier-G")      # simplest first: the tie-break of the assignment rule
VARIANT_IDS = {"tier1-blank": "tier1-blank-v1", "three-tier": "three-tier-v1", "three-tier-G": "three-tier-G-v1"}
FAMILY_VARIANT = {"H-tier1-blank": "tier1-blank", "H-constantG": "three-tier-G", "H-threetier": "three-tier"}
# THE MEMBERSHIP OF RECORD, FIXED HERE BEFORE THE RUN (amendment (a) (1), verbatim). Defined by the disagreement signature in
# model_vintage_extractor_check.txt, never by name or provider. The run scores each model under this and may FAIL it; nothing
# in this file re-makes it from an outcome (a re-assignment is a new registration section, before any generation).
FAMILY_ASSIGNMENT = {
    "Llama-2-13b-hf": "H-tier1-blank", "Llama-2-7b-hf": "H-tier1-blank", "Qwen1.5-72B-Chat": "H-tier1-blank",
    "Yi-6b-Chat": "H-tier1-blank", "c4ai-command-r-v01": "H-tier1-blank",
    "Meta-Llama-3_1-70B-Instruct": "H-constantG", "Meta-Llama-3_1-8B": "H-constantG",
    "deepseek-chat-v2_5": "H-threetier", "gemini-3.1-pro_5-shots": "H-threetier", "gpt-4o-2024-08-06": "H-threetier",
    "iask_pro": "H-threetier", "arx_0314": "H-threetier",
}
# The ONE stated exception to the canary reading of the rule: arx_0314 ties on the canary between these two variants (the same
# two rows disagree under both) and the tie is broken by the full-table reading (three-tier 0.9933 > tier1-blank) -> H-threetier.
ASSIGNMENT_EXCEPTIONS = {"arx_0314": ("tier1-blank", "three-tier")}
# Models whose UNASSIGNED stamp has been recorded in the programme by insertion (falsifier (4)); empty today. The --ingest gate
# permits an UNASSIGNED harness_id only for a model named here; anything else is a refusal.
RECORDED_EXCLUSIONS = ()
PREMISE_OVERTURN_AT = 3                                  # "three or more exclusions overturn the amendment's premise"
ASSIGNMENT_RULE_TEXT = ("a model is assigned to the variant in {tier1-blank, three-tier, three-tier-G} that best reproduces its pred "
                        "column on the canary, ties to the simplest (tier1-blank < three-tier < three-tier-G); applied to the precheck's "
                        "classes it gives the three memberships, with ONE stated exception: arx_0314 ties at 0.9928 between tier1-blank "
                        "and three-tier on the canary and the tie is broken by the full-table reading (three-tier 0.9933), so H-threetier. "
                        "The rule is printed as a CHECK beside the fixed membership and is never used to assign or re-assign.")


# ── identity ────────────────────────────────────────────────────────────────────

def script_sha_lf():
    """sha256 of this file's bytes with CRLF normalised to LF (the blob git stores under core.autocrlf=true)."""
    b = open(os.path.abspath(__file__), "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest()


def extractor_sha():
    """sha256 of extract-v1's source text (LF) so an outcome pins the function, not just the script."""
    src = inspect.getsource(extract_v1).replace("\r\n", "\n")
    return hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]


def rel(p):
    try: return os.path.relpath(p, ROOT)
    except ValueError: return p


def header(mode):
    return ["=== %s | %s | script sha256(LF) %s | %s %s | %s ===" % (TEST_ID, mode, script_sha_lf(), EXTRACTOR_VERSION, extractor_sha(),
                                                                       time.strftime("%Y-%m-%d %H:%M:%S")),
            "registration: docs/judge_v2_program.md 'Registered 2026-09-18 ... MODEL-VINTAGE-CANARY' (~L5984-6084); judge calls: 0"]


def ro(path):
    """Read-only AND immutable: no lock, no WAL replay, no shm touch (the DBs are of record)."""
    if not os.path.isfile(path):
        raise SystemExit("[DB] not found: %s" % path)
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % path.replace("\\", "/"), uri=True)


# ── the canary set (never re-frozen) ────────────────────────────────────────────

def set_hash(matches):
    """canary_baseline.set_hash verbatim (match_id:qid:model_a:model_b:stratum lines, sha256[:16]); asserted against it lazily."""
    canon = "\n".join("%d:%d:%s:%s:%s" % (m["match_id"], m["qid"], m["model_a"], m["model_b"], m["stratum"]) for m in matches)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def load_canary_set():
    """(matches, qids, roster, meta). Hash-verified against the record; refuses anything else. Never writes."""
    if not os.path.exists(SET_JSON):
        raise SystemExit("[SET] %s is missing; the set of record (hash %s) is committed with plan Amendment 1: restore it from git. "
                         "This script never freezes a set." % (rel(SET_JSON), SET_HASH_OF_RECORD))
    d = json.load(open(SET_JSON, encoding="utf-8"))
    ms = d["matches"]
    if d.get("pool_id") != POOL:
        raise SystemExit("[SET] canary_set.json pool_id %r is not the pool of record %s" % (d.get("pool_id"), POOL))
    h = set_hash(ms)
    if h != d.get("set_hash") or h != SET_HASH_OF_RECORD:
        raise SystemExit("[SET] canary_set.json hashes to %s (file says %s); the hash of record is %s" % (h, d.get("set_hash"), SET_HASH_OF_RECORD))
    try:
        import canary_baseline as cb                       # the hash function of record; a drift there is caught here
        if cb.set_hash(ms) != h or cb.SET_HASH_OF_RECORD != SET_HASH_OF_RECORD:
            raise SystemExit("[SET] local set_hash disagrees with canary_baseline.set_hash")
    except ImportError:
        pass
    if len(ms) != N_MATCHES:
        raise SystemExit("[SET] %d matches, not %d" % (len(ms), N_MATCHES))
    qids = sorted({int(m["qid"]) for m in ms})
    roster = sorted({m["model_a"] for m in ms} | {m["model_b"] for m in ms})
    if len(qids) != N_QUESTIONS:
        raise SystemExit("[SET] %d distinct questions, not %d" % (len(qids), N_QUESTIONS))
    if EXCLUDED in roster:
        raise SystemExit("[SET] %s is in the canary roster; excluded by rule 6" % EXCLUDED)
    if len(roster) != ROSTER_SIZE:
        raise SystemExit("[SET] roster has %d models, not %d" % (len(roster), ROSTER_SIZE))
    missing_fixed = [m for m in FIXED_CHECKPOINTS if m not in roster]
    if missing_fixed:
        raise SystemExit("[SET] fixed checkpoints not in the roster: %s" % missing_fixed)
    return ms, qids, roster, d


def verify_x12_matches(matches):
    """The 300 match ids re-read from the x12 cache (mode=ro&immutable=1) must carry the set's (qid, model_a, model_b, node_id)
    under condition MAIN and the MAIN snapshot. Returns the count verified."""
    con = ro(X12_DB)
    ids = [int(m["match_id"]) for m in matches]
    rows = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        for r in con.execute("SELECT id, eval_question_id, model_a, model_b, node_id, condition, snapshot_id FROM match_history WHERE id IN (%s)"
                             % ",".join("?" * len(chunk)), chunk):
            rows[int(r[0])] = r
    con.close()
    bad = []
    for m in matches:
        r = rows.get(int(m["match_id"]))
        if r is None or (int(r[1]), r[2], r[3], r[4], r[5], r[6]) != (int(m["qid"]), m["model_a"], m["model_b"], m["node_id"], "MAIN", SNAP_MAIN):
            bad.append(m["match_id"])
    if bad:
        raise SystemExit("[X12] %d of %d canary matches do not reproduce in %s match_history (first: %s)" % (len(bad), len(matches), rel(X12_DB), bad[:5]))
    return len(rows)


# ── the OPTIONS key (never question_text) ───────────────────────────────────────

def okey(o):
    """OPTIONS key: the JSON option list with each option whitespace-stripped (boundary_disagreement.okey); the join key of record."""
    try:
        v = json.loads(o)
        if isinstance(v, list):
            return json.dumps([str(x).strip() for x in v])
    except Exception:
        pass
    return (o or "").strip()


# ── extract-v1 ──────────────────────────────────────────────────────────────────

def extract_v1(text):
    """extract-v1: the TIGER-Lab MMLU-Pro three-tier letter extractor. Returns (letter or "", tier in t1|t2|t3|none).
    Applied unchanged to the cached model_output (v0) and to any new generation (v1). Version-pinned by extractor_sha()."""
    t = text or ""
    m = _T1.search(t)
    if m: return m.group(1), "t1"
    m = _T2.search(t)
    if m: return m.group(1), "t2"
    m = _T3.search(t)
    if m: return m.group(0), "t3"
    return "", "none"


def norm_pred(p):
    """The cached pred as a letter: stripped, upper-cased, first character if it is A-J, else blank."""
    p = (p or "").strip().upper()
    return p[0] if p and p[0] in LETTERS else ""


# ── the three harness variants (step 0b; amendment (a) (1)-(2)) ─────────────────

def extract_tier1_blank(text):
    """tier1-blank-v1 (H-tier1-blank's harness behaviour): tier 1 only, else blank. Returns (letter or "", t1|none)."""
    m = _T1.search(text or "")
    if m: return m.group(1), "t1"
    return "", "none"


def extract_three_tier_G(text):
    """three-tier-G-v1 (H-constantG's harness behaviour): extract-v1's three tiers, else the constant "G" (tier 'default')."""
    e, tier = extract_v1(text)
    if e: return e, tier
    return CONSTANT_G, "default"


VARIANT_FN = {"tier1-blank": extract_tier1_blank, "three-tier": extract_v1, "three-tier-G": extract_three_tier_G}
VARIANT_DESC = {"tier1-blank": "tier 1 %r, else blank" % _T1.pattern,
                "three-tier": "= extract-v1: t1 %r ; t2 %r ; t3 %r (DOTALL); else blank" % (_T1.pattern, _T2.pattern, _T3.pattern),
                "three-tier-G": "extract-v1's three tiers, else the constant %r" % CONSTANT_G}


def variant_sha(variant):
    """sha256[:16] of the variant function's source (LF); three-tier's equals extractor_sha() by construction."""
    src = inspect.getsource(VARIANT_FN[variant]).replace("\r\n", "\n")
    return hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]


def residual_rows(qrows, extractor):
    """qrows: iterable of (qid, pred, model_output). The rows that disagree under `extractor` (the strict rule of reproduction_stats),
    as [(qid, pred_letter, extract_letter, tier)] sorted by qid: the sidecar's residual_qids."""
    out = []
    for q, pred, mo in qrows:
        p = norm_pred(pred); e, tier = extractor(mo)
        if p != e:
            out.append((int(q), p, e, tier))
    return sorted(out)


def best_variant(rates):
    """The assignment rule on one {variant: rate} row: the best-reproducing variant, ties to the simplest (VARIANT_ORDER).
    Returns (best, tied) with tied = every variant at the best rate, in simplicity order. A CHECK, never an assignment."""
    top = max(rates[v] for v in VARIANT_ORDER)
    tied = [v for v in VARIANT_ORDER if abs(rates[v] - top) < 1e-12]
    return tied[0], tied


def rule_check(model, family, canary_rates, fulltable_rates):
    """The assignment rule printed BESIDE the fixed membership, never used to re-assign. Verdicts:
    AGREES: the canary's best variant (ties to the simplest) is the assigned one;
    AGREES-BY-EXCEPTION: the model's stated exception holds (the canary's tied best includes the named pair and the assigned variant,
        the full table's rule-best is the assigned variant, and it beats the pair's other member there strictly); the tied set is
        printed, so a wider tie than the registration's wording (three-tier-G joining) is visible;
    CONTRADICTION-TIE: the assigned variant is among the canary's tied best but the rule's tie-break (simplest) picks another: the
        canary does not distinguish the variants and the clause does (printed and recorded; membership NOT changed);
    CONTRADICTION: the assigned variant is strictly beaten on the canary (printed and recorded; membership NOT changed).
    The full-table reading is checked separately (descriptive): FULLTABLE-AGREES iff the assigned variant is among the full-table
    best, else FULLTABLE-CONTRADICTION (printed and recorded, membership unchanged)."""
    assigned = FAMILY_VARIANT[family]
    c_best, c_tied = best_variant(canary_rates)
    f_best, f_tied = best_variant(fulltable_rates)
    exc = ASSIGNMENT_EXCEPTIONS.get(model)
    if c_best == assigned:
        verdict = "AGREES"; note = "canary best = assigned"
    elif (exc and assigned in exc and set(exc) <= set(c_tied) and f_best == assigned
          and all(fulltable_rates[assigned] > fulltable_rates[v] for v in exc if v != assigned)):
        verdict = "AGREES-BY-EXCEPTION"
        note = "the stated exception: canary tie %s at %.4f, broken by the full table toward %s (%s)" % (
            "/".join(c_tied), canary_rates[assigned], assigned, " vs ".join("%s %.4f" % (v, fulltable_rates[v]) for v in VARIANT_ORDER))
    elif assigned in c_tied:
        verdict = "CONTRADICTION-TIE"
        note = "canary tie %s at %.4f does not distinguish; the tie-break (simplest) picks %s != assigned %s; membership NOT changed" % (
            "/".join(c_tied), canary_rates[assigned], c_best, assigned)
    else:
        verdict = "CONTRADICTION"
        note = "canary best %s (%.4f) beats assigned %s (%.4f); membership NOT changed" % (c_best, canary_rates[c_best], assigned, canary_rates[assigned])
    ft = "FULLTABLE-AGREES" if assigned in f_tied else "FULLTABLE-CONTRADICTION"
    return dict(assigned_variant=assigned, canary_best=c_best, canary_tied=c_tied, fulltable_best=f_best, fulltable_tied=f_tied,
                verdict=verdict, note=note, fulltable_verdict=ft)


# ── the cached rows (vintage v0) ─────────────────────────────────────────────────

def load_cached_rows(qids, roster):
    """{(qid, model): dict(pred, output, gt, okey, category, correct)} for the roster on the canary questions; EXCLUDED never loaded."""
    con = ro(EVAL_DB)
    out = {}
    for i in range(0, len(qids), 500):
        chunk = qids[i:i + 500]
        for q, m, pred, mo, gt, opts, cat, c in con.execute(
                "SELECT question_id, model_name, pred, model_output, gt_answer, options_json, category, is_correct "
                "FROM eval_results WHERE model_name != ? AND question_id IN (%s)" % ",".join("?" * len(chunk)), [EXCLUDED] + chunk):
            if m in roster:
                out[(int(q), m)] = dict(pred=pred, output=mo or "", gt=norm_pred(gt), okey=okey(opts), category=cat, correct=int(c or 0))
    con.close()
    return out


def row_counts(rows, qids, roster):
    return {m: sum(1 for q in qids if (q, m) in rows) for m in roster}


def options_key_audit(rows, qids, roster):
    """Question identity across the 12 model files and against mmlu_pro, by the OPTIONS key (never question_text):
    per qid one key across the files that carry it, one gt letter, and the key's mmlu_pro row count (unique / ambiguous / none)."""
    keys = defaultdict(set); gts = defaultdict(set)
    for (q, m), r in rows.items():
        keys[q].add(r["okey"]); gts[q].add(r["gt"])
    multi_key = sorted(q for q in qids if len(keys[q]) > 1)
    multi_gt = sorted(q for q in qids if len(gts[q]) > 1)
    no_row = sorted(q for q in qids if not keys[q])
    con = ro(EVAL_DB)
    mp = defaultdict(set)
    for i, o in con.execute("SELECT id, options FROM mmlu_pro"):
        mp[okey(o)].add(i)
    con.close()
    uniq = amb = none = 0
    for q in qids:
        if not keys[q]: continue
        n = len(mp.get(next(iter(keys[q])), ()))
        if n == 1: uniq += 1
        elif n > 1: amb += 1
        else: none += 1
    return dict(multi_key=multi_key, multi_gt=multi_gt, no_row=no_row, mmlu_unique=uniq, mmlu_ambiguous=amb, mmlu_none=none)


# ── statistics ──────────────────────────────────────────────────────────────────

def wilson(k, n, z=1.96):
    if n <= 0: return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def reproduction_stats(pairs, extractor=extract_v1):
    """pairs: iterable of (pred, model_output). The C1 metric: strict agreement extractor(output) == norm_pred(pred), both-blank
    counted as agreement (extractor = extract_v1 for C1; a family's variant for C1-H). Returns n, agree, rate, interval,
    disagreement classes, tier counts, committed-rows agreement, lengths."""
    n = agree = 0; cls = Counter(); tiers = Counter(); both = both_agree = 0; chars = 0; pred_blank = ext_blank = 0
    for pred, out in pairs:
        n += 1; chars += len(out or "")
        p = norm_pred(pred); e, tier = extractor(out); tiers[tier] += 1
        if not p: pred_blank += 1
        if not e: ext_blank += 1
        if p and e:
            both += 1
            if p == e: both_agree += 1
        if p == e:
            agree += 1
        elif not p:
            cls["pred blank / extract %s=%s" % (tier, e)] += 1
        elif not e:
            cls["pred %s / extract blank" % p] += 1
        else:
            cls["pred %s / extract %s (%s)" % (p, e, tier)] += 1
    rate = agree / n if n else float("nan")
    return dict(n=n, agree=agree, rate=rate, interval=wilson(agree, n), classes=dict(cls), tiers=dict(tiers),
                committed=both, committed_agree=both_agree, pred_blank=pred_blank, extract_blank=ext_blank,
                mean_chars=(chars / n if n else float("nan")))


def score_c1(rates, threshold=C1_THRESHOLD):
    """rates: {model: reproduction rate}. C1 as registered (all models >= threshold) and the registrar's addition (>= 10 of 12)."""
    passed = sorted(m for m, r in rates.items() if r >= threshold)
    failed = sorted(m for m, r in rates.items() if not (r >= threshold))
    return dict(n_models=len(rates), n_pass=len(passed), passed=passed, failed=failed,
                held_registered=(len(rates) == C1_MODELS_REGISTERED and len(failed) == 0),
                held_registrar=(len(rates) == C1_MODELS_REGISTERED and len(passed) >= C1_MODELS_REGISTRAR))


def nonterm_guard(model, n_total, n_nonterm, rate=NONTERM_RATE):
    """Rule 10 per model: NON_TERMINATED rows stay in the printed denominator, leave a_m's numerator and denominator, and refuse the
    model above `rate`. Returns (ok, message)."""
    if n_total <= 0:
        return False, "%s: no rows" % model
    share = n_nonterm / n_total
    ok = share <= rate
    return ok, "%s: NON_TERMINATED %d of %d (%.3f) %s %.2f -> %s" % (model, n_nonterm, n_total, share, "<=" if ok else ">", rate,
                                                                    "read" if ok else "REFUSED")


def agreement_a_m(triples):
    """a_m: triples of (extract_v0, extract_v1, non_terminated). NON_TERMINATED rows are neither agreement nor disagreement
    (excluded from numerator and denominator; counted for the guard). Returns dict(n_total, n_nonterm, n, agree, a, interval)."""
    n_total = n_nonterm = n = agree = 0
    for e0, e1, nt in triples:
        n_total += 1
        if nt: n_nonterm += 1; continue
        n += 1
        if e0 == e1: agree += 1
    return dict(n_total=n_total, n_nonterm=n_nonterm, n=n, agree=agree, a=(agree / n if n else float("nan")), interval=wilson(agree, n))


def alarm_threshold(F, n, z=ALARM_Z):
    """The registered rule's arithmetic: F - z x sqrt(F(1-F)/n). At F=0.94, n=279 -> 0.897; at F=0.90 -> 0.846."""
    return F - z * math.sqrt(F * (1 - F) / n)


# ── write-once ──────────────────────────────────────────────────────────────────

def write_once(path, text):
    """Creates the file or refuses; never overwrites (O_EXCL). LF line endings."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        raise SystemExit("[WRITE-ONCE] %s exists; the outcome of record is written once and corrected by insertion only. Nothing written." % rel(path))
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


# ── precheck ────────────────────────────────────────────────────────────────────

def precheck_lines(qids, roster, rows, audit, n_x12, meta):
    L = header("precheck (instrument step 0: extract-v1 on the cached rows, vintage v0)")
    L += ["[POOL] %s (pool of record; verified by pool_guard.assert_pool_of_record)" % POOL,
          "canary set: %s hash %s (= record %s) | %d matches | %d distinct questions | roster %d models | x12 match_history rows verified %d (condition MAIN, %s)"
          % (rel(SET_JSON), meta["set_hash"], SET_HASH_OF_RECORD, N_MATCHES, len(qids), len(roster), n_x12, SNAP_MAIN),
          "DBs (mode=ro&immutable=1): %s | %s ; %s asserted absent" % (rel(EVAL_DB), rel(X12_DB), EXCLUDED),
          "OPTIONS-key audit (never question_text): questions with >1 options key across the roster files %d; with >1 gt letter %d; with no row %d; "
          "mmlu_pro rows by the key: unique %d / ambiguous %d / none %d"
          % (len(audit["multi_key"]), len(audit["multi_gt"]), len(audit["no_row"]), audit["mmlu_unique"], audit["mmlu_ambiguous"], audit["mmlu_none"]),
          "extractor: %s (%s) = TIGER-Lab MMLU-Pro three-tier: t1 %r ; t2 %r ; t3 %r (DOTALL); blank when none matches"
          % (EXTRACTOR_VERSION, extractor_sha(), _T1.pattern, _T2.pattern, _T3.pattern),
          "metric: reproduction = share of the model's canary rows with extract-v1(model_output) == pred (both blank = agreement; blank on one side "
          "= disagreement); interval = Wilson 95%; NON_TERMINATED on v0: UNSTAMPED (eval_results carries no finish_reason)",
          "denominator: the model's rows on the %d canary questions (registered 279 per model, 278 for iask_pro)" % len(qids), ""]
    rates = {}; stats = {}
    L.append("%-28s %5s %6s %8s %17s %7s %7s %9s  %s" % ("model", "n", "agree", "repro", "wilson95", "pBlank", "eBlank", "commAgr", "tiers"))
    for m in roster:
        st = reproduction_stats((rows[(q, m)]["pred"], rows[(q, m)]["output"]) for q in qids if (q, m) in rows)
        stats[m] = st; rates[m] = st["rate"]
        lo, hi = st["interval"]
        L.append("%-28s %5d %6d %8.4f [%6.4f, %6.4f] %7d %7d %4d/%-4d  %s" % (m, st["n"], st["agree"], st["rate"], lo, hi, st["pred_blank"],
                                                                                 st["extract_blank"], st["committed_agree"], st["committed"],
                                                                                 " ".join("%s=%d" % kv for kv in sorted(st["tiers"].items()))))
    L.append("")
    L.append("disagreement classes per model (description; what an amendment by insertion would have to name):")
    for m in roster:
        cls = stats[m]["classes"]
        L.append("  %-28s %s" % (m, "; ".join("%s x%d" % kv for kv in sorted(cls.items(), key=lambda kv: -kv[1])) if cls else "none"))
    L.append("")
    L.append("mean chars per cached answer (the registration's cost table): " + "; ".join("%s %.0f" % (m, stats[m]["mean_chars"]) for m in roster))
    L.append("")
    sc = score_c1(rates)
    L.append("(C1) extract-v1 reproduces the cached pred at >= %.2f per model on the 279: %d of %d models at or above the bar" % (C1_THRESHOLD, sc["n_pass"], sc["n_models"]))
    L.append("     models below: %s" % (", ".join("%s %.4f" % (m, rates[m]) for m in sc["failed"]) or "none"))
    L.append("     C1 as registered (12 of 12): %s" % ("HELD" if sc["held_registered"] else "FAILED"))
    L.append("     C1 registrar's blind addition (>= %d of 12): %s" % (C1_MODELS_REGISTRAR, "HELD" if sc["held_registrar"] else "FAILED"))
    L.append("     fixed checkpoints (the null's): %s" % ", ".join("%s %.4f" % (m, rates[m]) for m in FIXED_CHECKPOINTS))
    L.append("     API rows: %s" % ", ".join("%s %.4f" % (m, rates[m]) for m in roster if m not in FIXED_CHECKPOINTS))
    if not sc["held_registrar"]:
        L.append("     consequence (registration): the extractor, not the model, is the object; amend extract-v1 by insertion BEFORE any generation, never after")
    L.append("")
    L.append("does not show: any model drift (no v1 exists); F_gen, F_cache, a_m, the alarm (C2-C4 need the author's generation pass); the frontier order.")
    return L, rates, sc


def cmd_precheck(run):
    ms, qids, roster, meta = load_canary_set()
    if not run:
        raise SystemExit("[PRECHECK] add --run to compute and write %s (write-once), or --dry-run to see what would be computed" % rel(PRECHECK_OUT))
    if os.path.exists(PRECHECK_OUT):
        raise SystemExit("[WRITE-ONCE] %s exists; nothing computed, nothing written." % rel(PRECHECK_OUT))
    n_x12 = verify_x12_matches(ms)
    rows = load_cached_rows(qids, roster)
    counts = row_counts(rows, qids, roster)
    for m in roster:
        expected = N_QUESTIONS - 1 if m == "iask_pro" else N_QUESTIONS
        if counts[m] != expected:
            raise SystemExit("[ROWS] %s has %d cached rows on the canary questions, registered denominator %d" % (m, counts[m], expected))
    audit = options_key_audit(rows, qids, roster)
    if audit["multi_key"] or audit["multi_gt"] or audit["no_row"]:
        raise SystemExit("[OPTIONS-KEY] question identity across the roster files is not unanimous: >1 key %s, >1 gt %s, no row %s"
                         % (audit["multi_key"][:5], audit["multi_gt"][:5], audit["no_row"][:5]))
    L, rates, sc = precheck_lines(qids, roster, rows, audit, n_x12, meta)
    text = "\n".join(L) + "\n"
    write_once(PRECHECK_OUT, text)
    print(text, end="")
    print("[WRITE-ONCE] wrote %s" % rel(PRECHECK_OUT))


def cmd_dry_run():
    ms, qids, roster, meta = load_canary_set()
    n_x12 = verify_x12_matches(ms)
    rows = load_cached_rows(qids, roster)
    counts = row_counts(rows, qids, roster)
    audit = options_key_audit(rows, qids, roster)
    for l in header("dry-run (nothing computed on the rows beyond counts; nothing written; 0 calls)"): print(l)
    print("[POOL] %s (pool of record; verified by pool_guard.assert_pool_of_record)" % POOL)
    print("canary set: %s hash %s (= record %s) | %d matches | %d distinct questions | frozen_at %s | source %s"
          % (rel(SET_JSON), meta["set_hash"], SET_HASH_OF_RECORD, len(ms), len(qids), meta.get("frozen_at"), meta.get("source")))
    print("x12 cache: %s (mode=ro&immutable=1): %d of %d canary match ids reproduce (qid, model_a, model_b, node_id, MAIN, %s)" % (rel(X12_DB), n_x12, len(ms), SNAP_MAIN))
    print("eval cache: %s (mode=ro&immutable=1); %s asserted absent from the roster and never loaded" % (rel(EVAL_DB), EXCLUDED))
    print("roster (%d): fixed checkpoints (the null's 7): %s | API rows (5): %s"
          % (len(roster), ", ".join(m for m in roster if m in FIXED_CHECKPOINTS), ", ".join(m for m in roster if m not in FIXED_CHECKPOINTS)))
    print("per-model cached rows on the %d canary questions (registered denominators: 279, iask_pro 278):" % len(qids))
    for m in roster:
        expected = N_QUESTIONS - 1 if m == "iask_pro" else N_QUESTIONS
        print("  %-28s %3d %s" % (m, counts[m], "OK" if counts[m] == expected else "!= registered %d" % expected))
    print("OPTIONS-key audit (never question_text): >1 key across files %d; >1 gt %d; no row %d; mmlu_pro by key unique %d / ambiguous %d / none %d"
          % (len(audit["multi_key"]), len(audit["multi_gt"]), len(audit["no_row"]), audit["mmlu_unique"], audit["mmlu_ambiguous"], audit["mmlu_none"]))
    print("would compute (--precheck --run): per model, %s(model_output) == pred on every cached row -> reproduction rate with a Wilson 95%% interval, "
          "disagreement classes, tier counts, committed-rows agreement, mean chars; C1 at >= %.2f per model, scored as registered (12 of 12) and "
          "as the registrar's addition (>= %d of 12)" % (EXTRACTOR_VERSION, C1_THRESHOLD, C1_MODELS_REGISTRAR))
    print("would write (write-once): %s -> exists now: %s" % (rel(PRECHECK_OUT), os.path.exists(PRECHECK_OUT)))
    print("would NOT: post any call; generate anything; open %s (the author's pass); touch eval_results" % rel(V1_CACHE))
    print("[DRY-RUN] nothing written; 0 calls")


# ── step 0b: the harness stamp ──────────────────────────────────────────────────

def fulltable_rates(roster):
    """DESCRIPTIVE: per model, the reproduction of the cached pred under each of the three variants over EVERY eval_results row of
    the model (mode=ro&immutable=1; streamed; pred and model_output only; EXCLUDED never read). Returns {model: {rows, agree: {variant: k}}}."""
    con = ro(EVAL_DB)
    acc = {m: dict(rows=0, agree={v: 0 for v in VARIANT_ORDER}) for m in roster}
    for m, pred, mo in con.execute("SELECT model_name, pred, model_output FROM eval_results WHERE model_name != ? AND model_name IN (%s)"
                                   % ",".join("?" * len(roster)), [EXCLUDED] + list(roster)):
        a = acc[m]; a["rows"] += 1
        p = norm_pred(pred)
        for v in VARIANT_ORDER:
            if VARIANT_FN[v](mo)[0] == p:
                a["agree"][v] += 1
    con.close()
    return acc


def stamp_model(model, family, qrows, full):
    """One model's sidecar entry. qrows: [(qid, pred, model_output)] on the canary; full: fulltable_rates()[model]. Scored under the
    ASSIGNED family's variant; a rate < C1_THRESHOLD stamps harness_id = UNASSIGNED and refused = True (never re-assigned)."""
    variant = FAMILY_VARIANT[family]
    stats = {v: reproduction_stats(((p, mo) for _, p, mo in qrows), VARIANT_FN[v]) for v in VARIANT_ORDER}
    st = stats[variant]
    canary_rates = {v: stats[v]["rate"] for v in VARIANT_ORDER}
    ft_rates = {v: (full["agree"][v] / full["rows"] if full["rows"] else float("nan")) for v in VARIANT_ORDER}
    res = residual_rows(qrows, VARIANT_FN[variant])
    ok = st["rate"] >= C1_THRESHOLD
    lo, hi = st["interval"]
    return dict(assigned_family=family, harness_id=(family if ok else UNASSIGNED), extractor_variant=variant, variant_id=VARIANT_IDS[variant],
                variant_sha=variant_sha(variant), n=st["n"],
                reproduction=dict(agree=st["agree"], n=st["n"], rate=st["rate"], wilson95=[lo, hi], threshold=C1_THRESHOLD, at_or_above=ok),
                canary_table={v: canary_rates[v] for v in VARIANT_ORDER}, canary_agree={v: stats[v]["agree"] for v in VARIANT_ORDER},
                fulltable=dict(rows=full["rows"], **{v: ft_rates[v] for v in VARIANT_ORDER}), fulltable_agree=dict(full["agree"]),
                residual_qids=[dict(qid=q, pred=p, extract=e, tier=t) for q, p, e, t in res], refused=(not ok),
                rule_check=rule_check(model, family, canary_rates, ft_rates))


def build_sidecar(models, meta_extra=None):
    """The sidecar dict from {model: stamp_model(...)}: meta (script LF sha, extract-v1 sha, variant shas, set hash, pool id, date,
    the assignment rule as text, the fixed families), models, criteria (A1 / C1-H / A2 / A3, contradictions, the premise flag)."""
    refused = sorted(m for m, e in models.items() if e["refused"])
    contradictions = sorted("%s: %s (%s)" % (m, e["rule_check"]["verdict"], e["rule_check"]["note"]) for m, e in models.items()
                            if e["rule_check"]["verdict"].startswith("CONTRADICTION"))
    contradictions += sorted("%s: FULLTABLE-CONTRADICTION (full-table best %s, assigned %s)" % (m, "/".join(e["rule_check"]["fulltable_tied"]),
                                                                                              e["rule_check"]["assigned_variant"])
                             for m, e in models.items() if e["rule_check"]["fulltable_verdict"] != "FULLTABLE-AGREES")
    a1 = (len(models) == ROSTER_SIZE and set(models) == set(FAMILY_ASSIGNMENT)
          and all(e["assigned_family"] == FAMILY_ASSIGNMENT[m] and e["extractor_variant"] == FAMILY_VARIANT[FAMILY_ASSIGNMENT[m]] for m, e in models.items()))
    meta = dict(test_id=TEST_ID, step="0b (amendment (a): per-model harness_id on vintage v0)", registration=AMENDMENT_REF,
                script_sha_lf=script_sha_lf(), extract_v1_sha=extractor_sha(), extractor_version=EXTRACTOR_VERSION,
                variant_shas={VARIANT_IDS[v]: variant_sha(v) for v in VARIANT_ORDER}, variant_order=list(VARIANT_ORDER),
                set_hash=SET_HASH_OF_RECORD, pool_id=POOL, date=time.strftime("%Y-%m-%d %H:%M:%S"), threshold=C1_THRESHOLD,
                assignment_rule=ASSIGNMENT_RULE_TEXT,
                families={f: dict(variant=FAMILY_VARIANT[f], members=sorted(m for m, ff in FAMILY_ASSIGNMENT.items() if ff == f)) for f in FAMILY_VARIANT},
                exceptions={m: list(v) for m, v in ASSIGNMENT_EXCEPTIONS.items()}, recorded_exclusions=list(RECORDED_EXCLUSIONS), judge_calls=0)
    if meta_extra: meta.update(meta_extra)
    return dict(meta=meta, models={m: models[m] for m in sorted(models)},
                criteria=dict(A1=("HELD" if a1 else "FAILED"), C1H=("HELD" if (a1 and not refused) else "FAILED"), A2_refused=refused,
                              A2_count=len(refused), A3_residual_rows={m: len(e["residual_qids"]) for m, e in sorted(models.items())},
                              contradictions=contradictions, premise_overturned=(len(refused) >= PREMISE_OVERTURN_AT)))


def validate_sidecar(d, expected_n=None):
    """Every problem with a sidecar dict (empty list = validates). Membership against FAMILY_ASSIGNMENT (A1), the variant of each family,
    harness_id in {family, UNASSIGNED}, refused == (rate < threshold) == (harness_id == UNASSIGNED), rate == agree / n, residuals == n -
    agree, the denominators (expected_n: {model: n}; default the registered 279 / 278 iask_pro), set hash, pool id, extract-v1 sha."""
    P = []
    meta = d.get("meta") or {}; models = d.get("models") or {}
    if meta.get("pool_id") != POOL: P.append("meta.pool_id %r != %s" % (meta.get("pool_id"), POOL))
    if meta.get("set_hash") != SET_HASH_OF_RECORD: P.append("meta.set_hash %r != %s" % (meta.get("set_hash"), SET_HASH_OF_RECORD))
    if meta.get("extract_v1_sha") != extractor_sha(): P.append("meta.extract_v1_sha %r != %s" % (meta.get("extract_v1_sha"), extractor_sha()))
    for v in VARIANT_ORDER:
        if (meta.get("variant_shas") or {}).get(VARIANT_IDS[v]) != variant_sha(v): P.append("meta.variant_shas[%s] != %s" % (VARIANT_IDS[v], variant_sha(v)))
    if set(models) != set(FAMILY_ASSIGNMENT) or len(models) != ROSTER_SIZE:
        P.append("models %s != the fixed membership of (1) %s" % (sorted(models), sorted(FAMILY_ASSIGNMENT)))
    if EXCLUDED in models: P.append("%s present" % EXCLUDED)
    if expected_n is None: expected_n = {m: (N_QUESTIONS - 1 if m == "iask_pro" else N_QUESTIONS) for m in FAMILY_ASSIGNMENT}
    for m, e in models.items():
        fam = FAMILY_ASSIGNMENT.get(m)
        if e.get("assigned_family") != fam: P.append("%s: assigned_family %r != (1)'s %r" % (m, e.get("assigned_family"), fam))
        if fam and e.get("extractor_variant") != FAMILY_VARIANT[fam]: P.append("%s: extractor_variant %r != %s" % (m, e.get("extractor_variant"), FAMILY_VARIANT[fam]))
        if e.get("harness_id") not in (fam, UNASSIGNED): P.append("%s: harness_id %r not in {%s, %s}" % (m, e.get("harness_id"), fam, UNASSIGNED))
        r = e.get("reproduction") or {}
        n, k = r.get("n"), r.get("agree")
        if not isinstance(n, int) or not isinstance(k, int) or n <= 0 or not (0 <= k <= n): P.append("%s: reproduction agree/n %r/%r" % (m, k, n)); continue
        if e.get("n") != n or (m in expected_n and n != expected_n[m]): P.append("%s: n %r (expected %r)" % (m, n, expected_n.get(m)))
        if abs(r.get("rate", -1) - k / n) > 1e-12: P.append("%s: rate %r != %d/%d" % (m, r.get("rate"), k, n))
        below = (k / n) < C1_THRESHOLD
        if bool(e.get("refused")) != below: P.append("%s: refused %r but rate %.4f vs %.2f" % (m, e.get("refused"), k / n, C1_THRESHOLD))
        if (e.get("harness_id") == UNASSIGNED) != below: P.append("%s: harness_id %r inconsistent with rate %.4f" % (m, e.get("harness_id"), k / n))
        if len(e.get("residual_qids") or []) != n - k: P.append("%s: %d residual rows != n - agree %d" % (m, len(e.get("residual_qids") or []), n - k))
        if set(e.get("canary_table") or {}) != set(VARIANT_ORDER): P.append("%s: canary_table lacks a variant" % m)
    return P


def sidecar_gate(path=STAMP_JSON):
    """The --ingest gate: the sidecar must exist and validate; an UNASSIGNED model is refused unless named in RECORDED_EXCLUSIONS.
    Returns {model: harness_id} or raises SystemExit."""
    if not os.path.exists(path):
        raise SystemExit("[INGEST] refused: the harness sidecar %s does not exist; run --stamp-harness --run first (amendment (a))." % rel(path))
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as ex:
        raise SystemExit("[INGEST] refused: %s is not readable JSON (%s)" % (rel(path), ex))
    P = validate_sidecar(d)
    if P:
        raise SystemExit("[INGEST] refused: the harness sidecar %s does not validate (%d problems): %s" % (rel(path), len(P), "; ".join(P[:6])))
    un = sorted(m for m, e in d["models"].items() if e["harness_id"] == UNASSIGNED and m not in RECORDED_EXCLUSIONS)
    if un:
        raise SystemExit("[INGEST] refused: %d model(s) stamped %s and not recorded by insertion (RECORDED_EXCLUSIONS): %s" % (len(un), UNASSIGNED, ", ".join(un)))
    return {m: e["harness_id"] for m, e in d["models"].items()}


def stamp_header():
    return ["=== %s | stamp-harness (instrument step 0b: per-model harness_id on vintage v0; amendment (a)) | script sha256(LF) %s | %s %s | %s ==="
            % (TEST_ID, script_sha_lf(), EXTRACTOR_VERSION, extractor_sha(), time.strftime("%Y-%m-%d %H:%M:%S")),
            "registration: %s over 'Registered 2026-09-18 ... MODEL-VINTAGE-CANARY' (~L5984-6084); judge calls: 0; generation: none" % AMENDMENT_REF]


def assignment_lines():
    L = ["variants (versioned functions; source sha beside %s %s):" % (EXTRACTOR_VERSION, extractor_sha())]
    for v in VARIANT_ORDER:
        fam = next(f for f, vv in FAMILY_VARIANT.items() if vv == v)
        L.append("  %-13s %-16s %s  %s  [%s]" % (v, VARIANT_IDS[v], variant_sha(v), VARIANT_DESC[v], fam))
    L.append("assignment (FIXED IN CODE before the run, amendment (a) (1); defined by the disagreement signature in %s; never re-made from this output):"
             % rel(PRECHECK_OUT))
    for f in FAMILY_VARIANT:
        mem = sorted(m for m, ff in FAMILY_ASSIGNMENT.items() if ff == f)
        L.append("  %-14s variant %-13s %d members: %s" % (f, FAMILY_VARIANT[f], len(mem), ", ".join(mem)))
    L.append("  stated exception: " + "; ".join("%s ties on the canary between %s; the full table breaks it toward %s -> %s"
                                                % (m, "/".join(pair), FAMILY_VARIANT[FAMILY_ASSIGNMENT[m]], FAMILY_ASSIGNMENT[m]) for m, pair in ASSIGNMENT_EXCEPTIONS.items()))
    L.append("assignment rule (a CHECK printed beside the fixed membership; never used to assign): " + ASSIGNMENT_RULE_TEXT)
    L.append("falsifier (4): a model < %.2f under its ASSIGNED variant is stamped harness_id = %s, refused, excluded from the null and the alarm, NEVER "
             "re-assigned; >= %d exclusions overturn the premise (the choice returns to the author)" % (C1_THRESHOLD, UNASSIGNED, PREMISE_OVERTURN_AT))
    return L


def stamp_lines(sidecar, qids, n_x12, meta_set):
    """The outcome text of step 0b (the .txt companion): the same numbers as the sidecar."""
    M = sidecar["models"]; C = sidecar["criteria"]; roster = sorted(M)
    L = stamp_header()
    L += ["[POOL] %s (pool of record; verified by pool_guard.assert_pool_of_record)" % POOL,
          "canary set: %s hash %s (= record %s) | %d matches | %d distinct questions | roster %d models | x12 match_history rows verified %d (condition MAIN, %s)"
          % (rel(SET_JSON), meta_set["set_hash"], SET_HASH_OF_RECORD, N_MATCHES, len(qids), len(roster), n_x12, SNAP_MAIN),
          "DBs (mode=ro&immutable=1): %s | %s ; %s asserted absent; nothing of record modified (the stamp lives in %s)"
          % (rel(EVAL_DB), rel(X12_DB), EXCLUDED, rel(STAMP_JSON))]
    L += assignment_lines()
    L += ["metric: reproduction = share of the model's canary rows with variant(model_output) == pred (both blank = agreement; blank on one side = "
          "disagreement); interval = Wilson 95%; C1-H reads each model under ITS ASSIGNED family's variant",
          "denominator: the model's rows on the %d canary questions (registered 279 per model, 278 for iask_pro); the full-table column is every "
          "eval_results row of the model (DESCRIPTIVE, not a criterion)" % len(qids), ""]
    L.append("canary table (3 variants x %d models; the criterion's; * = the assigned variant):" % len(roster))
    L.append("%-28s %-14s %12s %12s %12s  %-13s %s" % ("model", "family", VARIANT_ORDER[0], VARIANT_ORDER[1], VARIANT_ORDER[2], "rule best", "check"))
    for m in roster:
        e = M[m]; rc = e["rule_check"]
        cells = ["%s%.4f" % ("*" if v == e["extractor_variant"] else " ", e["canary_table"][v]) for v in VARIANT_ORDER]
        L.append("%-28s %-14s %12s %12s %12s  %-13s %s%s" % (m, e["assigned_family"], cells[0], cells[1], cells[2], rc["canary_best"], rc["verdict"],
                                                              "" if rc["verdict"] == "AGREES" else " (%s)" % rc["note"]))
    L.append("")
    L.append("full-table column (DESCRIPTIVE; 3 variants x %d models over every eval_results row of the model; * = the assigned variant):" % len(roster))
    L.append("%-28s %6s %12s %12s %12s  %-13s %s" % ("model", "rows", VARIANT_ORDER[0], VARIANT_ORDER[1], VARIANT_ORDER[2], "rule best", "check"))
    for m in roster:
        e = M[m]; rc = e["rule_check"]
        cells = ["%s%.4f" % ("*" if v == e["extractor_variant"] else " ", e["fulltable"][v]) for v in VARIANT_ORDER]
        L.append("%-28s %6d %12s %12s %12s  %-13s %s" % (m, e["fulltable"]["rows"], cells[0], cells[1], cells[2], rc["fulltable_best"], rc["fulltable_verdict"]))
    L.append("")
    L.append("the stamp (per model, under the ASSIGNED variant; the sidecar's row):")
    L.append("%-28s %-14s %-13s %5s %6s %8s %17s %8s %s" % ("model", "harness_id", "variant", "n", "agree", "repro", "wilson95", "residual", "refused"))
    for m in roster:
        e = M[m]; r = e["reproduction"]
        L.append("%-28s %-14s %-13s %5d %6d %8.4f [%6.4f, %6.4f] %8d %s" % (m, e["harness_id"], e["extractor_variant"], r["n"], r["agree"], r["rate"],
                                                                             r["wilson95"][0], r["wilson95"][1], len(e["residual_qids"]), e["refused"]))
    L.append("")
    L.append("residual rows per model (A3; the canary rows that still disagree under the assigned variant, by qid with pred and extract):")
    for m in roster:
        rs = M[m]["residual_qids"]
        L.append("  %-28s %s" % (m, "; ".join("q%d pred %s / extract %s (%s)" % (r["qid"], r["pred"] or "blank", r["extract"] or "blank", r["tier"]) for r in rs) if rs else "none"))
    L.append("")
    L.append("(A1) the sidecar carries %d models with the memberships of (1) exactly (assigned_family and variant per model = FAMILY_ASSIGNMENT): %s" % (len(M), C["A1"]))
    L.append("(C1-H) every model reproduces its pred column at >= %.2f under ITS OWN family's variant: %d of %d -> %s (C1 as registered, one extractor: FAILED of record, %s)"
             % (C1_THRESHOLD, len(M) - C["A2_count"], len(M), C["C1H"], rel(PRECHECK_OUT)))
    L.append("     models below under their assigned variant (stamped %s, EXCLUDED from the null and the alarm, never re-assigned): %s"
             % (UNASSIGNED, ", ".join("%s %.4f" % (m, M[m]["reproduction"]["rate"]) for m in C["A2_refused"]) or "none"))
    L.append("(A2) REFUSED (%s) models: %d (0 expected)%s" % (UNASSIGNED, C["A2_count"],
                                                            "; >= %d: the amendment's premise is OVERTURNED, the choice returns to the author" % PREMISE_OVERTURN_AT if C["premise_overturned"] else ""))
    L.append("(A3) residual rows: " + "; ".join("%s %d" % (m, C["A3_residual_rows"][m]) for m in roster))
    L.append("assignment-rule check (beside, never re-assigning): %s" % ("no contradiction" if not C["contradictions"] else
                                                                       "%d CONTRADICTION(S) printed and recorded, membership NOT changed: %s" % (len(C["contradictions"]), " | ".join(C["contradictions"]))))
    L.append("")
    # predictions (amendment (a) "Predictions", scored blind against the sidecar)
    t1b = [m for m in roster if FAMILY_ASSIGNMENT[m] == "H-tier1-blank"]; cg = [m for m in roster if FAMILY_ASSIGNMENT[m] == "H-constantG"]
    api = [m for m in roster if FAMILY_ASSIGNMENT[m] == "H-threetier" and m != "arx_0314"]
    arx = M.get("arx_0314")
    pa1 = (C["C1H"] == "HELD" and all(M[m]["reproduction"]["rate"] == 1.0 for m in t1b + cg + api) and arx is not None
           and (arx["reproduction"]["agree"], arx["reproduction"]["n"]) == (277, 279))
    L.append("P-A1 (C1-H HELD 12 of 12; 11 at 1.0000; arx_0314 at 0.9928 [0.9742, 0.9980]; A2 = 0): %s" % ("HELD" if pa1 else "FAILED"))
    pa2 = (all(C["A3_residual_rows"][m] == 0 for m in t1b + cg + api) and arx is not None and sorted(r["qid"] for r in arx["residual_qids"]) == [4941, 7433])
    L.append("P-A2 (residual rows 0 for eleven models; 2 for arx_0314, q4941 and q7433): %s" % ("HELD" if pa2 else "FAILED"))
    pa3 = (all(M[m]["fulltable"]["tier1-blank"] == 1.0 for m in t1b) and all(M[m]["fulltable"]["three-tier"] == 1.0 for m in api)
           and all(M[m]["fulltable"]["three-tier-G"] >= 0.99 for m in cg) and arx is not None and round(arx["fulltable"]["three-tier"], 4) == 0.9933)
    L.append("P-A3 (descriptive, the full-table column: H-tier1-blank 1.0000 under tier1-blank; the four API models 1.0000 under three-tier; the Llama-3.1 pair "
             ">= 0.99 under three-tier-G; arx_0314 0.9933 under three-tier): %s" % ("HELD" if pa3 else "FAILED"))
    L.append("P-A4 (the generation pass): not scorable here (no v1 exists).")
    L.append("")
    L.append("does not show: any model drift (no v1 exists); F_gen, F_cache, a_m, the alarm (C2-H, C3-H, C4 need the author's generation pass); a fourth extractor "
             "(no regex was added to extract-v1); any change to pred, is_correct or a verdict; the frontier order.")
    return L


def cmd_stamp_harness(run):
    ms, qids, roster, meta_set = load_canary_set()
    if run:
        for p in (STAMP_JSON, STAMP_TXT):
            if os.path.exists(p):
                raise SystemExit("[WRITE-ONCE] %s exists; nothing computed, nothing written (the sidecar is corrected by insertion in the programme, never rewritten)." % rel(p))
    if set(roster) != set(FAMILY_ASSIGNMENT):
        raise SystemExit("[A1] FAILED: the canary roster %s is not the fixed membership of (1) %s; stopped, nothing written" % (sorted(roster), sorted(FAMILY_ASSIGNMENT)))
    n_x12 = verify_x12_matches(ms)
    rows = load_cached_rows(qids, roster)
    counts = row_counts(rows, qids, roster)
    for m in roster:
        expected = N_QUESTIONS - 1 if m == "iask_pro" else N_QUESTIONS
        if counts[m] != expected:
            raise SystemExit("[ROWS] %s has %d cached rows on the canary questions, registered denominator %d" % (m, counts[m], expected))
    audit = options_key_audit(rows, qids, roster)
    if audit["multi_key"] or audit["multi_gt"] or audit["no_row"]:
        raise SystemExit("[OPTIONS-KEY] question identity across the roster files is not unanimous: >1 key %s, >1 gt %s, no row %s"
                         % (audit["multi_key"][:5], audit["multi_gt"][:5], audit["no_row"][:5]))
    t0 = time.time()
    full = fulltable_rates(roster)
    t_full = time.time() - t0
    models = {m: stamp_model(m, FAMILY_ASSIGNMENT[m], [(q, rows[(q, m)]["pred"], rows[(q, m)]["output"]) for q in qids if (q, m) in rows], full[m]) for m in roster}
    sidecar = build_sidecar(models, dict(x12_matches_verified=n_x12, fulltable_seconds=round(t_full, 1), mode=("run" if run else "dry-run")))
    P = validate_sidecar(sidecar)
    if P:
        raise SystemExit("[A1] FAILED: the assembled sidecar does not validate (%d problems): %s; stopped, nothing written" % (len(P), "; ".join(P[:6])))
    L = stamp_lines(sidecar, qids, n_x12, meta_set)
    text = "\n".join(L) + "\n"
    if not run:
        print(text, end="")
        print("would write (write-once, O_EXCL, LF): %s (exists now: %s) and %s (exists now: %s); %d models, %d %s, %d contradiction(s); A1 %s, C1-H %s"
              % (rel(STAMP_JSON), os.path.exists(STAMP_JSON), rel(STAMP_TXT), os.path.exists(STAMP_TXT), len(models), sidecar["criteria"]["A2_count"], UNASSIGNED,
                 len(sidecar["criteria"]["contradictions"]), sidecar["criteria"]["A1"], sidecar["criteria"]["C1H"]))
        print("would NOT: post any call; generate anything; touch eval_results, %s, %s or %s" % (rel(EVAL_DB), rel(X12_DB), rel(PRECHECK_OUT)))
        print("[DRY-RUN] nothing written; 0 calls; full-table pass %.1f s" % t_full)
        return
    write_once(STAMP_JSON, json.dumps(sidecar, indent=1, sort_keys=False) + "\n")
    write_once(STAMP_TXT, text)
    back = json.load(open(STAMP_JSON, encoding="utf-8"))
    P = validate_sidecar(back)
    print(text, end="")
    print("[WRITE-ONCE] wrote %s and %s; re-read sidecar validates: %s" % (rel(STAMP_JSON), rel(STAMP_TXT), "OK" if not P else "NO: %s" % P[:3]))
    if P:
        raise SystemExit(1)


# ── the author's pass (not under this registration) ─────────────────────────────

def cmd_ingest():
    stamps = sidecar_gate()
    print("[INGEST] harness sidecar %s validates: %s" % (rel(STAMP_JSON), ", ".join("%s=%s" % kv for kv in sorted(stamps.items()))))
    raise SystemExit("[INGEST] not implemented under this registration: contestant generation is the author's cost and is not launched "
                     "by MODEL-VINTAGE-CANARY. An ingest must record protocol P per generation (harness prompt bytes, sampling as a literal "
                     "or 'omitted', max_tokens, provider, deployment fingerprint, extractor_version=%s %s), finish_reason (length -> "
                     "NON_TERMINATED), content_filter refusals as unusable rows, into %s only (never eval_results), and must not run before "
                     "%s reports C1 HELD." % (EXTRACTOR_VERSION, extractor_sha(), rel(V1_CACHE), rel(PRECHECK_OUT)))


def cmd_analyze():
    if not os.path.exists(V1_CACHE):
        raise SystemExit("[ANALYZE] %s does not exist: no generation pass has been ingested; C2-C4 cannot be read. Nothing written." % rel(V1_CACHE))
    raise SystemExit("[ANALYZE] not implemented under this registration: the F_gen / F_cache null, the a_m alarm (threshold F - 3 SE, per model, "
                     "never pooled) and the McNemar delta are read only from a COMPLETE %s; %s is write-once." % (rel(V1_CACHE), rel(PASS1_OUT)))


# ── selftest (synthetic rows; no DB but the pool guard's) ───────────────────────

def cmd_selftest():
    for l in header("selftest (synthetic rows; 0 calls; writes only into a temporary directory)"): print(l)
    print("[POOL] %s (pool of record; verified by pool_guard.assert_pool_of_record)" % POOL)
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond))); print("  [%s] %s" % ("ok" if cond else "FAIL", name))

    # 1. extract-v1 tiers
    check("t1: 'the answer is (C)' -> C", extract_v1("blah. The answer is (C).") == ("C", "t1"))
    check("t1 without parentheses: 'answer is D' -> D", extract_v1("So the answer is D") == ("D", "t1"))
    check("t2: 'Answer: B' -> B", extract_v1("Reasoning...\nAnswer: B") == ("B", "t2"))
    check("t3: last standalone letter -> J", extract_v1("options E and J were close; I pick J") == ("J", "t3"))
    check("none: no letter -> blank", extract_v1("the model rambled 42 42 42") == ("", "none"))
    check("empty / None -> blank", extract_v1("") == ("", "none") and extract_v1(None) == ("", "none"))
    check("t1 beats t3: 'answer is (A) ... B' -> A", extract_v1("answer is (A). Not B")[0] == "A")
    check("bold markdown '**(H)**' is t3 not t1", extract_v1("The answer is **(H)**.") == ("H", "t3"))
    check("norm_pred: ' c ' -> C, '' -> blank, 'K' -> blank", norm_pred(" c ") == "C" and norm_pred("") == "" and norm_pred("K") == "")

    # 2. the reproduction metric on synthetic rows
    rows = [("C", "The answer is (C)."), ("", "no letter here 42"), ("D", "Answer: D"), ("", "last letter J"), ("B", "nothing"),
            ("A", "answer is (B)"), ("E", "The answer is (E)."), ("F", "The answer is (F).")]
    st = reproduction_stats(rows)
    check("metric: n=8 agree=5 (both-blank counts; blank-one-side and letter mismatch do not)", st["n"] == 8 and st["agree"] == 5 and abs(st["rate"] - 0.625) < 1e-12)
    check("metric: classes named", st["classes"].get("pred blank / extract t3=J") == 1 and st["classes"].get("pred B / extract blank") == 1
          and st["classes"].get("pred A / extract B (t1)") == 1)
    check("metric: committed rows 5, committed agree 4", st["committed"] == 5 and st["committed_agree"] == 4)
    check("metric: tiers t1=4 t2=1 t3=1 none=2", st["tiers"] == {"t1": 4, "t2": 1, "t3": 1, "none": 2})
    lo, hi = wilson(4, 8); check("wilson(4, 8) = [0.215, 0.785]", abs(lo - 0.2152) < 1e-3 and abs(hi - 0.7848) < 1e-3)
    check("wilson(279, 279) upper = 1.0, lower > 0.98", wilson(279, 279)[1] == 1.0 and wilson(279, 279)[0] > 0.98)

    # 3. the >= 10 of 12 rule and the registered 12 of 12
    names = ["m%02d" % i for i in range(12)]
    all_pass = {m: 0.995 for m in names}
    sc = score_c1(all_pass); check("12 of 12 at 0.995: registered HELD, registrar HELD", sc["held_registered"] and sc["held_registrar"] and sc["n_pass"] == 12)
    two_fail = dict(all_pass); two_fail["m00"] = 0.98; two_fail["m01"] = 0.9899
    sc = score_c1(two_fail); check("10 of 12: registered FAILED, registrar HELD, failed names listed", (not sc["held_registered"]) and sc["held_registrar"] and sc["failed"] == ["m00", "m01"])
    three_fail = dict(two_fail); three_fail["m02"] = 0.5
    sc = score_c1(three_fail); check("9 of 12: both FAILED", (not sc["held_registered"]) and (not sc["held_registrar"]) and sc["n_pass"] == 9)
    exact = dict(all_pass); exact["m03"] = 0.99
    sc = score_c1(exact); check("exactly 0.99 passes (>=)", sc["held_registered"])
    eleven = {m: 0.995 for m in names[:11]}
    sc = score_c1(eleven); check("11 models is not a 12-roster: both FAILED", (not sc["held_registered"]) and (not sc["held_registrar"]))

    # 4. NON_TERMINATED > 5% refusal per model; a_m excludes NON_TERMINATED from both numerator and denominator
    ok, msg = nonterm_guard("m", 279, 14); check("14/279 = 5.02%% > 5%%: REFUSED (%s)" % msg.split(": ", 1)[1], not ok)
    ok, msg = nonterm_guard("m", 280, 14); check("14/280 = 5.00%: read (<= 5%)", ok)
    ok, msg = nonterm_guard("m", 279, 0); check("0/279: read", ok)
    ok, msg = nonterm_guard("m", 0, 0); check("no rows: refused", not ok)
    am = agreement_a_m([("A", "A", 0), ("B", "C", 0), ("D", "D", 1), ("", "", 0)])
    check("a_m: NON_TERMINATED row neither agrees nor disagrees: n_total 4, n 3, agree 2, a 0.667", am["n_total"] == 4 and am["n_nonterm"] == 1 and am["n"] == 3 and am["agree"] == 2 and abs(am["a"] - 2 / 3) < 1e-12)
    check("alarm threshold F=0.94 n=279 -> 0.897", abs(alarm_threshold(0.94, 279) - 0.897) < 5e-4)
    check("alarm threshold F=0.90 n=279 -> 0.846", abs(alarm_threshold(0.90, 279) - 0.846) < 5e-4)

    # 5. write-once
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "model_vintage_extractor_check.txt")
        write_once(p, "first\n")
        refused = False
        try: write_once(p, "second\n")
        except SystemExit: refused = True
        body = open(p, "rb").read()
        check("write-once: second write refused, first content intact, LF only", refused and body == b"first\n" and b"\r" not in body)

    # 6. the set hash function reproduces the record on a synthetic 2-match set (formula, not the file)
    ms = [dict(match_id=1, qid=10, model_a="a", model_b="b", stratum="cross"), dict(match_id=2, qid=11, model_a="c", model_b="d", stratum="contested")]
    check("set_hash is a 16-hex sha256 prefix of the canonical lines", re.fullmatch(r"[0-9a-f]{16}", set_hash(ms)) is not None
          and set_hash(ms) == hashlib.sha256(b"1:10:a:b:cross\n2:11:c:d:contested").hexdigest()[:16])

    # 7. this file is LF on disk and the header sha is the LF sha
    raw = open(os.path.abspath(__file__), "rb").read()
    check("script bytes on disk carry no CRLF (LF line endings)", b"\r\n" not in raw)
    check("header sha = sha256 of the LF bytes", script_sha_lf() == hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest())

    # 8. step 0b: the three variants
    check("tier1-blank: 'Answer: B' (t2) -> blank; 'The answer is (C)' -> C", extract_tier1_blank("Answer: B") == ("", "none") and extract_tier1_blank("The answer is (C).") == ("C", "t1"))
    check("tier1-blank: a bare last letter (t3) -> blank", extract_tier1_blank("options E and J; I pick J") == ("", "none"))
    check("three-tier-G: 'Answer: B' -> B (t2); no letter -> G (default); empty -> G", extract_three_tier_G("Answer: B") == ("B", "t2")
          and extract_three_tier_G("loop loop 42") == ("G", "default") and extract_three_tier_G("") == ("G", "default"))
    check("three-tier is extract-v1 itself; its variant sha = extract-v1's", VARIANT_FN["three-tier"] is extract_v1 and variant_sha("three-tier") == extractor_sha())
    check("three variant shas: 16-hex, pairwise distinct", all(re.fullmatch(r"[0-9a-f]{16}", variant_sha(v)) for v in VARIANT_ORDER) and len({variant_sha(v) for v in VARIANT_ORDER}) == 3)
    check("VARIANT_ORDER is simplest-first tier1-blank < three-tier < three-tier-G", VARIANT_ORDER == ("tier1-blank", "three-tier", "three-tier-G"))

    # 9. the metric under a variant; residuals by qid
    r_t1b = [("C", "The answer is (C)."), ("", "Answer: B"), ("", "last letter J")]
    rates = {v: reproduction_stats(r_t1b, VARIANT_FN[v])["rate"] for v in VARIANT_ORDER}
    check("H-tier1-blank rows: tier1-blank 3/3, three-tier 1/3, three-tier-G 1/3", rates == {"tier1-blank": 1.0, "three-tier": 1 / 3, "three-tier-G": 1 / 3})
    r_g = [("G", "a repetition loop with no letter"), ("A", "answer is (A)")]
    rates = {v: reproduction_stats(r_g, VARIANT_FN[v])["rate"] for v in VARIANT_ORDER}
    check("H-constantG rows: three-tier-G 2/2, three-tier 1/2, tier1-blank 1/2", rates == {"tier1-blank": 0.5, "three-tier": 0.5, "three-tier-G": 1.0})
    check("reproduction_stats default extractor is extract-v1 (the precheck unchanged)", reproduction_stats(r_t1b)["rate"] == 1 / 3)
    qr = [(2, "", "Answer: B"), (1, "C", "The answer is (C).")]
    check("residual_rows under three-tier = [(2, blank, B, t2)], under tier1-blank = []", residual_rows(qr, extract_v1) == [(2, "", "B", "t2")] and residual_rows(qr, extract_tier1_blank) == [])

    # 10. the assignment rule (a check) and the stated exception
    check("rule: {0.9, 1.0, 0.95} -> three-tier", best_variant({"tier1-blank": 0.9, "three-tier": 1.0, "three-tier-G": 0.95}) == ("three-tier", ["three-tier"]))
    check("rule: tie {1.0, 1.0, 0.9} -> tier1-blank (simplest), tied pair listed", best_variant({"tier1-blank": 1.0, "three-tier": 1.0, "three-tier-G": 0.9}) == ("tier1-blank", ["tier1-blank", "three-tier"]))
    check("rule: three-way tie -> tier1-blank", best_variant({v: 0.5 for v in VARIANT_ORDER})[0] == "tier1-blank")
    rc = rule_check("gpt-4o-2024-08-06", "H-threetier", {"tier1-blank": 0.9892, "three-tier": 1.0, "three-tier-G": 0.9964}, {"tier1-blank": 0.98, "three-tier": 1.0, "three-tier-G": 0.99})
    check("rule_check: canary best = assigned -> AGREES; full table -> FULLTABLE-AGREES", rc["verdict"] == "AGREES" and rc["fulltable_verdict"] == "FULLTABLE-AGREES")
    arx_c = {"tier1-blank": 277 / 279, "three-tier": 277 / 279, "three-tier-G": 0.9}
    rc = rule_check("arx_0314", "H-threetier", arx_c, {"tier1-blank": 0.9918, "three-tier": 0.9933, "three-tier-G": 0.9})
    check("arx-style tie (tier1-blank = three-tier on the canary), full table toward three-tier -> AGREES-BY-EXCEPTION", rc["verdict"] == "AGREES-BY-EXCEPTION" and rc["canary_best"] == "tier1-blank" and rc["fulltable_verdict"] == "FULLTABLE-AGREES")
    arx3 = {v: 277 / 279 for v in VARIANT_ORDER}
    rc = rule_check("arx_0314", "H-threetier", arx3, {"tier1-blank": 11907 / 12005, "three-tier": 11925 / 12005, "three-tier-G": 11925 / 12005})
    check("arx's real shape: a THREE-way canary tie (three-tier-G = three-tier, no blank extraction) and a full-table tie three-tier = three-tier-G > tier1-blank -> AGREES-BY-EXCEPTION, tied set printed",
          rc["verdict"] == "AGREES-BY-EXCEPTION" and rc["fulltable_best"] == "three-tier" and "tier1-blank/three-tier/three-tier-G" in rc["note"])
    rc = rule_check("arx_0314", "H-threetier", arx_c, {"tier1-blank": 0.9933, "three-tier": 0.9918, "three-tier-G": 0.9})
    check("arx-style tie but the full table toward tier1-blank -> CONTRADICTION-TIE + FULLTABLE-CONTRADICTION (membership unchanged)", rc["verdict"] == "CONTRADICTION-TIE" and rc["fulltable_verdict"] == "FULLTABLE-CONTRADICTION" and rc["assigned_variant"] == "three-tier")
    rc = rule_check("deepseek-chat-v2_5", "H-threetier", {"tier1-blank": 1.0, "three-tier": 1.0, "three-tier-G": 0.9}, {"tier1-blank": 0.9, "three-tier": 1.0, "three-tier-G": 0.9})
    check("the same tie on a model WITHOUT a stated exception -> CONTRADICTION-TIE (the exception is arx_0314's only)", rc["verdict"] == "CONTRADICTION-TIE")
    rc = rule_check("gemini-3.1-pro_5-shots", "H-threetier", {v: 1.0 for v in VARIANT_ORDER}, {"tier1-blank": 0.998, "three-tier": 1.0, "three-tier-G": 0.9986})
    check("gemini's real shape: all three at 1.0000 on the canary (uninformative) -> CONTRADICTION-TIE by the tie-break, FULLTABLE-AGREES; recorded, membership unchanged",
          rc["verdict"] == "CONTRADICTION-TIE" and rc["canary_best"] == "tier1-blank" and rc["fulltable_verdict"] == "FULLTABLE-AGREES" and rc["assigned_variant"] == "three-tier")
    rc = rule_check("Yi-6b-Chat", "H-tier1-blank", {"tier1-blank": 0.95, "three-tier": 1.0, "three-tier-G": 0.9}, {"tier1-blank": 1.0, "three-tier": 0.9, "three-tier-G": 0.9})
    check("a tier1-blank member whose canary best is three-tier -> CONTRADICTION (strict), printed, assigned variant still tier1-blank", rc["verdict"] == "CONTRADICTION" and rc["assigned_variant"] == "tier1-blank")

    # 11. the fixed membership of (1)
    fam_n = Counter(FAMILY_ASSIGNMENT.values())
    check("FAMILY_ASSIGNMENT: 12 models = 7 fixed checkpoints + 5 API rows; 5 / 2 / 5; EXCLUDED absent",
          len(FAMILY_ASSIGNMENT) == 12 and set(FIXED_CHECKPOINTS) <= set(FAMILY_ASSIGNMENT) and EXCLUDED not in FAMILY_ASSIGNMENT
          and fam_n == {"H-tier1-blank": 5, "H-constantG": 2, "H-threetier": 5})
    check("H-tier1-blank = {Llama-2-13b-hf, Llama-2-7b-hf, Qwen1.5-72B-Chat, Yi-6b-Chat, c4ai-command-r-v01}",
          {m for m, f in FAMILY_ASSIGNMENT.items() if f == "H-tier1-blank"} == {"Llama-2-13b-hf", "Llama-2-7b-hf", "Qwen1.5-72B-Chat", "Yi-6b-Chat", "c4ai-command-r-v01"})
    check("H-constantG = {Meta-Llama-3_1-70B-Instruct, Meta-Llama-3_1-8B}", {m for m, f in FAMILY_ASSIGNMENT.items() if f == "H-constantG"} == {"Meta-Llama-3_1-70B-Instruct", "Meta-Llama-3_1-8B"})
    check("H-threetier = {deepseek-chat-v2_5, gemini-3.1-pro_5-shots, gpt-4o-2024-08-06, iask_pro, arx_0314} (arx WITH the residual named, not its own family)",
          {m for m, f in FAMILY_ASSIGNMENT.items() if f == "H-threetier"} == {"deepseek-chat-v2_5", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "iask_pro", "arx_0314"})
    check("every exception names an assigned model and its assigned variant is in the tied pair; RECORDED_EXCLUSIONS empty today",
          all(m in FAMILY_ASSIGNMENT and FAMILY_VARIANT[FAMILY_ASSIGNMENT[m]] in pair for m, pair in ASSIGNMENT_EXCEPTIONS.items()) and RECORDED_EXCLUSIONS == ())

    # 12. the stamp, the exclusion rule (never re-assigned), the sidecar and its validation, the ingest gate, write-once
    def synth(model, n, n_fail=0):
        fam = FAMILY_ASSIGNMENT[model]; rows = []
        for i in range(n - n_fail):
            if fam == "H-tier1-blank": rows.append((i, "", "Answer: B") if i % 3 == 0 else (i, "C", "The answer is (C)."))
            elif fam == "H-constantG": rows.append((i, "G", "a loop with no letter") if i % 3 == 0 else (i, "A", "answer is (A)"))
            else: rows.append((i, "B", "Answer: B") if i % 3 == 0 else ((i, "", "a loop with no letter") if i % 3 == 1 else (i, "C", "The answer is (C).")))
        for i in range(n - n_fail, n):                      # rows that DISAGREE under the assigned variant only
            if fam == "H-tier1-blank": rows.append((i, "B", "Answer: B"))
            elif fam == "H-constantG": rows.append((i, "", "a loop with no letter"))
            else: rows.append((i, "B", "a loop with no letter"))
        return rows
    full_ok = dict(rows=1000, agree={"tier1-blank": 990, "three-tier": 1000, "three-tier-G": 995})
    e = stamp_model("Qwen1.5-72B-Chat", "H-tier1-blank", synth("Qwen1.5-72B-Chat", 100, 2), full_ok)
    check("exclusion: 98/100 under the ASSIGNED tier1-blank -> refused, harness_id UNASSIGNED, 2 residual qids, even though the rule's best IS tier1-blank (AGREES)",
          e["refused"] and e["harness_id"] == UNASSIGNED and e["extractor_variant"] == "tier1-blank" and e["reproduction"]["agree"] == 98
          and e["canary_table"]["three-tier"] == 0.67 and e["rule_check"]["verdict"] == "AGREES" and len(e["residual_qids"]) == 2)
    e = stamp_model("Qwen1.5-72B-Chat", "H-tier1-blank", [(i, "C", "The answer is (C).") for i in range(98)] + [(98, "B", "Answer: B"), (99, "D", "Answer: D")], full_ok)
    check("never re-assigned: 98/100 under tier1-blank while three-tier reads 1.0000 -> still refused, UNASSIGNED, variant tier1-blank, CONTRADICTION printed",
          e["refused"] and e["harness_id"] == UNASSIGNED and e["extractor_variant"] == "tier1-blank" and e["canary_table"]["three-tier"] == 1.0
          and e["rule_check"]["verdict"] == "CONTRADICTION" and [r["qid"] for r in e["residual_qids"]] == [98, 99])
    e = stamp_model("Qwen1.5-72B-Chat", "H-tier1-blank", synth("Qwen1.5-72B-Chat", 100, 1), dict(rows=1000, agree={"tier1-blank": 1000, "three-tier": 990, "three-tier-G": 995}))
    check("99/100 under the assigned variant passes (>=): harness_id = H-tier1-blank, 1 residual qid listed, rule AGREES",
          (not e["refused"]) and e["harness_id"] == "H-tier1-blank" and e["residual_qids"] == [dict(qid=99, pred="B", extract="", tier="none")] and e["rule_check"]["verdict"] == "AGREES")
    full_by_fam = {"H-tier1-blank": dict(rows=1000, agree={"tier1-blank": 1000, "three-tier": 900, "three-tier-G": 900}),
                   "H-constantG": dict(rows=1000, agree={"tier1-blank": 900, "three-tier": 900, "three-tier-G": 1000}),
                   "H-threetier": dict(rows=1000, agree={"tier1-blank": 990, "three-tier": 1000, "three-tier-G": 995})}
    def sidecar_with(failing):
        return build_sidecar({m: stamp_model(m, f, synth(m, 278 if m == "iask_pro" else 279, 3 if m in failing else 0), full_by_fam[f]) for m, f in FAMILY_ASSIGNMENT.items()})
    sc0 = sidecar_with(set())
    check("all 12 pass: A1 HELD, C1-H HELD, A2 0, no contradiction, premise not overturned, validates with the registered denominators",
          sc0["criteria"]["A1"] == "HELD" and sc0["criteria"]["C1H"] == "HELD" and sc0["criteria"]["A2_count"] == 0 and not sc0["criteria"]["contradictions"]
          and sc0["models"]["arx_0314"]["rule_check"]["verdict"] == "AGREES"
          and not sc0["criteria"]["premise_overturned"] and validate_sidecar(sc0) == [] and all(sc0["models"][m]["harness_id"] == f for m, f in FAMILY_ASSIGNMENT.items()))
    sc1 = sidecar_with({"Meta-Llama-3_1-8B"})
    check("one model at 276/279 under its variant: C1-H FAILED, A1 still HELD, A2 = [Meta-Llama-3_1-8B] stamped UNASSIGNED, premise stands, sidecar still validates",
          sc1["criteria"]["C1H"] == "FAILED" and sc1["criteria"]["A1"] == "HELD" and sc1["criteria"]["A2_refused"] == ["Meta-Llama-3_1-8B"]
          and sc1["models"]["Meta-Llama-3_1-8B"]["harness_id"] == UNASSIGNED and not sc1["criteria"]["premise_overturned"] and validate_sidecar(sc1) == [])
    sc3 = sidecar_with({"Llama-2-7b-hf", "iask_pro", "arx_0314"})
    check("three exclusions: premise_overturned True (the choice returns to the author)", sc3["criteria"]["A2_count"] == 3 and sc3["criteria"]["premise_overturned"])
    t = json.loads(json.dumps(sc0)); t["models"]["arx_0314"]["assigned_family"] = "H-tier1-blank"
    check("tampered membership (arx_0314 -> H-tier1-blank) does not validate", any("assigned_family" in p for p in validate_sidecar(t)))
    t = json.loads(json.dumps(sc0)); t["models"]["arx_0314"]["harness_id"] = "H-tier1-blank"
    check("a harness_id outside {family, UNASSIGNED} does not validate", any("harness_id" in p for p in validate_sidecar(t)))
    t = json.loads(json.dumps(sc0)); del t["models"]["iask_pro"]
    check("11 models do not validate", any("fixed membership" in p for p in validate_sidecar(t)))
    t = json.loads(json.dumps(sc0)); t["models"]["Yi-6b-Chat"]["refused"] = True
    check("refused flag inconsistent with the rate does not validate", any("refused" in p for p in validate_sidecar(t)))
    t = json.loads(json.dumps(sc0)); t["meta"]["set_hash"] = "0000000000000000"
    check("a foreign set hash does not validate", any("set_hash" in p for p in validate_sidecar(t)))
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "model_vintage_v0_harness.json")
        refused = False
        try: sidecar_gate(p)
        except SystemExit: refused = True
        check("ingest gate: missing sidecar -> refused", refused)
        write_once(p, json.dumps(sc1, indent=1) + "\n")
        refused = False
        try: sidecar_gate(p)
        except SystemExit as ex: refused = UNASSIGNED in str(ex)
        check("ingest gate: a sidecar with an UNASSIGNED model not in RECORDED_EXCLUSIONS -> refused, naming it", refused)
        refused = False
        try: write_once(p, "{}")
        except SystemExit: refused = True
        check("sidecar write-once: second write refused, content intact", refused and json.load(open(p, encoding="utf-8"))["criteria"]["C1H"] == "FAILED")
        p2 = os.path.join(td, "ok.json"); write_once(p2, json.dumps(sc0) + "\n")
        g = sidecar_gate(p2)
        check("ingest gate: a validating all-assigned sidecar passes and returns 12 harness_ids", g == FAMILY_ASSIGNMENT)
        body = open(p2, "rb").read(); check("sidecar bytes LF only", b"\r" not in body)
    # the outcome text renders from a synthetic sidecar without touching a DB
    L = stamp_lines(sc1, list(range(279)), 300, dict(set_hash=SET_HASH_OF_RECORD))
    check("stamp_lines: A1 HELD, C1-H FAILED, A2 1, the excluded model and its 3 residual qids printed, P-A1 FAILED",
          any(l.startswith("(A1)") and l.endswith("HELD") for l in L) and any(l.startswith("(C1-H)") and "FAILED" in l for l in L)
          and any(l.startswith("(A2)") and "models: 1" in l for l in L) and any("Meta-Llama-3_1-8B" in l and "q276" in l and "q278" in l for l in L)
          and any(l.startswith("P-A1") and l.endswith("FAILED") for l in L))

    n_fail = sum(1 for _, c in checks if not c)
    print("[SELFTEST] %d checks, %d failed; wrote nothing outside a temporary directory; 0 calls" % (len(checks), n_fail))
    if n_fail:
        raise SystemExit(1)


# ── entry ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pool_guard.assert_pool_of_record(POOL)
    print("[POOL] %s (pool of record; verified by pool_guard.assert_pool_of_record)" % POOL, flush=True)
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true", help="synthetic rows: extractor, metric, the >= 10 of 12 rule, the NON_TERMINATED refusal, write-once; step 0b: the three variants, the assignment rule and the arx-style tie, the exclusion rule, the sidecar, the ingest gate")
    ap.add_argument("--dry-run", action="store_true", help="pool id, roster, set hash, per-model row counts, what would be computed; writes nothing")
    ap.add_argument("--precheck", action="store_true", help="instrument step 0: extract-v1 reproduction of the cached pred (C1); needs --run to write")
    ap.add_argument("--run", action="store_true", help="with --precheck or --stamp-harness: compute and write the write-once outcome")
    ap.add_argument("--stamp-harness", action="store_true", help="step 0b (amendment (a)): the per-model harness stamp; takes exactly one of --dry-run | --run")
    ap.add_argument("--ingest", action="store_true", help="the author's generation pass: refuses until the sidecar validates, then refuses under this registration")
    ap.add_argument("--analyze", action="store_true", help="C2-C4 from a complete v1 cache: refuses until one exists")
    a = ap.parse_args()
    if a.stamp_harness:
        others = [k for k in ("selftest", "precheck", "ingest", "analyze") if getattr(a, k)]
        if others:
            raise SystemExit("--stamp-harness cannot be combined with %s" % others)
        if a.dry_run == a.run:
            raise SystemExit("--stamp-harness takes exactly one of --dry-run (prints the tables, writes nothing) | --run (writes the write-once sidecar)")
        cmd_stamp_harness(a.run)
        raise SystemExit(0)
    modes = [k for k in ("selftest", "dry_run", "precheck", "ingest", "analyze") if getattr(a, k)]
    if len(modes) != 1:
        raise SystemExit("exactly one of --selftest, --dry-run, --precheck, --stamp-harness, --ingest, --analyze (got %s)" % (modes or "none"))
    if a.run and not a.precheck:
        raise SystemExit("--run belongs to --precheck or --stamp-harness only")
    if a.selftest: cmd_selftest()
    elif a.dry_run: cmd_dry_run()
    elif a.precheck: cmd_precheck(a.run)
    elif a.ingest: cmd_ingest()
    elif a.analyze: cmd_analyze()
