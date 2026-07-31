# Construction: open items after the documentation audit

Follow-up to `docs/construction-doc-audit.md`. That audit left seven items
marked unverifiable and several more marked insufficient. This document
reports what could be closed by computing against artifacts already on disk,
what needs a run and exactly which run, and what cannot be closed at all.

Reference object is the same one: snapshot `20260727_042523_Headless_Run_Auto_ge`,
built from `experiment_configs/freeze_mcs55.toml` at seed 42, commit `c381211`,
outputs under `experiment_results/freeze_mcs55/seed_42/`. The 20-seed sweep is
`experiment_results/sweep20_s1..s20`.

Every number below is labelled **DERIVED** (computed here from an artifact or
from source, with the command shown) or **INFERRED** (an argument, not a
measurement). No run was started; no gradle was invoked.

Provenance rule used throughout, taken from the frozen config's own header:
*every result predating commit `c381211` is void*, because `c381211` fixed
`routeToVmfs` to score with shared kappa. Commit order confirmed:

```
git merge-base --is-ancestor a7fdf7d c381211   # true
git log --oneline a7fdf7d..c381211
  c381211 Route split candidates with the same rule the trickler uses
  b5313ed Remove the probe-era lastDeclineReason field
  e3c4b2c k-fallback for split proposals; decouple marginalEps and maxK
```

So `a7fdf7d` and everything older is pre-fix.

---

# 1. Closed by computation

Six of the seven unverifiable items moved. Four are fully closed, two are
closed as to the question but leave a run to do. Eleven further items that the
audit filed as "insufficient" or "undocumented" are also closed here.

## 1.1 SE(ΔJ) spread, edit counts, and worst z — re-derived from the frozen run

**Status: closed. The quoted numbers do not reproduce as stated, and the
correct restatement is stronger.**

`experiment_results/freeze_mcs55/seed_42/diagnostics/proposals.csv`, 373 data
rows, matches `run_manifest.json`'s `proposals_rows: 373`.

```python
import csv, numpy as np, statistics as st
rows = list(csv.DictReader(open(
  'experiment_results/freeze_mcs55/seed_42/diagnostics/proposals.csv')))
acc  = [r for r in rows if r['decision'] == 'ACCEPTED']
se   = sorted(float(r['SE_dJ']) for r in acc if float(r['SE_dJ']) > 0)
```

**DERIVED, composition of the log:**

| | count |
|---|---|
| rows | 373 |
| ACCEPTED | 70 (68 GROW, 2 SHRINK) |
| REJECTED | 173 (all `z_gate`) |
| NO_PROPOSAL | 129 (all `min_pair_sep_below_bar`) |
| RUBRIC_SPAN | 1 |

**DERIVED, SE(ΔJ) over the 69 accepted edits carrying a positive SE:**

| statistic | value |
|---|---|
| min | 3.2712e-05 |
| max | 4.3751e-04 |
| **max/min** | **13.375×** |
| p10 (numpy linear) | 6.3265e-05 |
| p90 | 2.5434e-04 |
| **p90/p10** | **4.020×** |
| median | 1.2793e-04 |

Over all 242 proposals with a positive SE: min–max 18.64×, p10–p90 5.61×.

The thesis and the frozen config header say "SE(ΔJ) spans 13.1× **p10–p90**".
The 13.1× reproduces almost exactly on the frozen run — but as **min–max**
(13.375×), not p10–p90. The frozen run's p10–p90 is 4.0×. The statistic was
mislabelled, not miscomputed. Also note `TaxonomyOperations.kt:44` states
"median SE(dJ) is 5.85e-5"; the frozen run's accepted-edit median is
1.28e-04, 2.2× larger.

**DERIVED, z on accepted edits:** min 2.0830, median 8.2710, max 24.0150.
Zero accepted edits below z = 1, and none below z = 2. That is forced — the
gate is `z* = 2.0`. So "4 of 52 edits at z < 1, worst z = 0.156" **cannot**
be a property of a run with the gate on. It is a counterfactual about the
uncalibrated rule, which the frozen config header states correctly and
`6_Results.tex:1108-1110` does not.

The frozen run's own counterpart to that counterfactual is directly derivable:
which rejections would a τ-only rule (ΔJ > τ) have accepted?

```python
tau = 1e-6
would = [r for r in rows if r['reason'].startswith('z_gate')
         and float(r['dJ']) > tau]
```

**DERIVED:** 56 rejection events over **8 distinct sites**. Best z per site:

| site | label | iterations blocked | best ΔJ | SE | best z |
|---|---|---|---|---|---|
| n00000032 | Emergent Concept #17 | 3 | 5.413e-05 | 1.309e-04 | 0.4135 |
| n00000053 | Emergent Concept #38 | 1 | 1.049e-04 | 2.082e-04 | 0.5038 |
| n00000006 | Chemistry | 1 | 2.451e-04 | 2.942e-04 | 0.8333 |
| n00000056 | Emergent Concept #41 | 3 | 4.172e-05 | 4.414e-05 | 0.9451 |
| n00000064 | Emergent Concept #49 | 21 | 1.039e-04 | 7.811e-05 | 1.3298 |
| n00000037 | Emergent Concept #22 | 21 | 4.047e-04 | 2.712e-04 | 1.4925 |
| n00000076 | Emergent Concept #61 | 3 | 8.373e-05 | 5.326e-05 | 1.5721 |
| n00000203 | Emergent Concept #188 | 3 | 1.701e-04 | 9.041e-05 | 1.8818 |

**4 of the 8 sites sit below z = 1.** Worst single blocked proposal:
ΔJ = 9.462e-06 against SE = 1.063e-04, **z = 0.0890** (iteration 2, site
n00000032). The void five-seed number was ΔJ = 9.4e-06 against SE = 6.0e-05,
z = 0.156 — same ΔJ to two figures, different SE, and the same shape of
finding.

**Replacement sentence the thesis can use, all of it derived from the frozen
run:** *On the frozen construction, the paired standard error of ΔJ varies
13.4× across the 69 accepted edits that move queries (3.27e-05 to 4.38e-04),
and 4.0× between its 10th and 90th percentiles. The z gate blocked eight
distinct split sites whose ΔJ exceeded τ, four of them at z < 1 and the worst
at z = 0.089 (ΔJ = 9.46e-06 against SE = 1.06e-04). A τ-only rule would have
committed all eight.*

