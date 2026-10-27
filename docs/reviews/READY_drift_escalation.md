# READY review — DRIFT-REPLAY and ESCALATION-CURVE (2026-10-05; zero calls)

Build: branch `drift-escalation` tip 823f6148 (worktree agent-af2c83d397755e469), diff vs main = 2 files, 3,133 insertions
(`git diff --name-only main...823f6148 | wc -l` = 2). Registrations prog L24639-L24651 (DRIFT-REPLAY), L24653-L24665
(ESCALATION-CURVE), record L24618-L24623 (_as_of 64538609, re-grepped: no later bracket on either id).
Pins (LF of record; both working-tree files are the LF rendering): `drift_replay.py` blob:39e0515f (sha256-lf16 59ad40cdb0fd5b33,
crlf16 f8f178da7eae1f41); `escalation_curve.py` blob:0acfb0cc (lf16 b3b17943e1e51b23, crlf16 b3690bceb8666241). Imported:
escalation_rc 8f99db7d, union_af_route bf3f17db, g13_breakdown c29fa1c3, union_route_common d5473976, union_cells_io 92a04543.

## Verdict

- **DRIFT-REPLAY: NOT READY** (B-1, design, pre-data). The code is correct and as registered; the registered DR0 gate fails BY
  CONSTRUCTION, so DR2 / DR1 would read UNDETERMINED with near certainty. Needs a registrar bracket choosing a fix (below), then a
  delta review of the change (small).
- **ESCALATION-CURVE: READY**, conditions C-EC1..C-EC3 (registrar brackets; no code change).

## Rulings asked for

| item | ruling | evidence |
|---|---|---|
| C-1 tau rule vs value (DRIFT) | **CONFIRMED: the rule decides; 0.540800 is a transcription, bracket it as such.** The [DR-TAU] check recomputes ESCALATION-RC's CANDIDATE form (`ERC.score_items` -> `af_cands`: an item whose routing-row cell is the IFEVAL one-cell is scored against that cell only; every other item against the 122 graft leaves, IFEVAL centroid excluded). That form reads the declared source through the routing-row filing, so it is not "max-cos to the arm's cells, filing never reads the declared source". It reproduces 0.540800 because it IS the same computation on the same 2,033 GATE items. The source-blind score (max over all 123) is >= the candidate score on every GATE item (18 of 2,033 strictly higher, 0 lower; 54 candidate one-cell items vs 38 source-blind filings to the IFEVAL centroid), hence p5 0.542658 > 0.540800. Using the value with source-blind scores would give GATE TPR 0.9513, not the registered 0.95, and no value exists for the KM-U arms ("the same rule on GATE for each k-means seed"): only the rule is like with like. | own script `gate_check.py` (GATE only): tau cand 0.540800, blind 0.542658; dry-run line `GATE-ONLY ... AF-U 0.542658` |
| escalation_rc pin a17f6821 -> 8f99db7d | **CONFIRMED selftest-only**: `git diff a17f6821 8f99db7d` = 2 lines changed (L1474, L1564: `import tempfile; import scratch_dir`), both below the SELFTEST marker (L883); code the readers call is byte-identical. Registrar bracket owed (EC-R12 / DR-R14 deviation). | `git diff a17f6821 8f99db7d \| grep -c '^[-+][^-+]'` = 4 |
| bootstrap seed 20261008 (DR-R10) | ACCEPTED, descriptive only (component bootstrap, B 200); never enters DR0/DR1/DR2. Registrar bracket owed. | `comp_boot` result only feeds `st["comp"]` lines |
| GATE before EVAL | **CONFIRMED both.** DRIFT: `prepare()` reads GATE rows, vectors, scores, the tau identity and the gen-view GATE meta before the marker and `eval_structure`; tau, reference occupancy, bins and alarm levels are functions of GATE arrays only (`arms_from` og/cg; `simulate` GATE streams with GATE shares; own mutants R3/R4 and X14-X16 killed). ECURVE: GATE ECDFs in `prepare()`; EVAL scored without key; GATE key inside `between` (after TRAIN key, before the eval view); one EVAL key read after the marker. | code read; dry-runs: no EVAL opened (DRIFT), no key read (ECURVE) |
| ECURVE not blind | **CARRIED, partly**: WORDS line ("SEEN in ESCALATION-RC (no fresh test)"), the component-area line, and the P1 Brier line ("not credited as a forecast: informed"). The P1 numeric band line and both P3 lines carry no qualifier (C-EC1). | `ec_lines` L297-L397 |

## Per-claim table (deciding paths)

