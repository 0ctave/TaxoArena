"""data_v2.ro: the ONE place in the v2 data layer that calls sqlite3.connect (ARCH-v2 E-D; data §3 "Read-only analysis layer").

Three openers; nothing else in tools/analysis/data_v2 connects (lint_connect.py enforces it for this package and counts the
rest of tools/ without changing it):
  open_ro(path)          read-only, for ANY DB (a DB of record included): the -wal and the -journal beside it are checked
                         first and a non-empty one is REFUSED (an immutable read would hide a WAL tail or read a live
                         rollback writer's pages: the pool_guard.open_ro rule, restated here so this package imports no
                         pinned blob), then mode=ro&immutable=1, then PRAGMA query_only=1. With expect_sha256 the file
                         bytes are hashed first and a mismatch is refused; with require_sealed the DB must carry a v2 seal
                         row and be read-only on disk.
  create_new(path)       a NEW file only (write-once): refuses when the path, its -wal or its -journal exists. It is the
                         only way the v2 builders get a writable handle, so they cannot write into any existing DB.
  open_run_writer(path)  re-opens an EXISTING, UNSEALED v2 verdict DB for append (a relaunch). The file is first opened
                         read-only and must carry schema_id = taxoarena-verdict-v2 and no seal row. Any other DB (a DB of
                         record) is refused before a writable connection exists.

Every refusal is an explicit raise SystemExit("[DATA-V2-RO] ..."), never an assert (the guards hold under python -O).

Helpers:
  file_sha256            sha256 of the file bytes (hash kind sha256-bytes).
  git_blob_lf            the git blob id of a file's LF rendering (hash kind blob; CONTEXT rule 8).
  table_sha              sha256 over one table's rows ordered by its primary key, repr + LF per row (hash kind table-sha).
  seal(conn, path)       inserts the seal row carrying the per-table shas, checkpoints, sets journal_mode=DELETE, closes,
                         chmods the file read-only and returns sha256-bytes.
"""
import hashlib
import json
import os
import sqlite3
import stat

SEAL_TABLE = "v2_seal"
RUN_SCHEMA_ID = "taxoarena-verdict-v2"


