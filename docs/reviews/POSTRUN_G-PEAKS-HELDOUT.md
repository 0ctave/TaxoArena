# POSTRUN G-PEAKS-HELDOUT (adversarial post-run review; zero LLM calls; nothing written under E:/benchzoom_demo)

Reviewed: benchzoom master `9e3937f` (registration `docs/peaks_registration.md` LF blob fc15b09e at f6f344a = HEAD = working tree;
`peaks.py` a062f093, `examples/peaks_test.py` 8ee53c63; the 8 library blobs equal to registration §1; LF = working tree, no CRLF
difference). Outputs `E:/benchzoom_demo/peaks_v1/` (meta.json pins the same 11 blobs and 6 data sha256; SHA256SUMS 7/7 OK).
Authority: author decisions D-2026-10-11-3/-5/-6. Pre-data review: READY_G-PEAKS-REGISTRATION (CHANGES, E1-E9).

## Verdict: VALID (with conditions C1-C5). The verdict words are applied mechanically and reproduce:
**MATH: NO POCKETS** (P1 HELD) and **MMLU-Pro: NOT INTERPRETABLE (support)** (P2 FAILED; P3 FAILED, P4 FAILED by the letter of
[R12]; falsifier NOT FALSIFIED). Neither dataset says anything about pockets as capability nodes: the method could not have
detected them here (N2 6-7%, and N4 cannot pass at ANY effect size on these data, C1).

Plain-language summary of what the pockets show. The pocket finder found almost nothing. In MATH it found no pocket in any leaf.
In MMLU-Pro it found one dense group: the 84 questions that came from MMLU's old econometrics subject, inside the economics
leaf (named after that source subject). That group is borderline: with my own random subsamples it fails the stability rule
(one grid cell matched 3 of 10, the floor is 4). On the training folds, pockets appeared in only 2 leaves, once each, which is
far too little to test whether pockets help predict how models score (782 support pairs against a floor of 10,000). The
calibration shows why: when a pocket is planted on purpose, the finder recovers it 6-7% of the time. So "no pockets" here
means "this method cannot see them", not "the leaves have no internal concentrations". The useful outcome is the method
diagnosis (single dense groups in a diffuse leaf are not returned; the per-cell floor is fragile), for a new registration.

## Per-claim table (deciding claims)

