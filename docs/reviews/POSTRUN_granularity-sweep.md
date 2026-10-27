# POST-RUN review: GRANULARITY-SWEEP (adversarial; zero calls; read-only)

Reviewed: outcome `experiment_results/archv2/granularity_sweep/granularity_sweep_outcome.txt` sha256
989023540370dc4626eb9aa37e49a8e6c603b73961c68410d79dde11f2035363 (= the backup copy in E:/TaxoArena_backup_2026-10-06_granularity-sweep;
`sha256sum -c SHA256SUMS.txt` 5/5 OK). Script tools/analysis/granularity_sweep.py blob:1cf20fe88993bbcdfb780fd34a1b3de38dcf6cf8 (LF, of
record; = READY c963f646's pin; `git hash-object` on main = 1cf20fe8; merge 000ae9cf touches 1 path, `git show --name-only --format= 000ae9cf
| wc -l` = 1; df0f81bf is an ancestor of HEAD). Registration prog L24828-L24840 with the registrar's brackets (df0f81bf). Pool
pv2_1575de61bb20e977 (content-closed under CK-CLOSE-v2, residual disclosed). Label status: every arm [SC] (source-conditioned).

## VERDICT: VALID. GS1 = NOT-SHOWN (sub-reason: D_lo's 95% two-stage lower bound -0.00151 <= 0), as registered.

Conditions: the words of record below (W-1..W-4); Support as realised (table) printed beside the registered one; PR-1 disclosed.

## Per-claim table (deciding claims)
| # | claim | reviewer's number | verdict | sev |
|---|---|---|---|---|
| 1 | Data object: 5,907 EVAL / 5,404 components; TRAIN 11,841; GATE 1,944; roster 18 | own key read (V.read_key, UNUSABLE_CELL, MATH-FIX overlay): TRAIN 11,841, EVAL 5,907, GATE 1,944, components 5,404, roster 18; view sha before = after (gen c2930c60..., eval e35b7518...) | CONFIRMED | - |
| 2 | IDENTITY: best single 0.6049, AF-U 0.6201, K0 0.6271 | own policy (per-cell argmax of TRAIN correct counts, sorted-roster tie-break) on AF-U and K0 cells: 0.6049 (Qwen2.5-72B-Instruct) / 0.6201 / 0.6271 | CONFIRMED (4 dp) | - |
| 3 | GATE curve and k* = 100 | own re-fit (skm_best = the registered k-means; own renormalisation, own scipy Ward cut, own filing, own policy): GATE mean +0.00535 / +0.00535 / +0.00823 / +0.00720 / -0.00730 at 25/50/100/200/400 -> k* 100 (margin over k 200: 0.10pp, against the registered GATE SE ~1.05pp) | CONFIRMED (to the digit) | - |
| 4 | G_KW(k) on EVAL, seed means and the 30 per-seed values | own: +0.01571 / +0.01971 / +0.02262 / +0.02326 / +0.02191 / +0.00711 (25/50/100/123/200/400); all 30 per-seed values equal the outcome to the printed 2 dp (e.g. seed 0: 1.78/1.95/2.40/2.84/2.52/1.00) | CONFIRMED (5th digit) | - |
| 5 | D_lo +0.00691, D_hi +0.01551, F-GS -0.00691 | own: +0.00691 / +0.01551 / -0.00691 | CONFIRMED | - |
| 6 | Two-stage SE 0.00429 (D_lo), 0.00459 (D_hi); lo -0.00151 / +0.00652 | own two-stage bootstrap (B 500, own rng 777: TRAIN items within stratum, every policy re-fitted; EVAL components within stratum; 5 seeds with replacement): SD 0.00432 / 0.00457 (gap < 1%); own lo = 0.00691 - 1.96 x 0.00432 = -0.00156 <= 0 | CONFIRMED (SE within 1%; word reproduces) | - |
| 7 | GS1 -> NOT-SHOWN; F-GS NOT FIRED | k* interior; D_lo point > 0 but lo <= 0 -> NOT-SHOWN (registered clause); F-GS point < 0 -> not fired | CONFIRMED | - |
| 8 | Support lines (C-2): DEFF 2.439 / 3.261, n_eff 2,422 / 1,811, MDE80 1.20 / 1.28pp (one), 1.38 / 1.47pp (joint) | (se2/se_iid)^2 from the printed 5-digit SEs: 2.434 / 3.266 (rounding); n_eff 2,427 / 1,809; 2.80 x SE 1.201 / 1.285pp; 3.21 x SE 1.377 / 1.473pp | CONFIRMED (rounding) | - |
| 9 | i.i.d. SE 0.00275 / 0.00254 | own item-i.i.d. SE of the seed-mean paired difference 0.00276 / 0.00257 | CONFIRMED | - |
| 10 | Predictions P1 5/5, P4 band, P5 2/2, P6 HELD; P2/P3/P4 Brier 0.32 / 0.0098 / 0.32 | bands recomputed from the outcome's points: all HELD. Brier: the outcome uses the TWO-CLASS sum; the record's convention (POSTRUN_construction_arms #7) is one-sided (p - o)^2 = 0.16 / 0.0049 / 0.16 | PARTLY (PR-4) | LOW |
| 11 | C-1 met (busy.ps1 rc 1 before launch; detached; nothing else reading the pool) | run_launch.log busy_rc=1, PID 76908; BUT GAP-FIX `gap_fix.py --run --part b` (PID 61508, created 17:12:38, a registered POOL READER) ran inside the window 17:01-18:33; busy.ps1's pattern list names neither granularity_sweep nor gap_fix | PARTLY (PR-1) | MEDIUM |
| 12 | Run report: "D_hi ... MDE80 one contrast +1.28pp (registered +1.47pp)" | outcome line 157 prints "(registered +1.74pp)" (code L804 prints SUPPORT["mde1"] for both D) | REFUTED (transcription) | LOW |

## Support as realised (C-2), beside the registration
| contrast | SE_2stage | DEFF (2-stage / i.i.d.) | DEFF (components only, policy fixed) | n_eff | MDE80 one / joint | observed (z) |
|---|---|---|---|---|---|---|
| D_lo | 0.429pp (reg 0.620) | 2.44 (reg 1.847) | 1.065 | 2,422 (reg 3,198) | 1.20 / 1.38pp (reg 1.74 / 1.99) | +0.69pp (1.61) |
| D_hi | 0.459pp (reg 0.620) | 3.26 (reg 1.847) | 0.989 | 1,811 (reg 3,198) | 1.28 / 1.47pp (reg 1.74 / 1.99) | +1.55pp (3.38) |
The realised SEs are 26-31% BELOW the registered 0.620pp: the higher "DEFF" sits on a smaller i.i.d. SE (nested cells of one fit have
low discordance), so the test was better powered than registered. Item clustering is negligible (Kish sum n^2/n 1.3115, mean component
size 1.093; one-stage component-clustered DEFF 1.065 / 0.989); the excess variance is the TRAIN-refit (policy-estimation) stage and the
seed term, not clustering (PR-2). Verdict line: DESCRIPTIVE-ONLY at the prediction stands (predicted +0.4pp < realised joint MDE80 1.38pp);
D_lo's observed +0.69pp is 0.51pp short of its own realised one-contrast MDE80. D-2 (seed variance x 0.8) only widens the interval:
the word is stable in the direction of that correction.

## Words of record (the registrar copies them)
- W-1 (deciding): "GS1 NOT-SHOWN. k* = 100 on GATE (interior; 0.10pp ahead of k 200 against a GATE SE of about 1.05pp: a noisy
  choice). On EVAL, D_lo = G_KW(100) - G_KW(25) = +0.69pp [-0.15, +1.53] (two-stage 95%; lower bound <= 0) and D_hi = G_KW(100) -
  G_KW(400) = +1.55pp [+0.65, +2.45]. An interior maximum of the routing gain in granularity is not shown at this support (rule 8:
  INTERIOR-MAX refuted at the planned n). F-GS not fired." Never "there is no best granularity", "granularity does not matter",
  "coarse cells route as well as fine ones", or "a peak at 100 cells".
- W-2 (D-4, binding): D_hi's lower bound > 0 is never read as "400 cells are over-split by granularity": G falls at 398 cells with
  TRAIN support median 26.5 items per cell and an overfit gap of +7.45pp in-sample vs +0.71pp EVAL; it is estimation noise as much as
  granularity. The percentile intervals of fine-k quantities are bias-shifted by the per-replicate re-fit (D_hi percentile
  [+1.61, +3.37] excludes its own point +1.55; G_KW(400) percentile [-1.82, +0.64] excludes +0.71; own bootstrap mean of D_hi +2.50pp):
  quote only the registered two-stage (Wald) interval (PR-3).
- W-3 (descriptive): the EVAL curve rises 25 -> 100/123 (+1.57 -> +2.26 / +2.33pp), is flat to 200 (+2.19pp) and falls at 398
  (+0.71pp); KF tracks KW (+1.70 / +2.08 / +2.25 / +1.97 / +0.71pp). BBH carries it: without BBH G_KW is +0.21..+0.60pp at k 25-200
  and D_lo +0.38pp [-0.57, +1.33]; MUSR's jump at 100 (+5.68 -> +13.10pp) rests on 3 cells. R2_int_KW peaks at 100 (+0.0573) and is
  lowest at 400 (+0.0484) (descriptive, no contrast interval). Support: EVAL share in cells with TRAIN >= 309 is 0.864 at 25 and
  0.027 at 398. TC - KW (-0.40pp at 100, -0.80pp [-1.70, +0.10] at 123) is shape- and count-confounded and filing-asymmetric (D-3), not
  a tree-vs-k-means quality comparison; G_KW(123) is not G_K (D-1).
- W-4: all arms [SC]; key-scored, no judge; one draw (5a3e756), one roster (18), one embedder (qwen3); content-closed
  pv2_1575de61bb20e977 under CK-CLOSE-v2 with the residual disclosed.

## Defects
- PR-1 (MEDIUM, process; no effect on the numbers): the C-1 "nothing else reads the pool in the window" was not met: GAP-FIX part b
  (PID 61508, started 17:12:38, still running at this review) overlapped the run (17:01-18:33). Both are read-only; no JVM or
  construction ran (busy.ps1 checks java); every pool/view read of this run is pinned with equal before/after sha256 (gen c2930c60,
  eval e35b7518) and the EVAL read began at 17:01 (marker). busy.ps1 is VACUOUS for the four 2026-10-06 readers: its pattern list
  (resp_profile_info|granularity_gt|site_support|tree_like|cell_strata|cell_difficulty|scale_agree) omits granularity_sweep, gap_fix,
  tree_backoff and gmm_fixedk. Fix: add those names to E:/TaxoArena_tmp/busy.ps1 (or match on any tools/analysis/*.py with --run);
  operators log the process list at launch. Disclosure: this review's own recomputes (about 90 s and 110 s, read-only) also ran
  while PID 61508 was alive; busy.ps1 returned 1 before each.
- PR-2 (LOW, words): the printed "DEFF" is Var_2stage / Var_iid (policy-refit + seed + clustering), not an item-clustering DEFF;
  the registered 1.847 was the same kind (ROUTE-SOURCE-NULL two-stage), so the comparison is like with like. Quote it as "two-stage
  variance ratio" with the component-only 1.07 / 0.99 beside it.
- PR-3 (LOW): bootstrap bias at fine k (W-2). Future G14-machinery registrations with fine-cell arms should pre-declare which
  interval form decides when percentile and Wald disagree.
- PR-4 (LOW): Brier convention: the outcome prints the two-class sum (0.32 / 0.0098 / 0.32); the record's one-sided values are
  0.16 / 0.0049 / 0.16. The registrar records the one-sided values and names the convention.
- PR-5 (LOW, run report): the hand-back misquotes D_hi's registered MDE80 as +1.47pp; the outcome prints +1.74pp.
- Carried: D-1, D-3, D-4 (W-2/W-3), D-2 (direction only widens), D-5 (realised SE below the registered one; D_hi's 398-cell refit did
  not inflate the SE beyond 0.62pp). No new mutants: blob unchanged since READY c963f646 (52/52 + R1-R8 8/8 there); the deciding
  numbers were instead re-derived by own code (claims 2-6).

## Commands (all read-only; zero calls)
```
git hash-object tools/analysis/granularity_sweep.py; git show --name-only --format= 000ae9cf | wc -l; git merge-base --is-ancestor df0f81bf HEAD
sha256sum experiment_results/archv2/granularity_sweep/granularity_sweep_outcome.txt; (cd E:/TaxoArena_backup_2026-10-06_granularity-sweep; sha256sum -c SHA256SUMS.txt)
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # rc 1 before each recompute
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/gspr/recompute.py
  # GS.prepare (loaders) + V.open_tw/read_key (keys, sha before = after) + CA.skm_best; own renorm, scipy Ward fcluster, filing, policy,
  # gains, k*, D, i.i.d. and component-clustered SE, Kish -> claims 1-5, 9; Support table column 4
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/gspr/boot.py   # own two-stage B 500 -> claim 6
ls -l data_v2/REG_ARCHV2-SPLIT-2_*/ *.db experiment_results/*.db before/after the recomputes: diff empty
powershell "Get-CimInstance Win32_Process -Filter 'ProcessId=61508'"   # gap_fix.py --run --part b, created 17:12:38 (PR-1)
python -c "<(se2/se_iid)^2, n_eff, 2.80 / 3.21 x SE, lo = pt - 1.96 SE, percentile midpoints vs points>"
```
Scripts and logs: E:/TaxoArena_tmp/gspr/{recompute.py,recompute.log,boot.py,boot.log} (not committed).

## Registrar duties
1. Outcome entry for GRANULARITY-SWEEP: GS1 NOT-SHOWN (D_lo lower bound), F-GS NOT FIRED, with W-1..W-4; outcome sha256 98902354...,
   backup E:/TaxoArena_backup_2026-10-06_granularity-sweep (5/5 OK); this review VALID.
2. Support as realised (the table above) beside the registered 1.847 / 3,198 / 1.74 / 1.99pp (C-2 closed).
3. Predictions: P1 5/5, P4 band, P5 2/2, P6 HELD; P2 / P3 / P4-direction Brier 0.16 / 0.0049 / 0.16 one-sided (two-class 0.32 /
   0.0098 / 0.32 as printed).
4. Bracket C-1 as PARTLY met (PR-1) and relay the busy.ps1 pattern fix to the orchestrator / run-operator.
5. Results JSON, INDEX, queue, ledger chip: NOT-SHOWN [SC], "an interior maximum is not shown at this support".
