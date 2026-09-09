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

### RUBRIC-P8 OUTCOME (2026-09-09): **NULL — exactly zero.** 994 matches on p8a29 (the frozen
tree's true held-out pool; its rubrics never saw any of these questions), Mistral, same session,
dual order, 0 invalid: cell 0.823 vs generic 0.823, discordant 20:20, McNemar p = 1.0.
Discursive anchors −0.5pp (13:16), quantitative +0.8pp (7:4); no anchor beyond ±4pp on
n = 71 each (Chemistry/Health +4.2 on 3:0; Psychology −5.6 on 0:4). Secondary FAILS.
This is the clean, powered measurement the withdrawn p = 0.0001 result should have been:
for a non-reasoning judge on key-verifiable questions, the frozen tree's induced cell
rubrics add nothing over the production generic judge. Cache experiment_results/rubric_p8/
mistral.db, output outcome.txt. (The verdict rate is higher here than on x12's decidable
subset, 0.82 vs 0.77, because pairs were sampled uniformly among decidable pairs rather
than by the arena's placement schedule — disclosed; it does not affect the paired contrast.)

### RUBRIC-512 OUTCOME (2026-09-09): **PRIMARY PASS at the boundary; SECONDARY PASS.** Tree
bareq512_s42 (built with reservedPoolFile = p2dca, 87 leaves, all with induced rubrics; snapshot
20260909_212117), R3's 1,980 matches, Mistral, 0 invalid; 946 key-decidable paired matches:
cell 0.773 vs generic 0.755 (+1.8pp), discordant 42:25, McNemar p = 0.0498. Discursive anchors
(n = 514) +3.7pp, 34:15, p = 0.009; quantitative anchors (n = 432) −0.5pp, 8:10, p = 0.81.
Per anchor: Philosophy +16.7 (5:0), Biology +7.4 (4:0), Business +6.1, Psychology +4.4,
Health +3.4; Physics −1.6, Engineering −4.7. Prediction (+1 to +2pp, NOT significant; secondary
holds) was right on the effect size and wrong on the letter — the p-value sits on the threshold.
Two disclosures: (i) the GENERIC arm is the cached verdict set from the earlier rubric-contrast
session, the CELL arm was judged today (the ladder's old-vs-fresh session confound applies; a
same-session GENERIC re-judge of the same 1,980 matches, ~4k calls, would remove it and is the
registered follow-up RUBRIC-512-SS if the claim is to be published as significant); (ii) the two
clean measurements disagree on the anchor pattern: RUBRIC-P8 (frozen tree's rubrics on p8a29,
same session) found 0.0pp with discursive −0.5 / quantitative +0.8, RUBRIC-512 finds +1.8 with
discursive +3.7 / quantitative −0.5. What can be claimed after both: cell rubrics induced without
the judged questions are worth 0 to +2pp to a non-reasoning judge on keyed questions, borderline
at n ≈ 950, with the gain — where there is one — in the discursive anchors where S1 showed the
judge is competent; the +1.5pp p = 0.0001 of the contaminated run is not recoverable as a
headline. Cache experiment_results/rubric_512/bareq512_s42.db, output outcome.txt.

## RUBRIC-512-SS — same-session control for RUBRIC-512 (registered 2026-09-09, NOT launched)
RUBRIC-512's GENERIC arm is the cached verdict set from the earlier rubric-contrast session;
its CELL arm was judged on 2026-09-09. The ladder showed session drift of the same order as
the effect (old-vs-fresh confound). Design: re-judge the GENERIC arm (production GENERIC_JUDGE
text, byte-identical templates) on the same 1,980 R3 matches, Mistral, in one session
interleaved with nothing else (~4k calls, ~1 h at 12 workers); primary = paired McNemar of
RUBRIC-512's CELL verdicts vs the fresh GENERIC verdicts on key-decidable matches.
REGISTERED: the rubric-value claim is publishable as significant iff cell > generic at
p < 0.05 against the SAME-SESSION generic; otherwise the claim is "0 to +2pp, not
significant". Secondary: discursive gain > quantitative gain. Prediction: +1pp, p > 0.1 —
the boundary p = 0.0498 does not survive the session control.

### RUBRIC-512-SS OUTCOME (2026-09-10 00:24): **PRIMARY FAIL, as predicted — the boundary pass does not
survive the session control.** Fresh GENERIC on the same 1,980 matches (0 invalid), 946 key-decidable
triples: cell 0.773 vs fresh generic 0.763 (+1.0pp), 35:26, p = 0.31. The session drift itself is
+0.8pp (fresh 0.763 vs cached 0.755, 27:19, p = 0.30) — almost half of RUBRIC-512's +1.8. Secondary
holds again: discursive +2.5pp (26:13, p = 0.053), quantitative −0.9pp (9:13); Philosophy +23.3pp on
7:0 (n = 30), Physics −3.2, Engineering −2.3. FINAL rubric-value statement for the non-reasoning judge
on keyed questions, from three clean measurements (P8 0.0pp; 512 +1.8 boundary; 512-SS +1.0 n.s.):
cell rubrics add about +1pp overall, not distinguishable from zero at n ≈ 950, with a repeatable
concentration in the discursive anchors (Philosophy in particular) and nothing or slightly negative
in the quantitative ones. The contaminated p = 0.0001 is withdrawn for good; the STACK judge uses the
anchor rubric. Cache experiment_results/rubric_512/generic_ss.db, output generic_ss_outcome.txt.

## J2-R — J2 with the reasoning judge's references (registered)
As J2 (Mistral judges, same 1,980 matches, same templates) but the reference is
grok-4-1-fast-reasoning's S1 answer (85.6% correct). REGISTERED: all-decidable gain > J2's
+3.4pp with McNemar p < 0.05; strata reported. Prediction from J2's strata arithmetic
(+9.7 x 0.856 − 7.1 x 0.144): ≈ +7pp overall.

### J2-R OUTCOME (2026-09-09): **PASS, as predicted.** 1,974 judged, 0 invalid. All decidable
(n = 944) +7.6pp (0.849 vs 0.772; 88:16, p < 1e-4); top cluster +13.9pp (0.665 vs 0.526;
45:8); reference-correct +9.4 (82:5), reference-wrong −3.9 (6:11, n.s.). Mistral with a
reasoning reference matches the reasoning judge of J1 (0.847 / 0.647). Full record in
docs/judge_improvement_proposals.md; output experiment_results/x12_crossdomain/j2r_outcome.txt.

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
