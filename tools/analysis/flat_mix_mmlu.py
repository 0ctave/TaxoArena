"""FLAT-MIX-MMLU (docs/judge_v2_program.md L20672-L20735, "## Registered 2026-09-26 (before any code or call) - FLAT-MIX-MMLU",
registered at 31d092e before any code). ZERO calls: no judge, no LLM, no embedding call, no cap, no temperature, no call cache.

Question (verbatim in the programme): on MMLU-Pro, is the content-closed anchor-free tree af_clean_s42 (82 leaves) a better
PARTITION of the corpus of record than a flat vMF mixture and spherical k-means at the same k = 82 (seeds 0-4), on held-out purity,
F6 key-only LOO Brier, split-half R and held-out log-likelihood, all through ONE instrument?

Launch sequence (the run-operator; zero calls; ONE python process at a time; outside any construction or W-window; after
MIX-LRT-SITE, never concurrently):
  python tools/analysis/flat_mix_mmlu.py --selftest        # synthetic only; green before the READY
  python tools/analysis/flat_mix_mmlu.py --mutants         # every check removed in turn; every mutant must be KILLED
  python tools/analysis/flat_mix_mmlu.py --dry-run         # pool line first; inputs, counts, pins, cost; NO statistic
  python tools/analysis/flat_mix_mmlu.py --identity-check  # THE READY's identity check (real data; prints T's M1 / M2 through
                                                           # the flat wrapper against the recorded 0.727 [0.712, 0.741] / +12.785)
  python tools/analysis/flat_mix_mmlu.py --run             # fits the partitions, one arm-seed per chunk (<= 4 wall-min each),
                                                           # write-once state under experiment_results/flat_mix_mmlu/state/
  python tools/analysis/flat_mix_mmlu.py --analyze         # REFUSES unless all 12 partitions (T, V0-V4, K0-K4, O) are present;
                                                           # writes the outcome of record WRITE-ONCE (open mode 'x')
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree (the DBs and the run dirs are not in a worktree).

Inputs and rules (the registration's words in brackets):
  POOL       pool_guard.assert_pool_of_record("p2dca21ab5f4ef3ae") is the first printed line; held-out = its 3,445 judgeable
             questions (anchor_free_readout.corpus); train (the readout's label set) = the other 8,324 distinct mmlu_pro texts.
  FIT SET    the 8,125 texts placed at the root of af_clean_s42 (snapshot 20260917_201353_Headless_Run_Auto_ge, snapshots.db,
             read-only): regionQueryIds(rootId) of the snapshot graph, id -> embeddings_cache.db queries.distilled_text; the
             script ASSERTS 8,125 and REFUSES otherwise; 256-slice, unit-normalised, via anchor_free_readout.full_vectors / sliced;
             rows sorted by text. No held-out question enters any fit; labels and keys enter no fit.
  ARMS       T  af_clean_s42 as built (anchor_free_readout.load_tree on its run dir; 82 leaves asserted), flatLeaf rule.
             V  flat vMF mixture, k = 82, seeds 0-4: soft EM, per-component kappa (Banerjee), mixing weights, max_iter 200,
                tol 1e-6 on the mean log-likelihood; INITIALISED by spherical k-means++ SEEDING with the seed (D^2 sampling,
                D^2 = 2 - 2 cos) followed by one hard M-step on the nearest-seed assignment (ruling B1; no full k-means run
                precedes EM); assignment = MAP; the nearest-mean assignment printed beside.
             K  spherical k-means, k = 82, k-means++ seeding with the seed, max_iter 300 (stops when no assignment changes; an
                emptied cluster keeps its previous centroid), assignment = nearest centroid by cosine.
             O  o0_clean_s42 (its run dir), flatLeaf; REPORTED ONLY.     Comparator of record: V0.
  MEASURES   IMPORTED, never re-implemented (both files pin-verified on import, REFUSE on mismatch):
             M1 anchor_free_readout.score_cells on the arm's cells of the readout's train and held-out sets (+ Wilson);
             M2 free_tests_f4_f7.loo_imp by the path of anchor_free_readout.f6_block (keyed_questions, embed_matrix, 256 slice);
             M3 anchor_free_readout.key_reliability on the arm's held-out cells (leaf level);
             M4 held-out mean log-likelihood (nats) of each arm read as a flat vMF mixture in 256 d; for T, K and O the cells are
                refitted on the FIT SET the arm assigns to them (mu = normalised mean, kappa Banerjee, pi = share; ruling B2: the
                8,125 fit texts, O refitted on the same set); log C_d through scipy.special.ive. DEGENERATE FITS: in a V seed (a
                component that loses all responsibility, a k-means++ seed owning no point, a one-member cell, an underflowing
                ive) ruling B6 applies: the seed is VOID and the analysis REFUSES (a failed precondition); in the DESCRIPTIVE M4
                refit of T, K or O a degenerate cell VOIDs M4 for that arm ONLY and never blocks C1 or C2 (the orchestrator's
                ruling on the registrar's note O2).
             A flat arm is passed to the readout functions as a one-level partition (its cell id per question).
  PAIRED     arm minus V0 per question; M1 and M4: 1,000 bootstrap resamples of held-out stem_key twin groups (split_side.stem_key),
             groups resampled WHOLE, fixed seed 20260926 (ruling B3); M2: F6's own
             free_tests_f4_f7.boot_mean_ci over keyed questions; spread_V(M) = max - min over V0-V4 (spread_K likewise).
  CRITERIA   C1, C2, L1, readings T-1..T-5, predictions P1-P8, falsifier F1, as registered; every print branch is executed by
             --selftest on synthetic numbers. Ruling B5 (the registrar's, derived from (T-5)'s own example): C1 HELD with L1
             FIRED (on M2) is recorded JOINED as "C1 HELD / L1 FIRED on M2", reading (T-5), no sentence; F1 fires, P7 FAILED.
  PINS       per-table sha256 (repr(row) + LF, primary-key order) of embeddings_cache.db (embeddings, queries) and of the
             mmlu_pro_dataset_cache_v2.db tables read (mmlu_pro, eval_question_link, eval_results, reserved_pool); sha256 of the
             snapshot row and of both run dirs' dag_snapshots.jsonl; BEFORE and AFTER --run / --analyze; any change REFUSES.
             A process-wide connect guard admits only file: URIs with mode=ro on the four DBs read, checks that no non-empty
             -wal / -journal sits beside them (pool_guard.open_ro's rule) and adds immutable=1 where an imported readout
             function opened mode=ro alone (the open flags only; the measure code is untouched).
Outputs: experiment_results/flat_mix_mmlu/state/*.json (write-once); experiment_results/flat_mix_mmlu/flat_mix_mmlu_outcome.txt
         and flat_mix_mmlu_arms.csv (--analyze only, write-once) (ruling B4).

[2026-09-27, the engine-coder, EMBEDDER-PLUMBING (RP08; programme L21754-L21772, registered at a357ef0); zero calls; insertion
only, nothing above is rewritten] (1) the embedding DB is a PARAMETER (registration item (e)): configure_embedding(cache_file,
model), reachable as --embedding-cache-file / --embedding-model with --dry-run and --identity-check only (--run and --analyze
REFUSE them: FLAT-MIX-MMLU's state and outcome of record are on the DB of record); an explicit file is validated fail-closed
(exists, SQLite header, embeddings and queries tables; a relative path is DATA_ROOT-relative), is admitted by the connect guard,
and replaces embeddings_cache.db in the fit set, AF.EMB_DB, F.EMB_DB and the table pins. (2) header() ends with
embedding_guard_flat(): BEFORE any partition fit, the model is named by the tree's run manifest embedding_model or
--embedding-model (item (d); a manifest without it, or a missing manifest, and no explicit name REFUSES), and
embedder_guard.guard_file checks cos(normalised mean of each accepted split site's member vectors read from the OPENED cache,
the snapshot's vmfMu) >= 0.99 over ALL split sites and the raw vector dimension against the model's native one (item (c)); it
prints the minimum and the budget on every run and REFUSES on any finding. The model named is the TREE's embedder (the one its
vectors must come from), so the P-2 (vi) refusal leg is "--embedding-cache-file <nomic DB>" with no --embedding-model (the
manifest names qwen3). ABSENT flags: the DB of record, the manifest's qwen3 model, the same reads as before plus the guard's
read and its printed lines (no statistic, no output file changed). embedder_guard.py is pin-verified on import.
[2026-09-27, the engine-coder, READY_w0_rp08 F1 / F3 (bb30526); insertion only] FT-EMBGUARD now EXECUTES, with DATA_ROOT
pointed at a temp dir whose embeddings_cache.db is an EMPTY decoy: the guard on a TWO-split-site synthetic tree through the
configured cache (ADMIT, each site on its own region, n 120 / 60), and fit_set() reading the CONFIGURED cache (120 texts); a
reader that opened the DB-of-record name instead reads the decoy and fails. embedder_guard.py re-pinned (its docstring and
selftest changed; no guard arithmetic changed).
[2026-09-27, the engine-coder, MIX-FLAT-SELFTEST-GAPS (FLAT half) and FLAT-GENERALITY's parameterisation (programme L21646-L21678);
zero calls; insertion only, nothing above is rewritten] (1) READY dde660e D5: analyze()'s assembly of the result is the function
assemble_res(), and FT-ASSEMBLY executes paired() and assemble_res() on synthetic arms with T's M4 VOID and C1 HELD (mutants R3,
R3b, R3d must die); (2) post-run review 643995a LOW: --analyze prints the before-pins as well as the after-pins; (3) the
functions that read the FLAT-MIX-MMLU constants take optional keyword parameters (tree run dir, snapshot, fit-set size, K, DIM,
partition names, the paired arm and references), each defaulting to the constant above, so every mode of THIS script is
unchanged when they are absent (the inertness proof is flat_generality.py --inertness plus the dry-run diff, recorded with the
build). The driver of FLAT-GENERALITY is tools/analysis/flat_generality.py, which pins this file's blob on import.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported (the author's cap: single-threaded)
    os.environ[_v] = "1"

import sys
import csv
import io
import json
import math
import time
import hashlib
import sqlite3
import argparse
import tempfile
import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

DATA_ROOT = pool_guard.DATA_ROOT
POOL_ID = "p2dca21ab5f4ef3ae"
TAG = "[FLAT-MIX]"

K = 82
SEEDS = (0, 1, 2, 3, 4)
FIT_N = 8125
DIM = 256
V_MAX_ITER, V_TOL = 200, 1e-6
K_MAX_ITER = 300
BOOT_B, BOOT_SEED = 1000, 20260926
T_SNAPSHOT = "20260917_201353_Headless_Run_Auto_ge"
T_RUN = os.path.join("experiment_results", "anchorfree", "redraw", "af_clean_s42", "seed_42")
O_RUN = os.path.join("experiment_results", "anchorfree", "redraw", "o0_clean_s42", "seed_42")
T_LEAVES = 82
RECORD_M1, RECORD_M2 = "0.727 [0.712, 0.741]", "+12.785"
PARTITIONS = ("T", "O") + tuple("V%d" % s for s in SEEDS) + tuple("K%d" % s for s in SEEDS)
IMPORT_PINS = {"anchor_free_readout.py": ("514e74daebb5a631f65e3ed586a856a791fb5a60", "203b62c09b7cfd36"),
               "free_tests_f4_f7.py": ("f0749d6133e030422671d15af69b6cff94ea1298", "463462338e53019e"),
               "embedder_guard.py": ("3fd9aea5b220828f7e6bcb3f115c43aa6743218d", "9393c820af557fb2")}
READOUT_TXT = ("experiment_results/anchorfree/redraw/anchor_free_af_clean_s42_readout.txt",
               "b8dc4dbae0c346f3f20acf0555c8c9c18a9af498", "69715ce266433342")
MDE_M1, MDE_M2 = 0.0213, 0.84e-3
SE_M1, SE_M2 = 0.00762, 0.300e-3
OUT_DIR = os.path.join(ROOT, "experiment_results", "flat_mix_mmlu")
STATE_DIR = os.path.join(OUT_DIR, "state")
OUTCOME = os.path.join(OUT_DIR, "flat_mix_mmlu_outcome.txt")
ARMS_CSV = os.path.join(OUT_DIR, "flat_mix_mmlu_arms.csv")
CHUNK_WALL_S = 240.0
PIN_TABLES = (("embeddings_cache.db", "embeddings", "query"), ("embeddings_cache.db", "queries", "id"),
              ("mmlu_pro_dataset_cache_v2.db", "mmlu_pro", "id"), ("mmlu_pro_dataset_cache_v2.db", "eval_question_link", "question_id"),
              ("mmlu_pro_dataset_cache_v2.db", "eval_results", "question_id, model_name"),
              ("mmlu_pro_dataset_cache_v2.db", "reserved_pool", "pool_id, question_id"))


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ------------------------------------------------------------------------------------------------ connect guard
_RAW_CONNECT = getattr(sqlite3.connect, "_raw", sqlite3.connect)
ALLOWED_DB_BASENAMES = ("embeddings_cache.db", "mmlu_pro_dataset_cache_v2.db", "snapshots.db", "snapshots_frozen.db")


def _admit(s, uri):
    """-> the URI actually opened: file: + mode=ro required, four DBs only, no non-empty -wal / -journal, immutable=1 added."""
    if not (uri and s.startswith("file:")):
        refuse("sqlite3.connect(%r) is not a file: URI opened with uri=True" % s)
    path, _, query = s[5:].partition("?")
    params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
    if params.get("mode") != "ro":
        refuse("sqlite3.connect(%r): only mode=ro is admitted" % s)
    if os.path.basename(path) not in ALLOWED_DB_BASENAMES:
        refuse("sqlite3.connect(%r): %s is not a DB this test reads" % (s, os.path.basename(path)))
    for side in ("-wal", "-journal"):
        sp = os.path.abspath(path) + side
        if os.path.exists(sp) and os.path.getsize(sp) > 0:
            refuse("%s is non-empty (%d bytes): an immutable read would hide it (pool_guard.open_ro's rule)" % (sp, os.path.getsize(sp)))
    if params.get("immutable") != "1":
        params["immutable"] = "1"
    return "file:%s?%s" % (path, "&".join("%s=%s" % kv for kv in params.items()))


def _guarded_connect(database, *a, **k):
    return _RAW_CONNECT(_admit(str(database), k.get("uri")), *a, **k)


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


for _f, (_b, _l) in IMPORT_PINS.items():                  # the imported instrument is the registered one, or nothing runs
    verify_pin(os.path.join(HERE, _f), _b, _l)
import anchor_free_readout as AF  # noqa: E402
import free_tests_f4_f7 as F      # noqa: E402
import rejudge_grok as RJ         # noqa: E402
import split_side                 # noqa: E402
import embedder_guard as EG       # noqa: E402

for _mod, _attr, _name in ((AF, "EMB_DB", "embeddings_cache.db"), (AF, "EVAL_DB", "mmlu_pro_dataset_cache_v2.db"),
                           (RJ, "EVAL_DB", "mmlu_pro_dataset_cache_v2.db"), (F, "EMB_DB", "embeddings_cache.db")):
    setattr(_mod, _attr, os.path.join(DATA_ROOT, _name))  # the caches live under DATA_ROOT (a worktree has none)


def data_path(rel):
    return os.path.join(DATA_ROOT, rel)


# ------------------------------------------------------------------------------------------------ EMBEDDER-PLUMBING (RP08)
EMB_DB_NAME = "embeddings_cache.db"   # the embedding cache the readers open: DATA_ROOT-relative, or an absolute path
EMB_MODEL_EXPLICIT = None             # --embedding-model: the TREE's embedder, the model the opened vectors must come from
EMB_CACHE_SET = False                 # whether --embedding-cache-file was given
# EMB-TARGET-DIR (READY_emb_target 6202766 C-ET-3; 2026-09-29, insertion): an EMBEDDER-CROSS-FLAT arm file (a card file, a file
# with the pre-embedder's provenance beside it, or any file under DATA_ROOT/EMB_CROSS_DIR) is configured ONLY by
# embedder_arms.configure_arm_copy (copy-only + provenance + registrar pin), which names the one path it checked here for the
# duration of its call; the --embedding-cache-file route (and any other caller) REFUSES such a file. Absent any such file: inert.
EMB_CROSS_DIR = os.path.join("experiment_results", "embedder_cross")
ARM_COPY_ADMITTED = None


def is_arm_copy(path):
    xd = os.path.normcase(os.path.abspath(data_path(EMB_CROSS_DIR))) + os.sep
    return bool(os.path.basename(path).endswith("__card.db") or os.path.exists(path + ".provenance.json")
                or os.path.normcase(os.path.abspath(path)).startswith(xd))


def configure_embedding(cache_file=None, model=None):
    """EMBEDDER-PLUMBING (e): the FLAT reader's embedding DB as a parameter. Both None -> nothing changes (byte-inert)."""
    global EMB_DB_NAME, EMB_MODEL_EXPLICIT, EMB_CACHE_SET, PIN_TABLES, ALLOWED_DB_BASENAMES
    if model is not None:
        if not model.strip():
            refuse("--embedding-model is present but blank")
        EMB_MODEL_EXPLICIT = model
    if cache_file is not None:
        if not cache_file.strip():
            refuse("--embedding-cache-file is present but blank")
        path = os.path.abspath(data_path(cache_file))
        if is_arm_copy(path) and os.path.normcase(ARM_COPY_ADMITTED or "") != os.path.normcase(path):
            refuse("--embedding-cache-file %s is an EMBEDDER-CROSS-FLAT arm file: it is read only through "
                   "embedder_arms.configure_arm(target_dir=...) (copy-only, provenance and registrar pin; C-ET-3)" % path)
        base = os.path.basename(path)
        if base not in ALLOWED_DB_BASENAMES:
            ALLOWED_DB_BASENAMES = ALLOWED_DB_BASENAMES + (base,)
        EG.validate_cache_file(path)
        EMB_DB_NAME, EMB_CACHE_SET = path, True
        PIN_TABLES = ((path, "embeddings", "query"), (path, "queries", "id")) + tuple(t for t in PIN_TABLES if t[0] != "embeddings_cache.db")
        AF.EMB_DB = F.EMB_DB = path


