"""GOLD-LEVEL-EMB: on the pinned S0 embeddings, is the GOLD COARSE-level k-means readout invariant (within 0.025 NMI) across the arm
contrasts already examined, slice (qwen3 256 / 512 / 4096 vs 1024), quantisation (Q8_0 vs Q4_K_M), prompt (CARD vs RAW, qwen3 and gemma)
and embedder (gemma 768, nomic vs qwen3 1024), on MASSIVE and CLINC, while the fine level is not (descriptive)?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-02 (before any code or call) — GOLD-LEVEL-EMB: on the pinned S0
embeddings, is the GOLD COARSE-level k-means readout invariant ...", span L23377-L23422 _as_of d635fec5 (the registrar's commit
1a922a80, parent 487ac3bd; plan Amendment 37). Record docs/agents/results/GOLD-LEVEL-EMB.json. --run REFUSES unless a LINE of the
programme starts with that heading (REG_RE, line-anchored). Kind: zero-call CPU reader: zero judge calls, zero embeddings, no build, no
Ollama, no pool of record (pool_guard not engaged), no embeddings_cache*.db.

INSTRUMENT (imported UNCHANGED, each LF blob asserted at every entry point; another blob REFUSES):
  intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271: pin_check / raw_pin_check, load_corpora, text_set, check_meta /
      expected_meta, load_vectors (with SLICE2 set to the read width for the call, restored), Space (first d coordinates, L2-renormalised),
      km_fit (spherical k-means, k-means++, n_init 1, max_iter 300; TRAIN through fit_rows), S_idx, assign, codes, nmi, comp_weights,
      basic_ci, kish, c1_status, d2 (H and its random p95), fit_audit.
  embed_dim_slice.py blob:068550b4f7a5a918b9bd1f3e9c2ae4e4a86a9b44: load_full (qwen3 4096 / gemma 768 reads), pick (the GATE selection
      rule: smallest d within TIE 0.001 of the max), h_boot (H's TRAIN-component bootstrap, seed SEED_H + corpus index).
  embed_quant.py blob:3930cf4bc5e77bebd38309c74cf4ecf8eeba74d0: status (the registered TOST form: EQUIVALENT iff the 90% interval lies in
      the OPEN interval (-margin, +margin); DIFFERENT iff |D| > margin AND the 95% interval excludes 0), q8_pin_check, load_slice (the Q8
      file at 1024 under the in-memory tag registration), read_selection, and its writer's expected_meta_q8.
  card_protocol.py blob:cdcc1dbb4ece15b150988f43913e757432e90e77: load_card_pins, card_pin_check, load_slice (the CARD files at d*),
      read_selection (EMBED-DIM-SLICE's selection.json, sha256 of the LF rendering f1b508cf..., d_q* 1024 / d_g* 768), and its writer's
      load_prompts / expected_meta_card.

ARMS (9; first d coordinates, L2-renormalised): q256, q512, q1024, q4096 (qwen3 Q4_K_M, S0's file), q8 (qwen3 Q8_0 at 1024), qcard
(qwen3 CARD at 1024), g768 (gemma RAW), gcard (gemma CARD at 768), n* (nomic RAW at d_n* in {256, 512, 768}, EMBED-DIM-SLICE's rule
verbatim: GATE fine NMI, seeds 0-4, mean over the 3 corpora, ties within 0.001 to the smaller d; nomic_selection.json written mode "x"
and hashed BEFORE any nomic EVAL row is read, at any slice: eval_idx refuses otherwise). LEVELS: coarse on MASSIVE (K_c 18) and CLINC
(K_c 10), seeds 0-29; fine on MASSIVE (60), CLINC (150), Banking77 (77), seeds 0-4. k-means fitted on TRAIN, EVAL (kept in-scope rows;
CLINC OOS excluded) filed to the nearest centroid. Sources are loaded one at a time (q4 at 4096, q8 at 1024, qcard at 1024, g at 768,
gcard at 768, nomic at 768), every arm of a source read from that one load.

CRITERIA (registered; criteria_lines prints every branch, each executed by the selftest):
  GL1 (DECIDING; coarse), per contrast A - B and coarse corpus: D = mean_{s 0..29} NMI_EVAL(A, s) - mean_{s 0..29} NMI_EVAL(B, s) at K_c;
      SE_total = sqrt(SE_boot^2 + var_seed / 30); SE_boot = SD (ddof 1) of D over B 2,000 paired component-bootstrap draws (partitions
      fixed; one weight vector per draw for every arm; S0's C1 coarse stream BOOT_SEED + 10 x corpus index + 0); var_seed = sample
      variance (ddof 1) over s of NMI(A, s) - NMI(B, s). EQUIVALENT iff D -/+ 1.645 SE_total inside (-0.025, +0.025); DIFFERENT iff
      |D| > 0.025 AND D -/+ 1.96 SE_total excludes 0 (direction printed); NEITHER otherwise.
      CONTRASTS: DIM q256 / q512 / q4096 - q1024; QUANT q8 - q1024; PROMPT qcard - q1024, gcard - g768; EMBEDDER g768 - q1024, n* - q1024.
      FAMILY (intersection-union, over BOTH coarse corpora): INVARIANT iff every status EQUIVALENT; NOT-INVARIANT iff at least one
      DIFFERENT; UNDETERMINED otherwise. READING (first that applies): LEVEL (all four INVARIANT); TRANSFORMATION (DIM and QUANT INVARIANT,
      EMBEDDER NOT-INVARIANT); NO-LEVEL-ADVANTAGE (DIM NOT-INVARIANT); MIXED. F-GL fires iff any family NOT-INVARIANT; F-GL' iff EMBEDDER
      INVARIANT.
  GL2 (DESCRIPTIVE-ONLY) the same on fine NMI at K_f, three corpora, seeds 0-4 (var_seed / 5), S0's C1 fine stream; never a criterion.
  GL3 (DESCRIPTIVE-ONLY) H per arm on MASSIVE and CLINC (ITS.d2) with EDS.h_boot's interval and the random p95; Delta H per contrast.
  PRINTED BESIDE: S0's C1 status on seeds 0-4 (BETTER / WORSE / NEITHER against max(MDE80, in-run seed spread)); each arm's 5- and
      30-seed spreads; GL1 at a margin of 0.05 (sensitivity, never deciding).
  IDENTITY PRECONDITION (refuse; nothing but nomic_selection.json written): seeds 0-4 coarse and fine EVAL NMI of q256, q512, q1024,
      q4096, g768 reproduce nmi_matrix.csv (blob 1056bad9 asserted on --run); q8 fine reproduces nmi_q.csv; qcard / gcard fine reproduce
      nmi_card.csv (its RAW rows too); nomic at 256 / 512 coarse and fine reproduce s0_c1.csv; H, lo, hi, p95 and dropped labels of the
      EMBED-DIM-SLICE arms reproduce h_table.csv. Checked per source, right after the source is read (fail fast).

BUILDER'S READINGS (printed in the outcome; the registrar confirms or brackets):
  GB1 "to 5 dp" read as |value - CSV| <= 5e-6 (the CSVs print 6 dp; a 5-dp string compare would double-round); the max deviation printed.
  GB2 nomic's GATE selection precedes EVERY nomic EVAL read (not only at d_n*): the identity's nomic 256 / 512 EVAL reads come after
      nomic_selection.json, so whichever slice wins, no nomic EVAL row was read before the file.
  GB3 the n* arm at d_n* = 256 or 512 IS the identity's nomic arm at that slice (its seeds 0-4 checked against s0_c1.csv).
  GB4 every contrast on a corpus and level shares ONE weight stream (S0's C1 stream for that corpus and level), so the draws are paired
      across arms AND across contrasts; the S0 C1 status beside is read from the same draws restricted to seeds 0-4 (BASIC interval).
  GB5 verdict lines re-stated at the measured SE_total against the registered P1 points: SCOREABLE (EQUIVALENT side) iff |P| <= 0.025 -
      2.487 SE_total; SCOREABLE (DIFFERENT side) iff |P| >= 0.025 + 0.842 SE_total; DESCRIPTIVE-ONLY otherwise.
  GB6 numeric predictions HELD iff the point lies in the closed 80% interval; SEEN points scored and printed "SEEN: never a
      confirmation"; one Brier per probability (event 1 / 0).
  GB7 P4's "fine DIM family statuses all EQUIVALENT" = the 9 fine DIM statuses (3 contrasts x 3 corpora); P5's "at every qwen3 slice"
      = q256, q512, q1024, q4096.

HYGIENE: reads only the pinned files (sha256-bytes before and after; a change REFUSES and nothing is written): ingest 487e0093...,
intent_emb_qwen3.db 9e100e04..., intent_emb_nomic.db 4aafd6c7..., intent_emb_gemma.db b187b82f... (intent_transfer_s0_pins.json),
intent_emb_qwen3_q8.db 771666bc... (embed_quant_pins.json), intent_emb_qwen3_card.db e8dd85af... and intent_emb_gemma_card.db
9396cb1b... (card_protocol_pins.json), selection.json f1b508cf...; mode=ro&immutable=1 through S0's readers (non-empty -wal / -journal
REFUSES). Threads OMP / OPENBLAS / MKL = 1 before numpy. --dry-run and --run REFUSE while a java.exe runs.

OUTPUT (experiment_results/gold_level_emb/, every file write-once, mode "x"; an existing path REFUSES before any read):
nomic_selection.json (between nomic's GATE phase and any nomic EVAL read), outcome.txt (of record), nmi_gold.csv, h_gold.csv.

LAUNCH (run-operator; zero calls; nothing heavy running; CPU lane):
  python tools/analysis/gold_level_emb.py --selftest
  python tools/analysis/gold_level_emb.py --mutants
  python tools/analysis/gold_level_emb.py --dry-run                # pins, selection, census / denominators, timed fits + bootstrap, price
  python tools/analysis/gold_level_emb.py --dry-run --identity     # + the identity on the non-nomic arms (values of record only; minutes)
  python tools/analysis/gold_level_emb.py --run                    # nomic_selection.json, then the file of record (write-once)
  (DBs under TAXOARENA_DATA_ROOT, default the repo root; --db / --emb-dir / --out-dir override.)

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
import io              # noqa: E402
import json            # noqa: E402
import re              # noqa: E402
import shutil          # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile; import scratch_dir        # noqa: E402
import time            # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import intent_transfer_s0 as ITS      # noqa: E402  (imported unchanged; blob asserted)
import embed_dim_slice as EDS         # noqa: E402  (imported unchanged; blob asserted)
import embed_quant as EQ              # noqa: E402  (imported unchanged; blob asserted)
import card_protocol as CP            # noqa: E402  (imported unchanged; blob asserted)
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402
II = ITS.II
QW = EQ.W                              # embed_quant_writer (Q8 meta, tag registration)
CW = CP.W                              # card_protocol_writer (CARD meta, prompts)

TAG = "[GOLD-LEVEL-EMB]"
BLOBS = {"intent_transfer_s0": ("f662ceb19738f515972871f5963f5dcfc764a271", ITS), "embed_dim_slice": ("068550b4f7a5a918b9bd1f3e9c2ae4e4a86a9b44", EDS),
         "embed_quant": ("3930cf4bc5e77bebd38309c74cf4ecf8eeba74d0", EQ), "card_protocol": ("cdcc1dbb4ece15b150988f43913e757432e90e77", CP)}
ARMS = ("q256", "q512", "q1024", "q4096", "q8", "qcard", "g768", "gcard", "n*")
ARM_SRC = {"q256": ("q4", 256), "q512": ("q4", 512), "q1024": ("q4", 1024), "q4096": ("q4", 4096), "q8": ("q8", 1024), "qcard": ("qcard", 1024),
           "g768": ("g", 768), "gcard": ("gcard", 768), "n*": ("n", None)}
SOURCES = ("q4", "q8", "qcard", "g", "gcard", "n")
EDS_ARMS = ("q256", "q512", "q1024", "q4096", "g768")
NOMIC_SLICES = (256, 512, 768)
NOMIC_ID_SLICES = (256, 512)
CORPORA = ITS.CORPORA
LEVELS = ITS.LEVELS
COARSE_C = ("massive", "clinc")
SEEDS_C = tuple(range(30))
SEEDS_F = ITS.SEEDS
BOOT_B = ITS.BOOT_B
BOOT_SEED = ITS.BOOT_SEED
MARGIN = 0.025
MARGIN_SENS = 0.05
Z90, Z95, Z80P = 1.645, 1.96, 0.842
ID_TOL = 5e-6
CONTRASTS = (("DIM", "q256", "q1024"), ("DIM", "q512", "q1024"), ("DIM", "q4096", "q1024"), ("QUANT", "q8", "q1024"),
             ("PROMPT", "qcard", "q1024"), ("PROMPT", "gcard", "g768"), ("EMBEDDER", "g768", "q1024"), ("EMBEDDER", "n*", "q1024"))
FAMILIES = ("DIM", "QUANT", "PROMPT", "EMBEDDER")
FAMILY_N = {"coarse": {"DIM": 6, "QUANT": 2, "PROMPT": 4, "EMBEDDER": 4}, "fine": {"DIM": 9, "QUANT": 3, "PROMPT": 6, "EMBEDDER": 6}}
PLAN_DEN = {"massive": (4946, 4923, 1.0093), "clinc": (6672, 6672, 1.0000), "banking77": (3908, 3905, 1.0015)}
PLAN_SE = {("q256", "massive"): 0.0064, ("q256", "clinc"): 0.0072, ("q512", "massive"): 0.0067, ("q512", "clinc"): 0.0062,
           ("q4096", "massive"): 0.0062, ("q4096", "clinc"): 0.0067, ("q8", "massive"): 0.0064, ("q8", "clinc"): 0.0070,
           ("qcard", "massive"): 0.0064, ("qcard", "clinc"): 0.0070, ("gcard", "massive"): 0.0065, ("gcard", "clinc"): 0.0079,
           ("g768", "massive"): 0.0064, ("g768", "clinc"): 0.0075, ("n*", "massive"): 0.0068, ("n*", "clinc"): 0.0085}
# Registered predictions (PREDICTIONS P1-P5).
P1 = {("q256", "massive"): (-0.045, -0.065, -0.025, True), ("q512", "massive"): (-0.030, -0.050, -0.010, True),
      ("q4096", "massive"): (-0.015, -0.035, 0.005, True), ("q8", "massive"): (0.003, -0.007, 0.010, False),
      ("qcard", "massive"): (0.040, 0.000, 0.080, False), ("gcard", "massive"): (-0.020, -0.050, 0.010, False),
      ("g768", "massive"): (0.085, 0.065, 0.105, True), ("n*", "massive"): (-0.055, -0.080, -0.030, False),
      ("q256", "clinc"): (0.010, -0.015, 0.035, True), ("q512", "clinc"): (-0.005, -0.025, 0.015, True),
      ("q4096", "clinc"): (0.030, 0.005, 0.055, True), ("q8", "clinc"): (0.003, -0.007, 0.010, False),
      ("qcard", "clinc"): (0.000, -0.030, 0.030, False), ("gcard", "clinc"): (-0.030, -0.070, 0.010, False),
      ("g768", "clinc"): (-0.005, -0.030, 0.020, True), ("n*", "clinc"): (-0.065, -0.100, -0.030, False)}
P2 = {"DIM": {"NOT-INVARIANT": 0.65, "UNDETERMINED": 0.30, "INVARIANT": 0.05}, "QUANT": {"INVARIANT": 0.75},
      "PROMPT": {"NOT-INVARIANT": 0.55}, "EMBEDDER": {"NOT-INVARIANT": 0.90}}
P3 = {"LEVEL": 0.03, "TRANSFORMATION": 0.15, "NO-LEVEL-ADVANTAGE": 0.65, "MIXED": 0.17}
P3_FGL = 0.95
P4 = (("fine DIM statuses all EQUIVALENT (9)", 0.60), ("fine g768 - q1024 DIFFERENT on MASSIVE and Banking77", 0.85))
P5 = (("H(g768) > H(q) at every qwen3 slice on MASSIVE", 0.95), ("|H(q8) - H(q1024)| <= 0.02 on both corpora", 0.80))
SEL_PATH = EQ.SEL_PATH
SEL_SHA = EQ.SEL_SHA
RES = os.path.join(ROOT, "experiment_results")
ID_FILES = {"nmi_matrix": os.path.join(RES, "embed_dim_slice", "nmi_matrix.csv"), "h_table": os.path.join(RES, "embed_dim_slice", "h_table.csv"),
            "nmi_q": os.path.join(RES, "embed_quant", "nmi_q.csv"), "nmi_card": os.path.join(RES, "card_protocol", "nmi_card.csv"),
            "s0_c1": os.path.join(RES, "intent_transfer", "s0_c1.csv")}
NMI_MATRIX_BLOB = "1056bad95a5353f0060f4c24e0cc392975e3bf2d"
OUT_DIR = os.path.join(RES, "gold_level_emb")
OUTCOME = "outcome.txt"
SELECTION = "nomic_selection.json"
CSVS = ("nmi_gold.csv", "h_gold.csv")
PROGRAMME = os.path.join(ROOT, "docs", "judge_v2_program.md")
REG_HEADING = "## Registered 2026-10-02 (before any code or call) — GOLD-LEVEL-EMB:"
REG_RE = re.compile(r"^" + re.escape(REG_HEADING), re.M)
REG = ("docs/judge_v2_program.md \"## Registered 2026-10-02 (before any code or call) — GOLD-LEVEL-EMB: on the pinned S0 embeddings, "
       "is the GOLD COARSE-level k-means readout invariant ...\" L23377-L23422 _as_of d635fec5 (registrar 1a922a80); kind zero-call; plan "
       "Amendment 37")
READINGS = ("builder's readings: GB1 5 dp = |value - CSV| <= 5e-6; GB2 nomic GATE selection before EVERY nomic EVAL read; GB3 n* at 256 / "
            "512 is the identity's nomic arm; GB4 one weight stream per corpus x level shared by every arm and contrast, S0 C1 beside from "
            "the same draws (seeds 0-4, BASIC); GB5 verdict lines at the measured SE_total; GB6 numeric HELD on the closed interval, SEEN "
            "never a confirmation, one Brier per probability; GB7 P4 = the 9 fine DIM statuses, P5 = q256 / q512 / q1024 / q4096")
DOES_NOT_SHOW = ("WHAT THIS RESULT WILL NOT SHOW (registered): anything about trees, leaves or the construction (k-means against gold labels "
                 "only); MTEB-style averages or any corpus beyond the three; capability text or MMLU-Pro; which embedder is better; precision "
                 "above Q8_0, other prompts or task lines, nomic CARD; that the gold coarse level is the right taxonomy; parity outside "
                 "+/-0.025 NMI or at the fine level (GL2 descriptive); a second split draw.")
SENTENCE = {
    "LEVEL": "at the gold coarse level the k-means readout is invariant within 0.025 NMI to slice, quantisation (Q4_K_M ~ Q8_0), prompt and "
             "embedder on MASSIVE and CLINC (GL2's fine statuses beside; the literature reconciliation holds here)",
    "TRANSFORMATION": "the coarse readout is invariant to within-model truncation and quantisation but not to the embedder: invariance follows "
                      "the transformation, not the level",
    "NO-LEVEL-ADVANTAGE": "the coarse k-means readout moves with the slice inside one model; the gold coarse level is not a more invariant "
                          "readout than the fine level on these corpora (GL2 beside)",
    "MIXED": "family verdicts recorded joined; no sentence"}

EVENTS = []
PHASE = {"nomic_sel": None}
STORE = {}


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_blobs():
    for name, (want, mod) in BLOBS.items():
        got = RO.git_blob_lf(mod.__file__)
        if got != want:
            refuse("%s.py is blob %s, not the registered %s: the readers must be imported unchanged" % (name, got, want))
    return True


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


def reset():
    del EVENTS[:]
    PHASE["nomic_sel"] = None
    STORE.clear()
    STORE.update({"nm": {}, "pred": {}, "truth": {}, "evrows": {}, "H": {}})
    del ITS.FIT_LOG[:]


reset()


# ------------------------------------------------------------------------------------------------ inputs
PINS = {"q8": [None], "card": [None]}           # pins-file overrides (selftest); None = the files of record


def src_path(src, emb_dir):
    return {"q4": ITS.emb_path("qwen3", emb_dir), "q8": QW.q8_path(emb_dir), "qcard": CW.card_path("qwen3", emb_dir),
            "g": ITS.emb_path("gemma", emb_dir), "gcard": CW.card_path("gemma", emb_dir), "n": ITS.emb_path("nomic", emb_dir)}[src]


def pin_all(db, emb_dir, strict, sel_path, sel_sha):
    """Every pin before any read: S0's (ingest, raw, qwen3 / gemma / nomic), EMBED-QUANT's Q8, CARD-PROTOCOL's two CARD files, the selection."""
    sha0 = {"ingest_db": ITS.pin_check(db, "ingest_db", strict)}
    ITS.raw_pin_check(db, strict)
    for src, e in (("q4", "qwen3"), ("g", "gemma"), ("n", "nomic")):
        sha0[src] = ITS.pin_check(src_path(src, emb_dir), "emb", strict, sub=e, label="intent_emb_%s.db" % e)
    sha0["q8"] = EQ.q8_pin_check(src_path("q8", emb_dir), strict, PINS["q8"][0])
    cpins = CP.load_card_pins(PINS["card"][0])
    for src, e in (("qcard", "qwen3"), ("gcard", "gemma")):
        sha0[src] = CP.card_pin_check(e, src_path(src, emb_dir), cpins, strict)
    sel = CP.read_selection(sel_path, sel_sha)
    return sha0, sel


