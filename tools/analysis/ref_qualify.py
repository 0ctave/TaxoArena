"""REF-QUAL — qualify a candidate REFERENCE model before spending on a re-judge (registered 2026-09-14).

  python tools/analysis/ref_qualify.py --baseline                  (incumbent's numbers, from cache, 0 calls)
  python tools/analysis/ref_qualify.py --model <deployment> --run  (~600 calls)
  python tools/analysis/ref_qualify.py --model <deployment> --report

WHY THIS EXISTS. A better reference is the only lever measured to raise the judge's ceiling rather than move
along it (ORACLE: +16.4pp from a perfect reference). But it cannot buy the frontier ORDER - ORACLE gave the
judge the answer key and arx/iask still did not come out (p=0.29) - so the payoff is concentrated where the
incumbent reference is WEAK. REF-BY-CELL measured that spread: grok-reasoning runs 0.727 (History) to 0.952
(Math). This qualifies a candidate on exactly the two things that decide whether a re-judge is worth buying,
plus the leakage term ARENA-13/DECOMP identified, for about 600 calls instead of 10,000.

THE THREE READOUTS, and the gate.
 (1) accuracy on the 302 arx/iask DISCRIMINATING questions, against the incumbent's 0.726 there;
 (2) accuracy in the three weakest cells (History, Engineering, Law), against the incumbent per cell;
 (3) ANSWER-AGREEMENT with each of the 12 contestants. DECOMP showed the leakage mechanism is answer
     agreement, not vendor identity, so a candidate that mirrors a FRONTIER contestant more closely than the
     incumbent does will inflate that contestant whatever its badge says.
GATE, fixed before any candidate is run: promote to a full re-judge only if (1) beats the incumbent by at least
3pp AND (3) shows no frontier contestant agreeing with the candidate more than it agrees with the incumbent by
more than 3pp. A candidate that fails (1) cannot raise the ceiling; one that fails (3) buys accuracy and pays
for it in bias exactly where the board is already weakest.
"""
import os, sys, re, json, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import arxiask_probe as ax
import pool_guard

MAXTOK = None   # --maxtok N raises the completion budget for this run only; None leaves rejudge_reasoning's
                # default untouched so every other script keeps posting a byte-identical payload.
PROTOCOL = "cot"  # --protocol json solves the candidate under the INCUMBENT's protocol (judge_solve_map: JSON
                  # answer-only prompt, its parser). The first two Kimi attempts used the contestants' CoT prompt
                  # against an incumbent solved with JSON - not like for like. json is the protocol of record.
WEAK = ("History", "Engineering", "Law")
PER_WEAK = 100
LETTERS = "ABCDEFGHIJ"
SYSTEM = ("The following is a multiple choice question about {cat}. Think step by step and then finish your "
          "answer with \"the answer is (X)\" where X is the correct letter choice.")
USER = "Question:\n{q}\n\nOptions:\n{opts}\n\nLet's think step by step."
ANS = re.compile(r"answer is\s*\(?([A-J])\)?", re.I)


def cache_path(model):
    """A raised token budget gets its OWN cache so a voided run is preserved as evidence rather than
    overwritten. REF-QUAL-KIMI's first attempt lives in the unsuffixed file."""
    tag = re.sub(r"[^A-Za-z0-9]+", "_", model) + ("" if PROTOCOL == "cot" else "_" + PROTOCOL) + ("" if not MAXTOK else "_mt%d" % MAXTOK)
    return os.path.join(ROOT, "experiment_results", "judge_solve", "refqual_%s.db" % tag)


