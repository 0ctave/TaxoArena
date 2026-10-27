"""TOPIC-PARTITION-20NG-T1B-NULL addendum readout (zero LLM calls; no construction; no arena pool).

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-09-23 (before any run; the instrument exists and is
pinned, nothing has been launched) -- TOPIC-PARTITION-20NG-T1B-NULL: ..." (a5dfcf0; L11542-L11570 as of 7da2ec5; the
record's "L11525-L11553" is the pre-insertion span), read TOGETHER WITH the registrar's rulings of 2026-09-23
("## Registrar's rulings 2026-09-23 ... six items ruled", 0a1b44b, L13445-L13525): (1) the Support section, (2) AF1 fires
iff A2 = PARTIAL, (3) target item (4) is a POINTER LINE and stays UNDETERMINED, (4) A4's print quotes T1's recorded share
0.158 and never restates T1's counts, (5) the four target strings verbatim with the exact whole-line match rule, the
arm-block line pinned to L120 and L128 checked as unchanged, not superseded, (6) A1 reads the arm's dag_snapshots.jsonl
and may open snapshots.db ONLY mode=ro&immutable=1 to cross-check the leaf id set. Machine record:
docs/agents/results/TOPIC-PARTITION-20NG-T1B-NULL.json; queue item TP20-T1B-NULL.

THIS ADDENDUM DOES NOT TOUCH C2 AND COMPUTES NOTHING ABOUT IT: no per-site NMI, no stratified gap, no OLS, no
permutation, no pooling of T1b's sites with T1's, no restatement of T1's certified / uncertified counts. It does not
touch C0, C1, T1's C3 or P12, and never compares T1b's certified count with T1's or with ANCHOR-FREE-CERT arm 4's as a
certified-count claim (pre-run bracket (b)(5); A4 is the single registered, DESCRIPTIVE-ONLY exception and prints only
the ruled sentence). It imports ONLY tribool / verdict_word (topic_partition.py) and wilson (t3_routing_inflation.py)
and never calls anything else in the main readout; topic_partition.py and its outcome file are never written.

LAUNCH SEQUENCE (the run-operator's, after the reviewer's READY; ONE rule-7 window, AFTER the null has exited):
  python tools/analysis/topic_partition_t1b_null.py --selftest        # synthetic fixtures under tempfile.mkdtemp(); no real DB
  python tools/analysis/topic_partition_t1b_null.py --dry-run         # reads every input read-only, prints the whole outcome, writes nothing
  python tools/analysis/topic_partition_t1b_null.py --run             # write-once outcome (mode "x"); refuses when A1 fails
  python tools/analysis/topic_partition_t1b_null.py --run --record-a1-failed   # ONLY to record AF2 (A1 FAILED) of record
  (--root <checkout> points every path at another checkout; default: this script's own checkout)

WHAT IT READS (all read-only), under experiment_results/topic_partition/:
  site_null_ng_af_bareq512_s42.csv   the arm's own 300-rep site null (97 sites)
  sitenull_ng_af_bareq512_s42.out    the LAST "[SEPBAR]" line (pre-run bracket (b)(7)), which must stand after the last
                                     "[SITENULL-HEAP]" line (the heap guard prints first in every run); the run segment
                                     from that heap line on gives AP1 (OutOfMemoryError, gradle "BUILD ... in <t>")
  ng_af_bareq512_s42/seed_42/dag_snapshots.jsonl   the LAST line (as topic_partition.py), sites = nodes with >= 2 childIds
  topic_partition_outcome.txt        the outcome of record: the four target strings + L128, read as bytes, never written
  <root>/snapshots.db                mode=ro&immutable=1, ONE row (id = the arm's snapshot), leaf id set only. The jsonl
                                     carries no snapshot id, so this leaf-set equality is what binds the jsonl's last tree
                                     to snapshot 20260923_043423_Headless_Run_Auto_ge (ruling (6)'s "taking the snapshot
                                     whose id equals ..." realised the only way the file allows; it is part of clause (1)).
WHAT IT WRITES: experiment_results/topic_partition/t1b_null_addendum_outcome.txt, WRITE-ONCE (open mode "x"), and nothing
else. Never snapshots_frozen.db, never any .db for write, never the main outcome, the CSVs, the .out files or a marker.

THE THREE-CLAUSE GUARD (registration, "THE THREE-CLAUSE GUARD"; each clause prints its values on PASS and on REFUSED):
  (1) PROVENANCE PIN: last [SEPBAR] reads proposalSeparationBar 0.0145 and sliceDim 512; CSV = exactly 97 rows, reps 300
      on every row, one snapshot id = 20260923_043423_Headless_Run_Auto_ge; jsonl sites exactly 97; no orphan either way
      (every CSV node_id is a site, every site has exactly one row); leaf id set of the jsonl = snapshots.db's; leaves'
      sliceDim 512; the A2 denominator (ruling (1)(a)) is root n00000001 with depth-1 sites n00000004 / n00000005.
  (2) DISJOINTNESS: the four target strings are EXACT whole lines at L226 / L238 / L120 / L220 of the outcome of record,
      each occurring exactly once and each containing UNDETERMINED; L128 is unchanged (not a target, not superseded).
  (3) SUPERSESSION BY INSERTION ONLY: the addendum's own outcome path does not exist and is none of the files it may never
      touch; the outcome of record's bytes are identical before the readout, immediately before the write and after it.
CRITERIA A1-A4, PREDICTIONS AP1-AP5, FALSIFIERS AF1-AF2: scored below exactly as registered and ruled. Every print branch
is tagged by hit(); the selftest asserts that the union of tags over its scenarios equals REQUIRED_BRANCHES and that the
number of checks equals SELFTEST_CHECKS.
"""
import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from topic_partition import tribool, verdict_word   # noqa: E402  the ONLY names used from the main readout
from t3_routing_inflation import wilson              # noqa: E402

# ------------------------------------------------------------------------------------------------ pins of record
ARM = "ng_af_bareq512_s42"
SNAPSHOT = "20260923_043423_Headless_Run_Auto_ge"
BAR = 0.0145
SLICE = 512
REPS = 300
N_SITES = 97
ROOT_ID = "n00000001"
D1_IDS = ("n00000004", "n00000005")
POOL = "pf844849e133cda4e"
T1_RECORDED_SHARE = 0.158        # topic_partition_outcome.txt L14, QUOTED, never recomputed (ruling (4))
MAIN_OUTCOME_BLOB = "90632b36bed00d3d39a24dca27f4d428411e5a2a"   # git blob (LF), ruling (5)
AP1_RANGE = (90.0, 140.0)
AP2_RANGE = (0.08, 0.22)
BANDS = (("n<200", lambda n: n < 200), ("200-400", lambda n: 200 <= n < 400),
         ("400-800", lambda n: 400 <= n < 800), (">=800", lambda n: n >= 800))   # as topic_partition.py L863
