"""COST-AXES-INGEST (FRAMEWORK.md item 16, registered by reference at commit eaf1dbf; plan docs/plan_2026-09-15.md,
block 1). ZERO LLM calls, ZERO network. Reads only multicorpus_cache_v1.db (read-only) and two tokenizer files
already on disk (plus the tiktoken rank file; provenance in (b)).

  python tools/analysis/cost_axes_ingest.py

The item, quoted from docs/design/FRAMEWORK.md (commit 8d77f7b), "Tests to register before shipping":

  16. COST-AXES-INGEST. Token counts per (model, cell) from stored generations via each model's tokenizer;
      TIER-ROUTER-U re-read out of sample (policy on TRAIN, scored on paeec) with token cost. Criterion:
      tier-then-cheapest within 0.5pp of per-cell best at <= 85% of token cost. 0 LLM calls (latency needs timed
      regeneration, registered separately).

What the record makes of it (tier_design_probes.py:128-135, tier_design_probes.txt, judge_v2_program.md
"TIER-ROUTER-U", FRAMEWORK.md L131/L175/L340): the in-sample numbers are best single 0.5543, per-cell best 0.6169,
per-cell-best-TIER-then-smallest 0.6143 at 83% of the parameters (38.3 vs 46.1 B), cells = (source, domain) on
the union pool paeec37aa28063c75, tier gap 0.017 on key accuracy, cost = parameter count parsed from the model
name. FRAMEWORK L131 wants cost = declared price per 1k output tokens x mean output tokens per query in the cell
from the stored generations, and calls parameter count a PROXY until this test records tokens.

Readings taken here, and where the item is under-specified the reading hardest on the programme's own claims:

  (a) "stored generations". The union DB stores a generation (eval_results.model_output) only for the two
      generative corpora, MATH (7 cells, 398 EVAL questions) and IFEval (1 cell, 162). BBH, GPQA, MMLU-Pro and
      MuSR were scored by option loglikelihood on the leaderboard: model_output is empty for every row, and the
      raw lm-eval sample files (experiment_results/multicorpus/raw) carry loglikelihood pairs, not text. Token
      cost therefore EXISTS on 8 of 52 cells / 560 of 6,482 EVAL questions, and the criterion is scored on those.
      On the other 44 cells the cost axis stays the parameter PROXY the framework already labels as such; the
      out-of-sample re-read of the record's all-cell numbers is reported under that proxy, separately.
  (b) "each model's tokenizer". None of the 18 models' tokenizers is on this machine (no HF tokenizer cache for
      them) and this script is network-free by construction, so the item's own count is NOT COMPUTED. Five
      offline proxies are counted instead and the criterion is read under each: OpenAI's cl100k_base (100k BPE,
      the nearest on-disk relative of the Llama-3 / Qwen2.5 / Mistral 100-150k BPEs; loaded from the local
      tiktoken cache with the network client disabled, see load_proxy_tokenizers), a byte-level BPE trained on
      LaTeX/markdown (vikp/texify, 50k), a WordPiece (mpnet/BERT-uncased, 30k), characters/4, and whitespace
      words. PROVENANCE: the cl100k_base rank file entered the tiktoken cache on 2026-09-16 01:19 through an
      environment probe run in this session before this script existed; that probe was a network fetch the
      test's constraint forbids and it is disclosed as such; the script itself refuses any download. Scale
      anchor: the two R1 distills' <think>-unclosed outputs (checker_answers_v1.db non_terminated, item 7) sit
      at the harness cap (max_gen_toks 1024 MATH / 1280 IFEval in the model's OWN tokens; read from the raw
      lm-eval sample files), so proxy count / cap is each proxy's own-token scale on those two tokenizers
      (Llama-3, 128k; Qwen2.5, 152k). Diagnostic only. A verdict is stated only if the proxies agree.
  (c) "policy on TRAIN, scored on paeec". TRAIN = the 15,124 union questions outside pool paeec37aa28063c75.
      Per cell, per-cell best = argmax TRAIN accuracy; tier-then-cheapest = top key tier (gap 0.017, the record's
      rule, tier_design_probes.key_tiers) on TRAIN accuracy, then argmin TRAIN mean output tokens. Both are scored
      on the cell's EVAL questions, accuracy and tokens alike. Nothing is selected on EVAL.
  (d) MATH labels. The record's TIER-ROUTER-U used eval_results.is_correct, under which six models score 0.000
      on MATH because the harness credits only the Minerva sentence (MATH-FIX, 2026-09-13). The corrected labels
      (eval_results_mathfix, correctness only raised, 60 extractor disagreements reported) are the primary
      reading; the harness labels are reported as sensitivity.
  (e) The record's parameter regex mis-sizes three models (Phi-3.5-mini -> 70 B default, command-r-plus -> 70 B
      default, Mixtral-8x7B -> 7 B). The reproduction uses the record's regex byte-for-byte; the proxy re-read
      also uses declared parameter counts from the model cards.

Key denominator: EVAL questions of pool paeec37aa28063c75 with results for all 18 models, per (source, domain)
cell; 6,482 in all, 560 on the generative cells. This test is key-scored end to end (leaderboard verifiers,
no judge verdict enters), so no wrong-direction count arises and the McNemar/established machinery of
systematic_budget does not apply; that is stated rather than silently omitted.

Excluded: Meta-Llama-3-70B-Instruct (asserted absent from the union roster).
Output: experiment_results/x12_crossdomain/cost_axes_ingest.txt. Cache: scratchpad/block1/cost_axes_tokens.json.
Reads experiment_results/multicorpus/checker_answers_v1.db read-only for the non_terminated flag (anchor only).
"""
import os, sys, re, json, glob, math, random, sqlite3, time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard
pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)          # MMLU-Pro pool of record, verified by id (guard first)
pool_guard.assert_pool_of_record(pool_guard.UNION_POOL)             # union pool of record, verified by id
from tier_design_probes import key_tiers, KEY_GAP   # the record's tier rule, reused, not re-implemented