def _refuse(msg):
    raise SystemExit("[DATA-V2-RO] " + msg)


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_lf(path):
    """git's blob id of the LF rendering of a text file (CRLF -> LF), i.e. `git hash-object` under autocrlf."""
    with open(path, "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha256_lf16(path):
    with open(path, "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:16]


def sidecars_empty(path):
    ap = os.path.abspath(path)
    for suffix in ("-wal", "-journal"):
        p = ap + suffix
        if os.path.exists(p) and os.path.getsize(p) > 0:
            _refuse("%s is non-empty (%d bytes): an immutable read would hide a WAL tail or read a live writer's pages;"
                    " stop the writer or have the data-steward checkpoint it, then re-run" % (p, os.path.getsize(p)))


def _uri(path):
    p = os.path.abspath(path).replace("\\", "/")
    if not p.startswith("/"):
        p = "/" + p
    return "file:%s?mode=ro&immutable=1" % p


def open_ro(path, expect_sha256=None, require_sealed=False):
    if not os.path.isfile(path):
        _refuse("database not found: %s (set TAXOARENA_DATA_ROOT)" % path)
    sidecars_empty(path)
    if expect_sha256 is not None:
        got = file_sha256(path)
        if got != expect_sha256:
            _refuse("%s: sha256 %s != the pinned %s" % (path, got, expect_sha256))
    conn = sqlite3.connect(_uri(path), uri=True)
    conn.execute("PRAGMA query_only=1")
    if require_sealed:
        if not is_sealed(conn):
            conn.close()
            _refuse("%s is not sealed (no %s row): an unsealed v2 DB is readable only by its writer" % (path, SEAL_TABLE))
        if os.access(path, os.W_OK):
            conn.close()
            _refuse("%s carries a seal row but is writable on disk: refused" % path)
    return conn


def is_sealed(conn):
    t = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (SEAL_TABLE,)).fetchone()
    if t is None:
        return False
    return conn.execute("SELECT COUNT(*) FROM %s" % SEAL_TABLE).fetchone()[0] > 0


def create_new(path):
    ap = os.path.abspath(path)
    for p in (ap, ap + "-wal", ap + "-journal"):
        if os.path.exists(p):
            _refuse("create_new: %s exists; v2 outputs are write-once and are never reopened for writing here" % p)
    d = os.path.dirname(ap)
    if not os.path.isdir(d):
        _refuse("create_new: directory %s does not exist" % d)
    conn = sqlite3.connect(ap)
    conn.execute("PRAGMA journal_mode=DELETE")
    return conn


def open_run_writer(path):
    if not os.path.isfile(path):
        _refuse("open_run_writer: %s does not exist (verdicts.VerdictStore.create starts a new run)" % path)
    c = open_ro(path)
    try:
        has_meta = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='run_meta'").fetchone()
        sid = c.execute("SELECT value FROM run_meta WHERE key='schema_id'").fetchone() if has_meta else None
        sealed = is_sealed(c)
    finally:
        c.close()
    if sid is None or sid[0] != RUN_SCHEMA_ID:
        _refuse("open_run_writer: %s is not a v2 verdict DB (schema_id %r); refused before any writable open" % (path, sid))
    if sealed:
        _refuse("open_run_writer: %s is SEALED; a sealed run is never appended to" % path)
    if not os.access(path, os.W_OK):
        _refuse("open_run_writer: %s is read-only on disk" % path)
    conn = sqlite3.connect(os.path.abspath(path))
    conn.execute("PRAGMA journal_mode=DELETE")
    return conn


def open_scratch_rw(path):
    """A read-write open of an EXISTING file under the system temporary directory ONLY (selftest fixtures). Any other
    path is refused, so this opener cannot reach a DB of record."""
    import tempfile
    tmp = os.path.normcase(os.path.realpath(tempfile.gettempdir())) + os.sep
    ap = os.path.normcase(os.path.realpath(path))
    if not ap.startswith(tmp):
        _refuse("open_scratch_rw: %s is not under the temporary directory %s" % (path, tmp))
    if not os.path.isfile(path):
        _refuse("open_scratch_rw: %s does not exist" % path)
    return sqlite3.connect(path)


def _pk_cols(conn, table):
    cols = conn.execute('PRAGMA table_info("%s")' % table).fetchall()
    pk = [c[1] for c in sorted(cols, key=lambda c: c[5]) if c[5] > 0]
    return pk or [c[1] for c in cols]


def table_sha(conn, table):
    order = ", ".join('"%s"' % c for c in _pk_cols(conn, table))
    h = hashlib.sha256()
    n = 0
    for row in conn.execute('SELECT * FROM "%s" ORDER BY %s' % (table, order)):
        h.update((repr(row) + "\n").encode("utf-8"))
        n += 1
    return h.hexdigest(), n


def user_tables(conn):
    return [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                                       " ORDER BY name")]


def table_shas(conn, exclude=(SEAL_TABLE,)):
    out = {}
    for t in user_tables(conn):
        if t in exclude:
            continue
        s, n = table_sha(conn, t)
        out[t] = {"table_sha": s, "rows": n}
    return out


SEAL_DDL = ("CREATE TABLE IF NOT EXISTS %s (only_row INTEGER PRIMARY KEY CHECK (only_row = 1), label TEXT NOT NULL,"
            " tables_json TEXT NOT NULL)" % SEAL_TABLE)


def seal(conn, path, label):
    """Seal a v2 DB built through create_new / open_run_writer: record the per-table shas in the seal row, checkpoint,
    journal_mode=DELETE, close, chmod read-only. Returns {"sha256_bytes", "tables"}. No wall-clock value is written into
    the DB, so a rebuild from the same inputs is byte-comparable."""
    shas = table_shas(conn)
    conn.execute(SEAL_DDL)
    conn.execute("INSERT INTO %s (only_row, label, tables_json) VALUES (1, ?, ?)" % SEAL_TABLE,
                 (label, json.dumps(shas, sort_keys=True)))
    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.close()
    sidecars_empty(path)
    os.chmod(path, stat.S_IREAD)
    return {"sha256_bytes": file_sha256(path), "tables": shas}