TARGETS = (   # ruling (5): (registration item, pinned line, exact whole line)
    (1, 226, "C3 beside, T1b (same clauses, its own null at its own bar): UNDETERMINED -- T1b built (leaves 100) but no complete site null"),
    (2, 238, "  P11  UNDETERMINED T1b builds: HELD; more leaves than T1: 100 vs 110: FAILED; certified share comparison: UNDETERMINED; NMI(20) within 0.03 of T1's: |0.5526 - 0.5422| = 0.0104: HELD"),
    (3, 120, "  site null experiment_results/topic_partition/site_null_ng_af_bareq512_s42.csv ABSENT: this arm's certification is UNDETERMINED (C0's null clause FAILED; every criterion and prediction that reads the null is UNDETERMINED); a partial null still refuses"),
    (4, 220, "  certification vs alignment: no site null (UNDETERMINED)"),
)
NON_TARGET = (128, "  site null: ABSENT (certified share UNDETERMINED)")
POINTER_4 = ("T1b certification vs alignment: site null now present; NOT COMPUTED by the addendum (C2 exclusion; a new "
             "test would need its own registration)")
AF1_TEXT = ("the per-corpus pair BUILDS BUT DOES NOT CERTIFY on this corpus - overturns the reading that the FRAMEWORK "
            "512 / 0.0145 pair transfers whole, and narrows the transfer finding to the bar-0.025 / 256-dim recipe alone; "
            "TOPIC-PARTITION-20NG's C3 is untouched either way")
AF2_TEXT = ("ceiling (8) of the TOPIC-PARTITION-20NG outcome STANDS UNCHANGED and the addendum records only that the arm "
            "is not certifiable within the 24 g house heap ceiling; nothing about the certificate is claimed")
SELFTEST_CHECKS = 78
REQUIRED_BRANCHES = frozenset("""
G1:PASS G1:REFUSED G2:PASS G2:REFUSED G3:PASS G3:REFUSED
A1:HELD A1:FAILED A2:HELD A2:PARTIAL A2:UNDETERMINED A3:RECORDED A3:UNDETERMINED
A4:BELOW A4:NOT_BELOW A4:UNDETERMINED AF1:FIRED AF1:NOT_FIRED AF2:FIRED AF2:NOT_FIRED
AP1:HELD AP1:FAILED AP1:UNDETERMINED AP2:HELD AP2:FAILED AP2:UNDETERMINED AP3:HELD AP3:FAILED AP3:UNDETERMINED
AP4:HELD AP4:FAILED AP4:UNDETERMINED AP5:HELD AP5:FAILED
SUP:SUPERSEDED SUP:NOTHING WRITE:WRITTEN WRITE:PREVIEW WRITE:REFUSED_EXISTS
""".split())
BRANCHES = set()


def hit(tag):
    if tag not in REQUIRED_BRANCHES:
        raise SystemExit("[T1B-NULL] internal: branch tag %r is not declared in REQUIRED_BRANCHES" % tag)
    BRANCHES.add(tag)


class Refusal(Exception):
    pass


def die(msg):
    raise SystemExit("[T1B-NULL] REFUSED: %s" % msg)


# ------------------------------------------------------------------------------------------------ paths
class Paths:
    def __init__(self, root=ROOT, snap_db=None):
        self.root = root
        self.res = os.path.join(root, "experiment_results", "topic_partition")
        self.csv = os.path.join(self.res, "site_null_%s.csv" % ARM)
        self.out = os.path.join(self.res, "sitenull_%s.out" % ARM)
        self.jsonl = os.path.join(self.res, ARM, "seed_42", "dag_snapshots.jsonl")
        self.main_outcome = os.path.join(self.res, "topic_partition_outcome.txt")
        self.outcome = os.path.join(self.res, "t1b_null_addendum_outcome.txt")
        self.snap_db = snap_db or os.path.join(root, "snapshots.db")

    def never_touch(self):
        """Registration "FILES IT MAY NEVER TOUCH" plus its own inputs; the outcome path may be none of them."""
        return [self.main_outcome, self.csv, self.out, self.jsonl, self.snap_db,
                os.path.join(self.res, "site_null_ng_af_s42.csv"), os.path.join(self.res, "sitenull_ng_af_s42.out"),
                os.path.join(self.root, "snapshots_frozen.db")]


def rel(p, root):
    try:
        return os.path.relpath(p, root).replace("\\", "/")
    except ValueError:
        return p


def sha16_bytes(b):
    return hashlib.sha256(b).hexdigest()[:16]


