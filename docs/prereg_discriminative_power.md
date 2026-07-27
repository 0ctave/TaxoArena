# Pre-registration: discriminative power, 14 / 88 / 152 cells

Written **before** the analysis is run. Recorded because two predictions in this
project were stated in conversation, measured afterwards, and then argued about —
a prediction only constrains interpretation if it is fixed in advance.

## Question

Does a finer partition carry more evaluative information, or slice the same
information thinner? This decides which tree to freeze, and it is not answered
by J.

## Why J cannot answer it

J is an in-sample geometric criterion. Evaluative usefulness requires cells that
rank models *differently* from one another. These are distinct properties, and
they have already disagreed twice:

* `proposalSeparationBar` 0.020 vs 0.025 — J favoured 0.020, held-out Top-1
  favoured 0.025. Resolved on convergence, not on J.
* The router fix raised J 20.4% (0.238987 -> 0.287671) while median per-leaf
  reliability fell 0.842 -> 0.745.

## Design

* Per-leaf, per-model accuracy from `eval_results.is_correct`, joined
  `queries.raw_text` -> `eval_results.question_text` (exact, 11769/11769 = 100%).
* Roster: the 8 arena models. All 8 are present in every cell of both trees
  (measured), so coverage does not confound.
* Restrict to reserved queries (3437 flagged texts).
* Spearman rho between cells, over BOTH sibling pairs and all pairs — all-pairs
  is the common population across granularities and matches the original
  redundancy analysis.
* Granularities: 14 domains / 88 leaves (frozen) / 152 leaves (router-fixed).

## Reporting rules, fixed in advance

* **Observed rho is primary.** Disattenuated is reported separately and second.
  Disattenuation divides by sqrt(r_A r_B), so it inflates whatever the observed
  value is — a higher disattenuated median on the finer tree is partly
  guaranteed by the correction rather than measured. Leading with it would
  repeat the CV-vs-additive-effect error from the z-gate sweep.
* At r = 0.745 disattenuated values clip past 1.0, so "fraction >= 0.95" measures
  the correction, not the taxonomy. Report it, but not as the headline.
* Report **n pairs and IQR** on the same line as every median. The three
  granularities give roughly 91 / 3,800 / 11,500 pairs; three medians presented
  bare will be read as equally precise.

## The three outcomes, named in advance

| observed sibling rho at 152 vs 88 | reading | implication |
|---|---|---|
| **falls** | finer cells rank models differently — genuinely more signal | freeze the finer tree |
| **flat** | same signal, thinner cells | freeze the coarser tree; finer buys nothing |
| **rises** | finer cells rank models MORE alike — subdividing axes irrelevant to model performance | strongest case for the coarser tree |

The third is not implausible: the splits that the router fix unlocked are the
marginal ones, and marginal geometric structure need not correspond to any axis
along which models differ.

## What is NOT being claimed

This measures evaluative *redundancy* between cells, not arena accuracy. It does
not settle RQ1, which is computed on the pooled leaderboard and is nearly
insensitive to cell count.

---

# RESULTS

Run after the above was fixed. Join exact (11769/11769), all 8 roster models
present in every cell of every tree, 0 cells dropped at any granularity.

| tree | cells | pairs | observed rho | IQR | disatt | global-order-removed |
|---|---:|---:|---:|:--:|---:|---:|
| 14 domains (frozen) | 14 | 91 | 0.929 | [0.905, 0.976] | 0.942 | -0.119 |
| 88 leaves (frozen, biased router) | 88 | 3828 | 0.922 | [0.857, 0.970] | 1.015 | -0.024 |
| 87 leaves (mcs=55, correct router) | 87 | 3741 | **0.922** | [0.881, 0.969] | 1.002 | -0.024 |
| 152 leaves (mcs=30, correct router) | 152 | 11476 | 0.905 | [0.834, 0.952] | 1.039 | -0.024 |

## Outcome: BRANCH 2 — "same signal, thinner"

Observed rho is flat across an 11x change in granularity (0.929 -> 0.922 ->
0.905), with overlapping IQRs throughout. Finer cells do not resolve more
evaluative signal.

The disattenuated column moves in the OPPOSITE direction (0.942 -> 1.015 ->
1.039) and clips past 1.0. Reading it as primary would have given the opposite
conclusion from the correction's arithmetic rather than from the data. This is
why observed-primary was fixed in advance.

## Unplanned second control: the router

