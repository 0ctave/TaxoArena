# Construction documentation audit

Scope: the taxonomy construction only — how the tree is built, what governs
splitting and stopping, what the frozen artifact is, what is claimed about its
stability. The arena is out of scope except where construction parameters
feed it.

Reference object throughout: the **frozen artifact**, snapshot
`20260727_042523_Headless_Run_Auto_ge`, built from
`experiment_configs/freeze_mcs55.toml` at seed 42, and the 20-seed sweep
(`experiment_configs/sweep20_s1..s20.toml`) run at the same parameters. No
other construction is treated as canonical here.

Verified against: `snapshots.db`, `experiment_results/freeze_mcs55/seed_42/`,
`experiment_results/sweep20_s*/`, and Kotlin source at commit `c381211`
(the commit recorded in `run_manifest.json` for the frozen run).

Status vocabulary: **correct** / **wrong** / **insufficient** / **undocumented**.

---

## 1. Frozen artifact identity

**Status: correct.**

Documented: `report/03_Content/3_System_Architecture.tex:140-147`,
`report/03_Content/6_Results.tex:985-991`.

Every claimed number reproduces from `snapshots.db` and the run artifacts:

| Claim | Verified value | Source |
|---|---|---|
| 154 nodes | 154 | `metrics.totalNodes`, and `len(graph.nodes)` |
| 87 leaves | 87 | `metrics.leafNodes`, and count of nodes with empty `childIds` |
| max depth 6 | 6 | depth histogram `0:1, 1:14, 2:32, 3:54, 4:42, 5:9, 6:2` |
| J = 0.253129 | 0.2531286645082361 | `MAIN_taxonomy_quality.csv`; `iteration_metrics.csv` iter 10 |
| mass 8299.00 | 8299.000 exactly | sum of leaf `queryWeights` |
| 87/87 rubrics | 87 nodes carry `judgeRubric`, all leaves | graph scan; `metrics.nodesWithJudges = 87` |
| leaf median 88, min 54, max 396 | 88 / 54 / 396 | leaf `queryIds` lengths |
| one leaf below the floor | 1 (`n00000182`, 54 queries) | leaf scan |

The IQR `[71, 118]` quoted at `6_Results.tex:988` is the
`statistics.quantiles` convention; numpy's linear interpolation gives
`[71.5, 115.0]`. The convention is not named. Cosmetic, but the figure
caption repeats it.

Small mismatch: the snapshot's anchor label is `Math`; the thesis writes
`Mathematics` throughout (`6_Results.tex:1216`).

**Gap:** none material.

---

## 2. Anchors and the 14 MMLU-Pro categories

**Status: correct.**

Documented: `3_System_Architecture.tex:85-88`,
`11_Appendix_DAGConstructionFormalism.tex:14-44` (anchor immutability),
`6_Results.tex:1196-1234` (the per-anchor cell table).

Code: `TaxonomyOperations.kt` exempts depth ≤ 1 from every destructive
topology operation. Verified in the artifact: exactly 14 depth-1 nodes,
names matching the 14 MMLU-Pro categories with no extras and no omissions.

Leaves per anchor, computed by descent from each depth-1 node, sum to 87
with no leaf shared:

    Math 11 · Physics 10 · Chemistry 8 · Psychology 8 · Other 7 ·
    Economics 6 · Biology 6 · Computer science 6 · Law 6 · Health 5 ·
    History 4 · Engineering 4 · Business 3 · Philosophy 3

This matches `6_Results.tex:1216-1231` row for row. The thesis uses the
anchor definition consistently and explicitly corrects the rival
plurality-label count at `6_Results.tex:1282-1295` (physics 12→10,
computer science 3→6). Mathematics 13→11 is implied by the same paragraph
but is not spelled out.

**Gap:** none material.

---

## 3. Embedding: MRL and the fixed 256-dimensional prefix

**Status: documented but insufficient — one supporting claim is unsupported.**

Documented: `3_System_Architecture.tex:89-107`,
`11_Appendix:407-452`.

Code: `GraphNode.kt:360` — `fun dimForDepth(depth: Int): Int = 256`.
A literal, with no configuration knob anywhere. `TaxonomyFitter.kt:203`
and `TaxonomySplitter.kt:132` both route through it.
`Embedding.projectTo` slices and re-normalises, matching the thesis's
"re-normalisation after slicing is mandatory".

The embedding model is `qwen3-embedding:latest` via Ollama, recorded in
the snapshot's `config` blob. The thesis names Qwen3-Embedding at
`3_System_Architecture.tex:104`. Correct, but the model **version/tag is
never recorded in the thesis**, and `run_manifest.json` does not record it
either — only the snapshot `config` column does.

**Gap 1 (serious).** `11_Appendix:450-452` states: "The dimension itself is
ablated (A1, Section 8.2) at {128, 256, 512} to confirm that d = 256 is a
quality-stable operating point rather than a fragile one." No such
ablation can have been run from a configuration: `dimForDepth` is a
hardcoded literal with no config path. `7_Appendix_TuningProtocol.tex:217`
separately states that only three ablation rows have citable outcomes and
A1 is not among them. The two appendices contradict each other, and the
one that asserts the result is the one a reader will believe. **Unverifiable
as stated; would require either an A1 run artifact or a code path that
varies `d`.**

**Gap 2.** The justification for one fixed width — "narrowing the vector
keeps the directional concentration estimates well conditioned"
(`3_System_Architecture.tex:99-100`) — is argued but never measured at
any other width, for the same reason.

---

## 4. Node model: von Mises–Fisher, κ estimation, small-sample stabilisation

**Status: correct, and unusually well specified.**

Documented: `11_Appendix:277-366`; numerics at `12_Appendix_Numerics.tex:11-47`.

