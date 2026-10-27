"""INTENT-S0-CARD-PROTOCOL readout: at each embedder's EMBED-DIM-SLICE-selected slice, does gemma's fine-level edge over qwen3 survive
card-conformant prompts on both sides (CP1), and do card prompts raise qwen3's fine NMI over RAW (CP2)?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — INTENT-S0-CARD-PROTOCOL: at
each embedder's EMBED-DIM-SLICE-selected slice, does gemma's fine-level edge over qwen3 survive card-conformant prompts on both sides
(CP1), and do card prompts raise qwen3's fine NMI over RAW (CP2)? (zero calls; Ollama re-embedding; no build)", span L22655-L22680
_as_of 46954215 (drafted in docs/agents/plans/2026-10-02_next_registrations.md section 3, ce0d0f17). --run REFUSES unless a LINE of
the programme starts with that heading (REG_RE, line-anchored: a quotation inside another section does not satisfy it; READY
EMBED-DIM-SLICE D-note). Slices from EMBED-DIM-SLICE's GATE selection (experiment_results/embed_dim_slice/selection.json, sha256 of the
LF rendering f1b508cf...; REFUSES another file or another d*): d_q* = 1024, d_g* = 768. Kind: zero-call CPU reader: zero judge calls,
zero embeddings (the CARD files are written by tools/analysis/card_protocol_writer.py), no build, no pool of record, no GATE row.

THE REGISTERED CRITERIA (quoted from READOUTS AND CRITERIA; "BASIC component-bootstrap CI, B 2,000, partitions fixed; S0's C1 rule"):
  "CP1 (deciding; POINT AND INTERVAL, one conjunctive clause each way; stated here once). Per corpus D_card = mean_s NMI_EVAL(gemma,
  CARD, d_g*) - mean_s NMI_EVAL(qwen3, CARD, d_q*) at K_f. BETTER iff D_card > bar AND CI > 0; WORSE symmetrically; NEITHER otherwise.
  bar = max(MDE80, max(spread_qwen3,CARD, spread_gemma,CARD)), both spreads IN-RUN (max - min over seeds 0-4 of that arm's EVAL NMI).
  VERDICT: REOPEN-CANDIDATE iff gemma BETTER on >= 2 of 3; KEEP iff on <= 1; KEEP-STRONG iff gemma WORSE on >= 2 of 3. Total
  classification."
  "CP2 (deciding; pooled; POINT AND INTERVAL). D-bar = (1/3) Sum_c [mean_s NMI_EVAL(qwen3, CARD, d_q*) - mean_s NMI_EVAL(qwen3, RAW,
  d_q*)]. bar_pool = max(MDE80(D-bar), the mean over corpora of max(spread_qwen3,CARD, spread_qwen3,RAW)), in-run. HELD (card raises
  qwen3) iff D-bar > bar_pool AND lower(CI) > 0; HURTS iff D-bar < -bar_pool AND upper(CI) < 0; NOT SHOWN otherwise. CI from a joint
  bootstrap over the three corpora, resampled independently per corpus."
  "CP3 (DESCRIPTIVE): S under CARD for qwen3 and gemma at d* (MASSIVE, K 60, seeds 0-4), ceiling-normalised with the
  supervised-centroid S and the random co-filing floor recomputed per arm."
  "CP4 (DESCRIPTIVE): the nomic CARD rows; gemma CARD - gemma RAW."
  "Fail observables at the planned n: CP1 REOPEN-CANDIDATE (F-CP1); CP2 NOT SHOWN or HURTS (F-CP2)."
  FALSIFIERS: "F-CP1 fires iff CP1 reads REOPEN-CANDIDATE ... F-CP2 fires iff CP2 is NOT SHOWN or HURTS ...".
  MDE80 = 2.8 x SE (Support (e)); SE = the SD (ddof 1) of the bootstrap draws of the statistic.

INSTRUMENT (imported, never copied): tools/analysis/intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271 (asserted at
every entry point): pin_check / raw_pin_check (--run strict), load_corpora, text_set, check_meta / expected_meta, load_vectors (with
ITS.SLICE2 = the arm's slice for the call, restored in a finally: the first d raw coordinates), Space (first d coordinates,
L2-renormalised), km_fit (spherical k-means, k-means++, n_init 1, max_iter 300, TRAIN fit through fit_rows, the TRAIN-ONLY guard),
assign, nmi (arithmetic), comp_weights (CK-CLOSE component bootstrap), basic_ci, pct_ci, c1_status (S0's C1 rule verbatim), kish, c4
(SLOTSWAP's S, its supervised-centroid ceiling and random co-filing floor). The CARD files' meta is checked against
card_protocol_writer.expected_meta_card (prompt, prompt sha256, prompts-file sha256, writer blob).

ARMS (seeds 0-4, K_f 60 / 150 / 77; EVAL = kept in-scope EVAL rows, CLINC OOS excluded): qwen3 RAW @1024 (S0's intent_emb_qwen3.db,
the Q4_K_M tag), gemma RAW @768 (S0's intent_emb_gemma.db), qwen3 CARD @1024 (intent_emb_qwen3_card.db), gemma CARD @768
(intent_emb_gemma_card.db); DESCRIPTIVE (CP4) nomic RAW and CARD @256 (S0's intent_emb_nomic.db, intent_emb_nomic_card.db), read only
when the registrar has pinned intent_emb_nomic_card.db (else the CP4 nomic line prints NOT READ). The CARD files are pinned in
experiment_configs/card_protocol_pins.json (--run REFUSES a null or different pin for qwen3_card / gemma_card).

IDENTITY (precondition; REFUSES, nothing written): the RAW arms at the chosen slices reproduce EMBED-DIM-SLICE's values of record:
seed-mean EVAL fine NMI and seed spread (seeds 0-4, "%.5f") of qwen3@1024 0.76554 / 0.92810 / 0.84900 (spread 0.01428 / 0.00417 /
0.01043) and gemma@768 0.79883 / 0.92566 / 0.89286 (spread 0.01277 / 0.00968 / 0.01216) (nmi_matrix.csv), and DS1's D* +0.03329 /
-0.00244 / +0.04386 with its 95% BASIC CI [+0.02961, +0.03998] / [-0.00560, -0.00048] / [+0.04108, +0.04990] ("%+.5f"; outcome.txt),
the last on this script's own bootstrap stream (DS1's, EB3), so the stream that decides CP1 is shown to be DS1's.

SUPPORT printed per corpus from the run: n, components, Kish DEFF of the EVAL components (planned 1.0093 / 1.0000 / 1.0015), n_eff,
SE(D_card) (planned 0.00289 / 0.00137 / 0.00247), MDE80, bar (planning 0.0246 / 0.0094 / 0.0143) and the registered (f) word at the
prediction (SCOREABLE iff |P| - bar > MDE80); CP2's SE(D-bar) (planned 0.00135), MDE80, spread term, bar_pool (planning 0.0161) and
its word at +0.020; the STRUCTURAL LEG line.

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets):
  CB1 INSTRUMENT: two new scripts (card_protocol_writer.py, card_protocol.py) importing S0 and embedder_arms unchanged (both blobs are
      pinned by S0's DBs), not "a card writer on embedder_arms.py" as a code change (the EMBED-QUANT QB1 pattern).
  CB2 PREFLIGHT "checks route parity (S0's bars: qwen3 0.9980, gemma 0.9999)": applied to the RAW route (same model, same protocol)
      and to the CARD route's repeatability (T3) and resume parity (T4); cos(CARD, RAW) printed with no bar; CW1 no transform; CW3 the
      tag's digest must equal S0's RAW file's stored digest.
  CB3 bootstrap stream = DS1's / S0's C1 fine stream (BOOT_SEED + 10 x corpus index + fine level index); ONE weight vector per draw
      for every arm of the corpus (paired); CP2's joint draw b = the mean over corpora of each corpus's draw b (independent streams).
  CB4 SE = SD (ddof 1) of the draws; MDE80 = 2.8 x SE; CP1 / CP2 / CP4 intervals BASIC; percentile printed beside.
  CB5 CP3: S per arm = the mean over seeds 0-4 of the variant-stability rate on the CP1 fits (DS3's construction); ceiling = c4's
      supervised-centroid stability and floor = c4's random same-intent co-filing rate, recomputed on each arm's Space (c4's seed-mean
      S is asserted equal to this script's); R = (S - floor) / (ceiling - floor); D_S interval percentile on stream BOOT_SEED + 4 (DS3's
      EB4), BASIC beside.
  CB6 CP4 nomic at 256 (S0's C1 slice; EMBED-DIM-SLICE selected no nomic slice), CARD - RAW BASIC CI on CP1's stream.
  CB7 the --dry-run reads EVAL of the RAW arms only (IDENTITY; values already of record); no CARD EVAL is read before --run.
  CB8 predictions: numeric HELD iff the point lies in the closed 80% interval; probabilities scored by Brier on the event, KEEP-STRONG
      counted in the KEEP event (DS1 P4's convention).
  CB9 the registration's conditional bracket ("if [EMBED-DIM-SLICE's] outcome moves P3 by more than 0.01 on any corpus, the registrar
      brackets the shifted CP1 points pre-data"): DS1 moved P3 MASSIVE by +0.0113 (+0.03329 against +0.022); no such bracket exists at
      build; the CP1 points are scored as registered and the outcome says so.

OUTPUT (experiment_results/card_protocol/, every file write-once "x"; an existing path REFUSES before any read): outcome.txt (of record,
the registered path), nmi_card.csv (embedder, protocol, slice, corpus, seed, EVAL fine NMI), s_card.csv (CP3 per arm and seed).

LAUNCH (run-operator; zero calls; nothing heavy running; the order is C-EQ-2's):
  python tools/analysis/card_protocol.py --selftest        # also runs the writer's selftest
  python tools/analysis/card_protocol.py --mutants
  python tools/analysis/card_protocol.py --dry-run         # pins, selection, census, RAW IDENTITY (before any Ollama pass), card files
  (the writer's passes; the registrar pins the CARD files)
  python tools/analysis/card_protocol.py --run             # the file of record (write-once)

MUTANT TABLE: `--mutants` (each mutant names the selftest sections that must kill it); the result at build is in the commit message.
Selftest fixtures A / B / C plant REOPEN-CANDIDATE + HELD / KEEP-STRONG + HURTS / KEEP + NOT SHOWN, each recomputed by an independent
oracle (own sqlite read, own slice, sklearn NMI, own weighted NMI and component resampling). Stubs and fixtures only: no real DB read,
no embedding posted.
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
import card_protocol_writer as W      # noqa: E402
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402
II = ITS.II

TAG = "[CARD-PROTOCOL]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
EMB = ("qwen3", "gemma")
DSTAR = {"qwen3": 1024, "gemma": 768}
NOMIC_D = 256
QR, GR, QC, GC = ("qwen3", "RAW"), ("gemma", "RAW"), ("qwen3", "CARD"), ("gemma", "CARD")
NR, NC = ("nomic", "RAW"), ("nomic", "CARD")
DECIDING = (QR, GR, QC, GC)
SEEDS = ITS.SEEDS
BOOT_B = ITS.BOOT_B
BOOT_SEED = ITS.BOOT_SEED
CORPORA = ITS.CORPORA
LEVELS = ITS.LEVELS
MDE_K = 2.8
IDENTITY = {"mean": {"qwen3": {"massive": "0.76554", "clinc": "0.92810", "banking77": "0.84900"},
                     "gemma": {"massive": "0.79883", "clinc": "0.92566", "banking77": "0.89286"}},
            "spread": {"qwen3": {"massive": "0.01428", "clinc": "0.00417", "banking77": "0.01043"},
                       "gemma": {"massive": "0.01277", "clinc": "0.00968", "banking77": "0.01216"}},
            "D": {"massive": "+0.03329", "clinc": "-0.00244", "banking77": "+0.04386"},
            "ci": {"massive": ("+0.02961", "+0.03998"), "clinc": ("-0.00560", "-0.00048"), "banking77": ("+0.04108", "+0.04990")}}
SEL_PATH = os.path.join(ROOT, "experiment_results", "embed_dim_slice", "selection.json")
SEL_SHA = "f1b508cfa889021e6a4d8dac5e82a2188399373996818db0d622aad076bf400d"
DIMSLICE_OUTCOME = os.path.join(ROOT, "experiment_results", "embed_dim_slice", "outcome.txt")
PINS_FILE = os.path.join(ROOT, "experiment_configs", "card_protocol_pins.json")
PINS_SCHEMA = "card_protocol_pins/v1"
PLAN_SE = {"massive": 0.00289, "clinc": 0.00137, "banking77": 0.00247}
PLAN_BAR = {"massive": 0.0246, "clinc": 0.0094, "banking77": 0.0143}
PLAN_DEFF = {"massive": 1.0093, "clinc": 1.0000, "banking77": 1.0015}
PLAN_SE2, PLAN_BAR2 = 0.00135, 0.0161
P_CP1 = {"massive": (0.010, -0.010, 0.030), "clinc": (-0.025, -0.040, -0.010), "banking77": (0.035, 0.015, 0.055)}
P_CP1_V = (("KEEP", 0.75), ("KEEP-STRONG", 0.10), ("REOPEN-CANDIDATE", 0.25))
P_CP2 = (0.020, 0.000, 0.040)
P_CP2_V = (("HELD", 0.45), ("HURTS", 0.05))
P_CP3 = (0.04, 0.01, 0.07)
OUT_DIR = os.path.join(ROOT, "experiment_results", "card_protocol")
OUTCOME = "outcome.txt"
CSVS = ("nmi_card.csv", "s_card.csv")
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_HEADING = "## Registered 2026-10-01 (before any code or call) \u2014 INTENT-S0-CARD-PROTOCOL:"
REG_RE = re.compile(r"^" + re.escape(REG_HEADING), re.M)
REG = ("docs/judge_v2_program.md \"## Registered 2026-10-01 (before any code or call) \u2014 INTENT-S0-CARD-PROTOCOL: at each embedder's "
       "EMBED-DIM-SLICE-selected slice, ...\" L22655-L22680 _as_of 46954215; kind zero-call CPU reader")
READINGS = ("builder's readings: CB1 two new scripts importing S0 and embedder_arms unchanged; CB2 S0's route-parity bars on the RAW "
            "route and on the CARD route's repeatability / resume parity, cos(CARD, RAW) printed with no bar, no transform (CW1), the "
            "tag's digest = S0's RAW file's digest (CW3); CB3 DS1's bootstrap stream, paired over arms, CP2 joint draws averaged per draw "
            "index over independent per-corpus streams; CB4 SE = SD of draws, MDE80 = 2.8 SE, BASIC intervals; CB5 CP3 S on the CP1 fits, "
            "c4's ceiling and floor per arm, percentile interval (DS3's EB4); CB6 CP4 nomic at 256; CB7 the dry-run reads RAW EVAL only; "
            "CB8 closed 80% intervals, KEEP-STRONG inside the KEEP event; CB9 no shifted-CP1-points bracket at build, points scored as "
            "registered")
DOES_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): quantisation effects; capability text; parity (no TOST); that MASSIVE's "
                 "NEITHER is explanation; any change to the embedder of record (D3 is the author's)")
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
    ok = os.path.isfile(programme) and REG_RE.search(open(programme, encoding="utf-8").read()) is not None
    print("%s registration heading (line-anchored) %r in %s: %s" % (TAG, REG_HEADING, os.path.basename(programme), "PRESENT" if ok else "ABSENT"))
    return ok


def read_selection(path, want_sha):
    with open(path, "rb") as f:
        raw = f.read()
    data = raw.replace(b"\r\n", b"\n")
    sha = hashlib.sha256(data).hexdigest()
    print("%s selection %s sha256 (LF rendering) %s%s [%s]" % (TAG, path, sha, "" if raw == data else " (CRLF working-tree sha256 %s)"
                                                               % hashlib.sha256(raw).hexdigest(), "PIN OK" if sha == want_sha else "PIN MISMATCH"))
    if sha != want_sha:
        refuse("EMBED-DIM-SLICE's selection.json sha256 %s != %s" % (sha, want_sha))
    js = json.loads(data.decode("utf-8"))
    got = {"qwen3": js.get("d_q*"), "gemma": js.get("d_g*")}
    print("%s d_q* = %s, d_g* = %s (registered %d / %d; no slice is reselected)" % (TAG, got["qwen3"], got["gemma"], DSTAR["qwen3"], DSTAR["gemma"]))
    if got != DSTAR:
        refuse("selection.json d* %s != the registered %s" % (got, DSTAR))
    return sha


def dimslice_verdict(path):
    """EMBED-DIM-SLICE's DS1 verdict of record (for the registered READING AGAINST D3)."""
    txt = open(path, "rb").read().replace(b"\r\n", b"\n")
    m = re.search(r"^DS1 VERDICT: (REOPEN-CANDIDATE|KEEP-STRONG|KEEP)\b", txt.decode("utf-8"), re.M)
    if not m:
        refuse("%s carries no DS1 VERDICT line" % path)
    v = m.group(1)
    print("%s EMBED-DIM-SLICE outcome %s sha256 (LF) %s: DS1 VERDICT %s" % (TAG, os.path.basename(path), hashlib.sha256(txt).hexdigest()[:16], v))
    return v


