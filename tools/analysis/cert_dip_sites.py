"""cert_dip_sites.py: CERT-DIP-SITES (lead #7 of docs/agents/plans/2026-11-06_leads.md, b42d58ef; author decision
D-2026-11-06-3). EXPLORATORY readout; ZERO calls (no judge, no LLM, no embedding call); CPU only; a POOL READER under
CONTEXT rule 7 (W1-W5).

PLAN OF RECORD (it governs; this docstring restates it and never replaces it): docs/agents/plans/2026-11-07_cert_dip_sites.md,
committed 67c0a16a BEFORE any statistic on tree members' vectors. Question: under CERT-RESOLUTION's prefix-closed hierarchical
BH over nested sites (per-family q = 0.05), which sites of the trees of record are MODAL along their own split axis by
CERT-SPLIT-DIP's split-dip rule (unchanged), are Chemistry n00000006 and Engineering n00000015 (bareq512_s42) among them, and
how does the MODAL set sit beside the J hierarchical set of the same tree? bareq512_s42 (R512, id-disjoint only) and
af_clean_s42 (R256, content-closed) are read in separate blocks and NEVER joined (S4).

WHAT IT READS (plan section 2): the site-null CSVs and dag_snapshots.jsonl last records of record, located and pinned by
cert_resolution.locate with CERT-RESOLUTION's pins; the snapshot graphs from snapshots.db (snapshots_frozen.db is never
opened); member vectors from embeddings_cache.db via embedder_guard.read_vectors (first `slice` of 4,096 floats, unit). Every
DB through pool_guard.open_ro (mode=ro&immutable=1, sidecars checked); a process-wide connect guard admits nothing else; the
sha256 of both DB files is printed before and after --run and must be equal. The pool p2dca21ab5f4ef3ae is printed first,
"printed, not used" (its id file hashed; the dataset DB is not opened; members are construction rows).

ARMS (plan section 3; t = 0 bareq512_s42, 1 af_clean_s42; i = 0-based CSV row): OBS = the rule on the site's member rows
(ascending id); NULL = M = 10 draws per site from the J site null's generator in its exact-in-distribution eigen form (mean +
Z diag(s) V^T / sqrt(n), C = U diag(s) V^T the thin SVD of the centred rows; MIX-LRT-SITE ruling A6), draw m from
numpy default_rng([202611073, t, i, m]); PLANT = one fresh delta-6 plant per site via cert_planted.direction / halves /
plant_rows unchanged (u seed 202611071000 + 1000 t + i, halves seed 202611072000 + 1000 t + i, each minus the record offset);
J = the CSV's p = (k + 1) / 301 through cert_resolution.hierarchical_bh, which must reproduce the recorded J sets.
THE RULE: cert_split_dip.dip_site (blob 1d46cd73, imported unchanged; diptest 0.11.0 pinned): R = 20 halvings, spherical
k-means k = 2 on half A, Hartigan's dip of half B on c1 - c2, p_site = min(1, 2 x median); site names
"CDS|<tree>|<node>|OBS", "...|N<m>", "...|P6". BH: cert_resolution.bh_cutoff / by_q / site_structure / hierarchical_bh
unchanged, p as exact Fractions of the float.

WORDS (plan sections 5-6, 9): G0 SIZE-OK iff the NULL draws are p <= 0.05 at a rate <= 0.10 with 95% CP upper <= 0.15
(denominator 10 x m), else ANTI-CONSERVATIVE and every word of the tree reads NOT EVALUABLE; W1 SOME / NONE-POWERED (PLANT
certifies >= 0.5 of m) / NONE-UNDERPOWERED; W2 (bareq512_s42) BOTH / ONE (<site>) / NEITHER; W3 MORE / SAME / FEWER (|D| vs
|J| within the tree); site words M1 MODAL (split-dip) ..., M2 split-dip BH ..., M3 split-dip p <= 0.05 ...; UNTESTED where a
site ancestor was not rejected. F-DIP fires on a tree iff G0 ANTI-CONSERVATIVE or >= 3 of 10 NULL-TREE replicates reject.
Predictions P1-P9 as the plan (section 8).

LAUNCH SEQUENCE (zero calls; at most 3 worker processes, BLAS single-threaded each):
  python tools/analysis/cert_dip_sites.py --selftest      # fixtures in a sandbox (scratch_dir, E:); every branch, values
  python tools/analysis/cert_dip_sites.py --mutants       # MUTANTS below on copies in the sandbox; every one must be KILLED
  python tools/analysis/cert_dip_sites.py --probe         # rule 7: W1 exclusive-open probe, W2 process list, W4 free RAM
  python tools/analysis/cert_dip_sites.py --dry-run       # READS the pool (probe first): pins, members, guards, counts; no p
  python tools/analysis/cert_dip_sites.py --run --workers 3 --out E:/TaxoArena_tmp/cert_dip_sites/record
                                                          # clean tracked script, selftest gate, probe, DB sha before/after;
                                                          # cache <out>/cache.jsonl, meta pinned at first launch; resumable
  python tools/analysis/cert_dip_sites.py --analyze --out <same>   # opens no DB; complete cache -> write-once outcome
  Defaults: --data-root $TAXOARENA_DATA_ROOT or the main checkout (the DBs are not in a worktree); text inputs from this
  checkout then the main checkout, pin-matched; --pylib E:/TaxoArena_tmp/cert_split/pylib (diptest 0.11.0).
  --pilot N: the first N sites of each tree into <out>/pilot_cache.jsonl; --analyze --pilot N writes *_PILOT.txt and REFUSES
  above 5% missing tasks (no judge: the truncation guard reads failed tasks, which are never cached).
  Outputs (never committed): CERT_DIP_SITES_OUTCOME.txt, cert_dip_sites_sites.csv (write-once, mode x); *_partial / *_PILOT
  otherwise; back up to E:/TaxoArena_backup_2026-11-06_cert-dip-sites with SHA256SUMS.txt.

SELFTEST (--selftest): ST1 pins; ST2 regionQueryIds; ST3 the null generator draw for draw against cert_split_dip.gen_matched;
ST4 the plant seeds; ST5 every word function at its boundaries; ST6 the rule-7 probe (classification, exclusive open, RAM bar);
ST7 end to end on fixture DBs through main(): --dry-run (0 dip calls), --run (workers 1 and 2 equal), --analyze (the MODAL sets,
W1-W3, G0, F-DIP, UNTESTED, site words, P lines, S4), independent recomputation of an OBS p and NULL / PLANT row hashes, resume
without recomputation, write-once, meta mismatch, partial, pilot and every precondition refusal; ST8 engineered caches through
--analyze for the remaining word branches (NONE-POWERED, NONE-UNDERPOWERED, NOT EVALUABLE incl. its printed lines, BOTH,
NEITHER, SAME, F-DIP by replicates 2 vs 3, alpha inclusive, prediction band endpoints).
MUTANTS: table filled at the build commit (see the commit message and the MUTANT TABLE paragraph at the end of this docstring).

MUTANT TABLE (--mutants, 2026-11-07, copies in the scratch_dir sandbox on E:, one at a time; each copy's --selftest must FAIL):
46 / 46 KILLED. Killing check in brackets.
  X01 G0 rate bar strict [ST5 G0 70/700]; X02 G0 CP clause dropped [ST5 2/20]; X03 G0 denominator m [ST7 G0 0 of 60];
  X04 G0 on OBS, wrong population [ST7 G0]; X05 MODAL set from the flat BH [ST7 D = 3 of 6]; X06 hierarchy without ancestors,
  prefix closure lost [ST7 D]; X07 BH level 0.10 [ST1]; X08 site alpha strict [ST5]; X09 PLANT alpha strict [ST8 3 of 6];
  X10 W1 power share strict [ST5 35/70]; X11 W2 BOTH on one site [ST5]; X12 W2 skips the G0 gate [ST5]; X13 W3 against the
  flat set [ST7 W3 MORE]; X14 W3 MORE / FEWER swapped [ST5]; X15 F-DIP bar 2 [ST5]; X16 F-DIP without its G0 clause [ST5];
  X17 NOT EVALUABLE path omits the W2 line [ST8 ANTI]; X18 members checked at the first site only [ST7 n_mismatch at the
  last site]; X19 members without the DFS [ST2]; X20 embedder guard skipped [ST7 bad_vmfmu]; X21 J reproduction unchecked
  [ST7 j_wrong]; X22 zero sites admitted [ST7 zero_sites]; X23 slice 4 for every tree [ST7 --run]; X24 NULL seed m + 1 [ST3];
  X25 NULL without the site's moments [ST3 draw for draw]; X26 PLANT delta 4 [ST4]; X27 halving name without the tree [ST7
  independent OBS halving p]; X28 DB after-state not compared [ST7 touch]; X29 outcome from a partial cache [ST7 partial];
  X30 outcome not write-once [ST7 second --analyze]; X31 resume recomputes [ST7 resume]; X32 meta mismatch ignored [ST7 meta];
  X33 workers cap 4 [ST7 --workers 4]; X34 probe admits a JVM [ST6]; X35 probe admits a busy file [ST6]; X36 RAM bar 1 GB
  [ST6]; X37 pilot truncation guard off [ST7 pilot 4 of 24]; X38 --no-probe on any root [ST7]; X39 P5 band endpoint [ST8];
  X40 ANTI path drops the P3 NOT SCORED line [ST8 ANTI]; X41 site rows truncated [ST7 --run]; X42 graph vs jsonl structure
  unchecked [ST7 graph_mismatch]; X43 site words skip the G0 gate [ST5]; X44 MODAL set from the PLANT arm [ST7 D]; X45 NULL-TREE
  on the OBS arm [ST7 F-DIP]; X46 P2 bar 2 [ST8 repl2].
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported: single-threaded BLAS per process
    os.environ[_v] = "1"

import argparse  # noqa: E402
import contextlib  # noqa: E402
import csv  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import shutil  # noqa: E402
import sqlite3  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from fractions import Fraction  # noqa: E402

import numpy as np  # noqa: E402

SELF = os.path.abspath(__file__)
SELF_DIR = os.path.dirname(SELF)
HERE = os.environ.get("CDS_SRC_DIR") or SELF_DIR          # the record modules live here (a mutant copy points back)
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tempfile; import scratch_dir  # noqa: E401,E402  TEMP-SPRAWL: temp on E:, removed at exit
import pool_guard  # noqa: E402
import embedder_guard as EG  # noqa: E402
import cert_resolution as CR  # noqa: E402
import cert_split_dip as CSD  # noqa: E402

CP = CSD.CP
TAG = "[CDS]"
TEST = "CERT-DIP-SITES"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ================================================================================================ pins
def lf_bytes(path):
    with open(path, "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def pins_of_bytes(data):
    data = data.replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest(),
                lf16=hashlib.sha256(data).hexdigest()[:16],
                crlf16=hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest()[:16])


def pins_of(path):
    return pins_of_bytes(lf_bytes(path))


CSD_BLOB = "1d46cd733e8728a35a30e5c88df5a564d1d5961a"     # cert_split_dip.py of record (CERT-SPLIT-DIP's run)
CR_BLOB = "dbe9425dc406edcd41661a6df4e00d33b44299b6"      # cert_resolution.py of record (READY 7375a97)
EG_BLOB = "3fd9aea5b220828f7e6bcb3f115c43aa6743218d"      # embedder_guard.py on main at 298b9cc9
DIPTEST_PIN = dict(version="0.11.0", files=4, sha256="302edebf89c97588e9e114d147bc9ff0ae1553636a385d956db0f2afad24b34f")
MODULE_PINS = (("cert_split_dip.py", CSD, CSD_BLOB), ("cert_resolution.py", CR, CR_BLOB), ("embedder_guard.py", EG, EG_BLOB))


def module_pins():
    out = {}
    for name, mod, blob in MODULE_PINS:
        got = pins_of(mod.__file__)["blob"]
        if got != blob:
            refuse("%s is blob %s, not the pinned %s (imported unchanged, never copied)" % (name, got, blob))
        out[name] = got
    out["cert_planted.py"] = CSD.CP_BLOB          # asserted by cert_split_dip at its import
    return out


if CR.MUTANT is not None:
    refuse("cert_resolution.MUTANT is set")

# ================================================================================================ constants (the plan)
PLAN_REL = "docs/agents/plans/2026-11-07_cert_dip_sites.md"
PLAN_COMMIT = "67c0a16a"
POOL_ID = "p2dca21ab5f4ef3ae"
MODEL = "qwen3-embedding:latest"
RAW_DIM = 4096
ALPHA = 0.05                       # per-site bar of the rule (cert_split_dip.certified)
Q = Fraction(1, 20)                # BH level, flat and per family
M_NULL = 10
DELTA = 6
NULL_SEED, U_SEED_P, H_SEED_P = 202611073, 202611071000, 202611072000
G0_RATE, G0_CP = Fraction(1, 10), 0.15
FDIP_REPL = 3
POWER_SHARE = Fraction(1, 2)
MAX_WORKERS = 3
RAM_GB = 12.0
PILOT_MISSING_MAX = 0.05
NAMED = ("n00000006", "n00000015")
PYLIB_DEFAULT = "E:/TaxoArena_tmp/cert_split/pylib"
OUTCOME, SITES_CSV = "CERT_DIP_SITES_OUTCOME.txt", "cert_dip_sites_sites.csv"
FIXTURE_MARK = ".cds_fixture"
DB_NAMES = ("embeddings_cache.db", "snapshots.db")
PROBE_FILES = ("embeddings_cache.db", "embeddings_cache.db-wal", "embeddings_cache.db-shm", "snapshots.db", "snapshots.db-wal",
               "snapshots.db-shm", "snapshots_frozen.db", "snapshots_frozen.db-wal", "snapshots_frozen.db-shm")
KINDS = ("OBS",) + tuple("N%d" % m for m in range(M_NULL)) + ("P%d" % DELTA,)

# predictions (plan section 8)
P1_P, P1_BAND = 0.95, (0.0, 0.02)
P2_MAX = 1
P3_P = {"BOTH": 0.20, "ONE": 0.45, "NEITHER": 0.35}
P4_BAND, P5_BAND = (3, 0, 10), (12, 3, 30)
P6_P, P6_SITE = 0.90, "n00000001"
P7_BAND = {"bareq512_s42": (0.75, 0.50, 0.95), "af_clean_s42": (0.80, 0.55, 0.97)}
P8_P = {"bareq512_s42": {"MORE": 0.40, "SAME": 0.20, "FEWER": 0.40},
        "af_clean_s42": {"MORE": 0.60, "SAME": 0.10, "FEWER": 0.30}}
P9_BAND = (6, 8)

WORD_M1 = "MODAL (split-dip) at per-family FDR q = 0.05 (hierarchical BH over nested sites, {tree}, {recipe}; EXPLORATORY)"
WORD_M2 = "split-dip BH at q = 0.05 over the tree's m sites (nesting not respected; EXPLORATORY)"
WORD_M3 = "split-dip p <= 0.05 (per-site, uncorrected; EXPLORATORY)"
WORD_UNTESTED = "UNTESTED (a site ancestor not rejected)"
S4_LINE = ("S4: bareq512_s42 (R512) and af_clean_s42 (R256) are read in separate blocks; no count, share or word is summed, "
           "differenced, ranked or compared across the two recipes.")
NOT_SHOW = ("WHAT THIS READOUT WILL NOT SHOW: a certificate (the J site null stays THE certificate; nothing here is registered); "
            "a tree-wide FDR; k > 2 modes or which 2-way split the tree declared (the axis is the data's 2-means axis on half A); "
            "that an unselected site lacks modes; anything across R512 and R256; other trees, embedders or held-out data; "
            "anything about a judge, board or profile.")


def _cr_tree(name):
    for t in CR.TREES:
        if t["name"] == name:
            return t
    refuse("cert_resolution.TREES has no %s" % name)


def _spec(name, recipe, dim, t, snapshot, m, split, j_hier, named):
    cr = _cr_tree(name)
    if cr["recipe"] != recipe or cr["m"] != m:
        refuse("cert_resolution.TREES %s is %s / %d, the plan %s / %d" % (name, cr["recipe"], cr["m"], recipe, m))
    return dict(name=name, recipe=recipe, dim=dim, t=t, snapshot=snapshot, m=m, split=split, j_hier=sorted(j_hier),
                named=list(named), csv=dict(rel=cr["csv"]["rel"], lf=cr["csv"]["lf"]),
                jsonl=dict(rel=cr["jsonl"]["rel"], lf=cr["jsonl"]["lf"]))


TREES = [
    _spec("bareq512_s42", "R512", 512, 0, "20260909_212117_Headless_Run_Auto_ge", 70, "id-disjoint only",
          {"n00000006", "n00000015"}, NAMED),
    _spec("af_clean_s42", "R256", 256, 1, "20260917_201353_Headless_Run_Auto_ge", 69, "content-closed",
          {"n00000001", "n00000005", "n00000017", "n00000018", "n00000042", "n00000045", "n00000043", "n00000074"}, ()),
]

# ================================================================================================ connect guard
_RAW_CONNECT = getattr(sqlite3.connect, "_raw", sqlite3.connect)


def _guarded_connect(database, *a, **k):
    """Process-wide: only file: URIs opened with mode=ro AND immutable=1 on the two DBs this readout reads."""
    s = str(database)
    if not (k.get("uri") and s.startswith("file:")):
        refuse("sqlite3.connect(%r) is not a file: URI opened with uri=True" % s)
    path, _, query = s[5:].partition("?")
    params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
    if params.get("mode") != "ro" or params.get("immutable") != "1":
        refuse("sqlite3.connect(%r): only mode=ro&immutable=1 is admitted" % s)
    if os.path.basename(path) not in DB_NAMES:
        refuse("sqlite3.connect(%r): %s is not a DB this readout reads" % (s, os.path.basename(path)))
    return _RAW_CONNECT(database, *a, **k)


_guarded_connect._raw = _RAW_CONNECT
sqlite3.connect = _guarded_connect

# ================================================================================================ rule 7 probe (W1, W2, W4)
_IS_WIN = os.name == "nt"


def exclusive_open(path):
    """W1: CreateFileW(GENERIC_READ, share 0). FREE (opened exclusively and closed), BUSY (sharing violation: another
    process holds it), ABSENT, or ERROR <code>. A read-only open; nothing is written."""
    if not os.path.exists(path):
        return "ABSENT"
    if not _IS_WIN:
        return "ERROR not-windows"
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                                wintypes.DWORD, wintypes.HANDLE]
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    h = k32.CreateFileW(os.path.abspath(path), 0x80000000, 0, None, 3, 0x80, None)
    if h is None or h == wintypes.HANDLE(-1).value or h == ctypes.c_void_p(-1).value:
        err = ctypes.get_last_error()
        return "BUSY" if err in (32, 33) else ("ABSENT" if err in (2, 3) else "ERROR %d" % err)
    k32.CloseHandle(h)
    return "FREE"


def free_ram_gb():
    if not _IS_WIN:
        return float("nan")
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = MS()
    ms.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return ms.ullAvailPhys / float(1024 ** 3)


def ram_ok(gb):
    return bool(gb == gb and gb >= RAM_GB)


def list_processes():
    cmd = ["powershell", "-NoProfile", "-Command",
           "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'java|python|gradle|ollama' } | "
           "Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        refuse("W2: the process list could not be read (%s)" % r.stderr.strip()[:200])
    txt = r.stdout.strip()
    if not txt:
        return []
    data = json.loads(txt)
    return data if isinstance(data, list) else [data]


def classify(procs, me):
    """W2: -> list of (pid, name, verdict, cmd). Verdicts: SELF, ADMIT (--selftest), REFUSE (...), OTHER (listed)."""
    rows = []
    for p in procs:
        pid, ppid = int(p.get("ProcessId") or 0), int(p.get("ParentProcessId") or 0)
        name = str(p.get("Name") or "")
        cmd = str(p.get("CommandLine") or "")
        c = cmd.replace("\\", "/")
        lname = name.lower()
        if pid in me or ppid in me:
            v = "SELF"
        elif lname.startswith("java") or "gradle" in c.lower() or "gradle" in lname:
            v = "REFUSE (a JVM: construction, site null or Gradle worker)"
        elif "python" in lname:
            if "pool_guard" in c:
                v = "REFUSE (pool_guard)"
            elif "tools/analysis/" in c or "tools/chains/" in c:
                v = "ADMIT (--selftest)" if " --selftest" in (" " + c + " ").replace("--selftest-io", "") else \
                    "REFUSE (a tools/analysis or tools/chains reader)"
            else:
                v = "OTHER (not a TaxoArena tools process; listed)"
        else:
            v = "OTHER (not a pool reader; listed)"
        rows.append((pid, name, v, cmd))
    return rows


def probe(data_root, say, me=None, procs=None, phase="pre"):
    """W1 + W2 + W4, printed; -> True iff every check passes."""
    me = set(me or ()) | {os.getpid()}
    ok = True
    say("[RULE7 %s] W1 exclusive-open probe under %s:" % (phase, data_root))
    for f in PROBE_FILES:
        st = exclusive_open(os.path.join(data_root, f))
        bad = st not in ("FREE", "ABSENT")
        ok = ok and not bad
        say("[RULE7 %s]   %-26s %s" % (phase, f, st + (" -> REFUSE" if bad else "")))
    if phase == "pre":
        rows = classify(list_processes() if procs is None else procs, me)
        say("[RULE7 %s] W2 processes (java / python / gradle / ollama), %d listed:" % (phase, len(rows)))
        for pid, name, v, cmd in rows:
            say("[RULE7 %s]   pid %-7d %-14s %s | %s" % (phase, pid, name[:14], v, cmd[:140]))
            if v.startswith("REFUSE"):
                ok = False
        gb = free_ram_gb()
        r_ok = ram_ok(gb)
        ok = ok and r_ok
        say("[RULE7 %s] W4 free physical memory %.2f GB; bar >= %.0f GB -> %s" % (phase, gb, RAM_GB, "OK" if r_ok else "REFUSE"))
    say("[RULE7 %s] -> %s" % (phase, "FREE" if ok else "BUSY (a failed precondition)"))
    return ok


# ================================================================================================ inputs
class _W(object):
    def __init__(self, say):
        self.say = say

    def write(self, s):
        for line in s.rstrip("\n").split("\n"):
            self.say(line)


def _cr(fn, *a):
    try:
        return fn(*a)
    except CR.Refusal as e:
        refuse("cert_resolution: %s" % e)


def region_query_ids(root_id, byid):
    """SeparationNullBySizeTest.regionQueryIds (as MIX-LRT-SITE transcribed it): LIFO stack over childIds present in the graph,
    seen-set, union of every visited node's queryIds."""
    ids, stack, seen = {}, [root_id], set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        node = byid[cur]
        for q in node.get("queryIds") or []:
            ids.setdefault(q, None)
        for c in node.get("childIds") or []:
            if c in byid:
                stack.append(c)
    return list(ids)