def embedding_guard_flat(graph=None, manifest_path=None, dim=None):
    """EMBEDDER-PLUMBING (c)/(d), BEFORE any partition fit: the model named by the tree's run manifest (or --embedding-model),
    then embedder_guard.guard_file on the snapshot's accepted split sites against the OPENED cache. Refuses on any finding.
    graph / manifest_path / dim default to FLAT-MIX-MMLU's T (af_clean_s42: T_SNAPSHOT, T_RUN's run_manifest.json, DIM)."""
    mp = manifest_path if manifest_path is not None else os.path.join(data_path(T_RUN), "diagnostics", "run_manifest.json")
    manifest = {}
    if os.path.exists(mp):
        with open(mp, encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        print("%s [EMB-GUARD] run manifest %s not found: the model must be named by --embedding-model" % (TAG, mp))
    model, source = EG.resolve_model(manifest, EMB_MODEL_EXPLICIT, EMB_CACHE_SET)
    g = load_snapshot_graph(T_SNAPSHOT) if graph is None else graph
    return EG.guard_file(data_path(EMB_DB_NAME), g["byid"], lambda s: region_query_ids(s["id"], g["byid"]),
                         DIM if dim is None else dim, model, source)


def configure_from_args(a):
    """main()'s embedding flags: admitted with --dry-run and --identity-check only; absent -> nothing is configured."""
    if (a.embedding_cache_file is not None or a.embedding_model is not None) and not (a.dry_run or a.identity_check):
        refuse("--embedding-cache-file / --embedding-model are admitted with --dry-run and --identity-check only (FLAT-MIX-MMLU's "
               "state and outcome of record are on the DB of record; FLAT-GENERALITY calls configure_embedding)")
    if a.embedding_cache_file is not None or a.embedding_model is not None:
        configure_embedding(cache_file=a.embedding_cache_file, model=a.embedding_model)


# ------------------------------------------------------------------------------------------------ vMF / k-means
B6 = "ruling B6 (programme L20864-L20919): the seed is VOID; the analysis refuses; a failed precondition"


class Degenerate(Exception):
    """A degenerate vMF fit: a one-member / degenerate cell (mean resultant length outside (0, 1)) or an underflowing ive.
    In a V seed it is ruling B6 (refuse); in the descriptive M4 refit of T, K or O it VOIDs M4 for that arm only (ruling O2)."""


def log_cd(d, kappa):
    """log C_d(kappa) = (d/2 - 1) log kappa - (d/2) log 2 pi - log I_{d/2-1}(kappa), I via scipy.special.ive."""
    from scipy.special import ive
    kappa = np.asarray(kappa, dtype=np.float64)
    v = d / 2.0 - 1.0
    iv = ive(v, kappa)
    if not np.all(np.isfinite(iv)) or np.any(iv <= 0):
        raise Degenerate("ive(%g, kappa) underflows or is not finite for kappa in [%g, %g]" % (v, kappa.min(), kappa.max()))
    return v * np.log(kappa) - (d / 2.0) * math.log(2 * math.pi) - (np.log(iv) + kappa)


def banerjee_kappa(rbar, d):
    rbar = np.asarray(rbar, dtype=np.float64)
    if np.any(rbar >= 1.0) or np.any(rbar <= 0.0):
        raise Degenerate("mean resultant length outside (0, 1) (a one-member or degenerate cell)")
    return rbar * (d - rbar ** 2) / (1.0 - rbar ** 2)


def unit_rows(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return M / n


def kmeanspp(X, k, rng):
    """k-means++ seeding on the sphere: the first centre uniform, then D^2 sampling with D^2 = ||x - c||^2 = 2 - 2 cos."""
    n = X.shape[0]
    idx = [int(rng.integers(n))]
    d2 = np.maximum(2.0 - 2.0 * (X @ X[idx[0]]), 0.0)
    for _ in range(1, k):
        s = d2.sum()
        j = int(rng.choice(n, p=d2 / s)) if s > 0 else int(rng.integers(n))
        idx.append(j)
        d2 = np.minimum(d2, np.maximum(2.0 - 2.0 * (X @ X[j]), 0.0))
    return X[idx].copy()


def spherical_kmeans(X, k, seed, max_iter=K_MAX_ITER):
    rng = np.random.default_rng(seed)
    C = kmeanspp(X, k, rng)
    labels = None
    it = 0
    converged = False
    for it in range(1, max_iter + 1):
        new = np.argmax(X @ C.T, axis=1)
        if labels is not None and np.array_equal(new, labels):
            converged = True
            break
        labels = new
        for j in range(k):
            m = labels == j
            if m.any():
                s = X[m].sum(axis=0)
                C[j] = s / np.linalg.norm(s)
    return dict(centers=C, labels=labels, iters=it, converged=converged)


def vmf_params_from_labels(X, labels, k, d):
    """mu = normalised mean, kappa by Banerjee, pi = share, for every cell with members; absent cells get pi = 0."""
    mu = np.zeros((k, d))
    kappa = np.ones(k)
    pi = np.zeros(k)
    for j in range(k):
        m = labels == j
        if m.any():
            s = X[m].sum(axis=0)
            nrm = np.linalg.norm(s)
            mu[j] = s / nrm
            kappa[j] = banerjee_kappa(nrm / m.sum(), d)
            pi[j] = m.sum() / X.shape[0]
    return mu, kappa, pi


def vmf_logp(X, mu, kappa, pi):
    """n x k: log pi_k + log C_d(kappa_k) + kappa_k mu_k . x (cells with pi = 0 get -inf)."""
    d = X.shape[1]
    live = pi > 0
    out = np.full((X.shape[0], len(pi)), -np.inf)
    out[:, live] = np.log(pi[live]) + log_cd(d, kappa[live]) + (X @ mu[live].T) * kappa[live]
    return out


def logsumexp_rows(A):
    m = np.max(A, axis=1, keepdims=True)
    return (m + np.log(np.sum(np.exp(A - m), axis=1, keepdims=True)))[:, 0]


def vmf_em(X, k, seed, max_iter=V_MAX_ITER, tol=V_TOL):
    try:
        return _vmf_em(X, k, seed, max_iter, tol)
    except Degenerate as e:
        refuse("V seed %d: %s; %s" % (seed, e, B6))


def _vmf_em(X, k, seed, max_iter, tol):
    n, d = X.shape
    rng = np.random.default_rng(seed)
    C0 = kmeanspp(X, k, rng)
    lab0 = np.argmax(X @ C0.T, axis=1)
    mu, kappa, pi = vmf_params_from_labels(X, lab0, k, d)
    if np.any(pi == 0):
        refuse("V seed %d: a k-means++ seed owns no point after the hard step; %s" % (seed, B6))
    prev = None
    converged = False
    it = 0
    mean_ll = None
    for it in range(1, max_iter + 1):
        lp = vmf_logp(X, mu, kappa, pi)
        ll = logsumexp_rows(lp)
        mean_ll = float(ll.mean())
        if prev is not None and abs(mean_ll - prev) < tol:
            converged = True
            break
        prev = mean_ll
        R = np.exp(lp - ll[:, None])
        Nk = R.sum(axis=0)
        if np.any(Nk <= 0):
            refuse("V seed %d: a vMF component lost all responsibility at iteration %d; %s" % (seed, it, B6))
        S = R.T @ X
        nrm = np.linalg.norm(S, axis=1)
        mu = S / nrm[:, None]
        kappa = banerjee_kappa(nrm / Nk, d)
        pi = Nk / n
    return dict(mu=mu, kappa=kappa, pi=pi, iters=it, converged=converged, mean_ll=mean_ll)


def m4_refit(X, labels, k):
    """Ruling O2: the descriptive M4 mixture of T, K or O; a degenerate cell VOIDs M4 for this arm only (never C1 / C2)."""
    try:
        mu, kappa, pi = vmf_params_from_labels(X, labels, k, X.shape[1])
    except Degenerate as why:
        return dict(mu=None, kappa=None, pi=None, m4_void="M4 VOID (ruling O2): %s" % why)
    return dict(mu=mu.tolist(), kappa=kappa.tolist(), pi=pi.tolist(), m4_void=None)


def m4_block(body, Qh):
    """-> (mean ll, per-question ll, void reason). V (rule 'map'): a degenerate V is ruling B6 and REFUSES."""
    if body.get("m4_void"):
        return None, None, body["m4_void"]
    try:
        ll = heldout_ll(Qh, np.array(body["mu"]), np.array(body["kappa"]), np.array(body["pi"]))
    except Degenerate as why:
        if body["rule"] == "map":
            refuse("V partition %s: %s; %s" % (body["partition"], why, B6))
        return None, None, "M4 VOID (ruling O2): %s" % why
    return float(ll.mean()), ll, None


def map_assign(Q, mu, kappa, pi):
    return np.argmax(vmf_logp(Q, mu, kappa, pi), axis=1)


def nearest_assign(Q, M):
    return np.argmax(Q @ unit_rows(M).T, axis=1)


def heldout_ll(Q, mu, kappa, pi):
    return logsumexp_rows(vmf_logp(Q, mu, kappa, pi))


# ------------------------------------------------------------------------------------------------ bootstrap and criteria
def twin_groups(texts):
    keys = [split_side.stem_key(t) for t in texts]
    ids = {}
    return np.array([ids.setdefault(k, len(ids)) for k in keys]), len(ids)


def group_members(groups):
    members = [[] for _ in range(int(groups.max()) + 1)]
    for i, g in enumerate(groups):
        members[g].append(i)
    return [np.array(m, dtype=int) for m in members]


def twin_boot_indices(groups, rng, members=None):
    """One resample: whole groups drawn with replacement; returns the question indices (every member of every drawn group)."""
    members = members if members is not None else group_members(groups)
    G = len(members)
    draw = rng.integers(0, G, size=G)
    return np.concatenate([members[g] for g in draw])


def twin_boot_ci(diff, groups, B=BOOT_B, seed=BOOT_SEED):
    """Percentile 95% CI of the mean paired difference over B whole-group resamples (F6's index convention)."""
    diff = np.asarray(diff, dtype=np.float64)
    members = group_members(groups)
    rng = np.random.default_rng(seed)
    bs = sorted(float(diff[twin_boot_indices(groups, rng, members)].mean()) for _ in range(B))
    return bs[int(0.025 * B)], bs[int(0.975 * B) - 1]


def kish_mbar(groups):
    c = np.bincount(groups).astype(np.float64)
    return float((c ** 2).sum() / c.sum())


def spread(vals):
    return float(max(vals) - min(vals))


def spread_opt(vals):
    """spread over the seeds, or None when any seed's value is VOID (M4 under ruling O2; never M1 / M2)."""
    return None if any(v is None for v in vals) else spread(vals)


def criterion(diff, spr, lo, hi):
    """HELD iff diff > spread AND the paired 95% CI excludes 0 on the positive side (one conjunctive clause)."""
    return bool(diff > spr and lo > 0)


def loss(diff, spr, lo, hi):
    return bool(diff < -spr and hi < 0)


def reading(c1, c2, l1):
    """-> (label, joined). The registered table T-1..T-5; ruling B5: C1 HELD with L1 FIRED (on M2) is (T-5), recorded joined."""
    if c1 and l1:
        return "T-5", True
    if c1:
        return "T-3", False
    if l1 and c2:
        return "T-5", False
    if l1:
        return "T-4", False
    if c2:
        return "T-2", False
    return "T-1", False


READING_TEXT = {
    "T-1": "(T-1) the 20NG sentence TRANSFERS to MMLU-Pro: the hierarchy buys the certificate, the support per cell, the names and "
           "the routing discipline, not a better partition; worded \"not shown to partition better at MDE 2.1 pp purity / 0.84 x1e-3 "
           "F6\", never \"equal\".",
    "T-2": "(T-2) a NEW PRO-TREE sentence candidate (the tree's cuts carry more key information than an unconstrained mixture at the "
           "same k); PROVISIONAL until a second seed replicates it in a new registration on a second content-closed anchor-free "
           "tree; recorded as \"one seed, not replicated\".",
    "T-3": "(T-3) the tree is a better partition on MMLU-Pro and the 20NG sentence does NOT transfer; the same second-seed requirement.",
    "T-4": "(T-4) the size floor and the greedy cuts cost partition quality or key information: a LIMITATION for the construction "
           "chapter's record.",
    "T-5": "(T-5) a mixed pattern: recorded joined; no sentence; the research-lead's synthesis.",
    "C1+L1": "recorded JOINED as \"C1 HELD / L1 FIRED on M2\" (ruling B5, the registrar's, derived from (T-5)'s own example): "
             "reading (T-5), a mixed pattern; NO SENTENCE; the research-lead's synthesis; F1 fires and P7 is FAILED.",
}


def render(res):
    """res: dict with per-arm measures and the paired quantities. Returns the outcome lines (every branch reachable)."""
    L = []
    L.append("=== FLAT-MIX-MMLU outcome (docs/judge_v2_program.md L20672-L20735; zero calls) ===")
    L.append("pool %s: held-out %d judgeable questions in %d stem_key twin groups (Kish mean group size %.4f); keyed questions %d"
             % (POOL_ID, res["n_heldout"], res["n_groups"], res["mbar"], res["n_keyed"]))
    L.extend(res.get("info", []))
    L.append("")
    L.append("PER ARM (M1 held-out purity [Wilson 95%%], M2 F6 x1000, M3 split-half R(SB) at leaves, M4 held-out mean ll in nats):".replace("%%", "%"))
    for a in res["order"]:
        m = res["arms"][a]
        L.append("  %-3s M1 %.3f [%.3f, %.3f] (%d/%d) | M2 %+.3f | M3 %s | M4 %s%s"
                 % (a, m["m1"], m["m1_lo"], m["m1_hi"], m["hits"], res["n_heldout"], 1000 * m["m2"],
                    "NA" if m["m3"] is None else "%.3f" % m["m3"], "%.4f" % m["m4"] if m["m4"] is not None else
                    (m.get("m4_void") or "M4 VOID (ruling O2)") + " [C1 / C2 unaffected]", m.get("note", "")))
    sv1, sv2 = res["spread_V"]["m1"], res["spread_V"]["m2"]
    sk1, sk2 = res["spread_K"]["m1"], res["spread_K"]["m2"]
    f4 = lambda x: "NA (an M4 VOID)" if x is None else "%.4f" % x
    L.append("  spread_V: M1 %.4f, M2 %.3f x1e-3, M4 %s | spread_K: M1 %.4f, M2 %.3f x1e-3, M4 %s"
             % (sv1, 1000 * sv2, f4(res["spread_V"]["m4"]), sk1, 1000 * sk2, f4(res["spread_K"]["m4"])))
    L.append("")
    p = res["paired"]["V0"]
    c1 = criterion(p["d1"], sv1, p["d1_lo"], p["d1_hi"])
    c2 = criterion(p["d2"], sv2, p["d2_lo"], p["d2_hi"])
    l1_m1 = loss(p["d1"], sv1, p["d1_lo"], p["d1_hi"])
    l1_m2 = loss(p["d2"], sv2, p["d2_lo"], p["d2_hi"])
    l1 = bool(l1_m1 or l1_m2)
    L.append("CRITERIA (against V0; the point decides the seed-spread leg, the interval the CI leg; one conjunctive clause each):")
    L.append("  C1 PURITY: M1(T) - M1(V0) = %+.4f, twin-group 95%% CI [%+.4f, %+.4f], spread_V %.4f (MDE %.4f; effective threshold %.4f, "
             "bound by %s) -> %s" % (p["d1"], p["d1_lo"], p["d1_hi"], sv1, MDE_M1, max(MDE_M1, sv1),
                                      "the seed spread" if sv1 > MDE_M1 else "the MDE", "HELD" if c1 else "FAILED"))
    L.append("  C2 KEY INFORMATION: M2(T) - M2(V0) = %+.3f x1e-3, F6 95%% CI [%+.3f, %+.3f], spread_V %.3f x1e-3 (MDE %.2f; effective "
             "threshold %.3f, bound by %s) -> %s" % (1000 * p["d2"], 1000 * p["d2_lo"], 1000 * p["d2_hi"], 1000 * sv2, 1000 * MDE_M2,
                                                  1000 * max(MDE_M2, sv2), "the seed spread" if sv2 > MDE_M2 else "the MDE",
                                                  "HELD" if c2 else "FAILED"))
    L.append("  L1 LOSS FLAG: %s (M1 loss %s, M2 loss %s)" % ("FIRES" if l1 else "does not fire", "yes" if l1_m1 else "no", "yes" if l1_m2 else "no"))
    k = res["paired"]["K0"]
    L.append("  BESIDE (reported only) against K0 with spread_K: M1 %+.4f [%+.4f, %+.4f] -> %s; M2 %+.3f [%+.3f, %+.3f] x1e-3 -> %s; loss %s"
             % (k["d1"], k["d1_lo"], k["d1_hi"], "win" if criterion(k["d1"], sk1, k["d1_lo"], k["d1_hi"]) else "no win",
                1000 * k["d2"], 1000 * k["d2_lo"], 1000 * k["d2_hi"], "win" if criterion(k["d2"], sk2, k["d2_lo"], k["d2_hi"]) else "no win",
                "yes" if (loss(k["d1"], sk1, k["d1_lo"], k["d1_hi"]) or loss(k["d2"], sk2, k["d2_lo"], k["d2_hi"])) else "no"))
    if p["d4"] is None:
        L.append("  M4 (DESCRIPTIVE BY DESIGN): T - V0 not computed: M4 VOID for T (ruling O2; C1, C2 and L1 are unaffected)")
    else:
        L.append("  M4 (DESCRIPTIVE BY DESIGN; V maximises this likelihood): T - V0 = %+.4f nats, twin-group 95%% CI [%+.4f, %+.4f]%s"
                 % (p["d4"], p["d4_lo"], p["d4_hi"], " (a T ADVANTAGE: notable, not scored)" if p["d4"] > 0 and p["d4_lo"] > 0 else ""))
    L.append("")
    lab, joined = reading(c1, c2, l1)
    L.append("THE READING OF THE OUTCOME: %s" % (READING_TEXT["C1+L1"] + " " + READING_TEXT["T-5"] if joined else READING_TEXT[lab]))
    L.append("")
    L.append("PREDICTIONS:")

    def sc(ok):
        return "HELD" if ok else "FAILED"
    L.append("  P1a M1(T) - M1(V0) = -0.005, 80%% [-0.025, +0.015]: observed %+.4f -> %s" % (p["d1"], sc(-0.025 <= p["d1"] <= 0.015)))
    L.append("  P1b C1 FAILED (p 0.80): C1 %s -> %s" % ("HELD" if c1 else "FAILED", sc(not c1)))
    L.append("  P2a M2(T) - M2(V0) = +0.3 x1e-3, 80%% [-1.0, +1.5]: observed %+.3f -> %s" % (1000 * p["d2"], sc(-1.0e-3 <= p["d2"] <= 1.5e-3)))
    L.append("  P2b C2 FAILED (p 0.75): C2 %s -> %s" % ("HELD" if c2 else "FAILED", sc(not c2)))
    L.append("  P3 spread_V(M1) = 0.008, 80%% [0.003, 0.020]: observed %.4f -> %s" % (sv1, sc(0.003 <= sv1 <= 0.020)))
    if res["arms"]["T"]["m4"] is None or res["arms"]["V0"]["m4"] is None:
        L.append("  P4 M4: V0 above T (p 0.85): UNSCOREABLE (M4 VOID for T, ruling O2)")
    else:
        L.append("  P4 M4: V0 above T (p 0.85): V0 %.4f, T %.4f -> %s" % (res["arms"]["V0"]["m4"], res["arms"]["T"]["m4"],
                                                                         sc(res["arms"]["V0"]["m4"] > res["arms"]["T"]["m4"])))
    dk = abs(res["arms"]["K0"]["m1"] - res["arms"]["V0"]["m1"])
    L.append("  P5 |M1(K0) - M1(V0)| <= 0.010 (p 0.70): %.4f -> %s" % (dk, sc(dk <= 0.010)))
    L.append("  P6 L1 fires (p 0.15): L1 %s -> %s" % ("fired" if l1 else "not fired", sc(l1)))
    L.append("  P7 the reading is (T-1) (the largest registered probability, 0.65): observed %s -> %s" % (lab, sc(lab == "T-1")))
    ident = res["identity"]
    L.append("  P8 the identity check reproduces M1 %s and M2 %s: observed M1 %s, M2 %s -> %s"
             % (RECORD_M1, RECORD_M2, ident["m1"], ident["m2"], sc(ident["m1"] == RECORD_M1 and ident["m2"] == RECORD_M2)))
    L.append("")
    if c1 or c2 or l1:
        L.append("FALSIFIER F1 FIRES (%s): the registered expectation that the TOPIC-PARTITION-20NG sentence holds on MMLU-Pro is "
                 "overturned (%s); TOPIC-PARTITION-20NG stands on 20NG." % (", ".join(x for x, y in (("C1 HELD", c1), ("C2 HELD", c2),
                                                                                                    ("L1 FIRED", l1)) if y),
                                                                          "a WIN: a second seed before any sentence of record" if (c1 or c2) and not l1
                                                                          else "a LOSS: a stated limitation" if l1 and not (c1 or c2)
                                                                          else "a mixed pattern"))
    else:
        L.append("FALSIFIER F1 does not fire (C1 FAILED, C2 FAILED, L1 not fired).")
    L.append("")
    L.append("SUPPORT:")
    L.append("  (a) C1: %d held-out questions in %d twin groups (Kish mean size %.4f; DEFF upper bound %.4f at rho = 1); C2: %d keyed"
             " questions (F6's unit)." % (res["n_heldout"], res["n_groups"], res["mbar"], res["mbar"], res["n_keyed"]))
    L.append("  (b) DEFF C1 1.0 declared (measured m-bar above); C2 transported from anchor_free_af_clean_s42_readout.txt (-0.409 [-0.976, +0.201]).")
    L.append("  (c) n_eff C1 %d / 1.0; C2 inside the transported SE." % res["n_heldout"])
    L.append("  (d) SE C1 sqrt(0.20 / 3,445) = %.5f (declared discordance 0.20; observed discordance T vs V0 %.4f); C2 %.3f x1e-3."
             % (SE_M1, res["discordance"], 1000 * SE_M2))
    L.append("  (e) MDE C1 %.4f (2.1 pp), C2 %.2f x1e-3; effective thresholds max(MDE, spread_V): C1 %.4f, C2 %.3f x1e-3."
             % (MDE_M1, 1000 * MDE_M2, max(MDE_M1, sv1), 1000 * max(MDE_M2, sv2)))
    L.append("  (f) a FAILED C1 / C2 licenses \"not shown better at MDE 2.1 pp / 0.84 x1e-3\", never equivalence.")
    L.append("  (g) the seed-spread leg does not shrink with n; spread_V printed beside every difference.")
    return L, dict(c1=c1, c2=c2, l1=l1, reading=lab, joined=joined)


# ------------------------------------------------------------------------------------------------ inputs
def load_snapshot_graph(snapshot_id):
    p = data_path("snapshots.db")
    con = pool_guard.open_ro(p)
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (snapshot_id,)).fetchone()
    finally:
        con.close()
    if row is None:
        refuse("snapshot %s not in %s" % (snapshot_id, p))
    g = json.loads(row[0])
    return dict(sha=hashlib.sha256(row[0].encode("utf-8")).hexdigest(), byid={n["id"]: n for n in g["nodes"]}, root=g["rootId"])


def region_query_ids(root_id, byid):
    """SeparationNullBySizeTest.regionQueryIds (the same DFS as mix_lrt_site.region_query_ids)."""
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


def assert_fit_count(n, fit_n=None):
    fit_n = FIT_N if fit_n is None else fit_n
    if n != fit_n:
        refuse("the fit set has %d texts; the registration fixes the tree's %d root texts (no substitution)" % (n, fit_n))


def fit_set(snapshot=None, fit_n=None):
    g = load_snapshot_graph(T_SNAPSHOT if snapshot is None else snapshot)
    ids = region_query_ids(g["root"], g["byid"])
    assert_fit_count(len(ids), fit_n)
    con = pool_guard.open_ro(data_path(EMB_DB_NAME))
    text = {}
    try:
        for s in range(0, len(ids), 400):
            ch = ids[s:s + 400]
            for qid, t in con.execute("SELECT id, distilled_text FROM queries WHERE id IN (%s)" % ",".join("?" * len(ch)), ch):
                text[qid] = t
    finally:
        con.close()
    miss = [i for i in ids if i not in text]
    if miss:
        refuse("%d fit-set ids have no queries row (e.g. %s)" % (len(miss), miss[:3]))
    texts = sorted(set(text[i] for i in ids))
    assert_fit_count(len(texts), fit_n)
    return texts, g, ids, text


def fit_matrix(texts, dim=None):
    vec = AF.full_vectors(texts)
    miss = [t for t in texts if t not in vec]
    if miss:
        refuse("%d fit texts have no embedding" % len(miss))
    return AF.sliced(vec, texts, DIM if dim is None else dim)


def load_T(which="T", run=None, leaves=None, dim=None, name=None):
    """The tree of arm `which`; run / leaves / dim / name default to FLAT-MIX-MMLU's T (af_clean_s42) or O (o0_clean_s42)."""
    rd = data_path(run if run is not None else (T_RUN if which == "T" else O_RUN))
    dim = DIM if dim is None else dim
    n_leaves = leaves if leaves is not None else (T_LEAVES if which == "T" else None)
    tree = AF.load_tree(rd)
    if n_leaves is not None and len(tree["leaves"]) != n_leaves:
        refuse("%s has %d leaves, registered %d" % (name or "af_clean_s42", len(tree["leaves"]), n_leaves))
    if tree["dim"] != dim:
        refuse("%s slice dim %d != %d" % (which, tree["dim"], dim))
    return tree


# ------------------------------------------------------------------------------------------------ partitions (state)
def write_once(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def fit_partition(name, X, k=None, tree_kw=None):
    """-> the state body of one partition: its assignment rule's parameters and the M4 mixture. k defaults to K; tree_kw (the
    keyword arguments of load_T for a T / O partition) defaults to FLAT-MIX-MMLU's trees."""
    t0 = time.process_time()
    k = K if k is None else k
    kind, seed = name[0], (int(name[1:]) if name[0] in "VK" else None)
    if kind == "V":
        r = vmf_em(X, k, seed)
        body = dict(rule="map", mu=r["mu"].tolist(), kappa=r["kappa"].tolist(), pi=r["pi"].tolist(), iters=r["iters"],
                    converged=r["converged"], mean_ll_fit=r["mean_ll"])
    elif kind == "K":
        r = spherical_kmeans(X, k, seed)
        body = dict(rule="nearest", centers=r["centers"].tolist(), iters=r["iters"], converged=r["converged"],
                    **m4_refit(X, r["labels"], k))
    else:
        tree = load_T(kind, **(tree_kw or {}))
        lab = AF.route(tree, X)
        body = dict(rule="flatLeaf", leaf_ids=tree["leaf_ids"], centers=tree["leaf_mu"].tolist(), run_dir=tree["run_dir"],
                    **m4_refit(X, lab, len(tree["leaf_ids"])))
    body.update(partition=name, cpu_s=time.process_time() - t0, script=script_pins())
    return body


def partition_assign(body, Q):
    if body["rule"] == "map":
        return map_assign(Q, np.array(body["mu"]), np.array(body["kappa"]), np.array(body["pi"]))
    return nearest_assign(Q, np.array(body["centers"]))


def cell_ids(body, idx):
    names = body.get("leaf_ids") or ["%s_c%02d" % (body["partition"], j) for j in range(len(body.get("centers") or body["mu"]))]
    return [names[i] for i in idx]


def read_state(state_dir):
    out = {}
    if not os.path.isdir(state_dir):
        return out
    for f in sorted(os.listdir(state_dir)):
        if f.startswith("part_") and f.endswith(".json"):
            with open(os.path.join(state_dir, f), encoding="utf-8") as h:
                b = json.load(h)
            if b["partition"] in out:
                refuse("partition %s present twice in the state" % b["partition"])
            out[b["partition"]] = b
    return out


def require_all(parts, names=None):
    names = PARTITIONS if names is None else names
    missing = [p for p in names if p not in parts]
    if missing:
        refuse("partitions missing: %s (the analysis needs all of %s)" % (missing, "T, V0-V4, K0-K4 and O" if names is PARTITIONS
                                                                         else ", ".join(names)))
    extra = [p for p in parts if p not in names]
    if extra:
        refuse("unexpected partitions in the state: %s" % extra)


# ------------------------------------------------------------------------------------------------ measures (the wrapper)
def m1_block(assign_fn, Qt, Qh, train, heldout):
    kt, kh = assign_fn(Qt), assign_fn(Qh)
    sc = AF.score_cells(kt, kh, train, heldout)
    hits = np.array([1.0 if sc["major"].get(k) == c else 0.0 for k, (_, c) in zip(kh, heldout)])
    if int(hits.sum()) != sc["hits"]:
        refuse("per-question hits disagree with score_cells")
    return sc, hits, kh


def m2_block(assign_fn, keyed, veck):
    models, G, cat, text, qs_all = keyed
    qs = [q for q in qs_all if text[q] in veck]
    Q = np.stack([veck[text[q]] for q in qs])
    part = dict(zip(qs, assign_fn(Q)))
    il = F.loo_imp(part, qs, models, G)
    return dict(n=len(qs), mean=float(il.mean()), per_q=dict(zip(qs, il)))


def m3_block(kh, heldout, heldout_ids):
    r = AF.key_reliability(None, {"heldout_cell": {"leaf": kh, "d1": kh}}, heldout, heldout_ids)["leaf"]
    return None if not r["cells"] else float(r["R"])


def fmt_m1(sc):
    return "%.3f [%.3f, %.3f]" % (sc["acc"], sc["lo"], sc["hi"])


def identity(tree, train, heldout, vec, keyed, veck, dim=None):
    dim = DIM if dim is None else dim
    Qt, Qh = AF.sliced(vec, [t for t, _ in train], dim), AF.sliced(vec, [t for t, _ in heldout], dim)
    fn = lambda Q: [tree["leaf_ids"][i] for i in nearest_assign(Q, tree["leaf_mu"])]
    sc, _, _ = m1_block(fn, Qt, Qh, train, heldout)
    m2 = m2_block(fn, keyed, veck)
    return dict(m1=fmt_m1(sc), m2="%+.3f" % (1000 * m2["mean"]))


# ------------------------------------------------------------------------------------------------ pins of the DBs
def table_pins(tables=None, snapshots=None, runs=None):
    """snapshots / runs default to FLAT-MIX-MMLU's (T's snapshot row; T's and O's dag_snapshots.jsonl)."""
    tables = PIN_TABLES if tables is None else tables      # read at call time (configure_embedding may replace PIN_TABLES)
    lines = {}
    for db, t, order in tables:
        con = pool_guard.open_ro(data_path(db))
        try:
            h, n = hashlib.sha256(), 0
            for row in con.execute('SELECT * FROM "%s" ORDER BY %s' % (t, order)):
                h.update(repr(row).encode())
                h.update(b"\n")
                n += 1
        finally:
            con.close()
        lines["%s:%s" % (db, t)] = "n=%d sha256=%s" % (n, h.hexdigest())
    for sid in ((T_SNAPSHOT,) if snapshots is None else snapshots):
        g = load_snapshot_graph(sid)
        lines["snapshots.db:snapshots[%s]" % sid] = "graph sha256=%s" % g["sha"]
    for rd in ((T_RUN, O_RUN) if runs is None else runs):
        p = os.path.join(data_path(rd), "dag_snapshots.jsonl")
        with open(p, "rb") as f:
            lines[rd.replace(os.sep, "/") + "/dag_snapshots.jsonl"] = "sha256-bytes=%s" % hashlib.sha256(f.read()).hexdigest()
    return lines


def check_pins_after(before, **pin_kw):
    after = table_pins(**pin_kw)
    for k, v in after.items():
        print("[PIN after ] %s %s" % (k, v))
    bad = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
    if bad:
        refuse("a pinned input changed during the run: %s" % bad)
    print("[PIN] before == after on every pinned table / row / file")


# ------------------------------------------------------------------------------------------------ modes
def header():
    pid = pool_guard.assert_pool_of_record(POOL_ID)
    print("pool %s (pool_guard.assert_pool_of_record: id file and reserved_pool rows agree; opened mode=ro&immutable=1)" % pid)
    print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    print("[SCRIPT] tools/analysis/flat_mix_mmlu.py %s" % fmt_pins(script_pins()))
    for f, (b, l) in IMPORT_PINS.items():
        print("[PIN] tools/analysis/%s %s (registered; verified)" % (f, fmt_pins(pins_of(os.path.join(HERE, f)))))
    for m in ("consensus_tree", "profile_reliability", "rubric_p8", "h9_stability", "t3_routing_inflation", "free_tests_f",
              "rejudge_grok", "judge_free_tests", "split_side", "pool_guard"):
        print("[PIN] tools/analysis/%s.py %s (imported; printed for the READY)" % (m, fmt_pins(pins_of(os.path.join(HERE, m + ".py")))))
    print("[DATA] DATA_ROOT %s" % DATA_ROOT)
    embedding_guard_flat()
    return pid


def dry_run():
    header()
    print("[MODE] --dry-run: counts, pins and the plan only; NO measure (M1-M4), no fit, nothing written")
    print("[PRECONDITION OWED] content closure: the data-steward confirms at the READY that the build's keyRule ck-v1 equals "
          "CK-CLOSE-v1's stem_key (split_side.KEY_RULE = %r; build.out '[SPLIT-SIDE] ... keyRule=ck-v1'; not decided here)" % split_side.KEY_RULE)
    p = verify_pin(os.path.join(ROOT, READOUT_TXT[0]), READOUT_TXT[1], READOUT_TXT[2])
    print("[PIN] %s %s (the transported C2 SE and the identity values)" % (READOUT_TXT[0], fmt_pins(p)))
    t0 = time.perf_counter()
    pins = table_pins()
    for k, v in pins.items():
        print("[PIN table/row/file] %s %s" % (k, v))
    print("[PIN] %.1f s (taken before and after --run and --analyze)" % (time.perf_counter() - t0))
    texts, g, ids, text = fit_set()
    ok_ids = sum(1 for i in ids if i == "q_" + hashlib.sha256(text[i].encode("utf-8")).hexdigest()[:16])
    print("FIT SET: snapshot %s root %s: %d member ids == %d distinct texts (ASSERTED %d); ids equal to q_ + sha256(text)[:16]: %d of %d"
          % (T_SNAPSHOT, g["root"], len(ids), len(texts), FIT_N, ok_ids, len(ids)))
    vec = AF.full_vectors(texts)
    print("  fit texts with an embedding: %d of %d" % (sum(1 for t in texts if t in vec), len(texts)))
    train, heldout, cs = AF.corpus(POOL_ID)
    tr, ho = set(t for t, _ in train), set(t for t, _ in heldout)
    print("READOUT SETS: corpus %d mmlu_pro rows, %d distinct texts; held-out %d questions (%d distinct texts); train %d texts"
          % (cs["rows"], cs["distinct"], len(heldout), len(ho), len(train)))
    print("  fit texts among the readout's train texts: %d; among held-out texts: %d (content hygiene count; must be 0)"
          % (sum(1 for t in texts if t in tr), sum(1 for t in texts if t in ho)))
    groups, G = twin_groups([t for t, _ in heldout])
    sizes = np.bincount(groups)
    print("  held-out stem_key twin groups: %d groups; %d groups with more than one question (holding %d questions)"
          % (G, int((sizes > 1).sum()), int(sizes[sizes > 1].sum())))
    for which in ("T", "O"):
        tr_ = load_T(which)
        print("ARM %s: %s | %d leaves, %d nodes, slice %d, manifest pool %s" % (which, tr_["name"], len(tr_["leaves"]), tr_["nodes"],
              tr_["dim"], tr_["manifest"].get("reserved_pool_id", "?")))
    keyed = F.keyed_questions()
    print("KEYED (F6): %d questions, %d models" % (len(keyed[4]), len(keyed[0])))
    print("PLAN: %d partitions %s; one per chunk; V: EM k %d, max_iter %d, tol %g; K: spherical k-means, max_iter %d; bootstrap %d "
          "twin-group resamples (seed %d); F6 CI by boot_mean_ci (B %d, seed 42)" % (len(PARTITIONS), ",".join(PARTITIONS), K, V_MAX_ITER,
                                                                                      V_TOL, K_MAX_ITER, BOOT_B, BOOT_SEED, F.B))
    rng = np.random.default_rng(1)
    Xs = unit_rows(rng.standard_normal((FIT_N, DIM)))
    t0 = time.process_time()
    r = vmf_em(Xs, K, 0, max_iter=5, tol=0.0)
    per_it = (time.process_time() - t0) / 5
    t0 = time.process_time()
    spherical_kmeans(Xs, K, 0, max_iter=5)
    per_km = (time.process_time() - t0) / 5
    print("COST (SYNTHETIC timing, n %d x %d, k %d): EM %.3f s/iteration -> <= %.1f CPU-min for 5 seeds at %d iterations; k-means "
          "%.3f s/iteration -> <= %.1f CPU-min for 5 seeds at %d; plus the readout functions (minutes); registered ~10 CPU-min"
          % (FIT_N, DIM, K, per_it, per_it * V_MAX_ITER * 5 / 60, V_MAX_ITER, per_km, per_km * K_MAX_ITER * 5 / 60, K_MAX_ITER))
    print("%s dry-run complete: zero measures on real data, nothing written" % TAG)
    return 0


def ensure_meta(state_dir):
    body = json.dumps(dict(test="FLAT-MIX-MMLU", registration="docs/judge_v2_program.md L20672-L20735 (31d092e)", pool=POOL_ID,
                           script=script_pins(), imports={k: v[0] for k, v in IMPORT_PINS.items()}, k=K, seeds=SEEDS, fit_n=FIT_N,
                           dim=DIM, v=[V_MAX_ITER, V_TOL], km=K_MAX_ITER, boot=[BOOT_B, BOOT_SEED],
                           threads={v: os.environ.get(v) for v in THREAD_VARS}), sort_keys=True)
    p = os.path.join(state_dir, "meta.json")
    if os.path.exists(p):
        if open(p, encoding="utf-8").read() != body:
            refuse("state/meta.json differs from this script's meta; a new state directory is needed")
    else:
        write_once(p, body)


def run(state_dir=STATE_DIR, max_chunks=None):
    header()
    before = table_pins()
    for k, v in before.items():
        print("[PIN before] %s %s" % (k, v))
    ensure_meta(state_dir)
    texts, _, _, _ = fit_set()
    X = fit_matrix(texts)
    done = read_state(state_dir)
    n = 0
    for name in PARTITIONS:
        if name in done or (max_chunks is not None and n >= max_chunks):
            continue
        t0 = time.perf_counter()
        body = fit_partition(name, X)
        body["wall_s"] = time.perf_counter() - t0
        write_once(os.path.join(state_dir, "part_%s.json" % name), json.dumps(body, sort_keys=True))
        n += 1
        print("%s partition %s fitted (%.1f s wall%s); no measure is printed by --run"
              % (TAG, name, body["wall_s"], "" if body["wall_s"] <= CHUNK_WALL_S else "; OVER the 4-min chunk budget"))
    print("%s %d partition(s) written; present: %s" % (TAG, n, ",".join(sorted(read_state(state_dir)))))
    check_pins_after(before)
    return 0


def measures(parts, train, heldout, heldout_ids, vec, keyed, veck, names=None, dim=None):
    dim = DIM if dim is None else dim
    Qt, Qh = AF.sliced(vec, [t for t, _ in train], dim), AF.sliced(vec, [t for t, _ in heldout], dim)
    arms = {}
    for name in (PARTITIONS if names is None else names):
        b = parts[name]
        fn = (lambda b_: (lambda Q: cell_ids(b_, partition_assign(b_, Q))))(b)
        sc, hits, kh = m1_block(fn, Qt, Qh, train, heldout)
        m2 = m2_block(fn, keyed, veck)
        m4, per4, m4_void = m4_block(b, Qh)
        arms[name] = dict(m1=sc["acc"], m1_lo=sc["lo"], m1_hi=sc["hi"], hits=sc["hits"], sc=sc, per1=hits, m2=m2["mean"],
                          per2=m2["per_q"], m3=m3_block(kh, heldout, heldout_ids), m4=m4, per4=per4, m4_void=m4_void, cells_h=kh)
        if b["rule"] == "map":
            fn_nm = (lambda b_: (lambda Q: cell_ids(b_, nearest_assign(Q, np.array(b_["mu"])))))(b)
            sc2, _, _ = m1_block(fn_nm, Qt, Qh, train, heldout)
            arms[name]["note"] = " | nearest-mean assignment M1 %.3f (descriptive)" % sc2["acc"]
    return arms


def paired(arms, ref, groups, arm="T", refs=("V0", "K0")):
    """arm minus each reference, per question (the defaults are FLAT-MIX-MMLU's T against V0 and K0)."""
    out = {}
    for a in refs:
        d1 = arms[arm]["per1"] - arms[a]["per1"]
        lo1, hi1 = twin_boot_ci(d1, groups)
        if arms[arm]["per4"] is None or arms[a]["per4"] is None:
            d4, lo4, hi4 = None, None, None
        else:
            d4 = arms[arm]["per4"] - arms[a]["per4"]
            lo4, hi4 = twin_boot_ci(d4, groups)
        common = [q for q in arms[arm]["per2"] if q in arms[a]["per2"]]
        d2 = np.array([arms[arm]["per2"][q] - arms[a]["per2"][q] for q in common])
        lo2, hi2 = F.boot_mean_ci(d2)
        out[a] = dict(d1=float(d1.mean()), d1_lo=lo1, d1_hi=hi1, d2=float(d2.mean()), d2_lo=lo2, d2_hi=hi2,
                      d4=None if d4 is None else float(d4.mean()), d4_lo=lo4, d4_hi=hi4)
    return out


def assemble_res(arms, groups, G, info):
    """analyze()'s assembly of the result render() reads (READY dde660e D5: factored out, unchanged, so FT-ASSEMBLY executes it)."""
    pr = paired(arms, "V0", groups)
    return dict(n_heldout=len(arms["T"]["per1"]), n_groups=G, mbar=kish_mbar(groups), n_keyed=len(arms["T"]["per2"]),
                order=list(PARTITIONS), arms=arms, paired=pr,
                spread_V={m: spread_opt([arms["V%d" % s][m] for s in SEEDS]) for m in ("m1", "m2", "m4")},
                spread_K={m: spread_opt([arms["K%d" % s][m] for s in SEEDS]) for m in ("m1", "m2", "m4")},
                discordance=float(np.mean(arms["T"]["per1"] != arms["V0"]["per1"])),
                identity=dict(m1=fmt_m1(arms["T"]["sc"]), m2="%+.3f" % (1000 * arms["T"]["m2"])),
                info=info)


def analyze(state_dir=STATE_DIR, outcome=OUTCOME, arms_csv=ARMS_CSV):
    header()
    for p in (outcome, arms_csv):
        if os.path.exists(p):
            refuse("%s exists: outcome files of record are WRITE-ONCE" % p)
    before = table_pins()
    for k, v in before.items():
        print("[PIN before] %s %s" % (k, v))
    ensure_meta(state_dir)
    parts = read_state(state_dir)
    require_all(parts)
    if {json.dumps(b["script"], sort_keys=True) for b in parts.values()} != {json.dumps(script_pins(), sort_keys=True)}:
        refuse("partitions were written by another script identity")
    train, heldout, cs = AF.corpus(POOL_ID)
    heldout_ids = sorted(pool_guard.eval_ids(POOL_ID))
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    keyed = F.keyed_questions()
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), DIM)
    arms = measures(parts, train, heldout, heldout_ids, vec, keyed, veck)
    groups, G = twin_groups([t for t, _ in heldout])
    res = assemble_res(arms, groups, G, ["script %s; state %s (%d partitions)" % (fmt_pins(script_pins()), state_dir, len(parts))])
    L, verdict = render(res)
    txt = "\n".join(L) + "\n"
    check_pins_after(before)
    write_once(outcome, txt)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["arm", "M1", "M1_lo", "M1_hi", "hits", "M2_x1000", "M3_R", "M4_nats", "iters", "converged"])
    for a in PARTITIONS:
        m = arms[a]
        w.writerow([a, repr(m["m1"]), repr(m["m1_lo"]), repr(m["m1_hi"]), m["hits"], repr(1000 * m["m2"]),
                    "" if m["m3"] is None else repr(m["m3"]), "VOID" if m["m4"] is None else repr(m["m4"]), parts[a].get("iters", ""),
                    parts[a].get("converged", "")])
    write_once(arms_csv, buf.getvalue())
    print(txt)
    print("%s wrote %s and %s (write-once)" % (TAG, outcome, arms_csv))
    return 0