**DERIVED, and worth stating separately: τ never binds.** The operative
threshold is `max(τ, z*·SE)`. Over the 173 gate rejections the logged
`need>` value ranges 8.828e-05 to 1.220e-03, minimum 88× τ. Over the accepted
edits, min `z*·SE` = 6.542e-05, 65× τ. So on the frozen run the acceptance
rule reduces to `ΔJ > 2·SE` everywhere, and the neutrality band τ decided
nothing. That is the sharpest available answer to R4 and it also finishes off
the two wrong statements of the rule in the appendix.

## 1.2 The four failing seeds — mechanism identified, and it is worse than "κ still moving"

**Status: closed. All four are period-2 limit cycles. The structural stopping
arm has a 0-for-3 certification record.**

All 20 certificates extracted from
`experiment_results/sweep20_s{n}/seed_{n}/fixed_point_certificate.txt`.

**DERIVED:** 16 certify, 4 do not (seeds 4, 5, 11, 12). `editsDelta` is
exactly 0 in all 20. `max rel Δκ` is **bimodal, not a continuum**:

| group | seeds | max rel Δκ |
|---|---|---|
| certified | 16 | 3.17e-13 – 6.79e-13 |
| failed | 4 | 1.30e-03 – 6.04e-03 |

Ten orders of magnitude between the groups, with nothing in between. No seed
is marginal. That rules out "tail noise" as a reading.

**DERIVED from `diagnostics/iteration_metrics.csv`, the mechanism:**

```
seed 5 : it10 J=0.256955 trickleΔ=+2.436468e-06
         it11 J=0.256952 trickleΔ=-2.436468e-06
         it12 J=0.256955 trickleΔ=+2.436468e-06   ... to it15
seed 11: 0.257168 ↔ 0.257164, trickleΔ = ±3.576201e-06
seed 12: 0.254366 ↔ 0.254354, trickleΔ = ±1.162318e-05
seed 4 : J fixed at 0.259891, trickleΔ = ±9.37e-10 from it8
```

Identical magnitude, alternating sign, every iteration, for as long as the
run continues. These are **period-2 limit cycles of the construction
operator**, with the structure frozen (GED = 0) and routing plus θ
oscillating between two states. The certificate tests for a period-1 fixed
point and correctly refuses to certify a 2-cycle.

Note this is the same failure mode the author already diagnosed once, at
`experiment_configs/dm000_s42.toml`'s header: *"That produced a period-2 limit
cycle: a marginal split at sep=0.021 was created locally on separation and
destroyed globally on (J, -|V|), forever."* That one was a split/fuse cycle,
visible in GED. This one is invisible to GED, because the structure does not
move at all.

**DERIVED, stopping arm by outcome:**

| stopping arm | fired | failed certificate |
|---|---|---|
| GED quiescence (structural) | 3 (seeds 5, 11, 12) | **3 of 3** |
| J stationarity (objective) | 17 | 1 of 17 (seed 4) |

One-tailed Fisher exact on 3/3 against 1/17, hypergeometric:
`P = C(4,3)·C(16,0)/C(20,3) = 4/1140` = **p = 0.0035**.

Interpretation, and it is a result rather than a caveat:

- The structural arm fired only when routing was in a 2-cycle whose J
  amplitude (2.4e-06 to 1.2e-05) exceeded τ = 1e-6, so J stationarity could
  never fire. GED quiescence then fired at iteration 15, the earliest
  possible instant (floor 11 plus a 5-streak). **The structural arm is what
  the runs fall back on when the objective refuses to settle, and it certified
  zero times out of three.**
- Seed 4 is the case the audit described: both arms are satisfied
  (`editsDelta` = 0, |trickleΔ| = 9.37e-10 ≤ τ) while κ moves by 1.3e-03,
  1300× the θ tolerance. So the κ motion there is nearly J-neutral — a
  direction the objective is flat in and neither criterion observes.
- None of the four hit the 50-iteration budget.

**Replacement paragraph the thesis can use:** *Four of twenty seeds fail the
certificate. All four fail on the concentration term by three to four orders
of magnitude, with the structural gate quiescent in every case. The mechanism
is not slow convergence: `iteration_metrics.csv` shows the re-routing delta
alternating in sign at constant magnitude for every remaining iteration, so
the construction operator has entered a period-2 cycle and the certificate,
which tests a period-1 fixed point, correctly refuses. Three of the four
stopped on the structural arm — which is every run in the sweep that did so
(Fisher exact, one-tailed, p = 0.0035). Neither stopping criterion observes θ,
and the structural criterion does not observe routing either.*

## 1.3 Newton–Raphson iteration count

**Status: closed. "One or two steps" is wrong at the artifact's operating
point. It is two or three, never more than three.**

`StatisticsUtils.correctedKappa` and `logBesselI` ported exactly to Python
(the Kotlin `logBesselI` is a uniform Debye asymptotic, so scipy would give a
different answer; the port reproduces the code, not the mathematics).

**DERIVED**, d = 256, using the loop's own break test
(`abs(next - kappa) < 1e-6 * kappa`), over a 4000-point grid of r̄ in
(0.001, 0.999):

| steps | share of grid |
|---|---|
| 1 | 0.7% (r̄ ∈ [0.032, 0.040] only) |
| 2 | 54.2% |
| 3 | 45.1% |
| 4 or 5 | 0% |

Transitions: 2→3 at r̄ = 0.377, 3→2 at r̄ = 0.827. The 5-step cap is never
reached anywhere in the domain.

The artifact's operating range: leaf κ (post-shrinkage, from the snapshot)
runs 43.83 to 224.22, median 97.03. Undoing the shrinkage factor
(n−1)/(n+d−2) for leaf sizes 54–396 puts κ_ML in roughly [72, 1303], so
r̄ ∈ [0.26, 0.91], which straddles the 3-step band and lands in it for almost
every leaf:

| κ_ML | r̄ | steps |
|---|---|---|
| 72 | 0.2621 | 2 |
| 150 | 0.4617 | **3** |
| 317 | 0.6753 | **3** |
| 600 | 0.8097 | **3** |
| 1303 | 0.9069 | 2 |