def load_graph(data_root, snapshot):
    p = os.path.join(data_root, "snapshots.db")
    con = pool_guard.open_ro(p)
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (snapshot,)).fetchone()
    finally:
        con.close()
    if row is None:
        refuse("snapshot %s is not in %s" % (snapshot, p))
    g = json.loads(row[0])
    return dict(byid={n["id"]: n for n in g["nodes"]}, sha=hashlib.sha256(row[0].encode("utf-8")).hexdigest())


def sha16_rows(Y):
    return hashlib.sha256(np.ascontiguousarray(Y, dtype=np.float64).tobytes()).hexdigest()[:16]


def load_tree(spec, data_roots, data_root, say, with_db=True):
    name = spec["name"]
    w = _W(say)
    csv_path, csv_raw, csv_p = _cr(CR.locate, spec["csv"], data_roots, None, w)
    jl_path, jl_raw, jl_p = _cr(CR.locate, spec["jsonl"], data_roots, None, w)
    n_rows = len(list(csv.DictReader(io.StringIO(csv_raw.decode("utf-8-sig").replace("\r\n", "\n")))))
    if n_rows == 0:
        refuse("%s: zero sites in %s" % (name, spec["csv"]["rel"]))
    sites, snap = _cr(CR.read_sites, csv_raw, name)
    if snap != spec["snapshot"]:
        refuse("%s: the CSV carries snapshot %s, the plan %s" % (name, snap, spec["snapshot"]))
    if len(sites) != spec["m"]:
        refuse("%s: %d sites, the plan %d" % (name, len(sites), spec["m"]))
    rec = _cr(CR.read_last_record, jl_raw)
    fails = _cr(CR.identity_check, sites, rec)
    if fails:
        refuse("%s: identity check failed: %s" % (name, "; ".join(fails[:5])))
    fam, anc, multi = _cr(CR.site_structure, sites, rec)
    pj = {s["node_id"]: CR.p_site(s["k"]) for s in sites}
    jh = _cr(CR.hierarchical_bh, sites, fam, anc, pj, Q)["rejected"]
    if sorted(jh) != sorted(spec["j_hier"]):
        refuse("%s: the J hierarchical set recomputed from the CSV is %s, the record %s" % (name, sorted(jh), spec["j_hier"]))
    say("%s %s: CSV %s (%s; sha256-lf16:%s), jsonl %s (sha256-lf16:%s); %d sites; identity check PASS; multi-parent sites %d; "
        "TOP family %d; J hierarchical set reproduced: %d %s" % (TAG, name, spec["csv"]["rel"], csv_path, spec["csv"]["lf"][:16],
                                                              spec["jsonl"]["rel"], spec["jsonl"]["lf"][:16], len(sites), multi,
                                                              sum(1 for s in sites if fam[s["node_id"]] == "TOP"), len(jh),
                                                              sorted(jh)))
    ctx = dict(spec=spec, sites=sites, rec=rec, fam=fam, anc=anc, multi=multi, j_hier=set(jh),
               cert={s["node_id"]: s["cert"] for s in sites}, csv_lf=spec["csv"]["lf"], jsonl_lf=spec["jsonl"]["lf"])
    if not with_db:
        return ctx
    g = load_graph(data_root, spec["snapshot"])
    byid = g["byid"]
    recn = {n["id"]: n for n in rec["nodes"]}
    for s in sites:
        v = s["node_id"]
        if v not in byid:
            refuse("%s: site %s is not in snapshot %s" % (name, v, spec["snapshot"]))
        for f in ("childIds", "parentIds"):
            if sorted(byid[v].get(f) or []) != sorted(recn[v].get(f) or []):
                refuse("%s: site %s %s differ between the snapshot graph and the jsonl last record" % (name, v, f))
    members = {}
    for s in sites:
        ids = sorted(region_query_ids(s["node_id"], byid))
        if len(ids) != s["n"]:
            refuse("%s: membership-count mismatch at %s: %d members in the graph, CSV n = %d" % (name, s["node_id"], len(ids),
                                                                                              s["n"]))
        members[s["node_id"]] = ids
    union = sorted(set(q for ids in members.values() for q in ids))
    dbp = os.path.join(data_root, "embeddings_cache.db")
    con = pool_guard.open_ro(dbp)
    try:
        vec, dims = EG.read_vectors(con, union, spec["dim"])
        if set(dims) != {RAW_DIM}:
            refuse("%s: raw vector lengths %s, expected {%d}" % (name, dims, RAW_DIM))
        missing = [q for q in union if q not in vec]
        if missing:
            refuse("%s: %d of %d members have no vector (first %s)" % (name, len(missing), len(union), missing[:3]))
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            res = EG.guard(con, dbp, [byid[s["node_id"]] for s in sites], lambda node: members[node["id"]], spec["dim"], MODEL,
                           "explicit (%s: the trees of record are qwen3, KNOWLEDGE section 1)" % TEST)
    finally:
        con.close()
    for line in buf.getvalue().rstrip("\n").split("\n"):
        say(line)
    X = {v: np.stack([vec[q] for q in ids]) for v, ids in members.items()}
    ctx.update(graph_sha=g["sha"], members=members, X=X, xsha={v: sha16_rows(x) for v, x in X.items()},
               min_cos=res["min_cos"], n_union=len(union))
    ns = [s["n"] for s in sites]
    say("%s %s: snapshot %s graph sha256 %s; members == CSV n at all %d sites (n %d..%d); %d member vectors at slice %d of %d; "
        "graph == jsonl structure at every site; vmfMu min cos %.6f over the %d tested sites" % (
            TAG, name, spec["snapshot"], g["sha"][:16], len(sites), min(ns), max(ns), len(union), spec["dim"], RAW_DIM,
            res["min_cos"], len(sites)))
    return ctx


def pool_line():
    ids = pool_guard.judgeable(pool_guard.pool_file_ids(POOL_ID))
    got = pool_guard.compute_pool_id(ids)
    if got != POOL_ID:
        refuse("the pool id file hashes to %s, not %s" % (got, POOL_ID))
    return ("pool %s (printed, not used: tree members are construction rows; id file %s hashes to it via "
            "pool_guard.compute_pool_id, %d judgeable ids; the dataset DB is not opened)"
            % (POOL_ID, pool_guard.registry_entry(POOL_ID)["id_file"], sum(len(v) for v in ids.values())))


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 22)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def db_state(data_root):
    out = {}
    for n in DB_NAMES:
        p = os.path.join(data_root, n)
        if not os.path.isfile(p):
            refuse("%s not found under %s" % (n, data_root))
        st = os.stat(p)
        out[n] = (file_sha(p), st.st_size, int(st.st_mtime))
    return out


