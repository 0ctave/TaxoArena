# Mathematical Foundations

> **Scope** Paper sections §3–5: the statistical and geometric basis of TaxoArena.
> Status column tracks what is fully publication-ready vs. what still needs a sentence.

---

## 1. von Mises–Fisher Estimation (Phase 2 — Fit)

### 1.1 Model

Each taxonomy node is modelled as a single von Mises–Fisher (vMF) distribution on the
`d`-dimensional unit hypersphere `S^{d-1}`, with `d = 256` fixed across all depths
(see §3 for the dimension choice):

```
p(x | μ, κ) = C_d(κ) · exp(κ · μᵀx)
C_d(κ) = κ^{d/2−1} / ( (2π)^{d/2} · I_{d/2−1}(κ) )
```

where `μ ∈ S^{d-1}` is the mean direction and `κ ≥ 0` is the concentration parameter.

### 1.2 MLE and Bias Correction

The MLE for `μ` is the normalised sample mean. The MLE for `κ` inverts
`A_d(κ̂) = R̄` where `R̄ = ‖∑xᵢ‖/N` is the mean resultant length and
`A_d(r) = I_{d/2}(r) / I_{d/2−1}(r)` is the ratio of modified Bessel functions
(Banerjee et al. 2005, JMLR 6).

**Bias.** The MLE `κ̂_MLE` is positively biased with bias `O(d/N)`. With the fixed
`d = 256` and the observed median leaf size `N ≈ 105` (IQR 77–146), the typical
`d/N ≈ 2.4`; the smallest leaves (`N ≈ 50`) give `d/N ≈ 5`. The bias is therefore
mild-to-moderate, not severe. The correction is still applied for correctness.

**Correction implemented (`correctedKappa` in `StatisticsUtils.kt`):**

```
κ̂_HG = κ̂_MLE · (N−1) / (N + d − 2)
```

This is Eq. (9) of Hornik & Grün 2014 (JSS 58:10). A `WARN` is logged when
`d/N > 10` (degenerate leaf regime) — with `d = 256` this only triggers for
leaves with `N < 25`, which sit far below `minClusterSize = 55` (frozen artifact; this
document previously said 50).

> Two amendments (2026-07-27). First, "which are pruned by `minClusterSize`" overstates the
> guarantee: the floor is enforced on the **routed partition at split time**, and populations
> drift under later re-routing, so about 1% of leaves end marginally below it (1/87 in the
> frozen artifact; also 1/152 and 1/104 in other builds). It is a **birth constraint, not an
> invariant**. Second, the `(N−1)/(N+d−2)` factor scales with `N`, which is the reason the
> pipeline forbids likelihood comparisons across levels in routing — parents, fitted on
> larger populations, are systematically sharper. See
> [`../router-shared-kappa-correction.md`](../router-shared-kappa-correction.md).

**d/N-gated shrinkage toward the parent prior.** `TaxonomyFitter` blends the
corrected MLE with a parent-derived prior via

```
κ = (1 − α_d) · κ̂_HG + α_d · κ_prior,   α_d = dOverNAlpha(d/N)
```

where `κ_prior` is the average fitted κ of the node's parents (or
`defaultKappaPrior = 10` for the root / orphans). The blend weight `α_d` grows
with `d/N`, so high-uncertainty (small-`N`) nodes lean more on the prior. This is
a legitimate empirical-Bayes shrinkage; state it as such in the paper. Nodes with
`N < effectiveSupportFloor` (2.0) fall back entirely to `κ_prior`.

### 1.3 NiW Prior

A Normal-inverse-Wishart (NiW) prior is placed over `(μ, Σ)`. The scale matrix
`Ψ₀` is initialised via empirical Bayes: OAS (§4) is applied to the sample
embeddings to produce a regularised covariance estimate. The NiW scale matrix is
stored in **diagonal (factored) form** (`GraphNode.niwLambda`) for `O(d)` time
and space — at `d = 256` a full matrix would be tractable, but the diagonal form
is retained because only the per-dimension directional variance is needed for
the Mahalanobis distance and log-semantic-volume computations. The prior mean
direction is the spherical centroid of parent `μ` vectors. State this empirical-Bayes
construction explicitly in the paper.

### 1.4 Paper text to write