Code: `StatisticsUtils.correctedKappa` (`StatisticsUtils.kt:24-53`) and
`TaxonomyFitter.fitSingleNode` (`TaxonomyFitter.kt:195-300`).

Every step in the thesis matches the source:

- μ̂ = normalised weighted sample mean (`TaxonomyFitter.kt:231-247`).
- Banerjee seed `rBar*(d - rBar²)/(1 - rBar²)` (`StatisticsUtils.kt:28`).
- Up to five Newton–Raphson steps on `A_d(κ) = rBar`, with
  `A_d'(κ) = 1 - A_d² - ((d-1)/κ)A_d` (`StatisticsUtils.kt:33-42`).
  The thesis's claim of "typically one or two steps" is the code comment,
  not a measurement.
- Shrinkage `(n-1)/(n+d-2)` (`StatisticsUtils.kt:45`).
- Parent-anchored EB blend with the ramp
  `α(ρ) = 0 for ρ ≤ 2; (ρ-2)/8 for 2 < ρ ≤ 10; 1 for ρ > 10`, ρ = d/n
  (`TaxonomyFitter.kt:171-177, 287-296`). Exact match to the thesis
  piecewise definition.
- ρ = 256/55 = 4.65 ⇒ α = 0.33, as stated at `11_Appendix:344-347`. Arithmetic
  checks.
- `defaultKappaPrior = 10.0` at the root, `effectiveSupportFloor = 2.0`
  below which the prior is taken whole (`TaxonomyFitter.kt:287-289`).
  Both are in the locked-parameter table.

Shared-concentration assumption in routing is documented at
`11_Appendix:498-503` and implemented at `TaxonomyTrickler.kt:154, 160`:
`meanKappa = children.map { it.vmfKappa }.average()`, `f = meanKappa * dot`.
The thesis's stated reason — that the N-dependent shrinkage makes parents
systematically sharper, so cross-level density comparisons are biased — is
correct given the shrinkage formula.

**Minor code/doc drift (not thesis-facing):** the code comment at
`TaxonomyTrickler.kt:151-153` still says children are scored with "its own
kappa and normalizer". The code three lines below does the opposite. The
thesis matches the code, not the comment.

**Gap:** none material. The κ ceiling (`coerceIn(1e-3, 1e4)`) and the
`d/N > 10` warning counter are undocumented but inert for this artifact —
no leaf reaches ρ > 10.

---

## 5. NiW auxiliary posterior

**Status: correct.**

Documented: `11_Appendix:368-405`, `12_Appendix_Numerics.tex:49-87`.

Code: `TaxonomyFitter.kt:306-330` — `m0` = parent's vMF centroid,
`kappa0 = 1.0`, `nu0 = d + 2`, `lambda = 1/(κ_parent · d)`, diagonal Λ.
Matches the thesis exactly, including the "diagonal only" storage.

The thesis is explicit that NiW is not conjugate to vMF and is used as a
regulariser whose only live consumer is the leaf log-semantic-volume
diagnostic. That matches: `calculateLogSemanticVolume`
(`StatisticsUtils.kt:622-626`) is the only reader, and
`TaxonomyStabilizer.kt:92` is its only caller. It participates in neither
stopping criterion, as claimed.

The centroid no-update band at cosine ≥ 0.9975 (`11_Appendix:400-405`) is
implemented at `TaxonomyFitter.kt:258`. Correct.

**Gap:** the diffuse exclusion `κ < 0.5` is documented; see §8, where the
undocumented second conjunct lives.

---

## 6. Separation score and its chance correction

**Status: correct.**

Documented: `11_Appendix:566-601`.

Code: `StatisticsUtils.chanceCorrectedSeparation` (`StatisticsUtils.kt:193-219`).

Term by term:

- `W(S) = |S|² - ‖Σx‖²` → `wWithin += c.n*c.n - normC2` (line 209).
- `E[Σ W(S_c)] = W(S_total) · Σ n_c(n_c-1)/(n(n-1))` → `expectedWithin =
  wTotal * pairFrac / (n*(n-1))` with `pairFrac += c.n*(c.n-1)` (lines 210, 216).
- `s = 1 - Σ W(S_c)/E[·]` → line 218.

Degenerate cases behave as claimed: k=1 gives exactly 0 (wWithin equals
expectedWithin), so a pass-through wrapper cannot clear a positive bar.

The null the correction is against is stated precisely and correctly:
uniformly random relabelling into clusters of the same sizes. The
limitation this leaves — that an elongated single cluster cut across its
long axis still scores well — is stated as limitation 1 at
`3_System_Architecture.tex:190-208`, with the counts that quantified it
correctly marked **void as to values**.

The global objective J is the same score lifted to the whole corpus with
one cell per leaf plus one per internal residual pool
(`11_Appendix:657-661`); `StatisticsUtils.computeDagSeparationJ`
(`StatisticsUtils.kt:221+`) collects leaves and residual-holding internal
nodes exactly that way. Correct — but see §11 on residual pools being
empty in this artifact, which makes the residual-cell clause vacuous here.

---

## 7. The acceptance gate

**Status: correct in the section that defines it; contradicted twice inside
the same appendix.**

Documented (correctly): `11_Appendix:653-728`,
`3_System_Architecture.tex:124-131`, `6_Results.tex:1106-1131`.

Code: `isProposalAccepted` (`TaxonomyOperations.kt:55-69`):

```kotlin
if (zGate > 0.0 && seDeltaJ != null) {
    if (seDeltaJ > 0.0) deltaJ > maxOf(tau, zGate * seDeltaJ) else deltaV < 0
} else { /* legacy lexicographic on (J, -|V|) against tau */ }
```

