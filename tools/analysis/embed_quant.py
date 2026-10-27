"""EMBED-QUANT readout: is qwen3-embedding's Q4_K_M quantisation a confound of the intent-corpus embedder contrasts, i.e. is fine NMI at
d_q* equivalent between Q4_K_M and Q8_0 within the k-means seed spread?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — EMBED-QUANT: is qwen3-embedding's
Q4_K_M quantisation a confound of the intent-corpus embedder contrasts, ...", span L22738-L22760 _as_of 28b4032b (the registrar's
commit; drafted in docs/agents/plans/2026-10-02_next_registrations.md section 4, ce0d0f17). --run REFUSES unless the programme carries
the heading (REG_NEEDLE). Kind: zero-call CPU reader: zero judge calls, zero embeddings (the Q8 file is written by
tools/analysis/embed_quant_writer.py), no build, no pool of record, no GATE row, no embeddings_cache*.db.

INSTRUMENT (imported, never copied): tools/analysis/intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271 (asserted at
every entry point). Its frozen readers and functions: pin_check / raw_pin_check (experiment_configs/intent_transfer_s0_pins.json; --run
strict), load_corpora, text_set, check_meta / expected_meta, load_vectors (run with ITS.SLICE2 = d_q* for the call, restored in a
finally: the first 1024 raw coordinates), Space (first d coordinates, L2-renormalised), km_fit (spherical k-means, k-means++, n_init 1,
max_iter 300, TRAIN fit through fit_rows, the TRAIN-ONLY guard), assign, nmi (arithmetic), comp_weights (CK-CLOSE component
bootstrap), basic_ci, kish. The Q8 file's meta is checked against embed_quant_writer.expected_meta_q8 (its writer blob included).

ARMS: Q4 = qwen3-embedding:latest (Q4_K_M), S0's pinned intent_emb_qwen3.db; Q8 = qwen3-embedding:8b-q8_0, intent_emb_qwen3_q8.db
(pinned by the registrar in experiment_configs/embed_quant_pins.json after the writer completes; --run REFUSES a null pin). Slice
d_q* = 1024 read from EMBED-DIM-SLICE's selection.json (sha256 f1b508cf..., REFUSES another file or another d_q*), both arms. K_f
60 / 150 / 77; k-means seeds 0-19 per arm; EVAL = kept in-scope EVAL rows (CLINC OOS excluded), read once per arm.

IDENTITY (precondition; REFUSES, nothing written): the Q4 arm at 1024, seeds 0-4, reproduces EMBED-DIM-SLICE's qwen3@1024 seed-mean
EVAL fine NMI 0.76554 / 0.92810 / 0.84900 and seed spreads 0.01428 / 0.00417 / 0.01043 (5 dp, "%.5f").

EQ1 (deciding; TOST), per corpus: D_q = mean_{s 0..19} NMI_EVAL(Q8) - mean_{s 0..19} NMI_EVAL(Q4). delta_c = max - min over seeds 0-4
of the Q4 arm's EVAL fine NMI (the 20-seed spreads of both arms printed beside, DESCRIPTIVE). SE_total = sqrt(SE_boot^2 + var_seed /
20); SE_boot = SD (ddof 1) of the paired component-bootstrap draws of D_q (B 2,000, partitions fixed); var_seed = sample variance
(ddof 1) over the 20 seeds of NMI(Q8, s) - NMI(Q4, s). EQUIVALENT iff D_q -/+ 1.645 SE_total lies inside the OPEN interval
(-delta_c, +delta_c); DIFFERENT iff |D_q| > delta_c AND D_q -/+ 1.96 SE_total excludes 0 (direction Q8 HIGHER / LOWER); NEITHER
otherwise. VERDICT: NOT-A-CONFOUND iff EQUIVALENT on >= 2 of 3; CONFOUND-CANDIDATE iff DIFFERENT on >= 2 of 3; MIXED (UNDETERMINED)
otherwise. F-EQ fires iff CONFOUND-CANDIDATE. EQ2 (DESCRIPTIVE-ONLY): per text cos(Q8, Q4) after slicing to 1024 and renormalising,
median and min over the 57,350 texts and per corpus (cos_q.csv: sha256-16 of the text, never the text).

SUPPORT printed per corpus from the run: n, components, Kish DEFF (the EVAL rows' components), n_eff, SE_boot, the seed term, SE_total,
the 90% half-width, the TOST MDE80 2.487 x SE_total and the DIFFERENT MDE delta + 0.842 x SE_total; SCOREABLE iff delta - 0.003 >=
2.487 x SE_total (the registered (f) rule at the predicted |D_q| = 0.003), DESCRIPTIVE-ONLY otherwise. Predictions P1 (Brier per outcome),
P2 (|D_q| in [0.000, 0.010] per corpus), P3 (median cos at 1024 >= 0.98, Brier) scored.

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets):
  QB1 INSTRUMENT: two new scripts (embed_quant_writer.py, embed_quant.py) importing S0 unchanged, NOT a model-tag flag on
      embedder_arms.py and a --quant arm on embed_dim_slice.py as the registration's INSTRUMENT line says: both files' blobs are
      pinned by results of record (S0's embedding DBs, EMBED-DIM-SLICE's run 54ea7329); the orchestrator's brief preferred new scripts.
  QB2 PREFLIGHT "route parity against S0's qwen3 bar 0.9980": applied where it is defined (same model): the writer's T3 repeatability
      and T4 resume parity; cos(Q8, Q4) on the 20 texts is printed with no bar (the orchestrator's brief).
  QB3 SE_boot = SD (ddof 1) of the paired draws; the BASIC interval is printed beside, DESCRIPTIVE; the TOST intervals are the
      registered normal ones on SE_total.
  QB4 bootstrap stream = S0's C1 fine stream (BOOT_SEED + 10 x corpus index + fine level index); one weight vector per draw for both
      arms (paired).
  QB5 EQ2 per corpus = the texts of the corpus's kept rows (CLINC OOS included); overall = every text of the set (variants and pairs).
  QB6 P1 scored as three one-vs-rest Briers; P2 HELD iff 0.000 <= |D_q| <= 0.010 (inclusive), per corpus.

OUTPUT (experiment_results/embed_quant/, every file write-once "x"; an existing path REFUSES before any read): outcome.txt (of record),
nmi_q.csv (arm, corpus, seed, EVAL fine NMI), cos_q.csv.

LAUNCH (run-operator; zero calls; nothing heavy running; after the writer completed and the registrar pinned the Q8 file):
  python tools/analysis/embed_quant.py --selftest      # also runs the writer's selftest
  python tools/analysis/embed_quant.py --mutants
  python tools/analysis/embed_quant.py --dry-run       # pins, selection, census, Q4 identity, Q8 completeness, one timed fit; writes nothing
  python tools/analysis/embed_quant.py --run           # the file of record (write-once)

MUTANT TABLE: `--mutants` (each mutant names the selftest sections that must kill it) and the commit message: 58 of 58 KILLED at
build (57 by an assertion, 'outcome paths not checked' by the mode-x FileExistsError); the writer's own --mutants 21 of 21.
Selftest: 184 checks (fixtures N / C / M plant NOT-A-CONFOUND / CONFOUND-CANDIDATE / MIXED, each recomputed by an independent oracle)
plus the writer's 44. Stubs and fixtures only: no real DB was read and no embedding was posted at build.
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
import embed_quant_writer as W        # noqa: E402
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402
II = ITS.II

TAG = "[EMBED-QUANT]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
ARMS = ("q4", "q8")
D_Q = 1024
SEEDS = tuple(range(20))
DELTA_SEEDS = (0, 1, 2, 3, 4)
BOOT_B = ITS.BOOT_B
BOOT_SEED = ITS.BOOT_SEED
CORPORA = ITS.CORPORA
LEVELS = ITS.LEVELS
Z90, Z95, Z80P = 1.645, 1.96, 0.842
PRED_D = 0.003
IDENTITY = {"mean": {"massive": "0.76554", "clinc": "0.92810", "banking77": "0.84900"},
            "spread": {"massive": "0.01428", "clinc": "0.00417", "banking77": "0.01043"}}
SEL_PATH = os.path.join(ROOT, "experiment_results", "embed_dim_slice", "selection.json")
SEL_SHA = "f1b508cfa889021e6a4d8dac5e82a2188399373996818db0d622aad076bf400d"
PINS_FILE = os.path.join(ROOT, "experiment_configs", "embed_quant_pins.json")
PINS_SCHEMA = "embed_quant_pins/v1"
P1 = (("NOT-A-CONFOUND", 0.70), ("CONFOUND-CANDIDATE", 0.10), ("MIXED", 0.20))
P2 = (0.003, 0.000, 0.010)
P3 = (0.98, 0.85)
VERDICTS = ("NOT-A-CONFOUND", "CONFOUND-CANDIDATE", "MIXED")
OUT_DIR = os.path.join(ROOT, "experiment_results", "embed_quant")
OUTCOME = "outcome.txt"
CSVS = ("nmi_q.csv", "cos_q.csv")
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_NEEDLE = "(before any code or call) \u2014 EMBED-QUANT:"
REG = ("docs/judge_v2_program.md \"## Registered 2026-10-01 (before any code or call) \u2014 EMBED-QUANT: is qwen3-embedding's Q4_K_M "
       "quantisation a confound ...\" L22738-L22760 _as_of 28b4032b; kind zero-call CPU reader")
READINGS = ("builder's readings: QB1 two new scripts importing S0 unchanged (not a flag on embedder_arms.py / a --quant arm on "
            "embed_dim_slice.py); QB2 the 0.998 route-parity bar on the writer's same-model repeatability and resume parity, cos(Q8, Q4) "
            "printed with no bar; QB3 SE_boot = SD of the paired draws, BASIC interval descriptive; QB4 S0's C1 fine bootstrap stream, "
            "paired; QB5 EQ2 per corpus over its kept rows' texts, overall over the set; QB6 P1 one-vs-rest Briers, P2 inclusive interval")
DOES_NOT_SHOW = ("DOES NOT SHOW: anything about F16 or full precision (Q8_0 is itself quantised); gemma's precision (BF16, untested); "
                 "slices other than 1024 or card prompts; MMLU-Pro or capability text; that gemma is a better embedder or any change to "
                 "the embedder of record (D3 is the author's); parity on CLINC if it reads NEITHER")
EVENTS = []


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_its_blob():
    got = RO.git_blob_lf(ITS.__file__)
    if got != ITS_BLOB:
        refuse("intent_transfer_s0.py is blob %s, not %s: S0's machinery must be imported unchanged" % (got, ITS_BLOB))
    return got


_foreign_heavy = ITS._foreign_heavy


def heavy_check():
    heavy = _foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a foreign heavy process runs (%s): never beside a construction, a site null or an Ollama pass" % heavy[:3])


def check_registered(programme):
    ok = os.path.isfile(programme) and REG_NEEDLE in open(programme, encoding="utf-8").read()
    print("%s registration heading %r in %s: %s" % (TAG, REG_NEEDLE, os.path.basename(programme), "PRESENT" if ok else "ABSENT"))
    return ok


def read_selection(path, want_sha):
    with open(path, "rb") as f:
        raw = f.read()
    data = raw.replace(b"\r\n", b"\n")           # the LF rendering is of record (a CRLF checkout hashes otherwise)
    sha = hashlib.sha256(data).hexdigest()
    print("%s selection %s sha256 (LF rendering) %s%s [%s]" % (TAG, path, sha, "" if raw == data else " (CRLF working-tree sha256 %s)"
                                                               % hashlib.sha256(raw).hexdigest(), "PIN OK" if sha == want_sha else "PIN MISMATCH"))
    if sha != want_sha:
        refuse("EMBED-DIM-SLICE's selection.json sha256 %s != %s" % (sha, want_sha))
    dq = json.loads(data.decode("utf-8")).get("d_q*")
    print("%s d_q* = %s (registered %d; no slice is reselected)" % (TAG, dq, D_Q))
    if dq != D_Q:
        refuse("selection.json d_q* %s != the registered %d" % (dq, D_Q))
    return sha


def q8_pin_check(path, strict, pins_file=None):
    pf = pins_file or PINS_FILE
    want = None
    if os.path.isfile(pf):
        with open(pf, encoding="utf-8") as f:
            pins = json.load(f)
        if pins.get("schema") != PINS_SCHEMA:
            refuse("%s schema %r != %r" % (pf, pins.get("schema"), PINS_SCHEMA))
        want = pins.get("q8")
    II.open_db_ro(path).close()
    s = II.file_sha(path)
    print("%s pin intent_emb_qwen3_q8.db: sha256 %s [%s]" % (TAG, s, "UNPINNED" if not want else ("PIN OK" if want == s else "PIN MISMATCH")))
    if want and want != s:
        refuse("%s sha256 %s != the pinned %s" % (path, s, want))
    if strict and not want:
        refuse("%s is UNPINNED: --run reads the Q8 file only against the registrar's pin (%s)" % (path, pf))
    return s


PINS_OVERRIDE = [None]


def emb_file(arm, emb_dir):
    return ITS.emb_path("qwen3", emb_dir) if arm == "q4" else W.q8_path(emb_dir)


def load_inputs(db, emb_dir, strict, need_q8=True):
    sha0 = {"ingest_db": ITS.pin_check(db, "ingest_db", strict)}
    ITS.raw_pin_check(db, strict)
    sha0["q4"] = ITS.pin_check(emb_file("q4", emb_dir), "emb", strict, sub="qwen3", label="intent_emb_qwen3.db")
    if need_q8:
        sha0["q8"] = q8_pin_check(emb_file("q8", emb_dir), strict, PINS_OVERRIDE[0])
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    ITS.check_meta(emb_file("q4", emb_dir), ITS.expected_meta("qwen3", set_sha, len(texts), sha0["ingest_db"]))
    if need_q8:
        ITS.check_meta(emb_file("q8", emb_dir), W.expected_meta_q8(set_sha, len(texts), sha0["ingest_db"]))
    return sha0, CS, texts, set_sha


def after_check(sha0, db, emb_dir):
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else emb_file(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))


def load_slice(path, arm, texts, allow_missing=False):
    """S0's load_vectors at d_q* (ITS.SLICE2 set for the call, restored in a finally); Q8 under the in-memory tag registration."""
    saved = ITS.SLICE2
    ITS.SLICE2 = D_Q
    try:
        if arm == "q8":
            with W.q8_registered():
                v = ITS.load_vectors(path, W.E_Q8, texts, allow_missing=allow_missing)
        else:
            v = ITS.load_vectors(path, "qwen3", texts, allow_missing=allow_missing)
    finally:
        ITS.SLICE2 = saved
    bad = sum(1 for x in v.values() if len(x) != D_Q)
    if bad:
        refuse("%s: %d vectors are not %d-d after the slice read" % (arm, bad, D_Q))
    return v


