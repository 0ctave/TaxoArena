"""MIX-LRT-SITE (docs/judge_v2_program.md L20595-L20670, "## Registered 2026-09-26 (before any code or call) - MIX-LRT-SITE",
registered at 31d092e before any code). ZERO calls: no judge, no LLM, no embedding call, no cap, no temperature, no call cache.

Question (verbatim in the programme): does a full-covariance 1-vs-2 Gaussian likelihood ratio in site-local PCA-10, calibrated
against the SAME site null (withinNodeCloud; B = 199 draws per site), separate the frozen tree's CS contamination split n00000013
from Philosophy (n00000014, n00000055), and which sites of af_clean_s42, o0_clean_s42 and af_bareq512_s42 does it certify?

Launch sequence (the run-operator; every step zero calls; ONE python process at a time; outside any construction or W-window):
  python tools/analysis/mix_lrt_site.py --selftest     # synthetic only (ST1-ST7 + the unit checks); green before the READY
  python tools/analysis/mix_lrt_site.py --mutants      # every check removed in turn; every mutant must be KILLED
  python tools/analysis/mix_lrt_site.py --power-probe  # SYNTHETIC, descriptive: ST2's certified count at 4 / 6 / 8 within-SD
                                                       # (ST2 runs at 8: at the registered floor of 4 the fixture has ~no power)
  python tools/analysis/mix_lrt_site.py --dry-run      # pool id first; trees, sites, n, B plan, pins, cost; NO statistic
  python tools/analysis/mix_lrt_site.py --route-sweep  # generator + pca_basis on EVERY registered draw; counts only, no LR
  python tools/analysis/mix_lrt_site.py --run          # resumable chunks (<= 4 wall-min each) under experiment_results/mix_lrt_site/state/
  python tools/analysis/mix_lrt_site.py --analyze      # REFUSES unless every registered (site, draw) cell is present exactly once;
                                                       # writes the outcome of record WRITE-ONCE (open mode 'x')
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree (the DBs are not in a worktree).

What the script does (the registration's words in brackets):
  SITES      the rows of each tree's site-null CSV (pinned; blob / sha256-lf16 verified on load, REFUSE on mismatch).
  MEMBERS    regionQueryIds(site) over the snapshot graph exactly as SeparationNullBySizeTest.kt L510-L524 (DFS over childIds,
             union of every visited node's queryIds, insertion-ordered), the graph loaded read-only as loadFrozenGraph
             (L1326-L1342) does: snapshots_frozen.db first, then snapshots.db; |members| == the CSV's n for EVERY site, else REFUSE.
  VECTORS    embeddings_cache.db, "SELECT q.id, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text"
             (loadVectorsById, L1580-L1604), big-endian float32, first sliceDim values (256; 512 for af_bareq512_s42),
             L2-normalised; dropTop 0, whiten false (canonicalConfig L96-L118 defaults); a missing vector REFUSES.
             Rows sorted by (distilled_text, id).
  STATISTIC  centre, principal axes from np.linalg.eigh of the d x d scatter matrix Xc^T Xc, eigenvalues descending (the
             orchestrator's ruling after the b617888 crash of np.linalg.svd on a rank-deficient scatter; the same subspace as
             the thin SVD of Xc, kept as pca_basis_thin; ST-PCA / ST-REG / --route-sweep verify it), top p axes; k = 1 closed-form MLE; k = 2 sklearn GaussianMixture(covariance_type 'full', n_init 5,
             init_params 'kmeans', max_iter 500, tol 1e-4, reg_covar 1e-6, random_state from the site's stream);
             LR = 2 (l2 - l1); dBIC = BIC(1) - BIC(2); dICL with ICL = BIC + 2 x entropy(responsibilities).
  NULL       withinNodeCloud (SeparationNullBySizeTest.kt L558-L577, blob:0b6e176f): out = mu + sum_c g_c c / sqrt(m),
             g_c iid N(0, 1), unit-normalised; then the DRAW's own centring, PCA-p and the same two fits.
             RULING A6 (programme L20864-L20919): the null draws use within_node_cloud_eigen, mu + Z diag(s) V^T / sqrt(m) with
             C = U diag(s) V^T the thin SVD of the site's centred members (computed once per site), Z iid N(0, 1), then
             unit-normalised: EXACT IN DISTRIBUTION with the literal form (same N(mu, C^T C / m) before normalisation), not draw
             for draw. --selftest ST-EQ tests it: (i) moments of both forms on the JVM F2 fixture, (ii) a two-sample KS test on
             the p = 10 LR null (199 + 199 draws, independent streams; bar p >= 0.01, fixed in the code before its first run).
             The literal forms are KEPT as the reference: within_node_cloud (m Gaussians per output row, consumed row-major as
             the Kotlin loop consumes them) and within_node_cloud_loop. Their equivalence is PROVEN by --selftest ST-JVM: the
             COMPILED Kotlin method (build/classes/kotlin/test/taxonomy/SeparationNullBySizeTest.class, sha256
             dfa5a30e7529cd1b..., compiled 2026-09-25 20:43 from the unmodified blob 0b6e176f) was invoked by reflection on two
             fixtures with java.util.Random seeds (generator: tools/analysis/mix_lrt_site_fixture/WithinNodeCloudFixture.java);
             its outputs are embedded below (JVM_FIXTURE) and the Python literal transcription, driven by a Python clone of
             java.util.Random, must reproduce them; the vectorised production form fed the same Gaussians must agree to 1e-12.
  q          q_LR = (1 + #{b : LR_b >= LR_obs}) / (B + 1), exact Fractions; CERTIFIED iff q_LR <= 0.05.
  FAILED FITS (ruling A3; a failure = an exception or a non-finite log-likelihood; a non-converged EM is NOT a failure):
             a failed p = 10 null draw is excluded and counted (f): q = (1 + c) / (B - f + 1); f >= 2 at B = 199 (more than 1%)
             or a failed observed fit makes the site VOID (excluded from D1-D7, denominators printed net of VOID); at a
             DECIDING site ANY failed p = 10 fit, observed or null, VOIDs C1 (a failed precondition: --analyze then writes
             mix_lrt_site_VOID.txt, never the outcome); a failure in a p = 5 / p = 20 leg VOIDs that leg's q at that site only;
             a failed leaf fit is excluded from its site's leaf median and counted (all failed -> D5 NA).
  R-a        ruling A4: decided PER TREE ("on every tree" scopes both clauses); the pooled-superset reading is printed beside it,
             marked "not of record".
  ESCALATION a DECIDING site (frozen n00000013, n00000014, n00000055) with q_LR at B = 199 in [0.02, 0.10] (inclusive) gets
             draws 199..998 of its SAME stream (B = 999); no other site is escalated.
  p = 5, 20  descriptive only, on draws 0..48 of each site's stream (B = 49); flagged OVERPARAM when n < 2 k1 + 1 parameters.
  SECONDARY  gain = (l2 - l1) / n at the site (p = 10) minus the median gain over its descendant LEAVES with n >= 110, each leaf in
             its own PCA-10; NA when no such leaf.
  SEEDS      rulings A1, A2, A7: numpy SeedSequence(20260926, spawn_key=(tree_index, row)) per site, tree_index 0..3 in the
             registered TREES order (frozen, af_clean_s42, o0_clean_s42, af_bareq512_s42), row = the 0-based data-row index of
             the site in its CSV; draw b uses the b-th spawned child SeedSequence(20260926, spawn_key=(tree_index, row, b)); in a
             draw, the Gaussians are drawn first, then three sklearn random_states (p10, p5, p20, in that order); the observed
             fit's random_states come from the site's own SeedSequence; a leaf's (secondary statistic) from
             SeedSequence(20260926, spawn_key=(tree_index, 1000000 + <leaf number>)).
  POWER      ruling A5: ST2 runs at 8 within-SD (the registered ">= 4"); the synthetic power curve 0 / 20 at 4, 14 / 20 at 6,
             20 / 20 at 8 (--power-probe) is printed beside any FAILED-NO-POWER reading.
  COST GUARD the first chunk of each tree is one draw (b = 0) at every site with all three legs; from those four chunks the total
             is projected (p10 legs x 199 draws + the maximal escalation 3 x 800 + p5/p20 legs x 49) and printed WITH the
             budget (80 CPU-min) on every --run, pass or fail; above the budget the p = 5 / p = 20 legs are DROPPED (written
             once to state/plan.json); the p = 10 leg is never dropped.
  GAPS       MIX-FLAT-SELFTEST-GAPS (2026-09-27, engineering, zero calls; a new blob, never a re-run of record): READY dde660e D3
             (cost_lines prints the post-drop projection p10 + escalation + observed against the cap; measured_cpu /
             measured_cost_line print the MEASURED CPU at the end of --run and in the outcome's info lines, as post-run review
             8032197 D3 asked), D4 (ST-EQ (iii): literal(G) == eigen(G U) draw for draw on four fixtures), D6 (run()'s
             escalation decision factored into escalation_tasks, behaviour unchanged, executed by ST-ESC; mutants R4c / R4d),
             D7 (ST-PCA checks that the printed sine is the projector distance); delta READY e8a9eed D1 (route_cell_check: a
             thin-SVD spot check every 50th draw and the minimum relative eigen-gap printed by --route-sweep; ST-ROUTE) and D4
             (ST-REG's "the old route raises" is a printed NOTE with the environment line, no longer a check).
  PINS       per-table sha256 (repr(row) + LF, ordered by the primary key; the data-steward's convention) of
             embeddings_cache.db tables embeddings and queries, and sha256 of each snapshot row read, BEFORE and AFTER every
             --run; any change REFUSES. Every DB is opened via pool_guard.open_ro (non-empty -wal / -journal REFUSED, then
             mode=ro&immutable=1); a process-wide connect guard refuses any other open. Nothing is written to any DB.
  POOL       p2dca21ab5f4ef3ae is printed FIRST, "printed, not used": its id FILE is hashed by pool_guard.compute_pool_id; the
             dataset DB is NOT opened (the registration: "The script reads no DB other than embeddings_cache.db and the snapshot
             stores").
Outputs: experiment_results/mix_lrt_site/state/*.json (chunks, meta.json, plan.json; write-once each);
         experiment_results/mix_lrt_site/mix_lrt_site_outcome.txt and mix_lrt_site_sites.csv (--analyze only, write-once).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported (the author's cap: single-threaded)
    os.environ[_v] = "1"

import sys
import csv
import json
import math
import time
import hashlib
import sqlite3
import argparse
import tempfile; import scratch_dir  # TEMP-SPRAWL: temp on E:, removed at exit
import warnings
import datetime
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

DATA_ROOT = pool_guard.DATA_ROOT
POOL_ID = "p2dca21ab5f4ef3ae"
TAG = "[MIX-LRT]"

# ------------------------------------------------------------------------------------------------ registered constants
ROOT_ENTROPY = 20260926
B_MAIN = 199
B_ESC = 999
B_DESC = 49
LEGS_ALL = ("10", "5", "20")
LEG_STATE_INDEX = {"10": 0, "5": 1, "20": 2}
CERT_Q = Fraction(1, 20)
ESC_LO, ESC_HI = Fraction(1, 50), Fraction(1, 10)
DECIDING_TREE = "frozen"
DECIDING = ("n00000013", "n00000014", "n00000055")
GMM_KW = dict(n_components=2, covariance_type="full", n_init=5, init_params="kmeans", max_iter=500, tol=1e-4, reg_covar=1e-6)
LEAF_MIN_N = 110
LEAF_SPAWN_BASE = 1000000
CAP_CPU_MIN = 80.0
CHUNK_WALL_S = 240.0
P8_CPU_MIN = 60.0

TREES = (
    dict(name="frozen", csv="docs/data/site_null_frozen.csv",
         blob="1577e9e4073d286425a8a04ff1b83359fce8e172", lf16="09c41b45ef5d0596", crlf16="71965a361d7954fa",
         snapshot="20260727_042523_Headless_Run_Auto_ge", dim=256, sites=66, j_cert=6),
    dict(name="af_clean_s42", csv="experiment_results/anchorfree/redraw/site_null_af_clean_s42.csv",
         blob="8ed1b699d692af1d4f1d573127196248598079dd", lf16="e15302b76a1aba3a", crlf16="a21f1836900cb8bc",
         snapshot="20260917_201353_Headless_Run_Auto_ge", dim=256, sites=69, j_cert=14),
    dict(name="o0_clean_s42", csv="experiment_results/anchorfree/redraw/site_null_o0_clean_s42.csv",
         blob="f69179a0ca375ea59c785d52a9db9e040c3b85ca", lf16="f44c4dbff0d8e360", crlf16="58d79630d11bc689",
         snapshot="20260918_040207_Headless_Run_Auto_ge", dim=256, sites=60, j_cert=11),
    dict(name="af_bareq512_s42", csv="experiment_results/anchorfree/site_null_af_bareq512_s42.csv",
         blob="f6875fc111f10f892285e2aec53da5cf17cc8c56", lf16="ae24c73beb3b7a82", crlf16="751065a0aa534378",
         snapshot="20260917_161817_Headless_Run_Auto_ge", dim=512, sites=87, j_cert=10),
)
TREE_BY_NAME = {t["name"]: t for t in TREES}
TREE_INDEX = {t["name"]: i for i, t in enumerate(TREES)}   # ruling A1: the registered order
SNAP_STORES = ("snapshots_frozen.db", "snapshots.db")          # loadFrozenGraph's order
EMB_DB_NAME = "embeddings_cache.db"
PIN_TABLES = ((EMB_DB_NAME, "embeddings", "query"), (EMB_DB_NAME, "queries", "id"))
OUT_DIR = os.path.join(ROOT, "experiment_results", "mix_lrt_site")
STATE_DIR = os.path.join(OUT_DIR, "state")
OUTCOME = os.path.join(OUT_DIR, "mix_lrt_site_outcome.txt")
SITES_CSV = os.path.join(OUT_DIR, "mix_lrt_site_sites.csv")

# P4 intervals (registration PREDICTIONS) and the J shares of D3
P4 = {"frozen": (40, 20, 60), "af_clean_s42": (45, 20, 63), "o0_clean_s42": (38, 18, 55), "af_bareq512_s42": (55, 25, 80)}


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ------------------------------------------------------------------------------------------------ connect guard
_RAW_CONNECT = getattr(sqlite3.connect, "_raw", sqlite3.connect)
ALLOWED_DB_BASENAMES = (EMB_DB_NAME,) + SNAP_STORES


def _guarded_connect(database, *a, **k):
    """Process-wide: only file: URIs with mode=ro AND immutable=1 on the three DBs this test reads are admitted."""
    s = str(database)
    if not (k.get("uri") and s.startswith("file:")):
        refuse("sqlite3.connect(%r) is not a file: URI opened with uri=True" % s)
    path, _, query = s[5:].partition("?")
    params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
    if params.get("mode") != "ro" or params.get("immutable") != "1":
        refuse("sqlite3.connect(%r): only mode=ro&immutable=1 is admitted" % s)
    if os.path.basename(path) not in ALLOWED_DB_BASENAMES:
        refuse("sqlite3.connect(%r): %s is not a DB this test reads" % (s, os.path.basename(path)))
    return _RAW_CONNECT(database, *a, **k)


_guarded_connect._raw = _RAW_CONNECT
sqlite3.connect = _guarded_connect


# ------------------------------------------------------------------------------------------------ pins
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


def fmt_pins(p):
    return "blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (p["blob"][:8], p["lf16"], p["crlf16"])


def verify_pin(path, blob, lf16):
    got = pins_of(path)
    if got["blob"] != blob or got["lf16"] != lf16:
        refuse("pin mismatch on %s: got %s, registered blob:%s / sha256-lf16:%s" % (path, fmt_pins(got), blob[:8], lf16))
    return got


def script_pins():
    return pins_of(os.path.abspath(__file__))


# ------------------------------------------------------------------------------------------------ inputs
def load_csv(tree):
    path = os.path.join(ROOT, tree["csv"])
    pins = verify_pin(path, tree["blob"], tree["lf16"])
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != tree["sites"]:
        refuse("%s has %d rows, registered %d" % (tree["csv"], len(rows), tree["sites"]))
    sids = {r["snapshot_id"] for r in rows}
    if sids != {tree["snapshot"]}:
        refuse("%s carries snapshot ids %s, registered %s" % (tree["csv"], sorted(sids), tree["snapshot"]))
    jc = sum(1 for r in rows if r["cert_site_p95"].strip().lower() == "true")
    if jc != tree["j_cert"]:
        refuse("%s: %d cert_site_p95 rows, registered %d" % (tree["csv"], jc, tree["j_cert"]))
    bad = [r["node_id"] for r in rows if r["feasibility"] != "OK"]
    if bad:
        refuse("%s: feasibility not OK at %s" % (tree["csv"], bad))
    return rows, pins


def load_graph(snapshot_id):
    for name in SNAP_STORES:
        p = os.path.join(DATA_ROOT, name)
        if not os.path.exists(p):
            continue
        con = pool_guard.open_ro(p)
        try:
            row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
        finally:
            con.close()
        if row is not None:
            g = json.loads(row[0])
            return dict(store=name, sha=hashlib.sha256(row[0].encode("utf-8")).hexdigest(),
                        byid={n["id"]: n for n in g["nodes"]}, root=g.get("rootId"))
    refuse("snapshot %s is in none of %s under %s" % (snapshot_id, SNAP_STORES, DATA_ROOT))


def region_query_ids(root_id, byid):
    """SeparationNullBySizeTest.regionQueryIds: LIFO stack over childIds, seen-set, insertion-ordered union of queryIds."""
    ids = {}
    stack = [root_id]
    seen = set()
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


def descendant_leaves(root_id, byid):
    out, stack, seen = [], [root_id], set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        kids = [c for c in (byid[cur].get("childIds") or []) if c in byid]
        if not kids:
            out.append(cur)
        stack.extend(kids)
    return sorted(out)


def load_vectors(ids, dim):
    """loadVectorsById's SQL plus distilled_text (for the sort): id -> (text, unit slice vector)."""
    con = pool_guard.open_ro(os.path.join(DATA_ROOT, EMB_DB_NAME))
    out = {}
    try:
        ids = list(ids)
        for s in range(0, len(ids), 400):
            chunk = ids[s:s + 400]
            sql = ("SELECT q.id, q.distilled_text, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text "
                   "WHERE q.id IN (%s)" % ",".join("?" * len(chunk)))
            for qid, text, blob in con.execute(sql, chunk):
                if blob is None or len(blob) // 4 < dim:
                    continue
                v = np.frombuffer(blob, dtype=">f4")[:dim].astype(np.float64)
                nrm = math.sqrt(float(v @ v))
                if nrm > 0:
                    out[qid] = (text, v / nrm)
    finally:
        con.close()
    return out


class SiteCtx(object):
    def __init__(self, tree, row, node_id, label, depth, n_csv, k, cert_j, q_defl, X, texts_ids, tree_index=None):
        if tree_index is None:
            refuse("SiteCtx needs its tree_index (ruling A1: the stream is keyed by (tree_index, row))")
        self.tree, self.row, self.node_id, self.label, self.depth = tree, row, node_id, label, depth
        self.tree_index = int(tree_index)
        self.n_csv, self.k, self.cert_j, self.q_defl = n_csv, k, cert_j, q_defl
        self.X = X
        self.n = X.shape[0]
        self.mu = X.mean(axis=0)
        self.C = X - self.mu
        _, self.s, self.Vt = np.linalg.svd(self.C, full_matrices=False)   # thin SVD, once per site (ruling A6)
        self.order = texts_ids


def prepare_members(ids, vecmap, n_expected, where):
    """|members| == the CSV's n, every member has a vector, rows sorted by (text, id). REFUSES otherwise."""
    if len(ids) != n_expected:
        refuse("membership-count mismatch at %s: %d members in the graph, CSV n = %d (VOID: a failed precondition)"
               % (where, len(ids), n_expected))
    missing = [i for i in ids if i not in vecmap]
    if missing:
        refuse("%d of %d members of %s have no embedding (e.g. %s)" % (len(missing), len(ids), where, missing[:3]))
    order = sorted(ids, key=lambda i: (vecmap[i][0], i))
    return np.stack([vecmap[i][1] for i in order]), order


# ------------------------------------------------------------------------------------------------ the generator
def within_node_cloud_eigen(mu, s, Vt, m, n, rng, block=1024, normalise=True):
    """THE PRODUCTION GENERATOR (ruling A6): mu + Z diag(s) V^T / sqrt(m), Z iid N(0, 1) of shape n x rank, then unit-normalised,
    with C = U diag(s) V^T the thin SVD of the site's centred m x sliceDim member matrix. Before normalisation each row is
    N(mu, V diag(s^2) V^T / m) = N(mu, C^T C / m): the law of withinNodeCloud, EXACT IN DISTRIBUTION (not draw for draw).
    The literal forms below stay the bit-verified reference (ST-JVM); ST-EQ tests the equivalence."""
    scale = s / math.sqrt(m)
    out = np.empty((n, mu.size))
    for a in range(0, n, block):
        e = min(n, a + block)
        Z = rng.standard_normal((e - a, s.size))
        Y = mu + (Z * scale) @ Vt
        if normalise:
            Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)
        out[a:e] = Y
    return out


def within_node_cloud(mu, C, n, rng, block=1024, normalise=True):
    """withinNodeCloud (Kotlin L558-L577): out = mu + sum_c (g_c / sqrt(m)) c, g iid N(0,1) consumed row-major, then
    unit-normalised. Rows are generated in blocks; the Generator's stream is sequential, so the blocks change nothing."""
    m = C.shape[0]
    inv = 1.0 / math.sqrt(m)
    out = np.empty((n, mu.size))
    for s in range(0, n, block):
        e = min(n, s + block)
        G = rng.standard_normal((e - s, m))
        Y = mu + (G * inv) @ C
        if normalise:
            Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)
        out[s:e] = Y
    return out


