"""BFCL-Result multi_turn ingest: the pilot data for AGENT-CORPUS-ADMISSION (plan A10; night schedule
2026-09-18 lane 5; survey docs/agents/leads/2026-09-18_agent_corpora.md section 1.5). Registration: A10
AGENT-CORPUS-ADMISSION in docs/judge_v2_program.md (filed by the registrar on 2026-09-18; this script is the
ingest only, it reads no criterion and writes no outcome). The readout is tools/analysis/agent_admission_pilot.py.

  python tools/ingest/bfcl_ingest.py --selftest                      # synthetic fixture in a temp dir, no network
  python tools/ingest/bfcl_ingest.py --download                      # raw files -> experiment_results/agent/bfcl_raw/<snapshot>/
  python tools/ingest/bfcl_ingest.py --dry-run                       # parse the raw files, print counts, write NOTHING
  python tools/ingest/bfcl_ingest.py --build                         # write experiment_results/agent/bfcl_result_<snapshot>.db (write-once)

Zero LLM calls. Network only under --download (raw.githubusercontent.com, pinned commit shas). No pool_guard
import; no DB of record is opened (not mmlu_pro_dataset_cache_v2.db, not multicorpus_cache_v1.db, nothing under
experiment_results/** except the NEW file this script writes). This corpus has no pool id yet: the first printed
line is "corpus=bfcl_result_<snapshot>".

CORPUS. BFCL-Result (github HuanzhiMao/BFCL-Result, Apache-2.0), date folder 2025-12-16, pinned at the archive
commit ARCHIVE_SHA ("add 12/16 result"). multi_turn v4 = 800 entries = 4 categories x 200: base, miss_func,
miss_param, long_context, templated on the 200 base scenarios (family_id = the base scenario id). Result files
(result/<model>/multi_turn/BFCL_v4_multi_turn_<cat>_result.json, one JSON object per line) carry per entry:
result (list of turns, each a list of per-step model responses), input/output token counts and latency per step,
inference_log (per turn: begin_of_turn_query + step_k lists of assistant / handler_log / tool messages; the
state_info snapshots between turns). Score files (score/<model>/multi_turn/BFCL_v4_multi_turn_<cat>_score.json)
carry line 1 {"accuracy", "correct_count", "total_count"} then ONE RECORD PER FAILED ENTRY (id, valid=false,
error{error_message, error_type, details}, prompt, model_result_raw, model_result_decoded, possible_answer,
inference_log). Passes are the complement: passed = id not listed, asserted against total_count - correct_count.
The task text comes from the gorilla dataset (ShishirPatil/gorilla, bfcl_eval/data/BFCL_v4_multi_turn_<cat>.json
and possible_answer/, pinned at GORILLA_SHA = the last data-directory commit before the snapshot date).

TERMINATION (the 20-step cap). The harness (bfcl_eval/model_handler/base_handler.py, inference_multi_turn_FC)
allows MAXIMUM_STEP_LIMIT = 20 executed steps per turn; on the 21st it appends a handler_log
"Model has been forced to quit after 20 steps." and stops the WHOLE entry. The checker then fails the entry as
multi_turn:force_terminated only when the turn count is short, i.e. a cap hit on the LAST turn is evaluated like
any other entry and can even pass (a hazard the dry-run counts). termination_class per episode:
  step_cap    the force-quit marker is present in the inference log (cross-checked: the capped turn has 21 steps)
  error       the result is not a list ("Error during inference: ..." with a traceback; no inference_log)
  terminated  a list result with an inference log and no marker
  unknown     the entry has no result row at all
Token counts are stored as the sums the handler recorded (NULL when absent); their reliability differs by
handler (claude-* logs tiny input counts), so they are provenance, not a cap proxy.
The REGISTERED proxy bfcl_term_v1 (AGENT-CORPUS-ADMISSION, programme L5855ff: "any turn's step count >= 20 -> CAP_HIT;
an entry absent from the result file or carrying a harness/API error -> ERROR; else TERMINATED") is stored beside it
as its literal reading over the per-turn response counts (column bfcl_term_v1). The two differ where a turn ends by
the model's own text reply after 19 or 20 executed calls (20 or 21 responses, no force-quit marker): the literal rule
reads CAP_HIT, the marker rule TERMINATED; the dry-run prints the disagreement count. Neither is re-derived from the
checker's multi_turn:force_terminated error, which only fires when the cap shortens the turn count.
SPLIT (rule (a)). tasks.side = split_side.tier_b(family_id, content_key) = the side of the FAMILY hash (norm-v1,
GATE [300, 400)), so the four templates of a base scenario sit on one side by construction (straddling = 0 is
asserted). The pool id (pool_guard.compute_pool_id over the EVAL ids) and the reserved-pool file are NOT written here:
this script imports no pool_guard; the operator exports them under the registration's hygiene paragraph.

SCHEMA of experiment_results/agent/bfcl_result_<snapshot>.db (a NEW file; the script refuses to overwrite):
  meta(key, value)                         corpus, snapshot, archive_sha, gorilla_sha, step_cap, normaliser_version,
                                           key_rule, script_sha, built_at, reading rule (this docstring's TERMINATION)
  agents(agent PK, source_dir, snapshot)   agent = the archive's model directory name (one harness: (scaffold=BFCL FC
                                           handler, model, config, date) is fixed by the archive)
  tasks(task_id PK, category, family_id, stem, content_key, dialogue_key, side, turns, involved_classes)
                                           category in {base, miss_func, miss_param, long_context}; family_id =
                                           'multi_turn_base_<n>'; stem = the first user message of turn 0;
                                           content_key = split_side.stem_key(stem) (norm-v1 / ck-v1, options-free);
                                           dialogue_key = stem_key over every user message of every turn joined by
                                           U+000A (the tool schema is NOT part of either key: the function docs are
                                           not downloaded; involved_classes names them for a later join);
                                           side = tier_b(family_id) in {EVAL, GATE, TRAIN}; turns = user turns
  episodes(task_id, agent, passed, checker_output, error_type, checker_details, checker_sha, steps, max_turn_steps,
           turns_answered, termination_class, bfcl_term_v1, tokens_in, tokens_out, latency_s,
           PRIMARY KEY (task_id, agent))
                                           passed 0/1 from the score file; checker_output = 'PASS' or
                                           '<error_type>: <error_message>'; checker_details = the checker's
                                           expected-vs-actual JSON (compact) or NULL; checker_sha = sha256 of
                                           checker_output + details; steps = model calls over all turns
  files(path, url, bytes, sha256)          provenance of every raw file read
  views checker(task_id, agent, valid, error_text, checker_sha) and provenance(path, bytes, sha256) give the
  registration's table names over episodes and files.
An agent directory missing any of its 8 multi_turn files is recorded in meta (key 'agents_excluded') and excluded; the
count is printed, never silently dropped.
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import tempfile
import time
import urllib.request
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))
import split_side  # the side function's normaliser (tools/analysis/split_side.py); imports nothing of record

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAPSHOT = "2025-12-16"
ARCHIVE_SHA = "6830ed13035c0cfee9aa7a9a0ffed70f10b3dd50"   # HuanzhiMao/BFCL-Result "add 12/16 result", 2025-12-17T07:51:12Z
GORILLA_SHA = "9d8416a96d1d69975493f1b6d60ff07d12a1726a"   # ShishirPatil/gorilla, last bfcl_eval/data commit before the snapshot
LICENCE = "Apache-2.0 (HuanzhiMao/BFCL-Result LICENSE; gorilla berkeley-function-call-leaderboard README)"
STEP_CAP = 20
CATEGORIES = ("base", "miss_func", "miss_param", "long_context")
TERMINATION_CLASSES = ("terminated", "step_cap", "error", "unknown")
FORCE_QUIT_MARKER = "Model has been forced to quit after"
# The 8 agents of the pilot: the night plan's candidate list (lane 5, decision 5: the author's to confirm) mapped to
# the archive's directory names; all on the FC (native function-calling) handler so the scaffold is one; eight
# providers, four closed frontier models (one reasoning) and four open-weight ones (one function-calling fine-tune).
DEFAULT_MODELS = (
    "claude-sonnet-4-5-20250929-FC",
    "gpt-5.2-2025-12-11-FC",
    "gemini-2.5-flash-FC",
    "DeepSeek-V3.2-Exp-FC",
    "Qwen_Qwen3-32B-FC",
    "grok-4-1-fast-reasoning-FC",
    "meta-llama_Llama-3.3-70B-Instruct-FC",
    "Salesforce_Llama-xLAM-2-70b-fc-r",
)
ARCHIVE_RAW = "https://raw.githubusercontent.com/HuanzhiMao/BFCL-Result/%s/%s/%s/%s/multi_turn/BFCL_v4_multi_turn_%s_%s.json"
GORILLA_RAW = "https://raw.githubusercontent.com/ShishirPatil/gorilla/%s/berkeley-function-call-leaderboard/bfcl_eval/data/%sBFCL_v4_multi_turn_%s.json"


def corpus_name(snapshot):
    return "bfcl_result_%s" % snapshot


def default_raw_dir(snapshot):
    return os.path.join(ROOT, "experiment_results", "agent", "bfcl_raw", snapshot)


def default_db(snapshot):
    return os.path.join(ROOT, "experiment_results", "agent", "%s.db" % corpus_name(snapshot))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def script_sha():
    return sha256_file(os.path.abspath(__file__))


# --------------------------------------------------------------------------------------------------------------
# raw file layout
# --------------------------------------------------------------------------------------------------------------
def raw_files(raw_dir, models, snapshot=SNAPSHOT, archive_sha=ARCHIVE_SHA, gorilla_sha=GORILLA_SHA):
    """-> list of (relative path, url). Dataset + possible_answer, then result + score per model per category."""
    out = []
    for cat in CATEGORIES:
        out.append(("dataset/BFCL_v4_multi_turn_%s.json" % cat, GORILLA_RAW % (gorilla_sha, "", cat)))
        out.append(("dataset/possible_answer/BFCL_v4_multi_turn_%s.json" % cat, GORILLA_RAW % (gorilla_sha, "possible_answer/", cat)))
    for m in models:
        for kind in ("result", "score"):
            for cat in CATEGORIES:
                rel = "%s/%s/multi_turn/BFCL_v4_multi_turn_%s_%s.json" % (kind, m, cat, kind)
                out.append((rel, ARCHIVE_RAW % (archive_sha, snapshot, kind, m, cat, kind)))
    return out


def fetch(url, dest, retries=4):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "taxoarena-bfcl-ingest/1"})
            with urllib.request.urlopen(req, timeout=180) as r, open(dest + ".part", "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            os.replace(dest + ".part", dest)
            return
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("download failed after %d attempts: %s (%s)" % (retries, url, last))


def download(raw_dir, models, snapshot):
    files = raw_files(raw_dir, models, snapshot)
    manifest = os.path.join(raw_dir, "MANIFEST.txt")
    rows = []
    fetched = skipped = 0
    for rel, url in files:
        dest = os.path.join(raw_dir, rel)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            skipped += 1
        else:
            print("  GET %s" % url, flush=True)
            fetch(url, dest)
            fetched += 1
        rows.append((rel, url, os.path.getsize(dest), sha256_file(dest)))
    with open(manifest, "w", encoding="utf-8") as f:
        f.write("# BFCL-Result multi_turn raw files, snapshot %s\n" % snapshot)
        f.write("# archive HuanzhiMao/BFCL-Result @ %s ; dataset ShishirPatil/gorilla @ %s\n" % (ARCHIVE_SHA, GORILLA_SHA))
        f.write("# licence: %s\n" % LICENCE)
        f.write("# downloaded_at: %s ; script_sha: %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), script_sha()))
        f.write("# columns: path<TAB>bytes<TAB>sha256<TAB>url\n")
        for rel, url, n, h in rows:
            f.write("%s\t%d\t%s\t%s\n" % (rel, n, h, url))
    total = sum(r[2] for r in rows)
    print("download: %d files (%d fetched, %d already present), %.1f MB, manifest %s" % (len(rows), fetched, skipped, total / 1e6, manifest))
    return rows


# --------------------------------------------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------------------------------------------
def read_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError("%s line %d: %s" % (path, ln, e))
    return out


_ID_RE = re.compile(r"^multi_turn_(base|miss_func|miss_param|long_context)_(\d+)$")


def parse_task_id(task_id):
    m = _ID_RE.match(task_id)
    if not m:
        raise ValueError("unrecognised task id %r" % task_id)
    return m.group(1), int(m.group(2))


def first_user_stem(question):
    """The first user message of turn 0. question = list of turns, each a list of {role, content}."""
    if not question or not question[0]:
        raise ValueError("empty question")
    for msg in question[0]:
        if msg.get("role") == "user":
            c = msg.get("content")
            if isinstance(c, list):  # content blocks
                c = " ".join(b.get("text", "") for b in c if isinstance(b, dict))
            return str(c)
    raise ValueError("turn 0 has no user message")


def load_tasks(raw_dir):
    """-> dict task_id -> row dict (category, family_id, stem, content_key, turns, involved_classes)."""
    tasks = {}
    for cat in CATEGORIES:
        path = os.path.join(raw_dir, "dataset", "BFCL_v4_multi_turn_%s.json" % cat)
        for e in read_jsonl(path):
            c, n = parse_task_id(e["id"])
            if c != cat:
                raise ValueError("%s: id %s in the %s file" % (path, e["id"], cat))
            stem = first_user_stem(e["question"])
            dialogue = "\n".join(str(m.get("content")) for turn in e["question"] for m in turn if m.get("role") == "user")
            family_id = "multi_turn_base_%d" % n
            ck = split_side.stem_key(stem)
            tasks[e["id"]] = {
                "task_id": e["id"], "category": cat, "family_id": family_id, "stem": stem,
                "content_key": ck, "dialogue_key": split_side.stem_key(dialogue), "side": split_side.tier_b(family_id, ck),
                "turns": len(e["question"]),
                "involved_classes": json.dumps(e.get("involved_classes", []), separators=(",", ":")),
            }
    # rule (a): a family sits on one side (side is a function of family_id; asserted anyway)
    fam_sides = defaultdict(set)
    for t in tasks.values():
        fam_sides[t["family_id"]].add(t["side"])
    straddling = [f for f, ss in fam_sides.items() if len(ss) > 1]
    if straddling:
        raise AssertionError("families on more than one side: %s" % straddling[:5])
    return tasks


def load_score(path):
    """-> (header dict, failures dict id -> {error_type, error_message, details})."""
    recs = read_jsonl(path)
    if not recs or not {"accuracy", "correct_count", "total_count"} <= set(recs[0]):
        raise ValueError("%s: line 1 is not the accuracy header" % path)
    header = recs[0]
    failures = {}
    for r in recs[1:]:
        if r.get("valid") is not False:
            raise ValueError("%s: record %s has valid=%r (only failures are listed)" % (path, r.get("id"), r.get("valid")))
        err = r.get("error") or {}
        if isinstance(err, dict):
            msg = err.get("error_message", "")
            if isinstance(msg, list):
                msg = " | ".join(str(x) for x in msg)
            failures[r["id"]] = {"error_type": str(err.get("error_type", "")), "error_message": str(msg),
                                 "details": err.get("details")}
        else:
            failures[r["id"]] = {"error_type": "unstructured", "error_message": str(err), "details": None}
    if len(failures) != header["total_count"] - header["correct_count"]:
        raise ValueError("%s: %d failure records but total_count - correct_count = %d" %
                         (path, len(failures), header["total_count"] - header["correct_count"]))
    return header, failures


def load_result(path):
    return {e["id"]: e for e in read_jsonl(path)}


def _sum_nested(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return x
    if isinstance(x, list):
        vals = [_sum_nested(v) for v in x]
        vals = [v for v in vals if v is not None]
        return sum(vals) if vals else 0
    return None


def find_marker(inference_log):
    """-> (marker_found, steps_in_capped_turn or None). Walks every turn dict's step_k lists."""
    if not isinstance(inference_log, list):
        return False, None
    for turn in inference_log:
        if not isinstance(turn, dict):
            continue
        for k, v in turn.items():
            if not k.startswith("step_") or not isinstance(v, list):
                continue
            for msg in v:
                if isinstance(msg, dict) and msg.get("role") == "handler_log" and str(msg.get("content", "")).startswith(FORCE_QUIT_MARKER):
                    n_steps = len([kk for kk in turn if kk.startswith("step_")])
                    return True, n_steps
    return False, None


