"""EVAL-METRIC-DETERMINISM harness: shared constants and helpers (registration docs/judge_v2_program.md L20311-L20389,
commit 55a6ce1; P2 kept at L20382, 8bf15da). Zero calls. Imported by emd_prep.py, emd_leg_check.py, emd_compare.py and
emd_selftest.py; nothing here opens a database or runs a process.

THE LEGS (registration INSTRUMENT): five, sequential, in the order P1 (BASE), R1 (FIX), R2 (FIX), P2 (BASE), R3 (FIX),
each in a fresh worktree. BASE = 2f080e0 (main when the fix branch eval-metric-det3 was cut, 2026-09-30); FIX = 6569cd3
(BASE + the change + the new test, nothing else: 77f7cb8 / eef090a cherry-picked, the same four blobs; the harness commits
that follow it on the branch touch no src/, tools/ or experiment_configs/ path, and the legs check out 6569cd3 itself, never
the branch tip). [RE-CUT 2026-09-30/10-01, READY_backfill_2026-09-30 b938c14 B-EM-1: was BASE 8bf15da / FIX eef090a; every
leg's bootRun now carries -PjvmThreads=12 and emd_leg_check requires the witness "[THREAD-CAP] requested=12
availableProcessors=12" on every such transcript line (check TC), equal across the five legs (the verdict's TC); main's AG
input files moved since D9b (checkpointed on 2026-09-27: the DB is now the former checkpointed copy e3415684..., the -wal is
empty), so AG_BASE is re-read below; the staged copy (AG_COPY_SHA) and the embeddings pin are unchanged (re-hashed).]

THE OBJECT AND DROP LISTS are copies of the D9 (d9_compare.py, blob:743cd1a1, sha256-lf16:8636b21591e70a76) and D9b
(d9b_compare.py, blob:209eb2e6, sha256-lf16:55b961cac7165688) instruments, VERBATIM. `assert_lists_match_originals()`
imports both originals from experiment_results/lcb_stage0 (after checking their LF sha256 against the pins below) and
asserts equality; every compare mode calls it before reading any leg.
"""
import hashlib, importlib.util, json, os

VERSION = "emd-harness-2"
BASE = "2f080e079f79c62c3a38337005438c6a310be81b"
FIX = "6569cd31ead59b2f822ab5c2b91347443e1cd378"
LEGS = ("P1", "R1", "R2", "P2", "R3")               # the registered order
COMMIT = {"P1": BASE, "R1": FIX, "R2": FIX, "P2": BASE, "R3": FIX}
R_LEGS, P_LEGS = ("R1", "R2", "R3"), ("P1", "P2")
C1_PAIRS = (("R1", "R2"), ("R1", "R3"), ("R2", "R3"))   # C1 and C4
C3_PAIRS = (("P1", "R1"),)
X1 = "canonicalByRawText"                           # the declared execution discriminator (V3)
X1_DECLARED_COUNT = 3                               # the build report's count (eef090a); PRINTED, the bar is V3's.
#   RE-MEASURE OWED at FIX 6569cd3 (needs a compile; no JVM was allowed during the re-cut): grep -rlaF canonicalByRawText
#   build/classes/kotlin/main after `gradlew compileKotlin --offline --no-daemon` in a FIX worktree; edit only if it differs.
THREAD_CAP_N = 12                                   # -PjvmThreads in every leg (registrar L22178; THREAD-CAP binds bootRun)
TC_WITNESS = "requested=%d availableProcessors=%d" % (THREAD_CAP_N, THREAD_CAP_N)
TC_RE = r"\[THREAD-CAP\] requested=(\S+) availableProcessors=(\d+)"
FIX_SRC = {"src/main/kotlin/taxonomy/utils/AdditionalMetrics.kt": "c908caf570cf8e2f79fa4687ccfa656109c1033f",
           "src/main/kotlin/taxonomy/utils/HierarchicalMetrics.kt": "4af031448cec7fac1fcc57cd78627ffe75409068",
           "src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt": "930adb430476fb75ac4dc3ac3cfa8968df896b7d"}
TEST_PATH = "src/test/kotlin/taxonomy/EvalMetricDeterminismTest.kt"
TEST_BLOB = "45d8f0abeb210b7bd70a76178b0ac332687e7ce7"
TEST_CLASS = "taxonomy.EvalMetricDeterminismTest"
TDC_TEST = "tdcSampledPermutationInvariant()"
TA_TEST = "tripletAccuracyPermutationInvariant()"
KNOWN_FAILURES = {("taxonomy.MrlRoutingTest", "testMrlConfigDefaults()"),
                  ("taxonomy.TraceEnvelopeUnwrapTest", "no model has a wholly blank trace column()")}
