# POSTRUN review: MMLU-GAP-ROSTER (cause 3, strong / near-ceiling HELM roster; EXPLORATORY, WORK rows only)

Authority: D-2026-10-22-1 (`docs/agents/author_decisions/2026-10-22.md`). Reviewer: adversarial reviewer, 2026-10-22.
Zero LLM calls. No vault or reserved response read: my MMLU loads asserted `guard.reads` helm 0 / tinyb 0 / math 0;
MATH through `granularity_work.load_real` (reads 0). Reviewed: benchzoom branch `gap-roster` (local, no remote),
6f8d204..c93f3b8 on master dfeb0aa. Run of record = 77c3c9a, script LF blob `93fa852a` (`meta.json` dirty ""); CF
secondary = f71e0b6, blob `4b924d0f`; tip blob `565362ab` (working tree is LF; `git hash-object` = the committed blob,
no CRLF rendering differs). From 77c3c9a to the tip, only `analyse_cf`, `cf_text`, `run_cf`, `main` and `selftest` change
(AST hash of every top-level definition): the primary path is unchanged. Outputs: `E:/benchzoom_demo/mmlu_gap_work/roster`
(summary.txt sha256 26963e6f…; summary_cf.txt aff8348e…).

## Verdict

**CONFIRMED (exploratory), with one MEDIUM finding on the reading (D1) and one MEDIUM test gap that is decisive (D2).**
- Every deciding number reproduces to at most 1.4e-17 from my own wiring. That wiring is the FULL `meter.chain` record
  path (`M._restep` for tau², `pseudo_cdata` draw 0, `fixed_reader`), not the builder's slim `l2_contexts`, with my own
  subsets, matching, aggregation, cluster SE and Spearman.
