# Bradley-Terry Model Fitting & Log-Strength Optimization

This document details the mathematical formulation and optimization techniques used in **TaxoArena** to fit model capabilities from pairwise win/loss/tie stats. It covers the Bradley-Terry (BT) model, the Minorization-Maximization (MM) algorithm, tie handling, and Fisher Information standard error estimation.

---

## 1. The Bradley-Terry Model

The Bradley-Terry model is a probabilistic framework for predicting the outcome of a pairwise comparison between items. In TaxoArena, let $K$ be the number of models evaluated. Each model $i$ is assigned a latent skill strength parameter $\pi_i > 0$. The probability that model $i$ beats model $j$ is defined as:

$$ P(i \succ j) = \frac{\pi_i}{\pi_i + \pi_j} $$

To work in an additive rating scale, we define the log-strength rating $s_i = \ln \pi_i$:

$$ P(i \succ j) = \frac{\exp(s_i)}{\exp(s_i) + \exp(s_j)} = \frac{1}{1 + \exp(-(s_i - s_j))} $$

This is mathematically equivalent to a logistic function of the rating difference. To ensure the ratings are identifiable, we enforce the zero-sum normalization constraint:

$$ \sum_{i=1}^{K} s_i = 0 $$

### Handling Ties
Pairwise comparisons in TaxoArena can result in a tie (where the LLM judge declares no preference, or the position-reversed evaluations contradict each other). We handle ties using the standard half-win encoding. Let $w_{ij}$ be the total wins of model $i$ against $j$, and $t_{ij}$ be the tie count. The effective wins are updated as:

$$ w'_{ij} = w_{ij} + 0.5 \cdot t_{ij} $$

$$ w'_{ji} = w_{ji} + 0.5 \cdot t_{ij} $$

The total matches between $i$ and $j$ is $n_{ij} = w'_{ij} + w'_{ji} = w_{ij} + w_{ji} + t_{ij}$.

---

## 2. Minorization-Maximization (MM) Optimization

To find the Maximum Likelihood Estimate (MLE) of the log-strengths $s$, we maximize the log-likelihood function:

$$ \mathcal{L}(s) = \sum_{i=1}^{K} \sum_{j \neq i} \left[ w'_{ij} s_i - w'_{ij} \ln(\exp(s_i) + \exp(s_j)) \right] $$

Direct maximization requires solving nonlinear equations. TaxoArena implements the **Minorization-Maximization (MM)** algorithm in [BtMmFitter.fit](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMmFitter.kt). The MM algorithm constructs a tight lower bound (surrogate function) and maximizes it iteratively, guaranteeing global and monotonic convergence.

The update equation for the strength parameter $\pi_i^{(t+1)}$ at iteration $t+1$ is:

$$ \pi_i^{(t+1)} = \frac{W_i}{\sum_{j \neq i} \frac{n_{ij}}{\pi_i^{(t)} + \pi_j^{(t)}}} $$

where $W_i = \sum_{j \neq i} w'_{ij}$ is the total effective wins of model $i$.

Converting to log-strength $s_i = \ln \pi_i$, the update becomes:

$$ s_i^{(t+1)} = \ln W_i - \ln \left( \sum_{j \neq i} \frac{n_{ij}}{\exp(s_i^{(t)}) + \exp(s_j^{(t)})} \right) $$

### Convergence Criteria
Post-update, we enforce the normalization $\sum s_i = 0$ by subtracting the mean: $s_i \leftarrow s_i - \bar{s}$. The iteration loops until the maximum parameter shift falls below a tolerance threshold ($\epsilon_{\text{tol}} = 10^{-6}$):

$$ \max_{i} \left| s_i^{(t+1)} - s_i^{(t)} \right| < \epsilon_{\text{tol}} $$

---

## 3. Variance & Standard Error Estimation

To compute confidence intervals for the ratings, we estimate the standard error of $s_i$. The variance of the MLE is derived from the diagonal elements of the Fisher Information matrix:

$$ I_{ii}(s) = -\frac{\partial^2 \mathcal{L}}{\partial s_i^2} = \sum_{j \neq i} n_{ij} \frac{\exp(s_i) \exp(s_j)}{(\exp(s_i) + \exp(s_j))^2} $$

The term $\frac{\exp(s_i) \exp(s_j)}{(\exp(s_i) + \exp(s_j))^2}$ is equal to $P(i \succ j) P(j \succ i)$, representing the Bernoulli variance of the match outcomes.

The standard error ($SE$) of the rating $s_i$ is computed in [BtMmFitter.estimateStdErrors](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMmFitter.kt) as:

$$ SE_i = \frac{1}{\sqrt{I_{ii}(s)}} $$

If a model has not participated in any matches ($I_{ii}(s) = 0$), the standard error defaults to a high value ($10.0$) to indicate complete uncertainty. These standard errors are used by the matchmaking scheduler to target high-variance pairs and by the stopping policy to detect convergence.

---

## 🔗 Related Code References
*   [BtMmFitter](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/BtMmFitter.kt): Implements the MM fitting algorithm and Fisher Information standard error estimator.
*   [TaxonomyRankingService](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/service/TaxonomyRankingService.kt): Handles saving and loading of `NodeBtState` objects from the SQLite database.