def check_metas(CS, emb_dir, ingest_sha):
    texts, set_sha, _d = ITS.text_set(CS)
    psha = CW.load_prompts()
    ITS.check_meta(src_path("q4", emb_dir), ITS.expected_meta("qwen3", set_sha, len(texts), ingest_sha))
    ITS.check_meta(src_path("g", emb_dir), ITS.expected_meta("gemma", set_sha, len(texts), ingest_sha))
    ITS.check_meta(src_path("n", emb_dir), ITS.expected_meta("nomic", set_sha, len(texts), ingest_sha))
    ITS.check_meta(src_path("q8", emb_dir), QW.expected_meta_q8(set_sha, len(texts), ingest_sha))
    ITS.check_meta(src_path("qcard", emb_dir), CW.expected_meta_card("qwen3", set_sha, len(texts), ingest_sha, psha))
    ITS.check_meta(src_path("gcard", emb_dir), CW.expected_meta_card("gemma", set_sha, len(texts), ingest_sha, psha))
    return texts


def corpus_texts(CS):
    return sorted(set(C.text[i] for C in CS.values() for i in np.nonzero(C.kept)[0]))


def load_source(src, emb_dir, texts):
    """One DB, read once by the pinned readers at the widest slice any arm of the source needs."""
    p = src_path(src, emb_dir)
    if src == "q4":
        return EDS.load_full(p, "qwen3", texts)
    if src == "g":
        return EDS.load_full(p, "gemma", texts)
    if src == "q8":
        return EQ.load_slice(p, "q8", texts)
    if src == "qcard":
        return CP.load_slice(p, ("qwen3", "CARD"), texts)
    if src == "gcard":
        return CP.load_slice(p, ("gemma", "CARD"), texts)
    saved = ITS.SLICE2
    ITS.SLICE2 = 768
    try:
        v = ITS.load_vectors(p, "nomic", texts)
    finally:
        ITS.SLICE2 = saved
    if any(len(x) != 768 for x in v.values()):
        refuse("nomic: a vector is not 768-d after the full-width read")
    return v


def after_check(sha0, db, emb_dir):
    for k, s in sha0.items():
        now = II.file_sha(db if k == "ingest_db" else src_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the readout (%s -> %s): nothing written" % (k, s, now))
    return "pins re-checked before and after, unchanged: %s" % {k: v[:16] for k, v in sha0.items()}


def census(CS):
    out = {}
    for c in CORPORA:
        C = CS[c]
        ev = C.idx(SS.EVAL)
        out[c] = {"TRAIN": int(len(C.idx(SS.TRAIN))), "GATE": int(len(C.idx(SS.GATE))), "EVAL": int(len(ev)),
                  "components": int(len(np.unique(C.comp[ev]))) if len(ev) else 0, "kish": ITS.kish(C.comp[ev]) if len(ev) else float("nan")}
    return out


def census_lines(cn):
    L = []
    for c in CORPORA:
        r, p = cn[c], PLAN_DEN[c]
        L.append("CENSUS %s: TRAIN %d / GATE %d (in-scope, kept); EVAL in-scope %d in %d components, Kish %.4f, n_eff %.0f (registered %d / "
                 "%d / %.4f%s)" % (c, r["TRAIN"], r["GATE"], r["EVAL"], r["components"], r["kish"], r["EVAL"] / r["kish"], p[0], p[1], p[2],
                                   "" if c in COARSE_C else "; fine only"))
    return L


# ------------------------------------------------------------------------------------------------ fits and EVAL
def eval_idx(C, S, src, what):
    """THE EVAL gate: no nomic EVAL row before nomic_selection.json exists (GB2)."""
    if src == "n" and PHASE["nomic_sel"] is None:
        refuse("nomic EVAL read (%s) before the GATE selection file is written and hashed" % what)
    EVENTS.append(("EVAL", src, what))
    ev = ITS.S_idx(C, S, SS.EVAL)
    if C.name in STORE["evrows"] and not np.array_equal(STORE["evrows"][C.name], ev):
        refuse("%s: the EVAL rows differ between arms (a vector missing)" % C.name)
    STORE["evrows"][C.name] = ev
    return ev


def arm_corpus(C, S, arm, src, coarse_seeds, fine_fits=None, h=True, fine=True):
    """TRAIN fits, EVAL (read once for the arm) filed to them; NMI per seed; H (TRAIN only) on the coarse corpora."""
    c = C.name
    kc, kf = II.GOLD_K[c]
    ev = eval_idx(C, S, src, "%s %s" % (arm, c))
    if c in COARSE_C and coarse_seeds:
        t = ITS.codes(C.coarse[ev])
        preds = [ITS.assign(S.X[ev], ITS.km_fit(C, S, kc, s, "GL coarse %s@%d %s K=%d s%d" % (arm, S.d, c, kc, s))) for s in coarse_seeds]
        STORE["truth"][(c, "coarse")] = t
        STORE["pred"][(arm, c, "coarse")] = preds
        STORE["nm"][(arm, c, "coarse")] = [ITS.nmi(t, p) for p in preds]
    if fine:
        fits = fine_fits if fine_fits is not None else [ITS.km_fit(C, S, kf, s, "GL fine %s@%d %s K=%d s%d" % (arm, S.d, c, kf, s)) for s in SEEDS_F]
        t = ITS.codes(C.fine[ev])
        preds = [ITS.assign(S.X[ev], Cm) for Cm in fits]
        STORE["truth"][(c, "fine")] = t
        STORE["pred"][(arm, c, "fine")] = preds
        STORE["nm"][(arm, c, "fine")] = [ITS.nmi(t, p) for p in preds]
    if h and c in COARSE_C:
        r = ITS.d2(C, S)
        r.update(EDS.h_boot(C, S, BOOT_B, EDS.SEED_H + CORPORA.index(c)))
        STORE["H"][(arm, c)] = r


def process_source(src, CS, vecs, coarse_seeds=SEEDS_C, arms=None, coarse_arms=None, h_arms=None):
    for c in CORPORA:
        C = CS[c]
        for arm in (arms or [a for a in ARMS if ARM_SRC[a][0] == src]):
            S = ITS.Space(vecs, C, ARM_SRC[arm][1])
            arm_corpus(C, S, arm, src, coarse_seeds if (coarse_arms is None or arm in coarse_arms) else (),
                       h=(h_arms is None or arm in h_arms))
            del S


def nomic_gate(CS, vecs):
    """Phase A for nomic: fine fits on TRAIN at 256 / 512 / 768 (seeds 0-4), GATE filed; no EVAL row touched."""
    fits, gate = {}, {}
    for d in NOMIC_SLICES:
        for c in CORPORA:
            C = CS[c]
            S = ITS.Space(vecs, C, d)
            kf = II.GOLD_K[c][1]
            fits[(d, c)] = [ITS.km_fit(C, S, kf, s, "GL nomic fine @%d %s K=%d s%d" % (d, c, kf, s)) for s in SEEDS_F]
            gi = ITS.S_idx(C, S, SS.GATE)
            truth = ITS.codes(C.fine[gi])
            gate[(d, c)] = [ITS.nmi(truth, ITS.assign(S.X[gi], Cm)) for Cm in fits[(d, c)]]
            del S
    score = {d: float(np.mean([np.mean(gate[(d, c)]) for c in CORPORA])) for d in NOMIC_SLICES}
    dstar, best = EDS.pick(score)
    return fits, gate, score, dstar, best


def write_selection(path, dstar, score, gate, sha0):
    doc = {"schema": "gold_level_emb_nomic_selection/v1", "rule": "d_n* = smallest d with GATE score >= max - %.3f; GATE score = mean over the 3 "
           "corpora of the seed-mean (0-4) GATE fine NMI on TRAIN centroids (EMBED-DIM-SLICE's rule)" % EDS.TIE,
           "script_blob_lf": RO.git_blob_lf(os.path.abspath(__file__)), "inputs_sha256": sha0, "d_n*": dstar,
           "gate_score": {str(d): round(v, 10) for d, v in score.items()},
           "gate_nmi": {"nomic@%d %s" % (d, c): [round(x, 10) for x in gate[(d, c)]] for d in NOMIC_SLICES for c in CORPORA}}
    data = (json.dumps(doc, sort_keys=True, indent=1) + "\n").encode("utf-8")
    with open(path, "xb") as f:
        f.write(data)
    sha = hashlib.sha256(data).hexdigest()
    PHASE["nomic_sel"] = sha
    EVENTS.append(("SELECTION", "n", sha))
    print("%s NOMIC SELECTION written %s sha256 %s (d_n* %d; GATE scores %s); nomic EVAL is opened only now"
          % (TAG, path, sha, dstar, {d: round(v, 5) for d, v in score.items()}))
    return sha


def nomic_eval(CS, vecs, fits, dstar):
    """Phase B for nomic: EVAL at 256 / 512 (identity: coarse and fine seeds 0-4) and at d_n* (coarse 0-29, fine 0-4, H)."""
    for d in sorted(set(NOMIC_ID_SLICES) | {dstar}):
        arm = "n*" if d == dstar else "n@%d" % d
        for c in CORPORA:
            C = CS[c]
            S = ITS.Space(vecs, C, d)
            # fine: phase A's TRAIN fits at this slice; coarse: fresh TRAIN fits
            arm_corpus(C, S, arm, "n", SEEDS_C if d == dstar else SEEDS_F, fine_fits=fits[(d, c)], h=(d == dstar))
            del S
        if d == dstar and d in NOMIC_ID_SLICES:            # GB3
            for k in list(STORE["nm"]):
                if k[0] == "n*":
                    STORE["nm"][("n@%d" % d,) + k[1:]] = STORE["nm"][k][:len(SEEDS_F)]


# ------------------------------------------------------------------------------------------------ identity
def _read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def identity_targets(files):
    """-> ({(arm, corpus, level, seed): [values]}, {(arm, corpus): row}) from the CSVs of record."""
    T, H = {}, {}

    def put(k, v):
        T.setdefault(k, []).append(float(v))
    for r in _read_csv(files["nmi_matrix"]):
        if r["side"] != "EVAL":
            continue
        arm = "q%s" % r["slice"] if r["embedder"] == "qwen3" else ("g768" if r["slice"] == "768" else None)
        if arm in EDS_ARMS and int(r["seed"]) in SEEDS_F:
            put((arm, r["corpus"], r["level"], int(r["seed"])), r["nmi"])
    for r in _read_csv(files["nmi_q"]):
        if int(r["seed"]) in SEEDS_F and r["side"] == "EVAL" and r["slice"] == "1024":
            put(({"q8": "q8", "q4": "q1024"}[r["arm"]], r["corpus"], r["level"], int(r["seed"])), r["nmi"])
    for r in _read_csv(files["nmi_card"]):
        arm = {("qwen3", "CARD"): "qcard", ("gemma", "CARD"): "gcard", ("qwen3", "RAW"): "q1024", ("gemma", "RAW"): "g768"}[(r["embedder"], r["protocol"])]
        put((arm, r["corpus"], r["level"], int(r["seed"])), r["nmi"])
    for r in _read_csv(files["s0_c1"]):
        if r["embedder"] == "nomic" and int(r["slice"]) in NOMIC_ID_SLICES:
            put(("n@%s" % r["slice"], r["corpus"], r["level"], int(r["seed"])), r["nmi"])
    for r in _read_csv(files["h_table"]):
        arm = "q%s" % r["slice"] if r["embedder"] == "qwen3" else ("g768" if r["slice"] == "768" else None)
        if arm in EDS_ARMS:
            H[(arm, r["corpus"])] = r
    return T, H


def identity_check(T, H, arms, what):
    """-> one line; REFUSES unless every target of these arms is reproduced (GB1) and each target has a computed value."""
    bad, n, dev = [], 0, 0.0
    for (arm, c, lev, s), vals in sorted(T.items()):
        if arm not in arms:
            continue
        got = STORE["nm"].get((arm, c, lev))
        if got is None or len(got) <= s:
            bad.append("%s %s %s s%d: not computed" % (arm, c, lev, s))
            continue
        for v in vals:
            n += 1
            dev = max(dev, abs(got[s] - v))
            if abs(got[s] - v) > ID_TOL:
                bad.append("%s %s %s s%d: %.6f vs %.6f" % (arm, c, lev, s, got[s], v))
    nh = 0
    for (arm, c), r in sorted(H.items()):
        if arm not in arms:
            continue
        g = STORE["H"].get((arm, c))
        if g is None:
            bad.append("H %s %s: not computed" % (arm, c))
            continue
        for k_csv, k in (("H", "H"), ("lo", "lo"), ("hi", "hi"), ("random_p95", "p95")):
            nh += 1
            dev = max(dev, abs(g[k] - float(r[k_csv])))
            if abs(g[k] - float(r[k_csv])) > ID_TOL:
                bad.append("H %s %s %s: %.6f vs %s" % (arm, c, k, g[k], r[k_csv]))
        if int(g["dropped"]) != int(r["dropped_labels"]):
            bad.append("H %s %s dropped %d vs %s" % (arm, c, g["dropped"], r["dropped_labels"]))
    line = "IDENTITY %s: %d NMI values and %d H values of record compared for %s; max |deviation| %.2e (tolerance %.0e, GB1)" % (
        what, n, nh, "/".join(sorted(arms)), dev, ID_TOL)
    print("%s %s" % (TAG, line))
    if bad or n == 0:
        refuse("IDENTITY PRECONDITION FAILED (%s): %s; no readout is written" % (what, bad[:6] if bad else "nothing compared"))
    return line + " -> REPRODUCED"


# ------------------------------------------------------------------------------------------------ statistics
def boot_level(CS, c, level, arms, B=None):
    """B paired draws (one weight vector per draw for every arm): -> {arm: (B x seeds) weighted NMI}. S0's C1 stream for (c, level)."""
    B = BOOT_B if B is None else B
    t = STORE["truth"][(c, level)]
    comp = CS[c].comp[STORE["evrows"][c]]
    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index(level))
    W = {a: np.empty((B, len(STORE["pred"][(a, c, level)]))) for a in arms}
    for b, w in enumerate(ITS.comp_weights(comp, B, rng)):
        for a in arms:
            for j, p in enumerate(STORE["pred"][(a, c, level)]):
                W[a][b, j] = ITS.nmi(t, p, w)
    return W


