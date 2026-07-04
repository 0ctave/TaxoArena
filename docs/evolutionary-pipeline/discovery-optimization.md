# Discovery and Topological Optimization

This document details the mechanics of domain splitting, component merging, passthrough collapsing, and structural pruning that refine the taxonomy DAG in **TaxoArena**.

---

## 1. Adaptive Splitting (Centroid Bifurcation)

When the query count of a leaf node $N$ exceeds a density threshold (typically $2 \times N_{min}$, where $N_{min}$ is the minimum cluster size, default $20$), the node becomes a candidate for splitting.

### Dimensionality Projection (Power Iteration PCA)
Raw vectors are in 4096-D. To compute stable statistical boundaries and avoid covariance singularities, we project vectors into a lower-dimensional subspace $d \in \{32, 64, 128\}$ based on query count.

TaxoArena implements a lightweight **Power Iteration PCA** in [StatisticsUtils.pcaProject](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt) that does not require LAPACK:
1.  Subtract the empirical mean vector to center the data.
2.  Iteratively extract the top eigenvectors.
3.  Project the centered data onto the top-$k$ components and re-normalize onto the unit sphere.

### Spherical k-Means (vMF EM)
Once projected, we initialize cluster centers using k-means++ adapted to cosine distance on the sphere. We then run a spherical Expectation-Maximization (EM) algorithm to fit a mixture of $k$ von Mises-Fisher components. Sibling components are updated until convergence.

### k-Selection and Dasgupta Cost Delta Validation
To determine the optimal number of child nodes $k \in \{2, 3, 4\}$, we calculate the **Dasgupta Cost Delta** ($\Delta$).

We define a cluster dissimilarity proxy $W(S)$ for a set of unit-norm vectors $S$:

$$ W(S) = N_S^2 - \left\| \sum_{x \in S} x \right\|_2^2 $$

This proxy is always $\ge 0$. It is $0$ if all vectors in $S$ are identical and grows larger as vectors diverge. The before-split and after-split costs are defined as:

$$ C_{\text{before}} = n \cdot W(S_{\text{all}}) $$

$$ C_{\text{after}} = \sum_{c=1}^{k} (n - n_c) W(S_c) $$

where $n_c$ is the query count of cluster $c$, and $n = \sum n_c$. The normalized delta is:

$$ \Delta = 1.0 - \frac{C_{\text{after}}}{C_{\text{before}}} $$

We try $k=2, 3, 4$. We select the largest $k$ whose Dasgupta Delta improves by at least the separation epsilon ($\epsilon_{\text{separation}} = 0.05$) over the previous $k-1$ candidate:

$$ \Delta_k - \Delta_{k-1} \ge \epsilon_{\text{separation}} $$

If even $k=2$ fails to yield $\Delta \ge \epsilon_{\text{separation}}$ (or if a split would result in any cluster falling below $N_{min}$), the split is rejected and the node remains a leaf.

---

## 2. Sibling Merging (JS-Divergence)

If two child nodes $A$ and $B$ under the same parent share highly similar query distributions, they are merged.

### von Mises-Fisher Jensen-Shannon Divergence
We measure sibling similarity using a vMF-adapted Jensen-Shannon Divergence. Let $\mu_A, \kappa_A$ and $\mu_B, \kappa_B$ be the parameters of the two components. We project them to their lowest common dimension $d$ and compute:

$$ D_{\text{JS}}(A, B) = \frac{1}{2} \left[ \kappa_A A_d(\kappa_A) (1.0 - \mu_A^T \mu_B) + \kappa_B A_d(\kappa_B) (1.0 - \mu_B^T \mu_A) \right] $$

where $A_d(\kappa) = \frac{I_{d/2}(\kappa)}{I_{d/2-1}(\kappa)}$ is the Bessel ratio.

If $D_{\text{JS}}(A, B) < \epsilon_{\text{separation}}$, the nodes are merged:
*   Queries are combined.
*   The mean direction is updated by a weighted sum:
    
    $$ \mu_{\text{fused}} = \frac{n_A \mu_A + n_B \mu_B}{\|n_A \mu_A + n_B \mu_B\|_2} $$
    
*   The concentration is blended:
    
    $$ \kappa_{\text{fused}} = \frac{n_A \kappa_A + n_B \kappa_B}{n_A + n_B} $$
    
*   Parent and child edges are redirected to the fused node.

---

## 3. Passthrough Collapsing & Starvation Pruning

### Bypassing Passthrough Nodes
If a parent node $P$ has exactly one tree child $C$, and their statistical divergence is low ($D_{\text{JS}}(P, C) < \epsilon_{\text{separation}}$), $P$ acts as an unnecessary intermediate node. The system collapses $P$:
*   Child $C$ is re-parented directly under $P$'s parents.
*   Residual queries of $P$ are pushed down into $C$.
*   Node $P$ is deleted from the DAG.

### Starved Leaf Pruning
If a leaf $L$ contains few queries relative to its siblings:

$$ n_L < 0.2 \times \bar{n}_{\text{siblings}} \quad \text{and} \quad n_L < 5 $$

it is pruned. Its queries are re-absorbed by its tree parent node, and its edges are severed to preserve taxonomy precision.

---

## 🔗 Related Code References
*   [TaxonomySplitter](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomySplitter.kt): Implements PCA projection, vMF-k-Means, and Dasgupta split audits.
*   [TaxonomyMerger](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyMerger.kt): Handles JS-divergence merges, passthrough collapsing, and starved node pruning.
