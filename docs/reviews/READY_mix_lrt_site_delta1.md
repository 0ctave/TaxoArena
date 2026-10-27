# DELTA READY 1: MIX-LRT-SITE eigh PCA fix at 54eccdf (adversarial reviewer, 2026-09-26, zero calls, no real-data statistic)

## VERDICT

**MIX-LRT-SITE at 54eccdf: READY-WITH-CONDITIONS. mix_lrt_site.py is MERGEABLE by path. The fresh re-run may proceed after conditions DC1-DC3 (section 4).** None of the conditions needs a code change.

- The fix is what ruling (a) asked for. `pca_basis` uses `np.linalg.eigh` of the scatter, sorts descending with a stable argsort, and has one route and no fallback. It is the only change on the statistic path. The diff 54eccdf^..54eccdf has 7 hunks and one of them is code the run executes (L500, `pca_basis`). `draw_cell`, `obs_cell`, `leaf_cell`, the generator, the streams and the fits are byte-unchanged.
- Correctness is checked on the cells the run will use. The eigh axes equal the thin SVD's to at most 3.8e-12 (sin of the largest principal angle, p = 5/10/20) on the 5,893 real cells I compared:
  - all 282 observed sites;
  - all 106 leaves with n >= 110;
  - all 3 x 999 draws at the three deciding sites;
  - all 17,313 af_bareq512_s42 draws swept, with every 10th thin-checked;
  - a sample of the other trees' draws.
  Every one of these cells returned finite, orthonormal axes in descending order. The old route raises on 4 of the 5,505 draws I tested with it, including frozen n00000109 b 10.