# ------------------------------------------------------------------------------------------------ fits and EVAL
def arm_eval(C, vecs, arm, seeds):
    """TRAIN fits (seeds) at d_q*, EVAL filed to them (EVAL read once for the arm). -> (EVAL rows, truth, preds, NMI per seed)."""
    S = ITS.Space(vecs, C, D_Q)
    kf = II.GOLD_K[C.name][1]
    fits = [ITS.km_fit(C, S, kf, s, "EQ k-means %s@%d %s fine K=%d s%d" % (arm, D_Q, C.name, kf, s)) for s in seeds]
    ev = ITS.S_idx(C, S, SS.EVAL)
    EVENTS.append(("EVAL", "%s %s" % (arm, C.name)))
    truth = ITS.codes(C.fine[ev])
    preds = [ITS.assign(S.X[ev], Cm) for Cm in fits]
    return ev, truth, preds, [ITS.nmi(truth, p) for p in preds]


def identity_values(nm_q4):
    """Q4 seeds 0-4 (the first five of SEEDS): seed-mean and spread."""
    x = nm_q4[:len(DELTA_SEEDS)]
    return float(np.mean(x)), float(max(x) - min(x))


def identity_check(vals, target):
    got = {c: ("%.5f" % vals[c][0], "%.5f" % vals[c][1]) for c in CORPORA}
    bad = [c for c in CORPORA if got[c] != (target["mean"][c], target["spread"][c])]
    line = ("IDENTITY: Q4 @%d seeds 0-4 seed-mean EVAL fine NMI %s (EMBED-DIM-SLICE %s), seed spread %s (EMBED-DIM-SLICE %s)"
            % (D_Q, " / ".join(got[c][0] for c in CORPORA), " / ".join(target["mean"][c] for c in CORPORA),
               " / ".join(got[c][1] for c in CORPORA), " / ".join(target["spread"][c] for c in CORPORA)))
    print("%s %s" % (TAG, line))
    if bad:
        refuse("IDENTITY PRECONDITION FAILED on %s: EMBED-DIM-SLICE's qwen3@1024 is not reproduced to 5 dp; no readout is written" % bad)
    return line + " -> REPRODUCED"


def status(D, delta, lo90, hi90, lo95, hi95):
    if lo90 > -delta and hi90 < delta:
        return "EQUIVALENT"
    if abs(D) > delta and (lo95 > 0 or hi95 < 0):
        return "DIFFERENT"
    return "NEITHER"


def eq1(c, truth, comp, preds, nm, B=None):
    """EQ1 for one corpus. preds / nm: {arm: per-seed list} over SEEDS."""
    B = BOOT_B if B is None else B
    m = {a: float(np.mean(nm[a])) for a in ARMS}
    D = m["q8"] - m["q4"]
    draws = []
    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index("fine"))
    for w in ITS.comp_weights(comp, B, rng):
        mw = {a: float(np.mean([ITS.nmi(truth, p, w) for p in preds[a]])) for a in ARMS}
        draws.append(mw["q8"] - mw["q4"])
    se_boot = float(np.std(draws, ddof=1))
    dseed = np.array(nm["q8"]) - np.array(nm["q4"])
    var_seed = float(np.var(dseed, ddof=1))
    seed_term = float(np.sqrt(var_seed / len(SEEDS)))
    se = float(np.sqrt(se_boot ** 2 + var_seed / len(SEEDS)))
    q4d = nm["q4"][:len(DELTA_SEEDS)]
    delta = float(max(q4d) - min(q4d))
    lo90, hi90, lo95, hi95 = D - Z90 * se, D + Z90 * se, D - Z95 * se, D + Z95 * se
    blo, bhi = ITS.basic_ci(D, draws)
    kish = ITS.kish(comp)
    st = status(D, delta, lo90, hi90, lo95, hi95)
    return {"D": D, "m": m, "se_boot": se_boot, "var_seed": var_seed, "seed_term": seed_term, "se": se, "delta": delta,
            "lo90": lo90, "hi90": hi90, "lo95": lo95, "hi95": hi95, "blo": blo, "bhi": bhi, "status": st,
            "direction": ("Q8 HIGHER" if D > 0 else "Q8 LOWER") if st == "DIFFERENT" else "",
            "spread20": {a: float(max(nm[a]) - min(nm[a])) for a in ARMS}, "n": int(len(truth)), "components": int(len(np.unique(comp))),
            "kish": kish, "n_eff": len(truth) / kish, "mde_tost": (Z90 + Z80P) * se, "mde_diff": delta + Z80P * se,
            "scoreable": (delta - PRED_D) >= (Z90 + Z80P) * se, "nm": nm}


def verdict(st):
    ne = sum(1 for c in CORPORA if st[c] == "EQUIVALENT")
    nd = sum(1 for c in CORPORA if st[c] == "DIFFERENT")
    if ne >= 2:
        return "NOT-A-CONFOUND", ne, nd
    if nd >= 2:
        return "CONFOUND-CANDIDATE", ne, nd
    return "MIXED", ne, nd


def eq2(texts, v4, v8, CS):
    """Per text cos(Q8, Q4) after the 1024 slice + renormalise. -> (cos array aligned with texts, summary dict)."""
    cos = np.empty(len(texts))
    for i0 in range(0, len(texts), 4096):
        ch = texts[i0:i0 + 4096]
        A = np.array([v4[t] for t in ch], dtype=np.float64)
        Bm = np.array([v8[t] for t in ch], dtype=np.float64)
        cos[i0:i0 + len(ch)] = (A * Bm).sum(1) / (np.linalg.norm(A, axis=1) * np.linalg.norm(Bm, axis=1))
    pos = {t: i for i, t in enumerate(texts)}
    summ = {"all": (float(np.median(cos)), float(cos.min()), len(texts), hashlib.sha256(texts[int(np.argmin(cos))].encode("utf-8")).hexdigest()[:16])}
    for c in CORPORA:
        C = CS[c]
        idx = sorted(set(pos[C.text[i]] for i in np.nonzero(C.kept)[0]))
        x = cos[idx]
        summ[c] = (float(np.median(x)), float(x.min()), len(idx), None)
    return cos, summ


# ------------------------------------------------------------------------------------------------ lines
def _hit(v, lo, hi):
    return "HELD" if (np.isfinite(v) and lo <= v <= hi) else "FAILED"


