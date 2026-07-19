# TaxoArena — Code Feature Audit (read-only)

**Repo:** https://github.com/0ctave/TaxoArena · **Commit audited:** `2b401c1 Experiment fixes` (latest on `main`) · **Date:** 2026-07-19

Scope: audit the codebase against the experiment checklist. Read-only — nothing was modified. Evidence is `file:line`. The two most consequential findings are **item 2 (C2 / ρ_canonical) = MISSING** and **item 8 (adaptive scheduler) = PRESENT/implemented**.

---

## Summary table

| # | Feature | Status | Evidence | Gap |
|---|---------|--------|----------|-----|
| 1 | MAIN arena→BT→ranking headless (12-model) | **PRESENT** | `TaxonomyBenchmarkService.runBenchmark`; `HeadlessBenchmarkRunner.kt:285-345`; ranking `TaxonomyRankingService.aggregateLeafScores` | — |
| 2 | C2 canonical re-grouping → ρ_canonical (no new judge calls) | **MISSING** | No re-group-by-editorial-domain + re-BT anywhere; grep canonical/editorial/reAggregate = 0 real hits | ρ_canonical never produced |
| 3 | Spearman ρ / Kendall τ vs GT accuracy | **PRESENT** | `ValidationService.computeSpearman:158`, `computeKendall:166`; logged `TaxonomyBenchmarkService.kt:1361` | — |
| 4 | Δρ = ρ_adapted − ρ_canonical | **MISSING** | Follows from #2 — no ρ_canonical → no Δρ | — |
| 5 | ORACLE condition (judge sees GT key) | **PRESENT** | `TaxonomyArenaService.kt:531-550` short-circuit winner from correctness, conf 1.0; cache disabled `:656` | — |
| 6 | GENERIC_JUDGE (C3) shared rubric | **PARTIAL** | `buildJudgeSystemPrompt:782-794` | GENERIC_JUDGE swaps prompt+rubric; C3 label swaps rubric only (asymmetry) |
| 7 | 12-model roster, precomputed, answer-key-blind | **PRESENT** | `PrecomputedModelOutputLoader.deriveModelName:33-44` (no cap); leakage guard `TaxonomyArenaService.kt:382-384` | — |
| 8 | Adaptive "Active BT Racing" scheduler | **PRESENT** | `ActiveBtRacingScheduler.kt` full impl; wired for MAIN `BtMatchScheduler.kt:273-284` | — (see detail) |
| 9 | C4 RANDOM_SCHEDULER clean random baseline | **PRESENT** | `RandomTournamentScheduler.kt` independent impl (empty predictions map); wired `BtMatchScheduler.kt:287-298` | — |
| 10 | Budget-fidelity curve (ρ at budget points) | **PRESENT** | Per-round `TrajectoryPoint` `TaxonomyBenchmarkService.kt:990-999`; random capped at MAIN budget `BtStoppingPolicy.kt:157-160`; CSV `ReportGenerator.kt:178-187` | No explicit "run at X% budget" param; curve is implicit per-round |
| 11 | Controlled centroid-routing test (Top-1/3/5/10) | **MISSING** | All routing via vMF trickle `routeQueryToLeaves`→`TaxonomyTrickler.routeQuery`; only Top-1+Any-Match | No standalone nearest-centroid router, no Top-3/5/10 |
| 12 | Migration flow matrix (source→target, Other-outflow) | **MISSING** | Only per-domain TP/FP/FN `BatchTrickleEvaluator.kt:104-141` | No domain×domain matrix, no Other-outflow |
| 13 | Within- vs cross-domain migration decomposition | **PARTIAL** | `ancestorCorrectRate` `TaxonomyMetrics.kt:291,454-468` | No flow matrix / Other-outflow |
| 14 | Wilson CI for routing Top-1 | **MISSING** | Top-1 bare point estimate `BatchTrickleEvaluator.kt:167`; grep wilson=0 | — |
| 15 | McNemar / paired bootstrap MAIN vs KMEANS | **MISSING** | Baselines routed independently `HeadlessBenchmarkRunner.kt:246-273`; grep mcnemar=0 | No paired per-query test |
| 16 | Bootstrap/permutation CI for Δρ | **PARTIAL** | Bootstrap CI on ρ/τ (resampling models) `ValidationService.kt:65-108` | On ρ itself, not Δρ; no permutation test |
| 17 | Wilcoxon / multi-seed ρ significance | **MISSING** | Seed only drives sampling; grep wilcoxon=0 | — |
| 18 | Baseline snapshot generation (Python subprocess) | **PRESENT** | `scripts/generate_baselines.py` (kmeans/ward/randomnull); invoked `HeadlessBenchmarkRunner.kt:172-188` | — |
| 19 | Trickle loops over MAIN + 3 baselines | **PRESENT** | `HeadlessBenchmarkRunner.kt:239-277` loops MAIN→KMEANS→WARD→RANDOMNULL | TUI path still MAIN-only (headless is fine) |
| 20 | ECE emitted in trickle output | **PRESENT** | `BatchTrickleEvaluator.kt:163`→`ece`; logged `HeadlessBenchmarkRunner.kt:512`; CSV `:542` | — |
| 21 | Per-domain trickle table (P/R/F1) | **PRESENT** | `perDomainF1` `BatchTrickleEvaluator.kt:150-161`; rendered `HeadlessBenchmarkRunner.kt:515-527` | — |
| 22 | NMI variant (standard vs LFK) | **PRESENT (corrected)** | Standard `ShannonNmi` on depth-1-collapsed partitions `TaxonomyMetrics.kt:249-251`; LFK `OverlappingNmi` retained only as tested object | Not still-LFK |
| 23 | WARD per-query routing diagnostics | **MISSING** | WARD uses same generic path `HeadlessBenchmarkRunner.kt:257-263`; only global match-rate line `:460-468` | No candidate-count/top-1-score/rank-of-first-correct logging |
| 24 | Multi-seed support (iterate seeds in one run) | **MISSING** | Single `seed: Long = 42L` `HeadlessCliConfig:42`; no seeds list/loop | Single-seed only |
| 25 | All 4 conditions wired to execute in headless | **PRESENT** | Loop `HeadlessBenchmarkRunner.kt:285-390` runs each via `runBenchmark`; gated by `runBenchmark` flag `:280` | Path exists; prior log had `runBenchmark=false` (config, not code) |
| 26 | ReportGenerator emits all metrics into report/CSV | **PARTIAL** | Emits ρ+CI, τ+CI, pairwise acc, TopKJaccard, structural, routingECE, trajectory | Lacks Δρ, migration flow; per-domain trickle emitted by runner not ReportGenerator |