**Replacement sentence:** *The refinement takes two or three steps at d = 256
and never more than three anywhere in the domain of r̄; the five-step cap is
a safety bound that is never reached. At the artifact's leaf concentrations
it takes three.* (`11_Appendix:307-308` currently says one or two, sourced
from the code comment at `StatisticsUtils.kt:31`, which is also wrong and
should be corrected in the source.)

## 1.4 The A1 embedding-dimension ablation: runnable, and cheaper than expected

**Status: the audit's finding is confirmed — no ablation can have been run
from a configuration. But two things the audit did not establish make the
ablation cheap.**

**DERIVED, no config path exists.** `GraphNode.kt:360` is
`fun dimForDepth(depth: Int): Int = 256`, a literal with an unused parameter.
`grep -rn dimForDepth src/main/kotlin/` gives 16 references across 7 files
(`GraphNode`, `TaxonomyFitter:203`, `TaxonomySplitter:132`,
`TaxonomyMerger:711,906`, `EmbeddingCache:38`, `TaxonomyPersistence:171`,
`TaxonomyEngine:92`). There is no `mrlSliceDim` field in
`TaxonomyConfig.FormalismConfig`. The claim at `11_Appendix:450-452` that
d is "ablated at {128, 256, 512}" cannot correspond to any run.

**DERIVED, the embeddings on disk support the ablation with no re-embedding.**

```python
import sqlite3
c = sqlite3.connect('file:embeddings_cache.db?mode=ro', uri=True)
q, v = c.execute("select query, vector from embeddings limit 1").fetchone()
len(v)   # 16384
```

`EmbeddingCache.kt:224` decodes as `FloatArray(bytes.size / 4)`, so
16384 / 4 = **4096 dimensions**, 11,773 cached vectors. Every MRL prefix in
{128, 256, 512, 1024, 2048} is already sliceable from the cache. The
ablation costs construction time only — no Ollama calls.

**DERIVED, a second consequence:** 4096 dimensions identifies the embedding
model. Qwen3-Embedding ships at 1024 (0.6B), 2560 (4B) and 4096 (8B). So the
snapshot's `qwen3-embedding:latest` was **Qwen3-Embedding-8B**. That narrows
the "model version unrecoverable" item from the audit — the parameter class is
recoverable even though the exact revision behind `:latest` is not.

**The code change needed, precisely.** Add to `FormalismConfig`:

```kotlin
var mrlSliceDim: Int = 256
```

and in `GraphNode.kt`, replace the literal with a module-level mutable that
the config setter writes once at load:

```kotlin
@Volatile var MRL_SLICE_DIM: Int = 256
fun dimForDepth(depth: Int): Int = MRL_SLICE_DIM
```

That is roughly five lines plus one assignment in `TaxonomyConfig`'s TOML
binder. No call site changes — the function comment at `GraphNode.kt:353-359`
says the seam was kept for exactly this. `TaxonomyEngine.kt:92`'s fast-fail
(`minRequired = dimForDepth(maxDepth)`) then does the right thing for free at
any d ≤ 4096.

**INFERRED confound, and it is a real one.** Changing d does not isolate
representation width. Three other quantities move with it:

| d | shrinkage (n−1)/(n+d−2) at n = 88 | ρ = d/n | EB blend α |
|---|---|---|---|
| 128 | 0.407 | 1.45 | 0.00 |
| 256 | 0.254 | 2.91 | 0.114 |
| 512 | 0.145 | 5.82 | 0.477 |

At d = 512 nearly half of every leaf's concentration is the parent prior; at
d = 128 the parent-anchored blend is switched off entirely. On top of that,
the PCA subspace ladder is 32/64/128 by target size (`TaxonomySplitter:137-141`),
so at d = 128 the largest rung equals the full space and the projection stops
being a projection. An A1 that varies d alone therefore confounds width with
the small-sample stabilisation regime and with the proposal geometry. Any
reported A1 must say so, or hold α fixed by adjusting the ramp — which is a
different experiment.

## 1.5 The residual subsystem: not dead code, and the margin over-pays by 1.85×

**Status: closed as to whether the subsystem works. Open as to the exact
threshold at the frozen configuration.**

**DERIVED, the descent bar is not vacuous at 0.12.** Computing
`childCentroidShrinkage` (r̄_v = ‖Σ_c ω_c μ̂_c‖) for all 67 internal nodes of
the frozen tree, straight from `dag_snapshots.jsonl`'s per-node `vmfMu` and
child masses:

| weighting | min | p25 | median | p75 | max |
|---|---|---|---|---|---|
| by direct mass (what the code does) | 0.8495 | 0.9647 | 0.9703 | 1.0000 | 1.0000 |
| by subtree mass | 0.8519 | 0.9614 | 0.9680 | 0.9718 | 0.9814 |

`descentBar = max(0, r̄_v − 0.12)` therefore sits between 0.73 and 0.88 —
around 0.85 at the median. The gate demands
`bestChildDot ≥ 0.85 · parentDot`. That is not "relaxed past the point where
anything residualises" in the sense of being switched off; it is a live gate
that nothing in the corpus trips.

**DERIVED, why nothing trips it.** The `[MU-GAP]` diagnostic in
`headless_run.log` reports exactly the quantity the margin exists to pay for:

```
Iteration 10 | internal nodes=67 cos(mu_v, resultant)
              min=0.9514 p10=0.9949 median=0.9989 max=0.9999
```

Worst Jensen gap on the frozen run is 1 − 0.9514 = **0.0486**. Across all 21
runs (20 sweep seeds plus the frozen one) the worst is 0.0647 at seed 20.
So `descentMargin = 0.12` is **2.47× the worst gap on the frozen run and
1.85× the worst gap ever observed**. The margin is not calibrated to the
quantity it is derived from — it is roughly double it.

**DERIVED, off-configuration runs that already produced residuals:**

