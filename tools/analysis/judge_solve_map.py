"""S1 — judge solve-rate map (docs/s_l_series_registration.md, registered before any call).

Each judge answers, without traces, every distinct reserved question judged in x12 MAIN
(2,812). One call per question; correctness vs the key. Per-anchor accuracy gives the
CEILING MAP (judge minus contestant accuracy) and the registered correlations.

  python tools/analysis/judge_solve_map.py --judge mistral|grok|grok-reasoning [--workers N] [--pilot N]
  python tools/analysis/judge_solve_map.py --analyze
"""
import os, sys, re, json, time, math, csv, random, sqlite3, argparse, threading, urllib.request, urllib.error
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj

JUDGES = {"mistral": ("Mistral-Large-3", "AZURE_AI_API_KEY"),
          "grok": ("grok-4-1-fast-non-reasoning", "AZURE_GROK_API_KEY"),
          "grok-reasoning": ("grok-4-1-fast-reasoning", "AZURE_GROK_API_KEY")}
OUT_DIR = os.path.join(ROOT, "experiment_results", "judge_solve")
ARENA12 = ["Llama-2-13b-hf", "Llama-2-7b-hf", "Meta-Llama-3_1-70B-Instruct", "Meta-Llama-3_1-8B", "Qwen1.5-72B-Chat",
           "Yi-6b-Chat", "arx_0314", "c4ai-command-r-v01", "deepseek-chat-v2_5", "gemini-3.1-pro_5-shots",
           "gpt-4o-2024-08-06", "iask_pro"]
TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]
SYSTEM = ("You are answering an expert-level multiple-choice question. Reason briefly if needed, then output "
          "ONLY a JSON object of the form {\"answer\": \"<letter>\"} with the letter of the single best option.")
ENDPOINT = KEY = None


