"""JUDGEBENCH-REASONING-SIDE ingest (docs/judge_v2_program.md, "## Registered 2026-09-25 (before any code or call; zero calls)
- JUDGEBENCH-REASONING-SIDE", registration commit 6134573, section L17330-L17533, verbatim L17335-L17498; the INGEST paragraph
and HYGIENE (b)). ZERO LLM calls.

WHAT IT WRITES
  judgebench_corpus_v1.db at the REPO ROOT (ignored by .gitignore L58 `*.db`, sidecars by L59 `*.db-*`; L145 re-includes only
  experiment_results/**/*.db; checked with `git check-ignore -v`). WRITE-ONCE: refused when the path exists. No wall-clock
  value is written into the DB. Tables:
    meta(key PK, value)            source repo / revision / file names / file sha256 + bytes / side export pin / rules
    pairs(pair_id PK, split, source, category, original_id, question, response_A, response_B, label, response_model,
          row_sha256, stem_key, side_v2, side_key_kind, len_A, len_B)
      split       'gpt' (data/gpt-00000-of-00001.jsonl, 350 rows) or 'claude' (data/claude-00000-of-00001.jsonl, 270 rows)
      category    knowledge (source mmlu-pro-*), reasoning (livebench-reasoning), math (livebench-math), coding (livecodebench)
      original_id the JSON rendering of the source row's original_id (it is an int for MMLU-Pro and null / text elsewhere)
      row_sha256  sha256 of the source line's bytes as served (without its LF)
      stem_key    split_side.stem_key of the side key text (below)
      side_v2     EVAL / GATE / TRAIN when "i:" + stem_key is a row of the COMMITTED side export of the split of record
                  (data_v2/manifests/REG_ARCHV2-SPLIT-2_2929bd46..._side.tsv, table_sha 75b4662e..., 20,544 rows), else
                  NOT_IN_SPLIT. EVERY row carries it (HYGIENE (c): "every knowledge row carries its side label").
      side_key_kind  the key text: knowledge = the text before the first "\\n(A) " (the specialist's rule, HYGIENE (b2));
                  other rows = the whole question, then its first paragraph (text before the first blank line); the first
                  that hits wins; 'none' when neither hits.
  experiment_results/judgebench_side/ingest_manifest.json (committed; not ignored), WRITE-ONCE, by --write-manifest: the
  source revisions, file sha256s and bytes, the DB's file sha256 and per-table sha256, row / category / label / side counts,
  the owed checks' results (--owed-checks) and the code pins (blob + sha256-lf16, rule 8).

RULES
  - Sources fetched by the PINNED revision URL; any sha256 or byte-count mismatch REFUSES (C0 (a)).
  - The source DBs of the owed checks are opened read-only and immutable after a sidecar check (pool_guard.open_ro); the
    SPLIT-2 eval_view ONLY through data_v2.views.open_eval (via archv2_pilot.common.open_view, stage 'judge').
  - The owed checks print counts and JudgeBench pair_ids only, never a pool text.
  - This corpus DB and both verdict caches are EXCLUDED inputs for any construction, labelling, induction, rubric fit,
    selection or policy fit (HYGIENE (c)); the knowledge rows are "mixed-side, disclosed" (rule 12).

OWED AT INGEST (INGEST (i)-(iii); one pass under rule 7 W1-W5; counts only; none gates the run or removes a pair):
  (i)   8-token runs (judge_v2.induction._tokens: \\w+ casefolded, k = 8) of the 350 GPT-split questions against the corpus
        texts of mmlu-pro-v2 (mmlu_pro_dataset_cache_v2.db, table mmlu_pro: question + options) and mc6
        (multicorpus_cache_v1.db, table corpus_questions: text + options, per source), and against the INDUCE-1
        (ef9c9e87...) / INDUCE-2 (ace41ede...) rubric texts; a planted positive control per corpus must fire;
  (ii)  pool membership of the GPT-split EVAL knowledge items in pv2_41dbd3dbcd399df0 (the eval_view's EVAL items of
        mmlu-pro-v2) and, as the converse, that no GATE / TRAIN item is in it;
  (iii) the OPTIONS-key map (never question_text; boundary_disagreement.okey) of the knowledge items to eval_results
        question ids, the legacy pool p2dca21ab5f4ef3ae (pool_guard.eval_ids) and the board of record's judged questions
        (distinct valid qid of stack_v2_promptv2_x12all.db).
  W1-W5 (CONTEXT section 4 rule 7, standing form): the pass prints a process census and REFUSES on a foreign
  tools/analysis / tools/chains / pool_guard / Gradle / java process (a --selftest process is admitted); an exclusive-open
  probe (CreateFileW, share mode 0) must show every DB it reads FREE; >= 12 GB free RAM; the admitted PIDs and the wall
  time are printed.

LAUNCH SEQUENCE
  python tools/ingest/judgebench_ingest.py --selftest                       # synthetic rows, temp dirs; no network, no DB of record
  python tools/ingest/judgebench_ingest.py --fetch --raw-dir <dir>          # download by the pinned revision, verify sha256
  python tools/ingest/judgebench_ingest.py --build --raw-dir <dir>          # write judgebench_corpus_v1.db (write-once)
  python tools/ingest/judgebench_ingest.py --owed-checks --data-root <main checkout> --owed-json <scratch file>
  python tools/ingest/judgebench_ingest.py --write-manifest --owed-json <scratch file>
"""
import argparse
import ctypes
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ANALYSIS = os.path.join(ROOT, "tools", "analysis")
if ANALYSIS not in sys.path:
    sys.path.insert(0, ANALYSIS)
import split_side  # noqa: E402