def derive_episode(task_id, agent, entry, failure):
    """One episodes row. entry = the result-file record or None; failure = the score-file record or None."""
    passed = 0 if failure is not None else 1
    if failure is None:
        checker_output, error_type, details = "PASS", None, None
    else:
        error_type = failure["error_type"]
        checker_output = "%s: %s" % (error_type, failure["error_message"])
        details = json.dumps(failure["details"], separators=(",", ":"), ensure_ascii=False, sort_keys=True) if failure["details"] is not None else None
    checker_sha = hashlib.sha256((checker_output + "" + (details or "")).encode("utf-8")).hexdigest()
    steps = max_turn_steps = turns_answered = tokens_in = tokens_out = latency = None
    hazards = []
    if entry is None:
        cls = "unknown"
    else:
        res = entry.get("result")
        log = entry.get("inference_log")
        if not isinstance(res, list) or "traceback" in entry:
            cls = "error"
        else:
            turns_answered = len(res)
            per_turn = [len(t) if isinstance(t, list) else 0 for t in res]
            steps = sum(per_turn)
            max_turn_steps = max(per_turn) if per_turn else 0
            tokens_in = _sum_nested(entry.get("input_token_count"))
            tokens_out = _sum_nested(entry.get("output_token_count"))
            latency = _sum_nested(entry.get("latency"))
            marker, n_capped = find_marker(log)
            if marker:
                cls = "step_cap"
                if n_capped != STEP_CAP + 1:
                    hazards.append("%s/%s: force-quit marker but the capped turn logs %s steps (expected %d)" % (agent, task_id, n_capped, STEP_CAP + 1))
            elif isinstance(log, list):
                cls = "terminated"
                if max_turn_steps > STEP_CAP + 1:
                    hazards.append("%s/%s: no marker but a turn has %d responses (> cap+1)" % (agent, task_id, max_turn_steps))
            else:
                cls = "unknown"
                hazards.append("%s/%s: list result without an inference_log" % (agent, task_id))
    # the registered literal proxy (bfcl_term_v1): step count >= 20 in any turn -> CAP_HIT; absent / error -> ERROR
    if cls in ("error", "unknown"):
        term_v1 = "ERROR"
    elif max_turn_steps is not None and max_turn_steps >= STEP_CAP:
        term_v1 = "CAP_HIT"
    else:
        term_v1 = "TERMINATED"
    if failure is not None and failure["error_type"] == "multi_turn:force_terminated" and cls != "step_cap":
        hazards.append("%s/%s: checker says force_terminated but the log class is %s" % (agent, task_id, cls))
    row = {"task_id": task_id, "agent": agent, "passed": passed, "checker_output": checker_output, "error_type": error_type,
           "checker_details": details, "checker_sha": checker_sha, "steps": steps, "max_turn_steps": max_turn_steps,
           "turns_answered": turns_answered, "termination_class": cls, "bfcl_term_v1": term_v1, "tokens_in": tokens_in,
           "tokens_out": tokens_out, "latency_s": latency}
    return row, hazards


