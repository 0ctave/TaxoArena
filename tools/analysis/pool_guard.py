"""Reserved-pool guard for the Python analyses (FRAMEWORK.md Stage 0, item 18 SPLIT-FUNCTION-IMPL).

The construction/arena split is the method's contamination guarantee: the tree and the rubrics
are built on the construction side, the arena judges only the reserved side. Sides are carried
by content, never by an active flag: the pinned pools are explicit id files listed in
experiment_configs/reserved_pools.json (the registry), `reserved_pool` rows in the dataset DB
corroborate them, and there is no longer an active pool, no `eval_results.is_reserved` writer
and no `--activate`. Every helper takes the pool id as a MANDATORY argument: a call without
one is a TypeError, because "the active pool" was the incident of 2026-09-09 (71% of arena
questions on the tree's train side) and of 2026-09-14 (~70% in the multi-corpus line).

    import pool_guard
    pool_guard.assert_pool_of_record("p2dca21ab5f4ef3ae")   # file hashes to the id, DB rows agree
    ev = pool_guard.eval_ids("p2dca21ab5f4ef3ae")           # frozenset of judgeable ids; replaces `is_reserved = 1`
    pool_guard.assert_scored_subset("p2dca21ab5f4ef3ae", scored_ids)  # prints the two first lines, exits unless 0

    python tools/analysis/pool_guard.py --pool p2dca21ab5f4ef3ae           # verify + print the registry entry
    python tools/analysis/pool_guard.py --diff-flag p2dca21ab5f4ef3ae      # |{is_reserved = 1} delta eval_ids| (legacy column)
    python tools/analysis/pool_guard.py --export-snapshot snapshots.db <snapshot id> --out <file>
    python tools/analysis/pool_guard.py --pool <id> --db <dataset db> --id-file <exported id file>
        # TOPIC-PARTITION-20NG (docs/judge_v2_program.md L10030-L10390, I0): a corpus's own split recorded
        # in a SEPARATE dataset DB (twenty_newsgroups_cache_v1.db) is verified against the id file exported
        # from its snapshot; the pool need not be in the registry. Both flags are INERT WHEN ABSENT: without
        # them `--pool` reads the registry exactly as before (byte-identical output). A registered pool may
        # take `--db` alone (the id file stays the registry's); an unregistered pool needs both.
    python tools/analysis/pool_guard.py --selftest
        # POOL-GUARD-IMMUTABLE (queue item, 2026-09-23): synthetic WAL-mode DBs in a temp dir; opens no DB of record.

The DBs are looked up under TAXOARENA_DATA_ROOT when set (a worktree without the caches), else
under the repo root. Every DB is opened read-only.
[POOL-GUARD-IMMUTABLE 2026-09-23, engine-coder: open_ro now refuses ([POOL-GUARD]) when the `-wal` beside the DB is
non-empty, then opens `file:<abs path>?mode=ro&immutable=1`, so a guard read of a WAL-mode DB (e.g.
mmlu_pro_dataset_cache_v2.db) creates no `-wal` / `-shm` beside it (review acd054a D7; queued at 8bbe6ce). Pool ids and
success messages are unchanged; `--selftest` executes both branches on synthetic DBs.]
[POOL-GUARD-IMMUTABLE fix 2026-09-23, engine-coder, on READY review d72c790 (D1, D2, D3c, D4, D5): open_ro also
REFUSES a non-empty `-journal` (a rollback-mode DB's live or hot transaction: an immutable read returned 19,634
uncommitted of 20,000 rows where plain mode=ro errored), before any connect; both refusals name the remedy when no
writer is left (back up the DB, then the data-steward's read-write open/close). A journal_mode=PERSIST DB keeps a
non-empty zeroed journal and is therefore refused too (fail-closed). immutable=1 also drops SQLite's locking: the
checks and the connect are not atomic, and a writer starting in between is excluded by rule 7, not by this code.
`--selftest` covers 7 cases, including the real sidecar state of the WAL DBs of record (0-byte -wal, 32 KB -shm).]
[POOL-GUARD-IMMUTABLE C1 2026-09-23, engine-coder, on re-review cc0ccc9 / e4e045a (condition C1, D-R3): rollback-mode
DBs are READ, not refused as a class: a journal_mode=DELETE DB with no -journal and a journal_mode=TRUNCATE DB with a
0-byte -journal are accepted (selftest cases 8 and 9; BFCL and MULTISWE are rollback-mode). LIMITATION, deliberate and
fail-closed: a journal_mode=PERSIST DB keeps a zeroed, NON-EMPTY -journal after a clean commit and is refused like a hot
one; the journal header is not parsed. Convert or checkpoint it before a guard read.]
"""
import hashlib
import json
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
REGISTRY_PATH = os.path.join(ROOT, "experiment_configs", "reserved_pools.json")

# The corpora CorpusRegistry.kt knows (BUILTIN then LEADERBOARD). Pinned by PinnedPoolsReproduceTest,
# which greps the Kotlin file; the split key of a leaderboard corpus is "<SOURCE>/<domain>".
KNOWN_SOURCES = ("MMLU_PRO", "MMLU_ORIGINAL", "ARC", "TWENTY_NEWSGROUPS", "AG_NEWS",
                 "MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA")
