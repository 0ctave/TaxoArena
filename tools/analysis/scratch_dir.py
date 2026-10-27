"""scratch_dir: temp and scratch storage on E: with guaranteed cleanup (TEMP-SPRAWL fix, 2026-10-04).

Zero judge calls; opens no database; touches nothing outside its base (and, for --purge-legacy-temp, the
registered prefixes in the system temp).

WHY. The analysis scripts' selftests and mutant runs left ~19,700 dirs (~83 GB) in C:\\Users\\octav\\AppData\\Local\\Temp
and C: filled up. The author asked for (1) cleanup after every selftest or mutant run and (2) temp storage on E:.

BASE. env TAXOARENA_TMP if set, else E:/TaxoArena_tmp (created). Only if E: is absent (or the base cannot be
created) a subdir <system temp>/TaxoArena_tmp is used, with a warning printed on stderr. Every base carries the marker
file .taxoarena_scratch (written by base()); the system temp itself, a drive root, the repo root (or any ancestor of
it or of the system temp) and any TaxoArena_backup_* dir are never a base and never marked (D-1, READY_scratch_dir_e).

ON IMPORT (once per process; prints nothing): a per-process dir <base>/py_<pid>_<YYYYmmddHHMMSS>_<rand> is
created and tempfile.tempdir is pointed at it, so every tempfile.mkdtemp / mkstemp / TemporaryDirectory /
NamedTemporaryFile / gettempdir of the process lands there. At interpreter exit (atexit; also after an uncaught
exception) the whole per-process dir is removed: read-only attributes cleared, gc + retries for Windows handles;
if a handle still pins a file (an sqlite connection held to the end), a detached reaper deletes the dir as soon
as this pid has exited. A killed process (no atexit) leaves its dir: `--purge-stale` removes dirs whose pid is
dead.

  Scripts that are blob-pinned by other scripts (their LF blob is asserted at import by a pinner) are NOT edited
  to import this module, because any edit would make the pinner refuse; run those under the wrapper instead:
      python tools/analysis/scratch_dir.py --run -- python tools/analysis/<script>.py --selftest

API.  base() / process_dir() / mkdtemp(...) / mkstemp(...) / TemporaryDirectory(...) / scratch(prefix) (context
manager, removes on exit and on exceptions) / rmtree_robust(path) / cleanup().

CLI.
  python tools/analysis/scratch_dir.py --where                 base and this process's dir
  python tools/analysis/scratch_dir.py --count                 entries under the base
  python tools/analysis/scratch_dir.py --purge-stale [--days 1] [--all] [--root <marked base>] [--dry-run]
        STALENESS (STALE-LIVE fix, 2026-10-04): the NEWEST mtime of anything inside an entry (recursive; an unfinished
        scan counts as young), never below a 24 h floor whatever --days says; a dir holding a .taxoarena_owner file
        ('<pid> <start>', written when py_/run_ dirs are made) is skipped while that pid lives.
        REFUSES (nothing deleted) unless the root carries the marker, and always on a forbidden root (above).
        Removes py_/run_ dirs whose pid is dead (any age) and, under <base>/gradle (the Gradle test JVM's
        java.io.tmpdir), children older than --days. Any other entry (other agents' hand-made files) only with
        --all and older than --days. Never an entry of a live pid, never the gradle dir itself.
  python tools/analysis/scratch_dir.py --run -- <command ...>
        runs <command> with TAXOARENA_TMP / TMP / TEMP / TMPDIR set to a fresh <base>/run_<pid>_<ts>_* dir and
        removes that dir when the command exits (any rc, Ctrl-C included); returns the command's rc.
  python tools/analysis/scratch_dir.py --purge-legacy-temp [--since 2026-07-01] [--root <dir>] [--dry-run]
        one-off: deletes top-level DIRS in the system temp (or --root) whose name starts with a LEGACY_PREFIXES
        entry and whose mtime is on/after --since; read-only attributes cleared first.
  python tools/analysis/scratch_dir.py --selftest              value-asserting selftest + mutant table below.

SELFTEST SAFETY: every purge on a real forbidden root in the selftest is a DRY RUN and every child gets TMP/TEMP/
TMPDIR = a fixture (TMPDIR is read first by tempfile and exported by Git Bash: D-4), and the marker is only written into
a dir just created, empty, or already marked (D-5), so a mutant that drops a guard can delete or mark nothing real. (A first mutant pass without those two
rules marked the real system temp and E:\ and then purged the system temp: incident disclosed in the commit.)

SELFTEST MUTANTS (2026-10-04, copies under E:/TaxoArena_mutants_scratch_dir, reverted; the harness aborts if a
marker appears at the system temp / E:\ / C:\ / repo root or the system temp count moves; selftest and mutants run
in a sandbox with TMP/TEMP/TMPDIR/TAXOARENA_TMP inside it): 32/32 killed (N1-N6, S1 added 2026-10-04, STALE-LIVE fix)
  M1 rmtree_robust without the read-only handler (onerror=None)           killed (C3)
  M2 scratch() without the finally-removal (exception path leaks)        killed (C4)
  M3 purge-stale ignores pid liveness (deletes a live pid's dir)         killed (C6)
  M4 purge-stale ignores age (deletes a young non-pid entry)             killed (C6)
  M5 purge-stale deletes the gradle dir itself                           killed (C6)
  M6 legacy purge ignores the date cutoff                                killed (C8)
  M7 legacy purge matches any prefix (startswith "")                     killed (C8)
  M8 --run does not remove its run dir                                   killed (C7)
  M9 --run returns 0 instead of the child's rc                           killed (C7)
  M10 import does not point tempfile.tempdir at the process dir          killed (C2)
  M11 multiprocessing workers create their own dir (no parent reuse)      killed (C9)
  G1 purge without the marker check                                      killed (C10)
  G2 no system-temp guard                                                killed (C10)
  G3 no drive-root guard                                                 killed (C10)
  G4 no repo-root guard                                                  killed (C10)
  G5 no TaxoArena_backup_* guard                                         killed (C10)
  G6 no ancestor (repo root / system temp) guard                         killed (C10)
  G7 purge ignores forbidden()                                           killed (C10)
  G8 fallback = the system temp itself (unmarked dir marked)             killed (C5)
  G9 forbidden TAXOARENA_TMP used and marked as is                       killed (C11)
  G10 --all ignored (other agents' entries deleted by default)           killed (C6)
  G11 subdir of a backup dir not re-checked                              killed (C11)
  D4a --run wrapper does not set TMPDIR                                   killed (C7)
  D4b a selftest child env without TMPDIR (cenv)                          killed (C0)
  D5 _claim marks a non-empty unmarked dir                                killed (C12)
  N1 staleness by the dir's own mtime (not the newest file inside)        killed (C13)
  N2 live-owner file ignored                                              killed (C13)
  N3 no 24 h floor (days used as given)                                   killed (C13)
  N4 dead-pid py_/run_ dir purged without the age test                    killed (C13)
  N5 process dir without an owner file                                    killed (C1)
  N6 a capped (unfinished) scan returns a partial newest mtime            killed (C13)
  S1 floor via max() (NaN passes: max(nan, 1) is nan)                     killed (C13)
"""
import atexit
import datetime
import gc
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time

