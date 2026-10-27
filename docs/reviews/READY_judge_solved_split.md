# READY review — JUDGE-SOLVED-SPLIT (first full review; zero calls)

Reviewed: branch `judge-solved-split`, tip `129fbc56` (parent `78386765`, base `50c71784`, an ancestor of main);
script `tools/analysis/judge_solved_split.py` **blob:c1f36f794d9d83ece13f5ecf2d553bdb6dbf0869** (LF, of record) /
sha256-lf16:eb29a82b5eb84f35 / sha256-crlf16:6be938f8da100edb (worktree holds the LF rendering). Imports
`k46_key_read.py` blob:c6a6729bb0256d394072ae844120867d2fa5c652 (= the registration's pin; identical in main and branch).
Registration: prog L23437-L23462 (`## Registered 2026-10-02 (before any code or call) — JUDGE-SOLVED-SPLIT: ...`).
Record: `docs/agents/results/JUDGE-SOLVED-SPLIT.json` (state registered). Reviewer: zero judge calls; no write to any DB.

## VERDICT: READY, with conditions C1 (operator, binding) and C2-C4 (LOW, non-blocking)

The deciding path is the registered one. The 95% percentile interval (B 2,000, default_rng(42), CK-CLOSE components
resampled jointly) decides JS1. NORMAL and the analytic DEFF are printed beside, labelled DESCRIPTIVE, NOT DECIDING.
The join and its refusal behave correctly, and every registered denominator reproduces to the digit from my own
read-only script. No accuracy by solve status was computed in this review: the equivalence checks ran on random
question-level labels, so the readout stays blind until --run.

## Per-claim table (deciding claims)

| # | claim | reviewer's evidence | result | sev |
|---|---|---|---|---|
| 1 | percentile decides JS1, normal descriptive only | `PRECONDITIONS.interval_form="percentile"`; `decide()` L437-443 picks (p_lo,p_hi); FORMS line reports agreement only; mutants normal_decides / form_ignored killed; my R4 (90% percentile) killed | CONFIRMED | — |
| 2 | JS1 bar strict (lower > 0 HELD; upper < 0 FAILED; otherwise UNDETERMINED) | `js1_word` L428-434; bar_inclusive killed; boundary checks in the selftest | CONFIRMED | — |
| 3 | join schedule.reference_row_id → reference(variant,vintage,source_key).legacy_qid → grok.db question_id; source_key ≠ "qid:<legacy_qid>" refuses | own script: 0 of the reference rows disagree; the refusal branch executed on the UNMUTATED `read_ref_qids` (fake conn: `[JOIN] 1 reference rows ...`; agreeing row → `{ref: 7}`) | CONFIRMED (the selftest does not cover this, see C2) | LOW |
| 4 | uncovered matches are never counted as unsolved | `attach_solve`: absent qid → solved None; `js1_rows` filters `solved is not None`; `correct NULL` refuses; mutant uncovered_as_unsolved killed; my R5 (uncovered folded into U) killed (15 checks) | CONFIRMED | — |
| 5 | denominators: 544 kd-ONE in 160 comps; covered 446; right 506 → 414 (226/188); wrong 38 → 32 (5 in 2 variants / 27 in 7); 98 uncovered on 29 qids; 2,801 solve rows | own script (sqlite `mode=ro&immutable=1`): **544 / 160 / 446; 506: 226 / 188 / 92 uncovered; 38: 5 (2 var) / 27 (7 var) / 6 uncovered; 98 on 29 qids; 2,801 rows** (correct ∈ {0: 1,183, 1: 1,618}); the script's dry-run prints the same | CONFIRMED (to the digit) | — |
| 6 | identity: C1 0.8787 / 544; right 0.9249 / 506; wrong 0.2632 / 38 | own script 0.8787 / 0.9249 / 0.2632; dry-run `-> IDENTITY: PASS` | CONFIRMED | — |
| 7 | JS1 boot_diff (conv A, comp) == K46 `boot_diff` | real 414 rows, 5 random label draws: point equal, replicate arrays `np.array_equal` True, percentile bounds equal (5/5), 0 NaN replicates | CONFIRMED | — |
| 8 | analytic DEFF of the difference (k46_repost D1 definition, extended) | my independent linearised loop equals the script on 5/5 draws (e.g. 1.3511 = 1.3511); the formula is correct for two ratio means with joint clusters (no g/(g-1) factor on either side, so it is consistent) | CONFIRMED | — |
| 9 | Support (b)-(f): DEFF 2.727 (source: K46-KEY-READ C1, bootstrap ratio on 544) → n_eff 82.9/68.9; SE = sqrt(.95·.05/226 + .90·.10/188)·sqrt(2.727) = 0.026247·1.6514 = **0.0433**; MDE80 **0.121**; reach 0.085; DESCRIPTIVE-ONLY | re-derived by hand (matches); C1 DEFF re-measured 2.727 from the real rows (K.boot_acc comp/iid, seed 42) | CONFIRMED; NON-VACUOUS | — |
| 10 | marker written only after the identity check; outcome written once | L663-664 follow `identity_js(refuse=True)`; direct run: identity refusal leaves **no marker, no outcome**; `write_once` mode x plus an existence pre-check of outcome and marker before any read; write_w / dry_writes killed. Moving the marker before identity (my R2-move) SURVIVES the selftest | CONFIRMED in code; test gap (C2) | LOW |
| 11 | sha re-check after the read → _VOID, never the file of record | direct run with the second solve-DB hash patched: `[PIN] ... written to _VOID`, outcome absent, VOID present. Dropping `ok_g` (my R3) SURVIVES | CONFIRMED in code; test gap (C2) | LOW |
| 12 | DESCRIPTIVE-ONLY respected; JS2 / JS3 never criteria | verdict lines print the registered VERDICT LINE beside the measured support; JS2 is labelled "never a criterion, never 'shown'"; F-JS fires only on HELD (falsifier_on_undet killed) | CONFIRMED | — |
| 13 | dry-run read-only, writes nothing, no accuracy by solve status | real --dry-run rc 0; sha256 and mtime of store / eval view / grok.db identical before and after (`diff` empty), no -wal or -journal; no output dir created in main or the worktree | CONFIRMED | — |
| 14 | commit hygiene | `git diff --name-only 50c71784..129fbc56 \| wc -l` = 1 (the script only); worktree clean (0 porcelain lines) | CONFIRMED | — |

Wrong(established): there is no model-edge count, so it does not apply (the script says so). Leakage: none. This is
a readout, not a construction. The EVAL key read is K46-KEY-READ's, already of record.

## Mutants
Builder's suite, re-run: selftest **63 checks, 0 failed; 18 / 18 killed**; 28 / 28 print branches executed.
The reviewer's own mutants (each run through the full selftest on a scratch copy):
- R1 drop the source_key ≠ qid refusal: SURVIVED. Not decisive: 0 disagreeing rows of record, and the branch was executed directly (row 3).
- R2 move the marker before identity: SURVIVED. Not decisive: the code order is verified by direct execution (row 10).
- R3 VOID ignores the solve-DB sha: SURVIVED. Not decisive: the hashes are equal before and after, and the branch was executed directly (row 11).
- R4 90% percentile bounds: killed (decisive path).
- R5 uncovered rows folded into the unsolved arm: killed.
- R6 B halved in JS1: killed.
- R7 identity never refuses in --run: killed.
- R8 a stray extra write before the sha check: SURVIVED. Not decisive: the selftest asserts no file inventory.

## Defects / conditions
- **C1 (binding, operator).** Merge `129fbc56` into main unchanged. In main, `git hash-object tools/analysis/judge_solved_split.py`
  must give c1f36f79 and `k46_key_read.py` must give c6a6729b. From main, run `--dry-run`: rc 0, both identity blocks PASS, and the
  DENOMINATORS line exactly as in row 5 (414 in 122 components, Kish 4.850). Then run `--run` with OMP / MKL / OPENBLAS = 1 set in
  the launching environment. The script refuses otherwise.
- **C2 (LOW, test gap; fix in the next delta, does not block this run).** Three guards are correct but the selftest does not
  defend them (R1, R2, R3 survive). Fix:
  - add `and not os.path.exists(ci.mark)` to the identity-refusal check;
  - add a fake-connection check that `read_ref_qids` refuses on `source_key != "qid:<legacy_qid>"`;
  - add a VOID check that patches the second solve-DB hash and asserts that `_VOID.txt` exists and `outcome.txt` does not.
- **C3 (LOW, post-run reading).** The measured "DEFF ... (ANALYTIC)" is the DEFF of the difference on the 414 matches. It is not
  the same object as the transported 2.727, which is a single proportion on the 544, measured as a bootstrap ratio. On random
  question-level labels the difference DEFF ran 1.25-1.54 (5 draws), so the transported plan is conservative. The verdict line
  DESCRIPTIVE-ONLY cannot change, because |pred| 0.01 < MDE80 whenever SE > 0.0036. The post-run review prints both values and the
  MDE beside Delta_S.
- **C4 (LOW, wording).** The dry-run prints "joined qids 174, present 143, absent (UNCOVERED) 31". That line counts every ONE qid,
  including 2 qids that have no key-decidable match. The registered "29 qids" is the key-decidable count and it reproduces (row 5).
  The registrar should quote 29, not 31.

## --run command (Git Bash, from the main checkout, after C1's merge and dry-run)
```
cd /z/FAC/TUBerlin/THESIS/TaxoArena && OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python tools/analysis/judge_solved_split.py --run
```
The run writes `experiment_results/archv2/judge_solved_split/outcome.txt` (mode x) and `judge_solved_split.READ_STARTED`.
It refuses if either file already exists.

## Commands (scratch = session scratchpad; all DB opens `mode=ro&immutable=1`)
```
git -C .claude/worktrees/judge-solved-split hash-object tools/analysis/judge_solved_split.py   # c1f36f79
git hash-object tools/analysis/k46_key_read.py   (main and worktree)                            # c6a6729b
python tools/analysis/judge_solved_split.py --selftest            # in the worktree: 63/0, 18/18
sha256sum + stat (3 DBs) > pre; TAXOARENA_DATA_ROOT=<main> ... --dry-run; sha256sum + stat > post; diff pre post   # empty
scratch/indep.py   # independent recount from schedule/match_status/response/reference/grok.db (row 5, 6)
scratch/blind.py   # random-label equality vs K.boot_diff, independent analytic DEFF, C1 DEFF 2.727 (rows 7-9)
scratch/direct.py  # unmutated [JOIN] refusal, VOID branch, identity refusal leaves no marker (rows 3, 10, 11)
scratch/mutrun.py, scratch/mut2.py   # R1-R8 against the full selftest
git diff --name-only 50c71784..129fbc56 | wc -l                    # 1
```