DEFAULT_SOURCE = "MMLU_PRO"

# The two pinned pools of record, named so a script says WHICH pool it scores. Both are registry
# entries; the names are not defaults (every helper still takes the id as an argument).
MMLU_PRO_POOL = "p2dca21ab5f4ef3ae"    # 3,445 judgeable MMLU-Pro questions (snapshot 20260727_042523)
UNION_POOL = "paeec37aa28063c75"       # 6,482 ids over six leaderboard corpora (snapshot 20260911_144214)
FROZEN_POOL_ID = MMLU_PRO_POOL         # historical name, kept for the scripts that print it

sys.path.insert(0, HERE)
from split_side import tier_a as side_of, stem_key, content_key, function_stamp  # noqa: E402,F401


# ── pool ids ────────────────────────────────────────────────────────────────────────────────

def canonical_line(key, qid):
    """Mirror of ReservedPool.canonicalLine: `domain:id` for a bare key or an MMLU_PRO key,
    `SOURCE|domain:id` for `<SOURCE>/<domain>` with SOURCE a known non-MMLU_PRO corpus."""
    if "/" in key:
        source, domain = key.split("/", 1)
        if source in KNOWN_SOURCES and source != DEFAULT_SOURCE:
            return "%s|%s:%d" % (source, domain, qid)
    return "%s:%d" % (key, qid)


def compute_pool_id(ids_by_key):
    """Mirror of ReservedPool.computePoolId: 'p' + sha256(sorted canonical lines joined by LF)[:16]."""
    canon = "\n".join(sorted(canonical_line(k, q) for k, ids in ids_by_key.items() for q in ids))
    return "p" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def judgeable(ids_by_key):
    """Drop sentinel ids (<= 0) and empty keys: what the fetcher hashes at split time."""
    out = {k: [q for q in ids if q > 0] for k, ids in ids_by_key.items()}
    return {k: v for k, v in out.items() if v}


# ── registry ────────────────────────────────────────────────────────────────────────────────

def load_registry():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["pools"]


def registry_entry(pool_id):
    if not isinstance(pool_id, str) or not pool_id:
        raise TypeError("pool_guard: a pool id is mandatory (see %s)" % REGISTRY_PATH)
    reg = load_registry()
    if pool_id not in reg:
        raise SystemExit("[POOL-GUARD] pool %s is not in the registry %s (known: %s)"
                         % (pool_id, REGISTRY_PATH, ", ".join(sorted(reg))))
    return reg[pool_id]


def db_path(pool_id):
    return os.path.join(DATA_ROOT, registry_entry(pool_id)["db"])


def id_file_path(pool_id):
    return os.path.join(ROOT, registry_entry(pool_id)["id_file"])


def pool_file_ids(pool_id):
    """key -> [ids] exactly as the id file lists them (sentinels included, routing-only)."""
    with open(id_file_path(pool_id), "r", encoding="utf-8") as f:
        return json.load(f)


def eval_ids(pool_id):
    """The judgeable EVAL ids of a pinned pool, from its id file. Replaces every per-row flag predicate."""
    return frozenset(q for ids in judgeable(pool_file_ids(pool_id)).values() for q in ids)


def in_pool_sql(pool_id, column="question_id", registered=True):
    """SQL predicate `column IN (SELECT question_id FROM reserved_pool WHERE pool_id = '<id>')`: the semijoin every
    reader uses in place of the legacy flag. The id is validated against the registry before it is inlined;
    `registered=False` is for a run's own fresh split (not a pool of record), which the caller must first have
    verified by rows with assert_frozen_pool(conn, pool_id)."""
    if registered:
        registry_entry(pool_id)
    if not isinstance(pool_id, str) or not pool_id:
        raise TypeError("pool_guard.in_pool_sql: a pool id is mandatory")
    if not all(c in "0123456789abcdefp" for c in pool_id):
        raise SystemExit("[POOL-GUARD] malformed pool id %r" % pool_id)
    return "%s IN (SELECT question_id FROM reserved_pool WHERE pool_id = '%s')" % (column, pool_id)


def ro_uri(path):
    """The URI every guard read opens: the ABSOLUTE path, read-only and immutable (POOL-GUARD-IMMUTABLE)."""
    return "file:%s?mode=ro&immutable=1" % os.path.abspath(path).replace("\\", "/")


