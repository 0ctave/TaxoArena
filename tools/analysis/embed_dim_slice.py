"""EMBED-DIM-SLICE: on S0's pinned intent corpora and embeddings, is S0's "gemma beats qwen3 at the fine level" (C1a, 2 of 3
corpora; SLOTSWAP M3) an artefact of the 256-d slice, which keeps 6% of qwen3's 4096 dims and 33% of gemma's 768?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — EMBED-DIM-SLICE: on S0's pinned
intent corpora and embeddings, is S0's "gemma beats qwen3 at the fine level" ...", span L22579-L22607 _as_of 46954215 (registered "as
written" from the draft docs/agents/plans/2026-10-02_embed_dim_slice.md a5c88533 in the registrar's commit 6983d397). Built to the
draft and checked against the committed text (no deviation found). --run REFUSES unless the programme carries the heading (REG_NEEDLE).
Kind: zero-call CPU reader. Zero judge calls, zero
embeddings, no build, no Ollama process, no pool of record, no embeddings_cache*.db.

INSTRUMENT (imported, never copied): tools/analysis/intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271, its LF
blob asserted at every entry point (any other blob REFUSES). Its frozen readers do every read and every fit: pin_check /
raw_pin_check (experiment_configs/intent_transfer_s0_pins.json; --run strict), load_corpora, text_set, check_meta / expected_meta,
load_vectors (run with ITS.SLICE2 set to the native width for the duration of the call, restored in a finally: S0's reader reads the
first SLICE2 coordinates, so this is the same reader at full width; the first 512 coordinates are asserted equal to S0's own call by
the selftest), Space (first d coordinates, then L2-renormalised: S0's slice rule), km_fit (spherical k-means, k-means++, n_init 1,
max_iter 300, seeds 0-4, TRAIN fit through fit_rows, the TRAIN-ONLY guard), assign (nearest centroid), nmi (arithmetic),
comp_weights (CK-CLOSE component bootstrap, B 2,000), basic_ci / pct_ci, c1_status (S0's C1 rule verbatim), kish, d2 (D2's H and its
size-matched random p95) and c4 (SLOTSWAP's S, called for the identity).

ARMS: qwen3 at d in {256, 512, 1024, 4096}; gemma at d in {256, 768}. Corpora MASSIVE (K_f 60, K_c 18), CLINC in-scope (150, 10),
Banking77 (77).

ORDER (the R3 pattern; shown by execution, EVENTS):
  phase A  every fit on TRAIN (fine and coarse, 6 arms x seeds 0-4), GATE filed to those TRAIN centroids, GATE fine NMI; DS4's H
           (TRAIN only). No EVAL row is touched: every EVAL index goes through eval_idx(), which REFUSES before the selection file
           exists (the dry-run's identity alone is admitted, on S0's own 256 arms, EB7).
  select   per embedder d* = argmax_d of the mean over the 3 corpora of the seed-mean GATE fine NMI; ties within 0.001 to the smaller
           d (EB1). Per-corpus GATE maxima printed, never used. selection.json written mode "x" (deterministic content), its sha256
           printed; only then is EVAL opened.
  phase B  EVAL filed to the stored TRAIN centroids for every arm (read once), the slot-swap variants filed for S.
  identity IDENTITY PRECONDITION (refuses; no outcome is written): D(gemma - qwen3, fine, 256) per corpus reproduces S0's printed
           +0.03340 / -0.00691 / +0.05628 to 5 dp ("%+.5f"), and S at seed 0 reproduces 0.7598 (qwen3) / 0.8262 (gemma) to 4 dp
           ("%.4f"), the composed path AND S0's own c4() agreeing exactly. A failure leaves selection.json (not a readout) and
           writes nothing else; a re-run needs a fresh --out-dir (selection.json is write-once too).

READOUTS (the registered text; criteria_lines prints every branch, each executed by the selftest):
  DS1 (deciding) per corpus D* = mean_s NMI_EVAL(gemma, d_g*) - mean_s NMI_EVAL(qwen3, d_q*) at K_f. BETTER iff D* > bar AND the
      BASIC CI lower > 0; WORSE iff D* < -bar AND upper < 0; NEITHER otherwise (ITS.c1_status). bar = max(MDE80, max(spread_qwen3(d_q*),
      spread_gemma(d_g*))), MDE80 = 2.8 x the bootstrap SE of D*, spread = max - min over seeds 0-4 of that arm's EVAL NMI (in-run).
      VERDICT REOPEN-CANDIDATE iff gemma BETTER on >= 2 of 3; KEEP iff BETTER on <= 1; KEEP-STRONG iff gemma WORSE on >= 2 of 3 (a
      sub-case of KEEP). Total: no UNDETERMINED. F-DS fires iff REOPEN-CANDIDATE.
  DS2 (DESCRIPTIVE-ONLY) qwen3 NMI(d) - NMI(256) for d in {512, 1024, 4096} and gemma 768 - 256, per corpus, BASIC CI (paired, DS1's
      weight stream).
  DS3 (DESCRIPTIVE-ONLY) S(gemma, d_g*) - S(qwen3, d_q*) on MASSIVE at K 60, mean over seeds 0-4, component-bootstrap CI; the 6-arm S
      table beside.
  DS4 (DESCRIPTIVE-ONLY) H per arm on MASSIVE and CLINC (ITS.d2), with an item (component) bootstrap interval and the size-matched
      random p95.
  Printed, never deciding: the 6-arm x 3-corpus fine NMI matrix (EVAL and GATE), coarse NMI per arm, d_q* against the tree slice of
  record (512; a difference is RELAYED to the tree specialist), the predictions P1-P6 scored, support (n, components, Kish DEFF from
  the components, n_eff, SE, MDE80, bar; SCOREABLE / DESCRIPTIVE-ONLY at the predictions), the reading table's words for the branch.
  EVERY outcome line ends with the uncontrolled confounds (CONFOUNDS: quantisation Q4_K_M vs BF16; prompt protocol RAW).

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets):
  EB1 tie rule: d* = the smallest d whose GATE score is >= max - 0.001 (the boundary 0.001 itself is a tie).
  EB2 GATE = kept in-scope GATE rows (CLINC OOS excluded, as for EVAL), filed to the very TRAIN centroids that file EVAL.
  EB3 DS1 / DS2 bootstrap stream = S0's C1 stream for the corpus's fine level (BOOT_SEED + 10 x corpus index + level index), so at
      (256, 256) the D* interval is S0's own C1 interval.
  EB4 DS3 interval: percentile (S0 C4's and SLOTSWAP M3's convention), stream BOOT_SEED + 4 (c4's); BASIC printed beside.
  EB5 DS4 bootstrap: TRAIN components resampled (B 2,000, seed SEED_D2 + 100 + corpus index); a fine label with zero weight in a draw
      is dropped from that draw (counted); percentile interval.
  EB6 P6 "gemma H > qwen3 H on MASSIVE at every qwen3 slice": gemma read at d_g*.
  EB7 the --dry-run's identity reads EVAL of S0's own 256 arms only (numbers already of record); no EVAL row of a new arm is read
      before selection.json. In --run the identity is computed after the selection, from phase B.
  EB8 "on every outcome line": literally every line of outcome.txt carries CONFOUNDS.
  EB9 coarse NMI (printed) at K_c, seeds 0-4, EVAL.

HYGIENE: reads only intent_transfer_corpora_v1.db, intent_emb_qwen3.db, intent_emb_gemma.db (S0's pins, sha256-bytes, checked before
and after; a change REFUSES and nothing is written), mode=ro&immutable=1 through S0's readers. --dry-run and --run REFUSE while a
java.exe runs. Threads: OMP/OPENBLAS/MKL = 1 (before numpy). Memory: about 0.94 GB for the qwen3 vectors plus one corpus's 4096-d
float64 space at a time.

OUTPUT (experiment_results/embed_dim_slice/, every file write-once, mode "x"; an existing path REFUSES before any read):
  selection.json (written between phase A and B), outcome.txt (of record), nmi_matrix.csv, s_table.csv, h_table.csv.

LAUNCH (run-operator; zero calls; nothing else heavy running; CPU lane):
  python tools/analysis/embed_dim_slice.py --selftest
  python tools/analysis/embed_dim_slice.py --mutants
  python tools/analysis/embed_dim_slice.py --dry-run      # pins, census, GATE/EVAL counts, identity (256 arms), one timed 4096-d fit, price
  python tools/analysis/embed_dim_slice.py --run          # selection.json, then the file of record (write-once)
  (S0's DBs under TAXOARENA_DATA_ROOT, default the repo root; --db / --emb-dir / --out-dir override.)

MUTANT TABLE: see the commit message and `--mutants` (each mutant names the selftest sections that must kill it; 53 of 53 killed
at build, every refusal mutant by its own check, each refusal run on a fresh output directory so no state is shared between mutants).

BUILD-TIME DRY RUN on the pinned DBs (2026-10-01, the engine-coder; TAXOARENA_DATA_ROOT = the main checkout): every pin OK;
census TRAIN / GATE / EVAL massive 9,870 / 1,691 / 4,946 (4,923 components), clinc 13,487 / 2,333 / 6,672 (6,672), banking77
7,885 / 1,290 / 3,908 (3,905); 3,222 variants; IDENTITY REPRODUCED: D +0.03340 / -0.00691 / +0.05628, S 0.7598 / 0.8262 (S0's
c4() 0.759777 / 0.826195, equal to the composed S); 8 EVAL reads, all on the 256 arms; one qwen3@4096 CLINC fine fit 15.6 s, the
150 fits priced at ~230 s plus the bootstraps; 43 fits audited, 0 with an EVAL row. The registration heading read ABSENT there
only because the branch predates the registrar's 6983d397; --run refuses until it runs on a tree carrying that heading.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import csv             # noqa: E402
import hashlib         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
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

TAG = "[EMBED-DIM-SLICE]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
EMB = ("qwen3", "gemma")
SLICES = {"qwen3": (256, 512, 1024, 4096), "gemma": (256, 768)}
ARMS = tuple((e, d) for e in EMB for d in SLICES[e])
NATIVE = {"qwen3": 4096, "gemma": 768}
BASE = 256
TIE = 0.001
TREE_SLICE = 512
SEEDS = ITS.SEEDS
BOOT_B = ITS.BOOT_B
BOOT_SEED = ITS.BOOT_SEED
SEED_H = ITS.SEED_D2 + 100
CORPORA = ITS.CORPORA
LEVELS = ITS.LEVELS
H_CORPORA = ("massive", "clinc")
IDENTITY = {"D": {"massive": "+0.03340", "clinc": "-0.00691", "banking77": "+0.05628"}, "S": {"qwen3": "0.7598", "gemma": "0.8262"}}
CONFOUNDS = "[UNCONTROLLED: quantisation qwen3 Q4_K_M vs gemma BF16; prompt protocol RAW on both sides]"
PLAN_SE = {"massive": 0.00289, "clinc": 0.00137, "banking77": 0.00247}
PLAN_BAR = {"massive": 0.0246, "clinc": 0.0094, "banking77": 0.0143}
PLAN_DEFF = {"massive": 1.0093, "clinc": 1.0000, "banking77": 1.0015}
DS3_SPREAD = 0.0335                       # SLOTSWAP M3's seed spread (planning bar; DS3 is descriptive)
PLAN_DS3_SE = 0.0078
# The registered predictions (80% intervals; probabilities scored with a Brier).
P1 = (("d_q* in {1024, 4096}", 0.55), ("d_q* = 512", 0.30), ("d_q* = 256", 0.15), ("d_g* = 768", 0.75))
P2 = (0.010, 0.000, 0.025)
P3 = {"massive": (0.022, 0.005, 0.040), "clinc": (-0.012, -0.025, 0.002), "banking77": (0.045, 0.030, 0.060)}
P4 = (("KEEP", 0.55), ("KEEP-STRONG", 0.05), ("REOPEN-CANDIDATE", 0.45))
P5 = (0.055, 0.030, 0.080)
P6 = (("gemma H > qwen3 H on MASSIVE at every qwen3 slice", 0.85), ("qwen3 H non-decreasing in d on both corpora", 0.50))
OUT_DIR = os.path.join(ROOT, "experiment_results", "embed_dim_slice")
SELECTION, OUTCOME = "selection.json", "outcome.txt"
CSVS = ("nmi_matrix.csv", "s_table.csv", "h_table.csv")
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_NEEDLE = "(before any code or call) \u2014 EMBED-DIM-SLICE:"
REG = ("docs/judge_v2_program.md \"## Registered 2026-10-01 (before any code or call) \u2014 EMBED-DIM-SLICE: ...\" L22579-L22607 "
       "_as_of 46954215 (registered as written in 6983d397 from a5c88533); kind zero-call CPU reader")
READINGS = ("builder's readings: EB1 d* = smallest d with GATE score >= max - 0.001; EB2 GATE = kept in-scope GATE rows on the TRAIN "
            "centroids that file EVAL; EB3 DS1/DS2 stream = S0's C1 fine stream; EB4 DS3 percentile CI, stream BOOT_SEED + 4, BASIC "
            "beside; EB5 DS4 TRAIN-component bootstrap, zero-weight labels dropped; EB6 P6 gemma at d_g*; EB7 the dry-run identity reads "
            "EVAL of S0's 256 arms only; EB8 every line carries the confounds; EB9 coarse NMI at K_c")
DOES_NOT_SHOW = ("DOES NOT SHOW: anything about quantisation (Q4_K_M vs BF16, uncontrolled) or prompts (RAW); anything about MMLU-Pro "
                 "or capability text (intent corpora only); embedder parity (no TOST; NEITHER is never parity); that the slice "
                 "'explains' the S0 edge when the deciding corpus reads NEITHER inside its seed-spread bar; that d_q* is the right slice "
                 "for trees (D1 measured certification; this measures fine NMI against gold); any change to the embedder of record (D3 "
                 "is the author's)")

EVENTS = []                                # ("SELECTION", sha) / ("EVAL", what): the order shown by execution
PHASE = {"selection_sha": None, "dry_identity": False}


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
    ok = os.path.isfile(programme) and REG_NEEDLE in open(programme, encoding="utf-8").read()
    print("%s registration heading %r in %s: %s" % (TAG, REG_NEEDLE, os.path.basename(programme), "PRESENT" if ok else "ABSENT"))
    return ok


def reset_phase():
    del EVENTS[:]
    PHASE["selection_sha"], PHASE["dry_identity"] = None, False


def eval_idx(C, S, what):
    """THE EVAL gate: every EVAL index of this script comes through here; before selection.json exists it REFUSES (the dry-run's
    identity alone may read S0's own 256 arms)."""
    if PHASE["selection_sha"] is None and not (PHASE["dry_identity"] and S.d == BASE):
        refuse("EVAL read (%s, d %d) before the GATE selection file is written and hashed" % (what, S.d))
    EVENTS.append(("EVAL", what))
    return ITS.S_idx(C, S, SS.EVAL)


# ------------------------------------------------------------------------------------------------ inputs
def load_full(path, e, texts):
    """S0's load_vectors at the native width (ITS.SLICE2 set for the call, restored in a finally)."""
    saved = ITS.SLICE2
    ITS.SLICE2 = NATIVE[e]
    try:
        v = ITS.load_vectors(path, e, texts)
    finally:
        ITS.SLICE2 = saved
    bad = sum(1 for x in v.values() if len(x) != NATIVE[e])
    if bad:
        refuse("%s: %d vectors are not %d-d after the full-width read" % (e, bad, NATIVE[e]))
    return v


def load_inputs(db, emb_dir, strict):
    sha0 = {"ingest_db": ITS.pin_check(db, "ingest_db", strict)}
    ITS.raw_pin_check(db, strict)
    for e in EMB:
        sha0[e] = ITS.pin_check(ITS.emb_path(e, emb_dir), "emb", strict, sub=e, label="intent_emb_%s.db" % e)
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    for e in EMB:
        ITS.check_meta(ITS.emb_path(e, emb_dir), ITS.expected_meta(e, set_sha, len(texts), sha0["ingest_db"]))
    return sha0, CS, texts, derived


def after_check(sha0, db, emb_dir):
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else ITS.emb_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))


