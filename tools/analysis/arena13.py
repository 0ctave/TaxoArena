"""ARENA-13 — a 13th contestant, judged without circularity, plus self-preference measured (registered 2026-09-14).

  python tools/analysis/arena13.py --schedule
  python tools/analysis/arena13.py --judge [--pilot N] [--workers 8]
  python tools/analysis/arena13.py --analyze

grok-4-1-fast-reasoning is admitted as a contestant, but it is also the judge's usual reference and its answer
coincides with that reference on 92.7% of questions. ARM A therefore judges the 12 new pairs against an ENSEMBLE
reference: the leave-out majority of the eight strongest contestants, excluding the match's own models, which
ENSEMBLE-REF measured at 0.833-0.880 and which contains no grok model. ARM B re-judges the four frontier pairs -
the same matches - with the grok reference, so the difference is a paired measurement of self-preference.
"""
import os, sys, json, time, random, sqlite3, argparse, threading
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import judge_free_tests as jf
import prompt_v2

NEW = "grok-4-1-fast-reasoning"
ENS = ["gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "arx_3", "claude-3-5-sonnet-20241022",
       "gpt-4o-2024-08-06", "claude-3.5-sonnet", "deepseek-chat-v2_5"]
FRONTIER = ["gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06"]
PER_PAIR = 150
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "arena13.db")
LETTERS = "ABCDEFGHIJ"


def setup():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id='p2dca21ab5f4ef3ae'")}
    P = defaultdict(dict); K = defaultdict(dict); OPT = {}
    for q, m, p, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        P[q][m] = (p or "").strip().upper()[:1]; K[q][m] = int(c or 0)
    for q, o in ev.execute("SELECT question_id, options_json FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
        try: OPT[q] = json.loads(o) if o else []
        except Exception: OPT[q] = []
    cot = {q: (a, c, raw) for q, a, c, raw in sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning-cot.db"), uri=True).execute("SELECT question_id, answer, correct, raw FROM answers")}
    route = r512.primary_routing("bareq512_s42")
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); anchor_of = r512.anchor_fn(nodes)
    return pool, P, K, OPT, cot, route, anchor_of


def ensemble_ref(q, P, OPT, exclude):
    """Leave-out majority of the strongest contestants, excluding the match's own models. No grok model is in ENS."""
    votes = Counter(P[q][m] for m in ENS if m not in exclude and P[q].get(m))
    if not votes: return None
    top = votes.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]: return None      # no decisive majority -> unusable
    letter = top[0][0]; i = LETTERS.find(letter); opts = OPT.get(q, [])
    return (letter, opts[i] if 0 <= i < len(opts) else "")


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS schedule (mid INTEGER PRIMARY KEY, qid INTEGER, opponent TEXT, anchor TEXT, frontier INTEGER)")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (mid INTEGER, arm TEXT, winner TEXT, invalid INTEGER, raw TEXT, ts REAL, PRIMARY KEY (mid, arm))")
    con.commit(); return con


