# Hierarchical Mixture Foundations for Semantic Taxonomy Adaptation

This document details the refined mathematical framework for **ArcTaxoAdapat**, a system that organizes semantic knowledge into a Dynamic Hierarchical Directed Acyclic Graph (DAG) using Hierarchical Mixture Models (HMM) and high-fidelity query distillation.

## 1. The Union-Based Topological Paradigm
Traditional taxonomies use "enveloping" distributions where a parent node fits a single broad Gaussian to cover its children. This creates "semantic voids"—regions of statistical inclusion that lack semantic relevance.

**ArcTaxoAdapat** utilizes a **Composite Distribution** paradigm:
*   **Parent Identity**: A parent node $P$ is mathematically defined strictly by the union of its children's localized distributions $\{C_1, C_2, \dots, C_m\}$.
*   **Precision**: By treating the parent as a "Composite GMM," the system preserves the high-precision boundaries of sub-domains within the macro-space, eliminating voids.

---

## 2. Phase 1: Semantic Distillation & Seeding
To maximize signal-to-noise ratio in 4096-D embedding space, the system performs **Semantic Distillation**:
*   **Taxonomic Signatures**: Raw queries (linguistically noisy) are processed by an LLM to extract 3-5 core technical keywords (e.g., "value chain, primary activities").
*   **Denoising**: This distillation removes conversational filler and question markers, resulting in "point-like" embeddings that form much tighter, more stable statistical clusters.
*   **Bootstrap Seeding**: Initial domains are seeded with 100% ground-truth data. This ensures that the first generation of Gaussians covers the entire intended semantic range of the dataset labels.

---

## 3. Phase 2: Fit (OAS-GMM Modeling)
### 3.1 Leaf Node Modeling: Multi-Centroid OAS
A terminal leaf node $L$ is modeled as a small-scale Gaussian Mixture Model (GMM):
$$ P(x | L) = \sum_{k=1}^{K} \pi_k \mathcal{N}(x | \mu_k, \Sigma_k) $$
*   **Oracle Approximating Shrinkage (OAS)**: Covariance matrices $\Sigma_k$ are estimated using OAS to ensure they are well-conditioned and positive-definite in high dimensions ($d=4096$).
*   **Diagonal Fidelity**: The system uses the diagonal of the OAS estimator to prioritize the unique semantic "energy" of each keyword dimension.

### 3.2 Parent Node Modeling: Recursive Union
An internal node $P$ has no independent parameters. Its distribution is the union of its children’s mixture components:
$$ \mathcal{D}_P = \bigcup_{i=1}^{m} \mathcal{D}_{C_i} $$
This recursive definition ensures that a parent node is exactly as broad as its children, and no broader.

---

## 4. Phase 3: Trickle (The Restrictive Funnel)
### 4.1 Normalized Mahalanobis Routing
In high-dimensional space, raw Mahalanobis distance ($D_M^2$) is brittle. ArcTaxoAdapat uses **Dimension-Normalized Distance**:
$$ \bar{D}_M^2 = \frac{1}{d} \sum_{i=1}^{d} \frac{(x_i - \mu_i)^2}{\sigma_i^2} $$
This normalization (where the expected value is 1.0) makes the Chi-Square bounds ($ \chi^2 / d $) stable across different embedding models.

### 4.2 Ground-Truth Immunity & Safety Valves
To prevent the "shrinking core" effect and preserve dataset magnitudes:
*   **Immunity Gate**: If a query is being evaluated against the branch it was originally part of, it is **ALWAYS inclusive**.
*   **Transparent Root**: The Root node (depth 0) is always inclusive, acting as a router rather than a filter.
*   **Depth-Decayed Funnel**: Confidence $\alpha$ narrows exponentially as queries descend ($0.999 \to 0.90$), making leaf nodes naturally more exclusive than macro-domains.

---

## 5. Phase 4: Discover (Centroid Bifurcation)
When a parent's residual pool $U_P$ (queries that fit the macro-domain but no specific child) reaches a density threshold, the system triggers **Discovery**:
*   **Angular DBSCAN**: Uses Cosine distance to identify cohesive sub-clusters in the residual space.
*   **LLM Synthesis**: New clusters are sent to the LLM for taxonomic labeling, spawning new child nodes and expanding the DAG.

---

## 6. Phase 5: Optimize (Topological Polish)
*   **Component Merging**: Overlapping GMM components (Similarity $> \tau_{merge}$) are fused to prevent linear complexity explosion.
*   **Transitive Reduction**: The DAG is swept to remove redundant edges (e.g., if $A \to B$ and $B \to C$, the shortcut $A \to C$ is severed), ensuring a clean hierarchy.

---

## 7. Phase 6: Stabilize (Convergence)
Stability is achieved when the **Total Log Semantic Volume** (sum of covariance determinants across all leaf GMMs) reaches a local minimum.
*   **Volume Minimization**: As iterations progress, the GMMs "tighten" around the distilled keywords.
*   **Equilibrium**: The process terminates when query migrations between domains drop to zero, signaling that each query has found its semantically optimal "home."
