"""Open LLM Leaderboard v2 per-sample details -> multi-corpus eval rows (docs/multi_corpus_design.md, stage 1).

  python tools/ingest/leaderboard_details.py --dry-run [--models m1,m2] [--corpora bbh,math,musr,ifeval,gpqa,mmlu_pro]
  python tools/ingest/leaderboard_details.py --fetch --out experiment_results/multicorpus/raw   (downloads JSONL only)

Zero LLM calls. Repos: open-llm-leaderboard/<org>__<model>-details, files
<org>__<model>/samples_leaderboard_<task>_<timestamp>.jsonl (one per task per run; latest run wins) and
results_<timestamp>.json. Gated repos need HUGGINGFACE_TOKEN (read from .env). The dry run prints the coverage
matrix models x corpora (task counts, latest timestamp) and writes it to experiment_results/multicorpus/coverage.csv.
"""
import os, sys, re, csv, json, argparse
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "experiment_results", "multicorpus")

# eval_results model name -> leaderboard repo slug (org__model). Open models of the campaign roster first.
MODELS = {
    "Meta-Llama-3_1-8B-Instruct": "meta-llama__Meta-Llama-3.1-8B-Instruct",
    "Meta-Llama-3_1-70B-Instruct": "meta-llama__Meta-Llama-3.1-70B-Instruct",
    "Meta-Llama-3_1-8B": "meta-llama__Meta-Llama-3.1-8B",
    "Qwen1.5-72B-Chat": "Qwen__Qwen1.5-72B-Chat",
    "Qwen1.5-14B-Chat": "Qwen__Qwen1.5-14B-Chat",
    "Qwen1.5-110B": "Qwen__Qwen1.5-110B",
    "Mixtral-8x7B-Instruct-v0.1": "mistralai__Mixtral-8x7B-Instruct-v0.1",
    "gemma-7b": "google__gemma-7b",
    "Phi-3-mini-4k-instruct": "microsoft__Phi-3-mini-4k-instruct",
    "Yi-6b-Chat": "01-ai__Yi-6B-Chat",
    "Llama-2-13b-hf": "meta-llama__Llama-2-13b-hf",
    "Llama-2-7b-hf": "meta-llama__Llama-2-7b-hf",
    "c4ai-command-r-v01": "CohereForAI__c4ai-command-r-v01",
    "Mistral-7B-Instruct-v0.2": "mistralai__Mistral-7B-Instruct-v0.2",
    "Qwen2.5-7B-Instruct": "Qwen__Qwen2.5-7B-Instruct",
    "Qwen2.5-72B-Instruct": "Qwen__Qwen2.5-72B-Instruct",
}
ROSTER18 = {   # multi-corpus roster (stage 1, 2026-09-11): official repos with full coverage of all 6 corpora; families x sizes x specialists
    "Llama-3.3-70B-Instruct": "meta-llama__Llama-3.3-70B-Instruct", "Llama-3.1-70B-Instruct": "meta-llama__Llama-3.1-70B-Instruct",
    "Llama-3.2-3B-Instruct": "meta-llama__Llama-3.2-3B-Instruct", "Qwen2.5-72B-Instruct": "Qwen__Qwen2.5-72B-Instruct",
    "Qwen2.5-32B-Instruct": "Qwen__Qwen2.5-32B-Instruct", "Qwen2.5-7B-Instruct": "Qwen__Qwen2.5-7B-Instruct",
    "Qwen2.5-Math-7B-Instruct": "Qwen__Qwen2.5-Math-7B-Instruct", "Qwen2.5-Coder-7B-Instruct": "Qwen__Qwen2.5-Coder-7B-Instruct",
    "DeepSeek-R1-Distill-Qwen-32B": "deepseek-ai__DeepSeek-R1-Distill-Qwen-32B", "DeepSeek-R1-Distill-Llama-8B": "deepseek-ai__DeepSeek-R1-Distill-Llama-8B",
    "Mistral-Small-Instruct-2409": "mistralai__Mistral-Small-Instruct-2409", "Mixtral-8x7B-Instruct-v0.1": "mistralai__Mixtral-8x7B-Instruct-v0.1",
    "Phi-3.5-mini-instruct": "microsoft__Phi-3.5-mini-instruct", "Yi-1.5-34B-Chat-16K": "01-ai__Yi-1.5-34B-Chat-16K",
    "c4ai-command-r-plus-08-2024": "CohereForAI__c4ai-command-r-plus-08-2024", "Falcon3-10B-Instruct": "tiiuae__Falcon3-10B-Instruct",
    "OLMo-2-1124-7B-Instruct": "allenai__OLMo-2-1124-7B-Instruct", "internlm2_5-20b-chat": "internlm__internlm2_5-20b-chat",
}
MODELS.update(ROSTER18)
CORPORA = ["bbh", "math", "musr", "ifeval", "gpqa", "mmlu_pro"]
PAT = re.compile(r"samples_leaderboard_(?P<task>.+?)_(?P<ts>\d{4}-\d{2}-\d{2}T[0-9\-.]+)\.jsonl$")


