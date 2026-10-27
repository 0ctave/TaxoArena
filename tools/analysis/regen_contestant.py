"""REGEN — regenerate a model's answers under the CONTESTANTS' prompt so it can enter the arena fairly.

  python tools/analysis/regen_contestant.py --run [--pilot N] [--workers 8]
  python tools/analysis/regen_contestant.py --report

Registered 2026-09-13 (docs/judge_v2_program.md). grok-4-1-fast-reasoning solved the pool at 0.860 under an
answer-only JSON prompt, producing 361-character responses against the contestants' 900-1,500 character
chain-of-thought solutions; entering it on those would be penalised by the judge's measured length preference.
Here it answers under the MMLU-Pro CoT instruction the contestants were run with. Admission rule, fixed before
the run: median trace length inside the contestants' range AND extraction above 98%, else key-level only.
"""
import os, re, sys, json, time, sqlite3, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import stack_judge as sj
import pool_guard

CACHE = os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning-cot.db")
LETTERS = "ABCDEFGHIJ"
SYSTEM = ("The following is a multiple choice question about {cat}. Think step by step and then finish your "
          "answer with \"the answer is (X)\" where X is the correct letter choice.")
USER = "Question:\n{q}\n\nOptions:\n{opts}\n\nLet's think step by step."
ANS = re.compile(r"answer is\s*\(?([A-J])\)?", re.I)
ANS2 = re.compile(r"\b([A-J])\b(?!.*\b[A-J]\b)", re.S)


def extract(text):
    t = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S)
    m = ANS.search(t)
    if m: return m.group(1).upper()
    tail = t[-200:]
    m = ANS2.search(tail)
    return m.group(1).upper() if m else ""


def questions():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = [q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")]
    out = {}
    for q in pool:
        r = ev.execute("SELECT question_text, options_json, gt_answer, category FROM eval_results WHERE question_id=? AND model_name='gpt-4o-2024-08-06'", (q,)).fetchone()
        if r is None:
            r = ev.execute("SELECT question_text, options_json, gt_answer, category FROM eval_results WHERE question_id=? AND model_name!='Meta-Llama-3-70B-Instruct'", (q,)).fetchone()
        if r is None: continue
        try: opts = json.loads(r[1]) if r[1] else []
        except Exception: opts = []
        if not opts: continue
        out[q] = (r[0], opts, (r[2] or "").strip().upper()[:1], (r[3] or "").strip())
    return out


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT, ts REAL)")
    con.commit(); return con


def run(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-reasoning"; rr.load_env()
    qs = questions(); con = open_cache()
    done = {q for (q,) in con.execute("SELECT question_id FROM answers")}
    todo = [q for q in sorted(qs) if q not in done]
    if pilot: todo = todo[:pilot]
    print("REGEN grok-4-1-fast-reasoning under the CoT contestant prompt: %d pool questions | to do %d | workers %d"
          % (len(qs), len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = 0; correct = 0

    def one(q):
        text, opts, gt, cat = qs[q]
        blk = "\n".join("%s. %s" % (LETTERS[i], o) for i, o in enumerate(opts))
        raw = rr.strip_think(rr.call_judge(SYSTEM.format(cat=cat or "various subjects"), USER.format(q=text, opts=blk))[0])
        a = extract(raw)
        return (q, a, gt, int(a == gt and a != ""), raw, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR q %s: %s" % (futs[f], str(e)[:110]), flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO answers VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1; correct += row[3]
            if i % 200 == 0 or i == len(todo): print("  %d/%d (ok %d, err %d) | running accuracy %.3f" % (i, len(todo), ok, err, correct / max(1, ok)), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)


def report():
    import statistics as st
    con = open_cache()
    rows = list(con.execute("SELECT question_id, answer, correct, raw FROM answers"))
    if not rows: print("nothing cached"); return
    n = len(rows); acc = sum(r[2] for r in rows) / n
    lens = sorted(len(r[3] or "") for r in rows)
    extracted = sum(1 for r in rows if r[1]) / n
    old = {q: (a, c) for q, a, c in sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning.db"), uri=True).execute("SELECT question_id, answer, correct FROM answers")}
    both = [r for r in rows if r[0] in old]
    agree = sum(1 for r in both if r[1] == old[r[0]][0]) / max(1, len(both))
    old_acc = sum(old[r[0]][1] or 0 for r in both) / max(1, len(both))
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = set(pool_guard.eval_ids(pool_guard.MMLU_PRO_POOL))
    cl = {}
    for m, l in ev.execute("SELECT model_name, AVG(LENGTH(model_output)) FROM eval_results WHERE " + pool_guard.in_pool_sql(pool_guard.MMLU_PRO_POOL) + " GROUP BY model_name"):
        if m in sj.TOP4 or m in ("deepseek-chat-v2_5", "Meta-Llama-3_1-70B-Instruct"): cl[m] = l
    print("=== REGEN report: grok-4-1-fast-reasoning under the contestant CoT prompt ===")
    print("  answered %d pool questions | accuracy %.3f | answer-only prompt on the same questions %.3f | per-question agreement %.3f"
          % (n, acc, old_acc, agree))
    print("  extraction succeeded on %.1f%% of responses" % (100 * extracted))
    print("  trace length: median %d, mean %d, p10 %d, p90 %d characters" % (st.median(lens), sum(lens) / n, lens[n // 10], lens[9 * n // 10]))
    print("  contestants for comparison: %s" % ", ".join("%s %.0f" % (k[:14], v) for k, v in sorted(cl.items(), key=lambda x: -x[1])))
    lo, hi = min(cl.values()), max(cl.values())
    admit = lo <= st.median(lens) <= hi and extracted > 0.98
    print("  ADMISSION RULE (median length inside the contestants' range %.0f-%.0f AND extraction > 98%%): %s"
          % (lo, hi, "ADMITTED as a contestant" if admit else "NOT admitted - remains a key-level data point"))


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)   # the pool of record, by id; fail loudly if it does not reproduce
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true"); ap.add_argument("--report", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.run: run(a.pilot, a.workers)
    elif a.report: report()
