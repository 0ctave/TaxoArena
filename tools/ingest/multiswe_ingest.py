"""Multi-SWE-bench admission ingest, CHEAP VARIANT: the tooling for MULTI-SWE-ADMISSION (registered 2026-09-22,
docs/judge_v2_program.md L9801-L9918, commit b97da18; the second application of AGENT-CORPUS-ADMISSION's rule set
(a)-(e), L5857-L5985; plan Amendment 7; lead docs/agents/leads/2026-09-18_agent_corpora.md section 1.3).

  python tools/ingest/multiswe_ingest.py --selftest                 # synthetic mini-corpus in a temp dir; no network
  python tools/ingest/multiswe_ingest.py --fetch --dry-run          # list what WOULD be downloaded (the two file listings
                                                                    #   are read over the network; nothing is written)
  python tools/ingest/multiswe_ingest.py --fetch                    # resumable, sha-verified download into
                                                                    #   experiment_results/agent/multiswe_raw/<date>/
  python tools/ingest/multiswe_ingest.py --dry-run                  # parse the raw files, print every count and the
                                                                    #   exit-status enumeration; write NOTHING
  python tools/ingest/multiswe_ingest.py --ingest                   # write experiment_results/agent/multiswe_result_<date>.db
                                                                    #   ONCE (refuses a partial download, refuses to overwrite)
  python tools/ingest/multiswe_ingest.py --readout                  # write-once experiment_results/agent/multiswe_admission.txt
                                                                    #   + multiswe_admission_strata.csv + the EVAL pool file
The registration names the modes --download / --build; they are accepted as aliases of --fetch / --ingest.

ZERO LLM CALLS anywhere (no judge, no embedding, no labelling; nothing judged, ranked, routed or induced). Network only
under --fetch (and the two listing reads of --fetch --dry-run). NO pool_guard is needed and none is imported by the
ingest: no pool of record is read, no DB of record is opened (not mmlu_pro_dataset_cache_v2.db, not snapshots.db, not
embeddings_cache.db, not multicorpus_cache_v1.db, no verdict cache; nothing under experiment_results/** except the NEW
files this script writes). The pool id of the EVAL export is computed by a local mirror of pool_guard.compute_pool_id
(pure hashing; the selftest asserts the mirror equals pool_guard's function). The first printed line is
"corpus=multiswe_trajs_<revision[:12]>", the second the script's LF sha256 (the file is LF; the sha is computed over
LF-normalised bytes so a CRLF checkout prints the same value). The script may run beside anything, including a
construction (no pool reader).

CORPUS OF RECORD and what the listing showed on 2026-09-22 (read before this script was written; nothing downloaded
beyond three sample files for the format):
  (1) HF dataset ByteDance-Seed/Multi-SWE-bench_trajs (CC0-1.0), revision pinned at the first --fetch in
      <raw>/hf_pin.json. It holds ONE ZIP PER (language, submission): <language>/<YYYYMMDD>_<scaffold>_<model>.zip,
      319 zips over top-level dirs c, c++, go, java, javascript, python, rust, typescript (the eight of record) plus
      mini and flash (LISTED AND IGNORED, never fetched). A zip holds trajectories ONLY: MSWE-agent and MagentLess zips
      one "<instance_id>.traj" per instance (JSON: environment, trajectory[], history[], info{exit_status, submission,
      model_stats{api_calls,...}}); MopenHands zips one "<instance_id>/<model>-<ts>.json" per instance. NO report.json
      is in this dataset. The Python zips name the scaffolds SWE-agent / OpenHands / Agentless (no M prefix).
  (2) GitHub multi-swe-bench/experiments (Apache-2.0; the leaderboard submissions), commit pinned at the first --fetch in
      <raw>/github_pin.json (the default branch head at that moment; every later run reuses the pin). Layout
      evaluation/<language>/verified/<YYYYMMDD>_<scaffold>_<model>/{all_preds.jsonl, metadata.yaml,
      results/results.json[, logs/<org>/<repo>/evals/pr-<id>/{fix.patch, fix-patch-run.log, report.json}]} and
      evaluation/<language>/verified/index.json {"all_ids": [...]}. The per-instance report.json of the registration's
      layout exists ONLY for two 2026 submissions (CodeArts-Agent c and c++, 255 files at the listing; 465 more sit under
      evaluation/visual_evaluation, ignored); every 2025 submission
      (the ones with trajectories on HF) carries the checker's verdict ONLY as the id lists of results/results.json:
      resolved, unresolved_ids, empty_error_patch_ids, incomplete_ids, completed_ids, submitted_ids (+ the counts).
      evaluation/{mini, flash, visual_evaluation} are LISTED AND IGNORED. all_preds.jsonl (the model patches) is
      listed with its bytes and NOT fetched (no use in this variant).
  So the cheap variant fetches: from GitHub every results/results.json, metadata.yaml and index.json of the eight
  languages (all scaffolds, all models), every logs/**/report.json that exists (for the F2P/P2P cross-check), LICENSE
  and index.yaml (three python 2025-04-26 MopenHands dirs carry metadata.yaml only: listed as a hazard, no episodes);
  from HF the zips of the MSWE-agent CLASS only (scaffold key in SWE_AGENT_SCAFFOLDS = mswe-agent,
  swe-agent; identified by the zip name pattern <language>/<date>_(MSWE-agent|SWE-agent)_<model>.zip). MopenHands /
  MagentLess / OpenHands / Agentless trajectories are NOT fetched (deferred by the registration).

READING RULE OF RECORD (fixed here, before any count; the checker header in meta repeats it):
  checker mswe_check_v1: the corpus's own flag is membership in results/results.json: resolved iff instance_id in
  "resolved"; unresolved iff in "unresolved_ids"; checker-DECIDED iff resolved or unresolved (= completed_ids);
  empty_error_patch_ids and incomplete_ids are NOT decided (the checker ran no test: no valid patch / not completed);
  an id only in submitted_ids is 'listed_only' (not decided). Where a per-instance report.json exists, the
  registration's rule "resolved iff every FAIL_TO_PASS test passes AND every PASS_TO_PASS test passes" is computed as
  valid AND all f2p_tests[*].fix == PASS AND all p2p_tests[*].fix == PASS and compared with the flag; a mismatch is
  counted and printed and the corpus's flag (results.json) wins, as registered. The alternative reading "empty patch =
  decided fail" is printed beside D_c as DESCRIPTIVE, never scored.
  Instance id "<org>__<repo>-<pr>" (the last '-' splits the PR number); family_id = "<org>/<repo>"; language = the
  directory. The universe of a language = the union of the ids in every submission's results.json lists; index.json's
  all_ids is printed beside with the set differences (the C1 / P denominator is the union, as registered).

AGENT = (scaffold, model). scaffold_key = casefold(scaffold dir token); model_key = casefold(model token) after
MODEL_ALIASES (the trajectory upload and the leaderboard submission spell three models differently:
"Doubao-thinking-1.5" = "Doubao-1.5-thinking"; the others differ by case only). The batch date is provenance; the same
(language, scaffold, model) under two GitHub batch dates is FLAGGED and counted and kept as two agents "<key>@<date>",
never merged; an HF zip whose batch date differs from its GitHub submission's is FLAGGED and counted (the 2025-03-29
trajectory uploads of the three later models sit under 2025-04-26 on GitHub / 2025-05-14 on HF).

TERMINATION PROXY mswe_term_v1 (fixed here BEFORE any count, from the SWE-agent harness's exit-status vocabulary; the
--dry-run enumerates every status string found; a string outside the map is UNKNOWN, printed, NOT recovered toward C2;
the map is not re-drawn after the D_c count):
  TERMINATED  info.exit_status == "submitted" exactly, or an agent-chosen stop without a cap or error
              (TERMINATED_TOKENS: exit_forfeit, exit_command)
  CAP_HIT     the status names a cap (CAP_TOKENS: exit_cost, exit_context, max_steps, max_iterations, exit_max_steps,
              exit_total_execution_time, cost_limit, context_limit, step_limit, max_turns), INCLUDING the autosubmission
              forms "submitted (exit_cost)" / "autosubmission (max_steps)": the cap qualifier wins over "submitted".
              NON_TERMINATED, a class in every denominator (rule 10 / FRAMEWORK L236 guard 10).
  ERROR       the trajectory file is missing from the agent's zip, or the agent has no zip in the corpus of record, or the
              file does not parse, or the status names a harness / API / format error (ERROR_TOKENS: exit_error,
              exit_api, exit_format, exit_environment_error, early_exit, error)
  UNKNOWN     a present, parsed trajectory whose info.exit_status is absent or outside the map (printed; not recovered)
  UNSTAMPED   every episode of a scaffold outside the MSWE-agent class (no trajectory fetched in this variant)
  Precedence: exact "submitted" > CAP_TOKENS > ERROR_TOKENS > TERMINATED_TOKENS > UNKNOWN.
  steps = len(trajectory) (one entry per executed action); api_calls = info.model_stats.api_calls (provenance).
  The cap is DECLARED from any info key naming it (cap_metadata in meta); the trajectories seen carry none, so the
  readout prints UNSTAMPED with the reason and the empirical maxima beside (never a declared value).

SPLIT (rule (a); SPLIT-FUNCTION-IMPL tier (b), norm-v1, as split_side implements it): h = uint64(first 8 bytes of
sha256("norm-v1" || U+001F || family_id)) mod 1000 (the "||" of the registration is split_side.side_hash's
concatenation, with its U+001F separator); EVAL iff h < 300; GATE iff 300 <= h < 400; TRAIN otherwise; family_id = repo
("<org>/<repo>"), so a whole (language, repo) stratum sits on ONE side (straddling 0 by construction; asserted).
The DESCRIPTIVE instance-within-repo split of the registrar's addition uses h_instance = side_hash(stem_key(instance_id))
(the instance id as content key, ck-v1 options-free), printed beside, never scored, no pool file.

DB experiment_results/agent/multiswe_result_<date>.db (NEW; write-once): meta(key, value); tasks(instance_id PK,
language, org, repo, pr, family_id, content_key, side, h, h_instance, side_instance, in_index_json, n_submissions);
agents(agent PK, scaffold_key, model_key, scaffold_raw, model_raw, batch_dates, n_submissions, languages,
swe_agent_class, archives_present, flagged_multi_batch, flagged_date_mismatch); submissions(language, dir_name,
batch_date, scaffold_raw, model_raw, agent, results_sha256, total_instances, submitted_instances, completed_instances,
resolved_instances, unresolved_instances, empty_error_patch_instances, incomplete_instances, n_report_json, zip_path,
zip_batch_date, zip_sha256, zip_members, metadata_name, verified); episodes(instance_id, agent, language,
submission_dir, checker_status, resolved, checker_decided, report_json_present, report_valid, f2p_pass, f2p_total,
p2p_pass, p2p_total, report_rule_resolved, resolved_mismatch, trajectory_present, exit_status, mswe_term_v1, steps,
api_calls, artefact_bytes, artefact_chars, artefact_sha256, PK (instance_id, agent)); provenance(path, source, url,
bytes, sha256, upstream_sha, revision); views instances (= tasks) and checker(instance_id, agent, output, f2p_vector,
p2p_vector, checker_sha).

OUTCOME (--readout, from a complete ingest only; write-once): experiment_results/agent/multiswe_admission.txt and
multiswe_admission_strata.csv; the EVAL ids as experiment_configs/reserved_pool_frozen_multiswe_<pool id>.json
({"MULTISWE/<language>/<org>__<repo>": [pr, ...]}; declared in no config, no registry, read by no tree). C1 stratum
support (HELD iff >= 1 stratum with >= 120 EVAL instances), C2 cap recovery on the MSWE-agent class (HELD iff
recovered >= 0.95 of every class episode with a checker row; recovered = TERMINATED + CAP_HIT + ERROR, the registered
literal rule; the number conditional on an archive being present is printed beside, descriptive), C3 roster
completeness (HELD iff every C1 stratum has a complete roster >= 3), strict D_c per stratum and pooled with Wilson 95%
(printed, not scored), P reproduction of the eight counts (HELD iff exact), predictions P1 / P1' / P2 / P3 / P4 / P5
scored HELD / FAILED, the falsifier line.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analysis"))
import split_side  # noqa: E402  the side function (tools/analysis/split_side.py); imports nothing of record

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATE = "2026-09-22"
HF_REPO = "ByteDance-Seed/Multi-SWE-bench_trajs"
HF_LICENCE = "CC0-1.0 (dataset card)"
GH_OWNER_REPO = "multi-swe-bench/experiments"
GH_BRANCH = "main"
GH_LICENCE = "Apache-2.0 (LICENSE in the repository)"
LANGUAGES = ("c", "c++", "go", "java", "javascript", "python", "rust", "typescript")
PAPER_COUNTS = {"python": 460, "java": 128, "typescript": 224, "javascript": 356, "go": 428, "rust": 239, "c": 128, "c++": 129}
PAPER_TOTAL, PAPER_PYTHON, PAPER_NON_PYTHON = 2092, 460, 1632
SUPPORT_MIN = 120          # FRAMEWORK L117: fewer than 120 EVAL-side tasks = description only
ROSTER_MIN = 3             # the rule set's minimum complete roster (L5914)
CAP_RECOVERY_MIN = 0.95    # C2
SWE_AGENT_SCAFFOLDS = ("mswe-agent", "swe-agent")
MODEL_ALIASES = {"doubao-thinking-1.5": "doubao-1.5-thinking"}
NORMALISER = "norm-v1"
CHECKER_VERSION = "mswe_check_v1"
TERM_VERSION = "mswe_term_v1"
TERMINATED, CAP_HIT, ERROR, UNKNOWN, UNSTAMPED = "TERMINATED", "CAP_HIT", "ERROR", "UNKNOWN", "UNSTAMPED"
CAP_TOKENS = ("exit_cost", "exit_context", "max_steps", "max_iterations", "exit_max_steps", "exit_total_execution_time",
              "cost_limit", "context_limit", "step_limit", "max_turns")
ERROR_TOKENS = ("exit_error", "exit_api", "exit_format", "exit_environment_error", "early_exit", "error")
TERMINATED_TOKENS = ("exit_forfeit", "exit_command")
CAP_META_KEYS = ("max_steps", "max_iterations", "cost_limit", "per_instance_cost_limit", "total_cost_limit", "step_limit",
                 "max_turns", "context_limit")
MISSING_TRAJ, MISSING_ARCHIVE, ABSENT_STATUS, UNPARSED_TRAJ = "<trajectory missing>", "<no archive for agent>", "<exit_status absent>", "<trajectory unparsed>"
CHECKER_STATUSES = ("resolved", "unresolved", "empty_error_patch", "incomplete", "listed_only")
_SUB_RE = re.compile(r"^(\d{8})_([^_]+)(?:_(.+))?$")
_ID_RE = re.compile(r"^(.+?)__(.+)-(\d+)$")
_GH_REPORT_RE = re.compile(r"^evaluation/([^/]+)/verified/([^/]+)/logs/(.+)/evals/pr-(\d+)/report\.json$")
_GH_SUB_FILE_RE = re.compile(r"^evaluation/([^/]+)/verified/([^/]+)/(results/results\.json|metadata\.yaml|all_preds\.jsonl)$")
_GH_INDEX_RE = re.compile(r"^evaluation/([^/]+)/verified/index\.json$")
_HF_ZIP_RE = re.compile(r"^([^/]+)/([^/]+)\.zip$")
USER_AGENT = "taxoarena-multiswe-ingest/1"


def corpus_name(revision):
    return "multiswe_trajs_%s" % (revision or "UNPINNED")[:12]


def default_raw_dir(date):
    return os.path.join(ROOT, "experiment_results", "agent", "multiswe_raw", date)


def default_db(date):
    return os.path.join(ROOT, "experiment_results", "agent", "multiswe_result_%s.db" % date)


def default_outcome():
    return os.path.join(ROOT, "experiment_results", "agent", "multiswe_admission.txt")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(b):
    """GitHub's tree sha of a blob: sha1('blob <len>\\0' + content)."""
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(b))
    h.update(b)
    return h.hexdigest()