DEFAULT_BASE = "E:/TaxoArena_tmp"
GRADLE_SUBDIR = "gradle"
LEGACY_PREFIXES = ("pkkst", "cpcst", "pk2st", "pcsst", "rp13_", "erc_", "sgpqa_selftest", "k46", "e1sd", "e1rq_",
                   "e1rep_", "g13b_", "g13rf_", "v2dc_selftest", "canary", "cp_mut_", "cpone_", "cpdbg_", "own_mut_",
                   "emd_selftest_work", "v2fx_", "intent_emb_run")
LEGACY_SINCE = "2026-07-01"

_SYSTEM_TEMP = tempfile.gettempdir()      # resolved before we redirect tempfile.tempdir
_BASE = None
_PROC_DIR = None
_TRACKED = []


def _warn(msg):
    print("[SCRATCH] WARNING: %s" % msg, file=sys.stderr, flush=True)


MARKER = ".taxoarena_scratch"
FALLBACK_SUBDIR = "TaxoArena_tmp"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _nc(p):
    return os.path.normcase(os.path.normpath(os.path.abspath(p)))


def forbidden(path):
    """Reason a path may never be a scratch base nor be purged, else None (D-1, READY_scratch_dir_e)."""
    p = _nc(path)
    if p == _nc(_SYSTEM_TEMP):
        return "the system temp dir"
    if os.path.dirname(p) == p or p == _nc(os.path.splitdrive(p)[0] + os.sep):
        return "a drive root"
    if p == _nc(REPO_ROOT):
        return "the repo root"
    if any(c.lower().startswith("taxoarena_backup_") for c in p.replace("/", os.sep).split(os.sep)):
        return "a TaxoArena_backup_* dir"
    for anc, what in ((REPO_ROOT, "an ancestor of the repo root"), (_SYSTEM_TEMP, "an ancestor of the system temp")):
        if _nc(anc).startswith(p.rstrip(os.sep) + os.sep):
            return what
    return None


def _mark(d):
    m = os.path.join(d, MARKER)
    if not os.path.exists(m):
        with open(m, "w", encoding="utf-8") as f:
            f.write("TaxoArena scratch base (tools/analysis/scratch_dir.py); --purge-stale acts only where this file is.\n")


def _claim(d):
    """Create d if absent and mark it, ONLY if it was just created here, is empty, or already carries the marker
    (D-5, READY_scratch_dir_e_delta). Returns False (nothing written) for an existing non-empty unmarked dir."""
    existed = os.path.isdir(d)
    if existed and not os.path.isfile(os.path.join(d, MARKER)) and os.listdir(d):
        return False
    os.makedirs(d, exist_ok=True)
    _mark(d)
    return True


def base():
    """The scratch base (created, carrying MARKER). TAXOARENA_TMP, else E:/TaxoArena_tmp; if E: is absent or the base
    cannot be created, a marked subdir <system temp>/TaxoArena_tmp with a warning (the temp dir itself is never marked).
    A forbidden TAXOARENA_TMP (drive root, system temp, repo root, backup dir) is never marked: its TaxoArena_tmp
    subdir is used instead."""
    global _BASE
    if _BASE is not None:
        return _BASE
    env = os.environ.get("TAXOARENA_TMP")
    cand = env or DEFAULT_BASE
    fallback = os.path.join(_SYSTEM_TEMP, FALLBACK_SUBDIR)
    if not env and not os.path.isdir(os.path.splitdrive(os.path.abspath(cand))[0] + os.sep):
        _warn("drive of %s is absent; falling back to the system temp subdir %s" % (cand, fallback))
        cand = fallback
    why = forbidden(cand)
    if why:
        _warn("%s is %s; using its subdir %s" % (cand, why, FALLBACK_SUBDIR))
        cand = os.path.join(cand, FALLBACK_SUBDIR)
        if forbidden(cand):                      # still inside a backup dir: never there
            _warn("%s is %s; falling back to the system temp subdir %s" % (cand, forbidden(cand), fallback))
            cand = fallback
    try:
        if not _claim(cand):
            sub = os.path.join(cand, FALLBACK_SUBDIR)
            _warn("%s exists, is not empty and carries no %s marker; using its subdir %s" % (cand, MARKER, sub))
            cand = sub
            if not _claim(cand):
                raise OSError("%s is non-empty and unmarked too" % cand)
    except OSError as e:
        _warn("cannot use %s (%s); falling back to the system temp subdir %s" % (cand, e, fallback))
        cand = fallback
        if not _claim(cand):
            raise SystemExit("[SCRATCH] REFUSED: the fallback %s is non-empty and unmarked; set TAXOARENA_TMP" % cand)
    _BASE = os.path.abspath(cand)
    return _BASE


