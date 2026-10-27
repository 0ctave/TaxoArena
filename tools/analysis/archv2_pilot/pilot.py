"""ARCH-V2-PILOT-K46 (registered 3a12115, docs/judge_v2_program.md L15913-L15955; amended 2296877 L15975-L15983; open items
ruled L15957-L15962 (rubric) and L15985-L15994 (anchors, frozen pair)): the SCHEDULE, the judged path and the launch
guards. The analysis is archv2_pilot.analysis. Zero calls here: a launch posts through the call_full the CLI injects
(rejudge_reasoning.call_judge_full, CONTEXT rule 9), only with --go, only on a posting day >= 2026-09-25.

STREAMS (master "ARCHV2-PILOT-K46-1:5e406fce61daf51e0cf9b1963ab6e58606bda320"; seed = sha256(master | name)[:8]
big-endian, numpy PCG64; archv2_arena.streams.Streams, the log's sha printed):
  "anchors"    the 2 pilot anchors, drawn uniformly WITHOUT replacement from the REGISTERED 7 of ARCH-V2-STAGE1-ANCHOR-DRAW
               sorted by name (rng.choice(7, 2, replace=False)); the stage-1 file is verified by stage1.verify (7
               anchors, reproduces, same counts and eval_view) and the draw is re-derived in a fresh Streams (C0 (g))
  "questions"  ONE stream over both anchors in name order: for each anchor, exactly design.schedule_stratum's procedure
               (pairs i < j of the roster sorted by name, a random pair order, for each pair the N eligible questions
               with the fewest uses so far, ties by a random key, then a random orientation), with ONE addition: a
               question is eligible for a pair only when BOTH models answered it under ONE variant (the loader judges a
               variant, never an item); the selftest proves the scheduler equals design.schedule_stratum when every
               question is judgeable
  "trim"       the TRIM RULE (below)
  "boot", "rungs"  the analysis (archv2_pilot.analysis)
ROSTER: the ACTIVE models of mmlu-pro-v2 in eval_view.model_registry (the 47 minus the QUARANTINED
  Meta-Llama-3-70B-Instruct): exactly 46 required, Meta-Llama absent, rubric_p8.ARENA12 inside (C0 (b); amendment).
  [AMENDED 2026-09-25 BEFORE ANY CODE (0761cfa, docs/judge_v2_program.md L16787-L16992; the author's decision (2) "k = 37"),
  insertion only: the ROSTER is the 46 ACTIVE models MINUS the 9 EvalIngestValidator.BANNED_MODELS entries other than the
  quarantined Meta-Llama (DROPPED_BANNED, drop-list sha256-text 36e10ea2...29b4) = EXACTLY 37, roster sha256-text
  (sorted, LF-joined, no final LF) 3a3204cc...6f91 (ROSTER_SHA256). C0 (b) requires: registry 47 = 46 ACTIVE + Meta-Llama
  QUARANTINED; each of the 9 present AND ACTIVE; roster = ACTIVE - 9, |roster| 37, its sha = ROSTER_SHA256; ARENA12
  inside the roster and disjoint from the 9; no scheduled / cached / board row naming a model outside the 37; 0 EMPTY raw
  outputs (zlib-decompressed response.output_zlib, stripped, before robust_trace) on the scheduled cells. C0 (h): matches
  before the trim <= 2 x N x C(37,2) = 2,664 and trim t = 0 (the TRIM RULE below stays a fail-closed guard; any t > 0 is
  a scheduler defect and REFUSES). MASTER, the streams, RUN_ID, the "K46-" match_id prefix, the store path and the
  ledger key are UNCHANGED.]
QUESTIONS: the EVAL items of the pool (corpus_version mmlu-pro-v2 named) whose split stratum is the anchor. The answer
  compared by the filter (convention A: a question is kept unless both answers are non-blank and EQUAL) is the model's
  pred letter (strip, upper, first character; systematic_budget's normalisation) RESOLVED TO THE OPTION TEXT in the
  model's own ordered options (strip), so two models that saw different orderings are compared by content
  [DECLARED DEVIATION from design.py's letter comparison, forced by the MIXED orderings of the v2 data]; a letter out of
  range compares as "raw:<letter>"; no pred is blank.
TRIM RULE (registered, as amended): if the filtered schedule exceeds 4,000 matches, pairs are removed: per anchor, the
  candidate list is the pairs with at least one match there and NOT both members in ARENA12, sorted by (anchor, model_a,
  model_b) (names sorted within the pair); the stream "trim" permutes each anchor's list (anchors in name order); the
  first t pairs of every anchor's permutation are removed, t the smallest integer that brings the total to <= 4,000
  (equal numbers per anchor). If no t reaches the cap without an ARENA12 pair, REFUSED (C0 fails before any call). The
  cap is counted on SCHEDULED matches (per-match exclusions below only lower the judged count).
EXCLUSIONS: the MIXED rules of the loader (ruling 2e7e3c3 / 7bf7256; D5): a match whose variant carries ONE
  grok-reasoning-v0 reference is excluded when either contestant's ordering (loader.ordering_key) differs from the
  SOLVER's (the ingest's SOLVER_MODEL row of the reference's legacy qid on the variant): "excluded_MIXED_referenced" when
  the two contestants differ from each other, else "excluded_ordering_differs_from_solver". The scheduler PREDICTS them
  from free data and passes them as load_matches(expected_exclusions=...): the loader refuses the whole load when its
  realised exclusions differ. Excluded matches stay in the schedule (counted per model and per variant), are not
  judged and are not replaced.
PILOT 12: the first 12 LOADED matches of the post-trim schedule order (anchors by name, then generation order).
JUDGE: judge_v2 (merged f5bbbda; pins asserted equal): loader.load_matches over open_eval("judge"), then
  writer.JudgeWriter (create / open, prescan on 100% of pending payloads, run); recipe STACK-v2, persona GENERIC_SYSTEM
  (payload.FIXED_SYSTEM_PERSONA), the rubric slot = the INDUCE-RUBRIC-1 artefact named by its artefact_sha256 AND
  rubric_sha256 (REQUIRED arguments), board vintage grok-reasoning-v0 only, corpus type mcq.
  [RE-PINNED 2026-09-25 per the author's PRE-DECIDED FALLBACK (docs/judge_v2_program.md L16994-L17006, the -3
  registration's FALLBACK L17072; the registrar's record of the INDUCE-RUBRIC-3 outcome is PENDING), insertion only:
  ARCH-V2-INDUCE-RUBRIC-3 (b653b0a) was read UNFIT by checklist reader B on K8 and K3b -> NOT ADOPTED, so the rubric slot
  holds GENERIC_RUBRIC (rubric_value_contrast.GENERIC_RUBRIC, IMPORTED, sha256-text 67f843eb...1dc, 81 characters;
  rubric_value_contrast.py blob:9e1541a7...), named by sha: load_generic_rubric() refuses any other text in record mode
  and asserts that payload.build_system gives EXACTLY STACK-NORUBRIC's measured system turn (v2 template, $systemPrompt =
  GENERIC_SYSTEM, $rubric = GENERIC_RUBRIC, + "\n\n" + SCHEMA_INSTRUCTION; stack_norubric.py L166-L169). The persona is
  GENERIC_SYSTEM (payload.FIXED_SYSTEM_PERSONA = rvc.GENERIC_SYSTEM, sha256-text 3a5e223c...). The INDUCE-RUBRIC-1
  path (load_rubric, the --rubric-artefact arguments) is kept for DISCLOSURE ONLY: a record run refuses it. The judge
  pins are MAIN b653b0a's judge_v2 (induction.py blob:147e6874..., the other six unchanged since 06a17be).]
ACCOUNTING: archv2_pilot.accounting.guard_day on accepted_tests_ledger's files (test ARCH-V2-PILOT-K46, ceiling 8,000 calls, the 4,000-match rule, the
  posting-date day cap 14,000) before every launch; the calls posted (the store's attempt rows added) appended to the
  posting-date ledger after every launch (finally).
[ADDED 2026-09-25 by JV2-PARALLEL-POSTING (registered bf9d80b, docs/judge_v2_program.md L19096-L19239; E-1 / E-2 / E-7),
  insertion only: launch(..., workers=1). At workers 1 the launch is TODAY'S (wrap_call; a new journal is created with
  today's DDL; the label, the journal, the store and the ledger are unchanged; judge_v2.writer prints its one [POOL] line).
  At 2 <= workers <= judge_v2.pool.MAX_INFLIGHT: the transport preflight still runs FIRST, before the journal, the store,
  the ledger and the pool (E-7); a NEW journal is created as JOURNAL v2 (max_inflight = MAX_INFLIGHT); the journal's
  begin_launch REFUSES workers above its max_inflight (a journal created at workers 1: 1) before any post; the label
  carries " w=N"; the posts go through accounting.TwoPhaseCall and writer.run(..., workers=N). The no-go path prints the
  [POOL] line with the journal's max_inflight. MUTANT_POOL (SELFTEST-ONLY): "preflight_after_pool",
  "preflight_skipped_pooled".
  [ADDED 2026-09-25, the coordinator's rate-control requirements relayed during the build] launch(..., rate=RateConfig):
  a rate configuration makes the launch POOLED at any workers (workers 1 included: the rate control then protects a
  single poster, at bound 1, on a journal v2); POOLED = workers > 1 or rate given; a pooled launch without rate uses
  judge_v2.pool.RateConfig()'s defaults (max_rpm 20, request timeout 120 s, breaker K 8). Without both (workers 1, rate
  None) the launch is today's, byte for byte.]
"""
import hashlib
import json
import math
import os
import time
import zlib
from dataclasses import asdict, dataclass, field, fields

import numpy as np

from . import common as C
from . import stage1
from archv2_arena import report
from archv2_arena.streams import Streams
from judge_v2 import induction as JI
from judge_v2 import leakage as L
from judge_v2 import loader as LD
from judge_v2 import payload as P
from judge_v2 import pool as POOL
from judge_v2 import writer as W
from judge_v2._base import dv2ingest, dv2verdicts, pin_table, rr
from archv2_arena import ro as aro
from . import accounting as ACC
import rubric_p8
import rubric_value_contrast as rvc

REGISTRATION = "ARCH-V2-PILOT-K46"
MASTER = "ARCHV2-PILOT-K46-1:5e406fce61daf51e0cf9b1963ab6e58606bda320"
RUN_ID = "ARCH-V2-PILOT-K46-run1"
BOARD_VINTAGE = "grok-reasoning-v0"
ARENA12 = tuple(sorted(rubric_p8.ARENA12))
QUARANTINED = "Meta-Llama-3-70B-Instruct"
# [AMENDMENT 0761cfa, k = 37] the 9 EvalIngestValidator.BANNED_MODELS entries (src/main/kotlin/taxonomy/dataset/
# EvalIngestValidator.kt blob:0e6d1bec0ca0f6ad1cc7fc009e64f3c82eb5b8a4, L315-L332) other than the quarantined Meta-Llama,
# sorted; dropped at the pilot's roster (they stay ACTIVE in the registry: the view is not rebound). Hash kind of both
# shas: sha256-text = sha256 of the UTF-8 names sorted, joined by LF, NO final newline.
DROPPED_BANNED = ("deepseek", "flash_0shots_00_35_03", "gemini-1.5-flash-002", "gemini-1.5-pro-002", "gpt4o(2024-05-13)",
                  "jamba-1.5-large", "opus_2shots_00_37_14", "sonnet-3.5_0shots_09_34_29", "sonnet_0shots_12_01_18")
DROPPED_SHA256 = "36e10ea298adf62d78bd88f0ba5caaa5146507644d4cd55238c11040c9ce29b4"
ROSTER_SHA256 = "3a3204cc35cf600495506e6e1f545ab379707b26c16371df78ce654837846f91"
C.need(tuple(sorted(DROPPED_BANNED)) == DROPPED_BANNED and C.sha256_text("\n".join(DROPPED_BANNED)) == DROPPED_SHA256,
       "DROPPED_BANNED is not the registered drop-list (sorted, sha256-text %s)" % DROPPED_SHA256)
