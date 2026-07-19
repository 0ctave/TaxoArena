# Phase 4: Discover (Adaptive Splitting)

*Implemented in `TaxonomySplitter.kt`*

Discover performs a bottom-up BFS traversal of the DAG. At each node it decides whether to split the node's query set into \(k \geq 2\) child clusters using vMF-k-Means, validates the split with the Dasgupta cost delta, and if accepted creates and wires new child nodes.

---

## 1. Split Eligibility Guards

A node is skipped without evaluation if any of the following hold:

| Guard | Condition |
|-------|----------|
| Too few queries | `|queries| ≤ 2 × minClusterSize` |
| Max depth reached | `depth ≥ maxDepth` |
| Too diffuse and small | `κ < 0.5` and `|queries| < 10 × minClusterSize` |

---

## 2. PCA Pre-projection

To make k-Means tractable at large \(N\), queries are first projected to a low-dimensional PCA subspace before clustering:

| \(N\) | PCA target dim |
|-------|---------------|
| < 100 | 32 |
| < 500 | 64 |
| ≥ 500 | 128 |

The PCA projection is a heuristic pre-clustering step only. It determines cluster *identities* but not node *parameters*; child vMF parameters are always re-fit in the full MRL-dimension space (`childDim = dimForDepth(depth + 1)`).

---

## 3. k-Ary vMF-EM Mixture Selection

The optimal number of components \(k\) is selected via a two-stage marginal improvement criterion (`performVmfKMeans`):

**Stage 1 — probe:** run vMF-EM with `maxK = 2`. If \(k < 2\) components survive, the node is not split.

**Stage 2 — full run:** run vMF-EM with `maxK = 4`, falling back to the stage-1 result if the full run collapses.

The marginal criterion adds component \(k\) only if the normalized log-likelihood gain from \(k-1\) to \(k\) exceeds `separationEpsilon` (\(\varepsilon\)), preventing over-fragmentation.

### 3.1 k-Means++ Initialization

- \(\boldsymbol{\mu}_1\) = normalized centroid of all queries.
- \(\boldsymbol{\mu}_2, \ldots, \boldsymbol{\mu}_k\) = maximin cosine distance from existing centers (furthest-point seeding).

### 3.2 E-step (Log-Space Softmax)

\[
a_{ik} = \log \pi_k + \log C_d(\kappa_k) + \kappa_k\, \boldsymbol{\mu}_k^\top \hat{\mathbf{x}}_i
\]

Computed with \(\max_k a_{ik}\) subtraction for numerical stability.

### 3.3 M-step

\[
\pi_k^{\text{new}} = \frac{\sum_i r_{ik}}{N}, \qquad \boldsymbol{\mu}_k^{\text{new}} = \frac{\sum_i r_{ik}\,\hat{\mathbf{x}}_i}{\left\lVert\sum_i r_{ik}\,\hat{\mathbf{x}}_i\right\rVert_2}
\]
\[
\bar{R}_k = \frac{\left\lVert\sum_i r_{ik}\,\hat{\mathbf{x}}_i\right\rVert_2}{\sum_i r_{ik}}, \qquad \hat{\kappa}_k = \hat{\kappa}_{\text{MLE}}(\bar{R}_k, d, \lfloor\sum_i r_{ik}\rfloor)
\]

Convergence: \(|L^{(t+1)} - L^{(t)}| < 10^{-5}\) or 200 iterations. A collapse guard returns `null` if any soft count \(\sum_i r_{ik} < \varepsilon_{\min} \cdot N\).

---

## 4. Dasgupta Cost Delta Validation

After hard-assigning queries to their highest-responsibility cluster, the \(k\)-way Dasgupta cost delta is computed:

\[
\Delta = 1 - \frac{C_{\text{after}}}{C_{\text{before}}}, \qquad C(S) = \sum_{(i,j)} w_{ij} \cdot |S_{ij}|
\]

where \(w_{ij} = \hat{\mathbf{x}}_i^\top \hat{\mathbf{x}}_j\) clipped to \([0, 1]\) (cosine similarity) and \(|S_{ij}|\) is the subtree size at the shallow LCA. The split is accepted iff:

\[
\Delta \geq \varepsilon_{\text{req}}, \quad \text{where} \quad \varepsilon_{\text{req}} = \begin{cases} 2\varepsilon & |\text{queries}| < 2 N_{\min} \\ \varepsilon & \text{otherwise} \end{cases}
\]

> **Note:** the Dasgupta \(W\) proxy uses \(n_k^2 - \lVert\mathbf{s}_k\rVert^2\) (where \(\mathbf{s}_k = \sum_{i \in S_k}\hat{\mathbf{x}}_i\)) rather than the canonical \((\lVert\mathbf{s}_k\rVert^2 - n_k)/2\). This is internally consistent (monotone in the same direction), but absolute delta values differ from the theoretical Dasgupta cost and are not cross-system comparable.

---

## 5. Sibling Distinctness Guard

Before any children are created, each proposed child vMF \((\hat{\boldsymbol{\mu}}_j, \hat{\kappa}_j)\) is compared against every *existing* sibling of the node using vMF JS-divergence:

\[
D_{JS}^{vMF}(p \| q) = \frac{1}{2}D_{KL}(p\|m) + \frac{1}{2}D_{KL}(q\|m), \quad m = \tfrac{1}{2}(p+q)
\]

If any proposed child has \(D_{JS} < \varepsilon_{\text{sep}}\) with an existing sibling, the entire split is rejected.

---

## 6. Child Creation and Immediate Macro-Decomposition

Accepted clusters are converted to `GraphNode` objects. Each child:
- Receives a vMF fit in `childDim` space.
- Has its NiW posterior computed immediately via `fitter.fitSingleNode`.
- Receives an LLM-generated label from a stratified sample of its queries (inner core 30%, middle shell 50%, outer boundary 20%).

Any child with more than \(3 \times \text{threshold}\) queries is recursively split immediately before continuing to the next node in the BFS. This prevents macro-clusters from blocking the depth-level BFS order.
