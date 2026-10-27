"""INTENT-TRANSFER stage 0 readouts (INTENT-TRANSFER-S0).

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-09-29 (before any code or call) — INTENT-TRANSFER-S0: on three
intent corpora with a known answer (MASSIVE en-US 18/60, CLINC150 10/150 + OOS, Banking77 77), split content-closed by CK-CLOSE-v1
hash sides, does the embedder dependence seen on MMLU-Pro (coarse holds, fine depends) reappear against GOLD labels, ...", span
L22092-L22134 _as_of 44ab46f (the registrar's commit; the author's D1 "Yes, all three" in the section before it, L22080-L22090).
Built first to the draft (docs/agents/plans/2026-09-29_intent_transfer_design.md section 7, 7a95a1a), then conformed to the
committed text: the registrar's items R-1 (C1 SE declared; the per-corpus SCOREABLE / DESCRIPTIVE-ONLY line for nomic at
measured SE <= 0.0071 and spread <= 0.020), R-2 (C2's OOS denominator = EVERY CLINC OOS row, all hash sides), R-3 (D7 prints
NOT RUN without an author admission of HWU64), R-4 (gemma's fine WORSE clause DESCRIPTIVE-ONLY at its prediction; still counted
as written) and R-5 (kind zero-call) are implemented and printed. The builder's readings of points the text leaves open are
B1-B8 below (renamed from the draft-time R1-R8 so they never collide with the registrar's R-1..R-5); none is a criterion
change, each is printed in the outcome and is the registrar's to confirm or bracket.

Kind: zero-call (R-5); ZERO LLM (judge) calls; no construction; no pool of record read (the study reads only its OWN DBs; the three
per-model caches of record are opened read-only, immutable, by the transport preflight's route parity only).

Files (all at DATA_ROOT = TAXOARENA_DATA_ROOT or the repo root; root *.db is gitignored; nothing under experiment_results/*.db):
  intent_transfer_corpora_v1.db   the ingest (tools/ingest/intent_ingest.py; read-only here)
  intent_emb_qwen3.db / intent_emb_nomic.db / intent_emb_gemma.db   this study's OWN embedding caches (EmbeddingCache schema:
      embeddings(query TEXT PK, vector BLOB big-endian float32, native dim) + intent_meta(key, value)). Written ONLY by
      --embed E --go, through embedder_arms' writer (write_vectors: whole batches, one keep-alive connection, bounded retry on
      transient connection errors, EMB-CONN) into --emb-dir (default DATA_ROOT); a file of record, a path inside
      experiment_results/ or an --emb-dir that holds a cache of record REFUSES. First launch creates the file EXCLUSIVELY and
      pins intent_meta (model, protocol RAW, native dim, text-set sha256 and count, ingest DB sha256, this script's LF blob,
      embedder_arms' LF blob, the Ollama model digest); a later launch RESUMES (only missing texts) and REFUSES any meta
      mismatch. The shared repo-root caches (embeddings_cache*.db) are NEVER written: their per-table hashes are printed before
      and after every --go and a change REFUSES.
  experiment_results/intent_transfer/s0_outcome.txt  WRITE-ONCE (mode x) + CSVs beside (mode x); only from COMPLETE
      embeddings with every pin set; --pilot writes s0_outcome_PILOT.txt (+ _PILOT CSVs), never the file of record.
  experiment_configs/intent_transfer_s0_pins.json    the registrar's pins (schema intent_transfer_s0_pins/v1): raw files, the
      ingest DB, the three embedding DBs. Committed with nulls: --run (not --pilot) REFUSES a null or different pin; the pins
      are re-checked AFTER the readouts too (a change REFUSES and nothing is written).

Text set (what is embedded, identical for the three embedders): every KEPT item (drop_reason NULL) of the three corpora, the
C4 slot-swap variants and the D5 synthetic pairs, sorted by sha256 of the text (so --limit N embeds a hash-random subset that
is the same for every embedder; the pilot's 500). Its sha256 (over the texts in that order, U+001E-terminated) is pinned in
intent_meta and re-derived at --run.

Hygiene (design section 5; preconditions, each a FAILED PRECONDITION when it trips, never an outcome):
  * every fit goes through fit_rows(C, idx, allowed, what): a row that is not on an allowed side, an OOS row or a dropped row
    REFUSES; the outcome prints "TRAIN-ONLY: <n> fits, 0 EVAL rows, 0 OOS rows" from the audit (FIT_LOG). TRAIN fits: k-means,
    supervised centroids, kNN, TF-IDF / SVD, slot inventory, P(y|cell), the D2 centroids; GATE fits: the vMF kappa (D4) and the
    C2 threshold. EVAL is read once, by the readouts. OOS never enters a fit.
  * census: EVAL counts within 5% of the planning values (PLANNED) or --census-bracket "<the registrar's bracket>" (printed
    verbatim into the outcome); otherwise --run REFUSES.
  * no non-empty -wal / -journal on any read (every read: mode=ro&immutable=1 after the sidecar check).
  * pins re-checked before and after; embeddings_cache.db per-table hashes unchanged across --embed --go.
  * transport preflight (--dry-run; and before any --go write): per embedder, route parity on PARITY_N = 20 texts of the
    embedder's cache of record (first 20 by sha256 of the text; min cos after slice-256 + renormalise >= 0.9999, embedder_arms'
    rule) and a TIMED PROBE of PROBE_N = 500 texts of the text set (posted, NOT written) that prices the full embedding.
  * no other heavy process: --go REFUSES while a java.exe runs (a construction or site null); Ollama is the one heavy process.

Instrument (draft section 7): embedders qwen3-embedding:latest, nomic-embed-text:latest, embeddinggemma:latest, RAW; slice 256
then renormalise (deciding), slice 512 printed. Spherical k-means: k-means++ (D^2 = 1 - cos), n_init 1, max_iter 300, seeds 0-4,
fit on TRAIN, EVAL filed to the nearest centroid. NMI arithmetic (sklearn's convention), ARI printed. Intervals: 95% percentile,
CK-CLOSE-component bootstrap (a component = the corpus's items sharing one stem_key), B = 2,000, seed BOOT_SEED, partitions fixed.

Criteria (verbatim logic of the draft; the verdict words are printed by criteria_lines, every branch executed by the selftest):
  S0-C1  D(e, g) = mean over seeds of NMI_e,g - NMI_qwen3,g (EVAL, slice 256), e in {nomic, gemma}, g in {coarse, fine}.
         WORSE iff D < -bar AND the paired CI upper < 0; BETTER iff D > bar AND lower > 0; bar = max(MDE80, spread),
         MDE80 = 2.8 x the bootstrap SE of D, spread = max(spread_qwen3, spread_e), spread_x = max - min over seeds of NMI_x.
         C1a HELD iff at least 1 of the 2 families is WORSE at the fine level on at least 2 of 3 corpora; FAILED otherwise.
         C1b NOT FIRED iff 0 of 2 are WORSE at the coarse level on both MASSIVE and CLINC; FIRES otherwise.
  S0-C2  A = AUROC of max-cos to label-free k-means (K 150, in-scope TRAIN) centroids, in-scope EVAL (positive) vs OOS.
         HELD iff lower(A) >= 0.85; FAILED iff upper(A) < 0.85; UNDETERMINED otherwise. FPR95 at the GATE 95%-TPR threshold.
  S0-C3  rho = Spearman(m_c, EVAL gold purity_c) over the K_f cells (qwen3 256, seed 0) with >= 10 EVAL items; cell bootstrap.
         HELD iff lower(rho) > 0 on >= 2 of 3 corpora; FAILED iff upper(rho) <= 0 on >= 2 of 3; UNDETERMINED otherwise.
  S0-C4  S = P(same k-means cell at K_f 60 | original, variant) (MASSIVE). HELD iff lower(S) >= 0.80; FAILED iff upper(S) < 0.80;
         UNDETERMINED otherwise.
  Falsifiers F1 (C1a FAILED), F1' (C1b FIRES), F2 (C2 FAILED), F3 (C3 FAILED), F4 (C4 FAILED): each printed FIRED / NOT FIRED.
  Predictions P1-P6 scored (a numeric prediction HELD iff its point lies in the 80% interval; a probability on its event, Brier
  beside). Descriptive D1-D6 printed with n; D7 NOT RUN (R-3) unless the author admits HWU64 (the steward's count).

[2026-09-30, the engine-coder, intent-s0b after READY_intent_s0 0f3591a; insertion only, the text above and below stands]
C-1 / C-2: C1's interval of record is the BASIC (reverse-percentile) bootstrap interval [2D - q97.5, 2D - q2.5] of the paired
component bootstrap; the bias b = mean(draws) - D, b / SE and the bias-corrected point D - b are printed beside; the percentile
interval is printed as DESCRIPTIVE (the registrar brackets the interval of record). C-4 (the orchestrator's ruling): B2 now
follows the registration's FAIL OBSERVABLE, "C1a fewer than 2 corpora with a WORSE fine family": C1a HELD iff at least 2 of 3
corpora have a WORSE fine family (either family; per corpus); the per-family reading is printed beside as NOT OF RECORD. B3 (seed 0
for C2 / C4) confirmed. B7 follows the design ("slot values swapped": every swappable slot); the swapped slots are printed
(per-variant counts and slot types in the outcome, s0_c4_variants.csv beside: item ids and slot TYPES only, no text). C-7: the
Hanley-McNeil SE is computed in its own order (A, n_pos = in-scope EVAL, n_neg = OOS): 0.0035 x sqrt(1.05) = 0.0036 at the planning
counts; the registered 0.0059 (counts swapped) is printed beside as conservative. C-6: the resolved Ollama URL is printed in
--dry-run and in every --embed header. C-8: --run compares the ingest DB's provenance sha256s with pins["raw"] (strict: every
raw pin set and equal); a MASSIVE row whose annot does not render to its text is EXCLUDED from C4 (counted). C-3: the selftest
recomputes the C1 and C2 intervals independently (paired, stratified weights) and the C3 / C4 seed-0 partitions.

[2026-09-30, the engine-coder, EMB-PACE after the qwen3 --go incident (experiment_results/intent_transfer_s0/embed/
embed_qwen3_go.log, main 6885f92: HTTP 400 WSAENOBUFS "lacked sufficient buffer space ... queue was full" refused as
non-transient); insertion only] embedder_arms now retries that 400 as transient (same bounded whole-batch rule). --embed E --go
takes two OPTIONAL pacing flags, both off by default: --pace-s S (a fixed pause after each committed batch) and --tw-drain N
(after a transient error's backoff, wait until the host's TIME_WAIT count is below N, polled, capped). Pacing never enters
intent_meta: it does not change a vector. PARTIAL FILES: intent_meta pins this script's LF blob and embedder_arms' LF blob; both
changed here, so a file started under the previous blobs (the incident's partial intent_emb_qwen3.db) REFUSES to resume
("intent_meta mismatch on ['embedder_arms_blob_lf', 'script_blob_lf']"). It is DISCARDED (the operator moves it aside), never
resumed or re-pinned; the rerun starts a fresh file under the new blobs. A resume is admitted only under the same pins (same
blobs, model, digest, text set, ingest), with INSERT OR IGNORE of the missing texts in whole batches.

BUILDER'S READINGS B1-B8 (points the registered text leaves open; each printed in the outcome; the registrar confirms or brackets):
  B1 C1 spread: max(spread_qwen3, spread_e) (the draft: "spread is the max-min over k-means seeds 0-4"; the per-seed D spread is
     printed beside). B2 C1a: "per family" (a family WORSE on >= 2 corpora); the alternative "per corpus" reading (>= 2 corpora
     with ANY family WORSE) is printed beside as NOT OF RECORD [SUPERSEDED 2026-09-30 by the orchestrator's C-4 ruling: C1a is
     per corpus, the fail observable's wording; the per-family reading is printed beside as NOT OF RECORD]. B3 C2 and C4: qwen3 slice 256, seed 0 (C3's instrument); seeds
     1-4 printed. B4 C2 bootstrap stratified (in-scope and OOS components resampled separately). B5 D5: 500 pairs on MASSIVE
     + 500 on CLINC (1,000). B6 D4: P(y|c) Laplace-smoothed with ALPHA = 0.1, prior = TRAIN cell shares, kappa on a log grid
     1..1000 (61 points) by GATE NLL. B7 C4 variant: EVERY slot with an alternative same-type, same-intent TRAIN value
     (norm-v1-different) is swapped; an item with none is excluded (counted). B8 P2 "qwen3 BETTER than both": both families
     WORSE on the corpus.

Launch sequence (run-operator; zero judge calls; one heavy process; no construction running):
  python tools/analysis/intent_transfer_s0.py --selftest
  python tools/analysis/intent_transfer_s0.py --mutants
  python tools/ingest/intent_ingest.py --fetch ; python tools/ingest/intent_ingest.py --manifest
  (registrar pins raw + ingest DB)
  python tools/analysis/intent_transfer_s0.py --dry-run          # census, denominators, support, transport preflight + timed probe price
  python tools/analysis/intent_transfer_s0.py --embed qwen3 --limit 500 --go ; ... nomic ; ... gemma        # pilot rows
  python tools/analysis/intent_transfer_s0.py --run --pilot      # smoke readout -> s0_outcome_PILOT.txt (discarded)
  python tools/analysis/intent_transfer_s0.py --embed qwen3 --go ; ... nomic --go ; ... gemma --go          # resumes to complete
  (registrar pins the three embedding DBs)
  python tools/analysis/intent_transfer_s0.py --run              # the file of record (write-once)
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import argparse
import contextlib
import csv
import hashlib
import io
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
import split_side as SS            # noqa: E402
import embedder_arms as EA         # noqa: E402  (keep-alive client, bounded retry, write_vectors; imports nothing of record)
import intent_ingest as II         # noqa: E402
from data_v2 import ro as RO       # noqa: E402

TAG = "[INTENT-S0]"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
OUT_DIR = os.path.join(ROOT, "experiment_results", "intent_transfer")
OUTCOME = "s0_outcome.txt"

EMBEDDERS = ("qwen3", "nomic", "gemma")
FAMILIES = ("nomic", "gemma")
ARM = {"qwen3": "qwen3_raw", "nomic": "nomic_raw", "gemma": "gemma_raw"}      # embedder_arms' RAW arms (prefix "", no transform)
MODEL = {e: EA.ARMS[ARM[e]].model for e in EMBEDDERS}
RECORD_CACHE = {e: EA.cache_file(EA.ARMS[ARM[e]]) for e in EMBEDDERS}        # the caches of record: parity source ONLY (read)
SHARED_CACHES = ("embeddings_cache.db", "embeddings_cache_nomic-embed-text_latest.db", "embeddings_cache_embeddinggemma_latest.db")

SLICE, SLICE2 = 256, 512
SEEDS = (0, 1, 2, 3, 4)
BOOT_B = 2000
BOOT_SEED = 20260929
SEED_C4, SEED_D5, SEED_D2, SEED_COFILE = 4104, 5105, 2102, 4204
C2_BAR, C4_BAR = 0.85, 0.80
C3_MIN_EVAL = 10
TPR_TARGET = 0.95
KNN_K = 15
ALPHA = 0.1
KAPPA_GRID = np.geomspace(1.0, 1000.0, 61)
N_PAIRS = {"massive": 500, "clinc": 500}
D2_REPS = 1000
NEAR_COS = 0.98
PARITY_N = 20
PARITY_COS = EA.PARITY_COS
# [2026-09-30, intent-s0c] per-embedder parity bar (the orchestrator's ruling on the qwen3 diagnosis, 9699d7d): numeric drift of the
# qwen3 route is >= 0.99915 (5 stored rows drift deterministically; GPU batch nondeterminism on one long text) while the smallest
# real route error measured (a trailing space) gives min 0.9846; qwen3 0.998, nomic and gemma keep embedder_arms' 0.9999.
PARITY_BAR = {"qwen3": 0.998, "nomic": 0.9999, "gemma": 0.9999}
PARITY_SOURCE = {
    "qwen3": "orchestrator's ruling 2026-09-30 on experiment_results/intent_transfer_s0/qwen3_parity_diagnosis_2026-09-30.txt (9699d7d): "
             "drift >= 0.99915, smallest route error 0.9846",
    "nomic": "embedder_arms.PARITY_COS 0.9999 (READY_w0_delta1 C8-3)",
    "gemma": "embedder_arms.PARITY_COS 0.9999 (READY_w0_delta1 C8-3)",
}
PROBE_N = 500
CENSUS_TOL = 0.05
PLANNED = {"massive": 4890, "clinc": 6750, "clinc_oos": 1350, "banking77": 3925}     # EVAL planning counts (draft Support (a))
LEVELS = {"massive": ("coarse", "fine"), "clinc": ("coarse", "fine"), "banking77": ("fine",)}
CORPORA = II.CORPORA

# The registered predictions (draft section 7 "Predictions"); scored in predictions_lines.
P1 = {("massive", "coarse"): (0.68, 0.58, 0.78), ("massive", "fine"): (0.78, 0.72, 0.84), ("clinc", "coarse"): (0.50, 0.38, 0.62),
      ("clinc", "fine"): (0.90, 0.86, 0.93), ("banking77", "fine"): (0.80, 0.74, 0.85)}
P2_NOMIC = {"massive": (-0.025, -0.05, 0.00), "clinc": (-0.020, -0.04, 0.00), "banking77": (-0.030, -0.06, -0.005)}
P2_GEMMA = (-0.010, -0.035, 0.015)
P2_PROB = {"C1a HELD": 0.55, "C1b NOT FIRED": 0.65, "qwen3 BETTER than both at fine on >= 2 of 3": 0.40}
P3 = {"A": (0.88, 0.80, 0.94), "FPR95": (0.45, 0.30, 0.65), "HELD": 0.65, "supervised A (point)": 0.91}
P4 = {"massive": (0.45, 0.20, 0.65), "clinc": (0.50, 0.35, 0.62), "banking77": (0.45, 0.25, 0.62), "HELD": 0.75}
P5 = {"S": (0.90, 0.85, 0.95), "HELD": 0.85, "kNN-1 < centroid": 0.60}
P6 = {"D2 massive": (0.45, 0.25, 0.65), "D2 clinc": (0.55, 0.30, 0.75), "D3 share": 0.55, "D4 gain": 0.05}

SLOT_RE = re.compile(r"\[\s*([^\[\]:]+?)\s*:\s*([^\[\]]*?)\s*\]")


class Skip(Exception):
    """A readout that cannot run on the rows present (n < k, no cell): a PILOT prints SKIPPED; a --run REFUSES."""


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    return RO.git_blob_lf(path)


# ------------------------------------------------------------------------------------------------ data
class Corpus(object):
    """One corpus's rows (every row, dropped ones included, so indices are stable); arrays aligned by row."""

    def __init__(self, name, rows):
        self.name = name
        rows = sorted(rows, key=lambda r: r["item_id"])
        self.rows = rows
        self.ids = [r["item_id"] for r in rows]
        self.text = [r["text"] for r in rows]
        self.coarse = np.array([r["coarse"] if r["coarse"] is not None else "" for r in rows], dtype=object)
        self.fine = np.array([r["fine"] for r in rows], dtype=object)
        self.side = np.array([r["side"] for r in rows], dtype=object)
        self.hash_side = np.array([r["hash_side"] for r in rows], dtype=object)
        self.oos = np.array([bool(r["is_oos"]) for r in rows])
        self.kept = np.array([r["drop_reason"] is None for r in rows])
        self.stem = [r["stem_key"] for r in rows]
        self.annot = [r["annot"] for r in rows]
        _, self.comp = np.unique(np.array(self.stem, dtype=object), return_inverse=True)

    def idx(self, side, oos=False):
        m = self.kept & (self.side == side) & (self.oos == oos)
        return np.nonzero(m)[0]

    def labels(self, level):
        return self.fine if level == "fine" else self.coarse


def load_corpora(db_path):
    con = II.open_db_ro(db_path)
    try:
        rows = II.rows_from_db(con)
    finally:
        con.close()
    return {c: Corpus(c, [r for r in rows if r["corpus"] == c]) for c in CORPORA}


FIT_LOG = []


def fit_rows(C, idx, allowed, what):
    """THE split guard of every fit: REFUSES a row off the allowed sides, an OOS row or a dropped row (TRAIN-ONLY assertion)."""
    idx = np.asarray(idx, dtype=int)
    sides = set(C.side[idx].tolist())
    bad = sides - set(allowed)
    n_oos, n_drop = int(C.oos[idx].sum()), int((~C.kept[idx]).sum())
    if bad or n_oos or n_drop:
        refuse("TRAIN-ONLY: fit %r on %s holds sides %s outside %s, %d OOS rows, %d dropped rows" % (what, C.name, sorted(bad), allowed, n_oos, n_drop))
    FIT_LOG.append((what, C.name, len(idx), tuple(sorted(sides))))
    return idx


def fit_audit():
    n = len(FIT_LOG)
    ev = sum(1 for f in FIT_LOG if "EVAL" in f[3])
    return "TRAIN-ONLY: %d fits audited (%d on TRAIN, %d on GATE), %d with an EVAL row, 0 OOS rows, 0 dropped rows (fit_rows refuses otherwise)" % (
        n, sum(1 for f in FIT_LOG if f[3] == ("TRAIN",)), sum(1 for f in FIT_LOG if f[3] == ("GATE",)), ev)


# ------------------------------------------------------------------------------------------------ derived texts (C4, D5)
def parse_annot(a):
    return [(m.start(), m.end(), m.group(1).strip(), m.group(2).strip()) for m in SLOT_RE.finditer(a or "")]


def render_annot(a, values):
    out, pos = [], 0
    for (s, e, _t, _v), val in zip(parse_annot(a), values):
        out.append(a[pos:s])
        out.append(val)
        pos = e
    out.append(a[pos:])
    return "".join(out)


def c4_variants(C):
    """B7: for each KEPT MASSIVE EVAL item with >= 1 slot (item_id order): every slot whose (intent, slot type) has another TRAIN
    value (norm-v1 different) takes one, drawn with SEED_C4 from the sorted candidates. -> (variants, counts). A variant whose
    stem_key equals any MASSIVE TRAIN row's (dropped rows included) or its original's is excluded and counted."""
    tr = fit_rows(C, C.idx(SS.TRAIN), (SS.TRAIN,), "C4 slot inventory")
    inv = {}
    for i in tr:
        for (_s, _e, t, v) in parse_annot(C.annot[i]):
            inv.setdefault((C.fine[i], t), set()).add(v)
    train_keys = set(C.stem[i] for i in range(len(C.ids)) if C.side[i] == SS.TRAIN)
    rng = np.random.default_rng(SEED_C4)
    out, cnt = [], {"eval_items": 0, "with_slot": 0, "no_alternative": 0, "train_collision": 0, "unchanged": 0,
                    "annot_text_mismatch": 0, "variants": 0}
    for i in C.idx(SS.EVAL):
        cnt["eval_items"] += 1
        slots = parse_annot(C.annot[i])
        if not slots:
            continue
        cnt["with_slot"] += 1
        if SS.norm(render_annot(C.annot[i], [v for (_s, _e, _t, v) in slots])) != SS.norm(C.text[i]):
            cnt["annot_text_mismatch"] += 1                       # C-8: EXCLUDED (the variant would not be a swap of the text)
            continue
        vals, changed = [], []
        for (_s, _e, t, v) in slots:
            cands = sorted(x for x in inv.get((C.fine[i], t), ()) if SS.norm(x) != SS.norm(v))
            if cands:
                vals.append(cands[int(rng.integers(len(cands)))])
                changed.append(t)
            else:
                vals.append(v)
        if not changed:
            cnt["no_alternative"] += 1
            continue
        txt = render_annot(C.annot[i], vals)
        sk = SS.stem_key(txt)
        if sk in train_keys:
            cnt["train_collision"] += 1
            continue
        if sk == C.stem[i]:
            cnt["unchanged"] += 1
            continue
        out.append((int(i), txt, tuple(changed)))
    cnt["variants"] = len(out)
    return out, cnt


