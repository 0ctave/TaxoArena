# Empirical Results Plan

> Paper §6 content. All experiments are **code-unblocked** after the M3 fixes;
> this is pure experimental-run work. Priority order reflects reviewer expectations.
> Updated June 2026.

> **STATUS: PARTIALLY SUPERSEDED (2026-07-27).** The plan below predates the 2026-07
> corrections. Read the following four amendments before running anything from it.
>
> **1. RQ2 is reframed.** The plan implicitly tests "does adapted grouping produce more
> informative per-cell rankings". A pre-registered analysis has already answered the premise
> underneath that question, and the answer is no: observed Spearman rho between cells is
> ~0.91-0.93 at **every** granularity (14 / 87 / 88 / 152) and under **both** routers, and
> centering out each model's global mean leaves a residual indistinguishable from the
> mechanical centering null `-1/(C-1)`. Cells do not have different true rankings on this
> corpus for this roster, so a per-cell `Delta tau` has no room to move. The question the
> system actually poses is **"does adapted grouping enable better judging"** — a claim about
> judge generalisation surface, not about rank divergence between cells. See
> [`../reframed-argument.md`](../reframed-argument.md) and
> [`../prereg_discriminative_power.md`](../prereg_discriminative_power.md).
>
> **2. The ablation matrix references parameters that no longer exist.** A5's
> `separationEpsilon` is now `proposalSeparationBar` (a level) and `marginalEps` (a
> difference), decoupled; A6's `deltaAssign` x `assignmentCosineGap` grid is gone entirely —
> the routing knobs are `descentMargin` (a mode selector, not a sweep axis),
> `routingBeamGamma` and `membershipFloor`. A7's default is 50 iterations with convergence
> certified at 10, not 35.
>
> **3. Routing ECE is reportable, with its aggregation named.** *~~Amendment 3 previously
> read "Routing ECE cannot currently be reported; `computeRoutingECE` returns 0.0 in every
> run in the project's history." That was false. Inverted 2026-07-30.~~* The metric is
> implemented and reached; the `return 0.0` is guarded on an empty ground-truth map, which
> a validation run does not produce. The frozen run exported **0.2114**
> (`experiment_results/freeze_mcs55/seed_42/validation/MAIN_routing_calibration.csv`). The
> real defect is that both export sites aggregate a domain's leaf shares with `maxOf`
> instead of summing, so confidences are understated. Cite 0.2114 with that named, or not
> at all. See [`../known-defects.md`](../known-defects.md).
>
> **4. Multi-seed runs must not use the `seeds = [...]` config list.** Only the first seed
> routes held-out queries; the rest silently take a ~80% NoMatchRate. Run one config per
> seed.
>
> **Two experiments the plan does not contain and should**, both pre-registered or costed
> already: the **three-arm rubric-specificity test** (leaf-87 / random-87 with matched cell
> sizes / domain-14, ~174 inductions, no judge calls — and a free within-arm null that may
> settle it without them), see
> [`../prereg_rubric_specificity.md`](../prereg_rubric_specificity.md); and the
> **hold-out-a-domain** recovery experiment, which must be run at `descentMargin ~ 0` or it
> fails by construction, see [`../incremental-taxonomy.md`](../incremental-taxonomy.md).

---

## 1. GT Plumbing (Unblocks H-F1, Overlapping NMI)

**What:** Wire per-query true-leaf ground truth through `TaxonomyService` into the
`computeHierarchicalF1` and `OverlappingNmi` call sites. The TODO comments are in
`TaxonomyMetrics.kt`.

**Why first:** H-F1 is the *mandatory* metric for comparison with HTC literature.
Every other baseline comparison is blocked on this.

**Effort:** ~2h engineering (data plumbing, no algorithm changes).

---

## 2. Baselines

Required for any submission claiming SOTA or competitive performance.

| Baseline | Type | Implementation |
|----------|------|----------------|
| **HiAGM** (Zhou et al. 2020) | Supervised HTC, BERT-based | External Python, evaluate on same MMLU-Pro split |
| **HGCLR** (Wang et al. 2022) | Graph-contrastive HTC | External Python |
| **Flat k-means** (cosine) | Unsupervised flat clustering | 1-2h, trivial from existing infrastructure |
| **Hierarchical Agglomerative Clustering** (Ward) | Unsupervised tree | Scipy / existing embeddings |
| **Random taxonomy** | Null baseline | Shuffle node assignments |

Minimum required: one supervised baseline (HiAGM or HGCLR) + flat k-means.
Report H-F1, Edge F1, Triplet Accuracy for all.

---