def within_node_cloud_loop(mu, centered, n, next_gaussian):
    """A line-by-line transcription of the Kotlin function (scalar loops, the same operation order)."""
    dim = len(mu)
    inv = 1.0 / math.sqrt(len(centered))
    res = []
    for _ in range(n):
        out = list(mu)
        for c in centered:
            g = next_gaussian() * inv
            for i in range(dim):
                out[i] += g * c[i]
        norm = 0.0
        for x in out:
            norm += x * x
        norm = math.sqrt(norm)
        res.append([out[i] / norm for i in range(dim)])
    return res


def _hi_lo(x):
    import struct
    u = struct.unpack(">Q", struct.pack(">d", x))[0]
    hi = u >> 32
    return (hi - (1 << 32) if hi >= (1 << 31) else hi), u & 0xFFFFFFFF


def _with_hi(x, hi):
    import struct
    u = struct.unpack(">Q", struct.pack(">d", x))[0]
    return struct.unpack(">d", struct.pack(">Q", ((hi & 0xFFFFFFFF) << 32) | (u & 0xFFFFFFFF)))[0]


def fdlibm_log(x):
    """StrictMath.log = fdlibm e_log.c (the JDK's FdLibm.Log), ported operation for operation; math.log may differ by 1 ulp."""
    ln2_hi, ln2_lo, two54 = 6.93147180369123816490e-01, 1.90821492927058770002e-10, 1.80143985094819840000e+16
    Lg1, Lg2, Lg3 = 6.666666666666735130e-01, 3.999999999940941908e-01, 2.857142874366239149e-01
    Lg4, Lg5, Lg6, Lg7 = 2.222219843214978396e-01, 1.818357216161805012e-01, 1.531383769920937332e-01, 1.479819860511658591e-01
    hx, lx = _hi_lo(x)
    k = 0
    if hx < 0x00100000:
        if ((hx & 0x7fffffff) | lx) == 0:
            return float("-inf")
        if hx < 0:
            return float("nan")
        k -= 54
        x *= two54
        hx, _ = _hi_lo(x)
    if hx >= 0x7ff00000:
        return x + x
    k += (hx >> 20) - 1023
    hx &= 0x000fffff
    i = (hx + 0x95f64) & 0x100000
    x = _with_hi(x, hx | (i ^ 0x3ff00000))
    k += (i >> 20)
    f = x - 1.0
    if (0x000fffff & (2 + hx)) < 3:
        if f == 0.0:
            if k == 0:
                return 0.0
            dk = float(k)
            return dk * ln2_hi + dk * ln2_lo
        R = f * f * (0.5 - 0.33333333333333333 * f)
        if k == 0:
            return f - R
        dk = float(k)
        return dk * ln2_hi - ((R - dk * ln2_lo) - f)
    s = f / (2.0 + f)
    dk = float(k)
    z = s * s
    i = hx - 0x6147a
    w = z * z
    j = 0x6b851 - hx
    t1 = w * (Lg2 + w * (Lg4 + w * Lg6))
    t2 = z * (Lg1 + w * (Lg3 + w * (Lg5 + w * Lg7)))
    i |= j
    R = t2 + t1
    if i > 0:
        hfsq = 0.5 * f * f
        if k == 0:
            return f - (hfsq - s * (hfsq + R))
        return dk * ln2_hi - ((hfsq - (s * (hfsq + R) + dk * ln2_lo)) - f)
    if k == 0:
        return f - s * (f - R)
    return dk * ln2_hi - ((s * (f - R) - dk * ln2_lo) - f)


class JavaRandom(object):
    """java.util.Random: the 48-bit LCG and the legacy polar nextGaussian (StrictMath.log via fdlibm_log; sqrt is exact)."""
    MULT, ADD, MASK = 0x5DEECE66D, 0xB, (1 << 48) - 1

    def __init__(self, seed):
        self.seed = (seed ^ self.MULT) & self.MASK
        self.have = False
        self.saved = 0.0

    def next(self, bits):
        self.seed = (self.seed * self.MULT + self.ADD) & self.MASK
        r = self.seed >> (48 - bits)
        return r - (1 << 32) if r >= (1 << 31) else r

    def next_double(self):
        return ((self.next(26) << 27) + self.next(27)) * (2.0 ** -53)

    def next_gaussian(self):
        if self.have:
            self.have = False
            return self.saved
        while True:
            v1 = 2 * self.next_double() - 1
            v2 = 2 * self.next_double() - 1
            s = v1 * v1 + v2 * v2
            if 0 < s < 1:
                break
        mul = math.sqrt(-2 * fdlibm_log(s) / s)
        self.saved = v2 * mul
        self.have = True
        return v1 * mul


# ------------------------------------------------------------------------------------------------ the statistic
class FitError(Exception):
    pass


def k1_params(p):
    return p + p * (p + 1) // 2


def k2_params(p):
    return 2 * k1_params(p) + 1


def pca_basis(X):
    """Centre, then the principal axes from np.linalg.eigh of the symmetric PSD scatter matrix Xc^T Xc, eigenvalues sorted
    DESCENDING (the orchestrator's ruling after the b617888 crash: np.linalg.svd of the scatter did not converge on a
    rank-deficient n < d draw, frozen n00000109 draw 10). Same subspace as the thin SVD of Xc (pca_basis_thin, the reference);
    one route for every cell, no fallback. Rows of the returned Vt are the axes, largest variance first."""
    Xc = X - X.mean(axis=0)
    w, V = np.linalg.eigh(Xc.T @ Xc)
    order = np.argsort(w, kind="stable")[::-1]
    return Xc, V[:, order].T


def pca_basis_thin(X):
    """The reference: thin SVD of the centred matrix (the e79fdb4 form)."""
    Xc = X - X.mean(axis=0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc, Vt


def loglik_k1(Z):
    n, p = Z.shape
    Zc = Z - Z.mean(axis=0)
    S = Zc.T @ Zc / n
    sign, logdet = np.linalg.slogdet(S)
    if sign <= 0 or not np.isfinite(logdet):
        raise FitError("k = 1 covariance is singular")
    return -0.5 * n * (p * math.log(2 * math.pi) + logdet + p)


def lr_stats(Z, random_state):
    from sklearn.mixture import GaussianMixture
    from sklearn.exceptions import ConvergenceWarning
    from scipy.special import xlogy
    n, p = Z.shape
    l1 = loglik_k1(Z)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        gm = GaussianMixture(random_state=int(random_state), **GMM_KW).fit(Z)
    l2 = float(gm.score(Z)) * n
    R = gm.predict_proba(Z)
    ent = float(-np.sum(xlogy(R, R)))
    bic1 = -2.0 * l1 + k1_params(p) * math.log(n)
    bic2 = -2.0 * l2 + k2_params(p) * math.log(n)
    lr = 2.0 * (l2 - l1)
    if not all(np.isfinite([l1, l2, lr])):
        raise FitError("non-finite log-likelihood")
    return dict(LR=lr, l1=l1, l2=l2, dBIC=bic1 - bic2, dICL=bic1 - (bic2 + 2.0 * ent), ent=ent,
                converged=bool(gm.converged_), n_iter=int(gm.n_iter_))


def safe_stats(Z, rs):
    try:
        return dict(ok=True, **lr_stats(Z, rs))
    except Exception as e:                       # recorded; --analyze REFUSES on any failed fit (see REFUSALS)
        return dict(ok=False, error="%s: %s" % (type(e).__name__, e))


def site_stream(tree_index, row):
    """Ruling A1: one SeedSequence per (tree, site), tree_index in the registered TREES order, row 0-based in the CSV."""
    return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, row))


def draw_stream(tree_index, row, b):
    """The b-th spawned child of the site's SeedSequence (identical to site_stream(tree_index, row).spawn(b + 1)[b])."""
    return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, row, b))


def leaf_stream(tree_index, leaf_id):
    """Ruling A2: spawn_key = (tree_index, 1000000 + node number)."""
    return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, LEAF_SPAWN_BASE + node_number(leaf_id)))


def node_number(node_id):
    if not (len(node_id) == 9 and node_id[0] == "n" and node_id[1:].isdigit()):
        refuse("unexpected node id %r" % node_id)
    return int(node_id[1:])


def draw_cell(ctx, b, legs):
    """One null draw of one site: the Gaussians first, then three random_states (p10, p5, p20)."""
    t0 = time.process_time()
    rng = np.random.default_rng(draw_stream(ctx.tree_index, ctx.row, b))
    Y = within_node_cloud_eigen(ctx.mu, ctx.s, ctx.Vt, ctx.C.shape[0], ctx.n, rng)
    states = rng.integers(0, 2 ** 31 - 1, size=3)
    Yc, Vt = pca_basis(Y)
    cpu = {"gen_pca": time.process_time() - t0}
    out = dict(site=ctx.node_id, b=int(b))
    for leg in LEGS_ALL:
        if leg not in legs:
            out["lr" + leg] = None
            continue
        t1 = time.process_time()
        st = safe_stats(Yc @ Vt[:int(leg)].T, states[LEG_STATE_INDEX[leg]])
        cpu[leg] = time.process_time() - t1
        out["lr" + leg] = st["LR"] if st["ok"] else None
        out["ok" + leg] = st["ok"]
        if not st["ok"]:
            out["err" + leg] = st["error"]
        else:
            out["conv" + leg] = st["converged"]
    cpu["10"] = cpu.get("10", 0.0) + cpu.pop("gen_pca")          # the generator is charged to the deciding leg
    out["cpu"] = cpu
    return out


def obs_cell(ctx):
    t0 = time.process_time()
    states = np.random.default_rng(site_stream(ctx.tree_index, ctx.row)).integers(0, 2 ** 31 - 1, size=3)
    Xc, Vt = pca_basis(ctx.X)
    out = dict(site=ctx.node_id, n=ctx.n)
    for leg in LEGS_ALL:
        out["p" + leg] = safe_stats(Xc @ Vt[:int(leg)].T, states[LEG_STATE_INDEX[leg]])
    s10 = out["p10"]
    out["gain"] = (s10["l2"] - s10["l1"]) / ctx.n if s10["ok"] else None
    out["cpu"] = {"10": time.process_time() - t0}
    return out


def leaf_cell(tree_index, leaf_id, X):
    t0 = time.process_time()
    rs = np.random.default_rng(leaf_stream(tree_index, leaf_id)).integers(0, 2 ** 31 - 1, size=1)[0]
    Xc, Vt = pca_basis(X)
    st = safe_stats(Xc @ Vt[:10].T, rs)
    return dict(leaf=leaf_id, n=int(X.shape[0]), ok=st["ok"], gain=(st["l2"] - st["l1"]) / X.shape[0] if st["ok"] else None,
                error=st.get("error"), cpu={"10": time.process_time() - t0})


# ------------------------------------------------------------------------------------------------ q, escalation, drop
def q_add_one(c, B):
    return Fraction(1 + c, B + 1)


def certified(q):
    return q <= CERT_Q


def in_escalation_band(q):
    return ESC_LO <= q <= ESC_HI


def escalates(tree, node_id, q199):
    return tree == DECIDING_TREE and node_id in DECIDING and in_escalation_band(q199)


def legs_after_guard(projected_cpu_min, cap=CAP_CPU_MIN):
    """The registered drop order: above the budget the p = 5 / p = 20 legs go first; p = 10 is never dropped."""
    return ("10",) if projected_cpu_min > cap else LEGS_ALL


def exceed_count(null_lrs, obs):
    return sum(1 for x in null_lrs if x >= obs)


def clopper_pearson(c, B, alpha=0.05):
    from scipy.stats import beta
    lo = 0.0 if c == 0 else float(beta.ppf(alpha / 2, c, B - c + 1))
    hi = 1.0 if c == B else float(beta.ppf(1 - alpha / 2, c + 1, B - c))
    return lo, hi


def secondary(site_gain, leaf_gains):
    """site gain minus the median gain over descendant leaves with n >= 110; None when no such leaf."""
    g = [x for (n, x) in leaf_gains if n >= LEAF_MIN_N]
    if site_gain is None or not g:
        return None
    return site_gain - float(np.median(g))