def c4_swap_summary(C, variants):
    """B7 printed: slots per variant item vs slots swapped, and the swapped slot TYPES (no text)."""
    hist, types = {}, {}
    for i, _t, ch in variants:
        key = "%d of %d" % (len(ch), len(parse_annot(C.annot[i])))
        hist[key] = hist.get(key, 0) + 1
        for t in ch:
            types[t] = types.get(t, 0) + 1
    return hist, sorted(types.items(), key=lambda kv: (-kv[1], kv[0]))


def d5_pairs(C, n):
    """B5: n synthetic two-intent texts "a and b" from KEPT in-scope EVAL items of DIFFERENT coarse labels and components."""
    ev = C.idx(SS.EVAL)
    rng = np.random.default_rng(SEED_D5 + CORPORA.index(C.name))
    seen, out, tries = set(), [], 0
    while len(out) < n and tries < 200 * n and len(ev) > 1:
        tries += 1
        a, b = (int(x) for x in rng.integers(len(ev), size=2))
        i, j = int(ev[a]), int(ev[b])
        if C.coarse[i] == C.coarse[j] or C.comp[i] == C.comp[j] or (i, j) in seen:
            continue
        seen.add((i, j))
        out.append((i, j, C.text[i] + " and " + C.text[j]))
    return out


def text_set(CS):
    """-> (sorted texts, sha256, derived dict). The embedded set: kept items + C4 variants + D5 pairs, sha256-ordered."""
    var, vcnt = c4_variants(CS["massive"])
    pairs = {c: d5_pairs(CS[c], N_PAIRS[c]) for c in N_PAIRS}
    ts = set()
    for C in CS.values():
        ts.update(C.text[i] for i in np.nonzero(C.kept)[0])
    ts.update(t for _i, t, _c in var)
    for c in pairs:
        ts.update(t for _i, _j, t in pairs[c])
    order = sorted(ts, key=lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest())
    h = hashlib.sha256()
    for t in order:
        h.update(t.encode("utf-8") + b"\x1e")
    return order, h.hexdigest(), {"variants": var, "variant_counts": vcnt, "pairs": pairs}


# ------------------------------------------------------------------------------------------------ own embedding DBs
def emb_path(e, emb_dir=None):
    return os.path.join(emb_dir or DATA_ROOT, "intent_emb_%s.db" % e)


def check_emb_dir(emb_dir):
    if II._inside(emb_dir, os.path.join(ROOT, "experiment_results")) or II._inside(emb_dir, os.path.join(DATA_ROOT, "experiment_results")):
        refuse("--emb-dir %s is under experiment_results/ (its *.db are re-included by .gitignore L145)" % emb_dir)
    if not os.path.isdir(emb_dir):
        refuse("--emb-dir %s is not an existing directory" % emb_dir)


def check_emb_target(path):
    if os.path.basename(path) in II.NEVER_WRITE or os.path.basename(path) in SHARED_CACHES:
        refuse("%s is a cache of record: never written" % path)
    for sc in SHARED_CACHES:
        if II._norm(path) == II._norm(os.path.join(DATA_ROOT, sc)):
            refuse("%s resolves to the shared cache %s" % (path, sc))
    for sfx in ("-wal", "-journal"):
        if os.path.exists(path + sfx) and os.path.getsize(path + sfx) > 0:
            refuse("%s%s is non-empty: checkpoint before any write or read" % (path, sfx))


def read_meta(path):
    con = RO.open_ro(path)
    try:
        if not con.execute("SELECT 1 FROM sqlite_master WHERE name='intent_meta'").fetchone():
            refuse("%s carries no intent_meta: not this study's embedding file" % path)
        return dict(con.execute("SELECT key, value FROM intent_meta"))
    finally:
        con.close()


def expected_meta(e, set_sha, n_texts, ingest_sha):
    return {"embedder": e, "model": MODEL[e], "protocol": "RAW", "native_dim": str(EA.EG.NATIVE_DIM[MODEL[e]]),
            "text_set_sha256": set_sha, "n_texts": str(n_texts), "ingest_db_sha256": ingest_sha,
            "script_blob_lf": blob_lf(os.path.abspath(__file__)), "embedder_arms_blob_lf": blob_lf(os.path.abspath(EA.__file__))}


def check_meta(path, want, digest=None):
    got = read_meta(path)
    bad = sorted(k for k in want if got.get(k) != want[k])
    if digest and got.get("model_digest") not in (None, "UNAVAILABLE", digest):
        bad.append("model_digest")
    if bad:
        refuse("%s intent_meta mismatch on %s (pinned %s; now %s): a resumed or read file must carry the first launch's pins; a "
               "file started under other pins is discarded (moved aside), never resumed"
               % (path, bad, {k: got.get(k) for k in bad}, {k: want.get(k, digest) for k in bad}))
    return got


def present_texts(path):
    con = RO.open_ro(path)
    try:
        return set(t for (t,) in con.execute("SELECT query FROM embeddings"))
    finally:
        con.close()


def load_vectors(path, e, texts, allow_missing=False):
    """-> {text: float32[512]} for the texts (raw, un-normalised first SLICE2 dims). REFUSES a vector that is not the model's
    native dimension and (unless allow_missing, the pilot) a missing text."""
    native = EA.EG.NATIVE_DIM[MODEL[e]]
    want = set(texts)
    out, dims = {}, {}
    con = RO.open_ro(path)
    try:
        for t, b in con.execute("SELECT query, vector FROM embeddings"):
            if t not in want:
                continue
            n = len(b) // 4
            dims[n] = dims.get(n, 0) + 1
            if n != native:
                continue
            out[t] = np.frombuffer(b, dtype=">f4", count=SLICE2).astype(np.float32)
    finally:
        con.close()
    miss = len(want) - len(out)
    print("%s %s: %d of %d texts have a %d-d vector (dims seen %s)" % (TAG, e, len(out), len(want), native, dict(sorted(dims.items()))))
    if set(dims) - {native}:
        refuse("%s: vector dims %s != {%d}" % (e, sorted(dims), native))
    if miss and not allow_missing:
        refuse("%s: %d texts of the registered set have no vector (complete the embedding first; --pilot reads partial)" % (e, miss))
    return out


def _foreign_heavy():
    """-> a list of heavy foreign processes (a JVM = a construction or site null). Windows tasklist; elsewhere pgrep."""
    try:
        if os.name == "nt":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq java.exe", "/NH", "/FO", "CSV"], capture_output=True, text=True,
                                 timeout=30).stdout
            return [ln for ln in out.splitlines() if ln.lower().startswith('"java.exe"')]
        out = subprocess.run(["pgrep", "-l", "java"], capture_output=True, text=True, timeout=30).stdout
        return [ln for ln in out.splitlines() if ln.strip()]
    except Exception as ex:                                 # noqa: BLE001
        return ["UNCHECKABLE (%s)" % ex]


def record_table_hashes():
    """Per-table hashes of the shared caches that exist under DATA_ROOT (read-only, immutable, sidecars checked)."""
    out = {}
    for sc in SHARED_CACHES:
        p = os.path.join(DATA_ROOT, sc)
        if not os.path.isfile(p):
            out[sc] = "absent"
            continue
        con = RO.open_ro(p)
        try:
            out[sc] = {t: v["table_sha"][:16] + "/%d" % v["rows"] for t, v in RO.table_shas(con).items()}
        finally:
            con.close()
    return out


def route_parity(e, embed_fn, n=PARITY_N, bar=None):
    """embedder_arms' route-parity rule on the embedder's cache of RECORD (read-only): the first n texts by sha256 of the text,
    re-embedded via /api/embed, min cos after slice-256 + renormalise >= bar; REFUSES below the bar or with < n rows. Reads only
    the n chosen blobs (the qwen3 cache is ~0.7 GB). bar None -> PARITY_BAR[e] (per embedder; its source printed)."""
    bar = PARITY_BAR[e] if bar is None else bar
    print("%s TRANSPORT parity bar %s: min cos >= %.4f (source: %s)" % (TAG, e, bar, PARITY_SOURCE[e]))
    p = os.path.join(DATA_ROOT, RECORD_CACHE[e])
    con = RO.open_ro(p)
    try:
        keys = sorted((hashlib.sha256(t.encode("utf-8")).hexdigest(), t) for (t,) in con.execute("SELECT query FROM embeddings"))
        if len(keys) < n:
            refuse("route parity %s: %d rows in %s < %d" % (e, len(keys), p, n))
        chosen = [t for _h, t in keys[:n]]
        blobs = [con.execute("SELECT vector FROM embeddings WHERE query = ?", (t,)).fetchone()[0] for t in chosen]
    finally:
        con.close()
    new = embed_fn(MODEL[e], chosen)
    cos = [float(np.dot(EA._slice_unit(np.frombuffer(b, dtype=">f4").astype(np.float64)), EA._slice_unit(v))) for b, v in zip(blobs, new)]
    mn = min(cos)
    print("%s TRANSPORT route parity %s: %d texts of %s re-embedded via /api/embed, cos after slice-%d + renormalise min %.6f "
          "median %.6f (bar >= %.4f): %s" % (TAG, e, len(cos), RECORD_CACHE[e], EA.PARITY_SLICE, mn, float(np.median(cos)), bar,
                                             "PASS" if mn >= bar else "FAIL"))
    if not mn >= bar:
        refuse("route parity %s: min cos %.6f < %.4f" % (e, mn, bar))
    return mn


def timed_probe(e, texts, embed_fn, n=PROBE_N, n_total=None):
    """Posts the first n texts of the set (sha order) in embedder_arms' batches, writes NOTHING; -> texts per second."""
    sub = texts[:n]
    t0 = time.perf_counter()
    for s in range(0, len(sub), EA.BATCH):
        embed_fn(MODEL[e], sub[s:s + EA.BATCH])
    dt = max(time.perf_counter() - t0, 1e-9)
    rate = len(sub) / dt
    tot = len(texts) if n_total is None else n_total
    print("%s PRICE %s: timed probe %d texts in %.1f s = %.1f texts/s -> %d texts to embed = %.1f min (estimate from the probe)"
          % (TAG, e, len(sub), dt, rate, tot, tot / rate / 60.0))
    return rate


def embed(e, go, limit=None, emb_dir=None, db=None, embed_fn=None):
    embed_fn = embed_fn or EA.ollama_embed
    emb_dir = emb_dir or DATA_ROOT
    check_emb_dir(emb_dir)
    path = emb_path(e, emb_dir)
    check_emb_target(path)
    db = db or II.DEFAULT_OUT
    ingest_sha = pin_check(db, "ingest_db", strict=False)
    CS = load_corpora(db)
    texts, set_sha, _d = text_set(CS)
    want = expected_meta(e, set_sha, len(texts), ingest_sha)
    exists = os.path.exists(path)
    if exists:
        check_meta(path, want)
        have = present_texts(path)
    else:
        have = set()
    miss = [t for t in texts if t not in have]
    todo = miss if limit is None else [t for t in texts[:int(limit)] if t not in have]
    print("%s embed %s (%s, RAW) -> %s (%s): text set %d (sha256 %s), present %d, missing %d, this launch %d%s"
          % (TAG, e, MODEL[e], path, "exists: RESUME" if exists else "new", len(texts), set_sha[:16], len(have), len(miss), len(todo),
             "" if limit is None else " (--limit %d)" % int(limit)))
    if not go:
        print("%s dry: nothing posted, nothing written (add --go)" % TAG)
        return 0
    print("%s Ollama endpoint %s (resolved from OLLAMA_HOST=%r by embedder_arms.client_base)" % (TAG, EA.OLLAMA_URL, os.environ.get("OLLAMA_HOST")))
    heavy = _foreign_heavy()
    if heavy:
        refuse("a foreign heavy process runs (%s): one heavy process at a time; the embedding waits" % heavy[:3])
    before = record_table_hashes()
    print("%s shared caches per-table before: %s" % (TAG, json.dumps(before, sort_keys=True)))
    route_parity(e, embed_fn)
    digest = EA.model_digest(MODEL[e]) or "UNAVAILABLE"
    if not exists:
        with open(path, "xb"):                            # exclusive create: a file that appeared meanwhile is never overwritten
            pass
        con = sqlite3.connect(path)
        try:
            con.execute("PRAGMA journal_mode=DELETE")
            con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
            con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(want, model_digest=digest).items()))
            con.commit()
        finally:
            con.close()
    else:
        check_meta(path, want, digest=digest)
    n = EA.write_vectors(path, EA.ARMS[ARM[e]], todo, embed_fn) if todo else 0
    after = record_table_hashes()
    if after != before:
        refuse("the shared caches' per-table hashes CHANGED during the embedding: before %s after %s" % (before, after))
    print("%s shared caches per-table after: unchanged" % TAG)
    left = len(miss) - n
    print("%s embed %s: wrote %d; %d of the set still missing%s" % (TAG, e, n, left, "" if left else " (COMPLETE)"))
    return n


# ------------------------------------------------------------------------------------------------ pins
def pin_check(path, key, strict, sub=None, pins_file=None, label=None):
    """-> sha256 of path; prints it against the registrar's pin; REFUSES a different pin, and (strict) a null pin."""
    pins = II.load_pins(pins_file or PINS_FILE_OVERRIDE[0])
    want = pins.get(key) if sub is None else (pins.get(key) or {}).get(sub)
    II.open_db_ro(path).close()                                     # sidecar + existence check
    s = II.file_sha(path)
    print("%s pin %s: sha256 %s [%s]" % (TAG, label or os.path.basename(path), s,
                                         "UNPINNED" if not want else ("PIN OK" if want == s else "PIN MISMATCH")))
    if want and want != s:
        refuse("%s sha256 %s != the pinned %s" % (path, s, want))
    if strict and not want:
        refuse("%s is UNPINNED: --run writes the file of record only against the registrar's pins (%s)" % (path, II.PINS_FILE))
    return s


PINS_FILE_OVERRIDE = [None]


# ------------------------------------------------------------------------------------------------ statistics
def unit(X):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def codes(labels):
    _, c = np.unique(np.asarray(labels, dtype=object).astype(str), return_inverse=True)
    return c.astype(np.int64)


def nmi(t, p, w=None):
    """Arithmetic NMI (sklearn's convention), with optional item weights (the bootstrap's multiplicities)."""
    t, p = np.asarray(t, dtype=np.int64), np.asarray(p, dtype=np.int64)
    kt, kp = int(t.max()) + 1, int(p.max()) + 1
    cont = np.bincount(t * kp + p, weights=w, minlength=kt * kp).reshape(kt, kp).astype(np.float64)
    n = cont.sum()
    pt, pp = cont.sum(1) / n, cont.sum(0) / n
    nt, npp = int((pt > 0).sum()), int((pp > 0).sum())
    if nt == npp == 1:
        return 1.0
    pij = cont / n
    nz = pij > 0
    mi = float((pij[nz] * np.log(pij[nz] / np.outer(pt, pp)[nz])).sum())
    if mi <= 0:
        return 0.0
    ht = -float((pt[pt > 0] * np.log(pt[pt > 0])).sum())
    hp = -float((pp[pp > 0] * np.log(pp[pp > 0])).sum())
    return mi / max((ht + hp) / 2.0, np.finfo(np.float64).eps)


def ari(t, p):
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(np.asarray(t), np.asarray(p)))


def auroc(pos, neg, wp=None, wn=None):
    """P(score_pos > score_neg) + 0.5 P(tie), weighted."""
    pos, neg = np.asarray(pos, dtype=np.float64), np.asarray(neg, dtype=np.float64)
    wp = np.ones(len(pos)) if wp is None else np.asarray(wp, dtype=np.float64)
    wn = np.ones(len(neg)) if wn is None else np.asarray(wn, dtype=np.float64)
    u, inv = np.unique(np.concatenate([pos, neg]), return_inverse=True)
    ip, ineg = inv[:len(pos)], inv[len(pos):]
    Wp = np.bincount(ip, weights=wp, minlength=len(u))
    Wn = np.bincount(ineg, weights=wn, minlength=len(u))
    below = np.cumsum(Wn) - Wn
    den = Wp.sum() * Wn.sum()
    return float((Wp * (below + 0.5 * Wn)).sum() / den) if den > 0 else float("nan")


def hanley_mcneil(A, n_pos, n_neg):
    """Hanley & McNeil (1982): Q1 = A / (2 - A) pairs with (n_pos - 1), Q2 = 2A^2 / (1 + A) with (n_neg - 1); positives = the class
    scored higher (here in-scope EVAL). C-7: the registration's Support (d) swapped the counts (0.0059, conservative)."""
    q1, q2 = A / (2 - A), 2 * A * A / (1 + A)
    return float(np.sqrt((A * (1 - A) + (n_pos - 1) * (q1 - A * A) + (n_neg - 1) * (q2 - A * A)) / (n_pos * n_neg)))


def spearman(x, y):
    from scipy.stats import spearmanr
    x, y = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    return float(spearmanr(x, y).correlation)


def comp_weights(comp, B, rng):
    """Yields B item-weight vectors: components resampled with replacement (CK-CLOSE-component bootstrap)."""
    _, cc = np.unique(comp, return_inverse=True)
    G = int(cc.max()) + 1
    for _ in range(B):
        yield np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(np.float64)


def pct_ci(draws):
    d = np.asarray([x for x in draws if np.isfinite(x)], dtype=np.float64)
    if len(d) == 0:
        return float("nan"), float("nan")
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def kish(comp):
    """Kish mean cluster size sum m^2 / sum m over the item set's components (the DEFF at ICC = 1, the worst case)."""
    _, m = np.unique(comp, return_counts=True)
    return float((m.astype(np.float64) ** 2).sum() / max(1, m.sum()))


def skmeans(X, k, seed, max_iter=300):
    """Spherical k-means: k-means++ seeding (D^2 = 1 - cos on unit vectors), n_init 1, Lloyd steps to max_iter or a fixed point."""
    n = len(X)
    if n < k or k < 1:
        raise Skip("n %d < k %d" % (n, k))
    rng = np.random.default_rng(seed)
    first = int(rng.integers(n))
    C = [X[first]]
    dmin = np.clip(1.0 - X @ X[first], 0.0, None)
    for _ in range(1, k):
        s = dmin.sum()
        i = int(rng.choice(n, p=dmin / s)) if s > 0 else int(rng.integers(n))
        C.append(X[i])
        dmin = np.minimum(dmin, np.clip(1.0 - X @ X[i], 0.0, None))
    C = np.array(C)
    lab = None
    for _ in range(max_iter):
        new = np.argmax(X @ C.T, axis=1)
        if lab is not None and np.array_equal(new, lab):
            break
        lab = new
        S = np.zeros_like(C)
        np.add.at(S, lab, X)
        nrm = np.linalg.norm(S, axis=1)
        keep = nrm > 0
        C[keep] = S[keep] / nrm[keep, None]
    return C


def assign(X, C):
    return np.argmax(X @ C.T, axis=1)


def centroids_by_label(X, lab):
    u = np.unique(lab)
    return u, unit(np.array([X[lab == v].mean(0) for v in u]))


class Space(object):
    """The vectors of one embedder for one corpus's rows, sliced and renormalised; derived texts looked up on demand."""

    def __init__(self, vecs, C, d):
        self.vecs, self.d = vecs, d
        self.have = np.array([t in vecs for t in C.text])
        Z = np.zeros((len(C.text), d))
        for i, t in enumerate(C.text):
            if self.have[i]:
                Z[i] = vecs[t][:d]
        self.X = unit(Z)

    def of(self, texts):
        return unit(np.array([self.vecs[t][:self.d] for t in texts], dtype=np.float64).reshape(len(texts), self.d))


def km_fit(C, S, k, seed, what):
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), what)
    return skmeans(S.X[tr], k, seed)


def S_idx(C, S, side, oos=False):
    i = C.idx(side, oos)
    return i[S.have[i]]


# ------------------------------------------------------------------------------------------------ readouts
def c1_level(C, spaces, level, k, rng_seed):
    """S0-C1 for one corpus x level at one slice: per embedder x seed the EVAL NMI / ARI; paired component bootstrap of D."""
    ev = S_idx(C, spaces["qwen3"], SS.EVAL)
    for e in EMBEDDERS:
        ev = ev[spaces[e].have[ev]]
    if len(ev) == 0:
        raise Skip("no EVAL row")
    truth = codes(C.labels(level)[ev])
    preds, nm, ar = {}, {}, {}
    for e in EMBEDDERS:
        preds[e] = [assign(spaces[e].X[ev], km_fit(C, spaces[e], k, s, "C1 k-means %s %s K=%d s%d" % (e, level, k, s))) for s in SEEDS]
        nm[e] = [nmi(truth, p) for p in preds[e]]
        ar[e] = [ari(truth, p) for p in preds[e]]
    D = {e: float(np.mean(nm[e]) - np.mean(nm["qwen3"])) for e in FAMILIES}
    draws = {e: [] for e in FAMILIES}
    for w in comp_weights(C.comp[ev], BOOT_B, np.random.default_rng(rng_seed)):
        m = {e: np.mean([nmi(truth, p, w) for p in preds[e]]) for e in EMBEDDERS}
        for e in FAMILIES:
            draws[e].append(m[e] - m["qwen3"])
    out = {"n": int(len(ev)), "components": int(len(np.unique(C.comp[ev]))), "kish": kish(C.comp[ev]), "k": k,
           "nmi": nm, "ari": ar, "D": D, "preds": preds, "truth": truth, "per": {}}
    spread = {e: float(max(nm[e]) - min(nm[e])) for e in EMBEDDERS}
    out["spread"] = spread
    for e in FAMILIES:
        se = float(np.std(draws[e], ddof=1))
        plo, phi = pct_ci(draws[e])
        lo, hi = basic_ci(D[e], draws[e])                        # C-1 / C-2: the BASIC interval decides
        bmean = float(np.mean(draws[e]))
        bar = max(2.8 * se, max(spread["qwen3"], spread[e]))
        dseed = [a - b for a, b in zip(nm[e], nm["qwen3"])]
        out["per"][e] = {"D": D[e], "lo": lo, "hi": hi, "plo": plo, "phi": phi, "se": se, "mde80": 2.8 * se, "bar": bar,
                         "bmean": bmean, "bias": bmean - D[e], "dbc": 2 * D[e] - bmean, "draws": draws[e],
                         "spread_seedD": float(max(dseed) - min(dseed)), "status": c1_status(D[e], lo, hi, bar)}
    return out


def basic_ci(point, draws):
    """The basic (reverse-percentile) 95% interval [2 point - q97.5, 2 point - q2.5] (C-1: removes the first-order bias shift)."""
    qlo, qhi = pct_ci(draws)
    return 2 * point - qhi, 2 * point - qlo


def c1_status(D, lo, hi, bar):
    if D < -bar and hi < 0:
        return "WORSE"
    if D > bar and lo > 0:
        return "BETTER"
    return "NEITHER"


