"""TREE-LIKE readout (docs/judge_v2_program.md, "## Registered 2026-10-04 (before any code or call) -- TREE-LIKE: does the
embedding space have hierarchy beyond its covariance (Gromov delta, ultrametricity, cophenetic correlation as z-scores against the
moment-matched Gaussian null), with a planted-hierarchy positive control?", L24362-L24373, registration commit 633255f2;
docs/agents/results/TREE-LIKE.json). ZERO LLM calls; CPU only; labels never read.

POOL: the intent arms (--run, the readout of record) read NO pool: the six intent_emb_*.db and intent_transfer_corpora_v1.db only
(rule 7 does not bind). The MMLU-Pro arm (--mmlu, DESCRIPTIVE, its own write-once file) IS A POOL READER under rule 7: it reads
embeddings_cache.db and the v2 side export (pool pv2_41dbd3dbcd399df0 recomputed and printed first); run it in a pool slot only.

LAUNCH SEQUENCE (zero calls; temp only under E: via scratch_dir; every DB is COPIED (db + -wal) into the process's scratch dir
before it is read: zc_common.stage_db):
  python tools/analysis/tree_like.py --selftest          # fixture worlds; value-asserting against an independent reference
  python tools/analysis/tree_like.py --mutants           # the mutant table (copies in a sandbox; the file is never edited)
  python tools/analysis/tree_like.py --dry-run           # pins, staged copies, census, IDENTITY PRECONDITION, a timed draw, price
  python tools/analysis/tree_like.py --run               # the readout of record (intent arms); WRITE-ONCE outcome on E:
  python tools/analysis/tree_like.py --dry-run --mmlu    # MMLU-Pro descriptive arm (POOL READER): pins, census, price
  python tools/analysis/tree_like.py --run --mmlu        # MMLU-Pro descriptive file (write-once, separate path)
      --out <path>        default E:/TaxoArena_backup_<date>_tree_like[_mmlu]/tree_like[_mmlu]_outcome.txt; an existing path REFUSES
      --data-root <dir>   where the DBs live (default: the checkout holding this script)

INPUTS (read-only; staged copies; sha256 of the file bytes against the registrar's pins, a mismatch REFUSES):
  intent_emb_{qwen3, qwen3_q8, qwen3_card, gemma, gemma_card, nomic}.db (pins: experiment_configs/intent_transfer_s0_pins.json
  emb, embed_quant_pins.json q8, card_protocol_pins.json); intent_transfer_corpora_v1.db (ingest_db pin). Rows: MASSIVE and CLINC,
  side TRAIN, kept (drop_reason NULL), in-scope (no OOS), through intent_transfer_s0.load_corpora / Corpus.idx (blob-pinned).
  --mmlu: embeddings_cache.db (qwen3, 4096), experiment_results/embedder_cross/embeddings_cache_{embeddinggemma,nomic-embed-text}
  _latest.db (gemma / nomic RAW; pins experiment_configs/embedder_cross_arm_pins.json), mmlu_pro_dataset_cache_v2.db (mmlu_pro.question
  only), the v2 side export (v2_engine_pool.read_side; TRAIN of draw 5a3e756).

INSTRUMENT (registration, verbatim in the code).
  Per arm x corpus x width (native; 256 = the first 256 coordinates, renormalised): 5 subsamples of 2,000 TRAIN points
  (subsample i: numpy default_rng(20261004 + i).choice(n_TRAIN, 2000, replace=False), the same items for every arm).
  Angular distance D = arccos(clip(x . y)). delta_rel = 2 delta / diam, delta = the four-point-condition maximum over 10^6
  sampled quadruples (Khrulkov's estimator; quadruple indices default_rng([20261004, 7, corpus, i]), distinct within a quadruple),
  diam = max D. Ultrametricity index = share of the triangles (the first three points of each quadruple) whose two largest sides
  agree within 2% ((c - b) <= 0.02 c). Cophenetic correlation of average-link (scipy). Each statistic as a z-score against
  B = 200 draws of the moment-matched null: siteNull's generator withinNodeCloud (SeparationNullBySizeTest.kt L558-L577) in numpy,
  out = mu + sum_c (g_c / sqrt(m)) c over the subsample's centred rows, unit-normalised (null draw b: default_rng([20261004,
  corpus, i, b]); common random numbers across arms); z = (obs - mean(null)) / SD(null, ddof 1).
  IDENTITY PRECONDITION (every --dry-run / --run, before any data is read; REFUSES otherwise): the numpy generator, fed the
  Gaussians of a Python clone of java.util.Random, reproduces the COMPILED Kotlin withinNodeCloud's outputs (mix_lrt_site's
  JVM_FIXTURE, two fixture sites, blob-pinned below) to 1e-12, and the literal transcription reproduces them bit for bit.
  POSITIVE CONTROL (TL0): per corpus and subsample, a planted 3-level hierarchical vMF mixture with the deciding arm's spectrum:
  3 x 3 x 3 = 27 leaf directions unit(mu + 1.0 u1 + 0.5 u2 + 0.25 u3), every u a draw from N(0, the subsample's covariance)
  (one per node of the planted tree), points round-robin over the leaves, each from a von Mises-Fisher (Wood 1994) around its leaf
  with kappa = (d - 1) / (theta3 / 2)^2, theta3 = the median angle between level-3 siblings (default_rng([20261004, 99, corpus,
  i])); scored like the data against its own moment-matched null (draws default_rng([20261004, 98, corpus, i, b])).
  NEGATIVE CONTROL (descriptive): null draw 0 of each subsample scored against draws 1..199.

CRITERIA (registered; every branch printed and executed by the selftest).
  TL0 (gate): PASS iff the positive control reaches z(delta_rel) < -2 in >= 4 of 5 subsamples on BOTH corpora; else TL1 reads
      NOT EVALUABLE.
  TL1 (DECIDING; qwen3 q4 = intent_emb_qwen3.db, native width 4096): per corpus TREE-LIKE iff z(delta_rel) < -2 in >= 4 of 5;
      TL1 = TREE-LIKE iff on both MASSIVE and CLINC; NOT-TREE-LIKE iff on neither; MIXED otherwise.
  F-TL fires iff TL1 reads NOT-TREE-LIKE.
  P1 TL0 PASS at 0.85. P2 MASSIVE TREE-LIKE 0.60, CLINC TREE-LIKE 0.60; TL1 TREE-LIKE 0.45 / MIXED 0.30 / NOT-TREE-LIKE 0.25
  (one Brier per event; not scored when TL1 is NOT EVALUABLE). P3 TL2 ordering agrees at 0.70 (descriptive; TT-R2).
SUPPORT (registered (a)-(f) quoted): 5 subsamples x 2,000 points per corpus; z against 200 null draws; DEFF 1.0; n_eff 5 per
  corpus; the reference mean's own SE 1 / sqrt(200) = 0.07 in z units; a classification over 5 subsamples; SCOREABLE conditional
  on TL0. Printed beside: the realised null SD and the mean / min / max z per cell.
DESCRIPTIVE: TL2, the ordering across arms (mean z(delta_rel) over subsamples) against the record's leaf counts (qwen3 M-AF 84 >
  gemma 4); every other arm and the 256-d widths; ultrametricity, cophenetic and mean-delta z-scores; the negative control;
  MMLU-Pro (--mmlu).

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets BEFORE --run):
  TT-R1 the identity precondition "validated against the Kotlin generator on one site" is met by the COMPILED Kotlin method's
        outputs on mix_lrt_site's two JVM fixture sites (the record's existing proof, ST-JVM), re-checked at every entry point; no
        JVM is run (the brief: no Gradle).
  TT-R2 TL2 "agrees" iff mean z(delta_rel) of qwen3 (native) < that of gemma (native) on BOTH corpora (more tree-like = lower z).
  TT-R3 "Khrulkov's estimator" = the four-point maximum over the sampled quadruples divided by the sample's diameter; the mean
        four-point delta (2 mean / diam) is printed beside, descriptive.
  TT-R4 the planted control's scales (1.0 / 0.5 / 0.25 of a covariance draw, kappa from theta3 / 2) are fixed here, before data;
        they were set on synthetic data only.
  TT-R5 MMLU-Pro texts = distinct mmlu_pro questions whose CK item ("i:" + stem_key) is TRAIN in the v2 side export and that
        carry a vector in all three DBs.

SELFTEST MUTANTS (2026-10-04; `--mutants`; copies in a scratch sandbox, the file never edited): the 21 mutants in MUTANTS below
(T1-T21: the -2 and 4-of-5 boundaries, either-corpus TREE-LIKE, MIXED lost, the gate ignored, a one-corpus gate, mean for max
delta, mean for max diam, the null without mu, one null seed, the wrong arm, the 256 width, one subsample seed, F-TL unprinted,
write-once dropped, the identity refusal dropped, every side read, z unscaled, a 20% ultrametric tolerance, the control on the
data's null, P1 on the TL1 event): 21 / 21 KILLED on this code (final run 2026-10-04; kill sites in the commit message).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import datetime
import hashlib
import json
import math
import sqlite3
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import zc_common as ZC          # noqa: E402  (imports scratch_dir: temp on E:, removed at exit)
import scratch_dir              # noqa: E402

import numpy as np              # noqa: E402

ROOT = ZC.ROOT
TAG = "[TREE-LIKE]"
REG = "docs/judge_v2_program.md L24362-L24373 (registration commit 633255f2)"
SEED = 20261004
N_SUB = 2000
SUBS = 5
B = 200
QUADS = 1_000_000
UM_TOL = 0.02
Z_BAR = -2.0
K_OF = 4
WIDTH = 256
CORPORA = ("massive", "clinc")
ARMS = ("qwen3", "qwen3_q8", "qwen3_card", "gemma", "gemma_card", "nomic")
NATIVE = {"qwen3": 4096, "qwen3_q8": 4096, "qwen3_card": 4096, "gemma": 768, "gemma_card": 768, "nomic": 768}
DECIDING_ARM = "qwen3"
PINS = {"qwen3": "9e100e04fc91b137a075b8abedbc87d2b29a6dc2244c5f242b1c587004a4ee74",
        "nomic": "4aafd6c7fa5f779ee21f152eb7e935774323903b32117f48f6acd24d1ccf11ad",
        "gemma": "b187b82f90ce98376ba3ffac100157493fd8c5ee52dfa88f707738dde2acf512",
        "qwen3_q8": "771666bc8563d972f6c3fea4d987925365cdcb0ce7f56815a8436d0a9fd26266",
        "qwen3_card": "e8dd85afc2afc0752fce019d7fb4ad127a7d06e094cf604401b82efb1f22a1ac",
        "gemma_card": "9396cb1bbb2352cbc2b9de895fb19a03ae41326373db3f58d7c67bf2f9366039"}
INGEST_PIN = "487e0093719c184c98bca53bc9bc61c193559690abb206d77010fd77f81c09a2"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
MIX_BLOB = "e2d28a7319da417a1ab42ca54538a8bf19e63661"
CONTROL_F = (1.0, 0.5, 0.25)
BRANCH = (3, 3, 3)
P1_PROB = 0.85
P2_PROB = {"massive": 0.60, "clinc": 0.60}
P2_TL1 = {"TREE-LIKE": 0.45, "MIXED": 0.30, "NOT-TREE-LIKE": 0.25}
P3_PROB = 0.70
MMLU_POOL = "pv2_41dbd3dbcd399df0"
MMLU_ARMS = ("qwen3", "gemma", "nomic")
MMLU_FILES = {"qwen3": "embeddings_cache.db",
              "gemma": "experiment_results/embedder_cross/embeddings_cache_embeddinggemma_latest.db",
              "nomic": "experiment_results/embedder_cross/embeddings_cache_nomic-embed-text_latest.db"}
MMLU_NATIVE = {"qwen3": 4096, "gemma": 768, "nomic": 768}
SELFTEST_CHECKS = 34

MUTANTS = [
    ("T1", "z bar read as <= -2 (not < -2)", "    return int(sum(1 for z in zs if bool(z < Z_BAR)))\n", "    return int(sum(1 for z in zs if bool(z <= Z_BAR)))\n"),
    ("T2", "per-corpus count >= 3 of 5", "    return \"TREE-LIKE\" if count >= K_OF else \"NOT\"\n", "    return \"TREE-LIKE\" if count >= K_OF - 1 else \"NOT\"\n"),
    ("T3", "TL1 TREE-LIKE on either corpus", "    if all(v == \"TREE-LIKE\" for v in per.values()):\n", "    if any(v == \"TREE-LIKE\" for v in per.values()):\n"),
    ("T4", "NOT-TREE-LIKE read on 'not both' (MIXED lost)", "    if all(v != \"TREE-LIKE\" for v in per.values()):\n", "    if True:\n"),
    ("T5", "the TL0 gate ignored", "    if gate != \"PASS\":\n        return \"NOT EVALUABLE\"\n", "    if False:\n        return \"NOT EVALUABLE\"\n"),
    ("T6", "TL0 needs one corpus only", "    return \"PASS\" if all(c >= K_OF for c in counts.values()) else \"FAIL\"\n", "    return \"PASS\" if any(c >= K_OF for c in counts.values()) else \"FAIL\"\n"),
    ("T7", "delta = mean four-point value, not the maximum", "    delta_rel = 2.0 * float(dq.max()) / diam\n", "    delta_rel = 2.0 * float(dq.mean()) / diam\n"),
    ("T8", "diam = mean distance, not the maximum", "    diam = float(D.max())\n", "    diam = float(D.mean())\n"),
    ("T9", "the null without the centred rows' mean mu (zero-mean cloud)", "    Y = mu + (G * inv) @ Cc\n", "    Y = (G * inv) @ Cc\n"),
    ("T10", "one null seed for every draw b", "default_rng([SEED, ci, i, b]) if tag is None else np.random.default_rng([SEED, tag, ci, i, b])\n", "default_rng([SEED, ci, i, 0]) if tag is None else np.random.default_rng([SEED, tag, ci, i, 0])\n"),
    ("T11", "deciding arm = qwen3_q8 (wrong population)", "DECIDING_ARM = \"qwen3\"\n", "DECIDING_ARM = \"qwen3_q8\"\n"),
    ("T12", "deciding width 256 instead of native", "    dec = cells[(DECIDING_ARM, \"native\")]\n", "    dec = cells[(DECIDING_ARM, \"w%d\" % ctx.width)]\n"),
    ("T13", "one subsample seed for all five", "        rng = np.random.default_rng(SEED + i)\n", "        rng = np.random.default_rng(SEED)\n"),
    ("T14", "F-TL line not printed on the NOT-TREE-LIKE branch", "        out.append(\"F-TL (fires iff TL1 NOT-TREE-LIKE): FIRED", "        0 and out.append(\"F-TL (fires iff TL1 NOT-TREE-LIKE): FIRED"),
    ("T15", "write-once dropped (pre-check and mode x both gone)",
     "        if os.path.exists(p):\n            ZC.refuse(TAG, \"%s exists: the outcome of record is WRITE-ONCE (refused before any read)\" % p)\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    ZC.write_once(out_path, text, TAG)\n",
     "        pass\n    lines, _ = analyse(ctx)\n    text = \"\\n\".join(lines) + \"\\n\"\n    print(text, end=\"\")\n    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)\n    open(out_path, \"w\", encoding=\"utf-8\").write(text)\n"),
    ("T16", "identity precondition not refused on a deviating generator", "    if dev > 1e-12 or lit_dev != 0.0 or not g_ok:\n", "    if False:\n"),
    ("T17", "every side read (TRAIN filter dropped)", "        rows = C.idx(SIDE_TRAIN)\n", "        rows = np.nonzero(C.kept & ~C.oos)[0]\n"),
    ("T18", "z with the null SD replaced by 1 (unscaled difference)", "    return (obs - mu) / sd\n", "    return (obs - mu)\n"),
    ("T19", "ultrametric tolerance 20% instead of 2%", "UM_TOL = 0.02\n", "UM_TOL = 0.2\n"),
    ("T20", "the positive control scored against the DATA's null (not its own)", "            pz = score_set(ctx, P, ci, i, quad, tag=98)\n", "            pz = score_set(ctx, P, ci, i, quad, tag=None)\n"),
    ("T21", "P1 Brier on the wrong event (TL1 instead of TL0)", "    out.append(\"P1 TL0 PASS predicted at 0.85, occurred: %s, Brier %.4f\" % (\"yes\" if gate == \"PASS\" else \"no\", ZC.brier(P1_PROB, gate == \"PASS\")))\n",
     "    out.append(\"P1 TL0 PASS predicted at 0.85, occurred: %s, Brier %.4f\" % (\"yes\" if tl1 == \"TREE-LIKE\" else \"no\", ZC.brier(P1_PROB, tl1 == \"TREE-LIKE\")))\n"),
]


class Ctx(object):
    def __init__(self, data_root=ROOT, n_sub=N_SUB, subs=SUBS, b=B, quads=QUADS, width=WIDTH, native=None, check_pins=True,
                 control_fn=None, arms=ARMS, mmlu=False):
        self.data_root, self.n_sub, self.subs, self.b, self.quads, self.width = data_root, n_sub, subs, b, quads, width
        self.native = native or dict(NATIVE)
        self.check_pins = check_pins
        self.control_fn = control_fn
        self.arms = arms
        self.mmlu = mmlu
        self.staged = {}
        self.stage_dir = None

    def stage(self, rel):
        if rel not in self.staged:
            if self.stage_dir is None:
                self.stage_dir = scratch_dir.mkdtemp(prefix="tree_like_stage_")
            d = os.path.join(self.stage_dir, str(len(self.staged)))
            self.staged[rel] = ZC.stage_db(os.path.join(self.data_root, rel), d, TAG)
        return self.staged[rel]


# ----------------------------------------------------------------------------------------------- generator and identity
def null_cloud(mu, Cc, n, rng):
    """withinNodeCloud (Kotlin L558-L577) vectorised: mu + (G / sqrt(m)) @ Cc, G iid N(0, 1) consumed row-major (m per output
    row, as the Kotlin loop consumes them), then each row unit-normalised."""
    m = Cc.shape[0]
    inv = 1.0 / math.sqrt(m)
    G = rng.standard_normal((n, m))
    Y = mu + (G * inv) @ Cc
    return Y / np.linalg.norm(Y, axis=1, keepdims=True)


class _Feed(object):
    def __init__(self, G):
        self.G, self.i = np.asarray(G), 0

    def standard_normal(self, shape):
        out = self.G[self.i:self.i + shape[0]]
        self.i += shape[0]
        return out


def identity_check(gen=None, out=None):
    """IDENTITY PRECONDITION: REFUSES unless the generator reproduces the compiled Kotlin withinNodeCloud's JVM fixture."""
    gen = gen or null_cloud
    raw = getattr(sqlite3.connect, "_raw", sqlite3.connect)
    import mix_lrt_site as MX            # its import replaces sqlite3.connect process-wide (MIX-LRT's own guard) ...
    sqlite3.connect = raw                # ... restored at once: this readout opens its staged copies itself (zc_common.open_ro)
    blob = ZC.git_blob(MX.__file__.replace(".pyc", ".py"))
    if blob != MIX_BLOB:
        ZC.refuse(TAG, "mix_lrt_site.py is blob:%s, the JVM fixture of record is in blob:%s" % (blob, MIX_BLOB))
    (mu1, c1, n1, s1, f1), (mu2, c2, n2, s2, f2), g42 = MX.jvm_fixture()
    jr = MX.JavaRandom(42)
    g_ok = [jr.next_gaussian() for _ in range(10)] == g42
    dev = 0.0; lit_dev = 0.0
    for mu, cen, n, seed, ref in ((mu1, c1, n1, s1, f1), (mu2, c2, n2, s2, f2)):
        lit = MX.within_node_cloud_loop(mu, cen, n, MX.JavaRandom(seed).next_gaussian)
        lit_dev = max(lit_dev, max(abs(a - b) for ra, rb in zip(lit, ref) for a, b in zip(ra, rb)))
        jr = MX.JavaRandom(seed)
        G = np.array([[jr.next_gaussian() for _ in range(len(cen))] for _ in range(n)])
        Y = gen(np.array(mu), np.array(cen), n, _Feed(G))
        dev = max(dev, float(np.max(np.abs(Y - np.array(ref)))))
    if dev > 1e-12 or lit_dev != 0.0 or not g_ok:
        ZC.refuse(TAG, "IDENTITY PRECONDITION failed: the numpy generator deviates from the compiled Kotlin withinNodeCloud by %.3e "
                       "(literal transcription %.3e; java.util.Random clone %s)" % (dev, lit_dev, "OK" if g_ok else "WRONG"))
    if out is not None:
        out.append("IDENTITY PRECONDITION: the numpy withinNodeCloud fed java.util.Random(seed) Gaussians reproduces the compiled "
                   "Kotlin method's JVM fixture (mix_lrt_site blob:%s, two sites) to max |dev| %.1e; literal transcription bit for "
                   "bit; java.util.Random(42) clone exact" % (MIX_BLOB, dev))
    return dev


