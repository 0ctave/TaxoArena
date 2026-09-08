"""J1 — judge-strength ceiling test: re-judge the R3 stratified x12 sample with a
REASONING-class judge, byte-identical prompts (docs/judge_improvement_proposals.md, J1;
criteria frozen at 7a4391a; launch parameters recorded there before the first call).

Judge: deepseek-ai/DeepSeek-R1-0528 via the Hugging Face inference router (provider-routed;
the provider and inference id are recorded per call). No reasoning model is deployed on the
Foundry resource that serves Mistral-Large-3 / grok; the Gemini key is not API-registered.
Family disclosure: deepseek-chat-v2_5 is a mid-tier CONTESTANT; no top-4 model is a
DeepSeek model, so the registered primary (top-cluster key-decidable accuracy) is not
self-preference-confounded; the full-board secondary is reported with that caveat.

Sample: rejudge_grok.sample_matches() — the same 1,980 matches R3 judged (seed 42,
100 per top-cluster pair + the rest spread), so Mistral / grok / R1 are all paired.
Prompts: rejudge_grok's v1 templates extracted from TaxonomyArenaService.kt at runtime
(embedded comment included, as in every re-judge comparison so far). Reasoning text
(<think>...</think>) is stripped before the JSON verdict is parsed.

    python tools/analysis/rejudge_reasoning.py --pilot 12
    python tools/analysis/rejudge_reasoning.py --workers 16
    python tools/analysis/rejudge_reasoning.py --analyze
"""
import os, sys, re, json, time, math, sqlite3, argparse, threading, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj

JUDGE_MODEL = "deepseek-ai/DeepSeek-R1-0528"
ROUTER = "https://router.huggingface.co/v1/chat/completions"
CACHE_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_r1.db")
MAX_TOKENS = 8192
TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]
TOKEN = None


def load_env():
    global TOKEN
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if line.startswith("HUGGINGFACE_TOKEN="):
            TOKEN = line.split("=", 1)[1]
    assert TOKEN, "HUGGINGFACE_TOKEN missing from .env"


THINK = re.compile(r"<think>.*?</think>", re.S)


