"""EMBEDDER-CROSS-FLAT, leg E0b (E0b-CPU = RP15a, E0b-EMBED = RP15b): flat partitions in other embedding spaces, no builds.

REGISTRATION OF RECORD: docs/judge_v2_program.md section "## Registered 2026-09-27 (before any code or call) — EMBEDDER-CROSS-FLAT:
is the FLAT partition result (and the tree's filing) a property of qwen3's space or of the method ..." (L21705-L21730 _as_of
parent b9491bf), with the author's decision (b) (section "## Registrar's record 2026-09-27 ... the author's decisions (a)-(c)",
L21837: nomic-embed-text v1.5 and embeddinggemma; PRIMARY = RAW, card-conformant = REGISTERED SECONDARY; mxbai NOT decided),
ruling 19 (L21876: explicit flag + model, native-dimension / coverage refusal, a sha256 pin of each arm file bracketed by the
registrar; the read refuses on a mismatch), the data-steward's 3,504 correction (L21837, L21901, L21912: the registered read set
is fit 8,125 U held-out 3,445 U keyed = 11,687 texts), and READY_emb_target 6202766 C-ET-3 / C-ET-4 (every non-qwen3 read through
embedder_arms.open_arm_reader: copy-only, provenance, the registrar's pin). The registration governs; this docstring restates it.
E1 (RP09, the nomic build) is OUT OF SCOPE here (see "E1" at the end). ZERO judge calls. The EMBED part posts FLOOR_N = 500
EMBEDDING requests to the local Ollama (the qwen3 re-embed reproducibility floor), never a judge call.

WHAT IS COMPUTED (per part; PARTS below)
  spaces: qwen3_raw (the DB of record, no flag, ruling R2), nomic_raw, tfidf (TF-IDF -> SVD-256, fitted on the 8,125 fit texts
  only) in part cpu; qwen3_raw, nomic_raw, nomic_card, gemma_raw, gemma_card in part embed (nomic_raw again so F1 reads both
  families in one outcome; mxbai printed NOT RUN). Every vector sliced to 256 and renormalised (the readers' rule).
  partitions: V (vMF EM, flat_mix_mmlu.vmf_em; a degenerate seed REFUSES, ruling B6 inherited) and K (spherical k-means) at
  k in KS = (14, 82), seeds 0-4, fitted on the 8,125 fit texts only.
  M1 purity on the 3,445 held-out (cell majority from the 8,125 FIT texts' categories; D2), per-question hits; M2 = F6 LOO key
  information on the 10,925 keyed questions (flat_mix_mmlu.m2_block); the paired 95% CI: M1 by the twin-group bootstrap
  (flat_mix_mmlu.twin_boot_ci on stem_key groups), M2 by free_tests_f4_f7.boot_mean_ci (FLAT's forms).
  CRITERION (per non-qwen3 space S, k, M): WORSE_S,k FIRES iff M(V_S) - M(V_qwen3) < -spread_qwen3(M) AND the paired CI's
  upper end < 0 (flat_mix_mmlu.loss, the FLAT L1 form; strict inequalities). Otherwise printed "not shown worse beyond
  max(MDE, spread) = x" (no TOST registered). spread_qwen3(M) = max - min of M over qwen3's V seeds 0-4 at that k.
  FALSIFIER F1 (part embed only): fires iff >= 2 of the 3 non-qwen3 FAMILIES are WORSE on M2 at k = 14; families = the PRIMARY
  raw arms nomic_raw, gemma_raw; mxbai NOT RUN (not decided) counts as not WORSE, so F1 fires iff both (the registrar's reading,
  L21837). Card arms are SECONDARY: WORSE printed, never counted in F1. Part cpu prints "F1 NOT SCORED".
  PREDICTIONS: P1 (nomic_raw - qwen3, k 14, M1; part cpu), P2 (tfidf - qwen3; part cpu), P5 (F1; part embed), P6 (mutual
  kNN@10 qwen3-nomic_raw in [0.25, 0.55]; part cpu), each scored HELD / FAILED with its value; P3 / P4 are E1: NOT SCORED here.
  GEOMETRY (printed, NOT scored; EMB-03): anisotropy (mean pairwise cosine) raw and centred, participation ratio, mutual kNN@10
  and linear CKA of each space against qwen3, on the 8,125 fit texts at 256-d.
  CONFOUNDS (printed per arm): prefix policy, layer_norm, context truncation (D5 proxy), quantisation (registration: only qwen3
  is Q4), the Ollama tag digest now (D6).
  SUPPORT READOUT: the registered denominators, DEFF (Kish m-bar of the held-out twin groups, measured), n_eff, SE, MDE80 and
  the registered verdict line (f), beside the measured bars max(MDE, spread_qwen3).

HYGIENE AND GUARDS: the pool of record printed first (pool_guard.assert_pool_of_record); fit n 8,125 / held-out 3,445 / keyed
10,925 / read set 11,687 ASSERTED (the registration and the 3,504 correction); no held-out text or stem_key in the fit (REFUSED
otherwise); qwen3 read in place (open_arm_reader returns None); every other arm ONLY through embedder_arms.open_arm_reader (its
--target-dir copy, provenance, the registrar's pin in experiment_configs/embedder_cross_arm_pins.json: a null or different
sha256 REFUSES, at --dry-run too) and embedder_arms.arm_read_guard (every needed text, native dimension). The flat_mix globals and
sqlite3.connect are restored after each arm. Outcome and CSV are write-once (mode x); --run refuses before any work if either
exists. The imported instrument files are pinned (IMPORT_PINS; refused on a mismatch).

LAUNCH SEQUENCE (run-operator; zero judge calls; rule 7: one reader window, no construction running)
  python tools/analysis/embedder_cross_flat.py --selftest
  python tools/analysis/embedder_cross_flat.py --mutants
  python tools/analysis/embedder_cross_flat.py --dry-run --part cpu --target-dir experiment_results/embedder_cross
  python tools/analysis/embedder_cross_flat.py --run --part cpu --target-dir experiment_results/embedder_cross
  (after the gemma / card --go runs and the registrar's pins:) the same two lines with --part embed

BUILDER DECLARATIONS (handed to the registrar; none changes a registered word):
  D1 V_S and V_qwen3 in the criterion are the seed-0 partitions (the FLAT L1 form pairs one partition against the reference V0);
     the mean over seeds 0-4 and K0 are printed DESCRIPTIVE.
  D2 M1's cell majority comes from the 8,125 FIT texts (the registered read set), not FLAT-MIX-MMLU's "every other mmlu_pro row";
     so the record's spread 0.0305 is printed beside the measured spread, never used.
  D3 TF-IDF: sklearn TfidfVectorizer(lowercase, min_df 2, sublinear_tf) + TruncatedSVD(256, randomized, n_iter 7, seed 0), both
     fitted on the 8,125 fit texts only.
  D4 the reproducibility floor = the first FLOOR_N fit texts by sha256(text), re-embedded through /api/embed with
     qwen3-embedding:latest; printed: min / median / mean cosine after slice-256 + renormalise against the stored vectors, and
     the count below 0.9999 (DESCRIPTIVE; the registration names the floor, not its readout).
  D5 context truncation is a PROXY: texts with ceil(chars / 4) > the model's context (CONTEXT_TOKENS, unsourced); no tokenizer.
  D6 the tag digest is read from Ollama's /api/tags at the run (UNAVAILABLE if the server is down); the arm file's sha256 pin is
     the provenance of the vectors, the digest is printed beside it.
  D7 P1 / P2 are scored HELD iff the observed value lies inside the registered 80% interval; P6 HELD iff inside [0.25, 0.55].

[2026-09-29, the engine-coder, after READY_emb_e0b cd85961; insertion only, the text above stands]
  D2 RULED by the orchestrator: the 8,125-text read set is kept (not extended); the purity column is labelled M1' in every output
     (outcome lines, P1 / P2, the CSV header) with the note M1P_NOTE; FLAT's 0.0305 / 0.00663 are printed NOMINAL. The registrar
     brackets it.
  C-E0B-3: st_contrast makes qwen3's seed 0 the unique extreme and K differ from V (kills OM1 / OM2); the synthetic keyed set spans
     fit, held-out and keyed-only texts; every partition's M2 n is ASSERTED equal to the keyed count (assert_m2_n; 10,925 on real
     data), printed on the FITTED line and in the CSV (M2_n) (kills OM8).
  C-E0B-2: every WORSE line carries SCOREABLE / DESCRIPTIVE-ONLY against the MEASURED bar max(MDE, spread_qwen3) (support_tag); the
     registered (f) is printed verbatim and labelled NOMINAL, then RE-DERIVED on this instrument's spread (rederive_f).
     D8: a line with no registered prior (every M2 line, every k 82 line, gemma, cards) is DESCRIPTIVE-ONLY; F1 (on M2) therefore
     reads DESCRIPTIVE-ONLY lines: for the registrar.
  C-E0B-4: part embed REFUSES (dry-run and run) unless Ollama's /api/tags lists qwen3-embedding:latest (ollama_preflight); the
     500-text floor runs BEFORE the fits, so an Ollama fault costs no fit.
  C-E0B-5: every non-qwen3 arm's registrar pin is checked right after the pool line (early_pins), before the read set and the
     DB-of-record read.
  C-E0B-6: each WORSE line prints its realised SE ((hi - lo) / 3.92 of its own CI) and MDE80 = 2.8 x SE.
  C-E0B-7: embedder_arms.write_provenance now records the model's tag digest at the --go (model_digest); each ARM line prints it
     ("NOT RECORDED" for copies written before, e.g. gemma_raw at 2332d29) beside today's digest (confound lines).

[2026-09-29, the engine-coder, after READY_emb_conn_e0b2 38f0fd0; insertion only, the text above stands]
  C-E0B2-2: support_tag's bar = max(registered MDE, MEASURED spread_qwen3, the line's realised MDE80), the three legs printed;
     E0-TAG makes each leg decide once (kills the reviewer's OMX1). Which P1 label governs if the registered (f) and the
     re-derived one disagree is the registrar's (pre-data).
  C-E0B2-3: a non-firing F1 line carries F1_NOT_SHOWN ("not shown; no support computed for M2 contrasts ...") and never names
     the SQ5 wording; a firing F1 line is unchanged.
  C-CONN-1 / C-CONN-2 (LOW) are embedder_arms.py items, NOT done here (the file is in use by a run-operator; the orchestrator's
     instruction).

[2026-09-29, the engine-coder, after the E0b embed REFUSAL at ee3a40f (gemma_raw k 82, V seeds 3-4, B6) and the orchestrator's
ruling (a); insertion only, the text above stands]
  Ruling (a), pre-data, a narrowing like O2: a V seed that flat_mix_mmlu.vmf_em refuses under ruling B6 VOIDs the WHOLE (arm, k)
     cell (fit_space -> voids): printed "VOID (ruling B6)", none of its V / K partitions kept, every contrast on it NA and excluded
     from every summary (cell_void: its own VOID or the reference qwen3's at that k); F1 / P1 / P2 read NOT SCORED only if their
     own (arm, first k) cell is VOID; the CSV carries one VOID row per cell. No replacement seed, no clamp, no estimator change;
     flat_mix_mmlu.py untouched (it still refuses for its own callers). A non-B6 refusal still propagates.
  EXIT STATUS: entry() returns 2 on any refusal and prints "[E0B] EXIT 2 (REFUSED)" last (the rc=0 at ee3a40f is what a shell pipe
     without pipefail reports: the operator's log line should record ${PIPESTATUS[0]}).
  C-E0B3-2: E0-SPREAD runs part cpu on a stub whose qwen3 V spread is 0.25, so the call-site OMX1 (the run passing spread 0) dies.

E1 (RP09; not built here): the N-raw / N-card builds need the JVM to read nomic's vectors. N-raw reads the repo-root nomic file
by -Dtaxoadapt.llm.embedding-model (no copy needed). N-card needs -Dtaxoarena.embeddingCacheFile=<the card copy> (C-ET-5), but a
construction WRITES the file it reads (EmbeddingCache.putQuery; raw misses), which changes the sha256 the registrar pinned, so
every later E0b / Python read of that copy REFUSES. E1 needs EITHER a JVM working copy (a byte copy of the pinned card file,
sha256 printed before and after, never read by E0b) OR a registered read-only EmbeddingCache mode (putQuery and saveBatchToDisk
refused under the explicit property). The choice is the registrar's / author's.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import io
import sys
import csv
import json
import math
import time
import struct
import sqlite3
import hashlib
import argparse
import tempfile
import contextlib
import urllib.request
from collections import namedtuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

TAG = "[E0B]"
IMPORT_PINS = {"embedder_arms.py": ("2073d1315981a30464037913b85ce2bf8838aa00", "82836509285bde16"),   # EMB-PACE 2026-09-30 (was 0546800f / 4bfd77986e4bfb92)
               "flat_mix_mmlu.py": ("555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2", "b80cec50c2eef49d")}


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


for _f, (_b, _l) in IMPORT_PINS.items():          # the imported instrument is the pinned one, or nothing runs
    _p = pins_of(os.path.join(HERE, _f))
    if _p["blob"] != _b or _p["lf16"] != _l:
        refuse("pin mismatch on tools/analysis/%s: %s, pinned blob:%s / sha256-lf16:%s" % (_f, fmt_pins(_p), _b[:8], _l))
import flat_mix_mmlu as FM      # noqa: E402  (its own import pins; installs the read-only connect guard)
import embedder_arms as EA      # noqa: E402
AF, F, EG = FM.AF, FM.F, EA.EG

POOL_ID = FM.POOL_ID
KS = (14, 82)
SEEDS = (0, 1, 2, 3, 4)
DIM = 256
PARTS = {"cpu": ("qwen3_raw", "nomic_raw", "tfidf"),
         "embed": ("qwen3_raw", "nomic_raw", "nomic_card", "gemma_raw", "gemma_card")}
FAMILIES = (("nomic", "nomic_raw"), ("gemma", "gemma_raw"), ("mxbai", None))      # None: NOT RUN (not decided)
EXPECT = dict(fit=8125, heldout=3445, keyed=10925, read=11687)
SUPPORT = dict(se_m1=0.00663, se_m2=0.357e-3, mde_m1=0.0186, mde_m2=1.00e-3, record_spread_m1=0.0305, deff_m1=1.0)
P1 = (-0.020, (-0.050, 0.010), 0.40)
P2 = (-0.08, (-0.15, -0.03), 0.85)
P5_PROB = 0.35
P6 = ((0.25, 0.55), 0.70)
CONTEXT_TOKENS = {"qwen3-embedding:latest": 32768, "nomic-embed-text:latest": 2048, "embeddinggemma:latest": 2048}
QWEN3 = "qwen3-embedding:latest"
FLOOR_N = 500
FLOOR_BAR = 0.9999
KNN = 10
OUT_DIR = os.path.join(ROOT, "experiment_results", "embedder_cross_flat")
VERDICT_F = ("(f) VERDICT LINE (registered): E0b nomic-vs-qwen3 at k 14 on M1 DESCRIPTIVE-ONLY (P1 -0.020 lies inside max(0.0186, "
             "spread) on the record's spread 0.0305); TF-IDF floor SCOREABLE (P2 -0.08 beyond 0.0305); every cross-arm contrast "
             "DESCRIPTIVE-ONLY.")

ML = {"m1": "M1'", "m2": "M2"}     # D2 (orchestrator's ruling 2026-09-29): E0b's purity is M1' (majority from the 8,125 fit texts)
M1P_NOTE = ("M1' (D2; the orchestrator's ruling, bracketed by the registrar): purity on the 3,445 held-out with each cell's "
            "majority from the 8,125 FIT texts; FLAT-MIX-MMLU's M1 (majority from its 8,324 train texts) is NOT computed; the "
            "read set is not extended")
PRIORS = {("nomic_raw", "m1"): P1[0], ("tfidf", "m1"): P2[0]}     # the registered priors at the first k (Support (f))
F1_NOT_SHOWN = ("; not shown; no support computed for M2 contrasts (registration (f): every cross-arm contrast DESCRIPTIVE-ONLY): "
                "a non-firing F1 is not evidence about the SQ5 wording (READY_emb_conn_e0b2 D8 ruling, C-E0B2-3)")
World = namedtuple("World", "fit heldout keyed")        # fit / heldout: [(text, category)]; keyed: F.keyed_questions()


def say(L, s=""):
    print(s)
    L.append(s)


# ------------------------------------------------------------------------------------------------ the world (real data)
def real_world():
    """The registered read set: af_clean_s42's 8,125 root texts (flat_mix_mmlu.fit_set, on the DB of record's queries), the
    pool's 3,445 held-out (anchor_free_readout.corpus) and the 10,925 keyed questions (free_tests_f4_f7.keyed_questions)."""
    texts, _g, _ids, _t = FM.fit_set()
    train, heldout, _cs = AF.corpus(POOL_ID)
    cat = dict(train)
    miss = [t for t in texts if t not in cat]
    if miss:
        refuse("%d fit texts carry no mmlu_pro category among the corpus's train texts" % len(miss))
    return World([(t, cat[t]) for t in texts], heldout, F.keyed_questions())