This is the rule the thesis states, including the SE = 0 clause and its
justification (a pure structural edit that moves no query). `z* = 2.0`
from `freeze_mcs55.toml:102`. `tau = 1e-6`. The bootstrap is a paired
Dirichlet resample at 200 replicates over only the queries whose cell
changed (`JBootstrap.kt:110, 202, 232`). All as documented.

The gate applies uniformly to every edit type: `tryProposal` is the single
path for GROW, fusion, prune and dissolution
(`TaxonomyOperations.kt:600-745`). As claimed.

**Gap 1 (serious, internal contradiction).** `11_Appendix:122-123`
(Phase 4 walkthrough) says a split "is then committed only if the measured
global objective improves beyond the neutrality band (ΔJ > τ)".
`11_Appendix:626-629` (stage 4, Global veto) says "committed only if the
measured global objective does not degrade, ΔJ > 0". Neither is the rule.
Both appear *before* the section that gives the real one. A reader working
front-to-back gets the superseded rule twice and the correct rule once.

**Gap 2.** `6_Results.tex:1094-1112` reports the R4 evidence row, but the
supporting five-seed measurements (the `13.1×` SE spread, "4 of 52 edits at
z < 1", worst z = 0.156) are quoted from the pre-freeze five-seed sweep,
which `6_Results.tex:1172-1176` itself marks **void as to values**. The
void marker is applied to the leaf counts of that sweep but not to the SE
spread and edit counts drawn from the same runs. The frozen run's own
`proposals.csv` (373 rows) has never been used to re-derive them.

---

## 8. Splitting procedure

**Status: documented but wrong in three places.**

Documented: `11_Appendix:553-651`.

Code: `TaxonomySplitter.splitSingleNode` (`TaxonomySplitter.kt:64+`),
driven by the ascending-k loop in `TaxonomyOperations.kt:212-220`.

What is correct:

- PCA subspace by target size: `< 100 → 32, < 500 → 64, else 128`
  (`TaxonomySplitter.kt:137-141`). Exactly as stated at
  `3_System_Architecture.tex:112-115` and `11_Appendix:555-561`.
- PCA power iteration seeded from the problem shape
  (`StatisticsUtils.kt:656`: `Random(0x5EEDL + comp*7919 + d*104729 + n*31)`),
  30 iterations, deflation. Determinism claim at `11_Appendix:242-247` holds.
- Acceptance and fitting happen at d = 256, never in the reduced space
  (`childDim = dimForDepth(node.depth+1) = 256`, `TaxonomySplitter.kt:132`).
- Routed sustainability: children are refit and re-assigned by the same
  level-local posterior, and the split is rejected if any routed child
  falls below `minClusterSize` (`TaxonomySplitter.kt:389-408`). Correct.
- The min-pair bar is the load-bearing gate, not the k-way score
  (`TaxonomySplitter.kt:432-446`), which the appendix's stage 3 implies
  and the source comment confirms (5682 min-pair rejections against 0 for
  the joint gate).
- `D_max = 8` from config; the artifact reaches depth 6, so it is not binding.

**Wrong 1 (serious).** `11_Appendix:562-564`: "For an internal node, the
split target is its residual pool, which is the mechanism by which coherent
unexplained mass is carved into new children alongside existing ones."
`TaxonomySplitter.kt:65` is `if (!node.isLeaf) return false`. **Internal
nodes are never split.** The residual-viability path exists, but it applies
to a *diffuse leaf*, not to an internal node, and it is unreachable in this
configuration anyway (§11). The described mechanism does not exist.

**Wrong 2.** `11_Appendix:621-622`: the routed partition "must score
s ≥ ε_sep (2ε_sep for small populations)". The 2× small-population margin
was **removed from the code**; `TaxonomySplitter.kt:323-333` records its
deletion and that `bar=0.0500` appears zero times in the repository's logs
against 5628 occurrences of `bar=0.0250`. The thesis states a gate that
does not exist.

**Wrong 3.** `11_Appendix:606-609`, stage 1: "vMF-EM with k ∈ {2,…,4}, k
selected by chance-corrected marginal improvement ≥ ε_sep". In the frozen
configuration this selector never runs. `TaxonomyOperations.kt:212-220`
forces k explicitly, ascending from 2, and `TaxonomySplitter.kt:195-197`
sets `maxK = forcedK` and `marginalEps = -1e9` whenever `forcedK` is
non-null — which is always. The real selector is the ascending-k gate
fallback, described correctly 100 lines later at `11_Appendix:709-713`.
Stage 1 describes the superseded selector as if it were live.
(`marginalEps` defaults to `-1.0` = "fall back to `proposalSeparationBar`"
and is absent from `freeze_mcs55.toml`, so the fallback is what a reader
would infer from the config — and it is still not what runs.)

**Undocumented 1.** Split eligibility requires **both** mass ≥ 2·`minClusterSize`
**and effective sample size** `ess = mass²/Σw²` ≥ 2·`minClusterSize`
(`TaxonomySplitter.kt:67-70`). The ESS gate appears nowhere in the thesis.
Under soft membership these are different quantities, and the ESS gate can
refuse a node the mass gate admits.

**Undocumented 2.** The diffuse exclusion is `κ < 0.5 **and** mass <
10·minClusterSize` (`TaxonomySplitter.kt:77`). `11_Appendix:379-381`
documents only the κ < 0.5 half. A large diffuse node is therefore eligible
for ordinary splitting, contrary to the appendix.

**Undocumented 3.** `maxK = 4` is not in the hyperparameter table
(`7_Appendix:8-31`). It appears only as "k ∈ {2,…,4}" inside prose, and
`freeze_mcs55.toml` does not set it, so its value comes from
`TaxonomyConfig.kt:182`. It bounds the k-fallback loop directly, so it is a
structural parameter, not a comment.

---

## 9. Descent, routing, and the descent margin

**Status: correct on the three gates; one constant is stated wrong.**

Documented: `11_Appendix:454-551`.

Code: `TaxonomyTrickler.childTransitions` (`TaxonomyTrickler.kt:139-225`)
and the membership stage at `TaxonomyTrickler.kt:400-430`.

- **Descent gate.** `descentBar = (childCentroidShrinkage - descentMargin)
  .coerceAtLeast(0.0)`; descend iff `bestChildDot ≥ descentBar * parentDot`
  (`TaxonomyTrickler.kt:190-191`). `childCentroidShrinkage` is
  `‖Σ_c ω_c μ̂_c‖` clamped to [0,1] (`GraphNode.kt:398-402`), which is the
  thesis's r̄_v. `descentMargin = 0.12`. Correct, including the Jensen
  derivation and the note that the bound is only non-vacuous because μ_v is
  fitted independently of the children's resultant (`GraphNode.kt:404-414`
  and `11_Appendix:478-490` agree).
