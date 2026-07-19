# Phase 2: Fit (vMF + NiW Posterior Estimation)

*Implemented in `TaxonomyFitter.kt`*

For every active node the fitter estimates two probabilistic models: a von Mises-Fisher (vMF) distribution that describes the directional mean and concentration of the node's query set on the unit hypersphere, and a Normal-inverse-Wishart (NiW) posterior that provides a Bayesian regularization envelope for that estimate.

---

## 1. MRL Dimension Schedule

Embedding slices follow the Matryoshka Representation Learning schedule tied to node depth:

| Depth | Slice dimension |
|-------|----------------|
| 0 (root) | 128 |
| 1 | 256 |
| 2 | 512 |
| 3 + | 1024 |

Each slice is renormalized to the unit hypersphere before any distance or density computation: \(\hat{\mathbf{x}} = \mathbf{x}_{[1:d]} \;/\; \lVert \mathbf{x}_{[1:d]} \rVert_2\). Renormalization is mandatory because MRL prefix slices are not unit-norm by construction (Kusupati et al., NeurIPS 2022).

---

## 2. vMF Parameter Estimation

Each node is modelled as a single-component vMF distribution on \(\mathcal{S}^{d-1}\):

\[
p(\hat{\mathbf{x}} \mid \boldsymbol{\mu}, \kappa) = C_d(\kappa)\, \exp\!\left(\kappa\, \boldsymbol{\mu}^\top \hat{\mathbf{x}}\right)
\]

where \(C_d(\kappa) = \kappa^{d/2-1} \;/\; \bigl((2\pi)^{d/2} I_{d/2-1}(\kappa)\bigr)\) and \(I_\nu\) is the modified Bessel function of the first kind.

### 2.1 Mean Direction MLE

\[
\hat{\boldsymbol{\mu}} = \frac{\sum_{i=1}^{N} \hat{\mathbf{x}}_i}{\left\lVert \sum_{i=1}^{N} \hat{\mathbf{x}}_i \right\rVert_2}, \qquad \bar{R} = \frac{\left\lVert \sum_{i=1}^{N} \hat{\mathbf{x}}_i \right\rVert_2}{N}
\]

### 2.2 Concentration MLE with Hornik–Grün Shrinkage

The raw Banerjee closed-form approximation to the MLE (Banerjee et al., JMLR 2005) is:

\[
\hat{\kappa}_{\text{MLE}} = \frac{\bar{R}(d - \bar{R}^2)}{1 - \bar{R}^2}
\]

Because the bias of \(\hat{\kappa}_{\text{MLE}}\) is \(O(d/N)\), a multiplicative shrinkage correction (Hornik & Grün, JSS 2014, Eq. 9) is applied in `correctedKappa`:

\[
\hat{\kappa} = \hat{\kappa}_{\text{MLE}} \cdot \frac{N-1}{N+d-2}
\]

The correction is material at depth ≥ 2 where \(d/N \gg 1\) (e.g., \(d=1024\), \(N \approx 20\) → \(d/N \approx 51\)).

### 2.3 EMA Stabilization Heuristic

To prevent oscillation across iterations, a sample-weight-gated exponential moving average is applied to \(\kappa\):

\[
\alpha_{\text{eff}} = \alpha_{\text{EMA}} \cdot \min\!\left(1,\, \frac{N}{4 \cdot N_{\min}}\right), \qquad \kappa_{\text{new}} = (1 - \alpha_{\text{eff}})\,\hat{\kappa} + \alpha_{\text{eff}}\,\kappa_{\text{old}}
\]

This is a stabilization heuristic with no statistical derivation; it does not correspond to any vMF MLE and should be treated as an engineering choice.

---

## 3. NiW Posterior (Diagonal Approximation)

At \(d \gg N\) the full \(d \times d\) NiW scale matrix is singular and infeasible to store. The fitter uses an **empirical-Bayes diagonal NiW** prior, initializing \(\mathbf{\Lambda}_0\) with the OAS-shrunk diagonal of the sample covariance (Chen et al., IEEE TSP 2010):

\[
\hat{\boldsymbol{\Sigma}}_{\text{OAS}} = (1 - \hat{\rho})\mathbf{S} + \hat{\rho}\,\frac{\operatorname{tr}(\mathbf{S})}{d}\mathbf{I}
\]

The prior mean direction \(\mathbf{m}_0\) is the spherical average of all parent vMF means (for DAG nodes with multiple parents, \(\mathbf{m}_0 = \text{normalize}(\sum_p \boldsymbol{\mu}_p / |\text{parents}|)\)).

Diagonal NiW update equations:

\[
\kappa_N = \kappa_0 + N, \qquad \nu_N = \nu_0 + N
\]
\[
\mathbf{m}_N = \frac{\kappa_0 \mathbf{m}_0 + N\bar{\mathbf{x}}}{\kappa_N}
\]
\[
\lambda_{N,i} = \lambda_{0,i} + \sum_{j=1}^{N}(x_{ji} - \bar{x}_i)^2 + \frac{\kappa_0 N}{\kappa_N}(\bar{x}_i - m_{0,i})^2
\]

The posterior predictive is a Student-t distribution with \(\nu_N - d + 1\) degrees of freedom, which provides calibrated uncertainty estimates at leaf nodes where \(N\) is small.

---

## 4. Recursive Application

`fitNodeRecursive` applies the vMF + NiW update to every node in the subtree (DFS), setting `PHASE_VMF_FIT` on each node. A node whose `sliceDim` changed due to a depth reassignment (passthrough collapse) has `PHASE_VMF_FIT` cleared and is re-fit at the correct dimension.