**Tally:** PRESENT 13 · PARTIAL 4 · MISSING 9.

---

## Per-feature detail

### A. Arena core (RQ1 ρ + RQ2 Δρ)

**1 — MAIN pipeline (PRESENT).** `HeadlessBenchmarkRunner.kt:285-390` iterates conditions, builds `BenchmarkRequest` (models data-driven `:331`), calls `benchmarkService.runBenchmark`, then aggregates a global BT leaderboard via `rankingService.aggregateLeafScores` (`:371`) and exports. Full arena→BT→ranking is wired for the headless N-model run.

**2 — C2 canonical / ρ_canonical (MISSING — critical).** There is **no** code that takes the C1/MAIN verdicts and re-groups them by MMLU-Pro editorial domain to re-aggregate a fresh BT ranking. `ValidationService.computeMetrics` accepts a `domain` filter (`:34-40`) but that filters the metric computation by domain — it does not re-group all verdicts into an editorial-domain partition and re-run BT to produce a global "canonical" model ranking. Grep for `canonical`/`editorial`/`regroup`/`reAggregate`/`deltaRho` returns no relevant implementation. Consequence: **ρ_canonical is never produced**, so the entire RQ2 Δρ comparison (adapted vs canonical grouping, free of new judge calls) is not built.

**3 — ρ / τ (PRESENT).** `ValidationService.computeSpearman:158`, `computeKendall:166`, computed against per-model GT accuracy vector and BT-score vector; surfaced in the report and logged at `TaxonomyBenchmarkService.kt:1361`.

**4 — Δρ (MISSING).** Direct consequence of #2. No subtraction of two ρ values anywhere.

**5 — ORACLE (PRESENT).** In `TaxonomyArenaService.kt:531-550`, when the condition is ORACLE the judge decision is short-circuited to the model that matches the GT answer key with confidence 1.0; response caching is disabled (`:656`) so ORACLE verdicts aren't polluted by MAIN cache.

**6 — GENERIC_JUDGE / C3 (PARTIAL).** `buildJudgeSystemPrompt:782-794` swaps in a shared rubric. Asymmetry worth flagging: the `GENERIC_JUDGE` branch replaces both judge prompt and rubric with generic text, while the `C3` label path swaps only the rubric — so the two names are not equivalent. Functionally a generic-rubric condition exists.