def _on_rm_error(func, path, exc_info):
    """Clear the read-only attribute and retry once (git objects, copied repos, sqlite journals are read-only)."""
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        parent = os.path.dirname(path)
        if parent:
            os.chmod(parent, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        func(path)
    except FileNotFoundError:
        pass


def rmtree_robust(path, retries=3, delay=0.2):
    """Remove path (dir or file); True when it is gone. Never raises."""
    for i in range(retries):
        if not os.path.lexists(path):
            return True
        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path, onerror=_on_rm_error)
            else:
                try:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    pass
                os.remove(path)
        except OSError:
            pass
        if not os.path.lexists(path):
            return True
        gc.collect()
        time.sleep(delay * (i + 1))
    return not os.path.lexists(path)


def _stamp():
    return time.strftime("%Y%m%d%H%M%S")


OWNER = ".taxoarena_owner"
MIN_AGE_DAYS = 1.0          # --purge-stale never removes anything whose newest file is younger than 24 h


def _write_owner(d):
    """Live-owner file: '<pid> <start epoch>' of the creating process; purge skips the dir while that pid lives."""
    with open(os.path.join(d, OWNER), "w", encoding="utf-8") as f:
        f.write("%d %.3f\n" % (os.getpid(), time.time()))


def _owner_alive(path):
    """True when path is a dir holding an OWNER file whose pid is alive (an unreadable owner file counts as alive)."""
    f = os.path.join(path, OWNER)
    if not os.path.isfile(f):
        return False
    try:
        pid = int(open(f, encoding="utf-8").read().split()[0])
    except (OSError, ValueError, IndexError):
        return True
    return pid_alive(pid)


def process_dir():
    """This process's dir under the base (created on first call, with a live-owner file; tempfile.tempdir points at it)."""
    global _PROC_DIR
    if _PROC_DIR is None or not os.path.isdir(_PROC_DIR):
        _PROC_DIR = tempfile.mkdtemp(prefix="py_%d_%s_" % (os.getpid(), _stamp()), dir=base())
        _write_owner(_PROC_DIR)
        tempfile.tempdir = _PROC_DIR
    return _PROC_DIR


def mkdtemp(suffix=None, prefix=None, dir=None):
    """tempfile.mkdtemp under this process's dir (removed at exit)."""
    d = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir or process_dir())
    _TRACKED.append(d)
    return d


def mkstemp(suffix=None, prefix=None, dir=None, text=False):
    fd, p = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir or process_dir(), text=text)
    _TRACKED.append(p)
    return fd, p


class TemporaryDirectory(object):
    """tempfile.TemporaryDirectory with robust removal (read-only files, Windows handles); never raises on cleanup."""

    def __init__(self, suffix=None, prefix=None, dir=None, ignore_cleanup_errors=True):
        self.name = mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    def __enter__(self):
        return self.name

    def __exit__(self, *exc):
        self.cleanup()
        return False

    def cleanup(self):
        rmtree_robust(self.name)


class scratch(object):
    """with scratch("x_") as d: ...   -> d removed on exit, exceptions included."""

    def __init__(self, prefix="scratch_", suffix=None):
        self.prefix, self.suffix, self.name = prefix, suffix, None

    def __enter__(self):
        self.name = mkdtemp(suffix=self.suffix, prefix=self.prefix)
        return self.name

    def __exit__(self, *exc):
        rmtree_robust(self.name)
        return False


def _spawn_reaper(path):
    """Detached child that waits for this pid to exit, then removes path (Windows keeps files of open handles)."""
    try:
        flags = 0
        if os.name == "nt":
            flags = 0x00000008 | 0x00000200 | 0x08000000   # DETACHED_PROCESS | NEW_PROCESS_GROUP | NO_WINDOW
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "--reap", str(os.getpid()), path],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         close_fds=True, creationflags=flags)
        return True
    except Exception:
        return False


def cleanup():
    """Remove every tracked path and this process's dir. Registered with atexit on import."""
    gc.collect()
    for p in reversed(_TRACKED):
        rmtree_robust(p, retries=1)
    del _TRACKED[:]
    if _PROC_DIR and os.path.lexists(_PROC_DIR):
        if tempfile.tempdir == _PROC_DIR:
            tempfile.tempdir = None
        if not rmtree_robust(_PROC_DIR):
            _spawn_reaper(_PROC_DIR)


def pid_alive(pid):
    if pid == os.getpid():
        return True
    if os.name == "nt":
        import ctypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        h = k.OpenProcess(0x1000, False, int(pid))     # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5        # ACCESS_DENIED: it exists
        try:
            code = ctypes.c_ulong()
            if not k.GetExitCodeProcess(h, ctypes.byref(code)):
                return True
            return code.value == 259                   # STILL_ACTIVE
        finally:
            k.CloseHandle(h)
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _owner_pid(name):
    """pid encoded in a py_<pid>_... / run_<pid>_... entry name, else None."""
    parts = name.split("_")
    if len(parts) >= 3 and parts[0] in ("py", "run") and parts[1].isdigit():
        return int(parts[1])
    return None


