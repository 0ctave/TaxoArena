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
