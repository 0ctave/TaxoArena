# Phase 4: Discover (Adaptive Splitting)

## 1. Centroid Bifurcation
When the density of the residual query pool $U_P$ in a parent node exceeds the `splitBaseThreshold`, ArcTaxoAdapat triggers a "Discovery" phase to identify emergent sub-concepts.

## 2. Advanced Angular DBSCAN
The system performs high-dimensional density-based clustering (DBSCAN) using **Cosine Distance**.

### 2.1 Mathematical Knee Detection
To auto-tune the Epsilon ($\epsilon$) radius for DBSCAN, the system calculates the point of **Maximum Orthogonal Curvature** (the "Knee") on the sorted $k$-distance graph of the residual pool. This mathematically separates dense cluster inliers from sparse spatial noise.

### 2.2 Epsilon Relaxation (Macro-Concept Formation)
*   **Leaves**: Use the strict Knee-detected $\epsilon$ to ensure highly granular sub-domains.
*   **Parents/Root**: Relax the radius to the mean of $k$-distances. This allows for the formation of broader macro-concepts, effectively "draining" the root node of sparse outliers.

## 3. Semantic Synthesis via LLM
Once dense clusters are identified, they are converted into new child nodes through **Recursive Thematic Partitioning (RTP)**.

### 3.1 Representative Sample Selection
The system selects a diverse set of representative queries for the LLM:
*   **Central Queries**: Samples closest to the cluster's angular centroid.
*   **Boundary Queries**: Samples at the cluster's periphery to provide grounding for the domain's limits.

### 3.2 Label Synthesis
The LLM (`TaxoExpander` agent) evaluates these samples within the context of the parent's label, the existing sibling labels, and the branch's historical lineage. This ensures that the generated label is stylistically consistent and semantically distinct from its neighbors.

## 4. Constraints on Splitting
*   **Max Depth Boundary**: No splits occur beyond the `maxDepth` limit (default 5).
*   **Relative Max Size**: A new cluster cannot encompass more than a certain percentage (`relativeMaxSize`, default 0.9) of its parent's pool to prevent a single child from overwhelming the branch's identity.