- MATH full / weak / strong / matched reproduce to at most 2.8e-17 with the RAW `fit_theta_slope` and my own
  re-implemented folds (equal to the record's on 5/5 seeds), so the fallback count is 0 on every subset.
- The plan preceded every statistic, the word follows the pre-specified rule, and hygiene is clean.

**My cause verdict: MIXED by the rule as printed (reproduced); NOT SUPPORTED in substance.**
- The one arm that fires, B-matched, is vacuous. The UNMATCHED full roster passes the same bound: +0.0765 ≥ +0.0236
  (E-MMLU), and +0.0575 ≥ +0.0406 on MATH's estimator. B-matched therefore certifies that the WORK gap is not
  established (z −0.95), not that matching closes it (D1).
- A has the wrong sign: ρ +0.123, one-sided negative p 0.85.
- The premise is false: MATH is the near-ceiling roster (median 0.985, 47/69 above 0.95; MMLU 0/79 above 0.9).
- Like for like at the same accuracy, MATH's gain exceeds MMLU's by +0.352 SE 0.138 (z +2.55; same estimator +0.341
  SE 0.135). With the like-for-like comparator the rule itself prints NOT SUPPORTED (OM2).

## Per-claim table (deciding claims; units 1e-3 nats per cell)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 6f8d204 committed before any statistic; [P1] pre-data | Plan 12:15:08; [P1] 12:25:49; run commit 77c3c9a 12:46:04; run start ≈12:46:11 (13:24:46 − 2,315 s). Files under `mmlu_gap_work` newer than 12:00 and older than 12:46:04: 3, all `baseline/` (the cause-1 agent's math_hx, 12:32:52). The deciding functions (`verdict`, `match`, `halves`, `perm_spearman`, `diff_stat`, `per_model`, `Fit`) are AST-identical from d1d2898 (pre-data) to the tip. Plan diff: 2 inserted brackets, 0 deleted lines | CONFIRMED | - |
| 2 | E-MMLU reproduces C-M1 WORK +0.076489 SE 0.036066, n 3,342, tau² 0.02 | Own full chain: +0.0764891961 / 0.0360662673 (gap 0 / 6.9e-18), tau² 0.02, 3,333 clusters. `support_recut.json` draw 0 read here: 0.07648919607361708 / 0.036066267266545 | CONFIRMED | - |
| 3 | E-MATH reproduces +0.124052 SE 0.034974 (estimator = GRANULARITY-WORK) | `controls.csv` L3a\|L2 0.124052 / 0.0349738 read here. Builder 0.1240519375 (\|dg\| 6.3e-8 = 6-dp rounding). Own full recompute: +0.1240519375 / 0.0349738318 (gap 2.8e-17 / 0), raw `fit_theta_slope`. Same harness as the record (folds `[20261021, s]`, 5 × 5, clusters 2,946) | CONFIRMED | - |
| 4 | Profiles: MMLU median 0.758, 29% > 0.8, 0 > 0.9; MATH median 0.985, 47/69 > 0.95 | Own quantiles equal to 3 dp (MMLU 0.281/0.586/0.678/0.758/0.806/0.843/0.877; MATH 0.329/…/0.995; 47 > 0.95). Info terms not recomputed (descriptive) | CONFIRMED (spot) | - |
| 5 | A: Spearman +0.1235, two-sided perm p 0.2858 → fails | Per-model g_j max gap 0. ρ +0.123480. p on the builder's stream 0.2858; independent 100k stream 0.2770; asymptotic 0.2783 | CONFIRMED | - |
| 6 | B-halves: weak +0.0492 (0.0282, 39), strong +0.0034 (0.0191, 40), diff +0.0458 SE 0.0320 → fails | Own median 0.7584569733, 39/40. Own: +0.0492445742 / 0.0282466599; +0.0034187961 / 0.0190552864; paired diff +0.0458257780 / 0.0320358836 (gaps ≤ 1.4e-17); tau² 0.01 / 0.01; z +1.43 | CONFIRMED | - |
| 7 | B-matched: 16 pairs, KS 0.188; matched +0.0417 SE 0.0450 ≥ bound +0.0101 → holds | My matching (transposed LSA, cost 1e3 beyond the caliper) selects the same 16 MMLU and 16 MATH models. A 1-D greedy gives maximum cardinality 16. KS 0.1875. Own +0.0417033644 / 0.0449654136; bound +0.010121 | CONFIRMED (value); VACUOUS (D1) | MEDIUM |
| 8 | MATH (secondary): weak +0.232 (0.071), strong −0.004 (0.004), diff +0.236 (0.071); matched +0.394 SE 0.130 | Own: +0.2318183552 / 0.0711078924; −0.0038409787 / 0.0041153279; +0.2356593340 / 0.0712477625; +0.3939575294 / 0.1304316696 (gaps ≤ 2.8e-17) | CONFIRMED | - |
| 9 | Word MIXED by the pre-specified rule | Own rule on own numbers: A no, B-halves no, B-matched yes → MIXED. Forking: E-MMLU-CF gives MIXED too (ρ +0.107, diff +0.017 SE 0.025, matched +0.053 ≥ +0.026). Draws 1-4: matched g 0.028-0.121, all above a bound of about 0.01; weak−strong max 0.058 < about 0.064. Approximate, since the per-draw SEs are not stored. The word is the same on every path, and on every path it is carried by the vacuous arm | CONFIRMED | - |
| 10 | "B-matched passed only because its SE is wide"; "MATH gains about 7 to 9 times more at the same accuracy" | Imprecision is half the story: the unmatched roster also passes (D1). Ratios 9.45 and 7.45 are right, but have no interval, and the denominator's 95% CI includes 0 (D4) | PARTLY | MEDIUM |
| 11 | Bins: MMLU Q1-Q4 +0.077/+0.061/+0.039/+0.133; MATH Q1 +0.503 (0.131), Q2-Q4 about 0 | MMLU 4/4 bins equal to 4 dp. MATH: per-model g_j max gap 4.4e-16, ρ −0.107665 (equal), bins +0.5028 (0.1306) / −0.0307 / +0.0009 / +0.0009 (equal) | CONFIRMED | - |
| 12 | Selftest 55 checks; 30/30 mutants killed; ruff; sync test 33 | Unmutated sandbox copy: 55 PASS, exit 0. ruff "All checks passed!". `test_execution_graph_sync` 33 passed. Branch touches 2 paths, 0 under `src/` or `execution_graph`. Own mutants: OM2 survives and is decisive (D2) | PARTLY | MEDIUM |
| 13 | Seal 0 on every guard; ≤ 3 processes; read-only dirs; backup 13 files | `meta.json` reads 0 × 4; `run_cf` reads 0 × 3. `Engine` caps workers at 3 and `run` refuses more; primary and CF did not overlap (CF start ≈13:27:31). Files newer than 12:00: `mmlu_confirm` 0 (its 11:04-11:09 files are the vault read of record), `benchzoom_cache` 0. `mmlu_pro_more`: 36 newer files, 0 named `*roster*`; the script names `mmlu_confirm` only in a label string (L118). SHA256SUMS 5/5 + logs 2/2 + cf 3/3 OK. Backup `SHA256SUMS_backup` 13/13 OK, full-tree sha256 listing equal to the source | CONFIRMED | - |

**Support** (re-measured from pseudo draw 0's own clusters; all SEs are item-clustered with the roster fixed):

| Statistic | n / clusters | DEFF | n_eff |
|---|---|---|---|
| full | 3,342 / 3,333 | 1.002 | 3,334 |
| weak | 3,342 / 3,333 | 1.001 | 3,338 |
| strong | 3,342 / 3,333 | 1.006 | 3,323 |
| matched | 3,342 / 3,333 | 1.000 | 3,341 |
| weak − strong | 3,342 / 3,333 | 1.003 | 3,333 |

MDEs:
- B-halves at its own bar: MDE80 = (2 + 0.84) × 0.0320 = **0.091**, which is above the whole full-roster MMLU gain
  (0.0765).
- B-matched contrast: SE 0.0570, MDE80 **0.160**, which is above MATH's whole gain (0.124).

## Defects

- **D1 MEDIUM: B-matched is vacuous, and the comparator that carries the vote is not like for like.**
  - Count check: the unmatched full roster passes the same bound, on both estimators (row 9 / Verdict).
  - P(pass | true matched gain 0) = 0.41.
  - The MDE80 of the contrast (0.160) exceeds MATH's whole gain.
  - The matched set covers only MATH's weak tail (16 of 69 MATH models lie inside MMLU's range; matched median 0.64 vs
    MATH's roster median 0.985). Yet the vote compares that set with MATH's FULL-roster gain.
  - The like-for-like comparison (MATH on the same 16-model accuracy band, +0.394) was "secondary, no vote", and points
    the other way.
  - The design came from the spec ("within 2 SE"); the builder disclosed the imprecision ([P2]).
  - Fix: state the result as "MIXED by the rule; B-matched VACUOUS (the full-roster control passes); NOT SUPPORTED in
    substance". In any re-use: run the full-roster control through every equivalence arm, and compare matched with
    matched.
- **D2 MEDIUM: the `analyse` → `verdict` wiring of g_MATH has no value check, and a mutant that changes it flips the real
  word.**
  - OM2 feeds MATH's matched gain into the bound instead of the full-roster gain. It SURVIVES (55/55 PASS).
  - On the real numbers that bound is 0.394 − 2·hypot(0.045, 0.130) = +0.119 > +0.042, so B-matched fails and the word
    turns MIXED → NOT SUPPORTED.
  - The run of record is wired correctly (my bound +0.010121 uses the full MATH fit).
  - Fix: a selftest assert that `r["verdict"]["matched_bound"]` equals g_full_MATH − 2·hypot(SE_m, SE_full_MATH) on the
    fixture.
- **D3 LOW: the paired SE of weak − strong has no value check** (OM1 survives).
  - The unpaired SE would be 0.0341 against the paired 0.0320; the word is unchanged here.
  - Fix: a fixture assert against a hand-computed paired cluster SE.
- **D4 LOW: "7 to 9 times" is a point ratio.**
  - The denominator's 95% CI includes 0 (0.042 ± 0.088), so the ratio is unbounded above.
  - It also crosses datasets whose leaf-gain scales differ (POSTRUN_MMLU-GAP-BASELINE D2).
  - Fix: quote the difference instead, +0.352 SE 0.138, or on the same estimator +0.341 SE 0.135.
- **D5 LOW: the SEs are roster-conditional.**
  - The per-model g_j spread (SD 0.334 against an RMS per-model SE of 0.234) implies a true between-model SD of about
    0.24.
  - Treating models as sampled would add about 0.054 to the SE of the halves difference.
  - This only widens the intervals; no word changes. Fix: label the halves and matched SEs "roster-fixed".
- **D6 LOW: the plan had no Support section.** B-halves could not detect a weak − strong gap as large as the whole MMLU
  gain (MDE 0.091 > 0.0765). This is exploratory, so it is noted, not blocking. Fix: print the MDE beside each arm.
- **COSMETIC:**
  - "MMLU's weaker models carry little gain": the MMLU quartile gains are flat (Q1 +0.077 ≈ the full roster; Q4 is the
    highest).
  - The summary's "runtime 2247 s" is the `analyse` time; `meta.json` has 2,315 s for the whole run.

## Own mutants (deciding paths; sandbox copies under `E:/TaxoArena_tmp/rev_gap_roster/mut/`, `--selftest`, TMP/TEMP/TMPDIR redirected, pool 1)

| id | change (one line) | result | decisive |
|---|---|---|---|
| OM0 | control (unmutated copy, blob 565362ab) | 55 PASS / 0 FAIL, exit 0 | - |
| OM1 | `diff_stat`: SE = hypot of the two unpaired SEs | SURVIVED (55/55 PASS) | no (0.0341 vs 0.0320; B-halves still fails) |
| OM2 | `analyse`: B-matched bound uses MATH's matched fit instead of the full fit | SURVIVED (55/55 PASS) | **yes** (real word MIXED → NOT SUPPORTED) |
| OM3 | `analyse`: halves frozen on pseudo draw 0's fit rows instead of the full WORK rows | KILLED (2 FAIL: tau² check; analyse_cf == analyse) | - |

## Commands (read-only on outputs and caches; at most 3 of my processes at any time, BLAS 1; scripts in the reviewer's scratchpad, outputs under `E:/TaxoArena_tmp/rev_gap_roster/`)

```
git -C <wt> log --format='%h %ad | %cd' --date=iso master..HEAD ; git log --format= --name-only master..HEAD | sort -u | wc -l  -> 2 (grep -c '^src/\|execution_graph' -> 0)
git diff 6f8d204 c93f3b8 -- docs/mmlu_gap_roster.md | grep -c '^-[^-]'  -> 0 ; AST hash of top-level defs at d1d2898 / 77c3c9a / f71e0b6 / c93f3b8
find E:/benchzoom_demo/mmlu_gap_work -newermt '2026-10-22 12:00' ! -newermt '2026-10-22 12:46:04' | wc -l  -> 3 (baseline/ only)
find E:/benchzoom_demo/mmlu_confirm -newermt '2026-10-22 12:00' | wc -l -> 0 ; E:/benchzoom_cache -newermt 11:00 -> 0 (both also after my runs)
python rev_roster_mmlu.py full|weak|strong|matched   own subsets + own matching, M.chain (full) + M._restep + pseudo_cdata(.,0) + fixed_reader -> per-cell D
python rev_roster_math.py <subset> 0 1 2 3 4         own folds (== gw.group_folds 5/5), M.backbone/M.contexts/M.step, raw fit_theta_slope
python -I rev_roster_agg.py [math support]           own cluster SE, per-model g_j, Spearman + perms (builder stream and an independent 100k stream), bins, bounds, DEFF, MDE
sh mut/run1.sh OM0..OM3 ; sha256sum -c SHA256SUMS / SHA256SUMS_logs / cf_mmlu/SHA256SUMS / SHA256SUMS_backup (13/13) ; tree listing diff -> equal
ruff check examples/mmlu_gap_roster.py (clean) ; pytest tests/test_execution_graph_sync.py (33 passed) ; git status --porcelain | wc -l -> 0
```