def _newest_mtime(path, cap=20000):
    try:
        newest = os.lstat(path).st_mtime
    except OSError:
        return None
    if os.path.isdir(path) and not os.path.islink(path):
        n = 0
        for root, dirs, files in os.walk(path):
            for x in dirs + files:
                try:
                    newest = max(newest, os.lstat(os.path.join(root, x)).st_mtime)
                except OSError:
                    pass
                n += 1
                if n >= cap:
                    return None             # not fully scanned: unknown age, never purged
    return newest


def purge_stale(days=1.0, root=None, dry_run=False, now=None, out=print, all_entries=False):
    """Delete leftovers under a MARKED base. Returns dict(removed, kept_alive, kept_young, kept_foreign, failed).
    REFUSES (SystemExit, nothing deleted) on a forbidden root (system temp, drive root, repo root or an ancestor of it
    or of the system temp, TaxoArena_backup_*) and on a root without the MARKER file. By default only py_/run_ dirs
    of dead pids and old gradle/ children go; other entries (e.g. other agents' hand-made files) only with
    all_entries=True (--all)."""
    root = os.path.abspath(root or base())
    why = forbidden(root)
    if why:
        raise SystemExit("[SCRATCH] purge-stale REFUSED: %s is %s; nothing deleted" % (root, why))
    if not os.path.isfile(os.path.join(root, MARKER)):
        raise SystemExit("[SCRATCH] purge-stale REFUSED: %s carries no %s marker (not a scratch base); nothing deleted"
                         % (root, MARKER))
    now = time.time() if now is None else now
    d_ = float(days)
    days = d_ if d_ >= MIN_AGE_DAYS else MIN_AGE_DAYS   # floor (NaN/negative/0 -> 24 h; S-1): nothing younger than 24 h
    limit = now - days * 86400.0
    res = dict(removed=[], kept_alive=[], kept_young=[], kept_foreign=[], failed=[])

    def consider(path, name):
        if name == MARKER:
            return
        if path == _PROC_DIR:
            res["kept_alive"].append(path)
            return
        pid = _owner_pid(name)
        if (pid is not None and pid_alive(pid)) or _owner_alive(path):
            res["kept_alive"].append(path)
            return
        if pid is None and not all_entries:
            res["kept_foreign"].append(path)
            return
        m = _newest_mtime(path)                 # NEWEST mtime of anything inside (recursive), not the dir's own
        if m is None or m >= limit:
            res["kept_young"].append(path)
            return
        if dry_run or rmtree_robust(path):
            res["removed"].append(path)
        else:
            res["failed"].append(path)

    if not os.path.isdir(root):
        return res
    for e in sorted(os.scandir(root), key=lambda x: x.name):
        if e.name == GRADLE_SUBDIR and e.is_dir(follow_symlinks=False):
            for g in sorted(os.scandir(e.path), key=lambda x: x.name):
                if _owner_alive(g.path):
                    res["kept_alive"].append(g.path)
                    continue
                m = _newest_mtime(g.path)
                if m is not None and m < limit:
                    if dry_run or rmtree_robust(g.path):
                        res["removed"].append(g.path)
                    else:
                        res["failed"].append(g.path)
                else:
                    res["kept_young"].append(g.path)
            continue
        consider(e.path, e.name)
    out("[SCRATCH] purge-stale%s under %s (newest file older than %.2f day(s), owner dead): removed %d, kept (live pid) %d, "
        "kept (young) %d, kept (not ours; --all) %d, failed %d"
        % (" DRY-RUN" if dry_run else "", root, days, len(res["removed"]), len(res["kept_alive"]),
           len(res["kept_young"]), len(res["kept_foreign"]), len(res["failed"])))
    return res


def purge_legacy(root=None, since=LEGACY_SINCE, prefixes=LEGACY_PREFIXES, dry_run=False, out=print):
    """Top-level DIRS in root (default: the system temp) starting with a registered prefix, mtime >= since."""
    root = root or _SYSTEM_TEMP
    cut = datetime.datetime.strptime(since, "%Y-%m-%d").timestamp()
    res = dict(matched=0, removed=0, failed=[])
    for e in sorted(os.scandir(root), key=lambda x: x.name):
        if not e.is_dir(follow_symlinks=False) or not e.name.startswith(tuple(prefixes)):
            continue
        if e.stat(follow_symlinks=False).st_mtime < cut:
            continue
        res["matched"] += 1
        if dry_run:
            continue
        if rmtree_robust(e.path):
            res["removed"] += 1
        else:
            res["failed"].append(e.path)
    out("[SCRATCH] purge-legacy-temp%s under %s (prefixes %d, mtime >= %s): matched %d, removed %d, failed %d"
        % (" DRY-RUN" if dry_run else "", root, len(prefixes), since, res["matched"], res["removed"], len(res["failed"])))
    return res


def count_entries(root=None):
    root = root or base()
    return sum(1 for _ in os.scandir(root)) if os.path.isdir(root) else 0


