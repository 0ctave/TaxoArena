"""AGENT-CORPUS-ADMISSION pilot readout (registered 2026-09-18 in docs/judge_v2_program.md, section
"Registered 2026-09-18 (before any code or call) - AGENT-CORPUS-ADMISSION", programme L5855-L5982, commit 9cbd5ab;
plan A10; night schedule 2026-09-18 lane 5; lead docs/agents/leads/2026-09-17_judge_loop2.md section 2).

Launch sequence (every step zero LLM calls, zero network; the ingest DB is opened mode=ro; no DB of record is touched):
  python tools/analysis/agent_admission_pilot.py --selftest          # synthetic corpus in a temp dir; every guard exercised
  python tools/analysis/agent_admission_pilot.py --dry-run           # counts only (per agent x stratum; pairwise decidable share); writes nothing
  python tools/analysis/agent_admission_pilot.py --draw              # the 300-episode draw -> experiment_results/agent/bfcl_admission_pilot_draw.csv (write-once)
  python tools/analysis/agent_admission_pilot.py --labels-template   # 50 drawn episodes with EMPTY manual columns -> ..._labels_TEMPLATE.csv (write-once)
  <an independent labeller fills experiment_results/agent/bfcl_admission_pilot_labels.csv from the RAW result/score files>
  python tools/analysis/agent_admission_pilot.py --run               # refuses without 50 filled labels; writes bfcl_admission_pilot.txt ONCE
                                                                     # and experiment_configs/reserved_pool_frozen_bfcl_<id>.json ONCE

Input: experiment_results/agent/bfcl_result_2025-12-16.db built by tools/ingest/bfcl_ingest.py (tables meta, agents, tasks,
episodes; views checker, provenance). This corpus has no pool id until --run exports one, so the first printed line is
"corpus=<meta.corpus>" and the second "pool_id=<id or NONE>". pool_guard is imported ONLY inside the export step
(checked 2026-09-18: tools/analysis/pool_guard.py opens no database at import time and compute_pool_id is pure hashing;
its module level sets path constants and imports split_side).

THE DRAW (registration "Instrument"): 300 episodes question-stratified: 75 per category (the designed stratum, (e)),
each category's 75 distinct tasks drawn without replacement from the 200 by random.Random(42) (categories in the fixed
order base, miss_func, miss_param, long_context; one rng for the whole draw), and the agents assigned round-robin over a
seeded permutation of the ingested agents so the 75 are spread as evenly as the agent count allows (8 agents: three
agents get 10 and five get 9 per category). Written once as (task_id, agent, category, family_id, side).

THE LABELS (C4): 50 of the 300 drawn episodes (seed 42; 13/13/12/12 over the four categories in the fixed order) are
listed in the TEMPLATE with the raw result and score file paths and EMPTY passed_manual / termination_manual / notes
columns. The labeller reads the raw files and writes passed_manual in {0,1} (1 = the id is ABSENT from the score
file's failure records) and termination_manual in {TERMINATED, CAP_HIT, ERROR} (bfcl_term_v1's rule: any turn with
>= 20 responses in the result file -> CAP_HIT; no result row or a non-list result -> ERROR; else TERMINATED). The labels
file must be written BEFORE --run prints any D_c (the registration's order); --run refuses a template with an empty
cell, a value outside the alphabet, or a (task_id, agent) set different from the template's. Reproduction = the share
of the 50 on which (passed_manual, termination_manual) == (episodes.passed, episodes.bfcl_term_v1); C4 HELD at >= 0.98.

STRICT D_c, THE EXACT DEFINITION TAKEN FROM THE REGISTRATION (part (b) and "Instrument"): an EPISODE is decidable iff
its termination proxy of record is TERMINATED (bfcl_term_v1) AND the checker decided it, i.e. the score file carries a
state- or response-based verdict for it: PASS, or a failure whose error_type is one of multi_turn:instance_state_mismatch,
multi_turn:execution_response_mismatch, multi_turn:empty_turn_model_response, multi_turn:method_invoke_order_mismatch
(multi_turn:force_terminated and multi_turn:inference_error are harness outcomes, not checker decisions; an unknown
error_type is NOT decided and is printed). D_c per stratum = decidable drawn episodes / ALL drawn episodes of the
stratum (cap-hit and error episodes stay in the denominator: rule 10), pooled = over the 300; Wilson 95% intervals;
PASS-AT-POINT iff D_c >= 0.95 at the point, else PREDICTIVE-ONLY (C2). The same share under the ingest's marker class
(termination_class == terminated) is printed beside as a second reading (the two proxies disagree on 6 of 6,400
episodes; see HAZARD NOTES). The coordinator's pair-level reading (both agents' checker verdicts decided AND different
on the same task, the MATCH-FILTER object) is NOT the registered D_c; it cannot be formed on the draw (one agent per
drawn task) and is printed DESCRIPTIVELY on the full table per stratum, denominator = tasks x C(agents, 2).

C1 (parts (a)-(e) verified by command on the ingested tables): (a) tasks.side recomputed per row with split_side.tier_b
(family hash, norm-v1) and compared to the stored side, straddling families counted, the EVAL-side id list exported
write-once as experiment_configs/reserved_pool_frozen_bfcl_<id>.json with id = pool_guard.compute_pool_id over
{"BFCL/<category>": [N ...]} (canonical lines "BFCL/<category>:N", N = the integer suffix of multi_turn_<category>_N;
"BFCL" is not a KNOWN_SOURCE so canonical_line falls to the bare "key:id" form; the registry
experiment_configs/reserved_pools.json is NOT edited: that is the registrar's step); (b) the checker view exists, the
reading rules are in meta (termination_rule, term_v1_rule), and the checker table sha = sha256 over the sorted
"task_id\\tagent\\tchecker_sha" lines is printed; (c) bfcl_term_v1 counts per agent x category, denominator = the agent's
800; (d) the judged artefact = the decoded call sequence + the final state_info text, re-read from the RAW result files
for every drawn episode, its length in characters and an ESTIMATED token count (chars / 4; no tokenizer is run) printed
as a distribution; the per-episode artefact cap is the author's number: printed as given by --artefact-cap-tokens, else
"NOT DECLARED"; fingerprint / provider / response id UNSTAMPED (the archive carries none); (e) stratum = (BFCL, category),
4 strata of 200 tasks each, checked on the tasks table. C1 HELD iff (a), (b), (c), (e) verify and (d)'s artefact is
present for every drawn episode; the undeclared cap is printed, not scored (the registration: "the pilot only prints
the length distribution").
C3: cap-hit share and ERROR share per agent over the agent's DRAWN episodes (denominator = its drawn count), under both
proxies, and per stratum; the terminated share beside every number. Descriptively (the registrar's addition): the
full-table strict D_c and cap-hit share per category x agent over the agent's 800.
Predictions scored exactly as registered: P1 strict D_c < 0.95 at the point in >= 2 of 4 strata AND long_context the
lowest; P2 the median agent's cap-hit share on its full 800 in [0.12, 0.19] (bfcl_term_v1); P3 at least one stratum
PREDICTIVE-ONLY; P4 terminated share >= 0.60 in all 4 strata (on the draw, bfcl_term_v1; the full-table share beside);
the registrar's blind addition: C4 HELD.
Falsifier (of the admission test itself): needs a FIRST JUDGED pilot or a full judged run; neither exists, so it is
printed NOT TRIGGERABLE at this stage; as an early warning the full-table strict D_c per stratum is compared with the
pilot's PASS-AT-POINT class (a stratum passing on the draw but under 0.95 on its 1,600 episodes is flagged).
Support rule (registration, enforcement clause): a stratum with fewer than 120 EVAL-side tasks is admitted for
description only (UNDETERMINED as a profile cell); the EVAL-side task count per stratum is printed and the class stated.

OUTPUT (write-once, refused if present): experiment_results/agent/bfcl_admission_pilot_draw.csv (--draw),
experiment_results/agent/bfcl_admission_pilot_labels_TEMPLATE.csv (--labels-template),
experiment_results/agent/bfcl_admission_pilot.txt and experiment_configs/reserved_pool_frozen_bfcl_<id>.json (--run).
The labels file experiment_results/agent/bfcl_admission_pilot_labels.csv is never written by this script.

HAZARD NOTES (bracket-ready, for the registrar; both found by the ingest dry-run of 2026-09-18 on the 6,400 episodes):
 [H1] The registered proxy bfcl_term_v1 ("any turn's step count >= 20 -> CAP_HIT") and the harness's own marker
      (handler_log "Model has been forced to quit after 20 steps.", written on the 21st executed step,
      bfcl_eval/model_handler/base_handler.py) disagree on 6 of 6,400 episodes: a turn the model ends by itself with a
      text reply after 19-20 executed calls has 20-21 responses and no marker; the literal rule reads CAP_HIT, the
      harness TERMINATED (DeepSeek-V3.2-Exp-FC miss_param_0, long_context_9; Qwen_Qwen3-32B-FC miss_param_0;
      meta-llama_Llama-3.3-70B-Instruct-FC base_97, miss_param_180, long_context_170). Suggested bracket on the proxy:
      "CAP_HIT = the harness's force-quit marker present, equivalently 21 responses in a turn"; bfcl_term_v1 stays the
      class of record here and the marker reading is printed beside every number.
 [H2] A cap hit on the LAST turn does not shorten the turn count, so BFCL's checker (eval_runner.py
      _evaluate_single_multi_turn_entry) evaluates it like any other entry: 13 of the 297 marker cap-hits carry a
      state / response verdict (11 instance_state_mismatch, 1 empty_turn_model_response, 1 execution_response_mismatch)
      instead of multi_turn:force_terminated, and such an entry CAN pass by the checker's code (0 did here). Under
      the strict reading they are CAP_HIT (not decidable) regardless of the verdict; the survey's "force-terminate =
      incorrect" is true only for cap hits before the last turn.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import sqlite3
import statistics
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
from collections import Counter, defaultdict
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import split_side  # noqa: E402  (norm-v1; imports nothing of record)

AGENT_DIR = os.path.join(ROOT, "experiment_results", "agent")
DB = os.path.join(AGENT_DIR, "bfcl_result_2025-12-16.db")
DRAW_CSV = os.path.join(AGENT_DIR, "bfcl_admission_pilot_draw.csv")
TEMPLATE_CSV = os.path.join(AGENT_DIR, "bfcl_admission_pilot_labels_TEMPLATE.csv")
LABELS_CSV = os.path.join(AGENT_DIR, "bfcl_admission_pilot_labels.csv")
OUT_TXT = os.path.join(AGENT_DIR, "bfcl_admission_pilot.txt")
RAW_DIR = os.path.join(AGENT_DIR, "bfcl_raw", "2025-12-16")
POOL_DIR = os.path.join(ROOT, "experiment_configs")

CATEGORIES = ("base", "miss_func", "miss_param", "long_context")
TERM_V1 = ("TERMINATED", "CAP_HIT", "ERROR")
MARKER = ("terminated", "step_cap", "error", "unknown")
DECIDED_TYPES = {"multi_turn:instance_state_mismatch", "multi_turn:execution_response_mismatch",
                 "multi_turn:empty_turn_model_response", "multi_turn:method_invoke_order_mismatch"}
HARNESS_TYPES = {"multi_turn:force_terminated", "multi_turn:inference_error"}
SEED = 42
N_PER_STRATUM = 75
N_LABELS = 50
DC_BAR = 0.95
REPRO_BAR = 0.98
SUPPORT_MIN_EVAL_TASKS = 120
TERMINATED_BAR = 0.60
P2_RANGE = (0.12, 0.19)


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return max(0.0, c - h), min(1.0, c + h)


def fmt_ci(k, n):
    lo, hi = wilson(k, n)
    return "%d/%d = %.4f [%.4f, %.4f]" % (k, n, k / n if n else float("nan"), lo, hi)


def refuse_if_exists(path):
    if os.path.exists(path):
        raise FileExistsError("%s exists; write-once (delete it by hand only if the record allows a redraw)" % path)


# --------------------------------------------------------------------------------------------------------------
# DB
# --------------------------------------------------------------------------------------------------------------
class Corpus:
    def __init__(self, db_path):
        self.db_path = db_path
        uri = "file:%s?mode=ro" % db_path.replace("\\", "/")
        conn = sqlite3.connect(uri, uri=True)
        try:
            self.meta = dict(conn.execute("SELECT key, value FROM meta").fetchall())
            self.agents = [r[0] for r in conn.execute("SELECT agent FROM agents ORDER BY agent")]
            self.tasks = {r[0]: {"category": r[1], "family_id": r[2], "content_key": r[3], "side": r[4]}
                          for r in conn.execute("SELECT task_id, category, family_id, content_key, side FROM tasks")}
            self.eps = {}
            for r in conn.execute("SELECT task_id, agent, passed, error_type, termination_class, bfcl_term_v1, checker_sha FROM episodes"):
                self.eps[(r[0], r[1])] = {"task_id": r[0], "agent": r[1], "passed": r[2], "error_type": r[3],
                                          "termination_class": r[4], "bfcl_term_v1": r[5], "checker_sha": r[6]}
            self.has_checker_view = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name='checker'").fetchone()[0] == 1
        finally:
            conn.close()

    def category(self, task_id):
        return self.tasks[task_id]["category"]

    def rows(self, category=None, agent=None):
        out = []
        for e in self.eps.values():
            if category and self.category(e["task_id"]) != category:
                continue
            if agent and e["agent"] != agent:
                continue
            out.append(e)
        return out


def checker_decided(e):
    if e["passed"] == 1:
        return True
    return e["error_type"] in DECIDED_TYPES


def decidable_v1(e):
    return e["bfcl_term_v1"] == "TERMINATED" and checker_decided(e)


def decidable_marker(e):
    return e["termination_class"] == "terminated" and checker_decided(e)


# --------------------------------------------------------------------------------------------------------------
# dry-run (counts only)
# --------------------------------------------------------------------------------------------------------------
def counts_block(rows):
    n = len(rows)
    p = sum(r["passed"] for r in rows)
    tv = Counter(r["bfcl_term_v1"] for r in rows)
    tm = Counter(r["termination_class"] for r in rows)
    return "%5d %5d %6.3f | %5d %5d %5d | %5d %5d %5d %5d" % (
        n, p, (p / n if n else float("nan")), tv["TERMINATED"], tv["CAP_HIT"], tv["ERROR"],
        tm["terminated"], tm["step_cap"], tm["error"], tm["unknown"])


def pairwise(rows, agents):
    """-> (decidable pairs, all pairs, decidable among both-decidable-episodes, both-decidable pairs)."""
    by_task = defaultdict(dict)
    for e in rows:
        by_task[e["task_id"]][e["agent"]] = e
    dec = tot = dec_t = tot_t = 0
    for d in by_task.values():
        for a, b in combinations(agents, 2):
            if a not in d or b not in d:
                continue
            tot += 1
            diff = d[a]["passed"] != d[b]["passed"]
            dec += diff
            if decidable_v1(d[a]) and decidable_v1(d[b]):
                tot_t += 1
                dec_t += diff
    return dec, tot, dec_t, tot_t


def dry_run_lines(c):
    L = []
    L.append("db=%s (mode=ro) agents=%d tasks=%d episodes=%d snapshot=%s archive_sha=%s" % (
        c.db_path, len(c.agents), len(c.tasks), len(c.eps), c.meta.get("snapshot"), c.meta.get("archive_sha")))
    L.append("agents: " + ", ".join(c.agents))
    L.append("termination classes: bfcl_term_v1 (registered; TERM/CAP/ERR) | ingest marker class (term/cap/err/unk)")
    L.append("%-40s %-13s %5s %5s %6s | %5s %5s %5s | %5s %5s %5s %5s" % (
        "agent", "stratum", "n", "pass", "rate", "TERM", "CAP", "ERR", "term", "cap", "err", "unk"))
    for a in c.agents:
        for cat in CATEGORIES:
            L.append("%-40s %-13s %s" % (a, cat, counts_block(c.rows(cat, a))))
        L.append("%-40s %-13s %s" % (a, "ALL(800)", counts_block(c.rows(agent=a))))
    for cat in CATEGORIES:
        L.append("%-40s %-13s %s" % ("ALL", cat, counts_block(c.rows(cat))))
    L.append("%-40s %-13s %s" % ("ALL", "ALL", counts_block(c.rows())))
    n_pairs = len(c.agents) * (len(c.agents) - 1) // 2
    L.append("pairwise decidable share (different pass verdict on the same task; DESCRIPTIVE, not the registered D_c); "
             "denominator = tasks x C(%d,2)=%d agent pairs; second reading: both episodes decidable (TERMINATED and checker-decided)" % (len(c.agents), n_pairs))
    L.append("%-13s %7s %7s %7s | %7s %7s %7s" % ("stratum", "decid", "pairs", "share", "decidT", "pairsT", "shareT"))
    for cat in CATEGORIES + ("ALL",):
        rows = c.rows() if cat == "ALL" else c.rows(cat)
        dec, tot, dec_t, tot_t = pairwise(rows, c.agents)
        L.append("%-13s %7d %7d %7.3f | %7d %7d %7.3f" % (cat, dec, tot, dec / tot if tot else float("nan"),
                                                          dec_t, tot_t, dec_t / tot_t if tot_t else float("nan")))
    return L


# --------------------------------------------------------------------------------------------------------------
# the draw and the labels template
# --------------------------------------------------------------------------------------------------------------
def make_draw(c, n_per_stratum=N_PER_STRATUM, seed=SEED):
    rng = random.Random(seed)
    draw = []
    for cat in CATEGORIES:
        task_ids = sorted(t for t, v in c.tasks.items() if v["category"] == cat)
        if len(task_ids) < n_per_stratum:
            raise ValueError("stratum %s has %d tasks, fewer than the %d to draw" % (cat, len(task_ids), n_per_stratum))
        chosen = rng.sample(task_ids, n_per_stratum)
        order = list(c.agents)
        rng.shuffle(order)
        for i, t in enumerate(chosen):
            a = order[i % len(order)]
            if (t, a) not in c.eps:
                raise KeyError("no episode for %s x %s" % (t, a))
            draw.append({"task_id": t, "agent": a, "category": cat, "family_id": c.tasks[t]["family_id"], "side": c.tasks[t]["side"]})
    return draw


def write_draw(draw, path):
    refuse_if_exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["task_id", "agent", "category", "family_id", "side"])
        w.writeheader()
        for r in draw:
            w.writerow(r)


def read_draw(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def label_sizes(n_labels, k=len(CATEGORIES)):
    base, rem = divmod(n_labels, k)
    return [base + (1 if i < rem else 0) for i in range(k)]


def make_label_subset(draw, n_labels=N_LABELS, seed=SEED):
    rng = random.Random(seed)
    sub = []
    for cat, n in zip(CATEGORIES, label_sizes(n_labels)):
        rows = [r for r in draw if r["category"] == cat]
        if len(rows) < n:
            raise ValueError("stratum %s has %d drawn episodes, fewer than the %d labels" % (cat, len(rows), n))
        sub.extend(rng.sample(rows, n))
    return sub


TEMPLATE_FIELDS = ["task_id", "agent", "category", "raw_result_file", "raw_score_file", "passed_manual", "termination_manual", "notes"]


def write_template(sub, path, raw_dir, snapshot):
    refuse_if_exists(path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TEMPLATE_FIELDS)
        w.writeheader()
        for r in sub:
            w.writerow({"task_id": r["task_id"], "agent": r["agent"], "category": r["category"],
                        "raw_result_file": "%s/result/%s/multi_turn/BFCL_v4_multi_turn_%s_result.json" % (raw_dir, r["agent"], r["category"]),
                        "raw_score_file": "%s/score/%s/multi_turn/BFCL_v4_multi_turn_%s_score.json" % (raw_dir, r["agent"], r["category"]),
                        "passed_manual": "", "termination_manual": "", "notes": ""})


def read_labels(path, template_path, n_labels):
    """The filled labels: refuses an empty cell, a value outside the alphabet, or a (task_id, agent) set != template."""
    if not os.path.exists(path):
        raise FileNotFoundError("%s missing: the labeller writes it from the TEMPLATE before --run (registration: labels first)" % path)
    if not os.path.exists(template_path):
        raise FileNotFoundError("%s missing: run --labels-template first" % template_path)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(template_path, newline="", encoding="utf-8") as f:
        tmpl = list(csv.DictReader(f))
    if len(rows) != n_labels:
        raise ValueError("labels: %d rows, expected %d" % (len(rows), n_labels))
    if {(r["task_id"], r["agent"]) for r in rows} != {(r["task_id"], r["agent"]) for r in tmpl}:
        raise ValueError("labels: the (task_id, agent) set differs from the template's")
    for r in rows:
        if r.get("passed_manual", "").strip() not in ("0", "1"):
            raise ValueError("labels: %s x %s passed_manual=%r (must be 0 or 1)" % (r["task_id"], r["agent"], r.get("passed_manual")))
        if r.get("termination_manual", "").strip() not in TERM_V1:
            raise ValueError("labels: %s x %s termination_manual=%r (must be one of %s)" % (r["task_id"], r["agent"], r.get("termination_manual"), "/".join(TERM_V1)))
    return rows


# --------------------------------------------------------------------------------------------------------------
# the artefact (C1 (d)), re-read from the raw result files for the drawn episodes
# --------------------------------------------------------------------------------------------------------------
def artefact_text(entry):
    """Decoded call sequence (handler_log model_response_decoded per step) + the final state_info text."""
    calls = []
    final_state = ""
    log = entry.get("inference_log")
    if not isinstance(log, list):
        return None
    for turn in log:
        if isinstance(turn, dict):
            for k in sorted((kk for kk in turn if kk.startswith("step_")), key=lambda s: int(s.split("_")[1])):
                for msg in turn[k]:
                    if isinstance(msg, dict) and msg.get("role") == "handler_log" and "model_response_decoded" in msg:
                        calls.append(json.dumps(msg["model_response_decoded"], ensure_ascii=False))
        elif isinstance(turn, list):
            final_state = json.dumps(turn, ensure_ascii=False, sort_keys=True)
    return "\n".join(calls) + "\n" + final_state


def artefact_lengths(draw, raw_dir):
    """-> dict (task_id, agent) -> chars or None (no artefact: error entry / missing row)."""
    need = defaultdict(set)
    for r in draw:
        need[(r["agent"], r["category"])].add(r["task_id"])
    out = {}
    for (agent, cat), ids in need.items():
        path = os.path.join(raw_dir, "result", agent, "multi_turn", "BFCL_v4_multi_turn_%s_result.json" % cat)
        found = set()
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                if e.get("id") in ids:
                    t = artefact_text(e)
                    out[(e["id"], agent)] = len(t) if t is not None else None
                    found.add(e["id"])
        for t in ids - found:
            out[(t, agent)] = None
    return out


# --------------------------------------------------------------------------------------------------------------
# --run
# --------------------------------------------------------------------------------------------------------------
def pool_export(c, pool_dir):
    """(a): EVAL-side ids as {"BFCL/<category>": [N...]}, id via pool_guard.compute_pool_id; write-once."""
    import pool_guard  # opens no DB at import; compute_pool_id is pure hashing (see docstring)
    ids_by_key = defaultdict(list)
    for t, v in sorted(c.tasks.items()):
        if v["side"] == "EVAL":
            ids_by_key["BFCL/%s" % v["category"]].append(int(t.rsplit("_", 1)[1]))
    ids_by_key = {k: sorted(v) for k, v in ids_by_key.items()}
    pid = pool_guard.compute_pool_id(ids_by_key)
    path = os.path.join(pool_dir, "reserved_pool_frozen_bfcl_%s.json" % pid)
    return pid, path, ids_by_key


def run(c, draw, labels, raw_dir, out_txt, pool_dir, artefact_cap_tokens=None, n_labels=N_LABELS):
    refuse_if_exists(out_txt)
    pid, pool_path, ids_by_key = pool_export(c, pool_dir)
    refuse_if_exists(pool_path)
    L = []
    P = L.append
    P("AGENT-CORPUS-ADMISSION pilot readout (registered 2026-09-18, programme L5855-L5982, commit 9cbd5ab); zero LLM calls")
    P("corpus=%s pool_id=%s" % (c.meta.get("corpus"), pid))
    P("db=%s snapshot=%s archive_sha=%s gorilla_sha=%s script=%s" % (c.db_path, c.meta.get("snapshot"), c.meta.get("archive_sha"), c.meta.get("gorilla_sha"), hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]))
    P("agents ingested (%d): %s" % (len(c.agents), ", ".join(c.agents)))
    P("agents excluded (missing files): %s" % c.meta.get("agents_excluded", "?"))
    P("draw: %d episodes = %d per stratum x %d strata, seed %d; labels: %d rows, file written before this readout" % (len(draw), len(draw) // len(CATEGORIES), len(CATEGORIES), SEED, len(labels)))
    P("")
    # ---------------- C1 ----------------
    P("== C1: parts (a)-(e) verified by command on the ingested tables ==")
    # (a)
    mism = 0
    fam_sides = defaultdict(set)
    for t, v in c.tasks.items():
        if split_side.tier_b(v["family_id"], v["content_key"]) != v["side"]:
            mism += 1
        fam_sides[v["family_id"]].add(v["side"])
    straddling = sum(1 for s in fam_sides.values() if len(s) > 1)
    eval_tasks = Counter(v["category"] for v in c.tasks.values() if v["side"] == "EVAL")
    a_ok = mism == 0 and straddling == 0
    P("(a) side recomputed per row (split_side.tier_b, %s): mismatches %d of %d; straddling families %d of %d; "
      "EVAL tasks per stratum %s; pool id %s over %d EVAL ids -> %s; registry NOT edited: %s" % (
          split_side.NORMALISER_VERSION, mism, len(c.tasks), straddling, len(fam_sides),
          ", ".join("%s %d" % (cat, eval_tasks[cat]) for cat in CATEGORIES), pid, sum(len(v) for v in ids_by_key.values()),
          pool_path, "VERIFIED" if a_ok else "FAILED"))
    # (b)
    lines = sorted("%s\t%s\t%s" % (e["task_id"], e["agent"], e["checker_sha"]) for e in c.eps.values())
    table_sha = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    b_ok = c.has_checker_view and "termination_rule" in c.meta and "term_v1_rule" in c.meta
    unknown_types = Counter(e["error_type"] for e in c.eps.values() if e["passed"] == 0 and e["error_type"] not in DECIDED_TYPES | HARNESS_TYPES)
    P("(b) checker view present %s; reading rules in meta (termination_rule, term_v1_rule) %s; checker table sha %s over %d rows; "
      "checker-decided error_types %s; harness outcomes %s; unknown error_types %s: %s" % (
          c.has_checker_view, "termination_rule" in c.meta and "term_v1_rule" in c.meta, table_sha, len(lines),
          sorted(DECIDED_TYPES), sorted(HARNESS_TYPES), dict(unknown_types) or "none", "VERIFIED" if b_ok and not unknown_types else "FAILED"))
    # (c)
    P("(c) bfcl_term_v1 per agent x stratum (denominator = the agent's 800; marker class beside):")
    P("    %-40s %-13s %5s %5s %6s | %5s %5s %5s | %5s %5s %5s %5s" % ("agent", "stratum", "n", "pass", "rate", "TERM", "CAP", "ERR", "term", "cap", "err", "unk"))
    c_ok = True
    for a in c.agents:
        for cat in CATEGORIES:
            P("    %-40s %-13s %s" % (a, cat, counts_block(c.rows(cat, a))))
        rows_a = c.rows(agent=a)
        c_ok = c_ok and len(rows_a) == 4 * 200
        P("    %-40s %-13s %s" % (a, "ALL", counts_block(rows_a)))
    P("    (c) every agent has 800 episodes: %s" % ("VERIFIED" if c_ok else "FAILED"))
    # (d)
    lens = artefact_lengths(draw, raw_dir)
    present = [v for v in lens.values() if v is not None]
    missing = [k for k, v in lens.items() if v is None]
    d_ok = len(present) == len(draw)
    if present:
        qs = statistics.quantiles(present, n=20) if len(present) >= 20 else sorted(present)
        P("(d) artefact (decoded call sequence + final state_info) re-read from the raw result files for %d of %d drawn episodes; "
          "%d without artefact (error / missing rows: %s); length chars min %d p5 %d median %d p95 %d max %d; "
          "ESTIMATED tokens (chars/4, no tokenizer) median %d p95 %d max %d; per-episode artefact cap: %s; "
          "fingerprint / provider / response id: UNSTAMPED (archive carries none): %s" % (
              len(present), len(draw), len(missing), ", ".join("%s x %s" % k for k in missing[:5]) or "none",
              min(present), qs[0] if len(present) >= 20 else present[0], statistics.median(present), qs[-1] if len(present) >= 20 else present[-1], max(present),
              statistics.median(present) // 4, (qs[-1] if len(present) >= 20 else present[-1]) // 4, max(present) // 4,
              ("%d tokens (author's declaration)" % artefact_cap_tokens) if artefact_cap_tokens else "NOT DECLARED (the author's number; the pilot prints the distribution only)",
              "VERIFIED (artefact present for every drawn episode)" if d_ok else "FAILED (artefact missing for %d drawn episodes)" % len(missing)))
        if artefact_cap_tokens:
            over = sum(1 for v in present if v // 4 > artefact_cap_tokens)
            P("    ARTEFACT_OVER_CAP (estimated tokens > %d): %d of %d drawn episodes (a class, never truncated; a match with one is not judged)" % (artefact_cap_tokens, over, len(present)))
    else:
        P("(d) no artefact could be read: FAILED")
    # (e)
    per_cat = Counter(v["category"] for v in c.tasks.values())
    e_ok = set(per_cat) == set(CATEGORIES) and all(per_cat[cat] == 200 for cat in CATEGORIES)
    P("(e) stratum = (BFCL, category): %s: %s" % (", ".join("%s %d tasks" % (cat, per_cat[cat]) for cat in CATEGORIES), "VERIFIED" if e_ok else "FAILED"))
    c1 = a_ok and b_ok and not unknown_types and c_ok and d_ok and e_ok
    P("C1: %s (a %s, b %s, c %s, d %s, e %s)" % ("HELD" if c1 else "FAILED", a_ok, b_ok and not unknown_types, c_ok, d_ok, e_ok))
    P("")
    # ---------------- C2 ----------------
    P("== C2: strict D_c on the draw (episode decidable = bfcl_term_v1 TERMINATED AND checker-decided; denominator = ALL drawn episodes of the stratum; Wilson 95%) ==")
    dc_point = {}
    cls = {}
    P("    %-13s %-40s | %-40s | %s" % ("stratum", "D_c of record (bfcl_term_v1)", "D_c marker reading (termination_class)", "class"))
    for cat in CATEGORIES + ("ALL",):
        rows = [c.eps[(r["task_id"], r["agent"])] for r in draw if cat == "ALL" or r["category"] == cat]
        k1 = sum(decidable_v1(e) for e in rows)
        k2 = sum(decidable_marker(e) for e in rows)
        dc_point[cat] = k1 / len(rows) if rows else float("nan")
        cls[cat] = "PASS-AT-POINT" if dc_point[cat] >= DC_BAR else "PREDICTIVE-ONLY"
        P("    %-13s %-40s | %-40s | %s" % (cat, fmt_ci(k1, len(rows)), fmt_ci(k2, len(rows)), cls[cat] if cat != "ALL" else "pooled"))
    P("C2: per stratum %s" % ", ".join("%s %s (%.4f)" % (cat, cls[cat], dc_point[cat]) for cat in CATEGORIES))
    P("")
    # ---------------- C3 ----------------
    P("== C3: cap-hit share and ERROR share per agent over the agent's DRAWN episodes (both proxies); terminated share beside ==")
    P("    %-40s %5s | %-22s %-22s %-22s | %-22s %-22s %-22s" % ("agent", "drawn", "CAP_HIT v1", "ERROR v1", "TERMINATED v1", "step_cap marker", "error marker", "terminated marker"))
    drawn_by_agent = defaultdict(list)
    for r in draw:
        drawn_by_agent[r["agent"]].append(c.eps[(r["task_id"], r["agent"])])
    def share(rows, pred):
        k = sum(pred(e) for e in rows)
        lo, hi = wilson(k, len(rows))
        return "%d/%d=%.3f[%.2f,%.2f]" % (k, len(rows), k / len(rows) if rows else float("nan"), lo, hi)
    for a in c.agents:
        rows = drawn_by_agent[a]
        P("    %-40s %5d | %-22s %-22s %-22s | %-22s %-22s %-22s" % (
            a, len(rows), share(rows, lambda e: e["bfcl_term_v1"] == "CAP_HIT"), share(rows, lambda e: e["bfcl_term_v1"] == "ERROR"),
            share(rows, lambda e: e["bfcl_term_v1"] == "TERMINATED"), share(rows, lambda e: e["termination_class"] == "step_cap"),
            share(rows, lambda e: e["termination_class"] == "error"), share(rows, lambda e: e["termination_class"] == "terminated")))
    P("    per stratum (drawn):")
    term_share_draw = {}
    for cat in CATEGORIES + ("ALL",):
        rows = [c.eps[(r["task_id"], r["agent"])] for r in draw if cat == "ALL" or r["category"] == cat]
        term_share_draw[cat] = sum(e["bfcl_term_v1"] == "TERMINATED" for e in rows) / len(rows)
        P("    %-40s %5d | %-22s %-22s %-22s | %-22s %-22s %-22s" % (
            cat, len(rows), share(rows, lambda e: e["bfcl_term_v1"] == "CAP_HIT"), share(rows, lambda e: e["bfcl_term_v1"] == "ERROR"),
            share(rows, lambda e: e["bfcl_term_v1"] == "TERMINATED"), share(rows, lambda e: e["termination_class"] == "step_cap"),
            share(rows, lambda e: e["termination_class"] == "error"), share(rows, lambda e: e["termination_class"] == "terminated")))
    P("C3: printed (a readout, no bar)")
    P("")
    # ---------------- C4 ----------------
    P("== C4: reproduction of the %d manual labels against the ingested columns (passed, bfcl_term_v1) ==" % len(labels))
    agree = 0
    disagreements = []
    for r in labels:
        e = c.eps[(r["task_id"], r["agent"])]
        ok = int(r["passed_manual"].strip()) == e["passed"] and r["termination_manual"].strip() == e["bfcl_term_v1"]
        agree += ok
        if not ok:
            disagreements.append("%s x %s: manual (%s, %s) vs ingested (%d, %s)" % (r["task_id"], r["agent"], r["passed_manual"].strip(), r["termination_manual"].strip(), e["passed"], e["bfcl_term_v1"]))
    repro = agree / len(labels)
    c4 = repro >= REPRO_BAR
    P("    reproduction %s; disagreements: %s" % (fmt_ci(agree, len(labels)), "; ".join(disagreements) or "none"))
    P("C4: %s (bar >= %.2f, i.e. %d of %d)" % ("HELD" if c4 else "FAILED", REPRO_BAR, math.ceil(REPRO_BAR * len(labels) - 1e-9), len(labels)))
    P("")
    # ---------------- descriptive full table ----------------
    P("== Descriptive (registrar's addition, not scored): full-table strict D_c and CAP_HIT share per stratum x agent over the agent's 800 ==")
    P("    %-40s " % "agent" + " ".join("%-24s" % cat for cat in CATEGORIES) + " %-24s" % "ALL")
    full_dc = {}
    full_cap_by_agent = {}
    for a in c.agents:
        cells = []
        for cat in CATEGORIES + ("ALL",):
            rows = c.rows(None if cat == "ALL" else cat, a)
            k = sum(decidable_v1(e) for e in rows)
            cap = sum(e["bfcl_term_v1"] == "CAP_HIT" for e in rows)
            cells.append("Dc %.3f cap %.3f (%d)" % (k / len(rows), cap / len(rows), len(rows)))
            if cat == "ALL":
                full_cap_by_agent[a] = cap / len(rows)
        P("    %-40s " % a + " ".join("%-24s" % x for x in cells))
    cells = []
    for cat in CATEGORIES + ("ALL",):
        rows = c.rows(None if cat == "ALL" else cat)
        k = sum(decidable_v1(e) for e in rows)
        full_dc[cat] = k / len(rows)
        cells.append("Dc %.4f term %.4f (%d)" % (full_dc[cat], sum(e["bfcl_term_v1"] == "TERMINATED" for e in rows) / len(rows), len(rows)))
    P("    %-40s " % "ALL agents" + " ".join("%-24s" % x for x in cells))
    pw = []
    for cat in CATEGORIES:
        dec, tot, dec_t, tot_t = pairwise(c.rows(cat), c.agents)
        pw.append("%s %d/%d=%.3f (both decidable %d/%d=%.3f)" % (cat, dec, tot, dec / tot if tot else float("nan"), dec_t, tot_t, dec_t / tot_t if tot_t else float("nan")))
    P("    pairwise decidable share on the full table (coordinator's pair reading, descriptive): " + "; ".join(pw))
    P("")
    # ---------------- predictions ----------------
    P("== Predictions (recorded blind in the registration; scored on the numbers above) ==")
    below = [cat for cat in CATEGORIES if dc_point[cat] < DC_BAR]
    lowest = min(CATEGORIES, key=lambda cat: dc_point[cat])
    p1 = len(below) >= 2 and lowest == "long_context"
    P("P1 strict D_c < 0.95 at the point in >= 2 of 4 strata AND long_context the lowest: below-bar strata %s (%d); lowest %s (%.4f): %s" % (below or "none", len(below), lowest, dc_point[lowest], "HELD" if p1 else "FAILED"))
    med = statistics.median(full_cap_by_agent.values())
    p2 = P2_RANGE[0] <= med <= P2_RANGE[1]
    P("P2 median agent's cap-hit share on its full 800 (bfcl_term_v1) in [%.2f, %.2f]: per agent %s; median %.4f: %s" % (
        P2_RANGE[0], P2_RANGE[1], ", ".join("%s %.4f" % (a, full_cap_by_agent[a]) for a in c.agents), med, "HELD" if p2 else "FAILED"))
    p3 = any(cls[cat] == "PREDICTIVE-ONLY" for cat in CATEGORIES)
    P("P3 at least one stratum PREDICTIVE-ONLY: %s: %s" % ([cat for cat in CATEGORIES if cls[cat] == "PREDICTIVE-ONLY"] or "none", "HELD" if p3 else "FAILED"))
    p4 = all(term_share_draw[cat] >= TERMINATED_BAR for cat in CATEGORIES)
    P("P4 terminated share >= %.2f in all 4 strata (draw, bfcl_term_v1): %s: %s" % (TERMINATED_BAR, ", ".join("%s %.4f" % (cat, term_share_draw[cat]) for cat in CATEGORIES), "HELD" if p4 else "FAILED"))
    P("Registrar's blind addition, C4 HELD: %s" % ("HELD" if c4 else "FAILED"))
    P("")
    # ---------------- falsifier, enforcement, support ----------------
    P("== Falsifier of the admission test (a first JUDGED pilot refused by the truncation guard, or a full judged run's strict D_c < 0.95 in a stratum that passed the pilot) ==")
    P("    NOT TRIGGERABLE at this stage: no judged pilot exists (nothing judged is scheduled by the registration).")
    warn = [cat for cat in CATEGORIES if cls[cat] == "PASS-AT-POINT" and full_dc[cat] < DC_BAR]
    P("    early warning on the archive itself (full-table strict D_c vs the pilot's class): %s" % (
        ("strata passing on the draw but under 0.95 on their 1,600 episodes: %s" % warn) if warn else "none (every PASS-AT-POINT stratum is also >= 0.95 on its full table, or none passed)"))
    P("== Enforcement clause ==")
    for cat in CATEGORIES:
        P("    %-13s %s: %s" % (cat, cls[cat], "may receive the item-19 probe and a first judged pilot (<= 4,000 matches), a separate launch" if cls[cat] == "PASS-AT-POINT"
                                else "REFUSED for judged cells; checker-built rows on terminated episodes only (terminated share draw %.4f, full %.4f)" % (term_share_draw[cat], sum(e["bfcl_term_v1"] == "TERMINATED" for e in c.rows(cat)) / len(c.rows(cat)))))
    P("== Support rule (fewer than %d EVAL-side tasks in a stratum -> admitted for description only, UNDETERMINED as a profile cell) ==" % SUPPORT_MIN_EVAL_TASKS)
    for cat in CATEGORIES:
        P("    %-13s EVAL-side tasks %d: %s" % (cat, eval_tasks[cat], "profile cell UNDETERMINED (description only)" if eval_tasks[cat] < SUPPORT_MIN_EVAL_TASKS else "supported"))
    P("")
    P("== Hazard notes (bracket-ready; see the docstring's [H1] [H2]) ==")
    dis = sum(1 for e in c.eps.values() if (e["termination_class"] == "step_cap") != (e["bfcl_term_v1"] == "CAP_HIT"))
    last_turn = sum(1 for e in c.eps.values() if e["termination_class"] == "step_cap" and e["error_type"] != "multi_turn:force_terminated")
    last_turn_pass = sum(1 for e in c.eps.values() if e["termination_class"] == "step_cap" and e["passed"] == 1)
    P("    [H1] bfcl_term_v1 (>= 20 responses) vs the harness force-quit marker: disagree on %d of %d episodes" % (dis, len(c.eps)))
    P("    [H2] marker cap-hits evaluated by the checker (cap on the last turn): %d of %d, of which passed %d" % (last_turn, sum(1 for e in c.eps.values() if e["termination_class"] == "step_cap"), last_turn_pass))
    P("")
    P("== Verdict of record ==")
    P("C1 %s; C2 %s; C3 printed; C4 %s; P1 %s; P2 %s; P3 %s; P4 %s; falsifier NOT TRIGGERABLE; support rule: %s" % (
        "HELD" if c1 else "FAILED", ", ".join("%s %s" % (cat, cls[cat]) for cat in CATEGORIES), "HELD" if c4 else "FAILED",
        "HELD" if p1 else "FAILED", "HELD" if p2 else "FAILED", "HELD" if p3 else "FAILED", "HELD" if p4 else "FAILED",
        "all 4 strata description-only" if all(eval_tasks[cat] < SUPPORT_MIN_EVAL_TASKS for cat in CATEGORIES) else "see above"))
    # ---------------- write-once ----------------
    os.makedirs(os.path.dirname(pool_path), exist_ok=True)
    with open(pool_path, "w", encoding="utf-8") as f:
        json.dump(ids_by_key, f, indent=1)
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return L, pid, pool_path


# --------------------------------------------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------------------------------------------
def selftest():
    sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
    import bfcl_ingest as bi
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw")
        bi._fixture(raw)
        tasks, episodes, agents, files, hazards = bi.ingest(raw, ["agentA", "agentB"], "selftest", verbose=False)
        db = os.path.join(td, "t.db")
        bi.build_db(db, tasks, episodes, agents, files, "selftest")
        c = Corpus(db)
        assert len(c.eps) == 24 and c.agents == ["agentA", "agentB"]
        assert abs(wilson(95, 100)[0] - 0.88825) < 0.0005 and abs(wilson(95, 100)[1] - 0.97846) < 0.0005  # z=1.96, same formula as t3_routing_inflation.wilson
        lines = dry_run_lines(c)
        assert any(l.startswith("agentA") for l in lines)
        # draw: 3 per stratum (the fixture has 3 tasks per category), distinct tasks, agents spread
        draw = make_draw(c, n_per_stratum=3)
        assert len(draw) == 12 and all(len({r["task_id"] for r in draw if r["category"] == cat}) == 3 for cat in CATEGORIES)
        assert Counter(r["agent"] for r in draw if r["category"] == "base") in (Counter({"agentA": 2, "agentB": 1}), Counter({"agentA": 1, "agentB": 2}))
        assert make_draw(c, n_per_stratum=3) == draw  # deterministic
        try:
            make_draw(c, n_per_stratum=4)
            raise AssertionError("draw larger than the stratum did not refuse")
        except ValueError:
            pass
        draw_csv = os.path.join(td, "draw.csv")
        write_draw(draw, draw_csv)
        assert read_draw(draw_csv) == draw
        try:
            write_draw(draw, draw_csv)
            raise AssertionError("draw write-once did not fire")
        except FileExistsError:
            pass
        # labels: 4 rows (1 per category)
        sub = make_label_subset(draw, n_labels=4)
        assert len(sub) == 4 and label_sizes(50) == [13, 13, 12, 12]
        tmpl = os.path.join(td, "labels_TEMPLATE.csv")
        write_template(sub, tmpl, raw, "selftest")
        with open(tmpl, newline="", encoding="utf-8") as f:
            trows = list(csv.DictReader(f))
        assert all(r["passed_manual"] == "" and r["termination_manual"] == "" for r in trows)
        labels_path = os.path.join(td, "labels.csv")
        try:
            read_labels(labels_path, tmpl, 4)
            raise AssertionError("missing labels did not refuse")
        except FileNotFoundError:
            pass
        # an empty cell refuses
        with open(labels_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=TEMPLATE_FIELDS)
            w.writeheader()
            for r in trows:
                w.writerow(r)
        try:
            read_labels(labels_path, tmpl, 4)
            raise AssertionError("empty labels did not refuse")
        except ValueError:
            pass
        # filled from the DB, one row deliberately wrong -> reproduction 3/4 = 0.75 -> C4 FAILED
        with open(labels_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=TEMPLATE_FIELDS)
            w.writeheader()
            for i, r in enumerate(trows):
                e = c.eps[(r["task_id"], r["agent"])]
                r = dict(r)
                r["passed_manual"] = str(1 - e["passed"] if i == 0 else e["passed"])
                r["termination_manual"] = e["bfcl_term_v1"]
                w.writerow(r)
        labels = read_labels(labels_path, tmpl, 4)
        out_txt = os.path.join(td, "pilot.txt")
        pool_dir = os.path.join(td, "cfg")
        L, pid, pool_path = run(c, draw, labels, raw, out_txt, pool_dir, artefact_cap_tokens=100, n_labels=4)
        txt = "\n".join(L)
        assert pid.startswith("p") and len(pid) == 17 and os.path.exists(pool_path) and os.path.exists(out_txt)
        assert "C4: FAILED" in txt and "reproduction 3/4" in txt, txt
        assert "(e) stratum = (BFCL, category): base 3 tasks" in txt
        assert "C1: FAILED" in txt  # the fixture has 3 tasks per stratum and 6 episodes per agent, not 200 / 800
        assert "ARTEFACT_OVER_CAP" in txt and "NOT TRIGGERABLE" in txt and "[H1]" in txt
        assert "P2 median agent's cap-hit share" in txt and "Support rule" in txt
        # D_c arithmetic on the draw: recompute by hand
        rows = [c.eps[(r["task_id"], r["agent"])] for r in draw]
        k = sum(e["bfcl_term_v1"] == "TERMINATED" and (e["passed"] == 1 or e["error_type"] in DECIDED_TYPES) for e in rows)
        assert ("ALL           %s" % fmt_ci(k, len(rows))) in txt, (k, len(rows))
        # the exported pool: EVAL families of the fixture, ids as integers under BFCL/<category>
        pool = json.load(open(pool_path, encoding="utf-8"))
        assert all(k2.startswith("BFCL/") for k2 in pool) and all(isinstance(x, int) for v in pool.values() for x in v)
        eval_n = sum(1 for v in c.tasks.values() if v["side"] == "EVAL")
        assert sum(len(v) for v in pool.values()) == eval_n
        import pool_guard
        assert pool_guard.compute_pool_id(pool) == pid
        # write-once guards on --run outputs
        try:
            run(c, draw, labels, raw, out_txt, pool_dir, n_labels=4)
            raise AssertionError("pilot txt write-once did not fire")
        except FileExistsError:
            pass
        os.remove(out_txt)
        try:
            run(c, draw, labels, raw, out_txt, pool_dir, n_labels=4)
            raise AssertionError("pool file write-once did not fire")
        except FileExistsError:
            pass
        assert not os.path.exists(out_txt)
    print("selftest OK: draw deterministic and refuses oversize; template empty; labels refused when missing / empty / wrong; "
          "C4 arithmetic (3/4 FAILED); pool id = pool_guard.compute_pool_id over the EVAL families; write-once guards fire on the draw, "
          "the pilot file and the pool file; no DB of record opened")


# --------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", default=DB)
    ap.add_argument("--raw-dir", default=RAW_DIR)
    ap.add_argument("--dry-run", action="store_true", help="counts only; nothing written")
    ap.add_argument("--draw", action="store_true", help="write the 300-episode draw (write-once)")
    ap.add_argument("--labels-template", action="store_true", help="write the 50-row labels TEMPLATE (write-once)")
    ap.add_argument("--run", action="store_true", help="the registered readout; refuses without 50 filled labels; write-once")
    ap.add_argument("--artefact-cap-tokens", type=int, default=None, help="the author's per-episode artefact cap (printed; ARTEFACT_OVER_CAP counted)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        print("corpus=bfcl_result_2025-12-16")
        print("pool_id=NONE")
        selftest()
        return 0
    if not (a.dry_run or a.draw or a.labels_template or a.run):
        ap.error("one of --dry-run / --draw / --labels-template / --run / --selftest")
    if not os.path.exists(a.db):
        print("corpus=bfcl_result_2025-12-16")
        print("pool_id=NONE")
        print("missing %s (build it with tools/ingest/bfcl_ingest.py --build)" % a.db)
        return 2
    c = Corpus(a.db)
    print("corpus=%s" % c.meta.get("corpus", "?"))
    print("pool_id=%s" % ("NONE" if not a.run else "computed at export (below)"))
    if a.dry_run:
        for line in dry_run_lines(c):
            print(line)
        print("dry-run: nothing written")
    if a.draw:
        draw = make_draw(c)
        write_draw(draw, DRAW_CSV)
        print("draw: %d episodes written once to %s (seed %d)" % (len(draw), DRAW_CSV, SEED))
        print("%-40s " % "agent" + " ".join("%-13s" % cat for cat in CATEGORIES) + " total")
        for ag in c.agents:
            cnt = Counter(r["category"] for r in draw if r["agent"] == ag)
            print("%-40s " % ag + " ".join("%-13d" % cnt[cat] for cat in CATEGORIES) + " %d" % sum(cnt.values()))
        print("distinct tasks per stratum: " + ", ".join("%s %d" % (cat, len({r["task_id"] for r in draw if r["category"] == cat})) for cat in CATEGORIES)
              + "; sides in the draw: " + ", ".join("%s %d" % kv for kv in sorted(Counter(r["side"] for r in draw).items())))
    if a.labels_template:
        if not os.path.exists(DRAW_CSV):
            raise FileNotFoundError("%s missing: run --draw first" % DRAW_CSV)
        draw = read_draw(DRAW_CSV)
        sub = make_label_subset(draw)
        write_template(sub, TEMPLATE_CSV, os.path.relpath(a.raw_dir, ROOT).replace("\\", "/"), c.meta.get("snapshot"))
        print("labels template: %d rows (%s per stratum) written once to %s; columns passed_manual / termination_manual / notes EMPTY; "
              "the labeller fills %s from the raw files BEFORE --run" % (len(sub), "/".join(str(x) for x in label_sizes(N_LABELS)), TEMPLATE_CSV, LABELS_CSV))
    if a.run:
        if not os.path.exists(DRAW_CSV):
            raise FileNotFoundError("%s missing: run --draw first" % DRAW_CSV)
        draw = read_draw(DRAW_CSV)
        if len(draw) != N_PER_STRATUM * len(CATEGORIES):
            raise ValueError("draw has %d rows, expected %d" % (len(draw), N_PER_STRATUM * len(CATEGORIES)))
        labels = read_labels(LABELS_CSV, TEMPLATE_CSV, N_LABELS)  # refuses before any number is printed
        L, pid, pool_path = run(c, draw, labels, a.raw_dir, OUT_TXT, POOL_DIR, artefact_cap_tokens=a.artefact_cap_tokens)
        for line in L:
            print(line)
        print("written once: %s ; %s (pool_id=%s; registry experiment_configs/reserved_pools.json NOT edited)" % (OUT_TXT, pool_path, pid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
