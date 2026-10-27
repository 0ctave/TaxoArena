# POST-RUN review: GMM-FIXEDK (adversarial; zero calls; read-only)

Reviewed: outcome `gmm_fixedk_outcome.txt` sha256 a89fb861cd8153898fc4d0b9b453ce8d598e6890a00c7eabd536c0e2f92803cf (identical in
E:/TaxoArena_backup_2026-10-06_gmm-fixedk and E:/TaxoArena_backup_2026-10-06_gmm_fixedk); script tools/analysis/gmm_fixedk.py
blob:fdca150f71caa49542a7389b2647eceab0a4bc39 (LF, of record; = READY 215b551f's pin; working tree and HEAD 0ebc0fe1 both hash to it).
Registration prog L24856-L24868 with brackets (registrar 81d9e385). Label status [LF] (fine / coarse gold labels of MASSIVE and CLINC).

## VERDICT: VALID (C-GK NO-GMM-WINS, as registered; not parity; no TOST)

Conditions: the words W-1..W-4 below; Support as realised (PR-1 table) printed beside the registered 0.076.

## Per-claim table (deciding claims)
| # | claim | reviewer's number | verdict | sev |
|---|---|---|---|---|
| 1 | Per-seed readouts of the two deciding arms (40 values: DIAG/FULL x MASSIVE/CLINC x (a)/(c) x 5 seeds) | own re-fit with own best-first, own k=2 GMM node rules (sklearn, seeds s*1000003+17c+2, PCA full unwhitened, reg 1e-4 / 1e-6, n_init 3, max_iter 200), own centroid filing, own plurality majority and own (c) scorer: all 40 agree to the 5th digit (e.g. FULL clinc (c) 0.87170/0.87155/0.85267/0.84817/0.85746); L 84 / 139 reached; 0 replaced splits | CONFIRMED (to the digit) | - |
| 2 | D_jr and spread_1r (8 cells) | recomputed from the per-seed lines: DIAG a -0.00884/-0.00593, c -0.00364/-0.04550; FULL a +0.01564/+0.00910, c +0.02451/+0.02080 (MASSIVE/CLINC); spreads 0.04305/0.06048 (a), 0.10796/0.02324 (c) (5th-digit rounding of printed seeds; script 0.10797/0.02323 = GK-I0 record) | CONFIRMED | - |
| 3 | C-GK NO-GMM-WINS | every one of the 8 cells has D <= spread_1r, so every (j, r) fails on BOTH corpora by the point alone; the lower bounds cannot change the word. Smallest margin: FULL (c) CLINC -0.00244 (D 0.02080 vs 0.02323); every pair also fails on MASSIVE by >= 0.027 | CONFIRMED | - |
| 4 | GK-I0 and I1-I3 REPRODUCED (R-C3) | arm-1 means/ranges equal the registered constants; corroborated independently by claim 1 (same loader, own fits match) | CONFIRMED | - |
| 5 | PR-3: 8 re-print points read "point REPRODUCED" | 8/8 equal the CONSTRUCTION-ARMS outcome (E:/TaxoArena_backup_2026-10-05_construction_arms, `^D ` lines): -0.03802, +0.01290, +0.00423, -0.00142, +0.00056, -0.02119, +0.01667, -0.14832 | CONFIRMED | - |
| 6 | PR-2: item-only SD > 0 everywhere | 0.00441, 0.00220, 0.00313, 0.00375, 0.00504, 0.00235, 0.00307, 0.00284 (8/8 > 0); D-1's R1 risk did not materialise | CONFIRMED | - |
| 7 | PR-1: DEFF / n_eff / MDE80 | DEFF = Kish x (SE/SE_item)^2 recomputed for 8 cells: 8.82 / 21.96 / 39.82 / 3.94 / 3.68 / 31.79 / 40.47 / 5.82 (printed 8.82 / 21.94 / 39.89 / 3.94 / 3.68 / 31.75 / 40.47 / 5.80; gaps are 5-digit rounding); n_eff within 4 of printed; MDE80 = spread + 0.84 / 1.25 x SE(D) reproduces 0.0540 / 0.0594 etc. | CONFIRMED (see W-3 for the seed-corrected figure) | LOW |
| 8 | Predictions P1/P2 8/8 HELD, P3 Brier 0.0025, P4 TRUE, P5 TRUE, P6 FALSE | recomputed: all 8 D in their bands; P6 FULL-minus-BISECT-SKM (c) +0.01161 / +0.04200 (CLINC outside [-0.03, +0.03]) | CONFIRMED (the operator's "did not read P2" is closed: P2 4/4 HELD) | - |
| 9 | No DB write, zero calls | intent-s1-run DB mtimes/sizes identical before/after my re-fit (`diff` empty); pins OK lines; outcome prints 0 calls; `git status -uno` shows only the two pre-existing tracked changes | CONFIRMED | - |
| 10 | R-C1 busy.ps1 exit 1 before --run; "and before the dry run" | run.log has exactly 1 busy line (`grep -c busy` = 1), busy_rc=1, between the dry run and --run. The pre-dry-run check is not evidenced in the log | PARTLY (R-C1 met; the extra claim unsupported) | LOW |
| 11 | Bootstrap intervals (lo/hi) | NOT recomputed (non-deciding here: claim 3 shows the word is fixed by the points); spot check only of form | UNDETERMINED (non-deciding) | - |

## Support as realised (PR-1), beside the registration
| pair | realised joint MDE80, SE(D) as registered (d) | with the seed-corrected SE (D-4) | registered |
|---|---|---|---|
| DIAG (a) | 0.0734 (CLINC binds) | 0.0748 | 0.076 |
| FULL (a) | 0.0770 (CLINC binds) | 0.0789 | 0.076 |
| DIAG (c) | 0.1325 (MASSIVE binds) | 0.1353 | 0.130 |
| FULL (c) | 0.1323 (MASSIVE binds) | 0.1350 | 0.130 |
Realised DEFF_total 3.68-40.47; the maximum (FULL (c) MASSIVE 40.47, n_eff 122) is carried by the SEED term (arm 1's seed 2 at 0.686;
Kish 1.0093), not by item clustering. Largest realised |D| 0.0455 (DIAG (c) CLINC, negative); largest positive D 0.0245, below every MDE.
The verdict line DESCRIPTIVE-ONLY stands.

## Words of record (the registrar copies them; overstatements to avoid)
- W-1 (MEDIUM): "BISECT-GMM-FULL (c) on CLINC led arm 1 by +0.021 [+0.007, +0.034] and cleared the interval conjunct, but fell 0.002
  short of arm 1's seed range 0.023; on MASSIVE (c) it was +0.025 against a 0.108 bar that one arm-1 seed carries (structurally
  unreachable, Support (g))." Never "full-covariance GMM beats the engine-like arm on CLINC", never "no GMM rule helps".
- W-2 (MEDIUM): the FULL-minus-BISECT-SKM leads ((c) +0.012 [+0.003, +0.020] MASSIVE, +0.042 [+0.030, +0.054] CLINC; (a) MASSIVE +0.054)
  are DESCRIPTIVE (never in C-GK; no multiplicity control; percentile interval anti-conservative on the seed axis, D-4); P6 FALSE.
  Write "descriptively ahead of spherical bisection at the same binary shape", never "the mixture's covariance boundary is better".
- W-3 (LOW): Support as realised = the table above; quote the realised (a) pair MDE80 as 0.073 / 0.077 with 0.075 / 0.079 seed-corrected,
  and the (c) pair as 0.132 / 0.135; DEFF up to 40.5 is a seed-driven design effect.
- W-4 (LOW): DIAG ARM-1-AHEAD on CLINC (c) (D -0.046 [-0.060, -0.032]), OOS AUROC FULL +0.004, and the C leg (FULL DP 0.43-0.44 vs
  arm 1 0.39-0.40; in-sample; id-disjoint scope) are descriptive; arm 1 = ENGINE-LIKE SKM, NOT the engine, differences (i)-(vi).
- Consequence (registered): NO-GMM-WINS -> no GMM engine arm is indicated by these approximations; not parity.

## Defects
- P-1 (LOW, record): the outcome sits in two folders (script default `..._gmm_fixedk`, brief's `..._gmm-fixedk`), same sha256; the
  registrar names one as of record (suggest the script's own, whose SHA256SUMS the script wrote) and lists the other as a copy.
- P-2 (LOW, operator log): the pre-dry-run busy check claimed in the hand-back is not in run.log; R-C1 (before --run) is evidenced.
  Fix: log every busy.ps1 rc in the run log.
- P-3 (LOW, cosmetic, carried D-3): outcome line 24 reads "GK-R1..GK-R6"; GK-R7 is the registrar's bracket (never binds at d 256;
  FULL p min 15/17/5 on CLINC/MASSIVE/C comes from floor(n/10), not from GK-R7).
- No new mutants: the blob is unchanged since READY 215b551f (68/68 + R2-R6 killed there); the deciding numbers were instead
  re-derived by independent code (claim 1).

## Commands
```
sha256sum E:/TaxoArena_backup_2026-10-06_gmm-fixedk/gmm_fixedk_outcome.txt E:/TaxoArena_backup_2026-10-06_gmm_fixedk/*  # a89fb861... both
git hash-object tools/analysis/gmm_fixedk.py; git show HEAD:tools/analysis/gmm_fixedk.py | git hash-object --stdin       # fdca150f both
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1                                                                   # exit 1
ls -l --time-style=full-iso .claude/worktrees/intent-s1-run/*.db > before; <re-fit>; ls ... | diff - before             # empty
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/gk_post/indep.py 20   # own re-fit, 20 fits, rc 0 (claim 1)
python E:/TaxoArena_tmp/gk_post/arith.py      # D, spread, C-GK by points, bands, P6, DEFF/n_eff/MDE (claims 2,3,7,8; W-3 table)
grep '^D ' E:/TaxoArena_backup_2026-10-05_construction_arms/construction_arms_outcome.txt   # PR-3 record points
grep -c busy E:/TaxoArena_tmp/gmm-fixedk_run/run.log                                        # 1 (claim 10)
```
Scripts/logs (not committed): E:/TaxoArena_tmp/gk_post/indep.py, indep.log, arith.py, db_before.txt.

## Registrar duties
Outcome section `## GMM-FIXEDK (2026-10-06, 0 calls) — VALID (POSTRUN <this commit>): C-GK NO-GMM-WINS ...`; [OUTCOME] brackets on
READOUTS AND CRITERIA (W-1, W-2, W-4) and SUPPORT (W-3 realised table); P1-P6 scored (P1/P2 8/8 HELD; P3 Brier 0.0025; P4 TRUE 0.0625;
P5 TRUE 0.0400; P6 FALSE 0.3600); outcome pin a89fb861 and the backup folder of record (P-1); results JSON GMM-FIXEDK state done,
INDEX, queue item, ledger section-7 chip (null class, "NO-GMM-WINS; not parity").