PINS_OVERRIDE = [None]


def load_card_pins(pins_file=None):
    pf = pins_file or PINS_OVERRIDE[0] or PINS_FILE
    with open(pf, encoding="utf-8") as f:
        pins = json.load(f)
    if pins.get("schema") != PINS_SCHEMA:
        refuse("%s schema %r != %r" % (pf, pins.get("schema"), PINS_SCHEMA))
    return pins


def card_pin_check(e, path, pins, strict):
    want = pins.get(e + "_card")
    II.open_db_ro(path).close()
    s = II.file_sha(path)
    print("%s pin %s: sha256 %s [%s]" % (TAG, os.path.basename(path), s, "UNPINNED" if not want else ("PIN OK" if want == s else "PIN MISMATCH")))
    if want and want != s:
        refuse("%s sha256 %s != the pinned %s" % (path, s, want))
    if strict and not want:
        refuse("%s is UNPINNED: --run reads a CARD file only against the registrar's pin" % path)
    return s


def emb_file(arm, emb_dir):
    e, prot = arm
    return ITS.emb_path(e, emb_dir) if prot == "RAW" else W.card_path(e, emb_dir)


def slice_of(arm):
    return NOMIC_D if arm[0] == "nomic" else DSTAR[arm[0]]


def arm_key(arm):
    return arm[0] if arm[1] == "RAW" else arm[0] + "_card"


def load_inputs(db, emb_dir, strict, cards=True):
    """-> (sha0, CS, texts, derived, arms). arms = the arms read: the four deciding arms (CARD ones only when `cards`), plus nomic RAW
    and CARD when intent_emb_nomic_card.db is pinned (strict) or present (dry-run)."""
    check_its_blob()
    psha = W.load_prompts()
    pins = load_card_pins()
    nomic = bool(pins.get("nomic_card")) if strict else os.path.exists(emb_file(NC, emb_dir))
    arms = [a for a in DECIDING if cards or a[1] == "RAW"] + ([NR, NC] if (nomic and cards) else [])
    sha0 = {"ingest_db": ITS.pin_check(db, "ingest_db", strict)}
    ITS.raw_pin_check(db, strict)
    for a in arms:
        p = emb_file(a, emb_dir)
        if a[1] == "RAW":
            sha0[arm_key(a)] = ITS.pin_check(p, "emb", strict, sub=a[0], label="intent_emb_%s.db" % a[0])
        else:
            sha0[arm_key(a)] = card_pin_check(a[0], p, pins, strict)
    CS = ITS.load_corpora(db)
    texts, set_sha, derived = ITS.text_set(CS)
    for a in arms:
        if a[1] == "RAW":
            ITS.check_meta(emb_file(a, emb_dir), ITS.expected_meta(a[0], set_sha, len(texts), sha0["ingest_db"]))
        else:
            ITS.check_meta(emb_file(a, emb_dir), W.expected_meta_card(a[0], set_sha, len(texts), sha0["ingest_db"], psha))
    return sha0, CS, texts, derived, arms, psha


def after_check(sha0, db, emb_dir):
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else ITS.emb_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))


def load_slice(path, arm, texts, allow_missing=False):
    """S0's load_vectors at the arm's slice (ITS.SLICE2 set for the call, restored in a finally)."""
    d = slice_of(arm)
    saved = ITS.SLICE2
    ITS.SLICE2 = d
    try:
        v = ITS.load_vectors(path, arm[0], texts, allow_missing=allow_missing)
    finally:
        ITS.SLICE2 = saved
    bad = sum(1 for x in v.values() if len(x) != d)
    if bad:
        refuse("%s %s: %d vectors are not %d-d after the slice read" % (arm[0], arm[1], bad, d))
    return v


# ------------------------------------------------------------------------------------------------ fits, EVAL, bootstrap
def arm_eval(C, vecs, arm, variants=None):
    """TRAIN fits (seeds 0-4) at the arm's slice, EVAL filed to them (EVAL read once for the arm). On MASSIVE with `variants`: the
    variant-stability arrays on the same fits (CP3) and c4's ceiling / floor on the same Space."""
    d = slice_of(arm)
    S = ITS.Space(vecs, C, d)
    kf = II.GOLD_K[C.name][1]
    fits = [ITS.km_fit(C, S, kf, s, "CP k-means %s %s@%d %s fine K=%d s%d" % (arm[0], arm[1], d, C.name, kf, s)) for s in SEEDS]
    ev = ITS.S_idx(C, S, SS.EVAL)
    EVENTS.append(("EVAL", "%s %s %s" % (arm[0], arm[1], C.name)))
    truth = ITS.codes(C.fine[ev])
    preds = [ITS.assign(S.X[ev], Cm) for Cm in fits]
    out = {"ev": ev, "truth": truth, "preds": preds, "nm": [ITS.nmi(truth, p) for p in preds]}
    if variants is not None:
        v = [(i, tx) for i, tx, _c in variants if S.have[i] and tx in S.vecs]
        if len(v) != len(variants):
            refuse("massive %s %s: %d of %d variants have a vector" % (arm[0], arm[1], len(v), len(variants)))
        oi = np.array([i for i, _t in v], dtype=int)
        Xo, Xv = S.X[oi], S.of([tx for _i, tx in v])
        out["same"] = [(ITS.assign(Xo, Cm) == ITS.assign(Xv, Cm)).astype(np.float64) for Cm in fits]
        out["vcomp"] = C.comp[oi]
        c4 = ITS.c4(C, {"qwen3": S}, variants)
        mine = float(np.mean([s.mean() for s in out["same"]]))
        theirs = float(np.mean([c4["per_seed"][s] for s in SEEDS]))
        if mine != theirs:
            refuse("CP3 %s %s: S0's c4() seed-mean S %r != this script's %r (a different machinery)" % (arm[0], arm[1], theirs, mine))
        out["ceiling"], out["floor"], out["floor_n"] = c4["centroid_stab"], c4["cofile"], c4["cofile_n"]
    return out


def boot(c, truth, comp, preds, B):
    """One paired component bootstrap per corpus: draw b's weights are shared by every arm (CB3). -> {arm: array of seed-mean NMI}."""
    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index("fine"))
    out = {a: [] for a in preds}
    for w in ITS.comp_weights(comp, B, rng):
        for a in preds:
            out[a].append(float(np.mean([ITS.nmi(truth, p, w) for p in preds[a]])))
    return {a: np.array(v) for a, v in out.items()}


def spread(nm):
    return float(max(nm) - min(nm))


def contrast(m, draws, plus, minus):
    """Point, BASIC and percentile intervals and SE of m[plus] - m[minus] on the paired draws."""
    D = m[plus] - m[minus]
    dd = draws[plus] - draws[minus]
    lo, hi = ITS.basic_ci(D, dd)
    plo, phi = ITS.pct_ci(dd)
    se = float(np.std(dd, ddof=1))
    return {"D": float(D), "lo": lo, "hi": hi, "plo": plo, "phi": phi, "se": se, "mde80": MDE_K * se, "draws": dd}


def cp1(m, nm, draws, n, comp):
    r = contrast(m, draws, GC, QC)
    r["spread"] = {QC: spread(nm[QC]), GC: spread(nm[GC])}
    r["bar"] = max(r["mde80"], max(r["spread"][QC], r["spread"][GC]))
    r["status"] = ITS.c1_status(r["D"], r["lo"], r["hi"], r["bar"])
    r.update({"n": int(n), "components": int(len(np.unique(comp))), "kish": ITS.kish(comp)})
    r["n_eff"] = r["n"] / r["kish"]
    return r


def verdict(status):
    nb = sum(1 for c in CORPORA if status[c] == "BETTER")
    nw = sum(1 for c in CORPORA if status[c] == "WORSE")
    if nb >= 2:
        return "REOPEN-CANDIDATE", nb, nw
    if nw >= 2:
        return "KEEP-STRONG", nb, nw
    return "KEEP", nb, nw


def cp2(per):
    """per[c] = {"m": means, "nm": per-seed NMI, "draws": draws} (each corpus's own stream). Joint draw b = mean over corpora."""
    D = float(np.mean([per[c]["m"][QC] - per[c]["m"][QR] for c in CORPORA]))
    jd = np.mean([per[c]["draws"][QC] - per[c]["draws"][QR] for c in CORPORA], axis=0)
    se = float(np.std(jd, ddof=1))
    lo, hi = ITS.basic_ci(D, jd)
    plo, phi = ITS.pct_ci(jd)
    sterm = float(np.mean([max(spread(per[c]["nm"][QC]), spread(per[c]["nm"][QR])) for c in CORPORA]))
    bar = max(MDE_K * se, sterm)
    if D > bar and lo > 0:
        st = "HELD"
    elif D < -bar and hi < 0:
        st = "HURTS"
    else:
        st = "NOT SHOWN"
    return {"D": D, "se": se, "mde80": MDE_K * se, "spread_term": sterm, "bar": bar, "lo": lo, "hi": hi, "plo": plo, "phi": phi,
            "status": st, "per": {c: per[c]["m"][QC] - per[c]["m"][QR] for c in CORPORA}, "draws": jd}


def cp3(E, B):
    """E = {arm: arm_eval output on MASSIVE with variants}. S, R per arm; D_S = S(gemma CARD) - S(qwen3 CARD), percentile interval."""
    rows = {}
    for a, o in E.items():
        S = float(np.mean([s.mean() for s in o["same"]]))
        den = o["ceiling"] - o["floor"]
        rows[a] = {"S": S, "per_seed": [float(s.mean()) for s in o["same"]], "ceiling": o["ceiling"], "floor": o["floor"],
                   "floor_n": o["floor_n"], "R": (S - o["floor"]) / den if den else float("nan")}
    comp = E[QC]["vcomp"]
    D = rows[GC]["S"] - rows[QC]["S"]
    draws = []
    for w in ITS.comp_weights(comp, B, np.random.default_rng(BOOT_SEED + 4)):
        sw = w.sum()
        draws.append(float(np.mean([(w * s).sum() / sw for s in E[GC]["same"]]) - np.mean([(w * s).sum() / sw for s in E[QC]["same"]])))
    lo, hi = ITS.pct_ci(draws)
    blo, bhi = ITS.basic_ci(D, draws)
    se = float(np.std(draws, ddof=1))
    return {"rows": rows, "D": D, "lo": lo, "hi": hi, "blo": blo, "bhi": bhi, "se": se, "n": int(len(comp)),
            "components": int(len(np.unique(comp))), "kish": ITS.kish(comp)}


# ------------------------------------------------------------------------------------------------ identity
def identity_values(per):
    out = {"mean": {}, "spread": {}, "D": {}, "ci": {}}
    for e, a in (("qwen3", QR), ("gemma", GR)):
        out["mean"][e] = {c: "%.5f" % per[c]["m"][a] for c in CORPORA}
        out["spread"][e] = {c: "%.5f" % spread(per[c]["nm"][a]) for c in CORPORA}
    for c in CORPORA:
        r = contrast(per[c]["m"], per[c]["draws"], GR, QR)
        out["D"][c] = "%+.5f" % r["D"]
        out["ci"][c] = ("%+.5f" % r["lo"], "%+.5f" % r["hi"])
    return out


def identity_check(got, target, with_ci=True):
    bad = []
    for k in ("mean", "spread"):
        for e in EMB:
            bad += ["%s %s %s" % (k, e, c) for c in CORPORA if got[k][e][c] != target[k][e][c]]
    bad += ["D %s" % c for c in CORPORA if got["D"][c] != target["D"][c]]
    if with_ci:
        bad += ["CI %s" % c for c in CORPORA if tuple(got["ci"][c]) != tuple(target["ci"][c])]
    line = ("IDENTITY: RAW qwen3@%d seed-mean EVAL fine NMI %s (EMBED-DIM-SLICE %s), spread %s (%s); RAW gemma@%d %s (%s), spread %s (%s); "
            "DS1 D* %s (%s); 95%% BASIC CI %s (%s)"
            % (DSTAR["qwen3"], " / ".join(got["mean"]["qwen3"][c] for c in CORPORA), " / ".join(target["mean"]["qwen3"][c] for c in CORPORA),
               " / ".join(got["spread"]["qwen3"][c] for c in CORPORA), " / ".join(target["spread"]["qwen3"][c] for c in CORPORA),
               DSTAR["gemma"], " / ".join(got["mean"]["gemma"][c] for c in CORPORA), " / ".join(target["mean"]["gemma"][c] for c in CORPORA),
               " / ".join(got["spread"]["gemma"][c] for c in CORPORA), " / ".join(target["spread"]["gemma"][c] for c in CORPORA),
               " / ".join(got["D"][c] for c in CORPORA), " / ".join(target["D"][c] for c in CORPORA),
               " / ".join("[%s, %s]" % tuple(got["ci"][c]) for c in CORPORA), " / ".join("[%s, %s]" % tuple(target["ci"][c]) for c in CORPORA)))
    print("%s %s" % (TAG, line))
    if bad:
        refuse("IDENTITY PRECONDITION FAILED on %s: EMBED-DIM-SLICE's RAW values at d_q* %d / d_g* %d are not reproduced; no readout is "
               "written" % (bad, DSTAR["qwen3"], DSTAR["gemma"]))
    return line + " -> REPRODUCED"


# ------------------------------------------------------------------------------------------------ lines
def scoreable(pred, bar, mde):
    beyond = abs(pred) - bar
    return beyond, ("SCOREABLE" if bool(beyond > mde) else "DESCRIPTIVE-ONLY")


def brier(p, event):
    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2


def _hit(v, lo, hi):
    return "HELD" if (np.isfinite(v) and lo <= v <= hi) else "FAILED"