def run_wrapped(cmd, out=None):
    """Run cmd with all temp env vars on a fresh run dir; remove it afterwards; return cmd's rc."""
    out = out or (lambda s: print(s, file=sys.stderr, flush=True))
    b = base()
    before = count_entries(b)
    rd = tempfile.mkdtemp(prefix="run_%d_%s_" % (os.getpid(), _stamp()), dir=b)
    _write_owner(rd)
    env = dict(os.environ)
    for k in ("TAXOARENA_TMP", "TMP", "TEMP", "TMPDIR"):
        env[k] = rd
    rc = 1
    try:
        rc = subprocess.call(cmd, env=env)
    except KeyboardInterrupt:
        rc = 130
    finally:
        gone = rmtree_robust(rd, retries=6)
        if not gone:
            _spawn_reaper(rd)
        out("[SCRATCH] --run rc %d | run dir %s %s | entries under %s: before %d, after %d"
            % (rc, rd, "removed" if gone else "NOT removed (reaper spawned)", b, before, count_entries(b)))
    return rc


def _reap(pid, path):
    t0 = time.time()
    while pid_alive(pid) and time.time() - t0 < 600:
        time.sleep(0.5)
    rmtree_robust(path, retries=10, delay=0.5)


PROC_ENV = "TAXOARENA_TMP_PROC"


def _install():
    """On import. A multiprocessing worker (Windows spawn: sys.orig_argv carries --multiprocessing-fork;
    sys.argv is reset to the parent's by multiprocessing.spawn.prepare) reuses its parent's
    dir and registers nothing: pool workers are ended by TerminateProcess, which skips atexit, so a dir of their own
    would be left behind; the parent removes the shared dir at its exit. Every other process gets its own dir."""
    global _PROC_DIR
    inherited = os.environ.get(PROC_ENV)
    if "--multiprocessing-fork" in getattr(sys, "orig_argv", sys.argv) and inherited and os.path.isdir(inherited):
        _PROC_DIR = inherited
        tempfile.tempdir = inherited
        return
    process_dir()
    os.environ[PROC_ENV] = _PROC_DIR
    atexit.register(cleanup)


# ---- on import: redirect this process's temp into the base and remove it at exit ----
if __name__ != "__main__":
    _install()


