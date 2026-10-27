"""TOPIC-PARTITION-20NG ingest (docs/judge_v2_program.md, "Registered 2026-09-22 (before any code or call) -
TOPIC-PARTITION-20NG", L10030-L10390, registration commit 6aa2a0d; instrument I0). ZERO LLM calls.

Writes the SEPARATE root-level dataset DB `twenty_newsgroups_cache_v1.db` (gitignored by `*.db`) under Design N
(namespaced ids), never mmlu_pro_dataset_cache_v2.db (data-steward H1: the built-in loader joins a corpus table to
eval_question_link by local rowid, MMLUDatasetFetcher.kt L498-506, so a 20NG row in the DB of record would inherit
an MMLU-Pro eval id). Schema, column names and types copied from the engine so that its CREATE TABLE IF NOT EXISTS
is a no-op (MMLUDatasetFetcher.initDatabase L117-190; ModelEvalStore.initSchema L129-200; the corpus_questions
reader ModelEvalStore.getReservedQuestionTexts L639-656):
  twenty_newsgroups(id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT,
                    options TEXT, answer TEXT)          id = ingest order (bydate order after filtering, 1..N);
                    question = body.strip(); category = the raw sklearn target_name ("rec.sport.hockey");
                    cot_content = ''; options = '[]'; answer = category
  eval_question_link(question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT,
                    has_embedding INTEGER DEFAULT 0)   question_id = k >= 1 (k = rowid); mmlu_pro_row_id = rowid
  corpus_questions(question_id INTEGER PRIMARY KEY, text TEXT)   question_id = 8,000,000 + k
                    (TWENTY_NEWSGROUPS offset 8,000,000 = CorpusRegistry.BUILTIN, (LEADERBOARD_COUNT + 3) x 1M;
                    AG_NEWS 9,000,000), so the engine's [POOL] / [POOL-PIN] / TRAIN-ONLY-at-save guards resolve the
                    pool's texts through corpus_questions in this DB.
Ingest rules (registration I0 (1)-(7), fixed because they change the corpus the seed splits):
  (1) text = stripped body (sklearn remove=('headers','footers','quotes'));
  (2) drop any document whose norm-v1 text (tools/analysis/split_side.norm: NFKC, ASCII case fold, whitespace runs
      to one space, trimmed) is shorter than 100 characters;
  (3) drop ALL copies of any norm-v1 collision (cross-posts and duplicates, label-agreeing or not);
  (4) no NUL bytes (refused, never repaired);
  (5) the table must hold >= 2,000 rows (the engine's HF fallback short-circuit, MMLUDatasetFetcher.kt L961);
  (6) manifest: raw 18,846; dropped short; dropped duplicate; kept; per label; sha256 over
      `SELECT id, question, category FROM twenty_newsgroups ORDER BY id` (repr(row) + LF per row, the review
      2026-09-20 section 3 hashing);
  (7) leak count: kept documents whose body contains any of the 20 label strings, case-insensitive (kept; a
      sensitivity row in the readout).

Launch sequence (the chain tools/chains/topic_partition.sh runs the real ingest; the engine-coder ran only the
selftest and the dry-run):
  python tools/ingest/twenty_newsgroups_ingest.py --selftest                 # synthetic mini-corpus, temp DB
  python tools/ingest/twenty_newsgroups_ingest.py --dry-run                  # counts + manifest, writes nothing
  python tools/ingest/twenty_newsgroups_ingest.py [--fetch] [--out twenty_newsgroups_cache_v1.db]   # the ingest
  python tools/ingest/twenty_newsgroups_ingest.py --manifest [--out <db>]    # recompute, verify against the DB,
                                                                             # print and write <out>.manifest.json
  python tools/ingest/twenty_newsgroups_ingest.py --smoke-ag-news [--dry-run]   # I1: the 2,000 ag_news rows of
      mmlu_pro_dataset_cache_v2.db (mode=ro) copied VERBATIM into ag_news_smoke_cache_v1.db under Design N
      (table ag_news, offset 9,000,000), same manifest (rules (2)-(3) are COUNTED, not applied: a verbatim copy)
Cache it reads: sklearn's 20news-bydate (fetch_20newsgroups(subset='all', remove=('headers','footers','quotes'),
shuffle=False)) in the default sklearn data home. The ~14 MB network fetch is the ONE fetch the registration
declares (CORPUS (c)); it is performed only under --fetch (download_if_missing=True); every other mode refuses when
the cache is absent. Guard: the output DB is write-once (refused if it exists), never one of the DBs of record;
every DB of record is opened mode=ro; the manifest is verified by re-reading the written DB.
"""
import argparse
import datetime
import hashlib
import json
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "analysis"))
from split_side import norm  # noqa: E402  norm-v1, byte-identical to SplitSide.kt