def census(CS, derived):
    out = {}
    for c in CORPORA:
        C = CS[c]
        out[c] = {sd: int(len(C.idx(sd))) for sd in (SS.TRAIN, SS.GATE, SS.EVAL)}
        ev = C.idx(SS.EVAL)
        out[c]["eval_components"] = int(len(np.unique(C.comp[ev]))) if len(ev) else 0
        out[c]["eval_kish"] = ITS.kish(C.comp[ev]) if len(ev) else float("nan")
    out["variants"] = len(derived["variants"])
    return out


# ------------------------------------------------------------------------------------------------ phase A (TRAIN fits, GATE)
def h_boot(C, S, B, seed):
    """EB5: H on TRAIN-component bootstrap draws (weighted fine centroids, average-link cosine, cut at K_c, ARI vs the gold map)."""
    from scipy.cluster.hierarchy import linkage, fcluster
    import scipy.sparse as sps
    kc = II.GOLD_K[C.name][0]
    tr = ITS.fit_rows(C, ITS.S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "DS4 H bootstrap d%d" % S.d)
    lab = C.fine[tr].astype(str)
    u, inv = np.unique(lab, return_inverse=True)
    f2c = {}
    for i in tr:
        f2c[str(C.fine[i])] = C.coarse[i]
    gold = np.array([f2c[x] for x in u], dtype=object)
    X = S.X[tr]
    draws, dropped = [], 0
    rows = np.arange(len(tr))
    for w in ITS.comp_weights(C.comp[tr], B, np.random.default_rng(seed)):
        M = sps.csr_matrix((w, (inv, rows)), shape=(len(u), len(tr)))
        keep = np.bincount(inv, weights=w, minlength=len(u)) > 0
        dropped += int((~keep).sum())
        G = ITS.unit(np.asarray(M @ X)[keep])
        cut = fcluster(linkage(G, method="average", metric="cosine"), t=kc, criterion="maxclust")
        draws.append(ITS.ari(ITS.codes(gold[keep]), cut))
    lo, hi = ITS.pct_ci(draws)
    return {"lo": lo, "hi": hi, "dropped": dropped, "se": float(np.std(draws, ddof=1))}


def phase_a(CS, vecs):
    fits, gate, H = {}, {}, {}
    for c in CORPORA:
        C = CS[c]
        kc, kf = II.GOLD_K[c]
        for e, d in ARMS:
            S = ITS.Space(vecs[e], C, d)
            for g in LEVELS[c]:
                k = kf if g == "fine" else kc
                fits[(e, d, c, g)] = [ITS.km_fit(C, S, k, s, "EDS k-means %s@%d %s %s K=%d s%d" % (e, d, c, g, k, s)) for s in SEEDS]
            gi = ITS.S_idx(C, S, SS.GATE)
            truth = ITS.codes(C.fine[gi])
            gate[(e, d, c)] = [ITS.nmi(truth, ITS.assign(S.X[gi], Cm)) for Cm in fits[(e, d, c, "fine")]]
            gate[(e, d, c, "n")] = int(len(gi))
            if c in H_CORPORA:
                r = ITS.d2(C, S)
                r.update(h_boot(C, S, BOOT_B, SEED_H + CORPORA.index(c)))
                H[(e, d, c)] = r
            del S
    return fits, gate, H


def pick(score):
    """EB1: the smallest d whose score is >= max - TIE (the boundary itself is a tie)."""
    best = max(score.values())
    return min(d for d in sorted(score) if score[d] >= best - TIE), best


def select(gate):
    """EB1 / EB2: per embedder, d* = the smallest d whose GATE score (mean over corpora of the seed-mean GATE fine NMI) is within TIE of
    the maximum."""
    out = {}
    for e in EMB:
        score = {d: float(np.mean([np.mean(gate[(e, d, c)]) for c in CORPORA])) for d in SLICES[e]}
        dstar, best = pick(score)
        per = {c: max(SLICES[e], key=lambda d: (np.mean(gate[(e, d, c)]), -d)) for c in CORPORA}
        out[e] = {"d": dstar, "score": score, "best": best, "per_corpus_max": per}
    return out


def write_selection(path, sel, sha0, gate):
    doc = {"schema": "embed_dim_slice_selection/v1", "rule": "d* = smallest d with GATE score >= max - %.3f; GATE score = mean over "
           "corpora of the seed-mean GATE fine NMI on TRAIN centroids" % TIE, "script_blob_lf": RO.git_blob_lf(os.path.abspath(__file__)),
           "its_blob_lf": ITS_BLOB, "inputs_sha256": sha0, "d_q*": sel["qwen3"]["d"], "d_g*": sel["gemma"]["d"],
           "gate_score": {e: {str(d): round(v, 10) for d, v in sel[e]["score"].items()} for e in EMB},
           "per_corpus_gate_max_never_used": {e: sel[e]["per_corpus_max"] for e in EMB},
           "gate_nmi": {"%s@%d %s" % (e, d, c): [round(x, 10) for x in gate[(e, d, c)]] for e, d in ARMS for c in CORPORA}}
    data = (json.dumps(doc, sort_keys=True, indent=1) + "\n").encode("utf-8")
    with open(path, "xb") as f:
        f.write(data)
    sha = hashlib.sha256(data).hexdigest()
    PHASE["selection_sha"] = sha
    EVENTS.append(("SELECTION", sha))
    print("%s SELECTION written %s sha256 %s (d_q* %d, d_g* %d); EVAL is opened only now" % (TAG, path, sha, sel["qwen3"]["d"], sel["gemma"]["d"]))
    return sha


# ------------------------------------------------------------------------------------------------ phase B (EVAL, read once)
def phase_b(CS, vecs, derived, fits):
    ev_nmi, preds, truth, evrows, same, coarse = {}, {}, {}, {}, {}, {}
    var = derived["variants"]
    for c in CORPORA:
        C = CS[c]
        for e, d in ARMS:
            S = ITS.Space(vecs[e], C, d)
            ev = eval_idx(C, S, "phase B %s@%d %s" % (e, d, c))
            if c in evrows and not np.array_equal(evrows[c], ev):
                refuse("%s: the EVAL rows differ between arms (a vector missing)" % c)
            evrows[c] = ev
            for g in LEVELS[c]:
                t = ITS.codes(C.labels(g)[ev])
                p = [ITS.assign(S.X[ev], Cm) for Cm in fits[(e, d, c, g)]]
                nm = [ITS.nmi(t, q) for q in p]
                if g == "fine":
                    truth[c], preds[(e, d, c)], ev_nmi[(e, d, c)] = t, p, nm
                else:
                    coarse[(e, d, c)] = nm
            if c == "massive":
                v = [(i, tx) for i, tx, _c in var if S.have[i] and tx in S.vecs]
                if len(v) != len(var):
                    refuse("massive: %d of %d variants have a vector" % (len(v), len(var)))
                oi = np.array([i for i, _t in v], dtype=int)
                Xo, Xv = S.X[oi], S.of([tx for _i, tx in v])
                same[(e, d)] = [(ITS.assign(Xo, Cm) == ITS.assign(Xv, Cm)).astype(np.float64) for Cm in fits[(e, d, c, "fine")]]
            del S
    vcomp = CS["massive"].comp[np.array([i for i, _t, _c in var], dtype=int)] if var else np.array([], dtype=int)
    return {"ev_nmi": ev_nmi, "preds": preds, "truth": truth, "evrows": evrows, "same": same, "coarse": coarse, "vcomp": vcomp}


def identity_values(PB):
    D = {c: float(np.mean(PB["ev_nmi"][("gemma", BASE, c)]) - np.mean(PB["ev_nmi"][("qwen3", BASE, c)])) for c in CORPORA}
    S = {e: float(PB["same"][(e, BASE)][0].mean()) for e in EMB}
    return D, S


def identity_check(D, S, S_c4, target):
    """-> lines; REFUSES unless every value prints to the registered digits and the composed S equals S0's c4() S exactly."""
    got_D = {c: "%+.5f" % D[c] for c in CORPORA}
    got_S = {e: "%.4f" % S[e] for e in EMB}
    bad = [c for c in CORPORA if got_D[c] != target["D"][c]] + [e for e in EMB if got_S[e] != target["S"][e]]
    bad += ["c4(%s)" % e for e in EMB if S_c4[e] != S[e]]
    line = ("IDENTITY: D(gemma - qwen3, fine, 256) massive %s / clinc %s / banking77 %s (S0 printed %s / %s / %s); S seed 0 qwen3 %s / gemma "
            "%s (SLOTSWAP %s / %s); S0's c4() S %s" % (got_D["massive"], got_D["clinc"], got_D["banking77"], target["D"]["massive"],
                                                       target["D"]["clinc"], target["D"]["banking77"], got_S["qwen3"], got_S["gemma"],
                                                       target["S"]["qwen3"], target["S"]["gemma"],
                                                       {e: round(S_c4[e], 6) for e in EMB}))
    print("%s %s" % (TAG, line))
    if bad:
        refuse("IDENTITY PRECONDITION FAILED on %s: S0 is not reproduced to the printed digits (a different machinery); no readout is "
               "written" % bad)
    return [line + " -> REPRODUCED"]


def c4_identity(CS, vecs, derived):
    out = {}
    C = CS["massive"]
    for e in EMB:
        sp = ITS.Space(vecs[e], C, BASE)
        eval_idx(C, sp, "identity c4 %s@256" % e)
        out[e] = ITS.c4(C, {"qwen3": sp}, derived["variants"])["S"]
    return out


# ------------------------------------------------------------------------------------------------ readouts
def ds1(PB, c, dq, dg, B=None):
    """DS1 for one corpus (and DS2 on the same weight stream). EB3: S0's C1 stream for the corpus's fine level."""
    B = BOOT_B if B is None else B
    t = PB["truth"][c]
    comp = CS_COMP[c][PB["evrows"][c]]
    nm = {a: PB["ev_nmi"][a + (c,)] for a in ARMS}
    m = {a: float(np.mean(nm[a])) for a in ARMS}
    D = m[("gemma", dg)] - m[("qwen3", dq)]
    draws, curve = [], {a: [] for a in ARMS}
    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index("fine"))
    for w in ITS.comp_weights(comp, B, rng):
        mw = {a: float(np.mean([ITS.nmi(t, p, w) for p in PB["preds"][a + (c,)]])) for a in ARMS}
        draws.append(mw[("gemma", dg)] - mw[("qwen3", dq)])
        for e, d in ARMS:
            curve[(e, d)].append(mw[(e, d)] - mw[(e, BASE)])
    se = float(np.std(draws, ddof=1))
    lo, hi = ITS.basic_ci(D, draws)
    plo, phi = ITS.pct_ci(draws)
    spread = {a: float(max(nm[a]) - min(nm[a])) for a in ARMS}
    bar = max(2.8 * se, max(spread[("qwen3", dq)], spread[("gemma", dg)]))
    ds2 = {}
    for e, d in ARMS:
        if d == BASE:
            continue
        pt = m[(e, d)] - m[(e, BASE)]
        clo, chi = ITS.basic_ci(pt, curve[(e, d)])
        ds2[(e, d)] = {"d": pt, "lo": clo, "hi": chi, "se": float(np.std(curve[(e, d)], ddof=1))}
    return {"D": D, "lo": lo, "hi": hi, "plo": plo, "phi": phi, "se": se, "mde80": 2.8 * se, "spread": spread, "bar": bar,
            "status": ITS.c1_status(D, lo, hi, bar), "m": m, "n": int(len(t)), "components": int(len(np.unique(comp))),
            "kish": ITS.kish(comp), "ds2": ds2}