# ------------------------------------------------------------------------------------------------ state (chunks)
def write_once(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def list_chunks(state_dir):
    if not os.path.isdir(state_dir):
        return []
    return sorted(f for f in os.listdir(state_dir) if f.startswith("chunk_") and f.endswith(".json"))


def read_chunks(state_dir):
    out = []
    for f in list_chunks(state_dir):
        with open(os.path.join(state_dir, f), encoding="utf-8") as h:
            out.append(json.load(h))
    return out


def cell_key(kind, cell):
    if kind == "obs":
        return ("obs", cell["site"])
    if kind == "leaf":
        return ("leaf", cell["leaf"])
    return ("draw", cell["site"], cell["b"])


def run_chunk(state_dir, tree, kind, tasks, compute, meta_sha, budget_s=CHUNK_WALL_S, max_cells=None, group_of=None):
    """Compute cells in `tasks` order until the next group (a draw-set: the same b across the site range) would overrun the
    wall budget; write ONE write-once chunk file; return the number of cells written."""
    t_wall0, t_cpu0 = time.perf_counter(), time.process_time()
    cells, groups_t, i = [], [], 0
    group_of = group_of or (lambda t: id(t))
    while i < len(tasks):
        g = group_of(tasks[i])
        j = i
        while j < len(tasks) and group_of(tasks[j]) == g:
            j += 1
        if cells:
            pred = max(groups_t) if groups_t else 0.0
            if time.perf_counter() - t_wall0 + pred > budget_s:
                break
            if max_cells is not None and len(cells) + (j - i) > max_cells:
                break
        tg = time.perf_counter()
        for t in tasks[i:j]:
            cells.append(compute(t))
        groups_t.append(time.perf_counter() - tg)
        i = j
    if not cells:
        return 0
    seq = len(list_chunks(state_dir)) + 1
    body = dict(kind=kind, tree=tree, meta_sha=meta_sha, script=script_pins(), cells=cells,
                wall_s=time.perf_counter() - t_wall0, cpu_s=time.process_time() - t_cpu0,
                written=datetime.datetime.now().isoformat(timespec="seconds"))
    write_once(os.path.join(state_dir, "chunk_%05d_%s_%s.json" % (seq, tree, kind)), json.dumps(body, sort_keys=True))
    return len(cells)


def strip_timing(cell):
    return {k: v for k, v in cell.items() if k != "cpu"}


# ------------------------------------------------------------------------------------------------ per-table pins
def table_pins():
    lines = {}
    for db, t, order in PIN_TABLES:
        con = pool_guard.open_ro(os.path.join(DATA_ROOT, db))
        try:
            h, n = hashlib.sha256(), 0
            for row in con.execute('SELECT * FROM "%s" ORDER BY %s' % (t, order)):
                h.update(repr(row).encode())
                h.update(b"\n")
                n += 1
        finally:
            con.close()
        lines["%s:%s" % (db, t)] = "n=%d sha256=%s" % (n, h.hexdigest())
    for tree in TREES:
        g = load_graph(tree["snapshot"])
        lines["%s:snapshots[%s]" % (g["store"], tree["snapshot"])] = "graph sha256=%s" % g["sha"]
    return lines


# ------------------------------------------------------------------------------------------------ tree contexts
def tree_contexts(tree, verbose=False):
    rows, csv_pins = load_csv(tree)
    g = load_graph(tree["snapshot"])
    byid = g["byid"]
    members = {}
    for r in rows:
        if r["node_id"] not in byid:
            refuse("%s: CSV site %s is not in snapshot %s" % (tree["name"], r["node_id"], tree["snapshot"]))
        members[r["node_id"]] = region_query_ids(r["node_id"], byid)
    leaves = {}
    for r in rows:
        for lf in descendant_leaves(r["node_id"], byid):
            if lf not in leaves:
                leaves[lf] = region_query_ids(lf, byid)
    need = set()
    for v in members.values():
        need.update(v)
    for v in leaves.values():
        need.update(v)
    vecmap = load_vectors(sorted(need), tree["dim"])
    ctxs = []
    for i, r in enumerate(rows):
        X, order = prepare_members(members[r["node_id"]], vecmap, int(r["n"]), "%s/%s" % (tree["name"], r["node_id"]))
        ctxs.append(SiteCtx(tree["name"], i, r["node_id"], r["label"], int(r["depth"]), int(r["n"]), int(r["k"]),
                            r["cert_site_p95"].strip().lower() == "true", r["q_deflated"], X, order,
                            tree_index=TREE_INDEX[tree["name"]]))
    leaf_sets = {}
    for lf, ids in leaves.items():
        if len(ids) >= LEAF_MIN_N:
            miss = [i for i in ids if i not in vecmap]
            if miss:
                refuse("%s leaf %s: %d members without an embedding" % (tree["name"], lf, len(miss)))
            order = sorted(ids, key=lambda i: (vecmap[i][0], i))
            leaf_sets[lf] = np.stack([vecmap[i][1] for i in order])
    site_leaves = {r["node_id"]: [(lf, len(leaves[lf])) for lf in descendant_leaves(r["node_id"], byid)] for r in rows}
    return dict(tree=tree, rows=rows, csv_pins=csv_pins, graph=g, ctxs=ctxs, leaf_sets=leaf_sets, site_leaves=site_leaves,
                n_vectors=len(vecmap), n_needed=len(need))


# ------------------------------------------------------------------------------------------------ run
def meta_body():
    return dict(test="MIX-LRT-SITE", registration="docs/judge_v2_program.md L20595-L20670 (31d092e)", pool=POOL_ID,
                script=script_pins(), trees=[{k: t[k] for k in ("name", "csv", "blob", "lf16", "snapshot", "dim")} for t in TREES],
                root_entropy=ROOT_ENTROPY, B=[B_MAIN, B_ESC, B_DESC], gmm=GMM_KW, leaf_min_n=LEAF_MIN_N, cap_cpu_min=CAP_CPU_MIN,
                threads={v: os.environ.get(v) for v in THREAD_VARS})


def ensure_meta(state_dir):
    body = json.dumps(meta_body(), sort_keys=True)
    p = os.path.join(state_dir, "meta.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            old = f.read()
        if old != body:
            refuse("state/meta.json differs from this script's meta (script, pins or constants changed since the first "
                   "launch); a new state directory is needed")
    else:
        write_once(p, body)
    return hashlib.sha256(body.encode()).hexdigest()


def done_keys(chunks):
    keys = {}
    for ch in chunks:
        for c in ch["cells"]:
            k = (ch["tree"],) + cell_key(ch["kind"], c)
            keys[k] = keys.get(k, 0) + 1
    return keys


def projection(chunks, legs_desc=True):
    """CPU-min projected from each tree's FIRST draws chunk (b = 0 at every site)."""
    first = {}
    for ch in chunks:
        if ch["kind"] == "draws" and ch["tree"] not in first:
            first[ch["tree"]] = ch
    if set(first) != {t["name"] for t in TREES}:
        return None
    p10 = pdesc = 0.0
    esc = 0.0
    for name, ch in first.items():
        for c in ch["cells"]:
            p10 += c["cpu"].get("10", 0.0) * B_MAIN
            pdesc += (c["cpu"].get("5", 0.0) + c["cpu"].get("20", 0.0)) * B_DESC
            if name == DECIDING_TREE and c["site"] in DECIDING:
                esc += c["cpu"].get("10", 0.0) * (B_ESC - B_MAIN)
    obs = sum(sum(c["cpu"].get("10", 0.0) for c in ch["cells"]) for ch in chunks if ch["kind"] in ("obs", "leaf"))
    return dict(p10=p10 / 60, esc=esc / 60, desc=pdesc / 60, obs=obs / 60, total=(p10 + esc + pdesc) / 60 + obs / 60)


def post_drop_total(pr):
    """MIX-FLAT-SELFTEST-GAPS D3 (READY dde660e): the projection after the registered drop (p = 5 / p = 20 gone, p = 10 never
    dropped): p10 + maximal escalation + observed."""
    return pr["p10"] + pr["esc"] + pr["obs"]


def cost_lines(pr, plan):
    """The [COST] lines of print_cost (pure; the selftest executes both OVER / within branches of each line)."""
    if pr is None:
        return ["[COST] not yet measured (the first draws chunk of every tree is pending); budget %.0f CPU-min" % CAP_CPU_MIN]
    L = ["[COST] projected from the first draws chunk of each tree: p10 %.1f + max escalation %.1f + p5/p20 %.1f + observed "
         "%.1f = %.1f CPU-min; budget %.0f CPU-min -> %s%s"
         % (pr["p10"], pr["esc"], pr["desc"], pr["obs"], pr["total"], CAP_CPU_MIN,
            "OVER: p5/p20 legs DROPPED (registered drop order)" if pr["total"] > CAP_CPU_MIN else "within budget",
            "" if plan is None else " | plan.json: legs %s" % "/".join(plan["legs_desc"]) if plan["legs_desc"] else " | plan.json: p5/p20 DROPPED")]
    pd = post_drop_total(pr)
    L.append("[COST] post-drop projection (p10 %.1f + max escalation %.1f + observed %.1f; p = 10 is never dropped, no second step is "
             "registered) = %.1f CPU-min against the %.0f CPU-min cap -> %s"
             % (pr["p10"], pr["esc"], pr["obs"], pd, CAP_CPU_MIN, "OVER the cap even after the drop" if pd > CAP_CPU_MIN else "within the cap"))
    return L


def measured_cpu(chunks):
    """MIX-FLAT-SELFTEST-GAPS D3 (post-run review 8032197): the MEASURED process CPU of the cells in the state, in CPU-min:
    p10 = observed cells (all legs of the observed fit) + the p = 10 leg of every null draw (escalation included, the generator
    charged to it); desc = the p = 5 / p = 20 legs of the draws; leaf = the secondary statistic's leaf fits."""
    p10 = desc = leaf = 0.0
    for ch in chunks:
        for c in ch["cells"]:
            cpu = c.get("cpu", {})
            if ch["kind"] == "leaf":
                leaf += cpu.get("10", 0.0)
            else:
                p10 += cpu.get("10", 0.0)
                desc += cpu.get("5", 0.0) + cpu.get("20", 0.0)
    return dict(p10=p10 / 60, desc=desc / 60, leaf=leaf / 60, total=(p10 + desc + leaf) / 60)


def measured_cost_line(m, cap=CAP_CPU_MIN):
    return ("[COST] MEASURED (process CPU of the cells in the state): p = 10 leg (observed + null draws, escalation included) %.1f "
            "CPU-min; all legs and leaves %.1f CPU-min (p5/p20 %.1f, leaves %.1f); against the %.0f CPU-min cap -> %s"
            % (m["p10"], m["total"], m["desc"], m["leaf"], cap, "OVER the cap" if m["total"] > cap else "within the cap"))


def print_cost(chunks, plan):
    for line in cost_lines(projection(chunks), plan):
        print(line)


def run(state_dir=STATE_DIR, max_chunks=None):
    print_header()
    before = table_pins()
    for k, v in before.items():
        print("[PIN before] %s %s" % (k, v))
    meta_sha = ensure_meta(state_dir)
    n_chunks = 0
    for tree in TREES:
        tc = tree_contexts(tree)
        ctxs = tc["ctxs"]
        by_id = {c.node_id: c for c in ctxs}
        chunks = read_chunks(state_dir)
        dk = done_keys(chunks)
        name = tree["name"]
        # 1. observed statistics, then the leaves of the secondary statistic
        todo = [c for c in ctxs if (name, "obs", c.node_id) not in dk]
        while todo and (max_chunks is None or n_chunks < max_chunks):
            k = run_chunk(state_dir, name, "obs", todo, obs_cell, meta_sha)
            todo = todo[k:]
            n_chunks += 1
        todo = [lf for lf in sorted(tc["leaf_sets"]) if (name, "leaf", lf) not in dk]
        while todo and (max_chunks is None or n_chunks < max_chunks):
            k = run_chunk(state_dir, name, "leaf", todo, lambda lf: leaf_cell(TREE_INDEX[name], lf, tc["leaf_sets"][lf]), meta_sha)
            todo = todo[k:]
            n_chunks += 1
        # 2. the first draws chunk: b = 0 at every site, all three legs
        if not any((name, "draw", c.node_id, 0) in dk for c in ctxs) and (max_chunks is None or n_chunks < max_chunks):
            run_chunk(state_dir, name, "draws", [(c.node_id, 0) for c in ctxs],
                      lambda t: draw_cell(by_id[t[0]], t[1], LEGS_ALL), meta_sha, budget_s=float("inf"),
                      group_of=lambda t: t[1])
            n_chunks += 1
    chunks = read_chunks(state_dir)
    plan_p = os.path.join(state_dir, "plan.json")
    plan = json.load(open(plan_p, encoding="utf-8")) if os.path.exists(plan_p) else None
    pr = projection(chunks)
    if plan is None and pr is not None:
        legs = legs_after_guard(pr["total"])
        plan = dict(projection=pr, legs_desc=[l for l in legs if l != "10"], cap_cpu_min=CAP_CPU_MIN)
        write_once(plan_p, json.dumps(plan, sort_keys=True))
    print_cost(chunks, plan)
    if plan is None:
        print("%s the cost plan is pending (not every tree's first draws chunk exists); re-run --run" % TAG)
        return after_pins(before)
    legs_b = ("10",) + tuple(plan["legs_desc"])
    for tree in TREES:
        name = tree["name"]
        tc = tree_contexts(tree)
        by_id = {c.node_id: c for c in tc["ctxs"]}
        while max_chunks is None or n_chunks < max_chunks:
            dk = done_keys(read_chunks(state_dir))
            tasks = [(c.node_id, b) for b in range(1, B_MAIN) for c in tc["ctxs"] if (name, "draw", c.node_id, b) not in dk]
            if not tasks:
                break
            run_chunk(state_dir, name, "draws", tasks,
                      lambda t: draw_cell(by_id[t[0]], t[1], legs_b if t[1] < B_DESC else ("10",)), meta_sha,
                      group_of=lambda t: t[1])
            n_chunks += 1
        if name == DECIDING_TREE:
            for sid in DECIDING:
                while max_chunks is None or n_chunks < max_chunks:
                    tasks = escalation_tasks(read_chunks(state_dir), name, sid)
                    if not tasks:
                        break
                    run_chunk(state_dir, name, "draws", tasks, lambda t: draw_cell(by_id[t[0]], t[1], ("10",)), meta_sha,
                              group_of=lambda t: t[1])
                    n_chunks += 1
    print_cost(read_chunks(state_dir), plan)
    print(measured_cost_line(measured_cpu(read_chunks(state_dir))))
    print("%s %d chunk(s) written this run; no statistic is printed by --run" % (TAG, n_chunks))
    return after_pins(before)


def after_pins(before):
    after = table_pins()
    changed = [k for k in before if after.get(k) != before[k]] + [k for k in after if k not in before]
    for k, v in after.items():
        print("[PIN after ] %s %s" % (k, v))
    if changed:
        refuse("a DB pin changed during the run: %s" % changed)
    print("[PIN] before == after on every pinned table / row")
    return 0


def q_admitted(c, B, f):
    """Ruling A3 (ii): q over the B - f admitted draws, (1 + c) / (B - f + 1)."""
    return q_add_one(c, B - f)


def escalation_tasks(chunks, name, sid):
    """run()'s escalation decision (MIX-FLAT-SELFTEST-GAPS D6, READY dde660e; behaviour unchanged): the pending escalation
    draws (b = 199..998) of site sid, or [] when its 199 main draws are not all present, its q at B = 199 over the ADMITTED draws
    (failed draws excluded and counted, ruling A3) is not computable, or the site does not escalate (a deciding site of the
    frozen tree with q in [0.02, 0.10])."""
    dk = done_keys(chunks)
    if not all((name, "draw", sid, b) in dk for b in range(B_MAIN)):
        return []
    q199 = site_q(chunks, name, sid, B_MAIN)
    if q199 is None or not escalates(name, sid, q199):
        return []
    return [(sid, b) for b in range(B_MAIN, B_ESC) if (name, "draw", sid, b) not in dk]


def site_q(chunks, tree, sid, B):
    """q at B over the admitted draws (failed draws excluded and counted), for the escalation decision; None if not computable."""
    obs = None
    lrs = {}
    for ch in chunks:
        if ch["tree"] != tree:
            continue
        for c in ch["cells"]:
            if ch["kind"] == "obs" and c["site"] == sid:
                obs = c["p10"]["LR"] if c["p10"]["ok"] else None
            elif ch["kind"] == "draws" and c["site"] == sid and c["b"] < B:
                lrs[c["b"]] = c["lr10"] if c.get("ok10", False) else None
    if obs is None or len(lrs) != B:
        return None
    ok = [v for v in lrs.values() if v is not None]
    return q_admitted(exceed_count(ok, obs), B, B - len(ok))


# ------------------------------------------------------------------------------------------------ analysis
def collect(chunks, sites_by_tree, leaves_by_tree, plan):
    """REFUSES unless every registered cell is present exactly once. Failed fits follow ruling A3 (programme L20864-L20919):
    (ii) a non-deciding site: failed p = 10 null draws are excluded and counted (f); f >= 2 at B = 199 (more than 1%) or a failed
    observed fit makes the site VOID; (iii) a deciding site: ANY failed p = 10 fit, observed or null, up to the final B, VOIDs C1;
    (iv) p = 5 / p = 20: any failure in a leg VOIDs that leg's q at that site only; (vi) a failed leaf fit is excluded and counted.
    A non-converged EM is NOT a failure."""
    dk = done_keys(chunks)
    dup = [k for k, v in dk.items() if v != 1]
    if dup:
        refuse("%d cell(s) present more than once, e.g. %s" % (len(dup), dup[:3]))
    obs, leaf, draws = {}, {}, {}
    for ch in chunks:
        for c in ch["cells"]:
            if ch["kind"] == "obs":
                obs[(ch["tree"], c["site"])] = c
            elif ch["kind"] == "leaf":
                leaf[(ch["tree"], c["leaf"])] = c
            else:
                draws.setdefault((ch["tree"], c["site"]), {})[c["b"]] = c
    legs_desc = tuple(plan["legs_desc"]) if plan is not None else None
    if legs_desc is None:
        refuse("state/plan.json is missing (the cost plan is part of the registered design)")
    out = {}
    expected_keys = set()
    for tree, sites in sites_by_tree.items():
        rows = []
        for s in sites:
            sid = s["node_id"]
            deciding = bool(tree == DECIDING_TREE and sid in DECIDING)
            o = obs.get((tree, sid))
            if o is None:
                refuse("%s/%s: the observed cell is missing" % (tree, sid))
            expected_keys.add((tree, "obs", sid))
            d = draws.get((tree, sid), {})
            B = B_MAIN
            for b in range(B_MAIN):
                if b not in d:
                    refuse("%s/%s: draw %d is missing (analysis refuses partial designs)" % (tree, sid, b))
            obs_ok = bool(o["p10"]["ok"])
            if obs_ok:
                ok199 = [d[b]["lr10"] for b in range(B_MAIN) if d[b].get("ok10", False) and d[b]["lr10"] is not None]
                q199 = q_admitted(exceed_count(ok199, o["p10"]["LR"]), B_MAIN, B_MAIN - len(ok199))
                if escalates(tree, sid, q199):
                    B = B_ESC
                    for b in range(B_MAIN, B_ESC):
                        if b not in d:
                            refuse("%s/%s: escalation draw %d is missing (q at B = 199 is in the band)" % (tree, sid, b))
            extra = [b for b in d if b >= B]
            if extra:
                refuse("%s/%s: %d draw(s) beyond the registered B = %d (e.g. %s)" % (tree, sid, len(extra), B, extra[:3]))
            failed = []
            for b in range(B):
                expected_keys.add((tree, "draw", sid, b))
                if not d[b].get("ok10", False) or d[b]["lr10"] is None:
                    failed.append(b)
            f = len(failed)
            void, reason, c1_void = False, "", ""
            if not obs_ok:
                void, reason = True, "observed p = 10 fit FAILED (%s)" % o["p10"].get("error")
            elif f >= 2:
                void, reason = True, "%d of %d null p = 10 fits FAILED (more than 1%%)" % (f, B)
            if deciding and (not obs_ok or f > 0):
                c1_void = "a failed p = 10 fit at the deciding site %s (%s)" % (
                    sid, reason if not obs_ok else "%d of %d null fits failed, e.g. draw %d: %s" % (f, B, failed[0], d[failed[0]].get("err10")))
            null = {"10": [d[b]["lr10"] for b in range(B) if b not in failed]}
            for leg in ("5", "20"):
                if leg in legs_desc:
                    vals = [d[b].get("lr" + leg) for b in range(B_DESC)]
                    if (not o["p" + leg]["ok"]) or any(v is None for v in vals) or not all(d[b].get("ok" + leg, False) for b in range(B_DESC)):
                        null[leg] = "VOID"
                    else:
                        null[leg] = vals
                else:
                    null[leg] = None
            lg, lfail = [], []
            for lf, n in s["leaves"]:
                if n >= LEAF_MIN_N:
                    lc = leaf.get((tree, lf))
                    if lc is None:
                        refuse("%s: leaf %s (n %d) of the secondary statistic is missing" % (tree, lf, n))
                    expected_keys.add((tree, "leaf", lf))
                    if lc["ok"]:
                        lg.append((n, lc["gain"]))
                    else:
                        lfail.append(lf)
            rows.append(dict(s, obs={leg: o["p" + leg] for leg in LEGS_ALL}, gain=o.get("gain"), leaf_gains=lg, leaf_fail_ids=lfail,
                             null=null, B_total=B, f=f, void=void, void_reason=reason, c1_void=c1_void,
                             cpu10=o["cpu"]["10"] + sum(d[b]["cpu"].get("10", 0.0) for b in range(B))))
        out[tree] = rows
    stray = [k for k in dk if k not in expected_keys]
    if stray:
        refuse("%d unexpected cell(s) in the state (e.g. %s)" % (len(stray), stray[:3]))
    return out


def summarise_site(s):
    r = dict(node_id=s["node_id"], label=s["label"], depth=s["depth"], n=s["n"], k=s["k"], cert_j=bool(s["cert_j"]),
             q_defl=s["q_defl"], f=s.get("f", 0), B_total=s.get("B_total", len(s["null"]["10"])), void=bool(s.get("void", False)),
             void_reason=s.get("void_reason", ""), c1_void=s.get("c1_void", ""), leaf_fail_ids=list(s.get("leaf_fail_ids", [])),
             cpu10=s.get("cpu10", 0.0), overparam=[leg for leg in LEGS_ALL if s["n"] < k2_params(int(leg))])
    if r["void"]:
        r.update(LR=None, c=None, B=None, q=None, cert=False, dBIC=None, dICL=None, gain=None, leaf_median=None, sec=None,
                 q5=None, cert5=None, q20=None, cert20=None)
        return r
    obs10 = s["obs"]["10"]["LR"]
    B = len(s["null"]["10"])                       # the admitted draws: B_total - f
    c = exceed_count(s["null"]["10"], obs10)
    q = q_add_one(c, B)
    lgood = [g for n, g in s["leaf_gains"] if n >= LEAF_MIN_N]
    r.update(LR=obs10, c=c, B=B, q=q, cert=bool(certified(q)), dBIC=s["obs"]["10"]["dBIC"], dICL=s["obs"]["10"]["dICL"],
             gain=s["gain"], leaf_median=float(np.median(lgood)) if lgood else None, sec=secondary(s["gain"], s["leaf_gains"]))
    for leg in ("5", "20"):
        nl = s["null"][leg]
        if nl is None:
            r["q" + leg], r["cert" + leg] = None, None
        elif nl == "VOID":
            r["q" + leg], r["cert" + leg] = "VOID", None
        else:
            r["q" + leg] = q_add_one(exceed_count(nl, s["obs"][leg]["LR"]), len(nl))
            r["cert" + leg] = bool(certified(r["q" + leg]))
    return r


def kappa_2x2(a, b, c, d):
    """a = both certified, b = LR only, c = J only, d = neither."""
    N = a + b + c + d
    if N == 0:
        return None
    po = (a + d) / N
    pe = ((a + b) * (a + c) + (c + d) * (b + d)) / (N * N)
    if pe == 1:
        return None
    return (po - pe) / (1 - pe)


def tree_summary(all_rows):
    """D1-D7 over the NON-VOID sites (ruling A3 (v)); the VOID count is carried for the net denominators."""
    rows = [r for r in all_rows if not r["void"]]
    a = sum(1 for r in rows if r["cert"] and r["cert_j"])
    b = sum(1 for r in rows if r["cert"] and not r["cert_j"])
    c = sum(1 for r in rows if not r["cert"] and r["cert_j"])
    d = sum(1 for r in rows if not r["cert"] and not r["cert_j"])
    n = len(rows)
    jn = a + c
    dropped = bool(rows) and all(r["q5"] is None for r in rows)
    lf = set()
    for r in all_rows:
        lf.update(r.get("leaf_fail_ids", []))
    return dict(n=n, n_all=len(all_rows), void=len(all_rows) - n, f_total=sum(r["f"] for r in all_rows),
                lr_cert=a + b, j_cert=jn, table=(a, b, c, d),
                jaccard=(a / (a + b + c)) if (a + b + c) else None, kappa=kappa_2x2(a, b, c, d),
                superset=(a / jn) if jn else None,
                dbic_pos=sum(1 for r in rows if r["dBIC"] > 0),
                dbic_x_lr=(sum(1 for r in rows if r["dBIC"] > 0 and r["cert"]), sum(1 for r in rows if r["dBIC"] > 0 and not r["cert"]),
                           sum(1 for r in rows if r["dBIC"] <= 0 and r["cert"]), sum(1 for r in rows if r["dBIC"] <= 0 and not r["cert"])),
                dbic_x_j=(sum(1 for r in rows if r["dBIC"] > 0 and r["cert_j"]), sum(1 for r in rows if r["dBIC"] > 0 and not r["cert_j"]),
                          sum(1 for r in rows if r["dBIC"] <= 0 and r["cert_j"]), sum(1 for r in rows if r["dBIC"] <= 0 and not r["cert_j"])),
                dicl_pos=sum(1 for r in rows if r["dICL"] > 0),
                sec_n=sum(1 for r in rows if r["sec"] is not None), leaf_fail=len(lf),
                cert5=None if dropped else sum(1 for r in rows if r["cert5"]),
                cert20=None if dropped else sum(1 for r in rows if r["cert20"]),
                void5=sum(1 for r in rows if r["q5"] == "VOID"), void20=sum(1 for r in rows if r["q20"] == "VOID"),
                over={leg: sum(1 for r in rows if leg in r["overparam"]) for leg in LEGS_ALL},
                cpu10=sum(r["cpu10"] for r in all_rows))


def c1_verdict(dec):
    """dec: node_id -> summarised row (frozen). Returns (held, branches, void_reason); void_reason non-empty -> C1 VOID."""
    vr = "; ".join(dec[s]["c1_void"] for s in DECIDING if dec[s]["c1_void"])
    if vr:
        return False, [], vr
    c13, c14, c55 = (bool(dec[s]["cert"]) for s in DECIDING)
    branches = []
    if c14 or c55:
        branches.append("FAILED-ALL-CERTIFY")
    if not c13:
        branches.append("FAILED-NO-POWER")
    held = bool(c13 and not c14 and not c55)
    return held, branches, ""


def fmt_opt(x, f="%.4f"):
    return "NA" if x is None else f % x


def fq(q):
    return "%.4f (= %d/%d)" % (float(q), q.numerator, q.denominator)


def fden(s):
    return "%d (= %d - %d VOID)" % (s["n"], s["n_all"], s["void"])


def render(summ, legs_desc, run_info=None):
    """The outcome text of record, from summarised rows: every criterion, reading, prediction and falsifier branch."""
    L = []
    names = [t["name"] for t in TREES]
    ts = {t: tree_summary(summ[t]) for t in names}
    dec = {r["node_id"]: r for r in summ[DECIDING_TREE] if r["node_id"] in DECIDING}
    L.append("=== MIX-LRT-SITE outcome (docs/judge_v2_program.md L20595-L20670; rulings L20864-L20919; zero calls) ===")
    L.append("pool %s (printed, not used: geometry of construction members only)" % POOL_ID)
    if run_info:
        L.extend(run_info)
    L.append("")
    L.append("C1 POWER CHECK (frozen; p = 10; the point decides, per site, after the registered escalation):")
    held, branches, c1v = c1_verdict(dec)
    marginal = []
    for sid in DECIDING:
        r = dec[sid]
        if r["void"]:
            L.append("  %s %-40s n %4d | site VOID: %s | f %d" % (sid, r["label"][:40], r["n"], r["void_reason"], r["f"]))
            continue
        lo, hi = clopper_pearson(r["c"], r["B"])
        mc = bool(lo <= 0.05 <= hi)
        if mc:
            marginal.append(sid)
        L.append("  %s %-40s n %4d | LR %.3f | %d of %d admitted null LRs >= observed (B %d, f %d failed) | q_LR %s | %s | "
                 "exceedance 95%% CP [%.4f, %.4f]%s"
                 % (sid, r["label"][:40], r["n"], r["LR"], r["c"], r["B"], r["B_total"], r["f"], fq(r["q"]),
                    "CERTIFIED" if r["cert"] else "not certified", lo, hi, " MC-MARGINAL" if mc else ""))
    if c1v:
        L.append("  C1 VOID (a failed precondition, never an outcome; ruling A3 (iii)): %s" % c1v)
    elif held:
        L.append("  C1 HELD: n00000013 certifies at q_LR <= 0.05 and neither Philosophy site does.")
    else:
        L.append("  C1 FAILED [%s]" % " + ".join(branches))
    if c1v:
        L.append("  WORDING RULE: not applied (C1 VOID)")
    elif marginal:
        L.append("  WORDING RULE: MC-MARGINAL at %s (the 95%% Clopper-Pearson interval on q at the final B contains 0.05)"
                 % ", ".join(marginal))
    else:
        L.append("  WORDING RULE: no deciding site is MC-MARGINAL")
    L.append("")
    L.append("DESCRIPTIVE READOUTS (no bar; nested sites, DEFF > 1 unmeasured; every denominator net of VOID sites, ruling A3 (v)):")
    for t in names:
        s = ts[t]
        a, b, c, d = s["table"]
        nn = max(s["n"], 1)
        L.append("  D1 %-16s LR-certified %d of %s sites (%.3f) | J (cert_site_p95) %d of %s | failed null fits excluded %d"
                 % (t, s["lr_cert"], fden(s), s["lr_cert"] / nn, s["j_cert"], fden(s), s["f_total"]))
        L.append("  D2 %-16s 2x2 [LR&J %d, LR only %d, J only %d, neither %d] | Jaccard %s | Cohen's kappa %s | superset share %s (of %d J-certified)"
                 % (t, a, b, c, d, fmt_opt(s["jaccard"], "%.3f"), fmt_opt(s["kappa"], "%.3f"), fmt_opt(s["superset"], "%.3f"), s["j_cert"]))
        L.append("  D4 %-16s dBIC > 0 on %d of %s (%.3f); x LR-cert [dBIC>0&cert %d, dBIC>0&not %d, dBIC<=0&cert %d, dBIC<=0&not %d];"
                 " x J [%d, %d, %d, %d]; dICL > 0 on %d" % ((t, s["dbic_pos"], fden(s), s["dbic_pos"] / nn) + s["dbic_x_lr"] + s["dbic_x_j"] + (s["dicl_pos"],)))
        L.append("  D5 %-16s secondary statistic defined at %d of %s sites (>= 1 admitted descendant leaf with n >= %d); failed leaf fits"
                 " excluded: %d" % (t, s["sec_n"], fden(s), LEAF_MIN_N, s["leaf_fail"]))
        if s["cert5"] is None:
            L.append("  D6 %-16s p = 5 / p = 20: DROPPED by the cost guard (registered drop order); p = 10 %d" % (t, s["lr_cert"]))
        else:
            L.append("  D6 %-16s certified at B = 49: p = 5 %d (%d leg VOID), p = 10 %d (B = 199), p = 20 %d (%d leg VOID) | OVERPARAM"
                     " p5 %d / p10 %d / p20 %d" % (t, s["cert5"], s["void5"], s["lr_cert"], s["cert20"], s["void20"], s["over"]["5"],
                                                  s["over"]["10"], s["over"]["20"]))
    for sid in DECIDING:
        L.append("  D5 at %s: gain %s, leaf median %s, secondary %s" % (sid, fmt_opt(dec[sid]["gain"], "%.5f"),
                 fmt_opt(dec[sid]["leaf_median"], "%.5f"), fmt_opt(dec[sid]["sec"], "%+.5f")))
    sa = ts["af_clean_s42"]["lr_cert"] / max(ts["af_clean_s42"]["n"], 1)
    so = ts["o0_clean_s42"]["lr_cert"] / max(ts["o0_clean_s42"]["n"], 1)
    L.append("  D3 transfer: LR share af_clean_s42 %.4f minus o0_clean_s42 %.4f = %+.4f | J: 14/69 - 11/60 = 0.2029 - 0.1833 = +0.0196"
             " | SE lower bound 0.0706, MDE 0.198: no transfer sentence is licensed either way" % (sa, so, sa - so))
    s7 = ts["af_bareq512_s42"]
    L.append("  D7 512-d arm af_bareq512_s42: LR-certified %d of %s beside the 256-d trees (another tree on another split; "
             "never a within-tree dimension contrast)" % (s7["lr_cert"], fden(s7)))
    L.append("")
    # ---- readings
    applied = []
    if c1v:
        L.append("THE READING OF THE OUTCOME: none (C1 VOID: a failed precondition; no reading, no sentence)")
    else:
        L.append("THE READING OF THE OUTCOME (the registered table; every reading that applies is printed):")
        every_sup = all(ts[t]["superset"] is not None and ts[t]["superset"] >= 0.8 for t in names)
        pooled_j = sum(ts[t]["table"][0] + ts[t]["table"][2] for t in names)
        pooled_sup = (sum(ts[t]["table"][0] for t in names) / pooled_j) if pooled_j else None
        d1_above = all(ts[t]["lr_cert"] > ts[t]["j_cert"] for t in names)
        ra1 = bool(held and every_sup and d1_above)
        ra2 = bool(held and pooled_sup is not None and pooled_sup >= 0.8 and d1_above)
        rb = bool(held and all(ts[t]["kappa"] is not None and ts[t]["kappa"] >= 0.4 for t in ("af_clean_s42", "o0_clean_s42")))
        rc = bool(held and ts["af_clean_s42"]["lr_cert"] >= 0.9 * ts["af_clean_s42"]["n"])
        rd = bool("FAILED-ALL-CERTIFY" in branches)
        re_ = bool(branches == ["FAILED-NO-POWER"])
        rf = bool(len(branches) == 2)
        pooled_note = (" [pooled-superset reading, NOT OF RECORD (ruling A4): pooled superset share %s -> %s]"
                       % (fmt_opt(pooled_sup, "%.3f"), "would apply" if ra2 else "would not apply"))
        if ra1:
            applied.append("R-a")
            L.append("  (R-a) APPLIES (per tree, ruling A4): the J null is conservative through elongation inflation; the certificate may"
                     " be stated as \"a mode test beyond the node's own elongation\", and the LR-certified set is thicker than the J"
                     " trunk. STILL AN OFFLINE VIEW: no tree, trunk of record, certified count of record, routing or board changes."
                     + pooled_note)
        else:
            L.append("  (R-a) does not apply (per tree, ruling A4)" + pooled_note)
        if rb:
            applied.append("R-b")
            L.append("  (R-b) APPLIES: the site certificate behaves as a mixture test in all but name; a model-based justification of"
                     " the site null; no object changes.")
        else:
            L.append("  (R-b) does not apply")
        if rc:
            applied.append("R-c")
            L.append("  (R-c) APPLIES: \"a mode test with a texture floor\"; D5 is read before any sentence, and no \"mode\" sentence"
                     " is written without it.")
        else:
            L.append("  (R-c) does not apply")
        if rd:
            applied.append("R-d")
            L.append("  (R-d) APPLIES: question embeddings carry non-Gaussian texture at every node; a Gaussian mixture LR cannot"
                     " separate modes from texture here; L6 CLOSES NEGATIVE for its LR / BIC half: \"the certificate is geometric,"
                     " not modal\".")
        else:
            L.append("  (R-d) does not apply")
        if re_:
            applied.append("R-e")
            L.append("  (R-e) APPLIES: the LR has no more power than the deflated null at this site; L6 closes the same way (\"the"
                     " certificate is geometric, not modal\"), with the power qualifier. DISCLOSED BESIDE IT (ruling A5): on the"
                     " synthetic ST2 fixture the LR certified 0 / 20 at 4 within-SD, 14 / 20 at 6, 20 / 20 at 8.")
        else:
            L.append("  (R-e) does not apply")
        if rf:
            applied.append("R-f")
            L.append("  (R-f) APPLIES: both failure branches at once, recorded joined; reading (R-d). DISCLOSED (ruling A5): the ST2"
                     " power curve 0 / 20 at 4, 14 / 20 at 6, 20 / 20 at 8 within-SD.")
        else:
            L.append("  (R-f) does not apply")
        L.append("  L6 now reads: \"mixture LR / BIC: %s; dip test: unexplored\"" % ("C1 HELD" if held else "C1 FAILED [%s]" % " + ".join(branches)))
    L.append("")
    # ---- predictions
    L.append("PREDICTIONS (scored as events or intervals):")

    def sc(ok):
        return "HELD" if ok else "FAILED"
    r13, r14 = dec["n00000013"], dec["n00000014"]
    if c1v:
        L.append("  P1 C1 HELD (p 0.35): UNSCOREABLE (C1 VOID)")
        L.append("  P2 q_LR(n00000013) = 0.005 at B = 199 (p 0.60): UNSCOREABLE (C1 VOID)")
        L.append("  P3 q_LR(n00000014) <= 0.05 (p 0.45): UNSCOREABLE (C1 VOID)")
    else:
        L.append("  P1 C1 HELD (p 0.35): %s" % sc(held))
        L.append("  P2 q_LR(n00000013) = 0.005 at B = 199 (p 0.60): observed %s -> %s" % (fq(r13["q"]), sc(r13["c"] == 0 and r13["B"] == B_MAIN)))
        L.append("  P3 q_LR(n00000014) <= 0.05 (p 0.45): observed %s -> %s" % (fq(r14["q"]), sc(r14["cert"])))
    for t in names:
        pt, lo, hi = P4[t]
        L.append("  P4 %-16s D1 predicted %d, 80%% [%d, %d]; observed %d of %s -> %s" % (t, pt, lo, hi, ts[t]["lr_cert"], fden(ts[t]),
                                                                                    sc(lo <= ts[t]["lr_cert"] <= hi)))
    k_af, s_af = ts["af_clean_s42"]["kappa"], ts["af_clean_s42"]["superset"]
    L.append("  P5a kappa(af_clean_s42) 0.10, 80%% [-0.05, 0.35]; observed %s -> %s" % (fmt_opt(k_af, "%.3f"),
             "UNSCOREABLE (kappa undefined)" if k_af is None else sc(-0.05 <= k_af <= 0.35)))
    L.append("  P5b superset share(af_clean_s42) 0.85, 80%% [0.60, 1.00]; observed %s -> %s" % (fmt_opt(s_af, "%.3f"),
             "UNSCOREABLE (no J-certified site)" if s_af is None else sc(0.60 <= s_af <= 1.00)))
    p6 = all(ts[t]["dbic_pos"] >= 0.9 * ts[t]["n"] for t in names)
    L.append("  P6 dBIC > 0 on >= 90%% of the sites of every tree (p 0.75): %s -> %s"
             % (", ".join("%s %d/%d" % (t, ts[t]["dbic_pos"], ts[t]["n"]) for t in names), sc(p6)))
    s13, s14 = r13["sec"], r14["sec"]
    L.append("  P7a D5 positive at n00000013 (p 0.65): %s -> %s" % (fmt_opt(s13, "%+.5f"), "UNSCOREABLE (NA)" if s13 is None else sc(s13 > 0)))
    L.append("  P7b D5 <= 0 at n00000014 (p 0.55): %s -> %s" % (fmt_opt(s14, "%+.5f"), "UNSCOREABLE (NA)" if s14 is None else sc(s14 <= 0)))
    cpu10 = sum(ts[t]["cpu10"] for t in names) / 60.0
    L.append("  P8 the deciding p = 10 leg completes in <= %.0f CPU-min (p 0.75): %.1f CPU-min -> %s (the eigen generator as run, ruling"
             " A6; the literal-generator projection 100.9 CPU-min is disclosed beside it)" % (P8_CPU_MIN, cpu10, sc(cpu10 <= P8_CPU_MIN)))
    L.append("")
    if c1v:
        L.append("FALSIFIER F1: not scored (C1 VOID).")
    elif held:
        L.append("FALSIFIER F1 does not fire (C1 HELD). A \"mode test\" sentence additionally requires (R-a) or (R-b); none from (R-c) without D5.")
    else:
        L.append("FALSIFIER F1 FIRES (C1 FAILED [%s]): L6 closes NEGATIVE for the Gaussian mixture LR / BIC at p = 10 (\"the certificate"
                 " is geometric, not modal\"); the J site null of record stays THE certificate; nothing is rebuilt." % " + ".join(branches))
    L.append("")
    L.append("SUPPORT (the registered section, with the measured B):")
    L.append("  (a) C1 denominator: 3 sites of the frozen tree (n %s), final admitted B %s; draws independent (Kish mean cluster size 1)."
             % ("/".join(str(dec[s]["n"]) for s in DECIDING), "/".join(str(dec[s]["B"]) for s in DECIDING)))
    L.append("  (b) DEFF: C1 1 BY CONSTRUCTION (declared, not measured); D1-D6 > 1 through nesting, NOT measured.")
    for sid in DECIDING:
        B = dec[sid]["B"]
        if not B:
            L.append("  (c-e) %s: VOID" % sid)
            continue
        se = math.sqrt(0.05 * 0.95 / B)
        L.append("  (c-e) %s: n_eff %d draws; MC SE of q at the bar sqrt(0.0475/%d) = %.4f; MDE (2.80 SE) %.3f" % (sid, B, B, se, 2.80 * se))
    L.append("  (e) D3: SE lower bound 0.0706, MDE 0.198 (nesting ignored).")
    L.append("  (g) STRUCTURAL LEG: reachable; EM local optima cost power, not calibration; n 292 gives 2.2 points per parameter at p = 10.")
    L.append("  SCOPE LIMIT: the LR is invariant to linear maps ONLY INSIDE the top-p PCA subspace of each site; elongation outside"
             " those p axes and the sphere projection enter only through the generator.")
    L.append("  READINGS APPLIED: %s" % (", ".join(applied) if applied else "none"))
    return L, dict(ts=ts, c1_void=bool(c1v), held=held, branches=branches)


def sites_csv_text(summ):
    cols = ["tree", "node_id", "label", "n", "depth", "k", "VOID", "void_reason", "f_failed_null", "B_total", "B_admitted", "LR_obs",
            "q_LR", "q_LR5", "q_LR20", "dBIC", "dICL", "gain", "leaf_median_gain", "secondary", "failed_leaves", "OVERPARAM",
            "cert_LR", "cert_site_p95", "q_deflated"]
    import io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)

    def fv(x):
        return "" if x is None else ("VOID" if x == "VOID" else ("%.6f" % float(x) if isinstance(x, Fraction) else repr(x)))
    for t in [x["name"] for x in TREES]:
        for r in summ[t]:
            w.writerow([t, r["node_id"], r["label"], r["n"], r["depth"], r["k"], "true" if r["void"] else "false", r["void_reason"],
                        r["f"], r["B_total"], "" if r["B"] is None else r["B"], fv(r["LR"]), fv(r["q"]), fv(r["q5"]), fv(r["q20"]),
                        fv(r["dBIC"]), fv(r["dICL"]), fv(r["gain"]), fv(r["leaf_median"]), fv(r["sec"]), ";".join(r["leaf_fail_ids"]),
                        ";".join("p" + x for x in r["overparam"]), "true" if r["cert"] else "false",
                        "true" if r["cert_j"] else "false", r["q_defl"]])
    return buf.getvalue()


def analyze(state_dir=STATE_DIR, outcome=OUTCOME, sites_csv=SITES_CSV):
    print_header()
    for p in (outcome, sites_csv):
        if os.path.exists(p):
            refuse("%s exists: outcome files of record are WRITE-ONCE" % p)
    chunks = read_chunks(state_dir)
    if not chunks:
        refuse("no state under %s" % state_dir)
    before = table_pins()
    for k, v in before.items():
        print("[PIN before] %s %s" % (k, v))
    ensure_meta(state_dir)
    scripts = {json.dumps(ch["script"], sort_keys=True) for ch in chunks}
    if scripts != {json.dumps(script_pins(), sort_keys=True)}:
        refuse("chunks were written by another script identity: %s" % scripts)
    plan_p = os.path.join(state_dir, "plan.json")
    plan = json.load(open(plan_p, encoding="utf-8")) if os.path.exists(plan_p) else None
    sites_by_tree = {}
    for tree in TREES:
        tc = tree_contexts(tree)
        sites_by_tree[tree["name"]] = [dict(node_id=c.node_id, label=c.label, depth=c.depth, n=c.n, k=c.k, cert_j=c.cert_j,
                                            q_defl=c.q_defl, leaves=tc["site_leaves"][c.node_id]) for c in tc["ctxs"]]
    data = collect(chunks, sites_by_tree, None, plan)
    summ = {t: [summarise_site(s) for s in rows] for t, rows in data.items()}
    info = ["script %s" % fmt_pins(script_pins()), "state %s: %d chunks; plan legs p5/p20 %s"
            % (state_dir, len(chunks), "kept" if plan["legs_desc"] else "DROPPED")]
    info.extend(cost_lines(plan.get("projection"), plan))
    info.append(measured_cost_line(measured_cpu(chunks)))
    L, v = render(summ, plan["legs_desc"], info)
    txt = "\n".join(L) + "\n"
    after_pins(before)
    if v["c1_void"]:                              # VOID is a failed precondition, never an outcome (L20622)
        void_path = outcome.replace("_outcome.txt", "_VOID.txt")
        write_once(void_path, txt)
        print(txt)
        print("%s C1 VOID: no outcome of record; the failed precondition is written to %s (write-once)" % (TAG, void_path))
        return 1
    write_once(outcome, txt)
    write_once(sites_csv, sites_csv_text(summ))
    print(txt)
    print("%s wrote %s and %s (write-once)" % (TAG, outcome, sites_csv))
    return 0


# ------------------------------------------------------------------------------------------------ header / dry-run
def pool_line():
    ids = pool_guard.judgeable(pool_guard.pool_file_ids(POOL_ID))
    got = pool_guard.compute_pool_id(ids)
    if got != POOL_ID:
        refuse("the pool id file hashes to %s, not %s" % (got, POOL_ID))
    return ("pool %s (printed, not used; id file %s hashes to it via pool_guard.compute_pool_id, %d judgeable ids; the dataset DB "
            "is not opened)" % (POOL_ID, pool_guard.registry_entry(POOL_ID)["id_file"], sum(len(v) for v in ids.values())))


def threads_line():
    vals = {v: os.environ.get(v) for v in THREAD_VARS}
    return "[THREADS] " + " ".join("%s=%s" % kv for kv in vals.items())


def print_header():
    print(pool_line())
    print(threads_line())
    print("[SCRIPT] tools/analysis/mix_lrt_site.py %s" % fmt_pins(script_pins()))
    print("[DATA] DATA_ROOT %s" % DATA_ROOT)


def synthetic_cost_model():
    """Seconds per null draw cell (generator + PCA + fits) on SYNTHETIC elongated clouds; interpolated log-log in n per dim."""
    rng = np.random.default_rng(7)
    pts = {}
    warm = SiteCtx("synthetic", 0, "n00000000", "synthetic", 1, 200, 2, False, "", synth_elongated(rng, 200, 64), None, tree_index=90)
    draw_cell(warm, 0, LEGS_ALL)                  # imports and first-call overheads are not a per-draw cost
    for d, ns in ((256, (150, 400, 1000, 2500, 8125)), (512, (150, 400, 1000, 2500, 8133))):
        for n in ns:
            X = synth_elongated(rng, n, d)
            ctx = SiteCtx("synthetic", 0, "n00000000", "synthetic", 1, n, 2, False, "", X, None, tree_index=90)
            reps = 3                             # process_time ticks at 15.6 ms on Windows: average
            p10 = desc = 0.0
            for b in range(reps):
                c = draw_cell(ctx, b, LEGS_ALL)
                p10 += c["cpu"]["10"]
                desc += c["cpu"].get("5", 0) + c["cpu"].get("20", 0)
            pts[(d, n)] = dict(p10=p10 / reps, desc=desc / reps)
    return pts


def interp_cost(pts, d, n, key):
    xs = sorted(k[1] for k in pts if k[0] == d)
    ys = [pts[(d, x)][key] for x in xs]
    lx, ly = np.log(xs), np.log(np.maximum(ys, 1e-6))
    return float(np.exp(np.interp(math.log(n), lx, ly, left=None, right=None))) if xs[0] <= n <= xs[-1] else \
        float(np.exp(ly[0] + (ly[1] - ly[0]) / (lx[1] - lx[0]) * (math.log(n) - lx[0]))) if n < xs[0] else \
        float(np.exp(ly[-1] + (ly[-1] - ly[-2]) / (lx[-1] - lx[-2]) * (math.log(n) - lx[-1])))


def synth_elongated(rng, n, d, sd_top=(0.1, 0.01), sd_rest=0.004, shift=None):
    Q, _ = np.linalg.qr(rng.standard_normal((d, d)))
    mu = Q[:, 0]
    sds = np.full(d - 1, sd_rest)
    sds[:10] = np.geomspace(sd_top[0], sd_top[1], 10)
    E = rng.standard_normal((n, d - 1)) * sds
    if shift is not None:
        axis, delta, labels = shift
        E[:, axis] += np.where(labels, delta / 2, -delta / 2)
    X = mu + E @ Q[:, 1:].T
    return X / np.linalg.norm(X, axis=1, keepdims=True)


def dry_run():
    print_header()
    print("[MODE] --dry-run: reads the CSVs, the snapshot graphs and the embedding cache ONLY for counts and pins; computes NO LR,"
          " BIC, ICL, gain or q on real data; writes nothing")
    print("[PRECONDITION OWED] content closure: the data-steward confirms at the READY that the build's keyRule ck-v1 equals"
          " CK-CLOSE-v1's stem_key (split_side.KEY_RULE = %r here; not verified by this script)"
          % __import__("split_side").KEY_RULE)
    print("[PIN] registered inputs (hash kinds named; the LF rendering is of record):")
    for tree in TREES:
        p = verify_pin(os.path.join(ROOT, tree["csv"]), tree["blob"], tree["lf16"])
        ok = "OK" if p["crlf16"] == tree["crlf16"] else "MISMATCH (registered %s)" % tree["crlf16"]
        print("  %-16s %s %s | crlf16 %s" % (tree["name"], tree["csv"], fmt_pins(p), ok))
    t0 = time.perf_counter()
    pins = table_pins()
    for k, v in pins.items():
        print("[PIN table/row] %s %s" % (k, v))
    print("[PIN] %.1f s for the per-table pins (the same pins are taken before and after every --run)" % (time.perf_counter() - t0))
    plan_rows = []
    for tree in TREES:
        tc = tree_contexts(tree)
        ctxs = tc["ctxs"]
        g = tc["graph"]
        print("")
        print("TREE %s | snapshot %s from %s (graph sha256 %s) | sliceDim %d | %d sites | members == CSV n at every site: YES"
              " | %d member/leaf texts, %d vectors found"
              % (tree["name"], tree["snapshot"], g["store"], g["sha"][:16], tree["dim"], len(ctxs), tc["n_needed"], tc["n_vectors"]))
        print("  %-10s %5s %5s %2s %-5s %-24s %s" % ("site", "depth", "n", "k", "J", "OVERPARAM (n < 2k1+1)", "leaves n>=110 below"))
        for c in ctxs:
            op = [leg for leg in LEGS_ALL if c.n < k2_params(int(leg))]
            nl = sum(1 for lf, n in tc["site_leaves"][c.node_id] if n >= LEAF_MIN_N)
            print("  %-10s %5d %5d %2d %-5s %-24s %d%s" % (c.node_id, c.depth, c.n, c.k, "true" if c.cert_j else "false",
                  ",".join("p" + x for x in op) or "-", nl, "  DECIDING" if (tree["name"] == DECIDING_TREE and c.node_id in DECIDING) else ""))
        print("  OVERPARAM counts: p5 %d, p10 %d, p20 %d (registration: p10 3/2/3/2, p20 52/46/46/64)"
              % tuple(sum(1 for c in ctxs if c.n < k2_params(int(leg))) for leg in ("5", "10", "20")))
        print("  leaves with n >= %d (secondary statistic fits): %d" % (LEAF_MIN_N, len(tc["leaf_sets"])))
        plan_rows.append((tree, [c.n for c in ctxs], [x.shape[0] for x in tc["leaf_sets"].values()],
                          [c.n for c in ctxs if tree["name"] == DECIDING_TREE and c.node_id in DECIDING]))
    print("")
    print("B PLAN: p = 10 B = %d at every site; p = 5 / p = 20 on draws 0..%d (B = %d); escalation only at %s/%s when q in [0.02, 0.10]:"
          " + %d draws each (B = %d)" % (B_MAIN, B_DESC - 1, B_DESC, DECIDING_TREE, ",".join(DECIDING), B_ESC - B_MAIN, B_ESC))
    tot = 0
    for tree, ns, _, _ in plan_rows:
        print("  %-16s %d sites x %d = %d p10 cells; %d x %d = %d p5 and p20 cells" % (tree["name"], len(ns), B_MAIN, len(ns) * B_MAIN, len(ns), B_DESC, len(ns) * B_DESC))
        tot += len(ns) * B_MAIN
    print("  total %d p10 cells (+ at most %d escalation cells)" % (tot, 3 * (B_ESC - B_MAIN)))
    print("")
    print("COST (SYNTHETIC calibration of one draw cell per n, the EIGEN generator of ruling A6, single-threaded; the --run guard"
          " re-projects from the real first chunk; the literal-generator projection of e79fdb4 was 125.5 CPU-min, p10 + escalation 100.9):")
    pts = synthetic_cost_model()
    for (d, n), v in sorted(pts.items()):
        print("  synthetic d %3d n %5d: p10 leg (generator + PCA + fits) %.3f s, p5+p20 legs %.3f s" % (d, n, v["p10"], v["desc"]))
    grand = dict(p10=0.0, desc=0.0, esc=0.0, obs=0.0)
    for tree, ns, leaf_ns, dec_ns in plan_rows:
        d = tree["dim"]
        p10 = sum(interp_cost(pts, d, n, "p10") for n in ns) * B_MAIN
        desc = sum(interp_cost(pts, d, n, "desc") for n in ns) * B_DESC
        esc = sum(interp_cost(pts, d, n, "p10") for n in dec_ns) * (B_ESC - B_MAIN)
        obs = sum(interp_cost(pts, d, n, "p10") + interp_cost(pts, d, n, "desc") for n in ns) + sum(interp_cost(pts, d, n, "p10") for n in leaf_ns)
        for k, v in (("p10", p10), ("desc", desc), ("esc", esc), ("obs", obs)):
            grand[k] += v
        print("  %-16s p10 %.1f CPU-min | p5+p20 %.1f | max escalation %.1f | observed + leaves %.1f" % (tree["name"], p10 / 60, desc / 60, esc / 60, obs / 60))
    total = sum(grand.values()) / 60
    print("  PROJECTED TOTAL %.1f CPU-min (p10 %.1f + max escalation %.1f + p5/p20 %.1f + observed %.1f) against the %.0f CPU-min cap"
          " -> %s" % (total, grand["p10"] / 60, grand["esc"] / 60, grand["desc"] / 60, grand["obs"] / 60, CAP_CPU_MIN,
                      "p5/p20 legs would be DROPPED (registered order)" if total > CAP_CPU_MIN else "all legs kept"))
    print("  P8 context: the deciding p = 10 leg (with max escalation) projects to %.1f CPU-min against the predicted <= %.0f"
          % ((grand["p10"] + grand["esc"]) / 60, P8_CPU_MIN))
    print("")
    print("%s dry-run complete: zero statistics on real data, nothing written" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest
JVM_FIXTURE = """
F1 seed 20260926 n 6
0.6903137499932468 -0.2679355546765454 -0.13964183391169632 0.6214804968935478 -0.21433528713947284
0.5163627941597217 -0.18972041034310919 0.2082801164027084 0.808007734611597 -0.033444351180973435
0.613354299867399 -0.23700956860772365 0.045529855620859455 0.7421417307095041 -0.1215551356759518
0.609098722651827 -0.2417115500211481 0.04713207347262139 0.7443069292034914 -0.11983336530418905
0.5258543815281802 -0.2959831996596524 0.1057749797898453 0.7867398869786899 -0.0756512976363605
0.6034810068800049 -0.1692537556813553 0.12144161994679817 0.7644688170212531 -0.08946061295159323
F2 seed 42 n 8 MU 0.25244129544236893 0.2727892280477045 0.042336002417960164 -0.22704074859237844 -0.2876772823989415 -0.08382464945967776
C 0.1 -0.09899924966004454 0.0960170286650366 -0.0911130261884677 0.08438539587324922 -0.07596879128588213
C 0.07539022543433047 -0.08390715290764525 0.09074467814501963 -0.09576594803233847 0.09887046181866693 -0.09999608263946372
C 0.013673721820783361 -0.027516333805159693 0.0408082061813392 -0.05328330203333975 0.06469193223286404 -0.07480575296890003
C -0.05477292602242684 0.0424179007336997 -0.02921388087338362 0.015425144988758405 -0.001327674722305948 -0.012796368962740468
C -0.09626058663135667 0.09147423578045313 -0.08485702747846052 0.07654140519453434 -0.06669380616522619 0.05551133015206257
C -0.09036922050915068 0.0955073644047295 -0.09873392775238266 0.09998433086476913 -0.09923354691509288 0.09649660284921134
C -0.03999853149883513 0.052532198881772976 -0.06401443394691997 0.07421541968137826 -0.08293098328631503 0.08998668269691938
C 0.03005925437436371 -0.01629907807957055 0.0022126756261955736 0.01191801354488193 -0.02581016359382675 0.039185723042955006
C 0.08532201077225843 -0.07710802229758452 0.06735071623235862 -0.05624538512381721 0.04401430224960407 -0.030902272816607068
C 0.09858965815825498 -0.099964745596635 0.09933903797222716 -0.09672505882738824 0.09217512697247493 -0.08578030932449879
C 0.06333192030862998 -0.07361927182273159 0.08243313311075579 -0.08959709467909632 0.09496776978825433 -0.0984376643394042
C -0.003097503173121646 -0.011038724383904757 0.024954011797333815 -0.03836984449497419 0.0510177044941669 -0.06264444479103391
0.5851927974046057 0.3018941175023561 0.2406918925127591 -0.5575176198602242 -0.3216940397956153 -0.3068611947888485
0.5938250516021323 0.315398332260394 0.22741184094711847 -0.5412991819643191 -0.3589119064215936 -0.272684788222053
0.2754027559148275 0.6456193536117965 -0.09914284438967884 -0.22357245322549202 -0.668821907098137 0.01386662998258761
0.565913477555708 0.31004084351031785 0.24142735383251876 -0.5674951099101773 -0.3006655103204316 -0.3359746943289536
0.49735361028512287 0.4947285193525042 0.08718718617582769 -0.4246152439185567 -0.5482424474835047 -0.13933264675464968
0.5720116772967678 0.38289995239688623 0.17914640556568315 -0.5033695814015957 -0.4386582372317689 -0.2197608889038165
0.36970667016897546 0.5991391752362115 -0.03019819783882101 -0.30254875963831573 -0.640669363368462 -0.03800408477380045
0.36867897218995255 0.6061155911922608 -0.01310583918684942 -0.3387308424345854 -0.6109888945486542 -0.09209739236044832
G42 1.1419053154730547 0.9194079489827879 -0.9498666368908959 -1.1069902863993377 0.2809776380727795 0.6846227956326554 -0.8172214073987268 -1.3966434026780434 -0.19094451307087512 1.4862133923906502
"""


def jvm_fixture():
    """Parse the JVM output (fixture F1: literal inputs; F2: inputs printed by the JVM, so no sin/cos is recomputed here)."""
    lines = JVM_FIXTURE.strip().splitlines()
    rows = lambda ls: [[float(x) for x in l.split()] for l in ls]
    i2 = next(i for i, l in enumerate(lines) if l.startswith("F2 "))
    f1 = rows(lines[1:i2])
    head = lines[i2].split()
    mu2 = [float(x) for x in head[head.index("MU") + 1:]]
    c2 = rows([l[2:] for l in lines[i2 + 1:] if l.startswith("C ")])
    body = [l for l in lines[i2 + 1:] if not l.startswith("C ") and not l.startswith("G42 ")]
    f2 = rows(body)
    g42 = [float(x) for x in next(l for l in lines if l.startswith("G42 ")).split()[1:]]
    mu1 = [0.5, -0.25, 0.125, 0.75, -0.0625]
    c1 = [[0.1, -0.2, 0.05, 0.3, 0.0], [-0.3, 0.1, 0.2, -0.1, 0.15], [0.2, 0.1, -0.25, -0.2, -0.15], [0.0] * 5]
    if not (len(f1) == 6 and len(f2) == 8 and len(c2) == 12 and len(mu2) == 6 and len(g42) == 10):
        raise AssertionError("JVM fixture malformed")
    return (mu1, c1, 6, 20260926, f1), (mu2, c2, 8, 42, f2), g42


class _Checks(object):
    def __init__(self, quiet=False):
        self.n = 0
        self.quiet = quiet

    def ok(self, cond, what):
        self.n += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not self.quiet:
            print("  ok  " + what)


def expect_refusal(fn, needle):
    try:
        r = fn()
    except SystemExit as e:
        return needle in str(e)
    if hasattr(r, "close"):                      # an open that should have been refused: release the handle first
        r.close()
    return False


def _synthetic_summary(q13=(0, 199), q14=(50, 199), q55=(60, 199), lr_cert=None, kappa_high=False, all_cert=False, sec=(0.1, -0.1),
                       dbic_pos=True, drop=False):
    """Hand-built summarised rows for the branch tests (no fitting)."""
    summ = {}
    for t in TREES:
        rows = []
        n_sites = t["sites"]
        n_lr = lr_cert[t["name"]] if lr_cert else 0
        for i in range(n_sites):
            cert_j = i < t["j_cert"]
            if all_cert:
                cert = True
            elif kappa_high:
                cert = cert_j
            else:
                cert = i < n_lr
            sid = "n%08d" % (1000 + i)
            c, B = (0, B_MAIN) if cert else (100, B_MAIN)
            rows.append(dict(node_id=sid, label="site %d" % i, depth=1, n=300, k=2, cert_j=cert_j, q_defl="0.1", LR=10.0, c=c, B=B,
                             q=q_add_one(c, B), cert=bool(certified(q_add_one(c, B))), dBIC=(1.0 if dbic_pos else -1.0), dICL=0.5,
                             gain=0.01, leaf_median=None, sec=None, cpu10=1.0, overparam=["20"],
                             q5=None if drop else Fraction(1, 50), cert5=None if drop else True,
                             q20=None if drop else Fraction(1, 2), cert20=None if drop else False,
                             void=False, void_reason="", c1_void="", f=0, B_total=B, leaf_fail_ids=[]))
        summ[t["name"]] = rows
    fz = summ[DECIDING_TREE]
    for sid, (c, B), s in zip(DECIDING, (q13, q14, q55), (sec[0], sec[1], None)):
        q = q_add_one(c, B)
        fz.append(dict(node_id=sid, label="deciding site", depth=1, n=400, k=2, cert_j=False, q_defl="0.05", LR=5.0, c=c, B=B, q=q,
                       cert=bool(certified(q)), dBIC=1.0, dICL=0.5, gain=0.02, leaf_median=0.01, sec=s, cpu10=1.0, overparam=[],
                       q5=None if drop else Fraction(1, 2), cert5=None if drop else False,
                       q20=None if drop else Fraction(1, 2), cert20=None if drop else False,
                       void=False, void_reason="", c1_void="", f=0, B_total=B, leaf_fail_ids=[]))
    return summ


def st_branches(chk):
    def txt(**kw):
        L, _ = render(_synthetic_summary(**kw), [] if kw.get("drop") else ["5", "20"])
        return "\n".join(L)
    t = txt()
    chk.ok("C1 HELD" in t and "F1 does not fire" in t and "P1 C1 HELD (p 0.35): HELD" in t, "branch: C1 HELD, F1 not fired, P1 HELD")
    chk.ok("P2 q_LR(n00000013) = 0.005 at B = 199 (p 0.60): observed 0.0050 (= 1/200) -> HELD" in t, "branch: P2 HELD")
    chk.ok("P3 q_LR(n00000014) <= 0.05 (p 0.45): observed 0.2550 (= 51/200) -> FAILED" in t, "branch: P3 FAILED")
    t = txt(q14=(5, 199))
    chk.ok("C1 FAILED [FAILED-ALL-CERTIFY]" in t and "(R-d) APPLIES" in t and "(R-e) does not apply" in t and "F1 FIRES" in t
           and "-> HELD" in t.split("P3")[1].split("\n")[0], "branch: FAILED-ALL-CERTIFY -> R-d, F1 FIRES, P3 HELD")
    t = txt(q13=(50, 199))
    chk.ok("C1 FAILED [FAILED-NO-POWER]" in t and "(R-e) APPLIES" in t and "(R-d) does not apply" in t and "(R-f) does not apply" in t,
           "branch: FAILED-NO-POWER only -> R-e")
    chk.ok("P2 q_LR(n00000013) = 0.005 at B = 199 (p 0.60): observed 0.2550 (= 51/200) -> FAILED" in t, "branch: P2 FAILED")
    t = txt(q13=(50, 199), q55=(2, 199))
    chk.ok("C1 FAILED [FAILED-ALL-CERTIFY + FAILED-NO-POWER]" in t and "(R-f) APPLIES" in t and "(R-d) APPLIES" in t,
           "branch: both failure branches -> R-f joined, reading R-d")
    t = txt(q13=(8, 199))
    chk.ok("MC-MARGINAL at n00000013" in t, "branch: wording rule MC-MARGINAL fires when the CP interval contains 0.05")
    t = txt()
    chk.ok("no deciding site is MC-MARGINAL" in t, "branch: wording rule silent otherwise")
    t = txt(q13=(40, 999), q14=(200, 999), q55=(300, 999))
    chk.ok("1000" in t.split("n00000013")[1].split("\n")[0] and "C1 HELD" in t, "branch: C1 decided at the escalated B = 999 point")
    t = txt(all_cert=True)
    chk.ok("(R-a) APPLIES (per tree, ruling A4)" in t and "(R-c) APPLIES" in t, "branch: R-a (superset, D1 above J on every tree) and R-c (>= 90% of af sites)")
    chk.ok("NOT OF RECORD (ruling A4): pooled superset share 1.000 -> would apply" in t, "branch: the pooled R-a reading is printed beside, not of record")
    chk.ok("READINGS APPLIED: R-a, R-c" in t, "branch: applied readings listed")
    t = txt(kappa_high=True)
    chk.ok("(R-b) APPLIES" in t and "(R-a) does not apply" in t, "branch: R-b (kappa >= 0.4 on af_clean and o0_clean)")
    lr = {"frozen": 0, "af_clean_s42": 0, "o0_clean_s42": 0, "af_bareq512_s42": 0}
    t = txt(lr_cert=lr)
    chk.ok("(R-a) does not apply" in t and "(R-b) does not apply" in t and "(R-c) does not apply" in t, "branch: no positive reading")
    chk.ok("UNSCOREABLE (kappa undefined)" not in t and "P5b" in t and "-> FAILED" in t.split("P5b")[1].split("\n")[0],
           "branch: P5b FAILED (superset 0)")
    lr_in = {"frozen": 40, "af_clean_s42": 45, "o0_clean_s42": 38, "af_bareq512_s42": 55}
    t = txt(lr_cert=lr_in)
    chk.ok(all("-> HELD" in l for l in t.splitlines() if l.strip().startswith("P4")), "branch: P4 HELD on every tree")
    chk.ok(all("-> FAILED" in l for l in txt(lr_cert=lr).splitlines() if l.strip().startswith("P4")), "branch: P4 FAILED on every tree")
    # a scope-ambiguous R-a: superset >= 0.8 pooled but not on every tree
    s = _synthetic_summary(all_cert=True)
    for r in s["o0_clean_s42"]:
        if r["cert_j"]:
            r["cert"] = False
            break
    for r in s["o0_clean_s42"]:
        if r["cert_j"] and r["cert"]:
            r["cert"] = False
            break
    for r in s["o0_clean_s42"]:
        if r["cert_j"] and r["cert"]:
            r["cert"] = False
            break
    L, _ = render(s, ["5", "20"])
    t = "\n".join(L)
    chk.ok("(R-a) does not apply (per tree, ruling A4)" in t and "-> would apply]" in t and "SCOPE AMBIGUOUS" not in t,
           "branch: R-a decided per tree (ruling A4): o0 superset 8/11 < 0.8 -> not applied although the pooled reading would apply")
    t = txt(sec=(0.2, -0.1))
    chk.ok("P7a D5 positive at n00000013 (p 0.65): +0.20000 -> HELD" in t and "P7b D5 <= 0 at n00000014 (p 0.55): -0.10000 -> HELD" in t,
           "branch: P7a / P7b HELD")
    t = txt(sec=(-0.2, 0.1))
    chk.ok("P7a D5 positive at n00000013 (p 0.65): -0.20000 -> FAILED" in t and "P7b D5 <= 0 at n00000014 (p 0.55): +0.10000 -> FAILED" in t,
           "branch: P7a / P7b FAILED")
    t = txt(sec=(None, None))
    chk.ok("P7a D5 positive at n00000013 (p 0.65): NA -> UNSCOREABLE (NA)" in t, "branch: P7 UNSCOREABLE when D5 is NA")
    chk.ok("P6 dBIC > 0" in txt() and "-> HELD" in txt().split("P6")[1].split("\n")[0], "branch: P6 HELD")
    chk.ok("-> FAILED" in txt(dbic_pos=False).split("P6")[1].split("\n")[0], "branch: P6 FAILED")
    chk.ok("P8 the deciding p = 10 leg completes in <= 60 CPU-min (p 0.75): 4.8 CPU-min -> HELD" in txt(), "branch: P8 HELD")
    s = _synthetic_summary()
    for t_ in s.values():
        for r in t_:
            r["cpu10"] = 20.0
    chk.ok("-> FAILED" in "\n".join(render(s, ["5", "20"])[0]).split("P8")[1].split("\n")[0], "branch: P8 FAILED")
    chk.ok("D6 frozen           p = 5 / p = 20: DROPPED" in txt(drop=True), "branch: D6 printed as DROPPED under the cost guard")
    chk.ok("D6 frozen           certified at B = 49" in txt(), "branch: D6 counts when kept")
    s = _synthetic_summary(lr_cert=lr)
    for t_ in s.values():
        for r in t_:
            r["cert_j"] = False
    L, ts = render(s, ["5", "20"])
    t = "\n".join(L)
    chk.ok("UNSCOREABLE (kappa undefined)" in t and "UNSCOREABLE (no J-certified site)" in t, "branch: P5 UNSCOREABLE when undefined")
    chk.ok("P5a" in txt(kappa_high=True) and "-> FAILED" in txt(kappa_high=True).split("P5a")[1].split("\n")[0], "branch: P5a FAILED (kappa 1)")
    t = txt(lr_cert={"frozen": 3, "af_clean_s42": 2, "o0_clean_s42": 2, "af_bareq512_s42": 5})
    chk.ok("-> HELD" in t.split("P5a")[1].split("\n")[0], "branch: P5a HELD")
    chk.ok("-> HELD" in txt(kappa_high=True).split("P5b")[1].split("\n")[0], "branch: P5b HELD")


ST2_SEP_SD = 8.0     # registration: "separated along one axis by >= 4 within-SD"; at the floor (4) the LR has ~no power at
#                      n 400 / p 10 on this fixture (see --power-probe), so the fixture sits at 8; REPORTED to the registrar.


def st_heavy(chk, which, n_clouds=20, B=99, sep_sd=ST2_SEP_SD):
    """ST1 elongated one-mode, ST-ISO isotropic one-mode, ST2 two modes: 20 clouds each, d 256, n 400, B = 99."""
    rng = np.random.default_rng({"ST1": 101, "ISO": 202, "ST2": 303}[which])
    cert = 0
    for k in range(n_clouds):
        if which == "ST1":
            X = synth_elongated(rng, 400, 256)
        elif which == "ISO":
            X = synth_elongated(rng, 400, 256, sd_top=(0.02, 0.02), sd_rest=0.02)
        else:
            labels = np.arange(400) < 200
            sd_axis = np.geomspace(0.1, 0.01, 10)[3]
            X = synth_elongated(rng, 400, 256, shift=(3, sep_sd * sd_axis, labels))
        ctx = SiteCtx("synthetic", 5000 + k, "n%08d" % k, "synthetic", 1, 400, 2, False, "", X, None, tree_index=91)
        o = obs_cell(ctx)["p10"]["LR"]
        null = [draw_cell(ctx, b, ("10",))["lr10"] for b in range(B)]
        cert += int(certified(q_add_one(exceed_count(null, o), B)))
    return cert


def selftest(only=None, quiet=False, heavy=True):
    chk = _Checks(quiet)
    sel = (lambda name: only is None or name in only)
    if sel("ST7"):
        chk.ok(all(os.environ.get(v) == "1" for v in THREAD_VARS), "ST7 %s" % threads_line())
        try:
            from threadpoolctl import threadpool_info
            chk.ok(all(i.get("num_threads") == 1 for i in threadpool_info()), "ST7 threadpoolctl: every BLAS/OpenMP pool has 1 thread")
        except ImportError:
            chk.ok(True, "ST7 threadpoolctl not installed; environment variables checked")
    if sel("ST-JVM"):
        (mu1, c1, n1, s1, f1), (mu2, c2, n2, s2, f2), g42 = jvm_fixture()
        jr = JavaRandom(42)
        chk.ok([jr.next_gaussian() for _ in range(10)] == g42, "ST-JVM java.util.Random(42).nextGaussian x10 reproduced bit for bit")
        for tag, mu, cen, n, seed, ref in (("F1", mu1, c1, n1, s1, f1), ("F2", mu2, c2, n2, s2, f2)):
            lit = within_node_cloud_loop(mu, cen, n, JavaRandom(seed).next_gaussian)
            dev = max(abs(a - b) for ra, rb in zip(lit, ref) for a, b in zip(ra, rb))
            chk.ok(dev == 0.0, "ST-JVM %s: the literal transcription reproduces the COMPILED Kotlin withinNodeCloud BIT FOR BIT (max |dev| %.1e)" % (tag, dev))
            jr = JavaRandom(seed)
            G = np.array([[jr.next_gaussian() for _ in range(len(cen))] for _ in range(n)])

            class _FeedG(object):
                def __init__(self, G):
                    self.G, self.i = G, 0

                def standard_normal(self, shape):
                    out = self.G[self.i:self.i + shape[0]]
                    self.i += shape[0]
                    return out
            vec = within_node_cloud(np.array(mu), np.array(cen), n, _FeedG(G), block=3)
            dev = float(np.max(np.abs(vec - np.array(ref))))
            chk.ok(dev <= 1e-12, "ST-JVM %s: the vectorised production form fed the same Gaussians agrees (max |dev| %.1e)" % (tag, dev))
    if sel("ST3"):
        rng = np.random.default_rng(3)
        C0 = rng.standard_normal((30, 5)) * np.array([1.0, 0.5, 0.2, 0.1, 0.05])
        C0 -= C0.mean(axis=0)
        mu = np.array([1.0, 0.2, -0.1, 0.0, 0.3])
        Y = within_node_cloud(mu, C0, 200000, np.random.default_rng(4), normalise=False)
        cov_formula = C0.T @ C0 / C0.shape[0]
        chk.ok(np.max(np.abs(Y.mean(axis=0) - mu)) < 5e-3, "ST3 draw mean matches mu to MC tolerance")
        chk.ok(np.max(np.abs(np.cov(Y, rowvar=False, bias=True) - cov_formula)) < 0.02 * np.max(np.abs(cov_formula)),
               "ST3 draw covariance matches C^T C / m to MC tolerance (2% of the largest entry)")
        Yn = within_node_cloud(mu, C0, 1000, np.random.default_rng(5))
        chk.ok(np.max(np.abs(np.linalg.norm(Yn, axis=1) - 1)) < 1e-12, "ST3 every generated row has unit norm")
        a = within_node_cloud(mu, C0, 1000, np.random.default_rng(6), block=7)
        b = within_node_cloud(mu, C0, 1000, np.random.default_rng(6), block=1024)
        chk.ok(np.array_equal(a, b), "ST3 row-blocked generation is bit-identical to one block (the stream is sequential)")
        _, s0, Vt0 = np.linalg.svd(C0, full_matrices=False)
        Ye = within_node_cloud_eigen(mu, s0, Vt0, C0.shape[0], 200000, np.random.default_rng(14), normalise=False)
        chk.ok(np.max(np.abs(Ye.mean(axis=0) - mu)) < 5e-3, "ST3-eigen draw mean matches mu to MC tolerance")
        chk.ok(np.max(np.abs(np.cov(Ye, rowvar=False, bias=True) - cov_formula)) < 0.02 * np.max(np.abs(cov_formula)),
               "ST3-eigen draw covariance matches C^T C / m to MC tolerance (2% of the largest entry)")
        pv = ((Ye - mu) @ Vt0.T).var(axis=0)
        ev = s0 ** 2 / C0.shape[0]
        chk.ok(float(np.max(np.abs(pv / ev - 1))) < 0.03, "ST3-eigen the variance along EVERY principal axis (smallest included) is s_i^2 / m"
               " within 3%% relative (max %.4f)" % float(np.max(np.abs(pv / ev - 1))))
        Yen = within_node_cloud_eigen(mu, s0, Vt0, C0.shape[0], 1000, np.random.default_rng(15))
        chk.ok(np.max(np.abs(np.linalg.norm(Yen, axis=1) - 1)) < 1e-12, "ST3-eigen every generated row has unit norm")
        a = within_node_cloud_eigen(mu, s0, Vt0, C0.shape[0], 1000, np.random.default_rng(16), block=7)
        b = within_node_cloud_eigen(mu, s0, Vt0, C0.shape[0], 1000, np.random.default_rng(16), block=1024)
        chk.ok(np.array_equal(a, b), "ST3-eigen row-blocked generation is bit-identical to one block")
    if sel("ST-EQ"):
        st_eq(chk)
    elif sel("ST-EQ3"):
        st_eq3(chk)
    if sel("ST4"):
        chk.ok(q_add_one(0, 199) == Fraction(1, 200) and q_add_one(9, 199) == Fraction(1, 20), "ST4 q = (1 + count)/(B + 1): 0 -> 0.005, 9 -> 0.05")
        chk.ok(certified(q_add_one(9, 199)) and not certified(q_add_one(10, 199)), "ST4 certified iff q <= 0.05 (9 of 199 certifies, 10 does not)")
        chk.ok(certified(q_add_one(49, 999)) and not certified(q_add_one(50, 999)), "ST4 at B = 999: 49 certifies, 50 does not")
        chk.ok(certified(q_add_one(1, 49)) and not certified(q_add_one(2, 49)), "ST4 at B = 49: 1 certifies, 2 does not")
        chk.ok(in_escalation_band(q_add_one(3, 199)) and not in_escalation_band(q_add_one(2, 199)), "ST4 band lower edge inclusive (q 0.02 in, 0.015 out)")
        chk.ok(in_escalation_band(q_add_one(19, 199)) and not in_escalation_band(q_add_one(20, 199)), "ST4 band upper edge inclusive (q 0.10 in, 0.105 out)")
        chk.ok(escalates("frozen", "n00000014", q_add_one(5, 199)), "ST4 a deciding site in the band escalates")
        chk.ok(not escalates("frozen", "n00000006", q_add_one(5, 199)) and not escalates("af_clean_s42", "n00000014", q_add_one(5, 199)),
               "ST4 no other site (nor the same id on another tree) escalates")
        chk.ok(not escalates("frozen", "n00000013", q_add_one(0, 199)), "ST4 a deciding site outside the band does not escalate")
        chk.ok(B_ESC - B_MAIN == 800 and B_DESC == 49 and B_MAIN == 199, "ST4 B = 199, escalation +800 to B = 999, descriptive B = 49")
        chk.ok(legs_after_guard(80.0) == LEGS_ALL and legs_after_guard(80.01) == ("10",), "ST4 drop order: above 80 CPU-min p5/p20 drop, p10 stays")
        chk.ok("10" in legs_after_guard(1e9), "ST4 the p = 10 leg is never dropped")
        chk.ok(k2_params(10) == 131 and k2_params(20) == 461 and k2_params(5) == 41, "ST4 parameter counts 131 (p10), 461 (p20), 41 (p5)")
        chk.ok(q_admitted(3, 199, 1) == Fraction(4, 199) and q_admitted(3, 199, 0) == Fraction(4, 200),
               "ST4 q over admitted draws (ruling A3 (ii)): (1 + c) / (B - f + 1)")
        lo, hi = clopper_pearson(0, 199)
        chk.ok(lo == 0.0 and abs(hi - (1 - 0.025 ** (1 / 199))) < 1e-9, "ST4 Clopper-Pearson at 0 of 199: [0, 1 - 0.025^(1/199)]")
    if sel("ST-PCA"):
        st_pca(chk)
    if sel("ST-REG"):
        st_reg(chk)
    if sel("ST-L1"):
        from scipy.stats import multivariate_normal
        rng = np.random.default_rng(9)
        Z = rng.standard_normal((300, 4)) @ rng.standard_normal((4, 4))
        S = np.cov(Z, rowvar=False, bias=True)
        ref = float(multivariate_normal(Z.mean(axis=0), S).logpdf(Z).sum())
        chk.ok(abs(loglik_k1(Z) - ref) < 1e-8 * abs(ref), "ST-L1 the k = 1 closed-form MLE log-likelihood equals scipy's")
    if sel("ST-INV"):
        rng = np.random.default_rng(11)
        Z = np.vstack([rng.standard_normal((150, 6)), rng.standard_normal((150, 6)) + np.array([6, 0, 0, 0, 0, 0])])
        A = rng.standard_normal((6, 6)) + 3 * np.eye(6)
        s0, s1 = lr_stats(Z, 5), lr_stats(Z @ A, 5)
        chk.ok(abs(s0["LR"] - s1["LR"]) < 1e-4 * abs(s0["LR"]), "ST-INV full-covariance LR invariant under an invertible linear map (%.4f vs %.4f)"
               % (s0["LR"], s1["LR"]))
        chk.ok(abs(s0["dICL"] - (s0["dBIC"] - 2 * s0["ent"])) < 1e-9 and s0["ent"] >= 0, "ST-ICL dICL = dBIC - 2 x entropy, entropy >= 0")
        n, p = Z.shape
        chk.ok(abs(s0["dBIC"] - (s0["LR"] - (k2_params(p) - k1_params(p)) * math.log(n))) < 1e-8, "ST-BIC dBIC = LR - (k2 - k1) log n")
    if sel("ST-SEC"):
        chk.ok(secondary(0.5, [(120, 0.1), (50, 9.0), (200, 0.3)]) == 0.5 - 0.2, "ST-SEC median over leaves with n >= 110 only")
        chk.ok(secondary(0.5, [(109, 0.1)]) is None and secondary(None, [(200, 0.1)]) is None, "ST-SEC NA without an eligible leaf")
    if sel("ST-REGION"):
        byid = {"a": dict(childIds=["b", "c"], queryIds=["x0"]), "b": dict(childIds=["d"], queryIds=["x1", "x2"]),
                "c": dict(childIds=["d", "e"], queryIds=[]), "d": dict(childIds=[], queryIds=["x3", "x1"]),
                "e": dict(childIds=["zz"], queryIds=["x4"])}
        chk.ok(region_query_ids("a", byid) == ["x0", "x4", "x3", "x1", "x2"], "ST-REGION regionQueryIds order and DAG de-duplication (LIFO, seen-set)")
        chk.ok(descendant_leaves("a", byid) == ["d", "e"], "ST-REGION descendant leaves (a node whose children are all unknown is a leaf)")
    if sel("ST6"):
        vm = {"q1": ("b", np.array([1.0, 0])), "q2": ("a", np.array([0, 1.0]))}
        chk.ok(expect_refusal(lambda: prepare_members(["q1", "q2"], vm, 3, "t/s"), "membership-count mismatch"),
               "ST6 a membership-count mismatch REFUSES")
        chk.ok(expect_refusal(lambda: prepare_members(["q1", "q3"], vm, 2, "t/s"), "have no embedding"), "ST6 a missing vector REFUSES")
        X, order = prepare_members(["q1", "q2"], vm, 2, "t/s")
        chk.ok(order == ["q2", "q1"] and X[0, 1] == 1.0, "ST6 rows sorted by (text, id)")
    if sel("ST-PIN"):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.csv")
            with open(p, "wb") as f:
                f.write(b"a,b\r\n1,2\r\n")
            good = pins_of_bytes(b"a,b\n1,2\n")
            chk.ok(verify_pin(p, good["blob"], good["lf16"])["crlf16"] == good["crlf16"], "ST-PIN a CRLF file verifies against its LF pins")
            chk.ok(expect_refusal(lambda: verify_pin(p, good["blob"], "0" * 16), "pin mismatch"), "ST-PIN a pin mismatch REFUSES")
            q = os.path.join(td, "o.txt")
            write_once(q, "a")
            chk.ok(isinstance(_raises(lambda: write_once(q, "b")), FileExistsError), "ST-WO a second write of an outcome file REFUSES")
    if sel("ST-GUARD"):
        chk.ok(expect_refusal(lambda: sqlite3.connect("file:embeddings_cache.db?mode=ro", uri=True), "only mode=ro&immutable=1"),
               "ST-GUARD a mode=ro open without immutable=1 REFUSES")
        chk.ok(expect_refusal(lambda: sqlite3.connect("x.db"), "not a file: URI"), "ST-GUARD a plain path REFUSES")
        chk.ok(expect_refusal(lambda: sqlite3.connect("file:ratings.db?mode=ro&immutable=1", uri=True), "not a DB this test reads"),
               "ST-GUARD a DB outside the three this test reads REFUSES")
    if sel("ST5"):
        rng = np.random.default_rng(21)
        ctxs = [SiteCtx("syn", i, "n%08d" % (100 + i), "s", 1, 150, 2, False, "", synth_elongated(rng, 150, 32), None, tree_index=92) for i in range(2)]
        by = {c.node_id: c for c in ctxs}
        tasks = [(c.node_id, b) for b in range(5) for c in ctxs]

        def comp(t):
            return draw_cell(by[t[0]], t[1], LEGS_ALL if t[1] < 3 else ("10",))
        with tempfile.TemporaryDirectory() as td:
            a_dir, b_dir = os.path.join(td, "a"), os.path.join(td, "b")
            run_chunk(a_dir, "syn", "draws", tasks, comp, "m", budget_s=float("inf"), group_of=lambda t: t[1])
            rest = list(tasks)
            while rest:
                k = run_chunk(b_dir, "syn", "draws", rest, comp, "m", budget_s=float("inf"), max_cells=4, group_of=lambda t: t[1])
                rest = rest[k:]
            A = sorted((json.dumps(strip_timing(c), sort_keys=True) for ch in read_chunks(a_dir) for c in ch["cells"]))
            Bc = sorted((json.dumps(strip_timing(c), sort_keys=True) for ch in read_chunks(b_dir) for c in ch["cells"]))
            chk.ok(len(read_chunks(b_dir)) == 3 and len(read_chunks(a_dir)) == 1, "ST5 chunking: one pass = 1 chunk, capped = 3 chunks")
            chk.ok(A == Bc and len(A) == 10, "ST5 a chunked run equals a single-pass run bit for bit (10 cells, every float)")
            one = draw_cell(by["n00000101"], 4, ("10",))
            chk.ok(json.dumps(strip_timing(one), sort_keys=True) in A, "ST5 a cell recomputed alone is identical (order-free streams)")
            lrs = [c["lr10"] for ch in read_chunks(a_dir) for c in ch["cells"] if c["site"] == "n00000101"]
            chk.ok(len(set(lrs)) == 5, "ST5 the five draws of a site are distinct (each b has its own child stream)")
        twin = SiteCtx("syn", 1, "n00000101", "s", 1, 150, 2, False, "", by["n00000101"].X, None, tree_index=93)
        chk.ok(draw_cell(twin, 4, ("10",))["lr10"] != one["lr10"], "ST5 row r of two different trees draws different streams (ruling A1)")
        chk.ok(list(draw_stream(0, 5, 7).generate_state(4)) != list(draw_stream(1, 5, 7).generate_state(4))
               and list(site_stream(0, 5).generate_state(4)) != list(site_stream(1, 5).generate_state(4)),
               "ST5 site and draw SeedSequences differ across tree_index at the same (row, b)")
        chk.ok(list(leaf_stream(0, "n00000013").generate_state(4)) != list(leaf_stream(1, "n00000013").generate_state(4))
               and tuple(leaf_stream(2, "n00000013").spawn_key) == (2, 1000013), "ST5 leaf streams keyed (tree_index, 1000000 + node) (ruling A2)")
    if sel("ST-COMPLETE"):
        _st_complete(chk)
    if sel("ST-COST"):
        st_cost(chk)
    if sel("ST-ESC"):
        st_esc(chk)
    if sel("ST-ROUTE"):
        st_route(chk)
    if sel("ST-FAIL"):
        st_fail(chk)
    if sel("ST-BRANCH"):
        st_branches(chk)
    if heavy and sel("ST1"):
        c = st_heavy(chk, "ST1")
        chk.ok(c <= 3, "ST1 elongated single Gaussian (d 256, n 400, top-10 condition number 100): certified on %d of 20 (<= 3)" % c)
    if heavy and sel("ISO"):
        c = st_heavy(chk, "ISO")
        chk.ok(c <= 3, "ST1b isotropic single Gaussian: certified on %d of 20 (<= 3)" % c)
    if heavy and sel("ST2"):
        c = st_heavy(chk, "ST2")
        chk.ok(c >= 18, "ST2 two Gaussians %g within-SD apart (registered floor 4), 0.5/0.5, the ST1 noise: certified on %d of 20 (>= 18)"
               % (ST2_SEP_SD, c))
    return chk.n


def _raises(fn):
    try:
        fn()
    except BaseException as e:
        return e
    return None


def st_cost(chk):
    """MIX-FLAT-SELFTEST-GAPS D3: the post-drop projection and the MEASURED CPU are printed against the cap, both branches."""
    pr = dict(p10=70.0, esc=4.6, desc=20.7, obs=0.9, total=96.2)
    chk.ok(abs(post_drop_total(pr) - 75.5) < 1e-12, "ST-COST post-drop = p10 + escalation + observed (70.0 + 4.6 + 0.9 = 75.5)")
    L = cost_lines(pr, dict(legs_desc=[]))
    chk.ok(len(L) == 2 and "OVER: p5/p20 legs DROPPED" in L[0] and "= 75.5 CPU-min against the 80 CPU-min cap -> within the cap" in L[1],
           "ST-COST pre-drop OVER, post-drop within: both printed")
    L = cost_lines(dict(pr, p10=80.0, total=106.2), dict(legs_desc=[]))
    chk.ok("-> OVER the cap even after the drop" in L[1], "ST-COST post-drop OVER printed")
    L = cost_lines(dict(p10=40.0, esc=4.0, desc=10.0, obs=1.0, total=55.0), dict(legs_desc=["5", "20"]))
    chk.ok("within budget | plan.json: legs 5/20" in L[0] and "within the cap" in L[1], "ST-COST within budget, legs kept")
    chk.ok(cost_lines(None, None) == ["[COST] not yet measured (the first draws chunk of every tree is pending); budget 80 CPU-min"],
           "ST-COST nothing measured yet: one line")
    chunks = [dict(kind="obs", cells=[dict(site="a", cpu={"10": 60.0})]),
              dict(kind="draws", cells=[dict(site="a", b=0, cpu={"10": 30.0, "5": 6.0, "20": 6.0}), dict(site="a", b=1, cpu={"10": 30.0})]),
              dict(kind="leaf", cells=[dict(leaf="l", cpu={"10": 12.0})])]
    m = measured_cpu(chunks)
    chk.ok(abs(m["p10"] - 2.0) < 1e-12 and abs(m["desc"] - 0.2) < 1e-12 and abs(m["leaf"] - 0.2) < 1e-12 and abs(m["total"] - 2.4) < 1e-12,
           "ST-COST measured CPU: p10 (observed + draws) 2.0, p5/p20 0.2, leaves 0.2, total 2.4 CPU-min")
    chk.ok("-> within the cap" in measured_cost_line(m) and "-> OVER the cap" in measured_cost_line(m, cap=2.0),
           "ST-COST measured line: within / OVER branches")


def st_esc(chk):
    """MIX-FLAT-SELFTEST-GAPS D6 (READY dde660e, mutants R4c / R4d): run()'s escalation decision, escalation_tasks, executed."""
    def chunks(sid, hi=0, fail=0, missing=None, esc_done=0, obs_ok=True, tree="frozen"):
        obs = [dict(site=sid, n=10, gain=0.1, cpu={"10": 0.0}, p10=dict(ok=obs_ok, LR=1.0))]
        cells = []
        for b in range(B_MAIN + esc_done):
            if b == missing:
                continue
            if b < fail:
                cells.append(dict(site=sid, b=b, lr10=None, ok10=False, cpu={"10": 0.0}))
            else:
                cells.append(dict(site=sid, b=b, lr10=(2.0 if b < fail + hi else 0.0), ok10=True, cpu={"10": 0.0}))
        return [dict(kind="obs", tree=tree, cells=obs), dict(kind="draws", tree=tree, cells=cells)]
    sid = DECIDING[1]
    t = escalation_tasks(chunks(sid, hi=5), "frozen", sid)
    chk.ok(t == [(sid, b) for b in range(B_MAIN, B_ESC)], "ST-ESC q = 6/200 (in the band) at a deciding site: the 800 escalation draws")
    t = escalation_tasks(chunks(sid, hi=5, esc_done=200), "frozen", sid)
    chk.ok(t == [(sid, b) for b in range(B_MAIN + 200, B_ESC)], "ST-ESC resumable: 200 escalation draws done -> the other 600")
    chk.ok(escalation_tasks(chunks(sid, hi=0), "frozen", sid) == [], "ST-ESC q = 1/200 (below the band) at a deciding site: none (R4c)")
    chk.ok(escalation_tasks(chunks(sid, hi=30), "frozen", sid) == [], "ST-ESC q = 31/200 (above the band) at a deciding site: none (R4c)")
    chk.ok(escalation_tasks(chunks(sid, hi=5, missing=57), "frozen", sid) == [], "ST-ESC a main draw missing: none yet")
    chk.ok(escalation_tasks(chunks(sid, hi=5, obs_ok=False), "frozen", sid) == [], "ST-ESC a failed observed fit (q not computable): none")
    chk.ok(escalation_tasks(chunks("n00000006", hi=5), "frozen", "n00000006") == [], "ST-ESC a non-deciding site in the band: none")
    chk.ok(escalation_tasks(chunks(sid, hi=5, tree="af_clean_s42"), "af_clean_s42", sid) == [], "ST-ESC the same id on another tree: none")
    chk.ok(escalation_tasks(chunks(sid, hi=19, fail=0), "frozen", sid) != [], "ST-ESC 19 exceedances, f = 0: q = 20/200 = 0.10, in the band")
    chk.ok(escalation_tasks(chunks(sid, hi=19, fail=1), "frozen", sid) == [],
           "ST-ESC 19 exceedances, f = 1: q over the ADMITTED draws 20/199 > 0.10, no escalation (R4d: q199 must count f)")


def _st_complete(chk):
    sites = {"frozen": [dict(node_id=s, label=s, depth=1, n=10, k=2, cert_j=False, q_defl="", leaves=[]) for s in DECIDING]}

    def chunks_for(B_of, drop_cell=None, dup=False, extra=False):
        cells_obs = [dict(site=s, n=10, gain=0.1, cpu={"10": 0.0},
                          p10=dict(ok=True, LR=1.0, dBIC=1, dICL=1), p5=dict(ok=True, LR=1.0), p20=dict(ok=True, LR=1.0)) for s in DECIDING]
        cells = []
        for s in DECIDING:
            for b in range(B_of[s] + (1 if extra and s == DECIDING[0] else 0)):
                if drop_cell == (s, b):
                    continue
                lr = 2.0 if b < B_of.get(s + "_hi", 0) else 0.0
                cells.append(dict(site=s, b=b, lr10=lr, ok10=True, lr5=None, lr20=None, cpu={"10": 0.0}))
        if dup:
            cells.append(dict(cells[0]))
        return [dict(kind="obs", tree="frozen", cells=cells_obs), dict(kind="draws", tree="frozen", cells=cells)]
    plan = dict(legs_desc=[])
    base = {s: B_MAIN for s in DECIDING}
    chk.ok(set(collect(chunks_for(base), sites, None, plan)) == {"frozen"}, "ST-COMPLETE a complete design is accepted")
    chk.ok(expect_refusal(lambda: collect(chunks_for(base, drop_cell=(DECIDING[1], 57)), sites, None, plan), "draw 57 is missing"),
           "ST-COMPLETE a missing draw REFUSES")
    chk.ok(expect_refusal(lambda: collect(chunks_for(base, dup=True), sites, None, plan), "more than once"),
           "ST-COMPLETE a duplicated cell REFUSES")
    chk.ok(expect_refusal(lambda: collect(chunks_for(base, extra=True), sites, None, plan), "beyond the registered B"),
           "ST-COMPLETE a draw beyond the registered B REFUSES")
    esc = dict(base)
    esc[DECIDING[1] + "_hi"] = 5                  # 5 of 199 null LRs above the observed: q = 6/200 = 0.03, in the band
    chk.ok(expect_refusal(lambda: collect(chunks_for(esc), sites, None, plan), "escalation draw 199 is missing"),
           "ST-COMPLETE an in-band deciding site without its 800 escalation draws REFUSES")
    esc[DECIDING[1]] = B_ESC
    got = collect(chunks_for(esc), sites, None, plan)
    chk.ok(len([r for r in got["frozen"] if r["node_id"] == DECIDING[1]][0]["null"]["10"]) == B_ESC,
           "ST-COMPLETE the escalated site is read at B = 999")
    chk.ok(expect_refusal(lambda: collect(chunks_for(base), sites, None, None), "plan.json is missing"), "ST-COMPLETE no plan REFUSES")



ST_EQ_ALPHA = 0.01          # ST-EQ bar, FIXED BEFORE ITS FIRST EXECUTION (2026-09-26): the two-sample KS test must not reject at 0.01
ST_EQ_B = 199               # draws per generator (independent streams)
ST_EQ_MEAN_SE = 5.0         # moments bar: |mean diff| <= 5 MC SE; covariance within 2% (vs formula) and 3% (between forms) of max |cov|


def _lr10_of(Y, rs):
    Yc, Vt = pca_basis(Y)
    return lr_stats(Yc @ Vt[:10].T, rs)["LR"]


class _FeedGauss(object):
    """A stand-in Generator whose standard_normal hands out the rows of a fixed matrix in order (ST-EQ (iii))."""
    def __init__(self, G):
        self.G, self.i = G, 0

    def standard_normal(self, shape):
        out = self.G[self.i:self.i + shape[0]]
        if out.shape != tuple(shape):
            raise AssertionError("fixture exhausted or mis-shaped: asked %s, have %s" % (shape, out.shape))
        self.i += shape[0]
        return out


ST_EQ3_TOL = 1e-12          # ST-EQ (iii) bar (MIX-FLAT-SELFTEST-GAPS D4; the READY's own identity measured max 3.3e-16)


def st_eq3(chk):
    """MIX-FLAT-SELFTEST-GAPS D4 (READY dde660e): the DRAW-FOR-DRAW identity that carries ruling A6's equivalence. With
    C = U diag(s) V^T the thin SVD of the centred members, G C = (G U) diag(s) V^T, so the literal generator fed G equals the eigen
    generator fed Z = G U to rounding. Four fixtures (m < d 110 x 256, 400 x 256, m > d 1200 x 512, 30 x 5), normalised and not;
    both PRODUCTION functions are fed through a stand-in Generator (the block boundaries differ on purpose)."""
    rng = np.random.default_rng(71)
    for m, d in ((110, 256), (400, 256), (1200, 512), (30, 5)):
        C = synth_elongated(rng, m, d) if d >= 20 else rng.standard_normal((m, d)) * np.linspace(1.0, 0.05, d)
        C = C - C.mean(axis=0)
        mu = rng.standard_normal(d)
        mu /= np.linalg.norm(mu)
        U, sv, Vt = np.linalg.svd(C, full_matrices=False)
        n = 37
        G = rng.standard_normal((n, m))
        for norm in (False, True):
            lit = within_node_cloud(mu, C, n, _FeedGauss(G), block=5, normalise=norm)
            eig = within_node_cloud_eigen(mu, sv, Vt, m, n, _FeedGauss(G @ U), block=8, normalise=norm)
            dev = float(np.max(np.abs(lit - eig)))
            chk.ok(dev <= ST_EQ3_TOL, "ST-EQ (iii) literal(G) == eigen(G U) draw for draw, m %d d %d%s: max |dev| %.1e (bar %.0e)"
                   % (m, d, ", unit-normalised" if norm else "", dev, ST_EQ3_TOL))


def st_eq(chk):
    """Ruling A6: the eigen generator is exact in distribution with the literal, bit-verified one. (i) moments on the JVM F2
    fixture; (ii) a two-sample KS test on the p = 10 LR null of a synthetic site, 199 draws each, independent streams (about
    alpha power against tail-only or scale defects: READY dde660e D4); (iii) the draw-for-draw identity (st_eq3), which carries
    the equivalence."""
    st_eq3(chk)
    (_, _, _, _, _), (mu2, c2, _, _, _), _ = jvm_fixture()
    mu, C = np.array(mu2), np.array(c2)
    m = C.shape[0]
    _, sv, Vt = np.linalg.svd(C, full_matrices=False)
    N = 200000
    Yl = within_node_cloud(mu, C, N, np.random.default_rng(31), normalise=False)
    Ye = within_node_cloud_eigen(mu, sv, Vt, m, N, np.random.default_rng(32), normalise=False)
    cov = C.T @ C / m
    se = math.sqrt(float(np.max(np.diag(cov))) / N)
    chk.ok(np.max(np.abs(Ye.mean(axis=0) - mu)) <= ST_EQ_MEAN_SE * se and np.max(np.abs(Yl.mean(axis=0) - mu)) <= ST_EQ_MEAN_SE * se
           and np.max(np.abs(Ye.mean(axis=0) - Yl.mean(axis=0))) <= ST_EQ_MEAN_SE * math.sqrt(2) * se,
           "ST-EQ (i) on the JVM F2 fixture: eigen and literal means agree with mu and each other within %.0f MC SE" % ST_EQ_MEAN_SE)
    ce, cl = np.cov(Ye, rowvar=False, bias=True), np.cov(Yl, rowvar=False, bias=True)
    big = float(np.max(np.abs(cov)))
    chk.ok(np.max(np.abs(ce - cov)) <= 0.02 * big and np.max(np.abs(cl - cov)) <= 0.02 * big and np.max(np.abs(ce - cl)) <= 0.03 * big,
           "ST-EQ (i) covariances: eigen and literal within 2%% of C^T C / m and 3%% of each other (max |dev| %.2e / %.2e)"
           % (np.max(np.abs(ce - cov)), big))
    from scipy.stats import ks_2samp
    ctx = SiteCtx("syn", 0, "n00000001", "s", 1, 150, 2, False, "", synth_elongated(np.random.default_rng(33), 150, 64), None, tree_index=95)
    lr_e, lr_l = [], []
    for b in range(ST_EQ_B):
        r1 = np.random.default_rng(draw_stream(95, 0, b))
        Y = within_node_cloud_eigen(ctx.mu, ctx.s, ctx.Vt, ctx.C.shape[0], ctx.n, r1)
        lr_e.append(_lr10_of(Y, r1.integers(0, 2 ** 31 - 1)))
        r2 = np.random.default_rng(draw_stream(96, 0, b))
        Y = within_node_cloud(ctx.mu, ctx.C, ctx.n, r2)
        lr_l.append(_lr10_of(Y, r2.integers(0, 2 ** 31 - 1)))
    ks = ks_2samp(lr_e, lr_l)
    chk.ok(ks.pvalue >= ST_EQ_ALPHA, "ST-EQ (ii) two-sample KS on the p = 10 LR null (n 150, d 64, %d + %d draws): D %.4f, p %.4f >= bar %.2f "
           "(bar fixed in the code before the first run); medians %.2f / %.2f" % (ST_EQ_B, ST_EQ_B, ks.statistic, ks.pvalue, ST_EQ_ALPHA,
                                                                                   float(np.median(lr_e)), float(np.median(lr_l))))


def _fail_fixture(fail10=(), obs_fail=(), fail20=(), leaf_fail=(), extra_site="n00000006"):
    """Synthetic chunks for ruling A3: frozen with the three deciding sites + one ordinary site that has two eligible leaves."""
    sites_ = list(DECIDING) + [extra_site]
    sites = {"frozen": [dict(node_id=x, label=x, depth=1, n=300, k=2, cert_j=False, q_defl="",
                             leaves=([("n00000100", 120), ("n00000101", 130), ("n00000102", 50)] if x == extra_site else [])) for x in sites_]}
    obs_c = [dict(site=x, n=300, gain=0.1, cpu={"10": 0.0},
                  p10=(dict(ok=False, error="FitError: synthetic") if x in obs_fail else dict(ok=True, LR=1.0, dBIC=1.0, dICL=0.5)),
                  p5=dict(ok=True, LR=1.0), p20=dict(ok=True, LR=1.0)) for x in sites_]
    cells = []
    for x in sites_:
        for b in range(B_MAIN):
            c = dict(site=x, b=b, lr10=(2.0 if b % 7 == 0 else 0.5), ok10=True, cpu={"10": 0.0})
            if (x, b) in fail10:
                c.update(lr10=None, ok10=False, err10="FitError: synthetic")
            if b < B_DESC:
                c.update(lr5=0.5, ok5=True, lr20=0.5, ok20=True)
                if (x, b) in fail20:
                    c.update(lr20=None, ok20=False, err20="FitError: synthetic")
            else:
                c.update(lr5=None, lr20=None)
            cells.append(c)
    leaves = [dict(leaf=lf, n=nl, ok=lf not in leaf_fail, gain=(None if lf in leaf_fail else g), error=None, cpu={"10": 0.0})
              for lf, nl, g in (("n00000100", 120, 0.01), ("n00000101", 130, 0.03))]
    ch = [dict(kind="obs", tree="frozen", cells=obs_c), dict(kind="draws", tree="frozen", cells=cells),
          dict(kind="leaf", tree="frozen", cells=leaves)]
    rows = collect(ch, sites, None, dict(legs_desc=["5", "20"]))["frozen"]
    return {r["node_id"]: summarise_site(r) for r in rows}


def st_fail(chk):
    """Ruling A3 (programme L20864-L20919), executed branch by branch."""
    X = "n00000006"
    ok = _fail_fixture()
    chk.ok(not ok[X]["void"] and ok[X]["f"] == 0 and ok[X]["q"] == Fraction(1 + 29, 200), "ST-FAIL no failure: q = 30/200 (29 of 199 null LRs >= observed)")
    r = _fail_fixture(fail10=[(X, 7)])[X]
    chk.ok(not r["void"] and r["f"] == 1 and r["B"] == 198 and r["q"] == Fraction(1 + 28, 199),
           "ST-FAIL f = 1 at a non-deciding site is ADMITTED: q = (1 + c) / (B - f + 1) = 29/199")
    r = _fail_fixture(fail10=[(X, 3), (X, 4)])[X]
    chk.ok(r["void"] and r["f"] == 2 and "2 of 199" in r["void_reason"] and r["q"] is None, "ST-FAIL f = 2 (more than 1% of 199) makes the site VOID")
    r = _fail_fixture(obs_fail=[X])[X]
    chk.ok(r["void"] and "observed p = 10 fit FAILED" in r["void_reason"], "ST-FAIL a failed observed fit makes the site VOID")
    fx = _fail_fixture(fail10=[("n00000014", 7)])
    chk.ok(fx["n00000014"]["c1_void"] and not fx["n00000014"]["void"], "ST-FAIL one failed null fit at a deciding site VOIDs C1 (no 1% allowance)")
    held, br, vr = c1_verdict({k: fx[k] for k in DECIDING})
    chk.ok(bool(vr) and not held, "ST-FAIL c1_verdict returns VOID")
    summ = _synthetic_summary()
    summ["frozen"] = list(fx.values())
    L, v = render(summ, ["5", "20"])
    t = "\n".join(L)
    chk.ok(v["c1_void"] and "C1 VOID (a failed precondition" in t and "P1 C1 HELD (p 0.35): UNSCOREABLE (C1 VOID)" in t
           and "FALSIFIER F1: not scored (C1 VOID)" in t and "THE READING OF THE OUTCOME: none (C1 VOID" in t,
           "ST-FAIL render: C1 VOID printed; P1-P3 UNSCOREABLE; F1 not scored; no reading")
    fx = _fail_fixture(obs_fail=["n00000055"])
    chk.ok(fx["n00000055"]["c1_void"] and fx["n00000055"]["void"], "ST-FAIL a failed observed fit at a deciding site VOIDs the site and C1")
    r = _fail_fixture(fail20=[(X, 3)])[X]
    chk.ok(r["q20"] == "VOID" and r["q5"] not in (None, "VOID") and not r["void"] and r["q"] is not None,
           "ST-FAIL a failed p = 20 fit VOIDs that leg's q at that site only (p = 5 and p = 10 stand)")
    r = _fail_fixture(leaf_fail=["n00000100"])[X]
    chk.ok(r["leaf_fail_ids"] == ["n00000100"] and r["leaf_median"] == 0.03, "ST-FAIL a failed leaf fit is excluded and counted (median of the rest)")
    r = _fail_fixture(leaf_fail=["n00000100", "n00000101"])[X]
    chk.ok(r["sec"] is None and len(r["leaf_fail_ids"]) == 2, "ST-FAIL all qualifying leaves failed: D5 reads NA, the failures counted")
    rows = list(_fail_fixture(fail10=[(X, 3), (X, 4)]).values())
    tsum = tree_summary(rows)
    chk.ok(tsum["n"] == 3 and tsum["n_all"] == 4 and tsum["void"] == 1 and tsum["f_total"] == 2,
           "ST-FAIL D1-D7 run over the non-VOID sites; denominators printed net of VOID (3 = 4 - 1)")
    summ = _synthetic_summary()
    summ["frozen"] = summ["frozen"] + [rows[-1]]
    t = "\n".join(render(summ, ["5", "20"])[0])
    chk.ok("of 69 (= 70 - 1 VOID)" in t, "ST-FAIL render prints the net denominator 'n (= all - v VOID)'")
    fx = _fail_fixture(fail10=[(X, 3)])
    chk.ok("f_failed_null" in sites_csv_text({**{t_["name"]: [] for t_ in TREES}, "frozen": list(fx.values())}).splitlines()[0],
           "ST-FAIL the sites CSV carries VOID, f and the admitted B")


PCA_TOL = 1e-9     # ST-PCA / ST-REG bar (the orchestrator's): principal angle and relative LR difference vs the thin SVD


def max_sin_angle(Va, Vb):
    """sin of the largest principal angle between the row spaces of Va and Vb (orthonormal rows); exact near 0, unlike arccos."""
    R = Va - (Va @ Vb.T) @ Vb
    return float(np.linalg.norm(R, 2))


def _pca_compare(X, ps=(5, 10, 20), rs=3):
    Xc, Va = pca_basis(X)
    _, Vb = pca_basis_thin(X)
    ang = max(max_sin_angle(Va[:p_], Vb[:p_]) for p_ in ps)
    lr = 0.0
    for p_ in ps:
        la, lb = lr_stats(Xc @ Va[:p_].T, rs)["LR"], lr_stats(Xc @ Vb[:p_].T, rs)["LR"]
        lr = max(lr, abs(la - lb) / abs(lb))
    return ang, lr


def st_pca(chk):
    """The eigh route against the thin SVD: full-rank, rank-deficient (n < d) and repeated-eigenvalue fixtures, p = 5, 10, 20.
    MIX-FLAT-SELFTEST-GAPS D7: the printed quantity is sin(largest principal angle) = the projector distance ||P_a - P_b||_2,
    verified on fixtures with a known angle (READY dde660e's blob printed the arccos floor; 3e6a682c already prints the sine)."""
    for p_, theta in ((5, 0.3), (10, 1e-6), (20, 0.0)):
        E = np.eye(64)
        Va, Vb = E[:p_].copy(), E[:p_].copy()
        Vb[0] = math.cos(theta) * E[0] + math.sin(theta) * E[p_ + 3]
        proj = float(np.linalg.norm(Va.T @ Va - Vb.T @ Vb, 2))
        got = max_sin_angle(Va, Vb)
        chk.ok(abs(got - math.sin(theta)) <= 1e-12 and abs(proj - math.sin(theta)) <= 1e-12,
               "ST-PCA (D7) p %d, angle %g: max_sin_angle %.6e == projector distance ||P_a - P_b||_2 %.6e == sin(angle)" % (p_, theta, got, proj))
    rng = np.random.default_rng(41)
    cases = [(150, 32), (400, 256), (2000, 512)] + [(n, d) for d in (256, 512) for n in (60, 140, 250)]
    for n, d in cases:
        ang, lr = _pca_compare(synth_elongated(rng, n, d))
        chk.ok(ang < PCA_TOL and lr < PCA_TOL, "ST-PCA n %d d %d%s: max sin(principal angle) %.1e, max relative LR difference %.1e (bar %.0e)"
               % (n, d, " (rank-deficient, n < d)" if n < d else "", ang, lr, PCA_TOL))
    # repeated eigenvalues: Xc = U diag(s) V^T with ties INSIDE the groups and gaps at 5, 10 and 20
    n, d = 60, 256
    U, _ = np.linalg.qr(np.column_stack([np.ones(n)] + [rng.standard_normal(n) for _ in range(40)]))
    U = U[:, 1:41]                                   # orthogonal to the ones vector: centring leaves Xc unchanged
    V, _ = np.linalg.qr(rng.standard_normal((d, 40)))
    sv = np.array([5.0] * 3 + [4.0] * 2 + [3.0] * 5 + [2.0] * 10 + [1.0] * 20) * 0.05
    X = (U * sv) @ V.T + 0.3 * np.eye(d)[0]
    ang, lr = _pca_compare(X)
    chk.ok(ang < PCA_TOL and lr < PCA_TOL, "ST-PCA repeated eigenvalues (n 60, d 256, ties inside the top 5 / 10 / 20): max sin(angle) %.1e,"
           " max relative LR difference %.1e (bar %.0e)" % (ang, lr, PCA_TOL))


def st_reg(chk):
    """Regression of the b617888 crash: frozen n00000109 (CSV row 39), draw 10, regenerated with the registered stream from the
    site's member vectors (read-only). Asserts that the old route (np.linalg.svd of the scatter) fails on it, and that pca_basis
    matches the thin SVD within PCA_TOL. Prints no statistic. Needs the DBs (TAXOARENA_DATA_ROOT); fails closed without them."""
    tree = TREE_BY_NAME["frozen"]
    rows, _ = load_csv(tree)
    r = rows[39]
    chk.ok(r["node_id"] == "n00000109" and int(r["n"]) == 140, "ST-REG frozen CSV row 39 is n00000109 with n 140 (the crash site)")
    g = load_graph(tree["snapshot"])
    ids = region_query_ids("n00000109", g["byid"])
    X, order = prepare_members(ids, load_vectors(ids, tree["dim"]), 140, "frozen/n00000109")
    ctx = SiteCtx("frozen", 39, "n00000109", r["label"], int(r["depth"]), 140, int(r["k"]), False, "", X, order,
                  tree_index=TREE_INDEX["frozen"])
    rng = np.random.default_rng(draw_stream(ctx.tree_index, ctx.row, 10))
    Y = within_node_cloud_eigen(ctx.mu, ctx.s, ctx.Vt, ctx.C.shape[0], ctx.n, rng)
    Yc = Y - Y.mean(axis=0)
    try:
        np.linalg.svd(Yc.T @ Yc)
        old_fails = False
    except np.linalg.LinAlgError:
        old_fails = True
    note = ("ST-REG note (NOT a check; delta READY e8a9eed D4): the old route (np.linalg.svd of the scatter) on the regenerated cell %s;"
            " environment %s" % ("raises LinAlgError (the b617888 crash reproduced)" if old_fails else
                                 "CONVERGES here (a numpy / BLAS difference, not a failure)", env_line()))
    if not chk.quiet:
        print("  note " + note)
    Yc2, Va = pca_basis(Y)
    _, Vb = pca_basis_thin(Y)
    ang = max(max_sin_angle(Va[:p_], Vb[:p_]) for p_ in (5, 10, 20))
    states = rng.integers(0, 2 ** 31 - 1, size=3)
    lr_rel = max(abs(lr_stats(Yc2 @ Va[:p_].T, states[LEG_STATE_INDEX[str(p_)]])["LR"] - lr_stats(Yc2 @ Vb[:p_].T, states[LEG_STATE_INDEX[str(p_)]])["LR"])
                 / abs(lr_stats(Yc2 @ Vb[:p_].T, states[LEG_STATE_INDEX[str(p_)]])["LR"]) for p_ in (5, 10, 20))
    chk.ok(ang < PCA_TOL and lr_rel < PCA_TOL, "ST-REG on that cell pca_basis matches the thin SVD: max sin(angle) %.1e, max relative LR"
           " difference %.1e (bar %.0e; no statistic printed)" % (ang, lr_rel, PCA_TOL))


ROUTE_SPOT_EVERY = 50     # --route-sweep: the thin-SVD spot check on draws b = 0, 50, 100, ... of every site (delta READY e8a9eed D1)
ROUTE_PS = (5, 10, 20)


def env_line():
    """numpy / scipy / sklearn versions and the BLAS threadpool (the environment ST-REG's note is read against)."""
    import scipy
    import sklearn
    blas = "unknown"
    try:
        from threadpoolctl import threadpool_info
        blas = ", ".join("%s %s" % (i.get("internal_api"), i.get("version")) for i in threadpool_info()) or "none reported"
    except ImportError:
        pass
    return "numpy %s, scipy %s, scikit-learn %s, BLAS %s" % (np.__version__, scipy.__version__, sklearn.__version__, blas)


def route_cell_check(Y, spot, basis=None):
    """--route-sweep's per-cell check -> (ok, why, gap, sin_thin). ok needs finite, orthonormal top-20 axes AND, on a spot cell,
    the top-5 / 10 / 20 subspaces equal to the thin SVD's within PCA_TOL (delta READY e8a9eed D1: the orthonormality check alone
    passes ANY orthonormal basis, a wrong subspace included). gap = min over p in (5, 10, 20) of (var_p - var_{p+1}) / var_1, the
    variances ||Xc v_j||^2 along the returned axes (a relative eigen-gap; negative if the axes are not sorted)."""
    basis = pca_basis if basis is None else basis
    try:
        Xc, Vt = basis(Y)
        V20 = Vt[:20]
        ok = bool(np.all(np.isfinite(V20)) and np.max(np.abs(V20 @ V20.T - np.eye(V20.shape[0]))) < 1e-8)
        why = "" if ok else "non-finite or non-orthonormal axes"
        var = np.sum((Xc @ Vt[:max(ROUTE_PS) + 1].T) ** 2, axis=0)
        gap = float(min((var[p_ - 1] - var[p_]) / var[0] for p_ in ROUTE_PS))
        sin_thin = None
        if spot:
            _, Vb = pca_basis_thin(Y)
            sin_thin = max(max_sin_angle(Vt[:p_], Vb[:p_]) for p_ in ROUTE_PS)
            if not sin_thin < PCA_TOL:
                ok = False
                why = (why + "; " if why else "") + "subspace differs from the thin SVD (max sin %.1e >= %.0e)" % (sin_thin, PCA_TOL)
    except Exception as e:                            # noqa: B902 - the sweep reports every failure class
        return False, "%s: %s" % (type(e).__name__, e), None, None
    return ok, why, gap, sin_thin


def st_route(chk):
    """delta READY e8a9eed D1: route_cell_check REJECTS a wrong subspace on a spot cell (the reviewer's R3 passed the old
    orthonormality-only check at sin 1.00) and measures the relative eigen-gap exactly on a fixture with known variances."""
    rng = np.random.default_rng(81)
    Y = synth_elongated(rng, 140, 256)
    ok, why, gap, sin_thin = route_cell_check(Y, True)
    chk.ok(ok and sin_thin is not None and sin_thin < PCA_TOL and gap > 0, "ST-ROUTE a regular n < d cell passes (spot sin %.1e, gap %.3e)"
           % (sin_thin, gap))

    def bottom_axes(Y_):
        Xc_, Vt_ = pca_basis(Y_)
        return Xc_, np.vstack([Vt_[20:40], Vt_[:20]])
    ok_w, why_w, _, sin_w = route_cell_check(Y, True, basis=bottom_axes)
    chk.ok((not ok_w) and "thin SVD" in why_w, "ST-ROUTE a wrong (orthonormal) subspace FAILS the spot check (sin %.2f): %s" % (sin_w, why_w))
    ok_n, _, _, sin_n = route_cell_check(Y, False, basis=bottom_axes)
    chk.ok(ok_n and sin_n is None, "ST-ROUTE (disclosed) off a spot cell the orthonormality check alone passes the same wrong basis")
    n, d = 60, 256
    U, _ = np.linalg.qr(np.column_stack([np.ones(n)] + [rng.standard_normal(n) for _ in range(40)]))
    U = U[:, 1:41]
    V, _ = np.linalg.qr(rng.standard_normal((d, 40)))
    sv = np.array([5.0] * 3 + [4.0] * 2 + [3.0] * 5 + [2.0] * 10 + [1.0] * 20) * 0.05
    X = (U * sv) @ V.T + 0.3 * np.eye(d)[0]
    ok, _, gap, _ = route_cell_check(X, True)
    chk.ok(ok and abs(gap - 3.0 / 25.0) < 1e-9, "ST-ROUTE relative eigen-gap on known variances 25/16/9/4/1: %.12f == min(7, 5, 3) / 25 = 0.12" % gap)


def route_sweep():
    """Zero-statistic sweep: the generator + pca_basis over EVERY registered draw of every site of the four trees (b < 199;
    b < 999 at the three deciding sites, the maximal escalation). Prints only counts, the minimum relative eigen-gap, the
    thin-SVD spot checks, or the failing cells; never an LR (delta READY e8a9eed D1)."""
    print_header()
    print("[MODE] --route-sweep: generator + pca_basis on every registered draw; no fit, no LR, nothing written")
    total, bad = 0, []
    n_spot, worst_sin = 0, 0.0
    min_gap = None
    t0 = time.perf_counter()
    for tree in TREES:
        tc = tree_contexts(tree)
        n_tree = 0
        for ctx in tc["ctxs"]:
            B = B_ESC if (tree["name"] == DECIDING_TREE and ctx.node_id in DECIDING) else B_MAIN
            for b in range(B):
                rng = np.random.default_rng(draw_stream(ctx.tree_index, ctx.row, b))
                Y = within_node_cloud_eigen(ctx.mu, ctx.s, ctx.Vt, ctx.C.shape[0], ctx.n, rng)
                ok, why, gap, sin_thin = route_cell_check(Y, b % ROUTE_SPOT_EVERY == 0)
                if gap is not None and (min_gap is None or gap < min_gap[0]):
                    min_gap = (gap, tree["name"], ctx.node_id, b)
                if sin_thin is not None:
                    n_spot += 1
                    worst_sin = max(worst_sin, sin_thin)
                n_tree += 1
                if not ok:
                    bad.append((tree["name"], ctx.node_id, ctx.row, b, ctx.n, why))
                    print("  FAIL %s %s row %d draw %d n %d: %s" % (tree["name"], ctx.node_id, ctx.row, b, ctx.n, why))
        total += n_tree
        print("  %-16s %d cells (%d sites) swept; failures so far %d; %.0f s" % (tree["name"], n_tree, len(tc["ctxs"]), len(bad),
                                                                              time.perf_counter() - t0))
    print("  thin-SVD spot checks: %d cells (every %d-th draw of every site), max sin(principal angle) %.1e (bar %.0e)"
          % (n_spot, ROUTE_SPOT_EVERY, worst_sin, PCA_TOL))
    if min_gap is not None:
        print("  minimum relative eigen-gap at p = 5 / 10 / 20: %.3e (%s %s draw %d)" % min_gap)
    if bad:
        print("route FAILED on %d of %d cells" % (len(bad), total))
        return 1
    print("route OK for %d cells" % total)
    return 0

# ------------------------------------------------------------------------------------------------ mutants
MUTANTS = (
    ("q without add-one", "return Fraction(1 + c, B + 1)", "return Fraction(c, B)", ("ST4",)),
    ("certify strictly below 0.05", "return q <= CERT_Q", "return q < CERT_Q", ("ST4",)),
    ("band lower edge exclusive", "return ESC_LO <= q <= ESC_HI", "return ESC_LO < q <= ESC_HI", ("ST4",)),
    ("band upper edge exclusive", "return ESC_LO <= q <= ESC_HI", "return ESC_LO <= q < ESC_HI", ("ST4",)),
    ("escalate every site", "return tree == DECIDING_TREE and node_id in DECIDING and in_escalation_band(q199)",
     "return in_escalation_band(q199)", ("ST4",)),
    ("no drop above the budget", 'return ("10",) if projected_cpu_min > cap else LEGS_ALL', "return LEGS_ALL", ("ST4",)),
    ("drop the deciding leg", 'return ("10",) if projected_cpu_min > cap else LEGS_ALL',
     'return ("5", "20") if projected_cpu_min > cap else LEGS_ALL', ("ST4",)),
    ("escalation to B = 1000", "B_ESC = 999", "B_ESC = 1000", ("ST4",)),
    ("descriptive on 50 draws", "B_DESC = 49", "B_DESC = 50", ("ST4",)),
    ("membership check removed", "    if len(ids) != n_expected:\n", "    if False:\n", ("ST6",)),
    ("missing-vector check removed", "    if missing:\n        refuse(\"%d of %d members", "    if False:\n        refuse(\"%d of %d members", ("ST6",)),
    ("no sort by text", "order = sorted(ids, key=lambda i: (vecmap[i][0], i))\n    return", "order = list(ids)\n    return", ("ST6",)),
    ("pin check removed", 'if got["blob"] != blob or got["lf16"] != lf16:', "if False:", ("ST-PIN",)),
    ("outcome opened 'w'", 'with open(path, "x", encoding="utf-8", newline="\\n") as f:',
     'with open(path, "w", encoding="utf-8", newline="\\n") as f:', ("ST-PIN",)),
    ("diagonal covariance", 'covariance_type="full"', 'covariance_type="diag"', ("ST-INV",)),
    ("generator not renormalised", "        if normalise:\n            Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)\n        out[s:e] = Y",
     "        if False:\n            Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)\n        out[s:e] = Y", ("ST3",)),
    ("generator without 1/sqrt(m)", "    inv = 1.0 / math.sqrt(m)\n    out = np.empty", "    inv = 1.0\n    out = np.empty", ("ST3", "ST-JVM")),
    ("generator adds the mean twice", "        Y = mu + (G * inv) @ C\n", "        Y = 2 * mu + (G * inv) @ C\n", ("ST3", "ST-JVM")),
    ("PCA of the uncentred scatter", "    w, V = np.linalg.eigh(Xc.T @ Xc)\n", "    w, V = np.linalg.eigh(X.T @ X)\n", ("ST-PCA",)),
    ("PCA axes in ascending order", "    order = np.argsort(w, kind=\"stable\")[::-1]\n", "    order = np.argsort(w, kind=\"stable\")\n", ("ST-PCA",)),
    ("PCA back to svd of the scatter (the crash)", "    w, V = np.linalg.eigh(Xc.T @ Xc)\n    order = np.argsort(w, kind=\"stable\")[::-1]\n    return Xc, V[:, order].T",
     "    _, _, Vt = np.linalg.svd(Xc.T @ Xc)\n    return Xc, Vt", ("ST-REG",)),
    ("k = 1 log-likelihood without the + p", "return -0.5 * n * (p * math.log(2 * math.pi) + logdet + p)",
     "return -0.5 * n * (p * math.log(2 * math.pi) + logdet)", ("ST-L1",)),
    ("ICL without the entropy", "dICL=bic1 - (bic2 + 2.0 * ent)", "dICL=bic1 - bic2", ("ST-INV",)),
    ("BIC with a wrong k2", "return 2 * k1_params(p) + 1", "return 2 * k1_params(p)", ("ST4", "ST-INV")),
    ("secondary over all leaves", "g = [x for (n, x) in leaf_gains if n >= LEAF_MIN_N]", "g = [x for (n, x) in leaf_gains]", ("ST-SEC",)),
    ("draw streams alias (b mod 4)", "return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, row, b))",
     "return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, row, b % 4))", ("ST5",)),
    ("draw stream without the tree (A1)", "return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, row, b))",
     "return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(row, b))", ("ST5",)),
    ("site stream without the tree (A1)", "return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(tree_index, row))",
     "return np.random.SeedSequence(ROOT_ENTROPY, spawn_key=(row,))", ("ST5",)),
    ("leaf stream without the tree (A2)", "spawn_key=(tree_index, LEAF_SPAWN_BASE + node_number(leaf_id)))",
     "spawn_key=(LEAF_SPAWN_BASE + node_number(leaf_id),))", ("ST5",)),
    ("eigen generator without 1/sqrt(m)", "    scale = s / math.sqrt(m)\n", "    scale = s\n", ("ST3", "ST-EQ")),
    ("eigen generator not renormalised", "        if normalise:\n            Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)\n        out[a:e] = Y",
     "        if False:\n            Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)\n        out[a:e] = Y", ("ST3",)),
    ("eigen generator drops the smallest axis", "        Z = rng.standard_normal((e - a, s.size))\n        Y = mu + (Z * scale) @ Vt",
     "        Z = rng.standard_normal((e - a, s.size))\n        Z[:, -2:] = 0\n        Y = mu + (Z * scale) @ Vt", ("ST3", "ST-EQ")),
    ("q not over admitted draws", "    return q_add_one(c, B - f)", "    return q_add_one(c, B)", ("ST4",)),
    ("f >= 2 VOID raised to 3", "            elif f >= 2:", "            elif f >= 3:", ("ST-FAIL",)),
    ("f = 1 VOIDs the site", "            elif f >= 2:", "            elif f >= 1:", ("ST-FAIL",)),
    ("deciding site gets the 1% allowance", "            if deciding and (not obs_ok or f > 0):", "            if deciding and (not obs_ok or f > 1):", ("ST-FAIL",)),
    ("failed p20 leg not VOIDed", '                        null[leg] = "VOID"', '                        null[leg] = [0.0] * B_DESC', ("ST-FAIL",)),
    ("failed leaf kept as gain 0", "                        lfail.append(lf)", "                        lg.append((n, 0.0))", ("ST-FAIL",)),
    ("VOID sites kept in D1-D7", '    rows = [r for r in all_rows if not r["void"]]', "    rows = list(all_rows)", ("ST-FAIL",)),
    ("C1 VOID ignored", "    if vr:\n        return False, [], vr", "    if False:\n        return False, [], vr", ("ST-FAIL",)),
    ("regionQueryIds FIFO", "        cur = stack.pop()\n        if cur in seen:\n            continue\n        seen.add(cur)\n        node = byid[cur]",
     "        cur = stack.pop(0)\n        if cur in seen:\n            continue\n        seen.add(cur)\n        node = byid[cur]", ("ST-REGION",)),
    ("completeness check removed", '                    refuse("%s/%s: draw %d is missing', '                    None and refuse("%s/%s: draw %d is missing', ("ST-COMPLETE",)),
    ("duplicate check removed", "    if dup:\n        refuse(\"%d cell(s) present more than once", "    if False:\n        refuse(\"%d cell(s) present more than once", ("ST-COMPLETE",)),
    ("escalation completeness removed", '                        refuse("%s/%s: escalation draw %d is missing',
     '                        None and refuse("%s/%s: escalation draw %d is missing', ("ST-COMPLETE",)),
    ("C1 ignores n00000014", "held = bool(c13 and not c14 and not c55)", "held = bool(c13 and not c55)", ("ST-BRANCH",)),
    ("MC-marginal never printed", "        mc = bool(lo <= 0.05 <= hi)", "        mc = False", ("ST-BRANCH",)),
    ("R-f never", "    rf = bool(len(branches) == 2)", "    rf = False", ("ST-BRANCH",)),
    ("R-a decided by the pooled reading", "        if ra1:\n            applied.append(\"R-a\")", "        if ra2:\n            applied.append(\"R-a\")", ("ST-BRANCH",)),
    ("threads not pinned", 'for _v in THREAD_VARS:                       # BEFORE numpy', 'for _v in ():                       # BEFORE numpy', ("ST7",)),
    ("connect guard admits mode=ro", 'if params.get("mode") != "ro" or params.get("immutable") != "1":', 'if params.get("mode") != "ro":', ("ST-GUARD",)),
    ("java nextGaussian without the cached second value", "        if self.have:\n            self.have = False", "        if False:\n            self.have = False", ("ST-JVM",)),
    # MIX-FLAT-SELFTEST-GAPS (READY dde660e D3 / D4 / D6 / D7; delta READY e8a9eed D1)
    ("post-drop sum keeps p5/p20 (D3)", '    return pr["p10"] + pr["esc"] + pr["obs"]', '    return pr["total"]', ("ST-COST",)),
    ("post-drop line never OVER (D3)", '"OVER the cap even after the drop" if pd > CAP_CPU_MIN', '"OVER the cap even after the drop" if False', ("ST-COST",)),
    ("measured CPU omits the p10 leg (D3)", '                p10 += cpu.get("10", 0.0)', '                p10 += 0.0', ("ST-COST",)),
    ("run() escalates every deciding site (R4c, D6)", "    if q199 is None or not escalates(name, sid, q199):\n        return []",
     "    if q199 is None:\n        return []", ("ST-ESC",)),
    ("run()'s q199 ignores f (R4d, D6)", "    return q_admitted(exceed_count(ok, obs), B, B - len(ok))", "    return q_add_one(exceed_count(ok, obs), B)", ("ST-ESC",)),
    # (no mutant on escalation_tasks' "all 199 main draws present" guard: EQUIVALENT, site_q returns None unless all B are present)
    ("eigen generator axes reversed (D4, ST-EQ iii)", "        Y = mu + (Z * scale) @ Vt\n", "        Y = mu + (Z * scale[::-1]) @ Vt[::-1]\n", ("ST-EQ3",)),
    ("principal angle by arccos (D7)", "    return float(np.linalg.norm(R, 2))",
     "    return float(np.max(np.arccos(np.clip(np.linalg.svd(Va @ Vb.T, compute_uv=False), -1, 1))))", ("ST-PCA",)),
    ("route spot check removed (e8a9eed D1)", "        if spot:\n            _, Vb = pca_basis_thin(Y)", "        if False:\n            _, Vb = pca_basis_thin(Y)", ("ST-ROUTE",)),
    ("route gap not relative (e8a9eed D1)", "        gap = float(min((var[p_ - 1] - var[p_]) / var[0] for p_ in ROUTE_PS))",
     "        gap = float(min((var[p_ - 1] - var[p_]) for p_ in ROUTE_PS))", ("ST-ROUTE",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    print("MUTANTS (%d): each removes or alters one check; KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed = 0
    cut = src.index(chr(10) + "MUTANTS = (")      # mutate the code only, never the mutant table itself
    head, tail = src[:cut], src[cut:]
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: the target text occurs %d times (must be exactly 1)" % (TAG, name, head.count(old)))
        ok_orig = _exec_selftest(src, tests)
        res = _exec_selftest(head.replace(old, new) + tail, tests)
        k = (res is not True) and ok_orig is True
        killed += int(k)
        print("  %-50s tests %-18s original %-4s mutant %-8s | %s" % (name, ",".join(tests), "PASS" if ok_orig is True else "FAIL",
                                                                   "KILLED" if k else "SURVIVED", "" if res is True else res[:110]))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def _exec_selftest(src, tests):
    saved = {v: os.environ.get(v) for v in THREAD_VARS}
    ns = {"__name__": "mix_lrt_site_mutant", "__file__": os.path.abspath(__file__)}
    try:
        for v in THREAD_VARS:
            os.environ.pop(v, None)
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True, heavy=False)
        return True
    except BaseException as e:                   # noqa: B902 - a killed mutant may raise anything
        return "%s: %s" % (type(e).__name__, str(e)[:120])
    finally:
        for v, x in saved.items():
            os.environ[v] = x
        sqlite3.connect = _guarded_connect


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--analyze", action="store_true")
    g.add_argument("--route-sweep", action="store_true", help="zero-statistic sweep of the generator + pca_basis over every draw")
    g.add_argument("--power-probe", action="store_true", help="SYNTHETIC: ST2's certified count at 4, 6, 8 within-SD (descriptive)")
    ap.add_argument("--max-chunks", type=int, default=None)
    ap.add_argument("--light", action="store_true", help="--selftest without ST1/ST1b/ST2 (the READY runs the full one)")
    a = ap.parse_args(argv)
    if a.route_sweep:
        return route_sweep()
    if a.power_probe:
        print(pool_line())
        print(threads_line())
        print("[SCRIPT] %s" % fmt_pins(script_pins()))
        print("POWER PROBE (synthetic only; the ST2 fixture: d 256, n 400, p 10, B 99, 20 clouds, the ST1 elongated noise):")
        for sep in (4.0, 6.0, 8.0):
            c = st_heavy(None, "ST2", sep_sd=sep)
            print("  separation %.0f within-SD: certified on %d of 20" % (sep, c))
        return 0
    if a.selftest:
        print(pool_line())
        print(threads_line())
        print("[SCRIPT] %s" % fmt_pins(script_pins()))
        t0 = time.perf_counter()
        n = selftest(heavy=not a.light)
        print("SELFTEST PASSED: %d checks%s (%.0f s)" % (n, " (light: ST1/ST1b/ST2 skipped)" if a.light else "", time.perf_counter() - t0))
        return 0
    if a.mutants:
        print(pool_line())
        print(threads_line())
        print("[SCRIPT] %s" % fmt_pins(script_pins()))
        return run_mutants()
    if a.dry_run:
        return dry_run()
    if a.run:
        return run(max_chunks=a.max_chunks)
    return analyze()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