def ingest(raw_dir, models, snapshot, verbose=True):
    """Parse everything. -> (tasks, episodes list, agents list, files list, hazards list)."""
    tasks = load_tasks(raw_dir)
    by_cat = Counter(t["category"] for t in tasks.values())
    if verbose:
        print("tasks: %d (%s)" % (len(tasks), ", ".join("%s=%d" % (c, by_cat[c]) for c in CATEGORIES)))
    hazards = []
    # stem identity across the four templates of a family (the family is the split unit either way)
    fam = defaultdict(dict)
    for t in tasks.values():
        fam[t["family_id"]][t["category"]] = t["content_key"]
    same = Counter()
    for f, d in fam.items():
        if "base" in d:
            for c in CATEGORIES[1:]:
                if c in d:
                    same[c] += int(d[c] == d["base"])
    if verbose:
        print("stem identity with base (content_key equal, per category): " + ", ".join("%s %d/%d" % (c, same[c], by_cat[c]) for c in CATEGORIES[1:]))
    if verbose:
        sides = Counter((t["category"], t["side"]) for t in tasks.values())
        print("sides by family hash (tier_b, norm-v1): " + "; ".join("%s EVAL %d GATE %d TRAIN %d" % (c, sides[(c, "EVAL")], sides[(c, "GATE")], sides[(c, "TRAIN")]) for c in CATEGORIES) + "; straddling families 0")
    episodes, agents, files, excluded = [], [], [], []
    for cat in CATEGORIES:
        for rel in ("dataset/BFCL_v4_multi_turn_%s.json" % cat, "dataset/possible_answer/BFCL_v4_multi_turn_%s.json" % cat):
            p = os.path.join(raw_dir, rel)
            if os.path.exists(p):
                files.append({"path": rel, "bytes": os.path.getsize(p), "sha256": sha256_file(p)})
    for m in models:
        paths = []
        for cat in CATEGORIES:
            paths.append(os.path.join(raw_dir, "result", m, "multi_turn", "BFCL_v4_multi_turn_%s_result.json" % cat))
            paths.append(os.path.join(raw_dir, "score", m, "multi_turn", "BFCL_v4_multi_turn_%s_score.json" % cat))
        missing = [p for p in paths if not os.path.exists(p)]
        if missing:
            excluded.append(m)
            hazards.append("%s: EXCLUDED, %d of 8 multi_turn files missing (e.g. %s)" % (m, len(missing), os.path.relpath(missing[0], raw_dir)))
            continue
        agents.append({"agent": m, "source_dir": "%s/result/%s" % (snapshot, m), "snapshot": snapshot})
        for cat in CATEGORIES:
            rpath = os.path.join(raw_dir, "result", m, "multi_turn", "BFCL_v4_multi_turn_%s_result.json" % cat)
            spath = os.path.join(raw_dir, "score", m, "multi_turn", "BFCL_v4_multi_turn_%s_score.json" % cat)
            for p in (rpath, spath):
                files.append({"path": os.path.relpath(p, raw_dir).replace("\\", "/"), "bytes": os.path.getsize(p), "sha256": sha256_file(p)})
            header, failures = load_score(spath)
            results = load_result(rpath)
            ids = [tid for tid, t in tasks.items() if t["category"] == cat]
            if header["total_count"] != len(ids):
                hazards.append("%s/%s: score total_count %d != %d dataset ids" % (m, cat, header["total_count"], len(ids)))
            unknown_fail = set(failures) - set(ids)
            if unknown_fail:
                hazards.append("%s/%s: %d failure ids not in the dataset: %s" % (m, cat, len(unknown_fail), sorted(unknown_fail)[:3]))
            extra_res = set(results) - set(ids)
            if extra_res:
                hazards.append("%s/%s: %d result ids not in the dataset" % (m, cat, len(extra_res)))
            missing_res = [tid for tid in ids if tid not in results]
            if missing_res:
                hazards.append("%s/%s: %d dataset ids without a result row (termination_class=unknown)" % (m, cat, len(missing_res)))
            for tid in ids:
                row, hz = derive_episode(tid, m, results.get(tid), failures.get(tid))
                episodes.append(row)
                hazards.extend(hz)
    if verbose:
        print("agents requested %d, ingested %d, excluded %d%s" % (len(models), len(agents), len(excluded), (": " + ",".join(excluded)) if excluded else ""))
    if not agents:
        raise FileNotFoundError("no agent has its 8 multi_turn files under %s (run --download first)" % raw_dir)
    ingest.excluded = excluded
    return tasks, episodes, agents, files, hazards


