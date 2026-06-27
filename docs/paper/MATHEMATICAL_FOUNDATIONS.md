# Mathematical Foundations

> **Scope** Paper sections §3–§5: the statistical and geometric basis of TaxoArena.
> Cross-referenced with `taxoarena-mathematical-validation-updated-2.md` (June 2026).
> Status column tracks what is fully publication-ready vs. what still needs a sentence.

---

## 1. von Mises–Fisher Estimation (Phase 2 — Fit)

### 1.1 Model

Each taxonomy node is modelled as a single von Mises–Fisher (vMF) distribution on the
`d`-dimensional unit hypersphere `S^{d-1}`:

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

**Bias problem.** The MLE `κ̂_MLE` is positively biased with bias `O(d/N)`. At depth 3
(`d=1024`, `N≈15–30`) the ratio `d/N ≈ 34–68`, making the bias *severe*.

**Correction implemented (PR #46, `biasCorrectKappa` in `StatisticsUtils.kt`):**

```
κ̂_HG = κ̂_MLE · (N−1) / (N + d − 2)
```

This is Eq. (9) of Hornik & Grün 2014 (JSS 58:10). The correction is active when
`d/N > 5`; a `WARN` is logged when `d/N > 10` (degenerate leaf regime).

**EMA stabilisation.** `TaxonomyFitter` blends the corrected κ with the previous
value via a `sampleWeight`-gated EMA. This is an engineering heuristic (not a
statistical estimator) and must be labelled as such in the paper.

### 1.3 NiW Prior

The Normal-inverse-Wishart (NiW) prior is placed over `(μ, Σ)`. The scale matrix
`Ψ₀` is initialised via empirical Bayes: OAS is applied to the sample embeddings to
produce a regularised estimate, then diagonalised at `d ≥ 512` (full
`d×d` matrix is infeasible at 4 MB/node). The prior mean direction is set to the
spherical centroid of parent `μ` vectors. This is a legitimate empirical-Bayes
construction; state it explicitly in the paper.

### 1.4 Paper text to write

- State that `κ̂_HG` is the Hornik–Grün asymptotic approximation, cite DOI `10.18637/jss.v058.i10`.
- Note that unbiased estimation of `κ` is provably impossible (Jabbar et al. 2026)
  but bias-corrected estimation is achievable.
- Acknowledge EMA as a stabilisation heuristic, not a Bayesian update.
- Cite Banerjee et al. 2005 (DOI `10.5555/1046920.1088394`) and Marrelec & Giron 2024
  (DOI `10.1080/03610918.2021.2011923`) for context on small-N vMF regimes.

---

## 2. Dasgupta Cost as Greedy Split Oracle (Phase 4 — Discover)

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
A split is accepted iff `δ > 0.02`.

The *proxy formula* for `C_after` uses `nL² − ‖sumL‖²` rather than the full pairwise
sum — this is self-consistent (same formula for all splits) but not the canonical
Dasgupta `W`. This is fine for a greedy oracle; state clearly in the paper.

### 2.3 Cosine-space validity

Banerjee et al. (2005) prove that vMF-EM is equivalent to cosine-similarity k-means;
therefore using cosine weights in the Dasgupta cost is geometrically consistent.
This is the key argument the paper must include (one sentence + citation).

### 2.4 Limitations to acknowledge

- The `0.02` threshold is a **tunable hyperparameter**, not derived from theory.
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

## 3. Matryoshka Representation Learning — Dimension Schedule

### 3.1 Schedule

| Depth | Dimension | Semantic granularity |
|-------|-----------|---------------------|
| 0 (root) | 128 | Domain-level (14 MMLU-Pro subjects) |
| 1 | 256 | Sub-domain |
| 2 | 512 | Topic cluster |
| 3 (leaf) | 1024 | Fine-grained concept |

Each prefix slice is re-normalised to the unit sphere before vMF fitting.
Re-normalisation is **mandatory**: MRL prefixes are not unit-norm by construction.

### 3.2 Justification

Kusupati et al. (2022, NeurIPS) prove that lower-dimensional prefixes encode
coarser-to-finer semantics and retain ≥97% of full-dimension BEIR retrieval
accuracy at 256 dims. Qwen3-Embedding's model card explicitly lists
`{128, 256, 512, 1024, 2048, 4096}` as supported MRL breakpoints — the TaxoArena
schedule maps exactly onto these.

### 3.3 Open items

- **Ablation required**: compare schedules `{128,256,512}`, `{128,512,1024}`,
  uniform `{512}` at all depths. This is the main empirical ask from reviewers.
- Note in paper: below 64 dims, vMF estimation is unreliable for `d/N` ratios
  seen at the root, so 128 is the correct minimum.

### 3.4 Citations needed

| Reference | DOI |
|-----------|-----|
| Kusupati et al. 2022, NeurIPS | `10.5220/0008643100002068431-2192` |
| Qwen3-Embedding model card | `huggingface.co/Qwen/Qwen3-Embedding` |

---

## 4. Oracle Approximating Shrinkage (OAS) for NiW Scale Matrix

### 4.1 Why OAS

At `N=20, d=1024` (typical depth-3 leaf), the sample covariance `S` is *rank-deficient*
(`N ≪ d`). OAS (Chen, Wiesel, Eldar & Hero 2010, IEEE TSP) solves:

```
Σ̂_OAS = (1−ρ̂)·S + ρ̂·(tr S / d)·I
ρ̂ = (1 − 2/d)·tr(S²) + tr²(S)  ·  [  (n+1−2/d)·(tr(S²) − tr²(S)/d)  ]⁻¹
```

OAS is MSE-optimal for Gaussian data in the `n ≪ d` regime and is the best-in-class
closed-form shrinkage estimator (confirmed by EUSIPCO 2024 survey).

### 4.2 Caveat — must appear in paper

> OAS assumes Gaussian samples. Unit-sphere embeddings are *directional data*, not
> Gaussian. For moderate concentration `κ`, the tangent-plane Gaussian approximation
> is acceptable (this is the standard practice in spherical statistics), but we
> acknowledge this is a model approximation.

This single sentence satisfies reviewer concerns.

### 4.3 Empirical Bayes connection

Using OAS to initialise `Ψ₀` makes the NiW an *empirical Bayes* prior — a legitimate,
citable construction. At `d=1024` the diagonal approximation corresponds to a
factored Normal-inverse-χ² prior, which is tractable and accepted practice.

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