| run | descentMargin | mcs | bar | seed | commit | residual queries | held-out residual rate |
|---|---|---|---|---|---|---|---|
| `freeze_mcs55` | 0.12 | 55 | 0.025 | 42 | c381211 | **0** (0.00%) | 0.00% |
| `dm000_s42` | 0.00 | 30 | 0.025 | 42 | pre-fix | **7** (0.08%) | **6.42%** |
| `repro_seed2048` | 0.05 | 25 | 0.01 | 2048 | pre-fix | **30** (0.36%) | not exported |
| `tuning/` L9 ×3 | 0.06 | 25/30/35 | .01–.03 | 42 | 334b95d | 0 | — |
| `tuning/` L9 ×3 | 0.12 | 25/30/35 | .01–.03 | 42 | 334b95d | 0 | — |
| `tuning/` L9 ×3 | 0.18 | 25/30/35 | .01–.03 | 42 | 334b95d | 0 | — |

(L9 rows from `tuning/combined_ledger.csv`, column `ResidualCount`.)

**The subsystem is not dead code.** It fires at margins 0.00 and 0.05 and is
silent at 0.06 and above, across three commits and four configurations. The
bracket is (0.05, 0.06] — but the two runs that bracket it differ on
`membershipFloor` (0.25 vs 0.15), `routingBeamGamma` (0.1 vs default), seed
and commit, so it is a bracket and not a threshold.

**DERIVED, a claim in the tuning appendix that does not reproduce.**
`7_Appendix:58-63` says a descentMargin near 0 costs "roughly five points of
routing quality". The only artifact that could support it is `dm000_s42`:

```
freeze_mcs55  Top1Accuracy = 0.774660  (3599 held-out)
dm000_s42     Top1Accuracy = 0.743583  (3584 held-out)
```

That is **3.11 points**, not five, and the comparison is void anyway — `dm000`
is pre-`c381211`, at `minClusterSize = 30`, and carries an extra model
(`Meta-Llama-3-70B-Instruct`) in its roster, which is why the held-out counts
differ. The config file also carries a stale `cal_seeds_bar025.toml` header,
the exact sed-derivation failure `freeze_mcs55.toml` warns about.

## 1.6 The split-acceptance rule, stated once, correctly

**Status: closed. Confirmed against `TaxonomyOperations.isProposalAccepted`
(lines 55-69). Four statements exist in the thesis; three are wrong.**

The rule the code implements, in full:

> A proposal is committed iff
>
> * SE_paired(ΔJ) > 0 and ΔJ > max(τ, z*·SE_paired(ΔJ)), with z* = 2.0,
>   τ = 1e-6; **or**
> * SE_paired(ΔJ) = 0 and ΔV < 0.
>
> The two branches are alternatives, not layers. When SE > 0 there is no
> lexicographic tie-break, so a J-neutral simplification with positive SE
> cannot commit. SE = 0 identifies a pure structural edit that moves no
> query, for which ΔJ is exactly 0 and z is undefined; the size test lets
> those commit. The gate is applied identically to GROW, sibling fusion,
> near-duplicate fusion, starved-leaf handling and sole-child dissolution,
> because `tryProposal` is the single path for all of them.

On the frozen run the τ arm never bound (§1.1), so the operative rule was
`ΔJ > 2·SE` throughout.

The three wrong statements: `11_Appendix:122-123` (ΔJ > τ),
`11_Appendix:626-629` (ΔJ > 0), and — undocumented by the audit — the SE = 0
branch appears nowhere at all, so the correct statement at
`11_Appendix:672-678` is also incomplete as a specification.

**One stale source comment to fix while you are there.**
`TaxonomyOperations.kt:52` says *"That is why `acceptanceZ = 0` is canonical."*
The canonical config sets 2.0 and `TaxonomyConfig.kt:105` still defaults to
0.0. Anyone reading the source for the canonical value gets the opposite of
the truth.

## 1.7 Phase-5 operator ordering

**Status: closed by reading `TaxonomyMerger.optimizeHierarchy` (lines 33-73).
No run needed.**

Non-learning phase, in order, once per iteration:

1. `pruneUnrelevantNodesWithProposals` — starved-leaf handling.
2. `mergeSimilarSiblingsWithProposals` — sibling fusion.
3. `mergeRedundantNodesWithProposals` — near-duplicate fusion.
4. `do {} while (prunePassthroughNodes(...))` — sole-child dissolution,
   **repeated to a fixed point within the iteration**.
5. `pruneUnrelevantNodesWithProposals` again — starved-leaf, second pass.
6. `removeStaleParentRefs`, `invalidateAncestorCache`, then `isBridge` recompute.

So starved-leaf handling runs twice and dissolution runs to convergence, both
of which the thesis omits. Each accepted move re-routes the corpus and becomes
the next proposal's base (`TaxonomyOperations.kt:735-737`), so the order is
outcome-relevant and this list belongs in the appendix verbatim.

## 1.8 `fusionSimilarityThreshold = 0.90` — what it filters, and how close to inert it is

**Status: closed. The value sits one step from switching the operator off.**

`TaxonomyMerger.kt:954-978`: near-duplicate fusion enumerates all node pairs,
keeps those with `depth > 1`, identical parent sets (`isTreeLegalFusionPair`
is `nodeA.parents == nodeB.parents`), no ancestry relation, then **skips any
pair with `cos(μ_A, μ_B) ≤ fusionSimilarityThreshold`**. Survivors go to the
chance-corrected separation test at `proposalSeparationBar`.

**DERIVED** on the frozen tree, computing all pairwise cosines from
`dag_snapshots.jsonl`:

| | |
|---|---|
| tree-legal same-parent pairs at depth > 1 | 81 |
| max cosine in the whole tree | **0.9194** |
| median | 0.8686 |
| min | 0.7290 |
| pairs admitted at 0.90 (config) | **9 of 81 (11%)** |
| pairs admitted at 0.92 (`TaxonomyConfig.kt` default) | **0 of 81** |
| pairs admitted at 0.85 | 55 |

The operator's activity is a step function right at the chosen value. At the
code's own default the near-duplicate fusion pass sees nothing at all. The
thesis lists 0.90 in a table as "Fusion pre-filter threshold" and never says
what it filters or that 0.02 higher makes the operator inert.

## 1.9 What the coarsening operators actually did

**Status: closed. Three of the four named moves never fired.**

**DERIVED** from `proposals.csv` and the log tag histogram:

- 12 SHRINK proposals in the entire run against 360 GROW.
- **2 SHRINK accepted**, both at iteration 2, both on Psychology, both with
  ΔV = −1, i.e. sole-child dissolutions. The log confirms:
  `dissolving sole child 'Emergent Concept #20' into 'Psychology'
  (4 grandchildren hoisted)`.
- The other 10 SHRINK proposals were rejected at z between −7.2 and −14.6 —
  strongly harmful, correctly refused. Nine of the ten are the same Philosophy
  site re-proposed every iteration.
- `grep -cE "\[FUSE|Sibling Fusion|Redundant"` over `headless_run.log` returns
  **0**. No fusion of any kind fired.

So the four-move coarsening apparatus contributed **2 of 70 accepted edits**,
both of one type. Sibling fusion, near-duplicate fusion and starved-leaf
absorption produced nothing on the artifact every result is attributed to.
`3_System_Architecture.tex:131-135` and `11_Appendix:125-136` describe all
four as live machinery.

## 1.10 The diffuse-node branch is unreachable, not merely inactive

**Status: closed. Strengthens the audit's §8 "Undocumented 2".**

`TaxonomySplitter.kt:77` gates the diffuse path on `κ < 0.5 && mass < 10·mcs`.

**DERIVED:** zero of 154 nodes in the frozen artifact have κ < 0.5; the
minimum is 43.83. And the first conjunct cannot be satisfied at all at
d = 256 for a split-eligible node:

- Split eligibility already requires mass ≥ 2·`minClusterSize` = 110.
- Shrinkage at n = 110, d = 256 is (n−1)/(n+d−2) = 109/364 = 0.2995.
- κ_final < 0.5 therefore needs κ_ML < 1.670.
- Inverting the Banerjee seed r̄(d − r̄²)/(1 − r̄²) = 1.670 at d = 256 gives
  **r̄ < 0.00652**.

The least concentrated node in the tree has r̄ ≈ 0.167 (κ = 43.83), 25× that.
Real text embeddings do not produce r̄ < 0.007 on 110 points. So the diffuse
branch, the residual-viability path inside it, and the 2ε_sep margin the
appendix attributes to it are unreachable at d = 256 by arithmetic, not by
configuration. The undocumented `mass < 10·mcs` conjunct is moot for the same
reason. This should be stated once and the whole branch described as retired.

## 1.11 A fourth wrong statement in the splitting section, which the audit missed

**Status: new. `11_Appendix:620-624` names three gates in stage 3; the
operative one is not among them.**

The appendix says the routed partition *"must score s ≥ ε_sep (2ε_sep for
small populations), and each new child must remain chance-corrected-distinct
(≥ ε_sep) from every existing sibling branch."* Three claims:

1. **Joint k-way score `s ≥ ε_sep`** — removed. `TaxonomySplitter.kt:462-478`
   records the removal: at routed k = 2, `sepScore` and `minPairSep` are the
   same number, and above k = 2 the coarsening loop has already merged every
   sub-bar pair. `sepScore` is still computed but only as
   `dasguptaDeltaNorm`, a diagnostic. Measured 5682 min-pair rejections
   against 0 k-way across the repo.
2. **The 2ε_sep small-population margin** — removed (audit §8, Wrong 2).
   Confirmed: `bar=0.0500` appears zero times in the logs.
3. **Sibling distinctness against existing siblings** — removed, and it was
   *vacuous before removal*. `TaxonomySplitter.kt:480-490`: the guard iterated
   `node.children`, but the function returns at its first line unless
   `node.isLeaf`, and `isLeaf` is `children.isEmpty() && crossLinkChildren.isEmpty()`.
   The collection was always empty and `all {}` on it was always true. Its log
   line "Split Rejected: child too similar to sibling" appears zero times in
   every run in the repo.

The gate that actually runs is the **min-pairwise** bar
(`TaxonomySplitter.kt:428-446`): every routed child pair must clear
`proposalSeparationBar` on the same chance-corrected statistic the sibling
merger uses to destroy a pair. That single sentence replaces all three.

Frozen-run evidence: **129 of 373 proposal rows are
`min_pair_sep_below_bar`**, and zero are anything else in that family.

## 1.12 The A5b ablation row is void by the thesis's own rule, and is a three-factor comparison

**Status: new. `7_Appendix:217-224`.**

The appendix says three ablation rows have citable outcomes and gives A5b's:
*"83 leaves at J = 0.230247 against the canonical artifact's 87 leaves at
J = 0.253129."*

**DERIVED**, by scanning every `iteration_metrics.csv` on disk for that pair:

```
experiment_results/marginaleps0_repaired/seed_42/  leaves=83  J=0.230247  commit=a7fdf7d
```

`a7fdf7d` is pre-`c381211`. The very next paragraph of the same appendix voids
the maxK plateau *because* it predates that correction. So the appendix voids
one pre-fix result and cites another from the same commit, two sentences
apart.

Worse, the table caption says each ablation varies "exactly one hyperparameter
while holding all others fixed". `marginaleps0_repaired.toml` differs from
`freeze_mcs55.toml` on **three**:

| | canonical | A5b run |
|---|---|---|
| `marginalEps` | −1.0 (default) | 0.0 |
| `minClusterSize` | 55 | **30** |
| `acceptanceZ` | 2.0 | **0.0** |

A leaf-count comparison against the canonical is meaningless when the size
floor is nearly halved and the acceptance gate is switched off.

## 1.13 The maxK plateau, re-checked

**Status: the appendix's handling is correct — the numbers are void. Confirmed
with the artifacts.**

`experiment_results/kfb_maxk{4,6,8,10}` exist, all at commit `a7fdf7d`
(pre-fix), all at `minClusterSize = 30`:

| maxK | nodes | leaves | J | certified |
|---|---|---|---|---|
| 4 | 141 | 84 | 0.238987 | true (iter 10) |
| 6 | 155 | 93 | 0.241473 | true (iter 11) |
| 8 | 157 | 94 | 0.241567 | run incomplete, no certificate |
| 10 | — | — | — | no artifacts |

ΔJ from 4→6 is +2.5e-03; from 6→8 is +9.4e-05, 26× smaller. That is the
plateau the config header describes. It is void as to values and the appendix
says so. `maxK` is a real config key (`TaxonomyConfig.kt:182`), so a
re-derivation needs no code change.