def contrast(c, level, A, Bm, W, margin=None):
    m = MARGIN if margin is None else margin
    nA, nB = np.asarray(STORE["nm"][(A, c, level)]), np.asarray(STORE["nm"][(Bm, c, level)])
    if len(nA) != len(nB):
        refuse("%s / %s %s %s: seed counts differ (%d vs %d)" % (A, Bm, c, level, len(nA), len(nB)))
    ns = len(nA)
    D = float(nA.mean() - nB.mean())
    dw = W[A].mean(1) - W[Bm].mean(1)
    se_boot = float(np.std(dw, ddof=1))
    var_seed = float(np.var(nA - nB, ddof=1))
    se = float(np.sqrt(se_boot ** 2 + var_seed / ns))
    lo90, hi90, lo95, hi95 = D - Z90 * se, D + Z90 * se, D - Z95 * se, D + Z95 * se
    st = EQ.status(D, m, lo90, hi90, lo95, hi95)
    k = len(SEEDS_F)
    d5 = float(nA[:k].mean() - nB[:k].mean())
    dw5 = W[A][:, :k].mean(1) - W[Bm][:, :k].mean(1)
    se5 = float(np.std(dw5, ddof=1))
    lo5, hi5 = ITS.basic_ci(d5, dw5)
    sp5 = max(float(nA[:k].max() - nA[:k].min()), float(nB[:k].max() - nB[:k].min()))
    bar5 = max(2.8 * se5, sp5)
    return {"D": D, "se_boot": se_boot, "var_seed": var_seed, "seed_term": float(np.sqrt(var_seed / ns)), "se": se, "ns": ns,
            "lo90": lo90, "hi90": hi90, "lo95": lo95, "hi95": hi95, "status": st,
            "direction": ("%s HIGHER" % A if D > 0 else "%s LOWER" % A) if st == "DIFFERENT" else "",
            "status_sens": EQ.status(D, MARGIN_SENS, lo90, hi90, lo95, hi95) if margin is None else None,
            "c1": ITS.c1_status(d5, lo5, hi5, bar5), "d5": d5, "lo5": lo5, "hi5": hi5, "bar5": bar5,
            "spread": {A: (float(nA[:k].max() - nA[:k].min()), float(nA.max() - nA.min())), Bm: (float(nB[:k].max() - nB[:k].min()), float(nB.max() - nB.min()))},
            "eq_reach": m - (Z90 + Z80P) * se, "diff_reach": m + Z80P * se}


def family_verdicts(stat, level):
    out = {}
    for F in FAMILIES:
        sts = [v for (f, _a, _b, _c), v in stat.items() if f == F]
        if len(sts) != FAMILY_N[level][F]:
            refuse("%s family %s holds %d statuses, registered %d" % (level, F, len(sts), FAMILY_N[level][F]))
        if all(s == "EQUIVALENT" for s in sts):
            out[F] = "INVARIANT"
        elif any(s == "DIFFERENT" for s in sts):
            out[F] = "NOT-INVARIANT"
        else:
            out[F] = "UNDETERMINED"
    return out


def reading(fam):
    if all(fam[F] == "INVARIANT" for F in FAMILIES):
        return "LEVEL"
    if fam["DIM"] == "INVARIANT" and fam["QUANT"] == "INVARIANT" and fam["EMBEDDER"] == "NOT-INVARIANT":
        return "TRANSFORMATION"
    if fam["DIM"] == "NOT-INVARIANT":
        return "NO-LEVEL-ADVANTAGE"
    return "MIXED"


def falsifiers(fam):
    moved = [F for F in FAMILIES if fam[F] == "NOT-INVARIANT"]
    return bool(moved), moved, bool(fam["EMBEDDER"] == "INVARIANT")


def verdict_line(pred, r):
    if abs(pred) <= r["eq_reach"]:
        return "SCOREABLE (EQUIVALENT side)"
    if abs(pred) >= r["diff_reach"]:
        return "SCOREABLE (DIFFERENT side)"
    return "DESCRIPTIVE-ONLY"


def brier(p, event):
    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2


def _hit(v, lo, hi):
    return bool(lo <= v <= hi)


def readouts(CS, B=None):
    """GL1 (coarse, deciding), GL2 (fine, descriptive), GL3 (H): every contrast on the shared per-(corpus, level) stream."""
    R = {"coarse": {}, "fine": {}}
    for level, corp in (("coarse", COARSE_C), ("fine", CORPORA)):
        for c in corp:
            W = boot_level(CS, c, level, ARMS, B)
            for F, A, Bm in CONTRASTS:
                R[level][(F, A, Bm, c)] = contrast(c, level, A, Bm, W)
    R["fam"] = family_verdicts({k: v["status"] for k, v in R["coarse"].items()}, "coarse")
    R["fam_sens"] = family_verdicts({k: v["status_sens"] for k, v in R["coarse"].items()}, "coarse")
    R["fam_fine"] = family_verdicts({k: v["status"] for k, v in R["fine"].items()}, "fine")
    R["reading"] = reading(R["fam"])
    R["fgl"], R["moved"], R["fgl2"] = falsifiers(R["fam"])
    return R


# ------------------------------------------------------------------------------------------------ lines
def support_lines(R, cn):
    L = ["== SUPPORT (measured; registered planning values beside) =="]
    for c in CORPORA:
        r = cn[c]
        ev = STORE["evrows"][c]
        L.append("  %s: n %d EVAL in-scope items in %d components, Kish %.4f, n_eff %.0f; seeds coarse %d / fine %d; B %d" % (
            c, len(ev), r["components"], r["kish"], len(ev) / r["kish"], len(SEEDS_C) if c in COARSE_C else 0, len(SEEDS_F), BOOT_B))
    for (F, A, Bm, c), r in R["coarse"].items():
        p = P1[(A, c)][0]
        L.append("  GL1 %s - %s %s: SE_boot %.5f, seed term sqrt(var_seed / %d) %.5f, SE_total %.5f (planned %.4f); EQUIVALENT reach |D_true| <= "
                 "%.4f, DIFFERENT reach >= %.4f; verdict line at P1 %+.3f: %s" % (A, Bm, c, r["se_boot"], r["ns"], r["seed_term"], r["se"],
                                                                                PLAN_SE[(A, c)], r["eq_reach"], r["diff_reach"], p, verdict_line(p, r)))
    return L


def gl1_lines(R):
    L = ["== GL1 (DECIDING; coarse; D = 30-seed mean NMI difference at K_c; EQUIVALENT iff D +/- 1.645 SE_total inside (-%.3f, +%.3f); "
         "DIFFERENT iff |D| > %.3f AND D +/- 1.96 SE_total excludes 0; NEITHER otherwise) ==" % (MARGIN, MARGIN, MARGIN)]
    for (F, A, Bm, c), r in R["coarse"].items():
        L.append("GL1 %s %s - %s %s: %s%s (D %+.5f; 90%% [%+.5f, %+.5f]; 95%% [%+.5f, %+.5f]; SE_total %.5f; means %.5f / %.5f)" % (
            F, A, Bm, c, r["status"], (" " + r["direction"]) if r["direction"] else "", r["D"], r["lo90"], r["hi90"], r["lo95"], r["hi95"],
            r["se"], float(np.mean(STORE["nm"][(A, c, "coarse")])), float(np.mean(STORE["nm"][(Bm, c, "coarse")]))))
    for F in FAMILIES:
        L.append("FAMILY %s: %s (%d statuses: %s)" % (F, R["fam"][F], FAMILY_N["coarse"][F], ", ".join(
            "%s-%s %s %s" % (A, Bm, c, r["status"]) for (f, A, Bm, c), r in R["coarse"].items() if f == F)))
    L.append("READING: %s: %s" % (R["reading"], SENTENCE[R["reading"]]))
    if R["fgl"]:
        L.append("F-GL: FIRED (NOT-INVARIANT: %s): the thesis may not write that the gold coarse level is invariant to slice, quantisation, "
                 "prompt and embedder here; SQ5's reconciliation must name the family that moved (%s), not the level" % (", ".join(R["moved"]), ", ".join(R["moved"])))
    else:
        L.append("F-GL: NOT FIRED (no coarse family NOT-INVARIANT)")
    if R["fgl2"]:
        L.append("F-GL': FIRED (EMBEDDER INVARIANT): the seen coarse gemma lead (MASSIVE +0.086 at 5 seeds; S0's gemma coarse BETTER +0.135 at "
                 "256) is overturned as a property of the embedders")
    else:
        L.append("F-GL': NOT FIRED (EMBEDDER %s)" % R["fam"]["EMBEDDER"])
    L.append("No recorded number is revised; S0 C1b's \"not fired, never parity\" stands")
    return L


def gl2_lines(R):
    L = ["== GL2 (DESCRIPTIVE-ONLY; fine; seeds 0-4, var_seed / 5, margin 0.025; never a criterion) =="]
    for (F, A, Bm, c), r in R["fine"].items():
        L.append("  GL2 %s %s - %s %s: %s%s (D %+.5f; 90%% [%+.5f, %+.5f]; SE_total %.5f)" % (
            F, A, Bm, c, r["status"], (" " + r["direction"]) if r["direction"] else "", r["D"], r["lo90"], r["hi90"], r["se"]))
    L.append("  GL2 families (descriptive): %s" % ", ".join("%s %s" % (F, R["fam_fine"][F]) for F in FAMILIES))
    return L


def gl3_lines(R):
    L = ["== GL3 (DESCRIPTIVE-ONLY; H = ARI of average-link on the gold fine TRAIN centroids cut at K_c vs the gold map; TRAIN-component "
         "bootstrap B %d, percentile) ==" % BOOT_B]
    for c in COARSE_C:
        for a in ARMS:
            h = STORE["H"][(a, c)]
            L.append("  H %s %s: %.4f [%.4f, %.4f], random p95 %.4f, dropped labels %d" % (a, c, h["H"], h["lo"], h["hi"], h["p95"], h["dropped"]))
        for F, A, Bm in CONTRASTS:
            L.append("  Delta H %s - %s %s: %+.4f" % (A, Bm, c, STORE["H"][(A, c)]["H"] - STORE["H"][(Bm, c)]["H"]))
    return L