AMENDMENT_K37 = "0761cfa"
SHORT_CHARS = 40            # C2: a SHORT raw output has < 40 code points after strip (empty included)
EARLIEST_POSTING_DAY = "2026-09-25"
# judge_v2 as merged at f5bbbda (git rev-parse f5bbbda:tools/analysis/judge_v2/<f>; hash kind blob, LF)
JUDGE_V2_F5BBBDA = {
    "judge_v2/_base.py": "blob:f88fefa7cdbfea9505a79f4b9e4c0eb12127af54",
    "judge_v2/payload.py": "blob:4b0af34decc3a34fb6ec42f1477a09fcee6593db",
    "judge_v2/leakage.py": "blob:d4c4d6b3b83576ca3ded5e6eca44a48a74755bf3",
    "judge_v2/combiner.py": "blob:19c7c5667f697ff370c7a9e8b34dc86406669303",
    "judge_v2/writer.py": "blob:6db4ab3207a24aa61a1d4ea43ca6f2da2c68e547",
    "judge_v2/induction.py": "blob:ae17ba25567fd07a2ba4cb5b6d8a558610dd0435",
    "judge_v2/loader.py": "blob:da4fcbbf3f04cd1d49bf1a3229f14f5340a70b33",
}
# [READY 65a9173 K2] INDUCE-RUBRIC-1 replaces judge_v2/induction.py (branch archv2-induce-rubric-1 at 23e56e7; hash kind
# blob of the LF text; sha256-lf16 d49af83f2d3ff633). C0 (c) of record (to be bracketed by the registrar): the pins equal
# f5bbbda's with induction.py replaced by this blob, AND the blob must be MAIN's actual induction.py (main_blob()).
INDUCE_INDUCTION_BLOB_23E56E7 = "blob:0de6153f61c5c4c2dc0c84b81fc097e282487862"    # superseded (disclosure only)
# [RE-PINNED 2026-09-24 to MAIN after the judge_v2 merge by path at 06a17be (C0 (c) bracketed forward by the registrar,
# 86f26e2; programme L15932 and the R2 record L16216), insertion only: induction.py merged as the D1 amendment
# blob:f4d65f59156f8f3f28d3257989d8baab1953d83e / sha256-lf16:ab0db179a8380a5d (NOT 0de6153f), and the merge also moved
# _base.py (ED_PINS: data_v2 views 7a0f0ab3, common 462ffef3) to blob:6f25e4ceac4ee5515930a751ce19864a2c9897cc /
# sha256-lf16:36f386ccc8c45782. The other five pinned files are f5bbbda's, unchanged on main (git rev-parse main:<path>).
# The table below is the record's; JUDGE_V2_F5BBBDA and the 23e56e7 blob stay for disclosure and are never accepted.]
INDUCE_INDUCTION_BLOB = "blob:f4d65f59156f8f3f28d3257989d8baab1953d83e"
JUDGE_V2_MAIN_06A17BE = dict(JUDGE_V2_F5BBBDA, **{
    "judge_v2/_base.py": "blob:6f25e4ceac4ee5515930a751ce19864a2c9897cc",
    "judge_v2/induction.py": INDUCE_INDUCTION_BLOB,
})
JUDGE_V2_PINS_LABEL = "main 06a17be's (= f5bbbda's with _base.py 6f25e4ce and induction.py f4d65f59)"
# The DEV fixture's former "f5bbbda" mode is RETIRED (the checkout no longer carries f5bbbda's _base.py / induction.py):
# the fixture runs under the record pin mode, which it can only pass on a checkout equal to main's judge_v2.
JUDGE_PIN_MODES = ("INDUCE-RUBRIC-1",)
# [RE-PINNED 2026-09-25 to MAIN b653b0a (after the ARCH-V2-INDUCE-RUBRIC-3 build merged by path at 0b512e3), insertion
# only: `git rev-parse main:tools/analysis/judge_v2/<f>` at b653b0a moves ONE of the seven files, induction.py, to
# blob:147e6874926b65393037cdcacd0e29aa308651ef / sha256-lf16:1117d74f06438d98 (jv2-induce-5); _base.py, payload.py,
# leakage.py, combiner.py, writer.py and loader.py are 06a17be's (= the table above), unchanged. The rubric slot is
# GENERIC_RUBRIC (below), so the pilot does NOT use induction.py to fill the slot; its pin STAYS as a LAYER-IDENTITY pin
# (the builder's recommendation, for the READY to confirm): (i) judge_v2.writer records pin_table() -- induction.py
# included -- in the store's pins_json and the pilot writes it into <store>.launch.json, so the store names this blob
# whatever the pilot checks; (ii) this module imports judge_v2.induction (the disclosure path load_rubric), so its
# module-level code runs in the pilot's process; an unpinned executed file is what K2 exists to refuse. Every one of the
# seven pins must ALSO be MAIN's actual blob (K2 generalised from induction.py alone to the seven). The mode
# "INDUCE-RUBRIC-1" (06a17be's table) is RETIRED: kept above for disclosure, never admitted.]
INDUCE_INDUCTION_BLOB_06A17BE = INDUCE_INDUCTION_BLOB                                   # superseded (disclosure only)
INDUCTION_BLOB_B653B0A = "blob:147e6874926b65393037cdcacd0e29aa308651ef"
JUDGE_V2_MAIN_B653B0A = dict(JUDGE_V2_MAIN_06A17BE, **{"judge_v2/induction.py": INDUCTION_BLOB_B653B0A})
JUDGE_V2_PINS_LABEL = ("main b653b0a's (= 06a17be's with induction.py 147e6874, a layer-identity pin: the GENERIC_RUBRIC"
                       " slot does not use it; = f5bbbda's with _base.py 6f25e4ce and induction.py 147e6874)")
JUDGE_PIN_MODES = ("MAIN-B653B0A",)
RETIRED_PIN_MODES = ("INDUCE-RUBRIC-1", "f5bbbda")
# [RE-PINNED 2026-09-25 by JV2-PARALLEL-POSTING (registered bf9d80b, docs/judge_v2_program.md L19096-L19239), insertion
# only; the build branch, NOT MERGED (the merge waits for the K46 OUTCOME, F5; the K46 run itself finishes on its build of
# record 5e9de0f / 788ea85 under MAIN-B653B0A, which this branch retires): judge_v2/writer.py moves from 6db4ab32 to
# WRITER_BLOB_JV2PP and judge_v2/pool.py (NEW; imported by writer.py, so an executed file K2 pins) is pinned at
# POOL_BLOB_JV2PP; _base.py, payload.py, leakage.py, combiner.py, induction.py and loader.py are b653b0a's, unchanged.
# The live table is judge_v2.writer._pins() (= _base.pin_table() + pool.py; _base.py is not edited). Every one of the
# EIGHT pins must ALSO be MAIN's actual blob (K2): on the unmerged branch K2 REFUSES writer.py and pool.py by design; the
# selftest's --main-ref flag is the pre-merge simulation (printed), never a launch of record.]
WRITER_BLOB_JV2PP = "blob:0c9c57c335151ff198ea45c8bc98ffbd9c23adf2"      # sha256-lf16:f3e2d1cf7447d8ca
POOL_BLOB_JV2PP = "blob:a7fdd8a28707b52b7abfe347c13bf938facd28db"        # sha256-lf16:588360a0eae82b3d
# [RE-PINNED 2026-09-25 on the READY review d32fa75 (NOT READY; F1 serialised token taker, F3 abort flag, F4 live guard),
# insertion only; the line above is SUPERSEDED (the build's pool.py a7fdd8a2) and kept as the record of the build:]
POOL_BLOB_JV2PP = "blob:e9bc770fb16aafa0256e10adbd18c91da237e61e"        # sha256-lf16:978ad89c8632a1b2
JUDGE_V2_JV2PP = dict(JUDGE_V2_MAIN_B653B0A, **{"judge_v2/writer.py": WRITER_BLOB_JV2PP,
                                                "judge_v2/pool.py": POOL_BLOB_JV2PP})
JUDGE_V2_PINS_LABEL = ("main b653b0a's with judge_v2/writer.py %s and judge_v2/pool.py %s (JV2-PARALLEL-POSTING; = main's"
                       " at its merge; the other six b653b0a's: induction.py 147e6874 a layer-identity pin, _base.py"
                       " 6f25e4ce)" % (WRITER_BLOB_JV2PP[5:13], POOL_BLOB_JV2PP[5:13]))
JUDGE_PIN_MODES = ("JV2-PARALLEL-POSTING",)
RETIRED_PIN_MODES = ("INDUCE-RUBRIC-1", "f5bbbda", "MAIN-B653B0A")
# The FIRST stage-1 draw (53eccb6 + 1463759) read the superseded split 1; kept for disclosure, never read by the pilot.
STAGE1_1_RECORD_REL = os.path.join("experiment_results", "archv2", "stage1_anchor_draw", "archv2_stage1_anchors.json")
STAGE1_1_RECORD_SHA256 = "08cdff0e314dce5520bca8316e3a74a94845c64850fe8956c99b6d875ffb6140"
STAGE1_1_ANCHORS = ("business", "history", "math", "other", "philosophy", "physics", "psychology")
# THE RE-DRAW (ARCH-V2-STAGE1-ANCHOR-DRAW-2, registered 5b89159) on the split of record 5a3e756: its output path under the
# main checkout; its sha256-bytes and its 7 anchors are PINNED AFTER THE DRAW (None until then: a record run REFUSES)
STAGE1_RECORD_REL = os.path.join("experiment_results", "archv2", "stage1_anchor_draw_2", "archv2_stage1_anchors_2.json")
STAGE1_RECORD_SHA256 = None
STAGE1_ANCHORS_OF_RECORD = None
# [PINNED 2026-09-24 after the draw, insertion only: ARCH-V2-STAGE1-ANCHOR-DRAW-2 RAN ONCE (e4f0658), anchors chemistry,
# computer science, economics, health, math, other, philosophy, counts_digest 08bc48d1..., seed 4030866750177695589, equal
# to the READY reviewer's independent prediction (a254a1d). HASH KIND: sha256-lf = sha256 of the LF rendering (CRLF -> LF),
# NOT of the working-tree bytes (READY a254a1d MEDIUM-1: core.autocrlf=true renders the committed LF file as CRLF on
# checkout; this worktree's copy is sha256-crlf 3a0764c6...). The git blob is checked beside it.]
STAGE1_RECORD_SHA256 = "777e2f6a4cd8ee0d1ce92659f8c3ad4f72a45319d166135dd918575d0ace5e43"     # sha256-lf (full)
STAGE1_RECORD_BLOB = "blob:7b7a41d8d7b285b663eba3fbf4ba2d8bb38c883c"
STAGE1_ANCHORS_OF_RECORD = ("chemistry", "computer science", "economics", "health", "math", "other", "philosophy")
# [READY 65a9173 K8, ruled: accepted as a forced deviation] a question is eligible for a pair only when both answered it
# under ONE variant (the loader judges a variant). The only admitted value; the lost cells are printed.
VARIANT_MASK = "ONE_VARIANT"
MASK_THIN_SHARE = 0.02      # the ruling: > 2% of an anchor's pairs exhausted -> "the mask thins the target design"
# [READY 65a9173 K3] the pilot guard: PASS iff every pilot slot carries a usable verdict, unusable 0, foreign 0; ERRORED
# attempts are counted and printed; no bound is registered (None = none applied; a registered bound refuses above it)
PILOT_ERRORED_BOUND = None
MUTANT = None       # SELFTEST-ONLY: "trim_arena12", "cap_off", "anchors_from_14", "guard_errored_fails", "mask_off_count",
                    # "ledger_guard_off"
MUTANT_POOL = None  # SELFTEST-ONLY [JV2-PARALLEL-POSTING I5]: "preflight_after_pool", "preflight_skipped_pooled"


