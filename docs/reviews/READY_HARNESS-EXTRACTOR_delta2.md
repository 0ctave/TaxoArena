# DELTA READY review 2: HARNESS-EXTRACTOR, the B-2 fix (rule 8 per HX-R4), adversarial reviewer, 2026-10-09

Reviewed: `git diff 5f5acab5..70dd5a83` on branch `hx-r4` (worktree `.claude/worktrees/hx-r4`). It changes 1 file
(`git diff --name-only 5f5acab5 70dd5a83 | wc -l` = 1), tools/analysis/harness_extractor.py, +49 / -30. 5f5acab5 is an ancestor, and the
worktree `status --porcelain | wc -l` = 0.
Blob: blob:398336f08a4381e3dfe7f645adf9555751c4f3b4 (`rev-parse` = `hash-object`), sha256-lf16:9019ce455051f3ea (LF, of record). The worktree
holds the CRLF rendering, sha256-crlf16:e0f777e296cb338f (2,185 CR); the script's identity line prints the same three.
Code outside the delta is cited from READY_HARNESS-EXTRACTOR.md (c953775e) and READY_HARNESS-EXTRACTOR_delta.md, not re-derived. Zero calls.

## VERDICT: NOT READY. B-2 is CLOSED (CONFIRMED). The Support gate is still open: (d)-(f) must be registered first, then a small delta 3.
The L25274 bracket reads "(d)-(f) must be re-derived by a registrar's insertion before HARNESS-EXTRACTOR's READY". No insertion
exists. The programme ends at L25401 and has no later bracket at L25274. The code still prints the superseded plan: SUPPORT_PLAN L263-L267
holds HX1/HX2 0.0184 / 0.052 and "0.92 vs bar 0.85: SCOREABLE".