def support_lines(R):
    L = ["== SUPPORT (measured in-run; planning values beside) =="]
    for c in CORPORA:
        r = R["cp1"][c]
        beyond, word = scoreable(P_CP1[c][0], r["bar"], r["mde80"])
        L.append("  CP1 %s: n %d EVAL items in %d components, Kish DEFF %.4f (planned %.4f), n_eff %.0f; SE(D_card) %.5f (planned %.5f), "
                 "MDE80 2.8 x SE %.5f, bar %.5f (planning %.4f); at the predicted %+.3f: |P| - bar = %+.5f vs MDE80 -> %s"
                 % (c, r["n"], r["components"], r["kish"], PLAN_DEFF[c], r["n_eff"], r["se"], PLAN_SE[c], r["mde80"], r["bar"], PLAN_BAR[c],
                    P_CP1[c][0], beyond, word))
    r = R["cp2"]
    beyond, word = scoreable(P_CP2[0], r["bar"], r["mde80"])
    L.append("  CP2: SE(D-bar) %.5f (planned %.5f; joint draws), MDE80 %.5f, spread term %.5f, bar_pool %.5f (planning %.4f); at the predicted "
             "%+.3f: |P| - bar_pool = %+.5f vs MDE80 -> %s" % (r["se"], PLAN_SE2, r["mde80"], r["spread_term"], r["bar"], PLAN_BAR2, P_CP2[0],
                                                               beyond, word))
    L.append("  STRUCTURAL LEG (registered (g)): CP1 and CP2 are reachable only where the true difference exceeds the in-run seed spread, "
             "which does not shrink with n; inside it a corpus reads NEITHER and CP2 NOT SHOWN at any budget")
    return L


def criteria_lines(R):
    L = ["== CP1 (deciding; D_card = mean_s NMI_EVAL(gemma, CARD, %d) - mean_s NMI_EVAL(qwen3, CARD, %d) at K_f; S0's C1 rule) =="
         % (DSTAR["gemma"], DSTAR["qwen3"])]
    for c in CORPORA:
        r = R["cp1"][c]
        L.append("  CP1 %s K_f %d n %d: D_card = gemma %.5f - qwen3 %.5f = %+.5f, 95%% BASIC CI [%+.5f, %+.5f] (decides); percentile "
                 "[%+.5f, %+.5f]; SE %.5f, MDE80 %.5f, spread max(qwen3 CARD %.5f, gemma CARD %.5f), bar %.5f -> %s"
                 % (c, II.GOLD_K[c][1], r["n"], R["m"][c][GC], R["m"][c][QC], r["D"], r["lo"], r["hi"], r["plo"], r["phi"], r["se"],
                    r["mde80"], r["spread"][QC], r["spread"][GC], r["bar"], r["status"]))
    v, nb, nw = R["verdict"]
    st = {c: R["cp1"][c]["status"] for c in CORPORA}
    better = [c for c in CORPORA if st[c] == "BETTER"]
    worse = [c for c in CORPORA if st[c] == "WORSE"]
    if v == "REOPEN-CANDIDATE":
        L.append("CP1 VERDICT: REOPEN-CANDIDATE -- gemma BETTER on %d of 3 %s (>= 2); WORSE on %d of 3 %s" % (nb, better, nw, worse))
        L.append("F-CP1: FIRED (CP1 reads REOPEN-CANDIDATE): it overturns the reading that protocol explains S0's gemma edge; with "
                 "EMBED-DIM-SLICE REOPEN-CANDIDATE it satisfies the first of D3's revisit conditions (CP1 HELD in the gemma direction); E1 "
                 "remains")
    else:
        if v == "KEEP-STRONG":
            L.append("CP1 VERDICT: KEEP-STRONG (a sub-case of KEEP) -- gemma BETTER on %d of 3 %s (<= 1); gemma WORSE on %d of 3 %s (>= 2)"
                     % (nb, better, nw, worse))
        else:
            L.append("CP1 VERDICT: KEEP -- gemma BETTER on %d of 3 %s (<= 1); gemma WORSE on %d of 3 %s" % (nb, better, nw, worse))
        L.append("F-CP1: NOT FIRED (CP1 reads %s, not REOPEN-CANDIDATE)" % v)
        L.append("READING (KEEP): gemma's fine-level edge over qwen3 under card prompts at the selected slices is \"not shown\" on >= 2 of 3 "
                 "intent corpora; KEEP reads \"not shown\", never \"explained by protocol\" (Support (f))")
        if v == "KEEP-STRONG":
            L.append("READING (KEEP-STRONG): in addition, qwen3 CARD is better than gemma CARD at the fine level on >= 2 of 3")
    if st["massive"] == "NEITHER":
        L.append("READING caveat: MASSIVE reads NEITHER inside its bar (D_card %+.5f, bar %.5f); it is DESCRIPTIVE-ONLY at the prediction "
                 "and its NEITHER is not explanation" % (R["cp1"]["massive"]["D"], R["cp1"]["massive"]["bar"]))
    ds = R["dimslice"]
    if v == "REOPEN-CANDIDATE" and ds == "REOPEN-CANDIDATE":
        L.append("READING AGAINST D3 (registered): REOPEN-CANDIDATE on both EMBED-DIM-SLICE and CP1: the evidence for the author's revisit is "
                 "complete except E1 and quantisation (EMBED-QUANT, an option)")
    elif v != "REOPEN-CANDIDATE" and ds != "REOPEN-CANDIDATE":
        L.append("READING AGAINST D3 (registered): KEEP on both EMBED-DIM-SLICE and CP1: D3 stands; neither the slice nor the protocol is "
                 "shown to hide a gemma advantage")
    else:
        L.append("READING AGAINST D3 (registered): Mixed (EMBED-DIM-SLICE %s, CP1 %s): relayed as mixed; no wording chosen here" % (ds, v))
    r = R["cp2"]
    L.append("== CP2 (deciding; pooled D-bar = (1/3) Sum_c [mean_s NMI_EVAL(qwen3, CARD, %d) - mean_s NMI_EVAL(qwen3, RAW, %d)]) =="
             % (DSTAR["qwen3"], DSTAR["qwen3"]))
    L.append("  CP2 per corpus qwen3 CARD - RAW: %s" % "; ".join("%s %+.5f" % (c, r["per"][c]) for c in CORPORA))
    L.append("  CP2 D-bar %+.5f, 95%% BASIC CI [%+.5f, %+.5f] (joint bootstrap, independent per corpus; decides); percentile [%+.5f, %+.5f]; "
             "SE %.5f, MDE80 %.5f, spread term %.5f, bar_pool %.5f -> %s"
             % (r["D"], r["lo"], r["hi"], r["plo"], r["phi"], r["se"], r["mde80"], r["spread_term"], r["bar"], r["status"]))
    if r["status"] == "HELD":
        L.append("CP2 VERDICT: HELD (card raises qwen3)")
        L.append("F-CP2: NOT FIRED (CP2 reads HELD)")
    else:
        L.append("CP2 VERDICT: %s" % r["status"])
        L.append("F-CP2: FIRED (CP2 reads %s): \"qwen3 is instruction-aware and was run RAW\" is withdrawn as a candidate MECHANISM for S0's "
                 "qwen3 rows (the sentence stays as a disclosure only)" % r["status"])
        if r["status"] == "HURTS":
            L.append("F-CP2 (HURTS): in addition, RAW is the better protocol for qwen3 on intent clustering")
    return L


def descriptive_lines(R):
    L = ["== CP3 (DESCRIPTIVE-ONLY; MASSIVE slot swap, K %d, mean over seeds 0-4; R = (S - floor) / (ceiling - floor)) ==" % II.GOLD_K["massive"][1]]
    d3 = R["cp3"]
    for a in DECIDING:
        x = d3["rows"][a]
        L.append("  CP3 %s %s@%d: S %.5f (seeds %s); supervised-centroid ceiling %.5f; random co-filing floor %.5f (%d pairs); R %.4f"
                 % (a[0], a[1], slice_of(a), x["S"], " / ".join("%.4f" % s for s in x["per_seed"]), x["ceiling"], x["floor"], x["floor_n"], x["R"]))
    L.append("  CP3 S(gemma CARD) - S(qwen3 CARD) = %+.5f, 95%% percentile CI [%+.5f, %+.5f] (CB5; BASIC [%+.5f, %+.5f]); SE %.5f; n %d variants "
             "in %d components, Kish DEFF %.4f" % (d3["D"], d3["lo"], d3["hi"], d3["blo"], d3["bhi"], d3["se"], d3["n"], d3["components"], d3["kish"]))
    L.append("== CP4 (DESCRIPTIVE-ONLY) ==")
    for c in CORPORA:
        g = R["cp4"]["gemma"][c]
        L.append("  CP4 %s gemma CARD - RAW @%d: %+.5f, 95%% BASIC CI [%+.5f, %+.5f]" % (c, DSTAR["gemma"], g["D"], g["lo"], g["hi"]))
    if R["cp4"]["nomic"] is None:
        L.append("  CP4 nomic: NOT READ -- intent_emb_nomic_card.db is not pinned in card_protocol_pins.json (the DESCRIPTIVE arm; the "
                 "deciding criteria do not read it)")
    else:
        for c in CORPORA:
            x = R["cp4"]["nomic"][c]
            L.append("  CP4 %s nomic @%d: RAW %.5f, CARD %.5f, CARD - RAW %+.5f, 95%% BASIC CI [%+.5f, %+.5f]"
                     % (c, NOMIC_D, R["m"][c][NR], R["m"][c][NC], x["D"], x["lo"], x["hi"]))
    L.append("== PRINTED, NEVER DECIDING ==")
    for c in CORPORA:
        L.append("  fine NMI %s seed-mean EVAL: %s" % (c, "; ".join("%s %s@%d %.5f" % (a[0], a[1], slice_of(a), R["m"][c][a]) for a in R["arms"])))
    return L


def predictions_lines(R):
    L = ["== PREDICTIONS (numeric HELD iff the point lies in the closed 80%% interval; probabilities scored on the event, Brier; CB8; CB9: "
         "scored as registered, no shifted-points bracket) =="]
    for c in CORPORA:
        x = R["cp1"][c]["D"]
        L.append("  CP1-P %s D_card %+.5f vs %+.3f [%+.3f, %+.3f]: %s" % (c, x, P_CP1[c][0], P_CP1[c][1], P_CP1[c][2], _hit(x, P_CP1[c][1], P_CP1[c][2])))
    v = R["verdict"][0]
    ev = {"KEEP": v in ("KEEP", "KEEP-STRONG"), "KEEP-STRONG": v == "KEEP-STRONG", "REOPEN-CANDIDATE": v == "REOPEN-CANDIDATE"}
    for name, p in P_CP1_V:
        L.append("  CP1-P %s (p %.2f): %s, Brier %.4f" % (name, p, "OCCURRED" if ev[name] else "did not occur", brier(p, ev[name])))
    x = R["cp2"]["D"]
    L.append("  CP2-P D-bar %+.5f vs %+.3f [%+.3f, %+.3f]: %s" % (x, P_CP2[0], P_CP2[1], P_CP2[2], _hit(x, P_CP2[1], P_CP2[2])))
    s = R["cp2"]["status"]
    for name, p in P_CP2_V:
        L.append("  CP2-P %s (p %.2f): %s, Brier %.4f" % (name, p, "OCCURRED" if s == name else "did not occur", brier(p, s == name)))
    x = R["cp3"]["D"]
    L.append("  CP3-P gemma S - qwen3 S under CARD %+.5f vs %+.3f [%+.3f, %+.3f]: %s" % (x, P_CP3[0], P_CP3[1], P_CP3[2], _hit(x, P_CP3[1], P_CP3[2])))
    return L


def out_paths(out_dir):
    return [os.path.join(out_dir, p) for p in (OUTCOME,) + CSVS]


def evaluate(CS, vecs, derived, arms, B):
    """Every fit, EVAL filing, bootstrap and criterion. -> R (no line printed, nothing written)."""
    R = {"arms": arms, "m": {}, "cp1": {}, "per": {}, "B": B}
    E3 = {}
    for c in CORPORA:
        C = CS[c]
        out = {a: arm_eval(C, vecs[a], a, derived["variants"] if (c == "massive" and a in DECIDING) else None) for a in arms}
        ev = out[QR]["ev"]
        for a in arms:
            if not np.array_equal(out[a]["ev"], ev):
                refuse("%s: the EVAL rows differ between arms (%s %s; a vector missing)" % (c, a[0], a[1]))
        if c == "massive":
            E3 = {a: out[a] for a in DECIDING}
        truth, comp = out[QR]["truth"], C.comp[ev]
        nm = {a: out[a]["nm"] for a in arms}
        m = {a: float(np.mean(nm[a])) for a in arms}
        draws = boot(c, truth, comp, {a: out[a]["preds"] for a in arms}, B)
        R["m"][c] = m
        R["per"][c] = {"m": m, "nm": nm, "draws": draws}
        R["cp1"][c] = cp1(m, nm, draws, len(truth), comp)
    R["verdict"] = verdict({c: R["cp1"][c]["status"] for c in CORPORA})
    R["cp2"] = cp2(R["per"])
    R["cp3"] = cp3(E3, B)
    R["cp4"] = {"gemma": {c: contrast(R["m"][c], R["per"][c]["draws"], GC, GR) for c in CORPORA},
                "nomic": ({c: contrast(R["m"][c], R["per"][c]["draws"], NC, NR) for c in CORPORA} if NC in arms else None)}
    R["identity"] = identity_values(R["per"])
    return R


