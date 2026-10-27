"""Safe WAL checkpoint for one allow-listed repo-root SQLite cache (ops tool, zero judge calls).

A narrow replacement for ad-hoc `python -c "...PRAGMA wal_checkpoint..."` one-liners, so that the
author can allow `Bash(python tools/ops/wal_checkpoint.py:*)` without allowing arbitrary SQL.
Background: every construction leaves a WAL tail in the caches (memory construction-writes-cache-dbs;
data-steward review docs/reviews/2026-09-20_cache_writes_by_construction.md); `immutable=1` readers miss
it, and whole-file shas move on every checkpoint, so content is pinned PER TABLE.

    python tools/ops/wal_checkpoint.py --db embeddings_cache.db             # checkpoint
    python tools/ops/wal_checkpoint.py --db embeddings_cache.db --dry-run   # everything but the checkpoint
    python tools/ops/wal_checkpoint.py --selftest                           # temp DBs only

Sequence (each step refuses, exit 2, with a `[wal-ckpt] REFUSED:` line naming the reason):
  1. `--db` must be a bare file name on the hard-coded allow-list (ALLOWED_FIXED, or ALLOWED_PATTERN for
     the intent_emb_*.db working copies), the file must exist at the repo root, resolve INSIDE the repo
     root (no symlink, no separator, no `..`), and be a regular file. There is no --root flag: the
     root is this file's grand-parent directory.
  2. No java.exe / javaw.exe / gradle* process may be running (tasklist; a tasklist failure refuses).
  3. Exclusive-open probe: CreateFileW with share mode 0 on the db, -wal and -shm; any sharing
     violation refuses (SQLite opens with FILE_SHARE_READ|WRITE, so any open handle trips it).
     Non-Windows platforms refuse (no mandatory-lock probe). Repeated right before the checkpoint.
  4. Backup: db, -wal, -shm (those present) copied to experiment_results/_backup/wal_ckpt_<stamp>_<stem>/
     (the directory must not exist); every copy byte-equal to its source by sha256, source re-hashed
     after the copy (stability); free disk >= 2.2 x (db + wal) checked first.
  5. BEFORE: per-table sha256 read through a SCRATCH copy of the backup's db + wal (the WAL is applied by
     SQLite on open), never through the live file (closing the last connection to a WAL DB checkpoints it).
  6. `PRAGMA wal_checkpoint(TRUNCATE)` on the live DB (busy_timeout 0); the result must be (0, x, x).
     Skipped under --dry-run. The -wal must be 0 bytes (or absent) while the connection is still open
     (so the TRUNCATE, not the close-time checkpoint, did the work) and again after close.
  7. AFTER: per-table sha256 of the live file opened `mode=ro&immutable=1` (exact once the WAL is empty).
     Any difference in any table, the schema or the table set REFUSES with the table names and the
     backup directory to restore from.
  8. One summary line `[wal-ckpt] OK|DRY-RUN db=... result=... tables=... rows=... content=UNCHANGED ...`;
     before.json / after.json are written into the backup directory.
  Any failure at any stage, a Refused or any other exception (sqlite3.Error such as a garbage file or a
  locked DB, OSError such as a full disk), prints ONE line
  `[wal-ckpt] REFUSED: [stage <s>] <reason>; checkpoint NOT run|was ATTEMPTED; backup kept at <dir>|no
  backup written` and exits 2; never a traceback, never exit 1. The backup is always kept.
  Root files must not be symlinks or carry more than one hard link (db, -wal, -shm).

Retention: every run, dry runs included, leaves a full copy (up to ~1.9 GB for multicorpus_cache_v1.db) in
experiment_results/_backup/wal_ckpt_*; nothing is pruned automatically (the 2.2 x disk check refuses
first). Prune old folders by hand once a later OK has been read.
Allow-rule note (review C3, author's call): `Bash(python tools/ops/wal_checkpoint.py:*)` runs whatever file
sits at that relative path; pair it with a deny on Edit/Write of this file. A checkpoint moves whole-file
shas; pins stay per table (before.json / after.json).

Per-table hash: sha256 over repr(tuple(row)) + "\\n" for `SELECT * FROM t ORDER BY rowid` (WITHOUT ROWID
tables: ORDER BY the primary-key columns), plus the row count; `__schema__` hashes the sorted
sqlite_master rows. Virtual tables are skipped (their shadow tables are ordinary tables and are hashed).

Selftest (`--selftest`, temp dirs only, no DB of record opened): see `selftest()` docstring for the
cases and the mutant table.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_FIXED = frozenset({
    "mmlu_pro_dataset_cache_v2.db",
    "embeddings_cache.db",
    "multicorpus_cache_v1.db",
    "snapshots.db",
})
ALLOWED_PATTERN = re.compile(r"intent_emb_[A-Za-z0-9_]+\.db")
FORBIDDEN_PROCS = ("java.exe", "javaw.exe")
EXIT_OK, EXIT_REFUSED = 0, 2
DISK_FACTOR = 2.2


class Refused(Exception):
    pass


def log(msg: str) -> None:
    print(f"[wal-ckpt] {msg}", flush=True)


# ---------------------------------------------------------------- step 1: name and path
def resolve_db(name: str, root: Path) -> Path:
    if not name or name != os.path.basename(name) or "/" in name or "\\" in name or name in (".", ".."):
        raise Refused(f"--db must be a bare file name at the repo root, got {name!r}")
    if not (name in ALLOWED_FIXED or ALLOWED_PATTERN.fullmatch(name)):
        raise Refused(f"--db {name!r} is not on the allow-list "
                      f"({', '.join(sorted(ALLOWED_FIXED))}, intent_emb_*.db)")
    root_r = root.resolve()
    p = root / name
    if p.is_symlink():
        raise Refused(f"{name} is a symlink")
    if not p.is_file():
        raise Refused(f"{name} does not exist as a regular file at the repo root {root_r}")
    pr = p.resolve()
    if pr.parent != root_r:
        raise Refused(f"{name} resolves outside the repo root ({pr})")
    for f in (pr, Path(str(pr) + "-wal"), Path(str(pr) + "-shm")):
        if f.exists() and os.stat(f).st_nlink > 1:
            raise Refused(f"{f.name} has {os.stat(f).st_nlink} hard links (it may alias a file outside the root)")
    return pr


# ---------------------------------------------------------------- step 2: processes
def list_processes(runner=subprocess.run) -> list[str]:
    if os.name == "nt":
        out = runner(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                     errors="replace", timeout=60)
        if out.returncode != 0:
            raise Refused(f"tasklist failed (rc {out.returncode}); cannot verify no JVM is running")
        return parse_tasklist(out.stdout)
    out = runner(["ps", "-A", "-o", "comm="], capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        raise Refused("ps failed; cannot verify no JVM is running")
    return [os.path.basename(l.strip()) for l in out.stdout.splitlines() if l.strip()]


def parse_tasklist(text: str) -> list[str]:
    names = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('"'):
            names.append(line[1:].split('"', 1)[0])
    return names


def check_processes(names: list[str]) -> None:
    if not names:
        raise Refused("process list is empty; cannot verify no JVM is running")
    bad = sorted({n for n in names
                  if n.lower() in FORBIDDEN_PROCS or n.lower() == "java"
                  or n.lower().startswith("gradle")})
    if bad:
        raise Refused(f"forbidden process running: {', '.join(bad)} (stop every JVM / Gradle daemon first)")


# ---------------------------------------------------------------- step 3: exclusive-open probe
def exclusive_probe(path: Path) -> None:
    if os.name != "nt":
        raise Refused("exclusive-open probe is implemented for Windows only")
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    invalid = wintypes.HANDLE(-1).value
    for suffix in ("", "-wal", "-shm"):
        f = Path(str(path) + suffix)
        if not f.exists():
            continue
        h = k32.CreateFileW(str(f), 0x80000000 | 0x40000000, 0, None, 3, 0x80, None)
        if h == invalid or h is None:
            err = ctypes.get_last_error()
            if err == 2:  # vanished between exists() and open: nothing holds it
                continue
            raise Refused(f"exclusive-open probe failed on {f.name} (Win32 error {err}; "
                          f"32 = another process holds it open)")
        k32.CloseHandle(h)


# ---------------------------------------------------------------- hashing helpers
def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def table_hashes(con: sqlite3.Connection) -> dict:
    master = con.execute("SELECT type, name, tbl_name, sql FROM sqlite_master "
                         "ORDER BY type, name").fetchall()
    sh = hashlib.sha256()
    for r in master:
        sh.update((repr(tuple(r)) + "\n").encode("utf-8"))
    out = {"__schema__": {"rows": len(master), "sha256": sh.hexdigest()}}
    for typ, name, _tbl, sql in master:
        if typ != "table":
            continue
        s = (sql or "").upper()
        if s.startswith("CREATE VIRTUAL TABLE"):
            continue
        # WITHOUT ROWID is detected by asking SQLite, not by searching the SQL text (a default value or a
        # comment can contain the words)
        try:
            con.execute(f"SELECT _rowid_ FROM {_q(name)} LIMIT 0").fetchall()
            order = "_rowid_"
        except sqlite3.OperationalError:
            pk = [r[1] for r in sorted(con.execute(f"PRAGMA table_info({_q(name)})"), key=lambda r: r[5])
                  if r[5] > 0]
            if not pk:
                raise Refused(f"table {name!r} has neither a rowid nor primary-key columns; cannot order it")
            order = ", ".join(_q(c) for c in pk)
        h = hashlib.sha256()
        n = 0
        for row in con.execute(f"SELECT * FROM {_q(name)} ORDER BY {order}"):
            h.update((repr(tuple(row)) + "\n").encode("utf-8"))
            n += 1
        out[name] = {"rows": n, "sha256": h.hexdigest()}
    return out


def hashes_via_scratch(db_copy: Path, wal_copy: Path | None, scratch_dir: Path) -> dict:
    scratch_dir.mkdir(parents=True, exist_ok=False)
    sdb = scratch_dir / db_copy.name
    shutil.copyfile(db_copy, sdb)
    if wal_copy is not None:
        shutil.copyfile(wal_copy, Path(str(sdb) + "-wal"))
    try:
        con = sqlite3.connect(str(sdb), isolation_level=None)
        try:
            return table_hashes(con)
        finally:
            con.close()
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)


def hashes_immutable(db: Path) -> dict:
    con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        return table_hashes(con)
    finally:
        con.close()


def diff_hashes(a: dict, b: dict) -> list[str]:
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


# ---------------------------------------------------------------- the run
def run(db_name: str, *, root: Path = REPO_ROOT, dry_run: bool = False,
        procs=list_processes, probe=exclusive_probe, hooks: dict | None = None) -> int:
    """Every failure, Refused or any other exception (sqlite3.Error, OSError, ...), prints one
    `[wal-ckpt] REFUSED: [stage <s>] ...; <backup state>` line and returns EXIT_REFUSED; never a traceback."""
    hooks = hooks or {}
    bdir = None
    stage = "name"
    checkpointed = False
    try:
        db = resolve_db(db_name, root)
        stage = "processes"
        check_processes(procs())
        stage = "probe"
        probe(db)
        stage = "disk"
        wal, shm = Path(str(db) + "-wal"), Path(str(db) + "-shm")
        wal_before = wal.stat().st_size if wal.exists() else None
        need = DISK_FACTOR * (db.stat().st_size + (wal_before or 0))
        free = shutil.disk_usage(root).free
        if free < need:
            raise Refused(f"free disk {free} < {int(need)} bytes needed for backup + scratch")

        stage = "backup"
        stamp = hooks.get("stamp") or _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        target = root / "experiment_results" / "_backup" / f"wal_ckpt_{stamp}_{db.stem}"
        if target.exists():
            raise Refused(f"backup directory already exists: {target}")
        target.mkdir(parents=True)
        bdir = target
        copies = {}
        for f in (db, wal, shm):
            if not f.exists():
                continue
            src_sha = file_sha(f)
            dst = bdir / f.name
            shutil.copyfile(f, dst)
            if "after_copy" in hooks:
                hooks["after_copy"](dst)
            dst_sha, src_sha2 = file_sha(dst), file_sha(f)
            if not (src_sha == dst_sha == src_sha2):
                raise Refused(f"backup copy of {f.name} is not byte-equal to its source "
                              f"(src {src_sha[:12]} / copy {dst_sha[:12]} / src again {src_sha2[:12]})")
            copies[f.name] = dst_sha
        log(f"backup {bdir} verified byte-equal ({len(copies)} files)")

        stage = "before-hash"
        bwal = bdir / wal.name
        before = hashes_via_scratch(bdir / db.name, bwal if bwal.exists() else None, bdir / "_scratch")
        (bdir / "before.json").write_text(json.dumps(before, indent=1, sort_keys=True), encoding="utf-8")
        tables = len(before) - 1
        rows = sum(v["rows"] for k, v in before.items() if k != "__schema__")
        log(f"BEFORE (scratch copy, WAL applied): {tables} tables, {rows} rows")

        if dry_run:
            print(f"[wal-ckpt] DRY-RUN db={db.name} wal_bytes={wal_before} tables={tables} rows={rows} "
                  f"checkpoint=SKIPPED backup={bdir}", flush=True)
            return EXIT_OK

        stage = "recheck"
        check_processes(procs())
        probe(db)
        stage = "checkpoint"
        con = sqlite3.connect(str(db), isolation_level=None, timeout=0)
        try:
            mode = con.execute("PRAGMA journal_mode").fetchone()[0]
            if str(mode).lower() != "wal":
                raise Refused(f"{db.name} journal_mode is {mode!r}, not wal; nothing to checkpoint")
            checkpointed = True
            res = tuple(con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
            if "checkpoint_result" in hooks:
                res = hooks["checkpoint_result"](res)
            if not (len(res) == 3 and res[0] == 0 and res[1] == res[2]):
                raise Refused(f"wal_checkpoint(TRUNCATE) returned {res}, required (0, x, x)")
            # TRUNCATE empties the -wal while this connection is still open; a close-time checkpoint
            # (SQLite checkpoints when the last connection closes) must not be what did the work
            wal_open = wal.stat().st_size if wal.exists() else None
            if wal_open not in (None, 0):
                raise Refused(f"-wal is still {wal_open} bytes after wal_checkpoint(TRUNCATE) returned {res}")
        finally:
            con.close()
        if "after_close" in hooks:
            hooks["after_close"](wal)
        wal_after = wal.stat().st_size if wal.exists() else None
        if wal_after not in (None, 0):
            raise Refused(f"-wal is {wal_after} bytes after the checkpoint (expected absent or 0)")
        if "after_checkpoint" in hooks:
            hooks["after_checkpoint"](db)

        stage = "after-hash"
        after = hashes_immutable(db)
        (bdir / "after.json").write_text(json.dumps(after, indent=1, sort_keys=True), encoding="utf-8")
        changed = diff_hashes(before, after)
        if changed:
            raise Refused(f"CONTENT CHANGED by the checkpoint in {', '.join(changed)}; restore "
                          f"{db.name} (+ -wal/-shm) from the backup with no process running")
        print(f"[wal-ckpt] OK db={db.name} result={res} wal_bytes={wal_before}->{wal_after or 0} "
              f"tables={tables} rows={rows} content=UNCHANGED backup={bdir}", flush=True)
        return EXIT_OK
    except Exception as e:  # noqa: BLE001 - fail closed: every failure is a refusal, never a traceback
        what = str(e) if isinstance(e, Refused) else f"{type(e).__name__}: {e}"
        kept = f"backup kept at {bdir}" if bdir is not None else "no backup written"
        ck = ("checkpoint was ATTEMPTED (compare before.json with the DB before reuse)" if checkpointed
              else "checkpoint NOT run")
        print(f"[wal-ckpt] REFUSED: [stage {stage}] {what}; {ck}; {kept}", flush=True)
        return EXIT_REFUSED


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    """Temp-root selftest; opens no DB of record (every path is under a fresh tempfile.mkdtemp root).

    Cases (each asserts the exit code AND the printed value / verdict word, not just that it ran):
      S1 happy path: snapshots.db with 40 rows of which 25 live only in the WAL; the main file read
         immutable BEFORE shows 15 rows (WAL really pending), the run prints `OK`, `result=(0, N, N)` (only
         N == N is asserted: SQLite 3.39 TRUNCATE reports (0, 0, 0); the proof of the checkpoint is the next
         clause), `content=UNCHANGED`, `rows=40`; AFTER the main file alone (immutable) holds 40 rows,
         -wal is absent/0, before.json == after.json, backup holds db + wal byte-equal to the pre-run files.
      S2 --dry-run: prints `DRY-RUN ... checkpoint=SKIPPED rows=40`; live db and -wal byte-identical.
      S3 not on allow-list (ratings.db); S4 `../snapshots.db`; S5 absolute path; S6 allowed name absent;
      S7 intent_emb_x.db accepted (pattern) / intent_emb_../x refused; S8 java.exe running; S9 gradle.exe;
      S10 empty process list; S11 a live sqlite connection holds the db -> real CreateFileW probe refuses;
      S12 checkpoint result (1, 5, 5) refused; S13 (0, 5, 3) refused; S14 corrupted backup copy refused;
      S15 content mutated after the checkpoint -> REFUSED naming the table `t`; S16 backup dir exists;
      S17 parse_tasklist on a CSV fixture; S18 WITHOUT ROWID table hashed by pk, content diff detected
      only in that table, w hash equals the pk-ordered value; S19 non-WAL db refused at the journal_mode
      check; S20 a -wal of 64 bytes appearing after close refused; S21 a (0, x, x) result with a 64-byte
      -wal while the connection is open refused; S11 also asserts nothing was written.
      Review READY_wal_checkpoint C1/C2/D5: S22 symlink (Path.is_symlink patched: no symlink privilege
      here) refused at [stage name], no backup written; S23 resolve() outside the root refused; S24 the
      SECOND probe refuses -> checkpoint NOT run, backup kept, main file still 15 rows; S25 the SECOND
      process check refuses; S26 the source changes during the copy; S27 disk full; S28 tasklist rc != 0
      refused even with harmless stdout; S29 javaw.exe; S30 a hard link to the db (os.link) refused;
      S31 a garbage file named snapshots.db -> REFUSED `DatabaseError` at [stage before-hash], exit 2,
      backup kept; S32 `OperationalError: database is locked` at [stage checkpoint] -> REFUSED, exit 2,
      "checkpoint was ATTEMPTED"; S33 OSError during the copy -> REFUSED, exit 2; S34 a rowid table whose
      SQL contains "without rowid" is hashed in rowid order (non-first column order distinguishes it);
      S35 main() returns 2 on a refusal.

    Mutants: `python tools/ops/wal_checkpoint_mutants.py` (committed; M1-M25 builder, R1-R8 review,
    N1-N6 for C1/C2) applies each to a scratch copy and re-runs this selftest; the count of record is in
    the commit message.
    """
    import contextlib
    import io

    fails = []

    def check(cond, label):
        if not cond:
            fails.append(label)
            print(f"  FAIL {label}")
        else:
            print(f"  ok   {label}")

    def capture(fn, *a, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = fn(*a, **kw)
        return rc, buf.getvalue()

    def make_wal_db(root: Path, name: str, extra_sql: str = "") -> None:
        """15 rows checkpointed into the main file, 25 more left in a persisted -wal."""
        work = Path(tempfile.mkdtemp(dir=root.parent))
        src = work / name
        con = sqlite3.connect(str(src), isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA wal_autocheckpoint=0")
        con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT, b BLOB)")
        if extra_sql:
            con.executescript(extra_sql)
        for i in range(15):
            con.execute("INSERT INTO t VALUES (?, ?, ?)", (i, f"v{i}", bytes([i]) * 7))
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        for i in range(15, 40):
            con.execute("INSERT INTO t VALUES (?, ?, ?)", (i, f"v{i}", bytes([i]) * 7))
        # snapshot db + wal while the writer is still open (its close would checkpoint)
        shutil.copyfile(src, root / name)
        shutil.copyfile(Path(str(src) + "-wal"), root / (name + "-wal"))
        con.close()
        shutil.rmtree(work, ignore_errors=True)

    def imm_count(p: Path) -> int:
        c = sqlite3.connect(p.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
        try:
            return c.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        finally:
            c.close()

    clean = lambda: ["explorer.exe", "python.exe"]
    no_probe = lambda p: None
    base = Path(tempfile.mkdtemp(prefix="walckpt_selftest_"))
    try:
        def fresh(tag):
            r = base / tag
            r.mkdir()
            return r

        # S1 happy path
        r = fresh("s1")
        make_wal_db(r, "snapshots.db")
        db, wal = r / "snapshots.db", r / "snapshots.db-wal"
        pre_db, pre_wal = file_sha(db), file_sha(wal)
        check(wal.stat().st_size > 0 and imm_count(db) == 15, "S1 fixture: WAL pending (main file alone 15 rows)")
        rc, out = capture(run, "snapshots.db", root=r, procs=clean, hooks={"stamp": "T"})
        print(out, end="")
        m = re.search(r"result=\((\d+), (-?\d+), (-?\d+)\)", out)
        check(rc == EXIT_OK and "[wal-ckpt] OK db=snapshots.db" in out, "S1 verdict OK, exit 0")
        # TRUNCATE resets the frame counters once the log is truncated: SQLite 3.39 reports (0, 0, 0)
        check(m is not None and m.group(1) == "0" and m.group(2) == m.group(3),
              "S1 result=(0, N, N)")
        check("rows=40" in out and "tables=1" in out and "content=UNCHANGED" in out, "S1 rows=40 tables=1 UNCHANGED")
        check(imm_count(db) == 40, "S1 main file alone now holds 40 rows (checkpoint happened)")
        check((not wal.exists()) or wal.stat().st_size == 0, "S1 -wal absent or 0 bytes")
        bdir = r / "experiment_results" / "_backup" / "wal_ckpt_T_snapshots"
        check(file_sha(bdir / "snapshots.db") == pre_db and file_sha(bdir / "snapshots.db-wal") == pre_wal,
              "S1 backup db + wal byte-equal to pre-run files")
        bj = json.loads((bdir / "before.json").read_text(encoding="utf-8"))
        aj = json.loads((bdir / "after.json").read_text(encoding="utf-8"))
        check(bj == aj and bj["t"]["rows"] == 40, "S1 before.json == after.json, t rows 40")
        exp_t = hashlib.sha256("".join(repr((i, f"v{i}", bytes([i]) * 7)) + "\n" for i in range(40))
                               .encode("utf-8")).hexdigest()
        check(bj["t"]["sha256"] == exp_t, "S1 t sha256 equals the independently computed value")
        check(not (bdir / "_scratch").exists(), "S1 scratch removed")

        # S2 dry-run
        r = fresh("s2")
        make_wal_db(r, "embeddings_cache.db")
        db, wal = r / "embeddings_cache.db", r / "embeddings_cache.db-wal"
        pre_db, pre_wal = file_sha(db), file_sha(wal)
        rc, out = capture(run, "embeddings_cache.db", root=r, dry_run=True, procs=clean, hooks={"stamp": "T"})
        print(out, end="")
        check(rc == EXIT_OK and "[wal-ckpt] DRY-RUN db=embeddings_cache.db" in out
              and "checkpoint=SKIPPED" in out and "rows=40" in out, "S2 DRY-RUN verdict, rows=40")
        check(file_sha(db) == pre_db and wal.exists() and file_sha(wal) == pre_wal, "S2 live db + wal untouched")
        check(not (r / "experiment_results/_backup/wal_ckpt_T_embeddings_cache/after.json").exists(),
              "S2 no after.json")

        def refused(label, expect, *a, **kw):
            rc, out = capture(run, *a, **kw)
            check(rc == EXIT_REFUSED and "[wal-ckpt] REFUSED:" in out and expect in out, f"{label}: {expect!r}")
            return out

        r = fresh("s3")
        make_wal_db(r, "ratings.db")
        refused("S3 not on allow-list", "not on the allow-list", "ratings.db", root=r, procs=clean, probe=no_probe)
        refused("S4 traversal", "bare file name", "../snapshots.db", root=r, procs=clean, probe=no_probe)
        refused("S5 absolute", "bare file name", str(base / "s1" / "snapshots.db"), root=r, procs=clean,
                probe=no_probe)
        refused("S6 absent", "does not exist", "multicorpus_cache_v1.db", root=r, procs=clean, probe=no_probe)
        r7 = fresh("s7")
        make_wal_db(r7, "intent_emb_x.db")
        rc, out = capture(run, "intent_emb_x.db", root=r7, dry_run=True, procs=clean, probe=no_probe)
        check(rc == EXIT_OK and "DRY-RUN db=intent_emb_x.db" in out, "S7 intent_emb_x.db accepted by pattern")
        refused("S7b pattern traversal", "bare file name", "intent_emb_../x.db", root=r7, procs=clean,
                probe=no_probe)
        refused("S7c pattern suffix", "not on the allow-list", "intent_emb_x.db.bak", root=r7, procs=clean,
                probe=no_probe)
        r8 = fresh("s8")
        make_wal_db(r8, "snapshots.db")
        pre = file_sha(r8 / "snapshots.db-wal")
        refused("S8 java", "java.exe", "snapshots.db", root=r8, procs=lambda: ["python.exe", "java.exe"],
                probe=no_probe)
        refused("S9 gradle", "Gradle.exe", "snapshots.db", root=r8, procs=lambda: ["Gradle.exe"],
                probe=no_probe)
        refused("S10 empty process list", "process list is empty", "snapshots.db", root=r8, procs=lambda: [],
                probe=no_probe)
        check(not (r8 / "experiment_results").exists() and file_sha(r8 / "snapshots.db-wal") == pre,
              "S8-S10 nothing written, wal untouched")
        # S11 real probe against a live connection
        holder = sqlite3.connect(str(r8 / "snapshots.db"))
        holder.execute("SELECT COUNT(*) FROM t").fetchone()
        try:
            refused("S11 live handle", "exclusive-open probe failed", "snapshots.db", root=r8, procs=clean)
            check(not (r8 / "experiment_results").exists(), "S11 refused before any backup was written")
        finally:
            holder.close()
        r12 = fresh("s12")
        make_wal_db(r12, "snapshots.db")
        refused("S12 busy result", "returned (1, 5, 5)", "snapshots.db", root=r12, procs=clean,
                hooks={"checkpoint_result": lambda res: (1, 5, 5)})
        r13 = fresh("s13")
        make_wal_db(r13, "snapshots.db")
        refused("S13 partial result", "returned (0, 5, 3)", "snapshots.db", root=r13, procs=clean,
                hooks={"checkpoint_result": lambda res: (0, 5, 3)})
        r14 = fresh("s14")
        make_wal_db(r14, "snapshots.db")

        def corrupt(p):
            with open(p, "r+b") as fh:
                fh.seek(200)
                b = fh.read(1)
                fh.seek(200)
                fh.write(bytes([b[0] ^ 0xFF]))
        pre = file_sha(r14 / "snapshots.db-wal")
        refused("S14 corrupted backup", "not byte-equal", "snapshots.db", root=r14, procs=clean,
                hooks={"after_copy": lambda p: corrupt(p) if p.name.endswith("-wal") else None})
        check(file_sha(r14 / "snapshots.db-wal") == pre, "S14 live wal untouched")
        r15 = fresh("s15")
        make_wal_db(r15, "snapshots.db")

        def mutate(p):
            c = sqlite3.connect(str(p), isolation_level=None)
            c.execute("PRAGMA journal_mode=DELETE")
            c.execute("UPDATE t SET v = 'X' WHERE id = 39")
            c.close()
        out = refused("S15 content change", "CONTENT CHANGED by the checkpoint in t;", "snapshots.db", root=r15,
                      procs=clean, hooks={"after_checkpoint": mutate})
        check("__schema__" not in out.split("CONTENT CHANGED")[1].split(";")[0], "S15 only t named (schema same)")
        r16 = fresh("s16")
        make_wal_db(r16, "snapshots.db")
        (r16 / "experiment_results/_backup/wal_ckpt_T_snapshots").mkdir(parents=True)
        refused("S16 backup exists", "backup directory already exists", "snapshots.db", root=r16, procs=clean,
                hooks={"stamp": "T"})
        fixture = ('"System Idle Process","0","Services","0","8 K"\n'
                   '"java.exe","31012","Console","1","541 728 Ko"\n"gradlew.bat","1","C","1","1 K"\n')
        names = parse_tasklist(fixture)
        check(names == ["System Idle Process", "java.exe", "gradlew.bat"], "S17 parse_tasklist")
        try:
            check_processes(names)
            check(False, "S17 parsed java.exe refused")
        except Refused as e:
            check("gradlew.bat" in str(e) and "java.exe" in str(e), "S17 parsed java.exe + gradlew.bat refused")
        # S18 WITHOUT ROWID
        r18 = fresh("s18")
        make_wal_db(r18, "snapshots.db",
                    "CREATE TABLE w (a TEXT, b INTEGER, c TEXT, PRIMARY KEY (b, a)) WITHOUT ROWID;"
                    "INSERT INTO w VALUES ('z', 2, 'p'), ('a', 2, 'q'), ('m', 1, 'r');")

        def mutate_w(p):
            c = sqlite3.connect(str(p), isolation_level=None)
            c.execute("PRAGMA journal_mode=DELETE")
            c.execute("UPDATE w SET c = 'Q' WHERE a = 'a'")
            c.close()
        out = refused("S18 WITHOUT ROWID diff", "CONTENT CHANGED by the checkpoint in w;", "snapshots.db", root=r18,
                      procs=clean, hooks={"after_checkpoint": mutate_w, "stamp": "T"})
        bj = json.loads((r18 / "experiment_results/_backup/wal_ckpt_T_snapshots/before.json").read_text("utf-8"))
        check(bj["w"]["rows"] == 3 and bj["t"]["rows"] == 40, "S18 w hashed (3 rows), t 40 rows")
        exp_w = hashlib.sha256("".join(repr(r) + "\n" for r in [("m", 1, "r"), ("a", 2, "q"), ("z", 2, "p")])
                               .encode("utf-8")).hexdigest()
        check(bj["w"]["sha256"] == exp_w, "S18 w hashed in primary-key (b, a) order")
        # S20 a -wal reappearing after close is refused (the immutable AFTER view would miss it)
        r20 = fresh("s20")
        make_wal_db(r20, "snapshots.db")
        refused("S20 wal after close", "bytes after the checkpoint", "snapshots.db", root=r20, procs=clean,
                hooks={"after_close": lambda w: w.write_bytes(b"x" * 64)})
        # S21 a (0, x, x) result whose -wal is NOT empty while the connection is open is refused: the
        # close-time checkpoint must never be what passes the run
        r21 = fresh("s21")
        make_wal_db(r21, "snapshots.db")

        def grow_wal(res):
            with open(r21 / "snapshots.db-wal", "ab") as fh:
                fh.write(b"\0" * 64)
            return res
        refused("S21 wal not truncated", "-wal is still 64 bytes", "snapshots.db", root=r21, procs=clean,
                hooks={"checkpoint_result": grow_wal})
        # S19 non-WAL db
        r19 = fresh("s19")
        c = sqlite3.connect(str(r19 / "snapshots.db"))
        c.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
        c.commit()
        c.close()
        refused("S19 non-WAL", "not wal", "snapshots.db", root=r19, procs=clean)
        # ---- review READY_wal_checkpoint C1 (guards pinned) and C2 (every failure is REFUSED, exit 2)
        from unittest import mock
        import collections

        # S22 (R1) symlink refused (no symlink privilege here: Path.is_symlink is patched)
        r22 = fresh("s22")
        make_wal_db(r22, "snapshots.db")
        with mock.patch.object(Path, "is_symlink", lambda self: self.name == "snapshots.db"):
            out = refused("S22 symlink", "snapshots.db is a symlink", "snapshots.db", root=r22, procs=clean,
                          probe=no_probe)
        check("[stage name]" in out and "no backup written" in out, "S22 stage name, no backup written")
        # S23 (R2) resolves outside the root
        orig_resolve = Path.resolve
        outside = base / "elsewhere" / "snapshots.db"

        def fake_resolve(self, strict=False):
            r = orig_resolve(self, strict)
            return outside if r.name == "snapshots.db" else r
        with mock.patch.object(Path, "resolve", fake_resolve):
            refused("S23 outside root", "resolves outside the repo root", "snapshots.db", root=r22, procs=clean,
                    probe=no_probe)
        # S24 (R3) the SECOND probe (right before the checkpoint) refuses: no checkpoint happens
        r24 = fresh("s24")
        make_wal_db(r24, "snapshots.db")
        pre = file_sha(r24 / "snapshots.db-wal")
        calls = {"n": 0}

        def probe_second(p):
            calls["n"] += 1
            if calls["n"] == 2:
                raise Refused("probe2 held")
        out = refused("S24 second probe", "probe2 held", "snapshots.db", root=r24, procs=clean, probe=probe_second)
        check("[stage recheck]" in out and "checkpoint NOT run" in out and "backup kept at" in out,
              "S24 stage recheck, checkpoint NOT run, backup kept")
        check(file_sha(r24 / "snapshots.db-wal") == pre and imm_count(r24 / "snapshots.db") == 15,
              "S24 live wal untouched, main file still 15 rows")
        # S25 (R4) the SECOND process check refuses
        r25 = fresh("s25")
        make_wal_db(r25, "snapshots.db")
        pre = file_sha(r25 / "snapshots.db-wal")
        pc = {"n": 0}

        def procs_second():
            pc["n"] += 1
            return ["python.exe"] if pc["n"] == 1 else ["python.exe", "java.exe"]
        refused("S25 second process check", "forbidden process running: java.exe", "snapshots.db", root=r25,
                procs=procs_second, probe=no_probe)
        check(file_sha(r25 / "snapshots.db-wal") == pre and imm_count(r25 / "snapshots.db") == 15,
              "S25 live wal untouched, main file still 15 rows")
        # S26 (R5) the SOURCE changes during the copy (copy equals the first source hash): refused
        r26 = fresh("s26")
        make_wal_db(r26, "snapshots.db")

        def grow_source(dst):
            if dst.name.endswith("-wal"):
                with open(r26 / dst.name, "ab") as fh:
                    fh.write(b"\0" * 16)
        refused("S26 source moved during copy", "not byte-equal", "snapshots.db", root=r26, procs=clean,
                probe=no_probe, hooks={"after_copy": grow_source})
        # S27 (R6) disk check
        du = collections.namedtuple("du", "total used free")
        with mock.patch.object(shutil, "disk_usage", lambda p: du(10, 10, 0)):
            out = refused("S27 disk full", "free disk 0 <", "snapshots.db", root=r22, procs=clean, probe=no_probe)
        check("no backup written" in out and not (r22 / "experiment_results").exists(), "S27 nothing written")
        # S28 (R7) tasklist/ps non-zero return code refuses even when stdout lists harmless processes
        stub_out = collections.namedtuple("cp", "returncode stdout")(1, '"python.exe","1","C","1","1 K"\npython\n')
        try:
            list_processes(runner=lambda *a, **k: stub_out)
            check(False, "S28 non-zero tasklist rc refused")
        except Refused as e:
            check("failed" in str(e), "S28 non-zero tasklist rc refused")
        ok_out = collections.namedtuple("cp", "returncode stdout")(0, '"python.exe","1","C","1","1 K"\npython\n')
        check(list_processes(runner=lambda *a, **k: ok_out) in (["python.exe"], ['"python.exe","1","C","1","1 K"',
                                                                                  "python"]),
              "S28 rc 0 parses")
        # S29 (R8) javaw.exe
        refused("S29 javaw", "javaw.exe", "snapshots.db", root=r22, procs=lambda: ["javaw.exe"], probe=no_probe)
        # S30 hard link (D5)
        r30 = fresh("s30")
        make_wal_db(r30, "snapshots.db")
        try:
            os.link(r30 / "snapshots.db", base / "alias_outside.db")
            linked = True
        except OSError as e:
            linked = False
            check(False, f"S30 hard link fixture SKIPPED ({e}); counted as a failure")
        if linked:
            refused("S30 hard link", "snapshots.db has 2 hard links", "snapshots.db", root=r30, procs=clean,
                    probe=no_probe)
            os.remove(base / "alias_outside.db")
        # S31 (C2) garbage file named snapshots.db -> REFUSED exit 2 with the error type, backup kept
        r31 = fresh("s31")
        (r31 / "snapshots.db").write_bytes(b"this is not a sqlite database at all" * 200)
        out = refused("S31 garbage db", "DatabaseError", "snapshots.db", root=r31, procs=clean, probe=no_probe)
        check("[stage before-hash]" in out and "backup kept at" in out and "checkpoint NOT run" in out,
              "S31 stage before-hash, backup kept, checkpoint NOT run")
        # S32 (C2) locked DB at the checkpoint (sqlite3.OperationalError) -> REFUSED exit 2
        r32 = fresh("s32")
        make_wal_db(r32, "snapshots.db")

        def locked(res):
            raise sqlite3.OperationalError("database is locked")
        out = refused("S32 locked", "OperationalError: database is locked", "snapshots.db", root=r32, procs=clean,
                      hooks={"checkpoint_result": locked})
        check("[stage checkpoint]" in out and "checkpoint was ATTEMPTED" in out and "backup kept at" in out,
              "S32 stage checkpoint, ATTEMPTED, backup kept")
        # S33 (C2) OSError during the backup copy -> REFUSED exit 2, backup dir named
        r33 = fresh("s33")
        make_wal_db(r33, "snapshots.db")

        def oserr(dst):
            raise OSError(28, "No space left on device")
        out = refused("S33 OSError on copy", "OSError: [Errno 28] No space left on device", "snapshots.db",
                      root=r33, procs=clean, probe=no_probe, hooks={"after_copy": oserr})
        check("[stage backup]" in out and "backup kept at" in out, "S33 stage backup, backup kept")
        # S34 (C2) a rowid table whose SQL contains the words 'without rowid' is hashed by rowid
        r34 = fresh("s34")
        make_wal_db(r34, "snapshots.db", "CREATE TABLE c (note TEXT DEFAULT 'without rowid', "
                                         "id INTEGER PRIMARY KEY); INSERT INTO c VALUES ('a', 2), ('b', 1);")
        rc, out = capture(run, "snapshots.db", root=r34, procs=clean, hooks={"stamp": "T"})
        check(rc == EXIT_OK and "content=UNCHANGED" in out and "tables=2" in out and "rows=42" in out,
              "S34 'without rowid' text in a rowid table: OK, tables=2 rows=42")
        bj = json.loads((r34 / "experiment_results/_backup/wal_ckpt_T_snapshots/before.json").read_text("utf-8"))
        exp_c = hashlib.sha256("".join(repr(r) + "\n" for r in [("b", 1), ("a", 2)])
                               .encode("utf-8")).hexdigest()
        check(bj["c"]["sha256"] == exp_c, "S34 c hashed in rowid order")
        # S35 the CLI entry point itself returns 2 on a refusal (main -> run)
        check(main(["--db", "ratings.db"]) == EXIT_REFUSED, "S35 main() returns 2 on a refusal")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"[wal-ckpt] SELFTEST {'PASS' if not fails else 'FAIL'} ({len(fails)} failed)")
    return EXIT_OK if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", help="bare file name of an allow-listed repo-root DB")
    ap.add_argument("--dry-run", action="store_true", help="backup + BEFORE hashes, no checkpoint")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        if a.db or a.dry_run:
            ap.error("--selftest takes no other flag")
        return selftest()
    if not a.db:
        ap.error("--db is required")
    return run(a.db, dry_run=a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