def support_lines(R):
    L = []
    for c in CORPORA:
        r = R["eq1"][c]
        L.append("SUPPORT %s: n %d EVAL items in %d components, Kish DEFF %.4f, n_eff %.0f; SE_boot %.5f (B %d), seed term sqrt(var_seed/20) "
                 "%.5f, SE_total %.5f; 90%% half-width %.5f; TOST MDE80 2.487 x SE_total %.5f; DIFFERENT MDE delta + 0.842 x SE_total %.5f; "
                 "delta_c %.5f; at the predicted |D_q| %.3f: delta - |D| %.5f %s 2.487 x SE_total -> %s"
                 % (c, r["n"], r["components"], r["kish"], r["n_eff"], r["se_boot"], R["B"], r["seed_term"], r["se"], Z90 * r["se"],
                    r["mde_tost"], r["mde_diff"], r["delta"], PRED_D, r["delta"] - PRED_D, ">=" if r["scoreable"] else "<",
                    "SCOREABLE" if r["scoreable"] else "DESCRIPTIVE-ONLY"))
    return L


def criteria_lines(R):
    L = []
    for c in CORPORA:
        r = R["eq1"][c]
        L.append("EQ1 %s: D_q = Q8 %.5f - Q4 %.5f = %+.5f (seeds 0-19; denominator %d EVAL items); delta_c %.5f (Q4 seeds 0-4); SE_total %.5f; "
                 "90%% [%+.5f, %+.5f]; 95%% [%+.5f, %+.5f]; BASIC bootstrap 95%% [%+.5f, %+.5f] (descriptive); 20-seed spreads Q4 %.5f / Q8 %.5f "
                 "(descriptive) -> %s%s"
                 % (c, r["m"]["q8"], r["m"]["q4"], r["D"], r["n"], r["delta"], r["se"], r["lo90"], r["hi90"], r["lo95"], r["hi95"],
                    r["blo"], r["bhi"], r["spread20"]["q4"], r["spread20"]["q8"], r["status"],
                    (" (" + r["direction"] + ")") if r["direction"] else ""))
    v, ne, nd = R["verdict"]
    if v == "NOT-A-CONFOUND":
        L.append("EQ1 VERDICT: NOT-A-CONFOUND (EQUIVALENT on %d of 3, DIFFERENT on %d of 3)" % (ne, nd))
    elif v == "CONFOUND-CANDIDATE":
        dirs = ", ".join("%s %s" % (c, R["eq1"][c]["direction"]) for c in CORPORA if R["eq1"][c]["status"] == "DIFFERENT")
        L.append("EQ1 VERDICT: CONFOUND-CANDIDATE (DIFFERENT on %d of 3: %s; EQUIVALENT on %d of 3)" % (nd, dirs, ne))
    else:
        L.append("EQ1 VERDICT: MIXED (UNDETERMINED; EQUIVALENT on %d of 3, DIFFERENT on %d of 3)" % (ne, nd))
    if v == "CONFOUND-CANDIDATE":
        L.append("F-EQ: FIRED -- the Q4 tag as \"qwen3\" is overturned in every intent-corpus embedder contrast (S0 C1a, SLOTSWAP M3, "
                 "EMBED-DIM-SLICE DS1, CARD-PROTOCOL CP1); those rows carry \"Q4_K_M; the higher-precision model differs\"")
    else:
        L.append("F-EQ: NOT FIRED")
    if v == "NOT-A-CONFOUND":
        L.append("CONSEQUENCE: the quantisation half of EMBED-DIM-SLICE's W2 confound line is discharged for qwen3 at d_q* 1024 only "
                 "(prompts stay until CP1)")
    elif v == "MIXED":
        L.append("CONSEQUENCE: MIXED leaves the confound line as written")
    if R["eq1"]["clinc"]["status"] == "NEITHER":
        L.append("NOTE: CLINC NEITHER was expected at the planned n (Support (f)) and is not evidence of a confound")
    return L


def eq2_lines(R):
    s = R["eq2"]
    L = ["EQ2 (DESCRIPTIVE-ONLY) cos(Q8, Q4) per text after slice %d + renormalise: all %d texts median %.6f min %.6f (text sha256-16 %s)"
         % (D_Q, s["all"][2], s["all"][0], s["all"][1], s["all"][3])]
    for c in CORPORA:
        L.append("EQ2 %s: %d texts median %.6f min %.6f" % (c, s[c][2], s[c][0], s[c][1]))
    return L


def predictions_lines(R):
    v = R["verdict"][0]
    L = []
    for name, p in P1:
        ev = v == name
        L.append("P1 %s p %.2f: event %s, Brier %.4f" % (name, p, "TRUE" if ev else "FALSE", (p - (1.0 if ev else 0.0)) ** 2))
    held = 0
    for c in CORPORA:
        a = abs(R["eq1"][c]["D"])
        h = _hit(a, P2[1], P2[2])
        held += h == "HELD"
        L.append("P2 %s: |D_q| %.5f vs %.3f [%.3f, %.3f] -> %s" % (c, a, P2[0], P2[1], P2[2], h))
    L.append("P2: HELD on %d of 3" % held)
    med = R["eq2"]["all"][0]
    ev = med >= P3[0]
    L.append("P3 median cos(Q8, Q4) at %d >= %.2f p %.2f: median %.6f, event %s, Brier %.4f" % (D_Q, P3[0], P3[1], med, "TRUE" if ev else "FALSE",
                                                                                                (P3[1] - (1.0 if ev else 0.0)) ** 2))
    return L


def out_paths(out_dir):
    return [os.path.join(out_dir, p) for p in (OUTCOME,) + CSVS]


def main_run(db=None, emb_dir=None, out_dir=OUT_DIR, programme=PROGRAMME, identity=None, sel_path=SEL_PATH, sel_sha=SEL_SHA, B=None):
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    identity = identity or IDENTITY
    B = BOOT_B if B is None else B
    del EVENTS[:]
    print("%s pool of record: none read (S0's DBs and the Q8 file); zero calls; no embeddings; no GATE row" % TAG)
    for p in out_paths(out_dir):
        if os.path.lexists(p):
            refuse("%s exists: every output of record is write-once" % p)
    check_its_blob()
    heavy_check()
    if not check_registered(programme):
        refuse("EMBED-QUANT is not registered in %s: --run writes a record only after the registration" % programme)
    selsha = read_selection(sel_path, sel_sha)
    sha0, CS, texts, set_sha = load_inputs(db, emb_dir, True)
    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts) for a in ARMS}
    del ITS.FIT_LOG[:]
    R = {"eq1": {}, "B": B}
    idv = {}
    for c in CORPORA:
        C = CS[c]
        out = {a: arm_eval(C, vecs[a], a, SEEDS) for a in ARMS}
        if not np.array_equal(out["q4"][0], out["q8"][0]):
            refuse("%s: the EVAL rows differ between arms (a vector missing)" % c)
        idv[c] = identity_values(out["q4"][3])
        R["eq1"][c] = {"_ev": out["q4"][0], "_truth": out["q4"][1], "_preds": {a: out[a][2] for a in ARMS}, "_nm": {a: out[a][3] for a in ARMS}}
    id_line = identity_check(idv, identity)
    for c in CORPORA:
        x = R["eq1"][c]
        R["eq1"][c] = eq1(c, x["_truth"], CS[c].comp[x["_ev"]], x["_preds"], x["_nm"], B=B)
    R["verdict"] = verdict({c: R["eq1"][c]["status"] for c in CORPORA})
    cos, R["eq2"] = eq2(texts, vecs["q4"], vecs["q8"], CS)
    audit = ITS.fit_audit()
    n_ev = sum(1 for e in EVENTS if e[0] == "EVAL")
    after_check(sha0, db, emb_dir)
    L = ["EMBED-QUANT outcome (tools/analysis/embed_quant.py blob %s; writer embed_quant_writer.py blob %s; S0 machinery intent_transfer_s0.py "
         "blob %s, imported unchanged)" % (RO.git_blob_lf(os.path.abspath(__file__)), W.writer_blob(), ITS_BLOB),
         "registration: " + REG,
         "zero judge calls; zero embeddings; no build; no GATE row; pool of record: none read; pins re-checked before and after, unchanged: %s"
         % {k: v[:16] for k, v in sha0.items()},
         "arms: Q4 %s (intent_emb_qwen3.db) vs Q8 %s (intent_emb_qwen3_q8.db); slice d_q* %d from selection.json sha256 %s; seeds 0-19; "
         "EVAL read %d times (once per arm per corpus)" % (W.MODEL_Q4, W.MODEL_Q8, D_Q, selsha, n_ev),
         READINGS, audit, id_line]
    L += support_lines(R) + criteria_lines(R) + eq2_lines(R) + predictions_lines(R) + [DOES_NOT_SHOW]
    for ln in L:
        print(ln)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, OUTCOME), "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(out_dir, CSVS[0]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["arm", "model", "slice", "corpus", "level", "side", "seed", "nmi"])
        for c in CORPORA:
            for a in ARMS:
                for s, x in zip(SEEDS, R["eq1"][c]["nm"][a]):
                    w.writerow([a, W.MODEL_Q4 if a == "q4" else W.MODEL_Q8, D_Q, c, "fine", "EVAL", s, "%.6f" % x])
    with open(os.path.join(out_dir, CSVS[1]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["text_sha256_16", "cos_q8_q4_1024"])
        for t, x in zip(texts, cos):
            w.writerow([hashlib.sha256(t.encode("utf-8")).hexdigest()[:16], "%.6f" % x])
    print("%s wrote %s (write-once, of record)" % (TAG, os.path.join(out_dir, OUTCOME)))
    R["lines"] = L
    return R


def dry_run(db=None, emb_dir=None, programme=PROGRAMME, identity=None, sel_path=SEL_PATH, sel_sha=SEL_SHA, timing=True):
    """Pins, selection, census, the Q4 identity (seeds 0-4, values of record), Q8 completeness, one timed fit. Writes nothing."""
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    identity = identity or IDENTITY
    del EVENTS[:]
    print("%s pool of record: none read; zero calls; DRY RUN: nothing written" % TAG)
    check_its_blob()
    heavy_check()
    check_registered(programme)
    read_selection(sel_path, sel_sha)
    q8p = emb_file("q8", emb_dir)
    have_q8 = os.path.exists(q8p)
    sha0, CS, texts, set_sha = load_inputs(db, emb_dir, False, need_q8=have_q8)
    for c in CORPORA:
        C = CS[c]
        ev = C.idx(SS.EVAL)
        k = ITS.kish(C.comp[ev])
        print("%s census %s: TRAIN %d, EVAL %d in %d components (Kish DEFF %.4f, n_eff %.0f); GATE not read"
              % (TAG, c, len(C.idx(SS.TRAIN)), len(ev), len(np.unique(C.comp[ev])), k, len(ev) / k))
    if have_q8:
        v8 = load_slice(q8p, "q8", texts, allow_missing=True)
        print("%s Q8 file %s: %d of %d texts present (%d missing)%s" % (TAG, q8p, len(v8), len(texts), len(texts) - len(v8),
                                                                         "" if len(v8) == len(texts) else ": --run REFUSES until COMPLETE"))
        del v8
    else:
        print("%s Q8 file %s absent: run tools/analysis/embed_quant_writer.py --embed --go first" % (TAG, q8p))
    v4 = load_slice(emb_file("q4", emb_dir), "q4", texts)
    del ITS.FIT_LOG[:]
    idv = {}
    for c in CORPORA:
        _ev, _t, _p, nm = arm_eval(CS[c], v4, "q4", DELTA_SEEDS)
        idv[c] = identity_values(nm)
    identity_check(idv, identity)
    if timing:
        C = CS["clinc"]
        S = ITS.Space(v4, C, D_Q)
        kf = II.GOLD_K["clinc"][1]
        t0 = time.time()
        ITS.km_fit(C, S, kf, 0, "EQ dry timing q4@%d clinc s0" % D_Q)
        dt = time.time() - t0
        print("%s TIMING: one %d-d CLINC fine fit %.1f s; the run's %d fits priced at about %.0f s plus %d bootstrap draws x 3 corpora"
              % (TAG, D_Q, dt, len(SEEDS) * len(ARMS) * len(CORPORA), dt * len(SEEDS) * len(ARMS) * len(CORPORA), BOOT_B))
    after_check(sha0, db, emb_dir)
    print("%s %s" % (TAG, ITS.fit_audit()))
    print("%s DRY RUN complete: nothing written" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest fixtures
NAT = 4096
FX_SIG = 1.6                              # Q4 cloud noise (dims 0-19): overlapping fine intents -> a seed spread > 0
# Q8 mode per corpus: same (byte copy), garble (no class signal), sharp (less noise -> higher NMI), noisy (Q4 + extra noise)
FX_SPEC = {
    "N": {"massive": "garble", "clinc": "same", "banking77": "same"},       # EQUIVALENT 2, DIFFERENT 1 -> NOT-A-CONFOUND
    "C": {"massive": "same", "clinc": "garble", "banking77": "sharp"},      # DIFFERENT 2 (LOWER, HIGHER) -> CONFOUND-CANDIDATE
    "M": {"massive": "noisy", "clinc": "garble", "banking77": "same"},      # NEITHER / DIFFERENT / EQUIVALENT -> MIXED
}
FX_EXPECT = {"N": ("NOT-A-CONFOUND", {"massive": "DIFFERENT", "clinc": "EQUIVALENT", "banking77": "EQUIVALENT"}),
             "C": ("CONFOUND-CANDIDATE", {"massive": "EQUIVALENT", "clinc": "DIFFERENT", "banking77": "DIFFERENT"}),
             "M": ("MIXED", {"massive": "NEITHER", "clinc": "DIFFERENT", "banking77": "EQUIVALENT"})}


def _rng(*parts):
    return np.random.default_rng(int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12], 16))


