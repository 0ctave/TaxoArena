"""zc_common: shared plumbing of the three zero-call readouts SITE-SUPPORT, TREE-LIKE and SCALE-AGREE (2026-10-04).

Zero judge calls; opens no database of record for writing; writes only (a) staged copies under the process's scratch dir
on E: (scratch_dir) and (b) write-once outcome files under E:/TaxoArena_backup_<date>_<tag>/ (mode "x").

API
  ROOT                     the checkout holding this file (the scripts' default data root and the committed configs)
  refuse(tag, msg)         prints "<tag> REFUSED: msg" and raises Refused (SystemExit 2): a failed precondition, never an outcome
  git_blob(path)           git hash-object of the LF rendering (LF is of record; CRLF working trees under autocrlf)
  script_pins(path)        blob / sha256-lf16 / sha256-crlf16 of a script (the LF pins are of record, CRLF beside)
  sha256_file(path)        streamed sha256 of the file bytes
  stage_db(src, dest_dir)  COPY-BEFORE-READ (the orchestrator's brief, 2026-10-04: "copy db+wal before reading working copies"):
                           REFUSES a missing file or a non-empty -journal (a rollback writer's live / hot transaction); copies
                           the DB and, when non-empty, its -wal into dest_dir (never over an existing path); REFUSES when the
                           source DB or -wal changed (size or mtime_ns) during the copy; hashes the copy BEFORE any
                           checkpoint (= the source bytes, the hash the registrar's pins name); when a -wal was copied, folds
                           it into the COPY (read-write open of the copy only, wal_checkpoint(TRUNCATE), journal_mode=DELETE)
                           so the copy is self-contained; the source is only ever read. -> dict(src, path, sha256, bytes,
                           wal_bytes).
  open_ro(path)            sqlite3 connect mode=ro&immutable=1 after the -wal / -journal check (used on staged copies)
  write_once(path, text)   REFUSES when the path or the SHA256SUMS.txt beside it exists; writes both with mode "x"
  default_out(tag, name)   E:/TaxoArena_backup_<date>_<tag>/<name>
  capture(fn, *a)          (rc, stdout) with a Refused turned into ("refused", code), any other SystemExit into ("exit", msg)
  line(text, prefix)       the unique line starting with prefix (assert)
  quantile_strata(ns)      CERT-ALIGN-SIZE's size quintiles: cutpoints np.quantile(log n, .2/.4/.6/.8); stratum = number of
                           cutpoints strictly below log n
  run_mutants(...)         the mutant harness: each mutant is a (id, description, old, new) text replacement applied to a COPY
                           of the script inside a scratch dir (the old text must occur exactly once), the copy's --selftest run
                           in a child with TMP / TEMP / TMPDIR / TAXOARENA_TMP inside the sandbox; KILLED iff the child exits
                           non-zero. The original file is never edited.

SELFTEST (python tools/analysis/zc_common.py --selftest): stage_db on a WAL-mode fixture whose committed rows live only in its
-wal (the copy must carry them and the source -wal must be untouched), the -journal refusal, the changed-source refusal, the
never-overwrite refusal; write_once and its SHA256SUMS; quantile_strata at its boundaries. Mutants (final run 2026-10-04, copies
in a scratch sandbox): the 7 in MUTANTS below, 7 / 7 KILLED on this code.
"""
import datetime
import hashlib
import io
import os
import shutil
import sqlite3
import subprocess
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ZC_REPO_ROOT") or os.path.dirname(os.path.dirname(HERE))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import scratch_dir  # noqa: E402  TEMP-SPRAWL: temp on E:, removed at exit