## 1.14 Two artifact-reading defects worth fixing

**`iteration_metrics.csv` column names are wrong.** `TaxonomyEngine.kt:640-643`
writes `gedAdd = stabilizationResult.ged` and
`gedRem = stabilizationResult.volumeDelta.toInt()`. So the column labelled
`ged_rem` is the truncated log-semantic-volume delta, not an edge-removal
count. The frozen run's iteration 2 reads `ged_add=92, ged_rem=12157` — that
is GED 92 and a volume delta of 12157, not 12157 removed edges. Anyone
analysing the CSV without reading the writer gets this wrong. **DERIVED**
from source.

**`updateChildCentroidShrinkage` weights internal children at zero.**
`GraphNode.kt:150` uses `child.queryWeights.values.sum()` as the mixing
weight. **DERIVED** from the snapshot: all 67 internal nodes have
`directQueries = 0`, so every internal child contributes weight 0. Of the 67
internal nodes, 21 have mixed children and 20 of those have exactly one leaf
child — at which the resultant collapses to that single leaf's μ and r̄_v = 1.0
exactly. Fourteen nodes have only internal children, where `sumW = 0` triggers
the uniform-weight fallback. The effect on the median is small (0.9703 vs
0.9680 under subtree-mass weighting) but the maximum moves from 0.9814 to
1.0000, which is precisely where the descent bar is loosest. Not thesis-facing
yet, because nothing residualises either way, but any residual-margin
experiment lands on this first.

---

# 2. Items that need a run

Four runs, in value order. All are construction-only, single-seed, and none
touch the arena. Wall-clock reference: the frozen run took **1,317,749 ms
(22 minutes)** at 10 iterations with labelling and judge induction on
(`run_manifest.json`). With `enableLabeling = false` and
`judgeInduction = false` the sweep runs are faster; budget ~15 minutes each.

## R-A. A1 embedding-dimension ablation — highest value, needs the 5-line patch

**Why it is first.** MRL's entire selling point is that any prefix is a valid
representation. The thesis fixes d = 256 and justifies it with a claim
(`11_Appendix:450-452`) that no run can have produced. Right now the choice is
unsupported at any width. It is also the cheapest real ablation available,
because §1.4 shows the cache already holds 4096-dimensional vectors.

**Patch:** `FormalismConfig.mrlSliceDim: Int = 256`; module-level
`@Volatile var MRL_SLICE_DIM` in `GraphNode.kt`; `dimForDepth` returns it;
one assignment in the TOML binder. About five lines. Add it to the locked
hyperparameter table at the same time.

**Configs:** copy `freeze_mcs55.toml` to `a1_d128.toml`, `a1_d512.toml`,
`a1_d1024.toml`; change `outputDir`, set `mrlSliceDim`, set
`enableLabeling = false` and `judgeInduction = false`. Rewrite the header
(do not sed the frozen one). Everything else identical, seed 42.

**Cost:** three runs, ~45 minutes total, no API calls.

**What it buys.** A table of leaf count, J, held-out Top-1, ECE and
certificate status against d ∈ {128, 256, 512, 1024}. Either d = 256 is a
flat region and the thesis can say so with numbers, or it is not and the
thesis reports a sensitivity it currently asserts away. Both outcomes are
publishable. Either way `11_Appendix:450-452` stops being a claim about a run
that never happened.

**Mandatory caveat to report with it** (§1.4): d also moves the κ shrinkage
factor and the EB blend weight α, and at d = 128 the PCA ladder's top rung
equals the full space. State the confound; do not present A1 as isolating
representation width.

## R-B. Repeat the frozen run at seed 42 — closes the reproducibility claim

**Why.** `6_Results.tex:1100-1104` says "two of the six certificate fields are
bounded rather than exactly reproducible, because routing is parallel and
float accumulation is not associative." **DERIVED:** scanning all 82
`run_manifest.json` files on disk, exactly **one** has
`config_sha256 = 5ae10780…c70f`. There has never been a second run of the
frozen configuration. The claim is unsupported by any artifact.

**Config:** `freeze_mcs55.toml` verbatim, `outputDir` changed to
`experiment_results/freeze_mcs55_repro`. Nothing else. Seed 42.

**Cost:** one run, ~22 minutes with labelling on, ~15 without. Turn labelling
off; it is not what is being tested.

**What it buys.** A field-by-field diff of two certificates from the same
config and commit. That either names the two non-reproducible fields or shows
all five reproduce bit-for-bit, in which case the sentence should be deleted.

**INFERRED prediction, for pre-registration:** the two bounded fields are
`trickleDelta` and `maxKappaRel`. `editsDelta` is exactly 0 and
`final iteration` is an integer, so neither can drift. `maxMuDelta` takes only
two values across all 21 existing runs — 0.0 or 1.110223e-16, which is one ULP
— so it is quantised rather than continuous. That leaves two continuous
accumulations. Register the prediction before running.

## R-C. descentMargin ladder at the frozen configuration

**Why.** §1.5 shows the residual subsystem works and is bracketed at
(0.05, 0.06], but every run in that bracket is off-configuration and
pre-`c381211`. At the frozen configuration nothing is known except that 0.12
gives zero.

**Configs:** copy `freeze_mcs55.toml` four times, vary `descentMargin` over
{0.00, 0.04, 0.06, 0.08}, keep everything else including
`minClusterSize = 55`, seed 42, labelling off.

**Cost:** four runs, ~60 minutes.

**What it buys.** Three things at once.

1. The first margin at which `Residual Queries > 0` **at the frozen
   configuration**, which converts "the residual subsystem is switched off"
   from an inference into a measurement and lets the thesis say where the
   mode boundary is.
2. A replacement for the "roughly five points of routing quality" claim,
   which currently does not reproduce (§1.5: the only supporting artifact
   gives 3.11 points and is void). Held-out Top-1 at each margin, all at
   c381211, all at mcs = 55, is a clean one-factor curve.
3. A justification for 0.12 that references the measured Jensen gap. The
   worst gap ever observed is 0.0647; a margin of 0.08 covers it with 24%
   slack instead of 85%. If 0.08 gives zero residuals and equal Top-1, the
   thesis can say the margin was set to cover the measured worst-case gap and
   verified inert — which is an argument, unlike the current table row.

