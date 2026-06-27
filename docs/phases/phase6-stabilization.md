# Phase 6: Stabilize (Convergence of the Mixture)

## 1. Thermodynamic Convergence
ArcTaxoAdapat runs an iterative adaptation loop (default 5 iterations) to refine the taxonomy's structure. Stability is achieved when the structural and statistical changes between iterations approach zero.

### 1.1 Thermodynamic Annealing
The system applies an `annealingAlpha` (default 1.05) to its hyperparameters across iterations, cooling the "thermal motion" of the taxonomy as it settles into a stable configuration.

### 1.1 Centroid Stabilization (EMA)
The system prevents radical shifts in semantic boundaries by applying an **Exponential Moving Average (EMA)** to the GMM centroids and weights during the fitting phase. This ensures that new data points gradually adapt the domain's statistical identity rather than causing volatile re-configurations.
$$ \mu_{t} = (1 - \alpha) \mu_{t-1} + \alpha \mu_{new} $$
Where $\alpha$ (default 0.7) controls the adaptation rate.

### 1.2 Persistence Bias (Conceptual Inertia)
To eliminate query "oscillation" between highly similar nodes, the trickle phase incorporates a **Persistence Bias**. If a query was assigned to a specific node in the previous iteration, its Mahalanobis distance to that node is scaled by a stability factor (0.8), creating a mathematical "staying" preference.

## 2. Convergence Metrics

### 2.1 Graph Edit Distance (GED)
Structural stability is measured by the delta in the number of nodes, parents, and children between iterations. When the relative GED error plateaus, the topology is considered converged.

### 2.2 Semantic Volume Minimization
The system tracks the **Total Log-Semantic Volume** across all leaf nodes.
$$ \mathcal{V} = \sum_{L \in \text{Leaves}} \sum_{k=1}^{K} \pi_k \log(\text{det}(\Sigma_{k})) $$
Convergence is reached when the total volume reaches a local minimum, signifying that the semantic clusters have been tightly packed into the most granular and distinct sub-domains possible without losing coverage of the total query space.

## 3. The Algorithmic Loop
The complete orchestration cycle follows these steps:
1.  **Extract**: Precompute embeddings and seed initial domains.
2.  **Fit**: Bottom-Up GMM and OAS modeling.
3.  **Bootstrap**: Initial splitting of ground-truth domains to discover internal structure.
4.  **Trickle (Main Loop)**: Global reset and top-down routing of queries.
5.  **Discover**: DBSCAN-driven centroid bifurcation in unmapped pools.
6.  **Optimize**: Parenting, merging, and transitive reduction.
7.  **Refit**: Final adjustments of boundaries.
8.  **Terminate**: Final trickling and stabilization check.
