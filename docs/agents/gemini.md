# ArcTaxoAdapat Project Mandates & Implementation Hub

## Project Overview
**ArcTaxoAdapat** is an advanced classification system that organizes continuously expanding semantic knowledge into a **Dynamic Hierarchical Directed Acyclic Graph (DAG)**. Unlike traditional flat or tree-based taxonomies, this system allows for polyhierarchical relationships and utilizes state-of-the-art statistical modeling to maintain stability and scalability in 4096-dimensional embedding spaces.

## Core Architectural Implementation
For a deep dive into the math and logic behind each part of the system, refer to the following documentation:

### [1. Topological Paradigms](../architecture/topological-paradigms.md)
*   **DAG Structure**: Support for polyhierarchical relationships.
*   **Union-Based Domain Definition**: Eliminating the "semantic void" via composite GMMs.

### [2. Phase 2: Fit (Context-Aware Distribution Modeling)](../phases/phase2-fitting.md)
*   **Hierarchical Mixture Modeling (HMM)**: Multi-centroid GMM representations.
*   **Oracle Approximating Shrinkage (OAS)**: Well-conditioned 4096-D covariance estimation.
*   **Simplified Isolation Kernel (SIK)**: Non-parametric leaf inclusion envelopes.

### [3. Phase 3: Trickle (Top-Down Restrictive Routing)](../phases/phase3-trickle.md)
*   **Multi-Component GMM Routing**: Regularized Mahalanobis distance logic.
*   **The Restrictive Funnel**: Depth-decayed confidence intervals and Chi-Square thresholding.
*   **Outlier Retention**: Parent-level residual pools for emergent concept discovery.

### [4. Phase 4: Discover (Adaptive Splitting)](../phases/phase4-discovery.md)
*   **Angular DBSCAN**: Density-based clustering using Cosine distance.
*   **Knee Detection**: Automated Epsilon tuning for high-dimensional clusters.
*   **LLM Synthesis**: Recursive Thematic Partitioning (RTP) for label generation.

### [5. Phase 5: Optimize (Structural Refinement)](../phases/phase5-optimization.md)
*   **Global Redundancy Merging**: Fusing overlapping domains across branches.
*   **Polyhierarchical Reparenting**: Specificity-guarded cross-linking using Semantic Volume.
*   **Transitive Reduction**: Enforcing DAG purity and eliminating topological shortcuts.

### [6. Phase 6: Stabilize (Convergence of the Mixture)](../phases/phase6-stabilization.md)
*   **Thermodynamic Annealing**: Iterative cooling of the taxonomy structure.
*   **Convergence Metrics**: Semantic Volume minimization and GED error plateaus.

## Engineering Standards

### Core Principle: Geometric Coherence Priority
*   **Geometric Priority**: The physical clustering and statistical layout (geometric repartition and mathematical fitting of nodes in the high-dimensional embedding space) is the primary driver of DAG construction.
*   **Adaptive Granularity**: Depending on the concentration of closely related queries, the granularity dynamically scales (high-density areas receive deeper, narrower concept subdivisions, while low-density areas remain coarser).
*   **Non-Blocking Diagnostics**: While tree metrics and calibration functions are crucial diagnostic tools to identify anomalies, they must never act as hard-blocking constraints that obstruct or distort the mathematically true representation of the queries' natural geometry in the 4096-D embedding space.

### Coding Conventions
*   **Language**: Kotlin (JVM).
*   **Math**: Optimized linear algebra in `StatisticsUtils.kt`.
*   **Concurrency**: Coroutine-based parallel processing of DAG nodes.
*   **Logging**: Detailed algorithm tracing in `algorithm_trace.log`.
*   **Configuration**: Global hyperparameters defined in `TaxonomyConfig.kt`.

### Implementation Source Map
*   `src/main/kotlin/taxonomy/DataModels.kt`: Core graph and statistical data structures.
*   `src/main/kotlin/taxonomy/StatisticsUtils.kt`: Mathematical implementations (OAS, Mahalanobis, SIK, DBSCAN).
*   `src/main/kotlin/taxonomy/operations/`: Individual phase implementations:
    *   `TaxonomyFitter.kt`: Phase 2 (Fitting).
    *   `TaxonomyTrickler.kt`: Phase 3 (Trickling).
    *   `TaxonomySplitter.kt`: Phase 4 (Discovering).
    *   `TaxonomyMerger.kt`: Phase 5 (Optimizing).
*   `src/main/kotlin/taxonomy/TaxonomyEngine.kt`: The main adaptation orchestrator.
