# READY review: ONLINE-STAGE2 (tools/analysis/online_stage2.py)

Reviewer: adversarial-reviewer, 2026-10-03. Zero calls. Branch online-stage2, tip 0b8b1900, which contains the registration
56093589. Script: **blob:6bbc40dde71447f0d8844c222ea019223b3c56ff** (`git hash-object`, LF; 0 CR bytes; sha256-lf16:d38b671ee33f633d).
It imports online_replay_lomo.py `blob:fb3a9563…` (asserted before import), and through it union_af_route bf3f17db and
g13_breakdown c29fa1c3. Registration: prog L24054-L24068. The commit touches 1 path
(`git show --name-only --format= 0b8b1900 | grep -c .` = 1).

## Verdict: READY. Conditions: the registrar's pre-data brackets B-1..B-7 must be committed before --run.

The code does what the registration says on every deciding path. The real --dry-run is clean, and my brute-force calibration
reproduces all 12 tau_m values to 5 dp. One Support defect needs a bracket, not code: OS2's per-member n and SE in Support (f)
do not reproduce (S-1 below). The rule "arithmetic that does not reproduce is NOT READY" therefore binds the run, not the
build: **--run must not start before B-1 is committed.**

## Per-claim table (deciding paths)

| # | claim | mine | status | sev |
|---|---|---|---|---|
| F | frozen means | `stream()`: `U = A["mu"][keep].copy()` is never written. `U_ref` is compared after the stream, and churn is recomputed on `U`. INTEGRITY refuses on a nonzero count. It cannot fail by design (registered as such); it is a guard that the code did not regress | CONFIRMED | - |
| C | GATE-calibrated tau for a 0.80 catch (OS-R1) | `calibrate()`: j's GATE items against the cells of sources minus {m, j} (four members). Strict share via `searchsorted(left)`. Smallest candidate in the union of observed scores with median_j >= 0.80. Dry-run tau_m tree 0.51424 / 0.57442 / 0.57440 / 0.62246 / 0.62246 / 0.57440; K_0 0.50420 / 0.56583 / 0.56588 / 0.63131 / 0.62845 / 0.56583. **My own brute-force walk reproduces all 12 to 5 dp, including every median share.** The held-out member's GATE items never enter (sources minus {m, j}) | CONFIRMED | - |
| C' | calibration granularity (descriptive) | The median j is often IFEVAL (54 GATE items) or GPQA (53), so tau moves in 1/54 = 0.0185 share steps. The median over five j is unweighted (as registered); BBH's 565 items count as one vote | NOTE (for the post-run) | LOW |
| R | rebuild every 100 buffered items (OS-R3) | `len(buf) % 100 == 0` after the append. Refit from scratch on ALL buffered items (TRAIN + EVAL), `ukm_fit` seed 0, k = min(L_m, size), TRAIN-majority names. Buffered items after the last multiple of 100 never enter a prequential cell (the tail < 100 is used only by end-of-stream filing). My mutant S1 (cadence 1, 101, …) KILLED | CONFIRMED | - |
| A | filing at arrival; transduction disclosed (OS-R4) | Order in the loop: (1) an EVAL item is filed over `U` (frozen) plus `Cb` (last rebuild), (2) the buffer decision on max-cos to `U`, (3) append, then rebuild if the count reaches a multiple of 100. So the arriving item is never in the cells it is filed against. TRAIN streams first, so every EVAL item sees the final names. The disclosure line (prequential; earlier EVAL items shape later cells; oracle k = L_m favours online; end-of-stream fully transductive, descriptive) is in `outcome_lines`. Mutant S5 (buffer cells ignored at arrival) KILLED | CONFIRMED | - |
| O1 | OS1 +/-0.020, F-OS | OS1 = `ORL.ol1_of(GB.stat(diff))`, the same TOST form as OL1. diff is against ORL's deciding symmetric batch (`W["batch"]`, 0.7265 / 0.7289). `f_os` fires on LOSS only. The stage-1 identity guard recomputes -0.0386 / -0.0687 by `ORL.replay` before any stage-2 statistic (R22 / R23 KILLED) | CONFIRMED | - |
| O2 | OS2 median catch >= 0.70 | catch = buffered / streamed over TRAIN + EVAL. `os2_word` = numpy median (mean of the 3rd and 4th of six) >= 0.70. Mutant S6 (strict >) KILLED | CONFIRMED | - |
| K | like-for-like k-means arm | The same `calibrate` / `stream` run on the K_0 unit centres with its own calibration, against batch K_0 nearest-of-all 0.7289. Same order, rebuild cadence, filing and naming | CONFIRMED | - |
| S | Support (OS1) | sqrt(0.20 x 1.263 / 6,139) = **0.006415**; n_eff 6,139 / 1.263 = **4,861**; TOST reach 0.020 - 2.487 SE = **0.00405**; DIFFERENT reach 0.020 + 0.842 SE = **0.02540**. All reproduce. DEFF source: 1.263 is MY own-stream readout in POSTRUN_online_replay_lomo (SE 0.00648). The outcome's GB.stat gave 1.245 / SE 0.00644. The registration names "the reviewer's readout of SE 0.00644", mixing the two. 1.263 is the conservative one | CONFIRMED (attribution, S-2) | LOW |
| S-1 | Support (OS2): "per-member catch rates rest on 1,000-5,000 items each (SE <= 0.016 per member)… distance 0.05 > MDE80 about 0.03: SCOREABLE" | Streamed n per member = **10,455 / 5,192 / 1,163 / 683 / 487 / 493** (dry-run "streamed if held out"). Binomial SE at p 0.75: 0.0042 / 0.0060 / 0.0127 / **0.0166 / 0.0196 / 0.0195**; MDE80 up to **0.055** > the 0.05 distance. The script's DENOMINATORS line copies "(1,000-5,000 streamed items each)" | **REFUTED as stated** (bracket; OS2 is decided by the point, so it stays scoreable but THIN) | MEDIUM |
| DR | real --dry-run | Run with no java.exe (`tasklist` count 0 at 20:00, after polling every 5 min while gemma-own-bar Gradle ran). rc 0. POOL line first; B0-2 rc 0. Manifest 53021e26… has 18 + 11 files EQUAL. GATE 2,028. Bundle rows 5.55e-17. I3 6,139/6,139; 0.7346 / 0.7265 / 0.7368 / 0.7289. 123 cells per arm. 12 calibration lines; no catch rate or OS statistic printed. DB sizes and mtimes unchanged (diff empty). Output dir absent; worktree status clean | CONFIRMED | - |
| T | selftest 15; mutants 58/58 | **SELFTEST PASSED (15 cases)** rc 0; **MUTANTS 58 of 58 KILLED, control SURVIVED** rc 0 | CONFIRMED | - |

