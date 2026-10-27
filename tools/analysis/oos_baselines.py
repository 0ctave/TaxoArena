"""OOS-BASELINES: on the SAME pinned qwen3 256-d S0 embeddings and the same CLINC150 EVAL rows, is S0's label-free no-match score
(AUROC 0.974) equivalent to standard out-of-scope detectors fitted on TRAIN in-scope rows (label-using: nearest-class-centroid cosine,
shared-covariance class Mahalanobis; label-free: kNN distance, marginal Mahalanobis), within 0.010 AUROC?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-02 (before any code or call) — OOS-BASELINES: on the SAME pinned
qwen3 256-d S0 embeddings and the same CLINC150 EVAL rows, ...", span L23342-L23375 _as_of d635fec5 (the registrar's commit 1a922a80,
parent 487ac3bd; plan Amendment 37). Record docs/agents/results/OOS-BASELINES.json. --run REFUSES unless a LINE of the programme starts
with that heading (REG_RE, line-anchored). Kind: zero-call CPU reader: zero judge calls, zero embeddings, no build, no Ollama, no pool
of record (pool_guard is not engaged: no pool is read), no embeddings_cache*.db.

INSTRUMENT (imported, never copied): tools/analysis/intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271 (LF), its blob
asserted at every entry point (another blob REFUSES): pin_check / raw_pin_check (experiment_configs/intent_transfer_s0_pins.json; --run
strict), load_corpora, text_set, check_meta / expected_meta, load_vectors (S0's 512-d read), Space (first 256 coordinates,
L2-renormalised), km_fit (spherical k-means, k-means++, n_init 1, max_iter 300; TRAIN through fit_rows), fit_rows (the TRAIN-ONLY
guard: an OOS, dropped or off-side row REFUSES), S_idx, centroids_by_label, auroc, comp_weights, pct_ci, basic_ci, kish, hanley_mcneil
and S0's C2 itself (ITS.c2, called UNCHANGED for the identity: per-seed A, supervised A, the GATE threshold, FPR95, K 300 and its
bootstrap draws). sklearn.covariance.LedoitWolf (assume_centered=True) for (b) and (d).

SCORES (higher = more in-scope; S0's auroc(in-scope EVAL, OOS)):
  S0   max-cos to label-free k-means K 150 TRAIN centroids, seeds 0-4 (S0's partitions re-fitted; equal to c2's per seed, asserted).
  (a)  max-cos to the nearest TRAIN class centroid (centroids_by_label; equal to c2's supervised A, asserted). LABELLED reference.
  (b)  -min_c (x - mu_c)' Sigma^-1 (x - mu_c); mu_c class means of the renormalised TRAIN vectors (not renormalised); Sigma = LW of the
       pooled within-class residuals (assume_centered). Unshrunk (pinv of the empirical residual covariance) DESCRIPTIVE. LABELLED.
  (c)  cos to the k-th nearest TRAIN in-scope row, k = 10 fixed; k 1 / 5 / 25 / 50 DESCRIPTIVE, never selected. LIKE-FOR-LIKE peer.
  (d)  -(x - mu)' Sigma^-1 (x - mu); ONE mean and ONE LW covariance of all TRAIN in-scope rows; marginal_fit(X) takes the matrix only
       (no label argument exists; asserted by signature at every call). Unshrunk DESCRIPTIVE. LIKE-FOR-LIKE peer.
  Thresholds: each detector's own GATE threshold (S0's rule: the floor(0.05 n)-th smallest GATE in-scope score, TPR 0.95), FPR95 on
  EVAL OOS, DESCRIPTIVE.

CRITERIA (registered; criteria_lines prints every branch, each executed by the selftest):
  Delta_b = A(b) - mean_{s=0..4} A(S0, s). SE_total = sqrt(SE_boot^2 + var_seed / 5): SE_boot = SD (ddof 1) of Delta_b over B 2,000
  paired draws of S0 C2's stratified component bootstrap (in-scope and OOS components resampled separately; one weight pair per draw
  for every score; S0's C2 stream BOOT_SEED + 2, consumed in c2's order: the S0 seed-0 draws are asserted equal to c2's draws);
  var_seed = sample variance (ddof 1) over s of A(S0, s).
  OB-x EQUIVALENT iff Delta +/- 1.645 SE_total lies inside (-0.010, +0.010); DIFFERENT iff |Delta| > 0.010 AND Delta +/- 1.96 SE_total
  excludes 0, read BASELINE-BETTER (Delta > 0) or S0-BETTER (Delta < 0); NEITHER otherwise.
  READING (two, joined "<like-for-like> / <label>"; first that applies): LIKE-FOR-LIKE CELLS-NOT-BEST (OB-c or OB-d BASELINE-BETTER),
  CELLS-ADD (OB-c AND OB-d S0-BETTER), GEOMETRY-CARRIES (OB-d EQUIVALENT), NOT-SHOWN; LABEL LABELS-HELP (OB-a or OB-b BASELINE-BETTER),
  COMPETITIVE (OB-a AND OB-b EQUIVALENT), NOT-SHOWN. F-OB fires iff any OB-x reads BASELINE-BETTER (its OB-c / OB-d sentence too when
  it fires through a peer). IDENTITY PRECONDITION (refuse; nothing written): S0 A per seed 0.97437 / 0.97263 / 0.97601 / 0.97446 /
  0.97649, A(a) 0.97640 ("%.5f"), FPR95 0.1578 ("%.4f") at threshold 0.74326 ("%.5f"), seed 0.

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets):
  OB1 S0's c2 is called unchanged with spaces {"qwen3": S, "nomic": S, "gemma": S}: c2's beside-lines for nomic / gemma would read
      those embedders; HYGIENE reads qwen3 only, so the qwen3 Space is passed in their slots and their two values are DISCARDED
      (never printed). Every other c2 value is used (identity) and its bootstrap draws are asserted equal to this script's S0 seed-0
      draws (the stream that decides is c2's).
  OB2 the BASIC interval [2 Delta - q97.5, 2 Delta - q2.5] and the percentile interval of the draws printed beside, DESCRIPTIVE.
  OB3 the verdict line of each OB-x is re-stated at the measured SE_total against the registered prediction point (a: the SEEN
      +0.0016; b +0.007; c +0.002; d -0.030): SCOREABLE (EQUIVALENT side) iff |P| <= 0.010 - 2.487 SE_total; SCOREABLE (DIFFERENT side)
      iff |P| >= 0.010 + 0.842 SE_total; DESCRIPTIVE-ONLY otherwise. Criteria are scored as written either way.
  OB4 numeric predictions HELD iff the point lies in the closed 80% interval; each probability is scored by its own Brier (event
      1 / 0), the per-prediction sum printed beside.
  OB5 kNN: the k-th largest cosine among the TRAIN in-scope rows (ties counted with multiplicity); no query row is a TRAIN row.

HYGIENE: reads intent_transfer_corpora_v1.db and intent_emb_qwen3.db only (S0's pins, sha256-bytes, checked before and after; a change
REFUSES and nothing is written), mode=ro&immutable=1 through S0's readers (non-empty -wal / -journal REFUSES). Threads OMP / OPENBLAS /
MKL = 1 before numpy. --dry-run and --run REFUSE while a java.exe runs.

OUTPUT (experiment_results/oos_baselines/, write-once, mode "x"; an existing path REFUSES before any read): outcome.txt (of record),
oos_scores.csv (item id, role, every score; never text).

LAUNCH (run-operator; zero calls; nothing heavy running; CPU lane):
  python tools/analysis/oos_baselines.py --selftest
  python tools/analysis/oos_baselines.py --mutants
  python tools/analysis/oos_baselines.py --dry-run      # pins, census / denominators, S0 identity (numbers of record), timings; writes nothing
  python tools/analysis/oos_baselines.py --run          # the file of record (write-once)
  (S0's DBs under TAXOARENA_DATA_ROOT, default the repo root; --db / --emb-dir / --out-dir override.)

MUTANT TABLE: `--mutants` and the commit message (each mutant names the selftest sections that must kill it).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import csv             # noqa: E402
import hashlib         # noqa: E402
import inspect         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import re              # noqa: E402
import shutil          # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile        # noqa: E402
import time            # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import intent_transfer_s0 as ITS      # noqa: E402  (imported unchanged; blob asserted)
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402
II = ITS.II

TAG = "[OOS-BASELINES]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
CORPUS = "clinc"
D = ITS.SLICE                              # 256
S0_SEEDS = ITS.SEEDS                       # 0-4
BOOT_B = ITS.BOOT_B                        # 2,000
BOOT_SEED = ITS.BOOT_SEED
STREAM = BOOT_SEED + 2                     # S0's C2 stream
TPR = ITS.TPR_TARGET                       # 0.95
MARGIN = 0.010
Z90, Z95, Z80P = 1.645, 1.96, 0.842
KNN_K = 10
KNN_DESC = (1, 5, 25, 50)
DET = ("a", "b", "c", "d")
DET_NAME = {"a": "nearest TRAIN class centroid, max-cos (LABELLED reference)",
            "b": "class Mahalanobis, shared Ledoit-Wolf covariance (LABELLED reference)",
            "c": "kNN distance, cos to the 10th nearest TRAIN in-scope row (LIKE-FOR-LIKE peer)",
            "d": "marginal Mahalanobis, one mean + one Ledoit-Wolf covariance (LIKE-FOR-LIKE peer, label-free)"}
PEER = {"c": "kNN", "d": "marginal Mahalanobis"}
LABELLED = {"a": "labelled centroid", "b": "class Mahalanobis"}
IDENTITY = {"per_seed": ("0.97437", "0.97263", "0.97601", "0.97446", "0.97649"), "A_a": "0.97640", "fpr95": "0.1578", "thr": "0.74326"}
# Registered predictions (PREDICTIONS P1-P6).
PRED_POINT = {"a": 0.0016, "b": 0.007, "c": 0.002, "d": -0.030}              # a: the SEEN point (no numeric prediction is made of it)
P_NUM = {"b": (0.007, -0.006, 0.018), "c": (0.002, -0.006, 0.008), "d": (-0.030, -0.080, 0.000)}
P_STAT = {"a": {"EQUIVALENT": 0.95},
          "b": {"BASELINE-BETTER": 0.30, "EQUIVALENT": 0.20, "NEITHER": 0.45, "S0-BETTER": 0.05},
          "c": {"EQUIVALENT": 0.45, "NEITHER": 0.45, "BASELINE-BETTER": 0.07, "S0-BETTER": 0.03},
          "d": {"S0-BETTER": 0.60, "NEITHER": 0.25, "EQUIVALENT": 0.10, "BASELINE-BETTER": 0.05}}
P_READ = {"like": {"CELLS-NOT-BEST": 0.11, "CELLS-ADD": 0.02, "GEOMETRY-CARRIES": 0.10, "NOT-SHOWN": 0.77},
          "label": {"LABELS-HELP": 0.30, "COMPETITIVE": 0.19, "NOT-SHOWN": 0.51}}
P_FPR = {"a": (0.15, 0.10, 0.20), "b": (0.13, 0.07, 0.22), "c": (0.15, 0.09, 0.22), "d": (0.30, 0.15, 0.50)}
P6 = (0.0015, 0.70)
PLAN = {"n_in": 6672, "n_oos": 1350, "se_total": {"a": 0.00288, "b": 0.00288, "c": 0.00288, "d": 0.00374}, "hm": 0.00152, "se_A": 0.00198}
OUT_DIR = os.path.join(ROOT, "experiment_results", "oos_baselines")
OUTCOME = "outcome.txt"
SCORES_CSV = "oos_scores.csv"
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_HEADING = "## Registered 2026-10-02 (before any code or call) \u2014 OOS-BASELINES:"
REG_RE = re.compile(r"^" + re.escape(REG_HEADING), re.M)
REG = ("docs/judge_v2_program.md \"## Registered 2026-10-02 (before any code or call) \u2014 OOS-BASELINES: on the SAME pinned qwen3 "
       "256-d S0 embeddings ...\" L23342-L23375 _as_of d635fec5 (registrar 1a922a80); kind zero-call; plan Amendment 37")
ASYMMETRY = ("THE ASYMMETRY (registered): S0's no-match reads (i) which TRAIN rows are in scope and (ii) one integer of label information, "
             "K = 150 = the number of gold intents; it never reads a class label. (c) kNN and (d) marginal Mahalanobis read exactly (i) "
             "and no class label: they are the LIKE-FOR-LIKE PEERS, and (d) decides whether 0.974 belongs to the cells or to the "
             "embedder's in-scope geometry. (a) and (b) read the 150 class labels of every TRAIN row: LABELLED REFERENCES, an upper "
             "comparison, not peers. S0 reads flat k-means cells, not a tree: no result here credits or debits a tree.")
QUALIFIER = "[asymmetry: (a)/(b) read 150 TRAIN class labels; S0, (c), (d) read none (S0 reads K = 150)]"
SPLIT_NOTE = ("CLINC150 SPLIT (registered): the oos_plus variant (clinc_data_oos_plus.json, sha256 bfcca9ae...); S0's CK-CLOSE-v1 hash "
              "sides, not the file's splits; every kept OOS row (1,350, all hash sides) read as EVAL. Published CLINC150 OOS numbers "
              "(standard split, fine-tuned encoders) are never like-for-like with any number here; at most 'indicative'.")
READINGS = ("builder's readings: OB1 c2 called unchanged with the qwen3 Space in its nomic / gemma slots (those two beside-values "
            "discarded, never printed); OB2 BASIC and percentile intervals DESCRIPTIVE; OB3 verdict lines re-stated at the measured SE_total "
            "against the registered prediction points; OB4 numeric HELD iff in the closed 80% interval, one Brier per probability; OB5 kNN "
            "k-th largest cosine with multiplicity")
DOES_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): OOS on real traffic or any other corpus; comparability with published "
                 "CLINC150 numbers; anything about a tree (flat k-means cells only); OOS on capability text, MMLU-Pro cells or tree leaves; "
                 "fine-tuned detectors, energy / logit scores or any detector beyond the four; other embedders, slices or prompts (qwen3 "
                 "256 RAW only); that labels are unnecessary in general; a parity word outside +/-0.010 AUROC; that FPR95 decides anything.")
EVENTS = []


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_its_blob():
    got = RO.git_blob_lf(ITS.__file__)
    if got != ITS_BLOB:
        refuse("intent_transfer_s0.py is blob %s, not the registered %s: S0's machinery must be imported unchanged" % (got, ITS_BLOB))
    return got


_foreign_heavy = ITS._foreign_heavy


def heavy_check():
    heavy = _foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a foreign heavy process runs (%s): never beside a construction or site null (one heavy process)" % heavy[:3])


def check_registered(programme):
    ok = os.path.isfile(programme) and bool(REG_RE.search(open(programme, encoding="utf-8").read()))
    print("%s registration heading (line-anchored) in %s: %s" % (TAG, os.path.basename(programme), "PRESENT" if ok else "ABSENT"))
    return ok


# ------------------------------------------------------------------------------------------------ inputs
def load_inputs(db, emb_dir, strict):
    """-> (sha0, C, S): S0's pins (strict on --run), meta check, the CLINC rows and the qwen3 256-d Space (S0's readers)."""
    sha0 = {"ingest_db": ITS.pin_check(db, "ingest_db", strict)}
    ITS.raw_pin_check(db, strict)
    p = ITS.emb_path("qwen3", emb_dir)
    sha0["qwen3"] = ITS.pin_check(p, "emb", strict, sub="qwen3", label="intent_emb_qwen3.db")
    CS = ITS.load_corpora(db)
    texts, set_sha, _derived = ITS.text_set(CS)
    ITS.check_meta(p, ITS.expected_meta("qwen3", set_sha, len(texts), sha0["ingest_db"]))
    C = CS[CORPUS]
    want = sorted(set(C.text[i] for i in np.nonzero(C.kept)[0]))
    vecs = ITS.load_vectors(p, "qwen3", want)
    S = ITS.Space(vecs, C, D)
    return sha0, C, S


def after_check(sha0, db, emb_dir):
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else ITS.emb_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))
    return "pins re-checked before and after, unchanged: %s" % {k: v[:16] for k, v in sha0.items()}


def rows(C, S):
    """The four index sets (S0's): TRAIN in-scope (fits), GATE in-scope (thresholds), EVAL in-scope, EVAL OOS (every kept OOS row)."""
    return {"train": ITS.S_idx(C, S, SS.TRAIN), "gate": ITS.S_idx(C, S, SS.GATE), "in": ITS.S_idx(C, S, SS.EVAL),
            "oos": ITS.S_idx(C, S, SS.EVAL, oos=True)}


def census(C, S):
    R = rows(C, S)
    out = {k: int(len(v)) for k, v in R.items()}
    for k in ("in", "oos"):
        out[k + "_components"] = int(len(np.unique(C.comp[R[k]])))
        out[k + "_kish"] = ITS.kish(C.comp[R[k]])
    out["train_oos_rows"] = int(C.oos[R["train"]].sum())
    return out


def census_line(cn):
    return ("CENSUS (CLINC, qwen3 256): TRAIN in-scope %d (fits); GATE in-scope %d (thresholds); EVAL in-scope n_in %d in %d components "
            "(Kish %.4f); EVAL OOS n_OOS %d in %d components (Kish %.4f); registered n_in %d / n_OOS %d"
            % (cn["train"], cn["gate"], cn["in"], cn["in_components"], cn["in_kish"], cn["oos"], cn["oos_components"], cn["oos_kish"],
               PLAN["n_in"], PLAN["n_oos"]))


# ------------------------------------------------------------------------------------------------ detectors
def maxcos(Cm, X):
    """S0's C2 score: max-cos to the centroids."""
    return (X @ Cm.T).max(1)


def threshold(sg):
    """S0's C2 rule: >= 95% of GATE in-scope scores are >= thr."""
    return float(np.sort(sg)[int(np.floor((1 - TPR) * len(sg)))])


def lw_precision(R):
    from sklearn.covariance import LedoitWolf
    lw = LedoitWolf(assume_centered=True).fit(R)
    return np.asarray(lw.precision_, dtype=np.float64), float(lw.shrinkage_)


def class_fit(X, labels):
    """(b): class means (not renormalised) and the LW precision of the pooled within-class residuals; the unshrunk pinv beside."""
    u, inv = np.unique(np.asarray(labels).astype(str), return_inverse=True)
    M = np.array([X[inv == j].mean(0) for j in range(len(u))])
    Rz = X - M[inv]
    P, shrink = lw_precision(Rz)
    P0 = np.linalg.pinv(Rz.T @ Rz / len(Rz))
    return {"M": M, "P": P, "P0": P0, "shrinkage": shrink, "n_class": int(len(u))}


def marginal_fit(X):
    """(d): ONE mean and ONE LW covariance of the TRAIN in-scope rows. Takes the matrix ONLY: no label column can reach this fit."""
    if not (isinstance(X, np.ndarray) and X.ndim == 2 and X.dtype.kind == "f"):
        refuse("marginal fit: input is not a 2-d float matrix (a label column?)")
    X = X.astype(np.float64)
    mu = X.mean(0)
    Rz = X - mu
    P, shrink = lw_precision(Rz)
    P0 = np.linalg.pinv(Rz.T @ Rz / len(Rz))
    return {"mu": mu, "P": P, "P0": P0, "shrinkage": shrink}


def maha_min(X, M, P):
    XP = X @ P
    d = np.einsum("ij,ij->i", XP, X)[:, None] - 2.0 * (XP @ M.T) + np.einsum("ij,ij->i", M @ P, M)[None, :]
    return d.min(1)


def maha_one(X, mu, P):
    Z = X - mu
    return np.einsum("ij,ij->i", Z @ P, Z)


def knn_scores(Q, T, ks, chunk=1024):
    """-> {k: cos to the k-th nearest row of T} for each query row (OB5)."""
    kmax = max(ks)
    out = {k: np.empty(len(Q)) for k in ks}
    for a in range(0, len(Q), chunk):
        sims = Q[a:a + chunk] @ T.T
        top = -np.sort(-np.partition(sims, sims.shape[1] - kmax, axis=1)[:, sims.shape[1] - kmax:], axis=1)
        for k in ks:
            out[k][a:a + chunk] = top[:, k - 1]
    return out


def s0_scores(C, S, R):
    """S0 no-match per seed 0-4 (S0's partitions re-fitted through km_fit / fit_rows)."""
    kf = II.GOLD_K[CORPUS][1]
    out = {}
    for s in S0_SEEDS:
        Cm = ITS.km_fit(C, S, kf, s, "OB S0 k-means K=%d s%d" % (kf, s))
        out["s%d" % s] = {k: maxcos(Cm, S.X[R[k]]) for k in ("in", "oos", "gate")}
    return out


def baseline_scores(C, S, R):
    """(a)-(d) and the descriptive variants; every fit on TRAIN in-scope rows through fit_rows; no fit reads GATE / EVAL / OOS."""
    tr = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OB (a) class centroids")
    Xtr = S.X[tr]
    _u, G = ITS.centroids_by_label(Xtr, C.fine[tr])
    tr_b = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OB (b) class Mahalanobis")
    fb = class_fit(S.X[tr_b], C.fine[tr_b])
    tr_c = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OB (c) kNN reference set")
    tr_d = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OB (d) marginal Mahalanobis")
    if list(inspect.signature(marginal_fit).parameters) != ["X"]:
        refuse("marginal_fit takes %s: the label-free fit must take the matrix only" % list(inspect.signature(marginal_fit).parameters))
    fd = marginal_fit(S.X[tr_d])
    out, ks = {}, (KNN_K,) + KNN_DESC
    for k in ("in", "oos", "gate"):
        X = S.X[R[k]]
        kn = knn_scores(X, S.X[tr_c], ks)
        out.setdefault("a", {})[k] = maxcos(G, X)
        out.setdefault("b", {})[k] = -maha_min(X, fb["M"], fb["P"])
        out.setdefault("c", {})[k] = kn[KNN_K]
        out.setdefault("d", {})[k] = -maha_one(X, fd["mu"], fd["P"])
        out.setdefault("b_unshrunk", {})[k] = -maha_min(X, fb["M"], fb["P0"])
        out.setdefault("d_unshrunk", {})[k] = -maha_one(X, fd["mu"], fd["P0"])
        for kk in KNN_DESC:
            out.setdefault("c_k%d" % kk, {})[k] = kn[kk]
    meta = {"shrink_b": fb["shrinkage"], "shrink_d": fd["shrinkage"], "n_class": fb["n_class"], "n_train": int(len(tr))}
    return out, meta


def fpr_line(sc):
    thr = threshold(sc["gate"])
    return {"thr": thr, "fpr95": float(np.mean(sc["oos"] >= thr)), "tpr_eval": float(np.mean(sc["in"] >= thr)),
            "tpr_gate": float(np.mean(sc["gate"] >= thr))}


# ------------------------------------------------------------------------------------------------ identity
def identity_values(c2r, s0, A_a, f0):
    return {"per_seed": tuple("%.5f" % a for a in c2r["per_seed"]), "A_a": "%.5f" % A_a, "fpr95": "%.4f" % f0["fpr95"],
            "thr": "%.5f" % f0["thr"], "mine_per_seed": tuple("%.5f" % ITS.auroc(s0["s%d" % s]["in"], s0["s%d" % s]["oos"]) for s in S0_SEEDS)}


def identity_check(got, target):
    bad = [k for k in ("per_seed", "A_a", "fpr95", "thr") if got[k] != target[k]]
    if got["mine_per_seed"] != got["per_seed"]:
        bad.append("refit per seed %s != c2 %s" % (got["mine_per_seed"], got["per_seed"]))
    line = ("IDENTITY: S0 A per seed %s (registered %s); A(a) %s (registered %s); FPR95 %s at threshold %s (registered %s at %s); this "
            "script's re-fitted S0 per seed %s" % (" / ".join(got["per_seed"]), " / ".join(target["per_seed"]), got["A_a"], target["A_a"],
                                                   got["fpr95"], got["thr"], target["fpr95"], target["thr"], " / ".join(got["mine_per_seed"])))
    print("%s %s" % (TAG, line))
    if bad:
        refuse("IDENTITY PRECONDITION FAILED on %s: S0 C2 is not reproduced to the registered digits; no readout is written" % bad)
    return line + " -> REPRODUCED"


# ------------------------------------------------------------------------------------------------ statistics
def ob_status(Dl, se, margin=None):
    m = MARGIN if margin is None else margin
    lo90, hi90, lo95, hi95 = Dl - Z90 * se, Dl + Z90 * se, Dl - Z95 * se, Dl + Z95 * se
    if lo90 > -m and hi90 < m:
        return "EQUIVALENT"
    if abs(Dl) > m and (lo95 > 0 or hi95 < 0):
        return "BASELINE-BETTER" if Dl > 0 else "S0-BETTER"
    return "NEITHER"


def paired_boot(C, R, s0, bs, B=None):
    """B paired draws: one (in-scope, OOS) weight pair per draw, S0's C2 stream consumed in c2's order (zip of the two generators)."""
    B = BOOT_B if B is None else B
    rng = np.random.default_rng(STREAM)
    names = ["s%d" % s for s in S0_SEEDS] + list(DET)
    allsc = dict((k, s0[k]) for k in names if k in s0)
    allsc.update((k, bs[k]) for k in DET)
    draws = {k: [] for k in names}
    for wi, wo in zip(ITS.comp_weights(C.comp[R["in"]], B, rng), ITS.comp_weights(C.comp[R["oos"]], B, rng)):
        for k in names:
            draws[k].append(ITS.auroc(allsc[k]["in"], allsc[k]["oos"], wi, wo))
    return {k: np.asarray(v) for k, v in draws.items()}


def readout(s0, bs, draws):
    A_s0 = np.array([ITS.auroc(s0["s%d" % s]["in"], s0["s%d" % s]["oos"]) for s in S0_SEEDS])
    mean_s0 = float(A_s0.mean())
    var_seed = float(np.var(A_s0, ddof=1))
    s0_draw_mean = np.mean(np.vstack([draws["s%d" % s] for s in S0_SEEDS]), axis=0)
    out = {"A_s0": A_s0, "mean_s0": mean_s0, "var_seed": var_seed, "det": {}}
    for b in DET:
        A = ITS.auroc(bs[b]["in"], bs[b]["oos"])
        Dl = A - mean_s0
        dd = draws[b] - s0_draw_mean
        se_boot = float(np.std(dd, ddof=1))
        se = float(np.sqrt(se_boot ** 2 + var_seed / len(S0_SEEDS)))
        plo, phi = ITS.pct_ci(dd)
        blo, bhi = ITS.basic_ci(Dl, dd)
        out["det"][b] = {"A": A, "D": Dl, "se_boot": se_boot, "se": se, "lo90": Dl - Z90 * se, "hi90": Dl + Z90 * se,
                         "lo95": Dl - Z95 * se, "hi95": Dl + Z95 * se, "plo": plo, "phi": phi, "blo": blo, "bhi": bhi,
                         "status": ob_status(Dl, se), "status_m": None, "D_seed0": A - float(A_s0[0]),
                         "A_lo": ITS.pct_ci(draws[b])[0], "A_hi": ITS.pct_ci(draws[b])[1]}
    return out


def readings(st):
    if st["c"] == "BASELINE-BETTER" or st["d"] == "BASELINE-BETTER":
        like = "CELLS-NOT-BEST"
    elif st["c"] == "S0-BETTER" and st["d"] == "S0-BETTER":
        like = "CELLS-ADD"
    elif st["d"] == "EQUIVALENT":
        like = "GEOMETRY-CARRIES"
    else:
        like = "NOT-SHOWN"
    if st["a"] == "BASELINE-BETTER" or st["b"] == "BASELINE-BETTER":
        label = "LABELS-HELP"
    elif st["a"] == "EQUIVALENT" and st["b"] == "EQUIVALENT":
        label = "COMPETITIVE"
    else:
        label = "NOT-SHOWN"
    return like, label


def falsifier(st):
    via = [b for b in DET if st[b] == "BASELINE-BETTER"]
    return bool(via), via


def verdict_line(pred, se):
    eq_reach = MARGIN - (Z90 + Z80P) * se
    diff_reach = MARGIN + Z80P * se
    if abs(pred) <= eq_reach:
        w = "SCOREABLE (EQUIVALENT side)"
    elif abs(pred) >= diff_reach:
        w = "SCOREABLE (DIFFERENT side)"
    else:
        w = "DESCRIPTIVE-ONLY"
    return eq_reach, diff_reach, w


def brier(p, event):
    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2


def _hit(v, lo, hi):
    return bool(lo <= v <= hi)


# ------------------------------------------------------------------------------------------------ lines
def support_lines(cn, RD, c2r):
    L = ["== SUPPORT (measured; planning values beside) =="]
    deff = max(cn["in_kish"], cn["oos_kish"])
    L.append("  denominators: n_in %d CLINC in-scope EVAL rows in %d components (Kish %.4f); n_OOS %d in %d components (Kish %.4f); DEFF %.4f "
             "(measured, the max of the two strata); n_eff %.0f in-scope / %.0f OOS (registered 6,672 / 1,350, DEFF 1.0000)"
             % (cn["in"], cn["in_components"], cn["in_kish"], cn["oos"], cn["oos_components"], cn["oos_kish"], deff, cn["in"] / cn["in_kish"],
                cn["oos"] / cn["oos_kish"]))
    L.append("  S0 seeds: A %s, mean %.5f, var_seed %.3e, var_seed / 5 %.3e (registered mean 0.97479, var 2.332e-6); S0 seed-0 bootstrap SE(A) "
             "%.5f (registered 0.00198); Hanley-McNeil %.5f (registered 0.00152)" % (" / ".join("%.5f" % a for a in RD["A_s0"]), RD["mean_s0"],
                                                                                   RD["var_seed"], RD["var_seed"] / 5, c2r["se_boot"], c2r["hm_se"]))
    for b in DET:
        r = RD["det"][b]
        eq, df, w = verdict_line(PRED_POINT[b], r["se"])
        L.append("  OB-%s: SE_boot %.5f, seed term %.5f, SE_total %.5f (planned %.5f); 90%% half-width %.5f; EQUIVALENT reach |Delta_true| <= "
                 "%.5f, DIFFERENT reach >= %.5f; verdict line at the prediction %+.4f: %s" % (b, r["se_boot"], np.sqrt(RD["var_seed"] / 5), r["se"],
                                                                                         PLAN["se_total"][b], Z90 * r["se"], eq, df, PRED_POINT[b], w))
    return L


def readout_lines(RD, bs_meta, fl, c2r, desc):
    L = ["== READOUTS (A = AUROC in-scope EVAL vs OOS; Delta = A(b) - mean_s A(S0, s); paired stratified component bootstrap, B %d) ==" % BOOT_B]
    L.append("  S0 no-match (K 150, seeds 0-4): A %s; mean %.5f; FPR95 (seed 0) %.4f at %.5f; K 300 seed 0 (c2, DESCRIPTIVE) %s"
             % (" / ".join("%.5f" % a for a in RD["A_s0"]), RD["mean_s0"], fl["s0"]["fpr95"], fl["s0"]["thr"], c2r["K_alt"].get(300)))
    for b in DET:
        r = RD["det"][b]
        L.append("  (%s) %s: A %.5f [pct %.5f, %.5f]; Delta %+.5f; 90%% [%+.5f, %+.5f]; 95%% [%+.5f, %+.5f]; SE_total %.5f" % (
            b, DET_NAME[b], r["A"], r["A_lo"], r["A_hi"], r["D"], r["lo90"], r["hi90"], r["lo95"], r["hi95"], r["se"]))
    L.append("  Ledoit-Wolf shrinkage coefficient: (b) %.6f (pooled within-class residuals, %d classes); (d) %.6f (one covariance); "
             "TRAIN in-scope rows fitted %d" % (bs_meta["shrink_b"], bs_meta["n_class"], bs_meta["shrink_d"], bs_meta["n_train"]))
    return L


def criteria_lines(RD):
    st = {b: RD["det"][b]["status"] for b in DET}
    L = ["== CRITERIA (EQUIVALENT iff Delta +/- 1.645 SE_total inside (-%.3f, +%.3f); DIFFERENT iff |Delta| > %.3f AND Delta +/- 1.96 SE_total "
         "excludes 0; NEITHER otherwise) %s ==" % (MARGIN, MARGIN, MARGIN, QUALIFIER)]
    for b in DET:
        r = RD["det"][b]
        L.append("OB-%s: %s (Delta %+.5f, 90%% [%+.5f, %+.5f], 95%% [%+.5f, %+.5f]; %s)" % (b, st[b], r["D"], r["lo90"], r["hi90"], r["lo95"],
                                                                                    r["hi95"], DET_NAME[b]))
    like, label = readings(st)
    L.append("READING: %s / %s" % (like, label))
    if like == "CELLS-NOT-BEST":
        for b in ("c", "d"):
            if st[b] == "BASELINE-BETTER":
                L.append("  LIKE-FOR-LIKE CELLS-NOT-BEST: on this embedding a label-free %s score beats label-free cells for OOS by %+.5f AUROC %s"
                         % (PEER[b], RD["det"][b]["D"], QUALIFIER))
    elif like == "CELLS-ADD":
        L.append("  LIKE-FOR-LIKE CELLS-ADD: label-free cells beat both label-free peers on the same embedding (kNN %+.5f, marginal "
                 "Mahalanobis %+.5f) %s" % (RD["det"]["c"]["D"], RD["det"]["d"]["D"], QUALIFIER))
    elif like == "GEOMETRY-CARRIES":
        L.append("  LIKE-FOR-LIKE GEOMETRY-CARRIES: a single label-free ellipsoid around the TRAIN in-scope cloud does as well within 0.010 "
                 "AUROC: the OOS signal is the embedder's in-scope geometry, not the cells' %s" % QUALIFIER)
    else:
        L.append("  LIKE-FOR-LIKE NOT-SHOWN: statuses OB-c %s, OB-d %s recorded joined; neither parity nor a gap %s" % (st["c"], st["d"], QUALIFIER))
    if label == "LABELS-HELP":
        for b in ("a", "b"):
            if st[b] == "BASELINE-BETTER":
                L.append("  LABEL LABELS-HELP: labels buy %+.5f AUROC on this embedding (%s) %s" % (RD["det"][b]["D"], LABELLED[b], QUALIFIER))
    elif label == "COMPETITIVE":
        L.append("  LABEL COMPETITIVE: label-free no-match is equivalent within 0.010 AUROC to labelled centroid and class-Mahalanobis "
                 "detectors on the same frozen qwen3 256-d embedding (CLINC150 oos_plus OOS pool) %s" % QUALIFIER)
    else:
        L.append("  LABEL NOT-SHOWN: statuses OB-a %s, OB-b %s recorded joined; neither parity nor a gap %s" % (st["a"], st["b"], QUALIFIER))
    fired, via = falsifier(st)
    if fired:
        L.append("F-OB: FIRED (via %s): every quote of S0 C2 carries %s; no-match may be described as label-free scope detection only, "
                 "never as competitive with standard detectors" % (", ".join("OB-" + b for b in via), "; ".join(
                     "\"a %s detector on the same qwen3 256-d embedding reaches A = %.5f\"" % (
                         {"a": "labelled centroid", "b": "class Mahalanobis", "c": "kNN", "d": "marginal Mahalanobis"}[b], RD["det"][b]["A"])
                     for b in via)))
        if any(b in ("c", "d") for b in via):
            L.append("F-OB (like-for-like): it fired through a peer: \"label-free cells carry the OOS signal\" is overturned (neighbourhood "
                     "density or a single in-scope ellipsoid does better on the same embedding)")
    else:
        L.append("F-OB: NOT FIRED (no OB-x reads BASELINE-BETTER)")
    if st["d"] == "EQUIVALENT":
        L.append("GEOMETRY BAR: OB-d EQUIVALENT: no sentence may credit the 0.974 to the cells rather than to the embedder (F-OB unaffected)")
    L.append("S0 C2 HELD and F2 NOT FIRED stand (bar 0.85); no recorded number is revised")
    return L


def descriptive_lines(RD, fl, bs, c2r):
    L = ["== DESCRIPTIVE (never scored) =="]
    for k in ("s0",) + DET:
        f = fl[k]
        L.append("  FPR95 %s: %.4f at its own GATE threshold %.5f (GATE TPR %.4f; EVAL TPR %.4f)" % (k, f["fpr95"], f["thr"], f["tpr_gate"], f["tpr_eval"]))
    for b in DET:
        r = RD["det"][b]
        L.append("  OB-%s: Delta vs S0 seed 0 (0.97437 of record) %+.5f; BASIC 95%% [%+.5f, %+.5f]; percentile 95%% [%+.5f, %+.5f]" % (
            b, r["D_seed0"], r["blo"], r["bhi"], r["plo"], r["phi"]))
    for k in ("b_unshrunk", "d_unshrunk") + tuple("c_k%d" % kk for kk in KNN_DESC):
        A = ITS.auroc(bs[k]["in"], bs[k]["oos"])
        L.append("  %s: A %.5f, Delta %+.5f (DESCRIPTIVE, never selected)" % (k, A, A - RD["mean_s0"]))
    L.append("  S0 at K 300 seed 0 (c2): %s (seen 0.97972); K 50 / 100: %s / %s" % (c2r["K_alt"].get(300), c2r["K_alt"].get(50), c2r["K_alt"].get(100)))
    return L


def predictions_lines(RD, fl):
    st = {b: RD["det"][b]["status"] for b in DET}
    like, label = readings(st)
    L = ["== PREDICTIONS (registered; numeric HELD iff the point lies in the closed 80% interval; probabilities by Brier) =="]
    L.append("  P1 Delta_a %+.5f (SEEN +0.0016, no numeric prediction); P(OB-a EQUIVALENT) 0.95: event %s, Brier %.4f" % (
        RD["det"]["a"]["D"], st["a"] == "EQUIVALENT", brier(0.95, st["a"] == "EQUIVALENT")))
    for i, b in ((2, "b"), (3, "c"), (4, "d")):
        p, lo, hi = P_NUM[b]
        v = RD["det"][b]["D"]
        br = {k: brier(q, st[b] == k) for k, q in P_STAT[b].items()}
        L.append("  P%d Delta_%s %+.5f vs %+.3f [%+.3f, %+.3f]: %s; status %s; Brier %s (sum %.4f)" % (
            i, b, v, p, lo, hi, "HELD" if _hit(v, lo, hi) else "FAILED", st[b], ", ".join("%s %.4f" % kv for kv in br.items()), sum(br.values())))
    for key, got in (("like", like), ("label", label)):
        br = {k: brier(q, got == k) for k, q in P_READ[key].items()}
        L.append("  P4' %s reading %s: Brier %s (sum %.4f)" % (key, got, ", ".join("%s %.4f" % kv for kv in br.items()), sum(br.values())))
    for b in DET:
        p, lo, hi = P_FPR[b]
        v = fl[b]["fpr95"]
        L.append("  P5 FPR95 (%s) %.4f vs %.2f [%.2f, %.2f]: %s (DESCRIPTIVE, scored at the point)" % (b, v, p, lo, hi, "HELD" if _hit(v, lo, hi) else "FAILED"))
    se_a = RD["det"]["a"]["se"]
    L.append("  P6 SE_total(OB-a) %.5f < %.4f: event %s; p %.2f, Brier %.4f" % (se_a, P6[0], bool(se_a < P6[0]), P6[1], brier(P6[1], se_a < P6[0])))
    return L


def header_lines(blob, pins_state, cn, idline):
    return ["OOS-BASELINES outcome (tools/analysis/oos_baselines.py, blob %s; imports intent_transfer_s0.py blob %s unchanged)" % (blob, ITS_BLOB),
            "registration: " + REG, "pool of record: none read (S0's own DBs only); zero judge calls; no construction; no Ollama",
            ASYMMETRY, SPLIT_NOTE, pins_state, census_line(cn), idline, READINGS]


# ------------------------------------------------------------------------------------------------ run
def out_paths(out_dir):
    return os.path.join(out_dir, OUTCOME), os.path.join(out_dir, SCORES_CSV)


def compute(C, S, identity, B=None):
    """Identity first (refuses before any baseline is scored on EVAL), then the four baselines, the paired bootstrap and the readout."""
    del ITS.FIT_LOG[:]
    del EVENTS[:]
    R = rows(C, S)
    if int(C.oos[R["train"]].sum()) or int(C.oos[R["gate"]].sum()):
        refuse("an OOS row sits in the TRAIN / GATE index sets")
    c2r = ITS.c2(C, {"qwen3": S, "nomic": S, "gemma": S})           # OB1: S0's C2 unchanged (nomic / gemma slots discarded)
    c2r.pop("other_emb", None)
    s0 = s0_scores(C, S, R)
    ITS.fit_rows(C, R["gate"], (SS.GATE,), "OB thresholds (GATE in-scope, every detector)")
    tr = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OB identity (a)")
    _u, G = ITS.centroids_by_label(S.X[tr], C.fine[tr])
    A_a = ITS.auroc(maxcos(G, S.X[R["in"]]), maxcos(G, S.X[R["oos"]]))
    f0 = fpr_line(s0["s0"])
    idline = identity_check(identity_values(c2r, s0, A_a, f0), identity)
    EVENTS.append(("IDENTITY", "ok"))
    bs, meta = baseline_scores(C, S, R)
    EVENTS.append(("BASELINES", "scored"))
    if ITS.auroc(bs["a"]["in"], bs["a"]["oos"]) != c2r["supervised_A"]:
        refuse("(a) %r != S0 c2's supervised A %r" % (ITS.auroc(bs["a"]["in"], bs["a"]["oos"]), c2r["supervised_A"]))
    draws = paired_boot(C, R, s0, bs, B)
    if (BOOT_B if B is None else B) == ITS.BOOT_B:
        if not np.array_equal(draws["s0"], np.asarray(c2r["draws"])):
            refuse("the S0 seed-0 bootstrap draws differ from S0 c2's draws: not S0's C2 stream")
    RD = readout(s0, bs, draws)
    fl = {"s0": f0}
    for b in DET:
        fl[b] = fpr_line(bs[b])
    return {"R": R, "c2": c2r, "s0": s0, "bs": bs, "meta": meta, "draws": draws, "RD": RD, "fl": fl, "idline": idline}


def main_run(db=None, emb_dir=None, out_dir=OUT_DIR, programme=PROGRAMME, identity=None, B=None):
    check_its_blob()
    db = db or os.path.join(ITS.DATA_ROOT, II.DB_NAME)
    emb_dir = emb_dir or ITS.DATA_ROOT
    for p in out_paths(out_dir):
        if os.path.lexists(p):
            refuse("%s exists: the outcome of record is write-once" % p)
    if not check_registered(programme):
        refuse("the registration heading is absent from %s: --run reads only a registered test" % programme)
    heavy_check()
    sha0, C, S = load_inputs(db, emb_dir, strict=True)
    cn = census(C, S)
    print("%s %s" % (TAG, census_line(cn)))
    X = compute(C, S, IDENTITY if identity is None else identity, B)
    pins_state = after_check(sha0, db, emb_dir)
    blob = RO.git_blob_lf(os.path.abspath(__file__))
    L = header_lines(blob, pins_state, cn, X["idline"])
    L += support_lines(cn, X["RD"], X["c2"])
    L.append(ITS.fit_audit())
    L += readout_lines(X["RD"], X["meta"], X["fl"], X["c2"], None)
    L += criteria_lines(X["RD"])
    L += descriptive_lines(X["RD"], X["fl"], X["bs"], X["c2"])
    L += predictions_lines(X["RD"], X["fl"])
    L.append(DOES_NOT_SHOW)
    for ln in L:
        print(ln)
    os.makedirs(out_dir, exist_ok=True)
    po, pc = out_paths(out_dir)
    with open(po, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    write_scores(pc, C, X)
    print("%s wrote %s and %s (write-once, of record)" % (TAG, po, pc))
    return X, L, po


def write_scores(path, C, X):
    cols = ["s%d" % s for s in S0_SEEDS] + list(DET) + ["b_unshrunk", "d_unshrunk"] + ["c_k%d" % k for k in KNN_DESC]
    with open(path, "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["item_id", "role"] + cols)
        for role, key in (("EVAL_IN", "in"), ("EVAL_OOS", "oos"), ("GATE_IN", "gate")):
            for j, i in enumerate(X["R"][key]):
                row = [C.ids[i], role]
                for c in cols:
                    src = X["s0"][c] if c in X["s0"] else X["bs"][c]
                    row.append("%.8f" % src[key][j])
                w.writerow(row)


def dry_run(db=None, emb_dir=None, programme=PROGRAMME, identity=None, timing=True):
    """Pins, census / denominators, the S0 identity (numbers of record only: c2 and S0's own seeds), timings; NO baseline is scored on
    EVAL; nothing is written."""
    check_its_blob()
    db = db or os.path.join(ITS.DATA_ROOT, II.DB_NAME)
    emb_dir = emb_dir or ITS.DATA_ROOT
    print("%s DRY RUN (zero calls; nothing written); script blob %s; ITS blob %s" % (TAG, RO.git_blob_lf(os.path.abspath(__file__)), ITS_BLOB))
    print("%s pool of record: none read (pool_guard not engaged); %s" % (TAG, REG))
    check_registered(programme)
    heavy_check()
    sha0, C, S = load_inputs(db, emb_dir, strict=False)
    cn = census(C, S)
    print("%s %s" % (TAG, census_line(cn)))
    print("%s DENOMINATORS vs registration: n_in %d (registered %d) %s; n_OOS %d (registered %d) %s; components %d / %d; Kish %.4f / %.4f "
          "(registered 1.0000 / 1.0000)" % (TAG, cn["in"], PLAN["n_in"], "MATCH" if cn["in"] == PLAN["n_in"] else "DIFFERENT", cn["oos"],
                                             PLAN["n_oos"], "MATCH" if cn["oos"] == PLAN["n_oos"] else "DIFFERENT", cn["in_components"],
                                             cn["oos_components"], cn["in_kish"], cn["oos_kish"]))
    del ITS.FIT_LOG[:]
    R = rows(C, S)
    t0 = time.time()
    c2r = ITS.c2(C, {"qwen3": S, "nomic": S, "gemma": S})
    c2r.pop("other_emb", None)
    s0 = s0_scores(C, S, R)
    tr = ITS.fit_rows(C, R["train"], (SS.TRAIN,), "OB identity (a)")
    _u, G = ITS.centroids_by_label(S.X[tr], C.fine[tr])
    A_a = ITS.auroc(maxcos(G, S.X[R["in"]]), maxcos(G, S.X[R["oos"]]))
    idline = identity_check(identity_values(c2r, s0, A_a, fpr_line(s0["s0"])), IDENTITY if identity is None else identity)
    t_id = time.time() - t0
    if timing:
        t1 = time.time()
        fb = class_fit(S.X[tr], C.fine[tr])
        fd = marginal_fit(S.X[tr])
        t_lw = time.time() - t1
        t2 = time.time()
        knn_scores(S.X[R["gate"]], S.X[tr], (KNN_K,) + KNN_DESC)
        t_knn = (time.time() - t2) * (cn["gate"] + cn["in"] + cn["oos"]) / max(1, cn["gate"])
        t3 = time.time()
        rng = np.random.default_rng(STREAM)
        n_t = 20
        for wi, wo in zip(ITS.comp_weights(C.comp[R["in"]], n_t, rng), ITS.comp_weights(C.comp[R["oos"]], n_t, rng)):
            for _k in range(9):
                ITS.auroc(s0["s0"]["in"], s0["s0"]["oos"], wi, wo)
        t_boot = (time.time() - t3) / n_t * BOOT_B
        print("%s TIMING: identity (c2 + 5 refits) %.1f s; two Ledoit-Wolf fits %.1f s (shrinkage (b) %.4f, (d) %.4f: TRAIN only, DESCRIPTIVE "
              "here); kNN over GATE + EVAL priced %.1f s; %d paired draws x 9 AUROCs priced %.1f s; total about %.1f min single-threaded"
              % (TAG, t_id, t_lw, fb["shrinkage"], fd["shrinkage"], t_knn, BOOT_B, t_boot, (t_id + t_lw + t_knn + t_boot) / 60.0))
    print("%s %s" % (TAG, after_check(sha0, db, emb_dir)))
    print("%s %s" % (TAG, ITS.fit_audit()))
    print("%s %s" % (TAG, idline))
    print("%s DRY RUN complete: nothing written; no baseline scored on EVAL" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest fixtures
FX_MODES = ("P", "W", "C")
FX_K = 16


def _rng(*parts):
    return np.random.default_rng(int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12], 16))


def _plant(mode, f, t):
    """CLINC planting (first 64 dims of 4096; the rest 1e-4 noise). In-scope intent f: 3 E[f] + E[16 + f % 4] + noise.
    P (perfect): OOS on orthogonal axes 40-47 -> every A = 1, every Delta 0, SE 0 (EQUIVALENT x 4).
    W (whiten): in-scope noise 0.6 on dims 0-23 only; OOS = an in-scope point plus 0.35 on dims 48-63 (directions the in-scope cloud
      never visits): cos scores overlap, Mahalanobis separates (BASELINE-BETTER for (b) and (d)).
    C (between): OOS halfway between two intents (3/sqrt2 on each axis): far from every centroid / row (S0, (a), (c) high), no
      farther from the marginal mean than an in-scope row ((d) low: S0-BETTER)."""
    r = _rng("fx", mode, t)
    v = np.zeros(4096)
    v[64:] = 1e-4 * r.normal(size=4032)
    if f is not None:
        sig = 0.6 if mode == "W" else 0.3
        v[f] += 3.0
        v[16 + f % 4] += 1.0
        v[:24] += sig * r.normal(size=24)
        return v
    if mode == "P":
        v[40 + int(r.integers(8))] += 3.0
        v[:64] += 0.3 * r.normal(size=64)
    elif mode == "W":
        ff = int(r.integers(FX_K))
        v[ff] += 3.0
        v[16 + ff % 4] += 1.0
        v[:24] += 0.6 * r.normal(size=24)
        v[48:64] += 0.35 * r.normal(size=16)
    else:
        f1, f2 = (int(x) for x in r.choice(FX_K, size=2, replace=False))
        v[f1] += 3.0 / np.sqrt(2.0)
        v[f2] += 3.0 / np.sqrt(2.0)
        v[16 + f1 % 4] += 0.5
        v[16 + f2 % 4] += 0.5
        v[:24] += 0.3 * r.normal(size=24)
    return v


def build_fixture(td, mode):
    rows = ITS._fixture_rows()
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows, [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = ITS.load_corpora(db)
    texts, set_sha, _d = ITS.text_set(CS)
    C = CS[CORPUS]
    V = {}
    for i in np.nonzero(C.kept)[0]:
        V[C.text[i]] = _plant(mode, None if C.oos[i] else int(C.fine[i][-2:]), C.text[i])
    p = ITS.emb_path("qwen3", td)
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(ITS.expected_meta("qwen3", set_sha, len(texts), II.file_sha(db)),
                                                                          model_digest="stub").items()))
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(v, dtype=">f4").tobytes()) for t, v in sorted(V.items())])
    con.commit()
    con.close()
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": II.file_sha(db), "emb": {"qwen3": II.file_sha(p)}}, fh)
    prog = os.path.join(td, "programme.md")
    with open(prog, "w", encoding="utf-8") as fh:
        fh.write("intro\n%s fixture\n" % REG_HEADING)
    fx = {"td": td, "db": db, "pins": pins, "prog": prog, "mode": mode}
    fx["identity"] = _s0_identity(fx)
    fx["oracle"] = _oracle(fx)
    return fx