CS_COMP = {}


def verdict(status):
    """The registered 2-of-3 classification (total)."""
    nb = sum(1 for c in CORPORA if status[c] == "BETTER")
    nw = sum(1 for c in CORPORA if status[c] == "WORSE")
    if nb >= 2:
        return "REOPEN-CANDIDATE", nb, nw
    if nw >= 2:
        return "KEEP-STRONG", nb, nw
    return "KEEP", nb, nw


def ds3(PB, dq, dg, B=None):
    B = BOOT_B if B is None else B
    same, comp = PB["same"], PB["vcomp"]
    S = {a: float(np.mean([s.mean() for s in same[a]])) for a in ARMS}
    D = S[("gemma", dg)] - S[("qwen3", dq)]
    draws = []
    for w in ITS.comp_weights(comp, B, np.random.default_rng(BOOT_SEED + 4)):
        sw = w.sum()
        draws.append(float(np.mean([(w * s).sum() / sw for s in same[("gemma", dg)]]) - np.mean([(w * s).sum() / sw for s in same[("qwen3", dq)]])))
    lo, hi = ITS.pct_ci(draws)
    blo, bhi = ITS.basic_ci(D, draws)
    se = float(np.std(draws, ddof=1))
    return {"D": D, "lo": lo, "hi": hi, "blo": blo, "bhi": bhi, "se": se, "mde80": 2.8 * se, "S": S,
            "S0": {a: float(same[a][0].mean()) for a in ARMS}, "spread": {a: float(max(s.mean() for s in same[a]) - min(s.mean() for s in same[a])) for a in ARMS},
            "n": int(len(comp)), "components": int(len(np.unique(comp))), "kish": ITS.kish(comp) if len(comp) else float("nan")}


def scoreable(pred, bar, mde):
    beyond = abs(pred) - bar
    return beyond, ("SCOREABLE" if bool(beyond > mde) else "DESCRIPTIVE-ONLY")


def brier(p, event):
    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2


def _hit(v, lo, hi):
    return ITS._hit(float(v), lo, hi)


# ------------------------------------------------------------------------------------------------ lines
def selection_lines(sel):
    L = ["== GATE SELECTION (written and hashed before EVAL; EB1 tie 0.001 to the smaller d) =="]
    for e in EMB:
        s = sel[e]
        L.append("  %s: GATE score by d %s; max %.5f -> d* = %d; per-corpus GATE maxima (printed, never used) %s"
                 % (e, {d: round(v, 5) for d, v in s["score"].items()}, s["best"], s["d"], s["per_corpus_max"]))
    dq = sel["qwen3"]["d"]
    if dq != TREE_SLICE:
        L.append("  d_q* = %d != the tree slice of record %d: RELAYED to the tree specialist; nothing of record changes (D1 measured "
                 "certification, not NMI)" % (dq, TREE_SLICE))
    else:
        L.append("  d_q* = %d = the tree slice of record %d" % (dq, TREE_SLICE))
    return L


def criteria_lines(R):
    dq, dg = R["dq"], R["dg"]
    L = ["== DS1 (deciding; D* = mean_s NMI_EVAL(gemma, %d) - mean_s NMI_EVAL(qwen3, %d) at K_f; S0's C1 rule) ==" % (dg, dq)]
    for c in CORPORA:
        r = R["ds1"][c]
        L.append("  DS1 %s K_f %d n %d: D* = %+.5f, 95%% BASIC CI [%+.5f, %+.5f] (decides); percentile [%+.5f, %+.5f]; SE %.5f, MDE80 %.5f, "
                 "spread max(qwen3@%d %.5f, gemma@%d %.5f), bar %.5f -> %s"
                 % (c, II.GOLD_K[c][1], r["n"], r["D"], r["lo"], r["hi"], r["plo"], r["phi"], r["se"], r["mde80"], dq,
                    r["spread"][("qwen3", dq)], dg, r["spread"][("gemma", dg)], r["bar"], r["status"]))
    v, nb, nw = R["verdict"]
    st = {c: R["ds1"][c]["status"] for c in CORPORA}
    better = [c for c in CORPORA if st[c] == "BETTER"]
    worse = [c for c in CORPORA if st[c] == "WORSE"]
    if v == "REOPEN-CANDIDATE":
        L.append("DS1 VERDICT: REOPEN-CANDIDATE -- gemma BETTER on %d of 3 %s (>= 2)" % (nb, better))
        L.append("F-DS: FIRED (DS1 reads REOPEN-CANDIDATE): the working hypothesis that S0's gemma > qwen3 at the fine level is a slice "
                 "artefact is overturned; S0 C1a's and SLOTSWAP M3's descriptive 'gemma beats qwen3' rows survive the dimension confound, "
                 "on RAW prompts and with mismatched quantisation; no recorded number is revised")
        L.append("READING (REOPEN-CANDIDATE): \"gemma's fine edge survives the slice confound on >= 2 of 3 corpora\"; D3's revisit conditions "
                 "stay the author's (checkpoint B: CARD-PROTOCOL CP1 HELD AND F-E1 not fired); this test alone never changes the embedder "
                 "of record, and quantisation stays uncontrolled")
    else:
        if v == "KEEP-STRONG":
            L.append("DS1 VERDICT: KEEP-STRONG (a sub-case of KEEP) -- gemma BETTER on %d of 3 %s (<= 1); gemma WORSE on %d of 3 %s (>= 2)"
                     % (nb, better, nw, worse))
        else:
            L.append("DS1 VERDICT: KEEP -- gemma BETTER on %d of 3 %s (<= 1); gemma WORSE on %d of 3 %s" % (nb, better, nw, worse))
        L.append("F-DS: NOT FIRED (DS1 reads %s, not REOPEN-CANDIDATE)" % v)
        L.append("READING (KEEP): \"at each embedder's GATE-selected slice, gemma's fine-level edge over qwen3 is not shown on >= 2 of 3 "
                 "intent corpora (RAW protocol; qwen3 Q4_K_M vs gemma BF16)\"; this supports D3 as decided (qwen3 of record, gemma secondary)")
        if v == "KEEP-STRONG":
            L.append("READING (KEEP-STRONG): in addition, \"qwen3 is better at the fine level at its selected slice on >= 2 of 3\"")
        if st["massive"] == "NEITHER":
            L.append("READING caveat: MASSIVE reads NEITHER inside its bar (D* %+.5f, bar %.5f): KEEP does NOT say that the slice explains "
                     "the S0 edge (Support (f))" % (R["ds1"]["massive"]["D"], R["ds1"]["massive"]["bar"]))
    return L


def ds_lines(R):
    dq, dg = R["dq"], R["dg"]
    L = ["== DS2 (DESCRIPTIVE-ONLY; slice curve, paired BASIC CI on DS1's stream) =="]
    for c in CORPORA:
        r = R["ds1"][c]["ds2"]
        L.append("  DS2 %s: qwen3 NMI(d) - NMI(256): %s; gemma 768 - 256 %+.5f [%+.5f, %+.5f]"
                 % (c, "; ".join("%d %+.5f [%+.5f, %+.5f]" % (d, r[("qwen3", d)]["d"], r[("qwen3", d)]["lo"], r[("qwen3", d)]["hi"])
                                 for d in SLICES["qwen3"][1:]), r[("gemma", 768)]["d"], r[("gemma", 768)]["lo"], r[("gemma", 768)]["hi"]))
    d3 = R["ds3"]
    L.append("== DS3 (DESCRIPTIVE-ONLY; MASSIVE slot swap, K 60, mean over seeds 0-4) ==")
    L.append("  DS3 S(gemma@%d) - S(qwen3@%d) = %+.5f, 95%% percentile CI [%+.5f, %+.5f] (EB4; BASIC [%+.5f, %+.5f]); SE %.5f, MDE80 %.5f; "
             "against the SLOTSWAP seed spread %.4f" % (dg, dq, d3["D"], d3["lo"], d3["hi"], d3["blo"], d3["bhi"], d3["se"], d3["mde80"], DS3_SPREAD))
    L.append("  DS3 S table (seed-mean / seed 0 / seed spread): %s" % "; ".join(
        "%s@%d %.5f / %.5f / %.5f" % (e, d, d3["S"][(e, d)], d3["S0"][(e, d)], d3["spread"][(e, d)]) for e, d in ARMS))
    L.append("== DS4 (DESCRIPTIVE-ONLY; H = ARI of average-link on gold fine TRAIN centroids cut at K_c vs the gold map) ==")
    for c in H_CORPORA:
        L.append("  DS4 %s: %s" % (c, "; ".join("%s@%d H %.4f [%.4f, %.4f] (random p95 %.4f, dropped labels %d)"
                                                 % (e, d, R["H"][(e, d, c)]["H"], R["H"][(e, d, c)]["lo"], R["H"][(e, d, c)]["hi"],
                                                    R["H"][(e, d, c)]["p95"], R["H"][(e, d, c)]["dropped"]) for e, d in ARMS)))
    L.append("== PRINTED, NEVER DECIDING ==")
    for c in CORPORA:
        L.append("  fine NMI %s seed-mean EVAL: %s" % (c, "; ".join("%s@%d %.5f" % (e, d, np.mean(R["ev_nmi"][(e, d, c)])) for e, d in ARMS)))
        L.append("  fine NMI %s seed-mean GATE (n %d): %s" % (c, R["gate"][("qwen3", BASE, c, "n")],
                                                            "; ".join("%s@%d %.5f" % (e, d, np.mean(R["gate"][(e, d, c)])) for e, d in ARMS)))
    for c in H_CORPORA:
        L.append("  coarse NMI %s seed-mean EVAL K_c %d: %s" % (c, II.GOLD_K[c][0], "; ".join(
            "%s@%d %.5f" % (e, d, np.mean(R["coarse"][(e, d, c)])) for e, d in ARMS)))
    return L


def support_lines(R):
    L = ["== SUPPORT (measured; planning values beside) =="]
    for c in CORPORA:
        r = R["ds1"][c]
        beyond, word = scoreable(P3[c][0], r["bar"], r["mde80"])
        L.append("  DS1 %s: n %d EVAL items in %d components, Kish DEFF %.4f (planned %.4f), n_eff %.0f; SE(D*) %.5f (planned %.5f), "
                 "MDE80 %.5f, bar %.5f (planning %.4f); at P3's point %+.3f: |P3| - bar = %+.5f vs MDE80 -> %s"
                 % (c, r["n"], r["components"], r["kish"], PLAN_DEFF[c], r["n"] / r["kish"], r["se"], PLAN_SE[c], r["mde80"], r["bar"],
                    PLAN_BAR[c], P3[c][0], beyond, word))
        L.append("  GATE %s: n %d in-scope items (the selection's denominator)" % (c, R["gate"][("qwen3", BASE, c, "n")]))
    d3 = R["ds3"]
    beyond, word = scoreable(P5[0], DS3_SPREAD, d3["mde80"])
    L.append("  DS3: n %d variants in %d components, Kish DEFF %.4f, n_eff %.0f; SE %.5f (planned %.4f), MDE80 %.5f; at P5's point %+.3f: "
             "|P5| - %.4f = %+.5f -> %s" % (d3["n"], d3["components"], d3["kish"], d3["n"] / d3["kish"], d3["se"], PLAN_DS3_SE, d3["mde80"],
                                            P5[0], DS3_SPREAD, beyond, word))
    L.append("  STRUCTURAL LEG: DS1 is reachable only where |D*| exceeds the in-run seed spread, which does not shrink with n; inside "
             "it a corpus reads NEITHER at any budget (KEEP by construction on that corpus)")
    return L


def predictions_lines(R):
    dq, dg = R["dq"], R["dg"]
    L = ["== PREDICTIONS (numeric HELD iff the point lies in the closed 80% interval; probabilities scored on the event, Brier) =="]
    briers = []
    ev1 = {"d_q* in {1024, 4096}": dq in (1024, 4096), "d_q* = 512": dq == 512, "d_q* = 256": dq == 256, "d_g* = 768": dg == 768}
    for name, p in P1:
        b = brier(p, ev1[name])
        briers.append(b)
        L.append("  P1 %s (p %.2f): %s, Brier %.4f" % (name, p, "OCCURRED" if ev1[name] else "did not occur", b))
    for c in CORPORA:
        x = R["ds1"][c]["ds2"][("qwen3", dq)]["d"] if dq != BASE else 0.0
        L.append("  P2 %s qwen3 NMI(%d) - NMI(256) %+.5f in [%+.3f, %+.3f]: %s" % (c, dq, x, P2[1], P2[2], _hit(x, P2[1], P2[2])))
    for c in CORPORA:
        x = R["ds1"][c]["D"]
        L.append("  P3 %s D* %+.5f in [%+.3f, %+.3f]: %s" % (c, x, P3[c][1], P3[c][2], _hit(x, P3[c][1], P3[c][2])))
    v = R["verdict"][0]
    ev4 = {"KEEP": v in ("KEEP", "KEEP-STRONG"), "KEEP-STRONG": v == "KEEP-STRONG", "REOPEN-CANDIDATE": v == "REOPEN-CANDIDATE"}
    for name, p in P4:
        b = brier(p, ev4[name])
        briers.append(b)
        L.append("  P4 %s (p %.2f): %s, Brier %.4f" % (name, p, "OCCURRED" if ev4[name] else "did not occur", b))
    x = R["ds3"]["D"]
    L.append("  P5 DS3 %+.5f in [%+.3f, %+.3f]: %s" % (x, P5[1], P5[2], _hit(x, P5[1], P5[2])))
    Hm = {d: R["H"][("qwen3", d, "massive")]["H"] for d in SLICES["qwen3"]}
    ev6a = all(bool(R["H"][("gemma", dg, "massive")]["H"] > Hm[d]) for d in SLICES["qwen3"])
    ev6b = all(bool(R["H"][("qwen3", b, c)]["H"] >= R["H"][("qwen3", a, c)]["H"]) for c in H_CORPORA
               for a, b in zip(SLICES["qwen3"][:-1], SLICES["qwen3"][1:]))
    for (name, p), ev in zip(P6, (ev6a, ev6b)):
        b = brier(p, ev)
        briers.append(b)
        L.append("  P6 %s (p %.2f; EB6 gemma@%d): %s, Brier %.4f" % (name, p, dg, "OCCURRED" if ev else "did not occur", b))
    L.append("  mean Brier over the %d probability predictions: %.4f" % (len(briers), float(np.mean(briers))))
    return L