def summarise(tasks, episodes, agents):
    """Counts per category and per agent (episodes, passes, termination classes)."""
    cat_of = {t: tasks[t]["category"] for t in tasks}
    lines = []
    lines.append("agents: %d" % len(agents))
    lines.append("episodes: %d" % len(episodes))
    lines.append("marker class (termination_class): term/cap/err/unk; registered literal bfcl_term_v1: TERM/CAP/ERR")
    lines.append("%-40s %-13s %5s %5s %6s %5s %5s %5s %5s | %5s %5s %5s" % ("agent", "category", "n", "pass", "rate", "term", "cap", "err", "unk", "TERM", "CAP", "ERR"))
    def block(rows, agent_label, cat_label):
        n = len(rows)
        p = sum(r["passed"] for r in rows)
        tc = Counter(r["termination_class"] for r in rows)
        tv = Counter(r["bfcl_term_v1"] for r in rows)
        lines.append("%-40s %-13s %5d %5d %6.3f %5d %5d %5d %5d | %5d %5d %5d" % (agent_label, cat_label, n, p, (p / n if n else float("nan")),
                                                                    tc["terminated"], tc["step_cap"], tc["error"], tc["unknown"],
                                                                    tv["TERMINATED"], tv["CAP_HIT"], tv["ERROR"]))
    for a in agents:
        rows_a = [r for r in episodes if r["agent"] == a["agent"]]
        for cat in CATEGORIES:
            block([r for r in rows_a if cat_of[r["task_id"]] == cat], a["agent"], cat)
        block(rows_a, a["agent"], "ALL")
    for cat in CATEGORIES:
        block([r for r in episodes if cat_of[r["task_id"]] == cat], "ALL", cat)
    block(episodes, "ALL", "ALL")
    dis = sum(1 for r in episodes if (r["termination_class"] == "step_cap") != (r["bfcl_term_v1"] == "CAP_HIT"))
    lines.append("marker class vs registered literal rule (>= %d responses in a turn) disagree on %d of %d episodes" % (STEP_CAP, dis, len(episodes)))
    cap_pass = sum(1 for r in episodes if r["termination_class"] == "step_cap" and r["passed"])
    lines.append("step_cap episodes that the checker PASSED (cap hit on the last turn): %d" % cap_pass)
    et = Counter(r["error_type"] for r in episodes if r["error_type"])
    lines.append("checker error_type counts: " + ", ".join("%s=%d" % kv for kv in et.most_common()))
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------------------------
# DB
# --------------------------------------------------------------------------------------------------------------
DDL = """
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE agents(agent TEXT PRIMARY KEY, source_dir TEXT NOT NULL, snapshot TEXT NOT NULL);
CREATE TABLE tasks(task_id TEXT PRIMARY KEY,
                   category TEXT NOT NULL CHECK(category IN ('base','miss_func','miss_param','long_context')),
                   family_id TEXT NOT NULL, stem TEXT NOT NULL, content_key TEXT NOT NULL, dialogue_key TEXT NOT NULL,
                   side TEXT NOT NULL CHECK(side IN ('EVAL','GATE','TRAIN')), turns INTEGER NOT NULL,
                   involved_classes TEXT NOT NULL);
CREATE TABLE episodes(task_id TEXT NOT NULL REFERENCES tasks(task_id), agent TEXT NOT NULL REFERENCES agents(agent),
                      passed INTEGER NOT NULL CHECK(passed IN (0,1)), checker_output TEXT NOT NULL, error_type TEXT,
                      checker_details TEXT, checker_sha TEXT NOT NULL, steps INTEGER, max_turn_steps INTEGER,
                      turns_answered INTEGER, termination_class TEXT NOT NULL
                        CHECK(termination_class IN ('terminated','step_cap','error','unknown')),
                      bfcl_term_v1 TEXT NOT NULL CHECK(bfcl_term_v1 IN ('TERMINATED','CAP_HIT','ERROR')),
                      tokens_in REAL, tokens_out REAL, latency_s REAL, PRIMARY KEY (task_id, agent));
CREATE TABLE files(path TEXT PRIMARY KEY, bytes INTEGER NOT NULL, sha256 TEXT NOT NULL);
CREATE INDEX episodes_agent ON episodes(agent);
CREATE VIEW checker AS SELECT task_id, agent, passed AS valid, checker_output AS error_text, checker_sha FROM episodes;
CREATE VIEW provenance AS SELECT path, bytes, sha256 FROM files;
"""