def needed_texts(W):
    return sorted(set(t for t, _ in W.fit) | set(t for t, _ in W.heldout) | set(W.keyed[3].values()))


def check_counts(W, L, expect):
    got = dict(fit=len(W.fit), heldout=len(W.heldout), keyed=len(W.keyed[4]), read=len(needed_texts(W)))
    say(L, "READ SET: fit %d, held-out %d, keyed %d, read set %d distinct texts (registered 8,125 / 3,445 / 10,925 / 11,687 after the "
           "data-steward's 3,504 correction)" % (got["fit"], got["heldout"], got["keyed"], got["read"]))
    if expect is not None:
        bad = {k: (got[k], v) for k, v in expect.items() if got[k] != v}
        if bad:
            refuse("the read set differs from the registration: %s (got, registered)" % bad)
    return got


def hygiene(W, L):
    fit = set(t for t, _ in W.fit)
    ho = [t for t, _ in W.heldout]
    exact = sum(1 for t in set(ho) if t in fit)
    fk = set(FM.split_side.stem_key(t) for t in fit)
    keys = sum(1 for t in set(ho) if FM.split_side.stem_key(t) in fk)
    say(L, "HYGIENE: held-out texts in the fit %d; held-out stem_keys in the fit %d (both must be 0: no held-out question enters "
           "any fit)" % (exact, keys))
    if exact or keys:
        refuse("%d held-out texts / %d stem_keys are in the fit set" % (exact, keys))


# ------------------------------------------------------------------------------------------------ arms
@contextlib.contextmanager
def fm_session():
    """One arm's read: flat_mix's embedding globals, AF / F's DB paths and sqlite3.connect restored afterwards."""
    saved = {k: getattr(FM, k) for k in FM._EMB_GLOBALS}
    saved_af, saved_f, saved_c = AF.EMB_DB, F.EMB_DB, sqlite3.connect
    try:
        yield
    finally:
        sqlite3.connect = saved_c
        for k, v in saved.items():
            setattr(FM, k, v)
        AF.EMB_DB, F.EMB_DB = saved_af, saved_f


def unit(v):
    v = np.asarray(v, dtype=np.float64)[:DIM]
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def load_arm(name, need, target_dir, data_root, L):
    """-> ({text: 256-d unit vector}, info). qwen3 in place; every other arm ONLY through embedder_arms.open_arm_reader."""
    arm = EA.ARMS[name]
    buf = io.StringIO()
    with fm_session(), contextlib.redirect_stdout(buf):
        if name == "qwen3_raw":
            if EA.open_arm_reader(FM, name, target_dir, data_root) is not None:
                refuse("qwen3_raw must be read in place with no flag (ruling R2)")
            db = os.path.join(data_root, EG.DB_OF_RECORD)
            AF.EMB_DB = db
        else:
            db = EA.open_arm_reader(FM, name, target_dir, data_root)
        con = pool_guard.open_ro(db)
        try:
            EA.arm_read_guard(con, arm, need)
        finally:
            con.close()
        full = AF.full_vectors(need)
        sha = EA._sha(db)
    for line in buf.getvalue().splitlines():
        say(L, "  " + line)
    native = {len(v) for v in full.values()}
    dg = "n/a (the DB of record)"
    if name != "qwen3_raw":
        with open(db + EA.PROVENANCE_SUFFIX, encoding="utf-8") as f:
            dg = json.load(f).get("model_digest") or "NOT RECORDED (written before C-E0B-7)"
    say(L, "ARM %s (%s, %s): file %s sha256 %s; %d vectors, native dim %s; sliced to %d and renormalised; model digest at the --go %s"
        % (name, arm.model, arm.role, os.path.basename(db), sha, len(full), sorted(native), DIM, dg))
    return {t: unit(full[t]) for t in need}, dict(db=db, sha=sha, model=arm.model, role=arm.role)


def tfidf_space(W, need, L):
    """D3: TF-IDF -> SVD-256 fitted on the fit texts ONLY; every needed text transformed; rows unit-normalised."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    fit_texts = [t for t, _ in W.fit]
    tv = TfidfVectorizer(lowercase=True, min_df=2, sublinear_tf=True)
    A = tv.fit_transform(fit_texts)
    if A.shape[1] <= DIM:
        refuse("TF-IDF vocabulary %d <= %d: SVD-%d undefined" % (A.shape[1], DIM, DIM))
    svd = TruncatedSVD(n_components=DIM, algorithm="randomized", n_iter=7, random_state=0).fit(A)
    Z = FM.unit_rows(svd.transform(tv.transform(need)))
    say(L, "ARM tfidf (TF-IDF -> SVD-%d, fitted on the %d fit texts only): vocabulary %d; explained variance %.4f"
        % (DIM, len(fit_texts), A.shape[1], float(svd.explained_variance_ratio_.sum())))
    return {t: Z[i] for i, t in enumerate(need)}, dict(db=None, sha=None, model="tfidf-svd256", role="FLOOR")


# ------------------------------------------------------------------------------------------------ partitions and measures
def fit_space(X, ks, seeds):
    """-> (parts, voids). The orchestrator's ruling (a) of 2026-09-29 (pre-data; a narrowing like O2): a V seed that
    flat_mix_mmlu.vmf_em refuses under ruling B6 VOIDs that WHOLE (arm, k) cell: none of its V or K partitions is kept, every
    contrast on it reads NA and it enters no summary; the other k run. No replacement seed, no clamp, no estimator change;
    flat_mix_mmlu itself is unchanged (it still refuses for its own callers). Any other refusal propagates."""
    parts, voids = {}, {}
    for k in ks:
        cell = {}
        for s in seeds:
            try:
                r = FM.vmf_em(X, k, s)
            except SystemExit as e:
                if FM.B6 not in str(e):
                    raise
                voids[k] = str(e).split("REFUSED: ", 1)[-1].split(";")[0]
                break
            cell[("V", k, s)] = dict(rule="map", mu=r["mu"], kappa=r["kappa"], pi=r["pi"], iters=r["iters"], converged=r["converged"])
            r = FM.spherical_kmeans(X, k, s)
            cell[("K", k, s)] = dict(rule="nearest", centers=r["centers"], iters=r["iters"], converged=r["converged"])
        if k not in voids:
            parts.update(cell)
    return parts, voids


def cell_void(voids, n, k):
    """The reason (arm, k) reads NA: its own VOID, or the reference qwen3's VOID at that k; None when both are live."""
    if k in voids.get(n, {}):
        return "%s k %d VOID (ruling B6)" % (n, k)
    if k in voids.get("qwen3_raw", {}):
        return "the reference qwen3_raw k %d VOID (ruling B6)" % k
    return None


def assign_fn(p):
    if p["rule"] == "map":
        return lambda Q: list(FM.map_assign(Q, p["mu"], p["kappa"], p["pi"]))
    return lambda Q: list(FM.nearest_assign(Q, p["centers"]))


def measure_space(vec, W, parts):
    Xf = np.stack([vec[t] for t, _ in W.fit])
    Xh = np.stack([vec[t] for t, _ in W.heldout])
    veck = {t: vec[t] for t in W.keyed[3].values()}
    out = {}
    for key, p in parts.items():
        fn = assign_fn(p)
        sc, hits, _kh = FM.m1_block(fn, Xf, Xh, W.fit, W.heldout)
        m2 = FM.m2_block(fn, W.keyed, veck)
        out[key] = dict(m1=sc["acc"], per1=hits, m2=m2["mean"], per2=m2["per_q"], n2=m2["n"], iters=p["iters"], converged=p["converged"])
    return out


def assert_m2_n(name, parts_m, n_keyed):
    """C-E0B-3: every partition's M2 is scored on the whole keyed set (the registered denominator, 10,925 on real data)."""
    n2 = sorted(set(m["n2"] for m in parts_m.values()))
    if n2 != [n_keyed]:
        refuse("space %s: M2 scored on %s keyed questions, the registered denominator is %d (C-E0B-3)" % (name, n2, n_keyed))
    return n2[0]


