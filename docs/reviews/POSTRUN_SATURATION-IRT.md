# POST-RUN review: SATURATION-IRT (run 2026-10-09, blob 2a50e833, main fae77f6d)

Reviewer: adversarial-reviewer, 2026-10-09. Zero judge calls; every DB opened `mode=ro&immutable=1`; busy.ps1 exit 1 before each
of my pool reads (4 reads). The registration is "## Registered 2026-10-08 (before any code or call) — SATURATION-IRT: ..." (L25051-L25064).

## Verdict
**VALID.** SI1 = LOSES-RANKING (descriptive-only by support), and RULE 8 refutes KEEPS-RANKING. SI2 = GPQA-OPEN. F-SI did NOT FIRE.
P1 HELD, P2 FAILED, P3 FAILED, P4 HELD, P5 HELD (vacuous: holds by construction), P6 HELD.
I recomputed every deciding number with my own fitter, written independently: unpooled columns, sum-zero theta parameterisation,
no theta bound, and no import of saturation_irt.py. All of them agree to the digit.
Conditions for the registrar's record: C-1 to C-3 below. None of them changes a word.

## Data object
- The R1 pool is paeec37aa28063c75 (6,482 EVAL ids). Twins: 471 ids / 427 texts. 20,546 questions kept after collapse.
- The v2 views are gen_view_REG.db (c2930c60) and eval_view_REG.db (e35b7518). multicorpus_cache_v1.db is ad66e30a.
- All three shas are equal before and after my reads.
- Roster: 18 models, Meta-Llama-3-70B-Instruct not ACTIVE. Scored flag: `is_correct` (official, no MATH-FIX overlay; D-2026-10-08-5).
- Per source, kept = complete: MMLU_PRO 11637, BBH 5757, MATH 1309, MUSR 756, GPQA 546, IFEVAL 541. 0 incomplete.
- Deciding denominator: the LOMO top-decile subsets, 1164+576+131+76+55+54 = 2,056 items. 18 models, 153 pairs.

## Per-claim table (deciding claims)
| # | claim (outcome file) | reviewer's number | result | sev |
|---|---|---|---|---|
| 1 | tau_LOMO 0.8824, discordant 9 of 153 | 0.8824, discordant 9; 114 fits, 114 converged | CONFIRMED | - |
| 2 | SI1 LOSES-RANKING; RULE 8 refutes KEEPS (0.8824 < 0.90) | same | CONFIRMED | - |
| 3 | bootstrap 95% [0.8036, 0.9219], SE 0.0337 (B 200) | from the cache: 200 distinct r (0-199); tau recomputed from each row's own vectors, 0 mismatches; SD 0.0337; linear pctl [0.8036, 0.9219] | CONFIRMED | - |
| 4 | replicates are honest (cache meta EQUAL; 3 reused from the pilot) | r=0 0.8431 and r=1 0.9216 re-derived independently (draws regenerated from default_rng(20261008), my weighted fitter) = cache; meta pins blob 2a50e833 + data sha + seed; boot_weights draws sequentially, so reuse = fresh | CONFIRMED | - |
| 5 | F-SI NOT FIRED (upper 0.9219 >= 0.90) | the upper bound is >= 0.90 under every percentile rule (linear 0.9219, lower/nearest 0.9216, midpoint 0.9281, higher 0.9346) | CONFIRMED (robust) | - |
| 6 | SI2: NEFF_GPQA 0.9487 > NEFF_MMLU_PRO 0.7176, so GPQA-OPEN | 0.9487 vs 0.7176 (top 4 Llama-3.1-70B, Qwen2.5-72B, Llama-3.3-70B, Falcon3-10B) | CONFIRMED | - |
| 7 | P2 tau_in-sample 0.8431 (FAILED) | 0.8431, discordant 12 | CONFIRMED | - |
| 8 | P4 SAT4 MMLU_PRO 0.2940, GPQA 0.0806 (HELD) | 0.2940 / 0.0806 | CONFIRMED | - |
| 9 | P6 smallest share 15% (HELD) | curve 5% 0.8824, 10% 0.8824, 15% 0.9085, 20% 0.8954, 25% 0.9346 | CONFIRMED (see C-3) | LOW |
| 10 | per-benchmark ALL / NONE / NEFF / SAT4 / theta4 (6 rows) | all 6 rows equal to the digit | CONFIRMED | - |
| 11 | Support: clusters 20,544, Kish 1.0002, n_eff 2,056, MDE80 0.0945 | 20,544 stem_key clusters, Kish 1.0002 (MMLU_PRO 1.0003); 2.8 x 0.03374 = 0.0945 | CONFIRMED | - |
| 12 | H sensitivity: tau_LOMO_H 0.9216 (disc 6), in-sample_H 0.8954, MATH official 2270 vs H 6976, NEFF_H 0.5844, SAT4_H 0.2536 | all equal; H table sha256-lf 6b010fa6... equal to the pin, 0 CR | CONFIRMED (descriptive) | - |
| 13 | run hygiene | selftest 17/17; dry rc 0; pilot rc 0 with 0 REFUSE; run rc 0; outcome file written once; 14/14 backup sums OK; blob 2a50e833 = HEAD:tools/analysis/saturation_irt.py = working tree (LF) | CONFIRMED | - |

