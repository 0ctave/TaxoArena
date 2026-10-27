"""REF-CHECKLIST, generation half (docs/judge_v2_program.md, "Registered 2026-09-17 ... REF-CHECKLIST"; registered
before any code or call). One reasoning call per question of the 944 key-decidable R3 matches produces a
VERIFICATION CHECKLIST: the facts and reasoning steps a correct answer MUST contain and the pitfalls a wrong answer
typically shows, as JSON {"required": [...], "pitfalls": [...]} - WITHOUT the answer, any option letter or any
option text. ref_checklist.py then renders it into the judge's question block in place of (or beside) the answer
reference.

  python tools/analysis/checklist_gen.py --dry-run [--pilot N]     (0 calls: assemble every payload, print the first)
  python tools/analysis/checklist_gen.py --run [--pilot N] [--workers 8]
  python tools/analysis/checklist_gen.py --audit                    (0 calls: (re)apply the leakage audit, print counts)

HYGIENE (registration): the checklist is derived from the judged question ALONE, at judgment time, by the reference's
own model (grok-4-1-fast-reasoning, rejudge_reasoning PROVIDER azure), exactly as the reference solve is: the user
prompt is judge_solve_map.user_prompt (stem + lettered options, byte-identical to the S1 solve's), the system prompt is
GEN_SYSTEM below. Nothing is induced over the reserved split; no train-side material enters. Cap 8192, temperature
OMITTED (D2), finish_reason recorded per call.

LEAKAGE AUDIT, applied to every parsed checklist (all items of both lists joined) before use; a failing checklist is
marked dropped=1 with the reason and is NEVER edited (the text stays in the cache as evidence):
 (i)  LETTER RULE - a standalone option letter A-J used as an answer statement. Letters are uppercase only (a
      generated checklist capitalises normally; a lowercase "option a company can take" is prose). The patterns:
        "answer|choice|option|alternative|solution|result" + "is|would be|should be|must be|:|=" + "(X)" or "X"
        "option|choice|answer|alternative|letter" + "(X)" or "X"          e.g. "option D", "choice (B)"
        "select|pick|choose" + "(X)" or "X"
        "X is (the) correct|right|best|wrong|incorrect"
        a bare "(X)" NOT preceded by a word character (so "P(A)", "f(B)", "log(C)" in a formula do not fire,
        while an enumeration "(A)" does)
      The rule errs towards dropping: a formula-free "(A)" that is not an answer statement is still dropped.
 (ii) N-GRAM RULE (TaxonomyJudgeService.maxSharedNgram / auditRubricLeakage, the rubric-induction rule): tokens are
      lowercase, every non [a-z0-9 whitespace] character becomes a space; the LONGEST word n-gram (cap 12) shared
      between the checklist text and the CORRECT option's text is found; the checklist is flagged when that n-gram
      is >= 4 words long AND does not also occur in the question stem or in any distractor (an n-gram present in
      the stem is part of the problem statement; one present in an incorrect option is not answer-specific; either
      is vocabulary, not a leaked key). Kotlin's advisory threshold is 5; the registration makes the audit a gate
      and this script uses 4, stricter. As in Kotlin only the LONGEST shared n-gram is judged; --audit additionally
      prints, as an advisory that drops nothing, the count of checklists holding ANY maximal shared n-gram >= 4
      words unique to the correct option.
 (iii) SHORT-OPTION / NUMERAL RULE (added at the adversarial check of 2026-09-17, before any call): 363 of the 782
      correct options are SHORTER than NGRAM_MIN tokens ("600", "0.373 atm", "Procurement"), so rule (ii) can never
      fire on them and a checklist that states the answer verbatim would pass. The checklist is therefore also
      flagged when (a) the correct option has fewer than NGRAM_MIN tokens and the WHOLE normalised option occurs in
      the checklist as a contiguous token sequence, or (b) any numeral (\\d+(\\.\\d+)?, thousands commas removed) of
      the checklist occurs in the correct option; in both cases only if that sequence / numeral occurs in neither
      the stem nor any distractor (token-boundary match, so "0.5" does not excuse "5"). Errs towards dropping.

GUARD: finish_reason and the parse outcome are recorded per question; the first PILOT_BLOCK questions of a --run are
posted first and read by the guard before the rest; a checklist set with more than 5% unparsed questions (empty
content, finish_reason=length, malformed JSON) is not usable for a verdict-bearing run - --audit says so and
ref_checklist.py refuses to launch on it.

CACHE: experiment_results/judge_solve/checklist_grok-reasoning.db, table checklists (question_id PRIMARY KEY, raw,
parsed_json, finish_reason, completion_tokens, response_id, created, provider, ts, dropped, drop_reason, audit_n,
audit_gram); meta (judge, cap, temperature, protocol, system-prompt sha, script sha pinned once at first launch).
'created' is the receipt wall-clock (rejudge_reasoning.call_judge_full does not expose the provider's created field;
the response id is taken from msg["_response_id"]). Resumable by question_id.
"""
import os, sys, re, json, time, hashlib, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import judge_solve_map as jsm
import pair_noref as pn