# ----------------------------------------------------------------------------------------------- statistics
def quad_sample(n, q, ci, i):
    rng = np.random.default_rng([SEED, 7, ci, i])
    Q = rng.integers(0, n, size=(q, 4))
    ok = (Q[:, 0] != Q[:, 1]) & (Q[:, 0] != Q[:, 2]) & (Q[:, 0] != Q[:, 3]) & (Q[:, 1] != Q[:, 2]) & (Q[:, 1] != Q[:, 3]) & (Q[:, 2] != Q[:, 3])
    return Q[ok].T


def stats(X, quad):
    """-> (delta_rel, mean_delta_rel, ultrametricity index, cophenetic correlation) on angular distance."""
    from scipy.cluster.hierarchy import linkage, cophenet
    from scipy.spatial.distance import squareform
    S = X @ X.T
    np.clip(S, -1.0, 1.0, out=S)
    D = np.arccos(S)
    np.fill_diagonal(D, 0.0)
    a, b, c, e = quad
    dab, dcd, dac, dbd, dad, dbc = D[a, b], D[c, e], D[a, c], D[b, e], D[a, e], D[b, c]
    st = np.sort(np.stack([dab + dcd, dac + dbd, dad + dbc]), axis=0)
    dq = (st[2] - st[1]) / 2.0
    diam = float(D.max())
    delta_rel = 2.0 * float(dq.max()) / diam
    mean_rel = 2.0 * float(dq.mean()) / diam
    t = np.sort(np.stack([dab, dbc, dac]), axis=0)
    ultra = float(np.mean((t[2] - t[1]) <= UM_TOL * t[2]))
    cond = squareform(D, checks=False)
    coph = float(cophenet(linkage(cond, method="average"), cond)[0])
    return np.array([delta_rel, mean_rel, ultra, coph])


