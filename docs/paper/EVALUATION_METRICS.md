# Evaluation Metrics

> **Scope** Paper §6 (Experiments) and appendix. Defines every metric used,
> its citation, implementation status, and any open wiring/rename work.
> Updated post PR #46 (commit `f257dcf`), June 2026.

---

## Status legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented, wired, reports correct values |
| 🔌 | Code in, but GT-plumbing TODO — reports `0.0` until wired |
| 📋 | Defined below, implementation pending |
| ⚠️ | Needs rename / documentation fix only |

---

## Category A — Quality Targets (optimise upward)

These metrics align with the polyhierarchical goal. Do NOT interpret low values as
failure — they may reflect correct polyhierarchy.

### Edge F1 vs Gold ✅

Fraction of predicted parent→child edges that match a gold taxonomy edge set,
and vice versa. Well-defined; implementation stable.

**Citation:** taxonomy induction literature (Zhang et al. 2022).

### κ Profile by Depth ✅

Reports mean vMF concentration `κ̄(d)` per depth level. Rising κ with depth
indicates increasing intra-cluster coherence — the expected signature.

Typical observed values: depth-0 κ≈2, depth-3 κ≈44–75 depending on params.

### Spherical Silhouette ✅

Silhouette coefficient computed with cosine distance (not Euclidean) on the unit
hypersphere. Values in `[−1, 1]`; higher is better.

**Citation:** Banerjee et al. 2005 (vMF–cosine equivalence).

### Avg Match Count ✅

Mean number of taxonomy nodes a query is assigned to. Values > 1 confirm
polyhierarchical routing is active.

### Hierarchical F1 (H-F1) 🔌

Defined as the harmonic mean of Hierarchical Precision (H-P) and Hierarchical
Recall (H-R), where ancestor-level matches are counted:

```
H-P(q) = |pred_ancestors(q) ∩ true_ancestors(q)| / |pred_ancestors(q)|
H-R(q) = |pred_ancestors(q) ∩ true_ancestors(q)| / |true_ancestors(q)|
H-F1   = 2·H-P·H-R / (H-P + H-R)
```