def main_run(db=None, emb_dir=None, out_dir=OUT_DIR, programme=PROGRAMME, identity=None, sel_path=SEL_PATH, sel_sha=SEL_SHA, B=None,
             dimslice=DIMSLICE_OUTCOME):
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    identity = identity or IDENTITY
    B = BOOT_B if B is None else B
    del EVENTS[:]
    print("%s pool of record: none read (S0's DBs and the CARD files); zero calls; no embeddings; no GATE row" % TAG)
    for p in out_paths(out_dir):
        if os.path.lexists(p):
            refuse("%s exists: every output of record is write-once" % p)
    check_its_blob()
    heavy_check()
    if not check_registered(programme):
        refuse("INTENT-S0-CARD-PROTOCOL is not registered in %s: --run writes a record only after the registration" % programme)
    selsha = read_selection(sel_path, sel_sha)
    ds = dimslice_verdict(dimslice)
    sha0, CS, texts, derived, arms, psha = load_inputs(db, emb_dir, True)
    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts) for a in arms}
    del ITS.FIT_LOG[:]
    R = evaluate(CS, vecs, derived, arms, B)
    R["dimslice"] = ds
    id_line = identity_check(R["identity"], identity)
    audit = ITS.fit_audit()
    n_ev = sum(1 for e in EVENTS if e[0] == "EVAL")
    after_check(sha0, db, emb_dir)
    L = ["INTENT-S0-CARD-PROTOCOL outcome (tools/analysis/card_protocol.py blob %s; writer card_protocol_writer.py blob %s; S0 machinery "
         "intent_transfer_s0.py blob %s, imported unchanged)" % (RO.git_blob_lf(os.path.abspath(__file__)), W.writer_blob(), ITS_BLOB),
         "registration: " + REG,
         "zero judge calls; zero embeddings; no build; no GATE row; pool of record: none read; pins re-checked before and after, unchanged: %s"
         % {k: v[:16] for k, v in sha0.items()},
         "prompts: experiment_configs/card_protocol_prompts.json sha256 (LF) %s; %s" % (psha, "; ".join("%s %r sha256 %s" % (e, W.PROMPTS[e], W.sha_text(W.PROMPTS[e])[:16]) for e in W.EMB)),
         "arms: %s; slices d_q* %d, d_g* %d from selection.json sha256 %s; nomic @%d (CB6); seeds 0-4; EVAL read %d times (once per arm per "
         "corpus, plus c4's co-filing read on MASSIVE)" % (", ".join("%s %s" % a for a in arms), DSTAR["qwen3"], DSTAR["gemma"], selsha, NOMIC_D, n_ev),
         "EMBED-DIM-SLICE DS1 VERDICT of record: %s" % ds,
         READINGS, audit, id_line]
    L += support_lines(R) + criteria_lines(R) + descriptive_lines(R) + predictions_lines(R) + [DOES_NOT_SHOW]
    for ln in L:
        print(ln)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, OUTCOME), "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(out_dir, CSVS[0]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["embedder", "protocol", "slice", "corpus", "level", "side", "seed", "nmi"])
        for c in CORPORA:
            for a in arms:
                for s, x in zip(SEEDS, R["per"][c]["nm"][a]):
                    w.writerow([a[0], a[1], slice_of(a), c, "fine", "EVAL", s, "%.6f" % x])
    with open(os.path.join(out_dir, CSVS[1]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["embedder", "protocol", "slice", "seed", "S", "ceiling", "floor"])
        for a in DECIDING:
            x = R["cp3"]["rows"][a]
            for s, v in zip(SEEDS, x["per_seed"]):
                w.writerow([a[0], a[1], slice_of(a), s, "%.6f" % v, "%.6f" % x["ceiling"], "%.6f" % x["floor"]])
    print("%s wrote %s (write-once, of record)" % (TAG, os.path.join(out_dir, OUTCOME)))
    R["lines"] = L
    return R


def dry_run(db=None, emb_dir=None, programme=PROGRAMME, identity=None, sel_path=SEL_PATH, sel_sha=SEL_SHA, timing=True, B=None,
            dimslice=DIMSLICE_OUTCOME):
    """Pins, selection, census, the RAW IDENTITY (values of record; CB7), CARD file completeness, one timed fit. Writes nothing."""
    db = db or II.DEFAULT_OUT
    emb_dir = emb_dir or ITS.DATA_ROOT
    identity = identity or IDENTITY
    B = BOOT_B if B is None else B
    del EVENTS[:]
    print("%s pool of record: none read; zero calls; DRY RUN: nothing written" % TAG)
    check_its_blob()
    heavy_check()
    check_registered(programme)
    read_selection(sel_path, sel_sha)
    dimslice_verdict(dimslice)
    sha0, CS, texts, derived, arms, _psha = load_inputs(db, emb_dir, False, cards=False)
    for e in W.EMB:
        p = W.card_path(e, emb_dir)
        if os.path.exists(p):
            v = load_slice(p, (e, "CARD"), texts, allow_missing=True)
            print("%s CARD file %s: %d of %d texts present (%d missing)%s" % (TAG, p, len(v), len(texts), len(texts) - len(v),
                                                                              "" if len(v) == len(texts) else ": --run REFUSES until COMPLETE"))
            del v
        else:
            print("%s CARD file %s absent: run tools/analysis/card_protocol_writer.py --embed --embedder %s --go first" % (TAG, p, e))
    for c in CORPORA:
        C = CS[c]
        ev = C.idx(SS.EVAL)
        k = ITS.kish(C.comp[ev])
        print("%s census %s: TRAIN %d, EVAL %d in %d components (Kish DEFF %.4f, n_eff %.0f); GATE not read"
              % (TAG, c, len(C.idx(SS.TRAIN)), len(ev), len(np.unique(C.comp[ev])), k, len(ev) / k))
    raw = [QR, GR]
    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts) for a in raw}
    del ITS.FIT_LOG[:]
    per = {}
    for c in CORPORA:
        out = {a: arm_eval(CS[c], vecs[a], a) for a in raw}
        if not np.array_equal(out[QR]["ev"], out[GR]["ev"]):
            refuse("%s: the EVAL rows differ between the RAW arms" % c)
        nm = {a: out[a]["nm"] for a in raw}
        m = {a: float(np.mean(nm[a])) for a in raw}
        per[c] = {"m": m, "nm": nm, "draws": boot(c, out[QR]["truth"], CS[c].comp[out[QR]["ev"]], {a: out[a]["preds"] for a in raw}, B)}
    identity_check(identity_values(per), identity, with_ci=True)
    if timing:
        C = CS["clinc"]
        S = ITS.Space(vecs[QR], C, DSTAR["qwen3"])
        t0 = time.time()
        ITS.km_fit(C, S, II.GOLD_K["clinc"][1], 0, "CP dry timing qwen3@%d clinc s0" % DSTAR["qwen3"])
        dt = time.time() - t0
        print("%s TIMING: one %d-d CLINC fine fit %.1f s; the run's %d fits priced at about %.0f s plus %d bootstrap draws x 3 corpora"
              % (TAG, DSTAR["qwen3"], dt, 6 * len(SEEDS) * len(CORPORA) + 4 * len(SEEDS), dt * (6 * len(SEEDS) * len(CORPORA) + 4 * len(SEEDS)), B))
    after_check(sha0, db, emb_dir)
    print("%s %s" % (TAG, ITS.fit_audit()))
    print("%s DRY RUN complete: nothing written" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest fixtures
NAT = {"qwen3": 4096, "gemma": 768, "nomic": 768}
NF = 20                                    # signal dims: fine axes 0-15, coarse 16-19
# arm mode per corpus: a float = noise sigma on the signal dims; "copyQC" = the qwen3 CARD vector's first coordinates (a deterministic
# NEITHER: the same partition up to 0.01-noise dims); "copyQR" = the qwen3 RAW vector (qwen3 CARD = RAW: D-bar exactly 0); "garble" = no
# class signal
FX_SPEC = {
    "A": {QR: {"massive": 1.6, "clinc": 1.6, "banking77": 1.6}, GR: {"massive": 1.0, "clinc": 1.0, "banking77": 1.0},
          QC: {"massive": 0.9, "clinc": 0.9, "banking77": 0.9}, GC: {"massive": 0.25, "clinc": "copyQC", "banking77": 0.25},
          NR: {"massive": 1.2, "clinc": 1.2, "banking77": 1.2}, NC: {"massive": 0.6, "clinc": 1.2, "banking77": 2.4}},
    "B": {QR: {"massive": 0.25, "clinc": 0.25, "banking77": 0.25}, GR: {"massive": 1.0, "clinc": 1.0, "banking77": 1.0},
          QC: {"massive": 1.3, "clinc": 1.3, "banking77": 1.3}, GC: {"massive": "garble", "clinc": "garble", "banking77": "copyQC"}},
    "C": {QR: {"massive": 1.3, "clinc": 1.3, "banking77": 1.3}, GR: {"massive": 1.0, "clinc": 1.0, "banking77": 1.0},
          QC: {"massive": "copyQR", "clinc": "copyQR", "banking77": "copyQR"}, GC: {"massive": "copyQC", "clinc": "garble", "banking77": 0.25},
          NR: {"massive": 1.0, "clinc": 1.0, "banking77": 1.0}, NC: {"massive": 1.0, "clinc": 1.0, "banking77": 1.0}},
}
FX_EXPECT = {"A": ("REOPEN-CANDIDATE", {"massive": "BETTER", "clinc": "NEITHER", "banking77": "BETTER"}, "HELD"),
             "B": ("KEEP-STRONG", {"massive": "WORSE", "clinc": "WORSE", "banking77": "NEITHER"}, "HURTS"),
             "C": ("KEEP", {"massive": "NEITHER", "clinc": "WORSE", "banking77": "BETTER"}, "NOT SHOWN")}
FX_B = 200


def _rng(*parts):
    return np.random.default_rng(int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12], 16))


def _vec(e, mode, f, t, tag):
    v = np.zeros(NAT[e])
    r = _rng(tag, e, t)
    if mode == "garble" or f is None:
        v[:NF] = 2.0 * r.normal(size=NF)
    else:
        v[f] += 3.0
        v[16 + f % 4] += 1.0
        v[:NF] += mode * r.normal(size=NF)
    v[NF:] += 0.01 * r.normal(size=NAT[e] - NF)
    return v


def _write_emb(path, meta, V, texts):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(meta.items()))
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(V[t], dtype=">f4").tobytes()) for t in texts])
    con.commit()
    con.close()


def build_fixture(td, name):
    """S0's synthetic rows; planted RAW and CARD DBs per FX_SPEC with their metas; S0's and the CARD pins files; a programme with the
    heading on its own line; a selection.json (d_q* 1024, d_g* 768); a DS1 outcome; the identity target from the independent oracle."""
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
    var_of = {t: CS["massive"].text[i] for i, t, _c in derived["variants"]}
    pair_of = {t: (CS[c].text[i], CS[c].text[j]) for c, ps in derived["pairs"].items() for i, j, t in ps}
    ingest_sha = II.file_sha(db)
    with contextlib.redirect_stdout(io.StringIO()):
        psha = W.load_prompts()
    V = {}
    order = [QR, QC, GR, GC] + ([NR, NC] if NR in spec else [])
    for a in order:
        e = a[0]
        V[a] = {}
        for t in texts:
            if t not in lab:                  # a pure variant / pair text: set below from its source(s)
                continue
            c, f = lab[t]
            mode = spec[a][c]
            if mode == "copyQC":
                v = np.zeros(NAT[e])
                v[:NAT[e]] = V[QC][t][:NAT[e]]
            elif mode == "copyQR":
                v = V[QR][t].copy()
            else:
                v = _vec(e, mode, f, t, "%s%s" % a)
            V[a][t] = v
        r = np.random.default_rng(99)
        for t, o in var_of.items():
            V[a][t] = V[a][o] + 0.02 * r.normal(size=NAT[e])
        for t, (x, y) in pair_of.items():
            V[a][t] = V[a][x] + V[a][y]
    for a in order:
        e, prot = a
        if prot == "RAW":
            meta = dict(ITS.expected_meta(e, set_sha, len(texts), ingest_sha), model_digest="stub")
        else:
            meta = dict(W.expected_meta_card(e, set_sha, len(texts), ingest_sha, psha), model_digest="stub")
        _write_emb(emb_file(a, td), meta, V[a], texts)
    if NR not in spec:                     # S0's nomic RAW file exists in every S0 fixture (pinned); its CARD file does not
        _write_emb(ITS.emb_path("nomic", td), dict(ITS.expected_meta("nomic", set_sha, len(texts), ingest_sha), model_digest="stub"),
                   {t: _vec("nomic", 1.0, lab.get(t, (None, None))[1], t, "nr") for t in texts}, texts)
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": II.file_sha(db),
                   "emb": {e: II.file_sha(ITS.emb_path(e, td)) for e in ("qwen3", "gemma", "nomic")}}, fh)
    cpins = os.path.join(td, "cpins.json")
    with open(cpins, "w") as fh:
        json.dump({"schema": PINS_SCHEMA, "qwen3_card": II.file_sha(W.card_path("qwen3", td)), "gemma_card": II.file_sha(W.card_path("gemma", td)),
                   "nomic_card": II.file_sha(W.card_path("nomic", td)) if NC in spec else None}, fh)
    prog = os.path.join(td, "programme.md")
    with open(prog, "w", encoding="utf-8") as fh:
        fh.write("intro\n%s fixture\n" % REG_HEADING)
    sel = os.path.join(td, "selection.json")
    with open(sel, "wb") as fh:
        fh.write(json.dumps({"d_q*": 1024, "d_g*": 768}).encode("utf-8"))
    dsl = os.path.join(td, "ds_outcome.txt")
    with open(dsl, "w", encoding="utf-8") as fh:
        fh.write("x\nDS1 VERDICT: REOPEN-CANDIDATE -- gemma BETTER on 2 of 3 [UNCONTROLLED]\n")
    fx = {"td": td, "db": db, "pins": pins, "cpins": cpins, "prog": prog, "sel": sel, "sel_sha": II.file_sha(sel), "dsl": dsl, "name": name,
          "texts": texts, "nomic": NC in spec}
    fx["oracle"] = _oracle(fx)
    o = fx["oracle"]
    fx["identity"] = {"mean": {e: {c: "%.5f" % o[c]["m"][a] for c in CORPORA} for e, a in (("qwen3", QR), ("gemma", GR))},
                      "spread": {e: {c: "%.5f" % o[c]["spread"][a] for c in CORPORA} for e, a in (("qwen3", QR), ("gemma", GR))},
                      "D": {c: "%+.5f" % o[c]["raw"]["D"] for c in CORPORA},
                      "ci": {c: ("%+.5f" % o[c]["raw"]["lo"], "%+.5f" % o[c]["raw"]["hi"]) for c in CORPORA}}
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


def _basic(D, draws):
    q = np.percentile(np.asarray(draws, dtype=float), [2.5, 97.5])
    return 2 * D - q[1], 2 * D - q[0]


def _oracle(fx, B=FX_B):
    """INDEPENDENT recomputation: own sqlite read, own slice + renormalise, own side masks, sklearn NMI for points, own weighted NMI and
    own component resampling (numpy Generator.integers, the documented CK-CLOSE rule); own variant stability, own supervised-centroid
    ceiling, own co-filing floor (c4's documented sampling rule). Only S0's skmeans is shared."""
    from sklearn.metrics import normalized_mutual_info_score as NMI
    with ITS.fixture_scope():
        K = dict(II.GOLD_K)
        CS = ITS.load_corpora(fx["db"])
        derived = ITS.text_set(CS)[2]
    arms = list(DECIDING) + ([NR, NC] if fx["nomic"] else [])
    raw = {}
    for a in arms:
        con = sqlite3.connect(emb_file(a, fx["td"]))
        raw[a] = {t: np.frombuffer(b, dtype=">f4").astype(np.float64)[:slice_of(a)] for t, b in con.execute("SELECT query, vector FROM embeddings")}
        con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    out = {}
    jd = []
    for ci, c in enumerate(CORPORA):
        C = CS[c]
        msk = lambda sd: [i for i in range(len(C.text)) if C.kept[i] and not C.oos[i] and C.side[i] == sd]
        tr, ev = msk(SS.TRAIN), msk(SS.EVAL)
        truth = list(C.fine[ev])
        preds, nm, fits = {}, {}, {}
        for a in arms:
            Xtr = U(np.array([raw[a][C.text[i]] for i in tr]))
            Xe = U(np.array([raw[a][C.text[i]] for i in ev]))
            fits[a] = [ITS.skmeans(Xtr, K[c][1], s) for s in SEEDS]
            preds[a] = [np.argmax(Xe @ Cm.T, 1) for Cm in fits[a]]
            nm[a] = [NMI(truth, p, average_method="arithmetic") for p in preds[a]]
        m = {a: float(np.mean(nm[a])) for a in arms}
        sp = {a: max(nm[a]) - min(nm[a]) for a in arms}
        stems = [C.stem[i] for i in ev]
        ustem = sorted(set(stems))
        gidx = np.array([ustem.index(s) for s in stems])
        msz = np.bincount(gidx).astype(float)
        rng = np.random.default_rng(BOOT_SEED + 10 * ci + LEVELS[c].index("fine"))
        dr = {a: [] for a in arms}
        for _ in range(B):
            w = np.bincount(rng.integers(len(ustem), size=len(ustem)), minlength=len(ustem))[gidx].astype(float)
            for a in arms:
                dr[a].append(np.mean([_wnmi(truth, p, w) for p in preds[a]]))
        dr = {a: np.array(v) for a, v in dr.items()}

        def con_(p_, q_):
            D = m[p_] - m[q_]
            dd = dr[p_] - dr[q_]
            lo, hi = _basic(D, dd)
            return {"D": D, "lo": lo, "hi": hi, "se": float(np.std(dd, ddof=1))}
        r1 = con_(GC, QC)
        bar = max(2.8 * r1["se"], sp[QC], sp[GC])
        st = "BETTER" if (r1["D"] > bar and r1["lo"] > 0) else ("WORSE" if (r1["D"] < -bar and r1["hi"] < 0) else "NEITHER")
        jd.append(dr[QC] - dr[QR])
        out[c] = {"m": m, "spread": sp, "cp1": dict(r1, bar=bar, status=st), "raw": con_(GR, QR), "g4": con_(GC, GR),
                  "n4": con_(NC, NR) if fx["nomic"] else None, "n": len(ev), "comps": len(ustem),
                  "kish": float((msz ** 2).sum() / msz.sum()), "q2": m[QC] - m[QR], "s2": max(sp[QC], sp[QR])}
        if c == "massive":
            var = derived["variants"]
            oi = [i for i, _t, _c in var]
            S3 = {}
            for a in DECIDING:
                Xo = U(np.array([raw[a][C.text[i]] for i in oi]))
                Xv = U(np.array([raw[a][t] for _i, t, _c in var]))
                same = [(np.argmax(Xo @ Cm.T, 1) == np.argmax(Xv @ Cm.T, 1)).astype(float) for Cm in fits[a]]
                Xt = U(np.array([raw[a][C.text[i]] for i in tr]))
                ytr = np.array([C.fine[i] for i in tr])
                labs = sorted(set(ytr))
                G = U(np.array([Xt[ytr == l].mean(0) for l in labs]))
                labs = np.array(labs)
                ceil = float(np.mean(labs[np.argmax(Xo @ G.T, 1)] == labs[np.argmax(Xv @ G.T, 1)]))
                Xe = U(np.array([raw[a][C.text[i]] for i in ev]))
                cell = dict(zip(ev, np.argmax(Xe @ fits[a][0].T, 1).tolist()))
                by = {}
                for i in ev:
                    by.setdefault(C.fine[i], []).append(int(i))
                ls = sorted(l for l, v in by.items() if len(v) > 1)
                rg = np.random.default_rng(ITS.SEED_COFILE)
                co, tries = [], 0
                while ls and len(co) < len(var) and tries < 100 * len(var):
                    tries += 1
                    Lx = by[ls[int(rg.integers(len(ls)))]]
                    x, y = Lx[int(rg.integers(len(Lx)))], Lx[int(rg.integers(len(Lx)))]
                    if x != y and C.comp[x] != C.comp[y]:
                        co.append(cell[x] == cell[y])
                Sm = float(np.mean([s.mean() for s in same]))
                fl = float(np.mean(co))
                S3[a] = {"S": Sm, "ceiling": ceil, "floor": fl, "R": (Sm - fl) / (ceil - fl), "same": same}
            vst = [C.stem[i] for i in oi]
            uv = sorted(set(vst))
            vg = np.array([uv.index(s) for s in vst])
            rng3 = np.random.default_rng(BOOT_SEED + 4)
            d3 = []
            for _ in range(B):
                w = np.bincount(rng3.integers(len(uv), size=len(uv)), minlength=len(uv))[vg].astype(float)
                d3.append(np.mean([(w * s).sum() / w.sum() for s in S3[GC]["same"]]) - np.mean([(w * s).sum() / w.sum() for s in S3[QC]["same"]]))
            D3 = S3[GC]["S"] - S3[QC]["S"]
            out["cp3"] = {"rows": S3, "D": D3, "lo": float(np.percentile(d3, 2.5)), "hi": float(np.percentile(d3, 97.5))}
    st = {c: out[c]["cp1"]["status"] for c in CORPORA}
    nb, nw = sum(v == "BETTER" for v in st.values()), sum(v == "WORSE" for v in st.values())
    out["verdict"] = "REOPEN-CANDIDATE" if nb >= 2 else ("KEEP-STRONG" if nw >= 2 else "KEEP")
    Db = float(np.mean([out[c]["q2"] for c in CORPORA]))
    J = np.mean(jd, axis=0)
    se = float(np.std(J, ddof=1))
    lo, hi = _basic(Db, J)
    bar = max(2.8 * se, float(np.mean([out[c]["s2"] for c in CORPORA])))
    out["cp2"] = {"D": Db, "se": se, "lo": lo, "hi": hi, "bar": bar,
                  "status": "HELD" if (Db > bar and lo > 0) else ("HURTS" if (Db < -bar and hi < 0) else "NOT SHOWN")}
    return out