def zscore(obs, null):
    null = np.asarray(null, dtype=np.float64)
    mu = null.mean(axis=0)
    sd = null.std(axis=0, ddof=1)
    return (obs - mu) / sd


def score_set(ctx, X, ci, i, quad, tag=None):
    """obs stats of X and its B moment-matched null draws -> dict(obs, null, z). tag None: the data's null stream
    default_rng([SEED, ci, i, b]); tag t: default_rng([SEED, t, ci, i, b]) (the planted control's own stream)."""
    obs = stats(X, quad)
    mu = X.mean(axis=0)
    Cc = X - mu
    null = []
    for b in range(ctx.b):
        rng = np.random.default_rng([SEED, ci, i, b]) if tag is None else np.random.default_rng([SEED, tag, ci, i, b])
        null.append(stats(null_cloud(mu, Cc, len(X), rng), quad))
    null = np.array(null)
    return dict(obs=obs, null=null, z=zscore(obs, null), neg=zscore(null[0], null[1:]))


def vmf_sample(mu, kappa, n, rng):
    """Wood (1994) von Mises-Fisher sampler on S^{d-1} around the unit vector mu."""
    d = mu.size
    m1 = d - 1.0
    b = m1 / (2.0 * kappa + math.sqrt(4.0 * kappa * kappa + m1 * m1))
    x0 = (1.0 - b) / (1.0 + b)
    c = kappa * x0 + m1 * math.log(1.0 - x0 * x0)
    w = np.empty(n)
    todo = np.arange(n)
    while todo.size:
        z = rng.beta(m1 / 2.0, m1 / 2.0, size=todo.size)
        ww = (1.0 - (1.0 + b) * z) / (1.0 - (1.0 - b) * z)
        u = rng.random(todo.size)
        acc = kappa * ww + m1 * np.log(1.0 - x0 * ww) - c >= np.log(u)
        w[todo[acc]] = ww[acc]
        todo = todo[~acc]
    V = rng.standard_normal((n, d))
    V -= np.outer(V @ mu, mu)
    V /= np.linalg.norm(V, axis=1, keepdims=True)
    return w[:, None] * mu[None, :] + np.sqrt(np.maximum(0.0, 1.0 - w * w))[:, None] * V


