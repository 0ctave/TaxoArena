# Phase 3: Trickle (Top-Down Restrictive Routing)

*Implemented in `TaxonomyTrickler.kt`*

Trickle routes every embedding from the root down the DAG, accumulating log-probabilities at each level via a temperature-scaled vMF log-likelihood, and returns a set of destination leaves filtered by a margin criterion.

---

## 1. DAG Walk and Log-Probability Accumulation

The walk starts at the root with \(\log p = 0\) and recurses into every child. Because the DAG may have cross-link edges (a node reachable via multiple paths), the log-probability from all paths is combined with log-sum-exp:

\[
\log p_{\text{acc}}(v) = \log\!\left(\sum_{\text{paths } \pi : \text{root} \to v} \exp\!\left(\sum_{e \in \pi} \log p_e\right)\right)
\]

This ensures polyhierarchical assignments are treated correctly: if a leaf is reachable by two paths, both paths contribute to its total score.

---

## 2. Per-Level Scoring: vMF Log-Likelihood

At each non-leaf node \(v\) with children \(\{c_1, \ldots, c_K\}\), the raw score for child \(c_k\) is the vMF log-density of the query \(\hat{\mathbf{x}}\) projected to the child's slice dimension \(d_k\):

\[
f_k = \log C_{d_k}(\kappa_{\text{sib}}) + \kappa_{\text{sib}}\, \boldsymbol{\mu}_{c_k}^\top \hat{\mathbf{x}}_{[1:d_k]}
\]

where \(\kappa_{\text{sib}} = \operatorname{clip}\!\left(\frac{1}{K}\sum_k \kappa_{c_k},\, 1,\, 100\right)\) is the sibling-average concentration used as a shared normalizer to make scores comparable across siblings with varying \(\kappa\).

**Ground-truth bias (iteration 1 only):** when a query's original category matches a child label, the score is boosted by \(\log(1/0.7) \approx 0.357\) nats to guide early-stage routing before the vMF parameters have fully converged.

---

## 3. Temperature-Scaled Softmax

The raw scores are divided by temperature \(\tau\) (config: `cosineTau`, default 0.5) and passed through a numerically stable log-softmax:

\[
\log q_k = \frac{f_k}{\tau} - \log\!\sum_{j=1}^{K} \exp\!\left(\frac{f_j}{\tau}\right)
\]

To prevent zero-probability mass at any child (important for the DAG log-sum-exp accumulation), Laplace smoothing with \(\varepsilon = 0.05/K\) is applied before taking logs:

\[
p_k^{\text{smooth}} = \frac{e^{\log q_k} + \varepsilon}{1 + K\varepsilon}, \qquad \log p_k = \log p_k^{\text{smooth}}
\]

---

## 4. Assignment Margin Filter

After the full DAG walk, only leaf nodes within `assignmentGap` (fractional, e.g. 0.05) of the best-scoring leaf are returned:

\[
\mathcal{A}(\hat{\mathbf{x}}) = \left\{\, v \in \text{Leaves} \;\Big|\; \exp\!\left(\log p_{\text{acc}}(v)\right) \geq (1 - \delta_{\text{gap}}) \cdot \max_{\ell}\, e^{\log p_{\text{acc}}(\ell)} \right\}
\]

This replaces the legacy hard cap on multi-assignments. The number of assigned leaves is now determined purely by the geometry of the embedding space:
- At bootstrap (4 coarse leaves), well-separated domains produce \(|\mathcal{A}| = 1\) for the vast majority of queries.
- At equilibrium with hundreds of fine-grained leaves, semantically ambiguous queries naturally land in 2–3 close-scoring leaves.

If the filter returns an empty set (all leaves below the gap threshold, e.g. out-of-distribution query), the query falls back to the root.

---

## 5. Output Normalization

The returned map \(\{v \to \log p_v\}\) is renormalized so that \(\sum_{v \in \mathcal{A}} \exp(\log p_v) = 1\), making the returned values proper log-probabilities suitable for downstream use in metrics (ECE, triplet accuracy).