def build_db(db_path, tasks, episodes, agents, files, snapshot):
    if os.path.exists(db_path):
        raise FileExistsError("%s exists; this script is write-once (delete it by hand if a rebuild is intended)" % db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    tmp = db_path + ".building"
    if os.path.exists(tmp):
        os.remove(tmp)
    conn = sqlite3.connect(tmp)
    try:
        conn.executescript(DDL)
        conn.executemany("INSERT INTO agents VALUES (?,?,?)", [(a["agent"], a["source_dir"], a["snapshot"]) for a in agents])
        conn.executemany("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)",
                         [(t["task_id"], t["category"], t["family_id"], t["stem"], t["content_key"], t["dialogue_key"], t["side"],
                           t["turns"], t["involved_classes"]) for t in tasks.values()])
        cols = ["task_id", "agent", "passed", "checker_output", "error_type", "checker_details", "checker_sha", "steps",
                "max_turn_steps", "turns_answered", "termination_class", "bfcl_term_v1", "tokens_in", "tokens_out", "latency_s"]
        conn.executemany("INSERT INTO episodes(%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))),
                         [tuple(r[c] for c in cols) for r in episodes])
        conn.executemany("INSERT INTO files VALUES (?,?,?)", [(f["path"], f["bytes"], f["sha256"]) for f in files])
        meta = {"corpus": corpus_name(snapshot), "snapshot": snapshot, "archive_sha": ARCHIVE_SHA, "gorilla_sha": GORILLA_SHA,
                "licence": LICENCE, "step_cap": str(STEP_CAP), "normaliser_version": split_side.NORMALISER_VERSION,
                "key_rule": split_side.KEY_RULE + " (stem_key: options-free)", "script_sha": script_sha(),
                "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "termination_rule": "step_cap = handler_log '%s' present; error = non-list result / traceback; "
                                    "terminated = list result with inference_log and no marker; unknown = no result row. "
                                    "passed = id absent from the score file's failure records." % FORCE_QUIT_MARKER,
                "term_v1_rule": "bfcl_term_v1: CAP_HIT if any turn has >= %d responses; ERROR if no result row / non-list result; "
                                "else TERMINATED (the registration's literal proxy, AGENT-CORPUS-ADMISSION)" % STEP_CAP,
                "side_rule": "tasks.side = split_side.tier_b(family_id, content_key): the family hash under norm-v1; no pool id "
                             "computed here (pool_guard is not imported); EVAL list export is the operator's step",
                "agents_excluded": ",".join(getattr(ingest, "excluded", []) or []) or "none",
                "pool_id": "NONE (no pool declared for this corpus yet)"}
        conn.executemany("INSERT INTO meta VALUES (?,?)", list(meta.items()))
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp, db_path)
    return db_path