def unit(X):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def planted(X, rng, f=CONTROL_F, branch=BRANCH):
    """The positive control (TT-R4): a 3-level hierarchical vMF mixture with X's spectrum (see the module docstring)."""
    n, d = X.shape
    mu = X.mean(axis=0)
    Cc = X - mu
    m = len(X)

    def off():
        return (rng.standard_normal(m) / math.sqrt(m)) @ Cc
    leaves = []
    for _ in range(branch[0]):
        u1 = off()
        for _ in range(branch[1]):
            u2 = off()
            for _ in range(branch[2]):
                leaves.append(mu + f[0] * u1 + f[1] * u2 + f[2] * off())
    L = unit(np.array(leaves))
    g = branch[2]
    sib = []
    for s in range(0, len(L), g):
        for x in range(g):
            for y in range(x + 1, g):
                sib.append(math.acos(max(-1.0, min(1.0, float(L[s + x] @ L[s + y])))))
    th = float(np.median(sib))
    kappa = (d - 1.0) / (th / 2.0) ** 2
    lab = np.arange(n) % len(L)
    P = np.empty((n, d))
    for k in range(len(L)):
        idx = np.nonzero(lab == k)[0]
        if idx.size:
            P[idx] = vmf_sample(L[k], kappa, idx.size, rng)
    return P, th, kappa


# ----------------------------------------------------------------------------------------------- decisions
def count_below(zs):
    return int(sum(1 for z in zs if bool(z < Z_BAR)))


def corpus_word(count):
    return "TREE-LIKE" if count >= K_OF else "NOT"


def tl0_decide(counts):
    """TL0 (gate): PASS iff the control reaches z(delta_rel) < -2 in >= 4 of 5 on both corpora."""
    return "PASS" if all(c >= K_OF for c in counts.values()) else "FAIL"


def tl1_decide(gate, per):
    """TL1: NOT EVALUABLE without TL0; TREE-LIKE iff both corpora; NOT-TREE-LIKE iff neither; MIXED otherwise."""
    if gate != "PASS":
        return "NOT EVALUABLE"
    if all(v == "TREE-LIKE" for v in per.values()):
        return "TREE-LIKE"
    if all(v != "TREE-LIKE" for v in per.values()):
        return "NOT-TREE-LIKE"
    return "MIXED"


# ----------------------------------------------------------------------------------------------- data
SIDE_TRAIN = "TRAIN"


def its_module():
    import intent_transfer_s0 as ITS
    b = ZC.git_blob(ITS.__file__.replace(".pyc", ".py"))
    if b != ITS_BLOB:
        ZC.refuse(TAG, "intent_transfer_s0.py is blob:%s, not the pinned blob:%s" % (b, ITS_BLOB))
    return ITS


def config_pins():
    """The registrar's pins from the committed configs; each must equal the copy in PINS (else REFUSE)."""
    cfg = os.path.join(ROOT, "experiment_configs")
    j = lambda f: json.load(open(os.path.join(cfg, f), encoding="utf-8"))
    s0, q8, card = j("intent_transfer_s0_pins.json"), j("embed_quant_pins.json"), j("card_protocol_pins.json")
    got = dict(qwen3=s0["emb"]["qwen3"], nomic=s0["emb"]["nomic"], gemma=s0["emb"]["gemma"], qwen3_q8=q8["q8"],
               qwen3_card=card["qwen3_card"], gemma_card=card["gemma_card"])
    bad = sorted(k for k in PINS if got.get(k) != PINS[k])
    if bad or s0["ingest_db"] != INGEST_PIN:
        ZC.refuse(TAG, "the committed pin configs disagree with this script's PINS on %s" % (bad or ["ingest_db"]))
    return got


def mmlu_pins():
    """--mmlu: the registrar's sha256 pins of the gemma / nomic RAW files (experiment_configs/embedder_cross_arm_pins.json);
    embeddings_cache.db carries no pin (its sha256 is printed)."""
    d = json.load(open(os.path.join(ROOT, "experiment_configs", "embedder_cross_arm_pins.json"), encoding="utf-8"))["arms"]
    return {"gemma": d["gemma_raw"]["sha256"], "nomic": d["nomic_raw"]["sha256"]}


def read_vectors(path, texts, native):
    want = set(texts)
    out = {}
    con = ZC.open_ro(path, TAG)
    try:
        for t, bl in con.execute("SELECT query, vector FROM embeddings"):
            if t in want:
                if bl is None or len(bl) != 4 * native:
                    ZC.refuse(TAG, "%s: a vector of %s bytes, not %d-d" % (path, None if bl is None else len(bl), native))
                out[t] = np.frombuffer(bl, dtype=">f4").astype(np.float64)
    finally:
        con.close()
    miss = len(want) - len(out)
    if miss:
        ZC.refuse(TAG, "%s: %d of %d subsample texts have no vector" % (path, miss, len(want)))
    return out


def subsamples(ctx, n_rows):
    subs = []
    for i in range(ctx.subs):
        rng = np.random.default_rng(SEED + i)
        subs.append(np.sort(rng.choice(n_rows, ctx.n_sub, replace=False)))
    return subs


def intent_inputs(ctx, out):
    """-> (texts per corpus per subsample, census lines). Reads the staged ingest copy only."""
    ITS = its_module()
    ing = ctx.stage("intent_transfer_corpora_v1.db")
    if ctx.check_pins and ing["sha256"] != INGEST_PIN:
        ZC.refuse(TAG, "intent_transfer_corpora_v1.db sha256 %s != the pin %s" % (ing["sha256"], INGEST_PIN))
    CS = ITS.load_corpora(ing["path"])
    sub_texts = {}
    for ci, c in enumerate(CORPORA):
        C = CS[c]
        rows = C.idx(SIDE_TRAIN)
        if len(rows) < ctx.n_sub:
            ZC.refuse(TAG, "%s: %d TRAIN rows < the subsample size %d" % (c, len(rows), ctx.n_sub))
        texts = [C.text[j] for j in rows]
        sub_texts[c] = [[texts[j] for j in s] for s in subsamples(ctx, len(texts))]
        out.append("  census %s: %d TRAIN rows (kept, in-scope; sides of the ingest: TRAIN %d / GATE %d / EVAL %d); %d subsamples of %d"
                   % (c, len(rows), len(C.idx("TRAIN")), len(C.idx("GATE")), len(C.idx("EVAL")), ctx.subs, ctx.n_sub))
    out.append("  ingest intent_transfer_corpora_v1.db sha256 %s (%s)" % (ing["sha256"][:16], "PIN OK" if ing["sha256"] == INGEST_PIN else "unpinned fixture"))
    return sub_texts


def arm_vectors(ctx, arm, sub_texts, out, files=None, native=None):
    rel = (files or {}).get(arm, "intent_emb_%s.db" % arm)
    st = ctx.stage(rel)
    pin = PINS.get(arm) if not ctx.mmlu else mmlu_pins().get(arm)
    if ctx.check_pins and pin is not None and st["sha256"] != pin:
        ZC.refuse(TAG, "%s sha256 %s != the registrar's pin %s" % (rel, st["sha256"], pin))
    allt = sorted({t for c in sub_texts for s in sub_texts[c] for t in s})
    vec = read_vectors(st["path"], allt, (native or ctx.native)[arm])
    out.append("  arm %-10s %s sha256 %s (%s); %d-d; %d subsample texts read" % (
        arm, rel, st["sha256"][:16], ("PIN OK" if st["sha256"] == pin else "PIN MISMATCH") if pin else "no pin (sha256 printed)",
        (native or ctx.native)[arm], len(allt)))
    return vec


def cell_matrix(vec, texts, width):
    X = np.array([vec[t] for t in texts], dtype=np.float64)
    if width is not None:
        X = X[:, :width]
    return unit(X)