def worse(diff, spr, lo, hi):
    """The registered criterion (the FLAT L1 form): diff < -spread AND the paired CI's upper end < 0."""
    return FM.loss(diff, spr, lo, hi)


def contrast(ms, mq, groups, k, metric):
    """S minus qwen3 on seed 0 (D1), the paired CI, and qwen3's spread over its V seeds at k."""
    a, b = ms[("V", k, 0)], mq[("V", k, 0)]
    if metric == "m1":
        d = a["per1"] - b["per1"]
        lo, hi = FM.twin_boot_ci(d, groups)
        diff = float(d.mean())
    else:
        common = [q for q in a["per2"] if q in b["per2"]]
        d = np.array([a["per2"][q] - b["per2"][q] for q in common])
        lo, hi = F.boot_mean_ci(d)
        diff = float(d.mean())
    spr = FM.spread([mq[("V", k, s)][metric] for s in SEEDS])
    return dict(diff=diff, lo=lo, hi=hi, spread=spr, fires=worse(diff, spr, lo, hi),
                mean_diff=float(np.mean([ms[("V", k, s)][metric] - mq[("V", k, s)][metric] for s in SEEDS])),
                k0_diff=float(ms[("K", k, 0)][metric] - mq[("K", k, 0)][metric]),
                spread_S=FM.spread([ms[("V", k, s)][metric] for s in SEEDS]))


def support_tag(n, k, metric, spread, mde80, k14):
    """C-E0B-2 / C-E0B2-2: SCOREABLE iff a registered prior exists for this arm / metric at the first k and lies beyond the bar
    max(registered MDE, MEASURED spread_qwen3, realised MDE80 of this line); DESCRIPTIVE-ONLY otherwise (no registered prior = no
    support computed; D8). The three legs are printed."""
    pr = PRIORS.get((n, metric)) if k == k14 else None
    if pr is None:
        return "DESCRIPTIVE-ONLY (no registered prior)"
    reg = mde(metric)
    bar = max(reg, spread, mde80)
    return "%s (prior %s vs bar %s = max(registered MDE %s, spread_qwen3 %s, realised MDE80 %s))" % (
        "SCOREABLE" if abs(pr) > bar else "DESCRIPTIVE-ONLY", fmt_m(metric, pr), fmt_m(metric, bar).lstrip("+"),
        fmt_m(metric, reg).lstrip("+"), fmt_m(metric, spread).lstrip("+"), fmt_m(metric, mde80).lstrip("+"))


def rederive_f(C, k14, L):
    parts = []
    for n, what in (("nomic_raw", "E0b nomic-vs-qwen3"), ("tfidf", "TF-IDF floor")):
        if (n, k14, "m1") not in C:
            continue
        c = C[(n, k14, "m1")]
        parts.append("%s at k %d on M1' %s" % (what, k14, "NA (VOID, ruling B6)" if c is None else c["tag"]))
    say(L, "(f) RE-DERIVED with this instrument's spread (C-E0B-2): %s; every other WORSE line DESCRIPTIVE-ONLY (no registered prior)"
        % ("; ".join(parts) if parts else "no primed arm in this part"))


def mde(metric):
    return SUPPORT["mde_m1"] if metric == "m1" else SUPPORT["mde_m2"]


def fmt_m(metric, x):
    return ("%+.4f" % x) if metric == "m1" else ("%+.3fe-3" % (1000 * x))


# ------------------------------------------------------------------------------------------------ geometry (printed, not scored)
def anisotropy(X):
    n = X.shape[0]
    s = X.sum(axis=0)
    return float((s @ s - n) / (n * (n - 1)))


def participation_ratio(X):
    ev = np.clip(np.linalg.eigvalsh(np.cov(X, rowvar=False)), 0, None)
    return float(ev.sum() ** 2 / (ev ** 2).sum())


def knn_sets(X, k=KNN, chunk=1000):
    out = []
    for s in range(0, X.shape[0], chunk):
        S = X[s:s + chunk] @ X.T
        for i in range(S.shape[0]):
            S[i, s + i] = -np.inf                       # a text is never its own neighbour
        idx = np.argpartition(-S, k, axis=1)[:, :k]
        out.extend(set(r.tolist()) for r in idx)
    return out


def mutual_knn(Xa, Xb, k=KNN):
    A, B = knn_sets(Xa, k), knn_sets(Xb, k)
    return float(np.mean([len(a & b) / k for a, b in zip(A, B)]))


def linear_cka(Xa, Xb):
    A = Xa - Xa.mean(axis=0)
    B = Xb - Xb.mean(axis=0)
    num = np.linalg.norm(A.T @ B, "fro") ** 2
    return float(num / (np.linalg.norm(A.T @ A, "fro") * np.linalg.norm(B.T @ B, "fro")))


# ------------------------------------------------------------------------------------------------ confounds / floor
def fetch_tags():
    """D6: Ollama's /api/tags (a local listing, not an embedding and never a judge call) -> {name: digest} or None."""
    url = EA.OLLAMA_URL[:-len("/api/embed")] + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return {m.get("name"): m.get("digest") for m in json.loads(r.read().decode("utf-8")).get("models", [])}
    except Exception:                                   # noqa: BLE001  (printed UNAVAILABLE)
        return None


def confound_lines(names, need, L):
    tags = fetch_tags()
    say(L, "CONFOUNDS (per arm; printed, not scored): prefix policy, layer_norm, context truncation (D5 proxy ceil(chars/4) > "
           "context), quantisation (registration: only qwen3 is Q4), Ollama tag digest now (D6)")
    for n in names:
        if n == "tfidf":
            say(L, "  tfidf: no model (lexical floor)")
            continue
        a = EA.ARMS[n]
        ctx = CONTEXT_TOKENS[a.model]
        over = sum(1 for t in need if math.ceil(len(t) / 4.0) > ctx)
        dg = "UNAVAILABLE" if tags is None else (tags.get(a.model) or "NOT LISTED")
        say(L, "  %-10s prefix %r; layer_norm %s; texts over context %d of %d (context %d tokens, proxy); %s; digest %s"
            % (n, a.prefix or "none", a.layer_norm, over, len(need), ctx, "Q4" if a.model == QWEN3 else "not Q4", dg))


def repro_floor(qvec, W, L, embed_fn=None, n=None):
    """D4: re-embed the first n fit texts by sha256 through /api/embed (qwen3) and compare with the stored vectors."""
    n = FLOOR_N if n is None else n
    embed_fn = EA.ollama_embed if embed_fn is None else embed_fn
    texts = sorted((t for t, _ in W.fit), key=lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest())[:n]
    cos = []
    for s in range(0, len(texts), EA.BATCH):
        ch = texts[s:s + EA.BATCH]
        for t, e in zip(ch, embed_fn(QWEN3, list(ch))):
            cos.append(float(np.dot(unit(e), qvec[t])))
    cos = np.array(cos)
    say(L, "REPRODUCIBILITY FLOOR (D4, DESCRIPTIVE): %d fit texts re-embedded via /api/embed with %s: cosine after slice-%d + "
           "renormalise min %.6f, median %.6f, mean %.6f; below %.4f: %d" % (len(cos), QWEN3, DIM, cos.min(), float(np.median(cos)),
                                                                          cos.mean(), FLOOR_BAR, int((cos < FLOOR_BAR).sum())))
    return cos


# ------------------------------------------------------------------------------------------------ preconditions
def early_pins(names, target_dir, L):
    """C-E0B-5: every non-qwen3 arm's DIR copy equals the registrar's pin, checked right after the pool line: a null or
    different pin costs no read of the pool's texts and no read of the DB of record."""
    for n in names:
        if n in ("qwen3_raw", "tfidf"):
            continue
        if target_dir is None:
            refuse("arm %s is read only from its --target-dir copy (EMBEDDER-CROSS-FLAT; C-ET-3): no DIR given" % n)
        pth = os.path.join(os.path.abspath(target_dir), EA.cache_file(EA.ARMS[n]))
        if not os.path.isfile(pth):
            refuse("no --target-dir copy of arm %s at %s" % (n, pth))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            EA.registrar_pin(EA.ARMS[n], EA._sha(pth))
        for line in buf.getvalue().splitlines():
            say(L, "  " + line)
    say(L, "PINS: every non-qwen3 arm's copy equals the registrar's pin (checked before any read of the read set or the DB of record)")


def ollama_preflight(L):
    """C-E0B-4 (part embed): the floor needs qwen3-embedding:latest on the local Ollama; REFUSED (dry-run and run) otherwise."""
    tags = fetch_tags()
    if tags is None or QWEN3 not in tags:
        refuse("part embed: Ollama /api/tags %s: the %d-text reproducibility floor cannot run"
               % ("does not answer" if tags is None else "does not list %s" % QWEN3, FLOOR_N))
    say(L, "OLLAMA PREFLIGHT: /api/tags lists %s (digest %s)" % (QWEN3, tags[QWEN3]))