# ---------------------------------------------------------------- selftest
def selftest():
    """Value-asserting checks C1-C8 on a private base (TAXOARENA_TMP is never the real E: base here)."""
    import io
    checks = 0
    sys_tmp = _SYSTEM_TEMP
    root = tempfile.mkdtemp(prefix="scratch_dir_selftest_", dir=base())
    try:
        here = os.path.abspath(__file__)
        ctmp = os.path.join(root, "CHILDTMP")
        os.makedirs(ctmp)

        def cenv(**kw):
            """Child env: TMP, TEMP and TMPDIR (tempfile reads TMPDIR first; Git Bash exports it) on a fixture (D-4)."""
            t = kw.pop("_tmp", ctmp)
            e = dict(os.environ, TMP=t, TEMP=t, TMPDIR=t)
            e.update(kw)
            return e

        # C0 (D-4): a child's tempfile resolves to the fixture, whatever TMPDIR/TMP/TEMP the caller exported
        p = subprocess.run([sys.executable, "-c", "import tempfile; print(tempfile.gettempdir())"],
                           env=cenv(), capture_output=True, text=True)
        assert p.returncode == 0 and _nc(p.stdout.strip()) == _nc(ctmp), (p.stdout, ctmp)
        checks += 1
        env = cenv(TAXOARENA_TMP=os.path.join(root, "B"))

        # C1/C2: a child importing the module puts its temp under TAXOARENA_TMP and removes it at exit
        prog = ("import sys; sys.path.insert(0, %r); import tempfile, os, scratch_dir as s; "
                "d = tempfile.mkdtemp(prefix='c1_'); open(os.path.join(d, 'f'), 'w').write('x'); "
                "os.chmod(os.path.join(d, 'f'), 0o444); "
                "t = tempfile.TemporaryDirectory(); "
                "print(s.base()); print(s.process_dir()); print(tempfile.gettempdir()); print(d); "
                "print(open(os.path.join(s.process_dir(), s.OWNER)).read().split()[0] == str(os.getpid()))"
                % os.path.dirname(here))
        p = subprocess.run([sys.executable, "-c", prog], env=env, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        b, pd, gt, d, own_ok = p.stdout.split("\n")[:5]
        assert own_ok == "True", p.stdout
        assert os.path.normcase(b) == os.path.normcase(os.path.join(root, "B")), (b, root)
        checks += 1                                                                      # C1 base = TAXOARENA_TMP
        assert gt == pd and os.path.dirname(pd) == b and os.path.dirname(d) == pd, (b, pd, gt, d)
        assert os.path.basename(pd).startswith("py_"), pd
        checks += 1                                                                      # C2 tempfile redirected
        assert not os.path.exists(pd) and os.listdir(b) == [MARKER], os.listdir(b)
        checks += 1                                                                      # C3 removed at exit (read-only file)

        # C4: exception path inside scratch() and an uncaught exception at top level both clean up
        prog2 = ("import sys; sys.path.insert(0, %r); import os, scratch_dir as s\n"
                 "try:\n    with s.scratch('c4_') as d:\n        open(os.path.join(d, 'f'), 'w').write('x'); "
                 "print(d, flush=True); raise ValueError('boom')\nexcept ValueError:\n    pass\n"
                 "print(os.path.exists(d), flush=True)\nimport tempfile; tempfile.mkdtemp(prefix='c4b_')\n"
                 "raise RuntimeError('uncaught')\n" % os.path.dirname(here))
        p = subprocess.run([sys.executable, "-c", prog2], env=env, capture_output=True, text=True)
        assert p.returncode == 1 and "uncaught" in p.stderr, (p.returncode, p.stderr)
        assert p.stdout.split("\n")[1] == "False", p.stdout
        assert os.listdir(b) == [MARKER], os.listdir(b)
        checks += 1

        # C5: E: absent -> system temp + warning (simulated with a drive letter that does not exist)
        envx = dict(os.environ)
        envx.pop("TAXOARENA_TMP", None)
        drive = next(c for c in "QRSTUVWXYJKLMNOP" if not os.path.isdir(c + ":\\"))
        fake_sys = os.path.join(root, "SYS")
        os.makedirs(fake_sys)
        imp = os.path.join(root, "IMP")              # import-time base of the child (a fixture), then TAXOARENA_TMP unset
        p = subprocess.run([sys.executable, "-c", "import sys, os; sys.path.insert(0, %r); import scratch_dir as s; "
                            "os.environ.pop('TAXOARENA_TMP'); "
                            "s.DEFAULT_BASE = %r; s._BASE = None; s._SYSTEM_TEMP = %r; print(s.base())"
                            % (os.path.dirname(here), drive + ":/TaxoArena_tmp", fake_sys)],
                           env=cenv(TAXOARENA_TMP=imp, _tmp=fake_sys), capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        fb = os.path.join(fake_sys, FALLBACK_SUBDIR)
        assert os.path.normcase(p.stdout.strip()) == os.path.normcase(fb), (p.stdout, fb)
        assert "falling back to the system temp subdir %s" % fb in p.stderr and "is the system temp dir" not in p.stderr, p.stderr
        assert os.listdir(fake_sys) == [FALLBACK_SUBDIR] and os.path.isfile(os.path.join(fb, MARKER)), os.listdir(fake_sys)
        checks += 1                                      # C5 marked fallback subdir; the temp dir itself stays unmarked
        del sys_tmp

        # C6: purge-stale keeps a live pid, a young entry, the gradle dir; removes a dead pid and an old entry
        pb = os.path.join(root, "P")
        os.makedirs(pb)
        live = os.path.join(pb, "py_%d_20260101000000_x" % os.getpid())
        dead_pid = 4194300
        while pid_alive(dead_pid):
            dead_pid -= 1
        dead = os.path.join(pb, "py_%d_20260101000000_y" % dead_pid)
        young = os.path.join(pb, "young_dir")
        old = os.path.join(pb, "old_dir")
        gr = os.path.join(pb, GRADLE_SUBDIR)
        gold, gyoung = os.path.join(gr, "old_tmp"), os.path.join(gr, "young_tmp")
        for x in (live, dead, young, old, gold, gyoung):
            os.makedirs(x)
            open(os.path.join(x, "f"), "w").write("x")
        _mark(pb)
        os.chmod(os.path.join(old, "f"), 0o444)
        t_old = time.time() - 3 * 86400
        for x in (old, os.path.join(old, "f"), gold, os.path.join(gold, "f"), live, dead, os.path.join(dead, "f")):
            os.utime(x, (t_old, t_old))
        buf = io.StringIO()
        r = purge_stale(days=1, root=pb, out=lambda s_: buf.write(s_ + "\n"))       # default: only ours
        assert sorted(os.listdir(pb)) == sorted([MARKER, os.path.basename(live), "young_dir", "old_dir",
                                                 GRADLE_SUBDIR]), os.listdir(pb)
        assert os.listdir(gr) == ["young_tmp"], os.listdir(gr)
        assert len(r["removed"]) == 2 and r["failed"] == [], r
        assert "removed 2, kept (live pid) 1, kept (young) 1, kept (not ours; --all) 2, failed 0" in buf.getvalue(), buf.getvalue()
        buf = io.StringIO()
        r = purge_stale(days=1, root=pb, out=lambda s_: buf.write(s_ + "\n"), all_entries=True)
        assert sorted(os.listdir(pb)) == sorted([MARKER, os.path.basename(live), "young_dir", GRADLE_SUBDIR]), os.listdir(pb)
        assert "removed 1, kept (live pid) 1, kept (young) 2, kept (not ours; --all) 0, failed 0" in buf.getvalue(), buf.getvalue()
        checks += 1

        # C13 (STALE-LIVE fix): staleness = newest file inside (recursive); a live-owner file protects; 24 h floor;
        # a dead-pid dir with young content stays; an unfinished scan counts as young
        sb = os.path.join(root, "S")
        os.makedirs(sb)
        _mark(sb)
        t3 = time.time() - 3 * 86400

        def mk(name, file_age, dir_age=t3):
            d_ = os.path.join(sb, name)
            os.makedirs(os.path.join(d_, "sub"))
            f_ = os.path.join(d_, "sub", "f")
            open(f_, "w").write("x")
            os.utime(f_, (file_age, file_age))
            for x in (os.path.join(d_, "sub"), d_):
                os.utime(x, (dir_age, dir_age))
            return d_
        mk("fresh_inside", time.time() - 3600)                       # dir 3 d old, a file 1 h old (live review)
        own = mk("owned", t3)                                        # all 3 d old, owner = this (live) pid
        with open(os.path.join(own, OWNER), "w") as f:
            f.write("%d %.3f\n" % (os.getpid(), time.time()))
        os.utime(os.path.join(own, OWNER), (t3, t3))
        os.utime(own, (t3, t3))
        mk("half_day", time.time() - 12 * 3600, time.time() - 12 * 3600)   # 12 h old: under the floor
        mk("py_%d_20260101000000_q" % dead_pid, time.time() - 600)        # dead pid, young content
        dead_own = mk("dead_owner", t3)                              # owner pid dead, all old -> removed
        with open(os.path.join(dead_own, OWNER), "w") as f:
            f.write("%d 0\n" % dead_pid)
        os.utime(os.path.join(dead_own, OWNER), (t3, t3))
        os.utime(dead_own, (t3, t3))
        buf = io.StringIO()
        r = purge_stale(days=0, root=sb, out=lambda s_: buf.write(s_ + "\n"), all_entries=True)
        assert sorted(os.listdir(sb)) == sorted([MARKER, "fresh_inside", "owned", "half_day",
                                                 "py_%d_20260101000000_q" % dead_pid]), os.listdir(sb)
        assert [os.path.basename(x) for x in r["removed"]] == ["dead_owner"], r
        assert "older than 1.00 day(s)" in buf.getvalue() and "removed 1, kept (live pid) 1, kept (young) 3" in buf.getvalue(), buf.getvalue()
        assert _newest_mtime(os.path.join(sb, "fresh_inside"), cap=1) is None
        for bad in (float("nan"), -1, 0, "nan"):                     # S-1: every value below the floor gets 24 h
            buf = io.StringIO()
            r = purge_stale(days=bad, root=sb, out=lambda s_: buf.write(s_ + "\n"), all_entries=True)
            assert r["removed"] == [] and "half_day" in os.listdir(sb), (bad, r)
            assert "older than 1.00 day(s)" in buf.getvalue(), (bad, buf.getvalue())
        checks += 1

        # C10: purge REFUSES (SystemExit, nothing deleted) without the marker and on every forbidden root
        def refused(rt, want):
            try:
                purge_stale(days=0, root=rt, out=lambda s_: None, all_entries=True, dry_run=True)   # dry: a mutant that drops a guard deletes nothing
            except SystemExit as e:
                assert want in str(e) and "nothing deleted" in str(e), (rt, want, str(e))
                return
            raise AssertionError("purge on %s was not refused" % rt)
        um = os.path.join(root, "UNMARKED")
        os.makedirs(os.path.join(um, "py_%d_20260101000000_z" % dead_pid))
        refused(um, "carries no %s marker" % MARKER)
        assert os.listdir(um) == ["py_%d_20260101000000_z" % dead_pid], os.listdir(um)
        refused(_SYSTEM_TEMP, "is the system temp dir")
        refused(os.path.splitdrive(root)[0] + os.sep, "is a drive root")
        refused(REPO_ROOT, "is the repo root")
        refused(os.path.dirname(REPO_ROOT), "is an ancestor of the repo root")
        bk = os.path.join(root, "TaxoArena_backup_2026-10-04")
        os.makedirs(os.path.join(bk, "py_%d_20260101000000_z" % dead_pid))
        _mark(bk)
        refused(bk, "is a TaxoArena_backup_* dir")
        assert sorted(os.listdir(bk)) == sorted([MARKER, "py_%d_20260101000000_z" % dead_pid]), os.listdir(bk)
        p = subprocess.run([sys.executable, here, "--purge-stale", "--root", um, "--dry-run"], env=cenv(),
                           capture_output=True, text=True)
        assert p.returncode != 0 and "REFUSED" in p.stderr and os.path.exists(os.path.join(um, "py_%d_20260101000000_z" % dead_pid)), p.stderr
        checks += 1

        # C11: a forbidden TAXOARENA_TMP is never marked: the (fixture) system temp and a backup dir are redirected.
        # SAFETY: no child here may resolve a real system temp or drive root (a mutant would mark it): every child
        # gets TMP/TEMP = the fixture, and the drive-root case is covered by forbidden() in C10 (dry-run purges only).
        sys2 = os.path.join(root, "SYS2")
        os.makedirs(sys2)
        p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import scratch_dir as s; print(s.base())"
                            % os.path.dirname(here)], env=cenv(TAXOARENA_TMP=sys2, _tmp=sys2),
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        assert _nc(p.stdout.strip()) == _nc(os.path.join(sys2, FALLBACK_SUBDIR)), p.stdout
        assert os.listdir(sys2) == [FALLBACK_SUBDIR], os.listdir(sys2)
        p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import scratch_dir as s; "
                            "s._SYSTEM_TEMP = %r; s._BASE = None; print(s.base())" % (os.path.dirname(here), fake_sys)],
                           env=cenv(TAXOARENA_TMP=os.path.join(root, "TaxoArena_backup_x"), _tmp=fake_sys),
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        assert _nc(p.stdout.strip()) == _nc(os.path.join(fake_sys, FALLBACK_SUBDIR)), p.stdout
        assert not os.path.exists(os.path.join(root, "TaxoArena_backup_x", MARKER))
        checks += 1

        # C7: --run sets the temp env to a run dir, removes it, and returns the child's rc
        rb = os.path.join(root, "R")
        prog4 = ("import os, tempfile, sys; d = tempfile.mkdtemp(prefix='c7_'); "
                 "print(os.environ['TAXOARENA_TMP']); print(d); "
                 "print(os.environ['TMPDIR'] == os.environ['TMP'] == os.environ['TEMP'] == os.environ['TAXOARENA_TMP']); sys.exit(7)")
        p = subprocess.run([sys.executable, here, "--run", "--", sys.executable, "-c", prog4],
                           env=cenv(TAXOARENA_TMP=rb), capture_output=True, text=True)
        assert p.returncode == 7, (p.returncode, p.stderr)
        rd, cd, same = p.stdout.split("\n")[:3]
        assert same == "True", p.stdout
        assert os.path.dirname(rd) == rb and os.path.basename(rd).startswith("run_") and os.path.dirname(cd) == rd
        assert os.listdir(rb) == [MARKER] and "rc 7" in p.stderr and "before 1, after 1" in p.stderr, (os.listdir(rb), p.stderr)
        checks += 1

        # C8: legacy purge: only registered prefixes, only dirs, only mtime >= since; read-only files removed
        lr = os.path.join(root, "L")
        os.makedirs(lr)
        mk = {"rp13_abc": "2026-09-01", "erc_x": "2026-08-01", "rp13_old": "2026-06-15", "zzz_keep": "2026-09-01",
              "canary_y": "2026-07-02"}
        for n, dt in mk.items():
            os.makedirs(os.path.join(lr, n))
            f = os.path.join(lr, n, "f")
            open(f, "w").write("x")
            os.chmod(f, 0o444)
            ts = datetime.datetime.strptime(dt, "%Y-%m-%d").timestamp()
            os.utime(os.path.join(lr, n), (ts, ts))
        open(os.path.join(lr, "rp13_file"), "w").write("x")
        buf = io.StringIO()
        r = purge_legacy(root=lr, since="2026-07-01", out=lambda s_: buf.write(s_ + "\n"))
        assert sorted(os.listdir(lr)) == ["rp13_file", "rp13_old", "zzz_keep"], os.listdir(lr)
        assert r["matched"] == 3 and r["removed"] == 3 and r["failed"] == [], r
        assert "matched 3, removed 3, failed 0" in buf.getvalue(), buf.getvalue()
        checks += 1

        # C9: a multiprocessing pool (workers ended by terminate()) leaves nothing; workers use the parent's dir
        mb = os.path.join(root, "M")
        mp_prog = os.path.join(root, "mp_child.py")
        open(mp_prog, "w").write(
            "import sys; sys.path.insert(0, %r)\n"
            "import os, tempfile, multiprocessing as mp, scratch_dir\n"
            "def f(_):\n    return tempfile.gettempdir()\n"
            "if __name__ == '__main__':\n"
            "    p = mp.Pool(2); r = set(p.map(f, range(4))); p.terminate(); p.join()\n"
            "    print(scratch_dir.process_dir()); print(sorted(r))\n" % os.path.dirname(here))
        p = subprocess.run([sys.executable, mp_prog], env=cenv(TAXOARENA_TMP=mb), capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        pdir, workers = p.stdout.split("\n")[:2]
        assert workers == repr([pdir]), (pdir, workers)
        assert os.listdir(mb) == [MARKER], os.listdir(mb)
        checks += 1

        # C12 (D-5): an existing NON-EMPTY unmarked TAXOARENA_TMP is never marked (its TaxoArena_tmp subdir is used);
        # an existing EMPTY dir is marked
        busy = os.path.join(root, "BUSY")
        os.makedirs(os.path.join(busy, "run_of_record"))
        open(os.path.join(busy, "run_of_record", "outcome.txt"), "w").write("x")
        p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import scratch_dir as s; print(s.base())"
                            % os.path.dirname(here)], env=cenv(TAXOARENA_TMP=busy), capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        assert _nc(p.stdout.strip()) == _nc(os.path.join(busy, FALLBACK_SUBDIR)), p.stdout
        assert sorted(os.listdir(busy)) == sorted(["run_of_record", FALLBACK_SUBDIR]), os.listdir(busy)
        assert "carries no %s marker" % MARKER in p.stderr, p.stderr
        empty = os.path.join(root, "EMPTY")
        os.makedirs(empty)
        p = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import scratch_dir as s; print(s.base())"
                            % os.path.dirname(here)], env=cenv(TAXOARENA_TMP=empty), capture_output=True, text=True)
        assert p.returncode == 0 and _nc(p.stdout.strip()) == _nc(empty), (p.stdout, p.stderr)
        assert os.listdir(empty) == [MARKER], os.listdir(empty)
        checks += 1
    finally:
        rmtree_robust(root)
    print("[SCRATCH] SELFTEST OK: %d checks (C0-C13); base %s; 0 calls, no DB" % (checks, base()))
    return 0