- **Beam.** Additive cosine margin: `dots[i] ≥ maxDot - routingBeamGamma`
  (`TaxonomyTrickler.kt:204`), γ = 0.20. Matches `11_Appendix:506-516`.
  (The config comment at `TaxonomyConfig.kt:139-146` describes a
  *relative responsibility* beam instead. The thesis matches the code; the
  config comment is stale and should not be trusted by anyone reading the
  parameter list.)
- **Membership share floor.** Self-normalised over reached destinations,
  floor 0.25, fall back to the single best if nothing clears
  (`TaxonomyTrickler.kt:409-415`). Matches `11_Appendix:524-536`.
- **Transition renormalisation over the beam** (`TaxonomyTrickler.kt:218-222`).
  Matches.

**Wrong.** `11_Appendix:521-522`: "Paths whose absolute posterior falls
below 10⁻⁴ are abandoned as a purely numerical fan-out guard."
`TaxonomyTrickler.kt:90` is `LOG_NEGLIGIBLE_PATH = ln(1e-30)`. The comment
immediately above it explains that 1e-4 was the *old* value and that at
1e-4 the guard was doing real selection work, which is why it was moved to
1e-30. The thesis quotes the value that was deliberately abandoned, and
quotes it while making the claim ("carries no membership semantics") that is
only true of the new one.

**Insufficient.** `11_Appendix:518-520` says the log-sum-exp path
aggregation is "retained dead code" in a tree. True — but the walk is a
topological dynamic program (`TaxonomyTrickler.kt:286-360`) and there is a
second, path-enumerating reference implementation kept for a differential
test (`TaxonomyTrickler.kt:430+`). Neither is named. A reader trying to
reimplement routing has no way to know which traversal produced the
artifact.

---

## 10. Soft membership and multi-membership

**Status: correct about construction; the appendix's claim about the arena
is wrong, and the numerics appendix contradicts it.**

Documented: `3_System_Architecture.tex:249-258` (limit 4),
`11_Appendix:538-548` and `11_Appendix:795-800`,
`9_Appendix_MetricDefinitions.tex:71-83` (AvgMatch),
`12_Appendix_Numerics.tex:207-211`.

Construction side, verified correct:

- Membership floor 0.25, construction-time membership **unbounded**
  (`TaxonomyTrickler.kt:111`: `maxAssignments = if (isInference)
  maxLeafAssignments else Int.MAX_VALUE`). Exactly as documented.
- Primary leaf = argmax of normalised memberships
  (`TaxonomyTrickler.kt:428`), described correctly as a bookkeeping
  convention.
- Measured multi-membership in the artifact: `avgMatchCount = 1.101`; raw
  leaf `queryIds` sum to 9141 against 8299 unique queries. Consistent with
  a 0.25 floor.
- Evaluation-time cap of 5 (`maxLeafAssignments`). Present.

**Wrong (serious).** `11_Appendix:797-800` says evaluation-time multi-leaf
assignment "determines which leaves a given query contributes comparisons to
during the arena run". It did not. `TaxonomyBenchmarkService.kt:326-355`
carries a dated comment — *2026-07-31* — recording that until that date
**only the primary leaf was filed** and the secondaries were computed and
discarded. Every arena run reported in Chapter 6 predates it. The
construction description is right; the sentence about what the arena did
with it is wrong.

`12_Appendix_Numerics.tex:207-211` states the opposite, correctly: "The
propagation path receives only a query's primary leaf and adds weight 1.0."
So the thesis contains both the true and the false statement, in two
appendices, with no cross-reference.