# ================================================================================================ tasks
def task_key(tree, node, kind):
    return "%s|%s|%s" % (tree, node, kind)


def gen_null(X, rng, Z=None):
    """The J site null's generator (withinNodeCloud: mean + sum_c g_c c / sqrt(n), unit rows) in its exact-in-distribution eigen
    form: mean + Z diag(s) V^T / sqrt(n), C = U diag(s) V^T the thin SVD of the centred rows, Z iid N(0, 1) (n x rank)."""
    X = np.asarray(X, dtype=np.float64)
    n = len(X)
    mu = X.mean(axis=0)
    _U, s, Vt = np.linalg.svd(X - mu, full_matrices=False)
    if Z is None:
        Z = rng.standard_normal((n, len(s)))
    return CSD.unit(mu + (Z * s[None, :]) @ Vt / math.sqrt(n))


def plant(X, ids, t, i, dim):
    u = CP.direction(U_SEED_P + 1000 * t + i - CP.U_SEED0, dim=dim)
    hl = CP.halves(ids, H_SEED_P + 1000 * t + i - CP.H_SEED0)
    hi = np.array([hl[q] == "hi" for q in ids])
    Y, _s = CP.plant_rows(X, hi, u, DELTA)
    return Y


def make_rows(kind, X, job):
    if kind == "OBS":
        return np.asarray(X, dtype=np.float64)
    if kind.startswith("N"):
        m = int(kind[1:])
        return gen_null(X, np.random.default_rng([NULL_SEED, job["t"], job["i"], m]))
    if kind == "P%d" % DELTA:
        return plant(X, job["ids"], job["t"], job["i"], job["dim"])
    refuse("unknown task kind %s" % kind)


DIP_CALLS = [0]
_DIP_READY = {}


def _ensure_dip(pylib):
    if "ok" not in _DIP_READY:
        CSD.load_diptest(pylib)
        got = CSD.diptest_pins()
        if got != DIPTEST_PIN:
            refuse("diptest %s is not the pinned %s" % (got, DIPTEST_PIN))
        _DIP_READY["ok"] = got
    return _DIP_READY["ok"]


def dip(name, Y):
    DIP_CALLS[0] += 1
    return CSD.dip_site(name, Y)


def compute_job(job):
    try:
        _ensure_dip(job["pylib"])
        rows = []
        for kind in job["kinds"]:
            Y = make_rows(kind, job["X"], job)
            key = task_key(job["tree"], job["node"], kind)
            r = dip("CDS|" + key, Y)
            rows.append(dict(key=key, p=float(r["p"]), ps=[float(x) for x in r["ps"]], ysha=sha16_rows(Y), n=int(len(Y))))
        return dict(ok=True, node=job["node"], tree=job["tree"], rows=rows)
    except SystemExit as e:
        return dict(ok=False, node=job["node"], tree=job["tree"], err="SystemExit %s" % e)
    except Exception as e:  # noqa: BLE001  (an error is reported and never cached)
        return dict(ok=False, node=job["node"], tree=job["tree"], err=repr(e))


def _winit(pylib):
    _ensure_dip(pylib)


# ================================================================================================ cache
def expected_keys(ctxs, pilot=0):
    keys = []
    for c in ctxs:
        sites = c["sites"][:pilot] if pilot else c["sites"]
        for s in sites:
            for k in KINDS:
                keys.append(task_key(c["spec"]["name"], s["node_id"], k))
    return sorted(keys)


def constants():
    return dict(R=CSD.R_HALV, km_restarts=CSD.KM_RESTARTS, km_iters=CSD.KM_ITERS, alpha=ALPHA, q=str(Q), m_null=M_NULL,
                delta=DELTA, seeds=[NULL_SEED, U_SEED_P, H_SEED_P], g0=[str(G0_RATE), G0_CP], fdip=FDIP_REPL,
                power=str(POWER_SHARE), kinds=list(KINDS))


def make_meta(ctxs, pilot, plan_pins, with_db=True):
    trees = []
    for c in ctxs:
        sp = c["spec"]
        t = dict(name=sp["name"], recipe=sp["recipe"], dim=sp["dim"], t=sp["t"], snapshot=sp["snapshot"], m=sp["m"],
                 csv_lf=c["csv_lf"], jsonl_lf=c["jsonl_lf"], j_hier=sorted(c["j_hier"]))
        if with_db:
            t.update(graph_sha=c["graph_sha"], sites=[[s["node_id"], s["n"], c["xsha"][s["node_id"]]] for s in c["sites"]])
        trees.append(t)
    keys = expected_keys(ctxs, pilot)
    meta = dict(test=TEST, plan=plan_pins, script=pins_of(SELF), modules=module_pins(), diptest=_DIP_READY.get("ok"),
                numpy=np.__version__, constants=constants(), pilot=pilot, trees=trees, tasks=keys)
    meta["set_hash"] = hashlib.sha256(json.dumps([trees, keys], sort_keys=True).encode("utf-8")).hexdigest()
    return meta


def read_cache(path):
    if not os.path.exists(path):
        return None, {}
    meta, done = None, {}
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if ln == 0:
                if "meta" not in obj:
                    refuse("%s: the first line is not the meta" % path)
                meta = obj["meta"]
                continue
            if obj["key"] in done:
                refuse("%s: duplicate task %s" % (path, obj["key"]))
            done[obj["key"]] = obj
    return meta, done


def append_rows(path, rows):
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
        f.flush()


# ================================================================================================ words
def g0_word(k, N):
    if N <= 0:
        refuse("G0: zero NULL draws")
    lo, hi = CR.clopper_pearson(k, N)
    ok = bool(Fraction(k, N) <= G0_RATE and hi <= G0_CP)
    return ("SIZE-OK" if ok else "ANTI-CONSERVATIVE"), lo, hi


def w1_word(g0ok, h, plant_cert, m):
    if not g0ok:
        return "NOT EVALUABLE"
    if h >= 1:
        return "SOME"
    return "NONE-POWERED" if Fraction(plant_cert, m) >= POWER_SHARE else "NONE-UNDERPOWERED"


def w2_word(g0ok, D, named):
    if not named:
        return None
    if not g0ok:
        return "NOT EVALUABLE"
    inn = [s for s in named if s in D]
    if len(inn) == len(named):
        return "BOTH"
    if len(inn) == 1:
        return "ONE (%s)" % inn[0]
    return "NEITHER"


def w3_word(g0ok, h, j):
    if not g0ok:
        return "NOT EVALUABLE"
    return "MORE" if h > j else ("SAME" if h == j else "FEWER")


def fdip_word(g0ok, repl_pos):
    clauses = []
    if not g0ok:
        clauses.append("G0 ANTI-CONSERVATIVE")
    if repl_pos >= FDIP_REPL:
        clauses.append("%d of %d NULL-TREE replicates reject (bar %d)" % (repl_pos, M_NULL, FDIP_REPL))
    return bool(clauses), clauses


WORD_NE = "NOT EVALUABLE (G0 ANTI-CONSERVATIVE)"


def site_word(tree, recipe, in_d, in_flat, p, reached, g0ok=True):
    if not g0ok:
        return WORD_NE
    if in_d:
        w = WORD_M1.format(tree=tree, recipe=recipe)
    elif in_flat:
        w = WORD_M2
    elif p <= ALPHA:
        w = WORD_M3
    else:
        w = ""
    if not reached:
        w = (w + "; " if w else "") + WORD_UNTESTED
    return w


def word_class(w):
    return None if w is None else w.split(" ")[0]


def brier(probs, obs):
    return sum((p - (1.0 if c == obs else 0.0)) ** 2 for c, p in probs.items())


def in_band(x, lo, hi):
    return bool(lo <= x <= hi)


READING = {
    "BOTH": "modal support for both J-certified sites of bareq512_s42 (a candidate stronger certificate sentence; the registrar's)",
    "NONE-POWERED": ("no site of {tree} is modal along its split axis at per-family q = 0.05 although the rule finds a planted "
                     "delta-6 shift at most of its sites: consistent with 'the certificate is geometric, not modal' (still a "
                     "qualifier, never a closure)"),
    "MORE": ("the split-dip finds more modal sites than the J hierarchical set of {tree} holds (the J set is resolution-limited at "
             "300 reps; a different question, not a correction of the J null)"),
}


# ================================================================================================ readout
def tree_readout(ctx, done, say):
    sp = ctx["spec"]
    name, recipe = sp["name"], sp["recipe"]
    sites, fam, anc = ctx["sites"], ctx["fam"], ctx["anc"]
    nodes = [s["node_id"] for s in sites]
    m = len(nodes)
    byn = {s["node_id"]: s for s in sites}
    p_obs = {v: done[task_key(name, v, "OBS")]["p"] for v in nodes}
    p_null = {v: [done[task_key(name, v, "N%d" % j)]["p"] for j in range(M_NULL)] for v in nodes}
    p_pl = {v: done[task_key(name, v, "P%d" % DELTA)]["p"] for v in nodes}
    say("")
    say("== TREE %s (%s; %s; snapshot %s; m = %d sites; slice %d)" % (name, recipe, sp["split"], sp["snapshot"], m, sp["dim"]))
    say("[J] hierarchical set of record reproduced from the CSV (p = (k + 1) / 301; CERT-RESOLUTION): %d sites %s" % (
        len(ctx["j_hier"]), sorted(ctx["j_hier"])))
    # G0
    k0 = sum(1 for v in nodes for x in p_null[v] if x <= ALPHA)
    N0 = m * M_NULL
    g0, lo, hi = g0_word(k0, N0)
    g0ok = g0 == "SIZE-OK"
    say("[G0] NULL draws certified %d of %d (rate %.4f; 95%% CP [%.4f, %.4f]); bar rate <= %.2f and CP upper <= %.2f -> %s" % (
        k0, N0, k0 / float(N0), lo, hi, float(G0_RATE), G0_CP, g0))
    icc, deff = CSD.icc_deff([[1 if x <= ALPHA else 0 for x in p_null[v]] for v in nodes])
    deff_u = deff if (deff is not None and deff >= 1.0) else 1.0
    neff = N0 / deff_u
    se = math.sqrt(0.05 * 0.95 / neff)
    say("[G0-SUPPORT] denominator %d = %d sites x %d draws; realised ICC %s -> DEFF %s (declared 1 by construction; the "
        "readout uses max(1, DEFF) = %.3f); n_eff %.1f; SE at 0.05 %.5f; MDE80 %.4f above 0.05" % (
            N0, m, M_NULL, "NA" if icc is None else "%.4f" % icc, "NA" if deff is None else "%.4f" % deff, deff_u, neff, se,
            2.8 * se))
    # NULL-TREE
    repl = [len(_cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_null[v][j]) for v in nodes}, Q)["rejected"])
            for j in range(M_NULL)]
    repl_pos = sum(1 for r in repl if r >= 1)
    say("[NULL-TREE] hierarchical rejections per replicate (m = 0..%d): %s; replicates with >= 1 rejection: %d of %d" % (
        M_NULL - 1, repl, repl_pos, M_NULL))
    # OBS
    per = sum(1 for v in nodes if p_obs[v] <= ALPHA)
    fi, fthr = CR.bh_cutoff([Fraction(p_obs[v]) for v in nodes], Q)
    flat = {nodes[i] for i in fi}
    qby = CR.by_q(m, Q)
    bi, _bthr = CR.bh_cutoff([Fraction(p_obs[v]) for v in nodes], qby)
    by = {nodes[i] for i in bi}
    H = _cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_obs[v]) for v in nodes}, Q)
    D, reached = set(H["rejected"]), set(H["reached"])
    top = [f for f in H["families"] if f["key"] == "TOP"]
    m_top = top[0]["m_f"] if top else 0
    fam_run = sum(1 for f in H["families"] if f["run"])
    say("[OBS] per-site p <= 0.05: %d of %d; flat BH q = 0.05: %d of %d (cutoff %s); BY: %d of %d; hierarchical BH (per-family "
        "q = 0.05): TOP family %d sites, families run %d, sites reached %d, MODAL set D = %d of %d" % (
            per, m, len(flat), m, "none" if fthr is None else "%.6f" % float(fthr), len(by), m, m_top, fam_run, len(reached),
            len(D), m))
    for v in sorted(D, key=lambda x: (byn[x]["depth"], x)):
        s = byn[v]
        say("[D] %s '%s' depth %d n %d p %.6g family %s; J hierarchical %s; cert_site_p95 %s" % (
            v, s["label"][:40], s["depth"], s["n"], p_obs[v], fam[v], "yes" if v in ctx["j_hier"] else "no",
            "true" if ctx["cert"][v] else "false"))
    # PLANT
    a = sum(1 for v in nodes if p_pl[v] <= ALPHA)
    a_out = sum(1 for v in nodes if v not in D and p_pl[v] <= ALPHA)
    say("[PLANT] delta %d: certified %d of %d (share %.4f); at the sites outside D: %d of %d" % (
        DELTA, a, m, a / float(m), a_out, m - len(D)))
    # words
    w1 = w1_word(g0ok, len(D), a, m)
    w2 = w2_word(g0ok, D, sp["named"])
    w3 = w3_word(g0ok, len(D), len(ctx["j_hier"]))
    ov = sorted(D & ctx["j_hier"])
    donly = sorted(D - ctx["j_hier"])
    say("W1 (Q1) %s: %s (|D| %d of %d; PLANT %d of %d)" % (name, w1, len(D), m, a, m))
    if w2 is not None:
        say("W2 (Q2) %s: %s (named %s; in D: %s)" % (name, w2, sp["named"], [s for s in sp["named"] if s in D]))
    else:
        say("W2 (Q2) %s: not defined (no named sites on this tree)" % name)
    say("W3 (Q3) %s: %s (|D| %d vs |J| %d); overlap %d of %d %s; D-only sites %d %s" % (
        name, w3, len(D), len(ctx["j_hier"]), len(ov), len(ctx["j_hier"]), ov, len(donly), donly))
    for w in (w1, word_class(w2), word_class(w3)):
        if w in READING:
            say("READING (%s, EXPLORATORY): %s" % (w, READING[w].format(tree=name)))
    fired, clauses = fdip_word(g0ok, repl_pos)
    say("F-DIP %s: %s (%s)" % (name, "FIRED" if fired else "NOT FIRED", "; ".join(clauses) if clauses else
                                 "G0 SIZE-OK; %d of %d replicates reject; bar %d" % (repl_pos, M_NULL, FDIP_REPL)))
    if fired:
        say("F-DIP %s consequence: no M1-M3 word of %s may be quoted; D holds the rule's false positives at the real geometry"
            % (name, name))
    words = {}
    for v in nodes:
        words[v] = site_word(name, recipe, v in D, v in flat, p_obs[v], v in reached, g0ok)
    untested = sum(1 for v in nodes if v not in reached)
    say("[SITE WORDS] %s: M1 %d, M2 %d, M3 %d, UNTESTED %d of %d" % (
        name, len(D), len(flat - D), sum(1 for v in nodes if v not in D and v not in flat and p_obs[v] <= ALPHA), untested, m))
    for v in nodes:
        if words[v] and not (words[v] == WORD_UNTESTED):
            say("  %s %s: %s" % (name, v, words[v]))
    rows = []
    for v in nodes:
        s = byn[v]
        rows.append([name, recipe, v, s["label"], s["depth"], s["n"], fam[v], str(v in reached).lower(), repr(p_obs[v]),
                     str(v in flat).lower(), str(v in by).lower(), str(v in D).lower(), str(v in ctx["j_hier"]).lower(),
                     str(ctx["cert"][v]).lower(), sum(1 for x in p_null[v] if x <= ALPHA), repr(min(p_null[v])), repr(p_pl[v]),
                     str(p_pl[v] <= ALPHA).lower(), words[v]])
    return dict(name=name, g0=g0, g0ok=g0ok, k0=k0, N0=N0, repl=repl, repl_pos=repl_pos, D=D, flat=flat, w1=w1, w2=w2, w3=w3,
                fdip=fired, plant=a, m=m, overlap=len(ov), rows=rows)