def load_token():
    for p in (os.path.join(ROOT, ".env"),):
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                if line.startswith("HUGGINGFACE_TOKEN=") or line.startswith("HF_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"')
    return os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")


def corpus_of(task):
    for c in CORPORA:
        if task.startswith(c + "_") or task == c:
            return c
    return None


def survey(api, slug, token):
    rid = "open-llm-leaderboard/%s-details" % slug
    try:
        files = api.list_repo_files(rid, repo_type="dataset", token=token)
    except Exception as e:
        return None, str(e)[:60]
    runs = defaultdict(lambda: defaultdict(set))   # ts -> corpus -> tasks
    for f in files:
        m = PAT.search(f)
        if not m: continue
        c = corpus_of(m.group("task"))
        if c: runs[m.group("ts")][c].add(m.group("task"))
    if not runs: return {}, "no sample files"
    latest = max(runs)
    return {c: (len(t), latest) for c, t in runs[latest].items()}, None


def dry_run(models, corpora):
    from huggingface_hub import HfApi
    api = HfApi(); token = load_token()
    os.makedirs(OUT, exist_ok=True)
    print("coverage (task files in the latest run; token %s)" % ("present" if token else "ABSENT — gated repos will fail"))
    print("%-30s %-40s " % ("model", "leaderboard slug") + " ".join("%8s" % c for c in corpora) + "  latest run")
    rows = []
    for m in models:
        slug = MODELS[m]; cov, err = survey(api, slug, token)
        if cov is None:
            print("%-30s %-40s ERROR %s" % (m, slug, err)); rows.append([m, slug] + [""] * len(corpora) + ["ERROR " + err]); continue
        ts = next(iter(cov.values()))[1] if cov else ""
        print("%-30s %-40s " % (m, slug) + " ".join("%8s" % (cov[c][0] if c in cov else "-") for c in corpora) + "  " + ts)
        rows.append([m, slug] + [cov[c][0] if c in cov else 0 for c in corpora] + [ts])
    with open(os.path.join(OUT, "coverage.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["model", "slug"] + corpora + ["latest_run"]); w.writerows(rows)
    print("written %s" % os.path.join(OUT, "coverage.csv"))


def fetch(models, corpora, out):
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi(); token = load_token()
    for m in models:
        slug = MODELS[m]; rid = "open-llm-leaderboard/%s-details" % slug
        try:
            files = api.list_repo_files(rid, repo_type="dataset", token=token)
        except Exception as e:
            print("%s: SKIPPED (%s)" % (m, str(e)[:80]), flush=True); continue
        runs = defaultdict(list)
        for f in files:
            mm = PAT.search(f)
            if mm and corpus_of(mm.group("task")) in corpora: runs[mm.group("ts")].append(f)
        if not runs: print("%s: nothing to fetch" % m); continue
        latest = max(runs); n = 0
        try:
            for f in runs[latest]:
                hf_hub_download(rid, f, repo_type="dataset", token=token, local_dir=os.path.join(out, m)); n += 1
        except Exception as e:
            print("%s: SKIPPED after %d files (%s)" % (m, n, str(e).split(chr(10))[0][:100]), flush=True); continue
        print("%s: %d files from run %s" % (m, n, latest), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--models", default=",".join(MODELS)); ap.add_argument("--corpora", default=",".join(CORPORA))
    ap.add_argument("--out", default=os.path.join(OUT, "raw"))
    a = ap.parse_args(); models = [m for m in a.models.split(",") if m in MODELS]; corpora = a.corpora.split(",")
    if a.dry_run: dry_run(models, corpora)
    elif a.fetch: fetch(models, corpora, a.out)