## Per-claim table (deciding claims only)
| # | claim | reviewer's evidence | status | sev |
|---|---|---|---|---|
| 1 | B-2: rule 8 refutes RANKS-MOVE iff every tau-b >= 0.85 AND max shift <= 2 | `rule8_hx1` reads `round(p[2],12) >= tau_bar` over all pairs and `max_shift <= shift_bar` (2.0); `move_bar` is removed; this is the same comparison as `set_word` L323, so rule 8 is the exact complement of the HX1 word; the DEFECT_R4 branch is gone; the text reads "more than 2 ranks" | CONFIRMED | - |
| 2 | HX-R4 binds HX2 / HX3 | HX2 / HX3 words use `set_word` (the HX1 rule); HX2's rule 8 is the HX-R5 cross-observable line (unchanged) | CONFIRMED | - |
| 3 | Selftest 9/9 | own run on a `git archive` copy: "[HX] selftest: 9 / 9 passed" (busyself included; busy.ps1 was free) | CONFIRMED | - |
| 4 | Mutants: X13 / X83 / X84 die; X15 dies (pure) | own: X13, X14, X15, X83, X84 KILLED; X00 SURVIVED | CONFIRMED | - |
| 5 | Real --dry-run | own (busy.ps1 rc 1): rc 0, 39 lines, "POOL paeec37aa28063c75 verified" first; rule-7 line exit 1 with the excluded PIDs printed; `grep -c "^HX\|RULE 8\|PREDICTION\|HX-R4"` = 0; multicorpus_cache_v1.db ad66e30a0eb4abd6 and checker_answers_v2.db 6cfaf74d647829d1 EQUAL before / after | CONFIRMED | - |
| 6 | No other path changed | the diff is docstring, REG (move_bar removed), BRANCHES, rule8_hx1, verdict_lines rule-8 lines, the selftest cases and X13 / X15 / X83 / X84 | CONFIRMED | - |
| 7 | Support (d)-(f) re-derivation (builder's draft) | recomputed: 0.03374 x sqrt(2,056 / 1,324) = 0.04204; x sqrt(2,056 / 541) = 0.06577; MDE80 0.118 / 0.094 (floor) / 0.184. HX4 sqrt(0.099 / 1,324) x sqrt(1.2) = 0.00947 -> 0.027. The inputs match POSTRUN_SATURATION-IRT rows 3 and 11 (SD 0.0337, B 200; 2,056 items; Kish 1.0002) | CONFIRMED (arithmetic) | - |
| 8 | Support registered | absent (see the verdict) | NOT MET | BLOCKER (registration) |

## Own mutants (sandbox E:/TaxoArena_tmp/rev_hx; appended to MUTANTS)
- H01: rule 8's tau clause made strict (> 0.85). KILLED (decisive; boundary).
- H03: rule 8's tau clause reads only the first pair. SURVIVED. No fixture has a non-first pair below 0.85 together with max shift <= 2.
  The shipped code is correct; this is a test gap on a printed verdict line. MEDIUM (T-1).
- H04: rule 8 lets an undefined (NaN) tau-b pass. SURVIVED. No rule-8 case carries a NaN pair. The shipped code is correct
  (`round(nan) >= 0.85` is False, the same as set_word's -inf). MEDIUM (T-1).

## What the registrar must insert (Support (d)-(f) at L25274, replacing the bracketed figures; planning, no data read)
- (d) SE. The noise of a ranking tau over 18 models is model-level and does not shrink as sqrt(n_items) (POSTRUN_SATURATION-IRT C-1).
  Planning SE(tau) = 0.03374 x sqrt(2,056 / n) for n < 2,056. 0.03374 is SATURATION-IRT's realised bootstrap SD at 2,056 items, Kish
  1.0002. The floor is 0.0337.
  - HX1, HX2 (n 1,324): 0.0420.
  - HX3 (n 541): 0.0658.
  - HX4 (a per-model paired accuracy difference; C-1 does not apply): 0.0095 unchanged. The declared DEFF 1.2 is conservative against the measured Kish 1.0002.
  - HX5: 0.0072 unchanged (DEFF 3.0 declared).
  - TRANSPORT ASSUMPTION, disclosed: SATURATION's tau compares rankings fitted on different item subsets. HX's taus compare scorers on the
    SAME items, so item noise is largely shared and the transported SE is probably an OVER-statement. The classification below takes
    the conservative side. The run's bootstrap SD is the value of record.
- (e) MDE80 = 2.8 x SE: HX1 / HX2 0.118 (0.094 at the floor); HX3 0.184; HX4 0.027; HX5 0.020.
- (f) Verdict lines:
  - HX1 SCOREABLE: the predicted 0.35 is 0.50 below the bar 0.85.
  - HX2 DESCRIPTIVE-ONLY BY SUPPORT: the predicted 0.92 is 0.07 above 0.85, inside 0.094-0.118. Its shift clause (predicted 3 against 2)
    has no measured SE and a one-rank margin.
  - HX3 DESCRIPTIVE-ONLY (unchanged).
  - HX4 SCOREABLE: 0.099 against 0.02, a margin of 0.079 > 0.027.
  - HX5 SCOREABLE.
- Registrar's ruling owed in the same insertion: F-H fires iff HX2 reads RANKS-HOLD. With HX2 descriptive-only, rule whether F-H is
  (i) printed "(descriptive-only by support)" and decides nothing (the reviewer's recommendation: a falsifier must not rest on an
  unpowered word), or (ii) kept scored with that disclosure.

## Defects and fixes
- **S-1 BLOCKER (registrar).** The insertion above.
- **D-3 (builder, after S-1).** SUPPORT_PLAN rows HX1 / HX2 / HX3 change to 0.0420 / 0.118, 0.0420 / 0.118 "DESCRIPTIVE-ONLY", and
  0.0658 / 0.184. The HX2 word line gains "(descriptive-only by support)", as HX3's L853 form does, and F-H follows the registrar's
  ruling. Add selftest value checks and mutants for each.
- **T-1 MEDIUM (builder, in D-3).** Add a pure / verdicts case where a NON-first pair has tau-b < 0.85 with max shift <= 2, and one with a
  NaN pair: rule 8 must read "not refuted" in both. Assert `rule8_hx1(h) == (set_word(...)["word"] == "RANKS-HOLD")` on them. H03 and H04
  must then die.
- **L-A LOW (carried).** Launch directly, not through a wrapper whose command line matches busy.ps1.
- After D-3: a delta READY of D-3 plus regression (selftest, X13 / X15 / X83 / X84, H03 / H04).

## Run commands (ONLY after S-1, D-3 and its delta READY)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                        # must exit 1
python tools/analysis/scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest
python tools/analysis/harness_extractor.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
python tools/analysis/harness_extractor.py --run     --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena
# back up outcome + figure json to E:/TaxoArena_backup_<date>_harness_extractor with SHA256SUMS; never commit
```

## Commands (read-only; zero calls)
```
git diff --name-only 5f5acab5 70dd5a83 | wc -l ; git merge-base --is-ancestor 5f5acab5 70dd5a83   # 1 ; ok
git rev-parse 70dd5a83:<path> ; git hash-object <wt path>                       # 398336f0 both; lf16 9019ce45, crlf16 e0f777e2
git archive 70dd5a83 -- . ':!*.db' ':!*.npz' | tar -x -C E:/TaxoArena_tmp/rev_hx    # + H01 H03 H04
scratch_dir.py --run -- python tools/analysis/harness_extractor.py --selftest  # 9 / 9
scratch_dir.py --run -- python tools/analysis/harness_extractor.py --mutants --only X00 X13 X14 X15 X83 X84 H01 H03 H04   # 6 of 8 KILLED
busy.ps1 -> 1 ; python tools/analysis/harness_extractor.py --dry-run --data-root <main>   # rc 0, 39 lines (E:/TaxoArena_tmp/rev_hx/hx_dry.log)
sha256sum multicorpus_cache_v1.db checker_answers_v2.db (before / after)       # EQUAL
sed -n 25270,25280p docs/judge_v2_program.md ; wc -l docs/judge_v2_program.md # (d) bracketed, no insertion; 25,401
python: 0.03374*sqrt(2056/1324)=0.04204, *sqrt(2056/541)=0.06577, x2.8 = 0.118 / 0.184; floor 0.094
```