def git_blob(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def script_shas():
    raw = open(os.path.abspath(__file__), "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(lf=sha16_bytes(lf), crlf=sha16_bytes(lf.replace(b"\n", b"\r\n")), blob=git_blob(lf)[:12])


# ------------------------------------------------------------------------------------------------ readers
def read_lines(path, errors="strict"):
    """Lines without terminators. The outcome of record is decoded STRICTLY (exact equality); the gradle .out with
    errors="replace" (a Windows console may write cp1252 bytes, e.g. the harness header's dash), as topic_partition.py."""
    b = open(path, "rb").read()
    txt = b.decode("utf-8", errors=errors)
    lines = txt.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return b, [l[:-1] if l.endswith("\r") else l for l in lines]


def last_tree(jsonl):
    last = None
    with open(jsonl, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line
    if last is None:
        raise Refusal("%s has no snapshot line" % jsonl)
    return json.loads(last)


def db_leaf_ids(snap_db, snapshot):
    if not os.path.exists(snap_db):
        raise Refusal("snapshots.db not found at %s (the leaf-set cross-check that binds the jsonl to %s)" % (snap_db, snapshot))
    con = sqlite3.connect("file:%s?mode=ro&immutable=1" % snap_db.replace("\\", "/"), uri=True)
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (snapshot,)).fetchone()
    finally:
        con.close()
    if row is None:
        raise Refusal("snapshot %s is not in snapshots.db" % snapshot)
    g = json.loads(row[0])
    return sorted(n["id"] for n in g["nodes"] if not n.get("childIds"))


def read_csv(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    need = ("snapshot_id", "node_id", "depth", "n", "observed_sep", "site_null_p95", "cert_site_p95", "reps")
    if rows and any(c not in rows[0] for c in need):
        raise Refusal("CSV lacks columns %s" % [c for c in need if c not in rows[0]])
    return rows


def flag(v):
    v = v.strip().lower()
    if v not in ("true", "false"):
        raise Refusal("cert_site_p95 value %r is neither true nor false" % v)
    return v == "true"


def out_segment(path):
    """(last [SEPBAR] line + its index, last heap line index, the run segment from the last heap line on)."""
    _, lines = read_lines(path, errors="replace")
    sep_i = max((i for i, l in enumerate(lines) if "[SEPBAR] proposalSeparationBar=" in l), default=None)
    heap_i = max((i for i, l in enumerate(lines) if "[SITENULL-HEAP] sliceDim=" in l), default=None)
    seg = lines[heap_i:] if heap_i is not None else lines
    return dict(sep_line=lines[sep_i] if sep_i is not None else None, sep_i=sep_i, heap_i=heap_i,
                heap_line=lines[heap_i] if heap_i is not None else None, seg=seg, n_lines=len(lines))


# ------------------------------------------------------------------------------------------------ guard clauses
def clause1(P, out):
    """PROVENANCE PIN. Returns (ok, facts); prints its values on both branches."""
    facts = dict(csv_present=os.path.exists(P.csv))
    try:
        if not os.path.exists(P.out):
            raise Refusal("%s absent (no [SEPBAR] line to pin)" % rel(P.out, P.root))
        seg = out_segment(P.out)
        facts.update(sep_line=seg["sep_line"], sep_i=seg["sep_i"], heap_i=seg["heap_i"])
        if seg["sep_line"] is None:
            raise Refusal("no [SEPBAR] line in %s" % rel(P.out, P.root))
        if seg["heap_i"] is not None and seg["sep_i"] < seg["heap_i"]:
            raise Refusal("the last [SEPBAR] line (line %d) precedes the last [SITENULL-HEAP] line (line %d): it belongs to an earlier run"
                          % (seg["sep_i"] + 1, seg["heap_i"] + 1))
        mb = re.search(r"proposalSeparationBar=([0-9.eE+-]+)", seg["sep_line"])
        ms = re.search(r"sliceDim=(\d+)", seg["sep_line"])
        facts["sep_bar"] = float(mb.group(1)) if mb else None
        facts["sep_slice"] = int(ms.group(1)) if ms else None
        if facts["sep_bar"] is None or abs(facts["sep_bar"] - BAR) > 1e-12:
            raise Refusal("[SEPBAR] bar %s != %s" % (facts["sep_bar"], BAR))
        if facts["sep_slice"] != SLICE:
            raise Refusal("[SEPBAR] sliceDim %s != %d" % (facts["sep_slice"], SLICE))
        if not facts["csv_present"]:
            raise Refusal("%s ABSENT" % rel(P.csv, P.root))
        rows = read_csv(P.csv)
        facts["rows"] = len(rows)
        facts["reps"] = sorted({r["reps"] for r in rows})
        facts["sids"] = sorted({r["snapshot_id"] for r in rows})
        if len(rows) != N_SITES:
            raise Refusal("CSV carries %d site rows, not %d" % (len(rows), N_SITES))
        if facts["reps"] != [str(REPS)]:
            raise Refusal("CSV reps %s: not %d on every row (partial null)" % (facts["reps"], REPS))
        if facts["sids"] != [SNAPSHOT]:
            raise Refusal("CSV snapshot ids %s != [%s] (the arm's own, never T1's)" % (facts["sids"], SNAPSHOT))
        ids = [r["node_id"] for r in rows]
        dup = sorted(i for i in set(ids) if ids.count(i) > 1)
        if dup:
            raise Refusal("CSV node_ids occur more than once: %s" % dup[:5])
        tree = last_tree(P.jsonl)
        byid = {n["id"]: n for n in tree["nodes"]}
        sites = sorted(i for i, n in byid.items() if len(n.get("childIds") or []) >= 2)
        leaves = sorted(i for i, n in byid.items() if n.get("isLeaf", not n.get("childIds")))
        facts.update(jsonl_sites=len(sites), jsonl_leaves=len(leaves), iteration=tree.get("iteration"))
        if len(sites) != N_SITES:
            raise Refusal("dag_snapshots.jsonl (last line) yields %d sites, not %d" % (len(sites), N_SITES))
        orphan_csv = sorted(set(ids) - set(sites)); orphan_site = sorted(set(sites) - set(ids))
        facts.update(orphan_csv=len(orphan_csv), orphan_site=len(orphan_site))
        if orphan_csv or orphan_site:
            raise Refusal("orphans: CSV rows for non-sites %s; sites without a row %s" % (orphan_csv[:5], orphan_site[:5]))
        dims = sorted({byid[l].get("sliceDim", len(byid[l].get("vmfMu") or [])) for l in leaves})
        facts["leaf_dims"] = dims
        if dims != [SLICE]:
            raise Refusal("jsonl leaves carry sliceDim %s, not [%d]" % (dims, SLICE))
        dbl = db_leaf_ids(P.snap_db, SNAPSHOT)
        facts["db_leaves"] = len(dbl)
        if dbl != leaves:
            raise Refusal("leaf id set of the jsonl (%d) != snapshots.db's snapshot %s (%d)" % (len(leaves), SNAPSHOT, len(dbl)))
        roots = [i for i, n in byid.items() if n.get("depth") == 0]
        d1 = sorted(c for c in (byid[roots[0]].get("childIds") or []) if c in sites) if len(roots) == 1 else []
        facts.update(root=roots, d1=d1)
        if roots != [ROOT_ID] or tuple(d1) != D1_IDS:
            raise Refusal("A2 denominator: root %s / depth-1 sites %s != %s / %s (ruling (1)(a))" % (roots, d1, ROOT_ID, list(D1_IDS)))
        facts["csv_rows"] = {r["node_id"]: r for r in rows}
        facts["leaves"] = len(leaves)
        out.append("GUARD (1) PROVENANCE PIN: PASS -- last [SEPBAR] (line %d; after [SITENULL-HEAP] line %s): bar %s, sliceDim %d; CSV %d rows, reps %s, snapshot %s; "
                   "jsonl iteration %s: %d sites, %d leaves (sliceDim %s), orphans CSV->site %d / site->CSV %d; snapshots.db leaf set %d = jsonl's; root %s, depth-1 sites %s"
                   % (facts["sep_i"] + 1, facts["heap_i"] + 1 if facts["heap_i"] is not None else "none", facts["sep_bar"], facts["sep_slice"], len(rows),
                      facts["reps"], SNAPSHOT, facts["iteration"], len(sites), len(leaves), dims, 0, 0, len(dbl), ROOT_ID, " / ".join(d1)))
        hit("G1:PASS")
        return True, facts
    except Refusal as e:
        facts["reason"] = str(e)
        out.append("GUARD (1) PROVENANCE PIN: REFUSED -- %s; values: %s" % (e, {k: v for k, v in facts.items() if k != "csv_rows"}))
        hit("G1:REFUSED")
        return False, facts


def clause2(P, out):
    """DISJOINTNESS: exact whole-line equality at the pinned lines, each target once, each containing UNDETERMINED; L128 unchanged."""
    try:
        if not os.path.exists(P.main_outcome):
            raise Refusal("%s absent" % rel(P.main_outcome, P.root))
        b, lines = read_lines(P.main_outcome)
        vals = []
        for item, ln, s in TARGETS:
            at = lines[ln - 1] if ln <= len(lines) else None
            cnt = sum(1 for l in lines if l == s)
            vals.append("target (%d) L%d equal %s, occurrences %d, UNDETERMINED %s" % (item, ln, at == s, cnt, "UNDETERMINED" in s))
            if at != s or cnt != 1 or "UNDETERMINED" not in s:
                raise Refusal("target (%d) at L%d: pinned-line equal %s, occurrences %d (%s)" % (item, ln, at == s, cnt, "; ".join(vals)))
        ln, s = NON_TARGET
        at = lines[ln - 1] if ln <= len(lines) else None
        vals.append("L%d (not a target) unchanged %s" % (ln, at == s))
        if at != s:
            raise Refusal("L%d changed (not a target, must stand as written): %r" % (ln, at))
        blob = git_blob(b.replace(b"\r\n", b"\n"))
        out.append("GUARD (2) DISJOINTNESS: PASS -- %s; %d lines; blob %s (pinned %s: %s; informational, the match rule is the line rule)"
                   % ("; ".join(vals), len(lines), blob[:12], MAIN_OUTCOME_BLOB[:12], blob == MAIN_OUTCOME_BLOB))
        hit("G2:PASS")
        return True, b
    except Refusal as e:
        out.append("GUARD (2) DISJOINTNESS: REFUSED -- %s; the addendum refuses rather than supersede something it did not read" % e)
        hit("G2:REFUSED")
        return False, None


def clause3_pre(P):
    """SUPERSESSION BY INSERTION ONLY, first half: the addendum's outcome path is fresh and is not a protected file."""
    norm = lambda p: os.path.normcase(os.path.abspath(p))
    bad = [p for p in P.never_touch() if norm(p) == norm(P.outcome)]
    if bad:
        return False, "the outcome path %s is a file the addendum may never touch" % rel(P.outcome, P.root)
    if os.path.exists(P.outcome):
        return False, "%s EXISTS (write-once; nothing written, nothing overwritten)" % rel(P.outcome, P.root)
    return True, "%s absent and not a protected path" % rel(P.outcome, P.root)


# ------------------------------------------------------------------------------------------------ AP1 (the run segment)
def ap1_reading(P):
    if not os.path.exists(P.out):
        return None, "sitenull .out absent"
    seg = out_segment(P.out)
    text = "\n".join(seg["seg"])
    oom = "OutOfMemoryError" in text
    m = None
    for l in seg["seg"]:
        mm = re.search(r"BUILD (SUCCESSFUL|FAILED) in (.+)$", l)
        if mm:
            m = mm
    heap = seg["heap_line"] or "no [SITENULL-HEAP] line"
    if m is None:
        return (False if oom else None), "run segment: OutOfMemoryError %s; no gradle BUILD line (wall time not in the .out); %s" % (oom, heap)
    mins = 0.0
    for v, u in re.findall(r"(\d+)(h|ms|m|s)\b", m.group(2)):
        mins += {"h": 60.0, "m": 1.0, "s": 1 / 60.0, "ms": 1 / 60000.0}[u] * int(v)
    ok = tribool(m.group(1) == "SUCCESSFUL" and not oom and AP1_RANGE[0] <= mins <= AP1_RANGE[1])
    return ok, ("run segment: BUILD %s in %s = %.1f min (task wall clock from gradle's line; registered 90-140); OutOfMemoryError %s; %s"
                % (m.group(1), m.group(2).strip(), mins, oom, heap))


# ------------------------------------------------------------------------------------------------ the readout
def a2_word(a1, clauses):
    """A2 through verdict_word: HELD / (FAILED -> PARTIAL, the arm is built) / UNDETERMINED when A1 fails. Total."""
    if not a1:
        return "UNDETERMINED"
    w = verdict_word(all(tribool(c) for c in clauses))
    if w == "HELD":
        return "HELD"
    if w == "FAILED":
        return "PARTIAL"
    die("A2 verdict %r outside HELD / FAILED on a passed gate" % w)


def readout(P, record_a1_failed=False, write=False, pre_write_hook=None):
    """Build the outcome text; write it (mode "x") only when asked and allowed. Returns (lines, state)."""
    out = []
    shas = script_shas()
    out.append("TOPIC-PARTITION-20NG-T1B-NULL addendum readout (registration docs/judge_v2_program.md a5dfcf0, L11542-L11570 as of 7da2ec5; "
               "registrar's rulings 0a1b44b, L13445-L13525); script sha256[:16] LF %s / CRLF %s (git blob %s, LF); date %s"
               % (shas["lf"], shas["crlf"], shas["blob"], datetime.date.today().isoformat()))
    out.append("pool %s (the corpus's own split; NOT read: no pool, no arena DB, no judge, no construction); arm %s, snapshot %s, bar %s, slice %d, %d reps"
               % (POOL, ARM, SNAPSHOT, BAR, SLICE, REPS))
    ok3, why3 = clause3_pre(P)
    if not ok3:
        out.append("GUARD (3) SUPERSESSION BY INSERTION ONLY: REFUSED -- %s" % why3)
        hit("G3:REFUSED"); hit("WRITE:REFUSED_EXISTS")
        return out, dict(written=False, refused=True)
    ok2, main_bytes = clause2(P, out)
    ok1, f = clause1(P, out)
    out.append("GUARD (3) SUPERSESSION BY INSERTION ONLY: PASS (pre-write) -- %s; outcome of record sha256[:16] %s, never opened for write"
               % (why3, sha16_bytes(main_bytes) if main_bytes is not None else "unread"))
    hit("G3:PASS")
    a1 = tribool(ok1 and ok2 and ok3)
    rows = f.get("csv_rows") or {}
    out.append("A1 GATE (SCOREABLE, deterministic): %s -- CSV %s; rows %s; reps %s; snapshot ids %s; clauses (1) %s / (2) %s / (3) %s"
               % ("HELD" if a1 else "FAILED", "present" if f.get("csv_present") else "ABSENT", f.get("rows", "n/a"), f.get("reps", "n/a"),
                  f.get("sids", "n/a"), "PASS" if ok1 else "REFUSED", "PASS" if ok2 else "REFUSED", "PASS" if ok3 else "REFUSED"))
    hit("A1:HELD" if a1 else "A1:FAILED")
    # A2 ------------------------------------------------------------------------------------------------------
    root_c = d1_c = None
    if a1:
        rr = rows[ROOT_ID]
        root_c = tribool(flag(rr["cert_site_p95"]))
        d1_c = tribool(any(flag(rows[d]["cert_site_p95"]) for d in D1_IDS))
        for nid, tag in ((ROOT_ID, "root"),) + tuple((d, "depth-1") for d in D1_IDS):
            r = rows[nid]
            obs, p95 = float(r["observed_sep"]), float(r["site_null_p95"])
            out.append("  A2 row %s %s: depth %s n %s observed %.6f site p95 %.6f margin %.3f cert_site_p95 %s (the CSV's flag decides; observed >= p95 at printed precision %s)"
                       % (tag, nid, r["depth"], r["n"], obs, p95, obs / p95 if p95 else float("nan"), flag(r["cert_site_p95"]), bool(obs >= p95)))
    a2 = a2_word(a1, [f.get("leaves", 0) > 20, root_c, d1_c] if a1 else [])
    if a2 == "UNDETERMINED":
        out.append("A2 (C3-beside for T1b; SCOREABLE): UNDETERMINED -- A1 FAILED")
    else:
        out.append("A2 (C3-beside for T1b; SCOREABLE, a structural read of three rows; Monte-Carlo fragility of a 300-rep p95 disclosed, not modelled): %s -- leaves %d (> 20: %s); root certified %s; at least one depth-1 site certified %s"
                   % (a2, f["leaves"], f["leaves"] > 20, verdict_word(root_c), verdict_word(d1_c)))
    hit("A2:" + a2)
    # A3 ------------------------------------------------------------------------------------------------------
    k = share = None
    if a1:
        k = sum(1 for r in rows.values() if flag(r["cert_site_p95"]))
        share = k / N_SITES
        lo, hi = wilson(k, N_SITES)
        bands = []
        for name, cond in BANDS:
            b = [r for r in rows.values() if cond(int(r["n"]))]
            bands.append("%s %d/%d" % (name, sum(1 for r in b if flag(r["cert_site_p95"])), len(b)))
        out.append("A3 (DESCRIPTIVE-ONLY; recorded): T1b certified share (cert_site_p95, %d reps, bar %s) %d of %d = %.3f [%.3f, %.3f] (Wilson 95%%, NOMINAL: sites are nested, n_eff %d is an upper bound); by site-size band: %s"
                   % (REPS, BAR, k, N_SITES, share, lo, hi, N_SITES, "; ".join(bands)))
        hit("A3:RECORDED")
    else:
        out.append("A3 (DESCRIPTIVE-ONLY): UNDETERMINED -- A1 FAILED")
        hit("A3:UNDETERMINED")
    # A4 ------------------------------------------------------------------------------------------------------
    below = None
    if a1:
        below = tribool(share < T1_RECORDED_SHARE)
        out.append("A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): %s -- T1b certified share %d of %d = %.3f [%.3f, %.3f; Wilson, nominal] against T1's RECORDED share %.3f "
                   "(topic_partition_outcome.txt L14, blob %s; quoted, not recomputed): %s at the point; DESCRIPTIVE-ONLY under (b)(5); no cross-bar certified-count claim"
                   % (verdict_word(below), k, N_SITES, share, lo, hi, T1_RECORDED_SHARE, MAIN_OUTCOME_BLOB[:12], "below" if below else "not below"))
        hit("A4:BELOW" if below else "A4:NOT_BELOW")
    else:
        out.append("A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): UNDETERMINED -- A1 FAILED")
        hit("A4:UNDETERMINED")
    # falsifiers ----------------------------------------------------------------------------------------------
    af1 = bool(a2 == "PARTIAL")
    af2 = bool(not a1)
    out.append("AF1 (fires iff A2 = PARTIAL, ruling (2)): %s" % ("FIRED -- " + AF1_TEXT if af1 else "NOT FIRED (A2 %s)" % a2))
    hit("AF1:FIRED" if af1 else "AF1:NOT_FIRED")
    out.append("AF2 (fires iff A1 FAILED, ruling (2)): %s" % ("FIRED -- " + AF2_TEXT if af2 else "NOT FIRED (A1 HELD)"))
    hit("AF2:FIRED" if af2 else "AF2:NOT_FIRED")
    # predictions ---------------------------------------------------------------------------------------------
    ok, detail = ap1_reading(P)
    out.append("  AP1  %-12s null completes at 14 g without OOM, wall 90-140 min: %s" % (verdict_word(ok), detail))
    hit("AP1:" + verdict_word(ok))
    ap2 = tribool(AP2_RANGE[0] <= share <= AP2_RANGE[1]) if a1 else None
    out.append("  AP2  %-12s certified share 8-22%% of 97: %s" % (verdict_word(ap2), "%.3f (%d/%d)" % (share, k, N_SITES) if a1 else "A1 FAILED"))
    hit("AP2:" + verdict_word(ap2))
    ap3 = tribool(a2 == "HELD") if a1 else None
    out.append("  AP3  %-12s root certifies (P 0.7): %s; at least one depth-1 certifies (P 0.6): %s; A2 HELD (P ~0.6): %s"
               % (verdict_word(ap3), verdict_word(root_c), verdict_word(d1_c), verdict_word(ap3)))
    hit("AP3:" + verdict_word(ap3))
    out.append("  AP4  %-12s share below T1's recorded 0.158 (P 0.6): %s -- recorded, DESCRIPTIVE-ONLY, never a cross-bar claim"
               % (verdict_word(below), ("below" if below else "not below") if a1 else "A1 FAILED"))
    hit("AP4:" + verdict_word(below))
    ap5 = tribool(ok2)
    out.append("  AP5  %-12s the four target strings still contain UNDETERMINED at launch (P 0.98): disjointness %s" % (verdict_word(ap5), "PASS" if ok2 else "REFUSED"))
    hit("AP5:" + verdict_word(ap5))
    # supersession pointers -----------------------------------------------------------------------------------
    if a1:
        out.append("SUPERSESSION BY INSERTION (topic_partition_outcome.txt is NOT edited; the last bracket wins; the programme's TOPIC-PARTITION-20NG outcome section receives the registrar's dated bracket):")
        out.append("  target (1) L226 superseded by A2 above: %s" % a2)
        out.append("  target (2) L238: ONLY the clause \"certified share comparison: UNDETERMINED\" is superseded, by A4 above (%s, DESCRIPTIVE-ONLY); P11's other three clauses are not restated" % verdict_word(below))
        out.append("  target (3) L120 superseded: site null %s PRESENT, %d sites at %d reps, snapshot %s (A1 HELD)" % (rel(P.csv, P.root), N_SITES, REPS, SNAPSHOT))
        out.append("  target (4) L220 NOT superseded, stays UNDETERMINED: " + POINTER_4)
        out.append("  L128 %r: not a registered target; not superseded" % NON_TARGET[1])
        hit("SUP:SUPERSEDED")
    else:
        out.append("SUPERSESSION: NOTHING SUPERSEDED (A1 FAILED); the four target strings and L128 stand as written")
        hit("SUP:NOTHING")
    out.append("WHAT THIS DOES NOT SHOW: nothing about C2 (not computed; T1b's sites never pooled); nothing about the partition (C1); nothing like-for-like against T1 or MMLU-Pro (different bars, p95 falls with n); one corpus, one embedding model, one seed, one split, no re-draw.")
    state = dict(a1=a1, a2=a2, af1=af1, af2=af2, k=k, written=False, refused=False)
    if not write:
        return out, state
    if not a1 and not record_a1_failed:
        out.append("NOT WRITTEN: A1 FAILED; --run refuses (pass --record-a1-failed only to record AF2 of record)")
        hit("WRITE:PREVIEW")
        state["refused"] = True
        return out, state
    if pre_write_hook:
        pre_write_hook()
    now = open(P.main_outcome, "rb").read() if os.path.exists(P.main_outcome) else None
    if main_bytes is not None and now != main_bytes:
        out.append("GUARD (3) SUPERSESSION BY INSERTION ONLY: REFUSED -- the outcome of record changed during the readout (sha256[:16] %s -> %s); nothing written"
                   % (sha16_bytes(main_bytes), sha16_bytes(now) if now is not None else "absent"))
        hit("G3:REFUSED")
        state["refused"] = True
        return out, state
    out.append("GUARD (3) SUPERSESSION BY INSERTION ONLY: PASS (at write) -- outcome of record unchanged, sha256[:16] %s" % (sha16_bytes(now) if now is not None else "absent"))
    with open(P.outcome, "x", encoding="utf-8", newline="\n") as fh:   # WRITE-ONCE
        fh.write("\n".join(out) + "\n")
    hit("WRITE:WRITTEN")
    state["written"] = True
    return out, state


# ------------------------------------------------------------------------------------------------ selftest
def _fixture(td, cert=None, n_rows=None, reps=None, sid=None, bar="0.0145", slice_=512, heap_first=True, oom=False,
             build="BUILD SUCCESSFUL in 1h 45m 12s", targets_ok=True, l128_ok=True, extra_row=False, db_leaf_drop=False,
             leaf_slice=None, d1_id=None, extra_site=False):
    """A synthetic arm: a heap-shaped binary tree of 97 sites / 98 leaves (root n00000001, depth-1 n00000004 / n00000005),
    its CSV, .out, snapshots.db (temp), and a 243-line outcome of record carrying the four targets and L128."""
    res = os.path.join(td, "experiment_results", "topic_partition")
    os.makedirs(os.path.join(res, ARM, "seed_42"), exist_ok=True)
    total = 2 * N_SITES + 1
    ids = [ROOT_ID, D1_IDS[0], d1_id or D1_IDS[1]] + ["n%08d" % (100 + i) for i in range(total - 3)]
    nodes = []
    for i, nid in enumerate(ids):
        kids = [ids[j] for j in (2 * i + 1, 2 * i + 2) if j < total]
        nodes.append(dict(id=nid, depth=int(math.log2(i + 1)), isLeaf=not kids, childIds=kids, sliceDim=(leaf_slice or slice_) if not kids else 0))
    if extra_site:   # one more split site: the last leaf gets two children (98 sites in the tree)
        last = nodes[-1]; last.update(isLeaf=False, childIds=["n08000001", "n08000002"])
        nodes += [dict(id=c, depth=last["depth"] + 1, isLeaf=True, childIds=[], sliceDim=slice_) for c in last["childIds"]]
    with open(os.path.join(res, ARM, "seed_42", "dag_snapshots.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(iteration=3, nodes=nodes[:3])) + "\n")   # an earlier iteration: must be ignored
        fh.write(json.dumps(dict(iteration=15, nodes=nodes)) + "\n")
    sites = [n for n in nodes if len(n["childIds"]) >= 2]
    cert = cert or {}
    rows = sites[: (n_rows if n_rows is not None else N_SITES)]
    with open(os.path.join(res, "site_null_%s.csv" % ARM), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["snapshot_id", "node_id", "label", "depth", "n", "k", "observed_sep", "site_null_p50", "site_null_p95", "cert_site_p95", "reps"])
        for j, s in enumerate(rows + ([dict(id="n09999999", depth=9)] if extra_row else [])):
            c = cert.get(s["id"], j % 9 == 0)
            n = [150, 300, 600, 1200][j % 4]
            w.writerow([sid or SNAPSHOT, s["id"], "L", s["depth"], n, 2, "0.050000" if c else "0.020000", "0.02", "0.030000",
                        "true" if c else "false", (reps if (reps and j == 5) else REPS)])
    heap = "[SITENULL-HEAP] sliceDim=512 largest site n=11845 live=24 -> peak live 7.28 GB; budget 0.90 * maxMemory(15.03 GB) = 13.53 GB"
    sep = "[SEPBAR] proposalSeparationBar=%s (-DsepBar '%s'); sliceDim=%d dropTop=0 whiten=false reps=300" % (bar, bar, slice_)
    body = ["old run", "[SEPBAR] proposalSeparationBar=0.0145 (-DsepBar '0.0145'); sliceDim=512 dropTop=0 whiten=false reps=300",
            "Caused by java.lang.OutOfMemoryError: Java heap space (an earlier run)", "BUILD FAILED in 2m 50s"]
    hdr = "SITE-LEVEL + DEFLATED WITHIN-NODE NULLS \x97 FROZEN ARTIFACT.  snapshot=%s  minClusterSize=55  bar=%s" % (SNAPSHOT, bar)
    body += ([heap, hdr, sep] if heap_first else [hdr, sep, heap]) + ["site table ..."] + (["java.lang.OutOfMemoryError: Java heap space"] if oom else []) + ([build] if build else [])
    with open(os.path.join(res, "sitenull_%s.out" % ARM), "wb") as fh:   # CRLF and a cp1252 byte, as a Windows console writes them
        fh.write(("\r\n".join(body) + "\r\n").encode("latin-1"))
    lines = ["line %d" % (i + 1) for i in range(243)]
    lines[13] = "  certified share (...): T1 line of record"
    for _, ln, s in TARGETS:
        lines[ln - 1] = s
    lines[NON_TARGET[0] - 1] = NON_TARGET[1]
    if not targets_ok:
        lines[225] = lines[225].replace("UNDETERMINED --", "HELD --")
    if not l128_ok:
        lines[127] = "  site null: PRESENT"
    with open(os.path.join(res, "topic_partition_outcome.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    db = os.path.join(td, "snapshots.db")
    if os.path.exists(db):
        os.remove(db)
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE snapshots (id TEXT PRIMARY KEY, graph TEXT)")
    gnodes = [dict(id=n["id"], childIds=n["childIds"]) for n in nodes]
    if db_leaf_drop:
        gnodes = [g for g in gnodes if g["id"] != ids[-1]]
    con.execute("INSERT INTO snapshots VALUES (?, ?)", (SNAPSHOT, json.dumps(dict(rootId=ROOT_ID, nodes=gnodes))))
    con.commit(); con.close()
    return Paths(root=td)


def selftest():
    checks = 0
    real_connect = sqlite3.connect
    tmp_roots = []

    def guarded_connect(target, *a, **k):   # no real DB: every connect must point inside a mkdtemp() fixture
        t = str(target).replace("file:", "").split("?")[0].replace("/", os.sep)
        assert any(os.path.abspath(t).startswith(os.path.abspath(r)) for r in tmp_roots), "selftest opened a non-fixture DB: %s" % target
        return real_connect(target, *a, **k)
    sqlite3.connect = guarded_connect
    BRANCHES.clear()
    try:
        def fresh(**kw):
            td = tempfile.mkdtemp(prefix="t1b_null_selftest_")
            tmp_roots.append(td)
            return _fixture(td, **kw)

        def run(P, **kw):
            out, st = readout(P, **kw)
            return "\n".join(out), st

        # 1 the good draw: A1 HELD, A2 HELD, AF1 / AF2 NOT FIRED, 11 of 97 certified (the j % 9 == 0 rows)
        cert = {ROOT_ID: True, D1_IDS[0]: False, D1_IDS[1]: True}
        P = fresh(cert=cert)
        main_before = open(P.main_outcome, "rb").read()
        txt, st = run(P, write=True)
        assert st["written"] and st["a1"] is True and st["a2"] == "HELD"; checks += 1
        assert "GUARD (1) PROVENANCE PIN: PASS" in txt and "GUARD (2) DISJOINTNESS: PASS" in txt and "GUARD (3) SUPERSESSION BY INSERTION ONLY: PASS (pre-write)" in txt; checks += 1
        assert "GUARD (3) SUPERSESSION BY INSERTION ONLY: PASS (at write)" in txt; checks += 1
        assert open(P.main_outcome, "rb").read() == main_before; checks += 1
        written = open(P.outcome, encoding="utf-8").read()
        assert written == txt + "\n"; checks += 1
        k = st["k"]
        assert "A3 (DESCRIPTIVE-ONLY; recorded): T1b certified share (cert_site_p95, 300 reps, bar 0.0145) %d of 97" % k in txt; checks += 1
        assert "n<200 " in txt and ">=800 " in txt and "NOMINAL" in txt; checks += 1
        assert "A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): HELD" in txt and ": below at the point" in txt; checks += 1
        assert "AF1 (fires iff A2 = PARTIAL, ruling (2)): NOT FIRED (A2 HELD)" in txt and "AF2 (fires iff A1 FAILED, ruling (2)): NOT FIRED" in txt; checks += 1
        assert "  AP1  HELD" in txt and "105.2 min" in txt; checks += 1
        assert "  AP2  HELD" in txt and "  AP3  HELD" in txt and "  AP4  HELD" in txt and "  AP5  HELD" in txt; checks += 1
        assert POINTER_4 in txt and "target (4) L220 NOT superseded, stays UNDETERMINED" in txt; checks += 1
        assert "not a registered target; not superseded" in txt; checks += 1
        assert "margin" in txt and "A2 row root n00000001" in txt and "A2 row depth-1 n00000005" in txt; checks += 1
        # the C2 exclusion and the T1-count ban, on the written file (ruling (3) / (4))
        low = written.lower()
        assert not any(w in low for w in ("stratified", "permutation", "ols ", "nmi_", "hc1")); checks += 1
        assert not any(w in written for w in ("16/101", "of 101", "16 of", "/85", "85 uncertified", "16 certified")); checks += 1
        assert "0.158" in written and "quoted, not recomputed" in written; checks += 1
        # write-once: a second --run refuses and leaves the file byte-identical
        txt2, st2 = run(P, write=True)
        assert st2["refused"] and not st2["written"] and "EXISTS (write-once" in txt2; checks += 1
        assert open(P.outcome, encoding="utf-8").read() == written; checks += 1
        # 2 PARTIAL on the root clause: AF1 FIRES; A4 not below (share above 0.158); AP2 FAILED; AP3 FAILED; AP4 FAILED
        many = {s: True for s in ["n%08d" % (100 + i) for i in range(40)]}
        many.update({ROOT_ID: False, D1_IDS[0]: True, D1_IDS[1]: False})
        txt, st = run(fresh(cert=many))
        assert st["a2"] == "PARTIAL" and st["af1"] is True and "AF1 (fires iff A2 = PARTIAL, ruling (2)): FIRED -- " + AF1_TEXT in txt; checks += 1
        assert "root certified FAILED; at least one depth-1 site certified HELD" in txt; checks += 1
        assert "A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): FAILED" in txt and ": not below at the point" in txt; checks += 1
        assert "  AP2  FAILED" in txt and "  AP3  FAILED" in txt and "  AP4  FAILED" in txt; checks += 1
        assert "target (1) L226 superseded by A2 above: PARTIAL" in txt; checks += 1
        # 2b A4's point at the quoted 0.158, on both sides of it: 15 of 97 = 0.155 below, 17 of 97 = 0.175 not below
        site_ids = [ROOT_ID, D1_IDS[0], D1_IDS[1]] + ["n%08d" % (100 + i) for i in range(N_SITES - 3)]
        for kk, word, side in ((15, "HELD", "below"), (17, "FAILED", "not below")):
            exact = {s: (i < kk) for i, s in enumerate(site_ids)}
            txt, st = run(fresh(cert=exact))
            assert st["k"] == kk and "A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): %s" % word in txt and ": %s at the point" % side in txt and "  AP2  HELD" in txt; checks += 1
        # 2c AP2's LOWER bound: 5 of 97 = 0.052 is below 8% -> AP2 FAILED (A4 below, HELD)
        txt, st = run(fresh(cert={s: (i < 5) for i, s in enumerate(site_ids)}))
        assert st["k"] == 5 and "  AP2  FAILED" in txt and "A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): HELD" in txt; checks += 1
        # 3 PARTIAL on the depth-1 clause
        txt, st = run(fresh(cert={ROOT_ID: True, D1_IDS[0]: False, D1_IDS[1]: False}))
        assert st["a2"] == "PARTIAL" and "root certified HELD; at least one depth-1 site certified FAILED" in txt; checks += 1
        # 4 A1 FAILED: CSV absent -> everything UNDETERMINED, AF2 FIRES, nothing superseded, --run writes nothing
        P = fresh(); os.remove(P.csv)
        txt, st = run(P, write=True)
        assert st["a1"] is False and st["a2"] == "UNDETERMINED" and not st["written"] and not os.path.exists(P.outcome); checks += 1
        assert "A1 GATE (SCOREABLE, deterministic): FAILED -- CSV ABSENT" in txt and "GUARD (1) PROVENANCE PIN: REFUSED" in txt; checks += 1
        assert "A2 (C3-beside for T1b; SCOREABLE): UNDETERMINED" in txt and "A3 (DESCRIPTIVE-ONLY): UNDETERMINED" in txt and "A4 (P11's certified-share clause; DESCRIPTIVE-ONLY): UNDETERMINED" in txt; checks += 1
        assert "AF2 (fires iff A1 FAILED, ruling (2)): FIRED -- " + AF2_TEXT in txt and "AF1 (fires iff A2 = PARTIAL, ruling (2)): NOT FIRED (A2 UNDETERMINED)" in txt; checks += 1
        assert "  AP2  UNDETERMINED" in txt and "  AP3  UNDETERMINED" in txt and "  AP4  UNDETERMINED" in txt; checks += 1
        assert "SUPERSESSION: NOTHING SUPERSEDED" in txt and "NOT WRITTEN: A1 FAILED" in txt; checks += 1
        # ... and with --record-a1-failed the AF2 outcome is written, once
        txt, st = run(P, write=True, record_a1_failed=True)
        assert st["written"] and "AF2 (fires iff A1 FAILED, ruling (2)): FIRED" in open(P.outcome, encoding="utf-8").read(); checks += 1
        # 5 guard clause (1), refusal branch by branch (each prints its reason and the values)
        for kw, needle in ((dict(bar="0.025"), "[SEPBAR] bar 0.025 != 0.0145"),
                           (dict(slice_=256), "[SEPBAR] sliceDim 256 != 512"),
                           (dict(heap_first=False), "precedes the last [SITENULL-HEAP] line"),
                           (dict(n_rows=96), "CSV carries 96 site rows, not 97"),
                           (dict(reps=24), "not 300 on every row (partial null)"),
                           (dict(sid="20260922_195728_Headless_Run_Auto_ge"), "the arm's own, never T1's"),
                           (dict(extra_row=True), "CSV carries 98 site rows"),
                           (dict(db_leaf_drop=True), "!= snapshots.db's snapshot"),
                           (dict(extra_site=True), "dag_snapshots.jsonl (last line) yields 98 sites, not 97"),
                           (dict(leaf_slice=256), "jsonl leaves carry sliceDim [256], not [512]"),
                           (dict(d1_id="n00000006"), "A2 denominator: root ['n00000001'] / depth-1 sites ['n00000004', 'n00000006']")):
            txt, st = run(fresh(**kw))
            assert st["a1"] is False and "GUARD (1) PROVENANCE PIN: REFUSED -- " in txt and needle in txt and "values: {" in txt, (kw, txt[:3000]); checks += 1
        P = fresh(); rows = open(P.csv, encoding="utf-8").read().splitlines()
        open(P.csv, "w", encoding="utf-8").write("\n".join(rows[:-1] + [rows[-1].replace(rows[-1].split(",")[1], '"n09999999"')]) + "\n")
        txt, st = run(P)
        assert st["a1"] is False and "orphans: CSV rows for non-sites" in txt; checks += 1
        P = fresh(); rows = open(P.csv, encoding="utf-8").read().splitlines()
        open(P.csv, "w", encoding="utf-8").write("\n".join(rows[:-1] + [rows[1]]) + "\n")   # 97 rows, one node twice
        txt, st = run(P)
        assert st["a1"] is False and "CSV node_ids occur more than once: ['n00000001']" in txt; checks += 1
        P = fresh(); os.remove(P.out)
        txt, st = run(P)
        assert "sitenull_ng_af_bareq512_s42.out absent" in txt and "  AP1  UNDETERMINED" in txt; checks += 1
        # 6 guard clause (2): a changed target, a moved target, a changed L128, the file absent -> REFUSED, AP5 FAILED, A1 FAILED
        txt, st = run(fresh(targets_ok=False))
        assert st["a1"] is False and "GUARD (2) DISJOINTNESS: REFUSED -- target (1) at L226" in txt and "  AP5  FAILED" in txt; checks += 1
        txt, st = run(fresh(l128_ok=False))
        assert "GUARD (2) DISJOINTNESS: REFUSED -- L128 changed" in txt; checks += 1
        P = fresh(); ls = open(P.main_outcome, encoding="utf-8").read().split("\n"); ls.insert(0, "inserted")
        open(P.main_outcome, "w", encoding="utf-8", newline="\n").write("\n".join(ls))
        txt, st = run(P)
        assert "GUARD (2) DISJOINTNESS: REFUSED -- target (1) at L226: pinned-line equal False, occurrences 1" in txt; checks += 1
        P = fresh(); ls = open(P.main_outcome, encoding="utf-8").read().split("\n"); ls[10] = TARGETS[3][2]
        open(P.main_outcome, "w", encoding="utf-8", newline="\n").write("\n".join(ls))
        txt, st = run(P)
        assert "target (4) at L220: pinned-line equal True, occurrences 2" in txt; checks += 1
        P = fresh(); os.remove(P.main_outcome)
        txt, st = run(P)
        assert "GUARD (2) DISJOINTNESS: REFUSED -- experiment_results/topic_partition/topic_partition_outcome.txt absent" in txt; checks += 1
        # 7 guard clause (3): a protected outcome path; the outcome of record changed before the write
        P = fresh(); P.outcome = P.main_outcome
        txt, st = run(P, write=True)
        assert st["refused"] and "is a file the addendum may never touch" in txt and open(P.main_outcome, "rb").read().count(b"\n") == 243; checks += 1
        P = fresh(cert=cert)
        txt, st = run(P, write=True, pre_write_hook=lambda: open(P.main_outcome, "a", encoding="utf-8").write("tamper\n"))
        assert st["refused"] and not os.path.exists(P.outcome) and "changed during the readout" in txt; checks += 1
        # 8 AP1: OOM in the run segment -> FAILED; out of the wall range -> FAILED; no BUILD line -> UNDETERMINED; an
        #   earlier run's OOM (before the last heap line) is NOT read
        txt, _ = run(fresh(cert=cert, oom=True))
        assert "  AP1  FAILED" in txt and "OutOfMemoryError True" in txt; checks += 1
        txt, _ = run(fresh(cert=cert, build="BUILD SUCCESSFUL in 2h 31m 4s"))
        assert "  AP1  FAILED" in txt and "151.1 min" in txt; checks += 1
        txt, _ = run(fresh(cert=cert, build="BUILD SUCCESSFUL in 58m 30s"))
        assert "  AP1  FAILED" in txt and "58.5 min" in txt; checks += 1
        txt, _ = run(fresh(cert=cert, build=None))
        assert "  AP1  UNDETERMINED" in txt and "no gradle BUILD line" in txt; checks += 1
        txt, _ = run(fresh(cert=cert))
        assert "OutOfMemoryError False" in txt; checks += 1
        # 9 the dry run writes nothing
        P = fresh(cert=cert)
        txt, st = run(P, write=False)
        assert not st["written"] and not os.path.exists(P.outcome); checks += 1
        # 10 tribool / verdict routing on numpy values (the D1 class): a numpy bool must score, never drop a line
        import numpy as np
        assert a2_word(True, [np.True_, np.True_, np.bool_(True)]) == "HELD"; checks += 1
        assert a2_word(True, [np.True_, np.False_, np.True_]) == "PARTIAL"; checks += 1
        assert a2_word(False, []) == "UNDETERMINED"; checks += 1
        assert verdict_word(np.float64(0.12) < T1_RECORDED_SHARE) == "HELD" and verdict_word(np.float64(0.2) < T1_RECORDED_SHARE) == "FAILED"; checks += 1
        try:
            tribool("HELD"); raise AssertionError("tribool accepted a string")
        except SystemExit:
            pass
        checks += 1
        # 11 the cert flag parse is fail-closed
        try:
            flag("yes"); raise AssertionError("flag accepted 'yes'")
        except Refusal:
            pass
        checks += 1
        # 12 the pinned strings of record
        assert [t[1] for t in TARGETS] == [226, 238, 120, 220] and all("UNDETERMINED" in t[2] for t in TARGETS); checks += 1
        assert NON_TARGET == (128, "  site null: ABSENT (certified share UNDETERMINED)"); checks += 1
        assert (ARM, SNAPSHOT, BAR, SLICE, REPS, N_SITES, ROOT_ID, D1_IDS) == ("ng_af_bareq512_s42", "20260923_043423_Headless_Run_Auto_ge", 0.0145, 512, 300, 97, "n00000001", ("n00000004", "n00000005")); checks += 1
        assert T1_RECORDED_SHARE == 0.158 and MAIN_OUTCOME_BLOB == "90632b36bed00d3d39a24dca27f4d428411e5a2a"; checks += 1
        # 13 the imports: only tribool / verdict_word / wilson are bound from the two modules
        src = open(os.path.abspath(__file__), encoding="utf-8").read()
        imports = [l for l in src.splitlines() if l.startswith(("import ", "from "))]
        assert "from topic_partition import tribool, verdict_word   # noqa: E402  the ONLY names used from the main readout" in imports; checks += 1
        assert sum(1 for l in imports if "topic_partition" in l) == 1 and sum(1 for l in imports if "t3_routing_inflation" in l) == 1; checks += 1
        assert 'open(P.outcome, "x"' in src and ', "w"' not in src.split("def _fixture")[0]; checks += 1
        # 14 every registered print branch was EXECUTED above
        missing = sorted(REQUIRED_BRANCHES - BRANCHES)
        assert not missing, "branches never executed: %s" % missing; checks += 1
        assert BRANCHES == REQUIRED_BRANCHES; checks += 1
        # 15 the fixture's snapshots.db was the only DB opened, inside mkdtemp()
        assert all(r.startswith(tempfile.gettempdir()) for r in tmp_roots); checks += 1
    finally:
        sqlite3.connect = real_connect
    if checks != SELFTEST_CHECKS:
        raise SystemExit("[T1B-NULL] SELFTEST count %d != pinned SELFTEST_CHECKS %d" % (checks, SELFTEST_CHECKS))
    shas = script_shas()
    print("[T1B-NULL] SELFTEST OK: %d checks (pinned %d); %d of %d registered print branches executed; script sha256[:16] LF %s / CRLF %s"
          % (checks, SELFTEST_CHECKS, len(BRANCHES), len(REQUIRED_BRANCHES), shas["lf"], shas["crlf"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--record-a1-failed", action="store_true", help="with --run: write the A1-FAILED / AF2 outcome of record")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if a.record_a1_failed and not a.run:
        die("--record-a1-failed needs --run")
    P = Paths(root=os.path.abspath(a.root))
    print("[T1B-NULL] pool %s: the corpus's own split (no arena pool read or written); %s; root %s"
          % (POOL, "RUN" if a.run else "DRY RUN (writes nothing)", P.root))
    out, st = readout(P, record_a1_failed=a.record_a1_failed, write=a.run)
    print("\n".join(out))
    if st["written"]:
        after = open(P.main_outcome, "rb").read() if os.path.exists(P.main_outcome) else b""
        print("[T1B-NULL] written %s (write-once); outcome of record sha256[:16] after the write %s" % (rel(P.outcome, P.root), sha16_bytes(after)))
        return 0
    return 2 if (st["refused"] or (a.run and not st["written"])) else 0


if __name__ == "__main__":
    sys.exit(main())
