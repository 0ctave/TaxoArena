"""harness_extractor.py -- HARNESS-EXTRACTOR (amended; HF post 3, "The harness picks the winner"): the MATH + IFEval scorer gap
on the 18-model union roster. Re-scoring the cached raw MATH and IFEval outputs under the documented scorers, do the model
rankings hold (min pairwise Kendall tau-b >= 0.85 AND max rank shift <= 2)? ZERO judge calls; no construction; no embedder; CPU.

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-10-08 (before any code or call) — HARNESS-EXTRACTOR
(amended; supersedes the MMLU-Pro design before any build): re-scoring the cached raw MATH and IFEval outputs of the 18-model
union roster under the documented scorers, do the model rankings hold (min pairwise Kendall tau-b >= 0.85 and max rank shift <=
2)? (zero calls; CPU readout; HF post 3)" (L25229-L25315, _as_of 16ff6d0d), with the registrar's record directly before it
(L25221-L25227) and the brackets of "## Author's decision 2026-10-08 ... D-2026-10-08-1..6 ..." (L25317-L25327, _as_of bb5eb124;
authority docs/agents/author_decisions/2026-10-08.md, 5211616a: D-5 "Official scorer, H as sensitivity (Recommended)"; HX2 no
longer informs a scorer-of-record choice and is scored as registered). Results record docs/agents/results/HARNESS-EXTRACTOR.json.
The MATH criteria CONFIRM a disclosed pilot (the audit on E:/TaxoArena_tmp/math_audit/, read-only); IFEval is blind.

LAUNCH SEQUENCE (the run-operator; plain form from the MAIN checkout, or from a worktree with --data-root <main checkout>; rule 7:
--dry-run and --run are POOL READERS: `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` must exit 1 (free); the script runs
that same check itself before any read and REFUSES on exit 0 (busy) or any other result) [DELTA 2026-10-09: with its own
process and parent chain excluded from busy.ps1's scan, the excluded PIDs printed on the rule-7 line; see DELTA below]:
  0. python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest   # fixtures only
     python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants    # the mutant table
     [DELTA 4, F-2: both need the REAL DBs' schema (the fixture tables are built from their sqlite_master, read-only immutable);
     from a worktree append --data-root <main checkout>; without it the selftest FAILS (fail-closed), it never falls back]
  1. python tools/analysis/harness_extractor.py --dry-run   # POOL line first; busy; pins; the H table pin; R1 (471 / 427);
        roster and per-model row counts (no scorer column is selected [from the DB views; the raw IFEval sample files' strict /
        loose verdict fields ARE parsed into memory for the join and never printed: DELTA L-1]: the tripwire seals is_correct /
        model_output / non_terminated [DELTA 4: is_correct covers eval_results_mathfix.is_correct]); [DELTA 4, S-1: the SCHEMA
        CONFORMANCE block, one line per table.column the --run / --dry-run statements name, checked against the real DBs]; the
        raw IFEval sample files and their sha256; planned B; NO statistic; writes nothing
  2. python tools/analysis/harness_extractor.py --run       # the whole readout; the outcome WRITE-ONCE (mode x) at
        <data root>/experiment_results/hf_blog/harness_extractor/harness_extractor_outcome.txt and the figure data WRITE-ONCE at
        E:/TaxoArena_tmp/blog/harness/harness_extractor_scores.json (scorer x model accuracies and ranks, category shares; no
        response text, R5). Runtime: minutes (B 2,000 weighted means over 18 x about 1,300 and 18 x 541; the DB sha256 twice).
  Outputs are NEVER committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_harness_extractor with SHA256SUMS.txt.
  Then the adversarial-reviewer (numbers), the registrar. No cache, --pilot or truncation guard: zero calls, one deterministic pass.

DATA (as registered; DATA OBJECTS AND HYGIENE):
  POOL   pool_guard.assert_pool_of_record("paeec37aa28063c75") is the first printed line (R1's object: the twin rule is keyed on
         that pool's EVAL ids). No split word is claimed (S3): a scorer comparison over all cached MATH / IFEval rows.
  DB     <data root>/multicorpus_cache_v1.db opened through pool_guard.open_ro (mode=ro&immutable=1; a non-empty -wal / -journal
         refuses), wrapped in the KeyTripwire (v2_reader_guards): corpus_questions (question_id, source, upstream_id, text,
         target), eval_results (model_output, is_correct), eval_results_mathfix (is_correct [DELTA 4, F-1: the real column; the
         former text named a column that does not exist]). sha256-bytes before and
         after the read; a difference REFUSES.
  R1     the paeec EVAL ids whose corpus_questions.text is byte-equal to the text of any id outside that EVAL set: REFUSED unless
         471 ids / 427 distinct texts; dropped first; then every remaining group of byte-equal texts is collapsed to its lowest
         question_id; counts printed per source (the MATH and IFEval questions kept are scored).
  ROSTER the models with MATH rows in eval_results, Meta-Llama-3-70B-Instruct excluded (counted, never scored): 18, the same 18
         on IFEval; every model has 1,324 MATH and 541 IFEval rows; a duplicate (question_id, model) or a kept question without
         all 18 rows REFUSES.
  CLUSTERS CK-CLOSE-v1 components: split_side.stem_key of the question text, within source (Kish sum(n^2)/sum(n) printed).

SCORERS (INSTRUMENT; every one frozen in code before any data are read):
  MATH X0  eval_results.is_correct, as stored (the imported harness verdict; the official scorer of record, D-5).
  MATH MF  eval_results_mathfix.is_correct, as stored (MATH-FIX) [DELTA 4, F-1]. A MATH row without it, or a value outside {0, 1},
           REFUSES.
  MATH H   the pinned H table (math_scorer_h.py --run, 62d269af; READY f4f7e0a0): <data root>/experiment_results/math_scorer_h/
           math_h_table.csv, sha256-lf 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1, 23,832 rows, REFUSED
           otherwise. Its definition is the registered one (H credits iff X0 credits OR a stated answer outside any unclosed think
           block matches the reference as a string or an exact value; unit-only prefix allowed; corrected references 2060002 ->
           20x+23y+26z-69=0, 2060129 -> 11x+6y+5z+86=0, 2000164 -> 4x-5y=-50 inside H only; corrections printed with their
           source). Two checks per row: the table's route is "imported" iff X0 = 1, and the table's H equals the pinned
           implementation math_scorer_h.h_score recomputed on the row (blob:3ab51e3f, imported); any difference REFUSES.
  MATH H-L (lenient; beside, not used by any criterion): H, plus a conclusion inside an unclosed think block (the R1
           convention): a row with "<think>" and no "</think>" is also credited iff h_score credits the text after its last
           "<think>" (region() then delivers the whole thinking; the same candidates, modes and corrected references).
  IFEval I0  eval_results.is_correct, as stored (the imported prompt_level_strict_acc).
  IFEval IS / IL  prompt-level strict / loose of the official IFEval instruction checks. [HX-R1, DEVIATION FORCED BY THE CODE
           BASE, for the READY and the registrar: the registration says "re-scored from the raw responses with the official IFEval
           instruction checks (the repo's checker, version printed)"; no official checker is installed here (lm_eval /
           instruction_following_eval absent; the offline re-implementation in checker_answer_ingest.py has no langdetect and is
           kept there as a diagnostic only). IS and IL are therefore the official checker's OWN per-sample verdicts
           (prompt_level_strict_acc, prompt_level_loose_acc; instruction-level inst_level_strict_acc / inst_level_loose_acc beside)
           read from the leaderboard harness's raw sample files on disk, <data root>/experiment_results/multicorpus/raw/<model>/
           */samples_leaderboard_ifeval_*.jsonl (exactly one per model; each file's name and sha256 printed as the "version": the
           files carry no harness version field), joined by (model, doc_id == corpus_questions.upstream_id) and validated row by
           row (doc.prompt == the question text and resps[0][0] == eval_results.model_output, else REFUSED), as
           checker_answer_ingest.py's IFEval backfill does. Rows with IS != I0 are counted and printed (expected 0: I0 was
           ingested from the same field).]
  Disagreement categories: the audit's 7 categories, the ordered rule list categorise() COPIED VERBATIM below from
           E:/TaxoArena_tmp/math_audit/math_scorer_audit.py (sha256-lf16:b22251009ac14ab5; the selftest asserts the copied source
           text equals the file's, via ast), first match wins: CONFLICT_stated_wrong_other_matched, LASTNUM_ONLY_no_stated_answer,
           PREFIX_partial_numeric, NONTERM_stated_answer_matches, EQUIV_numeric_form, BOXED_no_minerva_sentence,
           FORMAT_minerva_present_norm_mismatch. Applied to the X0-vs-MF disagreements (HX5) and, beside, to the MF-vs-H ones.
           [HX-R2, DEVIATION FORCED BY THE FROZEN RULE LIST: categorise(resp, target, nt) reads the non-terminated flag nt, which
           the audit took from experiment_results/multicorpus/checker_answers_v2.db (math_checker_answers_v2.non_terminated); that
           DB is opened here read-only (pool_guard.open_ro) for that one column; a MATH row without it REFUSES. The registration's
           DATA OBJECTS list multicorpus_cache_v1.db only.]
  Ranks by accuracy, rank 1 = the highest, ties at MID-RANK. Kendall tau-b. Rank shift = |rank under A - rank under B|.
  Interval: question-level component bootstrap, B 2,000, default_rng(20261008): per replicate the MATH components then the IFEval
  components are resampled with replacement (one stream, in that order); every scorer reads the same weights. Percentile 2.5 /
  97.5 (numpy linear). S_w = the share of replicates that give the point's word (HX1, HX2, HX3, HX5). DEFF (measured, beside):
  the component-bootstrap variance over an i.i.d. bootstrap on default_rng(20261009) (questions for HX1 / HX4; disagreement
  rows for HX5), the same number of replicates.

READINGS (stated, for the READY to confirm or refuse; none chosen silently):
  [HX-R3] min tau-b and max shift are computed at full precision; the word compares round(min tau-b, 12) >= 0.85 and max shift
          <= 2 (shifts are multiples of 0.5 under mid-ranks).
  [HX-R4] RESOLVED by the registrar (da1ef992, prog L25366, bracket at L25258; pre-data): rule 8 refutes RANKS-MOVE iff every
          pairwise tau-b >= 0.85 AND the max rank shift is <= 2 (the exact complement of HX1); a mid-rank shift of 2.5 reads
          RANKS-MOVE and is NOT a refutation. Implemented in rule8_hx1 (DELTA 2, B-2); the former "REGISTRATION DEFECT HX-R4
          REACHED" branch is unreachable and removed.
  [HX-R5] HX2's FAILS clause ("either word is refuted by the other word's observable") is printed as: the observed word's
          refutation = the other word's observable (tau-b and shift on the {MF, H} pair).
  [HX-R6] HX4's interval is the 95% percentile interval of acc_MF - acc_H per model; "wholly beyond 0.02 in absolute value" =
          lower bound > 0.02 or upper bound < -0.02. HX5's shares are weighted by the component multiplicities of the
          disagreement rows' questions; a replicate with no disagreement row is dropped for HX5 (counted).
  [HX-R7] Predictions: a band is HELD iff the point lies in it (closed); words by the multi-outcome Brier sum (two outcomes).
          P2 reads the HX1 minimum pairwise tau-b (the registration expects it on the X0-MF pair; the pair is printed).
  Not applicable (stated): wrong(established) and tie conventions A / B (no judge verdict enters; scorers only).

CRITERIA (verbatim words; each rule exhaustive and exclusive; computed values are bool()-cast, never identity-tested):
  HX1 DECIDING (point; "(stable)" iff S_w >= 0.80, else "(fragile)"): {X0, MF, H}: RANKS-HOLD iff min pairwise tau-b >= 0.85
      AND max rank shift <= 2; RANKS-MOVE otherwise. Rule 8 (as amended by HX-R4): RANKS-MOVE refuted iff every pair tau-b
      >= 0.85 and no model moves more than 2 ranks (max shift <= 2). F-HX fires iff HX1 reads RANKS-HOLD.
  HX2 (point): {MF, H}, the same rule. F-H fires iff HX2 reads RANKS-HOLD. [DELTA 3: HX2 DESCRIPTIVE-ONLY BY SUPPORT (registrar S-1,
      prog L25412-L25418), its word printed "(descriptive-only by support)"; ruling F-H-SUPPORT: F-H is printed "(descriptive-only
      by support; decides nothing)" and takes no part in the FALSIFIER OF RECORD line, which reads F-HX alone.]
  HX3 (point; DESCRIPTIVE-ONLY by Support (f), printed "(descriptive-only by support)"): {I0, IS, IL}, the same rule.
  HX4 (the 95% INTERVAL decides): SHIFT-MATERIAL iff >= 1 model's acc_MF - acc_H interval lies wholly beyond |0.02|; else
      SHIFT-SMALL. Rule 8: SHIFT-MATERIAL refuted if no model's bound clears 0.02. Beside: X0-vs-MF and IS-vs-IL.
  HX5 (point): FORMAT-DOMINATED iff the share of BOXED_no_minerva_sentence + FORMAT_minerva_present_norm_mismatch +
      EQUIV_numeric_form among the X0-vs-MF disagreements (after R1) >= 0.50; MIXED otherwise. All 7 shares with intervals.
  SENSITIVITY (decides nothing): HX1 and HX2 recomputed without the 3 corrupted-reference questions, and with H-L for H.
  PREDICTIONS P1-P8 as registered; SUPPORT (a)-(g) printed planned beside measured.

SELFTEST (--selftest; fixtures only: a synthetic multicorpus DB, a synthetic checker_answers_v2 DB, raw IFEval sample files, an H
table built by the pinned h_score and pinned in the fixture cfg, a pool id file hashed by pool_guard; nothing of record is opened
[DELTA 4, F-2: EXCEPT the schema of the two real DBs, multicorpus_cache_v1.db and checker_answers_v2.db, through pool_guard.open_ro
(mode=ro&immutable=1): sqlite_master and PRAGMA table_info only, no row; the fixture tables are created from that DDL];
temp under scratch_dir). The cases are listed after the SELFTEST marker (SELFTEST_DOC).
MUTANTS (--mutants; each edits the code ABOVE the SELFTEST marker in memory and runs the whole selftest; KILLED iff it fails; X00 is
the control and must survive): the MUTANTS tuple at the end of this file (X01-X73: the HX1-HX3 rule, its edges, min<->max,
first-pair-only, wrong set / population; HX4 / HX5 bounds, sides, populations, weights; every scorer read; every refusal and gate;
the bootstrap streams, units and order; sensitivity, predictions, Support, the header). Its last run is in the commit message.
DELTA (2026-10-09; READY_HARNESS-EXTRACTOR.md B-1 and L-1; nothing else changed):
  B-1 busy_check runs the SAME E:/TaxoArena_tmp/busy.ps1, unmodified, inside a PowerShell session whose Get-CimInstance drops
      this process and its parent chain (each ancestor no younger than its child), so busy.ps1's pattern (which names
      harness_extractor) no longer sees the caller; java, peers and every other python still make it exit 0. Fail-closed: a
      throw (exit 3), no exit code (99) or an exit that bypasses the report REFUSES. The rule-7 line prints the excluded PIDs.
      Selftest busyself (real busy.ps1 + sandbox copies, through busy_check). busy.ps1 itself is not changed (shared).
  L-1 the dry-run's closing line now says the IFEval sample files' verdict fields were parsed (not printed).
DELTA 2 (2026-10-09; READY_HARNESS-EXTRACTOR_delta.md B-2; ruling HX-R4, prog L25366; nothing else changed):
  B-2 rule8_hx1 reads `max_shift <= shift_bar` (2) in place of `< move_bar` (3; REG.move_bar removed); the RULE 8 (HX1) lines read
      "no model moves more than 2 ranks" / "a model moving more than 2 ranks"; the HX1.DEFECT_R4 branch and its line are removed
      (unreachable: rule 8 is now the exact complement of the HX1 word). The selftest that enforced the superseded rule is
      fixed (pure: shift 2.0 refuted, 2.5 not; verdicts: tau-b 0.9 / shift 2.5 prints "RANKS-MOVE is not refuted" and no HX-R4
      text; run_e2e oracle: rule 8 at <= 2 and == (HX1 word is RANKS-HOLD); the "edge" fixture, end to end, reads RANKS-MOVE at
      max shift 2.5 with every tau-b >= 0.85 and prints "not refuted"). X13 now restores the superseded `< 3`; X15 is rule 8 at
      a strict `< 2`; X83 the superseded rule-8 text; X84 rule 8 inverted. Support (d)-(f) and SUPPORT_PLAN are unchanged here
      (the registrar's re-derivation is owed; a further delta follows it).
DELTA 3 (2026-10-09; READY_HARNESS-EXTRACTOR_delta2.md D-3 / T-1; registrar S-1 and ruling F-H-SUPPORT, prog L25412-L25418):
  D-3 SUPPORT_PLAN carries the re-derived (d)-(f): SE(tau) = 0.03374 x sqrt(2,056 / n), floor 0.0337 (TAU_SD0 / TAU_N0 / TAU_FLOOR,
      printed with the TRANSPORT ASSUMPTION): HX1 0.0420 / 0.118, HX2 0.0420 / 0.118, HX3 0.0658 / 0.184, HX4 0.0095 / 0.027, HX5
      0.0072 / 0.020; the DEFF / n_eff fields of HX1-HX3 read "carried by the transported realised SD" / "not entering" (the
      registrar's DEFF note); each row's word is COMPUTED by plan_word (SCOREABLE iff |predicted - bar| >= MDE80): HX1 SCOREABLE,
      HX2 "DESCRIPTIVE-ONLY (by support)", HX3 DESCRIPTIVE-ONLY, HX4 / HX5 SCOREABLE. The HX2 word line gains "(descriptive-only by
      support)"; the F-H lines read "FALSIFIER F-H (descriptive-only by support; decides nothing): ..."; a new line "FALSIFIER OF
      RECORD: F-HX FIRED | NOT FIRED (F-H takes no part; ruling F-H-SUPPORT)" is computed from HX1 alone; the plan block prints the
      ruling. P4 is scored as written (unchanged). Nothing else changed (rules, statistics, reads, refusals, outputs' paths).
  T-1 pure / verdicts: a NON-first pair at tau-b 0.7647 with max shift 2, and a NaN pair with max shift 0.5, through set_word:
      rule 8 "not refuted" and rule8_hx1(h) == (word == RANKS-HOLD) (H03 / H04 die). run_e2e gains the "shift2" fixture (X15):
      the "hold" fixture with MATH-FIX credits on one model, chosen by the ORACLE so that HX1 reads RANKS-HOLD at max shift
      EXACTLY 2.0 with every tau-b >= 0.85; end to end RULE 8 prints REFUTED, F-HX FIRED and the FALSIFIER OF RECORD FIRED.
DELTA 4 (2026-10-10; docs/reviews/POSTRUN_HARNESS-EXTRACTOR.md 8012b48a, INVALID: the --run crashed at the MATH-FIX SELECT,
  "no such column: f.is_correct_mathfix"; the real table is eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct
  INTEGER, PRIMARY KEY (question_id, model_name)); READY delta3 LOW conditions L-H1 / L-H2; nothing else changed: rules,
  statistics, refusals' conditions, outputs' paths and the bootstrap are untouched):
  F-1 the MATH-FIX SELECT reads f.is_correct (the real column); the docstrings (LAUNCH step 1, DATA DB, SCORERS MATH MF) and the
      REFUSE.MF message name eval_results_mathfix.is_correct; KEY_SEAL drops the invented name (is_correct, already sealed,
      covers the corrected column; st_schema (e) shows the sealed tripwire refuses the corrected SELECT, X109 / X110).
      Every statement read_inputs executes now lives in RUN_SQL (one place), with the columns it reads declared in RUN_COLUMNS.
  F-2 the selftest fixture no longer writes its own CREATE TABLE text: _layout builds every table from the REAL DBs' DDL
      (_real_ddl: sqlite_master, read-only immutable; fail-closed when the DBs are absent) with named inserts (NOT NULL fillers);
      st_schema (a) asserts the built fixture's sqlite_master text and PRAGMA table_info equal the real DBs' for all 5 tables.
      Two declared fixture variants: "nopk" (the dup refusal only: the real PRIMARY KEY dropped, a row the real table cannot
      hold; the guard is defence in depth) and "schema_drift" (the invented column, for the S-1 refusal cases).
  S-1 schema_check runs in BOTH --dry-run and --run, after the H table and before the first row is read: G1 PRAGMA table_info
      presence of every RUN_COLUMNS entry (one printed line per column, cid and type); G2 every RUN_SQL statement compiled
      by EXPLAIN on its DB (no row read) with an authorizer recording its (table, column) reads; G3 the reads equal RUN_COLUMNS;
      then "SCHEMA CONFORMANCE (S-1): 15 columns in 4 tables named by 6 statements ...". Each gate REFUSES with its own message
      (branches REFUSE.SCHEMA.DECLARED / .COMPILE / .READS, SCHEMA.OK).
  L-H1 figure_payload "words": HX2 and HX3 are released as {"word": ..., "support": "descriptive-only by support"}; HX1 / HX4
      bare (scored). L-H2 the "RULE 8 (HX2, HX-R5)" line ends "... is not refuted (descriptive-only by support)".
  Selftest: st_schema (new; a-e as in its docstring, by value, incl. the real DBs' 15 reads against a hand-written oracle);
  st_dry_run asserts the 15 schema lines by value and their place before R1; run_e2e asserts the HX2 rule-8 line and the
  figure words of every fixture; st_verdicts the HX2 rule-8 line both ways. Mutants X99-X114 (X54 re-anchored on RUN_SQL).
NOT DONE HERE: the real --run (the operator's, after a delta READY); no Kotlin / Gradle; no judge call.
"""
import os
import sys


def _pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _pre_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import io            # noqa: E402
import re            # noqa: E402
import ast           # noqa: E402
import glob          # noqa: E402
import json          # noqa: E402
import math          # noqa: E402
import time          # noqa: E402
import types         # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import platform      # noqa: E402
import itertools     # noqa: E402
import contextlib    # noqa: E402
import subprocess    # noqa: E402
from collections import Counter, defaultdict   # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


MY_PINS = (("pool_guard.py", "6521b51ac0fce04063563f9e6dcf42554ad86591"),
           ("split_side.py", "05224b5a4b76e74353bc3931ec69f0b14f0e340b"),
           ("v2_reader_guards.py", "14d10ff8a4a03afd0e4edf4beae6281bd8c69982"),
           ("math_fix.py", "c44a2618d8ad07fff37b875ab81b8ecfbb94917f"),
           ("math_scorer_h.py", "3ab51e3fe5125722a75600fcfbf72a0a0ddcb67b"))