@dataclass
class Config:
    """The registered values; a fixture passes others and is then DEV (deviations() lists them)."""
    master: str = MASTER
    n_pilot_anchors: int = 2
    N: int = 2
    cap_matches: int = 4000
    ceiling_calls: int = 8000
    day_cap: int = 14000
    roster_n: int = 37              # [0761cfa] 46 ACTIVE - the 9 dropped
    active_n: int = 46              # [0761cfa] the ACTIVE models of the registry (C0 (b))
    dropped: tuple = DROPPED_BANNED
    roster_sha256: str = ROSTER_SHA256
    k_lo: int = 12
    arena12: tuple = ARENA12
    quarantined: str = QUARANTINED
    pilot_n: int = 12
    earliest_day: str = EARLIEST_POSTING_DAY
    cv: str = C.CV_MMLU
    pool_id: str = C.POOL_MMLU
    view_sha: str = C.EVAL_VIEW_SHA256
    stage1_master: str = stage1.MASTER
    rungs: tuple = (12, 20, 28, 37)     # [0761cfa] rung 36 dropped; 37 = the roster
    B_outer: int = 2000
    B_inner: int = 300
    B_rungs: int = 200
    n_integrated: int = 21
    between_sd: float = 0.20
    frozen_pair: tuple = (-3.3172, 3.3001)
    L12: float = 0.1078
    bar_P: float = 1.06
    bar_M: float = 2.0529           # [0761cfa] = round(exact_M(37, 12), 4) (checked by exact_bar_M); every comparison
                                    # is made against the EXACT value exact_M(k_hi, k_lo), never this rounded print
    registry_total: int = 47
    judge_pins: str = "JV2-PARALLEL-POSTING"   # [JV2-PARALLEL-POSTING] was "MAIN-B653B0A"; before it "INDUCE-RUBRIC-1"
    level_cv: float = 0.133         # K6 ruling: the DEV-transported between-anchor CV of a level

    def deviations(self):
        ref = Config()
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) != getattr(ref, f.name)}

    def record(self):
        return not self.deviations() and MUTANT is None and C.MUTANT is None


def exact_M(k_hi, k_lo):
    """The M bar of C1 at (k_hi, k_lo): ln(C(k_hi,2) / C(k_lo,2)) / ln(k_hi / k_lo) (2.052941 at 37 / 12)."""
    return math.log((k_hi * (k_hi - 1) / 2.0) / (k_lo * (k_lo - 1) / 2.0)) / math.log(k_hi / float(k_lo))


def exact_bar_M(cfg, k_hi):
    """[0761cfa] THE M BAR IS REGISTERED AT ITS EXACT VALUE: returns exact_M(k_hi, cfg.k_lo), the value every comparison
    uses; REFUSES unless the printed bar cfg.bar_M equals it rounded to 4 decimals (2.0529 at k 37)."""
    m = exact_M(k_hi, cfg.k_lo)
    C.need(round(m, 4) == cfg.bar_M, "the M bar %r is not round(exact_M(%d, %d), 4) = %.4f (the exact bar, amendment %s)"
           % (cfg.bar_M, k_hi, cfg.k_lo, m, AMENDMENT_K37))
    return m


# the registered Config's printed bar is the exact bar at k 37 (checked at import; python -O safe)
exact_bar_M(Config(), Config().roster_n)


def word(cfg):
    dev = cfg.deviations()
    if dev or MUTANT is not None or C.MUTANT is not None:
        return "DEV, NOT OF RECORD (deviations from the registered values: %s; mutants %r / %r)" % (
            json.dumps(dev, sort_keys=True, default=str), MUTANT, C.MUTANT)
    return ("UNDER THE REGISTRATION %s (3a12115, amended 2296877, open items ruled b44227f / 53eccb6; amended %s (k 37))"
            % (REGISTRATION, AMENDMENT_K37))


# ── the judge layer's pins (C0 (c)) ─────────────────────────────────────────────────────────

def expected_pins(cfg):
    if cfg.judge_pins not in JUDGE_PIN_MODES:
        C.refuse("judge pin mode %r (admitted: %s; retired: %s)" % (cfg.judge_pins, JUDGE_PIN_MODES, RETIRED_PIN_MODES))
    return dict(JUDGE_V2_JV2PP)         # [JV2-PARALLEL-POSTING] was dict(JUDGE_V2_MAIN_B653B0A) (mode MAIN-B653B0A)


def main_blob(rel):
    """MAIN's actual blob of tools/analysis/<rel> (`git rev-parse main:<path>`, run in this checkout); None if unreadable."""
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "main:tools/analysis/" + rel], capture_output=True, text=True, cwd=C.ROOT,
                           timeout=60)
    except Exception:  # noqa: BLE001
        return None
    return ("blob:" + r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def judge_pins_ok(cfg, main_blob_fn=main_blob, table_fn=None):
    """C0 (c): the live judge_v2 blobs equal the expected pins, AND [re-pin 2026-09-25] each of the seven pinned files is
    ALSO main's actual blob (K2 guard, generalised from induction.py alone: a branch-local judge_v2 file is refused).
    table_fn: SELFTEST-ONLY substitute for judge_v2._base.pin_table (a mutant live table).
    [JV2-PARALLEL-POSTING] the live table is judge_v2.writer._pins() (pin_table() + judge_v2/pool.py)."""
    t = (table_fn or W._pins)()
    exp = expected_pins(cfg)
    bad = {k: (t.get(k), v) for k, v in exp.items() if t.get(k) != v}
    for k in sorted(exp):
        mb = main_blob_fn(k)
        if mb != exp[k]:
            bad["main:" + k] = (mb, exp[k])
    return (not bad), bad


def persona_sha():
    """K10 (b): the persona text's sha256 (payload's fixed GENERIC_SYSTEM; the registration's "its text sha printed")."""
    from judge_v2._base import FIXED_SYSTEM_PERSONA
    return C.sha256_text(FIXED_SYSTEM_PERSONA)


def main_checkout():
    """The MAIN checkout (the parent of git's common dir), or None."""
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True,
                           text=True, cwd=C.ROOT, timeout=60)
    except Exception:  # noqa: BLE001
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return os.path.dirname(os.path.normpath(r.stdout.strip()))


def main_ledger_dir():
    m = main_checkout()
    return os.path.join(m, "experiment_results") if m else None


def check_ledger_dir(ledger_dir, cfg, out=print):
    """K9: the ledger directory's FULL path is printed; a record launch refuses unless it is the MAIN checkout's
    experiment_results/ (where the day ledgers of record live)."""
    full = os.path.realpath(os.path.abspath(ledger_dir))
    want = main_ledger_dir()
    out("  ledger directory: %s (the main checkout's: %s)" % (full, want))
    if cfg.record() and MUTANT != "ledger_guard_off":
        C.need(want is not None and full == os.path.realpath(want), "the ledger directory %s is not the MAIN checkout's"
               " experiment_results (%s): refused (K9)" % (full, want))
    return full


def default_stage1_record():
    m = main_checkout() or C.ROOT
    return os.path.join(m, STAGE1_RECORD_REL)


def file_sha256_lf(path):
    """sha256 (full hex) of the file's LF rendering (CRLF -> LF), the rendering of record (CONTEXT rule 8); the same
    normalisation as data_v2.ro.git_blob_lf / sha256_lf16, so a CRLF checkout (core.autocrlf=true) hashes as committed."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def check_stage1_file(path, cfg):
    """Record mode: the stage-1 file is the committed record (sha256-lf AND git blob pinned; READY a254a1d MEDIUM-1: the
    working-tree bytes are NOT hashed raw) carrying the 7 anchors of record. Returns the sha256-lf."""
    sha = file_sha256_lf(path)
    if cfg.record():
        C.need(STAGE1_RECORD_SHA256 is not None and STAGE1_ANCHORS_OF_RECORD is not None,
               "the re-drawn stage-1 record's sha256 and anchors are not pinned yet (they are pinned after the draw, "
               "ARCH-V2-STAGE1-ANCHOR-DRAW-2): a record run is refused")
        C.need(sha == STAGE1_RECORD_SHA256, "the stage-1 file %s is sha256-lf %s, not the record's %s" % (
            path, sha, STAGE1_RECORD_SHA256))
        blob = "blob:" + C.dv2ro.git_blob_lf(path)
        C.need(blob == STAGE1_RECORD_BLOB, "the stage-1 file %s is %s, not the record's %s" % (path, blob,
                                                                                              STAGE1_RECORD_BLOB))
    return sha


# ── the rubric slot of record: GENERIC_RUBRIC (the author's pre-decided fallback 2026-09-25), named by sha ──────────
# [2026-09-25, insertion] ARCH-V2-INDUCE-RUBRIC-1, -2 and -3 are NOT ADOPTED (-3: read UNFIT by checklist reader B on K8
# and K3b; one UNFIT reading = NOT ADOPTED under the registered verdict rule; the registrar's record is PENDING). The
# author's pre-decided fallback (programme L16994-L17006; -3 FALLBACK L17072) fills the slot with GENERIC_RUBRIC.
RUBRIC_SLOT = "GENERIC_RUBRIC"
GENERIC_RUBRIC_SHA256 = "67f843eb7a632ae5bd411a9debcbaf9dedccd362e0c8355c366c6d85cb89b1dc"   # sha256-text (UTF-8)
GENERIC_RUBRIC_CHARS = 81
RVC_BLOB = "blob:9e1541a7bdf1260268c850ccac81db4570c064e4"     # rubric_value_contrast.py (L69), printed as provenance
RUBRIC_SLOT_LINE = ("rubric slot: GENERIC_RUBRIC (author's pre-decided fallback 2026-09-25; INDUCE-RUBRIC-1/-2/-3 NOT"
                    " ADOPTED)")
RUBRIC_SLOT_OF_RECORD = "GENERIC_RUBRIC per the author's pre-decided fallback 2026-09-25 (programme L16994-L17006)"
MUTANT_RUBRIC = None    # SELFTEST-ONLY: "norubric_off" (the STACK-NORUBRIC system-turn identity check skipped)


def stack_norubric_system():
    """The system turn STACK-NORUBRIC measured (tools/analysis/stack_norubric.py L166-L169, the norubric arm, --sp
    generic): prompt_v2.v2_system_template().replace("$systemPrompt", GENERIC_SYSTEM).replace("$rubric", GENERIC_RUBRIC)
    + "\n\n" + rejudge_grok.SCHEMA_INSTRUCTION, both slot texts IMPORTED from rubric_value_contrast (never retyped)."""
    from judge_v2._base import prompt_v2, rj
    return (prompt_v2.v2_system_template().replace("$systemPrompt", rvc.GENERIC_SYSTEM)
            .replace("$rubric", rvc.GENERIC_RUBRIC) + "\n\n" + rj.SCHEMA_INSTRUCTION)


def rvc_blob():
    """rubric_value_contrast.py's git blob of its LF rendering (provenance, printed; the text sha is what binds)."""
    return "blob:" + C.dv2ro.git_blob_lf(os.path.abspath(rvc.__file__))


def load_generic_rubric(record=True, rubric_sha256=None, text=None):
    """The rubric slot of record: rubric_value_contrast.GENERIC_RUBRIC (imported), corpus type mcq, as a
    payload.RubricArtifact (payload.load_rubric: placeholders refused, the sha RE-COMPUTED; artefact_id "" -- there is
    no induced artefact). Record mode REFUSES unless the text's sha256-text is GENERIC_RUBRIC_SHA256 (any other text is
    refused) AND payload.build_system(slot) equals STACK-NORUBRIC's measured system turn byte for byte. rubric_sha256: an
    optional operator witness (--rubric-sha256), refused when it differs. text: SELFTEST-ONLY substitute text.
    Returns (RubricArtifact, of_record label)."""
    t = rvc.GENERIC_RUBRIC if text is None else text
    sha = C.sha256_text(t)
    if record:
        C.need(sha == GENERIC_RUBRIC_SHA256, "the rubric slot text is sha256-text %s, not GENERIC_RUBRIC's %s: the slot of"
               " record holds GENERIC_RUBRIC only (the author's pre-decided fallback 2026-09-25); refused" % (
                   sha, GENERIC_RUBRIC_SHA256))
        C.need(len(t) == GENERIC_RUBRIC_CHARS, "GENERIC_RUBRIC is %d characters, not %d" % (len(t), GENERIC_RUBRIC_CHARS))
    if rubric_sha256 is not None:
        C.need(rubric_sha256 == sha, "--rubric-sha256 %s is not the slot's sha256-text %s; refused" % (rubric_sha256, sha))
    rub = P.load_rubric({"corpus_type": "mcq", "rubric": t, "rubric_sha256": sha})
    if record and MUTANT_RUBRIC != "norubric_off":
        C.need(P.build_system(rub) == stack_norubric_system(), "payload.build_system(GENERIC_RUBRIC) is not STACK-NORUBRIC's"
               " measured system turn (v2 template + GENERIC_SYSTEM + GENERIC_RUBRIC + SCHEMA_INSTRUCTION); refused")
    return rub, (RUBRIC_SLOT_OF_RECORD if sha == GENERIC_RUBRIC_SHA256 else "DEV rubric text, NOT OF RECORD")