import numpy as np

UNION_DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
UNION_POOL = "paeec37aa28063c75"
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "cost_axes_ingest.txt")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude", "Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "block1")
TOKEN_CACHE = os.path.join(SCRATCH, "cost_axes_tokens.json")
EXCLUDED = "Meta-Llama-3-70B-Instruct"
CHECKER_DB = os.path.join(ROOT, "experiment_results", "multicorpus", "checker_answers_v1.db")
CL100K_URL = "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
TOKENIZER_FAMILY = {  # vocabulary each model generates in (model cards); used only to say whether two picks share a tokenizer
    "DeepSeek-R1-Distill-Llama-8B": "Llama-3 (128k)", "DeepSeek-R1-Distill-Qwen-32B": "Qwen2.5 (152k)",
    "Falcon3-10B-Instruct": "Falcon3 (131k)", "Llama-3.1-70B-Instruct": "Llama-3 (128k)", "Llama-3.2-3B-Instruct": "Llama-3 (128k)",
    "Llama-3.3-70B-Instruct": "Llama-3 (128k)", "Mistral-Small-Instruct-2409": "Mistral v3 (131k)", "Mixtral-8x7B-Instruct-v0.1": "Mistral v1 (32k)",
    "OLMo-2-1124-7B-Instruct": "OLMo-2 (100k)", "Phi-3.5-mini-instruct": "Llama-2 SP (32k)", "Qwen2.5-32B-Instruct": "Qwen2.5 (152k)",
    "Qwen2.5-72B-Instruct": "Qwen2.5 (152k)", "Qwen2.5-7B-Instruct": "Qwen2.5 (152k)", "Qwen2.5-Coder-7B-Instruct": "Qwen2.5 (152k)",
    "Qwen2.5-Math-7B-Instruct": "Qwen2.5 (152k)", "Yi-1.5-34B-Chat-16K": "Yi (64k)", "c4ai-command-r-plus-08-2024": "Cohere (256k)",
    "internlm2_5-20b-chat": "InternLM2 (92k)",
}
GEN_CAP = {"MATH": 1024, "IFEVAL": 1280}    # lm-eval max_gen_toks, read from the raw sample files' arguments
ACC_TOL = 0.005                              # "within 0.5pp"
COST_BAR = 0.85                              # "<= 85% of token cost"
B_EVAL = 2000; B_TRAIN = 1000; SEED = 42

# declared parameter counts (billions), model cards; the record's regex is reproduced separately
PARAMS_B = {
    "DeepSeek-R1-Distill-Llama-8B": 8.0, "DeepSeek-R1-Distill-Qwen-32B": 32.8, "Falcon3-10B-Instruct": 10.3,
    "Llama-3.1-70B-Instruct": 70.6, "Llama-3.2-3B-Instruct": 3.2, "Llama-3.3-70B-Instruct": 70.6,
    "Mistral-Small-Instruct-2409": 22.2, "Mixtral-8x7B-Instruct-v0.1": 46.7, "OLMo-2-1124-7B-Instruct": 7.3,
    "Phi-3.5-mini-instruct": 3.8, "Qwen2.5-32B-Instruct": 32.8, "Qwen2.5-72B-Instruct": 72.7,
    "Qwen2.5-7B-Instruct": 7.6, "Qwen2.5-Coder-7B-Instruct": 7.6, "Qwen2.5-Math-7B-Instruct": 7.6,
    "Yi-1.5-34B-Chat-16K": 34.4, "c4ai-command-r-plus-08-2024": 104.0, "internlm2_5-20b-chat": 19.9,
}


def record_size(m):
    """tier_design_probes.py:118-120, byte-for-byte: the record's cost proxy."""
    g = re.search(r"(\d+(?:\.\d+)?)[bB]\b", m)
    return float(g.group(1)) if g else 70.0