DEFAULT_OUT = os.path.join(ROOT, "twenty_newsgroups_cache_v1.db")
SMOKE_OUT = os.path.join(ROOT, "ag_news_smoke_cache_v1.db")
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)        # a worktree without the caches (pool_guard.py rule)
DB_OF_RECORD = os.path.join(DATA_ROOT, "mmlu_pro_dataset_cache_v2.db")
NEVER_WRITE = {"mmlu_pro_dataset_cache_v2.db", "embeddings_cache.db", "snapshots.db", "snapshots_frozen.db",
               "multicorpus_cache_v1.db"}
OFFSET = {"twenty_newsgroups": 8_000_000, "ag_news": 9_000_000}   # CorpusRegistry.BUILTIN (LEADERBOARD_COUNT + i) x 1M
MIN_ROWS = 2000            # rule (5): MMLUDatasetFetcher.kt L961 short-circuit
MIN_NORM_LEN = 100         # rule (2)
RAW_EXPECTED = 18846       # registration CORPUS
LABELS_20 = ['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc', 'comp.sys.ibm.pc.hardware',
             'comp.sys.mac.hardware', 'comp.windows.x', 'misc.forsale', 'rec.autos', 'rec.motorcycles',
             'rec.sport.baseball', 'rec.sport.hockey', 'sci.crypt', 'sci.electronics', 'sci.med', 'sci.space',
             'soc.religion.christian', 'talk.politics.guns', 'talk.politics.mideast', 'talk.politics.misc',
             'talk.religion.misc']
LONG_DOC_CHARS = 8000      # readout sensitivity row (Ollama truncation), counted here for the manifest