# --------------------------------------------------------------------------------------------------------------
# selftest on a synthetic fixture
# --------------------------------------------------------------------------------------------------------------
def _fixture(raw_dir):
    """Two categories x 3 tasks x 2 agents with planted classes: pass, state mismatch, cap-hit-and-pass,
    cap-hit-and-fail (short turn count), inference error, missing result row."""
    os.makedirs(os.path.join(raw_dir, "dataset", "possible_answer"), exist_ok=True)
    stems = {0: "Move  'a.txt' to temp", 1: "Post a tweet", 2: "Book a flight"}
    for cat in CATEGORIES:
        with open(os.path.join(raw_dir, "dataset", "BFCL_v4_multi_turn_%s.json" % cat), "w", encoding="utf-8") as f:
            for i in range(3):
                q = [[{"role": "user", "content": stems[i] + (" (long)" if cat == "long_context" else "")}], [{"role": "user", "content": "then verify"}]]
                f.write(json.dumps({"id": "multi_turn_%s_%d" % (cat, i), "question": q, "involved_classes": ["GorillaFileSystem"]}) + "\n")
        with open(os.path.join(raw_dir, "dataset", "possible_answer", "BFCL_v4_multi_turn_%s.json" % cat), "w", encoding="utf-8") as f:
            for i in range(3):
                f.write(json.dumps({"id": "multi_turn_%s_%d" % (cat, i), "ground_truth": [["ls()"], ["ls()"]]}) + "\n")

    def step_log(n, capped=False):
        d = {"begin_of_turn_query": [{"role": "user", "content": "x"}]}
        for k in range(n):
            steps = [{"role": "assistant", "content": [{"ls": "{}"}]}, {"role": "handler_log", "content": "Successfully decoded model response.", "model_response_decoded": ["ls()"]}, {"role": "tool", "content": "{}"}]
            if capped and k == n - 1:
                steps.append({"role": "handler_log", "content": "Model has been forced to quit after 20 steps."})
            d["step_%d" % k] = steps
        return d

    def entry(tid, turns_steps, capped_last=False, error=False):
        if error:
            return {"id": tid, "result": "Error during inference: boom", "traceback": "Traceback ..."}
        res = [[[{"ls": "{}"}]] * n for n in turns_steps]
        log = [[{"role": "state_info", "class_name": "GorillaFileSystem", "content": {}}]]
        for j, n in enumerate(turns_steps):
            log.append(step_log(n, capped=(capped_last and j == len(turns_steps) - 1)))
            log.append([{"role": "state_info", "class_name": "GorillaFileSystem", "content": {}}])
        return {"id": tid, "result": res, "input_token_count": [[10] * n for n in turns_steps], "output_token_count": [[5] * n for n in turns_steps],
                "latency": [[0.5] * n for n in turns_steps], "inference_log": log}

    def failure(tid, etype, msg, details=None):
        return {"id": tid, "model_name": "m", "test_category": "x", "valid": False, "error": {"error_message": msg, "error_type": etype, "details": details}}

    for agent in ("agentA", "agentB"):
        for cat in CATEGORIES:
            os.makedirs(os.path.join(raw_dir, "result", agent, "multi_turn"), exist_ok=True)
            os.makedirs(os.path.join(raw_dir, "score", agent, "multi_turn"), exist_ok=True)
            ids = ["multi_turn_%s_%d" % (cat, i) for i in range(3)]
            if agent == "agentA":
                # 0 pass (2 turns, 3+2 steps); 1 state mismatch; 2 cap hit on the LAST turn and PASS
                results = [entry(ids[0], [3, 2]), entry(ids[1], [2, 2]), entry(ids[2], [2, 21], capped_last=True)]
                fails = [failure(ids[1], "multi_turn:instance_state_mismatch", ["Model instance for GorillaFileSystem does not match the state with ground truth instance."], {"differences": {"root": {"model": "a", "ground_truth": "b"}}})]
                header = {"accuracy": 2 / 3, "correct_count": 2, "total_count": 3}
            else:
                # 0 cap hit on the FIRST turn -> force_terminated failure; 1 inference error; 2 MISSING result row (fails)
                results = [entry(ids[0], [21], capped_last=True), entry(ids[1], [], error=True)]
                fails = [failure(ids[0], "multi_turn:force_terminated", ["Model was force-terminated during inference phase."]),
                         failure(ids[1], "multi_turn:inference_error", ["Error during inference phase. Model did not output a list of model responses."]),
                         failure(ids[2], "multi_turn:empty_turn_model_response", ["Model response list is empty for turn 0"])]
                header = {"accuracy": 0.0, "correct_count": 0, "total_count": 3}
            with open(os.path.join(raw_dir, "result", agent, "multi_turn", "BFCL_v4_multi_turn_%s_result.json" % cat), "w", encoding="utf-8") as f:
                for r in results:
                    f.write(json.dumps(r) + "\n")
            with open(os.path.join(raw_dir, "score", agent, "multi_turn", "BFCL_v4_multi_turn_%s_score.json" % cat), "w", encoding="utf-8") as f:
                f.write(json.dumps(header) + "\n")
                for r in fails:
                    f.write(json.dumps(r) + "\n")