TOML = "experiment_configs/topic_partition/ag_news_smoke_s42.toml"
TOML_BLOB = "efd82bdacc06144439280d3b76923d38527bd7ae"
OUT = os.path.join("experiment_results", "topic_partition", "ag_news_smoke_s42")
QUALITY = "seed_42/validation/MAIN_taxonomy_quality.csv"
LEDGER = "tuning_ledger.csv"
DECLARED = ["DendrogramPurity", "SphericalSilhouette", "TotalDasguptaCost"]
SANITY = ("Fetched 2000 AG News queries across 4 categories", "[POOL] recorded p18579549e6d95873",
          "[SPLIT-SIDE] 1400 train (145 gate) / 600 test")
CEIL_S = 480                                        # V8: 8 min
P9_DUR_MS, P9_GRADLE_S = (5000, 60000), 120
MARGIN_TDC, P7_DP, P7_SS = 0.01, 1e-13, 1e-15       # P7 bars (registered)

# the inputs of record (V2): main's files as in D9b (d9b_prep.py AG_BASE; the embeddings file) and the leg copies
# RE-READ 2026-09-30 (sha256sum of main's files, read-only): the D9b values were (1622016, 7cf2082f...) and (206032, 7eea2abd...);
# main's DB was checkpointed on 2026-09-27 (mtime 16:25) and is now byte-equal to the D9b checkpointed copy; its -wal is empty.
# A simulated prep on a scratch copy (copy + PRAGMA wal_checkpoint(TRUNCATE)) gives (0, 0, 0) and e3415684... = AG_COPY_SHA.
AG_BASE = {"ag_news_smoke_cache_v1.db": (1748992, "e3415684318c937c8e9073e1eb189c1f5a89006c0444794c20cf7b79ba527430"),
           "ag_news_smoke_cache_v1.db-wal": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")}
EMB_BASE = (804462592, "52229e1ebfdda76ebaed3e461eeee80ae654dfb35ac480eb9cb9868bb0269769")
AG_COPY_SHA = "e3415684318c937c8e9073e1eb189c1f5a89006c0444794c20cf7b79ba527430"   # the checkpointed copy (D9b V2)

# ---- the D9 object set and drops (d9_compare.py, verbatim) ----
D9_BYTE = ["seed_42/dag_snapshots.jsonl", "seed_42/gate_ids.json", "seed_42/fixed_point_certificate.txt"] + \
          ["seed_42/validation/" + f for f in ("MAIN_bridge_quality.csv", "MAIN_centroid_routing_results.csv", "MAIN_graph_validity.csv",
                                               "MAIN_heldout_leaf_support.csv", "MAIN_migration_flow_matrix.csv",
                                               "MAIN_routing_calibration.csv", "MAIN_routing_diagnostics.txt", "MAIN_taxonomy_quality.csv",
                                               "MAIN_trickle_validation_results.csv", "bridge_nodes.csv", "bridge_residuals.csv")] + \
          ["seed_42/diagnostics/" + f for f in ("dag_snapshots.jsonl", "proposals.csv", "rank_history.csv", "config.toml")]
D9_CSV_DROP = {"seed_42/diagnostics/iteration_metrics.csv": ["wall_ms"], "tuning_ledger.csv": ["CommitSHA"]}
# ---- the D9b object set and drops (d9b_compare.py, verbatim) ----
D9B_BYTE = ["seed_42/dag_snapshots.jsonl", "seed_42/gate_ids.json", "seed_42/fixed_point_certificate.txt"] + \
           ["seed_42/validation/" + f for f in ("MAIN_bridge_quality.csv", "MAIN_centroid_routing_results.csv", "MAIN_graph_validity.csv",
                                                "MAIN_heldout_leaf_support.csv", "MAIN_migration_flow_matrix.csv",
                                                "MAIN_routing_calibration.csv", "MAIN_routing_diagnostics.txt",
                                                "MAIN_trickle_validation_results.csv", "bridge_nodes.csv", "bridge_residuals.csv")] + \
           ["seed_42/diagnostics/" + f for f in ("dag_snapshots.jsonl", "proposals.csv", "rank_history.csv", "config.toml")]
D9B_CSV_DROP = {"seed_42/diagnostics/iteration_metrics.csv": ["wall_ms"], "tuning_ledger.csv": ["CommitSHA"] + DECLARED}
D9B_ROW_DROP = {"seed_42/validation/MAIN_taxonomy_quality.csv": ("Metric", DECLARED)}
# ---- shared by both ----
JSON_DROP = {"seed_42/diagnostics/run_manifest.json": ["commit", "branch", "dirty", "dirty_src", "dirty_src_files", "dirty_other",
                                                       "dirty_other_files", "dirty_files", "started_at_millis", "finished_at_millis",
                                                       "duration_ms", "config_path", "proposal_memo_digest_ms"]}
EXCLUDED = {"seed_42/headless_run.log", "seed_42/diagnostics/headless_run.log", "seed_42/performance_report.json"}
POOL_DROP = {"reserved_pool_meta": ["created_at"]}
FILESET = "FILE-SET"
TABLES = ["reserved_pool", "reserved_pool_meta"]
D9B_OBJECTS = D9B_BYTE + list(D9B_CSV_DROP)[:1] + list(JSON_DROP) + list(D9B_ROW_DROP) + list(D9B_CSV_DROP)[1:] + [FILESET] + TABLES
D9_OBJECTS = D9_BYTE + list(D9_CSV_DROP) + list(JSON_DROP) + [FILESET] + TABLES
C1_OBJECTS = [QUALITY, LEDGER]
assert len(D9B_BYTE) == 17 and len(D9B_OBJECTS) == 24 and len(set(D9B_OBJECTS)) == 24
assert len(D9_BYTE) == 18 and len(D9_OBJECTS) == 24 and len(set(D9_OBJECTS)) == 24

HERE = os.path.dirname(os.path.abspath(__file__))
# the repository whose experiment_results/lcb_stage0 holds the pinned originals; EMD_REPO overrides it ONLY for the
# selftest's mutant copies (the originals are sha256-pinned either way)
REPO = os.environ.get("EMD_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORIG = {"d9_compare": (os.path.join(REPO, "experiment_results", "lcb_stage0", "d9", "helpers", "d9_compare.py"),
                       "8636b21591e70a76c1d1a8d52d28ba6a59cfe238db49b4720e99355a438138a8"),
        "d9b_compare": (os.path.join(REPO, "experiment_results", "lcb_stage0", "d9b", "helpers", "d9b_compare.py"),
                        "55b961cac716568800f724eea17e3fa41b0ce9110f8f1b8ab53d6378254009c9")}


