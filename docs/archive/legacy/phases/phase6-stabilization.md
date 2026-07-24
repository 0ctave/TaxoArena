# Phase 6: Stabilize (Convergence Assessment)

*Implemented in `TaxonomyStabilizer.kt`*

Stabilize measures whether the taxonomy has reached a fixed point by combining a structural Graph Edit Distance (GED) criterion with a log-semantic-volume tracking signal. Early stopping fires only when both criteria are met for a required number of consecutive iterations.

---

## 1. Structural GED

The GED between iteration \(t\) and \(t-1\) counts symmetric differences in the DAG's node and relation sets:

\[
\text{GED}(t) = |V_t \triangle V_{t-1}| + |E_t \triangle E_{t-1}|
\]

where \(V_t\) = set of node IDs and \(E_t\) = set of parent-child pairs at iteration \(t\). GED is normalized by total edge count to get a relative change:

\[
\widetilde{\text{GED}}(t) = \frac{\text{GED}(t)}{|E_t|}
\]

---

## 2. Log-Semantic Volume

For each leaf node \(\ell\), the log-semantic volume is computed as a function of its vMF and NiW parameters (see `StatisticsUtils.calculateLogSemanticVolume`). The total volume over all leaves is:

\[
\mathcal{V}(t) = \sum_{\ell \in \text{Leaves}(t)} \log\operatorname{SemanticVolume}(\ell)
\]

The absolute and relative volume changes are tracked:

\[
\Delta\mathcal{V}(t) = |\mathcal{V}(t) - \mathcal{V}(t-1)|, \qquad \delta\mathcal{V}(t) = \frac{\Delta\mathcal{V}(t)}{|\mathcal{V}(t-1)|}
\]

A decreasing \(\mathcal{V}\) over iterations corresponds to the vMF mixture tightening around its query set — the probabilistic analogue of inertia reduction in k-means.

---

## 3. Convergence Decision

Early stopping is allowed only after a minimum number of iterations that scales with the breadth of the taxonomy:

\[
t_{\min} = \max\!\left(5,\, \lfloor 0.8 \cdot |\text{depth-1 nodes}| \rfloor\right)
\]

After \(t_{\min}\) iterations, the single-iteration convergence flag is set when:

\[
\widetilde{\text{GED}}(t) \leq \theta_{\text{GED}} \qquad (\text{config: `gedThreshold`})
\]

Early stopping fires only if `enableEarlyStopping = true` and the flag has been set for \(M = 5\) **consecutive** iterations:

\[
\text{converged} = \mathbb{1}\!\left[\sum_{s=t-M+1}^{t} \mathbb{1}[\widetilde{\text{GED}}(s) \leq \theta_{\text{GED}}] = M\right]
\]

The consecutive-count requirement prevents premature termination during transient lulls in structural change (e.g., a single iteration where no split passes the Dasgupta threshold by coincidence).

---

## 4. State Tracking

The stabilizer maintains:
- `prevNodes: Set<String>` — node IDs from the previous iteration.
- `prevRelations: Set<Pair<String,String>>` — edges from the previous iteration.
- `prevVolume: Double` — total log-semantic volume from the previous iteration.
- `consecutiveConvergedCount: Int` — streak counter, reset to 0 whenever \(\widetilde{\text{GED}} > \theta_{\text{GED}}\).

`reset()` must be called at the start of each new adaptation run to clear all tracking state.
