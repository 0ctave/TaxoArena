# Active Matchmaking & Information-Theoretic Scheduling

This document details the scheduling and stopping algorithms used in **TaxoArena** to run efficient model evaluations. It formalizes matchmaking utility using binary entropy maximization, KDE score-space valley detection, dual-maturity scheduling, and difficulty-weighted convergence.

---

## 1. The Active Matchmaking Problem

In a standard model evaluation arena, evaluation is performed via round-robin matchmaking, where all model pairs are evaluated on all queries. For $M$ models and $N$ queries, this requires:

$$ \text{Total Comparisons} = N \times \frac{M(M-1)}{2} $$

As the number of models $M$ increases, this round-robin approach becomes computationally and financially prohibitive. Furthermore, evaluating pairs with highly divergent capabilities (e.g., a state-of-the-art model vs. a weak baseline) on every query yields no new information because the outcome is already certain.

**TaxoArena** implements **Active Matchmaking**. The system schedules matches dynamically, targeting model pairs and taxonomy nodes with the highest rating uncertainty, using a unified budget ceiling to prevent convergence deadlocks.

---

## 2. Pre-Arena Query Routing & Verdict Reuse

To optimize judge call efficiency, TaxoArena decouples query routing from matchmaking evaluation:

1.  **Frozen Pre-Routing Pass**: Before the active matchmaking loop starts, all queries are routed to target leaves using the Von Mises-Fisher (vMF) projected similarity engine. The assignments are frozen in an inverse mapping `queryToLeaves: Map<QueryId, List<LeafId>>`.
2.  **Verdict Propagation**: Sibling leaves frequently share boundary queries due to cross-links. When a judge verdict is computed for a query $q$ and model pair $(i, j)$ at leaf $L$, the outcome is automatically propagated to all sibling leaves in `queryToLeaves[q]`. This avoids duplicate LLM evaluations and reduces the total match budget by up to $10\%$.

---

## 3. Dual-Maturity Scheduling Utility

Matchmaking is managed by [BtMatchScheduler](../../src/main/kotlin/taxonomy/service/BtMatchScheduler.kt). Instead of purely optimizing rating uncertainty, the scheduler balances **global rank ordering** and **local rating resolution** via a composite utility:

$$ \text{Utility}(i, j, L) = \left( \alpha \cdot U_{\text{structure}}(i, j) + (1 - \alpha) \cdot U_{\text{resolve}}(i, j, L) \right) \times \left( 1.0 - 0.3 \times \frac{n_{ij}}{\text{budget}_{\text{pair}}} \right) $$

where:
*   $n_{ij}$ is the current number of times this pair has been compared on leaf $L$.
*   $\text{budget}_{\text{pair}}$ is the unified maximum comparison ceiling (synchronized with the stopping policy).

### Dual-Maturity Decay ($\alpha$)
The mixing parameter $\alpha \in [0.2, 1.0]$ decays dynamically as rating maturity increases, transitioning from global rank structuring to local uncertainty resolution:

$$ \alpha = 0.20 + 0.80 \exp(-2.5 \cdot \text{maturity}) $$
$$ \text{maturity} = 0.35 \cdot \text{maturity}_{\text{SE}} + 0.65 \cdot \text{maturity}_{\text{pairs}} $$

where:
*   $\text{maturity}_{\text{SE}} = \left(1.0 - \frac{\text{avgSE}}{\text{priorSE}}\right)$ measures standard error shrinkage relative to the prior standard error ($\text{priorSE} = 10.0$).
*   $\text{maturity}_{\text{pairs}} = \frac{N_{\text{resolved pairs}}}{N_{\text{total pairs}}}$ measures the fraction of pairs already separated.

### Term 1: Structure Score ($U_{\text{structure}}$)
Focuses on binary search-like rating pivots by prioritizing matchups between models that are adjacent in the current log-strength ranking:

$$ U_{\text{structure}}(i, j) = \exp(-|\text{rank}_i - \text{rank}_j|) $$

### Term 2: Resolve Score & KDE Valley Boost ($U_{\text{resolve}}$)
Focuses on rating boundary resolution by scaling the matchup entropy by the standard errors and boosting pairs located in score-density valleys:

$$ U_{\text{resolve}}(i, j, L) = \frac{H(Y_{ij} \mid \hat{s})}{SE_i^2 + SE_j^2} \times w_{ij} $$

The valley weight $w_{ij}$ is estimated using a Gaussian Kernel Density Estimator (KDE) with Silverman's rule bandwidth $h$:

$$ h = 1.06 \cdot \hat{\sigma}_{\text{scores}} \cdot K^{-1/5} $$
$$ \text{density}(x) = \frac{1}{K \cdot h} \sum_{k=1}^{K} K_{\text{Gauss}}\left(\frac{x - s_k}{h}\right) $$
$$ w_{ij} = 1.0 - \frac{\text{density}\left(\frac{s_i + s_j}{2}\right)}{\max_x \text{density}(x)} $$

This penalizes matchups inside dense score clusters (where models are statistically indistinguishable) and boosts matchups crossing rating boundaries (low-density valleys).

---

## 4. Centroid-Proximal Query Selection

For a scheduled pair $(i, j)$ at leaf $L$, the query scheduler selects the most representative queries from the pool. Available query embeddings $E_q$ are projected onto the node's slice dimension $D_L$ and sorted by **descending cosine similarity** (ascending distance) to the Von Mises-Fisher (vMF) centroid vector $\mu_L$:

$$ \text{Similarity}(q) = \text{dot}\left( \text{project}(E_q, D_L), \mu_L \right) $$

Queries with higher centroid similarity are scheduled first, ensuring that LLM judges evaluate pairs on queries that best represent the leaf's category core.

---

## 5. Difficulty-Weighted Stopping Policy

The evaluation rounds run until the stopping criteria defined in [BtStoppingPolicy](../../src/main/kotlin/taxonomy/service/BtStoppingPolicy.kt) are met.

### Leaf Node Convergence (`isLeafConverged`)
A leaf node $L$ is marked as converged if:
1.  **Data Exhaustion**: The live comparisons count exceeds the target data capacity.
2.  **Informative Pair Resolution**: All informative pairs $(i, j)$ are resolved (either rating gap $|s_i - s_j| \ge 3.0 \cdot (SE_i + SE_j)$ or pair budget $n_{ij} \ge \text{budget}_{\text{pair}}$ is exhausted).
3.  **Top-2 Separation**: The gap between the first and second ranked models exceeds a confidence threshold:
    
    $$ s_{(1)} - s_{(2)} > 1.5 \times (SE_{(1)} + SE_{(2)}) $$

### Difficulty-Weighted Global Stopping (`shouldStop`)
Rather than counting converged leaves equally, the global stopping check weights each leaf's stability contribution by its routed query support size:

$$ \frac{\sum_{L \in \text{converged \& stable}} |Q_L|}{\sum_{L \in \text{all leaves}} |Q_L|} \ge \text{targetLeafConvergenceFraction} $$

where $|Q_L|$ is the size of the pre-routed query pool for leaf $L$. This prevents small boundary leaves (which exhaust data trivially) from inflating the convergence metric and stopping evaluation prematurely.

---

## 🔗 Related Code References
*   [BtMatchScheduler](../../src/main/kotlin/taxonomy/service/BtMatchScheduler.kt): Implements entropy and KDE-based priority scheduling and query selection.
*   [BtStoppingPolicy](../../src/main/kotlin/taxonomy/service/BtStoppingPolicy.kt): Computes leaf-level and difficulty-weighted global convergence.