def call_judge(system, user, retries=6):
    body = json.dumps({"model": JUDGE_MODEL, "max_tokens": MAX_TOKENS,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(ROUTER, data=body, method="POST", headers={
            "Content-Type": "application/json", "Authorization": "Bearer " + TOKEN})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                provider = r.headers.get("x-inference-provider", "")
                payload = json.loads(r.read().decode("utf-8"))
            content = payload["choices"][0]["message"].get("content") or ""
            usage = payload.get("usage") or {}
            return content, provider, usage.get("completion_tokens"), time.time() - t0
        except urllib.error.HTTPError as e:
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
    raise RuntimeError("unreachable")


def strip_think(text):
    return THINK.sub("", text).strip()


def open_cache():
    con = sqlite3.connect(CACHE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER,
        mistral_winner TEXT,
        vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL,
        r1_winner TEXT, r1_flip INTEGER, r1_invalid INTEGER,
        raw1 TEXT, raw2 TEXT, provider1 TEXT, provider2 TEXT,
        tok1 INTEGER, tok2 INTEGER, lat1 REAL, lat2 REAL, ts REAL)""")
    con.commit()
    return con


def judge_one(match, nodes, evals):
    mid, qid, ma, mb, nid, winner, is_tie = match
    qid = int(qid)
    ra, rb = evals.get((qid, ma)), evals.get((qid, mb))
    if ra is None or rb is None:
        return None
    qtext = ra[0]
    ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
    system = rj.build_system_prompt(nodes[nid])
    raw1, p1, k1, l1 = call_judge(system, rj.build_user_prompt(qtext, ta, tb))
    raw2, p2, k2, l2 = call_judge(system, rj.build_user_prompt(qtext, tb, ta))
    v1, c1 = rj.parse_judge(strip_think(raw1))
    v2, c2 = rj.parse_judge(strip_think(raw2))
    w, flip, invalid = rj.combine_orders(v1, v2)
    w_name = {"Model A": ma, "Model B": mb}.get(w, w)
    return (mid, ma, mb, nid, qid, "TIE" if is_tie else winner, v1, v2, c1, c2,
            w_name, int(flip), int(invalid), raw1, raw2, p1, p2, k1, k2, l1, l2, time.time())


def run(pilot=None, workers=16):
    load_env()
    nodes = rj.load_nodes()
    sample = rj.sample_matches()
    if pilot:
        sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    print("sample %d | cached %d | to judge %d (%d calls) | workers %d"
          % (len(sample), len(sample) - len(todo), len(todo), 2 * len(todo), workers), flush=True)
    if not todo:
        return
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    lock = threading.Lock()
    ok = skip = err = 0
    toks, lats = [], []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(judge_one, m, nodes, evals): m for m in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                row = fut.result()
            except Exception as e:
                err += 1
                print("  ERROR match %s: %s" % (futs[fut][0], str(e)[:160]), flush=True)
                continue
            if row is None:
                skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 22), row)
                cache.commit()
            ok += 1
            toks += [t for t in (row[17], row[18]) if t]
            lats += [row[19], row[20]]
            if i % 20 == 0 or i == len(todo):
                print("  %d/%d (ok %d, skip %d, err %d) | mean tokens %.0f | mean latency %.0fs"
                      % (i, len(todo), ok, skip, err, sum(toks) / max(1, len(toks)), sum(lats) / max(1, len(lats))), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


# ── Analysis (J1 registered) ───────────────────────────────────────────────────
def gt_correct():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    return {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * sum(math.comb(n, i) * 0.5 ** n for i in range(k + 1)))


def analyze():
    cache = open_cache()
    rows = cache.execute("SELECT match_id, model_a, model_b, qid, mistral_winner, r1_winner, r1_flip, r1_invalid, "
                         "provider1, tok1, tok2 FROM verdicts").fetchall()
    if not rows:
        print("no verdicts cached"); return
    grok = {}
    if os.path.exists(rj.CACHE_DB):
        g = sqlite3.connect("file:%s?mode=ro" % rj.CACHE_DB, uri=True)
        grok = {r[0]: r[1] for r in g.execute("SELECT match_id, grok_winner FROM verdicts WHERE grok_invalid=0")}
    G = gt_correct()
    valid = [r for r in rows if not r[7]]
    print("=== J1: %s vs Mistral-Large-3 (paired, same matches, same prompts) ===" % JUDGE_MODEL)
    print("judged %d | invalid %d | flips %.1f%% | ties R1 %.1f%% vs Mistral %.1f%% | providers %s | mean completion tokens %.0f"
          % (len(valid), len(rows) - len(valid), 100 * sum(r[6] for r in valid) / len(valid),
             100 * sum(r[5] == "TIE" for r in valid) / len(valid), 100 * sum(r[4] == "TIE" for r in valid) / len(valid),
             sorted({r[8] for r in valid}), sum((r[9] or 0) + (r[10] or 0) for r in valid) / (2 * len(valid))))

    def decidable(r):
        ca, cb = G.get((r[3], r[1])), G.get((r[3], r[2]))
        if ca is None or cb is None or ca == cb:
            return None
        return r[1] if ca else r[2]

    for label, subset in (("TOP-CLUSTER pairs (REGISTERED PRIMARY)", [r for r in valid if r[1] in TOP4 and r[2] in TOP4]),
                          ("all pairs", valid)):
        dec = [(r, decidable(r)) for r in subset]
        dec = [(r, d) for r, d in dec if d is not None]
        m_ok = sum(r[4] == d for r, d in dec); r_ok = sum(r[5] == d for r, d in dec)
        b = sum(1 for r, d in dec if r[5] == d and r[4] != d); c = sum(1 for r, d in dec if r[4] == d and r[5] != d)
        p = mcnemar_p(b, c)
        line = "  %s: n_dec=%d | correct-verdict rate (ties wrong): R1 %.3f vs Mistral %.3f (%+.3f) | discordant R1-only %d vs Mistral-only %d | McNemar p=%.4f" % (
            label, len(dec), r_ok / max(1, len(dec)), m_ok / max(1, len(dec)), (r_ok - m_ok) / max(1, len(dec)), b, c, p)
        if grok:
            gd = [(r, d) for r, d in dec if r[0] in grok]
            if gd:
                line += " | grok %.3f (n=%d)" % (sum(grok[r[0]] == d for r, d in gd) / len(gd), len(gd))
        print(line)
        if "PRIMARY" in label:
            print("  REGISTERED J1 PRIMARY (R1 > Mistral on top-cluster key-decidable, p < 0.05): %s"
                  % ("PASS" if (r_ok > m_ok and p < 0.05) else "FAIL"))
    # secondary: top-4 BT order on the top-cluster matches, violations vs GT (key accuracy on frozen pool)
    import judge_free_tests as jf
    acc, _ = jf.gt_and_lengths(set(TOP4))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    top = [r for r in valid if r[1] in TOP4 and r[2] in TOP4]
    for name, col in (("Mistral", 4), ("R1", 5)):
        th = jf.board_from(((r[1], r[2], 0.5 if r[col] == "TIE" else (1.0 if r[col] == r[1] else 0.0), 1.0) for r in top), TOP4)
        o, pv, av = jf.violations(th, gt_order)
        print("  top-4 board [%s] on %d matches: %s (pairwise violations %d, GT %s)" % (name, len(top), " > ".join(o), pv, " > ".join(gt_order)))
    if grok:
        th = jf.board_from(((r[1], r[2], 0.5 if grok[r[0]] == "TIE" else (1.0 if grok[r[0]] == r[1] else 0.0), 1.0) for r in top if r[0] in grok), TOP4)
        o, pv, _ = jf.violations(th, gt_order)
        print("  top-4 board [grok]: %s (violations %d)" % (" > ".join(o), pv))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
    else:
        run(pilot=a.pilot, workers=a.workers)
        analyze()