def c2(C, spaces, seeds=SEEDS):
    """S0-C2 on CLINC (B3: qwen3 256 seed 0 decides; R-2: the OOS denominator is every kept CLINC OOS row, all forced to EVAL
    by the ingest whatever their hash side)."""
    S = spaces["qwen3"]
    ev_in, ev_oos, gate = S_idx(C, S, SS.EVAL), S_idx(C, S, SS.EVAL, oos=True), S_idx(C, S, SS.GATE)
    if len(ev_oos) == 0 or len(ev_in) == 0 or len(gate) == 0:
        raise Skip("C2 needs in-scope EVAL, OOS EVAL and GATE rows (%d / %d / %d)" % (len(ev_in), len(ev_oos), len(gate)))
    kf = II.GOLD_K["clinc"][1]

    def scores(Cm, X):
        return (X @ Cm.T).max(1)
    per_seed, res = [], None
    for s in seeds:
        Cm = km_fit(C, S, kf, s, "C2 k-means K=%d s%d" % (kf, s))
        si, so, sg = scores(Cm, S.X[ev_in]), scores(Cm, S.X[ev_oos]), scores(Cm, S.X[fit_rows(C, gate, (SS.GATE,), "C2 threshold s%d" % s)])
        A = auroc(si, so)
        per_seed.append(A)
        if s == 0:
            res = (si, so, sg)
    si, so, sg = res
    thr = float(np.sort(sg)[int(np.floor((1 - TPR_TARGET) * len(sg)))])        # >= 95% of GATE in-scope scores are >= thr
    A = per_seed[0]
    rng = np.random.default_rng(BOOT_SEED + 2)
    ci_in, ci_oos = C.comp[ev_in], C.comp[ev_oos]
    draws = []
    for wi, wo in zip(comp_weights(ci_in, BOOT_B, rng), comp_weights(ci_oos, BOOT_B, rng)):
        draws.append(auroc(si, so, wi, wo))
    lo, hi = pct_ci(draws)
    n1, n2 = len(ev_oos), len(ev_in)
    kin, koos = kish(ci_in), kish(ci_oos)
    deff = max(kin, koos)
    out = {"A": A, "lo": lo, "hi": hi, "se_boot": float(np.std(draws, ddof=1)), "thr": thr, "fpr95": float(np.mean(so >= thr)),
           "tpr_eval": float(np.mean(si >= thr)), "tpr_gate": float(np.mean(sg >= thr)), "n_in": n2, "n_oos": n1, "n_gate": len(sg),
           "draws": draws, "hm_se": hanley_mcneil(A, n2, n1), "hm_se_swapped": hanley_mcneil(A, n1, n2), "deff": deff, "per_seed": per_seed, "scores": (si, so, sg)}
    out["verdict"] = band(lo, hi, C2_BAR)
    # printed beside: supervised TRAIN-centroid max-cos; K in {50, 100, 300}; nomic / gemma at K_f seed 0
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "C2 supervised centroids")
    _u, G = centroids_by_label(S.X[tr], C.fine[tr])
    out["supervised_A"] = auroc(scores(G, S.X[ev_in]), scores(G, S.X[ev_oos]))
    out["K_alt"] = {}
    for K in (50, 100, 300):
        try:
            Cm = km_fit(C, S, K, 0, "C2 k-means K=%d s0" % K)
            out["K_alt"][K] = auroc(scores(Cm, S.X[ev_in]), scores(Cm, S.X[ev_oos]))
        except Skip as ex:
            out["K_alt"][K] = "SKIPPED (%s)" % ex
    out["other_emb"] = {}
    for e in FAMILIES:
        Se = spaces[e]
        ii, oo = S_idx(C, Se, SS.EVAL), S_idx(C, Se, SS.EVAL, oos=True)
        Cm = km_fit(C, Se, kf, 0, "C2 k-means %s s0" % e)
        out["other_emb"][e] = auroc(scores(Cm, Se.X[ii]), scores(Cm, Se.X[oo]))
    return out


def band(lo, hi, bar):
    if lo >= bar:
        return "HELD"
    if hi < bar:
        return "FAILED"
    return "UNDETERMINED"


def cell_margin_purity(C, S, Cm):
    """Per cell: m_c = mean over its TRAIN members of cos(own) - cos(second-nearest); EVAL purity; EVAL count."""
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "C3 margins")
    sims = S.X[tr] @ Cm.T
    top2 = np.sort(sims, axis=1)[:, -2:]
    own = np.argmax(sims, axis=1)
    marg = top2[:, 1] - top2[:, 0]
    ev = S_idx(C, S, SS.EVAL)
    evc = assign(S.X[ev], Cm)
    rows = []
    for c in range(len(Cm)):
        m = marg[own == c]
        labs = C.fine[ev][evc == c]
        n_ev = int(len(labs))
        pur = float(max(np.unique(labs, return_counts=True)[1]) / n_ev) if n_ev else float("nan")
        rows.append({"cell": c, "n_train": int((own == c).sum()), "margin": float(m.mean()) if len(m) else float("nan"),
                     "n_eval": n_ev, "purity": pur})
    return rows


def c3(C, spaces):
    S = spaces["qwen3"]
    kf = II.GOLD_K[C.name][1]
    per_seed, main = {}, None
    for s in SEEDS:
        Cm0 = km_fit(C, S, kf, s, "C3 k-means s%d" % s)
        cells = cell_margin_purity(C, S, Cm0)
        use = [r for r in cells if r["n_eval"] >= C3_MIN_EVAL and np.isfinite(r["margin"])]
        rho = spearman([r["margin"] for r in use], [r["purity"] for r in use])
        per_seed[s] = rho
        if s == 0:
            main = (cells, use, rho, Cm0)
    cells, use, rho, Cm0 = main
    m, p = np.array([r["margin"] for r in use]), np.array([r["purity"] for r in use])
    rng = np.random.default_rng(BOOT_SEED + 3 + CORPORA.index(C.name))
    draws = []
    for _ in range(BOOT_B):
        j = rng.integers(len(use), size=len(use)) if len(use) else np.array([], dtype=int)
        draws.append(spearman(m[j], p[j]) if len(use) else float("nan"))
    lo, hi = pct_ci(draws)
    ncell = len(use)
    return {"rho": rho, "lo": lo, "hi": hi, "n_cells": ncell, "n_excluded": len(cells) - ncell, "per_seed": per_seed,
            "nan_draws": int(sum(1 for d in draws if not np.isfinite(d))), "cells": cells, "k": kf, "Cm": Cm0,
            "se_z": (1.0 / np.sqrt(ncell - 3)) if ncell > 3 else float("nan")}


def c3_verdict(res):
    pos = [c for c in CORPORA if c in res and np.isfinite(res[c]["lo"]) and res[c]["lo"] > 0]
    nonpos = [c for c in CORPORA if c in res and np.isfinite(res[c]["hi"]) and res[c]["hi"] <= 0]
    if len(pos) >= 2:
        return "HELD", pos, nonpos
    if len(nonpos) >= 2:
        return "FAILED", pos, nonpos
    return "UNDETERMINED", pos, nonpos


def c4(C, spaces, variants):
    S = spaces["qwen3"]
    kf = II.GOLD_K["massive"][1]
    var = [(i, t) for i, t, _c in variants if S.have[i] and t in S.vecs]
    if not var:
        raise Skip("no variant with a vector")
    oi = np.array([i for i, _t in var])
    Xo, Xv = S.X[oi], S.of([t for _i, t in var])
    per_seed, same0 = {}, None
    for s in SEEDS:
        Cm = km_fit(C, S, kf, s, "C4 k-means s%d" % s)
        same = (assign(Xo, Cm) == assign(Xv, Cm)).astype(np.float64)
        per_seed[s] = float(same.mean())
        if s == 0:
            same0, Cm0 = same, Cm
    comp = C.comp[oi]
    draws = [float((same0 * w).sum() / w.sum()) for w in comp_weights(comp, BOOT_B, np.random.default_rng(BOOT_SEED + 4))]
    lo, hi = pct_ci(draws)
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "C4 supervised centroids / kNN-1")
    u, G = centroids_by_label(S.X[tr], C.fine[tr])
    cent = float(np.mean(u[assign(Xo, G)] == u[assign(Xv, G)]))
    ytr = C.fine[tr]
    knn = float(np.mean(ytr[np.argmax(Xo @ S.X[tr].T, axis=1)] == ytr[np.argmax(Xv @ S.X[tr].T, axis=1)]))
    # random same-intent co-filing: as many pairs as variants, distinct components, the same intent (SEED_COFILE)
    ev = S_idx(C, S, SS.EVAL)
    by = {}
    for i in ev:
        by.setdefault(C.fine[i], []).append(int(i))
    labs = sorted(l for l, v in by.items() if len(v) > 1)
    rng = np.random.default_rng(SEED_COFILE)
    cell = dict(zip(ev.tolist(), assign(S.X[ev], Cm0).tolist()))
    co, tries = [], 0
    while labs and len(co) < len(var) and tries < 100 * len(var):
        tries += 1
        L = by[labs[int(rng.integers(len(labs)))]]
        a, b = L[int(rng.integers(len(L)))], L[int(rng.integers(len(L)))]
        if a != b and C.comp[a] != C.comp[b]:
            co.append(cell[a] == cell[b])
    return {"S": float(same0.mean()), "lo": lo, "hi": hi, "n": int(len(var)), "components": int(len(np.unique(comp))),
            "kish": kish(comp), "se_boot": float(np.std(draws, ddof=1)), "per_seed": per_seed, "centroid_stab": cent,
            "knn1_stab": knn, "cofile": float(np.mean(co)) if co else float("nan"), "cofile_n": len(co), "verdict": band(lo, hi, C4_BAR),
            "same0": same0, "Cm0": Cm0}


def d1(C, spaces_all, level_k):
    """Ceilings: supervised TRAIN-centroid and kNN-15 accuracy per level x embedder; k-means NMI / ARI at 0.5x / 1x / 2x K (256)."""
    out = {}
    for e in EMBEDDERS:
        S = spaces_all[e]
        tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "D1 centroids / kNN %s" % e)
        ev = S_idx(C, S, SS.EVAL)
        if len(ev) == 0:
            raise Skip("no EVAL row")
        sims_top = []
        for s in range(0, len(ev), 1000):
            sm = S.X[ev[s:s + 1000]] @ S.X[tr].T
            j = np.argpartition(-sm, min(KNN_K, sm.shape[1]) - 1, axis=1)[:, :KNN_K]
            sims_top.append((j, np.take_along_axis(sm, j, axis=1)))
        for level, K in level_k:
            lab = C.labels(level)
            u, G = centroids_by_label(S.X[tr], lab[tr])
            acc_c = float(np.mean(u[assign(S.X[ev], G)] == lab[ev]))
            ytr = lab[tr]
            pred = []
            for j, w in sims_top:
                for jj, ww in zip(j, w):
                    sc = {}
                    for a, b in zip(ytr[jj], ww):
                        sc[a] = sc.get(a, 0.0) + b
                    pred.append(max(sorted(sc), key=lambda x: sc[x]))
            acc_k = float(np.mean(np.array(pred, dtype=object) == lab[ev]))
            truth = codes(lab[ev])
            curve = {}
            for mult in (0.5, 1.0, 2.0):
                kk = max(2, int(round(mult * K)))
                try:
                    ps = [assign(S.X[ev], km_fit(C, S, kk, s, "D1 k-means %s %s K=%d s%d" % (e, level, kk, s))) for s in SEEDS]
                    curve[mult] = (kk, float(np.mean([nmi(truth, p) for p in ps])), float(np.mean([ari(truth, p) for p in ps])))
                except Skip as ex:
                    curve[mult] = (kk, "SKIPPED (%s)" % ex, None)
            out[(e, level)] = {"centroid_acc": acc_c, "knn15_acc": acc_k, "curve": curve, "n": int(len(ev))}
    return out


def tfidf_floor(C, level_k):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    tr = fit_rows(C, C.idx(SS.TRAIN), (SS.TRAIN,), "TF-IDF / SVD-256")
    ev = C.idx(SS.EVAL)
    vec = TfidfVectorizer().fit([C.text[i] for i in tr])
    Ttr, Tev = vec.transform([C.text[i] for i in tr]), vec.transform([C.text[i] for i in ev])
    nc = min(256, Ttr.shape[1] - 1, Ttr.shape[0] - 1)
    svd = TruncatedSVD(n_components=nc, random_state=0).fit(Ttr)
    Xtr, Xev = unit(svd.transform(Ttr)), unit(svd.transform(Tev))
    out = {}
    for level, K in level_k:
        truth = codes(C.labels(level)[ev])
        try:
            out[level] = float(np.mean([nmi(truth, assign(Xev, skmeans(Xtr, K, s))) for s in SEEDS]))
        except Skip as ex:
            out[level] = "SKIPPED (%s)" % ex
    return out


def d2(C, S):
    """Gold geometricity H: ARI (fine-label units) of average-link (cosine) on the gold fine TRAIN centroids cut at K_c, against
    the gold fine -> coarse map; beside it the p95 of size-matched random partitions (permutations of the gold map, D2_REPS)."""
    from scipy.cluster.hierarchy import linkage, fcluster
    kc = II.GOLD_K[C.name][0]
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "D2 gold centroids")
    u, G = centroids_by_label(S.X[tr], C.fine[tr])
    f2c = {}
    for i in tr:
        f2c[C.fine[i]] = C.coarse[i]
    gold = codes([f2c[x] for x in u])
    cut = fcluster(linkage(G, method="average", metric="cosine"), t=kc, criterion="maxclust")
    H = ari(gold, cut)
    rng = np.random.default_rng(SEED_D2 + CORPORA.index(C.name))
    null = [ari(gold, rng.permutation(gold)) for _ in range(D2_REPS)]
    return {"H": H, "p95": float(np.percentile(null, 95)), "n_fine": int(len(u)), "k_c": kc, "clusters": int(len(set(cut)))}


def d3(C, S):
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "D3 centroids")
    ev = S_idx(C, S, SS.EVAL)
    u, G = centroids_by_label(S.X[tr], C.fine[tr])
    pred = u[assign(S.X[ev], G)]
    gold = C.fine[ev]
    f2c = {}
    for i in tr:
        f2c[C.fine[i]] = C.coarse[i]
    off = [(a, b) for a, b in zip(gold, pred) if a != b]
    pairs = {}
    for a, b in off:
        k = tuple(sorted((a, b)))
        pairs[k] = pairs.get(k, 0) + 1
    within = sum(1 for a, b in off if f2c.get(a) == f2c.get(b)) if C.name != "banking77" else None
    return {"n": int(len(ev)), "errors": len(off), "within_share": (within / len(off)) if (off and within is not None) else float("nan"),
            "top20": sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0]))[:20]}


def vmf_post(X, Cm, kappa, logpi):
    L = kappa * (X @ Cm.T) + logpi
    L -= L.max(1, keepdims=True)
    P = np.exp(L)
    return P / P.sum(1, keepdims=True)


def d4(C, S):
    """Soft / hard / selective filing (B6)."""
    kf = II.GOLD_K[C.name][1]
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "D4 P(y|c)")
    Cm = km_fit(C, S, kf, 0, "D4 k-means s0")
    labs = np.unique(C.fine[tr])
    li = {l: j for j, l in enumerate(labs)}
    ctr = assign(S.X[tr], Cm)
    cnt = np.zeros((kf, len(labs)))
    for c, y in zip(ctr, C.fine[tr]):
        cnt[c, li[y]] += 1
    Pyc = (cnt + ALPHA) / (cnt.sum(1, keepdims=True) + ALPHA * len(labs))
    logpi = np.log((np.bincount(ctr, minlength=kf) + ALPHA) / (len(ctr) + ALPHA * kf))
    gate = fit_rows(C, S_idx(C, S, SS.GATE), (SS.GATE,), "D4 kappa")
    gate = np.array([i for i in gate if C.fine[i] in li])
    if len(gate) == 0:
        raise Skip("no GATE row")
    yg = np.array([li[C.fine[i]] for i in gate])
    nll = []
    for k in KAPPA_GRID:
        Py = vmf_post(S.X[gate], Cm, k, logpi) @ Pyc
        nll.append(-float(np.mean(np.log(Py[np.arange(len(gate)), yg]))))
    kappa = float(KAPPA_GRID[int(np.argmin(nll))])
    ev = np.array([i for i in S_idx(C, S, SS.EVAL) if C.fine[i] in li])
    ye = np.array([li[C.fine[i]] for i in ev])
    Py = vmf_post(S.X[ev], Cm, kappa, logpi) @ Pyc
    hard_c = assign(S.X[ev], Cm)
    hard = np.argmax(Pyc[hard_c], axis=1)
    soft = np.argmax(Py, axis=1)
    onehot = np.eye(len(labs))[ye]
    srt = np.sort(Py, axis=1)
    margin = srt[:, -1] - srt[:, -2]
    order = np.argsort(-margin, kind="stable")
    sel = {}
    for cov in (0.8, 0.9, 1.0):
        m = order[:max(1, int(round(cov * len(ev))))]
        sel[cov] = float(np.mean(soft[m] == ye[m]))
    return {"kappa": kappa, "kappa_at_edge": kappa in (KAPPA_GRID[0], KAPPA_GRID[-1]), "n": int(len(ev)),
            "hard_acc": float(np.mean(hard == ye)), "soft_acc": float(np.mean(soft == ye)),
            "brier_soft": float(np.mean(((Py - onehot) ** 2).sum(1))), "brier_hard": float(np.mean(((Pyc[hard_c] - onehot) ** 2).sum(1))),
            "selective": sel, "gain80": sel[0.8] - sel[1.0], "Cm": Cm, "Pyc": Pyc, "logpi": logpi, "labs": labs}


def d5(C, S, pairs, d4r):
    got = [(i, j, t) for i, j, t in pairs if t in S.vecs and S.have[i] and S.have[j]]
    if not got:
        raise Skip("no pair with a vector")
    Cm, Pyc, labs = d4r["Cm"], d4r["Pyc"], d4r["labs"]
    maj = labs[np.argmax(Pyc, axis=1)]
    Xp = S.of([t for _i, _j, t in got])
    top2 = np.argsort(-(Xp @ Cm.T), axis=1)[:, :2]
    both = [set((C.fine[i], C.fine[j])) <= set(maj[top2[r]]) for r, (i, j, _t) in enumerate(got)]
    each = np.mean([(C.fine[i] in set(maj[top2[r]])) + (C.fine[j] in set(maj[top2[r]])) for r, (i, j, _t) in enumerate(got)]) / 2

    def ent(X):
        P = vmf_post(X, Cm, d4r["kappa"], d4r["logpi"])
        return -(P * np.log(np.clip(P, 1e-300, None))).sum(1)
    ev = S_idx(C, S, SS.EVAL)
    return {"n_pairs": len(got), "both_recall": float(np.mean(both)), "per_intent_recall": float(each),
            "entropy_auroc": auroc(ent(Xp), ent(S.X[ev])), "n_single": int(len(ev))}


def d6(C, S):
    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "D6 centroids")
    ev = S_idx(C, S, SS.EVAL)
    u, G = centroids_by_label(S.X[tr], C.fine[tr])
    ok_ = u[assign(S.X[ev], G)] == C.fine[ev]
    ln = np.array([len(C.text[i].split()) for i in ev])
    edges = np.quantile(ln, [0.2, 0.4, 0.6, 0.8])
    q = np.searchsorted(edges, ln, side="right")
    return {"edges": edges.tolist(), "rows": [(int(b), int((q == b).sum()), float(ok_[q == b].mean()) if (q == b).any() else float("nan"))
                                              for b in range(5)]}


def near_copies(C, S512):
    tr, ev = S_idx(C, S512, SS.TRAIN), np.concatenate([S_idx(C, S512, SS.EVAL), S_idx(C, S512, SS.EVAL, oos=True)])
    n = 0
    for s in range(0, len(ev), 1000):
        n += int(((S512.X[ev[s:s + 1000]] @ S512.X[tr].T).max(1) >= NEAR_COS).sum()) if len(tr) else 0
    return {"n_eval": int(len(ev)), "near": n}


# ------------------------------------------------------------------------------------------------ verdicts + printing
def c1_verdicts(c1):
    """-> dict. C1a per corpus (the fail observable's wording; the orchestrator's C-4 ruling), the per-family reading beside (NOT of
    record), C1b, and P2's 'qwen3 BETTER than both'."""
    st = {(c, g, e): c1[(c, g)]["per"][e]["status"] for (c, g) in c1 for e in FAMILIES}
    fine_worse = {e: [c for c in CORPORA if st.get((c, "fine", e)) == "WORSE"] for e in FAMILIES}
    alt = [c for c in CORPORA if any(st.get((c, "fine", e)) == "WORSE" for e in FAMILIES)]
    c1a = "HELD" if len(alt) >= 2 else "FAILED"
    fam = "HELD" if any(len(v) >= 2 for v in fine_worse.values()) else "FAILED"
    coarse_worse = [(c, e) for c in ("massive", "clinc") for e in FAMILIES if st.get((c, "coarse", e)) == "WORSE"]
    c1b = "FIRES" if coarse_worse else "NOT FIRED"
    both = [c for c in CORPORA if all(st.get((c, "fine", e)) == "WORSE" for e in FAMILIES)]
    return {"C1a": c1a, "fine_worse": fine_worse, "C1a_alt": fam, "alt_corpora": alt,
            "C1b": c1b, "coarse_worse": coarse_worse, "qwen3_better_both": both}


R1_SE, R1_SPREAD = 0.020 / 2.8, 0.020          # R-1: nomic's fine line SCOREABLE while SE <= 0.0071 and spread <= 0.020


def r1_lines(c1):
    """R-1: per corpus, nomic's fine C1 line SCOREABLE iff the measured SE <= 0.020 / 2.8 and the measured spread (the bar's,
    max(spread_qwen3, spread_nomic)) <= 0.020; otherwise DESCRIPTIVE-ONLY, printed BESIDE the criterion, which is scored as written."""
    out = {}
    for c in CORPORA:
        r = c1.get((c, "fine"))
        if r is None:
            continue
        se, sp = r["per"]["nomic"]["se"], max(r["spread"]["qwen3"], r["spread"]["nomic"])
        out[c] = ("SCOREABLE" if (se <= R1_SE and sp <= R1_SPREAD) else "DESCRIPTIVE-ONLY", se, sp)
    return out


def verdicts(R):
    V = {}
    V.update(c1_verdicts(R["c1"]))
    V["R1"] = r1_lines(R["c1"])
    V["C2"] = band(R["c2"]["lo"], R["c2"]["hi"], C2_BAR)
    V["C3"], V["C3_pos"], V["C3_nonpos"] = c3_verdict(R["c3"])
    V["C4"] = band(R["c4"]["lo"], R["c4"]["hi"], C4_BAR)
    return V