def _s0_identity(fx):
    """The fixture's identity target from S0's OWN c2 (and S0's GATE rule)."""
    CS = ITS.load_corpora(fx["db"])
    C = CS[CORPUS]
    with contextlib.redirect_stdout(io.StringIO()):
        vecs = ITS.load_vectors(ITS.emb_path("qwen3", fx["td"]), "qwen3", sorted(set(C.text[i] for i in np.nonzero(C.kept)[0])))
    S = ITS.Space(vecs, C, D)
    r = ITS.c2(C, {"qwen3": S, "nomic": S, "gemma": S})
    return {"per_seed": tuple("%.5f" % a for a in r["per_seed"]), "A_a": "%.5f" % r["supervised_A"], "fpr95": "%.4f" % r["fpr95"],
            "thr": "%.5f" % r["thr"]}


def _lw_oracle(Xc):
    """An INDEPENDENT Ledoit-Wolf (assume centred), written from the published estimator."""
    n, p = Xc.shape
    emp = Xc.T @ Xc / n
    mu = np.trace(emp) / p
    X2 = Xc ** 2
    beta_ = float((X2.T @ X2).sum())
    delta_ = float(((Xc.T @ Xc) ** 2).sum()) / n ** 2
    beta = (beta_ / n - delta_) / (p * n)
    delta = (delta_ - 2.0 * mu * np.trace(emp) + p * mu ** 2) / p
    beta = min(beta, delta)
    sh = 0.0 if beta == 0 else beta / delta
    cov = (1 - sh) * emp + sh * mu * np.eye(p)
    return np.linalg.inv(cov), sh