**7 — 12-model roster / answer-key-blind (PRESENT).** `PrecomputedModelOutputLoader.deriveModelName:33-44` derives model identity with no cap on model count; the arena consumes stored model *answers* (`pred`) and a leakage guard (`TaxonomyArenaService.kt:382-384`) keeps correctness out of the judging path except under ORACLE.

### B. Scheduling (RQ3)

**8 — Adaptive scheduler (PRESENT — fully implemented, not a skeleton).** `ActiveBtRacingScheduler.kt` implements the redesign end-to-end:
- Hoeffding radius with union bound over P pairs × Bmax peeks: `epsilon()` `:51-55`.
- Copeland ranking `:58-68`.
- RESOLVED / PAIR_EXHAUSTED / UNRESOLVED status via CI vs 0.5 `pairStatus:70-81`.
- Warm-start tournament pass (each pair ≥1 comparison, else EXHAUSTED) `pickPair:87-100`.
- Rank-adjacent, largest-overlap pair selection `:102-128`.
- Prediction-disagreement query selection, answer-key-blind `pickQuery:132-140`.
- Per-leaf `debt()` `:142-156` and round-robin global batching by descending debt `selectNextBatch:207-235`.
Wired as the MAIN scheduler: `BtMatchScheduler.selectNextBatch:273-284` dispatches `condition=="MAIN"` to it. The legacy `BtMatchScheduler` utility logic remains only as the fallback/LEGACY path (and in tests). So MAIN runs the redesigned scheduler.

**9 — C4 RANDOM_SCHEDULER (PRESENT — clean).** `RandomTournamentScheduler.kt` is an independent Erdős–Rényi-style scheduler: uniform random active leaf → uniform random unresolved pair → uniform random unused query (`:60-91`), constructed with an **empty predictions map** (`:31`) so it cannot reuse the adaptive disagreement logic. Only stopping condition is budget/query exhaustion. Wired via `BtMatchScheduler.kt:287-298` for `condition=="RANDOM_SCHEDULER"`. Seeded (`seed` ctor arg) for determinism.

**10 — Budget-fidelity curve (PRESENT).** Each scheduling round appends a `TrajectoryPoint(round, comparisons, spearmanRho, kendallTau, pairwiseWinnerAccuracy)` (`TaxonomyBenchmarkService.kt:990-999`), giving ρ as a function of cumulative comparisons — the budget-fidelity curve within a run. RANDOM_SCHEDULER is capped at MAIN's total comparisons for an equal-budget comparison (`mainConditionTotalComparisons` captured `:1007-1008`, enforced `BtStoppingPolicy.kt:157-160`). Exported to `${condition}_trajectory.csv` (`ReportGenerator.kt:178-187`). Note: the curve is emitted per-round rather than via an explicit "run at 25/50/75% budget" parameter.

### C. Free analyses (no LLM)

**11 — Centroid-routing test (MISSING).** No standalone nearest-centroid classifier. All routing goes through the vMF trickle router (`TaxonomyTrickler.routeQuery:31-134`); `vmfMu` centroids are used only inside trickle scoring (`:68`), never as a separate router. Output is Top-1 + Any-Match only (`BatchTrickleTestResults.kt:26-29`) — no Top-3/5/10, and no MAIN/KMEANS/WARD/RANDOMNULL centroid sweep distinct from trickle.

**12 — Migration flow matrix (MISSING).** Metrics build only per-domain TP/FP/FN tallies (`BatchTrickleEvaluator.kt:104-141`). No source(editorial)→target(leaf domain) tabulation, no "Other"-outflow quantification. Grep `flowMatrix`/`outflow` = 0.

**13 — Within/cross-domain decomposition (PARTIAL).** Only `ancestorCorrectRate` exists (`TaxonomyMetrics.kt:291,454-468,527`). No source→target matrix, no Other-outflow.

### D. Statistics

**14 — Wilson CI Top-1 (MISSING).** Top-1 is a bare ratio (`BatchTrickleEvaluator.kt:167`). Grep `wilson` = 0.

**15 — McNemar / paired bootstrap MAIN vs KMEANS (MISSING).** Baselines are routed independently in separate loop iterations (`HeadlessBenchmarkRunner.kt:246-273`); there is no per-query pairing between MAIN and KMEANS, hence no paired test. Grep `mcnemar` = 0.

**16 — Bootstrap CI for Δρ (PARTIAL).** `ValidationService.kt:65-108` bootstraps CIs for ρ and τ by resampling *models* as the unit — but on ρ itself, not on the paired difference Δρ between conditions. No permutation test.

**17 — Wilcoxon / multi-seed ρ (MISSING).** Seed only drives sampling; no across-seed collection or significance test. Grep `wilcoxon` = 0.

