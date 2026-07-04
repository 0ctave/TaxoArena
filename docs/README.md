# TaxoArena: Dynamic Hierarchical DAG Taxonomy for Model Evaluation

Welcome to the comprehensive documentation suite for **TaxoArena**, a self-organizing system that constructs a **Dynamic Hierarchical Directed Acyclic Graph (DAG)** taxonomy directly from MMLU-Pro evaluation queries. By leveraging high-dimensional embeddings and spherical statistical models, TaxoArena organizes semantic knowledge into a geometrically coherent hierarchy. Each terminal leaf node in this taxonomy acts as an independent evaluation arena, hosting LLM-judge pairwise comparisons and maintaining local model leaderboards fitted using the Bradley-Terry probabilistic model.

---

## 📖 Table of Contents & Sitemap

The documentation is organized into five core functional areas, mapping directly to the underlying architecture of the project:

### 1. [Core Concepts](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/core-concepts/)
Fundamental mathematical models, design paradigms, and data representation models.
*   **[Taxonomy DAG Paradigm](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/core-concepts/taxonomy-dag.md)**: Details the union-based topological paradigm and polyhierarchy design.
*   **[Data Representations](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/core-concepts/data-representations.md)**: Specifies the data models for nodes, embeddings, ratings, and execution configurations.

### 2. [Evolutionary Pipeline](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/evolutionary-pipeline/)
The lifecycle of the self-organizing taxonomy engine, divided into distinct execution phases.
*   **[Pipeline Overview](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/evolutionary-pipeline/overview.md)**: The end-to-end flow from query distillation to snapshot convergence.
*   **[von Mises–Fisher (vMF) Fitting](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/evolutionary-pipeline/fitting-vmf.md)**: Mathematical modeling on the unit sphere, concentration parameter estimation, and small-sample bias corrections.
*   **[Trickle Routing](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/evolutionary-pipeline/trickle-routing.md)**: Top-down restrictive soft routing with log-space temperature-scaled softmax.
*   **[Discovery & Optimization](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/evolutionary-pipeline/discovery-optimization.md)**: Sibling merging via JS-divergence, adaptive splitting via Dasgupta cost delta, and transitive reduction.

### 3. [Arena Evaluations](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/arena-evaluations/)
Adjudication of agent outputs and statistical model ranking.
*   **[Judge Design](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/arena-evaluations/judge-design.md)**: LLM pairwise judge prompting, contrastive rubric synthesis, and context-aware grading.
*   **[Bradley-Terry Fit](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/arena-evaluations/bradley-terry-fit.md)**: Solving pairwise leaderboards via Minorization-Maximization (MM) and computing confidence intervals.
*   **[Active Matchmaking](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/arena-evaluations/active-matchmaking.md)**: Information-theoretic scheduling using binary entropy maximization to minimize evaluation budget.

### 4. [Metrics & Validation](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/metrics-validation/)
Statistical checks to assess taxonomic quality, classification correctness, and structural balance.
*   **[Clustering Metrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/metrics-validation/clustering-metrics.md)**: Cosine silhouette, NMI (fuzzy/overlapping LFK 2009), and Dasgupta cost.
*   **[Classification Metrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/metrics-validation/classification-metrics.md)**: Hierarchical F1 (Kosmopoulos 2014) and Exact-Match Ancestor Rate (EMAR).
*   **[Structural Metrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/metrics-validation/structural-metrics.md)**: Avg match count, contamination ratio, and Normalised Sackin Index.

### 5. [System Architecture](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/system-architecture/)
Technical details of implementation, integration, and database operations.
*   **[TUI Dashboard](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/system-architecture/tui-dashboard.md)**: Layout, terminal controls, and visualizer panel representation.
*   **[Spring Integration](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/system-architecture/spring-integration.md)**: Component structure, dependency injection, and transaction layout.
*   **[Database Concurrency](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/system-architecture/database-concurrency.md)**: Threading model, SQLite WAL (write-ahead log) operations, and connection pooling.

### 6. [Legacy Documentation Archive](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/docs-old/)
Archive of old designs and development notes. See [docs/docs-old/old-README.md](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/docs/docs-old/old-README.md) for details.

---

## 🛠️ Codebase Quick Reference

For developers working directly with the implementation, these are the primary classes and services:

*   **Taxonomy Pipeline**:
    *   [TaxonomyEngine](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/TaxonomyEngine.kt): Orchestrates the lifecycle phases.
    *   [TaxonomyFitter](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyFitter.kt): Fits single-component vMF and NiW posteriors.
    *   [TaxonomyTrickler](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyTrickler.kt): Performs trickle routing.
    *   [TaxonomySplitter](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomySplitter.kt): Evaluates splits using k-ary vMF-k-Means.
    *   [TaxonomyMerger](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyMerger.kt): Handles JS-divergence sibling merges, cross-links, and transitive reduction.
*   **Arena & Benchmarking**:
    *   [TaxonomyBenchmarkService](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyBenchmarkService.kt): Handles active matchmaking and round evaluations.
    *   [TaxonomyRankingService](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt): Interface for persisting ratings and match results.
    *   [BtMatchScheduler](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMatchScheduler.kt): Schedules informative matches.
    *   [BtStoppingPolicy](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtStoppingPolicy.kt): Decides when leaves or rounds have converged.
    *   [BtMmFitter](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMmFitter.kt): Runs MM updates for Bradley-Terry parameters.
*   **Statistical Utilities**:
    *   [StatisticsUtils](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt): vMF, log-Bessel ratios, Dasgupta delta, and PCA.
    *   [TaxonomyMetrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt): Suite of classification, clustering, and structural metrics.
