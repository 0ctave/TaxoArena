"""R3 second-judge robustness check: grok-4-1-fast-non-reasoning re-judges a
stratified sample of the x12 run's matches.

WHY (2026-09-06). The x12 leaderboard and interaction claims rest on one judge
(Mistral-Large-3). The predictable reviewer attack is circularity: an LLM ranking
LLMs. This script re-judges a sample of the same (query, pair, cell) slots with a
judge from a family absent from the experiment (xAI; deployed on the same Azure
Foundry resource, sold-direct so it clears the CSP wall), then reports verdict
agreement and rank stability.

PROMPT FIDELITY. The judge must see byte-identical prompts to the ones Mistral saw,
or judge identity is confounded with prompt drift. The system/user templates are
therefore EXTRACTED FROM TaxonomyArenaService.kt AT RUNTIME (raw strings between
'return \"\"\"' and '\"\"\".trimIndent()', with Kotlin trimIndent semantics applied here) —
including the code-comment block that has shipped inside the system prompt since
2026-07-27 (present in every published run; do not "fix" it before this comparison).
The Azure structured-output path is replicated too: schema instruction appended to
the system prompt (with its confidence-renders-as-<string> quirk), two presentation
orders, flip -> TIE, INVALID rules, RESOLVED answer injection, envelope unwrap and
blank-trace fallbacks ported from getRobustTrace.

SAMPLING. Seeded (42), stratified: up to TOP_PER_PAIR matches from each of the six
top-cluster pairs (iask_pro, gemini, gpt-4o, arx — the region where the x12 anomaly
lives), the rest filled uniformly per remaining pair to TOTAL. Deterministic given
the db.

DURABILITY. Every verdict lands in rejudge_grok.db immediately; reruns skip
completed matches, so the run can be stopped and restarted at any time without
re-paying judge calls.

Usage:
  python tools/analysis/rejudge_grok.py --pilot 12     # smoke test
  python tools/analysis/rejudge_grok.py                # full sample (TOTAL)
  python tools/analysis/rejudge_grok.py --analyze      # report only, no calls
"""
import argparse
import json
import math
import os
import random
import re
import sqlite3
import sys
import threading
import time
import urllib.request
import urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
X12_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "ratings_x12.db")
CACHE_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rejudge_grok.db")
EVAL_DB = os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db")
SNAP_DB = os.path.join(ROOT, "snapshots_frozen.db")
ARENA_KT = os.path.join(ROOT, "src", "main", "kotlin", "taxonomy", "service", "TaxonomyArenaService.kt")
SNAP_ID = "20260727_042523_Headless_Run_Auto_ge"
SNAP_MAIN = SNAP_ID + "_MAIN"

JUDGE_MODEL = "grok-4-1-fast-non-reasoning"
TOP_CLUSTER = {"iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"}
TOP_PER_PAIR = 100
TOTAL = 2000
CONCURRENCY = 12
MAX_TOKENS = 2048
SEED = 42

# Ported verbatim from ArcTaxonomyLLMClient.buildAzureSchemaInstruction applied to
# judgeSchema: string properties carry their description; the number property's cast
# to JsonStringSchema fails, so it renders as <string>. Property order = declaration.
SCHEMA_INSTRUCTION = (
    "You MUST respond with a single valid JSON object and nothing else. "
    'Required shape: { "critique_a": <Critique of Model A\'s response against the rubric>, '
    '"critique_b": <Critique of Model B\'s response against the rubric>, '
    '"comparison": <The decisive difference in reasoning quality between A and B>, '
    '"winner": <Model A, Model B, or TIE>, "confidence": <string> }'
)


# ── Kotlin template extraction ─────────────────────────────────────────────────

def kotlin_trim_indent(s):
    lines = s.split("\n")
    if lines and lines[0].strip() == "":
        lines = lines[1:]
    if lines and lines[-1].strip() == "":
        lines = lines[:-1]
    indents = [len(l) - len(l.lstrip(" ")) for l in lines if l.strip()]
    common = min(indents) if indents else 0
    return "\n".join(l[common:] if l.strip() else l for l in lines)


def extract_template(src, fun_name):
    i = src.index("private fun " + fun_name)
    start = src.index('return """', i) + len('return """')
    end = src.index('""".trimIndent()', start)
    return kotlin_trim_indent(src[start:end])


_src = open(ARENA_KT, encoding="utf-8").read()
SYSTEM_TEMPLATE = extract_template(_src, "buildJudgeSystemPrompt")   # $systemPrompt / $rubric
USER_TEMPLATE = extract_template(_src, "buildJudgeUserPrompt")       # $query / $traceA / $traceB
assert "$systemPrompt" in SYSTEM_TEMPLATE and "$rubric" in SYSTEM_TEMPLATE
assert all(v in USER_TEMPLATE for v in ("$query", "$traceA", "$traceB"))
assert "MEASURED: this instruction does not work" in SYSTEM_TEMPLATE, \
    "embedded comment missing — template extraction no longer matches the shipped prompt"


