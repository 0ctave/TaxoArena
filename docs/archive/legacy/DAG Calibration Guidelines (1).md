# DAG Parameter Calibration Guidelines (v2 — judge-centric)

> **Reframe.** The DAG is not tuned for flat classification accuracy. It is an
> instrument for producing **granular, sufficiently-supported, semantically
> coherent leaf judges**. Calibration therefore targets **construction coherence
> (DQ1)** and **leaf statistical sufficiency**, with the **trickle test** as a
> held-out confirmation. RQ1/RQ2 (arena rankings vs MMLU-Pro) are downstream and
> are NOT tuned on — they are too expensive and conflated with judge-model quality.
>
> Supersedes v1 (Macro-F1 / contamination / AvgMatch objective). Aligned to the
> thesis design: RQ1 (C1), RQ2 (C1 vs C2), DQ1, trickle test, 60/15/25 split,
> seeds {42, 137, 2048}.

---

## 1. Calibration objective

Maximize **leaf coherence** subject to **statistical sufficiency** and
**coverage** gates — all measured on the construction + tuning-validation subsets
(75%) only.

| Goal | Metric(s) | Direction | Source |
|---|---|---|---|
| Coherence (DQ1) | Weighted Leaf Purity, Spherical Silhouette, Total Dasgupta Cost, Normalised Sackin | WLP↑, Sil↑, Dasgupta↓, Sackin≈balanced | headless runner |
| Routing calibration | Routing ECE (softmax vs GT domain) | ↓ | headless runner |
| Leaf sufficiency | leaf-size distribution, median support, % leaves below BT floor | median↑, tail↓ | headless runner |
| Coverage | % queries reaching ≥1 leaf; multi-path rate (AvgMatch) | ≥95%; [1.5, 4] | headless runner |
| **Held-out confirmation** | **Trickle test** (out-of-sample routing-vs-label agreement on 25%) | report only — **do not tune on this** | headless runner |

**Baselines are mandatory for DQ1:** every sweep runs `runBaselines = true`
(flat k-means, HAC-Ward, random-null). Coherence gates are *relative* — WLP and
Silhouette must beat the flat baselines at matched leaf count, otherwise the
induced structure is not non-trivially better than simple unsupervised
alternatives (§5.8).

---

## 2. The granularity / support trade-off (the hinge)

This is the central tension for "granular judges":

- **More leaves (granularity)** → tighter, more specialized rubrics → better
  judge specialization.
- **Fewer queries per leaf (support)** → Bradley–Terry standard errors fail to
  converge → rankings not statistically identifiable → RQ1 meaningless.

The frontier is set by `minClusterSize` (granularity floor) and
`deltaAssign`/`assignmentCosineGap` (multi-path breadth). Calibrate along this
frontier, not against flat accuracy.

**Sufficiency gate (hard):** for BT SEs to converge, every selected leaf needs
enough *held-out* matches. Rule of thumb: median held-out support per selected
leaf ≥ ~12 queries × the pairwise budget, and 0% of selected leaves below the BT
identifiability floor. Report BT SEs + convergence rate for the selected nodes
before running RQ1.

---

## 3. Knob classification

### TUNE (L9 core = 4 factors × 3 levels, + 1 ablation)

| Knob | Role | L9 levels | Why it moves the front |
|---|---|---|---|
| `minClusterSize` | granularity / support hinge | {50, 75, 100} | d/N-safe range (N≥50 → d/N≤5.12 at d=256); trades leaf count vs support |
| `routingSoftmaxTau` | sibling softmax temperature | {1.0, 1.5, 2.0} | routing sharpness → trickle agreement + multi-path |
| `assignmentCosineGap` | leaf-acceptance margin | {0.10, 0.15, 0.20} | secondary-assignment gate → polyhierarchy breadth |
| `deltaAssign` | internal traversal margin | {0.5, 1.0, 2.0} | multi-path traversal; the coverage knob |
| `tauKappaScalingFactor` | κ-adaptive temperature (`dynamicTau=τ·κ^γ`) | {0.0, 0.5, 1.0} | **ablation only** (3-row table), not in the L9 |

