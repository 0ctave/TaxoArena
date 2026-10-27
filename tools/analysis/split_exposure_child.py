"""SPLIT-EXPOSURE-SENSITIVITY - the ROUTE (A) consumer child (registrar's ruling a4d736a, programme L14867-L14881).

ONE CONSUMER PER PROCESS (A5). This module is launched by split_exposure_sensitivity.py as

  python tools/analysis/split_exposure_child.py --job <job.json> --out <result.json>

and NEVER imports cert_under_filter (whose stack_judge stub would collide with STACK, STACK-v2 and LEAF-POWERED). The
parent imports it only for its declarative specs (ROUTE_A_SPECS) and pure helpers; nothing here runs at import.

For each job the child, in order:
  A4  refuses to start if any judge credential is left in its environment (the parent strips them), and installs a
      socket guard: every outbound connect / connect_ex / create_connection raises and is COUNTED (must be 0);
  A1  checks the original's file against its pinned git blob and sha256-lf16 BEFORE importing it, unedited;
  A2  wraps sqlite3.connect for the duration of the consumer's import and calls ONLY (removed in a finally): every open,
      whatever the original asked for, becomes file:<absolute path>?mode=ro&immutable=1 after a -wal / -journal
      emptiness check (a non-empty one is a FAILED PRECONDITION); snapshots_frozen.db and a missing file are refused;
      each open is logged (path, URI, kind, count). For a removal run, the consumer's verdict cache(s) named in its spec
      are opened through that same immutable URI, copied to memory by the SQLite backup API, the removal applied to the
      COPY by the spec's DELETE statements (the original's INPUT, never its code), and the copy set PRAGMA query_only;
  A3  so no write can land: an INSERT / UPDATE / DELETE, a CREATE of a MISSING table or a committed change raises
      (a CREATE TABLE IF NOT EXISTS on an existing table and a no-op commit write nothing and are admitted); every
      proxied connection's total_changes must stay at its baseline; sha256_16, size and mtime of every opened file are
      taken at first open and asserted unchanged at the end;
  A6  runs the original's own entry point with stdout captured, and parses the REGISTERED headline line(s) by patterns
      pinned in the spec (each must match exactly one line); where an exact value is needed that the print rounds, the
      original's own local is read at its return (sys.setprofile), never recomputed; on the full run a probe
      (sys.settrace) records the original's scored set at a pinned source line (or from its locals at return);
  A7  reports everything; the PARENT evaluates C0 (the recorded headline reproduced to the digit) as the witness.

[ADDED 2026-09-23 after the READY review f33ca79 (D1, D3, D4, D5): (D1) total_changes is recorded when the original
closes a connection, so writes() never reads a closed one. (D3) sqlite3.dbapi2.connect is redirected as well, and an
AUDIT HOOK (PEP 578, active only inside the guarded window) refuses any sqlite3.connect whose database is not an
immutable URI or :memory: (this covers direct sqlite3.Connection construction and subclasses, which no Python wrapper can
intercept), any open() / os.open() for writing (__pycache__ excepted; sys.dont_write_bytecode is set), and process
creation; every refusal is recorded and makes the cell UNDETERMINED (BY VALIDITY) even if the original swallows the
exception. (D4) the same hook refuses socket.connect at the C level (a raw _socket connect included) and any read of a
.env file, the ONLY source of judge credentials in this project (load_env reads ROOT/.env): the socket guard is the
enforcing control of zero calls, the .env refusal the credential control; stripping environment variables is kept but
is descriptive. The .env refusal is BY FILE NAME: a credential kept in a file of another name is readable (reads are
not refused in general), so a key can be READ but never SENT: the socket guard is the control (the reviewer's
adversarial original 'env_key' scores for this reason, with 0 connection attempts). (D5) every tools/analysis module loaded in the child is reported with its blob / sha256-lf16 and
checked by the parent against the pins. DOCUMENTED LIMITS: connect() keyword arguments (factory, isolation_level,
detect_types, ...) are dropped by the redirect (the originals pass none that matters; C0 is the witness), and an
attribute ASSIGNED on a connection (row_factory, text_factory, isolation_level) lands on the proxy, not the connection,
so such an original fails closed (grep over the 7 originals and their helpers: 0 uses); ctypes /
C-extension file writes and a non-audited native socket are outside any Python-level control (grep over the 7 originals
and their 9 local helpers: 0 uses of dbapi2, sqlite3.Connection, _sqlite3, apsw, _socket, subprocess, os.system, ctypes
writes, or open(..., "w"/"a")); the opened-file fingerprints (A3) remain the after-the-fact backstop. Directory creation (os.mkdir) is NOT refused: rubric_512.open_cache calls os.makedirs(exist_ok=True) on an
existing directory. A refused write raises the child's Refused (not an OSError), so a library that retries on
PermissionError (tempfile.mkstemp on Windows) cannot spin; tempfile.gettempdir() is resolved before the guard.]

Reads that the originals repeat on large, immutable inputs (the eval DB, snapshots.db, the x12 history) are served from a
per-process memo of the identical query's rows (transparent: same SQL, same parameters, same immutable file).
"""
import argparse, contextlib, hashlib, inspect, io, json, os, socket, sqlite3, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
REAL_CONNECT = sqlite3.connect

SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD")
SECRET_PREFIXES = ("AZURE", "OPENAI", "XAI", "MISTRAL", "ANTHROPIC", "GROK", "DEEPSEEK", "GEMINI", "HF_")


def is_secret(name):
    u = name.upper()
    return any(m in u for m in SECRET_MARKERS) or u.startswith(SECRET_PREFIXES)


def clean_env(env):
    """A4: the child's environment with every judge credential removed."""
    return {k: v for k, v in env.items() if not is_secret(k)}


def lf_identity(path):
    raw = open(path, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(sha256_lf16=hashlib.sha256(lf).hexdigest()[:16], blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest())


def file_fp(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    st = os.stat(path)
    return [st.st_size, st.st_mtime_ns, h.hexdigest()[:16]]


def rss_line():
    try:
        if sys.platform == "win32":
            import ctypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong), ("PeakWorkingSetSize", ctypes.c_size_t),
                            ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]
            c = PMC(); c.cb = ctypes.sizeof(PMC)
            gcp = ctypes.windll.kernel32.GetCurrentProcess
            gcp.restype = ctypes.c_void_p
            gpmi = ctypes.windll.psapi.GetProcessMemoryInfo
            gpmi.argtypes = [ctypes.c_void_p, ctypes.POINTER(PMC), ctypes.c_ulong]
            gpmi(gcp(), ctypes.byref(c), c.cb)
            return "working set %.0f MB (peak %.0f MB)" % (c.WorkingSetSize / 2 ** 20, c.PeakWorkingSetSize / 2 ** 20)
        with open("/proc/self/status") as f:
            return " ".join(l.strip() for l in f if l.startswith(("VmRSS", "VmHWM")))
    except Exception as e:                           # printed, never a guard
        return "unavailable (%s)" % e


# ------------------------------------------------------------------------------------------ the ROUTE (A) specs
def _paired(header, line, b="b", c="c", n="n", sign=1, verdict=("v",)):
    return dict(kind="paired", patterns=[header, line], stat=dict(b=b, c=c, n=n, sign=sign), verdict=list(verdict))