## Defects / conditions
- **C-1 (MEDIUM; the registration, not the run). The planned SE understated the realised SE by 2.3x.**
  The plan had 0.0146 and MDE80 0.041; the realised SE is 0.0337 and MDE80 0.0945. DEFF is not the cause: the measured Kish is
  1.0002, below the transported 1.2. The planning model is the cause: it scaled the SE of tau by sqrt(590/2100), but the noise of a
  LOMO tau over 18 models comes from model-level selection and does not shrink as sqrt(n_items).
  Consequence: SI1 stays DESCRIPTIVE-ONLY, as registered. SI2 is unaffected (margin 0.231).
  Fix: the registrar records the realised SE and MDE beside the plan. HARNESS-EXTRACTOR's Support (d) reuses this exact arithmetic
  ("0.0275 at 590 items scaled", L25089 / L25274) and must be re-derived before its READY.
- **C-2 (MEDIUM; disclosure). The SI1 word depends on the MATH scorer.**
  Under H, tau_LOMO_H = 0.9216 (6 discordant), which is on the KEEPS side, and the top 4 changes (Falcon3-10B drops out).
  The official MATH scorer is near the floor: 9.6% of cells correct, against 29.6% under H.
  D-5 makes the official scorer of record, so the word stands. But the record and the post must print the H line beside the word,
  never the word alone.
- **C-3 (LOW). P6 is non-monotone.** 15% gives 0.9085 but 20% falls back to 0.8954. Quote the curve, not "15% suffices".
- **L-1 (LOW). P5 is vacuous.** The 2PL nests the Rasch fit at log a = 0 with zero penalty, so "2PL >= Rasch" holds by construction
  (the outcome file says so). Record it as "HELD (vacuous)", not as a held prediction.
- **L-2 (LOW). The outer cmdlog has no busy line between --dry-run and --pilot.** The in-script rule-7 check did print exit 1 in the
  PILOT file (line 2) and in the outcome file (line 2), so rule 7 was met. Note only.
- **L-3 (LOW, carried).** "posterior-mean a_i" is read as the MAP a_i. This reading was ACCEPTED at READY_SATURATION-IRT.md row 12.

## Other items in the same operator batch
- HARNESS-EXTRACTOR: NOT RUN, which is correct (NOT READY, B-2). Zero HX outputs: `ls experiment_results | grep -ci harness` = 0;
  there is no E:/TaxoArena_backup_20261009_harness*. Nothing to review.
- GEMMA-UNION-EXT: see docs/reviews/POSTRUN_GEMMA-UNION-EXT.md.

## Commands (reviewer scripts and logs backed up to E:/TaxoArena_backup_20261009_postrun_sat_gemma, SHA256SUMS.txt)
```
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # rc=1 before each read (4x)
python E:/TaxoArena_tmp/rev_20261009/si_recompute.py   # rows 1,2,6,7,8,10; twins/kept/roster; DB shas equal
python E:/TaxoArena_tmp/rev_20261009/si_boot1.py       # row 4 (r=0,1), row 11 (clusters, Kish)
python E:/TaxoArena_tmp/rev_20261009/si_p6.py          # row 9 (curve 5-25%)
python E:/TaxoArena_tmp/rev_20261009/si_h.py           # row 12 (H line)
python - <<cache stats>>  # rows 3,5: 200 rows, 0 tau mismatches, SD, percentiles under 5 rules
git hash-object tools/analysis/saturation_irt.py; git rev-parse HEAD:tools/analysis/saturation_irt.py   # 2a50e833 both
(cd E:/TaxoArena_backup_20261009_saturation_irt && sha256sum -c SHA256SUMS.txt | grep -c ': OK')       # 14 of 14 lines
```