def _wauc(pos, neg, wp, wn):
    """Brute-force weighted Mann-Whitney (independent of S0's auroc)."""
    gt = (pos[:, None] > neg[None, :]).astype(np.float64) + 0.5 * (pos[:, None] == neg[None, :])
    return float((wp[:, None] * wn[None, :] * gt).sum() / (wp.sum() * wn.sum()))


def _oracle(fx, B=None):
    """INDEPENDENT recomputation: own sqlite read, own slice + renormalise, own side masks, own LW, own kNN, own AUROC, own weights
    (the same generator order); only S0's skmeans (same seeds) is shared."""
    CS = ITS.load_corpora(fx["db"])
    C = CS[CORPUS]
    con = sqlite3.connect(ITS.emb_path("qwen3", fx["td"]))
    raw = {t: np.frombuffer(b, dtype=">f4").astype(np.float64)[:D] for t, b in con.execute("SELECT query, vector FROM embeddings")}
    con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    m = lambda sd, o: [i for i in range(len(C.text)) if C.kept[i] and bool(C.oos[i]) == o and C.side[i] == sd]
    tr, gt, ein, eoos = m(SS.TRAIN, False), m(SS.GATE, False), m(SS.EVAL, False), m(SS.EVAL, True)
    X = lambda idx: U(np.array([raw[C.text[i]] for i in idx]))
    Xtr, Xg, Xi, Xo = X(tr), X(gt), X(ein), X(eoos)
    sc = {}
    for s in S0_SEEDS:
        Cm = ITS.skmeans(Xtr, II.GOLD_K[CORPUS][1], s)
        sc["s%d" % s] = [(Z @ Cm.T).max(1) for Z in (Xi, Xo, Xg)]
    lab = np.array([C.fine[i] for i in tr], dtype=str)
    ul = sorted(set(lab.tolist()))
    G = np.array([Xtr[lab == u].mean(0) for u in ul])
    Gn = U(G)
    sc["a"] = [(Z @ Gn.T).max(1) for Z in (Xi, Xo, Xg)]
    Rz = Xtr - np.array([G[ul.index(l)] for l in lab])
    Pb, shb = _lw_oracle(Rz)
    sc["b"] = [-np.array([min(float((z - g) @ Pb @ (z - g)) for g in G) for z in Z]) for Z in (Xi, Xo, Xg)]
    mu = Xtr.mean(0)
    Pd, shd = _lw_oracle(Xtr - mu)
    sc["d"] = [-np.array([float((z - mu) @ Pd @ (z - mu)) for z in Z]) for Z in (Xi, Xo, Xg)]
    sc["c"] = [np.array([np.sort(Xtr @ z)[::-1][KNN_K - 1] for z in Z]) for Z in (Xi, Xo, Xg)]
    one = lambda n: np.ones(n)
    A = {k: _wauc(v[0], v[1], one(len(v[0])), one(len(v[1]))) for k, v in sc.items()}
    A_s0 = np.array([A["s%d" % s] for s in S0_SEEDS])
    B = FX_B if B is None else B
    rng = np.random.default_rng(STREAM)
    ci = np.unique(C.comp[ein], return_inverse=True)[1]
    co = np.unique(C.comp[eoos], return_inverse=True)[1]
    dd = {b: [] for b in DET}
    for _ in range(B):
        wi = np.bincount(rng.integers(ci.max() + 1, size=ci.max() + 1), minlength=ci.max() + 1)[ci].astype(float)
        wo = np.bincount(rng.integers(co.max() + 1, size=co.max() + 1), minlength=co.max() + 1)[co].astype(float)
        s0m = np.mean([_wauc(sc["s%d" % s][0], sc["s%d" % s][1], wi, wo) for s in S0_SEEDS])
        for b in DET:
            dd[b].append(_wauc(sc[b][0], sc[b][1], wi, wo) - s0m)
    out = {"A": A, "mean_s0": float(A_s0.mean()), "var_seed": float(np.var(A_s0, ddof=1)), "shrink": (shb, shd), "det": {}}
    for b in DET:
        Dl = A[b] - out["mean_s0"]
        se = float(np.sqrt(np.std(dd[b], ddof=1) ** 2 + out["var_seed"] / 5))
        thr = float(np.sort(sc[b][2])[int(np.floor(0.05 * len(sc[b][2])))])
        if Dl - 1.645 * se > -0.010 and Dl + 1.645 * se < 0.010:
            st = "EQUIVALENT"
        elif abs(Dl) > 0.010 and (Dl - 1.96 * se > 0 or Dl + 1.96 * se < 0):
            st = "BASELINE-BETTER" if Dl > 0 else "S0-BETTER"
        else:
            st = "NEITHER"
        out["det"][b] = {"D": Dl, "se": se, "status": st, "fpr95": float(np.mean(sc[b][1] >= thr))}
    out["n"] = {"train": len(tr), "gate": len(gt), "in": len(ein), "oos": len(eoos)}
    return out