def population():
    """The two strata the gate is about, plus everything needed to score them."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    K = defaultdict(dict); P = defaultdict(dict); META = {}
    for q, m, pr, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12: K[q][m] = int(c or 0); P[q][m] = (pr or "").strip().upper()[:1]
    for q, t, o, g, c in ev.execute(
            "SELECT question_id, question_text, options_json, gt_answer, category FROM eval_results "
            "WHERE model_name='gpt-4o-2024-08-06'"):
        if q in pool:
            try: opts = json.loads(o) if o else []
            except Exception: opts = []
            META[q] = (t, opts, (g or "").strip().upper()[:1], (c or "").strip())
    disc, _ = ax.questions()
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    weak = {a: [] for a in WEAK}
    for q in sorted(pool):
        if q not in route or q not in META: continue
        a = anchor_of(route[q])
        if a in weak and len(weak[a]) < PER_WEAK: weak[a].append(q)
    return pool, K, P, META, [q for q in disc if q in META], weak, anchor_of, route


def baseline():
    pool, K, P, META, disc, weak, anchor_of, route = population()
    rref.set_reference("grok-reasoning"); inc = rref.references()
    incc = {q: bool(v[2]) for q, v in inc.items()}
    print("=== REF-QUAL baseline: the incumbent reference (grok-4-1-fast-reasoning), from cache ===")
    d = [q for q in disc if q in incc]
    print("  (1) DISCRIMINATING subset: %d questions | incumbent accuracy %.3f"
          % (len(d), sum(incc[q] for q in d) / max(1, len(d))))
    print("  (2) WEAK cells:")
    for a in WEAK:
        qs = [q for q in weak[a] if q in incc]
        if qs: print("      %-14s n=%3d | incumbent accuracy %.3f" % (a, len(qs), sum(incc[q] for q in qs) / len(qs)))
    print("  (3) ANSWER-AGREEMENT of the incumbent with each contestant, over the pool:")
    ia = {q: v[0] for q, v in inc.items()}
    rows = []
    for m in sorted(p8.ARENA12):
        both = [q for q in pool if q in ia and P[q].get(m)]
        if both: rows.append((sum(1 for q in both if ia[q] == P[q][m]) / len(both), m, len(both)))
    for r, m, n in sorted(rows, reverse=True):
        print("      %-30s %.3f  (n=%d)%s" % (m[:30], r, n, "   <- frontier" if m in ("gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06") else ""))
    print("\n  GATE for a candidate: beat 0.726 on (1) by >= 3pp, and agree with no FRONTIER contestant more")
    print("  than the incumbent does by > 3pp.")


def extract(t):
    t = re.sub(r"<think>.*?</think>", "", t or "", flags=re.S)
    m = ANS.search(t)
    if m: return m.group(1).upper()
    m = re.search(r"\b([A-J])\b(?!.*\b[A-J]\b)", t[-200:], re.S)
    return m.group(1).upper() if m else ""


def run(model, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = model; rr.load_env()
    if MAXTOK:
        rr.MAX_TOKENS = MAXTOK
        print("REF-QUAL: completion budget raised to %d for this run" % MAXTOK, flush=True)
    pool, K, P, META, disc, weak, anchor_of, route = population()
    todo_qs = list(dict.fromkeys(list(disc) + [q for a in WEAK for q in weak[a]]))
    con = sqlite3.connect(cache_path(model))
    con.execute("CREATE TABLE IF NOT EXISTS answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT, ts REAL)")
    for col, decl in (("finish", "TEXT"), ("ctokens", "INTEGER")):
        try: con.execute("ALTER TABLE answers ADD COLUMN %s %s" % (col, decl))
        except sqlite3.OperationalError: pass
    con.commit()
    done = {q for (q,) in con.execute("SELECT question_id FROM answers")}
    todo = [q for q in todo_qs if q not in done]
    print("REF-QUAL [%s]: %d questions (%d discriminating + %d weak-cell) | to do %d | workers %d"
          % (model, len(todo_qs), len(disc), len(todo_qs) - len(disc), len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = 0

    def one(q):
        t, opts, gt, cat = META[q]
        if PROTOCOL == "json":
            # the incumbent's protocol, byte for byte: judge_solve_map's system prompt, user prompt and parser
            import judge_solve_map as jsm
            content, _, ctok, _, finish, _ = rr.call_judge_full(jsm.SYSTEM, jsm.user_prompt(t, opts))
            raw = rr.strip_think(content)
            a = (jsm.parse_answer(raw) or "").upper()[:1]
        else:
            blk = "\n".join("%s. %s" % (LETTERS[i], o) for i, o in enumerate(opts))
            content, _, ctok, _, finish, _ = rr.call_judge_full(
                SYSTEM.format(cat=cat or "various subjects"), USER.format(q=t, opts=blk))
            raw = rr.strip_think(content)
            a = extract(raw)
        return (q, a, gt, int(a == gt and a != ""), raw, time.time(), finish, ctok)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s" % (futs[f], str(e)[:110]), flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO answers (question_id,answer,gt,correct,raw,ts,finish,ctokens) "
                            "VALUES (?,?,?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)


def report(model):
    pool, K, P, META, disc, weak, anchor_of, route = population()
    con = sqlite3.connect("file:%s?mode=ro" % cache_path(model), uri=True)
    A = {q: (a, c) for q, a, c in con.execute("SELECT question_id, answer, correct FROM answers")}
    # TRUNCATION GUARD, added 2026-09-14 after REF-QUAL-KIMI was voided by exactly this. A reasoning
    # deployment that exhausts its budget inside `reasoning_content` returns EMPTY content, which
    # scores as a wrong answer and is indistinguishable from one unless it is counted.
    blank = [q for q, (a, _) in A.items() if not (a or "").strip()]
    dblank = [q for q in disc if q in A and not (A[q][0] or "").strip()]
    dn = sum(1 for q in disc if q in A)
    # The guard is evaluated on the DISCRIMINATING subset, where the 3pp gate is decided, as well as overall:
    # the review of 2026-09-15 found 7.5% overall hid 11.0% on that subset. And it REFUSES - the first version
    # only warned, and the warning never reached the .txt, so a clean-looking verdict was written anyway.
    rate_all = len(blank) / max(1, len(A)); rate_disc = len(dblank) / max(1, dn)
    if rate_all > 0.05 or rate_disc > 0.05:
        try:
            fr = dict(con.execute("SELECT COALESCE(finish,'(not recorded)'), COUNT(*) FROM answers "
                                  "WHERE answer IS NULL OR TRIM(answer)='' GROUP BY 1"))
        except Exception:
            fr = "(not recorded in this cache)"
        L = ["=== REF-QUAL: %s - VERDICT REFUSED ===" % model,
             "  %d of %d answers (%.1f%%) did not parse overall; %d of %d (%.1f%%) on the DISCRIMINATING subset."
             % (len(blank), len(A), 100 * rate_all, len(dblank), dn, 100 * rate_disc),
             "  An unparsed answer scores as wrong, so any accuracy below the 5% bar would be a floor, not an",
             "  estimate, and the 3pp gate cannot be read. finish_reason among the unparsed: %s" % fr,
             "  Re-run with a larger --maxtok, or record non-termination as a property of the candidate and",
             "  report accuracy among terminated answers as a SEPARATE, non-gate number."]
        txt = "\n".join(L)
        print(txt)
        open(cache_path(model)[:-3] + ".txt", "w", encoding="utf-8").write(txt + "\n")
        return
    rref.set_reference("grok-reasoning"); inc = rref.references()
    incc = {q: bool(v[2]) for q, v in inc.items()}; ia = {q: v[0] for q, v in inc.items()}
    L = ["=== REF-QUAL: %s against the incumbent grok-4-1-fast-reasoning ===" % model]
    d = [q for q in disc if q in A and q in incc]
    ca = sum(A[q][1] for q in d) / max(1, len(d)); ib = sum(incc[q] for q in d) / max(1, len(d))
    L.append("  (1) DISCRIMINATING subset n=%d | candidate %.3f | incumbent %.3f | %+.3f" % (len(d), ca, ib, ca - ib))
    L.append("  (2) WEAK cells:")
    for a in WEAK:
        qs = [q for q in weak[a] if q in A and q in incc]
        if not qs: continue
        c1 = sum(A[q][1] for q in qs) / len(qs); c0 = sum(incc[q] for q in qs) / len(qs)
        L.append("      %-14s n=%3d | candidate %.3f | incumbent %.3f | %+.3f" % (a, len(qs), c1, c0, c1 - c0))
    L.append("  (3) ANSWER-AGREEMENT with each contestant (leakage predictor), on the scored questions:")
    worst = 0.0
    for m in sorted(p8.ARENA12):
        both = [q for q in A if P[q].get(m) and q in ia]
        if not both: continue
        ac = sum(1 for q in both if A[q][0] == P[q][m]) / len(both)
        ai = sum(1 for q in both if ia[q] == P[q][m]) / len(both)
        fr = m in ("gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06")
        if fr: worst = max(worst, ac - ai)
        L.append("      %-30s candidate %.3f | incumbent %.3f | %+.3f%s" % (m[:30], ac, ai, ac - ai, "   <- frontier" if fr else ""))
    g1 = (ca - ib) >= 0.03; g2 = worst <= 0.03
    L.append("")
    L.append("  GATE (1) beat the incumbent on the discriminating subset by >= 3pp: %s (%+.3f)" % ("PASS" if g1 else "FAIL", ca - ib))
    L.append("  GATE (3) no frontier contestant gains > 3pp of agreement: %s (worst %+.3f)" % ("PASS" if g2 else "FAIL", worst))
    L.append("  -> %s" % ("PROMOTE: a full re-judge is worth buying" if (g1 and g2) else
                          "DO NOT PROMOTE on this evidence; 600 calls spent instead of 10,000"))
    txt = "\n".join(L)
    print(txt)
    # same tag as cache_path so a raised-cap report never overwrites the report of the run it corrects
    open(cache_path(model)[:-3] + ".txt", "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true"); ap.add_argument("--model", default=None)
    ap.add_argument("--run", action="store_true"); ap.add_argument("--report", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--maxtok", type=int, default=None)
    ap.add_argument("--protocol", choices=["cot", "json"], default="cot")
    a = ap.parse_args()
    if a.maxtok: MAXTOK = a.maxtok
    PROTOCOL = a.protocol
    if a.baseline: baseline()
    elif a.model and a.run: run(a.model, a.workers)
    elif a.model and a.report: report(a.model)
    else: ap.print_help()
