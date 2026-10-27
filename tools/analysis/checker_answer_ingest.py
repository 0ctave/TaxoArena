"""CHECKER-ANSWER-INGEST (FRAMEWORK.md "Tests to register before shipping", item 7; registered by reference at
commit eaf1dbf against the text at 8d77f7b; scheduled in docs/plan_2026-09-15.md Block 1, pipelined into item 8).

  python tools/analysis/checker_answer_ingest.py

The item, verbatim:

  7. CHECKER-ANSWER-INGEST. Backfill normalised checker outputs for MATH (target) and IFEval (per-constraint
     vector). Criterion: D_c >= 0.95 on MATH; share of question-pairs offered on MATH falls below 50%.
     Prediction: MATH passes, IFEval stays below 0.95 and PREDICTIVE-ONLY. 0 LLM calls.

The record it cites (FRAMEWORK.md line 39; RESOLVE_stress_operations RISK 3; MatchFilter.kt): eval_results.pred
is blank on all 23,832 MATH and 9,738 IFEval rows, so AnswerDisagreementFilter returns UNDETERMINED on every
question-pair and keeps 100% of them. D_c = share of eval-side question-pairs with two non-blank extracted
answers; a cell below 0.95 is PREDICTIVE-ONLY for edges. "Offered" = kept by the filter = every pair whose
verdict is not AGREE (DISAGREE or UNDETERMINED), exactly MatchFilter.kt's keep(); the Kotlin comparison is
trimmed, case-insensitive string equality.

WHAT THIS SCRIPT DOES (zero LLM calls, zero network; every input is a committed file or a file already on disk):
  * MATH: the checker of record is the committed MATH-FIX extractor (math_fix.extract / normalise / equal;
    experiment_results/multicorpus/math_fix.txt defines "no extractable answer" as its own 217 rows). It runs over
    every stored model_output and records, per (question, model), the raw candidate, its normalised form, a
    canonical form (numerically equal answers printed in one spelling so that "9/4", "2.25" and "\\frac{9}{4}"
    compare equal under the Kotlin string rule) and the extraction tier: 1 = last \\boxed{}, 2 = "final answer
    is ...", 3 = last number in the final 400 characters (MATH-FIX's fallback). Correctness is recomputed with
    MATH-FIX's equal() and cross-checked against eval_results_mathfix (must be 0 differences).
  * IFEval: the checker of record is the leaderboard's own instruction checker; its per-constraint strict
    vector (inst_level_strict_acc) is read verbatim from the raw sample files already on disk under
    experiment_results/multicorpus/raw/<model>/*/samples_leaderboard_ifeval_*.jsonl, joined to the DB by
    doc_id == upstream_id and validated row by row (response text identical, prompt_level_strict_acc identical
    to the ingested is_correct, all(vector) == prompt_level_strict_acc). An offline re-implementation of the
    strict checkers (no langdetect, so language slots are undeterminable) is kept ONLY as a slot-level
    cross-check of the join; it is not the instrument.
  * Writes both tables into a NEW sqlite file experiment_results/multicorpus/checker_answers_v1.db (never touches
    multicorpus_cache_v1.db; refuses to replace a file it did not write) and the readout to
    experiment_results/x12_crossdomain/checker_answer_ingest.txt.

READINGS (where the item under-specifies, the reading hardest on the programme's claims is the verdict of record,
and the others are printed beside it):
  * Eval side = the union pool of record paeec37aa28063c75, addressed by explicit id (398 MATH / 162 IFEval
    questions; FRAMEWORK's "394" is GEN-ARENA's re-derived random split, which overlaps the pool by 114/394).
  * Pairs = all 153 unordered pairs of the 18 corpus models (Meta-Llama-3-70B-Instruct is not on this corpus).
  * Cell: the source row AND the minimum over the 7 designed MATH domain strata of the pool (hardest).
  * "Non-blank extracted answer" on MATH, three readings:
      A  checker of record (MATH-FIX tier 1-3), every row counted as the checker parses it;
      B  checker of record with the record's own NON_TERMINATED rule (FRAMEWORK guard 10 / reference rule line 37:
         a length-truncated generation yields no answer): a response whose <think> block is never closed is
         truncated by construction and its fallback number is blank.  [VERDICT OF RECORD: the hardest reading
         that the record's own rules support; the leaderboard stores no finish_reason, so only the R1 distills'
         truncation is detectable and B is a LOWER bound on truncation, i.e. still lenient];
      C  explicit answer statement only (tier 1-2), the fallback treated as a guess: STRICTER than the committed
         checker, printed as a diagnostic, not a verdict.
  * "Offered" share: the Kotlin string rule on the normalised form (hardest; the canonical numeric form can only
    lower it, printed beside); scored on the point estimate with the interval printed, and the bar also read
    against the interval.
  * IFEval: the checker's vector is complete on every row, so D_c is 1.000 by construction under reading A;
    reading B (unclosed <think> -> blank) is the hardest and is the verdict of record for the prediction.
No wrong-direction counts arise in this test (nothing is judged); the McNemar/established rule has no object here.
The key denominator for every share is named in the output.

RERUN SAFETY (2026-09-16): the backfill DB is written once. If experiment_results/multicorpus/checker_answers_v1.db already
exists and carries this script's meta table, the freshly computed rows are compared with it row by row and the file is
left untouched (item 8, CERT-CORPUS, reads it); a content mismatch is printed and the run exits non-zero without
overwriting. A file not written by this script is never replaced. Scoring convention for both criteria: the point
estimate against the bar, with the 95% question-bootstrap interval read beside it (PASS-AT-POINT / FAIL-AT-POINT when
the interval crosses the bar). The readout header carries the sha256 of this file (the producing code hash).

V2 MODE (2026-09-16, STAGE3-MATH re-registration prerequisite; zero LLM calls, zero network):

  python tools/analysis/checker_answer_ingest.py --v2

The checker's confirmed HIGH finding on this item: reading B's non_terminated column encodes the `<think>` proxy only,
while the raw lm-eval files cap MATH generation at max_gen_toks 1024 and 12-19% of the eval-side rows of models with no
`<think>` marker end at that cap mid-sentence. --v2 writes a NEW file experiment_results/multicorpus/checker_answers_v2.db
(table math_checker_answers_v2; checker_answers_v1.db is read, verified against its cited sha256 and NEVER rewritten)
carrying per (question_id, model_name): answer_norm / answer_canon / tier / is_correct (copied from v1),
non_terminated_think (v1's proxy), cl100k_tokens, last_char, abrupt_end, cap_hit (the CONSISTENT proxy) and
non_terminated = non_terminated_think OR cap_hit. The rule, exactly the checker's (scratch chk_cai_truncation2.py):
  cap      = max_gen_toks read from every raw MATH sample file on disk (asserted uniform; 1024);
  tokens   = cl100k_base count of the stored model_output (tiktoken, loaded from the local cache with the network
             client replaced by a raiser; the model's own tokenizer is not on disk; cl100k anchors at 0.98-1.00
             own-tokens per proxy token on Llama-3 / Qwen2.5, COST-AXES-INGEST);
  abrupt   = the last non-whitespace character of the response is NOT one of . } ) $ ! ? (an empty or
             whitespace-only response is abrupt);
  cap_hit  = tokens >= cap - CAP_SLACK (64; i.e. >= 960) AND abrupt;
  non_terminated = (unclosed <think>) OR cap_hit.
It prints per-model cap_hit rates, the 18-model and 16-model source rows and the 7 domain cells under reading B with
the consistent proxy (the checker's 0.6701 / 0.8167), the 8-model GEN-ARENA roster on this pool (STAGE3-MATH's cell)
and on GEN-ARENA's own scheduled questions (the checker's 0.8189), and writes the readout to
experiment_results/x12_crossdomain/checker_answer_ingest_v2.txt. The v1 readout and DB are not touched by --v2.
"""
import os, sys, re, json, math, sqlite3, collections, glob, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
import nltk
from nltk.tokenize import RegexpTokenizer
import pool_guard
import math_fix as mf

DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
RAW = os.path.join(ROOT, "experiment_results", "multicorpus", "raw")
NEW_DB = os.path.join(ROOT, "experiment_results", "multicorpus", "checker_answers_v1.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "checker_answer_ingest.txt")
GEN_ARENA = os.path.join(ROOT, "experiment_results", "multicorpus", "gen_arena_grok.db")
UNION_POOL = "paeec37aa28063c75"
EXCLUDE = {"Meta-Llama-3-70B-Instruct"}
DC_BAR = 0.95
OFFER_BAR = 0.50
B_BOOT = 2000
SEED = 42
# --v2 (consistent cap proxy)
NEW_DB_V2 = os.path.join(ROOT, "experiment_results", "multicorpus", "checker_answers_v2.db")
OUT_V2 = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "checker_answer_ingest_v2.txt")
V1_SHA256 = "cc4a4a29d166f172d657af27dd7e61df58dd2ef3e9e9c384b8c0fcb08654232e"     # cited in the programme record
CL100K_URL = "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
CAP_SLACK = 64                       # cap_hit threshold = max_gen_toks - CAP_SLACK (the checker's 960 at cap 1024)
ENDS = (".", "}", ")", "$", "!", "?")   # a response whose last non-whitespace character is one of these ended on purpose