# ----------------------------------------------------------------------------------------------- run
def header(ctx, out, mode):
    out.append("TREE-LIKE readout (%s); mode %s; %s; zc_common blob:%s; intent_transfer_s0 blob:%s (pinned); mix_lrt_site blob:%s (pinned); date %s; ZERO calls"
               % (REG, mode, ZC.pins_line(os.path.abspath(__file__)), ZC.git_blob(ZC.__file__.replace(".pyc", ".py")), ITS_BLOB,
                  MIX_BLOB, datetime.date.today().isoformat()))
    if ctx.mmlu:
        out.append("POOL READER (rule 7; --mmlu, DESCRIPTIVE): reads embeddings_cache.db and the v2 side export (pool %s); split word TRAIN of draw 5a3e756 (content-closed under CK-CLOSE-v2)" % MMLU_POOL)
    else:
        out.append("POOL: none read (intent DBs and the intent ingest only; rule 7 does not bind). TRAIN rows only; labels never read.")


def compute(ctx, sub_texts, vecs_by_arm, out, with_control=True):
    """cells[(arm, 'native' | 'w<width>')][corpus] = list over subsamples of score_set dicts; control[corpus] likewise."""
    cells = {}
    control = {}
    for arm, vec in vecs_by_arm.items():
        for wkey, width in (("native", None), ("w%d" % ctx.width, ctx.width)):
            cells[(arm, wkey)] = {}
            for ci, c in enumerate(CORPORA if not ctx.mmlu else ("mmlu",)):
                res = []
                for i, texts in enumerate(sub_texts[c]):
                    X = cell_matrix(vec, texts, width)
                    quad = quad_sample(len(X), ctx.quads, ci, i)
                    res.append(score_set(ctx, X, ci, i, quad))
                    if with_control and arm == DECIDING_ARM and wkey == "native" and not ctx.mmlu:
                        rng = np.random.default_rng([SEED, 99, ci, i])
                        if ctx.control_fn is None:
                            P, th, kap = planted(X, rng)
                        else:
                            P, th, kap = ctx.control_fn(X, rng)
                        pz = score_set(ctx, P, ci, i, quad, tag=98)
                        pz["theta3"], pz["kappa"] = th, kap
                        control.setdefault(c, []).append(pz)
                cells[(arm, wkey)][c] = res
    return cells, control


def cell_line(label, res):
    z = np.array([r["z"] for r in res])
    return ("  %-26s z(delta_rel) [%s] (< -2: %d of %d); obs delta_rel [%s]; null SD %.4g; z(mean delta) mean %+.2f; z(ultrametricity) mean %+.2f; z(cophenetic) mean %+.2f"
            % (label, ", ".join("%+.3f" % v for v in z[:, 0]), count_below(z[:, 0]), len(res),
               ", ".join("%.4f" % r["obs"][0] for r in res), float(np.mean([r["null"][:, 0].std(ddof=1) for r in res])),
               float(z[:, 1].mean()), float(z[:, 2].mean()), float(z[:, 3].mean())))


def verdict_lines(ctx, cells, control, out):
    dec = cells[(DECIDING_ARM, "native")]
    counts_c = {c: count_below([r["z"][0] for r in control[c]]) for c in CORPORA}
    gate = tl0_decide(counts_c)
    per = {c: corpus_word(count_below([r["z"][0] for r in dec[c]])) for c in CORPORA}
    tl1 = tl1_decide(gate, per)
    out.append("CRITERIA AND PREDICTIONS")
    out.append("TL0 (gate; PASS iff the planted control reaches z(delta_rel) < -2 in >= 4 of 5 on both corpora): %s -- control counts %s"
               % (gate, ", ".join("%s %d of %d" % (c, counts_c[c], len(control[c])) for c in CORPORA)))
    cnt = {c: count_below([r["z"][0] for r in dec[c]]) for c in CORPORA}
    if tl1 == "NOT EVALUABLE":
        out.append("TL1 (DECIDING; qwen3 q4, native 4096; TREE-LIKE iff z(delta_rel) < -2 in >= 4 of 5 on both MASSIVE and CLINC): NOT EVALUABLE -- TL0 FAIL; the counts (massive %d of 5, clinc %d of 5) are printed, not scored"
                   % (cnt["massive"], cnt["clinc"]))
        out.append("F-TL (fires iff TL1 NOT-TREE-LIKE): NOT FIRED (TL1 NOT EVALUABLE)")
    else:
        out.append("TL1 (DECIDING; qwen3 q4, native 4096; TREE-LIKE iff z(delta_rel) < -2 in >= 4 of 5 on both MASSIVE and CLINC): %s -- massive %d of %d (%s), clinc %d of %d (%s)"
                   % (tl1, cnt["massive"], len(dec["massive"]), "TREE-LIKE" if per["massive"] == "TREE-LIKE" else "not tree-like",
                      cnt["clinc"], len(dec["clinc"]), "TREE-LIKE" if per["clinc"] == "TREE-LIKE" else "not tree-like"))
        if tl1 == "NOT-TREE-LIKE":
            out.append("F-TL (fires iff TL1 NOT-TREE-LIKE): FIRED -- on MASSIVE and CLINC (known two-level gold) any tree hierarchy is imposed by the algorithm, not found; GRANULARITY-GT GR2's random-tree comparison becomes the only defensible hierarchy claim")
        else:
            out.append("F-TL (fires iff TL1 NOT-TREE-LIKE): NOT FIRED")
    out.append("P1 TL0 PASS predicted at 0.85, occurred: %s, Brier %.4f" % ("yes" if gate == "PASS" else "no", ZC.brier(P1_PROB, gate == "PASS")))
    if tl1 == "NOT EVALUABLE":
        out.append("P2 not scored (TL1 NOT EVALUABLE)")
    else:
        out.append("P2 MASSIVE TREE-LIKE predicted at 0.60, occurred: %s, Brier %.4f; CLINC TREE-LIKE predicted at 0.60, occurred: %s, Brier %.4f; TL1 events: %s"
                   % ("yes" if per["massive"] == "TREE-LIKE" else "no", ZC.brier(0.60, per["massive"] == "TREE-LIKE"),
                      "yes" if per["clinc"] == "TREE-LIKE" else "no", ZC.brier(0.60, per["clinc"] == "TREE-LIKE"),
                      "; ".join("%s %.2f Brier %.4f" % (k, v, ZC.brier(v, tl1 == k)) for k, v in P2_TL1.items())))
    zq = {c: float(np.mean([r["z"][0] for r in cells[("qwen3", "native")][c]])) for c in CORPORA}
    zg = {c: float(np.mean([r["z"][0] for r in cells[("gemma", "native")][c]])) for c in CORPORA} if ("gemma", "native") in cells else None
    if zg is None:
        out.append("TL2 / P3 not computed (gemma arm absent)")
        agree = None
    else:
        agree = bool(all(zq[c] < zg[c] for c in CORPORA))
        out.append("TL2 (DESCRIPTIVE; TT-R2: agrees iff mean z(delta_rel) qwen3 < gemma on both corpora; record leaf counts qwen3 M-AF 84 > gemma 4): %s -- %s"
                   % ("AGREES" if agree else "DOES NOT AGREE", "; ".join("%s qwen3 %+.3f vs gemma %+.3f" % (c, zq[c], zg[c]) for c in CORPORA)))
        out.append("P3 TL2 agrees predicted at 0.70 (descriptive), occurred: %s, Brier %.4f" % ("yes" if agree else "no", ZC.brier(P3_PROB, agree)))
    out.append("WHAT THIS RESULT DOES NOT SHOW (registered): that a particular tree is right; anything a covariance determines (second-moment descriptors are descriptive only); MMLU-Pro as decisive.")
    return dict(gate=gate, per=per, tl1=tl1, agree=agree, counts=cnt, control_counts=counts_c)


