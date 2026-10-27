"""MATH-FIX — a tolerant answer extractor for the MATH corpus (registered 2026-09-13, docs/multi_corpus_design.md).

  python tools/analysis/math_fix.py --apply     # writes eval_results_mathfix (never overwrites eval_results)
  python tools/analysis/math_fix.py --report

The leaderboard's MATH-hard exact_match only credits the literal Minerva sentence "The final answer is X", so six
of 18 models score exactly 0.000 despite answering correctly in \\boxed{}. Extraction order: last \\boxed/\\fbox,
then "final answer is ...", then the last number. Both sides are normalised, then compared numerically (rel. tol
1e-6) or as strings. Correctness is only RAISED; any 1 -> 0 disagreement is reported as an extractor bug.
Zero LLM calls.
"""
import os, re, sys, sqlite3, argparse
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
BOXED = re.compile(r"\\(?:boxed|fbox)\s*\{")
FINAL = re.compile(r"final answer is[:\s]*\$?(.+?)(?:\$|\.\s|\.$|\n|$)", re.I | re.S)
NUM = re.compile(r"-?\d+(?:\.\d+)?(?:/\d+)?")


def last_braced(text, pat):
    """Last \\boxed{...} honouring nested braces."""
    out = None
    for m in pat.finditer(text):
        i = m.end(); depth = 1; buf = []
        while i < len(text) and depth:
            ch = text[i]
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if not depth: break
            buf.append(ch); i += 1
        out = "".join(buf)
    return out


def extract_all(resp):
    """Every plausible final answer, in preference order. A response counts as correct if ANY candidate matches:
    the harness scores its Minerva sentence, we also read \boxed, and preferring one over the other would
    manufacture disagreements in both directions."""
    if not resp: return []
    out = []
    b = last_braced(resp, BOXED)
    if b is not None and b.strip(): out.append(b)
    m = FINAL.search(resp)
    if m and m.group(1).strip(): out.append(m.group(1))
    n = NUM.findall(resp[-400:])
    if n: out.append(n[-1])
    return out


def extract(resp):
    c = extract_all(resp)
    return c[0] if c else None


UNITS = re.compile(r"\s*(?:inches|inch|feet|foot|cm|mm|km|meters|metre|metres|meter|miles|mile|seconds|second|sec|minutes|minute|hours|hour|days|day|degrees|degree|units|unit|square|cubic|dollars|dollar|percent|ways|people|students|integers|cents)\.?", re.I)


def normalise(s):
    if s is None: return None
    s = s.strip()
    # Upstream bug repair: the leaderboard's own doc.answer strips the substring "ft" as a unit, so \infty is
    # stored as \iny (verified in the raw JSONL). Undo it on both sides so the comparison is like for like.
    s = s.replace("\iny", "\infty")
    s = s.replace("\$", "").replace("\%", "")
    for junk in ("\\left", "\\right", "\\!", "\\,", "\\;", "\\ ", "$", "\\displaystyle", "%"):
        s = s.replace(junk, "")
    s = re.sub(r"\\(?:text|mbox|mathrm|hbox)\s*\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\d?frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\[tdc]frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", s)
    s = re.sub(r"^[a-zA-Z]\s*=\s*", "", s.strip())
    s = UNITS.sub("", s)
    s = s.replace(",", "").replace(" ", "").rstrip(".").strip()
    return s


def as_number(s):
    if s is None: return None
    t = s.replace("(", "").replace(")", "")
    try: return float(t)
    except ValueError: pass
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)/(-?\d+(?:\.\d+)?)", t)
    if m:
        try: return float(Fraction(m.group(1)) / Fraction(m.group(2)))
        except Exception: return None
    return None


def equal_one(pred, target):
    p, t = normalise(pred), normalise(target)
    if p is None or t is None or p == "": return False
    if p == t: return True
    if p.replace("(", "").replace(")", "") == t.replace("(", "").replace(")", ""): return True
    a, b = as_number(p), as_number(t)
    if a is not None and b is not None: return abs(a - b) <= 1e-6 * max(1.0, abs(b))
    if b is not None:                       # target numeric, prediction carries a unit or stray markup
        m = NUM.search(p)
        if m:
            a = as_number(m.group(0))
            if a is not None: return abs(a - b) <= 1e-6 * max(1.0, abs(b))
    return False


def equal(pred, target, candidates=None):
    for c in (candidates if candidates is not None else [pred]):
        if equal_one(c, target): return True
    return False


def run(apply_):
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT e.question_id, e.model_name, e.model_output, e.is_correct, q.target FROM eval_results e "
                       "JOIN corpus_questions q USING(question_id) WHERE q.source='MATH'").fetchall()
    per = {}; no_answer = {}; bug = []
    out = []
    for qid, m, resp, old, target in rows:
        cands = extract_all(resp or ""); pred = cands[0] if cands else None
        ok = equal(pred, target, cands)
        if not cands or normalise(pred) == "": no_answer[m] = no_answer.get(m, 0) + 1
        if old and not ok: bug.append((qid, m, pred, target))
        new = 1 if (ok or old) else 0          # only ever raise
        per.setdefault(m, [0, 0]); per[m][0] += new; per[m][1] += 1
        out.append((qid, m, new))
    print("MATH-FIX: %d (question, model) rows | extractor 1->0 disagreements: %d %s" % (len(rows), len(bug), "(reported below)" if bug else "(none)"))
    print("\n%-30s %8s %8s %8s   %s" % ("model", "before", "after", "delta", "responses with no extractable answer"))
    for m in sorted(per, key=lambda m: -per[m][0] / per[m][1]):
        new = per[m][0] / per[m][1]
        old = con.execute("SELECT AVG(e.is_correct) FROM eval_results e JOIN corpus_questions q USING(question_id) WHERE q.source='MATH' AND e.model_name=?", (m,)).fetchone()[0]
        print("  %-28s %8.3f %8.3f %+8.3f   %d" % (m, old, new, new - old, no_answer.get(m, 0)))
    for qid, m, pred, target in bug[:10]: print("  BUG 1->0: q%s %s pred=%r target=%r" % (qid, m, pred, target))
    if apply_:
        con.execute("DROP TABLE IF EXISTS eval_results_mathfix")
        con.execute("CREATE TABLE eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct INTEGER, PRIMARY KEY (question_id, model_name))")
        con.executemany("INSERT OR REPLACE INTO eval_results_mathfix VALUES (?,?,?)", out)
        con.commit()
        print("\nwrote eval_results_mathfix: %d rows (eval_results untouched)" % len(out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); ap.add_argument("--report", action="store_true")
    a = ap.parse_args(); run(a.apply)
