# Clustering Quality Metrics: Spherical Silhouette, NMI, and Dasgupta Cost

This document details the mathematical formulations and implementation status of clustering quality metrics in **TaxoArena**, focusing on spherical geometry, overlapping partitions, and hierarchical tree validation.

---

## 1. Spherical Silhouette Coefficient

Standard Silhouette coefficients utilize Euclidean distance. For high-dimensional embeddings L2-normalized onto the unit sphere, cosine-based angular distances are geometrically appropriate.

### Angular Distance Formulation
For two unit vectors $x, y \in S^{d-1}$, we define their angular distance as:

$$ d_{\theta}(x, y) = \arccos(x^T y) $$

where $x^T y \in [-1.0, 1.0]$ is the cosine similarity.

### Silhouette Score Calculation
For each query embedding $x$ in the dataset:
1.  We identify its assigned cluster $A$ and calculate the angular distance to its centroid $\mu_A$:
    
    $$ a(x) = \arccos(x^T \mu_A) $$
    
2.  We find the nearest neighboring cluster $B \neq A$ and calculate the angular distance to its centroid $\mu_B$:
    
    $$ b(x) = \min_{B \neq A} \arccos(x^T \mu_B) $$
    
3.  The spherical silhouette score $s(x)$ for the query is:
    
    $$ s(x) = \frac{b(x) - a(x)}{\max(a(x), b(x))} $$
    
    If $\max(a(x), b(x)) = 0$, then $s(x) = 0.0$.

The overall **Spherical Silhouette** is the mean $s(x)$ across all queries:

$$ \bar{S} = \frac{1}{n} \sum_{i=1}^n s(x_i) $$

Values range within $[-1.0, 1.0]$. A positive value close to $1.0$ indicates that queries are tightly aligned with their cluster centroids and well-separated from neighboring domains. This is implemented in [StatisticsUtils.calculateSphericalSilhouette](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt).

---

## 2. Normalized Mutual Information (NMI)

Standard NMI assumes a flat, hard partition where each query is assigned to exactly one domain. In a polyhierarchical DAG, queries can be assigned to multiple leaf nodes. Standard NMI penalizes this overlap as error.

To evaluate overlapping assignments, TaxoArena originally implemented the **Lancichinetti–Fortunato–Kértesz (LFK 2009)** overlapping NMI:

$$ NMI_{\text{ovlp}}(X, Y) = 1.0 - \frac{1}{2} \left[ H(X \mid Y) + H(Y \mid X) \right] $$

> [!WARNING]
> **LFK-NMI Mathematical Degeneracy:**
> Under fine-grained hierarchies (e.g. 134 tiny leaves over 8016 queries), LFK-NMI suffers from a known mathematical degeneracy. The LFK formulation guards each pairwise conditional entropy with the constraint $h(P_{11}) + h(P_{00}) \ge h(P_{10}) + h(P_{01})$, otherwise defaulting to the marginal. With tiny leaves (each $\approx 1\%$ of $n$), $P_{00} \approx 1 \implies h(P_{00}) \approx 0$ and the asymmetric residue term dominates, causing this constraint to fail for almost every pair. Thus, both normalized conditional entropies default to 1, forcing $NMI_{\text{ovlp}} = 1 - 0.5(1 + 1) = \text{exactly } 0.0$.
>
> **Solution:** TaxoArena collapses the predicted assignments to their depth-1 ancestors (matching the 13 MMLU-Pro ground truth categories) and computes the standard **Shannon NMI** (with geometric-mean normalization) on these collapsed partitions, ensuring a robust, non-degenerate clustering quality measure.

---

## 3. Total Dasgupta Cost

The **Dasgupta Cost** (Dasgupta 2016) is a theory-grounded metric for evaluating hierarchical clustering structures.

### Mathematical Formulation
Given a similarity matrix $W$, where $w_{ij} \ge 0$ is the cosine similarity between query $i$ and query $j$, the cost of a hierarchical tree $T$ is defined as:

$$ \text{Cost}(T) = \sum_{i < j} w_{ij} \cdot \left| \text{Leaves}(T(i, j)) \right| $$

where:
*   $T(i, j)$ is the lowest common ancestor (LCA) node of query $i$ and query $j$ in the tree.
*   $\left| \text{Leaves}(T(i, j)) \right|$ is the count of terminal leaf nodes descending from that LCA.

### Interpretation
Dasgupta's cost formalizes the intuition that similar items should split as deep in the tree as possible. If two highly similar queries ($w_{ij} \approx 1.0$) split at the root, their LCA is the root node, and they are penalized by the total leaf count of the entire tree. If they split near the leaves, their LCA has few descendant leaves, resulting in a low penalty.

A lower Total Dasgupta Cost indicates a more structurally coherent hierarchy. This provides a gold-standard, dataset-independent quality measure that enables cross-system comparison.

---

## 🔗 Related Code References
*   [StatisticsUtils](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt): Computes spherical silhouette and the local Dasgupta split delta.
*   [TaxonomyMetrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt): Computes overall quality metrics for the final reports.
