# Structural Characterization Metrics: Match Count, Contamination, and Sackin Index

This document details the structural metrics used in **TaxoArena** to verify DAG topology, balance, and polyhierarchical coverage.

---

## 1. Average Match Count

In a polyhierarchical Directed Acyclic Graph (DAG), a single query can route down multiple ancestral paths and land in multiple leaf nodes.

### Mathematical Formulation
Let $\mathcal{L}(q)$ be the set of leaf nodes assigned to query $q$ by the trickle router. The **Average Match Count** is the mean cardinality of this set across the dataset:

$$ \text{AvgMatch} = \frac{1}{N} \sum_{i=1}^{N} \left| \mathcal{L}(q_i) \right| $$

### Interpretation
*   $\text{AvgMatch} = 1.0$: The taxonomy acts as a strict tree. No polyhierarchical assignments are active.
*   $\text{AvgMatch} > 1.0$: Confirms that soft-routing and cross-linking are functioning. Typically, observed values in TaxoArena range between $1.1$ and $1.3$, showing that a fraction of queries are evaluated in multiple specialized arenas (e.g., a "biostatistics" query evaluated by both biology and mathematics judges).

---

## 2. Contamination Ratio

The **Contamination Ratio** measures the semantic composition of leaf nodes.

### Mathematical Formulation
For each leaf node $L$, let $Q_L$ be the set of queries assigned to $L$. Let $C(Q_L)$ be the set of distinct ground-truth category tags associated with those queries. The Contamination Ratio is the fraction of leaf nodes containing queries from two or more ground-truth categories:

$$ \text{ContaminationRatio} = \frac{\left| \left\{ L \in \text{Leaves} : \left| C(Q_L) \right| \ge 2 \right\} \right|}{\left| \text{Leaves} \right|} $$

### Design Intent & Calibration
In standard clustering, "contamination" is treated as an error. However, in TaxoArena, **contamination is desirable**. The system is designed to discover cross-domain leaf nodes that capture nuances between parent domains.

Empirical runs show that the contamination ratio stabilizes around $16.8\%$ across different parameter configurations (e.g., varying split thresholds and depth limits). This invariance indicates that contamination is a bottleneck of the embedding space geometry (Qwen3-Embedding) rather than a failure of the algorithm.

---

## 3. Normalised Sackin Index

In structural biology and phylogenetics, the **Sackin Index** is used to measure the balance of a hierarchical tree. Historically, TaxoArena tracked tree equality via the Gini index of leaf sizes (`equilibriumIndex = 1.0 - Gini(leaf_sizes)`). This measures member count balance rather than topological structure. The Normalised Sackin Index replaces this.

### Mathematical Formulation
The Sackin Index $S(T)$ of a tree $T$ is the sum of the depths of all leaf nodes:

$$ S(T) = \sum_{l \in \text{Leaves}} \text{depth}(l) $$

To normalize the index and make it independent of the total leaf count, we define the **Normalised Sackin Index** $\tilde{S}(T)$ as the average leaf depth:

$$ \tilde{S}(T) = \frac{1}{\left| \text{Leaves} \right|} \sum_{l \in \text{Leaves}} \text{depth}(l) $$

### Interpretation
*   **Low $\tilde{S}(T)$**: Indicates a flat, shallow tree where most nodes split early and close to the Root.
*   **High $\tilde{S}(T)$**: Indicates a deep, narrow tree with uneven branches, suggesting that some domains have decomposed into deep hierarchies while others remained unresolved.
*   The index helps monitor whether the taxonomy is developing balanced hierarchical depth or suffering from premature flattening.

---

## 🔗 Related Code References
*   [TaxonomyMetrics](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt): Computes structural metrics for snapshot logging.
