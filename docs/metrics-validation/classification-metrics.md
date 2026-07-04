# Hierarchical Classification Metrics: Hierarchical F1 and Exact-Match Ancestor Rate (EMAR)

This document details the hierarchical classification metrics used in **TaxoArena** to validate query routing accuracy against ground-truth labels. It formalizes Hierarchical Precision, Recall, F1, and the Exact-Match Ancestor Rate (EMAR).

---

## 1. The Necessity of Hierarchical Classification Metrics

Standard classification benchmarks use flat metrics (e.g., accuracy, macro F1). In a taxonomy, flat metrics are deficient because they treat all classification errors equally:
*   If a query on "Linear Algebra" is classified under "Group Theory" (both under "Mathematics"), a flat metric treats this error with the same penalty as if it were classified under "Clinical Medicine".
*   In a hierarchical system, the first error is a minor, localized shift, whereas the second error is a major routing failure.

Hierarchical classification metrics resolve this by evaluating the overlap of ancestral paths, rewarding predictions that remain within the correct general branch of the taxonomy.

---

## 2. Hierarchical Precision, Recall, and F1 (H-F1)

Following the formalisms of **Kosmopoulos et al. 2014** (*Information Retrieval Journal*), we define precision and recall over ancestor sets.

For a query $q$, let:
*   $\mathcal{P}(q)$ be the set of predicted nodes (the leaf node where the query was routed, plus all its ancestors up to the Root).
*   $\mathcal{T}(q)$ be the set of true nodes (the true ground-truth leaf node and all its ancestors).

### Hierarchical Precision (H-P)
The fraction of predicted ancestors that are correct:

$$ H\text{-}P(q) = \frac{\left| \mathcal{P}(q) \cap \mathcal{T}(q) \right|}{\left| \mathcal{P}(q) \right|} $$

### Hierarchical Recall (H-R)
The fraction of true ancestors that were successfully predicted:

$$ H\text{-}R(q) = \frac{\left| \mathcal{P}(q) \cap \mathcal{T}(q) \right|}{\left| \mathcal{T}(q) \right|} $$

### Hierarchical F1 (H-F1)
The harmonic mean of Hierarchical Precision and Recall:

$$ H\text{-}F_1 = \frac{2 \cdot H\text{-}P \cdot H\text{-}R}{H\text{-}P + H\text{-}R} $$

These values are calculated per query and averaged over the dataset.

> [!NOTE]
> Hierarchical metrics are computed inside [TaxonomyMetrics.computeHierarchicalF1](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt). A recent PR (#48) plumbed the per-query true-leaf ground truth into this service, enabling live validation of classification quality.

---

## 3. Exact-Match Ancestor Rate (EMAR)

The **Exact-Match Ancestor Rate (EMAR)**—historically labeled as `ACR` (Ancestor Coverage Rate) in the legacy code—is a strict classification metric.

While Hierarchical Precision averages correctness over the set of ancestors (allowing a query to have some incorrect ancestral branches and still achieve a high score), EMAR requires absolute containment.

### Mathematical Formulation
For a dataset of $N$ queries, EMAR is defined as the fraction of queries for which *every* predicted ancestor lies within the ground-truth ancestral path:

$$ \text{EMAR} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}\left( \mathcal{P}(q_i) \subseteq \mathcal{T}(q_i) \right) $$

where $\mathbb{I}(\cdot)$ is the binary indicator function:

$$ \mathbb{I}(\text{statement}) = \begin{cases} 1 & \text{if statement is true} \\ 0 & \text{if statement is false} \end{cases} $$

### Interpretation
EMAR is highly sensitive to cross-branch leakage. If a query is routed to a leaf that introduces even one incorrect parent node (e.g., via an incorrect cross-link), $\mathcal{P}(q) \subseteq \mathcal{T}(q)$ is violated, and the score for that query drops to $0.0$.

EMAR provides a strict upper bound on routing safety. A high EMAR guarantees that queries are never routed into incorrect macro-domains.

---

## 🔗 Related Code References
*   [TaxonomyMetrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt): Code location for `computeHierarchicalF1` and EMAR calculation.