@contextlib.contextmanager
def _scope(fx):
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], PINS_OVERRIDE[0], ITS.DATA_ROOT)
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        PINS_OVERRIDE[0] = fx["cpins"] if fx else None
        ITS.DATA_ROOT = fx["td"] if fx else tempfile.gettempdir()
        try:
            yield
        finally:
            g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], PINS_OVERRIDE[0], ITS.DATA_ROOT = saved


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
    out_dir = os.path.join(tempfile.mkdtemp(prefix="out_%s_" % tag, dir=fx["td"]), "o")      # unique: never a prior run's directory
    args = dict(db=fx["db"], emb_dir=fx["td"], out_dir=out_dir, programme=fx["prog"], identity=fx["identity"], sel_path=fx["sel"],
                sel_sha=fx["sel_sha"], B=FX_B, dimslice=fx["dsl"])
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
        td = tempfile.mkdtemp(prefix="cp_st_")
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


def _syn(st, D=None, cp2s="HELD", Db=0.03, ds="REOPEN-CANDIDATE", nomic=True):
    """A synthetic R for the printers (every branch executed)."""
    R = {"cp1": {}, "m": {}, "B": 200, "arms": list(DECIDING) + ([NR, NC] if nomic else []), "dimslice": ds}
    for c in CORPORA:
        d = 0.001 if D is None else D[c]
        R["cp1"][c] = {"D": d, "lo": d - 0.004, "hi": d + 0.004, "plo": d - 0.004, "phi": d + 0.004, "se": 0.002, "mde80": 0.0056,
                       "spread": {QC: 0.01, GC: 0.012}, "bar": 0.012, "status": st[c], "n": 100, "components": 99, "kish": 1.01, "n_eff": 99.0}
        R["m"][c] = {a: 0.8 for a in R["arms"]}
    R["verdict"] = verdict(st)
    R["cp2"] = {"D": Db, "se": 0.002, "mde80": 0.0056, "spread_term": 0.016, "bar": 0.016, "lo": Db - 0.005, "hi": Db + 0.005, "plo": 0, "phi": 0,
                "status": cp2s, "per": {c: Db for c in CORPORA}}
    R["cp3"] = {"rows": {a: {"S": 0.8, "per_seed": [0.8] * 5, "ceiling": 0.9, "floor": 0.5, "floor_n": 10, "R": 0.75} for a in DECIDING},
                "D": 0.04, "lo": 0.01, "hi": 0.07, "blo": 0.01, "bhi": 0.07, "se": 0.01, "n": 10, "components": 10, "kish": 1.0}
    R["cp4"] = {"gemma": {c: {"D": 0.0, "lo": -0.01, "hi": 0.01} for c in CORPORA},
                "nomic": {c: {"D": 0.0, "lo": -0.01, "hi": 0.01} for c in CORPORA} if nomic else None}
    return R