**Implementation:** `computeHierarchicalF1` in `HierarchicalMetrics.kt` (PR #46).
**Status:** Reports `0.0` — per-query true-leaf ground truth must be plumbed from
`TaxonomyService` into `TaxonomyMetrics.computeHierarchicalF1`. TODO comment left
at call site.

**Citation:** Kosmopoulos, Partalas, Gaussier, Paliouras & Androutsopoulos 2014,
*Information Retrieval Journal* 18:83–112.

### Triplet Accuracy 📋

A triplet `(x, y, z)` is *correct* iff `depth(LCA(x,y)) > depth(LCA(x,z))` when
`sim(x,y) > sim(x,z)`. Does not require a gold taxonomy — intrinsic measure.

```
TripAcc = |{(x,y,z) : triplet correct}| / |{(x,y,z) : sim(x,y) > sim(x,z)}|
```

**Implementation:** pending (see `docs/paper/EMPIRICAL_PLAN.md`).
**Citation:** Vrandečič et al. 2023 (taxonomy quality evaluation).

### Routing ECE (Expected Calibration Error) 📋

Measures whether soft-routing probabilities `p_c` are calibrated:

```
ECE = Σ_b (|B_b|/N) · |acc(B_b) − conf(B_b)|
```

where bins `B_b` group routing decisions by confidence. Tests whether the
softmax temperature `τ=0.5` in `TaxonomyTrickler` is well-calibrated.

**Implementation:** pending.
**Citation:** Guo et al. 2017, ICML (temperature scaling / ECE).

### Total Dasgupta Cost 📋

The full-tree Dasgupta cost (not just the per-split delta used during construction):

```
cost(T) = Σᵢ≠ⱼ  wᵢⱼ · |T(i,j)|
```

This is the theory-grounded, dataset-independent quality measure that enables
cross-system comparison. Trivially computable from existing pair-weight infrastructure.

**Implementation:** pending — add to `TaxonomyMetrics` final-report output.
**Citation:** Dasgupta 2016 (DOI `10.1145/2897518.2897527`);
Roy & Pokutta 2017; Cohen-Addad et al. 2018.

---

## Category B — Characterisation Metrics (do NOT optimise down)

These compare against single-label ground truth and will look "bad" precisely when
polyhierarchy is working correctly. Report them but do not present them as targets.

### Overlapping NMI ✅ (formula correct post PR #46)

For a DAG with overlapping assignments, standard NMI is incorrect (inflates by
treating overlap as agreement). The Lancichinetti–Fortunato–Kértesz 2009 formula is:

```
NMI_ovlp(X, Y) = 1 − [H(X|Y) + H(Y|X)] / 2
```

where `H(X|Y)` is a generalised conditional entropy over fuzzy community assignments
(column-normalised encoding).

**Implementation:** `OverlappingNmi.kt` (PR #46). GT-plumbing TODO remains at call
site — overlapping GT domain covering not yet wired.

**Citation:** Lancichinetti, Fortunato & Kértesz 2009, *New J. Phys.* 11:033015
(DOI `10.1088/1367-2630/11/3/033015`).

### ARI ✅

Adjusted Rand Index on flat partitions. Known to penalise polyhierarchy.

### DAG Dendrogram Purity ✅ (formula correct post PR #46)

For a DAG, LCA is not unique. Implementation uses the *shallowest* LCA across all
paths (conservative bound), following Monath et al. 2021.

**Implementation:** `dagDendrogramPurity` in `HierarchicalMetrics.kt` (PR #46).
**Citation:** Monath, Zaheer, Dubey, Ahmed & McCallum 2021, AISTATS, PMLR 130
(DOI `10.48550/arXiv.2105.04024`).

### Weighted Leaf Purity (WLP) ⚠️

Leaf-node purity weighted by leaf size:

```
WLP = Σ_ℓ  (|ℓ| / N) · purity(ℓ)
    where purity(ℓ) = max_c |{q ∈ ℓ : gt(q) = c}| / |ℓ|
```

This is a **custom metric**. It is related to standard cluster purity but is not
an established named metric. Must be presented with this explicit formula and
labelled as *We define Weighted Leaf Purity as...*

**Action required:** add formal definition to paper methods section.
**Related work:** Zhong & Ghosh 2005; Zhang et al. 2022 (taxonomy induction).

### Contamination Ratio ⚠️

Fraction of leaf nodes that contain queries from ≥2 ground-truth categories.
Currently ~16.8% across both run configurations — invariant, indicating the
bottleneck is embedding geometry (Qwen3-embedding), not algorithm parameters.

**Action required:** add formal definition (denominator = total leaf nodes;
threshold = 2 or more GT categories co-present).

### Exact-Match Ancestor Rate (EMAR) ⚠️ *(currently named ACR)*

Fraction of queries for which *all* predicted ancestor nodes match GT ancestors.
This is a stricter variant of Hierarchical Precision.

**Action required:** rename from `ACR` to `Exact-Match Ancestor Rate` in code,
TUI, and paper. Cite Silla & Freitas 2011, DMKD as closest standard (Hierarchical
Precision). Note the distinction: HP averages over ancestors; EMAR requires all.

### Normalised Sackin Index ⚠️ *(currently Equilibrium Index)*

Currently `EI = 1 − Gini(leaf_sizes)`. This measures inequality of *member counts*,
not structural tree balance. The standard index is the normalised Sackin:

```
S̃ = (1/N) · Σ_ℓ  depth(ℓ)  (summed over leaves, normalised by leaf count)
```

Alternatively, the Lemant et al. 2022 `Ī` index (Systematic Biology 71:S1210–S1224)
is universal (handles non-binary trees, normalised to `[0,1]`).

**Action required:** either rename EI to Normalised Sackin with the formula above,
or add `Ī` alongside it. Cite Fischer et al. 2021 (arXiv:2109.12281) survey.

---

## Metric Suite Summary Table

| Metric | Type | Status | Key Citation |
|--------|------|--------|--------------|
| Edge F1 | Quality | ✅ | Zhang et al. 2022 |
| κ by depth | Quality | ✅ | Banerjee 2005 |
| Spherical Silhouette | Quality | ✅ | Banerjee 2005 |
| Avg Match Count | Quality | ✅ | — |
| H-F1 | Quality | 🔌 GT-wiring | Kosmopoulos 2014 |
| Triplet Accuracy | Quality | 📋 pending | Vrandečič 2023 |
| Routing ECE | Quality | 📋 pending | Guo 2017 |
| Total Dasgupta Cost | Quality | 📋 pending | Dasgupta 2016 |
| Overlapping NMI | Characterisation | ✅ formula; 🔌 GT | Lancichinetti 2009 |
| ARI | Characterisation | ✅ | Hubert & Arabie 1985 |
| DAG Dendrogram Purity | Characterisation | ✅ | Monath 2021 |
| WLP | Characterisation | ⚠️ define formally | Zhong & Ghosh 2005 |
| Contamination Ratio | Characterisation | ⚠️ define formally | — |
| EMAR (rename ACR) | Characterisation | ⚠️ rename | Silla & Freitas 2011 |
| Normalised Sackin | Characterisation | ⚠️ supplement EI | Fischer 2021 |