**Undocumented.** Arena-time routing is not "exactly the same gate, beam
and share floor" as `11_Appendix:544-548` claims. `TaxonomyArenaService
.routeToLeavesSoft` (`TaxonomyArenaService.kt:383-453`) calls the trickler
and then applies two further arena-only mechanisms: a **near-uniform
entropy guard** (`isNearUniform`, `TaxonomyArenaService.kt:455-462`;
drops *all* secondaries when the posterior entropy ratio exceeds 0.95 or the
entropy deficit is under 0.05) and a second degree cap at `1 + (K-1)`. The
entropy guard appears nowhere in the thesis. This is very likely part of the
"two routing paths, and where they disagree" anomaly the thesis reports
honestly but leaves **not diagnosed** at `6_Results.tex:1236-1252` (561
held-out questions discarded by the live path, composition shifting, not
only coverage).

**Live defect worth recording.** In the 2026-07-31 change,
`secondaryMemberships` is keyed by leaf **label**
(`TaxonomyArenaService.kt:448`) while `TaxonomyBenchmarkService.kt:355-358`
compares those keys against leaf **ids** (`secondaryId == leaf.id`,
`secondaryId !in frozenLeafIds`). With a non-empty `frozenLeafIds` every
secondary is dropped, so the widening the comment describes does not
happen. Not a thesis error — the thesis describes pre-change behaviour —
but any future claim about multi-leaf pooling rests on it.

---

## 11. Residual retention

**Status: documented at length; inert in the frozen artifact, and the
thesis never says so. One statement about it is wrong.**

Documented: `11_Appendix:254-273` (a full subsection),
`11_Appendix:102-114` (Phase 3), `11_Appendix:657-661` (residual pools as J
cells), `11_Appendix:562-564` (residual splitting).

**The frozen artifact contains zero residual queries.** `metrics.residualQueries
= 0` in the snapshot. `TaxonomySplitter.kt:315-317` states the mechanism:
at `descentMargin = 0.12` the descent gate is relaxed far enough that no
node residualises. The splitter's own comment calls the residual-viability
branch "dead twice over".

So: residual pools as first-class measurable objects, the residual clause in
J's cell decomposition, the residual-split gate, and the residual-viability
path are all described as live machinery and all produce nothing in the
artifact every result is attributed to. `7_Appendix:58-63` comes closest to
saying this — it calls `descentMargin` "a mode selector with two justified
operating points", 0.12 being "sub-domain discovery off" — but it never
states the consequence: **at the operating point actually used, the residual
subsystem is switched off.** A reader auditing J's definition will look for
residual cells that do not exist.

**Wrong.** `11_Appendix:98-99` (Phase 2): "The concentration fit excludes
residual-flagged queries; the mean direction includes them."
`TaxonomyFitter.kt` contains no reference to `residualQueries` at all.
`getRegionQueryWeights` (`TaxonomyFitter.kt:179-193`) sums `node.queryWeights`
over the region, and residual queries are merged into `queryWeights` with
full weight 1.0 (`TaxonomyOperations.kt:313-319`). Both μ̂ and κ̂ use the
same weight map. The claimed asymmetry does not exist. (Moot for this
artifact, since there are no residuals — but it is stated as a property of
the estimator, not of this run.)

---

## 12. Stopping criterion

**Status: correct.**

Documented: `3_System_Architecture.tex:220-247` (limit 3),
`11_Appendix:196-252`, `6_Results.tex:1005-1018`.

Code: `TaxonomyEngine.kt:604-657`, `TaxonomyStabilizer.kt:45-128`.

- Structural arm: GED = 0 over node and edge sets, five consecutive
  (`requiredConsecutive = 5`, `TaxonomyStabilizer.kt:25`), floor
  `max((0.8·|anchors|).toInt(), 5)` = `max(11, 5)` = 11 at 14 anchors
  (`TaxonomyStabilizer.kt:45-48`). Verified.
- Objective arm: `|editsDelta| ≤ τ` **and** `|trickleDelta| ≤ τ`, five
  consecutive (`TaxonomyEngine.kt:607-611, 655-658`). Verified.
- The disjunction: either fires (`TaxonomyEngine.kt:650-658`). Verified.
- The frozen run stopped at iteration 10 on J stationarity;
  `headless_run.log` carries "Early stopping triggered in iteration 10 due
  to convergence (J stationarity)" and `GED converged=false` throughout.
  Verified.
- Iterations 8, 9, 10 identical on every column of
  `iteration_metrics.csv`. Verified (structure was already fixed from
  iteration 5; `editsDelta` is 0 from iteration 6).

The thesis's argument — the structural arm *could not* have fired at
iteration 10, so the weaker arm is what stopped it — is sound and is stated
against the interest of the result. Good.

Minor: the floor means the structural arm cannot fire before iteration 15
(streak starts no earlier than 11 and needs five). The thesis says
"cannot fire before 11", which is a correct but loose bound. It does not
weaken the argument.

Minor: `11_Appendix:138-144` (Phase 6 walkthrough) describes only the GED
arm, and the table row at `11_Appendix:81-83` says "GED quiescence streak".
The disjunction appears three subsections later. A reader stopping at the
phase table gets the wrong stopping rule.

---

## 13. Fixed-point certificate

**Status: correct in substance; the tolerance attribution is wrong, and one
term goes missing in the results chapter.**

Documented: `3_System_Architecture.tex:160-165`,
`11_Appendix:232-234`, `6_Results.tex:993-1003, 1093-1104`.

Code: `TaxonomyEngine.kt:660-712`. Artifact:
`experiment_results/freeze_mcs55/seed_42/fixed_point_certificate.txt`:

```
final iteration : 10
edits delta     : 0.000000e+00
trickle delta   : -3.330669e-16
max 1-cos(mu)   : 1.110223e-16
max rel d kappa : 4.246836e-13
tolerance (tau) : 1.000000e-06
tolerance (theta): 1.000000e-06
CERTIFIED       : true
```

Four terms, period 1, evaluated once on the frozen artifact — all as
documented, including the explicit disclaimer in the certificate file that
it certifies *this* artifact and not general termination.

**Wrong (small but load-bearing for a reimplementer).**
`3_System_Architecture.tex:163-165` says "All four terms are magnitudes
tested against **τ**". They are not. `TaxonomyEngine.kt:672-674` uses
`tol = config.formalism.tau` for `editsDelta` and `trickleDelta`, and
**separate hardcoded** `epsMu = epsKappa = 1e-6` for the two parameter
terms — with a comment saying precisely why they are separate ("tau bounds a
change in J, these bound a change in the parameters that produce it"). They
coincide numerically only because the canonical τ happens to be 1e-6. Change
τ and the certificate silently stops meaning what the thesis says.

**Incomplete.** `6_Results.tex:993-997` narrates three of the four terms —
edit-phase change, max 1-cos(μ), max relative Δκ — and omits **trickleDelta**
(-3.33e-16), the re-routing term. That is the term the code comment singles
out as the one that "would miss the ungated routing step". Chapter 3 lists
all four; the results section that certifies the artifact lists three.

**Insufficient.** `6_Results.tex:1100-1104` says "two of the six certificate
fields are bounded rather than exactly reproducible, because routing is
parallel and float accumulation is not associative." The certificate has
five value fields plus a boolean. Which two are meant is not stated, and no
reproduction run is cited.

---

## 14. Seed sensitivity and the stability claim

**Status: correct, and the strongest-verified claim in the chapter — but
the reason four seeds fail is undocumented.**

Documented: `3_System_Architecture.tex:60-77` (R3),
`11_Appendix:248-252`, `5_Experimental_Design.tex:97-107`.

Verified against all 20 sweep runs:

| Claim | Verified |
|---|---|
| 72 to 93 leaves | min 72 (seed 7), max 93 (seed 4) |
| median 86 | 86.0 |
| standard deviation 4.4 | 4.4186 (sample) |
| seed 42 gives 87 | 87, from `freeze_mcs55/seed_42` |
| 16 of 20 certify, 4 do not | 16 / 4 |
| the four that fail | seeds 4, 5, 11, 12 |
| labelling and induction off across the sweep | confirmed |

All 20 configs differ from `freeze_mcs55.toml` on exactly four keys: `seed`,
`outputDir`, `enableLabeling`, `judgeInduction`. Nothing structural.

The void 88-leaf / 64–68 / ARI 0.609 figures **do not survive in the
thesis**. `3_System_Architecture.tex:72-74` states plainly that no
cross-seed agreement index has been computed on this construction. The
0.609 exists only in `docs/gap-analysis-final.md:238` and is formally listed
in `docs/void-results.md`. Correctly handled.

**Undocumented (serious).** The thesis says four seeds "do not [certify]"
and stops. The certificates say *how*:

| seed | trickleDelta | max 1-cos μ | max rel Δκ | stopped at | on |
|---|---|---|---|---|---|
| 4 | 9.37e-10 | 0.0 | **1.30e-03** | 10 | J stationarity |
| 5 | **-2.44e-06** | 0.0 | **3.95e-03** | 15 | GED quiescence |
| 11 | **-3.58e-06** | 0.0 | **6.04e-03** | 15 | GED quiescence |
| 12 | **-1.16e-05** | 1.11e-16 | **3.17e-03** | 15 | GED quiescence |

`editsDelta` is 0 in all four — the structural gate is quiescent. All four
fail on **κ**, by three to four orders of magnitude, and three also fail on
re-routing. None hit the iteration budget of 50.

This is a finding about the stopping rule, not about the seeds: **both
stopping criteria can fire while the concentration refit is still moving.**
Neither criterion observes θ. That is exactly the hole the certificate was
built to detect, and in 4 of 20 runs it detects it. The thesis reports the
count and not the mechanism, which makes a diagnostic result read as noise.

**Minor.** `3_System_Architecture.tex:65` says the twenty runs are "identical
in every parameter except the seed"; the footnote two lines later correctly
lists labelling and induction as also off. The body sentence overstates.

**Provenance note.** Seeds 1–19 were built from commit `c381211`; **seed 20
from `83ff7ba`**, one commit later. The change is gated on
`excludeFromAnchoring`, which defaults empty and is absent from the config,
so it is behaviourally inert — but the sweep is a 19+1 build, not a single
build, and nothing records that.

---

## 15. `minClusterSize = 55` and the tuned parameters

**Status: mostly correct; the table has one wrong value and two omissions.**

Documented: `7_Appendix_TuningProtocol.tex:8-64` (the hyperparameter table),
`7_Appendix:50-63` (provenance of the two contested values),
`6_Results.tex:1133-1140`.

Checked against `freeze_mcs55.toml` and the snapshot's `config` blob:

| Thesis | Config | |
|---|---|---|
| d = 256 | hardcoded 256 | ok |
| D_max = 8 | `maxDepth = 8` | ok |
| n_min = 55 | `minClusterSize = 55` | ok |
| ε_sep = 0.025 | `proposalSeparationBar = 0.025` | ok |
| τ = 1e-6 | `tau = 1e-6` | ok |
| acceptanceZ = 2.0 | 2.0 | ok |
| membershipFloor = 0.25 | 0.25 | ok |
| routingBeamGamma = 0.20 | 0.2 | ok |
| descentMargin = 0.12 | 0.12 | ok |
| effectiveSupportFloor = 2.0 | 2.0 | ok |
| maxLeafAssignments = 5 | 5 | ok |
| fusionSimilarityThreshold = 0.90 | 0.90 | ok |
| dagMode = DAG_MAX | DAG_MAX | ok |
| **numIterations = 35** | **50** | **wrong** |

`numIterations` is 50 in `freeze_mcs55.toml:112` and 50 in the snapshot's
recorded `config`. The thesis states 35 twice — `7_Appendix:28` and
`7_Appendix:165` (locked-parameters table) — and adds a footnote saying the
values are "read from its run configuration". They were not. The budget was
not binding (the run stopped at 10), so nothing downstream moves; but it is
a stated provenance that fails on inspection.

**Omissions from the table:** `maxK` (= 4, default, structural — see §8),
`marginalEps` (= -1.0 default, inert), `seed` (= 42), `testRatio` (= 0.3),
`enableRefitGate` (= false). Seed and split ratio are given in Chapter 5, so
only `maxK` is a real gap.

Provenance of 55 is documented well and honestly: `7_Appendix:50-57` states
it is a *budget* choice, that it is not on the historical sweep's
{50, 75, 100} grid, and that it was not selected by that sweep. The
licensing result (granularity flatness) is cited and pre-registered. The
`11_Appendix:353-364` passage that retracts the earlier "leaf size is
constrained by the concentration estimator" reasoning is correct: at
n_min = 55, α = 0.33, so the estimator is not binding.

The L9/Pareto protocol at `7_Appendix:66-113` is documented as **historical**
and explicitly disclaimed as not having fixed any canonical value. That is
the honest reading, and it means **no current tuning study exists**: the four
live factors are named, the machinery is described, and the sweep is
"pending". A reader cannot audit how 0.12, 0.25, 0.20 and 0.025 were jointly
chosen, because the record of that choice is not in the thesis.

---

## 16. Coarsening operators

**Status: documented but insufficient.**

Documented: `3_System_Architecture.tex:131-135` (four moves named),
`11_Appendix:125-136` (Phase 5), `11_Appendix:730-740` (structural
consequences).

Code: `TaxonomyMerger.kt` (46 kB), invoked through the same
`tryProposal` gate.

The four moves are named correctly — starved-leaf handling (three-way:
keep / absorb / fuse-into-sibling, decided by measured J), sibling fusion,
near-duplicate fusion, sole-child dissolution — and the anchor exemption and
same-parent restriction (which is what preserves tree-ness) are both real.

**Gap.** `fusionSimilarityThreshold = 0.90` is in the hyperparameter table
labelled "Fusion pre-filter threshold" and is otherwise never explained. It
is a cosine pre-filter on which pairs are even considered for fusion, and it
therefore bounds what the gate can ever see. No section says what it filters,
on which vectors, or why 0.90. Neither ablated nor derived.

**Gap.** The order in which the four moves run within Phase 5, and whether an
accepted move re-opens earlier candidates in the same iteration, is not
stated anywhere. Since each move re-routes the whole corpus and the next
proposal's base is the previous acceptance
(`TaxonomyOperations.kt:735-737`), order is outcome-relevant. Not
reimplementable from the thesis.

---

## 17. Determinism

**Status: correct.**

Documented: `11_Appendix:242-252`.

Three mechanisms claimed, three found: PCA power-iteration seeded from the
problem shape (`StatisticsUtils.kt:656`), monotonic node-id counters, and
sorted iteration for order-sensitive float aggregation
(`TaxonomyFitter.kt:232`, `TaxonomySplitter.kt:128-130`). The
`Random(n*31 + depth)` shuffle at `TaxonomySplitter.kt:552` is for LLM
label sampling only, and is seeded too.

The scoping is stated correctly: determinism holds *at* a seed and says
nothing across seeds. The 20-seed spread is the evidence for the second
half.

---

## 18. Polyhierarchy as a measured negative result

**Status: correct.**

Documented: `6_Results.tex:1703-1744`, mechanics at `11_Appendix:742-800`.

The outcome is stated before the mechanics, which is the right order for a
retired feature. The measurements (42 proposals, r(f, ΔJ) = +0.085, complete
distributional overlap, median ΔJ an order of magnitude below splits, one
node acquiring five parents by iteration 1) are specific and falsifiable.
The argued part — that a partition objective is structurally indifferent to
a second parent — is correct given J's definition in §6.

Verified in the artifact: `crossDomainNodes = 0`, `BridgeCount = 0`, and
every one of the 154 nodes has exactly one parent. The single-parent
invariant holds.

Not verified here: the 42-proposal measurements themselves, which come from
a run that no longer exists in the current configuration. **Unverifiable
from the frozen artifact**; would need the cross-link-era proposal log.

---

## 19. Metric definitions used to characterise the construction

**Status: correct, with one defect the thesis itself documents fully.**

Documented: `9_Appendix_MetricDefinitions.tex`.

Spherical silhouette, Total Dasgupta Cost, Normalised Sackin, AvgMatch,
Weighted Leaf Purity and Dendrogram Purity are all given in closed form.
The appendix is explicit that the construction's separation score is **not**
a Dasgupta quantity and that Dasgupta cost is retained only as a whole-tree
evaluation metric — consistent with `11_Appendix:598-601`.

Routing ECE at 0.2114 is reported with its aggregation defect stated in full
(`9_Appendix:144-157`): the definition sums leaf membership onto the depth-1
ancestor, the export takes the maximum, and a maximum is not a distribution.
Direction of the error known, size not. Quoted as a diagnostic only in all
three places it appears. This is handled correctly.

One thing worth noting: `metrics.weightedLeafPurity = 1.0` in the snapshot
blob, while the validation export recomputes 0.7299 on held-out. Two
quantities, one name. Neither is quoted in the construction section, so no
claim depends on it, but the snapshot field is misleading to anyone reading
the artifact directly.

---

# Prioritised gaps, worst first

### 1. The appendix states the split-acceptance rule three different ways, and twice gets it wrong

`11_Appendix:122-123` (ΔJ > τ) and `11_Appendix:626-629` (ΔJ > 0) both
precede the correct rule at `11_Appendix:672-678`
(ΔJ > max(τ, z*·SE_paired)). The whole R4 argument — that the gate is right
because its *units* are right — is destroyed for a reader who takes either
of the earlier statements at face value. This is the single most-defended
design decision in the chapter, and the appendix undercuts it twice before
stating it.

### 2. Three mechanisms in the splitting section describe code that does not run

Internal-node residual splitting (`11_Appendix:562-564`) — the function
returns immediately for non-leaves. The 2ε_sep small-population bar
(`11_Appendix:621-622`) — deleted from the source, zero occurrences in the
logs. Marginal-improvement k-selection (`11_Appendix:606-609`) — bypassed
by the forced-k loop in every proposal. A reader reimplementing from stage 1
through stage 4 builds a different splitter. Any examiner who checks stage 1
against `TaxonomySplitter.kt` finds it does not match, and then has to decide
what else does not.

### 3. The residual subsystem is documented as live and produces nothing

A subsection, a phase, a clause in J's cell decomposition, and a split gate
are all built on residual pools. `metrics.residualQueries = 0` in the frozen
artifact, because `descentMargin = 0.12` relaxes the descent gate past the
point where anything residualises. The thesis says descentMargin is a "mode
selector" (`7_Appendix:58-63`) but never says which mode the artifact is in
or that the whole residual apparatus is switched off in it. This matters
because J's definition — the objective every acceptance decision reads — has
a term that is empty, and a reader verifying J against the artifact will
look for cells that do not exist. The related claim at `11_Appendix:98-99`
(concentration fit excludes residuals) is simply false of the code.

### Then, in order

4. **The certificate's tolerance attribution is wrong.**
   `3_System_Architecture.tex:163-165` says all four terms test against τ;
   two test against a separate hardcoded 1e-6. They coincide only at the
   canonical τ. Compounded by `6_Results.tex:993-997` narrating three of the
   four terms and dropping the re-routing term — the one the code singles
   out as indispensable.

5. **Why 4 of 20 seeds fail to certify is not reported.** All four fail on
   κ by three to four orders, three also on re-routing, none on structure,
   none on budget. Both stopping criteria can fire while the parameter refit
   is still moving, and neither observes θ. Reported as a bare count, it
   reads as seed noise; reported with the mechanism, it is a measured
   limitation of the stopping rule.

6. **The MRL slice width is asserted to be ablated and cannot have been.**
   `11_Appendix:450-452` claims an A1 ablation at {128, 256, 512};
   `dimForDepth` is a hardcoded literal with no config path, and
   `7_Appendix:217` says A1 has no citable outcome. The load-bearing claim
   for the fixed 256-slice — that it is a stable operating point — rests on
   this.

7. **`numIterations` is stated as 35 and is 50**, in a table footnoted
   "read from its run configuration". Harmless numerically (the budget never
   bound), corrosive to the provenance claim the table makes about itself.

8. **The evaluation-time routing path has an undocumented entropy guard**
   (`TaxonomyArenaService.kt:455-462`) on top of the trickler, contradicting
   `11_Appendix:544-548`'s "exactly the same gate, beam and share floor".
   This is a live candidate explanation for the undiagnosed 561-question
   routing disagreement at `6_Results.tex:1236-1252`.

9. **Two undocumented split-eligibility gates**: the ESS gate
   (`ess ≥ 2·minClusterSize`) and the second conjunct of the diffuse rule
   (`mass < 10·minClusterSize`). Both change which nodes are candidates at
   all. `maxK = 4` is likewise absent from the hyperparameter table despite
   directly bounding the k-fallback.

10. **The path-abandonment constant is quoted as 1e-4 and is 1e-30**
    (`11_Appendix:521-522` against `TaxonomyTrickler.kt:90`), and the
    accompanying claim that it "carries no membership semantics" is only
    true of the value actually used.

11. **`11_Appendix:797-800` says the arena filed multi-leaf memberships.**
    It filed primaries only until 2026-07-31, after every reported run.
    `12_Appendix_Numerics.tex:207-211` states this correctly. The two are
    not cross-referenced.

12. **No current tuning record exists.** `7_Appendix` is candid that the
    L9/Pareto sweep is historical and fixed none of the surviving values,
    and that the sweep over the four live factors is pending. So how 0.025,
    0.12, 0.25 and 0.20 were jointly chosen is not auditable from the
    thesis. `minClusterSize = 55` is the exception and is documented well.

13. **Phase-5 operator ordering is unstated**, and it is outcome-relevant
    because each accepted edit becomes the next proposal's base.
    `fusionSimilarityThreshold = 0.90` appears only as a table row with no
    explanation of what it pre-filters.

---

# Unverifiable

| Claim | What would settle it |
|---|---|
| A1 embedding-dimension ablation at {128, 256, 512} (`11_Appendix:450-452`) | A run artifact at d ≠ 256, or a code path that varies `dimForDepth` |
| "Newton–Raphson converges in one or two steps" (`11_Appendix:307-308`) | An iteration-count histogram; the source only caps at 5 |
| SE(ΔJ) 13.1× spread, 4 of 52 edits at z < 1, worst z = 0.156 (`6_Results.tex:1108-1110`) | Re-derivation from the frozen run's own `proposals.csv` (373 rows). The quoted values come from the five-seed sweep the same section marks void as to values |
| "Two of the six certificate fields are bounded rather than exactly reproducible" (`6_Results.tex:1100-1104`) | Naming the two fields, and a repeat run at seed 42 |
| The 42 cross-link proposals and r(f, ΔJ) = +0.085 (`6_Results.tex:1717-1725`) | The cross-link-era proposal log; the operator is gone from the current source |
| Within-node null median "~0.04" (`freeze_mcs55.toml` header; `11_Appendix:637-640` says only "above it") | Correctly marked **void as to values** in the thesis. Re-derivation needs `SeparationNullBySizeTest` re-run on the frozen tree |
| Embedding model version | `qwen3-embedding:latest` is in the snapshot `config` blob only. `:latest` is not a version; the exact model revision is unrecoverable |

---

# Counts

- **19 construction elements checked.**
- **8 documented and correct** (frozen artifact identity; anchors; vMF/κ
  estimation; NiW; the separation score and its chance correction; the
  stopping criterion; seed sensitivity; determinism; polyhierarchy — the
  metric-definitions appendix makes a 10th if counted).
- **6 documented but wrong in at least one respect** (splitting; the
  acceptance gate as stated in the appendix walkthrough; routing's path
  cutoff; multi-membership at arena time; residual retention; the
  certificate's tolerances).
- **3 documented but insufficient** (MRL slice justification; coarsening
  operators; hyperparameter provenance).
- **2 with material undocumented components** (split eligibility gates and
  `maxK`; the arena-side entropy guard).