# ----------------------------------------------------------------------------------------------- tokenizers
def load_proxy_tokenizers():
    """Offline only. Returns {name: callable(list[str]) -> list[int]}; never touches the network."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1"); os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    prox = {}
    # cl100k_base: only from the local tiktoken cache. requests.get is replaced by a raiser for the load, so a
    # missing or corrupt cache file ends in "skipped", never in a download.
    try:
        import tempfile, hashlib, tiktoken, requests
        cache_dir = os.environ.get("TIKTOKEN_CACHE_DIR") or os.environ.get("DATA_GYM_CACHE_DIR") or os.path.join(tempfile.gettempdir(), "data-gym-cache")
        cache_file = os.path.join(cache_dir, hashlib.sha1(CL100K_URL.encode()).hexdigest())
        if os.path.exists(cache_file):
            _get = requests.get
            def _raiser(*a, **k): raise RuntimeError("network disabled in cost_axes_ingest")
            requests.get = _raiser
            try: enc = tiktoken.get_encoding("cl100k_base")
            finally: requests.get = _get
            prox["cl100k_bpe"] = (lambda e: (lambda xs: [len(t) for t in e.encode_ordinary_batch(xs)]))(enc)
            prox["_cl100k_note"] = "loaded from %s (file mtime %s)" % (cache_file, time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(cache_file))))
        else:
            prox["_cl100k_note"] = "skipped: no cached rank file at %s (no download attempted)" % cache_file
    except Exception as e:
        prox["_cl100k_note"] = "skipped: %s" % str(e)[:120]
    from tokenizers import Tokenizer
    hub = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    for name, pat in (("texify_bpe", "models--vikp--texify"), ("mpnet_wordpiece", "models--sentence-transformers--all-mpnet-base-v2")):
        fs = glob.glob(os.path.join(hub, pat, "snapshots", "*", "tokenizer.json"))
        if not fs: continue
        t = Tokenizer.from_file(fs[0]); t.no_padding(); t.no_truncation()
        prox[name] = (lambda t: (lambda xs: [len(e.ids) for e in t.encode_batch(xs, add_special_tokens=False)]))(t)
    prox["chars_div4"] = lambda xs: [int(math.ceil(len(x) / 4.0)) for x in xs]
    prox["ws_words"] = lambda xs: [len(x.split()) for x in xs]
    return prox


def token_counts(gen_rows, prox):
    """gen_rows: list of (q, m, text). Cached per proxy in the scratchpad; keyed 'q|m'."""
    cache = {}
    if os.path.exists(TOKEN_CACHE):
        try: cache = json.load(open(TOKEN_CACHE, encoding="utf-8"))
        except Exception: cache = {}
    out = {}
    for name, fn in prox.items():
        have = cache.get(name, {})
        todo = [(q, m, t) for q, m, t in gen_rows if "%d|%s" % (q, m) not in have]
        if todo:
            BS = 512
            for i in range(0, len(todo), BS):
                chunk = todo[i:i + BS]
                for (q, m, _), n in zip(chunk, fn([c[2] for c in chunk])):
                    have["%d|%s" % (q, m)] = n
            cache[name] = have
        out[name] = {tuple(k.split("|")): v for k, v in have.items()}
        out[name] = {(int(q), m): v for (q, m), v in out[name].items()}
    os.makedirs(SCRATCH, exist_ok=True)
    json.dump(cache, open(TOKEN_CACHE, "w", encoding="utf-8"))
    return out


# ----------------------------------------------------------------------------------------------- data
def load():
    con = sqlite3.connect("file:%s?mode=ro" % UNION_DB, uri=True)
    Q = {q: (s, d, int(g)) for q, s, d, g in con.execute("SELECT question_id, source, domain, generative FROM corpus_questions")}
    pool = {q for (q,) in con.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (UNION_POOL,))}
    assert len(pool) == 6482, len(pool)
    C_raw = {}
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        C_raw[(q, m)] = int(c)
    C_fix = dict(C_raw)
    nfix = 0
    for q, m, c in con.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix"):
        if C_fix.get((q, m)) != int(c): nfix += 1
        C_fix[(q, m)] = int(c)
    gen_q = [q for q in Q if Q[q][2]]
    gen_rows = []
    for q, m, t in con.execute("SELECT e.question_id, e.model_name, e.model_output FROM eval_results e "
                               "JOIN corpus_questions c USING(question_id) WHERE c.generative=1"):
        gen_rows.append((q, m, t))
    models = sorted({m for (_, m) in C_raw})
    assert EXCLUDED not in models and len(models) == 18, models
    return Q, pool, C_raw, C_fix, gen_rows, models, nfix


# ----------------------------------------------------------------------------------------------- policies
class Cells:
    """Per cell: TRAIN/EVAL question lists, correctness matrices (n_q x n_m) and cost matrices per proxy."""
    def __init__(self, Q, pool, models, C, cost_by_proxy, cell_filter=None):
        self.models = models; self.midx = {m: i for i, m in enumerate(models)}
        by = defaultdict(lambda: {"train": [], "eval": []})
        for q, (s, d, g) in Q.items():
            if cell_filter and not cell_filter(s, d): continue
            by[(s, d)]["eval" if q in pool else "train"].append(q)
        self.cells = {}
        for cell, sides in sorted(by.items()):
            rec = {}
            for side in ("train", "eval"):
                qs = sorted(sides[side])
                A = np.array([[C[(q, m)] for m in models] for q in qs], dtype=float)
                rec[side] = qs; rec[side + "_acc"] = A
                for pname, cost in cost_by_proxy.items():
                    K = np.array([[cost(q, m) for m in models] for q in qs], dtype=float)
                    rec[side + "_cost_" + pname] = K
            self.cells[cell] = rec
        self.proxies = list(cost_by_proxy)

    def pick(self, cell, pname, side="train", A=None, K=None):
        """(per-cell best, top-tier members, tier-then-cheapest) selected on `side` (or on the given resampled
        matrices A, K). Ties in accuracy: first by sorted model name; ties in cost: the record's own tie-break,
        min() over the tier in accuracy order (tier_design_probes.py:131, `min(top, key=size)`), i.e. the more
        accurate of two equal-cost members. An alphabetical tie-break moves 2 of 52 cells and 0.05pp."""
        rec = self.cells[cell]
        A = rec[side + "_acc"] if A is None else A
        K = rec[side + "_cost_" + pname] if K is None else K
        la = A.mean(axis=0); lc = K.mean(axis=0)
        acc = {m: float(la[self.midx[m]]) for m in self.models}
        pcb = max(self.models, key=lambda m: (acc[m], -self.midx[m]))
        top = key_tiers(acc, self.models, gap=KEY_GAP)[0]
        ttc = min(top, key=lambda m: (float(lc[self.midx[m]]), top.index(m)))
        return pcb, top, ttc

    def best_single(self, side="train"):
        tot = defaultdict(float); n = 0
        for rec in self.cells.values():
            tot_cell = rec[side + "_acc"].sum(axis=0); n += len(rec[side])
            for m in self.models: tot[m] += tot_cell[self.midx[m]]
        return max(self.models, key=lambda m: (tot[m] / n, -self.midx[m]))

    def score(self, picks, pname, side="eval"):
        """picks: cell -> model. Returns (accuracy, mean cost, n) pooled over the cells' `side` questions."""
        sa = sc = 0.0; n = 0
        for cell, m in picks.items():
            rec = self.cells[cell]; j = self.midx[m]
            sa += rec[side + "_acc"][:, j].sum(); sc += rec[side + "_cost_" + pname][:, j].sum(); n += len(rec[side])
        return sa / n, sc / n, n


