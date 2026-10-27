"""The connection discipline of archv2_arena.

  * every DB is opened through open_ro(): refused by NAME first (snapshots_frozen.db, any 20NG / twenty_newsgroups DB),
    then pool_guard.open_ro(), which REFUSES a non-empty -wal or -journal beside the DB before any connect and opens
    file:<abs>?mode=ro&immutable=1 (POOL-GUARD-IMMUTABLE, CONTEXT.md section 3);
  * install_global_guard() wraps sqlite3.connect for the whole process: only mode=ro&immutable=1 URIs and ':memory:'
    are admitted, so a recorded function that opens a DB any other way (a plain path, mode=ro without immutable) is
    refused instead of silently reading or writing;
  * Shim stands in for the sqlite3 module INSIDE recorded code (systematic_budget, rubric_512), translating its
    "file:<path>?mode=ro" URIs to open_ro(<path>);
  * LOG lists every admitted open (printed in every output).
Selftests create their synthetic DBs with REAL_CONNECT, the unwrapped function, in a temp dir.
"""
import os
import sqlite3

import pool_guard

REAL_CONNECT = sqlite3.connect
LOG = []                    # absolute paths admitted by open_ro, in order
REFUSED = []
_FORBIDDEN_EXACT = ("snapshots_frozen.db",)
_FORBIDDEN_PARTS = ("20ng", "twenty_newsgroups")


def forbidden(path):
    b = os.path.basename(str(path)).lower()
    return b in _FORBIDDEN_EXACT or any(p in b for p in _FORBIDDEN_PARTS)


def open_ro(path):
    if forbidden(path):
        REFUSED.append(str(path))
        raise SystemExit("[ARCHV2-RO] refused by name: %s is never opened by this instrument" % path)
    con = pool_guard.open_ro(path)          # the -wal / -journal refusal, then mode=ro&immutable=1
    LOG.append(os.path.abspath(path))
    return con


def _guarded_connect(database, *a, **k):
    if database == ":memory:":
        return REAL_CONNECT(database, *a, **k)
    if isinstance(database, str) and database.startswith("file:") and k.get("uri") \
            and database.endswith("?mode=ro&immutable=1"):
        path = database[5:].split("?", 1)[0]
        if forbidden(path):
            REFUSED.append(path)
            raise SystemExit("[ARCHV2-RO] refused by name: %s" % path)
        return REAL_CONNECT(database, *a, **k)
    REFUSED.append(str(database))
    raise SystemExit("[ARCHV2-RO] refused sqlite3.connect(%r, %r): only open_ro() (mode=ro&immutable=1 after the "
                     "-wal/-journal check) may open a DB in this process" % (database, k))


def install_global_guard():
    sqlite3.connect = _guarded_connect
    return _guarded_connect


def guard_installed():
    return sqlite3.connect is _guarded_connect


class Shim:
    """Stands in for the sqlite3 module inside recorded code: connect("file:<p>?mode=ro", uri=True) -> open_ro(<p>)."""

    def __init__(self):
        self.opens = 0

    def connect(self, target, *a, **k):
        if isinstance(target, str) and target.startswith("file:") and "mode=ro" in target:
            self.opens += 1
            return open_ro(target[5:].split("?", 1)[0])
        REFUSED.append(str(target))
        raise SystemExit("[ARCHV2-RO] recorded code tried a non-read-only open %r; refused" % (target,))

    def __getattr__(self, name):
        return getattr(sqlite3, name)


def log_lines():
    out = ["  DB OPENS (all through pool_guard.open_ro: -wal/-journal refused, then mode=ro&immutable=1): %d" % len(LOG)]
    for p in LOG:
        out.append("    %s" % p)
    if REFUSED:
        out.append("  REFUSED OPEN ATTEMPTS: %d: %s" % (len(REFUSED), "; ".join(REFUSED)))
    return out