def predictions(res, say):
    say("")
    say("PREDICTIONS (plan section 8; words by Brier, counts HELD iff the point lies in the band)")
    for name in sorted(res):
        r = res[name]
        y = 1.0 if r["g0"] == "SIZE-OK" else 0.0
        rate = r["k0"] / float(r["N0"])
        say("P1 %s: G0 %s (Brier %.4f at p(SIZE-OK) %.2f); NULL rate %.4f in [%.2f, %.2f] -> %s" % (
            name, r["g0"], (P1_P - y) ** 2, P1_P, rate, P1_BAND[0], P1_BAND[1],
            "HELD" if in_band(rate, *P1_BAND) else "FAILED"))
        say("P2 %s: replicates with >= 1 rejection %d (HELD iff <= %d) -> %s" % (
            name, r["repl_pos"], P2_MAX, "HELD" if r["repl_pos"] <= P2_MAX else "FAILED"))
    ns = "NOT SCORED (G0 ANTI-CONSERVATIVE)"
    b = res.get("bareq512_s42")
    if b is not None:
        if b["g0ok"]:
            c = word_class(b["w2"])
            say("P3 bareq512_s42: W2 %s (Brier %.4f over %s)" % (b["w2"], brier(P3_P, c), P3_P))
            say("P4 bareq512_s42: |D| %d in [%d, %d] (point %d) -> %s" % (
                len(b["D"]), P4_BAND[1], P4_BAND[2], P4_BAND[0], "HELD" if in_band(len(b["D"]), P4_BAND[1], P4_BAND[2])
                else "FAILED"))
        else:
            say("P3 bareq512_s42: " + ns)
            say("P4 bareq512_s42: " + ns)
    a = res.get("af_clean_s42")
    if a is not None:
        if a["g0ok"]:
            say("P5 af_clean_s42: |D| %d in [%d, %d] (point %d) -> %s" % (
                len(a["D"]), P5_BAND[1], P5_BAND[2], P5_BAND[0], "HELD" if in_band(len(a["D"]), P5_BAND[1], P5_BAND[2])
                else "FAILED"))
            y6 = 1.0 if P6_SITE in a["D"] else 0.0
            say("P6 af_clean_s42: root %s in D: %s (Brier %.4f at p %.2f)" % (P6_SITE, "yes" if y6 else "no", (P6_P - y6) ** 2,
                                                                             P6_P))
        else:
            say("P5 af_clean_s42: " + ns)
            say("P6 af_clean_s42: " + ns)
    for name in sorted(res):
        r = res[name]
        if name in P7_BAND:
            sh = r["plant"] / float(r["m"])
            pt, lo, hi = P7_BAND[name]
            say("P7 %s: PLANT share %.4f in [%.2f, %.2f] (point %.2f) -> %s" % (name, sh, lo, hi, pt,
                                                                                "HELD" if in_band(sh, lo, hi) else "FAILED"))
        if name in P8_P:
            if r["g0ok"]:
                say("P8 %s: W3 %s (Brier %.4f over %s)" % (name, r["w3"], brier(P8_P[name], word_class(r["w3"])), P8_P[name]))
            else:
                say("P8 %s: %s" % (name, ns))
    if a is not None:
        if a["g0ok"]:
            say("P9 af_clean_s42: J sites in D %d of %d in [%d, %d] -> %s" % (
                a["overlap"], len(TREE_J(a)), P9_BAND[0], P9_BAND[1], "HELD" if in_band(a["overlap"], *P9_BAND) else "FAILED"))
        else:
            say("P9 af_clean_s42: " + ns)


def TREE_J(r):
    return [row[2] for row in r["rows"] if row[12] == "true"]


def render(ctxs, done, meta, pilot, say):
    say("%s OUTCOME%s (EXPLORATORY; zero calls; plan %s blob:%s sha256-lf16:%s, committed %s before any statistic)" % (
        TEST, " PILOT %d" % pilot if pilot else "", PLAN_REL, meta["plan"]["blob"][:8], meta["plan"]["lf16"], PLAN_COMMIT))
    say(pool_line())
    say("[SCRIPT] cert_dip_sites.py blob:%s sha256-lf16:%s; the rule cert_split_dip.py blob:%s (dip_site unchanged); "
        "cert_resolution.py blob:%s (bh_cutoff, by_q, site_structure, hierarchical_bh, identity_check unchanged); "
        "embedder_guard.py blob:%s; cert_planted.py blob:%s; diptest %s (%s files, sha256 %s...); numpy %s" % (
            meta["script"]["blob"][:8], meta["script"]["lf16"], meta["modules"]["cert_split_dip.py"][:8],
            meta["modules"]["cert_resolution.py"][:8], meta["modules"]["embedder_guard.py"][:8],
            meta["modules"]["cert_planted.py"][:8], meta["diptest"]["version"], meta["diptest"]["files"],
            meta["diptest"]["sha256"][:16], meta["numpy"]))
    say("[CACHE] tasks %d; done %d; set hash %s..." % (len(meta["tasks"]), len(done), meta["set_hash"][:16]))
    say("[RULE] R = %d halvings; spherical k-means k = 2 (%d restarts, <= %d iterations) on half A; Hartigan's dip of half B on "
        "c1 - c2; p_site = min(1, 2 x median); per-site bar %.2f; BH q = %s flat and per family; NULL %d draws per site; PLANT "
        "delta %d" % (CSD.R_HALV, CSD.KM_RESTARTS, CSD.KM_ITERS, ALPHA, Q, M_NULL, DELTA))
    say(S4_LINE)
    res = {}
    rows = []
    for c in ctxs:
        r = tree_readout(c, done, say)
        res[r["name"]] = r
        rows.extend(r["rows"])
    predictions(res, say)
    say("")
    say(NOT_SHOW)
    return res, rows


SITES_HEADER = ["tree", "recipe", "node_id", "label", "depth", "n", "family_key", "reached", "p_obs", "flat_bh", "by_bh",
                "modal_hier", "j_hier", "cert_site_p95", "null_cert", "null_p_min", "plant_p", "plant_cert", "words"]


def sites_csv_text(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(SITES_HEADER)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def write_text(path, text, once):
    if once:
        try:
            with open(path, "x", encoding="utf-8", newline="\n") as f:
                f.write(text)
        except FileExistsError:
            refuse("%s exists: outcome files of record are write-once" % path)
    else:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)


# ================================================================================================ modes
def resolve(a):
    if a.data_root:
        data_root = os.path.abspath(a.data_root)
    elif os.environ.get("TAXOARENA_DATA_ROOT"):
        data_root = os.path.abspath(os.environ["TAXOARENA_DATA_ROOT"])
    else:
        data_root = CR.main_checkout_of(REPO) or REPO
    fixture = os.path.isfile(os.path.join(data_root, FIXTURE_MARK))
    if (a.no_probe or a.allow_dirty or a.fixture_specs) and not fixture:
        refuse("--no-probe / --allow-dirty / --fixture-specs are admitted only with a fixture data root (%s absent)"
               % FIXTURE_MARK)
    if a.fixture_specs:
        with open(a.fixture_specs, encoding="utf-8") as f:
            specs = json.load(f)
        roots = [data_root]
    else:
        specs = TREES
        main = CR.main_checkout_of(REPO)
        roots = [REPO] + ([main] if main and os.path.normcase(main) != os.path.normcase(REPO) else [])
        if data_root not in roots:
            roots.append(data_root)
    if a.workers < 1 or a.workers > MAX_WORKERS:
        refuse("--workers %d: at most %d worker processes (the brief's cap)" % (a.workers, MAX_WORKERS))
    out_dir = os.path.abspath(a.out) if a.out else os.path.join(REPO, "experiment_results", "cert_dip_sites")
    return specs, data_root, roots, fixture, out_dir


def plan_pins(fixture):
    p = os.path.join(REPO, PLAN_REL)
    if not os.path.isfile(p):
        if fixture:
            return dict(blob="0" * 40, lf16="0" * 16, crlf16="0" * 16)
        refuse("the plan %s is absent" % p)
    return pins_of(p)


