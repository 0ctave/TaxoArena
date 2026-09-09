"""RUBRIC-P8 — cell vs generic rubric on the frozen tree's TRUE held-out pool p8a29
(docs/incident_reserved_pool_mismatch_2026-09-09.md; registered before any call).

  python tools/analysis/rubric_p8.py [--pilot N] [--workers N]
  python tools/analysis/rubric_p8.py --analyze
"""
import os, sys, re, json, time, math, struct, random, sqlite3, argparse, threading, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_value_contrast as rc

POOL = "p8a29d8f3ff75aa55"
N_MATCHES = 1000
SEED = 42
MODEL = "Mistral-Large-3"
ARENA12 = ["Llama-2-13b-hf", "Llama-2-7b-hf", "Meta-Llama-3_1-70B-Instruct", "Meta-Llama-3_1-8B", "Qwen1.5-72B-Chat",
           "Yi-6b-Chat", "arx_0314", "c4ai-command-r-v01", "deepseek-chat-v2_5", "gemini-3.1-pro_5-shots",
           "gpt-4o-2024-08-06", "iask_pro"]
DISCURSIVE = {"Philosophy", "History", "Psychology", "Biology", "Health", "Law", "Economics", "Business", "Other"}
OUT_DIR = os.path.join(ROOT, "experiment_results", "rubric_p8")
ENDPOINT = KEY = None