def _q4vec(f, t):
    v = np.zeros(NAT)
    r = _rng("q4", t)
    if f is not None:
        v[f] += 3.0
        v[16 + f % 4] += 1.0
    v[:20] += FX_SIG * r.normal(size=20)
    v[20:] += 0.01 * r.normal(size=NAT - 20)
    return v


def _q8vec(mode, f, t, q4):
    r = _rng("q8", mode, t)
    if mode == "same":
        return q4
    if mode == "garble":
        v = np.zeros(NAT)
        v[:20] = 2.0 * r.normal(size=20)
        v[20:] = 0.01 * r.normal(size=NAT - 20)
        return v
    if mode == "sharp":
        v = q4.copy()
        if f is not None:
            v[:20] = 0.0
            v[f] += 3.0
            v[16 + f % 4] += 1.0
            v[:20] += 0.3 * r.normal(size=20)
        return v
    if mode == "noisy":
        return q4 + 1.2 * r.normal(size=NAT) * (np.arange(NAT) < 20)
    raise ValueError(mode)


def _write_emb(path, meta, V, texts):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(meta.items()))
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(V[t], dtype=">f4").tobytes()) for t in texts])
    con.commit()
    con.close()


def build_fixture(td, name):
    """S0's synthetic rows; planted Q4 (4096-d) and Q8 (per FX_SPEC) DBs with their metas; S0 and Q8 pins files; a programme with the
    heading; a selection.json (d_q* 1024); the identity target from an independent oracle."""
    spec = FX_SPEC[name]
    rows = ITS._fixture_rows()
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows, [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    lab = {}
    for C in CS.values():
        for i in np.nonzero(C.kept)[0]:
            lab[C.text[i]] = (C.name, None if C.oos[i] else int(C.fine[i][-2:]))
    ingest_sha = II.file_sha(db)
    V4, V8 = {}, {}
    for t in texts:
        c, f = lab.get(t, (None, None))
        V4[t] = _q4vec(f, t)
        V8[t] = _q8vec(spec[c], f, t, V4[t]) if c else V4[t] + 0.05 * _rng("d", t).normal(size=NAT)
    _write_emb(ITS.emb_path("qwen3", td), dict(ITS.expected_meta("qwen3", set_sha, len(texts), ingest_sha), model_digest="stub"), V4, texts)
    _write_emb(W.q8_path(td), dict(W.expected_meta_q8(set_sha, len(texts), ingest_sha), model_digest="stubq8"), V8, texts)
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": II.file_sha(db), "emb": {"qwen3": II.file_sha(ITS.emb_path("qwen3", td))}}, fh)
    qpins = os.path.join(td, "q8pins.json")
    with open(qpins, "w") as fh:
        json.dump({"schema": PINS_SCHEMA, "q8": II.file_sha(W.q8_path(td))}, fh)
    prog = os.path.join(td, "programme.md")
    with open(prog, "w", encoding="utf-8") as fh:
        fh.write("## Registered 2026-10-01 %s fixture\n" % REG_NEEDLE)
    sel = os.path.join(td, "selection.json")
    with open(sel, "wb") as fh:
        fh.write(json.dumps({"d_q*": D_Q, "d_g*": 768}).encode("utf-8"))
    fx = {"td": td, "db": db, "pins": pins, "qpins": qpins, "prog": prog, "sel": sel, "sel_sha": II.file_sha(sel), "name": name, "texts": texts}
    fx["oracle"] = _oracle(fx)
    fx["identity"] = {"mean": {c: "%.5f" % fx["oracle"][c]["id_mean"] for c in CORPORA},
                      "spread": {c: "%.5f" % fx["oracle"][c]["id_spread"] for c in CORPORA}}
    return fx


def _wnmi(t, p, w):
    """An independent weighted arithmetic NMI (own contingency via a dict; natural logs)."""
    cont = {}
    for a, b, x in zip(t, p, w):
        if x:
            cont[(a, b)] = cont.get((a, b), 0.0) + x
    n = sum(cont.values())
    pa, pb = {}, {}
    for (a, b), x in cont.items():
        pa[a] = pa.get(a, 0.0) + x
        pb[b] = pb.get(b, 0.0) + x
    if len(pa) == 1 and len(pb) == 1:
        return 1.0
    mi = sum(x / n * np.log((x / n) / ((pa[a] / n) * (pb[b] / n))) for (a, b), x in cont.items())
    ha = -sum(x / n * np.log(x / n) for x in pa.values())
    hb = -sum(x / n * np.log(x / n) for x in pb.values())
    return 0.0 if mi <= 0 else mi / ((ha + hb) / 2.0)


def _oracle(fx, B=200):
    """INDEPENDENT recomputation: own sqlite read, own slice + renormalise, own side masks, sklearn NMI for points, own weighted NMI and
    own component resampling (numpy Generator.integers, the documented CK-CLOSE rule) for the bootstrap; only S0's skmeans is shared."""
    from sklearn.metrics import normalized_mutual_info_score as NMI
    CS = ITS.load_corpora(fx["db"])
    raw = {}
    for a, p in (("q4", ITS.emb_path("qwen3", fx["td"])), ("q8", W.q8_path(fx["td"]))):
        con = sqlite3.connect(p)
        raw[a] = {t: np.frombuffer(b, dtype=">f4").astype(np.float64)[:D_Q] for t, b in con.execute("SELECT query, vector FROM embeddings")}
        con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    out = {}
    for ci, c in enumerate(CORPORA):
        C = CS[c]
        msk = lambda sd: [i for i in range(len(C.text)) if C.kept[i] and not C.oos[i] and C.side[i] == sd]
        tr, ev = msk(SS.TRAIN), msk(SS.EVAL)
        truth = list(C.fine[ev])
        preds, nm = {}, {}
        for a in ARMS:
            Xtr = U(np.array([raw[a][C.text[i]] for i in tr]))
            Xe = U(np.array([raw[a][C.text[i]] for i in ev]))
            preds[a] = [np.argmax(Xe @ ITS.skmeans(Xtr, II.GOLD_K[c][1], s).T, 1) for s in SEEDS]
            nm[a] = [NMI(truth, p, average_method="arithmetic") for p in preds[a]]
        D = np.mean(nm["q8"]) - np.mean(nm["q4"])
        stems = [C.stem[i] for i in ev]
        ustem = sorted(set(stems))
        msz = np.array([stems.count(u) for u in ustem], dtype=float)
        kish = float((msz ** 2).sum() / msz.sum())
        gidx = np.array([ustem.index(s) for s in stems])
        rng = np.random.default_rng(BOOT_SEED + 10 * ci + LEVELS[c].index("fine"))
        draws = []
        for _ in range(B):
            cnt = np.bincount(rng.integers(len(ustem), size=len(ustem)), minlength=len(ustem))
            w = cnt[gidx].astype(float)
            draws.append(np.mean([_wnmi(truth, p, w) for p in preds["q8"]]) - np.mean([_wnmi(truth, p, w) for p in preds["q4"]]))
        seb = np.std(draws, ddof=1)
        d = np.array(nm["q8"]) - np.array(nm["q4"])
        se = np.sqrt(seb ** 2 + np.var(d, ddof=1) / 20.0)
        delta = max(nm["q4"][:5]) - min(nm["q4"][:5])
        if D - 1.645 * se > -delta and D + 1.645 * se < delta:
            st = "EQUIVALENT"
        elif abs(D) > delta and (D - 1.96 * se > 0 or D + 1.96 * se < 0):
            st = "DIFFERENT"
        else:
            st = "NEITHER"
        cos = []
        for t in sorted(set(C.text[i] for i in np.nonzero(C.kept)[0])):
            x, y = raw["q4"][t], raw["q8"][t]
            cos.append(float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y))))
        out[c] = {"D": D, "se": se, "seb": seb, "delta": delta, "status": st, "q4": np.mean(nm["q4"]), "q8": np.mean(nm["q8"]),
                  "id_mean": np.mean(nm["q4"][:5]), "id_spread": delta, "cos_med": float(np.median(cos)),
                  "cos_min": min(cos), "n": len(ev), "var_seed": np.var(d, ddof=1), "kish": kish, "comps": len(ustem)}
    allc = []
    for t in fx["texts"]:
        x, y = raw["q4"][t], raw["q8"][t]
        allc.append(float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y))))
    out["all"] = (float(np.median(allc)), min(allc))
    return out