def script_sha():
    with open(os.path.abspath(__file__), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()[:16]


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:            # another drive (the selftest's temp dir on Windows)
        return p.replace("\\", "/")


def die(msg, code=1):
    print("[20NG-INGEST] " + msg)
    sys.exit(code)


# ----------------------------------------------------------------------------------------------- rules
def apply_rules(docs, labels, min_rows=MIN_ROWS, min_norm_len=MIN_NORM_LEN, apply_filters=True, strip=True):
    """docs: list of (raw_body, label) in source order. Returns (kept rows [(text, label, source_index)], stats).
    Rules (1)-(5) and (7) of the registration; with apply_filters=False (the ag_news verbatim copy) rules (2)-(3)
    are counted but nothing is dropped (strip=False keeps the rows of record byte-for-byte). NUL bytes are refused
    in every mode."""
    raw = len(docs)
    texts = [((b.strip() if strip else b), lab, i) for i, (b, lab) in enumerate(docs)]     # (1)
    nul = sum(1 for t, _, _ in texts if "\x00" in t)
    norms = [norm(t) for t, _, _ in texts]
    short_idx = {i for i, n in enumerate(norms) if len(n) < min_norm_len}                  # (2)
    survivors = [i for i in range(raw) if i not in short_idx]
    counts = {}
    for i in survivors:
        counts[norms[i]] = counts.get(norms[i], 0) + 1
    dup_idx = {i for i in survivors if counts[norms[i]] > 1}                                # (3): ALL copies
    dup_groups = sum(1 for c in counts.values() if c > 1)
    cross_label_groups = 0
    if dup_groups:
        by_norm = {}
        for i in survivors:
            if counts[norms[i]] > 1:
                by_norm.setdefault(norms[i], set()).add(texts[i][1])
        cross_label_groups = sum(1 for labs in by_norm.values() if len(labs) > 1)
    if apply_filters:
        kept = [texts[i] for i in range(raw) if i not in short_idx and i not in dup_idx]
    else:
        kept = list(texts)
    if any("\x00" in t for t, _, _ in kept):                                                # (4)
        die("%d document(s) carry a NUL byte; refusing (rule 4: no NUL bytes, never repaired)" % nul)
    if len(kept) < min_rows:                                                                # (5)
        die("only %d rows would be kept, the table must hold >= %d (rule 5: MMLUDatasetFetcher.kt L961)" % (len(kept), min_rows))
    per_label = {}
    for _, lab, _ in kept:
        per_label[lab] = per_label.get(lab, 0) + 1
    lower_labels = [l.lower() for l in labels]
    leak = sum(1 for t, _, _ in kept if any(l in t.lower() for l in lower_labels))         # (7)
    stats = {
        "raw": raw, "nul_raw": nul, "dropped_short": len(short_idx), "dropped_duplicate": len(dup_idx),
        "duplicate_groups": dup_groups, "duplicate_groups_cross_label": cross_label_groups,
        "kept": len(kept), "labels": len(per_label), "per_label": {k: per_label[k] for k in sorted(per_label)},
        "leak_count": leak, "leak_share": round((leak / len(kept)) if kept else 0.0, 6),
        "long_docs_over_8000_chars": sum(1 for t, _, _ in kept if len(t) > LONG_DOC_CHARS),
        "max_chars": max((len(t) for t, _, _ in kept), default=0),
        "min_norm_len": min_norm_len, "min_rows": min_rows, "filters_applied": apply_filters,
    }
    return kept, stats


def rows_sha(rows):
    """sha256 over repr(row) + LF per row of `SELECT id, question, category ... ORDER BY id` (review 2026-09-20 section 3)."""
    h = hashlib.sha256()
    for row in rows:
        h.update(repr(tuple(row)).encode())
        h.update(b"\n")
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------- Design N
SCHEMA = """
CREATE TABLE IF NOT EXISTS {table} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    category TEXT,
    cot_content TEXT,
    options TEXT,
    answer TEXT
);
CREATE TABLE IF NOT EXISTS eval_question_link (
    question_id      INTEGER PRIMARY KEY,
    mmlu_pro_row_id  INTEGER,
    question_text    TEXT,
    has_embedding    INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS corpus_questions (
    question_id INTEGER PRIMARY KEY,
    text TEXT
);
"""


def write_design_n(out_db, table, kept):
    """Write the three tables; ids 1..N in ingest order; k = rowid; corpus id = offset + k. Write-once."""
    if os.path.exists(out_db):
        die("%s exists; the ingest DB is write-once (delete it by hand if a re-ingest is intended)" % out_db)
    if os.path.basename(out_db) in NEVER_WRITE:
        die("refusing to write %s (a DB of record)" % out_db)
    offset = OFFSET[table]
    con = sqlite3.connect(out_db)
    try:
        con.executescript(SCHEMA.format(table=table))
        con.execute("BEGIN")
        for k, (text, label, _src) in enumerate(kept, start=1):
            con.execute("INSERT INTO %s (id, question, category, cot_content, options, answer) VALUES (?, ?, ?, '', '[]', ?)" % table,
                        (k, text, label, label))
            con.execute("INSERT INTO eval_question_link (question_id, mmlu_pro_row_id, question_text, has_embedding) VALUES (?, ?, ?, 0)",
                        (k, k, text))
            con.execute("INSERT INTO corpus_questions (question_id, text) VALUES (?, ?)", (offset + k, text))
        con.commit()
    finally:
        con.close()


def verify_design_n(db, table, expected_kept=None):
    """Re-read the written DB: row counts agree across the three tables, k == rowid, texts agree, ids contiguous."""
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    try:
        n = con.execute("SELECT COUNT(*) FROM %s" % table).fetchone()[0]
        n_link = con.execute("SELECT COUNT(*) FROM eval_question_link").fetchone()[0]
        n_cq = con.execute("SELECT COUNT(*) FROM corpus_questions").fetchone()[0]
        lo, hi = con.execute("SELECT MIN(id), MAX(id) FROM %s" % table).fetchone()
        bad_link = con.execute(
            "SELECT COUNT(*) FROM %s m LEFT JOIN eval_question_link l ON l.mmlu_pro_row_id = m.id"
            " WHERE l.question_id IS NULL OR l.question_id != m.id OR l.question_text != m.question" % table).fetchone()[0]
        bad_cq = con.execute(
            "SELECT COUNT(*) FROM %s m LEFT JOIN corpus_questions q ON q.question_id = m.id + %d"
            " WHERE q.text IS NULL OR q.text != m.question" % (table, OFFSET[table])).fetchone()[0]
        rows = con.execute("SELECT id, question, category FROM %s ORDER BY id" % table).fetchall()
        nul = con.execute("SELECT COUNT(*) FROM %s WHERE instr(question, char(0)) > 0" % table).fetchone()[0]
        per_label = dict(con.execute("SELECT category, COUNT(*) FROM %s GROUP BY category ORDER BY category" % table).fetchall())
        opts = con.execute("SELECT COUNT(*) FROM %s WHERE options != '[]' OR cot_content != '' OR answer != category" % table).fetchone()[0]
    finally:
        con.close()
    problems = []
    if not (n == n_link == n_cq):
        problems.append("row counts differ: %s=%d eval_question_link=%d corpus_questions=%d" % (table, n, n_link, n_cq))
    if n and (lo, hi) != (1, n):
        problems.append("ids not contiguous 1..N: min=%s max=%s n=%d" % (lo, hi, n))
    if bad_link:
        problems.append("%d eval_question_link rows disagree with the corpus table (k != rowid or text)" % bad_link)
    if bad_cq:
        problems.append("%d corpus_questions rows disagree (offset + k or text)" % bad_cq)
    if nul:
        problems.append("%d rows carry a NUL byte" % nul)
    if opts:
        problems.append("%d rows have options != '[]' / cot_content != '' / answer != category" % opts)
    if expected_kept is not None and n != expected_kept:
        problems.append("row count %d != kept %d" % (n, expected_kept))
    if problems:
        die("verification of %s FAILED: %s" % (db, "; ".join(problems)))
    return dict(rows=n, sha256_id_question_category=rows_sha(rows), per_label=per_label, id_min=lo, id_max=hi)


# ----------------------------------------------------------------------------------------------- 20NG
def load_20ng(fetch):
    try:
        from sklearn.datasets import fetch_20newsgroups, get_data_home
    except ImportError:
        die("scikit-learn is not installed")
    import sklearn
    home = get_data_home()
    try:
        ds = fetch_20newsgroups(subset="all", remove=("headers", "footers", "quotes"), shuffle=False,
                                download_if_missing=bool(fetch))
    except OSError as e:
        die("20news-bydate is not in the sklearn data home %s and --fetch was not given (%s); the registration's one"
            " declared fetch is `--fetch`" % (home, e))
    cache = os.path.join(home, "20news-bydate_py3.pkz")
    print("[20NG-INGEST] sklearn %s data_home=%s cache=%s size=%s sha256=%s"
          % (sklearn.__version__, home, cache,
             os.path.getsize(cache) if os.path.exists(cache) else "absent",
             sha_file(cache) if os.path.exists(cache) else "absent"))
    names = list(ds.target_names)
    if names != LABELS_20:
        die("target_names differ from the registered 20 labels: %s" % names)
    docs = [(ds.data[i], names[ds.target[i]]) for i in range(len(ds.data))]
    if len(docs) != RAW_EXPECTED:
        die("raw count %d != %d (registration CORPUS: 18,846 documents)" % (len(docs), RAW_EXPECTED))
    return docs, names, dict(sklearn=sklearn.__version__, data_home=home, cache=cache,
                             cache_sha256=sha_file(cache) if os.path.exists(cache) else None,
                             fetch_call="fetch_20newsgroups(subset='all', remove=('headers','footers','quotes'), shuffle=False)")


def manifest_for(table, out_db, stats, verify, source):
    return {
        "registration": "TOPIC-PARTITION-20NG, docs/judge_v2_program.md L10030-L10390, commit 6aa2a0d, instrument I0",
        "design": "N (namespaced): %s(id=k) + eval_question_link(question_id=k, mmlu_pro_row_id=k) + corpus_questions(question_id=%d+k)"
                  % (table, OFFSET[table]),
        "table": table, "id_offset": OFFSET[table], "db": rel(out_db),
        "script_sha": script_sha(), "date": datetime.date.today().isoformat(),
        "rules": ["(1) text = body.strip()", "(2) drop norm-v1 length < %d" % stats["min_norm_len"],
                  "(3) drop ALL copies of any norm-v1 collision", "(4) no NUL bytes (refused)",
                  "(5) kept >= %d asserted" % stats["min_rows"],
                  "(6) sha256 over repr(row)+LF of SELECT id, question, category ORDER BY id",
                  "(7) leak = kept docs containing any label string, case-insensitive (kept)"],
        "filters_applied": stats["filters_applied"],
        "counts": {k: stats[k] for k in ("raw", "nul_raw", "dropped_short", "dropped_duplicate", "duplicate_groups",
                                         "duplicate_groups_cross_label", "kept", "labels", "leak_count", "leak_share",
                                         "long_docs_over_8000_chars", "max_chars")},
        "per_label": stats["per_label"],
        "sha256_id_question_category": verify["sha256_id_question_category"] if verify else None,
        "rows_in_db": verify["rows"] if verify else None,
        "source": source,
    }


def print_manifest(m):
    print("[20NG-INGEST] MANIFEST %s (%s, offset %d)" % (m["db"], m["table"], m["id_offset"]))
    c = m["counts"]
    print("  raw=%d  nul_raw=%d  dropped_short=%d (norm-v1 < %s)  dropped_duplicate=%d (%d groups, %d cross-label)  kept=%d  labels=%d"
          % (c["raw"], c["nul_raw"], c["dropped_short"], m["rules"][1].split("< ")[1], c["dropped_duplicate"],
             c["duplicate_groups"], c["duplicate_groups_cross_label"], c["kept"], c["labels"]))
    print("  leak_count=%d / %d kept (%.4f)  long_docs>8000_chars=%d  max_chars=%d  filters_applied=%s"
          % (c["leak_count"], c["kept"], c["leak_share"], c["long_docs_over_8000_chars"], c["max_chars"], m["filters_applied"]))
    for k, v in m["per_label"].items():
        print("  %-28s %6d" % (k, v))
    print("  sha256(id, question, category ORDER BY id) = %s   rows_in_db=%s" % (m["sha256_id_question_category"], m["rows_in_db"]))
    print("  script_sha=%s date=%s source=%s" % (m["script_sha"], m["date"], json.dumps(m["source"], sort_keys=True)))


def write_manifest(out_db, m):
    path = out_db + ".manifest.json"
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(m, f, indent=2, sort_keys=True)
        f.write("\n")
    print("[20NG-INGEST] wrote %s" % path)
    return path


def run_ingest(out_db, fetch, dry_run, manifest_only):
    docs, names, source = load_20ng(fetch)
    kept, stats = apply_rules(docs, names)
    if dry_run:
        m = manifest_for("twenty_newsgroups", out_db, stats, None, source)
        m["sha256_id_question_category"] = rows_sha([(k, t, lab) for k, (t, lab, _) in enumerate(kept, start=1)]) + " (computed from the kept rows; nothing written)"
        print_manifest(m)
        print("[20NG-INGEST] DRY RUN: nothing written (would write %s with %d rows)" % (out_db, len(kept)))
        return 0
    if manifest_only:
        if not os.path.exists(out_db):
            die("--manifest: %s does not exist; run the ingest first" % out_db)
        verify = verify_design_n(out_db, "twenty_newsgroups", expected_kept=len(kept))
        fresh = rows_sha([(k, t, lab) for k, (t, lab, _) in enumerate(kept, start=1)])
        if fresh != verify["sha256_id_question_category"]:
            die("--manifest: the DB's sha %s != the sha of a fresh application of the rules %s (the corpus or the rules moved)"
                % (verify["sha256_id_question_category"], fresh))
        m = manifest_for("twenty_newsgroups", out_db, stats, verify, source)
        print_manifest(m)
        write_manifest(out_db, m)
        print("[20NG-INGEST] --manifest: DB agrees with a fresh application of the rules (sha %s)" % fresh)
        return 0
    write_design_n(out_db, "twenty_newsgroups", kept)
    verify = verify_design_n(out_db, "twenty_newsgroups", expected_kept=len(kept))
    m = manifest_for("twenty_newsgroups", out_db, stats, verify, source)
    print_manifest(m)
    write_manifest(out_db, m)
    print("[20NG-INGEST] wrote %s (%d rows; verified by re-read)" % (out_db, verify["rows"]))
    return 0


# ----------------------------------------------------------------------------------------------- I1 smoke (ag_news)
def run_smoke_ag_news(out_db, dry_run):
    if not os.path.exists(DB_OF_RECORD):
        die("%s not found (the ag_news rows of record live there)" % DB_OF_RECORD)
    con = sqlite3.connect("file:%s?mode=ro" % DB_OF_RECORD.replace("\\", "/"), uri=True)
    try:
        rows = con.execute("SELECT id, question, category, cot_content, options, answer FROM ag_news ORDER BY id").fetchall()
        src_sha = rows_sha([(r[0], r[1], r[2]) for r in rows])
    finally:
        con.close()
    if len(rows) != 2000:
        die("ag_news of record has %d rows, expected 2,000" % len(rows))
    if [r[0] for r in rows] != list(range(1, 2001)):
        die("ag_news ids of record are not 1..2000")
    if any(r[3] != "" or r[4] != "[]" or r[5] != r[2] for r in rows):
        die("ag_news rows of record are not (cot_content '', options '[]', answer = category)")
    labels = sorted({r[2] for r in rows})
    docs = [(r[1], r[2]) for r in rows]
    kept, stats = apply_rules(docs, labels, min_rows=MIN_ROWS, apply_filters=False, strip=False)   # verbatim copy: counted, not dropped
    if [t for t, _, _ in kept] != [r[1] for r in rows]:
        die("ag_news copy is not verbatim")
    source = dict(db="mmlu_pro_dataset_cache_v2.db (mode=ro)", table="ag_news", rows=len(rows),
                  sha256_id_question_category_of_record=src_sha)
    fresh = rows_sha([(k, t, lab) for k, (t, lab, _) in enumerate(kept, start=1)])
    if fresh != src_sha:
        die("the verbatim copy would not hash to the rows of record (%s != %s)" % (fresh, src_sha))
    if dry_run:
        m = manifest_for("ag_news", out_db, stats, None, source)
        m["sha256_id_question_category"] = fresh + " (computed; equals the rows of record; nothing written)"
        print_manifest(m)
        print("[20NG-INGEST] DRY RUN: nothing written (would write %s with %d rows)" % (out_db, len(kept)))
        return 0
    write_design_n(out_db, "ag_news", kept)
    verify = verify_design_n(out_db, "ag_news", expected_kept=len(kept))
    if verify["sha256_id_question_category"] != src_sha:
        die("smoke copy sha %s != source sha %s" % (verify["sha256_id_question_category"], src_sha))
    m = manifest_for("ag_news", out_db, stats, verify, source)
    print_manifest(m)
    write_manifest(out_db, m)
    print("[20NG-INGEST] wrote %s (%d rows; sha equals the rows of record)" % (out_db, verify["rows"]))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
def selftest():
    """Synthetic mini-corpus (~60 docs, 4 labels) with planted short docs, exact duplicates, cross-label duplicates,
    a case/whitespace (norm-v1) collision, a leak doc and a NUL byte; written to a temp DB; every rule asserted."""
    import random
    rng = random.Random(20260922)
    labels = ["alpha.one", "beta.two", "gamma.three", "delta.four"]
    words = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore".split()

    def doc(n_words, seed_word):
        return seed_word + " " + " ".join(rng.choice(words) for _ in range(n_words))
    docs = []
    for li, lab in enumerate(labels):
        for j in range(12):
            docs.append(("  " + doc(40, "%s%02d" % (lab.split(".")[0], j)) + "\n", lab))          # 48 normal (leading/trailing ws)
    short = [("tiny doc %d" % i, labels[i % 4]) for i in range(4)]                                 # 4 short (< 100)
    exact = doc(40, "exactdup")
    exact_pair = [(exact, "alpha.one"), (exact, "alpha.one")]                                      # 2 exact, same label
    cross = doc(40, "crossdup")
    cross_pair = [(cross, "beta.two"), (cross, "gamma.three")]                                     # 2 exact, cross label
    casews = doc(40, "casews")
    norm_pair = [(casews, "delta.four"), (casews.upper().replace(" ", "   "), "alpha.one")]        # 2 norm-v1 collision
    leak_doc = [(doc(40, "leaky") + " this mentions Beta.Two explicitly", "gamma.three")]          # 1 leak
    nul_doc = [(doc(40, "nulbyte") + "\x00tail", "delta.four")]                                    # 1 NUL
    corpus = docs + short + exact_pair + cross_pair + norm_pair + leak_doc
    total = len(corpus) + len(nul_doc)
    print("[20NG-INGEST] selftest: %d synthetic docs (48 normal, 4 short, 2 exact dup, 2 cross-label dup, 2 norm-v1 collision, 1 leak, 1 NUL)" % total)
    checks = 0

    def expect_exit(fn, what):
        try:
            fn()
        except SystemExit as e:
            assert e.code == 1, what
            return
        raise AssertionError("expected a refusal: " + what)

    # (4) NUL refused
    expect_exit(lambda: apply_rules(corpus + nul_doc, labels, min_rows=40), "NUL byte must be refused"); checks += 1
    # (5) min rows refused at the default 2,000
    expect_exit(lambda: apply_rules(corpus, labels), "kept < 2000 must be refused at the default"); checks += 1
    kept, st = apply_rules(corpus, labels, min_rows=40)
    assert st["raw"] == len(corpus) == 59, st["raw"]; checks += 1
    assert st["dropped_short"] == 4, st; checks += 1
    assert st["dropped_duplicate"] == 6 and st["duplicate_groups"] == 3 and st["duplicate_groups_cross_label"] == 2, st; checks += 1
    assert st["kept"] == 49 and st["labels"] == 4, st; checks += 1
    assert st["per_label"] == {"alpha.one": 12, "beta.two": 12, "gamma.three": 13, "delta.four": 12}, st["per_label"]; checks += 1
    assert st["leak_count"] == 1, st; checks += 1
    assert all(t == t.strip() for t, _, _ in kept), "rule 1: stripped"; checks += 1
    assert all(len(norm(t)) >= 100 for t, _, _ in kept), "rule 2"; checks += 1
    assert len({norm(t) for t, _, _ in kept}) == len(kept), "rule 3: no collision survives"; checks += 1
    src_order = [s for _, _, s in kept]
    assert src_order == sorted(src_order), "ingest order = source order"; checks += 1
    # Design N in a temp DB, verified by re-read; write-once; never a DB of record
    tmp = tempfile.mkdtemp(prefix="ng_selftest_")
    db = os.path.join(tmp, "twenty_newsgroups_cache_v1.db")
    write_design_n(db, "twenty_newsgroups", kept)
    v = verify_design_n(db, "twenty_newsgroups", expected_kept=49)
    assert v["rows"] == 49 and (v["id_min"], v["id_max"]) == (1, 49), v; checks += 1
    con = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
    try:
        assert con.execute("SELECT question_id FROM corpus_questions ORDER BY question_id LIMIT 1").fetchone()[0] == 8_000_001; checks += 1
        assert con.execute("SELECT COUNT(*) FROM corpus_questions WHERE question_id - 8000000 NOT IN (SELECT question_id FROM eval_question_link)").fetchone()[0] == 0; checks += 1
        assert con.execute("SELECT has_embedding, mmlu_pro_row_id FROM eval_question_link WHERE question_id = 7").fetchone() == (0, 7); checks += 1
        assert con.execute("SELECT category, answer, options, cot_content FROM twenty_newsgroups WHERE id = 1").fetchone() == ("alpha.one", "alpha.one", "[]", ""); checks += 1
        # the engine's CREATE TABLE IF NOT EXISTS statements are no-ops on this schema (same table names)
        names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert {"twenty_newsgroups", "eval_question_link", "corpus_questions"} <= names, names; checks += 1
    finally:
        con.close()
    fresh = rows_sha([(k, t, lab) for k, (t, lab, _) in enumerate(kept, start=1)])
    assert fresh == v["sha256_id_question_category"], "manifest sha reproduces from the DB"; checks += 1
    expect_exit(lambda: write_design_n(db, "twenty_newsgroups", kept), "write-once"); checks += 1
    expect_exit(lambda: write_design_n(os.path.join(tmp, "mmlu_pro_dataset_cache_v2.db"), "twenty_newsgroups", kept), "never a DB of record"); checks += 1
    # a tampered DB is caught by the verifier
    con = sqlite3.connect(db)
    con.execute("UPDATE eval_question_link SET question_text = 'x' WHERE question_id = 3"); con.commit(); con.close()
    expect_exit(lambda: verify_design_n(db, "twenty_newsgroups"), "tampered link row"); checks += 1
    m = manifest_for("twenty_newsgroups", db, st, v, dict(selftest=True))
    print_manifest(m)
    mp = write_manifest(db, m)
    assert json.load(open(mp, encoding="utf-8"))["counts"]["kept"] == 49; checks += 1
    # ag_news verbatim mode: filters counted, nothing dropped, min_rows honoured
    kept2, st2 = apply_rules(corpus, labels, min_rows=40, apply_filters=False)
    assert st2["kept"] == 59 and st2["dropped_short"] == 4 and st2["dropped_duplicate"] == 6 and not st2["filters_applied"], st2; checks += 1
    for f in (db, mp):
        os.remove(f)
    os.rmdir(tmp)
    print("[20NG-INGEST] selftest OK: %d checks, 0 failed (temp DB removed)" % checks)
    return 0


# ----------------------------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fetch", action="store_true", help="download 20news-bydate into the sklearn data home if absent (the ONE declared fetch)")
    ap.add_argument("--out", default=None, help="output DB (default twenty_newsgroups_cache_v1.db at the repo root; ag_news_smoke_cache_v1.db for --smoke-ag-news)")
    ap.add_argument("--dry-run", action="store_true", help="counts and manifest, writes nothing")
    ap.add_argument("--selftest", action="store_true", help="synthetic mini-corpus in a temp DB, every rule asserted")
    ap.add_argument("--manifest", action="store_true", help="recompute the manifest, verify it against the existing DB, print and write <out>.manifest.json")
    ap.add_argument("--smoke-ag-news", action="store_true", help="I1: copy the 2,000 ag_news rows of record into ag_news_smoke_cache_v1.db under Design N")
    a = ap.parse_args(argv)
    print("[20NG-INGEST] pool: none (no arena pool is read or written; the corpus's own split is recorded by the build);"
          " script_sha=%s" % script_sha())
    if a.selftest:
        return selftest()
    if a.smoke_ag_news:
        out = os.path.abspath(a.out) if a.out else SMOKE_OUT
        if a.fetch or a.manifest:
            die("--smoke-ag-news takes --out / --dry-run only")
        return run_smoke_ag_news(out, a.dry_run)
    out = os.path.abspath(a.out) if a.out else DEFAULT_OUT
    if os.path.basename(out) in NEVER_WRITE:
        die("refusing --out %s (a DB of record)" % out)
    if a.dry_run and a.manifest:
        die("--dry-run and --manifest are exclusive")
    return run_ingest(out, a.fetch, a.dry_run, a.manifest)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