## 3. Ablation Matrix

Each row is a single run changing one variable. All other params held constant
at the canonical config (see `REPRODUCIBILITY.md §5`).

| Experiment | Variable | Values | Metric focus |
|------------|----------|--------|--------------|
| **A1** — Fixed dimension | `d` (MRL slice) | 128, **256 (default)**, 512 | H-F1, Edge F1, κ reliability (d/N) |
| **A2** — Bias correction | Hornik–Grün correction | on (default), off | κ profile, Leaf Coherence |
| **A3** — Overlapping NMI | NMI variant | Overlapping (default), disjoint Shannon | NMI value comparison |
| **A4** — DAG vs Tree purity | Purity formula | DAG-LCA + tree-skeleton subtree (default), standard tree purity | Dendrogram Purity |
| **A5** — Split gate | `separationEpsilon` | 0.01, 0.02, 0.05, 0.10 | node count, H-F1 (near-inert: observed deltas ≈0.8) |
| **A6** — Routing margin (joint) | `deltaAssign` × `assignmentCosineGap` | {1.0, 2.0, 3.0} × {0.10, 0.15, 0.20} | Macro F1, any-match, contamination, AvgMatch |
| **A7** — Iteration count | `numIterations` | 10, 25, **35 (default)** | convergence curve |
| **A8** — Reserved vs full | `reservedOnly` | true (default), false | all metrics |

**A1**, **A2**, and **A6** are the most consequential: A1 justifies the fixed-d=256
choice on d/N-coherence grounds (median leaf N≈105 → d/N≈2.4 at 256 vs ≈9.8 at 1024);
A2 quantifies the Hornik–Grün correction; A6 sweeps the joint precision↔coverage
frontier that drives every routing metric.

---

## 4. Multi-seed Runs

Minimum 3 seeds for all headline numbers. Report mean ± std.

```
Seeds: 42 (canonical), 137, 2048
```

Run the canonical config at all 3 seeds. H-F1, Edge F1, Triplet Accuracy,
Contamination Ratio, Total Dasgupta Cost.

---

## 5. Missing Metrics — Implementation Specs

### 5.1 Triplet Accuracy

```kotlin
// In HierarchicalMetrics.kt
fun tripletAccuracy(embeddings: List<Embedding>, root: GraphNode): Double {
    // Sample min(N*(N-1)*(N-2)/6, 10_000) random triplets
    // For each (x,y,z): correct iff depth(LCA(x,y)) > depth(LCA(x,z))
    //   when cosineSim(x,y) > cosineSim(x,z)
    // Return fraction correct
}
```

Use DAG LCA (shallowest) consistent with `dagDendrogramPurity`.

### 5.2 Routing ECE

```kotlin
// In TaxonomyTrickler or a new RoutingCalibration.kt
fun routingECE(routingLog: List<RoutingDecision>, numBins: Int = 10): Double {
    // RoutingDecision: { queryId, nodeId, confidence: Double, isCorrect: Boolean }
    // Bin by confidence; compute |acc(b) - conf(b)| weighted by bin size
}
```

Requires logging routing decisions with confidence scores during `reassignQueries`.
Add a `RoutingDecision` data class and a `routingLog` field to `TaxonomyMetrics`.

### 5.3 Total Dasgupta Cost

```kotlin
// In TaxonomyMetrics.kt, call after final iteration
fun totalDasguptaCost(root: GraphNode, embeddings: List<Embedding>): Double {
    // For each pair (i,j): wij = clip(cosineSim(xi, xj), 0, 1)
    // |T(i,j)| = subtree size at shallowest DAG LCA
    // Return Σ wij * |T(i,j)|
    // Can sample pairs for large N: O(N²) is feasible up to N~5000
}
```

### 5.4 Normalised Sackin Index

```kotlin
// Supplement existing EI in TaxonomyMetrics.kt
fun normalisedSackin(root: GraphNode): Double {
    val leaves = getAllLeaves(root)
    return leaves.sumOf { it.depth }.toDouble() / leaves.size
    // Note: canonical Sackin S = Σ depth(ℓ); normalised S̃ = S/N
}
```

---

## 6. Per-domain Leaderboard

The global leaderboard mixes domains without normalisation, which is misleading
(domains differ greatly in query count and difficulty). Add a per-domain breakdown:
- H-F1 per MMLU-Pro domain
- Contamination ratio per domain  
- Mean κ at depth-3 per domain

This also surfaces the embedding-bottleneck hypothesis: if contamination is invariant
across seeds but varies across domains, the bottleneck is domain-specific embedding
geometry, not algorithm stochasticity.