@contextlib.contextmanager
def _scope(fx, B=200):
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], PINS_OVERRIDE[0], g["BOOT_B"], ITS.DATA_ROOT)
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        PINS_OVERRIDE[0] = fx["qpins"] if fx else None
        ITS.DATA_ROOT = fx["td"] if fx else tempfile.gettempdir()
        g["BOOT_B"] = B
        try:
            yield
        finally:
            g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], PINS_OVERRIDE[0], g["BOOT_B"], ITS.DATA_ROOT = saved


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
    got = [ln for ln in lines if ln.startswith(prefix)]
    return got[-1] if got else ""


def _run(fx, tag, **kw):
    out_dir = os.path.join(fx["td"], "out_%s_%d" % (tag, len(os.listdir(fx["td"]))))
    args = dict(db=fx["db"], emb_dir=fx["td"], out_dir=out_dir, programme=fx["prog"], identity=fx["identity"], sel_path=fx["sel"],
                sel_sha=fx["sel_sha"], B=200)
    args.update(kw)
    with _scope(fx):
        o, err, res = _cap(lambda: main_run(**args))
    return o, err, res, out_dir


def selftest(only=None, quiet=False, fixture=None, writer=True):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    if fixture is None:
        td = tempfile.mkdtemp(prefix="eq_st_")
        try:
            _selftest(sel, ok, make_fixtures(td))
        finally:
            shutil.rmtree(td, ignore_errors=True)
    else:
        _selftest(sel, ok, fixture)
    if not quiet:
        print("SELFTEST (readout): %d checks passed" % n[0])
    if writer and only is None:
        W.selftest(quiet=quiet)
    return 0


def _syn(st, D=None):
    R = {"B": 200, "eq1": {}}
    for c in CORPORA:
        d = 0.001 if D is None else D[c]
        R["eq1"][c] = {"D": d, "m": {"q4": 0.8, "q8": 0.8 + d}, "se": 0.002, "se_boot": 0.0015, "seed_term": 0.001, "var_seed": 2e-5,
                       "delta": 0.01, "lo90": d - 0.0033, "hi90": d + 0.0033, "lo95": d - 0.004, "hi95": d + 0.004, "blo": 0, "bhi": 0,
                       "status": st[c], "direction": ("Q8 HIGHER" if d > 0 else "Q8 LOWER") if st[c] == "DIFFERENT" else "",
                       "spread20": {"q4": 0.02, "q8": 0.02}, "n": 100, "components": 99, "kish": 1.01, "n_eff": 99.0,
                       "mde_tost": 0.005, "mde_diff": 0.0117, "scoreable": True}
    R["verdict"] = verdict(st)
    R["eq2"] = {"all": (0.99, 0.95, 10, "x"), "massive": (0.99, 0.95, 3, None), "clinc": (0.99, 0.95, 3, None), "banking77": (0.99, 0.95, 3, None)}
    return R