def tag_lines(L):
    return ["%s %s" % (ln, CONFOUNDS) for ln in L]


# ------------------------------------------------------------------------------------------------ run
def out_paths(out_dir):
    return [os.path.join(out_dir, p) for p in (SELECTION, OUTCOME) + CSVS]


def main_run(db=None, emb_dir=None, out_dir=OUT_DIR, programme=PROGRAMME, identity=None):
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    identity = identity or IDENTITY
    reset_phase()
    print("%s pool of record: none read (S0's own DBs); zero calls; no embeddings" % TAG)
    for p in out_paths(out_dir):
        if os.path.lexists(p):
            refuse("%s exists: every output of record is write-once" % p)
    check_its_blob()
    heavy_check()
    if not check_registered(programme):
        refuse("EMBED-DIM-SLICE is not registered in %s: --run writes a record only after the registration" % programme)
    sha0, CS, texts, derived = load_inputs(db, emb_dir, True)
    for c in CORPORA:
        CS_COMP[c] = CS[c].comp
    vecs = {e: load_full(ITS.emb_path(e, emb_dir), e, texts) for e in EMB}
    del ITS.FIT_LOG[:]
    fits, gate, H = phase_a(CS, vecs)
    sel = select(gate)
    os.makedirs(out_dir, exist_ok=True)
    sel_sha = write_selection(os.path.join(out_dir, SELECTION), sel, sha0, gate)
    PB = phase_b(CS, vecs, derived, fits)
    D256, S256 = identity_values(PB)
    S_c4 = c4_identity(CS, vecs, derived)
    id_lines = identity_check(D256, S256, S_c4, identity)
    dq, dg = sel["qwen3"]["d"], sel["gemma"]["d"]
    R = {"dq": dq, "dg": dg, "sel": sel, "gate": gate, "H": H, "ev_nmi": PB["ev_nmi"], "coarse": PB["coarse"]}
    R["ds1"] = {c: ds1(PB, c, dq, dg) for c in CORPORA}
    R["verdict"] = verdict({c: R["ds1"][c]["status"] for c in CORPORA})
    R["ds3"] = ds3(PB, dq, dg)
    audit = ITS.fit_audit()
    first_eval = next(i for i, ev in enumerate(EVENTS) if ev[0] == "EVAL")
    sel_i = next(i for i, ev in enumerate(EVENTS) if ev[0] == "SELECTION")
    if not sel_i < first_eval:
        refuse("ORDER: an EVAL read (event %d) precedes the selection (event %d)" % (first_eval, sel_i))
    after_check(sha0, db, emb_dir)
    L = ["EMBED-DIM-SLICE outcome (tools/analysis/embed_dim_slice.py, blob %s; S0 machinery intent_transfer_s0.py blob %s, imported unchanged)"
         % (RO.git_blob_lf(os.path.abspath(__file__)), ITS_BLOB),
         "registration: " + REG,
         "zero judge calls; zero embeddings; no build; no Ollama; pool of record: none read; pins re-checked before and after, unchanged: %s"
         % {k: v[:16] for k, v in sha0.items()},
         "ORDER: selection.json sha256 %s written at event %d, before the first EVAL read at event %d (%d EVAL reads, all after)"
         % (sel_sha, sel_i, first_eval, sum(1 for ev in EVENTS if ev[0] == "EVAL")),
         READINGS, audit] + id_lines
    L += selection_lines(sel) + support_lines(R) + criteria_lines(R) + ds_lines(R) + predictions_lines(R) + [DOES_NOT_SHOW]
    L = tag_lines(L)
    for ln in L:
        print(ln)
    with open(os.path.join(out_dir, OUTCOME), "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    write_csvs(R, out_dir)
    print("%s wrote %s (write-once, of record)" % (TAG, os.path.join(out_dir, OUTCOME)))
    R["lines"] = L
    return R


def write_csvs(R, out_dir):
    with open(os.path.join(out_dir, CSVS[0]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["embedder", "slice", "corpus", "level", "side", "seed", "nmi"])
        for e, d in ARMS:
            for c in CORPORA:
                for s, x in zip(SEEDS, R["gate"][(e, d, c)]):
                    w.writerow([e, d, c, "fine", "GATE", s, "%.6f" % x])
                for s, x in zip(SEEDS, R["ev_nmi"][(e, d, c)]):
                    w.writerow([e, d, c, "fine", "EVAL", s, "%.6f" % x])
                for s, x in zip(SEEDS, R["coarse"].get((e, d, c), [])):
                    w.writerow([e, d, c, "coarse", "EVAL", s, "%.6f" % x])
    with open(os.path.join(out_dir, CSVS[1]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["embedder", "slice", "S_seed_mean", "S_seed0", "seed_spread"])
        for e, d in ARMS:
            w.writerow([e, d, "%.6f" % R["ds3"]["S"][(e, d)], "%.6f" % R["ds3"]["S0"][(e, d)], "%.6f" % R["ds3"]["spread"][(e, d)]])
    with open(os.path.join(out_dir, CSVS[2]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["embedder", "slice", "corpus", "H", "lo", "hi", "random_p95", "dropped_labels"])
        for e, d in ARMS:
            for c in H_CORPORA:
                h = R["H"][(e, d, c)]
                w.writerow([e, d, c, "%.6f" % h["H"], "%.6f" % h["lo"], "%.6f" % h["hi"], "%.6f" % h["p95"], h["dropped"]])


def dry_run(db=None, emb_dir=None, programme=PROGRAMME, identity=None, timing=True):
    """Pins, census, GATE / EVAL counts, the identity on S0's own 256 arms (EB7), one timed 4096-d fit and the price. Writes nothing."""
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    identity = identity or IDENTITY
    reset_phase()
    print("%s pool of record: none read (S0's own DBs); zero calls; DRY RUN: nothing written, no selection made" % TAG)
    check_its_blob()
    heavy_check()
    check_registered(programme)
    sha0, CS, texts, derived = load_inputs(db, emb_dir, False)
    cen = census(CS, derived)
    for c in CORPORA:
        x = cen[c]
        print("%s census %s: TRAIN %d, GATE %d (the selection's denominator), EVAL %d in %d components (Kish DEFF %.4f, n_eff %.0f)"
              % (TAG, c, x[SS.TRAIN], x[SS.GATE], x[SS.EVAL], x["eval_components"], x["eval_kish"], x[SS.EVAL] / x["eval_kish"]))
    print("%s census DS3: %d slot-swap variants" % (TAG, cen["variants"]))
    vecs = {e: load_full(ITS.emb_path(e, emb_dir), e, texts) for e in EMB}
    del ITS.FIT_LOG[:]
    PHASE["dry_identity"] = True
    try:
        D, Sv = {}, {}
        for c in CORPORA:
            C = CS[c]
            kf = II.GOLD_K[c][1]
            m = {}
            for e in EMB:
                S = ITS.Space(vecs[e], C, BASE)
                ev = eval_idx(C, S, "dry identity %s@256 %s" % (e, c))
                t = ITS.codes(C.fine[ev])
                cms = [ITS.km_fit(C, S, kf, s, "EDS dry identity %s %s s%d" % (e, c, s)) for s in SEEDS]
                m[e] = float(np.mean([ITS.nmi(t, ITS.assign(S.X[ev], Cm)) for Cm in cms]))
                if c == "massive":
                    v = derived["variants"]
                    oi = np.array([i for i, _t, _c in v], dtype=int)
                    Sv[e] = float(np.mean(ITS.assign(S.X[oi], cms[0]) == ITS.assign(S.of([tx for _i, tx, _c in v]), cms[0])))
            D[c] = m["gemma"] - m["qwen3"]
        S_c4 = c4_identity(CS, vecs, derived)
        identity_check(D, Sv, S_c4, identity)
    finally:
        PHASE["dry_identity"] = False
    if any(d != BASE for _w, d in [(ev[1], int(ev[1].split("@")[1].split()[0])) for ev in EVENTS if ev[0] == "EVAL"]):
        refuse("the dry-run read EVAL of an arm other than 256")
    print("%s dry-run EVAL reads: %d, all on S0's own 256 arms (EB7)" % (TAG, sum(1 for ev in EVENTS if ev[0] == "EVAL")))
    if timing:
        C = CS["clinc"]
        S = ITS.Space(vecs["qwen3"], C, NATIVE["qwen3"])
        kf = II.GOLD_K["clinc"][1]
        t0 = time.time()
        ITS.km_fit(C, S, kf, 0, "EDS dry timing qwen3@4096 clinc fine s0")
        dt = time.time() - t0
        n0 = len(ITS.S_idx(C, S, SS.TRAIN))
        unit_cost = dt / float(n0 * kf * NATIVE["qwen3"])
        tot = 0.0
        for c in CORPORA:
            ntr = len(CS[c].idx(SS.TRAIN))
            for e, d in ARMS:
                for g in LEVELS[c]:
                    k = II.GOLD_K[c][1] if g == "fine" else II.GOLD_K[c][0]
                    tot += len(SEEDS) * ntr * k * d * unit_cost
        print("%s TIMING: one qwen3@4096 CLINC fine fit (n %d x K %d) took %.1f s; the %d fits priced at %.0f s (~%.1f h; linear in n x K x d, "
              "iteration counts vary; plus the bootstraps)" % (TAG, n0, kf, dt, len(SEEDS) * sum(len(LEVELS[c]) for c in CORPORA) * len(ARMS),
                                                               tot, tot / 3600.0))
    after_check(sha0, db, emb_dir)
    print("%s %s" % (TAG, ITS.fit_audit()))
    print("%s DRY RUN complete: nothing written; no selection; the outcome lines will carry %s" % (TAG, CONFOUNDS))
    return 0


# ------------------------------------------------------------------------------------------------ selftest fixtures
FX_PER = 96
# Per fixture: {embedder: {corpus: [(a_trainGATE, a_EVAL, sigma) per band]}}; bands qwen3 [0,256,512,1024], gemma [0,256].
G_ = (0.0, 0.0, 3.0)                        # a garbage band: noise only
FX_SPEC = {
    # R: qwen3 best at 1024 (three informative bands, the fourth garbage); gemma at 768; gemma BETTER on massive and banking77, WORSE
    # on clinc -> REOPEN-CANDIDATE (BETTER on 2, not the first two corpora).
    "R": {"qwen3": {c: [(3, 3, 1.6), (3, 3, 1.6), (3, 3, 1.6), G_] for c in CORPORA},
          "gemma": {"massive": [(3, 3, 1.0), (3, 3, 1.0)], "clinc": [(3, 3, 2.5), (3, 3, 2.5)], "banking77": [(3, 3, 1.0), (3, 3, 1.0)]}},
    # K: qwen3's third band informative on TRAIN / GATE but noise on EVAL (GATE picks 1024; EVAL alone would pick 512); gemma best at 256
    # (second band garbage); gemma BETTER on massive only, WORSE on clinc and banking77 -> KEEP-STRONG.
    "K": {"qwen3": {c: [(3, 3, 1.2), (3, 3, 1.2), (3, 0, 1.2), G_] for c in CORPORA},
          "gemma": {"massive": [(3, 3, 0.7), G_], "clinc": [(3, 3, 2.5), G_], "banking77": [(3, 3, 2.5), G_]}},
    # N: qwen3 best at 512; gemma at 768 with the same noise as qwen3 on massive (NEITHER), BETTER on banking77, WORSE on clinc -> KEEP.
    "N": {"qwen3": {c: [(3, 3, 1.2), (3, 3, 1.2), G_, G_] for c in CORPORA},
          "gemma": {"massive": [(3, 3, 1.2), (3, 3, 1.2)], "clinc": [(3, 3, 2.5), (3, 3, 2.5)], "banking77": [(3, 3, 0.8), (3, 3, 0.8)]}},
}
BAND_START = {"qwen3": (0, 256, 512, 1024), "gemma": (0, 256)}


def _rng(*parts):
    return np.random.default_rng(int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12], 16))


def _plant(spec, e, c, f, side, key):
    v = np.zeros(NATIVE[e])
    r = _rng("fx", e, key)
    for b, (a_tg, a_ev, sig) in enumerate(spec[e][c]):
        s0 = BAND_START[e][b]
        a = a_ev if side == SS.EVAL else a_tg
        if f is not None:
            v[s0 + f] += a
            if b == 0:
                v[s0 + 16 + f % 4] += 1.0
        v[s0:s0 + 20] += sig * r.normal(size=20)
    return v


@contextlib.contextmanager
def _fx_rows_scope():
    saved = ITS.ST_PER_FINE
    ITS.ST_PER_FINE = FX_PER
    try:
        yield
    finally:
        ITS.ST_PER_FINE = saved


def build_fixture(td, name):
    """Fixture ingest DB (S0's synthetic rows at FX_PER per intent) and planted qwen3 4096-d / gemma 768-d DBs; pins file."""
    spec = FX_SPEC[name]
    with _fx_rows_scope():
        rows = ITS._fixture_rows()
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows, [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    meta = {}
    for C in CS.values():
        for i in np.nonzero(C.kept)[0]:
            meta[C.text[i]] = (C.name, None if C.oos[i] else int(C.fine[i][-2:]), C.side[i])
    var_of = {t: CS["massive"].text[i] for i, t, _c in derived["variants"]}
    pair_of = {t: (CS[c].text[i], CS[c].text[j]) for c, ps in derived["pairs"].items() for i, j, t in ps}
    ingest_sha = II.file_sha(db)
    for e in EMB:
        V = {t: _plant(spec, e, c, f, sd, t) for t, (c, f, sd) in meta.items()}
        for t, o in var_of.items():
            v = V[o].copy()
            v[:20] += 0.6 * _rng("var", e, t).normal(size=20)
            V[t] = v
        for t, (a, b) in pair_of.items():
            V[t] = V[a] + V[b]
        p = ITS.emb_path(e, td)
        con = sqlite3.connect(p)
        con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
        con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(ITS.expected_meta(e, set_sha, len(texts), ingest_sha),
                                                                              model_digest="stub").items()))
        con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(V[t], dtype=">f4").tobytes()) for t in texts])
        con.commit()
        con.close()
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": II.file_sha(db),
                   "emb": {e: II.file_sha(ITS.emb_path(e, td)) for e in EMB}}, fh)
    prog = os.path.join(td, "programme.md")
    with open(prog, "w", encoding="utf-8") as fh:
        fh.write("## Registered 2026-10-02 %s fixture\n" % REG_NEEDLE)
    fx = {"td": td, "db": db, "pins": pins, "prog": prog, "name": name}
    fx["oracle"] = _oracle(fx)
    fx["identity"] = _s0_identity(fx)
    return fx