MUTANTS = [
    ("Z1", "stage_db does not refuse a non-empty -journal", "    if os.path.exists(j) and os.path.getsize(j) > 0:\n", "    if False:\n"),
    ("Z2", "stage_db does not copy the -wal", "        shutil.copyfile(wal, dst + \"-wal\")\n", "        pass\n"),
    ("Z3", "stage_db does not compare the source stat before / after", "    if st0 != st1:\n", "    if False:\n"),
    ("Z4", "stage_db overwrites an existing copy", "    if os.path.lexists(dst) or os.path.lexists(dst + \"-wal\"):\n", "    if False:\n"),
    ("Z5", "write_once has no existence refusal", "            refuse(tag, \"%s exists: the outcome", "            0 and refuse(tag, \"%s exists: the outcome"),
    ("Z6", "quantile strata count cutpoints <= log n", "    return int(sum(1 for c in cuts if c < ln))\n", "    return int(sum(1 for c in cuts if c <= ln))\n"),
    ("Z7", "the copy is hashed AFTER the checkpoint (not the source bytes)", "    sha = sha256_file(dst)\n    if wal_bytes:\n", "    sha = None\n    if wal_bytes:\n"),
]


class Refused(SystemExit):
    pass


def refuse(tag, msg):
    print("%s REFUSED: %s" % (tag, msg))
    raise Refused(2)


def git_blob(path):
    with open(path, "rb") as f:
        b = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def script_pins(path):
    with open(path, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return dict(blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(), lf16=hashlib.sha256(lf).hexdigest()[:16],
                crlf16=hashlib.sha256(crlf).hexdigest()[:16])


def pins_line(path):
    p = script_pins(path)
    return "script %s blob:%s sha256-lf16:%s (LF rendering, of record; sha256-crlf16:%s beside)" % (
        os.path.basename(path), p["blob"], p["lf16"], p["crlf16"])


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _stat(p):
    if not os.path.exists(p):
        return None
    s = os.stat(p)
    return (s.st_size, s.st_mtime_ns)


def stage_db(src, dest_dir, tag="[ZC]", _hook=None):
    """Copy-before-read of a working-copy DB (see the module docstring). _hook(src) runs between the copy and the second stat
    (selftest only: it simulates a writer)."""
    if not os.path.isfile(src):
        refuse(tag, "%s not found" % src)
    j = src + "-journal"
    if os.path.exists(j) and os.path.getsize(j) > 0:
        refuse(tag, "%s is non-empty (%d bytes): a rollback-mode writer's transaction is live or hot; nothing copied"
               % (j, os.path.getsize(j)))
    wal = src + "-wal"
    os.makedirs(dest_dir, exist_ok=True)
    dst = os.path.join(dest_dir, os.path.basename(src))
    if os.path.lexists(dst) or os.path.lexists(dst + "-wal"):
        refuse(tag, "staged copy %s exists: a copy is never overwritten" % dst)
    st0 = (_stat(src), _stat(wal))
    shutil.copyfile(src, dst)
    wal_bytes = os.path.getsize(wal) if os.path.exists(wal) else 0
    if wal_bytes:
        shutil.copyfile(wal, dst + "-wal")
    if _hook is not None:
        _hook(src)
    st1 = (_stat(src), _stat(wal))
    if st0 != st1:
        for p in (dst, dst + "-wal"):
            if os.path.exists(p):
                os.remove(p)
        refuse(tag, "%s (or its -wal) changed during the copy (%s -> %s): a writer is active; wait (rule 7)" % (src, st0, st1))
    sha = sha256_file(dst)
    if wal_bytes:
        con = sqlite3.connect(dst)
        try:
            con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            con.execute("PRAGMA journal_mode=DELETE")
        finally:
            con.close()
    for sfx in ("-wal", "-journal"):
        if os.path.exists(dst + sfx) and os.path.getsize(dst + sfx) > 0:
            refuse(tag, "staged copy %s%s is non-empty after the checkpoint" % (dst, sfx))
    return dict(src=src, path=dst, sha256=sha, bytes=os.path.getsize(src), wal_bytes=wal_bytes)


def open_ro(path, tag="[ZC]"):
    if not os.path.isfile(path):
        refuse(tag, "%s not found" % path)
    for sfx in ("-wal", "-journal"):
        if os.path.exists(path + sfx) and os.path.getsize(path + sfx) > 0:
            refuse(tag, "%s%s is non-empty: an immutable read would hide it" % (path, sfx))
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % os.path.abspath(path).replace("\\", "/"), uri=True)