### E. Trickle & baselines

**18 — Baseline generation (PRESENT).** `scripts/generate_baselines.py`: k-means, Ward, random-null; excludes reserved test queries; writes `*_baseline_kmeans/_ward/_randomnull` snapshots. Invoked as a Python subprocess from `HeadlessBenchmarkRunner.kt:172-188` after DAG generation.

**19 — Multi-baseline trickle loop (PRESENT, headless).** `HeadlessBenchmarkRunner.kt:239-277` runs trickle validation over MAIN then loads and validates each of KMEANS/WARD/RANDOMNULL. (The interactive TUI batch-trickle path `TuiGatewayImpl.runBatchTrickle` remains MAIN/active-snapshot only — not a concern for the headless experiment.)

**20 — ECE (PRESENT).** Computed `BatchTrickleEvaluator.kt:163`, stored on `ece` field, logged (`HeadlessBenchmarkRunner.kt:512`) and written to the trickle CSV (`:542`).

**21 — Per-domain trickle table (PRESENT).** `perDomainF1` with support/precision/recall/F1 (`BatchTrickleEvaluator.kt:150-161`), rendered as a table (`HeadlessBenchmarkRunner.kt:515-527`).

**22 — NMI variant (PRESENT / corrected).** The reported path uses standard `ShannonNmi` computed on depth-1-collapsed partitions, with a comment stating this avoids LFK overlapping-NMI degeneracy (`TaxonomyMetrics.kt:249-251`, `ShannonNmi` def `:549`). LFK `OverlappingNmi` (`:615-730`) is retained only as a tested library object, not the reported metric. **Not still-LFK — this is the corrected/stable variant.**

**23 — WARD routing diagnostics (MISSING).** WARD is validated through the identical generic path as all conditions (`HeadlessBenchmarkRunner.kt:257-263`); the only routing diagnostics are a global match-rate line and three sample keys (`:460-468`), shared across conditions. There is **no** per-query logging of candidate count, top-1 score, rank of first correct-domain candidate, or candidate ordering — so the suspected WARD routing bug (6% Top-1 despite 77% pure leaves) currently has no instrumentation to investigate it.

### F. Multi-seed & orchestration

**24 — Multi-seed (MISSING).** `HeadlessCliConfig.seed` is a single `Long` (`:42`); it flows into split, sampling, and the random scheduler, but there is no seeds list and no loop over seeds within one invocation. Multi-seed requires repeated external invocations.

**25 — Four conditions wired to execute (PRESENT).** The conditions loop (`HeadlessBenchmarkRunner.kt:285-390`) executes each of `[MAIN, ORACLE, GENERIC_JUDGE, RANDOM_SCHEDULER]` back-to-back via `benchmarkService.runBenchmark`. It is gated by the `runBenchmark` flag (`:280`); the previously observed "conditions didn't run" was `runBenchmark=false` in the run config, not a code gap. The execution path for all four exists and is correct.

### G. Reporting

**26 — ReportGenerator coverage (PARTIAL).** `ReportGenerator.generateAndExport` emits ρ+CI, τ+CI, pairwise winner accuracy, Top-K Jaccard, structural metrics, routing ECE, and the trajectory/budget-fidelity CSV (`ReportGenerator.kt:178-187`) into `${cond}_thesis_metrics.json/csv`, `_domain_validation_details.csv`, `_trajectory.csv`. It does **not** emit Δρ (doesn't exist) or a migration flow matrix. Per-domain trickle P/R/F1 + ECE are written by `HeadlessBenchmarkRunner` (`:515-543`), not by ReportGenerator.

---

## Highest-impact gaps for the experiment
1. **C2 / ρ_canonical / Δρ (items 2, 4)** — the RQ2 linchpin is not built. Point-estimate ρ exists per condition, but the free re-grouping of MAIN verdicts by editorial domain to get ρ_canonical (and thus Δρ) is absent.
2. **Paired significance testing (items 14, 15, 16-permutation, 17)** — only model-resampled bootstrap CIs on ρ exist; no Wilson, McNemar, permutation-on-Δρ, or multi-seed Wilcoxon.
3. **Free routing diagnostics (items 11, 12, 23)** — no standalone centroid router, no migration flow matrix, and no WARD-specific per-query instrumentation to chase the 6%-Top-1 anomaly.
4. **Multi-seed orchestration (item 24)** — single-seed per invocation.

Scheduler redesign (8), clean random baseline (9), budget-fidelity trajectory (10), baseline generation + multi-baseline trickle (18-19), ECE/per-domain trickle (20-21), and corrected NMI (22) are all in place.
