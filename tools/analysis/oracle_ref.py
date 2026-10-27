"""ORACLE — what survives a PERFECT reference? (registered 2026-09-14)

  python tools/analysis/oracle_ref.py --judge [--pilot N] [--workers 8]
  python tools/analysis/oracle_ref.py --analyze

The same 302 pool questions on which arx_0314 and iask_pro differ, the same judge, rubric and v2 mechanics as
ARXIASK, pairwise dual order. The ONLY manipulation is the content of the reference block: the ground-truth
letter and option text in place of grok-reasoning's answer. The wrapper sentence is byte-identical, "may be
wrong" included, so the judge is not told the reference is now infallible and only its CORRECTNESS varies.
"""
import os, sys, json, time, sqlite3, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import stack_judge as sj
import rubric_p8 as p8
import prompt_v2
import arxiask_probe as ax

A, B = ax.A, ax.B
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "oracle.db")
LETTERS = "ABCDEFGHIJ"


def oracle_refs(qs):
    """qid -> (letter, option text, True). The answer key, shaped exactly like a model reference."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = {}
    for q in qs:
        r = ev.execute("SELECT gt_answer, options_json FROM eval_results WHERE question_id=? AND options_json IS NOT NULL LIMIT 1", (q,)).fetchone()
        if not r: continue
        letter = (r[0] or "").strip().upper()[:1]
        try: opts = json.loads(r[1]) if r[1] else []
        except Exception: opts = []
        i = LETTERS.find(letter)
        if not letter or not (0 <= i < len(opts)): continue
        out[q] = (letter, opts[i], True)
    return out


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS pairwise (qid INTEGER PRIMARY KEY, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit(); return con


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    qs, K = ax.questions()
    if pilot: qs = qs[:pilot]
    refs = oracle_refs(qs)
    evals = rj.load_eval_rows(qs, {A, B})
    con = open_cache()
    done = {q for (q,) in con.execute("SELECT qid FROM pairwise")}
    todo = [q for q in qs if q not in done]
    print("ORACLE: %d discriminating questions | key references built for %d | to do %d (%d calls) | workers %d"
          % (len(qs), len(refs), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(q):
        ra, rb, ref, anc = evals.get((q, A)), evals.get((q, B)), refs.get(q), anchors.get(q)
        if ra is None or rb is None or ref is None or anc is None: return None
        sp, rbc = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rbc) + "\n\n" + rj.SCHEMA_INSTRUCTION
        qtext = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(qtext, ta, tb))[0])
        raw2 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(qtext, tb, ta))[0])
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (q, v1, v2, {"Model A": A, "Model B": B}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s" % (futs[f], str(e)[:110]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO pairwise VALUES (?,?,?,?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    qs, K = ax.questions()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    L = {(q, m): len(o or "") for q, m, o in ev.execute("SELECT question_id, model_name, model_output FROM eval_results") if m in (A, B)}
    ora = {q: (w, inv, fl) for q, w, inv, fl in open_cache().execute("SELECT qid, winner, invalid, flip FROM pairwise")}
    old = {q: (w, inv) for q, w, inv in sqlite3.connect("file:%s?mode=ro" % ax.CACHE, uri=True).execute("SELECT qid, winner, invalid FROM pairwise")}
    # grok-reference correctness on these questions, for the decomposition
    import rejudge_reference as rr2
    rr2.set_reference("grok-reasoning"); gr = rr2.references()

    got = [(q, ora[q][0]) for q in qs if q in ora and not ora[q][1]]
    dec = [(q, w) for q, w in got if w != "TIE"]
    kw = sum(1 for q in qs if K[(q, A)])
    acc = sum(1 for q, w in got if w == (A if K[(q, A)] else B)) / max(1, len(got))
    wa = sum(1 for q, w in dec if w == A)
    wr = wa / max(1, len(dec)); pbin = ax.binom_p(wa, len(dec))
    print("=== ORACLE: the ANSWER KEY as the reference, %d of %d discriminating questions judged ===" % (len(got), len(qs)))
    print("  key on these questions: %s wins %d, %s wins %d (rate %.3f)" % (A, kw, B, len(qs) - kw, kw / len(qs)))
    print("  ties %d | flips %d" % (len(got) - len(dec), sum(1 for q in qs if q in ora and ora[q][2])))
    # The registration set NO numeric bar for (1): 0.78-0.88 was a PREDICTION and 0.70 the falsifier. The
    # >=0.78 bar this line used was invented here and gave the number a third, inconsistent adjudication
    # alongside the ledger chip and the programme doc; corrected 2026-09-14 (audit finding A6).
    verdict = ("IMPROVED by %+.3f, and the through-line SURVIVES: the falsifier was 0.70. The PREDICTED band was "
               "0.78-0.88, and this lands %.3f under its lower edge." % (acc - 0.612, 0.78 - acc)
               if acc > 0.70 else "FALSIFIES the through-line as written")
    print("\n  (1) PRIMARY accuracy against the key %.3f  (grok reference on the same questions: 0.612) -> %s"
          % (acc, verdict))
    print("  (2) ORDER: %s win rate %.3f against the key's %.3f | binomial p=%.4g -> order recovered: %s"
          % (A, wr, kw / len(qs), pbin, "YES" if (wr > 0.5 and pbin < 0.05) else "NO"))
    both = [q for q, w in got if q in old and not old[q][1]]
    b = sum(1 for q in both if ora[q][0] == (A if K[(q, A)] else B) and old[q][0] != (A if K[(q, A)] else B))
    c = sum(1 for q in both if old[q][0] == (A if K[(q, A)] else B) and ora[q][0] != (A if K[(q, A)] else B))
    oacc = sum(1 for q in both if old[q][0] == (A if K[(q, A)] else B)) / max(1, len(both))
    nacc = sum(1 for q in both if ora[q][0] == (A if K[(q, A)] else B)) / max(1, len(both))
    print("  (3) PAIRED against ARXIASK on the same %d questions: grok reference %.3f -> oracle %.3f (%+.3f) | %d:%d | McNemar p=%.4g"
          % (len(both), oacc, nacc, nacc - oacc, b, c, p8.mcn(b, c)))
    wrong = [(q, w) for q, w in got if w != (A if K[(q, A)] else B)]
    longer = sum(1 for q, w in wrong if w != "TIE" and L[(q, w)] > L[(q, A if w == B else B)])
    print("\n  (4) DECOMPOSITION of judge error on the discriminating questions:")
    print("      with the grok reference (ARXIASK)                 %.3f" % oacc)
    print("      with the grok reference, its CORRECT subset only  0.788   (ARXIASK, n=217)")
    print("      with a PERFECT reference (this run)               %.3f" % acc)
    print("      -> reference-induced error %.3f | judge IRREDUCIBLE error %.3f" % (max(0.0, acc - oacc), 1 - acc))
    print("      of the %d remaining errors, %d (%.0f%%) went to the LONGER answer, %d were ties"
          % (len(wrong), longer, 100 * longer / max(1, len(wrong) - sum(1 for q, w in wrong if w == "TIE")), sum(1 for q, w in wrong if w == "TIE")))
    # DESCRIPTIVE, not registered: why (2) can fail while (1) succeeds - abstention is not random
    tie = [(q, w) for q, w in got if w == "TIE"]
    kr = lambda s: sum(1 for q, _ in s if K[(q, A)]) / max(1, len(s))
    adec = sum(1 for q, w in dec if w == (A if K[(q, A)] else B)) / max(1, len(dec))
    L2 = []
    L2.append("\n  (5) DESCRIPTIVE, not registered - why the order still does not come out, given accuracy 0.777:")
    L2.append("      ties are %d of %d judged (%.1f%%), and they are NOT random: the key makes %s the winner on"
              % (len(tie), len(got), 100 * len(tie) / len(got), A))
    L2.append("      %.3f of the TIED questions against %.3f of the DECIDED ones. Dual-order abstention removes"
              % (kr(tie), kr(dec)))
    L2.append("      exactly the evidence that separates the pair.")
    L2.append("      on the %d verdicts the judge does COMMIT to, accuracy is %.3f - %d wrong - yet the %s win rate"
              % (len(dec), adec, len(dec) - round(adec * len(dec)), A))
    L2.append("      is %.3f against the key's %.3f ON THAT SAME SUBSET. So the order fails on WHICH questions get"
              % (sum(1 for q, w in dec if w == A) / max(1, len(dec)), kr(dec)))
    L2.append("      abstained on, not on how the committed calls come out.")
    print("\n".join(L2))
    # where the two references agreed, the prompts differ only if grok was wrong: split accordingly
    same = [q for q in both if gr.get(q) and gr[q][2]]
    diff = [q for q in both if gr.get(q) and not gr[q][2]]
    for lbl, ss in (("grok reference was CORRECT", same), ("grok reference was WRONG", diff)):
        if not ss: continue
        o = sum(1 for q in ss if old[q][0] == (A if K[(q, A)] else B)) / len(ss)
        n = sum(1 for q in ss if ora[q][0] == (A if K[(q, A)] else B)) / len(ss)
        print("      %-28s n=%3d | grok ref %.3f -> oracle %.3f (%+.3f)" % (lbl, len(ss), o, n, n - o))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze()
