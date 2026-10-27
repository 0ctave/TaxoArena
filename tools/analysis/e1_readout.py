"""EMBEDDER-CROSS-FLAT E1 READOUT (E1-minimal = RP09): FLAT C1 / C2 / L1 per arm at its own k, FILING (paired McNemar on the
3,445 against af_clean_s42), F-E1, P3 / P4 / P7, the reading table; zero calls.

REGISTRATION OF RECORD: docs/judge_v2_program.md section "## Registered 2026-09-27 (before any code or call) — EMBEDDER-CROSS-FLAT:
is the FLAT partition result (and the tree's filing) a property of qwen3's space or of the method ..." (L21705-L21730), lines
"E1-minimal (= RP09; W2)" (with its C-E1R-4 bracket: the two declared configs), "E1 criteria", "READING TABLE", SUPPORT (a)-(g),
PREDICTIONS P3 / P4, FALSIFIER (its F-E1 bracket, added pre-data at L22177: F-E1 FIRES iff FILING is HELD-WORSE; P7 0.60);
E1-ROUTE C3's D-PR-1 bracket (L22192: "E1's FLAT readout prints [EMB-GUARD] itself"); the post-run review of the builds
docs/reviews/POSTRUN_e1_route_builds.md (ba32fbc6): B-PB-1 (N-card's in-run JVM validation numbers are never read or quoted),
C-PB-1 (the corpus DB's -wal: pool readers refuse until the data-steward's checkpoint), C-PB-2 (the pinned arm files' queries
tables resolve only 5,706 of the 8,125 fit ids: id -> text comes from main's embeddings_cache.db queries, vectors come from the
PINNED arm file by text; no working copy is ever read). The FLAT criteria are FLAT-MIX-MMLU's (L20672-L20735, "READOUTS AND
CRITERIA"), verbatim, with T = the E1 tree and V = a flat vMF mixture at the TREE'S OWN leaf count. The registration governs.

LAUNCH SEQUENCE (run-operator; zero calls; ONE single-threaded python process; a pool reader (rule 7): never inside a
construction; AFTER the data-steward's C-PB-1 checkpoint of mmlu_pro_dataset_cache_v2.db-wal):
  python tools/analysis/e1_readout.py --selftest     # synthetic; executes dry_run() and run() end to end on fixtures
  python tools/analysis/e1_readout.py --mutants      # every declared mutant must be KILLED by the selftest
  python tools/analysis/e1_readout.py --dry-run      # pool line first; pins, denominators, guards, plan; NO measure
  python tools/analysis/e1_readout.py --dry-run --eval-db-copy <scratch dir>   # BEFORE C-PB-1 only: reads a checkpointed
                                                     # scratch copy of the corpus DB (db + wal copied, originals re-hashed)
  python tools/analysis/e1_readout.py --run          # fits + measures + verdicts; outcome of record WRITE-ONCE (mode x)
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree.

INPUTS (each printed with its pin; any mismatch REFUSES):
  pool       pool_guard.assert_pool_of_record("p2dca21ab5f4ef3ae") FIRST; held-out = its 3,445 judgeable questions and train =
             the other 8,324 distinct mmlu_pro texts (anchor_free_readout.corpus, the FLAT readout's sets); keyed = the 10,925
             questions of free_tests_f4_f7.keyed_questions.
  fit set    the 8,125 root-placed TRAIN ids of each E1 snapshot (flat_mix_mmlu.fit_set(snapshot, 8125): snapshots.db graph,
             id -> text through MAIN's embeddings_cache.db queries table, read-only); ASSERTED equal, as a text set, to
             af_clean_s42's fit set (the same TRAIN; content-closed under stem_key at norm-v1).
  trees      N-raw  experiment_results/e1_route/E1_nomic_raw/seed_42, snapshot 20261002_035009, 84 leaves (PRIMARY)
             N-card experiment_results/e1_route/E1_nomic_card/seed_42, snapshot 20261002_035237, 77 leaves (SECONDARY)
             af_clean_s42 (flat_mix_mmlu.T_RUN / T_SNAPSHOT), 82 leaves: the FILING comparator, read in qwen3's space.
             Each E1 run dir: manifest embedding_model nomic-embed-text:latest, reserved_pool_id p2dca, embedding_cache_
             source_sha256 = the registrar's arm pin; diagnostics/config.toml LF blob = the declared config blob (C-E1R-4);
             the run dir's last dag snapshot leaves = the snapshots.db graph leaves (ids equal, vmfMu within 1e-5).
  vectors    qwen3: the DB of record in place (ruling R2). nomic_raw / nomic_card: ONLY embedder_arms.open_arm_reader on the
             DIR experiment_results/embedder_cross (copy-only, provenance, registrar pin experiment_configs/embedder_cross_
             arm_pins.json), read BY TEXT; sliced to 256 and renormalised (the readers' rule). Never an e1_route_work file.
  guards     [EMB-GUARD] per arm: embedder_guard.guard() (the record's arithmetic, unchanged) over EVERY accepted split site of
             the arm's snapshot, on a TEXT-JOINED view: queries(id -> text) from main's queries table and embeddings(text ->
             the pinned arm's raw blob), so all 8,125 ids resolve (C-PB-2); af_clean_s42 by flat_mix_mmlu.embedding_guard_flat
             (qwen3, the DB of record). Discriminator, printed: the N-raw tree on the card vectors must REFUSE (else REFUSED).

WHAT IS COMPUTED (--run)
  per arm a (N-raw PRIMARY, N-card SECONDARY), k_a = its leaf count: T = flatLeaf (nearest vmfMu by cosine; FLAT's rule);
  V0-V4 = flat_mix_mmlu.vmf_em(fit, k_a, s) (ruling B6: a degenerate seed REFUSES; E0b's ruling (a) does not apply to E1);
  K0-K4 = flat_mix_mmlu.spherical_kmeans (BESIDE, reported only). M1 = flat_mix_mmlu.m1_block (cell majority from the readout's
  train texts, held-out top-1; Wilson); M2 = flat_mix_mmlu.m2_block (F6 key-only LOO Brier improvement x1000 on the keyed set).
  C1: M1(T) - M1(V0) > spread_V(M1) AND the twin-group bootstrap 95% CI > 0; C2 likewise on M2 with F6's boot_mean_ci;
  L1 FIRES iff on M1 or M2, M(T) - M(V0) < -spread_V(M) AND the CI < 0 (flat_mix_mmlu.criterion / loss, strict).
  FILING: per held-out question, hit = (the question's category == the majority train label of its flatLeaf leaf); N-raw's
  hits in nomic space minus af_clean_s42's hits in qwen3 space (each tree in its own embedder; the readout's train set for
  both). b = N right / af wrong, c = N wrong / af right, n = 3,445, diff = (b - c) / n; THE DECIDING INTERVAL is the paired
  McNemar (Wald) 95% interval diff -/+ 1.96 sqrt(b + c - (b - c)^2 / n) / n (Support (d)'s sqrt(d / n) form); HELD-WORSE iff
  hi < 0, HELD-BETTER iff lo > 0, UNDETERMINED otherwise. Beside (never deciding): the exact two-sided McNemar p
  (systematic_budget.mcnemar_edge) and the twin-group bootstrap percentile interval. F-E1 FIRES iff N-raw's FILING is
  HELD-WORSE. N-card's FLAT and FILING are printed SECONDARY: never F-E1, P3, P4, P7 or the reading table.
  Printed beside: leaf count, root axis (the two depth-1 nodes: held-out shares, top categories, cosine between their
  vmfMu), ARI to af_clean_s42 (leaf cells of the held-out 3,445 and of the 8,125 fit texts, each tree routed in its own space),
  Support (a)-(g) with the measured DEFF (Kish m-bar of the held-out twin groups), n_eff, discordance, SE, MDE80, the
  registered (f) verbatim and the tightening-only tag; the reading table with FLAT-GENERALITY's k read from its outcome file
  (sha256 pinned); P3 / P4 / P7 scored with Brier.

BUILDER DECLARATIONS (for the registrar; none changes a registered word):
  D1 "flatLeaf top-1" = anchor_free_readout's held-out top-1 (cell majority from the 8,324 readout train texts), i.e. FLAT's M1
     per question; filing and FLAT's M1 therefore share one per-question vector per tree.
  D2 the "paired McNemar interval" is the Wald interval of the paired difference (the form whose SE Support (d) plans,
     sqrt(d / n)); the exact McNemar p and the bootstrap interval are printed beside and never decide.
  D3 N-card (SECONDARY): its card file lacks 82 texts (POSTRUN claim 8: 81 unlinked mmlu_pro rows + 1 eval-linked text, all
     outside fit, held-out and keyed); its M1 majority is taken from the train texts that HAVE a card vector (8,242 of 8,324
     expected), disclosed with the count and the sha256-16 of the missing texts; a missing fit / held-out / keyed text REFUSES.
     N-raw (PRIMARY) must miss none (REFUSED otherwise): its M1 is FLAT's verbatim.
  D4 M3 / M4 (FLAT's descriptive measures) and FLAT-MIX-MMLU's reading table T-1..T-5 are not registered for E1: not computed.
  D5 P4 is HELD iff the observed filing difference lies in the registered 80% interval [-0.08, 0.00], endpoints inclusive.
  D6 not applicable here, printed as such: tie conventions A / B (no judge verdicts; hits are 0 / 1) and wrong(established)
     (no model pairs).
  D7 the ARI is DESCRIPTIVE ("ARI to af_clean_s42 printed"); the root axis is the depth-1 bipartition (both E1 trees have 2
     depth-1 nodes); neither is scored.

OUTPUTS: experiment_results/e1_route/e1_readout_outcome.txt and e1_readout_partitions.csv, --run only, WRITE-ONCE (mode x;
--run REFUSES before any work if either exists). Pins BEFORE and AFTER (arm files, main embeddings_cache.db, the corpus DB
read, the three snapshot rows, the three run dirs' dag_snapshots.jsonl, the FLAT-GENERALITY outcome); any change REFUSES.

SELFTEST (--selftest) and MUTANTS (--mutants): see the docstrings of selftest() and MUTANTS (the table is in the commit message).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import io
import re
import sys
import json
import math
import time
import shutil
import struct
import hashlib
import sqlite3
import argparse
import tempfile
import contextlib
import subprocess
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

TAG = "[E1-READOUT]"


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def pins_of(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest(), lf16=hashlib.sha256(d).hexdigest()[:16],
                crlf16=hashlib.sha256(d.replace(b"\n", b"\r\n")).hexdigest()[:16])


def fmt_pins(p):
    return "blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (p["blob"][:8], p["lf16"], p["crlf16"])


# the imported instrument is the pinned one, or nothing runs (LF git blobs at main 40d4b6cd)
IMPORT_PINS = {"embedder_cross_flat.py": "7868e8589fee107b15d3c535966b840cd648f771", "flat_mix_mmlu.py": "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2",
               "embedder_arms.py": "2073d1315981a30464037913b85ce2bf8838aa00", "embedder_guard.py": "3fd9aea5b220828f7e6bcb3f115c43aa6743218d",
               "anchor_free_readout.py": "514e74daebb5a631f65e3ed586a856a791fb5a60", "free_tests_f4_f7.py": "f0749d6133e030422671d15af69b6cff94ea1298",
               "systematic_budget.py": "54ca7b22bf3274ac47da7ec10be948e41aafd50c"}
for _f, _b in IMPORT_PINS.items():
    _p = pins_of(os.path.join(HERE, _f))
    if _p["blob"] != _b:
        refuse("pin mismatch on tools/analysis/%s: %s, pinned blob:%s" % (_f, fmt_pins(_p), _b[:8]))
import embedder_cross_flat as ECF   # noqa: E402  (its own import pins; installs flat_mix_mmlu's read-only connect guard)
import systematic_budget as SB      # noqa: E402  mcnemar_edge (the record's exact McNemar)
FM, EA, EG, AF, F = ECF.FM, ECF.EA, ECF.EG, ECF.AF, ECF.F

POOL_ID = "p2dca21ab5f4ef3ae"
DIM = 256
SEEDS = (0, 1, 2, 3, 4)
ARM_DIR = os.path.join("experiment_results", "embedder_cross")
EVAL_DB_NAME = "mmlu_pro_dataset_cache_v2.db"
NOMIC = "nomic-embed-text:latest"
E1_ARMS = (
    dict(name="N-raw", role="PRIMARY", arm="nomic_raw", run=os.path.join("experiment_results", "e1_route", "E1_nomic_raw", "seed_42"),
         snapshot="20261002_035009_Headless_Run_Auto_ge", leaves=84, config_blob="edace9f9534d0ca4272852baf9c55c91304d63aa"),
    dict(name="N-card", role="SECONDARY", arm="nomic_card", run=os.path.join("experiment_results", "e1_route", "E1_nomic_card", "seed_42"),
         snapshot="20261002_035237_Headless_Run_Auto_ge", leaves=77, config_blob="67bcdc2b1ad134c9b029eb1f9fb618764a836937"),
)
AF_LEAVES = 82
EXPECT = dict(fit=8125, heldout=3445, keyed=10925, train=8324)
FG_OUTCOME = os.path.join("experiment_results", "flat_generality", "flat_generality_outcome.txt")
FG_SHA256 = "ffcb416da8e11c9e5f3467812a630ec1ddf1ebb4aeb83a95a159feaa7af49f3d"   # sha256 of the LF rendering (blob:cbbd2f6b)
FG_K_RE = re.compile(r"^D2: the loss appears in (\d) of 3 qwen3 re-draws", re.M)
IDENTITY = dict(m1="0.727 [0.712, 0.741]", m2="+12.785")      # af_clean_s42 through FLAT's path (FLAT-MIX-MMLU / FG identity)
SUPPORT = dict(se_m1=0.00663, mde_m1=0.0186, se_m2=0.357e-3, mde_m2=1.00e-3, d_pilot=0.15, se_f=0.00660, mde_f=0.0185)
P3_PROB = 0.55
P4 = (-0.04, (-0.08, 0.00), 0.60)
P7_PROB = 0.60
Z95 = 1.959963984540054
OUT_DIR = os.path.join("experiment_results", "e1_route")
OUTCOME = "e1_readout_outcome.txt"
PART_CSV = "e1_readout_partitions.csv"
VERDICT_F = ("(f) VERDICT LINE (registered): ... E1 filing SCOREABLE (P4 -0.04 beyond 0.0185); E1 FLAT L1 SCOREABLE as in "
             "FLAT-GENERALITY; every cross-arm contrast DESCRIPTIVE-ONLY.")
READING = {
    "fires": "the loss appears in %d of 3 qwen3 re-draws and in the one nomic draw, on one corpus",
    "not": "in %d of 3 qwen3 re-draws, not in the one nomic draw (embedder contrast DESCRIPTIVE)",
    "low": "in %d of 3 re-draws (embedder contrast UNDETERMINED)",
}
FE1_FIRES = ("F-E1 FIRES: N-raw's FILING is HELD-WORSE (the paired 95% interval wholly below 0): it overturns the framing's "
             "planned SQ5 word \"the method's\" for the tree-FILING clause on MMLU-Pro (one corpus, one draw per arm); it moves "
             "no recorded number; Support (g): never a scored embedder contrast")
FE1_NOT = "F-E1 did not fire (FILING HELD-BETTER or UNDETERMINED); never \"the filing is embedder-invariant\""
BPB1 = ("B-PB-1: N-card's in-run JVM validation block is not read and not quoted (no file under a run's validation/ is opened); "
        "every in-run comparison here is on the 3,445")


def say(L, s=""):
    print(s)
    L.append(s)


def data_path(rel):
    return os.path.join(pool_guard.DATA_ROOT, rel)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def unit(v):
    v = np.asarray(v, dtype=np.float64)[:DIM]
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def sha16_texts(texts):
    return hashlib.sha256("\n".join(sorted(texts)).encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------------------------------------------ the corpus DB (C-PB-1)
def eval_db_copy(target_dir, L):
    """BEFORE C-PB-1 only (--dry-run): copy mmlu_pro_dataset_cache_v2.db AND its -wal into target_dir (fresh names only), the
    originals re-hashed equal before and after the copy, then checkpoint the COPY (a write to the scratch copy only) so the
    read-only guards admit it. Returns the copy's path."""
    src = data_path(EVAL_DB_NAME)
    dst = os.path.join(os.path.abspath(target_dir), EVAL_DB_NAME)
    if not os.path.isdir(target_dir):
        refuse("--eval-db-copy %s is not an existing directory" % target_dir)
    if os.path.normcase(os.path.abspath(target_dir)) == os.path.normcase(os.path.abspath(pool_guard.DATA_ROOT)):
        refuse("--eval-db-copy %s is the data root: the original is never the copy" % target_dir)
    for sfx in ("", "-wal", "-shm"):
        if os.path.lexists(dst + sfx):
            refuse("%s exists: the copy is written once into a fresh directory" % (dst + sfx))
    before = {s: sha256_file(src + s) for s in ("", "-wal") if os.path.exists(src + s)}
    for s in before:
        shutil.copyfile(src + s, dst + s)
    after = {s: sha256_file(src + s) for s in before}
    copied = {s: sha256_file(dst + s) for s in before}
    if not (before == after == copied):
        refuse("the corpus DB changed during the copy or the copy differs: before %s after %s copy %s" % (before, after, copied))
    raw = getattr(sqlite3.connect, "_raw", sqlite3.connect)
    con = raw(dst)
    try:
        con.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        con.close()
    for s in ("-wal", "-journal"):
        if os.path.exists(dst + s) and os.path.getsize(dst + s) > 0:
            refuse("the scratch copy's %s is non-empty after the checkpoint" % s)
    say(L, "[EVAL-DB-COPY] %s (+ -wal %s) copied to %s; originals sha256 %s (wal %s) equal before / after / copy; the COPY was "
           "checkpointed (scratch write only). C-PB-1 OPEN: --run reads the DB of record after the data-steward's checkpoint"
        % (src, "present" if "-wal" in before else "absent", dst, before[""][:16], before.get("-wal", "-")[:16]))
    return dst