TEST = "JUDGEBENCH-REASONING-SIDE"
HF_REPO = "ScalerLab/JudgeBench"
HF_REVISION = "57dd5e0b9817d07f05ec8f45a91b2ce1e310e308"
SOURCES = {  # split -> (path in the repo, bytes, sha256 of the file bytes as served)  -- the registration's pins
    "gpt": ("data/gpt-00000-of-00001.jsonl", 1960188, "d5106306b38dead1b2e964ecf5534a3e7b2fc4b8d3b8da327599edfcebd76042"),
    "claude": ("data/claude-00000-of-00001.jsonl", 920039, "3b70504588e400613bf5744a20a345da8701b7150be9a30c9db0e6f3d7b70a62"),
}
EXPECT_ROWS = {"gpt": 350, "claude": 270}
EXPECT_GPT_CATEGORIES = {"knowledge": 154, "reasoning": 98, "math": 56, "coding": 42}
DB_NAME = "judgebench_corpus_v1.db"
MANIFEST_REL = os.path.join("experiment_results", "judgebench_side", "ingest_manifest.json")
SIDE_EXPORT_REL = os.path.join("data_v2", "manifests", "REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2_side.tsv")
SIDE_EXPORT_TABLE_SHA = "75b4662eacf9adeb3aa44046e99c61712952668dd489a4933148fe9c5951117b"
SIDE_EXPORT_ROWS = 20544
SIDES = ("EVAL", "GATE", "TRAIN")
NOT_IN_SPLIT = "NOT_IN_SPLIT"
LEGACY_POOL = "p2dca21ab5f4ef3ae"
V2_POOL = "pv2_41dbd3dbcd399df0"
INDUCE_RUBRICS = {  # name -> (committed artefact, sha256 of the UTF-8 rubric text)
    "ARCH-V2-INDUCE-RUBRIC-1": (os.path.join("experiment_results", "archv2", "induce_rubric_1", "rubric_mcq_ARCH-V2-INDUCE-RUBRIC-1.json"),
                                "ef9c9e8759147960dedff70c3b86fe9f6b8b9caad8ddc39fb0fdc1c253e0eb07"),
    "ARCH-V2-INDUCE-RUBRIC-2": (os.path.join("experiment_results", "archv2", "induce_rubric_2", "rubric_mcq_ARCH-V2-INDUCE-RUBRIC-2.json"),
                                "ace41ede9b19974aaa6c29881aff2e17dae353c0ce05f5d0e246bd3edf2a49e0"),
}
EXCLUDED_MODEL = "Meta-Llama-3-70B-Instruct"
SHINGLE = 8
MIN_FREE_RAM_GB = 12.0
CODE_FILES = ("tools/ingest/judgebench_ingest.py", "tools/analysis/split_side.py")
KNOWLEDGE_SUFFIX = "\nIf you cannot determine the correct multiple-choice answer"


def refuse(msg):
    raise SystemExit("[JB-INGEST] " + msg)


def need(cond, msg):
    if not cond:
        refuse(msg)


# ── pins ────────────────────────────────────────────────────────────────────────────────────────