def _oracle(fx):
    """An INDEPENDENT recomputation: own sqlite read, own slice + renormalise, own side masks, sklearn NMI; only S0's skmeans (same
    seeds) is shared. -> selection, D* per corpus, DS2 qwen3 curve, DS3 S table."""
    from sklearn.metrics import normalized_mutual_info_score as NMI
    CS = ITS.load_corpora(fx["db"])
    raw = {}
    for e in EMB:
        con = sqlite3.connect(ITS.emb_path(e, fx["td"]))
        raw[e] = {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in con.execute("SELECT query, vector FROM embeddings")}
        con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    gate, ev, Sm = {}, {}, {}
    var = ITS.c4_variants(CS["massive"])[0]
    for c in CORPORA:
        C = CS[c]
        m = lambda sd: [i for i in range(len(C.text)) if C.kept[i] and not C.oos[i] and C.side[i] == sd]
        tr, gt, evr = m(SS.TRAIN), m(SS.GATE), m(SS.EVAL)
        for e, d in ARMS:
            X = lambda idx: U(np.array([raw[e][C.text[i]][:d] for i in idx]))
            Xtr, Xg, Xe = X(tr), X(gt), X(evr)
            cms = [ITS.skmeans(Xtr, II.GOLD_K[c][1], s) for s in SEEDS]
            gate[(e, d, c)] = np.mean([NMI(list(C.fine[gt]), np.argmax(Xg @ Cm.T, 1)) for Cm in cms])
            ev[(e, d, c)] = np.mean([NMI(list(C.fine[evr]), np.argmax(Xe @ Cm.T, 1)) for Cm in cms])
            if c == "massive":
                Xo = U(np.array([raw[e][C.text[i]][:d] for i, _t, _c in var]))
                Xv = U(np.array([raw[e][t][:d] for _i, t, _c in var]))
                Sm[(e, d)] = np.mean([np.mean(np.argmax(Xo @ Cm.T, 1) == np.argmax(Xv @ Cm.T, 1)) for Cm in cms])
    sel = {}
    gscore = {}
    for e in EMB:
        sc = {d: np.mean([gate[(e, d, c)] for c in CORPORA]) for d in SLICES[e]}
        sel[e] = min(d for d in SLICES[e] if sc[d] >= max(sc.values()) - TIE)
        gscore[e] = sc
    evsel = {}
    for e in EMB:
        sc = {d: np.mean([ev[(e, d, c)] for c in CORPORA]) for d in SLICES[e]}
        evsel[e] = max(sc, key=lambda d: sc[d])
    D = {c: ev[("gemma", sel["gemma"], c)] - ev[("qwen3", sel["qwen3"], c)] for c in CORPORA}
    curve = {(c, d): ev[("qwen3", d, c)] - ev[("qwen3", BASE, c)] for c in CORPORA for d in SLICES["qwen3"]}
    return {"sel": sel, "gate_score": gscore, "evsel": evsel, "D": D, "curve": curve, "S": Sm, "ds3": Sm[("gemma", sel["gemma"])] - Sm[("qwen3", sel["qwen3"])]}


def _s0_identity(fx):
    """The fixture's identity target from S0's OWN functions (c1_level at 256; c4 on each embedder's 256 space)."""
    CS = ITS.load_corpora(fx["db"])
    texts, _s, derived = ITS.text_set(CS)
    with contextlib.redirect_stdout(io.StringIO()):
        vecs = {e: ITS.load_vectors(ITS.emb_path(e, fx["td"]), e, texts) for e in EMB}
    D, S = {}, {}
    for c in CORPORA:
        sp = {e: ITS.Space(vecs[e], CS[c], BASE) for e in EMB}
        sp["nomic"] = sp["qwen3"]
        r = ITS.c1_level(CS[c], sp, "fine", II.GOLD_K[c][1], BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index("fine"))
        D[c] = "%+.5f" % r["per"]["gemma"]["D"]
        if c == "massive":
            fx["c1_massive"] = r["per"]["gemma"]
            for e in EMB:
                S[e] = "%.4f" % ITS.c4(CS[c], {"qwen3": sp[e]}, derived["variants"])["S"]
    return {"D": D, "S": S}


@contextlib.contextmanager
def _scope(fx, B=200):
    """Fixture scope: S0's fixture K (4 / 16), the fixture's pins file, no heavy process, a smaller bootstrap B (ITS's too); restored."""
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], g["BOOT_B"], ITS.BOOT_B)
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        g["BOOT_B"] = B
        ITS.BOOT_B = B
        try:
            yield
        finally:
            g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], g["BOOT_B"], ITS.BOOT_B = saved


def make_fixtures(td):
    out = {}
    for name in FX_SPEC:
        d = os.path.join(td, name)
        os.makedirs(d)
        with _scope(None):
            out[name] = build_fixture(d, name)
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
    return got[-1] if got else ""            # the last match: the outcome copy follows the progress print


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
    try:
        if fixture is None:
            td = tempfile.mkdtemp(prefix="eds_st_")
            try:
                _selftest(sel, ok, td, make_fixtures(td))
            finally:
                shutil.rmtree(td, ignore_errors=True)
        else:
            _selftest(sel, ok, fixture[0], fixture[1])
    finally:
        reset_phase()
    if not quiet:
        print("SELFTEST: %d checks passed" % n[0])
    return 0


def _syn_R(status, dq=1024, dg=768, massive_D=0.03):
    """A synthetic result dict for the line printers (every branch)."""
    r1 = {}
    for c in CORPORA:
        r1[c] = {"D": massive_D if c == "massive" else 0.05, "lo": 0.01, "hi": 0.06, "plo": 0.01, "phi": 0.06, "se": 0.003, "mde80": 0.0084,
                 "spread": {a: 0.01 for a in ARMS}, "bar": 0.02, "status": status[c], "n": 100, "components": 99, "kish": 1.01,
                 "ds2": {(e, d): {"d": 0.01, "lo": 0.0, "hi": 0.02, "se": 0.005} for e, d in ARMS if d != BASE}}
    return {"dq": dq, "dg": dg, "ds1": r1, "verdict": verdict(status)}


