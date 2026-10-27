"""judge_v2.induce_cache_3: the ARCH-V2-INDUCE-RUBRIC-3 attempt cache (its OWN store; not a verdict store; no view file).

The schema IS judge_v2.induce_cache_2's (the -2 cache, left byte-identical: its blob 9edfc767... is part of the -2
instrument of record) with the substitutions the registration names (docs/judge_v2_program.md L17008-L17110, INSTRUMENT
FILES: "-2 DDL with asserted substitutions only; schema id archv2-induce-rubric-3-cache-v1"), each asserted:
  (1) the DDL: ZERO textual substitutions. The -3 formal-failure classes are the -2 ones (NON_JSON, KEY, LENGTH,
      CONTENT_FILTER, VERBATIM, FITNESS: a jv2-v5-4 failure is the class FITNESS), so the -2 DDL is used as it is; asserted
      to carry the -2 failure_class CHECK exactly once, and to be the -1 DDL with exactly that one -2 substitution;
  (2) SCHEMA_ID "archv2-induce-rubric-3-cache-v1" (was "archv2-induce-rubric-2-cache-v1"), so a -1 or -2 cache is never
      reopened as a -3 one and vice versa; asserted to differ from both.
Every other rule is induce_cache's, unchanged: create() makes a NEW file only (an existing path, -wal or -journal is
refused); append-only (UPDATE / DELETE abort on every table); the WRITE-AHEAD invocation row and its triggers (no
invocation after the first valid reply, no 4th attempt, no 4th transport error, no invocation while an orphan is
unresolved, numbering in order); state() is induce_cache.state.
"""
import os
import sqlite3

from . import induce_cache as _IC1
from . import induce_cache_2 as _IC2

SCHEMA_ID = "archv2-induce-rubric-3-cache-v1"
ORPHAN_NOTE = _IC2.ORPHAN_NOTE
_CHECK_2 = "failure_class IN ('NON_JSON','KEY','LENGTH','CONTENT_FILTER','VERBATIM','FITNESS')"
if _IC2.DDL.count(_CHECK_2) != 1 or _IC2.DDL != _IC1.DDL.replace(_IC2._OLD_CHECK, _IC2._NEW_CHECK) or \
        _IC1.DDL.count(_IC2._OLD_CHECK) != 1:
    raise SystemExit("[INDUCE-CACHE-3] induce_cache_2.DDL is not the -1 DDL with the one -2 substitution: refused")
if SCHEMA_ID in (_IC1.SCHEMA_ID, _IC2.SCHEMA_ID):
    raise SystemExit("[INDUCE-CACHE-3] the -3 schema id must differ from the -1 and -2 ones: refused")
DDL = _IC2.DDL
state = _IC1.state


def _refuse(msg):
    raise SystemExit("[INDUCE-CACHE-3] " + msg)


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
        _refuse("%s is not an ARCH-V2-INDUCE-RUBRIC-3 attempt cache" % ap)
    conn.execute("PRAGMA journal_mode=DELETE")
    return conn