def selftest():
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw")
        _fixture(raw)
        tasks, episodes, agents, files, hazards = ingest(raw, ["agentA", "agentB"], "selftest", verbose=False)
        assert len(tasks) == 12 and len(episodes) == 24 and len(agents) == 2, (len(tasks), len(episodes), len(agents))
        # normaliser: NBSP and the double space collapse; the long_context stem differs from base by design
        t0 = tasks["multi_turn_base_0"]
        assert t0["content_key"] == split_side.stem_key("move 'a.txt' to temp"), t0["content_key"]
        assert tasks["multi_turn_miss_func_0"]["content_key"] == t0["content_key"]
        assert tasks["multi_turn_long_context_0"]["content_key"] != t0["content_key"]
        assert all(tasks["multi_turn_%s_%d" % (c, i)]["family_id"] == "multi_turn_base_%d" % i for c in CATEGORIES for i in range(3))
        assert all(len({tasks["multi_turn_%s_%d" % (c, i)]["side"] for c in CATEGORIES}) == 1 for i in range(3))
        assert tasks["multi_turn_base_0"]["side"] == split_side.tier_b("multi_turn_base_0", "ignored-when-family-present")
        assert tasks["multi_turn_base_0"]["dialogue_key"] == split_side.stem_key("move 'a.txt' to temp\nthen verify")
        ep = {(r["agent"], r["task_id"]): r for r in episodes}
        a = ep[("agentA", "multi_turn_base_0")]
        assert (a["passed"], a["termination_class"], a["steps"], a["max_turn_steps"], a["tokens_in"], a["checker_output"]) == (1, "terminated", 5, 3, 50, "PASS"), a
        assert a["bfcl_term_v1"] == "TERMINATED"
        assert ep[("agentA", "multi_turn_base_2")]["bfcl_term_v1"] == "CAP_HIT" and ep[("agentB", "multi_turn_base_1")]["bfcl_term_v1"] == "ERROR" and ep[("agentB", "multi_turn_base_2")]["bfcl_term_v1"] == "ERROR"
        # the literal rule reads a self-stopped 20-response turn as CAP_HIT; the marker rule does not
        r20, hz20 = derive_episode("multi_turn_base_0", "agentX", {"id": "multi_turn_base_0", "result": [[[{"ls": "{}"}]] * 20], "inference_log": [{"begin_of_turn_query": [], "step_0": []}]}, None)
        assert (r20["termination_class"], r20["bfcl_term_v1"]) == ("terminated", "CAP_HIT"), r20
        b = ep[("agentA", "multi_turn_base_1")]
        assert b["passed"] == 0 and b["termination_class"] == "terminated" and b["error_type"] == "multi_turn:instance_state_mismatch", b
        assert b["checker_output"].startswith("multi_turn:instance_state_mismatch: Model instance") and '"ground_truth":"b"' in b["checker_details"], b
        c = ep[("agentA", "multi_turn_base_2")]
        assert c["passed"] == 1 and c["termination_class"] == "step_cap" and c["max_turn_steps"] == 21, c
        d = ep[("agentB", "multi_turn_base_0")]
        assert d["passed"] == 0 and d["termination_class"] == "step_cap" and d["error_type"] == "multi_turn:force_terminated", d
        e = ep[("agentB", "multi_turn_base_1")]
        assert e["passed"] == 0 and e["termination_class"] == "error" and e["steps"] is None, e
        f = ep[("agentB", "multi_turn_base_2")]
        assert f["passed"] == 0 and f["termination_class"] == "unknown", f
        assert any("without a result row" in h for h in hazards), hazards
        assert not any("checker says force_terminated" in h for h in hazards), hazards
        txt = summarise(tasks, episodes, agents)
        assert "step_cap episodes that the checker PASSED (cap hit on the last turn): 4" in txt, txt
        db = os.path.join(td, "t.db")
        build_db(db, tasks, episodes, agents, files, "selftest")
        conn = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
        try:
            n = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
            cls = dict(conn.execute("SELECT termination_class, COUNT(*) FROM episodes GROUP BY 1").fetchall())
            assert n == 24 and cls == {"terminated": 8, "step_cap": 8, "error": 4, "unknown": 4}, (n, cls)
            assert conn.execute("SELECT value FROM meta WHERE key='corpus'").fetchone()[0] == "bfcl_result_selftest"
            assert conn.execute("SELECT COUNT(*) FROM checker WHERE valid=0").fetchone()[0] == 16
            assert conn.execute("SELECT COUNT(*) FROM provenance").fetchone()[0] == 24  # 8 dataset + 2 agents x 4 categories x 2 kinds
        finally:
            conn.close()
        # a missing agent is excluded and counted, not fatal
        _, eps2, ag2, _, hz2 = ingest(raw, ["agentA", "agentZ"], "selftest", verbose=False)
        assert [x["agent"] for x in ag2] == ["agentA"] and len(eps2) == 12 and any("agentZ: EXCLUDED" in h for h in hz2), hz2
        try:
            build_db(db, tasks, episodes, agents, files, "selftest")
            raise AssertionError("write-once guard did not fire")
        except FileExistsError:
            pass
        # the score-file arithmetic guard
        spath = os.path.join(raw, "score", "agentA", "multi_turn", "BFCL_v4_multi_turn_base_score.json")
        with open(spath, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"id": "multi_turn_base_0", "valid": False, "error": {"error_message": "x", "error_type": "y"}}) + "\n")
        try:
            load_score(spath)
            raise AssertionError("failure-count guard did not fire")
        except ValueError:
            pass
    print("selftest OK: 12 tasks, 24 episodes, classes terminated/step_cap/error/unknown planted and recovered; "
          "cap-hit-on-last-turn PASS recovered; write-once and score-arithmetic guards fire")