# ----------------------------------------------------------------------------------------------------------------
# MATH: the committed MATH-FIX extractor, with the extraction tier made explicit
# ----------------------------------------------------------------------------------------------------------------

def math_extract(resp):
    """(candidate, tier) in MATH-FIX preference order (== mf.extract): 1 boxed, 2 'final answer is', 3 last number."""
    if not resp: return None, 0
    b = mf.last_braced(resp, mf.BOXED)
    if b is not None and b.strip(): return b, 1
    m = mf.FINAL.search(resp)
    if m and m.group(1).strip(): return m.group(1), 2
    n = mf.NUM.findall(resp[-400:])
    if n: return n[-1], 3
    return None, 0


def canonical(norm):
    """Kotlin compares trimmed case-insensitive strings; give numerically equal answers one spelling."""
    if norm is None or norm == "": return None
    v = mf.as_number(norm)
    if v is not None and math.isfinite(v):
        return ("%.12g" % v)
    return norm.lower()


def non_terminated(resp):
    """Truncation detectable from the text alone: a reasoning block that is opened and never closed."""
    r = resp or ""
    return "<think>" in r and "</think>" not in r


# ----------------------------------------------------------------------------------------------------------------
# IFEval: offline re-implementation of the strict checkers (google-research/instruction_following_eval), used only
# as a slot-level cross-check of the raw-file join. Returns True / False, or None where langdetect would be needed.
# ----------------------------------------------------------------------------------------------------------------

_WORD_TOK = RegexpTokenizer(r"\w+")


def _count_words(t): return len(_WORD_TOK.tokenize(t))


def _count_sentences(t): return len(nltk.sent_tokenize(t))


def _rel(actual, relation, n):
    if relation == "less than": return actual < n
    return actual >= n            # "at least" (the reference's default)


def _re_search(pat, text, flags=0):
    try: return re.search(pat, text, flags=flags)
    except re.error: return re.search(re.escape(pat), text, flags=flags)


def _re_findall(pat, text, flags=0):
    try: return re.findall(pat, text, flags=flags)
    except re.error: return re.findall(re.escape(pat), text, flags=flags)


def check_instruction(iid, kw, value, prompt):
    """kw already stripped of falsy entries, as the lm-eval harness does ({k: v for k, v in kwargs.items() if v})."""
    if iid == "keywords:existence":
        return all(_re_search(k, value, re.IGNORECASE) for k in kw["keywords"])
    if iid == "keywords:frequency":
        return _rel(len(_re_findall(kw["keyword"], value, re.IGNORECASE)), kw.get("relation", "at least"), kw["frequency"])
    if iid == "keywords:forbidden_words":
        for w in kw["forbidden_words"]:
            if _re_search(r"\b" + w + r"\b", value, re.IGNORECASE): return False
        return True
    if iid == "keywords:letter_frequency":
        letters = collections.Counter(value.lower())
        return _rel(letters[kw["letter"].strip().lower()], kw.get("let_relation", "at least"), kw["let_frequency"])
    if iid == "language:response_language":
        return None                                    # needs langdetect; not installed, no network
    if iid == "length_constraints:number_sentences":
        return _rel(_count_sentences(value), kw.get("relation", "at least"), kw["num_sentences"])
    if iid == "length_constraints:number_paragraphs":
        paras = re.split(r"\s?\*\*\*\s?", value); num = len(paras)
        for i, p in enumerate(paras):
            if not p.strip():
                if i == 0 or i == len(paras) - 1: num -= 1
                else: return False
        return num == kw["num_paragraphs"]
    if iid == "length_constraints:number_words":
        return _rel(_count_words(value), kw.get("relation", "at least"), kw["num_words"])
    if iid == "length_constraints:nth_paragraph_first_word":
        paras = re.split(r"\n\n", value); num = len(paras)
        for p in paras:
            if not p.strip(): num -= 1
        nth = kw["nth_paragraph"]
        if nth <= num:
            p = paras[nth - 1].strip()
            if not p: return False
        else:
            return False
        first = ""; punct = {".", ",", "?", "!", "'", '"'}
        w = p.split()[0].strip().lstrip("'").lstrip('"')
        for ch in w:
            if ch in punct: break
            first += ch.lower()
        return num == kw["num_paragraphs"] and first == kw["first_word"].lower()
    if iid == "detectable_content:number_placeholders":
        return len(re.findall(r"\[.*?\]", value)) >= kw["num_placeholders"]
    if iid == "detectable_content:postscript":
        v = value.lower(); mk = kw["postscript_marker"]
        if mk == "P.P.S": pat = r"\s*p\.\s?p\.\s?s.*$"
        elif mk == "P.S.": pat = r"\s*p\.\s?s\..*$"
        else: pat = r"\s*" + mk.lower() + r".*$"
        return bool(re.findall(pat, v, flags=re.MULTILINE))
    if iid == "detectable_format:number_bullet_lists":
        n = len(re.findall(r"^\s*\*[^\*].*$", value, flags=re.MULTILINE)) + len(re.findall(r"^\s*-.*$", value, flags=re.MULTILINE))
        return n == kw["num_bullets"]
    if iid == "detectable_format:constrained_response":
        v = value.strip()
        return any(c in v for c in ("My answer is yes.", "My answer is no.", "My answer is maybe."))
    if iid == "detectable_format:number_highlighted_sections":
        n = 0
        for h in re.findall(r"\*[^\n\*]*\*", value):
            if h.strip("*").strip(): n += 1
        for h in re.findall(r"\*\*[^\n\*]*\*\*", value):
            if h.removeprefix("**").removesuffix("**").strip(): n += 1
        return n >= kw["num_highlights"]
    if iid == "detectable_format:multiple_sections":
        pat = r"\s?" + kw["section_spliter"] + r"\s?\d+\s?"
        return len(re.split(pat, value)) - 1 >= kw["num_sections"]
    if iid == "detectable_format:json_format":
        v = value.strip().removeprefix("```json").removeprefix("```Json").removeprefix("```JSON").removeprefix("```").removesuffix("```").strip()
        try: json.loads(v)
        except ValueError: return False
        return True
    if iid == "detectable_format:title":
        for t in re.findall(r"<<[^\n]+>>", value):
            if t.lstrip("<").rstrip(">").strip(): return True
        return False
    if iid == "combination:two_responses":
        parts = value.split("******"); valid = []
        for i, r in enumerate(parts):
            if not r.strip():
                if i != 0 and i != len(parts) - 1: return False
            else: valid.append(r)
        return len(valid) == 2 and valid[0].strip() != valid[1].strip()
    if iid == "combination:repeat_prompt":
        return value.strip().lower().startswith(kw.get("prompt_to_repeat", prompt).strip().lower())
    if iid == "startend:end_checker":
        return value.strip().strip('"').lower().endswith(kw["end_phrase"].strip().lower())
    if iid == "startend:quotation":
        v = value.strip(); return len(v) > 1 and v[0] == '"' and v[-1] == '"'
    if iid == "change_case:capital_word_frequency":
        words = nltk.word_tokenize(value)
        return _rel(sum(1 for w in words if w.isupper()), kw.get("capital_relation", "at least"), kw["capital_frequency"])
    if iid == "change_case:english_capital":
        return None if value.isupper() else False        # 'and langdetect == en' cannot be evaluated
    if iid == "change_case:english_lowercase":
        return None if value.islower() else False
    if iid == "punctuation:no_comma":
        return not re.search(r"\,", value)
    raise KeyError("unknown instruction id " + iid)


def ifeval_reimpl_vector(target_json, value, prompt):
    spec = json.loads(target_json); out = []
    for iid, kw in zip(spec["instruction_id_list"], spec["kwargs"]):
        kw = {k: v for k, v in (kw or {}).items() if v}
        if not value.strip(): out.append(False); continue     # harness: empty response follows nothing
        try: out.append(check_instruction(iid, kw, value, prompt))
        except Exception:
            out.append(None)
    return spec["instruction_id_list"], out


def load_raw_ifeval_vectors(models):
    """Per (model, doc_id): (prompt, response, prompt_level_strict_acc, inst_level_strict_acc, instruction_id_list)
    read from the leaderboard's own sample files on disk. Zero network."""
    raw = {}
    for m in models:
        fs = glob.glob(os.path.join(RAW, m, "*", "samples_leaderboard_ifeval_*.jsonl"))
        if len(fs) != 1: raise SystemExit("[RAW] expected exactly one IFEval sample file for %s, found %d" % (m, len(fs)))
        with open(fs[0], encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                resp = r["resps"][0][0] if r.get("resps") else None
                raw[(m, int(r["doc_id"]))] = (r["doc"]["prompt"], resp, bool(r["prompt_level_strict_acc"]),
                                              [bool(v) for v in r["inst_level_strict_acc"]], list(r["doc"]["instruction_id_list"]))
    return raw


# ----------------------------------------------------------------------------------------------------------------
# shares with question-bootstrap intervals
# ----------------------------------------------------------------------------------------------------------------

def boot_share(per_q_num, per_q_den, B=B_BOOT, seed=SEED):
    """per_q_num/den: arrays over questions. Share = sum(num)/sum(den); percentile CI over question resamples."""
    num = np.asarray(per_q_num, float); den = np.asarray(per_q_den, float); n = len(num)
    if n == 0 or den.sum() == 0: return float("nan"), (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    s = num[idx].sum(1) / den[idx].sum(1)
    return num.sum() / den.sum(), (float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5)))


