# Separation null as a function of node population

> **SCOPE NOTE (2026-07-27), added after commit `c381211`.** Split by section:
>
> * **The isotropic table and its reading are current.** They are generated on synthetic
>   clouds driven through the real `splitSingleNode`, so they measure the splitter's
>   behaviour on structureless data. The routing-sustainability correction changes which
>   *real* splits pass, not the shape of the isotropic null.
> * **The within-node section is VOID as to values.** "The within-node null on every accepted
>   split", the 50 accepted splits, the q values, the six named marginal splits, the Computer
>   science worked example and the leaf-lineage exposure table (7 / 25 / 13 leaves; 9.2% /
>   19.7% / 10.3%) were all computed on the **pre-`c381211`** 88-leaf tree, which is
>   superseded. **The method survives and is the right method** — including the censoring
>   control, the reach-first reading, and the anisotropy caveat. Re-derive the numbers on the
>   frozen mcs=55 artifact ([`frozen-artifact.md`](frozen-artifact.md)). The same applies to
>   the `docs/data/within_node_null_*.csv` exports and to the lambda1/lambda-bar proxy fitted
>   against these targets (R^2 0.865, LOO Q^2 0.851 — method survives, values do not).
>   **DONE 2026-09-07: see "CURRENT (2026-09-07, frozen mcs=55 artifact)" at the bottom of
>   this file (`gradlew withinNull`).**
> * **The configuration described is not the frozen one.** This sweep was run at
>   `minClusterSize = 30`; the frozen artifact uses 55, so the grid, the split-eligible
>   population and the `2*minClusterSize` prefilter all shift. The **bar** it justifies
>   (`proposalSeparationBar = 0.025`) is unchanged.
> * See [`void-results.md`](void-results.md) for the full list.

Measured by `gradlew nullBySize` (`SeparationNullBySizeTest`, arm A), which drives the real
`TaxonomySplitter.splitSingleNode` on structureless clouds rather than reimplementing it.
Fidelity check in the same suite: replaying the frozen Philosophy node through this driver
reproduces `sep = 0.02077` against the canonical run's logged `0.0208`.

Generator: isotropic single-mode, sigma = 0.5, d = 256, canonical `minClusterSize = 30`,
`proposalSeparationBar = 0.025`. 300 replicates per point. Grid matched to the frozen tree's
split-eligible population (88 leaves, 30..406, median 75; 32 sit below `2*minClusterSize` and
can never be candidates again, so the prefilter only ever sees n >= 60).

| n | splitDim | p50 | p90 | **p95** | p99 | p95 95% CI | reach% | accept% |
|---:|---:|---:|---:|---:|---:|:--:|---:|---:|
| 60 | 32 | 0.00000 | 0.00000 | **0.00000** | 0.00000 | [0.00000, 0.00000] | 0.0 | 0.0 |
| 75 | 32 | 0.00000 | 0.00000 | **0.00901** | 0.01171 | [0.00000, 0.01135] | 5.7 | 0.0 |
| 90 | 32 | 0.00000 | 0.00000 | **0.00933** | 0.01136 | [0.00000, 0.01038] | 7.0 | 0.0 |
| 110 | 64 | 0.00000 | 0.00827 | **0.00914** | 0.00962 | [0.00881, 0.00937] | 18.0 | 0.0 |
| 130 | 64 | 0.00495 | 0.00859 | **0.00915** | 0.00963 | [0.00889, 0.00948] | 51.0 | 0.0 |
| 160 | 64 | 0.00725 | 0.00872 | **0.00898** | 0.00955 | [0.00881, 0.00924] | 92.7 | 0.0 |
| 200 | 64 | 0.00736 | 0.00824 | **0.00840** | 0.00881 | [0.00830, 0.00858] | 99.7 | 0.0 |
| 250 | 64 | 0.00712 | 0.00771 | **0.00785** | 0.00807 | [0.00778, 0.00797] | 100.0 | 0.0 |
| 300 | 64 | 0.00677 | 0.00729 | **0.00745** | 0.00770 | [0.00735, 0.00754] | 100.0 | 0.0 |
| 350 | 64 | 0.00648 | 0.00700 | **0.00714** | 0.00727 | [0.00704, 0.00721] | 100.0 | 0.0 |
| 406 | 64 | 0.00626 | 0.00675 | **0.00688** | 0.00697 | [0.00681, 0.00695] | 100.0 | 0.0 |
| 500 | 128 | 0.00623 | 0.00647 | **0.00655** | 0.00662 | [0.00650, 0.00657] | 100.0 | 0.0 |
| 700 | 128 | 0.00568 | 0.00587 | **0.00590** | 0.00600 | [0.00589, 0.00597] | 100.0 | 0.0 |
| 900 | 128 | 0.00531 | 0.00547 | **0.00549** | 0.00558 | [0.00548, 0.00553] | 100.0 | 0.0 |

