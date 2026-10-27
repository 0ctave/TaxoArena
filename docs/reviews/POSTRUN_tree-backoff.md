# POST-RUN review: TREE-BACKOFF (adversarial; zero calls; read-only)

Reviewed: outcome `experiment_results/archv2/tree_backoff/outcome.txt` sha256
13c08450ebf9b9a57f98cfd4d2fb6819560c6cf89e2e244c608d267da8ea5be6 (= the backup copy; `sha256sum -c SHA256SUMS.txt` in
E:/TaxoArena_backup_2026-10-06_tree-backoff 6/6 OK). Script tools/analysis/tree_backoff.py blob:da80c57e927c6ebf8a1db9e2f0420c96c1514519
(LF, of record; `git hash-object` on the working tree and `git rev-parse HEAD:tools/analysis/tree_backoff.py` both da80c57e = READY
4eefac21's pin; merge 4303f24d touches 1 path, `git show --name-only --format= 4303f24d | wc -l` = 1). Registration prog L24814-L24826
with the registrar's brackets (READY record L24897ff). Pool pv2_1575de61bb20e977 (content-closed under CK-CLOSE-v2, residual
disclosed). Every arm [SC].

## VERDICT: VALID. BO1 = HIERARCHY-HELPS, as registered (D_B +0.00897, two-stage Wald lower bound +0.00033 > 0). MARGINAL.

The word follows the registered clause and reproduces under my own code. It stands only with the qualifiers W-1/W-2 below:
the lower bound clears 0 by 0.03pp, the registered Support under-stated the SE by 1.73x, the observed effect lies below its own
realised MDE80, and the word depends on a 1-item GATE margin in the tau choice (claim 6).