def _lf_bytes(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def git_blob_lf(path):
    d = _lf_bytes(path)
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def pins(rel):
    p = os.path.join(ROOT, rel)
    raw = open(p, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    out = {"blob": git_blob_lf(p), "sha256-lf16": hashlib.sha256(lf).hexdigest()[:16]}
    if raw != lf:
        out["sha256-crlf16"] = hashlib.sha256(raw).hexdigest()[:16]
    return out


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ── fetch ───────────────────────────────────────────────────────────────────────────────────────

def url_of(split):
    return "https://huggingface.co/datasets/%s/resolve/%s/%s" % (HF_REPO, HF_REVISION, SOURCES[split][0])


def verify_bytes(split, data):
    _, n, sha = SOURCES[split]
    got = hashlib.sha256(data).hexdigest()
    need(len(data) == n and got == sha, "%s: %d bytes sha256 %s; the registration pins %d bytes sha256 %s (C0 (a)); REFUSED"
         % (SOURCES[split][0], len(data), got, n, sha))
    return got


def fetch(raw_dir):
    os.makedirs(raw_dir, exist_ok=True)
    for split in SOURCES:
        with urllib.request.urlopen(url_of(split), timeout=120) as r:
            data = r.read()
        verify_bytes(split, data)
        p = os.path.join(raw_dir, os.path.basename(SOURCES[split][0]))
        if os.path.exists(p):
            need(open(p, "rb").read() == data, "%s exists with other bytes; refused" % p)
        else:
            with open(p, "xb") as f:
                f.write(data)
        print("[JB-INGEST] fetched %s @ %s: %d bytes, sha256 %s (= the pin) -> %s"
              % (SOURCES[split][0], HF_REVISION[:8], len(data), SOURCES[split][2], p))


def read_raw(raw_dir):
    out = {}
    for split in SOURCES:
        p = os.path.join(raw_dir, os.path.basename(SOURCES[split][0]))
        need(os.path.isfile(p), "%s is absent: run --fetch first" % p)
        data = open(p, "rb").read()
        verify_bytes(split, data)
        out[split] = data
    return out


# ── rows ────────────────────────────────────────────────────────────────────────────────────────

def category_of(source):
    if source.startswith("mmlu-pro-"):
        return "knowledge"
    return {"livebench-reasoning": "reasoning", "livebench-math": "math", "livecodebench": "coding"}.get(source) or \
        refuse("unknown source %r" % source)


def knowledge_stem(question):
    i = question.find("\n(A) ")
    need(i > 0, "a knowledge question carries no '\\n(A) ' marker")
    return question[:i]


def knowledge_options(question):
    """The option texts in letter order: the segments between the '\\n(X) ' markers, the last one ending at the answer-format
    suffix. Refuses on a gap in the letters."""
    i = question.find("\n(A) ")
    j = question.find(KNOWLEDGE_SUFFIX, i)
    need(i > 0 and j > i, "a knowledge question lacks its option block or its answer-format suffix")
    block = question[i:j]
    marks = list(re.finditer(r"\n\(([A-Z])\) ", block))
    letters = [m.group(1) for m in marks]
    need(letters == [chr(ord("A") + k) for k in range(len(letters))] and len(letters) >= 2,
         "option letters %s are not consecutive from A" % letters)
    opts = []
    for k, m in enumerate(marks):
        end = marks[k + 1].start() if k + 1 < len(marks) else len(block)
        opts.append(block[m.end():end])
    return opts


def okey_list(options):
    """boundary_disagreement.okey applied to a parsed list: the JSON option list, each option whitespace-stripped."""
    return json.dumps([str(x).strip() for x in options])


def okey(o):
    """OPTIONS key: the JSON option list with each option whitespace-stripped (boundary_disagreement.okey; the join key of
    record). Local copy; the selftest asserts its AST equals boundary_disagreement.okey's."""
    try:
        v = json.loads(o)
        if isinstance(v, list):
            return json.dumps([str(x).strip() for x in v])
    except Exception:
        pass
    return (o or "").strip()


def first_paragraph(text):
    i = text.find("\n\n")
    return text if i < 0 else text[:i]


def load_side_export(root=ROOT):
    p = os.path.join(root, SIDE_EXPORT_REL)
    lines = open(p, encoding="utf-8").read().split("\n")
    head = lines[0]
    need(("table_sha=%s" % SIDE_EXPORT_TABLE_SHA) in head and ("rows=%d" % SIDE_EXPORT_ROWS) in head,
         "the side export header %r is not the split of record's" % head[:160])
    cols = lines[1].split("\t")
    need(cols[:3] == ["item_id", "component_id", "side"], "side export columns %r" % cols)
    side = {}
    for ln in lines[2:]:
        if not ln.strip():
            continue
        f = ln.split("\t")
        need(f[2] in SIDES, "side %r" % f[2])
        side[f[0]] = f[2]
    need(len(side) == SIDE_EXPORT_ROWS, "side export carries %d rows, not %d" % (len(side), SIDE_EXPORT_ROWS))
    return side, head


def side_of(row, side_map):
    """(stem_key, side, kind) of one row (module docstring)."""
    q = row["question"]
    if row["category"] == "knowledge":
        cands = [("stem_before_A", knowledge_stem(q))]
    else:
        cands = [("whole", q), ("first_para", first_paragraph(q))]
    first_key = None
    for kind, text in cands:
        k = split_side.stem_key(text)
        first_key = first_key or k
        s = side_map.get("i:" + k)
        if s:
            return k, s, kind
    return first_key, NOT_IN_SPLIT, "none"


def parse_rows(split, data):
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines = lines[:-1]
    rows = []
    for ln in lines:
        r = json.loads(ln.decode("utf-8"))
        need(set(r) == {"pair_id", "original_id", "source", "question", "response_model", "response_A", "response_B", "label"},
             "unexpected keys %s" % sorted(r))
        need(r["label"] in ("A>B", "B>A"), "label %r (no ties are expected)" % r["label"])
        r["split"] = split
        r["category"] = category_of(r["source"])
        r["row_sha256"] = hashlib.sha256(ln).hexdigest()
        rows.append(r)
    need(len(rows) == EXPECT_ROWS[split], "%s: %d rows, not %d" % (split, len(rows), EXPECT_ROWS[split]))
    need(len({r["pair_id"] for r in rows}) == len(rows), "%s: duplicate pair_id" % split)
    return rows


PAIRS_DDL = """CREATE TABLE pairs (pair_id TEXT PRIMARY KEY, split TEXT NOT NULL, source TEXT NOT NULL, category TEXT NOT NULL,
    original_id TEXT NOT NULL, question TEXT NOT NULL, response_A TEXT NOT NULL, response_B TEXT NOT NULL, label TEXT NOT NULL,
    response_model TEXT NOT NULL, row_sha256 TEXT NOT NULL, stem_key TEXT NOT NULL, side_v2 TEXT NOT NULL,
    side_key_kind TEXT NOT NULL, len_A INTEGER NOT NULL, len_B INTEGER NOT NULL)"""
PAIR_COLS = ("pair_id", "split", "source", "category", "original_id", "question", "response_A", "response_B", "label",
             "response_model", "row_sha256", "stem_key", "side_v2", "side_key_kind", "len_A", "len_B")


def table_sha(conn, table, order):
    """sha256 over repr(row) + LF per row, ORDER BY the key (the twenty_newsgroups_ingest convention)."""
    h = hashlib.sha256()
    n = 0
    for row in conn.execute("SELECT * FROM %s ORDER BY %s" % (table, order)):
        h.update((repr(row) + "\n").encode("utf-8"))
        n += 1
    return h.hexdigest(), n


def build(raw, out_path, side_map, side_head):
    """Write the corpus DB (write-once). Returns the facts for the manifest."""
    need(not os.path.exists(out_path), "%s exists; the corpus DB is write-once. Refused." % out_path)
    for suf in ("-journal", "-wal", "-shm"):
        need(not os.path.exists(out_path + suf), "%s%s exists; refused" % (out_path, suf))
    rows = []
    for split in ("gpt", "claude"):
        rows.extend(parse_rows(split, raw[split]))
    need(len({r["pair_id"] for r in rows}) == len(rows), "a pair_id occurs in both splits")
    for r in rows:
        for tok in ("$query", "$traceA", "$traceB"):
            need(tok not in r["question"] and tok not in r["response_A"] and tok not in r["response_B"],
                 "pair %s carries the template token %s (build_user_prompt would substitute into it)" % (r["pair_id"], tok))
        r["stem_key"], r["side_v2"], r["side_key_kind"] = side_of(r, side_map)
        r["original_id"] = json.dumps(r["original_id"])
        r["len_A"], r["len_B"] = len(r["response_A"]), len(r["response_B"])
    rows.sort(key=lambda r: r["pair_id"])
    conn = sqlite3.connect(out_path)
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute(PAIRS_DDL)
        meta = {"test": TEST, "schema": "judgebench-corpus-v1", "hf_repo": HF_REPO, "hf_revision": HF_REVISION,
                "side_export": SIDE_EXPORT_REL.replace(os.sep, "/"), "side_export_header": side_head,
                "side_rule": "knowledge: split_side.stem_key(text before the first '\\n(A) '); other: whole question, then"
                             " first paragraph; 'i:' + key looked up in the side export; NOT_IN_SPLIT when absent",
                "normaliser_version": split_side.NORMALISER_VERSION,
                "excluded_inputs": "EXCLUDED input for any construction, labelling, induction, rubric fit, selection or policy"
                                   " fit (HYGIENE (c)); knowledge rows are mixed-side, disclosed (rule 12)"}
        for split, (path, n, sha) in SOURCES.items():
            meta["source_%s_path" % split] = path
            meta["source_%s_bytes" % split] = str(n)
            meta["source_%s_sha256" % split] = sha
        conn.executemany("INSERT INTO meta VALUES (?, ?)", sorted(meta.items()))
        conn.executemany("INSERT INTO pairs VALUES (%s)" % ",".join("?" * len(PAIR_COLS)),
                         [tuple(r[c] for c in PAIR_COLS) for r in rows])
        conn.commit()
    finally:
        conn.close()
    return describe(out_path)


def open_corpus_ro(path):
    need(os.path.isfile(path), "%s not found" % path)
    for suf in ("-journal", "-wal"):
        need(not (os.path.exists(path + suf) and os.path.getsize(path + suf) > 0), "%s%s is non-empty; refused" % (path, suf))
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % os.path.abspath(path).replace("\\", "/"), uri=True)


def describe(path):
    conn = open_corpus_ro(path)
    try:
        t_pairs = table_sha(conn, "pairs", "pair_id")
        t_meta = table_sha(conn, "meta", "key")
        facts = {"file": os.path.basename(path), "file_sha256": file_sha256(path), "bytes": os.path.getsize(path),
                 "sqlite_version": sqlite3.sqlite_version,
                 "tables": {"pairs": {"rows": t_pairs[1], "table_sha256": t_pairs[0]},
                            "meta": {"rows": t_meta[1], "table_sha256": t_meta[0]}}}
        counts = {}
        for split in ("gpt", "claude"):
            c = {"rows": conn.execute("SELECT COUNT(*) FROM pairs WHERE split=?", (split,)).fetchone()[0],
                 "unique_questions": conn.execute("SELECT COUNT(DISTINCT question) FROM pairs WHERE split=?", (split,)).fetchone()[0],
                 "category": dict(conn.execute("SELECT category, COUNT(*) FROM pairs WHERE split=? GROUP BY category", (split,))),
                 "label": dict(conn.execute("SELECT label, COUNT(*) FROM pairs WHERE split=? GROUP BY label", (split,))),
                 "response_model": dict(conn.execute("SELECT response_model, COUNT(*) FROM pairs WHERE split=? GROUP BY"
                                                     " response_model", (split,))),
                 "side_v2_by_category": {}}
            for cat, side, kind, n in conn.execute("SELECT category, side_v2, side_key_kind, COUNT(*) FROM pairs WHERE split=?"
                                                   " GROUP BY category, side_v2, side_key_kind", (split,)):
                c["side_v2_by_category"].setdefault(cat, {})["%s (%s)" % (side, kind)] = n
            lg = conn.execute("SELECT category, SUM(CASE WHEN (label='A>B' AND len_A>len_B) OR (label='B>A' AND len_B>len_A)"
                              " THEN 1 ELSE 0 END), COUNT(*) FROM pairs WHERE split=? GROUP BY category", (split,)).fetchall()
            c["longer_is_correct"] = {cat: "%d / %d = %.3f" % (a, n, a / n) for cat, a, n in lg}
            tot_a = sum(a for _, a, _ in lg)
            c["longer_is_correct"]["all"] = "%d / %d = %.3f" % (tot_a, c["rows"], tot_a / max(1, c["rows"]))
            counts[split] = c
        facts["counts"] = counts
        shared = conn.execute("SELECT COUNT(*) FROM (SELECT question FROM pairs WHERE split='gpt' INTERSECT SELECT question"
                              " FROM pairs WHERE split='claude')").fetchone()[0]
        facts["questions_in_both_splits"] = shared
        facts["meta"] = dict(conn.execute("SELECT key, value FROM meta"))
    finally:
        conn.close()
    return facts


def check_facts(facts):
    g = facts["counts"]["gpt"]
    need(g["rows"] == 350 and g["unique_questions"] == 350, "GPT split: %d rows / %d unique questions" % (g["rows"], g["unique_questions"]))
    need(g["category"] == EXPECT_GPT_CATEGORIES, "GPT split categories %s" % g["category"])
    need(g["response_model"] == {"gpt-4o-2024-05-13": 350}, "GPT split response models %s" % g["response_model"])


# ── the owed checks (rule 7 W1-W5) ─────────────────────────────────────────────────────────────────

def process_census():
    """(admitted, foreign): python / java / gradle processes other than this one."""
    ps = subprocess.run(["powershell", "-NoProfile", "-Command",
                         "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|java|gradle' } | "
                         "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json"],
                        capture_output=True, text=True, timeout=120).stdout.strip()
    procs = json.loads(ps) if ps else []
    if isinstance(procs, dict):
        procs = [procs]
    me, parent = os.getpid(), os.getppid()
    admitted, foreign = [], []
    for p in procs:
        pid, cmd = p["ProcessId"], (p.get("CommandLine") or "")
        if pid in (me, parent) or "judgebench_ingest.py" in cmd:
            continue
        c = cmd.replace("\\", "/").lower()
        bad = (("tools/analysis" in c or "tools/chains" in c or "pool_guard" in c) and "--selftest" not in c) or \
            "gradle" in c or p.get("Name", "").lower().startswith("java")
        (foreign if bad else admitted).append((pid, p.get("Name"), cmd[:160]))
    return admitted, foreign


def exclusive_probe(path):
    """FREE when CreateFileW(GENERIC_READ, share 0) succeeds (no other handle is open on the file), BUSY on a sharing
    violation. The handle is closed at once; nothing is written."""
    if os.name != "nt":
        return "UNPROBED (not Windows)"
    k32 = ctypes.windll.kernel32
    k32.CreateFileW.restype = ctypes.c_void_p
    h = k32.CreateFileW(ctypes.c_wchar_p(os.path.abspath(path)), 0x80000000, 0, None, 3, 0x80, None)
    if h is None or h == ctypes.c_void_p(-1).value:
        err = k32.GetLastError()
        return "BUSY (sharing violation)" if err == 32 else "ERROR %d" % err
    k32.CloseHandle(ctypes.c_void_p(h))
    return "FREE"


def free_ram_gb():
    out = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                         capture_output=True, text=True, timeout=60).stdout.strip()
    return int(out) / 1024.0 / 1024.0


