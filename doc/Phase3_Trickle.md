# Phase 3: Trickle (Top-Down Restrictive Routing)

## 1. Multi-Component GMM Inclusion
To trickle a query $x$ through the DAG, ArcTaxoAdapat evaluates it against the **Composite Distribution** of each node.

### 1.1 Regularized Mahalanobis Distance
A query $x$ is evaluated using the **Minimum Regularized Mahalanobis Distance** across all $K$ components of a node's GMM.
$$ D_M(x | \mu_k, \Sigma_k) = \sqrt{(x - \mu_k)^T \hat{\Sigma}_k^{-1} (x - \mu_k)} $$
The covariance is regularized using a $\lambda$ parameter (default 0.1) to align it with the properties of the Cosine embedding space, preventing singularities and ensuring stability.

### 1.2 Union Inclusion Logic
A query is considered to reside within a node if it falls within the statistical boundary of **any** of its components.
$$ \mathbb{I}(x \in P) = \bigvee_{k=1}^{K} D_M(x | \mu_k, \Sigma_k) \le \tau_{\text{threshold}} $$

## 2. The Restrictive Funnel Effect
Knowledge routing becomes progressively more exclusive as queries move deeper into the hierarchy.

### 2.1 Depth-Decayed Confidence ($\alpha$)
The system applies an exponential decay to the confidence interval $\alpha$ based on the node's depth:
$$ \alpha = \tau_{fit} \cdot e^{-\lambda \cdot depth} $$
Where $\tau_{fit}$ is the baseline confidence (default 0.95) and $\lambda$ is the `depthDecayLambda` (default 0.6).

### 2.2 Chi-Square Thresholding
The decayed $\alpha$ is converted to a distance threshold using a high-dimensional Chi-Square distribution approximation ($N(d, 2d)$ for $d=4096$). This ensures that macro-domains (shallow) are inclusive while leaf-domains (deep) are highly exclusive.

## 3. Top-Down Routing Logic
1.  **Start at Root**: All queries begin at the root node (depth 0).
2.  **Evaluate Children**: For each node, the query is checked against all child distributions.
3.  **Forking (Multi-Parent)**: If a query fits multiple children (within the `maxAssignmentsPerQuery` limit), it is "forked" and trickled down each matching branch.
4.  **Outlier Retention**: If a query satisfies the parent's macro-domain threshold but fails to map to any child sub-domain, it is retained in the parent's **unmapped query pool**. These "outliers" are the raw material for the **Discover** phase.