def build_system_prompt(node):
    sp = node.get("judgePrompt") or (
        "You are an expert academic evaluator in the domain: %s." % (node.get("label") or "General Science"))
    rubric = node.get("judgeRubric") or "Grade the response based on domain correctness, precision, and logical reasoning."
    base = SYSTEM_TEMPLATE.replace("$systemPrompt", sp).replace("$rubric", rubric)
    # Azure structured path: ArcTaxonomyLLMClient appends the schema instruction.
    return base + "\n\n" + SCHEMA_INSTRUCTION


def build_user_prompt(query, trace_a, trace_b):
    return (USER_TEMPLATE.replace("$query", query)
            .replace("$traceA", trace_a).replace("$traceB", trace_b))


# ── Trace preparation (getRobustTrace port) ────────────────────────────────────

def unwrap_envelope(output):
    t = output.lstrip()
    if not t.startswith("{"):
        return output
    try:
        obj = json.loads(t)
    except Exception:
        return output
    resp = obj.get("response") if isinstance(obj, dict) else None
    return resp if isinstance(resp, str) and resp.strip() else output


def robust_trace(model_output, pred, options):
    out = unwrap_envelope(model_output) if model_output else None
    if out and out.strip():
        return maybe_resolve(out, pred, options)
    p = (pred or "").strip().upper()
    if not p:
        return "The model did not provide a prediction."
    c = p[0]
    if "A" <= c <= "J":
        idx = ord(c) - ord("A")
        if 0 <= idx < len(options):
            return 'The model selected option %s: "%s".' % (c, options[idx])
    return 'The model predicted: "%s".' % p


def maybe_resolve(trace, pred, options):
    """RESOLVED mode injection (TaxonomyBenchmarkService.maybeResolveSelection)."""
    p = (pred or "").strip().upper()
    if not p or not ("A" <= p[0] <= "J"):
        return trace
    idx = ord(p[0]) - ord("A")
    if not (0 <= idx < len(options)):
        return trace
    text = str(options[idx]).strip()
    if not text:
        return trace
    return "%s\n\n[This model's selected answer: (%s) %s]" % (trace, p[0], text)


# ── Verdict parsing (parseJudgeResponse port) ──────────────────────────────────

def parse_judge(response):
    clean = response.strip()
    winner, confidence = "INVALID", 0.0
    if "```json" in clean:
        extracted = clean.split("```json", 1)[1].split("```", 1)[0].strip()
    else:
        a, b = clean.find("{"), clean.rfind("}")
        extracted = clean[a:b + 1] if a != -1 and b > a else clean
    try:
        el = json.loads(extracted, strict=False)
        raw = str(el.get("winner", "INVALID")).strip().upper()
        winner = {"MODEL A": "Model A", "MODEL B": "Model B",
                  "TIE": "TIE", "DRAW": "TIE", "EQUAL": "TIE"}.get(raw, "INVALID")
        try:
            confidence = float(el.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
    except Exception:
        m = re.search(r'"winner"\s*:\s*"([^"]+)"', clean, re.I)
        if m:
            raw = m.group(1).strip().upper()
            winner = {"MODEL A": "Model A", "MODEL B": "Model B",
                      "TIE": "TIE", "DRAW": "TIE", "EQUAL": "TIE"}.get(raw, "INVALID")
        m = re.search(r'"confidence"\s*:\s*"?([0-9.]+)"?', clean)
        if m:
            try:
                confidence = float(m.group(1))
            except ValueError:
                pass
    return winner, confidence


def combine_orders(vote1_raw, vote2_raw):
    """TaxonomyArenaService combination: order 2 presents B first, so its vote inverts."""
    vote2 = {"Model A": "Model B", "Model B": "Model A"}.get(vote2_raw, vote2_raw)
    invalid = vote1_raw == "INVALID" or vote2 == "INVALID"
    flip = (not invalid) and vote1_raw != vote2
    winner = "INVALID" if invalid else ("TIE" if flip else vote1_raw)
    return winner, flip, invalid


# ── Judge call ─────────────────────────────────────────────────────────────────

ENDPOINT = None
API_KEY = None


def load_env():
    global ENDPOINT, API_KEY
    envp = os.path.join(ROOT, ".env")
    kv = {}
    for line in open(envp, encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            kv[k] = v
    ENDPOINT = kv["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    API_KEY = kv["AZURE_GROK_API_KEY"]


def call_judge(system, user, retries=5):
    body = json.dumps({
        "model": JUDGE_MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "max_tokens": MAX_TOKENS,
    }).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
            "Content-Type": "application/json", "api-key": API_KEY})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                payload = json.loads(r.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 2, 30))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 2, 30))
                continue
            raise
    raise RuntimeError("unreachable")


