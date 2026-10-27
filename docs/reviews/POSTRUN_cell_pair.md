# POSTRUN review: CELL-DIFFICULTY (blob:20f0d98d, LF) and CELL-STRATA-EVAL (blob:e76f9a6d, LF); zero calls

Reviewer: adversarial-reviewer, 2026-10-04. Registrations: prog "## Registered 2026-10-04 (before any code or call) — CELL-DIFFICULTY: ..." L24402-L24414 and "— CELL-STRATA-EVAL: ..." L24416-L24428 (_as_of 4d2c5e41), with brackets B-CD2, B-CD9 (CD-R8/R9), C-CD1, R-3, T-CD2, B-CS (CS-R1..R7) and the R-IRT post-run duty.
Outcomes (write-once, not committed): `experiment_results/archv2/cell_difficulty/cell_difficulty_outcome.txt` sha256 11aed1ee35c609ff...; `experiment_results/archv2/cell_strata_eval/cell_strata_eval_outcome.txt` sha256 7966eebc56fe4dd6.... Logs `E:/TaxoArena_tmp/{cell_difficulty,cell_strata_eval}_run.log` (80f80fcd... / 69b655b1...).

## Verdicts

- **CELL-DIFFICULTY: VALID.** CD1 reads **DIFFICULTY-STRATA**, confirmed to the digit and unchanged under the constrained-ML 3PL. **F-CD of record NOT FIRED** (R-3: it is read from the CD1 line). T-CD2 HELD by execution. CD2 7/7 is DESCRIPTIVE. TASKFLOOR is NOT REPORTABLE (C-CD1). Word condition **R-CD-K**.
- **CELL-STRATA-EVAL: VALID.** CS1 **BEATS-RAND** (0.9447 [0.9206, 0.9676]). CS2: versus STRAT-SRC **UNDETERMINED**; versus STRAT-K0 **AF-NOT-BETTER**. **F-CS NOT FIRED.** All confirmed to the digit. R-IRT does not touch CS1/CS2, because no deciding arm uses the 3PL. Word conditions **R-CS-K** and **R-CS-X**.

## Per-claim table (data object: 18-model keyed correctness, SPLIT-2 gen/eval views; TRAIN 11,841, EVAL 5,907 items / 5,404 components; AF-U / K0..K4 cell files of the manifest 53021e26)

