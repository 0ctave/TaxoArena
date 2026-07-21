# Trickle Routing: Top-Down Soft Routing Mechanics

This document details the log-space soft routing mechanics used to distribute queries through the Directed Acyclic Graph (DAG) in **TaxoArena**. It formalizes the sibling scoring model, temperature scaling, Laplace smoothing, and the path prune filter.

---

## 1.Symmetric Sibling Scoring

During routing, when a query $q$ (with projected embedding vector $x$ at target dimension $d$) is evaluated at an internal node $P$, its child nodes $\{C_1, C_2, \dots, C_K\}$ compete to absorb the query.

To ensure sibling likelihoods are directly comparable and not distorted by localized variance in cluster density, we define a **shared sibling concentration** $\bar{\kappa}_{\text{siblings}}$:

$$ \bar{\kappa}_{\text{siblings}} = \frac{1}{K} \sum_{i=1}^{K} \kappa_{C_i} $$

We cap this value within $[1.0, 100.0]$. Sibling scores are then computed in log-space using the shared concentration and its corresponding vMF normalizer $\ln C_d(\bar{\kappa}_{\text{siblings}})$:

$$ f_i(x) = \ln C_d(\bar{\kappa}_{\text{siblings}}) + \bar{\kappa}_{\text{siblings}} \cdot (x^T \mu_{C_i}) $$

where:
*   $\mu_{C_i}$ is the unit mean direction vector of child $C_i$.
*   $x^T \mu_{C_i}$ is the cosine similarity between the query projection and the child centroid.

### Ground-Truth Guidance Bias
In the first iteration of the pipeline (iteration $\le 1$), if a query carries a ground-truth tag that matches a child's original category label, we inject a guidance bias:

$$ f_i(x) \leftarrow f_i(x) + \ln \left( \frac{1.0}{0.7} \right) \approx f_i(x) + 0.3567 $$

This acts as a soft seed, encouraging queries to route to their correct taxonomic branches initially to form stable centroids.

---

## 2. Temperature-Scaled Softmax & Laplace Regularization

Once raw sibling scores $f_i(x)$ are computed, they are normalized into a probability distribution.

### Softmax Temperature Scaling
To adjust routing selectivity, we divide raw scores by a temperature parameter $\tau > 0$ (default $2.0$):

$$ P_i = \frac{\exp(f_i(x) / \tau)}{\sum_{j=1}^{K} \exp(f_j(x) / \tau)} $$

In the codebase, this is computed safely in log-space using the Log-Sum-Exp identity to prevent numerical underflow or overflow.

### Laplace Regularization (Safety Valve)
To ensure that search pathways are not completely zeroed out due to minor embedding deviations, we smooth the softmax outputs using a Laplace-style regularizer:

$$ P'_i = \frac{P_i + \epsilon_{\text{Laplace}}}{1.0 + K \cdot \epsilon_{\text{Laplace}}} $$

where:
*   $K$ is the number of sibling choices.
*   $\epsilon_{\text{Laplace}} = \frac{0.05}{K}$.

This Laplace correction guarantees a minimum exploration probability for every child, acting as a safety valve.

---

## 3. Recursive Path Accumulation & Leaf Filtering

The trickle router traverses the DAG recursively. The log-probability of reaching any node $N$ is the sum of path decisions:

$$ \ln P(N) = \ln P(\text{Parent}) + \ln P'_{N \mid \text{Parent}} $$

At the Root node (depth 0), the log-probability is initialized to $0.0$.

### The Assignment Margin Filter
Once all reachable nodes are traversed, we identify the set of reached leaf nodes. Let $\ln P_{\text{best}}$ be the highest path log-probability among all leaves:

$$ \ln P_{\text{best}} = \max_{L \in \text{Leaves}} \ln P(L) $$

We filter out leaves that deviate significantly from this optimal path. A leaf $L$ is assigned the query only if its path log-probability lies within the configured **assignment cosine gap** boundary ($g_{\text{assign}}$, default $0.03$):

$$ \ln P(L) \ge \ln P_{\text{best}} - g_{\text{assign}} $$

Queries that satisfy this gate are assigned to the leaf. If multiple leaves pass, the query is assigned polyhierarchically to all of them. The final assignment log-probabilities are then normalized across the surviving leaves so that their linear sum equals $1.0$.

---

## 🔗 Related Code References
*   [TaxonomyTrickler](../../src/main/kotlin/taxonomy/operations/TaxonomyTrickler.kt): Contains the recursive routing logic and log-space softmax updates.