def rubric_slot_lines(rubric):
    """The slot's printed identity (the C0 header of every mode and the outcome)."""
    system = P.build_system(rubric)
    return ["  %s" % RUBRIC_SLOT_LINE,
            "    GENERIC_RUBRIC sha256-text %s (%d characters; required %s; rubric_value_contrast.py %s) | persona"
            " GENERIC_SYSTEM sha256-text %s | system turn sha256-text %s (= STACK-NORUBRIC's measured combination: %s)"
            % (rubric.rubric_sha256, len(rubric.rubric), GENERIC_RUBRIC_SHA256, rvc_blob(), persona_sha(),
               C.sha256_text(system), system == stack_norubric_system())]


def check_rubric_args(cfg, artefact, artefact_sha256):
    """[2026-09-25] a record run REFUSES the INDUCE-RUBRIC-1 artefact arguments (the slot holds GENERIC_RUBRIC by sha)."""
    if cfg.record():
        C.need(not artefact and not artefact_sha256, "--rubric-artefact / --rubric-artefact-sha256 given: the rubric slot"
               " of record holds GENERIC_RUBRIC (the author's pre-decided fallback 2026-09-25); an induced artefact is"
               " refused (INDUCE-RUBRIC-1/-2/-3 NOT ADOPTED)")


# ── the rubric slot (INDUCE-RUBRIC-1), named by sha ─────────────────────────────────────────
# [SUPERSEDED 2026-09-25, insertion only: DISCLOSURE ONLY. The INDUCE-RUBRIC-1 path below is kept as built and reviewed;
# the CLI never calls it, and a record call (record=True) REFUSES before reading the artefact. The slot of record is
# load_generic_rubric above.]

def load_rubric(path, artefact_sha256, rubric_sha256, record=True):
    """The rubric slot's artefact: path, artefact_sha256 and rubric_sha256 are ALL REQUIRED (the registration names both
    shas before the READY). REFUSED when any is missing, either sha differs, the corpus type is not mcq, or (record) the
    artefact is DEV / STUB / not of record. [2026-09-25: DISCLOSURE ONLY; record=True REFUSES first.]"""
    if record:
        C.refuse("the INDUCE-RUBRIC-1 artefact path is DISCLOSURE ONLY (2026-09-25): the rubric slot of record holds"
                 " GENERIC_RUBRIC (load_generic_rubric); refused")
    for name, v in (("--rubric-artefact", path), ("--rubric-artefact-sha256", artefact_sha256),
                    ("--rubric-sha256", rubric_sha256)):
        if not v:
            C.refuse("%s is required: the rubric slot holds the INDUCE-RUBRIC-1 artefact NAMED BY SHA (ruling on open"
                     " item 1); refused" % name)
    rub = JI.load_artefact(path, expect_artefact_sha256=artefact_sha256)
    C.need(rub.rubric_sha256 == rubric_sha256, "the artefact's rubric_sha256 %s is not the named %s" % (rub.rubric_sha256,
                                                                                                        rubric_sha256))
    C.need(rub.corpus_type == "mcq", "the rubric artefact is corpus type %r, not mcq" % rub.corpus_type)
    with open(path, encoding="utf-8") as f:
        art = json.load(f)
    of_record = str(art.get("of_record", ""))
    if record:
        low = of_record.upper()
        C.need(not ("DEV" in low or "STUB" in low or "NOT OF RECORD" in low),
               "the rubric artefact is not of record (%r): the pilot of record fills the slot with INDUCE-RUBRIC-1's"
               " artefact" % of_record)
        # K10 (c): the positive label and the population (C4 ruling (6))
        C.need(of_record.startswith("REGISTERED ARCH-V2-INDUCE-RUBRIC-1"), "the rubric artefact's of_record %r does not"
               " start with REGISTERED ARCH-V2-INDUCE-RUBRIC-1" % of_record)
        pop = (art.get("manifest") or {}).get("population") or {}
        C.need(pop.get("corpus_version") == C.CV_MMLU, "the rubric artefact's population %r is not %s" % (pop, C.CV_MMLU))
    return rub, of_record


# ── free data (the key stays sealed: is_correct / gt_raw / answer_text are never selected here) ─

def roster_of(conn, cfg):
    rows = conn.execute("SELECT model, status FROM model_registry WHERE corpus_version=?", (cfg.cv,)).fetchall()
    names = [m for m, _ in rows]
    C.need(len(names) == len(set(names)), "model_registry names repeat within %s" % cfg.cv)
    active = sorted(m for m, s in rows if s == "ACTIVE")
    quarantined = sorted(m for m, s in rows if s != "ACTIVE")
    # K10 (f): the registry total, and the quarantined model PRESENT as QUARANTINED
    C.need(len(rows) == cfg.registry_total, "C0 (b) FAILS: the %s registry carries %d models, not %d" % (
        cfg.cv, len(rows), cfg.registry_total))
    C.need(quarantined == [cfg.quarantined], "C0 (b) FAILS: the quarantined models are %s, not [%s]" % (
        quarantined, cfg.quarantined))
    C.need(cfg.quarantined not in active, "C0 (b) FAILS: %s is ACTIVE in the roster" % cfg.quarantined)
    # [0761cfa] 46 ACTIVE; each of the 9 dropped present AND ACTIVE; roster = ACTIVE - 9, exactly 37, its sha registered
    C.need(len(active) == cfg.active_n, "C0 (b) FAILS: the registry has %d ACTIVE models, not %d" % (len(active),
                                                                                                  cfg.active_n))
    dropped = sorted(cfg.dropped)
    status = dict(rows)
    absent = [m for m in dropped if m not in status]
    C.need(not absent, "C0 (b) FAILS (amendment %s): the dropped models %s are not in the %s registry (the registry has"
           " changed)" % (AMENDMENT_K37, absent, cfg.cv))
    inactive = [m for m in dropped if status[m] != "ACTIVE"]
    C.need(not inactive, "C0 (b) FAILS (amendment %s): the dropped models %s are not ACTIVE (the registry has changed)"
           % (AMENDMENT_K37, inactive))
    both = sorted(set(cfg.arena12) & set(dropped))
    C.need(not both, "C0 (b) FAILS (amendment %s): the ARENA12 models %s are among the dropped" % (AMENDMENT_K37, both))
    roster = sorted(m for m in active if m not in set(dropped))
    C.need(len(roster) == cfg.roster_n, "C0 (b) FAILS: the roster (ACTIVE minus the %d dropped) has %d models, not %d" % (
        len(dropped), len(roster), cfg.roster_n))
    sha = C.sha256_text("\n".join(roster))
    C.need(sha == cfg.roster_sha256, "C0 (b) FAILS (amendment %s): the roster sha256-text %s is not the registered %s" % (
        AMENDMENT_K37, sha, cfg.roster_sha256))
    miss = sorted(set(cfg.arena12) - set(roster))
    C.need(not miss, "C0 (b) FAILS (amendment 2296877): the ARENA12 models %s are not inside the %d-model roster" % (
        miss, len(roster)))
    C.need(len(set(cfg.arena12)) == cfg.k_lo, "ARENA12 carries %d distinct models, not %d" % (len(set(cfg.arena12)), cfg.k_lo))
    return roster, quarantined, dropped


def outside_roster(rows, roster):
    """[0761cfa] C0 (b): the number of rows (dicts with model_a / model_b, or (a, b) tuples) naming a model outside the
    roster (required 0)."""
    rs = set(roster)
    n = 0
    for r in rows:
        a, b = (r["model_a"], r["model_b"]) if isinstance(r, dict) else (r[0], r[1])
        n += int(a not in rs or b not in rs)
    return n


def require_inside(rows, roster, what):
    """[0761cfa] C0 (b), fail-closed: REFUSES when any row names a model outside the roster; returns 0."""
    n = outside_roster(rows, roster)
    C.need(n == 0, "C0 (b) FAILS: %d %s row(s) name a model outside the %d-model roster (amendment %s)" % (
        n, what, len(roster), AMENDMENT_K37))
    return n


def raw_output_len(blob):
    """[0761cfa] C2 / C0 (b): the RAW output's length = Unicode code points of the zlib-decompressed response.output_zlib
    (UTF-8), after str.strip(), BEFORE rejudge_grok.robust_trace (free data; the key is not read)."""
    return len(zlib.decompress(blob).decode("utf-8").strip())


def raw_output_counts(free, matches, roster):
    """[0761cfa] per model of the roster, over its SCHEDULED cells (the distinct (item, model) of the matches): cells,
    empty (length 0), short (< 40, empty included), short_nonempty. Returns {model: {...}}."""
    cells = {m: set() for m in roster}
    for x in matches:
        for mo in (x["model_a"], x["model_b"]):
            cells.setdefault(mo, set()).add(x["item_id"])
    out = {}
    for mo in sorted(cells):
        ls = [free["LEN"][(i, mo)] for i in sorted(cells[mo])]
        e = sum(1 for v in ls if v == 0)
        s = sum(1 for v in ls if v < SHORT_CHARS)
        out[mo] = {"cells": len(ls), "empty": e, "short": s, "short_nonempty": s - e}
    return out


def schedule_bound(cfg, n_models, n_anchors):
    """[0761cfa] C0 (h): the structural maximum N x C(k,2) per anchor (1,332 at k 37) and n_anchors x that in all (2,664)."""
    per = cfg.N * n_models * (n_models - 1) // 2
    return per, n_anchors * per


def check_c0h(cfg, stats, n_models, t, out=print):
    """[0761cfa] C0 (h), fail-closed: every anchor's matches before the trim <= N x C(k,2), the total <= n_anchors x that,
    and the trim NOT engaged (t = 0; any t > 0 is a scheduler defect). Prints the line; REFUSES on a failure."""
    per, tot = schedule_bound(cfg, n_models, len(stats))
    before = sum(s["matches_before_trim"] for s in stats.values())
    over = {a: s["matches_before_trim"] for a, s in sorted(stats.items()) if s["matches_before_trim"] > per}
    C.need(not over, "C0 (h) FAILS: matches before the trim %s exceed N x C(%d,2) = %d per anchor" % (over, n_models, per))
    C.need(before <= tot, "C0 (h) FAILS: %d matches before the trim > %d x N x C(%d,2) = %d" % (before, len(stats),
                                                                                                 n_models, tot))
    C.need(t == 0, "C0 (h) FAILS: the trim engaged (t = %d > 0): a scheduler defect at k %d (amendment %s)" % (
        t, n_models, AMENDMENT_K37))
    out("  C0 (h) SCHEDULE BOUND: matches before the trim %d <= %d x N %d x C(%d,2) = %d (%d per anchor); trim not engaged"
        " (t = 0)" % (before, len(stats), cfg.N, n_models, tot, per))
    return before, tot


def norm_answer(pred, options):
    p = (pred or "").strip().upper()[:1]
    if not p:
        return ""
    if p in C.LETTERS and C.LETTERS.index(p) < len(options):
        return "opt:" + str(options[C.LETTERS.index(p)]).strip()
    return "raw:" + p


