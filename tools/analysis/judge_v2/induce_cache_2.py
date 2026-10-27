"""judge_v2.induce_cache_2: the ARCH-V2-INDUCE-RUBRIC-2 attempt cache (its OWN store; not a verdict store; no view file).

The schema IS judge_v2.induce_cache's (the -1 cache, left byte-identical: its blob is part of the -1 instrument of record)
with EXACTLY two textual substitutions, each asserted to occur once:
  (1) the attempt.failure_class CHECK admits the new formal-failure class 'FITNESS' (V5; the registration: a V5 failure is
      a FORMAL FAILURE that consumes an attempt);
  (2) SCHEMA_ID "archv2-induce-rubric-2-cache-v1", so a -1 cache is never reopened as a -2 one and vice versa.
Every other rule is induce_cache's, unchanged: create() makes a NEW file only (an existing path, -wal or -journal is
refused); append-only (UPDATE / DELETE abort on every table); the WRITE-AHEAD invocation row and its triggers (no
invocation after the first valid reply, no 4th attempt, no 4th transport error, no invocation while an orphan is
unresolved, numbering in order); state() is induce_cache.state.
"""
import os
import sqlite3

from . import induce_cache as _IC1

SCHEMA_ID = "archv2-induce-rubric-2-cache-v1"
ORPHAN_NOTE = _IC1.ORPHAN_NOTE
_OLD_CHECK = "failure_class IN ('NON_JSON','KEY','LENGTH','CONTENT_FILTER','VERBATIM')"
_NEW_CHECK = "failure_class IN ('NON_JSON','KEY','LENGTH','CONTENT_FILTER','VERBATIM','FITNESS')"
if _IC1.DDL.count(_OLD_CHECK) != 1:
    raise SystemExit("[INDUCE-CACHE-2] induce_cache.DDL does not carry the -1 failure_class CHECK exactly once: refused")
DDL = _IC1.DDL.replace(_OLD_CHECK, _NEW_CHECK)
state = _IC1.state


def _refuse(msg):
    raise SystemExit("[INDUCE-CACHE-2] " + msg)


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
        _refuse("%s is not an ARCH-V2-INDUCE-RUBRIC-2 attempt cache" % ap)
    conn.execute("PRAGMA journal_mode=DELETE")
    return conn