def open_ro(path):
    """Read-only, sidecar-free open. immutable=1 makes SQLite skip the -wal / -shm entirely (a plain mode=ro open of a
    WAL-mode DB creates a 0-byte -wal and a 32 KB -shm beside it), and it also drops SQLite's locking and hot-journal
    handling, so it would HIDE an uncheckpointed WAL tail and READ the uncommitted pages a rollback-mode writer has
    spilled into the DB file (review d72c790 D1: 19,634 of 20,000 rows torn, where plain mode=ro errored). Both
    sidecars are therefore checked first and a non-empty one is REFUSED before any connect, by an explicit raise
    (never an assert: the guard must hold under -O). Residual (d72c790 D4): the checks and the connect are not atomic;
    a writer that starts in between is excluded by rule 7 (no writer while a pool reader runs), not by this code.
    A journal_mode=PERSIST DB keeps a zeroed non-empty -journal after a clean commit and is refused too (fail-closed,
    the header is not parsed): convert or checkpoint it before a guard read."""
    if not os.path.isfile(path):
        raise SystemExit("[POOL-GUARD] database not found: %s (set TAXOARENA_DATA_ROOT)" % path)
    wal = os.path.abspath(path) + "-wal"
    if os.path.exists(wal):
        n_wal = os.path.getsize(wal)
        if n_wal > 0:
            raise SystemExit("[POOL-GUARD] %s is non-empty (%d bytes): an immutable read would hide the uncheckpointed WAL"
                             " tail. If a writer is still running, stop it (closing it checkpoints the WAL) and re-run;"
                             " if none is left (e.g. a killed JVM), back up the DB, then have the data-steward checkpoint"
                             " it with a read-write open/close, and re-run" % (wal, n_wal))
    journal = os.path.abspath(path) + "-journal"
    if os.path.exists(journal):
        n_journal = os.path.getsize(journal)
        if n_journal > 0:
            raise SystemExit("[POOL-GUARD] %s is non-empty (%d bytes): a rollback-mode writer's transaction is live or was"
                             " left hot by a crash, and an immutable read would return its uncommitted pages. If a writer"
                             " is still running, stop it and re-run; if none is left (e.g. a killed JVM), back up the DB,"
                             " then have the data-steward roll the journal back with a read-write open/close, and re-run"
                             % (journal, n_journal))
    return sqlite3.connect(ro_uri(path), uri=True)


def pool_rows(conn, pool_id):
    rows = {}
    for d, q in conn.execute("SELECT domain, question_id FROM reserved_pool WHERE pool_id = ?", (pool_id,)):
        rows.setdefault(d, []).append(q)
    return rows


# ── guards ──────────────────────────────────────────────────────────────────────────────────

def assert_frozen_pool(conn, expected):
    """Verify on an open connection that `reserved_pool` holds rows for [expected] hashing to it."""
    if not isinstance(expected, str) or not expected:
        raise TypeError("pool_guard.assert_frozen_pool(conn, pool_id): the pool id is mandatory")
    rows = pool_rows(conn, expected)
    if not rows:
        raise SystemExit("[POOL-GUARD] pool %s has no reserved_pool rows in this DB" % expected)
    got = compute_pool_id(rows)
    if got != expected:
        raise SystemExit("[POOL-GUARD] reserved_pool rows for %s hash to %s" % (expected, got))
    return expected


def resolve_sources(pool_id, db=None, id_file=None):
    """(entry, db path, id-file path) for [pool_id]. Without overrides: the registry entry and its paths
    (the historical behaviour, unchanged). `db` overrides the dataset DB the reserved_pool rows are read
    from; `id_file` overrides the id file. A pool that is NOT in the registry is accepted only when BOTH
    are given (entry = None); a registered pool keeps its registry paths for whatever is not overridden."""
    if db is None and id_file is None:
        return registry_entry(pool_id), db_path(pool_id), id_file_path(pool_id)
    if not isinstance(pool_id, str) or not pool_id:
        raise TypeError("pool_guard: a pool id is mandatory (see %s)" % REGISTRY_PATH)
    reg = load_registry()
    entry = reg.get(pool_id)
    if entry is None and (db is None or id_file is None):
        raise SystemExit("[POOL-GUARD] pool %s is not in the registry %s: an unregistered pool needs BOTH --db <dataset db>"
                         " and --id-file <exported id file> (pool_guard.py --export-snapshot)" % (pool_id, REGISTRY_PATH))
    dbp = os.path.abspath(db) if db is not None else db_path(pool_id)
    idp = os.path.abspath(id_file) if id_file is not None else id_file_path(pool_id)
    return entry, dbp, idp


def assert_pool_of_record(pool_id, db=None, id_file=None):
    """First statement of every analysis: the id file hashes to [pool_id], the DB's reserved_pool
    rows hash to it too, and the two sets are equal. Returns the pool id. No default: a script
    that does not say which pool it scores is contaminated until shown otherwise.
    `db` / `id_file` (both default None = the registry) are the TOPIC-PARTITION-20NG overrides
    for a corpus's own split recorded in a separate DB; with neither, the path is the historical one."""
    entry, dbp, idp = resolve_sources(pool_id, db, id_file)
    db_name = entry["db"] if entry is not None and db is None else dbp
    file_name = entry["id_file"] if entry is not None and id_file is None else idp
    with open(idp, "r", encoding="utf-8") as f:
        file_ids = judgeable(json.load(f))
    file_hash = compute_pool_id(file_ids)
    if file_hash != pool_id:
        raise SystemExit("[POOL-GUARD] %s hashes to %s, not %s" % (file_name, file_hash, pool_id))
    n_file = sum(len(v) for v in file_ids.values())
    if entry is not None and n_file != entry["judgeable"]:
        raise SystemExit("[POOL-GUARD] %s lists %d judgeable ids, registry says %d" % (file_name, n_file, entry["judgeable"]))
    conn = open_ro(dbp)
    try:
        rows = pool_rows(conn, pool_id)
    finally:
        conn.close()
    if not rows:
        raise SystemExit("[POOL-GUARD] pool %s is not recorded in %s" % (pool_id, db_name))
    if compute_pool_id(rows) != pool_id:
        raise SystemExit("[POOL-GUARD] reserved_pool rows for %s in %s do not hash to it" % (pool_id, db_name))
    file_set = {(k, q) for k, ids in file_ids.items() for q in ids}
    row_set = {(k, q) for k, ids in rows.items() for q in ids}
    if file_set != row_set:
        raise SystemExit("[POOL-GUARD] %s: id file and reserved_pool rows differ by %d entries"
                         % (pool_id, len(file_set ^ row_set)))
    return pool_id