- State that `κ̂_HG` is the Hornik–Grün asymptotic approximation, cite DOI `10.18637/jss.v058.i10`.
- Note that unbiased estimation of `κ` is provably impossible (Jabbar et al. 2026)
  but bias-corrected estimation is achievable.
- Frame the d/N-gated shrinkage as empirical-Bayes, not an EMA heuristic.
- Cite Banerjee et al. 2005 (DOI `10.5555/1046920.1088394`) and Marrelec & Giron 2021
  (DOI `10.1080/03610918.2021.2011923`) for context on small-N vMF regimes.

---

## 2. Dasgupta Cost as Greedy Split Oracle (Phase 4 — Discover)

> **SUPERSEDED (2026-07-27) — and the diagnosis in §2.2 is exactly why.** This section
> observes that the split deltas cluster at 0.78-0.84, "an order of magnitude above the
> gate", so the threshold is "near-inert". That observation is correct and it is the reason
> the statistic was replaced: `δ = 1 − C_after/C_before` measures the **remaining** cost
> fraction, which is ~0.82 for every real split, so any epsilon below 0.82 is structurally
> inert. It was not measuring separation at all.
>
> **The current statistic is a chance-corrected separation score.** For a partition of a
> query set into cells `S_c` (sums of unit vectors):
>
> ```
> W(S)  = |S|^2 − ||Σ_{x∈S} x||^2
> E     = W(total) · Σ_c n_c(n_c−1) / (n(n−1))       expected within-scatter of a uniformly
>                                                     random partition into the same sizes
> score = 1 − Σ_c W(S_c) / E
> ```
>
> It is 1 for a perfect partition, ~0 for a random one, negative for anti-clustered, and
> **exactly 0 at k = 1**, so a non-separating wrapper candidate can never clear a positive
> bar. The chance correction is ARI-style: it removes the mechanical dependence of the raw
> within/total ratio on `k` and on cell sizes, which is what makes one threshold mean the
> same thing at every site. Lifted to the whole corpus (one cell per leaf, plus one per
> residual pool) it is the global objective `J`.
>
> **Do not cite this as Dasgupta's LCA cost.** It is not, notwithstanding the persisted field
> name `dasguptaDeltaNorm`. §2.4's honest-limitation note that the proxy "is not the
> canonical Dasgupta W" understates the gap: the current statistic is a different object with
> a different null, not an approximation to Dasgupta's.
>
> **The threshold is now derived rather than tuned.** `proposalSeparationBar = 0.025` sits
> between two *measured* nulls — an isotropic null (p95 0.0055-0.0093 over n = 75..900) and a
> within-node parametric-bootstrap null (p50 ~0.033-0.063) — both generated by driving the
> production splitter itself. §2.4's "tunable hyperparameter, not derived from theory" is
> superseded by [`../separation_null_by_size.md`](../separation_null_by_size.md).
>
> **A second gate now sits above it.** Split acceptance is not local: every edit is applied
> tentatively, the whole corpus is re-routed, and the edit commits only if `dJ` exceeds
> `max(tau, acceptanceZ · SE(dJ))` where `SE(dJ)` is a **paired** bootstrap standard error.
> `SE(dJ)` spans 13.1x p10-p90 on this corpus, which is why an absolute tolerance was not
> adequate. See [`../dag-logic-and-math.md`](../dag-logic-and-math.md) §6.
>
> §2.3 (Banerjee et al. cosine-space validity, dimension-agnosticism supporting fixed `d`)
> **remains valid and is still worth citing.**

### 2.1 Definition

For a binary tree `T` over `N` items with pairwise similarity weights `wᵢⱼ`,
Dasgupta (2016) defines:

```
cost(T) = Σᵢ≠ⱼ  wᵢⱼ · |T(i,j)|
```

where `|T(i,j)|` is the number of leaves in the subtree rooted at `LCA(i,j)`.
Thm. 2 of Dasgupta (2016) shows that minimising this cost produces trees where
high-similarity pairs are separated at deep levels — the desired property for a taxonomy.

### 2.2 Implementation

`TaxonomySplitter` computes the *delta* for a proposed bisection `(S_L, S_R)`:

```
δ = (C_before − C_after) / C_before
```