ROUTE_A_SPECS = {
    "RUBRIC-512": dict(
        module="rubric_512", blob="81ae1d3914b0fef5358191a8b2033f9befc142f6", sha256_lf16="b99b3e0eb823429d",
        setup=[], entry="analyze", args=["bareq512_s42"],
        **_paired(dict(name="header", re=r"^=== RUBRIC-512 \(bareq512_s42\): clean-tree leaf rubric vs cached generic, Mistral,"
                                          r" R3 sample, (?P<n>\d+) key-decidable paired matches ===$"),
                  dict(name="primary", re=r"^  correct-verdict rate: cell (?P<pc>\d\.\d{3}) vs generic (?P<pg>\d\.\d{3}) "
                                           r"\((?P<d>[+-]\d\.\d{3})\) \| discordant (?P<b>\d+):(?P<c>\d+) \| McNemar "
                                           r"p=(?P<p>\d\.\d{4}) -> (?P<v>PASS|FAIL) \(REGISTERED PRIMARY\)$")),
        removal={"bareq512_s42.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
        probe=dict(mode="line", func="analyze", line="rows[mid] = (w == d, gen[mid] == d, anc)", expr="(mid, q, anc)"),
        anchor_sql=None, ret_locals=[]),
    "RUBRIC-512-SS": dict(
        module="rubric_512_ss", blob="f401668c0a2014b8d24def7882518565c26e0278", sha256_lf16="41aa59a4db8a7f2d",
        setup=[], entry="analyze", args=[],
        **_paired(dict(name="header", re=r"^=== RUBRIC-512-SS: (?P<n>\d+) key-decidable matches with cell, fresh-generic and"
                                          r" cached-generic verdicts ===$"),
                  dict(name="primary", re=r"^  CELL vs FRESH generic \(REGISTERED PRIMARY\) +cell (?P<pc>\d\.\d{3}) vs fresh "
                                           r"(?P<pg>\d\.\d{3}) \((?P<d>[+-]\d\.\d{3})\) \| (?P<b>\d+):(?P<c>\d+) \| "
                                           r"p=(?P<p>\d\.\d{4})  -> (?P<v>PASS|FAIL)$")),
        removal={"generic_ss.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
        probe=dict(mode="line", func="analyze",
                   line='rows[mid] = {"cell": cell[mid][0] == d, "fresh": fresh[mid] == d, "cached": cached[mid] == d, "anchor": cell[mid][1]}',
                   expr="(mid, q, cell[mid][1])"),
        anchor_sql=None, ret_locals=[]),
    "RUBRIC-512-R": dict(
        module="rubric_512_r", blob="70b10af1e66f6ca52a35b9d1896d56b72db9cca4", sha256_lf16="1347ea95753daf3e",
        setup=[], entry="analyze", args=[],
        **_paired(dict(name="header", re=r"^=== RUBRIC-512-R \((?P<judge>[^)]+)\): clean-tree leaf rubric vs generic, BOTH fresh,"
                                          r" (?P<n>\d+) key-decidable paired matches ===$"),
                  dict(name="primary", re=r"^  ALL           cell (?P<pc>\d\.\d{3}) vs generic (?P<pg>\d\.\d{3}) "
                                           r"\((?P<d>[+-]\d\.\d{3})\) \| (?P<b>\d+):(?P<c>\d+) \| p=(?P<p>\d\.\d{4}) -> "
                                           r"PRIMARY (?P<v>PASS|FAIL)$")),
        removal={"grok_reasoning_cell.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"],
                 "grok_reasoning_generic.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
        probe=dict(mode="line", func="analyze",
                   line='rows[mid] = (arms["cell"][mid][0] == d, arms["generic"][mid][0] == d, arms["cell"][mid][1], a in rj.TOP_CLUSTER and b in rj.TOP_CLUSTER)',
                   expr="(mid, q, arms['cell'][mid][1])"),
        anchor_sql=None, ret_locals=[]),
    "LEAF-POWERED": dict(
        module="leaf_powered", blob="ca46cee930dfdae1fd02eea6d6c04a47a261ebf9", sha256_lf16="71d81ed60c1a437b",
        setup=[], entry="analyze", args=[],
        # b = anchor-only right, c = leaf-only right; T = leaf - anchor = (c - b) / n
        **_paired(dict(name="header", re=r"^=== LEAF-POWERED: leaf rubric vs anchor rubric, (?P<n>\d+) key-decidable paired "
                                          r"matches ===$"),
                  dict(name="primary", re=r"^  POOLED   anchor (?P<pa>\d\.\d{3}) \| leaf (?P<pl>\d\.\d{3}) "
                                           r"\((?P<d>[+-]\d\.\d{3})\) \| (?P<b>\d+):(?P<c>\d+) \| McNemar p=(?P<p>\d\.\d{4})"
                                           r" -> PRIMARY (?P<v>PASS|FAIL)$"), sign=-1),
        removal={"leaf_powered.db": ["DELETE FROM verdicts WHERE mid IN (SELECT mid FROM schedule WHERE qid IN ({ids}))"]},
        probe=dict(mode="line", func="analyze", line='rows.append((anc, d["anchor"] == win, d["leaf"] == win))',
                   expr="(m, q, anc)"),
        anchor_sql=None, ret_locals=[]),
    "LADDER": dict(
        module="rubric_ladder", blob="d94831fc534eac9cc8bd753f32cb26bb84d844cf", sha256_lf16="ca0485db122070fa",
        setup=[], entry="analyze", args=[],
        # b = leaf-only right, c = anchor-only right; T = leaf - anchor = (b - c) / n; the registered PRIMARY is (a) AND (b)
        kind="paired",
        patterns=[dict(name="header", re=r"^=== LADDER \(S_ladder, key-decidable n=(?P<n>\d+), fully paired\) ===$"),
                  dict(name="primary_a", re=r"^PRIMARY \(a\) leaf > anchor: discordant (?P<b>\d+):(?P<c>\d+), one-sided McNemar "
                                             r"p = (?P<p>\d\.\d{4}) (?P<va>PASS|FAIL)$"),
                  dict(name="primary_b", re=r"^PRIMARY \(b\) monotone generic<=anchor<=stratum<=leaf: (?P<vb>PASS|FAIL)$")],
        stat=dict(b="b", c="c", n="n", sign=1), verdict=["va", "vb"],
        removal={"rubric_ladder.db": ["DELETE FROM verdicts WHERE match_id IN ({mids})"]},
        probe=dict(mode="return", func="analyze", expr="[(mid, meta[mid][0], None) for mid in common]"),
        anchor_sql=dict(db_expr="DB", sql="SELECT match_id, unit FROM verdicts WHERE arm='anchor'"), ret_locals=[]),
    "STACK": dict(
        module="stack_judge", blob="6acfc3195d05c160afd5c01648d9f24835703c8e", sha256_lf16="a368321cd11066d0",
        setup=[["PROMPT", "v1"], ["JUDGE", "mistral"], ["ALL_X12", False], ["DATACARD", False]], entry="analyze", args=[],
        kind="accuracy",
        patterns=[dict(name="header", re=r"^=== STACK \(reference \+ v1 mechanics \+ anchor rubric\), Mistral, (?P<judged>\d+) "
                                          r"judged \((?P<invalid>\d+) invalid\), (?P<n>\d+) key-decidable ===$"),
                  dict(name="crit1", re=r"^  \(1\) all-decidable accuracy >= 0\.839 +(?P<acc>\d\.\d{3}) -> (?P<v>OK|FAIL)$")],
        stat=dict(acc_local="acc", n_local="n"), verdict=["v"],
        removal={"stack_v2.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
        probe=dict(mode="line", func="analyze",
                   line='rows[mid] = {"st": w == d, "tie": w == "TIE", "top": a in TOP4 and b in TOP4, "short_correct": L[(q, d)] < L[(q, wrong)], "w": w, "wrong": wrong,',
                   expr="(mid, q, None)"),
        anchor_sql=dict(db_expr="cache_path()", sql="SELECT match_id, anchor FROM verdicts"), ret_locals=["acc", "n"]),
    "STACK-v2": dict(
        module="stack_judge", blob="6acfc3195d05c160afd5c01648d9f24835703c8e", sha256_lf16="a368321cd11066d0",
        setup=[["PROMPT", "v2"], ["JUDGE", "mistral"], ["ALL_X12", False], ["DATACARD", False]], entry="analyze", args=[],
        kind="accuracy",
        patterns=[dict(name="header", re=r"^=== STACK-v2 \(reference \+ v2 mechanics \+ anchor rubric\), Mistral, (?P<judged>\d+) "
                                          r"judged \((?P<invalid>\d+) invalid\), (?P<n>\d+) key-decidable ===$"),
                  dict(name="crit1", re=r"^  \(1\) all-decidable accuracy >= 0\.839 +(?P<acc>\d\.\d{3}) -> (?P<v>OK|FAIL)$")],
        stat=dict(acc_local="acc", n_local="n"), verdict=["v"],
        removal={"stack_v2_promptv2.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
        probe=dict(mode="line", func="analyze",
                   line='rows[mid] = {"st": w == d, "tie": w == "TIE", "top": a in TOP4 and b in TOP4, "short_correct": L[(q, d)] < L[(q, wrong)], "w": w, "wrong": wrong,',
                   expr="(mid, q, None)"),
        anchor_sql=dict(db_expr="cache_path()", sql="SELECT match_id, anchor FROM verdicts"), ret_locals=["acc", "n"]),
    "J6": dict(
        module="j6_rubrics", blob="a898515f4184537e4918d515258579222981f3d4", sha256_lf16="de747c39fc368ce0",
        setup=[], entry="analyze", args=[],
        kind="paired",
        patterns=[dict(name="primary", re=r"^  contrastive vs mistral-induced \(PRIMARY\) +(?P<px>\d\.\d{3}) vs (?P<py>\d\.\d{3}) "
                                           r"\((?P<d>[+-]\d\.\d{3})\) \| (?P<b>\d+):(?P<c>\d+) \| p=(?P<p>\d\.\d{4}) "
                                           r"n=(?P<n>\d+)  -> PRIMARY (?P<v>PASS|FAIL)$")],
        stat=dict(b="b", c="c", n="n", sign=1), verdict=["v"],
        removal={"rubric_j6.db": ["DELETE FROM verdicts WHERE qid IN ({ids})"]},
        probe=dict(mode="line", func="analyze",
                   line='rows[mid] = {arm: arms[arm][0] == d for arm in ARMS}; rows[mid]["generic"] = (gen[mid] == d) if mid in gen else None; rows[mid]["anchor"] = anc',
                   expr="(mid, q, anc)"),
        anchor_sql=None, ret_locals=[]),
}

# The format literal each pinned pattern must parse, located in the original's source (checked by the parent's selftest):
# (consumer, pattern name, the literal's leading text, a dummy argument tuple rendering it).
FORMAT_PINS = [
    ("RUBRIC-512", "header", "=== RUBRIC-512 (%s)", ("bareq512_s42", 946)),
    ("RUBRIC-512", "primary", "  correct-verdict rate:", (0.773, 0.755, 0.018, 42, 25, 0.0498, "PASS")),
    ("RUBRIC-512-SS", "header", "=== RUBRIC-512-SS:", (946,)),
    ("RUBRIC-512-SS", "primary", "  %-48s %s %.3f vs %s %.3f",
     ("CELL vs FRESH generic (REGISTERED PRIMARY)", "cell", 0.773, "fresh", 0.763, 0.010, 35, 26, 0.3057, "  -> FAIL")),
    ("RUBRIC-512-R", "header", "=== RUBRIC-512-R (%s)", ("grok-4-1-fast-reasoning", 946)),
    ("RUBRIC-512-R", "primary", "  ALL           cell", (0.842, 0.842, 0.0, 24, 24, 1.0, "FAIL")),
    ("LEAF-POWERED", "header", "=== LEAF-POWERED:", (786,)),
    ("LEAF-POWERED", "primary", "  POOLED   anchor", (0.934, 0.931, -0.003, 9, 7, 0.8036, "FAIL")),
    ("LADDER", "header", "=== LADDER (S_ladder", (967,)),
    ("LADDER", "primary_a", "PRIMARY (a) leaf > anchor", (35, 38, 0.68, "FAIL")),
    ("LADDER", "primary_b", "PRIMARY (b) monotone", ("FAIL",)),
    ("STACK", "header", "=== STACK%s (reference + %s mechanics", ("", "v1", 1974, 1, 944)),
    ("STACK-v2", "header", "=== STACK%s (reference + %s mechanics", ("-v2", "v2", 1974, 0, 944)),
    ("STACK", "crit1", "  %-80s %.3f -> %s", ("(1) all-decidable accuracy >= 0.839", 0.843, "OK")),
    ("J6", "primary", "  %-46s %.3f vs %.3f (%+.3f)",
     ("contrastive vs mistral-induced (PRIMARY)", 0.761, 0.779, -0.018, 23, 40, 0.043, 944, "  -> PRIMARY FAIL")),
]


# ------------------------------------------------------------------------------------------ guards (installed per job)
class Refused(Exception):
    """A redirect refusal inside a consumer call (a write, a missing file, snapshots_frozen.db): the cell is refused."""


class SidecarRefused(Exception):
    """A non-empty -wal / -journal: a FAILED PRECONDITION of the whole run."""


ATTEMPTS = []                 # outbound connection attempts (refused): must be 0
REFUSALS = []                 # other refused operations inside the guarded window (writes, .env reads, processes)
GUARD = dict(active=False)    # the audit hook acts only while a consumer is imported / called
ENV_READS = []                # refused reads of a .env file (the credentials' only source in this project)
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
PROCESS_EVENTS = ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.startfile", "os.fork")


def _refuse_socket(*a, **k):
    ATTEMPTS.append(repr(a[1:2] or a[:1])[:120])
    raise ConnectionRefusedError("[A4] outbound connection refused in the consumer child (zero calls enforced)")


def install_socket_guard():
    """Layer 1 (Python): socket.socket.connect / connect_ex / create_connection refuse and count."""
    socket.socket.connect = _refuse_socket
    socket.socket.connect_ex = _refuse_socket
    socket.create_connection = _refuse_socket


def _immutable_or_memory(db):
    s = str(db)
    return s == ":memory:" or (s.startswith("file:") and s.endswith("?mode=ro&immutable=1"))


def _refusal(what):
    """Record a refusal (the first 50 verbatim, then a count). The refusal raises Refused, NOT an OSError: a library that
    retries on PermissionError (tempfile.mkstemp on Windows loops on it) must not spin; the import or call fails."""
    REFUSAL_COUNT[0] += 1
    if len(REFUSALS) < 50:
        REFUSALS.append(what)


REFUSAL_COUNT = [0]


def _audit(event, args):
    """Layer 2 (audit hook, PEP 578), active only inside the guarded window. It sees what the Python-level wrappers
    cannot: a raw _socket connect (socket.connect), sqlite3.dbapi2.connect and direct sqlite3.Connection construction
    (sqlite3.connect: any database that is not an immutable URI or :memory: is refused), an open() or os.open() for
    writing, a read of a .env file (the credentials' only source here), and process creation."""
    if not GUARD["active"]:
        return
    if event == "socket.connect":
        ATTEMPTS.append(repr(args[1:2])[:120])
        raise ConnectionRefusedError("[A4] outbound connection refused in the consumer child (audit hook; zero calls)")
    if event == "sqlite3.connect":
        if not _immutable_or_memory(args[0]):
            _refusal("sqlite3.connect %s" % str(args[0])[:160])
            raise Refused("[A3] refused: a database opened outside the redirect (%s): dbapi2 / Connection construction"
                          % str(args[0])[:160])
        return
    if event == "open":
        path, mode, flags = (list(args) + [None, None, None])[:3]
        if isinstance(path, int):
            return
        p = str(path)
        if os.path.basename(p).lower() == ".env":
            ENV_READS.append(p)
            _refusal("open .env %s" % p)
            raise Refused("[A4] refused: %s holds the judge credentials; the consumer child never reads it" % p)
        writing = bool(mode and any(ch in str(mode) for ch in "wax+")) or bool(flags and (int(flags) & WRITE_FLAGS))
        if writing and "__pycache__" not in p and not p.endswith(".pyc"):
            _refusal("open for writing %s (mode %r, flags %r)" % (p[:160], mode, flags))
            raise Refused("[A3] refused: the consumer child opens no file for writing (%s)" % p[:160])
        return
    if event.startswith(PROCESS_EVENTS):
        _refusal(event)
        raise Refused("[A4] refused: %s in the consumer child" % event)


def install_audit_guard():
    """Layer 2 (audit hook). Hooks cannot be removed; GUARD['active'] scopes it to the consumer's import and calls."""
    sys.addaudithook(_audit)


def install_guards(job):
    sys.dont_write_bytecode = True
    import tempfile
    tempfile.gettempdir()         # resolved (and cached) BEFORE the guard: its first call probes the temp dir with writes,
                                  # which third-party imports (scipy.stats) trigger; a later tempfile WRITE is still refused
    if job.get("socket_guard", True):
        install_socket_guard()
    install_audit_guard()


class MemoCursor(object):
    def __init__(self, rows):
        self._rows = rows; self._i = 0

    def __iter__(self):
        return iter(self._rows)

    def fetchone(self):
        if self._i < len(self._rows):
            self._i += 1
            return self._rows[self._i - 1]
        return None

    def fetchall(self):
        r = self._rows[self._i:]; self._i = len(self._rows)
        return list(r)

    def close(self):
        pass


MEMO = {}


class ROConn(object):
    """The connection handed to the original: the immutable (or in-memory, query_only) connection, its total_changes
    baseline, and a memo of SELECT results for inputs that are not removal targets."""

    def __init__(self, real, path, memo):
        object.__setattr__(self, "_real", real)
        object.__setattr__(self, "_path", path)
        object.__setattr__(self, "_memo", memo)
        object.__setattr__(self, "baseline", real.total_changes)
        object.__setattr__(self, "closed_changes", None)

    def close(self):
        """D1 (READY f33ca79): the originals close their connections; total_changes is recorded AT CLOSE so writes()
        never reads a closed connection."""
        if self.closed_changes is None:
            object.__setattr__(self, "closed_changes", self._real.total_changes)
        return self._real.close()

    def changes(self):
        return self.closed_changes if self.closed_changes is not None else self._real.total_changes

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *exc):
        return self._real.__exit__(*exc)

    def execute(self, sql, *params):
        if self._memo and sql.lstrip()[:6].upper() == "SELECT":
            key = (self._path, sql, tuple(params[0]) if params else ())
            if key not in MEMO:
                MEMO[key] = self._real.execute(sql, *params).fetchall()
            return MemoCursor(MEMO[key])
        return self._real.execute(sql, *params)

    def __getattr__(self, name):
        return getattr(self._real, name)


class Redirect(object):
    def __init__(self, removal_sql):
        self.removal_sql = removal_sql or {}
        self.removal = None              # dict(ids=[...], mids=[...]) during a removal run
        self.log = {}                    # path -> dict(uri, kinds, count)
        self.fp = {}                     # path -> fingerprint at first open
        self.conns = []
        self.removed_rows = {}

    def connect(self, db, *a, **k):
        s = str(db)
        if s == ":memory:":
            self.log.setdefault(":memory:", dict(uri=":memory:", kinds=["memory"], count=0))["count"] += 1
            return REAL_CONNECT(":memory:")
        path = s[len("file:"):].split("?", 1)[0] if s.startswith("file:") else s
        path = os.path.abspath(path)
        base = os.path.basename(path)
        if "snapshots_frozen" in base.lower():
            raise Refused("[A2] refused: %s (snapshots_frozen.db is never opened)" % path)
        if not os.path.isfile(path):
            raise Refused("[A3] refused: %s does not exist; a read-only open cannot create it" % path)
        for suf in ("-wal", "-journal"):
            if os.path.exists(path + suf) and os.path.getsize(path + suf) > 0:
                raise SidecarRefused("[SIDECAR] %s%s is non-empty (%d bytes): a failed precondition"
                                     % (path, suf, os.path.getsize(path + suf)))
        if path not in self.fp:
            self.fp[path] = file_fp(path)
        uri = "file:%s?mode=ro&immutable=1" % path.replace("\\", "/")
        real = REAL_CONNECT(uri, uri=True)
        kind = "immutable"
        target = base in self.removal_sql
        if target and self.removal is not None:
            mem = REAL_CONNECT(":memory:")
            real.backup(mem)
            real.close()
            before = mem.total_changes
            for sql in self.removal_sql[base]:
                mem.execute(sql.format(ids=",".join(str(int(q)) for q in self.removal["ids"]) or "NULL",
                                       mids=",".join(str(int(m)) for m in self.removal["mids"]) or "NULL"))
            mem.commit()
            self.removed_rows[base] = self.removed_rows.get(base, 0) + (mem.total_changes - before)
            mem.execute("PRAGMA query_only = ON")
            real = mem
            kind = "in-memory copy of the immutable URI, removal applied, PRAGMA query_only"
        e = self.log.setdefault(path, dict(uri=uri, kinds=[], count=0))
        e["count"] += 1
        if kind not in e["kinds"]:
            e["kinds"].append(kind)
        c = ROConn(real, path, memo=not target)
        self.conns.append(c)
        return c

    def writes(self):
        return [c._path for c in self.conns if c.changes() != c.baseline]


@contextlib.contextmanager
def redirected(rd):
    """A2 for the consumer's import and calls only: sqlite3.connect AND sqlite3.dbapi2.connect are redirected; the audit
    hook is active (direct Connection construction and any non-immutable open refuse)."""
    import sqlite3.dbapi2 as dbapi2
    sqlite3.connect = rd.connect
    dbapi2.connect = rd.connect
    GUARD["active"] = True
    try:
        yield
    finally:
        GUARD["active"] = False
        sqlite3.connect = REAL_CONNECT
        dbapi2.connect = REAL_CONNECT


# ------------------------------------------------------------------------------------------ capture (A6)
def parse_headline(patterns, out):
    import re
    lines = out.splitlines()
    got = {}
    for p in patterns:
        rx = re.compile(p["re"])
        hits = [m for m in (rx.match(l) for l in lines) if m]
        if len(hits) != 1:
            raise Refused("[A6] the pinned headline line %r matched %d lines of the original's stdout (exactly 1 required)"
                          % (p["name"], len(hits)))
        got.update(hits[0].groupdict())
    return got


def pinned_lineno(func, text):
    src, start = inspect.getsourcelines(func)
    hits = [start + i for i, l in enumerate(src) if l.strip() == text]
    if len(hits) != 1:
        raise Refused("[A6] the probe line %r occurs %d times in %s (exactly 1 required)" % (text, len(hits), func.__name__))
    return hits[0]


def call_captured(fn, args, probe_func=None, probe=None, ret_func=None, ret_names=()):
    """Run the original with stdout captured. probe (full run only): sys.settrace on the probe function's frame; ret_names:
    sys.setprofile reads those locals at the return of ret_func."""
    buf = io.StringIO()
    scored, ret = [], {}
    tracer = prof = None
    if probe is not None:
        code = probe_func.__code__
        lineno = pinned_lineno(probe_func, probe["line"]) if probe["mode"] == "line" else None

        def local(frame, event, arg):
            if event == "line" and lineno is not None and frame.f_lineno == lineno:
                scored.append(tuple(eval(probe["expr"], dict(frame.f_globals, **frame.f_locals))))
            elif event == "return" and probe["mode"] == "return":
                scored.extend(tuple(x) for x in eval(probe["expr"], dict(frame.f_globals, **frame.f_locals)))
            return local

        def tracer(frame, event, arg):
            return local if (event == "call" and frame.f_code is code) else None
    if ret_names:
        rcode = ret_func.__code__

        def prof(frame, event, arg):
            if event == "return" and frame.f_code is rcode:
                ret.update({k: frame.f_locals.get(k) for k in ret_names})
    try:
        if tracer:
            sys.settrace(tracer)
        if prof:
            sys.setprofile(prof)
        with contextlib.redirect_stdout(buf):
            fn(*args)
    finally:
        sys.settrace(None); sys.setprofile(None)
    return buf.getvalue(), scored, ret


# ------------------------------------------------------------------------------------------ the job
def run_job(job):
    spec = job["spec"]
    res = dict(pid=os.getpid(), consumer=job["consumer"], results=[], probe=None, anchors=None, error=None, sidecar=None,
               connlog={}, attempts=0, import_opens=[], secrets_left=[], fp_changed=[], rss=None, t=0.0, refusals=[],
               env_reads_refused=[], local_modules={})
    t0 = time.time()
    res["secrets_left"] = sorted(k for k in os.environ if is_secret(k))
    if res["secrets_left"]:
        res["error"] = "[A4] judge credentials present in the child's environment: %s" % res["secrets_left"]
        return res
    install_guards(job)
    mdir = spec.get("module_dir") or HERE
    mpath = os.path.join(mdir, spec["module"] + ".py")
    ident = lf_identity(mpath)
    res["identity"] = ident
    if ident["blob"] != spec["blob"] or ident["sha256_lf16"] != spec["sha256_lf16"]:
        res["error"] = ("[A1] %s is blob:%s / sha256-lf16:%s, pinned blob:%s / sha256-lf16:%s"
                        % (mpath, ident["blob"], ident["sha256_lf16"], spec["blob"], spec["sha256_lf16"]))
        return res
    if mdir not in sys.path:
        sys.path.insert(0, mdir)
    if HERE not in sys.path:
        sys.path.insert(1, HERE)
    rd = Redirect(spec.get("removal"))
    try:
        with redirected(rd):
            import importlib
            mod = importlib.import_module(spec["module"])
            res["import_opens"] = sorted(rd.log)
            for name, value in spec.get("setup", []):
                setattr(mod, name, value)
            fn = getattr(mod, spec["entry"])
            probe_fn = getattr(mod, spec["probe"]["func"]) if spec.get("probe") else None
            for i, rs in enumerate(job["sets"]):
                rd.removal = None if (not rs["ids"] and not rs["mids"]) else rs
                rd.removed_rows = {}
                one = dict(i=i, parsed=None, ret=None, error=None, removed_rows=None, t=None)
                ts = time.time()
                try:
                    probe = spec.get("probe") if (i == 0 and job.get("probe")) else None
                    out, scored, ret = call_captured(fn, spec.get("args", []), probe_fn, probe, fn, spec.get("ret_locals", []))
                    one["parsed"] = parse_headline(spec["patterns"], out)
                    one["ret"] = ret
                    one["removed_rows"] = dict(rd.removed_rows)
                    if probe is not None:
                        res["probe"] = [list(s) for s in scored]
                    w = rd.writes()
                    if w:
                        raise Refused("[A3] a write landed on %s (total_changes moved)" % w)
                except SidecarRefused as e:
                    res["sidecar"] = str(e); res["results"].append(one); break
                except Exception as e:                      # a refusal or any failure: this cell is not scoreable
                    one["error"] = "%s: %s" % (type(e).__name__, str(e)[:400])
                    one["trace"] = traceback.format_exc()[-1500:]
                one["t"] = time.time() - ts
                res["results"].append(one)
            if job.get("probe") and spec.get("anchor_sql") and res["probe"] is not None and not res["results"][0]["error"]:
                a = spec["anchor_sql"]
                con = sqlite3.connect(eval(a["db_expr"], vars(mod)))
                amap = {int(r[0]): r[1] for r in con.execute(a["sql"])}
                res["anchors"] = {str(k): v for k, v in amap.items()}
    except SidecarRefused as e:
        res["sidecar"] = str(e)
    except Exception as e:
        res["error"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        res["trace"] = traceback.format_exc()[-1500:]
    res["connlog"] = rd.log
    res["attempts"] = len(ATTEMPTS)
    res["attempt_log"] = list(ATTEMPTS)
    res["refusals"] = list(REFUSALS) + (["... %d refusals in all" % REFUSAL_COUNT[0]] if REFUSAL_COUNT[0] > len(REFUSALS) else [])
    res["env_reads_refused"] = list(ENV_READS)
    hdir = os.path.abspath(job.get("helper_dir") or HERE)
    res["local_modules"] = {n: lf_identity(m.__file__) for n, m in sorted(sys.modules.items())
                            if getattr(m, "__file__", None) and os.path.dirname(os.path.abspath(m.__file__)) == hdir
                            and n not in ("__main__", "__mp_main__", "split_exposure_child")}   # the child: pinned by the parent
    for p, fp in rd.fp.items():
        if file_fp(p) != fp:
            res["fp_changed"].append(p)
    res["fp"] = rd.fp
    res["rss"] = rss_line()
    res["t"] = time.time() - t0
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    sys.dont_write_bytecode = True
    job = json.load(open(a.job, encoding="utf-8"))
    res = run_job(job)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f)


if __name__ == "__main__":
    main()
