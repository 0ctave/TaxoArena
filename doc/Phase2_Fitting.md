# Phase 2: Fit (Context-Aware Distribution Modeling)

## 1. Hierarchical Mixture Modeling (HMM)
ArcTaxoAdapat models each node in the DAG not as a single Gaussian, but as a **Gaussian Mixture Model (GMM)**. This multi-centroid representation allows each node to capture internal semantic variance and multi-modal identities.

### 1.1 Multi-Centroid Components
A node $L$ is represented as a GMM with $K$ components:
$$ P(x | L) = \sum_{k=1}^{K} \pi_k \mathcal{N}(x | \mu_k, \Sigma_k) $$
Where $\pi_k$ is the mixture weight, $\mu_k$ is the component centroid, and $\Sigma_k$ is the diagonal covariance matrix.

## 2. Leaf Node Fitting
For terminal leaf nodes, the system utilizes two complementary models:

### 2.1 Multi-Centroid OAS
To ensure well-conditioned covariance matrices in 4096-dimensional space, ArcTaxoAdapat employs **Oracle Approximating Shrinkage (OAS)**. OAS calculates a shrinkage intensity $\rho$ to pull the empirical covariance towards an isotropic average, preventing singularities when the number of samples $N$ is much smaller than the dimensionality $D$.
$$ \Sigma_{OAS} = (1 - \rho) \Sigma_{emp} + \rho \frac{\text{Tr}(\Sigma_{emp})}{D} I $$

The system seeds up to `maxCentroidsPerNode` (default 3) by partitioning the data into dense clusters and fitting a separate OAS component to each.

### 2.2 Simplified Isolation Kernel (SIK)
Leaf nodes also maintain a **Simplified Isolation Kernel (SIK)** model. SIK uses $T$ random partition centers and an inclusion radius $\psi$ (based on the `sikPercentile`). This provides a non-parametric "envelope" for strict leaf inclusion, preventing distant outliers from being assigned to high-precision leaf domains.

## 3. Parent Node Fitting: Recursive Union
An internal parent node is fitted using a **Bottom-Up** traversal. Its distribution is the **Composite Union** of its children's already-fitted GMMs, plus its own residual query pool.

### 3.1 Structural Simplification
To prevent an exponential explosion of centroids in the root node, the system performs **GMM Simplification** after each union. Components with a `cosineSimilarity` higher than `tauMerge` (default 0.92) are fused into a single weighted average component.

### 3.2 Proportional Weighting
The mixture weights $\pi_k$ for a parent node are adjusted proportionally based on the sample count of its children, ensuring that larger sub-domains have a stronger influence on the parent's macro-domain boundaries.