def clean_tree_check(say):
    def git(*args):
        r = subprocess.run(["git", "-C", SELF_DIR] + list(args), capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    rc, top = git("rev-parse", "--show-toplevel")
    if rc != 0:
        refuse("--run of record needs the script in a git checkout")
    rel = os.path.relpath(SELF, top).replace("\\", "/")
    _rc, head = git("rev-parse", "HEAD")
    rc1, hb = git("rev-parse", "HEAD:" + rel)
    _rc2, st = git("status", "--porcelain", "--", rel, PLAN_REL)
    mine = pins_of(SELF)["blob"]
    ok = bool(rc1 == 0 and hb == mine and st == "")
    say("[CLEAN] HEAD %s; %s blob HEAD %s, working %s; porcelain '%s' -> %s" % (head[:12], rel, hb[:8] if rc1 == 0 else "absent",
                                                                              mine[:8], st, "CLEAN" if ok else "DIRTY"))
    if not ok:
        refuse("the run of record needs a clean tracked script and plan (commit first)")
    return head


def mode_probe(a):
    _specs, data_root, _roots, _fx, _out = resolve(a)
    return 0 if probe(data_root, print) else 1


def mode_dry_run(a):
    specs, data_root, roots, fixture, out_dir = resolve(a)
    say = print
    say(pool_line())
    if not a.no_probe and not probe(data_root, say):
        refuse("rule 7: the pool is not free (W1 / W2 / W4)")
    say("[MODE] --dry-run: reads the CSVs, the jsonl records, the snapshot graphs and the embedding cache for pins, members, "
        "guards and counts; computes NO dip p; writes nothing")
    say("[PINS] modules %s; plan %s" % (module_pins(), plan_pins(fixture)["blob"][:8]))
    _ensure_dip(a.pylib)
    say("[PINS] diptest %s" % _DIP_READY["ok"])
    ctxs = [load_tree(sp, roots, data_root, say, with_db=True) for sp in specs]
    keys = expected_keys(ctxs, a.pilot)
    est = 0.0
    for c in ctxs:
        for s in c["sites"][:a.pilot] if a.pilot else c["sites"]:
            est += len(KINDS) * 13.4 * (s["n"] / 8125.0) ** 1.6 * (c["spec"]["dim"] / 256.0) ** 0.5
    say("[TASKS] %d tasks (%s); rough CPU estimate %.1f min single-process, %.1f min at --workers %d" % (
        len(keys), ", ".join("%s %d sites x %d" % (c["spec"]["name"], len(c["sites"][:a.pilot] if a.pilot else c["sites"]),
                                                   len(KINDS)) for c in ctxs), est / 60.0, est / 60.0 / a.workers, a.workers))
    say("[DRY-RUN] dip calls %d (must be 0)" % DIP_CALLS[0])
    if DIP_CALLS[0] != 0:
        refuse("the dry-run computed a dip p")
    return 0


AFTER_HOOK = [None]                 # selftest only: called between the computation and the after-state of the DBs


def mode_run(a):
    specs, data_root, roots, fixture, out_dir = resolve(a)
    say = print
    say(pool_line())
    if not fixture:
        clean_tree_check(say)
        if not a.skip_selftest_gate:
            with contextlib.redirect_stdout(io.StringIO()):
                selftest(quiet=True, e2e=False)
            say("[GATE] in-process selftest (units, no fixture DB) PASS")
    if not a.no_probe and not probe(data_root, say):
        refuse("rule 7: the pool is not free (W1 / W2 / W4)")
    _ensure_dip(a.pylib)
    before = db_state(data_root)
    for n, v in sorted(before.items()):
        say("[DB-PIN before] %s sha256 %s size %d mtime %d" % (n, v[0][:16], v[1], v[2]))
    ctxs = [load_tree(sp, roots, data_root, say, with_db=True) for sp in specs]
    meta = make_meta(ctxs, a.pilot, plan_pins(fixture))
    os.makedirs(out_dir, exist_ok=True)
    cache = os.path.join(out_dir, "pilot_cache.jsonl" if a.pilot else "cache.jsonl")
    old, done = read_cache(cache)
    if old is not None:
        if old != meta:
            diff = sorted(k for k in set(old) | set(meta) if old.get(k) != meta.get(k))
            refuse("the cache meta at %s differs from this launch in %s (pinned at first launch)" % (cache, diff))
        say("[CACHE] resume: %d of %d tasks cached" % (len(done), len(meta["tasks"])))
    else:
        with open(cache, "x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"meta": meta}, sort_keys=True) + "\n")
        say("[CACHE] new cache %s, meta pinned (set hash %s...)" % (cache, meta["set_hash"][:16]))
    jobs = []
    for c in ctxs:
        sp = c["spec"]
        for i, s in enumerate(c["sites"][:a.pilot] if a.pilot else c["sites"]):
            v = s["node_id"]
            kinds = [k for k in KINDS if task_key(sp["name"], v, k) not in done]
            if kinds:
                jobs.append(dict(tree=sp["name"], t=sp["t"], i=i, node=v, ids=c["members"][v], X=c["X"][v], dim=sp["dim"],
                                 kinds=kinds, pylib=a.pylib))
    jobs.sort(key=lambda j: -len(j["ids"]))            # the largest first (wall time); results do not depend on order
    t0 = time.time()
    computed, failed = 0, []
    say("[RUN] %d site jobs, %d tasks to compute, --workers %d" % (len(jobs), sum(len(j["kinds"]) for j in jobs), a.workers))
    if jobs:
        if a.workers == 1:
            results = map(compute_job, jobs)
            pool = None
        else:
            import multiprocessing as mp
            pool = mp.get_context("spawn").Pool(processes=a.workers, initializer=_winit, initargs=(a.pylib,))
            results = pool.imap_unordered(compute_job, jobs)
        try:
            for r in results:
                if r["ok"]:
                    append_rows(cache, r["rows"])
                    computed += len(r["rows"])
                else:
                    failed.append(r)
                    say("[RUN] FAILED (not cached) %s %s: %s" % (r["tree"], r["node"], r["err"]))
        finally:
            if pool is not None:
                pool.close()
                pool.join()
    say("[RUN] computed %d tasks in %.1f s; failed jobs %d" % (computed, time.time() - t0, len(failed)))
    if AFTER_HOOK[0] is not None:
        AFTER_HOOK[0]()
    after = db_state(data_root)
    for n, v in sorted(after.items()):
        say("[DB-PIN after]  %s sha256 %s size %d mtime %d -> %s" % (n, v[0][:16], v[1], v[2],
                                                                     "EQUAL" if v == before[n] else "CHANGED"))
    if after != before:
        refuse("a DB of record changed during the run (before %s, after %s)" % (before, after))
    if not a.no_probe:
        probe(data_root, say, phase="post")
    _m, done2 = read_cache(cache)
    missing = [k for k in meta["tasks"] if k not in done2]
    say("[RUN] cache %d of %d tasks; missing %d" % (len(done2), len(meta["tasks"]), len(missing)))
    return 1 if failed else 0


def mode_analyze(a):
    specs, data_root, roots, fixture, out_dir = resolve(a)
    cache = os.path.join(out_dir, "pilot_cache.jsonl" if a.pilot else "cache.jsonl")
    meta, done = read_cache(cache)
    if meta is None:
        refuse("no cache at %s" % cache)
    buf = io.StringIO()

    def say(s):
        print(s)
        buf.write(s + "\n")
    print("pool: none (no DB opened by --analyze)")
    ctxs = [load_tree(sp, roots, data_root, print, with_db=False) for sp in specs]
    cur = make_meta(ctxs, a.pilot, plan_pins(fixture), with_db=False)
    for k in ("test", "script", "modules", "constants", "pilot", "plan"):
        if meta.get(k) != cur.get(k):
            refuse("the cache's %s differs from this analyzer's (%s vs %s)" % (k, meta.get(k), cur.get(k)))
    if meta.get("diptest") != DIPTEST_PIN:
        refuse("the cache's diptest %s is not the pinned %s" % (meta.get("diptest"), DIPTEST_PIN))
    for t_old, t_cur in zip(meta["trees"], cur["trees"]):
        for k in ("name", "recipe", "dim", "t", "snapshot", "m", "csv_lf", "jsonl_lf", "j_hier"):
            if t_old.get(k) != t_cur.get(k):
                refuse("the cache's tree %s field %s differs from the inputs" % (t_old.get("name"), k))
    if meta["tasks"] != cur["tasks"]:
        refuse("the cache's task list differs from the inputs' sites")
    extra = [k for k in done if k not in set(meta["tasks"])]
    if extra:
        refuse("the cache holds %d tasks outside its task list" % len(extra))
    missing = [k for k in meta["tasks"] if k not in done]
    if a.pilot:
        share = len(missing) / float(len(meta["tasks"]))
        if share > PILOT_MISSING_MAX:
            refuse("pilot: %d of %d tasks missing (%.1f%% > %.0f%%): the truncation guard refuses" % (
                len(missing), len(meta["tasks"]), 100 * share, 100 * PILOT_MISSING_MAX))
    complete = not missing and not a.pilot
    suffix = "" if complete else ("_PILOT" if a.pilot else "_partial")
    if missing:
        print("%s %d of %d tasks missing -> %s (NOT the outcome of record)" % (TAG, len(missing), len(meta["tasks"]), suffix))
        if not a.pilot:
            buf.write("PARTIAL: %d of %d tasks missing; NOT the outcome of record\n" % (len(missing), len(meta["tasks"])))
            write_text(os.path.join(out_dir, OUTCOME.replace(".txt", suffix + ".txt")), buf.getvalue(), once=False)
            return 2
    if a.pilot:
        for c in ctxs:
            nm = c["spec"]["name"]
            keep = [s for s in c["sites"][:a.pilot] if all(task_key(nm, s["node_id"], k) in done for k in KINDS)]
            say("[PILOT] %s: the first %d sites, %d with every task (%s dropped); the hierarchy is the pilot subset's" % (
                nm, a.pilot, len(keep), len(c["sites"][:a.pilot]) - len(keep)))
            c["sites"] = keep
            c["fam"], c["anc"], c["multi"] = _cr(CR.site_structure, keep, c["rec"])
            c["j_hier"] = c["j_hier"] & {s["node_id"] for s in keep}
    _res, rows = render(ctxs, done, meta, a.pilot, say)
    os.makedirs(out_dir, exist_ok=True)
    write_text(os.path.join(out_dir, OUTCOME.replace(".txt", suffix + ".txt")), buf.getvalue(), once=complete)
    write_text(os.path.join(out_dir, SITES_CSV.replace(".csv", suffix + ".csv")), sites_csv_text(rows), once=complete)
    print("%s wrote %s and %s (%s)" % (TAG, OUTCOME.replace(".txt", suffix + ".txt"), SITES_CSV.replace(".csv", suffix + ".csv"),
                                        "write-once" if complete else "overwritable"))
    return 0


def parse_args(argv):
    ap = argparse.ArgumentParser(description=TEST)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--probe", "--dry-run", "--run", "--analyze"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--data-root")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--pilot", type=int, default=0)
    ap.add_argument("--pylib", default=PYLIB_DEFAULT)
    ap.add_argument("--no-probe", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--fixture-specs")
    ap.add_argument("--skip-selftest-gate", action="store_true")
    a = ap.parse_args(argv)
    if a.pilot < 0:
        refuse("--pilot must be >= 0")
    if a.skip_selftest_gate and not a.fixture_specs:
        refuse("--skip-selftest-gate is a fixture-only flag")
    return a


def main(argv=None):
    a = parse_args(sys.argv[1:] if argv is None else argv)
    if a.selftest:
        return selftest(pylib=a.pylib)
    if a.mutants:
        return mutants(pylib=a.pylib)
    if a.probe:
        return mode_probe(a)
    if a.dry_run:
        return mode_dry_run(a)
    if a.run:
        return mode_run(a)
    return mode_analyze(a)


# ================================================================================================ selftest
class Checks(object):
    def __init__(self, quiet=False):
        self.n = 0
        self.quiet = quiet

    def ok(self, cond, what):
        self.n += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not self.quiet:
            print("  ok  " + what)


def _run_main(argv):
    """-> (rc or 'REFUSED: ...', stdout text)."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = main(argv)
    except SystemExit as e:
        rc = "REFUSED: %s" % e
    return rc, buf.getvalue()


def _line(text, prefix):
    for ln in text.split("\n"):
        if ln.startswith(prefix):
            return ln
    return None


def _blob4096(v_slice, rng, dim):
    raw = np.concatenate([np.asarray(v_slice, dtype=np.float64), 0.001 * rng.standard_normal(RAW_DIM - dim)])
    return raw.astype(">f4").tobytes()


FIX_BAREQ = dict(   # anchored: root not a site; TOP = the three anchors; n00000020 is bimodal under a unimodal parent
    name="bareq512_s42", recipe="R512", dim=8, t=0, snapshot="FIX_bareq_snap", split="id-disjoint only",
    nodes=[("n00000001", 0, None, ["n00000006", "n00000015", "n00000003"]),
           ("n00000006", 1, "n00000001", ["n00000021", "n00000022"]),
           ("n00000015", 1, "n00000001", ["n00000020", "n00000023"]),
           ("n00000003", 1, "n00000001", ["n00000024", "n00000026"]),
           ("n00000021", 2, "n00000006", ["n00000031", "n00000032"]),
           ("n00000020", 2, "n00000015", ["n00000033", "n00000034"]),
           ("n00000026", 2, "n00000003", ["n00000035", "n00000036"])],
    leaves={"n00000031": ("A", 80), "n00000032": ("B", 80), "n00000022": ("A", 60),
            "n00000033": ("C", 70), "n00000034": ("D", 70), "n00000023": ("G", 260),
            "n00000024": ("E", 90), "n00000035": ("F", 60), "n00000036": ("F", 60)},
    k_exceed={"n00000006": 0, "n00000015": 120, "n00000003": 60, "n00000021": 150, "n00000020": 0, "n00000026": 90},
    j_hier=["n00000006"], named=list(NAMED))
FIX_AF = dict(      # anchor-free: the root is a site (TOP alone)
    name="af_clean_s42", recipe="R256", dim=4, t=1, snapshot="FIX_af_snap", split="content-closed",
    nodes=[("n00000001", 0, None, ["n00000002", "n00000003"]),
           ("n00000002", 1, "n00000001", ["n00000004", "n00000005"]),
           ("n00000003", 1, "n00000001", ["n00000006", "n00000007"])],
    leaves={"n00000004": ("P", 120), "n00000005": ("P", 120), "n00000006": ("Q", 110), "n00000007": ("R", 110)},
    k_exceed={"n00000001": 0, "n00000002": 0, "n00000003": 0},
    j_hier=["n00000001", "n00000002", "n00000003"], named=[])


def _centres(dim):
    """Population centres in the slice (before unit-normalisation)."""
    e = np.eye(dim)
    base = e[0]
    return {"A": base + 0.6 * e[1], "B": base - 0.6 * e[1], "C": base + 0.05 * e[3], "D": base - 0.05 * e[3],
            "G": base, "E": base + 0.6 * e[2], "F": base - 0.6 * e[2],
            "P": base + 0.7 * e[1], "Q": base - 0.7 * e[1] + 0.5 * e[2], "R": base - 0.7 * e[1] - 0.5 * e[2]}


def _draw(pop, n, dim, rng):
    c = _centres(dim)[pop]
    if pop == "G":       # a wide unimodal cloud along e2 (the anchor whose child n00000020 is bimodal at a small scale)
        sd = np.full(dim, 0.04)
        sd[2] = 0.30
        return c + rng.standard_normal((n, dim)) * sd
    sd = 0.01 if pop in ("C", "D") else 0.05
    return c + sd * rng.standard_normal((n, dim))


def _fx_region(nid, nodes):
    """The fixture's own region (recursive, independent of region_query_ids): sorted union of queryIds of the subtree."""
    out = set(nodes[nid]["queryIds"])
    for c in nodes[nid]["childIds"]:
        if c in nodes:
            out |= set(_fx_region(c, nodes))
    return sorted(out)


def build_fixture(root, fixes=(FIX_BAREQ, FIX_AF), seed=7, mutate=None):
    """A fixture data root: snapshots.db, embeddings_cache.db, site-null CSVs and jsonl records, and the specs JSON.
    mutate: None or one of 'n_mismatch', 'bad_vmfmu', 'j_wrong', 'zero_sites', 'graph_mismatch'."""
    os.makedirs(root, exist_ok=True)
    open(os.path.join(root, FIXTURE_MARK), "w").close()
    rng = np.random.default_rng(seed)
    specs, graphs, emb = [], {}, []
    for fx in fixes:
        dim = fx["dim"]
        qids, node_q = {}, {}
        for leaf, (pop, n) in sorted(fx["leaves"].items()):
            Xs = _draw(pop, n, dim, rng)
            ids = ["%s_%s_%03d" % (fx["name"][:2], leaf, j) for j in range(n)]
            node_q[leaf] = ids
            for q, x in zip(ids, Xs):
                qids[q] = x
                emb.append((q, _blob4096(x, rng, dim)))
        nodes = {}
        for nid, depth, parent, kids in fx["nodes"]:
            nodes[nid] = dict(id=nid, label="L" + nid[-2:], depth=depth, isLeaf=False, isBridge=False,
                              parentIds=[parent] if parent else [], childIds=list(kids), queryIds=[])
        for leaf in fx["leaves"]:
            par = [nid for nid, _d, _p, kids in fx["nodes"] if leaf in kids][0]
            nodes[leaf] = dict(id=leaf, label="L" + leaf[-2:], depth=nodes[par]["depth"] + 1, isLeaf=True, isBridge=False,
                               parentIds=[par], childIds=[], queryIds=node_q[leaf])
        byid = nodes

        def unit_slice(q):
            x = qids[q]
            return x / np.linalg.norm(x)
        for nid in nodes:
            mem = _fx_region(nid, byid)
            mu = np.sum([unit_slice(q) for q in mem], axis=0)
            mu = mu / np.linalg.norm(mu)
            if mutate == "bad_vmfmu" and nid == fx["nodes"][-1][0] and fx is fixes[0]:
                mu = -mu
            nodes[nid]["vmfMu"] = [float(x) for x in mu]
            nodes[nid]["sliceDim"] = dim
        gnodes = json.loads(json.dumps(list(nodes.values())))
        if mutate == "graph_mismatch" and fx is fixes[0]:
            for nd in gnodes:
                if nd["id"] == "n00000003":
                    nd["childIds"] = nd["childIds"] + ["n00000099"]
        graphs[fx["snapshot"]] = json.dumps(dict(rootId=fx["nodes"][0][0], nodes=gnodes))
        rec = dict(iteration=1, nodes=[{k: v for k, v in nd.items() if k != "queryIds"} for nd in nodes.values()])
        jl_rel = "fx/%s/dag_snapshots.jsonl" % fx["name"]
        os.makedirs(os.path.join(root, os.path.dirname(jl_rel)), exist_ok=True)
        with open(os.path.join(root, jl_rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(iteration=0, nodes=[])) + "\n" + json.dumps(rec) + "\n")
        csv_rel = "fx/%s/site_null.csv" % fx["name"]
        hdr = ["snapshot_id", "node_id", "label", "depth", "n", "k", "observed_sep", "site_null_p50", "site_null_p95", "q_site",
               "site_reach_pct", "site_accept_pct", "defl_dims", "defl_null_p50", "defl_null_p95", "q_deflated",
               "defl_reach_pct", "defl_accept_pct", "cert_site_p95", "cert_deflated_p95", "trunk_member", "feasibility", "reps"]
        lines = [",".join(hdr)]
        site_rows = [] if mutate == "zero_sites" and fx is fixes[0] else [nd for nd in fx["nodes"] if nd[0] in fx["k_exceed"]]
        for nid, depth, _p, kids in site_rows:
            n = len(_fx_region(nid, byid)) + (1 if (mutate == "n_mismatch" and nid == site_rows[-1][0]
                                                          and fx is fixes[0]) else 0)
            k = fx["k_exceed"][nid]
            lines.append(",".join(['"%s"' % fx["snapshot"], '"%s"' % nid, '"L%s"' % nid[-2:], str(depth), str(n), str(len(kids)),
                                   "0.05", "0.04", "0.045", "%.4f" % (k / 300.0), "100.0", "100.0", "1", "0.02", "0.03",
                                   "0.0000", "100.0", "50.0", "true" if k <= 14 else "false", "true", "false", "OK", "300"]))
        with open(os.path.join(root, csv_rel), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n")
        j_hier = list(fx["j_hier"])
        if mutate == "j_wrong" and fx is fixes[0]:
            j_hier = j_hier + ["n00000003"]
        specs.append(dict(name=fx["name"], recipe=fx["recipe"], dim=dim, t=fx["t"], snapshot=fx["snapshot"],
                          m=len(site_rows), split=fx["split"], j_hier=sorted(j_hier), named=list(fx["named"]),
                          csv=dict(rel=csv_rel, lf=hashlib.sha256(lf_bytes(os.path.join(root, csv_rel))).hexdigest()),
                          jsonl=dict(rel=jl_rel, lf=hashlib.sha256(lf_bytes(os.path.join(root, jl_rel))).hexdigest())))
    c = _RAW_CONNECT(os.path.join(root, "snapshots.db"))
    c.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT)")
    for sid, g in graphs.items():
        c.execute("INSERT INTO snapshots VALUES (?, ?)", (sid, g))
    c.commit()
    c.close()
    c = _RAW_CONNECT(os.path.join(root, "embeddings_cache.db"))
    c.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    c.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, ground_truth_category TEXT "
              "DEFAULT '', query_id INTEGER DEFAULT -1)")
    for q, b in emb:
        c.execute("INSERT INTO queries (id, raw_text, distilled_text) VALUES (?, ?, ?)", (q, "text " + q, "text " + q))
        c.execute("INSERT INTO embeddings (query, vector) VALUES (?, ?)", ("text " + q, b))
    c.commit()
    c.close()
    sp = os.path.join(root, "specs.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(specs, f)
    return sp


def _fx_args(root, spec_path, out, *extra):
    return ["--data-root", root, "--fixture-specs", spec_path, "--out", out, "--no-probe", "--skip-selftest-gate"] + list(extra)


def _rewrite_cache(src, dst_dir, fn):
    """Copy a cache, rewriting every row's p by fn(key, p) (None keeps the row out: a missing task)."""
    os.makedirs(dst_dir, exist_ok=True)
    with open(src, encoding="utf-8") as f:
        lines = f.read().splitlines()
    out = [lines[0]]
    for ln in lines[1:]:
        r = json.loads(ln)
        p = fn(r["key"], r["p"])
        if p is None:
            continue
        r["p"] = p
        out.append(json.dumps(r, sort_keys=True))
    with open(os.path.join(dst_dir, "cache.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def selftest(pylib=PYLIB_DEFAULT, quiet=False, e2e=True):
    chk = Checks(quiet=quiet)
    say = (lambda s: None) if quiet else print
    say("%s SELFTEST (synthetic and fixture data only; no DB of record is opened)" % TAG)
    # ---- ST1 pins
    mp = module_pins()
    chk.ok(mp["cert_split_dip.py"] == CSD_BLOB and mp["cert_resolution.py"] == CR_BLOB and mp["embedder_guard.py"] == EG_BLOB,
           "ST1 the three imported modules are the pinned blobs")
    chk.ok(CR.Q == Q and CSD.ALPHA == ALPHA and CSD.R_HALV == 20, "ST1 q = 1/20, alpha 0.05, R = 20 as the record modules")
    chk.ok(len(KINDS) == 12 and KINDS[0] == "OBS" and KINDS[-1] == "P6", "ST1 12 tasks per site: OBS, N0..N9, P6")
    chk.ok([t["m"] for t in TREES] == [70, 69] and [t["dim"] for t in TREES] == [512, 256]
           and TREES[0]["csv"]["lf"].startswith("ea0cb19865f63036") and TREES[1]["csv"]["lf"].startswith("e15302b76a1aba3a"),
           "ST1 the trees of record: m 70 / 69, slices 512 / 256, CERT-RESOLUTION's CSV pins")
    chk.ok(len(TREES[1]["j_hier"]) == 8 and TREES[0]["j_hier"] == sorted(NAMED), "ST1 the recorded J sets (2 and 8)")
    # ---- ST2 regionQueryIds
    g = {"a": dict(childIds=["b", "c", "zz"], queryIds=[]), "b": dict(childIds=["d"], queryIds=["q1", "q2"]),
         "c": dict(childIds=["d"], queryIds=["q3"]), "d": dict(childIds=[], queryIds=["q2", "q4"])}
    chk.ok(sorted(region_query_ids("a", g)) == ["q1", "q2", "q3", "q4"] and sorted(region_query_ids("c", g)) == ["q2", "q3", "q4"],
           "ST2 regionQueryIds: DFS union over childIds, shared child once, absent child skipped")
    # ---- ST3 null generator draw for draw
    rng = np.random.default_rng(3)
    X = CSD.unit(rng.standard_normal((40, 6)) * 0.1 + np.array([1, 0, 0, 0, 0, 0.0]))
    Zf = np.random.default_rng(11).standard_normal((40, 40))
    ref = CSD.unit(X.mean(axis=0) + (Zf @ (X - X.mean(axis=0))) / math.sqrt(40))
    U, _s, _vt = np.linalg.svd(X - X.mean(axis=0), full_matrices=False)
    mine = gen_null(X, None, Z=Zf @ U)
    chk.ok(float(np.abs(mine - ref).max()) < 1e-10, "ST3 eigen-form null == cert_split_dip.gen_matched draw for draw (Z U)")
    y1 = gen_null(X, np.random.default_rng([NULL_SEED, 0, 2, 5]))
    y2 = make_rows("N5", X, dict(t=0, i=2))
    chk.ok(np.array_equal(y1, y2) and y1.shape == X.shape, "ST3 NULL draw m uses default_rng([202611073, t, i, m])")
    # ---- ST4 plant seeds
    ids = ["q%02d" % j for j in range(40)]
    u = CP.direction(U_SEED_P + 1000 * 1 + 3 - CP.U_SEED0, dim=6)
    r_ = random.Random(U_SEED_P + 1003)
    gg = np.array([r_.gauss(0.0, 1.0) for _ in range(6)])
    chk.ok(np.allclose(u, gg / np.linalg.norm(gg)), "ST4 PLANT direction = random.Random(202611071000 + 1000 t + i), normalised")
    hl = CP.halves(ids, H_SEED_P + 1003 - CP.H_SEED0)
    perm = sorted(ids)
    random.Random(H_SEED_P + 1003).shuffle(perm)
    chk.ok(sum(1 for q in ids if hl[q] == "hi") == 20 and set(q for q in ids if hl[q] == "hi") == set(perm[:20]),
           "ST4 PLANT halves = random.Random(202611072000 + 1000 t + i).shuffle, first floor(n / 2) hi")
    Yp = make_rows("P6", X, dict(t=1, i=3, ids=ids, dim=6))
    hi = np.array([hl[q] == "hi" for q in ids])
    ex, _ = CP.plant_rows(X, hi, u, 6)
    chk.ok(np.array_equal(Yp, ex), "ST4 PLANT rows = cert_planted.plant_rows(X, halves, u, delta 6)")
    # ---- ST5 words
    chk.ok(g0_word(70, 700)[0] == "SIZE-OK" and g0_word(71, 700)[0] == "ANTI-CONSERVATIVE", "ST5 G0 rate bar 0.10 inclusive")
    chk.ok(g0_word(2, 20)[0] == "ANTI-CONSERVATIVE" and g0_word(0, 50)[0] == "SIZE-OK",
           "ST5 G0 CP clause: 2 of 20 (rate 0.10, CP upper 0.317) ANTI; 0 of 50 OK")
    chk.ok(abs(g0_word(0, 700)[2] - (1 - 0.025 ** (1 / 700.0))) < 1e-9, "ST5 G0 CP upper at 0 of 700 = 0.005256")
    chk.ok(w1_word(True, 1, 0, 70) == "SOME" and w1_word(True, 0, 35, 70) == "NONE-POWERED"
           and w1_word(True, 0, 34, 70) == "NONE-UNDERPOWERED" and w1_word(False, 5, 70, 70) == "NOT EVALUABLE",
           "ST5 W1 SOME / NONE-POWERED (35 of 70 = 0.5 inclusive) / NONE-UNDERPOWERED / NOT EVALUABLE")
    chk.ok(w2_word(True, set(NAMED), NAMED) == "BOTH" and w2_word(True, {"n00000015"}, NAMED) == "ONE (n00000015)"
           and w2_word(True, {"n00000099"}, NAMED) == "NEITHER" and w2_word(False, set(NAMED), NAMED) == "NOT EVALUABLE"
           and w2_word(True, set(), []) is None, "ST5 W2 BOTH / ONE / NEITHER / NOT EVALUABLE / undefined")
    chk.ok(w3_word(True, 3, 2) == "MORE" and w3_word(True, 2, 2) == "SAME" and w3_word(True, 1, 2) == "FEWER"
           and w3_word(False, 9, 2) == "NOT EVALUABLE", "ST5 W3 MORE / SAME / FEWER / NOT EVALUABLE")
    chk.ok(fdip_word(True, 2) == (False, []) and fdip_word(True, 3)[0] and fdip_word(False, 0)[0],
           "ST5 F-DIP: 2 replicates not, 3 fire; G0 ANTI fires alone")
    chk.ok(site_word("T", "R", False, False, 0.05, True) == WORD_M3 and site_word("T", "R", False, False, 0.0500001, True) == ""
           and site_word("T", "R", False, True, 0.01, False) == WORD_M2 + "; " + WORD_UNTESTED
           and site_word("T", "R", True, True, 0.0, True) == WORD_M1.format(tree="T", recipe="R")
           and site_word("T", "R", True, True, 0.0, True, False) == WORD_NE,
           "ST5 site words M1 / M2 / M3 (alpha inclusive) / none / UNTESTED / NOT EVALUABLE under G0")
    chk.ok(abs(brier(P3_P, "ONE") - (0.04 + 0.3025 + 0.1225)) < 1e-12, "ST5 Brier over three classes")
    # ---- ST6 rule-7 probe
    procs = [dict(ProcessId=10, ParentProcessId=1, Name="java.exe", CommandLine="java -jar gradle-worker.jar"),
             dict(ProcessId=11, ParentProcessId=1, Name="python.exe", CommandLine="python tools\\analysis\\x.py --run"),
             dict(ProcessId=12, ParentProcessId=1, Name="python.exe", CommandLine="python tools/analysis/x.py --selftest"),
             dict(ProcessId=13, ParentProcessId=1, Name="python.exe", CommandLine="python tools/analysis/x.py --selftest-io"),
             dict(ProcessId=14, ParentProcessId=99, Name="python.exe", CommandLine="python -c spawn_main"),
             dict(ProcessId=15, ParentProcessId=1, Name="ollama.exe", CommandLine="ollama serve"),
             dict(ProcessId=16, ParentProcessId=1, Name="python.exe", CommandLine="python tools/analysis/pool_guard.py --pool x"),
             dict(ProcessId=17, ParentProcessId=1, Name="python.exe", CommandLine="python examples/foo.py")]
    v = {pid: verdict for pid, _n, verdict, _c in classify(procs, {99})}
    chk.ok(v[10].startswith("REFUSE") and v[11].startswith("REFUSE") and v[12].startswith("ADMIT") and v[13].startswith("REFUSE")
           and v[14] == "SELF" and v[15].startswith("OTHER") and v[16].startswith("REFUSE") and v[17].startswith("OTHER"),
           "ST6 W2 classification: JVM, reader, --selftest-io and pool_guard REFUSED; --selftest ADMITTED; own child SELF")
    td = tempfile.mkdtemp(prefix="cds_probe_")
    fp = os.path.join(td, "embeddings_cache.db")
    with open(fp, "wb") as f:
        f.write(b"x")
    if _IS_WIN:
        fh = open(fp, "rb")
        busy = exclusive_open(fp)
        fh.close()
        chk.ok(busy == "BUSY" and exclusive_open(fp) == "FREE" and exclusive_open(fp + "-wal") == "ABSENT",
               "ST6 W1 exclusive open: held BUSY, released FREE, absent ABSENT")
        lines = []
        fh = open(fp, "rb")
        okp = probe(td, lines.append, procs=[], phase="pre")
        fh.close()
        chk.ok(okp is False and any("embeddings_cache.db" in ln and "BUSY -> REFUSE" in ln for ln in lines),
               "ST6 probe() refuses when a pool file is held")
    chk.ok(ram_ok(12.0) and not ram_ok(11.99) and not ram_ok(float("nan")), "ST6 W4 bar >= 12 GB")
    if not e2e:
        say("%s SELFTEST (units) PASS: %d checks" % (TAG, chk.n))
        return 0
    # ---- ST7 end to end on fixture DBs
    _ensure_dip(pylib)
    base = tempfile.mkdtemp(prefix="cds_fx_")
    root = os.path.join(base, "root")
    spec_path = build_fixture(root)
    rc, txt = _run_main(["--dry-run"] + _fx_args(root, spec_path, os.path.join(base, "o_dry")))
    chk.ok(rc == 0 and "[DRY-RUN] dip calls 0 (must be 0)" in txt and "members == CSV n at all 6 sites" in txt
           and "members == CSV n at all 3 sites" in txt and "J hierarchical set reproduced: 1 ['n00000006']" in txt
           and "[TASKS] 108 tasks" in txt, "ST7 --dry-run: 0 dip calls, members checked at every site, J reproduced, 108 tasks")
    chk.ok(not os.path.exists(os.path.join(base, "o_dry")), "ST7 --dry-run writes nothing")
    o1 = os.path.join(base, "o1")
    rc, txt = _run_main(["--run", "--workers", "1"] + _fx_args(root, spec_path, o1))
    chk.ok(rc == 0 and "[RUN] computed 108 tasks" in txt and "EQUAL" in txt, "ST7 --run workers 1: 108 tasks, DB pins EQUAL")
    rc, txt = _run_main(["--run", "--workers", "1"] + _fx_args(root, spec_path, o1))
    chk.ok(rc == 0 and "[CACHE] resume: 108 of 108 tasks cached" in txt and "[RUN] computed 0 tasks" in txt,
           "ST7 resume: nothing recomputed")
    o2 = os.path.join(base, "o2")
    rc, txt2 = _run_main(["--run", "--workers", "2"] + _fx_args(root, spec_path, o2))
    m1, d1 = read_cache(os.path.join(o1, "cache.jsonl"))
    m2, d2 = read_cache(os.path.join(o2, "cache.jsonl"))
    chk.ok(rc == 0 and m1 == m2 and {k: (r["p"], r["ps"], r["ysha"]) for k, r in d1.items()}
           == {k: (r["p"], r["ps"], r["ysha"]) for k, r in d2.items()}, "ST7 workers 2 == workers 1 (every p, halving p, row hash)")
    # independent recomputation of one OBS p and the NULL / PLANT row hashes
    specs = json.load(open(spec_path, encoding="utf-8"))
    con = _RAW_CONNECT(os.path.join(root, "snapshots.db"))
    gb = json.loads(con.execute("SELECT graph FROM snapshots WHERE id = ?", ("FIX_bareq_snap",)).fetchone()[0])
    con.close()
    byid = {n["id"]: n for n in gb["nodes"]}
    mem = _fx_region("n00000015", {k: dict(v, queryIds=v.get("queryIds") or []) for k, v in byid.items()})
    con = _RAW_CONNECT(os.path.join(root, "embeddings_cache.db"))
    vv = {}
    for q in mem:
        b = con.execute("SELECT e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text WHERE q.id = ?",
                        (q,)).fetchone()[0]
        x = np.frombuffer(b, dtype=">f4")[:8].astype(np.float64)
        vv[q] = x / np.linalg.norm(x)
    con.close()
    Xs = np.stack([vv[q] for q in mem])
    r_obs = CSD.dip_site("CDS|bareq512_s42|n00000015|OBS", Xs)
    i15 = 1
    yn = gen_null(Xs, np.random.default_rng([NULL_SEED, 0, i15, 7]))
    yp = plant(Xs, mem, 0, i15, 8)
    chk.ok(d1["bareq512_s42|n00000015|OBS"]["p"] == float(r_obs["p"]) and d1["bareq512_s42|n00000015|OBS"]["ps"] ==
           [float(x) for x in r_obs["ps"]] and d1["bareq512_s42|n00000015|OBS"]["n"] == len(mem)
           and d1["bareq512_s42|n00000015|OBS"]["ysha"] == sha16_rows(Xs) and len(set(r_obs["ps"])) > 5,
           "ST7 OBS at n00000015 = an independent dip_site on its sorted members at slice 8 (rows, p and all 20 halving p; "
           "name CDS|tree|node|OBS)")
    chk.ok(d1["bareq512_s42|n00000015|N7"]["ysha"] == sha16_rows(yn) and d1["bareq512_s42|n00000015|P6"]["ysha"] == sha16_rows(yp),
           "ST7 NULL draw 7 and PLANT rows at n00000015 = an independent generation from the site's own rows and seeds")
    chk.ok(d1["bareq512_s42|n00000006|OBS"]["n"] == 220 and d1["af_clean_s42|n00000001|OBS"]["n"] == 460,
           "ST7 OBS rows = the whole region (n00000006 220, af root 460)")
    rc, txt = _run_main(["--analyze"] + _fx_args(root, spec_path, o1))
    out1 = open(os.path.join(o1, OUTCOME), encoding="utf-8").read()
    chk.ok(rc == 0 and out1 == txt[txt.index(TEST + " OUTCOME"):txt.index("%s wrote" % TAG)],
           "ST7 --analyze wrote the outcome = its printed readout")
    chk.ok(_line(out1, "[G0] NULL draws certified") is not None and "certified 0 of 60" in _line(out1, "[G0] NULL draws certified")
           and _line(out1, "[G0] NULL draws certified").endswith("-> SIZE-OK"), "ST7 G0 bareq fixture: 0 of 60 -> SIZE-OK")
    chk.ok("MODAL set D = 3 of 6" in out1 and "TOP family 3 sites" in out1, "ST7 bareq fixture: TOP 3, D = 3 of 6")
    chk.ok("W1 (Q1) bareq512_s42: SOME" in out1 and "W2 (Q2) bareq512_s42: ONE (n00000006)" in out1
           and "W3 (Q3) bareq512_s42: MORE (|D| 3 vs |J| 1)" in out1, "ST7 bareq fixture: W1 SOME, W2 ONE (n00000006), W3 MORE")
    chk.ok("bareq512_s42 n00000020: " + WORD_M2 + "; " + WORD_UNTESTED in out1
           and "bareq512_s42 n00000021: " + WORD_M1.format(tree="bareq512_s42", recipe="R512") in out1
           and "  bareq512_s42 n00000015:" not in out1 and "  bareq512_s42 n00000026:" not in out1,
           "ST7 prefix closure: n00000020 (bimodal, parent not rejected) UNTESTED with M2; n00000021 M1; n00000015 and "
           "n00000026 (reached, unimodal) no words")
    chk.ok("W1 (Q1) af_clean_s42: SOME" in out1 and "MODAL set D = 2 of 3" in out1 and "TOP family 1 sites" in out1
           and "W3 (Q3) af_clean_s42: FEWER (|D| 2 vs |J| 3)" in out1 and "W2 (Q2) af_clean_s42: not defined" in out1,
           "ST7 af fixture: root TOP alone, D = 2 of 3, W3 FEWER, W2 undefined")
    chk.ok("F-DIP bareq512_s42: NOT FIRED" in out1 and "F-DIP af_clean_s42: NOT FIRED" in out1, "ST7 F-DIP not fired on both")
    chk.ok("READING (MORE, EXPLORATORY)" in out1 and "P6 af_clean_s42: root n00000001 in D: yes (Brier 0.0100" in out1
           and "P4 bareq512_s42: |D| 3 in [0, 10] (point 3) -> HELD" in out1 and "P9 af_clean_s42: J sites in D 2 of 3" in out1,
           "ST7 predictions printed with values (P4 HELD, P6 Brier 0.01, P9 count)")
    chk.ok(all(("bareq512_s42" not in ln or "af_clean_s42" not in ln) or ln.startswith("S4:") for ln in out1.split("\n")),
           "ST7 S4: no outcome line joins the two trees except the S4 statement")
    sites_txt = open(os.path.join(o1, SITES_CSV), encoding="utf-8").read().splitlines()
    chk.ok(len(sites_txt) == 10 and sites_txt[0].split(",") == SITES_HEADER, "ST7 sites CSV: header + 9 rows")
    rc, txt = _run_main(["--analyze"] + _fx_args(root, spec_path, o1))
    chk.ok(isinstance(rc, str) and "write-once" in rc, "ST7 a second --analyze REFUSES (write-once)")
    # partial and pilot
    op = os.path.join(base, "o_part")
    _rewrite_cache(os.path.join(o1, "cache.jsonl"), op, lambda k, p: None if k == "af_clean_s42|n00000003|N4" else p)
    rc, txt = _run_main(["--analyze"] + _fx_args(root, spec_path, op))
    chk.ok(rc == 2 and os.path.exists(os.path.join(op, "CERT_DIP_SITES_OUTCOME_partial.txt"))
           and not os.path.exists(os.path.join(op, OUTCOME)), "ST7 a partial cache writes *_partial.txt only")
    opl = os.path.join(base, "o_pilot")
    rc, txt = _run_main(["--run", "--pilot", "1"] + _fx_args(root, spec_path, opl))
    rc2, txt2 = _run_main(["--analyze", "--pilot", "1"] + _fx_args(root, spec_path, opl))
    chk.ok(rc == 0 and rc2 == 0 and "[RUN] computed 24 tasks" in txt and os.path.exists(os.path.join(opl, "CERT_DIP_SITES_OUTCOME_PILOT.txt"))
           and not os.path.exists(os.path.join(opl, OUTCOME)), "ST7 --pilot 1: 24 tasks, *_PILOT.txt only")
    mm, dd = read_cache(os.path.join(opl, "pilot_cache.jsonl"))
    _rewrite_cache(os.path.join(opl, "pilot_cache.jsonl"), os.path.join(base, "o_pilot2"),
                   lambda k, p: None if k.endswith("|N1") or k.endswith("|N2") else p)
    os.replace(os.path.join(base, "o_pilot2", "cache.jsonl"), os.path.join(base, "o_pilot2", "pilot_cache.jsonl"))
    rc, txt = _run_main(["--analyze", "--pilot", "1"] + _fx_args(root, spec_path, os.path.join(base, "o_pilot2")))
    chk.ok(isinstance(rc, str) and "truncation guard" in rc, "ST7 pilot: 4 of 24 missing (16.7% > 5%) REFUSED")
    # meta mismatch
    om = os.path.join(base, "o_meta")
    os.makedirs(om)
    with open(os.path.join(o1, "cache.jsonl"), encoding="utf-8") as f:
        lines = f.read().splitlines()
    mt = json.loads(lines[0])
    mt["meta"]["constants"]["delta"] = 4
    with open(os.path.join(om, "cache.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join([json.dumps(mt, sort_keys=True)] + lines[1:]) + "\n")
    rc, txt = _run_main(["--run"] + _fx_args(root, spec_path, om))
    chk.ok(isinstance(rc, str) and "differs from this launch in ['constants']" in rc, "ST7 --run REFUSES a cache meta mismatch")
    rc, txt = _run_main(["--analyze"] + _fx_args(root, spec_path, om))
    chk.ok(isinstance(rc, str) and "constants" in rc, "ST7 --analyze REFUSES a cache meta mismatch")
    # preconditions
    for mut, needle in (("n_mismatch", "membership-count mismatch"), ("bad_vmfmu", "min cosine"),
                        ("j_wrong", "J hierarchical set recomputed"), ("zero_sites", "zero sites"),
                        ("graph_mismatch", "differ between the snapshot graph and the jsonl")):
        rt = os.path.join(base, "root_" + mut)
        spm = build_fixture(rt, mutate=mut)
        rc, txt = _run_main(["--dry-run"] + _fx_args(rt, spm, os.path.join(base, "o_" + mut)))
        chk.ok(isinstance(rc, str) and needle in rc, "ST7 precondition %s REFUSED (%s)" % (mut, needle))
    rc, txt = _run_main(["--run", "--workers", "4"] + _fx_args(root, spec_path, os.path.join(base, "o_w4")))
    chk.ok(isinstance(rc, str) and "at most 3 worker" in rc, "ST7 --workers 4 REFUSED")
    rc, txt = _run_main(["--run", "--no-probe", "--data-root", base, "--out", os.path.join(base, "o_np")])
    chk.ok(isinstance(rc, str) and "fixture data root" in rc, "ST7 --no-probe without a fixture root REFUSED")

    def touch():
        with open(os.path.join(root, "embeddings_cache.db"), "ab") as f:
            f.write(b"\0")
    AFTER_HOOK[0] = touch
    try:
        rc, txt = _run_main(["--run"] + _fx_args(root, spec_path, os.path.join(base, "o_touch")))
    finally:
        AFTER_HOOK[0] = None
    chk.ok(isinstance(rc, str) and "changed during the run" in rc and "CHANGED" in txt, "ST7 a DB change during --run REFUSED")
    # ---- ST8 engineered caches through --analyze
    src = os.path.join(o1, "cache.jsonl")

    def scen(tag, fn):
        d = os.path.join(base, "s_" + tag)
        _rewrite_cache(src, d, fn)
        rc_, t_ = _run_main(["--analyze"] + _fx_args(root, spec_path, d))
        if rc_ != 0:
            raise AssertionError("SELFTEST FAILED: scenario %s analyze rc %r: %s" % (tag, rc_, t_[-400:]))
        return open(os.path.join(d, OUTCOME), encoding="utf-8").read()

    def kind(k):
        return k.split("|")[2]
    t = scen("none_pow", lambda k, p: 0.9 if kind(k) == "OBS" else (0.01 if kind(k) == "P6" else p))
    chk.ok("W1 (Q1) bareq512_s42: NONE-POWERED" in t and "READING (NONE-POWERED, EXPLORATORY): no site of bareq512_s42" in t
           and "W2 (Q2) bareq512_s42: NEITHER" in t and "MODAL set D = 0 of 6" in t, "ST8 NONE-POWERED with its reading; W2 NEITHER")
    t = scen("none_under", lambda k, p: 0.9 if kind(k) in ("OBS", "P6") else p)
    chk.ok("W1 (Q1) bareq512_s42: NONE-UNDERPOWERED" in t and "W1 (Q1) af_clean_s42: NONE-UNDERPOWERED" in t,
           "ST8 NONE-UNDERPOWERED")
    # 3 of 6 bareq PLANT certified (0.5 >= 0.5) at alpha exactly: both inclusive
    pl = {"bareq512_s42|n00000006|P6": 0.05, "bareq512_s42|n00000015|P6": 0.05, "bareq512_s42|n00000003|P6": 0.05}
    t = scen("alpha_incl", lambda k, p: 0.9 if kind(k) == "OBS" else (pl.get(k, 0.9) if kind(k) == "P6" else p))
    chk.ok("W1 (Q1) bareq512_s42: NONE-POWERED" in t and "[PLANT] delta 6: certified 3 of 6" in t,
           "ST8 PLANT p = 0.05 counts (alpha inclusive): 3 of 6 = 0.5 (share inclusive) -> NONE-POWERED")
    t = scen("both", lambda k, p: 1e-6 if kind(k) == "OBS" and k.split("|")[1] in ("n00000006", "n00000015") else p)
    chk.ok("W2 (Q2) bareq512_s42: BOTH" in t and "READING (BOTH, EXPLORATORY)" in t and "P3 bareq512_s42: W2 BOTH (Brier 0.9650"
           in t, "ST8 W2 BOTH with its reading and P3 Brier 0.965")
    # G0 via the CP clause: 5 of 60 bareq NULL draws certified (rate 0.083, CP upper 0.184)
    nk = ["bareq512_s42|n00000026|N%d" % m for m in range(5)]      # depth 2 under an unrejected null parent: no replicate rejects
    t = scen("anti", lambda k, p: 0.04 if k in nk else p)
    chk.ok("certified 5 of 60" in t and "-> ANTI-CONSERVATIVE" in t and "W1 (Q1) bareq512_s42: NOT EVALUABLE" in t
           and "W2 (Q2) bareq512_s42: NOT EVALUABLE" in t and "W3 (Q3) bareq512_s42: NOT EVALUABLE" in t
           and "F-DIP bareq512_s42: FIRED (G0 ANTI-CONSERVATIVE)" in t and "P3 bareq512_s42: NOT SCORED" in t
           and "P4 bareq512_s42: NOT SCORED" in t and "P8 bareq512_s42: NOT SCORED" in t and "[SITE WORDS] bareq512_s42" in t
           and "W1 (Q1) af_clean_s42: SOME" in t and "  bareq512_s42 n00000006: " + WORD_NE in t
           and "replicates with >= 1 rejection: 0 of 10" in t and "[D] n00000006" in t,
           "ST8 G0 ANTI (CP clause alone, 0 replicates): every bareq word NOT EVALUABLE / NOT SCORED, lines still printed; "
           "af unaffected")
    # F-DIP by replicates (bareq, 60 draws: 3 certified keep G0 SIZE-OK, CP upper 0.139): 3 replicates fire, 2 do not
    t = scen("repl3", lambda k, p: 0.0 if k in ("bareq512_s42|n00000006|N0", "bareq512_s42|n00000006|N1",
                                                "bareq512_s42|n00000006|N2") else p)
    chk.ok("replicates with >= 1 rejection: 3 of 10" in t and "F-DIP bareq512_s42: FIRED (3 of 10 NULL-TREE replicates reject"
           in t and "P2 bareq512_s42: replicates with >= 1 rejection 3 (HELD iff <= 1) -> FAILED" in t
           and _line(t, "[G0]").endswith("-> SIZE-OK"), "ST8 F-DIP fires at 3 replicates with G0 SIZE-OK; P2 FAILED")
    t = scen("repl2", lambda k, p: 0.0 if k in ("bareq512_s42|n00000006|N0", "bareq512_s42|n00000006|N1") else p)
    chk.ok("F-DIP bareq512_s42: NOT FIRED" in t and _line(t, "[G0]").endswith("-> SIZE-OK")
           and "P2 bareq512_s42: replicates with >= 1 rejection 2 (HELD iff <= 1) -> FAILED" in t,
           "ST8 2 replicates: F-DIP not fired (G0 SIZE-OK at 2 of 60)")
    t = scen("same", lambda k, p: 0.9 if kind(k) == "OBS" and k.split("|")[1] in ("n00000003", "n00000021") else p)
    chk.ok("W3 (Q3) bareq512_s42: SAME (|D| 1 vs |J| 1)" in t and "P4 bareq512_s42: |D| 1 in [0, 10]" in t,
           "ST8 W3 SAME; P4 at |D| 1")
    t = scen("p4edge", lambda k, p: 1e-9 if kind(k) == "OBS" else p)
    chk.ok("P4 bareq512_s42: |D| 6 in [0, 10]" in t and "P5 af_clean_s42: |D| 3 in [3, 30] (point 12) -> HELD" in t,
           "ST8 P5 band endpoint 3 HELD")
    t = scen("p5low", lambda k, p: 0.9 if kind(k) == "OBS" and k.startswith("af_clean_s42|n00000003") else p)
    chk.ok("P5 af_clean_s42: |D| 1 in [3, 30] (point 12) -> FAILED" in t, "ST8 P5 below the band FAILED")
    say("%s SELFTEST PASS: %d checks" % (TAG, chk.n))
    return 0


# ================================================================================================ mutants
MUTANTS = [
    # (id, description, old, new) -- applied to a copy of this file; --selftest on the copy must FAIL
    ("X01", "G0 rate bar inclusive -> strict", "ok = bool(Fraction(k, N) <= G0_RATE and hi <= G0_CP)",
     "ok = bool(Fraction(k, N) < G0_RATE and hi <= G0_CP)"),
    ("X02", "G0 CP clause dropped", "ok = bool(Fraction(k, N) <= G0_RATE and hi <= G0_CP)", "ok = bool(Fraction(k, N) <= G0_RATE)"),
    ("X03", "G0 denominator m instead of m x M", "    N0 = m * M_NULL\n", "    N0 = m\n"),
    ("X04", "G0 counted on OBS (wrong population)", "k0 = sum(1 for v in nodes for x in p_null[v] if x <= ALPHA)",
     "k0 = sum(1 for v in nodes for x in [p_obs[v]] * M_NULL if x <= ALPHA)"),
    ("X05", "MODAL set from the flat BH (nesting ignored)", "D, reached = set(H[\"rejected\"]), set(H[\"reached\"])",
     "D, reached = set(flat), set(H[\"reached\"])"),
    ("X06", "hierarchical BH without ancestors (prefix closure lost)",
     "H = _cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_obs[v]) for v in nodes}, Q)",
     "H = _cr(CR.hierarchical_bh, sites, {v: 'TOP' for v in nodes}, {v: set() for v in nodes}, {v: Fraction(p_obs[v]) for v in nodes}, Q)"),
    ("X07", "BH level 0.10", "Q = Fraction(1, 20)                # BH level", "Q = Fraction(1, 10)                # BH level"),
    ("X08", "per-site alpha strict", "    elif p <= ALPHA:\n        w = WORD_M3", "    elif p < ALPHA:\n        w = WORD_M3"),
    ("X09", "PLANT count alpha strict", "a = sum(1 for v in nodes if p_pl[v] <= ALPHA)", "a = sum(1 for v in nodes if p_pl[v] < ALPHA)"),
    ("X10", "W1 power share strict", "return \"NONE-POWERED\" if Fraction(plant_cert, m) >= POWER_SHARE",
     "return \"NONE-POWERED\" if Fraction(plant_cert, m) > POWER_SHARE"),
    ("X11", "W2 BOTH on one site", "    if len(inn) == len(named):\n        return \"BOTH\"", "    if len(inn) >= 1:\n        return \"BOTH\""),
    ("X12", "W2 skips the G0 gate", "    if not named:\n        return None\n    if not g0ok:\n        return \"NOT EVALUABLE\"",
     "    if not named:\n        return None"),
    ("X13", "W3 against the flat set", "w3 = w3_word(g0ok, len(D), len(ctx[\"j_hier\"]))", "w3 = w3_word(g0ok, len(D), len(flat))"),
    ("X14", "W3 MORE / FEWER swapped", "return \"MORE\" if h > j else (\"SAME\" if h == j else \"FEWER\")",
     "return \"FEWER\" if h > j else (\"SAME\" if h == j else \"MORE\")"),
    ("X15", "F-DIP replicate bar 2", "FDIP_REPL = 3", "FDIP_REPL = 2"),
    ("X16", "F-DIP without the G0 clause", "    if not g0ok:\n        clauses.append(\"G0 ANTI-CONSERVATIVE\")\n", ""),
    ("X17", "NOT EVALUABLE path omits the W2 line", "    if w2 is not None:\n        say(\"W2 (Q2)",
     "    if w2 is not None and g0ok:\n        say(\"W2 (Q2)"),
    ("X18", "members checked at the first site only", "    for s in sites:\n        ids = sorted(region_query_ids(s[\"node_id\"], byid))\n        if len(ids) != s[\"n\"]:",
     "    for s in sites:\n        ids = sorted(region_query_ids(s[\"node_id\"], byid))\n        if len(ids) != s[\"n\"] and s is sites[0]:"),
    ("X19", "members = the node's own queryIds (no DFS)", "        for c in node.get(\"childIds\") or []:\n            if c in byid:\n                stack.append(c)",
     "        pass"),
    ("X20", "embedder guard skipped", "            res = EG.guard(con, dbp,", "            res = dict(min_cos=1.0) if True else EG.guard(con, dbp,"),
    ("X21", "J reproduction not checked", "    if sorted(jh) != sorted(spec[\"j_hier\"]):", "    if False:"),
    ("X22", "zero sites admitted", "    if n_rows == 0:\n        refuse(", "    if False:\n        refuse("),
    ("X23", "slice width ignored (read at 4 for every tree)", "        vec, dims = EG.read_vectors(con, union, spec[\"dim\"])",
     "        vec, dims = EG.read_vectors(con, union, 4)"),
    ("X24", "NULL seed off by one draw", "return gen_null(X, np.random.default_rng([NULL_SEED, job[\"t\"], job[\"i\"], m]))",
     "return gen_null(X, np.random.default_rng([NULL_SEED, job[\"t\"], job[\"i\"], m + 1]))"),
    ("X25", "NULL from a uniform Gaussian, not the site's moments", "    return CSD.unit(mu + (Z * s[None, :]) @ Vt / math.sqrt(n))",
     "    return CSD.unit(mu + Z @ Vt / math.sqrt(n))"),
    ("X26", "PLANT delta 4", "    Y, _s = CP.plant_rows(X, hi, u, DELTA)", "    Y, _s = CP.plant_rows(X, hi, u, 4)"),
    ("X27", "halving name without the tree", "            r = dip(\"CDS|\" + key, Y)", "            r = dip(\"CDS|\" + job[\"node\"] + \"|\" + kind, Y)"),
    ("X28", "DB after-state not compared", "    if after != before:\n        refuse(", "    if False:\n        refuse("),
    ("X29", "analyze writes the outcome from a partial cache", "    complete = not missing and not a.pilot",
     "    complete = not a.pilot\n    missing = []"),
    ("X30", "outcome not write-once", "            with open(path, \"x\", encoding=\"utf-8\", newline=\"\\n\") as f:\n                f.write(text)\n        except FileExistsError:",
     "            with open(path, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:\n                f.write(text)\n        except FileExistsError:"),
    ("X31", "resume recomputes cached tasks", "kinds = [k for k in KINDS if task_key(sp[\"name\"], v, k) not in done]", "kinds = list(KINDS)"),
    ("X32", "meta mismatch ignored on --run", "        if old != meta:\n", "        if False:\n"),
    ("X33", "workers cap 4", "MAX_WORKERS = 3", "MAX_WORKERS = 4"),
    ("X34", "probe admits a JVM", "            v = \"REFUSE (a JVM: construction, site null or Gradle worker)\"",
     "            v = \"OTHER (a JVM)\""),
    ("X35", "probe admits a busy pool file", "        bad = st not in (\"FREE\", \"ABSENT\")", "        bad = st not in (\"FREE\", \"ABSENT\", \"BUSY\")"),
    ("X36", "RAM bar 1 GB", "    return bool(gb == gb and gb >= RAM_GB)", "    return bool(gb == gb and gb >= 1.0)"),
    ("X37", "pilot truncation guard off", "        if share > PILOT_MISSING_MAX:", "        if share > 1.0:"),
    ("X38", "--no-probe admitted on any root", "    if (a.no_probe or a.allow_dirty or a.fixture_specs) and not fixture:",
     "    if False:"),
    ("X39", "P5 band upper endpoint used as lower", "\"HELD\" if in_band(len(a[\"D\"]), P5_BAND[1], P5_BAND[2])",
     "\"HELD\" if in_band(len(a[\"D\"]), P5_BAND[1] + 1, P5_BAND[2])"),
    ("X40", "G0 ANTI path skips the NOT SCORED P3 line", "            say(\"P3 bareq512_s42: \" + ns)\n", ""),
    ("X41", "site rows truncated to half the members", "    X = {v: np.stack([vec[q] for q in ids]) for v, ids in members.items()}",
     "    X = {v: np.stack([vec[q] for q in ids[: max(2, len(ids) // 2)]]) for v, ids in members.items()}"),
    ("X43", "site words skip the G0 gate", "    if not g0ok:\n        return WORD_NE\n", ""),
    ("X44", "MODAL set from the PLANT p (wrong arm)",
     "H = _cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_obs[v]) for v in nodes}, Q)",
     "H = _cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_pl[v]) for v in nodes}, Q)"),
    ("X45", "NULL-TREE replicates read the OBS p (wrong arm)",
     "repl = [len(_cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_null[v][j]) for v in nodes}, Q)[\"rejected\"])",
     "repl = [len(_cr(CR.hierarchical_bh, sites, fam, anc, {v: Fraction(p_obs[v]) for v in nodes}, Q)[\"rejected\"])"),
    ("X46", "P2 bar 2 replicates", "P2_MAX = 1", "P2_MAX = 2"),
    ("X42", "graph vs jsonl structure not checked", "            if sorted(byid[v].get(f) or []) != sorted(recn[v].get(f) or []):",
     "            if False:"),
]


MUTANT_CONCURRENCY = 1             # each selftest spawns 2 workers once (ST7): stays within the 3-worker cap


def mutants(pylib=PYLIB_DEFAULT):
    """Each mutant on a copy in the sandbox (scratch_dir temp on E:); --selftest on the copy must FAIL; one at a time."""
    import concurrent.futures as cf
    src = open(SELF, encoding="utf-8").read()
    head, tail = src.split("\nMUTANTS = [", 1)          # mutate the code above the table only
    base = tempfile.mkdtemp(prefix="cds_mut_")
    jobs = []
    for mid, desc, old, new in MUTANTS:
        if head.count(old) != 1:
            print("%s MUTANT %s: the target occurs %d times (must be 1): %r" % (TAG, mid, head.count(old), old[:80]))
            return 1
        d = os.path.join(base, mid)
        os.makedirs(d)
        p = os.path.join(d, "cert_dip_sites.py")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(head.replace(old, new) + "\nMUTANTS = [" + tail)
        jobs.append((mid, desc, p))
    env = dict(os.environ, CDS_SRC_DIR=HERE)

    def run(job):
        mid, desc, p = job
        t0 = time.time()
        r = subprocess.run([sys.executable, p, "--selftest", "--pylib", pylib], capture_output=True, text=True, env=env,
                           timeout=1800)
        last = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()]
        why = next((ln for ln in reversed(last) if "SELFTEST FAILED" in ln or "REFUSED" in ln or "Error" in ln), last[-1] if last
                   else "")
        return mid, desc, r.returncode != 0, why[:160], time.time() - t0
    rows = []
    with cf.ThreadPoolExecutor(max_workers=MUTANT_CONCURRENCY) as ex:
        for res in ex.map(run, jobs):
            rows.append(res)
            print("%s %s %-55s %s (%.0f s) %s" % (TAG, res[0], res[1][:55], "KILLED" if res[2] else "SURVIVED", res[4], res[3]))
    killed = sum(1 for r in rows if r[2])
    print("%s MUTANTS: %d / %d killed" % (TAG, killed, len(rows)))
    return 0 if killed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