def script_sha():
    with open(os.path.abspath(__file__), "rb") as f:
        return sha256_bytes(f.read().replace(b"\r\n", b"\n"))


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def refuse_if_exists(path):
    if os.path.exists(path):
        raise FileExistsError("%s exists; write-once (delete it by hand if a rebuild is intended)" % path)


def compute_pool_id(ids_by_key):
    """Local mirror of pool_guard.compute_pool_id / ReservedPool.computePoolId for a key with no known source:
    'p' + sha256(sorted '<key>:<id>' lines joined by LF)[:16]. The selftest asserts equality with pool_guard's."""
    canon = "\n".join(sorted("%s:%d" % (k, q) for k, ids in ids_by_key.items() for q in ids))
    return "p" + sha256_bytes(canon.encode("utf-8"))[:16]


# --------------------------------------------------------------------------------------------------------------
# names, keys, the proxy
# --------------------------------------------------------------------------------------------------------------
def parse_submission_dir(name):
    """'20250329_MSWE-agent_Claude-3.7-Sonnet' -> (batch_date, scaffold_raw, model_raw, parsed). An unparsable
    name keeps the whole name as scaffold_raw with model_raw '' and parsed False (flagged, still ingested)."""
    m = _SUB_RE.match(name)
    if not m:
        return ("", name, "", False)
    return (m.group(1), m.group(2), m.group(3) or "", True)


def agent_key(scaffold_raw, model_raw):
    mk = model_raw.casefold()
    return "%s|%s" % (scaffold_raw.casefold(), MODEL_ALIASES.get(mk, mk))


def is_swe_agent_class(scaffold_raw):
    return scaffold_raw.casefold() in SWE_AGENT_SCAFFOLDS


def parse_instance_id(iid):
    m = _ID_RE.match(iid)
    if not m:
        raise ValueError("unrecognised instance id %r" % iid)
    return m.group(1), m.group(2), int(m.group(3))


def mswe_term_v1(exit_status, trajectory_present, archive_present=True, parsed=True):
    if not archive_present or not trajectory_present or not parsed:
        return ERROR
    if not isinstance(exit_status, str):
        return UNKNOWN
    s = exit_status.strip().casefold()
    if s == "submitted":
        return TERMINATED
    if any(t in s for t in CAP_TOKENS):
        return CAP_HIT
    if any(t in s for t in ERROR_TOKENS):
        return ERROR
    if any(t in s for t in TERMINATED_TOKENS):
        return TERMINATED
    return UNKNOWN


def status_class(s):
    """The class of an enumeration entry (a status string or one of the script's <markers>), for printing."""
    if s in (MISSING_ARCHIVE, MISSING_TRAJ, UNPARSED_TRAJ):
        return ERROR
    if s == ABSENT_STATUS or s is None:
        return UNKNOWN
    return mswe_term_v1(s, True)


# --------------------------------------------------------------------------------------------------------------
# listings and the fetch plan
# --------------------------------------------------------------------------------------------------------------
def http_get(url, timeout=180, accept=None):
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def github_head_sha():
    d = json.loads(http_get("https://api.github.com/repos/%s/branches/%s" % (GH_OWNER_REPO, GH_BRANCH), accept="application/vnd.github+json"))
    return d["commit"]["sha"]