`reach%` = replicates whose proposal survived EM and the floor to arrive at the separation
gates. `accept%` = replicates the full pipeline accepted at bar = 0.025, i.e. the realised
null false-positive rate.

## Reading the table

**The quoted p95 is unconditional, and below n ~ 160 that is not the prefilter's operating
distribution.** At n = 75 only 5.7% of replicates reach the gate; the other 94.3% score
exactly 0 because EM collapses under `minClusterFrac = 30/n`. The p95 of that mixture sits
near the *bottom* of the reached set, not its tail. Conditional on reaching the gate the null
at small n is substantially higher than 0.009 — the sweep cannot resolve where, because it
would need the p99.7 of the unconditional draw. From n = 160 up, reach is >= 93% and the p95
is a genuine conditional quantile.

So the honest statement of the size effect has two regimes:

* **n >= 160** (reach ~ 100%): the null decays smoothly, 0.00898 -> 0.00549, a factor of 1.64
  across a 5.6x span of n. Mild and monotone.
* **n < 160**: EM collapse, not the separation statistic, does the rejecting. The bar is
  close to irrelevant there; `minClusterFrac` is the binding constraint.

**Accept% is 0.0 at every n.** At 0.025 the bar has no false-positive budget anywhere on the
grid, against a null whose worst point is 0.00933. That is a margin of 2.7x at the peak and
4.5x at n = 900.

**Only the min-pair gate ever binds.** Every rejection in every row is `min-pair`, and EM
proposes k = 2 on structureless clouds in 100% of reached replicates (`emK: k2=...`). At
routed k = 2 the min-pair and k-way statistics are computed from identical sufficient
statistics, so they are the same number — visible here as `bindP95` agreeing with `p95` to
five decimals at every row. The joint k-way gate (`sepScore < requiredEps`) was consequently
unreachable at k = 2, and the coarsening loop made it near-unreachable above it: it rejected
nothing in 5682 opportunities across the repo's logs. **It has since been removed**, leaving
min-pair as the splitter's only separation gate. `sepScore` is still computed — it is the
value persisted as `dasguptaDeltaNorm` and the one the within-node diagnostic below reads.

## Consequence for the small-node margin

The `requiredEps` assignment in `TaxonomySplitter.splitSingleNode` doubles the bar when
`targetQueries.size < 2 * minClusterSize`.
That is directionally correct for the *conditional* null documented above — small nodes that
do reach the gate carry noisier proposals. But it is unreachable on the direct path, because
the feasibility check at the top of `splitSingleNode` already requires
`mass >= 2 * minClusterSize`, and `mass <= size`. The only way in is the diffuse-residual
branch that reassigns `targetQueries`, where it becomes the residual subset
(floor `minClusterSize`, so 30..59 is possible); `enableResidualSplitGate` defaults to
`isDag`, so it is live under `DAG_MAX`. It has never fired: `bar=0.0500` appears zero times
in the logs against 5628 occurrences of `bar=0.0250`.

## The within-node null on every accepted split

