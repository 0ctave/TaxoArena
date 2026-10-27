"""SUPERGPQA-STAGE0 (RP11) -- per-discipline policy gain G and the key profile's interaction-only R on SuperGPQA's
DECLARED disciplines, key only, ZERO judge calls, zero construction, no embedding.

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-09-27 (before any code or call) --
SUPERGPQA-STAGE0: on SuperGPQA, split content-closed under CK-CLOSE-v1 at 0.30 EVAL per field, ..." (L21790-L21829 as of
a357ef0; resolve by the heading; the last bracket in the programme file wins over this copy), with the registrar's
reconciliations (i) and (ii) in the section "## Registrar's record 2026-09-27 ... Wave-0 REGISTRATIONS (record 2 of 2)"
(L21535-L21555). This script is BUILT TO that text; where it had to read the text, the reading is stated under READINGS
and is for the READY to confirm or refuse. Nothing here is a verdict until the READY, the run and the post-run review.

  python tools/analysis/supergpqa_stage0.py --selftest   # synthetic fixtures under tempfile.mkdtemp(); opens NO real file
  python tools/analysis/supergpqa_stage0.py --mutants    # the selftest under each registered mutant; every one must be KILLED
  python tools/analysis/supergpqa_stage0.py --split      # draws the CK-CLOSE-v1 split from the QUESTION FILE ALONE and writes
                                                         #   experiment_configs/supergpqa_stage0_split.json WRITE-ONCE
  python tools/analysis/supergpqa_stage0.py --dry-run    # pins, split re-derivation, stores, A1 (uuids ONLY), A3-A6 counts;
                                                         #   reads NO stored correctness, prints NO statistic, writes nothing
  python tools/analysis/supergpqa_stage0.py --run        # A1-A6 in order, then C1 / C2 / descriptive; outcome WRITE-ONCE

LAUNCH SEQUENCE (registration FLOW): tools/analysis/supergpqa_fetch.py --fetch (the whitelisted files, sha256 manifest,
outside git) -> this script --split (question file only; the EVAL id file and its sha COMMITTED BEFORE ANY RESPONSE FILE IS
PARSED) -> --selftest / --mutants -> adversarial-reviewer READY (fixes the whitelist, the size cap and the READINGS) ->
run-operator --dry-run -> --run -> post-run review -> registrar. Run with TAXOARENA_DATA_ROOT pointing at the main checkout
(the text stores live there) and SUPERGPQA_DATA at the fetch target; single-threaded (OMP / MKL / OPENBLAS_NUM_THREADS=1).
Preconditions of record (not checked here): DATASET-SURVEY's SuperGPQA row ADMITS; A5 confirmed by the data-steward.

THE SEAL (binding): any SuperGPQA-Records file whose content aggregates over questions (results_*.json / results_*.xlsx) is
NEVER opened: the reader opens ONLY files named in the whitelist experiment_configs/supergpqa_stage0_whitelist.json (names
+ bytes + sha256 from the fetch manifest), refuses a name matching the seal pattern whatever the whitelist says, refuses a
file above SIZE_CAP_BYTES, verifies sha256 BEFORE parsing, parses JSON lines only (json.loads; no pickle, no eval, no
archive extraction; the question file's `options` field is a Python-literal list string and is read with
ast.literal_eval, which evaluates literals only), and ACCESSES only uuid, the stored correctness (`status`, or
`extracted_answer` when `status` is absent) and `response` (A2 sample only). Every file opened is printed with its sha256.

INSTRUMENT (the registration's INSTRUMENT paragraph):
  split       CK-CLOSE-v1 at 0.30 EVAL per field, key split_side.stem_key (norm-v1), seed = sha256("SUPERGPQA-STAGE0-SPLIT-1");
              conditions (1) sentinels: none exist in SuperGPQA (printed 0); (2) global closure over the corpus; (3) family
              closure (identical stem_key -> one side); (4) within-EVAL twins CLUSTERED (component = stem_key family).
              content_closure.assert_content_disjoint is the guard of record on the drawn split.
  stores      stem_key of every question against every text store (STORES below; read-only, pool_guard.open_ro: -wal /
              -journal refused first, then mode=ro&immutable=1); colliding families EXCLUDED from both sides, counted per store.
  key         the Records' stored correctness of the admitted models (status == "correct"); the answer letter of the
              question file is the key it scores against (re-extraction in A2 scores against it).
  policy      per scored discipline the TRAIN argmax model (tie-break: higher pooled TRAIN accuracy, then name); best single:
              the pooled TRAIN argmax (tie-break: name); EVAL items of unscored disciplines take the best single (G counts
              only the EVAL items of the scored disciplines).
  bootstrap   ROUTER-CLEAN-POLICY's form: B = 2,000, numpy default_rng(42); two-stage (DECIDING) = TRAIN resampled within
              each of the 13 disciplines with every policy re-fitted, then EVAL CK-CLOSE components resampled within
              discipline; i.i.d. (beside) = scored EVAL items resampled i.i.d., policy fixed. Interval = point +- 1.96 SE_2stage
              (percentile beside). The refusal G4 of ROUTER-CLEAN-POLICY is kept: a zero two-stage variance refuses.
  placebo     the discipline labels of the TRAIN items permuted (random.Random(42).shuffle over the label list in sorted-uuid
              order; sizes kept); the pseudo-discipline argmax on TRAIN scored on the EVAL items by their TRUE discipline.
  R           PROFILE-RELIABILITY-INTERACTION's estimator, imported unchanged (profile_reliability_interaction.leg / intervals
              / null_tables): 40 halvings random.Random(7), model- and discipline-demeaned, Spearman-Brown; leave-one-
              discipline-out jackknife (re-halved primary, fixed beside, z 1.96); logit-additive null, 20 tables, seeds 1..20.
CRITERIA (verbatim bars; the INTERVAL decides; the point decides nothing):
  C1 HELD iff the two-stage 95% interval of G lies wholly above 0; FAILED iff wholly below 0; UNDETERMINED otherwise.
     Validity trigger: the placebo's interval wholly above 0 VOIDs C1.
  C2 HELD iff the jackknife 95% lower bound of R exceeds the null's 95th percentile (19th of 20); FAILED iff the upper bound
     is at or below it; UNDETERMINED otherwise. A6 (< 5 scored disciplines) -> UNDETERMINED-BY-SUPPORT.
  F1 fires iff C2 FAILED.
ADMISSION LEGS (evaluated FIRST, in order; a failure -> STOP and the refusal is the outcome, written write-once):
  A1 >= 20 complete models (the file-list count printed against 49); A2 key audit on 200 TRAIN questions, agreement >= 0.95
  per model, a model below EXCLUDED BY NAME, >= 20 must remain; A3 the split exists, re-derives, no family straddles;
  A4 cross-store collisions <= 2.0% of items; A5 ODC-BY on both cards (front matter `license:` only); A6 >= 5 disciplines
  with >= 120 EVAL items after closure and exclusions (fewer: C2 UNDETERMINED-BY-SUPPORT, C1 read on what exists).
  A store the reader cannot open (a non-empty -wal / -journal) is a FAILED PRECONDITION, never an outcome: no file is written.

READINGS (stated, not silent; each for the READY):
  R1 split mechanics: fields in sorted (discipline, field) order, one random.Random(int(sha256(seed string), 16)); within a
     field, families sorted by stem_key then shuffled; EVAL = the shortest prefix of the shuffled families whose item count
     reaches round-half-up(0.30 x n_field). A family spanning two fields REFUSES the draw (none exists: 2 twin families,
     both within one field).
  R2 split id: SuperGPQA has no pool of record; the first printed line is the split id "sg" + sha256(LF-joined sorted EVAL
     uuids)[:16] and the split file's sha256 (pool_guard.assert_pool_of_record does not apply).
  R3 completeness: a model is COMPLETE iff every corpus uuid has a record and no uuid carries two records with different
     stored correctness (the dry-run, which reads no correctness, checks presence and prints duplicate counts only).
  R4 A2 sample: 200 TRAIN uuids, largest-remainder proportional allocation over the 13 disciplines, drawn with
     random.Random(int(sha256("SUPERGPQA-STAGE0-A2-1"), 16)) from each discipline's sorted TRAIN uuids; the SAME sample for
     every model. Re-extraction = the SuperGPQA official zero-shot extractor, ported VERBATIM (upstream
     github.com/SuperGPQA/SuperGPQA @ e31e8bf3e7089aef808be5ddecafd4538dee6e41, eval/eval.py L32-L105, block sha256-lf
     UPSTREAM_BLOCK_SHA256, asserted by the selftest on this file's own bytes), options from the QUESTION file; agreement =
     (re-extracted letter == answer letter) == (stored status == "correct").
  R5 C2 cells: the scored disciplines in sorted-name order (the halvings depend on the order), each cell = its EVAL items
     after exclusions; the roster = the admitted models in sorted-name order; key build = per-model accuracy over the half.
     The jackknife lower / upper bound of record is the RE-HALVED one (PROFILE-RELIABILITY-INTERACTION's primary).
  R6 descriptive: field grain = the fields with >= 120 EVAL items, per-field TRAIN argmax against the best single over those
     fields' EVAL items (the discipline policy on the same items beside); family-collapsed = per FAMILY (FAMILY_OF below)
     the model with the highest pooled TRAIN accuracy (tie: name), best single and discipline policy re-fitted on that
     roster; dominance column = per scored discipline, whether its TRAIN argmax is the best single. The two-roster contrast
     (26 five-shot base models) and the best-of-N floor are NOT READ in this build (files not fetched; the BoN floor has
     no registered definition) and print as such.
  R7 predictions "X [lo, hi]" are HELD iff the point lies in [lo, hi] (inclusive); under STOP every prediction whose leg
     was not reached is UNDETERMINED (BY STOP); under the placebo trigger P3 is UNDETERMINED (BY TRIGGER).
[DELTA 2026-09-27, the engine-coder: SUPERGPQA-STAGE0b (docs/judge_v2_program.md L21848-L21865, registered at 3fdc5d2,
POST-COUNT, PRE-KEY; the author's decision (a)) and the READY review 1adce88; insertion only, the text above stands as the
STAGE0 build's] --run implements STAGE0b. (1) A4 becomes A4b, an IDENTITY GATE: the union of the colliding uuids over the
MMLU-Pro-bearing stores (MMLU_STORES) must EQUAL the pinned list experiment_configs/supergpqa_stage0b_mmlu_pro_exclusion.json
(sha256-lf EXCL_SHA256; 1,251 uuids, 370 EVAL / 881 TRAIN), else STOP at A4b; every store must be readable (20NG and ag_news
included: a non-empty -wal / -journal REFUSES, a failed precondition, nothing written); collisions in any other store are
also EXCLUDED and counted per store. No bar. (2) Order: A3, A4b, A1, A2, A5, A6 (reading: A1 sits before A2 because A2
audits the complete files; A2's TRAIN sample is drawn AFTER exclusion). (3) No STOP path prints a key or correctness count
(review B1): while the legs are decided the stored correctness is accessed ONLY for the A2 sample (TRAIN, after exclusion)
and for uuids that carry duplicate records (the R3 conflict check, a second pass on that file only); the per-model line
prints presence, duplicates and conflicts only; the full key is read only after A6 passes, and the miss + error share per
model is printed only there. (4) The population of every STAGE0b number is "SuperGPQA minus its MMLU-Pro stem_key
collisions", printed with the 4.7156% disclosure. Predictions are STAGE0b's (P1 legs A1 A2 A3 A5 A6; P1a A1 finds 49 read as
complete == 49; P1c >= 40 pass A2; P2 SEEN, an identity, not scored; P3-P7 as STAGE0; STAGE0's P1b is not registered in
STAGE0b). The two-roster contrast and the best-of-N floor print UNDEFINED (review M1: the registration names them without an
estimand, and the five-shot files are not fetched; owed a ruling, never silently absent). L1: the SPLIT line is the first
printed line. L4: an extractor match that is not an option counts as a re-extraction miss (ValueError caught).
Key-scored end to end: no judge verdict enters, so no wrong(established) count and no tie convention A / B arises; the
stored "miss" / "error" statuses are scored wrong (the Records' correctness); each model's miss + error share is printed.
OUTPUT: experiment_results/supergpqa/supergpqa_stage0_outcome.txt, WRITE-ONCE (opened mode "x"; refused if it exists).
The key matrix is persisted to experiment_results/supergpqa/supergpqa_stage0_key.db (own file, not a pool DB, never
committed; meta pinned at first write: script blob, split sha, whitelist sha; a mismatch refuses).
[DELTA 2026-09-29, the engine-coder, after delta READY fd6a349 and the registrar's record of 2026-09-29 (e09e551); insertion only,
the text above stands as the builder's report] Ruling 20: the two-roster contrast and the best-of-N floor are STRUCK by a pre-key
bracket and print "DESCRIPTIVE, STRUCK (bracket: the registrar's record of 2026-09-29, ruling 20, pre-key)", no longer UNDEFINED.
C11-3: A4b is a SET-equality gate (a same-size, same-side-count, different set STOPs; mutant a4b_counts_only); the A1 scan's key
holds only A2-sample uuids and the R3 pass only duplicated uuids, REFUSED otherwise and asserted by value on the mode_run
fixture (mutant a1_full_key, run through mode_run: MODE_RUN_MUTANTS). C11-4: PLAN_C1 is STAGE0b's Support (a)-(f) (n 7,396,
n_eff 5,637, SE 0.005265, MDE80 1.47pp), checked by value against its inputs on the --run fixture. Ruling 21's count of models
whose completeness differs from the full-corpus count is NOT built here.
"""
import argparse
import ast
import contextlib
import hashlib
import io
import json
import math
import os
import random
import re
import sqlite3
import sys
import tempfile
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import split_side as ss            # noqa: E402
import content_closure as cc       # noqa: E402

TEST_ID = "SUPERGPQA-STAGE0b"      # STAGE0b (3fdc5d2); STAGE0's split, seed and instrument are inherited verbatim
SEED_STRING = "SUPERGPQA-STAGE0-SPLIT-1"
A2_SEED_STRING = "SUPERGPQA-STAGE0-A2-1"
EVAL_SHARE = 0.30
FLOOR = 120                 # EVAL items per scored discipline (A6)
MIN_SCORED = 5              # A6
MIN_MODELS = 20             # A1, A2 (reconciliation (i))
EXPECTED_ZS = 49            # asserted file-list count (mismatch printed, not a STOP)
A2_N = 200
A2_BAR = 0.95
A4_BAR = 0.02               # collided share of the corpus's items (reconciliation (ii))
B = 2000
BOOT_SEED = 42
PLACEBO_SEED = 42
N_NULL = 20
NULL_SEEDS = list(range(1, 21))
NULL_P95_INDEX = 18         # 19th of 20, ascending
Z = 1.96
SIZE_CAP_BYTES = 900_000_000   # proposed; the READY fixes it (largest whitelisted file 853,814,205 bytes)
N_QUESTIONS_PLAN = 26529       # planning figure (UNSOURCED until the steward's count); printed, never asserted

DATA_DIR = os.environ.get("SUPERGPQA_DATA", "Z:/FAC/TUBerlin/THESIS/TaxoArena_data/supergpqa")
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
LCB_ROOT = os.environ.get("LCB_DATA", os.path.join(os.path.dirname(DATA_ROOT), "TaxoArena_data", "lcb"))
QUESTION_FILE = os.path.join(DATA_DIR, "SuperGPQA", "SuperGPQA-all.jsonl")
QUESTION_FILE_SHA256 = "28b998e70205ee95e540317b5adc06a06552a3961fb50b153df126b833f7a910"   # Hub LFS oid @ 4430d44
CARDS = {"m-a-p/SuperGPQA": os.path.join(DATA_DIR, "SuperGPQA", "README.md"),
         "m-a-p/SuperGPQA-Records": os.path.join(DATA_DIR, "SuperGPQA-Records", "README.md")}
SPLIT_PATH = os.path.join(ROOT, "experiment_configs", "supergpqa_stage0_split.json")
SPLIT_SHA256 = "1db5c7c4366b1a0d7d4109eb7d93368c61d5f520257d16f0df99595d4e695df2"   # sha256-lf of the split file as drawn
#   (split id sg893684444c6df3e9, EVAL 7,961 / TRAIN 18,568; drawn by blob:2343d573 before any response file was opened)
WHITELIST_PATH = os.path.join(ROOT, "experiment_configs", "supergpqa_stage0_whitelist.json")
OUT_DIR = os.path.join(ROOT, "experiment_results", "supergpqa")
OUT_PATH = os.path.join(OUT_DIR, "supergpqa_stage0b_outcome.txt")
KEY_DB = os.path.join(OUT_DIR, "supergpqa_stage0b_key.db")
# STAGE0b A4b identity gate (the pinned MMLU-Pro collision list; the READY review 1adce88's key-free count)
EXCL_PATH = os.path.join(ROOT, "experiment_configs", "supergpqa_stage0b_mmlu_pro_exclusion.json")
EXCL_SHA256 = "89d17b0df027728e674ef83ff822a99b7a85e7e820749e4226138aa862de7ae2"   # sha256-lf of the pinned list
EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN = 1251, 370, 881
N_ITEMS_SEEN = 26529
MMLU_STORES = ("S01 MMLU-Pro", "S02 union (6 tasks incl. GPQA)", "S07a v2 split-1 mmlu-pro-v2", "S07b v2 split-1 union mc6",
               "S07c v2 split-2 mmlu-pro-v2", "S07d v2 split-2 union mc6")
