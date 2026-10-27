# READY delta review: CERT-POSITIVE-CONTROL, b5653fb7 -> 416ac436 (C-1, C-2, D-5)

Reviewer: adversarial-reviewer, 2026-10-03. Branch cert-positive-control, tip 416ac436 (1 commit over the reviewed b5653fb7).
Prior review: docs/reviews/READY_cert_positive_control.md (b5653fb7). Delta only, plus regression. Zero calls; --analyze NOT run.
Delta numstat: build.gradle.kts 3 / 0; CertPositiveControlArmTest.kt 6 / 4 (KDoc only); cert_positive_control.py 45 / 6.
SeparationNullBySizeTest.kt is UNCHANGED (blob:50c4b0ef5601ca093b873d65eaa1bdf2d040b5b4, = the reviewed arm).
Pins (LF; `git hash-object` == `git rev-parse 416ac436:<path>`):
- cert_positive_control.py blob:e0751d7c6fe50b0a588cbb1160eee0b3e99ce8a1 (working tree LF)
- build.gradle.kts blob:5b6afb8b85e1bc285d424054837ee1f10e2f078a (working tree is the CRLF rendering)
- CertPositiveControlArmTest.kt blob:844fa2442c44bfd1fcdb75df42586758ebea8670

## Verdict

**READY for --analyze with blob e0751d7c on the arm outputs b5653fb7 produced: VALID** (ruling below). **C-1 MET, C-2 MET,
D-5 MET (as a disclosure)**. Merge to main: MERGEABLE on this review (C-2 closed). C-4 is half met here: the K11 sort is now
proved by execution; the root-null-beside-G12 line stays with the post-run review.

## Per-claim table

| # | claim | my evidence | status | sev |
|---|---|---|---|---|
| 1 | C-1: the readout's live gate is tested | selftest 21/21; `python -O` 21/21 (D-3 fixed: rc check replaces the assert); --mutants 30/30, M0 survived; my R1, R2, R9, R6 now KILLED by the new cases (R3, R7 KILLED as before) | MET | - |
| 2 | only selftest/mutant code changed in the readout | AST comparison of the 55 top-level defs/assigns at b5653fb7 vs 416ac436: only `MUTANTS`, `_fx`, `selftest` differ (plus the module docstring); `analyze`, `pctl`, `kcount`, `p_of`, `read_g12`, `i2_named`, `INSTRUMENT`, `BAR`, `REPS`, the sentences: byte-identical | CONFIRMED | - |
| 3 | C-2: nullBySize no longer selects the new test | `gradlew nullBySize --tests *certPositiveControl*` -> "No tests found for given includes: [*SeparationNullBySizeTest*] [*certPositiveControl*]" (before: 1 test FAILED). Insertion-only (3 lines) in the nullBySize block; the siteNull block is untouched | MET | - |
| 4 | certPositiveControl still selects it | `gradlew certPositiveControl` (no inputs, cpc worktree) -> 1 test, refuses "[CPC] REFUSING: -DsnapshotId is required" with the [THREAD-CAP] line printed; nothing read | CONFIRMED | - |
| 5 | D-5: K10 KDoc corrected | KDoc now reads "NOT equivalent ... an UNKILLED survivor of the arm path, disclosed"; "10 of 11 non-equivalent killed". The recompute-in-loop fix was not taken (optional; the arm already ran) | MET (disclosure) | LOW |
| 6 | arm unit tests still green | `gradlew test --tests taxonomy.CertPositiveControlArmTest` 7/7 | CONFIRMED | - |
| 7 | run claims I can see without the readout (identity only; no k_d read) | rp12-r2-run arm/status.txt COMPLETE, i1Form=live, i1Bracket L23470, instrument = registered (reps 300, sliceDim 512, sepBar 0.0145, dropTop 0, whiten false, mcs 55, c0Seed 20261002, threads 12); identity.csv: I1_LIVE 60 rows, 60 accepted, 60 bit-for-bit; **36 of them at k >= 3 (k=3: 21, k=4: 15), all 36 match** (the K11 sort, C-4, proved by execution); I1_REGISTERED 6 of 60 (= the D-I1 preview); I2 14 of 14 match; labels sha256 c0a20662... = the dry-run's; emb hashes before == after (cmp) | CONFIRMED | - |
| 8 | residual survivors | R4 (k_d recount check off) and R8 (C0 p95 recount check off) still SURVIVE: Kotlin-vs-Python cross-checks only; the verdict is computed by Python from replicates.csv, so neither can change it | carried | LOW |

## Ruling: --analyze e0751d7c on the b5653fb7 arm outputs

VALID. (i) The arm code that produced the outputs is the reviewed code (SeparationNullBySizeTest.kt 50c4b0ef in both commits;
build.gradle.kts's certPositiveControl block is unchanged, its only delta is the nullBySize exclusion). (ii) The readout path is
byte-identical (row 2): e0751d7c reads the same files with the same functions and the same constants as a2b80ed2; only the
selftest, which runs before the readout and must be green, is larger. (iii) The outcome prints the readout blob it ran
(e0751d7c), and the arm's outputs pin nothing about the readout blob. The record names both blobs: arm b5653fb7, readout e0751d7c.

## Defects

None new. The LOW items R4, R8 and D-5 are carried as disclosed.

## --analyze sequence (run-operator)

1. No java and no construction running (the arm is finished; no window is needed: --analyze opens no DB).
2. `git -C .claude/worktrees/rp12-r2-run checkout --detach 416ac436`: a clean fast-forward. 416ac436 tracks nothing under
   experiment_results/cert_positive_control/ (count 0), so the untracked arm outputs are untouched. Then check that
   `git hash-object tools/analysis/cert_positive_control.py` = e0751d7c.
3. From .claude/worktrees/rp12-r2-run:
   `python tools/analysis/cert_positive_control.py --analyze --data-root .`
   (--data-root is accepted and is not read by --analyze: it reads experiment_results/cert_positive_control/{arm/,declared_labels.tsv,
   emb_hashes_*.json} and G12_sites.csv relative to the script's checkout, which is why it must run from rp12-r2-run; it runs the
   21/21 selftest first and writes outcome.txt and cpc_sites.csv write-once.)

## Commands (compact)

```
git diff b5653fb7 416ac436 --numstat; git diff b5653fb7 416ac436 -- build.gradle.kts src/
python (ast) top-level def/assign comparison b5653fb7 vs 416ac436 -> ['MUTANTS', '_fx', 'selftest']
python tools/analysis/cert_positive_control.py --selftest (21/21); python -O ... --selftest (21/21); --mutants (30/30)
python scratchpad/rv_mut.py, rv_mut2.py -> R1 R2 R3 R6 R7 R9 KILLED; R4 R5(equiv) R8 SURVIVED
.\gradlew.bat nullBySize --offline --no-build-cache --tests *certPositiveControl*  -> No tests found
.\gradlew.bat certPositiveControl --offline --no-build-cache                        -> 1 test, [CPC] REFUSING -DsnapshotId
.\gradlew.bat test --offline --no-build-cache --tests taxonomy.CertPositiveControlArmTest -> 7/7
.\gradlew.bat --stop -> "1 Daemon stopped"; tasklist: no java
rp12-r2-run: arm/status.txt; identity.csv counts (python csv); cmp emb_hashes_before.json emb_hashes_after.json
git ls-tree -r --name-only 416ac436 experiment_results/cert_positive_control | wc -l -> 0
```