def criteria_lines(V):
    L = ["== CRITERIA (verdict words; the draft's logic, verbatim) =="]
    fw = V["fine_worse"]
    L.append("S0-C1a (fine dependence): %s -- corpora with a WORSE fine family: %d of 3 %s (nomic %s, gemma %s) (HELD iff >= 2 of 3 "
             "corpora; FAILED iff fewer than 2 corpora with a WORSE fine family: the registered fail observable, the orchestrator's C-4 ruling)"
             % (V["C1a"], len(V["alt_corpora"]), V["alt_corpora"], fw["nomic"], fw["gemma"]))
    for c, (word, se, sp) in sorted(V.get("R1", {}).items()):
        L.append("R-1 %s fine, nomic: %s (measured SE %.5f vs <= %.4f; spread %.5f vs <= %.3f); C1a is scored as written"
                 % (c, word, se, R1_SE, sp, R1_SPREAD))
    L.append("R-4 gemma's fine WORSE clause is DESCRIPTIVE-ONLY at its prediction (-0.010 inside the 0.0112 bar); it is counted in C1a as written")
    L.append("S0-C1a per-family reading (>= 1 family WORSE on >= 2 of 3 corpora; NOT OF RECORD since the C-4 ruling): %s"
             % V["C1a_alt"])
    if V["C1b"] == "NOT FIRED":
        L.append("S0-C1b (coarse): NOT FIRED -- 0 of 2 families WORSE at the coarse level on MASSIVE and on CLINC (a non-fire is never parity)")
    else:
        L.append("S0-C1b (coarse): FIRES -- WORSE at the coarse level: %s" % V["coarse_worse"])
    L.append("S0-C2 (OOS, CLINC): %s (HELD iff lower(A) >= %.2f; FAILED iff upper(A) < %.2f)" % (V["C2"], C2_BAR, C2_BAR))
    L.append("S0-C3 (label-free cell margin vs gold purity): %s -- lower(rho) > 0 on %s; upper(rho) <= 0 on %s (HELD iff >= 2 of 3 "
             "positive; FAILED iff >= 2 of 3 non-positive)" % (V["C3"], V["C3_pos"], V["C3_nonpos"]))
    L.append("S0-C4 (slot-swap stability, MASSIVE): %s (HELD iff lower(S) >= %.2f; FAILED iff upper(S) < %.2f)" % (V["C4"], C4_BAR, C4_BAR))
    L.append("== FALSIFIERS ==")
    fal = (("F1", V["C1a"] == "FAILED", "C1a FAILED: E0b's 'the fine structure is embedder-dependent' is not reproduced against a "
                                        "known answer on 2 of 3 corpora; that clause narrows to MMLU-Pro and one draw"),
           ("F1'", V["C1b"] == "FIRES", "C1b FIRES: the coarse 'not shown worse' of E0b does not generalise"),
           ("F2", V["C2"] == "FAILED", "C2 FAILED: label-free no-match is not an out-of-scope detector on the canonical known-answer "
                                       "corpus; stage 3 is declined and the framework may not describe no-match as scope detection"),
           ("F3", V["C3"] == "FAILED", "C3 FAILED: a label-free margin carries no sign of a flat cell's meaning; label-free cells get "
                                       "no self-diagnostic, and S1 (declared cells) is strengthened"),
           ("F4", V["C4"] == "FAILED", "C4 FAILED: flat cells are not stable addresses under slot swaps on the easiest known answer; "
                                       "every filing rate of record (81.6%) must carry 'surface-sensitive, untested on capability text'"))
    for fid, fired, text in fal:
        L.append("%s: %s -- %s" % (fid, "FIRED" if bool(fired) else "NOT FIRED", text))
    return L


def _hit(v, lo, hi):
    """A numeric prediction HELD iff the observed point lies in its 80% interval (registration, PREDICTIONS)."""
    return "HELD" if (isinstance(v, float) and np.isfinite(v) and lo <= v <= hi) else "FAILED"


def predictions_lines(R, V):
    L = ["== PREDICTIONS (a numeric prediction HELD iff the point lies in its 80% interval; a probability scored on its event, Brier beside) =="]
    briers = []

    def prob(name, p, outcome):
        b = (p - (1.0 if outcome else 0.0)) ** 2
        briers.append(b)
        L.append("  %s: predicted p %.2f, outcome %s, Brier %.4f" % (name, p, "YES" if outcome else "NO", b))
    for (c, g), (pt, lo, hi) in P1.items():
        if (c, g) in R["c1"]:
            v = float(np.mean(R["c1"][(c, g)]["nmi"]["qwen3"]))
            L.append("  P1 %s %s NMI (qwen3 256, seed mean) %.4f vs %.2f [%.2f, %.2f]: %s" % (c, g, v, pt, lo, hi, _hit(v, lo, hi)))
        else:
            L.append("  P1 %s %s: SKIPPED (not computed)" % (c, g))
    for c in CORPORA:
        if (c, "fine") in R["c1"]:
            for e, (pt, lo, hi) in (("nomic", P2_NOMIC[c]), ("gemma", P2_GEMMA)):
                v = R["c1"][(c, "fine")]["per"][e]["D"]
                L.append("  P2 %s fine D(%s) %+.4f vs %+.3f [%+.3f, %+.3f]: %s" % (c, e, v, pt, lo, hi, _hit(v, lo, hi)))
    prob("P2 C1a HELD", P2_PROB["C1a HELD"], V["C1a"] == "HELD")
    prob("P2 C1b NOT FIRED", P2_PROB["C1b NOT FIRED"], V["C1b"] == "NOT FIRED")
    prob("P2 qwen3 BETTER than both at fine on >= 2 of 3 (B8)", P2_PROB["qwen3 BETTER than both at fine on >= 2 of 3"],
         len(V["qwen3_better_both"]) >= 2)
    c2r = R["c2"]
    L.append("  P3 A %.4f vs %.2f [%.2f, %.2f]: %s" % (c2r["A"], P3["A"][0], P3["A"][1], P3["A"][2], _hit(c2r["A"], P3["A"][1], P3["A"][2])))
    L.append("  P3 FPR95 %.4f vs %.2f [%.2f, %.2f]: %s" % (c2r["fpr95"], P3["FPR95"][0], P3["FPR95"][1], P3["FPR95"][2],
                                                            _hit(c2r["fpr95"], P3["FPR95"][1], P3["FPR95"][2])))
    L.append("  P3 supervised-centroid A %.4f (predicted %.2f, a point; printed)" % (c2r["supervised_A"], P3["supervised A (point)"]))
    prob("P3 C2 HELD", P3["HELD"], V["C2"] == "HELD")
    for c in CORPORA:
        pt, lo, hi = P4[c]
        v = R["c3"][c]["rho"] if c in R["c3"] else float("nan")
        L.append("  P4 %s rho %.4f vs %.2f [%.2f, %.2f]: %s" % (c, v, pt, lo, hi, _hit(v, lo, hi)))
    prob("P4 C3 HELD", P4["HELD"], V["C3"] == "HELD")
    c4r = R["c4"]
    L.append("  P5 S %.4f vs %.2f [%.2f, %.2f]: %s" % (c4r["S"], P5["S"][0], P5["S"][1], P5["S"][2], _hit(c4r["S"], P5["S"][1], P5["S"][2])))
    prob("P5 C4 HELD", P5["HELD"], V["C4"] == "HELD")
    prob("P5 kNN-1 label stability < supervised-centroid stability", P5["kNN-1 < centroid"], c4r["knn1_stab"] < c4r["centroid_stab"])
    for c, key in (("massive", "D2 massive"), ("clinc", "D2 clinc")):
        pt, lo, hi = P6[key]
        d = R["d2"].get(c)
        if d is None:
            L.append("  P6 D2 %s: SKIPPED" % c)
            continue
        held = bool(lo <= d["H"] <= hi and d["H"] > d["p95"])
        L.append("  P6 D2 H(%s) %.4f vs %.2f [%.2f, %.2f], random p95 %.4f: %s" % (c, d["H"], pt, lo, hi, d["p95"], "HELD" if held else "FAILED"))
    share = R["d3"]["massive"]["within_share"]
    L.append("  P6 D3 within-scenario share of MASSIVE confusion %.4f (>= %.2f): %s" % (share, P6["D3 share"],
                                                                                        "HELD" if bool(share >= P6["D3 share"]) else "FAILED"))
    g = R["d4"]["massive"]["gain80"]
    L.append("  P6 D4 selective filing at 80%% coverage vs 100%% on MASSIVE %+.4f (>= +%.2f): %s" % (g, P6["D4 gain"],
                                                                                                   "HELD" if bool(g >= P6["D4 gain"]) else "FAILED"))
    L.append("  mean Brier over the %d probability predictions: %.4f" % (len(briers), float(np.mean(briers))))
    return L


def support_lines(CS, R=None):
    """The measured support beside the deciding statistic: denominators, clusters, Kish DEFF (sum m^2 / sum m), n_eff, SE, MDE80."""
    L = ["== SUPPORT (planning values of the draft beside the measured ones) =="]
    for c in CORPORA:
        C = CS[c]
        ev = C.idx(SS.EVAL)
        k = kish(C.comp[ev]) if len(ev) else float("nan")
        L.append("  C1 %s: EVAL in-scope n %d (planned %d), components %d, Kish DEFF %.4f (declared 1.05), n_eff %.0f"
                 % (c, len(ev), PLANNED[c], len(np.unique(C.comp[ev])) if len(ev) else 0, k, len(ev) / k if len(ev) else 0))
    oo = CS["clinc"].idx(SS.EVAL, oos=True)
    hs = {sd: int((CS["clinc"].hash_side[oo] == sd).sum()) for sd in (SS.EVAL, SS.GATE, SS.TRAIN)}
    L.append("  C2: OOS EVAL n %d (planned %d), components %d, Kish DEFF %.4f; in-scope as C1 clinc; R-2: EVERY kept CLINC OOS row "
             "(hash sides %s, all read as EVAL; %d OOS rows dropped by a collision)"
             % (len(oo), PLANNED["clinc_oos"], len(np.unique(CS["clinc"].comp[oo])) if len(oo) else 0,
                kish(CS["clinc"].comp[oo]) if len(oo) else float("nan"), json.dumps(hs, sort_keys=True),
                int((CS["clinc"].oos & ~CS["clinc"].kept).sum())))
    for c in CORPORA:
        K = II.GOLD_K[c][1]
        L.append("  C3 %s: K_f %d cells (unit = cell; SE_z 1/sqrt(K-3) = %.3f, rho-MDE80 ~ %.2f)" % (c, K, 1 / np.sqrt(K - 3), 2.8 / np.sqrt(K - 3)))
    if R is None:
        return L
    for (c, g), r in sorted(R["c1"].items()):
        for e in FAMILIES:
            p = r["per"][e]
            L.append("  C1 %s %s %s: n %d, clusters %d, DEFF %.4f, n_eff %.0f; bootstrap SE(D) %.5f (planned 0.004), MDE80 %.5f "
                     "(planned 0.0112), spread %.5f (planned 0.010), bar %.5f" % (c, g, e, r["n"], r["components"], r["kish"],
                                                                                 r["n"] / r["kish"], p["se"], p["mde80"],
                                                                                 max(r["spread"]["qwen3"], r["spread"][e]), p["bar"]))
    c2r = R["c2"]
    hm = c2r["hm_se"] * np.sqrt(c2r["deff"])
    L.append("  C2: n_in %d, n_OOS %d, DEFF %.4f; Hanley-McNeil SE (A, n_pos in-scope, n_neg OOS; C-7) %.5f x sqrt(DEFF) = %.5f, "
             "MDE80 %.5f; the registered order (counts swapped, conservative) %.5f x sqrt(DEFF) = %.5f (registered 0.0059, MDE80 0.017); "
             "bootstrap SE %.5f (the stratified bootstrap decides)"
             % (c2r["n_in"], c2r["n_oos"], c2r["deff"], c2r["hm_se"], hm, 2.8 * hm, c2r["hm_se_swapped"],
                c2r["hm_se_swapped"] * np.sqrt(c2r["deff"]), c2r["se_boot"]))
    for c in CORPORA:
        r = R["c3"].get(c)
        if r:
            L.append("  C3 %s: cells scored %d (excluded < %d EVAL: %d), SE_z %.4f, bootstrap draws undefined %d"
                     % (c, r["n_cells"], C3_MIN_EVAL, r["n_excluded"], r["se_z"], r["nan_draws"]))
    c4r = R["c4"]
    L.append("  C4: n %d variants, clusters %d, DEFF %.4f, n_eff %.0f, bootstrap SE %.5f (planned 0.0053), MDE80 %.5f (planned 0.015)"
             % (c4r["n"], c4r["components"], c4r["kish"], c4r["n"] / c4r["kish"], c4r["se_boot"], 2.8 * c4r["se_boot"]))
    return L


def census_check(CS, bracket):
    got = {"massive": len(CS["massive"].idx(SS.EVAL)), "clinc": len(CS["clinc"].idx(SS.EVAL)),
           "clinc_oos": len(CS["clinc"].idx(SS.EVAL, oos=True)), "banking77": len(CS["banking77"].idx(SS.EVAL))}
    off = {k: (got[k], PLANNED[k]) for k in PLANNED if abs(got[k] - PLANNED[k]) > CENSUS_TOL * PLANNED[k]}
    line = "CENSUS: EVAL %s vs planned %s: %s" % (json.dumps(got, sort_keys=True), json.dumps(PLANNED, sort_keys=True),
                                                  "WITHIN 5%" if not off else "OUTSIDE 5%% on %s" % off)
    if off and bracket:
        line += "; re-stated by the registrar's bracket: %s" % bracket
    return line, off


# ------------------------------------------------------------------------------------------------ run
def run_all(CS, vecs, derived, pilot):
    """Every readout. A Skip is a PILOT's 'SKIPPED' line and a --run's refusal."""
    del FIT_LOG[:]
    R = {"c1": {}, "c1_512": {}, "c3": {}, "d1": {}, "d2": {}, "d3": {}, "d4": {}, "d5": {}, "d6": {}, "near": {}, "tfidf": {},
         "skipped": []}

    def guard(name, fn):
        try:
            return fn()
        except Skip as ex:
            if not pilot:
                refuse("readout %s cannot run on the rows present (%s)" % (name, ex))
            R["skipped"].append("%s: SKIPPED (%s)" % (name, ex))
            return None
        except (ValueError, IndexError, ZeroDivisionError) as ex:     # a pilot's partial rows only; a --run propagates
            if not pilot:
                raise
            R["skipped"].append("%s: SKIPPED (%s: %s)" % (name, type(ex).__name__, str(ex)[:120]))
            return None
    sp = {c: {e: Space(vecs[e], CS[c], SLICE) for e in EMBEDDERS} for c in CORPORA}
    sp512 = {c: {e: Space(vecs[e], CS[c], SLICE2) for e in EMBEDDERS} for c in CORPORA}
    for c in CORPORA:
        kc, kf = II.GOLD_K[c]
        for g in LEVELS[c]:
            k = kf if g == "fine" else kc
            seed = BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index(g)
            r = guard("C1 %s %s" % (c, g), lambda: c1_level(CS[c], sp[c], g, k, seed))
            if r is not None:
                R["c1"][(c, g)] = r
            r = guard("C1-512 %s %s" % (c, g), lambda: c1_level(CS[c], sp512[c], g, k, seed))
            if r is not None:
                R["c1_512"][(c, g)] = r
        r = guard("C3 %s" % c, lambda: c3(CS[c], sp[c]))
        if r is not None:
            R["c3"][c] = r
        lk = [(g, (kf if g == "fine" else kc)) for g in LEVELS[c]]
        r = guard("D1 %s" % c, lambda: d1(CS[c], sp[c], lk))
        if r is not None:
            R["d1"][c] = r
        r = guard("TF-IDF %s" % c, lambda: tfidf_floor(CS[c], lk))
        if r is not None:
            R["tfidf"][c] = r
        if kc is not None:
            r = guard("D2 %s" % c, lambda: {e: d2(CS[c], sp[c][e]) for e in EMBEDDERS})
            if r is not None:
                R["d2"][c] = r["qwen3"]
                R["d2_all"] = R.get("d2_all", {})
                R["d2_all"][c] = r
        r = guard("D3 %s" % c, lambda: d3(CS[c], sp[c]["qwen3"]))
        if r is not None:
            R["d3"][c] = r
        r = guard("D4 %s" % c, lambda: d4(CS[c], sp[c]["qwen3"]))
        if r is not None:
            R["d4"][c] = r
            if c in N_PAIRS:
                r5 = guard("D5 %s" % c, lambda: d5(CS[c], sp[c]["qwen3"], derived["pairs"][c], R["d4"][c]))
                if r5 is not None:
                    R["d5"][c] = r5
        r = guard("D6 %s" % c, lambda: d6(CS[c], sp[c]["qwen3"]))
        if r is not None:
            R["d6"][c] = r
        R["near"][c] = near_copies(CS[c], sp512[c]["qwen3"])
    R["c2"] = guard("C2", lambda: c2(CS["clinc"], sp["clinc"]))
    R["c4"] = guard("C4", lambda: c4(CS["massive"], sp["massive"], derived["variants"]))
    R["variant_counts"] = derived["variant_counts"]
    R["c4_swaps"] = c4_swap_summary(CS["massive"], derived["variants"])
    R["c4_variant_rows"] = [(CS["massive"].ids[i], len(parse_annot(CS["massive"].annot[i])), len(ch), "|".join(ch))
                            for i, _t, ch in derived["variants"]]
    R["fit_audit"] = fit_audit()
    return R


def _f(x, fmt="%.4f"):
    return fmt % x if isinstance(x, (float, int, np.floating)) and np.isfinite(x) else str(x)


def readout_lines(R):
    L = ["== S0-C1 (k-means NMI against gold, EVAL; slice 256 decides, 512 printed) =="]
    for (c, g), r in sorted(R["c1"].items()):
        L.append("  %s %s K=%d n=%d: NMI seed-mean qwen3 %.4f nomic %.4f gemma %.4f; ARI seed-mean qwen3 %.4f nomic %.4f gemma %.4f"
                 % (c, g, r["k"], r["n"], np.mean(r["nmi"]["qwen3"]), np.mean(r["nmi"]["nomic"]), np.mean(r["nmi"]["gemma"]),
                    np.mean(r["ari"]["qwen3"]), np.mean(r["ari"]["nomic"]), np.mean(r["ari"]["gemma"])))
        for e in FAMILIES:
            p = r["per"][e]
            L.append("    D(%s, %s) = %+.5f, 95%% BASIC CI [%+.5f, %+.5f] (decides, C-1); bias b = %+.5f (b/SE %+.2f), bias-corrected "
                     "D - b = %+.5f; percentile CI [%+.5f, %+.5f] (descriptive); SE %.5f, MDE80 %.5f, spread max(qwen3 %.5f, %s %.5f), "
                     "per-seed-D spread %.5f, bar %.5f -> %s"
                     % (e, g, p["D"], p["lo"], p["hi"], p["bias"], p["bias"] / p["se"] if p["se"] > 0 else float("nan"), p["dbc"],
                        p["plo"], p["phi"], p["se"], p["mde80"], r["spread"]["qwen3"], e, r["spread"][e], p["spread_seedD"], p["bar"],
                        p["status"]))
    for (c, g), r in sorted(R["c1_512"].items()):
        L.append("  [512] %s %s: D(nomic) %+.5f basic [%+.5f, %+.5f]; D(gemma) %+.5f basic [%+.5f, %+.5f] (printed, not deciding)"
                 % (c, g, r["per"]["nomic"]["D"], r["per"]["nomic"]["lo"], r["per"]["nomic"]["hi"], r["per"]["gemma"]["D"],
                    r["per"]["gemma"]["lo"], r["per"]["gemma"]["hi"]))
    c2r = R["c2"]
    L.append("== S0-C2 (CLINC OOS; qwen3 256, K 150, seed 0 decides) ==")
    L.append("  A = %.5f, 95%% CI [%.5f, %.5f] (stratified component bootstrap, B %d); n_in %d, n_OOS %d; FPR95 %.4f at the GATE "
             "threshold %.5f (GATE TPR %.4f, n_GATE %d; EVAL TPR %.4f)" % (c2r["A"], c2r["lo"], c2r["hi"], BOOT_B, c2r["n_in"], c2r["n_oos"],
                                                                           c2r["fpr95"], c2r["thr"], c2r["tpr_gate"], c2r["n_gate"], c2r["tpr_eval"]))
    L.append("  per seed A: %s; supervised TRAIN-centroid A %.5f; K 50 / 100 / 300 (seed 0): %s; nomic %.5f, gemma %.5f (K 150 seed 0)"
             % ([round(a, 5) for a in c2r["per_seed"]], c2r["supervised_A"], {k: (_f(v, "%.5f")) for k, v in c2r["K_alt"].items()},
                c2r["other_emb"]["nomic"], c2r["other_emb"]["gemma"]))
    L.append("== S0-C3 (Spearman rho of the TRAIN margin vs EVAL purity over cells; qwen3 256 seed 0; cell bootstrap B %d) ==" % BOOT_B)
    for c in CORPORA:
        r = R["c3"].get(c)
        if r is None:
            L.append("  %s: SKIPPED" % c)
            continue
        L.append("  %s: rho %s, 95%% CI [%s, %s], cells %d (excluded < %d EVAL: %d); seeds 1-4: %s"
                 % (c, _f(r["rho"]), _f(r["lo"]), _f(r["hi"]), r["n_cells"], C3_MIN_EVAL, r["n_excluded"],
                    [_f(r["per_seed"][s]) for s in SEEDS[1:]]))
    c4r = R["c4"]
    vc = R["variant_counts"]
    L.append("== S0-C4 (MASSIVE slot swap; qwen3 256, K 60, seed 0 decides) ==")
    L.append("  S = %.5f, 95%% CI [%.5f, %.5f], n %d variants (EVAL items %d, with a slot %d; excluded: no alternative %d, TRAIN "
             "collision %d, unchanged %d; annot/text mismatch %d)" % (c4r["S"], c4r["lo"], c4r["hi"], c4r["n"], vc["eval_items"],
                                                                      vc["with_slot"], vc["no_alternative"], vc["train_collision"],
                                                                      vc["unchanged"], vc["annot_text_mismatch"]))
    if "c4_swaps" in R:
        L.append("  B7 swapped slots (every swappable slot, the design's reading): per variant 'swapped of slots' %s; slot types swapped %s"
                 % (json.dumps(R["c4_swaps"][0], sort_keys=True), R["c4_swaps"][1][:30]))
    L.append("  beside: supervised-centroid label stability %.5f; kNN-1 label stability %.5f; random same-intent co-filing %s (%d pairs); "
             "seeds 1-4 S %s" % (c4r["centroid_stab"], c4r["knn1_stab"], _f(c4r["cofile"]), c4r["cofile_n"],
                                 [round(c4r["per_seed"][s], 5) for s in SEEDS[1:]]))
    L.append("== DESCRIPTIVE (never scored; each with n) ==")
    for c in CORPORA:
        for (e, g), r in sorted(R["d1"].get(c, {}).items()):
            L.append("  D1 %s %s %s n %d: centroid acc %.4f, kNN-15 acc %.4f; k-means NMI/ARI at 0.5x/1x/2x: %s"
                     % (c, e, g, r["n"], r["centroid_acc"], r["knn15_acc"],
                        {m: (kk, _f(a), _f(b)) for m, (kk, a, b) in r["curve"].items()}))
        if c in R["tfidf"]:
            L.append("  D1 %s TF-IDF -> SVD-256 floor, k-means NMI seed-mean: %s" % (c, {g: _f(v) for g, v in R["tfidf"][c].items()}))
    for c, per in sorted(R.get("d2_all", {}).items()):
        for e, r in per.items():
            L.append("  D2 %s %s: H %.4f (average-link on %d gold fine centroids cut at K_c %d, %d clusters), random p95 %.4f (%d reps)"
                     % (c, e, r["H"], r["n_fine"], r["k_c"], r["clusters"], r["p95"], D2_REPS))
    for c, r in sorted(R["d3"].items()):
        L.append("  D3 %s: n %d, errors %d, within-coarse share %s; top-20 confusable pairs %s"
                 % (c, r["n"], r["errors"], _f(r["within_share"]), [("%s|%s" % k, v) for k, v in r["top20"]]))
    for c, r in sorted(R["d4"].items()):
        L.append("  D4 %s n %d: kappa %.3f%s; hard acc %.4f, soft acc %.4f; Brier soft %.4f, hard %.4f; selective precision at "
                 "80%% / 90%% / 100%% coverage %.4f / %.4f / %.4f" % (c, r["n"], r["kappa"], " (AT THE GRID EDGE)" if r["kappa_at_edge"] else "",
                                                                     r["hard_acc"], r["soft_acc"], r["brier_soft"], r["brier_hard"],
                                                                     r["selective"][0.8], r["selective"][0.9], r["selective"][1.0]))
    for c, r in sorted(R["d5"].items()):
        L.append("  D5 %s: %d synthetic pairs (seeded concatenation, not natural text): both-intent top-2 recall %.4f, per-intent %.4f; "
                 "entropy AUROC pair vs %d singles %.4f" % (c, r["n_pairs"], r["both_recall"], r["per_intent_recall"], r["n_single"], r["entropy_auroc"]))
    for c, r in sorted(R["d6"].items()):
        L.append("  D6 %s: token-length quintile edges %s; (quintile, n, centroid acc) %s" % (c, r["edges"], [(q, n, _f(a)) for q, n, a in r["rows"]]))
    L.append("  D7 HWU64 <-> MASSIVE-en twin count: NOT RUN (R-3: conditional on an author admission of HWU64; the steward's, "
             "never computed here)")
    for c, r in sorted(R["near"].items()):
        L.append("  near-copies %s: %d of %d EVAL items have a TRAIN neighbour at cos >= %.2f (qwen3 512); disclosed, not removed"
                 % (c, r["near"], r["n_eval"], NEAR_COS))
    for s in R["skipped"]:
        L.append("  " + s)
    return L