def default_out(tag, name):
    return os.path.join("E:/TaxoArena_backup_%s_%s" % (datetime.date.today().isoformat(), tag), name)


def write_once(path, text, tag="[ZC]"):
    sums = os.path.join(os.path.dirname(os.path.abspath(path)), "SHA256SUMS.txt")
    for p in (path, sums):
        if os.path.exists(p):
            refuse(tag, "%s exists: the outcome of record is WRITE-ONCE (never overwritten, never re-run over)" % p)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    h = sha256_file(path)
    with open(sums, "x", encoding="utf-8", newline="\n") as f:
        f.write("%s  %s\n" % (h, os.path.basename(path)))
    return h, sums


def capture(fn, *a, **k):
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            rc = fn(*a, **k)
        except Refused as e:
            rc = ("refused", e.code)
        except SystemExit as e:            # another guard's refusal (pool_guard raises SystemExit("[POOL-GUARD] ..."))
            rc = ("exit", str(e.code))
    return rc, buf.getvalue()


def line(text, prefix):
    ls = [l for l in text.splitlines() if l.startswith(prefix)]
    assert len(ls) == 1, (prefix, ls[:3], len(ls))
    return ls[0]


def quantile_cuts(ns):
    import numpy as np
    return [float(c) for c in np.quantile(np.log(np.asarray(ns, dtype=float)), [0.2, 0.4, 0.6, 0.8])]


def quantile_stratum(n, cuts):
    import math
    ln = math.log(n)
    return int(sum(1 for c in cuts if c < ln))


def in_band(x, band):
    return bool(x is not None and band[0] <= x <= band[1])


def brier(prob, occurred):
    return (prob - (1.0 if occurred else 0.0)) ** 2


# --------------------------------------------------------------------------------------------- mutant harness
def run_mutants(script_path, mutants, extra_args=("--selftest",), timeout=3600, out=print):
    """Each mutant: copy the script into a sandbox, apply the replacement (old must occur exactly once), run the copy's
    selftest with PYTHONPATH = tools/analysis and TMP / TEMP / TMPDIR / TAXOARENA_TMP inside the sandbox. KILLED iff rc != 0.
    Returns [(id, desc, 'killed' | 'SURVIVED', tail)]."""
    src = open(script_path, encoding="utf-8").read()
    res = []
    with scratch_dir.scratch("zc_mutants") as box:
        for mid, desc, old, new in mutants:
            n = src.count(old)
            if n != 1:
                res.append((mid, desc, "NOT APPLIED (old text occurs %d times)" % n, ""))
                out("  %-4s %-70s NOT APPLIED (%d occurrences)" % (mid, desc[:70], n))
                continue
            d = os.path.join(box, mid)
            os.makedirs(os.path.join(d, "tmp"))
            p = os.path.join(d, os.path.basename(script_path))
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(src.replace(old, new))
            env = dict(os.environ)
            env["PYTHONPATH"] = HERE + os.pathsep + env.get("PYTHONPATH", "")
            env["ZC_REPO_ROOT"] = ROOT
            for v in ("TMP", "TEMP", "TMPDIR", "TAXOARENA_TMP"):
                env[v] = os.path.join(d, "tmp")
            try:
                cp = subprocess.run([sys.executable, p] + list(extra_args), env=env, capture_output=True, text=True,
                                    timeout=timeout, encoding="utf-8", errors="replace")
                rc, tail = cp.returncode, (cp.stdout + cp.stderr).strip().splitlines()[-1:] or [""]
            except subprocess.TimeoutExpired:
                rc, tail = "timeout", ["timeout"]
            verdict = "killed" if rc != 0 else "SURVIVED"
            res.append((mid, desc, verdict, tail[0][:160]))
            out("  %-4s %-70s %s  (%s)" % (mid, desc[:70], verdict, tail[0][:110]))
    k = sum(1 for r in res if r[2] == "killed")
    out("  %d / %d killed" % (k, len(res)))
    return res