def _selftest(sel, ok, FX):
    if sel("P-CONST"):
        ok(check_its_blob() == ITS_BLOB, "P-CONST intent_transfer_s0.py is blob f662ceb (imported unchanged)")
        ok(DSTAR == {"qwen3": 1024, "gemma": 768} and SEEDS == (0, 1, 2, 3, 4) and BOOT_B == 2000 and MDE_K == 2.8 and NOMIC_D == 256,
           "P-CONST d_q* 1024, d_g* 768, seeds 0-4, B 2,000, MDE80 = 2.8 SE, nomic @256")
        ok(IDENTITY["mean"]["qwen3"] == {"massive": "0.76554", "clinc": "0.92810", "banking77": "0.84900"}
           and IDENTITY["mean"]["gemma"] == {"massive": "0.79883", "clinc": "0.92566", "banking77": "0.89286"}
           and IDENTITY["spread"]["qwen3"] == {"massive": "0.01428", "clinc": "0.00417", "banking77": "0.01043"}
           and IDENTITY["spread"]["gemma"] == {"massive": "0.01277", "clinc": "0.00968", "banking77": "0.01216"},
           "P-CONST identity means / spreads = EMBED-DIM-SLICE's nmi_matrix.csv at qwen3@1024 / gemma@768")
        ok(IDENTITY["D"] == {"massive": "+0.03329", "clinc": "-0.00244", "banking77": "+0.04386"}
           and IDENTITY["ci"] == {"massive": ("+0.02961", "+0.03998"), "clinc": ("-0.00560", "-0.00048"), "banking77": ("+0.04108", "+0.04990")},
           "P-CONST identity DS1 D* and BASIC CI = EMBED-DIM-SLICE's outcome.txt")
        mat = os.path.join(ROOT, "experiment_results", "embed_dim_slice", "nmi_matrix.csv")
        if os.path.isfile(mat):
            rows = list(csv.DictReader(open(mat, encoding="utf-8")))
            for e in EMB:
                for c in CORPORA:
                    x = [float(r["nmi"]) for r in rows if r["embedder"] == e and r["slice"] == str(DSTAR[e]) and r["corpus"] == c
                         and r["side"] == "EVAL" and r["level"] == "fine"]
                    ok(len(x) == 5 and "%.5f" % np.mean(x) == IDENTITY["mean"][e][c] and "%.5f" % (max(x) - min(x)) == IDENTITY["spread"][e][c],
                       "P-CONST nmi_matrix.csv %s@%d %s: mean %.5f spread %.5f = the identity constants" % (e, DSTAR[e], c, np.mean(x), max(x) - min(x)))
        if os.path.isfile(DIMSLICE_OUTCOME):
            txt = open(DIMSLICE_OUTCOME, encoding="utf-8").read()
            for c in CORPORA:
                ok(("DS1 %s K_f %d n" % (c, {"massive": 60, "clinc": 150, "banking77": 77}[c])) in txt and
                   ("D* = %s, 95%% BASIC CI [%s, %s]" % (IDENTITY["D"][c], IDENTITY["ci"][c][0], IDENTITY["ci"][c][1])) in txt,
                   "P-CONST outcome.txt DS1 %s D* %s CI [%s, %s] present verbatim" % (c, IDENTITY["D"][c], IDENTITY["ci"][c][0], IDENTITY["ci"][c][1]))
            o, err, v = _cap(lambda: dimslice_verdict(DIMSLICE_OUTCOME))
            ok(err is None and v == "REOPEN-CANDIDATE", "P-CONST EMBED-DIM-SLICE's DS1 VERDICT of record reads REOPEN-CANDIDATE")
        ok(SEL_SHA.startswith("f1b508cf"), "P-CONST selection.json sha f1b508cf")
        if os.path.isfile(SEL_PATH):
            o, err, r = _cap(lambda: read_selection(SEL_PATH, SEL_SHA))
            ok(err is None and "d_q* = 1024, d_g* = 768" in o, "P-CONST the committed selection.json reads PIN OK, d_q* 1024, d_g* 768")
        ok(P_CP1 == {"massive": (0.010, -0.010, 0.030), "clinc": (-0.025, -0.040, -0.010), "banking77": (0.035, 0.015, 0.055)}
           and dict(P_CP1_V) == {"KEEP": 0.75, "KEEP-STRONG": 0.10, "REOPEN-CANDIDATE": 0.25} and P_CP2 == (0.020, 0.000, 0.040)
           and dict(P_CP2_V) == {"HELD": 0.45, "HURTS": 0.05} and P_CP3 == (0.04, 0.01, 0.07), "P-CONST predictions as registered")
        ok(PLAN_SE == {"massive": 0.00289, "clinc": 0.00137, "banking77": 0.00247} and (PLAN_SE2, PLAN_BAR2) == (0.00135, 0.0161), "P-CONST planning SE / bars")
        ok(OUT_DIR.replace("\\", "/").endswith("experiment_results/card_protocol") and OUTCOME == "outcome.txt", "P-CONST the registered outcome path")
        pj = json.load(open(PINS_FILE, encoding="utf-8"))
        ok(pj.get("schema") == PINS_SCHEMA and all(k in pj for k in ("qwen3_card", "gemma_card", "nomic_card")), "P-CONST the committed pins file has the three keys")
        if os.path.isfile(PROGRAMME):
            ok(REG_RE.search(open(PROGRAMME, encoding="utf-8").read()) is not None,
               "P-CONST the programme carries the registration heading on its own line")
    if sel("P-UNIT"):
        cs = ITS.c1_status
        ok(cs(0.02, 0.001, 0.03, 0.01) == "BETTER" and cs(0.02, -0.001, 0.03, 0.01) == "NEITHER" and cs(0.01, 0.001, 0.03, 0.01) == "NEITHER"
           and cs(-0.02, -0.03, -0.001, 0.01) == "WORSE" and cs(-0.02, -0.03, 0.0, 0.01) == "NEITHER", "P-UNIT S0's C1 rule: point AND interval each way")
        B_, Wo, N_ = "BETTER", "WORSE", "NEITHER"
        cases = [((B_, B_, B_), "REOPEN-CANDIDATE"), ((B_, N_, B_), "REOPEN-CANDIDATE"), ((B_, B_, Wo), "REOPEN-CANDIDATE"),
                 ((B_, N_, N_), "KEEP"), ((N_, N_, N_), "KEEP"), ((B_, Wo, N_), "KEEP"), ((N_, N_, B_), "KEEP"),
                 ((Wo, Wo, N_), "KEEP-STRONG"), ((B_, Wo, Wo), "KEEP-STRONG"), ((Wo, Wo, Wo), "KEEP-STRONG"), ((N_, Wo, Wo), "KEEP-STRONG")]
        for sts, want in cases:
            ok(verdict(dict(zip(CORPORA, sts)))[0] == want, "P-UNIT CP1 verdict %s -> %s" % ("/".join(sts), want))

        def per_(dq, sp_q, sp_r, se_noise):
            per = {}
            for k, c in enumerate(CORPORA):
                rng = np.random.default_rng(k)
                d0 = rng.normal(size=400) * se_noise
                per[c] = {"m": {QC: 0.8 + dq[k], QR: 0.8, GC: 0.8, GR: 0.8},          # gemma flat: CP2 must read qwen3
                          "nm": {QC: [0.8, 0.8 + sp_q], QR: [0.8, 0.8 + sp_r], GC: [0.8, 0.8], GR: [0.8, 0.8]},
                          "draws": {QC: 0.8 + dq[k] + d0, QR: np.full(400, 0.8), GC: np.full(400, 0.8) + d0, GR: np.full(400, 0.8)}}
            return per
        r = cp2(per_((0.03, 0.03, 0.03), 0.01, 0.02, 0.002))
        ok(r["status"] == "HELD" and abs(r["spread_term"] - 0.02) < 1e-12 and abs(r["D"] - 0.03) < 1e-12, "P-UNIT CP2 HELD; spread term = mean of max(CARD, RAW) spreads")
        r = cp2(per_((-0.03, -0.03, -0.03), 0.01, 0.02, 0.002))
        ok(r["status"] == "HURTS", "P-UNIT CP2 HURTS (symmetric)")
        r = cp2(per_((0.015, 0.015, 0.015), 0.01, 0.02, 0.002))
        ok(r["status"] == "NOT SHOWN" and r["D"] < r["bar"] and r["lo"] > 0, "P-UNIT CP2 NOT SHOWN: interval > 0 but D-bar inside the spread term")
        sk = np.full(1000, 0.85)
        sk[:26] += 0.11                                  # a right-skewed bootstrap: SD small, q97.5 far out
        per = {c: {"m": {QC: 0.85, QR: 0.8}, "nm": {QC: [0.8, 0.801], QR: [0.8, 0.801]}, "draws": {QC: sk.copy(), QR: np.full(1000, 0.8)}} for c in CORPORA}
        r = cp2(per)
        ok(r["status"] == "NOT SHOWN" and r["D"] > r["bar"] and r["lo"] < 0,
           "P-UNIT CP2 NOT SHOWN: D-bar %.4f beyond bar_pool %.4f but the BASIC lower bound %.4f < 0 (the interval clause decides)" % (r["D"], r["bar"], r["lo"]))
        per = {c: {"m": {QC: 0.75, QR: 0.8}, "nm": {QC: [0.8, 0.801], QR: [0.8, 0.801]}, "draws": {QC: 1.6 - sk, QR: np.full(1000, 0.8)}} for c in CORPORA}
        r = cp2(per)
        ok(r["status"] == "NOT SHOWN" and r["D"] < -r["bar"] and r["hi"] > 0, "P-UNIT CP2 NOT SHOWN: D-bar below -bar_pool but the BASIC upper bound > 0")
        r = cp2(per_((0.06, 0.0, 0.0), 0.005, 0.005, 0.002))
        ok(abs(r["D"] - 0.02) < 1e-12 and r["status"] == "HELD", "P-UNIT CP2 pools all three corpora (one corpus +0.06 -> D-bar +0.02, HELD)")
        r = cp2(per_((0.0, 0.0, 0.06), 0.005, 0.005, 0.002))
        ok(abs(r["D"] - 0.02) < 1e-12, "P-UNIT CP2 pools the LAST corpus too")
        r = cp2(per_((0.02, 0.02, 0.02), 0.001, 0.001, 0.01))
        jd = np.mean([np.random.default_rng(k).normal(size=400) * 0.01 for k in range(3)], axis=0)
        ok(abs(r["se"] - float(np.std(jd, ddof=1))) < 1e-12 and r["bar"] == max(2.8 * r["se"], 0.001),
           "P-UNIT CP2 SE = SD of the per-draw corpus mean (joint draws), bar_pool = max(2.8 SE, spread term)")
        rng = np.random.default_rng(5)
        dq = 0.80 + 0.0075 * rng.standard_normal(4000)
        mm = {QC: 0.80, GC: 0.825}
        r = cp1(mm, {QC: [0.80, 0.801], GC: [0.825, 0.826]}, {QC: dq, GC: 0.825 + 0.0075 * rng.standard_normal(4000)}, 100, np.arange(100))
        ok(r["status"] == "NEITHER" and r["lo"] > 0 and r["spread"][GC] < r["D"] < r["mde80"] == r["bar"],
           "P-UNIT CP1 bar = MDE80 when MDE80 > the spreads: D %.4f, lower %.4f > 0, but D < MDE80 %.4f -> NEITHER" % (r["D"], r["lo"], r["mde80"]))
        r = cp1(mm, {QC: [0.80, 0.80], GC: [0.825, 0.865]}, {QC: dq, GC: dq + 0.025}, 100, np.arange(100))
        ok(abs(r["bar"] - 0.04) < 1e-12 and r["status"] == "NEITHER", "P-UNIT CP1 bar = the larger in-run spread (gemma CARD 0.040) when it exceeds MDE80")
        ok(scoreable(0.035, 0.0143, 0.0069) == (0.035 - 0.0143, "SCOREABLE") and scoreable(0.010, 0.0246, 0.0081)[1] == "DESCRIPTIVE-ONLY"
           and scoreable(-0.025, 0.0094, 0.0038)[1] == "SCOREABLE", "P-UNIT Support (f) words at the registered planning values (B77 / MASSIVE / CLINC)")
        E, Wd = "BETTER", "WORSE"
        R = _syn({"massive": E, "clinc": "NEITHER", "banking77": E}, D={"massive": 0.03, "clinc": 0.0, "banking77": 0.04})
        L = criteria_lines(R)
        ok("CP1 VERDICT: REOPEN-CANDIDATE -- gemma BETTER on 2 of 3 ['massive', 'banking77'] (>= 2); WORSE on 0 of 3 []" in L
           and any(x.startswith("F-CP1: FIRED (CP1 reads REOPEN-CANDIDATE): it overturns") and x.endswith("E1 remains") for x in L),
           "P-UNIT lines REOPEN-CANDIDATE: verdict and F-CP1 FIRED sentence")
        ok(any(x.startswith("READING AGAINST D3 (registered): REOPEN-CANDIDATE on both") for x in L), "P-UNIT lines REOPEN on both -> the registered 'evidence ... complete except E1' reading")
        ok("CP2 VERDICT: HELD (card raises qwen3)" in L and "F-CP2: NOT FIRED (CP2 reads HELD)" in L, "P-UNIT lines CP2 HELD, F-CP2 NOT FIRED")
        R = _syn({"massive": Wd, "clinc": Wd, "banking77": "NEITHER"}, cp2s="HURTS", Db=-0.03)
        L = criteria_lines(R)
        ok("CP1 VERDICT: KEEP-STRONG (a sub-case of KEEP) -- gemma BETTER on 0 of 3 [] (<= 1); gemma WORSE on 2 of 3 ['massive', 'clinc'] (>= 2)" in L
           and "F-CP1: NOT FIRED (CP1 reads KEEP-STRONG, not REOPEN-CANDIDATE)" in L and any(x.startswith("READING (KEEP-STRONG)") for x in L)
           and any(x.startswith("READING (KEEP):") and "never \"explained by protocol\"" in x for x in L), "P-UNIT lines KEEP-STRONG with both readings")
        ok("CP2 VERDICT: HURTS" in L and any(x.startswith("F-CP2: FIRED (CP2 reads HURTS)") for x in L)
           and "F-CP2 (HURTS): in addition, RAW is the better protocol for qwen3 on intent clustering" in L, "P-UNIT lines CP2 HURTS: F-CP2 FIRED + the HURTS sentence")
        ok(any(x.startswith("READING AGAINST D3 (registered): Mixed (EMBED-DIM-SLICE REOPEN-CANDIDATE, CP1 KEEP-STRONG)") for x in L), "P-UNIT lines mixed reading against D3")
        R = _syn({"massive": "NEITHER", "clinc": Wd, "banking77": E}, cp2s="NOT SHOWN", Db=0.0, ds="KEEP")
        L = criteria_lines(R)
        ok("CP1 VERDICT: KEEP -- gemma BETTER on 1 of 3 ['banking77'] (<= 1); gemma WORSE on 1 of 3 ['clinc']" in L
           and not any(x.startswith("READING (KEEP-STRONG)") for x in L), "P-UNIT lines KEEP (1 BETTER, 1 WORSE), no KEEP-STRONG reading")
        ok(any(x.startswith("READING caveat: MASSIVE reads NEITHER") for x in L), "P-UNIT lines the MASSIVE NEITHER caveat")
        ok(any(x.startswith("READING AGAINST D3 (registered): KEEP on both") for x in L), "P-UNIT lines KEEP on both -> D3 stands")
        ok("CP2 VERDICT: NOT SHOWN" in L and any(x.startswith("F-CP2: FIRED (CP2 reads NOT SHOWN)") for x in L)
           and not any(x.startswith("F-CP2 (HURTS)") for x in L), "P-UNIT lines CP2 NOT SHOWN: F-CP2 FIRED without the HURTS sentence")
        Ld = descriptive_lines(_syn({"massive": E, "clinc": E, "banking77": E}, nomic=False))
        ok(any(x.startswith("  CP4 nomic: NOT READ") for x in Ld), "P-UNIT CP4 nomic unpinned -> the NOT READ line")
        Ld = descriptive_lines(_syn({"massive": E, "clinc": E, "banking77": E}))
        ok(sum(1 for x in Ld if x.startswith("  CP4 ") and " nomic @256: RAW " in x) == 3, "P-UNIT CP4 nomic pinned -> three rows")
        P = predictions_lines(_syn({"massive": E, "clinc": "NEITHER", "banking77": E}, D={"massive": 0.030, "clinc": -0.010, "banking77": 0.0151}, Db=0.0401))
        ok("  CP1-P massive D_card +0.03000 vs +0.010 [-0.010, +0.030]: HELD" in P and "  CP1-P clinc D_card -0.01000 vs -0.025 [-0.040, -0.010]: HELD" in P
           and "  CP1-P banking77 D_card +0.01510 vs +0.035 [+0.015, +0.055]: HELD" in P, "P-UNIT CP1-P closed intervals (boundaries HELD)")
        ok("  CP1-P REOPEN-CANDIDATE (p 0.25): OCCURRED, Brier 0.5625" in P and "  CP1-P KEEP (p 0.75): did not occur, Brier 0.5625" in P
           and "  CP1-P KEEP-STRONG (p 0.10): did not occur, Brier 0.0100" in P, "P-UNIT CP1-P Briers on REOPEN")
        ok("  CP2-P D-bar +0.04010 vs +0.020 [+0.000, +0.040]: FAILED" in P and "  CP2-P HELD (p 0.45): OCCURRED, Brier 0.3025" in P
           and "  CP2-P HURTS (p 0.05): did not occur, Brier 0.0025" in P, "P-UNIT CP2-P interval and Briers")
        P = predictions_lines(_syn({"massive": Wd, "clinc": Wd, "banking77": E}))
        ok("  CP1-P KEEP (p 0.75): OCCURRED, Brier 0.0625" in P and "  CP1-P KEEP-STRONG (p 0.10): OCCURRED, Brier 0.8100" in P,
           "P-UNIT CP1-P KEEP-STRONG inside the KEEP event (CB8)")
        ok("  CP3-P gemma S - qwen3 S under CARD +0.04000 vs +0.040 [+0.010, +0.070]: HELD" in P, "P-UNIT CP3-P scored")
        S = support_lines(_syn({"massive": E, "clinc": E, "banking77": E}))
        ok(S[1].endswith("-> DESCRIPTIVE-ONLY") and S[3].endswith("-> SCOREABLE") and S[2].endswith("-> SCOREABLE"),
           "P-UNIT support words per corpus at the predictions (MASSIVE 0.010 vs bar 0.012 DESCRIPTIVE-ONLY; CLINC, B77 SCOREABLE)")
    if sel("P-E2E"):
        for name in FX_SPEC:
            fx = FX[name]
            orc = fx["oracle"]
            want_v, want_st, want_2 = FX_EXPECT[name]
            ok(orc["verdict"] == want_v and all(orc[c]["cp1"]["status"] == want_st[c] for c in CORPORA) and orc["cp2"]["status"] == want_2,
               "P-E2E %s: the oracle reads the planted %s / %s / CP2 %s" % (name, want_v, want_st, want_2))
            o, err, R, od = _run(fx, "e2e")
            ok(err is None, "P-E2E %s: --run completes (%s)" % (name, err))
            ok(_line(o, "CP1 VERDICT: ").startswith("CP1 VERDICT: %s " % want_v), "P-E2E %s: printed CP1 verdict %s" % (name, want_v))
            for c in CORPORA:
                r = orc[c]["cp1"]
                ln = _line(o, "  CP1 %s K_f" % c)
                ok(("D_card = gemma %.5f - qwen3 %.5f = %+.5f" % (orc[c]["m"][GC], orc[c]["m"][QC], r["D"])) in ln,
                   "P-E2E %s %s: D_card %+.5f = the oracle's (gemma CARD - qwen3 CARD)" % (name, c, r["D"]))
                ok(("95%% BASIC CI [%+.5f, %+.5f]" % (r["lo"], r["hi"])) in ln and ("SE %.5f, MDE80 %.5f" % (r["se"], 2.8 * r["se"])) in ln,
                   "P-E2E %s %s: BASIC CI and SE / MDE80 = the oracle's (own bootstrap, own weighted NMI)" % (name, c))
                ok(("spread max(qwen3 CARD %.5f, gemma CARD %.5f), bar %.5f" % (orc[c]["spread"][QC], orc[c]["spread"][GC], r["bar"])) in ln,
                   "P-E2E %s %s: in-run CARD spreads and bar %.5f = the oracle's" % (name, c, r["bar"]))
                ok(ln.endswith("-> " + want_st[c]), "P-E2E %s %s: printed status %s" % (name, c, want_st[c]))
                sp = _line(o, "  CP1 %s: n " % c)
                ok(("n %d EVAL items in %d components, Kish DEFF %.4f" % (orc[c]["n"], orc[c]["comps"], orc[c]["kish"])) in sp
                   and sp.endswith("-> " + scoreable(P_CP1[c][0], r["bar"], 2.8 * r["se"])[1]),
                   "P-E2E %s %s: support n / components / Kish and the (f) word from the run" % (name, c))
                g = orc[c]["g4"]
                ok(("CP4 %s gemma CARD - RAW @768: %+.5f, 95%% BASIC CI [%+.5f, %+.5f]" % (c, g["D"], g["lo"], g["hi"])) in o,
                   "P-E2E %s %s: CP4 gemma CARD - RAW = the oracle's" % (name, c))
                if fx["nomic"]:
                    x = orc[c]["n4"]
                    ok(("CARD - RAW %+.5f, 95%% BASIC CI [%+.5f, %+.5f]" % (x["D"], x["lo"], x["hi"])) in _line(o, "  CP4 %s nomic @256" % c),
                       "P-E2E %s %s: CP4 nomic CARD - RAW = the oracle's" % (name, c))
            ok(("CP4 nomic: NOT READ" in o) == (not fx["nomic"]), "P-E2E %s: CP4 nomic %s" % (name, "read" if fx["nomic"] else "NOT READ (unpinned)"))
            r2 = orc["cp2"]
            ln = _line(o, "  CP2 D-bar")
            ok(("D-bar %+.5f, 95%% BASIC CI [%+.5f, %+.5f]" % (r2["D"], r2["lo"], r2["hi"])) in ln and ("bar_pool %.5f -> %s" % (r2["bar"], want_2)) in ln
               and ("SE %.5f" % r2["se"]) in ln, "P-E2E %s: CP2 D-bar %+.5f, joint CI, SE, bar_pool = the oracle's -> %s" % (name, r2["D"], want_2))
            ok(("CP2 VERDICT: %s" % want_2) in o and (("F-CP2: FIRED" in o) == (want_2 != "HELD")), "P-E2E %s: CP2 verdict and F-CP2" % name)
            ok(_line(o, "F-CP1:").startswith("F-CP1: FIRED") == (want_v == "REOPEN-CANDIDATE"), "P-E2E %s: F-CP1 %s" % (name, "FIRED" if want_v == "REOPEN-CANDIDATE" else "NOT FIRED"))
            c3 = orc["cp3"]
            ok(("S(gemma CARD) - S(qwen3 CARD) = %+.5f, 95%% percentile CI [%+.5f, %+.5f]" % (c3["D"], c3["lo"], c3["hi"])) in o,
               "P-E2E %s: CP3 D_S %+.5f and its percentile CI = the oracle's" % (name, c3["D"]))
            for a in (QC, GC):
                x = c3["rows"][a]
                ok(("S %.5f" % x["S"]) in _line(o, "  CP3 %s %s@" % a) and ("ceiling %.5f; random co-filing floor %.5f" % (x["ceiling"], x["floor"])) in _line(o, "  CP3 %s %s@" % a)
                   and ("R %.4f" % x["R"]) in _line(o, "  CP3 %s %s@" % a), "P-E2E %s: CP3 %s %s S, ceiling, floor, R = the oracle's" % ((name,) + a))
            txt = open(os.path.join(od, OUTCOME), encoding="utf-8").read()
            ok(_line(o, "CP1 VERDICT: ") in txt and "-> REPRODUCED" in txt and DOES_NOT_SHOW in txt and READINGS in txt and ("CP2 VERDICT: %s" % want_2) in txt,
               "P-E2E %s: outcome.txt carries the verdicts, the identity, the readings and DOES NOT SHOW" % name)
            n_arms = 6 if fx["nomic"] else 4
            ok(("EVAL read %d times" % (3 * n_arms)) in txt and "0 with an EVAL row" in txt, "P-E2E %s: EVAL read %d times; no fit with an EVAL row" % (name, 3 * n_arms))
            rows = list(csv.reader(open(os.path.join(od, CSVS[0]), encoding="utf-8")))
            ok(len(rows) == 1 + n_arms * 3 * 5, "P-E2E %s: nmi_card.csv %d rows" % (name, n_arms * 15))
            x = [float(r[7]) for r in rows[1:] if r[0] == "gemma" and r[1] == "CARD" and r[3] == "banking77"]
            ok(len(x) == 5 and abs(np.mean(x) - orc["banking77"]["m"][GC]) < 1e-6, "P-E2E %s: nmi_card.csv gemma CARD banking77 = the oracle's mean" % name)
            try:
                o2, err2, _r, _od = _run(fx, "again", out_dir=od)
            except FileExistsError:
                err2 = None
            ok(err2 and "write-once" in err2, "P-E2E %s: a second --run into the same directory REFUSES (write-once)" % name)
        fx = FX["A"]
        p_un = os.path.join(tempfile.mkdtemp(prefix="cpins_", dir=fx["td"]), "cp.json")
        json.dump(dict(json.load(open(fx["cpins"])), nomic_card=None), open(p_un, "w"))
        saved = fx["cpins"]
        fx["cpins"] = p_un
        try:
            o, err, R, od = _run(fx, "nomic_unpinned")
        finally:
            fx["cpins"] = saved
        ok(err is None and "CP4 nomic: NOT READ" in o and all(a[0] != "nomic" for a in R["arms"]),
           "P-E2E A with intent_emb_nomic_card.db PRESENT but unpinned: the nomic arm is not read (CP4 NOT READ), the run completes")
        o, err, R, od = _run(fx, "pairs")
        ok(R["cp2"]["D"] > 0 and FX["B"]["oracle"]["cp2"]["D"] < 0 and FX["C"]["oracle"]["cp2"]["D"] == 0.0, "P-E2E CP2 sign: A positive, B negative, C exactly 0 (CARD = RAW bytes)")
        ok(any(x.startswith("IDENTITY: RAW qwen3@1024") and x.endswith("-> REPRODUCED") for x in R["lines"]), "P-E2E the identity line of record ends REPRODUCED")
    if sel("P-REFUSE"):
        fx = FX["C"]

        def nowrite(od):
            return not any(os.path.exists(p) for p in out_paths(od))
        for key, path in (("mean", ("mean", "gemma", "banking77")), ("spread", ("spread", "qwen3", "clinc"))):
            bad = json.loads(json.dumps(fx["identity"]))
            bad[path[0]][path[1]][path[2]] = "0.00000"
            o, err, _r, od = _run(fx, "id" + key, identity=bad)
            ok(err and ("IDENTITY PRECONDITION FAILED on ['%s %s %s']" % path) in err and nowrite(od),
               "P-REFUSE identity %s of %s %s off: refused, nothing written" % path)
        bad = json.loads(json.dumps(fx["identity"]))
        bad["D"]["banking77"] = "+0.99999"
        o, err, _r, od = _run(fx, "idD", identity=bad)
        ok(err and "['D banking77']" in err and nowrite(od), "P-REFUSE identity D* on the LAST corpus off: refused")
        bad = json.loads(json.dumps(fx["identity"]))
        bad["ci"]["clinc"] = [bad["ci"]["clinc"][0], "+0.99999"]
        o, err, _r, od = _run(fx, "idci", identity=bad)
        ok(err and "['CI clinc']" in err and nowrite(od), "P-REFUSE identity CI upper bound off: refused (the bootstrap stream is checked)")
        o, err, _r, od = _run(fx, "selsha", sel_sha="0" * 64)
        ok(err and "selection.json sha256" in err and nowrite(od), "P-REFUSE selection.json sha mismatch: refused")
        for dq, dg in ((512, 768), (1024, 256)):
            sel2 = os.path.join(fx["td"], "sel_%d_%d.json" % (dq, dg))
            with open(sel2, "wb") as fh:
                fh.write(json.dumps({"d_q*": dq, "d_g*": dg}).encode("utf-8"))
            o, err, _r, od = _run(fx, "sel%d%d" % (dq, dg), sel_path=sel2, sel_sha=II.file_sha(sel2))
            ok(err and "selection.json d*" in err and nowrite(od), "P-REFUSE selection with d_q* %d / d_g* %d: refused" % (dq, dg))
        prog = os.path.join(fx["td"], "quoted.md")
        open(prog, "w", encoding="utf-8").write("## Registrar's record x\nquoting \"%s ...\" in a sentence\n" % REG_HEADING)
        o, err, _r, od = _run(fx, "quoted", programme=prog)
        ok(err and "not registered" in err and nowrite(od), "P-REFUSE the heading only QUOTED inside a line: refused (line-anchored)")
        def with_cpins(obj, tag):
            p = os.path.join(fx["td"], "cp_%s.json" % tag)
            json.dump(obj, open(p, "w"))
            saved = fx["cpins"]
            fx["cpins"] = p
            try:
                return _run(fx, tag)
            finally:
                fx["cpins"] = saved
        base = json.load(open(fx["cpins"]))
        o, err, _r, od = with_cpins(dict(base, gemma_card=None), "gnull")
        ok(err and "UNPINNED" in err and "intent_emb_gemma_card.db" in err and nowrite(od), "P-REFUSE gemma CARD pin null: --run refused")
        o, err, _r, od = with_cpins(dict(base, qwen3_card="1" * 64), "qbad")
        ok(err and "intent_emb_qwen3_card.db" in err and "pinned" in err, "P-REFUSE qwen3 CARD pin different: refused")
        o, err, _r, od = with_cpins(dict(base, schema="x"), "schema")
        ok(err and "schema" in err, "P-REFUSE a pins file of another schema: refused")
        o, err, _r, od = with_cpins(dict(base, nomic_card="2" * 64), "nbad")
        ok(err and "intent_emb_nomic_card.db" in err, "P-REFUSE a nomic pin set while the file is absent / different: refused (pinned -> read strictly)")
        g = globals()
        real = g["_foreign_heavy"]
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ['"java.exe","1"']
            o, err, _r = _cap(lambda: main_run(db=fx["db"], emb_dir=fx["td"], out_dir=os.path.join(tempfile.mkdtemp(prefix="heavy_", dir=fx["td"]), "o"), programme=fx["prog"],
                                               identity=fx["identity"], sel_path=fx["sel"], sel_sha=fx["sel_sha"], B=FX_B, dimslice=fx["dsl"]))
        g["_foreign_heavy"] = real
        ok(err and "heavy" in err, "P-REFUSE a java.exe running: refused")
        real_cp3 = g["cp3"]
        pq = W.card_path("qwen3", fx["td"])
        saved_bytes = open(pq, "rb").read()

        def tamper(*a):
            with open(pq, "ab") as fh:
                fh.write(b"\0")
            return real_cp3(*a)
        g["cp3"] = tamper
        try:
            o, err, _r, od = _run(fx, "tamper")
        finally:
            g["cp3"] = real_cp3
            open(pq, "wb").write(saved_bytes)
        ok(err and "qwen3_card sha256 changed during the readout" in err and nowrite(od), "P-REFUSE a CARD file changes mid-readout: refused, nothing written")
        od_r = os.path.join(tempfile.mkdtemp(prefix="race_", dir=fx["td"]), "o")

        def racer(*a):
            os.makedirs(od_r, exist_ok=True)
            with open(os.path.join(od_r, OUTCOME), "w", encoding="utf-8") as fh:
                fh.write("PRIOR")
            return real_cp3(*a)
        g["cp3"] = racer
        raced = None
        try:
            _run(fx, "race", out_dir=od_r)
        except FileExistsError as ex:
            raced = ex
        finally:
            g["cp3"] = real_cp3
        ok(raced is not None and open(os.path.join(od_r, OUTCOME), encoding="utf-8").read() == "PRIOR", "P-REFUSE an outcome.txt that appears mid-run is never overwritten (mode x)")
        pg = W.card_path("gemma", fx["td"])
        orig = open(pg, "rb").read()
        con = sqlite3.connect(pg)
        t0 = con.execute("SELECT query FROM embeddings LIMIT 1").fetchone()[0]
        con.execute("DELETE FROM embeddings WHERE query = ?", (t0,))
        con.commit()
        con.close()
        try:
            o, err, _r, od = with_cpins(dict(base, gemma_card=II.file_sha(pg)), "partial")
            with _scope(fx):
                o3, err3, _r3 = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=fx["identity"], sel_path=fx["sel"],
                                                     sel_sha=fx["sel_sha"], timing=False, B=FX_B, dimslice=fx["dsl"]))
        finally:
            open(pg, "wb").write(orig)
        ok(err and "1 texts of the registered set have no vector" in err and nowrite(od), "P-REFUSE a partial gemma CARD file: --run refused")
        ok(err3 is None and ("%d of %d texts present (1 missing): --run REFUSES" % (len(fx["texts"]) - 1, len(fx["texts"]))) in o3,
           "P-REFUSE the dry-run reports the partial CARD file (1 missing)")
        ok(II.file_sha(pg) == base["gemma_card"], "P-REFUSE fixture gemma CARD file restored")
        for key, val in (("prompt", "task: clustering | query:"), ("protocol", "RAW"), ("writer_blob_lf", "x"), ("prompts_file_sha256", "0" * 64)):
            con = sqlite3.connect(pg)
            con.execute("UPDATE intent_meta SET value = ? WHERE key = ?", (val, key))
            con.commit()
            con.close()
            try:
                o, err, _r, od = with_cpins(dict(base, gemma_card=II.file_sha(pg)), "meta_" + key)
            finally:
                open(pg, "wb").write(orig)
            ok(err and "intent_meta mismatch" in err and key in err and nowrite(od), "P-REFUSE a gemma CARD file whose meta %s differs: refused" % key)
        ok(II.file_sha(pg) == base["gemma_card"], "P-REFUSE fixture gemma CARD file restored after the meta tests")
        dsl2 = os.path.join(fx["td"], "ds_none.txt")
        open(dsl2, "w").write("no verdict here\n")
        o, err, _r, od = _run(fx, "nods", dimslice=dsl2)
        ok(err and "DS1 VERDICT" in err and nowrite(od), "P-REFUSE an EMBED-DIM-SLICE outcome without a DS1 VERDICT line: refused")
    if sel("P-DRY"):
        fx = FX["A"]
        before = sorted(os.listdir(fx["td"]))
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=fx["identity"], sel_path=fx["sel"],
                                              sel_sha=fx["sel_sha"], timing=True, B=FX_B, dimslice=fx["dsl"]))
        ok(err is None and ("DS1 D* %s" % " / ".join(fx["identity"]["D"][c] for c in CORPORA)) in _line(o, "IDENTITY")
           and "DRY RUN complete" in o, "P-DRY completes; the RAW identity printed = the oracle's (D* and CI)")
        ok(all(("%d of %d texts present (0 missing)" % (len(fx["texts"]), len(fx["texts"]))) in _line(o, "CARD file %s" % W.card_path(e, fx["td"])) for e in W.EMB)
           and "TIMING" in o, "P-DRY three CARD files complete (0 missing) and a timed fit")
        ok(sorted(os.listdir(fx["td"])) == before, "P-DRY writes nothing (directory unchanged)")
        ok(sum(1 for e in EVENTS if e[0] == "EVAL") == 6 and all(" RAW " in e[1] for e in EVENTS), "P-DRY reads EVAL of the two RAW arms only (6 reads; CB7)")
        bad = json.loads(json.dumps(fx["identity"]))
        bad["mean"]["qwen3"]["massive"] = "0.00001"
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], identity=bad, sel_path=fx["sel"],
                                              sel_sha=fx["sel_sha"], timing=False, B=FX_B, dimslice=fx["dsl"]))
        ok(err and "IDENTITY PRECONDITION FAILED on ['mean qwen3 massive']" in err, "P-DRY identity mismatch refuses in the dry-run too")
        tdn = os.path.join(fx["td"], "nocard")
        os.makedirs(tdn, exist_ok=True)
        for f in (II.DB_NAME, "intent_emb_qwen3.db", "intent_emb_gemma.db", "intent_emb_nomic.db"):
            if not os.path.exists(os.path.join(tdn, f)):
                shutil.copyfile(os.path.join(fx["td"], f), os.path.join(tdn, f))
        with _scope(fx):
            ITS.DATA_ROOT = tdn
            o, err, _r = _cap(lambda: dry_run(db=os.path.join(tdn, II.DB_NAME), emb_dir=tdn, programme=fx["prog"], identity=fx["identity"],
                                              sel_path=fx["sel"], sel_sha=fx["sel_sha"], timing=False, B=FX_B, dimslice=fx["dsl"]))
        ok(err is None and o.count("absent: run tools/analysis/card_protocol_writer.py --embed --embedder") == 3 and "IDENTITY" in o,
           "P-DRY with no CARD file: prints the three absences and still checks the RAW identity (before any Ollama pass)")
    if sel("P-LOAD"):
        fx = FX["A"]
        with _scope(fx):
            CS = ITS.load_corpora(fx["db"])
            texts = ITS.text_set(CS)[0]
            with contextlib.redirect_stdout(io.StringIO()):
                v = {a: load_slice(emb_file(a, fx["td"]), a, texts) for a in (QC, GC, NC)}
        for a, d in ((QC, 1024), (GC, 768), (NC, 256)):
            con = sqlite3.connect(emb_file(a, fx["td"]))
            t, b = con.execute("SELECT query, vector FROM embeddings LIMIT 1").fetchone()
            con.close()
            ok(len(v[a][t]) == d and np.array_equal(v[a][t], np.frombuffer(b, dtype=">f4")[:d].astype(np.float32)),
               "P-LOAD %s %s read = the first %d raw coordinates of its own file" % (a[0], a[1], d))
        ok(ITS.SLICE2 == 512, "P-LOAD S0's SLICE2 restored to 512")