def identity_check():
    header()
    print("[MODE] --identity-check (the READY's check; real data; writes nothing)")
    tree = load_T("T")
    train, heldout, _ = AF.corpus(POOL_ID)
    vec = AF.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    keyed = F.keyed_questions()
    veck = F.embed_matrix(AF.EMB_DB, list(keyed[3].values()), DIM)
    got = identity(tree, train, heldout, vec, keyed, veck)
    ok = got["m1"] == RECORD_M1 and got["m2"] == RECORD_M2
    print("IDENTITY: T through the flat wrapper: M1 %s (recorded %s), M2 %s (recorded %s) -> %s"
          % (got["m1"], RECORD_M1, got["m2"], RECORD_M2, "REPRODUCED" if ok else "MISMATCH (a READY defect)"))
    return 0 if ok else 1


# ------------------------------------------------------------------------------------------------ selftest
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


def sample_vmf(rng, mu, kappa, n):
    """Wood (1994) sampler on S^{d-1}."""
    d = mu.size
    b = (-2 * kappa + math.sqrt(4 * kappa ** 2 + (d - 1) ** 2)) / (d - 1)
    x0 = (1 - b) / (1 + b)
    c = kappa * x0 + (d - 1) * math.log(1 - x0 ** 2)
    out = np.empty((n, d))
    for i in range(n):
        while True:
            z = rng.beta((d - 1) / 2, (d - 1) / 2)
            w = (1 - (1 + b) * z) / (1 - (1 - b) * z)
            u = rng.uniform()
            if kappa * w + (d - 1) * math.log(1 - x0 * w) - c >= math.log(u):
                break
        v = rng.standard_normal(d)
        v -= (v @ mu) * mu
        v /= np.linalg.norm(v)
        out[i] = w * mu + math.sqrt(max(0.0, 1 - w * w)) * v
    return out