def beside_lines(R, dstar):
    L = ["== PRINTED BESIDE (never deciding) =="]
    L.append("  d_n* = %d (nomic_selection.json); n* reads nomic RAW at %d" % (dstar, dstar))
    for level in ("coarse", "fine"):
        for (F, A, Bm, c), r in R[level].items():
            L.append("  S0 C1 %s %s - %s %s (seeds 0-4): %s (D5 %+.5f, BASIC [%+.5f, %+.5f], bar %.5f); spreads 5 / %d seeds: %s %.4f / %.4f, %s %.4f / %.4f%s" % (
                level, A, Bm, c, r["c1"], r["d5"], r["lo5"], r["hi5"], r["bar5"], r["ns"], A, r["spread"][A][0], r["spread"][A][1], Bm,
                r["spread"][Bm][0], r["spread"][Bm][1], ("; GL1 at margin 0.05: %s" % r["status_sens"]) if level == "coarse" else ""))
    L.append("  GL1 families at margin 0.05 (sensitivity): %s" % ", ".join("%s %s" % (F, R["fam_sens"][F]) for F in FAMILIES))
    return L


def predictions_lines(R):
    L = ["== PREDICTIONS (registered; numeric HELD iff the point lies in the closed 80% interval; probabilities by Brier; SEEN never a confirmation) =="]
    for (F, A, Bm, c), r in R["coarse"].items():
        p, lo, hi, seen = P1[(A, c)]
        L.append("  P1 %s - %s %s: D %+.5f vs %+.3f [%+.3f, %+.3f]: %s%s" % (A, Bm, c, r["D"], p, lo, hi, "HELD" if _hit(r["D"], lo, hi) else "FAILED",
                                                                       " (SEEN: never a confirmation)" if seen else ""))
    for F in FAMILIES:
        br = {k: brier(q, R["fam"][F] == k) for k, q in P2[F].items()}
        L.append("  P2 %s %s: Brier %s" % (F, R["fam"][F], ", ".join("%s %.4f" % kv for kv in br.items())))
    br = {k: brier(q, R["reading"] == k) for k, q in P3.items()}
    L.append("  P3 reading %s: Brier %s (sum %.4f); F-GL fires %s: p %.2f, Brier %.4f" % (R["reading"], ", ".join("%s %.4f" % kv for kv in br.items()),
                                                                                       sum(br.values()), R["fgl"], P3_FGL, brier(P3_FGL, R["fgl"])))
    e1 = all(R["fine"][(F, A, Bm, c)]["status"] == "EQUIVALENT" for (F, A, Bm, c) in R["fine"] if F == "DIM")
    e2 = all(R["fine"][("EMBEDDER", "g768", "q1024", c)]["status"] == "DIFFERENT" for c in ("massive", "banking77"))
    L.append("  P4 %s: event %s, p %.2f, Brier %.4f (GL2, descriptive)" % (P4[0][0], e1, P4[0][1], brier(P4[0][1], e1)))
    L.append("  P4 %s: event %s, p %.2f, Brier %.4f (GL2, descriptive; SEEN)" % (P4[1][0], e2, P4[1][1], brier(P4[1][1], e2)))
    H = STORE["H"]
    e3 = all(H[("g768", "massive")]["H"] > H[(q, "massive")]["H"] for q in ("q256", "q512", "q1024", "q4096"))
    e4 = all(abs(H[("q8", c)]["H"] - H[("q1024", c)]["H"]) <= 0.02 for c in COARSE_C)
    L.append("  P5 %s: event %s, p %.2f, Brier %.4f (GL3; SEEN)" % (P5[0][0], e3, P5[0][1], brier(P5[0][1], e3)))
    L.append("  P5 %s: event %s, p %.2f, Brier %.4f (GL3)" % (P5[1][0], e4, P5[1][1], brier(P5[1][1], e4)))
    return L


def header_lines(blob, pins_state, cn, idlines, dstar):
    L = ["GOLD-LEVEL-EMB outcome (tools/analysis/gold_level_emb.py, blob %s; imports %s unchanged)" % (
        blob, ", ".join("%s.py blob %s" % (k, v[0]) for k, v in BLOBS.items())),
         "registration: " + REG, "pool of record: none read; zero judge calls; no construction; no Ollama", pins_state]
    L += census_lines(cn)
    L += idlines
    L.append("NOMIC SELECTION: d_n* = %d (sha256 %s), written before any nomic EVAL read (GB2)" % (dstar, PHASE["nomic_sel"]))
    L.append(READINGS)
    return L


# ------------------------------------------------------------------------------------------------ run
def out_paths(out_dir):
    return [os.path.join(out_dir, n) for n in (SELECTION, OUTCOME) + CSVS]


def compute(CS, emb_dir, sha0, out_dir, files, B=None):
    """Every source once, identity per source (fail fast), nomic GATE -> selection file -> nomic EVAL; then the readouts."""
    T, H = identity_targets(files)
    texts = corpus_texts(CS)
    idlines = []
    for src in SOURCES:
        vecs = load_source(src, emb_dir, texts)
        if src == "n":
            fits, gate, score, dstar, best = nomic_gate(CS, vecs)
            os.makedirs(out_dir, exist_ok=True)
            write_selection(os.path.join(out_dir, SELECTION), dstar, score, gate, sha0)
            nomic_eval(CS, vecs, fits, dstar)
            STORE["dstar"], STORE["gate_score"] = dstar, score
            idlines.append(identity_check(T, H, {"n@256", "n@512"}, "nomic 256 / 512 (s0_c1.csv)"))
        else:
            process_source(src, CS, vecs)
            arms = {a for a in ARMS if ARM_SRC[a][0] == src}
            idlines.append(identity_check(T, H, arms, "source %s" % src))
        del vecs
    R = readouts(CS, B)
    return R, idlines


def main_run(db=None, emb_dir=None, out_dir=OUT_DIR, programme=PROGRAMME, files=None, sel_path=SEL_PATH, sel_sha=SEL_SHA, B=None, strict_blob=True):
    check_blobs()
    reset()
    db = db or os.path.join(ITS.DATA_ROOT, II.DB_NAME)
    emb_dir = emb_dir or ITS.DATA_ROOT
    files = files or ID_FILES
    for p in out_paths(out_dir):
        if os.path.lexists(p):
            refuse("%s exists: every output is write-once" % p)
    if not check_registered(programme):
        refuse("the registration heading is absent from %s: --run reads only a registered test" % programme)
    if strict_blob and RO.git_blob_lf(files["nmi_matrix"]) != NMI_MATRIX_BLOB:
        refuse("nmi_matrix.csv is blob %s, not the registered %s" % (RO.git_blob_lf(files["nmi_matrix"]), NMI_MATRIX_BLOB))
    heavy_check()
    sha0, _sel = pin_all(db, emb_dir, True, sel_path, sel_sha)
    CS = ITS.load_corpora(db)
    check_metas(CS, emb_dir, sha0["ingest_db"])
    cn = census(CS)
    for ln in census_lines(cn):
        print("%s %s" % (TAG, ln))
    R, idlines = compute(CS, emb_dir, sha0, out_dir, files, B)
    pins_state = after_check(sha0, db, emb_dir)
    blob = RO.git_blob_lf(os.path.abspath(__file__))
    L = header_lines(blob, pins_state, cn, idlines, STORE["dstar"])
    L += support_lines(R, cn)
    L.append(ITS.fit_audit())
    L += gl1_lines(R) + gl2_lines(R) + gl3_lines(R) + beside_lines(R, STORE["dstar"]) + predictions_lines(R)
    L.append(DOES_NOT_SHOW)
    for ln in L:
        print(ln)
    po = os.path.join(out_dir, OUTCOME)
    with open(po, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    write_csvs(out_dir)
    print("%s wrote %s (+ %s; write-once, of record)" % (TAG, po, ", ".join(CSVS)))
    return R, L, po


def write_csvs(out_dir):
    with open(os.path.join(out_dir, CSVS[0]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["arm", "source", "slice", "corpus", "level", "side", "seed", "nmi"])
        for (arm, c, lev), vals in sorted(STORE["nm"].items()):
            src, d = ARM_SRC[arm] if arm in ARM_SRC else ("n", int(arm.split("@")[1]))
            d = STORE["dstar"] if arm == "n*" else d
            for s, v in enumerate(vals):
                w.writerow([arm, src, d, c, lev, "EVAL", s, "%.6f" % v])
    with open(os.path.join(out_dir, CSVS[1]), "x", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["arm", "corpus", "H", "lo", "hi", "random_p95", "dropped_labels"])
        for (arm, c), h in sorted(STORE["H"].items()):
            w.writerow([arm, c, "%.6f" % h["H"], "%.6f" % h["lo"], "%.6f" % h["hi"], "%.6f" % h["p95"], h["dropped"]])


def dry_run(db=None, emb_dir=None, programme=PROGRAMME, files=None, sel_path=SEL_PATH, sel_sha=SEL_SHA, timing=True, identity=False):
    """Pins, selection, census / denominators against the registration, CSV blobs, timed fits + one bootstrap pass, price; with
    identity=True the identity on the NON-nomic arms (values of record only: no coarse value of q8 / qcard / gcard, no nomic EVAL). Writes
    nothing."""
    check_blobs()
    reset()
    db = db or os.path.join(ITS.DATA_ROOT, II.DB_NAME)
    emb_dir = emb_dir or ITS.DATA_ROOT
    files = files or ID_FILES
    print("%s DRY RUN (zero calls; nothing written); script blob %s; %s" % (TAG, RO.git_blob_lf(os.path.abspath(__file__)),
                                                                          ", ".join("%s %s" % (k, v[0][:8]) for k, v in BLOBS.items())))
    print("%s pool of record: none read (pool_guard not engaged); %s" % (TAG, REG))
    check_registered(programme)
    heavy_check()
    sha0, _sel = pin_all(db, emb_dir, False, sel_path, sel_sha)
    for k, p in sorted(files.items()):
        print("%s identity file %s blob %s%s" % (TAG, os.path.relpath(p, ROOT) if p.startswith(ROOT) else p, RO.git_blob_lf(p),
                                                 (" [registered %s: %s]" % (NMI_MATRIX_BLOB[:8], "PIN OK" if RO.git_blob_lf(p) == NMI_MATRIX_BLOB else "PIN MISMATCH")) if k == "nmi_matrix" else ""))
    CS = ITS.load_corpora(db)
    check_metas(CS, emb_dir, sha0["ingest_db"])
    cn = census(CS)
    for ln in census_lines(cn):
        print("%s %s" % (TAG, ln))
    ok = all((cn[c]["EVAL"], cn[c]["components"]) == PLAN_DEN[c][:2] for c in CORPORA)
    print("%s DENOMINATORS vs registration Support (a): %s" % (TAG, "MATCH (MASSIVE 4,946 / 4,923; CLINC 6,672 / 6,672; Banking77 3,908 / 3,905)"
                                                             if ok else "DIFFERENT: %s" % {c: (cn[c]["EVAL"], cn[c]["components"]) for c in CORPORA}))
    print("%s PLAN: arms %s; contrasts %d x 2 coarse corpora = %d statuses (families %s); coarse fits %d (9 arms x 2 corpora x 30 seeds); "
          "fine fits %d + nomic GATE %d; B %d" % (TAG, ", ".join(ARMS), len(CONTRASTS), 2 * len(CONTRASTS), FAMILY_N["coarse"],
                                                   9 * 2 * len(SEEDS_C), 9 * 3 * len(SEEDS_F), 3 * 3 * len(SEEDS_F), BOOT_B))
    texts = corpus_texts(CS)
    if timing:
        vecs = load_source("q4", emb_dir, texts)
        C = CS["clinc"]
        S = ITS.Space(vecs, C, 4096)
        t0 = time.time()
        ITS.km_fit(C, S, II.GOLD_K["clinc"][0], 0, "GL dry-run timing coarse q4096 clinc K=10 s0 (TRAIN only)")
        t_c = time.time() - t0
        t0 = time.time()
        ITS.km_fit(C, S, II.GOLD_K["clinc"][1], 0, "GL dry-run timing fine q4096 clinc K=150 s0 (TRAIN only)")
        t_f = time.time() - t0
        del S
        n = cn["clinc"]["EVAL"]
        rng = np.random.default_rng(0)
        tt, pp = rng.integers(10, size=n), rng.integers(10, size=n)
        ww = list(ITS.comp_weights(np.arange(n), 20, rng))
        t0 = time.time()
        for w in ww:
            ITS.nmi(tt, pp, w)
        t_n = (time.time() - t0) / 20
        boot = t_n * BOOT_B * (9 * 30 * 2 + 9 * 5 * 3)
        fits = t_c * 30 * 2 * sum(min(ARM_SRC[a][1] or 768, 4096) / 4096.0 for a in ARMS) + t_f * 5 * 3 * sum(min(ARM_SRC[a][1] or 768, 4096) / 4096.0 for a in ARMS)
        print("%s TIMING: one q4096 CLINC coarse fit (K 10, TRAIN) %.1f s; one q4096 CLINC fine fit (K 150) %.1f s; one weighted NMI (n %d) %.2f ms; "
              "PRICE about %.0f min fits (scaled by d / 4096) + %.0f min bootstraps + H bootstraps (18 x B %d), single-threaded (an estimate)"
              % (TAG, t_c, t_f, n, 1000 * t_n, fits / 60.0, boot / 60.0, BOOT_B))
        del vecs
    if identity:
        T, H = identity_targets(files)
        for src in ("q4", "q8", "qcard", "g", "gcard"):
            vecs = load_source(src, emb_dir, texts)
            arms = [a for a in ARMS if ARM_SRC[a][0] == src]
            process_source(src, CS, vecs, coarse_seeds=SEEDS_F, arms=arms, coarse_arms=EDS_ARMS, h_arms=EDS_ARMS)
            print("%s %s" % (TAG, identity_check(T, H, set(arms), "dry-run source %s (no nomic; no coarse beyond EDS arms)" % src)))
            del vecs
    print("%s %s" % (TAG, after_check(sha0, db, emb_dir)))
    print("%s %s" % (TAG, ITS.fit_audit()))
    print("%s DRY RUN complete: nothing written; no nomic EVAL read; no selection file" % TAG)
    return 0


# ------------------------------------------------------------------------------------------------ selftest fixtures
FX_B = 120
NAT = {"q4": 4096, "q8": 4096, "qcard": 4096, "g": 768, "gcard": 768, "n": 768}
# Bands: (offset, fine amplitude, coarse amplitude, noise, eval_fine_amplitude or None (= same), corpora or None (= all)).
BASE = (0, 1.5, 0.6, 0.9, None, None)
FX_SPEC = {
    # A -> NO-LEVEL-ADVANTAGE: a coarse boost in q4 at 512-531 on CLINC only (q256 / q512 DIFFERENT on CLINC, EQUIVALENT on MASSIVE: the
    # family is NOT-INVARIANT via CLINC alone); q8 = q4 plus a noise band at 40 (a file that differs from q4); qcard a copy of q4; g / gcard
    # carry the boost at 256 (g768 ~ q1024); nomic: no boost, a fine band at 512 that is informative on TRAIN / GATE and points at a random
    # axis on EVAL (GATE picks 768; EVAL alone would not).
    "A": {"q4": [BASE, (512, 0.0, 3.0, 0.2, None, ("clinc",))], "q8": [BASE, (512, 0.0, 3.0, 0.2, None, ("clinc",)), (40, 0.0, 0.0, 0.35, None, None)],
          "g": [BASE, (256, 0.0, 3.0, 0.2, None, ("clinc",))],
          "n": [BASE, (512, 3.0, 0.0, 0.2, -3.0, None)]},
    # B -> TRANSFORMATION: no boost anywhere (DIM, QUANT, PROMPT invariant; g768 = q1024 geometry); nomic's coarse axes destroyed on MASSIVE
    # only (EMBEDDER NOT-INVARIANT via MASSIVE alone), the TRAIN / GATE-only fine band again.
    "B": {"q4": [BASE], "g": [BASE], "n": [(0, 1.5, 0.6, 0.9, None, ("clinc", "banking77")), (0, 1.5, 0.0, 0.9, None, ("massive",)),
                                            (512, 3.0, 0.0, 0.2, -3.0, None)]},
    # C -> LEVEL: one geometry everywhere (nomic too; its three slices tie -> 256).
    "C": {"q4": [BASE], "g": [BASE], "n": [BASE]},
}


def _rng(*parts):
    return np.random.default_rng(int(hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12], 16))


def _plant(bands, nat, c, f, side, key):
    v = np.zeros(nat)
    for j, (o, af, ac, sig, aev, corp) in enumerate(bands):
        if corp is not None and c not in corp:
            continue
        a = af if (side != SS.EVAL or aev is None) else abs(aev)
        ff = f
        if side == SS.EVAL and aev is not None and aev < 0 and f is not None:      # EVAL: the band points at a random fine axis
            ff = int(_rng("ev", key, j).integers(16))
        if ff is not None:
            v[o + ff] += a
            v[o + 16 + ff % 4] += ac
        v[o:o + 20] += sig * _rng("fx", key, j).normal(size=20)     # keyed by text and band index: copies are exact copies
    return v


def _write_emb(path, meta, V):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
    con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(meta, model_digest="stub").items()))
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.asarray(v, dtype=">f4").tobytes()) for t, v in sorted(V.items())])
    con.commit()
    con.close()