def _selftest(sel, ok, FX):
    from sklearn.metrics import normalized_mutual_info_score as NMI
    if sel("Q-CONST"):
        ok(check_its_blob() == ITS_BLOB, "Q-CONST intent_transfer_s0.py is blob f662ceb (imported unchanged)")
        ok((D_Q, SEEDS, DELTA_SEEDS, BOOT_B) == (1024, tuple(range(20)), (0, 1, 2, 3, 4), 2000), "Q-CONST d_q* 1024, seeds 0-19, delta seeds 0-4, B 2,000")
        ok((Z90, Z95, Z80P, PRED_D) == (1.645, 1.96, 0.842, 0.003), "Q-CONST z 1.645 / 1.96, power 0.842, predicted |D| 0.003")
        ok(IDENTITY == {"mean": {"massive": "0.76554", "clinc": "0.92810", "banking77": "0.84900"},
                        "spread": {"massive": "0.01428", "clinc": "0.00417", "banking77": "0.01043"}}, "Q-CONST identity 0.76554/0.92810/0.84900, 0.01428/0.00417/0.01043")
        ok(SEL_SHA.startswith("f1b508cf") and SEL_PATH.replace("\\", "/").endswith("experiment_results/embed_dim_slice/selection.json"), "Q-CONST selection.json sha f1b508cf")
        ok(dict(P1) == {"NOT-A-CONFOUND": 0.70, "CONFOUND-CANDIDATE": 0.10, "MIXED": 0.20} and P2 == (0.003, 0.0, 0.010) and P3 == (0.98, 0.85),
           "Q-CONST predictions P1-P3")
        ok(II.GOLD_K == {"massive": (18, 60), "clinc": (10, 150), "banking77": (None, 77)}, "Q-CONST K_f 60/150/77")
        ok(OUT_DIR.replace("\\", "/").endswith("experiment_results/embed_quant") and OUTCOME == "outcome.txt", "Q-CONST outcome path")
        ok(W.MODEL_Q8 == "qwen3-embedding:8b-q8_0" and W.MODEL_Q4 == "qwen3-embedding:latest", "Q-CONST tags")
        pj = json.load(open(PINS_FILE, encoding="utf-8"))
        ok(pj.get("schema") == PINS_SCHEMA and "q8" in pj, "Q-CONST the committed pins file %s carries schema %s and a q8 key"
           % (os.path.basename(PINS_FILE), PINS_SCHEMA))
        if os.path.isfile(SEL_PATH):
            o, err, r = _cap(lambda: read_selection(SEL_PATH, SEL_SHA))
            ok(err is None and "d_q* = 1024" in o, "Q-CONST the committed selection.json reads sha f1b508cf, d_q* 1024")
    if sel("Q-UNIT"):
        ok(status(0.0, 0.01, -0.0099, 0.0099, -0.012, 0.012) == "EQUIVALENT", "Q-UNIT status: 90% inside (-delta, delta) -> EQUIVALENT")
        ok(status(0.0, 0.01, -0.01, 0.005, -0.012, 0.012) == "NEITHER", "Q-UNIT status: lo90 = -delta exactly -> not EQUIVALENT (open interval)")
        ok(status(0.0, 0.01, -0.005, 0.01, -0.012, 0.012) == "NEITHER", "Q-UNIT status: hi90 = +delta exactly -> not EQUIVALENT")
        ok(status(-0.02, 0.01, -0.025, -0.015, -0.026, -0.001) == "DIFFERENT", "Q-UNIT status: D -0.02 < -delta, 95% upper < 0 -> DIFFERENT")
        ok(status(0.02, 0.01, 0.015, 0.025, 0.001, 0.03) == "DIFFERENT", "Q-UNIT status: D +0.02, 95% lower > 0 -> DIFFERENT")
        ok(status(0.01, 0.01, 0.005, 0.015, 0.001, 0.02) == "NEITHER", "Q-UNIT status: |D| = delta exactly -> not DIFFERENT")
        ok(status(0.02, 0.01, 0.0, 0.04, -0.005, 0.045) == "NEITHER", "Q-UNIT status: |D| > delta but the 95% CI holds 0 -> NEITHER")
        ok(status(0.012, 0.01, 0.009, 0.015, 0.008, 0.016) == "DIFFERENT", "Q-UNIT status: a 90% interval over +delta, |D| > delta, 95% > 0 -> DIFFERENT")
        E, Dd, Nn = "EQUIVALENT", "DIFFERENT", "NEITHER"
        cases = [((E, E, E), "NOT-A-CONFOUND"), ((Dd, E, E), "NOT-A-CONFOUND"), ((E, Dd, E), "NOT-A-CONFOUND"), ((E, E, Dd), "NOT-A-CONFOUND"),
                 ((E, Nn, Nn), "MIXED"), ((Nn, Nn, E), "MIXED"), ((Dd, Dd, Dd), "CONFOUND-CANDIDATE"), ((Nn, Dd, Dd), "CONFOUND-CANDIDATE"),
                 ((Dd, Nn, Dd), "CONFOUND-CANDIDATE"), ((E, Dd, Dd), "CONFOUND-CANDIDATE"), ((E, Dd, Nn), "MIXED"), ((Nn, Nn, Nn), "MIXED"),
                 ((Dd, Nn, Nn), "MIXED"), ((Nn, Nn, Dd), "MIXED")]
        for sts, want in cases:
            ok(verdict(dict(zip(CORPORA, sts)))[0] == want, "Q-UNIT verdict %s -> %s" % ("/".join(sts), want))
        # every printed branch, by executing the printers
        R = _syn({"massive": E, "clinc": E, "banking77": Dd}, D={"massive": 0.001, "clinc": 0.0, "banking77": -0.02})
        L = criteria_lines(R)
        ok("EQ1 VERDICT: NOT-A-CONFOUND (EQUIVALENT on 2 of 3, DIFFERENT on 1 of 3)" in L and "F-EQ: NOT FIRED" in L
           and any(x.startswith("CONSEQUENCE: the quantisation half") for x in L), "Q-UNIT lines NOT-A-CONFOUND: verdict, F-EQ NOT FIRED, consequence")
        ok(L[2].endswith("-> DIFFERENT (Q8 LOWER)"), "Q-UNIT lines: DIFFERENT carries its direction (Q8 LOWER)")
        R = _syn({"massive": Nn, "clinc": Dd, "banking77": Dd}, D={"massive": 0.0, "clinc": -0.02, "banking77": 0.03})
        L = criteria_lines(R)
        ok("EQ1 VERDICT: CONFOUND-CANDIDATE (DIFFERENT on 2 of 3: clinc Q8 LOWER, banking77 Q8 HIGHER; EQUIVALENT on 0 of 3)" in L,
           "Q-UNIT lines CONFOUND-CANDIDATE with both directions")
        ok(any(x.startswith("F-EQ: FIRED") and "Q4_K_M; the higher-precision model differs" in x for x in L), "Q-UNIT lines F-EQ FIRED with the relabel sentence")
        R = _syn({"massive": E, "clinc": Nn, "banking77": Dd}, D={"massive": 0.0, "clinc": 0.0, "banking77": -0.02})
        L = criteria_lines(R)
        ok("EQ1 VERDICT: MIXED (UNDETERMINED; EQUIVALENT on 1 of 3, DIFFERENT on 1 of 3)" in L and "F-EQ: NOT FIRED" in L
           and "CONSEQUENCE: MIXED leaves the confound line as written" in L, "Q-UNIT lines MIXED: verdict, F-EQ NOT FIRED, consequence")
        ok(any(x.startswith("NOTE: CLINC NEITHER") for x in L), "Q-UNIT lines: the CLINC NEITHER note")
        P = predictions_lines(R)
        ok("P1 MIXED p 0.20: event TRUE, Brier 0.6400" in P and "P1 NOT-A-CONFOUND p 0.70: event FALSE, Brier 0.4900" in P
           and "P1 CONFOUND-CANDIDATE p 0.10: event FALSE, Brier 0.0100" in P, "Q-UNIT P1 Briers 0.64 / 0.49 / 0.01 on MIXED")
        ok("P2 banking77: |D_q| 0.02000 vs 0.003 [0.000, 0.010] -> FAILED" in P and "P2 massive: |D_q| 0.00000 vs 0.003 [0.000, 0.010] -> HELD" in P
           and "P2: HELD on 2 of 3" in P, "Q-UNIT P2 per corpus on |D_q| (0.02 FAILED, 0 HELD), 2 of 3")
        R2 = _syn({"massive": E, "clinc": E, "banking77": E}, D={"massive": 0.010, "clinc": -0.010, "banking77": 0.0101})
        P = predictions_lines(R2)
        ok("P2: HELD on 2 of 3" in P and "-> HELD" in [x for x in P if x.startswith("P2 clinc")][0][-7:], "Q-UNIT P2 boundary 0.010 inclusive, |-0.010| HELD, 0.0101 FAILED")
        ok("P3 median cos(Q8, Q4) at 1024 >= 0.98 p 0.85: median 0.990000, event TRUE, Brier 0.0225" in P, "Q-UNIT P3 event TRUE, Brier 0.0225")
        R2["eq2"]["all"] = (0.98, 0.5, 10, "x")
        ok("event TRUE" in predictions_lines(R2)[-1], "Q-UNIT P3 boundary: median exactly 0.98 -> TRUE")
        R2["eq2"]["all"] = (0.9799, 0.5, 10, "x")
        ok("event FALSE, Brier 0.7225" in predictions_lines(R2)[-1], "Q-UNIT P3 median 0.9799 -> FALSE, Brier 0.7225")
        S = support_lines(_syn({"massive": E, "clinc": E, "banking77": E}))
        ok("-> SCOREABLE" in S[0], "Q-UNIT support prints SCOREABLE")
        R3 = _syn({"massive": E, "clinc": E, "banking77": E})
        R3["eq1"]["clinc"]["scoreable"] = False
        ok(support_lines(R3)[1].endswith("-> DESCRIPTIVE-ONLY"), "Q-UNIT support prints DESCRIPTIVE-ONLY")
    if sel("Q-E2E"):
        for name in FX_SPEC:
            fx = FX[name]
            orc = fx["oracle"]
            o, err, R, od = _run(fx, "e2e")
            ok(err is None, "Q-E2E %s: --run completes (%s)" % (name, err))
            want_v, want_st = FX_EXPECT[name]
            ok(_line(o, "EQ1 VERDICT: ").startswith("EQ1 VERDICT: %s " % want_v), "Q-E2E %s: printed verdict %s (planted)" % (name, want_v))
            for c in CORPORA:
                r = orc[c]
                ln = _line(o, "EQ1 %s:" % c)
                ok(orc[c]["status"] == want_st[c], "Q-E2E %s %s: the oracle's status is the planted %s" % (name, c, want_st[c]))
                ok(("D_q = Q8 %.5f - Q4 %.5f = %+.5f" % (r["q8"], r["q4"], r["D"])) in ln, "Q-E2E %s %s: D_q %+.5f = the oracle's" % (name, c, r["D"]))
                ok(("delta_c %.5f" % r["delta"]) in ln and ("SE_total %.5f" % r["se"]) in ln,
                   "Q-E2E %s %s: delta_c %.5f and SE_total %.5f = the oracle's (own bootstrap, own weighted NMI)" % (name, c, r["delta"], r["se"]))
                ok(("90%% [%+.5f, %+.5f]" % (r["D"] - 1.645 * r["se"], r["D"] + 1.645 * r["se"])) in ln, "Q-E2E %s %s: 90%% interval" % (name, c))
                ok(ln.split(" -> ")[-1].startswith(want_st[c]), "Q-E2E %s %s: printed status %s" % (name, c, want_st[c]))
                ok(("denominator %d EVAL items" % r["n"]) in ln, "Q-E2E %s %s: denominator %d" % (name, c, r["n"]))
                sp = _line(o, "SUPPORT %s:" % c)
                word = "SCOREABLE" if (r["delta"] - 0.003) >= 2.487 * r["se"] else "DESCRIPTIVE-ONLY"
                ok(("TOST MDE80 2.487 x SE_total %.5f" % (2.487 * r["se"])) in sp and ("DIFFERENT MDE delta + 0.842 x SE_total %.5f" % (r["delta"] + 0.842 * r["se"])) in sp
                   and sp.endswith("-> " + word), "Q-E2E %s %s: support MDEs from the oracle's SE_total and the (f) word %s" % (name, c, word))
                ok(("n %d EVAL items in %d components, Kish DEFF %.4f, n_eff %.0f" % (r["n"], r["comps"], r["kish"], r["n"] / r["kish"])) in sp,
                   "Q-E2E %s %s: support n %d, components %d, Kish %.4f from the EVAL rows' components" % (name, c, r["n"], r["comps"], r["kish"]))
            ok(("all %d texts median %.6f min %.6f" % (len(fx["texts"]), orc["all"][0], orc["all"][1])) in _line(o, "EQ2 (DESCRIPTIVE-ONLY)"),
               "Q-E2E %s: EQ2 overall median / min = the oracle's" % name)
            for c in CORPORA:
                ok(("median %.6f min %.6f" % (orc[c]["cos_med"], orc[c]["cos_min"])) in _line(o, "EQ2 %s:" % c), "Q-E2E %s: EQ2 %s = the oracle's" % (name, c))
            fe = _line(o, "F-EQ:")
            ok(fe.startswith("F-EQ: FIRED --") if want_v == "CONFOUND-CANDIDATE" else fe == "F-EQ: NOT FIRED",
               "Q-E2E %s: F-EQ %s" % (name, "FIRED" if want_v == "CONFOUND-CANDIDATE" else "NOT FIRED"))
            txt = open(os.path.join(od, OUTCOME), encoding="utf-8").read()
            ok(_line(o, "EQ1 VERDICT: ") in txt and "IDENTITY: " in txt and "-> REPRODUCED" in txt and DOES_NOT_SHOW in txt and READINGS in txt,
               "Q-E2E %s: outcome.txt carries the verdict, the identity, the readings and DOES NOT SHOW" % name)
            ok("EVAL read 6 times (once per arm per corpus)" in txt and "0 with an EVAL row" in txt, "Q-E2E %s: EVAL read 6 times; 0 fits with an EVAL row" % name)
            rows = list(csv.reader(open(os.path.join(od, CSVS[0]), encoding="utf-8")))
            ok(len(rows) == 1 + 2 * 3 * 20, "Q-E2E %s: nmi_q.csv 120 rows" % name)
            x = [float(r[7]) for r in rows[1:] if r[0] == "q8" and r[3] == "banking77"]
            ok(len(x) == 20 and abs(np.mean(x) - orc["banking77"]["q8"]) < 1e-6, "Q-E2E %s: nmi_q.csv banking77 Q8 seeds = the oracle's mean" % name)
            cr = list(csv.reader(open(os.path.join(od, CSVS[1]), encoding="utf-8")))
            ok(len(cr) == 1 + len(fx["texts"]) and min(float(r[1]) for r in cr[1:]) <= orc["all"][1] + 1e-6, "Q-E2E %s: cos_q.csv one row per text" % name)
            o2, err2, _r, _od = _run(fx, "again", out_dir=od)
            ok(err2 and "write-once" in err2, "Q-E2E %s: a second --run into the same directory REFUSES (write-once)" % name)
        r = FX["C"]["oracle"]["banking77"]
        ok(1.645 * r["se"] <= r["delta"] - 0.003 < 2.487 * r["se"], "Q-E2E C banking77 discriminates the (f) rule: 1.645 SE <= delta - 0.003 < 2.487 SE")
        o, err, R, od = _run(FX["M"], "seedterm")
        r = R["eq1"]["massive"]
        ok(abs(r["var_seed"] - FX["M"]["oracle"]["massive"]["var_seed"]) < 1e-12 and r["var_seed"] > 0 and r["seed_term"] > 0,
           "Q-E2E M massive: var_seed over the 20 per-seed differences = the oracle's (> 0)")
        ok(R["eq1"]["clinc"]["direction"] == "Q8 LOWER" and FX["C"]["oracle"]["banking77"]["D"] > 0, "Q-E2E direction: garbled CLINC Q8 LOWER; sharp banking77 positive")
    if sel("Q-REFUSE"):
        fx = FX["N"]

        def nowrite(od):
            return not any(os.path.exists(p) for p in out_paths(od))
        bad = dict(fx["identity"], mean=dict(fx["identity"]["mean"], banking77="0.00000"))
        o, err, _r, od = _run(fx, "idbad", identity=bad)
        ok(err and "IDENTITY PRECONDITION FAILED on ['banking77']" in err and nowrite(od), "Q-REFUSE identity off on the LAST corpus (mean): refused, nothing written")
        bad = dict(fx["identity"], spread=dict(fx["identity"]["spread"], clinc="0.99999"))
        o, err, _r, od = _run(fx, "idspread", identity=bad)
        ok(err and "['clinc']" in err and nowrite(od), "Q-REFUSE identity off on a spread only: refused")
        o, err, _r, od = _run(fx, "selsha", sel_sha="0" * 64)
        ok(err and "selection.json sha256" in err and nowrite(od), "Q-REFUSE selection.json sha mismatch: refused")
        sel2 = os.path.join(fx["td"], "sel512.json")
        with open(sel2, "wb") as fh:
            fh.write(json.dumps({"d_q*": 512}).encode("utf-8"))
        o, err, _r, od = _run(fx, "sel512", sel_path=sel2, sel_sha=II.file_sha(sel2))
        ok(err and "d_q* 512" in err, "Q-REFUSE selection with d_q* 512: refused")
        prog = os.path.join(fx["td"], "noprog.md")
        open(prog, "w", encoding="utf-8").write("## Registered 2026-10-01 (before any code or call) \u2014 EMBED-DIM-SLICE: x\n")
        o, err, _r, od = _run(fx, "noreg", programme=prog)
        ok(err and "not registered" in err and nowrite(od), "Q-REFUSE registration heading absent: refused")
        qp = os.path.join(fx["td"], "q8null.json")
        json.dump({"schema": PINS_SCHEMA, "q8": None}, open(qp, "w"))
        saved = fx["qpins"]
        fx["qpins"] = qp
        try:
            o, err, _r, od = _run(fx, "q8null")
        finally:
            fx["qpins"] = saved
        ok(err and "UNPINNED" in err and nowrite(od), "Q-REFUSE Q8 pin null: --run refused")
        json.dump({"schema": PINS_SCHEMA, "q8": "1" * 64}, open(qp, "w"))
        fx["qpins"] = qp
        try:
            o, err, _r, od = _run(fx, "q8bad")
        finally:
            fx["qpins"] = saved
        ok(err and "intent_emb_qwen3_q8.db" in err and "pinned" in err, "Q-REFUSE Q8 pin different: refused")
        g = globals()
        real = g["_foreign_heavy"]
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ['"java.exe","1"']
            od = os.path.join(fx["td"], "heavy")
            o, err, _r = _cap(lambda: main_run(db=fx["db"], emb_dir=fx["td"], out_dir=od, programme=fx["prog"], identity=fx["identity"],
                                               sel_path=fx["sel"], sel_sha=fx["sel_sha"], B=200))
        g["_foreign_heavy"] = real
        ok(err and "heavy" in err, "Q-REFUSE a java.exe running: refused")
        real_eq2 = g["eq2"]

        def tamper(*a):
            with open(W.q8_path(fx["td"]), "ab") as fh:
                fh.write(b"\0")
            return real_eq2(*a)
        g["eq2"] = tamper
        saved_bytes = open(W.q8_path(fx["td"]), "rb").read()
        try:
            o, err, _r, od = _run(fx, "tamper")
        finally:
            g["eq2"] = real_eq2
            open(W.q8_path(fx["td"]), "wb").write(saved_bytes)
        ok(err and "q8 sha256 changed during the readout" in err and nowrite(od), "Q-REFUSE the Q8 file changes mid-readout: refused, nothing written")
        # the outcome appears between the path check and the write (a concurrent writer): the exclusive open never overwrites it
        od_r = os.path.join(fx["td"], "race_out")

        def racer(*a):
            os.makedirs(od_r, exist_ok=True)
            with open(os.path.join(od_r, OUTCOME), "w", encoding="utf-8") as fh:
                fh.write("PRIOR")
            return real_eq2(*a)
        g["eq2"] = racer
        raced = None
        try:
            _run(fx, "race", out_dir=od_r)
        except FileExistsError as ex:
            raced = ex
        finally:
            g["eq2"] = real_eq2
        ok(raced is not None and open(os.path.join(od_r, OUTCOME), encoding="utf-8").read() == "PRIOR",
           "Q-REFUSE an outcome.txt that appears mid-run is never overwritten (mode x)")
        # a partial Q8 file (one text missing): --run refuses (the file's bytes restored afterwards: fixtures are shared by mutants)
        p8 = W.q8_path(fx["td"])
        orig = open(p8, "rb").read()
        con = sqlite3.connect(p8)
        t0 = con.execute("SELECT query FROM embeddings LIMIT 1").fetchone()[0]
        blob = con.execute("SELECT vector FROM embeddings WHERE query = ?", (t0,)).fetchone()[0]
        con.execute("DELETE FROM embeddings WHERE query = ?", (t0,))
        con.commit()
        con.close()
        json.dump({"schema": PINS_SCHEMA, "q8": II.file_sha(p8)}, open(qp, "w"))
        fx["qpins"] = qp
        try:
            o, err, _r, od = _run(fx, "partial")
            with _scope(fx):
                od2 = os.path.join(fx["td"], "dry_partial")
                o3, err3, _r3 = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=fx["identity"],
                                                     sel_path=fx["sel"], sel_sha=fx["sel_sha"], timing=False))
        finally:
            fx["qpins"] = saved
            open(p8, "wb").write(orig)
        ok(err and "1 texts of the registered set have no vector" in err and nowrite(od), "Q-REFUSE a partial Q8 file: --run refused")
        ok(err3 is None and ("%d of %d texts present (1 missing): --run REFUSES" % (len(fx["texts"]) - 1, len(fx["texts"]))) in o3,
           "Q-REFUSE the dry-run reports the partial Q8 file (1 missing)")
        ok(II.file_sha(p8) == json.load(open(fx["qpins"]))["q8"], "Q-REFUSE fixture Q8 file restored")
        con = sqlite3.connect(p8)
        con.execute("UPDATE intent_meta SET value = 'qwen3-embedding:latest' WHERE key = 'model'")
        con.commit()
        con.close()
        json.dump({"schema": PINS_SCHEMA, "q8": II.file_sha(p8)}, open(qp, "w"))
        fx["qpins"] = qp
        try:
            o, err, _r, od = _run(fx, "meta")
        finally:
            fx["qpins"] = saved
            open(p8, "wb").write(orig)
        ok(err and "intent_meta mismatch" in err and "model" in err, "Q-REFUSE a Q8 file whose meta names the Q4 tag: refused")
        ok(II.file_sha(p8) == json.load(open(fx["qpins"]))["q8"], "Q-REFUSE fixture Q8 file restored after the meta test")
    if sel("Q-DRY"):
        fx = FX["C"]
        before = sorted(os.listdir(fx["td"]))
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=fx["identity"], sel_path=fx["sel"],
                                              sel_sha=fx["sel_sha"], timing=True))
        ok(err is None and ("IDENTITY: Q4 @1024 seeds 0-4 seed-mean EVAL fine NMI %s" % " / ".join(fx["identity"]["mean"][c] for c in CORPORA)) in o
           and "DRY RUN complete" in o, "Q-DRY completes; the identity values printed = the oracle's")
        ok(("%d of %d texts present (0 missing)" % (len(fx["texts"]), len(fx["texts"]))) in o and "TIMING" in o, "Q-DRY Q8 complete (0 missing) and a timed fit")
        ok(sorted(os.listdir(fx["td"])) == before, "Q-DRY writes nothing (directory unchanged)")
        ok(sum(1 for e in EVENTS if e[0] == "EVAL") == 3 and all(e[1].startswith("q4 ") for e in EVENTS), "Q-DRY reads EVAL of the Q4 arm only (3 reads)")
        bad = dict(fx["identity"], mean=dict(fx["identity"]["mean"], massive="0.00001"))
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=bad, sel_path=fx["sel"],
                                              sel_sha=fx["sel_sha"], timing=False))
        ok(err and "IDENTITY PRECONDITION FAILED on ['massive']" in err, "Q-DRY identity mismatch refuses in the dry-run too")
        tdn = os.path.join(fx["td"], "noq8")
        os.makedirs(tdn, exist_ok=True)
        for f in (II.DB_NAME, "intent_emb_qwen3.db"):
            if not os.path.exists(os.path.join(tdn, f)):
                shutil.copyfile(os.path.join(fx["td"], f), os.path.join(tdn, f))
        with _scope(fx):
            ITS.DATA_ROOT = tdn
            o, err, _r = _cap(lambda: dry_run(db=os.path.join(tdn, II.DB_NAME), emb_dir=tdn, programme=fx["prog"], identity=fx["identity"],
                                              sel_path=fx["sel"], sel_sha=fx["sel_sha"], timing=False))
        ok(err is None and "absent: run tools/analysis/embed_quant_writer.py --embed --go first" in o, "Q-DRY with no Q8 file: prints absent, completes")
    if sel("Q-LOAD"):
        fx = FX["N"]
        with _scope(fx):
            CS = ITS.load_corpora(fx["db"])
            texts = ITS.text_set(CS)[0]
            with contextlib.redirect_stdout(io.StringIO()):
                v = load_slice(W.q8_path(fx["td"]), "q8", texts)
        con = sqlite3.connect(W.q8_path(fx["td"]))
        t, b = con.execute("SELECT query, vector FROM embeddings LIMIT 1").fetchone()
        con.close()
        ok(len(v[t]) == 1024 and np.array_equal(v[t], np.frombuffer(b, dtype=">f4")[:1024].astype(np.float32)), "Q-LOAD the Q8 read is the first 1024 raw coordinates")
        ok(ITS.SLICE2 == 512 and W.MODEL_Q8 not in ITS.EA.EG.NATIVE_DIM, "Q-LOAD S0's SLICE2 restored to 512; the tag registration removed")