| # | claim | my number (command) | status | sev |
|---|---|---|---|---|
| 1 | Registration precedes outputs | 73f41a8 05:49, [R1]-[R12] 49d326e 06:24, [R13] f6f344a 07:03, code 9e3937f 07:23; run of record work/ 07:26, stage1 07:42, stage2 07:43, stage3 08:10 (A). BUT an undisclosed real-data pilot ran at 06:37-06:42 (C2) | CONFIRMED with C2 | MEDIUM |
| 2 | Pins (reg, peaks, runner, 8 lib, 6 data) | all equal; `git diff --name-only 9a08f54 HEAD -- src` = 1 line (peaks.py, new) (A) | CONFIRMED | - |
| 3 | N1 G/E/C 0/220 (MATH), 0/360 (MMLU-Pro); Wilson upper 0.0172 / 0.0106 | Wilson 3.8415/223.84 = 0.01716, 3.8415/363.84 = 0.01056. Own generators + own pipeline + own seeds, 3 leaves/dataset x 3 families x 3 draws: **0/54 fire** (B) | CONFIRMED | - |
| 4 | N2 7/110 = 0.0636, 13/190 = 0.0684: FAIL | own seeds, own Gaussian background, 0.05 n at 0.05 Sigma: MATH 0/15, MMLU-Pro 1/15; 0.10 n: 4/15, 4/15 (B) | CONFIRMED (FAIL) | - |
| 5 | N2 fails "by construction" because allow_single_cluster=False returns a lone dense cluster as noise | single reference run with allow_single_cluster=True recovers only 4/15 and 3/15 at 0.05 n (B): the flag is one cause, not the cause (plant size = mcs; plant at mcs of the 80% subsamples ~half the time) | PARTLY | LOW |
| 6 | N3 0/64 PASS; N4 0/32 FAIL | all 320 sims recorded with the exact shortcut: MATH 160x NO POCKETS, MMLU-Pro 160x NOT INTERPRETABLE (support) (C). Pockets are text-only and identical across sims, so N3/N4 are fixed before any answer is read: N3 PASS is vacuous, N4 is unreachable at infinite E | CONFIRMED; N3 VACUOUS, N4 IMPOSSIBLE (C1) | HIGH |
| 7 | Leaves pocketed any fold / >=3 of 5: MATH 0/0, MMLU-Pro 2/0 | from the work pickles: 0/0 and 2/0 (leaf 3 fold 3, 74 items; leaf 5 fold 4, 73) (D). Own seeds: 0/0 and 2/0 (leaf 3 folds 1,3; leaf 5 fold 4) (B). Alt folds: 0.95-groups 0 leaves, ungrouped 2 (D) | CONFIRMED | - |
| 8 | Support pairs 782 (floor 10,000) | 782 of 8,993 from the pickles (D); own seeds 4,163 of 14,076 (B): seed-sensitive, below the floor either way | CONFIRMED (C4) | - |
| 9 | Verdict MMLU-Pro NOT INTERPRETABLE (support); MATH NO POCKETS | [R2] rule 2 (0 leaves) for MATH; rule 3 for MMLU-Pro (0 < 2 leaves at >=3/5 AND 782 < 10,000); reproduces under my seeds | CONFIRMED | - |
| 10 | Delta 0.000057 (SE 0.000183), 8,993 pairs, 385 clusters, DEFF 1.82, n_eff 4,941, MDE 0.00051 (non-deciding) | own increments, gate z and CR SE from the runner's fold base fits: Delta 0.000056644, SE 0.000183294, n 8,993, G 385, DEFF 1.8201, n_eff 4,941.0, MDE 0.0005132 (E); fold 3 z 1.228 closed, fold 4 tau 0.2054 z 3.064 | CONFIRMED to the digit | - |
| 11 | Reference pockets: MMLU-Pro 1 (econometrics, n=84, P=R=0.988, stability 0.86, min cell 5) | own seeds: same cluster (84; best src ori_mmlu-econometrics) matched 79/90 but **min cell 3 < 4: not a pocket** (B) | PARTLY (seed-fragile, C4) | MEDIUM |
| 12 | P-scoring: P1 HELD, P2 FAILED, P3 FAILED, P4 FAILED | P2: 1 pocketed leaf < 3 -> FAILED. P3: word not POCKETS PREDICT -> FAILED. P4: ratio 0.000841/0.000057 = 14.8 > 10 -> FAILED. [R12] gives NOT SCORED only for calibration fail or no stage 3 | CONFIRMED mechanically (registrar ruling R-1) | LOW |
| 13 | Stage 3 gating "(a) passes" = rule-1 calibration | [R10]: stage 3 runs iff N1, N3 and the [R1] count rule pass; N2/N4 do not block. The builder's reading is the registered one | CONFIRMED | - |
| 14 | Leakage | fold units: no fold-k item labelled, every weighted item in fold k (all 90+55 units re-checked, D); PCA fitted on training text only; stage 1 projects text columns only; base eta checked against library crossfit at run time | CONFIRMED | - |
| 15 | Tests 372 passed / 4 deselected; peaks 38; sync 33; ruff, mypy clean; manifest OK; Stage D in execution_graph.md | reproduced exactly (F) | CONFIRMED | - |
| 16 | 38/38 mutants killed | own mutants on deciding paths (sandbox copy): X2 killed; **X3, X4 survived** (C5) | PARTLY | MEDIUM |

Own mutants (sandbox `git archive` copy; tests/test_peaks.py each time):
- X1 `support_pairs`: `mx >= 0.5` -> `mx > 0.5`: SURVIVED; not decisive here (782 / 4,163 far from 10,000).
- X2 `verdict` rule 3: `or` -> `and`: killed.
- X3 runner stage 1 `folds_3of5` counts `v >= 1` instead of `v >= 3`: SURVIVED; decisive in principle (rule 3 leaf condition), not on this run (pair floor also fails).
- X4 `build_fold_pockets` keeps unpocketed leaves (`n_pockets < 1` -> `< 0`): SURVIVED; decisive in principle (every leaf "pocketed" makes NO POCKETS unreachable); this run unaffected (counts re-derived from pickles, row 7).