`gradlew nullBySize --tests "*within-node null on every accepted split*"`, 150 replicates per
site. Observed value = each node's persisted `dasguptaDeltaNorm`, i.e. the `sepScore` the
splitter itself computed at acceptance (validated against the frozen log's `Split '...'
sep=` field: agrees to <5e-4 on all 12 nodes whose labels survived relabelling). Null =
parametric bootstrap on that node's own covariance, driven through the same
`splitSingleNode`. `q` = fraction of the null below the observed value.

Population drift between split time and the frozen tree is negligible: final/split-time n has
median 0.97 and range 0.89-1.02, against a null that moves 1.64x over a 5.6x span of n.

### Read the reach column first

Quantiles are conditional on the replicate reaching the separation gate, because the observed
value is by construction one that reached it. But when reach is low the conditional null is
drawn from the upper tail of a censored distribution, which inflates `nullP50` and deflates
`q`. Reach tracks n almost perfectly (rho = +0.94), and n tracks depth (rho = -0.80), so
**any apparent depth effect is confounded with censoring**. Restricting to sites with
reach >= 90% is what separates them:

| subset | sites | below own p50 | below own p95 | median q |
|---|---:|---:|---:|---:|
| all | 50 | 23 (46%) | 33 (66%) | 0.688 |
| reach >= 90% | 27 | 6 (22%) | 13 (48%) | 0.965 |

The depth gradient looks strong on the full set (depth 1: 8% below p50; depth 3: 71%) and
**disappears once censoring is controlled**: rho(q, depth) = -0.230 over all 50, but -0.071
within the clean subset. Depth is not the variable.

`rho(q, n) = +0.491` does survive into the clean subset, and it is a POWER effect, not a
quality one. The isotropic table above shows the null tightening with n (p95 0.0090 -> 0.0055
from n=160 to n=900), and the within-node null behaves the same way. For a fixed true effect,
a larger node therefore lands further into its own null's tail purely because that null is
narrower. Rising q with n is what constant structure quality predicts, not evidence that
large nodes split better.

The consequence matters for how the failures below are read. Small-node failures are at least
partly **under-powered rather than spurious**. "These splits cannot be distinguished from
elongation" is supported; "these splits are elongation" is not, and the size correlation is
itself evidence for the weaker reading.

### The six splits that fail a clean within-node null

| q | depth | n | k | observed | null p50 | node |
|---:|---:|---:|---:|---:|---:|---|
| 0.000 | 2 | 338 | 2 | 0.02663 | 0.03604 | Classical Mechanics and Kinematic Analysis |
| 0.007 | 1 | 550 | 2 | 0.02797 | 0.03397 | Computer science |
| 0.060 | 2 | 390 | 2 | 0.02896 | 0.03257 | Discrete Quantitative Problem Solving |
| 0.109 | 2 | 261 | 2 | 0.03944 | 0.05691 | Civil Liability and Contractual Dispute Principles |
| 0.138 | 2 | 162 | 2 | 0.02814 | 0.03323 | Organismal Biology and Ecological Adaptations |
| 0.285 | 3 | 116 | 2 | 0.05777 | 0.06340 | Formal Statement Discrimination and Validation |

All are k=2. Psychology (depth 1, n=629, observed 0.02734 against null p50 0.02639, q=0.767)
is the marginal case: it clears its own null median by less than the width of the bar.

### Computer science: the case that shows what the null cannot see

Computer science is the standout failure — depth 1, n=550, 100% reach, q=0.007 — and it is
also the site with the MOST statistical power, so the under-powered reading above does not
rescue it. Its actual partition (verified against the frozen snapshot):

```
Computer science (550)                                            sep=0.02797  q=0.007
├── Foundational Computing Systems and Data Principles (144)       sep=0.06481  q=0.889
│   ├── Foundational Computer Security and Cryptographic Systems (54)
│   ├── Legacy Systems Programming and Debugging Fundamentals (47)
│   └── Data Representation and Information Theory Fundamentals (46)
└── Formal Statement Validation and Logical Discrimination (419)   sep=0.06730  q=1.000
    ├── Formal Statement Discrimination and Validation (116)       sep=0.05777  q=0.285
    │   ├── Advanced Algebraic Group and Ring Theory (47)
    │   └── Formal Logical Statement Discrimination (71)
    ├── Computational Probability and Information Theory (93)      sep=0.03388  q=0.000
    └── Statistical Model Validation and Inference Discrimination (225)  sep=0.09256  q=1.000
        ├── Statistical Inference and Hypothesis Testing (84)
        ├── Time Series Model Diagnostics and Validation (41)
        ├── Logical Statement Veracity Discrimination (49)
        └── Machine Learning Model Theory and Evaluation (55)
```

The split separates systems CS (144: security, legacy programming, data representation) from
statistics, formal logic and mathematics labelled as CS (419) — a branch that contains
"Advanced Algebraic Group and Ring Theory", i.e. pure mathematics, inside the Computer
science domain. That is the corpus contamination finding (the 25.8% reassignment rate, the
label-geometry disagreement) surfacing at the domain level, and it is semantically real.

It is also precisely the configuration the caveat below describes. A genuinely heterogeneous
node has covariance elongated along the very axis that separates its parts, so the bootstrap
reproduces that elongation and the true split scores unremarkably against it. **The split
whose meaning is most obvious is the one this null penalises hardest.** Note also that both
children then split at q = 0.889 and q = 1.000: once the contamination is separated, the
substructure within each part clears its own null comfortably.

### Limit on the interpretation

A node that genuinely contains two clusters has an empirical covariance already **elongated
along the between-cluster axis**. The Gaussian bootstrap reproduces that elongation, so its
best cut scores high and the real split looks unremarkable against it. The within-node null
is therefore inflated by exactly the structure it is being used to test for, and "below own
p50" over-flags: it is necessary evidence of anisotropy-carving, not sufficient. Separating
the two would need a null built on the covariance with the candidate split direction removed,
or a direct unimodality test (dip, or mixture BIC). Not done here.

This is not an abstract concession — Computer science above is a worked instance of it, with
the semantics checkable by reading the child labels.

So the defensible claim is bounded: **a named minority of splits (6 of 27 with clean nulls,
22%) cannot be distinguished from a cut through their own node's elongation, and about half
(13 of 27) fall inside the range their own null routinely produces.** That is a real
limitation with a list attached. It is not a single mechanism explaining the taxonomy's
redundancy, non-recurrence and small fringe, because 78% of clean-null splits do clear their
own null median, and one of the six is demonstrably a real distinction the null cannot see.

### Where the bar actually sits

Against the within-node p50 values measured here (0.033-0.063 across the clean sites), the
bar at 0.025 is **permissive relative to that null** — it admits partitions that node-level
resampling produces routinely. Against the isotropic null (0.0055-0.0093) it is conservative
by 2.7x to 4.5x. Both statements are true at once and neither is the whole picture: 78% of
clean-reach splits clear their own null median regardless of where the bar sits, so the
permissiveness only decides the marginal cases — which are precisely the six named above.

### Per-node provenance export

The harness writes two CSVs so downstream analysis can report the distribution rather than
repeat the caveat:

* `docs/data/within_node_null_splits.csv` — one row per accepted split: node id, label,
  depth, n, k, observed separation, null p50/p95, q, reach%.
* `docs/data/within_node_null_leaves.csv` — one row per leaf, carrying both the null quantile
  of the split that FOUNDED it (its tree parent's) and `min_ancestor_q_clean`, the worst
  quantile anywhere in its lineage among ancestors whose null was not censored.

The leaf file is the useful one: it gives every cell a provenance flag ("founded by a split
at q = 0.97" against "q = 0.007"), which lets the low-q cells be joined per node against the
fringe-size, leaderboard-redundancy and cross-seed-recurrence findings, instead of a shared
cause being inferred from three separate aggregates.

**The lineage column is the one to report, because the founding split alone understates
exposure by about 3x.** Of 88 leaves holding 9186 queries:

| flagged by | leaves | queries | share of leaf-held corpus |
|---|---:|---:|---:|
| founding split below its own null median (clean reach) | 7 | 845 | 9.2% |
| **any clean ancestor below its null median** | **25** | **1807** | **19.7%** |
| any clean ancestor below its null 5th percentile | 13 | 944 | 10.3% |

Computer science is the whole reason for the gap: its q = 0.007 split produced two internal
nodes, so **not one of the nine leaves beneath it is flagged by founding split**, yet all
nine sit under it. Same pattern for Discrete Quantitative Problem Solving (q = 0.060, seven
leaves) and Organismal Biology (q = 0.138, two leaves).

Read with the caveat above, this is an upper bound on the concern rather than a count of
defective cells — Computer science alone contributes nine of the twenty-five leaves, and its
split is the one this null most clearly gets wrong.

Both are computed offline from the frozen snapshot. Doing it inline would cost
`reps x splitSingleNode` per proposing node and would change the freeze; this changes nothing
and needs no re-run.

## Reproducing

```
gradlew nullBySize -PnullReps=300 --tests "*SeparationNullBySizeTest*production splitter*"
```

Arms B-E of the same test cover the mcs=20 floor (the only way to reach n=40), an exact vMF
generator, a concentration sweep, and the Philosophy fidelity replay.

---

## CURRENT (2026-09-07, frozen mcs=55 artifact): within-node null re-derived

**This section supersedes, as to values, everything the scope note at the top voids**: the
50-site within-node table, its q values, the six named marginal splits, the leaf-lineage
exposure numbers and the `docs/data/within_node_null_*.csv` exports, all of which were
measured on the pre-`c381211` 88-leaf mcs=30 tree. The isotropic table above remains
current and is not touched. The METHOD is unchanged and is restated exactly below.

Measured by `gradlew withinNull` (`SeparationNullBySizeTest`, arm
"withinNull - anisotropy-preserving null per frozen depth-1 anchor") against the frozen
artifact **snapshot `20260727_042523_Headless_Run_Auto_ge`** (154 nodes / 87 leaves /
14 depth-1 anchors, `minClusterSize = 55`, `proposalSeparationBar = 0.025`,
`freeze_mcs55.toml`), read from the tracked `snapshots_frozen.db` extract. Embeddings are
served strictly from `embeddings_cache.db` (read-only, hard-fail on any cache miss; coverage
was 8299/8299 anchor-region queryIds, no duplicates).

**Null model (the anisotropy-preserving generator, same as the voided run):** for each
depth-1 anchor, fit the anchor's own 256-slice mean `mu` and empirical covariance, then draw
`x = normalize(mu + C^T g)` where `C`'s rows are the centered observations scaled by
`1/sqrt(m)` and `g ~ N(0, I_m)`. Draws are Gaussian moment-matched to the node — every
per-principal-component variance preserved, every discrete sub-cluster destroyed — then
projected to the sphere. "Texture but no sub-topics." **Statistic:** each replicate cloud
(same n as the anchor) is driven through the production `TaxonomySplitter.splitSingleNode`
at the frozen config (`minClusterSize = 55`, bar = 0.025) and `node.dasguptaDeltaNorm` is
recorded uncensored, exactly as the isotropic arms record it. `acceptanceZ` stays 0.0
because the z-gate lives in `TaxonomyOperations`' edit acceptance, outside
`splitSingleNode`; it cannot censor this statistic. 300 replicates per anchor, deterministic
seeds keyed on anchor id and replicate index.

| anchor | n | p50 | p90 | **p95** | p99 | p95 95% CI | reach% | accept% |
|---|---:|---:|---:|---:|---:|:--:|---:|---:|
| Chemistry | 934 | 0.04349 | 0.04836 | **0.06627** | 0.07056 | [0.06319, 0.06816] | 100.0 | 100.0 |
| Physics | 873 | 0.03315 | 0.03523 | **0.03555** | 0.03627 | [0.03539, 0.03604] | 100.0 | 100.0 |
| Math | 870 | 0.03659 | 0.03871 | **0.03943** | 0.04060 | [0.03898, 0.04002] | 100.0 | 100.0 |
| Law | 738 | 0.05073 | 0.07319 | **0.07531** | 0.07816 | [0.07393, 0.07751] | 100.0 | 100.0 |
| Psychology | 624 | 0.02613 | 0.02802 | **0.02899** | 0.02970 | [0.02835, 0.02931] | 100.0 | 81.7 |
| Business | 606 | 0.03486 | 0.03760 | **0.03856** | 0.04167 | [0.03794, 0.03988] | 100.0 | 100.0 |
| Engineering | 604 | 0.06407 | 0.06832 | **0.06989** | 0.07272 | [0.06902, 0.07188] | 100.0 | 100.0 |
| Biology | 571 | 0.03252 | 0.03524 | **0.03578** | 0.03702 | [0.03556, 0.03648] | 100.0 | 100.0 |
| Economics | 568 | 0.03493 | 0.03749 | **0.03844** | 0.04119 | [0.03796, 0.03975] | 100.0 | 100.0 |
| Computer science | 549 | 0.03215 | 0.03504 | **0.03565** | 0.03680 | [0.03536, 0.03627] | 100.0 | 99.7 |
| Health | 525 | 0.03015 | 0.03291 | **0.03365** | 0.03466 | [0.03331, 0.03419] | 100.0 | 99.7 |
| Other | 511 | 0.03006 | 0.03228 | **0.03347** | 0.03468 | [0.03258, 0.03388] | 100.0 | 99.7 |
| Philosophy | 402 | 0.04027 | 0.04467 | **0.04954** | 0.06347 | [0.04539, 0.06163] | 100.0 | 100.0 |
| History | 320 | 0.05140 | 0.06984 | **0.07344** | 0.07657 | [0.07128, 0.07495] | 100.0 | 100.0 |

Reach is 100% at every anchor (n >= 320 is far above the EM-collapse regime), so
unconditional and conditional quantiles coincide and the censoring caveat that dominated the
voided mcs=30 reading does not arise here.

### Where the frozen bar sits

The within-node p95 band is **0.02899 (Psychology) .. 0.07531 (Law)**. The frozen bar
0.025 sits **below the entire band** — below even the lowest anchor's p95, and below every
anchor's p50 except Psychology's by a wide margin. Both earlier statements therefore
sharpen into one: against the isotropic null (p95 0.0055-0.0093) the bar is conservative by
2.7-4.5x; against every anchor's own anisotropy-preserving null it is permissive,
full stop. The `accept%` column makes it operational: the FULL pipeline accepts
99.7-100% of structureless-but-anisotropic clouds at 12 of 14 anchors (81.7% at
Psychology). **The bar controls the isotropic false-positive rate and provides essentially
no control against anisotropy-carving.** Whatever distinguishes real sub-topics from
elongation in the frozen tree, it is not the separation bar.

### Accepted splits against their anchor's null

Every accepted split of the frozen tree (66 sites with k >= 2 and persisted
`dasguptaDeltaNorm > 0`) is scored against its depth-1 anchor's null:
q = fraction of ALL 300 null replicates >= the split's persisted separation.
Full listing: `docs/data/within_null_frozen_splits.csv`.

* **Depth-1 splits (exactly matched null — same population, same n, same covariance):
  5/14 (36%) clear their own null p95** (Chemistry q=0.000, Biology q=0.000,
  Engineering q=0.007, Math q=0.010, Business q=0.043); 11/14 (79%) are above their own
  null p50; median q = 0.183. The three below their own p50: Economics (q=0.963),
  Health (q=0.787), and Philosophy (q=1.000) — the Philosophy split the mcs=55 run
  accepted (sep 0.0319) is one its own elongation null beats in every replicate.
* **Deeper splits (anchor-null approximation): 18/52 (35%) clear their anchor's p95;
  all accepted splits together: 23/66 (35%).** The approximation's direction is known:
  the null narrows with n, so the larger-n anchor null is anti-conservative for smaller
  descendant sites — their own within-node p95 would be higher, and 35% is an upper bound
  on the clear rate under matched site-level nulls.

### Interpretation limit (unchanged from the voided section, still binding)

A genuinely heterogeneous node has covariance already elongated along the between-cluster
axis; the bootstrap reproduces that elongation, so the true split scores unremarkably
against it. Low q is necessary evidence of anisotropy-carving, not sufficient — and high
`accept%` is a statement about the bar, not about any individual split's truth. The mcs=30
run's worked example (Computer science) showed exactly this configuration; at mcs=55 the
Computer science depth-1 split sits at q=0.273 with both its children's subtrees clearing
their anchor p95 at deeper levels (`Probabilistic and Algebraic Reasoning in CS` q=0.003,
`Statistical Methods in Econometrics and Simulation` q=0.003).

### Comparison to the voided mcs=30 values

The voided within-node band (p95 0.068-0.130, p50 0.033-0.063, measured per-site on the
superseded 88-leaf tree) is replaced by the anchor-level band above (p95 0.029-0.075, p50
0.026-0.064). The direction of the conclusion survives the re-derivation: the bar is
permissive relative to the within-node null on the frozen artifact too, and by a wider
operational margin than the old numbers suggested (accept% ~100% here; the voided run did
not report an accept rate against its null).

### Reproducing

```
gradlew withinNull -PnullReps=300
```

Reads `snapshots_frozen.db` (tracked; falls back to the full local `snapshots.db`) and
`embeddings_cache.db`, both opened read-only; refuses to run on any snapshot other than the
one passed via `-DsnapshotId` (default: the frozen id). Writes
`docs/data/within_null_frozen_anchors.csv` and `docs/data/within_null_frozen_splits.csv`.
Site-level (rather than anchor-level) nulls remain available as the stage-2 harness above
run with `-DsnapshotId=20260727_042523_Headless_Run_Auto_ge`; not done here.

---

## SITE-LEVEL (2026-09-08): per-site + deflated nulls, certification by pruning (P2)

Measured by `gradlew siteNull` (`SeparationNullBySizeTest`, arm "siteNull - site-level and
deflated nulls on every accepted split of the frozen artifact"), adjudicating proposal P2
against the criteria frozen in `docs/v2_validation_plan.md` before the run. Same frozen
artifact (`20260727_042523_Headless_Run_Auto_ge`, mcs=55, bar=0.025), same
anisotropy-preserving generator and production-`splitSingleNode` statistic as the
anchor-level section above, with the anchor approximation removed: each of the **66
accepted split sites** is scored against a null fitted to **its own population** (the
site's region queryIds, 256-slice, cache-only with hard-fail on any miss), 300 replicates
per site per arm, deterministic seeds keyed on site id and replicate index. Guards, both
recorded as feasibility flags rather than fabricated q's: NULL-INFEASIBLE
(n < 2*minClusterSize = 110 — cannot be driven through the splitter) and DEGENERATE
(< 20 replicates reached the separation gate). **Neither fired**: all 66 sites have
n >= 126, reach is >= 91% everywhere and 100% at 59/66 sites. Seed-independence check:
the 14 depth-1 sites re-derive the anchor arm's q values under fully independent seeds to
within 0.033 (e.g. CS 0.240 vs 0.273, Economics 0.990 vs 0.963).

**Deflated variant** (the natural-projection construction, labelled as such): the observed
split's between-child-centroid subspace — frozen child-region centroids, Gram-Schmidt,
<= k-1 dims, exactly the between-centroid direction at k=2 — is projected out of the
centered observations before sampling; the mean is kept (a mean offset creates no
bimodality). This removes precisely the elongation that a genuinely two-cluster node bakes
into its own covariance, i.e. the circularity named in the interpretation-limit sections
above: the plain within-node null is inflated by the structure under test, the deflated
null is not, so it is the statistic intended to separate elongated texture from real
heterogeneity the elongated null hides.

Full table: `docs/data/site_null_frozen.csv` (one row per site: observed sep, both nulls'
p50/p95, q_site, q_deflated, reach/accept rates, cert flags, trunk membership,
feasibility). Certification rule, fixed in the harness: observed >= the null's
unconditional p95.

### Headline numbers

* **Site-level certification: 6/66 (9%).** Chemistry (q=0.000), Biology (0.000),
  Math (0.013), Engineering (0.013), Business (0.027) at depth 1, plus one deep site,
  Elementary Quantitative Reasoning and Symbolic Logic (depth 4, k=3, q=0.047). The
  anchor-level readout (23/66 = 35% clear) was registered as an upper bound because the
  anchor null narrows with n; matched site-level nulls collapse it fourfold. The
  direction was predicted; the magnitude ends the trunk tier as designed.
* **Deflated certification: 24/66 (36%).** The deflated null is much narrower (Chemistry
  p95 0.0667 -> 0.0295; Physics 0.0358 -> 0.0311) — but the production bar accepts its
  clouds at ~100% too, so deflation reorders sites rather than rescuing the bar.
* **Certified trunk (maximal all-certified prefix): 5 sites** — the depth-1 splits of
  **Chemistry, Math, Business, Engineering, Biology**. Nothing below depth 1 survives the
  prefix rule: the one deep certified site sits under two uncertified Math splits
  (q=0.963 and q=1.000) and drops out.

### Registered checks (frozen before the run; verdicts as coded)

**(a) Power check — FAIL.** Required: the deflated null certifies the CS contamination
split while leaving Philosophy's two sites uncertified. Observed: CS depth-1 certifies
(q_defl = 0.043) and 'Core Philosophical Concepts and Theorists' stays uncertified
(q_defl = 0.257) — but **Philosophy depth-1 also certifies, at exactly q_defl = 0.050**
(observed 0.03188 against a deflated p95 of 0.03162). The honest read is not "one
replicate away from PASS": at 300 reps the binomial SE of a q near 0.05 is ~0.013, so
CS (0.043) and Philosophy (0.050) are statistically indistinguishable. The deflated null
as constructed does **not** have the power to separate the CS-contamination configuration
from Philosophy at the domain level, and the check fails substantively, not numerically.

**(b) Trunk viability — FAIL.** Required: >= 15 sites certified at site-level p95,
including Chemistry and Biology depth-1. Observed: Chemistry and Biology both certify at
q=0.000, but the count is 6 — P2's own falsifier ("site-level nulls certify < 15 splits:
trunk tier too thin; strata absorb its role") fires. The plan's trunk-drift clause
(<= 0.5pp) is moot at this count and was not measured; this harness is offline geometry
with no routing arm.

### Consequences

P2-as-registered is falsified the same way P1 was: the mechanism works (the harness runs,
the nulls are honest, the trunk is a well-defined view) but the certified object is far
smaller than the proposal predicted — a 5-split trunk containing 19 nodes' worth of
structure, not the ~30-55 leaves P2 projected. Two downstream effects: (1) P3's candidate
twig set ("every leaf whose parent is inside the certified trunk") must be re-derived
against this 5-site trunk or P3's gate redesigned — with the trunk this thin, the
functional tier starts essentially at depth 2; (2) the strata (P5) inherit the
measurement role the trunk tier was meant to carry, exactly as the falsifier clause
anticipated. The deflated-null idea survives as a diagnostic (its per-site q's are in the
CSV) but is not, at 300 reps and this construction, the CS-vs-Philosophy discriminator
the plan required; dip-test / mixture-BIC alternatives from the proposal text remain
unexplored and would need their own registration.

### Reproducing

```
gradlew siteNull -PnullReps=300
```

Reads `snapshots_frozen.db` (tracked) and `embeddings_cache.db` read-only, hard-fails on
cache misses, refuses any snapshot but the one passed via `-DsnapshotId` (default: the
frozen id). Writes `docs/data/site_null_frozen.csv` and prints the registered-check
verdicts and trunk membership. Runtime ~9 min at 300 reps (66 sites x 2 arms).