> `minClusterSize` is promoted to TUNE (was fixed in v1). It is the single most
> important knob for the granular-judge claim. The d/N coherence constraint sets
> the *floor* (50), not the operating point.

### FIX (structural / coherence constants — document, don't tune)

| Knob | Fixed value | Justification |
|---|---|---|
| `maxDepth` | 8 | cap only; early stopping converges ~depth 4–5 |
| `separationEpsilon` | see §4 | Dasgupta delta gate — verify it binds, else fix as floor |
| `effectiveSupportFloor` | 2.0 | starved-leaf prior guard |
| `fusionSimilarityThreshold` | 0.92 | sibling-merge cosine gate |
| `defaultKappaPrior` | 10.0 | root/orphan prior fallback (d/N-gated blend handles the rest) |
| `maxLeafAssignments` | 5 | safety cap |
| `gedThreshold` | 0.005 | convergence tolerance |
| `dagMode` | DAG_MAX | TREE_BASELINE is the C1-vs-tree ablation row, not a tuning axis |
| `numIterations` | 35 | with early stopping (streak 5/5) |
| embedding dim | 256 (fixed) | d/N coherence (0% unreliable leaves); not a knob |

---

## 4. separationEpsilon — verify it binds

Last run: Dasgupta deltas ~0.78–0.84 at `separationEpsilon = 0.01` → the gate
never rejects a split (near-inert). A knob that silently never binds is
indefensible in the thesis. Two options:

- **Make it bind:** raise to ~0.3–0.5 so marginal splits are rejected (fewer,
  better-supported leaves — good for BT sufficiency).
- **Document as a floor:** keep it low and state explicitly it is a safety floor
  against degenerate splits, not a tuning parameter.

Pick one and state it in §4.5. Do not leave it as a knob that does nothing.

---

## 5. Sweep protocol (L9 / Pareto)

The L9 orthogonal design (4 factors × 3 levels = 9 runs) is instantiated as 9
TOML files in `experiment_configs/`. No automated L9 harness exists — it is
manual.

**Phase A — L9 core** (`minClusterSize × tau × gap × deltaAssign`, 9 configs)
- `tauKappaScalingFactor = 0.0`, structural knobs at §3 fixed values.
- `category = ""` (full 14-domain construction — required so cross-domain
  bridging/polyhierarchy is exercised).
- `runBaselines = true`, `runBenchmark = false` (construction + DQ1 only).
- 3 seeds {42, 137, 2048}; report mean ± sd on WLP, Silhouette, Dasgupta, Sackin,
  Routing ECE, leaf-size distribution, coverage, AvgMatch.
- Compute Pareto front over (WLP, Silhouette) subject to the §6 gates.

**Phase B — refine** around the Phase-A winner (±1 step on tau, gap, deltaAssign).

**Phase C — tauKappa ablation** (for the thesis table, not selection)
- `{0.0, 0.5, 1.0}` at the best config. One 3-row table showing the effect of
  κ-adaptive temperature. Prior evidence: 0.0 wins; confirm.

**Phase D — confirmation (held-out, NOT tuning)**
- Run the selected config and compute the **trickle test** on the 25% arena-test
  set (out-of-sample routing-vs-label agreement). This is a confirmation gate,
  not a tuning signal — tuning on it is leakage.

**Phase E — freeze**
- Commit the selected TOML as `thesis_canonical.toml`. Lock the commit SHA +
  environment in `REPRODUCIBILITY.md`. Only then run the arena (RQ1/RQ2).

---

## 6. Pareto gates (hard constraints)

Select among Pareto-optimal configs satisfying ALL of:

- **Coherence:** WLP and Silhouette **beat flat k-means and HAC-Ward** at matched
  leaf count (DQ1). If neither beats the baselines, the induced structure is not
  justified — do not proceed to the arena.