def header_lines(CS, pins_state, census_line, pilot=False):
    L = ["INTENT-TRANSFER-S0 outcome (tools/analysis/intent_transfer_s0.py, blob %s)" % blob_lf(os.path.abspath(__file__))]
    if pilot:
        L.append("PILOT: NOT OF RECORD (a smoke readout on the rows embedded so far; discarded)")
    L += [
         "pool of record: none read (the study's own DBs only)", "zero judge calls; no construction", census_line]
    L += ["pins: %s" % pins_state]
    L += ["registration: docs/judge_v2_program.md \"## Registered 2026-09-29 (before any code or call) — INTENT-TRANSFER-S0: ...\" "
          "L22092-L22134 _as_of 44ab46f; kind zero-call (R-5)",
          "builder's readings B1-B8 (printed for the registrar; see the script's docstring): B1 C1 spread = max(spread_qwen3, "
          "spread_e); B2 C1a per family; B3 C2 / C4 qwen3 256 seed 0; B4 C2 bootstrap stratified; B5 D5 500 MASSIVE + 500 CLINC; "
          "B6 D4 ALPHA 0.1, TRAIN cell prior, kappa grid 1..1000 x 61; B7 every swappable slot swapped; B8 'qwen3 BETTER than "
          "both' = both families WORSE"]
    L += ["ATTRIBUTION: " + II.ATTRIBUTION[c] for c in CORPORA]
    return L


def raw_pin_check(db, strict):
    """C-8: the ingest DB's provenance sha256 per raw file against pins["raw"]; a different pin REFUSES; strict (--run): a null or
    absent pin REFUSES too."""
    pins = II.load_pins(PINS_FILE_OVERRIDE[0])
    con = II.open_db_ro(db)
    try:
        prov = con.execute("SELECT name, sha256 FROM provenance ORDER BY name").fetchall()
    finally:
        con.close()
    raw = pins.get("raw") or {}
    for name, sha in prov:
        want = raw.get(name)
        print("%s raw provenance %s: sha256 %s [%s]" % (TAG, name, sha, "UNPINNED" if not want else ("PIN OK" if want == sha else "PIN MISMATCH")))
        if want and want != sha:
            refuse("raw %s: the ingest DB's provenance sha256 %s != the pinned %s" % (name, sha, want))
        if strict and not want:
            refuse("raw %s is UNPINNED: --run reads only an ingest built from pinned raw files" % name)
    return len(prov)


def main_run(pilot, bracket, db, emb_dir, out_dir):
    strict = not pilot
    sha0 = {"ingest_db": pin_check(db, "ingest_db", strict)}
    raw_pin_check(db, strict)
    for e in EMBEDDERS:
        sha0[e] = pin_check(emb_path(e, emb_dir), "emb", strict, sub=e, label="intent_emb_%s.db" % e)
    CS = load_corpora(db)
    texts, set_sha, derived = text_set(CS)
    census_line, off = census_check(CS, bracket)
    print("%s %s" % (TAG, census_line))
    if off and not bracket and not pilot:
        refuse("the census is outside 5%% of the planning counts (%s): re-stated by the registrar's bracket before any read "
               "(--census-bracket)" % off)
    vecs = {}
    for e in EMBEDDERS:
        p = emb_path(e, emb_dir)
        check_meta(p, expected_meta(e, set_sha, len(texts), sha0["ingest_db"]))
        vecs[e] = load_vectors(p, e, texts, allow_missing=pilot)
    R = run_all(CS, vecs, derived, pilot)
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else emb_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))
    pins_state = "re-checked before and after, unchanged: %s" % {k: v[:16] for k, v in sha0.items()}
    L = header_lines(CS, pins_state, census_line, pilot) + support_lines(CS, None if (R["c2"] is None or R["c4"] is None) else R)
    L.append(R["fit_audit"])
    if R["c2"] is None or R["c4"] is None or len(R["c1"]) < 5 or len(R["c3"]) < 3 or "massive" not in R["d3"] or "massive" not in R["d4"]:
        L.append("PILOT: a deciding readout was SKIPPED on the pilot's rows; no verdict is printed")
        L += [s for s in R["skipped"]]
        V = None
    else:
        V = verdicts(R)
        L += readout_lines(R) + criteria_lines(V) + predictions_lines(R, V)
    L.append("DOES NOT SHOW: the construction (no build); capability, judges, routing gain or any policy; that a gold coarse level "
             "is the right taxonomy; transfer to benchmark questions; embedder parity (no TOST); a second split draw; natural "
             "multi-intent text (D5 is synthetic); OOS on real traffic; any card-conformant protocol (RAW only)")
    for ln in L:
        print(ln)
    os.makedirs(out_dir, exist_ok=True)
    sfx = "_PILOT" if pilot else ""
    mode = "w" if pilot else "x"
    path = os.path.join(out_dir, OUTCOME.replace(".txt", sfx + ".txt"))
    if not pilot and os.path.lexists(path):
        refuse("%s exists: the outcome of record is write-once" % path)
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    write_csvs(R, out_dir, sfx, mode)
    print("%s wrote %s (%s)" % (TAG, path, "PILOT, not of record" if pilot else "write-once, of record"))
    return R, V, path


def write_csvs(R, out_dir, sfx, mode):
    with open(os.path.join(out_dir, "s0_c1%s.csv" % sfx), mode, encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["corpus", "level", "slice", "embedder", "seed", "nmi", "ari"])
        for sl, tab in ((SLICE, R["c1"]), (SLICE2, R["c1_512"])):
            for (c, g), r in sorted(tab.items()):
                for e in EMBEDDERS:
                    for s, (a, b) in enumerate(zip(r["nmi"][e], r["ari"][e])):
                        w.writerow([c, g, sl, e, s, "%.6f" % a, "%.6f" % b])
    with open(os.path.join(out_dir, "s0_c3_cells%s.csv" % sfx), mode, encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["corpus", "cell", "n_train", "n_eval", "margin", "purity"])
        for c, r in sorted(R["c3"].items()):
            for x in r["cells"]:
                w.writerow([c, x["cell"], x["n_train"], x["n_eval"], "%.6f" % x["margin"], "%.6f" % x["purity"]])
    with open(os.path.join(out_dir, "s0_c4_variants%s.csv" % sfx), mode, encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "n_slots", "n_swapped", "swapped_slot_types"])     # ids and slot TYPES only, never text
        for row in R.get("c4_variant_rows", []):
            w.writerow(list(row))


# ------------------------------------------------------------------------------------------------ dry run
def dry_run(db, emb_dir, embed_fn=None, skip_transport=False, probe_n=PROBE_N):
    embed_fn = embed_fn or EA.ollama_embed
    print("%s pool of record: none read (the study's own DBs only); zero judge calls" % TAG)
    ingest_sha = pin_check(db, "ingest_db", strict=False)
    CS = load_corpora(db)
    texts, set_sha, derived = text_set(CS)
    line, off = census_check(CS, None)
    print("%s %s" % (TAG, line))
    for c in CORPORA:
        C = CS[c]
        print("%s DENOMINATORS %s: EVAL %d / GATE %d / TRAIN %d in-scope kept; OOS EVAL %d; dropped %d; components %d"
              % (TAG, c, len(C.idx(SS.EVAL)), len(C.idx(SS.GATE)), len(C.idx(SS.TRAIN)), len(C.idx(SS.EVAL, oos=True)),
                 int((~C.kept).sum()), len(np.unique(C.comp))))
    for ln in support_lines(CS):
        print("%s %s" % (TAG, ln))
    vc = derived["variant_counts"]
    print("%s DERIVED: C4 variants %d (%s); D5 pairs %s; text set %d texts, sha256 %s"
          % (TAG, vc["variants"], json.dumps(vc, sort_keys=True), {c: len(v) for c, v in derived["pairs"].items()}, len(texts), set_sha))
    todo = {}
    for e in EMBEDDERS:
        p = emb_path(e, emb_dir)
        if os.path.exists(p):
            check_meta(p, expected_meta(e, set_sha, len(texts), ingest_sha))
            have = present_texts(p)
            todo[e] = sum(1 for t in texts if t not in have)
            print("%s EMB %s: %s present, %d of %d texts missing" % (TAG, e, p, todo[e], len(texts)))
        else:
            todo[e] = len(texts)
            print("%s EMB %s: %s absent; %d texts to embed" % (TAG, e, p, len(texts)))
    heavy = _foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    print("%s Ollama endpoint %s (resolved from OLLAMA_HOST=%r by embedder_arms.client_base)" % (TAG, EA.OLLAMA_URL, os.environ.get("OLLAMA_HOST")))
    if skip_transport:
        print("%s TRANSPORT PREFLIGHT NOT RUN (--skip-transport): this dry-run does NOT clear the transport precondition" % TAG)
    else:
        total_min = 0.0
        for e in EMBEDDERS:
            route_parity(e, embed_fn)
            rate = timed_probe(e, texts, embed_fn, n=probe_n, n_total=todo[e])
            total_min += todo[e] / rate / 60.0
        print("%s PRICE total: %.1f min of Ollama embedding, serial, one heavy process (estimate from the timed probes)" % (TAG, total_min))
        print("%s TRANSPORT PREFLIGHT PASSED (3 of 3 embedders)" % TAG)
    print("%s dry: nothing written" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest
SELFTEST_K = {"massive": (4, 16), "clinc": (4, 16), "banking77": (None, 16)}
ST_PER_FINE = 48


@contextlib.contextmanager
def fixture_scope():
    """The selftest's fixture corpora have K 4 / 16 (the registered K would need ~20k synthetic texts); every other constant is
    the registered one. Restored on exit."""
    saved = (dict(II.GOLD_K), dict(PLANNED))
    II.GOLD_K.clear()
    II.GOLD_K.update(SELFTEST_K)
    try:
        yield
    finally:
        II.GOLD_K.clear()
        II.GOLD_K.update(saved[0])
        PLANNED.clear()
        PLANNED.update(saved[1])


def _fixture_rows():
    """Synthetic corpora (synthetic tokens, never corpus text). Fine intents come in pairs within each coarse label: even pair
    members are well separated, odd pairs are near-duplicates (so a k-means cell may split them: low margin, low purity)."""
    rows = []
    rng = np.random.default_rng(7)
    for c in CORPORA:
        kc, kf = SELFTEST_K[c]
        for f in range(kf):
            co = "c%d" % (f % 4) if kc else None
            for j in range(ST_PER_FINE if f != kf - 1 else 20):      # the last intent is small: its cell has < 10 EVAL items
                val = "v%d_%d" % (f, int(rng.integers(4)))            # slot values are intent-specific
                if c == "massive" and j % 5 == 0:                     # no slot at all
                    annot, text = "%s f%02d plain %d" % (c, f, j), "%s f%02d plain %d" % (c, f, j)
                elif c == "massive":                                  # siblings j // 2 share the carrier: a swap can hit a TRAIN text
                    annot = "%s f%02d item %d [slot_%d : %s] please" % (c, f, j // 2, f % 3, val)
                    text = "%s f%02d item %d %s please" % (c, f, j // 2, val)
                else:
                    annot, text = None, "%s f%02d item %d" % (c, f, j)
                rows.append(dict(corpus=c, orig_split="train", orig_idx="%d_%d" % (f, j), text=text, coarse=co, fine="%s_f%02d" % (c, f),
                                 is_oos=0, annot=annot))
        if c == "clinc":
            for j in range(90):
                rows.append(dict(corpus=c, orig_split="oos_test", orig_idx=str(j), text="clinc oos %d" % j, coarse="oos", fine="oos",
                                 is_oos=1, annot=None))
            rows.append(dict(corpus=c, orig_split="oos_test", orig_idx="coll", text="CLINC f03 item 7", coarse="oos", fine="oos",
                             is_oos=1, annot=None))                   # collides with an in-scope row: the component is dropped
            rows.append(dict(corpus=c, orig_split="train", orig_idx="xl", text="clinc f05 item 9", coarse="c2", fine="clinc_f06",
                             is_oos=0, annot=None))                   # a cross-label duplicate: dropped
    return II.assign(rows)


def _planted(C_of_text, dim, family):
    """text -> vector (first 64 dims; the rest 0.01 noise). Fine intents sit on orthogonal axes E[f] (x 3.0) plus a shared coarse
    axis E[20 + f % 4] (x 1.0). Clouds of the even intents f < 8 are LOOSE (sigma 0.35) and ABSORB 35% of their odd partner's items
    (the cloud choice is hashed from the text alone, so it is the same for every embedder): loose cells are impure and have a low
    margin (C3's planted positive answer); every other cloud is tight (sigma 0.05). nomic: the fine axes REMOVED (coarse x 3.0 +
    noise), so its fine NMI collapses and its coarse survives (C1a's planted answer). OOS: an in-scope-like point at a random noise
    level (C2 about 0.9)."""
    out = {}
    E = np.eye(64)
    for t, (c, f, kind) in sorted(C_of_text.items()):
        r = np.random.default_rng(int(hashlib.sha256((family + t).encode()).hexdigest()[:8], 16))
        rc = np.random.default_rng(int(hashlib.sha256(("cloud" + t).encode()).hexdigest()[:8], 16))
        v = np.zeros(dim)
        if kind == "oos":
            ff = int(rc.integers(16))
            v[:64] = 1.0 * E[20 + ff % 4] + 3.0 * E[ff] + rc.uniform(0.2, 1.5) * r.normal(size=64)
        else:
            cloud = f - 1 if (f % 2 == 1 and f < 8 and rc.random() < 0.35) else f
            sig = 0.35 if (cloud % 2 == 0 and cloud < 8) else 0.05
            if family == "nomic":
                v[:64] = 3.0 * E[20 + f % 4] + 0.35 * r.normal(size=64)
            else:
                v[:64] = 1.0 * E[20 + f % 4] + 3.0 * E[cloud] + sig * r.normal(size=64)
        v[64:] = 0.01 * r.normal(size=dim - 64)
        out[t] = v
    return out


def build_fixture(td):
    """Writes the fixture ingest DB and the three embedding DBs (vectors planted for every text of the real text set)."""
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, _fixture_rows(), [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = load_corpora(db)
    texts, set_sha, derived = text_set(CS)
    meta = {}
    for C in CS.values():
        for i in np.nonzero(C.kept)[0]:
            meta[C.text[i]] = (C.name, -1 if C.oos[i] else int(C.fine[i][-2:]), "oos" if C.oos[i] else "item")
    variant_of = {}
    for i, t, _c in derived["variants"]:
        variant_of[t] = CS["massive"].text[i]
    pair_of = {}
    for c, ps in derived["pairs"].items():
        for i, j, t in ps:
            pair_of[t] = (CS[c].text[i], CS[c].text[j])
    ingest_sha = II.file_sha(db)
    for e in EMBEDDERS:
        dim = EA.EG.NATIVE_DIM[MODEL[e]]
        V = _planted(meta, dim, e)
        r = np.random.default_rng(99)
        for t, o in variant_of.items():
            V[t] = V[o] + 0.02 * r.normal(size=dim)
        for t, (a, b) in pair_of.items():
            V[t] = V[a] + V[b]
        p = emb_path(e, td)
        con = sqlite3.connect(p)
        con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
        con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(expected_meta(e, set_sha, len(texts), ingest_sha),
                                                                              model_digest="stub").items()))
        con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(V[t], dtype=">f4").tobytes()) for t in texts])
        con.commit()
        con.close()
    return db, CS, texts, derived


