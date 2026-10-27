"""judge_v2.induce_cache: the ARCH-V2-INDUCE-RUBRIC-1 attempt cache (its OWN store; not a verdict store; no view file).

create(path, meta)   a NEW file only (refuses an existing path, -wal or -journal), the DDL below, the meta rows
reopen(path)         an EXISTING cache of this schema (a relaunch; the caller checks the state); refuses another file
APPEND-ONLY: UPDATE / DELETE abort on every table.

WRITE-AHEAD INVOCATION RECORD (READY_induce_rubric_1 C1, 6b65efe): before EVERY call_judge_full the runner inserts and
commits an `invocation` row (seq, payload sha, PENDING). The triggers sit on THAT row, so the store REFUSES THE INVOCATION
ITSELF, before anything is posted, when:
  - a valid reply already exists (no call after the first valid reply: no best-of-n, no retry on a valid reply);
  - 3 attempts exist (no 4th attempt);
  - 3 transport errors exist (no call after UNDETERMINED BY INSTRUMENT);
  - an earlier invocation is still unresolved (an ORPHAN: posted, no reply and no error recorded);
  - the seq is not the next one.
Each invocation is then RESOLVED by exactly one row: an `attempt` (a reply was returned) or a `transport` row (the call
raised; or, found on a relaunch, an orphan: "TRANSPORT, no reply recorded (orphan invocation)", which consumes the
transport limit and is disclosed). Both reference invocation_seq (UNIQUE) and are refused for an unknown or already
resolved invocation.
Tables: meta; invocation; attempt; transport; event (the ordered witness: launch, reply_committed, eval_view_opened...).
"""
import os
import sqlite3

SCHEMA_ID = "archv2-induce-rubric-1-cache-v2"
ORPHAN_NOTE = "TRANSPORT, no reply recorded (orphan invocation)"

DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE invocation (seq INTEGER PRIMARY KEY CHECK (seq BETWEEN 1 AND 6), created_at TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL, status TEXT NOT NULL CHECK (status = 'PENDING'));
CREATE TABLE attempt (attempt_no INTEGER PRIMARY KEY CHECK (attempt_no BETWEEN 1 AND 3),
    invocation_seq INTEGER NOT NULL UNIQUE REFERENCES invocation(seq), posted_at TEXT NOT NULL,
    committed_at TEXT NOT NULL, payload_sha256 TEXT NOT NULL, body_zlib BLOB NOT NULL, reply_text TEXT, reply_sha256 TEXT,
    finish_reason TEXT, response_id TEXT, provider TEXT, completion_tokens INTEGER, latency_s REAL, failure_class TEXT
    CHECK (failure_class IS NULL OR failure_class IN ('NON_JSON','KEY','LENGTH','CONTENT_FILTER','VERBATIM')));
CREATE TABLE transport (seq INTEGER PRIMARY KEY CHECK (seq BETWEEN 1 AND 3),
    invocation_seq INTEGER NOT NULL UNIQUE REFERENCES invocation(seq), at TEXT NOT NULL, payload_sha256 TEXT NOT NULL,
    exception_class TEXT NOT NULL, message TEXT NOT NULL,
    note TEXT NOT NULL CHECK (note IN ('TRANSPORT, no reply', 'TRANSPORT, no reply recorded (orphan invocation)')));
CREATE TABLE event (seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, what TEXT NOT NULL, detail TEXT);
CREATE VIEW unresolved AS SELECT i.seq FROM invocation i
    WHERE NOT EXISTS (SELECT 1 FROM attempt a WHERE a.invocation_seq = i.seq)
      AND NOT EXISTS (SELECT 1 FROM transport t WHERE t.invocation_seq = i.seq);
CREATE TRIGGER invocation_after_valid BEFORE INSERT ON invocation
    WHEN EXISTS (SELECT 1 FROM attempt WHERE failure_class IS NULL)
    BEGIN SELECT RAISE(ABORT, 'induce cache: no invocation after the first valid reply'); END;
CREATE TRIGGER invocation_attempt_cap BEFORE INSERT ON invocation
    WHEN (SELECT COUNT(*) FROM attempt) >= 3
    BEGIN SELECT RAISE(ABORT, 'induce cache: 3 attempts exist; no further invocation'); END;
CREATE TRIGGER invocation_transport_cap BEFORE INSERT ON invocation
    WHEN (SELECT COUNT(*) FROM transport) >= 3
    BEGIN SELECT RAISE(ABORT, 'induce cache: 3 transport errors exist (UNDETERMINED BY INSTRUMENT); no further invocation'); END;