def github_tree(sha):
    """The recursive tree at a commit: [{path, type, size, sha}]. Refuses a truncated listing."""
    d = json.loads(http_get("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (GH_OWNER_REPO, sha), accept="application/vnd.github+json"))
    if d.get("truncated"):
        raise RuntimeError("GitHub tree listing truncated for %s; the plan cannot be complete" % sha)
    return [{"path": t["path"], "type": t["type"], "size": t.get("size"), "sha": t["sha"]} for t in d["tree"] if t["type"] == "blob"]


def hf_listing():
    """(revision, [{path, size, sha256}]) from the dataset's file metadata (one API call)."""
    from huggingface_hub import HfApi
    info = HfApi().dataset_info(HF_REPO, files_metadata=True)
    rows = [{"path": s.rfilename, "size": s.size, "sha256": (s.lfs.sha256 if s.lfs else None)} for s in info.siblings]
    return info.sha, rows


def github_raw_url(sha, path):
    return "https://raw.githubusercontent.com/%s/%s/%s" % (GH_OWNER_REPO, sha, urllib.parse.quote(path, safe="/"))


def hf_url(revision, path):
    return "https://huggingface.co/datasets/%s/resolve/%s/%s" % (HF_REPO, revision, urllib.parse.quote(path, safe="/"))


def plan(gh_blobs, hf_rows):
    """The fetch plan from the two listings. -> dict with gh_files [{path,size,sha,kind}], hf_files [{path,size,sha256}],
    the ignored / not-fetched lists and the counts. Pure (no network)."""
    gh_files, gh_ignored_dirs, all_preds = [], Counter(), []
    report_by_sub = Counter()
    for b in gh_blobs:
        p = b["path"]
        if p in ("LICENSE", "index.yaml"):
            gh_files.append(dict(b, kind=p.lower()))
            continue
        if not p.startswith("evaluation/"):
            continue
        top = p.split("/")[1]
        if top not in LANGUAGES:
            gh_ignored_dirs[top] += 1
            continue
        if _GH_INDEX_RE.match(p):
            gh_files.append(dict(b, kind="index"))
        elif _GH_SUB_FILE_RE.match(p):
            m = _GH_SUB_FILE_RE.match(p)
            if m.group(3) == "all_preds.jsonl":
                all_preds.append(b)
            else:
                gh_files.append(dict(b, kind="results" if m.group(3).endswith("results.json") else "metadata"))
        elif _GH_REPORT_RE.match(p):
            m = _GH_REPORT_RE.match(p)
            gh_files.append(dict(b, kind="report"))
            report_by_sub[(m.group(1), m.group(2))] += 1
    hf_files, hf_ignored_dirs, hf_not_fetched = [], Counter(), []
    for r in hf_rows:
        m = _HF_ZIP_RE.match(r["path"])
        if not m:
            continue
        lang, sub = m.group(1), m.group(2)
        if lang not in LANGUAGES:
            hf_ignored_dirs[lang] += 1
            continue
        date, scaffold, model, parsed = parse_submission_dir(sub)
        if parsed and is_swe_agent_class(scaffold):
            hf_files.append(dict(r, language=lang, submission=sub))
        else:
            hf_not_fetched.append(dict(r, language=lang, submission=sub, scaffold=scaffold))
    return {"gh_files": gh_files, "gh_ignored_dirs": gh_ignored_dirs, "all_preds": all_preds, "report_by_sub": report_by_sub,
            "hf_files": hf_files, "hf_ignored_dirs": hf_ignored_dirs, "hf_not_fetched": hf_not_fetched}


def describe_plan(p, gh_sha, hf_rev):
    L = []
    kinds = Counter(f["kind"] for f in p["gh_files"])
    gh_bytes = sum(f["size"] or 0 for f in p["gh_files"])
    L.append("GitHub %s @ %s (%s): %d files to fetch, %d bytes (%.2f MB): %s" % (
        GH_OWNER_REPO, gh_sha, GH_LICENCE, len(p["gh_files"]), gh_bytes, gh_bytes / 1e6,
        ", ".join("%s=%d" % kv for kv in sorted(kinds.items()))))
    rep = p["report_by_sub"]
    rep_bytes = sum(f["size"] or 0 for f in p["gh_files"] if f["kind"] == "report")
    L.append("  report.json: %d files, %d bytes, under %d submission dirs: %s" % (
        kinds.get("report", 0), rep_bytes, len(rep), "; ".join("%s/%s=%d" % (k[0], k[1], v) for k, v in sorted(rep.items()))))
    ap_bytes = sum(f["size"] or 0 for f in p["all_preds"])
    L.append("  NOT fetched: all_preds.jsonl x %d (%d bytes, %.1f MB; the model patches, no use in this variant)" % (len(p["all_preds"]), ap_bytes, ap_bytes / 1e6))
    L.append("  IGNORED evaluation/ subtrees (blobs): %s" % (", ".join("%s=%d" % kv for kv in sorted(p["gh_ignored_dirs"].items())) or "none"))
    hf_bytes = sum(f["size"] or 0 for f in p["hf_files"])
    L.append("HF %s @ %s (%s): pattern <language>/<date>_(MSWE-agent|SWE-agent)_<model>.zip over %s" % (
        HF_REPO, hf_rev, HF_LICENCE, ",".join(LANGUAGES)))
    L.append("  MSWE-agent-class zips to fetch: %d files, %d bytes (%.1f MB)" % (len(p["hf_files"]), hf_bytes, hf_bytes / 1e6))
    per_lang = defaultdict(lambda: [0, 0])
    for f in p["hf_files"]:
        per_lang[f["language"]][0] += 1
        per_lang[f["language"]][1] += f["size"] or 0
    for lang in LANGUAGES:
        n, b = per_lang.get(lang, (0, 0))
        L.append("    %-11s %2d zips %12d bytes" % (lang, n, b))
    nf = Counter(f["scaffold"] for f in p["hf_not_fetched"])
    nf_bytes = sum(f["size"] or 0 for f in p["hf_not_fetched"])
    L.append("  NOT fetched (other scaffolds, deferred): %d zips, %d bytes (%.1f MB): %s" % (
        len(p["hf_not_fetched"]), nf_bytes, nf_bytes / 1e6, ", ".join("%s=%d" % kv for kv in sorted(nf.items()))))
    L.append("  IGNORED top-level dirs (zips): %s" % (", ".join("%s=%d" % kv for kv in sorted(p["hf_ignored_dirs"].items())) or "none"))
    L.append("TOTAL to fetch: %d files, %d bytes (%.1f MB); trajectories of MopenHands / MagentLess / OpenHands / Agentless: 0 bytes" % (
        len(p["gh_files"]) + len(p["hf_files"]), gh_bytes + hf_bytes, (gh_bytes + hf_bytes) / 1e6))
    return "\n".join(L)


# --------------------------------------------------------------------------------------------------------------
# fetch (resumable, idempotent, sha-verified)
# --------------------------------------------------------------------------------------------------------------
def pin_paths(raw_dir):
    return (os.path.join(raw_dir, "github_pin.json"), os.path.join(raw_dir, "github_tree.json"),
            os.path.join(raw_dir, "hf_pin.json"), os.path.join(raw_dir, "hf_listing.json"))


def load_pins(raw_dir):
    gp, gt, hp, hl = pin_paths(raw_dir)
    for p in (gp, gt, hp, hl):
        if not os.path.exists(p):
            raise FileNotFoundError("%s missing: run --fetch first" % p)
    with open(gp, encoding="utf-8") as f:
        gh_pin = json.load(f)
    with open(gt, encoding="utf-8") as f:
        gh_blobs = json.load(f)
    with open(hp, encoding="utf-8") as f:
        hf_pin = json.load(f)
    with open(hl, encoding="utf-8") as f:
        hf_rows = json.load(f)
    return gh_pin, gh_blobs, hf_pin, hf_rows


def write_json(path, obj):
    with open(path + ".part", "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=0, sort_keys=True)
        f.write("\n")
    os.replace(path + ".part", path)


def resolve_pins(raw_dir, write):
    """The two listings; pinned at the first --fetch (write=True), re-read from the pin afterwards."""
    gp, gt, hp, hl = pin_paths(raw_dir)
    if os.path.exists(gp) and os.path.exists(gt) and os.path.exists(hp) and os.path.exists(hl):
        gh_pin, gh_blobs, hf_pin, hf_rows = load_pins(raw_dir)
        return gh_pin["sha"], gh_blobs, hf_pin["revision"], hf_rows, True
    gh_sha = github_head_sha()
    gh_blobs = github_tree(gh_sha)
    hf_rev, hf_rows = hf_listing()
    if write:
        os.makedirs(raw_dir, exist_ok=True)
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        write_json(gp, {"owner_repo": GH_OWNER_REPO, "branch": GH_BRANCH, "sha": gh_sha, "resolved_at": now, "licence": GH_LICENCE})
        write_json(gt, gh_blobs)
        write_json(hp, {"repo_id": HF_REPO, "revision": hf_rev, "resolved_at": now, "licence": HF_LICENCE})
        write_json(hl, hf_rows)
    return gh_sha, gh_blobs, hf_rev, hf_rows, False


def fetch_github_file(url, dest, blob_sha, retries=4):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    last = None
    for attempt in range(retries):
        try:
            b = http_get(url)
            if git_blob_sha1(b) != blob_sha:
                raise RuntimeError("blob sha mismatch for %s (%s != %s)" % (url, git_blob_sha1(b), blob_sha))
            with open(dest + ".part", "wb") as f:
                f.write(b)
            os.replace(dest + ".part", dest)
            return b
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("download failed after %d attempts: %s (%s)" % (retries, url, last))


def local_gh_path(raw_dir, path):
    return os.path.join(raw_dir, "github", *path.split("/"))


def local_hf_path(raw_dir, path):
    return os.path.join(raw_dir, "hf", *path.split("/"))


def verify_gh_file(raw_dir, f):
    dest = local_gh_path(raw_dir, f["path"])
    if not os.path.exists(dest):
        return None
    with open(dest, "rb") as fh:
        b = fh.read()
    return b if git_blob_sha1(b) == f["sha"] else None


def verify_hf_file(raw_dir, f):
    dest = local_hf_path(raw_dir, f["path"])
    if not os.path.exists(dest) or os.path.getsize(dest) != f["size"]:
        return None
    return dest if sha256_file(dest) == f["sha256"] else None


def fetch(raw_dir):
    gh_sha, gh_blobs, hf_rev, hf_rows, pinned = resolve_pins(raw_dir, write=True)
    p = plan(gh_blobs, hf_rows)
    print(describe_plan(p, gh_sha, hf_rev))
    print("pins %s" % ("reused" if pinned else "written"))
    rows, fetched, skipped = [], 0, 0
    for i, f in enumerate(p["gh_files"], 1):
        b = verify_gh_file(raw_dir, f)
        if b is None:
            url = github_raw_url(gh_sha, f["path"])
            if fetched % 50 == 0:
                print("  GET github file %d of %d: %s" % (i, len(p["gh_files"]), url), flush=True)
            b = fetch_github_file(url, local_gh_path(raw_dir, f["path"]), f["sha"])
            fetched += 1
        else:
            skipped += 1
        rows.append(("github/" + f["path"], "github", len(b), sha256_bytes(b), f["sha"], github_raw_url(gh_sha, f["path"])))
    from huggingface_hub import hf_hub_download
    for f in p["hf_files"]:
        dest = verify_hf_file(raw_dir, f)
        if dest is None:
            print("  GET %s (%d bytes)" % (hf_url(hf_rev, f["path"]), f["size"]), flush=True)
            got = hf_hub_download(repo_id=HF_REPO, filename=f["path"], repo_type="dataset", revision=hf_rev,
                                  local_dir=os.path.join(raw_dir, "hf"))
            if os.path.abspath(got) != os.path.abspath(local_hf_path(raw_dir, f["path"])):
                raise RuntimeError("hf_hub_download placed %s at %s" % (f["path"], got))
            dest = verify_hf_file(raw_dir, f)
            if dest is None:
                raise RuntimeError("sha256 mismatch after download: %s (expected %s)" % (f["path"], f["sha256"]))
            fetched += 1
        else:
            skipped += 1
        rows.append(("hf/" + f["path"], "hf", f["size"], f["sha256"], f["sha256"], hf_url(hf_rev, f["path"])))
    manifest = os.path.join(raw_dir, "MANIFEST.txt")
    with open(manifest, "w", encoding="utf-8", newline="\n") as m:
        m.write("# Multi-SWE-bench cheap-variant raw files, %s\n" % DATE)
        m.write("# github %s @ %s (%s); hf %s @ %s (%s)\n" % (GH_OWNER_REPO, gh_sha, GH_LICENCE, HF_REPO, hf_rev, HF_LICENCE))
        m.write("# fetched_at: %s ; script_sha: %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), script_sha()))
        m.write("# columns: path<TAB>source<TAB>bytes<TAB>sha256<TAB>upstream_sha<TAB>url\n")
        for r in rows:
            m.write("\t".join(str(x) for x in r) + "\n")
    total = sum(r[2] for r in rows)
    print("fetch: %d files (%d fetched, %d already present and verified), %.1f MB, manifest %s" % (len(rows), fetched, skipped, total / 1e6, manifest))
    return rows


# --------------------------------------------------------------------------------------------------------------
# ingest (parse; the DB is written only under --ingest)
# --------------------------------------------------------------------------------------------------------------
class Corpus:
    def __init__(self):
        self.tasks = {}          # instance_id -> row
        self.agents = {}         # agent -> row
        self.submissions = []    # rows
        self.episodes = {}       # (instance_id, agent) -> row
        self.files = []          # provenance rows
        self.hazards = []
        self.index_ids = {}      # language -> set
        self.status_enum = Counter()
        self.cap_metadata = Counter()
        self.gh_sha = self.hf_rev = None
        self.complete = False


def _read_json_bytes(b, where):
    try:
        return json.loads(b.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        raise ValueError("%s: %s" % (where, e))


def report_rule(rep):
    """(valid, f2p_pass, f2p_total, p2p_pass, p2p_total, resolved_by_rule, f2p_vector, p2p_vector)."""
    valid = bool(rep.get("valid", False))
    f2p = rep.get("f2p_tests") or {}
    p2p = rep.get("p2p_tests") or {}
    fv = sorted((k, (v or {}).get("fix")) for k, v in f2p.items())
    pv = sorted((k, (v or {}).get("fix")) for k, v in p2p.items())
    f2p_pass = sum(1 for _, s in fv if s == "PASS")
    p2p_pass = sum(1 for _, s in pv if s == "PASS")
    resolved = valid and f2p_pass == len(fv) and p2p_pass == len(pv)
    return valid, f2p_pass, len(fv), p2p_pass, len(pv), resolved, fv, pv


def ingest(raw_dir, verbose=True):
    """Parse the raw dir into a Corpus. Refuses a partial download (every planned file present and sha-verified)."""
    c = Corpus()
    gh_pin, gh_blobs, hf_pin, hf_rows = load_pins(raw_dir)
    c.gh_sha, c.hf_rev = gh_pin["sha"], hf_pin["revision"]
    p = plan(gh_blobs, hf_rows)
    missing = []
    gh_bytes = {}
    for f in p["gh_files"]:
        b = verify_gh_file(raw_dir, f)
        if b is None:
            missing.append(f["path"])
        else:
            gh_bytes[f["path"]] = b
            c.files.append(("github/" + f["path"], "github", len(b), sha256_bytes(b), f["sha"], c.gh_sha))
    zips = {}
    for f in p["hf_files"]:
        dest = verify_hf_file(raw_dir, f)
        if dest is None:
            missing.append(f["path"])
        else:
            zips[(f["language"], f["submission"])] = (dest, f)
            c.files.append(("hf/" + f["path"], "hf", f["size"], f["sha256"], f["sha256"], c.hf_rev))
    if missing:
        raise SystemExit("[MULTISWE-INGEST] partial download: %d planned files missing or sha-mismatched (first 20): %s"
                         % (len(missing), "; ".join(missing[:20])))
    # index.json per language
    for f in p["gh_files"]:
        if f["kind"] == "index":
            lang = _GH_INDEX_RE.match(f["path"]).group(1)
            d = _read_json_bytes(gh_bytes[f["path"]], f["path"])
            c.index_ids[lang] = set(d.get("all_ids") or [])
    for lang in LANGUAGES:
        if lang not in c.index_ids:
            c.hazards.append("no index.json for language %s" % lang)
    # report.json per (language, submission, instance)
    reports = {}
    for f in p["gh_files"]:
        if f["kind"] == "report":
            m = _GH_REPORT_RE.match(f["path"])
            lang, sub, orgrepo, pr = m.group(1), m.group(2), m.group(3), int(m.group(4))
            rep = _read_json_bytes(gh_bytes[f["path"]], f["path"])
            iid = "%s__%s-%d" % (rep.get("org", orgrepo.split("/")[0]), rep.get("repo", orgrepo.split("/", 1)[-1]), rep.get("number", pr))
            reports[(lang, sub, iid)] = rep
    # submissions
    subs_by_lang_agent = defaultdict(list)
    sub_specs = []
    for f in p["gh_files"]:
        if f["kind"] != "results":
            continue
        m = _GH_SUB_FILE_RE.match(f["path"])
        lang, sub = m.group(1), m.group(2)
        sub_specs.append((lang, sub, f))
        date, scaffold, model, parsed = parse_submission_dir(sub)
        subs_by_lang_agent[(lang, agent_key(scaffold, model))].append(sub)
    multi_batch = {k: v for k, v in subs_by_lang_agent.items() if len(v) > 1}
    for k, v in sorted(multi_batch.items()):
        c.hazards.append("FLAG same (language, scaffold, model) under %d batch dates: %s / %s: %s (kept as separate agents '<key>@<date>')" % (len(v), k[0], k[1], ", ".join(sorted(v))))
    meta_by_sub = {}
    for f in p["gh_files"]:
        if f["kind"] == "metadata":
            m = _GH_SUB_FILE_RE.match(f["path"])
            txt = gh_bytes[f["path"]].decode("utf-8", "replace")
            name = ""
            verified = None
            for line in txt.splitlines():
                if line.startswith("name:"):
                    name = line[5:].strip().strip("'\"")
                if line.startswith("verified:"):
                    verified = 1 if line[9:].strip().lower() == "true" else 0
            meta_by_sub[(m.group(1), m.group(2))] = (name, verified)
    results_keys = {(lang, sub) for lang, sub, _ in sub_specs}
    for k in sorted(set(meta_by_sub) - results_keys):
        c.hazards.append("submission dir without results/results.json (metadata.yaml only): %s/%s -> NOT ingested, no episodes" % k)
    zip_by_lang_agent = {}
    for (lang, sub), (dest, f) in zips.items():
        date, scaffold, model, parsed = parse_submission_dir(sub)
        k = (lang, agent_key(scaffold, model))
        if k in zip_by_lang_agent:
            c.hazards.append("FLAG two MSWE-agent-class zips for %s / %s: %s and %s (the first kept)" % (lang, k[1], zip_by_lang_agent[k][1]["submission"], sub))
            continue
        zip_by_lang_agent[k] = (dest, f, date)
    zips_joined = set()
    for lang, sub, f in sorted(sub_specs):
        date, scaffold, model, parsed = parse_submission_dir(sub)
        ak = agent_key(scaffold, model)
        agent = ak + ("@" + date if (lang, ak) in multi_batch else "")
        if not parsed:
            c.hazards.append("FLAG unparsable submission dir %s/%s: scaffold_raw = the dir name, model ''" % (lang, sub))
        d = _read_json_bytes(gh_bytes[f["path"]], f["path"])
        lists = {s: set(d.get(key) or []) for s, key in (("resolved", "resolved"), ("unresolved", "unresolved_ids"),
                                                         ("empty_error_patch", "empty_error_patch_ids"), ("incomplete", "incomplete_ids"))}
        completed = set(d.get("completed_ids") or [])
        submitted = set(d.get("submitted_ids") or [])
        universe = set().union(*lists.values()) | completed | submitted
        # count assertions (hazards, never silent)
        for s, key in (("resolved", "resolved_instances"), ("unresolved", "unresolved_instances"), ("empty_error_patch", "empty_error_patch_instances")):
            if key in d and d[key] != len(lists[s]):
                c.hazards.append("count mismatch %s/%s: %s=%d but %d ids" % (lang, sub, key, d[key], len(lists[s])))
        if "completed_instances" in d and d["completed_instances"] != len(completed):
            c.hazards.append("count mismatch %s/%s: completed_instances=%d but %d ids" % (lang, sub, d["completed_instances"], len(completed)))
        if (lists["resolved"] | lists["unresolved"]) != completed:
            c.hazards.append("completed_ids != resolved + unresolved in %s/%s (%d vs %d)" % (lang, sub, len(completed), len(lists["resolved"] | lists["unresolved"])))
        for a, b in (("resolved", "unresolved"), ("resolved", "empty_error_patch"), ("unresolved", "empty_error_patch")):
            ov = lists[a] & lists[b]
            if ov:
                c.hazards.append("ids in both %s and %s in %s/%s: %d (the first status wins)" % (a, b, lang, sub, len(ov)))
        zk = (lang, ak)
        zdest, zf, zdate = zip_by_lang_agent.get(zk, (None, None, None))
        swe_class = is_swe_agent_class(scaffold)
        if zf is not None:
            zips_joined.add(zk)
            if zdate != date:
                c.hazards.append("FLAG batch date differs across sources for %s / %s: github %s, hf zip %s" % (lang, ak, date, zdate))
        elif swe_class:
            c.hazards.append("MSWE-agent-class submission without a trajectory zip in the HF corpus of record: %s/%s (its episodes are ERROR under %s, the registered literal rule)" % (lang, sub, TERM_VERSION))
        members = {}
        zmembers = 0
        zh = zipfile.ZipFile(zdest) if zf is not None else None
        if zh is not None:
            for zi in zh.infolist():
                if zi.is_dir():
                    continue
                zmembers += 1
                base = zi.filename.split("/")[-1]
                if base.endswith(".traj"):
                    members[base[:-5]] = zi.filename
                else:
                    members[zi.filename.split("/")[0]] = zi.filename
        name, verified = meta_by_sub.get((lang, sub), ("", None))
        n_reports = 0
        for iid in sorted(universe):
            try:
                org, repo, pr = parse_instance_id(iid)
            except ValueError as e:
                c.hazards.append("%s/%s: %s" % (lang, sub, e))
                continue
            status = next((s for s in ("resolved", "unresolved", "empty_error_patch", "incomplete") if iid in lists[s]), "listed_only")
            t = c.tasks.get(iid)
            if t is None:
                fam = "%s/%s" % (org, repo)
                ck = split_side.stem_key(iid)
                t = {"instance_id": iid, "language": lang, "org": org, "repo": repo, "pr": pr, "family_id": fam, "content_key": ck,
                     "side": split_side.tier_b(fam, ck), "h": split_side.side_hash(fam), "h_instance": split_side.side_hash(ck),
                     "side_instance": split_side.side_of_hash(split_side.side_hash(ck)),
                     "in_index_json": 1 if iid in c.index_ids.get(lang, set()) else 0, "n_submissions": 0}
                c.tasks[iid] = t
            elif t["language"] != lang:
                c.hazards.append("instance %s under two languages: %s and %s" % (iid, t["language"], lang))
            t["n_submissions"] += 1
            rep = reports.get((lang, sub, iid))
            row = {"instance_id": iid, "agent": agent, "language": lang, "submission_dir": sub, "checker_status": status,
                   "resolved": 1 if status == "resolved" else 0, "checker_decided": 1 if status in ("resolved", "unresolved") else 0,
                   "report_json_present": 0, "report_valid": None, "f2p_pass": None, "f2p_total": None, "p2p_pass": None, "p2p_total": None,
                   "report_rule_resolved": None, "resolved_mismatch": 0, "f2p_vector": None, "p2p_vector": None,
                   "trajectory_present": 0, "exit_status": None, "mswe_term_v1": UNSTAMPED, "steps": None, "api_calls": None,
                   "artefact_bytes": None, "artefact_chars": None, "artefact_sha256": None}
            if rep is not None:
                n_reports += 1
                valid, fp, ft, pp, pt, rr, fv, pv = report_rule(rep)
                row.update({"report_json_present": 1, "report_valid": 1 if valid else 0, "f2p_pass": fp, "f2p_total": ft, "p2p_pass": pp, "p2p_total": pt,
                            "report_rule_resolved": 1 if rr else 0, "resolved_mismatch": 1 if (1 if rr else 0) != row["resolved"] else 0,
                            "f2p_vector": json.dumps(fv, separators=(",", ":")), "p2p_vector": json.dumps(pv, separators=(",", ":"))})
            if swe_class:
                if zf is None:
                    row["exit_status"] = MISSING_ARCHIVE
                    row["mswe_term_v1"] = mswe_term_v1(None, False, archive_present=False)
                elif iid not in members:
                    row["exit_status"] = MISSING_TRAJ
                    row["mswe_term_v1"] = mswe_term_v1(None, False)
                else:
                    b = zh.read(members[iid])
                    row.update({"trajectory_present": 1, "artefact_bytes": len(b), "artefact_sha256": sha256_bytes(b)})
                    try:
                        row["artefact_chars"] = len(b.decode("utf-8"))
                    except UnicodeDecodeError:
                        row["artefact_chars"] = len(b.decode("utf-8", "replace"))
                    try:
                        tj = json.loads(b.decode("utf-8", "replace"))
                        info = tj.get("info") if isinstance(tj, dict) else None
                        info = info if isinstance(info, dict) else {}
                        es = info.get("exit_status")
                        traj = tj.get("trajectory") if isinstance(tj, dict) else None
                        row["steps"] = len(traj) if isinstance(traj, list) else None
                        ms = info.get("model_stats") if isinstance(info.get("model_stats"), dict) else {}
                        row["api_calls"] = ms.get("api_calls")
                        row["exit_status"] = es if isinstance(es, str) else ABSENT_STATUS
                        row["mswe_term_v1"] = mswe_term_v1(es, True)
                        for k, v in info.items():
                            if any(t in str(k).casefold() for t in CAP_META_KEYS):
                                c.cap_metadata["%s=%s" % (k, v)] += 1
                    except Exception:  # noqa: BLE001 - an unparsable artefact is ERROR, counted
                        row["exit_status"] = UNPARSED_TRAJ
                        row["mswe_term_v1"] = mswe_term_v1(None, True, parsed=False)
                c.status_enum[row["exit_status"]] += 1
            key = (iid, agent)
            if key in c.episodes:
                c.hazards.append("duplicate episode %s / %s (second occurrence from %s/%s dropped)" % (iid, agent, lang, sub))
                continue
            c.episodes[key] = row
        if zh is not None:
            zh.close()
            extra = set(members) - universe
            if extra:
                c.hazards.append("%d trajectories without a checker row in %s/%s (first: %s)" % (len(extra), lang, sub, sorted(extra)[0]))
        c.submissions.append({"language": lang, "dir_name": sub, "batch_date": date, "scaffold_raw": scaffold, "model_raw": model, "agent": agent,
                              "results_sha256": sha256_bytes(gh_bytes[f["path"]]), "total_instances": d.get("total_instances"),
                              "submitted_instances": d.get("submitted_instances"), "completed_instances": d.get("completed_instances"),
                              "resolved_instances": d.get("resolved_instances"), "unresolved_instances": d.get("unresolved_instances"),
                              "empty_error_patch_instances": d.get("empty_error_patch_instances"), "incomplete_instances": len(lists["incomplete"]),
                              "n_report_json": n_reports, "zip_path": (zf["path"] if zf else None), "zip_batch_date": zdate,
                              "zip_sha256": (zf["sha256"] if zf else None), "zip_members": (zmembers if zf else None),
                              "metadata_name": name, "verified": verified})
        a = c.agents.get(agent)
        if a is None:
            a = {"agent": agent, "scaffold_key": ak.split("|")[0], "model_key": ak.split("|")[1], "scaffold_raw": set(), "model_raw": set(),
                 "batch_dates": set(), "n_submissions": 0, "languages": set(), "swe_agent_class": 1 if swe_class else 0, "archives_present": 0,
                 "flagged_multi_batch": 1 if (lang, ak) in multi_batch else 0, "flagged_date_mismatch": 0}
            c.agents[agent] = a
        a["scaffold_raw"].add(scaffold)
        a["model_raw"].add(model)
        a["batch_dates"].add(date)
        a["n_submissions"] += 1
        a["languages"].add(lang)
        if zf is not None:
            a["archives_present"] += 1
            if zdate != date:
                a["flagged_date_mismatch"] += 1
    for k in sorted(set(zip_by_lang_agent) - zips_joined):
        c.hazards.append("HF zip without a GitHub submission: %s / %s (%s)" % (k[0], k[1], zip_by_lang_agent[k][1]["submission"]))
    joined_reports = sum(e["report_json_present"] for e in c.episodes.values())
    if joined_reports != len(reports):
        c.hazards.append("%d report.json files, %d joined to an episode" % (len(reports), joined_reports))
    c.complete = True
    if verbose:
        print(summarise(c))
    return c


def summarise(c):
    L = []
    P = L.append
    P("submissions %d over %d languages; agents %d (%d in the MSWE-agent class); tasks %d; episodes %d; report.json joined %d"
      % (len(c.submissions), len(set(s["language"] for s in c.submissions)), len(c.agents),
         sum(a["swe_agent_class"] for a in c.agents.values()), len(c.tasks), len(c.episodes), sum(e["report_json_present"] for e in c.episodes.values())))
    per_lang = Counter(t["language"] for t in c.tasks.values())
    for lang in LANGUAGES:
        idx = c.index_ids.get(lang, set())
        ours = {t["instance_id"] for t in c.tasks.values() if t["language"] == lang}
        P("  %-11s instances %4d (paper %4d) | index.json all_ids %4d | ours-not-index %d | index-not-ours %d"
          % (lang, per_lang.get(lang, 0), PAPER_COUNTS[lang], len(idx), len(ours - idx), len(idx - ours)))
    st = Counter(e["checker_status"] for e in c.episodes.values())
    P("  checker_status: %s" % ", ".join("%s=%d" % (s, st.get(s, 0)) for s in CHECKER_STATUSES))
    P("  resolved_mismatch (report.json rule vs results.json flag): %d of %d report.json rows" % (
        sum(e["resolved_mismatch"] for e in c.episodes.values()), sum(e["report_json_present"] for e in c.episodes.values())))
    cls = Counter(e["mswe_term_v1"] for e in c.episodes.values())
    P("  %s classes: %s" % (TERM_VERSION, ", ".join("%s=%d" % (k, cls.get(k, 0)) for k in (TERMINATED, CAP_HIT, ERROR, UNKNOWN, UNSTAMPED))))
    P("  exit-status enumeration (MSWE-agent class, %d episodes):" % sum(c.status_enum.values()))
    for s, n in sorted(c.status_enum.items(), key=lambda kv: (-kv[1], kv[0])):
        P("    %6d  %-40s -> %s" % (n, s, status_class(s)))
    P("  cap metadata keys in trajectories: %s" % (", ".join("%s x%d" % kv for kv in sorted(c.cap_metadata.items())) or "none (UNSTAMPED)"))
    fams = defaultdict(set)
    for t in c.tasks.values():
        fams[t["family_id"]].add(t["side"])
    P("  families %d; straddling (two sides in one family) %d" % (len(fams), sum(1 for v in fams.values() if len(v) > 1)))
    P("hazards: %d" % len(c.hazards))
    for h in c.hazards[:80]:
        P("  " + h)
    if len(c.hazards) > 80:
        P("  ... %d more" % (len(c.hazards) - 80))
    return "\n".join(L)


DDL = """
CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE tasks(instance_id TEXT PRIMARY KEY, language TEXT NOT NULL, org TEXT NOT NULL, repo TEXT NOT NULL, pr INTEGER NOT NULL,
  family_id TEXT NOT NULL, content_key TEXT NOT NULL, side TEXT NOT NULL CHECK (side IN ('EVAL','GATE','TRAIN')), h INTEGER NOT NULL,
  h_instance INTEGER NOT NULL, side_instance TEXT NOT NULL, in_index_json INTEGER NOT NULL, n_submissions INTEGER NOT NULL);
CREATE TABLE agents(agent TEXT PRIMARY KEY, scaffold_key TEXT NOT NULL, model_key TEXT NOT NULL, scaffold_raw TEXT, model_raw TEXT,
  batch_dates TEXT, n_submissions INTEGER, languages TEXT, swe_agent_class INTEGER NOT NULL, archives_present INTEGER NOT NULL,
  flagged_multi_batch INTEGER NOT NULL, flagged_date_mismatch INTEGER NOT NULL);
CREATE TABLE submissions(language TEXT NOT NULL, dir_name TEXT NOT NULL, batch_date TEXT, scaffold_raw TEXT, model_raw TEXT, agent TEXT NOT NULL,
  results_sha256 TEXT, total_instances INTEGER, submitted_instances INTEGER, completed_instances INTEGER, resolved_instances INTEGER,
  unresolved_instances INTEGER, empty_error_patch_instances INTEGER, incomplete_instances INTEGER, n_report_json INTEGER, zip_path TEXT,
  zip_batch_date TEXT, zip_sha256 TEXT, zip_members INTEGER, metadata_name TEXT, verified INTEGER, PRIMARY KEY (language, dir_name));
CREATE TABLE episodes(instance_id TEXT NOT NULL, agent TEXT NOT NULL, language TEXT NOT NULL, submission_dir TEXT NOT NULL,
  checker_status TEXT NOT NULL, resolved INTEGER NOT NULL, checker_decided INTEGER NOT NULL, report_json_present INTEGER NOT NULL,
  report_valid INTEGER, f2p_pass INTEGER, f2p_total INTEGER, p2p_pass INTEGER, p2p_total INTEGER, report_rule_resolved INTEGER,
  resolved_mismatch INTEGER NOT NULL, f2p_vector TEXT, p2p_vector TEXT, trajectory_present INTEGER NOT NULL, exit_status TEXT,
  mswe_term_v1 TEXT NOT NULL, steps INTEGER, api_calls INTEGER, artefact_bytes INTEGER, artefact_chars INTEGER, artefact_sha256 TEXT,
  PRIMARY KEY (instance_id, agent));
CREATE TABLE provenance(path TEXT PRIMARY KEY, source TEXT NOT NULL, bytes INTEGER NOT NULL, sha256 TEXT NOT NULL, upstream_sha TEXT, revision TEXT);
CREATE VIEW instances AS SELECT * FROM tasks;
CREATE VIEW checker AS SELECT instance_id, agent,
  CASE checker_status WHEN 'resolved' THEN 'RESOLVED' WHEN 'unresolved' THEN 'UNRESOLVED' ELSE 'UNDECIDED:' || checker_status END AS output,
  f2p_vector, p2p_vector, checker_sha FROM episodes;
"""
EPISODE_COLS = ["instance_id", "agent", "language", "submission_dir", "checker_status", "resolved", "checker_decided", "report_json_present",
                "report_valid", "f2p_pass", "f2p_total", "p2p_pass", "p2p_total", "report_rule_resolved", "resolved_mismatch", "f2p_vector",
                "p2p_vector", "trajectory_present", "exit_status", "mswe_term_v1", "steps", "api_calls", "artefact_bytes", "artefact_chars",
                "artefact_sha256"]


def checker_sha(e):
    out = "RESOLVED" if e["checker_status"] == "resolved" else ("UNRESOLVED" if e["checker_status"] == "unresolved" else "UNDECIDED:" + e["checker_status"])
    return sha256_bytes(("%s\x1f%s\x1f%s" % (out, e["f2p_vector"] or "", e["p2p_vector"] or "")).encode("utf-8"))


def build_db(db_path, c):
    if not c.complete:
        raise SystemExit("[MULTISWE-INGEST] refusing to build from an incomplete ingest")
    refuse_if_exists(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    tmp = db_path + ".building"
    if os.path.exists(tmp):
        os.remove(tmp)
    conn = sqlite3.connect(tmp)
    try:
        conn.executescript(DDL)
        conn.execute("ALTER TABLE episodes ADD COLUMN checker_sha TEXT")
        for t in c.tasks.values():
            split_side.assert_row(t["side"], t["family_id"], t["content_key"], where="tasks.side")
        conn.executemany("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         [(t["instance_id"], t["language"], t["org"], t["repo"], t["pr"], t["family_id"], t["content_key"], t["side"], t["h"],
                           t["h_instance"], t["side_instance"], t["in_index_json"], t["n_submissions"]) for t in c.tasks.values()])
        conn.executemany("INSERT INTO agents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         [(a["agent"], a["scaffold_key"], a["model_key"], ",".join(sorted(a["scaffold_raw"])), ",".join(sorted(a["model_raw"])),
                           ",".join(sorted(a["batch_dates"])), a["n_submissions"], ",".join(sorted(a["languages"])), a["swe_agent_class"],
                           a["archives_present"], a["flagged_multi_batch"], a["flagged_date_mismatch"]) for a in c.agents.values()])
        scols = ["language", "dir_name", "batch_date", "scaffold_raw", "model_raw", "agent", "results_sha256", "total_instances", "submitted_instances",
                 "completed_instances", "resolved_instances", "unresolved_instances", "empty_error_patch_instances", "incomplete_instances",
                 "n_report_json", "zip_path", "zip_batch_date", "zip_sha256", "zip_members", "metadata_name", "verified"]
        conn.executemany("INSERT INTO submissions(%s) VALUES (%s)" % (",".join(scols), ",".join("?" * len(scols))),
                         [tuple(s[k] for k in scols) for s in c.submissions])
        cols = EPISODE_COLS + ["checker_sha"]
        conn.executemany("INSERT INTO episodes(%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))),
                         [tuple(e[k] for k in EPISODE_COLS) + (checker_sha(e),) for e in c.episodes.values()])
        conn.executemany("INSERT INTO provenance VALUES (?,?,?,?,?,?)", c.files)
        meta = {"corpus": corpus_name(c.hf_rev), "date": DATE, "hf_repo": HF_REPO, "hf_revision": c.hf_rev, "hf_licence": HF_LICENCE,
                "github_repo": GH_OWNER_REPO, "github_sha": c.gh_sha, "github_licence": GH_LICENCE,
                "normaliser_version": split_side.NORMALISER_VERSION, "key_rule": split_side.KEY_RULE + " (stem_key over the instance id; options-free)",
                "checker_version": CHECKER_VERSION,
                "checker_rule": "resolved iff instance_id in results.json 'resolved'; unresolved iff in 'unresolved_ids'; checker_decided iff "
                                "resolved or unresolved (= completed_ids); empty_error_patch_ids / incomplete_ids / listed_only NOT decided. "
                                "Where report.json exists: rule = valid AND every f2p_tests[*].fix == PASS AND every p2p_tests[*].fix == PASS, "
                                "compared with the flag; a mismatch is counted (episodes.resolved_mismatch) and the results.json flag wins.",
                "term_version": TERM_VERSION,
                "term_rule": "TERMINATED: exit_status == 'submitted' or a TERMINATED_TOKEN (%s); CAP_HIT: any CAP_TOKEN (%s), the cap qualifier "
                             "winning over 'submitted'; ERROR: trajectory / archive missing or unparsed, or any ERROR_TOKEN (%s); UNKNOWN: present "
                             "and outside the map; UNSTAMPED: scaffold outside the MSWE-agent class (%s). Precedence submitted > cap > error > "
                             "terminated-tokens > unknown." % (",".join(TERMINATED_TOKENS), ",".join(CAP_TOKENS), ",".join(ERROR_TOKENS), ",".join(SWE_AGENT_SCAFFOLDS)),
                "side_rule": "tasks.side = split_side.tier_b(family_id, content_key) with family_id = org/repo (h over the family; EVAL < 300, GATE "
                             "[300, 400)); side_instance = side_of_hash(side_hash(stem_key(instance_id))) DESCRIPTIVE only",
                "model_aliases": json.dumps(MODEL_ALIASES, sort_keys=True), "swe_agent_scaffolds": ",".join(SWE_AGENT_SCAFFOLDS),
                "cap_metadata": json.dumps(sorted(c.cap_metadata.items())) if c.cap_metadata else "none (UNSTAMPED)",
                "exit_status_enumeration": json.dumps(sorted(c.status_enum.items())),
                "hazards": json.dumps(c.hazards), "n_hazards": str(len(c.hazards)),
                "ingest_complete": "1", "script_sha": script_sha(), "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "pool_id": "NONE at ingest (the readout exports the EVAL ids and prints the id)"}
        conn.executemany("INSERT INTO meta VALUES (?,?)", list(meta.items()))
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp, db_path)
    return db_path


# --------------------------------------------------------------------------------------------------------------
# readout (from the DB, read-only)
# --------------------------------------------------------------------------------------------------------------
def open_ro(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def readout(db_path, out_txt, out_csv, pool_dir, support_min=SUPPORT_MIN, roster_min=ROSTER_MIN, recovery_min=CAP_RECOVERY_MIN, verbose=True):
    refuse_if_exists(out_txt)
    refuse_if_exists(out_csv)
    conn = open_ro(db_path)
    conn.row_factory = sqlite3.Row
    meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}
    if meta.get("ingest_complete") != "1":
        raise SystemExit("[MULTISWE-INGEST] the DB was not written from a complete ingest; no readout")
    tasks = [dict(r) for r in conn.execute("SELECT * FROM tasks")]
    agents = {r["agent"]: dict(r) for r in conn.execute("SELECT * FROM agents")}
    episodes = [dict(r) for r in conn.execute("SELECT * FROM episodes")]
    conn.close()
    for t in tasks:
        split_side.assert_row(t["side"], t["family_id"], t["content_key"], where="readout tasks.side")
    # --- pool export (write-once) ---
    ids_by_key = defaultdict(list)
    for t in tasks:
        if t["side"] == "EVAL":
            ids_by_key["MULTISWE/%s/%s__%s" % (t["language"], t["org"], t["repo"])].append(t["pr"])
    ids_by_key = {k: sorted(v) for k, v in sorted(ids_by_key.items())}
    pool_id = compute_pool_id(ids_by_key)
    pool_path = os.path.join(pool_dir, "reserved_pool_frozen_multiswe_%s.json" % pool_id)
    refuse_if_exists(pool_path)
    # --- strata ---
    by_stratum = defaultdict(list)
    for t in tasks:
        by_stratum[(t["language"], t["family_id"])].append(t)
    ep_by_stratum = defaultdict(list)
    task_lang_fam = {t["instance_id"]: (t["language"], t["family_id"]) for t in tasks}
    for e in episodes:
        ep_by_stratum[task_lang_fam[e["instance_id"]]].append(e)
    strata = []
    for (lang, fam), ts in by_stratum.items():
        n = len(ts)
        side = ts[0]["side"]
        h = ts[0]["h"]
        n_eval = n if side == "EVAL" else 0
        n_eval_inst = sum(1 for t in ts if t["side_instance"] == "EVAL")
        eps = ep_by_stratum[(lang, fam)]
        per_agent = defaultdict(set)
        for e in eps:
            per_agent[e["agent"]].add(e["instance_id"])
        complete = sorted(a for a, s in per_agent.items() if len(s) == n)
        swe = [e for e in eps if agents[e["agent"]]["swe_agent_class"]]
        swe_num = sum(1 for e in swe if e["mswe_term_v1"] == TERMINATED and e["checker_decided"])
        swe_den = len(swe)
        lo, hi = wilson(swe_num, swe_den)
        other = [e for e in eps if not agents[e["agent"]]["swe_agent_class"]]
        other_res = (sum(e["resolved"] for e in other) / len(other)) if other else float("nan")
        strata.append({"language": lang, "family_id": fam, "n_instances": n, "h": h, "side": side, "n_eval": n_eval,
                       "n_eval_instance_split_descriptive": n_eval_inst, "n_agents_any": len(per_agent), "largest_complete_roster": len(complete),
                       "complete_roster_agents": ";".join(complete), "c1_clears": 1 if n_eval >= support_min else 0,
                       "dc_swe_num": swe_num, "dc_swe_den": swe_den, "dc_swe": (swe_num / swe_den) if swe_den else float("nan"),
                       "dc_swe_wilson_lo": lo, "dc_swe_wilson_hi": hi, "other_scaffolds_n": len(other), "other_scaffolds_resolved_share": other_res})
    strata.sort(key=lambda s: (LANGUAGES.index(s["language"]) if s["language"] in LANGUAGES else 99, -s["n_instances"], s["family_id"]))
    c1_strata = [s for s in strata if s["c1_clears"]]
    c1 = len(c1_strata) >= 1
    # --- C2 ---
    swe_eps = [e for e in episodes if agents[e["agent"]]["swe_agent_class"]]
    enum = Counter(e["exit_status"] for e in swe_eps)
    cls = Counter(e["mswe_term_v1"] for e in swe_eps)
    recovered = cls[TERMINATED] + cls[CAP_HIT] + cls[ERROR]
    c2_rate = recovered / len(swe_eps) if swe_eps else float("nan")
    c2 = bool(swe_eps) and c2_rate >= recovery_min
    swe_with_archive = [e for e in swe_eps if e["exit_status"] != MISSING_ARCHIVE]
    cls_arch = Counter(e["mswe_term_v1"] for e in swe_with_archive)
    rec_arch = cls_arch[TERMINATED] + cls_arch[CAP_HIT] + cls_arch[ERROR]
    real_statuses = sorted(s for s in enum if s and not s.startswith("<"))
    steps_all = [e["steps"] for e in swe_eps if e["steps"] is not None]
    steps_cap = [e["steps"] for e in swe_eps if e["steps"] is not None and e["mswe_term_v1"] == CAP_HIT]
    cap_meta = meta.get("cap_metadata", "none (UNSTAMPED)")
    # --- C3 ---
    c3 = all(s["largest_complete_roster"] >= roster_min for s in c1_strata) if c1_strata else False
    # --- D_c pooled ---
    dc_num = sum(1 for e in swe_eps if e["mswe_term_v1"] == TERMINATED and e["checker_decided"])
    dc_den = len(swe_eps)
    dc_lo, dc_hi = wilson(dc_num, dc_den)
    dc_alt_num = sum(1 for e in swe_eps if e["mswe_term_v1"] == TERMINATED and (e["checker_decided"] or e["checker_status"] == "empty_error_patch"))
    # --- P ---
    per_lang = Counter(t["language"] for t in tasks)
    p_rows = [(lang, per_lang.get(lang, 0), PAPER_COUNTS[lang]) for lang in LANGUAGES]
    total = sum(per_lang.values())
    non_python = total - per_lang.get("python", 0)
    p_held = all(n == want for _, n, want in p_rows) and total == PAPER_TOTAL and non_python == PAPER_NON_PYTHON
    # --- predictions ---
    n_c1 = len(c1_strata)
    p1 = 2 <= n_c1 <= 4
    p1p = 0 <= n_c1 <= 2
    p2 = c2 and 3 <= len(real_statuses) <= 8
    non_py = [s for s in strata if s["language"] != "python"]
    late_agents = [a for a, r in agents.items() if r["scaffold_key"] in ("magentless", "mopenhands") and r["model_key"] in ("doubao-1.5-thinking", "gemini-2.5-pro", "llama-4-maverick")]
    late_incomplete = []
    for a in late_agents:
        for s in strata:
            if a not in s["complete_roster_agents"].split(";"):
                late_incomplete.append((a, s["language"], s["family_id"]))
                break
    p3 = bool(non_py) and all(9 <= s["largest_complete_roster"] <= 27 for s in non_py) and bool(late_agents) and bool(late_incomplete)
    p4 = p_held
    dc_pooled = dc_num / dc_den if dc_den else float("nan")
    p5 = dc_den > 0 and 0.80 <= dc_pooled <= 0.95 and cls[CAP_HIT] > cls[ERROR]

    def hf(x):
        return "HELD" if x else "FAILED"

    L = []
    P = L.append
    P("MULTI-SWE-ADMISSION (cheap variant) readout; registered 2026-09-22, docs/judge_v2_program.md L9801-L9918 (b97da18); zero LLM calls")
    P("corpus=%s pool_id=%s" % (meta.get("corpus"), pool_id))
    P("db=%s hf=%s@%s github=%s@%s script_sha=%s db_script_sha=%s" % (db_path, meta.get("hf_repo"), meta.get("hf_revision"), meta.get("github_repo"),
                                                                     meta.get("github_sha"), script_sha()[:16], (meta.get("script_sha") or "")[:16]))
    P("checker %s: %s" % (meta.get("checker_version"), meta.get("checker_rule")))
    P("termination %s: %s" % (meta.get("term_version"), meta.get("term_rule")))
    P("agents %d; MSWE-agent class %d (%s); tasks %d; episodes %d; hazards at ingest %s" % (
        len(agents), sum(a["swe_agent_class"] for a in agents.values()), meta.get("swe_agent_scaffolds"), len(tasks), len(episodes), meta.get("n_hazards")))
    P("")
    P("== C1 STRATUM SUPPORT: (language, repo) strata; side under norm-v1 h = side_hash(family_id) with family_id = org/repo; EVAL count is 0 or the whole stratum ==")
    P("denominator: the union of instance ids over every submission's results.json lists per language (%d instances; index.json all_ids beside in the P block)" % len(tasks))
    P("%-11s %-40s %5s %4s %-5s %5s | %8s | %6s %5s %s" % ("language", "org/repo", "n", "h", "side", "EVAL", "EVAL@inst", "agents", "cmplt", "(EVAL@inst = DESCRIPTIVE instance-within-repo split, never scored)"))
    for s in strata:
        P("%-11s %-40s %5d %4d %-5s %5d | %8d | %6d %5d" % (s["language"], s["family_id"], s["n_instances"], s["h"], s["side"], s["n_eval"],
                                                             s["n_eval_instance_split_descriptive"], s["n_agents_any"], s["largest_complete_roster"]))
    P("strata %d; EVAL-side strata %d; strata with >= %d EVAL instances: %d %s" % (
        len(strata), sum(1 for s in strata if s["side"] == "EVAL"), support_min, n_c1, "; ".join("%s/%s (%d)" % (s["language"], s["family_id"], s["n_eval"]) for s in c1_strata) or "none"))
    P("descriptive instance-within-repo split: strata with >= %d EVAL instances would be %d (no pool file, not scored)" % (
        support_min, sum(1 for s in strata if s["n_eval_instance_split_descriptive"] >= support_min)))
    P("C1: %s (>= 1 stratum with >= %d EVAL instances)" % (hf(c1), support_min))
    P("")
    P("== C2 CAP RECOVERY, MSWE-agent class (%s) ==" % meta.get("swe_agent_scaffolds"))
    P("denominator: every (instance, MSWE-agent-class agent) episode with a checker row = %d (of which %d under an agent with a trajectory archive)" % (len(swe_eps), len(swe_with_archive)))
    P("exit-status enumeration (%d distinct strings from trajectories; markers in <> are the script's):" % len(real_statuses))
    for s, n in sorted(enum.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        P("  %6d  %-40s -> %s" % (n, s, status_class(s)))
    P("classes: %s" % ", ".join("%s=%d" % (k, cls.get(k, 0)) for k in (TERMINATED, CAP_HIT, ERROR, UNKNOWN)))
    P("recovered (TERMINATED + CAP_HIT + ERROR, the registered literal rule; archive absence = ERROR): %d / %d = %.4f" % (recovered, len(swe_eps), c2_rate))
    P("recovered conditional on an archive present (DESCRIPTIVE): %d / %d = %s" % (rec_arch, len(swe_with_archive), ("%.4f" % (rec_arch / len(swe_with_archive))) if swe_with_archive else "n/a"))
    P("cap DECLARED: %s" % ("UNSTAMPED: the trajectories carry no cap value in info (keys scanned: %s); empirical max steps over %d episodes = %s, among CAP_HIT = %s"
                            % (",".join(CAP_META_KEYS), len(steps_all), max(steps_all) if steps_all else "n/a", max(steps_cap) if steps_cap else "n/a")
                            if cap_meta.startswith("none") else "from trajectory metadata: %s" % cap_meta))
    P("C2: %s (recovered >= %.2f)" % (hf(c2), recovery_min))
    P("")
    P("== C3 ROSTER COMPLETENESS: agents with a checker row on EVERY instance of the stratum (the cmplt column above) ==")
    for s in strata:
        P("  %-11s %-40s n=%4d complete roster %2d: %s" % (s["language"], s["family_id"], s["n_instances"], s["largest_complete_roster"], s["complete_roster_agents"] or "-"))
    P("C3: %s (every C1 stratum has a complete roster >= %d; C1 strata: %d)" % (hf(c3), roster_min, n_c1))
    P("")
    P("== D_c strict (TERMINATED and checker-decided) / ALL episodes, MSWE-agent class, Wilson 95%; PRINTED, not scored ==")
    for s in strata:
        P("  %-11s %-40s D_c %3d/%3d = %s [%s, %s] | other scaffolds: UNDETERMINED (UNSTAMPED), resolved share %s over %d" % (
            s["language"], s["family_id"], s["dc_swe_num"], s["dc_swe_den"], ("%.3f" % s["dc_swe"]) if s["dc_swe_den"] else "n/a",
            ("%.3f" % s["dc_swe_wilson_lo"]) if s["dc_swe_den"] else "n/a", ("%.3f" % s["dc_swe_wilson_hi"]) if s["dc_swe_den"] else "n/a",
            ("%.3f" % s["other_scaffolds_resolved_share"]) if s["other_scaffolds_n"] else "n/a", s["other_scaffolds_n"]))
    P("pooled strict D_c (MSWE-agent class): %d / %d = %s [%s, %s]; alternative reading empty patch = decided fail (DESCRIPTIVE): %d / %d = %s" % (
        dc_num, dc_den, ("%.4f" % dc_pooled) if dc_den else "n/a", ("%.4f" % dc_lo) if dc_den else "n/a", ("%.4f" % dc_hi) if dc_den else "n/a",
        dc_alt_num, dc_den, ("%.4f" % (dc_alt_num / dc_den)) if dc_den else "n/a"))
    P("")
    P("== P REPRODUCTION of the corpus counts (union of results.json ids per language; index.json all_ids beside) ==")
    for lang, n, want in p_rows:
        idx = [t for t in tasks if t["language"] == lang]
        n_idx = sum(t["in_index_json"] for t in idx)
        P("  %-11s ours %4d  paper %4d  %s | in index.json %4d, ours-not-in-index %d" % (lang, n, want, "exact" if n == want else "DEVIATION %+d" % (n - want), n_idx, len(idx) - n_idx))
        if n != want:
            P("    ids not in index.json: %s" % (", ".join(sorted(t["instance_id"] for t in idx if not t["in_index_json"])[:50]) or "none"))
    P("  total %d (paper %d); python %d (paper %d); non-python %d (paper %d)" % (total, PAPER_TOTAL, per_lang.get("python", 0), PAPER_PYTHON, non_python, PAPER_NON_PYTHON))
    P("P: %s (all eight counts exact)" % hf(p_held))
    P("")
    P("== PREDICTIONS (blind, registered) ==")
    P("P1  (lead) 2-4 strata with >= %d EVAL instances: %d -> %s" % (support_min, n_c1, hf(p1)))
    P("P1' (registrar) 0-2 under the by-repo split: %d -> %s" % (n_c1, hf(p1p)))
    P("P2  (lead) C2 HELD and 3-8 distinct exit-status strings: C2 %s, %d strings -> %s" % (hf(c2), len(real_statuses), hf(p2)))
    P("P3  (lead) largest complete roster per non-Python stratum in [9, 27] (%s) and the later MagentLess / MopenHands batches (%d agents) incomplete on >= 1 stratum (%s) -> %s" % (
        ("min %d max %d" % (min(s["largest_complete_roster"] for s in non_py), max(s["largest_complete_roster"] for s in non_py))) if non_py else "no non-Python stratum",
        len(late_agents), ("; ".join("%s misses %s/%s" % x for x in late_incomplete[:6]) or "none incomplete"), hf(p3)))
    P("P4  the eight counts exact -> %s" % hf(p4))
    P("P5  (registrar, descriptive) pooled strict D_c in [0.80, 0.95] (%s) and CAP_HIT (%d) > ERROR (%d) -> %s" % (("%.4f" % dc_pooled) if dc_den else "n/a", cls[CAP_HIT], cls[ERROR], hf(p5)))
    P("")
    if not c1:
        P("FALSIFIER: C1 FAILED -> agents stay DESCRIPTION-ONLY on this corpus; MopenHands / MagentLess trajectories are never downloaded; the survey's "
          "'only surveyed corpus that can carry an agent PROFILE cell' is overturned for the by-repo split; no BFCL number and nothing judged is touched.")
    else:
        P("FALSIFIER not triggered on C1: %d stratum/strata clear %d EVAL instances (a HELD C1 prices the judged pass in its own later registration; nothing judged is scheduled here)." % (n_c1, support_min))
    if swe_eps and not c2:
        P("FALSIFIER: C2 FAILED (%.4f < %.2f) -> the survey's (c) reading 'MSWE-agent trajs carry exit status' is overturned for this release; rule (c) unmet on every scaffold of this corpus." % (c2_rate, recovery_min))
    else:
        P("C2 not falsified: %s." % ("recovered %.4f >= %.2f" % (c2_rate, recovery_min) if swe_eps else "no MSWE-agent-class episode (n/a)"))
    P("UNDETERMINED strata (EVAL count between 1 and %d): %d, admitted for description only." % (support_min - 1, sum(1 for s in strata if 0 < s["n_eval"] < support_min)))
    P("pool export: %s (%d EVAL instances over %d repos; declared in no config, registered in no registry, read by no tree)" % (pool_path, sum(len(v) for v in ids_by_key.values()), len(ids_by_key)))
    P("hygiene: zero LLM calls; no pool of record read; no DB of record opened; the DB and this file written once.")
    text = "\n".join(L) + "\n"
    os.makedirs(os.path.dirname(out_txt), exist_ok=True)
    os.makedirs(pool_dir, exist_ok=True)
    with open(pool_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ids_by_key, f, indent=2, sort_keys=True)
        f.write("\n")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        cols = ["language", "family_id", "n_instances", "h", "side", "n_eval", "n_eval_instance_split_descriptive", "n_agents_any", "largest_complete_roster",
                "complete_roster_agents", "c1_clears", "dc_swe_num", "dc_swe_den", "dc_swe", "dc_swe_wilson_lo", "dc_swe_wilson_hi", "other_scaffolds_n",
                "other_scaffolds_resolved_share"]
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for s in strata:
            w.writerow({k: s[k] for k in cols})
    with open(out_txt, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    if verbose:
        print(text)
    return {"c1": c1, "c2": c2, "c3": c3, "p": p_held, "p1": p1, "p1p": p1p, "p2": p2, "p3": p3, "p4": p4, "p5": p5, "n_c1": n_c1,
            "c2_rate": c2_rate, "dc_pooled": dc_pooled, "dc_num": dc_num, "dc_den": dc_den, "pool_id": pool_id, "pool_path": pool_path,
            "strata": strata, "enum": enum, "classes": cls, "ids_by_key": ids_by_key}


# --------------------------------------------------------------------------------------------------------------
# selftest on a synthetic mini-corpus
# --------------------------------------------------------------------------------------------------------------
def _find_repo(side, prefix, start=0):
    """A family id 'orgX/<prefix>-<n>' whose family hash lands on the wanted side (deterministic search)."""
    n = start
    while True:
        fam = "orgX/%s-%d" % (prefix, n)
        if split_side.tier_b(fam, "") == side:
            return fam
        n += 1


def _fixture(raw_dir):
    """Two languages (c, java), three repos (c: E on EVAL with 5 instances, T on TRAIN with 3; java: G on GATE with 4),
    two scaffolds (MSWE-agent, MopenHands), three models (M1, M2, M3): MSWE-agent x {M1, M2, M3}, MopenHands x {M1, M2},
    plus MopenHands/M1 under a second java batch date (multi-batch flag). Planted: statuses submitted / submitted
    (exit_cost) / exit_error / weird_status; a missing .traj; an MSWE-agent agent (M3) without a zip; a report.json pair
    for MopenHands/M1 in c with one consistent and one mismatching row; a zip batch date differing from GitHub's."""
    gh_dir = os.path.join(raw_dir, "github")
    hf_dir = os.path.join(raw_dir, "hf")
    fam_e = _find_repo("EVAL", "repoE")
    fam_t = _find_repo("TRAIN", "repoT")
    fam_g = _find_repo("GATE", "repoG")
    repos = {"c": [(fam_e, [11, 12, 13, 14, 15]), (fam_t, [21, 22, 23])], "java": [(fam_g, [31, 32, 33, 34])]}

    def iid(fam, pr):
        org, repo = fam.split("/")
        return "%s__%s-%d" % (org, repo, pr)

    universe = {lang: [iid(f, p) for f, prs in repos[lang] for p in prs] for lang in repos}
    blobs = []

    def put(path, data):
        full = os.path.join(gh_dir, *path.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(data)
        blobs.append({"path": path, "type": "blob", "size": len(data), "sha": git_blob_sha1(data)})

    put("LICENSE", b"Apache-2.0 fixture\n")
    put("index.yaml", b"c:\n  name: C\njava:\n  name: Java\n")
    for lang in repos:
        put("evaluation/%s/verified/index.json" % lang, json.dumps({"all_ids": universe[lang] + (["orgZ__extra-1"] if lang == "java" else [])}).encode())
    # submissions: (lang, dir, resolved, unresolved, empty, incomplete, listed_only_extra)
    subs = []
    for lang in repos:
        U = universe[lang]
        subs.append((lang, "20250329_MSWE-agent_M1", U[:2], U[2:], [], []))
        subs.append((lang, "20250329_MSWE-agent_M2", [U[0]], U[1:-1], [U[-1]], []))
        subs.append((lang, "20250426_MSWE-agent_M3", [], U[:-1], [], [U[-1]]))
        subs.append((lang, "20250329_MopenHands_M1", U[:3], U[3:], [], []))
        subs.append((lang, "20250329_MopenHands_M2", [], U[:-1], [], []))   # incomplete roster: misses the last instance
    subs.append(("java", "20250514_MopenHands_M1", [], universe["java"], [], []))  # same (lang, scaffold, model), second batch
    for lang, sub, res, unres, empty, inc in subs:
        completed = res + unres
        d = {"total_instances": len(res) + len(unres) + len(empty) + len(inc), "submitted_instances": len(completed) + len(empty),
             "completed_instances": len(completed), "resolved_instances": len(res), "unresolved_instances": len(unres),
             "empty_error_patch_instances": len(empty), "unstopped_instances": 0, "completed_ids": completed, "incomplete_ids": inc,
             "submitted_ids": completed + empty, "resolved": res, "unresolved_ids": unres, "empty_error_patch_ids": empty,
             "unstopped_containers": [], "unremoved_images": []}
        put("evaluation/%s/verified/%s/results/results.json" % (lang, sub), json.dumps(d).encode())
        put("evaluation/%s/verified/%s/metadata.yaml" % (lang, sub), ("name: %s\nverified: true\n" % sub.replace("_", " + ")).encode())
        put("evaluation/%s/verified/%s/all_preds.jsonl" % (lang, sub), b'{"instance_id": "x", "model_patch": ""}\n')
    # report.json for MopenHands/M1 in c: instance U[0] resolved and consistent; U[3] unresolved in results.json but the rule says resolved (mismatch)
    U = universe["c"]
    for inst in (U[0], U[3]):
        org, repo, pr = parse_instance_id(inst)
        rep = {"org": org, "repo": repo, "number": pr, "valid": True, "f2p_tests": {"t1": {"run": "FAIL", "test": "FAIL", "fix": "PASS"}},
               "p2p_tests": {"t2": {"run": "PASS", "test": "PASS", "fix": "PASS"}}}
        put("evaluation/c/verified/20250329_MopenHands_M1/logs/%s/%s/evals/pr-%d/report.json" % (org, repo, pr), json.dumps(rep).encode())
    put("evaluation/mini/verified/20250329_MSWE-agent_M1/results/results.json", b"{}")   # ignored subtree
    put("evaluation/java/verified/20250426_MopenHands_M3/metadata.yaml", b"name: metadata-only\n")   # no results.json -> hazard
    # HF zips for the MSWE-agent class only (M1, M2; M3 has none), plus a MopenHands zip that must NOT be planned
    hf_rows = []

    def traj(status, n_steps, absent=False):
        info = {"model_stats": {"api_calls": n_steps}, "submission": "diff"}
        if not absent:
            info["exit_status"] = status
        return json.dumps({"environment": "swe_main", "trajectory": [{"action": "x"}] * n_steps, "history": [], "info": info}).encode()

    plan_status = {"M1": {}, "M2": {}}
    for lang in repos:
        U = universe[lang]
        for model, date in (("M1", "20250329"), ("M2", "20250514")):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for i, inst in enumerate(U):
                    if model == "M1":
                        st = ["submitted", "submitted (exit_cost)", "exit_error", "weird_status", "submitted"][i % 5]
                        if lang == "java" and i == 3:
                            continue   # missing trajectory -> ERROR
                        absent = False
                    else:
                        st = "submitted"
                        absent = (i == 0)  # exit_status absent -> UNKNOWN
                    z.writestr("%s.traj" % inst, traj(st, i + 1, absent=absent))
                    plan_status[model][(lang, inst)] = ("<absent>" if absent else st)
                if model == "M2":
                    z.writestr("orgQ__ghost-9.traj", traj("submitted", 1))   # trajectory without a checker row
            data = buf.getvalue()
            path = "%s/%s_MSWE-agent_%s.zip" % (lang, date, model)
            full = os.path.join(hf_dir, *path.split("/"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(data)
            hf_rows.append({"path": path, "size": len(data), "sha256": sha256_bytes(data)})
        hf_rows.append({"path": "%s/20250329_MopenHands_M1.zip" % lang, "size": 10, "sha256": "0" * 64})
    hf_rows.append({"path": "mini/20250329_MSWE-agent_M1.zip", "size": 10, "sha256": "0" * 64})
    hf_rows.append({"path": "README.md", "size": 3, "sha256": None})
    gp, gt, hp, hl = pin_paths(raw_dir)
    write_json(gp, {"owner_repo": GH_OWNER_REPO, "branch": GH_BRANCH, "sha": "f" * 40, "resolved_at": "selftest", "licence": GH_LICENCE})
    write_json(gt, blobs)
    write_json(hp, {"repo_id": HF_REPO, "revision": "selftest0000", "resolved_at": "selftest", "licence": HF_LICENCE})
    write_json(hl, hf_rows)
    return {"repos": repos, "universe": universe, "fam_e": fam_e, "fam_t": fam_t, "fam_g": fam_g, "plan_status": plan_status}


def selftest():
    tmp = tempfile.mkdtemp(prefix="multiswe_selftest_")
    raw = os.path.join(tmp, "raw")
    os.makedirs(raw)
    fx = _fixture(raw)
    gh_pin, gh_blobs, hf_pin, hf_rows = load_pins(raw)
    p = plan(gh_blobs, hf_rows)
    kinds = Counter(f["kind"] for f in p["gh_files"])
    assert kinds == Counter({"results": 11, "metadata": 12, "index": 2, "report": 2, "license": 1, "index.yaml": 1}), kinds
    assert len(p["all_preds"]) == 11 and p["gh_ignored_dirs"] == Counter({"mini": 1})
    assert [f["path"] for f in p["hf_files"]] == sorted(f["path"] for f in hf_rows if "MSWE-agent" in f["path"] and not f["path"].startswith("mini")), p["hf_files"]
    assert len(p["hf_not_fetched"]) == 2 and p["hf_ignored_dirs"] == Counter({"mini": 1})
    print(describe_plan(p, gh_pin["sha"], hf_pin["revision"]))
    # partial-download refusal: hide one zip
    hidden = local_hf_path(raw, p["hf_files"][0]["path"])
    os.replace(hidden, hidden + ".hidden")
    try:
        ingest(raw, verbose=False)
        raise AssertionError("partial-download guard did not fire")
    except SystemExit as e:
        assert "partial download" in str(e), e
    os.replace(hidden + ".hidden", hidden)
    c = ingest(raw, verbose=True)
    # split rule: recomputed by hand from sha256 for every task; whole repo on one side
    for t in c.tasks.values():
        d = hashlib.sha256(("norm-v1" + "\x1f" + t["family_id"]).encode("utf-8")).digest()
        h = int.from_bytes(d[:8], "big") % 1000
        assert h == t["h"] and t["side"] == ("EVAL" if h < 300 else "GATE" if h < 400 else "TRAIN"), t
    sides = defaultdict(set)
    for t in c.tasks.values():
        sides[t["family_id"]].add(t["side"])
    assert all(len(v) == 1 for v in sides.values())
    assert sides[fx["fam_e"]] == {"EVAL"} and sides[fx["fam_t"]] == {"TRAIN"} and sides[fx["fam_g"]] == {"GATE"}
    assert len(c.tasks) == 12 and Counter(t["language"] for t in c.tasks.values()) == Counter({"c": 8, "java": 4})
    # agents: MSWE-agent M1, M2, M3 (no zip), MopenHands M1 (c), MopenHands M1@20250329 / @20250514 (java), MopenHands M2
    assert "mopenhands|m1@20250329" in c.agents and "mopenhands|m1@20250514" in c.agents and "mopenhands|m1" in c.agents, sorted(c.agents)
    assert c.agents["mswe-agent|m3"]["archives_present"] == 0 and c.agents["mswe-agent|m2"]["flagged_date_mismatch"] == 2
    assert any("batch date differs" in h for h in c.hazards) and any("same (language, scaffold, model) under 2 batch dates" in h for h in c.hazards)
    assert any("without a checker row" in h for h in c.hazards) and any("without a trajectory zip" in h for h in c.hazards)
    assert any(h.startswith("submission dir without results/results.json") and "java/20250426_MopenHands_M3" in h for h in c.hazards)
    assert "mopenhands|m3" not in c.agents
    # proxy classes planted and recovered
    for (lang, inst), st in fx["plan_status"]["M1"].items():
        e = c.episodes[(inst, "mswe-agent|m1")]
        want = {"submitted": TERMINATED, "submitted (exit_cost)": CAP_HIT, "exit_error": ERROR, "weird_status": UNKNOWN}[st]
        assert e["mswe_term_v1"] == want and e["exit_status"] == st, (inst, e)
    missing = c.episodes[(fx["universe"]["java"][3], "mswe-agent|m1")]
    assert missing["mswe_term_v1"] == ERROR and missing["exit_status"] == MISSING_TRAJ and missing["trajectory_present"] == 0
    absent = c.episodes[(fx["universe"]["c"][0], "mswe-agent|m2")]
    assert absent["mswe_term_v1"] == UNKNOWN and absent["exit_status"] == ABSENT_STATUS and absent["steps"] == 1
    m3 = c.episodes[(fx["universe"]["c"][0], "mswe-agent|m3")]
    assert m3["mswe_term_v1"] == ERROR and m3["exit_status"] == MISSING_ARCHIVE
    assert c.episodes[(fx["universe"]["c"][1], "mswe-agent|m1")]["steps"] == 2
    assert all(e["mswe_term_v1"] == UNSTAMPED for e in c.episodes.values() if e["agent"].startswith("mopenhands"))
    # checker reading and the report.json cross-check
    U = fx["universe"]["c"]
    e0, e3 = c.episodes[(U[0], "mopenhands|m1")], c.episodes[(U[3], "mopenhands|m1")]
    assert e0["report_json_present"] == 1 and e0["resolved"] == 1 and e0["resolved_mismatch"] == 0 and e0["f2p_pass"] == 1 and e0["p2p_total"] == 1
    assert e3["report_json_present"] == 1 and e3["resolved"] == 0 and e3["report_rule_resolved"] == 1 and e3["resolved_mismatch"] == 1
    em = c.episodes[(U[-1], "mswe-agent|m2")]
    assert em["checker_status"] == "empty_error_patch" and em["checker_decided"] == 0
    assert c.episodes[(U[-1], "mswe-agent|m3")]["checker_status"] == "incomplete"
    # build (write-once) and readout
    db = os.path.join(tmp, "multiswe_result_selftest.db")
    build_db(db, c)
    try:
        build_db(db, c)
        raise AssertionError("write-once guard did not fire on the DB")
    except FileExistsError:
        pass
    conn = open_ro(db)
    assert conn.execute("SELECT value FROM meta WHERE key='corpus'").fetchone()[0] == "multiswe_trajs_selftest0000"
    assert conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0] == len(c.episodes)
    assert conn.execute("SELECT COUNT(*) FROM checker WHERE output LIKE 'UNDECIDED:%'").fetchone()[0] == sum(1 for e in c.episodes.values() if not e["checker_decided"])
    assert conn.execute("SELECT COUNT(*) FROM provenance").fetchone()[0] == len(p["gh_files"]) + len(p["hf_files"])
    conn.close()
    out_txt = os.path.join(tmp, "multiswe_admission.txt")
    out_csv = os.path.join(tmp, "multiswe_admission_strata.csv")
    pool_dir = os.path.join(tmp, "pool")
    # registered thresholds: 5 EVAL instances < 120 -> C1 FAILED
    r = readout(db, out_txt, out_csv, pool_dir, verbose=False)
    assert r["c1"] is False and r["n_c1"] == 0 and r["c3"] is False and r["p"] is False and r["p1"] is False and r["p1p"] is True and r["p4"] is False
    os.remove(out_txt)
    os.remove(out_csv)
    os.remove(r["pool_path"])
    # small support so the HELD path is exercised: fam_e (5 EVAL) clears at 4
    r = readout(db, out_txt, out_csv, pool_dir, support_min=4, roster_min=3, verbose=True)
    assert r["c1"] is True and r["n_c1"] == 1 and r["strata"][0]["family_id"] == fx["fam_e"] and r["strata"][0]["n_eval"] == 5
    # complete rosters: fam_e (5 instances) has every agent (MopenHands M2 misses only the LAST c instance, which is in fam_t) -> 5;
    # fam_t (3 instances): MopenHands M2 misses it -> 4; fam_g (java, 4): the two MopenHands M1 batches + M2 misses U[-1] -> 5
    by_fam = {s["family_id"]: s for s in r["strata"]}
    assert by_fam[fx["fam_e"]]["largest_complete_roster"] == 5 and by_fam[fx["fam_t"]]["largest_complete_roster"] == 4 \
        and by_fam[fx["fam_g"]]["largest_complete_roster"] == 5 and r["c3"] is True, r["strata"]
    assert "mopenhands|m2" not in by_fam[fx["fam_t"]]["complete_roster_agents"].split(";")
    # C2 on the class: 36 episodes = 3 agents x 12 tasks. Planted ledger (status index i % 5 over the language's instances):
    #   M1 c (8): sub, cap, err, weird, sub, sub, cap, err -> T 3, CAP 2, ERR 2, UNK 1 ; M1 java (4): sub, cap, err, MISSING -> T 1, CAP 1, ERR 2
    #   M2 (12): all sub, exit_status absent on the first instance of each language -> T 10, UNK 2 ; M3 (12): no archive -> ERR 12
    cls = r["classes"]
    assert sum(cls.values()) == 36, cls
    assert cls[TERMINATED] == 14 and cls[CAP_HIT] == 3 and cls[ERROR] == 16 and cls[UNKNOWN] == 3, cls
    assert abs(r["c2_rate"] - 33 / 36) < 1e-12 and r["c2"] is False
    # D_c pooled: TERMINATED and decided: M1 c idx 0 (res), 4 (unres), 5 (unres) = 3; M1 java idx 0 (res) = 1; M2: 10 TERMINATED, of which
    # c idx 7 and java idx 3 are empty_error_patch (undecided) -> 8 ; total 12 / 36
    assert r["dc_num"] == 12 and r["dc_den"] == 36, (r["dc_num"], r["dc_den"])
    lo, hi = wilson(12, 36)
    assert 0.20 < lo < 0.3334 < hi < 0.50
    # pool id equals pool_guard's function (imported here only; it opens no DB at import)
    import pool_guard  # noqa: E402
    assert pool_guard.compute_pool_id(r["ids_by_key"]) == r["pool_id"], (pool_guard.compute_pool_id(r["ids_by_key"]), r["pool_id"])
    assert list(r["ids_by_key"]) == ["MULTISWE/c/orgX__%s" % fx["fam_e"].split("/")[1]] and r["ids_by_key"][list(r["ids_by_key"])[0]] == [11, 12, 13, 14, 15]
    with open(r["pool_path"], encoding="utf-8") as f:
        assert json.load(f) == r["ids_by_key"]
    with open(out_csv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3 and rows[0]["side"] == "EVAL" and rows[0]["n_eval"] == "5"
    for hide in (None, out_txt, out_csv):   # the guard fires on the txt, then on the csv, then on the pool file
        if hide:
            os.replace(hide, hide + ".hidden")
        try:
            readout(db, out_txt, out_csv, pool_dir, support_min=4, verbose=False)
            raise AssertionError("write-once guard did not fire (hidden: %s)" % hide)
        except FileExistsError:
            pass
    for hide in (out_txt, out_csv):
        os.replace(hide + ".hidden", hide)
    with open(out_txt, encoding="utf-8") as f:
        txt = f.read()
    assert "<exit_status absent>                     -> UNKNOWN" in txt and "<no archive for agent>                   -> ERROR" in txt
    for st, n in r["enum"].items():
        assert Counter(e["mswe_term_v1"] for e in c.episodes.values() if e["exit_status"] == st) == Counter({status_class(st): n}), st
    assert "C1: HELD" in txt and "C2: FAILED" in txt and "C3: HELD" in txt and "P: FAILED" in txt and "FALSIFIER: C2 FAILED" in txt
    # dry-run parse writes nothing new under raw
    before = sorted(os.path.join(dp, fn) for dp, _, fns in os.walk(raw) for fn in fns)
    ingest(raw, verbose=False)
    after = sorted(os.path.join(dp, fn) for dp, _, fns in os.walk(raw) for fn in fns)
    assert before == after
    print("selftest OK: 12 tasks / 3 repos on EVAL, TRAIN, GATE (hand-recomputed h); 7 agents incl. multi-batch and archive-less flags; "
          "36 MSWE-agent-class episodes with TERMINATED / CAP_HIT / ERROR / UNKNOWN planted and recovered (C2 33/36 FAILED); "
          "D_c 12/36; C1 FAILED at 120 and HELD at 4; C3 rosters 5 / 4 / 5; report.json mismatch counted; pool id == pool_guard; "
          "write-once (DB, txt, csv, pool) and partial-download guards fire; dry-run writes nothing. tmp=%s (removed)" % tmp)
    shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=DATE)
    ap.add_argument("--raw-dir", default=None)
    ap.add_argument("--db", default=None)
    ap.add_argument("--outcome", default=None, help="the write-once outcome txt (the csv sits beside it)")
    ap.add_argument("--pool-dir", default=os.path.join(ROOT, "experiment_configs"))
    ap.add_argument("--fetch", "--download", action="store_true", dest="fetch", help="resumable sha-verified download; with --dry-run: list only")
    ap.add_argument("--dry-run", action="store_true", help="parse and print; write nothing (with --fetch: list what would be fetched)")
    ap.add_argument("--ingest", "--build", action="store_true", dest="ingest", help="write the DB (write-once)")
    ap.add_argument("--readout", action="store_true", help="write the outcome, the strata csv and the EVAL pool file (write-once)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    raw_dir = a.raw_dir or default_raw_dir(a.date)
    db = a.db or default_db(a.date)
    out_txt = a.outcome or default_outcome()
    out_csv = out_txt[:-4] + "_strata.csv" if out_txt.endswith(".txt") else out_txt + "_strata.csv"
    if a.selftest:
        print("corpus=%s" % corpus_name("selftest"))
        print("script_sha=%s (LF)" % script_sha())
        selftest()
        return 0
    if a.fetch and a.dry_run:
        gh_sha, gh_blobs, hf_rev, hf_rows, pinned = resolve_pins(raw_dir, write=False)
        print("corpus=%s" % corpus_name(hf_rev))
        print("script_sha=%s (LF)" % script_sha())
        print("raw_dir=%s (pins %s)" % (raw_dir, "reused from the raw dir" if pinned else "NOT written: dry-run"))
        print(describe_plan(plan(gh_blobs, hf_rows), gh_sha, hf_rev))
        print("dry-run: nothing downloaded, nothing written")
        return 0
    if not (a.fetch or a.dry_run or a.ingest or a.readout):
        ap.error("one of --fetch [--dry-run] / --dry-run / --ingest / --readout / --selftest")
    hp = pin_paths(raw_dir)[2]
    rev = None
    if os.path.exists(hp):
        with open(hp, encoding="utf-8") as f:
            rev = json.load(f)["revision"]
    print("corpus=%s" % corpus_name(rev))
    print("script_sha=%s (LF)" % script_sha())
    print("raw_dir=%s db=%s" % (raw_dir, db))
    if a.fetch:
        fetch(raw_dir)
    if a.dry_run or a.ingest:
        c = ingest(raw_dir, verbose=True)
        if a.dry_run and not a.ingest:
            print("dry-run: nothing written")
        if a.ingest:
            out = build_db(db, c)
            print("built %s (%.1f MB)" % (out, os.path.getsize(out) / 1e6))
    if a.readout:
        r = readout(db, out_txt, out_csv, a.pool_dir, verbose=True)
        print("wrote %s, %s and %s" % (out_txt, out_csv, r["pool_path"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