def _selftest(sel, ok, td, FX):
    g = globals()
    if sel("ST-CONST"):
        ok(check_its_blob() == ITS_BLOB, "ST-CONST intent_transfer_s0.py is the registered blob f662ceb (imported unchanged)")
        ok(ARMS == (("qwen3", 256), ("qwen3", 512), ("qwen3", 1024), ("qwen3", 4096), ("gemma", 256), ("gemma", 768)),
           "ST-CONST arms: qwen3 256/512/1024/4096, gemma 256/768")
        ok((TIE, BASE, TREE_SLICE, BOOT_B, SEEDS, NATIVE) == (0.001, 256, 512, 2000, (0, 1, 2, 3, 4), {"qwen3": 4096, "gemma": 768}),
           "ST-CONST tie 0.001, base 256, tree slice 512, B 2,000, seeds 0-4, native widths")
        ok(II.GOLD_K == {"massive": (18, 60), "clinc": (10, 150), "banking77": (None, 77)}, "ST-CONST K_f 60/150/77, K_c 18/10")
        ok(IDENTITY == {"D": {"massive": "+0.03340", "clinc": "-0.00691", "banking77": "+0.05628"}, "S": {"qwen3": "0.7598", "gemma": "0.8262"}},
           "ST-CONST identity digits +0.03340 / -0.00691 / +0.05628; S 0.7598 / 0.8262")
        ok("Q4_K_M" in CONFOUNDS and "BF16" in CONFOUNDS and "RAW" in CONFOUNDS, "ST-CONST confounds name the quantisation and the prompts")
        ok(P3 == {"massive": (0.022, 0.005, 0.040), "clinc": (-0.012, -0.025, 0.002), "banking77": (0.045, 0.030, 0.060)} and
           P2 == (0.010, 0.000, 0.025) and P5 == (0.055, 0.030, 0.080) and dict(P1)["d_q* = 512"] == 0.30 and dict(P4)["KEEP"] == 0.55,
           "ST-CONST registered predictions")
        ok(OUT_DIR.replace("\\", "/").endswith("experiment_results/embed_dim_slice") and OUTCOME == "outcome.txt", "ST-CONST outcome path")
    if sel("ST-UNIT"):
        def gt(scores):          # scores: {e: {d: score}} equal across corpora
            return {(e, d, c): [scores[e][d]] * 5 for e in EMB for d in SLICES[e] for c in CORPORA}
        s = select(gt({"qwen3": {256: 0.80, 512: 0.85, 1024: 0.8495, 4096: 0.84}, "gemma": {256: 0.7, 768: 0.9}}))
        ok(s["qwen3"]["d"] == 512 and s["gemma"]["d"] == 768, "ST-UNIT select: max at 512 wins over 1024 0.0005 below (smaller in the tie)")
        ok(pick({256: 0.80, 512: 0.85 - TIE, 1024: 0.85, 4096: 0.84}) == (512, 0.85), "ST-UNIT pick: 512 at exactly max - 0.001 is a tie -> smaller")
        ok(pick({256: 0.85 - TIE, 512: 0.85 - TIE / 2, 1024: 0.85, 4096: 0.85 - TIE}) == (256, 0.85), "ST-UNIT pick: every d within the tie -> the smallest (256)")
        s = select(gt({"qwen3": {256: 0.80, 512: 0.8495, 1024: 0.85, 4096: 0.84}, "gemma": {256: 0.9, 768: 0.9}}))
        ok(s["qwen3"]["d"] == 512 and s["gemma"]["d"] == 256, "ST-UNIT select: 512 0.0005 below the max -> 512; gemma equal -> 256")
        s = select(gt({"qwen3": {256: 0.80, 512: 0.8488, 1024: 0.85, 4096: 0.84}, "gemma": {256: 0.5, 768: 0.9}}))
        ok(s["qwen3"]["d"] == 1024, "ST-UNIT select: 512 at max - 0.0012 is not a tie -> 1024")
        s = select(gt({"qwen3": {256: 0.70, 512: 0.75, 1024: 0.80, 4096: 0.86}, "gemma": {256: 0.91, 768: 0.9}}))
        ok(s["qwen3"]["d"] == 4096 and s["gemma"]["d"] == 256, "ST-UNIT select: the last slice when it is the max; gemma 256 when larger")
        sc = {(e, d, c): [0.5] * 5 for e in EMB for d in SLICES[e] for c in CORPORA}
        sc[("qwen3", 4096, "banking77")] = [0.99] * 5
        sc[("qwen3", 1024, "massive")] = [0.53] * 5
        sc[("qwen3", 1024, "clinc")] = [0.53] * 5
        s = select(sc)
        ok(s["qwen3"]["d"] == 4096 and s["qwen3"]["per_corpus_max"]["massive"] == 1024, "ST-UNIT select averages over corpora (4096 by banking77's mean)")
        sc[("qwen3", 1024, "banking77")] = [0.99] * 5
        s = select(sc)
        ok(s["qwen3"]["d"] == 1024, "ST-UNIT select: every corpus counts (1024 wins when it ties banking77 and leads two corpora)")
        mk = lambda a, b, c: {"massive": a, "clinc": b, "banking77": c}
        ok(verdict(mk("BETTER", "NEITHER", "BETTER"))[0] == "REOPEN-CANDIDATE", "ST-UNIT verdict: BETTER on massive + banking77 -> REOPEN-CANDIDATE")
        ok(verdict(mk("NEITHER", "BETTER", "BETTER"))[0] == "REOPEN-CANDIDATE", "ST-UNIT verdict: BETTER on the last two -> REOPEN-CANDIDATE")
        ok(verdict(mk("BETTER", "BETTER", "BETTER"))[0] == "REOPEN-CANDIDATE", "ST-UNIT verdict: BETTER on 3 -> REOPEN-CANDIDATE")
        ok(verdict(mk("BETTER", "NEITHER", "NEITHER"))[0] == "KEEP", "ST-UNIT verdict: BETTER on 1 -> KEEP")
        ok(verdict(mk("NEITHER", "NEITHER", "NEITHER"))[0] == "KEEP", "ST-UNIT verdict: none -> KEEP")
        ok(verdict(mk("WORSE", "NEITHER", "BETTER"))[0] == "KEEP", "ST-UNIT verdict: WORSE on 1, BETTER on 1 -> KEEP")
        ok(verdict(mk("NEITHER", "WORSE", "WORSE"))[0] == "KEEP-STRONG", "ST-UNIT verdict: WORSE on 2 -> KEEP-STRONG")
        ok(verdict(mk("BETTER", "WORSE", "WORSE")) == ("KEEP-STRONG", 1, 2), "ST-UNIT verdict: BETTER 1 + WORSE 2 -> KEEP-STRONG (counts 1, 2)")
        ok(scoreable(0.045, 0.0143, 0.0069) == (0.045 - 0.0143, "SCOREABLE") and scoreable(-0.012, 0.0094, 0.0038)[1] == "DESCRIPTIVE-ONLY"
           and scoreable(0.022, 0.0246, 0.0081)[1] == "DESCRIPTIVE-ONLY", "ST-UNIT scoreable reproduces Support (f): banking77 / clinc / massive")
        # ds1 where the seed spread is 0 (identical partitions over seeds): the bar is MDE80 = 2.8 x the bootstrap SE
        rg = np.random.default_rng(5)
        tz = rg.integers(6, size=300)
        pz = {a: [np.where(rg.random(300) < 0.3 + 0.1 * j, rg.integers(6, size=300), tz)] * 5 for j, a in enumerate(ARMS)}
        PBz = {"truth": {"massive": tz}, "evrows": {"massive": np.arange(300)}, "preds": {a + ("massive",): pz[a] for a in ARMS},
               "ev_nmi": {a + ("massive",): [ITS.nmi(tz, q) for q in pz[a]] for a in ARMS}}
        CS_COMP["massive"] = np.arange(300) // 2
        rz = ds1(PBz, "massive", 1024, 768, B=300)
        ok(rz["spread"][("qwen3", 1024)] == 0 and rz["se"] > 0 and abs(rz["bar"] - 2.8 * rz["se"]) < 1e-15 and abs(rz["mde80"] - 2.8 * rz["se"]) < 1e-15,
           "ST-UNIT DS1 bar = MDE80 = 2.8 x SE %.5f when the seed spread is 0" % rz["se"])
        ok(abs(rz["D"] - (ITS.nmi(tz, pz[("gemma", 768)][0]) - ITS.nmi(tz, pz[("qwen3", 1024)][0]))) < 1e-15 and rz["components"] == 150,
           "ST-UNIT DS1 D* = gemma@d_g* - qwen3@d_q* on the chosen arms; components counted (150)")
        ok(abs(brier(0.55, True) - 0.2025) < 1e-12 and abs(brier(0.55, False) - 0.3025) < 1e-12 and brier(0.3, np.True_) == brier(0.3, 1), "ST-UNIT Brier (0.2025 / 0.3025; numpy bool accepted)")
        ok(_hit(0.005, 0.005, 0.04) == "HELD" and _hit(np.float32(0.01), 0.005, 0.04) == "HELD" and _hit(0.0401, 0.005, 0.04) == "FAILED" and _hit(-0.025, -0.025, 0.002) == "HELD",
           "ST-UNIT prediction interval closed at both ends (float32 accepted)")
        # every printed branch of the criteria (line printers on synthetic results)
        L = criteria_lines(_syn_R(mk("BETTER", "NEITHER", "BETTER")))
        ok(_line("\n".join(L), "DS1 VERDICT:").startswith("DS1 VERDICT: REOPEN-CANDIDATE -- gemma BETTER on 2 of 3 ['massive', 'banking77']")
           and _line("\n".join(L), "F-DS:").startswith("F-DS: FIRED") and _line("\n".join(L), "READING (REOPEN-CANDIDATE)") != "",
           "ST-UNIT lines REOPEN: verdict, F-DS FIRED, the REOPEN reading")
        L = "\n".join(criteria_lines(_syn_R(mk("NEITHER", "WORSE", "WORSE"))))
        ok(_line(L, "DS1 VERDICT:").startswith("DS1 VERDICT: KEEP-STRONG (a sub-case of KEEP) -- gemma BETTER on 0 of 3") and
           _line(L, "F-DS:") == "F-DS: NOT FIRED (DS1 reads KEEP-STRONG, not REOPEN-CANDIDATE)" and "not shown on >= 2 of 3" in _line(L, "READING (KEEP)")
           and _line(L, "READING (KEEP-STRONG)") != "" and "MASSIVE reads NEITHER" in _line(L, "READING caveat"),
           "ST-UNIT lines KEEP-STRONG: verdict, F-DS NOT FIRED, KEEP + KEEP-STRONG readings, the MASSIVE caveat")
        L = "\n".join(criteria_lines(_syn_R(mk("BETTER", "NEITHER", "WORSE"))))
        ok(_line(L, "DS1 VERDICT:").startswith("DS1 VERDICT: KEEP -- gemma BETTER on 1 of 3 ['massive']") and _line(L, "READING (KEEP-STRONG)") == ""
           and _line(L, "READING caveat") == "" and _line(L, "F-DS:").startswith("F-DS: NOT FIRED"),
           "ST-UNIT lines KEEP: no KEEP-STRONG reading, no caveat when MASSIVE is not NEITHER")
        L = "\n".join(selection_lines({"qwen3": {"d": 1024, "score": {256: .5}, "best": .5, "per_corpus_max": {}},
                                       "gemma": {"d": 768, "score": {768: .5}, "best": .5, "per_corpus_max": {}}}))
        ok("RELAYED to the tree specialist" in L and "d_q* = 1024 != the tree slice of record 512" in L, "ST-UNIT relay line when d_q* != 512")
        L = "\n".join(selection_lines({"qwen3": {"d": 512, "score": {256: .5}, "best": .5, "per_corpus_max": {}},
                                       "gemma": {"d": 768, "score": {768: .5}, "best": .5, "per_corpus_max": {}}}))
        ok("RELAYED" not in L and "d_q* = 512 = the tree slice of record 512" in L, "ST-UNIT no relay when d_q* = 512")
    if sel("ST-LOAD"):
        fx = FX["R"]
        with _scope(fx):
            CS = ITS.load_corpora(fx["db"])
            texts, _s, _d = ITS.text_set(CS)
            with contextlib.redirect_stdout(io.StringIO()):
                full = load_full(ITS.emb_path("qwen3", fx["td"]), "qwen3", texts)
                s0 = ITS.load_vectors(ITS.emb_path("qwen3", fx["td"]), "qwen3", texts)
                fg = load_full(ITS.emb_path("gemma", fx["td"]), "gemma", texts)
        t0 = texts[0]
        ok(len(full[t0]) == 4096 and len(fg[t0]) == 768 and ITS.SLICE2 == 512, "ST-LOAD full width 4096 / 768 read; ITS.SLICE2 restored to 512")
        ok(all(np.array_equal(full[t][:512], s0[t]) for t in texts), "ST-LOAD the first 512 coordinates equal S0's own load_vectors for every text")
        ok(float(np.abs(full[t0][1024:1044]).sum()) > 0, "ST-LOAD coordinates past 1024 are read (non-zero in the planted band)")
    if sel("ST-GATE"):
        fx = FX["R"]
        reset_phase()
        with _scope(fx):
            CS = ITS.load_corpora(fx["db"])
            texts, _s, _d = ITS.text_set(CS)
            with contextlib.redirect_stdout(io.StringIO()):
                v = load_full(ITS.emb_path("qwen3", fx["td"]), "qwen3", texts)
            S = ITS.Space(v, CS["massive"], 512)
            o, err, _r = _cap(lambda: eval_idx(CS["massive"], S, "probe"))
            ok(err and "before the GATE selection file" in err, "ST-GATE an EVAL read before the selection REFUSES")
            PHASE["dry_identity"] = True
            o, err, _r = _cap(lambda: eval_idx(CS["massive"], S, "probe"))
            ok(err and "before the GATE selection file" in err, "ST-GATE the dry-run identity may not read a non-256 arm")
            S2 = ITS.Space(v, CS["massive"], 256)
            o, err, r = _cap(lambda: eval_idx(CS["massive"], S2, "probe"))
            ok(err is None and len(r) == len(CS["massive"].idx(SS.EVAL)), "ST-GATE the dry-run identity reads S0's 256 arm")
        reset_phase()
    if sel("ST-E2E"):
        for name, want_v, want_st, want_sel in (("R", "REOPEN-CANDIDATE", ("BETTER", "WORSE", "BETTER"), (1024, 768)),
                                                ("K", "KEEP-STRONG", ("BETTER", "WORSE", "WORSE"), (1024, 256)),
                                                ("N", "KEEP", ("NEITHER", "WORSE", "BETTER"), (512, 768))):
            fx = FX[name]
            orc = fx["oracle"]
            o, err, R, od = _run(fx, "e2e")
            ok(err is None and R is not None, "ST-E2E %s --run completes (%s)" % (name, err))
            ok((orc["sel"]["qwen3"], orc["sel"]["gemma"]) == want_sel, "ST-E2E %s the fixture's oracle selects %s (planted)" % (name, want_sel))
            ok("SELECTION written" in o and ("d_q* %d, d_g* %d" % want_sel) in _line(o, "SELECTION written"),
               "ST-E2E %s printed selection d_q* %d, d_g* %d" % ((name,) + want_sel))
            for c, st in zip(CORPORA, want_st):
                ln = _line(o, "DS1 %s K_f" % c)
                ok(("D* = %+.5f," % orc["D"][c]) in ln, "ST-E2E %s DS1 %s printed D* equals the independent oracle %+.5f" % (name, c, orc["D"][c]))
                ok(ln.split(" -> ")[1].split(" ")[0] == st, "ST-E2E %s DS1 %s status %s (got %s)" % (name, c, st, ln.split(" -> ")[1][:10]))
            ok(_line(o, "DS1 VERDICT:").startswith("DS1 VERDICT: %s " % want_v), "ST-E2E %s verdict word %s" % (name, want_v))
            ok(_line(o, "F-DS:").startswith("F-DS: FIRED" if want_v == "REOPEN-CANDIDATE" else "F-DS: NOT FIRED"), "ST-E2E %s F-DS line" % name)
            for c in CORPORA:
                ln = _line(o, "DS2 %s:" % c)
                for d in SLICES["qwen3"][1:]:
                    ok(("%d %+.5f [" % (d, orc["curve"][(c, d)])) in ln, "ST-E2E %s DS2 %s qwen3 %d - 256 equals the oracle" % (name, c, d))
            ok(("= %+.5f," % orc["ds3"]) in _line(o, "DS3 S(gemma@"), "ST-E2E %s DS3 equals the oracle %+.5f" % (name, orc["ds3"]))
            ln = _line(o, "DS3 S table")
            ok(all(("%s@%d %.5f /" % (e, d, orc["S"][(e, d)])) in ln for e, d in ARMS), "ST-E2E %s DS3 S table (6 arms) equals the oracle" % name)
            ok(_line(o, "IDENTITY:").endswith("-> REPRODUCED " + CONFOUNDS), "ST-E2E %s identity line REPRODUCED" % name)
            txt = open(os.path.join(od, OUTCOME), encoding="utf-8").read().splitlines()
            ok(len(txt) > 40 and all(ln.endswith(CONFOUNDS) for ln in txt), "ST-E2E %s every one of the %d outcome lines carries the confounds" % (name, len(txt)))
            ok(all(os.path.isfile(p) for p in out_paths(od)), "ST-E2E %s selection.json, outcome.txt and the three CSVs written" % name)
            sj = json.load(open(os.path.join(od, SELECTION)))
            ok((sj["d_q*"], sj["d_g*"]) == want_sel and hashlib.sha256(open(os.path.join(od, SELECTION), "rb").read()).hexdigest() in _line(o, "ORDER:"),
               "ST-E2E %s selection.json carries d* and its sha256 is the one printed in ORDER" % name)
            ok(EVENTS[0][0] == "SELECTION" and all(ev[0] == "EVAL" for ev in EVENTS[1:]) and len(EVENTS) > 18,
               "ST-E2E %s by execution: the selection is event 0, every one of the %d EVAL reads follows" % (name, len(EVENTS) - 1))
            for e in EMB:
                ln = _line(o, "%s: GATE score by d" % e)
                ok(all(("%d: %r" % (d, round(float(v), 5))) in ln for d, v in orc["gate_score"][e].items()),
                   "ST-E2E %s printed GATE scores of %s (mean over corpora of the seed-mean GATE NMI) equal the oracle's" % (name, e))
            for c in CORPORA:
                ln = _line(o, "DS1 %s K_f" % c)
                se_, mde_ = float(ln.split("; SE ")[1].split(",")[0]), float(ln.split("MDE80 ")[1].split(",")[0])
                ok(abs(mde_ - 2.8 * se_) < 3e-5, "ST-E2E %s DS1 %s printed MDE80 %.5f = 2.8 x SE %.5f" % (name, c, mde_, se_))
            try:
                write_selection(os.path.join(od, SELECTION), R["sel"], {}, R["gate"])
                ok(False, "ST-E2E %s selection.json is write-once (a second write raises)" % name)
            except FileExistsError:
                ok(True, "ST-E2E %s selection.json is write-once (a second write raises)" % name)
            if name == "K":
                ok(orc["evsel"]["qwen3"] == 512, "ST-E2E K the planted GATE/EVAL disagreement: EVAL alone would select 512, GATE selects 1024")
                ok("RELAYED to the tree specialist" in o, "ST-E2E K the relay line (d_q* 1024 != 512)")
                ok("MASSIVE reads NEITHER" not in o and _line(o, "READING (KEEP-STRONG)") != "", "ST-E2E K KEEP-STRONG reading, no caveat")
                ok(_line(o, "P4 KEEP (p").startswith("P4 KEEP (p 0.55): OCCURRED, Brier 0.2025") and
                   _line(o, "P4 KEEP-STRONG (p").startswith("P4 KEEP-STRONG (p 0.05): OCCURRED"), "ST-E2E K P4 KEEP occurs under KEEP-STRONG (a sub-case)")
            if name == "N":
                ok("MASSIVE reads NEITHER inside its bar" in o and "d_q* = 512 = the tree slice" in o, "ST-E2E N KEEP caveat (MASSIVE NEITHER); no relay")
                ok(_line(o, "P1 d_q* = 512 (p 0.30)").startswith("P1 d_q* = 512 (p 0.30): OCCURRED, Brier %.4f" % (0.7 ** 2)),
                   "ST-E2E N P1 d_q* = 512 OCCURRED, Brier 0.4900")
            if name == "R":
                ok(_line(o, "P1 d_q* in {1024, 4096}").startswith("P1 d_q* in {1024, 4096} (p 0.55): OCCURRED, Brier %.4f" % (0.45 ** 2)),
                   "ST-E2E R P1 d_q* in {1024, 4096} OCCURRED, Brier 0.2025")
                ok(_line(o, "P4 REOPEN-CANDIDATE").startswith("P4 REOPEN-CANDIDATE (p 0.45): OCCURRED") and
                   _line(o, "P4 KEEP (p").startswith("P4 KEEP (p 0.55): did not occur"), "ST-E2E R P4 scored on the verdict")
                for c in CORPORA:
                    x = orc["D"][c]
                    ok(_line(o, "P3 %s D*" % c).endswith("%s %s" % (_hit(float("%.5f" % x), P3[c][1], P3[c][2]), CONFOUNDS)), "ST-E2E R P3 %s scored" % c)
                    xs = orc["curve"][(c, 1024)]
                    ok(_line(o, "P2 %s" % c).endswith("%s %s" % (_hit(xs, P2[1], P2[2]), CONFOUNDS)) and ("%+.5f" % xs) in _line(o, "P2 %s" % c),
                       "ST-E2E R P2 %s reads qwen3 NMI(d_q*) - NMI(256) = %+.5f" % (c, xs))
    if sel("ST-EQUIV"):
        fx = FX["R"]
        with _scope(fx):
            CS = ITS.load_corpora(fx["db"])
            texts, _s, derived = ITS.text_set(CS)
            for c in CORPORA:
                CS_COMP[c] = CS[c].comp
            with contextlib.redirect_stdout(io.StringIO()):
                vecs = {e: load_full(ITS.emb_path(e, fx["td"]), e, texts) for e in EMB}
            reset_phase()
            fits, gate, H = phase_a(CS, vecs)
            PHASE["selection_sha"] = "probe"
            PB = phase_b(CS, vecs, derived, fits)
            r = ds1(PB, "massive", 256, 256)
            ref = fx["c1_massive"]
            ok(all(abs(r[k] - ref[k]) < 1e-12 for k in ("D", "lo", "hi", "se", "mde80", "bar")) and r["status"] == ref["status"],
               "ST-EQUIV DS1 at (256, 256) equals S0's own c1_level (D, BASIC CI, SE, bar, status) on the same stream")
            D, S = identity_values(PB)
            S_c4 = c4_identity(CS, vecs, derived)
            ok(all(S_c4[e] == S[e] for e in EMB) and {e: "%.4f" % S[e] for e in EMB} == fx["identity"]["S"],
               "ST-EQUIV the composed S at seed 0 equals S0's c4() exactly, both embedders")
            for e, d in ARMS:
                for c in H_CORPORA:
                    sp = ITS.Space(vecs[e], CS[c], d)
                    ok(H[(e, d, c)]["H"] == ITS.d2(CS[c], sp)["H"], "ST-EQUIV DS4 H %s@%d %s equals S0's d2" % (e, d, c))
            # the H bootstrap, independently: own weights from the same stream, own centroids
            from scipy.cluster.hierarchy import linkage, fcluster
            C = CS["massive"]
            sp = ITS.Space(vecs["gemma"], C, 768)
            tr = ITS.S_idx(C, sp, SS.TRAIN)
            u = sorted(set(C.fine[tr]))
            f2c = {C.fine[i]: C.coarse[i] for i in tr}
            dr = []
            for w in ITS.comp_weights(C.comp[tr], BOOT_B, np.random.default_rng(SEED_H)):
                G = []
                for x in u:
                    m = C.fine[tr] == x
                    s = (sp.X[tr][m] * w[m][:, None]).sum(0)
                    G.append(s / np.linalg.norm(s))
                cut = fcluster(linkage(np.array(G), method="average", metric="cosine"), t=II.GOLD_K["massive"][0], criterion="maxclust")
                dr.append(ITS.ari(ITS.codes([f2c[x] for x in u]), cut))
            lo, hi = np.percentile(dr, 2.5), np.percentile(dr, 97.5)
            ok(abs(lo - H[("gemma", 768, "massive")]["lo"]) < 1e-9 and abs(hi - H[("gemma", 768, "massive")]["hi"]) < 1e-9 and hi > lo,
               "ST-EQUIV DS4 bootstrap interval equals an independent recomputation [%.4f, %.4f]" % (lo, hi))
            # DS2 interval, independently (qwen3 1024 - 256 on massive, the same stream)
            t, comp = PB["truth"]["massive"], CS["massive"].comp[PB["evrows"]["massive"]]
            dr = []
            for w in ITS.comp_weights(comp, BOOT_B, np.random.default_rng(BOOT_SEED + 10 * 0 + 1)):
                dr.append(np.mean([ITS.nmi(t, p, w) for p in PB["preds"][("qwen3", 1024, "massive")]])
                          - np.mean([ITS.nmi(t, p, w) for p in PB["preds"][("qwen3", 256, "massive")]]))
            pt = r["ds2"][("qwen3", 1024)]["d"]
            ok(abs((2 * pt - np.percentile(dr, 97.5)) - r["ds2"][("qwen3", 1024)]["lo"]) < 1e-12 and
               abs((2 * pt - np.percentile(dr, 2.5)) - r["ds2"][("qwen3", 1024)]["hi"]) < 1e-12,
               "ST-EQUIV DS2 BASIC interval (qwen3 1024 - 256, massive) equals an independent recomputation")
            # DS3 interval, independently
            q, gm = PB["same"][("qwen3", 1024)], PB["same"][("gemma", 768)]
            dr = []
            for w in ITS.comp_weights(PB["vcomp"], BOOT_B, np.random.default_rng(BOOT_SEED + 4)):
                dr.append(np.mean([(w * s).sum() / w.sum() for s in gm]) - np.mean([(w * s).sum() / w.sum() for s in q]))
            r3 = ds3(PB, 1024, 768)
            ok(abs(np.percentile(dr, 2.5) - r3["lo"]) < 1e-12 and abs(np.percentile(dr, 97.5) - r3["hi"]) < 1e-12,
               "ST-EQUIV DS3 percentile interval equals an independent recomputation (variant components)")
            reset_phase()
    if sel("ST-REFUSE"):
        fx = FX["R"]
        bad = json.loads(json.dumps(fx["identity"]))
        bad["D"]["banking77"] = "%+.5f" % (float(bad["D"]["banking77"]) + 0.00001)
        o, err, _r, od = _run(fx, "idD", identity=bad)
        ok(err and "IDENTITY PRECONDITION FAILED on ['banking77']" in err and not os.path.exists(os.path.join(od, OUTCOME))
           and os.path.exists(os.path.join(od, SELECTION)), "ST-REFUSE identity off by 1e-5 on banking77 (the last corpus) REFUSES; no outcome")
        bad = json.loads(json.dumps(fx["identity"]))
        bad["S"]["gemma"] = "%.4f" % (float(bad["S"]["gemma"]) + 0.0001)
        o, err, _r, od = _run(fx, "idS", identity=bad)
        ok(err and "IDENTITY PRECONDITION FAILED on ['gemma']" in err and not os.path.exists(os.path.join(od, OUTCOME)),
           "ST-REFUSE identity S(gemma) off by 1e-4 REFUSES; no outcome")
        o, err, _r, od = _run(fx, "reg", programme=os.path.join(td, "no_programme.md"))
        ok(err and "not registered" in err and not os.path.exists(od), "ST-REFUSE unregistered: REFUSES before any read")
        od = tempfile.mkdtemp(dir=fx["td"], prefix="exists_")
        os.makedirs(od, exist_ok=True)
        open(os.path.join(od, SELECTION), "w").close()
        o, err, _r, _od = _run(fx, "ex", out_dir=od)
        ok(err and "exists" in err and "selection.json" in err and "pin " not in o, "ST-REFUSE an existing selection.json REFUSES before any read")
        os.remove(os.path.join(od, SELECTION))
        open(os.path.join(od, OUTCOME), "w").close()
        o, err, _r, _od = _run(fx, "ex2", out_dir=od)
        ok(err and "outcome.txt exists" in err, "ST-REFUSE an existing outcome.txt REFUSES")
        pins = json.load(open(fx["pins"]))
        pins["emb"]["gemma"] = "0" * 64
        pf = os.path.join(td, "badpins.json")
        json.dump(pins, open(pf, "w"))
        with _scope(fx):
            ITS.PINS_FILE_OVERRIDE[0] = pf
            o, err, _r = _cap(lambda: main_run(fx["db"], fx["td"], tempfile.mkdtemp(dir=td), fx["prog"], fx["identity"]))
        ok(err and "intent_emb_gemma.db sha256" in err and "!= the pinned" in err, "ST-REFUSE a different gemma pin REFUSES")
        pins["emb"]["gemma"] = None
        json.dump(pins, open(pf, "w"))
        with _scope(fx):
            ITS.PINS_FILE_OVERRIDE[0] = pf
            o, err, _r = _cap(lambda: main_run(fx["db"], fx["td"], tempfile.mkdtemp(dir=td), fx["prog"], fx["identity"]))
        ok(err and "UNPINNED" in err, "ST-REFUSE --run is strict: a null pin REFUSES")
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ['"java.exe","1234"']
            o, err, _r = _cap(lambda: main_run(fx["db"], fx["td"], tempfile.mkdtemp(dir=td), fx["prog"], fx["identity"]))
        ok(err and "foreign heavy process" in err, "ST-REFUSE a running java.exe REFUSES")
        # a DB changed during the readout: copy the fixture, append to gemma's DB after phase B
        cp = os.path.join(tempfile.mkdtemp(dir=td), "R_copy")          # fresh every call: no state shared between mutants
        shutil.copytree(fx["td"], cp, ignore=shutil.ignore_patterns("out_*", "exists_*", "tmp*"))
        fc = dict(fx, td=cp, db=os.path.join(cp, II.DB_NAME), pins=os.path.join(cp, "pins.json"))
        saved_pb = g["phase_b"]

        def pb_then_touch(*a, **k):
            r = saved_pb(*a, **k)
            with open(ITS.emb_path("gemma", cp), "ab") as fh:
                fh.write(b"\0")
            return r
        g["phase_b"] = pb_then_touch
        try:
            o, err, _r, od = _run(fc, "touch")
        finally:
            g["phase_b"] = saved_pb
        ok(err and "gemma sha256 changed during the readout" in err and not os.path.exists(os.path.join(od, OUTCOME)),
           "ST-REFUSE a DB changed during the readout REFUSES; no outcome")
        shutil.rmtree(cp, ignore_errors=True)
    if sel("ST-DRY"):
        fx = FX["N"]
        before = sorted(os.listdir(fx["td"]))
        with _scope(fx):
            o, err, r = _cap(lambda: dry_run(fx["db"], fx["td"], fx["prog"], fx["identity"], timing=True))
        ok(err is None and r == 0, "ST-DRY completes (%s)" % err)
        ok(_line(o, "IDENTITY:").startswith("IDENTITY: D(gemma - qwen3, fine, 256) massive %s / clinc %s / banking77 %s"
                                            % tuple(fx["identity"]["D"][c] for c in CORPORA)), "ST-DRY identity line prints the reproduced digits")
        ok(all(ev[0] == "EVAL" and "@256" in ev[1] for ev in EVENTS) and len(EVENTS) == 2 * len(CORPORA) + 2,
           "ST-DRY by execution: the %d EVAL reads are all on the 256 arms (6 NMI + 2 c4)" % len(EVENTS))
        ok("TIMING: one qwen3@4096 CLINC fine fit" in o and "the 150 fits priced at" in o, "ST-DRY timing and price printed (150 fits)")
        ok("census banking77: TRAIN" in o and "census DS3:" in o and "SELECTION written" not in o, "ST-DRY census lines (GATE / EVAL counts); no selection")
        ok(sorted(os.listdir(fx["td"])) == before and PHASE["selection_sha"] is None and not any(ev[0] == "SELECTION" for ev in EVENTS),
           "ST-DRY writes nothing (fixture directory unchanged) and makes no selection")
        bad = json.loads(json.dumps(fx["identity"]))
        bad["D"]["massive"] = "+9.99999"
        with _scope(fx):
            o, err, r = _cap(lambda: dry_run(fx["db"], fx["td"], fx["prog"], bad, timing=False))
        ok(err and "IDENTITY PRECONDITION FAILED on ['massive']" in err, "ST-DRY refuses a failed identity")
        reset_phase()


