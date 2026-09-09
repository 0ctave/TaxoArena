# INCIDENT — the frozen tree's held-out split is not the pool the arena judged (found 2026-09-09)

## Finding
The frozen construction run (2026-07-27 04:03–04:25, snapshot 20260727_042523_Headless_Run_Auto_ge)
split the dataset with seed 42 and withheld pool **p8a29d8f3ff75aa55** (3,437 judgeable questions):
its own log records that pool as active, its trickle validation (Top-1 75.16%) was measured on it,
and its rubric induction withheld exactly its members (per-node `[JUDGE-LEAK] withheld N of M` counts
match the p8a29 membership, e.g. 4/169 where the p2dca hypothesis predicts 41).
The SNAPSHOT, however, stores a reserved list that hashes to **p2dca21ab5f4ef3ae** (3,445 questions),
and every judged run (r8, x8, x12, R2, and all re-judge harnesses) restored and used p2dca.
The two pools overlap on only 1,020 questions (29.6%). Mapping the frozen tree's train-side
queries to eval ids: **2,437 of p2dca's 3,445 questions (71%) are on the frozen tree's train
side** — used for construction AND for cell-rubric induction — and 0 of p8a29's.

## Mechanism (reconstructed from timestamps)
The freeze run wrote its split to the root `reserved_test_queries.json` at 04:03. Sweep runs were
executing concurrently on 2026-07-27 (pools recorded at 04:15, 04:19, 04:26 local); each rewrote the
same root file. `saveSnapshot` at 04:25 read the file as it then was — another run's split — and
stored it as the snapshot's reserved list. Every later load restored that foreign split. The
2026-08-02 clean-clone replication reproduced the DAG (same seed, same order at the time), which
is consistent: the tree is a p8a29-split tree; the replication did not check the stored pool.
Root cause: (1) a process-global mutable file as the carrier of the split, (2) no check at save
time that the stored reserved list equals the run's own split, (3) concurrent runs sharing the
repo root.

## What is affected
- **Rubric-value claims on p2dca verdicts are contaminated**: cell rubrics were induced on corpora
  containing ~71% of the questions they were then used to judge. Re-scored on the 1,020 CLEAN
  questions (in both pools) vs the contaminated rest (experiment_results/contamination_recheck.txt):
  - cell vs generic (Mistral): CLEAN +0.9pp, 52:41, p = 0.30 (n = 1,252) · CONTAMINATED +1.8pp,
    144:86, p = 0.0002. The registered "cell > generic, p = 0.0001" does NOT hold on clean questions.
  - H7 cell vs random-anchor: CLEAN +0.7pp, p = 0.82 · CONTAMINATED +2.7pp, p = 0.005.
  - H7 cell vs sibling: CLEAN 0.0 (5:5) · CONTAMINATED +2.0, p = 0.17.
  - LADDER leaf vs anchor: CLEAN −1.4 (5:9, p = 0.42) · CONTAMINATED +0.1 — the "knee at anchor"
    result stands in both halves (anchor/stratum rubrics were induced by the ladder harness
    withholding p2dca, so they are clean; only the LEAF arm is contaminated).
- **Routing of the pool of record is in-sample for 71%**: reserved_leaf_assignments.csv,
  the strata, the R2 atlas cells and every per-cell/per-stratum profile number were computed on
  routing that had seen most of the questions. The held-out Top-1 figures in the freeze run's own
  validation (on p8a29) are honest; arena-side routing purity (H5 73.6%) is not held-out.
- **NOT affected**: judge-behaviour results (J1 ceiling, L1 elaboration, S1 solve map, F3/F7
  confidence, verbosity coefficients, order/tie analyses) — they use verdicts and the key, not
  rubric hygiene; the structural sweeps D1–D3 and the key-only F2/F5/F6 (label-free, no judge);
  the anchor/stratum rubric arms of the ladder; the x12/R2 global rankings insofar as they are
  judge decisions (rubric content could shift verdicts marginally, but rho vs GT is a judge-level
  fact — to be re-checked on the clean subset).
- **To be re-checked on the clean subset** (zero calls): the model×domain interaction LRT, the
  12-model rho, the rubric-induced shift H1, the strata profile.

## Guards added (2026-09-09)
1. Save-time pool consistency: the snapshot's reserved list must hash to the run's OWN split
   pool id — FATAL otherwise (TaxonomySnapshotManager.saveSnapshot / HeadlessBenchmarkRunner).
2. `reservedPoolFile`: construction can take the held-out set from an explicit id file instead of
   a seed (experiment_configs/reserved_pool_frozen_p2dca.json = the pool of record); seeds do not
   reproduce a split across dataset-order changes.
3. Standing rule: never run two construction processes concurrently in the same repo root.

## Decision (2026-09-09): options A and D
- A: tools/analysis/clean_subset_reanalysis.py re-scores every affected claim on the clean
  subset; results appended below and disclosed in the ledger.
- D: promoted builds bareq512_s42 and abt2d512_s42 rebuilt with `reservedPoolFile =
  experiment_configs/reserved_pool_frozen_p2dca.json` (queued behind D3). REGISTERED
  follow-up **RUBRIC-512** (before running): on the R3 stratified sample (1,980 matches),
  Mistral, byte-identical prompts, the clean 512-dim tree's LEAF rubric (question routed
  through that tree, `routeReserved`) vs the cached GENERIC verdict, key-decidable, paired
  McNemar. PASS iff cell > generic at p < 0.05. Prediction, from the clean-subset numbers:
  positive direction, +1 to +2pp, NOT significant at n ≈ 950 decidable — i.e. the honest
  rubric-value effect under a non-reasoning judge is small; S1 says it should concentrate in
  the discursive anchors (secondary: gain in {Philosophy, History, Psychology, Biology,
  Health} > gain in {Math, Physics, Chemistry, Engineering}).