FX_B = 200


@contextlib.contextmanager
def _scope(fx):
    """Fixture scope: S0's fixture K (CLINC 16), the fixture's pins, no heavy process, B 200 (S0's too, so c2's draws stay comparable)."""
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], g["BOOT_B"], ITS.BOOT_B)
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        g["BOOT_B"] = FX_B
        ITS.BOOT_B = FX_B
        try:
            yield
        finally:
            g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], g["BOOT_B"], ITS.BOOT_B = saved


def make_fixtures(td):
    out = {}
    for mode in FX_MODES:
        d = os.path.join(td, mode)
        os.makedirs(d)
        with _scope(None):
            out[mode] = build_fixture(d, mode)
    return out


def _cap(fn):
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as ex:
            err = str(ex)
    return buf.getvalue(), err, res


def _line(out, prefix):
    lines = [ln[len(TAG) + 1:] if ln.startswith(TAG + " ") else ln for ln in out.splitlines()]
    got = [ln.lstrip() for ln in lines if ln.lstrip().startswith(prefix)]
    return got[-1] if got else ""


def _run(fx, tag, **kw):
    out_dir = os.path.join(fx["td"], "out_%s_%d" % (tag, len(os.listdir(fx["td"]))))
    args = dict(db=fx["db"], emb_dir=fx["td"], out_dir=out_dir, programme=fx["prog"], identity=fx["identity"])
    args.update(kw)
    with _scope(fx):
        o, err, res = _cap(lambda: main_run(**args))
    return o, err, res, out_dir