def _pins_file(td, db, emb_dir, blank=False):
    p = os.path.join(td, "pins_%d.json" % int(time.time() * 1e6))
    emb = {e: (None if blank else II.file_sha(emb_path(e, emb_dir))) for e in EMBEDDERS}
    con = II.open_db_ro(db)
    raw = {n: (None if blank else sh) for n, sh in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(p, "w") as f:
        json.dump({"schema": II.PINS_SCHEMA, "raw": raw, "ingest_db": None if blank else II.file_sha(db), "emb": emb}, f)
    return p


def _cap(fn):
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as ex:
            err = str(ex)
    return buf.getvalue(), err, res


def _line(out, prefix):
    got = [ln for ln in out.splitlines() if ln.startswith(prefix)]
    return got[0] if got else ""


def selftest(only=None, quiet=False, fixture=None):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    saved_url, saved_heavy = EA.OLLAMA_URL, globals()["_foreign_heavy"]
    EA.OLLAMA_URL = "http://127.0.0.1:9/api/embed"          # a closed port: nothing real is contacted
    try:
        with fixture_scope():
            if fixture is None:
                with tempfile.TemporaryDirectory() as td:
                    return _selftest(sel, ok, n, td, None)
            return _selftest(sel, ok, n, fixture[0], fixture)
    finally:
        EA.OLLAMA_URL = saved_url
        globals()["_foreign_heavy"] = saved_heavy
        PINS_FILE_OVERRIDE[0] = None


def _selftest(sel, ok, n, td, fixture):
    from sklearn.metrics import normalized_mutual_info_score, roc_auc_score
    if sel("ST-STATS"):
        r = np.random.default_rng(3)
        for _ in range(5):
            t, p = r.integers(6, size=300), r.integers(9, size=300)
            ok(abs(nmi(t, p) - normalized_mutual_info_score(t, p, average_method="arithmetic")) < 1e-10, "ST-STATS nmi == sklearn arithmetic NMI")
        ok(nmi(np.zeros(5, int), np.zeros(5, int)) == 1.0 and nmi(np.zeros(5, int), np.arange(5)) == 0.0, "ST-STATS nmi conventions (1 cluster each: 1.0; one side constant: 0.0)")
        w = r.integers(0, 3, size=300).astype(float)
        rep_t, rep_p = np.repeat(t, w.astype(int)), np.repeat(p, w.astype(int))
        ok(abs(nmi(t, p, w) - normalized_mutual_info_score(rep_t, rep_p)) < 1e-10, "ST-STATS weighted nmi == nmi of the replicated rows")
        pos, neg = np.round(r.normal(1, 1, 200), 1), np.round(r.normal(0, 1, 150), 1)
        ok(abs(auroc(pos, neg) - roc_auc_score(np.r_[np.ones(200), np.zeros(150)], np.r_[pos, neg])) < 1e-12, "ST-STATS auroc == sklearn (with ties)")
        hm_ = hanley_mcneil(0.90, 6750, 1350)
        ok(abs(hm_ - 0.00352) < 0.00002 and abs(hm_ * np.sqrt(1.05) - 0.0036) < 0.00005 and abs(hanley_mcneil(0.90, 1350, 6750) - 0.00573) < 0.00002,
           "ST-STATS Hanley-McNeil SE at A 0.90, n_pos 6,750 in-scope / n_neg 1,350 OOS = %.5f (x sqrt(1.05) = %.5f); swapped (registered) 0.00573" % (hm_, hm_ * np.sqrt(1.05)))
        ok(kish(np.array([0, 0, 1, 2, 2, 2])) == (4 + 1 + 9) / 6.0, "ST-STATS Kish = sum m^2 / sum m")
        ok([_hit(0.86, 0.86, 0.93), _hit(0.93, 0.86, 0.93), _hit(0.8599, 0.86, 0.93), _hit(float("nan"), 0.0, 1.0)] == ["HELD", "HELD", "FAILED", "FAILED"],
           "ST-STATS a prediction HELD at both interval ends, FAILED outside or undefined")
        ok(c1_status(-0.03, -0.05, -0.01, 0.02) == "WORSE" and c1_status(-0.03, -0.05, 0.001, 0.02) == "NEITHER"
           and c1_status(-0.015, -0.05, -0.01, 0.02) == "NEITHER" and c1_status(0.03, 0.01, 0.05, 0.02) == "BETTER"
           and c1_status(0.03, -0.001, 0.05, 0.02) == "NEITHER" and c1_status(-0.02, -0.04, -0.01, 0.02) == "NEITHER",
           "ST-STATS C1 status: WORSE needs D < -bar AND upper < 0 (strict at the bar); BETTER symmetric")
        ok([band(0.85, 0.9, 0.85), band(0.8499, 0.9, 0.85), band(0.7, 0.8499, 0.85), band(0.7, 0.85, 0.85)] == ["HELD", "UNDETERMINED", "FAILED", "UNDETERMINED"],
           "ST-STATS band: HELD at lower == bar; FAILED only when upper < bar")
        X = unit(np.r_[np.random.default_rng(1).normal(size=(40, 8)) + 12 * np.eye(8)[0], np.random.default_rng(2).normal(size=(40, 8)) + 12 * np.eye(8)[1]])
        lab = assign(X, skmeans(X, 2, 0))
        ok(nmi(np.r_[np.zeros(40, int), np.ones(40, int)], lab) == 1.0, "ST-STATS spherical k-means separates two planted clusters")
        try:
            skmeans(X[:3], 5, 0)
            ok(False, "ST-STATS n < k raises Skip")
        except Skip:
            ok(True, "ST-STATS n < k raises Skip")
    if sel("ST-VERDICT"):
        def mk(st):     # st: {(c, g, e): status}
            c1 = {}
            for c in CORPORA:
                for g in LEVELS[c]:
                    c1[(c, g)] = {"per": {e: {"status": st.get((c, g, e), "NEITHER")} for e in FAMILIES}}
            return c1
        v = c1_verdicts(mk({("massive", "fine", "nomic"): "WORSE", ("banking77", "fine", "nomic"): "WORSE"}))
        ok(v["C1a"] == "HELD" and v["C1b"] == "NOT FIRED", "ST-VERDICT C1a HELD: nomic WORSE on 2 of 3 (massive, banking77 -- not the first two)")
        v = c1_verdicts(mk({("massive", "fine", "nomic"): "WORSE", ("clinc", "fine", "gemma"): "WORSE"}))
        ok(v["C1a"] == "HELD" and v["C1a_alt"] == "FAILED", "ST-VERDICT C1a HELD per corpus (nomic on massive, gemma on clinc: 2 corpora); the per-family reading FAILED (not of record)")
        v = c1_verdicts(mk({("banking77", "fine", "nomic"): "WORSE", ("banking77", "fine", "gemma"): "WORSE"}))
        ok(v["C1a"] == "FAILED" and v["alt_corpora"] == ["banking77"], "ST-VERDICT C1a FAILED: both families WORSE on ONE corpus (fewer than 2 corpora)")
        v = c1_verdicts(mk({("banking77", "fine", "gemma"): "WORSE", ("clinc", "fine", "gemma"): "WORSE", ("clinc", "coarse", "gemma"): "BETTER"}))
        ok(v["C1a"] == "HELD" and v["C1b"] == "NOT FIRED", "ST-VERDICT C1a HELD via gemma (clinc, banking77); a coarse BETTER does not fire C1b")
        v = c1_verdicts(mk({("clinc", "coarse", "gemma"): "WORSE"}))
        ok(v["C1b"] == "FIRES" and v["coarse_worse"] == [("clinc", "gemma")] and v["C1a"] == "FAILED", "ST-VERDICT C1b FIRES on one coarse WORSE (clinc gemma, the last site)")
        v = c1_verdicts(mk({("massive", "fine", "nomic"): "WORSE", ("massive", "fine", "gemma"): "WORSE", ("banking77", "fine", "nomic"): "WORSE",
                            ("banking77", "fine", "gemma"): "WORSE"}))
        ok(v["qwen3_better_both"] == ["massive", "banking77"], "ST-VERDICT qwen3 BETTER than both on massive + banking77 (B8)")
        cr = lambda lo, hi: {"lo": lo, "hi": hi}
        ok(c3_verdict({"massive": cr(0.01, 0.5), "clinc": cr(-0.1, 0.4), "banking77": cr(0.001, 0.6)})[0] == "HELD", "ST-VERDICT C3 HELD on massive + banking77")
        ok(c3_verdict({"massive": cr(-0.5, 0.0), "clinc": cr(-0.1, 0.4), "banking77": cr(-0.4, -0.01)})[0] == "FAILED", "ST-VERDICT C3 FAILED (upper <= 0 at 0.0 counts)")
        ok(c3_verdict({"massive": cr(0.0, 0.5), "clinc": cr(-0.1, 0.4), "banking77": cr(0.2, 0.6)})[0] == "UNDETERMINED", "ST-VERDICT C3 lower == 0 is not positive -> UNDETERMINED")
        ok(c3_verdict({"massive": cr(float("nan"), float("nan")), "clinc": cr(0.1, 0.4), "banking77": cr(0.2, 0.6)})[0] == "HELD",
           "ST-VERDICT C3 an undefined corpus counts neither way")
        # every criterion and falsifier print branch, by execution
        base = {"fine_worse": {"nomic": ["massive", "clinc"], "gemma": []}, "C1a_alt": "HELD", "alt_corpora": ["massive", "clinc"],
                "coarse_worse": [], "C3_pos": [], "C3_nonpos": []}
        for c1a, c1b, c2v, c3v, c4v in (("HELD", "NOT FIRED", "HELD", "HELD", "HELD"), ("FAILED", "FIRES", "FAILED", "FAILED", "FAILED"),
                                        ("HELD", "NOT FIRED", "UNDETERMINED", "UNDETERMINED", "UNDETERMINED")):
            V = dict(base, C1a=c1a, C1b=c1b, C2=c2v, C3=c3v, C4=c4v)
            txt = "\n".join(criteria_lines(V))
            ok(("S0-C1a (fine dependence): %s" % c1a) in txt and ("S0-C1b (coarse): %s" % c1b) in txt and ("S0-C2 (OOS, CLINC): %s" % c2v) in txt
               and ("S0-C3 (label-free cell margin vs gold purity): %s" % c3v) in txt and ("S0-C4 (slot-swap stability, MASSIVE): %s" % c4v) in txt,
               "ST-VERDICT criteria lines print %s / %s / %s / %s / %s" % (c1a, c1b, c2v, c3v, c4v))
            fired = c1a == "FAILED"
            for fid, cond in (("F1", c1a == "FAILED"), ("F1'", c1b == "FIRES"), ("F2", c2v == "FAILED"), ("F3", c3v == "FAILED"), ("F4", c4v == "FAILED")):
                ok(("%s: %s --" % (fid, "FIRED" if cond else "NOT FIRED")) in txt, "ST-VERDICT falsifier %s prints %s" % (fid, "FIRED" if cond else "NOT FIRED"))
            del fired
        V = dict(base, C1a="HELD", C1b="NOT FIRED", C2="HELD", C3="HELD", C4="HELD",
                 R1={"massive": ("SCOREABLE", 0.005, 0.01), "clinc": ("DESCRIPTIVE-ONLY", 0.0072, 0.01)})
        txt = "\n".join(criteria_lines(V))
        ok("R-1 massive fine, nomic: SCOREABLE" in txt and "R-1 clinc fine, nomic: DESCRIPTIVE-ONLY" in txt and "R-4 gemma's fine WORSE" in txt,
           "ST-VERDICT the R-1 SCOREABLE / DESCRIPTIVE-ONLY and the R-4 lines print")
        c1s = {("massive", "fine"): {"per": {"nomic": {"se": 0.020 / 2.8}}, "spread": {"qwen3": 0.020, "nomic": 0.01}},    # both at the bound
               ("clinc", "fine"): {"per": {"nomic": {"se": 0.00715}}, "spread": {"qwen3": 0.0, "nomic": 0.0}},               # SE just above
               ("banking77", "fine"): {"per": {"nomic": {"se": 0.001}}, "spread": {"qwen3": 0.0201, "nomic": 0.0}}}         # qwen3's spread
        ok({c: w for c, (w, _a, _b) in r1_lines(c1s).items()} == {"massive": "SCOREABLE", "clinc": "DESCRIPTIVE-ONLY", "banking77": "DESCRIPTIVE-ONLY"},
           "ST-VERDICT R-1 at the boundaries: SE == 0.020/2.8 and spread == 0.020 SCOREABLE; just above either DESCRIPTIVE-ONLY; the spread is the max of the two arms")
        V = dict(base, C1a="HELD", C1b="NOT FIRED", C2=np.bool_(True) and "HELD", C3="HELD", C4="HELD")
        ok("F2: NOT FIRED" in "\n".join(criteria_lines(V)), "ST-VERDICT numpy-typed inputs still print (no identity tests)")
    if sel("ST-DERIVED") or sel("ST-E2E") or sel("ST-REFUSE") or sel("ST-EMBED") or sel("ST-DRY") or sel("ST-PILOT"):
        if fixture is None:
            db, CS, texts, derived = build_fixture(td)
        else:                                         # the mutants: fixture files built once, READ in this (mutated) namespace
            db = fixture[1]
            CS = load_corpora(db)
            texts, _sha, derived = text_set(CS)
    if sel("ST-DERIVED"):
        C = CS["massive"]
        var = derived["variants"]
        inv_ok = True
        tr = C.idx(SS.TRAIN)
        inv = {}
        for i in tr:
            for (_s, _e, t, v) in parse_annot(C.annot[i]):
                inv.setdefault((C.fine[i], t), set()).add(v)
        for i, t, ch in var:
            orig = parse_annot(C.annot[i])
            newv = re.findall(r"v\d+_\d+", t)[:len(orig)]
            for (_s, _e, ty, v), nv in zip(orig, newv):
                if nv != v and nv not in inv.get((C.fine[i], ty), set()):
                    inv_ok = False
            if C.side[i] != SS.EVAL or not C.kept[i]:
                inv_ok = False
        ok(all(isinstance(ch, tuple) and len(ch) >= 1 and all(t in [x[2] for x in parse_annot(C.annot[i])] for t in ch) for i, _t, ch in var),
           "ST-DERIVED each variant records the slot TYPES it swapped (B7 printed)")
        ok(inv_ok and len(var) > 50, "ST-DERIVED every C4 variant: an EVAL original, swapped values from the SAME intent x slot type on TRAIN (%d)" % len(var))
        ok(all(SS.stem_key(t) not in set(C.stem[j] for j in range(len(C.ids)) if C.side[j] == SS.TRAIN) for _i, t, _c in var),
           "ST-DERIVED no variant collides with a TRAIN stem_key")
        vc = derived["variant_counts"]
        ok(vc["train_collision"] > 0 and vc["with_slot"] < vc["eval_items"], "ST-DERIVED the fixture exercises TRAIN collisions (%d) and slot-less items (%d)"
           % (vc["train_collision"], vc["eval_items"] - vc["with_slot"]))
        ok(vc["variants"] + vc["no_alternative"] + vc["train_collision"] + vc["unchanged"] + vc["annot_text_mismatch"] == vc["with_slot"],
           "ST-DERIVED variant accounting closes (annot/text mismatches excluded, C-8)")
        Cm_ = CS["massive"]
        saved_annot = list(Cm_.annot)
        j0 = [int(i) for i in Cm_.idx(SS.EVAL) if parse_annot(Cm_.annot[i])][0]
        Cm_.annot[j0] = Cm_.annot[j0].replace(" please", " thanks")        # renders to a text that is not the item's text
        try:
            v2_, c2_ = c4_variants(Cm_)
        finally:
            Cm_.annot[:] = saved_annot
        ok(c2_["annot_text_mismatch"] == vc["annot_text_mismatch"] + 1 and j0 not in [i for i, _t, _c in v2_],
           "ST-DERIVED a row whose annot does not render to its text is EXCLUDED from C4 and counted")
        for c in N_PAIRS:
            ps = derived["pairs"][c]
            ok(len(ps) == N_PAIRS[c] and all(CS[c].coarse[i] != CS[c].coarse[j] and CS[c].side[i] == SS.EVAL and CS[c].side[j] == SS.EVAL
                                             for i, j, _t in ps), "ST-DERIVED D5 %s: %d EVAL-EVAL pairs of different coarse labels" % (c, N_PAIRS[c]))
        t2, sha2, _d2 = text_set(CS)
        ok(t2 == texts and sha2 == text_set(CS)[1], "ST-DERIVED the text set and its sha256 are deterministic")
        ok(int((~CS["clinc"].kept).sum()) == 4, "ST-DERIVED the fixture's CLINC carries 4 dropped rows (an OOS collision pair, a cross-label pair)")
        C = CS["clinc"]
        ev = C.idx(SS.EVAL)
        try:
            fit_rows(C, np.r_[C.idx(SS.TRAIN), ev[:1]], (SS.TRAIN,), "planted EVAL row")
            ok(False, "ST-DERIVED a planted EVAL row in a fit REFUSES")
        except SystemExit as ex:
            ok("TRAIN-ONLY" in str(ex), "ST-DERIVED a planted EVAL row in a fit REFUSES")
        try:
            fit_rows(C, np.r_[C.idx(SS.TRAIN), C.idx(SS.EVAL, oos=True)[:1]], (SS.TRAIN, SS.EVAL), "planted OOS row")
            ok(False, "ST-DERIVED a planted OOS row REFUSES even where EVAL is allowed")
        except SystemExit as ex:
            ok("1 OOS rows" in str(ex), "ST-DERIVED a planted OOS row REFUSES even where EVAL is allowed")
        drop = [int(i) for i in np.nonzero(~CS["clinc"].kept)[0] if not CS["clinc"].oos[i]]      # an IN-SCOPE dropped row
        try:
            fit_rows(C, np.r_[C.idx(SS.TRAIN), drop[:1]], (SS.TRAIN, SS.EVAL, SS.GATE), "planted dropped row")
            ok(False, "ST-DERIVED an in-scope dropped (cross-label) row in a fit REFUSES (every side allowed)")
        except SystemExit as ex:
            ok(len(drop) >= 1 and "0 OOS rows, 1 dropped rows" in str(ex), "ST-DERIVED an in-scope dropped (cross-label) row in a fit REFUSES (every side allowed)")
    if sel("ST-E2E"):
        pins = _pins_file(td, db, td)
        PINS_FILE_OVERRIDE[0] = pins
        outd = tempfile.mkdtemp(prefix="out_", dir=td)
        out, err, res = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd, "--census-bracket", "selftest fixture"]))
        ok(err is None and res is not None, "ST-E2E --run end to end on the fixture (%s)" % (err or "")[:300])
        R, V, path = _E2E[0]
        txt = open(path, encoding="utf-8").read()
        # C1: the planted answer (nomic has no fine structure; gemma = qwen3's structure)
        ok(V["C1a"] == "HELD" and V["fine_worse"]["nomic"] == ["massive", "clinc", "banking77"] and V["fine_worse"]["gemma"] == [],
           "ST-E2E C1a HELD: nomic WORSE at the fine level on 3 of 3, gemma on 0 (planted)")
        ok("S0-C1a (fine dependence): HELD" in txt and "F1: NOT FIRED" in txt, "ST-E2E the outcome prints C1a HELD, F1 NOT FIRED")
        ok(V["C1b"] == "NOT FIRED" and "S0-C1b (coarse): NOT FIRED" in txt and "F1': NOT FIRED" in txt, "ST-E2E C1b NOT FIRED (planted coarse intact)")
        r = R["c1"][("clinc", "fine")]
        from sklearn.metrics import normalized_mutual_info_score as NM
        Dind = np.mean([NM(r["truth"], p) for p in r["preds"]["nomic"]]) - np.mean([NM(r["truth"], p) for p in r["preds"]["qwen3"]])
        ok(abs(Dind - r["per"]["nomic"]["D"]) < 1e-9 and ("D(nomic, fine) = %+.5f" % Dind) in txt,
           "ST-E2E printed D(nomic, clinc fine) %+.5f == an independent sklearn recomputation (EVAL minus qwen3, seed means)" % Dind)
        CL = CS["clinc"]
        # C-3 (RV-2): the C1 interval recomputed independently: PAIRED component weights (one resample for all three embedders)
        con = II.open_db_ro(db)
        stem_of = dict(con.execute("SELECT item_id, stem_key FROM items WHERE corpus='clinc'").fetchall())
        con.close()
        ev_ids = [CL.ids[i] for i in CL.idx(SS.EVAL)]
        _u, cc_ = np.unique(np.array([stem_of[x] for x in ev_ids], dtype=object), return_inverse=True)
        rng_ = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index("clinc") + LEVELS["clinc"].index("fine"))
        dr_ = []
        G_ = int(cc_.max()) + 1
        for _b in range(BOOT_B):
            w_ = np.bincount(rng_.integers(G_, size=G_), minlength=G_)[cc_].astype(float)
            dr_.append(np.mean([nmi(r["truth"], p, w_) for p in r["preds"]["nomic"]]) - np.mean([nmi(r["truth"], p, w_) for p in r["preds"]["qwen3"]]))
        q_lo, q_hi = np.percentile(dr_, 2.5), np.percentile(dr_, 97.5)
        pn = r["per"]["nomic"]
        ok(abs(pn["lo"] - (2 * pn["D"] - q_hi)) < 1e-12 and abs(pn["hi"] - (2 * pn["D"] - q_lo)) < 1e-12
           and abs(pn["plo"] - q_lo) < 1e-12 and abs(pn["bias"] - (np.mean(dr_) - pn["D"])) < 1e-12,
           "ST-E2E C1 clinc fine nomic: BASIC CI [%+.5f, %+.5f] = [2D - q97.5, 2D - q2.5] of an independent PAIRED bootstrap; bias %+.5f" % (pn["lo"], pn["hi"], pn["bias"]))
        ok(("95%% BASIC CI [%+.5f, %+.5f] (decides, C-1)" % (pn["lo"], pn["hi"])) in txt and ("percentile CI [%+.5f, %+.5f] (descriptive)" % (pn["plo"], pn["phi"])) in txt
           and ("bias-corrected D - b = %+.5f" % pn["dbc"]) in txt, "ST-E2E the basic CI decides; the bias-corrected point and the percentile CI are printed beside")
        spq = [NM(r["truth"], p) for p in r["preds"]["qwen3"]]
        spn = [NM(r["truth"], p) for p in r["preds"]["nomic"]]
        sp_ind = max(max(spq) - min(spq), max(spn) - min(spn))
        ok(sp_ind > 0 and abs(max(r["spread"]["qwen3"], r["spread"]["nomic"]) - sp_ind) < 1e-9
           and abs(r["per"]["nomic"]["bar"] - max(2.8 * r["per"]["nomic"]["se"], sp_ind)) < 1e-12,
           "ST-E2E bar = max(2.8 SE, max(spread_qwen3, spread_nomic)) = %.5f with spread = max - min over seeds %.5f" % (r["per"]["nomic"]["bar"], sp_ind))
        CL = CS["clinc"]
        con = II.open_db_ro(db)
        n_ev = int(con.execute("SELECT COUNT(*) FROM items WHERE corpus='clinc' AND side='EVAL' AND is_oos=0 AND drop_reason IS NULL").fetchone()[0])
        n_oos = int(con.execute("SELECT COUNT(*) FROM items WHERE corpus='clinc' AND side='EVAL' AND is_oos=1 AND drop_reason IS NULL").fetchone()[0])
        con.close()
        ok(r["n"] == n_ev and R["c2"]["n_in"] == n_ev and R["c2"]["n_oos"] == n_oos and ("n_in %d, n_OOS %d" % (n_ev, n_oos)) in txt,
           "ST-E2E C1 / C2 denominators = the DB's kept EVAL in-scope %d and OOS %d rows (SQL count)" % (n_ev, n_oos))
        si, so, sg = R["c2"]["scores"]
        ok(abs(R["c2"]["A"] - roc_auc_score(np.r_[np.ones(len(si)), np.zeros(len(so))], np.r_[si, so])) < 1e-12 and 0.85 < R["c2"]["A"] < 0.999,
           "ST-E2E C2 A %.5f == sklearn roc_auc on the printed populations (in-scope EVAL vs OOS)" % R["c2"]["A"])
        ok(V["C2"] == "HELD" and "S0-C2 (OOS, CLINC): HELD" in txt and "F2: NOT FIRED" in txt and len(set(R["c2"]["per_seed"])) > 1,
           "ST-E2E C2 HELD (planted OOS), A varies by seed %s: seed 0 decides" % [round(a, 4) for a in R["c2"]["per_seed"]])
        # C-3 (RV-4): the C2 interval recomputed independently: stratified, interleaved in-scope / OOS component weights
        con = II.open_db_ro(db)
        stem_all = dict(con.execute("SELECT item_id, stem_key FROM items WHERE corpus='clinc'").fetchall())
        con.close()
        _u, cin = np.unique(np.array([stem_all[CL.ids[i]] for i in CL.idx(SS.EVAL)], dtype=object), return_inverse=True)
        _u, cout = np.unique(np.array([stem_all[CL.ids[i]] for i in CL.idx(SS.EVAL, oos=True)], dtype=object), return_inverse=True)
        rng_ = np.random.default_rng(BOOT_SEED + 2)
        Gi, Go = int(cin.max()) + 1, int(cout.max()) + 1
        a_ = []
        from sklearn.metrics import roc_auc_score as RAS
        for _b in range(200):
            wi = np.bincount(rng_.integers(Gi, size=Gi), minlength=Gi)[cin]
            wo = np.bincount(rng_.integers(Go, size=Go), minlength=Go)[cout]
            a_.append(RAS(np.r_[np.ones(int(wi.sum())), np.zeros(int(wo.sum()))], np.r_[np.repeat(si, wi), np.repeat(so, wo)]))
        dr2 = R["c2"]["draws"][:200]
        ok(np.allclose(dr2, a_, atol=1e-12), "ST-E2E C2: the first 200 bootstrap AUROCs == an independent stratified recomputation (sklearn on replicated rows)")
        ok((R["c2"]["lo"], R["c2"]["hi"]) == pct_ci(R["c2"]["draws"]) and len(R["c2"]["draws"]) == BOOT_B, "ST-E2E C2 CI = the percentile of all %d draws" % BOOT_B)
        thr_ind = float(np.sort(sg)[int(np.floor(0.05 * len(sg)))])
        ok(R["c2"]["thr"] == thr_ind and R["c2"]["tpr_gate"] >= 0.95 and abs(R["c2"]["fpr95"] - float(np.mean(so >= thr_ind))) < 1e-12,
           "ST-E2E FPR95 %.4f at the GATE threshold (GATE TPR %.4f >= 0.95)" % (R["c2"]["fpr95"], R["c2"]["tpr_gate"]))
        ok(V["C3"] == "HELD" and all(R["c3"][c]["lo"] > 0 for c in CORPORA) and "S0-C3 (label-free cell margin vs gold purity): HELD" in txt,
           "ST-E2E C3 HELD: rho lower > 0 on 3 of 3 (planted near-duplicate intents: low margin, low purity) %s" % [round(R["c3"][c]["rho"], 3) for c in CORPORA])
        cells = R["c3"]["massive"]["cells"]
        use = [x for x in cells if x["n_eval"] >= C3_MIN_EVAL]
        ok(abs(spearman([x["margin"] for x in use], [x["purity"] for x in use]) - R["c3"]["massive"]["rho"]) < 1e-12
           and R["c3"]["massive"]["n_cells"] == len(use), "ST-E2E C3 rho recomputed from the cell table (cells >= %d EVAL: %d)" % (C3_MIN_EVAL, len(use)))
        # independent recomputation of the C3 cell table from SQL rows and raw blobs (TRAIN margins, EVAL purity)
        con = II.open_db_ro(db)
        trr = con.execute("SELECT text, fine FROM items WHERE corpus='massive' AND side='TRAIN' AND is_oos=0 AND drop_reason IS NULL").fetchall()
        trr_ids = con.execute("SELECT item_id, text, fine FROM items WHERE corpus='massive' AND side='TRAIN' AND is_oos=0 AND drop_reason IS NULL").fetchall()
        evr_ids = con.execute("SELECT item_id, text, fine FROM items WHERE corpus='massive' AND side='EVAL' AND is_oos=0 AND drop_reason IS NULL").fetchall()
        evr = con.execute("SELECT text, fine FROM items WHERE corpus='massive' AND side='EVAL' AND is_oos=0 AND drop_reason IS NULL").fetchall()
        con.close()
        econ = II.open_db_ro(emb_path("qwen3", td))
        blob = dict(econ.execute("SELECT query, vector FROM embeddings").fetchall())
        econ.close()
        vec = lambda rows_: unit(np.array([np.frombuffer(blob[t], dtype=">f4")[:SLICE].astype(np.float64) for t, _f in rows_]))
        Cm = R["c3"]["massive"]["Cm"]
        trr_o = [(t, f) for (_id, t, f) in sorted(trr_ids)]
        Cm0_ind = skmeans(vec(trr_o), II.GOLD_K["massive"][1], 0)
        ok(np.allclose(Cm0_ind, Cm, atol=1e-12), "ST-E2E C3 (RV-5): the cell table's centroids are the SEED-0 k-means on MASSIVE TRAIN (independent refit)")
        evv = [(t, f) for (_id, t, f) in sorted(evr_ids)]
        vt = [t for _i, t, _c in derived["variants"]]
        vo = [CS["massive"].text[i] for i, _t, _c in derived["variants"]]
        vecv = lambda ts: unit(np.array([np.frombuffer(blob[t], dtype=">f4")[:SLICE].astype(np.float64) for t in ts]))
        same_ind = (np.argmax(vecv(vo) @ Cm0_ind.T, axis=1) == np.argmax(vecv(vt) @ Cm0_ind.T, axis=1)).astype(float)
        ok(np.array_equal(same_ind, R["c4"]["same0"]) and np.allclose(R["c4"]["Cm0"], Cm0_ind, atol=1e-12), "ST-E2E C4 (RV-6): the same-cell vector == an independent SEED-0 recomputation (S %.5f)" % same_ind.mean())
        del evv
        st_ = np.sort(vec(trr) @ Cm.T, axis=1)
        own = np.argmax(vec(trr) @ Cm.T, axis=1)
        evc = np.argmax(vec(evr) @ Cm.T, axis=1)
        good = True
        for x in R["c3"]["massive"]["cells"]:
            m_ = st_[own == x["cell"]]
            labs = [f for (_t, f), cc in zip(evr, evc) if cc == x["cell"]]
            if len(m_) and abs(float((m_[:, -1] - m_[:, -2]).mean()) - x["margin"]) > 1e-9:
                good = False
            if len(labs) != x["n_eval"] or (labs and abs(max(labs.count(l) for l in set(labs)) / len(labs) - x["purity"]) > 1e-12):
                good = False
        ok(good, "ST-E2E C3 cell table == an independent recomputation (TRAIN top1 - top2 margins, EVAL purities; SQL + raw blobs)")
        ok(all(R["c3"][c]["n_excluded"] >= 1 for c in CORPORA) and "excluded < 10 EVAL" in txt,
           "ST-E2E C3 excludes the small cells (< 10 EVAL): %s" % [R["c3"][c]["n_excluded"] for c in CORPORA])
        ok(len(R["c4"]["same0"]) == R["c4"]["n"] and R["c4"]["S"] == float(np.mean(R["c4"]["same0"])),
           "ST-E2E C4 S is the mean over the %d variants (the registered denominator)" % R["c4"]["n"])
        ok(V["C4"] == "HELD" and R["c4"]["S"] >= 0.95 and R["c4"]["n"] == len(derived["variants"]) and "S0-C4 (slot-swap stability, MASSIVE): HELD" in txt
           and ("n %d variants" % R["c4"]["n"]) in txt, "ST-E2E C4 HELD: S %.4f over %d variants (planted: variant = original + noise)" % (R["c4"]["S"], R["c4"]["n"]))
        ok("TRAIN-ONLY:" in txt and ", 0 with an EVAL row," in txt and R["fit_audit"].startswith("TRAIN-ONLY") and len(FIT_LOG) > 100,
           "ST-E2E the TRAIN-ONLY audit line prints 0 EVAL rows over %d fits" % len(FIT_LOG))
        ok(all(("ATTRIBUTION: " + II.ATTRIBUTION[c]) in txt for c in CORPORA) and "DOES NOT SHOW:" in txt and "mean Brier" in txt
           and "P6 D4 selective" in txt and "D7 HWU64" in txt, "ST-E2E attribution, the does-not-show list, predictions and D7 printed")
        ok("census" in txt.lower() and "selftest fixture" in txt, "ST-E2E the census line carries the bracket verbatim")
        ok("B7 swapped slots" in txt and os.path.isfile(os.path.join(outd, "s0_c4_variants.csv"))
           and sum(1 for _ in open(os.path.join(outd, "s0_c4_variants.csv"), encoding="utf-8")) == len(derived["variants"]) + 1,
           "ST-E2E B7: the swapped slots are printed and s0_c4_variants.csv lists every variant (ids and slot types)")
        ok("Hanley-McNeil SE (A, n_pos in-scope, n_neg OOS; C-7) %.5f" % hanley_mcneil(R["c2"]["A"], R["c2"]["n_in"], R["c2"]["n_oos"]) in txt
           and "counts swapped, conservative" in txt, "ST-E2E C-7: HM SE in its own order printed, the registered order beside")
        for c in CORPORA:
            rr = R["c1"][(c, "fine")]
            se_, sp_ = rr["per"]["nomic"]["se"], max(rr["spread"]["qwen3"], rr["spread"]["nomic"])
            w_ = "SCOREABLE" if (se_ <= 0.020 / 2.8 and sp_ <= 0.020) else "DESCRIPTIVE-ONLY"
            ok(("R-1 %s fine, nomic: %s" % (c, w_)) in txt, "ST-E2E R-1 %s prints %s (SE %.5f, spread %.5f)" % (c, w_, se_, sp_))
        ok("R-2: EVERY kept CLINC OOS row" in txt and ("hash sides {\"EVAL\": %d" % int((CL.hash_side[CL.idx(SS.EVAL, oos=True)] == SS.EVAL).sum())) in txt
           and "NOT RUN (R-3" in txt, "ST-E2E R-2 (every OOS row, its hash sides) and R-3 (D7 NOT RUN) printed")
        p1 = float(np.mean(R["c1"][("clinc", "fine")]["nmi"]["qwen3"]))
        ok(("P1 clinc fine NMI (qwen3 256, seed mean) %.4f vs 0.90 [0.86, 0.93]: %s" % (p1, "HELD" if 0.86 <= p1 <= 0.93 else "FAILED")) in txt,
           "ST-E2E P1 clinc fine scored HELD / FAILED at the point (%.4f)" % p1)
        for fn_ in ("s0_c1.csv", "s0_c3_cells.csv"):
            ok(os.path.isfile(os.path.join(outd, fn_)), "ST-E2E %s written beside" % fn_)
        out2, err2, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd, "--census-bracket", "x"]))
        ok(err2 is not None and "write-once" in err2 and open(path, encoding="utf-8").read() == txt, "ST-E2E a second --run REFUSES; the outcome is unchanged")
        # the pilot writes _PILOT, never the file of record
        outp = tempfile.mkdtemp(prefix="outp_", dir=td)
        out3, err3, _r = _cap(lambda: main(["--run", "--pilot", "--db", db, "--emb-dir", td, "--out-dir", outp]))
        ok(err3 is None and os.path.isfile(os.path.join(outp, "s0_outcome_PILOT.txt")) and not os.path.exists(os.path.join(outp, OUTCOME)),
           "ST-E2E --pilot writes s0_outcome_PILOT.txt only")
    if sel("ST-PILOT"):
        pd = tempfile.mkdtemp(prefix="pilot_", dir=td)
        keep = set(texts[:400])
        for e in EMBEDDERS:
            with open(emb_path(e, td), "rb") as s_, open(emb_path(e, pd), "wb") as d_:
                d_.write(s_.read())
            cp = sqlite3.connect(emb_path(e, pd))
            cp.executemany("DELETE FROM embeddings WHERE query = ?", [(t,) for t in texts if t not in keep])
            cp.commit()
            cp.close()
        PINS_FILE_OVERRIDE[0] = _pins_file(td, db, td, blank=True)
        outp = tempfile.mkdtemp(prefix="outpp_", dir=td)
        o, err, _r = _cap(lambda: main(["--run", "--pilot", "--db", db, "--emb-dir", pd, "--out-dir", outp]))
        ptxt = open(os.path.join(outp, "s0_outcome_PILOT.txt"), encoding="utf-8").read() if err is None else ""
        ok(err is None and "PILOT: NOT OF RECORD" in ptxt and "PILOT: a deciding readout was SKIPPED" in ptxt and ": SKIPPED (" in ptxt
           and "S0-C1a" not in ptxt and "F1:" not in ptxt and not os.path.exists(os.path.join(outp, OUTCOME)),
           "ST-PILOT partial rows (400 texts): the PILOT file names each SKIPPED readout and prints no verdict (%s)" % (err or "")[:200])
        o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", pd, "--out-dir", outp, "--census-bracket", "x"]))
        ok(err is not None and ("UNPINNED" in err or "have no vector" in err), "ST-PILOT --run (not pilot) on partial rows REFUSES")
        PINS_FILE_OVERRIDE[0] = _pins_file(td, db, pd)
        o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", pd, "--out-dir", outp, "--census-bracket", "x"]))
        ok(err is not None and "have no vector" in err and not os.path.exists(os.path.join(outp, OUTCOME)),
           "ST-PILOT --run on pinned partial rows REFUSES on the missing vectors; no outcome")
        vp = {}
        with contextlib.redirect_stdout(io.StringIO()):
            for e in EMBEDDERS:
                vp[e] = load_vectors(emb_path(e, pd), e, texts, allow_missing=True)
        o, err, _r = _cap(lambda: run_all(CS, vp, derived, pilot=False))
        ok(err is not None and "cannot run on the rows present" in err, "ST-PILOT a readout that cannot run is a REFUSAL outside the pilot (%s)" % (err or "")[-90:])
    if sel("ST-REFUSE"):
        outd = tempfile.mkdtemp(prefix="outr_", dir=td)
        PINS_FILE_OVERRIDE[0] = _pins_file(td, db, td, blank=True)
        _o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd, "--census-bracket", "x"]))
        ok(err is not None and "only against the registrar's pins" in err and not os.listdir(outd), "ST-REFUSE --run with null pins REFUSES before any read")
        PINS_FILE_OVERRIDE[0] = _pins_file(td, db, td)
        _o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd]))
        ok(err is not None and "outside 5%" in err and not os.listdir(outd), "ST-REFUSE the census outside 5%% without a bracket REFUSES (%s)" % (err or "")[-80:])
        with open(PINS_FILE_OVERRIDE[0]) as f:
            pj = json.load(f)
        pj["emb"]["gemma"] = "f" * 64
        pbad = os.path.join(td, "pins_bad.json")
        with open(pbad, "w") as f:
            json.dump(pj, f)
        PINS_FILE_OVERRIDE[0] = pbad
        _o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd, "--census-bracket", "x"]))
        ok(err is not None and "pinned" in err, "ST-REFUSE a gemma DB whose sha differs from its pin REFUSES")
        with open(_pins_file(td, db, td)) as f:
            pj = json.load(f)
        pj["raw"] = {k: None for k in pj["raw"]}
        praw = os.path.join(td, "pins_raw_null.json")
        with open(praw, "w") as f:
            json.dump(pj, f)
        PINS_FILE_OVERRIDE[0] = praw
        _o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd, "--census-bracket", "x"]))
        ok(err is not None and "raw none is UNPINNED" in err and not os.listdir(outd), "ST-REFUSE C-8: --run with a null raw pin REFUSES")
        pj["raw"] = {k: "e" * 64 for k in pj["raw"]}
        with open(praw, "w") as f:
            json.dump(pj, f)
        _o, err, _r = _cap(lambda: main(["--run", "--pilot", "--db", db, "--emb-dir", td, "--out-dir", outd]))
        ok(err is not None and "provenance sha256" in err, "ST-REFUSE C-8: a raw pin different from the ingest provenance REFUSES (even the pilot)")
        PINS_FILE_OVERRIDE[0] = _pins_file(td, db, td)
        open(emb_path("nomic", td) + "-wal", "wb").write(b"x")
        _o, err, _r = _cap(lambda: main(["--run", "--db", db, "--emb-dir", td, "--out-dir", outd, "--census-bracket", "x"]))
        os.remove(emb_path("nomic", td) + "-wal")
        ok(err is not None and "-wal" in err, "ST-REFUSE a non-empty -wal beside an embedding DB REFUSES the read")
        # the census branch passes when the planning counts match (PLANNED re-stated for the fixture)
        got = {"massive": len(CS["massive"].idx(SS.EVAL)), "clinc": len(CS["clinc"].idx(SS.EVAL)),
               "clinc_oos": len(CS["clinc"].idx(SS.EVAL, oos=True)), "banking77": len(CS["banking77"].idx(SS.EVAL))}
        PLANNED.update({k: int(round(v * 1.049)) for k, v in got.items()})
        line, off = census_check(CS, None)
        ok(not off and "WITHIN 5%" in line, "ST-REFUSE census at +4.9% passes")
        PLANNED.update({k: int(round(v * 1.06)) + 1 for k, v in got.items()})
        ok(census_check(CS, None)[1], "ST-REFUSE census at +6% is outside")
    if sel("ST-EMBED"):
        ed = tempfile.mkdtemp(prefix="emb_", dir=td)
        rec = tempfile.mkdtemp(prefix="rec_", dir=td)
        with EA.stub_ollama() as (url, log, state):
            EA.OLLAMA_URL = url
            saved_root = globals()["DATA_ROOT"]
            globals()["DATA_ROOT"] = rec
            try:
                for e in EMBEDDERS:                           # the caches of record: 25 rows each via the stub's own vectors
                    con = sqlite3.connect(os.path.join(rec, RECORD_CACHE[e]))
                    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
                    dim = EA.EG.NATIVE_DIM[MODEL[e]]
                    con.executemany("INSERT INTO embeddings VALUES (?, ?)",
                                    [("rec %d" % j, np.asarray(EA._stub_vec("rec %d" % j, dim), dtype=">f4").tobytes()) for j in range(25)])
                    con.commit()
                    con.close()
                globals()["_foreign_heavy"] = lambda: []
                PINS_FILE_OVERRIDE[0] = _pins_file(td, db, td, blank=True)
                n0 = len(log)
                o, err, _r = _cap(lambda: main(["--embed", "nomic", "--limit", "40", "--db", db, "--emb-dir", ed]))
                ok(err is None and len(log) == n0 and not os.path.exists(emb_path("nomic", ed)) and "dry: nothing posted" in o,
                   "ST-EMBED --embed without --go posts nothing and writes nothing")
                h0 = record_table_hashes()
                o, err, _r = _cap(lambda: main(["--embed", "nomic", "--limit", "40", "--go", "--db", db, "--emb-dir", ed]))
                posted = [x for x in log[n0:]]
                saved_go = (o, err)
                # intent-s0c: per-embedder bar. A stub route drifting to cos 0.9992 (after slice-256 + renormalise) on every row
                def drift_fn(cosv):
                    def fn(model, texts_):
                        e_ = [k for k, v in MODEL.items() if v == model][0]
                        con_ = sqlite3.connect(os.path.join(rec, RECORD_CACHE[e_]))
                        stored = dict(con_.execute("SELECT query, vector FROM embeddings").fetchall())
                        con_.close()
                        out_ = []
                        for t_ in texts_:
                            u_ = EA._slice_unit(np.frombuffer(stored[t_], dtype=">f4").astype(np.float64))
                            w_ = np.random.default_rng(int(hashlib.sha256(t_.encode()).hexdigest()[:8], 16)).normal(size=len(u_))
                            w_ -= np.dot(w_, u_) * u_
                            w_ /= np.linalg.norm(w_)
                            v_ = np.zeros(EA.EG.NATIVE_DIM[model])
                            v_[:len(u_)] = cosv * u_ + np.sqrt(1 - cosv * cosv) * w_
                            out_.append(v_.tolist())
                        return out_
                    return fn
                o, err, mn = _cap(lambda: route_parity("qwen3", drift_fn(0.9992)))
                ok(err is None and abs(mn - 0.9992) < 1e-5 and "parity bar qwen3: min cos >= 0.9980 (source: orchestrator's ruling" in o
                   and "min 0.999200" in o, "ST-PARITY a route drifting at 0.9992 PASSES qwen3 (bar 0.998, source printed)")
                o, err, _r = _cap(lambda: route_parity("nomic", drift_fn(0.9992)))
                ok(err is not None and "route parity nomic: min cos 0.999200 < 0.9999" in err and "parity bar nomic: min cos >= 0.9999 (source: embedder_arms" in o,
                   "ST-PARITY the same drift FAILS nomic (bar 0.9999, source printed)")
                o, err, _r = _cap(lambda: route_parity("gemma", drift_fn(0.9992)))
                ok(err is not None and "< 0.9999" in err, "ST-PARITY the same drift FAILS gemma (bar 0.9999)")
                o, err, _r = _cap(lambda: route_parity("qwen3", drift_fn(0.9979)))
                ok(err is not None and "route parity qwen3: min cos 0.997900 < 0.9980" in err, "ST-PARITY qwen3 at 0.9979 (just below 0.998) FAILS")
                o, err = saved_go
                ok(("Ollama endpoint %s" % url) in o, "ST-EMBED C-6: the --go header prints the resolved Ollama endpoint")
                ok(err is None and "route parity nomic" in o and "PASS" in _line(o, "[INTENT-S0] TRANSPORT route parity nomic"),
                   "ST-EMBED --go runs route parity on the cache of record first (%s)" % (err or "")[:200])
                ok(posted[0][2] == sorted(["rec %d" % j for j in range(25)], key=lambda t: hashlib.sha256(t.encode()).hexdigest())[:20],
                   "ST-EMBED parity posts the first 20 record texts by sha256")
                have = present_texts(emb_path("nomic", ed))
                ok(have == set(texts[:40]), "ST-EMBED --limit 40 writes exactly the first 40 texts of the sha-ordered set")
                ok(state["conns"] <= 2, "ST-EMBED one keep-alive connection reused across batches (%d TCP connections)" % state["conns"])
                ok(record_table_hashes() == h0 and "per-table after: unchanged" in o, "ST-EMBED the shared caches' per-table hashes unchanged")
                meta = read_meta(emb_path("nomic", ed))
                ok(meta["text_set_sha256"] == text_set(CS)[1] and meta["protocol"] == "RAW" and meta["model"] == MODEL["nomic"]
                   and meta["model_digest"] == "stubdigest-" + MODEL["nomic"], "ST-EMBED intent_meta pins set sha, RAW, model and the digest")
                o, err, _r = _cap(lambda: main(["--embed", "nomic", "--limit", "60", "--go", "--db", db, "--emb-dir", ed]))
                ok(err is None and present_texts(emb_path("nomic", ed)) == set(texts[:60]) and "present 40" in o, "ST-EMBED a second launch RESUMES (40 present, 20 new)")
                econ = II.open_db_ro(emb_path("nomic", ed))
                dims_ok = all(len(b) == 4 * EA.EG.NATIVE_DIM[MODEL["nomic"]] for (b,) in econ.execute("SELECT vector FROM embeddings"))
                econ.close()
                ok(dims_ok, "ST-EMBED stored vectors carry the native dimension")
                c2_ = sqlite3.connect(emb_path("nomic", ed))
                c2_.execute("UPDATE intent_meta SET value='x' WHERE key='text_set_sha256'")
                c2_.commit()
                c2_.close()
                o, err, _r = _cap(lambda: main(["--embed", "nomic", "--limit", "80", "--go", "--db", db, "--emb-dir", ed]))
                ok(err is not None and "intent_meta mismatch" in err, "ST-EMBED a meta mismatch REFUSES the resume")
                c2_ = sqlite3.connect(emb_path("nomic", ed))
                c2_.execute("UPDATE intent_meta SET value=? WHERE key='text_set_sha256'", (text_set(CS)[1],))
                c2_.commit()
                c2_.close()
                globals()["_foreign_heavy"] = lambda: ['"java.exe","1234"']
                o, err, _r = _cap(lambda: main(["--embed", "gemma", "--limit", "5", "--go", "--db", db, "--emb-dir", ed]))
                ok(err is not None and "foreign heavy" in err and not os.path.exists(emb_path("gemma", ed)), "ST-EMBED a running java.exe REFUSES --go before any post")
                globals()["_foreign_heavy"] = lambda: []
                gp = os.path.join(rec, RECORD_CACHE["gemma"])       # ONE of the 20 parity rows diverges (min fails, median passes)
                first = sorted(["rec %d" % j for j in range(25)], key=lambda t: hashlib.sha256(t.encode()).hexdigest())[0]
                gc = sqlite3.connect(gp)
                gc.execute("UPDATE embeddings SET vector=? WHERE query=?", (np.asarray(EA._stub_vec(first, 768, "x"), dtype=">f4").tobytes(), first))
                gc.commit()
                gc.close()
                o, err, _r = _cap(lambda: main(["--embed", "gemma", "--limit", "5", "--go", "--db", db, "--emb-dir", ed]))
                ok(err is not None and "route parity gemma" in err and not os.path.exists(emb_path("gemma", ed)),
                   "ST-EMBED ONE diverging parity row of 20 REFUSES (the bar is on the min); nothing written")
                gc = sqlite3.connect(gp)
                gc.execute("UPDATE embeddings SET vector=? WHERE query=?", (np.asarray(EA._stub_vec(first, 768), dtype=">f4").tobytes(), first))
                gc.commit()
                gc.close()
                for bad in (os.path.join(ROOT, "experiment_results"), ):
                    o, err, _r = _cap(lambda: main(["--embed", "gemma", "--db", db, "--emb-dir", bad]))
                    ok(err is not None and "experiment_results" in err, "ST-EMBED an --emb-dir under experiment_results/ REFUSES")
                try:
                    check_emb_target(os.path.join(rec, "embeddings_cache.db"))
                    ok(False, "ST-EMBED the cache of record is refused as a target")
                except SystemExit:
                    ok(True, "ST-EMBED the cache of record is refused as a target")
                # transient connection error: the whole batch is retried on the SAME client route (EMB-CONN)
                sleeps = []
                saved_sleep = EA._sleep
                EA._sleep = lambda s: sleeps.append(s)
                first_k = len(log)
                state["fault"] = lambda k: "port" if k == first_k + 1 else None      # request 0 = parity, 1 = the first batch
                try:
                    o, err, _r = _cap(lambda: main(["--embed", "qwen3", "--limit", "33", "--go", "--db", db, "--emb-dir", ed]))
                finally:
                    EA._sleep = saved_sleep
                    state["fault"] = None
                ok(err is None and sleeps == [2.0] and present_texts(emb_path("qwen3", ed)) == set(texts[:33]) and "pacing:" not in o,
                   "ST-EMBED a transient 'Only one usage of each socket address' is retried whole (backoff %s) and the run completes; "
                   "no pacing flag: no pause, no drain" % sleeps)
                # EMB-PACE: the incident's WSAENOBUFS 400 on a batch, with both pacing flags, RESUMES the same file (same pins)
                sleeps, probes = [], []
                saved_tw = EA._tw_count
                EA._sleep = lambda s: sleeps.append(s)
                EA._tw_count = lambda: (probes.append(1), 4000 if len(probes) == 1 else 10)[1]
                first_k = len(log)
                state["fault"] = lambda k: "nobufs" if k == first_k + 1 else None
                try:
                    o, err, _r = _cap(lambda: main(["--embed", "qwen3", "--limit", "70", "--go", "--pace-s", "0.25", "--tw-drain", "1500",
                                                    "--db", db, "--emb-dir", ed]))
                finally:
                    EA._sleep, EA._tw_count = saved_sleep, saved_tw
                    state["fault"] = None
                ok(err is None and "present 33" in o and present_texts(emb_path("qwen3", ed)) == set(texts[:70])
                   and sleeps == [2.0, EA.TW_POLL_S, 0.25, 0.25] and len(probes) == 2 and "pacing: pause 0.25 s" in o
                   and (EA.PACE_S, EA.TW_DRAIN) == (0.0, None),
                   "ST-EMBED EMB-PACE: WSAENOBUFS retried whole, TIME_WAIT drained (4000 -> 10 < 1500), a 0.25 s pause after each of "
                   "the 2 batches, the file RESUMED 33 -> 70 under the same pins; the pacing values restored (sleeps %s)" % sleeps)
                o, err, _r = _cap(lambda: main(["--dry-run", "--pace-s", "1", "--db", db, "--emb-dir", ed]))
                ok(err is not None and "--embed only" in err, "ST-EMBED --pace-s without --embed REFUSES")
                c3_ = sqlite3.connect(emb_path("qwen3", ed))
                c3_.execute("UPDATE intent_meta SET value='c5346ce29d55202ee4d4fdb068a3aca2c5563215' WHERE key='script_blob_lf'")
                c3_.commit()
                c3_.close()
                o, err, _r = _cap(lambda: main(["--embed", "qwen3", "--limit", "80", "--go", "--db", db, "--emb-dir", ed]))
                ok(err is not None and "intent_meta mismatch on ['script_blob_lf']" in err and "discarded (moved aside), never resumed" in err
                   and present_texts(emb_path("qwen3", ed)) == set(texts[:70]),
                   "ST-EMBED a partial file started under the PREVIOUS script blob (c5346ce2) REFUSES to resume; nothing written")
                c3_ = sqlite3.connect(emb_path("qwen3", ed))
                c3_.execute("UPDATE intent_meta SET value=? WHERE key='script_blob_lf'", (blob_lf(os.path.abspath(__file__)),))
                c3_.commit()
                c3_.close()
                # the dry-run: transport preflight + timed probe; writes nothing
                before = sorted(os.listdir(ed))
                o, err, _r = _cap(lambda: main(["--dry-run", "--db", db, "--emb-dir", ed, "--probe-n", "64"]))
                ok(err is None and "TRANSPORT PREFLIGHT PASSED (3 of 3 embedders)" in o and sorted(os.listdir(ed)) == before,
                   "ST-DRY --dry-run passes the transport preflight on the stub and writes nothing (%s)" % (err or "")[:200])
                ok(("Ollama endpoint %s" % url) in o, "ST-DRY C-6: the dry-run prints the resolved Ollama endpoint")
                pr = _line(o, "[INTENT-S0] PRICE qwen3")
                ok(("timed probe 64 texts" in pr) and ("-> %d texts to embed" % (len(texts) - 70)) in pr and "PRICE total" in o,
                   "ST-DRY the timed probe prices the MISSING texts per embedder (qwen3: %d)" % (len(texts) - 70))
                ok(("DENOMINATORS clinc: EVAL %d" % len(CS["clinc"].idx(SS.EVAL))) in o and "C2: OOS EVAL n %d" % len(CS["clinc"].idx(SS.EVAL, oos=True)) in o
                   and "text set %d texts" % len(texts) in o, "ST-DRY every denominator and the text-set count printed")
                state["salt"] = "other-route"
                o, err, _r = _cap(lambda: main(["--dry-run", "--db", db, "--emb-dir", ed, "--probe-n", "8"]))
                ok(err is not None and "route parity" in err, "ST-DRY a transport parity FAIL REFUSES the dry-run")
                state["salt"] = ""
                o, err, _r = _cap(lambda: main(["--dry-run", "--db", db, "--emb-dir", ed, "--skip-transport"]))
                ok(err is None and "TRANSPORT PREFLIGHT NOT RUN" in o and "does NOT clear" in o, "ST-DRY --skip-transport says the precondition is not cleared")
            finally:
                globals()["DATA_ROOT"] = saved_root
                EA.OLLAMA_URL = "http://127.0.0.1:9/api/embed"
    print("%s SELFTEST PASSED (%d checks)" % (TAG, n[0]))
    return 0