def _synthetic_res(d1=0.0, d1ci=(-0.01, 0.01), d2=0.0, d2ci=(-0.001, 0.001), sv1=0.008, sv2=0.0005, m4v=-1.0, m4t=-2.0,
                   k0m1=0.72, ident=("0.727 [0.712, 0.741]", "+12.785")):
    arms = {}
    for a in PARTITIONS:
        arms[a] = dict(m1=0.72, m1_lo=0.70, m1_hi=0.74, hits=2480, m2=0.012, m3=0.8, m4=-1.5)
    arms["V0"]["m1"], arms["V1"]["m1"] = 0.72, 0.72 + sv1
    arms["V0"]["m2"], arms["V1"]["m2"] = 0.012, 0.012 + sv2
    arms["T"]["m1"], arms["T"]["m2"] = 0.72 + d1, 0.012 + d2
    arms["V0"]["m4"], arms["T"]["m4"] = m4v, m4t
    arms["K0"]["m1"] = k0m1
    sp = dict(m1=sv1, m2=sv2, m4=0.01)
    p = dict(d1=d1, d1_lo=d1ci[0], d1_hi=d1ci[1], d2=d2, d2_lo=d2ci[0], d2_hi=d2ci[1], d4=m4t - m4v, d4_lo=m4t - m4v - 0.1,
             d4_hi=m4t - m4v + 0.1)
    return dict(n_heldout=3445, n_groups=3400, mbar=1.03, n_keyed=10925, order=list(PARTITIONS), arms=arms,
                paired={"V0": p, "K0": dict(p)}, spread_V=sp, spread_K=dict(sp), discordance=0.2,
                identity=dict(m1=ident[0], m2=ident[1]))


