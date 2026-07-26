# Separation null as a function of node population

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
five decimals at every row. The k-way gate (`sepScore < requiredEps`) is consequently
unreachable at k = 2, and the coarsening loop makes it near-unreachable above it: it has
rejected nothing in 5682 opportunities across the repo's logs.

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
within the clean subset. rho(q, n) = +0.491 survives. Depth is not the variable; node size
is, and most of that is the censoring.

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

### Limit on the interpretation

A node that genuinely contains two clusters has an empirical covariance already **elongated
along the between-cluster axis**. The Gaussian bootstrap reproduces that elongation, so its
best cut scores high and the real split looks unremarkable against it. The within-node null
is therefore inflated by exactly the structure it is being used to test for, and "below own
p50" over-flags: it is necessary evidence of anisotropy-carving, not sufficient. Separating
the two would need a null built on the covariance with the candidate split direction removed,
or a direct unimodality test (dip, or mixture BIC). Not done here.

So the defensible claim is bounded: **a named minority of splits (6 of 27 with clean nulls,
22%) cannot be distinguished from a cut through their own node's elongation, and about half
(13 of 27) fall inside the range their own null routinely produces.** That is a real
limitation with a list attached. It is not a single mechanism explaining the taxonomy's
redundancy, non-recurrence and small fringe, because 78% of clean-null splits do clear their
own null median.

## Reproducing

```
gradlew nullBySize -PnullReps=300 --tests "*SeparationNullBySizeTest*production splitter*"
```

Arms B-E of the same test cover the mcs=20 floor (the only way to reach n=40), an exact vMF
generator, a concentration sweep, and the Philosophy fidelity replay.
