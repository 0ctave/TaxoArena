# READY review: GMM-FIXEDK (adversarial; zero calls; nothing run beyond --selftest / --mutants / --dry-run)

Reviewed: branch gmm-fixedk, tip ea19a8b7 (parent 9bff7e39 = main HEAD at review time), one file added.
Registration: docs/judge_v2_program.md L24856-L24868 (_as_of 9bff7e39), "## Registered 2026-10-06 (before any code or call) — GMM-FIXEDK: ...".

## VERDICT: READY (no blocker)

Conditions on the run (operator): R-C1 `busy.ps1` exit 1 immediately before `--run` (the C leg is a pool reader, rule 7), and nothing
else heavy on the machine; R-C2 `--workers` <= 22 (the dry run estimates about 24 min wall at 20, so it does not need to be detached;
detach it anyway if anything else is running); R-C3 the run is accepted only if the GK-I0 identity line reads REPRODUCED (otherwise the
script refuses and writes nothing; that is a failed precondition, not an outcome).
Post-run checks owed (post-run reviewer): PR-1 re-measure DEFF / n_eff / MDE from the outcome's SUPPORT lines and set them beside the
registered 0.076 (realised SE of the GMM arms against the transported BISECT-SKM SE); PR-2 the (a) item-only SD must be > 0 on both corpora
(see D-1); PR-3 the re-print POINTS of BISECT-SKM / GMM-BIC must read "point REPRODUCED" (8 cells) against CONSTRUCTION-ARMS.

## Pins (LF of record)
| object | pin | how shown |
|---|---|---|
| tools/analysis/gmm_fixedk.py @ ea19a8b7 | blob:fdca150f71caa49542a7389b2647eceab0a4bc39, sha256-lf16:99cc418f47758921 (sha256-crlf16:86cc8a57a34d67c5 beside, printed by the script) | `git hash-object`; `git show ea19a8b7:<path> \| sha256sum`; dry-run pins line |
| construction_arms.py (imported unchanged) | blob:5d08a5dfb8c0cb0b5330512259b4732aa4af2dd2 | `git hash-object`; asserted by check_code_pins on every entry point (dry-run IMPORTS line) |

## Per-claim table (deciding claims)
| # | claim | reviewer's result | verdict | sev |
|---|---|---|---|---|
| 1 | C-GK coded as registered: GMM-WINS iff some (j,r), j in {DIAG, FULL}, r in {a, c}, has D > spread_1r AND lo > 0 on BOTH corpora | gk_decide/clears read: strict `>` both conjuncts, `all` over CORPORA, both j and both r; NaN fails closed; M01-M07 + own R3 killed | CONFIRMED | - |
| 2 | Interval = C-CA's: B 2,000, default_rng(20261006) fresh per corpus, components resampled once and shared (paired), seed indices drawn per arm (crossed), np.percentile 2.5/97.5 | bootstrap_means vs CAR.bootstrap_corpus read side by side: same stream, same component draw, vals_w identical to CA L1120-L1130 (weighted dp_fast on ok rows; weighted (c)); only the per-arm draw ORDER differs (GK-R1) | CONFIRMED (GK-R1 bracket) | LOW |
| 3 | D = point mean difference over 5 seeds; spread_1r = range of arm 1's 5 point values | contrast/corpus_fits read; own R4 (D from the bootstrap mean) killed; M09/M10 killed | CONFIRMED | - |
| 4 | Node rules (6)/(7) as registered (k 2; diag reg 1e-6; full reg 1e-4 in node PCA p = 32 / floor(n/10) min 2, unwhitened; n_init 3; max_iter 200; hard posterior; < 2 child -> forced spherical 2-means, counted) | BisectGmmRule read; pca_dim reproduces the clause; replacement counted out of rule_splits into forced; M17-M33, M65-M68 killed | CONFIRMED | - |
| 5 | Matched leaf count refused for arm 1 and both deciding arms | corpus_fits refuses nL != L; own R5 (overshoot only) killed; M38/M39 killed | CONFIRMED | - |
| 6 | Identity precondition GK-I0 (arm 1 means and ranges to %.5f, both readouts, both corpora) + I1-I3, refuse before any readout | arm1_identity / compute order read; values in ARM1_ID equal the registration and the CONSTRUCTION-ARMS outcome (prog L24788ff); own R6 killed; M34-M36 killed | CONFIRMED | - |
| 7 | Split hygiene: fits on TRAIN only, EVAL unlocked after the TRAIN matrices are frozen, dry run never unlocks EVAL, gold read by the scorer only | run(): load_world -> unlock_eval -> identity -> run_fits(Xtr) (same order as CA run L1615-L1618); dry run asserts gate_frozen False; M58/M59 killed | CONFIRMED | - |
| 8 | Support section NON-VACUOUS and its arithmetic reproduces | re-derived by hand from the CA intervals of record (prog L24788ff): SE (a) 0.06262/3.92 = 0.01597, 0.04873/3.92 = 0.01243; (c) 0.06799/3.92 = 0.01734, 0.02177/3.92 = 0.00555; DEFF 5.38 / 14.12 / 20.19 / 1.78; n_eff 919 / 473 / 245 / 3,748; MDE80 0.0631 / 0.0760 / 0.1296 / 0.0302; pair (a) 0.076, (c) 0.130; deciding 0.076; spread > 1.96 SE in all four cells (0.031 < 0.043, 0.024 < 0.060, 0.034 < 0.108, 0.011 < 0.023); 0.894^2 = 0.80. DEFF source named (transport from BISECT-SKM realised intervals). DESCRIPTIVE-ONLY at the prediction, stated | CONFIRMED (every digit) | - |
| 9 | Selftest 96 value checks pass | `--selftest` rc 0, "SELFTEST OK: 96 value checks in 27.0 s" | CONFIRMED | - |
| 10 | Mutants 68/68 killed, control survives | re-run: "MUTANTS: 68 / 68 killed; control C0 SURVIVED" (69 "killed"/"SURVIVED" lines counted with grep -c) | CONFIRMED | - |
| 11 | Dry run clean on real data: counts TRAIN 9,870 / 13,487, L 84 / 139 / 81, \|C\| 2,772, EVAL locked, 0 files written, no DB write | busy.ps1 exit 1; dry-run rc 0; lines match; mtimes/sizes of the 7 intent-s1-run DBs and embeddings_cache.db(+wal/shm) identical before/after (`diff` empty); estimate 150 fits, 2.7 CPU-h, ~24 min with 20 workers (builder: 2.0 / 22; my run overlapped the mutant suite) | CONFIRMED | - |
| 12 | Determinism: process pool equals serial fits | selftest E5 asserts pool(2) == serial on the real rules; OMP/OPENBLAS/MKL = 1 set at import (L91) | CONFIRMED | - |