def st_branches(chk):
    def txt(**kw):
        L, v = render(_synthetic_res(**kw))
        return "\n".join(L), v
    t, v = txt()
    chk.ok(v["reading"] == "T-1" and "(T-1) the 20NG sentence TRANSFERS" in t and "F1 does not fire" in t, "branch: T-1 (tie), F1 silent")
    chk.ok("C1 PURITY" in t and "-> FAILED" in t.split("C1 PURITY")[1].split("\n")[0], "branch: C1 FAILED")
    chk.ok("P1a" in t and "-> HELD" in t.split("P1a")[1].split("\n")[0] and "-> HELD" in t.split("P1b")[1].split("\n")[0], "branch: P1a/P1b HELD")
    chk.ok("-> HELD" in t.split("P7 ")[1].split("\n")[0] and "-> HELD" in t.split("P8 ")[1].split("\n")[0], "branch: P7 / P8 HELD")
    chk.ok("-> HELD" in t.split("P3 ")[1].split("\n")[0] and "-> HELD" in t.split("P4 ")[1].split("\n")[0] and "-> HELD" in t.split("P5 ")[1].split("\n")[0],
           "branch: P3 / P4 / P5 HELD")
    chk.ok("-> FAILED" in t.split("P6 ")[1].split("\n")[0], "branch: P6 FAILED (no loss)")
    t, v = txt(d1=0.03, d1ci=(0.01, 0.05))
    chk.ok(v["reading"] == "T-3" and "(T-3)" in t and "F1 FIRES (C1 HELD)" in t and "a WIN" in t, "branch: C1 HELD -> T-3, F1 FIRES (win)")
    chk.ok("-> win" in t.split("BESIDE")[1].split("\n")[0], "branch: the K0 comparison prints a win when the same clause holds against K0")
    chk.ok("-> FAILED" in t.split("P1a")[1].split("\n")[0] and "-> FAILED" in t.split("P1b")[1].split("\n")[0] and "-> FAILED" in t.split("P7 ")[1].split("\n")[0],
           "branch: P1a/P1b/P7 FAILED")
    t, v = txt(d1=0.005, d1ci=(0.001, 0.009))
    chk.ok(not v["c1"], "branch: a positive CI but a difference inside the seed spread is C1 FAILED (the spread leg)")
    t, v = txt(d1=0.03, d1ci=(-0.001, 0.05))
    chk.ok(not v["c1"], "branch: a difference above the spread with a CI reaching 0 is C1 FAILED (the CI leg)")
    t, v = txt(d2=0.002, d2ci=(0.0005, 0.0035))
    chk.ok(v["reading"] == "T-2" and "(T-2)" in t and "-> FAILED" in t.split("P2b")[1].split("\n")[0], "branch: C2 HELD alone -> T-2; P2b FAILED")
    chk.ok("-> FAILED" in t.split("P2a")[1].split("\n")[0], "branch: P2a FAILED (+2.0 x1e-3 outside [-1.0, +1.5])")
    t, v = txt(d1=-0.03, d1ci=(-0.05, -0.01))
    chk.ok(v["reading"] == "T-4" and "(T-4)" in t and "L1 LOSS FLAG: FIRES (M1 loss yes, M2 loss no)" in t and "a LOSS" in t,
           "branch: L1 on M1 -> T-4, F1 FIRES (loss)")
    chk.ok("-> HELD" in t.split("P6 ")[1].split("\n")[0], "branch: P6 HELD")
    chk.ok("; loss yes" in t.split("BESIDE")[1].split("\n")[0], "branch: the K0 comparison prints a loss")
    t, v = txt(d1=-0.03, d1ci=(-0.05, 0.002))
    chk.ok(not v["l1"] and "L1 LOSS FLAG: does not fire" in t, "branch: a loss beyond the spread whose CI reaches 0 does not fire L1 (the CI leg)")
    t, v = txt(d1=-0.005, d1ci=(-0.009, -0.001))
    chk.ok(not v["l1"], "branch: a negative CI inside the seed spread does not fire L1 (the spread leg)")
    t, v = txt(d2=-0.002, d2ci=(-0.0035, -0.0005))
    chk.ok(v["reading"] == "T-4" and "M2 loss yes" in t, "branch: L1 on M2 -> T-4")
    t, v = txt(d1=-0.03, d1ci=(-0.05, -0.01), d2=0.002, d2ci=(0.0005, 0.0035))
    chk.ok(v["reading"] == "T-5" and "(T-5) a mixed pattern" in t and "a mixed pattern" in t.split("FALSIFIER")[1], "branch: C2 HELD with L1 on M1 -> T-5")
    t, v = txt(d1=0.03, d1ci=(0.01, 0.05), d2=-0.002, d2ci=(-0.0035, -0.0005))
    chk.ok(v["reading"] == "T-5" and v["joined"] and "recorded JOINED as \"C1 HELD / L1 FIRED on M2\"" in t and "(T-5) a mixed pattern" in t
           and "AMBIGUOUS" not in t and "(T-3)" not in t, "branch: C1 HELD with L1 on M2 -> (T-5), recorded joined, no sentence (ruling B5)")
    chk.ok("FALSIFIER F1 FIRES (C1 HELD, L1 FIRED)" in t and "-> FAILED" in t.split("  P7 the reading")[1].split("\n")[0],
           "branch: ruling B5 case: F1 fires on both triggers; P7 FAILED")
    t, v = txt(sv1=0.001)
    chk.ok("-> FAILED" in t.split("P3 ")[1].split("\n")[0] and "bound by the MDE" in t.split("C1 PURITY")[1].split("\n")[0], "branch: P3 FAILED; threshold bound by the MDE")
    t, v = txt(sv1=0.03)
    chk.ok("bound by the seed spread" in t.split("C1 PURITY")[1].split("\n")[0], "branch: threshold bound by the seed spread")
    t, v = txt(m4v=-2.0, m4t=-1.0)
    chk.ok("-> FAILED" in t.split("P4 ")[1].split("\n")[0] and "a T ADVANTAGE" in t, "branch: P4 FAILED; a T advantage on M4 noted, not scored")
    t, v = txt(k0m1=0.75)
    chk.ok("-> FAILED" in t.split("P5 ")[1].split("\n")[0], "branch: P5 FAILED")
    t, v = txt(ident=("0.726 [0.711, 0.740]", "+12.785"))
    chk.ok("-> FAILED" in t.split("P8 ")[1].split("\n")[0], "branch: P8 FAILED on an identity mismatch")
    t, v = txt()
    chk.ok("K0" in t and "BESIDE" in t and "no win" in t.split("BESIDE")[1].split("\n")[0], "branch: the K0 comparison is printed, never deciding")