def selftest(only=None, quiet=False, fixture=None):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    if fixture is None:
        td = tempfile.mkdtemp(prefix="oob_st_")
        try:
            _selftest(sel, ok, td, make_fixtures(td))
        finally:
            shutil.rmtree(td, ignore_errors=True)
    else:
        _selftest(sel, ok, fixture[0], fixture[1])
    if not quiet:
        print("SELFTEST: %d checks passed" % n[0])
    return 0


def _syn(st, D=None):
    """A synthetic readout dict for the line printers (every branch)."""
    D = D or {"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0}
    det = {b: {"A": 0.97 + D[b], "D": D[b], "se": 0.002, "se_boot": 0.002, "lo90": D[b] - 0.0033, "hi90": D[b] + 0.0033, "lo95": D[b] - 0.004,
               "hi95": D[b] + 0.004, "status": st[b]} for b in DET}
    return {"det": det, "A_s0": np.array([0.97] * 5), "mean_s0": 0.97, "var_seed": 0.0}


def _selftest(sel, ok, td, FX):
    if sel("ST-CONST"):
        ok(MARGIN == 0.010 and (Z90, Z95, Z80P) == (1.645, 1.96, 0.842), "registered margin 0.010 and z 1.645 / 1.96 / 0.842")
        ok(KNN_K == 10 and KNN_DESC == (1, 5, 25, 50) and BOOT_B == 2000 and STREAM == ITS.BOOT_SEED + 2, "k 10 fixed; B 2,000; S0's C2 stream")
        ok(S0_SEEDS == (0, 1, 2, 3, 4) and D == 256 and TPR == 0.95, "S0 seeds 0-4, slice 256, TPR 0.95")
        ok(IDENTITY == {"per_seed": ("0.97437", "0.97263", "0.97601", "0.97446", "0.97649"), "A_a": "0.97640", "fpr95": "0.1578",
                        "thr": "0.74326"}, "registered identity digits")
        ok(RO.git_blob_lf(ITS.__file__) == ITS_BLOB, "ITS blob f662ceb1 (imported unchanged)")
        ok(PRED_POINT == {"a": 0.0016, "b": 0.007, "c": 0.002, "d": -0.030} and P_NUM["d"] == (-0.030, -0.080, 0.000), "registered points")
    if sel("ST-UNIT"):
        se = 0.002
        ok(ob_status(0.0, se) == "EQUIVALENT", "status: 0 +/- 1.645 x 0.002 inside -> EQUIVALENT")
        ok(ob_status(0.00670, se) == "EQUIVALENT" and ob_status(0.00672, se) == "NEITHER", "EQUIVALENT boundary 0.010 - 1.645 SE (0.00671)")
        ok(ob_status(0.0101, 0.001) == "BASELINE-BETTER" and ob_status(-0.0101, 0.001) == "S0-BETTER", "DIFFERENT both directions")
        ok(ob_status(0.0101, 0.0052) == "NEITHER", "|Delta| > 0.010 but the 95% interval reaches 0 -> NEITHER")
        ok(ob_status(0.009, 0.0001) == "EQUIVALENT" and ob_status(0.0099, 0.0001) == "NEITHER", "|Delta| <= 0.010 with a tight interval: never DIFFERENT")
        ok(ob_status(0.012, 0.0055) == "BASELINE-BETTER" and ob_status(0.012, 0.0062) == "NEITHER", "DIFFERENT uses 1.96, not 1.645")
        ok(ob_status(0.005, 0.003) == "EQUIVALENT" and ob_status(0.005, 0.003, margin=0.005) == "NEITHER", "EQUIVALENT uses 1.645 and the margin")
        ok(threshold(np.arange(100.0)) == 5.0 and threshold(np.arange(20.0)) == 1.0, "GATE rule: floor(0.05 n)-th smallest")
        Q = ITS.unit(_rng("q").normal(size=(7, 5)))
        T = ITS.unit(_rng("t").normal(size=(60, 5)))
        kn = knn_scores(Q, T, (1, 5, 10, 50), chunk=3)
        ok(all(np.allclose(kn[k], [np.sort(T @ q)[::-1][k - 1] for q in Q]) for k in (1, 5, 10, 50)), "kNN: k-th largest cos (chunked)")
        Xr = _rng("x").normal(size=(80, 6))
        Pp, sh = lw_precision(Xr)
        Po, sho = _lw_oracle(Xr)
        ok(np.allclose(Pp, Po) and abs(sh - sho) < 1e-12, "Ledoit-Wolf (assume centred) equals the independent estimator")
        fd = marginal_fit(Xr)
        ok(np.allclose(fd["mu"], Xr.mean(0)) and np.allclose(fd["P"], _lw_oracle(Xr - Xr.mean(0))[0]), "marginal fit: one mean, LW of x - mu")
        lab = np.array(["u", "v"] * 40)
        fb = class_fit(Xr, lab)
        M = np.array([Xr[lab == "u"].mean(0), Xr[lab == "v"].mean(0)])
        ok(np.allclose(fb["M"], M) and np.allclose(fb["P"], _lw_oracle(Xr - M[(lab == "v").astype(int)])[0]), "class fit: class means, LW of residuals")
        z = Xr[:5]
        ok(np.allclose(maha_min(z, M, fb["P"]), [min((x - m) @ fb["P"] @ (x - m) for m in M) for x in z]), "maha_min = the min over classes")
        ok(list(inspect.signature(marginal_fit).parameters) == ["X"], "marginal_fit takes the matrix only")
        o, err, _r = _cap(lambda: marginal_fit(np.array([["a", "b"]], dtype=object)))
        ok(err and "label column" in err, "marginal fit REFUSES a non-float input")
        ok(verdict_line(0.0016, 0.00288)[2] == "SCOREABLE (EQUIVALENT side)" and verdict_line(0.007, 0.00288)[2] == "DESCRIPTIVE-ONLY"
           and verdict_line(-0.030, 0.00374)[2] == "SCOREABLE (DIFFERENT side)", "verdict lines at the registered SEs (a / b / d as registered)")
        ok(abs(verdict_line(0, 0.00288)[0] - 0.00284) < 1e-4 and abs(verdict_line(0, 0.00374)[1] - 0.01315) < 1e-4, "reach 0.00284 / 0.01315 as registered")
        ok(abs(brier(0.7, True) - 0.09) < 1e-12 and abs(brier(0.7, np.bool_(False)) - 0.49) < 1e-12, "Brier on numpy bools")
        ok(_hit(0.5, 0.5, 0.6) and _hit(0.6, 0.5, 0.6) and not _hit(0.61, 0.5, 0.6), "numeric HELD on the closed interval")
    if sel("ST-READ"):
        E, BB, SB, NE = "EQUIVALENT", "BASELINE-BETTER", "S0-BETTER", "NEITHER"
        cases = [({"a": E, "b": E, "c": E, "d": E}, ("GEOMETRY-CARRIES", "COMPETITIVE"), False),
                 ({"a": NE, "b": BB, "c": NE, "d": BB}, ("CELLS-NOT-BEST", "LABELS-HELP"), True),
                 ({"a": BB, "b": NE, "c": BB, "d": SB}, ("CELLS-NOT-BEST", "LABELS-HELP"), True),
                 ({"a": E, "b": NE, "c": SB, "d": SB}, ("CELLS-ADD", "NOT-SHOWN"), False),
                 ({"a": NE, "b": E, "c": SB, "d": E}, ("GEOMETRY-CARRIES", "NOT-SHOWN"), False),
                 ({"a": E, "b": E, "c": NE, "d": SB}, ("NOT-SHOWN", "COMPETITIVE"), False),
                 ({"a": SB, "b": SB, "c": E, "d": NE}, ("NOT-SHOWN", "NOT-SHOWN"), False),
                 ({"a": BB, "b": E, "c": E, "d": E}, ("GEOMETRY-CARRIES", "LABELS-HELP"), True),
                 ({"a": E, "b": E, "c": BB, "d": E}, ("CELLS-NOT-BEST", "COMPETITIVE"), True),
                 ({"a": E, "b": BB, "c": SB, "d": SB}, ("CELLS-ADD", "LABELS-HELP"), True)]
        for st, want, fires in cases:
            ok(readings(st) == want, "reading %s -> %s" % (st, want))
            L = criteria_lines(_syn(st, {b: (0.02 if st[b] == BB else -0.02 if st[b] == SB else 0.0) for b in DET}))
            txt = "\n".join(L)
            ok(("READING: %s / %s" % want) in txt, "printed READING %s / %s" % want)
            ok(("F-OB: FIRED" in txt) == fires and ("F-OB: NOT FIRED" in txt) == (not fires), "F-OB %s printed" % ("FIRED" if fires else "NOT FIRED"))
            ok(("F-OB (like-for-like)" in txt) == (st["c"] == BB or st["d"] == BB), "F-OB like-for-like sentence iff fired through a peer")
            ok(("GEOMETRY BAR" in txt) == (st["d"] == E), "GEOMETRY BAR line iff OB-d EQUIVALENT")
            for b in DET:
                ok(("OB-%s: %s " % (b, st[b])) in txt, "OB-%s %s printed" % (b, st[b]))
            ok(all(QUALIFIER in ln for ln in L if ln.startswith("  LIKE") or ln.startswith("  LABEL")), "every reading sentence carries the qualifier")
        txt = "\n".join(criteria_lines(_syn({"a": NE, "b": NE, "c": BB, "d": BB}, {"a": 0, "b": 0, "c": 0.031, "d": 0.042})))
        ok("label-free kNN score beats label-free cells for OOS by +0.03100" in txt and "marginal Mahalanobis score beats label-free cells for OOS by +0.04200" in txt,
           "CELLS-NOT-BEST sentence per peer with its Delta")
        txt = "\n".join(criteria_lines(_syn({"a": BB, "b": BB, "c": NE, "d": NE}, {"a": 0.021, "b": 0.033, "c": 0, "d": 0})))
        ok("labels buy +0.02100 AUROC" in txt and "labels buy +0.03300 AUROC" in txt and "reaches A = 0.99100" in txt, "LABELS-HELP per labelled baseline; F-OB quotes A")
        RDs = _syn({"a": E, "b": BB, "c": NE, "d": SB}, {"a": 0.001, "b": 0.012, "c": 0.003, "d": -0.031})
        fl = {b: {"fpr95": v} for b, v in zip(DET, (0.15, 0.30, 0.10, 0.60))}
        P = "\n".join(predictions_lines(RDs, fl))
        ok("P2 Delta_b +0.01200 vs +0.007 [-0.006, +0.018]: HELD; status BASELINE-BETTER" in P, "P2 HELD branch with status")
        ok("P3 Delta_c +0.00300 vs +0.002 [-0.006, +0.008]: HELD" in P and "P4 Delta_d -0.03100 vs -0.030 [-0.080, +0.000]: HELD" in P, "P3 / P4 HELD")
        ok("BASELINE-BETTER 0.4900" in P and "S0-BETTER 0.1600" in P, "status Briers: P2 BB (0.30 - 1)^2, P4 S0B (0.60 - 1)^2")
        ok("P5 FPR95 (b) 0.3000 vs 0.13 [0.07, 0.22]: FAILED" in P and "P5 FPR95 (a) 0.1500 vs 0.15 [0.10, 0.20]: HELD" in P, "P5 both branches")
        ok("P6 SE_total(OB-a) 0.00200 < 0.0015: event False" in P and "P1 Delta_a +0.00100" in P and "event True, Brier 0.0025" in P, "P1 / P6 lines")
        ok("P4' like reading NOT-SHOWN" in P and "P4' label reading LABELS-HELP" in P, "P4' readings scored")
        RDs2 = _syn({"a": NE, "b": NE, "c": NE, "d": NE}, {"a": 0.02, "b": -0.02, "c": 0.02, "d": 0.01})
        P = "\n".join(predictions_lines(RDs2, fl))
        ok("P2 Delta_b -0.02000 vs +0.007 [-0.006, +0.018]: FAILED" in P and "P3 Delta_c +0.02000" in P and "P4 Delta_d +0.01000 vs -0.030 [-0.080, +0.000]: FAILED" in P,
           "numeric FAILED branches")
        ok("event False, Brier 0.9025" in P, "P1 OB-a not EQUIVALENT: Brier 0.9025")
    # ---------------------------------------------------------------- end-to-end on the fixtures
    for mode in FX_MODES:
        fx = FX[mode]
        orc = fx["oracle"]
        key = "ST-E2E-" + mode
        if not sel(key):
            continue
        o, err, res, out_dir = _run(fx, "e2e")
        ok(err is None, "%s: --run completes (%s)" % (mode, err))
        X, L, po = res
        txt = open(po, encoding="utf-8").read()
        ok(txt.splitlines() == L, "%s: the file of record is the printed lines" % mode)
        for b in DET:
            r = X["RD"]["det"][b]
            ok(abs(r["D"] - orc["det"][b]["D"]) < 1e-12, "%s OB-%s Delta %+.6f = oracle %+.6f" % (mode, b, r["D"], orc["det"][b]["D"]))
            ok(abs(r["se"] - orc["det"][b]["se"]) < 1e-9, "%s OB-%s SE_total %.6f = oracle %.6f (paired, var_seed / 5)" % (mode, b, r["se"], orc["det"][b]["se"]))
            ok(r["status"] == orc["det"][b]["status"], "%s OB-%s status %s = oracle" % (mode, b, r["status"]))
            ln = ([x for x in L if x.startswith("OB-%s: " % b)] or [""])[0]
            ok(ln.startswith("OB-%s: %s (Delta %+.5f" % (b, orc["det"][b]["status"], orc["det"][b]["D"])), "%s printed OB-%s value %s" % (mode, b, ln[:60]))
            ok(abs(X["fl"][b]["fpr95"] - orc["det"][b]["fpr95"]) < 1e-12, "%s FPR95 (%s) at its own GATE threshold = oracle" % (mode, b))
        ok(abs(X["RD"]["mean_s0"] - orc["mean_s0"]) < 1e-12 and abs(X["RD"]["var_seed"] - orc["var_seed"]) < 1e-15, "%s S0 seed mean / var_seed = oracle" % mode)
        ok(abs(X["meta"]["shrink_b"] - orc["shrink"][0]) < 1e-9 and abs(X["meta"]["shrink_d"] - orc["shrink"][1]) < 1e-9, "%s LW shrinkage = oracle" % mode)
        like, label = readings({b: orc["det"][b]["status"] for b in DET})
        ok(_line(o, "READING: ") == "READING: %s / %s" % (like, label), "%s printed READING %s / %s" % (mode, like, label))
        ok(_line(o, "CENSUS").find("EVAL OOS n_OOS %d" % orc["n"]["oos"]) > 0 and _line(o, "CENSUS").find("TRAIN in-scope %d" % orc["n"]["train"]) > 0,
           "%s census denominators = oracle (OOS %d, TRAIN %d)" % (mode, orc["n"]["oos"], orc["n"]["train"]))
        aud = _line(o, "TRAIN-ONLY:")
        ok(", 0 with an EVAL row, 0 OOS rows" in aud, "%s fit audit: no EVAL / OOS row in any fit (%s)" % (mode, aud[:60]))
        ok(any(f[0] == "OB (d) marginal Mahalanobis" and f[3] == (SS.TRAIN,) for f in ITS.FIT_LOG), "%s (d) fitted on TRAIN only" % mode)
        ok(sum(1 for f in ITS.FIT_LOG if f[3] == (SS.GATE,)) == 6, "%s GATE read only for thresholds (c2's 5 + this script's 1)" % mode)
        ok(EVENTS[:2] == [("IDENTITY", "ok"), ("BASELINES", "scored")], "%s identity precedes any baseline score" % mode)
        for need in ("THE ASYMMETRY (registered)", "CLINC150 SPLIT (registered)", "WHAT THIS RESULT WILL NOT SHOW", "IDENTITY:", "== PREDICTIONS",
                     "P6 SE_total(OB-a)", "F-OB: ", "S0 C2 HELD and F2 NOT FIRED stand", "builder's readings: OB1"):
            ok(need in txt, "%s outcome carries %r" % (mode, need))
        ok(os.path.isfile(os.path.join(out_dir, SCORES_CSV)), "%s scores CSV written" % mode)
        with open(os.path.join(out_dir, SCORES_CSV), encoding="utf-8") as fh:
            rr = list(csv.DictReader(fh))
        ok(sum(1 for r in rr if r["role"] == "EVAL_OOS") == orc["n"]["oos"] and sum(1 for r in rr if r["role"] == "EVAL_IN") == orc["n"]["in"], "%s CSV rows" % mode)
        o2, err2, _r2, _d = _run(fx, "again", out_dir=out_dir)
        ok(err2 and "write-once" in err2, "%s a second --run into the same directory REFUSES (write-once)" % mode)
        if mode == "P":
            ok(all(orc["det"][b]["status"] == "EQUIVALENT" for b in DET) and like == "GEOMETRY-CARRIES" and label == "COMPETITIVE",
               "P: planted answer EQUIVALENT x 4 -> GEOMETRY-CARRIES / COMPETITIVE")
            ok(_line(o, "F-OB: ").startswith("F-OB: NOT FIRED") and "GEOMETRY BAR" in txt, "P: F-OB NOT FIRED, GEOMETRY BAR printed")
        if mode == "W":
            ok(orc["det"]["b"]["status"] == "BASELINE-BETTER" and orc["det"]["d"]["status"] == "BASELINE-BETTER", "W: planted (b), (d) BASELINE-BETTER")
            ok(like == "CELLS-NOT-BEST" and label == "LABELS-HELP" and _line(o, "F-OB: ").startswith("F-OB: FIRED"), "W: CELLS-NOT-BEST / LABELS-HELP, F-OB FIRED")
            ok("F-OB (like-for-like)" in txt, "W: fired through a peer")
        if mode == "C":
            ok(orc["det"]["d"]["status"] == "S0-BETTER", "C: planted (d) S0-BETTER (OOS at the marginal mean)")
    if sel("ST-REFUSE"):
        fx = FX["P"]
        o, err, _r, _d = _run(fx, "idbad", identity=dict(fx["identity"], A_a="0.99999"))
        ok(err and "IDENTITY PRECONDITION FAILED" in err and not os.path.exists(os.path.join(_d, OUTCOME)), "identity mismatch REFUSES; nothing written")
        bad = dict(fx["identity"])
        bad["per_seed"] = tuple(list(bad["per_seed"][:4]) + ["0.00000"])
        o, err, _r, _d = _run(fx, "idseed", identity=bad)
        ok(err and "per_seed" in err, "identity on the 5th seed checked (all seeds, not the first)")
        o, err, _r, _d = _run(fx, "idthr", identity=dict(fx["identity"], thr="0.00000"))
        ok(err and "thr" in err, "identity threshold checked")
        o, err, _r, _d = _run(fx, "idfpr", identity=dict(fx["identity"], fpr95="0.9999"))
        ok(err and "fpr95" in err, "identity FPR95 checked")
        prog2 = os.path.join(fx["td"], "prog_quoted.md")
        with open(prog2, "w", encoding="utf-8") as fh:
            fh.write("a quotation: %s\n" % REG_HEADING)
        o, err, _r, _d = _run(fx, "noreg", programme=prog2)
        ok(err and "registration heading is absent" in err, "a quoted (not line-anchored) heading REFUSES")
        pins = json.load(open(fx["pins"]))
        p2 = os.path.join(fx["td"], "pins_null.json")
        pins["emb"]["qwen3"] = None
        json.dump(pins, open(p2, "w"))
        fx2 = dict(fx, pins=p2)
        o, err, _r, _d = _run(fx2, "nullpin")
        ok(err and "UNPINNED" in err, "--run REFUSES a null qwen3 pin")
        g = globals()
        saved = g["_foreign_heavy"]
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ["java.exe 1234"]
            try:
                o, err, _r = _cap(lambda: main_run(db=fx["db"], emb_dir=fx["td"], out_dir=os.path.join(fx["td"], "heavy_%d" % len(os.listdir(fx["td"]))), programme=fx["prog"],
                                                   identity=fx["identity"]))
            finally:
                g["_foreign_heavy"] = saved
        ok(err and "foreign heavy process" in err, "--run REFUSES beside a JVM")
    if sel("ST-DRY"):
        fx = FX["W"]
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=fx["identity"], timing=True))
        ok(err is None, "dry-run completes (%s)" % err)
        orc = fx["oracle"]
        ok("DENOMINATORS vs registration: n_in %d (registered 6672) DIFFERENT; n_OOS %d (registered 1350) DIFFERENT" % (orc["n"]["in"], orc["n"]["oos"]) in o,
           "dry-run prints the denominators against the registration")
        ok("-> REPRODUCED" in o and "DRY RUN complete: nothing written" in o, "dry-run identity printed; nothing written")
        ok(not any(f[0].startswith("OB (") for f in ITS.FIT_LOG), "dry-run scores no baseline on EVAL (no (a)-(d) fit logged)")
        ok(all(fn not in os.listdir(fx["td"]) for fn in (OUTCOME, SCORES_CSV)), "dry-run leaves no outcome file")