## Delta review of [R1]-[R13] (the step CHANGES asked for; done post hoc, all brackets committed before any output of record)
E1 -> [R1] faithful (s x w fit, template families, count rule); w_t uses 2 trace Sigma, the correct scale for a pair distance
(review wrote trace Sigma): accepted. E2 -> [R2], E3 -> [R3] (G/E exclusion added, 0 draws = FAIL), E4 -> [R4], E5 -> [R5]
(10,000-pair floor: one of the two offered options), E6 -> [R6], E7 -> [R7], E8 -> [R8] (Wilson lower 0.65 at 32: offered
option), E9 -> [R9]. [R10]-[R13] are placement, seeds, scoring and implementation details; none moves a bar. CONFIRMED.
[R12]'s gap (no rule for a NOT INTERPRETABLE (support) dataset) is the registrar's (R-1).

## Conditions / defects
- **C1 (HIGH, reading)**: no sentence may say MATH or MMLU-Pro "has no pockets" or that pockets "do not predict". The registered
  NO POCKETS word carries no UNDERPOWERED qualifier, yet N2 is 6-7% and N4 is impossible at any E on these data (all sims fixed by
  text-only rules 2/3; check 8). Fix: every quote of either verdict carries "method power failed (N2 7/110, 13/190; N4 unreachable)".
  P1 HELD is true by construction of the same weakness and is not evidence.
- **C2 (MEDIUM, disclosure)**: an undisclosed real-data pilot `E:/TaxoArena_tmp/peaks_build/pilot1` (06:37-06:42; reg blob
  7d507a2a = 49d326e; MATH leaf 17, n=157; stage 1 and stage 2 with 1 sim each, real Y read for the generator; no held-out number)
  preceded [R13] and the code commit; `pilot_m7` (07:13) is the M7 mutant. The hand-back says only "toy data". Fix: an insertion
  bracket in registration §0 naming both pilots, what they printed (N2 0/10 on leaf 17) and that [R13] followed them.
- **C3 (MEDIUM, closed here)**: run launched without the delta review of [R1]-[R13]; done above, CONFIRMED.
- **C4 (MEDIUM, robustness)**: seed fragility: the only reference pocket fails the per-cell floor under my seeds; support pairs
  782 vs 4,163; different fold pockets. Verdicts are unchanged under my seeds. Fix: any future pocket claim reports the
  matched-per-cell vector and a second seed stream.
- **C5 (MEDIUM, tests)**: X3 and X4 survive. Fix: a fixture where one leaf is pocketed in 2 of 5 folds (asserts folds_3of5 = 0)
  and one with an unpocketed leaf (asserts it is absent from FoldPockets.leaves and folds_any). LOW: X1 boundary test (w = 0.5 counts).
- LOW: SHA256SUMS written by hand (verifies 7/7); the runner should write it.

## AUTHOR / REGISTRAR DECISIONS
- R-1 (registrar): P3/P4 on a NOT INTERPRETABLE (support) dataset: FAILED (letter of [R12], applied here) or NOT SCORED.
- R-2 (author): G-peaks as registered is closed with no usable result; a redesign (single-cluster handling, plant > mcs, floor)
  is a NEW registration, not a re-run.

## Commands (A-F)
```
A  git -C Z:/FAC/TUBerlin/benchzoom log --format='%h %ad %s' --date=iso -5; ls -la --time-style=full-iso E:/benchzoom_demo/peaks_v1
   git rev-parse HEAD:<f> / git hash-object <f> for reg, peaks, runner, 8 lib; sha256sum -c SHA256SUMS (7 OK; find -newer = 0 after review)
B  scratchpad/gp_indep.py (own HDBSCAN/PCA pipeline, own seeds [990011,...], own groups = cos>=0.90 comps U doc_hash:
   n_groups 4839 / 11367, folds equal to the run's; 262 jobs, 6 workers, 674 s); analysis prints rows 3,4,5,7,8,11
C  json stage2_summary.json: Counter((word, shortcut)) over sims = 160x(NO POCKETS, True), 160x(NOT INTERPRETABLE (support), True)
D  python over work/<ds>/fold_<leaf>_<k>.pkl and alt10/alt20: pocketed counts, leakage asserts, support = sum answered on w_max>=0.5
E  own Delta: g,h from base_<k>.pkl (R, Info), centring, tau^2, gate z (re-implemented), d, W from nbrs, logloss, CR1 SE over groups
F  .venv pytest -q (372 passed, 4 deselected); test_peaks 38; test_execution_graph_sync 33; ruff "All checks passed!";
   mypy src examples/peaks_test.py "no issues in 15 source files"; update_graph_manifest.py --check "manifest OK"
```