def analyse(ctx):
    out = []
    header(ctx, out, "--run" + (" --mmlu" if ctx.mmlu else ""))
    identity_check(out=out)
    if ctx.mmlu:
        sub_texts, files = mmlu_inputs(ctx, out)
        vecs = {a: arm_vectors(ctx, a, sub_texts, out, files=files, native=MMLU_NATIVE) for a in MMLU_ARMS}
        cells, _ = compute(ctx, sub_texts, vecs, out, with_control=False)
        out.append("CELLS (MMLU-Pro, DESCRIPTIVE; no criterion): arm x width, 5 subsamples each")
        for (arm, wkey), per in sorted(cells.items()):
            out.append(cell_line("%s %s mmlu" % (arm, wkey), per["mmlu"]))
        out.append("WHAT THIS RESULT DOES NOT SHOW (registered): MMLU-Pro as decisive; that a particular tree is right.")
        return out, dict(cells=cells)
    if ctx.check_pins:
        config_pins()
    sub_texts = intent_inputs(ctx, out)
    vecs = {}
    for a in ctx.arms:
        vecs[a] = arm_vectors(ctx, a, sub_texts, out)
    cells, control = compute(ctx, sub_texts, vecs, out)
    out.append("SUPPORT (registered (a)-(f) quoted): %d subsamples x %d points per corpus; z against %d null draws; DEFF 1.0; n_eff %d per corpus; the null mean's own SE 1/sqrt(%d) = %.3f in z units; classification over 5 subsamples (4 of 5); SCOREABLE conditional on TL0"
               % (ctx.subs, ctx.n_sub, ctx.b, ctx.subs, ctx.b, 1.0 / math.sqrt(ctx.b)))
    out.append("POSITIVE CONTROL (planted 3-level vMF hierarchy with the qwen3 native spectrum; own null):")
    for c in CORPORA:
        out.append(cell_line("control %s" % c, control[c]) + "; theta3 [%s]" % ", ".join("%.3f" % r["theta3"] for r in control[c]))
    neg = [float(r["neg"][0]) for c in CORPORA for r in cells[(DECIDING_ARM, "native")][c]]
    out.append("NEGATIVE CONTROL (descriptive; null draw 0 vs draws 1..%d, deciding arm): z(delta_rel) [%s]; %d of %d below -2"
               % (ctx.b - 1, ", ".join("%+.2f" % v for v in neg), sum(1 for v in neg if v < Z_BAR), len(neg)))
    out.append("CELLS (deciding = qwen3 native; the rest DESCRIPTIVE):")
    for (arm, wkey) in sorted(cells, key=lambda k: (ARMS.index(k[0]) if k[0] in ARMS else 99, k[1])):
        for c in CORPORA:
            out.append(cell_line("%s %s %s" % (arm, wkey, c), cells[(arm, wkey)][c]))
    out.append("BUILDER'S READINGS (the registrar confirms or brackets): TT-R1 identity via the compiled-Kotlin JVM fixture; TT-R2 TL2 'agrees' on both corpora; TT-R3 Khrulkov = max four-point delta / diam; TT-R4 control scales fixed before data; TT-R5 MMLU texts")
    v = verdict_lines(ctx, cells, control, out)
    return out, dict(v=v, cells=cells, control=control)


def mmlu_inputs(ctx, out):
    import split_side as SSD
    import v2_engine_pool as EP
    items, meta = EP.read_side(os.path.join(ROOT, EP.DEFAULT_SIDE))
    got, n_comp = EP.pool_of(items, "mmlu-pro-v2")
    if got != MMLU_POOL:
        ZC.refuse(TAG, "the side export's mmlu-pro-v2 pool is %s, not %s" % (got, MMLU_POOL))
    out.append("  pool %s recomputed from the side export %s (sha256-lf %s); %d EVAL components" % (got, meta["path"], meta["sha256_lf"][:16], n_comp))
    mm = ctx.stage("mmlu_pro_dataset_cache_v2.db")
    con = ZC.open_ro(mm["path"], TAG)
    try:
        texts = sorted({t for (t,) in con.execute("SELECT question FROM mmlu_pro") if t})
    finally:
        con.close()
    train = [t for t in texts if items.get("i:" + SSD.stem_key(t), (None, None))[1] == "TRAIN"]
    have = None
    for a in MMLU_ARMS:
        st = ctx.stage(MMLU_FILES[a])
        con = ZC.open_ro(st["path"], TAG)
        try:
            s = {t for (t,) in con.execute("SELECT query FROM embeddings")}
        finally:
            con.close()
        have = s if have is None else (have & s)
    pool_t = sorted(t for t in train if t in have)
    out.append("  MMLU-Pro TRAIN texts of draw 5a3e756: %d distinct mmlu_pro questions on TRAIN, %d with a vector in all three DBs" % (len(train), len(pool_t)))
    if len(pool_t) < ctx.n_sub:
        ZC.refuse(TAG, "MMLU-Pro: %d texts < %d" % (len(pool_t), ctx.n_sub))
    return {"mmlu": [[pool_t[j] for j in s] for s in subsamples(ctx, len(pool_t))]}, MMLU_FILES


def dry_run(ctx):
    out = []
    header(ctx, out, "--dry-run" + (" --mmlu" if ctx.mmlu else ""))
    identity_check(out=out)
    if ctx.mmlu:
        sub_texts, files = mmlu_inputs(ctx, out)
        vecs = {a: arm_vectors(ctx, a, sub_texts, out, files=files, native=MMLU_NATIVE) for a in MMLU_ARMS}
    else:
        if ctx.check_pins:
            config_pins()
        sub_texts = intent_inputs(ctx, out)
        vecs = {a: arm_vectors(ctx, a, sub_texts, out) for a in ctx.arms}
    corp = list(sub_texts)[0]
    total = 0.0
    for a, vec in vecs.items():
        for wkey, width in (("native", None), ("w%d" % ctx.width, ctx.width)):
            X = cell_matrix(vec, sub_texts[corp][0], width)
            quad = quad_sample(len(X), ctx.quads, 0, 0)
            t0 = time.time(); stats(X, quad); null_cloud(X.mean(0), X - X.mean(0), len(X), np.random.default_rng(1)); dt = time.time() - t0
            sets = len(sub_texts) * ctx.subs * (ctx.b + 1) * (2 if (a == DECIDING_ARM and wkey == "native" and not ctx.mmlu) else 1)
            total += dt * sets
            out.append("  timed: %s %s one draw + statistics %.2f s x %d point sets = %.0f min" % (a, wkey, dt, sets, dt * sets / 60.0))
    out.append("PRICE: about %.1f h CPU single-threaded (OMP/OPENBLAS/MKL = %s); zero calls" % (total / 3600.0, os.environ.get("OMP_NUM_THREADS")))
    out.append("--dry-run: no z computed, nothing written.")
    print("\n".join(out))
    return 0


def run(ctx, out_path):
    sums = os.path.join(os.path.dirname(os.path.abspath(out_path)), "SHA256SUMS.txt")
    for p in (out_path, sums):
        if os.path.exists(p):
            ZC.refuse(TAG, "%s exists: the outcome of record is WRITE-ONCE (refused before any read)" % p)
    lines, _ = analyse(ctx)
    text = "\n".join(lines) + "\n"
    print(text, end="")
    ZC.write_once(out_path, text, TAG)
    print("%s wrote %s (write-once; never committed)" % (TAG, out_path.replace("\\", "/")))
    return 0


# ----------------------------------------------------------------------------------------------- selftest
FIX_NATIVE = {"qwen3": 48, "qwen3_q8": 48, "qwen3_card": 48, "gemma": 24, "gemma_card": 24, "nomic": 24}
FIX_ARMS = ("qwen3", "qwen3_q8", "gemma")


def _hier_cloud(rng, n, d, scale=(1.0, 0.45, 0.2), noise=0.04):
    """A strongly hierarchical cloud (3 x 3 x 3 leaves) on S^{d-1}: tree-like against its Gaussian null."""
    mu = np.zeros(d); mu[0] = 1.0
    L = []
    for _ in range(3):
        u1 = rng.standard_normal(d)
        for _ in range(3):
            u2 = rng.standard_normal(d)
            for _ in range(3):
                L.append(mu + scale[0] * u1 + scale[1] * u2 + scale[2] * rng.standard_normal(d))
    L = unit(np.array(L))
    lab = np.arange(n) % len(L)
    return unit(L[lab] + noise * rng.standard_normal((n, d)))


def _gauss_cloud(rng, n, d):
    """A structureless anisotropic Gaussian projected to the sphere."""
    sd = 1.0 / np.arange(1, d + 1) ** 0.5
    return unit(np.eye(d)[0] * 2.0 + rng.standard_normal((n, d)) * sd)


def _cloud(rng, kind, n):
    """48-d fixture cloud. 'hier': Gaussian noise (amplitude 0.15) in coordinates 0-23 and the hierarchy (noise 0.02) in 24-47,
    so the native width is tree-like and the first-24 slice (the fixture's 'w24') is not (T12); 'gauss': structureless."""
    if kind == "hier":
        return unit(np.concatenate([0.15 * rng.standard_normal((n, 24)), _hier_cloud(rng, n, 24, noise=0.02)], axis=1))
    return _gauss_cloud(rng, n, 48)