## Own mutants (7, deciding paths)

S1 rebuild cadence off by one: KILLED (decisive). S2 calibration share non-strict (`<=`): KILLED. S3 calibration against five
cells (j's own cells included): KILLED (decisive; leakage of j into its own share). S4 median -> mean over j: KILLED (decisive).
S5 arrival filing ignores the buffer cells: KILLED (decisive). S6 OS2 bar strict: KILLED (decisive). S7 buffer refit on TRAIN
only: KILLED.

## Rulings on OS-R1..R9 and the brackets needed (pre-data; proposed wording)

- **B-1 Support (f), OS2 (MEDIUM; must precede --run):** "OS2's per-member catch rates rest on 487-10,455 streamed items
  (MMLU_PRO_LB 10,455, BBH 5,192, MATH 1,163, MUSR 683, GPQA 493, IFEVAL 487). The binomial SE at 0.75 is 0.004-0.020 and
  MDE80 is up to 0.055 for the three smallest members. OS2 is decided by the point and stays SCOREABLE, but THIN at the
  prediction (distance 0.05). No SE is claimed for the median."
- **B-2 OS-R1 (YES, ruled ACCEPTED):** "tau_m = the smallest score among the union of the five in-members' calibration scores
  at which the median over j of #{s_j < tau} / n_j is >= 0.80 (strict count; the set is open at its infimum, so the smallest
  observed score attaining it is used). The median over j is unweighted, so a member with 53 GATE items has one vote, like one
  with 1,152."
- **B-3 OS-R2 (YES, LOW):** "An item is buffered iff its max-cos to the five frozen cells < tau_m (strict). A non-buffered TRAIN
  item is absorbed into its flatLeaf cell over the five frozen cells only (buffer cells are named at rebuilds only), and it
  counts for OL-R5 naming."
- **B-4 OS-R3 (YES, ruled ACCEPTED):** "A rebuild happens when the buffer count reaches a multiple of 100, after the arriving item
  is appended, and refits from scratch on all buffered items (TRAIN and EVAL) at k = min(L_m, size), seed 0. Items buffered after
  the last multiple of 100 enter no prequential cell."
- **B-5 OS-R4 (YES, ruled ACCEPTED; the order binds):** "Each held-out EVAL item is (1) filed at arrival over the five frozen
  cells plus the last rebuild's cells, then (2) given the buffer decision, then (3) appended and, at a multiple of 100, refit.
  An item is never filed against cells it helped fit."
- B-6 OS-R6 (YES, LOW): "The median of the six catch rates = the mean of the 3rd and 4th (numpy)."
- B-7 OS-R9 (YES, LOW): "OS2 is Brier-scored over two outcomes (CALIBRATED 0.60, UNDER-CATCH 0.40); stage 1's one-term form is
  printed beside." Also S-2 (LOW): DEFF 1.263 is the reviewer's own-stream readout (SE 0.00648); the outcome's GB.stat value was
  1.245 / 0.00644.
- No bracket needed: OS-R5 (as registered), OS-R7 (integrity, as registered), OS-R8 (descriptive).

## Defects

- S-1 (MEDIUM): bracket B-1 above. Optional code fix: the DENOMINATORS line should print the measured streamed range instead of
  "1,000-5,000" (descriptive; the outcome's DENOMINATOR (OS2) line already prints the measured counts).
- C' (LOW, for the post-run): report which j decided tau_m per replay (the line already prints all five shares).

## Launch (after B-1..B-7 are committed)

From main after the merge (`Z:\FAC\TUBerlin\THESIS\TaxoArena`), no env prefix: `python tools/analysis/online_stage2.py --run`.
From the worktree instead: add `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena`. Never beside a construction or site null
(rule 7). Write the outputs once and never commit them: pin by sha256 and back up to E: with SHA256SUMS.txt.

## Commands

```
git hash-object tools/analysis/online_stage2.py      # 6bbc40dd; grep -c $'\r' = 0; git merge-base --is-ancestor 56093589 HEAD
python tools/analysis/online_stage2.py --selftest     # SELFTEST PASSED (15 cases)
python tools/analysis/online_stage2.py --mutants      # 58 of 58 KILLED; control SURVIVED
python $TEMP/orl/s2_own.py ; s2_s1.py                 # S1-S7 all KILLED
python tools/analysis/online_stage2.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0 (java count 0)
python $TEMP/orl/s2_cal.py                            # brute-force calibration: 12 tau_m and median shares equal to the dry-run
python (binomial SE / MDE80 per member at p .75; OS1 SE 0.006415, n_eff 4,861, reach 0.00405 / 0.02540)
ls -l --time-style=full-iso *.db* before/after -> diff empty; worktree git status --porcelain = 0 lines
```