## Per-claim table (deciding claims)
| # | claim | reviewer's number | verdict | sev |
|---|---|---|---|---|
| 1 | Data object: EVAL 5,907 / 5,404 components; TRAIN 11,841; GATE 1,944; roster 18 | own key read (V.read_key, UNUSABLE_CELL, MATH-FIX overlay): 11,841 / 5,907 / 1,944 / 5,404 / 18; TRAIN and EVAL items without an AF cell 0 / 0; gen_view c2930c60 and eval_view e35b7518 sha before = after; `ls -l` of the view DBs identical before/after | CONFIRMED | - |
| 2 | AF-U hierarchy: 106 internal, depth 8 | own parse of the six members' last dag snapshots (+ IFEVAL one-cell under root): 229 nodes (the tool's 231 includes 2 pseudo-leaves that no scored item is filed to), 106 internal, max depth 8; every filed cell found | CONFIRMED | - |
| 3 | GATE counts and tau*(AF-U) = 100 | own back-off (top-down beta-binomial, p_root = TRAIN accuracy), own GATE scoring: 1228 1238 1238 1238 1238 1244 1244 1249 1248 1243 1237 -> 100 | CONFIRMED (every count) | - |
| 4 | TF 0.62011, TB 0.62908, D_B +0.00897, share changed 0.24733, BEST 0.60488 | own: 0.62011 / 0.62908 / +0.00897 / 0.24733 / 0.60488 (Qwen2.5-72B-Instruct) | CONFIRMED (5 dp) | - |
| 5 | SE_2stage 0.00441, lo +0.00033, percentile [-0.00020, +0.01680] | own two-stage bootstrap (TRAIN items within stratum, every node statistic and both policies re-fitted, EVAL components within stratum, tau held at 100): B 2,000 SD 0.00451 / 0.00435 / 0.00437 (rng 2026 / 7 / 11), B 500 0.00456; Wald lo +0.00013 / +0.00044 / +0.00041 / +0.00003; percentile lower bound -0.00085 / -0.00017 / -0.00068 / -0.00093 in every run; bootstrap mean +0.0077..+0.0079 (point +0.00897) | CONFIRMED (SE within 3%; Wald lo > 0 in 4/4; MC SD of lo at B 2,000 ~0.00014) | - |
| 6 | BO1 -> HIERARCHY-HELPS; rule 8 not refuted (lo > 0, tau* > 0) | registered deciding form = point +- 1.96 SE_2stage (run_boot / contrast, v2_declared_cells L736, carried): word follows. BUT EVAL D_B over the tau grid: +0.27 (1-10) / +0.47 (20) / +0.58 (50) / **+0.90 (100)** / +0.75 (200) / +0.64 (500) / +0.37pp (1000); tau 100 beats tau 200 on GATE by 1 item (1249 vs 1248); at tau 200 lo ~ +0.0075 - 1.96 x 0.0044 = -0.0012 (approximate, SE of tau 100) -> NEITHER | CONFIRMED, FRAGILE (PR-2) | MEDIUM |
| 7 | Support realised (C-2 duty): DEFF 2.208, n_eff 2,676, MDE80 +1.23pp | (0.00441/0.00297)^2 = 2.205 (rounding), 5,907/2.205 = 2,679, 2.80 x 0.441 = 1.235pp. Component-clustered DEFF (policy fixed) 0.985, Kish 1.3115: item clustering is nil; the excess is TRAIN-refit variance (refit-only SD 0.0034-0.0036) | CONFIRMED | - |
| 8 | C-3 duty: NO_XSRC count 191 = registered 191; D_B on NO_XSRC +0.00805 [-0.06, +1.67pp] | own: items whose AF cell member differs from the item's declared source (MMLU_PRO_LB = MMLU_PRO) 191; n 5,716, D_B +0.00805 | CONFIRMED (reconciled) | - |
| 9 | BBH contribution +0.00186 of +0.00897 (P5 FALSE); per source | own: +0.00186; NON_BBH +0.01002 (n 4,191); BBH +0.00641, MMLU_PRO +0.01333, MATH +0.00256, MUSR -0.01747, GPQA 0, IFEVAL 0 | CONFIRMED | - |
| 10 | F-BO NOT FIRED | BO1 is not HIERARCHY-HURTS | CONFIRMED | - |
| 11 | Predictions P1, P2, P4 (x2), P5 share, P6 band HELD; P5-BBH, P6-within FALSE; Brier 0.0225 / 1.3650 / 0.3025 / 0.3600 | bands HELD (P2 by 0.03pp: +0.897 <= +0.90). Binary Briers are one-sided (the record's convention); P3's 1.3650 is the three-class sum (one-sided on the observed class 0.7225) | CONFIRMED; convention named (PR-4) | LOW |
| 12 | Busy check rc 1 before dry-run and run | busy1.txt / busy2.txt are 0-byte files (no rc inside); busy.ps1 mtime 18:46:37 lies between busy1 (18:46:33) and busy2 (18:46:59): the dry-run check used the old pattern list (no tree_backoff/gap_fix), the run check the fixed one; no python/java reader alive at this review | PARTLY (PR-3) | LOW |

Descriptive only, NOT recomputed (taken from the outcome): D_TK +0.21pp [-0.57, +0.98], D_KB +0.24pp [-0.35, +0.83], D_B - D_KB
+0.66pp [-0.23, +1.54], K-WARD tau* 500/500/500/200/50, weak regions. They decide nothing; their words are C-1 (W-3).

## Support as realised (C-2 duty), beside the registration
| | SE_2stage | two-stage variance ratio | component-only DEFF | n_eff | MDE80 | observed (z) |
|---|---|---|---|---|---|---|
| registered | 0.255pp | 1.302 (ESCALATION-RC RC1, transported) | - | 4,537 | 0.71pp | pred. +0.30pp |
| realised | 0.441pp (own 0.435-0.456) | 2.205 | 0.985 | 2,679 | 1.23pp | +0.90pp (2.03) |
The transport failed by 1.73x in SE (2.9x in variance vs the i.i.d. 0.297pp): back-off changes 24.7% of picks (registered ~15%) and
its TRAIN re-fit variance exceeds escalation's. Verdict line DESCRIPTIVE-ONLY at the prediction stands (0.30 < 1.23pp); the observed
+0.90pp is 0.33pp short of its own realised MDE80: a result that clears the bar while below the MDE is expected to over-state the
effect (type-M); the bootstrap mean (+0.78pp) is already 0.12pp below the point.

## Words of record (the registrar copies them)
- W-1 (deciding): "BO1 HIERARCHY-HELPS, marginally. Empirical-Bayes back-off of AF-U leaf accuracies toward their ancestors
  (tau* = 100, chosen on GATE) routes EVAL +0.90pp better than AF-U's flat-leaf policy (two-stage 95% [+0.03pp, +1.76pp]; the
  percentile interval [-0.02, +1.68] reaches 0; realised SE 0.44pp against the registered 0.26pp; MDE80 1.23pp). F-BO not fired."
  Never "the hierarchy improves routing" unqualified, "a robust/clear gain", "+0.9pp from the hierarchy" without the interval, or
  "the tree's hierarchy beats k-means'".
