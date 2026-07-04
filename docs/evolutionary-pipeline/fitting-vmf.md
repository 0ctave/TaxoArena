# von Mises–Fisher (vMF) & Normal-Inverse-Wishart (NiW) Mathematical Fitting

This document details the mathematical formulas, approximations, and algorithms used in **TaxoArena** for spherical statistical modeling. It covers the von Mises-Fisher (vMF) distribution fitting, small-sample bias corrections, log-Bessel computations, and the recursive updating of the Normal-Inverse-Wishart (NiW) posterior.

---

## 1. The von Mises–Fisher (vMF) Model

The von Mises-Fisher distribution models directional data on the unit hypersphere $S^{d-1} \subset \mathbb{R}^d$. For a unit vector $x \in S^{d-1}$, the probability density is defined as:

$$ f(x \mid \mu, \kappa) = C_d(\kappa) \exp(\kappa \mu^T x) $$

where:
*   $\mu \in S^{d-1}$ is the unit mean direction vector ($\|\mu\| = 1$).
*   $\kappa \ge 0$ is the concentration parameter.
*   $C_d(\kappa)$ is the normalization constant.

### Normalization Constant & Log-Bessel Approximation
The normalization constant is given by:

$$ C_d(\kappa) = \frac{\kappa^{d/2 - 1}}{(2\pi)^{d/2} I_{d/2 - 1}(\kappa)} $$

where $I_{\nu}(\kappa)$ is the modified Bessel function of the first kind of order $\nu = d/2 - 1$. 

In high dimensions (e.g., $d \ge 1024$), computing $I_{\nu}(\kappa)$ directly causes numerical overflow or underflow. TaxoArena evaluates the normalizer in log-space using the **Debye uniform asymptotic approximation**:

$$ \ln C_d(\kappa) = \nu \ln \kappa - \frac{d}{2} \ln(2\pi) - \ln I_{\nu}(\kappa) $$

where the Debye approximation of $\ln I_{\nu}(\kappa)$ is computed in [StatisticsUtils.logBesselI](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt):

$$ \ln I_{\nu}(\kappa) \approx \nu \eta - \frac{1}{2} \ln(2\pi\nu) - \frac{1}{4} \ln(1 + z^2) $$

where $z = \kappa/\nu$ and $\eta = \sqrt{1+z^2} + \ln\left(\frac{z}{1+\sqrt{1+z^2}}\right)$.

---

## 2. Parameter Estimation & Bias Corrections

Given a set of $n$ unit-norm projected vectors $\{x_1, x_2, \dots, x_n\} \subset S^{d-1}$, the resultant sum vector is:

$$ R = \sum_{i=1}^n x_i $$

The mean resultant length is $\bar{R} = \frac{\|R\|}{n}$, and the Maximum Likelihood Estimate (MLE) for the mean direction is:

$$ \mu = \frac{R}{\|R\|} $$

### Banerjee Closed-Form Kappa Estimation
The MLE for the concentration parameter $\kappa$ requires inverting the ratio of Bessel functions: $A_d(\kappa) = \bar{R}$. Because this is transcendental, we use the Banerjee closed-form approximation:

$$ \kappa_{ML} \approx \bar{R} \frac{d - \bar{R}^2}{1 - \bar{R}^2} $$

### Small-Sample Shrinkage Correction
To prevent over-concentration when the sample size $n$ is small relative to the dimension $d$, we scale $\kappa_{ML}$ by a shrinkage factor:

$$ \kappa = \kappa_{ML} \cdot \left( \frac{n - 1}{n + d - 2} \right) $$

This is capped at $\kappa_{max} = 10^4$ and floored at $\kappa_{min} = 10^{-3}$.

### Hornik & Grün (2014) Bias Correction
In high-dimensional spaces, the MLE $\hat{\kappa}$ carries a positive bias of order $O(d/n)$. At deeper levels of the taxonomy DAG (where $d$ is large and $n$ is small, e.g., $d=1024, n \approx 15 \dots 30$), $\kappa$ is over-estimated. This makes leaf nodes appear more cohesive than they are.

Following Hornik & Grün (2014) (*Journal of Statistical Software*), when the ratio $d/n > 5.0$, we apply a second shrinkage step:

$$ \kappa_{\text{corrected}} = \kappa \cdot \left( \frac{n - 1}{n + d - 2} \right) $$

If $d/n > 10.0$, the estimation is flagged as unreliable, and the prior dominates. This is implemented in [StatisticsUtils.biasCorrectKappa](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt).

---

## 3. Normal-Inverse-Wishart (NiW) Posterior Updates

To perform Bayesian soft routing, TaxoArena models the covariance structure of each node using a Normal-Inverse-Wishart (NiW) conjugate prior. This regularizes the covariance estimation in high dimensions where the sample covariance would otherwise be singular.

For a node $N$, we project the query vectors onto the node's slice dimension $d$. We calculate the prior parameters $(m_0, \kappa_0, \nu_0, \Lambda)$ using the parent node's vMF mean vector $\mu_{parent}$ and concentration $\kappa_{parent}$:
*   $\kappa_0 = 1.0$
*   $\nu_0 = d + 2$
*   $\Lambda = \frac{1}{\bar{\kappa}_{parent} \cdot d}$ (acts as diagonal prior variance scale, where $\bar{\kappa}_{parent}$ is the average parent concentration)

Given sample mean vector $\bar{x} = \frac{1}{n} \sum_{i=1}^n x_i$, the posterior parameters $(m_N, \kappa_N, \nu_N, \Lambda_N)$ are updated as follows:

$$ \kappa_N = \kappa_0 + n $$

$$ \nu_N = \nu_0 + n $$

$$ m_N = \frac{\kappa_0 m_0 + n \bar{x}}{\kappa_N} $$

For the scale matrix $\Lambda_N$, we assume a diagonal covariance structure to maintain computational efficiency in high dimensions ($O(d)$ time and space). The diagonal elements $\Lambda_{N, i}$ are updated as:

$$ \Lambda_{N, i} = \Lambda + \sum_{j=1}^n (x_{j, i} - \bar{x}_i)^2 + \frac{\kappa_0 n}{\kappa_N} (\bar{x}_i - m_{0, i})^2 $$

These diagonal posterior scale values represent the directional variance. They are saved in `GraphNode.niwLambda` and are used to compute the log-semantic volume and Mahalanobis distances.

---

## 🔗 Related Code References
*   [StatisticsUtils](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/utils/StatisticsUtils.kt): Implements Bessel ratios, Banerjee approximation, Hornik & Grün correction, and Debye approximation.
*   [TaxonomyFitter](file:///Z:/FAC/TUBerlin/THESIS/TaxoArena/src/main/kotlin/taxonomy/operations/TaxonomyFitter.kt): Executes level-by-level vMF and NiW updates.
