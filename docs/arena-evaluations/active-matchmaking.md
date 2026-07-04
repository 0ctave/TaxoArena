# Active Matchmaking & Information-Theoretic Scheduling

This document details the scheduling and stopping algorithms used in **TaxoArena** to run efficient model evaluations. It formalizes matchmaking utility using binary entropy maximization, standard error scaling, and convergence policies.

---

## 1. The Active Matchmaking Problem

In a standard model evaluation arena, evaluation is performed via round-robin matchmaking, where all model pairs are evaluated on all queries. For $M$ models and $N$ queries, this requires:

$$ \text{Total Comparisons} = N \times \frac{M(M-1)}{2} $$

As the number of models $M$ increases, this round-robin approach becomes computationally and financially prohibitive. Furthermore, evaluating pairs with highly divergent capabilities (e.g., a state-of-the-art model vs. a weak baseline) on every query yields no new information because the outcome is already certain.

**TaxoArena** implements **Active Matchmaking**. The system schedules matches dynamically, targeting model pairs and taxonomy nodes with the highest rating uncertainty.

---

## 2. Information-Theoretic Utility Optimization

Matchmaking is managed by [BtMatchScheduler](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMatchScheduler.kt). The scheduler evaluates the utility of comparing model $i$ and model $j$ at leaf node $L$ using binary entropy.

### Matchup Entropy
Let $s_i, s_j$ be the current log-strength ratings of the models. The predicted probability of model $i$ winning is:

$$ P_{ij} = \frac{\exp(s_i)}{\exp(s_i) + \exp(s_j)} $$

The information entropy of the contest outcome is:

$$ H(Y_{ij} \mid \hat{s}) = -P_{ij} \ln P_{ij} - (1.0 - P_{ij}) \ln(1.0 - P_{ij}) $$

Entropy is maximized at $P_{ij} = 0.5$ (when ratings are identical, indicating maximum uncertainty) and approaches $0$ as $P_{ij} \to 0$ or $1.0$ (when one model is dominant).

### Variance Scaling & Repetition Discount
To prioritize pairs with high uncertainty and prevent over-sampling the same matchup, we scale the entropy by the sum of model rating variances and apply a repetition discount:

$$ \text{Utility}(i, j) = \frac{H(Y_{ij} \mid \hat{s})}{SE_i^2 + SE_j^2} \times \left( 1.0 - 0.3 \times \frac{n_{ij}}{\text{budget}_{\text{pair}}} \right) $$

where:
*   $SE_i, SE_j$ are the rating standard errors computed via Fisher Information.
*   $n_{ij}$ is the current number of times this pair has been compared.
*   $\text{budget}_{\text{pair}}$ is the maximum comparisons allowed per pair (default $100$).

### Bootstrap Priority
If model $i$ or model $j$ has zero comparisons on leaf $L$, the ratings cannot be fitted. The scheduler bypasses entropy calculation and assigns a maximum bootstrap utility:

$$ \text{Utility}_{\text{bootstrap}} = \ln 2 + 1.0 + (10 - \min(n_{ij}, 10)) \times 0.1 $$

This guarantees that all models are matched at least twice per leaf before entropy-driven matchmaking begins.

---

## 3. Convergence & Stopping Rules

The evaluation rounds run until the stopping criteria defined in [BtStoppingPolicy](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtStoppingPolicy.kt) are met.

### Leaf Node Convergence (`isLeafConverged`)
A leaf node $L$ is marked as converged (no further matchmaking utility) if any of the following conditions hold:
1.  **Data Exhaustion**: The total comparisons at the node reach the database query capacity.
2.  **Informative Pair Resolution**: All pairs $(i, j)$ are resolved. A pair is considered resolved if the gap between their ratings exceeds three standard deviations:
    
    $$ |s_i - s_j| \ge 3.0 \times (SE_i + SE_j) $$
    
    Unresolved pairs that have exhausted their budget do not block convergence.
3.  **Top-2 Separation**: The gap between the top-ranked model and the second-ranked model is statistically significant:
    
    $$ s_{(1)} - s_{(2)} > 1.5 \times (SE_{(1)} + SE_{(2)}) $$

### Global Stopping (`shouldStop`)
At the end of each benchmark round, the stopping policy checks for global convergence:
*   For each leaf node, it stores the model leaderboard ranking.
*   It monitors ranking stability over a window of rounds (default $3$ rounds).
*   The benchmark terminates when the ratio of converged and stable leaves exceeds the target convergence fraction (default $70\%$):
    
    $$ \frac{N_{\text{converged & stable}}}{N_{\text{total leaves}}} \ge \text{targetLeafConvergenceFraction} $$
    
    or when the maximum rounds threshold is reached.

---

## 🔗 Related Code References
*   [BtMatchScheduler](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMatchScheduler.kt): Implements entropy-based priority scheduling and batch selection.
*   [BtStoppingPolicy](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtStoppingPolicy.kt): Computes leaf-level and global convergence.