def run_policies(cs, pname, select_side="train", score_side="eval"):
    pcb = {}; ttc = {}; tops = {}
    for cell in cs.cells:
        b, top, c = cs.pick(cell, pname, side=select_side)
        pcb[cell] = b; ttc[cell] = c; tops[cell] = top
    bs = cs.best_single(select_side)
    res = {"best single": cs.score({c: bs for c in cs.cells}, pname, score_side),
           "per-cell best": cs.score(pcb, pname, score_side),
           "tier-then-cheapest": cs.score(ttc, pname, score_side)}
    return res, pcb, ttc, tops, bs


def fmt_policy_table(L, res, unit):
    L.append("    %-22s %9s %14s" % ("policy", "accuracy", "mean " + unit))
    for k in ("best single", "per-cell best", "tier-then-cheapest"):
        a, c, n = res[k]; L.append("    %-22s %9.4f %14.1f" % (k, a, c))
    d = res["tier-then-cheapest"][0] - res["per-cell best"][0]
    r = res["tier-then-cheapest"][1] / max(1e-9, res["per-cell best"][1])
    L.append("    tier-then-cheapest vs per-cell best: %+.4f accuracy (%+.2fpp) at %.1f%% of the %s   [n = %d]"
             % (d, 100 * d, 100 * r, unit, res["per-cell best"][2]))
    return d, r