# ── Data loading ───────────────────────────────────────────────────────────────

def load_nodes():
    con = sqlite3.connect("file:%s?mode=ro" % SNAP_DB, uri=True)
    g = json.loads(con.execute("SELECT graph FROM snapshots WHERE id=?", (SNAP_ID,)).fetchone()[0])
    nodes = g["nodes"]
    out = {}
    for n in (nodes.values() if isinstance(nodes, dict) else nodes):
        out[n["id"]] = n
    con.close()
    return out


def sample_matches():
    con = sqlite3.connect("file:%s?mode=ro" % X12_DB, uri=True)
    rows = con.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id, winner, is_tie "
        "FROM match_history WHERE condition='MAIN' AND snapshot_id=? ORDER BY id", (SNAP_MAIN,)).fetchall()
    con.close()
    by_pair = defaultdict(list)
    for r in rows:
        by_pair[(min(r[2], r[3]), max(r[2], r[3]))].append(r)
    rng = random.Random(SEED)
    sample = []
    top_pairs = [p for p in sorted(by_pair) if p[0] in TOP_CLUSTER and p[1] in TOP_CLUSTER]
    rest_pairs = [p for p in sorted(by_pair) if p not in set(top_pairs)]
    for p in top_pairs:
        pool = list(by_pair[p])
        rng.shuffle(pool)
        sample.extend(pool[:TOP_PER_PAIR])
    budget = TOTAL - len(sample)
    per_rest = max(1, budget // max(1, len(rest_pairs)))
    for p in rest_pairs:
        pool = list(by_pair[p])
        rng.shuffle(pool)
        sample.extend(pool[:per_rest])
    # Shuffle so a --pilot prefix spans all strata instead of one pair.
    rng.shuffle(sample)
    return sample


def load_eval_rows(question_ids, models):
    con = sqlite3.connect("file:%s?mode=ro" % EVAL_DB, uri=True)
    out = {}
    qlist = sorted(set(question_ids))
    for i in range(0, len(qlist), 500):
        chunk = qlist[i:i + 500]
        marks = ",".join("?" * len(chunk))
        for qid, m, qtext, opts, mo, pred in con.execute(
                "SELECT question_id, model_name, question_text, options_json, model_output, pred "
                "FROM eval_results WHERE question_id IN (%s)" % marks, chunk):
            if m in models:
                out[(qid, m)] = (qtext, json.loads(opts) if opts else [], mo, pred)
    con.close()
    return out


# ── Cache ──────────────────────────────────────────────────────────────────────

def open_cache():
    con = sqlite3.connect(CACHE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT,
        mistral_winner TEXT, mistral_tie INTEGER,
        vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL,
        grok_winner TEXT, grok_flip INTEGER, grok_invalid INTEGER,
        raw1 TEXT, raw2 TEXT, ts REAL)""")
    con.commit()
    return con


# ── Main run ───────────────────────────────────────────────────────────────────

def judge_one(match, nodes, evals):
    mid, qid, ma, mb, nid, winner, is_tie = match
    qid = int(qid)
    ra = evals.get((qid, ma))
    rb = evals.get((qid, mb))
    if ra is None or rb is None:
        return None  # missing trace (e.g. iask_pro coverage hole) — skip, recorded as absent
    qtext = ra[0]
    trace_a = robust_trace(ra[2], ra[3], ra[1])
    trace_b = robust_trace(rb[2], rb[3], rb[1])
    system = build_system_prompt(nodes[nid])
    raw1 = call_judge(system, build_user_prompt(qtext, trace_a, trace_b))
    raw2 = call_judge(system, build_user_prompt(qtext, trace_b, trace_a))
    v1, c1 = parse_judge(raw1)
    v2_raw, c2 = parse_judge(raw2)
    gw, flip, invalid = combine_orders(v1, v2_raw)
    # combine_orders speaks in presentation slots; the cache speaks in model names,
    # like match_history.winner does — translate before storing.
    gw_name = {"Model A": ma, "Model B": mb}.get(gw, gw)
    mistral_winner = "TIE" if is_tie else winner
    return (mid, ma, mb, nid, mistral_winner, int(is_tie),
            v1, v2_raw, c1, c2, gw_name, int(flip), int(invalid), raw1, raw2, time.time())


def run(pilot=None):
    load_env()
    nodes = load_nodes()
    sample = sample_matches()
    if pilot:
        sample = sample[:pilot]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts")}
    todo = [m for m in sample if m[0] not in done]
    print("sample %d matches | already cached %d | to judge %d (%d calls)"
          % (len(sample), len(sample) - len(todo), len(todo), 2 * len(todo)))
    if not todo:
        return
    evals = load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    lock = threading.Lock()
    n_ok = n_skip = n_err = 0
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {ex.submit(judge_one, m, nodes, evals): m for m in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                row = fut.result()
            except Exception as e:
                n_err += 1
                print("  ERROR match %s: %s" % (futs[fut][0], e))
                continue
            if row is None:
                n_skip += 1
                continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 16), row)
                cache.commit()
            n_ok += 1
            if i % 25 == 0 or i == len(todo):
                print("  %d/%d judged (ok %d, skipped %d, errors %d)" % (i, len(todo), n_ok, n_skip, n_err))
    print("done: ok %d, skipped(missing trace) %d, errors %d" % (n_ok, n_skip, n_err))


# ── Analysis ───────────────────────────────────────────────────────────────────

PRIOR = 0.5


def mm_fit(agg, models):
    idx = {m: i for i, m in enumerate(models)}
    M = len(models)
    W = [0.0] * M
    N = defaultdict(float)
    for (a, b), (wa, n) in agg.items():
        i, j = idx[a], idx[b]
        W[i] += wa + PRIOR
        W[j] += (n - wa) + PRIOR
        N[(i, j)] += n + 2 * PRIOR
        N[(j, i)] += n + 2 * PRIOR
    p = [1.0] * M
    for _ in range(2000):
        new = []
        for m in range(M):
            den = sum(N[(m, o)] / (p[m] + p[o]) for o in range(M) if N[(m, o)])
            new.append(W[m] / den if den > 0 else p[m])
        s = sum(new) / M
        new = [v / s for v in new]
        if max(abs(x - y) for x, y in zip(new, p)) < 1e-12:
            p = new
            break
        p = new
    th = [math.log(max(v, 1e-300)) for v in p]
    mean = sum(th) / M
    return {m: th[idx[m]] - mean for m in models}


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def analyze():
    cache = open_cache()
    rows = cache.execute(
        "SELECT model_a, model_b, mistral_winner, grok_winner, grok_flip, grok_invalid "
        "FROM verdicts").fetchall()
    if not rows:
        print("no cached verdicts yet")
        return
    valid = [r for r in rows if not r[5]]
    n = len(valid)
    agree = sum(1 for r in valid if r[2] == r[3])
    both_decisive = [r for r in valid if r[2] != "TIE" and r[3] != "TIE"]
    agree_dec = sum(1 for r in both_decisive if r[2] == r[3])
    tie_m = sum(1 for r in valid if r[2] == "TIE") / n
    tie_g = sum(1 for r in valid if r[3] == "TIE") / n
    flips = sum(r[4] for r in valid) / n

    def cluster(r):
        return "top" if r[0] in TOP_CLUSTER and r[1] in TOP_CLUSTER else "rest"

    print("=== R3 second judge: %s vs Mistral-Large-3 ===" % JUDGE_MODEL)
    print("matches judged: %d (INVALID excluded: %d)" % (n, len(rows) - n))
    print("raw verdict agreement (3-way): %.1f%%" % (100 * agree / n))
    print("decisive-only agreement:       %.1f%% (n=%d)" % (100 * agree_dec / max(1, len(both_decisive)), len(both_decisive)))
    print("tie rate: mistral %.1f%% | grok %.1f%% | grok flip rate %.1f%%" % (100 * tie_m, 100 * tie_g, 100 * flips))
    for cl in ("top", "rest"):
        sub = [r for r in valid if cluster(r) == cl]
        if sub:
            a = sum(1 for r in sub if r[2] == r[3])
            print("  %s cluster: agreement %.1f%% (n=%d)" % (cl, 100 * a / len(sub), len(sub)))

    # Rank stability: BT over the SAME sampled matches under each judge.
    models = sorted({r[0] for r in valid} | {r[1] for r in valid})
    def agg_for(col):
        agg = defaultdict(lambda: [0.0, 0.0])
        for r in valid:
            a, b = min(r[0], r[1]), max(r[0], r[1])
            w = r[col]
            rec = agg[(a, b)]
            rec[1] += 1
            if w == "TIE":
                rec[0] += 0.5
            elif w == a:
                rec[0] += 1.0
        return agg
    th_m = mm_fit(agg_for(2), models)
    th_g = mm_fit(agg_for(3), models)
    rho = spearman([th_m[m] for m in models], [th_g[m] for m in models])
    om = sorted(models, key=lambda m: -th_m[m])
    og = sorted(models, key=lambda m: -th_g[m])
    print("BT rank correlation between judges (same matches): rho = %.3f" % rho)
    print("order identical: %s" % ("YES" if om == og else "no"))
    print("%-30s %10s %10s" % ("model", "mistral", "grok"))
    for m in om:
        print("%-30s %+10.3f %+10.3f" % (m, th_m[m], th_g[m]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()
    if args.analyze:
        analyze()
    else:
        run(pilot=args.pilot)
        analyze()