# --------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--snapshot", default=SNAPSHOT)
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS), help="comma-separated archive directory names")
    ap.add_argument("--raw-dir", default=None)
    ap.add_argument("--db", default=None)
    ap.add_argument("--download", action="store_true", help="fetch the raw files that are missing; write MANIFEST.txt")
    ap.add_argument("--dry-run", action="store_true", help="parse and print counts; write nothing")
    ap.add_argument("--build", action="store_true", help="write the DB (write-once)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    print("corpus=%s" % corpus_name(a.snapshot), flush=True)
    if a.selftest:
        selftest()
        return 0
    models = [m for m in a.models.split(",") if m]
    raw_dir = a.raw_dir or default_raw_dir(a.snapshot)
    db = a.db or default_db(a.snapshot)
    print("snapshot=%s archive_sha=%s gorilla_sha=%s step_cap=%d" % (a.snapshot, ARCHIVE_SHA, GORILLA_SHA, STEP_CAP))
    print("raw_dir=%s" % raw_dir)
    print("models(%d)=%s" % (len(models), ",".join(models)))
    if not (a.download or a.dry_run or a.build):
        ap.error("one of --download / --dry-run / --build / --selftest")
    if a.download:
        download(raw_dir, models, a.snapshot)
    if a.dry_run or a.build:
        tasks, episodes, agents, files, hazards = ingest(raw_dir, models, a.snapshot)
        print(summarise(tasks, episodes, agents))
        print("hazards: %d" % len(hazards))
        for h in hazards[:60]:
            print("  " + h)
        if len(hazards) > 60:
            print("  ... %d more" % (len(hazards) - 60))
        if a.dry_run and not a.build:
            print("dry-run: nothing written")
        if a.build:
            out = build_db(db, tasks, episodes, agents, files, a.snapshot)
            print("built %s (%.1f MB)" % (out, os.path.getsize(out) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