def selftest(only=None, quiet=False, heavy=True):
    chk = _Checks(quiet)
    sel = (lambda name: only is None or name in only)
    if sel("FT-THREADS"):
        chk.ok(all(os.environ.get(v) == "1" for v in THREAD_VARS), "FT-THREADS the three thread variables are 1")
    if sel("FT-LOGC"):
        for kap in (0.5, 3.0, 40.0, 300.0):
            ref = math.log(kap / (4 * math.pi * math.sinh(kap))) if kap < 300 else math.log(kap / (2 * math.pi)) - kap
            chk.ok(abs(float(log_cd(3, kap)) - ref) < 1e-9 * max(1.0, abs(ref)), "FT-LOGC log C_3(%g) equals log(kappa / (4 pi sinh kappa))" % kap)
        from scipy.special import ive
        for x in (50.0, 200.0, 1000.0):
            v = 127.0
            lhs, rhs = ive(v - 1, x) - ive(v + 1, x), (2 * v / x) * ive(v, x)
            chk.ok(abs(lhs - rhs) < 1e-10 * abs(rhs), "FT-LOGC Bessel recurrence I_{v-1} - I_{v+1} = (2v/x) I_v at d = 256, x = %g" % x)
        chk.ok(isinstance(_raised(lambda: log_cd(256, 1e-3)), Degenerate), "FT-LOGC an underflowing ive is Degenerate")
    if sel("FT-VMF") and heavy:
        from sklearn.metrics import adjusted_rand_score
        rng = np.random.default_rng(32)
        d, k = 32, 5
        mus = unit_rows(rng.standard_normal((k, d)))
        kaps = np.array([40.0, 60.0, 80.0, 50.0, 70.0])
        X = np.vstack([sample_vmf(rng, mus[j], kaps[j], 300) for j in range(k)])
        y = np.repeat(np.arange(k), 300)
        r = vmf_em(X, k, 0)
        lab = map_assign(X, r["mu"], r["kappa"], r["pi"])
        ari = adjusted_rand_score(y, lab)
        chk.ok(ari >= 0.9, "FT-VMF V recovers a known vMF mixture (d 32, k 5): ARI %.3f >= 0.9" % ari)
        match = [int(np.argmax(r["mu"] @ mus[j])) for j in range(k)]
        rel = [abs(r["kappa"][match[j]] / kaps[j] - 1) for j in range(k)]
        chk.ok(len(set(match)) == k and max(rel) <= 0.20, "FT-VMF every kappa within 20%% (max rel. error %.3f)" % max(rel))
        km = spherical_kmeans(X, k, 0)
        chk.ok(adjusted_rand_score(y, km["labels"]) >= 0.9 and km["converged"], "FT-KM spherical k-means recovers the partition (ARI >= 0.9)")
    if sel("FT-KMPP"):
        rng = np.random.default_rng(5)
        centers = unit_rows(np.eye(8)[:5] * 1.0)
        X = unit_rows(np.vstack([centers[j] + 0.01 * rng.standard_normal((200, 8)) for j in range(5)]))
        distinct = 0
        for s in range(20):
            C = kmeanspp(X, 5, np.random.default_rng(s))
            distinct += int(len(set(np.argmax(C @ centers.T, axis=1))) == 5)
        chk.ok(distinct >= 19, "FT-KMPP k-means++ D^2 seeding hits all 5 well-separated clusters in %d of 20 seeds (>= 19)" % distinct)
    if sel("FT-MAP"):
        mu = np.array([[1.0, 0.0], [0.0, 1.0]])
        kap = np.array([1.0, 200.0])
        pi = np.array([0.5, 0.5])
        x = unit_rows(np.array([[0.6, 0.8]]))
        lp = [math.log(pi[j]) + float(log_cd(2, kap[j])) + kap[j] * float(mu[j] @ x[0]) for j in range(2)]
        chk.ok(int(map_assign(x, mu, kap, pi)[0]) == int(np.argmax(lp)) == 0 and int(nearest_assign(x, mu)[0]) == 1,
               "FT-MAP the MAP assignment is argmax(log pi + log C + kappa mu.x) and differs from nearest-mean here")
        chk.ok(abs(float(heldout_ll(x, mu, kap, pi)[0]) - float(np.log(np.sum(np.exp(lp))))) < 1e-12, "FT-M4 held-out ll = log sum_k pi_k C(kappa_k) exp(kappa_k mu_k.x)")
    if sel("FT-WRAP"):
        rng = np.random.default_rng(8)
        cats = ["a", "b", "c"]
        C = unit_rows(rng.standard_normal((4, 16)))
        tr_lab, ho_lab = rng.integers(0, 4, 300), rng.integers(0, 4, 120)
        Qt = unit_rows(C[tr_lab] + 0.05 * rng.standard_normal((300, 16)))
        Qh = unit_rows(C[ho_lab] + 0.05 * rng.standard_normal((120, 16)))
        train = [("t%d" % i, cats[(tr_lab[i] + (i % 7 == 0)) % 3]) for i in range(300)]
        heldout = [("h%d" % i, cats[(ho_lab[i] + (i % 5 == 0)) % 3]) for i in range(120)]
        body = dict(rule="nearest", centers=C.tolist(), mu=C.tolist(), partition="K9")
        fn = lambda Q: cell_ids(body, partition_assign(body, Q))
        sc, hits, kh = m1_block(fn, Qt, Qh, train, heldout)
        at, ah = np.argmax(Qt @ C.T, axis=1), np.argmax(Qh @ C.T, axis=1)
        maj = {}
        for j in range(4):
            labs = [train[i][1] for i in range(300) if at[i] == j]
            if labs:
                maj[j] = max(sorted(set(labs)), key=labs.count)
        direct = sum(1 for i in range(120) if maj.get(ah[i]) == heldout[i][1]) / 120
        chk.ok(abs(sc["acc"] - direct) < 1e-12 and hits.mean() == sc["acc"], "FT-WRAP the wrapper's M1 (anchor_free_readout.score_cells) equals a direct majority-label computation")
        tree = dict(leaf_ids=["L%d" % j for j in range(4)], leaf_mu=C, leaf_d1=["D0", "D0", "D1", "D1"], d1_ids=["D0", "D1"],
                    d1_mu=unit_rows(np.vstack([C[:2].sum(0), C[2:].sum(0)])), dim=16)
        vec = {t: q for (t, _), q in zip(train + heldout, np.vstack([Qt, Qh]))}
        pur = AF.purity(tree, train, heldout, vec)["leaf"]
        flat = dict(rule="nearest", centers=C.tolist(), mu=C.tolist(), partition="F", leaf_ids=tree["leaf_ids"])
        sc2, _, _ = m1_block(lambda Q: cell_ids(flat, partition_assign(flat, Q)), Qt, Qh, train, heldout)
        chk.ok(pur["acc"] == sc2["acc"] and pur["hits"] == sc2["hits"], "FT-FLATTREE a tree's leaves through anchor_free_readout.purity equal the same centroids as a flat arm through the wrapper")
        models = ["m1", "m2"]
        qs = ["q%d" % i for i in range(40)]
        G = {m: {q: int((i * (3 + j)) % 4 == 0) for i, q in enumerate(qs)} for j, m in enumerate(models)}
        part = {q: "c%d" % (i % 3) for i, q in enumerate(qs)}
        il = F.loo_imp(part, qs, models, G)
        man = np.zeros(len(qs))
        for m in models:
            for j, q in enumerate(qs):
                others = [G[m][r] for r in qs if r != q]
                cell = [G[m][r] for r in qs if r != q and part[r] == part[q]]
                man[j] += ((sum(others) / len(others)) - G[m][q]) ** 2 - ((sum(cell) / len(cell)) - G[m][q]) ** 2
        chk.ok(np.allclose(il, man / len(models), atol=1e-12), "FT-WRAP free_tests_f4_f7.loo_imp equals a direct LOO Brier improvement")
        keyed = (models, G, {q: "x" for q in qs}, {q: q for q in qs}, qs)
        veck = {q: unit_rows(rng.standard_normal((1, 16)))[0] for q in qs}
        m2 = m2_block(lambda Q: ["c%d" % i for i in nearest_assign(Q, C[:3])], keyed, veck)
        partq = {q: "c%d" % int(np.argmax(C[:3] @ veck[q])) for q in qs}
        chk.ok(abs(m2["mean"] - float(F.loo_imp(partq, qs, models, G).mean())) < 1e-15, "FT-WRAP the M2 wrapper follows f6_block's path (embed -> nearest cell -> loo_imp)")
    if sel("FT-BOOT"):
        groups = np.array([0] * 5 + [1] * 3 + list(range(2, 12)))
        rng = np.random.default_rng(1)
        whole = True
        for _ in range(50):
            idx = twin_boot_indices(groups, rng)
            cnt = np.bincount(groups[idx], minlength=12)
            size = np.bincount(groups, minlength=12)
            whole &= bool(np.all(cnt % size == 0))
        chk.ok(whole, "FT-BOOT every twin-group resample contains whole groups only")
        diff = np.array([1.0] * 5 + [0.0] * 3 + [0.0] * 10)
        lo, hi = twin_boot_ci(diff, groups, B=2000, seed=3)
        rng2 = np.random.default_rng(3)
        bs = sorted(float(diff[twin_boot_indices(groups, rng2)].mean()) for _ in range(2000))
        chk.ok(lo == bs[50] and hi == bs[1949], "FT-BOOT the CI is the 2.5 / 97.5 percentile of the whole-group resamples")
        lo_q, hi_q = np.percentile([float(diff[np.random.default_rng(k).integers(0, 18, 18)].mean()) for k in range(2000)], [2.5, 97.5])
        chk.ok(hi - lo > hi_q - lo_q, "FT-BOOT five identical twins widen the CI over question-level resampling")
        g2, G2 = twin_groups(["What is x?", "what  is X?", "Other"])
        chk.ok(G2 == 2 and g2[0] == g2[1] != g2[2], "FT-BOOT stem_key twins (norm-v1: case, whitespace) share a group")
        chk.ok(abs(kish_mbar(np.array([0, 0, 1])) - 5 / 3) < 1e-12, "FT-BOOT Kish mean group size = sum n^2 / sum n")
    if sel("FT-FIT"):
        chk.ok(expect_refusal(lambda: assert_fit_count(8124), "8124 texts"), "FT-FIT a fit set of 8,124 REFUSES")
        chk.ok(expect_refusal(lambda: assert_fit_count(8126), "8126 texts"), "FT-FIT a fit set of 8,126 REFUSES")
        assert_fit_count(8125)
        chk.ok(True, "FT-FIT a fit set of 8,125 passes")
        chk.ok(expect_refusal(lambda: require_all({p: {} for p in PARTITIONS if p != "V3"}), "V3"), "FT-FIT the analysis REFUSES without V3")
        chk.ok(isinstance(_raised(lambda: banerjee_kappa(np.array([1.0]), 256)), Degenerate), "FT-FIT a one-member cell (rbar = 1) is Degenerate")
        chk.ok(spread([0.70, 0.72, 0.71]) == 0.72 - 0.70, "FT-FIT spread = max - min")
    if sel("FT-PIN"):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.py")
            with open(p, "wb") as f:
                f.write(b"a = 1\r\n")
            good = pins_of_bytes(b"a = 1\n")
            chk.ok(verify_pin(p, good["blob"], good["lf16"])["crlf16"] == good["crlf16"], "FT-PIN a CRLF file verifies against its LF pins")
            chk.ok(expect_refusal(lambda: verify_pin(p, "0" * 40, good["lf16"]), "pin mismatch"), "FT-PIN a pin mismatch REFUSES")
            q = os.path.join(td, "o.txt")
            write_once(q, "a")
            try:
                write_once(q, "b")
                second = False
            except FileExistsError:
                second = True
            chk.ok(second, "FT-WO a second write of an outcome file REFUSES")
    if sel("FT-GUARD"):
        with tempfile.TemporaryDirectory() as td:
            dbp = os.path.join(td, "embeddings_cache.db")
            c = _RAW_CONNECT(dbp)
            c.execute("CREATE TABLE t (a)")
            c.commit()
            c.close()
            con = sqlite3.connect("file:%s?mode=ro" % dbp.replace(os.sep, "/"), uri=True)
            n_rows = con.execute("SELECT COUNT(*) FROM t").fetchone()[0]
            con.close()
            chk.ok(n_rows == 0 and "immutable=1" in _admit("file:%s?mode=ro" % dbp.replace(os.sep, "/"), True),
                   "FT-GUARD a mode=ro open is upgraded to mode=ro&immutable=1")
            chk.ok(expect_refusal(lambda: sqlite3.connect("file:%s?mode=rw" % dbp.replace("\\", "/"), uri=True), "only mode=ro"),
                   "FT-GUARD a writable open REFUSES")
            chk.ok(expect_refusal(lambda: sqlite3.connect(dbp), "not a file: URI"), "FT-GUARD a plain path REFUSES")
            with open(dbp + "-wal", "wb") as f:
                f.write(b"x")
            chk.ok(expect_refusal(lambda: sqlite3.connect("file:%s?mode=ro" % dbp.replace("\\", "/"), uri=True), "non-empty"),
                   "FT-GUARD a non-empty -wal REFUSES")
            other = os.path.join(td, "ratings.db")
            chk.ok(expect_refusal(lambda: sqlite3.connect("file:%s?mode=ro" % other.replace("\\", "/"), uri=True), "not a DB this test reads"),
                   "FT-GUARD a DB outside the four this test reads REFUSES")
    if sel("FT-BRANCH"):
        st_branches(chk)
    if sel("FT-M4VOID"):
        st_m4void(chk)
    if sel("FT-EMBGUARD"):
        st_embguard(chk)
    if sel("FT-ASSEMBLY"):
        st_assembly(chk)
    return chk.n


def _raised(fn):
    try:
        fn()
    except BaseException as e:                   # noqa: B902
        return e
    return None


