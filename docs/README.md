# TaxoArena: Dynamic Hierarchical DAG Taxonomy for Model Evaluation

**TaxoArena** is a self-organizing system that constructs a **Dynamic Hierarchical Directed Acyclic Graph (DAG)** taxonomy directly from MMLU-Pro evaluation queries. Using high-dimensional embeddings and spherical statistical models, it organizes semantic knowledge into a geometrically coherent hierarchy. Each terminal leaf node acts as an independent evaluation arena, hosting LLM-judge pairwise comparisons and maintaining local model leaderboards fitted with the Bradley-Terry model.

> **Implementation status:** all pipeline layers are green and the codebase builds cleanly. The canonical experiment configuration lives at [`../experiment_configs/thesis_canonical.toml`](../experiment_configs/thesis_canonical.toml).

---

## Sitemap

The documentation is organized into six functional areas, mirroring the system architecture.

### 1. Core Concepts — [`core-concepts/`](core-concepts/)
Fundamental models, design paradigms, and data representations.
- [Taxonomy DAG Paradigm](core-concepts/taxonomy-dag.md) — union-based topological paradigm and polyhierarchy design.
- [Data Representations](core-concepts/data-representations.md) — node, embedding, rating, and config data models.

### 2. Evolutionary Pipeline — [`evolutionary-pipeline/`](evolutionary-pipeline/)
The lifecycle of the self-organizing taxonomy engine.
- [Pipeline Overview](evolutionary-pipeline/overview.md) — end-to-end flow from query distillation to snapshot convergence.
- [vMF Fitting](evolutionary-pipeline/fitting-vmf.md) — modeling on the unit sphere, concentration estimation, small-sample bias correction.
- [Trickle Routing](evolutionary-pipeline/trickle-routing.md) — top-down restrictive soft routing with log-space temperature-scaled softmax.
- [Discovery & Optimization](evolutionary-pipeline/discovery-optimization.md) — sibling merging, adaptive splitting via Dasgupta cost delta, transitive reduction.

### 3. Arena Evaluations — [`arena-evaluations/`](arena-evaluations/)
Adjudication of agent outputs and statistical model ranking.
- [Judge Design](arena-evaluations/judge-design.md) — LLM pairwise judge prompting, contrastive rubric synthesis, context-aware grading.
- [Bradley-Terry Fit](arena-evaluations/bradley-terry-fit.md) — pairwise leaderboards via Minorization-Maximization, confidence intervals.
- [Active Matchmaking](arena-evaluations/active-matchmaking.md) — information-theoretic scheduling via binary-entropy maximization.

### 4. Metrics & Validation — [`metrics-validation/`](metrics-validation/)
Statistical checks on taxonomic quality, classification correctness, and structural balance.
- [Clustering Metrics](metrics-validation/clustering-metrics.md) — cosine silhouette, fuzzy/overlapping NMI (LFK 2009), Dasgupta cost.
- [Classification Metrics](metrics-validation/classification-metrics.md) — hierarchical F1 (Kosmopoulos 2014), exact-match ancestor rate.
- [Structural Metrics](metrics-validation/structural-metrics.md) — avg match count, contamination ratio, normalised Sackin index.

### 5. System Architecture — [`system-architecture/`](system-architecture/)
Implementation, integration, and database operation details.
- [Spring Integration](system-architecture/spring-integration.md) — component structure, dependency injection, transaction layout.
- [Database Concurrency](system-architecture/database-concurrency.md) — threading model, SQLite WAL, connection pooling.
- [TUI Dashboard](system-architecture/tui-dashboard.md) — layout, terminal controls, visualizer panel.
- [Headless Experimentation](system-architecture/headless-experimentation.md) — headless CLI runner, TOML/JSON config, condition matrix, CSV/JSON exporters.

### 6. Paper & Guides — [`paper/`](paper/) · [`guides/`](guides/)
Thesis-facing material and reproduction walkthroughs.
- [Mathematical Foundations](paper/MATHEMATICAL_FOUNDATIONS.md) — §3–5: statistical and geometric basis (vMF, NiW/OAS, Dasgupta, MRL, OpenSkill).
- [Evaluation Metrics](paper/EVALUATION_METRICS.md) — §6 metric-to-table mapping and implementation status.
- [Empirical Plan](paper/EMPIRICAL_PLAN.md) — experiment design and ablation schedule.
- [Reproducibility](paper/REPRODUCIBILITY.md) — artifact checklist.
- [Publication Hygiene](paper/PUBLICATION_HYGIENE.md) — citations, licensing, ethics, limitations.
- [Thesis Reproduction Guide](guides/thesis-reproduction.md) — end-to-end replication protocol.
- [Eval-Results ZIP Schema](guides/eval-results-zip-schema.md) — precomputed-evaluation ingestion format.

### Archive — [`archive/`](archive/)
Legacy designs and development notes, retained for history. Not authoritative — the live docs above supersede anything here.
- [`archive/legacy/`](archive/legacy/) — former `docs-old/` graveyard (old architecture, phase, and arena notes).

---

## Codebase Quick Reference

Primary classes and services for developers working with the implementation (paths relative to repo root):

- **Taxonomy Pipeline**
  - [`TaxonomyEngine`](../src/main/kotlin/taxonomy/TaxonomyEngine.kt) — orchestrates the lifecycle phases.
  - [`TaxonomyFitter`](../src/main/kotlin/taxonomy/operations/TaxonomyFitter.kt) — vMF fitting, parent-average prior, d/N shrinkage.
  - [`TaxonomyTrickler`](../src/main/kotlin/taxonomy/operations/TaxonomyTrickler.kt) — trickle routing, residual routing, leaf assignment.
  - [`TaxonomySplitter`](../src/main/kotlin/taxonomy/operations/TaxonomySplitter.kt) — k-ary vMF-k-means splits, Dasgupta delta gate.
  - [`TaxonomyMerger`](../src/main/kotlin/taxonomy/operations/TaxonomyMerger.kt) — sibling merges, cross-links, transitive reduction, bridging.
- **Arena & Benchmarking**
  - [`TaxonomyBenchmarkService`](../src/main/kotlin/taxonomy/service/TaxonomyBenchmarkService.kt) — active matchmaking and round evaluations.
  - [`TaxonomyRankingService`](../src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt) — ratings and match persistence.
  - [`BtMatchScheduler`](../src/main/kotlin/taxonomy/service/BtMatchScheduler.kt) — informative-match scheduling.
  - [`BtStoppingPolicy`](../src/main/kotlin/taxonomy/service/BtStoppingPolicy.kt) — leaf/round convergence.
  - [`BtMmFitter`](../src/main/kotlin/taxonomy/service/BtMmFitter.kt) — Bradley-Terry MM updates.
  - [`HeadlessBenchmarkRunner`](../src/main/kotlin/taxonomy/runner/HeadlessBenchmarkRunner.kt) — headless CLI batch entrypoint.
- **Statistical Utilities**
  - [`StatisticsUtils`](../src/main/kotlin/taxonomy/utils/StatisticsUtils.kt) — vMF, log-Bessel ratios, Dasgupta delta, PCA.
  - [`TaxonomyMetrics`](../src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt) — classification, clustering, and structural metrics.
