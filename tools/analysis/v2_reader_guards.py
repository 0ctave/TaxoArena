"""v2_reader_guards: the guards shared by the two Wave-0 zero-call v2 key readers (ZERO judge calls; opens nothing itself).

USED BY tools/analysis/v2_declared_cells.py (V2-DECLARED-CELLS, RP03, legs U and M) and tools/analysis/k46_key_read.py
(K46-KEY-READ, RP04). Registrations: docs/judge_v2_program.md, sections "## Registered 2026-09-27 (before any code or
call) — V2-DECLARED-CELLS: ..." (L21582-L21614 as of a357ef0) and "## Registered 2026-09-27 (before any code or call) —
K46-KEY-READ: ..." (L21616-L21644 as of a357ef0); binding ruling docs/reviews/RULING_w0_seal_k46_reuse.md (c5a8cb6).

WHAT LIVES HERE (no statistic, no DB path, no numbers of record):
  script_identity(path)   the three hash kinds of CONTEXT rule 8: blob:<LF git blob> / sha256-lf16 / sha256-crlf16, and
                          which rendering the working tree holds (the LF rendering is of record).
  KeyTripwire(conn, ...)  a connection wrapper that REFUSES any SQL naming a column the ruling never admits for the reader
                          (FORBIDDEN, always) and any SQL naming a KEY column (is_correct, is_correct_mathfix, correct)
                          until unseal(reason) is called. Every refusal is raise SystemExit("[KEY-TRIPWIRE] ...") (python
                          -O safe). The executed SQL texts are logged, so an audit can list every statement a run sent.
  write_once(path, text)  opens mode "x" (a re-run cannot overwrite an outcome of record; pass-2 review defect 2).
  read_marker(path, txt)  the B1 one-read marker (ruling c5a8cb6 section 1, B1): written mode "x" BEFORE the EVAL key is
                          read; if it already exists the read is REFUSED (a second read needs a registration bracket and a
                          delta of the script first; the first read's outputs are kept).
  Branches                the print-branch registry: every registered criterion / prediction / falsifier branch calls
                          hit(name); the selftest asserts the executed set equals the declared set (TOPIC-PARTITION D1/D7).
  as_bool(x)              bool() of a computed value; a verdict is never identity-tested (numpy.bool_ is not True).
"""
import hashlib
import os
import re

KEY_COLUMNS = ("is_correct", "is_correct_mathfix", "correct")


def script_identity(path):
    """(blob, sha256-lf16, sha256-crlf16, rendering). blob = git's blob id of the LF rendering (`git hash-object` under
    core.autocrlf=true); lf16 / crlf16 = the first 16 hex of sha256 over the LF / CRLF bytes."""
    with open(path, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    blob = hashlib.sha1(b"blob %d\x00" % len(lf) + lf).hexdigest()
    rendering = "CRLF" if (raw == crlf and raw != lf) else "LF"
    return blob, hashlib.sha256(lf).hexdigest()[:16], hashlib.sha256(crlf).hexdigest()[:16], rendering


def identity_line(path, label=None):
    blob, lf16, crlf16, rend = script_identity(path)
    return "%s: blob:%s / sha256-lf16:%s / sha256-crlf16:%s (working tree holds the %s rendering; LF is of record)" % (
        label or os.path.basename(path), blob, lf16, crlf16, rend)


def as_bool(x):
    return bool(x)


class KeyTripwire:
    """Wrap a read-only sqlite3 connection. forbidden: column names never admitted for this reader (ruling c5a8cb6
    section 2 'never' column); key: the key columns, sealed until unseal(). The check is a word match on the SQL text
    (identifiers are matched case-insensitively as whole words), so a statement that merely names a sealed column is
    refused before it runs."""

    def __init__(self, conn, forbidden=(), key=KEY_COLUMNS, label=""):
        self._c = conn
        self._forbidden = tuple(forbidden)
        self._key = tuple(key)
        self.sealed = True
        self.label = label
        self.log = []
        self.unseal_reason = None

    @staticmethod
    def _names(sql, cols):
        return [c for c in cols if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(c), sql, re.I)]

    def execute(self, sql, params=()):
        # READY e451753 D10: a "*" select list would bypass the word match; refused (COUNT(*) is admitted)
        if re.search(r"(?:\bSELECT\s+(?:DISTINCT\s+)?|,\s*|\.)\*", sql, re.I):
            raise SystemExit("[KEY-TRIPWIRE] %s: a '*' select list is refused (name the columns): %r" % (self.label, sql[:160]))
        bad = self._names(sql, self._forbidden)
        if bad:
            raise SystemExit("[KEY-TRIPWIRE] %s: SQL names column(s) %s that ruling c5a8cb6 never admits for this reader:"
                             " %r" % (self.label, bad, sql[:160]))
        if self.sealed:
            k = self._names(sql, self._key)
            if k:
                raise SystemExit("[KEY-TRIPWIRE] %s: SQL names the KEY column(s) %s while the key is SEALED (dry-run, or"
                                 " before the preconditions / the B3 policy file): %r" % (self.label, k, sql[:160]))
        self.log.append(sql)
        return self._c.execute(sql, params)

    def unseal(self, reason):
        if not reason:
            raise SystemExit("[KEY-TRIPWIRE] %s: unseal needs a stated reason" % self.label)
        self.sealed = False
        self.unseal_reason = reason

    def close(self):
        self._c.close()


def write_once(path, text):
    """Mode "x": refuses (FileExistsError -> SystemExit) when the path exists."""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        raise SystemExit("[WRITE-ONCE] %s exists: outcome files of record are write-once; refused" % path)
    return path


def read_marker(path, text):
    """B1: the one-read marker, written mode "x" BEFORE the key is read."""
    if os.path.exists(path):
        raise SystemExit("[B1] %s exists: this leg has already read the EVAL key once (ruling c5a8cb6 B1). A re-run needs a"
                         " registration bracket and a delta of this script BEFORE it happens; the first read's outputs"
                         " are kept and disclosed beside the second. Refused." % path)
    return write_once(path, text)


class Branches:
    def __init__(self, declared):
        self.declared = frozenset(declared)
        self.hit_set = set()

    def hit(self, name):
        if name not in self.declared:
            raise SystemExit("[BRANCH] undeclared print branch %r" % name)
        self.hit_set.add(name)

    def missing(self):
        return sorted(self.declared - self.hit_set)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_state(path):
    """[(suffix, size or None)] for -wal / -journal / -shm beside path (printed; a non-empty -wal / -journal refuses in the
    opener, data_v2.ro.open_ro)."""
    out = []
    for s in ("-wal", "-journal", "-shm"):
        p = path + s
        out.append((s, os.path.getsize(p) if os.path.exists(p) else None))
    return out


def sidecar_line(path):
    return ", ".join("%s %s" % (s, "absent" if n is None else "%d bytes" % n) for s, n in sidecar_state(path))