def shingles(text, k=SHINGLE):
    t = re.findall(r"\w+", text.casefold())       # judge_v2.induction._tokens (the selftest asserts equality)
    return {" ".join(t[i:i + k]) for i in range(len(t) - k + 1)}


class OverlapIndex:
    """The probe side (JudgeBench questions) held as shingle -> pair ids; corpus texts are STREAMED through hits()."""

    def __init__(self, probes):
        self.by_sh = defaultdict(set)
        for pid, text in probes:
            for s in shingles(text):
                self.by_sh[s].add(pid)

    def hits(self, text):
        out = defaultdict(int)
        for s in shingles(text):
            for pid in self.by_sh.get(s, ()):
                out[pid] += 1
        return out


def overlap_pass(gpt_rows, sources, out=print):
    """sources: {name: iterable of texts}. Returns {name: {pair_id: n shingles hit}} with a planted positive control per
    source (the control's id is 'CONTROL:<name>'; its text = the source's first text of >= 8 tokens)."""
    probes = [(r["pair_id"], r["question"]) for r in gpt_rows]
    controls = {}
    res = {}
    for name, texts in sources.items():
        texts = list(texts)
        ctrl = next((t for t in texts if len(shingles(t)) > 0), None)
        need(ctrl is not None, "source %s has no text of >= 8 tokens: the positive control cannot be planted" % name)
        controls[name] = ctrl
    idx = OverlapIndex(probes + [("CONTROL:%s" % n, t) for n, t in controls.items()])
    for name, texts in sources.items():
        agg = defaultdict(int)
        n_texts = 0
        for t in texts:
            n_texts += 1
            for pid, n in idx.hits(t).items():
                agg[pid] = max(agg[pid], n)
        res[name] = {"n_texts": n_texts, "hits": dict(agg)}
        need(agg.get("CONTROL:%s" % name, 0) > 0, "the positive control of %s did NOT fire: the overlap check is void" % name)
    return res