def _synthetic_arms(rng, n=400, t_m1_gain=0.10, t_m4_void=False, nq=60):
    """Per-question arms for FT-ASSEMBLY: T wins M1 by about t_m1_gain against every V and K seed; M2 per-question dicts."""
    base = (rng.uniform(size=n) < 0.70).astype(float)
    qs = ["q%03d" % i for i in range(nq)]
    arms = {}
    for j, a in enumerate(PARTITIONS):
        per1 = base.copy()
        flip = rng.uniform(size=n) < 0.02 * (j % 3)
        per1[flip] = 1.0 - per1[flip]
        if a == "T":
            up = (per1 == 0) & (rng.uniform(size=n) < t_m1_gain / 0.3)
            per1[up] = 1.0
        per2 = {q: 0.010 + 0.001 * math.sin(i + j) for i, q in enumerate(qs)}
        per4 = -1.0 - 0.01 * j + 0.001 * rng.standard_normal(n)
        m4void = (a == "T" and t_m4_void)
        m1 = float(per1.mean())
        arms[a] = dict(m1=m1, m1_lo=m1 - 0.02, m1_hi=m1 + 0.02, hits=int(per1.sum()), per1=per1, m2=float(np.mean(list(per2.values()))),
                       per2=per2, m3=0.8, m4=None if m4void else float(per4.mean()), per4=None if m4void else per4,
                       m4_void="M4 VOID (ruling O2): synthetic" if m4void else None,
                       sc=dict(acc=m1, lo=m1 - 0.02, hi=m1 + 0.02))
    return arms


def st_assembly(chk):
    """READY dde660e D5: paired() and analyze()'s assembly (assemble_res) EXECUTED, then render(): T's M4 VOID with C1 HELD
    (the reviewer's mutants R3, R3b, R3d must die), and the regular case where d4 is the mean per-question difference."""
    rng = np.random.default_rng(55)
    arms = _synthetic_arms(rng, t_m4_void=True)
    groups = np.arange(len(arms["T"]["per1"]))
    res = assemble_res(arms, groups, len(groups), ["synthetic"])
    p = res["paired"]["V0"]
    chk.ok(p["d4"] is None and p["d4_lo"] is None and abs(p["d1"] - float((arms["T"]["per1"] - arms["V0"]["per1"]).mean())) < 1e-15,
           "FT-ASSEMBLY paired(): T's M4 VOID leaves d4 None and d1 intact (R3b)")
    chk.ok(res["spread_V"]["m1"] is not None and res["spread_V"]["m2"] is not None and res["spread_V"]["m4"] is not None,
           "FT-ASSEMBLY spread_V over M1 / M2 / M4 is computed from the V seeds only, whatever T's M4 (R3d)")
    L, v = render(res)
    t = "\n".join(L)
    chk.ok(v["c1"] and v["reading"] == "T-3" and "-> HELD" in t.split("C1 PURITY")[1].split("\n")[0],
           "FT-ASSEMBLY C1 HELD with T's M4 VOID: reading T-3 (R3: an M4 VOID never forces C1 FAILED)")
    chk.ok("P4 M4: V0 above T (p 0.85): UNSCOREABLE" in t and "T - V0 not computed" in t and "M4 VOID (ruling O2): synthetic" in t,
           "FT-ASSEMBLY render: P4 UNSCOREABLE, T's M4 VOID printed")
    arms = _synthetic_arms(np.random.default_rng(56))
    res = assemble_res(arms, groups, len(groups), ["synthetic"])
    p = res["paired"]["V0"]
    chk.ok(abs(p["d4"] - float((arms["T"]["per4"] - arms["V0"]["per4"]).mean())) < 1e-15 and p["d4_lo"] <= p["d4"] <= p["d4_hi"],
           "FT-ASSEMBLY regular case: d4 is the mean per-question M4 difference, inside its twin-group CI")
    chk.ok(res["n_heldout"] == len(groups) and res["n_keyed"] == 60 and res["identity"]["m1"] == fmt_m1(arms["T"]["sc"])
           and abs(res["discordance"] - float(np.mean(arms["T"]["per1"] != arms["V0"]["per1"]))) < 1e-15,
           "FT-ASSEMBLY denominators, identity and discordance as analyze() assembled them")


def st_m4void(chk):
    """Ruling O2 (a degenerate M4 refit of T, K or O VOIDs M4 only) and ruling B6 (a degenerate V seed refuses)."""
    rng = np.random.default_rng(12)
    X = unit_rows(rng.standard_normal((40, 8)))
    lab = np.array([0] * 20 + [1] * 19 + [2])            # cell 2 has ONE member: rbar = 1
    r = m4_refit(X, lab, 3)
    chk.ok(r["mu"] is None and "M4 VOID (ruling O2)" in r["m4_void"], "FT-M4VOID a one-member cell in the M4 refit VOIDs M4 (no refusal)")
    r = m4_refit(X, np.array([0] * 20 + [1] * 20), 2)
    chk.ok(r["m4_void"] is None and len(r["mu"]) == 2, "FT-M4VOID a regular refit gives the M4 mixture")
    body = dict(rule="nearest", partition="K0", centers=X[:3].tolist(), mu=None, kappa=None, pi=None, m4_void="M4 VOID (ruling O2): x")
    chk.ok(m4_block(body, X) == (None, None, "M4 VOID (ruling O2): x"), "FT-M4VOID m4_block carries the VOID")
    tb = dict(rule="flatLeaf", partition="T", mu=[[1.0] + [0.0] * 255], kappa=[1e-3], pi=[1.0], m4_void=None)
    Q = unit_rows(np.random.default_rng(3).standard_normal((5, 256)))
    m4, per4, why = m4_block(tb, Q)
    chk.ok(m4 is None and "ruling O2" in why, "FT-M4VOID an underflowing ive in T's refit VOIDs M4 for T only")
    vb = dict(tb, rule="map", partition="V0")
    chk.ok(expect_refusal(lambda: m4_block(vb, Q), "ruling B6"), "FT-M4VOID the same degeneracy in a V seed REFUSES citing ruling B6")
    Xd = np.repeat(unit_rows(np.random.default_rng(4).standard_normal((3, 8))), 10, axis=0)
    chk.ok(expect_refusal(lambda: vmf_em(Xd, 3, 0), "ruling B6"), "FT-M4VOID a degenerate V fit (cells of identical points) REFUSES citing B6")
    res = _synthetic_res()
    res["arms"]["T"]["m4"] = None
    res["arms"]["T"]["m4_void"] = "M4 VOID (ruling O2): synthetic"
    res["paired"]["V0"].update(d4=None, d4_lo=None, d4_hi=None)
    L, v = render(res)
    t = "\n".join(L)
    chk.ok("M4 VOID (ruling O2): synthetic [C1 / C2 unaffected]" in t and "P4 M4: V0 above T (p 0.85): UNSCOREABLE" in t
           and "T - V0 not computed" in t, "FT-M4VOID render: T's M4 VOID printed; P4 UNSCOREABLE")
    chk.ok("C1 PURITY" in t and "-> FAILED" in t.split("C1 PURITY")[1].split("\n")[0] and v["reading"] == "T-1",
           "FT-M4VOID C1, C2, L1 and the reading are scored as usual with M4 VOID")
    chk.ok(spread_opt([1.0, None]) is None and spread_opt([1.0, 3.0]) == 2.0, "FT-M4VOID spread over seeds is NA when any M4 is VOID")


embedding_guard_flat_ref = embedding_guard_flat
_EMB_GLOBALS = ("EMB_DB_NAME", "EMB_MODEL_EXPLICIT", "EMB_CACHE_SET", "PIN_TABLES", "ALLOWED_DB_BASENAMES", "ARM_COPY_ADMITTED")


def st_embguard(chk):
    """EMBEDDER-PLUMBING: the FLAT wiring EXECUTED on synthetic caches (embedder_guard.synthetic); every global restored."""
    g = globals()
    saved = {k: g[k] for k in _EMB_GLOBALS}
    saved_af, saved_f, saved_pool = AF.EMB_DB, F.EMB_DB, pool_guard.assert_pool_of_record

    def restore():
        g.update(saved)
        AF.EMB_DB, F.EMB_DB = saved_af, saved_f

    rng = np.random.default_rng(27)
    vec, byid, ids = EG.synthetic(rng)
    graph = dict(byid=byid, root="n1", sha="synthetic")
    try:
        with tempfile.TemporaryDirectory() as td:
            right = EG._make_cache(os.path.join(td, "embeddings_cache.db"), vec)
            wrong = EG._make_cache(os.path.join(td, "embeddings_cache_nomic-embed-text_latest.db"),
                                   {q: rng.standard_normal(768) for q in ids})
            mq, m0 = os.path.join(td, "run_manifest.json"), os.path.join(td, "run_manifest_nomodel.json")
            with open(mq, "w", encoding="utf-8") as f:
                json.dump({"embedding_model": "qwen3-embedding:latest"}, f)
            with open(m0, "w", encoding="utf-8") as f:
                json.dump({"seed": 42}, f)
            chk.ok(EMB_DB_NAME == "embeddings_cache.db" and not EMB_CACHE_SET and EMB_MODEL_EXPLICIT is None
                   and PIN_TABLES[0][0] == "embeddings_cache.db", "FT-EMBGUARD unconfigured: the DB of record, no explicit model")
            configure_embedding(cache_file=right)
            chk.ok(AF.EMB_DB == F.EMB_DB == os.path.abspath(right) == g["EMB_DB_NAME"] and g["PIN_TABLES"][0][0] == os.path.abspath(right)
                   and all(t[0] != "embeddings_cache.db" for t in g["PIN_TABLES"]),
                   "FT-EMBGUARD configure_embedding redirects the fit set, AF, F and the pins")
            r = embedding_guard_flat(graph=graph, manifest_path=mq, dim=256)
            chk.ok(r["admitted"] and r["min_cos"] >= 0.99, "FT-EMBGUARD the right cache is ADMITTED for a qwen3 tree (min cos %.4f)" % r["min_cos"])
            restore()
            configure_embedding(cache_file=wrong)
            chk.ok(expect_refusal(lambda: embedding_guard_flat(graph=graph, manifest_path=mq, dim=256), "< budget 0.99")
                   and expect_refusal(lambda: embedding_guard_flat(graph=graph, manifest_path=mq, dim=256), "!= {4096}"),
                   "FT-EMBGUARD P-2 (vi) analogue: the nomic-like cache is REFUSED for the qwen3 tree (cosine and dimension)")
            restore()
            configure_embedding(model="nomic-embed-text:latest")
            chk.ok(expect_refusal(lambda: embedding_guard_flat(graph=graph, manifest_path=mq, dim=256), "contradicts"),
                   "FT-EMBGUARD an explicit model contradicting the tree's manifest REFUSES")
            restore()
            chk.ok(expect_refusal(lambda: embedding_guard_flat(graph=graph, manifest_path=m0, dim=256), "no embedding_model"),
                   "FT-EMBGUARD a manifest without embedding_model and no --embedding-model REFUSES")
            chk.ok(expect_refusal(lambda: embedding_guard_flat(graph=graph, manifest_path=os.path.join(td, "absent.json"), dim=256),
                                  "no embedding_model"), "FT-EMBGUARD a missing run manifest and no --embedding-model REFUSES")
            configure_embedding(cache_file=right, model="qwen3-embedding:latest")
            chk.ok(embedding_guard_flat(graph=graph, manifest_path=m0, dim=256)["admitted"] is True,
                   "FT-EMBGUARD --embedding-model names the model when the manifest does not")
            restore()
            chk.ok(expect_refusal(lambda: configure_embedding(cache_file=os.path.join(td, "absent.db")), "does not exist"),
                   "FT-EMBGUARD a missing --embedding-cache-file REFUSES")
            restore()
            # C-ET-3 (READY_emb_target 6202766): an EMBEDDER-CROSS-FLAT arm file is refused on this route in all three forms
            card = EG._make_cache(os.path.join(td, "embeddings_cache_embeddinggemma_latest__card.db"), {})
            os.makedirs(os.path.join(td, "xdir"))
            provd = EG._make_cache(os.path.join(td, "xdir", "embeddings_cache_embeddinggemma_latest.db"), {})
            with open(provd + ".provenance.json", "w", encoding="utf-8") as f:
                f.write("{}")
            os.makedirs(os.path.join(td, "experiment_results", "embedder_cross"))
            inx = EG._make_cache(os.path.join(td, "experiment_results", "embedder_cross", "any_name.db"), {})
            saved_root_x = g["DATA_ROOT"]
            try:
                g["DATA_ROOT"] = td
                for pth, what in ((card, "a card file"), (provd, "a file with a provenance beside it"), (inx, "a file under DATA_ROOT/" + EMB_CROSS_DIR)):
                    chk.ok(expect_refusal(lambda: configure_embedding(cache_file=pth, model="embeddinggemma:latest"),
                                          "is an EMBEDDER-CROSS-FLAT arm file") and g["EMB_DB_NAME"] == saved["EMB_DB_NAME"]
                           and os.path.basename(pth) not in g["ALLOWED_DB_BASENAMES"],
                           "FT-EMBGUARD C-ET-3 %s REFUSED by configure_embedding (nothing configured, nothing admitted)" % what)
                    restore()
                saved_apr = pool_guard.assert_pool_of_record
                pool_guard.assert_pool_of_record = lambda *a, **k: refuse("selftest: the pool is not read")   # a mutant reads nothing real
                try:
                    chk.ok(expect_refusal(lambda: main(["--dry-run", "--embedding-cache-file", provd, "--embedding-model", "embeddinggemma:latest"]),
                                          "is an EMBEDDER-CROSS-FLAT arm file"), "FT-EMBGUARD C-ET-3 main --dry-run --embedding-cache-file <DIR copy> REFUSES")
                finally:
                    pool_guard.assert_pool_of_record = saved_apr
                restore()
                g["ARM_COPY_ADMITTED"] = provd
                configure_embedding(cache_file=provd, model="embeddinggemma:latest")
                chk.ok(g["EMB_DB_NAME"] == os.path.abspath(provd) and AF.EMB_DB == os.path.abspath(provd),
                       "FT-EMBGUARD C-ET-3 the one path embedder_arms names (ARM_COPY_ADMITTED) is configured")
                restore()
                chk.ok(not is_arm_copy(right) and not is_arm_copy(wrong), "FT-EMBGUARD C-ET-3 ordinary cache files are not arm copies (inert)")
            finally:
                g["DATA_ROOT"] = saved_root_x
                restore()
            chk.ok(expect_refusal(lambda: configure_embedding(model=" "), "blank"), "FT-EMBGUARD a blank --embedding-model REFUSES")
            restore()
            for argv in (["--run", "--embedding-model", "qwen3-embedding:latest"], ["--analyze", "--embedding-cache-file", right]):
                chk.ok(expect_refusal(lambda: main(argv), "--dry-run and --identity-check only"),
                       "FT-EMBGUARD %s with an embedding flag REFUSES" % argv[0])
            restore()
            # READY_w0_rp08 F1 / F3: a two-site tree and fit_set, through the CONFIGURED cache, with an empty decoy at the
            # DB-of-record name under DATA_ROOT (a reader of the wrong name reads nothing and fails).
            vec2, byid2, ids2 = EG.synthetic_two_site(np.random.default_rng(28))
            graph2 = dict(byid=byid2, root="n1", sha="synthetic2")
            droot = os.path.join(td, "decoy_root")
            os.makedirs(droot)
            EG._make_cache(os.path.join(droot, "embeddings_cache.db"), {})
            right2 = EG._make_cache(os.path.join(td, "two_site_right.db"), vec2)
            saved_root, saved_lsg, saved_afc = g["DATA_ROOT"], g["load_snapshot_graph"], g["assert_fit_count"]
            try:
                g["DATA_ROOT"] = droot
                configure_embedding(cache_file=right2)
                chk.ok(bool(g["EMB_CACHE_SET"]) and g["EMB_DB_NAME"] == os.path.abspath(right2),
                       "FT-EMBGUARD configure_embedding records the explicit cache (EMB_CACHE_SET true, EMB_DB_NAME the file)")
                r2 = embedding_guard_flat(graph=graph2, manifest_path=mq, dim=256)
                chk.ok(bool(r2["admitted"]) and [(x["id"], x["n"], x["found"]) for x in r2["rows"]] == [("n1", 120, 120), ("n3", 60, 60)],
                       "FT-EMBGUARD two-site tree ADMITTED through the configured cache, each site on its OWN region (120/120, 60/60)")
                g["load_snapshot_graph"] = lambda sid: graph2
                g["assert_fit_count"] = lambda n, fit_n=None: None
                texts2, _g2, fids, _t2 = fit_set()
                chk.ok(len(fids) == 120 and texts2 == sorted("text " + q for q in ids2),
                       "FT-EMBGUARD fit_set() reads the CONFIGURED cache (120 texts, not the decoy at the DB-of-record name)")
            finally:
                g["DATA_ROOT"], g["load_snapshot_graph"], g["assert_fit_count"] = saved_root, saved_lsg, saved_afc
            restore()
            calls = []
            pool_guard.assert_pool_of_record = lambda pid: calls.append("pool") or pid
            g["embedding_guard_flat"] = lambda *a, **k: calls.append("guard")
            try:
                header()
            finally:
                pool_guard.assert_pool_of_record = saved_pool
                g["embedding_guard_flat"] = embedding_guard_flat_ref
            chk.ok(calls == ["pool", "guard"], "FT-EMBGUARD header() runs the embedding guard after the pool line (%s)" % calls)
    finally:
        restore()
        pool_guard.assert_pool_of_record = saved_pool