- **C1 is settled with respect to gaps.** Every cell that can decide C1 has a relative eigengap at p = 10 of at least 4.47e-4, far from a tie. These are the 3 observed deciding matrices plus all 2,997 of their possible draws (B = 999 included). The observed gaps are 1.22e-2, 9.09e-2 and 2.86e-2.
- The builder's claims reproduce to the digit:
  - selftest 127 checks, rc 0, the same 127 check lines as the builder's log;
  - ST-PCA worst sin 2.9e-13 and worst relative LR 1.2e-13;
  - ST-REG 2.3e-14;
  - 51/51 mutants (read from the builder's log).
- My own mutants on the eigh path: **6 of 6 non-equivalent KILLED**; 1 declared-equivalent control SURVIVED, as expected.
- No real-data statistic was printed. I checked the builder's four logs and my own for LR-like numbers (section 1, claim 3).

What I did NOT run: `--run` or `--analyze`. I computed no observed-site LR. The only GMM fits I ran on real-derived input were on three null draws (small_gap.py) and inside ST-REG, and only the relative difference between two bases was printed. The DBs (embeddings_cache.db, snapshots.db, snapshots_frozen.db, their -wal (0 bytes) and -shm) have the same size and mtime as at the start of the session (`ls -la --time-style=full-iso`). The per-table pins in my --dry-run equal the builder's (`diff` of the six `[PIN table/row]` lines, empty). The worktree is clean after every run (`git status --short | wc -l` = 0).

### Pins (the LF rendering is of record; worktree gmm-tests is LF, 0 CR bytes; `git hash-object` = `git rev-parse 54eccdf:tools/analysis/mix_lrt_site.py`)

| file @ 54eccdf (branch gmm-tests) | blob | sha256-lf16 | sha256-crlf16 (the main checkout's rendering, core.autocrlf true) |
|---|---|---|---|
| tools/analysis/mix_lrt_site.py (2,390 lines) | blob:3e6a682ca2b73db5198c670249a4bbef974b7740 | sha256-lf16:565c05b6bcffd856 | sha256-crlf16:bdd041ed7fc5859a |

These files are unchanged from the READY dde660e / merge 346ea3b (`git rev-parse` at main HEAD, b617888 and 54eccdf are equal for each):

- flat_mix_mmlu.py c5cc7934
- WithinNodeCloudFixture.java e983a3c4
- pool_guard.py 6521b51a
- split_side.py 05224b5a
- the four site-null CSVs 1577e9e4 / 8ed1b699 / f69179a0 / f6875fc1

Scope checks:

- `git diff --name-only b617888 54eccdf | wc -l` = 1.
- `git diff --name-only 346ea3b HEAD -- tools src config .gitignore | wc -l` = 0: main has changed only records since the merge.
- Main HEAD still holds mix_lrt_site.py ef965573.
- `git merge-base --is-ancestor 31d092e 54eccdf`: true (the registration precedes the code).

Environment: numpy 1.26.3 (OpenBLAS 0.3.23.dev, internal LAPACK), scikit-learn 1.8.0, scipy 1.14.1.

## 1. Per-claim table

| # | claim | result | evidence (my command / script) | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1a | Only `pca_basis` changed on the statistic path | CONFIRMED | `git diff 54eccdf^ 54eccdf \| grep -c '^@@'` = 7. The hunks are the docstring (2), `pca_basis` (1), selftest (2), MUTANTS (1) and argparse (1). I read the full diff: `draw_cell` L581 and the functions after it are untouched, and so are the generator, the streams, the fits and q | 1 statistic hunk | - |
| 1b | Nothing else changed since b617888 / 346ea3b | CONFIRMED | `git diff --name-only b617888 54eccdf \| wc -l` = 1. The imports and inputs are unchanged by blob (pins above). Main since 346ea3b: 0 files under tools/, src/ or config/ | 1 file | - |
| 1c | Pins 3e6a682c / 565c05b6bcffd856 / bdd041ed7fc5859a | CONFIRMED | `git hash-object`; `git show 54eccdf:... \| sha256sum`; the same with `sed 's/$/\r/'` for the CRLF rendering | equal | - |
| 2a | eigh, stable argsort, descending order | CONFIRMED | Code L504-L512. The Rayleigh quotients of the returned top-21 axes are non-increasing on every one of the 5,893 + 17,313 - 1,740 = 21,466 distinct cells I swept (`desc` check, gap_sweep.py). Mutant R2 (no transpose) and R3 (axes 10 and 11 swapped) are KILLED | 0 order violations | - |
| 2b | Rank-deficient n < d | CONFIRMED | Trailing eigenvalues are harmless. The smallest site n is 119, so rank >= 118 > p + 1 = 21, and the d - n + 1 near-zero eigenvalues never reach the top 21. On the real draws the relative gap at p = 20 is at least 6.4e-5 (af_bareq512 draws). Mutant R5 (top axis dropped ONLY when n < d) is KILLED by the ST-PCA n < d fixtures | see section 2 | - |
| 2c | Ties | CONFIRMED for ties INSIDE the top p (ST-PCA repeated-eigenvalue fixture, 3.8e-15). A tie AT p is not tested and has no code policy | The fixture has gaps at 5, 10 and 20 by construction. See section 2 for the measured gaps and the proposed policy | - | LOW (D3) |
| 3a | ST-REG executes the registered stream | CONFIRMED | st_reg: `draw_stream(0, 39, 10)`, then `within_node_cloud_eigen(ctx.mu, ctx.s, ctx.Vt, m, n, rng)`, then `rng.integers(..., size=3)`. This is the same order as `draw_cell` L583-L586. My gap_sweep, independently: "n00000109 b 10: old route raises True; eigh sin vs thin 2.3e-14" | 2.3e-14 = 2.3e-14 | - |
| 3b | No real-data statistic leaked into a log | CONFIRMED | In the builder's four logs, every decimal number that is not a pin, CPU figure or ST-PCA/REG ratio comes from a synthetic or fixture check (ST3-eigen 0.0057, ST-EQ D 0.0754 / medians 114.14 / 115.04 on the JVM F2 fixture, ST-INV 336.7644, dry-run synthetic timings). The route sweep prints counts only. ST-REG does compute three GMM fits per p on the real-derived null draw b 10 but prints only the relative difference | 0 real-data LR | MEDIUM (D2, a record issue) |
| 4 | --route-sweep: 58,518 cells, 0 failures | CONFIRMED, af_bareq512_s42 re-run in full | gap_sweep.py (the same loop: `draw_stream`, `within_node_cloud_eigen`, `pca_basis`) over all 17,313 af_bareq512 draws: 0 non-finite, 0 non-orthonormal (max 4.7e-15), 0 out of order; 1,740 thin-checked, max sin 6.4e-13. Arithmetic: 66 x 199 + 3 x 800 = 15,534; 69 x 199 = 13,731; 60 x 199 = 11,940; 87 x 199 = 17,313; sum 58,518 | 17,313 = 17,313, 0 = 0 | LOW (D1: the sweep is convergence-only) |
| 5a | Selftest 127 checks | CONFIRMED | `--selftest`, rc 0, 388 s. The 127 `ok` lines match the builder's exactly (`diff`, empty) | 127 = 127 | - |
| 5b | ST-PCA 10 fixtures, worst sin 2.9e-13, LR 1.2e-13 | CONFIRMED | same run (n 150 d 32: 2.9e-13; n 2000 d 512: 1.2e-13) | equal | - |
| 5c | Mutants 51/51 | CONFIRMED from the builder's log (51 lines KILLED; the scatter-svd mutant is killed by LinAlgError in ST-REG). My own 7 mutants are in section 3 | 51/51 | - |
| 6 | Selftest needs TAXOARENA_DATA_ROOT and fails closed | CONFIRMED | Without the variable in the worktree, `selftest(only={'ST-REG'})` gives SystemExit "[POOL-GUARD] database not found: ...gmm-tests\embeddings_cache.db (set TAXOARENA_DATA_ROOT)". In the main checkout DATA_ROOT defaults to ROOT, where the DBs are. ACCEPTABLE, disclosed. But see D2 (registration "synthetic only") and D4 (LAPACK dependence) | fail-closed | MEDIUM (D2), LOW (D4) |
| 7a | New cost: deciding leg 72.5 (68.6 + 3.0 + 0.9), P8 context 71.6 | PARTLY | My `--dry-run` on the same blob: TOTAL 81.1 = p10 59.4 + escalation 2.7 + p5/p20 18.2 + observed 0.7. Post-drop 62.8; P8 context 62.2. The synthetic dry-runs vary: 74.4, 83.6, 68.6 and 59.4 for p10 across four runs. The eigh saving is real: a 512 x 512 scatter takes 22.7 ms with eigh against 55.5 ms with svd (process time, 20 reps) | 62.8 vs 72.5 post-drop | LOW (D5) |
| 7b | Under the 80 cap; P8 still expected FAILED | PARTLY | Post-drop is 62.8-72.5 against 80: under. P8 projects 62.2-71.6 against 60, so "expected FAILED" holds on every projection, but mine clears the bar by only 2.2. On the old blob the real first chunk projected p10 +1.3% and p5/p20 +41% above the synthetic dry-run. The drop decision in my dry-run is at the boundary (81.1 against 80), so whether D6 exists is decided by timing noise | - | LOW (D5) |
| 8 | Fresh re-run procedure | CONFIRMED with conditions (section 4) | `experiment_results/mix_lrt_site` is absent in main (`ls`: No such file). The evidence dir `...\evidence_2026-09-25\mix_lrt_incident_state_0445\`: `sha256sum -c SHA256SUMS_source` gives 14 OK, equal to record L21098 ff. item 1 (e). FLAT is complete (b4248a6), so MIX never runs concurrently with it. meta.json carries the script pins, so a mixed state is refused anyway | - | - |

## 2. Gaps: eigh at n < d, ordering, ties

Definition: the relative gap at p is (lambda_p - lambda_{p+1}) / lambda_p, where lambda are the Rayleigh quotients ||Xc v_i||^2 of the axes `pca_basis` returns. They were checked against the thin SVD's s^2 on the observed sites and are equal to printed precision on all 282. Source: gap_sweep.py, rc 0, 953 s, single-threaded.

| cells | count | min rel gap p5 / p10 / p20 | max sin(angle) vs thin SVD (p 5/10/20) | old route raises |
|---|---|---|---|---|
| frozen observed sites | 66 | 8.3e-3 / 9.5e-3 / 1.9e-3 | 3.2e-13 | 0 / 66 |
| **deciding n00000013 observed (n 549)** | 1 | 9.83e-2 / **1.22e-2** / 2.19e-2 | 2.0e-14 | no |
| **deciding n00000014 observed (n 402)** | 1 | 5.90e-2 / **9.09e-2** / 3.20e-2 | 1.2e-14 | no |
| **deciding n00000055 observed (n 292)** | 1 | 7.43e-2 / **2.86e-2** / 4.24e-2 | 2.6e-14 | no |
| **n00000013, all 999 draws** | 999 | 5.4e-4 / **9.7e-4** / 1.1e-3 | 3.3e-12 | 0 / 999 |
| **n00000014, all 999 draws** | 999 | 4.1e-3 / **4.47e-4** / 1.5e-3 | 1.2e-12 | 0 / 999 |
| **n00000055, all 999 draws** | 999 | 2.8e-3 / **8.3e-4** / 7.0e-4 | 7.7e-13 | 0 / 999 |
| frozen draws, sample b 0, 10, 100, 198 | 252 | 7.9e-3 / 4.4e-3 / 8.4e-4 | 1.0e-12 | 1 / 252 (n00000109 b 10) |
| af_clean_s42 observed / leaves / draws sample | 69 / 31 / 276 | p10 min 2.0e-3 / 1.0e-2 / 4.8e-3 | <= 2.3e-13 | 0 |
| o0_clean_s42 observed / leaves / draws sample | 60 / 28 / 240 | p10 min 8.1e-3 / 2.0e-3 / 4.1e-3 | <= 4.5e-13 | 0 |
| af_bareq512_s42 observed / leaves | 87 / 22 | p10 min 1.47e-4 (n00000074) / 7.4e-3 | <= 3.2e-13 | 0 |
| af_bareq512_s42 ALL draws | 17,313 (1,740 thin-checked) | 1.1e-3 / 1.28e-4 / 6.4e-5 | 6.4e-13 | 3 / 1,740 |
| the 3 smallest p10 gaps of those draws (n00000120 b 68, n00000132 b 29, n00000134 b 131) | 3 | p10 1.28e-4 / 2.78e-4 / 8.0e-4 | 3.8e-12 / 1.6e-12 / 2.8e-13; relative p10 LR difference 5.0e-13 / 1.2e-13 / 2.7e-14 (small_gap.py; no LR printed) | converges |

Reading:

- **Top-p axes are well-defined wherever the run reads them.** The smallest relative gap at p = 10 anywhere is 1.28e-4 (a non-deciding af_bareq512 draw). Subspace perturbation theory puts the numerical error at about eps x lambda_1 / (lambda_10 - lambda_11), or at most about 2e-11 given lambda_1 / lambda_20 <= 9.9 (the READY). The measured error is 3.8e-12. Both are two orders below the 1e-9 bar and ten below anything the LR could feel.
- **C1 is exhaustively covered.** The null draws are deterministic: the same stream, generator and inputs, with the DB pins equal. So the 3 observed matrices and the 2,997 draws above are exactly the cells that can decide C1. None is near a tie; the minimum is 4.47e-4.
- **Policy when the gap is 0 (a tie at p).** The top-p subspace is then not unique: `eigh` returns a LAPACK-determined basis of the tied eigenspace, the stable argsort's tie-break is by index, and the LR is not a function of the data alone. The code has no gap check (D3). Such a tie has probability 0 under the continuous null and no measured cell comes within 4 orders of magnitude of one. The ruling I propose (DC2 (b)) needs no code: a cell whose relative gap at the deciding p is below 1e-10 counts as a FAILED FIT under ruling A3, so it VOIDs C1 at a deciding site and is excluded and counted elsewhere. The post-run review re-derives the gaps of the 282 observed sites (cheap, zero-statistic). The deciding-site draws are already done here.
- **The old route's failure rate.** It raised on 4 of the 5,505 draws I tested it on (about 0.07%). Over 58,518 draws that is about 40 expected crashes, so the incident was not a single freak cell.

## 3. Reviewer's mutants on the eigh path (my_mutants.py, through the script's own `_exec_selftest`, subsets ST-PCA + ST-REG; original PASS)

| mutant | result | killed by |
|---|---|---|
| R1 eigenvectors taken as rows, `V[order, :]` | KILLED | ST-PCA n 150 d 32: sin 1.0, LR 1.9e-1 |
| R2 no transpose, `V[:, order]` | KILLED | ST-PCA: sin 1.0, LR 6.8e-1 |
| R3 axes 10 and 11 swapped (wrong at the p = 10 boundary only) | KILLED | ST-PCA: sin 1.0, LR 1.1 |
| R4 float32 scatter | KILLED | ST-PCA: sin 1.2e-4, LR 1.6e-6 (the 1e-9 bar discriminates precision loss) |
| R5 top axis dropped ONLY when n < d | KILLED | ST-PCA n 60 d 256 (rank-deficient): sin 1.0 |
| R6 centred on the first row, not the mean | KILLED | ST-PCA: sin 9.8e-1 |
| R7 `np.argsort(-w, stable)`: a declared EQUIVALENT control | SURVIVED (expected) | - |

Vacuity probe: I applied `--route-sweep`'s per-cell check (finite, and max |V20 V20^T - I| < 1e-8) to mutant R3's output on a synthetic n 140 d 256 matrix. The check PASSES while the sin angle against the thin SVD is 1.00 (D1).

## 4. Conditions

- **DC1 (merge by path, the run-operator or coordinator).**
  - Run `git checkout 54eccdf -- tools/analysis/mix_lrt_site.py`, then `git commit -- tools/analysis/mix_lrt_site.py`: that one path only; no application.yml, .gitignore, .env or report/.
  - Verify:
    - `git rev-parse HEAD:tools/analysis/mix_lrt_site.py` = 3e6a682ca2b73db5198c670249a4bbef974b7740.
    - The working file sha256 = bdd041ed7fc5859a... (CRLF, the main checkout).
    - The first run's `[SCRIPT]` line prints blob:3e6a682c / sha256-lf16:565c05b6bcffd856 / sha256-crlf16:bdd041ed7fc5859a.
    - `git merge-base --is-ancestor <merge> HEAD`.
- **DC2 (the registrar, before the first --run; insertion only).** Record:
  - (a) This delta READY with the pin.
  - (b) The gap-tie policy of section 2 as a pre-data ruling: relative gap < 1e-10 at the deciding p means a failed fit under A3.
  - (c) A bracket at the registration's SELFTEST line (L20664 area, "--selftest, synthetic only"): ST-REG reads the real frozen n00000109 members and fits the GMM on its null draw b 10, printing only a relative difference. This is authorised by ruling (a)'s regression case and is not a statistic of record (D2).
  - (d) The cost re-projection: post-drop 62.8 (reviewer) / 72.5 (builder) against 80; P8 context 62.2 / 71.6 against 60, still EXPECTED FAILED but by as little as 2.2; the drop decision sits at the boundary (81.1 against 80) and is taken by the guard from the real first chunk (D5).
- **DC3 (the run procedure, R6 as amended).**
  - Rule 7 throughout: one single-threaded python process ([THREADS] all 1), kill by PID only, no construction, no W-window, -wal and -journal empty.
  - Order:
    1. `python tools/analysis/mix_lrt_site.py --dry-run` from main after DC1. It must print the new [SCRIPT] pins and the same six `[PIN table/row]` lines as this review (embeddings 641ff6fa..., queries cdeca05e..., graphs 30e2cdc8 / 30f5274d / d5eb7b98 / 9956b926).
    2. `--run` repeated until "0 chunks remaining", into a NEW `experiment_results/mix_lrt_site/state/` (absent now).
    3. Record the [COST] line, plan.json (dropped or kept) and the post-drop sum p10 + escalation + observed against 80.
    4. `--analyze` ONCE (write-once).
  - A LinAlgError or any other crash is a new incident: stop and do not patch in place.
  - R7 is unchanged for the post-run review. It adds: re-derive the observed-site gaps (DC2 (b)); confirm 0 failed fits at the deciding sites; the realised CPU against P8 and 80.

## 5. Defects

- **D1 LOW: `--route-sweep` is convergence-only.**
  - Its per-cell check (finite and orthonormal) passes any orthonormal basis, including a wrong subspace (mutant R3 passes it, sin 1.00).
  - Its "0 failures" meets ruling (a)'s letter ("the route converges everywhere") and nothing more.
  - Subspace correctness is carried by ST-PCA, ST-REG and this review's thin-SVD comparison on 5,893 real cells.
  - It also sweeps draws only, not the 282 observed sites or 106 leaves; this review covered those (0 bad, <= 3.2e-13).
  - Fix (queue MIX-FLAT-SELFTEST-GAPS): add a thin-SVD spot check and a printed minimum gap.
- **D2 MEDIUM (record): the selftest is no longer synthetic-only.**
  - The registration says "--selftest, synthetic only".
  - ST-REG reads real members and runs GMM fits on a real-derived null draw. Nothing decision-relevant is printed, and ruling (a) required the case.
  - Fix: the DC2 (c) bracket. No code change.
- **D3 LOW: no gap policy in code.**
  - A tie at p is undefined behaviour.
  - Measured: none within 4 orders of magnitude.
  - Fix: the DC2 (b) ruling.
- **D4 LOW: ST-REG asserts a LAPACK non-convergence.**
  - The assertion is "the old route raises". A numpy or OpenBLAS change that makes `svd` converge on that cell would fail the selftest. That fails closed, but as a false alarm.
  - Fix: pin the environment line in the outcome (numpy 1.26.3, OpenBLAS 0.3.23.dev) or downgrade that one check to a printed note in a later build.
- **D5 LOW: the cost projection is noise-dominated near two bars.**
  - Synthetic p10 ranges from 59.4 to 83.6 over four dry-runs.
  - P8 (60) and the drop trigger (80) both sit inside that range.
  - No code change; the guard decides from the real first chunk as registered (DC2 (d)).
- **D6 LOW (timing, disclosed):**
  - The fix commit 54eccdf (04:53:20) precedes the registrar's record of ruling (a) in aaa09b1 (04:56:20).
  - The ruling is the orchestrator's, issued after the 04:47:49 incident. It is pre-data and no statistic exists.
  - This is the same pattern as O2 in dde660e.

## 6. Commands (session scratchpad `delta1\`; every python run had OMP / OPENBLAS / MKL = 1, one process at a time; worktree clean after each)

- `python tools/analysis/mix_lrt_site.py --selftest` in the worktree with TAXOARENA_DATA_ROOT set to main: selftest.log, rc 0, 127 checks, 388 s. `diff` of the ok-lines against the builder's gmm_logs_54eccdf/mix_selftest.log: empty.
- `python my_mutants.py`: my_mutants.log (7 mutants plus the route-sweep vacuity probe).
- `python gap_sweep.py frozen,af_clean_s42,o0_clean_s42,af_bareq512_s42 10`: gap_sweep.log, rc 0, 953 s.
- `python small_gap.py`: small_gap.log (the three smallest-gap draws; eigh against svd timing).
- `python tools/analysis/mix_lrt_site.py --dry-run`: dryrun.log, rc 0 ("zero statistics on real data, nothing written").
- ST-REG without TAXOARENA_DATA_ROOT: SystemExit, fail-closed.
- DB check: `ls -la --time-style=full-iso embeddings_cache.db* snapshots*.db*` at the start and the end of the session; sizes and mtimes identical, -wal 0 bytes.
- `sha256sum -c SHA256SUMS_source` in the evidence dir: 14 OK.