# --------------------------------------------------------------------------------------------- selftest
def selftest():
    checks = 0
    with scratch_dir.scratch("zc_common_selftest") as tmp:
        # a WAL-mode DB whose last committed rows live only in the -wal (no checkpoint: autocheckpoint off, connection held)
        src_dir = os.path.join(tmp, "src")
        os.makedirs(src_dir)
        src = os.path.join(src_dir, "w.db")
        con = sqlite3.connect(src)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA wal_autocheckpoint=0")
        con.execute("CREATE TABLE t (x INTEGER)")
        con.commit()
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        con.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(50)])
        con.commit()
        assert os.path.getsize(src + "-wal") > 0
        src_bytes = open(src, "rb").read(); wal_bytes = open(src + "-wal", "rb").read()
        info = stage_db(src, os.path.join(tmp, "copy1"))
        c2 = open_ro(info["path"])
        n = c2.execute("SELECT count(*) FROM t").fetchone()[0]
        c2.close()
        assert n == 50, n; checks += 1                                                    # Z2
        assert info["wal_bytes"] == len(wal_bytes) and info["sha256"] == hashlib.sha256(src_bytes).hexdigest(), info; checks += 1   # Z7
        assert open(src, "rb").read() == src_bytes and open(src + "-wal", "rb").read() == wal_bytes; checks += 1
        rc, txt = capture(stage_db, src, os.path.join(tmp, "copy1"))
        assert rc == ("refused", 2) and "is never overwritten" in txt, txt; checks += 1     # Z4

        def writer(p):
            with open(p, "ab") as f:
                f.write(b"\0" * 4096)
        rc, txt = capture(stage_db, src, os.path.join(tmp, "copy2"), "[ZC]", writer)
        assert rc == ("refused", 2) and "changed during the copy" in txt and not os.path.exists(os.path.join(tmp, "copy2", "w.db")), txt; checks += 1   # Z3
        con.close()
        jsrc = os.path.join(tmp, "j.db")
        sqlite3.connect(jsrc).close()
        open(jsrc + "-journal", "wb").write(b"x" * 10)
        rc, txt = capture(stage_db, jsrc, os.path.join(tmp, "copy3"))
        assert rc == ("refused", 2) and "j.db-journal is non-empty (10 bytes)" in txt, txt; checks += 1    # Z1
        # write_once
        out = os.path.join(tmp, "o", "outcome.txt")
        h, sums = write_once(out, "a\nb\n")
        assert open(sums, encoding="utf-8").read() == "%s  outcome.txt\n" % h; checks += 1
        rc, txt = capture(write_once, out, "c\n")
        assert rc == ("refused", 2) and "WRITE-ONCE" in txt and open(out, encoding="utf-8").read() == "a\nb\n"; checks += 1   # Z5
        # quantile strata: a value equal to a cutpoint is NOT above it
        cuts = quantile_cuts([1, 2, 3, 4, 5, 6])          # positions q x 5 are integers: cuts = log 2, log 3, log 4, log 5 exactly
        assert quantile_stratum(2, cuts) == 0 and quantile_stratum(3, cuts) == 1 and quantile_stratum(6, cuts) == 4; checks += 1   # Z6
    print("[ZC] SELFTEST OK: %d value-asserting checks" % checks)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--mutants" in sys.argv:
        r = run_mutants(os.path.abspath(__file__), MUTANTS)
        sys.exit(0 if all(x[2] == "killed" for x in r) else 1)
    print(__doc__)
