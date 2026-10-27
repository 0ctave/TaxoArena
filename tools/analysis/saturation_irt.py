"""saturation_irt.py -- SATURATION-IRT (HF blog post 1): Rasch and 2PL over the 18-model union roster x six union benchmarks;
DECIDING: do the top 10% most discriminating items per benchmark, chosen WITHOUT the ranked model's own responses (leave-one-
model-out), keep Kendall tau-b >= 0.90 of the full macro ranking? ZERO judge calls; no construction; no embedder; CPU only.

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-10-08 (before any code or call) — SATURATION-IRT:
relative to these 18 models, how saturated is each of the six union benchmarks under Rasch and 2PL item response models, and
does the top 10% most discriminating items per benchmark (chosen without the ranked model's own responses) keep Kendall tau >=
0.90 of the full macro ranking? (zero calls; CPU readout; HF post 1)" (L25051-L25064 as of 375cbcc9), with the shared rules R1-R6
of the registrar's record directly before it (L25043-L25049 as of 375cbcc9). Results record docs/agents/results/SATURATION-IRT.json.
Every claim reads "relative to these 18 models" (R6).

LAUNCH SEQUENCE (the run-operator; plain form from the MAIN checkout, or from a worktree with --data-root; rule 7: every step except
--selftest / --mutants is a POOL READER: `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` must exit 1 (free); the script runs
that same check itself before any read and REFUSES on exit 0 (busy) or on any other result) [DELTA 2 2026-10-09: with its own
process and parent chain excluded from busy.ps1's scan, the excluded PIDs printed on the rule-7 line; see DELTA 2 below]:
  0. python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --selftest   # fixtures only; no DB of record
     python tools/analysis/scratch_dir.py --run -- python tools/analysis/saturation_irt.py --mutants    # the mutant table (sandbox)
  1. python tools/analysis/saturation_irt.py --dry-run     # POOL line first (pool_guard.assert_pool_of_record paeec37aa28063c75);
        pins; R1 twins recomputed (REFUSED unless 471 ids / 427 texts); duplicates collapsed; clusters; both v2 views opened with the
        KEY SEALED (the tripwire refuses any statement naming is_correct / is_correct_mathfix); pool row, roster, response counts;
        planned B / seeds / outputs / runtime; NO key, NO statistic; writes nothing
  2. python tools/analysis/saturation_irt.py --pilot 3     # the whole run with 3 component replicates and 3 parametric replicates:
        timing only; writes experiment_results/hf_blog/saturation_irt/saturation_irt_outcome_PILOT.txt (NOT of record, overwritten)
        and seeds the replicate cache (the replicates are deterministic, so the run of record reuses them)
  3. python tools/analysis/saturation_irt.py --run         # resumable (the component-bootstrap cache below); the outcome of record
        and the four figure files are written WRITE-ONCE only when the cache holds all B = 200 replicates; an interrupted --run is
        simply re-launched. Runtime: about 2-2.5 h single-threaded (timed on a synthetic matrix of the registered sizes, 18 x
        about 21,000, with pattern pooling: the six 18-model fits 4 s; one replicate = 18 LOMO models x 6 benchmarks, about 31 s;
        200 replicates about 1.7 h; parametric bootstrap 200 x 6 fits about 13 min); the pilot's per-replicate seconds re-time it.
  Outputs (NEVER committed; pin by sha256 and back up to E:/TaxoArena_backup_<date>_saturation_irt with SHA256SUMS.txt):
    <data root>/experiment_results/hf_blog/saturation_irt/saturation_irt_outcome.txt      (write-once, mode x)
    <data root>/experiment_results/hf_blog/saturation_irt/saturation_irt_boot_cache.jsonl (scratch; meta pinned at first launch)
    E:/TaxoArena_tmp/blog/irt/saturation_irt_{items,benchmarks,models,topk}.json           (write-once; figure data of post 1)
  --data-root <dir>: the checkout whose multicorpus_cache_v1.db, data_v2/ and experiment_results/ are read (from a worktree:
  --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena). Then the adversarial-reviewer (numbers), the registrar.

DATA (as registered; DATA OBJECTS AND HYGIENE + R1/R2):
  POOL     pool_guard.assert_pool_of_record("paeec37aa28063c75") is the first printed line (R1's object: the twin rule is keyed on
           that pool's EVAL ids); the v2 views' own pool row pv2_1575de61bb20e977 is asserted (5,642 components / 6,153 items).
  KEY      the G14 reader's keyed correctness: the sealed v2 views (data_v2.views, gen_view_REG.db sha256-bytes c2930c60... opened
           open_generation("policy_fit"), eval_view_REG.db e35b7518... opened open_eval("route"); the pins of v2_declared_cells),
           response.is_correct with the MATH-FIX overlay (is_correct_mathfix where non-null) [superseded by the DELTA below], read by legacy_qid (= the
           multicorpus question_id, data_v2/ingest.py _union_responses) over ALL THREE SIDES (TRAIN + GATE in the generation view,
           EVAL in the eval view): the registration uses "every item of every split side". R2's extractors are the cached ones
           (leaderboard imported scorer for MMLU-Pro / BBH / MuSR / GPQA, MATH-FIX for MATH [superseded by the DELTA below], prompt-level strict for IFEval).
           [DELTA 2026-10-09 per D-2026-10-08-5 (docs/agents/author_decisions/2026-10-08.md, 5211616a; prog "## Author's decision
           2026-10-08 (recorded by the registrar; ...) — D-2026-10-08-1..6", L25317-L25327 as of bb5eb124): the MATH scorer of
           record is the OFFICIAL one, response.is_correct (= eval_results.is_correct, data_v2/ingest.py _union_responses) for
           every source; is_correct_mathfix is no longer selected, so no MATH-FIX overlay. Criteria, Support, denominators and
           predictions stand as registered (DECLARED PRE-RUN DEVIATIONS (3)); a MATH-level band that assumed MATH-FIX accuracies is
           scored as written and named by the post-run review.]
  R1       TWINS: the paeec EVAL ids whose corpus_questions.text is byte-equal to the text of any id outside that EVAL set (the
           review's exact rule, recomputed); REFUSED unless 471 ids / 427 distinct texts; dropped first. Then every remaining
           group of byte-equal texts is collapsed to its lowest question_id (counts printed per source).
  ROSTER   model_registry ACTIVE of mc6-2026-09-11 in both views, equal, 18 models, Meta-Llama-3-70B-Instruct absent.
  ITEMS    a question is an item iff all 18 cells are present; incomplete questions are counted and the run REFUSES above 1%.
  CLUSTERS CK-CLOSE-v1: split_side.stem_key of the text, within benchmark (Kish sum(n^2)/sum(n) printed: an upper bound at rho=1).

INSTRUMENT (as registered; readings marked [R-x] are this script's and are for the READY to confirm or refuse):
  Per benchmark, penalised joint maximum likelihood (scipy L-BFGS-B, analytic gradient, ftol 1e-12, gtol 1e-6, maxiter 20,000):
  RASCH logit p = theta_m - b_i; 2PL logit p = a_i (theta_m - b_i); priors b ~ N(0, 2^2), log a ~ N(0, 0.5^2) as penalties; theta
  centred (theta = t - mean(t)); items solved by all or none of the FITTED models are excluded and counted (ALL / NONE).
  [R-a] "posterior-mean a_i" is read as the penalised-ML (MAP) a_i, the only a_i the registered estimator yields (under a Laplace
        approximation on the a scale the mean equals the mode; on the log-a scale E[a] = exp(mode + s^2/2) would re-weight items
        by their posterior variance, which the registration does not ask for).
  [R-b] "the top 10% of items" of benchmark b = k_b = round-half-up(0.10 x N_b) items, N_b = all deduplicated items of b (the
        Support's "about 1,180 of about 11,800; IFEVAL about 54"), chosen among the items not constant over the 17 fitted models,
        by (a_i descending, question_id ascending); fewer non-constant items than k_b: all of them are taken (counted).
  [R-c] theta is box-bounded at +-15 (a numerical guard against a model correct on every fitted item); fits that touch the bound
        and fits that do not report convergence are counted and printed (expected 0).
  [R-d] Under component resampling an item drawn c times carries weight c in the likelihood AND its priors (exactly the
        duplicated-copy objective); the top-k selection counts copies (the boundary item may contribute part of its copies).
        Every fit pools identical response columns (fit_cols: weights summed). The penalised objective is a weighted sum of
        per-item terms, so identical columns share one optimum and the pooling is EXACT; it makes tied items exactly tied, so
        the registered id tie-break decides among them (without it, optimiser noise of about 1e-6 decided: found in the build,
        replicate 0 moved by one boundary item between two inits), and it speeds the fits.
  [R-e] Seeds: component bootstrap numpy default_rng(20261008) as registered (all B weight vectors drawn first, in benchmark order
        MMLU_PRO_LB, BBH, MATH, MUSR, GPQA, IFEVAL); the parametric bootstrap default_rng(20261009) and the 20 random subsets
        default_rng(20261010) are this script's (the registration names one seed).
        [B1 fix 2026-10-08, READY review 0cd7fb5e: "MMLU_PRO_LB" in [R-e], SI2, P3 and P4 is the registration's name for the
        corpus_questions / v2-view source label of record "MMLU_PRO"; the code keys the data on "MMLU_PRO".]
  [R-f] Parametric bootstrap: the 18 x fitted-item matrix simulated from the fitted 2PL and refitted under the same exclusion
        rule; an item's interval is the 2.5 / 97.5 nanpercentile over the replicates where it was fitted (count printed).
  [R-g] The full macro ranking is by macro accuracy (mean over the six benchmarks of per-benchmark accuracy over ALL deduplicated
        items, ALL / NONE included); top 4 = the four highest full macro accuracies (ties by model name).
  [R-h] Percentile intervals: numpy percentile, linear interpolation; SE = the replicate SD (ddof 1).
  LOMO: for each model m, per benchmark refit the 2PL on the other 17 (warm start from the 18-model fit), select k_b items, score m
  by its accuracy on them; m's macro = the mean over the six; tau_LOMO = Kendall tau-b(LOMO macro, full macro), 18 models, 153
  pairs. In-sample (18-model fit, the same rule) beside, DESCRIPTIVE. Component bootstrap B 200 repeats the WHOLE LOMO procedure
  (clusters resampled within benchmark; the full macro recomputed on the replicate).

CRITERIA (verbatim words; each rule exhaustive and exclusive; computed values are bool()-cast, never identity-tested):
  SI1 (DECIDING; the POINT decides; printed "(descriptive-only by support)"): KEEPS-RANKING iff tau_LOMO >= 0.90, else
      LOSES-RANKING. RULE 8: KEEPS-RANKING is refuted by tau_LOMO < 0.90 (the discordant-pair count of 153 printed beside).
  SI2 (SCORED; CONFIRMATORY OF A SEEN PATTERN): NEFF_b = share of the N_b items with 2PL information a^2 p (1 - p) >= 0.10 at
      theta_top4 (the mean 2PL ability of the top 4, that benchmark's fit), ALL / NONE counted as 0; GPQA-OPEN iff
      NEFF_GPQA > NEFF_MMLU_PRO_LB, else NOT-SHOWN.
  F-SI fires iff SI1 reads LOSES-RANKING AND the 95% bootstrap upper bound < 0.90.
  PREDICTIONS P1-P6 as registered (bands inclusive; Brier = the multi-outcome sum over the listed outcomes).
  NOT APPLICABLE (stated): wrong(established) and tie conventions A / B (no judge verdict enters; key-scored end to end).

SCORER LINE AND SENSITIVITY H (DELTA 2026-10-09; DECLARED PRE-RUN DEVIATIONS (1), (2), (4), prog L25322 as of bb5eb124):
  HEADER   every outcome file (record, PILOT, partial) and the dry-run carry, right after the POOL and rule-7 lines, the line
           "MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf <hex>); MATH-FIX beside:
           no", then the H table's path, row count and sha.
  H TABLE  <data root>/experiment_results/math_scorer_h/math_h_table.csv (math_scorer_h.py --run, 62d269af; header
           question_id,model,H,route; 23,832 rows). Pinned in the script as the sha256 of its LF bytes, 6b010fa60dde7278...
           (full hex in the constant below). It is checked BEFORE the busy check and any pool read, in --dry-run, --pilot and
           --run: absent, any CR byte or another sha REFUSES; then a wrong header, a malformed or repeated row. At the H line
           every MATH cell of the analysed items must be in the table and agree with the official verdict the views gave
           (route "imported" iff official 1; official 1 implies H 1), else REFUSED.
  H LINES  after SUPPORT, before DESCRIPTIVE: the POINT LOMO procedure re-run with MATH re-keyed by H, the other five benchmarks
           unchanged (no bootstrap): MATH cells / official correct / H correct; tau_LOMO_H (discordant of 153) beside the official
           tau_LOMO; tau_in-sample_H; tau-b(full macro official, full macro H); max |rank shift|; MATH NEFF_H and SAT4_H (at the
           H top 4) beside the official ones; the top 4 under H. DESCRIPTIVE: no criterion, prediction or falsifier reads them;
           no SI1 / SI2 word is printed for H. Cost: one more 18 x 6 LOMO pass (about 35 s on the real sizes).
  CONDITION the registrar's record pinning the table (deviation (2): "no consumer prints an H line without that pin") is owed;
           this script carries the sha of the --run (62d269af) and must not --run before that record exists.

SELFTEST (--selftest; fixtures only: synthetic sealed v2 views, a synthetic multicorpus DB and a pool id file hashed by pool_guard;
nothing of record is opened; temp under scratch_dir). Cases (value-asserting; each executes the REAL entry point where named):
  grad        the analytic gradient of both models (weighted) against finite differences; the objective against a hand value;
              fit() lands where a hand-written penalised log-likelihood with the REGISTERED priors has zero item gradient
  weights     the weighted fit equals the fit on the duplicated matrix (R-d), parameters to 1e-3; pattern pooling equals the
              unpooled fit, ties exactly, zero-weight copies change nothing; Rasch pooled = unpooled
  recover     planted 2PL parameters recovered (corr(a) > 0.8 on 60 respondents); penalised 2PL >= Rasch (nesting)
  select      hand cases: top-k order, the id tie-break, partial boundary copies, fewer non-constant than k, k_of rounding
  taub        tau-b against scipy and hand values (one swap = 1 - 2/153; ties)
  lomo        model m's own responses never change m's selected set (flipping them); the in-sample set DOES change
  twins       R1 on a hand corpus: EVAL-EVAL equal texts are not twins, a cross-source twin is, distinct-text count, collapse
  verdicts    SI1 at tau exactly 0.90 / just below, rule 8, SI2 equality, F-SI at hi exactly 0.90, P1-P6 bands and Brier values
  run_e2e     --run on three fixtures whose word is known: "strong" (200 items per source, well-separated abilities) MUST print
              KEEPS-RANKING (tau 0.9739), "struct" and "noise" MUST print LOSES-RANKING; on each, every printed number of SI1 /
              SI2 / P2 / N / ALL / NONE / SAT4 / NEFF / top 4 / macro / micro equals an INDEPENDENT oracle (plain loops over the raw
              fixture rows: its own twin rule, collapse, overlay, completeness, selection and tau-b; it shares only fit()); 7 twin
              ids / 6 texts incl. one whose EVAL id is LOWER than its partner and one cross-source; the component draws re-derived
              independently (default_rng(seed), clusters by stem_key); the interval and SE = the percentiles / SD of the cached
              replicates; replicate 0's full macro = the oracle on the EXPANDED matrix and its LOMO scores = the pipeline on the
              expanded benchmarks; figure JSONs carry the same numbers; no GPQA text in any output; a second --run is refused
              write-once before any read
  resume      --pilot 2 then --run equals a fresh --run line for line; the cache then holds each replicate once; the pilot never
              writes the record; a changed seed refuses on the pinned cache meta; a partial cache writes *_partial.txt only
  refusals    twins ids, twins texts, roster size, excluded model ACTIVE, pool row, source mismatch, a duplicate (model, qid) row,
              incomplete > 1%, a seventh source; busy.ps1 exit 0 (run and dry-run) and an absent busy.ps1
  sha         a write to the multicorpus DB during the read window refuses (the sha after != before)
  dry_run     the POOL line is first; no statistic; nothing written; the key never selected; line 3 is the scorer header
              with the fixture table's sha, line 4 the H table line; no SENSITIVITY / H line
  run_e2e (delta) the oracle scores MATH by the OFFICIAL verdict while every fixture carries MATH-FIX values differing on about
              15% of MATH cells (an overlay would move the oracle checks); the header line is line 3 of the outcome file; each
              H number (cells, official / H correct, tau_LOMO_H, discordant, tau_in_H, tau-b(macro, macro_H), max rank shift,
              NEFF_H, SAT4_H, top 4 under H) equals the oracle re-keyed by H; the fixture's H credits more than the official
  hrefusals   H table: another sha (--run and --dry-run), absent, CR bytes REFUSE with nothing printed (before the busy check
              and any read); a wrong header; a missing kept cell; route imported with H 0; official 1 not routed imported;
              official 0 routed imported: each REFUSED (re-pinned, so the sha check is not what catches it); nothing written
  labels      (B1) the six labels are pinned to the REAL label set of corpus_questions / both v2 views (REAL_DB_LABELS, a literal
              below the SELFTEST marker, so a mutant of SOURCES cannot move it); the real --dry-run entry point on a fixture
              carrying exactly that set passes REFUSE.SOURCES and prints "MMLU_PRO <n>" in R1; the same fixture relabelled
              MMLU_PRO -> MMLU_PRO_LB (the B1 defect) is REFUSED at REFUSE.SOURCES before any view is opened
  branches    every declared print branch was executed
MUTANTS (--mutants; each edits the code ABOVE the SELFTEST marker in memory and runs the selftest; KILLED iff it fails; X00 is the
control and must survive). The table is the MUTANTS tuple at the end of this file; its last run is recorded in the commit message.
  DELTA mutants X74-X93 (D-2026-10-08-5) and the rewritten X32 (overlay re-introduced through the SQL) are in the same table.
DELTA 2 (2026-10-09; READY_SATURATION-IRT_delta2.md B1, B2, L-1, L-2; nothing else changed):
  B2 busy_check runs the SAME E:/TaxoArena_tmp/busy.ps1, unmodified, inside a PowerShell session whose Get-CimInstance drops this
     process and its parent chain (each ancestor no younger than its child), so busy.ps1's pattern (which names saturation_irt)
     no longer sees the caller; java, peers and every other python still make it exit 0. Fail-closed: a throw (exit 3), no exit
     code (99) or an exit that bypasses the report REFUSES. The rule-7 line prints the excluded PIDs. Selftest busyself (real
     busy.ps1 + sandbox copies, through busy_check). busy.ps1 itself is not changed (shared; the operator's).
  B1 run_e2e's noise fixture gives m15 every MMLU_PRO item (the largest source) and no IFEVAL item (the smallest): its micro
     accuracy enters the top 4 (0.568, third) while its macro is seventh (0.513), so the macro top-4 SET differs from the micro
     top-4 SET; run_e2e asserts that inequality and the top-4 / SAT4 / NEFF lines against the oracle; X94 (the prior Y2: top 4
     ranked by micro) is in the table.
  L-2 H_SHA is asserted against a literal below the SELFTEST marker (st_labels).
NOT DONE HERE: the real --dry-run / --pilot / --run (the operator's, after READY); no Kotlin / Gradle; no judge call.
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
import json          # noqa: E402
import math          # noqa: E402
import time          # noqa: E402
import types         # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
import platform      # noqa: E402
import contextlib    # noqa: E402
import subprocess    # noqa: E402
from collections import Counter, defaultdict   # noqa: E402

import numpy as np   # noqa: E402
import scipy         # noqa: E402
from scipy.optimize import minimize   # noqa: E402
from scipy.special import expit       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


MY_PINS = (("v2_declared_cells.py", "f0f568057995b5d0231da6e3d0d48755a7cf8386"),
           ("v2_reader_guards.py", "14d10ff8a4a03afd0e4edf4beae6281bd8c69982"),
           ("pool_guard.py", "6521b51ac0fce04063563f9e6dcf42554ad86591"),
           ("split_side.py", "05224b5a4b76e74353bc3931ec69f0b14f0e340b"))
for _name, _pin in MY_PINS:
    if blob_lf(os.path.join(HERE, _name)) != _pin:
        raise SystemExit("[SI] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_name, blob_lf(os.path.join(HERE, _name)), _pin))
import v2_declared_cells as V    # noqa: E402  (the G14 reader: open_tw, pool_row, registry, side_counts, after_sha, the pins)
import pool_guard as PG          # noqa: E402
from split_side import stem_key  # noqa: E402

G = V.G
TAG = "[SI]"
TEST_ID = "SATURATION-IRT"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — SATURATION-IRT: relative to these 18'
            ' models, how saturated is each of the six union benchmarks ..." (L25051-L25064 as of 375cbcc9; R1-R6 at L25043-L25049)')
# B1 (READY review 0cd7fb5e): the data are keyed on the label of record in corpus_questions and both v2 views, "MMLU_PRO";
# the registration's name "MMLU_PRO_LB" survives only as a display word in the printed SI2 / P3 / P4 lines.
SOURCES = ("MMLU_PRO", "BBH", "MATH", "MUSR", "GPQA", "IFEVAL")
GPQA, MMLU = "GPQA", "MMLU_PRO"
R1_POOL = "paeec37aa28063c75"
OUT_REL = "experiment_results/hf_blog/saturation_irt"
BLOG_DIR = "E:/TaxoArena_tmp/blog/irt"
BUSY_PS1 = "E:/TaxoArena_tmp/busy.ps1"
# D-2026-10-08-5 (docs/agents/author_decisions/2026-10-08.md, 5211616a; prog "DECLARED PRE-RUN DEVIATIONS" L25322 as of
# bb5eb124): MATH is scored by the official stored is_correct (no overlay); the audited hybrid H is a sensitivity line read
# from the pinned per-row H table (math_scorer_h.py --run, 62d269af; sha256 of its LF bytes), REFUSED on any other sha.
H_REL = "experiment_results/math_scorer_h/math_h_table.csv"
H_SHA = "6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1"
H_SOURCE = "MATH"
H_HEADER = "question_id,model,H,route"
SHARES = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50)
REG = dict(r1_pool=R1_POOL, twins_ids=471, twins_texts=427, pool_v2=V.POOL_U, cv=V.CV_U, comp_eval=5642, n_eval=6153, roster=18,
           share=0.10, bar=0.90, B=200, B_param=200, seed=20261008, seed_param=20261009, seed_rand=20261010, n_rand=20,
           info_min=0.10, s2b=4.0, s2a=0.25, top=4, incomplete_max=0.01, theta_bound=15.0)
SUPPORT_PLAN = dict(n=2100, deff=1.2, n_eff=1750, se=0.0146, mde=0.041, pred=0.93)
PRED = dict(P1=((("KEEPS-RANKING", 0.70), ("LOSES-RANKING", 0.30)), (0.86, 0.97)), P2=0.80,
            P3=((("GPQA-OPEN", 0.90), ("NOT-SHOWN", 0.10)), (0.30, 0.60), (0.15, 0.35)), P4=((0.28, 0.42), (0.04, 0.14)),
            P5=(0.80, 5), P6=(0.05, 0.25))
EXCLUDED = V.EXCLUDED
HIT = Counter()
FITSTAT = Counter()
BRANCHES = ("SI1.KEEPS", "SI1.LOSES", "RULE8.REFUTED", "RULE8.NOT", "SI2.OPEN", "SI2.NOT_SHOWN", "FSI.FIRED", "FSI.NOT_FIRED",
            "FSI.NOT_LOSES", "P1.HELD", "P1.FAILED", "P2.HELD", "P2.FAILED", "P3.HELD", "P3.FAILED", "P4.HELD", "P4.FAILED",
            "P5.HELD", "P5.FAILED", "P6.HELD", "P6.FAILED", "P6.NONE", "SUPPORT.SCOREABLE", "SUPPORT.DESCRIPTIVE", "OUT.RECORD",
            "OUT.PILOT", "OUT.PARTIAL", "REFUSE.TWINS", "REFUSE.ROSTER", "REFUSE.POOLROW", "REFUSE.SOURCE", "REFUSE.SOURCES",
            "REFUSE.INCOMPLETE", "REFUSE.WRITE_ONCE", "REFUSE.BUSY", "REFUSE.CACHE", "REFUSE.DUP", "REFUSE.MISSING_TEXT",
            "REFUSE.SHA", "DRY.DONE", "REFUSE.HSHA", "REFUSE.HTABLE", "SENS.H")


def hit(name):
    if name not in BRANCHES:
        raise SystemExit("%s undeclared branch %r" % (TAG, name))
    HIT[name] += 1


def refuse(msg, branch=None):
    if branch:
        hit(branch)
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ═══════════════════════════════════════════════════════════════════════════════ the IRT core
def _obj(x, Y, w, rasch, M, s2b, s2a):
    """Penalised negative log-likelihood (weights w per item multiply the likelihood AND the priors) and its gradient."""
    n = Y.shape[1]
    tr = x[:M]
    th = tr - tr.mean()
    b = x[M:M + n]
    if rasch:
        al = None
        a = 1.0
    else:
        al = x[M + n:]
        a = np.exp(al)
    d = th[:, None] - b[None, :]
    eta = d * a
    ll = Y * eta - np.logaddexp(0.0, eta)
    r = (Y - expit(eta)) * w[None, :]
    pen = b * b / (2.0 * s2b)
    if not rasch:
        pen = pen + al * al / (2.0 * s2a)
    f = -(ll.sum(0) @ w) + pen @ w
    ra = r * a
    gt = -ra.sum(1)
    gt = gt - gt.mean()
    gb = ra.sum(0) + w * b / s2b
    if rasch:
        return f, np.concatenate([gt, gb])
    ga = -(r * eta).sum(0) + w * al / s2a
    return f, np.concatenate([gt, gb, ga])


def fit(Y, w=None, rasch=False, init=None, reg=None):
    """Penalised JML of the 2PL (or Rasch) on a models x items 0/1 matrix (every column non-constant is the caller's rule)."""
    rg = reg or REG
    Y = np.asarray(Y, dtype=np.float64)
    M, n = Y.shape
    w = np.ones(n) if w is None else np.asarray(w, dtype=np.float64)
    npar = M + n + (0 if rasch else n)
    if n == 0:
        return dict(theta=np.zeros(M), b=np.zeros(0), a=np.zeros(0), al=np.zeros(0), pll=0.0, ok=True, nit=0)
    x0 = np.zeros(npar) if init is None else np.asarray(init, dtype=np.float64)[:npar].copy()
    tb = float(rg["theta_bound"])
    bounds = [(-tb, tb)] * M + [(None, None)] * (npar - M)
    res = minimize(_obj, x0, args=(Y, w, rasch, M, float(rg["s2b"]), float(rg["s2a"])), jac=True, method="L-BFGS-B",
                   bounds=bounds, options=dict(maxiter=20000, maxcor=20, gtol=1e-6, ftol=1e-12))
    tr = res.x[:M]
    th = tr - tr.mean()
    al = np.zeros(n) if rasch else res.x[M + n:]
    FITSTAT["fits"] += 1
    if not res.success:
        FITSTAT["not_converged"] += 1
    if np.any(np.abs(tr) >= tb - 1e-6):
        FITSTAT["theta_bound"] += 1
    return dict(theta=th, b=res.x[M:M + n].copy(), a=np.exp(al), al=al.copy(), pll=float(-res.fun), ok=bool(res.success),
                nit=int(res.nit))


def fit_cols(Y, w, rasch=False, theta0=None, a0=None, b0=None, reg=None):
    """fit() on the DISTINCT response patterns (identical columns pooled, their weights summed): the penalised objective is a
    sum over items of w_i (ll_i + prior_i), so identical columns have identical optima and pooling them is EXACT [R-d]; it makes
    tied items exactly tied (the registered id tie-break then decides, not optimiser noise) and the fits faster. Per-item a, b
    are returned (mapped back); init (theta0, a0, b0) per item, taken at each pattern's first item."""
    Y = np.asarray(Y, dtype=np.float64)
    w = np.ones(Y.shape[1]) if w is None else np.asarray(w, dtype=np.float64)
    if Y.shape[1] == 0:
        f = fit(Y, w, rasch=rasch, reg=reg)
        return dict(f, n_patterns=0)
    U, first, inv = np.unique(Y.T, axis=0, return_index=True, return_inverse=True)
    inv = np.asarray(inv).ravel()
    wu = np.bincount(inv, weights=w, minlength=U.shape[0])
    init = None
    if theta0 is not None:
        parts = [np.asarray(theta0, dtype=np.float64), np.nan_to_num(np.asarray(b0, dtype=np.float64)[first])]
        if not rasch:
            parts.append(np.log(np.nan_to_num(np.asarray(a0, dtype=np.float64)[first], nan=1.0)))
        init = np.concatenate(parts)
    f = fit(U.T, wu, rasch=rasch, init=init, reg=reg)
    return dict(f, a=f["a"][inv], b=f["b"][inv], al=f["al"][inv], n_patterns=int(U.shape[0]))


def info_at(a, b, theta):
    p = expit(a * (theta - b))
    return a * a * p * (1.0 - p)


# ═══════════════════════════════════════════════════════════════════════════════ data assembly (pure)
def r1_twins(text, eval_ids):
    """R1: EVAL ids of the pool whose exact text equals the text of any id OUTSIDE the EVAL set. (sorted ids, distinct texts)"""
    missing = sorted(q for q in eval_ids if q not in text)
    if missing:
        refuse("%d pool EVAL ids have no corpus_questions row (e.g. %s)" % (len(missing), missing[:3]), "REFUSE.MISSING_TEXT")
    outside = {t for q, t in text.items() if q not in eval_ids}
    tw = sorted(q for q in eval_ids if text[q] in outside)
    return tw, len({text[q] for q in tw})


def collapse(text, ids):
    """Remaining byte-equal texts collapsed to the lowest id. (kept sorted, dropped sorted)"""
    groups = defaultdict(list)
    for q in ids:
        groups[text[q]].append(q)
    keep, drop = [], []
    for g in groups.values():
        lo = min(g)
        keep.append(lo)
        drop.extend(q for q in g if q != lo)
    return sorted(keep), sorted(drop)


class Bench:
    def __init__(self, name, ids, Y, keys):
        self.name = name
        self.ids = np.asarray(ids, dtype=np.int64)
        self.Y = np.asarray(Y, dtype=np.float64)
        uniq = sorted(set(keys))
        idx = {k: i for i, k in enumerate(uniq)}
        self.cl = np.asarray([idx[k] for k in keys], dtype=np.int64)
        self.C = len(uniq)
        self.n = len(self.ids)


def kish(cl):
    sz = np.bincount(cl)
    sz = sz[sz > 0]
    return float((sz * sz).sum() / sz.sum()) if sz.size else float("nan")


# ═══════════════════════════════════════════════════════════════════════════════ statistics
def k_of(share, total):
    return max(1, int(math.floor(share * total + 0.5)))


def select_score(order, w, y, k):
    """Accuracy of y over the first k weighted copies of `order` (partial copies of the boundary item); (score, k_eff)."""
    order = np.asarray(order, dtype=np.int64)
    if order.size == 0:
        return float("nan"), 0.0
    wo = w[order]
    cw = np.cumsum(wo)
    if cw[-1] <= k:
        take, k_eff = wo, float(cw[-1])
    else:
        take, k_eff = np.minimum(wo, np.maximum(0.0, k - (cw - wo))), float(k)
    if k_eff <= 0:
        return float("nan"), 0.0
    return float((take * y[order]).sum() / k_eff), k_eff


def order_by_a(a, ids, cols):
    cols = np.asarray(cols, dtype=np.int64)
    return cols[np.lexsort((ids[cols], -np.asarray(a)))]


def nonconst(Ysub, w):
    s = Ysub.sum(0)
    return np.where((w > 0) & (s > 0) & (s < Ysub.shape[0]))[0]


def accs(benches, W):
    """(per-benchmark accuracy matrix M x 6, macro M, micro M) over the weighted items."""
    A = np.stack([(B.Y * w[None, :]).sum(1) / w.sum() for B, w in zip(benches, W)], axis=1)
    num = sum((B.Y * w[None, :]).sum(1) for B, w in zip(benches, W))
    den = sum(w.sum() for w in W)
    return A, A.mean(1), num / den


def full_fit(B, w, rasch=False, reg=None):
    cols = nonconst(B.Y, w)
    f = fit_cols(B.Y[:, cols], w[cols], rasch=rasch, reg=reg)
    a = np.full(B.n, np.nan)
    b = np.full(B.n, np.nan)
    a[cols] = f["a"]
    b[cols] = f["b"]
    return dict(f, cols=cols, a_full=a, b_full=b)


def lomo_orders(benches, W, fulls, reg=None, progress=None):
    """orders[m][b]: the items of benchmark b ranked by the 2PL a fitted WITHOUT model m (non-constant over the other models)."""
    M = benches[0].Y.shape[0]
    orders = []
    for m in range(M):
        rows = np.array([i for i in range(M) if i != m], dtype=np.int64)
        om = []
        for B, w, ff in zip(benches, W, fulls):
            Ym = B.Y[rows]
            cols = nonconst(Ym, w)
            f = fit_cols(Ym[:, cols], w[cols], theta0=ff["theta"][rows], a0=ff["a_full"][cols], b0=ff["b_full"][cols], reg=reg)
            om.append(order_by_a(f["a"], B.ids, cols))
        orders.append(om)
        if progress:
            progress(m)
    return orders


def insample_orders(benches, fulls):
    return [order_by_a(ff["a_full"][ff["cols"]], B.ids, ff["cols"]) for B, ff in zip(benches, fulls)]


def subset_scores(benches, W, orders_of_m, share):
    """Macro score per model: mean over benchmarks of the model's accuracy on its own selected subset (orders_of_m(m)[b])."""
    M = benches[0].Y.shape[0]
    out = np.zeros(M)
    short = 0
    for m in range(M):
        vals = []
        for bi, (B, w) in enumerate(zip(benches, W)):
            k = k_of(share, float(w.sum()))
            s, ke = select_score(orders_of_m(m)[bi], w, B.Y[m], k)
            short += int(ke < k)
            vals.append(s)
        out[m] = float(np.mean(vals))
    return out, short


def tau_b(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = len(x)
    c = d = tx = ty = 0
    for i in range(n):
        for j in range(i + 1, n):
            sx = np.sign(x[i] - x[j])
            sy = np.sign(y[i] - y[j])
            if sx == 0 and sy == 0:
                continue
            if sx == 0:
                tx += 1
            elif sy == 0:
                ty += 1
            elif sx == sy:
                c += 1
            else:
                d += 1
    den = math.sqrt((c + d + tx) * (c + d + ty))
    return (c - d) / den if den > 0 else float("nan")


def discordant(x, y):
    n = len(x)
    return sum(1 for i in range(n) for j in range(i + 1, n) if (x[i] - x[j]) * (y[i] - y[j]) < 0)


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def pctl(xs, q):
    return float(np.percentile(np.asarray(xs, dtype=np.float64), q))


def brier(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def in_band(x, band):
    return bool(band[0] <= x <= band[1])


# ═══════════════════════════════════════════════════════════════════════════════ bootstraps
def boot_weights(benches, B, seed):
    rng = np.random.default_rng(seed)
    out = []
    for _r in range(B):
        Ws = []
        for Bn in benches:
            cnt = np.bincount(rng.integers(0, Bn.C, Bn.C), minlength=Bn.C)
            Ws.append(cnt[Bn.cl].astype(np.float64))
        out.append(Ws)
    return out


def replicate(benches, W, fulls, share, reg=None):
    """The WHOLE LOMO procedure on one replicate's weights: (tau_LOMO, LOMO macro, full macro)."""
    _A, macro, _mi = accs(benches, W)
    orders = lomo_orders(benches, W, fulls, reg=reg)
    sc, _s = subset_scores(benches, W, lambda m: orders[m], share)
    return tau_b(sc, macro), sc, macro


def param_boot(benches, fulls, B, seed, reg=None, progress=None):
    rng = np.random.default_rng(seed)
    res = []
    for B_, ff in zip(benches, fulls):
        res.append(dict(A=np.full((B, B_.n), np.nan), Bb=np.full((B, B_.n), np.nan)))
    M = benches[0].Y.shape[0]
    for r in range(B):
        for bi, (Bn, ff) in enumerate(zip(benches, fulls)):
            cols = ff["cols"]
            P = expit(ff["a"][None, :] * (ff["theta"][:, None] - ff["b"][None, :]))
            Ys = (rng.random(P.shape) < P).astype(np.float64)
            s = Ys.sum(0)
            ok = np.where((s > 0) & (s < M))[0]
            f = fit_cols(Ys[:, ok], None, theta0=ff["theta"], a0=ff["a"][ok], b0=ff["b"][ok], reg=reg)
            res[bi]["A"][r, cols[ok]] = f["a"]
            res[bi]["Bb"][r, cols[ok]] = f["b"]
        if progress:
            progress(r)
    out = []
    for bi, (Bn, ff) in enumerate(zip(benches, fulls)):
        A, Bb = res[bi]["A"], res[bi]["Bb"]
        cnt = (~np.isnan(A)).sum(0)
        with np.errstate(all="ignore"), _quiet_nan():
            alo, ahi = np.nanpercentile(A, 2.5, axis=0), np.nanpercentile(A, 97.5, axis=0)
            blo, bhi = np.nanpercentile(Bb, 2.5, axis=0), np.nanpercentile(Bb, 97.5, axis=0)
        cols = ff["cols"]
        fitted = cols[cnt[cols] > 0]
        excl = int(np.sum((alo[fitted] > 1.0) | (ahi[fitted] < 1.0)))
        out.append(dict(alo=alo, ahi=ahi, blo=blo, bhi=bhi, cnt=cnt, excl1=excl, n_fitted=len(cols),
                        share_excl1=excl / len(cols) if len(cols) else float("nan"),
                        med_cnt=float(np.median(cnt[cols])) if len(cols) else float("nan")))
    return out


@contextlib.contextmanager
def _quiet_nan():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        yield


# ── the component-bootstrap cache (resumable; meta pinned at first launch; only complete replicates are appended) ─────────────
def cache_meta(data, reg, script_blob):
    h = hashlib.sha256()
    h.update(json.dumps(data["models"]).encode("utf-8"))
    for B in data["benches"]:
        h.update(B.name.encode("utf-8"))
        h.update(B.ids.tobytes())
        h.update(B.Y.astype(np.int8).tobytes())
        h.update(B.cl.tobytes())
    return dict(test=TEST_ID, script_blob=script_blob, data_sha256=h.hexdigest(), seed=int(reg["seed"]), B=int(reg["B"]),
                share=float(reg["share"]), s2b=float(reg["s2b"]), s2a=float(reg["s2a"]), sources=list(SOURCES))


def cache_load(path, meta, say):
    done = {}
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(dict(meta=meta), sort_keys=True) + "\n")
        say("  replicate cache %s CREATED; meta pinned: %s" % (path, json.dumps(meta, sort_keys=True)))
        return done
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    try:
        got = json.loads(lines[0])["meta"]
    except (ValueError, KeyError, IndexError):
        refuse("replicate cache %s has no meta line" % path, "REFUSE.CACHE")
    if got != meta:
        refuse("replicate cache %s meta %s != this run's %s (a different script, data or setting; move the cache aside)"
               % (path, json.dumps(got, sort_keys=True), json.dumps(meta, sort_keys=True)), "REFUSE.CACHE")
    torn = 0
    for ln in lines[1:]:
        if not ln.strip():
            continue
        try:
            row = json.loads(ln)
        except ValueError:
            torn += 1
            continue
        r = int(row["r"])
        if r in done or not 0 <= r < meta["B"]:
            refuse("replicate cache %s: replicate %d repeated or out of range" % (path, r), "REFUSE.CACHE")
        done[r] = row
    if torn > 1:
        refuse("replicate cache %s: %d unparseable lines (only one torn final line is tolerated)" % (path, torn), "REFUSE.CACHE")
    say("  replicate cache %s: meta EQUAL; %d of %d replicates present%s" % (path, len(done), meta["B"],
                                                                           "; 1 torn line ignored" if torn else ""))
    return done


def cache_append(path, row):
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


# ═══════════════════════════════════════════════════════════════════════════════ verdicts (pure; every branch printed)
def si1_word(tau, bar):
    return "KEEPS-RANKING" if bool(round(tau, 12) >= bar) else "LOSES-RANKING"


def fsi_fired(word, hi, bar):
    return bool(word == "LOSES-RANKING" and hi < bar)


def si2_word(neff_g, neff_m):
    return "GPQA-OPEN" if bool(neff_g > neff_m) else "NOT-SHOWN"


def p6_share(curve, bar):
    for s, t in curve:
        if round(t, 12) >= bar:
            return s
    return None


def _f(x, fmt="%.4f"):
    return "nan" if x is None or (isinstance(x, float) and math.isnan(x)) else fmt % x


def verdict_lines(st):
    reg = st["reg"]
    bar = reg["bar"]
    L = []
    tau, lo, hi, se = st["tau_lomo"], st["lo"], st["hi"], st["se"]
    w1 = si1_word(tau, bar)
    hit("SI1.KEEPS" if w1 == "KEEPS-RANKING" else "SI1.LOSES")
    L.append("SI1 (DECIDING; the POINT decides): tau_LOMO = %s (Kendall tau-b, %d models, %d pairs; discordant %d) | bootstrap"
             " 95%% [%s, %s] (B %d, components within benchmark, decides nothing) | SE %s" % (
                 _f(tau), st["M"], st["pairs"], st["disc_lomo"], _f(lo), _f(hi), st["B_done"], _f(se)))
    L.append("  SI1 -> %s (descriptive-only by support)" % w1)
    if w1 == "LOSES-RANKING":
        hit("RULE8.REFUTED")
        L.append("RULE 8: KEEPS-RANKING is REFUTED (tau_LOMO %s < %.2f; %d discordant pairs of %d)" % (_f(tau), bar, st["disc_lomo"], st["pairs"]))
    else:
        hit("RULE8.NOT")
        L.append("RULE 8: KEEPS-RANKING is not refuted (tau_LOMO %s >= %.2f; %d discordant pairs of %d)" % (_f(tau), bar, st["disc_lomo"], st["pairs"]))
    ng, nm = st["neff"][GPQA], st["neff"][MMLU]
    w2 = si2_word(ng, nm)
    hit("SI2.OPEN" if w2 == "GPQA-OPEN" else "SI2.NOT_SHOWN")
    L.append("SI2 (SCORED; CONFIRMATORY OF A SEEN PATTERN; the POINT decides): NEFF_GPQA = %s vs NEFF_MMLU_PRO_LB = %s (information"
             " >= %.2f at theta_top4, share of N_b; ALL / NONE count 0)" % (_f(ng), _f(nm), reg["info_min"]))
    L.append("  SI2 -> %s" % w2)
    fired = fsi_fired(w1, hi, bar)
    if fired:
        hit("FSI.FIRED")
        L.append("FALSIFIER F-SI: FIRED (LOSES-RANKING with the 95%% upper bound %s < %.2f): the top-decile discriminating items do"
                 " NOT reproduce the order of these 18 models" % (_f(hi), bar))
    elif w1 == "LOSES-RANKING":
        hit("FSI.NOT_FIRED")
        L.append("FALSIFIER F-SI: NOT FIRED (LOSES-RANKING but the 95%% upper bound %s >= %.2f)" % (_f(hi), bar))
    else:
        hit("FSI.NOT_LOSES")
        L.append("FALSIFIER F-SI: NOT FIRED (SI1 reads KEEPS-RANKING)")
    # predictions
    (p1probs, p1band) = PRED["P1"]
    ok1 = in_band(tau, p1band)
    hit("P1.HELD" if ok1 else "P1.FAILED")
    L.append("P1: SI1 word %s, Brier %.4f (KEEPS 0.70 / LOSES 0.30); tau_LOMO %s in [%.2f, %.2f]: %s" % (
        w1, brier(p1probs, w1), _f(tau), p1band[0], p1band[1], "HELD" if ok1 else "FAILED"))
    ev2 = bool(st["tau_in"] >= tau)
    hit("P2.HELD" if ev2 else "P2.FAILED")
    L.append("P2: tau_in-sample %s >= tau_LOMO %s: %s (p 0.80, Brier %.4f)" % (
        _f(st["tau_in"]), _f(tau), "HELD" if ev2 else "FAILED", brier(((True, PRED["P2"]), (False, 1 - PRED["P2"])), ev2)))
    p3probs, bg, bm = PRED["P3"]
    ok3 = bool(w2 == "GPQA-OPEN" and in_band(ng, bg) and in_band(nm, bm))
    hit("P3.HELD" if ok3 else "P3.FAILED")
    L.append("P3: SI2 word %s, Brier %.4f (GPQA-OPEN 0.90); NEFF_GPQA %s in [%.2f, %.2f]: %s; NEFF_MMLU_PRO_LB %s in [%.2f, %.2f]: %s;"
             " P3 %s" % (w2, brier(p3probs, w2), _f(ng), bg[0], bg[1], "yes" if in_band(ng, bg) else "no", _f(nm), bm[0], bm[1],
                         "yes" if in_band(nm, bm) else "no", "HELD" if ok3 else "FAILED"))
    bm4, bg4 = PRED["P4"]
    s4m, s4g = st["sat4"][MMLU], st["sat4"][GPQA]
    ok4 = bool(in_band(s4m, bm4) and in_band(s4g, bg4))
    hit("P4.HELD" if ok4 else "P4.FAILED")
    L.append("P4: SAT4 MMLU_PRO_LB %s in [%.2f, %.2f]: %s; SAT4 GPQA %s in [%.2f, %.2f]: %s; P4 %s" % (
        _f(s4m), bm4[0], bm4[1], "yes" if in_band(s4m, bm4) else "no", _f(s4g), bg4[0], bg4[1],
        "yes" if in_band(s4g, bg4) else "no", "HELD" if ok4 else "FAILED"))
    n2 = int(sum(1 for s in SOURCES if st["pll2"][s] > st["pllR"][s]))
    ev5 = bool(n2 >= PRED["P5"][1])
    hit("P5.HELD" if ev5 else "P5.FAILED")
    L.append("P5: 2PL beats Rasch by penalised log-likelihood on %d of 6 benchmarks (>= %d): %s (p 0.80, Brier %.4f; NOTE: the 2PL"
             " nests the Rasch fit at log a = 0, where the a-penalty is 0, so >= holds by construction)" % (
                 n2, PRED["P5"][1], "HELD" if ev5 else "FAILED", brier(((True, PRED["P5"][0]), (False, 1 - PRED["P5"][0])), ev5)))
    s6 = p6_share(st["curve_lomo"], bar)
    if s6 is None:
        hit("P6.NONE")
        L.append("P6: no subset share <= 50%% reaches tau_LOMO >= %.2f: FAILED (band [%.2f, %.2f])" % (bar, PRED["P6"][0], PRED["P6"][1]))
    else:
        ok6 = in_band(s6, PRED["P6"])
        hit("P6.HELD" if ok6 else "P6.FAILED")
        L.append("P6: smallest subset share with tau_LOMO >= %.2f is %.0f%% in [%.0f%%, %.0f%%]: %s" % (
            bar, 100 * s6, 100 * PRED["P6"][0], 100 * PRED["P6"][1], "HELD" if ok6 else "FAILED"))
    return L, w1, w2, fired


def support_lines(st):
    reg = st["reg"]
    L = []
    se = st["se"]
    mde = 2.8 * se if not math.isnan(se) else float("nan")
    dist = abs(st["tau_lomo"] - reg["bar"])
    L.append("SUPPORT (measured beside the registered plan): denominator = the LOMO top-decile subsets, %d items over 6 benchmarks"
             " (%s), of %d deduplicated items; 18 ranked models, %d pairs" % (
                 st["k_total"], ", ".join("%s %d" % (s, st["k"][s]) for s in SOURCES), st["n_total"], st["pairs"]))
    L.append("  clusters (CK-CLOSE-v1 stem_key, within benchmark): %d; Kish sum(n^2)/sum(n) = %.4f (an upper bound at rho = 1, from"
             " this run's own cluster sizes); n_eff = %d / %.4f = %.0f" % (st["C_total"], st["kish"], st["k_total"], st["kish"],
                                                                         st["k_total"] / st["kish"]))
    L.append("  realised SE(tau_LOMO) = bootstrap SD %s (B %d); MDE80 = 2.8 x SE = %s; |tau_LOMO - %.2f| = %s" % (
        _f(se), st["B_done"], _f(mde), reg["bar"], _f(dist)))
    if not math.isnan(mde) and dist >= mde:
        hit("SUPPORT.SCOREABLE")
        L.append("  realised support: the point lies beyond the MDE80 from the bar (SCOREABLE at the realised SE); the registered"
                 " verdict line stands: SI1 DESCRIPTIVE-ONLY")
    else:
        hit("SUPPORT.DESCRIPTIVE")
        L.append("  realised support: the point lies within the MDE80 of the bar (DESCRIPTIVE-ONLY at the realised SE, as registered)")
    p = SUPPORT_PLAN
    L.append("  registered plan: about %d items, DEFF %.1f transported (G13's measured 1.214), n_eff %d, SE %.4f, MDE80 %.3f vs"
             " predicted %.2f: SI1 DESCRIPTIVE-ONLY; SI2 SCOREABLE (MDE80 0.04 vs 0.20)" % (p["n"], p["deff"], p["n_eff"], p["se"],
                                                                                         p["mde"], p["pred"]))
    L.append("  not applicable: wrong(established) and tie conventions A / B (no judge verdict enters; key-scored end to end)")
    return L


# ═══════════════════════════════════════════════════════════════════════════════ the analysis
def analyse(data, reg, cache_path, n_boot, n_param, say, progress=print):
    benches, models = data["benches"], data["models"]
    M = len(models)
    W1 = [np.ones(B.n) for B in benches]
    A, macro, micro = accs(benches, W1)
    st = dict(reg=reg, M=M, pairs=M * (M - 1) // 2, models=models)
    fulls = [full_fit(B, w, reg=reg) for B, w in zip(benches, W1)]
    rasch = [full_fit(B, w, rasch=True, reg=reg) for B, w in zip(benches, W1)]
    rank = sorted(range(M), key=lambda m: (-macro[m], models[m]))
    top4 = rank[:int(reg["top"])]
    st.update(acc=A, macro=macro, micro=micro, rank=rank, top4=top4)
    neff, sat4, allc, nonec, theta4, info = {}, {}, {}, {}, {}, {}
    for B, ff in zip(benches, fulls):
        s = B.Y.sum(0)
        allc[B.name], nonec[B.name] = int((s == M).sum()), int((s == 0).sum())
        th4 = float(np.mean(ff["theta"][top4]))
        inf = np.zeros(B.n)
        inf[ff["cols"]] = info_at(ff["a"], ff["b"], th4)
        info[B.name] = inf
        theta4[B.name] = th4
        neff[B.name] = float((inf >= reg["info_min"]).sum() / B.n)
        sat4[B.name] = float((B.Y[top4].min(0) == 1).sum() / B.n)
    st.update(neff=neff, sat4=sat4, allc=allc, nonec=nonec, theta4=theta4,
              pll2={B.name: ff["pll"] for B, ff in zip(benches, fulls)}, pllR={B.name: fr["pll"] for B, fr in zip(benches, rasch)})
    progress("%s point: LOMO fits (18 models x 6 benchmarks) ..." % TAG)
    orders = lomo_orders(benches, W1, fulls, reg=reg)
    ins = insample_orders(benches, fulls)
    sc_lomo, short = subset_scores(benches, W1, lambda m: orders[m], reg["share"])
    sc_in, _s = subset_scores(benches, W1, lambda m: ins, reg["share"])
    st.update(sc_lomo=sc_lomo, sc_in=sc_in, short=short, tau_lomo=tau_b(sc_lomo, macro), tau_in=tau_b(sc_in, macro),
              disc_lomo=discordant(sc_lomo, macro), tau_macro_micro=tau_b(macro, micro),
              k={B.name: k_of(reg["share"], B.n) for B in benches})
    st["k_total"] = int(sum(st["k"].values()))
    st["n_total"] = int(sum(B.n for B in benches))
    st["C_total"] = int(sum(B.C for B in benches))
    allcl = np.concatenate([B.cl + off for B, off in zip(benches, np.cumsum([0] + [B.C for B in benches[:-1]]))])
    st["kish"] = kish(allcl)
    st["kish_b"] = {B.name: kish(B.cl) for B in benches}
    # curves (same LOMO fits; random subsets drawn once per share)
    st["curve_lomo"] = [(s, tau_b(subset_scores(benches, W1, lambda m: orders[m], s)[0], macro)) for s in SHARES]
    st["curve_in"] = [(s, tau_b(subset_scores(benches, W1, lambda m: ins, s)[0], macro)) for s in SHARES]
    rng = np.random.default_rng(int(reg["seed_rand"]))
    cr = []
    for s in SHARES:
        ts = []
        for _j in range(int(reg["n_rand"])):
            rnd = [rng.permutation(B.n)[:k_of(s, B.n)] for B in benches]
            ts.append(tau_b(subset_scores(benches, W1, lambda m: rnd, s)[0], macro))
        cr.append((s, float(np.mean(ts)), pctl(ts, 5), pctl(ts, 95)))
    st["curve_rand"] = cr
    # UpSet of the hard tail (items solved by 1..3 models; pooled over benchmarks)
    ups = Counter()
    for B in benches:
        s = B.Y.sum(0)
        for j in np.where((s >= 1) & (s <= 3))[0]:
            ups[tuple(models[m] for m in range(M) if B.Y[m, j] == 1)] += 1
    st["upset"] = ups
    # parametric bootstrap of the item parameters
    progress("%s parametric bootstrap B %d ..." % (TAG, n_param))
    st["pb"] = param_boot(benches, fulls, n_param, int(reg["seed_param"]), reg=reg,
                          progress=lambda r: progress("%s   parametric replicate %d / %d" % (TAG, r + 1, n_param)))
    st["B_param"] = n_param
    # component bootstrap (the whole LOMO procedure), cached and resumable
    meta = cache_meta(data, reg, data["script_blob"])
    done = cache_load(cache_path, meta, say)
    draws = boot_weights(benches, int(reg["B"]), int(reg["seed"]))
    for r in range(n_boot):
        if r in done:
            continue
        t0 = time.time()
        t, sc, mac = replicate(benches, draws[r], fulls, reg["share"], reg=reg)
        row = dict(r=r, tau=t, lomo=[float(x) for x in sc], full=[float(x) for x in mac])
        cache_append(cache_path, row)
        done[r] = row
        progress("%s   component replicate %d / %d: tau %.4f (%.1f s)" % (TAG, r + 1, n_boot, t, time.time() - t0))
    taus = [done[r]["tau"] for r in range(n_boot)]
    st["taus"] = taus
    st["B_done"] = len(taus)
    st["cache_total"] = len(done)
    st["lo"], st["hi"] = (pctl(taus, 2.5), pctl(taus, 97.5)) if taus else (float("nan"), float("nan"))
    st["se"] = float(np.std(taus, ddof=1)) if len(taus) > 1 else float("nan")
    st["fulls"], st["rasch"], st["orders"], st["ins"], st["info"] = fulls, rasch, orders, ins, info
    return st


def descriptive_lines(st, data):
    benches, models = data["benches"], data["models"]
    L = ["DESCRIPTIVE (decide nothing):"]
    L.append("  per benchmark: N | ALL (all 18 correct) | NONE | fitted | SAT4 [Wilson 95%%] | NEFF | theta_top4 | 2PL pll | Rasch pll"
             " | a-interval excludes 1 (share of fitted; median replicates fitted)")
    for B in benches:
        s = B.name
        k4 = int(round(st["sat4"][s] * B.n))
        lo, hi = wilson(k4, B.n)
        pb = st["pb"][benches.index(B)]
        L.append("  %-11s N %5d | ALL %5d (%.4f) | NONE %5d (%.4f) | fitted %5d | SAT4 %.4f [%.4f, %.4f] | NEFF %.4f | theta4 %+.3f |"
                 " %.2f | %.2f | %s (%s)" % (s, B.n, st["allc"][s], st["allc"][s] / B.n, st["nonec"][s], st["nonec"][s] / B.n,
                                             len(st["fulls"][benches.index(B)]["cols"]), st["sat4"][s], lo, hi, st["neff"][s],
                                             st["theta4"][s], st["pll2"][s], st["pllR"][s], _f(pb["share_excl1"]), _f(pb["med_cnt"], "%.0f")))
    L.append("  tau_in-sample (circular, optimistic) = %s; tau(macro, micro ranking) = %s; LOMO subsets short of k_b: %d" % (
        _f(st["tau_in"]), _f(st["tau_macro_micro"]), st["short"]))
    L.append("  how many items (tau vs subset share): share | top-a LOMO | top-a in-sample | random mean [5%%, 95%%] (%d draws)" % st["reg"]["n_rand"])
    for (s, tl), (_s2, ti), (_s3, rm, r5, r95) in zip(st["curve_lomo"], st["curve_in"], st["curve_rand"]):
        L.append("    %3.0f%% | %.4f | %.4f | %.4f [%.4f, %.4f]" % (100 * s, tl, ti, rm, r5, r95))
    L.append("  ranking (full macro): rank | model | macro | micro | LOMO-subset macro | in-sample-subset macro")
    for i, m in enumerate(st["rank"]):
        L.append("    %2d | %-40s | %.4f | %.4f | %.4f | %.4f" % (i + 1, models[m], st["macro"][m], st["micro"][m], st["sc_lomo"][m], st["sc_in"][m]))
    L.append("  top 4 (theta_top4 / SAT4): %s" % ", ".join(models[m] for m in st["top4"]))
    nh = sum(st["upset"].values())
    L.append("  hard tail (items solved by 1-3 models, pooled): %d items in %d solver sets; the 10 largest:" % (nh, len(st["upset"])))
    for combo, c in sorted(st["upset"].items(), key=lambda kv: (-kv[1], kv[0]))[:10]:
        L.append("    %4d  %s" % (c, " + ".join(combo)))
    return L


def figure_payloads(st, data):
    benches, models = data["benches"], data["models"]
    items = []
    for bi, B in enumerate(benches):
        ff, fr, pb = st["fulls"][bi], st["rasch"][bi], st["pb"][bi]
        ra = np.full(B.n, np.nan)
        ra[fr["cols"]] = fr["b"]
        s = B.Y.sum(0)
        for j in range(B.n):
            st_ = "ALL" if s[j] == len(models) else "NONE" if s[j] == 0 else "FIT"
            items.append(dict(id=int(B.ids[j]), benchmark=B.name, status=st_, n_correct=int(s[j]), a=_nn(ff["a_full"][j]),
                              b=_nn(ff["b_full"][j]), a_lo=_nn(pb["alo"][j]), a_hi=_nn(pb["ahi"][j]), b_lo=_nn(pb["blo"][j]),
                              b_hi=_nn(pb["bhi"][j]), rasch_b=_nn(ra[j]), info_top4=float(st["info"][B.name][j])))
    bench = []
    for bi, B in enumerate(benches):
        s = B.name
        k4 = int(round(st["sat4"][s] * B.n))
        bench.append(dict(benchmark=s, n=B.n, clusters=B.C, kish=st["kish_b"][s], all=st["allc"][s], none=st["nonec"][s],
                          sat4=st["sat4"][s], sat4_wilson=list(wilson(k4, B.n)), neff=st["neff"][s], theta_top4=st["theta4"][s],
                          pll_2pl=st["pll2"][s], pll_rasch=st["pllR"][s], share_a_interval_excludes_1=_nn(st["pb"][bi]["share_excl1"]),
                          k_top_decile=st["k"][s]))
    mods = []
    for m, name in enumerate(models):
        mods.append(dict(model=name, macro=float(st["macro"][m]), micro=float(st["micro"][m]),
                         acc={B.name: float(st["acc"][m, bi]) for bi, B in enumerate(benches)},
                         theta_2pl={B.name: float(st["fulls"][bi]["theta"][m]) for bi, B in enumerate(benches)},
                         theta_rasch={B.name: float(st["rasch"][bi]["theta"][m]) for bi, B in enumerate(benches)},
                         lomo_subset_macro=float(st["sc_lomo"][m]), insample_subset_macro=float(st["sc_in"][m]),
                         rank_full=st["rank"].index(m) + 1))
    topk = dict(models=models, share=st["reg"]["share"], insample_topk={}, lomo_topk={},
                curves=dict(lomo=st["curve_lomo"], insample=st["curve_in"], random=st["curve_rand"]),
                upset=[dict(models=list(c), n=n) for c, n in sorted(st["upset"].items(), key=lambda kv: (-kv[1], kv[0]))],
                taus=dict(lomo=st["tau_lomo"], insample=st["tau_in"], bootstrap=st["taus"]))
    for bi, B in enumerate(benches):
        k = st["k"][B.name]
        sel = st["ins"][bi][:k]
        topk["insample_topk"][B.name] = dict(ids=[int(B.ids[j]) for j in sel],
                                            correct={models[m]: [int(B.Y[m, j]) for j in sel] for m in range(len(models))})
        topk["lomo_topk"][B.name] = {models[m]: [int(B.ids[j]) for j in st["orders"][m][bi][:k]] for m in range(len(models))}
    return dict(items=dict(release="ids + parameters only (R4 / R5); relative to these 18 models", items=items),
                benchmarks=dict(benchmarks=bench), models=dict(models=mods), topk=topk)


def _nn(x):
    x = float(x)
    return None if math.isnan(x) else x


# ═══════════════════════════════════════════════════════════════════════════════ readers and modes
class Cfg:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def real_cfg():
    return Cfg(reg=dict(REG), r1_db=None, r1_idfile=None, mc_db=PG.db_path(R1_POOL),
               gen_path=os.path.join(V.DATA_ROOT, V.GEN_REL), eval_path=os.path.join(V.DATA_ROOT, V.EVAL_REL),
               gen_sha=V.GEN_SHA, eval_sha=V.EVAL_SHA, out_dir=os.path.join(V.DATA_ROOT, OUT_REL), blog_dir=BLOG_DIR,
               busy=BUSY_PS1, h_path=os.path.join(V.DATA_ROOT, H_REL), h_sha=H_SHA)


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


def outputs(cfg, pilot):
    o = os.path.join(cfg.out_dir, "saturation_irt_outcome%s.txt" % ("_PILOT" if pilot else ""))
    figs = {k: os.path.join(cfg.blog_dir, "saturation_irt_%s.json" % k) for k in ("items", "benchmarks", "models", "topk")}
    return o, figs, os.path.join(cfg.out_dir, "saturation_irt_boot_cache.jsonl")


def scorer_line(sha):
    """The header line of DECLARED PRE-RUN DEVIATIONS (1), verbatim form."""
    return ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf %s); MATH-FIX beside: no"
            % sha)


def load_h(path, want):
    """The pinned per-row H table (question_id, model, H, route). REFUSES (before any pool read) when it is absent, carries a CR
    byte, or its sha256 differs from the pin; then on a wrong header, a malformed or duplicate row."""
    if not path or not os.path.isfile(path):
        refuse("the H table %r is absent (pinned sha256-lf %s)" % (path, want), "REFUSE.HSHA")
    with open(path, "rb") as f:
        raw = f.read()
    if b"\r" in raw:
        refuse("the H table %s carries CR bytes (the pin is of its LF bytes)" % path, "REFUSE.HSHA")
    got = hashlib.sha256(raw).hexdigest()
    if got != want:
        refuse("the H table %s is sha256-lf %s, not the pinned %s" % (path, got, want), "REFUSE.HSHA")
    lines = raw.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != H_HEADER:
        refuse("the H table header %r != %r" % (lines[0] if lines else None, H_HEADER), "REFUSE.HTABLE")
    h = {}
    for ln in lines[1:]:
        p = ln.split(",")
        if len(p) != 4 or p[2] not in ("0", "1") or not p[0].isdigit():
            refuse("the H table row %r is malformed" % ln, "REFUSE.HTABLE")
        k = (int(p[0]), p[1])
        if k in h:
            refuse("the H table repeats (%d, %s)" % k, "REFUSE.HTABLE")
        h[k] = (int(p[2]), p[3])
    return h, got


def h_benches(data, htab):
    """The six benchmarks with MATH re-keyed by H (every other benchmark the same object). Each MATH cell is cross-checked
    against the official verdict the views gave: route 'imported' iff official 1, and official 1 implies H 1 (REFUSED else)."""
    models = data["models"]
    out, cnt = [], None
    for B in data["benches"]:
        if B.name != H_SOURCE:
            out.append(B)
            continue
        Y = np.empty_like(B.Y)
        for j, q in enumerate(B.ids):
            for mi, m in enumerate(models):
                r = htab.get((int(q), m))
                if r is None:
                    refuse("the H table lacks the MATH cell (%d, %s)" % (int(q), m), "REFUSE.HTABLE")
                hv, route = r
                off = int(B.Y[mi, j])
                if (route == "imported") != (off == 1) or (off == 1 and hv != 1):
                    refuse("the H table row (%d, %s) H %d route %r disagrees with the official verdict %d of the views"
                           % (int(q), m, hv, route, off), "REFUSE.HTABLE")
                Y[mi, j] = hv
        BH = Bench.__new__(Bench)
        BH.__dict__.update(B.__dict__)
        BH.Y = Y
        cnt = dict(items=B.n, cells=int(B.Y.size), official=int(B.Y.sum()), h=int(Y.sum()))
        out.append(BH)
    return out, cnt


def h_lines(data, st, htab, sha, reg):
    """SENSITIVITY H: the point LOMO procedure re-run with MATH scored by H (no bootstrap). Descriptive; decides nothing."""
    hit("SENS.H")
    models = data["models"]
    M = len(models)
    bh, cnt = h_benches(data, htab)
    W1 = [np.ones(B.n) for B in bh]
    _A, mach, _mi = accs(bh, W1)
    fh = [ff if B.name != H_SOURCE else full_fit(B, w, reg=reg) for B, w, ff in zip(bh, W1, st["fulls"])]
    oh = lomo_orders(bh, W1, fh, reg=reg)
    ih = insample_orders(bh, fh)
    sch, _s1 = subset_scores(bh, W1, lambda m: oh[m], reg["share"])
    sih, _s2 = subset_scores(bh, W1, lambda m: ih, reg["share"])
    tauh, disch, tinh = tau_b(sch, mach), discordant(sch, mach), tau_b(sih, mach)
    rankh = sorted(range(M), key=lambda m: (-mach[m], models[m]))
    top4h = rankh[:int(reg["top"])]
    bi = [B.name for B in bh].index(H_SOURCE)
    B, ff = bh[bi], fh[bi]
    inf = np.zeros(B.n)
    inf[ff["cols"]] = info_at(ff["a"], ff["b"], float(np.mean(ff["theta"][top4h])))
    neffh = float((inf >= reg["info_min"]).sum() / B.n)
    sat4h = float((B.Y[top4h].min(0) == 1).sum() / B.n)
    shift = max(abs(rankh.index(m) - st["rank"].index(m)) for m in range(M))
    return [
        "SENSITIVITY H (D-2026-10-08-5; MATH re-scored by the audited hybrid H, the other five benchmarks unchanged; DESCRIPTIVE,"
        " decides nothing: no criterion, prediction or falsifier reads it): table sha256-lf %s (the pin, verified)" % sha,
        "  H: MATH %d items x %d models = %d cells; official correct %d; H correct %d (+%d)" % (
            cnt["items"], M, cnt["cells"], cnt["official"], cnt["h"], cnt["h"] - cnt["official"]),
        "  H: tau_LOMO_H = %s (discordant %d of %d) vs the official tau_LOMO %s; tau_in-sample_H = %s; tau-b(full macro official,"
        " full macro H) = %s; max |rank shift| %d" % (_f(tauh), disch, st["pairs"], _f(st["tau_lomo"]), _f(tinh),
                                                       _f(tau_b(st["macro"], mach)), shift),
        "  H: MATH NEFF_H %s (official %s); MATH SAT4_H %s (official %s); top 4 under H: %s" % (
            _f(neffh), _f(st["neff"][H_SOURCE]), _f(sat4h), _f(st["sat4"][H_SOURCE]), ", ".join(models[m] for m in top4h)),
    ]


def read_inputs(cfg, say, keyed, pre=()):
    reg = cfg.reg
    pid = PG.assert_pool_of_record(reg["r1_pool"], db=cfg.r1_db, id_file=cfg.r1_idfile)
    say("POOL %s verified (pool_guard.assert_pool_of_record: id file and reserved_pool rows hash to it); R1's object. The v2 views'"
        " pool %s is asserted below. Relative to these 18 models (R6)." % (pid, reg["pool_v2"]))
    for ln in pre:
        say(ln)
    say(G.identity_line(os.path.abspath(__file__), "saturation_irt.py"))
    say("registration: %s" % REG_TEXT)
    say("python %s | numpy %s | scipy %s | %s | threads %s" % (platform.python_version(), np.__version__, scipy.__version__,
                                                               platform.platform(), ", ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS)))
    say("seeds: component bootstrap default_rng(%d) (registered); parametric default_rng(%d), random subsets default_rng(%d) [R-e]"
        % (reg["seed"], reg["seed_param"], reg["seed_rand"]))
    idfile = cfg.r1_idfile or PG.id_file_path(reg["r1_pool"])
    with open(idfile, "r", encoding="utf-8") as f:
        eval_ids = frozenset(q for v in PG.judgeable(json.load(f)).values() for q in v)
    mc_before = G.sha256_file(cfg.mc_db)
    conn = PG.open_ro(cfg.mc_db)
    try:
        rows = conn.execute("SELECT question_id, source, text FROM corpus_questions").fetchall()
    finally:
        conn.close()
    text = {int(q): t for q, _s, t in rows}
    src = {int(q): s for q, s, _t in rows}
    say("  %s sha256-bytes BEFORE %s; corpus_questions %d rows; pool EVAL ids %d" % (os.path.basename(cfg.mc_db), mc_before, len(rows), len(eval_ids)))
    srcs = sorted(set(src.values()))
    if srcs != sorted(SOURCES):
        refuse("corpus_questions sources %s != the six registered %s" % (srcs, sorted(SOURCES)), "REFUSE.SOURCES")
    tw, tw_texts = r1_twins(text, eval_ids)
    by = Counter(src[q] for q in tw)
    say("R1: %d EVAL ids / %d distinct texts have a byte-equal text outside the EVAL set (registered %d / %d): %s" % (
        len(tw), tw_texts, reg["twins_ids"], reg["twins_texts"], ", ".join("%s %d" % (s, by.get(s, 0)) for s in SOURCES)))
    if len(tw) != reg["twins_ids"] or tw_texts != reg["twins_texts"]:
        refuse("R1 twins %d / %d != the registered %d / %d" % (len(tw), tw_texts, reg["twins_ids"], reg["twins_texts"]), "REFUSE.TWINS")
    tws = set(tw)
    keep, drop = collapse(text, [q for q in sorted(text) if q not in tws])
    byd = Counter(src[q] for q in drop)
    say("R1: remaining byte-equal duplicates collapsed to the lowest id: %d dropped (%s); %d questions kept" % (
        len(drop), ", ".join("%s %d" % (s, byd.get(s, 0)) for s in SOURCES), len(keep)))
    # the views
    say("--- v2 views (G14 reader; key %s) ---" % ("UNSEALED for the read" if keyed else "SEALED (dry-run)"))
    gtw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view", say)
    etw, esha = V.open_tw("eval", "route", cfg.eval_path, cfg.eval_sha, "eval_view", say)
    try:
        nc, ni, scope = V.pool_row(etw, reg["pool_v2"], reg["cv"])
        say("  pool %s (scope %r): %d components (registered %d), %d items of %s (registered %d)" % (
            reg["pool_v2"], scope, nc, reg["comp_eval"], ni, reg["cv"], reg["n_eval"]))
        if nc != reg["comp_eval"] or ni != reg["n_eval"]:
            refuse("the v2 pool row differs from the registered counts", "REFUSE.POOLROW")
        rg, re_ = V.registry(gtw, reg["cv"]), V.registry(etw, reg["cv"])
        models = sorted(m for m, s in rg.items() if s == "ACTIVE")
        say("  roster (%s ACTIVE): %d (registered %d); %s ACTIVE: %s; the two views' registries equal: %s" % (
            reg["cv"], len(models), reg["roster"], EXCLUDED, EXCLUDED in models, rg == re_))
        if len(models) != reg["roster"] or EXCLUDED in models or rg != re_:
            refuse("roster check failed (%d models; %s ACTIVE %s; registries equal %s)" % (len(models), EXCLUDED, EXCLUDED in models, rg == re_),
                   "REFUSE.ROSTER")
        say("  roster: " + ", ".join(models))
        sg, se_ = V.side_counts(gtw), V.side_counts(etw)
        say("  side rows: gen_view TRAIN %d, GATE %d; eval_view EVAL %d (all three sides are read: 'every item of every split side')"
            % (sg.get("TRAIN", 0), sg.get("GATE", 0), se_.get("EVAL", 0)))
        mq = ",".join("?" * len(models))
        K = defaultdict(dict)
        nrows = Counter()
        for tw_, table, lab in ((gtw, "response_lite", "gen_view"), (etw, "response", "eval_view")):
            if not keyed:
                n = tw_.execute("SELECT COUNT(*) FROM %s WHERE corpus_version=? AND model IN (%s)" % (table, mq), [reg["cv"]] + models).fetchone()[0]
                say("  %s.%s rows of the roster: %d (key NOT read)" % (lab, table, n))
                continue
            tw_.unseal("SATURATION-IRT --run: the registered key read (G14 reader; all sides)")
            # D-2026-10-08-5: the official scorer only (response.is_correct = eval_results.is_correct, data_v2/ingest.py
            # _union_responses); is_correct_mathfix is NOT selected (no MATH-FIX overlay).
            for m, q, s, c in tw_.execute("SELECT model, legacy_qid, source, is_correct FROM %s WHERE"
                                          " corpus_version=? AND model IN (%s)" % (table, mq), [reg["cv"]] + models):
                q = int(q)
                if src.get(q) != s:
                    refuse("response (%s, %d) source %r != corpus_questions source %r" % (m, q, s, src.get(q)), "REFUSE.SOURCE")
                if m in K[q]:
                    refuse("(model %s, legacy_qid %d) carries more than one response row" % (m, q), "REFUSE.DUP")
                K[q][m] = int(c)
                nrows[lab] += 1
        if keyed:
            say("  key rows read: %s; every source scored by the official stored is_correct (MATH: official, no MATH-FIX"
                " overlay; D-2026-10-08-5)" % dict(nrows))
        lines_sql = len(gtw.log) + len(etw.log)
    finally:
        gtw.close()
        etw.close()
    hook = getattr(cfg, "during_read", None)          # SELFTEST-ONLY (None in real_cfg): a write during the read window
    if hook:
        hook()
    ok_g = V.after_sha(cfg.gen_path, gsha, "gen_view", say)
    ok_e = V.after_sha(cfg.eval_path, esha, "eval_view", say)
    mc_after = G.sha256_file(cfg.mc_db)
    say("  %s sha256-bytes AFTER %s (%s)" % (os.path.basename(cfg.mc_db), mc_after, "EQUAL to before" if mc_after == mc_before else "DIFFERS"))
    if not (ok_g and ok_e and mc_after == mc_before):
        refuse("a DB changed during the read (gen %s, eval %s, multicorpus %s)" % (ok_g, ok_e, mc_after == mc_before), "REFUSE.SHA")
    data = dict(models=models, keep=keep, src=src, text=text, n_sql=lines_sql)
    # clusters printed in both modes (text only)
    per = defaultdict(list)
    for q in keep:
        per[src[q]].append(q)
    if not keyed:
        for s in SOURCES:
            ks = [stem_key(text[q]) for q in per[s]]
            cl = Bench(s, per[s], np.zeros((1, len(per[s]))), ks)
            say("  %-11s kept %5d | clusters %5d | Kish %.4f | k_b (10%%) %d" % (s, len(per[s]), cl.C, kish(cl.cl), k_of(reg["share"], len(per[s]))))
        return data
    benches, incomplete = [], Counter()
    for s in SOURCES:
        ids = [q for q in per[s] if len(K.get(q, {})) == len(models)]
        incomplete[s] = len(per[s]) - len(ids)
        Y = np.array([[K[q][m] for q in ids] for m in models], dtype=np.float64).reshape(len(models), len(ids))
        benches.append(Bench(s, ids, Y, [stem_key(text[q]) for q in ids]))
        say("  %-11s kept %5d | complete (18 cells) %5d | incomplete %d | clusters %5d | Kish %.4f" % (
            s, len(per[s]), len(ids), incomplete[s], benches[-1].C, kish(benches[-1].cl)))
    ninc = sum(incomplete.values())
    if ninc > reg["incomplete_max"] * len(keep):
        refuse("%d of %d kept questions lack one of the 18 cells (> %.0f%%)" % (ninc, len(keep), 100 * reg["incomplete_max"]), "REFUSE.INCOMPLETE")
    data["benches"] = benches
    return data


def h_pre(cfg, htab, hsha):
    return [scorer_line(hsha), "  H table %s: %d rows; sha256-lf %s EQUAL to the pin (checked before any pool read)"
            % (cfg.h_path, len(htab), hsha)]


def dry_run(cfg, say):
    htab, hsha = load_h(cfg.h_path, cfg.h_sha)
    b = busy_check(cfg.busy)
    data = read_inputs(cfg, say, keyed=False, pre=[b] + h_pre(cfg, htab, hsha))
    o, figs, cache = outputs(cfg, False)
    reg = cfg.reg
    say("PLANNED: B %d component replicates (the whole LOMO procedure; cache %s), B %d parametric replicates, %d random subsets per"
        " share %s; outcome %s; figures %s (write-once)" % (reg["B"], cache, reg["B_param"], reg["n_rand"],
                                                          "/".join("%.0f%%" % (100 * s) for s in SHARES), o, ", ".join(figs.values())))
    say("COST: 0 calls, 0 CCE; CPU about 3.5-4.5 h single-threaded (about %d 2PL fits)" % (reg["B"] * 108 + 108 + 12 + reg["B_param"] * 6))
    hit("DRY.DONE")
    say("DRY-RUN: no key column was selected (%d tripwire statements, all key-free); no statistic printed; nothing written." % data["n_sql"])
    return data


def run(cfg, say, pilot=None, progress=print):
    reg = cfg.reg
    o, figs, cache = outputs(cfg, bool(pilot))
    if not pilot:
        for p in [o] + list(figs.values()):
            if os.path.exists(p):
                refuse("%s exists: outcome and figure files are write-once" % p, "REFUSE.WRITE_ONCE")
    htab, hsha = load_h(cfg.h_path, cfg.h_sha)
    b = busy_check(cfg.busy)
    data = read_inputs(cfg, say, keyed=True, pre=[b] + h_pre(cfg, htab, hsha))
    data["script_blob"] = blob_lf(os.path.abspath(__file__))
    n_boot = min(int(pilot), int(reg["B"])) if pilot else int(reg["B"])
    n_param = min(int(pilot), int(reg["B_param"])) if pilot else int(reg["B_param"])
    st = analyse(data, reg, cache, n_boot, n_param, say, progress=progress)
    say("FITS: %d L-BFGS-B fits; not converged %d; theta at the +-%.0f bound %d [R-c]" % (
        FITSTAT["fits"], FITSTAT["not_converged"], reg["theta_bound"], FITSTAT["theta_bound"]))
    vl, w1, w2, fired = verdict_lines(st)
    progress("%s sensitivity H: LOMO fits with MATH scored by H ..." % TAG)
    hl = h_lines(data, st, htab, hsha, reg)
    lines = []
    if pilot:
        hit("OUT.PILOT")
        lines.append("PILOT (%d component / %d parametric replicates): NOT OF RECORD; no verdict of record is read from this file" % (n_boot, n_param))
    lines += vl + support_lines(st) + hl + descriptive_lines(st, data)
    for ln in lines:
        say(ln)
    return data, st, (o, figs, cache, w1, w2, fired)


def write_outputs(cfg, buf, data, st, outs, pilot):
    o, figs, _cache, _w1, _w2, _f2 = outs
    text = "\n".join(buf) + "\n"
    if pilot:
        os.makedirs(os.path.dirname(o), exist_ok=True)
        with open(o, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return o
    if st["B_done"] != int(cfg.reg["B"]):
        hit("OUT.PARTIAL")
        p = o.replace(".txt", "_partial.txt")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return p
    pay = figure_payloads(st, data)
    shas = []
    for k, p in figs.items():
        G.write_once(p, json.dumps(pay[k], sort_keys=True, indent=1) + "\n")
        shas.append("  %s sha256-bytes %s" % (p, G.sha256_file(p)))
    hit("OUT.RECORD")
    text += "FIGURE FILES (write-once; never committed; back up with SHA256SUMS.txt):\n" + "\n".join(shas) + "\n"
    G.write_once(o, text)
    return o


def main(argv=None, out=print, cfg=None, progress=print):
    ap = argparse.ArgumentParser(description="SATURATION-IRT (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--pilot", type=int)
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
    pilot = a.pilot if a.pilot else None
    data, st, outs = run(cfg, say, pilot=pilot, progress=progress)
    p = write_outputs(cfg, buf, data, st, outs, pilot)
    out("%s written: %s" % (TAG, p))
    return 0


# ══ SELFTEST (fixtures only; nothing of record is opened; everything below is test code)
def _rm(d):
    import shutil
    import stat as _stat

    def onerr(func, path, _e):
        os.chmod(path, _stat.S_IWRITE)
        func(path)
    shutil.rmtree(d, onerror=onerr)


def _mkview(path, kind, spec):
    from data_v2 import ro as dv2ro
    c = dv2ro.create_new(path)
    c.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    for k, v in (("view_kind", kind), ("of_record", "SELFTEST FIXTURE")):
        c.execute("INSERT INTO meta VALUES (?,?)", (k, v))
    c.execute("CREATE TABLE side (item_id TEXT PRIMARY KEY, component_id TEXT, side TEXT, stratum_source TEXT, stratum_domain TEXT, corpora TEXT)")
    c.execute("CREATE TABLE pool (pool_id TEXT PRIMARY KEY, scope TEXT, n_components INTEGER, n_items_by_scope TEXT)")
    c.execute("CREATE TABLE model_registry (corpus_version TEXT, model TEXT, status TEXT, reason TEXT, n_responses INTEGER,"
              " PRIMARY KEY (corpus_version, model))")
    rt = "response_lite" if kind == "gen" else "response"
    c.execute("CREATE TABLE %s (corpus_version TEXT, response_id TEXT, model TEXT, legacy_qid INTEGER, source TEXT, seen_ck TEXT,"
              " item_id TEXT, gt_raw TEXT, answer_text TEXT, pred TEXT, is_correct INTEGER, is_correct_mathfix INTEGER%s,"
              " PRIMARY KEY (corpus_version, response_id))" % (rt, ", output_zlib BLOB" if kind == "eval" else ""))
    c.execute("INSERT INTO pool VALUES (?,?,?,?)", ("pv_fx", "all", spec["pool_comp"], json.dumps({"mcfx": spec["pool_items"]})))
    for m, s in spec["registry"]:
        c.execute("INSERT INTO model_registry VALUES (?,?,?,?,?)", ("mcfx", m, s, None, 0))
    sides = ("TRAIN", "GATE") if kind == "gen" else ("EVAL",)
    k = 0
    for q in spec["qids"]:
        sd = spec["vside"][q]
        if sd not in sides:
            continue
        c.execute("INSERT INTO side VALUES (?,?,?,?,?,?)", ("i:%d" % q, "c:%d" % q, sd, spec["src"][q], "d", "mcfx"))
        for m, (cv, mf) in spec["cells"].get(q, {}).items():
            k += 1
            vals = ["mcfx", "x%d" % k, m, q, spec["rsrc"].get(q, spec["src"][q]), "v", "i:%d" % q, "g", "a", "p", cv, mf]
            if kind == "eval":
                vals.append(b"z")
            c.execute("INSERT INTO %s VALUES (%s)" % (rt, ",".join("?" * len(vals))), vals)
    for (q, m, cv) in spec.get("dups", ()):
        if spec["vside"][q] in sides:
            k += 1
            vals = ["mcfx", "x%d" % k, m, q, spec["src"][q], "v", "i:%d" % q, "g", "a", "p", cv, None] + ([b"z"] if kind == "eval" else [])
            c.execute("INSERT INTO %s VALUES (%s)" % (rt, ",".join("?" * len(vals))), vals)
    c.commit()
    return dv2ro.seal(c, path, "saturation_irt selftest %s view" % kind)["sha256_bytes"]


FX_MODELS = ["m%02d" % i for i in range(18)]


def _spec(kind="struct", seed=5, n=(48, 30, 30, 30, 36, 24), twins=True, mutate=None):
    """A six-source fixture: qids, texts (twins, exact duplicates, case variants = one stem cluster), view sides, 18-model cells
    (+ the excluded model's rows, MATH-FIX overlays), the paeec-like EVAL id list."""
    rs = np.random.RandomState(seed)
    qids, text, src, vside, cells, ev = [], {}, {}, {}, {}, []
    th = np.linspace(-2.0, 2.0, 18) if kind == "strong" else np.linspace(-1.5, 1.5, 18)
    nid = [1000]

    def new(s, t, is_eval):
        nid[0] += 1
        q = nid[0]
        qids.append(q)
        text[q], src[q] = t, s
        vside[q] = ("EVAL", "TRAIN", "GATE", "TRAIN")[q % 4]
        if is_eval:
            ev.append(q)
        return q
    bank = {}
    for si, s in enumerate(SOURCES):
        for j in range(n[si]):
            t = "question %s %d about %s" % (s, j, "x" * (j % 3))
            if j % 7 == 3:
                t = t.upper()                       # same stem_key as no other row; a distinct cluster
            q = new(s, t, j % 3 == 0)
            bank[(s, j)] = q
            d = rs.normal(0, 1.5 if kind == "strong" else 1.0)
            a = np.exp(rs.normal(1.0, 0.3)) if kind == "strong" else np.exp(rs.normal(0.3, 0.4)) if kind == "struct" else 0.0
            for mi, m in enumerate(FX_MODELS):
                p = 0.5 + 0.02 * (mi % 3) if kind == "noise" else expit(a * (th[mi] - d))
                cv = int(rs.rand() < p)
                mf = None
                if s == "MATH" and rs.rand() < 0.15:
                    mf = 1 - cv
                cells.setdefault(q, {})[m] = (cv, mf)
            cells[q][EXCLUDED] = (1, None)
    # case variant of an existing text: a new item in the SAME stem cluster (norm-v1 folds case)
    for s in SOURCES:
        q0 = bank[(s, 1)]
        q = new(s, text[q0].upper(), False)
        cells[q] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
    q0 = bank[("MATH", 0)]                                       # an EVAL id with a stem-key (NOT exact) twin outside: not R1
    assert q0 in ev
    q = new("MATH", text[q0].upper(), False)
    cells[q] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
    tw_ids = []
    if twins:
        # R1 twins: EVAL ids whose exact text exists outside the EVAL set
        for s, j in (("GPQA", 2), ("GPQA", 4), ("MMLU_PRO", 5), ("BBH", 8)):
            q0 = bank[(s, j)]
            if q0 in ev:
                ev.remove(q0)
            q = new(s, text[q0], True)
            cells[q] = {m: cells[q0][m] for m in FX_MODELS}
            tw_ids.append(q)
        q = new("GPQA", text[bank[("GPQA", 2)]], True)          # a second EVAL twin of the same text: 6 ids / 5 texts below
        cells[q] = {m: cells[bank[("GPQA", 2)]][m] for m in FX_MODELS}
        tw_ids.append(q)
        q = new("GPQA", "an early EVAL question whose outside copy comes later", True)   # twin id LOWER than its partner
        cells[q] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
        tw_ids.append(q)
        q2 = new("GPQA", text[q], False)
        cells[q2] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
        q0 = bank[("MMLU_PRO", 9)]                            # a cross-source twin: MATH EVAL id with an MMLU-Pro TRAIN text
        if q0 in ev:
            ev.remove(q0)
        q = new("MATH", text[q0], True)
        cells[q] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
        tw_ids.append(q)
    # EVAL-EVAL equal texts (NOT twins) and TRAIN-TRAIN exact duplicates (collapsed to the lowest id)
    q0 = bank[("MUSR", 0)]
    if q0 not in ev:
        ev.append(q0)
    q = new("MUSR", text[q0], True)
    cells[q] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
    for j in (1, 2):
        q0 = bank[("IFEVAL", j)]
        if q0 in ev:
            ev.remove(q0)
        q = new("IFEVAL", text[q0], False)
        cells[q] = {m: (int(rs.rand() < 0.5), None) for m in FX_MODELS}
    # an incomplete question (one model missing): counted, not an item
    q = new("BBH", "an incomplete question", False)
    cells[q] = {m: (1, None) for m in FX_MODELS[:-1]}
    # the per-row H table of every MATH (question, model) of the 18 (the excluded model is not in it, as in the real table):
    # official 1 -> (1, imported); official 0 -> H 1 (a stated-answer route) with probability 1.0 for m10 / m12 / m13 and 0.05
    # for the others, else (0, none): on the "noise" fixture H changes the top-4 SET (so theta_top4 differs; run_e2e asserts it)
    hr = np.random.RandomState(seed + 1000)
    h = {}
    for q in qids:
        if src[q] != "MATH":
            continue
        for m in FX_MODELS:
            if m in cells[q]:
                cv = cells[q][m][0]
                ph = 1.0 if m in ("m10", "m12", "m13") else 0.05
                h[(q, m)] = (1, "imported") if cv == 1 else ((1, "boxed:str") if hr.rand() < ph else (0, "none"))
    spec = dict(qids=qids, text=text, src=src, vside=vside, cells=cells, ev=sorted(ev), rsrc={}, dups=[], h=h,
                registry=[(m, "ACTIVE") for m in FX_MODELS] + [(EXCLUDED, "QUARANTINED")], tw_ids=sorted(tw_ids))
    n_eval_v = sum(1 for q in qids if vside[q] == "EVAL")
    spec.update(pool_comp=n_eval_v, pool_items=n_eval_v)
    if mutate:
        mutate(spec)
    return spec


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
    c = sqlite3.connect(db)
    c.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT, text TEXT)")
    c.execute("CREATE TABLE reserved_pool (pool_id TEXT, domain TEXT, question_id INTEGER)")
    for q in spec["qids"]:
        c.execute("INSERT INTO corpus_questions VALUES (?,?,?)", (q, spec["src"][q], spec["text"][q]))
    for k, ids in keyd.items():
        for q in ids:
            c.execute("INSERT INTO reserved_pool VALUES (?,?,?)", (pid, k, q))
    c.commit()
    c.close()
    gp, ep = os.path.join(tmp, "gen.db"), os.path.join(tmp, "eval.db")
    gs, es = _mkview(gp, "gen", spec), _mkview(ep, "eval", spec)
    busy = os.path.join(tmp, "busy_free.ps1")
    with open(busy, "w", encoding="utf-8") as f:
        f.write("exit 1\n")
    reg = dict(REG, r1_pool=pid, twins_ids=len(spec["tw_ids"]), twins_texts=len({spec["text"][q] for q in spec["tw_ids"]}),
               pool_v2="pv_fx", cv="mcfx", comp_eval=spec["pool_comp"], n_eval=spec["pool_items"], B=6, B_param=3, n_rand=4)
    reg.update(reg_over or {})
    hp = os.path.join(tmp, "math_h_table.csv")
    hsha = _write_h(hp, spec["h"])
    return Cfg(reg=reg, r1_db=db, r1_idfile=idf, mc_db=db, gen_path=gp, eval_path=ep, gen_sha=gs, eval_sha=es,
               out_dir=os.path.join(tmp, "out"), blog_dir=os.path.join(tmp, "blog"), busy=busy, h_path=hp, h_sha=hsha)


def _write_h(path, h, eol=b"\n", header=H_HEADER):
    """The fixture H table in math_scorer_h.py's rendering (sorted by question_id, model; LF); returns its sha256."""
    body = eol.join([header.encode("utf-8")] + [("%d,%s,%d,%s" % (q, m, v, r)).encode("utf-8")
                                                for (q, m), (v, r) in sorted(h.items())]) + eol
    with open(path, "wb") as f:
        f.write(body)
    return hashlib.sha256(body).hexdigest()


def _main(cfg, argv):
    buf = []
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = main(argv, out=buf.append, cfg=cfg, progress=lambda s: None)
        except SystemExit as e:
            return None, buf, str(e)
    return rc, buf, None


def _line(buf, prefix):
    hits = [ln for ln in buf if ln.startswith(prefix)]
    assert len(hits) == 1, "expected one line starting %r, got %d" % (prefix, len(hits))
    return hits[0]


def _num(s, after):
    i = s.index(after) + len(after)
    while i < len(s) and s[i] == " ":
        i += 1
    j = i
    while j < len(s) and (s[j].isdigit() or s[j] in "+-.e"):
        j += 1
    return float(s[i:j])


# ── the INDEPENDENT oracle (plain loops over the raw fixture rows; shares only fit() with the script) ──────────────────────────
def _oracle(spec, reg, weights=None, h=False):
    text, src = spec["text"], spec["src"]
    ev = set(spec["ev"])
    tw = []
    for q in spec["ev"]:
        for g in spec["qids"]:
            if g not in ev and text[g] == text[q]:
                tw.append(q)
                break
    rest = [q for q in spec["qids"] if q not in set(tw)]
    keep = []
    for q in rest:
        if not any(text[g] == text[q] and g < q for g in rest):
            keep.append(q)
    models = sorted(FX_MODELS)
    val = {}
    for q in keep:
        row = {}
        for m in models:
            if m in spec["cells"][q]:
                cv, _mf = spec["cells"][q][m]          # the official verdict; the MATH-FIX value is ignored (D-2026-10-08-5)
                row[m] = spec["h"][(q, m)][0] if (h and src[q] == "MATH") else cv
        if len(row) == len(models):
            val[q] = row
    per = {s: sorted(q for q in val if src[q] == s) for s in SOURCES}
    if weights is not None:            # expand: an item drawn c times becomes c copies (ids repeated)
        per = {s: [q for q, c in zip(per[s], weights[si]) for _ in range(int(c))] for si, s in enumerate(SOURCES)}
    M = len(models)

    def acc(m, qs):
        return sum(val[q][models[m]] for q in qs) / len(qs)
    macro = [sum(acc(m, per[s]) for s in SOURCES) / 6 for m in range(M)]
    micro = [sum(val[q][models[m]] for s in SOURCES for q in per[s]) / sum(len(per[s]) for s in SOURCES) for m in range(M)]

    def top(rows, qs):
        cols = [j for j, q in enumerate(qs) if 0 < sum(val[q][models[r]] for r in rows) < len(rows)]
        Y = np.array([[val[qs[j]][models[r]] for j in cols] for r in rows], dtype=float)
        f = fit(Y, reg=reg)
        grp = defaultdict(list)                      # identical response patterns are exactly tied: their a averaged
        for i in range(len(cols)):
            grp[tuple(Y[:, i])].append(f["a"][i])
        av = [sum(grp[tuple(Y[:, i])]) / len(grp[tuple(Y[:, i])]) for i in range(len(cols))]
        ordered = sorted(range(len(cols)), key=lambda i: (-round(av[i], 4), qs[cols[i]], cols[i]))
        return [qs[cols[i]] for i in ordered], f
    lomo, ins_sc = [], [0.0] * M
    ins_sel = {}
    for s in SOURCES:
        ins_sel[s], _f0 = top(list(range(M)), per[s])
    for m in range(M):
        tot = 0.0
        for s in SOURCES:
            k = max(1, int(math.floor(0.10 * len(per[s]) + 0.5)))
            sel, _f1 = top([r for r in range(M) if r != m], per[s])
            sel = sel[:k]
            tot += sum(val[q][models[m]] for q in sel) / len(sel)
        lomo.append(tot / 6)
    for m in range(M):
        tot = 0.0
        for s in SOURCES:
            k = max(1, int(math.floor(0.10 * len(per[s]) + 0.5)))
            sel = ins_sel[s][:k]
            tot += sum(val[q][models[m]] for q in sel) / len(sel)
        ins_sc[m] = tot / 6

    def taub(x, y):
        c = d = tx = ty = 0
        for i in range(len(x)):
            for j in range(i + 1, len(x)):
                if x[i] == x[j] and y[i] == y[j]:
                    continue
                if x[i] == x[j]:
                    tx += 1
                elif y[i] == y[j]:
                    ty += 1
                elif (x[i] > x[j]) == (y[i] > y[j]):
                    c += 1
                else:
                    d += 1
        return (c - d) / math.sqrt((c + d + tx) * (c + d + ty))
    rank = sorted(range(M), key=lambda m: (-macro[m], models[m]))
    t4 = rank[:4]
    nmath = sum(1 for q in per["MATH"] for m in models if val[q][m] == 1)
    disc = 0
    for i in range(M):
        for j in range(i + 1, M):
            if (lomo[i] > lomo[j] and macro[i] < macro[j]) or (lomo[i] < lomo[j] and macro[i] > macro[j]):
                disc += 1
    out = dict(disc=disc, tw=len(tw), all={s: sum(1 for q in per[s] if sum(val[q].values()) == M) for s in SOURCES},
               none={s: sum(1 for q in per[s] if sum(val[q].values()) == 0) for s in SOURCES}, macro=macro, micro=micro, tau_lomo=taub(lomo, macro), tau_in=taub(ins_sc, macro), lomo=lomo,
               neff={}, sat4={}, n={s: len(per[s]) for s in SOURCES}, top4=[models[m] for m in t4], nmath=nmath,
               rank=[models[m] for m in rank])
    if weights is None:
        for s in SOURCES:
            qs = per[s]
            cols = [j for j, q in enumerate(qs) if 0 < sum(val[q].values()) < M]
            Y = np.array([[val[qs[j]][models[r]] for j in cols] for r in range(M)], dtype=float)
            f = fit(Y, reg=reg)
            th4 = sum(f["theta"][m] for m in t4) / 4
            cnt = 0
            for i in range(len(cols)):
                p = 1 / (1 + math.exp(-f["a"][i] * (th4 - f["b"][i])))
                cnt += int(f["a"][i] ** 2 * p * (1 - p) >= reg["info_min"])
            out["neff"][s] = cnt / len(qs)
            out["sat4"][s] = sum(1 for q in qs if all(val[q][models[m]] == 1 for m in t4)) / len(qs)
    return out


# ── cases ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def st_grad():
    from scipy.optimize import approx_fprime
    rs = np.random.RandomState(1)
    Y = (rs.rand(7, 9) < 0.5).astype(float)
    w = rs.rand(9) + 0.5
    for rasch in (False, True):
        npar = 7 + 9 + (0 if rasch else 9)
        x = rs.normal(0, 0.5, npar)
        g = _obj(x, Y, w, rasch, 7, 4.0, 0.25)[1]
        ng = approx_fprime(x, lambda z: _obj(z, Y, w, rasch, 7, 4.0, 0.25)[0], 1e-7)
        assert np.max(np.abs(g - ng)) < 1e-4, ("gradient", rasch, np.max(np.abs(g - ng)))
    # the objective's value against a hand computation (one model pair, one item)
    x = np.array([0.3, -0.3, 0.2, math.log(1.5)])
    Yh = np.array([[1.0], [0.0]])
    eta = 1.5 * (np.array([0.3, -0.3]) - 0.2)
    want = -(eta[0] - math.log1p(math.exp(eta[0])) - math.log1p(math.exp(eta[1]))) + 0.2 ** 2 / 8 + math.log(1.5) ** 2 / 0.5
    got = _obj(x, Yh, np.ones(1), False, 2, 4.0, 0.25)[0]
    assert abs(got - want) < 1e-12, (got, want)
    # fit() optimises the REGISTERED objective: at its optimum the gradient of a hand-written penalised log-likelihood
    # (b ~ N(0, 2^2), log a ~ N(0, 0.5^2), plain loops, constants written here) vanishes in every item parameter
    Ys = (rs.rand(8, 6) < 0.5).astype(float)
    Ys[:, 0] = [1, 1, 1, 1, 1, 1, 1, 0]
    Ys[:, 1] = [1, 0, 0, 0, 0, 0, 0, 0]
    f = fit(Ys)

    def hand(bb, aa):
        tot = 0.0
        for i in range(6):
            for m_ in range(8):
                e = aa[i] * (f["theta"][m_] - bb[i])
                tot += Ys[m_, i] * e - math.log1p(math.exp(e))
            tot -= bb[i] ** 2 / (2 * 2.0 ** 2) + math.log(aa[i]) ** 2 / (2 * 0.5 ** 2)
        return tot
    for i in range(6):
        for which in ("b", "a"):
            bb, aa = list(f["b"]), list(f["a"])
            h = 1e-6
            if which == "b":
                bp, bm = bb[:], bb[:]
                bp[i] += h
                bm[i] -= h
                g = (hand(bp, aa) - hand(bm, aa)) / (2 * h)
            else:
                ap, am = aa[:], aa[:]
                ap[i] *= math.exp(h)
                am[i] *= math.exp(-h)
                g = (hand(bb, ap) - hand(bb, am)) / (2 * h)
            assert abs(g) < 1e-3, ("not at the registered optimum", which, i, g)


def st_weights():
    rs = np.random.RandomState(2)
    th = np.linspace(-1, 1, 10)
    b = rs.normal(0, 1, 25)
    Y = (rs.rand(10, 25) < expit(th[:, None] - b)).astype(float)
    s = Y.sum(0)
    Y = Y[:, (s > 0) & (s < 10)]
    w = rs.randint(1, 4, Y.shape[1]).astype(float)
    f1 = fit(Y, w)
    Yd = np.repeat(Y, w.astype(int), axis=1)
    f2 = fit(Yd)
    idx = np.repeat(np.arange(Y.shape[1]), w.astype(int))
    assert np.max(np.abs(f1["a"][idx] - f2["a"])) < 1e-3 and np.max(np.abs(f1["b"][idx] - f2["b"])) < 1e-3, "weights != duplication"
    assert np.max(np.abs(f1["theta"] - f2["theta"])) < 1e-3
    assert abs(f1["theta"].mean()) < 1e-12, "theta not centred"
    # pattern pooling (fit_cols) is exact: same optimum as the unpooled fit, identical columns EXACTLY tied, weights summed
    Yt = np.concatenate([Y, Y[:, :5]], axis=1)
    wt = np.concatenate([w, np.full(5, 2.0)])
    g = fit_cols(Yt, wt)
    h = fit(Yt, wt)
    assert np.max(np.abs(g["a"] - h["a"])) < 1e-3 and np.max(np.abs(g["b"] - h["b"])) < 1e-3, "pooled != unpooled"
    assert np.array_equal(g["a"][:5], g["a"][-5:]) and g["n_patterns"] < Yt.shape[1]
    w3 = wt.copy()
    w3[-5:] = 0.0
    w3[:5] = w[:5]
    assert np.max(np.abs(fit_cols(Yt, w3)["a"][:5] - f1["a"][:5])) < 1e-3, "zero-weight copies changed the fit"
    gr = fit_cols(Yt, wt, rasch=True)
    assert np.allclose(gr["a"], 1.0) and np.max(np.abs(gr["b"] - fit(Yt, wt, rasch=True)["b"])) < 1e-3


def st_recover():
    rs = np.random.RandomState(3)
    M, n = 60, 400
    th = rs.normal(0, 1, M)
    b = rs.normal(0, 1, n)
    a = np.exp(rs.normal(0, 0.4, n))
    Y = (rs.rand(M, n) < expit(a * (th[:, None] - b))).astype(float)
    s = Y.sum(0)
    keep = (s > 0) & (s < M)
    f = fit(Y[:, keep])
    fr = fit(Y[:, keep], rasch=True)
    assert np.corrcoef(f["a"], a[keep])[0, 1] > 0.6, np.corrcoef(f["a"], a[keep])[0, 1]
    assert np.corrcoef(f["b"], b[keep])[0, 1] > 0.9
    assert np.corrcoef(f["theta"], th)[0, 1] > 0.95
    assert f["pll"] >= fr["pll"] - 1e-6, "2PL below the nested Rasch"
    assert np.allclose(fr["a"], 1.0)


def st_select():
    w = np.ones(6)
    y = np.array([1, 0, 1, 1, 0, 0], dtype=float)
    assert select_score([2, 0, 1], w, y, 2) == (1.0, 2.0)
    assert select_score([1, 4, 2], w, y, 2) == (0.0, 2.0)
    s, k = select_score([2, 1], w, y, 5)                       # fewer than k: all taken
    assert (s, k) == (0.5, 2.0)
    w2 = np.array([3, 1, 2, 1, 1, 1], dtype=float)            # partial copies of the boundary item
    s, k = select_score([0, 1, 2], w2, y, 5)                   # 3 x item0 (1) + 1 x item1 (0) + 1 of 2 x item2 (1) = 4 / 5
    assert (abs(s - 0.8) < 1e-12, k) == (True, 5.0), (s, k)
    ids = np.array([50, 10, 30, 20], dtype=np.int64)
    o = order_by_a(np.array([1.0, 2.0, 2.0, 0.5]), ids, np.array([0, 1, 2, 3]))
    assert list(o) == [1, 2, 0, 3], o                           # a desc, ties by id asc (10 before 30)
    assert [k_of(0.10, n) for n in (541, 545, 9, 4, 11800)] == [54, 55, 1, 1, 1180]
    Y = np.array([[1, 1, 0, 1], [1, 0, 0, 1], [1, 1, 0, 0]], dtype=float)
    assert list(nonconst(Y, np.ones(4))) == [1, 3]
    assert list(nonconst(Y, np.array([1, 0, 1, 1.0]))) == [3]


def st_taub():
    from scipy.stats import kendalltau
    rs = np.random.RandomState(4)
    x = np.arange(18, dtype=float)
    y = x.copy()
    y[[3, 4]] = y[[4, 3]]
    assert abs(tau_b(x, y) - (1 - 2 / 153)) < 1e-12 and discordant(x, y) == 1
    for _ in range(20):
        a = rs.randint(0, 5, 18).astype(float)
        b = rs.randint(0, 6, 18).astype(float)
        assert abs(tau_b(a, b) - kendalltau(a, b)[0]) < 1e-12
    assert discordant([1, 2, 3], [3, 2, 1]) == 3
    assert abs(pctl([0, 10], 2.5) - 0.25) < 1e-12
    lo, hi = wilson(5, 20)
    assert abs(lo - 0.11186) < 1e-4 and abs(hi - 0.46870) < 1e-4, (lo, hi)
    assert abs(kish(np.array([0, 0, 1, 2, 2, 2])) - 14 / 6) < 1e-12


def st_lomo():
    rs = np.random.RandomState(9)
    M = 18
    benches = []
    for si, s in enumerate(SOURCES):
        n = 40
        Y = (rs.rand(M, n) < expit(np.linspace(-1, 1, M)[:, None] - rs.normal(0, 1, n))).astype(float)
        benches.append(Bench(s, np.arange(n) + 100 * si, Y, ["k%d" % j for j in range(n)]))
    W = [np.ones(B.n) for B in benches]
    fulls = [full_fit(B, w) for B, w in zip(benches, W)]
    o1 = lomo_orders(benches, W, fulls)
    m = 5
    flipped = [Bench(B.name, B.ids, B.Y.copy(), ["k%d" % j for j in range(B.n)]) for B in benches]
    for B in flipped:
        B.Y[m] = 1 - B.Y[m]
    f2 = [full_fit(B, w) for B, w in zip(flipped, W)]
    o2 = lomo_orders(flipped, W, f2)
    k = k_of(0.10, 40)
    for bi in range(6):
        assert set(o1[m][bi][:k]) == set(o2[m][bi][:k]), "LOMO selection of m used m's own responses"
    i1, i2 = insample_orders(benches, fulls), insample_orders(flipped, f2)
    assert any(set(i1[bi][:k]) != set(i2[bi][:k]) for bi in range(6)), "in-sample selection insensitive to m (vacuous check)"


def st_twins():
    text = {1: "a", 2: "b", 3: "a", 4: "c", 5: "c", 6: "b", 7: "d", 8: "d"}
    ev = frozenset({3, 4, 5, 6, 7})
    tw, nt = r1_twins(text, ev)
    assert (tw, nt) == ([3, 6, 7], 3), (tw, nt)                  # 4 and 5 share only an EVAL text: not twins
    keep, drop = collapse(text, [1, 2, 4, 5, 8])
    assert (keep, drop) == ([1, 2, 4, 8], [5]), (keep, drop)
    try:
        r1_twins(text, frozenset({99}))
        raise AssertionError("missing text not refused")
    except SystemExit as e:
        assert "no corpus_questions row" in str(e)


def _st():
    return dict(reg=dict(REG), M=18, pairs=153, disc_lomo=7, tau_lomo=0.90, lo=0.85, hi=0.95, se=0.02, B_done=200, tau_in=0.95,
                neff={GPQA: 0.45, MMLU: 0.25}, sat4={GPQA: 0.08, MMLU: 0.35}, pll2={s: -10.0 for s in SOURCES},
                pllR={s: -11.0 for s in SOURCES}, curve_lomo=[(0.05, 0.85), (0.10, 0.90), (0.15, 0.95)], k={s: 10 for s in SOURCES},
                k_total=60, n_total=600, C_total=550, kish=1.1)


def st_verdicts():
    L, w1, w2, fired = verdict_lines(_st())
    assert w1 == "KEEPS-RANKING" and w2 == "GPQA-OPEN" and fired is False
    assert "  SI1 -> KEEPS-RANKING (descriptive-only by support)" in L
    assert any(ln.startswith("RULE 8: KEEPS-RANKING is not refuted") for ln in L)
    assert "FALSIFIER F-SI: NOT FIRED (SI1 reads KEEPS-RANKING)" in L
    p1 = [ln for ln in L if ln.startswith("P1:")][0]
    assert "Brier 0.1800" in p1 and p1.endswith("HELD"), p1               # (0.7-1)^2 + (0.3-0)^2
    p2 = [ln for ln in L if ln.startswith("P2:")][0]
    assert "HELD" in p2 and "Brier 0.0800" in p2, p2                      # (0.8-1)^2 + (0.2-0)^2
    p3 = [ln for ln in L if ln.startswith("P3:")][0]
    assert "Brier 0.0200" in p3 and p3.endswith("P3 HELD"), p3
    assert [ln for ln in L if ln.startswith("P4:")][0].endswith("P4 HELD")
    assert "on 6 of 6 benchmarks (>= 5): HELD" in [ln for ln in L if ln.startswith("P5:")][0]
    p6 = [ln for ln in L if ln.startswith("P6:")][0]
    assert "is 10% in [5%, 25%]: HELD" in p6, p6
    s = _st()
    s.update(tau_lomo=0.91, lo=0.80, hi=0.89)                 # KEEPS with the upper bound below the bar: F-SI must NOT fire
    L, w1, _w2, fired = verdict_lines(s)
    assert w1 == "KEEPS-RANKING" and fired is False and "FALSIFIER F-SI: NOT FIRED (SI1 reads KEEPS-RANKING)" in L
    s = _st()
    s.update(tau_lomo=0.8999999, hi=0.90, disc_lomo=8)
    L, w1, w2, fired = verdict_lines(s)
    assert w1 == "LOSES-RANKING" and fired is False
    assert any(ln.startswith("RULE 8: KEEPS-RANKING is REFUTED") and "8 discordant pairs of 153" in ln for ln in L)
    assert any(ln.startswith("FALSIFIER F-SI: NOT FIRED (LOSES-RANKING but the 95% upper bound 0.9000 >= 0.90)") for ln in L)
    assert "Brier 0.9800" in [ln for ln in L if ln.startswith("P1:")][0]
    s.update(hi=0.8999)
    L, w1, w2, fired = verdict_lines(s)
    assert fired is True and any(ln.startswith("FALSIFIER F-SI: FIRED") for ln in L)
    s.update(neff={GPQA: 0.25, MMLU: 0.25}, tau_in=0.5, sat4={GPQA: 0.15, MMLU: 0.35}, curve_lomo=[(0.05, 0.5), (0.30, 0.95)],
             pll2={s_: (-10.0 if i < 4 else -12.0) for i, s_ in enumerate(SOURCES)})
    L, w1, w2, fired = verdict_lines(s)
    assert w2 == "NOT-SHOWN" and "  SI2 -> NOT-SHOWN" in L
    assert "FAILED" in [ln for ln in L if ln.startswith("P2:")][0]
    assert [ln for ln in L if ln.startswith("P3:")][0].endswith("P3 FAILED")
    assert [ln for ln in L if ln.startswith("P4:")][0].endswith("P4 FAILED")
    assert "on 4 of 6 benchmarks (>= 5): FAILED" in [ln for ln in L if ln.startswith("P5:")][0]
    assert "is 30% in [5%, 25%]: FAILED" in [ln for ln in L if ln.startswith("P6:")][0]
    s.update(curve_lomo=[(0.05, 0.5), (0.5, 0.89)], tau_lomo=0.5, se=0.01)
    L, _w1, _w2, _f2 = verdict_lines(s)
    assert any(ln.startswith("P6: no subset share <= 50%") for ln in L)
    sl = support_lines(s)
    assert any("SCOREABLE at the realised SE" in ln for ln in sl)
    assert any("MDE80 = 2.8 x SE = 0.0280" in ln for ln in sl)
    s.update(tau_lomo=0.89, se=0.01)
    assert any("DESCRIPTIVE-ONLY at the realised SE" in ln for ln in support_lines(s))
    assert any("n_eff = 60 / 1.1000 = 55" in ln for ln in support_lines(s))
    assert si1_word(0.9, 0.90) == "KEEPS-RANKING" and si1_word(0.9 - 1e-9, 0.90) == "LOSES-RANKING"
    assert si2_word(0.3, 0.2) == "GPQA-OPEN" and si2_word(np.float64(0.2), np.float64(0.2)) == "NOT-SHOWN"


def _check_against_oracle(buf, spec, cfg):
    orc = _oracle(spec, cfg.reg)
    l1 = _line(buf, "SI1 (DECIDING")
    tau = _num(l1, "tau_LOMO = ")
    assert abs(tau - orc["tau_lomo"]) <= 5.0001e-5, ("tau_LOMO", tau, orc["tau_lomo"])
    assert ("discordant %d)" % orc["disc"]) in l1, ("discordant pairs", l1, orc["disc"])
    w = "KEEPS-RANKING" if orc["tau_lomo"] >= 0.90 else "LOSES-RANKING"
    assert _line(buf, "  SI1 -> ") == "  SI1 -> %s (descriptive-only by support)" % w
    p2 = _line(buf, "P2:")
    assert abs(_num(p2, "tau_in-sample ") - orc["tau_in"]) <= 5.0001e-5, ("tau_in", p2, orc["tau_in"])
    l2 = _line(buf, "SI2 (SCORED")
    assert abs(_num(l2, "NEFF_GPQA = ") - orc["neff"][GPQA]) <= 5.0001e-5 and abs(_num(l2, "NEFF_MMLU_PRO_LB = ") - orc["neff"][MMLU]) <= 5.0001e-5, (l2, orc["neff"])
    assert _line(buf, "  SI2 -> ") == "  SI2 -> %s" % ("GPQA-OPEN" if orc["neff"][GPQA] > orc["neff"][MMLU] else "NOT-SHOWN")
    for s in SOURCES:
        ln = [x for x in buf if x.startswith("  %-11s N " % s)][0]
        assert int(_num(ln, "N ")) == orc["n"][s], (s, ln, orc["n"][s])
        assert abs(_num(ln, "SAT4 ") - orc["sat4"][s]) <= 5.0001e-5, (s, ln, orc["sat4"][s])
        assert abs(_num(ln, "NEFF ") - orc["neff"][s]) <= 5.0001e-5
    assert _line(buf, "  top 4 (").endswith(", ".join(orc["top4"]))
    # the scorer header line (deviation (1)) and the H sensitivity lines against the oracle re-keyed by H
    assert _line(buf, "MATH scorer: ") == ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table"
                                           " sha256-lf %s); MATH-FIX beside: no" % cfg.h_sha)
    oh = _oracle(spec, cfg.reg, h=True)
    assert _line(buf, "SENSITIVITY H (").endswith("table sha256-lf %s (the pin, verified)" % cfg.h_sha)
    hc = _line(buf, "  H: MATH %d items " % orc["n"]["MATH"])
    want = "  H: MATH %d items x 18 models = %d cells; official correct %d; H correct %d (+%d)" % (
        orc["n"]["MATH"], 18 * orc["n"]["MATH"], orc["nmath"], oh["nmath"], oh["nmath"] - orc["nmath"])
    assert hc == want, (hc, want)
    assert oh["nmath"] > orc["nmath"], "the fixture's H must differ from the official verdict"
    ht = _line(buf, "  H: tau_LOMO_H = ")
    assert abs(_num(ht, "tau_LOMO_H = ") - oh["tau_lomo"]) <= 5.0001e-5, ("tau_LOMO_H", ht, oh["tau_lomo"])
    assert ("(discordant %d of 153)" % oh["disc"]) in ht, (ht, oh["disc"])
    assert abs(_num(ht, "the official tau_LOMO ") - orc["tau_lomo"]) <= 5.0001e-5
    assert abs(_num(ht, "tau_in-sample_H = ") - oh["tau_in"]) <= 5.0001e-5, (ht, oh["tau_in"])
    from scipy.stats import kendalltau
    tmo = kendalltau(orc["macro"], oh["macro"])[0]
    assert abs(_num(ht, "full macro H) = ") - tmo) <= 5.0001e-5, (ht, tmo)
    sh = max(abs(oh["rank"].index(m) - orc["rank"].index(m)) for m in FX_MODELS)
    assert ht.endswith("max |rank shift| %d" % sh), (ht, sh)
    hn = _line(buf, "  H: MATH NEFF_H ")
    assert abs(_num(hn, "NEFF_H ") - oh["neff"]["MATH"]) <= 5.0001e-5 and abs(_num(hn, "(official ") - orc["neff"]["MATH"]) <= 5.0001e-5, (hn, oh["neff"])
    assert abs(_num(hn, "SAT4_H ") - oh["sat4"]["MATH"]) <= 5.0001e-5, (hn, oh["sat4"])
    assert hn.endswith("top 4 under H: " + ", ".join(oh["top4"])), (hn, oh["top4"])
    orc["h_top4"] = oh["top4"]
    for ln in buf:
        if ln.startswith("    ") and " | " in ln and ln.strip()[0].isdigit() and len(ln.split("|")) == 6:
            r, name, mac, mic = [x.strip() for x in ln.split("|")[:4]]
            m = sorted(FX_MODELS).index(name)
            assert abs(float(mac) - orc["macro"][m]) <= 5.0001e-5 and abs(float(mic) - orc["micro"][m]) <= 5.0001e-5, ln
    return orc


def st_run_e2e():
    import tempfile
    # (kind, seed, items per source, the SI1 word the fixture must yield: KEEPS on the strong fixture, LOSES on the others)
    moved, mm = {}, {}
    for kind, seed, n, want in (("strong", 5, (200,) * 6, "KEEPS-RANKING"), ("struct", 5, None, "LOSES-RANKING"),
                                ("noise", 6, None, "LOSES-RANKING")):
        d = tempfile.mkdtemp(prefix="si_e2e_")
        try:
            spec = _spec(kind=kind, seed=seed, **({"n": n} if n else {}), **({"mutate": _mm_skew} if kind == "noise" else {}))
            cfg = _layout(d, spec)
            rc, buf, err = _main(cfg, ["--run"])
            assert err is None, err
            assert buf[0].startswith("POOL %s verified" % cfg.reg["r1_pool"]), buf[0]
            assert _line(buf, "  SI1 -> ") == "  SI1 -> %s (descriptive-only by support)" % want, (kind, _line(buf, "  SI1 -> "))
            orc = _check_against_oracle(buf, spec, cfg)
            moved[kind] = set(orc["h_top4"]) != set(orc["top4"])
            fx = sorted(FX_MODELS)
            mic4 = [fx[m] for m in sorted(range(18), key=lambda m: (-orc["micro"][m], fx[m]))[:4]]
            mm[kind] = bool(set(mic4) != set(orc["top4"]))
            assert _line(buf, "R1: %d EVAL ids / 6 distinct texts" % len(spec["tw_ids"])) and orc["tw"] == len(spec["tw_ids"]) == 7
            for s in SOURCES:
                ln = [x for x in buf if x.startswith("  %-11s N " % s)][0]
                assert int(_num(ln, "ALL ")) == orc["all"][s] and int(_num(ln, "NONE ")) == orc["none"][s], (s, ln, orc["all"][s], orc["none"][s])
            # the component draws, re-derived independently: default_rng(seed), benchmarks in SOURCES order, clusters within benchmark
            # bootstrap interval = the percentiles of the cached replicates; replicate 0 = the oracle on the expanded matrix
            o, figs, cache = outputs(cfg, False)
            rows = [json.loads(x) for x in open(cache, encoding="utf-8").read().split("\n")[1:] if x.strip()]
            taus = [r["tau"] for r in sorted(rows, key=lambda r: r["r"])]
            assert len(taus) == cfg.reg["B"]
            l1 = _line(buf, "SI1 (DECIDING")
            assert ("[%.4f, %.4f]" % (pctl(taus, 2.5), pctl(taus, 97.5))) in l1, (l1, taus)
            assert ("SE %.4f" % float(np.std(taus, ddof=1))) in l1
            data = read_inputs(cfg, lambda s: None, keyed=True)
            Wd = boot_weights(data["benches"], cfg.reg["B"], cfg.reg["seed"])
            rng = np.random.default_rng(cfg.reg["seed"])
            for r in range(cfg.reg["B"]):
                for bi, B in enumerate(data["benches"]):
                    keys = sorted(set(stem_key(spec["text"][int(q)]) for q in B.ids))
                    draw = rng.integers(0, len(keys), len(keys))
                    want = np.array([sum(1 for x in draw if keys[x] == stem_key(spec["text"][int(q)])) for q in B.ids], dtype=float)
                    assert np.array_equal(Wd[r][bi], want), ("component draws", r, B.name)
            ow = _oracle(spec, cfg.reg, weights=[[w for w in Wd[0][si]] for si in range(6)])
            assert np.allclose(rows[0]["full"], ow["macro"], atol=1e-12), "replicate 0 full macro != the oracle's expanded"
            # [R-d] replicate 0 = the same pipeline on the EXPANDED (duplicated-copy) benchmarks with unit weights
            eb = []
            for B, w in zip(data["benches"], Wd[0]):
                idx = np.repeat(np.arange(B.n), w.astype(int))
                eb.append(Bench(B.name, B.ids[idx], B.Y[:, idx], [str(i) for i in idx]))
            W1 = [np.ones(B.n) for B in data["benches"]]
            f1 = [full_fit(B, w) for B, w in zip(data["benches"], W1)]
            te, sce, mace = replicate(eb, [np.ones(B.n) for B in eb], f1_expand(f1, data["benches"], Wd[0]), cfg.reg["share"])
            assert abs(taus[0] - te) < 1e-6 and np.allclose(rows[0]["lomo"], sce, atol=1e-9), ("replicate 0 vs expanded", taus[0], te)
            # the outcome of record and the figure files
            text = open(o, encoding="utf-8").read()
            assert text.startswith("POOL ") and l1 in text
            assert text.split("\n")[2] == scorer_line(cfg.h_sha), text.split("\n")[:4]      # the header line, after POOL / rule 7
            assert _line(buf, "SENSITIVITY H (") in text and _line(buf, "  H: tau_LOMO_H = ") in text
            pay = {k: json.load(open(p, encoding="utf-8")) for k, p in figs.items()}
            assert abs(pay["topk"]["taus"]["lomo"] - orc["tau_lomo"]) <= 5.0001e-5
            assert len(pay["items"]["items"]) == sum(orc["n"].values())
            for b in pay["benchmarks"]["benchmarks"]:
                assert abs(b["sat4"] - orc["sat4"][b["benchmark"]]) < 1e-12 and abs(b["neff"] - orc["neff"][b["benchmark"]]) < 1e-12
            for t in [spec["text"][q] for q in spec["qids"] if spec["src"][q] == GPQA]:
                assert t not in text and all(t not in json.dumps(v) for v in pay.values()), "GPQA text released"
            # write-once: a second --run refuses before any read
            rc2, buf2, err2 = _main(cfg, ["--run"])
            assert err2 and "write-once" in err2 and not buf2, err2
        finally:
            _rm(d)
    assert moved == {"strong": False, "struct": False, "noise": True}, ("H must change the top-4 set on the noise fixture", moved)
    assert mm["noise"] is True, ("B1: the micro top-4 set must differ from the macro top-4 set on the noise fixture", mm)


def _mm_skew(spec, model="m15", big="MMLU_PRO", small="IFEVAL"):
    """B1 (delta review 2): `model` answers every item of the largest source and none of the smallest, so its micro accuracy
    rises while its macro accuracy barely moves; on the noise fixture (seed 6) m15 is third by micro (0.568), seventh by macro (0.513)."""
    for q in spec["qids"]:
        c = spec["cells"][q]
        if model in c and spec["src"][q] in (big, small):
            c[model] = (int(spec["src"][q] == big), c[model][1])


def f1_expand(fulls, benches, W):
    """The point fits re-indexed onto expanded benchmarks (warm starts only)."""
    out = []
    for ff, B, w in zip(fulls, benches, W):
        idx = np.repeat(np.arange(B.n), w.astype(int))
        out.append(dict(ff, a_full=ff["a_full"][idx], b_full=ff["b_full"][idx]))
    return out


def st_sha():
    import tempfile
    d = tempfile.mkdtemp(prefix="si_sha_")
    try:
        cfg = _layout(d, _spec(seed=19))

        def touch():
            with open(cfg.mc_db, "ab") as f:
                f.write(b"x")
        cfg.during_read = touch
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "a DB changed during the read" in err and "multicorpus False" in err, err
        assert not os.path.exists(outputs(cfg, False)[0])
    finally:
        _rm(d)


def st_resume():
    import tempfile
    d1, d2 = tempfile.mkdtemp(prefix="si_r1_"), tempfile.mkdtemp(prefix="si_r2_")
    try:
        spec = _spec(seed=11)
        c1, c2 = _layout(d1, spec), _layout(d2, spec)
        rc, bp, err = _main(c1, ["--pilot", "2"])
        assert err is None, err
        assert bp[0].startswith("POOL ") and any(x.startswith("PILOT (2 component / 2 parametric") for x in bp)
        o1, _f1, cache1 = outputs(c1, False)
        assert not os.path.exists(o1) and os.path.exists(outputs(c1, True)[0]), "the pilot wrote the record"
        rc, b1, err = _main(c1, ["--run"])
        assert err is None, err
        assert any("2 of 6 replicates present" in x for x in b1)
        crow = [json.loads(x)["r"] for x in open(cache1, encoding="utf-8").read().splitlines()[1:] if x.strip()]
        assert sorted(crow) == list(range(6)), ("cache rows after resume", crow)
        rc, b2, err = _main(c2, ["--run"])
        assert err is None, err
        def strip(b, d):
            return [x.replace(d, "<D>") for x in b if "replicate cache" not in x and not x.startswith("%s written" % TAG)
                    and not x.startswith("FITS:")]
        assert strip(b1, d1) == strip(b2, d2), [(a, b) for a, b in zip(strip(b1, d1), strip(b2, d2)) if a != b][:3]
        # a changed setting refuses on the pinned meta
        os.remove(o1)
        for p in _f1.values():
            os.remove(p)
        c1.reg["seed"] = c1.reg["seed"] + 1
        rc, b3, err = _main(c1, ["--run"])
        assert err and "meta" in err and "REFUSED" in err, err
        # a partial cache writes _partial, never the record
        c3 = _layout(tempfile.mkdtemp(prefix="si_r3_"), spec, reg_over=dict(B=4))
        os.makedirs(c3.out_dir)
        st_ = dict(B_done=1)
        p = write_outputs(c3, ["x"], None, st_, (outputs(c3, False)[0],) + outputs(c3, False)[1:] + ("", "", False), False)
        assert p.endswith("_partial.txt") and not os.path.exists(outputs(c3, False)[0])
        _rm(os.path.dirname(c3.out_dir))
    finally:
        _rm(d1)
        _rm(d2)


def st_refusals():
    import tempfile
    cases = [
        ("twins", None, dict(twins_ids=5), "R1 twins 7 / 6 != the registered 5 / 6"),
        ("twins_texts", None, dict(twins_texts=5), "R1 twins 7 / 6 != the registered 7 / 5"),
        ("roster", lambda s: s["registry"].pop(0), None, "roster check failed (17 models"),
        ("excluded", lambda s: s["registry"].__setitem__(-1, (EXCLUDED, "ACTIVE")), dict(roster=19), "roster check failed (19 models"),
        ("poolrow", None, dict(comp_eval=1), "the v2 pool row differs"),
        ("source", lambda s: s["rsrc"].__setitem__(s["qids"][3], "BBH"), None, "source 'BBH' != corpus_questions source"),
        ("dup", lambda s: s["dups"].append((s["qids"][1], FX_MODELS[0], 0)), None, "carries more than one response row"),
        ("incomplete", None, dict(incomplete_max=0.0), "lack one of the 18 cells"),
        ("sources", lambda s: s["src"].__setitem__(s["qids"][2], "ARC"), None, "corpus_questions sources"),
    ]
    for name, mut, over, want in cases:
        d = tempfile.mkdtemp(prefix="si_ref_")
        try:
            cfg = _layout(d, _spec(seed=13, mutate=mut), reg_over=over)
            rc, buf, err = _main(cfg, ["--run"])
            assert err is not None and want in err, (name, err)
            assert not os.path.exists(outputs(cfg, False)[0]), name
        finally:
            _rm(d)
    d = tempfile.mkdtemp(prefix="si_busy_")
    try:
        cfg = _layout(d, _spec(seed=13))
        with open(cfg.busy, "w", encoding="utf-8") as f:
            f.write("exit 0\n")
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "exited 0" in err and not buf, err
        rc, buf, err = _main(cfg, ["--dry-run"])
        assert err and "exited 0" in err and not buf, err
        cfg.busy = os.path.join(d, "absent.ps1")
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "is absent" in err, err
    finally:
        _rm(d)


def st_hrefusals():
    """The H table: a differing sha (run and dry-run), an absent file and CR bytes refuse BEFORE any pool read (nothing printed);
    a wrong header, a missing kept cell and a row disagreeing with the official verdict (both directions) refuse at the H line,
    with the table re-pinned so that the sha check is not what catches them; nothing is written in any case."""
    import tempfile
    d = tempfile.mkdtemp(prefix="si_h_")
    try:
        spec = _spec(seed=13)
        cfg = _layout(d, spec)
        good = cfg.h_sha
        for argv in (["--run"], ["--dry-run"]):
            cfg.h_sha = "0" * 64
            rc, buf, err = _main(cfg, argv)
            assert err and ("is sha256-lf %s, not the pinned %s" % (good, "0" * 64)) in err and not buf, (argv, err, buf[:2])
        cfg.h_sha = good
        hp = cfg.h_path
        cfg.h_path = os.path.join(d, "absent.csv")
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "is absent" in err and not buf, err
        cfg.h_path = hp
        cfg.h_sha = _write_h(hp, spec["h"], eol=b"\r\n")
        rc, buf, err = _main(cfg, ["--dry-run"])
        assert err and "carries CR bytes" in err and not buf, err
        cfg.h_sha = _write_h(hp, spec["h"], header="question_id,model,H_score,route")
        rc, buf, err = _main(cfg, ["--run"])
        assert err and "the H table header" in err and not buf, err
        q0 = [q for q in spec["qids"] if spec["src"][q] == "MATH"][0]           # MATH item 0: kept and complete
        cases = (("missing", lambda h: h.pop((q0, FX_MODELS[3])), "lacks the MATH cell (%d, %s)" % (q0, FX_MODELS[3])),)
        q1 = [q for q in spec["qids"] if spec["src"][q] == "MATH" and spec["cells"][q][FX_MODELS[0]][0] == 1][0]
        q2 = [q for q in spec["qids"] if spec["src"][q] == "MATH" and spec["cells"][q][FX_MODELS[0]][0] == 0][0]
        cases += (("imported_h0", lambda h: h.__setitem__((q1, FX_MODELS[0]), (0, "imported")),
                   "row (%d, %s) H 0 route 'imported' disagrees with the official verdict 1" % (q1, FX_MODELS[0])),
                  ("off1_not_imported", lambda h: h.__setitem__((q1, FX_MODELS[0]), (1, "boxed:str")),
                   "row (%d, %s) H 1 route 'boxed:str' disagrees with the official verdict 1" % (q1, FX_MODELS[0])),
                  ("off0_imported", lambda h: h.__setitem__((q2, FX_MODELS[0]), (1, "imported")),
                   "row (%d, %s) H 1 route 'imported' disagrees with the official verdict 0" % (q2, FX_MODELS[0])))
        for name, mut, want in cases:
            h = dict(spec["h"])
            mut(h)
            cfg.h_sha = _write_h(hp, h)
            rc, buf, err = _main(cfg, ["--run"])
            assert err and want in err, (name, err)
            assert buf and buf[0].startswith("POOL "), name
            assert not os.path.exists(outputs(cfg, False)[0]), name
        o_ = outputs(cfg, False)[0]
        assert not os.path.exists(o_)
    finally:
        _rm(d)


def st_dry_run():
    import tempfile
    d = tempfile.mkdtemp(prefix="si_dry_")
    try:
        spec = _spec(seed=17)
        cfg = _layout(d, spec)
        rc, buf, err = _main(cfg, ["--dry-run"])
        assert err is None, err
        assert buf[0].startswith("POOL %s verified" % cfg.reg["r1_pool"])
        assert not any(x.startswith(("SI1", "SI2", "P1", "FALSIFIER", "SUPPORT", "SENSITIVITY", "  H: ")) for x in buf), "a statistic in the dry-run"
        assert buf[2] == scorer_line(cfg.h_sha), buf[:4]
        assert buf[3].startswith("  H table %s: %d rows; sha256-lf %s EQUAL" % (cfg.h_path, len(spec["h"]), cfg.h_sha)), buf[3]
        assert buf[-1].startswith("DRY-RUN: no key column was selected")
        assert not os.path.exists(cfg.out_dir) and not os.path.exists(cfg.blog_dir), "the dry-run wrote"
        assert any(x.startswith("  gen_view.response_lite rows of the roster:") for x in buf)
        # the sealed key: a key statement in dry-run mode is refused by the tripwire
        tw, _s = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view", lambda s: None)
        try:
            tw.execute("SELECT is_correct FROM response_lite")
            raise AssertionError("key read while sealed")
        except SystemExit as e:
            assert "SEALED" in str(e)
        finally:
            tw.close()
    finally:
        _rm(d)


# B1: the source labels of record, as corpus_questions and both v2 views carry them (READY review 0cd7fb5e: the real
# --dry-run's refusal line printed them; recounted there: MMLU_PRO 11,637 / BBH 5,757 / MATH 1,309 / MUSR 756 / GPQA 546 /
# IFEVAL 541 kept). A literal, independent of SOURCES: the fixtures are built from SOURCES and could not see B1.
REAL_DB_LABELS = ("BBH", "GPQA", "IFEVAL", "MATH", "MMLU_PRO", "MUSR")
# L-2 (delta review 2): the H table pin of record (math_scorer_h.py --run 62d269af; registrar 40cd6d41), a literal the fixtures
# cannot move (they carry their own sha).
H_SHA_OF_RECORD = "6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1"
SELF_NAME = "saturation_irt"


def st_labels():
    import tempfile
    assert tuple(sorted(SOURCES)) == REAL_DB_LABELS, (sorted(SOURCES), REAL_DB_LABELS)
    assert H_SHA == H_SHA_OF_RECORD, (H_SHA, H_SHA_OF_RECORD)
    assert MMLU == "MMLU_PRO" and GPQA == "GPQA", (MMLU, GPQA)
    assert len(set(SOURCES)) == 6
    d = tempfile.mkdtemp(prefix="si_lab_")
    try:
        spec = _spec(seed=19)
        assert tuple(sorted(set(spec["src"].values()))) == REAL_DB_LABELS, sorted(set(spec["src"].values()))
        cfg = _layout(d, spec)
        rc, buf, err = _main(cfg, ["--dry-run"])
        assert err is None, err
        r1 = _line(buf, "R1: 7 EVAL ids / 6 distinct texts")
        assert " MMLU_PRO 1," in r1 and "MMLU_PRO_LB" not in r1, r1
        assert any(x.startswith("  MMLU_PRO    kept ") for x in buf), [x for x in buf if "kept" in x]
        assert buf[-1].startswith("DRY-RUN: no key column was selected"), buf[-1]
    finally:
        _rm(d)

    def relabel(sp):
        for q, s_ in list(sp["src"].items()):
            if s_ == "MMLU_PRO":
                sp["src"][q] = "MMLU_PRO_LB"
    d = tempfile.mkdtemp(prefix="si_lab_")
    try:
        cfg = _layout(d, _spec(seed=19, mutate=relabel))
        rc, buf, err = _main(cfg, ["--dry-run"])
        want = ("corpus_questions sources ['BBH', 'GPQA', 'IFEVAL', 'MATH', 'MMLU_PRO_LB', 'MUSR'] != the six registered "
                "['BBH', 'GPQA', 'IFEVAL', 'MATH', 'MMLU_PRO', 'MUSR']")
        assert err is not None and want in err, err
        assert not any(x.startswith("--- v2 views") for x in buf), "views opened after a source refusal"
    finally:
        _rm(d)


def st_branch_cover():
    missing = [b for b in BRANCHES if not HIT[b]]
    assert not missing, "print branches never executed: %s" % missing


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


CASES = (("grad", st_grad), ("weights", st_weights), ("recover", st_recover), ("select", st_select), ("taub", st_taub),
         ("lomo", st_lomo), ("twins", st_twins), ("verdicts", st_verdicts), ("run_e2e", st_run_e2e), ("resume", st_resume),
         ("refusals", st_refusals), ("hrefusals", st_hrefusals), ("sha", st_sha), ("dry_run", st_dry_run), ("labels", st_labels),
         ("busyself", st_busyself), ("branches", st_branch_cover))


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
            if not quiet:
                import traceback
                print("  FAIL %-10s %s: %s" % (name, type(e).__name__, str(e)[:800]), flush=True)
                traceback.print_exc()
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(only=None):
    import tempfile
    import scratch_dir   # noqa: F401
    NL = chr(10)
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
            mod = types.ModuleType("saturation_irt_mutant")
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
    ("X01 SI1 strict at the bar (tau exactly 0.90 loses)", 'bool(round(tau, 12) >= bar)', 'bool(round(tau, 12) > bar)'),
    ("X02 SI1 words inverted", 'return "KEEPS-RANKING" if bool(round(tau, 12) >= bar) else "LOSES-RANKING"', 'return "LOSES-RANKING" if bool(round(tau, 12) >= bar) else "KEEPS-RANKING"'),
    ("X03 F-SI fires at hi exactly 0.90 (boundary)", 'word == "LOSES-RANKING" and hi < bar', 'word == "LOSES-RANKING" and hi <= bar'),
    ("X04 F-SI without the LOSES clause", 'return bool(word == "LOSES-RANKING" and hi < bar)', 'return bool(hi < bar)'),
    ("X05 F-SI read on the lower bound", 'fired = fsi_fired(w1, hi, bar)', 'fired = fsi_fired(w1, st["lo"], bar)'),
    ("X06 SI2 at equality (>=)", 'bool(neff_g > neff_m)', 'bool(neff_g >= neff_m)'),
    ("X07 SI2 populations swapped", 'ng, nm = st["neff"][GPQA], st["neff"][MMLU]', 'nm, ng = st["neff"][GPQA], st["neff"][MMLU]'),
    ("X08 LOMO keeps model m (in-sample selection)", 'rows = np.array([i for i in range(M) if i != m], dtype=np.int64)', 'rows = np.array([i for i in range(M)], dtype=np.int64)'),
    ("X09 LOMO constant rule over all 18 models", '            cols = nonconst(Ym, w)', '            cols = nonconst(B.Y, w)'),
    ("X10 LOMO allows constant items", '            cols = nonconst(Ym, w)', '            cols = np.where(w > 0)[0]'),
    ("X11 order by a ascending (min<->max)", 'np.lexsort((ids[cols], -np.asarray(a)))', 'np.lexsort((ids[cols], np.asarray(a)))'),
    ("X12 tie-break by id descending", 'np.lexsort((ids[cols], -np.asarray(a)))', 'np.lexsort((-ids[cols], -np.asarray(a)))'),
    ("X13 LOMO ranked by b, not a", 'om.append(order_by_a(f["a"], B.ids, cols))', 'om.append(order_by_a(f["b"], B.ids, cols))'),
    ("X14 k_b by ceiling", 'int(math.floor(share * total + 0.5))', 'int(math.ceil(share * total))'),
    ("X15 k_b on the non-constant count", 'k = k_of(share, float(w.sum()))', 'k = k_of(share, float(len(orders_of_m(m)[bi])))'),
    ("X16 boundary copies dropped", 'take, k_eff = np.minimum(wo, np.maximum(0.0, k - (cw - wo))), float(k)', 'take, k_eff = wo * (cw <= k), float(k)'),
    ("X17 SI1 against the micro ranking", 'tau_lomo=tau_b(sc_lomo, macro)', 'tau_lomo=tau_b(sc_lomo, micro)'),
    ("X18 SI1 from the in-sample subset", 'tau_lomo=tau_b(sc_lomo, macro)', 'tau_lomo=tau_b(sc_in, macro)'),
    ("X19 macro = the first benchmark only (first site)", 'return A, A.mean(1), num / den', 'return A, A[:, 0], num / den'),
    ("X20 micro = macro", 'return A, A.mean(1), num / den', 'return A, A.mean(1), A.mean(1)'),
    ("X21 tau-b denominator as tau-a", 'den = math.sqrt((c + d + tx) * (c + d + ty))', 'den = float(c + d + tx + ty)'),
    ("X22 discordant counts ties", '* (y[i] - y[j]) < 0)', '* (y[i] - y[j]) <= 0)'),
    ("X23 top 4 = the bottom 4 (min<->max)", 'top4 = rank[:int(reg["top"])]', 'top4 = rank[-int(reg["top"]):]'),
    ("X24 NEFF over the fitted items, not N_b", 'neff[B.name] = float((inf >= reg["info_min"]).sum() / B.n)', 'neff[B.name] = float((inf >= reg["info_min"]).sum() / max(1, len(ff["cols"])))'),
    ("X25 NEFF at the mean theta of all models", 'th4 = float(np.mean(ff["theta"][top4]))', 'th4 = float(np.mean(ff["theta"]))'),
    ("X26 SAT4 any-of-4 instead of all-of-4", 'sat4[B.name] = float((B.Y[top4].min(0) == 1).sum() / B.n)', 'sat4[B.name] = float((B.Y[top4].max(0) == 1).sum() / B.n)'),
    ("X27 ALL / NONE swapped", 'int((s == M).sum()), int((s == 0).sum())', 'int((s == 0).sum()), int((s == M).sum())'),
    ("X28 in-sample tau from the LOMO orders", 'sc_in, _s = subset_scores(benches, W1, lambda m: ins, reg["share"])', 'sc_in, _s = subset_scores(benches, W1, lambda m: orders[m], reg["share"])'),
    ("X29 R1 outside set includes EVAL ids", 'outside = {t for q, t in text.items() if q not in eval_ids}', 'outside = {t for q, t in text.items()}'),
    ("X30 collapse keeps the highest id", '        lo = min(g)', '        lo = max(g)'),
    ("X31 twins not dropped (collapse only)", 'keep, drop = collapse(text, [q for q in sorted(text) if q not in tws])', 'keep, drop = collapse(text, sorted(text))'),
    ("X32 MATH-FIX overlay re-introduced (D-2026-10-08-5 delta)", 'source, is_correct FROM %s WHERE', 'source, COALESCE(is_correct_mathfix, is_correct) FROM %s WHERE'),
    ("X33 EVAL side not read (wrong split side)", ', (etw, "response", "eval_view")):', '):'),
    ("X34 incomplete refusal removed", 'if ninc > reg["incomplete_max"] * len(keep):', 'if False:'),
    ("X35 duplicate-row refusal removed", '                if m in K[q]:', '                if False:'),
    ("X36 source refusal removed", '                if src.get(q) != s:', '                if False:'),
    ("X37 excluded model admitted", 'if len(models) != reg["roster"] or EXCLUDED in models or rg != re_:', 'if len(models) != reg["roster"] or rg != re_:'),
    ("X38 roster size not checked", 'if len(models) != reg["roster"] or EXCLUDED in models or rg != re_:', 'if EXCLUDED in models or rg != re_:'),
    ("X39 pool-row refusal removed", 'if nc != reg["comp_eval"] or ni != reg["n_eval"]:', 'if False:'),
    ("X40 twins refusal removed", 'if len(tw) != reg["twins_ids"] or tw_texts != reg["twins_texts"]:', 'if False:'),
    ("X41 busy exit 0 accepted", '    if rc != 1:', '    if rc not in (0, 1):'),
    ("X42 write-once pre-check removed", '            if os.path.exists(p):', '            if False:'),
    ("X43 multicorpus sha check dropped", 'if not (ok_g and ok_e and mc_after == mc_before):', 'if not (ok_g and ok_e):'),
    ("X44 component bootstrap on another seed", 'draws = boot_weights(benches, int(reg["B"]), int(reg["seed"]))', 'draws = boot_weights(benches, int(reg["B"]), int(reg["seed"]) + 1)'),
    ("X45 bootstrap resamples items, not clusters", 'cnt = np.bincount(rng.integers(0, Bn.C, Bn.C), minlength=Bn.C)' + NL + '            Ws.append(cnt[Bn.cl].astype(np.float64))', 'cnt = np.bincount(rng.integers(0, Bn.n, Bn.n), minlength=Bn.n)' + NL + '            Ws.append(cnt.astype(np.float64))'),
    ("X46 interval 5 / 95", '(pctl(taus, 2.5), pctl(taus, 97.5))', '(pctl(taus, 5), pctl(taus, 95))'),
    ("X47 SE with ddof 0", 'float(np.std(taus, ddof=1))', 'float(np.std(taus, ddof=0))'),
    ("X48 replicate full macro at the point", '    _A, macro, _mi = accs(benches, W)', '    _A, macro, _mi = accs(benches, [np.ones(B.n) for B in benches])'),
    ("X49 replicate LOMO ignores the weights", '    orders = lomo_orders(benches, W, fulls, reg=reg)', '    orders = lomo_orders(benches, [np.ones(B.n) for B in benches], fulls, reg=reg)'),
    ("X50 pilot writes the record path", '    o, figs, _cache, _w1, _w2, _f2 = outs' + NL + '    text = "\\n".join(buf) + "\\n"' + NL + '    if pilot:', '    o, figs, _cache, _w1, _w2, _f2 = outs' + NL + '    text = "\\n".join(buf) + "\\n"' + NL + '    if False:'),
    ("X51 cache meta check removed", '    if got != meta:', '    if False:'),
    ("X52 cache resume recomputes done replicates", '        if r in done:' + NL + '            continue', '        if False:' + NL + '            continue'),
    ("X53 P2 direction reversed", 'ev2 = bool(st["tau_in"] >= tau)', 'ev2 = bool(st["tau_in"] <= tau)'),
    ("X54 P5 Rasch > 2PL counted", 'if st["pll2"][s] > st["pllR"][s]', 'if st["pll2"][s] < st["pllR"][s]'),
    ("X55 P6 largest share (min<->max)", '    for s, t in curve:', '    for s, t in reversed(curve):'),
    ("X56 P1 Brier on a fixed outcome", 'brier(p1probs, w1)', 'brier(p1probs, "KEEPS-RANKING")'),
    ("X57 P3 bands crossed", 'in_band(ng, bg) and in_band(nm, bm))', 'in_band(nm, bg) and in_band(ng, bm))'),
    ("X58 P4 bands crossed", 'ok4 = bool(in_band(s4m, bm4) and in_band(s4g, bg4))', 'ok4 = bool(in_band(s4m, bg4) and in_band(s4g, bm4))'),
    ("X59 rule-8 REFUTED line dropped (skip path)", '        L.append("RULE 8: KEEPS-RANKING is REFUTED', '        pass  # L.append("RULE 8: KEEPS-RANKING is REFUTED'),
    ("X60 F-SI NOT FIRED line dropped (skip path)", '        L.append("FALSIFIER F-SI: NOT FIRED (LOSES-RANKING but', '        pass  # L.append("FALSIFIER F-SI: NOT FIRED (LOSES-RANKING but'),
    ("X61 MDE80 with 1.96", 'mde = 2.8 * se if', 'mde = 1.96 * se if'),
    ("X62 n_eff on all items", 'st["k_total"] / st["kish"]))', 'st["n_total"] / st["kish"]))'),
    ("X63 dry-run reads the key", '"eval_view")):' + NL + '            if not keyed:', '"eval_view")):' + NL + '            if False:'),
    ("X64 pattern pooling ignores the weights", 'wu = np.bincount(inv, weights=w, minlength=U.shape[0])', 'wu = np.bincount(inv, minlength=U.shape[0]).astype(np.float64)'),
    ("X65 no log-a prior", '        pen = pen + al * al / (2.0 * s2a)', '        pen = pen + 0.0 * al'),
    ("X66 theta not centred", '    tr = res.x[:M]' + NL + '    th = tr - tr.mean()', '    tr = res.x[:M]' + NL + '    th = tr + 0.0'),
    ("X67 b prior variance 1 in the fit (not the registered 2^2)", 'args=(Y, w, rasch, M, float(rg["s2b"]), float(rg["s2a"]))', 'args=(Y, w, rasch, M, 1.0, float(rg["s2a"]))'),
    ("X68 a prior variance 1 in the fit (not the registered 0.5^2)", 'args=(Y, w, rasch, M, float(rg["s2b"]), float(rg["s2a"]))', 'args=(Y, w, rasch, M, float(rg["s2b"]), 1.0)'),
    ("X69 R1 twins by stem_key, not exact text", 'tw = sorted(q for q in eval_ids if text[q] in outside)', 'tw = sorted(q for q in eval_ids if stem_key(text[q]) in {stem_key(t) for t in outside})'),
    ("X70 duplicates collapsed by stem_key, not exact text", '        groups[text[q]].append(q)', '        groups[stem_key(text[q])].append(q)'),
    ("X71 B1 regression: SOURCES keyed on MMLU_PRO_LB", 'SOURCES = ("MMLU_PRO", "BBH",', 'SOURCES = ("MMLU_PRO_LB", "BBH",'),
    ("X72 B1 regression: SI2 population keyed on MMLU_PRO_LB", 'GPQA, MMLU = "GPQA", "MMLU_PRO"', 'GPQA, MMLU = "GPQA", "MMLU_PRO_LB"'),
    ("X73 source-set refusal removed", '    if srcs != sorted(SOURCES):', '    if False:'),
    # the D-2026-10-08-5 delta (official scorer + pinned H sensitivity line)
    ("X74 H sha check removed", '    if got != want:', '    if False:'),
    ("X75 H CR check removed", '    if b"\\r" in raw:', '    if False:'),
    ("X76 H table absent accepted (read attempted)", '    if not path or not os.path.isfile(path):' + NL + '        refuse("the H table', '    if not path:' + NL + '        refuse("the H table'),
    ("X77 dry-run skips the H table", 'def dry_run(cfg, say):' + NL + '    htab, hsha = load_h(cfg.h_path, cfg.h_sha)', 'def dry_run(cfg, say):' + NL + '    htab, hsha = {}, cfg.h_sha'),
    ("X78 H checked after the pool read (run)", '    htab, hsha = load_h(cfg.h_path, cfg.h_sha)' + NL + '    b = busy_check(cfg.busy)' + NL + '    data = read_inputs(cfg, say, keyed=True, pre=[b] + h_pre(cfg, htab, hsha))', '    b = busy_check(cfg.busy)' + NL + '    data = read_inputs(cfg, say, keyed=True, pre=[b])' + NL + '    htab, hsha = load_h(cfg.h_path, cfg.h_sha)' + NL + '    say(scorer_line(hsha))'),
    ("X79 H applied to another source (wrong population)", 'H_SOURCE = "MATH"', 'H_SOURCE = "GPQA"'),
    ("X80 H line keeps the official MATH cells", '                Y[mi, j] = hv', '                Y[mi, j] = off'),
    ("X81 H consistency check removed", '                if (route == "imported") != (off == 1) or (off == 1 and hv != 1):', '                if False:'),
    ("X82 H consistency: only the imported->H 1 half", '                if (route == "imported") != (off == 1) or (off == 1 and hv != 1):', '                if off == 1 and hv != 1:'),
    ("X83 H missing-cell refusal removed (default 0)", '                r = htab.get((int(q), m))', '                r = htab.get((int(q), m), (0, "none"))'),
    ("X84 header line says MATH-FIX beside: yes", 'MATH-FIX beside: no"', 'MATH-FIX beside: yes"'),
    ("X85 header line dropped (skip path)", '    return [scorer_line(hsha), "  H table', '    return ["  H table'),
    ("X86 tau_LOMO_H against the official macro", 'tauh, disch, tinh = tau_b(sch, mach), discordant(sch, mach), tau_b(sih, mach)', 'tauh, disch, tinh = tau_b(sch, st["macro"]), discordant(sch, mach), tau_b(sih, mach)'),
    ("X87 H top 4 from the official ranking", '    top4h = rankh[:int(reg["top"])]', '    top4h = st["top4"]'),
    ("X88 H LOMO orders = the official ones", '    oh = lomo_orders(bh, W1, fh, reg=reg)', '    oh = st["orders"]'),
    ("X89 H in-sample from the LOMO orders", 'sih, _s2 = subset_scores(bh, W1, lambda m: ih, reg["share"])', 'sih, _s2 = subset_scores(bh, W1, lambda m: oh[m], reg["share"])'),
    ("X90 H lines dropped from the outcome (skip path)", '    lines += vl + support_lines(st) + hl + descriptive_lines(st, data)', '    lines += vl + support_lines(st) + descriptive_lines(st, data)'),
    ("X91 H MATH fit reused from the official fit", 'fh = [ff if B.name != H_SOURCE else full_fit(B, w, reg=reg)', 'fh = [ff if True else full_fit(B, w, reg=reg)'),
    ("X92 H NEFF at the official top 4's theta", 'info_at(ff["a"], ff["b"], float(np.mean(ff["theta"][top4h])))', 'info_at(ff["a"], ff["b"], float(np.mean(ff["theta"][st["top4"]])))'),
    ("X93 rank shift = min over models (min<->max)", '    shift = max(abs(rankh.index(m)', '    shift = min(abs(rankh.index(m)'),
    # DELTA 2 (B1, B2)
    ("X94 B1: top 4 ranked by micro (the prior Y2)", '    rank = sorted(range(M), key=lambda m: (-macro[m], models[m]))', '    rank = sorted(range(M), key=lambda m: (-micro[m], models[m]))'),
    ("X95 B2: self-exclusion dropped (PID -1)", 'rc, info = busy_probe(path, os.getpid() if pid is None else pid)', 'rc, info = busy_probe(path, -1)'),
    ("X96 B2: chain starts at the parent (own PID kept)", 'rc, info = busy_probe(path, os.getpid() if pid is None else pid)', 'rc, info = busy_probe(path, os.getppid() if pid is None else pid)'),
    ("X97 B2: own PID only (parent chain not walked)", '    $cur = $pp', '    break'),
    ("X98 B2: exclusion hides every process", 'Where-Object { -not $global:__bx.Contains([int]$_.ProcessId) }', 'Where-Object { $false }'),
    ("X99 B2: exit code forced free", '  exit $rc', '  exit 1'),
    ("X100 B2: a throw exits free (fail-open)", 'exit 3 }', 'exit 1 }'),
    ("X101 B2: no exit code reads free", '$global:LASTEXITCODE = 99', '$global:LASTEXITCODE = 1'),
    ("X102 B2: report check removed", '    if not info or info.get("rc") != 1:', '    if False:'),
)


if __name__ == "__main__":
    sys.exit(main())