def load_env(key_name):
    global ENDPOINT, KEY
    kv = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            kv[k] = v
    ENDPOINT = kv["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    KEY = kv[key_name]


def questions():
    x = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
    qids = sorted({r[0] for r in x.execute("SELECT DISTINCT eval_question_id FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))})
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = {}
    for q in qids:
        # a campaign model's row: its text/options are verified against the HF rows (F2 data note)
        r = ev.execute("SELECT question_text, options_json, gt_answer FROM eval_results WHERE question_id=? AND model_name='gpt-4o-2024-08-06'", (q,)).fetchone()
        if r is None:
            r = ev.execute("SELECT question_text, options_json, gt_answer FROM eval_results WHERE question_id=? AND model_name!='Meta-Llama-3-70B-Instruct'", (q,)).fetchone()
        if r is None:
            continue
        opts = json.loads(r[1]) if r[1] else []
        out[q] = (r[0], opts, (r[2] or "").strip().upper()[:1])
    return out


def user_prompt(qtext, opts):
    letters = "ABCDEFGHIJ"
    return qtext + "\n\nOptions:\n" + "\n".join("(%s) %s" % (letters[i], o) for i, o in enumerate(opts))


def call(model, system, user, max_tokens=4096, retries=6):
    body = json.dumps({"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={"Content-Type": "application/json", "api-key": KEY})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                p = json.loads(r.read().decode("utf-8"))
            return (p["choices"][0]["message"].get("content") or ""), (p.get("usage") or {}).get("completion_tokens"), time.time() - t0
        except urllib.error.HTTPError as e:
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
    raise RuntimeError("unreachable")


def parse_answer(text):
    t = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = re.search(r'"answer"\s*:\s*"?\(?([A-J])\)?"?', t, re.I)
    if m:
        return m.group(1).upper()
    m = re.findall(r"\(([A-J])\)", t)
    return m[-1].upper() if m else ""


def open_cache(judge):
    os.makedirs(OUT_DIR, exist_ok=True)
    con = sqlite3.connect(os.path.join(OUT_DIR, "%s.db" % judge))
    con.execute("CREATE TABLE IF NOT EXISTS answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT, tokens INTEGER, latency REAL, ts REAL)")
    con.commit()
    return con


def run(judge, workers, pilot):
    model, key_name = JUDGES[judge]
    load_env(key_name)
    qs = questions()
    cache = open_cache(judge)
    done = {r[0] for r in cache.execute("SELECT question_id FROM answers")}
    todo = [q for q in sorted(qs) if q not in done]
    if pilot:
        todo = todo[:pilot]
    print("judge=%s model=%s | questions %d | cached %d | to solve %d | workers %d" % (judge, model, len(qs), len(qs) - len(todo), len(todo), workers), flush=True)
    lock = threading.Lock()
    ok = err = correct = 0

    def one(q):
        qtext, opts, gt = qs[q]
        raw, tok, lat = call(model, SYSTEM, user_prompt(qtext, opts))
        a = parse_answer(raw)
        return (q, a, gt, int(a == gt and a != ""), raw, tok, lat, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, q): q for q in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1
                print("  ERROR q %s: %s" % (futs[f], str(e)[:140]), flush=True)
                continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO answers VALUES (?,?,?,?,?,?,?,?)", row)
                cache.commit()
            ok += 1; correct += row[3]
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, err %d) | running accuracy %.3f" % (i, len(todo), ok, err, correct / max(1, ok)), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)


# ── analysis (registered) ──────────────────────────────────────────────────────
def spearman_perm(xs, ys, nperm=20000, seed=42):
    rho = rj.spearman(xs, ys)
    rng = random.Random(seed)
    ys2 = list(ys)
    cnt = 0
    for _ in range(nperm):
        rng.shuffle(ys2)
        r = rj.spearman(xs, ys2)
        if (rho < 0 and r <= rho) or (rho >= 0 and r >= rho):
            cnt += 1
    return rho, (cnt + 1) / (nperm + 1)


def analyze():
    nodes = rj.load_nodes()
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}

    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    best = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="", encoding="utf-8")):
        q = int(r["question_id"]); w = float(r["weight"].replace(",", "."))
        if q not in best or w > best[q][0]:
            best[q] = (w, r["leaf_id"])
    q_anchor = {q: anchor_of(l) for q, (_, l) in best.items()}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    solve = {}
    for judge in JUDGES:
        p = os.path.join(OUT_DIR, "%s.db" % judge)
        if os.path.exists(p):
            c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
            solve[judge] = {r[0]: r[1] for r in c.execute("SELECT question_id, correct FROM answers WHERE answer != ''")}
    if not solve:
        print("no solve caches"); return
    qs = sorted(set.intersection(*[set(v) for v in solve.values()]))
    anchors = sorted({q_anchor[q] for q in qs if q in q_anchor})
    print("=== S1 ceiling map: %d questions with all %d judges ===" % (len(qs), len(solve)))
    print("%-18s %5s | %s | contestants(12) top-4" % ("anchor", "n", " ".join("%14s" % j for j in solve)))
    acc_j = {j: {} for j in solve}
    cont = {}
    for a in anchors:
        sub = [q for q in qs if q_anchor.get(q) == a]
        for j in solve:
            acc_j[j][a] = sum(solve[j][q] for q in sub) / len(sub)
        c12 = [G.get((q, m)) for q in sub for m in ARENA12 if (q, m) in G]
        c4 = [G.get((q, m)) for q in sub for m in TOP4 if (q, m) in G]
        cont[a] = (sum(c12) / len(c12), sum(c4) / len(c4))
        print("%-18s %5d | %s | %.3f %.3f" % (a[:18], len(sub), " ".join("%14.3f" % acc_j[j][a] for j in solve), cont[a][0], cont[a][1]))
    tot = {j: sum(solve[j][q] for q in qs) / len(qs) for j in solve}
    print("%-18s %5d | %s | overall" % ("ALL", len(qs), " ".join("%14.3f" % tot[j] for j in solve)))
    if "mistral" in solve:
        below = sum(1 for a in anchors if acc_j["mistral"][a] < cont[a][1])
        print("  Mistral below the top-4 contestants' accuracy in %d/%d anchors" % (below, len(anchors)))
    # PRIMARY: Mistral rubric gain per anchor vs Mistral solve accuracy
    if "mistral" in solve:
        x12 = sqlite3.connect("file:%s?mode=ro" % rj.X12_DB, uri=True)
        cell = {r[0]: (int(r[1]), r[2], r[3], "TIE" if r[5] else r[4]) for r in x12.execute(
            "SELECT id, eval_question_id, model_a, model_b, winner, is_tie FROM match_history WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}
        rc = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_contrast.db"), uri=True)
        gen = {r[0]: r[1] for r in rc.execute("SELECT match_id, winner FROM verdicts WHERE judge='mistral' AND rubric='generic' AND invalid=0")}
        gain = defaultdict(lambda: [0, 0, 0])
        for mid, gw in gen.items():
            rec = cell.get(mid)
            if rec is None: continue
            q, ma, mb, cw = rec
            ca, cb = G.get((q, ma)), G.get((q, mb))
            if ca is None or cb is None or ca == cb: continue
            dw = ma if ca else mb
            a = q_anchor.get(q)
            if a is None: continue
            g = gain[a]; g[0] += 1; g[1] += (cw == dw); g[2] += (gw == dw)
        xs, ys, labels = [], [], []
        for a in anchors:
            if a in gain and gain[a][0] >= 20:
                xs.append(acc_j["mistral"][a]); ys.append((gain[a][1] - gain[a][2]) / gain[a][0]); labels.append(a)
        rho, p = spearman_perm(xs, ys)
        print("\n  REGISTERED PRIMARY: Mistral rubric gain (cell − generic, key-decidable) vs Mistral solve accuracy over %d anchors: rho = %+.3f, perm p = %.4f -> %s"
              % (len(xs), rho, p, "PASS" if (rho < 0 and p < 0.05) else "FAIL"))
        for a, x, y in sorted(zip(labels, xs, ys), key=lambda t: t[1]):
            print("     %-18s solve %.3f  rubric gain %+.3f" % (a[:18], x, y))
    # SECONDARY: J1 per-anchor gain vs solve gap
    if "mistral" in solve and "grok-reasoning" in solve:
        j1p = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_grok_4_1_fast_reasoning.db")
        if os.path.exists(j1p):
            j1 = sqlite3.connect("file:%s?mode=ro" % j1p, uri=True)
            g = defaultdict(lambda: [0, 0, 0])
            for mid, ma, mb, q, mw, rw, inv in j1.execute("SELECT match_id, model_a, model_b, qid, mistral_winner, r1_winner, r1_invalid FROM verdicts"):
                if inv: continue
                ca, cb = G.get((q, ma)), G.get((q, mb))
                if ca is None or cb is None or ca == cb: continue
                dw = ma if ca else mb
                a = q_anchor.get(q)
                if a is None: continue
                g[a][0] += 1; g[a][1] += (rw == dw); g[a][2] += (mw == dw)
            xs, ys = [], []
            for a in anchors:
                if a in g and g[a][0] >= 20:
                    xs.append(acc_j["grok-reasoning"][a] - acc_j["mistral"][a]); ys.append((g[a][1] - g[a][2]) / g[a][0])
            rho, p = spearman_perm(xs, ys)
            print("  SECONDARY: J1 accuracy gain per anchor vs solve-rate gap (reasoning − Mistral) over %d anchors: rho = %+.3f, perm p = %.4f -> %s"
                  % (len(xs), rho, p, "PASS" if (rho > 0 and p < 0.05) else "FAIL"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=list(JUDGES), default=None)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze or a.judge is None:
        analyze()
    else:
        run(a.judge, a.workers, a.pilot)