def build():
    pool, P, K, OPT, cot, route, anchor_of = setup()
    con = open_cache()
    if con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]:
        print("schedule exists: %d" % con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0]); return
    rng = random.Random(42); rows = []; mid = 60_000_000
    for opp in p8.ARENA12:
        cand = [q for q in sorted(pool)
                if q in cot and cot[q][0] and P[q].get(opp) and cot[q][0] != P[q][opp]
                and q in route and ensemble_ref(q, P, OPT, {opp, NEW}) is not None]
        rng.shuffle(cand); take = cand[:PER_PAIR]
        for q in take:
            rows.append((mid, q, opp, anchor_of(route[q]), int(opp in FRONTIER))); mid += 1
        dec = sum(1 for q in take if cot[q][1] != K[q][opp])
        print("  vs %-30s candidates %4d -> %3d scheduled | key-decidable %3d (%.0f%%)" % (opp, len(cand), len(take), dec, 100 * dec / max(1, len(take))))
    con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?)", rows); con.commit()
    nf = sum(1 for r in rows if r[4])
    print("scheduled %d matches | arm A (ensemble ref) %d calls | arm B (self ref, frontier only) %d calls | total %d"
          % (len(rows), len(rows), nf, len(rows) + nf))


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    pool, P, K, OPT, cot, route, anchor_of = setup()
    rref.set_reference("grok-reasoning"); grok_refs = rref.references()
    rubrics = sj.anchor_rubrics()
    con = open_cache()
    sched = con.execute("SELECT mid, qid, opponent, anchor, frontier FROM schedule ORDER BY mid").fetchall()
    if pilot: sched = sched[:pilot]
    done = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts")}
    jobs = [(s, "ensemble") for s in sched if (s[0], "ensemble") not in done]
    jobs += [(s, "selfref") for s in sched if s[4] and (s[0], "selfref") not in done]
    evals = rj.load_eval_rows([s[1] for s in sched], set(p8.ARENA12))
    print("ARENA-13: %d matches | jobs %d (1 call each) | workers %d" % (len(sched), len(jobs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        (mid, qid, opp, anc, fr), arm = job
        ro = evals.get((qid, opp))
        if ro is None or qid not in cot: return None
        ref = ensemble_ref(qid, P, OPT, {opp, NEW}) if arm == "ensemble" else (grok_refs.get(qid) or (None,))[0:2]
        if arm == "selfref":
            g = grok_refs.get(qid)
            if g is None: return None
            ref = (g[0], g[1])
        if ref is None: return None
        sp, rub = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = ro[0] + "\n\n[Reference solution — produced independently, may be wrong]\n(%s) %s" % (ref[0], ref[1])
        ta = cot[qid][2]                                  # the new contestant's regenerated CoT trace
        tb = rj.robust_trace(ro[2], ro[3], ro[1])
        raw = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, ta, tb))[0])
        v, _ = rj.parse_judge(raw)
        w = {"Model A": NEW, "Model B": opp}.get(v, "TIE")
        return (mid, arm, w, int(v not in ("Model A", "Model B", "TIE")), raw, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 200 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    pool, P, K, OPT, cot, route, anchor_of = setup()
    con = open_cache()
    sch = {m: (q, opp, anc, fr) for m, q, opp, anc, fr in con.execute("SELECT mid, qid, opponent, anchor, frontier FROM schedule")}
    V = defaultdict(dict)
    for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    ens = [(m, sch[m], V[m]["ensemble"]) for m in V if "ensemble" in V[m]]
    dec = [(m, s, w) for m, s, w in ens if cot[s[0]][1] != K[s[0]][s[1]]]
    acc = sum(1 for m, s, w in dec if w == (NEW if cot[s[0]][1] else s[1])) / max(1, len(dec))
    print("=== ARENA-13 arm A (ensemble reference): %d verdicts, %d key-decidable ===" % (len(ens), len(dec)))
    print("  (3) key-decidable accuracy on the new pairs %.3f -> %s" % (acc, "OK" if acc >= 0.85 else "FAIL"))
    # 13-model board: existing pairwise verdicts from ARENA-V2 + the new pairs
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    old = [r for r in sj.open_cache().execute("SELECT model_a, model_b, winner, invalid FROM verdicts") if not r[3]]
    models = sorted(set(p8.ARENA12) | {NEW})
    rows = [(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, w, _ in old]
    rows += [(NEW, s[1], 0.5 if w == "TIE" else (1.0 if w == NEW else 0.0), 1.0) for m, s, w in ens]
    th = jf.board_from(rows, models)
    acck, _ = jf.gt_and_lengths(set(p8.ARENA12))
    acck[NEW] = sum(cot[q][1] for q in cot if q in pool) / max(1, sum(1 for q in cot if q in pool))
    order = sorted(models, key=lambda m: -th[m]); rank = order.index(NEW) + 1
    krank = sorted(models, key=lambda m: -acck[m]).index(NEW) + 1
    print("\n  13-model board (existing verdicts + the new pairs):")
    for i, m in enumerate(order[:6], 1): print("    %d. %-34s theta %+.3f | key %.3f%s" % (i, m, th[m], acck[m], "   <- new" if m == NEW else ""))
    print("  (1) the new contestant places %d (key rank %d) -> %s" % (rank, krank, "OK" if rank in (2, 3) else "FAIL"))
    th12 = jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, w, _ in old], sorted(p8.ARENA12))
    o12 = sorted(p8.ARENA12, key=lambda m: -th12[m]); o13 = [m for m in order if m != NEW]
    pos = {m: i for i, m in enumerate(o13)}
    c = d = 0
    for i in range(len(o12)):
        for j in range(i + 1, len(o12)):
            s = (pos[o12[i]] - pos[o12[j]])
            c += s < 0; d += s > 0
    tau = (c - d) / max(1, c + d)
    print("  (2) the 12 keep their order, Kendall tau %.3f -> %s" % (tau, "OK" if tau >= 0.90 else "FAIL"))
    # (4) self-preference on the shared frontier matches
    both = [m for m in V if "ensemble" in V[m] and "selfref" in V[m]]
    we = sum(1 for m in both if V[m]["ensemble"] == NEW); ws = sum(1 for m in both if V[m]["selfref"] == NEW)
    b = sum(1 for m in both if V[m]["selfref"] == NEW and V[m]["ensemble"] != NEW)
    c_ = sum(1 for m in both if V[m]["ensemble"] == NEW and V[m]["selfref"] != NEW)
    print("\n=== arm B (self-reference), %d shared frontier matches ===" % len(both))
    print("  the new contestant's win rate: ensemble reference %.3f | its OWN reference %.3f (%+.3f)"
          % (we / max(1, len(both)), ws / max(1, len(both)), (ws - we) / max(1, len(both))))
    print("  discordant self-only %d : ensemble-only %d | McNemar p=%.4g" % (b, c_, p8.mcn(b, c_)))
    print("  (4) SELF-PREFERENCE higher with its own reference at p<0.05 -> %s"
          % ("CONFIRMED" if (ws > we and p8.mcn(b, c_) < 0.05) else "not confirmed"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", action="store_true"); ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.schedule: build()
    elif a.judge: build(); judge(a.pilot, a.workers)
    elif a.analyze: analyze()