POOL = pool_guard.MMLU_PRO_POOL
GEN_MODEL = "grok-4-1-fast-reasoning"      # the reference's own model (judge_solve_map JUDGES["grok-reasoning"])
MAXTOK = 8192
PILOT_BLOCK = 12
NGRAM_MIN = 4                              # the registered gate; Kotlin's advisory threshold is 5
NGRAM_CAP = 12                             # TaxonomyJudgeService.maxSharedNgram cap
LETTERS = "ABCDEFGHIJ"
CACHE = os.path.join(ROOT, "experiment_results", "judge_solve", "checklist_grok-reasoning.db")
PROTOCOL = ("checklist JSON: {\"required\": [...], \"pitfalls\": [...]} from stem + lettered options (judge_solve_map.user_prompt), "
            "no answer / letter / option text; leakage audit (letter rule + %d-word n-gram rule vs the correct option + whole short option / numeral rule, "
            "stem and distractors excused)" % NGRAM_MIN)
TEMPERATURE_DECISION = "omitted from the payload (provider default): docs/plan_2026-09-15.md Amendment 1, D2"

GEN_SYSTEM = """You are preparing a VERIFICATION CHECKLIST for graders who will compare two written answers to an expert-level multiple-choice question. The graders see the question stem and your checklist; they do NOT see the options.

Return ONLY a JSON object of the form {"required": [...], "pitfalls": [...]}.
- "required": the facts, definitions, formulas, computations and reasoning steps that any CORRECT answer MUST contain or rely on. One short, checkable statement per item.
- "pitfalls": the misreadings, omissions, confusions and errors a WRONG answer typically shows. One short statement per item.
Use 3 to 8 items per list, each at most 25 words.

STRICT RULES (a checklist that breaks any of them is discarded unread):
1. Do NOT state which option is correct and do NOT state the final answer, value, result or conclusion.
2. Do NOT mention any option letter (A, B, C, ... J) in any form.
3. Do NOT quote, copy or closely paraphrase the text of any option.
4. Describe what a correct answer must establish and how it must be established, never which choice it arrives at.
Output the JSON object and nothing else."""


def script_sha():
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def system_sha():
    return hashlib.sha256(GEN_SYSTEM.encode("utf-8")).hexdigest()


# ── the question set: the distinct questions of the 944 key-decidable R3 matches, exactly as pair_noref derives them ──
def question_ids():
    sched, K = pn.targets()
    assert len(sched) == 944, "expected the 944 key-decidable R3 matches, found %d" % len(sched)
    return sorted({t[1] for t in sched}), sched