MUTANTS = (
    ("tie goes to the larger d", "    return min(d for d in sorted(score) if score[d] >= best - TIE), best\n",
     "    return max(d for d in sorted(score) if score[d] >= best - TIE), best\n", ("ST-UNIT",)),
    ("tie boundary open (> max - 0.001)", "if score[d] >= best - TIE), best\n", "if score[d] > best - TIE), best\n", ("ST-UNIT",)),
    ("tie 0.01", "TIE = 0.001\n", "TIE = 0.01\n", ("ST-CONST",)),
    ("selection: plain argmax (no tie rule)", "        dstar, best = pick(score)\n",
     "        dstar, best = max(SLICES[e], key=lambda d: score[d]), max(score.values())\n", ("ST-UNIT",)),
    ("selection min instead of max", "    best = max(score.values())\n", "    best = min(score.values())\n", ("ST-UNIT", "ST-E2E")),
    ("selection from the first corpus only", "        score = {d: float(np.mean([np.mean(gate[(e, d, c)]) for c in CORPORA])) for d in SLICES[e]}\n",
     "        score = {d: float(np.mean([np.mean(gate[(e, d, c)]) for c in CORPORA[:1]])) for d in SLICES[e]}\n", ("ST-UNIT",)),
    ("selection on EVAL (GATE rows replaced by EVAL)", "            gi = ITS.S_idx(C, S, SS.GATE)\n", "            gi = ITS.S_idx(C, S, SS.EVAL)\n", ("ST-E2E",)),
    ("GATE filed with seed-0 centroids only", "            gate[(e, d, c)] = [ITS.nmi(truth, ITS.assign(S.X[gi], Cm)) for Cm in fits[(e, d, c, \"fine\")]]\n",
     "            gate[(e, d, c)] = [ITS.nmi(truth, ITS.assign(S.X[gi], fits[(e, d, c, \"fine\")][0])) for Cm in fits[(e, d, c, \"fine\")]]\n", ("ST-E2E",)),
    ("arm 4096 dropped", "SLICES = {\"qwen3\": (256, 512, 1024, 4096), \"gemma\": (256, 768)}\n", "SLICES = {\"qwen3\": (256, 512, 1024), \"gemma\": (256, 768)}\n", ("ST-CONST",)),
    ("D* sign flipped (qwen3 - gemma)", "    D = m[(\"gemma\", dg)] - m[(\"qwen3\", dq)]\n", "    D = m[(\"qwen3\", dq)] - m[(\"gemma\", dg)]\n", ("ST-E2E",)),
    ("D* at 256 for both (selection ignored)", "    R[\"ds1\"] = {c: ds1(PB, c, dq, dg) for c in CORPORA}\n", "    R[\"ds1\"] = {c: ds1(PB, c, BASE, BASE) for c in CORPORA}\n", ("ST-E2E",)),
    ("D* from seed 0 only", "    m = {a: float(np.mean(nm[a])) for a in ARMS}\n", "    m = {a: float(nm[a][0]) for a in ARMS}\n", ("ST-E2E", "ST-EQUIV")),
    ("CI percentile instead of BASIC", "    lo, hi = ITS.basic_ci(D, draws)\n    plo", "    lo, hi = ITS.pct_ci(draws)\n    plo", ("ST-EQUIV",)),
    ("bar without the spread", "    bar = max(2.8 * se, max(spread[(\"qwen3\", dq)], spread[(\"gemma\", dg)]))\n", "    bar = 2.8 * se\n", ("ST-EQUIV", "ST-E2E")),
    ("bar spread = min of the two arms", "    bar = max(2.8 * se, max(spread[(\"qwen3\", dq)], spread[(\"gemma\", dg)]))\n",
     "    bar = max(2.8 * se, min(spread[(\"qwen3\", dq)], spread[(\"gemma\", dg)]))\n", ("ST-EQUIV", "ST-E2E")),
    ("MDE80 = 1.96 SE", "    bar = max(2.8 * se,", "    bar = max(1.96 * se,", ("ST-EQUIV", "ST-UNIT")),
    ("bootstrap over items, not components", "    comp = CS_COMP[c][PB[\"evrows\"][c]]\n", "    comp = np.arange(len(PB[\"evrows\"][c]))\n", ("ST-EQUIV",)),
    ("bootstrap draws unweighted", "        mw = {a: float(np.mean([ITS.nmi(t, p, w) for p in", "        mw = {a: float(np.mean([ITS.nmi(t, p) for p in", ("ST-EQUIV",)),
    ("verdict REOPEN on >= 1 BETTER", "    if nb >= 2:\n        return \"REOPEN-CANDIDATE\"", "    if nb >= 1:\n        return \"REOPEN-CANDIDATE\"", ("ST-UNIT", "ST-E2E")),
    ("verdict counts the first two corpora only", "    nb = sum(1 for c in CORPORA if status[c] == \"BETTER\")\n",
     "    nb = sum(1 for c in CORPORA[:2] if status[c] == \"BETTER\")\n", ("ST-UNIT", "ST-E2E")),
    ("KEEP-STRONG on >= 1 WORSE", "    if nw >= 2:\n        return \"KEEP-STRONG\"", "    if nw >= 1:\n        return \"KEEP-STRONG\"", ("ST-UNIT", "ST-E2E")),
    ("F-DS fires on KEEP", "    if v == \"REOPEN-CANDIDATE\":\n        L.append(\"DS1 VERDICT: REOPEN", "    if v != \"REOPEN-CANDIDATE\":\n        L.append(\"DS1 VERDICT: REOPEN", ("ST-UNIT", "ST-E2E")),
    ("KEEP-STRONG reading never printed", "            L.append(\"READING (KEEP-STRONG):", "            (\"READING (KEEP-STRONG):", ("ST-UNIT",)),
    ("MASSIVE caveat never printed", "            L.append(\"READING caveat:", "            (\"READING caveat:", ("ST-UNIT", "ST-E2E")),
    ("relay printed when d_q* = 512", "    if dq != TREE_SLICE:\n", "    if dq == TREE_SLICE:\n", ("ST-UNIT",)),
    ("confounds not on every line", "    return [\"%s %s\" % (ln, CONFOUNDS) for ln in L]\n", "    return [\"%s %s\" % (ln, CONFOUNDS) for ln in L[6:]] and L\n", ("ST-E2E",)),
    ("identity check skipped", "    if bad:\n        refuse(\"IDENTITY", "    if False:\n        refuse(\"IDENTITY", ("ST-REFUSE",)),
    ("identity checks the first corpus only", "    bad = [c for c in CORPORA if got_D[c] != target[\"D\"][c]]", "    bad = [c for c in CORPORA[:1] if got_D[c] != target[\"D\"][c]]", ("ST-REFUSE",)),
    ("identity at 4 dp", "    got_D = {c: \"%+.5f\" % D[c] for c in CORPORA}\n", "    got_D = {c: \"%+.4f0\" % D[c] for c in CORPORA}\n", ("ST-REFUSE", "ST-E2E")),
    ("identity S from seed 1", "    S = {e: float(PB[\"same\"][(e, BASE)][0].mean()) for e in EMB}\n", "    S = {e: float(PB[\"same\"][(e, BASE)][1].mean()) for e in EMB}\n", ("ST-E2E", "ST-EQUIV")),
    ("identity S ignores the embedder", "    S = {e: float(PB[\"same\"][(e, BASE)][0].mean()) for e in EMB}\n", "    S = {e: float(PB[\"same\"][(\"qwen3\", BASE)][0].mean()) for e in EMB}\n", ("ST-E2E", "ST-EQUIV")),
    ("EVAL gate removed", "    if PHASE[\"selection_sha\"] is None and not (PHASE[\"dry_identity\"] and S.d == BASE):\n",
     "    if False:\n", ("ST-GATE",)),
    ("dry identity admits every arm", "and not (PHASE[\"dry_identity\"] and S.d == BASE):\n", "and not PHASE[\"dry_identity\"]:\n", ("ST-GATE",)),
    ("selection written after phase B", [("    sel_sha = write_selection(os.path.join(out_dir, SELECTION), sel, sha0, gate)\n    PB = phase_b(CS, vecs, derived, fits)\n",
                                          "    PHASE[\"selection_sha\"] = \"early\"\n    PB = phase_b(CS, vecs, derived, fits)\n    sel_sha = write_selection(os.path.join(out_dir, SELECTION), sel, sha0, gate)\n")],
     None, ("ST-E2E",)),
    ("selection file not write-once", "    with open(path, \"xb\") as f:\n", "    with open(path, \"wb\") as f:\n", ("ST-REFUSE", "ST-E2E")),
    ("outcome paths not checked", "        if os.path.lexists(p):\n            refuse(\"%s exists", "        if False:\n            refuse(\"%s exists", ("ST-REFUSE",)),
    ("registration not required", "    if not check_registered(programme):\n", "    if False:\n", ("ST-REFUSE",)),
    ("pins not strict at --run", "    sha0, CS, texts, derived = load_inputs(db, emb_dir, True)\n", "    sha0, CS, texts, derived = load_inputs(db, emb_dir, False)\n", ("ST-REFUSE",)),
    ("sha after-check skipped", "        if now != s:\n            refuse(\"%s sha256 changed", "        if False:\n            refuse(\"%s sha256 changed", ("ST-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("ST-REFUSE",)),
    ("full-width read: SLICE2 not set", "    ITS.SLICE2 = NATIVE[e]\n", "    ITS.SLICE2 = 512\n", ("ST-LOAD",)),
    ("full-width read: SLICE2 not restored", "        ITS.SLICE2 = saved\n", "        pass\n", ("ST-LOAD",)),
    ("DS2 curve against 512", "            curve[(e, d)].append(mw[(e, d)] - mw[(e, BASE)])\n", "            curve[(e, d)].append(mw[(e, d)] - mw[(e, SLICES[e][1])])\n", ("ST-E2E", "ST-EQUIV")),
    ("DS2 point against 512", "        pt = m[(e, d)] - m[(e, BASE)]\n", "        pt = m[(e, d)] - m[(e, SLICES[e][1])]\n", ("ST-E2E",)),
    ("DS3 S from seed 0 only", "    S = {a: float(np.mean([s.mean() for s in same[a]])) for a in ARMS}\n", "    S = {a: float(same[a][0].mean()) for a in ARMS}\n", ("ST-E2E",)),
    ("DS3 bootstrap over variants, not components", "    for w in ITS.comp_weights(comp, B, np.random.default_rng(BOOT_SEED + 4)):\n",
     "    for w in ITS.comp_weights(np.arange(len(comp)), B, np.random.default_rng(BOOT_SEED + 4)):\n", ("ST-EQUIV",)),
    ("DS4 bootstrap unweighted", "        M = sps.csr_matrix((w, (inv, rows))", "        M = sps.csr_matrix((np.ones_like(w), (inv, rows))", ("ST-EQUIV",)),
    ("P2 reads 256 vs 512", "        x = R[\"ds1\"][c][\"ds2\"][(\"qwen3\", dq)][\"d\"] if dq != BASE else 0.0\n",
     "        x = R[\"ds1\"][c][\"ds2\"][(\"qwen3\", 512)][\"d\"]\n", ("ST-E2E",)),
    ("P1 Brier on the complement", "        b = brier(p, ev1[name])\n", "        b = brier(p, not ev1[name])\n", ("ST-E2E",)),
    ("P4 KEEP excludes KEEP-STRONG", "    ev4 = {\"KEEP\": v in (\"KEEP\", \"KEEP-STRONG\"),", "    ev4 = {\"KEEP\": v == \"KEEP\",", ("ST-E2E",)),
    ("prediction interval open", "    return ITS._hit(float(v), lo, hi)\n", "    return \"HELD\" if lo < float(v) < hi else \"FAILED\"\n", ("ST-UNIT",)),
    ("dry run writes the selection", "    print(\"%s DRY RUN complete", "    PHASE[\"selection_sha\"] = 'x'\n    print(\"%s DRY RUN complete", ("ST-DRY",)),
    ("dry-run EVAL of 512", "                S = ITS.Space(vecs[e], C, BASE)\n                ev = eval_idx(C, S, \"dry identity",
     "                S = ITS.Space(vecs[e], C, 512)\n                ev = eval_idx(C, S, \"dry identity", ("ST-DRY",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="eds_mut_")
    fx = make_fixtures(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        pairs = old if isinstance(old, list) else [(old, new)]
        code = head
        for o_, n_ in pairs:
            if code.count(o_) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, code.count(o_)))
            code = code.replace(o_, n_)
        ns = {"__name__": "eds_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        finally:
            ITS.SLICE2 = 512
        killed += res.startswith("KILLED")
        print("  %-48s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="EMBED-DIM-SLICE (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-timing", action="store_true", help="--dry-run without the timed 4096-d fit")
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