class Refuse(Exception):
    pass


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 22), b""):
            h.update(ch)
    return h.hexdigest()


def sha_lf(p):
    return sha_bytes(open(p, "rb").read().replace(b"\r\n", b"\n"))


def write_once(path, text):
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_json_once(path, obj):
    write_once(path, json.dumps(obj, indent=1, sort_keys=True) + "\n")


def load_json(p, what):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise Refuse("%s %s cannot be read as JSON: %s: %s" % (what, p, type(e).__name__, e))


def decode(raw):
    if raw[:2] in (bytes([0xFF, 0xFE]), bytes([0xFE, 0xFF])):
        return raw.decode("utf-16")
    return raw.decode("utf-8", "replace")


def _load(name):
    path, want = ORIG[name]
    if not os.path.isfile(path):
        raise Refuse("original %s absent at %s" % (name, path))
    got = sha_lf(path)
    if got != want:
        raise Refuse("original %s at %s has sha256-lf %s, not the pin %s" % (name, path, got[:16], want[:16]))
    spec = importlib.util.spec_from_file_location("emd_orig_" + name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def assert_lists_match_originals():
    """The copies above equal the pinned originals, list for list (a mismatch is an INSTRUMENT REFUSAL)."""
    d9, d9b = _load("d9_compare"), _load("d9b_compare")
    checks = [("D9 BYTE", D9_BYTE, d9.BYTE), ("D9 CSV_DROP", D9_CSV_DROP, d9.CSV_DROP), ("D9 JSON_DROP", JSON_DROP, d9.JSON_DROP),
              ("D9 EXCLUDED", EXCLUDED, d9.EXCLUDED), ("D9 POOL_DROP", POOL_DROP, d9.POOL_DROP), ("D9 OUT", OUT, d9.OUT),
              ("D9b BYTE", D9B_BYTE, d9b.BYTE), ("D9b CSV_DROP", D9B_CSV_DROP, d9b.CSV_DROP),
              ("D9b ROW_DROP", D9B_ROW_DROP, d9b.ROW_DROP), ("D9b JSON_DROP", JSON_DROP, d9b.JSON_DROP),
              ("D9b EXCLUDED", EXCLUDED, d9b.EXCLUDED), ("D9b POOL_DROP", POOL_DROP, d9b.POOL_DROP),
              ("D9b TABLES", TABLES, d9b.TABLES), ("D9b OBJECTS", D9B_OBJECTS, d9b.OBJECTS), ("D9b OUT", OUT, d9b.OUT),
              ("D9b DECLARED", DECLARED, d9b.DECLARED)]
    bad = [n for n, mine, theirs in checks if mine != theirs]
    if bad:
        raise Refuse("object / drop lists differ from the pinned originals: %s" % bad)
    return len(checks)