- **Routing calibration:** Routing ECE ≤ 0.15 (or beats baselines).
- **Leaf sufficiency:** 0% of selected-node leaves below the BT identifiability
  floor; median held-out support per selected leaf ≥ ~12.
- **Coverage:** ≥95% of tuning-validation queries route to ≥1 leaf.
- **Polyhierarchy active:** AvgMatch ∈ [1.5, 4] — below 1.5 the DAG is a tree
  (polyhierarchy earns nothing; use TREE_BASELINE and reframe); above 4 is
  over-assignment.
- **Trickle (confirmation):** out-of-sample routing-vs-label agreement in a
  strong band. If it collapses, the DAG does not generalize — investigate before
  the arena.

Decision rule: among configs on the Pareto front satisfying all gates, pick the
one maximizing leaf coherence at sufficient support; report the full metric
vector + bootstrap CIs.

---

## 7. Methodology discipline (every sweep run)

1. **No leakage.** Tune on construction (60%) + tuning-validation (15%) only.
   The 25% arena-test is touched solely by the trickle test and the arena —
   never by hyperparameter selection. (§1.4, Table 1.1.)
2. **Baselines ON for DQ1.** `runBaselines = true` every sweep. Coherence is only
   meaningful relative to flat k-means / HAC-Ward / random-null.
3. **3 seeds.** {42, 137, 2048}; report mean ± sd. Single-seed DQ1 numbers are
   not defensible.
4. **Construction-only.** `runBenchmark = false` for all sweeps. The arena
   (BT/Weng-Lin, judge calls) is a separate run on the frozen DAG — never
   conflate tuning with arena evaluation.
5. **Statistical reporting.** Bootstrap CIs (2,000 resamples, query-level within
   domain) on every DQ1 estimate; McNemar for routing-agreement comparisons vs
   baselines where applicable.
6. **Reproducibility.** The runner writes `manifest.json` + CSVs; commit the
   exact selected TOML + SHA + lockfile.

---

## 8. Pre-calibration prerequisites (do these first)

You cannot calibrate coherently until the metrics reflect the actual
implementation:

1. **Fix the primary-leaf selection bug** (`TaxonomyMetrics.kt:196,457`):
   select by `queryWeights[queryText]`, not `max vmfKappa`. Until this is fixed,
   WLP, Routing ECE, and the trickle test are all computed on the wrong primary
   leaf.
2. **Move `tauKappaScalingFactor`** out of the `diagnostics` block into
   `FormalismConfig` (it is a live routing param — Phase C ablates it).
3. **Add unknown-key warnings** to the TOML parser (the pre-committed-config
   reproducibility claim requires stale keys to be rejected, not silently
   ignored).
4. **Reconcile thesis text ↔ code** (Ch 4.2–4.7, Ch 5.2): the MRL schedule, the
   Hornik-Grün formula, the funnel/`tauFunnelFloor` paragraph, and the stale
   hyperparameter list must match the implementation before the calibrated
   values are written into §5.2.

---

## 9. Discard / fallback gates

- If no L9 config beats flat baselines on WLP **and** Silhouette → the induced
  structure is not justified; report DQ1 honestly as a negative/neutral result
  and scope the contribution to the arena methodology, not the taxonomy.
- If AvgMatch < 1.5 at every operating point → polyhierarchy is inert; run
  TREE_BASELINE and reframe the DAG as a tree (RQ2 still tests adapted vs
  canonical on a tree).
- If the trickle test collapses on the 25% → the DAG does not generalise
  out-of-sample; do not run the arena until resolved.

---

## 10. One-line thesis statement (corrected)

> We calibrate the DAG along the granularity/support frontier — an L9 design
> over `minClusterSize`, routing temperature, leaf-acceptance margin, and
> traversal margin — maximising leaf coherence (WLP, silhouette, Dasgupta, Sackin)
> and routing calibration (ECE) subject to BT-statistical-sufficiency and
> coverage gates, with structural parameters fixed by the d/N coherence
> constraint at d = 256; the held-out trickle test confirms out-of-sample routing
> agreement before the answer-key-blind arena evaluation.