## Option A results (2026-09-09, experiment_results/clean_subset_reanalysis.txt)
CLEAN = 1,020 questions held out under both pools; CONTAMINATED = the 2,425 on the frozen tree's
train side. Paired McNemar on key-decidable matches, ties wrong.

| claim | CLEAN | CONTAMINATED | status |
|---|---|---|---|
| Cell rubric > generic (Mistral) | +0.9pp, 52:41, p=0.30 (n=1,252) | +1.8pp, 144:86, p=0.0002 | **WITHDRAWN as significant**; direction positive |
| Cell rubric > generic (grok) | +2.3pp, 14:8, p=0.29 (n=264) | +2.5pp, 43:26, p=0.05 | withdrawn; direction positive |
| H7 cell > random-anchor rubric | +0.7, 11:9, p=0.82 | +2.7, 28:10, p=0.005 | **WITHDRAWN** |
| H7 cell > sibling | 0.0, 5:5 | +2.0, p=0.17 | null (was null) |
| H7 length clause (cell vs cell+clause) | +1.1, p=0.73 | +1.1, p=0.33 | unchanged (null) |
| Ladder: leaf / stratum / generic vs anchor | −1.4 / −1.8 / −1.1, all p>0.35 | +0.1 / −1.6 / −1.3 | **STANDS**: anchor-level rubrics are as good as anything, on clean and contaminated alike |
| 12-model board rho vs key (x12, R2) | 0.951 | 0.951 | **STANDS** (identical top-4 and violations in every subset) |
| Model×domain interaction LRT (R2, question-level permutation) | LRT 38.8 vs null p95 21.0, p=0.002 | LRT 94.1, p=0.001 | **STANDS** on clean questions |
| Verbosity beta_len (x12 decisive) | +0.284/1k, z=6.7 | +0.457/1k, z=13.2 | **STANDS**; magnitude smaller on clean (reported) |
| R2 strata profile | 22–38% clean questions per stratum | — | in-sample routing for the rest; per-stratum precision not recoverable without re-measurement |

Net: the rubric-specificity results (RUBRIC, H7 random) do not survive; the anchor-knee,
ranking, interaction and verbosity results do. What the campaign can claim about rubrics
after this: a cell rubric induced WITHOUT the judged question is worth about +1pp to a
non-reasoning judge, not distinguishable from zero at n ≈ 1,250, and no better than an
anchor rubric — consistent with S1 (rubrics help where the judge is already competent)
and with the ladder. RUBRIC-512 (option D) is the registered clean measurement.

## RUBRIC-P8 — the clean, powered test of the frozen tree's OWN rubrics (registered 2026-09-09, before any call)
Questions: the frozen tree's true held-out pool p8a29 (3,437; its rubrics never saw any of
them). Matches: 1,000 key-decidable pairs among the 12 arena models, stratified by anchor
(~72 per anchor), pairs sampled uniformly among decidable pairs per question, seed 42.
Routing: nearest-leaf-centroid on the 256-slice (the disclosed approximation of routing
used for every rubric corpus; in-sample for none of these questions). Arms, same session,
Mistral-Large-3, dual order, byte-identical v1 templates: CELL (the routed leaf's induced
persona + rubric) vs GENERIC (the production GENERIC_JUDGE text via
rubric_value_contrast.build_generic_system_prompt). REGISTERED PRIMARY: cell > generic,
paired McNemar p < 0.05 on the decidable matches (all are decidable by construction).
SECONDARY (S1's prediction): the gain in discursive anchors {Philosophy, History,
Psychology, Biology, Health, Law, Economics, Business, Other} exceeds the gain in quantitative
anchors {Math, Physics, Chemistry, Engineering, Computer science}. Prediction: +1 to +2pp,
not significant at n = 1,000 (the clean-subset estimate); secondary direction holds.
~4,000 calls. Harness tools/analysis/rubric_p8.py.

## J2-R — J2 with the reasoning judge's references (registered)
As J2 (Mistral judges, same 1,980 matches, same templates) but the reference is
grok-4-1-fast-reasoning's S1 answer (85.6% correct). REGISTERED: all-decidable gain > J2's
+3.4pp with McNemar p < 0.05; strata reported. Prediction from J2's strata arithmetic
(+9.7 x 0.856 − 7.1 x 0.144): ≈ +7pp overall.

## Options (decision for the author)
A. Re-analyse on the clean subset and DISCLOSE — every affected claim restated with the clean
   numbers; the rubric-value claim is withdrawn as a significant result (direction positive,
   underpowered). Zero calls; ready today.
B. Re-judge on the frozen tree's TRUE held-out pool (p8a29): a confirmatory x12-scale run
   (~9k verdicts) reproduces every rubric/ranking claim on questions the tree never saw.
C. Re-induce the frozen tree's rubrics with p2dca withheld (rubrics only; the tree's routing of
   p2dca stays in-sample) — cheaper, partial.
D. Promote the 512-dim tree built with `reservedPoolFile` = p2dca and re-run the rubric-value
   contrast on it (the certified-leaf ladder was going to need this build anyway).