def _fixture(root, kind):
    """Writes the intent ingest DB and six arm DBs. kind[c] in {'hier', 'gauss'} sets the qwen3 cloud of corpus c's TRAIN rows;
    GATE / EVAL / OOS / dropped rows carry the OTHER cloud (hier <-> gauss), so reading them changes the answer (T17). qwen3_q8 is
    structureless everywhere (a wrong deciding arm changes the answer: T11); qwen3_card = qwen3; gemma / gemma_card / nomic = the
    first 8 coordinates (+ noise for gemma)."""
    its_module()                                         # puts tools/ingest on sys.path
    import intent_ingest as II
    os.makedirs(root, exist_ok=True)
    rng = np.random.default_rng(5)
    con = sqlite3.connect(os.path.join(root, "intent_transfer_corpora_v1.db"))
    for d in II.DDL:
        con.execute(d)
    vecs = {a: {} for a in ARMS}
    for c in CORPORA:
        n_tr, n_other = 400, 120
        clouds = {"TRAIN": _cloud(rng, kind[c], n_tr), "OTHER": _cloud(rng, "gauss" if kind[c] == "hier" else "hier", n_other)}
        q8 = _gauss_cloud(rng, n_tr + n_other, 48)
        rows = []
        r = 0
        for side in ("TRAIN", "OTHER"):
            for j in range(len(clouds[side])):
                t = "%s %s text %d" % (c, side, j)
                real_side = "TRAIN" if side == "TRAIN" else ("EVAL", "GATE")[j % 2]
                oos = 1 if (side == "OTHER" and j % 5 == 0 and c == "clinc") else 0
                drop = "dup" if (side == "OTHER" and j % 7 == 0) else None
                if side == "OTHER" and j % 3 == 0:
                    real_side = "TRAIN"           # OTHER rows on TRAIN carry a drop reason or the OOS flag, never clean TRAIN
                    if drop is None and not oos:
                        drop = "dup"
                rows.append((("%s-%s-%04d" % (c, side, j)), c, "train", str(j), t, "x", "y", oos, None, "k%s%d" % (side, j), real_side, real_side, drop))
                v = clouds[side][j]
                vecs["qwen3"][t] = v
                vecs["qwen3_card"][t] = v
                vecs["qwen3_q8"][t] = q8[r]
                vecs["gemma"][t] = unit((v[:24] + 0.3 * rng.standard_normal(24))[None, :])[0]
                vecs["gemma_card"][t] = v[:24]
                vecs["nomic"][t] = v[:24]
                r += 1
        con.executemany("INSERT INTO items VALUES (%s)" % ",".join("?" * 13), rows)
    con.commit(); con.close()
    for a in ARMS:
        e = sqlite3.connect(os.path.join(root, "intent_emb_%s.db" % a))
        e.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        e.executemany("INSERT INTO embeddings VALUES (?,?)", [(t, np.asarray(v, dtype=">f4").tobytes()) for t, v in vecs[a].items()])
        e.commit(); e.close()


def _fctx(root, **kw):
    kw.setdefault("arms", FIX_ARMS)
    c = Ctx(data_root=root, n_sub=300, subs=5, b=30, quads=50000, width=24, native=dict(FIX_NATIVE), check_pins=False, **kw)
    return c


def _ref_delta(X, quad):
    """Independent reference of delta_rel (explicit loops over the quadruples, math.acos)."""
    n = len(X)
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            v = math.acos(max(-1.0, min(1.0, float(np.dot(X[i], X[j])))))
            D[i][j] = D[j][i] = v
    diam = max(max(r) for r in D)
    best = 0.0
    for a, b, c, e in zip(*[q.tolist() for q in quad]):
        s = sorted([D[a][b] + D[c][e], D[a][c] + D[b][e], D[a][e] + D[b][c]])
        best = max(best, (s[2] - s[1]) / 2.0)
    return 2.0 * best / diam