_E2E = [None]

# ------------------------------------------------------------------------------------------------ mutants (source edits, each must fail a selftest)
MUTANTS = (
    ("C1 WORSE without the CI clause", "    if D < -bar and hi < 0:\n", "    if D < -bar:\n", ("ST-STATS",)),
    ("C1 WORSE at <= -bar", "    if D < -bar and hi < 0:\n", "    if D <= -bar and hi < 0:\n", ("ST-STATS",)),
    ("C1 bar = MDE only (spread dropped)", "        bar = max(2.8 * se, max(spread[\"qwen3\"], spread[e]))\n", "        bar = 2.8 * se\n", ("ST-E2E",)),
    ("C1 spread min<->max", "    spread = {e: float(max(nm[e]) - min(nm[e])) for e in EMBEDDERS}\n", "    spread = {e: float(min(nm[e]) - max(nm[e])) for e in EMBEDDERS}\n", ("ST-E2E",)),
    ("C1 D sign flipped", "    D = {e: float(np.mean(nm[e]) - np.mean(nm[\"qwen3\"])) for e in FAMILIES}\n",
     "    D = {e: float(np.mean(nm[\"qwen3\"]) - np.mean(nm[e])) for e in FAMILIES}\n", ("ST-E2E",)),
    ("C1 D from seed 0 only", "    D = {e: float(np.mean(nm[e]) - np.mean(nm[\"qwen3\"])) for e in FAMILIES}\n",
     "    D = {e: float(nm[e][0] - nm[\"qwen3\"][0]) for e in FAMILIES}\n", ("ST-E2E",)),
    ("C1a needs 3 of 3", "    c1a = \"HELD\" if len(alt) >= 2 else \"FAILED\"\n", "    c1a = \"HELD\" if len(alt) >= 3 else \"FAILED\"\n", ("ST-VERDICT",)),
    ("C1a per family (the superseded reading)", "    c1a = \"HELD\" if len(alt) >= 2 else \"FAILED\"\n",
     "    c1a = \"HELD\" if any(len(v) >= 2 for v in fine_worse.values()) else \"FAILED\"\n", ("ST-VERDICT",)),
    ("C1a first two corpora only", "    alt = [c for c in CORPORA if any(st.get((c, \"fine\", e)) == \"WORSE\" for e in FAMILIES)]\n",
     "    alt = [c for c in CORPORA[:2] if any(st.get((c, \"fine\", e)) == \"WORSE\" for e in FAMILIES)]\n", ("ST-VERDICT",)),
    ("C1a first family only", "    alt = [c for c in CORPORA if any(st.get((c, \"fine\", e)) == \"WORSE\" for e in FAMILIES)]\n",
     "    alt = [c for c in CORPORA if any(st.get((c, \"fine\", e)) == \"WORSE\" for e in FAMILIES[:1])]\n", ("ST-VERDICT",)),
    ("C1 percentile interval decides (C-1 undone)", "        lo, hi = basic_ci(D[e], draws[e])                        # C-1 / C-2: the BASIC interval decides\n",
     "        lo, hi = plo, phi\n", ("ST-E2E",)),
    ("C1 basic interval flipped", "    return 2 * point - qhi, 2 * point - qlo", "    return 2 * point - qlo, 2 * point - qhi", ("ST-E2E",)),
    ("RV-2 C1 bootstrap unpaired", "        m = {e: np.mean([nmi(truth, p, w) for p in preds[e]]) for e in EMBEDDERS}\n",
     "        m = {e: np.mean([nmi(truth, p, w if e == \"qwen3\" else np.roll(w, 1)) for p in preds[e]]) for e in EMBEDDERS}\n", ("ST-E2E",)),
    ("RV-4 C2 CI ignores the OOS resample", "        draws.append(auroc(si, so, wi, wo))\n", "        draws.append(auroc(si, so, wi, None))\n", ("ST-E2E",)),
    ("RV-5 C3 decided at seed 4", "        if s == 0:\n            main = (cells, use, rho, Cm0)\n", "        if s == 4:\n            main = (cells, use, rho, Cm0)\n", ("ST-E2E",)),
    ("RV-6 C4 decided at seed 4", "        if s == 0:\n            same0, Cm0 = same, Cm\n", "        if s == 4:\n            same0, Cm0 = same, Cm\n", ("ST-E2E",)),
    ("C-7 HM in the swapped order", "           \"draws\": draws, \"hm_se\": hanley_mcneil(A, n2, n1),", "           \"draws\": draws, \"hm_se\": hanley_mcneil(A, n1, n2),", ("ST-E2E",)),
    ("C-7 HM formula pairs Q1 with n_neg", "(n_pos - 1) * (q1 - A * A) + (n_neg - 1) * (q2 - A * A)", "(n_neg - 1) * (q1 - A * A) + (n_pos - 1) * (q2 - A * A)", ("ST-STATS",)),
    ("C-8 raw pin mismatch admitted", "        if want and want != sha:\n", "        if False:\n", ("ST-REFUSE",)),
    ("C-8 null raw pin admitted by --run", "        if strict and not want:\n            refuse(\"raw %s is UNPINNED", "        if False:\n            refuse(\"raw %s is UNPINNED", ("ST-REFUSE",)),
    ("C-8 raw pins never checked", "    raw_pin_check(db, strict)\n", "", ("ST-REFUSE",)),
    ("C-8 annot/text mismatch kept", "            cnt[\"annot_text_mismatch\"] += 1                       # C-8: EXCLUDED (the variant would not be a swap of the text)\n            continue\n",
     "            cnt[\"annot_text_mismatch\"] += 1                       # C-8: EXCLUDED (the variant would not be a swap of the text)\n", ("ST-DERIVED",)),
    ("B7 swapped types not recorded", "                changed.append(t)\n", "                changed.append(\"?\")\n", ("ST-DERIVED",)),
    ("C-6 URL not printed in the dry run", "    print(\"%s heavy foreign processes: %s\" % (TAG, heavy if heavy else \"none\"))\n    print(\"%s Ollama endpoint",
     "    print(\"%s heavy foreign processes: %s\" % (TAG, heavy if heavy else \"none\"))\n    (\"%s Ollama endpoint", ("ST-EMBED",)),
    ("C1b first family only", "    coarse_worse = [(c, e) for c in (\"massive\", \"clinc\") for e in FAMILIES if",
     "    coarse_worse = [(c, e) for c in (\"massive\", \"clinc\") for e in FAMILIES[:1] if", ("ST-VERDICT",)),
    ("C1 NMI on TRAIN rows", "    ev = S_idx(C, spaces[\"qwen3\"], SS.EVAL)\n    for e in EMBEDDERS:", "    ev = S_idx(C, spaces[\"qwen3\"], SS.TRAIN)\n    for e in EMBEDDERS:", ("ST-E2E",)),
    ("fit on EVAL (k-means)", "    tr = fit_rows(C, S_idx(C, S, SS.TRAIN), (SS.TRAIN,), what)\n", "    tr = fit_rows(C, S_idx(C, S, SS.EVAL), (SS.TRAIN,), what)\n", ("ST-E2E",)),
    ("fit guard admits every side", "    bad = sides - set(allowed)\n", "    bad = set()\n", ("ST-DERIVED",)),
    ("fit guard ignores OOS", "    if bad or n_oos or n_drop:\n", "    if bad or n_drop:\n", ("ST-DERIVED",)),
    ("fit guard ignores dropped rows", "    if bad or n_oos or n_drop:\n", "    if bad or n_oos:\n", ("ST-DERIVED",)),
    ("OOS rows counted as in-scope (idx oos flag ignored)", "        m = self.kept & (self.side == side) & (self.oos == oos)\n",
     "        m = self.kept & (self.side == side)\n", ("ST-E2E",)),
    ("C2 threshold on EVAL instead of GATE", "    ev_in, ev_oos, gate = S_idx(C, S, SS.EVAL), S_idx(C, S, SS.EVAL, oos=True), S_idx(C, S, SS.GATE)\n",
     "    ev_in, ev_oos, gate = S_idx(C, S, SS.EVAL), S_idx(C, S, SS.EVAL, oos=True), S_idx(C, S, SS.EVAL)\n", ("ST-E2E",)),
    ("C2 threshold quantile 0.95 (TPR 5%)", "    thr = float(np.sort(sg)[int(np.floor((1 - TPR_TARGET) * len(sg)))])",
     "    thr = float(np.sort(sg)[int(np.floor(TPR_TARGET * len(sg)))])", ("ST-E2E",)),
    ("C2 HELD at lower > bar only", "    if lo >= bar:\n        return \"HELD\"\n", "    if lo > bar:\n        return \"HELD\"\n", ("ST-STATS",)),
    ("C2 FAILED at upper <= bar", "    if hi < bar:\n        return \"FAILED\"\n", "    if hi <= bar:\n        return \"FAILED\"\n", ("ST-STATS",)),
    ("C2 decided on the seed mean", "    A = per_seed[0]\n", "    A = float(np.mean(per_seed))\n", ("ST-E2E",)),
    ("C2 positives and negatives swapped", "        A = auroc(si, so)\n", "        A = auroc(so, si)\n", ("ST-E2E",)),
    ("auroc ties counted as wins", "    return float((Wp * (below + 0.5 * Wn)).sum() / den) if den > 0 else float(\"nan\")",
     "    return float((Wp * (below + 1.0 * Wn)).sum() / den) if den > 0 else float(\"nan\")", ("ST-STATS",)),
    ("C3 purity on TRAIN", "    ev = S_idx(C, S, SS.EVAL)\n    evc = assign(S.X[ev], Cm)\n", "    ev = S_idx(C, S, SS.TRAIN)\n    evc = assign(S.X[ev], Cm)\n", ("ST-E2E",)),
    ("C3 margin = own cos only", "    marg = top2[:, 1] - top2[:, 0]\n", "    marg = top2[:, 1]\n", ("ST-E2E",)),
    ("C3 min-EVAL filter dropped", "        use = [r for r in cells if r[\"n_eval\"] >= C3_MIN_EVAL and np.isfinite(r[\"margin\"])]\n",
     "        use = [r for r in cells if np.isfinite(r[\"margin\"])]\n", ("ST-E2E",)),
    ("C3 HELD on 1 of 3", "    if len(pos) >= 2:\n        return \"HELD\", pos, nonpos\n", "    if len(pos) >= 1:\n        return \"HELD\", pos, nonpos\n", ("ST-VERDICT",)),
    ("C3 positive at lower >= 0", "res[c][\"lo\"] > 0]\n", "res[c][\"lo\"] >= 0]\n", ("ST-VERDICT",)),
    ("C3 non-positive at upper < 0", "res[c][\"hi\"] <= 0]\n", "res[c][\"hi\"] < 0]\n", ("ST-VERDICT",)),
    ("C4 S over all EVAL (denominator)", "    return {\"S\": float(same0.mean()),", "    return {\"S\": float(same0.sum() / max(1, len(S_idx(C, S, SS.EVAL)))),", ("ST-E2E",)),
    ("C4 variant from another intent", "            cands = sorted(x for x in inv.get((C.fine[i], t), ()) if SS.norm(x) != SS.norm(v))\n",
     "            cands = sorted(x for (f_, t_), vs in inv.items() if t_ == t for x in vs if SS.norm(x) != SS.norm(v))\n", ("ST-DERIVED",)),
    ("C4 TRAIN collision kept", "        if sk in train_keys:\n", "        if False:\n", ("ST-DERIVED",)),
    ("C4 inventory from EVAL", "    tr = fit_rows(C, C.idx(SS.TRAIN), (SS.TRAIN,), \"C4 slot inventory\")\n",
     "    tr = fit_rows(C, C.idx(SS.EVAL), (SS.TRAIN,), \"C4 slot inventory\")\n", ("ST-DERIVED",)),
    ("F-lines: F2 fires on HELD", "           (\"F2\", V[\"C2\"] == \"FAILED\",", "           (\"F2\", V[\"C2\"] == \"HELD\",", ("ST-VERDICT",)),
    ("F4 line never printed", "    for fid, fired, text in fal:\n", "    for fid, fired, text in fal[:4]:\n", ("ST-VERDICT",)),
    ("pilot: a Skip line omitted", "            R[\"skipped\"].append(\"%s: SKIPPED (%s)\" % (name, ex))\n            return None\n        except (",
     "            return None\n        except (", ("ST-PILOT",)),
    ("pilot: verdicts printed despite a skipped readout",
     "        L.append(\"PILOT: a deciding readout was SKIPPED on the pilot's rows; no verdict is printed\")\n        L += [s for s in R[\"skipped\"]]\n        V = None\n",
     "        V = None\n", ("ST-PILOT",)),
    ("a --run readout Skip tolerated", "            if not pilot:\n                refuse(\"readout %s cannot run", "            if False:\n                refuse(\"readout %s cannot run",
     ("ST-PILOT",)),
    ("missing vectors tolerated by --run", "    if miss and not allow_missing:\n", "    if False:\n", ("ST-PILOT",)),
    ("R-1 on the mean SE bound 0.0112", "R1_SE, R1_SPREAD = 0.020 / 2.8, 0.020 ", "R1_SE, R1_SPREAD = 0.0112, 0.020 ", ("ST-VERDICT",)),
    ("R-1 spread from nomic only", "        se, sp = r[\"per\"][\"nomic\"][\"se\"], max(r[\"spread\"][\"qwen3\"], r[\"spread\"][\"nomic\"])\n",
     "        se, sp = r[\"per\"][\"nomic\"][\"se\"], r[\"spread\"][\"nomic\"]\n", ("ST-VERDICT",)),
    ("R-1 strict at the bound", "(se <= R1_SE and sp <= R1_SPREAD)", "(se < R1_SE and sp < R1_SPREAD)", ("ST-VERDICT",)),
    ("prediction interval open at the ends", "    return \"HELD\" if (isinstance(v, float) and np.isfinite(v) and lo <= v <= hi) else \"FAILED\"",
     "    return \"HELD\" if (isinstance(v, float) and np.isfinite(v) and lo < v < hi) else \"FAILED\"", ("ST-STATS",)),
    ("outcome not write-once", "    if not pilot and os.path.lexists(path):\n", "    if False:\n", ("ST-E2E",)),
    ("pilot writes the file of record", "    sfx = \"_PILOT\" if pilot else \"\"\n", "    sfx = \"\"\n", ("ST-E2E",)),
    ("null pin admitted by --run", "    if strict and not want:\n        refuse(\"%s is UNPINNED", "    if False:\n        refuse(\"%s is UNPINNED", ("ST-REFUSE",)),
    ("pin mismatch admitted", "    if want and want != s:\n        refuse(\"%s sha256 %s != the pinned", "    if False:\n        refuse(\"%s sha256 %s != the pinned", ("ST-REFUSE",)),
    ("census 5% unchecked", "    if off and not bracket and not pilot:\n", "    if False:\n", ("ST-REFUSE",)),
    ("census tolerance 10%", "CENSUS_TOL = 0.05\n", "CENSUS_TOL = 0.10\n", ("ST-REFUSE",)),
    ("embed ignores --go", "    if not go:\n        print(\"%s dry: nothing posted, nothing written (add --go)\" % TAG)\n        return 0\n    print(\"%s Ollama endpoint",
     "    print(\"%s Ollama endpoint", ("ST-EMBED",)),
    ("embed parity skipped", "    route_parity(e, embed_fn)\n    digest", "    digest", ("ST-EMBED",)),
    ("PACE flags not applied", "            EA.PACE_S = a.pace_s if a.pace_s is not None else EA.PACE_S\n", "", ("ST-EMBED",)),
    ("PACE values not restored", "            EA.PACE_S, EA.TW_DRAIN = saved_pace\n", "            pass\n", ("ST-EMBED",)),
    ("PACE flag admitted outside --embed", "        refuse(\"--pace-s / --tw-drain are admitted with --embed only\")", "        pass", ("ST-EMBED",)),
    ("parity on the median", "    mn = min(cos)\n", "    mn = float(np.median(cos))\n", ("ST-EMBED",)),
    ("qwen3 parity bar back to 0.9999", "PARITY_BAR = {\"qwen3\": 0.998,", "PARITY_BAR = {\"qwen3\": 0.9999,", ("ST-EMBED",)),
    ("qwen3 parity bar loosened to 0.99", "PARITY_BAR = {\"qwen3\": 0.998,", "PARITY_BAR = {\"qwen3\": 0.99,", ("ST-EMBED",)),
    ("nomic parity bar at qwen3's 0.998", "\"nomic\": 0.9999, \"gemma\": 0.9999}", "\"nomic\": 0.998, \"gemma\": 0.9999}", ("ST-EMBED",)),
    ("gemma parity bar at qwen3's 0.998", "\"nomic\": 0.9999, \"gemma\": 0.9999}", "\"nomic\": 0.9999, \"gemma\": 0.998}", ("ST-EMBED",)),
    ("one bar for every embedder", "    bar = PARITY_BAR[e] if bar is None else bar\n", "    bar = PARITY_BAR[\"qwen3\"] if bar is None else bar\n", ("ST-EMBED",)),
    ("heavy-process check skipped", "    if heavy:\n        refuse(\"a foreign heavy", "    if False:\n        refuse(\"a foreign heavy", ("ST-EMBED",)),
    ("meta mismatch admitted", "    if bad:\n        refuse(\"%s intent_meta mismatch", "    if False:\n        refuse(\"%s intent_meta mismatch", ("ST-EMBED",)),
    ("--limit ignores the sha order", "    todo = miss if limit is None else [t for t in texts[:int(limit)] if t not in have]\n",
     "    todo = miss if limit is None else sorted(miss)[:int(limit)]\n", ("ST-EMBED",)),
    ("experiment_results admitted as --emb-dir", "        refuse(\"--emb-dir %s is under experiment_results/", "        print(\"--emb-dir %s is under experiment_results/", ("ST-EMBED",)),
    ("dry-run skips the preflight", "        for e in EMBEDDERS:\n            route_parity(e, embed_fn)\n", "        for e in EMBEDDERS:\n            pass\n", ("ST-EMBED",)),
    ("probe prices the whole set", "            rate = timed_probe(e, texts, embed_fn, n=probe_n, n_total=todo[e])\n",
     "            rate = timed_probe(e, texts, embed_fn, n=probe_n)\n", ("ST-EMBED",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head, tail = src[:cut] + src[end:], ""          # EMB-PACE: main() is mutable too; the table itself is not
    with fixture_scope():
        td = tempfile.mkdtemp(prefix="intent_s0_mut_")
        fx = build_fixture(td)[0]
    killed = 0
    rows = []
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "intent_s0_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(head.replace(old, new) + tail, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        killed += res.startswith("KILLED")
        rows.append((name, res))
        print("  %-48s %s" % (name, res))
    import shutil
    shutil.rmtree(td, ignore_errors=True)            # the fixture (~80-400 MB of synthetic vectors) lives in the system temp dir
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTENT-TRANSFER stage 0 readouts (zero judge calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--embed", choices=EMBEDDERS)
    g.add_argument("--run", action="store_true")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--census-bracket", default=None)
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--probe-n", type=int, default=PROBE_N)
    ap.add_argument("--skip-transport", action="store_true")
    ap.add_argument("--pace-s", type=float, default=None, help="--embed only: pause S seconds after each committed batch")
    ap.add_argument("--tw-drain", type=int, default=None, help="--embed only: after a transient error, wait for TIME_WAIT < N")
    a = ap.parse_args(argv)
    if (a.pace_s is not None or a.tw_drain is not None) and not a.embed:
        refuse("--pace-s / --tw-drain are admitted with --embed only")
    if (a.pace_s is not None and not a.pace_s > 0) or (a.tw_drain is not None and a.tw_drain < 1):
        refuse("--pace-s must be > 0 and --tw-drain >= 1 (got %r / %r)" % (a.pace_s, a.tw_drain))
    if a.go and not a.embed:
        refuse("--go is admitted with --embed only")
    if a.pilot and not a.run:
        refuse("--pilot is admitted with --run only")
    db = a.db or II.DEFAULT_OUT
    emb_dir = a.emb_dir or DATA_ROOT
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(db, emb_dir, skip_transport=a.skip_transport, probe_n=a.probe_n)
    if a.embed:
        saved_pace = (EA.PACE_S, EA.TW_DRAIN)
        if a.pace_s is not None or a.tw_drain is not None:
            EA.PACE_S = a.pace_s if a.pace_s is not None else EA.PACE_S
            EA.TW_DRAIN = a.tw_drain if a.tw_drain is not None else EA.TW_DRAIN
            print("%s pacing: pause %s s after each batch; TIME_WAIT drain threshold %s (poll %.0f s, cap %.0f s)"
                  % (TAG, EA.PACE_S or "none", EA.TW_DRAIN, EA.TW_POLL_S, EA.TW_MAX_S))
        try:
            embed(a.embed, a.go, limit=a.limit, emb_dir=emb_dir, db=db)
        finally:
            EA.PACE_S, EA.TW_DRAIN = saved_pace
        return 0
    R, V, path = main_run(a.pilot, a.census_bracket, db, emb_dir, a.out_dir)
    _E2E[0] = (R, V, path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