RUN_B = B                   # the two-stage B of --run (the selftest's fixture lowers it)
LAST = {}                   # the last --run's internals (read by the selftest's value checks only)
SEAL_RE = re.compile(r"(^|/)results_[^/]*$|\.xlsx$|(^|/)[^/]*(summary|leaderboard|aggregate|accurac)[^/]*$", re.I)
ZS_RE = re.compile(r"^zero-shot/([A-Za-z0-9._\-]+)_SuperGPQA-all_zero-shot\.jsonl$")
LETTERS = "ABCDEFGHIJ"

# Every text store of the programme (registration: MMLU-Pro, the six-task union incl. GPQA, LCB, 20NG, BFCL, Multi-SWE,
# the v2 split stores; S08 / S09 are further stores of the programme, included fail-closed). (root, relpath, [(table,
# column, kind)]); kind "text" = stem_key recomputed from the column, "key" = the column IS a stored stem_key (norm-v1,
# data_v2.common / LCB texts meta key_rule "stem_key (ck-v1)"), "id" = Multi-SWE's instance id (its only key, review D4).
_V2 = "data_v2/REG_ARCHV2-SPLIT-%d_%s"
_V2S = {1: "c03031568a0a9d827d834b075512b8e4dd095642", 2: "2929bd46aa271d883050bfe735f96e621ed55fd2"}
_MMLU_TABLES = [("mmlu_pro", "question", "text"), ("mmlu_original", "question", "text"), ("arc", "question", "text"),
                ("twenty_newsgroups", "question", "text"), ("ag_news", "question", "text"),
                ("eval_question_link", "question_text", "text"), ("eval_results", "question_text", "text")]
STORES = [
    ("S01 MMLU-Pro", "data", "mmlu_pro_dataset_cache_v2.db", _MMLU_TABLES),
    ("S02 union (6 tasks incl. GPQA)", "data", "multicorpus_cache_v1.db",
     [("corpus_questions", "text", "text")] + _MMLU_TABLES),
    ("S03a LCB v6 texts", "lcb", "lcb_v6_texts_7d2f4cad635b254d.db",
     [("problem", "question_content", "text"), ("problem", "stem_key", "key")]),
    ("S03b LCB v6 eval texts", "lcb", "lcb_v6_eval_texts_92764cb2900dd0dc.db",
     [("corpus_questions", "text", "text"), ("livecodebench", "question", "text")]),
    ("S04 20NG", "data", "twenty_newsgroups_cache_v1.db",
     [("twenty_newsgroups", "question", "text"), ("corpus_questions", "text", "text")]),
    ("S05 BFCL", "data", "experiment_results/agent/bfcl_result_2025-12-16.db", [("tasks", "stem", "text")]),
    ("S06 Multi-SWE", "data", "experiment_results/agent/multiswe_result_2026-09-22.db", [("tasks", "instance_id", "id")]),
    ("S07a v2 split-1 mmlu-pro-v2", "data", (_V2 % (1, _V2S[1])) + "/corpus_v2_mmlu_pro_v2.db", [("item", "stem_key", "key")]),
    ("S07b v2 split-1 union mc6", "data", (_V2 % (1, _V2S[1])) + "/corpus_v2_union_mc6.db", [("item", "stem_key", "key")]),
    ("S07c v2 split-2 mmlu-pro-v2", "data", (_V2 % (2, _V2S[2])) + "/corpus_v2_mmlu_pro_v2.db", [("item", "stem_key", "key")]),
    ("S07d v2 split-2 union mc6", "data", (_V2 % (2, _V2S[2])) + "/corpus_v2_union_mc6.db", [("item", "stem_key", "key")]),
    ("S08 ag_news smoke", "data", "ag_news_smoke_cache_v1.db",
     [("ag_news", "question", "text"), ("corpus_questions", "text", "text")]),
    ("S09 JudgeBench", "data", "judgebench_corpus_v1.db", [("pairs", "question", "text")]),
]

# R6: model -> family for the family-collapsed sensitivity (DESCRIPTIVE; a reading for the READY).
FAMILY_RULES = [("DeepSeek", "DeepSeek"), ("Doubao", "Doubao"), ("K2", "LLM360-K2"), ("Llama", "Llama"),
                ("MAP-Neo", "MAP-Neo"), ("MiniMax", "MiniMax"), ("Mistral", "Mistral"), ("Mixtral", "Mistral"),
                ("OLMo", "OLMo"), ("QwQ", "Qwen"), ("Qwen", "Qwen"), ("qwen", "Qwen"), ("Yi", "Yi"),
                ("claude", "Anthropic"), ("gemini", "Google-Gemini"), ("gemma", "Google-Gemma"), ("gpt-4o", "OpenAI"),
                ("o1", "OpenAI"), ("o3", "OpenAI"), ("granite", "IBM-Granite"), ("phi", "Microsoft-Phi")]

# Registered Support planning numbers (printed beside the measured ones).
PLAN_C1 = ("STAGE0b (post-exclusion scored-EVAL object): n_EVAL 7,396 in 7,395 CK-CLOSE components (Kish 1.00027, measured "
           "key-free); DEFF 1.312 (two-stage, TRANSPORTED from ROUTER-CLEAN-POLICY x component Kish 1.00027); n_eff 5,637; "
           "SE 0.005265 (d 0.15627); MDE80 1.47pp (1.86pp at d 0.25); VERDICT LINE: DESCRIPTIVE-ONLY (P3 +1.0pp is 1.0pp from "
           "the bar 0 < MDE 1.47pp)")
PLAN_C2 = ("SE 0.0339 transported from PROFILE-RELIABILITY-INTERACTION's K12 half-width 0.0665; MDE80 0.095; VERDICT "
           "LINE: SCOREABLE (prediction 0.85 against a null p95 <= 0.60; break-even null p95 0.755)")

MUTANT = None            # SELFTEST-ONLY switch; every real mode refuses when it is set
MUTANTS = ["tiebreak_name_first", "placebo_unpermuted", "eval_leak_fit", "null_p95_index19", "jack_fixed", "a1_ge_21",
           "a4_strict", "split_no_family", "write_mode_w", "c2_upper_lt", "g_all_eval", "a2_bar_gt", "eval_share_035",
           "seed_string", "numpy_bool_identity", "seal_open", "stored_status_ignored", "placebo_trigger_ge",
           "a4b_counts_only", "a1_full_key"]
MODE_RUN_MUTANTS = ("a1_full_key",)


def refuse(msg):
    raise SystemExit("[SUPERGPQA-STAGE0] " + msg)


# =========================================================================================== identity / pins
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def script_pins(path=None):
    """blob (git hash-object of the LF rendering), sha256 of the LF bytes, sha256 of the CRLF bytes (rule 8)."""
    path = path or os.path.abspath(__file__)
    with open(path, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    blob = hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest()
    return dict(blob=blob, lf16=hashlib.sha256(lf).hexdigest()[:16], crlf16=hashlib.sha256(crlf).hexdigest()[:16],
                working_tree="CRLF" if b"\r\n" in raw else "LF")


def pin_line(name, path=None):
    p = script_pins(path)
    return "%s blob:%s / sha256-lf16:%s / sha256-crlf16:%s (working tree %s)" % (
        name, p["blob"], p["lf16"], p["crlf16"], p["working_tree"])


def seed_int(s):
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest(), 16)


# =========================================================================================== restricted parsing
def check_file_admitted(path, rel, whitelist, cap=SIZE_CAP_BYTES, out=print):
    """The seal and the whitelist, BEFORE any byte is parsed: name not sealed, name whitelisted, size <= cap, sha256 equal."""
    if SEAL_RE.search(rel) and MUTANT != "seal_open":
        refuse("SEAL: %s matches the aggregate-file pattern; it is never opened" % rel)
    ent = whitelist.get(rel)
    if ent is None:
        refuse("%s is not in the whitelist" % rel)
    n = os.path.getsize(path)
    if n > cap:
        refuse("%s is %d bytes, above the size cap %d" % (rel, n, cap))
    if n != ent["bytes"]:
        refuse("%s is %d bytes, whitelist says %d" % (rel, n, ent["bytes"]))
    s = sha256_file(path)
    if s != ent["sha256"]:
        refuse("%s sha256 %s != whitelist %s" % (rel, s, ent["sha256"]))
    out("  [OPEN] %s sha256=%s bytes=%d" % (rel, s, n))
    return s


def load_whitelist(path=WHITELIST_PATH):
    with open(path, "r", encoding="utf-8") as f:
        w = json.load(f)
    out = {}
    for e in w["files"]:
        if SEAL_RE.search(e["path"]):
            refuse("the whitelist names a sealed file: %s" % e["path"])
        out[e["path"]] = e
    return w, out


def parse_options(v):
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str):
        x = ast.literal_eval(v)          # literals only; never eval()
        if isinstance(x, (list, tuple)):
            return [str(y) for y in x]
    refuse("options field is neither a list nor a literal list string")


def load_questions(path, expect_sha=QUESTION_FILE_SHA256, out=print):
    s = sha256_file(path)
    if expect_sha is not None and s != expect_sha:
        refuse("question file sha256 %s != pinned %s" % (s, expect_sha))
    out("  [OPEN] question file %s sha256=%s" % (os.path.basename(path), s))
    Q = []
    seen = set()
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            for k in ("uuid", "question", "options", "answer_letter", "discipline", "field", "subfield"):
                if k not in r:
                    refuse("question file line %d lacks %s" % (ln, k))
            u = r["uuid"]
            if u in seen:
                refuse("duplicate uuid %s" % u)
            seen.add(u)
            if not ss.norm(r["question"]):
                refuse("empty stem at uuid %s" % u)
            opts = parse_options(r["options"])
            al = r["answer_letter"]
            if not (isinstance(al, str) and len(al) == 1 and al in LETTERS[:len(opts)]):
                refuse("answer letter %r out of range at uuid %s" % (al, u))
            Q.append(dict(uuid=u, question=r["question"], options=opts, answer_letter=al, discipline=r["discipline"],
                          field=r["field"], subfield=r["subfield"], stem_key=ss.stem_key(r["question"])))
    Q.sort(key=lambda q: q["uuid"])
    return Q, s


def card_license(path):
    """The `license:` value of the card's YAML front matter; nothing after the closing '---' is read."""
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline()
        if first.strip() != "---":
            return None
        for line in f:
            if line.strip() == "---":
                return None
            m = re.match(r"^license:\s*([A-Za-z0-9._\-]+)\s*$", line.strip())
            if m:
                return m.group(1).lower()
    return None


# =========================================================================================== the split (CK-CLOSE-v1)
def round_half_up(x):
    return int(math.floor(x + 0.5))


def draw_split(Q):
    """R1. Returns dict(eval, train, families, per_field, twins)."""
    share = 0.35 if MUTANT == "eval_share_035" else EVAL_SHARE
    seed = SEED_STRING + ("X" if MUTANT == "seed_string" else "")
    fam = defaultdict(list)
    for q in Q:
        key = q["uuid"] if MUTANT == "split_no_family" else q["stem_key"]
        fam[key].append(q)
    by_field = defaultdict(list)
    for k, members in fam.items():
        fields = {(m["discipline"], m["field"]) for m in members}
        if len(fields) != 1:
            refuse("family %s spans %d fields; the stratified draw cannot keep it whole (R1)" % (k[:16], len(fields)))
        by_field[next(iter(fields))].append(k)
    rng = random.Random(seed_int(seed))
    ev, tr = set(), set()
    per_field = {}
    for fk in sorted(by_field):
        keys = sorted(by_field[fk])
        rng.shuffle(keys)
        n = sum(len(fam[k]) for k in keys)
        target = round_half_up(share * n)
        cum = 0
        n_ev = 0
        for k in keys:
            if cum < target:
                for m in fam[k]:
                    ev.add(m["uuid"])
                cum += len(fam[k])
                n_ev += len(fam[k])
            else:
                for m in fam[k]:
                    tr.add(m["uuid"])
        per_field["%s / %s" % fk] = dict(n=n, target=target, eval=n_ev)
    twins = {k: sorted(m["uuid"] for m in v) for k, v in fam.items() if len(v) > 1}
    return dict(eval=ev, train=tr, per_field=per_field, twins=twins, seed_hex=hashlib.sha256(seed.encode()).hexdigest())


def split_id(eval_uuids):
    return "sg" + hashlib.sha256("\n".join(sorted(eval_uuids)).encode("utf-8")).hexdigest()[:16]


def closure_check(Q, ev, tr, out=print):
    """A3: every family on one side (global + family closure, conditions 2-3), no sentinels (1), twins clustered (4),
    and content_closure.assert_content_disjoint as the guard of record."""
    text_of = {q["uuid"]: q["question"] for q in Q}
    side_by_key = defaultdict(set)
    for q in Q:
        side_by_key[q["stem_key"]].add("E" if q["uuid"] in ev else "T")
    straddle = sum(1 for v in side_by_key.values() if len(v) > 1)
    if ev & tr:
        refuse("an item is on both sides")
    if (ev | tr) != set(text_of):
        refuse("the split does not cover the corpus")
    buf = io.StringIO()
    try:
        cc.assert_content_disjoint(sorted(tr), sorted(ev), (), text_of, where="SUPERGPQA-STAGE0 split",
                                   out=lambda s: buf.write(s + "\n"))
        guard = "PASS"
    except SystemExit as e:
        guard = "REFUSED (%s)" % e
    out("  " + buf.getvalue().strip().replace("\n", "\n  ") if buf.getvalue().strip() else "  [CK-CLOSE] (no line)")
    comps = defaultdict(list)
    for q in Q:
        if q["uuid"] in ev:
            comps[q["stem_key"]].append(q["uuid"])
    sizes = [len(v) for v in comps.values()]
    kish = sum(s * s for s in sizes) / max(1, sum(sizes))
    return dict(straddle=straddle, guard=guard, n_eval=len(ev), n_train=len(tr), n_comp=len(comps),
                twins_eval=sum(1 for s in sizes if s > 1), kish=kish, sentinels=0)