def point_eval_db(path):
    """The corpus DB every reader opens (anchor_free_readout, rejudge_grok via free_tests_f4_f7, pool_guard's db override)."""
    AF.EVAL_DB = path
    FM.RJ.EVAL_DB = path
    F.rj.EVAL_DB = path


# ------------------------------------------------------------------------------------------------ arms and guards
def load_space(arm_name, need, L, allow_missing=None):
    """-> ({text: 256-d unit vector}, {text: raw blob} for the asked texts present, missing texts, info). qwen3 in place
    (no flag, ruling R2); nomic arms ONLY through embedder_arms.open_arm_reader on ARM_DIR (copy-only, provenance, registrar
    pin), read BY TEXT. allow_missing: the set of texts that may lack a vector (D3); any other missing text REFUSES."""
    arm = EA.ARMS[arm_name]
    buf = io.StringIO()
    with ECF.fm_session(), contextlib.redirect_stdout(buf):
        if arm_name == "qwen3_raw":
            if EA.open_arm_reader(FM, arm_name, None, pool_guard.DATA_ROOT) is not None:
                refuse("qwen3_raw must be read in place with no flag (ruling R2)")
            db = data_path(EG.DB_OF_RECORD)
        else:
            db = EA.open_arm_reader(FM, arm_name, data_path(ARM_DIR), pool_guard.DATA_ROOT)
        con = pool_guard.open_ro(db)
        try:
            want, blobs = set(need), {}
            for t, blob in con.execute("SELECT query, vector FROM embeddings"):
                if t in want and isinstance(blob, bytes):
                    blobs[t] = blob
            missing = sorted(want - set(blobs))
            bad = [t for t in missing if allow_missing is None or t not in allow_missing]
            if bad:
                refuse("arm %s: %d needed texts have no vector (outside the declared allowance)" % (arm_name, len(bad)))
            EA.arm_read_guard(con, arm, sorted(blobs))
        finally:
            con.close()
        sha = EA._sha(db)
    for line in buf.getvalue().splitlines():
        say(L, "  " + line)
    vec = {t: unit(struct.unpack(">%df" % (len(b) // 4), b)) for t, b in blobs.items()}
    say(L, "ARM %s (%s, %s): file %s sha256 %s; %d of %d needed texts read by text; %d missing%s"
        % (arm_name, arm.model, arm.role, os.path.relpath(db, pool_guard.DATA_ROOT), sha, len(vec), len(want), len(missing),
           (" (sha256-16 of the missing texts %s)" % sha16_texts(missing)) if missing else ""))
    return vec, blobs, missing, dict(db=db, sha=sha, model=arm.model, role=arm.role)


def text_join_guard(byid, region_ids, id2text, blobs, model, label, slice_dim=DIM):
    """[EMB-GUARD] on a TEXT-JOINED view (C-PB-2): an in-memory SQLite with queries(id -> text) and embeddings(text -> the arm's
    raw blob), so embedder_guard.guard (the record's arithmetic, unchanged) resolves every member id by text. REFUSES on any
    finding (guard's own refusal)."""
    raw = getattr(sqlite3.connect, "_raw", sqlite3.connect)
    con = raw(":memory:")
    try:
        con.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, distilled_text TEXT)")
        con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        con.executemany("INSERT INTO queries VALUES (?, ?)", sorted(id2text.items()))
        con.executemany("INSERT INTO embeddings VALUES (?, ?)", sorted(blobs.items()))
        return EG.guard(con, label, EG.split_sites(byid), region_ids, slice_dim, model, "the E1 run manifest; text-joined view")
    finally:
        con.close()


def guard_quiet(fn):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = fn()
        return r, None, buf.getvalue()
    except SystemExit as e:
        return None, str(e), buf.getvalue()


def check_run_dir(a, pins, L):
    """manifest, declared config blob, snapshot graph vs the run dir's last dag snapshot. -> (tree, graph)."""
    rd = data_path(a["run"])
    mp = os.path.join(rd, "diagnostics", "run_manifest.json")
    with open(mp, encoding="utf-8") as f:
        man = json.load(f)
    want_sha = pins["arms"][a["arm"]]["sha256"]
    bad = []
    if man.get("embedding_model") != NOMIC:
        bad.append("embedding_model %r" % man.get("embedding_model"))
    if man.get("reserved_pool_id") != POOL_ID:
        bad.append("reserved_pool_id %r" % man.get("reserved_pool_id"))
    if man.get("embedding_cache_source_sha256") != want_sha:
        bad.append("embedding_cache_source_sha256 %r != the registrar's pin %s" % (man.get("embedding_cache_source_sha256"), want_sha))
    cb = pins_of(os.path.join(rd, "diagnostics", "config.toml"))["blob"]
    if cb != a["config_blob"]:
        bad.append("config.toml blob %s != declared %s" % (cb, a["config_blob"]))
    tree = AF.load_tree(rd)
    g = FM.load_snapshot_graph(a["snapshot"])
    gl = {k: n["vmfMu"] for k, n in g["byid"].items() if not n.get("childIds")}
    tl = dict(zip(tree["leaf_ids"], [n["vmfMu"] for n in tree["leaves"]]))
    if set(gl) != set(tl):
        bad.append("snapshot leaves != run dir leaves")
    else:
        dmax = max(float(np.max(np.abs(np.asarray(tl[k]) - np.asarray(gl[k])))) for k in tl)
        if dmax > 1e-5:
            bad.append("leaf vmfMu differ by %.2e" % dmax)
    if len(tree["leaves"]) != a["leaves"]:
        bad.append("%d leaves, registered %d" % (len(tree["leaves"]), a["leaves"]))
    if tree["dim"] != DIM:
        bad.append("slice %d" % tree["dim"])
    if bad:
        refuse("%s run dir %s: %s" % (a["name"], a["run"], "; ".join(bad)))
    say(L, "TREE %s (%s): %s | snapshot %s graph sha256 %s | %d leaves, %d nodes, %d depth-1, slice %d | manifest commit %s, model %s, "
           "pool %s, source sha256 %s (== registrar pin) | config.toml blob:%s (== declared, C-E1R-4)"
        % (a["name"], a["role"], a["run"].replace(os.sep, "/"), a["snapshot"], g["sha"][:16], len(tree["leaves"]), tree["nodes"],
           len(tree["d1_ids"]), tree["dim"], (man.get("commit") or "?")[:8], man["embedding_model"], man["reserved_pool_id"],
           want_sha[:16], cb[:8]))
    return tree, g


def read_fg_k(path=None, sha=None):
    p = path if path is not None else os.path.join(ROOT, FG_OUTCOME)
    want = FG_SHA256 if sha is None else sha
    with open(p, "rb") as f:
        got = hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()     # the LF rendering is of record
    if got != want:
        refuse("FLAT-GENERALITY outcome %s sha256-lf %s != pinned %s" % (p, got, want))
    with open(p, encoding="utf-8") as f:
        m = FG_K_RE.search(f.read().replace("\r\n", "\n"))
    if m is None:
        refuse("FLAT-GENERALITY outcome %s carries no 'D2: the loss appears in k of 3' line" % p)
    return int(m.group(1)), got


def take_pins(arm_paths, eval_db, snapshots, runs, fg):
    out = {}
    for p in list(arm_paths) + [data_path(EG.DB_OF_RECORD), eval_db, fg]:
        out["file:" + os.path.basename(p)] = sha256_file(p)
    for sid in snapshots:
        out["snapshot:" + sid] = FM.load_snapshot_graph(sid)["sha"]
    for rd in runs:
        out["dag:" + rd.replace(os.sep, "/")] = sha256_file(os.path.join(data_path(rd), "dag_snapshots.jsonl"))
    return out


# ------------------------------------------------------------------------------------------------ the real world (loader)
def load_real(L, eval_copy_dir=None, run_mode=False):
    """Every real input, with the pool line first, pins, counts, hygiene and the per-arm guards. -> world dict."""
    eval_db = data_path(EVAL_DB_NAME)
    if eval_copy_dir is not None:
        if run_mode:
            refuse("--eval-db-copy is admitted with --dry-run only (the run of record reads the DB of record after C-PB-1)")
        eval_db = eval_db_copy(eval_copy_dir, L)
    point_eval_db(eval_db)
    pid = pool_guard.assert_pool_of_record(POOL_ID, db=None if eval_copy_dir is None else eval_db)
    say(L, "pool %s (pool_guard.assert_pool_of_record: id file and reserved_pool rows agree; %s)"
        % (pid, "the DB of record" if eval_copy_dir is None else "the checkpointed scratch copy (dry-run only)"))
    say(L, "[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    say(L, "[SCRIPT] tools/analysis/e1_readout.py %s" % fmt_pins(pins_of(os.path.abspath(__file__))))
    for f_ in IMPORT_PINS:
        say(L, "[PIN] tools/analysis/%s %s (verified)" % (f_, fmt_pins(pins_of(os.path.join(HERE, f_)))))
    say(L, "[DATA] DATA_ROOT %s" % pool_guard.DATA_ROOT)
    say(L, BPB1)
    with open(EA.ARM_PINS_FILE, encoding="utf-8") as f:
        pins = json.load(f)
    say(L, "[PIN] %s blob:%s; nomic_raw %s, nomic_card %s" % (os.path.relpath(EA.ARM_PINS_FILE, ROOT).replace(os.sep, "/"),
        pins_of(EA.ARM_PINS_FILE)["blob"][:8], pins["arms"]["nomic_raw"]["sha256"][:16], pins["arms"]["nomic_card"]["sha256"][:16]))
    k_fg, fg_sha = read_fg_k()
    say(L, "[PIN] %s sha256-lf %s (pinned): FLAT-GENERALITY k = %d" % (FG_OUTCOME.replace(os.sep, "/"), fg_sha[:16], k_fg))
    arm_paths = [data_path(os.path.join(ARM_DIR, EA.cache_file(EA.ARMS[a["arm"]]))) for a in E1_ARMS]
    pin_args = (arm_paths, eval_db, [a["snapshot"] for a in E1_ARMS] + [FM.T_SNAPSHOT], [a["run"] for a in E1_ARMS] + [FM.T_RUN],
                os.path.join(ROOT, FG_OUTCOME))
    before = take_pins(*pin_args)
    for k, v in sorted(before.items()):
        say(L, "[PIN before] %s %s" % (k, v))
    # trees
    trees, graphs = {}, {}
    for a in E1_ARMS:
        trees[a["name"]], graphs[a["name"]] = check_run_dir(a, pins, L)
    trees["af_clean_s42"] = FM.load_T("T")
    say(L, "TREE af_clean_s42 (FILING comparator, qwen3): %d leaves, %d nodes, %d depth-1, slice %d"
        % (len(trees["af_clean_s42"]["leaves"]), trees["af_clean_s42"]["nodes"], len(trees["af_clean_s42"]["d1_ids"]),
           trees["af_clean_s42"]["dim"]))
    # fit set: id -> text from MAIN's queries table (C-PB-2)
    fits, id2text = {}, {}
    for a in E1_ARMS:
        texts, g, ids, text = FM.fit_set(snapshot=a["snapshot"], fit_n=EXPECT["fit"])
        fits[a["name"]] = texts
        id2text[a["name"]] = text
        say(L, "FIT SET %s: snapshot %s root %s: %d member ids -> %d distinct texts via MAIN embeddings_cache.db queries (ASSERTED %d)"
            % (a["name"], a["snapshot"], g["root"], len(ids), len(texts), EXPECT["fit"]))
    af_texts, _g, _i, _t = FM.fit_set()
    for a in E1_ARMS:
        if fits[a["name"]] != af_texts:
            refuse("%s's fit set differs from af_clean_s42's (the same TRAIN is registered)" % a["name"])
    say(L, "  both E1 fit sets == af_clean_s42's fit set (%d texts, sha256-16 %s)" % (len(af_texts), sha16_texts(af_texts)))
    train, heldout, cs = AF.corpus(POOL_ID)
    keyed = F.keyed_questions()
    cat = dict(train)
    fit = [(t, cat[t]) for t in af_texts if t in cat]
    if len(fit) != len(af_texts):
        refuse("%d fit texts are not among the readout's train texts" % (len(af_texts) - len(fit)))
    W = dict(fit=fit, train=train, heldout=heldout, keyed=keyed, k_fg=k_fg, identity=IDENTITY, trees=trees)
    counts(W, L, EXPECT)
    hygiene(W, L)
    # vectors (by text) and guards
    need = sorted(set(t for t, _ in train) | set(t for t, _ in heldout) | set(keyed[3].values()))
    core = set(t for t, _ in fit) | set(t for t, _ in heldout) | set(keyed[3].values())
    allowance = set(t for t, _ in train) - core
    spaces, train_by = {}, {}
    vq, _bq, mq, _iq = load_space("qwen3_raw", need, L)
    spaces["af_clean_s42"] = vq
    for a in E1_ARMS:
        v, blobs, miss, _info = load_space(a["arm"], need, L, allow_missing=allowance if a["role"] == "SECONDARY" else None)
        spaces[a["name"]] = v
        tr = [x for x in train if x[0] in v]
        train_by[a["name"]] = tr
        if miss:
            say(L, "  D3 (%s, SECONDARY): M1's cell majority from %d of %d train texts (%d train-only texts without a vector; "
                   "none in fit / held-out / keyed)" % (a["name"], len(tr), len(train), len(miss)))
        g = graphs[a["name"]]
        txt = id2text[a["name"]]
        say(L, "[EMB-GUARD] %s tree on the pinned %s arm (text-joined view, every split site):" % (a["name"], a["arm"]))
        res, err, out = guard_quiet(lambda: text_join_guard(g["byid"], lambda s: FM.region_query_ids(s["id"], g["byid"]), txt,
                                                             {t: b for t, b in blobs.items()}, NOMIC,
                                                             "%s (text-joined: MAIN queries x %s)" % (a["arm"], os.path.basename(_info["db"]))))
        for line in out.splitlines():
            say(L, "  " + line)
        if err:
            refuse("[EMB-GUARD] %s: %s" % (a["name"], err))
        a["_blobs"] = blobs
    train_by["af_clean_s42"] = train
    # discriminator: the N-raw tree on the CARD vectors must refuse
    g = graphs["N-raw"]
    _r, err, out = guard_quiet(lambda: text_join_guard(g["byid"], lambda s: FM.region_query_ids(s["id"], g["byid"]), id2text["N-raw"],
                                                       E1_ARMS[1]["_blobs"], NOMIC, "DISCRIMINATOR N-raw tree x nomic_card"))
    mline = [l for l in out.splitlines() if "vmfMu cosine" in l]
    say(L, "[EMB-GUARD] DISCRIMINATOR N-raw tree on the nomic_card vectors: %s | %s" % ("REFUSE (expected)" if err else "ADMIT",
                                                                                          mline[0].strip() if mline else "-"))
    if not err:
        refuse("the guard admits the N-raw tree on the card vectors: it does not discriminate the arms")
    for a in E1_ARMS:
        a.pop("_blobs", None)
    say(L, "[EMB-GUARD] af_clean_s42 on qwen3 (the DB of record; flat_mix_mmlu.embedding_guard_flat):")
    _r, err, out = guard_quiet(lambda: FM.embedding_guard_flat())
    for line in out.splitlines():
        say(L, "  " + line)
    if err:
        refuse("[EMB-GUARD] af_clean_s42: %s" % err)
    W.update(spaces=spaces, train_by=train_by, pins_before=before, pins_fn=lambda: take_pins(*pin_args), real=True)
    return W


def counts(W, L, expect):
    got = dict(fit=len(W["fit"]), heldout=len(W["heldout"]), keyed=len(W["keyed"][4]), train=len(W["train"]))
    groups, G = FM.twin_groups([t for t, _ in W["heldout"]])
    say(L, "DENOMINATORS: fit %d (registered 8,125), held-out %d (registered 3,445; %d stem_key twin groups, Kish m-bar %.4f), "
           "keyed %d (registered 10,925), readout train %d (FLAT's 8,324); FILING n = held-out %d paired (registered 3,445)"
        % (got["fit"], got["heldout"], G, FM.kish_mbar(groups), got["keyed"], got["train"], got["heldout"]))
    if expect is not None:
        bad = {k: (got[k], v) for k, v in expect.items() if got[k] != v}
        if bad:
            refuse("the denominators differ from the registration: %s (got, registered)" % bad)
    return got


def hygiene(W, L):
    fit = set(t for t, _ in W["fit"])
    ho = set(t for t, _ in W["heldout"])
    tr = set(t for t, _ in W["train"])
    fk = set(FM.split_side.stem_key(t) for t in fit)
    keys = sum(1 for t in ho if FM.split_side.stem_key(t) in fk)
    say(L, "HYGIENE: held-out texts in the fit %d; held-out stem_keys in the fit %d; held-out texts in the readout train %d (all "
           "must be 0)" % (len(ho & fit), keys, len(ho & tr)))
    if ho & fit or keys or ho & tr:
        refuse("held-out content reaches the fit or the train side")


# ------------------------------------------------------------------------------------------------ measures and verdicts
def tree_fn(tree):
    ids, mu = tree["leaf_ids"], tree["leaf_mu"]
    return lambda Q: [ids[i] for i in FM.nearest_assign(Q, mu)]


def part_fn(p):
    if p["rule"] == "map":
        return lambda Q: list(FM.map_assign(Q, p["mu"], p["kappa"], p["pi"]))
    return lambda Q: list(FM.nearest_assign(Q, p["centers"]))


def default_fit(X, k):
    """V0-V4 (vmf_em; ruling B6 refuses a degenerate seed) and K0-K4 (spherical k-means, reported only)."""
    parts = {}
    for s in SEEDS:
        r = FM.vmf_em(X, k, s)
        parts["V%d" % s] = dict(rule="map", mu=r["mu"], kappa=r["kappa"], pi=r["pi"], iters=r["iters"], converged=r["converged"])
    for s in SEEDS:
        r = FM.spherical_kmeans(X, k, s)
        parts["K%d" % s] = dict(rule="nearest", centers=r["centers"], iters=r["iters"], converged=r["converged"])
    return parts


def mat(vec, texts):
    return np.stack([vec[t] for t in texts])


def measure(fn, vec, train, heldout, keyed):
    Qt, Qh = mat(vec, [t for t, _ in train]), mat(vec, [t for t, _ in heldout])
    sc, hits, kh = FM.m1_block(fn, Qt, Qh, train, heldout)
    veck = {t: vec[t] for t in keyed[3].values()}
    m2 = FM.m2_block(fn, keyed, veck)
    if m2["n"] != len(keyed[4]):
        refuse("M2 scored on %d keyed questions, the registered denominator is %d" % (m2["n"], len(keyed[4])))
    return dict(m1=sc["acc"], m1_lo=sc["lo"], m1_hi=sc["hi"], sc=sc, per1=hits, cells_h=kh, m2=m2["mean"], per2=m2["per_q"], n2=m2["n"])


def paired(a, b, groups):
    d1 = a["per1"] - b["per1"]
    lo1, hi1 = FM.twin_boot_ci(d1, groups)
    common = [q for q in a["per2"] if q in b["per2"]]
    d2 = np.array([a["per2"][q] - b["per2"][q] for q in common])
    lo2, hi2 = F.boot_mean_ci(d2)
    return dict(m1=(float(d1.mean()), lo1, hi1), m2=(float(d2.mean()), lo2, hi2))


def mcnemar(hn, ha):
    """The paired McNemar (Wald) interval of mean(hn - ha) (D2), the exact two-sided McNemar p by systematic_budget.mcnemar_edge."""
    hn, ha = np.asarray(hn, dtype=int), np.asarray(ha, dtype=int)
    n = len(hn)
    b = int(((hn == 1) & (ha == 0)).sum())
    c = int(((hn == 0) & (ha == 1)).sum())
    d = (b - c) / n
    se = math.sqrt(max(0.0, (b + c) - (b - c) ** 2 / n)) / n
    K = {i: {"N": int(hn[i]), "A": int(ha[i])} for i in range(n)}
    p, b2, c2 = SB.mcnemar_edge(dict(anchor=0, a="N", b="A"), K, {0: range(n)})
    if (b2, c2) != (b, c):
        refuse("mcnemar_edge counts (%d, %d) != (%d, %d)" % (b2, c2, b, c))
    return dict(n=n, b=b, c=c, diff=d, se=se, lo=d - Z95 * se, hi=d + Z95 * se, p=p, disc=(b + c) / n)


def filing_verdict(lo, hi):
    if hi < 0:
        return "HELD-WORSE"
    if lo > 0:
        return "HELD-BETTER"
    return "UNDETERMINED"


def ari(a, b):
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(list(a), list(b)))


def root_axis(tree, vec, heldout):
    Qh = mat(vec, [t for t, _ in heldout])
    li = FM.nearest_assign(Qh, tree["leaf_mu"])
    d1 = [tree["leaf_d1"][i] for i in li]
    out = []
    for nid in tree["d1_ids"]:
        cats = Counter(c for x, (_, c) in zip(d1, heldout) if x == nid)
        n = sum(cats.values())
        top = ", ".join("%s %.2f" % (c, m / n) for c, m in cats.most_common(3)) if n else "-"
        out.append("%s n=%d (%.3f) top: %s" % (nid, n, n / len(heldout), top))
    cos = float(tree["d1_mu"][0] @ tree["d1_mu"][1]) if len(tree["d1_ids"]) == 2 else float("nan")
    return out, cos, d1


def compute(W, fit_fn=default_fit):
    """The deciding path: identity of the comparator, per-arm FLAT and FILING, F-E1, predictions. -> res."""
    groups, G = FM.twin_groups([t for t, _ in W["heldout"]])
    af = measure(tree_fn(W["trees"]["af_clean_s42"]), W["spaces"]["af_clean_s42"], W["train_by"]["af_clean_s42"], W["heldout"], W["keyed"])
    ident = dict(m1=FM.fmt_m1(af["sc"]), m2="%+.3f" % (1000 * af["m2"]))
    if W.get("identity") is not None and ident != W["identity"]:
        refuse("af_clean_s42 through FLAT's path reads %s, the record's identity is %s" % (ident, W["identity"]))
    res = dict(n=len(W["heldout"]), G=G, mbar=FM.kish_mbar(groups), n_keyed=len(W["keyed"][4]), k_fg=W["k_fg"], af=af, ident=ident,
               arms={}, order=[])
    af_tree = W["trees"]["af_clean_s42"]
    af_fit_cells = tree_fn(af_tree)(mat(W["spaces"]["af_clean_s42"], [t for t, _ in W["fit"]]))
    _ax, _c, af_d1 = root_axis(af_tree, W["spaces"]["af_clean_s42"], W["heldout"])
    for a in E1_ARMS:
        name = a["name"]
        if name not in W["trees"]:
            continue
        tree, vec, train = W["trees"][name], W["spaces"][name], W["train_by"][name]
        k = len(tree["leaf_ids"])
        X = mat(vec, [t for t, _ in W["fit"]])
        parts = fit_fn(X, k)
        if sorted(parts) != sorted(["V%d" % s for s in SEEDS] + ["K%d" % s for s in SEEDS]):
            refuse("%s: partitions %s, expected V0-V4 and K0-K4" % (name, sorted(parts)))
        M = {"T": measure(tree_fn(tree), vec, train, W["heldout"], W["keyed"])}
        for pn in sorted(parts):
            M[pn] = measure(part_fn(parts[pn]), vec, train, W["heldout"], W["keyed"])
            M[pn].update(iters=parts[pn]["iters"], converged=parts[pn]["converged"])
        spread_V = {m: FM.spread([M["V%d" % s][m] for s in SEEDS]) for m in ("m1", "m2")}
        spread_K = {m: FM.spread([M["K%d" % s][m] for s in SEEDS]) for m in ("m1", "m2")}
        pv, pk = paired(M["T"], M["V0"], groups), paired(M["T"], M["K0"], groups)
        c1 = FM.criterion(pv["m1"][0], spread_V["m1"], pv["m1"][1], pv["m1"][2])
        c2 = FM.criterion(pv["m2"][0], spread_V["m2"], pv["m2"][1], pv["m2"][2])
        l1m = [m for m in ("m1", "m2") if FM.loss(pv[m][0], spread_V[m], pv[m][1], pv[m][2])]
        beside = dict(c1=FM.criterion(pk["m1"][0], spread_K["m1"], pk["m1"][1], pk["m1"][2]),
                      c2=FM.criterion(pk["m2"][0], spread_K["m2"], pk["m2"][1], pk["m2"][2]),
                      l1=[m for m in ("m1", "m2") if FM.loss(pk[m][0], spread_K[m], pk[m][1], pk[m][2])])
        mc = mcnemar(M["T"]["per1"], af["per1"])
        blo, bhi = FM.twin_boot_ci(M["T"]["per1"] - af["per1"], groups)
        mc.update(boot=(blo, bhi), verdict=filing_verdict(mc["lo"], mc["hi"]))
        ax, cos, d1 = root_axis(tree, vec, W["heldout"])
        fit_cells = tree_fn(tree)(X)
        res["arms"][name] = dict(role=a["role"], k=k, M=M, spread_V=spread_V, spread_K=spread_K, pv=pv, pk=pk, c1=bool(c1), c2=bool(c2),
                                 l1=l1m, beside=beside, filing=mc, axis=ax, axis_cos=cos,
                                 ari_ho=ari(M["T"]["cells_h"], af["cells_h"]), ari_fit=ari(fit_cells, af_fit_cells),
                                 ari_d1=ari(d1, af_d1), n_train=len(train), n_train_all=len(W["train"]))
        res["order"].append(name)
    if "N-raw" not in res["arms"]:
        refuse("the PRIMARY arm N-raw is absent")
    r = res["arms"]["N-raw"]
    res["fe1"] = bool(r["filing"]["verdict"] == "HELD-WORSE")
    res["l1_raw"] = bool(len(r["l1"]) > 0)
    return res


def fmt_m(metric, x):
    return "%+.4f" % x if metric == "m1" else "%+.3f" % (1000 * x)


def brier(p, event):
    return (p - (1.0 if event else 0.0)) ** 2


def reading_line(k, l1):
    if k >= 2:
        return READING["fires"] % k if l1 else READING["not"] % k
    return READING["low"] % k


def render(res):
    """Every registered criterion, prediction and falsifier line; all branches are executed by the selftest."""
    L = []
    n = res["n"]
    L.append("%s EMBEDDER-CROSS-FLAT E1 readout (zero calls). Registration L21705-L21730 (E1 criteria, READING TABLE, SUPPORT, "
             "P3 / P4, FALSIFIER with F-E1)." % TAG)
    L.append(BPB1)
    L.append("COMPARATOR af_clean_s42 (qwen3, 82 leaves; FLAT's identity): M1 %s, M2 %s x1e-3 (the record: %s / %s)"
             % (res["ident"]["m1"], res["ident"]["m2"], IDENTITY["m1"], IDENTITY["m2"]))
    L.append("DENOMINATORS: held-out n = %d (%d twin groups, Kish m-bar %.4f); keyed %d; FILING paired on the %d" % (n, res["G"], res["mbar"],
             res["n_keyed"], n))
    for name in res["order"]:
        r = res["arms"][name]
        sec = r["role"] == "SECONDARY"
        pre = "%s%s" % (name, " [SECONDARY: printed, never F-E1 / P3 / P4 / P7 / the reading table]" if sec else " [PRIMARY]")
        L.append("")
        L.append("=== FLAT %s at its own k = %d (T = its tree, flatLeaf; V = flat vMF, seeds 0-4; comparator V0) ===" % (pre, r["k"]))
        if r["n_train"] != r["n_train_all"]:
            L.append("  D3: M1's cell majority from %d of %d readout train texts (the card file lacks %d train-only texts)"
                     % (r["n_train"], r["n_train_all"], r["n_train_all"] - r["n_train"]))
        for pn in ["T"] + ["V%d" % s for s in SEEDS] + ["K%d" % s for s in SEEDS]:
            m = r["M"][pn]
            L.append("  %-3s M1 %.4f [%.4f, %.4f]  M2 %+.3f x1e-3%s" % (pn, m["m1"], m["m1_lo"], m["m1_hi"], 1000 * m["m2"],
                     "" if pn == "T" else "  (iters %d, converged %s)" % (m["iters"], m["converged"])))
        for metric, crit in (("m1", "C1 PURITY"), ("m2", "C2 KEY INFORMATION")):
            d, lo, hi = r["pv"][metric]
            held = r["c1"] if metric == "m1" else r["c2"]
            L.append("  %s: M(T) - M(V0) = %s, paired 95%% CI [%s, %s], spread_V %s -> %s" % (
                crit, fmt_m(metric, d), fmt_m(metric, lo), fmt_m(metric, hi), fmt_m(metric, r["spread_V"][metric]).lstrip("+"),
                "HELD" if held else "FAILED"))
        if r["l1"]:
            L.append("  L1 LOSS FLAG: FIRES on %s" % " AND ".join({"m1": "M1", "m2": "M2"}[m] for m in r["l1"]))
        else:
            L.append("  L1 LOSS FLAG: does not fire")
        bs = r["beside"]
        L.append("  BESIDE (reported only) against K0 with spread_K: C1 %s, C2 %s, L1 %s; T - K0 M1 %s, M2 %s" % (
            "HELD" if bs["c1"] else "FAILED", "HELD" if bs["c2"] else "FAILED",
            ("FIRES on " + " AND ".join(m.upper() for m in bs["l1"])) if bs["l1"] else "does not fire",
            fmt_m("m1", r["pk"]["m1"][0]), fmt_m("m2", r["pk"]["m2"][0])))
        for metric, se_r, mde_r in (("m1", SUPPORT["se_m1"], SUPPORT["mde_m1"]), ("m2", SUPPORT["se_m2"], SUPPORT["mde_m2"])):
            d, lo, hi = r["pv"][metric]
            se = (hi - lo) / 3.92
            bar = max(mde_r, r["spread_V"][metric], 2.8 * se)
            L.append("  SUPPORT %s: realised SE %s, MDE80 %s (registered SE %s, MDE80 %s); spread_V %s; bar max(registered MDE, spread_V, "
                     "realised MDE80) = %s" % (metric.upper(), fmt_m(metric, se).lstrip("+"), fmt_m(metric, 2.8 * se).lstrip("+"),
                                               fmt_m(metric, se_r).lstrip("+"), fmt_m(metric, mde_r).lstrip("+"),
                                               fmt_m(metric, r["spread_V"][metric]).lstrip("+"), fmt_m(metric, bar).lstrip("+")))
        L.append("  leaf count %d; root axis (depth-1 bipartition, held-out routed by flatLeaf): %s; cos(depth-1 vmfMu) %.4f"
                 % (r["k"], " | ".join(r["axis"]), r["axis_cos"]))
        L.append("  ARI to af_clean_s42 (DESCRIPTIVE; each tree routed in its own space): leaf cells held-out %.4f, fit %.4f; depth-1 "
                 "held-out %.4f" % (r["ari_ho"], r["ari_fit"], r["ari_d1"]))
        f = r["filing"]
        L.append("=== FILING %s: flatLeaf top-1, %s minus af_clean_s42, paired on the %d ===" % (pre, name, f["n"]))
        L.append("  top-1 %s %.4f vs af_clean_s42 %.4f; b (%s right, af wrong) = %d, c (%s wrong, af right) = %d; diff (b - c) / n = "
                 "%+.4f" % (name, float(r["M"]["T"]["per1"].mean()), float(res["af"]["per1"].mean()), name, f["b"], name, f["c"], f["diff"]))
        L.append("  paired McNemar 95%% interval [%+.4f, %+.4f] (SE %.5f) -> FILING %s" % (f["lo"], f["hi"], f["se"], f["verdict"]))
        L.append("  beside (never deciding): exact two-sided McNemar p %.4g (systematic_budget.mcnemar_edge); twin-group bootstrap "
                 "percentile [%+.4f, %+.4f]" % (f["p"], f["boot"][0], f["boot"][1]))
        bar_f = max(SUPPORT["mde_f"], 2.8 * f["se"])
        L.append("  SUPPORT (a)-(e): n %d paired; DEFF %.4f (Kish m-bar of the held-out twin groups, measured); n_eff %.1f; discordance "
                 "%.4f (registered pilot 0.15); SE %.5f (registered %.5f); MDE80 %.4f (registered %.4f)"
                 % (f["n"], res["mbar"], f["n"] / res["mbar"], f["disc"], f["se"], SUPPORT["se_f"], 2.8 * f["se"], SUPPORT["mde_f"]))
        if not sec:
            L.append("  SUPPORT TAG (tightening-only): P4 prior |-0.04| vs bar max(registered MDE80 %.4f, realised MDE80 %.4f) = %.4f -> %s"
                     % (SUPPORT["mde_f"], 2.8 * f["se"], bar_f, "SCOREABLE" if abs(P4[0]) > bar_f else "DESCRIPTIVE-ONLY (demoted)"))
    r = res["arms"]["N-raw"]
    f = r["filing"]
    L.append("")
    L.append(VERDICT_F)
    L.append("WRONG(ESTABLISHED) / TIE CONVENTIONS A, B: not applicable (D6: no judge verdicts, hits are 0 / 1; no model pairs)")
    L.append("=== E1 CRITERIA (N-raw, PRIMARY) ===")
    L.append("  FLAT C1 %s; C2 %s; L1 %s" % ("HELD" if r["c1"] else "FAILED", "HELD" if r["c2"] else "FAILED",
                                              ("FIRES on " + " AND ".join({"m1": "M1", "m2": "M2"}[m] for m in r["l1"])) if r["l1"]
                                              else "does not fire"))
    L.append("  FILING %s: %+.4f, paired McNemar 95%% interval [%+.4f, %+.4f], n = %d" % (f["verdict"], f["diff"], f["lo"], f["hi"], f["n"]))
    L.append("  " + (FE1_FIRES if res["fe1"] else FE1_NOT))
    L.append("READING TABLE (k = FLAT-GENERALITY's count, %d; N-raw's L1 %s): \"%s\"" % (
        res["k_fg"], "fires" if res["l1_raw"] else "does not fire", reading_line(res["k_fg"], res["l1_raw"])))
    L.append("=== PREDICTIONS ===")
    L.append("  P3 N-raw's L1 fires (prior %.2f): %s; Brier %.4f" % (P3_PROB, "FIRES" if res["l1_raw"] else "does not fire",
                                                                  brier(P3_PROB, res["l1_raw"])))
    inside = bool(P4[1][0] <= f["diff"] <= P4[1][1])
    L.append("  P4 filing N-raw minus af_clean_s42 = %+.2f (80%% [%+.2f, %+.2f]): observed %+.4f -> %s (D5: endpoints inclusive); "
             "HELD-WORSE (prior %.2f): %s; Brier %.4f" % (P4[0], P4[1][0], P4[1][1], f["diff"], "HELD" if inside else "FAILED", P4[2],
                                                          "occurred" if f["verdict"] == "HELD-WORSE" else "did not occur",
                                                          brier(P4[2], f["verdict"] == "HELD-WORSE")))
    L.append("  P7 F-E1 fires (prior %.2f): %s; Brier %.4f" % (P7_PROB, "FIRED" if res["fe1"] else "did not fire", brier(P7_PROB, res["fe1"])))
    L.append("  P1 / P2 / P5 / P6 are E0b's (scored there); not E1's")
    L.append("DOES NOT SHOW: an embedder contrast as a scored test (Support (g): one draw per arm); embedder invariance; another "
             "corpus; N-card's in-run JVM numbers (B-PB-1)")
    return L


def csv_rows(res):
    rows = ["arm,role,k,partition,M1,M1_lo,M1_hi,M2_x1e3,M2_n,iters,converged"]
    for name in res["order"]:
        r = res["arms"][name]
        for pn in ["T"] + ["V%d" % s for s in SEEDS] + ["K%d" % s for s in SEEDS]:
            m = r["M"][pn]
            rows.append("%s,%s,%d,%s,%.6f,%.6f,%.6f,%.6f,%d,%s,%s" % (name, r["role"], r["k"], pn, m["m1"], m["m1_lo"], m["m1_hi"],
                        1000 * m["m2"], m["n2"], m.get("iters", ""), m.get("converged", "")))
    return "\n".join(rows) + "\n"


def write_once(path, text):
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------------------------------------------ modes
def dry_run(loader, L=None):
    L = [] if L is None else L
    W = loader(L)
    for a in E1_ARMS:
        if a["name"] in W["trees"]:
            say(L, "PLAN %s: k = %d; V0-V4 (vmf_em, max_iter %d, tol %g) + K0-K4 on the %d fit texts; M1 on %d held-out with the majority "
                   "of %d train texts; M2 on %d keyed; FILING vs af_clean_s42 on %d" % (a["name"], len(W["trees"][a["name"]]["leaf_ids"]),
                                                                                   FM.V_MAX_ITER, FM.V_TOL, len(W["fit"]), len(W["heldout"]),
                                                                                   len(W["train_by"][a["name"]]), len(W["keyed"][4]),
                                                                                   len(W["heldout"])))
    say(L, "[MODE] --dry-run: pins, denominators, guards and the plan only; NO measure (M1 / M2 / filing), no fit, nothing written")
    say(L, "%s dry-run complete" % TAG)
    return 0


def run(loader, out_dir, fit_fn=default_fit, L=None):
    L = [] if L is None else L
    oc, pc = os.path.join(out_dir, OUTCOME), os.path.join(out_dir, PART_CSV)
    for p in (oc, pc):
        if os.path.exists(p):
            refuse("%s exists: the outcome of record is write-once" % p)
    t0 = time.process_time()
    W = loader(L)
    res = compute(W, fit_fn)
    body = render(res)
    for line in body:
        say(L, line)
    if W.get("pins_fn") is not None:
        after = W["pins_fn"]()
        for k, v in sorted(after.items()):
            say(L, "[PIN after ] %s %s" % (k, v))
        bad = [k for k in set(after) | set(W["pins_before"]) if after.get(k) != W["pins_before"].get(k)]
        if bad:
            refuse("a pinned input changed during the run: %s" % bad)
        say(L, "[PIN] before == after on every pinned file / row")
    say(L, "%s CPU %.1f s; zero calls" % (TAG, time.process_time() - t0))
    os.makedirs(out_dir, exist_ok=True)
    write_once(oc, "\n".join(L) + "\n")
    write_once(pc, csv_rows(res))
    say(L, "%s outcome written (write-once): %s ; %s" % (TAG, oc, pc))
    return res


# ------------------------------------------------------------------------------------------------ selftest
N_CAT = 4


def _fixture(seed=7, n_fit=240, n_extra=60, n_ho=160, n_keyed=200, n_models=6):
    """A clustered synthetic corpus: 4 categories, each a vMF-like cloud whose noise lives in 6 shared directions (E0b's recipe:
    a 256-d isotropic noise lets a component collapse, ruling B6, not a property worth testing). Keyed questions: model accuracy
    depends on the category, so a category partition carries key information (M2 > 0)."""
    rng = np.random.default_rng(seed)
    cats = ["cat%d" % i for i in range(N_CAT)]
    cent = FM.unit_rows(rng.normal(size=(N_CAT, DIM)))
    Pn = FM.unit_rows(rng.normal(size=(6, DIM)))
    def vec(c):
        return unit(cent[c] + rng.normal(0, 0.25, 6) @ Pn)
    def mk(prefix, n):
        return [("%s%05d" % (prefix, i), cats[i % N_CAT]) for i in range(n)]
    fit = mk("f", n_fit)
    extra = mk("x", n_extra)
    ho = mk("h", n_ho)
    space = {t: vec(int(c[3:])) for t, c in fit + extra + ho}
    # held-out question 0 (cat0) carries a private direction w orthogonal to every centre and noise direction: an extra
    # centre AT its vector captures it and no other text (cos(t, q0) = cos(t, cent0) / sqrt(1.64) < cos(t, cent0)); ST-G
    w = rng.normal(size=DIM)
    B = np.vstack([cent, Pn]).T
    w -= B @ np.linalg.lstsq(B, w, rcond=None)[0]
    space[ho[0][0]] = unit(cent[0] + 0.8 * w / np.linalg.norm(w))
    pool = fit + extra + ho
    models = ["m%d" % j for j in range(n_models)]
    qs = ["k%04d" % i for i in range(n_keyed)]
    textd = {q: pool[(7 * i) % len(pool)][0] for i, q in enumerate(qs)}
    catd = {q: pool[(7 * i) % len(pool)][1] for i, q in enumerate(qs)}
    G = {m: {q: int(rng.random() < (0.9 if (int(catd[q][3:]) + j) % 2 == 0 else 0.1)) for q in qs} for j, m in enumerate(models)}
    return dict(fit=sorted(fit), train=sorted(fit + extra), heldout=ho, keyed=(models, G, catd, textd, qs), cent=cent, space=space, rng=rng)


def _tree(mu, d1_split=2):
    mu = FM.unit_rows(np.asarray(mu, dtype=np.float64))
    k = mu.shape[0]
    ids = ["L%02d" % i for i in range(k)]
    d1 = ["D0" if i < d1_split else "D1" for i in range(k)]
    d1_mu = FM.unit_rows(np.stack([mu[:d1_split].sum(0), mu[d1_split:].sum(0)]))
    return dict(leaf_ids=ids, leaf_mu=mu, leaf_d1=d1, d1_ids=["D0", "D1"], d1_mu=d1_mu, leaves=ids, dim=DIM)


def _world(fx, raw_mu, card_mu, af_mu, k_fg=2, card_train_drop=0):
    """af_clean_s42's space is a random ROTATION of the fixture space (its tree rotated with it): its hits are unchanged, but
    reading af in N-raw's space (or N-raw in af's) files garbage, so a wrong-space read is visible."""
    good = fx["cent"]
    R = np.linalg.qr(np.random.default_rng(11).normal(size=(DIM, DIM)))[0]
    af_space = {t: R @ v for t, v in fx["space"].items()}
    trees = {"N-raw": _tree(raw_mu), "N-card": _tree(card_mu), "af_clean_s42": _tree(np.asarray(af_mu) @ R.T)}
    tr_card = fx["train"][card_train_drop:]
    return dict(fit=fx["fit"], train=fx["train"], heldout=fx["heldout"], keyed=fx["keyed"], k_fg=k_fg, identity=None, trees=trees,
                spaces={"N-raw": fx["space"], "N-card": fx["space"], "af_clean_s42": af_space},
                train_by={"N-raw": fx["train"], "N-card": tr_card, "af_clean_s42": fx["train"]}, real=False, _good=good)


def _loader(W):
    def ld(L):
        say(L, "pool FIXTURE (selftest; no DB read)")
        counts(W, L, None)
        hygiene(W, L)
        return W
    return ld


def _bad(fx):
    """A useless tree: every leaf mean is cat0's centre (identical rows), so argmax files every question in leaf 0: one cell,
    whose majority is one category of four (M1 = 0.25 on the balanced fixture)."""
    return fx["cent"][[0, 0, 0, 0]].copy()


def _merged(fx):
    """cat3 mapped onto cat2's centre: one category of four is always wrong (M1 ~ 0.75)."""
    return fx["cent"][[0, 1, 2, 2]] + np.random.default_rng(5).normal(0, 1e-3, (N_CAT, DIM))


def _inj_fit(fx, v_mus, k_mus=None):
    """An injected fitter: V0-V4 / K0-K4 as nearest-centre partitions on given centres (the spread is then known)."""
    def fit(X, k):
        out = {}
        for s in SEEDS:
            out["V%d" % s] = dict(rule="nearest", centers=np.asarray(v_mus[s]), iters=1, converged=True)
            out["K%d" % s] = dict(rule="nearest", centers=np.asarray((k_mus or v_mus)[s]), iters=1, converged=True)
        return out
    return fit


def _indep_hits(mu, space, train, heldout):
    """Independent recomputation of flatLeaf top-1 (no m1_block / score_cells): argmax cosine, majority of the TRAIN texts."""
    mu = FM.unit_rows(np.asarray(mu, dtype=np.float64))
    lt = [int(np.argmax(mu @ space[t])) for t, _ in train]
    maj = {}
    for k in set(lt):
        cnt = Counter(c for kk, (_, c) in zip(lt, train) if kk == k)
        maj[k] = sorted(cnt.items(), key=lambda kv: (-kv[1], list(cnt).index(kv[0])))[0][0]
    return np.array([1 if maj.get(int(np.argmax(mu @ space[t]))) == c else 0 for t, c in heldout])


def _run_fixture(W, fit_fn=default_fit):
    td = tempfile.mkdtemp(prefix="e1ro_")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = run(_loader(W), td, fit_fn=fit_fn)
    text = open(os.path.join(td, OUTCOME), encoding="utf-8").read()
    shutil.rmtree(td, ignore_errors=True)
    return res, text


def _line(text, needle):
    got = [l for l in text.splitlines() if needle in l]
    return got[0] if got else ""


def _refused(fn, needle):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn()
    except SystemExit as e:
        return needle in str(e)
    return False


def selftest(quiet=False):
    """Every deciding path EXECUTED through run() (or dry_run()) on fixtures whose answers are known, with VALUE assertions:
    ST-A real vmf_em: N-raw tree useless, af tree = the true centres, N-card good: L1 FIRES on M1 (value of T - V0 asserted
       against an independent recomputation), C1 FAILED; FILING HELD-WORSE with b / c / diff equal to the independent hits
       (denominator n = held-out, not b + c), F-E1 FIRES (from N-raw, not N-card: N-card's filing reads UNDETERMINED here);
       P3 / P4 / P7 Brier values; reading table k = 2 + L1 fires sentence.
    ST-B N-raw = true centres, af useless: FILING HELD-BETTER, F-E1 did not fire (P7 Brier 0.36); T = V0 (both true
       centres), so L1 does not fire; reading "not" sentence (k 2).
    ST-D2 a straddling interval (b = c = n / 4): UNDETERMINED; L1 FIRES there while F-E1 does not (P7 scored on F-E1).
    ST-G the C1 interval leg and the train side of M1: T - V0 = +1 / n > spread 0 with the CI reaching 0 -> C1 FAILED.
    ST-C injected: T merged, V0-V4 good (spread 0): L1 FIRES; the same T with V4 merged (spread ~ 0.25): L1 does not fire
       (kills spread -> 0 and the comparator swap); k = 1 -> the "UNDETERMINED" reading sentence.
    ST-D boundary: N-raw tree == af tree in the same space: b = c = 0, interval [0, 0] -> UNDETERMINED (kills <= / >= edges).
    ST-E C1 / C2 HELD: T good, V0-V4 merged (spread 0): C1 HELD and C2 HELD with values.
    ST-F refusals: write-once (outcome exists), the identity mismatch, a fixture missing a held-out vector (D3 allowance),
       the FG outcome sha / line, --eval-db-copy with --run, the guard on a text-joined view (ADMIT on the right space; REFUSE
       when only the SECOND site's members come from another space: all sites, not the first), the dry-run prints the
       denominators and writes nothing, D3's disclosure line carries the count, B-PB-1 is printed and no validation/ path
       is opened by this script."""
    n = [0]

    def ok(cond, what):
        n[0] += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    Z_REG = 1.959963984540054          # the registered 95% (two-sided normal quantile), independent of the module's Z95
    fx = _fixture()
    good, bad, merged = fx["cent"], _bad(fx), _merged(fx)
    sp, tr, ho = fx["space"], fx["train"], fx["heldout"]
    h_good, h_bad, h_mer = (_indep_hits(m, sp, tr, ho) for m in (good, bad, merged))
    ok(h_good.mean() == 1.0 and h_bad.mean() == 0.25 and abs(h_mer.mean() - 0.75) < 1e-9,
       "fixture: true centres 1.0, useless tree 0.25, merged 0.75 (independent hits)")

    # ST-A (real vmf_em)
    res, text = _run_fixture(_world(fx, bad, good, good))
    r = res["arms"]["N-raw"]
    d_exp = float((h_bad - h_good).mean())
    b_exp, c_exp = int(((h_bad == 1) & (h_good == 0)).sum()), int(((h_bad == 0) & (h_good == 1)).sum())
    ok(r["filing"]["b"] == b_exp and r["filing"]["c"] == c_exp and abs(r["filing"]["diff"] - d_exp) < 1e-12 and r["filing"]["n"] == len(ho),
       "ST-A filing b %d c %d diff %+.4f n %d == independent" % (b_exp, c_exp, d_exp, len(ho)))
    se_exp = math.sqrt(b_exp + c_exp - (b_exp - c_exp) ** 2 / len(ho)) / len(ho)
    ok(abs(r["filing"]["hi"] - (d_exp + Z_REG * se_exp)) < 1e-12, "ST-A McNemar interval upper end = d + 1.96 SE (%.5f)" % se_exp)
    ok("paired McNemar 95%% interval [%+.4f, %+.4f] (SE %.5f) -> FILING HELD-WORSE" % (d_exp - Z_REG * se_exp, d_exp + Z_REG * se_exp, se_exp)
       in text, "ST-A printed FILING HELD-WORSE with its interval")
    ok(FE1_FIRES in text and FE1_NOT not in text, "ST-A F-E1 FIRES (printed)")
    ok(res["arms"]["N-card"]["filing"]["verdict"] == "UNDETERMINED" and "FILING N-card [SECONDARY" in text,
       "ST-A N-card filing UNDETERMINED (F-E1 is N-raw's, not N-card's)")
    v0 = res["arms"]["N-raw"]["M"]["V0"]["per1"]
    ok(v0.mean() == 1.0, "ST-A real vmf_em V0 recovers the categories (M1 1.0)")
    ok(abs(r["pv"]["m1"][0] - float((h_bad - v0).mean())) < 1e-12 and r["l1"][:1] == ["m1"] and not r["c1"],
       "ST-A L1 FIRES on M1 at T - V0 = %+.4f; C1 FAILED" % r["pv"]["m1"][0])
    ok("  FLAT C1 FAILED; C2 FAILED; L1 FIRES on M1" in text, "ST-A criteria line printed (C1 FAILED, C2 FAILED, L1 FIRES on M1)")
    ok(("\"%s\"" % (READING["fires"] % 2)) in text, "ST-A reading table: k 2, L1 fires sentence")
    ok("P3 N-raw's L1 fires (prior 0.55): FIRES; Brier %.4f" % ((0.55 - 1) ** 2) in text, "ST-A P3 Brier 0.2025")
    ok(("observed %+.4f -> FAILED" % d_exp) in text and "HELD-WORSE (prior 0.60): occurred; Brier 0.1600" in text,
       "ST-A P4 FAILED (diff %+.4f outside [-0.08, 0.00]); HELD-WORSE occurred, Brier 0.16" % d_exp)
    ok("P7 F-E1 fires (prior 0.60): FIRED; Brier 0.1600" in text, "ST-A P7 FIRED, Brier 0.16")
    ok(BPB1 in text and "62.91" not in text and "NoMatchRate" not in text, "ST-A B-PB-1 printed; no in-run JVM number")
    ok("SUPPORT TAG (tightening-only)" in text and "DEFF 1.0000" in text and "n_eff %.1f" % len(ho) in text,
       "ST-A support readout: DEFF 1.0000 (singleton twin groups), n_eff = n")

    # ST-B (N-raw good, af useless)
    res, text = _run_fixture(_world(fx, good, good, bad), fit_fn=_inj_fit(fx, [good, good, good, good, merged]))
    r = res["arms"]["N-raw"]
    ok(r["filing"]["verdict"] == "HELD-BETTER" and abs(r["filing"]["diff"] - float((h_good - h_bad).mean())) < 1e-12,
       "ST-B FILING HELD-BETTER at %+.4f" % r["filing"]["diff"])
    ok(FE1_NOT in text and FE1_FIRES not in text and "P7 F-E1 fires (prior 0.60): did not fire; Brier 0.3600" in text,
       "ST-B F-E1 did not fire; P7 Brier 0.36")
    ok(not r["l1"] and ("\"%s\"" % (READING["not"] % 2)) in text, "ST-B L1 does not fire; reading 'not' sentence (k 2)")

    # ST-C (spread decides L1)
    res0, t0 = _run_fixture(_world(fx, merged, good, good), fit_fn=_inj_fit(fx, [good] * 5))
    res1, t1 = _run_fixture(dict(_world(fx, merged, good, good), k_fg=1), fit_fn=_inj_fit(fx, [good, good, good, good, merged]))
    a0, a1 = res0["arms"]["N-raw"], res1["arms"]["N-raw"]
    ok(a0["spread_V"]["m1"] == 0.0 and a0["l1"][:1] == ["m1"] and abs(a0["pv"]["m1"][0] - float((h_mer - h_good).mean())) < 1e-12,
       "ST-C spread 0: L1 FIRES on M1 at %+.4f" % a0["pv"]["m1"][0])
    ok(abs(a1["spread_V"]["m1"] - 0.25) < 1e-9 and "m1" not in a1["l1"] and abs(a1["pv"]["m1"][0] - a0["pv"]["m1"][0]) < 1e-12,
       "ST-C spread 0.25 (max - min over V0-V4): the same T - V0 does not fire on M1")
    ok(("\"%s\"" % (READING["low"] % 1)) in t1, "ST-C reading table k 1: UNDETERMINED sentence")

    # ST-D (boundary)
    res, text = _run_fixture(_world(fx, good, good, good), fit_fn=_inj_fit(fx, [good] * 5))
    f = res["arms"]["N-raw"]["filing"]
    ok(f["b"] == 0 and f["c"] == 0 and f["lo"] == 0.0 and f["hi"] == 0.0 and f["verdict"] == "UNDETERMINED" and FE1_NOT in text,
       "ST-D b = c = 0: interval [0, 0] -> UNDETERMINED; F-E1 did not fire")
    ok("observed +0.0000 -> HELD" in text, "ST-D P4 HELD at the inclusive endpoint 0.00 (D5)")
    # ST-D2: a straddling interval with discordance (N-raw wrong on cat3, af wrong on cat0): b = c = n / 4, diff 0, SE > 0
    af_mer = fx["cent"][[1, 1, 2, 3]] + np.random.default_rng(6).normal(0, 1e-3, (N_CAT, DIM))
    h_afm = _indep_hits(af_mer, sp, tr, ho)
    res, text = _run_fixture(_world(fx, merged, good, af_mer), fit_fn=_inj_fit(fx, [good] * 5))
    f = res["arms"]["N-raw"]["filing"]
    bq, cq = int(((h_mer == 1) & (h_afm == 0)).sum()), int(((h_mer == 0) & (h_afm == 1)).sum())
    ok(f["b"] == bq == len(ho) // 4 and f["c"] == cq == len(ho) // 4 and f["lo"] < 0 < f["hi"] and f["verdict"] == "UNDETERMINED"
       and "-> FILING UNDETERMINED" in _line(text, "paired McNemar 95% interval"),
       "ST-D2 b = c = %d: interval [%+.4f, %+.4f] straddles 0 -> UNDETERMINED (kills lo < 0 / hi > 0 edges)" % (bq, f["lo"], f["hi"]))
    ok(res["arms"]["N-raw"]["l1"][:1] == ["m1"] and "P7 F-E1 fires (prior 0.60): did not fire; Brier 0.3600" in text
       and "P3 N-raw's L1 fires (prior 0.55): FIRES; Brier 0.2025" in text, "ST-D2 L1 FIRES but F-E1 does not: P7 scored on F-E1 (0.36)")

    # ST-G: the CI leg of C1 and the train side of M1. V0-V4 = the true centres plus one EXTRA centre at held-out question 0's
    # own vector: that cell holds no TRAIN text (checked), so question 0 has no majority and is a miss under V; T = the true
    # centres. M1(T) - M1(V0) = 1 / n > spread_V = 0, but the bootstrap CI reaches 0: C1 FAILED by the interval leg.
    q0 = sp[ho[0][0]]
    vx = np.vstack([good, q0[None, :]])
    lt = [int(np.argmax(FM.unit_rows(vx) @ sp[t])) for t, _ in tr]
    h_vx = _indep_hits(vx, sp, tr, ho)
    res, text = _run_fixture(_world(fx, good, good, good), fit_fn=_inj_fit(fx, [vx] * 5))
    r = res["arms"]["N-raw"]
    ok(lt.count(N_CAT) == 0 and int((h_good - h_vx).sum()) == 1 and abs(r["pv"]["m1"][0] - 1.0 / len(ho)) < 1e-12
       and r["spread_V"]["m1"] == 0.0 and r["pv"]["m1"][1] <= 0.0 and not r["c1"] and "C1 PURITY: M(T) - M(V0) = %+.4f" % (1.0 / len(ho)) in text,
       "ST-G T - V0 = +1/n > spread 0 but the CI reaches 0 (lo %+.4f): C1 FAILED by the interval leg; the extra cell has 0 train texts"
       % r["pv"]["m1"][1])

    # ST-E (C1 / C2 HELD)
    res, text = _run_fixture(_world(fx, good, good, good), fit_fn=_inj_fit(fx, [merged] * 5))
    r = res["arms"]["N-raw"]
    ok(r["c1"] and r["c2"] and abs(r["pv"]["m1"][0] - 0.25) < 1e-9 and "  FLAT C1 HELD; C2 HELD; L1 does not fire" in text,
       "ST-E C1 HELD (T - V0 +0.2500, spread 0) and C2 HELD (M2 %+.3f x1e-3)" % (1000 * r["pv"]["m2"][0]))
    ok(r["pv"]["m2"][0] > 0 and r["pv"]["m2"][1] > 0, "ST-E C2's CI lower end > 0")

    # ST-F refusals and the dry-run
    W = _world(fx, good, good, good)
    td = tempfile.mkdtemp(prefix="e1ro_")
    open(os.path.join(td, OUTCOME), "x").close()
    ok(_refused(lambda: run(_loader(W), td, fit_fn=_inj_fit(fx, [good] * 5)), "write-once"), "ST-F an existing outcome REFUSES --run")
    try:
        write_once(os.path.join(td, OUTCOME), "overwrite")
        wo = False
    except FileExistsError:
        wo = True
    ok(wo and open(os.path.join(td, OUTCOME), encoding="utf-8").read() == "", "ST-F write_once never overwrites (mode x)")
    shutil.rmtree(td, ignore_errors=True)
    Wi = dict(_world(fx, good, good, good), identity=dict(m1="0.000 [0.000, 0.000]", m2="+0.000"))
    ok(_refused(lambda: compute(Wi, _inj_fit(fx, [good] * 5)), "the record's identity"), "ST-F identity mismatch REFUSES")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        dry_run(_loader(dict(_world(fx, good, good, good), card_train_drop=0)))
    out = buf.getvalue()
    ok(("DENOMINATORS: fit %d (registered 8,125), held-out %d" % (len(fx["fit"]), len(ho))) in out and "NO measure" in out
       and "FILING n = held-out %d paired" % len(ho) in out and "FILING HELD" not in out, "ST-F dry-run prints the denominators, no measure")
    res, text = _run_fixture(_world(fx, good, good, good, card_train_drop=7), fit_fn=_inj_fit(fx, [good] * 5))
    ok(("D3: M1's cell majority from %d of %d readout train texts (the card file lacks 7" % (len(tr) - 7, len(tr))) in text,
       "ST-F D3 disclosure line carries the count (7)")
    # FG outcome
    td = tempfile.mkdtemp(prefix="e1ro_")
    p = os.path.join(td, "fg.txt")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("x\nD2: the loss appears in 1 of 3 qwen3 re-draws (L1_r fired: af_s137)\n")
    ok(read_fg_k(p, sha256_file(p))[0] == 1, "ST-F FG k parsed (1)")
    with open(p, "wb") as fh:
        fh.write(b"x\r\nD2: the loss appears in 3 of 3 qwen3 re-draws (CRLF rendering)\r\n")
    lf = hashlib.sha256(b"x\nD2: the loss appears in 3 of 3 qwen3 re-draws (CRLF rendering)\n").hexdigest()
    ok(read_fg_k(p, lf)[0] == 3, "ST-F FG pinned by its LF sha256 (a CRLF working copy admitted, k 3)")
    ok(_refused(lambda: read_fg_k(p, "0" * 64), "sha256"), "ST-F FG sha mismatch REFUSES")
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("no line\n")
    ok(_refused(lambda: read_fg_k(p, sha256_file(p)), "carries no"), "ST-F FG without the D2 line REFUSES")
    ok(_refused(lambda: load_real([], eval_copy_dir=td, run_mode=True), "--dry-run only"), "ST-F --eval-db-copy with --run REFUSES")
    shutil.rmtree(td, ignore_errors=True)
    # the text-joined guard: two sites, member vectors from the right space vs the second site from another space
    rng = np.random.default_rng(3)
    ids = ["q%03d" % i for i in range(40)]
    id2t = {q: "t" + q for q in ids}
    c0, c1 = FM.unit_rows(rng.normal(size=(2, 768)))
    V = {id2t[q]: c0 + rng.normal(0, 0.05, 768) if i < 20 else c1 + rng.normal(0, 0.05, 768) for i, q in enumerate(ids)}
    def blob(v):
        return struct.pack(">%df" % len(v), *v)
    def mu(qs, vv):
        return list(unit(np.sum([unit(vv[id2t[q]]) for q in qs], 0)))
    byid = {"R": dict(id="R", childIds=["A", "B"], dasguptaDeltaNorm=1.0, queryIds=[], vmfMu=mu(ids, V)),
            "A": dict(id="A", childIds=["A1", "A2"], dasguptaDeltaNorm=1.0, queryIds=[], vmfMu=mu(ids[:20], V)),
            "A1": dict(id="A1", childIds=[], queryIds=ids[:10]), "A2": dict(id="A2", childIds=[], queryIds=ids[10:20]),
            "B": dict(id="B", childIds=[], queryIds=ids[20:])}
    reg = lambda s: FM.region_query_ids(s["id"], byid)
    good_b = {t: blob(v) for t, v in V.items()}
    rr, err, _o = guard_quiet(lambda: text_join_guard(byid, reg, id2t, good_b, NOMIC, "fixture"))
    ok(err is None and rr["min_cos"] > 0.99 and len(rr["rows"]) == 2, "ST-F text-joined guard ADMITs on the right space (2 sites)")
    other = dict(good_b)
    for q in ids[20:]:
        other[id2t[q]] = blob(rng.normal(size=768))       # B's members: only site R (the SECOND split site in id order, A < R) moves
    rr, err, _o = guard_quiet(lambda: text_join_guard(byid, reg, id2t, other, NOMIC, "fixture"))
    ok(err is not None and "min cosine" in err and [r_["id"] for r_ in EG.split_sites(byid)] == ["A", "R"],
       "ST-F text-joined guard REFUSEs when only the second split site (R; A first in id order) is wrong")
    missing = {t: b for t, b in good_b.items() if t != id2t[ids[0]]}
    rr, err, _o = guard_quiet(lambda: text_join_guard(byid, reg, id2t, missing, NOMIC, "fixture"))
    ok(err is None and [x["found"] for x in rr["rows"]] == [19, 39], "ST-F the guard reads members by TEXT (A 19 of 20, R 39 of 40 when one text lacks a vector)")
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    word = "valid" + "ation"                              # built here so the needle is not itself a literal of this file
    ok(all((q + word + e) not in src for q in ("\"", "'", "/", "\\") for e in ("\"", "'", "/", "\\")),
       "ST-F no validation/ path is built in this script (B-PB-1)")
    print("%s SELFTEST PASSED (%d checks)" % (TAG, n[0]))
    return 0


# ------------------------------------------------------------------------------------------------ mutants
MUTANTS = (
    ("M01 filing sign reversed", "mc = mcnemar(M[\"T\"][\"per1\"], af[\"per1\"])", "mc = mcnemar(af[\"per1\"], M[\"T\"][\"per1\"])"),
    ("M02 HELD-WORSE on lo < 0", "    if hi < 0:\n        return \"HELD-WORSE\"", "    if lo < 0:\n        return \"HELD-WORSE\""),
    ("M03 HELD-WORSE on hi <= 0 (boundary)", "    if hi < 0:\n        return \"HELD-WORSE\"", "    if hi <= 0:\n        return \"HELD-WORSE\""),
    ("M04 F-E1 from N-card", "r = res[\"arms\"][\"N-raw\"]\n    res[\"fe1\"]", "r = res[\"arms\"][\"N-card\"]\n    res[\"fe1\"]"),
    ("M05 McNemar denominator b + c", "    d = (b - c) / n\n", "    d = (b - c) / max(1, b + c)\n"),
    ("M06 spread_V -> 0", "spread_V = {m: FM.spread([M[\"V%d\" % s][m] for s in SEEDS]) for m in (\"m1\", \"m2\")}",
     "spread_V = {m: 0.0 for m in (\"m1\", \"m2\")}"),
    ("M07 spread over V0 only (first seed only)", "spread_V = {m: FM.spread([M[\"V%d\" % s][m] for s in SEEDS])",
     "spread_V = {m: FM.spread([M[\"V%d\" % s][m] for s in SEEDS[:1]])"),
    ("M08 comparator V4 instead of V0", "pv, pk = paired(M[\"T\"], M[\"V0\"], groups)", "pv, pk = paired(M[\"T\"], M[\"V4\"], groups)"),
    ("M09 M1 majority from the held-out (wrong side)", "sc, hits, kh = FM.m1_block(fn, Qt, Qh, train, heldout)",
     "sc, hits, kh = FM.m1_block(fn, Qh, Qh, heldout, heldout)"),
    ("M10 L1 only on M2", "l1m = [m for m in (\"m1\", \"m2\") if FM.loss(", "l1m = [m for m in (\"m2\",) if FM.loss("),
    ("M11 reading table k >= 1", "    if k >= 2:\n        return READING", "    if k >= 1:\n        return READING"),
    ("M12 F-E1 line omitted when not firing", "    L.append(\"  \" + (FE1_FIRES if res[\"fe1\"] else FE1_NOT))",
     "    L.append(\"  \" + (FE1_FIRES if res[\"fe1\"] else \"\"))"),
    ("M13 P4 interval exclusive", "inside = bool(P4[1][0] <= f[\"diff\"] <= P4[1][1])", "inside = bool(P4[1][0] < f[\"diff\"] < P4[1][1])"),
    ("M14 identity check skipped", "    if W.get(\"identity\") is not None and ident != W[\"identity\"]:",
     "    if False and ident != W[\"identity\"]:"),
    ("M15 write-once off", "    with open(path, \"x\", encoding=\"utf-8\", newline=\"\\n\") as f:",
     "    with open(path, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:"),
    ("M16 guard on the first split site only", "return EG.guard(con, label, EG.split_sites(byid), region_ids",
     "return EG.guard(con, label, EG.split_sites(byid)[:1], region_ids"),
    ("M17 C1 decided by the point only", "c1 = FM.criterion(pv[\"m1\"][0], spread_V[\"m1\"], pv[\"m1\"][1], pv[\"m1\"][2])",
     "c1 = bool(pv[\"m1\"][0] > spread_V[\"m1\"])"),
    ("M18 D3 disclosure line dropped", "        if r[\"n_train\"] != r[\"n_train_all\"]:\n            L.append(\"  D3:",
     "        if False:\n            L.append(\"  D3:"),
    ("M19 SE without the (b - c)^2 / n term", "se = math.sqrt(max(0.0, (b + c) - (b - c) ** 2 / n)) / n", "se = math.sqrt(b + c) / n"),
    ("M20 P7 scored on L1 instead of F-E1", "brier(P7_PROB, res[\"fe1\"])", "brier(P7_PROB, res[\"l1_raw\"])"),
    ("M21 spread min - max (sign)", "spread_V = {m: FM.spread([M[\"V%d\" % s][m] for s in SEEDS]) for m",
     "spread_V = {m: -FM.spread([M[\"V%d\" % s][m] for s in SEEDS]) for m"),
    ("M22 af_clean_s42 read in N-raw's space", "af = measure(tree_fn(W[\"trees\"][\"af_clean_s42\"]), W[\"spaces\"][\"af_clean_s42\"]",
     "af = measure(tree_fn(W[\"trees\"][\"af_clean_s42\"]), W[\"spaces\"][\"N-raw\"]"),
    ("M23 N-raw read in af_clean_s42's space", "tree, vec, train = W[\"trees\"][name], W[\"spaces\"][name], W[\"train_by\"][name]",
     "tree, vec, train = W[\"trees\"][name], W[\"spaces\"][\"af_clean_s42\"], W[\"train_by\"][name]"),
    ("M24 N-card's train restriction ignored", "tree, vec, train = W[\"trees\"][name], W[\"spaces\"][name], W[\"train_by\"][name]",
     "tree, vec, train = W[\"trees\"][name], W[\"spaces\"][name], W[\"train\"]"),
    ("M25 Z 1.645 instead of 1.96", "Z95 = 1.959963984540054", "Z95 = 1.6448536269514722"),
)


def run_mutants():
    """Each mutant: the source with one edit, its selftest run in a subprocess; KILLED iff the selftest fails."""
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    head, sep, tail = src.partition("\nMUTANTS = (")            # anchors are matched and edited ABOVE the table only
    killed = 0
    for name, a, b in MUTANTS:
        if head.count(a) != 1:
            print("%s MUTANT %s: anchor found %d times (must be 1)" % (TAG, name, head.count(a)))
            return 2
        td = tempfile.mkdtemp(prefix="e1mut_")
        p = os.path.join(td, "e1_readout_mut.py")
        mut = head.replace(a, b) + sep + tail
        # the mutant keeps the original's import pins and its own path checks; it runs from tools/analysis's sys.path
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(mut.replace("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = %r" % HERE, 1))
        r = subprocess.run([sys.executable, p, "--selftest", "--quiet"], capture_output=True, text=True, env=dict(os.environ))
        dead = r.returncode != 0
        killed += dead
        why = (r.stderr.strip().splitlines() or ["?"])[-1][:150] if dead else "SURVIVED"
        print("%s MUTANT %-48s %s  (%s)" % (TAG, name, "KILLED" if dead else "SURVIVED", why))
        shutil.rmtree(td, ignore_errors=True)
    print("%s MUTANTS %d of %d KILLED" % (TAG, killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--eval-db-copy", default=None, help="--dry-run only: a scratch dir for a checkpointed copy of the corpus DB")
    a = ap.parse_args(argv)
    if a.eval_db_copy is not None and not a.dry_run:
        refuse("--eval-db-copy is admitted with --dry-run only (the run of record reads the DB of record after C-PB-1)")
    if a.selftest:
        return selftest(quiet=a.quiet)
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(lambda L: load_real(L, eval_copy_dir=a.eval_db_copy))
    out = data_path(OUT_DIR)
    run(lambda L: load_real(L, run_mode=True), out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