Run 0.00 and 0.06 first; if 0.06 already residualises, drop 0.08.

## R-D. maxK re-derivation post-`c381211`

**Why.** `maxK = 4` bounds the ascending-k loop directly, is absent from the
hyperparameter table, and the only measurements of its effect are at
`a7fdf7d` and `minClusterSize = 30` (§1.13). No code change needed — `maxK`
is a live config key.

**Configs:** `freeze_mcs55.toml` with `maxK` ∈ {2, 6, 8}, seed 42, labelling
off. (maxK = 4 is the frozen run itself.)

**Cost:** three runs, ~45 minutes. maxK = 8 will be the slowest — the pre-fix
run at 8 attempted 1106 proposals against the frozen run's 463.

**What it buys.** A table row for `maxK` with current numbers, and either
confirmation that the 6→8 plateau survives the router fix (in which case
"cost bound, not structural determinant" becomes a defended claim) or the
finding that it does not. Also lets the appendix delete the "void as to
values, qualitative finding stands" hedge.

---

# 3. Cannot be closed — state as limitations

## 3.1 The 42 cross-link proposals and r(f, ΔJ) = +0.085

**Unrecoverable.** **DERIVED:** scanning all 82 `proposals.csv` files on disk
gives proposal types `{GROW: 26388, SHRINK: 1800, RUBRIC: 3}`. There is no
bridge or cross-link proposal type anywhere in the current diagnostics
schema, because the operator was deleted at `334b95d`. The measurements can
only be regenerated by checking out the cross-link-era commit, rebuilding,
and re-running — which produces a taxonomy at an obsolete router and is not
worth 22 minutes plus a build.

**Limitation to state:** *The polyhierarchy measurements come from a
construction the current source can no longer produce. They are reported as a
retired negative result and are not re-derivable from the frozen artifact.*
`6_Results.tex:1703-1744` already frames the outcome correctly; it should say
this about the provenance too.

## 3.2 The within-node null median "~0.04"

Correctly marked void as to values in `docs/separation_null_by_size.md:9`.
Re-deriving it means re-running `SeparationNullBySizeTest` against the frozen
tree — which is a test, not a benchmark, and would take a build. Worth doing
if the build is free, but it is not on the critical path: the isotropic table
in the same doc (p95 0.0090 → 0.0055 over n = 160 → 900) is current and is
what licenses `ε_sep = 0.025` from below. The within-node figure only
supports the upper bracket, and the thesis already states it as "above it"
rather than as a number.

Note the working tree has `src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt`
modified and uncommitted. Whatever that change is should be resolved before
the number is quoted again.

## 3.3 The exact embedding model revision

`qwen3-embedding:latest` in the snapshot `config` blob. `:latest` is a moving
tag, and Ollama's digest is not recorded in `run_manifest.json`. **Partially
closed** by §1.4: the stored vectors are 4096-dimensional, which identifies
the model as Qwen3-Embedding-8B. The specific weight revision behind the tag
on 27 July 2026 is gone.

**Limitation to state:** *The embedding model is Qwen3-Embedding-8B, served
via Ollama under the moving tag `qwen3-embedding:latest`; the exact revision
is not recorded and the construction is therefore not reproducible from
scratch against a future pull of that tag. It is reproducible against
`embeddings_cache.db`, which holds all 11,773 vectors used.* That second
sentence is worth having — it makes the artifact reproducible in the sense
that matters.

## 3.4 The 561-question routing disagreement

Out of scope for construction, and the audit already identified the likely
cause (the arena-side entropy guard at `TaxonomyArenaService.kt:455-462`).
Two things make it closable cheaply and neither is a construction run: the
guard is already instrumented — `tuning/combined_ledger.csv` carries an
`EntropyGuardRate` column, with values from 0.0 to 0.716 across the L9 rows —
and `TaxonomyBenchmarkService.kt:355-358` compares leaf **ids** against a map
keyed by leaf **labels**, so the guard's effect and the key mismatch can be
separated by inspection of an existing arena export rather than by a run.
Flagging it here so it does not get lost between the construction and arena
audits.

---

# 4. What a reviewer would still object to

Gaps the audit did not cover, ordered by how hard they are to answer.

**4.1 The acceptance gate has never been shown to change the outcome.**
§1.1 derives that the gate blocked eight sites a τ-only rule would have
committed. That is what the gate *refused*, not what refusing bought. The
counterfactual tree — same config, `acceptanceZ = 0.0` — is one 15-minute run
and there are already `zgate/tau_s42` and `zgate2_repaired` artifacts at
older commits. A reviewer will ask what the gate is worth and the answer is
currently a mechanism argument with no measured consequence. This is the
cheapest missing experiment in the whole chapter and it is not in §2 only
because R-A through R-D close documented contradictions and this one closes an
argumentative gap. Consider it R-E.

**4.2 Four of the eight gate-blocked sites were blocked in every single
iteration.** Sites n00000064 and n00000037 were each rejected 21 times across
iterations 4–10 with ΔJ stable at 1.04e-04 and 4.05e-04. The construction
re-proposes, re-bootstraps 200 Dirichlet replicates, and re-rejects the same
edit seven times running. The memoisation added at `9a0aab2`/`a7fdf7d` should
catch this and does not — `[MEMO]` appears 10 times in the frozen log, once
per iteration. That is a cost finding, and it also means the "463 proposals
attempted" figure counts the same decision repeatedly.

**4.3 There is no no-taxonomy baseline for the construction itself.** The
thesis reports J = 0.2531, 87 leaves, Top-1 0.7747. Against what? A flat
14-cell partition by MMLU-Pro category costs nothing to score and is the
obvious floor. The audit checked that every reported number is correct; a
reviewer will ask what any of them mean. (This overlaps the standing
`thesis-review-backlog` item and is stated here because the construction
chapter, not just the arena, needs it.)

**4.4 The stopping rule has a measured failure mode and no fix.** §1.2
establishes that the structural arm certified 0 for 3. The honest fix is one
line: require the certificate's θ terms as a third conjunct of the stopping
test, or refuse to stop on the structural arm while |trickleΔ| > τ. Either
turns a limitation into a correction. A reviewer who reads §1.2 will ask why
the diagnostic exists if nothing acts on it.