MUTANTS = (
    ("CP1 sign flipped (qwen3 - gemma)", "    r = contrast(m, draws, GC, QC)\n", "    r = contrast(m, draws, QC, GC)\n", ("P-E2E",)),
    ("CP1 on the RAW arms", "    r = contrast(m, draws, GC, QC)\n", "    r = contrast(m, draws, GR, QR)\n", ("P-E2E",)),
    ("CP1 bar from the RAW spreads", "    r[\"spread\"] = {QC: spread(nm[QC]), GC: spread(nm[GC])}\n", "    r[\"spread\"] = {QC: spread(nm[QR]), GC: spread(nm[GR])}\n", ("P-E2E",)),
    ("CP1 bar = min of the spreads", "    r[\"bar\"] = max(r[\"mde80\"], max(r[\"spread\"][QC], r[\"spread\"][GC]))\n",
     "    r[\"bar\"] = max(r[\"mde80\"], min(r[\"spread\"][QC], r[\"spread\"][GC]))\n", ("P-E2E",)),
    ("CP1 bar without MDE80", "    r[\"bar\"] = max(r[\"mde80\"], max(r[\"spread\"][QC], r[\"spread\"][GC]))\n", "    r[\"bar\"] = max(r[\"spread\"][QC], r[\"spread\"][GC])\n", ("P-UNIT", "P-E2E")),
    ("MDE80 = 1.96 SE", "MDE_K = 2.8\n", "MDE_K = 1.96\n", ("P-CONST", "P-E2E")),
    ("SE with ddof 0", "    se = float(np.std(dd, ddof=1))\n", "    se = float(np.std(dd))\n", ("P-E2E",)),
    ("CI percentile instead of BASIC", "    lo, hi = ITS.basic_ci(D, dd)\n", "    lo, hi = ITS.pct_ci(dd)\n", ("P-E2E",)),
    ("bootstrap unweighted", "            out[a].append(float(np.mean([ITS.nmi(truth, p, w) for p in preds[a]])))\n",
     "            out[a].append(float(np.mean([ITS.nmi(truth, p) for p in preds[a]])))\n", ("P-E2E",)),
    ("bootstrap over items, not components", "        draws = boot(c, truth, comp, {a: out[a][\"preds\"] for a in arms}, B)\n",
     "        draws = boot(c, truth, np.arange(len(truth)), {a: out[a][\"preds\"] for a in arms}, B)\n", ("P-E2E",)),
    ("bootstrap stream of the coarse level", "    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index(\"fine\"))\n",
     "    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c))\n", ("P-E2E",)),
    ("unpaired bootstrap (fresh weights per arm)", "    for w in ITS.comp_weights(comp, B, rng):\n        for a in preds:\n            out[a].append(",
     "    for w in ITS.comp_weights(comp, B, rng):\n        for a in preds:\n            w = next(ITS.comp_weights(comp, 1, rng))\n            out[a].append(", ("P-E2E",)),
    ("c1 status: BETTER without the interval", "    r[\"status\"] = ITS.c1_status(r[\"D\"], r[\"lo\"], r[\"hi\"], r[\"bar\"])\n",
     "    r[\"status\"] = ITS.c1_status(r[\"D\"], -1.0, 1.0, r[\"bar\"]) if r[\"D\"] < 0 else (\"BETTER\" if r[\"D\"] > r[\"bar\"] else \"NEITHER\")\n", ("P-E2E",)),
    ("REOPEN on >= 1", "    if nb >= 2:\n        return \"REOPEN-CANDIDATE\"", "    if nb >= 1:\n        return \"REOPEN-CANDIDATE\"", ("P-UNIT", "P-E2E")),
    ("REOPEN on 3 of 3", "    if nb >= 2:\n        return \"REOPEN-CANDIDATE\"", "    if nb >= 3:\n        return \"REOPEN-CANDIDATE\"", ("P-UNIT", "P-E2E")),
    ("KEEP-STRONG on >= 1", "    if nw >= 2:\n        return \"KEEP-STRONG\"", "    if nw >= 1:\n        return \"KEEP-STRONG\"", ("P-UNIT", "P-E2E")),
    ("KEEP-STRONG checked first", [("    if nb >= 2:\n        return \"REOPEN-CANDIDATE\", nb, nw\n    if nw >= 2:\n        return \"KEEP-STRONG\", nb, nw\n",
                                    "    if nw >= 1:\n        return \"KEEP-STRONG\", nb, nw\n    if nb >= 2:\n        return \"REOPEN-CANDIDATE\", nb, nw\n")], None, ("P-UNIT",)),
    ("verdict counts the first two corpora", "    nb = sum(1 for c in CORPORA if status[c] == \"BETTER\")\n", "    nb = sum(1 for c in CORPORA[:2] if status[c] == \"BETTER\")\n", ("P-UNIT",)),
    ("CP2 on gemma", "    D = float(np.mean([per[c][\"m\"][QC] - per[c][\"m\"][QR] for c in CORPORA]))\n    jd = np.mean([per[c][\"draws\"][QC] - per[c][\"draws\"][QR]",
     "    D = float(np.mean([per[c][\"m\"][GC] - per[c][\"m\"][GR] for c in CORPORA]))\n    jd = np.mean([per[c][\"draws\"][GC] - per[c][\"draws\"][GR]", ("P-UNIT", "P-E2E")),
    ("CP2 point on the first corpus only", "    D = float(np.mean([per[c][\"m\"][QC] - per[c][\"m\"][QR] for c in CORPORA]))\n",
     "    D = float(np.mean([per[c][\"m\"][QC] - per[c][\"m\"][QR] for c in CORPORA[:1]]))\n", ("P-UNIT", "P-E2E")),
    ("CP2 point sum, not mean", "    D = float(np.mean([per[c][\"m\"][QC] - per[c][\"m\"][QR] for c in CORPORA]))\n",
     "    D = float(np.sum([per[c][\"m\"][QC] - per[c][\"m\"][QR] for c in CORPORA]))\n", ("P-UNIT", "P-E2E")),
    ("CP2 joint draws: SE pooled as sqrt(sum se^2)/3 instead", "    se = float(np.std(jd, ddof=1))\n    lo, hi = ITS.basic_ci(D, jd)\n",
     "    se = float(np.sqrt(sum(np.var(per[c][\"draws\"][QC] - per[c][\"draws\"][QR], ddof=1) for c in CORPORA)) / 3 * 1.5)\n    lo, hi = ITS.basic_ci(D, jd)\n", ("P-UNIT", "P-E2E")),
    ("CP2 spread term = max over corpora", "    sterm = float(np.mean([max(spread(per[c][\"nm\"][QC]), spread(per[c][\"nm\"][QR])) for c in CORPORA]))\n",
     "    sterm = float(np.max([max(spread(per[c][\"nm\"][QC]), spread(per[c][\"nm\"][QR])) for c in CORPORA]))\n", ("P-UNIT", "P-E2E")),
    ("CP2 spread term from CARD only", "    sterm = float(np.mean([max(spread(per[c][\"nm\"][QC]), spread(per[c][\"nm\"][QR])) for c in CORPORA]))\n",
     "    sterm = float(np.mean([spread(per[c][\"nm\"][QC]) for c in CORPORA]))\n", ("P-UNIT",)),
    ("CP2 HELD without the interval", "    if D > bar and lo > 0:\n        st = \"HELD\"", "    if D > bar:\n        st = \"HELD\"", ("P-UNIT",)),
    ("CP2 HELD without the bar", "    if D > bar and lo > 0:\n        st = \"HELD\"", "    if lo > 0:\n        st = \"HELD\"", ("P-UNIT",)),
    ("CP2 HURTS without the interval", "    elif D < -bar and hi < 0:\n", "    elif D < -bar:\n", ("P-UNIT", "P-E2E")),
    ("CP2 HURTS never", "    elif D < -bar and hi < 0:\n", "    elif False:\n", ("P-UNIT", "P-E2E")),
    ("F-CP1 fires on KEEP-STRONG", "    if v == \"REOPEN-CANDIDATE\":\n        L.append(\"CP1 VERDICT: REOPEN", "    if v != \"KEEP\":\n        L.append(\"CP1 VERDICT: REOPEN", ("P-UNIT", "P-E2E")),
    ("F-CP2 not fired on NOT SHOWN", "    if r[\"status\"] == \"HELD\":\n        L.append(\"CP2 VERDICT: HELD", "    if r[\"status\"] != \"HURTS\":\n        L.append(\"CP2 VERDICT: HELD", ("P-UNIT", "P-E2E")),
    ("HURTS sentence never printed", "            L.append(\"F-CP2 (HURTS): in addition", "            (\"F-CP2 (HURTS): in addition", ("P-UNIT",)),
    ("KEEP-STRONG reading never printed", "            L.append(\"READING (KEEP-STRONG): in addition", "            (\"READING (KEEP-STRONG): in addition", ("P-UNIT",)),
    ("MASSIVE caveat never printed", "        L.append(\"READING caveat: MASSIVE", "        (\"READING caveat: MASSIVE", ("P-UNIT",)),
    ("D3 reading: mixed branch never printed", "        L.append(\"READING AGAINST D3 (registered): Mixed", "        (\"READING AGAINST D3 (registered): Mixed", ("P-UNIT",)),
    ("D3 reading: KEEP-on-both branch skipped", "    elif v != \"REOPEN-CANDIDATE\" and ds != \"REOPEN-CANDIDATE\":\n", "    elif False:\n", ("P-UNIT",)),
    ("CP4 nomic NOT READ line never printed", "        L.append(\"  CP4 nomic: NOT READ", "        (\"  CP4 nomic: NOT READ", ("P-UNIT", "P-E2E")),
    ("CP4 gemma on the qwen3 arms", "    R[\"cp4\"] = {\"gemma\": {c: contrast(R[\"m\"][c], R[\"per\"][c][\"draws\"], GC, GR)",
     "    R[\"cp4\"] = {\"gemma\": {c: contrast(R[\"m\"][c], R[\"per\"][c][\"draws\"], QC, QR)", ("P-E2E",)),
    ("CP3 D_S sign flipped", "    D = rows[GC][\"S\"] - rows[QC][\"S\"]\n", "    D = rows[QC][\"S\"] - rows[GC][\"S\"]\n", ("P-E2E",)),
    ("CP3 S at seed 0 only", "        S = float(np.mean([s.mean() for s in o[\"same\"]]))\n        den", "        S = float(o[\"same\"][0].mean())\n        den", ("P-E2E",)),
    ("CP3 R without the floor", "\"R\": (S - o[\"floor\"]) / den if den else", "\"R\": S / o[\"ceiling\"] if den else", ("P-E2E",)),
    ("CP3 interval stream of CP1", "    for w in ITS.comp_weights(comp, B, np.random.default_rng(BOOT_SEED + 4)):\n",
     "    for w in ITS.comp_weights(comp, B, np.random.default_rng(BOOT_SEED)):\n", ("P-E2E",)),
    ("identity checks the first corpus only (D)", "    bad += [\"D %s\" % c for c in CORPORA if", "    bad += [\"D %s\" % c for c in CORPORA[:1] if", ("P-REFUSE",)),
    ("identity ignores the CI", "    if with_ci:\n        bad += [\"CI", "    if False:\n        bad += [\"CI", ("P-REFUSE",)),
    ("identity ignores the spread", "    for k in (\"mean\", \"spread\"):\n", "    for k in (\"mean\",):\n", ("P-REFUSE",)),
    ("identity skipped", "    if bad:\n        refuse(\"IDENTITY", "    if False:\n        refuse(\"IDENTITY", ("P-REFUSE",)),
    ("identity from the CARD arms", "    for e, a in ((\"qwen3\", QR), (\"gemma\", GR)):\n        out[\"mean\"][e]", "    for e, a in ((\"qwen3\", QC), (\"gemma\", GC)):\n        out[\"mean\"][e]", ("P-E2E",)),
    ("selection sha not checked", "    if sha != want_sha:\n", "    if False:\n", ("P-REFUSE",)),
    ("selection d_g* not checked", "    got = {\"qwen3\": js.get(\"d_q*\"), \"gemma\": js.get(\"d_g*\")}\n", "    got = {\"qwen3\": js.get(\"d_q*\"), \"gemma\": 768}\n", ("P-REFUSE",)),
    ("registration matched anywhere (not line-anchored)", "REG_RE = re.compile(r\"^\" + re.escape(REG_HEADING), re.M)\n", "REG_RE = re.compile(re.escape(REG_HEADING))\n", ("P-REFUSE",)),
    ("registration not required", "    if not check_registered(programme):\n", "    if False:\n", ("P-REFUSE",)),
    ("CARD pins not strict at --run", "    sha0, CS, texts, derived, arms, psha = load_inputs(db, emb_dir, True)\n", "    sha0, CS, texts, derived, arms, psha = load_inputs(db, emb_dir, False)\n", ("P-REFUSE",)),
    ("CARD pin mismatch admitted", "    if want and want != s:\n        refuse(\"%s sha256 %s != the pinned", "    if False:\n        refuse(\"%s sha256 %s != the pinned", ("P-REFUSE",)),
    ("CARD meta not checked", "            ITS.check_meta(emb_file(a, emb_dir), W.expected_meta_card(", "            (emb_file(a, emb_dir), W.expected_meta_card(", ("P-REFUSE",)),
    ("partial CARD admitted at --run", "    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts) for a in arms}\n    del ITS.FIT_LOG[:]\n    R = evaluate",
     "    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts, allow_missing=True) for a in arms}\n    del ITS.FIT_LOG[:]\n    R = evaluate", ("P-REFUSE",)),
    ("after-check skipped", "        if now != s:\n            refuse(\"%s sha256 changed", "        if False:\n            refuse(\"%s sha256 changed", ("P-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("P-REFUSE",)),
    ("outcome not write-once", "    with open(os.path.join(out_dir, OUTCOME), \"x\"", "    with open(os.path.join(out_dir, OUTCOME), \"w\"", ("P-REFUSE",)),
    ("outcome paths not checked", "        if os.path.lexists(p):\n            refuse(\"%s exists", "        if False:\n            refuse(\"%s exists", ("P-E2E",)),
    ("qwen3 slice 512", "DSTAR = {\"qwen3\": 1024, \"gemma\": 768}\n", "DSTAR = {\"qwen3\": 512, \"gemma\": 768}\n", ("P-CONST", "P-LOAD")),
    ("gemma slice 256 in the Space", "    d = slice_of(arm)\n    S = ITS.Space(vecs, C, d)\n", "    d = 256 if arm[0] == \"gemma\" else slice_of(arm)\n    S = ITS.Space(vecs, C, d)\n", ("P-E2E",)),
    ("SLICE2 not restored", "        ITS.SLICE2 = saved\n    bad = sum(1 for x in v.values() if len(x) != d)\n", "        pass\n    bad = sum(1 for x in v.values() if len(x) != d)\n", ("P-LOAD",)),
    ("CARD read from the RAW file", "    return ITS.emb_path(e, emb_dir) if prot == \"RAW\" else W.card_path(e, emb_dir)\n", "    return ITS.emb_path(e, emb_dir)\n", ("P-E2E", "P-REFUSE")),
    ("EVAL replaced by GATE (wrong split side)", "    ev = ITS.S_idx(C, S, SS.EVAL)\n    EVENTS.append", "    ev = ITS.S_idx(C, S, SS.GATE)\n    EVENTS.append", ("P-E2E",)),
    ("Kish over items", "    r.update({\"n\": int(n), \"components\": int(len(np.unique(comp))), \"kish\": ITS.kish(comp)})\n",
     "    r.update({\"n\": int(n), \"components\": int(len(np.unique(comp))), \"kish\": 1.0})\n", ("P-E2E",)),
    ("support word on the planning bar", "        beyond, word = scoreable(P_CP1[c][0], r[\"bar\"], r[\"mde80\"])\n", "        beyond, word = scoreable(P_CP1[c][0], PLAN_BAR[c], r[\"mde80\"])\n", ("P-UNIT", "P-E2E")),
    ("CP1-P open interval", "    return \"HELD\" if (np.isfinite(v) and lo <= v <= hi) else \"FAILED\"\n", "    return \"HELD\" if (np.isfinite(v) and lo < v < hi) else \"FAILED\"\n", ("P-UNIT",)),
    ("KEEP event excludes KEEP-STRONG", "    ev = {\"KEEP\": v in (\"KEEP\", \"KEEP-STRONG\"),", "    ev = {\"KEEP\": v == \"KEEP\",", ("P-UNIT",)),
    ("Brier on the complement", "    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2\n", "    return (float(p) - (0.0 if bool(event) else 1.0)) ** 2\n", ("P-UNIT",)),
    ("dry-run reads the CARD files as RAW", "    vecs = {a: load_slice(emb_file(a, emb_dir), a, texts) for a in raw}\n",
     "    vecs = {a: load_slice(emb_file((a[0], \"CARD\"), emb_dir), a, texts) for a in raw}\n", ("P-DRY",)),
    ("dry-run identity skipped", "    identity_check(identity_values(per), identity, with_ci=True)\n", "    identity_values(per)\n", ("P-DRY",)),
    ("nomic read even when unpinned", "    nomic = bool(pins.get(\"nomic_card\")) if strict else", "    nomic = os.path.exists(emb_file(NC, emb_dir)) if strict else", ("P-E2E",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="cp_mut_")
    fx = make_fixtures(td)

    def snap():
        return {os.path.join(k, f): II.file_sha(os.path.join(v["td"], f)) for k, v in fx.items() for f in sorted(os.listdir(v["td"]))
                if os.path.isfile(os.path.join(v["td"], f))}
    base = snap()
    killed, n = 0, 0
    for name, old, new, tests in MUTANTS:
        pairs = old if isinstance(old, list) else [(old, new)]
        code = head
        for o_, n_ in pairs:
            if code.count(o_) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, code.count(o_)))
            code = code.replace(o_, n_)
        n += 1
        ns = {"__name__": "cp_mutant", "__file__": os.path.abspath(__file__)}
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
        now = snap()
        changed = sorted(k for k in base if now.get(k) != base[k])      # files the selftest adds (pins / selection variants) are not checked
        if changed:                              # a mutant left a fixture file changed: report it, rebuild, never reuse it
            print("  FIXTURE CHANGED after %r: %s" % (name, changed))
            td2 = tempfile.mkdtemp(prefix="cp_mut_")
            fx = make_fixtures(td2)
            base = snap()
        killed += res.startswith("KILLED")
        print("  %-48s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS (readout): %d of %d KILLED" % (killed, n))
    return 0 if killed == n else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTENT-S0-CARD-PROTOCOL readout (zero calls)")
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