# ------------------------------------------------------------------------------------------------ the part
def run_part(part, W, target_dir, data_root, out_dir, L, expect=EXPECT, ks=KS, write=True, embed_fn=None, floor_n=None):
    """The deciding path of --run (and, with write=False and no fit, of --dry-run's reads). -> result dict."""
    names = PARTS[part]
    if write:
        outcome, arms_csv = (os.path.join(out_dir, "e0b_%s_outcome.txt" % part), os.path.join(out_dir, "e0b_%s_arms.csv" % part))
        for p in (outcome, arms_csv):
            if os.path.exists(p):
                refuse("%s exists: outcome files of record are WRITE-ONCE" % p)
    pid = pool_guard.assert_pool_of_record(POOL_ID)
    say(L, "pool %s (pool_guard.assert_pool_of_record)" % pid)
    say(L, "[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    say(L, "[SCRIPT] tools/analysis/embedder_cross_flat.py %s" % fmt_pins(pins_of(os.path.abspath(__file__))))
    for f in IMPORT_PINS:
        say(L, "[PIN] tools/analysis/%s %s (verified on import)" % (f, fmt_pins(pins_of(os.path.join(HERE, f)))))
    say(L, "EMBEDDER-CROSS-FLAT E0b part %s (%s); spaces %s; k %s; seeds %s; slice %d; zero judge calls"
        % (part, "RP15a" if part == "cpu" else "RP15b", ", ".join(names), list(ks), list(SEEDS), DIM))
    if part == "embed":
        say(L, "  mxbai: NOT RUN (not decided; the author's decision (b)); card arms are the REGISTERED SECONDARY")
    early_pins(names, target_dir, L)
    if part == "embed":
        ollama_preflight(L)
    say(L, M1P_NOTE)
    if callable(W):
        W = W()                                        # the real read set, loaded after the pool line
    check_counts(W, L, expect)
    hygiene(W, L)
    need = needed_texts(W)
    vecs, info = {}, {}
    for n in names:
        if n == "tfidf":
            vecs[n], info[n] = tfidf_space(W, need, L)
        else:
            vecs[n], info[n] = load_arm(n, need, target_dir, data_root, L)
    confound_lines(names, need, L)
    if not write:
        return dict(names=names, info=info)
    floor = None
    if part == "embed":                               # C-E0B-4: an Ollama fault costs no fit
        floor = repro_floor(vecs["qwen3_raw"], W, L, embed_fn=embed_fn, n=floor_n)
    Xfit = {n: np.stack([vecs[n][t] for t, _ in W.fit]) for n in names}
    ms, voids = {}, {}
    for n in names:
        t0 = time.perf_counter()
        parts, voids[n] = fit_space(Xfit[n], ks, SEEDS)
        ms[n] = measure_space(vecs[n], W, parts)
        n2 = assert_m2_n(n, ms[n], len(W.keyed[4])) if ms[n] else 0
        say(L, "FITTED %s: %d partitions on %d fit texts (%.1f s); M2 n %d of %d keyed"
            % (n, len(ms[n]), Xfit[n].shape[0], time.perf_counter() - t0, n2, len(W.keyed[4])))
        for k, why in sorted(voids[n].items()):
            say(L, "  %s k %d: VOID (ruling B6): %s; the whole (arm, k) cell is VOID: every contrast on it reads NA and is excluded "
                   "from every summary (the orchestrator's ruling (a)); no replacement seed" % (n, k, why))
    groups, G = FM.twin_groups([t for t, _ in W.heldout])
    mbar = FM.kish_mbar(groups)
    say(L, "")
    say(L, "SUPPORT: denominators M1' %d held-out (%d stem_key twin groups; Kish m-bar %.4f = DEFF measured; n_eff %.0f), M2 %d keyed; "
           "registered SE M1 %.5f / M2 %.3fe-3, MDE80 M1 %.4f / M2 %.2fe-3 (FLAT's, NOMINAL for M1'); wrong(established) and tie conventions N/A (no judge)"
        % (len(W.heldout), G, mbar, len(W.heldout) / mbar, len(W.keyed[4]), SUPPORT["se_m1"], 1000 * SUPPORT["se_m2"],
           SUPPORT["mde_m1"], 1000 * SUPPORT["mde_m2"]))
    say(L, VERDICT_F + " [registered, verbatim; its premise 0.0305 is FLAT-MIX-MMLU's spread, NOMINAL here: re-derived below with "
           "this instrument's spread (C-E0B-2)]")
    say(L, "")
    say(L, "ARMS (V seed 0 / mean over seeds 0-4; M1' purity on %d, M2 F6 x1e-3 on %d)" % (len(W.heldout), len(W.keyed[4])))
    for n in names:
        for k in ks:
            if k in voids[n]:
                say(L, "  %-10s k %-3d VOID (ruling B6)" % (n, k))
                continue
            v0 = ms[n][("V", k, 0)]
            say(L, "  %-10s k %-3d V0 M1' %.4f M2 %+.3f | V mean M1' %.4f M2 %+.3f | K0 M1' %.4f M2 %+.3f"
                % (n, k, v0["m1"], 1000 * v0["m2"], np.mean([ms[n][("V", k, s)]["m1"] for s in SEEDS]),
                   1000 * np.mean([ms[n][("V", k, s)]["m2"] for s in SEEDS]), ms[n][("K", k, 0)]["m1"], 1000 * ms[n][("K", k, 0)]["m2"]))
    say(L, "")
    say(L, "CRITERION WORSE_S,k (registered): M(V_S) - M(V_qwen3) < -spread_qwen3(M) AND the paired 95%% CI's upper end < 0; "
           "V = seed 0 (D1); M = M1' (D2) or M2; record spread M1 %.4f NOMINAL, never used; each line carries its SUPPORT tag against the "
           "MEASURED bar max(MDE, spread_qwen3) and its realised SE / MDE80 (C-E0B-2, C-E0B-6)" % SUPPORT["record_spread_m1"])
    C = {}
    for n in names:
        if n == "qwen3_raw":
            continue
        for k in ks:
            for metric in ("m1", "m2"):
                why = cell_void(voids, n, k)
                if why is not None:
                    C[(n, k, metric)] = None
                    say(L, "  WORSE %s k=%d %s: NA (%s)" % (n, k, ML[metric], why))
                    continue
                c = contrast(ms[n], ms["qwen3_raw"], groups, k, metric)
                C[(n, k, metric)] = c
                bar = max(mde(metric), c["spread"])
                se = (c["hi"] - c["lo"]) / 3.92
                c["tag"] = support_tag(n, k, metric, c["spread"], 2.8 * se, ks[0])
                word = ("WORSE FIRES" if c["fires"] else "not shown worse beyond max(MDE, spread) = %s" % fmt_m(metric, bar).lstrip("+"))
                say(L, "  WORSE %s k=%d %s: diff %s, CI [%s, %s], spread_qwen3 %s -> %s [%s] | realised SE %s, MDE80 %s | "
                       "mean-over-seeds diff %s, K0 diff %s, spread_%s %s (descriptive)"
                    % (n, k, ML[metric], fmt_m(metric, c["diff"]), fmt_m(metric, c["lo"]), fmt_m(metric, c["hi"]),
                       fmt_m(metric, c["spread"]), word, c["tag"], fmt_m(metric, se).lstrip("+"), fmt_m(metric, 2.8 * se).lstrip("+"),
                       fmt_m(metric, c["mean_diff"]), fmt_m(metric, c["k0_diff"]), n, fmt_m(metric, c["spread_S"])))
    rederive_f(C, ks[0], L)
    say(L, "")
    k14 = ks[0]
    geo = geometry_lines(Xfit, names, L)
    say(L, "")
    res = dict(names=names, C=C, ms=ms, geo=geo, info=info, mbar=mbar, voids=voids)
    score_lines(part, res, k14, L)
    if floor is not None:
        res["floor"] = floor
    say(L, "")
    say(L, "E1 (RP09): out of scope of this script; P3 / P4 NOT SCORED here.")
    txt = "\n".join(L) + "\n"
    FM.write_once(outcome, txt)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["space", "kind", "k", "seed", "M1'", "M2", "M2_n", "iters", "converged"])
    for n in names:
        for (kind, k, s), m in sorted(ms[n].items()):
            w.writerow([n, kind, k, s, repr(m["m1"]), repr(m["m2"]), m["n2"], m["iters"], m["converged"]])
        for k in sorted(voids[n]):
            w.writerow([n, "VOID", k, "", "VOID (ruling B6)", "VOID (ruling B6)", "", "", ""])
    FM.write_once(arms_csv, buf.getvalue())
    print("%s wrote %s and %s (write-once)" % (TAG, outcome, arms_csv))
    res["outcome"] = outcome
    return res


def geometry_lines(Xfit, names, L):
    say(L, "GEOMETRY (fit texts, %d-d; printed, NOT scored; EMB-03)" % DIM)
    g = {}
    for n in names:
        X = Xfit[n]
        Xc = FM.unit_rows(X - X.mean(axis=0))
        g[n] = dict(aniso=anisotropy(X), aniso_c=anisotropy(Xc), pr=participation_ratio(X))
        if n != "qwen3_raw":
            g[n]["knn"] = mutual_knn(Xfit["qwen3_raw"], X)
            g[n]["cka"] = linear_cka(Xfit["qwen3_raw"], X)
        say(L, "  %-10s anisotropy %.4f (centred %.4f); participation ratio %.2f%s" % (
            n, g[n]["aniso"], g[n]["aniso_c"], g[n]["pr"],
            "" if n == "qwen3_raw" else "; vs qwen3: mutual kNN@%d %.4f, linear CKA %.4f" % (KNN, g[n]["knn"], g[n]["cka"])))
    return g


def inside(x, iv):
    return bool(iv[0] <= x <= iv[1])


def score_lines(part, res, k14, L):
    C, geo = res["C"], res["geo"]
    say(L, "PREDICTIONS (priors; scored HELD / FAILED, D7)")
    if part == "cpu":
        for pid, n, (pt, iv, pw) in (("P1", "nomic_raw", P1), ("P2", "tfidf", P2)):
            c = C[(n, k14, "m1")]
            if c is None:
                say(L, "%s NOT SCORED: %s at k %d is VOID (ruling B6); excluded" % (pid, n, k14))
                continue
            say(L, "%s %s: %s minus qwen3 at k %d, M1' = %+.4f (prior %+.3f, 80%% [%+.3f, %+.3f]); WORSE fired: %s (prior %.2f)"
                % (pid, "HELD" if inside(c["diff"], iv) else "FAILED", n, k14, c["diff"], pt, iv[0], iv[1],
                   "yes" if c["fires"] else "no", pw))
        kn = geo["nomic_raw"]["knn"]
        say(L, "P6 %s: mutual kNN@%d qwen3-nomic_raw = %.4f (prior [%.2f, %.2f], %.2f)"
            % ("HELD" if inside(kn, P6[0]) else "FAILED", KNN, kn, P6[0][0], P6[0][1], P6[1]))
        say(L, "P5 NOT SCORED in part cpu (F1 is read after E0b-EMBED)")
        say(L, "FALSIFIER F1 NOT SCORED: E0b-CPU alone reads the nomic family only (registration)")
        res["F1"] = None
        return
    say(L, "P1, P2, P6: scored in part cpu")
    gone = [arm for _f, arm in FAMILIES if arm is not None and C[(arm, k14, "m2")] is None]
    if gone:
        say(L, "FALSIFIER F1 NOT SCORED: %s at k %d VOID (ruling B6); excluded (the orchestrator's ruling (a))" % (", ".join(gone), k14))
        say(L, "P5 NOT SCORED: F1 not scored")
        res["F1"] = None
        return
    fam = []
    for fname, arm in FAMILIES:
        if arm is None:
            fam.append((fname, False, "NOT RUN (not decided): counted as not WORSE"))
            continue
        c = C[(arm, k14, "m2")]
        fam.append((fname, bool(c["fires"]), "%s M2 k %d diff %s: %s" % (arm, k14, fmt_m("m2", c["diff"]),
                                                                         "WORSE" if c["fires"] else "not WORSE")))
    nw = sum(1 for _, w, _ in fam if w)
    f1 = nw >= 2
    say(L, "FALSIFIER F1 %s: %d of 3 non-qwen3 embedding families WORSE beyond spread on M2 at k = %d (%s)%s"
        % ("FIRES" if f1 else "does not fire", nw, k14, "; ".join("%s: %s" % (f, d) for f, _, d in fam),
           ": the partition and key-information results are then qwen3-space properties (overturns the planned SQ5 wording "
           "'the method's' for the FLAT clause, no recorded number)" if f1 else F1_NOT_SHOWN))
    for arm in ("nomic_card", "gemma_card"):
        c = C[(arm, k14, "m2")]
        say(L, "  SECONDARY %s M2 k %d: %s (not counted in F1)" % (arm, k14, "NA (VOID, ruling B6)" if c is None
                                                                   else "WORSE" if c["fires"] else "not WORSE"))
    say(L, "P5 %s: F1 fired: %s (prior %.2f)" % ("HELD" if f1 else "FAILED", "yes" if f1 else "no", P5_PROB))
    res["F1"] = f1


# ------------------------------------------------------------------------------------------------ dry run
def dry_run(part, W, target_dir, data_root, L, expect=EXPECT):
    say(L, "[MODE] --dry-run: pool, pins, read set, hygiene, every arm read through open_arm_reader (pins verified); NO fit, "
           "no measure, nothing written, nothing posted")
    r = run_part(part, W, target_dir, data_root, None, L, expect=expect, write=False)
    n_fits = len(r["names"]) * len(KS) * len(SEEDS) * 2
    say(L, "PLAN: %d partitions (%d spaces x k %s x seeds 0-4 x V / K); %s" % (
        n_fits, len(r["names"]), list(KS), "then %d qwen3 re-embeds (embedding requests, zero judge calls)" % FLOOR_N
        if part == "embed" else "no embedding request"))
    say(L, "%s dry-run complete: nothing written" % TAG)
    return r


# ------------------------------------------------------------------------------------------------ selftest (stub arms)
N_CAT = 4


def _synth(rng, gemma_noise, n_fit=300, n_ho=120, n_keyed=200):
    cats = ["cat%d" % i for i in range(N_CAT)]
    vocab = ["w%04d" % i for i in range(1000)]
    cw = {c: ["%s_word%d" % (c, j) for j in range(12)] for c in cats}

    def text(i, c):
        return "q%05d %s %s" % (i, " ".join(rng.choice(cw[c], 4)), " ".join(rng.choice(vocab, 6)))
    fit = [(text(i, cats[i % N_CAT]), cats[i % N_CAT]) for i in range(n_fit)]
    ho = [(text(10000 + i, cats[i % N_CAT]), cats[i % N_CAT]) for i in range(n_ho)]
    extra = [(text(20000 + i, cats[i % N_CAT]), cats[i % N_CAT]) for i in range(20)]     # keyed-only texts (the read set's 117)
    pool = fit + ho + extra
    models = ["m%d" % j for j in range(6)]
    qs = ["k%04d" % i for i in range(n_keyed)]
    textd = {q: pool[(7 * i) % len(pool)][0] for i, q in enumerate(qs)}          # spread over fit, held-out and keyed-only
    catd = {q: pool[(7 * i) % len(pool)][1] for i, q in enumerate(qs)}
    G = {m: {q: int(rng.random() < (0.95 if (int(catd[q][3:]) + j) % 2 == 0 else 0.05)) for q in qs} for j, m in enumerate(models)}
    W = World(fit, ho, (models, G, catd, textd, qs))
    cent = {c: rng.normal(size=4096) for c in cats}
    for c in cats:
        cent[c][:DIM] /= np.linalg.norm(cent[c][:DIM])
    catof = dict(pool)
    # the within-cluster noise lives in a few shared directions (a 256-d isotropic noise on 75 points per cluster lets a vMF
    # component collapse onto one point: ruling B6's refusal, not a stub property worth testing)
    Pn = FM.unit_rows(rng.normal(size=(6, DIM)))

    def low(sd):
        return rng.normal(0, sd, 6) @ Pn
    base = {t: cent[catof[t]] + np.concatenate([low(0.25), rng.normal(0, 1.0, 4096 - DIM)]) for t, _ in pool}
    noisy = {t: np.concatenate([cent[catof[t]][:DIM] * 0.15 + low(1.0), rng.normal(0, 1.0, 768 - DIM)]) for t, _ in pool}
    gem = {t: (noisy[t] if gemma_noise else base[t][:768]) for t, _ in pool}
    card = {t: base[t][:768] * 1.0 + np.concatenate([rng.normal(0, 0.01, DIM), np.zeros(768 - DIM)]) for t, _ in pool}
    return W, dict(qwen3_raw=base, nomic_raw=noisy, gemma_raw=gem, nomic_card=noisy, gemma_card=card)