87 leaves (correct router, J 0.253129) and 88 leaves (biased router, J 0.229418)
give observed rho = 0.922 identically. So a routing correction worth +10.3% J
produces ZERO change in discriminative power at matched granularity. Flatness
holds across routers as well as across granularities.

## The stronger finding: it is nearly all the global ordering

Centering each model's accuracy by its global mean before correlating removes
the global capability ordering. The residual median correlation is ~0 at every
granularity (-0.119 / -0.024 / -0.024 / -0.024), with an IQR straddling zero
symmetrically.

Roster spread is 54.1 points (claude-3-5-sonnet 0.775 -> Llama-2-13b 0.234), so
rho ~ 0.92 was largely measuring "gpt-4o beats Llama-2-13b in every cell".

**Cell identity contributes essentially nothing to model ranking beyond global
capability ordering** — for this corpus, this 8-model roster, at any granularity
from 14 to 152, under either router.

Scope: with a capability-diverse roster. A roster spanning ~10 accuracy points
is untested and is the version of RQ2 that could still come out positive.
Caution: at 8 models a Spearman has little resolution, so "~0" means
"indistinguishable from zero", not "measured to be zero".

## What this licenses

Granularity being evaluatively flat is what makes cell count free to choose on
budget grounds. Without it, minClusterSize = 55 would be a compromise; with it,
it is a design choice at no evaluative cost, and per-cell reliability (r ~ 0.83)
is a consequence rather than a target.

## Ceiling caveat — permanent

Measured on each cell's own constituent (training) queries, not on routed
held-out queries, and on ground-truth accuracy, not judge verdicts. It bounds
what the arena CAN discover; it does not predict what the arena WILL produce.
The arena can show less discrimination than this (judge noise), not more. Only
running the arena resolves it.

## The residual is indistinguishable from the centering null

Subtracting each model's across-cell mean forces its residuals to sum to zero
across cells, which induces a negative correlation between any two cells of
about -1/(C-1). The observed residuals must be read against that, not against 0:

| cells | mechanical null -1/(C-1) | observed | ratio |
|---:|---:|---:|---:|
| 14 | -0.0769 | -0.119 | 1.5x |
| 88 | -0.0115 | -0.024 | 2.1x |
| 87 | -0.0116 | -0.024 | 2.1x |
| 152 | -0.0066 | -0.024 | 3.6x |

All within 1.5-3.6x of the artifact and all ~0 on any practical scale. The
defensible claim is "indistinguishable from the centering null", not "zero" —
same conclusion, but it survives a reviewer computing the null themselves.

## Scope the claim by POWER, not only by roster

A single model's per-cell accuracy has SE ~ sqrt(0.25/q):

| granularity | queries/cell | SE |
|---|---:|---:|
| 14 domains | 590 | 2.1 pp |
| 88 / 87 leaves | 74 | 5.8 pp |
| 152 leaves | 52 | 6.9 pp |

So a null residual is consistent with two different worlds — no cell-specific
ranking signal, or one smaller than roughly 6 pp at leaf granularity. This
analysis cannot separate them.

The 14-domain measurement is the stronger evidence precisely because it is the
LOW-NOISE condition (2.1 pp) and its residual is also at null.

**Scoped claim: no cell-specific ranking structure detectable above ~2 pp at
domain granularity or ~6 pp at leaf granularity, for a roster spanning 54
accuracy points.**

## Consequence for the thesis framing

This is a negative result about the PREMISE, not about the comparison. If cell
identity contributes nothing beyond global capability ordering, then no
partition — adapted, canonical or otherwise — improves ranking fidelity on this
corpus with this roster.

The contribution is therefore the method, the construction guarantees, the
transferable findings, and a measured, pre-registered negative result about
geometry-adapted evaluation partitioning. Pre-registering before the arena runs
is what makes the negative readable as a finding rather than a failure.

Obvious follow-up, costing nothing to name: a roster clustered within ~10
accuracy points might give a different answer.

## Where this sits in the argument

This measures **link 3** of the causal chain `coherent cells -> specific rubrics ->
better judgments -> ranking closer to ground truth`, and specifically its premise: do
cells have different *true* rankings. They do not, on this corpus with this roster.

It says **nothing about judge quality**, which is the claim the system actually makes.
Do not let the flat result be read as "the taxonomy does not help the arena" — it is a
finding about MMLU-Pro's saturation for a 54-point-spread roster. The reframed question,
the other two links, and the state of evidence on each are in
[`reframed-argument.md`](reframed-argument.md).
