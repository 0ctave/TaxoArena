"""GEN-ARENA — a judged arena on the union's generative corpora (registered 2026-09-13, docs/multi_corpus_design.md).

  python tools/analysis/generative_arena.py --schedule
  python tools/analysis/generative_arena.py --judge [--pilot N] [--workers 8]
  python tools/analysis/generative_arena.py --analyze

Does the deployed judge reproduce the ROUTER's decisions without an answer key? MATH and IFEval are the only two
of the six corpora that carry model traces. The judge is grok-4-1-fast-non-reasoning with the v2 verify-first
mechanics, dual order and confidence, NO induced rubric, and a VERIFIER as the reference (MATH: the corrected
target; IFEval: the constraint list) — so there are zero reasoning calls. Questions come from the reserved side
of the same per-(source, domain) 0.30 / seed-42 split the router analysis uses.

REGISTERED: (1) key-decidable accuracy >= 0.75; (2) per-corpus board Spearman rho vs corrected key accuracy
>= 0.85 on both corpora; (3) BRIDGE: judged per-corpus argmax == key-based per-corpus argmax on both;
(4) decidable tie rate <= 15%.
"""
import os, sys, json, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rubric_p8 as p8
import judge_free_tests as jf
import prompt_v2

DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
CACHE = os.path.join(ROOT, "experiment_results", "multicorpus", "gen_arena_grok.db")
ROSTER = ["Qwen2.5-32B-Instruct", "Qwen2.5-72B-Instruct", "Llama-3.3-70B-Instruct", "Qwen2.5-Math-7B-Instruct",
          "Llama-3.1-70B-Instruct", "Mistral-Small-Instruct-2409", "Phi-3.5-mini-instruct", "Mixtral-8x7B-Instruct-v0.1"]
N_MATCHES = {"MATH": 1800, "IFEVAL": 1200}
SYSTEM_BY_SOURCE = {
    "MATH": "You are judging two attempts at a competition mathematics problem. The verified correct final answer is given as a reference; a response is only better if it reaches that answer by sound reasoning.",
    "IFEVAL": "You are judging two responses to an instruction-following prompt. The instruction constraints that the response must satisfy are listed as a reference; a response is only better if it satisfies more of them.",
}
RUBRIC_BY_SOURCE = {
    "MATH": "Rank by: (1) does the final answer match the reference answer; (2) is the derivation valid and complete; (3) is the answer stated unambiguously. A wrong final answer cannot win, however elegant the work.",
    "IFEVAL": "Rank by: (1) how many of the listed constraints the response satisfies exactly; (2) whether it also answers the underlying request usefully. A response that violates a listed constraint cannot win on style.",
}


def correctness(con):
    """Corrected MATH (eval_results_mathfix) + IFEval as ingested."""
    G = defaultdict(dict)
    for q, m, c in con.execute("SELECT e.question_id, e.model_name, e.is_correct FROM eval_results e JOIN corpus_questions q USING(question_id) WHERE q.source IN ('MATH','IFEVAL')"):
        G[q][m] = int(c)
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix"):
        if q in G and m in G[q]: G[q][m] = int(c)
    return G


