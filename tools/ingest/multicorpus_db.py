"""Build the multi-corpus database from downloaded leaderboard details (docs/multi_corpus_design.md, stage 1).

  python tools/ingest/multicorpus_db.py --build [--raw experiment_results/multicorpus/raw] [--db multicorpus_cache_v1.db]
  python tools/ingest/multicorpus_db.py --summary

Zero LLM calls. Never touches mmlu_pro_dataset_cache_v2.db. Schema (namespaced ids, see design §3.2):
  corpus_registry(source, table_name, id_offset, verifier)
  corpus_questions(question_id PK, source, upstream_id, task, domain, text, options_json, target, verifier, generative)
  eval_results(question_id, model_name, category, question_text, options_json, gt_answer, pred, model_output,
               is_correct, PRIMARY KEY (question_id, model_name))   -- same shape as the v2 DB (no per-row side flag)
  item_side(content_key PK, family_id, side, contract_id, cell, pool_id_at_ingest, normaliser_version, recorded_at)
      -- tier-b sides of every ingested item (split_side.py), append-only; a DB built before the pin has none
Log-likelihood tasks (bbh, gpqa, musr, mmlu_pro) have no generated trace: model_output = '' and pred = the
argmax choice; generative tasks (math, ifeval) store the response text. is_correct = the leaderboard metric.
"""
import os, re, sys, json, glob, sqlite3, argparse, time
from collections import defaultdict, Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))
import split_side   # the side function, byte-identical to SplitSide.kt (tools/analysis/split_side.py)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "experiment_results", "multicorpus", "raw")
DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
OFFSET = {"MMLU_PRO": 0, "BBH": 1_000_000, "MATH": 2_000_000, "MUSR": 3_000_000, "IFEVAL": 4_000_000, "GPQA": 5_000_000}
VERIFIER = {"MMLU_PRO": "MC_LETTER", "BBH": "IMPORTED:acc_norm", "MATH": "IMPORTED:exact_match", "MUSR": "IMPORTED:acc_norm",
            "IFEVAL": "IMPORTED:prompt_level_strict_acc", "GPQA": "IMPORTED:acc_norm"}
GENERATIVE = {"MATH", "IFEVAL"}
PAT = re.compile(r"samples_leaderboard_(?P<task>.+?)_(?P<ts>\d{4}-\d{2}-\d{2}T[0-9\-.]+)\.jsonl$")


def source_of(task):
    for s in ("mmlu_pro", "bbh", "math", "musr", "ifeval", "gpqa"):
        if task == s or task.startswith(s + "_"): return s.upper()
    return None


def parse(source, task, rec):
    """-> (upstream_key, domain, text, options, target, pred, output, is_correct)"""
    doc = rec["doc"]; fr = rec.get("filtered_resps") or []
    if source == "MMLU_PRO":
        opts = doc["options"]; pred_i = max(range(len(fr)), key=lambda i: float(fr[i][0])) if fr else -1
        return (int(doc["question_id"]), doc["category"], doc["question"], opts, doc["answer"],
                "ABCDEFGHIJ"[pred_i] if 0 <= pred_i < 10 else "", "", int(bool(rec.get("acc", 0))))
    if source == "BBH":
        pred_i = max(range(len(fr)), key=lambda i: float(fr[i][0])) if fr else -1
        choices = [a[1] if isinstance(a, list) else str(a) for a in rec.get("arguments", {}).values()] if isinstance(rec.get("arguments"), dict) else []
        return (rec["doc_id"], task[len("bbh_"):], doc["input"], choices, str(doc["target"]),
                choices[pred_i] if 0 <= pred_i < len(choices) else "", "", int(bool(rec.get("acc_norm", 0))))
    if source == "GPQA":
        pred_i = max(range(len(fr)), key=lambda i: float(fr[i][0])) if fr else -1
        choices = [doc.get("choice1"), doc.get("choice2"), doc.get("choice3"), doc.get("choice4")]
        return (rec["doc_id"], doc.get("High-level domain", "gpqa"), doc["Question"], choices, str(rec.get("target")),
                "ABCD"[pred_i] if 0 <= pred_i < 4 else "", "", int(bool(rec.get("acc_norm", 0))))
    if source == "MUSR":
        pred_i = max(range(len(fr)), key=lambda i: float(fr[i][0])) if fr else -1
        import ast
        choices = doc["choices"] if isinstance(doc["choices"], list) else ast.literal_eval(doc["choices"])
        text = doc["question"] + "\n\n" + doc["narrative"]
        return (rec["doc_id"], task[len("musr_"):], text, choices, str(rec.get("target")),
                choices[pred_i] if 0 <= pred_i < len(choices) else "", "", int(bool(rec.get("acc_norm", 0))))
    if source == "MATH":
        out = fr[0] if fr and isinstance(fr[0], str) else (rec["resps"][0][0] if rec.get("resps") else "")
        return (rec["doc_id"], doc.get("type", task), doc["problem"], None, str(doc.get("answer", rec.get("target"))),
                "", out, int(bool(rec.get("exact_match", 0))))
    if source == "IFEVAL":
        out = fr[0] if fr and isinstance(fr[0], str) else (rec["resps"][0][0] if rec.get("resps") else "")
        return (rec["doc_id"], "ifeval", doc["prompt"], None, json.dumps({"instruction_id_list": doc.get("instruction_id_list"), "kwargs": doc.get("kwargs")}),
                "", out, int(bool(rec.get("prompt_level_strict_acc", False))))
    raise ValueError(source)