def _options(conn, sha, cache):
    if sha not in cache:
        raw = C.dv2c.options_raw(conn, sha)
        v = json.loads(raw) if raw else []
        C.need(isinstance(v, list), "options_ordered %s is not a list" % sha)
        cache[sha] = v
    return cache[sha]


def load_free(conn, cfg, anchors, anchor_of, roster):
    """Per pilot anchor: its questions (items, sorted) and, per (item, model), the ONE response's variant, normalised
    answer and ordering key ("" / None when the model has no response or several: counted).
    [0761cfa] also LEN[(item, model)]: the raw output's length (raw_output_len of response.output_zlib, before
    robust_trace) of that ONE response, for C0 (b)'s empty count and C2's empty / short table. FREE DATA ONLY: is_correct,
    gt_raw and answer_text are never selected here (K4 intact)."""
    items = {i for i, a in anchor_of.items() if a in anchors}
    rset = set(roster)
    rs = {}
    for m, iid, vid, pred, osha, src, oz in conn.execute(
            "SELECT model, item_id, seen_ck, pred, options_ordered_sha, source, output_zlib FROM response WHERE"
            " corpus_version=?", (cfg.cv,)):
        if iid in items and m in rset:
            rs.setdefault((iid, m), []).append((vid, pred, osha, src, oz))
    cache = {}
    V, A, OK, LEN = {}, {}, {}, {}
    multi = 0
    for (iid, m), lst in rs.items():
        if len(lst) != 1:
            multi += 1
            continue
        vid, pred, osha, src, oz = lst[0]
        C.need(not LD.refused_source(src), "a %s response in the pilot pool (source %r)" % (cfg.cv, src))
        opts = _options(conn, osha, cache)
        V.setdefault(iid, {})[m] = vid
        A.setdefault(iid, {})[m] = norm_answer(pred, opts)
        OK.setdefault(iid, {})[m] = LD.ordering_key(opts)
        LEN[(iid, m)] = raw_output_len(oz)
    qs = {a: sorted(i for i in items if anchor_of[i] == a) for a in anchors}
    return {"qs": qs, "V": V, "A": A, "OK": OK, "LEN": LEN, "multi_response_cells": multi, "n_items": len(items)}


# ── the scheduler ───────────────────────────────────────────────────────────────────────────

def schedule_anchor(Parr, Varr, N, rng):
    """design.schedule_stratum's procedure, rng call for rng call, with the judgeability mask (both models answered the
    question under ONE variant). Returns ([(i, j, qrow)], exhausted)."""
    Q, M = Parr.shape
    use = np.zeros(Q, dtype=int)
    pairs = [(i, j) for i in range(M) for j in range(i + 1, M)]
    order = rng.permutation(len(pairs))
    out = []
    exhausted = 0
    for k in order:
        i, j = pairs[k]
        pa, pb = Parr[:, i], Parr[:, j]
        va, vb = Varr[:, i], Varr[:, j]
        judg = (va != "") & (va == vb)
        elig = np.flatnonzero(judg & ~((pa != "") & (pb != "") & (pa == pb)))
        if elig.size < N:
            exhausted += 1
        if elig.size == 0:
            continue
        key = rng.random(elig.size)
        pick = elig[np.lexsort((key, use[elig]))][:N]
        use[pick] += 1
        for q in pick:
            out.append((i, j, int(q)) if rng.random() < 0.5 else (j, i, int(q)))
    return out, exhausted


def match_id(anchor, item, a, b):
    return "K46-" + hashlib.sha256(("%s|%s|%s|%s" % (anchor, item, a, b)).encode("utf-8")).hexdigest()[:20]