def _write_db(path, vecs):
    c = getattr(sqlite3.connect, "_raw", sqlite3.connect)(path)
    c.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    c.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, ground_truth_category TEXT DEFAULT '', "
              "query_id INTEGER DEFAULT -1)")
    c.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, struct.pack(">%df" % len(v), *v)) for t, v in vecs.items()])
    c.commit()
    c.close()


def _stage(td, arms_vec, pin_override=None, drop=None):
    saved = EA.OLLAMA_URL
    EA.OLLAMA_URL = "http://127.0.0.1:9/api/embed"          # no real Ollama: the provenance digest reads UNAVAILABLE
    try:
        return _stage_(td, arms_vec, pin_override, drop)
    finally:
        EA.OLLAMA_URL = saved


def _stage_(td, arms_vec, pin_override=None, drop=None):
    """A data root with the qwen3 DB of record (stub) and a --target-dir with each other arm's copy + provenance, written by
    embedder_arms' own writer (write_vectors + write_provenance); a pins fixture with each copy's sha256."""
    root, D = os.path.join(td, "root"), os.path.join(td, "copies")
    os.makedirs(root)
    os.makedirs(D)
    _write_db(os.path.join(root, EG.DB_OF_RECORD), arms_vec["qwen3_raw"])
    pins = {}
    for name, vec in arms_vec.items():
        if name == "qwen3_raw":
            continue
        arm = EA.ARMS[name]
        texts = sorted(t for t in vec if t != drop)
        fn = (lambda v_, a_: (lambda m, inputs: [list(v_[s[len(a_.prefix):]]) for s in inputs]))(vec, arm)
        copy = os.path.join(D, EA.cache_file(arm))
        with contextlib.redirect_stdout(io.StringIO()):
            n = EA.write_vectors(copy, arm, texts, fn)
            src = os.path.join(root, EG.DB_OF_RECORD)
            EA.write_provenance(copy, arm, src, EA._sha(src), n)
        pins[name] = {"sha256": EA._sha(copy)}
    pins.update(pin_override or {})
    pf = os.path.join(td, "pins.json")
    with open(pf, "w", encoding="utf-8") as f:
        json.dump({"schema": EA.ARM_PINS_SCHEMA, "arms": pins}, f)
    return root, D, pf


@contextlib.contextmanager
def _stubs(pf):
    saved = (EA.ARM_PINS_FILE, pool_guard.assert_pool_of_record, globals()["fetch_tags"])
    EA.ARM_PINS_FILE = pf
    pool_guard.assert_pool_of_record = lambda pid, *a, **k: pid
    globals()["fetch_tags"] = lambda: {QWEN3: "sha256:stubq", "nomic-embed-text:latest": "sha256:stubn"}
    try:
        yield
    finally:
        EA.ARM_PINS_FILE, pool_guard.assert_pool_of_record, globals()["fetch_tags"] = saved


def _quiet(fn):
    buf = io.StringIO()
    err, res = None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as e:
            err = str(e)
    return buf.getvalue(), err, res


SKS = (4, 8)


def selftest(only=None, quiet=False):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    if sel("E0-UNIT"):
        ok(worse(-0.03, 0.02, -0.05, -0.001) is True and worse(-0.02, 0.02, -0.05, -0.001) is False
           and worse(-0.03, 0.02, -0.05, 0.0) is False and worse(-0.021, 0.02, -0.05, -1e-9) is True,
           "E0-UNIT WORSE: diff < -spread strictly AND CI upper < 0 strictly (boundaries -0.02 / hi 0 do not fire)")
        rng = np.random.default_rng(3)
        X = FM.unit_rows(rng.normal(size=(300, 16)))
        R, _ = np.linalg.qr(rng.normal(size=(16, 16)))
        ok(abs(linear_cka(X, X @ R) - 1.0) < 1e-9 and linear_cka(X, FM.unit_rows(rng.normal(size=(300, 16)))) < 0.2,
           "E0-UNIT linear CKA: 1 under a rotation, small for an independent space")
        ok(mutual_knn(X, X @ R) == 1.0 and mutual_knn(X, FM.unit_rows(rng.normal(size=(300, 16)))) < 0.2,
           "E0-UNIT mutual kNN@10: 1.0 under a rotation (self excluded), small for an independent space")
        Y = np.tile(FM.unit_rows(rng.normal(size=(1, 16))), (50, 1))
        ok(abs(anisotropy(Y) - 1.0) < 1e-9 and abs(anisotropy(X)) < 0.05, "E0-UNIT anisotropy: 1 for identical rows, ~0 isotropic")
        ok(knn_sets(np.eye(12)[:, :12] + 0.0, 3)[0].isdisjoint({0}), "E0-UNIT kNN never lists the text itself")
        ok(inside(-0.05, (-0.05, 0.01)) and inside(0.01, (-0.05, 0.01)) and not inside(0.0101, (-0.05, 0.01)), "E0-UNIT interval inclusive")
        ok(assert_m2_n("x", {1: dict(n2=5), 2: dict(n2=5)}, 5) == 5
           and _quiet(lambda: assert_m2_n("x", {1: dict(n2=5), 2: dict(n2=4)}, 5))[1] is not None
           and "registered denominator is 5" in (_quiet(lambda: assert_m2_n("x", {1: dict(n2=4)}, 5))[1] or ""),
           "E0-UNIT the M2 denominator: every partition on the whole keyed set, else REFUSED")
        off = rng.normal(size=16) * 5
        ok(linear_cka(off + rng.normal(size=(300, 16)), off + rng.normal(size=(300, 16))) < 0.2,
           "E0-UNIT linear CKA is centred: a shared offset does not make two independent spaces similar")
    if sel("E0-TAG"):
        cases = [(("nomic_raw", 4, "m1", 0.03, 0.01), "DESCRIPTIVE-ONLY"),      # the spread leg decides (OMX1)
                 (("nomic_raw", 4, "m1", 0.0, 0.025), "DESCRIPTIVE-ONLY"),     # the realised MDE80 leg decides
                 (("nomic_raw", 4, "m1", 0.0, 0.01), "SCOREABLE"),             # bar = registered 0.0186 < 0.020
                 (("tfidf", 4, "m1", 0.03, 0.05), "SCOREABLE"),                # 0.08 beyond 0.05
                 (("nomic_raw", 8, "m1", 0.0, 0.0), "DESCRIPTIVE-ONLY (no registered prior)"),
                 (("gemma_raw", 4, "m2", 0.0, 0.0), "DESCRIPTIVE-ONLY (no registered prior)")]
        got = [support_tag(*a, 4) for a, _ in cases]
        ok(all(g.startswith(w) for g, (_, w) in zip(got, cases))
           and got[0] == "DESCRIPTIVE-ONLY (prior -0.0200 vs bar 0.0300 = max(registered MDE 0.0186, spread_qwen3 0.0300, realised MDE80 0.0100))"
           and got[2] == "SCOREABLE (prior -0.0200 vs bar 0.0186 = max(registered MDE 0.0186, spread_qwen3 0.0000, realised MDE80 0.0100))",
           "E0-TAG support tag: bar = max(registered MDE, measured spread, realised MDE80), each leg deciding once; no prior -> "
           "DESCRIPTIVE-ONLY (%s)" % [g.split(" ")[0] for g in got])
        with contextlib.redirect_stdout(io.StringIO()):
            L = []
            C = {(a, 4, m): dict(diff=0.0, lo=-0.1, hi=0.1, spread=0.0, fires=False) for a in ("nomic_raw", "gemma_raw", "nomic_card", "gemma_card")
                 for m in ("m1", "m2")}
            r = dict(C=C, geo={})
            score_lines("embed", r, 4, L)
        f1l = [x for x in L if x.startswith("FALSIFIER F1")][0]
        ok(r["F1"] is False and "does not fire" in f1l and "not shown; no support computed" in f1l and "the method's" not in f1l,
           "E0-TAG C-E0B2-3 a non-firing F1 prints 'not shown; no support computed' and never 'the method's'")
    if sel("E0-EXIT"):
        txt, err, rc = _quiet(lambda: entry(["--run"]))
        ok(err is None and rc == 2 and txt.rstrip().endswith("[E0B] EXIT 2 (REFUSED)") and "--part cpu|embed is required" in txt,
           "E0-EXIT a refusal returns 2 and prints '[E0B] EXIT 2 (REFUSED)' last (in-process)")
        import subprocess
        pr = subprocess.run([sys.executable, os.path.abspath(__file__), "--run"], capture_output=True, text=True, timeout=300)
        ok(pr.returncode == 2 and "EXIT 2 (REFUSED)" in pr.stdout, "E0-EXIT the process exits 2 on a refusal (rc %d)" % pr.returncode)
        saved_v = FM.vmf_em
        FM.vmf_em = lambda X, k, s: FM.refuse("some other failure")
        try:
            _o, err_o, _r = _quiet(lambda: fit_space(np.eye(4), (2,), (0,)))
        finally:
            FM.vmf_em = saved_v
        ok(err_o is not None and "some other failure" in err_o, "E0-EXIT a non-B6 refusal inside the V fit propagates (never a VOID)")
        ok(cell_void({"a": {8: "x"}}, "a", 8) == "a k 8 VOID (ruling B6)" and cell_void({"a": {}, "qwen3_raw": {4: "x"}}, "a", 4)
           == "the reference qwen3_raw k 4 VOID (ruling B6)" and cell_void({"a": {8: "x"}, "qwen3_raw": {}}, "a", 4) is None,
           "E0-EXIT cell_void: the arm's own VOID, the reference's VOID at that k, None otherwise")
    if sel("E0-CONTRAST"):
        st_contrast(ok)
    if sel("E0-SCORE"):
        st_score(ok)
    if sel("E0-MEASURE"):
        st_measure(ok)
    with tempfile.TemporaryDirectory() as td:
        if sel("E0-CPU"):
            st_cpu(ok, td)
        if sel("E0-EMBED"):
            st_embed(ok, td)
        if sel("E0-REFUSE"):
            st_refuse(ok, td)
        if sel("E0-VOID"):
            st_void(ok, td)
        if sel("E0-SPREAD"):
            st_spread(ok, td)
        import gc
        gc.collect()        # anchor_free_readout.full_vectors leaves its read-only connection to the GC (Windows temp cleanup)
    return n[0]


def _arm(m1_by_seed, per1_seed0, m2_by_seed, per2_seed0, k=4):
    d = {}
    for s in SEEDS:
        d[("V", k, s)] = dict(m1=m1_by_seed[s], m2=m2_by_seed[s],
                              per1=np.asarray(per1_seed0 if s == 0 else [m1_by_seed[s]] * len(per1_seed0)),
                              per2=per2_seed0 if s == 0 else {q: m2_by_seed[s] for q in per2_seed0})
        d[("K", k, s)] = dict(m1=0.3 + 0.15 * s, m2=-0.01 * s)           # K differs from V (a spread over K would be 0.6 / 0.04)
    return d