| # | claim (outcome) | reviewer (own script, read-only) | result | sev |
|---|---|---|---|---|
| 1 | data object 11,841 / 5,907 / 5,404; 18 models; theta (alternating fit) -1.971, -0.490, +0.422 ... | `cd.py` on the RPI reviewer's own SQL read (`data.npz`, sha256 b45af11d..., built from the views opened immutable, view sha before = after; POSTRUN_resp_profile_info row 1): 11,841 / 5,907 / 5,404 / 18; the builder's fit on my matrices gives theta = the log to 3 dp | CONFIRMED | - |
| 2 | eta2_b AF-U +0.2299; K0..K4 +0.2422/+0.2389/+0.2450/+0.2380/+0.2332; SRC +0.0874; declared +0.2365 | own CD-R1 code: identical to 4 dp in all 8 arms | CONFIRMED to the digit | - |
| 3 | RWS (200; rng 20261004+r) median +0.0746, p97.5 +0.0803 | own within-source RWS: median +0.0746, p97.5 +0.0803, max +0.0820 | CONFIRMED to the digit | - |
| 4 | median composition share 0.6985 (18 models, 0 NaN) | 0.6985 (min 0.2662, DeepSeek-R1-Distill-Llama-8B) | CONFIRMED to the digit | - |
| 5 | CD1 DIFFICULTY-STRATA | 0.2299 > 0.0803 AND 0.6985 > 0.5. The margin is 15.1 SE (component-bootstrap SE 0.0099, B 400) | CONFIRMED | - |
| 6 | R-IRT: CD1 under the constrained optimum | joint penalised ML, theta = standardise(u) (`irt.npz`; theta(R1-Llama-8B) -3.661): AF-U +0.2394 vs RWS p97.5 +0.0935 (max +0.0957); share 0.7389 -> DIFFICULTY-STRATA. P3 HELD (0.7389 lies in [0.4, 0.8]) | CONFIRMED (no verdict change) | - |
| 7 | T-CD2: CD1 ignores the CD2 inputs | (a) code: `flips` enters only flip_boot / calibration / task_floor_sensitivity, none writes I, arms or the CD1 keys of st; (b) EXECUTION on the builder's PLANTED fixture (`tcd2.py`): the CD1 block (4 lines) is byte-identical with the flip list as registered, reversed, rotated and dropped. Discriminator: CD2 3 -> 0 when dropped, so the patch ran; (c) real data: rows 2-4 reproduce with no flip-cell input at all. On real data a dropped or permuted list REFUSES at flip_cells / check_flips, a precondition, not a number change | CONFIRMED | - |
| 8 | CD2 7/7 MULTIDIM (descriptive): exp / k per cell | own: identical expectations and k (0,0,0,0,0,4,10). Constrained fit: k 1,0,1,5,5,9,6, all p <= 0.009 -> 7/7 after BH | CONFIRMED (descriptive; B-CD2 words) | - |
| 9 | CS1 ratio 0.9447 [0.9206, 0.9676]; MAE RAND 0.03912, STRAT-AF 0.03695 | `cs.py` (own CS-R1/R2/R7 implementation, n 100, no IRT): 0.03912 / 0.03695 = 0.9447. Interval [0.92045 at bs[49] / 0.9206 at U.pct's bs[50], 0.96758]. SE log 0.0129 | CONFIRMED to the digit | - |
| 10 | CS2: spread_K 0.00043; D_SRC -0.00069 [-0.00182, +0.00042]; D_K0 +0.00030 [-0.00045, +0.00110] | identical (K_s MAEs 0.03642/0.03647/0.03674/0.03685/0.03681) | CONFIRMED to the digit | - |
| 11 | R-IRT on CELL-STRATA-EVAL | RAND / STRAT-AF / K_s / SRC use only y and the cells (model_errors). The irt dict feeds IRT-ANCHOR, STRAT-AF+IRT and the keep-mask of NEYMAN only. Row 9-10 reproduce with no 3PL at all. P3 (IRT-ANCHOR 0.8523) was not re-fitted: descriptive, R-IRT words | CONFIRMED (deciding untouched) | - |
| 12 | Support CSE: planning SE 0.024, MDE 0.066; measured SE 0.0129, MDE 0.0362 | 0.10/sqrt(18) = 0.0236; 2.8 x 0.024 = 0.067. ln 0.9447 = -0.0569 = 4.4 measured SE; per-model ratio < 1 in 17/18. CS2 vs SRC: SE(D) about 0.00057, MDE80 about 0.0016 > \|D\| 0.00069: UNDETERMINED is below the MDE, as the Support (f) line DESCRIPTIVE-ONLY foresaw | CONFIRMED | - |
| 13 | Support CD: DEFF 1.6 declared, n_eff 3,690 | 5,907 / 1.6 = 3,692. Measured for eta2_b (component vs item bootstrap, TRAIN means fixed): DEFF 0.95, n_eff about 6,200. The outcome prints only Kish m 1.3115, no measured DEFF (LOW). The verdict is a percentile classification, so DEFF does not enter it | CONFIRMED | LOW |
| 14 | Predictions | CD P1 Brier (0.6-1)^2 = 0.1600; P2 HELD; P3 HELD. CSE P1 HELD, Brier 0.0625; P2 3-way Brier 0.0225+0.2025+0.09 = 0.3150; P3 HELD | CONFIRMED | - |
| 15 | pins | `git hash-object` = `git rev-parse HEAD:` for cell_difficulty 20f0d98d, cell_strata_eval e76f9a6d, resp_structure_common ba67f78f, union_cells_io 92a04543. The log prints the same LF blobs | CONFIRMED | - |
| 16 | hygiene | both logs: view sha256 before = after = pins; B0-2 rc 0; IDENTITY REPRODUCED. Split words: clean/disjoint 0 in both outcomes. "held-out" 22 in CSE, all "held-out model" (leave-one-model-out, the registered wording, not a data-split claim) | CONFIRMED | LOW |

## Cross-source filing split (unregistered, DESCRIPTIVE; the same 191 EVAL items as RPI/KEY-INFO-V2: MMLU_PRO 128, MATH 51, GPQA 12)

| test | subset | AF-U | comparator(s) | reading |
|---|---|---|---|---|
| CD1 | own-source 5,716 | eta2 +0.2360; share 0.6957 | own-source RWS p97.5 +0.0947 (median +0.0891); K0 +0.2445; SRC +0.0881 | DIFFICULTY-STRATA; AF-U still below K0 |
| CD1 | cross 191 | eta2 -0.1019 | K0 +0.0505 | AF-U's TRAIN cell means do not predict b there |
| CD1 (constrained fit) | own 5,716 | +0.2457 | K0 +0.2534 | same |
| CS (n 100) | own-source 5,716 (population changed) | ratio 0.9434 [0.9114, 0.9770] | D_SRC **-0.00139 [-0.00250, -0.00031]** (spread 0.00041); D_K0 -0.00032 [-0.00113, +0.00052] | vs SRC would read **AF-BETTER**; vs K0 UNDETERMINED (it reads AF-NOT-BETTER on all 5,907) |

The second CS row changes the estimand (accuracy on 5,716 items), so it is not a re-scoring of CS2. It does show that CS2's two words depend on the 191 cross-source filings.

## Defects and conditions

- **R-CD-K (MEDIUM, words).** DIFFICULTY-STRATA is against random within-source cells only. AF-U's eta2_b (0.2299) is BELOW all five K_s seeds (0.2332-0.2450; mean 0.2394) and below declared (0.2365), and also under the constrained fit (0.2394 vs mean 0.2480). Quote: "AF-U cells are difficulty strata beyond random within-source cells of the same sizes (eta2_b 0.230 vs RWS p97.5 0.080; composition share 0.70); per-source k-means cells stratify difficulty at least as well (0.239, descriptive)". Never write "the tree finds difficulty strata" without the K_0 clause.
- **C-CD1 (MEDIUM, record).** The outcome prints 7 TASKFLOOR lines without the NOT REPORTABLE reason (grep count 0), as C-CD1 foresaw ("if at all"). The registrar records them NOT REPORTABLE (TASK_OPTIONS disagrees with the data on movie_recommendation and reasoning_about_colored_objects). Nothing quotes them.
- **R-3 (record).** The outcome prints no F-CD-of-record line (count 0). F-CD of record is NOT FIRED, read from the CD1 line. The printed "no falsifier verdict" refers to the CD2 leg only.
- **R-CS-K (MEDIUM, words).** BEATS-RAND is a design contrast. STRAT-AF's gain over RAND is matched or exceeded by per-source k-means strata (MAE 0.03666 vs 0.03695; AF-NOT-BETTER) and is not separated from 6 source strata (0.03764). Quote: "AF-U-cell strata beat simple random sampling at n 100 (MAE ratio 0.945 [0.921, 0.968]); they are not better than per-source k-means strata and not separated from source strata (UNDETERMINED, below the MDE)". No SQ4 "the tree cuts evaluation cost" sentence; F-CS did not fire, but CS2 gives no support for that sentence either.
- **R-CS-X (LOW, words).** CS2's two words depend on the 191 cross-source filings (table above). Quote CS2 with "for AF-U as built; on the 5,716 own-source-filed items, versus SRC D -0.0014 [-0.0025, -0.0003] (unregistered, descriptive, a different population)".
- **R-IRT (carried).** CD1 is unchanged under the constrained optimum (row 6) and CSE's deciding numbers do not use the 3PL (row 11). The words of POSTRUN_resp_profile_info apply to every quote of the CD IRT numbers and of CSE's IRT-ANCHOR / STRAT-AF+IRT.
- **N-SUP (LOW).** CD prints no measured DEFF. This review supplies DEFF 0.95 for eta2_b (row 13). CSE's measured SE (0.0129) is below the planning SE (0.024), and both reproduce.
- **N-CONC (note).** RPI read 16:43-18:06; CD 18:08:22 (run dir) to 18:09:14 (outcome); CSE 18:09:15 (run dir) to 18:38:27 (outcome). The chain_sa_tl script started at 19:32. All were sequential zero-call readers, with no construction or site null, so rule 7 is not engaged. Not affecting.

## Backup
`E:/TaxoArena_backup_2026-10-04_cell_pair`: both outcomes, both READ_STARTED markers, both run logs, and the 6 reviewer scripts. `SHA256SUMS.txt` has 12 lines and `sha256sum -c` gives 12 OK. The repo outcomes hash to 11aed1ee... / 7966eebc..., equal to the backup.

## Commands (scratch E:/TaxoArena_tmp/rev_cell; single-threaded BLAS; read-only; data.npz / irt*.npz copied from rev_rpi)
```
python cd.py irt_b.npz     # CD1 all arms, RWS 200, share, cross-source split + own-source RWS (builder fit) -> rows 2-4, table
python cd.py irt.npz       # same, constrained-ML fit -> row 6
python cd2c.py irt_b.npz irt.npz            # CD2 exp/k both fits -> row 8
TMP=TEMP=TMPDIR=E:/TaxoArena_tmp/rev_cell/sbx python tcd2.py   # T-CD2 on the PLANTED fixture: 4/4 CD1 blocks identical; CD2 3->0
python cs.py               # CS1/CS2 n 100, B 2000 two-level bootstrap -> rows 9, 10, 12
python cs_own.py           # same on the 5,716 own-source items (descriptive)
python deff.py             # eta2_b component vs item bootstrap -> row 13
for f in cell_difficulty cell_strata_eval resp_structure_common union_cells_io; do git hash-object tools/analysis/$f.py; git rev-parse HEAD:tools/analysis/$f.py; done
grep -ciE '\bclean\b|disjoint' <outcome>; grep -c 'NOT REPORTABLE' <cd outcome>; grep -c 'F-CD of record' <cd outcome>   # 0 / 0 / 0
sha256sum -c SHA256SUMS.txt | grep -c ': OK'   # 12
```