MUTANTS = (
    ("fit-set count check removed", "    if n != fit_n:\n", "    if False:\n", ("FT-FIT",)),
    ("partition completeness removed", "    if missing:\n        refuse(\"partitions missing", "    if False:\n        refuse(\"partitions missing", ("FT-FIT",)),
    ("spread as a half-range", "return float(max(vals) - min(vals))", "return float(max(vals) - min(vals)) / 2", ("FT-FIT",)),
    ("rbar = 1 admitted", "if np.any(rbar >= 1.0) or np.any(rbar <= 0.0):", "if np.any(rbar > 1.0) or np.any(rbar <= 0.0):", ("FT-FIT",)),
    ("log C_d exponent d/2", "    return v * np.log(kappa) - (d / 2.0) * math.log(2 * math.pi) - (np.log(iv) + kappa)",
     "    return (d / 2.0) * np.log(kappa) - (d / 2.0) * math.log(2 * math.pi) - (np.log(iv) + kappa)", ("FT-LOGC",)),
    ("ive underflow admitted", "if not np.all(np.isfinite(iv)) or np.any(iv <= 0):", "if not np.all(np.isfinite(iv)):", ("FT-LOGC",)),
    ("Banerjee without the d term", "return rbar * (d - rbar ** 2) / (1.0 - rbar ** 2)", "return rbar * (2 - rbar ** 2) / (1.0 - rbar ** 2)", ("FT-VMF",)),
    ("MAP ignores the mixing weights", "out[:, live] = np.log(pi[live]) + log_cd(d, kappa[live]) + (X @ mu[live].T) * kappa[live]",
     "out[:, live] = log_cd(d, kappa[live]) + (X @ mu[live].T) * kappa[live]", ("FT-MAP",)),
    ("k-means++ uniform seeding", "j = int(rng.choice(n, p=d2 / s)) if s > 0 else int(rng.integers(n))", "j = int(rng.integers(n))", ("FT-KMPP",)),
    ("bootstrap over questions, not groups", "    draw = rng.integers(0, G, size=G)\n    return np.concatenate",
     "    return rng.integers(0, len(groups), size=len(groups))\n    return np.concatenate", ("FT-BOOT",)),
    ("CI from the extreme resamples", "    return bs[int(0.025 * B)], bs[int(0.975 * B) - 1]\n\n\ndef kish",
     "    return bs[0], bs[-1]\n\n\ndef kish", ("FT-BOOT",)),
    ("groups by raw text", "    keys = [split_side.stem_key(t) for t in texts]", "    keys = list(texts)", ("FT-BOOT",)),
    ("wrapper M1 routes held-out by train cells", "    kt, kh = assign_fn(Qt), assign_fn(Qh)", "    kt, kh = assign_fn(Qt), assign_fn(Qt)[:len(heldout)]", ("FT-WRAP",)),
    ("wrapper M2 passes a fit set", "    il = F.loo_imp(part, qs, models, G)\n    return dict(n=len(qs)", "    il = F.loo_imp(part, qs, models, G, fit=qs[:-5])\n    return dict(n=len(qs)", ("FT-WRAP",)),
    ("criterion without the CI leg", "    return bool(diff > spr and lo > 0)", "    return bool(diff > spr)", ("FT-BRANCH",)),
    ("criterion without the spread leg", "    return bool(diff > spr and lo > 0)", "    return bool(lo > 0)", ("FT-BRANCH",)),
    ("loss flag without the CI leg", "    return bool(diff < -spr and hi < 0)", "    return bool(diff < -spr)", ("FT-BRANCH",)),
    ("loss flag without the spread leg", "    return bool(diff < -spr and hi < 0)", "    return bool(hi < 0)", ("FT-BRANCH",)),
    ("C1 HELD + L1 read as T-3 (B5)", "    if c1 and l1:\n        return \"T-5\", True", "    if c1 and l1:\n        return \"T-3\", False", ("FT-BRANCH",)),
    ("M4 refit degeneracy refuses (O2)", "    except Degenerate as why:\n        return dict(mu=None", "    except ZeroDivisionError as why:\n        return dict(mu=None", ("FT-M4VOID",)),
    ("T M4 degeneracy refuses (O2)", "        if body[\"rule\"] == \"map\":\n            refuse(\"V partition", "        if True:\n            refuse(\"V partition", ("FT-M4VOID",)),
    ("V degeneracy tolerated (B6)", "    except Degenerate as e:\n        refuse(\"V seed %d: %s; %s\" % (seed, e, B6))", "    except Degenerate as e:\n        return None", ("FT-M4VOID",)),
    ("P8 on M1 only", "sc(ident[\"m1\"] == RECORD_M1 and ident[\"m2\"] == RECORD_M2)", "sc(ident[\"m2\"] == RECORD_M2)", ("FT-BRANCH",)),
    ("outcome opened 'w'", 'with open(path, "x", encoding="utf-8", newline="\\n") as f:', 'with open(path, "w", encoding="utf-8", newline="\\n") as f:', ("FT-PIN",)),
    ("pin check removed", 'if got["blob"] != blob or got["lf16"] != lf16:', "if False:", ("FT-PIN",)),
    ("connect guard without immutable", '        params["immutable"] = "1"\n', '        pass\n', ("FT-GUARD",)),
    ("connect guard ignores -wal", "        if os.path.exists(sp) and os.path.getsize(sp) > 0:", "        if False:", ("FT-GUARD",)),
    ("threads not pinned", "for _v in THREAD_VARS:                       # BEFORE numpy", "for _v in ():                       # BEFORE numpy", ("FT-THREADS",)),
    ("embedding guard not run by header", "    embedding_guard_flat()\n    return pid", "    return pid", ("FT-EMBGUARD",)),
    ("explicit model dropped", "        EMB_MODEL_EXPLICIT = model\n", "        EMB_MODEL_EXPLICIT = None\n", ("FT-EMBGUARD",)),
    ("readers not redirected", "        AF.EMB_DB = F.EMB_DB = path\n", "        pass\n", ("FT-EMBGUARD",)),
    ("pins not redirected", "        PIN_TABLES = ((path, \"embeddings\", \"query\")", "        _unused = ((path, \"embeddings\", \"query\")", ("FT-EMBGUARD",)),
    ("missing manifest read as no manifest", "    manifest = {}\n    if os.path.exists(mp):", "    manifest = None\n    if os.path.exists(mp):", ("FT-EMBGUARD",)),
    ("explicit cache file not validated", "        EG.validate_cache_file(path)\n", "        pass\n", ("FT-EMBGUARD",)),
    ("C-ET-3 arm-copy gate dropped", "        if is_arm_copy(path) and os.path.normcase(ARM_COPY_ADMITTED or \"\") != os.path.normcase(path):\n",
     "        if False:\n", ("FT-EMBGUARD",)),
    ("C-ET-3 arm copy = card files only", "    return bool(os.path.basename(path).endswith(\"__card.db\") or os.path.exists(path + \".provenance.json\")\n",
     "    return bool(os.path.basename(path).endswith(\"__card.db\")\n", ("FT-EMBGUARD",)),
    ("C-ET-3 embedder_cross dir not covered", "                or os.path.normcase(os.path.abspath(path)).startswith(xd))\n",
     "                or False)\n", ("FT-EMBGUARD",)),
    ("embedding flags admitted with --run", "    if (a.embedding_cache_file is not None or a.embedding_model is not None) and not (a.dry_run or a.identity_check):",
     "    if False:", ("FT-EMBGUARD",)),
    ("X8 guard uses the root region for every site", "    return EG.guard_file(data_path(EMB_DB_NAME), g[\"byid\"], lambda s: region_query_ids(s[\"id\"], g[\"byid\"]),",
     "    return EG.guard_file(data_path(EMB_DB_NAME), g[\"byid\"], lambda s: region_query_ids(g[\"root\"], g[\"byid\"]),", ("FT-EMBGUARD",)),
    ("X9 guard reads the DB-of-record name", "    return EG.guard_file(data_path(EMB_DB_NAME),", "    return EG.guard_file(data_path(\"embeddings_cache.db\"),",
     ("FT-EMBGUARD",)),
    ("X10 fit_set reads the DB-of-record name", "    con = pool_guard.open_ro(data_path(EMB_DB_NAME))\n",
     "    con = pool_guard.open_ro(data_path(\"embeddings_cache.db\"))\n", ("FT-EMBGUARD",)),
    ("X11 EMB_CACHE_SET never set", "        EMB_DB_NAME, EMB_CACHE_SET = path, True\n", "        EMB_DB_NAME, EMB_CACHE_SET = path, False\n", ("FT-EMBGUARD",)),
    # MIX-FLAT-SELFTEST-GAPS (READY dde660e D5: the reviewer's R3, R3b, R3d)
    ("R3 T's M4 VOID forces C1 FAILED", '    c1 = criterion(p["d1"], sv1, p["d1_lo"], p["d1_hi"])\n',
     '    c1 = criterion(p["d1"], sv1, p["d1_lo"], p["d1_hi"]) and p["d4"] is not None\n', ("FT-ASSEMBLY",)),
    ("R3b paired() M4-VOID guard removed", '        if arms[arm]["per4"] is None or arms[a]["per4"] is None:\n            d4, lo4, hi4 = None, None, None',
     '        if False:\n            d4, lo4, hi4 = None, None, None', ("FT-ASSEMBLY",)),
    ("R3d spread_V of M1 NA by T's M4 VOID", '                spread_V={m: spread_opt([arms["V%d" % s][m] for s in SEEDS]) for m in ("m1", "m2", "m4")},',
     '                spread_V={m: (None if arms["T"]["m4"] is None else spread_opt([arms["V%d" % s][m] for s in SEEDS])) for m in ("m1", "m2", "m4")},',
     ("FT-ASSEMBLY",)),
    ("paired() against the wrong arm", '        d1 = arms[arm]["per1"] - arms[a]["per1"]', '        d1 = arms[a]["per1"] - arms[arm]["per1"]', ("FT-ASSEMBLY",)),
)


def run_mutants(heavy=True):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    print("MUTANTS (%d): each removes or alters one check; KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: the target text occurs %d times (must be exactly 1)" % (TAG, name, head.count(old)))
        ok_orig = _exec_selftest(src, tests)
        res = _exec_selftest(head.replace(old, new) + tail, tests)
        k = (res is not True) and ok_orig is True
        killed += int(k)
        print("  %-42s tests %-11s original %-4s mutant %-8s | %s" % (name, ",".join(tests), "PASS" if ok_orig is True else "FAIL",
                                                                    "KILLED" if k else "SURVIVED", "" if res is True else res[:110]))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def _exec_selftest(src, tests):
    saved = {v: os.environ.get(v) for v in THREAD_VARS}
    ns = {"__name__": "flat_mix_mmlu_mutant", "__file__": os.path.abspath(__file__)}
    try:
        for v in THREAD_VARS:
            os.environ.pop(v, None)
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True, heavy=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:120])
    finally:
        for v, x in saved.items():
            os.environ[v] = x
        sqlite3.connect = _guarded_connect


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--identity-check", "--run", "--analyze"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--max-chunks", type=int, default=None)
    ap.add_argument("--embedding-cache-file", default=None, help="EMBEDDER-PLUMBING: the embedding cache to read (DATA_ROOT-relative "
                    "or absolute); absent -> embeddings_cache.db")
    ap.add_argument("--embedding-model", default=None, help="EMBEDDER-PLUMBING: the tree's embedder (the model the vectors must come "
                    "from); absent -> the run manifest's embedding_model")
    a = ap.parse_args(argv)
    configure_from_args(a)
    if a.selftest or a.mutants:
        print("pool %s (selftest: synthetic only; the pool is not read)" % POOL_ID)
        print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
        print("[SCRIPT] %s" % fmt_pins(script_pins()))
        if a.mutants:
            return run_mutants()
        t0 = time.perf_counter()
        n = selftest()
        print("SELFTEST PASSED: %d checks (%.0f s)" % (n, time.perf_counter() - t0))
        return 0
    if a.dry_run:
        return dry_run()
    if a.identity_check:
        return identity_check()
    if a.run:
        return run(max_chunks=a.max_chunks)
    return analyze()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
