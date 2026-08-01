# Structural Characterization Metrics: Match Count, Contamination, and Sackin Index

> **STATUS: §1 SUPERSEDED (2026-07-30). §2 and §3 are current.**
>
> The system is a **tree**. Cross-linking was removed and polyhierarchy is a reported
> negative result. So `AvgMatch = 1.0` by construction, and §1 no longer measures anything —
> it is an invariant check, not a coverage statistic. **The "observed values range between
> 1.1 and 1.3" claim below is dead** and must not be quoted; it described the pre-removal
> system. Contamination (§2) and Sackin (§3) are unaffected.

This document details the structural metrics used in **TaxoArena** to verify topology and
balance.

---

## 1. Average Match Count — now an invariant check

*The paragraph below describes the removed polyhierarchical system. Kept for the record.*

In a polyhierarchical Directed Acyclic Graph (DAG), a single query can route down multiple ancestral paths and land in multiple leaf nodes.

### Mathematical Formulation
Let $\mathcal{L}(q)$ be the set of leaf nodes assigned to query $q$ by the trickle router. The **Average Match Count** is the mean cardinality of this set across the dataset:

$$ \text{AvgMatch} = \frac{1}{N} \sum_{i=1}^{N} \left| \mathcal{L}(q_i) \right| $$

### Interpretation
*   $\text{AvgMatch} = 1.0$: the expected and only valid value in the current system. The taxonomy is a strict tree.
*   $\text{AvgMatch} > 1.0$: **a bug**, not a finding. It would mean a query reached more than one leaf, which the tree cannot produce. *~~This branch previously read "confirms soft-routing and cross-linking are functioning; observed values range between 1.1 and 1.3". Both the mechanism and the range are gone.~~*

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
*   [TaxonomyMetrics](../../src/main/kotlin/taxonomy/utils/TaxonomyMetrics.kt): Computes structural metrics for snapshot logging.