def pair_stats(qids, X, models, agree_fn):
    """Per question: (#pairs both non-blank, #AGREE, #DISAGREE, #UNDETERMINED, #pairs) under a given answer map X[q][m]."""
    pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    rows = []
    for q in qids:
        det = ag = dis = und = 0
        for a, b in pairs:
            xa = X.get(q, {}).get(a); xb = X.get(q, {}).get(b)
            if xa is None or xb is None: und += 1; continue
            det += 1
            if agree_fn(xa, xb): ag += 1
            else: dis += 1
        rows.append((det, ag, dis, und, len(pairs)))
    return np.array(rows, float), pairs


def decidability(qids, X, G, models, agree_fn):
    """The record's SCHEDULING diagnostic, key-derived and read-only: among AGREE / DISAGREE / UNDETERMINED pairs,
    the share where exactly one model is correct (the pair carries a correctness signal)."""
    pairs = [(models[i], models[j]) for i in range(len(models)) for j in range(i + 1, len(models))]
    c = {"AGREE": [0, 0], "DISAGREE": [0, 0], "UNDETERMINED": [0, 0]}
    for q in qids:
        for a, b in pairs:
            xa = X.get(q, {}).get(a); xb = X.get(q, {}).get(b)
            ga = G.get(q, {}).get(a); gb = G.get(q, {}).get(b)
            if ga is None or gb is None: continue
            v = "UNDETERMINED" if (xa is None or xb is None) else ("AGREE" if agree_fn(xa, xb) else "DISAGREE")
            c[v][1] += 1
            if ga != gb: c[v][0] += 1
    return c


def fmt_ci(v, ci): return "%.4f [%.4f, %.4f]" % (v, ci[0], ci[1])


# ----------------------------------------------------------------------------------------------------------------