CREATE TRIGGER invocation_no_orphan BEFORE INSERT ON invocation
    WHEN EXISTS (SELECT 1 FROM unresolved)
    BEGIN SELECT RAISE(ABORT, 'induce cache: an earlier invocation is unresolved (orphan); resolve it first'); END;
CREATE TRIGGER invocation_in_order BEFORE INSERT ON invocation
    WHEN NEW.seq != (SELECT COUNT(*) FROM invocation) + 1
    BEGIN SELECT RAISE(ABORT, 'induce cache: invocations are numbered in order'); END;
CREATE TRIGGER attempt_resolves BEFORE INSERT ON attempt
    WHEN NOT EXISTS (SELECT 1 FROM unresolved WHERE seq = NEW.invocation_seq)
    BEGIN SELECT RAISE(ABORT, 'induce cache: an attempt must resolve an unresolved invocation'); END;
CREATE TRIGGER transport_resolves BEFORE INSERT ON transport
    WHEN NOT EXISTS (SELECT 1 FROM unresolved WHERE seq = NEW.invocation_seq)
    BEGIN SELECT RAISE(ABORT, 'induce cache: a transport row must resolve an unresolved invocation'); END;
CREATE TRIGGER attempt_after_valid BEFORE INSERT ON attempt
    WHEN EXISTS (SELECT 1 FROM attempt WHERE failure_class IS NULL)
    BEGIN SELECT RAISE(ABORT, 'induce cache: no attempt after the first valid reply'); END;
CREATE TRIGGER attempt_in_order BEFORE INSERT ON attempt
    WHEN NEW.attempt_no != (SELECT COUNT(*) FROM attempt) + 1
    BEGIN SELECT RAISE(ABORT, 'induce cache: attempts are numbered 1, 2, 3 in order'); END;
CREATE TRIGGER transport_in_order BEFORE INSERT ON transport
    WHEN NEW.seq != (SELECT COUNT(*) FROM transport) + 1
    BEGIN SELECT RAISE(ABORT, 'induce cache: transport errors are numbered 1, 2, 3 in order'); END;
"""
for _t in ("meta", "invocation", "attempt", "transport", "event"):
    DDL += ("CREATE TRIGGER %(t)s_no_update BEFORE UPDATE ON %(t)s BEGIN SELECT RAISE(ABORT, 'induce cache is append-only');"
            " END;\nCREATE TRIGGER %(t)s_no_delete BEFORE DELETE ON %(t)s BEGIN SELECT RAISE(ABORT, 'induce cache is"
            " append-only'); END;\n") % {"t": _t}


def _refuse(msg):
    raise SystemExit("[INDUCE-CACHE] " + msg)


def create(path, meta):
    ap = os.path.abspath(path)
    for p in (ap, ap + "-wal", ap + "-journal"):
        if os.path.exists(p):
            _refuse("%s exists: the attempt cache is created once" % p)
    if not os.path.isdir(os.path.dirname(ap)):
        _refuse("directory %s does not exist" % os.path.dirname(ap))
    conn = sqlite3.connect(ap)
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.executescript(DDL)
    rows = dict(meta)
    rows["schema_id"] = SCHEMA_ID
    for k in sorted(rows):
        conn.execute("INSERT INTO meta VALUES (?,?)", (k, str(rows[k])))
    conn.commit()
    return conn


def reopen(path):
    ap = os.path.abspath(path)
    if not os.path.isfile(ap):
        _refuse("%s does not exist" % ap)
    conn = sqlite3.connect(ap)
    sid = conn.execute("SELECT value FROM meta WHERE key='schema_id'").fetchone()
    if sid is None or sid[0] != SCHEMA_ID:
        conn.close()
        _refuse("%s is not an ARCH-V2-INDUCE-RUBRIC-1 attempt cache" % ap)
    conn.execute("PRAGMA journal_mode=DELETE")
    return conn


def state(conn):
    meta = dict(conn.execute("SELECT key, value FROM meta"))
    attempts = conn.execute("SELECT attempt_no, failure_class FROM attempt ORDER BY attempt_no").fetchall()
    n_transport = conn.execute("SELECT COUNT(*) FROM transport").fetchone()[0]
    n_invocations = conn.execute("SELECT COUNT(*) FROM invocation").fetchone()[0]
    orphans = [s for (s,) in conn.execute("SELECT seq FROM unresolved ORDER BY seq")]
    return {"meta": meta, "attempts": attempts, "n_attempts": len(attempts), "n_transport": n_transport,
            "n_invocations": n_invocations, "orphans": orphans, "valid": any(c is None for _a, c in attempts)}