def selftest():
    checks = 0
    with scratch_dir.scratch("tree_like_selftest") as tmp:
        # identity precondition passes on the real generator; a generator without 1/sqrt(m) is REFUSED (T16)
        assert identity_check() <= 1e-12; checks += 1
        bad = lambda mu, Cc, n, rng: (lambda Y: Y / np.linalg.norm(Y, axis=1, keepdims=True))(mu + rng.standard_normal((n, Cc.shape[0])) @ Cc)
        rc, txt = ZC.capture(identity_check, bad)
        assert rc == ("refused", 2) and "IDENTITY PRECONDITION failed" in txt, txt; checks += 1
        # the reference delta_rel equals the vectorised one (T7, T8)
        rng = np.random.default_rng(3)
        X = _hier_cloud(rng, 40, 6)
        q = quad_sample(40, 3000, 0, 0)
        assert abs(stats(X, q)[0] - _ref_delta(X, q)) < 1e-12; checks += 1
        # the ultrametricity index against an explicit loop over the triangles (descriptive statistic; T19)
        Dm = [[math.acos(max(-1.0, min(1.0, float(np.dot(X[i], X[j]))))) if i != j else 0.0 for j in range(40)] for i in range(40)]
        um = []
        for a_, b_, c_ in zip(q[0].tolist(), q[1].tolist(), q[2].tolist()):
            sd_ = sorted([Dm[a_][b_], Dm[b_][c_], Dm[a_][c_]])
            um.append(1.0 if sd_[2] - sd_[1] <= 0.02 * sd_[2] else 0.0)
        assert abs(stats(X, q)[2] - sum(um) / len(um)) < 1e-12 and 0.0 < sum(um) / len(um) < 1.0, sum(um) / len(um); checks += 1
        # ---------------- F1: hier on both corpora -> TL0 PASS, TL1 TREE-LIKE, F-TL NOT FIRED; values vs the reference
        r1 = os.path.join(tmp, "f1")
        _fixture(r1, {"massive": "hier", "clinc": "hier"})
        ctx = _fctx(r1)
        outp = os.path.join(tmp, "f1_out", "o.txt")
        rc, txt = ZC.capture(main, ["--run", "--out", outp], ctx)
        assert rc == 0, txt[-3000:]; checks += 1
        assert txt.splitlines()[1].startswith("POOL: none read"); checks += 1
        tl0 = ZC.line(txt, "TL0 ")
        assert tl0.startswith("TL0 (gate; PASS iff the planted control reaches z(delta_rel) < -2 in >= 4 of 5 on both corpora): PASS -- control counts massive 5 of 5, clinc 5 of 5"), tl0; checks += 1
        tl1 = ZC.line(txt, "TL1 ")
        assert tl1.endswith("): TREE-LIKE -- massive 5 of 5 (TREE-LIKE), clinc 5 of 5 (TREE-LIKE)"), tl1; checks += 1
        assert ZC.line(txt, "F-TL ") == "F-TL (fires iff TL1 NOT-TREE-LIKE): NOT FIRED"; checks += 1
        assert ZC.line(txt, "P1 ") == "P1 TL0 PASS predicted at 0.85, occurred: yes, Brier 0.0225"; checks += 1
        assert ZC.line(txt, "P2 ").startswith("P2 MASSIVE TREE-LIKE predicted at 0.60, occurred: yes, Brier 0.1600; CLINC TREE-LIKE predicted at 0.60, occurred: yes, Brier 0.1600; TL1 events: TREE-LIKE 0.45 Brier 0.3025; MIXED 0.30 Brier 0.0900; NOT-TREE-LIKE 0.25 Brier 0.0625"), ZC.line(txt, "P2 "); checks += 1
        # independent recomputation of the deciding cell's z on subsample 0 of MASSIVE (TRAIN rows, seeds, null stream, z form)
        con = sqlite3.connect(os.path.join(r1, "intent_transfer_corpora_v1.db"))
        tr = [t for (t,) in con.execute("SELECT text FROM items WHERE corpus = 'massive' AND side = 'TRAIN' AND drop_reason IS NULL AND is_oos = 0 ORDER BY item_id")]
        con.close()
        e = sqlite3.connect(os.path.join(r1, "intent_emb_qwen3.db"))
        V = {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in e.execute("SELECT query, vector FROM embeddings")}
        e.close()
        sel = np.sort(np.random.default_rng(SEED + 0).choice(len(tr), 300, replace=False))
        Xr = unit(np.array([V[tr[j]] for j in sel]))
        qr = quad_sample(300, 50000, 0, 0)
        obs = _ref_delta(Xr, qr)
        mu = Xr.mean(0); Cc = Xr - mu
        nulls = []
        for b in range(30):
            G = np.random.default_rng([SEED, 0, 0, b]).standard_normal((300, 300))
            Y = mu[None, :] + np.einsum("rc,ck->rk", G, Cc) / math.sqrt(300.0)        # withinNodeCloud by its definition
            nulls.append(_ref_delta(Y / np.sqrt((Y * Y).sum(axis=1))[:, None], qr))
        z_ref = (obs - np.mean(nulls)) / np.std(nulls, ddof=1)
        cell = ZC.line(txt, "  qwen3 native massive")
        z0 = float(cell.split("z(delta_rel) [")[1].split(",")[0])
        assert abs(z0 - round(z_ref, 3)) < 1.5e-3, (z0, z_ref); checks += 1                       # T9 T10 T17 T18
        # subsample 1 is its own draw (seed 20261004 + 1): its observed delta_rel against the reference (T13)
        sel1 = np.sort(np.random.default_rng(SEED + 1).choice(len(tr), 300, replace=False))
        o1 = _ref_delta(unit(np.array([V[tr[j]] for j in sel1])), quad_sample(300, 50000, 0, 1))
        obs1 = float(cell.split("obs delta_rel [")[1].split(",")[1])
        assert abs(obs1 - round(o1, 4)) < 1e-9 and sorted(sel1.tolist()) != sorted(sel.tolist()), (obs1, o1); checks += 1
        # the positive control's z on subsample 0 of MASSIVE, scored against ITS OWN null stream (tag 98) (T20)
        P0, _, _ = planted(Xr, np.random.default_rng([SEED, 99, 0, 0]))
        muP = P0.mean(0); CP = P0 - muP
        pn = []
        for b in range(30):
            G = np.random.default_rng([SEED, 98, 0, 0, b]).standard_normal((300, 300))
            Y = muP[None, :] + np.einsum("rc,ck->rk", G, CP) / math.sqrt(300.0)
            pn.append(_ref_delta(Y / np.sqrt((Y * Y).sum(axis=1))[:, None], qr))
        zc_ref = (_ref_delta(P0, qr) - np.mean(pn)) / np.std(pn, ddof=1)
        zc0 = float(ZC.line(txt, "  control massive").split("z(delta_rel) [")[1].split(",")[0])
        assert abs(zc0 - round(zc_ref, 3)) < 1.5e-3, (zc0, zc_ref); checks += 1
        # write-once (T15)
        body = open(outp, encoding="utf-8").read()
        assert ZC.line(body, "TL1 ") == tl1; checks += 1
        rc2, txt2 = ZC.capture(main, ["--run", "--out", outp], ctx)
        assert rc2 == ("refused", 2) and "WRITE-ONCE" in txt2 and open(outp, encoding="utf-8").read() == body; checks += 1
        rc2b, _ = ZC.capture(ZC.write_once, outp, "x", TAG)
        assert rc2b == ("refused", 2); checks += 1
        # dry-run
        rc3, txt3 = ZC.capture(main, ["--dry-run"], _fctx(r1))
        assert rc3 == 0 and txt3.rstrip().endswith("--dry-run: no z computed, nothing written.") and "z(delta_rel)" not in txt3; checks += 1
        assert "IDENTITY PRECONDITION: the numpy withinNodeCloud" in txt3 and "census massive: 400 TRAIN rows" in txt3, txt3[-1500:]; checks += 1
        # ---------------- F2: gauss on both -> NOT-TREE-LIKE, F-TL FIRED (T14); P2 events
        r2 = os.path.join(tmp, "f2")
        _fixture(r2, {"massive": "gauss", "clinc": "gauss"})
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f2_out", "o.txt")], _fctx(r2))
        assert rc == 0, txt[-2000:]; checks += 1
        t1 = ZC.line(txt, "TL1 ")
        assert "): NOT-TREE-LIKE -- massive " in t1 and "(not tree-like), clinc " in t1, t1; checks += 1
        assert ZC.line(txt, "F-TL ").startswith("F-TL (fires iff TL1 NOT-TREE-LIKE): FIRED -- on MASSIVE and CLINC"); checks += 1
        assert "TL1 events: TREE-LIKE 0.45 Brier 0.2025; MIXED 0.30 Brier 0.0900; NOT-TREE-LIKE 0.25 Brier 0.5625" in ZC.line(txt, "P2 "); checks += 1
        assert ZC.line(txt, "P1 ") == "P1 TL0 PASS predicted at 0.85, occurred: yes, Brier 0.0225"; checks += 1      # TL0 PASS while TL1 is not TREE-LIKE (T21)
        # ---------------- F3: hier MASSIVE, gauss CLINC -> MIXED (T3 T4)
        r3 = os.path.join(tmp, "f3")
        _fixture(r3, {"massive": "hier", "clinc": "gauss"})
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f3_out", "o.txt")], _fctx(r3))
        assert rc == 0, txt[-2000:]; checks += 1
        assert "): MIXED -- massive 5 of 5 (TREE-LIKE), clinc " in ZC.line(txt, "TL1 "), ZC.line(txt, "TL1 "); checks += 1
        assert ZC.line(txt, "F-TL ") == "F-TL (fires iff TL1 NOT-TREE-LIKE): NOT FIRED"; checks += 1
        # ---------------- F4: the control replaced by a null draw -> TL0 FAIL -> TL1 NOT EVALUABLE (T5 T6 T20 T21)
        nullctl = lambda X, rng: (null_cloud(X.mean(0), X - X.mean(0), len(X), rng), 0.0, 0.0)
        rc, txt = ZC.capture(main, ["--run", "--out", os.path.join(tmp, "f4_out", "o.txt")], _fctx(r1, control_fn=nullctl))
        assert rc == 0, txt[-2000:]; checks += 1
        assert ZC.line(txt, "TL0 ").startswith("TL0 (gate; PASS iff the planted control reaches z(delta_rel) < -2 in >= 4 of 5 on both corpora): FAIL"), ZC.line(txt, "TL0 "); checks += 1
        assert ZC.line(txt, "TL1 ").endswith("NOT EVALUABLE -- TL0 FAIL; the counts (massive 5 of 5, clinc 5 of 5) are printed, not scored"), ZC.line(txt, "TL1 "); checks += 1
        assert ZC.line(txt, "F-TL ") == "F-TL (fires iff TL1 NOT-TREE-LIKE): NOT FIRED (TL1 NOT EVALUABLE)" and ZC.line(txt, "P2 ") == "P2 not scored (TL1 NOT EVALUABLE)"; checks += 1
        assert ZC.line(txt, "P1 ") == "P1 TL0 PASS predicted at 0.85, occurred: no, Brier 0.7225"; checks += 1
        # ---------------- decide-path boundaries (T1 T2 T6) on numpy scalars
        assert count_below([np.float64(-2.0), -2.0000001, -3.0, 0.0, -1.0]) == 2; checks += 1
        assert corpus_word(4) == "TREE-LIKE" and corpus_word(3) == "NOT" and tl0_decide({"massive": 5, "clinc": 3}) == "FAIL"; checks += 1
    assert checks == SELFTEST_CHECKS, "selftest ran %d checks, pinned %d" % (checks, SELFTEST_CHECKS)
    print("%s SELFTEST OK: %d value-asserting checks (pinned %d)" % (TAG, checks, SELFTEST_CHECKS))
    return 0


# ----------------------------------------------------------------------------------------------- main
def main(argv=None, ctx=None):
    ap = argparse.ArgumentParser(description="TREE-LIKE readout (zero calls; the intent arms read no pool; --mmlu is a pool reader)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--mmlu", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--data-root", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        res = ZC.run_mutants(os.path.abspath(__file__), MUTANTS)
        return 0 if all(r[2] == "killed" for r in res) else 1
    if ctx is None:
        ctx = Ctx(data_root=os.path.abspath(a.data_root) if a.data_root else ROOT, mmlu=a.mmlu)
    if a.dry_run:
        return dry_run(ctx)
    tag = "tree_like_mmlu" if ctx.mmlu else "tree_like"
    return run(ctx, a.out or ZC.default_out(tag, tag + "_outcome.txt"))


if __name__ == "__main__":
    sys.exit(main())
