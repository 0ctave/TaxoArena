# POSTRUN review: RESP-PROFILE-INFO (zero calls; run with blob:1817ec8a, LF)

Reviewer: adversarial-reviewer, 2026-10-04. Registration: prog "## Registered 2026-10-04 (before any code or call) — RESP-PROFILE-INFO: ..." L24388-L24400 (_as_of 61d1c5bf), with bracket B-RP (RP-R1..R9; post-run duties R-1, R-2).
Outcome: `experiment_results/archv2/resp_profile_info/resp_profile_info_outcome.txt` (sha256 11abd604...; write-once; not committed). Log: `E:/TaxoArena_tmp/rpi_run.log` (sha256 51eed7c6...).

## Verdict: **VALID**, with two word conditions (R-RP2-X, R-IRT)

- **RP1 BEYOND-SOURCE**: CONFIRMED to the digit, and robust. It survives the R-1 trim and an independent constrained-ML 3PL fit. F-RP NOT FIRED.
- **RP2 K0-BETTER**: CONFIRMED (point to the digit; interval within 3% of the run's SE). The cross-source split does **not** flip it, unlike KI1. On the 5,716 own-source-filed items D halves and still reads K0-BETTER (descriptive). About half of D comes from the 191 cross-source filings, so the qualifier R-RP2-X is owed.
- **P1 FAILED** (0.0527 is outside [0, 0.030]); P2 Brier 0.2025; P3 Brier 0.4900; **P4 HELD** (BBH 0.3609; 0.4694 under the constrained-ML fit).

## Per-claim table (deciding claims; data object = 18-model keyed correctness, gen/eval views of REG_ARCHV2-SPLIT-2, TRAIN 11,841 / EVAL 5,907 items, 5,404 EVAL components)

| # | claim (outcome) | reviewer | result | sev |
|---|---|---|---|---|
| 1 | data object: TRAIN 11,841 of 12,351; EVAL 5,907 of 6,153; 18 models, no Llama-3-70B | own SQL read of both views (`mode=ro&immutable=1`; sha256 before = after = the pins c2930c60.../e35b7518...): 11,841 / 5,907; 18 models | CONFIRMED | — |
| 2 | IRT: builder's 3PL residuals (theta e.g. DeepSeek-R1-Distill-Llama-8B -1.971, Qwen2.5-72B +1.530) | the builder's `fit_train`/`fit_items` on MY matrices give the same theta to 3 dp. Independent joint penalised ML with theta = standardise(u) (L-BFGS, analytic gradient, \|g\|max 4e-5) reaches a **higher** penalised log-lik: -100,147.9 vs the builder's -101,364.6 (+1,216.7); theta(R1-Distill-Llama-8B) -3.661 | PARTLY (see R-IRT) | MEDIUM |
| 3 | R2_int AF-U +0.052744; K0..K4 +0.057607/+0.057527/+0.056746/+0.056747/+0.057208; SRC +0.045400; declared +0.060463 | own R2 code (shrink sum/(n_c+20), TRAIN means, EVAL sums) on the builder-fit residuals: identical to 6 dp | CONFIRMED to the digit | — |
| 4 | RP1: RWS median +0.036597, p97.5 +0.037950 (200 draws, rng 20261004+r) | own RWS (within-source TRAIN partition at AF-U's per-source size profile; EVAL size-proportional): median +0.036597, p97.5 +0.037950, max +0.038513 | CONFIRMED to the digit | — |
| 5 | RP1 robust to the estimator | constrained-ML fit: AF-U +0.055433 vs RWS p97.5 +0.039648 (max 0.040147) -> BEYOND-SOURCE | CONFIRMED | — |
| 6 | RP2: D -0.004423, spread_K 0.000861 | -0.004423 / 0.000861 | CONFIRMED to the digit | — |
| 7 | RP2 interval [-0.006118, -0.002728], SE 0.000865 (two-stage with re-fit, B 2,000) | light two-stage (TRAIN + EVAL components, IRT fixed, B 400, seed 777): SE 0.000887 -> [-0.006162, -0.002684]; the gap in SE is 2.5%. Constrained-ML fit: D -0.004563, SE 0.000936 (B 200), [-0.00640, -0.00273], spread 0.001079 -> K0-BETTER | CONFIRMED (verdict) | — |
| 8 | Support: DEFF measured 2.118 (declared 1.6, source U1 1.595), n_eff 2,789, SE 0.000865, MDE80 0.002421 | own: DEFF 2.156, n_eff 2,739, MDE80 0.002483. The registered arithmetic reproduces: 5,907/1.6 = 3,692; 0.05/sqrt(3,690) = 0.00082; 2.8 x 0.0008 = 0.0023. Realised SE is 1.08x the registered one. \|D\| = 5.1 SE; RP2 decides with margin | CONFIRMED | — |
| 9 | P4: BBH share 0.3609 (largest; MMLU_PRO 0.3114) | 0.3609 / 0.3114; constrained-ML fit BBH 0.4694, MMLU_PRO 0.2287 | CONFIRMED | — |
| 10 | pins: resp_profile_info 1817ec8a, resp_structure_common ba67f78f, union_cells_io 92a04543, cell_flips 998d39a7, union_af_route bf3f17db, v2_declared_cells f0f56805 | `git rev-parse HEAD:<f>` = `git hash-object <f>` = `tr -d '\r' | git hash-object --stdin` for all six: the working tree is LF, so there is no separate CRLF rendering | CONFIRMED | — |
| 11 | words | split words (clean/disjoint/held-out) 0; all like-with-like arms [SC], declared [DECL]; wrong(established) N/A (keyed) | CONFIRMED | — |

## Post-run duties (B-RP), supplied by this review (descriptive; the criterion stays as registered)

- **R-1 (heavy tails).** The top 0.1% of EVAL item-model cells (107 of 106,326 by e^2; threshold e^2 15.9) carry **3.06%** of sum e^2. With them dropped, R2_int(AF-U) is **+0.050731** against an RWS p97.5 of **+0.035660** (median +0.034253): BEYOND-SOURCE unchanged. Under the constrained-ML fit: share 3.38%; +0.053156 vs p97.5 +0.036466. Not printed by blob 1817ec8a (count 0 in the outcome); this review supplies it.
- **R-2 (guessing floors).** TRAIN: floor 0.10 on 6,759 items (MMLU_PRO), 0.25 on 57 (GPQA), 0 on 5,025 (BBH 3,473, MATH 773, MUSR 454, IFEVAL 325). EVAL: 0.10 on 3,376 (MMLU_PRO), 0.25 on 34 (GPQA), 0 on 2,497. The floors are non-zero as expected (the source label `MMLU_PRO` matches the FLOOR key; counted from the builder's own `floors_of`).

## Cross-source filing split of RP2 (task 3; as in POSTRUN_route_trio.md C1; unregistered, descriptive)

AF-U files **191 EVAL items** into another source's leaf (MMLU_PRO 128, MATH 51, GPQA 12), plus 311 TRAIN items. This is the same set as KEY-INFO-V2's.

| subset | R2 AF-U | K mean | D | spread_K | approx 95% (light two-stage SE) | reading |
|---|---|---|---|---|---|---|
| ALL 5,907 | +0.052744 | +0.057167 | -0.004423 | 0.000861 | [-0.00616, -0.00268] | K0-BETTER |
| own-source 5,716 | +0.054229 | +0.056365 | **-0.002136** | 0.000756 | SE 0.000813: [-0.00373, -0.00054] | **K0-BETTER** (descriptive) |
| cross 191 | +0.009500 | +0.080521 | -0.071022 | 0.007859 | — | — |

The constrained-ML fit gives the same pattern: own-source D -0.002258, spread 0.000889, SE 0.000891, so [-0.00400, -0.00051], K0-BETTER. Unlike KI1, RP2 does not fall to NEITHER on the own-source items. D still halves (R2 is a ratio, so subset D values are not additive), and on the 191 items AF-U's cell means carry almost no residual information (0.0095 vs 0.0805).

## Defects and conditions

- **R-RP2-X (MEDIUM, words).** Every quote of RP2 must carry: "K0-BETTER for AF-U as built; about half of D comes from the 191 EVAL items AF-U files into another source's leaf (R2 0.0095 vs K mean 0.0805 there); on the 5,716 own-source-filed items D = -0.0021 (approx 95% [-0.0037, -0.0005]) against spread_K 0.0008: still K0-BETTER (unregistered, descriptive)."
- **R-IRT (MEDIUM, words + engineering).** `resp_structure_common.fit_train` alternates three item Newton steps with one diagonally preconditioned, clipped theta step and re-standardises theta after each step. Its fixed point is not the penalised ML under the mean-0/SD-1 constraint: its log-lik is 1,216.7 below the constrained optimum, and the weakest model's theta is shrunk (-1.97 vs -3.66). The printed "converged in 33 iterations" means the theta change fell below 1e-7, not that the fit reached the optimum. **No verdict changes** (rows 5, 7, 9; R-1). Words: quote the IRT as "a 3PL fitted by alternating JML with standardised theta (not the penalised optimum; verdicts robust to the constrained optimum, POSTRUN_resp_profile_info.md)". Fix for forward use: optimise (u, alpha, b) jointly with theta = standardise(u) (as `irt.py` below does), or project the theta gradient onto the constraint's tangent space before stepping. Registrar: the same module serves CELL-DIFFICULTY / CELL-STRATA-EVAL; carry this note to their post-runs.
- **R-P1 (LOW, record).** P1 FAILED: R2_int(AF-U) 0.0527 is 1.76x the band ceiling.
- **N-RWS (LOW, note).** The RWS bar (median 0.0366) sits below the 6-cell SRC arm (0.0454): at AF-U's cell sizes, shrunk random within-source cell means lose source signal. This is the registered within-anchor null (sizes and source preserved), so BEYOND-SOURCE stands. AF-U also exceeds SRC descriptively (+0.0073). Quote BEYOND-SOURCE as "beyond random within-source cells of the same sizes", as registered.
- **N-OVF (LOW).** One numpy overflow warning in `exp(alpha)`, raised on a line-search trial step (log, count 1). The final alphas are bounded (max 1.80). No effect.

## Concurrency (task 4)
The read ran 16:43-18:06 (READ_STARTED / outcome mtimes). In the same window: GRANULARITY-GT (granularity_gt --run, which reads the MASSIVE intent tree from another worktree; POSTRUN_route_trio.md L14/L54) and the tail of the routing trio (RSN / KNN / KEY-INFO-V2 outcomes 16:29-16:40). All are zero-call CPU readers of their own objects, with no construction or site null, so rule 7 is not engaged. The run's view sha256 before = after = the pins, and my independent re-read reproduces every deciding digit. **Not affecting.**

## Backup
`E:/TaxoArena_backup_2026-10-04_rpi`: outcome, READ_STARTED, run log, and the 5 reviewer scripts. `SHA256SUMS.txt` has 8 lines; `sha256sum -c` gives 8 OK. The repo originals hash to the same values (11abd604... / ba717c26...).

## Commands (scratch E:/TaxoArena_tmp/rev_rpi; single-threaded BLAS; read-only)
```
python load.py                 # own SQL read of gen/eval views (immutable; sha before=after=pins) -> data.npz (11841 / 5907 x 18)
python irt.py                  # own constrained joint penalised-ML 3PL (theta=standardise(u)); EVAL items theta fixed -> irt.npz
python irt_theirs.py           # builder's fit_train/fit_items on MY matrices -> irt_b.npz; penalised log-lik of both fits
python r2.py irt_b.npz         # R2_int all arms, D, spread, RWS 200 (own), per-source shares  -> digits = outcome
python r2.py irt.npz           # same under the constrained-ML fit
python dut.py irt_b.npz 400    # R-1, R-2, cross-source 191 split, light two-stage SE/DEFF (seed 777)
python dut.py irt.npz 200      # same under the constrained-ML fit
git rev-parse HEAD:tools/analysis/<f>.py; git hash-object <f>; tr -d '\r' < <f> | git hash-object --stdin   # 6 pins equal
grep -ciE '\bclean\b|disjoint|held-out' <outcome>   # 0 ;  grep -c 'R-1\|R-2\|top 0.1' <outcome>   # 0
sha256sum -c SHA256SUMS.txt | grep -c ': OK'        # 8
```