def st_contrast(ok):
    """contrast(): S seed 0 minus qwen3 seed 0; spread over QWEN3's V seeds; the per-question CI on the right population."""
    n = 200
    q_per1 = np.array([1.0] * 160 + [0.0] * 40)                 # 0.80
    s_per1 = np.array([1.0] * 140 + [0.0] * 60)                 # 0.70: -0.10 on 20 questions
    q = _arm([0.80, 0.81, 0.81, 0.81, 0.81], q_per1, [0.0] * 5, {"x%d" % i: 0.0 for i in range(n)})   # seed 0 the unique extreme
    S = _arm([0.70, 0.20, 0.95, 0.70, 0.70], s_per1, [0.0] * 5, {"x%d" % i: 0.0 for i in range(n)})
    c = contrast(S, q, np.arange(n), 4, "m1")
    ok(abs(c["diff"] - (-0.10)) < 1e-12 and abs(c["spread"] - 0.01) < 1e-12 and c["fires"] and c["hi"] < 0,
       "E0-CONTRAST M1': diff -0.1000 (seed 0 vs seed 0), spread_qwen3 over V seeds 0-4 0.0100 (not S's 0.75, not K's 0.60, "
       "not seeds 1-4's 0), CI upper < 0 -> FIRES "
       "(%.4f, %.4f, %.4f)" % (c["diff"], c["spread"], c["hi"]))
    per2q = {"x%d" % i: 0.002 for i in range(n)}
    per2s = {"x%d" % i: (0.002 if i < 100 else 0.0) for i in range(n)}
    q2 = _arm([0.8] * 5, q_per1, [0.002, 0.0021, 0.0021, 0.0021, 0.0021], per2q)
    S2 = _arm([0.8] * 5, q_per1, [0.001, 0.009, 0.0, 0.001, 0.001], per2s)
    c2 = contrast(S2, q2, np.arange(n), 4, "m2")
    ok(abs(c2["diff"] - (-0.001)) < 1e-12 and abs(c2["spread"] - 0.0001) < 1e-12 and c2["fires"],
       "E0-CONTRAST M2: diff -1.000e-3 over the keyed per-question values, spread_qwen3 0.1e-3 (V seeds 0-4) -> FIRES")


def st_score(ok):
    """score_lines on hand-made contrasts: F1 counts the PRIMARY families on M2 at the FIRST k only."""
    def c(f):
        return dict(diff=-0.01 if f else 0.0, lo=-0.02, hi=-0.001 if f else 0.01, spread=0.0, fires=f, mean_diff=0.0, k0_diff=0.0,
                    spread_S=0.0)
    for (nm1, nm2, gm1, gm2, cards, k2), want in (((True, True, True, False, True, False), False),
                                                   ((False, True, False, True, False, False), True),
                                                   ((True, True, False, False, True, True), False)):
        C = {}
        for arm, f1_, f2_ in (("nomic_raw", nm1, nm2), ("gemma_raw", gm1, gm2), ("nomic_card", cards, cards),
                              ("gemma_card", cards, cards)):
            for k in (4, 8):
                C[(arm, k, "m1")] = c(f1_ if k == 4 else True)
                C[(arm, k, "m2")] = c(f2_ if k == 4 else k2)
        res = dict(C=C, geo={})
        L = []
        with contextlib.redirect_stdout(io.StringIO()):
            score_lines("embed", res, 4, L)
        txt = "\n".join(L)
        ok(res["F1"] is want and ("FALSIFIER F1 %s" % ("FIRES" if want else "does not fire")) in txt,
           "E0-SCORE F1 %s (nomic M1/M2 %s/%s, gemma %s/%s, cards %s, second k %s): M2, first k, PRIMARY only"
           % ("FIRES" if want else "does not fire", nm1, nm2, gm1, gm2, cards, k2))
    C = {(a, 4, m): c(False) for a in ("nomic_raw", "tfidf") for m in ("m1", "m2")}
    C[("nomic_raw", 4, "m1")] = dict(c(False), diff=-0.02)
    C[("tfidf", 4, "m1")] = dict(c(True), diff=-0.16)
    res = dict(C=C, geo={"nomic_raw": dict(knn=0.55)})
    L = []
    with contextlib.redirect_stdout(io.StringIO()):
        score_lines("cpu", res, 4, L)
    txt = "\n".join(L)
    ok("P1 HELD: nomic_raw minus qwen3 at k 4, M1' = -0.0200" in txt and "P2 FAILED: tfidf minus qwen3 at k 4, M1' = -0.1600" in txt
       and "P6 HELD: mutual kNN@10 qwen3-nomic_raw = 0.5500" in txt and "WORSE fired: yes (prior 0.85)" in txt,
       "E0-SCORE P1 HELD at -0.0200 (inside), P2 FAILED at -0.1600 (below -0.15), P6 HELD at 0.5500 (inclusive)")


def st_measure(ok):
    """measure_space: M1's cell majority from the FIT texts (not the held-out); a known 1/3."""
    e = np.eye(DIM)
    fit = [("f%d" % i, "a") for i in range(3)] + [("g%d" % i, "b") for i in range(3)]
    ho = [("h0", "a"), ("h1", "b"), ("h2", "b")]
    vec = {t: e[0] for t, _ in fit[:3]}
    vec.update({t: e[1] for t, _ in fit[3:]})
    vec.update({t: e[0] for t, _ in ho})
    qs = ["k0", "k1", "k2", "k3"]
    keyed = (["m0"], {"m0": {"k0": 1, "k1": 1, "k2": 0, "k3": 0}}, {q: "a" for q in qs},
             {"k0": "f0", "k1": "f1", "k2": "g0", "k3": "g1"}, qs)
    W = World(fit, ho, keyed)
    part = {("K", 2, 0): dict(rule="nearest", centers=np.stack([e[0], e[1]]), iters=1, converged=True)}
    m = measure_space(vec, W, part)[("K", 2, 0)]
    ok(abs(m["m1"] - 1 / 3) < 1e-12 and list(m["per1"]) == [1.0, 0.0, 0.0],
       "E0-MEASURE M1 = 1/3: the held-out cell's majority 'a' comes from the fit texts (the held-out's own would give 2/3)")