def open_db(path):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS corpus_registry (source TEXT PRIMARY KEY, table_name TEXT, id_offset INTEGER, verifier TEXT);
    CREATE TABLE IF NOT EXISTS corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT NOT NULL, upstream_id INTEGER NOT NULL, task TEXT NOT NULL,
        domain TEXT NOT NULL, text TEXT NOT NULL, options_json TEXT, target TEXT, verifier TEXT NOT NULL, generative INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS eval_results (question_id INTEGER NOT NULL, model_name TEXT NOT NULL, category TEXT NOT NULL, question_text TEXT NOT NULL,
        options_json TEXT, gt_answer TEXT, pred TEXT, model_output TEXT NOT NULL, is_correct INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (question_id, model_name));
    CREATE INDEX IF NOT EXISTS idx_eval_model ON eval_results(model_name);
    CREATE INDEX IF NOT EXISTS idx_q_source ON corpus_questions(source, task);
    """)
    for s, off in OFFSET.items():
        con.execute("INSERT OR IGNORE INTO corpus_registry VALUES (?,?,?,?)", (s, "corpus_questions", off, VERIFIER[s]))
    con.commit(); return con


def build(raw, dbpath):
    con = open_db(dbpath); task_index = {}
    models = sorted(d for d in os.listdir(raw) if os.path.isdir(os.path.join(raw, d)))
    print("models: %d | db %s" % (len(models), dbpath), flush=True)
    for m in models:
        files = sorted(glob.glob(os.path.join(raw, m, "**", "*.jsonl"), recursive=True)); n = 0; bad = 0
        for f in files:
            mm = PAT.search(f)
            if not mm: continue
            task = mm.group("task"); src = source_of(task)
            if src is None: continue
            if task not in task_index: task_index[task] = len([t for t in task_index if source_of(t) == src])
            tix = task_index[task]
            qrows = []; erows = []
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    try: rec = json.loads(line)
                    except Exception: bad += 1; continue
                    up, domain, text, opts, target, pred, out, ok = parse(src, task, rec)
                    upstream = up if src == "MMLU_PRO" else tix * 10_000 + int(up)
                    qid = OFFSET[src] + upstream
                    qrows.append((qid, src, upstream, task, domain, text, json.dumps(opts) if opts is not None else None, target, VERIFIER[src], int(src in GENERATIVE)))
                    erows.append((qid, m, domain, text, json.dumps(opts) if opts is not None else None, target, pred, out or "", ok))
            con.executemany("INSERT OR IGNORE INTO corpus_questions VALUES (?,?,?,?,?,?,?,?,?,?)", qrows)
            con.executemany("INSERT OR IGNORE INTO eval_results (question_id, model_name, category, question_text, options_json, gt_answer, pred, model_output, is_correct) VALUES (?,?,?,?,?,?,?,?,?)", erows)
            # Tier-b side of every ingested item (FRAMEWORK Stage 0 rule b): content_key over the stem, the
            # options and the corpus verifier; recorded write-once with the per-row assertion; family_id is
            # reserved (no corpus metadata declares families yet). A pinned corpus keeps its id-file pool;
            # the item_side rows only say what f would assign a NEW item.
            side_rows = []
            for (qid, s_, up_, task_, domain_, text_, opts_json, target_, verifier_, gen_) in qrows:
                ck = split_side.content_key(text_, json.loads(opts_json) if opts_json else [], verifier_)
                side_rows.append((ck, None, split_side.tier_b(None, ck), verifier_, "%s/%s" % (s_, domain_)))
            split_side.record_sides(con, side_rows, pool_id_at_ingest=None, now_millis=int(time.time() * 1000))
            n += len(erows)
        con.commit(); print("  %-32s %6d rows%s" % (m, n, "" if not bad else " (%d bad lines)" % bad), flush=True)
    summary(con)


def summary(con):
    print("\nper corpus: questions | models | mean accuracy | generative")
    for s, nq, nm, acc, gen in con.execute("SELECT q.source, COUNT(DISTINCT q.question_id), COUNT(DISTINCT e.model_name), AVG(e.is_correct), MAX(q.generative) FROM corpus_questions q JOIN eval_results e USING(question_id) GROUP BY q.source"):
        print("  %-9s %6d | %2d | %.3f | %s" % (s, nq, nm, acc, "yes" if gen else "no (log-likelihood)"))
    print("\nbest model per corpus (mean is_correct):")
    for s in OFFSET:
        r = con.execute("SELECT e.model_name, AVG(e.is_correct) a FROM eval_results e JOIN corpus_questions q USING(question_id) WHERE q.source=? GROUP BY e.model_name ORDER BY a DESC LIMIT 3", (s,)).fetchall()
        if r: print("  %-9s %s" % (s, " | ".join("%s %.3f" % (m, a) for m, a in r)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true"); ap.add_argument("--summary", action="store_true")
    ap.add_argument("--raw", default=RAW); ap.add_argument("--db", default=DB)
    a = ap.parse_args()
    if a.build: build(a.raw, a.db)
    elif a.summary: summary(open_db(a.db))