def main():
    t0 = time.time(); L = []
    def P(s=""): print(s); L.append(s)

    # --- guards ---------------------------------------------------------------------------------------------------
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)          # MMLU-Pro pool of record, by id
    pool_guard.assert_pool_of_record(UNION_POOL)                        # union pool of record, by id
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    P("CHECKER-ANSWER-INGEST  (FRAMEWORK item 7; registered by reference at eaf1dbf; 0 LLM calls, 0 network)")
    P("producing code hash: sha256 %s  (%s)" % (hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
                                               os.path.relpath(os.path.abspath(__file__), ROOT).replace(os.sep, "/")))
    P("[POOL-GUARD] mmlu_pro dataset DB pool of record %s verified by id" % pool_guard.MMLU_PRO_POOL)
    P("[POOL-PIN]   multicorpus DB union pool %s verified by id; this script addresses it BY EXPLICIT ID" % UNION_POOL)

    # --- corpus ---------------------------------------------------------------------------------------------------
    Q = {}
    for qid, src, task, dom, up, text, target in con.execute(
            "SELECT question_id, source, task, domain, upstream_id, text, target FROM corpus_questions WHERE source IN ('MATH','IFEVAL')"):
        Q[qid] = dict(source=src, task=task, domain=dom, upstream=up, text=text, target=target)
    pool = {}
    for qid, dom in con.execute("SELECT question_id, domain FROM reserved_pool WHERE pool_id = ?", (UNION_POOL,)):
        if qid in Q: pool[qid] = dom
    eval_q = {s: sorted(q for q in pool if Q[q]["source"] == s) for s in ("MATH", "IFEVAL")}
    models = sorted({m for (m,) in con.execute(
        "SELECT DISTINCT e.model_name FROM eval_results e JOIN corpus_questions q USING(question_id) WHERE q.source IN ('MATH','IFEVAL')")} - EXCLUDE)
    n_pairs = len(models) * (len(models) - 1) // 2
    P("corpus: MATH %d questions (eval-side in %s: %d) | IFEVAL %d (eval-side: %d) | models %d -> %d unordered pairs | excluded: %s"
      % (sum(1 for q in Q if Q[q]["source"] == "MATH"), UNION_POOL, len(eval_q["MATH"]),
         sum(1 for q in Q if Q[q]["source"] == "IFEVAL"), len(eval_q["IFEVAL"]), len(models), n_pairs, ", ".join(sorted(EXCLUDE))))
    P("KEY DENOMINATOR: eval-side question-pairs = union-pool questions x %d model pairs: MATH %d x %d = %d; IFEVAL %d x %d = %d"
      % (n_pairs, len(eval_q["MATH"]), n_pairs, len(eval_q["MATH"]) * n_pairs, len(eval_q["IFEVAL"]), n_pairs, len(eval_q["IFEVAL"]) * n_pairs))

    blank = con.execute("SELECT q.source, SUM(e.pred IS NULL OR TRIM(e.pred)=''), COUNT(*) FROM eval_results e JOIN corpus_questions q USING(question_id) "
                        "WHERE q.source IN ('MATH','IFEVAL') GROUP BY 1").fetchall()
    P("baseline (eval_results.pred as ingested): " + "; ".join("%s blank %d of %d" % r for r in blank) + "  -> D_c = 0.000 on both, filter keeps 100%")

    # --- MATH backfill --------------------------------------------------------------------------------------------
    P(); P("=" * 110); P("MATH: checker-output backfill over every stored model_output (checker of record = MATH-FIX extractor, committed helper)"); P("=" * 110)
    mathfix = {(q, m): int(c) for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix")}
    math_rows = []; tier_count = collections.Counter(); xfix_dis = 0; raised = 0
    X_A, X_A_can, X_B, X_C, X_C_can, G_math = ({} for _ in range(6))
    trunc = collections.Counter(); trunc_rows = collections.Counter()
    for qid, m, resp, old in con.execute("SELECT e.question_id, e.model_name, e.model_output, e.is_correct FROM eval_results e "
                                         "JOIN corpus_questions q USING(question_id) WHERE q.source='MATH'"):
        if m in EXCLUDE: continue
        cand, tier = math_extract(resp or "")
        assert cand == mf.extract(resp or ""), "tiered extractor must equal the committed mf.extract"
        cands = mf.extract_all(resp or "")
        norm = mf.normalise(cand) if cand is not None else None
        if norm == "": norm = None; tier = 0
        can = canonical(norm)
        nt = int(non_terminated(resp))
        ok = 1 if (mf.equal(cand, Q[qid]["target"], cands) or old) else 0      # MATH-FIX rule: only ever raise
        if mathfix.get((qid, m)) is not None and mathfix[(qid, m)] != ok: xfix_dis += 1
        if ok and not old: raised += 1
        tier_count[tier] += 1
        trunc_rows[m] += 1
        if nt: trunc[m] += 1
        math_rows.append((qid, m, cand, norm, can, tier, nt, ok, mathfix.get((qid, m))))
        G_math.setdefault(qid, {})[m] = ok
        if norm is not None:
            X_A.setdefault(qid, {})[m] = norm; X_A_can.setdefault(qid, {})[m] = can
            if not nt: X_B.setdefault(qid, {})[m] = norm
            if tier in (1, 2):
                X_C.setdefault(qid, {})[m] = norm; X_C_can.setdefault(qid, {})[m] = can
    P("rows backfilled: %d | extraction tier: boxed %d, 'final answer is' %d, last-number fallback %d, nothing %d"
      % (len(math_rows), tier_count[1], tier_count[2], tier_count[3], tier_count[0]))
    P("cross-check against eval_results_mathfix (MATH-FIX's committed correctness): %d of %d rows differ; cells raised over the ingested key %d (MATH-FIX recorded 5,181)" % (xfix_dis, len(math_rows), raised))
    if xfix_dis: raise SystemExit("[MISMATCH] the backfill does not reproduce eval_results_mathfix; aborting before any stratum")
    P("NON_TERMINATED (unclosed <think>, the only truncation the leaderboard text makes detectable): %d of %d rows; by model: %s"
      % (sum(trunc.values()), len(math_rows), ", ".join("%s %d/%d" % (m, trunc[m], trunc_rows[m]) for m in sorted(trunc, key=lambda m: -trunc[m]))))
    per_model = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for qid, m, cand, norm, can, tier, nt, ok, _ in math_rows:
        r = per_model[m]; r[4] += 1
        if tier in (1, 2): r[0] += 1
        if norm is not None: r[1] += 1
        if norm is not None and not nt: r[2] += 1
        r[3] += ok
    P("%-30s %10s %12s %10s %8s" % ("model (all 1,324 q)", "A checker", "B non-trunc", "C explicit", "acc"))
    for m in sorted(per_model, key=lambda m: -per_model[m][0]):
        r = per_model[m]; P("  %-28s %10.3f %12.3f %10.3f %8.3f" % (m, r[1] / r[4], r[2] / r[4], r[0] / r[4], r[3] / r[4]))

    str_eq = lambda a, b: a.strip().lower() == b.strip().lower()        # MatchFilter.kt: trimmed, case-insensitive

    P(); P("D_c per cell = share of eval-side question-pairs with two non-blank extracted answers (question-bootstrap 95%% CI, B=%d)" % B_BOOT)
    cells = collections.OrderedDict(); cells["MATH (source row)"] = eval_q["MATH"]
    for d in sorted(set(pool[q] for q in eval_q["MATH"])):
        cells[d] = [q for q in eval_q["MATH"] if pool[q] == d]
    LA = "A: checker of record (MATH-FIX tier 1-3), every row"
    LB = "B: checker of record + NON_TERMINATED rule (unclosed <think> -> blank)  [VERDICT OF RECORD]"
    LC = "C: explicit answer statement only (tier 1-2)  [stricter than the checker; diagnostic]"
    readings = [(LA, X_A), (LB, X_B), (LC, X_C)]
    dc_res = {}
    for label, X in readings:
        P("  reading %s" % label)
        P("  %-32s %6s %8s %20s" % ("cell", "q", "D_c", "95% CI"))
        for cname, qs in cells.items():
            st, _ = pair_stats(qs, X, models, str_eq)
            v, ci = boot_share(st[:, 0], st[:, 4])
            dc_res[(label, cname)] = (v, ci, len(qs)); P("  %-32s %6d %8.4f   [%.4f, %.4f]" % (cname, len(qs), v, ci[0], ci[1]))
        mn_c = min((c for c in cells if c != "MATH (source row)"), key=lambda c: dc_res[(label, c)][0])
        P("  min over the 7 domain cells: %s at %s" % (fmt_ci(dc_res[(label, mn_c)][0], dc_res[(label, mn_c)][1]), mn_c))
        no_r1 = [m for m in models if not m.startswith("DeepSeek-R1")]
        st, _ = pair_stats(eval_q["MATH"], X, no_r1, str_eq); v, ci = boot_share(st[:, 0], st[:, 4])
        P("  diagnostic, source row without the two R1 distills (%d models, %d pairs): D_c %s"
          % (len(no_r1), len(no_r1) * (len(no_r1) - 1) // 2, fmt_ci(v, ci)))

    # offered share on MATH
    P(); P("share of eval-side MATH question-pairs OFFERED = kept by AnswerDisagreementFilter.keep() = not AGREE (DISAGREE + UNDETERMINED)")
    off_res = {}
    for label, Xn, Xc in [(LA, X_A, X_A_can), (LB, X_B, None), (LC, X_C, X_C_can)]:
        for cmp_label, X in [("string rule, normalised form [hardest]", Xn), ("string rule, canonical numeric form", Xc)]:
            if X is None: continue
            st, _ = pair_stats(eval_q["MATH"], X, models, str_eq)
            v, ci = boot_share(st[:, 4] - st[:, 1], st[:, 4])      # offered = total - AGREE
            dis, _ = boot_share(st[:, 2], st[:, 4]); und, _ = boot_share(st[:, 3], st[:, 4]); ag, _ = boot_share(st[:, 1], st[:, 4])
            off_res[(label, cmp_label)] = (v, ci, dis, und, ag)
            P("  %-3s %-40s offered %s  (DISAGREE %.4f, UNDETERMINED %.4f, AGREE %.4f)"
              % (label[:2], cmp_label, fmt_ci(v, ci), dis, und, ag))
    P("  per domain cell (reading B, string rule on normalised form):")
    for cname, qs in cells.items():
        if cname == "MATH (source row)": continue
        st, _ = pair_stats(qs, X_B, models, str_eq); v, ci = boot_share(st[:, 4] - st[:, 1], st[:, 4])
        P("    %-30s q=%3d offered %s" % (cname, len(qs), fmt_ci(v, ci)))
    # why the share is high: the roster's accuracy spread; agreement between two models is bounded by their joint correctness
    P("  context: MMLU-Pro's 16.9%% was measured on a frontier roster; on MATH the roster spans accuracy %.3f-%.3f, so most pairs"
      % (min(per_model[m][3] / per_model[m][4] for m in models), max(per_model[m][3] / per_model[m][4] for m in models)))
    top = [m for m in models if per_model[m][3] / per_model[m][4] >= 0.47]
    st, _ = pair_stats(eval_q["MATH"], X_A, top, str_eq); v, ci = boot_share(st[:, 4] - st[:, 1], st[:, 4])
    P("           genuinely disagree. Offered share among the %d models with accuracy >= 0.47 (reading A, normalised; %d pairs):" % (len(top), len(top) * (len(top) - 1) // 2))
    P("           %s -> offered %s" % (", ".join(top), fmt_ci(v, ci)))

    # the record's decidability diagnostic (key-derived, read-only; the filter itself never sees it)
    P(); P("diagnostic (key-derived via eval_results_mathfix; the filter never reads it): key-decidable share by filter verdict")
    for label, X in [(LA, X_A), (LB, X_B), (LC, X_C)]:
        dec = decidability(eval_q["MATH"], X, G_math, models, str_eq)
        tot_dec = sum(dec[k][0] for k in dec); kept_dec = dec["DISAGREE"][0] + dec["UNDETERMINED"][0]
        P("  %-3s " % label[:2] + "; ".join("%s %d pairs, decidable %d (%.4f)" % (k, dec[k][1], dec[k][0], dec[k][0] / max(1, dec[k][1])) for k in ("DISAGREE", "UNDETERMINED", "AGREE"))
          + "; decidable pairs kept %d of %d (%.4f)" % (kept_dec, tot_dec, kept_dec / max(1, tot_dec)))
    P("  record on MMLU-Pro: 99.8% of decidable pairs kept while judging 16.9%")

    # --- IFEval backfill: the leaderboard checker's own per-constraint strict vector, from the raw sample files ---------
    P(); P("=" * 110); P("IFEVAL: per-constraint strict pass vector = the leaderboard checker's inst_level_strict_acc, read from the raw sample files on disk"); P("=" * 110)
    raw = load_raw_ifeval_vectors(models)
    if_rows = []; join = collections.Counter(); reimpl = collections.Counter(); reimpl_iid = collections.Counter()
    X_if_A, X_if_B, G_if = {}, {}, {}
    n_slots = 0; n_true = 0; trunc_if = 0; empty_if = 0
    for qid, m, resp, old in con.execute("SELECT e.question_id, e.model_name, e.model_output, e.is_correct FROM eval_results e "
                                         "JOIN corpus_questions q USING(question_id) WHERE q.source='IFEVAL'"):
        if m in EXCLUDE: continue
        r = raw.get((m, Q[qid]["upstream"]))
        if r is None: join["missing"] += 1; continue
        prompt, rresp, pstrict, vec, ids = r
        spec_ids = json.loads(Q[qid]["target"])["instruction_id_list"]
        okj = (prompt == Q[qid]["text"] and rresp == resp and int(pstrict) == int(old) and all(vec) == pstrict and len(vec) == len(ids) and ids == spec_ids)
        join["ok" if okj else "MISMATCH"] += 1
        if not okj: continue
        # slot-level cross-check with the offline re-implementation (determinate slots only)
        _, rv = ifeval_reimpl_vector(Q[qid]["target"], resp or "", Q[qid]["text"])
        for iid, a, b in zip(ids, rv, vec):
            if a is None: reimpl["undeterminable offline"] += 1; continue
            reimpl["agree" if bool(a) == bool(b) else "disagree"] += 1
            if bool(a) != bool(b): reimpl_iid[iid] += 1
        nt = int(non_terminated(resp)); trunc_if += nt; empty_if += int(not (resp or '').strip())
        n_slots += len(vec); n_true += sum(vec)
        v = tuple(int(x) for x in vec)
        if_rows.append((qid, m, json.dumps(ids), json.dumps(list(v)), len(v), int(all(vec)), nt, int(old)))
        G_if.setdefault(qid, {})[m] = int(old)
        X_if_A.setdefault(qid, {})[m] = v
        if not nt: X_if_B.setdefault(qid, {})[m] = v
    P("raw-file join by (model, doc_id == upstream_id): %s" % dict(join))
    if join["MISMATCH"] or join["missing"]: raise SystemExit("[MISMATCH] raw IFEval rows do not reproduce the ingested rows; aborting before any stratum")
    P("rows backfilled: %d | constraint slots %d, all determined by the checker (pass %d, fail %d) | NON_TERMINATED rows (unclosed <think>) %d"
      % (len(if_rows), n_slots, n_true, n_slots - n_true, trunc_if))
    P("cross-check, offline re-implementation vs the checker's slots (validates the join; the raw vector is the instrument): %s%s"
      % (dict(reimpl), ("; disagreeing slots by instruction: " + ", ".join("%s %d" % kv for kv in reimpl_iid.most_common(6))) if reimpl_iid else ""))

    vec_eq = lambda a, b: a == b
    st_a, _ = pair_stats(eval_q["IFEVAL"], X_if_A, models, vec_eq)
    st_b, _ = pair_stats(eval_q["IFEVAL"], X_if_B, models, vec_eq)
    dca, cia = boot_share(st_a[:, 0], st_a[:, 4]); offa, cioa = boot_share(st_a[:, 4] - st_a[:, 1], st_a[:, 4])
    dcb, cib = boot_share(st_b[:, 0], st_b[:, 4]); offb, ciob = boot_share(st_b[:, 4] - st_b[:, 1], st_b[:, 4])
    P(); P("IFEVAL D_c on the %d eval-side questions x %d pairs = %d question-pairs:" % (len(eval_q["IFEVAL"]), n_pairs, len(eval_q["IFEVAL"]) * n_pairs))
    P("  A: checker vector, every row:                    D_c %s   offered %s" % (fmt_ci(dca, cia), fmt_ci(offa, cioa)))
    P("  B: + NON_TERMINATED rule [verdict of record]:    D_c %s   offered %s" % (fmt_ci(dcb, cib), fmt_ci(offb, ciob)))
    dec_if = decidability(eval_q["IFEVAL"], X_if_A, G_if, models, vec_eq)
    P("  diagnostic (key = prompt_level_strict_acc): " + "; ".join(
        "%s %d pairs, decidable %.4f" % (k, dec_if[k][1], dec_if[k][0] / max(1, dec_if[k][1])) for k in ("DISAGREE", "UNDETERMINED", "AGREE")))
    # strictness note: two different vectors can still both be all-pass? no: all-pass is one vector. Two all-fail vectors agree.
    # The vector filter therefore skips pairs where both responses satisfy exactly the same constraint subset.

    # --- GEN-ARENA questions (for item 8; labelled) ---------------------------------------------------------------
    P(); P("for CERT-CORPUS (item 8): the same readings on the questions GEN-ARENA actually scheduled")
    try:
        g = sqlite3.connect("file:%s?mode=ro" % GEN_ARENA, uri=True)
        gq = collections.defaultdict(set); groster = set()
        for s, q, a, b in g.execute("SELECT source, qid, model_a, model_b FROM schedule"):
            gq[s].add(q); groster.update((a, b))
        groster = sorted(groster - EXCLUDE)
        for s in ("MATH", "IFEVAL"):
            inpool = len(gq[s] & set(pool)); P("  %s: %d scheduled questions, %d in the union pool %s (the schedule re-derived a random.Random(42) split; not the pool of record)"
                                              % (s, len(gq[s]), inpool, UNION_POOL))
        for label, X in [(LA, X_A), (LB, X_B), (LC, X_C)]:
            stg, _ = pair_stats(sorted(gq["MATH"]), X, groster, str_eq); v, ci = boot_share(stg[:, 0], stg[:, 4]); o, oci = boot_share(stg[:, 4] - stg[:, 1], stg[:, 4])
            P("  MATH, GEN-ARENA roster (%d models, %d pairs), %s: D_c %s; offered %s" % (len(groster), len(groster) * (len(groster) - 1) // 2, label[:2], fmt_ci(v, ci), fmt_ci(o, oci)))
        for label, X in [(LA, X_A), (LB, X_B)]:
            n_ag = n_tot = n_und = 0
            for s, q, a, b in g.execute("SELECT source, qid, model_a, model_b FROM verdicts WHERE source='MATH' AND invalid=0"):
                xa = X.get(q, {}).get(a); xb = X.get(q, {}).get(b); n_tot += 1
                if xa is None or xb is None: n_und += 1
                elif str_eq(xa, xb): n_ag += 1
            P("  MATH judged matches in the GEN-ARENA cache, %s: %d, of which AGREE under the backfilled answers %d (%.1f%%), UNDETERMINED %d" % (label[:2], n_tot, n_ag, 100.0 * n_ag / max(1, n_tot), n_und))
        stg, _ = pair_stats(sorted(gq["IFEVAL"]), X_if_A, groster, vec_eq); v, ci = boot_share(stg[:, 0], stg[:, 4]); o, oci = boot_share(stg[:, 4] - stg[:, 1], stg[:, 4])
        P("  IFEVAL, GEN-ARENA roster, checker vectors: D_c %s; offered %s" % (fmt_ci(v, ci), fmt_ci(o, oci)))
        n_ag = n_tot = 0
        for s, q, a, b in g.execute("SELECT source, qid, model_a, model_b FROM verdicts WHERE source='IFEVAL' AND invalid=0"):
            xa = X_if_A.get(q, {}).get(a); xb = X_if_A.get(q, {}).get(b); n_tot += 1
            if xa is not None and xb is not None and xa == xb: n_ag += 1
        P("  IFEVAL judged matches in the GEN-ARENA cache: %d, of which AGREE (identical vectors) %d (%.1f%%)" % (n_tot, n_ag, 100.0 * n_ag / max(1, n_tot)))
    except Exception as e:
        P("  GEN-ARENA cache not readable: %r" % (e,))

    # --- write the new DB -----------------------------------------------------------------------------------------
    if os.path.exists(NEW_DB):
        # the file is item 8's input: verify it against the fresh backfill row by row, never rewrite it
        chk = sqlite3.connect("file:%s?mode=ro" % NEW_DB, uri=True)
        own = chk.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checker_answer_ingest_meta'").fetchone()
        if not own:
            chk.close(); raise SystemExit("[REFUSE] %s exists and was not written by this script; will not overwrite" % NEW_DB)
        old_math = sorted(tuple(r) for r in chk.execute("SELECT question_id, model_name, x_raw, x_norm, x_canon, tier, non_terminated, checker_correct, mathfix_correct FROM math_checker_answers"))
        old_if = sorted(tuple(r) for r in chk.execute("SELECT question_id, model_name, instruction_ids, strict_vector, n_constraints, all_pass_strict, non_terminated, ingested_is_correct FROM ifeval_checker_answers"))
        written_at = dict(chk.execute("SELECT key, value FROM checker_answer_ingest_meta")).get("written_at")
        chk.close()
        new_math = sorted(tuple(r) for r in math_rows); new_if = sorted(tuple(r) for r in if_rows)
        d_math = sum(1 for a, b in zip(old_math, new_math) if a != b) + abs(len(old_math) - len(new_math))
        d_if = sum(1 for a, b in zip(old_if, new_if) if a != b) + abs(len(old_if) - len(new_if))
        P(); P("%s already exists (written %s by this script): VERIFIED against the fresh backfill: math rows differing %d of %d, ifeval rows differing %d of %d; file left untouched (item 8 reads it)"
               % (NEW_DB, written_at, d_math, len(math_rows), d_if, len(if_rows)))
        if d_math or d_if:
            P("[MISMATCH] the existing backfill DB does not reproduce the fresh backfill; NOT overwritten; readout written, exiting non-zero")
            with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
            raise SystemExit(2)
    else:
        w = sqlite3.connect(NEW_DB)
        w.execute("CREATE TABLE checker_answer_ingest_meta (key TEXT PRIMARY KEY, value TEXT)")
        w.execute("CREATE TABLE math_checker_answers (question_id INTEGER, model_name TEXT, x_raw TEXT, x_norm TEXT, x_canon TEXT, "
                  "tier INTEGER, non_terminated INTEGER, checker_correct INTEGER, mathfix_correct INTEGER, PRIMARY KEY (question_id, model_name))")
        w.execute("CREATE TABLE ifeval_checker_answers (question_id INTEGER, model_name TEXT, instruction_ids TEXT, strict_vector TEXT, "
                  "n_constraints INTEGER, all_pass_strict INTEGER, non_terminated INTEGER, ingested_is_correct INTEGER, PRIMARY KEY (question_id, model_name))")
        w.executemany("INSERT INTO math_checker_answers VALUES (?,?,?,?,?,?,?,?,?)", math_rows)
        w.executemany("INSERT INTO ifeval_checker_answers VALUES (?,?,?,?,?,?,?,?)", if_rows)
        w.executemany("INSERT INTO checker_answer_ingest_meta VALUES (?,?)", [
            ("script", "tools/analysis/checker_answer_ingest.py"), ("source_db", os.path.basename(DB)), ("union_pool", UNION_POOL),
            ("written_at", time.strftime("%Y-%m-%d %H:%M:%S")), ("math_tier", "1 boxed, 2 'final answer is', 3 last-number fallback, 0 none (MATH-FIX order)"),
            ("math_checker", "math_fix.extract/normalise/equal (committed)"),
            ("ifeval_vector", "leaderboard inst_level_strict_acc from experiment_results/multicorpus/raw/<model>/*/samples_leaderboard_ifeval_*.jsonl"),
            ("non_terminated", "1 if the response opens <think> and never closes it (truncation detectable from text)")])
        w.commit(); w.close()
        P(); P("wrote %s: math_checker_answers %d rows, ifeval_checker_answers %d rows (multicorpus_cache_v1.db untouched)" % (NEW_DB, len(math_rows), len(if_rows)))

    # --- verdicts -------------------------------------------------------------------------------------------------
    P(); P("=" * 110); P("CRITERIA (item 7 wording; reading B is the verdict of record; the other readings printed beside)"); P("=" * 110)
    def dmin(label):
        c = min((c for c in cells if c != "MATH (source row)"), key=lambda c: dc_res[(label, c)][0]); return c, dc_res[(label, c)]
    def one_dc(v, ci):
        """point verdict against the bar, with the interval read beside it (…-AT-POINT when the interval crosses the bar)."""
        if v >= DC_BAR: return "PASS" if ci[0] >= DC_BAR else "PASS-AT-POINT (95% interval crosses 0.95)"
        return "FAIL" if ci[1] < DC_BAR else "FAIL-AT-POINT (95% interval crosses 0.95)"
    def verdict_dc(label):
        src = dc_res[(label, "MATH (source row)")]; cname, mn = dmin(label)
        v = "PASS" if (src[0] >= DC_BAR and mn[0] >= DC_BAR) else "FAIL"
        return v, src, cname, mn, one_dc(src[0], src[1]), one_dc(mn[0], mn[1])
    for label in (LB, LA, LC):
        v, src, cname, mn, v_src, v_mn = verdict_dc(label)
        P("(1) D_c >= 0.95 on MATH, %s:" % label)
        P("      source row (the item's literal cell) %s -> %s" % (fmt_ci(src[0], src[1]), v_src))
        P("      min domain cell (hardest) %s at %s -> %s;  criterion over both cells at the point -> %s" % (fmt_ci(mn[0], mn[1]), cname, v_mn, v))
    vB = verdict_dc(LB)[0]; vA = verdict_dc(LA)[0]; vC = verdict_dc(LC)[0]
    P("    VERDICT OF RECORD (reading B): %s   | beside: A %s, C %s" % (vB, vA, vC))
    P("    what B measures: the two R1 distills are NON_TERMINATED on %d/%d and %d/%d of the eval-side questions; under the record's own"
      % (sum(1 for r in math_rows if r[1] == "DeepSeek-R1-Distill-Llama-8B" and r[6] and r[0] in pool), len(eval_q["MATH"]),
         sum(1 for r in math_rows if r[1] == "DeepSeek-R1-Distill-Qwen-32B" and r[6] and r[0] in pool), len(eval_q["MATH"])))
    P("    rule their fallback numbers are not answers, and every pair containing one of them is UNDETERMINED. Without the two, reading A/B gives")
    st, _ = pair_stats(eval_q["MATH"], X_B, [m for m in models if not m.startswith("DeepSeek-R1")], str_eq); v16, ci16 = boot_share(st[:, 0], st[:, 4])
    P("    D_c %s on 16 models / 120 pairs: the shortfall is a roster property (two truncated contestants), not a checker property." % fmt_ci(v16, ci16))

    oB = off_res[(LB, "string rule, normalised form [hardest]")]; oA = off_res[(LA, "string rule, normalised form [hardest]")]
    oAc = off_res[(LA, "string rule, canonical numeric form")]; oC = off_res[(LC, "string rule, normalised form [hardest]")]; oCc = off_res[(LC, "string rule, canonical numeric form")]
    def v_off(o): return "PASS" if o[1][1] < OFFER_BAR else ("FAIL" if o[1][0] >= OFFER_BAR else "UNDETERMINED (interval crosses the bar)")
    P("(2) share of MATH question-pairs offered < 50%%: reading B / normalised string %s  -> %s" % (fmt_ci(oB[0], oB[1]), v_off(oB)))
    P("      beside: A / normalised %s -> %s; A / canonical %s -> %s; C / normalised %s -> %s; C / canonical %s -> %s"
      % (fmt_ci(oA[0], oA[1]), v_off(oA), fmt_ci(oAc[0], oAc[1]), v_off(oAc), fmt_ci(oC[0], oC[1]), v_off(oC), fmt_ci(oCc[0], oCc[1]), v_off(oCc)))
    P("      the lowest reading of 'offered' the filter admits is DISAGREE alone (dropping UNDETERMINED, which keep() does not do): A %.4f, B %.4f, C %.4f"
      % (oA[2], oB[2], oC[2]))
    c2 = v_off(oB) == "PASS"
    math_passes = (vB == "PASS") and c2
    P("(P) prediction 'MATH passes' [(1) and (2) both]: reading B -> %s (A -> %s: (2) fails under every reading)"
      % ("HELD" if math_passes else "NOT HELD", "HELD" if (vA == "PASS" and v_off(oA) == "PASS") else "NOT HELD"))
    if_b = "NOT HELD" if cib[0] >= DC_BAR else ("HELD" if cib[1] < DC_BAR else "UNDETERMINED (interval crosses 0.95)")
    if_a = "NOT HELD" if cia[0] >= DC_BAR else ("HELD" if cia[1] < DC_BAR else "UNDETERMINED (interval crosses 0.95)")
    P("(P) prediction 'IFEval stays below 0.95': reading B D_c %s -> %s; reading A %s -> %s" % (fmt_ci(dcb, cib), if_b, fmt_ci(dca, cia), if_a))
    P("      the checker's vector exists for every response (an empty or truncated response is an all-fail vector), so under reading A")
    P("      IFEval D_c = 1 by construction; the prediction could only hold if 'extracted' excluded such rows, and even the NON_TERMINATED")
    P("      rule (reading B) removes %d of 2,916 eval-side rows. No harder text-detectable blank rule exists: the corpus holds %d empty or" % (trunc_if, empty_if))
    P("      whitespace-only IFEval responses (counted over all %d backfilled rows)." % len(if_rows))
    P("(P) 'IFEval PREDICTIVE-ONLY' by the D_c rule: %s (D_c under B %.4f %s 0.95); routing precision per source is outside this item and can still class it"
      % ("NO" if dcb >= DC_BAR else "YES", dcb, ">=" if dcb >= DC_BAR else "<"))
    P("    MATH class by the D_c rule under reading B: %s; under reading A: %s"
      % ("PREDICTIVE-ONLY (D_c < 0.95 in the source row and in every domain cell)" if vB == "FAIL" else "edge pass admissible",
         "PREDICTIVE-ONLY" if vA == "FAIL" else "edge pass admissible (source row and all 7 domain cells >= 0.95 at the point)"))
    P("McNemar: no wrong-direction counts arise in this test (nothing is judged); the established-count rule has no object here.")
    P("elapsed %.0f s" % (time.time() - t0))
    with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
    print("-> " + OUT)


# ----------------------------------------------------------------------------------------------------------------
# --v2: the consistent cap proxy (STAGE3-MATH re-registration prerequisite)
# ----------------------------------------------------------------------------------------------------------------

def abrupt_end(resp):
    """The checker's rule: the last non-whitespace character is not a sentence / expression terminator; an empty or
    whitespace-only response is abrupt."""
    r = (resp or "").rstrip()
    return True if not r else (r[-1] not in ENDS)


def read_harness_cap(models):
    """max_gen_toks from the first row of every raw MATH sample file on disk (lm-eval stores it in
    arguments.gen_args_0.arg_1). Returns the one cap all files agree on; refuses if they disagree or a file is missing."""
    caps = collections.Counter(); n_files = 0
    for m in models:
        fs = sorted(glob.glob(os.path.join(RAW, m, "*", "samples_leaderboard_math_*_hard_*.jsonl")))
        if len(fs) != 7: raise SystemExit("[RAW] expected 7 MATH sample files for %s, found %d" % (m, len(fs)))
        for f in fs:
            with open(f, encoding="utf-8") as fh:
                r = json.loads(fh.readline())
            gk = None; args = r.get("arguments")
            if isinstance(args, dict):
                for v in args.values():
                    if isinstance(v, dict) and isinstance(v.get("arg_1"), dict): gk = v["arg_1"]
            elif isinstance(args, list) and args and isinstance(args[0], list) and len(args[0]) > 1: gk = args[0][1]
            if not isinstance(gk, dict) or "max_gen_toks" not in gk: raise SystemExit("[RAW] no max_gen_toks in %s" % f)
            caps[int(gk["max_gen_toks"])] += 1; n_files += 1
    if len(caps) != 1: raise SystemExit("[RAW] max_gen_toks is not uniform across the raw MATH files: %s" % dict(caps))
    return next(iter(caps)), n_files


def load_cl100k():
    """tiktoken cl100k_base from the local cache only; requests.get is a raiser for the load, so a missing file ends
    in a refusal, never a download."""
    import tempfile, tiktoken, requests
    cache_dir = os.environ.get("TIKTOKEN_CACHE_DIR") or os.environ.get("DATA_GYM_CACHE_DIR") or os.path.join(tempfile.gettempdir(), "data-gym-cache")
    cache_file = os.path.join(cache_dir, hashlib.sha1(CL100K_URL.encode()).hexdigest())
    if not os.path.exists(cache_file): raise SystemExit("[TOKENIZER] no cached cl100k_base rank file at %s; no download attempted; refusing" % cache_file)
    _get = requests.get
    def _raiser(*a, **k): raise RuntimeError("network disabled in checker_answer_ingest --v2")
    requests.get = _raiser
    try: enc = tiktoken.get_encoding("cl100k_base")
    finally: requests.get = _get
    return enc, cache_file


V2_COLS = ("question_id", "model_name", "answer_norm", "answer_canon", "tier", "is_correct", "non_terminated_think",
           "cl100k_tokens", "last_char", "abrupt_end", "cap_hit", "non_terminated")


def main_v2():
    t0 = time.time(); L = []
    def P(s=""): print(s); L.append(s)
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    pool_guard.assert_pool_of_record(UNION_POOL)
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    P("CHECKER-ANSWER-INGEST --v2: the CONSISTENT cap proxy (STAGE3-MATH re-registration prerequisite; 0 LLM calls, 0 network)")
    P("producing code hash: sha256 %s  (%s)" % (hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
                                               os.path.relpath(os.path.abspath(__file__), ROOT).replace(os.sep, "/")))
    P("[POOL-GUARD] mmlu_pro dataset DB pool of record %s verified by id" % pool_guard.MMLU_PRO_POOL)
    P("[POOL-PIN]   multicorpus DB union pool %s verified by id; this script addresses it BY EXPLICIT ID" % UNION_POOL)

    # --- v1: read, verify the cited hash, never write ------------------------------------------------------------
    if not os.path.exists(NEW_DB): raise SystemExit("[V1] %s is absent; --v2 extends it and refuses to run without it" % NEW_DB)
    v1_sha = hashlib.sha256(open(NEW_DB, "rb").read()).hexdigest()
    if v1_sha != V1_SHA256: raise SystemExit("[V1] %s sha256 %s != the cited %s; refusing (the v2 table is defined as v1 + cap columns)" % (NEW_DB, v1_sha, V1_SHA256))
    v1 = sqlite3.connect("file:%s?mode=ro" % NEW_DB, uri=True)
    v1_meta = dict(v1.execute("SELECT key, value FROM checker_answer_ingest_meta"))
    v1_rows = {(q, m): (xn, xc, int(t), int(nt), int(k)) for q, m, xn, xc, t, nt, k in
               v1.execute("SELECT question_id, model_name, x_norm, x_canon, tier, non_terminated, checker_correct FROM math_checker_answers")}
    v1.close()
    P("[V1] %s read-only: sha256 %s == cited; math_checker_answers %d rows (written %s); v1.non_terminated = %s"
      % (os.path.basename(NEW_DB), v1_sha[:8], len(v1_rows), v1_meta.get("written_at"), v1_meta.get("non_terminated")))

    # --- corpus, pool, models ---------------------------------------------------------------------------------------
    Q = {qid: dict(domain=dom, target=target) for qid, dom, target in con.execute("SELECT question_id, domain, target FROM corpus_questions WHERE source='MATH'")}
    pool = {qid: dom for qid, dom in con.execute("SELECT question_id, domain FROM reserved_pool WHERE pool_id = ?", (UNION_POOL,)) if qid in Q}
    eval_q = sorted(pool)
    outputs = {(q, m): (o or "") for q, m, o in con.execute("SELECT e.question_id, e.model_name, e.model_output FROM eval_results e JOIN corpus_questions c USING(question_id) WHERE c.source='MATH'") if m not in EXCLUDE}
    models = sorted({m for (_, m) in outputs}); n_pairs = len(models) * (len(models) - 1) // 2
    miss = [qm for qm in outputs if qm not in v1_rows]
    if miss or len(outputs) != len(v1_rows): raise SystemExit("[V1] row set differs from eval_results: %d missing, %d vs %d" % (len(miss), len(outputs), len(v1_rows)))
    P("corpus: MATH %d questions (eval-side in %s: %d) | models %d -> %d unordered pairs | rows %d" % (len(Q), UNION_POOL, len(eval_q), len(models), n_pairs, len(outputs)))
    P("KEY DENOMINATOR: eval-side question-pairs = %d x %d = %d; eval-side rows = %d x %d = %d" % (len(eval_q), n_pairs, len(eval_q) * n_pairs, len(eval_q), len(models), len(eval_q) * len(models)))

    # --- the rule ---------------------------------------------------------------------------------------------------
    cap, n_files = read_harness_cap(models)
    thr = cap - CAP_SLACK
    enc, cache_file = load_cl100k()
    P(); P("=" * 110); P("THE CONSISTENT NON_TERMINATED PROXY (the checker's rule, applied to every model)"); P("=" * 110)
    P("  cap       = max_gen_toks %d, read from the first row of all %d raw MATH sample files (%d models x 7 subjects), uniform" % (cap, n_files, len(models)))
    P("  tokens    = cl100k_base count of the stored model_output (tiktoken from local cache %s, network client disabled)" % cache_file)
    P("  abrupt    = last non-whitespace character of the response NOT in %s; an empty / whitespace-only response is abrupt" % (ENDS,))
    P("  cap_hit   = tokens >= cap - %d = %d  AND  abrupt" % (CAP_SLACK, thr))
    P("  think     = v1's proxy: the response opens <think> and never closes it")
    P("  non_terminated = think OR cap_hit   (reading B with the consistent proxy: such a response has NO extracted answer)")

    # --- per-row computation ----------------------------------------------------------------------------------------
    keys = sorted(outputs); texts = [outputs[k] for k in keys]
    ntoks = [len(t) for t in enc.encode_ordinary_batch(texts)]
    rows = []; X_B2 = {}; X_B1 = {}; G = {}
    per_m = collections.defaultdict(lambda: collections.Counter())
    for (q, m), resp, nt_tok in zip(keys, texts, ntoks):
        xn, xc, tier, nt_think, k = v1_rows[(q, m)]
        assert nt_think == int(non_terminated(resp)), "v1.non_terminated must equal the <think> rule on the stored text"
        r = resp.rstrip(); last = r[-1] if r else ""
        ab = int(abrupt_end(resp)); ch = int(nt_tok >= thr and ab); nt = int(nt_think or ch)
        rows.append((q, m, xn, xc, tier, k, nt_think, nt_tok, last, ab, ch, nt))
        G.setdefault(q, {})[m] = k
        c = per_m[m]; c["rows"] += 1; c["cap"] += ch; c["think"] += nt_think; c["nt"] += nt; c["ge_thr"] += int(nt_tok >= thr)
        if q in pool:
            c["rows_e"] += 1; c["cap_e"] += ch; c["think_e"] += nt_think; c["nt_e"] += nt
        if xn is not None:
            if not nt_think: X_B1.setdefault(q, {})[m] = xn
            if not nt: X_B2.setdefault(q, {})[m] = xn
    P(); P("per-model rates (eval-side = the %d pool questions; all = the %d corpus questions):" % (len(eval_q), len(Q)))
    P("  %-30s %9s %9s %9s %9s | %9s %9s %9s" % ("model", "cap_hit_e", "think_e", "nt_e", "rate_e", "cap_hit", ">=%d tok" % thr, "rate_all"))
    for m in sorted(models, key=lambda m: -per_m[m]["cap_e"]):
        c = per_m[m]
        P("  %-30s %9d %9d %9d %9.3f | %9d %9d %9.3f" % (m, c["cap_e"], c["think_e"], c["nt_e"], c["nt_e"] / c["rows_e"], c["cap"], c["ge_thr"], c["nt"] / c["rows"]))
    tot_e = sum(per_m[m]["nt_e"] for m in models); tot_ce = sum(per_m[m]["cap_e"] for m in models); tot_te = sum(per_m[m]["think_e"] for m in models)
    P("  eval-side rows NON_TERMINATED under the consistent proxy: %d of %d (cap_hit %d, unclosed <think> %d, both %d); v1's proxy alone: %d  [checker: 1,320 vs the builder's 600]"
      % (tot_e, len(eval_q) * len(models), tot_ce, tot_te, tot_ce + tot_te - tot_e, tot_te))

    # --- D_c under reading B with the consistent proxy ---------------------------------------------------------------
    str_eq = lambda a, b: a.strip().lower() == b.strip().lower()
    cells = collections.OrderedDict(); cells["MATH (source row)"] = eval_q
    for d in sorted(set(pool.values())): cells[d] = [q for q in eval_q if pool[q] == d]
    def dc_cell(qs, X, ms):
        st, _ = pair_stats(qs, X, ms, str_eq); v, ci = boot_share(st[:, 0], st[:, 4]); o, oci = boot_share(st[:, 4] - st[:, 1], st[:, 4]); return v, ci, o, oci
    P(); P("=" * 110); P("D_c under reading B with the CONSISTENT proxy (share of eval-side question-pairs with two non-blank extracted answers; question-bootstrap 95%% CI, B=%d, seed %d)" % (B_BOOT, SEED)); P("=" * 110)
    P("  %-32s %6s %-26s %-26s" % ("cell (18 models, 153 pairs)", "q", "D_c [95% CI]", "offered (not AGREE) [95% CI]"))
    res18 = {}
    for cname, qs in cells.items():
        v, ci, o, oci = dc_cell(qs, X_B2, models); res18[cname] = (v, ci)
        P("  %-32s %6d %-26s %-26s" % (cname, len(qs), fmt_ci(v, ci), fmt_ci(o, oci)))
    mn18 = min((c for c in cells if c != "MATH (source row)"), key=lambda c: res18[c][0])
    P("  18-model source row %s | min domain cell %s at %s   [checker: 0.6701 [0.6501, 0.6890]]" % (fmt_ci(*res18["MATH (source row)"]), fmt_ci(*res18[mn18]), mn18))
    m16 = [m for m in models if not m.startswith("DeepSeek-R1")]
    v, ci, o, oci = dc_cell(eval_q, X_B2, m16)
    P("  16 models without the R1 distills (%d pairs): D_c %s   [checker: 0.8167 [0.7952, 0.8380]]" % (len(m16) * (len(m16) - 1) // 2, fmt_ci(v, ci)))
    v1b, ci1b, _, _ = dc_cell(eval_q, X_B1, models)
    P("  beside, v1's <think>-only proxy (item 7's reading B of record): 18-model source row %s   [item 7: 0.8268 [0.8184, 0.8350]]" % fmt_ci(v1b, ci1b))
    dec = decidability(eval_q, X_B2, G, models, str_eq)
    tot_dec = sum(dec[k][0] for k in dec); kept_dec = dec["DISAGREE"][0] + dec["UNDETERMINED"][0]
    P("  key-decidable share by filter verdict (consistent proxy): " + "; ".join("%s %d pairs, decidable %d (%.4f)" % (k, dec[k][1], dec[k][0], dec[k][0] / max(1, dec[k][1])) for k in ("DISAGREE", "UNDETERMINED", "AGREE"))
      + "; decidable pairs kept %d of %d (%.4f)" % (kept_dec, tot_dec, kept_dec / max(1, tot_dec)))
    P("  sensitivity of the 18-model source row to the rule:")
    for lab, t_, need_ab in (("tokens >= %d AND abrupt (the rule)" % thr, thr, True), ("tokens >= %d AND abrupt" % (cap - 24), cap - 24, True),
                             ("tokens >= %d, abrupt not required" % thr, thr, False), ("tokens >= %d, abrupt not required" % (cap - 14), cap - 14, False)):
        X2 = {}
        for (q, m, xn, xc, tier, k, nt_think, nt_tok, last, ab, ch, nt) in rows:
            if xn is None: continue
            if nt_think or (nt_tok >= t_ and (ab or not need_ab)): continue
            X2.setdefault(q, {})[m] = xn
        v, ci, _, _ = dc_cell(eval_q, X2, models); v16 = dc_cell(eval_q, X2, m16)[0]
        P("    %-42s 18 models D_c %s; 16 models %.4f" % (lab, fmt_ci(v, ci), v16))

    # --- the 8-model GEN-ARENA roster: STAGE3-MATH's cell (this pool) and the checker's object (GEN-ARENA's schedule) ---
    P(); P("=" * 110); P("8-model GEN-ARENA roster under reading B with the consistent proxy"); P("=" * 110)
    try:
        g = sqlite3.connect("file:%s?mode=ro" % GEN_ARENA, uri=True)
        gq = set(); roster = set()
        for q, a, b in g.execute("SELECT qid, model_a, model_b FROM schedule WHERE source='MATH'"): gq.add(q); roster.update((a, b))
        roster = sorted(roster - EXCLUDE); gq = sorted(gq)
        judged = [(q, a, b) for q, a, b in g.execute("SELECT qid, model_a, model_b FROM verdicts WHERE source='MATH' AND invalid=0")]
        g.close()
    except Exception as e:
        raise SystemExit("[GEN-ARENA] cache not readable: %r" % (e,))
    n_rp = len(roster) * (len(roster) - 1) // 2
    P("  roster (%d models, %d pairs): %s" % (len(roster), n_rp, ", ".join(roster)))
    P("  (a) STAGE3-MATH's cell: the union pool's %d MATH questions (item 7's cell rule = source row AND min domain cell):" % len(eval_q))
    res8 = {}
    for cname, qs in cells.items():
        v, ci, o, oci = dc_cell(qs, X_B2, roster); res8[cname] = (v, ci)
        P("      %-30s q=%3d D_c %-26s offered %-26s" % (cname, len(qs), fmt_ci(v, ci), fmt_ci(o, oci)))
    mn8 = min((c for c in cells if c != "MATH (source row)"), key=lambda c: res8[c][0])
    row8 = res8["MATH (source row)"]
    P("      source row %s | min domain cell %s at %s -> item 7 rule (>= 0.95 on the row AND the min cell): %s"
      % (fmt_ci(*row8), fmt_ci(*res8[mn8]), mn8, "MET" if min(row8[0], res8[mn8][0]) >= DC_BAR else "NOT MET"))
    cap8 = sum(1 for r_ in rows if r_[0] in pool and r_[1] in roster and r_[11])
    P("      roster rows on the pool NON_TERMINATED under the consistent proxy: %d of %d" % (cap8, len(eval_q) * len(roster)))
    v, ci, o, oci = dc_cell(eval_q, X_B1, roster)
    P("      beside, v1's <think>-only proxy on the same cell: D_c %s (STAGE3-MATH's held dry-run printed 0.994)" % fmt_ci(v, ci))
    P("  (b) the checker's object: GEN-ARENA's own %d scheduled MATH questions (random.Random(42) re-derived split; %d in the union pool):" % (len(gq), len(set(gq) & set(pool))))
    v, ci, o, oci = dc_cell(gq, X_B2, roster)
    gqs = set(gq)
    capg = sum(1 for r_ in rows if r_[0] in gqs and r_[1] in roster and r_[11])
    P("      D_c %s offered %s | scheduled rows at the cap %d of %d   [checker: 0.8189 [0.7935, 0.8433], 321 of 3,152]" % (fmt_ci(v, ci), fmt_ci(o, oci), capg, len(gq) * len(roster)))
    NT = {(r_[0], r_[1]): r_[11] for r_ in rows}
    n_cap_match = sum(1 for q, a, b in judged if NT.get((q, a)) or NT.get((q, b)))
    n_und_match = sum(1 for q, a, b in judged if X_B2.get(q, {}).get(a) is None or X_B2.get(q, {}).get(b) is None)
    P("      judged MATH matches in the GEN-ARENA cache involving a NON_TERMINATED response: %d of %d; UNDETERMINED under the consistent proxy (either side blank, cap-hit OR no extractable answer): %d   [checker's 367 of 1,800 is the UNDETERMINED count]"
      % (n_cap_match, len(judged), n_und_match))
    v, ci, _, _ = dc_cell(gq, X_B1, roster)
    P("      beside, v1's proxy on the same questions: D_c %s   [item 7: 0.9898]" % fmt_ci(v, ci))

    # --- write / verify the v2 DB ------------------------------------------------------------------------------------
    meta_rows = [("script", "tools/analysis/checker_answer_ingest.py --v2"), ("source_db", os.path.basename(DB)), ("union_pool", UNION_POOL),
                 ("v1_db", os.path.basename(NEW_DB)), ("v1_sha256", v1_sha), ("harness_cap", str(cap)), ("cap_slack", str(CAP_SLACK)), ("cap_threshold", str(thr)),
                 ("tokenizer", "cl100k_base (tiktoken, local cache, network disabled)"), ("ends", json.dumps(list(ENDS))),
                 ("abrupt_end", "1 if the last non-whitespace character is not in ends, or the response is empty / whitespace-only"),
                 ("cap_hit", "1 if cl100k_tokens >= cap_threshold AND abrupt_end"),
                 ("non_terminated_think", "v1's proxy: opens <think> and never closes it"),
                 ("non_terminated", "non_terminated_think OR cap_hit (the consistent proxy)"),
                 ("answer_norm", "= v1.x_norm (MATH-FIX normalised); answer_canon = v1.x_canon; tier = v1.tier; is_correct = v1.checker_correct")]
    if os.path.exists(NEW_DB_V2):
        chk = sqlite3.connect("file:%s?mode=ro" % NEW_DB_V2, uri=True)
        own = chk.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checker_answer_ingest_v2_meta'").fetchone()
        if not own: chk.close(); raise SystemExit("[REFUSE] %s exists and was not written by this script; will not overwrite" % NEW_DB_V2)
        old = sorted(tuple(r_) for r_ in chk.execute("SELECT %s FROM math_checker_answers_v2" % ", ".join(V2_COLS)))
        written_at = dict(chk.execute("SELECT key, value FROM checker_answer_ingest_v2_meta")).get("written_at"); chk.close()
        new = sorted(tuple(r_) for r_ in rows)
        d = sum(1 for a, b in zip(old, new) if a != b) + abs(len(old) - len(new))
        P(); P("%s already exists (written %s by this script): VERIFIED against the fresh computation: rows differing %d of %d; file left untouched" % (NEW_DB_V2, written_at, d, len(rows)))
        if d:
            P("[MISMATCH] the existing v2 DB does not reproduce the fresh computation; NOT overwritten; exiting non-zero")
            with open(OUT_V2, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
            raise SystemExit(2)
    else:
        w = sqlite3.connect(NEW_DB_V2)
        w.execute("CREATE TABLE checker_answer_ingest_v2_meta (key TEXT PRIMARY KEY, value TEXT)")
        w.execute("CREATE TABLE math_checker_answers_v2 (question_id INTEGER, model_name TEXT, answer_norm TEXT, answer_canon TEXT, tier INTEGER, "
                  "is_correct INTEGER, non_terminated_think INTEGER, cl100k_tokens INTEGER, last_char TEXT, abrupt_end INTEGER, cap_hit INTEGER, "
                  "non_terminated INTEGER, PRIMARY KEY (question_id, model_name))")
        w.executemany("INSERT INTO math_checker_answers_v2 VALUES (%s)" % ",".join("?" * len(V2_COLS)), rows)
        w.executemany("INSERT INTO checker_answer_ingest_v2_meta VALUES (?,?)", meta_rows + [("written_at", time.strftime("%Y-%m-%d %H:%M:%S")),
                      ("producing_code_sha256", hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest())])
        w.commit(); w.close()
        P(); P("wrote %s: math_checker_answers_v2 %d rows (%s and %s untouched)" % (NEW_DB_V2, len(rows), os.path.basename(NEW_DB), os.path.basename(DB)))
    P("v2 DB sha256 %s" % hashlib.sha256(open(NEW_DB_V2, "rb").read()).hexdigest())
    v1_after = hashlib.sha256(open(NEW_DB, "rb").read()).hexdigest()
    P("v1 DB sha256 after this run %s (%s)" % (v1_after[:8], "unchanged" if v1_after == V1_SHA256 else "CHANGED"))
    P("elapsed %.0f s" % (time.time() - t0))
    with open(OUT_V2, "w", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
    print("-> " + OUT_V2)


if __name__ == "__main__":
    if sys.argv[1:] == ["--v2"]:
        main_v2()
    elif sys.argv[1:]:
        raise SystemExit("usage: checker_answer_ingest.py [--v2]")
    else:
        main()