MUTANTS = (
    ("D sign flipped (Q4 - Q8)", "    D = m[\"q8\"] - m[\"q4\"]\n", "    D = m[\"q4\"] - m[\"q8\"]\n", ("Q-E2E",)),
    ("delta from 20 seeds", "    q4d = nm[\"q4\"][:len(DELTA_SEEDS)]\n", "    q4d = nm[\"q4\"]\n", ("Q-E2E",)),
    ("delta from the Q8 arm", "    q4d = nm[\"q4\"][:len(DELTA_SEEDS)]\n", "    q4d = nm[\"q8\"][:len(DELTA_SEEDS)]\n", ("Q-E2E",)),
    ("delta = max of both arms' spreads", "    delta = float(max(q4d) - min(q4d))\n",
     "    delta = float(max(max(q4d) - min(q4d), max(nm[\"q8\"][:5]) - min(nm[\"q8\"][:5])))\n", ("Q-E2E",)),
    ("seed term dropped", "    se = float(np.sqrt(se_boot ** 2 + var_seed / len(SEEDS)))\n", "    se = se_boot\n", ("Q-E2E",)),
    ("seed term not divided by 20", "    se = float(np.sqrt(se_boot ** 2 + var_seed / len(SEEDS)))\n", "    se = float(np.sqrt(se_boot ** 2 + var_seed))\n", ("Q-E2E",)),
    ("var_seed population (ddof 0)", "    var_seed = float(np.var(dseed, ddof=1))\n", "    var_seed = float(np.var(dseed))\n", ("Q-E2E",)),
    ("var_seed of the Q4 arm, not of the difference", "    dseed = np.array(nm[\"q8\"]) - np.array(nm[\"q4\"])\n", "    dseed = np.array(nm[\"q4\"])\n", ("Q-E2E",)),
    ("bootstrap unweighted", "        mw = {a: float(np.mean([ITS.nmi(truth, p, w) for p in preds[a]])) for a in ARMS}\n",
     "        mw = {a: float(np.mean([ITS.nmi(truth, p) for p in preds[a]])) for a in ARMS}\n", ("Q-E2E",)),
    ("bootstrap over items, not components", "        R[\"eq1\"][c] = eq1(c, x[\"_truth\"], CS[c].comp[x[\"_ev\"]],",
     "        R[\"eq1\"][c] = eq1(c, x[\"_truth\"], np.arange(len(x[\"_ev\"])),", ("Q-E2E",)),
    ("bootstrap stream of the coarse level", "    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index(\"fine\"))\n",
     "    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c))\n", ("Q-E2E",)),
    ("Z90 = 1.96", "Z90, Z95, Z80P = 1.645, 1.96, 0.842\n", "Z90, Z95, Z80P = 1.96, 1.96, 0.842\n", ("Q-CONST", "Q-E2E")),
    ("EQUIVALENT on a closed interval", "    if lo90 > -delta and hi90 < delta:\n", "    if lo90 >= -delta and hi90 <= delta:\n", ("Q-UNIT",)),
    ("EQUIVALENT on the 95% interval", "    if lo90 > -delta and hi90 < delta:\n", "    if lo95 > -delta and hi95 < delta:\n", ("Q-UNIT",)),
    ("DIFFERENT without the point condition", "    if abs(D) > delta and (lo95 > 0 or hi95 < 0):\n", "    if (lo95 > 0 or hi95 < 0):\n", ("Q-UNIT",)),
    ("DIFFERENT without the interval condition", "    if abs(D) > delta and (lo95 > 0 or hi95 < 0):\n", "    if abs(D) > delta:\n", ("Q-UNIT",)),
    ("DIFFERENT only when Q8 is LOWER", "    if abs(D) > delta and (lo95 > 0 or hi95 < 0):\n", "    if -D > delta and hi95 < 0:\n", ("Q-UNIT", "Q-E2E")),
    ("DIFFERENT on |D| >= delta", "    if abs(D) > delta and", "    if abs(D) >= delta and", ("Q-UNIT",)),
    ("NOT-A-CONFOUND on >= 1", "    if ne >= 2:\n        return \"NOT-A-CONFOUND\"", "    if ne >= 1:\n        return \"NOT-A-CONFOUND\"", ("Q-UNIT", "Q-E2E")),
    ("NOT-A-CONFOUND on 3 of 3", "    if ne >= 2:\n        return \"NOT-A-CONFOUND\"", "    if ne >= 3:\n        return \"NOT-A-CONFOUND\"", ("Q-UNIT", "Q-E2E")),
    ("CONFOUND-CANDIDATE on >= 1", "    if nd >= 2:\n        return \"CONFOUND-CANDIDATE\"", "    if nd >= 1:\n        return \"CONFOUND-CANDIDATE\"", ("Q-UNIT", "Q-E2E")),
    ("CONFOUND checked first", [("    if ne >= 2:\n        return \"NOT-A-CONFOUND\", ne, nd\n    if nd >= 2:\n        return \"CONFOUND-CANDIDATE\", ne, nd\n",
                                 "    if nd >= 1:\n        return \"CONFOUND-CANDIDATE\", ne, nd\n    if ne >= 2:\n        return \"NOT-A-CONFOUND\", ne, nd\n")], None, ("Q-UNIT", "Q-E2E")),
    ("verdict counts the first two corpora", "    nd = sum(1 for c in CORPORA if st[c] == \"DIFFERENT\")\n", "    nd = sum(1 for c in CORPORA[:2] if st[c] == \"DIFFERENT\")\n", ("Q-UNIT", "Q-E2E")),
    ("F-EQ fires on MIXED", "    if v == \"CONFOUND-CANDIDATE\":\n        L.append(\"F-EQ: FIRED", "    if v != \"NOT-A-CONFOUND\":\n        L.append(\"F-EQ: FIRED", ("Q-UNIT", "Q-E2E")),
    ("MIXED consequence never printed", "        L.append(\"CONSEQUENCE: MIXED leaves", "        (\"CONSEQUENCE: MIXED leaves", ("Q-UNIT",)),
    ("CLINC note never printed", "        L.append(\"NOTE: CLINC NEITHER", "        (\"NOTE: CLINC NEITHER", ("Q-UNIT",)),
    ("direction inverted", "            \"direction\": (\"Q8 HIGHER\" if D > 0 else \"Q8 LOWER\")", "            \"direction\": (\"Q8 HIGHER\" if D < 0 else \"Q8 LOWER\")", ("Q-UNIT", "Q-E2E")),
    ("identity checks the first corpus only", "    bad = [c for c in CORPORA if got[c]", "    bad = [c for c in CORPORA[:1] if got[c]", ("Q-REFUSE",)),
    ("identity ignores the spread", "    bad = [c for c in CORPORA if got[c] != (target[\"mean\"][c], target[\"spread\"][c])]\n",
     "    bad = [c for c in CORPORA if got[c][0] != target[\"mean\"][c]]\n", ("Q-REFUSE",)),
    ("identity from seeds 1-5", "    x = nm_q4[:len(DELTA_SEEDS)]\n", "    x = nm_q4[1:len(DELTA_SEEDS) + 1]\n", ("Q-E2E",)),
    ("identity skipped", "    if bad:\n        refuse(\"IDENTITY", "    if False:\n        refuse(\"IDENTITY", ("Q-REFUSE",)),
    ("selection sha not checked", "    if sha != want_sha:\n", "    if False:\n", ("Q-REFUSE",)),
    ("selection d_q* not checked", "    if dq != D_Q:\n", "    if False:\n", ("Q-REFUSE",)),
    ("registration not required", "    if not check_registered(programme):\n", "    if False:\n", ("Q-REFUSE",)),
    ("Q8 pin not strict at --run", "    sha0, CS, texts, set_sha = load_inputs(db, emb_dir, True)\n", "    sha0, CS, texts, set_sha = load_inputs(db, emb_dir, False)\n", ("Q-REFUSE",)),
    ("Q8 pin mismatch admitted", "    if want and want != s:\n        refuse(\"%s sha256 %s != the pinned", "    if False:\n        refuse(\"%s sha256 %s != the pinned", ("Q-REFUSE",)),
    ("Q8 meta not checked", "        ITS.check_meta(emb_file(\"q8\", emb_dir), W.expected_meta_q8(", "        (emb_file(\"q8\", emb_dir), W.expected_meta_q8(", ("Q-REFUSE",)),
    ("partial Q8 admitted at --run", "    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts) for a in ARMS}\n",
     "    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts, allow_missing=True) for a in ARMS}\n", ("Q-REFUSE",)),
    ("after-check skipped", "        if now != s:\n            refuse(\"%s sha256 changed", "        if False:\n            refuse(\"%s sha256 changed", ("Q-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("Q-REFUSE",)),
    ("outcome not write-once", "    with open(os.path.join(out_dir, OUTCOME), \"x\"", "    with open(os.path.join(out_dir, OUTCOME), \"w\"", ("Q-REFUSE",)),
    ("outcome paths not checked", "        if os.path.lexists(p):\n            refuse(\"%s exists", "        if False:\n            refuse(\"%s exists", ("Q-E2E",)),
    ("slice 512 for Q8", "    ITS.SLICE2 = D_Q\n", "    ITS.SLICE2 = 512 if arm == \"q8\" else D_Q\n", ("Q-LOAD", "Q-E2E")),
    ("SLICE2 not restored", "        ITS.SLICE2 = saved\n", "        pass\n", ("Q-LOAD",)),
    ("Q8 read from the Q4 file", "    return ITS.emb_path(\"qwen3\", emb_dir) if arm == \"q4\" else W.q8_path(emb_dir)\n",
     "    return ITS.emb_path(\"qwen3\", emb_dir)\n", ("Q-E2E",)),
    ("EQ2 cos unnormalised", "        cos[i0:i0 + len(ch)] = (A * Bm).sum(1) / (np.linalg.norm(A, axis=1) * np.linalg.norm(Bm, axis=1))\n",
     "        cos[i0:i0 + len(ch)] = (A * Bm).sum(1)\n", ("Q-E2E",)),
    ("EQ2 min = max", "    summ = {\"all\": (float(np.median(cos)), float(cos.min()),", "    summ = {\"all\": (float(np.median(cos)), float(cos.max()),", ("Q-E2E",)),
    ("EQ2 per corpus over the first corpus", "        C = CS[c]\n        idx = sorted(", "        C = CS[CORPORA[0]]\n        idx = sorted(", ("Q-E2E",)),
    ("P1 Brier on the complement", "        L.append(\"P1 %s p %.2f: event %s, Brier %.4f\" % (name, p, \"TRUE\" if ev else \"FALSE\", (p - (1.0 if ev else 0.0)) ** 2))\n",
     "        L.append(\"P1 %s p %.2f: event %s, Brier %.4f\" % (name, p, \"TRUE\" if ev else \"FALSE\", (p - (0.0 if ev else 1.0)) ** 2))\n", ("Q-UNIT",)),
    ("P2 on signed D", "        a = abs(R[\"eq1\"][c][\"D\"])\n", "        a = R[\"eq1\"][c][\"D\"]\n", ("Q-UNIT",)),
    ("P2 interval open", "    return \"HELD\" if (np.isfinite(v) and lo <= v <= hi) else \"FAILED\"\n", "    return \"HELD\" if (np.isfinite(v) and lo < v < hi) else \"FAILED\"\n", ("Q-UNIT",)),
    ("P3 strict >", "    ev = med >= P3[0]\n", "    ev = med > P3[0]\n", ("Q-UNIT",)),
    ("SCOREABLE at 1.645 x SE", "            \"scoreable\": (delta - PRED_D) >= (Z90 + Z80P) * se,", "            \"scoreable\": (delta - PRED_D) >= Z90 * se,", ("Q-E2E",)),
    ("seeds 0-4 only for D", "SEEDS = tuple(range(20))\n", "SEEDS = tuple(range(5))\n", ("Q-CONST", "Q-E2E")),
    ("EVAL replaced by GATE (wrong split side)", "    ev = ITS.S_idx(C, S, SS.EVAL)\n    EVENTS.append", "    ev = ITS.S_idx(C, S, SS.GATE)\n    EVENTS.append", ("Q-E2E",)),
    ("identity read from the Q8 arm", "        idv[c] = identity_values(out[\"q4\"][3])\n", "        idv[c] = identity_values(out[\"q8\"][3])\n", ("Q-E2E",)),
    ("Kish over the whole corpus", "    kish = ITS.kish(comp)\n", "    kish = ITS.kish(np.arange(len(comp)) // 2)\n", ("Q-E2E",)),
    ("dry-run reads Q8 EVAL", "        _ev, _t, _p, nm = arm_eval(CS[c], v4, \"q4\", DELTA_SEEDS)\n",
     "        _ev, _t, _p, nm = arm_eval(CS[c], v4, \"q8\", DELTA_SEEDS)\n", ("Q-DRY",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="eq_mut_")
    fx = make_fixtures(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        pairs = old if isinstance(old, list) else [(old, new)]
        code = head
        for o_, n_ in pairs:
            if code.count(o_) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, code.count(o_)))
            code = code.replace(o_, n_)
        ns = {"__name__": "eq_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=fx, writer=False)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        finally:
            ITS.SLICE2 = 512
            W.EA.EG.NATIVE_DIM.pop(W.MODEL_Q8, None)
            ITS.MODEL.pop(W.E_Q8, None)
        killed += res.startswith("KILLED")
        print("  %-48s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS (readout): %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="EMBED-QUANT readout (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-timing", action="store_true", help="--dry-run without the timed fit")
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