def build_fixture(td, name):
    spec = FX_SPEC[name]
    rows = ITS._fixture_rows()
    db = os.path.join(td, II.DB_NAME)
    with contextlib.redirect_stdout(io.StringIO()):
        II.write_db(db, rows, [("fixture", "none", "none", "0" * 64, 0, "1970-01-01T00:00:00Z")])
    CS = ITS.load_corpora(db)
    texts, set_sha, _d = ITS.text_set(CS)
    ish = II.file_sha(db)
    meta = {}
    for C in CS.values():
        for i in np.nonzero(C.kept)[0]:
            meta[C.text[i]] = (C.name, None if C.oos[i] else int(C.fine[i][-2:]), C.side[i])
    with contextlib.redirect_stdout(io.StringIO()):
        psha = CW.load_prompts()
    metas = {"q4": ITS.expected_meta("qwen3", set_sha, len(texts), ish), "g": ITS.expected_meta("gemma", set_sha, len(texts), ish),
             "n": ITS.expected_meta("nomic", set_sha, len(texts), ish), "q8": QW.expected_meta_q8(set_sha, len(texts), ish),
             "qcard": CW.expected_meta_card("qwen3", set_sha, len(texts), ish, psha), "gcard": CW.expected_meta_card("gemma", set_sha, len(texts), ish, psha)}
    bands = {"q4": spec["q4"], "q8": spec.get("q8", spec["q4"]), "qcard": spec["q4"], "g": spec["g"], "gcard": spec["g"], "n": spec["n"]}
    for src in SOURCES:
        V = {t: _plant(bands[src], NAT[src], c, f, sd, t) for t, (c, f, sd) in meta.items()}
        _write_emb(src_path(src, td), metas[src], V)
    pins = os.path.join(td, "pins.json")
    con = II.open_db_ro(db)
    rawp = {n: s for n, s in con.execute("SELECT name, sha256 FROM provenance")}
    con.close()
    with open(pins, "w") as fh:
        json.dump({"schema": II.PINS_SCHEMA, "raw": rawp, "ingest_db": ish,
                   "emb": {e: II.file_sha(src_path(s, td)) for s, e in (("q4", "qwen3"), ("g", "gemma"), ("n", "nomic"))}}, fh)
    qp = os.path.join(td, "q8_pins.json")
    with open(qp, "w") as fh:
        json.dump({"schema": EQ.PINS_SCHEMA, "q8": II.file_sha(src_path("q8", td))}, fh)
    cp = os.path.join(td, "card_pins.json")
    with open(cp, "w") as fh:
        json.dump({"schema": CP.PINS_SCHEMA, "qwen3_card": II.file_sha(src_path("qcard", td)), "gemma_card": II.file_sha(src_path("gcard", td)),
                   "nomic_card": None}, fh)
    sel = os.path.join(td, "selection.json")
    data = (json.dumps({"d_q*": 1024, "d_g*": 768}, sort_keys=True) + "\n").encode()
    with open(sel, "wb") as fh:
        fh.write(data)
    prog = os.path.join(td, "programme.md")
    with open(prog, "w", encoding="utf-8") as fh:
        fh.write("intro\n%s fixture\n" % REG_HEADING)
    fx = {"td": td, "db": db, "pins": pins, "q8pins": qp, "cardpins": cp, "sel": sel, "sel_sha": hashlib.sha256(data).hexdigest(), "prog": prog, "name": name}
    fx["oracle"] = _oracle(fx)
    fx["files"] = _id_files(fx)
    return fx


def _wnmi(t, p, w):
    """Weighted arithmetic NMI written independently of S0's nmi."""
    ut, it = np.unique(t, return_inverse=True)
    up, ip = np.unique(p, return_inverse=True)
    M = np.zeros((len(ut), len(up)))
    np.add.at(M, (it, ip), w)
    n = M.sum()
    P = M / n
    a, b = P.sum(1), P.sum(0)
    if (a > 0).sum() == 1 and (b > 0).sum() == 1:
        return 1.0
    nz = P > 0
    mi = float((P[nz] * np.log(P[nz] / np.outer(a, b)[nz])).sum())
    ha = -float((a[a > 0] * np.log(a[a > 0])).sum())
    hb = -float((b[b > 0] * np.log(b[b > 0])).sum())
    return max(mi, 0.0) / max((ha + hb) / 2.0, 1e-300) if mi > 0 else 0.0


def _oracle(fx, B=None):
    """INDEPENDENT recomputation: own sqlite read, own slice + renormalise, own side masks, sklearn NMI for the points, own weighted NMI and
    own weight generation (the same generator order) for SE; own GATE selection, own TOST, own family / reading. Only S0's skmeans (same
    seeds) is shared."""
    from sklearn.metrics import normalized_mutual_info_score as NMI
    B = FX_B if B is None else B
    with ITS.fixture_scope():
        CS = ITS.load_corpora(fx["db"])
        GK = dict(II.GOLD_K)
    raw = {}
    for src in SOURCES:
        con = sqlite3.connect(src_path(src, fx["td"]))
        raw[src] = {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in con.execute("SELECT query, vector FROM embeddings")}
        con.close()
    U = lambda A: A / np.linalg.norm(A, axis=1, keepdims=True)
    idx = {}
    for c in CORPORA:
        C = CS[c]
        idx[c] = {sd: [i for i in range(len(C.text)) if C.kept[i] and not C.oos[i] and C.side[i] == sd] for sd in (SS.TRAIN, SS.GATE, SS.EVAL)}

    def X(src, d, c, sd):
        C = CS[c]
        return U(np.array([raw[src][C.text[i]][:d] for i in idx[c][sd]]))
    # nomic selection on GATE
    gs = {}
    for d in NOMIC_SLICES:
        vals = []
        for c in CORPORA:
            C = CS[c]
            cms = [ITS.skmeans(X("n", d, c, SS.TRAIN), GK[c][1], s) for s in SEEDS_F]
            Xg = X("n", d, c, SS.GATE)
            vals.append(np.mean([NMI([C.fine[i] for i in idx[c][SS.GATE]], np.argmax(Xg @ Cm.T, 1)) for Cm in cms]))
        gs[d] = float(np.mean(vals))
    dstar = min(d for d in NOMIC_SLICES if gs[d] >= max(gs.values()) - 0.001)
    arm_sd = {a: ARM_SRC[a] for a in ARMS}
    arm_sd["n*"] = ("n", dstar)
    arm_sd["n@256"], arm_sd["n@512"] = ("n", 256), ("n", 512)
    nm, pred = {}, {}
    for a, (src, d) in arm_sd.items():
        for c in CORPORA:
            C = CS[c]
            Xt, Xe = X(src, d, c, SS.TRAIN), X(src, d, c, SS.EVAL)
            levs = [("fine", 1, [C.fine[i] for i in idx[c][SS.EVAL]], SEEDS_F)]
            if c in COARSE_C:
                levs.append(("coarse", 0, [C.coarse[i] for i in idx[c][SS.EVAL]], SEEDS_C if a in ARMS else SEEDS_F))
            for lev, k, truth, seeds in levs:
                ps = [np.argmax(Xe @ ITS.skmeans(Xt, GK[c][k], s).T, 1) for s in seeds]
                pred[(a, c, lev)] = ps
                nm[(a, c, lev)] = [NMI(truth, p) for p in ps]
    out = {"dstar": dstar, "gate_score": gs, "nm": nm, "coarse": {}, "fine": {}}
    for lev, corp in (("coarse", COARSE_C), ("fine", CORPORA)):
        for c in corp:
            C = CS[c]
            ev = idx[c][SS.EVAL]
            truth = np.unique([C.coarse[i] if lev == "coarse" else C.fine[i] for i in ev], return_inverse=True)[1]
            cc = np.unique(C.comp[ev], return_inverse=True)[1]
            G = int(cc.max()) + 1
            rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index(lev))
            draws = {a: [] for a in ARMS}
            for _ in range(B):
                w = np.bincount(rng.integers(G, size=G), minlength=G)[cc].astype(float)
                for a in ARMS:
                    draws[a].append(np.mean([_wnmi(truth, p, w) for p in pred[(a, c, lev)]]))
            for F, A, Bm in CONTRASTS:
                nA, nB = np.array(nm[(A, c, lev)]), np.array(nm[(Bm, c, lev)])
                Dd = float(nA.mean() - nB.mean())
                se = float(np.sqrt(np.std(np.array(draws[A]) - np.array(draws[Bm]), ddof=1) ** 2 + np.var(nA - nB, ddof=1) / len(nA)))
                if Dd - 1.645 * se > -MARGIN and Dd + 1.645 * se < MARGIN:
                    st = "EQUIVALENT"
                elif abs(Dd) > MARGIN and (Dd - 1.96 * se > 0 or Dd + 1.96 * se < 0):
                    st = "DIFFERENT"
                else:
                    st = "NEITHER"
                out[lev][(F, A, Bm, c)] = {"D": Dd, "se": se, "status": st}
    fam = {}
    for F in FAMILIES:
        sts = [v["status"] for k, v in out["coarse"].items() if k[0] == F]
        fam[F] = "INVARIANT" if all(s == "EQUIVALENT" for s in sts) else ("NOT-INVARIANT" if "DIFFERENT" in sts else "UNDETERMINED")
    out["fam"] = fam
    if all(v == "INVARIANT" for v in fam.values()):
        out["reading"] = "LEVEL"
    elif fam["DIM"] == "INVARIANT" and fam["QUANT"] == "INVARIANT" and fam["EMBEDDER"] == "NOT-INVARIANT":
        out["reading"] = "TRANSFORMATION"
    elif fam["DIM"] == "NOT-INVARIANT":
        out["reading"] = "NO-LEVEL-ADVANTAGE"
    else:
        out["reading"] = "MIXED"
    out["n"] = {c: len(idx[c][SS.EVAL]) for c in CORPORA}
    # H targets from the registered machinery (ITS.d2 + EDS.h_boot) on own-read spaces: a plumbing check, not an independent one
    out["H"] = {}
    with ITS.fixture_scope():
        for a in EDS_ARMS:
            src, d = ARM_SRC[a]
            for c in COARSE_C:
                vecs = {t: v[:max(d, 512)].astype(np.float32) for t, v in raw[src].items()}
                S = ITS.Space(vecs, CS[c], d)
                with contextlib.redirect_stdout(io.StringIO()):
                    r = ITS.d2(CS[c], S)
                    r.update(EDS.h_boot(CS[c], S, FX_B, EDS.SEED_H + CORPORA.index(c)))
                out["H"][(a, c)] = r
    del ITS.FIT_LOG[:]
    return out