def main(argv):
    import argparse
    if "--run" in argv:
        i = argv.index("--run")
        cmd = argv[i + 1:]
        if cmd[:1] == ["--"]:
            cmd = cmd[1:]
        if not cmd:
            raise SystemExit("--run needs a command after --")
        return run_wrapped(cmd)
    if argv[:1] == ["--reap"]:
        _reap(int(argv[1]), argv[2])
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--where", action="store_true")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--purge-stale", action="store_true")
    ap.add_argument("--days", type=float, default=1.0)
    ap.add_argument("--all", action="store_true", help="--purge-stale also removes non-py_/run_ entries older than --days")
    ap.add_argument("--purge-legacy-temp", action="store_true")
    ap.add_argument("--since", default=LEGACY_SINCE)
    ap.add_argument("--root", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.where:
        print("[SCRATCH] base %s (TAXOARENA_TMP=%s); system temp %s"
              % (base(), os.environ.get("TAXOARENA_TMP", "-"), _SYSTEM_TEMP))
    if a.count:
        print("[SCRATCH] entries under %s: %d" % (base(), count_entries()))
    if a.purge_stale:
        r = purge_stale(days=a.days, root=a.root, dry_run=a.dry_run, all_entries=a.all)
        if r["failed"]:
            return 2
    if a.purge_legacy_temp:
        r = purge_legacy(root=a.root, since=a.since, dry_run=a.dry_run)
        if r["failed"]:
            for f in r["failed"][:20]:
                print("  failed: %s" % f)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