def st_cpu(ok, td):
    """The deciding path of --run part cpu, end to end on stub arms read through open_arm_reader under the real guards."""
    W, V = _synth(np.random.default_rng(4), gemma_noise=False)
    arms = {k: V[k] for k in ("qwen3_raw", "nomic_raw")}
    root, D, pf = _stage(os.path.join(td, "cpu"), arms)
    out = os.path.join(td, "cpu_out")
    with _stubs(pf):
        txt, err, res = _quiet(lambda: run_part("cpu", W, D, root, out, [], expect=None, ks=SKS))
        ok(err is None and os.path.exists(os.path.join(out, "e0b_cpu_outcome.txt")), "E0-CPU --run cpu wrote the outcome (%s)" % err)
        q = res["ms"]["qwen3_raw"]
        ok(all(abs(q[("V", 4, s)]["m1"] - 1.0) < 1e-12 for s in SEEDS) and res["C"][("nomic_raw", 4, "m1")]["spread"] == 0.0,
           "E0-CPU qwen3 stub: M1 1.0000 on every V seed at k 4; spread_qwen3 = 0 (known answer)")
        c = res["C"][("nomic_raw", 4, "m1")]
        wl = txt.split("WORSE nomic_raw k=4 M1':")[1].split("\n")[0]
        se = (c["hi"] - c["lo"]) / 3.92
        bar_n = max(0.0186, 0.0, 2.8 * se)
        tag_n = "%s (prior -0.0200 vs bar %.4f = max(registered MDE 0.0186, spread_qwen3 0.0000, realised MDE80 %.4f))" % (
            "SCOREABLE" if 0.020 > bar_n else "DESCRIPTIVE-ONLY", bar_n, 2.8 * se)
        ok(c["fires"] and c["diff"] < -0.3 and c["hi"] < 0 and ("WORSE nomic_raw k=4 M1': diff %+.4f" % c["diff"]) in txt
           and ("-> WORSE FIRES [%s]" % tag_n) in wl and ("realised SE %.4f, MDE80 %.4f" % (se, 2.8 * se)) in wl,
           "E0-CPU nomic_raw (noisy stub) WORSE k=4 M1' FIRES with diff %+.4f, tagged %s against max(0.0186, spread 0, realised "
           "MDE80 %.4f)" % (c["diff"], tag_n.split(" ")[0], 2.8 * se))
        ct = res["C"][("tfidf", 4, "m1")]
        se_t = (ct["hi"] - ct["lo"]) / 3.92
        bar_t = max(0.0186, 0.0, 2.8 * se_t)
        ok(("(f) RE-DERIVED with this instrument's spread (C-E0B-2): E0b nomic-vs-qwen3 at k 4 on M1' %s; TF-IDF floor at k 4 on M1' "
            "%s (prior -0.0800 vs bar %.4f" % (tag_n, "SCOREABLE" if 0.08 > bar_t else "DESCRIPTIVE-ONLY", bar_t)) in txt
           and "DESCRIPTIVE-ONLY (no registered prior)" in txt.split("WORSE nomic_raw k=8 M1':")[1].split("\n")[0]
           and "DESCRIPTIVE-ONLY (no registered prior)" in txt.split("WORSE nomic_raw k=4 M2:")[1].split("\n")[0],
           "E0-CPU (f) re-derived on the measured bar; lines without a registered prior DESCRIPTIVE-ONLY")
        ok(all(m["n2"] == len(W.keyed[4]) == 200 for m in res["ms"]["nomic_raw"].values()) and "M2 n 200 of 200 keyed" in txt
           and M1P_NOTE in txt and "V0 M1' " in txt and "FITTED nomic_raw: 20 partitions on 300 fit texts" in txt, "E0-CPU M2 n = 200 of 200 keyed (held-out and keyed-only texts included); the "
           "M1' (D2) label and note printed")
        c2 = res["C"][("nomic_raw", 4, "m2")]
        ok(c2["fires"] and c2["diff"] < 0, "E0-CPU nomic_raw WORSE k=4 M2 FIRES (diff %.5f)" % c2["diff"])
        ok("FALSIFIER F1 NOT SCORED" in txt and res["F1"] is None and "P5 NOT SCORED in part cpu" in txt,
           "E0-CPU F1 / P5 NOT SCORED in part cpu")
        p1 = "P1 %s: nomic_raw minus qwen3 at k 4, M1' = %+.4f" % ("HELD" if inside(c["diff"], P1[1]) else "FAILED", c["diff"])
        ok(p1 in txt and "P1 FAILED" in txt and "WORSE fired: yes (prior 0.40)" in txt, "E0-CPU P1 scored FAILED at %+.4f" % c["diff"])
        ok("P2 " in txt and "tfidf minus qwen3 at k 4" in txt and ("P6 %s: mutual kNN@10 qwen3-nomic_raw = %.4f"
                                                                   % ("HELD" if inside(res["geo"]["nomic_raw"]["knn"], P6[0]) else "FAILED",
                                                                      res["geo"]["nomic_raw"]["knn"])) in txt,
           "E0-CPU P2 and P6 printed with their values")
        from sklearn.feature_extraction.text import TfidfVectorizer
        vocab = len(TfidfVectorizer(lowercase=True, min_df=2, sublinear_tf=True).fit([t for t, _ in W.fit]).vocabulary_)
        ok(("vocabulary %d;" % vocab) in txt, "E0-CPU TF-IDF vocabulary %d = the fit-only vocabulary (the read set's differs)" % vocab)
        ok("HYGIENE: held-out texts in the fit 0; held-out stem_keys in the fit 0" in txt and "tfidf (TF-IDF -> SVD-256, fitted on the 300 fit texts only)" in txt,
           "E0-CPU hygiene printed 0 / 0; TF-IDF fitted on the fit texts only")
        ok("registrar pin: arm nomic_raw sha256" in txt and "digest sha256:stubn" in txt and VERDICT_F in txt,
           "E0-CPU the registrar pin, the digest and the registered verdict line (f) printed")
        with open(os.path.join(out, "e0b_cpu_arms.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        ok(len(rows) == 3 * 2 * 5 * 2 and {r["space"] for r in rows} == {"qwen3_raw", "nomic_raw", "tfidf"} and "M1'" in rows[0]
           and {r["M2_n"] for r in rows} == {"200"}, "E0-CPU CSV: 60 partitions, column M1', M2_n 200")
        txt2, err2, _ = _quiet(lambda: run_part("cpu", W, D, root, out, [], expect=None, ks=SKS))
        ok(err2 is not None and "WRITE-ONCE" in err2 and "pool" not in txt2, "E0-CPU a second --run REFUSES before any work (write-once)")
        out3 = os.path.join(td, "cpu_dry")
        txt3, err3, _ = _quiet(lambda: dry_run("cpu", W, D, root, [], expect=None))
        ok(err3 is None and not os.path.exists(out3) and "FITTED" not in txt3 and "registrar pin: arm nomic_raw" in txt3,
           "E0-CPU --dry-run: pins verified, nothing fitted, nothing written")


def st_embed(ok, td):
    for gnoise, expect_f1 in ((False, False), (True, True)):
        W, V = _synth(np.random.default_rng(4), gemma_noise=gnoise)
        root, D, pf = _stage(os.path.join(td, "embed%d" % gnoise), V)
        out = os.path.join(td, "embed_out%d" % gnoise)
        with EA.stub_ollama() as (url, log, _state), _stubs(pf):
            saved = EA.OLLAMA_URL
            EA.OLLAMA_URL = url
            try:
                txt, err, res = _quiet(lambda: run_part("embed", W, D, root, out, [], expect=None, ks=SKS, floor_n=40))
            finally:
                EA.OLLAMA_URL = saved
        ok(err is None, "E0-EMBED --run embed (gemma noisy %s) ran (%s)" % (gnoise, err))
        g = res["C"][("gemma_raw", 4, "m2")]
        ok(res["F1"] is expect_f1 and ("FALSIFIER F1 %s: %d of 3" % ("FIRES" if expect_f1 else "does not fire", 2 if expect_f1 else 1)) in txt
           and ("P5 %s: F1 fired: %s" % ("HELD" if expect_f1 else "FAILED", "yes" if expect_f1 else "no")) in txt,
           "E0-EMBED F1 %s with gemma %s (nomic WORSE; mxbai NOT RUN counted not WORSE)" % ("FIRES" if expect_f1 else "does not fire",
                                                                                          "noisy" if gnoise else "= qwen3"))
        if not gnoise:
            ok(g["diff"] == 0.0 and g["lo"] == 0.0 and not g["fires"] and "WORSE gemma_raw k=4 M1': diff +0.0000" in txt
               and "not shown worse beyond max(MDE, spread) = 0.0186 [DESCRIPTIVE-ONLY (no registered prior)]"
               in txt.split("WORSE gemma_raw k=4 M1':")[1].split("\n")[0],
               "E0-EMBED gemma_raw = qwen3's first 768 dims: diff exactly 0, not shown worse beyond max(MDE, spread) = 0.0186")
        ok([len(i) for _p, m, i in log] == [32, 8] and all(m == QWEN3 for _p, m, _i in log)
           and "REPRODUCIBILITY FLOOR (D4, DESCRIPTIVE): 40 fit texts" in txt
           and txt.index("REPRODUCIBILITY FLOOR") < txt.index("FITTED qwen3_raw") and "OLLAMA PREFLIGHT: /api/tags lists" in txt,
           "E0-EMBED the floor posted exactly 40 texts to %s through the stub Ollama (batches %s)" % (QWEN3, [len(i) for _p, _m, i in log]))
        ok("SECONDARY nomic_card M2 k 4" in txt and "SECONDARY gemma_card M2 k 4" in txt and "mxbai: NOT RUN" in txt,
           "E0-EMBED card arms printed SECONDARY (not in F1); mxbai NOT RUN")
    W, V = _synth(np.random.default_rng(4), gemma_noise=False)
    root, D, pf = _stage(os.path.join(td, "embed_down"), V)
    with _stubs(pf):
        g = globals()
        saved_ft = g["fetch_tags"]
        g["fetch_tags"] = lambda: None
        try:
            txt, err, _ = _quiet(lambda: dry_run("embed", W, D, root, [], expect=None))
        finally:
            g["fetch_tags"] = saved_ft
    ok(err is not None and "Ollama /api/tags does not answer" in err and "ARM qwen3_raw" not in txt,
       "E0-EMBED C-E0B-4 Ollama down: the embed dry-run REFUSES before any arm read")
    with EA.stub_ollama() as (url, log, state), _stubs(pf):
        saved = EA.OLLAMA_URL
        EA.OLLAMA_URL = url
        state["fault"] = lambda i: "bad"
        try:
            txt, err, _ = _quiet(lambda: run_part("embed", W, D, root, os.path.join(td, "embed_fault"), [], expect=None, ks=SKS, floor_n=40))
        finally:
            EA.OLLAMA_URL = saved
    ok(err is not None and "not a transient connection error" in err and "FITTED" not in txt
       and not os.path.exists(os.path.join(td, "embed_fault")), "E0-EMBED C-E0B-4 an Ollama fault at the floor REFUSES before any fit; "
       "nothing written")
    txt, _e, _r = _quiet(lambda: repro_floor({t: unit(V["qwen3_raw"][t]) for t in V["qwen3_raw"]}, W, [],
                                             embed_fn=lambda m, i: [list(V["qwen3_raw"][t]) for t in i], n=20))
    ok("min 1.000000" in txt and "below 0.9999: 0" in txt, "E0-EMBED floor: identical vectors -> min cosine 1.000000, 0 below the bar")


def _degenerate_at_8(W, V):
    """A stub arm (768-d) that is fine at k 4 and whose V seed 4 at k 8 hits ruling B6 (a one-member cell after the hard step):
    the tight qwen3 clusters plus four orthogonal singletons among the fit texts (the real gemma_raw k 82 seeds 3-4 diagnosis)."""
    rng = np.random.default_rng(99)
    need = needed_texts(W)
    out = {t: np.concatenate([unit(V["qwen3_raw"][t][:DIM] + rng.normal(0, 0.02, DIM)), np.zeros(768 - DIM)]) for t in need}
    fitt = [t for t, _ in W.fit]
    for j in range(4):
        d = np.zeros(768)
        d[200 + j] = 1.0
        out[fitt[j * 7]] = d
    return out


def st_void(ok, td):
    """Ruling (a): gemma_raw VOID at k 8 (B6), every other (arm, k) cell reports; F1 at k 4 unaffected."""
    W, V = _synth(np.random.default_rng(4), gemma_noise=True)
    V = dict(V, gemma_raw=_degenerate_at_8(W, V))
    root, D, pf = _stage(os.path.join(td, "void"), V)
    out = os.path.join(td, "void_out")
    with EA.stub_ollama() as (url, _log, _state), _stubs(pf):
        saved = EA.OLLAMA_URL
        EA.OLLAMA_URL = url
        try:
            txt, err, res = _quiet(lambda: run_part("embed", W, D, root, out, [], expect=None, ks=SKS, floor_n=40))
        finally:
            EA.OLLAMA_URL = saved
    ok(err is None and os.path.exists(os.path.join(out, "e0b_embed_outcome.txt")), "E0-VOID the embed run completes and writes (%s)" % err)
    ok(res["voids"]["gemma_raw"] == {8: res["voids"]["gemma_raw"].get(8)} and "V seed 4" in res["voids"]["gemma_raw"][8]
       and all(res["voids"][n] == {} for n in res["names"] if n != "gemma_raw"),
       "E0-VOID gemma_raw k 8 VOID at V seed 4 (B6); every other (arm, k) cell live (%s)" % res["voids"])
    ok("gemma_raw k 8: VOID (ruling B6): V seed 4" in txt and "  gemma_raw  k 8   VOID (ruling B6)" in txt
       and "WORSE gemma_raw k=8 M1': NA (gemma_raw k 8 VOID (ruling B6))" in txt and "WORSE gemma_raw k=8 M2: NA" in txt
       and res["C"][("gemma_raw", 8, "m1")] is None and res["C"][("gemma_raw", 4, "m2")] is not None
       and not any(k == 8 for (_kind, k, _s) in res["ms"]["gemma_raw"]),
       "E0-VOID the VOID cell prints VOID, its contrasts NA, none of its partitions kept; gemma_raw k 4 reports")
    ok(res["C"][("nomic_raw", 8, "m1")] is not None and "WORSE nomic_raw k=8 M1': diff" in txt and res["F1"] is not None
       and "FALSIFIER F1 " in txt and "NOT SCORED" not in txt.split("FALSIFIER F1")[1].split("\n")[0],
       "E0-VOID the other arms report at k 8; F1 at k 4 scored (%s)" % res["F1"])
    with open(os.path.join(out, "e0b_embed_arms.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ok([r for r in rows if r["kind"] == "VOID"] == [dict(space="gemma_raw", kind="VOID", k="8", seed="", **{"M1'": "VOID (ruling B6)"},
                                                         M2="VOID (ruling B6)", M2_n="", iters="", converged="")]
       and len(rows) == 5 * 20 - 10 + 1, "E0-VOID CSV: one VOID row for (gemma_raw, 8), its 10 partitions absent (%d rows)" % len(rows))
    C = {(a, 4, m): dict(diff=0.0, lo=-0.1, hi=0.1, spread=0.0, fires=False) for a in ("nomic_raw", "nomic_card", "gemma_card") for m in ("m1", "m2")}
    C[("gemma_raw", 4, "m1")] = C[("gemma_raw", 4, "m2")] = None
    r = dict(C=C, geo={})
    L = []
    with contextlib.redirect_stdout(io.StringIO()):
        score_lines("embed", r, 4, L)
    ok(r["F1"] is None and any(x.startswith("FALSIFIER F1 NOT SCORED: gemma_raw at k 4 VOID (ruling B6)") for x in L),
       "E0-VOID a VOID family at the first k: F1 NOT SCORED (excluded), never counted as not WORSE")


def st_spread(ok, td):
    """C-E0B3-2: a stub whose qwen3 V spread is NOT zero (one seed at purity 0.75): the run path passes the MEASURED spread to the
    support tag (the reviewer's call-site OMX1 passes 0)."""
    W, V = _synth(np.random.default_rng(1), gemma_noise=False)
    arms = {k: V[k] for k in ("qwen3_raw", "nomic_raw")}
    root, D, pf = _stage(os.path.join(td, "spread"), arms)
    with _stubs(pf):
        txt, err, res = _quiet(lambda: run_part("cpu", W, D, root, os.path.join(td, "spread_out"), [], expect=None, ks=SKS))
    c = res["C"][("nomic_raw", 4, "m1")] if res else None
    ok(err is None and c is not None and abs(c["spread"] - 0.25) < 1e-12 and "spread_qwen3 0.2500, realised MDE80" in c["tag"]
       and c["tag"].startswith("DESCRIPTIVE-ONLY") and c["tag"] in txt,
       "E0-SPREAD qwen3's V spread 0.2500 (> MDE and MDE80) reaches the tag: %s" % (c["tag"] if c else err))


def st_refuse(ok, td):
    W, V = _synth(np.random.default_rng(7), gemma_noise=False)
    arms = {k: V[k] for k in ("qwen3_raw", "nomic_raw")}
    for tag, over, needle in (("null", {"nomic_raw": {"sha256": None}}, "no sha256 for arm nomic_raw yet"),
                              ("bad", {"nomic_raw": {"sha256": "0" * 64}}, "!= the registrar's pin")):
        root, D, pf = _stage(os.path.join(td, "pin_" + tag), arms, pin_override=over)
        out = os.path.join(td, "pin_out_" + tag)
        with _stubs(pf):
            txt, err, _ = _quiet(lambda: run_part("cpu", W, D, root, out, [], expect=None, ks=SKS))
            txt2, err2, _ = _quiet(lambda: dry_run("cpu", W, D, root, [], expect=None))
        ok(err is not None and needle in err and not os.path.exists(out) and "FITTED" not in txt and err2 is not None and needle in err2
           and "ARM qwen3_raw" not in txt and "READ SET" not in txt and "ARM qwen3_raw" not in txt2,
           "E0-REFUSE a %s registrar pin REFUSES --run and --dry-run right after the pool line: no read-set load, no DB-of-record read "
           "(C-E0B-5)" % tag)
    root, D, pf = _stage(os.path.join(td, "okpins"), arms)
    with _stubs(pf):
        Wbad = World(W.fit + [W.heldout[0]], W.heldout, W.keyed)
        _t, err, _ = _quiet(lambda: run_part("cpu", Wbad, D, root, os.path.join(td, "hyg_out"), [], expect=None, ks=SKS))
        ok(err is not None and "held-out texts" in err and not os.path.exists(os.path.join(td, "hyg_out")),
           "E0-REFUSE a held-out text in the fit REFUSES (hygiene)")
        _t, err, _ = _quiet(lambda: run_part("cpu", W, D, root, os.path.join(td, "cnt_out"), [], expect=dict(EXPECT), ks=SKS))
        ok(err is not None and "differs from the registration" in err, "E0-REFUSE the read set != 8,125 / 3,445 / 10,925 / 11,687 REFUSES")
        _t, err, _ = _quiet(lambda: run_part("cpu", W, None, root, os.path.join(td, "nodir_out"), [], expect=None, ks=SKS))
        ok(err is not None and "no DIR given" in err, "E0-REFUSE no --target-dir: a non-qwen3 arm REFUSES (open_arm_reader)")
    drop = W.heldout[3][0]
    root, D, pf = _stage(os.path.join(td, "drop"), arms, drop=drop)
    with _stubs(pf):
        _t, err, _ = _quiet(lambda: run_part("cpu", W, D, root, os.path.join(td, "drop_out"), [], expect=None, ks=SKS))
    ok(err is not None and "1 needed texts missing" in err, "E0-REFUSE an arm copy lacking one needed text REFUSES (arm_read_guard)")
    ok(sqlite3.connect is FM._guarded_connect and FM.EMB_DB_NAME == "embeddings_cache.db" and FM.ARM_COPY_ADMITTED is None,
       "E0-REFUSE after every run the connect guard and flat_mix's globals are restored")