| claim | mine vs claimed | state | sev |
|---|---|---|---|
| DRIFT shift grid: s {0.05,0.10,0.20,0.40} x 6 members x R 200; 1,200 unshifted; pi_1 = (1-s)pi_0 + s e_m; change after 500; 81 windows w 200 step 10 | as registered (REG, `stream_plan`, `draw_streams`, `window_counts`); `default_rng(s).spawn(n)` == `SeedSequence(s).spawn(n)` checked (numpy 1.26.3, True) | CONFIRMED | — |
| DRIFT DR0 gate code (FAR on 1,200 unshifted, both AF-U detectors, point <= 0.10, any of 81 windows; h = sorted max[n-101]) | code correct; but the gate is **predicted MISCALIBRATED** (B-1) | CONFIRMED code / REFUTED design | BLOCKER |
| DRIFT DR2 interval: AF-U s 0.20, OCC minus OOS, stream-paired, 6 members fixed strata x 200, B 2,000 default_rng(20261007), percentile [int(.025B)], [int(.975B)-1] | as registered; no seed term in DR2 (correct); DR1 crosses 5 seeds (own R1 killed with RNG consumption preserved) | CONFIRMED | — |
| DRIFT like with like: AF-U 123 cells source-blind nearest (122 vmfMu + IFEVAL centroid) vs KM-U ukm_fit k 123 on the same 12,334 bundle TRAIN rows, 256-d, same GATE-occupancy bin rule, same streams | CONFIRMED; [SC] vs [LF] asymmetry printed in the LIKE WITH LIKE line. Cross-source filing: AF-U may file an item into another source's leaf or the IFEVAL centroid (registered flatLeaf over all leaves); agreement with af_cells.tsv printed at --run | CONFIRMED | — |
| DRIFT Support (a)-(f) arithmetic | DR2 sqrt(.5x1.5/1200)=0.0250, MDE 0.070; DR1 sqrt(1.875e-4+1.8e-4)=0.0192, MDE 0.054; DR0 sqrt(5.94e-5)=0.0077, MDE 0.019; n_eff 800 — all reproduce; DEFF 1.5 declared assumption, source stated. Support (g) "R can be raised at will" is wrong for DR0 (B-1) | PARTLY | BLOCKER (in B-1) |
| ECURVE Support: DEFF 1.302 source = ESCALATION-RC outcome L68 / POSTRUN_escalation_rc L34 (measured); n_eff 5907/1.302 = 4,537; SE <= 0.00255/sqrt(.226) x 2/3 = 0.00358; MDE 0.0100 | reproduce; post-run DEFF, n_eff, MDE printed beside EC1 (support line) | CONFIRMED | — |
| ECURVE EC1: A_E = mean of D_E over 101 points; u = min(F_m, F_oos), right-continuous GATE ECDF, +inf -> 1; u desc, sha tie; round(cN) kept; random line at realised weighted share; interval point +- 1.96 SE_2stage (ESCALATION-RC's form: RC1 0.00497 +- 0.0050); words lo>0 / hi<0 / else | CONFIRMED (code read; own E1-E4 killed) | CONFIRMED | — |
| ECURVE parity identity (margin-only, OOS-only tables, AF-U and K_0, 0.05 grid, 5 dp) against outcome sha 4dad8268 | regex captures margin/OOS columns; 21 rows each enforced; pin checked at dry-run (= pin) | CONFIRMED | — |
| Selftests | DRIFT 7/7 (22.8 s), ECURVE 6/6 (9.7 s), mine | CONFIRMED | — |
| Builder mutants | re-run: DRIFT 56/56 KILLED, ECURVE 50/50 KILLED, controls survived, none not applied (the brief's "50/50 and 56/56" in the other order) | CONFIRMED | — |
| No write to DBs of record | embeddings_cache.db sha256-16 b0e88d3a6e207bc0 before = after both dry-runs; gen view sha before = after (printed); no outcome dir created | CONFIRMED | — |

## Defects

- **B-1 (BLOCKER, DRIFT design; registrar + orchestrator, pre-data).** The OCC-CHI reference occupancy AND the alarm level are both
  taken from the SAME 2,033 GATE items. GATE streams are therefore exactly calibrated against their own population, while EVAL
  streams (5,907 items) carry a non-centrality from the finite-sample difference of the two occupancies (about w (bins-1)
  (1/2033 + 1/5907) = 200 x 34 x 0.00066 = 4.5 per window, applied to all 81 overlapping windows). Emulation (multinomial GATE and EVAL
  populations drawn from the REAL AF-U GATE occupancy, the module's own `make_bins` / `level` / `chi_stat` / `draw_streams`, s = 0):
  EVAL FAR OCC-CHI median **0.438**, p10 0.276, p90 0.570, **30 of 30 > 0.10**; sanity (test population = GATE) 0.052. A synthetic
  occupancy gives 0.308 (15 of 15 > 0.10). OOS-RATE: median 0.052, 9 of 30 > 0.10 (binomial noise of the GATE-p5 rate). So DR0 reads
  MISCALIBRATED and DR2 / DR1 UNDETERMINED regardless of R; P1 "DR0 CALIBRATED 0.80" and Support (g) "R can be raised at will" are
  not met by the design. FIX (choose one, bracket pre-data, re-emulate on GATE only before the bracket):
  (a) reference occupancy from an object independent of BOTH GATE and EVAL, e.g. the bundle's 12,334 TRAIN rows, level still
  GATE-calibrated: GATE and EVAL then stand exchangeably against the reference (emulated FAR median 0.023, 0 of 15 > 0.10;
  conservative); (b) split GATE: reference from one half, level from streams of the other half (same logic, noisier); (c) a
  self-referenced two-sample detector (window vs the stream's own items 1-200): a detector change, re-registration. Decide also
  whether the OOS-RATE leg keeps a GATE-p5 tau with GATE-calibrated h (30% emulated risk) or takes the same exchangeability fix.
- **M-1 (MEDIUM, DRIFT words).** At w 200, 123 cells give 35 bins of which 33 are rare bins pooling up to 8 cells by ascending GATE
  share (only 2 single-cell bins; own `gate_bins.py`). OCC-CHI is a share-rank-pooled statistic that mixes cells of different
  sources; outcome words must say "35-bin pooled occupancy", not "cell occupancy". If B-1 is re-registered, consider w or the
  pooling rule in the same bracket.
- **C-EC1 (LOW, ECURVE).** P1's numeric band line and the P3 lines lack the "informed by the seen component curves" qualifier;
  the registrar quotes P1/P3 with it (no code change).
- **C-EC2 (LOW, both).** Bracket the escalation_rc pin deviation a17f6821 -> 8f99db7d (selftest lines only, confirmed above).
- **C-EC3 (LOW, DRIFT).** Bracket DR-R10's unregistered seed 20261008 as descriptive only; and C-1's ruling (rule decides; 0.540800
  is the candidate-form transcription checked as an identity of the geometry, the detectors use the printed source-blind tau).

## Own mutants (sandboxed: in-memory edits via union_route_common.run_mutants, temp on E: through scratch_dir)

| id | change | result | decisive |
|---|---|---|---|
| R1 | DRIFT KM-U seeds not crossed, RNG consumption kept (`*0 + arange`) | KILLED | yes (DR1 interval) |
| R2 | DRIFT DR0 OCC FAR read on KU0 | KILLED | yes |
| R3 | DRIFT alarm level from post-change windows only | KILLED | yes (calibration) |
| R4 | DRIFT EVAL pre-change mix = GATE shares | KILLED | yes |
| E1 | ECURVE +inf margin mapped below all GATE (IFEVAL escalates first) | KILLED | yes (registered IFEVAL rule) |
| E2 | ECURVE random line with cells / best swapped | KILLED | yes |
| E3 | ECURVE EC1 read on K_0's area | KILLED | yes |
| E4 | ECURVE two-stage replicates traced unweighted | KILLED | yes (EC1 interval) |

## Commands

```
git -C <wt> hash-object tools/analysis/drift_replay.py tools/analysis/escalation_curve.py      # 39e0515f, 0acfb0cc
git -C <wt> diff a17f6821 8f99db7d                                                           # 2 lines, below SELFTEST (L883)
python tools/analysis/drift_replay.py --selftest ; python tools/analysis/escalation_curve.py --selftest    # 7/7, 6/6
python tools/analysis/<script>.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena      # rc 0 both; E:/TaxoArena_tmp/{drift,ecurve}_rev_dry.txt
python tools/analysis/<script>.py --mutants                                                  # E:/TaxoArena_tmp/{drift,ecurve}_rev_mut.txt
python E:/TaxoArena_tmp/drift_rev/gate_check.py    # GATE only: tau cand/blind, 18/0 items, TPR 0.9513, FAR emulation 0.438 (30/30)
python E:/TaxoArena_tmp/drift_rev/far_emul2.py     # sanity 0.052; as built 0.308; option (a) TRAIN reference 0.023
python E:/TaxoArena_tmp/drift_rev/gate_bins.py     # 35 bins, 33 rare, 2 single-cell, max 8 cells per bin
python E:/TaxoArena_tmp/drift_rev/own_mutants.py {drift|ecurve}                               # own R1-R4, E1-E4
sha256sum embeddings_cache.db | cut -c1-16         # b0e88d3a6e207bc0 before and after
```

## DELTA REVIEW 2026-10-05 — DRIFT-REPLAY fix (a) (tip 942d306b, `drift_replay.py` blob:a59389e2; brackets 7b31d00c)

**Verdict: DRIFT-REPLAY READY**, conditions D-C1 (OOS-leg words) and D-C2 (LOW, selftest note). B-1 and M-1 are discharged; C-1 is confirmed again.

Pins: blob:a59389e29887217349da17f4127c4694bcfda366, sha256-lf16 cfd78067357299db, crlf16 26f853888abaf079 (the working tree holds
the LF rendering). Diff 823f6148..942d306b = 1 file (`git diff --stat`: drift_replay.py, +90 / -18); escalation_curve.py and imports untouched.

| check | mine vs claimed | state | sev |
|---|---|---|---|
| Delta confined | code-path changes only: `arms_from` gains Xt / src_t; `ct = nearest(Xt, C)` gives the reference p and the bins (AF-U, KM-U); SRC reference = TRAIN class sources (`U.UCI.member`, members_index requires exactly the six); `prepare` returns Xt / tsrc; `run` / `cost_line` call sites; new M-1 line and the F-DR wording. tau (`og` p5), levels (GATE streams), DR words, bootstrap unchanged | CONFIRMED | — |
| 1. FAR emulation under fix (a), GATE only | REAL TRAIN reference (12,334 rows; 33 bins, all pooled), GATE and EVAL populations multinomial from the real AF-U GATE occupancy, module's own functions, s = 0, 30 reps: EVAL OCC-CHI FAR median **0.025**, p90 0.048, max 0.078, **0 of 30 > 0.10** (old rule 0.438, 30/30). Pessimistic variant (the REAL GATE population as the calibration, EVAL drawn around it): median 0.070, 1 of 30 > 0.10. Builder's b1_exch 0.047 vs 0.300 is consistent | CONFIRMED (B-1 discharged) | — |
| 2. tau | the `[DR-TAU] ... candidate-form ... 0.540800` line is only the identity check (ESCALATION-RC's candidate form, the refusal gate); the OOS flags use `info[nm]["tau"]` = GATE p5 of the source-blind max-cos over all 123 cells = **0.542658** (dry-run GATE-ONLY line), as bracketed (C-1) | CONFIRMED | — |
| 3. OOS-RATE FAR leg | exact model (uniform GATE / EVAL scores, tau = GATE p5, h from 2,000 GATE streams, 200 reps): EVAL FAR median 0.030, mean 0.047, p90 0.118, **share > 0.10 = 0.140**. This replaces my earlier 9/30 (0.052 median), which came from a cruder Bernoulli model. Real GATE: rate 0.0502, h = 20 flags per window. FAR is steep in the EVAL OOS rate: 0.050 -> 0.017, 0.055 -> 0.080, 0.060 -> 0.195. So there is about a 14% chance DR0 reads MISCALIBRATED from split sampling noise alone. That is a risk the registration already priced (P1 "CALIBRATED 0.80"), not a defect by construction: DR0 exists to test exactly this transport. Moving tau to TRAIN would change the operating point of record, and TRAIN is the construction's own data, so it is not recommended | NOT A BLOCKER | MEDIUM (words) |
| Selftest | 8/8 (b1_exch fails under the old rule: non-vacuous) | CONFIRMED | — |
| Mutants | 61/61 KILLED (X57-X61 new, X15 / X52 re-anchored); my earlier R1-R4 re-run 4/4 KILLED; delta mutants D1 (TRAIN shares divided by the GATE count) and D2 (TRAIN filed against KM-U seed-0 centroids for every arm) KILLED, both decisive | CONFIRMED | — |
| Dry-run | rc 0, 11 s order; REFERENCE OCCUPANCY line; bins 33 per arm, SRC 6; embeddings_cache.db sha256-16 b0e88d3a6e207bc0 before = after | CONFIRMED | — |

Conditions:
- **D-C1 (MEDIUM, registrar; settles the OPEN item at prog L24718).** Keep the OOS-RATE leg as registered. If DR0 reads MISCALIBRATED, the words name which leg failed and its FAR. If only OOS-RATE fails, the words say "GATE-to-EVAL transport of the p5 operating point (about 14% expected under split noise alone)", and never "cells fail". Correct the record's "0.052, 9 of 30" to "0.140 share > 0.10 (exact model)".
- **D-C2 (LOW).** The first `run_e2e` leg now forces MISCALIBRATED with far_max -1, so the registered bar 0.10 is no longer exercised end to end. It is still covered by value in `branches`. No action needed beyond noting it.

```
git diff --stat 823f6148 942d306b ; git hash-object tools/analysis/drift_replay.py          # 1 file; a59389e2
python tools/analysis/drift_replay.py --selftest | --mutants | --dry-run --data-root <main>  # 8/8; 61/61; rc 0
python E:/TaxoArena_tmp/drift_rev/delta_far.py    # fix (a): 0.025 (0/30); pessimistic 0.070 (1/30); OOS FAR vs EVAL rate
python E:/TaxoArena_tmp/drift_rev/oos_far.py      # OOS leg exact model: share > 0.10 = 0.140
python E:/TaxoArena_tmp/drift_rev/own_mutants.py drift ; inline D1/D2 runner            # 4/4, 2/2
```