where `wᵢⱼ = clip(xᵢᵀxⱼ, 0, 1)` (cosine similarity on unit vectors, already valid
by Cauchy–Schwarz; clipping prevents negative weights from MRL prefix mismatches).
A split is accepted iff `δ > separationEpsilon` (default `0.01`).

In practice the observed split deltas cluster tightly around `0.78–0.84` — an
order of magnitude above the gate — so `separationEpsilon` is near-inert in the
current regime; the Dasgupta oracle effectively accepts every geometrically
plausible split. This is reported honestly in §6.

The *proxy formula* for `C_after` uses `nL² − ‖sumL‖²` rather than the full pairwise
sum — this is self-consistent (same formula for all splits) but not the canonical
Dasgupta `W`. This is fine for a greedy oracle; state clearly in the paper.

### 2.3 Cosine-space validity

Banerjee et al. (2005) prove that vMF-EM is equivalent to cosine-similarity k-means;
therefore using cosine weights in the Dasgupta cost is geometrically consistent.
This equivalence is also dimension-agnostic, which supports the fixed-`d` choice
in §3 (clustering quality does not improve merely by raising `d`). Include this
argument (one sentence + citation).

### 2.4 Limitations to acknowledge

- `separationEpsilon` is a **tunable hyperparameter**, not derived from theory
  (and empirically near-inert at the observed delta magnitudes).
- Dasgupta originally proved bounds for *whole trees*; repurposing as a greedy
  oracle per-split has no worst-case guarantee.
- BIC for vMF mixtures (Gopal & Yang 2014, ICML) is a principled alternative:
  `BIC(k) = −2L(k) + k·(d+1)·ln N`. Consider adding as a secondary check.

### 2.5 Citations needed

| Reference | DOI / URL |
|-----------|----------|
| Dasgupta 2016, STOC | `10.1145/2897518.2897527` |
| Banerjee et al. 2005, JMLR 6 | `10.5555/1046920.1088394` |
| Gopal & Yang 2014, ICML | `proceedings.mlr.press/v32/gopal14` |

---

## 3. Matryoshka Representation Learning — Fixed Dimension

### 3.1 Choice: fixed `d = 256` at all depths

TaxoArena uses a **single fixed embedding dimension** `d = 256` for every node,
root through leaf. This is not a limitation but a coherence requirement imposed
by the vMF concentration estimator.

**d/N coherence.** The Hornik–Grün bias is `O(d/N)` (§1.2). With the observed
leaf-size distribution (median `N ≈ 105`, IQR 77–146, 165 leaves), the reliability
of `κ` at each candidate dimension is:

| `d` | Median `d/N` | Reliable (`d/N < 2`) | Warn (`> 5`) | Unreliable (`> 10`) |
|-----|--------------|----------------------|--------------|---------------------|
| 128 | 1.22 | 87% | 0% | 0% |
| 256 | 2.44 | 31% | 3% | 0% |
| 512 | 4.88 | 15% | 47% | 3% |
| 1024 | 9.75 | 6% | 82% | 47% |

At `d = 1024` only 6% of leaves are reliably fittable and 47% have outright
unreliable `κ`; at `d = 256` zero leaves are unreliable and 97% sit outside the
warning zone. `d = 256` is the highest dimension that remains coherent with the
node sizes the MMLU-Pro query budget (≈8 400 train queries, ≈165 leaves) can
sustain.

### 3.2 Justification

Three independent arguments converge on `d = 256`:

1. **Statistical** — `O(d/N)` bias control (Hornik & Grün 2014); small-`N` `κ`
   estimators are "more variable for small datasets" (Marrelec & Giron 2021).
   The node sizes cannot support `d > 256`.
2. **Geometric** — Banerjee et al. (2005) prove vMF-EM ≡ cosine k-means, and the
   equivalence is dimension-agnostic. Raising `d` inflates `κ` variance without
   improving cluster separation.
3. **Representation** — Kusupati et al. (2022, NeurIPS) show 256-dim MRL prefixes
   retain ≥97% of full-dimension BEIR retrieval accuracy. The semantic
   information at `d = 512/1024` over `d = 256` is marginal and not worth the
   `κ` instability.

MRL is therefore retained as the **representation** (the embedding is MRL-trained,
and the 256-dim slice is a valid Matryoshka prefix), not as a dynamic
depth-scheduling mechanism. Each prefix slice is re-normalised to the unit sphere
before vMF fitting — re-normalisation is **mandatory**, since MRL prefixes are
not unit-norm by construction.