def load_env():
    global ENDPOINT, KEY
    kv = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1); kv[k] = v
    ENDPOINT = kv["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    KEY = kv["AZURE_AI_API_KEY"]


def call(system, user, retries=6):
    body = json.dumps({"model": MODEL, "max_tokens": rj.MAX_TOKENS,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={"Content-Type": "application/json", "api-key": KEY})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                p = json.loads(r.read().decode("utf-8"))
            return p["choices"][0]["message"].get("content") or ""
        except urllib.error.HTTPError as e:
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
    raise RuntimeError("unreachable")


def route_p8(nodes):
    """p8a29 question -> (leaf id, anchor label) by nearest leaf centroid on the 256-slice."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    qids = sorted(r[0] for r in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,)))
    text = {q: t for q, t in ev.execute("SELECT question_id, question_text FROM eval_results WHERE model_name='gpt-4o-2024-08-06'") if q in set(qids)}
    emb = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "embeddings_cache.db"), uri=True)
    want = set(text.values()); vec = {}
    for t, blob in emb.execute("SELECT query, vector FROM embeddings"):
        if t in want and isinstance(blob, bytes) and len(blob) % 4 == 0:
            v = np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)[:256]
            n = np.linalg.norm(v)
            if n > 0: vec[t] = v / n
    parent = {c: n["id"] for n in nodes.values() for c in n.get("childIds", [])}
    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1: n = nodes[parent[n["id"]]]
        return n["label"]
    leaves = [(n["id"], np.array(n["vmfMu"], dtype=np.float64)) for n in nodes.values() if not n.get("childIds")]
    M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu in leaves])
    out = {}
    for q in qids:
        t = text.get(q)
        if t in vec:
            i = int(np.argmax(M @ vec[t]))
            out[q] = (leaves[i][0], anchor(leaves[i][0]))
    return out


def sample_matches(routing):
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results") if m in ARENA12}
    rng = random.Random(SEED)
    by_anchor = defaultdict(list)
    for q, (leaf, anc) in routing.items():
        pairs = [(a, b) for i, a in enumerate(ARENA12) for b in ARENA12[i + 1:]
                 if (q, a) in G and (q, b) in G and G[(q, a)] != G[(q, b)]]
        if pairs:
            a, b = rng.choice(pairs)
            if rng.random() < 0.5: a, b = b, a
            by_anchor[anc].append((q, a, b, leaf, anc))
    anchors = sorted(by_anchor)
    per = N_MATCHES // len(anchors)
    sample = []
    for anc in anchors:
        lst = by_anchor[anc]; rng.shuffle(lst); sample += lst[:per]
    rng.shuffle(sample)
    return sample


def open_cache():
    os.makedirs(OUT_DIR, exist_ok=True)
    con = sqlite3.connect(os.path.join(OUT_DIR, "mistral.db"))
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (qid INTEGER, model_a TEXT, model_b TEXT, arm TEXT, leaf TEXT, anchor TEXT, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (qid, model_a, model_b, arm))")
    con.commit()
    return con


def run(pilot, workers):
    load_env()
    nodes = rj.load_nodes()
    routing = route_p8(nodes)
    sample = sample_matches(routing)
    if pilot: sample = sample[:pilot]
    evals = rj.load_eval_rows([q for q, *_ in sample], set(ARENA12))
    generic = rc.build_generic_system_prompt()
    cache = open_cache()
    done = {(r[0], r[1], r[2], r[3]) for r in cache.execute("SELECT qid, model_a, model_b, arm FROM verdicts")}
    todo = [(m, arm) for m in sample for arm in ("cell", "generic") if (m[0], m[1], m[2], arm) not in done]
    print("RUBRIC-P8: routed %d p8a29 questions | sample %d matches | jobs %d (%d calls) | workers %d" % (len(routing), len(sample), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = 0

    def one(m, arm):
        q, a, b, leaf, anc = m
        ra, rb = evals[(q, a)], evals[(q, b)]
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = rj.build_system_prompt(nodes[leaf]) if arm == "cell" else generic
        raw1 = call(system, rj.build_user_prompt(ra[0], ta, tb)); raw2 = call(system, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (q, a, b, arm, leaf, anc, v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m, arm): (m, arm) for m, arm in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0][:3], str(e)[:120]), flush=True); continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 14), row); cache.commit()
            ok += 1
            if i % 50 == 0 or i == len(todo):
                print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)


def mcn(b, c):
    n = b + c
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) * 0.5 ** n for i in range(min(b, c) + 1)))


def analyze():
    cache = open_cache()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results") if m in ARENA12}
    rows = defaultdict(dict)
    for q, a, b, arm, leaf, anc, w, inv in cache.execute("SELECT qid, model_a, model_b, arm, leaf, anchor, winner, invalid FROM verdicts"):
        if not inv:
            rows[(q, a, b)][arm] = (w, anc)
    full = {k: v for k, v in rows.items() if "cell" in v and "generic" in v}
    def stats(keys):
        n = b = c = oc = og = 0
        for k in keys:
            q, a, bb = k; d = a if G[(q, a)] else bb
            cw, gw = full[k]["cell"][0], full[k]["generic"][0]
            n += 1; A = cw == d; B = gw == d; oc += A; og += B; b += (A and not B); c += (B and not A)
        return n, oc / max(1, n), og / max(1, n), b, c, mcn(b, c)
    n, pc, pg, b, c, p = stats(list(full))
    print("=== RUBRIC-P8: cell vs generic on p8a29 (frozen tree's true held-out pool), Mistral, %d complete matches ===" % n)
    print("  correct-verdict rate: cell %.3f vs generic %.3f (%+.3f) | discordant %d:%d | McNemar p=%.4f -> %s (REGISTERED PRIMARY)"
          % (pc, pg, pc - pg, b, c, p, "PASS" if (pc > pg and p < 0.05) else "FAIL"))
    disc = [k for k in full if full[k]["cell"][1] in DISCURSIVE]; quant = [k for k in full if full[k]["cell"][1] not in DISCURSIVE]
    for name, keys in (("discursive anchors", disc), ("quantitative anchors", quant)):
        n, pc, pg, b, c, p = stats(keys)
        print("  %-21s n=%4d | cell %.3f vs generic %.3f (%+.3f) | %d:%d p=%.4f" % (name, n, pc, pg, pc - pg, b, c, p))
    gd = stats(disc)[1] - stats(disc)[2]; gq = stats(quant)[1] - stats(quant)[2]
    print("  SECONDARY (discursive gain > quantitative gain): %s" % ("PASS" if gd > gq else "FAIL"))
    by = defaultdict(list)
    for k in full: by[full[k]["cell"][1]].append(k)
    for anc in sorted(by, key=lambda a: -(stats(by[a])[1] - stats(by[a])[2])):
        n, pc, pg, b, c, p = stats(by[anc])
        print("     %-18s n=%3d  gain %+.3f  (%d:%d)" % (anc[:18], n, pc - pg, b, c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
    else:
        run(a.pilot, a.workers); analyze()