## Own mutants (sandboxed through the script's run_mutants; driver E:/TaxoArena_tmp/gk_rev_mut.py, not committed)
| id | change | result | decisive |
|---|---|---|---|
| R1 | (a) bootstrap passes w=None to dp_fast (item axis dropped for DP only) | SURVIVED | yes (would narrow the (a) interval) -> D-1 |
| R2 | (c) readout values read DP | killed | yes |
| R3 | C-GK loops over (a) only | killed | yes |
| R4 | D = mean of bootstrap replicates instead of the point | killed | yes |
| R5 | matched-L refusal only when nL > L | killed | yes |
| R6 | GK-I0 compares (a) only | killed | yes |
Control C0 SURVIVED in the same harness.

## Defects
- D-1 (MEDIUM, test gap, not a code defect): R1 survives. The code of record is right (corpus_stats passes `w[ok]`; dp_fast honours
  `weights=w`; identical to CA L1126), but no selftest asserts that the (a) bootstrap moves with the component weights; M13 kills only the
  all-readout version. Fix: in _st_units add an independent weighted-DP bootstrap check for (a) (as _indep_boot does for (c)), or assert
  se_item(a) > 0 on the planted world. Not required before the run; PR-2 covers the run of record.
- D-2 (LOW, bracket owed): registration SUPPORT (b) writes DEFF_total = (SE / SE_item)^2; the script prints Kish x (SE / SE_item)^2
  (CONSTRUCTION-ARMS' own convention, its L104). Difference 0.93% on MASSIVE, 0 on CLINC; descriptive (no criterion reads DEFF).
- D-3 (LOW, cosmetic): the rendered BUILDER'S READINGS line says "GK-R1..GK-R6"; the docstring has GK-R7 (p capped at the slice
  dimension; never binds at d 256). Fix in the outcome-reading bracket, or add GK-R7 to the line in a later round.
- D-4 (LOW, disclosed by design): the percentile interval is anti-conservative on the 5-seed axis; the registration keeps it (mirrors
  C-CA) and the seed-corrected SE is printed beside. No action; keep the words in the outcome.

## Commands
```
git -C .claude/worktrees/gmm-fixedk hash-object tools/analysis/gmm_fixedk.py tools/analysis/construction_arms.py
git show ea19a8b7:tools/analysis/gmm_fixedk.py | sha256sum            # 99cc418f47758921
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gmm_fixedk.py --selftest          # rc 0, 96 checks
python tools/analysis/scratch_dir.py --run -- python tools/analysis/gmm_fixedk.py --mutants --jobs 10  # 68/68, C0 survived
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/gk_rev_mut.py                   # R1 survived, R2-R6 killed
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # exit 1 (free)
ls -l --time-style=full-iso <DBs> > before; ... --dry-run --workers 20 (rc 0); ls ... | diff - before   # empty
sed -n 24788,24806p docs/judge_v2_program.md   # CA intervals / P1 points used for claim 8 and claim 6
```
Logs (not committed): E:/TaxoArena_tmp/gk_rev_st.log, gk_rev_mut.log, gk_rev_mut2.log, gk_rev_dry.log.

## Brackets owed (registrar)
- GK-R1: per-replicate seed-draw order components -> ENGINE-SKM, BISECT-GMM-DIAG, BISECT-GMM-FULL, BISECT-SKM, GMM-BIC; the re-print
  intervals of BISECT-SKM / GMM-BIC therefore differ from CONSTRUCTION-ARMS' by stream; only their points are checked.
- GK-R2: node seed node_seed(s, c, 2) for both mixtures; replacement split on CA's forced slot 9.
- GK-R3: PCA svd_solver 'full', centred, unwhitened.
- GK-R4: a mixture fit that raises (ValueError / LinAlgError) is replaced by the forced split like a < 2 child, counted as a fit error.
- GK-R5: P4 forced share = (best-first forced + replaced) / all splits, mean over 5 seeds; scored on MASSIVE and CLINC, C printed.
- GK-R6: leaf balance = W-3's count (distinct non-null TRAIN-majority fine labels over distinct EVAL fine labels).
- GK-R7: p = min(p, slice dimension) (binds only on 8-d fixtures).
- D-2: DEFF_total printed as Kish x (SE / SE_item)^2 (CA convention), not the registration's (SE / SE_item)^2.