def assert_scored_subset(pool_id, scored_ids, out=sys.stdout):
    """Every scored run's first two lines: the pool id and |scored \\ eval|; exits non-zero unless 0."""
    ev = eval_ids(pool_id)
    extra = sorted(set(scored_ids) - ev)
    out.write("reserved_pool_id=%s\n" % pool_id)
    out.write("scored_minus_eval=%d\n" % len(extra))
    out.flush()
    if extra:
        raise SystemExit("[SCORED-EVAL] %d scored question(s) are not in pool %s (first: %s)"
                         % (len(extra), pool_id, extra[:10]))
    return 0


# ── one-time evidence and export ────────────────────────────────────────────────────────────

def diff_flag(pool_id):
    """Bit-identity evidence for the read cut-over: {is_reserved = 1} vs eval_ids on the pool's DB.
    Reads the legacy column, which nothing writes any more; prints the symmetric difference."""
    ev = eval_ids(pool_id)
    conn = open_ro(db_path(pool_id))
    try:
        flag = {q for (q,) in conn.execute("SELECT DISTINCT question_id FROM eval_results WHERE is_reserved = 1")}
    finally:
        conn.close()
    d = flag ^ ev
    print("diff_flag %s db=%s flag=%d eval=%d symdiff=%d" % (pool_id, registry_entry(pool_id)["db"], len(flag), len(ev), len(d)))
    return len(d)