for _name, _pin in MY_PINS:
    if blob_lf(os.path.join(HERE, _name)) != _pin:
        raise SystemExit("[HX] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_name, blob_lf(os.path.join(HERE, _name)), _pin))
import pool_guard as PG          # noqa: E402
import v2_reader_guards as G     # noqa: E402
import math_fix as mf            # noqa: E402  (used by the copied categorise() through labelled / modes)
import math_scorer_h as MSH      # noqa: E402  (the pinned H implementation: h_score, region, labelled, modes, REF_FIX)
from split_side import stem_key  # noqa: E402

labelled, modes, h_score, region, REF_FIX = MSH.labelled, MSH.modes, MSH.h_score, MSH.region, MSH.REF_FIX
assert mf is MSH.mf

# ======================= COPY BEGIN (verbatim; E:/TaxoArena_tmp/math_audit/math_scorer_audit.py) =======================
MINERVA = re.compile(r"final answer is", re.I)

def categorise(resp, target, nt):
    L = labelled(resp)
    res = [(k, c, modes(c, target)) for k, c in L]
    matched = [(k, md) for k, c, md in res if md]
    stated = [(k, md) for k, c, md in res if k in ("boxed", "final")]
    stated_ok = [x for x in stated if x[1]]
    route = "+".join("%s:%s" % x for x in matched)
    if stated and not stated_ok: cat = "CONFLICT_stated_wrong_other_matched"
    elif not stated: cat = "LASTNUM_ONLY_no_stated_answer"
    elif all(md == "prefix" for k, md in stated_ok): cat = "PREFIX_partial_numeric"
    elif nt: cat = "NONTERM_stated_answer_matches"
    elif all(md == "num" for k, md in stated_ok): cat = "EQUIV_numeric_form"
    elif not MINERVA.search(resp or ""): cat = "BOXED_no_minerva_sentence"
    else: cat = "FORMAT_minerva_present_norm_mismatch"
    return cat, route, res
# ======================= COPY END ==========================================================================================
AUDIT_SRC = ("E:/TaxoArena_tmp/math_audit/math_scorer_audit.py", "b22251009ac14ab5")
COPIED = ("MINERVA", "categorise")

TAG = "[HX]"
TEST_ID = "HARNESS-EXTRACTOR"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — HARNESS-EXTRACTOR (amended; supersedes'
            ' the MMLU-Pro design before any build): re-scoring the cached raw MATH and IFEval outputs ..." (L25229-L25315 as of'
            ' 16ff6d0d; record L25221-L25227; D-2026-10-08-5 brackets L25317-L25327 as of bb5eb124)')
R1_POOL = "paeec37aa28063c75"
OUT_REL = "experiment_results/hf_blog/harness_extractor"
BLOG_DIR = "E:/TaxoArena_tmp/blog/harness"
BUSY_PS1 = "E:/TaxoArena_tmp/busy.ps1"
H_REL = "experiment_results/math_scorer_h/math_h_table.csv"
H_SHA = "6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1"
CK_REL = "experiment_results/multicorpus/checker_answers_v2.db"
RAW_REL = "experiment_results/multicorpus/raw"
MC_REL = "multicorpus_cache_v1.db"
EXCLUDED = "Meta-Llama-3-70B-Instruct"
MATH, IFEVAL = "MATH", "IFEVAL"
CORRUPT = (2000164, 2060002, 2060129)
CATS = ("CONFLICT_stated_wrong_other_matched", "LASTNUM_ONLY_no_stated_answer", "PREFIX_partial_numeric",
        "NONTERM_stated_answer_matches", "EQUIV_numeric_form", "BOXED_no_minerva_sentence", "FORMAT_minerva_present_norm_mismatch")
FORMAT = ("BOXED_no_minerva_sentence", "FORMAT_minerva_present_norm_mismatch", "EQUIV_numeric_form")
SM = ("X0", "MF", "H")
SI = ("I0", "IS", "IL")
KEY_SEAL = ("is_correct", "model_output", "non_terminated")
DESC_ONLY = "descriptive-only by support"         # DELTA 4, L-H1 / L-H2: the qualifier of HX2 / HX3 wherever their word is released
# DELTA 4 (POSTRUN F-1 / S-1): every statement read_inputs executes, in ONE place, as (DB label, SQL, dummy parameters for the
# compile-only check). "mc" = multicorpus_cache_v1.db, "ck" = checker_answers_v2.db. schema_check() compiles each one on the
# real DB (EXPLAIN; an authorizer records every table.column it reads; no row is read) and checks the reads against RUN_COLUMNS
# and PRAGMA table_info. The real eval_results_mathfix is (question_id INTEGER, model_name TEXT, is_correct INTEGER, PRIMARY KEY
# (question_id, model_name)) (sqlite_master, mode=ro&immutable=1, 2026-10-09).
RUN_SQL = {
    "q": ("mc", "SELECT question_id, source, upstream_id, text, target FROM corpus_questions", ()),
    "ev_dry": ("mc", "SELECT e.question_id, e.model_name FROM eval_results e JOIN corpus_questions c USING(question_id)"
                     " WHERE c.source IN (?, ?)", ("MATH", "IFEVAL")),
    "ev": ("mc", "SELECT e.question_id, e.model_name, e.model_output, e.is_correct FROM eval_results e"
                 " JOIN corpus_questions c USING(question_id) WHERE c.source IN (?, ?)", ("MATH", "IFEVAL")),
    "mf": ("mc", "SELECT f.question_id, f.model_name, f.is_correct FROM eval_results_mathfix f JOIN"
                 " corpus_questions c USING(question_id) WHERE c.source = ?", ("MATH",)),
    "ck_count": ("ck", "SELECT COUNT(*) FROM math_checker_answers_v2", ()),
    "ck": ("ck", "SELECT question_id, model_name, non_terminated FROM math_checker_answers_v2", ()),
}
RUN_COLUMNS = (("mc", "corpus_questions", "question_id"), ("mc", "corpus_questions", "source"),
               ("mc", "corpus_questions", "upstream_id"), ("mc", "corpus_questions", "text"), ("mc", "corpus_questions", "target"),
               ("mc", "eval_results", "question_id"), ("mc", "eval_results", "model_name"), ("mc", "eval_results", "model_output"),
               ("mc", "eval_results", "is_correct"),
               ("mc", "eval_results_mathfix", "question_id"), ("mc", "eval_results_mathfix", "model_name"),
               ("mc", "eval_results_mathfix", "is_correct"),
               ("ck", "math_checker_answers_v2", "question_id"), ("ck", "math_checker_answers_v2", "model_name"),
               ("ck", "math_checker_answers_v2", "non_terminated"))
REG = dict(r1_pool=R1_POOL, twins_ids=471, twins_texts=427, roster=18, math_q=1324, ifeval_q=541, h_rows=23832, B=2000,
           seed=20261008, seed_iid=20261009, tau_bar=0.85, shift_bar=2.0, hx4_bar=0.02, hx5_bar=0.50, sw_bar=0.80)
PRED = dict(P1=(("RANKS-MOVE", 0.97), ("RANKS-HOLD", 0.03)), P2=(-0.20, 0.70), P3=(10.0, 17.0),
            P4_tau=(0.86, 0.97), P4_shift=(2.0, 4.0), P4=(("RANKS-MOVE", 0.75), ("RANKS-HOLD", 0.25)),
            P5_tau=(0.75, 0.97), P5_shift=(1.0, 4.0), P5=(("RANKS-HOLD", 0.55), ("RANKS-MOVE", 0.45)),
            P6=(("SHIFT-MATERIAL", 0.95), ("SHIFT-SMALL", 0.05)), P6_n=(2, 4), P6_max=(0.07, 0.12),
            P7=(0.85, 0.93), P7w=(("FORMAT-DOMINATED", 0.97), ("MIXED", 0.03)), P8=(0.02, 0.10))
# Support (d)-(f) as RE-DERIVED by the registrar 2026-10-09 (S-1; prog L25412-L25418): SE(tau) = 0.03374 x sqrt(2,056 / n), floor
# 0.0337 (SATURATION-IRT's realised SD; it carries its own resampling structure, so (b)'s DEFF / (c)'s n_eff do not enter HX1-HX3).
# Row: (criterion, denominator, DEFF, n_eff, SE, MDE80 = 2.8 x SE, predicted point, bar, note); the plan word is COMPUTED by
# plan_word: SCOREABLE iff |predicted - bar| >= MDE80, else DESCRIPTIVE-ONLY (HX2 DESCRIPTIVE-ONLY BY SUPPORT, HX3 unchanged).
TAU_SD0, TAU_N0, TAU_FLOOR = 0.03374, 2056, 0.0337
_TAU_DEFF = "carried by the transported realised SD"
SUPPORT_PLAN = (("HX1", "about 1,324 MATH questions, 153 pairs", _TAU_DEFF, "not entering", 0.0420, 0.118, 0.35, 0.85,
                 "MDE80 0.094 at the floor; the shift clause is a count, 15 against 2"),
                ("HX2", "about 1,324 MATH questions", _TAU_DEFF, "not entering", 0.0420, 0.118, 0.92, 0.85,
                 "inside MDE80 0.094-0.118; the shift clause, 3 against 2, has no measured SE and a one-rank margin"),
                ("HX3", "541 IFEval prompts", _TAU_DEFF, "not entering", 0.0658, 0.184, 0.88, 0.85, "unchanged"),
                ("HX4", "1,324 paired questions per model", "1.2", "1,103 per model", 0.0095, 0.027, 0.099, 0.02, "unchanged"),
                ("HX5", "5,181 disagreement rows (pilot)", "3.0", "1,727", 0.0072, 0.020, 0.90, 0.50, "unchanged"))
HIT = Counter()
BRANCHES = ("HX1.HOLD", "HX1.MOVE", "HX1.STABLE", "HX1.FRAGILE", "R8.HX1.REFUTED", "R8.HX1.NOT",
            "HX2.HOLD", "HX2.MOVE", "HX3.HOLD", "HX3.MOVE", "HX4.MATERIAL", "HX4.SMALL", "R8.HX4.REFUTED", "R8.HX4.NOT",
            "HX5.FORMAT", "HX5.MIXED", "R8.HX5.REFUTED", "R8.HX5.NOT", "FHX.FIRED", "FHX.NOT", "FH.FIRED", "FH.NOT",
            "PRED.HELD", "PRED.FAILED", "SUPPORT.SCOREABLE", "SUPPORT.DESCRIPTIVE", "OUT.RECORD", "DRY.DONE",
            "REFUSE.BUSY", "REFUSE.TWINS", "REFUSE.ROSTER", "REFUSE.COUNTS", "REFUSE.DUP", "REFUSE.MF", "REFUSE.NT", "REFUSE.H",
            "REFUSE.RAW", "REFUSE.INCOMPLETE", "REFUSE.SHA", "REFUSE.WRITE_ONCE",
            "SCHEMA.OK", "REFUSE.SCHEMA.DECLARED", "REFUSE.SCHEMA.COMPILE", "REFUSE.SCHEMA.READS")


def hit(name):
    if name not in BRANCHES:
        raise SystemExit("%s undeclared branch %r" % (TAG, name))
    HIT[name] += 1


def refuse(msg, branch=None):
    if branch:
        hit(branch)
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def _f(x, fmt="%.4f"):
    return "nan" if x is None or (isinstance(x, float) and math.isnan(x)) else fmt % x


# ═══════════════════════════════════════════════════════════════════════════════ pure statistics
def midrank(acc):
    """Rank 1 = the highest accuracy; ties at mid-rank."""
    a = np.asarray(acc, dtype=np.float64)
    gt = (a[None, :] > a[:, None]).sum(1)
    eq = (a[None, :] == a[:, None]).sum(1)
    return 1.0 + gt + (eq - 1) / 2.0


def tau_b(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    iu = np.triu_indices(len(x), 1)
    sx = np.sign(x[:, None] - x[None, :])[iu]
    sy = np.sign(y[:, None] - y[None, :])[iu]
    den = math.sqrt(float((sx != 0).sum()) * float((sy != 0).sum()))
    return float((sx * sy).sum()) / den if den > 0 else float("nan")


def max_shift(x, y):
    return float(np.max(np.abs(midrank(x) - midrank(y))))


def set_word(acc, names, reg):
    """The HX1 rule over every pair of `names`: (word, min tau-b, max shift, [(a, b, tau, shift)], argmin pair)."""
    pairs = []
    for a, b in itertools.combinations(names, 2):
        pairs.append((a, b, tau_b(acc[a], acc[b]), max_shift(acc[a], acc[b])))
    mt = min((p[2] if not math.isnan(p[2]) else float("-inf")) for p in pairs)   # an undefined tau-b cannot hold
    ms = max(p[3] for p in pairs)
    hold = bool(round(mt, 12) >= reg["tau_bar"] and ms <= reg["shift_bar"])
    arg = min(pairs, key=lambda p: ((p[2] if not math.isnan(p[2]) else float("-inf")), p[0], p[1]))
    return dict(word="RANKS-HOLD" if hold else "RANKS-MOVE", min_tau=mt, max_shift=ms, pairs=pairs, argmin=(arg[0], arg[1]))


def accw(Y, w):
    return (Y * w[None, :]).sum(1) / w.sum()


def stats(D, wM, wI, reg):
    accM = {s: accw(D["M"][s], wM) for s in ("X0", "MF", "H", "HL")}
    accI = {s: accw(D["I"][s], wI) for s in SI}
    st = dict(accM=accM, accI=accI)
    st["hx1"] = set_word(accM, SM, reg)
    st["hx2"] = set_word(accM, ("MF", "H"), reg)
    st["hx3"] = set_word(accI, SI, reg)
    st["d_mf_h"] = accM["MF"] - accM["H"]
    st["d_x0_mf"] = accM["X0"] - accM["MF"]
    st["d_is_il"] = accI["IS"] - accI["IL"]
    num = wM @ D["catq"]
    tot = float(num.sum())
    st["shares"] = num / tot if tot > 0 else np.full(len(CATS), np.nan)
    st["format"] = float(sum(st["shares"][CATS.index(c)] for c in FORMAT)) if tot > 0 else float("nan")
    st["n_dis_w"] = tot
    return st


def hx5_word(fs, reg):
    return "FORMAT-DOMINATED" if bool(fs >= reg["hx5_bar"]) else "MIXED"


def hx4_word(lo, hi, reg):
    """-> (word, number of models whose 95% interval lies wholly beyond |bar|)."""
    n = int(sum(1 for a, b in zip(lo, hi) if bool(a > reg["hx4_bar"]) or bool(b < -reg["hx4_bar"])))
    return ("SHIFT-MATERIAL" if n >= 1 else "SHIFT-SMALL"), n


def rule8_hx1(hx, reg):
    """RANKS-MOVE is refuted iff every pair has tau-b >= 0.85 and the max rank shift is <= 2 (HX-R4: the exact complement)."""
    return bool(all(round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"]) and hx["max_shift"] <= reg["shift_bar"])


def plan_word(name, pred, bar, mde):
    """Support (f): SCOREABLE iff the predicted point clears the bar by at least MDE80; HX2 reads 'DESCRIPTIVE-ONLY (by support)'."""
    if bool(abs(pred - bar) >= mde):
        return "SCOREABLE"
    return "DESCRIPTIVE-ONLY (by support)" if name == "HX2" else "DESCRIPTIVE-ONLY"


def pctl(xs, q):
    return float(np.percentile(np.asarray(xs, dtype=np.float64), q))


def brier(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def in_band(x, band):
    return bool(band[0] <= x <= band[1])


def kish(cl):
    sz = np.bincount(cl)
    sz = sz[sz > 0]
    return float((sz * sz).sum() / sz.sum()) if sz.size else float("nan")


def boot(D, reg, B):
    """B component replicates (default_rng(seed); MATH components then IFEval components per replicate) and B i.i.d. replicates
    (default_rng(seed_iid); MATH questions, IFEval questions, then the X0-vs-MF disagreement rows per replicate)."""
    rng = np.random.default_rng(int(reg["seed"]))
    rng2 = np.random.default_rng(int(reg["seed_iid"]))
    cm, ci = D["clM"], D["clI"]
    CM, CI = int(cm.max()) + 1, int(ci.max()) + 1
    nM, nI = len(cm), len(ci)
    rows = D["dis_rows"]                       # [(question index, category index)] of the X0-vs-MF disagreements
    fmt_idx = set(CATS.index(c) for c in FORMAT)
    comp, iid, fmt_iid = [], [], []
    for _r in range(int(B)):
        wM = np.bincount(rng.integers(0, CM, CM), minlength=CM)[cm].astype(np.float64)
        wI = np.bincount(rng.integers(0, CI, CI), minlength=CI)[ci].astype(np.float64)
        comp.append(stats(D, wM, wI, reg))
        uM = np.bincount(rng2.integers(0, nM, nM), minlength=nM).astype(np.float64)
        uI = np.bincount(rng2.integers(0, nI, nI), minlength=nI).astype(np.float64)
        iid.append(stats(D, uM, uI, reg))
        if rows:
            k = np.bincount(rng2.integers(0, len(rows), len(rows)), minlength=len(rows))
            fmt_iid.append(float(sum(int(k[j]) for j, (_q, c) in enumerate(rows) if c in fmt_idx)) / len(rows))
    return comp, iid, fmt_iid


# ═══════════════════════════════════════════════════════════════════════════════ readers
class Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def real_cfg():
    dr = PG.DATA_ROOT
    return Cfg(reg=dict(REG), r1_db=None, r1_idfile=None, mc_db=os.path.join(dr, MC_REL), ck_db=os.path.join(dr, CK_REL),
               raw_dir=os.path.join(dr, RAW_REL), h_path=os.path.join(dr, H_REL), h_pin=H_SHA,
               out_dir=os.path.join(dr, OUT_REL), blog_dir=BLOG_DIR, busy=BUSY_PS1, audit_src=AUDIT_SRC)


# B2 / B-1 (delta 2026-10-09): busy.ps1's pattern lists this script's own name, so a plain call always saw the caller and
# refused. The check now runs the SAME busy.ps1, unmodified, inside a PowerShell session whose Get-CimInstance drops the
# caller's own PID and its parent chain (each ancestor older than its child; a reused PID ends the chain). Nothing else is
# dropped: java, peers and every other process still make busy.ps1 exit 0. Fail-closed: a throw, an absent exit code or a
# missing report is not 1, and REFUSES.
BUSY_WRAP = r"""$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
  $self = [int]__PID__
  $byId = @{}
  foreach ($q in @(CimCmdlets\Get-CimInstance Win32_Process)) { $byId[[int]$q.ProcessId] = $q }
  $ex = New-Object 'System.Collections.Generic.List[int]'
  $cur = $self
  while ($byId.ContainsKey($cur) -and -not $ex.Contains($cur)) {
    $ex.Add($cur)
    $pp = [int]$byId[$cur].ParentProcessId
    if (-not $byId.ContainsKey($pp)) { break }
    if ($byId[$pp].CreationDate -gt $byId[$cur].CreationDate) { break }
    $cur = $pp
  }
  $global:__bx = $ex
  $global:__br = New-Object 'System.Collections.Generic.List[object]'
  $global:__bn = 0
  function global:Get-CimInstance {
    $global:__bn++
    $r = @(CimCmdlets\Get-CimInstance @args | Where-Object { -not $global:__bx.Contains([int]$_.ProcessId) })
    foreach ($x in $r) { $global:__br.Add(@{pid = [int]$x.ProcessId; cmd = [string]$x.CommandLine}) }
    $r
  }
  $global:LASTEXITCODE = 99
  & '__PATH__'
  $rc = $LASTEXITCODE
  $jv = @(Get-Process java -ErrorAction SilentlyContinue).Count
  $o = @{rc = $rc; excluded = $ex.ToArray(); returned = $global:__br.ToArray(); calls = $global:__bn; java = $jv}
  Write-Output ('BUSYJSON ' + (ConvertTo-Json $o -Compress -Depth 4))
  exit $rc
} catch { Write-Output ('BUSYERR ' + $_); exit 3 }
"""


def busy_probe(path, pid):
    """Run busy.ps1 (unmodified) with `pid` and its parent chain hidden from its process scan -> (exit code, report or None)."""
    import base64
    ps = BUSY_WRAP.replace("__PID__", str(int(pid))).replace("__PATH__", str(path).replace("'", "''"))
    enc = base64.b64encode(ps.encode("utf-16-le")).decode("ascii")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", enc], capture_output=True,
                       timeout=120)
    info = None
    for ln in r.stdout.decode("utf-8", "replace").splitlines():
        if ln.startswith("BUSYJSON "):
            info = json.loads(ln[len("BUSYJSON "):])
    return r.returncode, info


def busy_check(path, pid=None):
    """Rule 7: busy.ps1 exit 1 = free (proceed), 0 = busy (REFUSE), anything else REFUSES. The caller's own process and its
    parent chain are excluded from busy.ps1's scan (B2 / B-1); the excluded PIDs are printed. Returns the line printed after POOL."""
    if not path or not os.path.isfile(path):
        refuse("rule 7: the busy check %r is absent" % path, "REFUSE.BUSY")
    rc, info = busy_probe(path, os.getpid() if pid is None else pid)
    if rc != 1:
        refuse("rule 7: %s exited %d (1 = free; 0 = a construction or a pool reader is running): WAIT, then re-launch"
               % (path, rc), "REFUSE.BUSY")
    if not info or info.get("rc") != 1:
        refuse("rule 7: %s exited 1 without the self-exclusion report" % path, "REFUSE.BUSY")
    return ("  rule 7: %s exit 1 (free), checked before any read; own process chain excluded: PIDs %s"
            % (path, ",".join(str(x) for x in info.get("excluded") or []) or "none"))


def load_h(path, pin, rows):
    """The pinned H table -> ({(question_id, model): (H, route)}, sha256). REFUSED unless present, LF, sha256 == pin, the
    header, 0 / 1 values, no repeat, `rows` rows."""
    if not os.path.isfile(path):
        refuse("the H table %s is absent (math_scorer_h.py --run writes it; use --data-root from a worktree)" % path, "REFUSE.H")
    raw = open(path, "rb").read()
    if b"\r" in raw:
        refuse("the H table %s carries CR bytes (the LF rendering is of record)" % path, "REFUSE.H")
    sha = hashlib.sha256(raw).hexdigest()
    if sha != pin:
        refuse("the H table %s is sha256-lf %s, not the pinned %s" % (path, sha, pin), "REFUSE.H")
    lines = raw.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if not lines or lines[0] != "question_id,model,H,route":
        refuse("the H table header is not question_id,model,H,route", "REFUSE.H")
    H = {}
    for ln in lines[1:]:
        parts = ln.split(",")
        if len(parts) != 4 or parts[2] not in ("0", "1") or not parts[0].isdigit():
            refuse("the H table row %r is malformed" % ln[:80], "REFUSE.H")
        q, m, h, rt = int(parts[0]), parts[1], int(parts[2]), parts[3]
        if (q, m) in H:
            refuse("the H table repeats (question_id %d, model %s)" % (q, m), "REFUSE.H")
        H[(q, m)] = (h, rt)
    if len(H) != int(rows):
        refuse("the H table holds %d rows, not %d" % (len(H), rows), "REFUSE.H")
    return H, sha


def r1_twins(text, eval_ids):
    """R1: the EVAL ids whose text is byte-equal to the text of any id outside the EVAL set -> (sorted ids, distinct texts)."""
    outside = {t for q, t in text.items() if q not in eval_ids}
    tw = sorted(q for q in eval_ids if q in text and text[q] in outside)
    return tw, len({text[q] for q in tw})


def collapse(text, ids):
    """Every group of byte-equal texts collapsed to its lowest question_id -> (kept, dropped)."""
    groups = defaultdict(list)
    for q in ids:
        groups[text[q]].append(q)
    keep, drop = [], []
    for g in groups.values():
        lo = min(g)
        keep.append(lo)
        drop.extend(q for q in g if q != lo)
    return sorted(keep), sorted(drop)


def raw_ifeval(raw_dir, models, say):
    """The official IFEval checker's own per-sample verdicts from the leaderboard harness's sample files -> {(model, doc_id):
    (prompt, response, IS, IL, inst strict list, inst loose list)}; exactly one file per model (name and sha256 printed)."""
    out = {}
    for m in models:
        fs = sorted(glob.glob(os.path.join(raw_dir, m, "*", "samples_leaderboard_ifeval_*.jsonl")))
        if len(fs) != 1:
            refuse("expected exactly one IFEval sample file for %s under %s, found %d" % (m, raw_dir, len(fs)), "REFUSE.RAW")
        say("  IFEval checker verdicts (HX-R1): %s | %s | sha256-bytes %s" % (m, os.path.basename(fs[0]), G.sha256_file(fs[0])))
        with open(fs[0], encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                resp = r["resps"][0][0] if r.get("resps") else None
                k = (m, int(r["doc_id"]))
                if k in out:
                    refuse("IFEval sample file of %s repeats doc_id %d" % k, "REFUSE.RAW")
                out[k] = (r["doc"]["prompt"], resp, int(bool(r["prompt_level_strict_acc"])), int(bool(r["prompt_level_loose_acc"])),
                          [bool(v) for v in r["inst_level_strict_acc"]], [bool(v) for v in r["inst_level_loose_acc"]])
    return out


def hl_extra(resp, target, qid):
    """H-L's addition: a row with an unclosed think block is credited iff h_score credits the text after its last <think>."""
    if not resp or "<think>" not in resp or "</think>" in resp:
        return 0
    return int(h_score(resp[resp.rfind("<think>") + len("<think>"):], target, 0, qid)[0])


def schema_check(dbs, sql=None, cols=None):
    """DELTA 4, S-1 (POSTRUN_HARNESS-EXTRACTOR): SCHEMA CONFORMANCE of every statement the --run / --dry-run execute, against
    the DBs actually configured (the real ones in real_cfg), opened through pool_guard.open_ro (mode=ro&immutable=1). Three
    gates, in this order, each REFUSING with its own message:
      G1 DECLARED  PRAGMA table_info: every RUN_COLUMNS entry is a column of its table (one printed line per column);
      G2 COMPILE   every RUN_SQL statement compiles on its DB (EXPLAIN: the VDBE program only, discarded unprinted; no row of
                   any table is read); an authorizer records each (table, column) the statement reads;
      G3 READS     the recorded reads (all statements) equal the declared RUN_COLUMNS set (so the declaration cannot drift from
                   the SQL that runs).
    No key value is read: the check names sealed columns only inside EXPLAIN / PRAGMA on a separate raw connection, never in a
    SELECT that returns rows. Returns the printed lines."""
    import sqlite3
    sql = RUN_SQL if sql is None else sql
    cols = RUN_COLUMNS if cols is None else cols
    L, info = [], {}
    for lab, tab, col in cols:
        if (lab, tab) not in info:
            c = PG.open_ro(dbs[lab])
            try:
                info[(lab, tab)] = {r[1]: (r[0], r[2]) for r in c.execute('PRAGMA table_info("%s")' % tab.replace('"', '""'))}
            finally:
                c.close()
        have = info[(lab, tab)]
        if col not in have:
            refuse("SCHEMA (S-1, G1 DECLARED): %s %s.%s is not a column of the real table (PRAGMA table_info: %s)" % (
                os.path.basename(dbs[lab]), tab, col, sorted(have) or "no such table"), "REFUSE.SCHEMA.DECLARED")
        L.append("  schema: %s %s.%s present (PRAGMA table_info cid %d, %s)" % (os.path.basename(dbs[lab]), tab, col, have[col][0],
                                                                               have[col][1] or "untyped"))
    reads = set()
    for name in sql:
        lab, q, params = sql[name]
        got = []

        def auth(action, a1, a2, _db, _src):
            if action == sqlite3.SQLITE_READ and a2:
                got.append((lab, a1, a2))
            return sqlite3.SQLITE_OK
        c = PG.open_ro(dbs[lab])
        try:
            c.set_authorizer(auth)
            try:
                c.execute("EXPLAIN " + q, params).fetchall()
            except sqlite3.Error as e:
                refuse("SCHEMA (S-1, G2 COMPILE): statement %r does not compile on %s: %s" % (name, os.path.basename(dbs[lab]), e),
                       "REFUSE.SCHEMA.COMPILE")
        finally:
            c.close()
        reads.update(got)
    if reads != set(cols):
        refuse("SCHEMA (S-1, G3 READS): the statements read %s but RUN_COLUMNS declares %s" % (
            sorted(reads - set(cols)) or "nothing more", sorted(set(cols) - reads) or "nothing more"), "REFUSE.SCHEMA.READS")
    hit("SCHEMA.OK")
    L.append("SCHEMA CONFORMANCE (S-1): %d columns in %d tables named by %d statements (--run and --dry-run) checked against %s"
             " (mode=ro&immutable=1; PRAGMA table_info; each statement compiled by EXPLAIN, no row read): all present; the declared"
             " set equals the statements' reads" % (len(set(cols)), len({(a, t) for a, t, _c in cols}), len(sql),
                                                   " and ".join(sorted({dbs[a] for a, _t, _c in cols}))))
    return L


def read_inputs(cfg, say, full, pre=()):
    reg = cfg.reg
    pid = PG.assert_pool_of_record(reg["r1_pool"], db=cfg.r1_db, id_file=cfg.r1_idfile)
    say("POOL %s verified (pool_guard.assert_pool_of_record: id file and reserved_pool rows hash to it); R1's object. No split word"
        " is claimed (S3): a scorer comparison over all cached MATH and IFEval rows. Relative to these 18 models (R6)." % pid)
    for ln in pre:
        say(ln)
    say(G.identity_line(os.path.abspath(__file__), "harness_extractor.py"))
    say("pins: " + ", ".join("%s blob:%s" % (n, p[:8]) for n, p in MY_PINS))
    say("registration: %s" % REG_TEXT)
    say("python %s | numpy %s | %s | threads %s" % (platform.python_version(), np.__version__, platform.platform(),
                                                    ", ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS)))
    H, hsha = load_h(cfg.h_path, cfg.h_pin, reg["h_rows"])
    say("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf %s); MATH-FIX beside: yes"
        " (D-2026-10-08-5; this test compares X0 / MF / H as its own question)" % hsha)
    say("  H table %s: sha256-lf %s = the pin; %d rows. Corrected references inside H only (math_scorer_h.REF_FIX, from the"
        " dataset's full solutions, prog L25321): %s" % (cfg.h_path, hsha, len(H), json.dumps({str(k): v for k, v in sorted(REF_FIX.items())})))
    idfile = cfg.r1_idfile or PG.id_file_path(reg["r1_pool"])
    with open(idfile, "r", encoding="utf-8") as f:
        eval_ids = frozenset(q for v in PG.judgeable(json.load(f)).values() for q in v)
    for ln in schema_check({"mc": cfg.mc_db, "ck": cfg.ck_db}):
        say(ln)
    mc_before = G.sha256_file(cfg.mc_db)
    conn = G.KeyTripwire(PG.open_ro(cfg.mc_db), (), key=KEY_SEAL, label="multicorpus")
    try:
        rows = conn.execute(RUN_SQL["q"][1]).fetchall()
        text = {int(q): t for q, _s, _u, t, _g in rows}
        src = {int(q): s for q, s, _u, _t, _g in rows}
        up = {int(q): int(u) for q, _s, u, _t, _g in rows}
        tgt = {int(q): g for q, s, _u, _t, g in rows if s in (MATH, IFEVAL)}
        say("  %s sha256-bytes BEFORE %s; corpus_questions %d rows; pool EVAL ids %d" % (os.path.basename(cfg.mc_db), mc_before,
                                                                                      len(rows), len(eval_ids)))
        tw, tw_texts = r1_twins(text, eval_ids)
        by = Counter(src[q] for q in tw)
        srcs = sorted(set(src.values()))
        say("R1: %d EVAL ids / %d distinct texts have a byte-equal text outside the EVAL set (registered %d / %d): %s" % (
            len(tw), tw_texts, reg["twins_ids"], reg["twins_texts"], ", ".join("%s %d" % (s, by.get(s, 0)) for s in srcs)))
        if len(tw) != reg["twins_ids"] or tw_texts != reg["twins_texts"]:
            refuse("R1 twins %d / %d != the registered %d / %d" % (len(tw), tw_texts, reg["twins_ids"], reg["twins_texts"]), "REFUSE.TWINS")
        tws = set(tw)
        keep, drop = collapse(text, [q for q in sorted(text) if q not in tws])
        byd = Counter(src[q] for q in drop)
        kept = {s: [q for q in keep if src[q] == s] for s in (MATH, IFEVAL)}
        alls = {s: sorted(q for q in text if src[q] == s) for s in (MATH, IFEVAL)}
        say("R1: remaining byte-equal duplicates collapsed to the lowest id: %d dropped (%s); kept MATH %d of %d, IFEVAL %d of %d" % (
            len(drop), ", ".join("%s %d" % (s, byd.get(s, 0)) for s in srcs), len(kept[MATH]), len(alls[MATH]), len(kept[IFEVAL]),
            len(alls[IFEVAL])))
        qs = alls[MATH] + alls[IFEVAL]
        cnt = Counter()
        models_by = defaultdict(set)
        nexcl = 0
        if not full:
            for q, m in conn.execute(RUN_SQL["ev_dry"][1], (MATH, IFEVAL)):
                if m == EXCLUDED:
                    nexcl += 1
                    continue
                cnt[(src[int(q)], m)] += 1
                models_by[src[int(q)]].add(m)
            ev = None
        else:
            conn.unseal("HARNESS-EXTRACTOR --run: the scorer columns of every cached MATH / IFEval row")
            ev = {}
            for q, m, out, c in conn.execute(RUN_SQL["ev"][1], (MATH, IFEVAL)):
                q = int(q)
                if m == EXCLUDED:
                    nexcl += 1
                    continue
                if (q, m) in ev:
                    refuse("(question_id %d, model %s) carries more than one eval_results row" % (q, m), "REFUSE.DUP")
                if c not in (0, 1):
                    refuse("is_correct %r outside {0, 1} at (%d, %s)" % (c, q, m), "REFUSE.DUP")
                ev[(q, m)] = (out, int(c))
                cnt[(src[q], m)] += 1
                models_by[src[q]].add(m)
        models = sorted(models_by[MATH])
        say("  roster: MATH %d models, IFEVAL %d models (registered %d; the same set: %s); %s rows counted and excluded: %d" % (
            len(models), len(models_by[IFEVAL]), reg["roster"], models_by[MATH] == models_by[IFEVAL], EXCLUDED, nexcl))
        if len(models) != reg["roster"] or models_by[MATH] != models_by[IFEVAL]:
            refuse("roster check failed (MATH %d, IFEVAL %d models; same set %s)" % (len(models), len(models_by[IFEVAL]),
                                                                                   models_by[MATH] == models_by[IFEVAL]), "REFUSE.ROSTER")
        say("  roster: " + ", ".join(models))
        bad = {(s, m): cnt[(s, m)] for s in (MATH, IFEVAL) for m in models
               if cnt[(s, m)] != reg["math_q" if s == MATH else "ifeval_q"]}
        say("  rows per model: MATH %s, IFEVAL %s (registered %d / %d)" % (sorted(set(cnt[(MATH, m)] for m in models)),
                                                                         sorted(set(cnt[(IFEVAL, m)] for m in models)), reg["math_q"], reg["ifeval_q"]))
        if bad:
            refuse("rows per model differ from %d / %d: %s" % (reg["math_q"], reg["ifeval_q"], dict(list(bad.items())[:4])), "REFUSE.COUNTS")
        if full:
            mfv = {}
            for q, m, v in conn.execute(RUN_SQL["mf"][1], (MATH,)):
                if m != EXCLUDED:
                    mfv[(int(q), m)] = v
    finally:
        conn.close()
    hook = getattr(cfg, "during_read", None)           # SELFTEST-ONLY (None in real_cfg): a write during the read window
    if hook:
        hook()
    # checker_answers_v2 (HX-R2) and the raw IFEval sample files (HX-R1)
    ck = G.KeyTripwire(PG.open_ro(cfg.ck_db), (), key=KEY_SEAL, label="checker_answers_v2")
    try:
        if not full:
            n_ck = ck.execute(RUN_SQL["ck_count"][1]).fetchone()[0]
            say("  %s math_checker_answers_v2 rows %d (HX-R2: the categorise() nt flag; the column NOT read)" % (cfg.ck_db, n_ck))
            ntv = None
        else:
            ck.unseal("HARNESS-EXTRACTOR --run: the categorise() nt flag (HX-R2)")
            ntv = {(int(q), m): int(n or 0) for q, m, n in ck.execute(RUN_SQL["ck"][1])}
    finally:
        ck.close()
    rawv = raw_ifeval(cfg.raw_dir, models, say)
    mc_after = G.sha256_file(cfg.mc_db)
    say("  %s sha256-bytes AFTER %s (%s)" % (os.path.basename(cfg.mc_db), mc_after, "EQUAL to before" if mc_after == mc_before else "DIFFERS"))
    if mc_after != mc_before:
        refuse("the multicorpus DB changed during the read", "REFUSE.SHA")
    clM = [stem_key(text[q]) for q in kept[MATH]]
    clI = [stem_key(text[q]) for q in kept[IFEVAL]]
    data = dict(models=models, kept=kept, text=text, src=src)
    if not full:
        for s, cl in ((MATH, clM), (IFEVAL, clI)):
            u = {k: i for i, k in enumerate(sorted(set(cl)))}
            say("  %-7s kept %5d | components %5d | Kish %.4f" % (s, len(cl), len(u), kish(np.array([u[k] for k in cl]))))
        return data
    # ── the scorer matrices (kept questions x 18 models) ──
    M_, nM, nI = len(models), len(kept[MATH]), len(kept[IFEVAL])
    Ys = {s: np.zeros((M_, nM), dtype=np.int8) for s in ("X0", "MF", "H", "HL")}
    Is = {s: np.zeros((M_, nI), dtype=np.int8) for s in SI}
    inst = {s: [0, 0] for s in ("strict", "loose")}
    inst_m = {(m, s): [0, 0] for m in models for s in ("strict", "loose")}
    catq = np.zeros((nM, len(CATS)), dtype=np.float64)
    dis_rows, mfh_cats, nrow = [], Counter(), Counter()
    h_mismatch, h_route_bad, x0_1_mf_0, i0_ne_is = [], [], 0, 0
    for j, q in enumerate(kept[MATH]):
        for i, m in enumerate(models):
            if (q, m) not in ev:
                refuse("MATH question %d lacks model %s's row" % (q, m), "REFUSE.INCOMPLETE")
            out, x0 = ev[(q, m)]
            if (q, m) not in mfv or mfv[(q, m)] not in (0, 1):
                refuse("MATH (question_id %d, model %s): eval_results_mathfix.is_correct is %r" % (q, m, mfv.get((q, m))), "REFUSE.MF")
            if (q, m) not in ntv:
                refuse("MATH (question_id %d, model %s) has no checker_answers_v2 row (the nt flag, HX-R2)" % (q, m), "REFUSE.NT")
            if (q, m) not in H:
                refuse("MATH (question_id %d, model %s) is not in the H table" % (q, m), "REFUSE.H")
            h, route = H[(q, m)]
            if (route == "imported") != (x0 == 1):
                h_route_bad.append((q, m))
            hs = h_score(out, tgt[q], x0, q)[0]
            if hs != h:
                h_mismatch.append((q, m))
            mfx = int(mfv[(q, m)])
            Ys["X0"][i, j], Ys["MF"][i, j], Ys["H"][i, j] = x0, mfx, h
            Ys["HL"][i, j] = max(h, hl_extra(out, tgt[q], q))
            x0_1_mf_0 += int(x0 == 1 and mfx == 0)
            if x0 != mfx:
                c = CATS.index(categorise(out, tgt[q], ntv[(q, m)])[0])
                catq[j, c] += 1
                dis_rows.append((j, c))
            if mfx != h:
                mfh_cats[(categorise(out, tgt[q], ntv[(q, m)])[0], "MF1-H0" if mfx else "MF0-H1")] += 1
            nrow[MATH] += 1
    if h_route_bad or h_mismatch:
        refuse("the H table disagrees with this database state: %d rows whose route contradicts X0 (first %s), %d rows whose H !="
               " the pinned h_score (first %s)" % (len(h_route_bad), h_route_bad[:3], len(h_mismatch), h_mismatch[:3]), "REFUSE.H")
    for j, q in enumerate(kept[IFEVAL]):
        for i, m in enumerate(models):
            if (q, m) not in ev:
                refuse("IFEval question %d lacks model %s's row" % (q, m), "REFUSE.INCOMPLETE")
            out, i0 = ev[(q, m)]
            r = rawv.get((m, up[q]))
            if r is None:
                refuse("IFEval (question_id %d, upstream %d, model %s) has no row in the sample file" % (q, up[q], m), "REFUSE.RAW")
            prompt, rresp, isv, ilv, vs, vl = r
            if prompt != text[q] or rresp != out:
                refuse("IFEval (question_id %d, model %s): the sample file's prompt / response differ from the DB's (a join defect)"
                       % (q, m), "REFUSE.RAW")
            Is["I0"][i, j], Is["IS"][i, j], Is["IL"][i, j] = i0, isv, ilv
            i0_ne_is += int(i0 != isv)
            for s, v in (("strict", vs), ("loose", vl)):
                inst[s][0] += sum(v)
                inst[s][1] += len(v)
                inst_m[(m, s)][0] += sum(v)
                inst_m[(m, s)][1] += len(v)
            nrow[IFEVAL] += 1
    uM = {k: i for i, k in enumerate(sorted(set(clM)))}
    uI = {k: i for i, k in enumerate(sorted(set(clI)))}
    data.update(M=Ys, I=Is, catq=catq, dis_rows=dis_rows, mfh_cats=mfh_cats, clM=np.array([uM[k] for k in clM], dtype=np.int64),
                clI=np.array([uI[k] for k in clI], dtype=np.int64), inst=inst, inst_m=inst_m, x0_1_mf_0=x0_1_mf_0, i0_ne_is=i0_ne_is,
                corrupt=np.array([q in CORRUPT for q in kept[MATH]], dtype=bool), nrow=nrow)
    say("  scored: MATH %d rows (%d questions x %d models), IFEVAL %d rows (%d x %d); the H table agrees with this database"
        " state (route 'imported' iff X0 = 1 on every row; H == the pinned h_score on every row)" % (nrow[MATH], nM, M_, nrow[IFEVAL], nI, M_))
    for s, cl in ((MATH, data["clM"]), (IFEVAL, data["clI"])):
        say("  %-7s kept %5d | components %5d | Kish %.4f" % (s, len(cl), int(cl.max()) + 1, kish(cl)))
    return data


# ═══════════════════════════════════════════════════════════════════════════════ the analysis and the printed lines
def analyse(data, reg):
    nM, nI = len(data["kept"][MATH]), len(data["kept"][IFEVAL])
    st = stats(data, np.ones(nM), np.ones(nI), reg)
    comp, iid, fmt_iid = boot(data, reg, reg["B"])
    st["B"] = len(comp)
    st["comp"], st["iid"], st["fmt_iid"] = comp, iid, fmt_iid
    for k in ("hx1", "hx2", "hx3"):
        st[k]["sw"] = float(np.mean([r[k]["word"] == st[k]["word"] for r in comp]))
    fm = [r["format"] for r in comp if not math.isnan(r["format"])]
    st["hx5_dropped"] = len(comp) - len(fm)
    st["hx5_sw"] = float(np.mean([hx5_word(x, reg) == hx5_word(st["format"], reg) for x in fm])) if fm else float("nan")
    st["fmt_lo"], st["fmt_hi"] = (pctl(fm, 2.5), pctl(fm, 97.5)) if fm else (float("nan"), float("nan"))
    st["fmt_sd"] = float(np.std(fm, ddof=1)) if len(fm) > 1 else float("nan")
    sh = np.array([r["shares"] for r in comp if r["n_dis_w"] > 0])
    st["sh_lo"] = np.percentile(sh, 2.5, axis=0) if len(sh) else np.full(len(CATS), np.nan)
    st["sh_hi"] = np.percentile(sh, 97.5, axis=0) if len(sh) else np.full(len(CATS), np.nan)
    for key in ("d_mf_h", "d_x0_mf", "d_is_il"):
        arr = np.array([r[key] for r in comp])
        st[key + "_lo"] = np.percentile(arr, 2.5, axis=0)
        st[key + "_hi"] = np.percentile(arr, 97.5, axis=0)
        st[key + "_sd"] = np.std(arr, axis=0, ddof=1)
        st[key + "_sd_iid"] = np.std(np.array([r[key] for r in iid]), axis=0, ddof=1)
    st["hx4"], st["hx4_n"] = hx4_word(st["d_mf_h_lo"], st["d_mf_h_hi"], reg)
    for k in ("hx1", "hx2", "hx3"):
        st[k]["sd"] = float(np.std([r[k]["min_tau"] for r in comp], ddof=1))
        st[k]["sd_iid"] = float(np.std([r[k]["min_tau"] for r in iid], ddof=1))
        st[k]["lo"] = pctl([r[k]["min_tau"] for r in comp], 2.5)
        st[k]["hi"] = pctl([r[k]["min_tau"] for r in comp], 97.5)
    st["fmt_sd_iid"] = float(np.std(fmt_iid, ddof=1)) if len(fmt_iid) > 1 else float("nan")
    # sensitivity (point; decides nothing): without the 3 corrupted-reference questions; H-L for H
    w_ex = np.ones(nM)
    w_ex[data["corrupt"]] = 0.0
    se = stats(data, w_ex, np.ones(nI), reg)
    st["sens_ex"] = (se["hx1"], se["hx2"], int(data["corrupt"].sum()))
    accL = dict(st["accM"], H=st["accM"]["HL"])
    st["sens_hl"] = (set_word(accL, SM, reg), set_word(accL, ("MF", "H"), reg))
    return st


def _pairs_text(hx):
    return "; ".join("%s-%s tau-b %s, max shift %s" % (a, b, _f(t), _f(s, "%.1f")) for a, b, t, s in hx["pairs"])


def verdict_lines(st, reg):
    L, w = [], {}
    h1 = st["hx1"]
    w["HX1"] = h1["word"]
    hit("HX1.HOLD" if h1["word"] == "RANKS-HOLD" else "HX1.MOVE")
    stable = bool(h1["sw"] >= reg["sw_bar"])
    hit("HX1.STABLE" if stable else "HX1.FRAGILE")
    L.append("HX1 (DECIDING; MATH; {X0, MF, H}; the POINT decides): min pairwise tau-b %s (pair %s-%s), max rank shift %s | %s" % (
        _f(h1["min_tau"]), h1["argmin"][0], h1["argmin"][1], _f(h1["max_shift"], "%.1f"), _pairs_text(h1)))
    L.append("  HX1 -> %s (%s; S_w %s over B %d) [min tau-b 95%% %s, %s, bootstrap SD %s; decides nothing]" % (
        h1["word"], "stable" if stable else "fragile", _f(h1["sw"]), st["B"], _f(h1["lo"]), _f(h1["hi"]), _f(h1["sd"])))
    r8 = rule8_hx1(h1, reg)
    if r8:
        hit("R8.HX1.REFUTED")
        L.append("RULE 8 (HX1): RANKS-MOVE is REFUTED (every pair tau-b >= %.2f and no model moves more than %.0f ranks)" % (reg["tau_bar"], reg["shift_bar"]))
    else:
        hit("R8.HX1.NOT")
        L.append("RULE 8 (HX1): RANKS-MOVE is not refuted (a pair below tau-b %.2f or a model moving more than %.0f ranks)" % (reg["tau_bar"], reg["shift_bar"]))
    if h1["word"] == "RANKS-HOLD":
        hit("FHX.FIRED")
        L.append("FALSIFIER F-HX: FIRED (HX1 reads RANKS-HOLD): the pilot's rank preview is overturned; the post-run review checks the"
                 " instrument and the join first")
    else:
        hit("FHX.NOT")
        L.append("FALSIFIER F-HX: NOT FIRED (HX1 reads RANKS-MOVE)")
    h2 = st["hx2"]
    w["HX2"] = h2["word"]
    hit("HX2.HOLD" if h2["word"] == "RANKS-HOLD" else "HX2.MOVE")
    L.append("HX2 (MATH; {MF, H}; the POINT decides): tau-b %s, max rank shift %s -> %s (descriptive-only by support) (S_w %s)"
             " [tau-b 95%% %s, %s]" % (
        _f(h2["min_tau"]), _f(h2["max_shift"], "%.1f"), h2["word"], _f(h2["sw"]), _f(h2["lo"]), _f(h2["hi"])))
    other = "RANKS-MOVE" if h2["word"] == "RANKS-HOLD" else "RANKS-HOLD"
    L.append("  RULE 8 (HX2, HX-R5): %s would be refuted by %s's observable; observed tau-b %s, max shift %s: %s is not refuted"
             " (descriptive-only by support)" % (h2["word"], other, _f(h2["min_tau"]), _f(h2["max_shift"], "%.1f"), h2["word"]))
    if h2["word"] == "RANKS-HOLD":
        hit("FH.FIRED")
        L.append("FALSIFIER F-H (descriptive-only by support; decides nothing): FIRED (HX2 reads RANKS-HOLD; the audit's 'R1 distills"
                 " drop 3 ranks' preview, not scored)")
    else:
        hit("FH.NOT")
        L.append("FALSIFIER F-H (descriptive-only by support; decides nothing): NOT FIRED (HX2 reads RANKS-MOVE)")
    fired = bool(h1["word"] == "RANKS-HOLD")              # ruling F-H-SUPPORT: F-HX alone; F-H takes no part
    L.append("FALSIFIER OF RECORD: F-HX %s (F-H takes no part; ruling F-H-SUPPORT)" % ("FIRED" if fired else "NOT FIRED"))
    h3 = st["hx3"]
    w["HX3"] = h3["word"]
    hit("HX3.HOLD" if h3["word"] == "RANKS-HOLD" else "HX3.MOVE")
    L.append("HX3 (IFEval; {I0, IS, IL}; the POINT decides): min pairwise tau-b %s (pair %s-%s), max rank shift %s | %s" % (
        _f(h3["min_tau"]), h3["argmin"][0], h3["argmin"][1], _f(h3["max_shift"], "%.1f"), _pairs_text(h3)))
    L.append("  HX3 -> %s (descriptive-only by support) (S_w %s)" % (h3["word"], _f(h3["sw"])))
    w["HX4"] = st["hx4"]
    hit("HX4.MATERIAL" if st["hx4"] == "SHIFT-MATERIAL" else "HX4.SMALL")
    L.append("HX4 (MATH; acc_MF - acc_H per model; the 95%% INTERVAL decides): models whose interval lies wholly beyond |%.2f|: %d"
             " -> %s" % (reg["hx4_bar"], st["hx4_n"], st["hx4"]))
    if st["hx4_n"] == 0:
        hit("R8.HX4.REFUTED")
        L.append("RULE 8 (HX4): SHIFT-MATERIAL is REFUTED (no model's 95%% bound clears %.2f)" % reg["hx4_bar"])
    else:
        hit("R8.HX4.NOT")
        L.append("RULE 8 (HX4): SHIFT-MATERIAL is not refuted (%d model(s) clear %.2f)" % (st["hx4_n"], reg["hx4_bar"]))
    w["HX5"] = hx5_word(st["format"], reg)
    hit("HX5.FORMAT" if w["HX5"] == "FORMAT-DOMINATED" else "HX5.MIXED")
    L.append("HX5 (MATH; X0-vs-MF disagreements after R1; the POINT decides): format share (%s) %s [95%% %s, %s] of %d rows -> %s"
             " (S_w %s)" % (" + ".join(FORMAT), _f(st["format"]), _f(st["fmt_lo"]), _f(st["fmt_hi"]), int(st["n_dis_w"]), w["HX5"],
                            _f(st["hx5_sw"])))
    if bool(st["format"] < reg["hx5_bar"]):
        hit("R8.HX5.REFUTED")
        L.append("RULE 8 (HX5): FORMAT-DOMINATED is REFUTED (format share %s < %.2f)" % (_f(st["format"]), reg["hx5_bar"]))
    else:
        hit("R8.HX5.NOT")
        L.append("RULE 8 (HX5): FORMAT-DOMINATED is not refuted (format share %s >= %.2f)" % (_f(st["format"]), reg["hx5_bar"]))
    return L, w


def pred_lines(st, w, reg):
    L = []

    def band(name, x, b, fmt="%.4f"):
        ok = in_band(x, b)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        return "%s %s in [%s, %s]: %s" % (name, _f(x, fmt), _f(b[0], fmt), _f(b[1], fmt), "HELD" if ok else "FAILED")
    h1, h2, h3 = st["hx1"], st["hx2"], st["hx3"]
    L.append("PREDICTION P1 (HX1): word %s, Brier %.4f (RANKS-MOVE 0.97)" % (w["HX1"], brier(PRED["P1"], w["HX1"])))
    L.append("PREDICTION P2 (HX1): " + band("min pairwise tau-b (pair %s-%s)" % h1["argmin"], h1["min_tau"], PRED["P2"]))
    L.append("PREDICTION P3 (HX1): " + band("max rank shift", h1["max_shift"], PRED["P3"], "%.1f"))
    L.append("PREDICTION P4 (HX2): " + band("tau-b", h2["min_tau"], PRED["P4_tau"]) + "; " + band("max rank shift", h2["max_shift"],
                                                                                                  PRED["P4_shift"], "%.1f")
             + "; word %s, Brier %.4f (RANKS-MOVE 0.75)" % (w["HX2"], brier(PRED["P4"], w["HX2"])))
    L.append("PREDICTION P5 (HX3): " + band("min tau-b", h3["min_tau"], PRED["P5_tau"]) + "; " + band("max rank shift", h3["max_shift"],
                                                                                                      PRED["P5_shift"], "%.1f")
             + "; word %s, Brier %.4f (RANKS-HOLD 0.55)" % (w["HX3"], brier(PRED["P5"], w["HX3"])))
    mx = float(np.max(np.abs(st["d_mf_h"])))
    L.append("PREDICTION P6 (HX4): word %s, Brier %.4f (SHIFT-MATERIAL 0.95); " % (w["HX4"], brier(PRED["P6"], w["HX4"]))
             + band("models clearing 0.02", float(st["hx4_n"]), PRED["P6_n"], "%.0f") + "; " + band("max |acc_MF - acc_H|", mx, PRED["P6_max"]))
    L.append("PREDICTION P7 (HX5): " + band("format share", st["format"], PRED["P7"]) + "; word %s, Brier %.4f (FORMAT-DOMINATED 0.97)" % (
        w["HX5"], brier(PRED["P7w"], w["HX5"])))
    L.append("PREDICTION P8 (IFEval): " + band("max |acc_IS - acc_IL| over models", float(np.max(np.abs(st["d_is_il"]))), PRED["P8"]))
    return L


def support_lines(st, data, reg):
    nM, nI = len(data["kept"][MATH]), len(data["kept"][IFEVAL])
    L = ["SUPPORT (measured beside the registered plan; the bootstrap SD is of record):"]
    L.append("  denominators: MATH %d questions (%d components, Kish %.4f) x %d models; IFEval %d prompts (%d components, Kish %.4f);"
             " %d ranked models, %d pairs; HX5 %d X0-vs-MF disagreement rows on %d questions (%.2f rows per affected question)" % (
                 nM, int(data["clM"].max()) + 1, kish(data["clM"]), len(data["models"]), nI, int(data["clI"].max()) + 1, kish(data["clI"]),
                 len(data["models"]), len(data["models"]) * (len(data["models"]) - 1) // 2, len(data["dis_rows"]),
                 int((data["catq"].sum(1) > 0).sum()), len(data["dis_rows"]) / max(1, int((data["catq"].sum(1) > 0).sum()))))

    def one(name, pt, bar, sd, sd_iid, n):
        deff = (sd * sd) / (sd_iid * sd_iid) if sd_iid and sd_iid > 0 else float("nan")
        mde = 2.8 * sd
        sc = bool(abs(pt - bar) >= mde)
        hit("SUPPORT.SCOREABLE" if sc else "SUPPORT.DESCRIPTIVE")
        return ("  %s: point %s vs bar %s; bootstrap SD %s; DEFF %s (component / i.i.d. bootstrap variance); n_eff = %d / %s = %s;"
                " MDE80 = 2.8 x SD = %s; |point - bar| %s -> %s at the realised SE" % (
                    name, _f(pt), _f(bar), _f(sd), _f(deff), n, _f(deff), _f(n / deff if deff == deff and deff > 0 else float("nan"), "%.0f"),
                    _f(mde), _f(abs(pt - bar)), "SCOREABLE" if sc else "DESCRIPTIVE-ONLY"))
    L.append(one("HX1 min tau-b", st["hx1"]["min_tau"], reg["tau_bar"], st["hx1"]["sd"], st["hx1"]["sd_iid"], nM))
    L.append(one("HX2 tau-b", st["hx2"]["min_tau"], reg["tau_bar"], st["hx2"]["sd"], st["hx2"]["sd_iid"], nM))
    L.append(one("HX3 min tau-b", st["hx3"]["min_tau"], reg["tau_bar"], st["hx3"]["sd"], st["hx3"]["sd_iid"], nI))
    j = int(np.argmax(np.abs(st["d_mf_h"])))
    L.append(one("HX4 acc_MF - acc_H of %s (the largest |shift|)" % data["models"][j], abs(float(st["d_mf_h"][j])), reg["hx4_bar"],
                 float(st["d_mf_h_sd"][j]), float(st["d_mf_h_sd_iid"][j]), nM))
    L.append(one("HX5 format share", st["format"], reg["hx5_bar"], st["fmt_sd"], st["fmt_sd_iid"], len(data["dis_rows"])))
    L.append("  registered plan (Support (a)-(f); (d)-(f) as re-derived by the registrar 2026-10-09, S-1):")
    L.append("    SE(tau) for HX1-HX3 = %.5f x sqrt(%d / n), floor %.4f (SATURATION-IRT's realised SD; TRANSPORT ASSUMPTION: probably an"
             " over-statement, the scorers compare on the SAME items; the run's bootstrap SD is of record)" % (TAU_SD0, TAU_N0, TAU_FLOOR))
    for nm, den, deff, neff, se, mde, pred, bar, note in SUPPORT_PLAN:
        L.append("    %s: %s; DEFF %s; n_eff %s; SE %.4f; MDE80 %.3f; predicted %s vs bar %s (margin %s; %s): %s" % (
            nm, den, deff, neff, se, mde, _f(pred, "%g"), _f(bar, "%g"), _f(abs(pred - bar), "%.3f"), note, plan_word(nm, pred, bar, mde)))
    L.append("    F-H (fires iff HX2 reads RANKS-HOLD): descriptive-only by support, decides nothing; F-HX is the falsifier of record"
             " (ruling F-H-SUPPORT)")
    L.append("  not applicable: wrong(established) and tie conventions A / B (no judge verdict enters; scorers only)")
    return L


def descriptive_lines(st, data, reg):
    models = data["models"]
    L = ["DESCRIPTIVE (decides nothing):"]
    rk = {s: midrank(st["accM"][s]) for s in ("X0", "MF", "H", "HL")}
    L.append("  MATH accuracy (rank, mid-rank ties) per model: X0 | MF | H | H-L | acc_X0 - acc_MF [95%] | acc_MF - acc_H [95%]")
    for i, m in enumerate(models):
        L.append("    %-34s %.4f (%4.1f) | %.4f (%4.1f) | %.4f (%4.1f) | %.4f (%4.1f) | %+.4f [%+.4f, %+.4f] | %+.4f [%+.4f, %+.4f]" % (
            m, st["accM"]["X0"][i], rk["X0"][i], st["accM"]["MF"][i], rk["MF"][i], st["accM"]["H"][i], rk["H"][i], st["accM"]["HL"][i],
            rk["HL"][i], st["d_x0_mf"][i], st["d_x0_mf_lo"][i], st["d_x0_mf_hi"][i], st["d_mf_h"][i], st["d_mf_h_lo"][i], st["d_mf_h_hi"][i]))
    ri = {s: midrank(st["accI"][s]) for s in SI}
    L.append("  IFEval accuracy (rank) per model: I0 | IS | IL | acc_IS - acc_IL [95%] | instruction-level strict / loose")
    for i, m in enumerate(models):
        a, b = data["inst_m"][(m, "strict")], data["inst_m"][(m, "loose")]
        L.append("    %-34s %.4f (%4.1f) | %.4f (%4.1f) | %.4f (%4.1f) | %+.4f [%+.4f, %+.4f] | %.4f / %.4f" % (
            m, st["accI"]["I0"][i], ri["I0"][i], st["accI"]["IS"][i], ri["IS"][i], st["accI"]["IL"][i], ri["IL"][i], st["d_is_il"][i],
            st["d_is_il_lo"][i], st["d_is_il_hi"][i], a[0] / max(1, a[1]), b[0] / max(1, b[1])))
    L.append("  IFEval instruction-level (all models): strict %d / %d = %.4f; loose %d / %d = %.4f; rows with IS != I0: %d (expected 0)" % (
        data["inst"]["strict"][0], data["inst"]["strict"][1], data["inst"]["strict"][0] / max(1, data["inst"]["strict"][1]),
        data["inst"]["loose"][0], data["inst"]["loose"][1], data["inst"]["loose"][0] / max(1, data["inst"]["loose"][1]), data["i0_ne_is"]))
    L.append("  HX5 categories over the X0-vs-MF disagreements (rule order; count, share [95%]):")
    tot = data["catq"].sum(0)
    for k, c in enumerate(CATS):
        L.append("    %-40s %5d  %.4f [%.4f, %.4f]%s" % (c, int(tot[k]), st["shares"][k], st["sh_lo"][k], st["sh_hi"][k],
                                                       " (format)" if c in FORMAT else ""))
    L.append("  X0 = 1 with MF = 0 (the pilot found none): %d; HX5 replicates without a disagreement row (dropped): %d" % (
        data["x0_1_mf_0"], st["hx5_dropped"]))
    L.append("  MF-vs-H disagreements by category and direction (beside): " + ("; ".join(
        "%s %s %d" % (c, d, n) for (c, d), n in sorted(data["mfh_cats"].items())) or "none"))
    L.append("  H-L beyond H (an unclosed think block's conclusion): %d rows" % int(data["M"]["HL"].sum() - data["M"]["H"].sum()))
    e1, e2, ne = st["sens_ex"]
    L.append("  SENSITIVITY (decides nothing) without the %d corrupted-reference questions %s: HX1 min tau-b %s, max shift %s -> %s;"
             " HX2 tau-b %s, max shift %s -> %s" % (ne, list(CORRUPT), _f(e1["min_tau"]), _f(e1["max_shift"], "%.1f"), e1["word"],
                                                    _f(e2["min_tau"]), _f(e2["max_shift"], "%.1f"), e2["word"]))
    l1, l2 = st["sens_hl"]
    L.append("  SENSITIVITY (decides nothing) with H-L in place of H: HX1 min tau-b %s, max shift %s -> %s; HX2 tau-b %s, max shift %s"
             " -> %s" % (_f(l1["min_tau"]), _f(l1["max_shift"], "%.1f"), l1["word"], _f(l2["min_tau"]), _f(l2["max_shift"], "%.1f"), l2["word"]))
    L.append("WHAT THIS RESULT WILL NOT SHOW (registered): which scorer is right beyond the pilot's 150-row adjudication; anything about"
             " the MATH rows on which X0 and MF agree; MMLU-Pro, BBH, MuSR or GPQA (log-likelihood; out of scope); IFEval truth beyond"
             " the official checks; models outside these 18 or that a published leaderboard is wrong; judged quality")
    return L


def figure_payload(st, data):
    models = data["models"]
    return dict(release="scorer x model accuracies, mid-ranks and category shares only (R5: no response text); relative to these"
                        " 18 models", models=models,
                math={s: dict(acc=[float(x) for x in st["accM"][s]], rank=[float(x) for x in midrank(st["accM"][s])]) for s in ("X0", "MF", "H", "HL")},
                ifeval={s: dict(acc=[float(x) for x in st["accI"][s]], rank=[float(x) for x in midrank(st["accI"][s])]) for s in SI},
                categories={c: dict(count=int(data["catq"].sum(0)[k]), share=float(st["shares"][k])) for k, c in enumerate(CATS)},
                words=dict(HX1=st["hx1"]["word"], HX2=dict(word=st["hx2"]["word"], support=DESC_ONLY),
                           HX3=dict(word=st["hx3"]["word"], support=DESC_ONLY), HX4=st["hx4"]))


# ═══════════════════════════════════════════════════════════════════════════════ modes
def outputs(cfg):
    return (os.path.join(cfg.out_dir, "harness_extractor_outcome.txt"), os.path.join(cfg.blog_dir, "harness_extractor_scores.json"))


def dry_run(cfg, say):
    b = busy_check(cfg.busy)
    read_inputs(cfg, say, full=False, pre=[b])
    o, fj = outputs(cfg)
    say("PLANNED: B %d component replicates (default_rng(%d)) and B %d i.i.d. replicates (default_rng(%d)); outcome %s; figure data"
        " %s (both write-once)" % (cfg.reg["B"], cfg.reg["seed"], cfg.reg["B"], cfg.reg["seed_iid"], o, fj))
    say("COST: 0 calls, 0 CCE; CPU minutes")
    hit("DRY.DONE")
    say("DRY-RUN: no scorer column was selected from the DB views (the tripwire sealed %s); the IFEval sample files' strict /"
        " loose verdict fields were parsed into memory for the join and not printed; no statistic printed; nothing written."
        % ", ".join(KEY_SEAL))


def run(cfg, say):
    o, fj = outputs(cfg)
    for p in (o, fj):
        if os.path.exists(p):
            refuse("%s exists: outcome and figure files are write-once" % p, "REFUSE.WRITE_ONCE")
    b = busy_check(cfg.busy)
    data = read_inputs(cfg, say, full=True, pre=[b])
    st = analyse(data, cfg.reg)
    vl, w = verdict_lines(st, cfg.reg)
    lines = vl + pred_lines(st, w, cfg.reg) + support_lines(st, data, cfg.reg) + descriptive_lines(st, data, cfg.reg)
    for ln in lines:
        say(ln)
    return data, st, w


def main(argv=None, out=print, cfg=None):
    ap = argparse.ArgumentParser(description="HARNESS-EXTRACTOR (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--data-root")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=a.only)
        return 0
    if a.mutants:
        return run_mutants(only=a.only)
    cfg = cfg or real_cfg()
    buf = []

    def say(s):
        buf.append(s)
        out(s)
    if a.dry_run:
        dry_run(cfg, say)
        return 0
    data, st, _w = run(cfg, say)
    o, fj = outputs(cfg)
    G.write_once(fj, json.dumps(figure_payload(st, data), sort_keys=True, indent=1) + "\n")
    text = "\n".join(buf) + "\n" + "FIGURE DATA (write-once; never committed): %s sha256-bytes %s\n" % (fj, G.sha256_file(fj))
    G.write_once(o, text)
    hit("OUT.RECORD")
    out("%s written: %s" % (TAG, o))
    return 0


# ══ SELFTEST (fixtures only; nothing of record is opened; everything below is test code)
SELFTEST_DOC = """
SELFTEST CASES (value-asserting; each executes the REAL entry point main() where named):
  pure       midrank (ties at mid-rank), tau_b against hand values and scipy.stats.kendalltau (variant b) with ties, max_shift,
             set_word at its edges (tau-b exactly 0.85 with shift exactly 2 HOLDS; 0.85 - 1e-9 MOVES; shift 2.5 MOVES), an
             undefined tau-b (constant accuracies) MOVES, rule8_hx1 at shift 2.0 / 2.5 / 3.0 (HX-R4: refuted only at <= 2), hx4_word at lo exactly 0.02 (not beyond)
             and hi exactly -0.02, hx5_word at exactly 0.50, brier and in_band by value
  copy       the COPIED source text of MINERVA and categorise equals the audit file's (ast), the audit file's sha256-lf16 is the
             pin; one hand case per category of the 7 (the rule order), and the H-L addition on an unclosed think block
  verdicts   verdict_lines / pred_lines on synthetic st: every word and branch (HOLD / MOVE, stable / fragile at S_w exactly
             0.80 / 0.7999, HX1 MOVE with HX2 HOLD (F-HX not fired, F-H fired), rule 8 both ways,
             rule 8 NOT refuted at tau-b 0.9 / shift 2.5 (HX-R4) with no HX-R4 text, F-HX / F-H both ways, HX4 / HX5 both ways and their rule-8 lines), every
             prediction line's band and Brier by value
  run_e2e    --run (main) on three fixtures: "move" (format habits per model: HX1 RANKS-MOVE, HX2 RANKS-MOVE, HX3 RANKS-MOVE,
             HX4 SHIFT-MATERIAL, HX5 MIXED; one stored I0 differing from the sample file's IS), "hold" (one Minerva habit: HX1 /
             HX2 / HX3 RANKS-HOLD, F-HX and F-H FIRED, HX4 SHIFT-SMALL, HX5 FORMAT-DOMINATED) and "edge" (a few format credits per
             model: HX1 reads RANKS-MOVE at max shift 2.5 with every tau-b >= 0.85, and RULE 8 prints "RANKS-MOVE is not
             refuted" end to end (HX-R4); HX1's S_w below HX3's), with case-variant questions so that components != questions:
             every printed number of HX1-HX5 (pairs, min tau-b, max shift,
             S_w, intervals, SDs), the rule-8 / falsifier lines, P1-P8, the Support SDs and DEFFs (HX1, HX5), every per-model
             accuracy and mid-rank (X0, MF, H, H-L, I0, IS, IL), the shift intervals, the 7 category counts and shares, the two
             sensitivity lines, the IS != I0 and X0 = 1 / MF = 0 counts, against an INDEPENDENT oracle (plain loops over the
             fixture's raw rows: its own R1, collapse, mid-ranks, tau-b, words; the component and i.i.d. draws re-derived from
             default_rng(seed) and the stem_key components); POOL line first; the header line; the outcome == the printed text;
             the figure JSON's values; no response text in any output; a second --run refused write-once before any read
  refusals   twins, roster (a 19th model), counts (a missing row), a duplicate row, MF missing, MF outside {0, 1}, NT missing, H
             pin (--run and --dry-run), H CR bytes, H row count, H route vs X0, H value vs the pinned h_score, an incomplete kept
             question with the per-model count intact, the raw file absent, two raw files for one model, a raw response differing from the DB's, a raw doc
             missing, busy exit 0 (--run and --dry-run), busy absent, a DB write during the read: each by its message, nothing
             written
  dry_run    POOL line first; no statistic; nothing written; the tripwire refuses a scorer column while sealed
  support    support_lines on a hand-made st: SD, DEFF = SD^2 / SD_iid^2, n_eff, MDE80 = 2.8 SD and both words, by value; (DELTA 3)
             every SUPPORT_PLAN row's printed line by value, its SE / MDE80 against an independent 0.03374 x sqrt(2,056 / n)
             recomputation, plan_word at the MDE80 boundary, the SE(tau) and F-H-SUPPORT plan lines
  (DELTA 3)  verdicts: HX2's "(descriptive-only by support)", the F-H qualifier both ways, FALSIFIER OF RECORD both ways and NOT
             FIRED with F-H fired; T-1 (non-first pair / NaN pair) in pure and verdicts; run_e2e "shift2" (X15) as in DELTA 3
  schema     (DELTA 4) F-2 / S-1: the fixture's 5 tables equal the real DBs' (sqlite_master text, PRAGMA table_info);
             schema_check on the REAL DBs reads exactly the 15 hand-listed columns, one line each, and prints the count line;
             each gate isolated by its exact message (G1 a declared absent column, G2 a statement naming the invented column,
             G3 reads != declared, both directions); main --dry-run and --run on a fixture carrying the invented column REFUSE
             at G1 before any row (no R1 line), nothing written; the sealed tripwire refuses ev / mf / ck and admits the rest
  busyself   (DELTA B-1) the REAL busy.ps1 from a live probe whose argv names this script: unexcluded it is busy and sees the
             probe; with the probe's PID the probe and this process are excluded and the exit equals an independent oracle
             (java or a remaining pattern match); sandbox copies through busy_check: the probe's chain frees, PID -1 and the
             default (the probe is a child) refuse, nothing-matching frees with this PID first; a throw (3), no exit code (99)
             and an exit bypassing the report REFUSE
  branches   every declared print branch was executed
"""


def _rm(d):
    import shutil
    import stat as _stat

    def onerr(func, path, _e):
        os.chmod(path, _stat.S_IWRITE)
        func(path)
    shutil.rmtree(d, onerror=onerr)


FX_MODELS = ["m%02d" % i for i in range(18)]
# the registered HX5 format categories, written out here (not FORMAT: a mutant of FORMAT must not move the oracle)
FORMAT_REGISTERED = ("BOXED_no_minerva_sentence", "FORMAT_minerva_present_norm_mismatch", "EQUIV_numeric_form")
_STYLE_TXT = {
    "minerva_ok": "Work.\nFinal Answer: The final answer is $%s$. I hope it is correct.",
    "boxed": "We compute.\nSo the answer is \\boxed{%s}",
    "minerva_mis": "Work.\nFinal Answer: The final answer is $%s$. I hope it is correct.",
    "think": "<think>\nreasoning, so \\boxed{%s}",
    "lastnum": "We add them and get %s",
    "prefix": "So \\boxed{%s \\text{ apples}}",
    "conflict": "So \\boxed{999}. Actually %s",
    "equiv": "So \\boxed{%s.0}",
    "ansline": "Work.\nThe answer is: %s",
}
# (X0, MF) stored for a CORRECT answer in each style (the fixture's imported harness credits only the Minerva form it parses)
_STYLE_KEY = {"minerva_ok": (1, 1), "boxed": (0, 1), "minerva_mis": (0, 1), "think": (0, 1), "lastnum": (0, 1), "prefix": (0, 1),
              "conflict": (0, 1), "equiv": (0, 1), "ansline": (0, 0)}


def _spec(kind="move", seed=7, n_m=40, n_i=26, mutate=None):
    """A fixture: MATH (one corrupted-reference id 2000164), IFEVAL and GPQA questions; R1 twins (a MATH EVAL id whose text is a
    GPQA id's, an IFEVAL EVAL id whose text is another IFEVAL id's), a collapsed MATH duplicate; 18 models (+ the excluded one on
    two rows) with per-model style habits; MF / X0 stored, nt flags, IFEval strict / loose vectors."""
    rs = np.random.RandomState(seed)
    qids, text, src, up, tgt, ev = [], {}, {}, {}, {}, []
    nid = {"MATH": 2000150, "IFEVAL": 3000000, "GPQA": 4000000}

    def new(s, t, target=None, is_eval=False):
        nid[s] += 1
        q = nid[s]
        qids.append(q)
        text[q], src[q], up[q] = t, s, q % 100000
        if target is not None:
            tgt[q] = target
        if is_eval:
            ev.append(q)
        return q
    math_q = []
    for j in range(n_m):
        q = new("MATH", "math question %d %s" % (j, "y" * (j % 4)), str(10 + j), is_eval=(j % 3 == 0))
        math_q.append(q)
    q164 = 2000164
    assert q164 in math_q, "the fixture must carry the corrupted-reference id 2000164"
    tgt[q164] = "-50"
    if_q = []
    for j in range(n_i):
        if_q.append(new("IFEVAL", "ifeval prompt %d %s" % (j, "z" * (j % 3)), json.dumps({"instruction_id_list": ["i%d" % k for k in range(1 + j % 3)]}), is_eval=(j % 2 == 0)))
    gp = [new("GPQA", "gpqa question %d" % j, None, is_eval=(j % 2 == 0)) for j in range(6)]
    # R1 twins: a MATH EVAL id whose exact text is a GPQA non-EVAL id's; an IFEVAL EVAL id with another IFEVAL non-EVAL id's text
    tw1 = new("MATH", text[gp[1]], "7", is_eval=True)
    tw2 = new("IFEVAL", text[if_q[1]], json.dumps({"instruction_id_list": ["i0"]}), is_eval=True)
    dup = new("MATH", text[math_q[4]], tgt[math_q[4]], is_eval=False)          # math_q[4] is non-EVAL: collapsed (higher id dropped)
    # case variants: distinct texts (kept) in the SAME CK-CLOSE component as their original (stem_key folds case)
    cvm = [new("MATH", text[math_q[j]].upper(), tgt[math_q[j]], is_eval=False) for j in (2, 5, 8, 11, 14)]
    cvi = [new("IFEVAL", text[if_q[j]].upper(), tgt[if_q[j]], is_eval=False) for j in (2, 5, 8)]
    math_all = math_q + [tw1, dup] + cvm
    if_all = if_q + [tw2] + cvi
    p = np.linspace(0.15, 0.95, 18)
    if kind == "move":
        habits = (["minerva_ok"] * 6 + ["boxed", "minerva_mis", "equiv"] * 2 + ["think"] * 3 + ["lastnum", "conflict", "prefix"])
        abil = np.concatenate([np.linspace(0.30, 0.40, 6), np.linspace(0.45, 0.55, 6), np.linspace(0.85, 0.95, 6)])
        loose = np.concatenate([np.full(9, 0.85), np.zeros(9)])
    else:
        habits = ["minerva_ok"] * 18
        abil = p
        loose = np.zeros(18)
    cells, mfv, nt, ifv = {}, {}, {}, {}
    for q in math_all:
        for mi, m in enumerate(FX_MODELS):
            T = tgt[q]
            forced = kind == "hold" and q in math_q[:2]          # hold: every model boxed-correct on 2 questions (ranks unmoved)
            if forced or rs.rand() < abil[mi]:
                st = "boxed" if forced else habits[mi]
                if kind == "edge" and rs.rand() < 0.12:          # edge: a few format credits per model, near the HX1 bar
                    st = "boxed"
                if kind == "move" and st != "minerva_ok" and rs.rand() < 0.1:
                    st = "ansline"
                out = _STYLE_TXT[st] % T
                x0, mf_ = _STYLE_KEY[st]
            else:
                out = "So \\boxed{%d}" % (1000 + mi)
                x0, mf_ = 0, 0
            cells[(q, m)] = (out, x0)
            mfv[(q, m)] = mf_
            nt[(q, m)] = int("<think>" in out and "</think>" not in out)
    for q in if_all:
        k = len(json.loads(tgt[q])["instruction_id_list"])
        for mi, m in enumerate(FX_MODELS):
            vs = [bool(rs.rand() < 0.35 + 0.6 * p[mi] if kind == "hold" else rs.rand() < abil[mi]) for _k in range(k)]
            vl = [bool(v or rs.rand() < loose[mi]) for v in vs]
            out = "response to %d by %s" % (q, m)
            cells[(q, m)] = (out, int(all(vs)))
            ifv[(q, m)] = (vs, vl)
    if kind == "move":                    # one stored I0 that differs from the sample file's IS (printed, counted)
        k0 = (if_q[3], FX_MODELS[4])
        cells[k0] = (cells[k0][0], 1 - cells[k0][1])
    for q in gp:
        for m in FX_MODELS:
            cells[(q, m)] = ("g", int(rs.rand() < 0.5))
    excl = [((math_q[0], EXCLUDED), ("x", 1)), ((if_q[0], EXCLUDED), ("x", 1))]
    spec = dict(kind=kind, qids=qids, text=text, src=src, up=up, tgt=tgt, ev=sorted(ev), cells=cells, mfv=mfv, nt=nt, ifv=ifv, excl=excl,
                models=list(FX_MODELS), math_all=sorted(math_all), if_all=sorted(if_all), tw=sorted([tw1, tw2]), dup=dup,
                extra_rows=[], drop_rows=[], h_crlf=False, raw_drop=[], raw_resp={})
    # the fixture H table: the pinned implementation on every MATH row (route "imported" iff X0)
    spec["h"] = {(q, m): MSH.h_score(cells[(q, m)][0], tgt[q], cells[(q, m)][1], q) for q in math_all for m in FX_MODELS}
    if mutate:
        mutate(spec)
    return spec


# -- DELTA 4, F-2: the fixture's tables are built from the REAL DBs' DDL (sqlite_master, read through pool_guard.open_ro:
# mode=ro&immutable=1; schema only, no row), so a fixture can no longer invent a column the DB lacks (POSTRUN F-2: four READY
# reviews passed a fixture whose eval_results_mathfix carried a column the real table does not have). Fail-closed: the real DBs
# are REQUIRED (from a worktree, --data-root <main checkout>). st_schema asserts the built fixture's sqlite_master equals the real.
FX_MC_TABLES = ("corpus_questions", "eval_results", "eval_results_mathfix", "reserved_pool")
FX_CK_TABLES = ("math_checker_answers_v2",)
_REAL_DDL = {}


def _real_ddl():
    if not _REAL_DDL:
        for rel, tabs in ((MC_REL, FX_MC_TABLES), (CK_REL, FX_CK_TABLES)):
            path = os.path.join(PG.DATA_ROOT, rel)
            assert os.path.isfile(path), ("F-2: the real DB %s is required to build the fixture schema (run with --data-root"
                                          " <main checkout>)" % path)
            c = PG.open_ro(path)
            try:
                for t in tabs:
                    r = c.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (t,)).fetchone()
                    assert r and r[0], ("F-2: the real %s has no table %s" % (path, t))
                    _REAL_DDL[t] = r[0]
            finally:
                c.close()
    return dict(_REAL_DDL)


def _fixture_ddl(spec):
    """The real DDL; spec["nopk"] drops eval_results' PRIMARY KEY (the "dup" refusal only: a row the real table cannot hold, the
    guard is defence in depth); spec["schema_drift"] renames eval_results_mathfix.is_correct to the invented is_correct_mathfix
    (the POSTRUN defect, for the S-1 refusal cases)."""
    ddl = _real_ddl()
    if spec.get("nopk"):
        new = re.sub(r",\s*PRIMARY KEY \(question_id, model_name\)\)\s*$", ")", ddl["eval_results"])
        assert new != ddl["eval_results"], "the real eval_results DDL no longer carries the PRIMARY KEY the dup case removes"
        ddl["eval_results"] = new
    if spec.get("schema_drift"):
        new = ddl["eval_results_mathfix"].replace("is_correct INTEGER", "is_correct_mathfix INTEGER")
        assert new != ddl["eval_results_mathfix"]
        ddl["eval_results_mathfix"] = new
    return ddl


def _ins(c, table, **vals):
    """Named insert; every NOT NULL column without a default that the fixture does not set gets a filler ('' / 0)."""
    for _cid, name, typ, notnull, dflt, _pk in c.execute('PRAGMA table_info("%s")' % table).fetchall():
        if name not in vals and notnull and dflt is None:
            vals[name] = 0 if "INT" in (typ or "").upper() else ""
    ks = sorted(vals)
    c.execute("INSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(ks), ", ".join("?" * len(ks))), [vals[k] for k in ks])


def _layout(tmp, spec, reg_over=None):
    import sqlite3
    os.makedirs(tmp, exist_ok=True)
    keyd = defaultdict(list)
    for q in spec["ev"]:
        keyd["%s/d0" % spec["src"][q]].append(q)
    pid = PG.compute_pool_id(keyd)
    idf = os.path.join(tmp, "pool_ids.json")
    with open(idf, "w", encoding="utf-8") as f:
        json.dump(keyd, f)
    db = os.path.join(tmp, "mc.db")
    ddl = _fixture_ddl(spec)                       # DELTA 4, F-2: the REAL tables' DDL, read from the real DBs' sqlite_master
    c = sqlite3.connect(db)
    for t in FX_MC_TABLES:
        c.execute(ddl[t])
    for q in spec["qids"]:
        _ins(c, "corpus_questions", question_id=q, source=spec["src"][q], upstream_id=spec["up"][q], task="t", text=spec["text"][q],
             target=spec["tgt"].get(q))
    rows = [((q, m), v) for (q, m), v in sorted(spec["cells"].items()) if (q, m) not in spec["drop_rows"]] + spec["excl"] + spec["extra_rows"]
    for (q, m), (out, x0) in rows:
        _ins(c, "eval_results", question_id=q, model_name=m, model_output=out, is_correct=x0)
    mfcol = "is_correct_mathfix" if spec.get("schema_drift") else "is_correct"
    for (q, m), v in sorted(spec["mfv"].items()):
        if v is not None:
            _ins(c, "eval_results_mathfix", question_id=q, model_name=m, **{mfcol: v})
    for k, ids in keyd.items():
        for q in ids:
            _ins(c, "reserved_pool", pool_id=pid, domain=k, question_id=q)
    c.commit()
    c.close()
    ck = os.path.join(tmp, "ck.db")
    c = sqlite3.connect(ck)
    c.execute(ddl["math_checker_answers_v2"])
    for (q, m), v in sorted(spec["nt"].items()):
        if v is not None:
            _ins(c, "math_checker_answers_v2", question_id=q, model_name=m, non_terminated=v)
    c.commit()
    c.close()
    raw = os.path.join(tmp, "raw")
    for m in spec["models"]:
        if m in spec["raw_drop"]:
            continue
        d = os.path.join(raw, m, "org__" + m)
        os.makedirs(d)
        if m in spec.get("raw_two", ()):
            open(os.path.join(d, "samples_leaderboard_ifeval_2024-12-31T00.jsonl"), "w").close()
        with open(os.path.join(d, "samples_leaderboard_ifeval_2025-01-01T00.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for q in spec["if_all"]:
                if (q, m) in spec.get("raw_skip", ()):
                    continue
                vs, vl = spec["ifv"][(q, m)]
                resp = spec["raw_resp"].get((q, m), spec["cells"][(q, m)][0])
                f.write(json.dumps(dict(doc_id=spec["up"][q], doc=dict(prompt=spec["text"][q], instruction_id_list=json.loads(spec["tgt"][q])["instruction_id_list"]),
                                        resps=[[resp]], prompt_level_strict_acc=all(vs), inst_level_strict_acc=vs,
                                        prompt_level_loose_acc=all(vl), inst_level_loose_acc=vl)) + "\n")
    hp = os.path.join(tmp, "math_h_table.csv")
    body = ("question_id,model,H,route\n" + "".join("%d,%s,%d,%s\n" % (q, m, h, r) for (q, m), (h, r) in sorted(spec["h"].items()))).encode("utf-8")
    if spec["h_crlf"]:
        body = body.replace(b"\n", b"\r\n")
    with open(hp, "wb") as f:
        f.write(body)
    busy = os.path.join(tmp, "busy_free.ps1")
    with open(busy, "w", encoding="utf-8") as f:
        f.write("exit 1\n")
    nmq = Counter(m for (q, m) in spec["cells"] if spec["src"][q] == "MATH" and (q, m) not in spec["drop_rows"])
    reg = dict(REG, r1_pool=pid, twins_ids=len(spec["tw"]), twins_texts=len({spec["text"][q] for q in spec["tw"]}),
               math_q=len(spec["math_all"]), ifeval_q=len(spec["if_all"]), h_rows=len(spec["h"]), B=200)
    reg.update(reg_over or {})
    return Cfg(reg=reg, r1_db=db, r1_idfile=idf, mc_db=db, ck_db=ck, raw_dir=raw, h_path=hp, h_pin=hashlib.sha256(body).hexdigest(),
               out_dir=os.path.join(tmp, "out"), blog_dir=os.path.join(tmp, "blog"), busy=busy, audit_src=AUDIT_SRC, _nmq=nmq)


def _main(cfg, argv):
    buf = []
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = main(argv, out=buf.append, cfg=cfg)
        except SystemExit as e:
            return None, buf, str(e)
    return rc, buf, None


def _line(buf, prefix):
    hits = [ln for ln in buf if ln.startswith(prefix)]
    assert len(hits) == 1, "expected one line starting %r, got %d" % (prefix, len(hits))
    return hits[0]


def _nums(s):
    return [float(x) for x in re.findall(r"[-+]?(?:\d+\.\d+|\d+|inf)", s)]


def _after(s, key):
    i = s.index(key) + len(key)
    m = re.match(r"\s*([-+]?(?:\d+\.\d+|\d+|inf|nan))", s[i:])
    return float(m.group(1))


# ── the INDEPENDENT oracle (plain loops over the fixture's raw rows) ──────────────────────────────────────────────────────────
def _o_kept(spec):
    text, src = spec["text"], spec["src"]
    ev = set(spec["ev"])
    tw = [q for q in spec["ev"] if any(text[g] == text[q] for g in spec["qids"] if g not in ev)]
    rest = [q for q in spec["qids"] if q not in tw]
    keep = [q for q in rest if not any(text[g] == text[q] and g < q for g in rest)]
    return sorted(q for q in keep if src[q] == "MATH"), sorted(q for q in keep if src[q] == "IFEVAL"), tw


def _o_vals(spec):
    km, ki, _tw = _o_kept(spec)
    mods = sorted(spec["models"])
    V = {s: {} for s in ("X0", "MF", "H", "HL", "I0", "IS", "IL")}
    for q in km:
        for m in mods:
            out, x0 = spec["cells"][(q, m)]
            V["X0"][(q, m)] = x0
            V["MF"][(q, m)] = spec["mfv"][(q, m)]
            h = spec["h"][(q, m)][0]
            V["H"][(q, m)] = h
            hl = h
            if "<think>" in out and "</think>" not in out:
                hl = max(h, MSH.h_score(out.split("<think>")[-1], spec["tgt"][q], 0, q)[0])
            V["HL"][(q, m)] = hl
    for q in ki:
        for m in mods:
            vs, vl = spec["ifv"][(q, m)]
            V["I0"][(q, m)] = spec["cells"][(q, m)][1]
            V["IS"][(q, m)] = int(all(vs))
            V["IL"][(q, m)] = int(all(vl))
    return km, ki, mods, V


def _o_acc(V, s, qs, mods, w):
    return [sum(w[q] * V[s][(q, m)] for q in qs) / sum(w[q] for q in qs) for m in mods]


def _o_rank(a):
    return [1 + sum(1 for y in a if y > x) + 0.5 * (sum(1 for y in a if y == x) - 1) for x in a]


def _o_tau(x, y):
    c = d = nx = ny = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx, dy = x[i] - x[j], y[i] - y[j]
            nx += dx != 0
            ny += dy != 0
            if dx * dy > 0:
                c += 1
            elif dx * dy < 0:
                d += 1
    return (c - d) / math.sqrt(nx * ny) if nx * ny > 0 else float("nan")


def _o_word(acc, names):
    best_t, best_s, pairs = None, None, []
    for a, b in itertools.combinations(names, 2):
        t = _o_tau(acc[a], acc[b])
        ra, rb = _o_rank(acc[a]), _o_rank(acc[b])
        sh = max(abs(u - v) for u, v in zip(ra, rb))
        pairs.append((a, b, t, sh))
        tt = t if t == t else -1e9
        best_t = tt if best_t is None else min(best_t, tt)
        best_s = sh if best_s is None else max(best_s, sh)
    return ("RANKS-HOLD" if (best_t >= 0.85 - 1e-12 and best_s <= 2) else "RANKS-MOVE"), best_t, best_s, pairs


def _o_point(spec, wq=None, ex_corrupt=False):
    km, ki, mods, V = _o_vals(spec)
    w = {q: 1.0 for q in km + ki}
    if wq:
        w.update(wq)
    if ex_corrupt:
        for q in km:
            if q in CORRUPT:
                w[q] = 0.0
    acc = {s: _o_acc(V, s, km, mods, w) for s in ("X0", "MF", "H", "HL")}
    acc.update({s: _o_acc(V, s, ki, mods, w) for s in SI})
    o = dict(acc=acc, km=km, ki=ki, mods=mods, V=V)
    o["hx1"] = _o_word(acc, SM)
    o["hx2"] = _o_word(acc, ("MF", "H"))
    o["hx3"] = _o_word(acc, SI)
    o["hl1"] = _o_word(dict(acc, H=acc["HL"]), SM)
    o["hl2"] = _o_word(dict(acc, H=acc["HL"]), ("MF", "H"))
    cat = Counter()
    rows = []
    for q in km:
        for m in mods:
            if V["X0"][(q, m)] != V["MF"][(q, m)]:
                cc = categorise(spec["cells"][(q, m)][0], spec["tgt"][q], spec["nt"][(q, m)])[0]
                cat[cc] += w[q]
                rows.append((q, cc))
    tot = sum(cat.values())
    o["shares"] = {c: (cat[c] / tot if tot else float("nan")) for c in CATS}
    o["format"] = sum(o["shares"][c] for c in FORMAT_REGISTERED) if tot else float("nan")
    o["rows"] = rows
    o["cnt"] = Counter(c for _q, c in rows)
    o["d_mf_h"] = [a - b for a, b in zip(acc["MF"], acc["H"])]
    o["d_x0_mf"] = [a - b for a, b in zip(acc["X0"], acc["MF"])]
    o["d_is_il"] = [a - b for a, b in zip(acc["IS"], acc["IL"])]
    return o


def _o_boot(spec, reg):
    """The two streams re-derived: components = sorted unique stem_keys within source; per replicate MATH then IFEval draws."""
    o0 = _o_point(spec)
    km, ki = o0["km"], o0["ki"]
    ckm = sorted(set(stem_key(spec["text"][q]) for q in km))
    cki = sorted(set(stem_key(spec["text"][q]) for q in ki))
    rng = np.random.default_rng(reg["seed"])
    rng2 = np.random.default_rng(reg["seed_iid"])
    comp, iid, fmt_iid = [], [], []
    rows = o0["rows"]
    for _r in range(reg["B"]):
        dm = rng.integers(0, len(ckm), len(ckm))
        di = rng.integers(0, len(cki), len(cki))
        w = {q: float(sum(1 for x in dm if ckm[x] == stem_key(spec["text"][q]))) for q in km}
        w.update({q: float(sum(1 for x in di if cki[x] == stem_key(spec["text"][q]))) for q in ki})
        comp.append(_o_point(spec, w))
        um = rng2.integers(0, len(km), len(km))
        ui = rng2.integers(0, len(ki), len(ki))
        u = {q: float(sum(1 for x in um if x == j)) for j, q in enumerate(km)}
        u.update({q: float(sum(1 for x in ui if x == j)) for j, q in enumerate(ki)})
        iid.append(_o_point(spec, u))
        if rows:
            dr = rng2.integers(0, len(rows), len(rows))
            fmt_iid.append(sum(1 for x in dr if rows[x][1] in FORMAT_REGISTERED) / float(len(rows)))
    return o0, comp, iid, fmt_iid


def _close(a, b, tol, what):
    if not (abs(a - b) <= tol or (math.isnan(a) and math.isnan(b))):
        raise AssertionError("%s: %r vs %r (tol %g)" % (what, a, b, tol))


def _check(buf, spec, cfg, want):
    with np.errstate(invalid="ignore", divide="ignore"):      # a constant replicate series (hold) gives DEFF 0 / 0 = nan on both sides
        return _check_(buf, spec, cfg, want)


def _check_(buf, spec, cfg, want):
    reg = cfg.reg
    o, comp, iid, fmt_iid = _o_boot(spec, reg)
    mods = o["mods"]
    if want is None:                       # the "edge" fixture: the words are the oracle's (asserted non-vacuous by the caller)
        D0 = np.array([r["d_mf_h"] for r in comp])
        l0, h0 = np.percentile(D0, 2.5, axis=0), np.percentile(D0, 97.5, axis=0)
        want = dict(HX1=o["hx1"][0], HX2=o["hx2"][0], HX3=o["hx3"][0],
                    HX4="SHIFT-MATERIAL" if any(a > 0.02 or b < -0.02 for a, b in zip(l0, h0)) else "SHIFT-SMALL",
                    HX5="FORMAT-DOMINATED" if o["format"] >= 0.50 else "MIXED")
    T = 5.0001e-5
    for key, names, lab in (("hx1", SM, "HX1 (DECIDING"), ("hx2", ("MF", "H"), "HX2 (MATH"), ("hx3", SI, "HX3 (IFEval")):
        word, mt, ms, pairs = o[key]
        ln = _line(buf, lab)
        _close(_after(ln, "tau-b " if key == "hx2" else "min pairwise tau-b "), mt, T, key + " min tau")
        _close(_after(ln, "max rank shift "), ms, 0.05, key + " max shift")
        for a, b, t, sh in pairs:
            if key != "hx2":
                assert ("%s-%s tau-b %s, max shift %.1f" % (a, b, _f(t), sh)) in ln, (key, a, b, t, sh, ln)
        assert word == want[key.upper()], (key, word, want)
        sw = sum(1 for r in comp if r[key][0] == word) / float(len(comp))
        if key == "hx1":
            l2 = _line(buf, "  HX1 -> ")
            assert l2.startswith("  HX1 -> %s (%s; S_w %s over B %d)" % (word, "stable" if sw >= 0.80 else "fragile", _f(sw), reg["B"])), (l2, sw)
            ts = [r[key][1] for r in comp]
            assert ("[min tau-b 95%% %s, %s, bootstrap SD %s;" % (_f(pctl(ts, 2.5)), _f(pctl(ts, 97.5)), _f(float(np.std(ts, ddof=1))))) in l2, l2
        elif key == "hx2":
            assert ("-> %s (descriptive-only by support) (S_w %s)" % (word, _f(sw))) in ln, (ln, sw)
        else:
            assert _line(buf, "  HX3 -> ") == "  HX3 -> %s (descriptive-only by support) (S_w %s)" % (word, _f(sw))
    # rule 8 / falsifiers
    w1 = o["hx1"][0]
    r8 = all(p[2] >= 0.85 - 1e-12 for p in o["hx1"][3]) and o["hx1"][2] <= 2      # HX-R4: refuted only at max shift <= 2
    assert r8 == (w1 == "RANKS-HOLD"), ("HX-R4: rule 8 is the exact complement of the HX1 word", r8, w1)
    assert _line(buf, "RULE 8 (HX1): RANKS-MOVE is ") == ("RULE 8 (HX1): RANKS-MOVE is REFUTED (every pair tau-b >= 0.85 and no model moves"
                                                         " more than 2 ranks)" if r8 else "RULE 8 (HX1): RANKS-MOVE is not refuted (a pair"
                                                         " below tau-b 0.85 or a model moving more than 2 ranks)")
    assert not [x for x in buf if "HX-R4" in x or "REGISTRATION DEFECT" in x], "superseded HX-R4 defect text printed"
    w2o = o["hx2"][0]
    assert _line(buf, "  RULE 8 (HX2, HX-R5): ") == (
        "  RULE 8 (HX2, HX-R5): %s would be refuted by %s's observable; observed tau-b %s, max shift %.1f: %s is not refuted"
        " (descriptive-only by support)" % (w2o, "RANKS-MOVE" if w2o == "RANKS-HOLD" else "RANKS-HOLD", _f(o["hx2"][1]), o["hx2"][2], w2o))
    assert _line(buf, "FALSIFIER F-HX: ").startswith("FALSIFIER F-HX: %s" % ("FIRED" if w1 == "RANKS-HOLD" else "NOT FIRED"))
    assert _line(buf, "FALSIFIER F-H (").startswith("FALSIFIER F-H (descriptive-only by support; decides nothing): %s (HX2 reads %s" % (
        "FIRED" if o["hx2"][0] == "RANKS-HOLD" else "NOT FIRED", o["hx2"][0]))
    assert _line(buf, "FALSIFIER OF RECORD: ") == "FALSIFIER OF RECORD: F-HX %s (F-H takes no part; ruling F-H-SUPPORT)" % (
        "FIRED" if w1 == "RANKS-HOLD" else "NOT FIRED")
    # HX4 (intervals of acc_MF - acc_H over the replicates)
    D = np.array([r["d_mf_h"] for r in comp])
    lo, hi = np.percentile(D, 2.5, axis=0), np.percentile(D, 97.5, axis=0)
    n4 = sum(1 for a, b in zip(lo, hi) if a > 0.02 or b < -0.02)
    w4 = "SHIFT-MATERIAL" if n4 >= 1 else "SHIFT-SMALL"
    assert w4 == want["HX4"], (w4, want)
    assert _line(buf, "HX4 (MATH").endswith("models whose interval lies wholly beyond |0.02|: %d -> %s" % (n4, w4)), _line(buf, "HX4 (MATH")
    # HX5
    fs = [r["format"] for r in comp if r["format"] == r["format"]]
    w5 = "FORMAT-DOMINATED" if o["format"] >= 0.50 else "MIXED"
    assert w5 == want["HX5"], (w5, want)
    l5 = _line(buf, "HX5 (MATH")
    sw5 = sum(1 for x in fs if (x >= 0.5) == (o["format"] >= 0.5)) / float(len(fs))
    assert (") %s [95%% %s, %s] of %d rows -> %s (S_w %s)" % (_f(o["format"]), _f(pctl(fs, 2.5)), _f(pctl(fs, 97.5)), len(o["rows"]), w5, _f(sw5))) in l5, (l5, o["format"])
    # predictions (values and Brier)
    assert _line(buf, "PREDICTION P1 (HX1)") == "PREDICTION P1 (HX1): word %s, Brier %.4f (RANKS-MOVE 0.97)" % (
        w1, (0.97 - (w1 == "RANKS-MOVE")) ** 2 + (0.03 - (w1 == "RANKS-HOLD")) ** 2)
    _close(_after(_line(buf, "PREDICTION P2 (HX1)"), ") "), o["hx1"][1], T, "P2")
    assert ("HELD" if -0.20 <= o["hx1"][1] <= 0.70 else "FAILED") in _line(buf, "PREDICTION P2 (HX1)")
    _close(_after(_line(buf, "PREDICTION P3 (HX1)"), "max rank shift "), o["hx1"][2], 0.05, "P3")
    l6 = _line(buf, "PREDICTION P6 (HX4)")
    _close(_after(l6, "max |acc_MF - acc_H| "), max(abs(x) for x in o["d_mf_h"]), T, "P6 max")
    _close(_after(l6, "models clearing 0.02 "), n4, 0.0, "P6 n")
    _close(_after(_line(buf, "PREDICTION P8 (IFEval)"), "over models "), max(abs(x) for x in o["d_is_il"]), T, "P8")
    _close(_after(_line(buf, "PREDICTION P7 (HX5)"), "format share "), o["format"], T, "P7")
    # Support: the HX1 SD and DEFF, the HX5 SD and DEFF
    ts = [r["hx1"][1] for r in comp]
    ti = [r["hx1"][1] for r in iid]
    s1 = _line(buf, "  HX1 min tau-b: ")
    _close(_after(s1, "bootstrap SD "), float(np.std(ts, ddof=1)), T, "HX1 SD")
    _close(_after(s1, "DEFF "), float(np.var(ts, ddof=1) / np.var(ti, ddof=1)), 5.0001e-4, "HX1 DEFF")
    s5 = _line(buf, "  HX5 format share: ")
    _close(_after(s5, "bootstrap SD "), float(np.std(fs, ddof=1)), T, "HX5 SD")
    _close(_after(s5, "DEFF "), float(np.var(fs, ddof=1) / np.var(fmt_iid, ddof=1)), 5.0001e-4, "HX5 DEFF")
    # descriptive: every per-model accuracy and mid-rank, the shift intervals
    rk = {s: _o_rank(o["acc"][s]) for s in o["acc"]}
    DX = np.array([r["d_x0_mf"] for r in comp])
    DI = np.array([r["d_is_il"] for r in comp])
    for i, m in enumerate(mods):
        ln = [x for x in buf if x.startswith("    %-34s " % m)]
        assert len(ln) == 2 and ln[0].count("|") == 5 and ln[1].count("|") == 4, (m, ln)
        mline, iline = ln
        want_m = "%.4f (%4.1f) | %.4f (%4.1f) | %.4f (%4.1f) | %.4f (%4.1f) | %+.4f [%+.4f, %+.4f] | %+.4f [%+.4f, %+.4f]" % (
            o["acc"]["X0"][i], rk["X0"][i], o["acc"]["MF"][i], rk["MF"][i], o["acc"]["H"][i], rk["H"][i], o["acc"]["HL"][i], rk["HL"][i],
            o["d_x0_mf"][i], np.percentile(DX[:, i], 2.5), np.percentile(DX[:, i], 97.5), o["d_mf_h"][i], lo[i], hi[i])
        assert mline.endswith(want_m), (m, mline, want_m)
        want_i = "%.4f (%4.1f) | %.4f (%4.1f) | %.4f (%4.1f) | %+.4f [%+.4f, %+.4f]" % (
            o["acc"]["I0"][i], rk["I0"][i], o["acc"]["IS"][i], rk["IS"][i], o["acc"]["IL"][i], rk["IL"][i], o["d_is_il"][i],
            np.percentile(DI[:, i], 2.5), np.percentile(DI[:, i], 97.5))
        assert want_i in iline, (m, iline, want_i)
    for c in CATS:
        ln = _line(buf, "    %-40s " % c)
        assert int(_nums(ln.split(c)[1])[0]) == o["cnt"][c], (c, ln, o["cnt"][c])
        sh = [r["shares"][c] for r in comp if r["format"] == r["format"]]
        assert ("%.4f [%.4f, %.4f]" % (o["shares"][c] if o["shares"][c] == o["shares"][c] else float("nan"), np.percentile(sh, 2.5),
                                       np.percentile(sh, 97.5))) in ln, (c, ln)
    e = _o_point(spec, ex_corrupt=True)
    se = _line(buf, "  SENSITIVITY (decides nothing) without the 1 corrupted-reference")
    assert ("HX1 min tau-b %s, max shift %.1f -> %s; HX2 tau-b %s, max shift %.1f -> %s" % (
        _f(e["hx1"][1]), e["hx1"][2], e["hx1"][0], _f(e["hx2"][1]), e["hx2"][2], e["hx2"][0])) in se, se
    sl = _line(buf, "  SENSITIVITY (decides nothing) with H-L in place of H")
    assert ("HX1 min tau-b %s, max shift %.1f -> %s; HX2 tau-b %s, max shift %.1f -> %s" % (
        _f(o["hl1"][1]), o["hl1"][2], o["hl1"][0], _f(o["hl2"][1]), o["hl2"][2], o["hl2"][0])) in sl, sl
    nis = sum(1 for k in o["V"]["I0"] if o["V"]["I0"][k] != o["V"]["IS"][k])
    assert ("rows with IS != I0: %d (expected 0)" % nis) in _line(buf, "  IFEval instruction-level (all models)")
    assert nis == (1 if spec["kind"] == "move" else 0)
    km_ = o["km"]
    ncl = len(set(stem_key(spec["text"][q]) for q in km_))
    assert ncl < len(km_) and ("MATH %d questions (%d components," % (len(km_), ncl)) in _line(buf, "  denominators: ")
    hlx = sum(o["V"]["HL"].values()) - sum(o["V"]["H"].values())
    assert _line(buf, "  H-L beyond H") == "  H-L beyond H (an unclosed think block's conclusion): %d rows" % hlx
    assert _line(buf, "  X0 = 1 with MF = 0").startswith("  X0 = 1 with MF = 0 (the pilot found none): %d;" % sum(
        1 for k in o["V"]["X0"] if o["V"]["X0"][k] == 1 and o["V"]["MF"][k] == 0))
    return o


def _want(kind):
    if kind == "move":
        return dict(HX1="RANKS-MOVE", HX2="RANKS-MOVE", HX3="RANKS-MOVE", HX4="SHIFT-MATERIAL", HX5="MIXED")
    return dict(HX1="RANKS-HOLD", HX2="RANKS-HOLD", HX3="RANKS-HOLD", HX4="SHIFT-SMALL", HX5="FORMAT-DOMINATED")


def _shift2(spec):
    """X15 fixture (delta 3): on the "hold" fixture, MATH-FIX credits one model on its first k wrong kept questions, the first
    (model, k) in a fixed scan for which the ORACLE reads HX1 RANKS-HOLD at max rank shift EXACTLY 2.0 with every tau-b >= 0.85."""
    km = _o_kept(spec)[0]
    base = dict(spec["mfv"])
    for m in sorted(spec["models"]):
        wrong = [q for q in km if base[(q, m)] == 0]
        for k in range(1, len(wrong) + 1):
            spec["mfv"] = dict(base)
            for q in wrong[:k]:
                spec["mfv"][(q, m)] = 1
            w, mt, ms, _p = _o_point(spec)["hx1"]
            if ms == 2.0 and w == "RANKS-HOLD" and mt >= 0.85:
                spec["shift2"] = (m, k)
                return
            if ms > 2.0:
                break
    raise AssertionError("no shift-2 fixture found")


def st_run_e2e():
    import tempfile
    for kind, seed in (("move", 7), ("hold", 3), ("edge", 4), ("shift2", 3)):
        d = tempfile.mkdtemp(prefix="hx_e2e_")
        try:
            spec = _spec(kind="hold", seed=seed, mutate=_shift2) if kind == "shift2" else _spec(kind=kind, seed=seed)
            cfg = _layout(d, spec)
            rc, buf, err = _main(cfg, ["--run"])
            assert err is None, (kind, err)
            assert buf[0].startswith("POOL %s verified" % cfg.reg["r1_pool"]), buf[0]
            assert _line(buf, "MATH scorer: ").startswith("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H"
                                                          " (table sha256-lf %s); MATH-FIX beside: yes" % cfg.h_pin)
            o_ = _check(buf, spec, cfg, None if kind in ("edge", "shift2") else _want(kind))
            if kind == "shift2":               # non-vacuous (X15): HX1 HOLDS at max shift EXACTLY 2 -> rule 8 REFUTED, F-HX FIRED, end to end
                assert o_["hx1"][0] == "RANKS-HOLD" and o_["hx1"][2] == 2.0 and o_["hx1"][1] >= 0.85 and "shift2" in spec, o_["hx1"][:3]
                assert _after(_line(buf, "HX1 (DECIDING"), "max rank shift ") == 2.0
                assert _line(buf, "  HX1 -> ").startswith("  HX1 -> RANKS-HOLD (")
                assert _line(buf, "RULE 8 (HX1): ") == ("RULE 8 (HX1): RANKS-MOVE is REFUTED (every pair tau-b >= 0.85 and no model moves"
                                                        " more than 2 ranks)")
                assert _line(buf, "FALSIFIER F-HX: ").startswith("FALSIFIER F-HX: FIRED (HX1 reads RANKS-HOLD)")
                assert _line(buf, "FALSIFIER OF RECORD: ") == "FALSIFIER OF RECORD: F-HX FIRED (F-H takes no part; ruling F-H-SUPPORT)"
            if kind == "edge":                 # non-vacuous: HX1 MOVES at max shift 2.5 with every tau-b >= 0.85 (HX-R4: NOT refuted); S_w below HX3's
                assert o_["hx1"][0] == "RANKS-MOVE" and o_["hx1"][2] == 2.5 and o_["hx1"][1] >= 0.85, o_["hx1"][:3]
                assert _line(buf, "  HX1 -> ").startswith("  HX1 -> RANKS-MOVE (")
                assert _line(buf, "RULE 8 (HX1): ") == ("RULE 8 (HX1): RANKS-MOVE is not refuted (a pair below tau-b 0.85 or a model"
                                                        " moving more than 2 ranks)")
                assert _line(buf, "FALSIFIER F-HX: ") == "FALSIFIER F-HX: NOT FIRED (HX1 reads RANKS-MOVE)"
                assert _after(_line(buf, "  HX1 -> "), "S_w ") < _after(_line(buf, "  HX3 -> "), "S_w ") - 0.1, "S_w not per criterion"
            km, ki, tw = _o_kept(spec)
            assert _line(buf, "R1: 2 EVAL ids / 2 distinct texts") and len(tw) == 2
            assert ("kept MATH %d of %d, IFEVAL %d of %d" % (len(km), len(spec["math_all"]), len(ki), len(spec["if_all"]))) in _line(buf, "R1: remaining")
            assert ("excluded: 2") in _line(buf, "  roster: MATH ")
            o, fj = outputs(cfg)
            text = open(o, encoding="utf-8").read()
            assert text.startswith("POOL ") and all(ln in text for ln in buf[:-1]), "outcome != the printed lines"
            pay = json.load(open(fj, encoding="utf-8"))
            op = _o_point(spec)
            # DELTA 4, L-H1: HX2 / HX3 released only with their qualifier; HX1 / HX4 bare (scored words)
            assert pay["words"]["HX2"] == dict(word=o_["hx2"][0], support="descriptive-only by support"), pay["words"]
            assert pay["words"]["HX3"] == dict(word=o_["hx3"][0], support="descriptive-only by support"), pay["words"]
            assert pay["words"]["HX1"] == o_["hx1"][0] and isinstance(pay["words"]["HX4"], str), pay["words"]
            if kind in ("edge", "shift2"):
                continue
            for s in ("X0", "MF", "H", "HL"):
                assert np.allclose(pay["math"][s]["acc"], op["acc"][s], atol=1e-12) and pay["math"][s]["rank"] == _o_rank(op["acc"][s]), s
            assert pay["words"]["HX1"] == _want(kind)["HX1"] and pay["words"]["HX4"] == _want(kind)["HX4"]
            for (q, m), (out, _x) in spec["cells"].items():
                if len(out) > 12:
                    assert out not in text and out not in json.dumps(pay), "a response text was released"
            rc2, buf2, err2 = _main(cfg, ["--run"])
            assert err2 and "write-once" in err2 and not buf2, err2
        finally:
            _rm(d)


def _t1_sets(kind):
    """T-1 fixtures with max shift <= 2 and the FIRST pair perfect: 'nonfirst' = A == B (tau-b 1) and C = A with six 3-blocks
    reversed (shift 2 at each block's ends; tau-b 1 - 36 / 153 = 0.7647 on A-C and B-C); 'nan' = two models, C constant (tau-b
    undefined, mid-rank shift 0.5) after A == B."""
    if kind == "nonfirst":
        a = np.linspace(0.1, 0.9, 18)
        c = a.reshape(6, 3)[:, ::-1].reshape(-1).copy()
        return dict(A=a, B=a.copy(), C=c), ("A", "B", "C")
    a = np.array([0.1, 0.9])
    return dict(A=a, B=a.copy(), C=np.array([0.5, 0.5])), ("A", "B", "C")


def st_pure():
    from scipy.stats import kendalltau
    assert list(midrank([0.5, 0.7, 0.5, 0.1])) == [2.5, 1.0, 2.5, 4.0]
    rs = np.random.RandomState(3)
    for _ in range(20):
        x = rs.randint(0, 5, 18).astype(float)
        y = rs.randint(0, 5, 18).astype(float)
        _close(tau_b(x, y), kendalltau(x, y, variant="b").statistic, 1e-12, "tau_b vs scipy")
    x = np.arange(18, dtype=float)
    y = x.copy()
    y[[0, 1]] = y[[1, 0]]
    _close(tau_b(x, y), 1 - 2.0 / 153, 1e-12, "one swap")
    assert max_shift([0.9, 0.8, 0.7], [0.7, 0.8, 0.9]) == 2.0
    reg = dict(REG)
    mk = lambda t, s: dict(pairs=[("A", "B", t, s)], max_shift=s)     # noqa: E731
    # set_word edges through constructed accuracies: identical -> tau 1, shift 0
    a = np.linspace(0.1, 0.9, 18)
    assert set_word(dict(A=a, B=a), ("A", "B"), reg)["word"] == "RANKS-HOLD"
    b = a.copy()
    b[[0, 3]] = b[[3, 0]]                                  # shift exactly 3 -> MOVE
    sw = set_word(dict(A=a, B=b), ("A", "B"), reg)
    assert sw["max_shift"] == 3.0 and sw["word"] == "RANKS-MOVE", sw
    c_ = a.copy()
    c_[[0, 2]] = c_[[2, 0]]                                # shift exactly 2, tau 1 - 6/153 = 0.9608 -> HOLD
    sw = set_word(dict(A=a, B=c_), ("A", "B"), reg)
    assert sw["max_shift"] == 2.0 and sw["word"] == "RANKS-HOLD", sw
    cc = a.copy()
    cc[1] = cc[2]                                          # a tie: mid-rank shift 0.5
    assert set_word(dict(A=a, B=cc), ("A", "B"), reg)["max_shift"] == 0.5
    k = np.zeros(18)
    sw = set_word(dict(A=a, B=k), ("A", "B"), reg)         # tau-b undefined (constant) -> MOVE
    assert math.isnan(sw["pairs"][0][2]) and sw["word"] == "RANKS-MOVE", sw
    sw = set_word(dict(A=k, B=k + 0.5), ("A", "B"), reg)   # undefined tau-b with max shift 0: still MOVE (cannot hold)
    assert math.isnan(sw["pairs"][0][2]) and sw["max_shift"] == 0.0 and sw["word"] == "RANKS-MOVE", sw
    r2 = dict(reg, tau_bar=round(1 - 6.0 / 153, 12))      # the bar EXACTLY at the observed tau-b (12 dp, HX-R3) holds (>=)
    assert set_word(dict(A=a, B=c_), ("A", "B"), r2)["word"] == "RANKS-HOLD"
    r3 = dict(reg, tau_bar=1 - 6.0 / 153 + 1e-9)
    assert set_word(dict(A=a, B=c_), ("A", "B"), r3)["word"] == "RANKS-MOVE"
    assert rule8_hx1(mk(0.9, 2.0), reg) is True and rule8_hx1(mk(0.85, 2.0), reg) is True     # HX-R4: refuted at max shift <= 2
    assert rule8_hx1(mk(0.9, 2.5), reg) is False and rule8_hx1(mk(0.9, 3.0), reg) is False and rule8_hx1(mk(0.84, 0.0), reg) is False
    assert "move_bar" not in REG
    # T-1 (H03 / H04): a NON-first pair below 0.85, and a NaN pair, with max shift <= 2: rule 8 does not refute, == the HX1 word
    acc, names = _t1_sets("nonfirst")
    h = set_word(acc, names, reg)
    assert [round(p[2], 4) for p in h["pairs"]] == [1.0, 0.7647, 0.7647] and h["max_shift"] == 2.0 and h["word"] == "RANKS-MOVE", h
    assert rule8_hx1(h, reg) is False and rule8_hx1(h, reg) == (h["word"] == "RANKS-HOLD")
    acc, names = _t1_sets("nan")
    h = set_word(acc, names, reg)
    assert h["pairs"][0][2] == 1.0 and math.isnan(h["pairs"][1][2]) and h["max_shift"] == 0.5 and h["word"] == "RANKS-MOVE", h
    assert rule8_hx1(h, reg) is False and rule8_hx1(h, reg) == (h["word"] == "RANKS-HOLD")
    assert rule8_hx1(dict(pairs=[("A", "B", 0.95, 1.0), ("A", "C", 0.8499, 1.0)], max_shift=1.0), reg) is False
    assert rule8_hx1(dict(pairs=[("A", "B", 0.95, 1.0), ("A", "C", float("nan"), 1.0)], max_shift=1.0), reg) is False
    assert hx4_word([0.02, 0.0], [0.05, 0.01], reg) == ("SHIFT-SMALL", 0)
    assert hx4_word([-0.05, 0.021], [-0.02, 0.05], reg) == ("SHIFT-MATERIAL", 1)
    assert hx4_word([-0.05], [-0.0201], reg) == ("SHIFT-MATERIAL", 1)
    assert hx5_word(0.50, reg) == "FORMAT-DOMINATED" and hx5_word(0.4999, reg) == "MIXED" and hx5_word(float("nan"), reg) == "MIXED"
    _close(brier(PRED["P1"], "RANKS-MOVE"), 0.03 ** 2 * 2, 1e-12, "brier")
    assert in_band(0.70, PRED["P2"]) and not in_band(0.7001, PRED["P2"])
    assert kish(np.array([0, 0, 1])) == 5.0 / 3


def st_copy():
    path, pin = AUDIT_SRC
    raw = open(path, "rb").read().replace(b"\r\n", b"\n")
    assert hashlib.sha256(raw).hexdigest()[:16] == pin, "the audit source changed"
    src_a = raw.decode("utf-8")
    mine = open(os.path.abspath(__file__), encoding="utf-8").read()
    ta, tm = ast.parse(src_a), ast.parse(mine)

    def seg(tree, src, name):
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return ast.get_source_segment(src, node)
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                return ast.get_source_segment(src, node)
        raise AssertionError("%s not found" % name)
    for name in COPIED:
        assert seg(ta, src_a, name) == seg(tm, mine, name), "the copy of %s differs from the audit source" % name
    T = "17"
    cases = (("So \\boxed{999}. Actually 17", 0, "CONFLICT_stated_wrong_other_matched"),
             ("We add them and get 17", 0, "LASTNUM_ONLY_no_stated_answer"),
             ("So \\boxed{17 \\text{ apples}}", 0, "PREFIX_partial_numeric"),
             ("<think>\nso \\boxed{17}", 1, "NONTERM_stated_answer_matches"),
             ("So \\boxed{17.0}", 0, "EQUIV_numeric_form"),
             ("So the answer is \\boxed{17}", 0, "BOXED_no_minerva_sentence"),
             ("Final Answer: The final answer is $17$. I hope it is correct.", 0, "FORMAT_minerva_present_norm_mismatch"))
    for resp, nt, want in cases:
        assert categorise(resp, T, nt)[0] == want, (resp, want, categorise(resp, T, nt)[0])
    assert [c for _r, _n, c in cases] == list(CATS), "CATS is not the rule order"
    assert tuple(sorted(FORMAT)) == tuple(sorted(FORMAT_REGISTERED)), ("FORMAT is not the registered three", FORMAT)
    assert hl_extra("<think>\nso \\boxed{17}", T, 5) == 1 and hl_extra("<think>a</think> \\boxed{17}", T, 5) == 0
    assert hl_extra("so \\boxed{17}", T, 5) == 0 and hl_extra("<think>\nso \\boxed{18}", T, 5) == 0
    assert h_score("<think>\nso \\boxed{17}", T, 0, 5)[0] == 0          # H itself never credits an unclosed think block


def _fake_st(w1="RANKS-MOVE", t1=0.3, s1=9.0, sw=0.9, w2="RANKS-MOVE", w3="RANKS-HOLD", fmt=0.6, n4lo=0.05):
    hx = lambda w, t, s: dict(word=w, min_tau=t, max_shift=s, pairs=[("X0", "MF", t, s)], argmin=("X0", "MF"), sw=sw, lo=t - 0.1,   # noqa: E731
                              hi=t + 0.1, sd=0.05, sd_iid=0.04)
    st = dict(hx1=hx(w1, t1, s1), hx2=hx(w2, 0.9 if w2 == "RANKS-HOLD" else 0.5, 1.0 if w2 == "RANKS-HOLD" else 4.0),
              hx3=hx(w3, 0.95 if w3 == "RANKS-HOLD" else 0.5, 0.0 if w3 == "RANKS-HOLD" else 5.0), B=200, format=fmt, fmt_lo=fmt - 0.1,
              fmt_hi=fmt + 0.1, n_dis_w=100.0, hx5_sw=0.9, d_mf_h=np.array([-0.05, 0.01]), d_is_il=np.array([-0.03, 0.0]))
    st["hx4"], st["hx4_n"] = hx4_word([n4lo, -0.02], [0.08, 0.0], dict(REG))
    return st


def st_verdicts():
    reg = dict(REG)
    L, w = verdict_lines(_fake_st(), reg)
    t = "\n".join(L)
    assert "HX1 -> RANKS-MOVE (stable; S_w 0.9000 over B 200)" in t and "RANKS-MOVE is not refuted" in t and "F-HX: NOT FIRED" in t
    assert "HX4 (MATH; acc_MF - acc_H per model; the 95% INTERVAL decides): models whose interval lies wholly beyond |0.02|: 1 -> SHIFT-MATERIAL" in t
    assert "HX5 (MATH" in t and "-> MIXED" not in t and "FORMAT-DOMINATED is not refuted (format share 0.6000 >= 0.50)" in t
    L, w = verdict_lines(_fake_st(w1="RANKS-HOLD", t1=0.9, s1=1.0, sw=0.5, w2="RANKS-HOLD", w3="RANKS-MOVE", fmt=0.4, n4lo=0.01), reg)
    t = "\n".join(L)
    assert "HX1 -> RANKS-HOLD (fragile; S_w 0.5000 over B 200)" in t and "RANKS-MOVE is REFUTED" in t and "F-HX: FIRED" in t
    assert "F-H (descriptive-only by support; decides nothing): FIRED (HX2 reads RANKS-HOLD;" in t and "HX3 -> RANKS-MOVE (descriptive-only by support)" in t and "-> SHIFT-SMALL" in t
    assert "FALSIFIER OF RECORD: F-HX FIRED (F-H takes no part; ruling F-H-SUPPORT)" in L, L
    assert "-> RANKS-HOLD (descriptive-only by support) (S_w 0.5000) [tau-b 95% 0.8000, 1.0000]" in _line(L, "HX2 (MATH"), L
    assert "SHIFT-MATERIAL is REFUTED (no model's 95% bound clears 0.02)" in t and "-> MIXED (S_w" in t
    assert "FORMAT-DOMINATED is REFUTED (format share 0.4000 < 0.50)" in t
    assert "HX-R4" not in t
    L, w = verdict_lines(_fake_st(sw=0.80, w2="RANKS-HOLD"), reg)
    t = "\n".join(L)
    assert "HX1 -> RANKS-MOVE (stable; S_w 0.8000 over B 200)" in t and "F-HX: NOT FIRED" in t and "F-H (descriptive-only by support; decides nothing): FIRED" in t
    assert "FALSIFIER OF RECORD: F-HX NOT FIRED (F-H takes no part; ruling F-H-SUPPORT)" in L, L     # F-H fired, decides nothing
    assert "FALSIFIER F-H (descriptive-only by support; decides nothing): NOT FIRED (HX2 reads RANKS-MOVE)" in verdict_lines(_fake_st(), reg)[0]
    assert "FALSIFIER OF RECORD: F-HX NOT FIRED (F-H takes no part; ruling F-H-SUPPORT)" in verdict_lines(_fake_st(), reg)[0]
    assert "-> RANKS-MOVE (descriptive-only by support) (S_w 0.9000)" in _line(verdict_lines(_fake_st(), reg)[0], "HX2 (MATH")
    # DELTA 4, L-H2: the HX2 rule-8 line carries the qualifier, both words, by value
    for w2_ in ("RANKS-MOVE", "RANKS-HOLD"):
        st_ = _fake_st(w2=w2_)
        oth = "RANKS-HOLD" if w2_ == "RANKS-MOVE" else "RANKS-MOVE"
        assert _line(verdict_lines(st_, reg)[0], "  RULE 8 (HX2, HX-R5): ") == (
            "  RULE 8 (HX2, HX-R5): %s would be refuted by %s's observable; observed tau-b %s, max shift %s: %s is not refuted"
            " (descriptive-only by support)" % (w2_, oth, _f(st_["hx2"]["min_tau"]), _f(st_["hx2"]["max_shift"], "%.1f"), w2_))
    L, w = verdict_lines(_fake_st(sw=0.7999), reg)
    assert "(fragile; S_w 0.7999" in "\n".join(L)
    st = _fake_st(w1="RANKS-MOVE", t1=0.9, s1=2.5)
    L, w = verdict_lines(st, reg)
    t = "\n".join(L)
    assert ("RULE 8 (HX1): RANKS-MOVE is not refuted (a pair below tau-b 0.85 or a model moving more than 2 ranks)" in L
            and "RANKS-MOVE is REFUTED" not in t and "HX-R4" not in t and "REGISTRATION DEFECT" not in t and w["HX1"] == "RANKS-MOVE"), t
    L, w = verdict_lines(_fake_st(w1="RANKS-HOLD", t1=0.85, s1=2.0), reg)
    assert "RULE 8 (HX1): RANKS-MOVE is REFUTED (every pair tau-b >= 0.85 and no model moves more than 2 ranks)" in L, L
    # T-1 (READY delta 2, H03 / H04): the real accuracies of _t1_sets through set_word, then verdict_lines
    for kind in ("nonfirst", "nan"):
        acc, names = _t1_sets(kind)
        h = set_word(acc, names, reg)
        assert h["word"] == "RANKS-MOVE" and h["max_shift"] <= 2.0, (kind, h)
        assert rule8_hx1(h, reg) is False and rule8_hx1(h, reg) == (h["word"] == "RANKS-HOLD"), kind
        st = _fake_st()
        st["hx1"] = dict(h, sw=0.9, lo=0.0, hi=1.0, sd=0.05)
        L, w = verdict_lines(st, reg)
        assert ("RULE 8 (HX1): RANKS-MOVE is not refuted (a pair below tau-b 0.85 or a model moving more than 2 ranks)" in L
                and w["HX1"] == "RANKS-MOVE" and "FALSIFIER OF RECORD: F-HX NOT FIRED (F-H takes no part; ruling F-H-SUPPORT)" in L), (kind, L)
    st = _fake_st()
    L = pred_lines(st, dict(HX1="RANKS-MOVE", HX2="RANKS-MOVE", HX3="RANKS-HOLD", HX4="SHIFT-MATERIAL", HX5="FORMAT-DOMINATED"), reg)
    t = "\n".join(L)
    assert "PREDICTION P1 (HX1): word RANKS-MOVE, Brier %.4f" % (2 * 0.03 ** 2) in t
    assert "min pairwise tau-b (pair X0-MF) 0.3000 in [-0.2000, 0.7000]: HELD" in t and "max rank shift 9.0 in [10.0, 17.0]: FAILED" in t
    assert "word RANKS-MOVE, Brier %.4f (RANKS-MOVE 0.75)" % (2 * 0.25 ** 2) in t and "word RANKS-HOLD, Brier %.4f (RANKS-HOLD 0.55)" % (2 * 0.45 ** 2) in t
    assert "models clearing 0.02 1 in [2, 4]: FAILED" in t and "max |acc_MF - acc_H| 0.0500 in [0.0700, 0.1200]: FAILED" in t
    assert "format share 0.6000 in [0.8500, 0.9300]: FAILED; word FORMAT-DOMINATED, Brier %.4f" % (2 * 0.03 ** 2) in t
    assert "max |acc_IS - acc_IL| over models 0.0300 in [0.0200, 0.1000]: HELD" in t


def st_support():
    """support_lines by value on a hand-made st / data: SD, DEFF = SD^2 / SD_iid^2, n_eff, MDE80 = 2.8 SD, both verdict words."""
    reg = dict(REG)
    data = dict(kept={MATH: list(range(10)), IFEVAL: list(range(4))}, clM=np.array([0, 0, 1, 2, 3, 4, 5, 6, 7, 8]),
                clI=np.array([0, 1, 2, 3]), models=["a", "b", "c"], dis_rows=[(0, 5), (1, 0)], catq=np.zeros((10, 7)))
    data["catq"][0, 5] = 1
    data["catq"][1, 0] = 1
    hx = lambda t, sd, si: dict(min_tau=t, sd=sd, sd_iid=si)      # noqa: E731
    st = dict(hx1=hx(0.30, 0.02, 0.01), hx2=hx(0.86, 0.02, 0.02), hx3=hx(0.90, 0.10, 0.05), d_mf_h=np.array([0.01, -0.05, 0.0]),
              d_mf_h_sd=np.array([0.001, 0.01, 0.0]), d_mf_h_sd_iid=np.array([0.001, 0.005, 0.0]), format=0.6, fmt_sd=0.05, fmt_sd_iid=0.025)
    t = "\n".join(support_lines(st, data, reg))
    assert ("HX1 min tau-b: point 0.3000 vs bar 0.8500; bootstrap SD 0.0200; DEFF 4.0000 (component / i.i.d. bootstrap variance);"
            " n_eff = 10 / 4.0000 = 2; MDE80 = 2.8 x SD = 0.0560; |point - bar| 0.5500 -> SCOREABLE") in t, t
    assert "HX2 tau-b: point 0.8600 vs bar 0.8500; bootstrap SD 0.0200; DEFF 1.0000" in t and "|point - bar| 0.0100 -> DESCRIPTIVE-ONLY" in t
    assert "HX3 min tau-b: point 0.9000" in t and "n_eff = 4 / 4.0000 = 1; MDE80 = 2.8 x SD = 0.2800; |point - bar| 0.0500 -> DESCRIPTIVE-ONLY" in t
    assert "HX4 acc_MF - acc_H of b (the largest |shift|): point 0.0500 vs bar 0.0200; bootstrap SD 0.0100; DEFF 4.0000" in t
    assert "HX5 format share: point 0.6000 vs bar 0.5000; bootstrap SD 0.0500; DEFF 4.0000" in t and "n_eff = 2 / 4.0000 = 0;" in t
    # the registered plan rows (Support (d)-(f) as re-derived 2026-10-09, S-1), by value against an independent recomputation
    for n, nm in ((1324, "HX1"), (1324, "HX2"), (541, "HX3")):
        se = max(0.0337, 0.03374 * math.sqrt(2056.0 / n))
        row = [r for r in SUPPORT_PLAN if r[0] == nm][0]
        assert row[4] == round(se, 4) and row[5] == round(2.8 * se, 3), (nm, row, se)
    assert round(2.8 * 0.0337, 3) == 0.094 and [r[4:6] for r in SUPPORT_PLAN[3:]] == [(0.0095, 0.027), (0.0072, 0.020)]
    want = (("HX1", "0.35 vs bar 0.85 (margin 0.500; MDE80 0.094 at the floor; the shift clause is a count, 15 against 2): SCOREABLE"),
            ("HX2", "0.92 vs bar 0.85 (margin 0.070; inside MDE80 0.094-0.118; the shift clause, 3 against 2, has no measured SE and a"
                    " one-rank margin): DESCRIPTIVE-ONLY (by support)"),
            ("HX3", "0.88 vs bar 0.85 (margin 0.030; unchanged): DESCRIPTIVE-ONLY"),
            ("HX4", "0.099 vs bar 0.02 (margin 0.079; unchanged): SCOREABLE"), ("HX5", "0.9 vs bar 0.5 (margin 0.400; unchanged): SCOREABLE"))
    se_t = {"HX1": "SE 0.0420; MDE80 0.118", "HX2": "SE 0.0420; MDE80 0.118", "HX3": "SE 0.0658; MDE80 0.184", "HX4": "SE 0.0095; MDE80 0.027",
            "HX5": "SE 0.0072; MDE80 0.020"}
    tr = "DEFF carried by the transported realised SD; n_eff not entering"
    dn = {"HX1": tr, "HX2": tr, "HX3": tr, "HX4": "DEFF 1.2; n_eff 1,103 per model", "HX5": "DEFF 3.0; n_eff 1,727"}
    tl = t.split(chr(10))
    for nm, tail in want:
        ln = _line(tl, "    %s: " % nm)
        assert ln.endswith("; %s; %s; predicted %s" % (dn[nm], se_t[nm], tail)), (nm, ln)
    assert plan_word("HX2", 0.92, 0.85, 0.094) == "DESCRIPTIVE-ONLY (by support)" and plan_word("HX1", 0.85 + 0.118, 0.85, 0.118) == "SCOREABLE"
    assert plan_word("HX3", 0.88, 0.85, 0.184) == "DESCRIPTIVE-ONLY"
    assert ("    SE(tau) for HX1-HX3 = 0.03374 x sqrt(2056 / n), floor 0.0337 (SATURATION-IRT's realised SD; TRANSPORT ASSUMPTION:") in t, t
    assert ("    F-H (fires iff HX2 reads RANKS-HOLD): descriptive-only by support, decides nothing; F-HX is the falsifier of record"
            " (ruling F-H-SUPPORT)") in t, t
    assert ("MATH 10 questions (9 components, Kish %.4f) x 3 models; IFEval 4 prompts (4 components, Kish 1.0000); 3 ranked models, 3"
            " pairs; HX5 2 X0-vs-MF disagreement rows on 2 questions (1.00 rows per affected question)" % (12.0 / 10)) in t, t


def st_refusals():
    import tempfile

    def first_math(sp):
        return sp["math_all"][0]

    def dup(sp):
        sp["nopk"] = True
        sp["extra_rows"].append(((first_math(sp), "m00"), ("dup", 0)))

    def mf_missing(sp):
        sp["mfv"][(first_math(sp), "m01")] = None

    def mf_bad(sp):
        sp["mfv"][(first_math(sp), "m01")] = 2

    def nt_missing(sp):
        sp["nt"][(first_math(sp), "m02")] = None

    def h_route(sp):
        k = [k for k in sorted(sp["h"]) if sp["cells"][k][1] == 0][0]
        sp["h"][k] = (1, "imported")

    def h_value(sp):
        k = [k for k in sorted(sp["h"]) if sp["h"][k] == (0, "none")][0]
        sp["h"][k] = (1, "boxed:str")

    def h_crlf(sp):
        sp["h_crlf"] = True

    def roster(sp):
        for q in sp["math_all"] + sp["if_all"]:
            sp["extra_rows"].append(((q, "m18"), ("r", 0)))

    def counts(sp):
        sp["drop_rows"].append((first_math(sp), "m03"))

    def incomplete(sp):                     # m04 loses a kept question's row and gains one on the dropped duplicate's twin id
        sp["drop_rows"].append((first_math(sp), "m04"))
        sp["extra_rows"].append(((sp["dup"] + 1000, "m04"), ("x", 0)))
        sp["qids"].append(sp["dup"] + 1000)
        sp["text"][sp["dup"] + 1000], sp["src"][sp["dup"] + 1000], sp["up"][sp["dup"] + 1000] = "zz extra", "MATH", 1
        sp["tgt"][sp["dup"] + 1000] = "1"

    def raw_resp(sp):
        sp["raw_resp"][(sp["if_all"][0], "m05")] = "a different response"

    def raw_skip(sp):
        sp["raw_skip"] = [(sp["if_all"][0], "m06")]

    def raw_drop(sp):
        sp["raw_drop"] = ["m07"]

    def raw_two(sp):
        sp["raw_two"] = ["m08"]
    cases = [("twins", None, dict(twins_ids=3), "R1 twins 2 / 2 != the registered 3 / 2", ("--run",)),
             ("roster", roster, None, "roster check failed (MATH 19", ("--run", "--dry-run")),
             ("counts", counts, None, "rows per model differ", ("--run", "--dry-run")),
             ("dup", dup, None, "carries more than one eval_results row", ("--run",)),
             ("mf_missing", mf_missing, None, "eval_results_mathfix.is_correct is None", ("--run",)),
             ("mf_bad", mf_bad, None, "eval_results_mathfix.is_correct is 2", ("--run",)),
             ("nt_missing", nt_missing, None, "has no checker_answers_v2 row", ("--run",)),
             ("h_pin", None, "pin", "not the pinned " + "0" * 64, ("--run", "--dry-run")),
             ("h_crlf", h_crlf, None, "carries CR bytes", ("--run", "--dry-run")),
             ("h_rows", None, "rows", "the H table holds", ("--run",)),
             ("h_route", h_route, None, "rows whose route contradicts X0", ("--run",)),
             ("h_value", h_value, None, "rows whose H != the pinned h_score", ("--run",)),
             ("incomplete", incomplete, None, "lacks model m04's row", ("--run",)),
             ("raw_resp", raw_resp, None, "the sample file's prompt / response differ", ("--run",)),
             ("raw_skip", raw_skip, None, "has no row in the sample file", ("--run",)),
             ("raw_drop", raw_drop, None, "expected exactly one IFEval sample file for m07", ("--run", "--dry-run")),
             ("raw_two", raw_two, None, "expected exactly one IFEval sample file for m08 under", ("--run",))]
    for name, mut, over, want, modes_ in cases:
        for mode_ in modes_:
            d = tempfile.mkdtemp(prefix="hx_ref_")
            try:
                sp = _spec(kind="hold", seed=3, n_m=40, n_i=14, mutate=mut)
                cfg = _layout(d, sp, reg_over=over if isinstance(over, dict) else None)
                if over == "pin":
                    cfg.h_pin = "0" * 64
                if over == "rows":
                    cfg.reg["h_rows"] += 1
                rc, buf, err = _main(cfg, [mode_])
                assert err is not None and want in err, (name, mode_, err)
                assert not any(x.startswith(("HX1", "HX2", "HX5", "PREDICTION", "SUPPORT")) for x in buf), (name, "a statistic")
                assert not os.path.exists(cfg.out_dir) and not os.path.exists(cfg.blog_dir), (name, "written")
                if name in ("h_pin", "h_crlf", "h_rows"):
                    assert not any(x.startswith(("R1:", "MATH scorer:")) for x in buf), (name, "read past an unpinned H table")
            finally:
                _rm(d)
    d = tempfile.mkdtemp(prefix="hx_busy_")
    try:
        cfg = _layout(d, _spec(kind="hold", seed=3, n_i=14))
        with open(cfg.busy, "w", encoding="utf-8") as f:
            f.write("exit 0\n")
        for mode_ in ("--run", "--dry-run"):
            rc, buf, err = _main(cfg, [mode_])
            assert err and "exited 0" in err and not buf, (mode_, err)
        cfg.busy = os.path.join(d, "absent.ps1")
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "is absent" in err, err
        cfg.busy = os.path.join(d, "busy_free.ps1")
        with open(cfg.busy, "w", encoding="utf-8") as f:
            f.write("exit 1\n")

        def touch():
            with open(cfg.mc_db, "ab") as f:
                f.write(b"x")
        cfg.during_read = touch
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "the multicorpus DB changed during the read" in err, err
        assert not os.path.exists(cfg.out_dir)
    finally:
        _rm(d)


def st_dry_run():
    import tempfile
    d = tempfile.mkdtemp(prefix="hx_dry_")
    try:
        cfg = _layout(d, _spec(kind="move", seed=7, n_i=14))
        rc, buf, err = _main(cfg, ["--dry-run"])
        assert err is None, err
        assert buf[0].startswith("POOL %s verified" % cfg.reg["r1_pool"])
        assert not any(x.startswith(("HX", "PREDICTION", "SUPPORT", "DESCRIPTIVE", "  H-L", "  SENSITIVITY")) for x in buf), "a statistic"
        assert buf[-1].startswith("DRY-RUN: no scorer column was selected") and any(x.startswith("PLANNED: B 200") for x in buf)
        assert buf[-1] == ("DRY-RUN: no scorer column was selected from the DB views (the tripwire sealed %s); the IFEval sample"
                           " files' strict / loose verdict fields were parsed into memory for the join and not printed; no statistic"
                           " printed; nothing written." % ", ".join(KEY_SEAL)), buf[-1]
        assert not os.path.exists(cfg.out_dir) and not os.path.exists(cfg.blog_dir), "the dry-run wrote"
        # DELTA 4, S-1: the schema block, one line per declared column, before the first row read (R1), by value
        sc = [i for i, x in enumerate(buf) if x.startswith("  schema: ")]
        si = [i for i, x in enumerate(buf) if x.startswith("SCHEMA CONFORMANCE (S-1): 15 columns in 4 tables named by 6 statements")]
        r1 = [i for i, x in enumerate(buf) if x.startswith("R1: ")]
        assert len(sc) == 15 and len(si) == 1 and sc == list(range(si[0] - 15, si[0])) and si[0] < r1[0], (sc, si, r1)
        assert [buf[i] for i in sc] == ["  schema: %s %s.%s present (PRAGMA table_info cid %d, %s)" % (
            "mc.db" if a == "mc" else "ck.db", t, c_, cid, typ) for (a, t, c_), cid, typ in zip(RUN_COLUMNS, (
                0, 1, 2, 5, 7, 0, 1, 7, 8, 0, 1, 2, 0, 1, 11), ("INTEGER", "TEXT", "INTEGER", "TEXT", "TEXT", "INTEGER", "TEXT", "TEXT",
                                                               "INTEGER", "INTEGER", "TEXT", "INTEGER", "INTEGER", "TEXT", "INTEGER"))], buf[sc[0]:si[0]]
        tw = G.KeyTripwire(PG.open_ro(cfg.mc_db), (), key=KEY_SEAL, label="t")
        try:
            tw.execute("SELECT model_output FROM eval_results")
            raise AssertionError("a scorer column read while sealed")
        except SystemExit as e:
            assert "SEALED" in str(e)
        finally:
            tw.close()
    finally:
        _rm(d)


# the real schema's columns the statements read, written out by hand from sqlite_master (2026-10-09), NOT from RUN_COLUMNS
REAL_READS = {("multicorpus_cache_v1.db", "corpus_questions", c) for c in ("question_id", "source", "upstream_id", "text", "target")} | \
    {("multicorpus_cache_v1.db", "eval_results", c) for c in ("question_id", "model_name", "model_output", "is_correct")} | \
    {("multicorpus_cache_v1.db", "eval_results_mathfix", c) for c in ("question_id", "model_name", "is_correct")} | \
    {("checker_answers_v2.db", "math_checker_answers_v2", c) for c in ("question_id", "model_name", "non_terminated")}


def st_schema():
    """DELTA 4 (POSTRUN F-1 / F-2 / S-1). (a) the built fixture's tables equal the REAL ones (sqlite_master text and PRAGMA
    table_info, the real DBs re-opened here, mode=ro&immutable=1); (b) schema_check on the REAL DBs: one line per column, the
    exact 15 (table, column) reads of a hand-written oracle, the count line by value; (c) each gate isolated, by its message:
    G1 (a declared column absent), G2 (a statement naming the invented column while the declaration is right), G3 (a statement
    reading a column the declaration lacks); (d) main --dry-run and --run on a fixture whose eval_results_mathfix carries the
    invented column REFUSE at G1 before any row is read, nothing written; (e) the seal: a sealed tripwire refuses every scorer
    statement (the corrected MATH-FIX SELECT included) and admits the others."""
    import sqlite3
    import tempfile
    d = tempfile.mkdtemp(prefix="hx_schema_")
    try:
        cfg = _layout(os.path.join(d, "ok"), _spec(kind="hold", seed=3, n_i=14))
        n_tab = 0
        for fx, rel, tabs in ((cfg.mc_db, MC_REL, FX_MC_TABLES), (cfg.ck_db, CK_REL, FX_CK_TABLES)):
            rc_ = PG.open_ro(os.path.join(PG.DATA_ROOT, rel))
            fc = sqlite3.connect(fx)
            try:
                for t in tabs:
                    a = fc.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (t,)).fetchone()
                    b = rc_.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?", (t,)).fetchone()
                    assert a is not None and b is not None and a[0] == b[0], ("F-2: fixture DDL != real", t, a, b)
                    pa = fc.execute('PRAGMA table_info("%s")' % t).fetchall()
                    pb = rc_.execute('PRAGMA table_info("%s")' % t).fetchall()
                    assert pa == pb and pa, ("F-2: fixture columns != real", t, pa, pb)
                    n_tab += 1
            finally:
                fc.close()
                rc_.close()
        assert n_tab == 5, n_tab
        # (b) the REAL DBs
        rcfg = real_cfg()
        L = schema_check({"mc": rcfg.mc_db, "ck": rcfg.ck_db})
        cl = [x for x in L if x.startswith("  schema: ")]
        got = set()
        for x in cl:
            m = re.match(r"  schema: (\S+) (\w+)\.(\w+) present \(PRAGMA table_info cid \d+, (\w+)\)$", x)
            assert m, x
            got.add(m.groups()[:3])
        assert len(cl) == 15 and got == REAL_READS, ("S-1 real", sorted(got ^ REAL_READS), len(cl))
        assert L[-1].startswith("SCHEMA CONFORMANCE (S-1): 15 columns in 4 tables named by 6 statements (--run and --dry-run) checked"
                                " against "), L[-1]
        assert L[-1].endswith("all present; the declared set equals the statements' reads") and "multicorpus_cache_v1.db" in L[-1], L[-1]
        assert ("  schema: multicorpus_cache_v1.db eval_results_mathfix.is_correct present (PRAGMA table_info cid 2, INTEGER)") in L, L
        assert not [x for x in L if "is_correct_mathfix" in x]
        # (c) the gates, isolated, on the fixture DBs
        dbs = {"mc": cfg.mc_db, "ck": cfg.ck_db}
        bad_sql = dict(RUN_SQL, mf=("mc", "SELECT f.question_id, f.model_name, f.is_correct_mathfix FROM eval_results_mathfix f JOIN"
                                          " corpus_questions c USING(question_id) WHERE c.source = ?", ("MATH",)))
        for kw, want in ((dict(cols=RUN_COLUMNS + (("mc", "eval_results_mathfix", "is_correct_mathfix"),)),
                          "SCHEMA (S-1, G1 DECLARED): mc.db eval_results_mathfix.is_correct_mathfix is not a column of the real table"
                          " (PRAGMA table_info: ['is_correct', 'model_name', 'question_id'])"),
                         (dict(sql=bad_sql), "SCHEMA (S-1, G2 COMPILE): statement 'mf' does not compile on mc.db: no such column:"
                                             " f.is_correct_mathfix"),
                         (dict(sql=dict(RUN_SQL, extra=("mc", "SELECT category FROM eval_results", ()))),
                          "SCHEMA (S-1, G3 READS): the statements read [('mc', 'eval_results', 'category')] but RUN_COLUMNS declares"
                          " nothing more"),
                         (dict(cols=RUN_COLUMNS + (("mc", "eval_results", "category"),)),
                          "SCHEMA (S-1, G3 READS): the statements read nothing more but RUN_COLUMNS declares [('mc', 'eval_results',"
                          " 'category')]")):
            try:
                schema_check(dbs, **kw)
                raise AssertionError("schema_check passed %r" % sorted(kw))
            except SystemExit as e:
                assert str(e) == "%s REFUSED: %s" % (TAG, want), (str(e), want)
        Lf = schema_check(dbs)
        assert len([x for x in Lf if x.startswith("  schema: mc.db ")]) == 12 and len([x for x in Lf if x.startswith("  schema: ck.db ")]) == 3, Lf
        # (d) the invented column in the DB the script reads: --dry-run and --run refuse at G1, before any row is read
        for mode_ in ("--dry-run", "--run"):
            sp = _spec(kind="hold", seed=3, n_i=14, mutate=lambda q: q.__setitem__("schema_drift", True))
            cfg2 = _layout(os.path.join(d, "drift" + mode_), sp)
            rc, buf, err = _main(cfg2, [mode_])
            assert err == ("%s REFUSED: SCHEMA (S-1, G1 DECLARED): mc.db eval_results_mathfix.is_correct is not a column of the real"
                           " table (PRAGMA table_info: ['is_correct_mathfix', 'model_name', 'question_id'])" % TAG), (mode_, err)
            assert buf[0].startswith("POOL ") and not any(x.startswith(("R1:", "  roster", "HX", "PREDICTION", "SCHEMA CONFORMANCE"))
                                                          for x in buf), (mode_, buf)
            assert not os.path.exists(cfg2.out_dir) and not os.path.exists(cfg2.blog_dir), (mode_, "written")
        # (e) the seal covers the corrected column
        tw = G.KeyTripwire(PG.open_ro(cfg.mc_db), (), key=KEY_SEAL, label="t")
        tk = G.KeyTripwire(PG.open_ro(cfg.ck_db), (), key=KEY_SEAL, label="t")
        try:
            for name, (lab, q, _p) in sorted(RUN_SQL.items()):
                conn = tw if lab == "mc" else tk
                try:
                    conn.execute(q, _p)
                    refused = False
                except SystemExit as e:
                    refused = "SEALED" in str(e)
                assert refused == (name in ("ev", "mf", "ck")), (name, refused)
        finally:
            tw.close()
            tk.close()
    finally:
        _rm(d)


def st_branch_cover():
    missing = [b for b in BRANCHES if not HIT[b]]
    assert not missing, "print branches never executed: %s" % missing


SELF_NAME = "harness_extractor"


def st_busyself():
    """B2 / B-1 (delta 2026-10-09): the rule-7 check never matches its own caller, and hides nothing else.
    REAL busy.ps1 (BUSY_PS1, unmodified): a live probe process whose argv names this script; with no exclusion (PID -1) busy.ps1
    exits 0 and the probe is in its scan (the self-match is real, so the test is not vacuous); with the probe's PID the probe
    AND this process (its parent) are excluded, neither is in the scan, and the exit code equals an independent oracle (busy iff
    a java process or a remaining python whose command line matches busy.ps1's own -match pattern; a race retries).
    SANDBOX copies of busy.ps1 (its own code, the pattern replaced by a unique token, the java line neutralised): through the
    ENTRY POINT busy_check, the probe's PID frees (its chain printed first), PID -1 and the default (this process: the probe is
    a CHILD, not an ancestor) refuse; a token matching nothing frees with this process first in the printed chain."""
    import re
    import tempfile
    assert os.path.isfile(BUSY_PS1), "the real busy.ps1 is required (%s)" % BUSY_PS1
    real = open(BUSY_PS1, encoding="utf-8-sig").read()
    pats = re.findall(r"-match '([^']+)'", real)
    assert len(pats) == 1 and re.search(pats[0], SELF_NAME, re.I), ("busy.ps1 no longer names this script", pats)
    pat = pats[0]
    tok = "%s_selftest_probe_%d" % (SELF_NAME, os.getpid())
    d = tempfile.mkdtemp(prefix="busyself_")
    probe = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)", tok],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        def pids(info):
            return set(int(r["pid"]) for r in info["returned"])
        rc0, i0 = busy_probe(BUSY_PS1, -1)
        assert i0 is not None and rc0 == 0 == i0["rc"] and i0["excluded"] == [] and probe.pid in pids(i0), ("self-match", rc0, i0)
        got = None
        for _attempt in range(3):
            rc1, i1 = busy_probe(BUSY_PS1, probe.pid)
            assert i1 is not None and i1["rc"] == rc1 and i1["calls"] >= 1, (rc1, i1)
            ex = [int(x) for x in i1["excluded"]]
            assert ex[0] == probe.pid and os.getpid() in ex, ("own chain", ex, os.getpid())
            assert not (set(ex) & pids(i1)), ("an excluded PID reached busy.ps1", ex)
            want = 0 if (int(i1["java"]) > 0 or any(re.search(pat, r["cmd"] or "", re.I) for r in i1["returned"])) else 1
            got = rc1
            if got == want:
                break
        assert got == want, ("busy.ps1 with the chain excluded vs the oracle", got, want)
        sb = os.path.join(d, "busy_sandbox.ps1")
        nb = os.path.join(d, "busy_nothing.ps1")
        jl = [ln for ln in real.splitlines() if ln.lstrip().startswith("$j = Get-Process java")]
        assert len(jl) == 1, jl
        for p, t in ((sb, re.escape(tok)), (nb, "no_such_process_token_%d" % os.getpid())):
            with open(p, "w", encoding="utf-8") as f:
                f.write(real.replace("'%s'" % pat, "'%s'" % t).replace(jl[0], "$j = $null"))
        line = busy_check(sb, pid=probe.pid)
        assert ("excluded: PIDs %d,%d" % (probe.pid, os.getpid())) in line, line
        for kw in (dict(pid=-1), {}):
            try:
                busy_check(sb, **kw)
                raise AssertionError("busy_check freed with the probe visible %r" % kw)
            except SystemExit as e:
                assert "%s exited 0" % sb in str(e), (kw, str(e))
        line = busy_check(nb)
        assert ("excluded: PIDs %d," % os.getpid()) in line or line.endswith("excluded: PIDs %d" % os.getpid()), line
        # fail-closed: a throw, no exit code, an exit that bypasses the report
        for body, msg in (("throw 'x'", "exited 3"), ("$null = 1", "exited 99"), ("[Environment]::Exit(1)", "without the self-exclusion report")):
            with open(sb, "w", encoding="utf-8") as f:
                f.write(body + "\n")
            try:
                busy_check(sb, pid=probe.pid)
                raise AssertionError("busy_check freed on %r" % body)
            except SystemExit as e:
                assert msg in str(e), (body, str(e))
    finally:
        probe.kill()
        probe.wait()
        _rm(d)


CASES = (("pure", st_pure), ("copy", st_copy), ("verdicts", st_verdicts), ("run_e2e", st_run_e2e), ("refusals", st_refusals),
         ("dry_run", st_dry_run), ("support", st_support), ("schema", st_schema), ("busyself", st_busyself),
         ("branches", st_branch_cover))


def selftest(only=None, quiet=False):
    import tempfile
    import scratch_dir   # noqa: F401  TEMP-SPRAWL: temp on E:, removed at exit
    assert tempfile.gettempdir()
    HIT.clear()
    fails, ran = [], 0
    for name, fn in CASES:
        if only and name not in only:
            continue
        if name == "branches" and only:
            continue
        ran += 1
        t0 = time.time()
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
            if not quiet:
                print("  ok   %-10s (%.1f s)" % (name, time.time() - t0), flush=True)
        except BaseException as e:   # noqa: B902
            fails.append(name)
            if quiet:
                break
            import traceback
            print("  FAIL %-10s %s: %s" % (name, type(e).__name__, str(e)[:900]), flush=True)
            traceback.print_exc()
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(only=None):
    import tempfile
    import scratch_dir   # noqa: F401
    mark = NL + "# " + chr(0x2550) * 2 + " SELFTEST"
    path = os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    cut = src.index(mark)
    rows, bad = [], []
    assert tempfile.gettempdir()
    for name, old, new in MUTANTS:
        if only and not any(name.startswith(o) for o in only):
            continue
        head = src[:cut]
        if old and head.count(old) != 1:
            bad.append(name)
            rows.append((name, "NOT APPLIED (%d matches)" % head.count(old)))
            print("  %-78s NOT APPLIED (%d matches)" % (name, head.count(old)), flush=True)
            continue
        t0 = time.time()
        try:
            mod = types.ModuleType("harness_extractor_mutant")
            mod.__file__ = path
            exec(compile((head.replace(old, new) if old else head) + src[cut:], path, "exec"), mod.__dict__)
            with contextlib.redirect_stdout(io.StringIO()):
                mod.selftest(quiet=True)
            res = "SURVIVED"
        except BaseException as e:   # noqa: B902
            res = "KILLED (%s)" % type(e).__name__
        rows.append((name, res))
        print("  %-78s %s (%.0f s)" % (name, res, time.time() - t0), flush=True)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied %s" % (
        TAG, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "", ""),
    # HX1-HX3: the rule, its edges, min<->max, first-pair-only, the wrong set / population
    ("X01 tau-b bar strict (>)", 'hold = bool(round(mt, 12) >= reg["tau_bar"] and', 'hold = bool(round(mt, 12) > reg["tau_bar"] and'),
    ("X02 shift bar strict (<)", 'and ms <= reg["shift_bar"])', 'and ms < reg["shift_bar"])'),
    ("X03 min tau-b -> max (min<->max)", '    mt = min((p[2] if not math.isnan(p[2]) else float("-inf")) for p in pairs)',
     '    mt = max((p[2] if not math.isnan(p[2]) else float("-inf")) for p in pairs)'),
    ("X04 max shift -> min (min<->max)", '    ms = max(p[3] for p in pairs)', '    ms = min(p[3] for p in pairs)'),
    ("X05 first pair only (first-site-only)", '    for a, b in itertools.combinations(names, 2):', '    for a, b in list(itertools.combinations(names, 2))[:1]:'),
    ("X06 HX1 without H", '    st["hx1"] = set_word(accM, SM, reg)', '    st["hx1"] = set_word(accM, ("X0", "MF"), reg)'),
    ("X07 HX2 on X0-H", '    st["hx2"] = set_word(accM, ("MF", "H"), reg)', '    st["hx2"] = set_word(accM, ("X0", "H"), reg)'),
    ("X08 HX3 on the MATH scorers (wrong population)", '    st["hx3"] = set_word(accI, SI, reg)',
     '    st["hx3"] = set_word(dict(I0=accM["X0"], IS=accM["MF"], IL=accM["H"]), SI, reg)'),
    ("X09 ties at the best rank, not mid-rank", '    return 1.0 + gt + (eq - 1) / 2.0', '    return 1.0 + gt'),
    ("X10 rank 1 = the lowest accuracy", '    gt = (a[None, :] > a[:, None]).sum(1)', '    gt = (a[None, :] < a[:, None]).sum(1)'),
    ("X11 tau-a denominator", '    den = math.sqrt(float((sx != 0).sum()) * float((sy != 0).sum()))', '    den = float(len(sx))'),
    ("X12 an undefined tau-b counts as 1", '    mt = min((p[2] if not math.isnan(p[2]) else float("-inf")) for p in pairs)',
     '    mt = min((p[2] if not math.isnan(p[2]) else 1.0) for p in pairs)'),
    ("X13 B-2: rule 8 at the superseded bar (< 3)", 'and hx["max_shift"] <= reg["shift_bar"])', 'and hx["max_shift"] < 3.0)'),
    ("X14 rule 8 ignores the tau-b clause", 'return bool(all(round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"]) and hx["max_shift"]',
     'return bool(True and hx["max_shift"]'),
    ("X15 B-2: rule 8 strict (< 2)", 'and hx["max_shift"] <= reg["shift_bar"])', 'and hx["max_shift"] < reg["shift_bar"])'),
    ("X16 stable at S_w > 0.80 (boundary)", '    stable = bool(h1["sw"] >= reg["sw_bar"])', '    stable = bool(h1["sw"] > reg["sw_bar"])'),
    ("X17 S_w of every criterion from HX1's replicates", '        st[k]["sw"] = float(np.mean([r[k]["word"] == st[k]["word"] for r in comp]))',
     '        st[k]["sw"] = float(np.mean([r["hx1"]["word"] == st[k]["word"] for r in comp]))'),
    ("X18 F-HX inverted", '    if h1["word"] == "RANKS-HOLD":' + NL + '        hit("FHX.FIRED")', '    if h1["word"] != "RANKS-HOLD":' + NL + '        hit("FHX.FIRED")'),
    ("X19 F-H read on HX1", '    if h2["word"] == "RANKS-HOLD":' + NL + '        hit("FH.FIRED")', '    if h1["word"] == "RANKS-HOLD":' + NL + '        hit("FH.FIRED")'),
    # HX4
    ("X20 HX4 bound inclusive (>=)", 'bool(a > reg["hx4_bar"]) or bool(b < -reg["hx4_bar"])', 'bool(a >= reg["hx4_bar"]) or bool(b < -reg["hx4_bar"])'),
    ("X21 HX4 one-sided (negative shifts ignored)", 'bool(a > reg["hx4_bar"]) or bool(b < -reg["hx4_bar"])', 'bool(a > reg["hx4_bar"])'),
    ("X22 HX4 on the point, not the interval", 'st["hx4"], st["hx4_n"] = hx4_word(st["d_mf_h_lo"], st["d_mf_h_hi"], reg)',
     'st["hx4"], st["hx4_n"] = hx4_word(st["d_mf_h"], st["d_mf_h"], reg)'),
    ("X23 HX4 on X0 - MF (wrong pair)", '    st["d_mf_h"] = accM["MF"] - accM["H"]', '    st["d_mf_h"] = accM["X0"] - accM["MF"]'),
    ("X24 HX4 interval 5 / 95", '        st[key + "_lo"] = np.percentile(arr, 2.5, axis=0)', '        st[key + "_lo"] = np.percentile(arr, 5.0, axis=0)'),
    # HX5
    ("X25 format set without EQUIV", 'FORMAT = ("BOXED_no_minerva_sentence", "FORMAT_minerva_present_norm_mismatch", "EQUIV_numeric_form")',
     'FORMAT = ("BOXED_no_minerva_sentence", "FORMAT_minerva_present_norm_mismatch")'),
    ("X26 HX5 bar strict (>)", 'return "FORMAT-DOMINATED" if bool(fs >= reg["hx5_bar"]) else "MIXED"', 'return "FORMAT-DOMINATED" if bool(fs > reg["hx5_bar"]) else "MIXED"'),
    ("X27 HX5 over the MF-vs-H disagreements (wrong population)", '            if x0 != mfx:' + NL + '                c = CATS.index(',
     '            if mfx != h:' + NL + '                c = CATS.index('),
    ("X28 categories with nt = 0", '                c = CATS.index(categorise(out, tgt[q], ntv[(q, m)])[0])', '                c = CATS.index(categorise(out, tgt[q], 0)[0])'),
    ("X29 HX5 shares ignore the replicate weights", '    num = wM @ D["catq"]', '    num = np.ones(len(wM)) @ D["catq"]'),
    # the scorers
    ("X30 MF = X0 (MATH-FIX not read)", 'Ys["X0"][i, j], Ys["MF"][i, j], Ys["H"][i, j] = x0, mfx, h', 'Ys["X0"][i, j], Ys["MF"][i, j], Ys["H"][i, j] = x0, x0, h'),
    ("X31 H = MF (the table not read)", 'Ys["X0"][i, j], Ys["MF"][i, j], Ys["H"][i, j] = x0, mfx, h', 'Ys["X0"][i, j], Ys["MF"][i, j], Ys["H"][i, j] = x0, mfx, mfx'),
    ("X32 H-L = H (lenient addition dropped)", '            Ys["HL"][i, j] = max(h, hl_extra(out, tgt[q], q))', '            Ys["HL"][i, j] = h'),
    ("X33 H-L credits a closed think block too", '    if not resp or "<think>" not in resp or "</think>" in resp:', '    if not resp or "<think>" not in resp:'),
    ("X34 IS and IL swapped", 'Is["I0"][i, j], Is["IS"][i, j], Is["IL"][i, j] = i0, isv, ilv', 'Is["I0"][i, j], Is["IS"][i, j], Is["IL"][i, j] = i0, ilv, isv'),
    ("X35 I0 read from the sample file (stored verdict ignored)", 'Is["I0"][i, j], Is["IS"][i, j], Is["IL"][i, j] = i0, isv, ilv',
     'Is["I0"][i, j], Is["IS"][i, j], Is["IL"][i, j] = isv, isv, ilv'),
    # refusals and gates
    ("X36 H route check removed", '    if h_route_bad or h_mismatch:', '    if h_mismatch:'),
    ("X37 H value check removed", '    if h_route_bad or h_mismatch:', '    if h_route_bad:'),
    ("X38 H pin check removed", '    if sha != pin:', '    if False:'),
    ("X39 H CR check removed", '    if b"\\r" in raw:', '    if False:'),
    ("X40 H row count check removed", '    if len(H) != int(rows):', '    if False:'),
    ("X41 twins refusal removed", 'if len(tw) != reg["twins_ids"] or tw_texts != reg["twins_texts"]:', 'if False:'),
    ("X42 R1 twins kept (not dropped)", 'keep, drop = collapse(text, [q for q in sorted(text) if q not in tws])', 'keep, drop = collapse(text, sorted(text))'),
    ("X43 collapse keeps the highest id", '        lo = min(g)', '        lo = max(g)'),
    ("X44 roster check removed", '        if len(models) != reg["roster"] or models_by[MATH] != models_by[IFEVAL]:', '        if False:'),
    ("X45 rows-per-model check removed", '        if bad:' + NL + '            refuse("rows per model', '        if False:' + NL + '            refuse("rows per model'),
    ("X46 duplicate-row check removed", '                if (q, m) in ev:', '                if False:'),
    ("X47 MF presence check removed", '            if (q, m) not in mfv or mfv[(q, m)] not in (0, 1):', '            if (q, m) in mfv and mfv[(q, m)] not in (0, 1, None):'),
    ("X48 NT presence check removed", '            if (q, m) not in ntv:', '            if False:'),
    ("X49 raw join check removed", '            if prompt != text[q] or rresp != out:', '            if False:'),
    ("X50 raw one-file-per-model check removed", '        if len(fs) != 1:', '        if not fs:'),
    ("X51 busy exit 0 accepted", '    if rc != 1:', '    if rc not in (0, 1):'),
    ("X52 write-once pre-check removed", '        if os.path.exists(p):' + NL + '            refuse("%s exists: outcome', '        if False:' + NL + '            refuse("%s exists: outcome'),
    ("X53 DB sha check removed", '    if mc_after != mc_before:', '    if False:'),
    ("X54 dry-run selects the stored verdict (DELTA 4: in RUN_SQL)", '"ev_dry": ("mc", "SELECT e.question_id, e.model_name FROM eval_results e',
     '"ev_dry": ("mc", "SELECT e.question_id, e.model_name, e.is_correct FROM eval_results e'),
    ("X55 incomplete-question refusal removed (MATH)", '            if (q, m) not in ev:' + NL + '                refuse("MATH question',
     '            if False:' + NL + '                refuse("MATH question'),
    # the bootstrap
    ("X56 questions resampled, not components", '        wM = np.bincount(rng.integers(0, CM, CM), minlength=CM)[cm].astype(np.float64)',
     '        wM = np.bincount(rng.integers(0, nM, nM), minlength=nM).astype(np.float64)'),
    ("X57 component stream seed + 1", '    rng = np.random.default_rng(int(reg["seed"]))', '    rng = np.random.default_rng(int(reg["seed"]) + 1)'),
    ("X58 IFEval drawn before MATH", '        wM = np.bincount(rng.integers(0, CM, CM), minlength=CM)[cm].astype(np.float64)' + NL +
     '        wI = np.bincount(rng.integers(0, CI, CI), minlength=CI)[ci].astype(np.float64)',
     '        wI = np.bincount(rng.integers(0, CI, CI), minlength=CI)[ci].astype(np.float64)' + NL +
     '        wM = np.bincount(rng.integers(0, CM, CM), minlength=CM)[cm].astype(np.float64)'),
    ("X59 min tau-b interval 5 / 95", '        st[k]["lo"] = pctl([r[k]["min_tau"] for r in comp], 2.5)', '        st[k]["lo"] = pctl([r[k]["min_tau"] for r in comp], 5.0)'),
    ("X60 SD with ddof 0", '        st[k]["sd"] = float(np.std([r[k]["min_tau"] for r in comp], ddof=1))', '        st[k]["sd"] = float(np.std([r[k]["min_tau"] for r in comp], ddof=0))'),
    ("X61 i.i.d. stream on the component seed", '    rng2 = np.random.default_rng(int(reg["seed_iid"]))', '    rng2 = np.random.default_rng(int(reg["seed"]))'),
    ("X62 HX5 i.i.d. resample over questions, not rows", '            k = np.bincount(rng2.integers(0, len(rows), len(rows)), minlength=len(rows))',
     '            k = np.ones(len(rows), dtype=np.int64)'),
    # sensitivity, predictions, support, header
    ("X63 corrupted references not excluded", '    w_ex[data["corrupt"]] = 0.0', '    w_ex[data["corrupt"]] = 1.0'),
    ("X64 H-L sensitivity reads H", '    accL = dict(st["accM"], H=st["accM"]["HL"])', '    accL = dict(st["accM"])'),
    ("X65 P1 Brier on a fixed outcome", 'brier(PRED["P1"], w["HX1"])', 'brier(PRED["P1"], "RANKS-MOVE")'),
    ("X66 P2 read on HX2", 'h1["argmin"], h1["min_tau"], PRED["P2"])', 'h1["argmin"], h2["min_tau"], PRED["P2"])'),
    ("X67 P6 max shift signed (not |.|)", '    mx = float(np.max(np.abs(st["d_mf_h"])))', '    mx = float(np.max(st["d_mf_h"]))'),
    ("X68 P8 signed (not |.|)", 'float(np.max(np.abs(st["d_is_il"]))), PRED["P8"]', 'float(np.max(st["d_is_il"])), PRED["P8"]'),
    ("X69 bands exclusive", '    return bool(band[0] <= x <= band[1])', '    return bool(band[0] < x < band[1])'),
    ("X70 MDE80 with 1.96", '        mde = 2.8 * sd', '        mde = 1.96 * sd'),
    ("X71 DEFF inverted", '        deff = (sd * sd) / (sd_iid * sd_iid) if', '        deff = (sd_iid * sd_iid) / (sd * sd) if'),
    ("X72 HX4 support on the smallest shift", '    j = int(np.argmax(np.abs(st["d_mf_h"])))', '    j = int(np.argmin(np.abs(st["d_mf_h"])))'),
    ("X73 header says MATH-FIX beside: no", 'MATH-FIX beside: yes"', 'MATH-FIX beside: no"'),
    # DELTA (B-1)
    ("X74 B-1: self-exclusion dropped (PID -1)", 'rc, info = busy_probe(path, os.getpid() if pid is None else pid)', 'rc, info = busy_probe(path, -1)'),
    ("X75 B-1: chain starts at the parent (own PID kept)", 'rc, info = busy_probe(path, os.getpid() if pid is None else pid)', 'rc, info = busy_probe(path, os.getppid() if pid is None else pid)'),
    ("X76 B-1: own PID only (parent chain not walked)", '    $cur = $pp', '    break'),
    ("X77 B-1: exclusion hides every process", 'Where-Object { -not $global:__bx.Contains([int]$_.ProcessId) }', 'Where-Object { $false }'),
    ("X78 B-1: exit code forced free", '  exit $rc', '  exit 1'),
    ("X79 B-1: a throw exits free (fail-open)", 'exit 3 }', 'exit 1 }'),
    ("X80 B-1: no exit code reads free", '$global:LASTEXITCODE = 99', '$global:LASTEXITCODE = 1'),
    ("X81 B-1: report check removed", '    if not info or info.get("rc") != 1:', '    if False:'),
    ("X82 L-1: dry-run closing line hides the parse", "verdict fields were parsed into memory for the join and not printed; ", ""),
    # DELTA 2 (B-2, HX-R4)
    ("X83 B-2: superseded rule-8 text (>= 3)", 'or a model moving more than %.0f ranks)" % (reg["tau_bar"], reg["shift_bar"]))',
     'or a model moving >= %.0f ranks)" % (reg["tau_bar"], reg["shift_bar"] + 1))'),
    ("X84 B-2: rule 8 inverted at the print site", '    r8 = rule8_hx1(h1, reg)', '    r8 = not rule8_hx1(h1, reg)'),
    # DELTA 3 (D-3, T-1; registrar S-1 and ruling F-H-SUPPORT); H01 / H03 / H04 are the delta-2 reviewer's, verbatim
    ("H01 rule 8 tau clause strict (> 0.85)", 'return bool(all(round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"])',
     'return bool(all(round(p[2], 12) > reg["tau_bar"] for p in hx["pairs"])'),
    ("H03 rule 8 tau clause on the first pair only", 'return bool(all(round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"])',
     'return bool(all(round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"][:1])'),
    ("H04 rule 8 lets an undefined tau-b pass", 'return bool(all(round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"])',
     'return bool(all((p[2] != p[2]) or round(p[2], 12) >= reg["tau_bar"] for p in hx["pairs"])'),
    # DELTA 4 (POSTRUN F-1 / F-2 / S-1, LOW L-H1 / L-H2)
    ("X99 F-1 reverted: the MATH-FIX SELECT names the invented column", '"SELECT f.question_id, f.model_name, f.is_correct FROM eval_results_mathfix f JOIN"',
     '"SELECT f.question_id, f.model_name, f.is_correct_mathfix FROM eval_results_mathfix f JOIN"'),
    ("X100 F-1 reverted in the declaration: RUN_COLUMNS names the invented column", '("mc", "eval_results_mathfix", "is_correct"),',
     '("mc", "eval_results_mathfix", "is_correct_mathfix"),'),
    ("X101 S-1: the schema check not called", '    for ln in schema_check({"mc": cfg.mc_db, "ck": cfg.ck_db}):', '    for ln in ():'),
    ("X102 S-1: G1 (PRAGMA presence) removed", '        if col not in have:', '        if False:'),
    ("X103 S-1: G2 (compile) refusal removed", '            except sqlite3.Error as e:' + NL + '                refuse("SCHEMA (S-1, G2',
     '            except sqlite3.Error as e:' + NL + '                str("SCHEMA (S-1, G2'),
    ("X104 S-1: G3 (reads == declared) removed", '    if reads != set(cols):', '    if False:'),
    ("X105 S-1: only the first statement compiled (first-site-only)", '    for name in sql:', '    for name in list(sql)[:1]:'),
    ("X106 S-1: every statement compiled on the multicorpus DB", '        c = PG.open_ro(dbs[lab])' + NL + '        try:' + NL + '            c.set_authorizer',
     '        c = PG.open_ro(dbs["mc"])' + NL + '        try:' + NL + '            c.set_authorizer'),
    ("X107 S-1: PRAGMA read on the multicorpus DB for every table", '            c = PG.open_ro(dbs[lab])' + NL + '            try:' + NL + '                info[',
     '            c = PG.open_ro(dbs["mc"])' + NL + '            try:' + NL + '                info['),
    ("X108 S-1: the authorizer records nothing", '            if action == sqlite3.SQLITE_READ and a2:', '            if False:'),
    ("X109 F-1: the seal no longer covers is_correct", 'KEY_SEAL = ("is_correct", "model_output", "non_terminated")', 'KEY_SEAL = ("model_output", "non_terminated")'),
    ("X110 F-1: --run never unseals (the corrected SELECT refused)", '            conn.unseal("HARNESS-EXTRACTOR --run', '            str("HARNESS-EXTRACTOR --run'),
    ("X111 L-H1: HX2 released bare in the figure JSON", 'HX2=dict(word=st["hx2"]["word"], support=DESC_ONLY)', 'HX2=st["hx2"]["word"]'),
    ("X112 L-H1: HX3 released bare in the figure JSON", 'HX3=dict(word=st["hx3"]["word"], support=DESC_ONLY)', 'HX3=st["hx3"]["word"]'),
    ("X113 L-H1: the qualifier text changed", 'DESC_ONLY = "descriptive-only by support"', 'DESC_ONLY = "descriptive-only"'),
    ("X114 L-H2: the HX2 rule-8 line without the qualifier", '             " (descriptive-only by support)" % (h2["word"], other,', '             "" % (h2["word"], other,'),
    ("X85 D-3: HX1 plan SE / MDE80 superseded (0.0184 / 0.052)", '"not entering", 0.0420, 0.118, 0.35, 0.85,', '"not entering", 0.0184, 0.052, 0.35, 0.85,'),
    ("X86 D-3: HX2 plan SE / MDE80 superseded (0.0184 / 0.052)", '"not entering", 0.0420, 0.118, 0.92, 0.85,', '"not entering", 0.0184, 0.052, 0.92, 0.85,'),
    ("X87 D-3: HX3 plan SE / MDE80 superseded (0.0287 / 0.080)", '"not entering", 0.0658, 0.184, 0.88, 0.85,', '"not entering", 0.0287, 0.080, 0.88, 0.85,'),
    ("X88 D-3: plan word strict (> MDE80; boundary)", '    if bool(abs(pred - bar) >= mde):', '    if bool(abs(pred - bar) > mde):'),
    ("X89 D-3: plan word ignores MDE80 (always SCOREABLE)", '    if bool(abs(pred - bar) >= mde):', '    if True:'),
    ("X90 D-3: HX2 plan word without '(by support)'", 'return "DESCRIPTIVE-ONLY (by support)" if name == "HX2" else', 'return "DESCRIPTIVE-ONLY" if name == "HX2" else'),
    ("X91 D-3: SE(tau) line on the superseded constants", 'TAU_SD0, TAU_N0, TAU_FLOOR = 0.03374, 2056, 0.0337', 'TAU_SD0, TAU_N0, TAU_FLOOR = 0.0275, 590, 0.0337'),
    ("X92 D-3: F-H-SUPPORT plan line dropped", '    L.append("    F-H (fires iff HX2 reads RANKS-HOLD)', '    str("    F-H (fires iff HX2 reads RANKS-HOLD)'),
    ("X93 D-3: HX2 word line without the qualifier", '-> %s (descriptive-only by support) (S_w %s)"' + NL + '             " [tau-b 95%%',
     '-> %s (S_w %s)"' + NL + '             " [tau-b 95%%'),
    ("X94 D-3: F-H FIRED line scored (qualifier dropped)", 'L.append("FALSIFIER F-H (descriptive-only by support; decides nothing): FIRED',
     'L.append("FALSIFIER F-H (scored): FIRED'),
    ("X95 D-3: F-H NOT FIRED line scored (qualifier dropped)", 'L.append("FALSIFIER F-H (descriptive-only by support; decides nothing): NOT FIRED',
     'L.append("FALSIFIER F-H (scored): NOT FIRED'),
    ("X96 D-3: F-H enters the falsifier of record", '    fired = bool(h1["word"] == "RANKS-HOLD")',
     '    fired = bool(h1["word"] == "RANKS-HOLD" or h2["word"] == "RANKS-HOLD")'),
    ("X97 D-3: falsifier of record read on HX2", '    fired = bool(h1["word"] == "RANKS-HOLD")', '    fired = bool(h2["word"] == "RANKS-HOLD")'),
    ("X98 D-3: falsifier of record inverted", '    fired = bool(h1["word"] == "RANKS-HOLD")', '    fired = bool(h1["word"] != "RANKS-HOLD")'),
)


if __name__ == "__main__":
    sys.exit(main())