def owed_checks(data_root, corpus_path, out=print):
    t0 = time.time()
    import pool_guard
    from archv2_pilot import common as apc
    mm_db = os.path.join(data_root, "mmlu_pro_dataset_cache_v2.db")
    mc_db = os.path.join(data_root, "multicorpus_cache_v1.db")
    x12_db = os.path.join(data_root, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x12all.db")
    view = os.path.join(data_root, apc.EVAL_VIEW_REL)
    reads = [corpus_path, mm_db, mc_db, x12_db, view]
    # W1-W5
    admitted, foreign = process_census()
    out("[W2] process census: admitted %s" % ([a[0] for a in admitted] or "none"))
    for a in admitted:
        out("       admitted pid %s %s %s" % a)
    for f in foreign:
        out("       FOREIGN pid %s %s %s" % f)
    need(not foreign, "foreign process(es) %s: rule 7 W1-W5 refuses the pass (a failed precondition)" % [f[0] for f in foreign])
    probes = {p: exclusive_probe(p) for p in reads}
    for p, s in probes.items():
        out("[W1] exclusive-open probe %s: %s" % (p, s))
    need(all(s == "FREE" for s in probes.values()), "a DB the pass reads is not FREE; refused")
    ram = free_ram_gb()
    out("[W3] free RAM %.1f GB (>= %.0f GB required)" % (ram, MIN_FREE_RAM_GB))
    need(ram >= MIN_FREE_RAM_GB, "free RAM below %.0f GB" % MIN_FREE_RAM_GB)

    res = {"reads": {os.path.relpath(p, data_root).replace(os.sep, "/") if p != corpus_path else os.path.basename(p): None
                     for p in reads},
           "w1_w5": {"admitted_pids": [a[0] for a in admitted], "probes": {os.path.basename(p): s for p, s in probes.items()},
                     "free_ram_gb": round(ram, 1)}}
    conn = open_corpus_ro(corpus_path)
    cols = ("pair_id", "category", "question", "side_v2", "stem_key", "split")
    rows = [dict(zip(cols, r)) for r in conn.execute("SELECT %s FROM pairs ORDER BY pair_id" % ", ".join(cols))]
    conn.close()
    gpt = [r for r in rows if r["split"] == "gpt"]
    need(len(gpt) == 350, "corpus DB: %d GPT rows" % len(gpt))

    # pool of record first (the CONTEXT convention), then (iii) the OPTIONS-key map
    out("[POOL] %s" % pool_guard.assert_pool_of_record(LEGACY_POOL))
    p2dca = pool_guard.eval_ids(LEGACY_POOL)
    ev = pool_guard.open_ro(mm_db)
    try:
        res["reads"]["mmlu_pro_dataset_cache_v2.db"] = file_sha256(mm_db)
        okey2eval = defaultdict(set)
        for q, o in ev.execute("SELECT DISTINCT question_id, options_json FROM eval_results WHERE model_name != ?",
                               (EXCLUDED_MODEL,)):
            okey2eval[okey(o)].add(q)
        okey2mm = defaultdict(set)
        mm_texts = []
        for i, t, o in ev.execute("SELECT id, question, options FROM mmlu_pro ORDER BY id"):
            okey2mm[okey(o)].add(i)
            mm_texts.append(t or "")
            try:
                mm_texts.extend(str(x) for x in (json.loads(o) or []))
            except Exception:
                pass
    finally:
        ev.close()
    x12 = pool_guard.open_ro(x12_db)
    try:
        res["reads"]["experiment_results/x12_crossdomain/stack_v2_promptv2_x12all.db"] = file_sha256(x12_db)
        xc = [r[1] for r in x12.execute("PRAGMA table_info(verdicts)")]
        need("qid" in xc, "x12all verdicts carries no qid column: %s" % xc)
        where = " WHERE invalid = 0" if "invalid" in xc else ""
        board = {r[0] for r in x12.execute("SELECT DISTINCT qid FROM verdicts%s" % where) if r[0] is not None}
    finally:
        x12.close()
    omap = {}
    for split in ("gpt", "claude"):
        ks = [r for r in rows if r["split"] == split and r["category"] == "knowledge"]
        if split == "gpt":
            need(len(ks) == 154, "GPT knowledge rows %d" % len(ks))
        d = Counter()
        board_ids = []
        for r in ks:
            k = okey_list(knowledge_options(r["question"]))
            eids, mids = okey2eval.get(k, set()), okey2mm.get(k, set())
            d["keyed_eval"] += bool(eids)
            d["keyed_eval_ambiguous(>1 id)"] += len(eids) > 1
            d["keyed_mmlu_pro_row"] += bool(mids)
            d["in_p2dca_judgeable"] += bool(eids & p2dca)
            inb = bool(eids & board)
            d["board_of_record_judged"] += inb
            if inb:
                board_ids.append(r["pair_id"])
            d["in_p2dca_by_side[%s]" % r["side_v2"]] += bool(eids & p2dca)
            d["board_by_side[%s]" % r["side_v2"]] += inb
        omap[split] = {"knowledge_rows": len(ks), "counts": dict(sorted(d.items())), "board_pair_ids": sorted(board_ids)}
    res["iii_options_key_map"] = {"pool": LEGACY_POOL, "p2dca_judgeable_ids": len(p2dca),
                                  "board_of_record_judged_qids(x12all distinct valid qid)": len(board),
                                  "key": "boundary_disagreement.okey (JSON option list, whitespace-stripped); never question_text",
                                  "excluded_model": EXCLUDED_MODEL, "splits": omap}

    # (ii) pool membership through the sealed eval_view
    vconn, vsha, _meta = apc.open_view("judge", view, apc.EVAL_VIEW_SHA256, out=out)
    try:
        pool = apc.pool_of(vconn, apc.CV_MMLU, V2_POOL)
        items = apc.eval_items(vconn, apc.CV_MMLU)
        need(len(items) == pool["n_items"], "eval_view items %d != pool n_items %d" % (len(items), pool["n_items"]))
    finally:
        vconn.close()
    res["reads"][apc.EVAL_VIEW_REL.replace(os.sep, "/")] = vsha
    mem = {}
    for split in ("gpt", "claude"):
        ks = [r for r in rows if r["split"] == split and r["category"] == "knowledge"]
        c = Counter()
        odd = []
        for r in ks:
            inp = ("i:" + r["stem_key"]) in items
            c["%s in_pool=%s" % (r["side_v2"], inp)] += 1
            if inp != (r["side_v2"] == "EVAL"):
                odd.append(r["pair_id"])
        mem[split] = {"counts": dict(sorted(c.items())), "side_vs_pool_disagreements": sorted(odd)}
    res["ii_pool_membership"] = {"pool": V2_POOL, "pool_row": pool, "view_sha256": vsha, "splits": mem}

    # (i) 8-token overlap
    mc = pool_guard.open_ro(mc_db)
    try:
        res["reads"]["multicorpus_cache_v1.db"] = file_sha256(mc_db)
        mc_src = defaultdict(list)
        for src, t, o in mc.execute("SELECT source, text, options_json FROM corpus_questions ORDER BY question_id"):
            mc_src["mc6:" + str(src)].append(t or "")
            if o:
                try:
                    mc_src["mc6:" + str(src)].extend(str(x) for x in (json.loads(o) or []))
                except Exception:
                    pass
    finally:
        mc.close()
    sources = {"mmlu-pro-v2:mmlu_pro": mm_texts}
    sources.update(sorted(mc_src.items()))
    for name, (rel, sha) in INDUCE_RUBRICS.items():
        d = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
        need(hashlib.sha256(d["rubric"].encode("utf-8")).hexdigest() == sha, "%s rubric text sha256 is not %s" % (name, sha))
        sources["rubric:" + name] = [d["rubric"]]
    ov = overlap_pass(gpt, sources, out=out)
    cat = {r["pair_id"]: r["category"] for r in gpt}
    summ = {}
    for name, r in ov.items():
        by = Counter()
        nonk = []
        for pid, n in r["hits"].items():
            if pid.startswith("CONTROL:"):
                continue
            by[cat[pid]] += 1
            if cat[pid] != "knowledge":
                nonk.append((pid, n))
        summ[name] = {"texts_streamed": r["n_texts"], "gpt_questions_hit_by_category": dict(sorted(by.items())),
                      "control_fired": r["hits"].get("CONTROL:%s" % name, 0) > 0,
                      "non_knowledge_hits(pair_id, max shingles in one text)": sorted(nonk)}
    res["i_overlap_8token"] = {"rule": "judge_v2.induction._tokens (\\w+ casefolded), k = 8; probe = the 350 GPT-split questions"
                                       " verbatim (answer-format suffix included); a question counts as hit when any 8-token run"
                                       " of it occurs in any text of the source", "sources": summ}
    res["produced_by"] = {rel: pins(rel) for rel in CODE_FILES}
    res["corpus_db_file_sha256"] = file_sha256(corpus_path)
    res["wall_seconds"] = round(time.time() - t0, 1)
    out("[OWED] done in %.1f s" % res["wall_seconds"])
    return res


def print_owed(res, out=print):
    out("[OWED] (iii) OPTIONS-key map to %s: %s" % (LEGACY_POOL, json.dumps(res["iii_options_key_map"]["splits"]["gpt"]["counts"])))
    out("[OWED]       board of record judged qids: %d; p2dca judgeable ids: %d"
        % (res["iii_options_key_map"]["board_of_record_judged_qids(x12all distinct valid qid)"],
           res["iii_options_key_map"]["p2dca_judgeable_ids"]))
    out("[OWED] (ii) %s membership (GPT): %s; disagreements %s" % (
        V2_POOL, json.dumps(res["ii_pool_membership"]["splits"]["gpt"]["counts"]),
        res["ii_pool_membership"]["splits"]["gpt"]["side_vs_pool_disagreements"]))
    for name, s in res["i_overlap_8token"]["sources"].items():
        out("[OWED] (i) %-28s texts %6d | GPT questions hit %s | control %s | non-knowledge %s" % (
            name, s["texts_streamed"], s["gpt_questions_hit_by_category"] or "{}", "FIRED" if s["control_fired"] else "SILENT",
            s["non_knowledge_hits(pair_id, max shingles in one text)"] or "none"))


# ── manifest ─────────────────────────────────────────────────────────────────────────────────────

def write_manifest(db_path, owed, path):
    need(not os.path.exists(path), "%s exists; the manifest is write-once. Refused." % path)
    facts = describe(db_path)
    check_facts(facts)
    man = {"test": TEST, "registration": "docs/judge_v2_program.md L17330-L17533 (verbatim L17335-L17498), commit 6134573",
           "kind_of_hashes": "file_sha256 / table_sha256 = sha256 hex of the bytes (tables: repr(row) + LF per row ORDER BY key);"
                             " code pins: blob = git blob id of the LF rendering, sha256-lf16 / sha256-crlf16 = first 16 hex",
           "sources": {s: {"url": url_of(s), "revision": HF_REVISION, "path": p, "bytes": n, "sha256": h}
                       for s, (p, n, h) in SOURCES.items()},
           "corpus_db": facts,
           "side_export": {"file": SIDE_EXPORT_REL.replace(os.sep, "/"), "table_sha": SIDE_EXPORT_TABLE_SHA,
                           "rows": SIDE_EXPORT_ROWS},
           "owed_checks": owed,
           "code": {rel: pins(rel) for rel in CODE_FILES},
           "hygiene": "The corpus DB and both verdict caches are EXCLUDED inputs for any construction, labelling, induction,"
                      " rubric fit, selection or policy fit (HYGIENE (c)). Knowledge rows are mixed-side, disclosed (rule 12)."}
    txt = json.dumps(man, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    print("[JB-INGEST] wrote %s (write-once), sha256 %s" % (path, hashlib.sha256(txt.encode("utf-8")).hexdigest()))
    return txt


# ── selftest ─────────────────────────────────────────────────────────────────────────────────────

def selftest():
    import ast
    fails = []

    def check(cond, what):
        print("  [%s] %s" % ("ok" if cond else "FAIL", what))
        if not cond:
            fails.append(what)

    # okey equals boundary_disagreement.okey (AST, docstring dropped)
    def fn_ast(path, name):
        t = ast.parse(open(path, encoding="utf-8").read())
        f = next(n for n in t.body if isinstance(n, ast.FunctionDef) and n.name == name)
        body = f.body[1:] if isinstance(f.body[0], ast.Expr) and isinstance(getattr(f.body[0], "value", None), ast.Constant) else f.body
        return ast.dump(ast.Module(body=body, type_ignores=[]))
    check(fn_ast(os.path.abspath(__file__), "okey") == fn_ast(os.path.join(ANALYSIS, "boundary_disagreement.py"), "okey"),
          "okey is boundary_disagreement.okey (AST equal)")
    src = open(os.path.join(ANALYSIS, "judge_v2", "induction.py"), encoding="utf-8").read()
    check('re.findall(r"\\w+", s.casefold())' in src, "the shingle tokeniser is judge_v2.induction._tokens' rule")
    # option parsing
    q = "Stem line?\n(A) one\n(B) two words\n(C)  three \n" + KNOWLEDGE_SUFFIX.lstrip("\n") + " x.\nLet's think step by step."
    check(knowledge_stem(q) == "Stem line?", "knowledge stem = text before the first '\\n(A) '")
    check(knowledge_options(q) == ["one", "two words", " three "] and okey_list(knowledge_options(q)) == okey(json.dumps(["one", "two words", "three"])),
          "options parsed in letter order; okey_list == okey of the JSON list")
    try:
        knowledge_options("S\n(A) a\n(C) c\n" + KNOWLEDGE_SUFFIX.lstrip("\n"))
        check(False, "a letter gap is refused")
    except SystemExit:
        check(True, "a letter gap is refused")
    # sha refusal
    try:
        verify_bytes("gpt", b"not the file")
        check(False, "a source whose sha256 differs is REFUSED")
    except SystemExit:
        check(True, "a source whose sha256 differs is REFUSED")
    # build on synthetic rows (sha check bypassed by building the rows directly)
    tmp = tempfile.mkdtemp(prefix="jb_ingest_selftest_")
    side_map = {"i:" + split_side.stem_key("Stem line?"): "EVAL"}

    def mk(pid, src, qq, lab):
        return json.dumps({"pair_id": pid, "original_id": 1, "source": src, "question": qq, "response_model": "m",
                           "response_A": "aa", "response_B": "b", "label": lab}).encode("utf-8")
    saved = dict(EXPECT_ROWS)
    try:
        EXPECT_ROWS.update(gpt=2, claude=1)
        raw = {"gpt": mk("p1", "mmlu-pro-law", q, "A>B") + b"\n" + mk("p2", "livebench-math", "Para one.\n\nPara two.", "B>A") + b"\n",
               "claude": mk("p3", "livecodebench", "code?", "A>B") + b"\n"}
        dbp = os.path.join(tmp, "c.db")
        facts = build(raw, dbp, side_map, "# header")
        check(facts["counts"]["gpt"]["rows"] == 2 and facts["counts"]["claude"]["rows"] == 1, "rows written per split")
        c = open_corpus_ro(dbp)
        sides = dict(c.execute("SELECT pair_id, side_v2 FROM pairs"))
        c.close()
        check(sides == {"p1": "EVAL", "p2": NOT_IN_SPLIT, "p3": NOT_IN_SPLIT}, "every row carries its side (EVAL / NOT_IN_SPLIT)")
        check(facts["counts"]["gpt"]["longer_is_correct"]["all"].startswith("1 / 2"), "longer-is-correct counted")
        try:
            build(raw, dbp, side_map, "# header")
            check(False, "the corpus DB is write-once")
        except SystemExit:
            check(True, "the corpus DB is write-once")
        f2 = describe(dbp)
        check(f2["tables"] == facts["tables"], "describe() is deterministic")
        bad = {"gpt": raw["gpt"].replace(b"Para two.", b"$traceA"), "claude": raw["claude"]}
        try:
            build(bad, os.path.join(tmp, "d.db"), side_map, "# header")
            check(False, "a template token in a row is refused")
        except SystemExit:
            check(True, "a template token in a row is refused")
    finally:
        EXPECT_ROWS.clear()
        EXPECT_ROWS.update(saved)
    # overlap control
    rows = [{"pair_id": "x", "question": "alpha beta gamma delta epsilon zeta eta theta iota"}]
    ov = overlap_pass(rows, {"s": ["one two three four five six seven eight nine", "alpha beta gamma delta epsilon zeta eta theta"]})
    check(ov["s"]["hits"].get("x") == 1 and ov["s"]["hits"].get("CONTROL:s", 0) > 0, "overlap: a shared 8-run hits; control fires")
    try:
        overlap_pass(rows, {"s": ["too short"]})
        check(False, "a source with no 8-token text voids the control (refused)")
    except SystemExit:
        check(True, "a source with no 8-token text voids the control (refused)")
    # manifest write-once
    mp = os.path.join(tmp, "m.json")
    open(mp, "x").close()
    try:
        write_manifest(dbp, {}, mp)
        check(False, "the manifest is write-once")
    except SystemExit:
        check(True, "the manifest is write-once")
    print("[JB-INGEST SELFTEST] %d failure(s)%s" % (len(fails), "" if not fails else ": " + "; ".join(fails)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--fetch", action="store_true")
    g.add_argument("--build", action="store_true")
    g.add_argument("--owed-checks", action="store_true")
    g.add_argument("--write-manifest", action="store_true")
    g.add_argument("--describe", action="store_true")
    ap.add_argument("--raw-dir")
    ap.add_argument("--out", default=os.path.join(ROOT, DB_NAME))
    ap.add_argument("--data-root", default=os.environ.get("TAXOARENA_DATA_ROOT", ROOT))
    ap.add_argument("--owed-json")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.fetch:
        need(a.raw_dir, "--fetch needs --raw-dir")
        fetch(a.raw_dir)
        return 0
    if a.build:
        need(a.raw_dir, "--build needs --raw-dir")
        side_map, head = load_side_export()
        facts = build(read_raw(a.raw_dir), a.out, side_map, head)
        check_facts(facts)
        print(json.dumps(facts, indent=1, sort_keys=True))
        return 0
    if a.describe:
        print(json.dumps(describe(a.out), indent=1, sort_keys=True))
        return 0
    if a.owed_checks:
        need(a.owed_json, "--owed-checks needs --owed-json <scratch file>")
        need(not os.path.exists(a.owed_json), "%s exists; refused" % a.owed_json)
        res = owed_checks(a.data_root, a.out)
        with open(a.owed_json, "x", encoding="utf-8") as f:
            json.dump(res, f, indent=1, sort_keys=True)
        print_owed(res)
        return 0
    if a.write_manifest:
        need(a.owed_json and os.path.isfile(a.owed_json), "--write-manifest needs --owed-json <file of --owed-checks>")
        write_manifest(a.out, json.load(open(a.owed_json, encoding="utf-8")), os.path.join(ROOT, MANIFEST_REL))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