**4.5 The 20-seed sweep is a 19+1 build.** The audit flagged that seed 20 came
from `83ff7ba` rather than `c381211` and that the difference is behaviourally
inert. It is also true that seed 20 has the worst μ-resultant gap of all 21
runs (cos = 0.9353 against 0.9514 for the frozen run). That is almost
certainly coincidence, but "almost certainly" is what a reviewer will not
accept from a 19+1 build. Rebuilding seed 20 at `c381211` costs 15 minutes and
removes the question.

**4.6 One accepted edit has no z at all.** The iteration-2 SHRINK on Psychology
committed with ΔJ = 0, SE = 0, z blank, ΔV = −1. That is the SE = 0 branch
working as designed, and it is the *only* time it fired in 70 accepted edits.
A rule branch that fires once should either be justified with that number or
described as a special case rather than as a co-equal arm.

**4.7 `numIterations = 35` in a table footnoted "read from its run
configuration".** The audit caught this. It is worth restating that the fix is
not just the number — the footnote makes a provenance claim about the whole
table, and the table also omits `maxK` (§1.13), which is the only omission
that changes structure. Fix both or drop the footnote.

**4.8 Nothing records that the frozen run's `dirty` flag is uninformative.**
`run_manifest.json` reports `dirty: true` with 15 files listed, 14 of them
`report/*.tex` and one a test. The config header explains this; the manifest
does not, and the manifest is the machine-readable artifact. A
`dirty_production_source` boolean would cost one line and make the flag mean
something.

---

# 5. Prioritised list

Documentation corrections first — they cost nothing and several of them are
the difference between a reader trusting the chapter and not.

**Tier 0 — text fixes, no runs, all numbers already derived above**

1. State the split-acceptance rule once, with the SE = 0 branch (§1.6), and
   delete the two superseded statements at `11_Appendix:122-123` and
   `11_Appendix:626-629`.
2. Rewrite stage 3 of the splitting section (§1.11). Three named gates, none
   of which run; the min-pair bar, which does, is not named.
3. Replace the R4 evidence sentence with the frozen-run derivation (§1.1),
   including that τ never binds.
4. Replace the four-failing-seeds sentence with the limit-cycle mechanism and
   the 0-for-3 structural-arm record (§1.2).
5. Correct "one or two Newton steps" to "two or three, never more than three"
   (§1.3) — in the thesis *and* in `StatisticsUtils.kt:31`.
6. Say that the residual subsystem is inactive at the operating point, and
   that the margin is 1.85× the worst measured Jensen gap (§1.5).
7. Add the Phase-5 operator order (§1.7) and say what
   `fusionSimilarityThreshold` filters, with the 9-of-81 number and the fact
   that 0.92 admits none (§1.8).
8. Fix `numIterations` 35 → 50 and add `maxK` to the table.
9. Withdraw or re-source the A5b row (§1.12) and the "roughly five points"
   claim (§1.5). Both are pre-`c381211` and the second does not reproduce even
   there.
10. Say that the coarsening apparatus contributed 2 of 70 edits and that no
    fusion fired (§1.9). Describe the diffuse branch as unreachable, with the
    r̄ < 0.0065 arithmetic (§1.10).

**Tier 1 — runs, in order**

11. **R-A**, the d ablation. Needs the 5-line patch. Three runs, ~45 min.
    It is the only one that turns an unsupported assertion into a result, and
    it is the one an examiner reading the MRL section will ask about first.
12. **R-E** (§4.1), the `acceptanceZ = 0` counterfactual at the frozen config.
    One run, ~15 min, no patch. Measures what the most-defended design
    decision in the chapter is actually worth.
13. **R-C**, the descentMargin ladder. Four runs, ~60 min, no patch. Buys the
    mode boundary, a replacement for a claim that does not reproduce, and a
    real justification for 0.12.
14. **R-B**, the seed-42 repeat. One run, ~15 min. Cheap, and it is the only
    way to keep the reproducibility sentence.
15. **R-D**, the maxK re-derivation. Three runs, ~45 min. Lowest value —
    it fills a table row and removes a hedge.

**Tier 2 — source hygiene, thesis-invisible but audit-visible**

16. Fix the `ged_add`/`ged_rem` column names in `iteration_metrics.csv`
    (§1.14). Anyone reproducing the stopping analysis from the CSV gets it
    wrong.
17. Fix `updateChildCentroidShrinkage` to weight children by subtree mass
    (§1.14). Do this **before** R-C, or R-C measures the defect.
18. Fix the stale `acceptanceZ = 0 is canonical` comment at
    `TaxonomyOperations.kt:52` and the stale comment at
    `TaxonomyTrickler.kt:151-153`.
19. Add `dirty_production_source` to the manifest (§4.8).

---

## Summary of what moved

| Audit item | Status now |
|---|---|
| A1 dimension ablation | Confirmed unrunnable; 5-line patch specified; cache is 4096-d so the runs are free of API cost |
| Newton–Raphson step count | **Closed** — 2 or 3, three at the operating point, cap never reached |
| SE(ΔJ) spread and edit counts | **Closed** — 13.4× min–max, 4.0× p10–p90, 8 blocked sites, 4 below z = 1, worst z = 0.089, τ never binds |
| Two of six certificate fields | Not closed; no second run exists; the two are predicted and R-B settles it |
| 42 cross-link proposals | **Unrecoverable** — no bridge proposal type exists in any of the 82 logs on disk |
| Within-node null ~0.04 | Not closed; correctly void; not on the critical path |
| Embedding model version | **Partially closed** — 4096 dims identifies Qwen3-Embedding-8B; the revision is gone |
| Failing seeds (audit gap 5) | **Closed** — period-2 limit cycles; structural arm 0-for-3, p = 0.0035 |
| Residual subsystem (audit gap 3) | **Closed as to viability** — fires at 0.00 and 0.05, silent from 0.06; margin is 1.85× the worst Jensen gap |
| Phase-5 ordering (audit gap 13) | **Closed** from source |
| `fusionSimilarityThreshold` (audit gap 13) | **Closed** — 9 of 81 pairs at 0.90, 0 at 0.92 |