MUTANTS = (
    ("margin 0.02", "MARGIN = 0.010\n", "MARGIN = 0.020\n", ("ST-CONST",)),
    ("z90 = 1.96 (EQUIVALENT at 95%)", "    if lo90 > -m and hi90 < m:\n", "    if lo95 > -m and hi95 < m:\n", ("ST-UNIT",)),
    ("DIFFERENT point clause dropped", "    if abs(Dl) > m and (lo95 > 0 or hi95 < 0):\n", "    if (lo95 > 0 or hi95 < 0):\n", ("ST-UNIT",)),
    ("DIFFERENT at 90%", "    if abs(Dl) > m and (lo95 > 0 or hi95 < 0):\n", "    if abs(Dl) > m and (lo90 > 0 or hi90 < 0):\n", ("ST-UNIT",)),
    ("direction flipped", "        return \"BASELINE-BETTER\" if Dl > 0 else \"S0-BETTER\"\n", "        return \"BASELINE-BETTER\" if Dl < 0 else \"S0-BETTER\"\n", ("ST-UNIT",)),
    ("Delta against seed 0 instead of the seed mean", "        Dl = A - mean_s0\n", "        Dl = A - float(A_s0[0])\n", ("ST-E2E-W", "ST-E2E-C")),
    ("seed term dropped", "        se = float(np.sqrt(se_boot ** 2 + var_seed / len(S0_SEEDS)))\n", "        se = float(np.sqrt(se_boot ** 2))\n", ("ST-E2E-W", "ST-E2E-C")),
    ("seed term var_seed (not / 5)", "        se = float(np.sqrt(se_boot ** 2 + var_seed / len(S0_SEEDS)))\n", "        se = float(np.sqrt(se_boot ** 2 + var_seed))\n", ("ST-E2E-W", "ST-E2E-C")),
    ("var_seed ddof 0", "    var_seed = float(np.var(A_s0, ddof=1))\n", "    var_seed = float(np.var(A_s0))\n", ("ST-E2E-W", "ST-E2E-C")),
    ("unpaired bootstrap (baseline draw minus S0 point)", "        dd = draws[b] - s0_draw_mean\n", "        dd = draws[b] - mean_s0\n", ("ST-E2E-W", "ST-E2E-C")),
    ("unpaired weights (fresh stream per score)", "            draws[k].append(ITS.auroc(allsc[k][\"in\"], allsc[k][\"oos\"], wi, wo))\n",
     "            draws[k].append(ITS.auroc(allsc[k][\"in\"], allsc[k][\"oos\"], np.random.default_rng(len(draws[k]) + len(k)).permutation(wi), wo))\n", ("ST-E2E-W", "ST-E2E-C")),
    ("bootstrap not stratified (OOS weights reuse in-scope stream order)", "    for wi, wo in zip(ITS.comp_weights(C.comp[R[\"in\"]], B, rng), ITS.comp_weights(C.comp[R[\"oos\"]], B, rng)):\n",
     "    for wo, wi in zip(ITS.comp_weights(C.comp[R[\"oos\"]], B, rng), ITS.comp_weights(C.comp[R[\"in\"]], B, rng)):\n", ("ST-E2E-W", "ST-E2E-C")),
    ("SE from ddof 0", "        se_boot = float(np.std(dd, ddof=1))\n", "        se_boot = float(np.std(dd))\n", ("ST-E2E-W", "ST-E2E-C")),
    ("an OOS row in the (d) fit", "    fd = marginal_fit(S.X[tr_d])\n", "    fd = marginal_fit(S.X[np.concatenate([tr_d, R[\"oos\"]])])\n", ("ST-E2E-W", "ST-E2E-C")),
    ("an OOS row through fit_rows", "    tr_d = ITS.fit_rows(C, R[\"train\"], (SS.TRAIN,), \"OB (d) marginal Mahalanobis\")\n",
     "    tr_d = ITS.fit_rows(C, np.concatenate([R[\"train\"], R[\"oos\"]]), (SS.TRAIN, SS.EVAL), \"OB (d) marginal Mahalanobis\")\n", ("ST-E2E-P",)),
    ("EVAL in the class Mahalanobis fit", "    fb = class_fit(S.X[tr_b], C.fine[tr_b])\n",
     "    fb = class_fit(S.X[np.concatenate([tr_b, R[\"in\"]])], C.fine[np.concatenate([tr_b, R[\"in\"]])])\n", ("ST-E2E-W", "ST-E2E-C")),
    ("marginal fit takes labels", "def marginal_fit(X):\n", "def marginal_fit(X, labels=None):\n", ("ST-UNIT",)),
    ("marginal = class Mahalanobis (labels used)", "        out.setdefault(\"d\", {})[k] = -maha_one(X, fd[\"mu\"], fd[\"P\"])\n",
     "        out.setdefault(\"d\", {})[k] = -maha_min(X, fb[\"M\"], fb[\"P\"])\n", ("ST-E2E-C", "ST-E2E-W")),
    ("threshold from EVAL", "def fpr_line(sc):\n    thr = threshold(sc[\"gate\"])\n", "def fpr_line(sc):\n    thr = threshold(sc[\"in\"])\n", ("ST-E2E-W", "ST-E2E-C")),
    ("threshold 90% TPR", "    return float(np.sort(sg)[int(np.floor((1 - TPR) * len(sg)))])\n", "    return float(np.sort(sg)[int(np.floor(0.10 * len(sg)))])\n", ("ST-UNIT",)),
    ("k selected on EVAL (best of the k grid)", "        out.setdefault(\"c\", {})[k] = kn[KNN_K]\n",
     "        out.setdefault(\"c\", {})[k] = kn[max(ks, key=lambda q: ITS.auroc(knn_scores(S.X[R['in']], S.X[tr_c], (q,))[q], knn_scores(S.X[R['oos']], S.X[tr_c], (q,))[q]))]\n",
     ("ST-E2E-W", "ST-E2E-C", "ST-E2E-P")),
    ("k = 1", "KNN_K = 10\n", "KNN_K = 1\n", ("ST-CONST",)),
    ("kNN max instead of k-th (min<->max)", "            out[k][a:a + chunk] = top[:, k - 1]\n", "            out[k][a:a + chunk] = top[:, 0]\n", ("ST-UNIT",)),
    ("class Mahalanobis max over classes (min<->max)", "    return d.min(1)\n", "    return d.max(1)\n", ("ST-UNIT",)),
    ("Mahalanobis sign (higher = OOS)", "        out.setdefault(\"b\", {})[k] = -maha_min(X, fb[\"M\"], fb[\"P\"])\n",
     "        out.setdefault(\"b\", {})[k] = maha_min(X, fb[\"M\"], fb[\"P\"])\n", ("ST-E2E-W",)),
    ("unshrunk used for (d)", "        out.setdefault(\"d\", {})[k] = -maha_one(X, fd[\"mu\"], fd[\"P\"])\n",
     "        out.setdefault(\"d\", {})[k] = -maha_one(X, fd[\"mu\"], fd[\"P0\"])\n", ("ST-E2E-W", "ST-E2E-C")),
    ("LW not assume_centered", "    lw = LedoitWolf(assume_centered=True).fit(R)\n", "    lw = LedoitWolf(assume_centered=False).fit(R + 0.5)\n", ("ST-UNIT",)),
    ("class means renormalised", "    M = np.array([X[inv == j].mean(0) for j in range(len(u))])\n", "    M = ITS.unit(np.array([X[inv == j].mean(0) for j in range(len(u))]))\n", ("ST-UNIT",)),
    ("reading: CELLS-ADD needs only one peer", "    elif st[\"c\"] == \"S0-BETTER\" and st[\"d\"] == \"S0-BETTER\":\n", "    elif st[\"c\"] == \"S0-BETTER\" or st[\"d\"] == \"S0-BETTER\":\n", ("ST-READ",)),
    ("reading order: GEOMETRY before CELLS-NOT-BEST", "    if st[\"c\"] == \"BASELINE-BETTER\" or st[\"d\"] == \"BASELINE-BETTER\":\n        like = \"CELLS-NOT-BEST\"\n",
     "    if st[\"d\"] == \"EQUIVALENT\":\n        like = \"GEOMETRY-CARRIES\"\n    elif st[\"c\"] == \"BASELINE-BETTER\" or st[\"d\"] == \"BASELINE-BETTER\":\n        like = \"CELLS-NOT-BEST\"\n", ("ST-READ",)),
    ("COMPETITIVE needs only OB-a", "    elif st[\"a\"] == \"EQUIVALENT\" and st[\"b\"] == \"EQUIVALENT\":\n", "    elif st[\"a\"] == \"EQUIVALENT\":\n", ("ST-READ",)),
    ("LABELS-HELP from OB-a only", "    if st[\"a\"] == \"BASELINE-BETTER\" or st[\"b\"] == \"BASELINE-BETTER\":\n        label = \"LABELS-HELP\"\n",
     "    if st[\"a\"] == \"BASELINE-BETTER\":\n        label = \"LABELS-HELP\"\n", ("ST-READ",)),
    ("F-OB only through the peers", "    via = [b for b in DET if st[b] == \"BASELINE-BETTER\"]\n", "    via = [b for b in (\"c\", \"d\") if st[b] == \"BASELINE-BETTER\"]\n", ("ST-READ",)),
    ("F-OB identity-tested (never fires on numpy bool)", "    if fired:\n        L.append(\"F-OB: FIRED", "    if fired is np.True_:\n        L.append(\"F-OB: FIRED", ("ST-READ",)),
    ("GEOMETRY BAR line omitted", "    if st[\"d\"] == \"EQUIVALENT\":\n        L.append(\"GEOMETRY BAR", "    if False:\n        L.append(\"GEOMETRY BAR", ("ST-READ",)),
    ("like-for-like F-OB sentence omitted", "        if any(b in (\"c\", \"d\") for b in via):\n", "        if False:\n", ("ST-READ",)),
    ("P2 interval open", "    return bool(lo <= v <= hi)\n", "    return bool(lo < v < hi)\n", ("ST-UNIT",)),
    ("P6 event flipped", "bool(se_a < P6[0]), P6[1], brier(P6[1], se_a < P6[0])", "bool(se_a > P6[0]), P6[1], brier(P6[1], se_a > P6[0])", ("ST-READ",)),
    ("Brier on the complement", "    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2\n", "    return (float(p) - (0.0 if bool(event) else 1.0)) ** 2\n", ("ST-UNIT",)),
    ("identity checks the first seed only", "    bad = [k for k in (\"per_seed\", \"A_a\", \"fpr95\", \"thr\") if got[k] != target[k]]\n",
     "    bad = [k for k in (\"A_a\", \"fpr95\", \"thr\") if got[k] != target[k]] + ([\"per_seed\"] if got[\"per_seed\"][0] != target[\"per_seed\"][0] else [])\n", ("ST-REFUSE",)),
    ("identity skipped", "    idline = identity_check(identity_values(c2r, s0, A_a, f0), identity)\n", "    idline = \"IDENTITY: skipped\"\n", ("ST-REFUSE", "ST-E2E-P")),
    ("baselines scored before the identity", "    idline = identity_check(identity_values(c2r, s0, A_a, f0), identity)\n    EVENTS.append((\"IDENTITY\", \"ok\"))\n    bs, meta = baseline_scores(C, S, R)\n    EVENTS.append((\"BASELINES\", \"scored\"))\n",
     "    bs, meta = baseline_scores(C, S, R)\n    EVENTS.append((\"BASELINES\", \"scored\"))\n    idline = identity_check(identity_values(c2r, s0, A_a, f0), identity)\n    EVENTS.append((\"IDENTITY\", \"ok\"))\n", ("ST-E2E-P",)),
    ("outcome opened 'w' (not write-once)", "    for p in out_paths(out_dir):\n        if os.path.lexists(p):\n            refuse(", "    for p in out_paths(out_dir):\n        if False:\n            refuse(", ("ST-E2E-P",)),
    ("registration check not line-anchored", "REG_RE = re.compile(r\"^\" + re.escape(REG_HEADING), re.M)\n", "REG_RE = re.compile(re.escape(REG_HEADING))\n", ("ST-REFUSE",)),
    ("non-strict pins on --run", "    sha0, C, S = load_inputs(db, emb_dir, strict=True)\n", "    sha0, C, S = load_inputs(db, emb_dir, strict=False)\n", ("ST-REFUSE",)),
    ("heavy check dropped from --run", "        refuse(\"the registration heading is absent from %s: --run reads only a registered test\" % programme)\n    heavy_check()\n",
     "        refuse(\"the registration heading is absent from %s: --run reads only a registered test\" % programme)\n", ("ST-REFUSE",)),
    ("OOS denominator = EVAL hash side only (wrong population)", "            \"oos\": ITS.S_idx(C, S, SS.EVAL, oos=True)}\n",
     "            \"oos\": np.array([i for i in ITS.S_idx(C, S, SS.EVAL, oos=True) if C.hash_side[i] == SS.EVAL], dtype=int)}\n", ("ST-E2E-P", "ST-E2E-W")),
    ("in-scope from GATE (wrong split side)", "    return {\"train\": ITS.S_idx(C, S, SS.TRAIN), \"gate\": ITS.S_idx(C, S, SS.GATE), \"in\": ITS.S_idx(C, S, SS.EVAL),\n",
     "    return {\"train\": ITS.S_idx(C, S, SS.TRAIN), \"gate\": ITS.S_idx(C, S, SS.GATE), \"in\": ITS.S_idx(C, S, SS.GATE),\n", ("ST-E2E-P", "ST-E2E-W")),
    ("P5 FPR95 scored on (a) only", "    for b in DET:\n        p, lo, hi = P_FPR[b]\n", "    for b in DET[:1]:\n        p, lo, hi = P_FPR[b]\n", ("ST-READ",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="oob_mut_")
    fx = make_fixtures(td)
    killed = 0
    rows_ = []
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        code = head.replace(old, new)
        ns = {"__name__": "oob_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests) if tests else None, quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:100])
        killed += res.startswith("KILLED")
        rows_.append((name, res))
        print("  %-62s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="OOS-BASELINES (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-timing", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(a.db, a.emb_dir, timing=not a.no_timing)
    main_run(a.db, a.emb_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