def write_split(Q, qsha, path=SPLIT_PATH, out=print):
    d = draw_split(Q)
    obj = {
        "registration": TEST_ID + " (docs/judge_v2_program.md L21790-L21829 as of a357ef0)",
        "rule": "CK-CLOSE-v1 at %.2f EVAL per field; key split_side.stem_key %s / %s; reading R1 of the script docstring"
                % (EVAL_SHARE, ss.NORMALISER_VERSION, ss.KEY_RULE),
        "seed_string": SEED_STRING, "seed_sha256": d["seed_hex"],
        "question_file_sha256": qsha, "n_items": len(Q), "n_eval": len(d["eval"]), "n_train": len(d["train"]),
        "split_id": split_id(d["eval"]), "sentinels": [],
        "twin_families": d["twins"], "per_field": d["per_field"],
        "drawn_by": script_pins(),
        "eval": sorted(d["eval"]), "train": sorted(d["train"]),
    }
    data = (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode("utf-8")
    with open(path, "xb") as f:          # write-once
        f.write(data)
    out("wrote %s sha256=%s (split id %s; EVAL %d / TRAIN %d)" % (path, hashlib.sha256(data).hexdigest(), obj["split_id"],
                                                                  obj["n_eval"], obj["n_train"]))
    return obj


def sha256_lf(path):
    """sha256 of the LF rendering (a committed text file is CRLF in an autocrlf working tree; rule 8: LF is of record)."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def load_split(path=SPLIT_PATH, expect_sha=None):
    s = sha256_lf(path)
    if expect_sha is not None and s != expect_sha:
        refuse("split file sha256-lf %s != pinned %s" % (s, expect_sha))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f), s


def rederive_split(Q, split_obj):
    d = draw_split(Q)
    ok = (sorted(d["eval"]) == split_obj["eval"] and sorted(d["train"]) == split_obj["train"])
    return bool(ok), d


# =========================================================================================== text stores (A4)
def store_path(root, rel):
    base = LCB_ROOT if root == "lcb" else DATA_ROOT
    return os.path.join(base, *rel.split("/"))


def read_store_keys(path, cols, open_ro):
    conn = open_ro(path)
    keys = set()
    n_rows = 0
    try:
        for table, col, kind in cols:
            for (v,) in conn.execute("SELECT DISTINCT %s FROM %s WHERE %s IS NOT NULL" % (col, table, col)):
                n_rows += 1
                if kind == "key":
                    keys.add(v)
                elif kind in ("text", "id"):
                    if isinstance(v, str) and ss.norm(v):
                        keys.add(ss.stem_key(v))
    finally:
        conn.close()
    return keys, n_rows


def collisions(Q, stores, open_ro, out=print, want_per=False):
    """Returns (per_store rows, excluded uuid set, blocked list). A store that cannot be opened is BLOCKED (precondition)."""
    fam = defaultdict(list)
    for q in Q:
        fam[q["stem_key"]].append(q["uuid"])
    sg = set(fam)
    rows, excl, blocked = [], set(), []
    per = {}
    for name, root, rel, cols in stores:
        path = store_path(root, rel)
        try:
            keys, n_rows = read_store_keys(path, cols, open_ro)
        except SystemExit as e:
            blocked.append((name, str(e)))
            out("  store %-32s BLOCKED (failed precondition): %s" % (name, str(e)[:160]))
            continue
        hit = sg & keys
        items = sorted(u for k in hit for u in fam[k])
        excl |= set(items)
        per[name] = set(items)
        rows.append((name, rel, n_rows, len(keys), len(hit), len(items)))
        out("  store %-32s %s: %d distinct values, %d keys; colliding families %d, items %d"
            % (name, rel, n_rows, len(keys), len(hit), len(items)))
    if want_per:
        return rows, excl, blocked, per
    return rows, excl, blocked


def load_exclusion(path=None, expect_sha=None):
    """STAGE0b: the pinned MMLU-Pro collision list (sorted uuids), sha256-lf verified before it is parsed."""
    path = EXCL_PATH if path is None else path
    expect_sha = EXCL_SHA256 if expect_sha is None else expect_sha
    if not os.path.exists(path):
        refuse("the pinned exclusion list %s is absent" % path)
    got = sha256_lf(path)
    if got != expect_sha:
        refuse("the pinned exclusion list %s has sha256-lf %s, pinned %s" % (path, got, expect_sha))
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    u = obj["uuids"]
    if u != sorted(set(u)) or len(u) != obj["n"]:
        refuse("the pinned exclusion list is not a sorted set of %s uuids" % obj.get("n"))
    return set(u), obj


def leg_a4b(per, pinned, ev, tr, mm_stores=None):
    """STAGE0b A4b IDENTITY GATE: the MMLU-Pro-bearing stores' colliding uuids must EQUAL the pinned list, with the pinned counts
    (EXCL_N, EXCL_N_EVAL on EVAL, EXCL_N_TRAIN on TRAIN). -> (ok, mm set, {other store: its items outside mm}, missing stores)."""
    mm_stores = MMLU_STORES if mm_stores is None else mm_stores
    missing = [x for x in mm_stores if x not in per]
    mm = set()
    for x in mm_stores:
        mm |= per.get(x, set())
    same = (len(mm) == len(pinned)) if MUTANT == "a4b_counts_only" else (mm == pinned)
    ok = (not missing) and same and len(mm) == EXCL_N and len(mm & ev) == EXCL_N_EVAL and len(mm & tr) == EXCL_N_TRAIN
    other = {x: set(v) - mm for x, v in per.items() if set(v) - mm}
    return bool(ok), mm, other, missing


# =========================================================================================== records
def iter_records(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def stored_correct(rec, answer_letter):
    """The Records' stored correctness: status == 'correct'; if no status field, the stored extracted_answer against the
    question file's letter; neither -> None (the key is not stored: A2 / C1 unreachable, refused by the caller)."""
    if "status" in rec:
        return 1 if rec["status"] == "correct" else 0
    if "extracted_answer" in rec:
        return 1 if (rec["extracted_answer"] is not None and rec["extracted_answer"] == answer_letter) else 0
    return None


def scan_model(path, uuid_set, want_key, sample=None, answer_of=None, key_scope=None):
    """One pass over a model's file. Accesses only uuid, (want_key) the stored correctness, (sample) response text.
    Returns dict(n_records, present, dups, foreign, conflicts, key{uuid: 0/1}, resp{uuid: text}, missing_key, statuses).
    key_scope (STAGE0b, review B1): when given, the stored correctness is accessed ONLY for those uuids."""
    present = set()
    dups = foreign = conflicts = missing_key = 0
    key, resp, statuses = {}, {}, Counter()
    dup_uuids = set()
    fields = Counter()                  # PRESENCE of the three accessible fields (never their values) -- dry-run safe
    n = 0
    for rec in iter_records(path):
        n += 1
        for fk in ("status", "extracted_answer", "response"):
            if fk in rec:
                fields[fk] += 1
        u = rec.get("uuid")
        if u not in uuid_set:
            foreign += 1
            continue
        if u in present:
            dups += 1
            dup_uuids.add(u)
        present.add(u)
        if want_key and (key_scope is None or u in key_scope):
            v = stored_correct(rec, answer_of[u])
            if v is None:
                missing_key += 1
                continue
            if "status" in rec:
                statuses[rec["status"]] += 1
            if u in key and key[u] != v:
                conflicts += 1
            key[u] = v
        if sample is not None and u in sample:
            r = rec.get("response")
            resp[u] = r
    return dict(n_records=n, present=present, dups=dups, foreign=foreign, conflicts=conflicts, key=key, resp=resp,
                missing_key=missing_key, statuses=statuses, fields=fields, dup_uuids=dup_uuids)


# ---- the SuperGPQA official zero-shot extractor, ported VERBATIM (R4). Do not edit between the markers.
def safe_regex_search(pattern, text, flags=0):
    """upstream's wrapper without timeout_decorator (which does not work on Windows, as upstream's own TODO says)."""
    try:
        return re.search(pattern, text, flags)
    except Exception:
        return None


# <<UPSTREAM_BLOCK_BEGIN>>
def extract_option_labels(text, options='ABCDEFGHIJ'):
    if not isinstance(text, str) or not isinstance(options, str):
        return 'error'
    
    text = text.rstrip()
    last_line = text.split('\n')[-1]
    
    option_str = ''.join([chr(65 + i) for i in range(len(options))]) if options else 'ABCDEFGHIJ'
    
    patterns = [
        # e.g. "The final answer to this question is: A."
        #      "The best option is $\boxed{B}:"
        #      "The correct answer is (C)."
        f'[Tt]he\s+(?:\w+\s+)?(?:answer|option)(?:\w+\s+)?\s+is?:?\s*(?:[\*\$\\{{(\[\\\\(]*?(?:(?:\\\\boxed|\\\\mathbf|\\\\mathrm|\\\\text){{)?)*\s*([{option_str}])(?:\\\\?\}}?\$?\)?\]?\}}?)*(?:[\s:\.\*)]|$)',

        # e.g. "ANSWER: A"
        #      "Answer: $\boxed{B}."
        #      "ANSWER: (C):"
        f'(?i:Answer)[\*\s]*:\s*(?:[\*\$\\{{(\[\\\\(]*?(?:(?:\\\\boxed|\\\\mathbf|\\\\mathrm|\\\\text){{)?)*\s*([{option_str}])(?:\\\\?\}}?\$?\)?\]?\}}?)*(?:[\s:\.\*)]|$)',
        
        # e.g. "A"
        #      "$\boxed{B}$"
        #      "(C)."
        #      "[D]:"
        f'^[^\w\r\n]*(?:[\*\$\\{{(\[\\\\(]*?(?:(?:\\\\boxed|\\\\mathbf|\\\\mathrm|\\\\text){{)?)*\s*([{option_str}])(?:\\\\?\}}?\$?\)?\]?\}}?)*(?:[\s:\.\*)]|$)',
    ]

    for pattern in patterns:
        match = safe_regex_search(pattern, last_line, re.IGNORECASE)
        if match:
            return match.group(1)
    
    for pattern in patterns:
        match = safe_regex_search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_option_content(text, options_content=None):
    if not isinstance(text, str) or not isinstance(options_content, list):
        return 'error'
    
    escaped_options_content = [re.escape(option_content) for option_content in options_content]
    escaped_options_content_str = '|'.join(escaped_options_content)
    
    text = text.rstrip()
    last_line = text.split('\n')[-1]
        
    patterns = [
        f'[Tt]he\s+(?:\w+\s+)?(?:answer|option)(?:\w+\s+)?\s+is:?\s*(?:[\*\$\\{{\(\[\\\\(]*?(?:(?:\\\\boxed|\\\\mathbf|\\\\mathrm|\\\\text){{)?)*\s*({escaped_options_content_str})(?:\\\\?\}}?\$?\)?\]?\}}?)*(?:[\s:\.\*)]|$)',
        
        f'(?i:Answer)\s*(?:[\*\$\\{{\(\[\\\\(]*?(?:(?:\\\\boxed|\\\\mathbf|\\\\mathrm|\\\\text){{)?)*\s*({escaped_options_content_str})(?:\\\\?\}}?\$?\)?\]?\}}?)*(?:[\s:\.\*)]|$)',
        
        f'^[^\w\r\n]*(?:[\*\$\\{{\(\[\\\\(]*?(?:(?:\\\\boxed|\\\\mathbf|\\\\mathrm|\\\\text){{)?)*\s*({escaped_options_content_str})(?:\\\\?\}}?\$?\)?\]?\}}?)*(?:[\s:\.\*)]|$)',
    ]
    
    for pattern in patterns:
        match = safe_regex_search(pattern, last_line)
        if match:
            if match.group(1) in escaped_options_content:
                return options_content[escaped_options_content.index(match.group(1))]
            else:
                return match.group(1)
    
    for pattern in patterns:
        match = safe_regex_search(pattern, text)
        if match:
            if match.group(1) in escaped_options_content:
                return options_content[escaped_options_content.index(match.group(1))]
            else:
                return match.group(1)
    
    return None
# <<UPSTREAM_BLOCK_END>>
UPSTREAM_BLOCK_SHA256 = "24d32e051c0c73356e7a6fe15c3c554adb0ef3d8f3d8342ae88f1d1772a50317"


def reextract(response, options):
    """upstream calculate_accuracy's zero-shot branch (eval.py L131-L135)."""
    predict = extract_option_labels(response, 'ABCDEFGHIJ')
    if predict is None:
        predict = extract_option_content(response, options)
        try:
            predict = chr(options.index(predict) + 65) if predict else None
        except ValueError:              # review L4: a matched content that is not an option -> a re-extraction miss (R4)
            predict = None
    return predict


def upstream_block_sha(path=None):
    with open(path or os.path.abspath(__file__), "rb") as f:
        src = f.read().replace(b"\r\n", b"\n")
    a = src.index(b"# <<UPSTREAM_BLOCK_BEGIN>>\n") + len(b"# <<UPSTREAM_BLOCK_BEGIN>>\n")
    b = src.index(b"# <<UPSTREAM_BLOCK_END>>")
    return hashlib.sha256(src[a:b]).hexdigest()


def a2_sample(Q, train, n=A2_N):
    """R4: largest-remainder proportional allocation over disciplines, per-discipline draw from sorted TRAIN uuids."""
    by = defaultdict(list)
    for q in Q:
        if q["uuid"] in train:
            by[q["discipline"]].append(q["uuid"])
    tot = sum(len(v) for v in by.values())
    quota = {d: n * len(v) / tot for d, v in by.items()}
    alloc = {d: int(math.floor(x)) for d, x in quota.items()}
    rest = n - sum(alloc.values())
    for d in sorted(quota, key=lambda d: (-(quota[d] - alloc[d]), d))[:rest]:
        alloc[d] += 1
    rng = random.Random(seed_int(A2_SEED_STRING))
    out = []
    for d in sorted(by):
        out += rng.sample(sorted(by[d]), min(alloc[d], len(by[d])))
    return sorted(out), alloc


def a2_agreement(sample, resp, key, answer_of, options_of):
    agree = ours_miss = stored_miss = 0
    for u in sample:
        letter = reextract(resp.get(u), options_of[u])
        ours = 1 if (letter and letter == answer_of[u]) else 0
        if letter is None or letter == "error":
            ours_miss += 1
        st = key.get(u)
        if MUTANT == "stored_status_ignored":
            st = ours
        if st is None:
            stored_miss += 1
            continue
        agree += int(ours == st)
    return agree / len(sample), ours_miss, stored_miss


# =========================================================================================== policy, G, bootstrap
class Data:
    """Items (sorted uuid), model columns (sorted names), 0/1 key matrix A, sides, discipline / field / component codes."""

    def __init__(self, uuids, models, A, is_eval, disc, field, comp):
        self.uuids = list(uuids)
        self.models = list(models)
        self.A = np.asarray(A, dtype=np.int64)
        self.E = np.flatnonzero(is_eval)
        self.T = np.flatnonzero(~np.asarray(is_eval, dtype=bool))
        self.is_eval = np.asarray(is_eval, dtype=bool)
        self.disc_names = sorted(set(disc))
        self.field_names = sorted(set(field))
        self.dc = np.array([self.disc_names.index(d) for d in disc], dtype=np.int64)
        self.fc = np.array([self.field_names.index(f) for f in field], dtype=np.int64)
        self.comp = list(comp)
        self.n, self.m = self.A.shape
        self.rank = np.arange(self.m)                       # models are sorted: rank = column index
        self.fit_asserts = 0


def _argmax_lex(S, pooled, mask):
    """Row-wise lexicographic argmax of (S, pooled, -rank) over the admitted columns; exact int64 arithmetic."""
    Bg = np.int64(1 << 17)
    m = S.shape[1]
    tie = (np.int64(m - 1) - np.arange(m, dtype=np.int64))
    if MUTANT == "tiebreak_name_first":
        key = S * Bg * Bg + tie * Bg
    else:
        key = S * Bg * Bg + pooled[None, :] * Bg + tie[None, :]
    key = np.where(mask[None, :], key, np.int64(-1))
    return key.argmax(axis=1)


def fit(D, w, groups, n_groups, mask=None):
    """Weights w (int multiplicities) must sit on TRAIN only (guard, an explicit raise). Returns (best, pol[g]); pol = -1
    for a group with no TRAIN mass."""
    if MUTANT == "eval_leak_fit":
        w = w.copy(); w[D.E] += 1
    if int(w[D.E].sum()) != 0:
        raise SystemExit("[G3] a policy fit received weight on EVAL items")
    D.fit_asserts += 1
    mask = np.ones(D.m, dtype=bool) if mask is None else mask
    Aw = D.A * w[:, None]
    pooled = Aw.sum(axis=0)
    tie = np.arange(D.m, dtype=np.int64)
    pk = np.where(mask, pooled * np.int64(1 << 17) + (np.int64(D.m - 1) - tie), np.int64(-1))
    best = int(pk.argmax())
    S = np.zeros((n_groups, D.m), dtype=np.int64)
    np.add.at(S, groups, Aw)
    mass = np.bincount(groups, weights=w, minlength=n_groups)
    pol = _argmax_lex(S, pooled, mask).astype(np.int64)
    pol[mass <= 0] = -1
    return best, pol


def g_of(D, best, pol, groups, items, v):
    """(weighted) G over `items` with EVAL multiplicities v (aligned to items): policy pol[groups] (fallback best) vs best."""
    p = pol[groups[items]]
    p = np.where(p < 0, best, p)
    a_pol = D.A[items, p]
    a_bs = D.A[items, best]
    tot = v.sum()
    return float(((a_pol - a_bs) * v).sum() / tot), float((a_pol * v).sum() / tot), float((a_bs * v).sum() / tot)


def strat_resample(rng, groups_idx, size):
    w = np.zeros(size, dtype=np.int64)
    for idx in groups_idx:
        if len(idx):
            w[idx] += np.bincount(rng.integers(0, len(idx), len(idx)), minlength=len(idx))
    return w


def placebo_labels(D):
    """TRAIN discipline labels permuted (Random(42) over the label list in sorted-uuid order); EVAL keeps its true label."""
    lab = D.dc.copy()
    t = [int(i) for i in D.T]                           # D.uuids sorted -> T is in sorted-uuid order
    vals = [int(lab[i]) for i in t]
    if MUTANT != "placebo_unpermuted":
        random.Random(PLACEBO_SEED).shuffle(vals)
    for i, v in zip(t, vals):
        lab[i] = v
    return lab


def family_of(name):
    for pre, fam in FAMILY_RULES:
        if name.startswith(pre):
            return fam
    return name


def family_mask(D, w):
    pooled = (D.A * w[:, None]).sum(axis=0)
    best = {}
    for j, mname in enumerate(D.models):
        f = family_of(mname)
        if f not in best or pooled[j] > pooled[best[f]]:
            best[f] = j
    mask = np.zeros(D.m, dtype=bool)
    mask[list(best.values())] = True
    return mask


def scored_units(D, codes, names):
    """Units (disciplines or fields) with >= FLOOR EVAL items (A6 / field grain), listed before any key is read."""
    cnt = np.bincount(codes[D.E], minlength=len(names))
    return [i for i in range(len(names)) if cnt[i] >= FLOOR], cnt


def run_g(D, B_=B, seed=BOOT_SEED, log=None, hook=None):
    """Point + two-stage + i.i.d. for the arms: disc (C1), placebo, field (descriptive), family (descriptive)."""
    sd, _ = scored_units(D, D.dc, D.disc_names)
    sf, _ = scored_units(D, D.fc, D.field_names)
    sd_set = np.zeros(len(D.disc_names), dtype=bool); sd_set[sd] = True
    sf_set = np.zeros(len(D.field_names), dtype=bool); sf_set[sf] = True
    items_d = D.E if MUTANT == "g_all_eval" else D.E[sd_set[D.dc[D.E]]]
    items_f = D.E[sf_set[D.fc[D.E]]]
    plab = placebo_labels(D)
    nd, nf = len(D.disc_names), len(D.field_names)
    train_strata = [D.T[D.dc[D.T] == k] for k in range(nd)]
    # EVAL components within discipline: comp_groups[k] = list of item-index arrays
    comp_groups = []
    for k in range(nd):
        g = defaultdict(list)
        for i in D.E[D.dc[D.E] == k]:
            g[D.comp[i]].append(int(i))
        comp_groups.append([np.array(v, dtype=np.int64) for _, v in sorted(g.items())])

    def arms(w, vfull):
        best, pol = fit(D, w, D.dc, nd)
        pb, ppol = fit(D, w, plab, nd)
        fb, fpol = fit(D, w, D.fc, nf)
        fm = family_mask(D, w)
        mb, mpol = fit(D, w, D.dc, nd, mask=fm)
        r = {}
        r["disc"] = g_of(D, best, pol, D.dc, items_d, vfull[items_d]) if len(items_d) else (float("nan"),) * 3
        r["placebo"] = g_of(D, pb, ppol, D.dc, items_d, vfull[items_d]) if len(items_d) else (float("nan"),) * 3
        r["field"] = g_of(D, fb, fpol, D.fc, items_f, vfull[items_f]) if len(items_f) else (float("nan"),) * 3
        r["disc_on_field_items"] = g_of(D, best, pol, D.dc, items_f, vfull[items_f]) if len(items_f) else (float("nan"),) * 3
        r["family"] = g_of(D, mb, mpol, D.dc, items_d, vfull[items_d]) if len(items_d) else (float("nan"),) * 3
        return r, (best, pol, fb, fpol, fm, mb, mpol, pb, ppol)

    w0 = np.zeros(D.n, dtype=np.int64); w0[D.T] = 1
    v0 = np.zeros(D.n, dtype=np.int64); v0[D.E] = 1
    point, fits = arms(w0, v0)
    names = list(point)
    two = {k: np.empty(B_) for k in names}
    iid = {k: np.empty(B_) for k in names}
    rng = np.random.default_rng(seed)
    for b in range(B_):
        w = strat_resample(rng, train_strata, D.n)
        v = np.zeros(D.n, dtype=np.int64)
        for k in range(nd):
            cg = comp_groups[k]
            if cg:
                for j in rng.integers(0, len(cg), len(cg)):
                    v[cg[j]] += 1
        r, _ = arms(w, v)
        if hook is not None:
            hook(b, w, v, train_strata, comp_groups)
        for k in names:
            two[k][b] = r[k][0]
        if log and (b + 1) % 500 == 0:
            log("  two-stage replicate %d / %d" % (b + 1, B_))
    rng = np.random.default_rng(seed)
    best, pol, fb, fpol, fm, mb, mpol, pb, ppol = fits
    fixed = {"disc": (best, pol, D.dc, items_d), "placebo": (pb, ppol, D.dc, items_d), "field": (fb, fpol, D.fc, items_f),
             "disc_on_field_items": (best, pol, D.dc, items_f), "family": (mb, mpol, D.dc, items_d)}
    for b in range(B_):
        for k in names:
            bb, pp, gg, it = fixed[k]
            if len(it) == 0:
                iid[k][b] = float("nan"); continue
            vv = np.bincount(rng.integers(0, len(it), len(it)), minlength=len(it))
            iid[k][b] = g_of(D, bb, pp, gg, it, vv)[0]
    return dict(point=point, fits=fits, two=two, iid=iid, scored_disc=sd, scored_field=sf, items_d=items_d,
                items_f=items_f, B=B_)


def _var(x):
    x = np.asarray(x, dtype=np.float64)
    x = x[~np.isnan(x)]
    if len(x) < 2 or float(np.ptp(x)) == 0.0:
        return 0.0
    return float(np.var(x, ddof=1))


def interval(point, draws):
    se = math.sqrt(_var(draws))
    return dict(point=point, se=se, lo=point - Z * se, hi=point + Z * se,
                pct=tuple(float(x) for x in np.nanpercentile(draws, [2.5, 97.5])) if len(draws) else (float("nan"),) * 2)


def three_way(iv):
    """HELD iff wholly above 0, FAILED iff wholly below 0, UNDETERMINED otherwise."""
    if bool(iv["lo"] > 0):
        return "HELD"
    if bool(iv["hi"] < 0):
        return "FAILED"
    return "UNDETERMINED"


def placebo_fires(iv):
    if MUTANT == "placebo_trigger_ge":
        return bool(iv["lo"] >= 0)
    return bool(iv["lo"] > 0)


def comp_kish(D, items):
    c = Counter(D.comp[i] for i in items)
    s = list(c.values())
    return sum(x * x for x in s) / max(1, sum(s)), len(s)


# =========================================================================================== R (C2)
def r_readout(D, cells_order, n_null=N_NULL, seeds=NULL_SEEDS, progress=None):
    import profile_reliability_interaction as pri
    items = {name: [D.uuids[i] for i in D.E[D.dc[D.E] == D.disc_names.index(name)]] for name in cells_order}
    cells = {name: items[name] for name in cells_order}
    LAST["r_items"] = {name: list(v) for name, v in items.items()}
    col = {u: i for i, u in enumerate(D.uuids)}
    qsel = set(u for v in cells.values() for u in v)

    def build(cqs):
        idx = [col[u] for u in cqs]
        if not idx:
            return {}
        acc = D.A[idx].mean(axis=0)
        return {m: float(acc[j]) for j, m in enumerate(D.models)}
    out = pri.leg(cells, qsel, build, D.models, "SGPQA", progress=progress)
    iv = pri.intervals(out, "both")
    ivm = pri.intervals(out, "model")
    K = {u: {m: int(D.A[col[u], j]) for j, m in enumerate(D.models)} for u in qsel}
    nul = pri.null_tables(cells, K, D.models, n_null, seeds)
    reads = sorted(x[1] for x in nul["reads"])
    return dict(iv=iv, ivm=ivm, null_sorted=reads, null_model=sorted(x[0] for x in nul["reads"]), leg=out,
                clipped=nul["clipped"], iters=nul["iters"])


def c2_verdict(iv, null_sorted):
    """R5: re-halved jackknife bounds against the null's 19th of 20."""
    idx = 19 if MUTANT == "null_p95_index19" else NULL_P95_INDEX
    p95 = null_sorted[idx]
    lo, hi = (iv["lo_fx"], iv["hi_fx"]) if MUTANT == "jack_fixed" else (iv["lo_re"], iv["hi_re"])
    if bool(lo > p95):
        return "HELD", p95, lo, hi
    failed = bool(hi < p95) if MUTANT == "c2_upper_lt" else bool(hi <= p95)
    if failed:
        return "FAILED", p95, lo, hi
    return "UNDETERMINED", p95, lo, hi


# =========================================================================================== admission legs
def leg_a1(complete_names, n_files):
    need = 21 if MUTANT == "a1_ge_21" else MIN_MODELS
    return bool(len(complete_names) >= need), "A1 file-list zero-shot models %d (asserted %d%s); complete %d (>= %d required)" % (
        n_files, EXPECTED_ZS, "" if n_files == EXPECTED_ZS else ", MISMATCH printed, not a STOP", len(complete_names), MIN_MODELS)


def leg_a2(agree):
    """agree: {model: rate}. Returns (pass, admitted, excluded)."""
    if MUTANT == "a2_bar_gt":
        adm = sorted(m for m, r in agree.items() if r > A2_BAR)
    else:
        adm = sorted(m for m, r in agree.items() if r >= A2_BAR)
    exc = sorted(set(agree) - set(adm))
    return bool(len(adm) >= MIN_MODELS), adm, exc


def leg_a4(n_excl, n_items):
    share = n_excl / n_items if n_items else float("nan")
    ok = bool(share < A4_BAR) if MUTANT == "a4_strict" else bool(share <= A4_BAR)
    return ok, share


def leg_a6(scored):
    return bool(len(scored) >= MIN_SCORED)


# =========================================================================================== verdict text
def _pp(x):
    return "%+.2fpp" % (100 * float(x))


def score_range(v, lo, hi):
    return "HELD" if bool(v == v and lo <= v <= hi) else "FAILED"


def verdict_block(st):
    """Every registered criterion, prediction and falsifier has a print branch here; the selftest executes each."""
    L = []
    stop = st.get("stop")
    legs = st.get("legs", {})
    L.append("POPULATION: " + POPULATION)
    if stop:
        L.append("STOP AS REGISTERED: admission leg %s FAILED -- the refusal is the outcome; no criterion is read; no key or "
                 "correctness count is printed on a STOP path." % stop)
        L.append("C1: UNDETERMINED (BY STOP at %s)" % stop)
        L.append("C2: UNDETERMINED (BY STOP at %s)" % stop)
    else:
        c1 = st["c1"]
        if st["placebo_fires"]:
            L.append("C1: VOID (BY TRIGGER: the placebo's two-stage interval lies wholly above 0; the instrument manufactures "
                     "gain from noise). G %s [%s, %s] printed, not scored." % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"])))
        elif st["c1_class"] == "HELD":
            L.append("C1: HELD -- G %s, two-stage 95%% [%s, %s] lies wholly above 0 (recorded as notable: the verdict line is "
                     "DESCRIPTIVE-ONLY at the planned support)." % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"])))
        elif st["c1_class"] == "FAILED":
            L.append("C1: FAILED -- G %s, two-stage 95%% [%s, %s] lies wholly below 0." % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"])))
        else:
            L.append("C1: UNDETERMINED -- G %s, two-stage 95%% [%s, %s] contains 0 (the expected reading at the planned "
                     "support; changes no sentence)." % (_pp(c1["point"]), _pp(c1["lo"]), _pp(c1["hi"])))
        if not st["a6_pass"]:
            L.append("C2: UNDETERMINED-BY-SUPPORT (A6: %d scored disciplines < %d)" % (st["n_scored"], MIN_SCORED))
        else:
            c2, p95, lo, hi = st["c2"]
            if c2 == "HELD":
                L.append("C2: HELD -- R %.4f, jackknife 95%% lower bound %.4f > null p95 (19th of 20) %.4f." % (st["R"], lo, p95))
            elif c2 == "FAILED":
                L.append("C2: FAILED -- R %.4f, jackknife 95%% upper bound %.4f <= null p95 (19th of 20) %.4f." % (st["R"], hi, p95))
            else:
                L.append("C2: UNDETERMINED -- R %.4f, jackknife 95%% [%.4f, %.4f] against null p95 %.4f." % (st["R"], lo, hi, p95))
    # predictions
    P = []
    if stop and stop != "A4b":
        P.append("P1 legs A1, A2, A3, A5, A6 all pass (0.70): FAILED (%s)" % stop)
    elif stop == "A4b":
        P.append("P1 legs A1, A2, A3, A5, A6 all pass (0.70): UNDETERMINED (BY STOP at A4b: legs A1, A2, A5, A6 not reached)")
    else:
        P.append("P1 legs A1, A2, A3, A5, A6 all pass (0.70): HELD")
    for name, key, fmt in (("P1a A1 finds 49 zero-shot models (read: complete == 49) (0.85)", "p1a", None),
                           ("P1c >= 40 models pass A2 (0.75)", "p1c", None)):
        v = legs.get(key)
        if v is None:
            P.append("%s: UNDETERMINED (BY STOP: leg not reached)" % name)
        else:
            P.append("%s: %s" % (name, "HELD" if bool(v) else "FAILED"))
    if "n_scored" in st and st.get("a6_reached"):
        P.append("P2 SEEN (post-count, 10 scored disciplines): recorded as an identity, not scored (observed %d; %s)"
                 % (st["n_scored"], "equal" if int(st["n_scored"]) == 10 else "DIFFERS from the seen 10"))
    else:
        P.append("P2 SEEN (10 scored disciplines): not re-observed (BY STOP; an identity, never scored)")
    if stop:
        for p in ("P3 G = +1.0pp [-0.2, +2.5]", "P4 R = 0.85 [0.70, 0.93]", "P5 best single is the TRAIN argmax in >= 5 scored disciplines",
                  "P6 the placebo's interval covers 0", "P7 best zero-shot pooled EVAL accuracy <= 0.65"):
            P.append("%s: UNDETERMINED (BY STOP)" % p)
    else:
        c1 = st["c1"]
        if st["placebo_fires"]:
            P.append("P3 G = +1.0pp, 80% [-0.2, +2.5]: UNDETERMINED (BY TRIGGER: placebo)")
        else:
            P.append("P3 G = +1.0pp, 80%% [-0.2, +2.5] (observed %s): %s; realised C1 class %s (priors HELD 0.35 / UNDETERMINED 0.60 / "
                     "FAILED 0.05)" % (_pp(c1["point"]), score_range(c1["point"], -0.002, 0.025), st["c1_class"]))
        if st["a6_pass"]:
            P.append("P4 R = 0.85, 80%% [0.70, 0.93] (observed %.4f): %s; C2 HELD prior 0.85" % (st["R"], score_range(st["R"], 0.70, 0.93)))
        else:
            P.append("P4 R = 0.85 [0.70, 0.93]: UNDETERMINED (BY SUPPORT)")
        P.append("P5 best single is the TRAIN argmax in >= 5 scored disciplines (0.60) (observed %d): %s"
                 % (st["n_dominated"], "HELD" if bool(st["n_dominated"] >= 5) else "FAILED"))
        covers = bool(st["placebo"]["lo"] <= 0 <= st["placebo"]["hi"])
        P.append("P6 the placebo's interval covers 0 (0.90) ([%s, %s]): %s" % (_pp(st["placebo"]["lo"]), _pp(st["placebo"]["hi"]),
                                                                          "HELD" if covers else "FAILED"))
        P.append("P7 best zero-shot pooled EVAL accuracy <= 0.65 (0.85) (observed %.4f, %s): %s"
                 % (st["max_acc"], st["max_model"], "HELD" if bool(st["max_acc"] <= 0.65) else "FAILED"))
    L.append("PREDICTIONS:")
    L += ["  " + p for p in P]
    L.append("DESCRIPTIVE, STRUCK (bracket: the registrar's record of 2026-09-29, ruling 20, pre-key): the two-roster contrast "
             "(49 zero-shot vs the 26 five-shot base models) and the best-of-N resample floor; either returns only in a later "
             "registration with a definition and a whitelist amendment.")
    # falsifier
    if stop or not st.get("a6_pass"):
        L.append("F1: NOT EVALUATED (%s)" % ("STOP" if stop else "C2 UNDETERMINED-BY-SUPPORT"))
    elif st["c2"][0] == "FAILED":
        L.append("F1: FIRES -- C2 FAILED: the key-profile interaction licence does NOT transport to SuperGPQA's declared "
                 "disciplines at this roster; it overturns the framing's planned SQ5 corpus-invariance of the key-R clause, "
                 "not any recorded number.")
    else:
        L.append("F1: DOES NOT FIRE (C2 %s)." % st["c2"][0])
    if MUTANT == "numpy_bool_identity":          # the TOPIC-PARTITION D1 defect, reproduced for the mutant only
        L = [x for x in L if not (x.startswith("C1: HELD") and not (np.bool_(True) is True))]
    return L


POPULATION = ("SuperGPQA minus its MMLU-Pro stem_key collisions (1,251 of 26,529 items = 4.7156% excluded, 370 EVAL / 881 TRAIN; "
              "the programme's own corpus; STAGE0b says nothing about the excluded items or SuperGPQA as a whole)")


def write_once(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "w" if MUTANT == "write_mode_w" else "x"
    with open(path, mode, encoding="utf-8", newline="\n") as f:
        f.write(text)


# =========================================================================================== real modes
def prelude(out):
    if MUTANT is not None:
        refuse("MUTANT is set (%s): selftest-only" % MUTANT)
    sp0, ssha0 = load_split(SPLIT_PATH, SPLIT_SHA256)            # review L1: the split id is the FIRST printed line
    out("SPLIT %s (%s; SuperGPQA has no pool of record; reading R2) | split file sha256-lf=%s" % (sp0["split_id"], TEST_ID, ssha0))
    out(pin_line("SCRIPT supergpqa_stage0.py"))
    out(pin_line("       split_side.py", ss.__file__))
    out(pin_line("       content_closure.py", cc.__file__))
    out(pin_line("       profile_reliability_interaction.py", __import__("profile_reliability_interaction").__file__))
    b = upstream_block_sha()
    if b != UPSTREAM_BLOCK_SHA256:
        refuse("the ported extractor block drifted: %s != %s" % (b, UPSTREAM_BLOCK_SHA256))
    out("  extractor port block sha256-lf %s == upstream eval.py L32-L105 @ e31e8bf: OK" % b)


def common_inputs(out):
    import pool_guard as pg
    split, ssha = load_split(SPLIT_PATH, SPLIT_SHA256)
    out("SPLIT %s (SuperGPQA has no pool of record; reading R2) | split file %s sha256-lf=%s%s"
        % (split["split_id"], os.path.relpath(SPLIT_PATH, ROOT), ssha, "" if SPLIT_SHA256 else " (NOT YET PINNED in the script)"))
    Q, qsha = load_questions(QUESTION_FILE, out=out)
    out("  questions %d (planning figure %d, unsourced: %s)" % (len(Q), N_QUESTIONS_PLAN, "equal" if len(Q) == N_QUESTIONS_PLAN else "DIFFERS"))
    ok, _ = rederive_split(Q, split)
    if not ok:
        refuse("A3: the committed split does not re-derive from the question file")
    ev, tr = set(split["eval"]), set(split["train"])
    cl = closure_check(Q, ev, tr, out=out)
    wl_obj, wl = load_whitelist()
    out("  whitelist %s sha256-lf=%s: %d files (revision %s)" % (os.path.relpath(WHITELIST_PATH, ROOT), sha256_lf(WHITELIST_PATH),
                                                              len(wl), wl_obj.get("revisions")))
    return pg, split, ssha, Q, qsha, ev, tr, cl, wl_obj, wl


def zs_files(wl):
    out = []
    for rel in sorted(wl):
        m = ZS_RE.match(rel)
        if m:
            out.append((m.group(1), rel, os.path.join(DATA_DIR, "SuperGPQA-Records", *rel.split("/"))))
    return out


def mode_split(out=print):
    if MUTANT is not None:
        refuse("MUTANT is set")
    out(pin_line("SCRIPT supergpqa_stage0.py"))
    if os.path.exists(SPLIT_PATH):
        refuse("%s exists (write-once)" % SPLIT_PATH)
    Q, qsha = load_questions(QUESTION_FILE, out=out)
    obj = write_split(Q, qsha, out=out)
    cl = closure_check(Q, set(obj["eval"]), set(obj["train"]), out=out)
    out("  closure: sentinels %d; straddling families %d; EVAL components %d, twins in EVAL %d, component Kish %.4f; guard %s"
        % (cl["sentinels"], cl["straddle"], cl["n_comp"], cl["twins_eval"], cl["kish"], cl["guard"]))
    return 0


def a6_table(Q, ev, excl, out):
    cnt = Counter(q["discipline"] for q in Q if q["uuid"] in ev and q["uuid"] not in excl)
    alln = Counter(q["discipline"] for q in Q if q["uuid"] not in excl)
    scored = sorted(d for d, n in cnt.items() if n >= FLOOR)
    for d in sorted(alln, key=lambda d: (-cnt[d], d)):
        out("    %-22s items %5d  EVAL %5d  %s" % (d, alln[d], cnt[d], "SCORED" if d in scored else "unscored (< %d EVAL)" % FLOOR))
    fcnt = Counter((q["discipline"], q["field"]) for q in Q if q["uuid"] in ev and q["uuid"] not in excl)
    return scored, sum(1 for v in fcnt.values() if v >= FLOOR), len({(q["discipline"], q["field"]) for q in Q})


def mode_dry_run(out=print):
    prelude(out)
    pg, split, ssha, Q, qsha, ev, tr, cl, wl_obj, wl = common_inputs(out)
    out("A3 split exists and re-derives: EVAL %d / TRAIN %d; sentinels %d; straddling families %d; EVAL components %d "
        "(twins in EVAL %d, component Kish %.4f); CK-CLOSE guard %s -> %s"
        % (cl["n_eval"], cl["n_train"], cl["sentinels"], cl["straddle"], cl["n_comp"], cl["twins_eval"], cl["kish"], cl["guard"],
           "PASS" if (cl["straddle"] == 0 and cl["guard"] == "PASS") else "FAIL"))
    out("A4 cross-store collisions (stem_key, norm-v1):")
    rows, excl, blocked, per = collisions(Q, STORES, pg.open_ro, out=out, want_per=True)
    if blocked:
        out("A4b BLOCKED: %d store(s) cannot be read (failed precondition, never an outcome; --run refuses): %s"
            % (len(blocked), ", ".join(b[0] for b in blocked)))
    pinned, _eobj = load_exclusion()
    ok4b, mm, other, missing = leg_a4b(per, pinned, ev, tr)
    out("A4b IDENTITY GATE (STAGE0b): MMLU-Pro-bearing stores' colliding uuids %d (EVAL %d / TRAIN %d) vs the pinned %d (%d / %d); "
        "equal: %s%s -> %s" % (len(mm), len(mm & ev), len(mm & tr), EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN, mm == pinned,
                               ("; missing stores %s" % missing) if missing else "", "PASS" if ok4b else "STOP"))
    for x, v in sorted(other.items()):
        out("  further collisions in %s: %d items outside the MMLU-Pro list (EXCLUDED, counted)" % (x, len(v)))
    out("A4b excluded %d of %d items = %.4f%% in total (disclosed; no bar in STAGE0b)%s"
        % (len(excl), len(Q), 100 * len(excl) / len(Q), " on the readable stores only" if blocked else ""))
    lic = {r: (card_license(p) if os.path.exists(p) else None) for r, p in CARDS.items()}
    for r, p in CARDS.items():
        out("A5 card %s sha256=%s front-matter license=%s" % (r, sha256_file(p) if os.path.exists(p) else "MISSING", lic[r]))
    out("A5 %s (the data-steward's confirmation of record is separate)" % ("PASS" if all(v == "odc-by" for v in lic.values()) else "FAIL"))
    out("A6 disciplines (EVAL after closure and exclusions; listed BEFORE any key is read):")
    scored, nf120, nf = a6_table(Q, ev, excl, out)
    out("A6 %s: %d scored disciplines (>= %d required): %s" % ("PASS" if leg_a6(scored) else "UNDETERMINED-BY-SUPPORT for C2",
                                                              len(scored), MIN_SCORED, ", ".join(scored)))
    out("  field grain (DESCRIPTIVE): %d of %d fields with >= %d EVAL items" % (nf120, nf, FLOOR))
    files = zs_files(wl)
    out("A1 zero-shot files in the whitelist: %d (asserted %d)" % (len(files), EXPECTED_ZS))
    uu = set(q["uuid"] for q in Q)
    complete = []
    for name, rel, path in files:
        check_file_admitted(path, rel, wl, out=out)
        s = scan_model(path, uu, want_key=False)
        comp = bool(len(s["present"]) == len(uu))
        if comp:
            complete.append(name)
        out("    %-40s records %6d  present %6d  missing %5d  duplicate %4d  foreign %4d  fields present %s  %s"
            % (name, s["n_records"], len(s["present"]), len(uu) - len(s["present"]), s["dups"], s["foreign"],
               dict(sorted(s["fields"].items())), "complete (presence)" if comp else "INCOMPLETE"))
        no_key = s["n_records"] - max(s["fields"].get("status", 0), s["fields"].get("extracted_answer", 0))
        if no_key:
            out("      WARNING: %d records carry neither `status` nor `extracted_answer`: the stored key is absent there "
                "(--run refuses: the key of record would be unreachable)" % no_key)
    ok1, msg = leg_a1(complete, len(files))
    out("%s -> %s (presence only; --run adds the duplicate-conflict check of R3)" % (msg, "PASS" if ok1 else "FAIL"))
    out("A2 key audit: NOT RUN in --dry-run (it reads stored correctness on TRAIN); sample %d TRAIN uuids, bar %.2f, >= %d must remain"
        % (A2_N, A2_BAR, MIN_MODELS))
    out("PLANNED: B %d two-stage + %d i.i.d., default_rng(%d); placebo Random(%d); R: 40 halvings Random(7), null %d tables seeds 1..20, "
        "p95 = 19th of 20; outcome %s (exists: %s)" % (B, B, BOOT_SEED, PLACEBO_SEED, N_NULL, os.path.relpath(OUT_PATH, ROOT),
                                                      os.path.exists(OUT_PATH)))
    out("DRY-RUN: no stored correctness read, no statistic computed, nothing written.")
    return 0


def mode_run(out=print):
    """STAGE0b: A3, A4b, A1, A2, A5, A6; no key or correctness count on any STOP path (review B1)."""
    if os.path.exists(OUT_PATH):
        refuse("%s exists (write-once)" % OUT_PATH)
    if SPLIT_SHA256 is None:
        refuse("SPLIT_SHA256 is not pinned: the READY pins it before any run")
    buf = []

    def tee(s):
        out(s); buf.append(s)
    LAST.clear()
    prelude(tee)
    pg, split, ssha, Q, qsha, ev, tr, cl, wl_obj, wl = common_inputs(tee)
    pinned, eobj = load_exclusion()
    tee("  pinned exclusion list %s sha256-lf=%s: %d uuids (EVAL %d / TRAIN %d)"
        % (os.path.relpath(EXCL_PATH, ROOT), EXCL_SHA256, len(pinned), len(pinned & ev), len(pinned & tr)))
    st = dict(legs={})
    # ---- A3
    ok3 = bool(cl["straddle"] == 0 and cl["guard"] == "PASS")
    tee("A3 closure: straddling families %d, guard %s -> %s" % (cl["straddle"], cl["guard"], "PASS" if ok3 else "FAIL"))
    stop = None if ok3 else "A3"
    # ---- A4b (identity gate; every store readable)
    rows, excl, blocked, per = collisions(Q, STORES, pg.open_ro, out=tee, want_per=True)
    if blocked:
        refuse("FAILED PRECONDITION: store(s) unreadable: %s (no outcome written)" % ", ".join(b[0] for b in blocked))
    ok4b, mm, other, missing = leg_a4b(per, pinned, ev, tr)
    tee("A4b IDENTITY GATE: MMLU-Pro-bearing stores' colliding uuids %d (EVAL %d / TRAIN %d) vs the pinned %d (%d / %d); equal %s%s -> %s"
        % (len(mm), len(mm & ev), len(mm & tr), EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN, mm == pinned,
           ("; missing stores %s" % missing) if missing else "", "PASS" if ok4b else "FAIL"))
    for x, v in sorted(other.items()):
        tee("  further collisions in %s: %d items outside the MMLU-Pro list (EXCLUDED, counted)" % (x, len(v)))
    tee("A4b excluded %d of %d items = %.4f%% in total, EVAL %d / TRAIN %d (disclosed; no bar)"
        % (len(excl), len(Q), 100 * len(excl) / len(Q), len(excl & ev), len(excl & tr)))
    tee("POPULATION of every STAGE0b number: " + POPULATION)
    if stop is None:
        stop = None if ok4b else "A4b"
    st["excl"] = len(excl)
    answer_of = {q["uuid"]: q["answer_letter"] for q in Q}
    options_of = {q["uuid"]: q["options"] for q in Q}
    uu = set(answer_of)
    files = zs_files(wl)
    keys, agree, complete = {}, {}, []
    adm = []
    sample, alloc = a2_sample(Q, tr - excl)
    LAST.update(sample=list(sample), excl=set(excl), ev=set(ev), tr=set(tr))
    # ---- A1 (presence + the R3 conflict check; correctness accessed ONLY for the A2 sample and duplicated uuids)
    if stop is None:
        for name, rel, path in files:
            check_file_admitted(path, rel, wl, out=tee)
            s = scan_model(path, uu, want_key=True, sample=set(sample), answer_of=answer_of,
                           key_scope=None if MUTANT == "a1_full_key" else set(sample))
            conflicts = 0
            a1_keyed = set(s["key"])
            if s["dup_uuids"]:
                s2 = scan_model(path, uu, want_key=True, answer_of=answer_of, key_scope=set(s["dup_uuids"]))
                conflicts = s2["conflicts"]
                if set(s2["key"]) - set(s["dup_uuids"]):
                    refuse("B1 seal: the R3 conflict pass of %s read correctness outside the duplicated uuids" % name)
            if a1_keyed - set(sample):
                refuse("B1 seal: the A1 scan of %s read correctness for %d uuids outside the A2 sample" % (name, len(a1_keyed - set(sample))))
            LAST.setdefault("a1_keyed", {})[name] = len(a1_keyed)
            if s["missing_key"]:
                refuse("the Records carry no stored correctness for %d A2-sample rows of %s: the key of record is unreachable"
                       % (s["missing_key"], name))
            comp = bool(len(s["present"]) == len(uu) and conflicts == 0)
            tee("    %-40s records %6d missing %5d dup %4d conflicts %4d foreign %4d -> %s"
                % (name, s["n_records"], len(uu) - len(s["present"]), s["dups"], conflicts, s["foreign"],
                   "complete" if comp else "INCOMPLETE (excluded)"))
            if comp:
                complete.append(name)
                rate, om, sm = a2_agreement(sample, s["resp"], s["key"], answer_of, options_of)
                agree[name] = rate
                tee("      A2 %s agreement %.3f on the TRAIN sample (re-extraction miss %d / %d; stored miss %d)"
                    % (name, rate, om, len(sample), sm))
        ok1, msg = leg_a1(complete, len(files))
        tee(msg + " -> " + ("PASS" if ok1 else "FAIL"))
        st["legs"]["p1a"] = bool(len(complete) == EXPECTED_ZS)
        stop = None if ok1 else "A1"
    # ---- A2
    if stop is None:
        ok2, adm, exc = leg_a2(agree)
        st["legs"]["p1c"] = bool(len(adm) >= 40)
        tee("A2 sample %d TRAIN uuids after exclusion (allocation %s); admitted %d, EXCLUDED BY NAME %d: %s -> %s"
            % (len(sample), dict(sorted(alloc.items())), len(adm), len(exc), ", ".join("%s (%.3f)" % (m, agree[m]) for m in exc) or "none",
               "PASS" if ok2 else "FAIL"))
        stop = None if ok2 else "A2"
    # ---- A5
    if stop is None:
        lic = {r: card_license(p) for r, p in CARDS.items()}
        ok5 = all(v == "odc-by" for v in lic.values())
        tee("A5 licences %s -> %s" % (lic, "PASS" if ok5 else "FAIL"))
        stop = None if ok5 else "A5"
    # ---- A6
    if stop is None:
        tee("A6 disciplines (EVAL after closure and exclusions):")
        scored, nf120, nf = a6_table(Q, ev, excl, tee)
        st["a6_reached"] = True
        st["n_scored"] = len(scored)
        st["a6_pass"] = leg_a6(scored)
    if stop is not None:
        st["stop"] = stop
        for x in verdict_block(st):
            tee(x)
        write_once(OUT_PATH, "\n".join(buf) + "\n")
        LAST.update(st=st, text="\n".join(buf))
        return 0
    # ---- the key matrix over non-excluded items, admitted models
    items = sorted(u for u in uu if u not in excl)
    models = sorted(adm)
    iset = set(items)
    tee("KEY (read only now, after A6 passed): the admitted models' stored correctness on the %d non-excluded items "
        "[population: %s]" % (len(items), POPULATION))
    for name, rel, path in files:
        if name not in models:
            continue
        sk = scan_model(path, uu, want_key=True, answer_of=answer_of, key_scope=iset)
        keys[name] = sk["key"]
        nm = sum(v for k_, v in sk["statuses"].items() if k_ in ("miss", "error"))
        tee("    %-40s miss + error share %.4f (%d of %d non-excluded items; scored wrong)" % (name, nm / len(items), nm, len(items)))
    A = np.array([[keys[m][u] for m in models] for u in items], dtype=np.int64)
    qd = {q["uuid"]: q for q in Q}
    D = Data(items, models, A, np.array([u in ev for u in items]), [qd[u]["discipline"] for u in items],
             ["%s / %s" % (qd[u]["discipline"], qd[u]["field"]) for u in items], [qd[u]["stem_key"] for u in items])
    persist_key_db(D, ssha, out=tee)
    g = run_g(D, B_=RUN_B, log=tee)
    LAST.update(D=D, g=g, st=st)
    c1 = interval(g["point"]["disc"][0], g["two"]["disc"])
    pl = interval(g["point"]["placebo"][0], g["two"]["placebo"])
    se_iid = math.sqrt(_var(g["iid"]["disc"]))
    deff = (c1["se"] ** 2 / se_iid ** 2) if se_iid > 0 else float("nan")
    if c1["se"] == 0 or pl["se"] == 0:
        refuse("[G4] a two-stage variance is 0: every interval is degenerate")
    kish, ncomp = comp_kish(D, g["items_d"])
    n_d = len(g["items_d"])
    tee("C1 DENOMINATOR: EVAL items of the %d scored disciplines n = %d in %d CK-CLOSE components (component Kish %.4f); "
        "roster %d admitted models" % (len(g["scored_disc"]), n_d, ncomp, kish, D.m))
    tee("C1 G = acc(policy) %.4f - acc(best single %s) %.4f = %s; two-stage SE %.5f -> 95%% [%s, %s]; percentile [%s, %s]"
        % (g["point"]["disc"][1], D.models[g["fits"][0]], g["point"]["disc"][2], _pp(c1["point"]), c1["se"], _pp(c1["lo"]),
           _pp(c1["hi"]), _pp(c1["pct"][0]), _pp(c1["pct"][1])))
    tee("  SUPPORT (measured): SE_iid %.5f | SE_2stage %.5f -> DEFF %.3f, n_eff %.0f, MDE80 = 2.80 x SE = %s"
        % (se_iid, c1["se"], deff, n_d / deff if deff > 0 else float("nan"), _pp(2.80 * c1["se"])))
    tee("  SUPPORT (registered plan): " + PLAN_C1)
    tee("PLACEBO P = %s, two-stage 95%% [%s, %s] -> %s" % (_pp(pl["point"]), _pp(pl["lo"]), _pp(pl["hi"]),
                                                       "FIRES (VOIDS C1)" if placebo_fires(pl) else "does not fire"))
    best, pol = g["fits"][0], g["fits"][1]
    dom = 0
    tee("DOMINANCE column (per scored discipline: TRAIN argmax; is it the best single?):")
    for k in g["scored_disc"]:
        p = pol[k] if pol[k] >= 0 else best
        dom += int(p == best)
        tee("    %-22s %-40s %s" % (D.disc_names[k], D.models[p], "= best single" if p == best else ""))
    st.update(c1=c1, c1_class=three_way(c1), placebo=pl, placebo_fires=placebo_fires(pl), n_dominated=dom)
    if st["a6_pass"]:
        cells_order = sorted(D.disc_names[k] for k in g["scored_disc"])
        r = r_readout(D, cells_order, progress=None)
        iv = r["iv"]
        st["R"] = iv["R"]
        st["c2"] = c2_verdict(iv, r["null_sorted"])
        se = iv["se_re"]
        tee("C2 DENOMINATOR: %d scored disciplines x %d models; EVAL items %d" % (len(cells_order), D.m, n_d))
        tee("C2 R (interaction-only) %.4f; jackknife re-halved [%.4f, %.4f] (SE %.4f); fixed [%.4f, %.4f]; halving SD %.4f; "
            "model-only R %.4f" % (iv["R"], iv["lo_re"], iv["hi_re"], se, iv["lo_fx"], iv["hi_fx"], iv["sd"], r["ivm"]["R"]))
        tee("  null (logit-additive, 20 tables): interaction-only sorted %s; p95 (19th) %.4f; model-only median %.4f; clipped %d"
            % (["%.3f" % x for x in r["null_sorted"]], r["null_sorted"][NULL_P95_INDEX], r["null_model"][10], r["clipped"]))
        tee("  SUPPORT (measured): jackknife SE %.4f -> MDE80 %.4f | (registered plan): %s" % (se, 2.80 * se, PLAN_C2))
    acc = D.A[D.E].mean(axis=0)
    j = int(np.argmax(acc))
    st["max_acc"], st["max_model"] = float(acc[j]), D.models[j]
    tee("DESCRIPTIVE (decide nothing):")
    tee("  pooled EVAL accuracy per model (all %d EVAL items after exclusions; the 'mostly solved' readout P7):" % len(D.E))
    for jj in np.argsort(-acc, kind="stable"):
        tee("    %-40s %.4f" % (D.models[jj], acc[jj]))
    fi = interval(g["point"]["field"][0], g["two"]["field"])
    tee("  field grain: %d fields >= %d EVAL, n %d; G_field %s [%s, %s]; discipline policy on the same items %s"
        % (len(g["scored_field"]), FLOOR, len(g["items_f"]), _pp(fi["point"]), _pp(fi["lo"]), _pp(fi["hi"]),
           _pp(g["point"]["disc_on_field_items"][0])))
    fa = interval(g["point"]["family"][0], g["two"]["family"])
    tee("  family-collapsed (R6 map, %d families): G_family %s [%s, %s]" % (int(g["fits"][4].sum()), _pp(fa["point"]), _pp(fa["lo"]), _pp(fa["hi"])))
    tee("  miss + error share per model: printed in the KEY block above (read after A6 only; stored 'miss' / 'error' scored wrong).")
    for x in verdict_block(st):
        tee(x)
    write_once(OUT_PATH, "\n".join(buf) + "\n")
    LAST.update(text="\n".join(buf))
    return 0


def persist_key_db(D, ssha, out=print, path=KEY_DB):
    meta = {"script_blob": script_pins()["blob"], "split_sha256_lf": ssha, "whitelist_sha256_lf": sha256_lf(WHITELIST_PATH),
            "models": json.dumps(D.models), "n_items": str(D.n)}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
        got = dict(con.execute("SELECT key, value FROM meta").fetchall())
        con.close()
        if got != meta:
            refuse("%s exists with different meta: %s" % (path, got))
        out("  key DB %s exists with matching meta (not rewritten)" % path)
        return
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    con.execute("CREATE TABLE key (uuid TEXT NOT NULL, model TEXT NOT NULL, correct INTEGER NOT NULL, side TEXT NOT NULL, "
                "PRIMARY KEY (uuid, model)) WITHOUT ROWID")
    con.executemany("INSERT INTO meta VALUES (?, ?)", sorted(meta.items()))
    con.executemany("INSERT INTO key VALUES (?, ?, ?, ?)",
                    ((u, m, int(D.A[i, j]), "EVAL" if D.is_eval[i] else "TRAIN") for i, u in enumerate(D.uuids) for j, m in enumerate(D.models)))
    con.commit()
    con.close()
    out("  key DB written %s (%d rows) sha256=%s" % (path, D.n * D.m, sha256_file(path)))


# =========================================================================================== selftest
def _synthetic_Q(n_per_field=None, seed=5):
    rng = random.Random(seed)
    n_per_field = n_per_field or {("Alpha", "a1"): 400, ("Alpha", "a2"): 60, ("Beta", "b1"): 500, ("Gamma", "g1"): 450,
                                  ("Delta", "d1"): 420, ("Eps", "e1"): 410, ("Zeta", "z1"): 90}
    Q = []
    k = 0
    for (d, f), n in sorted(n_per_field.items()):
        for _ in range(n):
            k += 1
            Q.append(dict(uuid="u%05d" % k, question="synthetic question %d about %s %s" % (k, d, f), options=list("0123456789"),
                          answer_letter=LETTERS[rng.randrange(10)], discipline=d, field=f, subfield=f + "-s"))
    # two twin families (identical stems modulo case / whitespace) inside one field
    Q[1]["question"] = "  SYNTHETIC question 1 about Alpha a1 "
    Q[2]["question"] = "a shared stem"
    Q[3]["question"] = "A  shared stem"
    for q in Q:
        q["stem_key"] = ss.stem_key(q["question"])
    Q.sort(key=lambda q: q["uuid"])
    return Q


def _synthetic_D(Q, ev, models, gen, seed=11):
    rng = np.random.default_rng(seed)
    uu = [q["uuid"] for q in Q]
    disc = [q["discipline"] for q in Q]
    A = np.zeros((len(Q), len(models)), dtype=np.int64)
    for i, q in enumerate(Q):
        for j, m in enumerate(models):
            A[i, j] = int(rng.random() < gen(q["discipline"], j))
    return Data(uu, models, A, np.array([u in ev for u in uu]), disc, ["%s / %s" % (q["discipline"], q["field"]) for q in Q],
                [q["stem_key"] for q in Q])


class _Check:
    def __init__(self):
        self.n = 0
        self.fail = []

    def __call__(self, cond, what):
        self.n += 1
        if not bool(cond):
            self.fail.append(what)


def selftest(out=print, quick=False):
    chk = _Check()
    tmp = tempfile.mkdtemp(prefix="sgpqa_selftest_")
    # (1) extractor port verbatim + behaviour
    chk(upstream_block_sha() == UPSTREAM_BLOCK_SHA256, "port block sha")
    chk(reextract("Some reasoning.\nAnswer: C", list("abcdefghij")) == "C", "extract Answer: C")
    chk(reextract("The correct answer is (B).", list("abcdefghij")) == "B", "extract the correct answer is (B)")
    chk(reextract("no letter here at all 12345", ["x", "y"]) is None, "extract None")
    chk(reextract("## foo bar", ["foo bar", "baz"]) == "A", "extract content fallback")
    chk(reextract({"error": "x"}, list("ab")) == "error" or reextract({"error": "x"}, list("ab")) is not None, "non-str response")
    # (2) split: share, family closure, determinism, re-derivation, write-once
    Q = _synthetic_Q()
    d = draw_split(Q)
    chk(len(d["eval"] & d["train"]) == 0 and len(d["eval"] | d["train"]) == len(Q), "split partition")
    for fk, row in d["per_field"].items():
        chk(row["eval"] >= row["target"] and row["eval"] - row["target"] <= 1, "field share %s" % fk)
    chk(d["per_field"]["Alpha / a1"]["target"] == 120 and d["per_field"]["Alpha / a2"]["target"] == 18, "targets round-half-up")
    tw = [v for v in d["twins"].values()]
    chk(len(tw) == 2, "two twin families found")
    for v in tw:
        chk(len({u in d["eval"] for u in v}) == 1, "twin family on one side")
    d2 = draw_split(Q)
    chk(d2["eval"] == d["eval"], "split deterministic")
    chk(hashlib.sha256("\n".join(sorted(d["eval"])).encode()).hexdigest()[:16] == SELFTEST_SPLIT_PIN, "split vector pin")
    qpath = os.path.join(tmp, "q.jsonl")
    with open(qpath, "w", encoding="utf-8") as f:
        for q in Q:
            f.write(json.dumps(dict(uuid=q["uuid"], question=q["question"], options=str(q["options"]),
                                    answer_letter=q["answer_letter"], discipline=q["discipline"], field=q["field"],
                                    subfield=q["subfield"])) + "\n")
    Q2, qsha = load_questions(qpath, expect_sha=None, out=lambda s: None)
    chk([q["stem_key"] for q in Q2] == [q["stem_key"] for q in Q] and Q2[0]["options"] == list("0123456789"), "question loader")
    spath = os.path.join(tmp, "split.json")
    obj = write_split(Q2, qsha, path=spath, out=lambda s: None)
    ok, _ = rederive_split(Q2, obj)
    chk(ok, "split re-derives")
    try:
        write_split(Q2, qsha, path=spath, out=lambda s: None)
        chk(False, "split write-once")
    except FileExistsError:
        chk(True, "split write-once")
    cl = closure_check(Q2, set(obj["eval"]), set(obj["train"]), out=lambda s: None)
    chk(cl["straddle"] == 0 and cl["guard"] == "PASS" and cl["twins_eval"] + 0 >= 0, "closure check")
    if tw:
        u0 = tw[0][0]
        if u0 in obj["eval"]:
            bad_ev, bad_tr = set(obj["eval"]) - {u0}, set(obj["train"]) | {u0}
        else:
            bad_ev, bad_tr = set(obj["eval"]) | {u0}, set(obj["train"]) - {u0}
        clb = closure_check(Q2, bad_ev, bad_tr, out=lambda s: None)
        chk(clb["straddle"] == 1 and clb["guard"].startswith("REFUSED"), "closure detects a straddling twin")
    else:
        chk(False, "closure detects a straddling twin (no twin family to move)")
    # family spanning fields refuses
    Qx = [dict(q) for q in Q]
    Qx[-1]["question"] = Qx[2]["question"]; Qx[-1]["stem_key"] = Qx[2]["stem_key"]
    try:
        draw_split(Qx)
        chk(MUTANT == "split_no_family", "field-spanning family refuses")
    except SystemExit:
        chk(True, "field-spanning family refuses")
    # (3) seal / whitelist / size cap / sha
    rec_dir = os.path.join(tmp, "rec")
    os.makedirs(os.path.join(rec_dir, "zero-shot"))
    sealed = os.path.join(rec_dir, "zero-shot", "results_SuperGPQA-all_all_models.json")
    with open(sealed, "w") as f:
        f.write("{}")
    wl = {"zero-shot/results_SuperGPQA-all_all_models.json": {"bytes": 2, "sha256": sha256_file(sealed)}}
    try:
        check_file_admitted(sealed, "zero-shot/results_SuperGPQA-all_all_models.json", wl, out=lambda s: None)
        chk(False, "seal refuses")
    except SystemExit:
        chk(True, "seal refuses")
    good = os.path.join(rec_dir, "zero-shot", "m_SuperGPQA-all_zero-shot.jsonl")
    with open(good, "w") as f:
        f.write("{}\n")
    wl2 = {"zero-shot/m_SuperGPQA-all_zero-shot.jsonl": {"bytes": os.path.getsize(good), "sha256": sha256_file(good)}}
    chk(check_file_admitted(good, "zero-shot/m_SuperGPQA-all_zero-shot.jsonl", wl2, out=lambda s: None) == sha256_file(good), "admit")
    for bad, why in (({}, "not whitelisted"), ({"zero-shot/m_SuperGPQA-all_zero-shot.jsonl": {"bytes": 1, "sha256": "x"}}, "bytes"),
                     ({"zero-shot/m_SuperGPQA-all_zero-shot.jsonl": {"bytes": os.path.getsize(good), "sha256": "0" * 64}}, "sha")):
        try:
            check_file_admitted(good, "zero-shot/m_SuperGPQA-all_zero-shot.jsonl", bad, out=lambda s: None)
            chk(False, "refuse %s" % why)
        except SystemExit:
            chk(True, "refuse %s" % why)
    try:
        check_file_admitted(good, "zero-shot/m_SuperGPQA-all_zero-shot.jsonl", wl2, cap=1, out=lambda s: None)
        chk(False, "size cap")
    except SystemExit:
        chk(True, "size cap")
    # card licence front matter only
    cpath = os.path.join(tmp, "card.md")
    with open(cpath, "w") as f:
        f.write("---\nlicense: odc-by\n---\nlicense: mit\n")
    chk(card_license(cpath) == "odc-by", "card licence")
    with open(cpath, "w") as f:
        f.write("# no front matter\nlicense: odc-by\n")
    chk(card_license(cpath) is None, "card without front matter")
    # (4) records scan + stored correctness + A2
    uu = {q["uuid"] for q in Q}
    answer_of = {q["uuid"]: q["answer_letter"] for q in Q}
    options_of = {q["uuid"]: q["options"] for q in Q}
    mpath = os.path.join(rec_dir, "zero-shot", "m2.jsonl")
    with open(mpath, "w") as f:
        for i, q in enumerate(Q):
            right = (i % 4 != 0)
            letter = q["answer_letter"] if right else LETTERS[(LETTERS.index(q["answer_letter"]) + 1) % 10]
            f.write(json.dumps({"uuid": q["uuid"], "response": "blah\nAnswer: %s" % letter, "status": "correct" if right else "incorrect",
                                "answer_letter": "IGNORED"}) + "\n")
        f.write(json.dumps({"uuid": "foreign", "status": "correct"}) + "\n")
    sample, alloc = a2_sample(Q, set(obj["train"]))
    chk(len(sample) == A2_N and sum(alloc.values()) == A2_N and set(sample) <= set(obj["train"]), "A2 sample")
    s = scan_model(mpath, uu, want_key=True, sample=set(sample), answer_of=answer_of)
    chk(len(s["present"]) == len(uu) and s["foreign"] == 1 and s["dups"] == 0 and s["conflicts"] == 0, "scan counts")
    chk(sum(s["key"].values()) == sum(1 for i in range(len(Q)) if i % 4 != 0), "stored key")
    rate, om, sm = a2_agreement(sample, s["resp"], s["key"], answer_of, options_of)
    chk(rate == 1.0 and om == 0, "A2 agreement on a faithful file")
    # a file whose stored status disagrees with its text on 1 in 10 of the sample -> agreement 0.90
    mpath3 = os.path.join(rec_dir, "zero-shot", "m3.jsonl")
    flip = set(sorted(sample)[::10])
    with open(mpath3, "w") as f:
        for i, q in enumerate(Q):
            st_ = "correct" if (q["uuid"] not in flip) else "incorrect"
            f.write(json.dumps({"uuid": q["uuid"], "response": "Answer: %s" % q["answer_letter"], "status": st_}) + "\n")
    s3 = scan_model(mpath3, uu, want_key=True, sample=set(sample), answer_of=answer_of)
    rate3, _, _ = a2_agreement(sample, s3["resp"], s3["key"], answer_of, options_of)
    chk(abs(rate3 - 0.90) < 1e-12, "A2 detects stored-vs-text disagreement")
    # conflicting duplicate -> conflict counted; missing status and extracted_answer -> missing_key
    mpath4 = os.path.join(rec_dir, "zero-shot", "m4.jsonl")
    with open(mpath4, "w") as f:
        f.write(json.dumps({"uuid": Q[0]["uuid"], "status": "correct"}) + "\n")
        f.write(json.dumps({"uuid": Q[0]["uuid"], "status": "miss"}) + "\n")
        f.write(json.dumps({"uuid": Q[1]["uuid"], "extracted_answer": Q[1]["answer_letter"]}) + "\n")
        f.write(json.dumps({"uuid": Q[2]["uuid"], "response": "x"}) + "\n")
    s4 = scan_model(mpath4, uu, want_key=True, answer_of=answer_of)
    chk(s4["dups"] == 1 and s4["conflicts"] == 1 and s4["key"][Q[1]["uuid"]] == 1 and s4["missing_key"] == 1, "dup / conflict / fallback")
    # (5) legs at their boundaries
    chk(leg_a1(["m%d" % i for i in range(20)], 49)[0] is True, "A1 exactly 20 passes")
    chk(leg_a1(["m%d" % i for i in range(19)], 49)[0] is False, "A1 19 fails")
    ok2, adm, exc = leg_a2({"m%d" % i: (0.95 if i == 0 else 0.99) for i in range(20)} | {"bad": 0.949})
    chk(ok2 and "m0" in adm and exc == ["bad"], "A2 bar inclusive, exclusion by name")
    ok2b, adm_b, _ = leg_a2({"m%d" % i: (0.94 if i < 2 else 0.99) for i in range(21)})
    chk(not ok2b and len(adm_b) == 19, "A2 < 20 remain -> fail")
    chk(leg_a4(20, 1000)[0] is True and leg_a4(21, 1000)[0] is False, "A4 2.0% inclusive")
    chk(leg_a6(list("abcde")) is True and leg_a6(list("abcd")) is False, "A6 5 inclusive")
    # (6) collisions against synthetic stores, incl. a BLOCKED store (non-empty -wal)
    import pool_guard as pg
    sdb = os.path.join(tmp, "store.db")
    con = sqlite3.connect(sdb)
    con.execute("CREATE TABLE t (question TEXT)")
    con.execute("INSERT INTO t VALUES (?)", ("A SHARED   stem",))
    con.execute("INSERT INTO t VALUES (?)", ("unrelated",))
    con.execute("CREATE TABLE k (stem_key TEXT)")
    con.execute("INSERT INTO k VALUES (?)", (Q[10]["stem_key"],))
    con.commit(); con.close()
    bdb = os.path.join(tmp, "blocked.db")
    sqlite3.connect(bdb).close()
    with open(bdb + "-wal", "wb") as f:
        f.write(b"x" * 10)
    global DATA_ROOT
    saved = DATA_ROOT
    DATA_ROOT = tmp
    try:
        rows, excl, blocked = collisions(Q, [("T1", "data", "store.db", [("t", "question", "text"), ("k", "stem_key", "key")]),
                                             ("T2", "data", "blocked.db", [("t", "question", "text")])], pg.open_ro, out=lambda s: None)
    finally:
        DATA_ROOT = saved
    chk(len(blocked) == 1 and blocked[0][0] == "T2", "blocked store reported, not read")
    chk(excl == {Q[2]["uuid"], Q[3]["uuid"], Q[10]["uuid"]} and rows[0][4] == 2 and rows[0][5] == 3, "collision families excluded whole")
    # (7) policy fit: tie-break, EVAL guard, placebo, G restricted to scored
    models = ["m_a", "m_b", "m_c"]
    ev = set(obj["eval"])
    Dt = _synthetic_D(Q, ev, models, lambda d, j: 0.5)
    Dt.A[:] = 0
    # discipline Alpha: m_b and m_c tie on Alpha TRAIN; m_c has the higher pooled TRAIN accuracy -> m_c must win
    for i in Dt.T:
        if Dt.disc_names[Dt.dc[i]] == "Alpha":
            Dt.A[i, 1] = 1; Dt.A[i, 2] = 1
        else:
            Dt.A[i, 2] = 1 if (i % 2 == 0) else 0
            Dt.A[i, 0] = 1 if (i % 3 == 0) else 0
    w0 = np.zeros(Dt.n, dtype=np.int64); w0[Dt.T] = 1
    best, pol = fit(Dt, w0, Dt.dc, len(Dt.disc_names))
    chk(Dt.models[pol[Dt.disc_names.index("Alpha")]] == "m_c", "tie-break by pooled TRAIN accuracy")
    Dt.A[:] = 0
    for i in Dt.T:
        Dt.A[i, 1] = 1; Dt.A[i, 2] = 1
    best, pol = fit(Dt, w0, Dt.dc, len(Dt.disc_names))
    chk(Dt.models[best] == "m_b" and Dt.models[pol[0]] == "m_b", "full tie -> name order")
    try:
        wl_ = w0.copy(); wl_[Dt.E[0]] = 1
        fit(Dt, wl_, Dt.dc, len(Dt.disc_names))
        chk(False, "EVAL weight refused")
    except SystemExit:
        chk(True, "EVAL weight refused")
    # G exact value: construct A so that the policy gains exactly on scored EVAL items
    def gen_inter(dname, j):
        table = {"Alpha": (0.8, 0.3, 0.5), "Beta": (0.3, 0.8, 0.5), "Gamma": (0.3, 0.3, 0.9), "Delta": (0.5, 0.5, 0.5),
                 "Eps": (0.6, 0.4, 0.5), "Zeta": (0.2, 0.2, 0.9)}
        return table[dname][j]
    Dg = _synthetic_D(Q, ev, models, gen_inter)
    Bq = 60 if quick else 200
    gres = run_g(Dg, B_=Bq, seed=3)
    sd_names = [Dg.disc_names[k] for k in gres["scored_disc"]]
    chk("Zeta" not in sd_names and "Alpha" in sd_names, "scored disciplines exclude < 120 EVAL")
    it = gres["items_d"]
    chk(set(Dg.disc_names[k] for k in Dg.dc[it]) == set(sd_names), "G over scored-discipline EVAL items only")
    bb, pp = gres["fits"][0], gres["fits"][1]
    manual = np.mean([Dg.A[i, pp[Dg.dc[i]] if pp[Dg.dc[i]] >= 0 else bb] - Dg.A[i, bb] for i in it])
    chk(abs(manual - gres["point"]["disc"][0]) < 1e-12, "G point exact")
    c1 = interval(gres["point"]["disc"][0], gres["two"]["disc"])
    chk(three_way(c1) == "HELD", "strong interaction -> C1 HELD on the synthetic")
    pl = interval(gres["point"]["placebo"][0], gres["two"]["placebo"])
    chk(not placebo_fires(pl), "placebo does not fire on the synthetic")
    chk(Dg.fit_asserts == 4 * (1 + Bq), "fit asserts executed = 4 fitted arms x (1 + B)")
    # placebo trigger boundary: lo exactly 0 must NOT fire
    chk(placebo_fires(dict(lo=0.0, hi=0.1)) is False and placebo_fires(dict(lo=1e-9, hi=0.1)) is True, "placebo bar strict")
    # null G on a no-interaction synthetic -> interval covers 0 (UNDETERMINED)
    Dn = _synthetic_D(Q, ev, models, lambda d, j: (0.5, 0.52, 0.54)[j], seed=12)
    gn = run_g(Dn, B_=Bq, seed=3)
    chk(three_way(interval(gn["point"]["disc"][0], gn["two"]["disc"])) in ("UNDETERMINED", "FAILED"), "no interaction -> not HELD")
    chk(three_way(dict(lo=-0.02, hi=-0.001)) == "FAILED" and three_way(dict(lo=-0.01, hi=0.01)) == "UNDETERMINED"
        and three_way(dict(lo=0.001, hi=0.02)) == "HELD", "three-way bars")
    # family map
    chk(family_of("o3-mini-2025-01-31-high") == "OpenAI" and family_of("QwQ") == "Qwen" and family_of("qwen-max-2025-01-25") == "Qwen"
        and family_of("Mixtral-8x7B-Instruct-v0.1") == "Mistral" and family_of("K2-Chat") == "LLM360-K2", "family map")
    # (8) C2 verdict bars (the null's 19th of 20; re-halved bounds; upper at the bar -> FAILED)
    ns = [i / 100 for i in range(20)]           # p95 = 0.18
    ivx = dict(lo_re=0.19, hi_re=0.5, lo_fx=0.10, hi_fx=0.5)
    chk(c2_verdict(ivx, ns)[0] == "HELD", "C2 HELD above the 19th")
    chk(c2_verdict(dict(lo_re=0.185, hi_re=0.5, lo_fx=0.3, hi_fx=0.5), [x if x != 0.19 else 0.184 for x in ns])[0] == "HELD", "C2 p95 index")
    chk(c2_verdict(dict(lo_re=0.10, hi_re=0.18, lo_fx=0.10, hi_fx=0.19), ns)[0] == "FAILED", "C2 FAILED at the bar (<=)")
    chk(c2_verdict(dict(lo_re=0.10, hi_re=0.30, lo_fx=0.2, hi_fx=0.30), ns)[0] == "UNDETERMINED", "C2 UNDETERMINED")
    chk(c2_verdict(dict(lo_re=0.185, hi_re=0.30, lo_fx=0.10, hi_fx=0.30), ns)[0] == "HELD", "C2 uses re-halved bounds")
    # (9) R readout end to end on a small synthetic (estimator imported unchanged)
    if not quick:
        Dr = _synthetic_D(Q, ev, ["m%02d" % j for j in range(12)],
                          lambda dname, j: min(0.95, max(0.05, 0.5 + 0.03 * (j - 6) + (0.25 if (sum(map(ord, dname)) + j) % 3 == 0 else -0.1))),
                          seed=21)
        gr = run_g(Dr, B_=20, seed=3)
        cells = sorted(Dr.disc_names[k] for k in gr["scored_disc"])
        rr = r_readout(Dr, cells, n_null=N_NULL, seeds=NULL_SEEDS)
        chk(len(rr["null_sorted"]) == 20 and rr["iv"]["R"] == rr["iv"]["R"], "R readout runs")
        chk(c2_verdict(rr["iv"], rr["null_sorted"])[0] in ("HELD", "UNDETERMINED", "FAILED"), "R verdict class")
    # (10) every print branch of verdict_block, executed
    base = dict(legs=dict(p1a=True, p1c=True), a6_reached=True, n_scored=10, a6_pass=True,
                c1=dict(point=0.012, lo=0.002, hi=0.022), c1_class="HELD", placebo=dict(point=0.0, lo=-0.01, hi=0.01),
                placebo_fires=False, n_dominated=6, R=0.86, c2=("HELD", 0.55, 0.80, 0.92), max_acc=0.61, max_model="X")
    branches = {
        "C1: HELD": dict(), "C1: FAILED": dict(c1_class="FAILED", c1=dict(point=-0.02, lo=-0.03, hi=-0.01)),
        "C1: UNDETERMINED": dict(c1_class="UNDETERMINED", c1=dict(point=0.0, lo=-0.01, hi=0.01)),
        "C1: VOID (BY TRIGGER": dict(placebo_fires=True, placebo=dict(point=0.02, lo=0.01, hi=0.03)),
        "C2: HELD": dict(), "C2: FAILED": dict(c2=("FAILED", 0.60, 0.40, 0.55), R=0.5),
        "C2: UNDETERMINED --": dict(c2=("UNDETERMINED", 0.60, 0.50, 0.70)),
        "C2: UNDETERMINED-BY-SUPPORT": dict(a6_pass=False, n_scored=4),
        "STOP AS REGISTERED: admission leg A2": dict(stop="A2", legs=dict(p1a=True)),
        "F1: FIRES": dict(c2=("FAILED", 0.60, 0.40, 0.55)), "F1: DOES NOT FIRE": dict(),
        "F1: NOT EVALUATED (STOP)": dict(stop="A1", legs={}), "F1: NOT EVALUATED (C2 UNDETERMINED-BY-SUPPORT)": dict(a6_pass=False),
        "P1 legs A1, A2, A3, A5, A6 all pass (0.70): HELD": dict(), "P1 legs A1, A2, A3, A5, A6 all pass (0.70): FAILED (A3)": dict(stop="A3"),
        "P1 legs A1, A2, A3, A5, A6 all pass (0.70): UNDETERMINED (BY STOP at A4b": dict(stop="A4b", legs={}),
        "P1a A1 finds 49 zero-shot models (read: complete == 49) (0.85): FAILED": dict(legs=dict(p1a=False, p1c=True)),
        "P1a A1 finds 49 zero-shot models (read: complete == 49) (0.85): UNDETERMINED (BY STOP": dict(stop="A4b", legs={}),
        "P1c >= 40 models pass A2 (0.75): FAILED": dict(stop="A2", legs=dict(p1a=True, p1c=False)),
        "(observed 10; equal)": dict(), "(observed 12; DIFFERS from the seen 10)": dict(n_scored=12),
        "P2 SEEN (10 scored disciplines): not re-observed (BY STOP": dict(stop="A1", legs={}, a6_reached=False),
        "POPULATION: SuperGPQA minus its MMLU-Pro stem_key collisions (1,251 of 26,529 items = 4.7156% excluded": dict(),
        "DESCRIPTIVE, STRUCK (bracket: the registrar's record of 2026-09-29, ruling 20": dict(stop="A4b", legs={}),
        "P3 G = +1.0pp, 80% [-0.2, +2.5] (observed +1.20pp): HELD": dict(),
        "(observed +3.00pp): FAILED": dict(c1=dict(point=0.03, lo=0.02, hi=0.04)),
        "P3 G = +1.0pp, 80% [-0.2, +2.5]: UNDETERMINED (BY TRIGGER": dict(placebo_fires=True),
        "P3 G = +1.0pp [-0.2, +2.5]: UNDETERMINED (BY STOP)": dict(stop="A1"),
        "(observed 0.8600): HELD; C2": dict(), "(observed 0.9500): FAILED; C2": dict(R=0.95),
        "P4 R = 0.85 [0.70, 0.93]: UNDETERMINED (BY SUPPORT)": dict(a6_pass=False),
        "(observed 6): HELD": dict(), "(observed 4): FAILED": dict(n_dominated=4),
        "P6 the placebo's interval covers 0 (0.90) ([-1.00pp, +1.00pp]): HELD": dict(),
        "P6 the placebo's interval covers 0 (0.90) ([+0.10pp, +2.00pp]): FAILED": dict(placebo=dict(point=0.01, lo=0.001, hi=0.02)),
        "(observed 0.6100, X): HELD": dict(), "(observed 0.7000, X): FAILED": dict(max_acc=0.70),
    }
    for needle, delta in branches.items():
        stx = json.loads(json.dumps(base))
        stx.update(delta)
        if "c2" in stx and isinstance(stx["c2"], list):
            stx["c2"] = tuple(stx["c2"])
        lines = verdict_block(stx)
        chk(any(needle in x for x in lines), "verdict branch printed: %s" % needle)
    chk(not any("P1b" in x for x in verdict_block(json.loads(json.dumps(base)))), "STAGE0b prints no P1b (not registered in STAGE0b)")
    # (10b) STAGE0b: scoped key access, A4b gate, L4, the A6 floor, the bootstrap units (value-asserting)
    st_stage0b_units(chk, tmp, Q, obj, quick)
    if MUTANT is None or MUTANT in MODE_RUN_MUTANTS:          # mode_run-level mutants run it too
        st_mode_run(chk, tmp)
    # numpy booleans flow through bool(): a numpy-valued HELD still prints
    stn = json.loads(json.dumps(base)); stn["c2"] = tuple(stn["c2"])
    stn["n_dominated"] = np.int64(6); stn["max_acc"] = np.float64(0.61)
    chk(any(x.startswith("C1: HELD") for x in verdict_block(stn)), "numpy-valued state prints C1 HELD")
    # (11) write-once
    op = os.path.join(tmp, "out", "o.txt")
    write_once(op, "a\n")
    try:
        write_once(op, "b\n")
        chk(False, "outcome write-once")
    except FileExistsError:
        chk(True, "outcome write-once")
    with open(op) as f:
        chk(f.read() == "a\n", "outcome not overwritten")
    # (12) real modes refuse under a mutant
    if MUTANT is not None:
        try:
            prelude(lambda s: None)
            chk(False, "prelude refuses a mutant")
        except SystemExit:
            chk(True, "prelude refuses a mutant")
    ok = not chk.fail
    out("supergpqa_stage0 selftest: %d checks, %d failed%s%s" % (chk.n, len(chk.fail), "" if MUTANT is None else " [MUTANT %s]" % MUTANT,
                                                               (": " + "; ".join(chk.fail[:6])) if chk.fail else ""))
    return 0 if ok else 1


def st_stage0b_units(chk, tmp, Q, obj, quick):
    ev, tr = set(obj["eval"]), set(obj["train"])
    uu = {q["uuid"] for q in Q}
    answer_of = {q["uuid"]: q["answer_letter"] for q in Q}
    # scoped key access (review B1): only the scoped uuids' correctness is read; duplicated uuids are listed
    mp = os.path.join(tmp, "scoped.jsonl")
    with open(mp, "w", encoding="utf-8") as f:
        for q in Q:
            f.write(json.dumps({"uuid": q["uuid"], "response": "Answer: A", "status": "correct"}) + "\n")
        f.write(json.dumps({"uuid": Q[5]["uuid"], "status": "incorrect"}) + "\n")
    scope = {Q[0]["uuid"], Q[1]["uuid"]}
    sk = scan_model(mp, uu, want_key=True, answer_of=answer_of, key_scope=scope)
    chk(set(sk["key"]) == scope and sum(sk["statuses"].values()) == 2 and sk["dup_uuids"] == {Q[5]["uuid"]} and sk["conflicts"] == 0,
        "B1 scoped key: correctness read for the 2 scoped uuids only; the duplicate listed, its conflict not read")
    s2 = scan_model(mp, uu, want_key=True, answer_of=answer_of, key_scope=sk["dup_uuids"])
    chk(s2["conflicts"] == 1 and set(s2["key"]) == {Q[5]["uuid"]}, "B1 the R3 conflict check on the duplicated uuid alone")
    # A4b identity gate (values)
    global EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN
    saved = (EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN)
    pin = {Q[2]["uuid"], Q[3]["uuid"], Q[10]["uuid"]}
    try:
        EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN = 3, len(pin & ev), len(pin & tr)
        per = {"M1": {Q[2]["uuid"], Q[3]["uuid"]}, "M2": {Q[10]["uuid"]}, "O1": {Q[10]["uuid"], Q[20]["uuid"]}}
        ok, mm, other, missing = leg_a4b(per, pin, ev, tr, mm_stores=("M1", "M2"))
        chk(ok and mm == pin and other == {"O1": {Q[20]["uuid"]}} and not missing, "A4b PASS on the pinned set; another store's extra item counted")
        chk(not leg_a4b(dict(per, M2=set()), pin, ev, tr, mm_stores=("M1", "M2"))[0], "A4b STOP on a smaller collision set")
        chk(not leg_a4b(dict(per, M2={Q[10]["uuid"], Q[30]["uuid"]}), pin, ev, tr, mm_stores=("M1", "M2"))[0], "A4b STOP on a larger collision set")
        chk(not leg_a4b({"M1": per["M1"]}, pin, ev, tr, mm_stores=("M1", "M2"))[0], "A4b STOP when an MMLU-bearing store is missing")
        # C11-3 (Y11-2): same size AND same EVAL / TRAIN counts, a different set -> STOP (set equality, not counts)
        side10 = Q[10]["uuid"] in ev
        swap = next(q["uuid"] for q in Q if q["uuid"] not in pin and (q["uuid"] in ev) == side10 and q["uuid"] not in per["O1"])
        per_sw = dict(per, M2={swap})
        mm_sw = per_sw["M1"] | per_sw["M2"]
        chk(len(mm_sw) == len(pin) and len(mm_sw & ev) == EXCL_N_EVAL and len(mm_sw & tr) == EXCL_N_TRAIN and mm_sw != pin
            and not leg_a4b(per_sw, pin, ev, tr, mm_stores=("M1", "M2"))[0],
            "A4b STOP on a same-size, same-side-count, DIFFERENT collision set (set equality decides)")
        EXCL_N_EVAL = EXCL_N_EVAL + 1
        chk(not leg_a4b(per, pin, ev, tr, mm_stores=("M1", "M2"))[0], "A4b STOP on a wrong EVAL count")
    finally:
        EXCL_N, EXCL_N_EVAL, EXCL_N_TRAIN = saved
    # L4: a matched content that is not an option -> a miss, not a crash
    import types
    saved_eoc = globals()["extract_option_content"]
    globals()["extract_option_content"] = lambda text, options_content=None: "not an option"
    try:
        chk(reextract("nothing labelled", ["x", "y"]) is None, "L4 a non-option content match is a re-extraction miss")
    finally:
        globals()["extract_option_content"] = saved_eoc
    # X11: the A6 floor is 120 inclusive (a discipline with EXACTLY 120 EVAL items is scored)
    Qf = [dict(uuid="f%04d" % i, discipline="Exact", field="e", question="x", answer_letter="A") for i in range(120)] + \
         [dict(uuid="g%04d" % i, discipline="Short", field="s", question="y", answer_letter="A") for i in range(119)]
    scored_f, _, _ = a6_table(Qf, {q["uuid"] for q in Qf}, set(), lambda s_: None)
    chk(scored_f == ["Exact"], "A6 floor: 120 EVAL items scored, 119 not")
    # X9 / X10: the two-stage units, observed per replicate on a synthetic D
    models = ["m_a", "m_b", "m_c"]
    Dg = _synthetic_D(Q, ev, models, lambda d, j: (0.4, 0.5, 0.6)[j], seed=31)
    seen = dict(train_ok=True, multi_comp=False, comp_const=True)

    def hook(b, w, v, train_strata, comp_groups):
        for k, idx in enumerate(train_strata):
            if int(w[Dg.T[Dg.dc[Dg.T] == k]].sum()) != int((Dg.dc[Dg.T] == k).sum()):
                seen["train_ok"] = False
        for cg in comp_groups:
            drawn = [int(v[c[0]]) for c in cg if len(c)]
            if sum(1 for x in drawn if x > 0) > 1:
                seen["multi_comp"] = True
            if sum(drawn) != len(cg):
                seen["comp_const"] = False
            for c in cg:
                if len(set(int(x) for x in v[c])) > 1:
                    seen["comp_const"] = False
    run_g(Dg, B_=8, seed=3, hook=hook)
    chk(seen["train_ok"], "X10 two-stage TRAIN resample keeps every discipline's TRAIN count (stratified)")
    chk(seen["multi_comp"] and seen["comp_const"], "X9 two-stage EVAL draws whole components, several per discipline, as many as it has")


def _fixture_run(tmp, mode):
    """A SYNTHETIC run fixture (the review's runfix.py): question file, cards, split, 22 model files, a whitelist, two stores
    (an MMLU-bearing one colliding with 30 uuids and another colliding with 5 more); mode 'pass', 'stop' (the pinned list
    has 29 of the 30) or 'blocked' (a store with a non-empty -wal). Every module path is redirected into tmp."""
    import pool_guard as pg
    d = os.path.join(tmp, "run_" + mode)
    os.makedirs(d)
    Q = _synthetic_Q()
    qf = os.path.join(d, "SuperGPQA", "SuperGPQA-all.jsonl")
    os.makedirs(os.path.dirname(qf))
    with open(qf, "w", encoding="utf-8", newline="\n") as f:
        for q in Q:
            f.write(json.dumps(dict(uuid=q["uuid"], question=q["question"], options=str(q["options"]), answer_letter=q["answer_letter"],
                                    discipline=q["discipline"], field=q["field"], subfield=q["subfield"])) + "\n")
    for r in ("SuperGPQA", "SuperGPQA-Records"):
        os.makedirs(os.path.join(d, r), exist_ok=True)
        with open(os.path.join(d, r, "README.md"), "w") as f:
            f.write("---\nlicense: odc-by\n---\n")
    Q2, _ = load_questions(qf, expect_sha=None, out=lambda s_: None)
    sp = os.path.join(d, "split.json")
    obj = write_split(Q2, None, path=sp, out=lambda s_: None)
    ev = set(obj["eval"])
    rng = random.Random(3)
    wl = {"files": []}
    zs = os.path.join(d, "SuperGPQA-Records", "zero-shot")
    os.makedirs(zs)
    for j in range(22):
        name = "Model%02d" % j
        rel = "zero-shot/%s_SuperGPQA-all_zero-shot.jsonl" % name
        pth = os.path.join(d, "SuperGPQA-Records", *rel.split("/"))
        with open(pth, "w", encoding="utf-8", newline="\n") as f:
            for q in Q2:
                pr = 0.3 + 0.02 * j + (0.2 if (sum(map(ord, q["discipline"])) + j) % 3 == 0 else 0)
                right = rng.random() < pr
                letter = q["answer_letter"] if right else LETTERS[(LETTERS.index(q["answer_letter"]) + 1) % 10]
                f.write(json.dumps({"uuid": q["uuid"], "response": "Answer: %s" % letter, "status": "correct" if right else "incorrect"}) + "\n")
        wl["files"].append({"path": rel, "bytes": os.path.getsize(pth), "sha256": sha256_file(pth)})
    wlp = os.path.join(d, "wl.json")
    with open(wlp, "w") as f:
        json.dump(wl, f)
    coll = [q for q in Q2 if q["discipline"] == "Beta"][:30]
    more = [q for q in Q2 if q["discipline"] == "Beta"][30:35]
    for nm, rows_ in (("mm.db", coll), ("other.db", more)):
        c = sqlite3.connect(os.path.join(d, nm))
        c.execute("CREATE TABLE t (question TEXT)")
        c.executemany("INSERT INTO t VALUES (?)", [(q["question"],) for q in rows_])
        c.commit()
        c.close()
    stores = [("S01 MMLU-Pro", "data", "mm.db", [("t", "question", "text")]), ("S09 JudgeBench", "data", "other.db", [("t", "question", "text")])]
    if mode == "blocked":
        c = sqlite3.connect(os.path.join(d, "blk.db")); c.execute("CREATE TABLE t (question TEXT)"); c.commit(); c.close()
        with open(os.path.join(d, "blk.db-wal"), "wb") as f:
            f.write(b"x" * 16)
        stores.append(("S04 20NG", "data", "blk.db", [("t", "question", "text")]))
    pin = sorted(q["uuid"] for q in coll)
    if mode == "stop":
        pin = pin[:-1]
    ep = os.path.join(d, "excl.json")
    txt = json.dumps(dict(n=len(pin), uuids=pin), indent=1, sort_keys=True) + "\n"
    with open(ep, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    pset = set(pin)
    return dict(d=d, qf=qf, sp=sp, wlp=wlp, ep=ep, stores=stores, n_ev=len(pset & ev), n_tr=len(pset - ev), n=len(pin), ev=ev,
                coll={q["uuid"] for q in coll}, more={q["uuid"] for q in more})


def _with_fixture(fx, fn):
    g = globals()
    names = ("ROOT", "DATA_DIR", "DATA_ROOT", "QUESTION_FILE", "CARDS", "SPLIT_PATH", "SPLIT_SHA256", "WHITELIST_PATH", "OUT_DIR",
             "OUT_PATH", "KEY_DB", "STORES", "EXCL_PATH", "EXCL_SHA256", "EXCL_N", "EXCL_N_EVAL", "EXCL_N_TRAIN", "MMLU_STORES", "RUN_B")
    saved = {k: g[k] for k in names}
    saved_def = (load_questions.__defaults__, load_whitelist.__defaults__, persist_key_db.__defaults__)
    try:
        d = fx["d"]
        g.update(ROOT=d, DATA_DIR=d, DATA_ROOT=d, QUESTION_FILE=fx["qf"], CARDS={k: os.path.join(d, k.split("/")[1], "README.md") for k in saved["CARDS"]},
                 SPLIT_PATH=fx["sp"], SPLIT_SHA256=sha256_lf(fx["sp"]), WHITELIST_PATH=fx["wlp"], OUT_DIR=os.path.join(d, "out"),
                 OUT_PATH=os.path.join(d, "out", "o.txt"), KEY_DB=os.path.join(d, "out", "k.db"), STORES=fx["stores"], EXCL_PATH=fx["ep"],
                 EXCL_SHA256=sha256_lf(fx["ep"]), EXCL_N=fx["n"], EXCL_N_EVAL=fx["n_ev"], EXCL_N_TRAIN=fx["n_tr"], MMLU_STORES=("S01 MMLU-Pro",),
                 RUN_B=40)
        load_questions.__defaults__ = (None, print)
        load_whitelist.__defaults__ = (fx["wlp"],)
        persist_key_db.__defaults__ = (print, g["KEY_DB"])
        try:
            rc = fn()
        except SystemExit as e:
            rc = "SystemExit: %s" % e
        txt = open(g["OUT_PATH"], encoding="utf-8").read() if os.path.exists(g["OUT_PATH"]) else ""
        kdb = g["KEY_DB"]
        return rc, txt, kdb
    finally:
        g.update(saved)
        load_questions.__defaults__, load_whitelist.__defaults__, persist_key_db.__defaults__ = saved_def


def st_mode_run(chk, tmp):
    """READY 1adce88 H1: mode_run EXECUTED on synthetic fixtures, both paths, with exact-value assertions."""
    # ---- STOP at A4b: the pinned list has 29 of the 30 MMLU-bearing collisions
    fx = _fixture_run(tmp, "stop")
    rc, txt, _ = _with_fixture(fx, lambda: mode_run(out=lambda s_: None))
    lines = txt.splitlines()
    chk(rc == 0 and lines and lines[0].startswith("SPLIT sg"), "L1 the SPLIT line is the first printed line of --run")
    chk("STOP AS REGISTERED: admission leg A4b FAILED" in txt and "A4b IDENTITY GATE" in txt and "equal False" in txt,
        "STOP path: the A4b identity gate STOPs (29 pinned vs 30 found)")
    chk(not any(w in txt for w in ("statuses", "'correct'", "'incorrect'", "agreement", "miss + error")),
        "B1 the STOP outcome prints no key or correctness count (no model file was read)")
    chk("P1 legs A1, A2, A3, A5, A6 all pass (0.70): UNDETERMINED (BY STOP at A4b" in txt and "C1: UNDETERMINED (BY STOP at A4b)" in txt,
        "STOP path: P1 / C1 UNDETERMINED by the A4b STOP")
    # ---- BLOCKED store refuses, nothing written
    fx = _fixture_run(tmp, "blocked")
    rc, txt, _ = _with_fixture(fx, lambda: mode_run(out=lambda s_: None))
    chk(isinstance(rc, str) and "FAILED PRECONDITION" in rc and "S04 20NG" in rc and txt == "", "a BLOCKED store refuses --run; nothing written")
    # ---- PASS path
    fx = _fixture_run(tmp, "pass")
    rc, txt, kdb = _with_fixture(fx, lambda: mode_run(out=lambda s_: None))
    L = LAST
    chk(rc == 0 and "A4b IDENTITY GATE" in txt and "-> PASS" in txt.split("A4b IDENTITY GATE")[1].split("\n")[0]
        and "further collisions in S09 JudgeBench: 5 items" in txt, "PASS path: A4b PASS; the other store's 5 collisions excluded and counted")
    excl = fx["coll"] | fx["more"]
    chk(set(L.get("excl", ())) == excl, "the excluded set is the 30 + 5 colliding uuids")
    chk(set(L.get("sample", ())) <= (set(L.get("tr", ())) - excl) and len(L.get("sample", ())) == A2_N,
        "X3 the A2 sample is TRAIN minus the excluded uuids")
    per_model = [ln for ln in txt.splitlines() if ln.strip().startswith("Model") and " records " in ln]
    chk(len(per_model) == 22 and not any("statuses" in ln or "correct" in ln for ln in per_model),
        "B1 the per-model leg lines print presence / duplicates / conflicts only")
    a1k = L.get("a1_keyed", {})
    chk(len(a1k) == 22 and all(0 < v <= A2_N for v in a1k.values()) and max(a1k.values()) < len(_synthetic_Q()) - len(fx["coll"] | fx["more"]),
        "C11-3 the A1 scan reads correctness for at most the %d A2-sample uuids per model (max %s), never the full key"
        % (A2_N, max(a1k.values()) if a1k else None))
    con = sqlite3.connect("file:%s?mode=ro" % kdb.replace("\\", "/"), uri=True) if kdb and os.path.exists(kdb) else None
    ku = set(u for (u,) in con.execute("SELECT DISTINCT uuid FROM key")) if con else set()
    ev_acc = {}
    if con:
        for m_, c_, n_ in con.execute("SELECT model, SUM(correct), COUNT(*) FROM key WHERE side = 'EVAL' GROUP BY model"):
            ev_acc[m_] = c_ / n_
        con.close()
    chk(ku and not (ku & excl) and len(ku) == len(_synthetic_Q()) - len(excl), "X2 the key DB holds the non-excluded uuids only")
    st, D, g = L.get("st", {}), L.get("D"), L.get("g")
    chk(D is not None and abs(st.get("max_acc", -1) - max(ev_acc.values())) < 1e-12, "X8 P7's maximum is over EVAL items only")
    chk(D is not None and "c1" in st, "PASS path: the run reached C1")
    # C11-4: STAGE0b's Support (a)-(f), recomputed from its inputs (d 0.15627, n 7,396, DEFF 1.312), printed by --run
    se_b = math.sqrt(0.15627 / 7396) * math.sqrt(1.312)
    sup = [ln for ln in txt.splitlines() if "SUPPORT (registered plan):" in ln]
    chk(len(sup) == 1 and ("n_EVAL 7,396 in 7,395" in sup[0]) and ("n_eff %s" % format(round(7396 / 1.312), ",") in sup[0])
        and ("SE %.6f" % se_b in sup[0]) and ("MDE80 %.2fpp" % (100 * 2.80 * se_b) in sup[0]) and "7,959" not in txt,
        "C11-4 --run prints STAGE0b's plan line: n 7,396, n_eff 5,637, SE %.6f, MDE80 %.2fpp (STAGE0's 7,959 absent)" % (se_b, 100 * 2.80 * se_b))
    if D is not None and "c1" in st:
        sd2 = float(np.std(g["two"]["disc"], ddof=1))
        chk(abs(st["c1"]["se"] - sd2) < 1e-12 and abs(st["c1"]["lo"] - (st["c1"]["point"] - Z * sd2)) < 1e-12,
            "X12 C1 SE = the SD of the TWO-STAGE draws (%.6f)" % sd2)
        ri = L.get("r_items", {})
        chk(ri and all(u in fx["ev"] for v in ri.values() for u in v), "X4 the R cells hold EVAL uuids only")
        plab = placebo_labels(D)
        chk(np.array_equal(plab[D.E], D.dc[D.E]) and not np.array_equal(plab[D.T], D.dc[D.T]),
            "X5 the placebo permutes TRAIN labels only")
    chk("POPULATION of every STAGE0b number: SuperGPQA minus its MMLU-Pro stem_key collisions" in txt
        and "DESCRIPTIVE, STRUCK (bracket: the registrar's record of 2026-09-29, ruling 20, pre-key)" in txt and "UNDEFINED (review M1" not in txt,
        "PASS path: the population words and the ruling-20 STRUCK line are printed")


SELFTEST_SPLIT_PIN = "d68e38d942dae8eb"      # sha256(LF-joined sorted EVAL uuids of _synthetic_Q())[:16]; pins R1


def mutants(out=print):
    global MUTANT
    killed = []
    for m in MUTANTS:
        MUTANT = m
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = selftest(out=print, quick=True)
        except BaseException as e:           # a mutant that crashes the selftest is killed too
            rc = "crash: %s" % str(e)[:80]
        MUTANT = None
        k = rc != 0
        killed.append(k)
        out("  mutant %-24s %s  (%s)" % (m, "KILLED" if k else "SURVIVED", buf.getvalue().strip().splitlines()[-1][:150] if buf.getvalue().strip() else rc))
    out("supergpqa_stage0 mutants: %d / %d killed" % (sum(killed), len(killed)))
    return 0 if all(killed) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for k in ("selftest", "mutants", "split", "dry-run", "run"):
        g.add_argument("--" + k, action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return mutants()
    if a.split:
        return mode_split()
    if a.dry_run:
        return mode_dry_run()
    return mode_run()


if __name__ == "__main__":
    sys.exit(main())