- W-2 (fragility, binding): the sign of D_B is positive at every tau > 0 on the grid (+0.27..+0.90pp), but significance holds only at
  tau = 100, which beat tau = 200 by one GATE item; tau selection variance is not propagated (registered disclosure). The gain is
  carried by MMLU_PRO (+1.33pp [+0.11, +2.55]), not BBH (BBH +0.19pp of +0.90pp; P5 FALSE); MUSR -1.75pp (n 229); D_B without the
  191 cross-source filings +0.80pp [-0.06, +1.67] reaches 0.
- W-3 (C-1): D_TK and D_B - D_KB are shape-confounded (AF-U multiway, depth 8, 106 internal vs K-WARD binary, depth 10, 118
  internal; one common tau per arm) and filing-asymmetric (191 cross-source AF-U filings vs K_s by true source); not a comparison of
  hierarchy quality; descriptive.
- W-4: all arms [SC]; key-scored, no judge; one tree, one draw (5a3e756), one roster (18), one embedder (qwen3).
- Consequence (registered): the hierarchy enters the router-card policy as a CANDIDATE for a new registration only; a confirmation
  should register tau with selection propagated (GATE resampled) and Support built on this realised variance ratio 2.2.

## Defects
- PR-1 (MEDIUM, registration; carried C-2): DEFF transport from ESCALATION-RC under-stated the SE 1.73x. Fix: future back-off /
  policy-modification registrations take the variance ratio 2.2 measured here, or measure it on a TRAIN-only pilot.
- PR-2 (MEDIUM, words): the word rests on a 1-item GATE margin in tau (claim 6). Fix: W-2 is mandatory beside every quote of BO1.
- PR-3 (LOW, process): busy evidence files are empty, and the first check ran on the pre-fix busy.ps1. Fix: operators write the rc
  and the matched process list into busyN.txt (`... ; echo rc=$?`).
- PR-4 (LOW): P3's Brier 1.3650 is the three-class sum; name the convention (one-sided on the observed class 0.7225).
- No new mutants: blob unchanged since READY 4eefac21 (64/64 + R1-R8 there); the deciding numbers were re-derived by own code.

## Commands (all read-only; zero calls)
```
git hash-object tools/analysis/tree_backoff.py; git rev-parse HEAD:tools/analysis/tree_backoff.py; git show --name-only --format= 4303f24d | wc -l
sha256sum experiment_results/archv2/tree_backoff/outcome.txt; (cd E:/TaxoArena_backup_2026-10-06_tree-backoff; sha256sum -c SHA256SUMS.txt)
powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1   # rc 1 before each recompute; Get-CimInstance: no python/java reader
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/tbpr/recompute.py          # claims 1-5, 7 (B 500)
BOOT_B=2000 BOOT_SEED={2026,7,11} python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/tbpr/recompute.py  # claim 5
python tools/analysis/scratch_dir.py --run -- python E:/TaxoArena_tmp/tbpr/extras.py / extras2.py  # claims 6, 8, 9; McNemar 182 vs 129 p 0.0031 (policy fixed)
ls -l --time-style=full-iso data_v2/REG_ARCHV2-SPLIT-2_*/*.db before/after: diff empty
ls -l --time-style=full-iso E:/TaxoArena_tmp/busy.ps1 E:/TaxoArena_backup_2026-10-06_tree-backoff/   # PR-3
```
Reused for loading only: TB.prepare (AF cells, GATE items + modal AF cell), V.open_tw / read_key. Own: hierarchy, back-off, tau,
policies, D_B, SEs, bootstrap, subsets. Scripts and logs: E:/TaxoArena_tmp/tbpr/ (not committed).

## Registrar duties
1. Outcome entry: BO1 HIERARCHY-HELPS (marginal) with W-1..W-4; F-BO NOT FIRED; outcome sha256 13c08450...; backup 6/6 OK; this review VALID.
2. Support as realised (table) beside 1.302 / 4,537 / 0.255pp / 0.71pp (C-2 closed); C-3 closed (191 = 191); C-1 words W-3.
3. Predictions: P1, P2, P4 x2, P5-share, P6-band HELD; P5-BBH FALSE (0.3025), P6-within FALSE (0.36), P1 0.0225, P3 1.365 (three-class; 0.7225 one-sided).
4. Results JSON, INDEX, queue, ledger chip: "HIERARCHY-HELPS (marginal) [SC]", never an unqualified "hierarchy helps".
5. Relay PR-1 (Support transport) and PR-3 (busy evidence) to the orchestrator / run-operator.