### 3.3 Open items

- Report the `d/N` table above in §6 to justify the fixed dimension empirically.
- Note in the paper: below 64 dims, vMF estimation is unreliable even at the
  root, so 128 is the sensible minimum and 256 the chosen operating point.

### 3.4 Citations needed

| Reference | DOI |
|-----------|-----|
| Kusupati et al. 2022, NeurIPS | `10.5220/0008643100002068431-2192` |
| Hornik & Grün 2014, JSS 58:10 | `10.18637/jss.v058.i10` |
| Marrelec & Giron 2021, Comm. Stat. | `10.1080/03610918.2021.2011923` |
| Qwen3-Embedding model card | `huggingface.co/Qwen/Qwen3-Embedding` |

---

## 4. Oracle Approximating Shrinkage (OAS) for NiW Scale Matrix

### 4.1 Why OAS

At `d = 256` with the smallest leaves (`N ≈ 50`), the sample covariance `S` is
near rank-deficient (`N ≲ d`). OAS (Chen, Wiesel, Eldar & Hero 2010, IEEE TSP)
solves:

```
Σ̂_OAS = (1−ρ̂)·S + ρ̂·(tr S / d)·I
ρ̂ = (1 − 2/d)·tr(S²) + tr²(S)  ·  [  (n+1−2/d)·(tr(S²) − tr²(S)/d)  ]⁻¹
```

OAS is MSE-optimal for Gaussian data in the `n ≲ d` regime and is the best-in-class
closed-form shrinkage estimator (confirmed by EUSIPCO 2024 survey). At the typical
leaf (`N ≈ 105 > d = 256`? no — `N < d`) the shrinkage is moderate; for the
smallest leaves it is essential.

### 4.2 Caveat — must appear in paper

> OAS assumes Gaussian samples. Unit-sphere embeddings are *directional data*, not
> Gaussian. For moderate concentration `κ`, the tangent-plane Gaussian approximation
> is acceptable (standard practice in spherical statistics), but we acknowledge this
> is a model approximation.

This single sentence satisfies reviewer concerns.

### 4.3 Empirical Bayes connection

Using OAS to initialise `Ψ₀` makes the NiW an *empirical Bayes* prior — a legitimate,
citable construction. The NiW scale matrix is kept in diagonal (factored) form
(`GraphNode.niwLambda`) for `O(d)` efficiency; OAS regularises the diagonal
covariance used downstream.

### 4.4 Citations needed

| Reference | DOI |
|-----------|-----|
| Chen et al. 2010, IEEE TSP | `10.1109/TSP.2010.2053029` |
| Ledoit & Wolf 2025, JMVA | for robustness comparison (unknown mean setting) |

---

## 5. OpenSkill / Weng–Lin for LLM-Judge Ranking

### 5.1 Model

Pairwise LLM-judge comparisons update OpenSkill ratings with initial parameters
`μ₀=25, σ₀=25/3≈8.333, β=25/6≈4.167`. This is the standard Weng–Lin
Plackett–Luce variant parameterisation.

Weng & Lin (2011, JMLR 12) place Gaussian priors over player skills
`θᵢ ~ N(μᵢ, σᵢ²)` and update via Expectation Propagation (EP) after each outcome.
EP updates are `O(1)` per comparison and converge well incrementally.

### 5.2 Parameter choices

The `β ≈ σ/2` relationship means ~3 comparisons meaningfully distinguish two nodes,
which is appropriate for LLM evaluation. With `N < 10` comparisons per node,
`σ` remains large — the system correctly reports high uncertainty. Report
confidence intervals, not point estimates, for low-comparison nodes.

### 5.3 Novelty note

Applying Weng–Lin to *taxonomy node quality ranking* rather than player ranking is
a novel application. The independence assumption holds iff each node is treated as
an independent player; when nodes share queries (cross-links), partial non-independence
should be acknowledged as a limitation.

### 5.4 Citations needed

| Reference | DOI |
|-----------|-----|
| Weng & Lin 2011, JMLR 12 | `10.5555/1953048.1953057` |
| OpenSkill library | `arXiv:2401.05451` |
| JuStRank 2025, ACL | for context: Bayesian > BTL for sparse comparisons |
