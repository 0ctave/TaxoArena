# Phase 5: Optimize (Structural Refinement)

## 1. Global Redundancy Merging
ArcTaxoAdapat performs a global sweep of the DAG to identify and fuse semantically redundant domains across different branches.

### 1.1 GMM Similarity
Similarity between two nodes is calculated using a **Hausdorff-like symmetric approximation** of the GMMs. This approach preserves multi-modal identities and compares the closest matching component centroids.
If the similarity exceeds the `tauMerge` threshold (default 0.92), the nodes are fused into a single domain.

## 2. Polyhierarchical Cross-Linking (Reparenting)
The system creates cross-links between branches to optimize the DAG topology.

### 2.1 Specificity Guard
A node $N$ can only be cross-linked as a child to a potential parent $P$ if $P$ is "broader" than $N$. This is enforced by comparing the **Log-Semantic Volume** ($\sum \log \sigma^2$) of their respective GMM distributions. A parent must have a larger semantic volume (representing more conceptual breath) to justify the hierarchical relationship.

### 2.2 Angular Inclusion
If the angular similarity between the child node's centroid and the parent's distribution exceeds the `tauReparent` threshold (default 0.82) and the child's centroid mathematically falls within the parent's Chi-Square bounds, a new parent-child edge is created.

## 3. Transitive Reduction
To ensure a pure DAG topology and eliminate topological paradoxes created by splitting and merging, the system performs a global **Transitive Reduction**.
If a node has a direct link to parent $P_1$, and also a link to parent $P_2$, but $P_2$ is a descendant of $P_1$, the direct "shortcut" link from $P_1$ is severed. This enforces the principle of **Maximum Specificity**, ensuring that queries are mapped through the most granular path available.

## 4. Pruning
After topological restructuring, any terminal leaf nodes that have become empty (zero queries) are pruned from the graph to maintain a lean and efficient taxonomy.