def export_snapshot(snapshot_db, snapshot_id, out_path):
    """Export a snapshot's reserved_queries (key -> ids, sentinels included) as an id file; read-only."""
    conn = open_ro(snapshot_db)
    try:
        row = conn.execute("SELECT reserved_queries FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
    finally:
        conn.close()
    if row is None or not row[0]:
        raise SystemExit("[POOL-GUARD] snapshot %s not found or carries no reserved pool" % snapshot_id)
    reserved = json.loads(row[0])
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(reserved, f, indent=4, ensure_ascii=False)
        f.write("\n")
    pid = compute_pool_id(judgeable(reserved))
    print("exported %s: %d keys, %d ids -> %s (%s)" % (snapshot_id, len(reserved), sum(len(v) for v in reserved.values()), pid, out_path))
    return pid


def describe(pool_id, db=None, id_file=None):
    if db is not None or id_file is not None:
        return describe_with_overrides(pool_id, db, id_file)
    entry = registry_entry(pool_id)
    assert_pool_of_record(pool_id)
    ids = pool_file_ids(pool_id)
    print("pool %s OK: %s hashes to it; reserved_pool rows in %s agree" % (pool_id, entry["id_file"], entry["db"]))
    print("  keys=%d ids=%d judgeable=%d sentinels=%d corpus_set=%s (%s) origin=%s"
          % (len(ids), sum(len(v) for v in ids.values()), entry["judgeable"],
             sum(1 for v in ids.values() for q in v if q <= 0), "+".join(entry["corpus_set"]),
             entry.get("corpus_set_version"), entry.get("snapshot_of_origin")))
    for src, mid in sorted(entry.get("member_pools", {}).items()):
        member = {k: v for k, v in ids.items() if k.split("/", 1)[0] == src}
        got = compute_pool_id(judgeable(member))
        print("  member %s -> %s %s" % (src, got, "OK" if got == mid else "MISMATCH (registry %s)" % mid))
        if got != mid:
            raise SystemExit("[POOL-GUARD] member pool %s of %s hashes to %s, registry says %s" % (src, pool_id, got, mid))


def describe_with_overrides(pool_id, db, id_file):
    """`--pool <id> --db <path> [--id-file <path>]`: the same three checks as [assert_pool_of_record] on the
    given DB / id file, then the DB's reserved_pool_meta row (dataset, corpus_size, seed, test_ratio, counts)
    so a corpus's own split (TOPIC-PARTITION-20NG) is described from the DB that recorded it. Never reached
    without an override (the registry path above is untouched)."""
    entry, dbp, idp = resolve_sources(pool_id, db, id_file)
    assert_pool_of_record(pool_id, db, id_file)
    with open(idp, "r", encoding="utf-8") as f:
        ids = json.load(f)
    print("pool %s OK: %s hashes to it; reserved_pool rows in %s agree%s"
          % (pool_id, idp, dbp, "" if entry is None else " (registered pool; registry paths overridden)"))
    print("  keys=%d ids=%d judgeable=%d sentinels=%d%s"
          % (len(ids), sum(len(v) for v in ids.values()), sum(1 for v in ids.values() for q in v if q > 0),
             sum(1 for v in ids.values() for q in v if q <= 0),
             "" if entry is None else " registry_judgeable=%d" % entry["judgeable"]))
    conn = open_ro(dbp)
    try:
        meta = conn.execute("SELECT dataset, corpus_size, seed, test_ratio, question_count, domain_count, created_at"
                            " FROM reserved_pool_meta WHERE pool_id = ?", (pool_id,)).fetchone()
        n_rows = conn.execute("SELECT COUNT(*) FROM reserved_pool WHERE pool_id = ?", (pool_id,)).fetchone()[0]
    finally:
        conn.close()
    if meta is None:
        print("  reserved_pool_meta: no row for %s (rows=%d)" % (pool_id, n_rows))
    else:
        print("  reserved_pool_meta: dataset=%s corpus_size=%s seed=%s test_ratio=%s question_count=%s domain_count=%s created_at=%s (rows=%d)"
              % (meta + (n_rows,)))


def _flag_value(argv, flag):
    """The value after [flag], or None when the flag is absent (the flag without a value is fatal)."""
    if flag not in argv:
        return None
    i = argv.index(flag)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        raise SystemExit("[POOL-GUARD] %s needs a value" % flag)
    return argv[i + 1]


# ── selftest (POOL-GUARD-IMMUTABLE) ─────────────────────────────────────────────────────────

def _legacy_open_ro(path):
    """open_ro's body at blob c857fd2e (before POOL-GUARD-IMMUTABLE), kept for the selftest's before/after checks only."""
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


# A writer that commits a WAL tail (no checkpoint) and dies without closing: leaves a non-empty -wal and a -shm.
_CRASHED_WAL_WRITER = (
    "import os, sqlite3, sys\n"
    "c = sqlite3.connect(sys.argv[1]); c.execute('PRAGMA wal_autocheckpoint=0')\n"
    "c.executemany('INSERT INTO reserved_pool VALUES (?, ?, ?)', [('ptail', 'tail', i) for i in range(1, 51)])\n"
    "c.commit()\n"
    "os._exit(0)\n")

# A rollback-mode writer that spills uncommitted pages into the DB file (cache_size 5) and dies mid-transaction:
# leaves a HOT -journal and a torn DB file (the reviewer's hot/mk.py, d72c790 claim 2, at 3,000 rows).
_CRASHED_ROLLBACK_WRITER = (
    "import os, sqlite3, sys\n"
    "c = sqlite3.connect(sys.argv[1], isolation_level=None); c.execute('PRAGMA cache_size=5')\n"
    "c.execute('BEGIN'); c.execute('UPDATE reserved_pool SET question_id = -question_id')\n"
    "os._exit(0)\n")


def selftest():
    """Synthetic DBs in a fresh temp dir; opens no DB of record. Every check is an explicit branch (no assert), so it
    runs identically under `python -O`; an unexpected refusal or error in a case that must be accepted is recorded as a
    FAIL, never a crash. The URI handed to sqlite3.connect is recorded and printed (execution witness).
    Cases (review d72c790 D1 / D2): 1 no -wal; 2 a 0-byte -wal alone; 3 the REAL state of the WAL DBs of record (0-byte
    -wal beside a 32 KB -shm, made by the plain mode=ro opener) accepted with the -shm untouched, and the pool id equal
    under both openers; 4 a live WAL writer's tail refused; 5 a crashed WAL writer's tail with NO -shm refused, and the
    immutable and WAL-inclusive views shown to differ; 6 a crashed rollback writer's hot -journal refused, the torn
    immutable view shown; 7 a live rollback writer's transaction refused; 8 a rollback-mode (DELETE) DB with no
    -journal ACCEPTED; 9 a TRUNCATE-mode DB with a 0-byte -journal ACCEPTED (re-review cc0ccc9 C1)."""
    import gc
    import shutil
    import subprocess
    import tempfile
    failures = []
    n_checks = [0]

    def check(cond, label):
        ok = bool(cond)
        n_checks[0] += 1
        print("  [%s] %s" % ("PASS" if ok else "FAIL", label))
        if not ok:
            failures.append(label)

    def sidecars(p):
        return {s: (os.path.getsize(p + s) if os.path.exists(p + s) else None) for s in ("-wal", "-shm", "-journal")}

    def file_state(p):
        if not os.path.exists(p):
            return None
        with open(p, "rb") as f:
            return (os.path.getsize(p), os.stat(p).st_mtime_ns, hashlib.sha256(f.read()).hexdigest()[:16])

    def raw_count(uri, sql):
        c = real_connect(uri, uri=True)
        try:
            return c.execute(sql).fetchone()[0]
        finally:
            c.close()

    def guarded_rows(p, pool_id):
        """(rows, None) when open_ro accepts, (None, message) when it refuses or errors; never raises."""
        try:
            conn = open_ro(p)
        except SystemExit as e:
            return None, "SystemExit: %s" % e
        except Exception as e:  # noqa: BLE001 - recorded as a FAIL by the caller
            return None, "%s: %s" % (type(e).__name__, e)
        try:
            return pool_rows(conn, pool_id), None
        except Exception as e:  # noqa: BLE001
            return None, "%s: %s" % (type(e).__name__, e)
        finally:
            conn.close()

    def expect_refusal(p, what):
        n0 = len(seen)
        rows, msg = guarded_rows(p, expected)
        print("  refusal: %s" % msg)
        check(rows is None and msg is not None and msg.startswith("SystemExit: [POOL-GUARD] "),
              "%s REFUSED with the [POOL-GUARD] tag" % what)
        check(len(seen) == n0, "refused BEFORE any connect (connects attempted: %d)" % (len(seen) - n0))
        check(msg is not None and "back up the DB" in msg and "data-steward" in msg and "read-write open/close" in msg,
              "the refusal names the killed-writer remedy (back up, data-steward read-write open/close)")

    def make_db(p, journal_mode):
        w = real_connect(p)
        mode = w.execute("PRAGMA journal_mode=%s" % journal_mode).fetchone()[0]
        w.execute("CREATE TABLE reserved_pool (pool_id TEXT, domain TEXT, question_id INTEGER)")
        w.executemany("INSERT INTO reserved_pool VALUES (?, ?, ?)",
                      [(expected, k, q) for k, qs in sorted(ids.items()) for q in qs] + [(other, "history", 1)])
        w.commit()
        w.close()
        return mode

    def header_mode(p):
        with open(p, "rb") as f:
            h = f.read(20)
        return h[18], h[19]

    ids = {"biology": [3, 5, 7], "law": [2, 41], "MATH/algebra": [11, 12], "IFEVAL/default": [9]}
    expected = compute_pool_id(ids)
    other = compute_pool_id({"history": [1]})
    seen = []
    real_connect = sqlite3.connect

    def recording_connect(*a, **k):
        seen.append(a[0])
        return real_connect(*a, **k)

    tmp = tempfile.mkdtemp(prefix="pool_guard_selftest_")
    print("pool_guard selftest (POOL-GUARD-IMMUTABLE): temp dir %s; synthetic pool %s" % (tmp, expected))
    sqlite3.connect = recording_connect
    try:
        dirs = {k: os.path.join(tmp, k) for k in ("a", "b", "c", "d", "e", "f", "g", "h")}
        for d in dirs.values():
            os.makedirs(d)
        db = os.path.join(dirs["a"], "synthetic_pool.db")
        mode = make_db(db, "WAL")
        check(mode == "wal" and header_mode(db) == (2, 2),
              "synthetic DB is WAL-mode (journal_mode=%s, header bytes 18/19 = %d/%d)" % ((mode,) + header_mode(db)))
        check(sidecars(db) == {"-wal": None, "-shm": None, "-journal": None},
              "precondition: no sidecar beside it (%s)" % sidecars(db))
        legacy_db = os.path.join(dirs["b"], "synthetic_pool.db")
        shutil.copyfile(db, legacy_db)
        sha_before = file_state(db)[2]

        print("case 1: WAL-mode DB, no -wal present")
        n0 = len(seen)
        rows, msg = guarded_rows(db, expected)
        print("  URI used: %s" % (seen[n0:] or ["<none>"])[0])
        check(rows is not None, "accepted (%s)" % (msg or "rows read"))
        check(len(seen) - n0 == 1 and seen[n0] == "file:%s?mode=ro&immutable=1" % os.path.abspath(db).replace("\\", "/"),
              "exactly one connect, URI = file:<abs path>?mode=ro&immutable=1")
        after = sidecars(db)
        check(after["-shm"] is None, "no -shm created (%s)" % after)
        check(after["-wal"] is None, "no -wal created (%s)" % after)
        conn = open_ro(db) if rows is not None else None
        if conn is not None:
            try:
                verified = assert_frozen_pool(conn, expected)
            finally:
                conn.close()
        else:
            verified = None
        check(verified == expected, "assert_frozen_pool verifies %s on the immutable open" % expected)
        check(file_state(db)[2] == sha_before, "DB bytes unchanged (sha256 %s)" % sha_before)

        print("case 2: WAL-mode DB, a 0-byte -wal alone")
        open(db + "-wal", "wb").close()
        n0 = len(seen)
        rows2, msg = guarded_rows(db, expected)
        print("  URI used: %s" % (seen[n0:] or ["<none>"])[0])
        after = sidecars(db)
        check(rows2 is not None and compute_pool_id(rows2) == expected,
              "accepted beside an empty -wal; rows hash to %s (%s)" % (expected, msg or "ok"))
        check(after["-shm"] is None, "no -shm created beside an empty -wal (%s)" % after)
        check(after["-wal"] == 0, "the empty -wal is left at 0 bytes (%s)" % after)
        os.remove(db + "-wal")

        print("case 3: the REAL sidecar state of the WAL DBs of record: 0-byte -wal beside a 32 KB -shm")
        n0 = len(seen)
        lc = _legacy_open_ro(legacy_db)
        try:
            legacy_id = compute_pool_id(pool_rows(lc, expected))
            legacy_during = sidecars(legacy_db)
        finally:
            lc.close()
        print("  legacy URI used: %s" % (seen[n0:] or ["<none>"])[0])
        state = sidecars(legacy_db)
        check(state["-wal"] == 0 and (state["-shm"] or 0) > 0,
              "discriminator: the plain mode=ro open (blob c857fd2e) leaves a 0-byte -wal and a -shm (%s / during: %s)"
              % (state, legacy_during))
        shm_before = file_state(legacy_db + "-shm")
        n0 = len(seen)
        rows3, msg = guarded_rows(legacy_db, expected)
        print("  URI used: %s" % (seen[n0:] or ["<none>"])[0])
        check(rows3 is not None, "ACCEPTED: 0-byte -wal beside a %s-byte -shm (%s)" % (state["-shm"], msg or "rows read"))
        check(file_state(legacy_db + "-shm") == shm_before,
              "the -shm is left byte-identical (size, mtime_ns, sha256-16 = %s)" % (shm_before,))
        check(sidecars(legacy_db)["-wal"] == 0, "the -wal is left at 0 bytes")
        new_id = compute_pool_id(rows3) if rows3 is not None else None
        print("  pool id: expected %s, legacy open %s, immutable open %s" % (expected, legacy_id, new_id))
        check(legacy_id == new_id == expected, "pool id identical before (plain mode=ro) and after (immutable)")

        print("case 4: WAL-mode DB, NON-EMPTY -wal held by a LIVE writer (uncheckpointed tail, -shm present)")
        w = real_connect(db)
        w.execute("PRAGMA wal_autocheckpoint=0")
        w.execute("INSERT INTO reserved_pool VALUES (?, ?, ?)", (other, "history", 2))
        w.commit()
        try:
            state = sidecars(db)
            check((state["-wal"] or 0) > 0, "precondition: the -wal is non-empty (%s)" % state)
            expect_refusal(db, "a live writer's non-empty -wal")
        finally:
            w.close()

        print("case 5: WAL-mode DB, NON-EMPTY -wal left by a CRASHED writer, with NO -shm")
        crashed = os.path.join(dirs["d"], "synthetic_pool.db")
        make_db(crashed, "WAL")
        subprocess.run([sys.executable, "-c", _CRASHED_WAL_WRITER, crashed], check=True)
        wal_view = os.path.join(dirs["c"], "synthetic_pool.db")
        shutil.copyfile(crashed, wal_view)
        shutil.copyfile(crashed + "-wal", wal_view + "-wal")
        if os.path.exists(crashed + "-shm"):
            os.remove(crashed + "-shm")
        state = sidecars(crashed)
        check((state["-wal"] or 0) > 0 and state["-shm"] is None,
              "precondition: non-empty -wal and no -shm beside it (%s)" % state)
        expect_refusal(crashed, "a crashed writer's non-empty -wal with no -shm")
        sql = "SELECT COUNT(*) FROM reserved_pool"
        n_imm = raw_count("file:%s?mode=ro&immutable=1" % crashed.replace("\\", "/"), sql)
        n_wal = raw_count("file:%s?mode=ro" % wal_view.replace("\\", "/"), sql)
        print("  rows: immutable view %d, WAL-inclusive mode=ro view (on a copy) %d" % (n_imm, n_wal))
        check(n_imm != n_wal and n_wal - n_imm == 50,
              "the refusal guards a real divergence: the immutable view misses the 50-row WAL tail")

        print("case 6: ROLLBACK-mode DB, HOT -journal left by a crashed writer (uncommitted pages spilled)")
        hot = os.path.join(dirs["e"], "synthetic_pool.db")
        mode = make_db(hot, "DELETE")
        w = real_connect(hot)
        w.executemany("INSERT INTO reserved_pool VALUES (?, ?, ?)", [("pbulk", "bulk", i) for i in range(1, 3001)])
        w.commit()
        w.close()
        subprocess.run([sys.executable, "-c", _CRASHED_ROLLBACK_WRITER, hot], check=True)
        state = sidecars(hot)
        check(mode == "delete" and header_mode(hot) == (1, 1) and (state["-journal"] or 0) > 0,
              "precondition: rollback-mode (journal_mode=%s, header %d/%d) with a non-empty -journal (%s)"
              % ((mode,) + header_mode(hot) + (state,)))
        expect_refusal(hot, "a crashed rollback writer's hot -journal")
        torn = raw_count("file:%s?mode=ro&immutable=1" % hot.replace("\\", "/"),
                         "SELECT COUNT(*) FROM reserved_pool WHERE question_id < 0")
        print("  immutable view (bypassing the guard): %d uncommitted negated rows" % torn)
        check(torn > 0, "the refusal guards a real divergence: an immutable read returns uncommitted pages")

        print("case 7: ROLLBACK-mode DB, a LIVE writer holding a transaction")
        live = os.path.join(dirs["f"], "synthetic_pool.db")
        make_db(live, "DELETE")
        w = real_connect(live, isolation_level=None)
        try:
            w.execute("BEGIN")
            w.execute("UPDATE reserved_pool SET question_id = question_id + 1000")
            state = sidecars(live)
            check((state["-journal"] or 0) > 0, "precondition: the live transaction's -journal is non-empty (%s)" % state)
            expect_refusal(live, "a live rollback writer's -journal")
        finally:
            w.execute("ROLLBACK")
            w.close()

        print("case 8: ROLLBACK-mode (journal_mode=DELETE) DB with NO -journal")
        rb = os.path.join(dirs["g"], "synthetic_pool.db")
        mode = make_db(rb, "DELETE")
        state = sidecars(rb)
        check(mode == "delete" and header_mode(rb) == (1, 1) and state == {"-wal": None, "-shm": None, "-journal": None},
              "precondition: rollback-mode (journal_mode=%s, header %d/%d), no sidecar (%s)"
              % ((mode,) + header_mode(rb) + (state,)))
        n0 = len(seen)
        conn, msg = None, None
        try:
            conn = open_ro(rb)
        except SystemExit as e:
            msg = "SystemExit: %s" % e
        except Exception as e:  # noqa: BLE001
            msg = "%s: %s" % (type(e).__name__, e)
        verified = None
        if conn is not None:
            try:
                verified = assert_frozen_pool(conn, expected)
            except BaseException as e:  # noqa: BLE001 - a SystemExit from the guard is a FAIL here
                msg = "%s: %s" % (type(e).__name__, e)
            finally:
                conn.close()
        print("  URI used: %s" % (seen[n0:] or ["<none>"])[0])
        check(conn is not None and msg is None, "ACCEPTED: a rollback-mode DB with no -journal (%s)" % (msg or "opened"))
        check(len(seen) - n0 == 1 and seen[n0] == "file:%s?mode=ro&immutable=1" % os.path.abspath(rb).replace("\\", "/"),
              "exactly one connect, URI = file:<abs path>?mode=ro&immutable=1 (connects: %d)" % (len(seen) - n0))
        check(verified == expected, "assert_frozen_pool verifies %s on the rollback-mode DB" % expected)
        check(sidecars(rb) == state, "no sidecar created (%s)" % sidecars(rb))

        print("case 9: TRUNCATE-mode DB with a 0-byte -journal (the state a clean TRUNCATE commit leaves)")
        tr = os.path.join(dirs["h"], "synthetic_pool.db")
        mode = make_db(tr, "TRUNCATE")
        state = sidecars(tr)
        check(mode == "truncate" and header_mode(tr) == (1, 1) and state["-journal"] == 0 and state["-wal"] is None,
              "precondition: TRUNCATE-mode (journal_mode=%s, header %d/%d) with a 0-byte -journal left by the commit (%s)"
              % ((mode,) + header_mode(tr) + (state,)))
        n0 = len(seen)
        rows9, msg = guarded_rows(tr, expected)
        print("  URI used: %s" % (seen[n0:] or ["<none>"])[0])
        check(rows9 is not None and compute_pool_id(rows9) == expected,
              "ACCEPTED: a 0-byte -journal; rows hash to %s (%s)" % (expected, msg or "ok"))
        check(len(seen) - n0 == 1, "exactly one connect (connects: %d)" % (len(seen) - n0))
        check(sidecars(tr) == state, "the 0-byte -journal is left as it was (%s)" % sidecars(tr))
    except Exception as e:  # noqa: BLE001 - an unexpected error is a FAIL, and the temp dir is still removed
        check(False, "unexpected %s: %s" % (type(e).__name__, e))
    finally:
        sqlite3.connect = real_connect
        gc.collect()  # release any connection the code under test leaked, so Windows lets the temp dir go (d72c790 D6)
        shutil.rmtree(tmp, ignore_errors=True)
        if os.path.exists(tmp):
            print("  [WARN] temp dir not fully removed (a handle is still open): %s" % tmp)
    print("python optimize flag = %d (the checks are explicit branches, not asserts)" % sys.flags.optimize)
    if failures:
        print("SELFTEST FAIL: %d of %d checks failed: %s" % (len(failures), n_checks[0], "; ".join(failures)))
        return 1
    print("SELFTEST PASS: %d/%d checks" % (n_checks[0], n_checks[0]))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--activate" in argv or "--activate-id" in argv:
        raise SystemExit("[POOL-GUARD] --activate is gone: there is no active pool. A build records its pool and switches "
                         "nothing; verify with `--pool <id>` and declare the pool in the run's TOML (`pool = \"<id>\"`).")
    if "--export-snapshot" in argv:
        i = argv.index("--export-snapshot")
        out = argv[argv.index("--out") + 1]
        export_snapshot(argv[i + 1], argv[i + 2], out)
        return 0
    if "--diff-flag" in argv:
        return 0 if diff_flag(argv[argv.index("--diff-flag") + 1]) == 0 else 1
    if "--pool" in argv:
        describe(argv[argv.index("--pool") + 1], db=_flag_value(argv, "--db"), id_file=_flag_value(argv, "--id-file"))
        return 0
    if "--db" in argv or "--id-file" in argv:
        raise SystemExit("[POOL-GUARD] --db / --id-file apply to --pool <id> only")
    print(__doc__)
    print("registry: " + ", ".join(sorted(load_registry())))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