def build_schedule(cfg, st, free, anchors, roster):
    rng = st.np("questions")
    models = sorted(roster)
    matches, stats = [], {}
    for anc in sorted(anchors):
        qs = free["qs"][anc]
        Parr = np.array([[free["A"].get(q, {}).get(m, "") for m in models] for q in qs], dtype=str).reshape(len(qs), len(models))
        Varr = np.array([[free["V"].get(q, {}).get(m, "") for m in models] for q in qs], dtype=str).reshape(len(qs), len(models))
        if VARIANT_MASK != "ONE_VARIANT":
            C.refuse("VARIANT_MASK %r: the only admitted value is ONE_VARIANT (K8 ruling; the loader judges a variant)"
                     % VARIANT_MASK)
        sched, exhausted = schedule_anchor(Parr, Varr, cfg.N, rng)
        mask = mask_stats(Parr, Varr, models, cfg.N)
        uses = np.zeros(len(qs), dtype=int)
        for i, j, r in sched:
            q = qs[r]
            uses[r] += 1
            matches.append({"anchor": anc, "item_id": q, "variant_id": free["V"][q][models[i]], "model_a": models[i],
                            "model_b": models[j], "match_id": match_id(anc, q, models[i], models[j])})
        stats[anc] = {"questions": len(qs), "matches_before_trim": len(sched), "exhausted_pairs": exhausted,
                      "pairs": len(models) * (len(models) - 1) // 2, "uses": uses.tolist(), "mask": mask}
        # [0761cfa] C0 (h) per anchor: at most N matches per pair of the roster
        per, _tot = schedule_bound(cfg, len(models), 1)
        C.need(len(sched) <= per, "C0 (h) FAILS: anchor %s scheduled %d matches > N x C(%d,2) = %d" % (
            anc, len(sched), len(models), per))
    ids = [m["match_id"] for m in matches]
    C.need(len(ids) == len(set(ids)), "match ids collide")
    require_inside(matches, models, "scheduled")
    return matches, stats


def mask_stats(Parr, Varr, models, N):
    """K8: against the UNMASKED filter (both models answered; convention A), the (pair, question) cells the ONE-variant
    mask loses, per anchor and per model, and the pairs exhausted (fewer than N eligible questions) with and without it."""
    M = len(models)
    lost, ex_m, ex_u, by_model = 0, 0, 0, {m: 0 for m in models}
    for i in range(M):
        for j in range(i + 1, M):
            pa, pb, va, vb = Parr[:, i], Parr[:, j], Varr[:, i], Varr[:, j]
            both = (va != "") & (vb != "")
            unmasked = both & ~((pa != "") & (pb != "") & (pa == pb))
            masked = unmasked & (va == vb)
            k = int(unmasked.sum() - masked.sum())
            if MUTANT == "mask_off_count":
                k = 0
            lost += k
            by_model[models[i]] += k
            by_model[models[j]] += k
            ex_u += int(unmasked.sum() < N)
            ex_m += int(masked.sum() < N)
    return {"lost_cells": lost, "lost_by_model": {m: v for m, v in by_model.items() if v}, "exhausted_masked": ex_m,
            "exhausted_unmasked": ex_u}


def mask_lines(stats, cfg):
    out = []
    for anc in sorted(stats):
        mk = stats[anc]["mask"]
        out.append("  K8 mask (%s, forced deviation, ruled) anchor %s: (pair, question) cells lost %d; pairs exhausted (< %d"
                   " eligible) %d with the mask vs %d unmasked, of %d pairs" % (VARIANT_MASK, anc, mk["lost_cells"], cfg.N,
                                                                              mk["exhausted_masked"],
                                                                              mk["exhausted_unmasked"], stats[anc]["pairs"]))
        if mk["lost_by_model"]:
            out.append("    lost cells per model: %s" % ", ".join("%s %d" % kv for kv in sorted(mk["lost_by_model"].items())))
    return out


def mask_thin_lines(stats):
    """K8 ruling: beside C1, "the mask thins the target design (N 2, all pairs) on anchor X" when more than 2% of the
    anchor's pairs are exhausted BY THE MASK (exhausted with the mask and not without it); both counts printed.
    [0761cfa] the rule is unchanged (share-based); at k 37 an anchor has C(37,2) = 666 pairs, 2% = 13.32, so the line
    fires at 14 or more pairs exhausted by the mask and not at 13."""
    out = []
    for anc in sorted(stats):
        mk, n = stats[anc]["mask"], stats[anc]["pairs"]
        ex = mk["exhausted_masked"] - mk["exhausted_unmasked"]
        line = "(%d of %d pairs exhausted by the mask; %d exhausted with it, %d without it)" % (
            ex, n, mk["exhausted_masked"], mk["exhausted_unmasked"])
        if ex > MASK_THIN_SHARE * n:
            report.hit("K8.THIN")
            out.append("  the mask thins the target design (N 2, all pairs) on anchor %s %s" % (anc, line))
        else:
            report.hit("K8.NOT_THIN")
            out.append("  the mask does not thin the target design beyond 2%% on anchor %s %s" % (anc, line))
    return out


def pair_key(m):
    a, b = sorted((m["model_a"], m["model_b"]))
    return (m["anchor"], a, b)


def trim(cfg, st, matches, out=print):
    """The TRIM RULE (module docstring). Returns (kept matches, removed pair keys, t)."""
    rng = st.np("trim")
    arena = set(cfg.arena12)
    total = len(matches)
    per_pair = {}
    for m in matches:
        per_pair[pair_key(m)] = per_pair.get(pair_key(m), 0) + 1
    anchors = sorted({m["anchor"] for m in matches})
    cands = {}
    for anc in anchors:
        lst = sorted(k for k in per_pair if k[0] == anc and
                     (MUTANT == "trim_arena12" or not (k[1] in arena and k[2] in arena)))
        cands[anc] = [lst[int(i)] for i in rng.permutation(len(lst))]
    if MUTANT == "cap_off" or total <= cfg.cap_matches:
        report.hit("TRIM.NOT_NEEDED" if total <= cfg.cap_matches else "TRIM.MUTANT_CAP_OFF")
        kept, removed, t = list(matches), [], 0
    else:
        t, removed = 0, []
        while True:
            t += 1
            if any(t > len(cands[a]) for a in anchors):
                C.refuse("C0 FAILS: the cap %d cannot be met by trimming non-ARENA12 pairs in equal numbers per anchor"
                         " (t %d)" % (cfg.cap_matches, t))
            removed = [k for a in anchors for k in cands[a][:t]]
            if total - sum(per_pair[k] for k in removed) <= cfg.cap_matches:
                break
        rs = set(removed)
        kept = [m for m in matches if pair_key(m) not in rs]
        report.hit("TRIM.APPLIED")
    arena_pairs = {k for k in per_pair if k[1] in arena and k[2] in arena}
    kept_keys = {pair_key(m) for m in kept}
    C.need(arena_pairs <= kept_keys, "the TRIM removed %d ARENA12 pair(s): NEVER trimmed (amendment 2296877); refused"
           % len(arena_pairs - kept_keys))
    C.need(len(kept) <= cfg.cap_matches, "the schedule has %d matches > the cap %d (8,000 calls): refused, never posted"
           % (len(kept), cfg.cap_matches))
    out("  TRIM: %d scheduled matches %s the cap %d; t = %d pair(s) removed per anchor (%d pairs, %d matches); %d kept;"
        " ARENA12 pairs kept %d of %d" % (total, ">" if total > cfg.cap_matches else "<=", cfg.cap_matches, t,
                                         len(removed), total - len(kept), len(kept), len(arena_pairs & kept_keys),
                                         len(arena_pairs)))
    return kept, removed, t


def schedule_digest(matches):
    return C.sha256_text("".join("%s\t%s\t%s\t%s\t%s\t%s\n" % (m["anchor"], m["match_id"], m["item_id"], m["variant_id"],
                                                              m["model_a"], m["model_b"]) for m in matches))


def draw_pilot_anchors(st, seven, counts14=None):
    names = sorted(seven)
    if MUTANT == "anchors_from_14" and counts14 is not None:
        names = sorted(counts14)
    rng = st.np("anchors")
    idx = rng.choice(len(names), size=2, replace=False)
    return sorted(names[int(i)] for i in idx)


def check_pilot_anchors(chosen, seven, master):
    """C0 (g): the pilot's 2 anchors are inside the registered 7 and reproduce in a fresh Streams."""
    C.need(set(chosen) <= set(seven), "C0 (g) FAILS: the pilot anchors %s are not inside the registered stage-1 7 %s"
           % (chosen, sorted(seven)))
    names = sorted(seven)
    idx = Streams(master).np("anchors").choice(len(names), size=2, replace=False)
    again = sorted(names[int(i)] for i in idx)
    C.need(again == sorted(chosen), "C0 (g) FAILS: the pilot anchors %s do not reproduce (%s) from the registered 7"
           % (chosen, again))
    return again


# ── references and the expected exclusions (free data; the loader re-derives them) ───────────

def predict_references(conn, cfg, matches, free):
    """-> (expected_exclusions {match_id: code}, per-match reference class ONE / NONE / excluded code)."""
    solver = dv2ingest.SOLVER_MODEL
    cache, ref_of = {}, {}
    for vid in sorted({m["variant_id"] for m in matches}):
        rows = conn.execute("SELECT variant_id, vintage, legacy_qid FROM reference WHERE corpus_version=? AND variant_id=?",
                            (cfg.cv, vid)).fetchall()
        v0 = [r for r in rows if r[1] == BOARD_VINTAGE]
        C.need(len(v0) <= 1, "variant %s carries %d %s references: the loader refuses the whole load" % (vid, len(v0),
                                                                                                        BOARD_VINTAGE))
        if not v0:
            ref_of[vid] = None
            continue
        qid = v0[0][2]
        srow = None if qid is None else conn.execute(
            "SELECT options_ordered_sha FROM response WHERE corpus_version=? AND model=? AND legacy_qid=? AND seen_ck=?",
            (cfg.cv, solver, qid, vid)).fetchone()
        C.need(srow is not None, "variant %s: the %s reference has no solver row (the loader refuses the whole load)" % (
            vid, BOARD_VINTAGE))
        ref_of[vid] = LD.ordering_key(_options(conn, srow[0], cache))
    expected, klass = {}, {}
    for m in matches:
        ks = ref_of[m["variant_id"]]
        if ks is None:
            klass[m["match_id"]] = "NONE"
            continue
        ka = free["OK"][m["item_id"]][m["model_a"]]
        kb = free["OK"][m["item_id"]][m["model_b"]]
        if ka != ks or kb != ks:
            code = "excluded_MIXED_referenced" if ka != kb else "excluded_ordering_differs_from_solver"
            expected[m["match_id"]] = code
            klass[m["match_id"]] = code
        else:
            klass[m["match_id"]] = "ONE"
    return expected, klass


def class_tables(matches, klass):
    """Per model and per variant: counts of each reference class (C2)."""
    by_model, by_var = {}, {}
    for m in matches:
        k = klass[m["match_id"]]
        for mo in (m["model_a"], m["model_b"]):
            by_model.setdefault(mo, {}).setdefault(k, 0)
            by_model[mo][k] += 1
        by_var.setdefault(m["variant_id"], {}).setdefault(k, 0)
        by_var[m["variant_id"]][k] += 1
    return by_model, by_var


def requests_of(cfg, matches):
    return [{"match_id": m["match_id"], "variant_id": m["variant_id"], "model_a": m["model_a"], "model_b": m["model_b"],
             "corpus_version": cfg.cv, "batch_id": m["anchor"]} for m in matches]


# ── the payloads (dry-run scan; the payload anchor) ─────────────────────────────────────────

def payload_anchor(rows):
    """sha256 over "match_id TAB order TAB payload_sha256 LF" in schedule order (the dry-run's and the store's)."""
    return C.sha256_text("".join("%s\t%d\t%s\n" % r for r in rows))


def scan_payloads(loaded, rubric, order_ids, out=print):
    """Build and scan BOTH orders of every loaded match (100% of the payloads a run would post). Returns
    (rows (match_id, order, sha), n_scanned, hits by rule)."""
    rows, hits, n = [], {}, 0
    for mid in order_ids:
        inp = loaded.specs[mid]
        for order in (1, 2):
            pl = P.build_payload(inp, rubric, order)
            h = L.scan_hits(pl, inp, rubric, loaded.materials.get(mid))
            n += 1
            for rule, _w in h:
                hits[rule] = hits.get(rule, 0) + 1
            rows.append((mid, order, pl.sha256))
    out("  [LEAK-SCAN dry-run] payloads built and scanned %d of %d (both orders of %d loaded matches); hits %s"
        % (n, 2 * len(order_ids), len(order_ids), json.dumps(hits, sort_keys=True) if hits else "0"))
    return rows, n, hits


# ── the whole plan (shared by --dry-run, --pilot, --run and --analyze's C0 (g)) ─────────────

@dataclass
class Plan:
    cfg: Config
    streams: object
    view_path: str
    view_sha: str
    pool: dict
    counts14: dict
    seven: list
    anchors: list
    roster: list
    quarantined: list
    free: dict
    before: list
    stats: dict
    kept: list
    removed: list
    t: int
    expected: dict
    klass: dict
    digests: dict = field(default_factory=dict)
    dropped: list = field(default_factory=list)         # [0761cfa] the 9 dropped (sorted)
    raw_counts: dict = field(default_factory=dict)      # [0761cfa] per model: cells / empty / short / short_nonempty


def make_plan(cfg, view_path, stage1_record, out=print):
    """Everything up to the load, from free data: pool, anchors, roster, schedule, trim, predicted exclusions."""
    record = cfg.record()
    conn, sha, _meta = C.open_view("arena", view_path, cfg.view_sha if record else None, out)
    try:
        if record:
            C.need(sha == C.EVAL_VIEW_SHA256, "the eval_view is not the split of record's")
        pool = C.pool_of(conn, cfg.cv, cfg.pool_id if record else None)
        anchor_of, counts14, _raw = C.anchor_of_items(conn, cfg.cv, pool)
        out("  [POOL] %s (scope %s): %d EVAL components, %d EVAL items; %d anchors, counts digest %s" % (
            pool["pool_id"], pool["scope"], pool["n_components"], pool["n_items"], len(counts14),
            C.counts_digest(counts14)))
        s1sha = check_stage1_file(stage1_record, cfg)
        seven = stage1.verify(stage1_record, counts=counts14, view_sha=sha, record=record)
        if record:
            C.need(tuple(seven) == STAGE1_ANCHORS_OF_RECORD, "the stage-1 anchors %s are not the record's %s" % (
                seven, STAGE1_ANCHORS_OF_RECORD))
        out("  stage-1 record %s | sha256-lf %s%s" % (os.path.abspath(stage1_record), s1sha,
                                                       " (= the pinned record)" if s1sha == STAGE1_RECORD_SHA256 else
                                                       " (NOT the record: DEV)"))
        st = Streams(cfg.master)
        anchors = draw_pilot_anchors(st, seven, counts14)
        check_pilot_anchors(anchors, seven, cfg.master)
        out("  anchors: the registered stage-1 7 (%s): %s; the pilot's 2 (stream 'anchors', uniformly without"
            " replacement from the 7 sorted by name): %s" % (stage1.REGISTRATION, ", ".join(seven), ", ".join(anchors)))
        roster, quar, dropped = roster_of(conn, cfg)
        dropped_sha = C.sha256_text("\n".join(dropped))
        out("  roster: %d = %d ACTIVE - %d dropped (BANNED_MODELS; author 2026-09-25; amendment %s) of %s (quarantined,"
            " absent: %s); ARENA12 inside: %d of %d, among the dropped: %d; roster sha256-text %s (registered %s)"
            % (len(roster), cfg.active_n, len(dropped), AMENDMENT_K37, cfg.cv, ", ".join(quar) or "none",
               len(set(cfg.arena12) & set(roster)), cfg.k_lo, len(set(cfg.arena12) & set(dropped)),
               C.sha256_text("\n".join(roster)), cfg.roster_sha256))
        out("    dropped (%d): %s | dropped_sha %s" % (len(dropped), ", ".join(dropped), dropped_sha))
        out("    " + ", ".join(roster))
        free = load_free(conn, cfg, anchors, anchor_of, roster)
        before, stats = build_schedule(cfg, st, free, anchors, roster)
        for anc in sorted(stats):
            s = stats[anc]
            out("  anchor %-18s questions %4d | pairs %d | filtered matches before the trim %d | exhausted pairs %d"
                % (anc, s["questions"], s["pairs"], s["matches_before_trim"], s["exhausted_pairs"]))
        out("  (model, item) cells with several responses (unusable, counted): %d" % free["multi_response_cells"])
        for ln in mask_lines(stats, cfg):
            out(ln)
        kept, removed, t = trim(cfg, st, before, out)
        check_c0h(cfg, stats, len(roster), t, out)
        raw = raw_output_counts(free, kept, roster)
        n_empty = sum(v["empty"] for v in raw.values())
        out("  C0 (b) raw outputs on the scheduled cells (zlib-decompressed output_zlib, stripped, before robust_trace):"
            " EMPTY %d, SHORT (< %d) %d, of %d cells; rows naming a model outside the roster: scheduled %d" % (
                n_empty, SHORT_CHARS, sum(v["short"] for v in raw.values()), sum(v["cells"] for v in raw.values()),
                outside_roster(kept, roster)))
        C.need(n_empty == 0, "C0 (b) FAILS (amendment %s): %d EMPTY raw output(s) on the scheduled cells (%s)" % (
            AMENDMENT_K37, n_empty, ", ".join("%s %d" % (m, v["empty"]) for m, v in sorted(raw.items()) if v["empty"])))
        expected, klass = predict_references(conn, cfg, kept, free)
    finally:
        conn.close()
    plan = Plan(cfg, st, view_path, sha, pool, counts14, seven, anchors, roster, quar, free, before, stats, kept, removed,
                t, expected, klass, dropped=dropped, raw_counts=raw)
    plan.digests = {"anchors_sha": C.sha256_text("\n".join(anchors)), "roster_sha": C.sha256_text("\n".join(roster)),
                    "dropped_sha": dropped_sha,
                    "questions_digest": schedule_digest(before), "trim_digest": C.sha256_text(
                        "".join("%s\t%s\t%s\n" % k for k in removed)), "schedule_digest": schedule_digest(kept),
                    "order_sha": C.sha256_text("\n".join(m["match_id"] for m in kept
                                                         if m["match_id"] not in expected))}
    out("  digests: %s" % json.dumps(plan.digests, sort_keys=True))
    return plan


KEY_MATERIAL_LOADS = {"n": 0}      # K4 witness: load_plan (the loader reads gt_raw / answer_text / is_correct) calls


def load_plan(plan, out=print):
    KEY_MATERIAL_LOADS["n"] += 1
    loaded = LD.load_matches(requests_of(plan.cfg, plan.kept), plan.view_path, plan.view_sha if plan.cfg.record() else None,
                             corpus_type="mcq", board_vintage=BOARD_VINTAGE, expected_exclusions=plan.expected, out=out)
    order_ids = [m["match_id"] for m in plan.kept if m["match_id"] not in plan.expected]
    C.need(set(order_ids) == set(loaded.specs), "the loaded matches differ from the schedule minus the expected exclusions")
    return loaded, order_ids


# ── launch guards ───────────────────────────────────────────────────────────────────────────

def open_store_ro(path):
    """THE ONE read-only open of the pilot's own v2 verdict run DB (never a corpus or a view): archv2_arena.ro.open_ro
    (the instrument's opener: refused by name for snapshots_frozen / 20NG, then pool_guard.open_ro: a non-empty -wal or
    -journal refused, mode=ro&immutable=1; logged), then schema_id must be the v2 verdict schema (the check of
    judge_v2.writer.match_verdicts). A corpus / gen_view / eval_view is opened ONLY through data_v2.views.open_eval."""
    c = aro.open_ro(path)
    has = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='run_meta'").fetchone()
    sid = c.execute("SELECT value FROM run_meta WHERE key='schema_id'").fetchone() if has else None
    if sid is None or sid[0] != C.dv2ro.RUN_SCHEMA_ID:
        c.close()
        C.refuse("%s is not a v2 verdict run DB (schema_id %r)" % (path, sid))
    return c


def store_counts(path):
    """(attempt rows = posted calls, verdict rows, error attempts) of a verdict store; zeros when absent."""
    if not os.path.exists(path):
        return 0, 0, 0
    c = open_store_ro(path)
    try:
        a = c.execute("SELECT COUNT(*) FROM attempt").fetchone()[0]
        v = c.execute("SELECT COUNT(*) FROM verdict").fetchone()[0]
        e = c.execute("SELECT COUNT(*) FROM attempt WHERE error_class IS NOT NULL").fetchone()[0]
    finally:
        c.close()
    return int(a), int(v), int(e)


def pending_ro(store_path, only=None):
    """The pending slots (schedule minus verdict, by key), read read-only; restricted to the match ids `only` if given."""
    c = open_store_ro(store_path)
    try:
        sched = c.execute("SELECT run_id, match_id, presentation_order, draw_index FROM schedule").fetchall()
        done = set(c.execute("SELECT run_id, match_id, presentation_order, draw_index FROM verdict").fetchall())
    finally:
        c.close()
    ids = set(only) if only is not None else None
    return [k for k in sched if k not in done and (ids is None or k[1] in ids)]


def posting_day_ok(cfg, today=None):
    today = today or time.strftime("%Y-%m-%d")
    return today >= cfg.earliest_day, today


class _OnlyStore(dv2verdicts.VerdictStore):
    """The pilot launch: pending() restricted to the pilot's matches (the writer's prescan and drain read pending())."""

    def __init__(self, base, only):
        self.conn, self.path, self.run_id = base.conn, base.path, base.run_id
        self._only = set(only)

    def pending(self):
        k = dv2verdicts.SCHEDULE_COLS.index("match_id")
        return [r for r in dv2verdicts.VerdictStore.pending(self) if r[k] in self._only]


def pilot_guard(store_path, pilot_ids, usable=("FIRST", "SECOND", "TIE")):
    """The pilot-12 guard (CANARY D3; READY 65a9173 K3): cached = verdict rows of the pilot slots (2 per match), ERRORED =
    attempt rows with an error class (counted and printed: an errored slot is re-posted on a relaunch), unusable = verdicts
    outside FIRST / SECOND / TIE, foreign = verdict or attempt rows of any other match. PASS iff every pilot slot carries a
    usable verdict (cached == 2 x pilot, unusable 0), foreign 0, and (a registered bound only) errored <= the bound. A
    relaunch that fills an errored slot can therefore PASS."""
    ids = set(pilot_ids)
    c = open_store_ro(store_path)
    try:
        vrows = c.execute("SELECT match_id, presentation_order, vote FROM verdict").fetchall()
        arows = c.execute("SELECT match_id, error_class FROM attempt").fetchall()
    finally:
        c.close()
    cached = sum(1 for m, _o, _v in vrows if m in ids)
    unusable = sum(1 for m, _o, v in vrows if m in ids and v not in usable)
    errored = sum(1 for m, e in arows if m in ids and e is not None)
    foreign = sum(1 for m, _o, _v in vrows if m not in ids) + sum(1 for m, _e in arows if m not in ids)
    ok = cached == 2 * len(ids) and unusable == 0 and foreign == 0
    if PILOT_ERRORED_BOUND is not None:
        ok = ok and errored <= PILOT_ERRORED_BOUND
    if MUTANT == "guard_errored_fails":
        ok = ok and errored == 0
    report.hit("PILOT.GUARD_PASS" if ok else "PILOT.GUARD_FAIL")
    return {"pass": bool(ok), "pilot_matches": len(ids), "cached_calls": cached, "errored_attempts": errored,
            "unusable": unusable, "foreign_rows": foreign, "errored_bound": PILOT_ERRORED_BOUND}


def guard_line(g):
    return ("  [PILOT-GUARD] %s: pilot matches %d, cached order verdicts %d of %d, ERRORED attempts %d (counted; bound %s),"
            " unusable %d, foreign rows %d" % ("PASS" if g["pass"] else "FAIL (the run is refused)", g["pilot_matches"],
                                               g["cached_calls"], 2 * g["pilot_matches"], g["errored_attempts"],
                                               "none registered" if g["errored_bound"] is None else g["errored_bound"],
                                               g["unusable"], g["foreign_rows"]))


def failed_guard_path(store_path):
    """K3: a collision-free FAILED file name (a counter, never a timestamp); the file itself is written mode x."""
    k = 1
    while os.path.exists("%s.pilot_guard_FAILED.%d.json" % (store_path, k)):
        k += 1
    return "%s.pilot_guard_FAILED.%d.json" % (store_path, k)


def journal_path(store_path):
    return store_path + ".invocations.db"


# ── the transport and the store after the pilot-12 incident of 2026-09-25 ─────────────────────────────────────────
# [ADDED 2026-09-25 after the pilot 12 on 64ff708 FAILED its gate (insertion only): all 24 attempts raised "ValueError:
# unknown url type: 'None'" because the K46 path never called rejudge_reasoning.load_env(), so rr.AZURE_ENDPOINT stayed
# None; NO request left the machine, yet the journal and the day ledger booked 24 invocations (they are counted before the
# post, by design). Incident copy experiment_results/archv2/pilot_k46_incident_2026-09-25/ (store sha256 84f00117...,
# journal sha256 995087c3...). Structural fix: (1) load_transport() reads the endpoint / key through rr.load_env() from
# the DATA ROOT's .env (TAXOARENA_DATA_ROOT, else the MAIN checkout), never the worktree's, never echoing a value; (2)
# transport_preflight() refuses a None / empty endpoint, key or deployment and a URL that is not https, and runs BEFORE any
# journal row, post counter, store or ledger row -- in every launch (with or without --go) and in the dry-run; (3) the
# failed store is RETIRED (a record run refuses it; the store of record is pilot_k46_verdicts_run2.db); (4) its journal's
# 24 booked invocations are PRIOR invocations of this test (pinned by sha256), added to the journal side of every
# ledger == journal check, so the ledger's 24 rows reconcile and are never duplicated or dropped.]
INCIDENT_DIR_REL = os.path.join("experiment_results", "archv2", "pilot_k46_incident_2026-09-25")
RETIRED_STORE_NAMES = ("pilot_k46_verdicts.db",)
STORE_OF_RECORD_NAME = "pilot_k46_verdicts_run2.db"
PRIOR_JOURNALS = (
    (os.path.join("experiment_results", "archv2", "pilot_k46", "pilot_k46_verdicts.db.invocations.db"),
     "995087c316036df717471c909f94bc19c088485676b4610ff1a085e2eea80375"),     # sha256 of the bytes (a SQLite file)
)
MUTANT_TRANSPORT = None     # SELFTEST-ONLY: "load_env_skipped"


def data_root():
    """The root whose .env carries the credentials: TAXOARENA_DATA_ROOT, else the MAIN checkout, else this checkout."""
    return os.environ.get("TAXOARENA_DATA_ROOT") or main_checkout() or C.ROOT


def load_transport(root=None, out=print):
    """rejudge_reasoning.load_env() pointed at <root>/.env (rr.ROOT swapped for the call and restored; the module is
    pinned and not edited). Prints the .env PATH only, never a value. REFUSES a missing .env; rr.load_env's own assert
    vanishes under python -O, so transport_preflight is the guard that binds."""
    root = root or data_root()
    envp = os.path.join(root, ".env")
    C.need(os.path.isfile(envp), "TRANSPORT: no .env at the data root %s (set TAXOARENA_DATA_ROOT to the main checkout):"
           " refused before any post" % root)
    if MUTANT_TRANSPORT == "load_env_skipped":
        out("  transport: load_env SKIPPED (MUTANT load_env_skipped)")
        return envp
    saved = rr.ROOT
    try:
        rr.ROOT = root
        try:
            rr.load_env()
        except AssertionError as e:
            C.refuse("TRANSPORT: rejudge_reasoning.load_env found no endpoint / key in %s (%s): refused" % (envp, e))
    finally:
        rr.ROOT = saved
    out("  transport: credentials loaded from %s through rejudge_reasoning.load_env (values not printed)" % envp)
    return envp


def transport_preflight(out=print):
    """REFUSES unless the provider is azure and rejudge_reasoning's endpoint, key and deployment (JUDGE_MODEL) are
    non-empty strings and the endpoint parses as an https URL with a host. Zero calls; writes nothing. Prints the host
    and the deployment only, never the key or the full URL."""
    from urllib.parse import urlparse
    bad = []
    if rr.PROVIDER != "azure":
        bad.append("provider %r is not azure" % rr.PROVIDER)
    for name, v in (("endpoint (AZURE_ENDPOINT)", rr.AZURE_ENDPOINT), ("key (AZURE_KEY)", rr.AZURE_KEY),
                    ("deployment (JUDGE_MODEL)", rr.JUDGE_MODEL)):
        if not isinstance(v, str) or not v.strip():
            bad.append("%s is %s" % (name, "None" if v is None else "empty"))
    host = None
    if isinstance(rr.AZURE_ENDPOINT, str) and rr.AZURE_ENDPOINT.strip():
        try:
            u = urlparse(rr.AZURE_ENDPOINT)
            host = u.hostname
            if u.scheme != "https" or not host:
                bad.append("the endpoint does not parse as an https URL with a host (scheme %r)" % u.scheme)
        except ValueError:
            bad.append("the endpoint does not parse as a URL")
    if bad:
        C.refuse("TRANSPORT PREFLIGHT: REFUSED before any journal row, post or ledger row: %s (the credentials come from"
                 " the data root's .env through load_transport)" % "; ".join(bad))
    line = "TRANSPORT PREFLIGHT: OK (endpoint host=%s, deployment=%s)" % (host, rr.JUDGE_MODEL)
    out(line)
    return line


def check_store_path(cfg, store_path):
    """A record run REFUSES the retired store of the 2026-09-25 incident (F9: its recipe identity and script blob differ
    and it carries 24 errored attempts); the store of record is STORE_OF_RECORD_NAME."""
    if cfg.record():
        C.need(os.path.basename(store_path) not in RETIRED_STORE_NAMES, "the store %s is RETIRED: the pilot 12 of"
               " 2026-09-25 failed there without a request leaving the machine (load_env was never called; incident copy"
               " %s); the store of record is %s" % (store_path, INCIDENT_DIR_REL, STORE_OF_RECORD_NAME))
    return store_path


def prior_journals_state(cfg, ledger_dir, prior_journals=None):
    """The invocations of this test booked by RETIRED stores' journals: {"invocations", "per_day", "paths"}. Record mode
    reads PRIOR_JOURNALS under the ledger directory's checkout (each sha256 pinned, none unresolved); DEV reads only
    what the caller passes (selftest)."""
    if prior_journals is None:
        prior_journals = PRIOR_JOURNALS if cfg.record() else ()
    base = os.path.dirname(os.path.realpath(os.path.abspath(ledger_dir)))
    tot, per_day, paths = 0, {}, []
    for rel, sha in prior_journals:
        p = rel if os.path.isabs(rel) else os.path.join(base, rel)
        C.need(os.path.isfile(p), "the prior journal %s is missing (pinned sha256 %s)" % (p, sha))
        got = C.dv2ro.file_sha256(p)
        C.need(got == sha, "the prior journal %s is sha256 %s, not the pinned %s: refused" % (p, got, sha))
        js = ACC.read_journal(p)
        C.need(not js["unresolved"], "the prior journal %s has unresolved invocations %s" % (p, js["unresolved"]))
        tot += js["invocations"]
        for d, n in js["per_day"].items():
            per_day[d] = per_day.get(d, 0) + int(n)
        paths.append(p)
    return {"invocations": tot, "per_day": per_day, "paths": paths}


def pool_line(jpath, workers, pooled=None):
    """[JV2-PARALLEL-POSTING EC5] the [POOL] line of a launch without --go (and of the CLI's dry-run): the workers, and
    the journal's max_inflight (read read-only) or the bound a new journal would be created with. Zero calls."""
    pooled = (workers > 1) if pooled is None else pooled
    if os.path.exists(jpath):
        mi = ACC.journal_max_inflight(jpath)
        j = "journal max_inflight %d (%s)" % (mi, "journal v2" if mi > 1 else "created at workers 1")
        ok = "OK" if workers <= mi and not (pooled and mi == 1) else "REFUSED at the launch (%s)" % (
            "workers > max_inflight" if workers > mi else "a pooled launch on it")
    else:
        j = "journal max_inflight %d (a new journal; %s)" % (
            POOL.MAX_INFLIGHT if pooled else 1, "journal v2" if pooled else "today's DDL")
        ok = "OK"
    return "[POOL] workers %d (%s); %s; registered maximum %d -> %s" % (
        workers, "pipelined path" if pooled else "sequential path", j, POOL.MAX_INFLIGHT, ok)


def _payload_sha(system, user):
    return hashlib.sha256(rr.payload_bytes(system, user)).hexdigest()


def launch(plan, loaded, order_ids, rubric, store_path, ledger_dir, call_full, mode, expect, script_blob, go=False,
           today=None, out=print, clock=None, prior_journals=None, workers=1, rate=None):
    """mode "pilot" (the first pilot_n loaded matches) or "run" (every pending slot, after a PASSED pilot guard).
    expect: {"payload_anchor", "order_sha"} from the dry-run (REQUIRED in a record launch). Posts only with go, and every
    post through the write-ahead journal (accounting.py, K1).
    [2026-09-25] the posting day is fixed HERE, once; the guard, the journal rows and the ledger append carry it (day=), and
    every post is refused once the local date differs (accounting.wrap_call: a clean stop, the relaunch resumes). clock:
    SELFTEST-ONLY; by default the local date, or the constant `today` when a test fixes it.
    [JV2-PARALLEL-POSTING] workers: 1 (today's launch) or 2..judge_v2.pool.MAX_INFLIGHT; rate: a judge_v2.pool.RateConfig
    (None: the default RateConfig on a pooled launch; given at workers 1: the POOLED path at bound 1, the rate control
    protecting a single poster). POOLED = workers > 1 or rate given (the module docstring)."""
    cfg = plan.cfg
    C.need(mode in ("pilot", "run"), "launch mode %r" % mode)
    C.need(isinstance(workers, int) and not isinstance(workers, bool) and 1 <= workers <= POOL.MAX_INFLIGHT,
           "launch workers %r (1 <= workers <= %d)" % (workers, POOL.MAX_INFLIGHT))
    pooled = workers > 1 or rate is not None
    C.need(rate is None or isinstance(rate, POOL.RateConfig), "launch rate %r is not a judge_v2.pool.RateConfig" % (rate,))
    C.need(cfg.ceiling_calls <= ACC.AUTHOR_HARD_CAP, "a ceiling above the author's hard %d" % ACC.AUTHOR_HARD_CAP)
    ok_day, day = posting_day_ok(cfg, today)
    C.need(ok_day, "posting day %s is before %s (a fresh posting day, the registration): refused" % (day, cfg.earliest_day))
    # [2026-09-25 incident] the transport preflight and the retired store, BEFORE any journal / store / ledger write
    # [JV2-PARALLEL-POSTING E-7] ... and before the pool, at every workers
    if not (MUTANT_POOL == "preflight_after_pool" or (MUTANT_POOL == "preflight_skipped_pooled" and pooled)):
        transport_preflight(out)
    check_store_path(cfg, store_path)
    prior = prior_journals_state(cfg, ledger_dir, prior_journals)
    if prior["paths"]:
        out("  prior journals (retired stores; counted on the journal side): %d invocation(s) %s in %s" % (
            prior["invocations"], json.dumps(prior["per_day"], sort_keys=True), prior["paths"]))
    if clock is None:
        clock = (lambda: today) if today else ACC.local_day
    out("  posting day fixed at the launch's start: %s (the guard's (iii), every journal row and the ledger append carry"
        " it; a post is REFUSED once the local date differs: a clean stop, the relaunch resumes)" % day)
    okp, bad = judge_pins_ok(cfg)
    C.need(okp, "C0 (c): the judge layer's pins differ from the expected (%s): %s" % (cfg.judge_pins, bad))
    check_ledger_dir(ledger_dir, cfg, out)
    rows, n, hits = scan_payloads(loaded, rubric, order_ids, out)
    C.need(not hits, "the dry-run scan found leak hits %s: refused" % hits)
    anchor = payload_anchor(rows)
    if cfg.record():
        C.need(expect.get("payload_anchor") and expect.get("order_sha"), "a record launch names the dry-run's payload"
               " anchor and order sha (--expect-payload-anchor, --expect-order-sha)")
    for k, v in (("payload_anchor", anchor), ("order_sha", plan.digests["order_sha"])):
        if expect.get(k) is not None:
            C.need(expect[k] == v, "C0 (c)/(g): the %s %s differs from the dry-run's %s" % (k, v, expect[k]))
    pilot_ids = order_ids[:cfg.pilot_n]
    manifest_path = store_path + ".launch.json"
    jpath = journal_path(store_path)
    ctx = {"script_blob": script_blob, "pool_id": plan.pool["pool_id"]}
    if not os.path.exists(store_path):
        C.need(mode == "pilot", "the first launch is the pilot 12 (the guard runs before the run)")
        C.need(not os.path.exists(jpath), "a journal %s without its store: refused" % jpath)
    else:
        C.need(os.path.exists(jpath), "the store %s has no invocation journal %s: refused (K1)" % (store_path, jpath))
    if mode == "pilot":
        C.need(not os.path.exists(store_path + ".pilot_guard.json"), "the pilot 12 already PASSED (%s.pilot_guard.json):"
               " the next launch is --run" % store_path)
    a0, _v0, _e0 = store_counts(store_path)
    if not go:
        # no writable open without --go: the pending count and the journal are read read-only
        if os.path.exists(store_path):
            planned = len(pending_ro(store_path, pilot_ids if mode == "pilot" else None))
        else:
            planned = 2 * len(pilot_ids)
        js = ACC.read_journal(jpath)
        nums = ACC.guard_day(REGISTRATION, planned, a0, ledger_dir, day=day, refuse=False, what=mode + " (no --go)",
                             out=out, own_journal=js["invocations"] + prior["invocations"])
        out("  NOT POSTED (no --go): %d slot(s) would be posted%s; journal invocations %d, unresolved %d" % (
            planned, "" if os.path.exists(store_path) else " (the store does not exist yet; nothing created)",
            js["invocations"], len(js["unresolved"])))
        out("  " + pool_line(jpath, workers, pooled))       # [JV2-PARALLEL-POSTING EC5]
        if pooled:
            out("  " + (rate or POOL.RateConfig()).line())
        return {"posted": 0, "planned": planned, "account": nums}
    creating = not os.path.exists(jpath)
    journal = ACC.Journal.open(jpath, cap=min(cfg.ceiling_calls, ACC.AUTHOR_HARD_CAP), create=creating,
                               max_inflight=POOL.MAX_INFLIGHT if (pooled and creating) else None)
    posts = {"n": 0}
    planned_pending = None
    guard_nums = None
    writer = None
    label = None
    try:
        orphans, caught = ACC.reconcile(REGISTRATION, journal, ledger_dir, out, prior=prior)
        js = journal.state()
        label = "%s#%d %s" % (mode, js["launches"] + 1, RUN_ID)
        if pooled:
            label += " w=%d" % workers                      # [JV2-PARALLEL-POSTING E-1] recorded per launch
        journal.begin_launch(label, workers, pooled)        # refuses workers > the journal's max_inflight, before any post
        out("  [JOURNAL] %s: invocations %d (orphans resolved now %d, reconciled into the ledger now %d; by outcome %s)" % (
            jpath, js["invocations"], orphans, caught, json.dumps(js["by_outcome"], sort_keys=True)))
        if os.path.exists(store_path):
            writer = W.JudgeWriter.open(store_path, loaded, rubric, ctx)
        else:
            man = {"registration": REGISTRATION, "run_id": RUN_ID, "digests": plan.digests, "payload_anchor": anchor,
                   "pilot_ids": pilot_ids, "expected_exclusions": plan.expected, "config": asdict(cfg),
                   "rubric_sha256": rubric.rubric_sha256, "rubric_artefact_sha256": rubric.artefact_id,
                   "rubric_slot": RUBRIC_SLOT_LINE, "system_turn_sha256": C.sha256_text(P.build_system(rubric)),
                   "eval_view_sha256_bytes": plan.view_sha, "streams_digest": plan.streams.digest(),
                   "judge_v2_pins": W._pins(), "archv2_pilot_lf16": C.package_lf16(), "persona_sha256": persona_sha(),
                   # [0761cfa] REUSE CONDITION (v): stage-1 reuse only if stage 1's roster sha256-text equals this one
                   "roster_sha256": plan.digests["roster_sha"], "roster_n": len(plan.roster),
                   "dropped_sha256": plan.digests["dropped_sha"], "amendment_k37": AMENDMENT_K37}
            C.write_once_json(manifest_path, man)
            writer = W.JudgeWriter.create(store_path, REGISTRATION, RUN_ID, loaded, rubric, ctx, n_draws=1)
        with open(manifest_path, encoding="utf-8") as f:
            man = json.load(f)
        C.need(man["digests"] == plan.digests and man["payload_anchor"] == anchor and man["pilot_ids"] == pilot_ids,
               "this launch's schedule / payload anchor / pilot ids differ from the first launch's (%s)" % manifest_path)
        if mode == "run":
            C.need(os.path.exists(store_path + ".pilot_guard.json"), "the run is refused: no PASSED pilot guard file")
            g = pilot_guard(store_path, pilot_ids)
            out(guard_line(g))
            # on a relaunch of the run other matches' rows exist (foreign to the pilot); the pilot's own slots must still
            # be complete and usable
            C.need(g["cached_calls"] == 2 * g["pilot_matches"] and g["unusable"] == 0,
                   "the run is refused: the pilot 12 are not complete and usable in the store")
        if mode == "pilot":
            writer.store = _OnlyStore(writer.store, pilot_ids)
        planned_pending = len(writer.store.pending())
        guard_nums = ACC.guard_day(REGISTRATION, planned_pending, a0, ledger_dir, day=day, refuse=True, what=mode,
                                   out=out, own_journal=journal.state()["invocations"] + prior["invocations"])
        slot_of = {}
        for mid, order, sha in rows:
            slot_of.setdefault(sha, []).append((mid, order))
        if MUTANT_POOL == "preflight_after_pool":
            transport_preflight(out)
        if not pooled:
            call = ACC.wrap_call(call_full, journal, slot_of, posts, label, day, _payload_sha, clock=clock)
            writer.run(call, out=out)
        else:
            call = ACC.TwoPhaseCall(call_full, journal, slot_of, posts, label, day, _payload_sha, clock=clock)
            writer.run(call, out=out, workers=workers, rate=rate or POOL.RateConfig())
    finally:
        if writer is not None:
            writer.close()
        if posts["n"]:
            ACC.append(REGISTRATION, label, posts["n"], ledger_dir, day=day)
        jn = journal.state()["invocations"]
        journal.close()
    led = ACC.check_equal(REGISTRATION, jn + prior["invocations"], ledger_dir, "at the end of the launch")
    a1, _v1, _e1 = store_counts(store_path)
    out("  [JOURNAL] launch %s: posted %d (holder), journal invocations %d + prior %d = ledger %d; store attempts %d -> %d"
        % (label, posts["n"], jn, prior["invocations"], led, a0, a1))
    res = {"posted": posts["n"], "planned": planned_pending, "account": guard_nums}
    if mode == "pilot":
        g = pilot_guard(store_path, pilot_ids)
        out(guard_line(g))
        path = store_path + ".pilot_guard.json" if g["pass"] else failed_guard_path(store_path)
        C.write_once_json(path, g)
        res["guard"] = g
        C.need(g["pass"], "the pilot-12 guard FAILED: the run is refused (%s)" % json.dumps(g, sort_keys=True))
    return res