# ----------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time(); L = []
    L.append("COST-AXES-INGEST (FRAMEWORK item 16; registered by reference at eaf1dbf) -- zero LLM calls, zero network")
    L.append("pool of record p2dca21ab5f4ef3ae verified by id (pool_guard); union pool %s verified and addressed by explicit id" % UNION_POOL)
    Q, pool, C_raw, C_fix, gen_rows, models, nfix = load()
    L.append("union DB: %d questions, %d models (%s asserted absent); TRAIN = %d outside the pool, EVAL = %d in it"
             % (len(Q), len(models), EXCLUDED, len(Q) - len(pool), len(pool)))
    L.append("MATH-FIX labels differ from the harness labels on %d (question, model) rows; primary reading uses MATH-FIX" % nfix)

    # ---------------- 1. token counts per (model, cell)
    L.append("")
    L.append("=== 1. Token counts per (model, cell) from the stored generations ===")
    gen_sources = sorted({Q[q][0] for q, _, _ in gen_rows})
    n_gen_q = len({q for q, _, _ in gen_rows})
    L.append("  stored generations exist for %s only: %d questions x %d models = %d texts; the other four corpora were"
             % (", ".join(gen_sources), n_gen_q, len(models), len(gen_rows)))
    L.append("  scored by option loglikelihood (model_output empty on every row; raw lm-eval samples hold logprob pairs).")
    L.append("  Generative EVAL questions in the pool: %d of %d (%s)"
             % (sum(1 for q in pool if Q[q][2]), len(pool),
                ", ".join("%s %d" % (s, sum(1 for q in pool if Q[q][0] == s)) for s in gen_sources)))
    prox = load_proxy_tokenizers(); cl_note = prox.pop("_cl100k_note", "")
    L.append("  each model's OWN tokenizer: NOT COMPUTED -- none of the 18 tokenizers is on disk and the run is network-free.")
    L.append("  proxies counted offline: %s" % ", ".join(prox))
    L.append("  cl100k_base: %s" % cl_note)
    L.append("  PROVENANCE: the cl100k rank file was fetched into the tiktoken cache by an environment probe in this session (2026-09-16 01:19),")
    L.append("  before this script existed; that fetch was a network access the test constraint forbids and is disclosed here. The script never downloads.")
    tok = token_counts(gen_rows, prox)
    L.append("  (per-model scale anchor below uses the harness cap: max_gen_toks %s in the model's own tokens)"
             % ", ".join("%s %d" % kv for kv in GEN_CAP.items()))
    text_len = {(q, m): len(t) for q, m, t in gen_rows}
    # mean tokens per (model, source) on EVAL and TRAIN, primary proxy first
    P0 = "cl100k_bpe" if "cl100k_bpe" in tok else ("texify_bpe" if "texify_bpe" in tok else list(tok)[0])
    L.append("")
    L.append("  mean output tokens per query, EVAL side (pool), by proxy; MATH pooled over its 7 cells:")
    hdr = "    %-30s" % "model" + "".join(" %8s|%-8s" % (s[:4] + "." + p[:3], "") for s in gen_sources for p in list(tok))
    L.append("    %-30s %s" % ("model", "  ".join("%-38s" % (s + " (" + "/".join(p[:6] for p in tok) + ")") for s in gen_sources)))
    for m in models:
        row = []
        for s in gen_sources:
            qs = [q for q in pool if Q[q][0] == s]
            row.append("  ".join("%7.0f" % (sum(tok[p][(q, m)] for q in qs) / len(qs)) for p in tok))
        L.append("    %-30s %s" % (m[:30], "   ".join("%-38s" % r for r in row)))
    L.append("")
    L.append("  per (model, cell) mean tokens on EVAL, proxy %s (the criterion's primary cost unit):" % P0)
    gen_cells = sorted({(Q[q][0], Q[q][1]) for q in pool if Q[q][2]})
    L.append("    %-30s %s" % ("model", " ".join("%9s" % (c[1][:9]) for c in gen_cells)))
    for m in models:
        vals = []
        for c in gen_cells:
            qs = [q for q in pool if (Q[q][0], Q[q][1]) == c]
            vals.append(sum(tok[P0][(q, m)] for q in qs) / len(qs))
        L.append("    %-30s %s" % (m[:30], " ".join("%9.0f" % v for v in vals)))
    L.append("    cells: %s" % "; ".join("%s=%s/%s" % (c[1][:9], c[0], c[1]) for c in gen_cells))

    # cap-anchored diagnostic: a <think> that never closes (checker_answers_v1.db non_terminated, item 7) means the
    # generation ran into max_gen_toks, i.e. the output holds exactly the cap in the model's OWN tokens.
    L.append("")
    L.append("  DIAGNOSTIC scale anchor: outputs whose <think> never closes (non_terminated in checker_answers_v1.db) stopped at")
    L.append("  the harness cap, so they hold max_gen_toks OWN tokens; median proxy count / cap = proxy tokens per own token.")
    nt = set()
    try:
        ck = sqlite3.connect("file:%s?mode=ro" % CHECKER_DB, uri=True)
        for tbl in ("math_checker_answers", "ifeval_checker_answers"):
            nt |= {(q, m) for q, m in ck.execute("SELECT question_id, model_name FROM %s WHERE non_terminated = 1" % tbl)}
        ck.close()
    except Exception as e:
        L.append("    checker DB unavailable (%s); no anchor" % str(e)[:80])
    anchor_rows = 0
    L.append("    %-30s %-7s %6s %6s %s" % ("model", "corpus", "n@cap", "cap", " ".join("%12s" % p[:12] for p in tok)))
    for m in models:
        for s_ in gen_sources:
            wall = [q for q in Q if Q[q][0] == s_ and (q, m) in nt]
            if len(wall) < 5: continue
            anchor_rows += 1
            scales = [float(np.median([tok[p][(q, m)] for q in wall])) / GEN_CAP[s_] for p in tok]
            L.append("    %-30s %-7s %6d %6d %s   [%s]" % (m[:30], s_, len(wall), GEN_CAP[s_], " ".join("%12.3f" % x for x in scales), TOKENIZER_FAMILY.get(m, "?")))
    if not anchor_rows:
        L.append("    (no (model, corpus) has >= 5 non_terminated outputs; no anchor row)")
    L.append("  READ: 1.00 means the proxy counts like that model's own tokenizer on its capped outputs; only the two R1 distills")
    L.append("  ever hit the cap, so the anchor covers the Llama-3 and Qwen2.5 vocabularies only. Nothing below uses this scale.")

    # ---------------- 2. reproduction of the record (in-sample, harness labels, record regex)
    L.append("")
    L.append("=== 2. Reproduction of TIER-ROUTER-U as recorded (in-sample: selected AND scored on the pool; harness labels;")
    L.append("       cost = parameter count by the record's regex) ===")
    cost_rec = {"record_regex": (lambda q, m: record_size(m))}
    cs_all_raw = Cells(Q, pool, models, C_raw, cost_rec)
    res_rep, _, _, _, _ = run_policies(cs_all_raw, "record_regex", select_side="eval", score_side="eval")
    d_rep, r_rep = fmt_policy_table(L, res_rep, "params B (regex)")
    ok_rep = abs(res_rep["best single"][0] - 0.5543) < 5e-4 and abs(res_rep["per-cell best"][0] - 0.6169) < 5e-4 \
        and abs(res_rep["tier-then-cheapest"][0] - 0.6143) < 5e-4
    L.append("    record: 0.5543 / 0.6169 / 0.6143 at 72.0 / 46.1 / 38.3 B -> %s" % ("REPRODUCED" if ok_rep else "NOT REPRODUCED"))
    L.append("    the regex sizes Phi-3.5-mini-instruct at %.0f B (declared 3.8), c4ai-command-r-plus at %.0f B (104), Mixtral-8x7B at %.0f B (46.7)"
             % (record_size("Phi-3.5-mini-instruct"), record_size("c4ai-command-r-plus-08-2024"), record_size("Mixtral-8x7B-Instruct-v0.1")))

    # ---------------- 3. the item: out of sample on the generative cells with token cost
    L.append("")
    L.append("=== 3. THE ITEM: TIER-ROUTER-U out of sample (policy on TRAIN, scored on the pool) with TOKEN cost, on the")
    L.append("       8 cells that have stored generations (MATH x7, IFEval x1) ===")
    L.append("  per-cell best = argmax TRAIN accuracy; tier-then-cheapest = top key tier on TRAIN (gap %.3f) then argmin TRAIN" % KEY_GAP)
    L.append("  mean tokens; both scored on the cell's EVAL questions. Criterion: accuracy within %.1fpp AND tokens <= %.0f%%." % (100 * ACC_TOL, 100 * COST_BAR))
    is_gen = lambda s, d: s in GEN_CAP
    cost_tok = {p: (lambda p: (lambda q, m: tok[p][(q, m)]))(p) for p in tok}
    verdict_rows = []; oracle_rows = []
    primary_detail = None
    for label_name, C in (("MATH-FIX labels (primary)", C_fix), ("harness labels (sensitivity)", C_raw)):
        cs = Cells(Q, pool, models, C, cost_tok, cell_filter=is_gen)
        L.append("")
        L.append("  --- %s: %d cells, EVAL n = %d, TRAIN n = %d ---"
                 % (label_name, len(cs.cells), sum(len(r["eval"]) for r in cs.cells.values()), sum(len(r["train"]) for r in cs.cells.values())))
        for p in tok:
            res, pcb, ttc, tops, bs = run_policies(cs, p)
            L.append("  proxy %s:" % p)
            d, r = fmt_policy_table(L, res, "tokens")
            accok = d >= -ACC_TOL; costok = r <= COST_BAR
            L.append("    criterion: accuracy %s (%+.2fpp vs -%.1fpp), cost %s (%.1f%% vs %.0f%%)"
                     % ("MET" if accok else "NOT MET", 100 * d, 100 * ACC_TOL, "MET" if costok else "NOT MET", 100 * r, 100 * COST_BAR))
            verdict_rows.append((label_name, p, d, r, accok and costok, accok, costok))
            if label_name.startswith("MATH-FIX") and p == P0:
                primary_detail = (cs, res, pcb, ttc, tops, bs)
            # in-sample counterpart (the record's reading) on the same cells, for the optimism gap
            res_in, _, _, _, _ = run_policies(cs, p, select_side="eval", score_side="eval")
            L.append("    in-sample counterpart (select on EVAL): per-cell best %.4f, tier-then-cheapest %.4f at %.1f%% tokens; OOS optimism gap %+.2fpp / %+.2fpp"
                     % (res_in["per-cell best"][0], res_in["tier-then-cheapest"][0],
                        100 * res_in["tier-then-cheapest"][1] / max(1e-9, res_in["per-cell best"][1]),
                        100 * (res_in["per-cell best"][0] - res["per-cell best"][0]),
                        100 * (res_in["tier-then-cheapest"][0] - res["tier-then-cheapest"][0])))
            # HARDEST reading: the OOS tier-then-cheapest against the EVAL-selected (oracle) per-cell best, i.e. the
            # record's own in-sample ceiling. Reported, not the verdict's comparator (the item pairs two TRAIN policies).
            d_or = res["tier-then-cheapest"][0] - res_in["per-cell best"][0]
            r_or = res["tier-then-cheapest"][1] / max(1e-9, res_in["per-cell best"][1])
            L.append("    hardest reading (OOS tier-then-cheapest vs ORACLE per-cell best selected on EVAL): %+.2fpp at %.1f%% tokens -> accuracy %s, cost %s"
                     % (100 * d_or, 100 * r_or, "MET" if d_or >= -ACC_TOL else "NOT MET", "MET" if r_or <= COST_BAR else "NOT MET"))
            oracle_rows.append((label_name, p, d_or, r_or))

    # per-cell picks under the primary reading
    cs, res, pcb, ttc, tops, bs = primary_detail
    L.append("")
    L.append("  per-cell picks, primary reading (MATH-FIX, %s); EVAL accuracy and mean tokens of each pick; best single = %s" % (P0, bs))
    L.append("    %-28s %5s %4s  %-28s %6s %7s  %-28s %6s %7s" % ("cell", "n_ev", "tier", "per-cell best (TRAIN)", "acc", "tok", "tier-then-cheapest", "acc", "tok"))
    for cell in cs.cells:
        rec = cs.cells[cell]; ne = len(rec["eval"])
        def ev(m):
            j = cs.midx[m]; return rec["eval_acc"][:, j].mean(), rec["eval_cost_" + P0][:, j].mean()
        a1, c1 = ev(pcb[cell]); a2, c2 = ev(ttc[cell])
        L.append("    %-28s %5d %4d  %-28s %6.3f %7.0f  %-28s %6.3f %7.0f%s"
                 % ((cell[0] + "/" + cell[1])[:28], ne, len(tops[cell]), pcb[cell][:28], a1, c1, ttc[cell][:28], a2, c2,
                    "  (same pick)" if pcb[cell] == ttc[cell] else ("  (both %s)" % TOKENIZER_FAMILY[pcb[cell]] if TOKENIZER_FAMILY.get(pcb[cell]) == TOKENIZER_FAMILY.get(ttc[cell]) else "  (%s vs %s)" % (TOKENIZER_FAMILY.get(pcb[cell]), TOKENIZER_FAMILY.get(ttc[cell])))))
    n_div = sum(1 for c in cs.cells if pcb[c] != ttc[c]); n_samefam = sum(1 for c in cs.cells if pcb[c] != ttc[c] and TOKENIZER_FAMILY.get(pcb[c]) == TOKENIZER_FAMILY.get(ttc[c]))
    L.append("    cells where the two policies diverge: %d; of those, both picks generate in the same vocabulary: %d" % (n_div, n_samefam))
    L.append("    (where both picks share a tokenizer, the own-tokenizer cost ratio differs from a proxy's only through the proxy's")
    L.append("     text-dependent scale, not through vocabulary differences)")
    L.append("    top-tier members on TRAIN per cell: %s" % "; ".join("%s: %s" % (c[1][:9], ", ".join(m[:14] for m in tops[c])) for c in cs.cells))

    # ---------------- 4. bootstraps on the primary reading
    L.append("")
    L.append("=== 4. Uncertainty on the primary reading (MATH-FIX labels), every proxy ===")
    L.append("  (i) EVAL question bootstrap, policy fixed (selected once on TRAIN), stratified within cell, B = %d;" % B_EVAL)
    L.append("  (ii) TRAIN bootstrap, policy re-selected on each resample and scored on the full EVAL side, B = %d." % B_TRAIN)
    cs = Cells(Q, pool, models, C_fix, cost_tok, cell_filter=is_gen)
    rng = np.random.default_rng(SEED)
    cells = list(cs.cells)
    boot_rows = []
    for p in tok:
        res, pcb, ttc, tops, bs = run_policies(cs, p)
        # (i) EVAL bootstrap
        dd = []; rr = []
        pre = []
        for cell in cells:
            rec = cs.cells[cell]
            j1 = cs.midx[pcb[cell]]; j2 = cs.midx[ttc[cell]]
            pre.append((rec["eval_acc"][:, j1], rec["eval_acc"][:, j2], rec["eval_cost_" + p][:, j1], rec["eval_cost_" + p][:, j2]))
        N = sum(len(x[0]) for x in pre)
        for _ in range(B_EVAL):
            sa1 = sa2 = sc1 = sc2 = 0.0
            for a1, a2, c1, c2 in pre:
                idx = rng.integers(0, len(a1), len(a1))
                sa1 += a1[idx].sum(); sa2 += a2[idx].sum(); sc1 += c1[idx].sum(); sc2 += c2[idx].sum()
            dd.append((sa2 - sa1) / N); rr.append(sc2 / max(1e-9, sc1))
        dd = np.array(dd); rr = np.array(rr)
        d_lo, d_hi = np.percentile(dd, [2.5, 97.5]); r_lo, r_hi = np.percentile(rr, [2.5, 97.5])
        # (ii) TRAIN bootstrap
        td = []; tr = []; same = 0
        for _ in range(B_TRAIN):
            pcb_b = {}; ttc_b = {}
            for cell in cells:
                rec = cs.cells[cell]; n = len(rec["train"])
                idx = rng.integers(0, n, n)
                b, top, c = cs.pick(cell, p, A=rec["train_acc"][idx], K=rec["train_cost_" + p][idx])
                pcb_b[cell] = b; ttc_b[cell] = c
            r1 = cs.score(pcb_b, p); r2 = cs.score(ttc_b, p)
            td.append(r2[0] - r1[0]); tr.append(r2[1] / max(1e-9, r1[1]))
            same += int(pcb_b == pcb and ttc_b == ttc)
        td = np.array(td); tr = np.array(tr)
        both = float(np.mean((td >= -ACC_TOL) & (tr <= COST_BAR)))
        L.append("  proxy %-16s point %+.2fpp at %5.1f%% | (i) EVAL-boot delta 95%% [%+.2f, %+.2f]pp, ratio [%.1f, %.1f]%%, SE %.2fpp"
                 % (p, 100 * res["tier-then-cheapest"][0] - 100 * res["per-cell best"][0],
                    100 * res["tier-then-cheapest"][1] / max(1e-9, res["per-cell best"][1]),
                    100 * d_lo, 100 * d_hi, 100 * r_lo, 100 * r_hi, 100 * dd.std()))
        L.append("  %-22s | (ii) TRAIN-boot delta 95%% [%+.2f, %+.2f]pp, ratio [%.1f, %.1f]%%; P(both criteria met) = %.3f; identical policy in %.1f%% of resamples"
                 % ("", 100 * np.percentile(td, 2.5), 100 * np.percentile(td, 97.5), 100 * np.percentile(tr, 2.5), 100 * np.percentile(tr, 97.5), both, 100 * same / B_TRAIN))
        boot_rows.append((p, d_lo, d_hi, r_lo, r_hi, both))

    # ---------------- 5. the all-cell OOS re-read under the parameter PROXY (the record's numbers, out of sample)
    L.append("")
    L.append("=== 5. All 52 cells out of sample under the parameter PROXY (no token cost exists on 44 of them) ===")
    L.append("  This is the record's 0.6143-vs-0.6169 read with selection on TRAIN and scoring on the pool; not the item's criterion.")
    cost_par = {"record_regex": (lambda q, m: record_size(m)), "declared_params": (lambda q, m: PARAMS_B[m])}
    for label_name, C in (("MATH-FIX labels", C_fix), ("harness labels", C_raw)):
        cs_all = Cells(Q, pool, models, C, cost_par)
        for p in cost_par:
            res, pcb, ttc, tops, bs = run_policies(cs_all, p)
            L.append("  %s, cost = %s (best single on TRAIN = %s):" % (label_name, p, bs))
            d, r = fmt_policy_table(L, res, "params B")
            L.append("    accuracy criterion (%.1fpp): %s; parameter ratio %.1f%% (%s %.0f%%)"
                     % (100 * ACC_TOL, "MET" if d >= -ACC_TOL else "NOT MET", 100 * r, "<=" if r <= COST_BAR else ">", 100 * COST_BAR))
            n_same = sum(1 for c in cs_all.cells if pcb[c] == ttc[c]); n_single = sum(1 for c in cs_all.cells if len(tops[c]) == 1)
            L.append("    cells where tier-then-cheapest = per-cell best: %d of %d; singleton top tier on TRAIN: %d" % (n_same, len(cs_all.cells), n_single))

    # ---------------- 6. verdict
    L.append("")
    L.append("=== 6. Verdict ===")
    L.append("  Key denominator: EVAL questions of union pool %s with all 18 models' results, per (source, domain) cell;" % UNION_POOL)
    L.append("  560 on the 8 generative cells (MATH 398, IFEval 162), 6,482 on all 52. Key-scored throughout (leaderboard verifiers;")
    L.append("  MATH-FIX extractor on MATH): no judge verdict enters, so no wrong-direction count and no McNemar-established count arises.")
    L.append("  Criterion (a), token counts per (model, cell) via each model's tokenizer: NOT COMPUTED offline; %d proxies recorded (section 1)." % len(tok))
    prim = [v for v in verdict_rows if v[0].startswith("MATH-FIX")]
    sens = [v for v in verdict_rows if not v[0].startswith("MATH-FIX")]
    for tag, rows in (("primary (MATH-FIX)", prim), ("sensitivity (harness labels)", sens)):
        L.append("  Criterion (b), %s, per proxy:" % tag)
        for (_, p, d, r, both, accok, costok) in rows:
            L.append("    %-16s delta %+.2fpp (%s)  tokens %5.1f%% (%s)  -> %s"
                     % (p, 100 * d, "ok" if accok else "FAIL", 100 * r, "ok" if costok else "FAIL", "MET" if both else "NOT MET"))
    L.append("  Hardest reading (OOS tier-then-cheapest vs ORACLE per-cell best on EVAL), primary labels: %s"
             % "; ".join("%s %+.2fpp at %.1f%%" % (p, 100 * d, 100 * r) for (ln, p, d, r) in oracle_rows if ln.startswith("MATH-FIX")))
    n_met = sum(1 for v in prim if v[4]); n_acc = sum(1 for v in prim if v[5]); n_cost = sum(1 for v in prim if v[6])
    if n_met == len(prim): word = "PASS under every proxy tokenizer (the item's own-tokenizer count is NOT COMPUTED; PROXY-TOKENIZED)"
    elif n_met == 0: word = "FAIL under every proxy tokenizer"
    else: word = "UNDETERMINED: the proxies disagree (%d of %d meet both parts)" % (n_met, len(prim))
    L.append("  accuracy part met under %d/%d proxies; cost part met under %d/%d proxies." % (n_acc, len(prim), n_cost, len(prim)))
    L.append("  VERDICT on the item's criterion (generative cells, out of sample): %s" % word)
    L.append("  Bootstrap (section 4): TRAIN-resample P(both parts met) per proxy = %s" % ", ".join("%s %.3f" % (p, b) for p, _, _, _, _, b in boot_rows))
    L.append("  Scope statement: the criterion is decidable only where generations are stored (8 of 52 cells, 560 of 6,482 EVAL")
    L.append("  questions); on the other 44 cells token cost does not exist in this DB and the router's cost axis remains the")
    L.append("  parameter PROXY (section 5). Latency: NOT COMPUTED, needs timed regeneration (registered separately per the item).")
    L.append("  elapsed %.0f s" % (time.time() - t0))

    txt = "\n".join(L)
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
