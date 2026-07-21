# vMF & NiW Fitting — Implementation Reference

> **Scope:** implementation details of the vMF fit and the Normal-Inverse-Wishart
> posterior in TaxoArena. The statistical **derivations** (model, MLE, bias
> correction, d/N-gated prior blend, OAS) live in
> [`../paper/MATHEMATICAL_FOUNDATIONS.md`](../paper/MATHEMATICAL_FOUNDATIONS.md);
> this document covers the numerical approximations, the recursive NiW update,
> and the code locations. The embedding dimension is fixed at `d = 256`.

---

## 1. vMF Normalizer & Log-Bessel Approximation

The vMF density and its normalization constant are derived in
[Mathematical Foundations §1.1](../paper/MATHEMATICAL_FOUNDATIONS.md). Evaluating
the normalizer requires the modified Bessel function `I_ν(κ)` with
`ν = d/2 − 1`. TaxoArena evaluates it in log-space via the **Debye uniform
asymptotic approximation** (numerically stable, avoids overflow/underflow):

$$ \ln C_d(\kappa) = \nu \ln \kappa - \frac{d}{2} \ln(2\pi) - \ln I_{\nu}(\kappa) $$

with the Debye approximation of `ln I_ν(κ)` computed in
[`StatisticsUtils.logBesselI`](../../src/main/kotlin/taxonomy/utils/StatisticsUtils.kt):

$$ \ln I_{\nu}(\kappa) \approx \nu \eta - \frac{1}{2} \ln(2\pi\nu) - \frac{1}{4} \ln(1 + z^2) $$

where `z = κ/ν` and `η = √(1+z²) + ln(z / (1+√(1+z²)))`.

---

## 2. Concentration Estimation (`StatisticsUtils.correctedKappa`)

Given `n` unit-norm projected vectors, the mean resultant length is
`R̄ = ‖∑xᵢ‖/n` and the MLE for the mean direction is `μ = R/‖R‖`.

The concentration is estimated in three steps inside
[`correctedKappa`](../../src/main/kotlin/taxonomy/utils/StatisticsUtils.kt):

1. **Banerjee closed-form MLE** (inverts `A_d(κ) = R̄`):

   $$ \kappa_{ML} \approx \bar{R}\,\frac{d - \bar{R}^2}{1 - \bar{R}^2} $$

2. **Hornik–Grün shrinkage** (single factor, the `O(d/N)` bias correction of
   Hornik & Grün 2014, Eq. 9 — see
   [Mathematical Foundations §1.2](../paper/MATHEMATICAL_FOUNDATIONS.md)):

   $$ \kappa_{HG} = \kappa_{ML} \cdot \frac{n - 1}{n + d - 2} $$

3. **Clamp** to `[1e-3, 1e4]` (`κ_min` for the uniform/degenerate case when
   `R̄ ≤ 0`; `κ_max` for the spike case when `R̄ ≥ 1`).

A `WARN` is logged when `d/N > 10` (degenerate leaf regime); with `d = 256` and
`minClusterSize = 50` this is rare. The separate **d/N-gated prior blend**
(`(1−α_d)·κ_HG + α_d·κ_prior`, performed in `TaxonomyFitter`) is described in
[Mathematical Foundations §1.2](../paper/MATHEMATICAL_FOUNDATIONS.md).

---

## 3. Normal-Inverse-Wishart (NiW) Diagonal Posterior

TaxoArena models per-node directional variance with a Normal-Inverse-Wishart
conjugate prior, stored in **diagonal (factored) form** as
`GraphNode.niwLambda` for `O(d)` time and space. The prior parameters are derived
from the parent node's vMF mean `μ_parent` and concentration `κ_parent`:

- `κ₀ = 1.0`
- `ν₀ = d + 2`
- `Λ = 1 / (κ̄_parent · d)` (diagonal prior variance scale, `κ̄_parent` = average
  parent concentration)

Given the sample mean `x̄ = (1/n)∑xᵢ`, the posterior parameters update as:

$$ \kappa_N = \kappa_0 + n, \qquad \nu_N = \nu_0 + n, \qquad m_N = \frac{\kappa_0 m_0 + n \bar{x}}{\kappa_N} $$

The diagonal posterior scale elements are:

$$ \Lambda_{N,i} = \Lambda + \sum_{j=1}^{n}(x_{j,i} - \bar{x}_i)^2 + \frac{\kappa_0\, n}{\kappa_N}(\bar{x}_i - m_{0,i})^2 $$

These diagonal values represent per-dimension directional variance and feed the
log-semantic-volume and Mahalanobis-distance computations. The OAS-regularised
initialisation of `Ψ₀` is covered in
[Mathematical Foundations §4](../paper/MATHEMATICAL_FOUNDATIONS.md).

---

## Related Code References

- [`StatisticsUtils`](../../src/main/kotlin/taxonomy/utils/StatisticsUtils.kt) — Bessel ratios, Banerjee MLE, Hornik–Grün correction, Debye approximation.
- [`TaxonomyFitter`](../../src/main/kotlin/taxonomy/operations/TaxonomyFitter.kt) — level-by-level vMF fits, d/N-gated prior blend, NiW diagonal updates.
- [`GraphNode`](../../src/main/kotlin/taxonomy/model/GraphNode.kt) — `niwLambda` diagonal scale storage.
