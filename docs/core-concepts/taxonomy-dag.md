# The Union-Based Topological Paradigm & Polyhierarchy

This document details the theoretical and mathematical foundations of the taxonomy structure in **TaxoArena**. Specifically, it contrasts traditional taxonomy induction paradigms with the **Union-Based Topological Paradigm (Composite GMM)** and describes the **Polyhierarchical DAG** design.

---

## 1. Traditional vs. Union-Based Paradigms

Traditional hierarchical clustering and taxonomy induction systems typically employ "enveloping" or "hierarchical wrapping" distributions. Under that approach, a parent node $P$ is modeled by fitting a single broad distribution (e.g., a high-variance Gaussian) that spans the space containing all its children's centroids:

$$ P(x \mid P) = \mathcal{N}(x \mid \mu_P, \Sigma_P) $$

In high-dimensional embedding spaces ($d=4096$ for Qwen3-Embedding), this approach fails due to the **curse of dimensionality** and the creation of **semantic voids**. A semantic void is a region of statistical inclusion (where the probability density $P(x \mid P)$ is high) that is completely devoid of semantically relevant queries. The parent distribution "fills" the empty space between children, incorrectly classifying unrelated out-of-distribution queries as members of the parent category.

### The Composite Distribution Paradigm (Composite GMM)

To resolve the issue of semantic voids, **TaxoArena** utilizes the **Composite Distribution** paradigm:
*   **Parent Identity by Union**: An internal parent node $P$ has no independent parameters (like a standalone mean or covariance). Instead, its distribution $\mathcal{D}_P$ is defined strictly by the recursive union of its children's localized distributions $\{C_1, C_2, \dots, C_m\}$:
    
    $$ \mathcal{D}_P = \bigcup_{i=1}^{m} \mathcal{D}_{C_i} $$
    
*   **Precision Boundaries**: By treating the parent as a "Composite Gaussian Mixture Model" (Composite GMM), we ensure that the parent boundary fits the child sub-spaces exactly. If a query lies in the empty space between child distributions, it is rejected by the trickle router rather than absorbed.
*   **Recursive Definition**: This ensures that parent nodes represent the exact semantic footprint of their descendent leaves and no more, maintaining high precision throughout the hierarchy.

---

## 2. Polyhierarchy & Cross-Linking

A strict tree hierarchy (where each node has exactly one parent) cannot capture the multidimensional nature of human knowledge. Many scientific queries belong to the intersection of multiple fields. For example, a query on "Quantum Computing" resides between "Computer Science" and "Physics".

TaxoArena implements a **Directed Acyclic Graph (DAG)** topology allowing **polyhierarchy**, where a node can have multiple parents.

### Topological Separation: Tree vs. Cross-Links

To maintain a clean structural skeleton for routing, TaxoArena distinguishes between two types of parent-child edges:
1.  **Tree Edges**: Stored in [GraphNode.children](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/model/GraphNode.kt). These define the primary hierarchical skeleton. A node has at most one tree parent, which is tracked via `GraphNode.treeParentId`.
2.  **Cross-Link Edges**: Stored in [GraphNode.crossLinkChildren](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/model/GraphNode.kt). These define the secondary polyhierarchical relationships.

> [!IMPORTANT]
> A critical bug fix (resolved in PR #46) separates cross-link edges from primary tree child edges. If cross-links were added to `children`, it would cause `isLeaf = children.isEmpty()` to evaluate to `false` for terminal nodes that receive cross-links, preventing the trickle router from identifying them as active evaluation arenas. Maintaining `crossLinkChildren` separately ensures tree leaves remain recognized as leaves.

### Evaluation and Insertion of Cross-Links

Cross-links are evaluated and inserted in a dedicated pass within the [TaxonomyMerger](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyMerger.kt):
1.  **Eligibility**: A node $N$ and a potential parent $P$ are eligible for cross-linking if:
    *   $N \neq P$
    *   $P$ is not an ancestor of $N$, and $N$ is not an ancestor of $P$ (preventing cycles).
    *   The depth difference satisfies $\text{depth}(N) - \text{depth}(P) \le 3$.
    *   They do not share the same depth-1 ground-truth ancestor.
2.  **Voting Mechanism**: Let $Q_N$ be the set of queries assigned to $N$, and $d_N, d_P$ be the embedding projection dimensions of $N$ and $P$. For each query $q \in Q_N$, we project the query vector $x$ onto $d_N$ and $d_P$, yielding $x_N$ and $x_P$.
3.  We calculate the dot product of these projections with the respective cluster mean directions $\mu_N$ and $\mu_P$:
    
    $$ \cos_N = x_N^T \mu_N, \quad \cos_P = x_P^T \mu_P $$
    
4.  A cross-link from $P$ to $N$ is created if a majority of queries (at least $50\%$) show a substantial cosine similarity shift towards $P$'s mean vector:
    
    $$ \cos_P - \cos_N > 0.05 $$
    
    When this holds, $P$ is added to $N$'s `parents` set, and $N$ is added to $P$'s `crossLinkChildren` set.

---

## 3. Transitive Reduction

Polyhierarchy can introduce redundant edges. For instance, if there exist edges $A \to B$, $B \to C$, and a direct edge $A \to C$, the direct edge is redundant because the relationship is already transitively captured via $B$.

TaxoArena runs a **transitive reduction** post-pass inside [TaxonomyMerger.transitiveReduction](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyMerger.kt):
*   For each node $C$, we collect its parent set.
*   We construct an ancestor map listing all ancestors for every node in the DAG.
*   If parent $P_1$ is an ancestor of another parent $P_2$ (meaning $P_1 \in \text{Ancestors}(P_2)$), then the direct edge $P_1 \to C$ is redundant and is severed.
*   **Protection**: Tree parent edges (where $P_1.\text{id} == C.\text{treeParentId}$) are never removed, preserving the fundamental taxonomy tree.

---

## 🔗 Related Code References
*   [GraphNode](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/model/GraphNode.kt): Node data class.
*   [TaxonomyMerger](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyMerger.kt): Contains the cross-linking and transitive reduction implementations.