def _id_files(fx):
    """Fixture identity CSVs in the record's formats, from the oracle's values (seeds 0-4)."""
    o = fx["oracle"]
    d = os.path.join(fx["td"], "idfiles")
    os.makedirs(d, exist_ok=True)
    files = {k: os.path.join(d, k + ".csv") for k in ID_FILES}
    nm = o["nm"]
    with open(files["nmi_matrix"], "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["embedder", "slice", "corpus", "level", "side", "seed", "nmi"])
        for a in EDS_ARMS:
            e, sl = ("gemma", 768) if a == "g768" else ("qwen3", ARM_SRC[a][1])
            for (aa, c, lev), vals in sorted(nm.items()):
                if aa == a:
                    for s in SEEDS_F:
                        w.writerow([e, sl, c, lev, "EVAL", s, "%.6f" % vals[s]])
    with open(files["nmi_q"], "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["arm", "model", "slice", "corpus", "level", "side", "seed", "nmi"])
        for a, lab in (("q1024", "q4"), ("q8", "q8")):
            for c in CORPORA:
                for s in SEEDS_F:
                    w.writerow([lab, "m", 1024, c, "fine", "EVAL", s, "%.6f" % nm[(a, c, "fine")][s]])
    with open(files["nmi_card"], "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["embedder", "protocol", "slice", "corpus", "level", "side", "seed", "nmi"])
        for a, e, prot, sl in (("q1024", "qwen3", "RAW", 1024), ("qcard", "qwen3", "CARD", 1024), ("g768", "gemma", "RAW", 768), ("gcard", "gemma", "CARD", 768)):
            for c in CORPORA:
                for s in SEEDS_F:
                    w.writerow([e, prot, sl, c, "fine", "EVAL", s, "%.6f" % nm[(a, c, "fine")][s]])
    with open(files["s0_c1"], "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["corpus", "level", "slice", "embedder", "seed", "nmi", "ari"])
        for sl in NOMIC_ID_SLICES:
            for (aa, c, lev), vals in sorted(nm.items()):
                if aa == "n@%d" % sl:
                    for s in SEEDS_F:
                        w.writerow([c, lev, sl, "nomic", s, "%.6f" % vals[s], "0"])
    with open(files["h_table"], "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["embedder", "slice", "corpus", "H", "lo", "hi", "random_p95", "dropped_labels"])
        for (a, c), h in sorted(o["H"].items()):
            e, sl = ("gemma", 768) if a == "g768" else ("qwen3", ARM_SRC[a][1])
            w.writerow([e, sl, c, "%.6f" % h["H"], "%.6f" % h["lo"], "%.6f" % h["hi"], "%.6f" % h["p95"], h["dropped"]])
    return files


@contextlib.contextmanager
def _scope(fx):
    """Fixture scope: S0's fixture K (4 / 16), the fixture's pins files, no heavy process, B FX_B (S0's too); restored."""
    g = globals()
    saved = (g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], PINS["q8"][0], PINS["card"][0], g["BOOT_B"], ITS.BOOT_B)
    g["_foreign_heavy"] = lambda: []
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"] if fx else None
        PINS["q8"][0] = fx["q8pins"] if fx else None
        PINS["card"][0] = fx["cardpins"] if fx else None
        g["BOOT_B"] = FX_B
        ITS.BOOT_B = FX_B
        try:
            yield
        finally:
            g["_foreign_heavy"], ITS.PINS_FILE_OVERRIDE[0], PINS["q8"][0], PINS["card"][0], g["BOOT_B"], ITS.BOOT_B = saved


def make_fixtures(td, names=None):
    out = {}
    for name in (names or FX_SPEC):
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


def _run(fx, tag, **kw):
    out_dir = os.path.join(fx["td"], "out_%s_%d" % (tag, len(os.listdir(fx["td"]))))
    args = dict(db=fx["db"], emb_dir=fx["td"], out_dir=out_dir, programme=fx["prog"], files=fx["files"], sel_path=fx["sel"], sel_sha=fx["sel_sha"],
                strict_blob=False)
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
            td = tempfile.mkdtemp(prefix="gle_st_")
            try:
                _selftest(sel, ok, td, make_fixtures(td))
            finally:
                shutil.rmtree(td, ignore_errors=True)
        else:
            _selftest(sel, ok, fixture[0], fixture[1])
    finally:
        reset()
    if not quiet:
        print("SELFTEST: %d checks passed" % n[0])
    return 0


def _syn_R(fam_st):
    """A synthetic readout for the line printers: per family the list of coarse statuses (in CONTRASTS x COARSE_C order)."""
    R = {"coarse": {}, "fine": {}}
    it = {F: iter(v) for F, v in fam_st.items()}
    for F, A, Bm in CONTRASTS:
        for c in COARSE_C:
            st = next(it[F])
            D = 0.03 if st == "DIFFERENT" else 0.0
            R["coarse"][(F, A, Bm, c)] = {"D": D, "status": st, "direction": "%s HIGHER" % A if st == "DIFFERENT" else "", "lo90": D - 0.01,
                                          "hi90": D + 0.01, "lo95": D - 0.012, "hi95": D + 0.012, "se": 0.006}
    R["fam"] = family_verdicts({k: v["status"] for k, v in R["coarse"].items()}, "coarse")
    R["reading"] = reading(R["fam"])
    R["fgl"], R["moved"], R["fgl2"] = falsifiers(R["fam"])
    return R


def _gl1_print(R):
    """gl1_lines on a synthetic R (the NMI means are not part of the branch under test)."""
    for (F, A, Bm, c) in R["coarse"]:
        for a in (A, Bm):
            STORE["nm"].setdefault((a, c, "coarse"), [0.5])
    return "\n".join(gl1_lines(R))


def _selftest(sel, ok, td, FX):
    E, DF, NE = "EQUIVALENT", "DIFFERENT", "NEITHER"
    if sel("ST-CONST"):
        ok(MARGIN == 0.025 and MARGIN_SENS == 0.05 and (Z90, Z95, Z80P) == (1.645, 1.96, 0.842), "margin 0.025 (sensitivity 0.05), z 1.645 / 1.96 / 0.842")
        ok(SEEDS_C == tuple(range(30)) and SEEDS_F == (0, 1, 2, 3, 4) and BOOT_B == 2000, "coarse seeds 0-29, fine 0-4, B 2,000")
        ok(COARSE_C == ("massive", "clinc") and CORPORA == ("massive", "clinc", "banking77") and NOMIC_SLICES == (256, 512, 768), "corpora and nomic slices")
        ok([(F, A, Bm) for F, A, Bm in CONTRASTS] == [("DIM", "q256", "q1024"), ("DIM", "q512", "q1024"), ("DIM", "q4096", "q1024"), ("QUANT", "q8", "q1024"),
                                                      ("PROMPT", "qcard", "q1024"), ("PROMPT", "gcard", "g768"), ("EMBEDDER", "g768", "q1024"),
                                                      ("EMBEDDER", "n*", "q1024")], "the 8 registered contrasts")
        ok(ARM_SRC["q8"] == ("q8", 1024) and ARM_SRC["qcard"] == ("qcard", 1024) and ARM_SRC["gcard"] == ("gcard", 768) and ARM_SRC["q4096"] == ("q4", 4096),
           "arm slices as registered")
        ok(all(RO.git_blob_lf(m.__file__) == b for b, m in BLOBS.values()), "the four imported readers at their registered blobs")
        ok(EDS.TIE == 0.001 and SEL_SHA.startswith("f1b508cf") and NMI_MATRIX_BLOB.startswith("1056bad9"), "tie 0.001; selection and nmi_matrix pins")
        ok(abs(sum(P3.values()) - 1.0) < 1e-9 and P1[("q256", "massive")] == (-0.045, -0.065, -0.025, True) and P1[("n*", "clinc")] == (-0.065, -0.100, -0.030, False),
           "registered P1 / P3 values")
        ok(EQ.status(0.0, MARGIN, -0.01, 0.01, -0.012, 0.012) == E, "EQ.status is the TOST form")
    if sel("ST-UNIT"):
        st = {"DIM": [E] * 6, "QUANT": [E] * 2, "PROMPT": [E] * 4, "EMBEDDER": [E] * 4}
        cases = [(st, {"DIM": "INVARIANT", "QUANT": "INVARIANT", "PROMPT": "INVARIANT", "EMBEDDER": "INVARIANT"}, "LEVEL", False, True),
                 (dict(st, EMBEDDER=[E, E, DF, NE]), None, "TRANSFORMATION", True, False),
                 (dict(st, DIM=[E, E, E, E, E, DF]), None, "NO-LEVEL-ADVANTAGE", True, True),
                 (dict(st, DIM=[E, NE, E, E, E, E]), None, "MIXED", False, True),
                 (dict(st, QUANT=[E, NE], EMBEDDER=[DF, E, E, E]), None, "MIXED", True, False),
                 (dict(st, DIM=[DF, NE, E, E, E, E], EMBEDDER=[DF, E, E, E]), None, "NO-LEVEL-ADVANTAGE", True, False),
                 (dict(st, PROMPT=[E, E, E, DF]), None, "MIXED", True, True),
                 (dict(st, DIM=[NE] * 6, EMBEDDER=[DF] * 4), None, "MIXED", True, False),
                 (dict(st, EMBEDDER=[E, NE, E, E]), None, "MIXED", False, False)]
        for fst, want_fam, want_r, fgl, fgl2 in cases:
            R = _syn_R(fst)
            if want_fam:
                ok(R["fam"] == want_fam, "families %s" % want_fam)
            ok(R["reading"] == want_r, "reading %s for %s" % (want_r, {k: v for k, v in fst.items() if v != st[k]}))
            txt = _gl1_print(R)
            ok(("READING: %s: %s" % (want_r, SENTENCE[want_r])) in txt, "printed READING %s with its sentence" % want_r)
            ok(("F-GL: FIRED" in txt) == fgl and ("F-GL: NOT FIRED" in txt) == (not fgl), "F-GL %s printed" % fgl)
            ok(("F-GL': FIRED" in txt) == fgl2 and ("F-GL': NOT FIRED" in txt) == (not fgl2), "F-GL' %s printed" % fgl2)
            for F in FAMILIES:
                ok(("FAMILY %s: %s (" % (F, R["fam"][F])) in txt, "FAMILY %s %s printed" % (F, R["fam"][F]))
            if fgl:
                ok(("name the family that moved (%s)" % ", ".join(R["moved"])) in txt, "F-GL names the families that moved %s" % R["moved"])
        R = _syn_R(dict(st, DIM=[E, E, E, NE, E, E]))
        ok(R["fam"]["DIM"] == "UNDETERMINED", "UNDETERMINED: a NEITHER and no DIFFERENT")
        o, err, _r = _cap(lambda: family_verdicts({("DIM", "a", "b", "massive"): E}, "coarse"))
        ok(err and "holds 1 statuses, registered 6" in err, "a family with the wrong status count REFUSES (both corpora required)")
        ok(EQ.status(0.0244, MARGIN, 0.0244 - 1e-4, 0.0244 + 1e-4, 0.024, 0.0249) == E and EQ.status(0.0251, MARGIN, 0.025, 0.0252, 0.0249, 0.0253) == DF,
           "TOST boundaries at 0.025")
        ok(EQ.status(0.026, MARGIN, 0.0, 0.052, -0.004, 0.056) == NE, "|D| > 0.025 but the 95% interval reaches 0 -> NEITHER")
        r = {"eq_reach": 0.025 - 2.487 * 0.0064, "diff_reach": 0.025 + 0.842 * 0.0064}
        ok(verdict_line(-0.045, r) == "SCOREABLE (DIFFERENT side)" and verdict_line(-0.030, r) == "DESCRIPTIVE-ONLY" and verdict_line(0.003, r) == "SCOREABLE (EQUIVALENT side)",
           "verdict lines at the planned SE (MASSIVE q256 / q512 / q8 as registered)")
        ok(_hit(0.01, 0.0, 0.01) and not _hit(0.0101, 0.0, 0.01) and abs(brier(0.65, np.bool_(True)) - 0.1225) < 1e-12, "closed interval; Brier on numpy bool")
        reset()
        C = type("C", (), {"name": "massive", "idx": lambda self, side, oos=False: np.array([], dtype=int)})()
        S = type("S", (), {"d": 256, "have": np.array([], dtype=bool)})()
        o, err, _r = _cap(lambda: eval_idx(C, S, "n", "probe"))
        ok(err and "before the GATE selection file" in err, "a nomic EVAL read before the selection file REFUSES (GB2)")
        ok(EDS.pick({256: 0.5, 512: 0.5009, 768: 0.4}) == (256, 0.5009) and EDS.pick({256: 0.5, 512: 0.502, 768: 0.4})[0] == 512, "EDS.pick: tie to the smaller d")
        Rw = {"q256": np.array([[0.5, 0.6], [0.4, 0.5], [0.45, 0.62]]), "q1024": np.array([[0.5, 0.52], [0.47, 0.49], [0.44, 0.40]])}
        reset()
        STORE["nm"][("q256", "massive", "coarse")] = [0.55, 0.45]
        STORE["nm"][("q1024", "massive", "coarse")] = [0.52, 0.47]
        g = globals()
        saved = g["SEEDS_F"]
        g["SEEDS_F"] = (0, 1)
        try:
            r = contrast("massive", "coarse", "q256", "q1024", Rw)
        finally:
            g["SEEDS_F"] = saved
        dw_ = [0.55 - 0.51, 0.45 - 0.48, 0.535 - 0.42]
        ok(abs(r["D"] - 0.005) < 1e-12 and abs(r["se_boot"] - np.std(dw_, ddof=1)) < 1e-12 and abs(r["var_seed"] - np.var([0.03, -0.02], ddof=1)) < 1e-12,
           "contrast: D, paired SE_boot (ddof 1, per-draw A - B), var_seed of the per-seed differences")
        ok(abs(r["se"] - np.sqrt(r["se_boot"] ** 2 + r["var_seed"] / 2)) < 1e-12, "SE_total = sqrt(SE_boot^2 + var_seed / n_seeds)")
        Wd = {"q256": np.array([[0.512, 0.512], [0.52, 0.52], [0.528, 0.528]]), "q1024": np.array([[0.5, 0.5]] * 3)}
        STORE["nm"][("q256", "massive", "coarse")] = [0.52, 0.52]
        STORE["nm"][("q1024", "massive", "coarse")] = [0.5, 0.5]
        g["SEEDS_F"] = (0, 1)
        try:
            r2 = contrast("massive", "coarse", "q256", "q1024", Wd)
        finally:
            g["SEEDS_F"] = saved
        ok(abs(r2["D"] - 0.02) < 1e-12 and abs(r2["se"] - 0.008) < 1e-12 and r2["status"] == NE,
           "contrast: |D| 0.020 <= 0.025 with the 95% interval [+0.0043, +0.0357] off 0 -> NEITHER (the point clause decides)")
        We = {"q256": np.array([[0.502, 0.502], [0.51, 0.51], [0.518, 0.518]]), "q1024": np.array([[0.5, 0.5]] * 3)}
        STORE["nm"][("q256", "massive", "coarse")] = [0.51, 0.51]
        g["SEEDS_F"] = (0, 1)
        try:
            r3 = contrast("massive", "coarse", "q256", "q1024", We)
        finally:
            g["SEEDS_F"] = saved
        ok(abs(r3["se"] - 0.008) < 1e-12 and r3["status"] == E, "contrast: D 0.010, SE 0.008: 90% [-0.0032, +0.0232] inside -> EQUIVALENT (95% would not be)")
        reset()
    if sel("ST-PRED"):
        reset()
        st = {"DIM": [DF, E, E, E, E, E], "QUANT": [E, E], "PROMPT": [E] * 4, "EMBEDDER": [DF, E, E, E]}
        R = _syn_R(st)
        R["coarse"][("DIM", "q256", "q1024", "massive")]["D"] = -0.025                  # on the closed P1 boundary [-0.065, -0.025]
        R["coarse"][("EMBEDDER", "g768", "q1024", "massive")]["D"] = 0.106              # just outside [+0.065, +0.105]
        R["fine"] = {(F, A, Bm, c): {"status": E} for F, A, Bm in CONTRASTS for c in CORPORA}
        R["fine"][("EMBEDDER", "g768", "q1024", "massive")]["status"] = DF            # DIFFERENT on MASSIVE only: P4b event False
        for a in ARMS:
            for c in COARSE_C:
                STORE["H"][(a, c)] = {"H": 0.5}
        STORE["H"][("g768", "massive")]["H"] = 0.9
        STORE["H"][("q4096", "massive")]["H"] = 0.95                                   # P5a False via the last slice only
        STORE["H"][("q8", "clinc")]["H"] = 0.53                                        # P5b False via CLINC only
        P = "\n".join(predictions_lines(R))
        ok("P1 q256 - q1024 massive: D -0.02500 vs -0.045 [-0.065, -0.025]: HELD (SEEN: never a confirmation)" in P, "P1 HELD on the closed boundary, SEEN marked")
        ok("P1 g768 - q1024 massive: D +0.10600 vs +0.085 [+0.065, +0.105]: FAILED (SEEN" in P, "P1 FAILED just outside")
        ok("P1 q8 - q1024 clinc: D +0.00000 vs +0.003 [-0.007, +0.010]: HELD\n" in P + "\n" and "P1 q8 - q1024 clinc: D +0.00000 vs +0.003 [-0.007, +0.010]: HELD (SEEN" not in P,
           "P1 HELD, not SEEN for a new contrast")
        ok("P2 DIM NOT-INVARIANT: Brier NOT-INVARIANT 0.1225, UNDETERMINED 0.0900, INVARIANT 0.0025" in P, "P2 DIM Briers per outcome")
        ok("P2 QUANT INVARIANT: Brier INVARIANT 0.0625" in P and "P2 EMBEDDER NOT-INVARIANT: Brier NOT-INVARIANT 0.0100" in P, "P2 QUANT / EMBEDDER Briers")
        ok("P3 reading NO-LEVEL-ADVANTAGE: Brier LEVEL 0.0009, TRANSFORMATION 0.0225, NO-LEVEL-ADVANTAGE 0.1225, MIXED 0.0289 (sum 0.1748); F-GL fires True: p 0.95, Brier 0.0025" in P,
           "P3 reading and F-GL Briers")
        ok("P4 fine DIM statuses all EQUIVALENT (9): event True" in P and "P4 fine g768 - q1024 DIFFERENT on MASSIVE and Banking77: event False" in P,
           "P4 events (the second needs BOTH corpora)")
        ok("P5 H(g768) > H(q) at every qwen3 slice on MASSIVE: event False" in P and "P5 |H(q8) - H(q1024)| <= 0.02 on both corpora: event False" in P,
           "P5 events (every slice; both corpora)")
        STORE["H"][("q4096", "massive")]["H"] = 0.5
        STORE["H"][("q8", "clinc")]["H"] = 0.515
        R["fine"][("EMBEDDER", "g768", "q1024", "banking77")]["status"] = DF
        R["fine"][("DIM", "q512", "q1024", "banking77")]["status"] = NE
        P = "\n".join(predictions_lines(R))
        ok("P5 H(g768) > H(q) at every qwen3 slice on MASSIVE: event True" in P and "P5 |H(q8) - H(q1024)| <= 0.02 on both corpora: event True" in P,
           "P5 events True (|Delta H| 0.015 <= 0.02)")
        ok("P4 fine DIM statuses all EQUIVALENT (9): event False" in P and "P4 fine g768 - q1024 DIFFERENT on MASSIVE and Banking77: event True" in P,
           "P4 events flip (one fine DIM NEITHER; both corpora DIFFERENT)")
        reset()
    # ---------------------------------------------------------------- end-to-end on the fixtures
    for name in FX_SPEC:
        key = "ST-E2E-" + name
        if not sel(key):
            continue
        fx = FX[name]
        orc = fx["oracle"]
        o, err, res, out_dir = _run(fx, "e2e")
        ok(err is None, "%s: --run completes (%s)" % (name, err))
        R, L, po = res
        txt = open(po, encoding="utf-8").read()
        ok(txt.splitlines() == L, "%s: the file of record is the printed lines" % name)
        ok(STORE["dstar"] == orc["dstar"], "%s: d_n* %d = oracle %d (GATE rule)" % (name, STORE["dstar"], orc["dstar"]))
        for k, r in R["coarse"].items():
            q = orc["coarse"][k]
            ok(abs(r["D"] - q["D"]) < 1e-12 and abs(r["se"] - q["se"]) < 1e-9 and r["status"] == q["status"],
               "%s GL1 %s: D %+.5f SE %.5f %s = oracle (%+.5f %.5f %s)" % (name, k[1:], r["D"], r["se"], r["status"], q["D"], q["se"], q["status"]))
            ln = [x for x in L if x.startswith("GL1 %s %s - %s %s: " % k)]
            ok(len(ln) == 1 and ln[0].startswith("GL1 %s %s - %s %s: %s" % (k + (q["status"],))) and ("D %+.5f;" % q["D"]) in ln[0],
               "%s printed GL1 %s value" % (name, k[1:]))
        for k, r in R["fine"].items():
            q = orc["fine"][k]
            ok(abs(r["D"] - q["D"]) < 1e-12 and abs(r["se"] - q["se"]) < 1e-9 and r["status"] == q["status"], "%s GL2 %s = oracle" % (name, k[1:]))
        ok(R["fam"] == orc["fam"], "%s families %s = oracle" % (name, orc["fam"]))
        ok(R["reading"] == orc["reading"] and ("READING: %s: " % orc["reading"]) in txt, "%s READING %s printed" % (name, orc["reading"]))
        ok(("F-GL: FIRED" in txt) == any(v == "NOT-INVARIANT" for v in orc["fam"].values()), "%s F-GL printed per the oracle" % name)
        ok(("F-GL': FIRED" in txt) == (orc["fam"]["EMBEDDER"] == "INVARIANT"), "%s F-GL' printed per the oracle" % name)
        for need in ("IDENTITY source q4", "IDENTITY source q8", "IDENTITY source qcard", "IDENTITY source g", "IDENTITY source gcard",
                     "IDENTITY nomic 256 / 512", "NOMIC SELECTION: d_n* = %d" % orc["dstar"], "== GL2", "== GL3", "== PRINTED BESIDE",
                     "== PREDICTIONS", "P5 |H(q8) - H(q1024)|", "P4 fine DIM", "P3 reading", "WHAT THIS RESULT WILL NOT SHOW", "builder's readings: GB1"):
            ok(need in txt, "%s outcome carries %r" % (name, need))
        ok(txt.count("-> REPRODUCED") == 6, "%s six identity lines REPRODUCED" % name)
        ok(", 0 with an EVAL row, 0 OOS rows" in txt, "%s fit audit: no EVAL / OOS row in any fit" % name)
        ev = [i for i, e in enumerate(EVENTS) if e[0] == "EVAL" and e[1] == "n"]
        sl = [i for i, e in enumerate(EVENTS) if e[0] == "SELECTION"]
        ok(len(sl) == 1 and ev and min(ev) > sl[0], "%s: the selection precedes every nomic EVAL read (GB2)" % name)
        ok(all(len(STORE["nm"][(a, c, "coarse")]) == 30 for a in ARMS for c in COARSE_C) and all(len(STORE["nm"][(a, c, "fine")]) == 5 for a in ARMS for c in CORPORA),
           "%s: 30 coarse seeds and 5 fine seeds per arm" % name)
        ok(("massive", "coarse") in STORE["truth"] and ("banking77", "coarse") not in STORE["truth"], "%s: no coarse level on Banking77" % name)
        ok(all(len(STORE["evrows"][c]) == orc["n"][c] for c in CORPORA), "%s: EVAL in-scope rows (OOS excluded) = oracle %s" % (name, orc["n"]))
        ok(sum(1 for f in ITS.FIT_LOG if f[0].startswith("GL coarse") and f[0].split()[2].split("@")[0] in ARMS) == 9 * 2 * 30,
           "%s: 540 coarse TRAIN fits of the 9 arms" % name)
        with open(os.path.join(out_dir, CSVS[0]), encoding="utf-8") as fh:
            rows_ = list(csv.DictReader(fh))
        ok(sum(1 for r in rows_ if r["level"] == "coarse" and r["arm"] == "n*") == 60, "%s nmi_gold.csv carries n* coarse 2 x 30" % name)
        ok(os.path.isfile(os.path.join(out_dir, SELECTION)) and json.load(open(os.path.join(out_dir, SELECTION)))["d_n*"] == orc["dstar"], "%s selection file" % name)
        o2, err2, _r2, _d = _run(fx, "again", out_dir=out_dir)
        ok(err2 and "write-once" in err2, "%s: a second --run into the same directory REFUSES" % name)
        if name == "A":
            ok(orc["dstar"] == 768, "A: GATE picks 768 (EVAL alone would not: its band is noise on EVAL)")
            ok(orc["coarse"][("DIM", "q256", "q1024", "clinc")]["status"] == DF and orc["coarse"][("DIM", "q256", "q1024", "massive")]["status"] == E,
               "A: q256 DIFFERENT on CLINC only (the family is decided by one corpus)")
            ok(R["reading"] == "NO-LEVEL-ADVANTAGE" and R["fam"]["QUANT"] == "INVARIANT", "A: planted NO-LEVEL-ADVANTAGE, QUANT INVARIANT")
        if name == "B":
            ok(R["reading"] == "TRANSFORMATION" and orc["coarse"][("EMBEDDER", "n*", "q1024", "clinc")]["status"] != DF
               and orc["coarse"][("EMBEDDER", "n*", "q1024", "massive")]["status"] == DF, "B: planted TRANSFORMATION, EMBEDDER via MASSIVE alone")
        if name == "C":
            ok(R["reading"] == "LEVEL" and "F-GL': FIRED" in txt and orc["dstar"] == 256, "C: planted LEVEL, F-GL' FIRED, nomic tie -> 256")
    if sel("ST-REFUSE"):
        fx = FX["C"]
        f2 = dict(fx["files"])
        bad = os.path.join(fx["td"], "bad_q.csv")
        rows_ = _read_csv(fx["files"]["nmi_q"])
        rows_[-1]["nmi"] = "%.6f" % (float(rows_[-1]["nmi"]) + 1e-4)
        with open(bad, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows_)
        f2["nmi_q"] = bad
        o, err, _r, d = _run(fx, "idq", files=f2)
        ok(err and "IDENTITY PRECONDITION FAILED (source q8)" in err and not os.path.exists(os.path.join(d, OUTCOME)), "q8 identity off by 1e-4 on the last seed REFUSES")
        bad2 = os.path.join(fx["td"], "bad_h.csv")
        rows_ = _read_csv(fx["files"]["h_table"])
        rows_[0]["hi"] = "%.6f" % (float(rows_[0]["hi"]) + 1e-3)
        with open(bad2, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows_)
        o, err, _r, d = _run(fx, "idh", files=dict(fx["files"], h_table=bad2))
        ok(err and "H " in err and "IDENTITY PRECONDITION FAILED" in err, "an H interval off by 1e-3 REFUSES")
        bad3 = os.path.join(fx["td"], "bad_n.csv")
        rows_ = _read_csv(fx["files"]["s0_c1"])
        for r in rows_:
            if r["slice"] == "512" and r["level"] == "coarse" and r["seed"] == "4":
                r["nmi"] = "0.000000"
        with open(bad3, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows_)
        o, err, _r, d = _run(fx, "idn", files=dict(fx["files"], s0_c1=bad3))
        ok(err and "nomic" in err and os.path.exists(os.path.join(d, SELECTION)) and not os.path.exists(os.path.join(d, OUTCOME)),
           "a nomic 512 coarse identity miss REFUSES after the selection file; no outcome")
        prog2 = os.path.join(fx["td"], "prog_quoted.md")
        with open(prog2, "w", encoding="utf-8") as fh:
            fh.write("a quotation: %s\n" % REG_HEADING)
        o, err, _r, _d = _run(fx, "noreg", programme=prog2)
        ok(err and "registration heading is absent" in err, "a quoted (not line-anchored) heading REFUSES")
        cp2 = os.path.join(fx["td"], "card_null.json")
        js = json.load(open(fx["cardpins"]))
        js["gemma_card"] = None
        json.dump(js, open(cp2, "w"))
        o, err, _r, _d = _run(dict(fx, cardpins=cp2), "nullcard")
        ok(err and "UNPINNED" in err, "--run REFUSES a null CARD pin")
        qp2 = os.path.join(fx["td"], "q8_bad.json")
        json.dump({"schema": EQ.PINS_SCHEMA, "q8": "0" * 64}, open(qp2, "w"))
        o, err, _r, _d = _run(dict(fx, q8pins=qp2), "badq8")
        ok(err and "pinned" in err, "--run REFUSES a different Q8 pin")
        o, err, _r, _d = _run(fx, "badsel", sel_sha="0" * 64)
        ok(err and "selection.json sha256" in err, "--run REFUSES another selection.json")
        o, err, _r, _d = _run(fx, "blob", strict_blob=True)
        ok(err and "nmi_matrix.csv is blob" in err, "--run REFUSES an nmi_matrix.csv that is not blob 1056bad9")
        g = globals()
        saved = g["_foreign_heavy"]
        with _scope(fx):
            g["_foreign_heavy"] = lambda: ["java.exe 1"]
            try:
                o, err, _r = _cap(lambda: main_run(db=fx["db"], emb_dir=fx["td"], out_dir=os.path.join(fx["td"], "heavy_%d" % len(os.listdir(fx["td"]))), programme=fx["prog"],
                                                   files=fx["files"], sel_path=fx["sel"], sel_sha=fx["sel_sha"], strict_blob=False))
            finally:
                g["_foreign_heavy"] = saved
        ok(err and "foreign heavy process" in err, "--run REFUSES beside a JVM")
    if sel("ST-DRY"):
        fx = FX["A"]
        with _scope(fx):
            o, err, _r = _cap(lambda: dry_run(db=fx["db"], emb_dir=fx["td"], programme=fx["prog"], files=fx["files"], sel_path=fx["sel"],
                                              sel_sha=fx["sel_sha"], timing=True, identity=True))
        ok(err is None, "dry-run (timing + identity) completes (%s)" % err)
        ok("DENOMINATORS vs registration Support (a): DIFFERENT" in o and "TIMING:" in o and "PRICE about" in o, "dry-run prints denominators and the price")
        ok(o.count("-> REPRODUCED") == 5 and "IDENTITY nomic" not in o, "dry-run identity on the 5 non-nomic sources")
        ok(not any(e[1] == "n" for e in EVENTS if e[0] == "EVAL"), "dry-run reads no nomic EVAL row")
        ok(not any(("q8", c, "coarse") in STORE["nm"] or ("qcard", c, "coarse") in STORE["nm"] or ("gcard", c, "coarse") in STORE["nm"] for c in COARSE_C),
           "dry-run computes no coarse value of q8 / qcard / gcard (new data)")
        ok(all(len(STORE["nm"][(a, c, "coarse")]) == 5 for a in EDS_ARMS for c in COARSE_C), "dry-run coarse identity on seeds 0-4 only")
        ok(not any(os.path.exists(os.path.join(fx["td"], n)) for n in (SELECTION, OUTCOME) + CSVS), "dry-run writes nothing")


MUTANTS = (
    ("margin 0.05", "MARGIN = 0.025\n", "MARGIN = 0.05\n", ("ST-CONST",)),
    ("margin read as a seed spread", "    st = EQ.status(D, m, lo90, hi90, lo95, hi95)\n",
     "    st = EQ.status(D, max(float(nA.max() - nA.min()), float(nB.max() - nB.min())), lo90, hi90, lo95, hi95)\n", ("ST-E2E-A", "ST-E2E-B", "ST-E2E-C")),
    ("coarse seeds 0-4 (not 30)", "SEEDS_C = tuple(range(30))\n", "SEEDS_C = tuple(range(5))\n", ("ST-CONST",)),
    ("seed term over 5 not 30 coarse seeds", "    se = float(np.sqrt(se_boot ** 2 + var_seed / ns))\n", "    se = float(np.sqrt(se_boot ** 2 + var_seed / 5))\n", ("ST-E2E-A", "ST-E2E-B")),
    ("seed term dropped", "    se = float(np.sqrt(se_boot ** 2 + var_seed / ns))\n", "    se = float(np.sqrt(se_boot ** 2))\n", ("ST-UNIT",)),
    ("var_seed of the arms (not the per-seed differences)", "    var_seed = float(np.var(nA - nB, ddof=1))\n", "    var_seed = float(np.var(nA, ddof=1) + np.var(nB, ddof=1))\n", ("ST-UNIT", "ST-E2E-B")),
    ("unpaired bootstrap (A draws minus B point)", "    dw = W[A].mean(1) - W[Bm].mean(1)\n", "    dw = W[A].mean(1) - nB.mean()\n", ("ST-UNIT", "ST-E2E-B")),
    ("unpaired weights (fresh stream per arm)", "    for b, w in enumerate(ITS.comp_weights(comp, B, rng)):\n        for a in arms:\n",
     "    for b, w in enumerate(ITS.comp_weights(comp, B, rng)):\n        for a in arms:\n            w = np.random.default_rng(b + len(a)).permutation(w)\n", ("ST-E2E-A", "ST-E2E-B")),
    ("bootstrap stream of the fine level for coarse", "    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + LEVELS[c].index(level))\n    W = {a",
     "    rng = np.random.default_rng(BOOT_SEED + 10 * CORPORA.index(c) + 1)\n    W = {a", ("ST-E2E-A", "ST-E2E-B")),
    ("DIFFERENT point clause dropped (own TOST)", "    st = EQ.status(D, m, lo90, hi90, lo95, hi95)\n",
     "    st = \"EQUIVALENT\" if (lo90 > -m and hi90 < m) else (\"DIFFERENT\" if (lo95 > 0 or hi95 < 0) else \"NEITHER\")\n", ("ST-E2E-A", "ST-E2E-B", "ST-E2E-C")),
    ("EQUIVALENT at 95%", "    lo90, hi90, lo95, hi95 = D - Z90 * se, D + Z90 * se, D - Z95 * se, D + Z95 * se\n    st = EQ",
     "    lo90, hi90, lo95, hi95 = D - Z95 * se, D + Z95 * se, D - Z95 * se, D + Z95 * se\n    st = EQ", ("ST-UNIT", "ST-E2E-A", "ST-E2E-B", "ST-E2E-C")),
    ("family verdict from one corpus", "        sts = [v for (f, _a, _b, _c), v in stat.items() if f == F]\n",
     "        sts = [v for (f, _a, _b, _c), v in stat.items() if f == F and _c != \"clinc\"]\n", ("ST-E2E-A",)),
    ("family verdict from CLINC only", "        sts = [v for (f, _a, _b, _c), v in stat.items() if f == F]\n",
     "        sts = [v for (f, _a, _b, _c), v in stat.items() if f == F and _c != \"massive\"]\n", ("ST-E2E-B",)),
    ("family count check dropped (+ one corpus)", "        if len(sts) != FAMILY_N[level][F]:\n", "        if False:\n", ("ST-UNIT",)),
    ("INVARIANT on any EQUIVALENT", "        if all(s == \"EQUIVALENT\" for s in sts):\n            out[F] = \"INVARIANT\"\n",
     "        if any(s == \"EQUIVALENT\" for s in sts) and not any(s == \"DIFFERENT\" for s in sts):\n            out[F] = \"INVARIANT\"\n", ("ST-UNIT",)),
    ("NOT-INVARIANT needs all DIFFERENT", "        elif any(s == \"DIFFERENT\" for s in sts):\n            out[F] = \"NOT-INVARIANT\"\n",
     "        elif all(s == \"DIFFERENT\" for s in sts):\n            out[F] = \"NOT-INVARIANT\"\n", ("ST-UNIT",)),
    ("reading order: NO-LEVEL-ADVANTAGE before TRANSFORMATION", "    if fam[\"DIM\"] == \"INVARIANT\" and fam[\"QUANT\"] == \"INVARIANT\" and fam[\"EMBEDDER\"] == \"NOT-INVARIANT\":\n        return \"TRANSFORMATION\"\n    if fam[\"DIM\"] == \"NOT-INVARIANT\":\n        return \"NO-LEVEL-ADVANTAGE\"\n",
     "    if fam[\"DIM\"] != \"INVARIANT\":\n        return \"NO-LEVEL-ADVANTAGE\"\n    if fam[\"DIM\"] == \"INVARIANT\" and fam[\"QUANT\"] == \"INVARIANT\" and fam[\"EMBEDDER\"] == \"NOT-INVARIANT\":\n        return \"TRANSFORMATION\"\n", ("ST-UNIT",)),
    ("TRANSFORMATION ignores QUANT", "    if fam[\"DIM\"] == \"INVARIANT\" and fam[\"QUANT\"] == \"INVARIANT\" and fam[\"EMBEDDER\"] == \"NOT-INVARIANT\":\n",
     "    if fam[\"DIM\"] == \"INVARIANT\" and fam[\"EMBEDDER\"] == \"NOT-INVARIANT\":\n", ("ST-UNIT",)),
    ("F-GL' on EMBEDDER NOT-INVARIANT", "    return bool(moved), moved, bool(fam[\"EMBEDDER\"] == \"INVARIANT\")\n", "    return bool(moved), moved, bool(fam[\"EMBEDDER\"] != \"NOT-INVARIANT\")\n", ("ST-UNIT",)),
    ("F-GL identity-tested (numpy bool never fires)", "    if R[\"fgl\"]:\n        L.append(\"F-GL: FIRED", "    if R[\"fgl\"] is np.True_:\n        L.append(\"F-GL: FIRED", ("ST-UNIT",)),
    ("F-GL names only the first family", "prompt and embedder here; SQ5's reconciliation must name the family that moved (%s), not the level\" % (\", \".join(R[\"moved\"]), \", \".join(R[\"moved\"])))",
     "prompt and embedder here; SQ5's reconciliation must name the family that moved (%s), not the level\" % (\", \".join(R[\"moved\"]), R[\"moved\"][0]))", ("ST-UNIT",)),
    ("OOS rows in the coarse readout", "    ev = ITS.S_idx(C, S, SS.EVAL)\n    if C.name in STORE",
     "    ev = np.concatenate([ITS.S_idx(C, S, SS.EVAL), ITS.S_idx(C, S, SS.EVAL, oos=True)])\n    if C.name in STORE", ("ST-E2E-C",)),
    ("EVAL in a fit (coarse k-means on TRAIN + EVAL)", "        preds = [ITS.assign(S.X[ev], ITS.km_fit(C, S, kc, s, \"GL coarse %s@%d %s K=%d s%d\" % (arm, S.d, c, kc, s))) for s in coarse_seeds]\n",
     "        preds = [ITS.assign(S.X[ev], ITS.skmeans(S.X[np.concatenate([ITS.S_idx(C, S, SS.TRAIN), ev])], kc, s)) for s in coarse_seeds]\n", ("ST-E2E-C",)),
    ("EVAL through fit_rows", "            fits[(d, c)] = [ITS.km_fit(C, S, kf, s, \"GL nomic fine @%d %s K=%d s%d\" % (d, c, kf, s)) for s in SEEDS_F]\n",
     "            fits[(d, c)] = [ITS.skmeans(S.X[ITS.fit_rows(C, np.concatenate([ITS.S_idx(C, S, SS.TRAIN), ITS.S_idx(C, S, SS.EVAL)]), (SS.TRAIN, SS.EVAL), 'x')], kf, s) for s in SEEDS_F]\n", ("ST-E2E-C",)),
    ("nomic selection on EVAL", "            gi = ITS.S_idx(C, S, SS.GATE)\n            truth = ITS.codes(C.fine[gi])\n            gate[(d, c)]",
     "            gi = ITS.S_idx(C, S, SS.EVAL)\n            truth = ITS.codes(C.fine[gi])\n            gate[(d, c)]", ("ST-E2E-A",)),
    ("nomic selection: plain argmax (no tie rule)", "    dstar, best = EDS.pick(score)\n", "    dstar, best = max(score, key=lambda d: (score[d], d)), max(score.values())\n", ("ST-E2E-C",)),
    ("nomic EVAL before the selection (gate off, order swapped)", "            write_selection(os.path.join(out_dir, SELECTION), dstar, score, gate, sha0)\n            nomic_eval(CS, vecs, fits, dstar)\n",
     "            PHASE[\"nomic_sel\"] = \"x\"\n            nomic_eval(CS, vecs, fits, dstar)\n            write_selection(os.path.join(out_dir, SELECTION), dstar, score, gate, sha0)\n", ("ST-E2E-C",)),
    ("EVAL gate disabled", "    if src == \"n\" and PHASE[\"nomic_sel\"] is None:\n", "    if False:\n", ("ST-UNIT",)),
    ("n* fixed at 256 (selection ignored)", "        arm = \"n*\" if d == dstar else \"n@%d\" % d\n", "        arm = \"n*\" if d == 256 else \"n@%d\" % d\n", ("ST-E2E-A",)),
    ("q8 read as the Q4 file", "    if src == \"q8\":\n        return EQ.load_slice(p, \"q8\", texts)\n", "    if src == \"q8\":\n        return EDS.load_full(src_path(\"q4\", emb_dir), \"qwen3\", texts)\n", ("ST-E2E-A",)),
    ("gcard vs q1024 (wrong baseline)", "(\"PROMPT\", \"gcard\", \"g768\"), (\"EMBEDDER\", \"g768\", \"q1024\"), (\"EMBEDDER\", \"n*\", \"q1024\"))\n",
     "(\"PROMPT\", \"gcard\", \"q1024\"), (\"EMBEDDER\", \"g768\", \"q1024\"), (\"EMBEDDER\", \"n*\", \"q1024\"))\n", ("ST-CONST",)),
    ("identity checks seed 0 only", "        for v in vals:\n            n += 1\n", "        for v in vals[:1] if s == 0 else []:\n            n += 1\n", ("ST-REFUSE",)),
    ("identity skips H", "        for k_csv, k in ((\"H\", \"H\"), (\"lo\", \"lo\"), (\"hi\", \"hi\"), (\"random_p95\", \"p95\")):\n",
     "        for k_csv, k in ((\"H\", \"H\"),):\n", ("ST-REFUSE",)),
    ("identity tolerance 1e-3", "ID_TOL = 5e-6\n", "ID_TOL = 1e-3\n", ("ST-REFUSE",)),
    ("nomic identity skipped", "            idlines.append(identity_check(T, H, {\"n@256\", \"n@512\"}, \"nomic 256 / 512 (s0_c1.csv)\"))\n",
     "            idlines.append(\"IDENTITY nomic 256 / 512 skipped -> REPRODUCED\")\n", ("ST-REFUSE",)),
    ("H bootstrap seed of another corpus", "        r.update(EDS.h_boot(C, S, BOOT_B, EDS.SEED_H + CORPORA.index(c)))\n        STORE",
     "        r.update(EDS.h_boot(C, S, BOOT_B, EDS.SEED_H))\n        STORE", ("ST-E2E-C",)),
    ("outcome not write-once", "    for p in out_paths(out_dir):\n        if os.path.lexists(p):\n            refuse(", "    for p in out_paths(out_dir):\n        if False:\n            refuse(", ("ST-E2E-C",)),
    ("registration not line-anchored", "REG_RE = re.compile(r\"^\" + re.escape(REG_HEADING), re.M)\n", "REG_RE = re.compile(re.escape(REG_HEADING))\n", ("ST-REFUSE",)),
    ("non-strict pins on --run", "    sha0, _sel = pin_all(db, emb_dir, True, sel_path, sel_sha)\n", "    sha0, _sel = pin_all(db, emb_dir, False, sel_path, sel_sha)\n", ("ST-REFUSE",)),
    ("nmi_matrix blob not checked", "    if strict_blob and RO.git_blob_lf(files[\"nmi_matrix\"]) != NMI_MATRIX_BLOB:\n", "    if False:\n", ("ST-REFUSE",)),
    ("heavy check dropped", "        refuse(\"nmi_matrix.csv is blob %s, not the registered %s\" % (RO.git_blob_lf(files[\"nmi_matrix\"]), NMI_MATRIX_BLOB))\n    heavy_check()\n",
     "        refuse(\"nmi_matrix.csv is blob %s, not the registered %s\" % (RO.git_blob_lf(files[\"nmi_matrix\"]), NMI_MATRIX_BLOB))\n", ("ST-REFUSE",)),
    ("dry-run computes q8 coarse (new data)", "            process_source(src, CS, vecs, coarse_seeds=SEEDS_F, arms=arms, coarse_arms=EDS_ARMS, h_arms=EDS_ARMS)\n",
     "            process_source(src, CS, vecs, coarse_seeds=SEEDS_F, arms=arms, coarse_arms=None, h_arms=EDS_ARMS)\n", ("ST-DRY",)),
    ("dry-run reads nomic", "        for src in (\"q4\", \"q8\", \"qcard\", \"g\", \"gcard\"):\n", "        for src in (\"q4\", \"q8\", \"qcard\", \"g\", \"gcard\", \"n\"):\n", ("ST-DRY",)),
    ("P1 interval open", "    return bool(lo <= v <= hi)\n", "    return bool(lo < v < hi)\n", ("ST-UNIT",)),
    ("P5 q8 event on one corpus", "    e4 = all(abs(H[(\"q8\", c)][\"H\"] - H[(\"q1024\", c)][\"H\"]) <= 0.02 for c in COARSE_C)\n",
     "    e4 = all(abs(H[(\"q8\", c)][\"H\"] - H[(\"q1024\", c)][\"H\"]) <= 0.02 for c in COARSE_C[:1])\n", ("ST-PRED",)),
    ("P4 g768 event on MASSIVE only", "    e2 = all(R[\"fine\"][(\"EMBEDDER\", \"g768\", \"q1024\", c)][\"status\"] == \"DIFFERENT\" for c in (\"massive\", \"banking77\"))\n",
     "    e2 = all(R[\"fine\"][(\"EMBEDDER\", \"g768\", \"q1024\", c)][\"status\"] == \"DIFFERENT\" for c in (\"massive\",))\n", ("ST-PRED",)),
    ("P5 g768 vs the first three slices", "for q in (\"q256\", \"q512\", \"q1024\", \"q4096\"))\n", "for q in (\"q256\", \"q512\", \"q1024\"))\n", ("ST-PRED",)),
    ("P1 SEEN mark dropped", "\" (SEEN: never a confirmation)\" if seen else \"\"", "\"\"", ("ST-PRED",)),
    ("Brier on the complement", "    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2\n", "    return (float(p) - (0.0 if bool(event) else 1.0)) ** 2\n", ("ST-UNIT",)),
)


def run_mutants(only=None):
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="gle_mut_")
    fx = make_fixtures(td)
    killed, total = 0, 0
    for name, old, new, tests in MUTANTS:
        if only and name not in only:
            continue
        total += 1
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        code = head.replace(old, new)
        ns = {"__name__": "gle_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests) if tests else None, quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:100])
        finally:
            ITS.SLICE2 = 512
            reset()
        killed += res.startswith("KILLED")
        print("  %-60s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, total))
    return 0 if killed == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="GOLD-LEVEL-EMB (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--no-timing", action="store_true")
    ap.add_argument("--identity", action="store_true", help="--dry-run: also the identity on the non-nomic arms (values of record only)")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(a.db, a.emb_dir, timing=not a.no_timing, identity=a.identity)
    main_run(a.db, a.emb_dir, a.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