def reserved_split(con, ratio=0.3, seed=42):
    """The reserved side of the per-(source, domain) split — identical rule to multicorpus_router_e2e.py."""
    Q = {q: (s, d) for q, s, d in con.execute("SELECT question_id, source, domain FROM corpus_questions")}
    rng = random.Random(seed); strata = defaultdict(list)
    for q, sd in Q.items(): strata[sd].append(q)
    test = set()
    for k in sorted(strata):
        v = sorted(strata[k]); rng.shuffle(v); test.update(v[:int(round(len(v) * ratio))])
    return Q, test


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS schedule (match_id INTEGER PRIMARY KEY, source TEXT, qid INTEGER, model_a TEXT, model_b TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, source TEXT, qid INTEGER, model_a TEXT, model_b TEXT, "
                "vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit(); return con


def build_schedule():
    src = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    Q, test = reserved_split(src); G = correctness(src)
    con = open_cache()
    if con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        print("schedule exists: %d matches" % con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]); return
    rng = random.Random(42); rows = []; mid = 30_000_000
    pairs = [(ROSTER[i], ROSTER[j]) for i in range(len(ROSTER)) for j in range(i + 1, len(ROSTER))]
    for source, n_total in N_MATCHES.items():
        qs = sorted(q for q in test if Q[q][0] == source and all(m in G.get(q, {}) for m in ROSTER))
        deck = [p for p in pairs for _ in range((n_total // len(pairs)) + 1)][:n_total]; rng.shuffle(deck)
        for a, b in deck:
            if rng.random() < 0.5: a, b = b, a
            rows.append((mid, source, qs[rng.randrange(len(qs))], a, b)); mid += 1
        print("%-7s %d reserved questions with full roster coverage -> %d matches over %d pairs" % (source, len(qs), n_total, len(pairs)))
    con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?)", rows); con.commit()
    print("schedule: %d matches | %d distinct questions" % (len(rows), len({r[2] for r in rows})))


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    src = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    meta = {q: (s, t, tg) for q, s, t, tg in src.execute("SELECT question_id, source, text, target FROM corpus_questions WHERE source IN ('MATH','IFEVAL')")}
    outputs = {(q, m): o for q, m, o in src.execute("SELECT e.question_id, e.model_name, e.model_output FROM eval_results e JOIN corpus_questions q USING(question_id) WHERE q.source IN ('MATH','IFEVAL')")}
    con = open_cache()
    sched = con.execute("SELECT match_id, source, qid, model_a, model_b FROM schedule ORDER BY match_id").fetchall()
    if pilot: sched = sched[:pilot]
    done = {r[0] for r in con.execute("SELECT match_id FROM verdicts")}
    todo = [s for s in sched if s[0] not in done]
    print("GEN-ARENA: schedule %d | jobs %d (%d calls) | workers %d" % (len(sched), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def reference(source, target):
        if source == "MATH":
            return "\n\n[Verified reference answer]\n%s" % target
        try:
            d = json.loads(target); ids = d.get("instruction_id_list") or []
            kw = d.get("kwargs") or []
            lines = []
            for i, c in enumerate(ids):
                args = {k: v for k, v in (kw[i] or {}).items() if v is not None} if i < len(kw) and isinstance(kw[i], dict) else {}
                lines.append("- %s%s" % (c, (" " + json.dumps(args)) if args else ""))
            return "\n\n[Constraints the response must satisfy]\n%s" % "\n".join(lines)
        except Exception:
            return ""

    def one(m):
        mid, source, qid, a, b = m
        s, text, target = meta[qid]
        ta, tb = outputs.get((qid, a)) or "", outputs.get((qid, b)) or ""
        if not ta.strip() or not tb.strip(): return None
        q = text + reference(source, target)
        system = (prompt_v2.v2_system_template().replace("$systemPrompt", SYSTEM_BY_SOURCE[source]).replace("$rubric", RUBRIC_BY_SOURCE[source])
                  + "\n\n" + rj.SCHEMA_INSTRUCTION)
        raw1 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, ta, tb))[0])
        raw2 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, tb, ta))[0])
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, source, qid, a, b, v1, v2, c1, c2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR match %s: %s" % (futs[f][0], str(e)[:110]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 15), row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    src = sqlite3.connect("file:%s?mode=ro" % DB, uri=True); G = correctness(src)
    con = open_cache()
    rows = [r for r in con.execute("SELECT match_id, source, qid, model_a, model_b, winner, flip, invalid, conf1, conf2 FROM verdicts") if not r[7]]
    n_inv = con.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=1").fetchone()[0]
    print("=== GEN-ARENA: %d valid verdicts (%d invalid), judge grok-4-1-fast-non-reasoning, verifier reference, no rubric ===" % (len(rows), n_inv))
    checks = []
    dec_all = []
    for source in ("MATH", "IFEVAL", "ALL"):
        sub = [r for r in rows if source == "ALL" or r[1] == source]
        dec = [r for r in sub if G[r[2]][r[3]] != G[r[2]][r[4]]]
        acc = sum(1 for r in dec if r[5] == (r[3] if G[r[2]][r[3]] else r[4])) / max(1, len(dec))
        ties = sum(1 for r in dec if r[5] == "TIE") / max(1, len(dec))
        flip = sum(r[6] for r in sub) / max(1, len(sub))
        print("  %-7s matches %4d | key-decidable %4d (%.0f%%) | accuracy %.3f | decidable ties %.3f | flip %.3f"
              % (source, len(sub), len(dec), 100 * len(dec) / max(1, len(sub)), acc, ties, flip))
        if source == "ALL": dec_all = (acc, ties)
    for source in ("MATH", "IFEVAL"):
        sub = [r for r in rows if r[1] == source]
        qs = {r[2] for r in sub}
        key = {m: sum(G[q][m] for q in qs) / len(qs) for m in ROSTER}
        th = jf.board_from(((r[3], r[4], 0.5 if r[5] == "TIE" else (1.0 if r[5] == r[3] else 0.0), 1.0) for r in sub), ROSTER)
        rho = rj.spearman([th[m] for m in ROSTER], [key[m] for m in ROSTER])
        j_best = max(ROSTER, key=lambda m: th[m]); k_best = max(ROSTER, key=lambda m: key[m])
        print("\n  %s board (n=%d matches over %d questions): rho vs corrected key accuracy = %.3f" % (source, len(sub), len(qs), rho))
        for m in sorted(ROSTER, key=lambda m: -th[m]): print("    %-30s theta %+.3f | key %.3f" % (m, th[m], key[m]))
        print("    judged argmax %s | key argmax %s -> BRIDGE %s" % (j_best, k_best, "HOLDS" if j_best == k_best else "BREAKS"))
        checks.append(("(2) %s rho >= 0.85" % source, rho, rho >= 0.85))
        checks.append(("(3) %s bridge: judged argmax == key argmax" % source, 1.0 if j_best == k_best else 0.0, j_best == k_best))
    checks.insert(0, ("(1) key-decidable accuracy >= 0.75", dec_all[0], dec_all[0] >= 0.75))
    checks.append(("(4) decidable tie rate <= 0.15", dec_all[1], dec_all[1] <= 0.15))
    print()
    for lab, val, ok in checks: print("  %-52s %.3f -> %s" % (lab, val, "OK" if ok else "FAIL"))
    print("  GEN-ARENA REGISTERED: %s" % ("PASS" if all(c[2] for c in checks) else "FAIL"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", action="store_true"); ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.schedule: build_schedule()
    elif a.judge: build_schedule(); judge(a.pilot, a.workers)
    elif a.analyze: analyze()