def question_rows(qids):
    """qid -> (stem, options, key letter): a campaign model's row (its text/options are verified against the HF rows)."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    out = {}
    for q in qids:
        assert q in pool, "question %s is outside the pool of record %s" % (q, POOL)
        r = ev.execute("SELECT question_text, options_json, gt_answer FROM eval_results WHERE question_id=? AND model_name='gpt-4o-2024-08-06'", (q,)).fetchone()
        if r is None:
            r = ev.execute("SELECT question_text, options_json, gt_answer FROM eval_results WHERE question_id=? AND model_name!='Meta-Llama-3-70B-Instruct'", (q,)).fetchone()
        if r is None: continue
        opts = json.loads(r[1]) if r[1] else []
        out[q] = (r[0], opts, (r[2] or "").strip().upper()[:1])
    return out


# ── parsing ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def parse_checklist(text):
    """{"required": [str...], "pitfalls": [str...]} or None. Lenient on fences and surrounding prose, strict on shape."""
    t = rr.strip_think(text or "")
    if not t: return None
    if "```json" in t: t = t.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in t: t = t.split("```", 1)[1].split("```", 1)[0]
    a, b = t.find("{"), t.rfind("}")
    if a == -1 or b <= a: return None
    try: el = json.loads(t[a:b + 1], strict=False)
    except Exception: return None
    if not isinstance(el, dict): return None
    out = {}
    for k in ("required", "pitfalls"):
        v = el.get(k)
        if not isinstance(v, list) or not v or not all(isinstance(x, str) and x.strip() for x in v): return None
        out[k] = [x.strip() for x in v]
    return out


def checklist_text(parsed):
    return " | ".join(parsed["required"] + parsed["pitfalls"])


# ── the leakage audit ─────────────────────────────────────────────────────────────────────────────────────────────────
_L = "[A-J]"
LETTER_PATTERNS = [
    re.compile(r"\b(?:[Aa]nswer|[Cc]hoice|[Oo]ption|[Aa]lternative|[Ss]olution|[Rr]esult)\s*(?:(?:is|would be|should be|must be)\s*[:=]?|[:=])\s*\(?(%s)\)?(?![A-Za-z0-9])" % _L),
    re.compile(r"\b(?:[Oo]ption|[Cc]hoice|[Aa]nswer|[Aa]lternative|[Ll]etter)\s+\(?(%s)\)?(?![A-Za-z0-9])" % _L),
    re.compile(r"\b(?:[Ss]elect|[Pp]ick|[Cc]hoose)\s+\(?(%s)\)?(?![A-Za-z0-9])" % _L),
    re.compile(r"\b(%s)\s+is\s+(?:the\s+)?(?:correct|right|best|wrong|incorrect)\b" % _L),
    re.compile(r"(?<![A-Za-z0-9_])\((%s)\)" % _L),
]


def letter_hits(text):
    hits = []
    for p in LETTER_PATTERNS:
        for m in p.finditer(text): hits.append(m.group(0))
    return hits


def tokens(s):
    return [w for w in re.sub(r"[^a-z0-9\s]", " ", (s or "").lower()).split() if w]


def norm(s):
    return " ".join(tokens(s))


def max_shared_ngram(text, sources, cap=NGRAM_CAP):
    """Port of TaxonomyJudgeService.maxSharedNgram: (length, gram) of the longest word n-gram of text present in any source."""
    t = tokens(text)
    if not t: return 0, ""
    grams = defaultdict(set)
    for s in sources:
        st = tokens(s)
        for k in range(1, min(cap, len(st)) + 1):
            for i in range(len(st) - k + 1): grams[k].add(" ".join(st[i:i + k]))
    for k in range(min(cap, len(t)), 0, -1):
        src = grams.get(k)
        if not src: continue
        for i in range(len(t) - k + 1):
            g = " ".join(t[i:i + k])
            if g in src: return k, g
    return 0, ""


def unique_shared_ngrams(text, correct, stem, distractors, k_min=NGRAM_MIN, cap=NGRAM_CAP):
    """ADVISORY: every maximal shared n-gram (>= k_min words) with the correct option that is absent from the stem and
    every distractor. Stricter than the Kotlin rule (which judges the longest only); printed, never a drop reason."""
    t = tokens(text); c = tokens(correct)
    if not t or not c: return []
    cg = {" ".join(c[i:i + k]) for k in range(k_min, min(cap, len(c)) + 1) for i in range(len(c) - k + 1)}
    found = set()
    for k in range(min(cap, len(t)), k_min - 1, -1):
        for i in range(len(t) - k + 1):
            g = " ".join(t[i:i + k])
            if g in cg and not excused(g, stem, distractors) and not any(has_seq(g, f) for f in found): found.add(g)
    return sorted(found)


def has_seq(gram, normed):
    """Token-boundary containment of a normalised word sequence in a normalised text."""
    return (" %s " % gram) in (" %s " % normed)


def excused(gram, stem, distractors):
    """A sequence that also occurs in the stem or in a distractor is vocabulary, not a leaked key."""
    return has_seq(gram, norm(stem)) or any(has_seq(gram, norm(d)) for d in distractors)


NUMERAL = re.compile(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])")


def numerals(s):
    return set(NUMERAL.findall(re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s or "")))


def short_option_hit(text, correct, stem, distractors):
    """Rule (iii a): the WHOLE correct option, when shorter than NGRAM_MIN tokens, present as a token sequence."""
    c = norm(correct)
    if not c or len(c.split()) >= NGRAM_MIN: return ""
    return c if has_seq(c, norm(text)) and not excused(c, stem, distractors) else ""


def numeral_hit(text, correct, stem, distractors):
    """Rule (iii b): a numeral of the checklist that occurs in the correct option and in neither the stem nor a distractor."""
    shared = numerals(text) & numerals(correct)
    if not shared: return ""
    ex = set(numerals(stem))
    for d in distractors: ex |= numerals(d)
    hit = sorted(shared - ex, key=lambda v: (-len(v), v))
    return hit[0] if hit else ""


def audit_one(parsed, stem, opts, key):
    """(dropped, reason, n, gram). Rule (i) first, then rule (ii), then rule (iii)."""
    text = checklist_text(parsed)
    hits = letter_hits(text)
    if hits:
        return 1, "letter: %s" % "; ".join(sorted(set(hits))[:5]), 0, ""
    i = LETTERS.find(key)
    if not (0 <= i < len(opts)): return 0, "", 0, ""       # no key text to leak (never observed in the pool of record)
    correct = opts[i]; distractors = [o for j, o in enumerate(opts) if j != i]
    n, gram = max_shared_ngram(text, [correct])
    if n >= NGRAM_MIN and not excused(gram, stem, distractors):
        return 1, "ngram %d: \"%s\" (only in the correct option)" % (n, gram), n, gram
    s = short_option_hit(text, correct, stem, distractors)
    if s: return 1, "short-option: \"%s\" (the whole correct option, only there)" % s, n, gram
    v = numeral_hit(text, correct, stem, distractors)
    if v: return 1, "numeral: %s (only in the correct option)" % v, n, gram
    return 0, "", n, gram


DROP_RULES = ("letter", "ngram", "short-option", "numeral")


# ── cache ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def open_cache():
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS checklists (question_id INTEGER PRIMARY KEY, raw TEXT, parsed_json TEXT, finish_reason TEXT, "
                "completion_tokens INTEGER, response_id TEXT, created REAL, provider TEXT, ts REAL, "
                "dropped INTEGER DEFAULT 0, drop_reason TEXT DEFAULT '', audit_n INTEGER, audit_gram TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)")
    con.commit(); return con


def meta_of():
    return {"pool": POOL, "judge": GEN_MODEL, "provider": "azure", "max_tokens": str(MAXTOK), "temperature": "omitted (provider default)",
            "temperature_decision": TEMPERATURE_DECISION, "protocol": PROTOCOL, "system_sha256": system_sha(),
            "user_prompt": "judge_solve_map.user_prompt (the S1 reference solve's, byte-identical)", "ngram_min": str(NGRAM_MIN)}


def pin_meta(con):
    want = meta_of(); have = dict(con.execute("SELECT k, v FROM meta"))
    if have:
        diff = {k: (have.get(k), v) for k, v in want.items() if k in have and have[k] != v}
        if diff:
            raise SystemExit("[CACHE] %s was generated under different parameters; refusing to resume into it: %s\n"
                             "        A new prompt, cap or model is a NEW generation and gets a new cache: move %s aside and relaunch."
                             % (os.path.basename(CACHE), "; ".join("%s cached=%r now=%r" % (k, a, b) for k, (a, b) in diff.items()), CACHE))
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    for k, v in want.items(): con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (k, v))
    con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", ("script_sha256", script_sha()))
    con.execute("INSERT OR IGNORE INTO meta VALUES (?,?)", ("started", ts))
    if have:
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("script_sha256_relaunch_" + ts, script_sha()))
        con.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", ("resumed", (have.get("resumed", "") + "; " if have.get("resumed") else "") + ts))
    con.commit()


def load_checklists(qids=None):
    """qid -> dict(parsed, dropped, reason, finish, ...) for every cached question (or the given ones). Read-only."""
    if not os.path.exists(CACHE): return {}
    con = sqlite3.connect("file:%s?mode=ro" % CACHE, uri=True)
    cols = ["question_id", "parsed_json", "finish_reason", "completion_tokens", "dropped", "drop_reason", "audit_n", "audit_gram", "response_id"]
    out = {}
    for r in con.execute("SELECT %s FROM checklists" % ",".join(cols)):
        d = dict(zip(cols, r))
        if qids is not None and d["question_id"] not in qids: continue
        d["parsed"] = json.loads(d["parsed_json"]) if d["parsed_json"] else None
        out[d["question_id"]] = d
    con.close(); return out


def checklist_sha(qids):
    """Pins the checklist CONTENT and the audit decisions for the given questions (what ref_checklist.py judges under)."""
    rows = load_checklists(set(qids))
    h = hashlib.sha256()
    for q in sorted(rows):
        d = rows[q]; h.update(("%d\x1f%s\x1f%d\x1f%s\n" % (q, d["parsed_json"] or "", d["dropped"] or 0, d["drop_reason"] or "")).encode("utf-8"))
    return h.hexdigest()


def usable(qids):
    """(usable checklists {qid: parsed}, counts dict). Usable = parsed and not dropped. The 5% guard is over the given questions."""
    rows = load_checklists(set(qids)); n = len(qids)
    parsed = {q: d for q, d in rows.items() if d["parsed"] is not None}
    unparsed = n - len(parsed)              # missing from the cache counts as unparsed for the guard
    rule_of = lambda why: (why or "").split(":")[0].split(" ")[0]        # "letter: ...", "ngram 6: ...", "short-option: ...", "numeral: ..."
    by_rule = {r: sum(1 for d in parsed.values() if d["dropped"] and rule_of(d["drop_reason"]) == r) for r in DROP_RULES}
    use = {q: d["parsed"] for q, d in parsed.items() if not d["dropped"]}
    counts = dict(questions=n, cached=len(rows), parsed=len(parsed), unparsed=unparsed, unparsed_rate=unparsed / max(1, n),
                  dropped_letter=by_rule["letter"], dropped_ngram=by_rule["ngram"], dropped_short=by_rule["short-option"], dropped_numeral=by_rule["numeral"],
                  dropped=sum(1 for d in parsed.values() if d["dropped"]), usable=len(use), guard_ok=unparsed <= 0.05 * n)
    return use, counts


def dropped_label(c):
    return "dropped letter %d, ngram %d, short-option %d, numeral %d" % (c["dropped_letter"], c["dropped_ngram"], c["dropped_short"], c["dropped_numeral"])


# ── dry run ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def prepare(pilot):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = GEN_MODEL; rr.MAX_TOKENS = MAXTOK
    qids, sched = question_ids()
    if pilot: qids = qids[:pilot]
    rows = question_rows(qids)
    return qids, rows, sched


def dry_run(pilot):
    qids, rows, sched = prepare(pilot)
    built = []
    for q in qids:
        stem, opts, key = rows[q]
        body = rr.payload_body(GEN_SYSTEM, jsm.user_prompt(stem, opts))
        assert tuple(body) == ("model", "max_tokens", "messages"), "temperature must be omitted (D2); body keys %r" % (tuple(body),)
        assert body["model"] == GEN_MODEL and body["max_tokens"] == MAXTOK
        built.append((q, body))
    # audit self-test on synthetic text, so the rules are exercised in every dry run
    stem, opts, key = rows[qids[0]]; ci = LETTERS.find(key)
    leak_letter = {"required": ["The answer is (%s)." % key], "pitfalls": ["x"]}
    leak_text = {"required": [opts[ci]], "pitfalls": ["x"]}
    clean = {"required": ["State the governing rule and apply it to the facts."], "pitfalls": ["Confusing timing of the force with its purpose."]}
    formula = {"required": ["Use P(A) and P(B) correctly."], "pitfalls": ["x"]}
    a1 = audit_one(leak_letter, stem, opts, key); a2 = audit_one(leak_text, stem, opts, key); a3 = audit_one(clean, stem, opts, key); a4 = audit_one(formula, stem, opts, key)
    assert a1[0] == 1 and a1[1].startswith("letter"), a1
    assert a2[0] == 1 and a2[1].split(":")[0] in ("ngram", "short-option", "numeral"), a2   # the whole correct option is caught by (ii) or (iii)
    assert a3[0] == 0 and a4[0] == 0, (a3, a4)
    # rule (iii) on fixed synthetic material: a short option / a numeral unique to the correct option drops; one shared with a distractor or the stem does not
    s_stem = "A gas at 0.5 atm is cooled. What is the new pressure?"; s_opts = ["600", "0.373 atm", "0.5 atm", "Procurement"]
    b1 = audit_one({"required": ["The final value is 600."], "pitfalls": ["x"]}, s_stem, s_opts, "A")
    b2 = audit_one({"required": ["The pressure is 0.373 atm."], "pitfalls": ["x"]}, s_stem, s_opts, "B")
    b3 = audit_one({"required": ["Start from 0.5 atm and apply Gay-Lussac."], "pitfalls": ["x"]}, s_stem, s_opts, "C")      # "0.5 atm" is in the stem: excused
    b4 = audit_one({"required": ["Procurement is a support activity."], "pitfalls": ["x"]}, s_stem, s_opts, "D")
    b5 = audit_one({"required": ["Divide by 2 and use 0.5 atm as the start."], "pitfalls": ["x"]}, s_stem, s_opts, "A")     # neither 2 nor 0.5 is in "600"
    b6 = audit_one({"required": ["The value 600 appears in the stem."], "pitfalls": ["x"]}, "It reads 600 units at first.", s_opts, "A")   # in the stem: excused
    assert b1[0] == 1 and b1[1].split(":")[0] in ("short-option", "numeral"), b1
    assert b2[0] == 1 and b2[1].split(":")[0] in ("short-option", "numeral"), b2
    b7 = audit_one({"required": ["The pressure reaches 0.373 at equilibrium."], "pitfalls": ["x"]}, s_stem, s_opts, "B")   # numeral alone, not the whole option
    assert b7[0] == 1 and b7[1].startswith("numeral"), b7
    assert b3[0] == 0 and b4[0] == 1 and b4[1].startswith("short-option") and b5[0] == 0 and b6[0] == 0, (b3, b4, b5, b6)
    print("CHECKLIST-GEN DRY RUN: nothing posted")
    print("  questions    %d distinct questions of the %d key-decidable R3 matches (%s)" % (len(qids), len(sched), "pilot %d" % pilot if pilot else "full"))
    print("  CALL COUNT   %d (1 per question)" % len(built))
    print("  POOL         %s (every question asserted inside it)" % POOL)
    print("  MODEL        %s (provider azure; the reference's own model)" % GEN_MODEL)
    print("  CAP          max_tokens %d | temperature %s   [%s]" % (MAXTOK, "omitted", TEMPERATURE_DECISION))
    print("  PROTOCOL     %s" % PROTOCOL)
    print("  USER PROMPT  judge_solve_map.user_prompt (stem + lettered options), byte-identical to the S1 reference solve's")
    print("  SYSTEM SHA   %s" % system_sha())
    print("  CACHE        %s%s" % (CACHE, "   <- EXISTS" if os.path.exists(CACHE) else "   (new)"))
    print("  PILOT BLOCK  the first %d questions of a --run are posted first and read by the 5%% unparsed guard before the rest" % PILOT_BLOCK)
    print("  AUDIT        letter rule (%d patterns) + n-gram rule (>= %d words, longest shared with the correct option) + whole short option / numeral rule; stem and distractors excuse; self-test OK" % (len(LETTER_PATTERNS), NGRAM_MIN))
    print("  SCRIPT SHA   %s" % script_sha())
    q0, b0 = built[0]
    print("\n=== FIRST PAYLOAD: question %d (request body keys %s) ===" % (q0, tuple(b0)))
    print("--- system ---"); print(b0["messages"][0]["content"]); print("--- user ---"); print(b0["messages"][1]["content"]); print("--- end of first payload ---")
    return 0


# ── run ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _gen_block(todo, rows, con, workers, tag):
    lock = threading.Lock(); ok = err = 0

    def one(q):
        stem, opts, key = rows[q]
        content, provider, ctok, _, finish, msg = rr.call_judge_full(GEN_SYSTEM, jsm.user_prompt(stem, opts))
        raw = content or ""
        parsed = parse_checklist(raw)
        rid = (msg or {}).get("_response_id") if isinstance(msg, dict) else None
        now = time.time()
        if parsed is None:
            return (q, raw, None, finish, ctok, rid, now, provider, now, 0, "", None, "")
        d, why, n, gram = audit_one(parsed, stem, opts, key)
        return (q, raw, json.dumps(parsed, ensure_ascii=False), finish, ctok, rid, now, provider, now, d, why, n, gram)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s" % (futs[f], str(e)[:120]), flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO checklists VALUES (%s)" % ",".join("?" * 13), row); con.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo): print("  [%s] %d/%d (ok %d, err %d)" % (tag, i, len(todo), ok, err), flush=True)
    print("[%s] done: ok %d, errors %d" % (tag, ok, err), flush=True)


def guard_readout(qids, label):
    use, c = usable(qids)
    print("  GUARD %-6s questions %d | cached %d | parsed %d | unparsed %d (%.1f%%) | %s | usable %d | %s"
          % (label, c["questions"], c["cached"], c["parsed"], c["unparsed"], 100 * c["unparsed_rate"], dropped_label(c), c["usable"],
             "OK" if c["guard_ok"] else "ABOVE 5%: not usable for a verdict-bearing run"))
    return c["guard_ok"]


def run(pilot, workers):
    rr.load_env()
    qids, rows, sched = prepare(pilot)
    con = open_cache(); pin_meta(con)
    done = {q for (q,) in con.execute("SELECT question_id FROM checklists WHERE parsed_json IS NOT NULL")}   # unparsed rows are re-posted on resume
    todo = [q for q in qids if q not in done]
    print("CHECKLIST-GEN RUN: pool %s | model %s | questions %d | cached %d | to do %d (%d calls) | max_tokens %d | temperature omitted | workers %d | script %s"
          % (POOL, GEN_MODEL, len(qids), len(qids) - len(todo), len(todo), len(todo), MAXTOK, workers, script_sha()[:16]), flush=True)
    pilot_ids = qids[:PILOT_BLOCK]
    first = [q for q in todo if q in set(pilot_ids)]; rest = [q for q in todo if q not in set(pilot_ids)]
    if first:
        print("  PILOT BLOCK: %d calls on the first %d questions, then the guard" % (len(first), PILOT_BLOCK), flush=True)
        _gen_block(first, rows, con, workers, "pilot")
    if not guard_readout(pilot_ids, "pilot"):
        for q, fin, ct, raw in con.execute("SELECT question_id, finish_reason, completion_tokens, substr(raw,1,160) FROM checklists WHERE parsed_json IS NULL"):
            if q in set(pilot_ids): print("      unparsed q %d | finish %s | completion tokens %s | raw[:160] %r" % (q, fin, ct, raw))
        print("  PILOT GUARD FAILED: not posting the remaining %d questions. finish_reason=length means the cap is too small (a new cap is a new\n"
              "  cache: move %s aside); finish_reason=stop with malformed JSON is a prompt problem, fix GEN_SYSTEM (new system sha, new cache)." % (len(rest), CACHE), flush=True)
        return False
    if rest: _gen_block(rest, rows, con, workers, "main")
    return guard_readout(qids, "all")


# ── audit ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def audit(pilot, verbose):
    """(Re)apply the audit to every parsed checklist of the question set - idempotent; the text is never edited - and print counts."""
    if not os.path.exists(CACHE):
        print("[CACHE] %s does not exist: nothing to audit" % CACHE); return
    qids, rows, sched = prepare(pilot)
    con = open_cache()
    cached = {q: (pj, dr) for q, pj, dr in con.execute("SELECT question_id, parsed_json, drop_reason FROM checklists")}
    changed = 0; advisory = 0; nd = defaultdict(int); examples = []
    for q in qids:
        if q not in cached or not cached[q][0]: continue
        parsed = json.loads(cached[q][0]); stem, opts, key = rows[q]
        d, why, n, gram = audit_one(parsed, stem, opts, key)
        if (d, why) != (int(bool(cached[q][1])), cached[q][1] or ""): changed += 1
        con.execute("UPDATE checklists SET dropped=?, drop_reason=?, audit_n=?, audit_gram=? WHERE question_id=?", (d, why, n, gram, q))
        if d: nd[why.split(":")[0].split(" ")[0]] += 1; examples.append((q, why))
        ci = LETTERS.find(key)
        if 0 <= ci < len(opts) and unique_shared_ngrams(checklist_text(parsed), opts[ci], stem, [o for j, o in enumerate(opts) if j != ci]): advisory += 1
    con.commit()
    use, c = usable(qids)
    dropped_q = {q for q in qids if q in cached and cached[q][0] and q not in use}
    unparsed_q = {q for q in qids if q not in cached or not cached[q][0]}
    excl = [t for t in sched if t[1] in dropped_q or t[1] in unparsed_q]
    print("=== CHECKLIST AUDIT (%s): %d questions of the %d key-decidable R3 matches ===" % ("pilot %d" % pilot if pilot else "full", len(qids), len(sched)))
    print("  cached %d | parsed %d | unparsed %d (%.1f%%) -> guard %s" % (c["cached"], c["parsed"], c["unparsed"], 100 * c["unparsed_rate"], "OK" if c["guard_ok"] else "FAIL (> 5%)"))
    print("  dropped by the letter rule %d | by the n-gram rule (>= %d words, longest, stem/distractor excused) %d | by the short-option rule %d | by the numeral rule %d | dropped total %d | usable %d"
          % (c["dropped_letter"], NGRAM_MIN, c["dropped_ngram"], c["dropped_short"], c["dropped_numeral"], c["dropped"], c["usable"]))
    print("  advisory (drops nothing): %d checklists hold ANY maximal shared n-gram >= %d words unique to the correct option" % (advisory, NGRAM_MIN))
    print("  matches EXCLUDED from all three arms of ref_checklist.py: %d of %d (%d questions dropped, %d unparsed or missing)" % (len(excl), len(sched), len(dropped_q), len(unparsed_q)))
    print("  audit decisions changed by this pass: %d | checklist sha (content + decisions) %s" % (changed, checklist_sha(qids)[:16]))
    fr = defaultdict(int)
    for (f,) in con.execute("SELECT finish_reason FROM checklists"): fr[f or "(none)"] += 1
    if fr: print("  finish_reason %s" % dict(fr))
    for q, why in (examples if verbose else examples[:10]): print("      dropped q %d: %s" % (q, why))
    if not c["guard_ok"]: print("  VERDICT-BEARING RUN REFUSED on this checklist set (unparsed > 5%%): ref_checklist.py --run will not launch")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    print("[POOL] %s (pool of record; active pool verified by pool_guard)" % POOL, flush=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="assemble every payload, print counts and the first payload, post nothing")
    ap.add_argument("--run", action="store_true"); ap.add_argument("--audit", action="store_true")
    ap.add_argument("--pilot", type=int, default=None, help="only the first N questions (sorted by id)")
    ap.add_argument("--workers", type=int, default=8); ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.dry_run: sys.exit(dry_run(a.pilot))
    elif a.run:
        ok = run(a.pilot, a.workers); audit(a.pilot, a.verbose)
        sys.exit(0 if ok else 2)
    elif a.audit: audit(a.pilot, a.verbose)
    else: ap.print_help()