def entry(argv):
    """The process's exit status: 0 on success; 2 on any REFUSAL (a SystemExit carrying a message, from this script,
    embedder_arms or flat_mix_mmlu), with a last stdout line "[E0B] EXIT 2 (REFUSED)" that a tee'd log keeps (a shell pipe
    without pipefail reports the last command's status, not this one's)."""
    try:
        return main(argv)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code)
            print("%s EXIT 2 (REFUSED)" % TAG)
            sys.stdout.flush()
            return 2
        raise


MUTANTS = (
    ("WORSE on <=", "    return FM.loss(diff, spr, lo, hi)\n", "    return bool(diff <= -spr and hi <= 0)\n", ("E0-UNIT",)),
    ("spread from S not qwen3", "    spr = FM.spread([mq[(\"V\", k, s)][metric] for s in SEEDS])\n",
     "    spr = FM.spread([ms[(\"V\", k, s)][metric] for s in SEEDS])\n", ("E0-CONTRAST",)),
    ("S seed 0 vs qwen3 seed 1", "    a, b = ms[(\"V\", k, 0)], mq[(\"V\", k, 0)]\n", "    a, b = ms[(\"V\", k, 0)], mq[(\"V\", k, 1)]\n", ("E0-CONTRAST",)),
    ("M1 CI one-sided on lo", "    return FM.loss(diff, spr, lo, hi)\n", "    return bool(diff < -spr and lo < 0)\n", ("E0-UNIT",)),
    ("F1 counts cards", "    for fname, arm in FAMILIES:\n", "    for fname, arm in FAMILIES + ((\"c1\", \"nomic_card\"), (\"c2\", \"gemma_card\")):\n", ("E0-SCORE", "E0-EMBED")),
    ("F1 threshold 1", "    f1 = nw >= 2\n", "    f1 = nw >= 1\n", ("E0-EMBED",)),
    ("F1 on M1", "        c = C[(arm, k14, \"m2\")]\n        fam.append(", "        c = C[(arm, k14, \"m1\")]\n        fam.append(", ("E0-SCORE",)),
    ("F1 at the second k", "    k14 = ks[0]\n", "    k14 = ks[-1]\n", ("E0-CPU", "E0-EMBED")),
    ("M2 contrast on M1 values", "        d = np.array([a[\"per2\"][q] - b[\"per2\"][q] for q in common])\n",
     "        d = a[\"per1\"] - b[\"per1\"]\n", ("E0-CONTRAST",)),
    ("TF-IDF fitted on the read set", "    A = tv.fit_transform(fit_texts)\n", "    A = tv.fit_transform(need)\n", ("E0-CPU",)),
    ("hygiene not enforced", "    if exact or keys:\n", "    if False:\n", ("E0-REFUSE",)),
    ("counts not enforced", "        if bad:\n            refuse(\"the read set", "        if False:\n            refuse(\"the read set", ("E0-REFUSE",)),
    ("M1 majority from held-out", "        sc, hits, _kh = FM.m1_block(fn, Xf, Xh, W.fit, W.heldout)\n",
     "        sc, hits, _kh = FM.m1_block(fn, Xh, Xh, W.heldout, W.heldout)\n", ("E0-MEASURE",)),
    ("partitions fitted on the held-out", "    Xfit = {n: np.stack([vecs[n][t] for t, _ in W.fit]) for n in names}\n",
     "    Xfit = {n: np.stack([vecs[n][t] for t, _ in W.fit + W.heldout]) for n in names}\n", ("E0-CPU",)),
    ("non-qwen3 read bypasses open_arm_reader", "            db = EA.open_arm_reader(FM, name, target_dir, data_root)\n",
     "            db = os.path.join(target_dir, EA.cache_file(arm))\n            FM.configure_embedding(cache_file=db, model=arm.model)\n", ("E0-REFUSE",)),
    ("coverage guard skipped", "            EA.arm_read_guard(con, arm, need)\n", "            pass\n", ("E0-REFUSE",)),
    ("session not restored", "        sqlite3.connect = saved_c\n", "        pass\n", ("E0-REFUSE",)),
    ("write-once off", "            if os.path.exists(p):\n                refuse(\"%s exists", "            if False:\n                refuse(\"%s exists", ("E0-CPU",)),
    ("dry run fits", "    if not write:\n        return dict(names=names, info=info)\n", "", ("E0-CPU",)),
    ("floor n off by one", "    texts = sorted((t for t, _ in W.fit), key=lambda t: hashlib.sha256(t.encode(\"utf-8\")).hexdigest())[:n]\n",
     "    texts = sorted((t for t, _ in W.fit), key=lambda t: hashlib.sha256(t.encode(\"utf-8\")).hexdigest())[:n - 1]\n", ("E0-EMBED",)),
    ("floor on the wrong model", "        for t, e in zip(ch, embed_fn(QWEN3, list(ch))):\n", "        for t, e in zip(ch, embed_fn(\"nomic-embed-text:latest\", list(ch))):\n",
     ("E0-EMBED",)),
    ("P1 scored on M2", "            c = C[(n, k14, \"m1\")]\n", "            c = C[(n, k14, \"m2\")]\n", ("E0-SCORE",)),
    ("kNN includes self", "            S[i, s + i] = -np.inf                       # a text is never its own neighbour\n", "            pass\n", ("E0-UNIT",)),
    ("CKA uncentred", "    A = Xa - Xa.mean(axis=0)\n    B = Xb - Xb.mean(axis=0)\n", "    A = Xa\n    B = Xb\n", ("E0-UNIT",)),
    ("OM1 spread over qwen3's K seeds", "    spr = FM.spread([mq[(\"V\", k, s)][metric] for s in SEEDS])\n",
     "    spr = FM.spread([mq[(\"K\", k, s)][metric] for s in SEEDS])\n", ("E0-CONTRAST",)),
    ("OM2 spread over V seeds 1-4", "    spr = FM.spread([mq[(\"V\", k, s)][metric] for s in SEEDS])\n",
     "    spr = FM.spread([mq[(\"V\", k, s)][metric] for s in SEEDS[1:]])\n", ("E0-CONTRAST",)),
    ("OM8 M2 on the keyed texts in the fit only", "    veck = {t: vec[t] for t in W.keyed[3].values()}\n",
     "    veck = {t: vec[t] for t in W.keyed[3].values() if t in set(x for x, _ in W.fit)}\n", ("E0-CPU",)),
    ("M2 n not asserted", "    if n2 != [n_keyed]:\n", "    if False:\n", ("E0-UNIT",)),
    ("pins checked late (after the qwen3 read)", "    early_pins(names, target_dir, L)\n", "", ("E0-REFUSE",)),
    ("no Ollama preflight", "        ollama_preflight(L)\n", "        pass\n", ("E0-EMBED",)),
    ("floor after the fits", "    if part == \"embed\":                               # C-E0B-4: an Ollama fault costs no fit\n",
     "    if False:\n", ("E0-EMBED",)),
    ("support tag on the record's spread", "    bar = max(reg, spread, mde80)\n", "    bar = max(reg, 0.0305, mde80)\n", ("E0-TAG",)),
    ("OMX1 support tag drops the measured spread", "    bar = max(reg, spread, mde80)\n", "    bar = max(reg, mde80)\n", ("E0-TAG",)),
    ("support tag drops the realised MDE80", "    bar = max(reg, spread, mde80)\n", "    bar = max(reg, spread)\n", ("E0-TAG",)),
    ("support tag drops the registered MDE", "    bar = max(reg, spread, mde80)\n", "    bar = max(spread, mde80)\n", ("E0-TAG",)),
    ("F1 non-firing unqualified", "\"'the method's' for the FLAT clause, no recorded number)\" if f1 else F1_NOT_SHOWN))",
     "\"'the method's' for the FLAT clause, no recorded number)\" if f1 else \"\"))", ("E0-TAG",)),
    ("support tag on every line", "    if pr is None:\n        return \"DESCRIPTIVE-ONLY (no registered prior)\"\n", "    if pr is None:\n        pr = -1.0\n", ("E0-CPU",)),
    ("M1' label dropped", "ML = {\"m1\": \"M1'\", \"m2\": \"M2\"}", "ML = {\"m1\": \"M1\", \"m2\": \"M2\"}", ("E0-CPU",)),
    ("OMX1 call site drops the measured spread", "                c[\"tag\"] = support_tag(n, k, metric, c[\"spread\"], 2.8 * se, ks[0])\n",
     "                c[\"tag\"] = support_tag(n, k, metric, 0.0, 2.8 * se, ks[0])\n", ("E0-SPREAD",)),
    ("B6 refuses the run again", "                if FM.B6 not in str(e):\n", "                if True:\n", ("E0-VOID",)),
    ("B6 VOIDs one seed only (cell kept)", "        if k not in voids:\n            parts.update(cell)\n", "        parts.update(cell)\n", ("E0-VOID",)),
    ("B6 VOIDs the whole arm", "                voids[k] = str(e).split(\"REFUSED: \", 1)[-1].split(\";\")[0]\n                break\n",
     "                voids.update({kk: \"x\" for kk in ks})\n                break\n", ("E0-VOID",)),
    ("any refusal VOIDs", "                if FM.B6 not in str(e):\n                    raise\n", "                pass\n", ("E0-EXIT",)),
    ("reference VOID ignored", "    if k in voids.get(\"qwen3_raw\", {}):\n", "    if False:\n", ("E0-EXIT",)),
    ("VOID family counted as not WORSE", "    if gone:\n", "    if False:\n", ("E0-VOID",)),
    ("refusal exits 0", "            return 2\n        raise\n", "            return 0\n        raise\n", ("E0-EXIT",)),
    ("P6 upper bound exclusive", "    return bool(iv[0] <= x <= iv[1])\n", "    return bool(iv[0] <= x < iv[1])\n", ("E0-UNIT",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index("\nMUTANTS = (")
    head, tail = src[:cut], src[cut:]
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "embedder_cross_flat_mutant", "__file__": os.path.abspath(__file__)}
        saved = (sqlite3.connect, {k: getattr(FM, k) for k in FM._EMB_GLOBALS}, AF.EMB_DB, F.EMB_DB, EA.ARM_PINS_FILE,
                 pool_guard.assert_pool_of_record, EA.OLLAMA_URL)
        try:
            exec(compile(head.replace(old, new) + tail, "<mutant>", "exec"), ns)
            ns["selftest"](only=set(tests), quiet=True)
            res = "SURVIVED"
        except BaseException as e:            # noqa: B902
            root = e
            while not isinstance(root, (AssertionError, SystemExit)) and root.__context__ is not None:
                root = root.__context__
            res = "KILLED | %s" % str(root if isinstance(root, (AssertionError, SystemExit)) else e)[:110]
        finally:                                  # one mutant's leaked state never kills the next
            sqlite3.connect = saved[0]
            for k, v in saved[1].items():
                setattr(FM, k, v)
            AF.EMB_DB, F.EMB_DB, EA.ARM_PINS_FILE, pool_guard.assert_pool_of_record, EA.OLLAMA_URL = saved[2:]
        killed += res.startswith("KILLED")
        print("  %-42s %s" % (name, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run", "--run"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--part", choices=sorted(PARTS))
    ap.add_argument("--target-dir", default=None, help="the pre-embedder's --target-dir (the arm copies); DATA_ROOT-relative or absolute")
    a = ap.parse_args(argv)
    if a.selftest or a.mutants:
        if a.part or a.target_dir:
            refuse("--part / --target-dir are admitted with --dry-run / --run only")
        print("pool %s (selftest: synthetic stub arms only; the pool is not read)" % POOL_ID)
        if a.mutants:
            return run_mutants()
        print("SELFTEST PASSED: %d checks" % selftest())
        return 0
    if not a.part:
        refuse("--part cpu|embed is required")
    td = None if a.target_dir is None else (a.target_dir if os.path.isabs(a.target_dir) else os.path.join(pool_guard.DATA_ROOT, a.target_dir))
    L = []
    if a.dry_run:
        dry_run(a.part, real_world, td, pool_guard.DATA_ROOT, L)
        return 0
    run_part(a.part, real_world, td, pool_guard.DATA_ROOT, OUT_DIR, L)
    return 0


if __name__ == "__main__":
    sys.exit(entry(sys.argv[1:]))
