# The tree construction, restated — and a plan to make the report say it

Companion to `docs/construction-doc-audit.md` (what the report currently says
against what the code does) and `docs/construction-open-items.md` (what was
closed by computation and what still needs a run).

This document does three things. Part I restates the construction as the thing
that actually runs, with no account of what it replaced. Part II and Part III
state what that design buys and what it costs, each backed by a number derived
in the open-items doc. Part IV is a file-by-file edit plan for `report/`.

Scope is **tree construction only**. The arena is out of scope except where a
construction parameter feeds it. An arena run is in progress; nothing in Part
IV requires stopping it, and nothing in Parts I–III requires a new run.

The frozen artifact throughout: snapshot `20260727_042523_Headless_Run_Auto_ge`,
`experiment_configs/freeze_mcs55.toml`, seed 42, commit `c381211`.
154 nodes, 87 leaves, depth 6, mass 8299.000, J = 0.253129.

---

# Part I — The construction, as it runs

## The object

An **anchored single-parent tree** over the 14 MMLU-Pro categories. Every node
carries a von Mises–Fisher direction and concentration fitted on a fixed
256-dimensional slice of the corpus embedding. Every leaf carries a judging
rubric. Every query in the construction pool holds soft membership in one or
more leaves and a designated primary leaf.

## Five commitments

Everything else follows from these. Stated as commitments rather than as steps,
because each one is a decision a reviewer can disagree with, and each one has
a measured consequence.

### C1 — The top level is fixed; membership is not

The 14 category labels seed 14 depth-1 anchors. Depth ≤ 1 is exempt from every
destructive topology operation, so anchors are never split, fused, dissolved or
pruned. Queries are not fixed: routing moves them across anchors freely from
iteration 2 onward, which is what makes the induced *adapted* partition differ
from the editorial *canonical* one.

The point of the exemption is reporting, not geometry. Because every leaf is
nested under exactly one anchor, a per-leaf result aggregates to a per-domain
result that can be set against MMLU-Pro's own published category scores. In the
frozen artifact the 14 anchors partition the 87 leaves exactly, no leaf shared,
counts 11/10/8/8/7/6/6/6/6/5/4/4/3/3.

### C2 — One representation width, at every depth

The embedding is a 4096-dimensional Qwen3-Embedding vector. The construction
uses its first 256 coordinates, re-normalised to unit length. Same width at
every depth, for fitting, routing, separation scoring and acceptance.

Matryoshka Representation Learning is what licenses the truncation: every
prefix is trained to be a usable embedding on its own. Re-normalisation after
slicing is mandatory, because MRL preserves meaning and not norm.

Splits are *proposed* in a smaller principal-component subspace — 32, 64 or 128
dimensions by target size — and every gate is *evaluated* at 256. The subspace
shapes candidates and never decides.

### C3 — Every structural edit is judged in units of its own uncertainty

One global objective, J: the chance-corrected separation score of the whole
corpus, one cell per leaf. Chance-corrected against uniformly random
relabelling into clusters of the same sizes, so the score cannot be produced by
the size profile alone.

A candidate edit is applied tentatively, the whole corpus is re-routed, J is
recomputed, and the edit commits iff

> **ΔJ > max(τ, z*·SE_paired(ΔJ))** when SE_paired > 0, with z* = 2.0 and
> τ = 10⁻⁶;
> **ΔV < 0** when SE_paired = 0.

SE_paired is a paired Dirichlet bootstrap at 200 replicates over only the
queries whose cell assignment changed, so both sides share a corpus draw and
the shared variance cancels. SE = 0 identifies a pure structural edit that
moves no query — a pass-through dissolution — for which ΔJ is exactly 0 and z
is undefined; the size test lets those commit. The two branches are
alternatives, not layers: with SE > 0 there is no lexicographic tie-break, so a
J-neutral simplification cannot commit.

The τ floor exists for the termination bound. Every accepted edit raises J by
at least τ and J is bounded above by 1, so at most (1 − J₀)/τ edits can ever
commit. On the frozen run τ never bound — the smallest operative threshold
across 173 rejections was 8.83e-05, 88× τ — so the rule reduced in practice to
ΔJ > 2·SE everywhere.

**The same gate applies to every operator.** `tryProposal` is the single path
for splits, fusions, starved-leaf handling and dissolutions.

### C4 — A split must survive routing, not merely clustering

Growth proposes a split of a leaf by vMF-EM at forced k, ascending k = 2, 3, 4,
first acceptance wins. The candidate is then made to earn its place three times
over:

1. **Re-route.** Children are refit and every query is re-assigned by the same
   level-local vMF posterior the router uses. What is scored is the routed
   partition, never the EM partition.
2. **Routed sustainability.** If any routed child falls below
   `minClusterSize`, the proposal dies.
3. **Min-pairwise separation.** Every routed child *pair* must clear
   ε_sep = 0.025 on the chance-corrected statistic — the same statistic, at the
   same bar, that the sibling merger uses to *destroy* a pair.

Point 3 is the load-bearing one and the reason it is pairwise rather than
k-way: creation and destruction now read one statistic at one bar, so their
acceptance regions are disjoint and nothing creatable is immediately
destroyable. A joint k-way score of 0.06 can hide a pair at 0.015, and that
pair is exactly what the merger fuses next iteration — the split/fuse limit
cycle.

Eligibility to be considered at all: the node is a leaf, its mass **and** its
effective sample size mass²/Σw² both reach 2·`minClusterSize`, and its depth is
below D_max.

### C5 — The frozen artifact is certified, not assumed

The loop stops when either criterion holds for five consecutive iterations:
J stationarity (|ΔJ_edits| ≤ τ **and** |ΔJ_route| ≤ τ) or graph-edit-distance
quiescence (GED = 0, with a floor of max(⌊0.8·anchors⌋, 5) = 11 iterations).

Stopping is not the guarantee. After stopping, a **fixed-point certificate**
asks whether one further application of the construction operator would change
the artifact, on four terms: the edit-phase change in J, the re-routing change
in J, the maximum per-node 1 − cos(μ), and the maximum per-node relative change
in κ. The first two test against τ; the two parameter terms test against a
separate tolerance of 10⁻⁶ on θ, because τ bounds a change in J and these bound
a change in the parameters that produce it.

The θ terms are the reason the certificate exists. Held-out queries route
through θ, so a certificate over structure and objective alone would not cover
the object being frozen.

Frozen artifact: iteration 10, editsΔ = 0, trickleΔ = −3.33e-16,
max 1−cos(μ) = 1.11e-16, max relative Δκ = 4.25e-13, **CERTIFIED true**.

## Routing, once

At each internal node, three separate decisions:

- **Descend or hold.** Descend iff `max_c ⟨μ_c, x⟩ ≥ (r̄_v − m)·⟨μ_v, x⟩`,
  where r̄_v = ‖Σ_c ω_c μ̂_c‖ is the children's mass-weighted resultant length
  and m = `descentMargin` = 0.12. The bound is Jensen-derived; the margin is
  slack below it. A query that fails is held at the node. **At m = 0.12 this
  never happens: 0 of 8299 construction queries and 0.00% of held-out queries
  are held.**
- **Which siblings compete.** Additive cosine beam: child i stays iff
  ⟨μ_i, x⟩ ≥ max_j⟨μ_j, x⟩ − γ, γ = 0.20. Transition probabilities are
  renormalised over the beam.
- **Which destinations count.** Memberships are self-normalised over reached
  leaves and floored at 0.25; if nothing clears the floor, the single best
  leaf is taken. The primary leaf is the argmax, a bookkeeping convention.

Scoring inside a level uses a **shared concentration** — the mean of the
children's κ — so siblings are compared on direction alone. Per-child κ would
bias the comparison, because the small-sample shrinkage (n−1)/(n+d−2) makes
nodes with more mass systematically sharper.

Construction-time membership is unbounded; evaluation-time membership is capped
at 5. Measured multi-membership in the frozen artifact: `avgMatchCount` 1.101.

## Node model, once

μ̂ is the normalised weighted sample mean. κ̂ is the Banerjee closed form
r̄(d − r̄²)/(1 − r̄²), refined by Newton–Raphson on A_d(κ) = r̄ (two or three
steps at d = 256; the five-step cap is never reached), multiplied by the
Hornik–Grün shrinkage (n−1)/(n+d−2), then blended toward the parent's κ by a
ramp α(ρ) = 0 for ρ ≤ 2, (ρ−2)/8 for 2 < ρ ≤ 10, 1 for ρ > 10, with ρ = d/n.
At the median leaf (n = 88, d = 256): ρ = 2.91, α = 0.114.

A Normal-inverse-Wishart posterior is fitted alongside as a regulariser. It is
not conjugate to vMF, participates in neither stopping criterion, and its only
consumer is the leaf log-semantic-volume diagnostic.

## Parameters that decide something

| symbol | value | what it decides |
|---|---|---|
| d | 256 | representation width, everywhere |
| n_min | 55 | routed child floor at split time |
| ε_sep | 0.025 | min-pairwise separation bar |
| z* | 2.0 | acceptance gate, in SE units |
| τ | 10⁻⁶ | acceptance floor; termination bound |
| maxK | 4 | ascending-k cap |
| m | 0.12 | descent-gate slack |
| γ | 0.20 | sibling beam |
| membership floor | 0.25 | which leaves count |
| D_max | 8 | depth cap (not binding; artifact reaches 6) |
| numIterations | 50 | budget (not binding; artifact stops at 10) |

---

# Part II — What this design buys

Each claim below is backed by a number derived in
`docs/construction-open-items.md`. None requires a new run.

**A1. The acceptance threshold moves with the edit's noise, and it has to.**
Across the 69 accepted edits that move queries, SE(ΔJ) spans **13.4×**
(3.27e-05 to 4.38e-04). No single fixed ΔJ threshold is correct at both ends of
that range. The gate blocked **8 distinct split sites whose ΔJ exceeded τ**,
four of them at z < 1, the worst at **z = 0.089** (ΔJ = 9.46e-06 against
SE = 1.06e-04). A τ-only rule commits all eight.

**A2. Creation and destruction read one statistic at one bar.** The min-pair
gate is the binding separation test — **129 of 373 proposal rows** are min-pair
rejections, against zero for the joint k-way score. Because the merger fuses on
the same statistic at the same bar, the split/fuse limit cycle that a joint
score permits cannot occur.

**A3. The separation bar sits between two measured nulls.** ε_sep = 0.025 is
2.7 to 4.5× the isotropic null's p95 (which decays 0.0090 → 0.0055 from n = 160
to n = 900) and below the within-node null's median. It is conservative against
"separated at all" and permissive against "separated by more than this node's
own elongation".

**A4. The partition is total.** Zero residual queries, 0.00% held-out residual
rate. Every cell in J's decomposition is a leaf and no term is empty. Every
held-out query the arena judges reaches a leaf.

**A5. The single-parent invariant holds exactly.** All 154 nodes have exactly
one parent; `crossDomainNodes = 0`.

**A6. Mass is conserved exactly.** 8299.000 at every one of the 10 iterations,
no mass warnings.

**A7. The certificate caught something both stopping criteria missed.** In 4 of
20 seeds the run stopped, both criteria satisfied or the structural one
satisfied, while θ was still moving by three to four orders of magnitude above
tolerance. Structure and objective alone would have declared all 20 converged.

**A8. Determinism at a seed is real and its scope is stated.** PCA power
iteration is seeded from the problem shape, node-id counters are monotonic, and
order-sensitive float aggregation iterates sorted. The scoping is honest:
determinism holds *at* a seed and says nothing across seeds.

**A9. The artifact is reproducible from cache.** All 11,773 embeddings are in
`embeddings_cache.db` at full 4096 dimensions, so the construction can be
rebuilt without re-embedding and without depending on a moving model tag.

---

# Part III — What it costs

Ordered by how much a reviewer will care. Each states whether it is fixable and
how.

**L1. The chance correction controls size, not shape.** J corrects against
random relabelling into clusters of the same sizes. A single elongated cluster
cut across its long axis beats that null. A subset of accepted splits therefore
cannot be distinguished from such a cut on the evidence J provides.
*Not fixable within J.* Bounded, not eliminated, by A3 and by the min-pair
bar's measured null.

**L2. Both stopping criteria can fire while θ is still moving, and this is
measured.** 4 of 20 seeds fail the certificate. All four are **period-2 limit
cycles**: `trickleDelta` alternates sign at constant magnitude for every
remaining iteration while `editsDelta` stays 0. `max rel Δκ` is bimodal —
16 certified seeds at 3–7e-13, 4 failures at 1.3–6.0e-03, ten orders apart
with nothing in between, so no seed is marginal. Of the three runs that stopped
on the *structural* criterion, **three of three failed the certificate**
(one-tailed Fisher exact, p = 0.0035), against 1 of 17 for the objective
criterion. Neither criterion observes θ, and the structural one does not
observe routing either.
*Fixable in one line* — require the certificate's θ terms as a third conjunct,
or refuse to stop on the structural arm while |trickleΔ| > τ. Until then it is
a limitation with a measured frequency.

**L3. The certificate is period-1 only.** It asks whether one further iteration
would change the artifact. A construction cycling between two states reports
`CERTIFIED: false` and the certificate does not distinguish that from
divergence. Given L2, this is not hypothetical — it is what happens in 4 of 20
runs.
*Fixable* by testing the operator applied twice; no one has implemented it.

**L4. Nothing validates held-out routing.** Every arena result depends on cell
membership for queries the construction never saw. The one exported measure,
routing ECE = 0.2114, is computed under an aggregation defect that takes a
maximum where the definition takes a sum, so it understates every confidence.
Direction of the error known, magnitude not.
*Fixable* by correcting the export; the defect is documented.

**L5. d = 256 is unjustified at any other width.** `dimForDepth` is a hardcoded
literal with no config path, so the ablation the appendix claims cannot have
run. Worse for a future ablation: d is entangled with the estimator. At
n = 88 the shrinkage factor is 0.407 / 0.254 / 0.145 and the EB blend weight α
is 0.00 / 0.114 / 0.477 at d = 128 / 256 / 512, and at d = 128 the PCA ladder's
top rung equals the full space. Varying d alone does not isolate representation
width.
*Fixable* by a ~5-line patch plus three runs (R-A in the open-items doc), with
the confound stated.

**L6. The descent margin is over-provisioned by roughly a factor of two.**
m = 0.12 exists to pay for the gap between a node's own fitted direction and its
children's resultant. That gap is measured every iteration: worst
1 − cos(μ_v, resultant) = **0.0486** on the frozen run and **0.0647** across all
21 runs. So m is **1.85× the worst gap ever observed**. The hold outcome is
therefore switched off by over-provisioning rather than by design.
*Fixable* by R-C (four runs). The subsystem is not dead code — it produces
queries at m = 0.00 and m = 0.05 and none from 0.06 up.

**L7. Coarsening is nearly inert.** Of 70 accepted edits, **2** came from the
coarsening half, both sole-child dissolutions at iteration 2. **No fusion of any
kind ever fired** — zero fusion log lines in the whole run. The near-duplicate
pre-filter admits **9 of 81** legal pairs at its configured 0.90 and **0 of 81**
at the code's own default 0.92, so the operator's activity is a step function
right at the chosen value.
*Not a defect, but it must be reported* — the design claims a growth/coarsening
symmetry that the artifact does not exercise.

**L8. The size floor is a birth constraint, not an invariant.** It is enforced
on the routed partition at split time; populations drift afterward. 1 of 87
leaves ends below 55. Any statement of the form "every leaf holds at least
`minClusterSize` queries" is false as written.
*Not fixable without a post-hoc repair pass that would break the certificate.*

**L9. Structure varies substantially across seeds.** 72 to 93 leaves, median
86, sample sd 4.42, over 20 runs identical in every parameter except the seed
(and labelling/induction, both post-structural). No cross-seed agreement index
has been computed on this construction.
*Fixable* by computing an agreement index over the existing 20 artifacts — no
new run needed, only analysis.

**L10. The acceptance gate's value is unmeasured.** Part II A1 says what the
gate *refused*. Nothing says what refusing bought. There is no
`acceptanceZ = 0` counterfactual at the frozen configuration.
*Fixable* by one 15-minute run.

**L11. There is no no-taxonomy floor for the construction metrics.** J = 0.2531
and 87 leaves are reported against nothing. A flat 14-cell partition by category
costs nothing to score and would give every construction number a baseline.
*Fixable* by analysis on the frozen artifact — no construction run needed.

**L12. `minClusterSize = 55` is a budget choice.** It was set against the
judge-call budget, not selected by a sweep, and it is not on the historical
sweep's grid. This is already documented honestly and is licensed by the
measured flatness of discriminative power from 14 to 152 cells. Listed here for
completeness, not as a gap.

---

# Part IV — Implementation plan for `report/`

## Ground rules

1. **Anchor edits by quoted text, not line number.** Line numbers shift.
   Every unit below quotes its anchor.
2. **Work bottom-up within each file** so earlier line numbers stay valid.
3. **Do not rename `11_Appendix_DAGConstructionFormalism.tex` or the label
   `app:dag-formalism`.** 28 references across 8 files, zero reader benefit —
   the chapter title is already "Taxonomy Construction Formalism". Only the
   four reader-visible occurrences of "DAG" need touching (`2_Literature.tex`,
   `0_Appendix.tex`, `7_Appendix_TuningProtocol.tex` ×2).
4. **Compile after each phase**, not after each unit. No perl, so `latexmk` is
   unavailable; use the pdflatex/biber sequence already in
   `docs/guides/thesis-reproduction.md`.
5. **Nothing here needs the arena run to stop.**

## Phase 0 — Deletions (do these first; they shrink what the rest must be
consistent with)

| # | File | Anchor | Action |
|---|---|---|---|
| D1 | `11_Appendix` | `\subsection{Residual Retention}\label{subsec:residuals}` (≈254–273) | **Delete the subsection.** Replace every `\ref{subsec:residuals}` with the one-sentence property in E7. |
| D2 | `11_Appendix` | `\section{The Retired Cross-Link Operator}\label{app:cross-link-operator}` (≈742–800) | **Delete the section.** The negative *result* stays in `6_Results.tex:sec:poly-negative`; the mechanics go. Retarget any `\ref{app:cross-link-operator}` to `sec:poly-negative`. |
| D3 | `11_Appendix` | `For an internal node, the split target is its residual pool` (≈562) | **Delete the sentence.** Internal nodes are never split — `TaxonomySplitter.kt:65` returns immediately for non-leaves. |
| D4 | `11_Appendix` | `The concentration fit excludes residual-flagged queries; the mean direction includes them.` (≈98–99) | **Delete both clauses.** No such asymmetry exists; μ̂ and κ̂ read the same weight map. |
| D5 | `11_Appendix` | `($2\epsilon_{\text{sep}}$ for small populations)` and `each new child must remain chance-corrected-distinct ... from every existing sibling branch` (≈621–624) | **Delete both.** Removed from the source; the sibling guard was vacuous even before removal (it iterated `node.children` inside a function that returns unless the node is a leaf). Replaced wholesale by E3. |
| D6 | `11_Appendix` | Stage 1's `k$ selected by chance-corrected marginal improvement $\geq \epsilon_{\text{sep}}$` (≈606–609) | **Delete the selector clause.** Replaced by E3. |
| D7 | `11_Appendix` | `The dimension itself is ablated (A1, ...) at $\{128, 256, 512\}$ to confirm that $d = 256$ is a quality-stable operating point` (≈450–452) | **Delete.** Replaced by E9. |
| D8 | `3_System_Architecture` | `One possible confusion is worth closing here ... is Appendix~\ref{app:tuning-protocol}.` (≈149–159) | **Delete the paragraph.** This is an account of a superseded configuration. Keep one clause in the tuning appendix's provenance note if you want the file named; the Method chapter should describe one construction. |
| D9 | `7_Appendix` | The A1 row of `tab:ablations` and the A5b outcome sentence (`83 leaves at $J = 0.230247$`) | **Delete both.** A1 could not have run (D7). A5b's run is at `a7fdf7d`, pre-`c381211`, which the *next paragraph* of the same appendix uses as grounds to void the maxK figures — and it differs from canonical on three parameters, not one (`marginalEps` 0.0, `minClusterSize` 30, `acceptanceZ` 0.0), against a caption promising one. |

**Net:** roughly 130 lines out of `11_Appendix` (800 → ~670), 11 lines out of
`3_System_Architecture`, one table row and one paragraph out of `7_Appendix`.

## Phase 1 — Corrections that need no run

Each has replacement substance ready. Numbers all derived in
`docs/construction-open-items.md`.

**E1 — State the acceptance rule once, completely.**
`11_Appendix`, at `\section{The Proposal Gate}` (≈653–690). The displayed
equation at ≈672–678 is correct but incomplete. Add the SE = 0 branch and the
non-layering note; then delete the two superseded statements at ≈122–123
(`ΔJ > τ`) and ≈626–629 (`ΔJ > 0`), replacing both with a `\ref` to this
section. Use the text of C3 above verbatim.

**E2 — Add "τ never binds" as a measured property.**
Same section. One sentence: on the frozen run the smallest operative threshold
across 173 rejections was 8.83e-05, 88× τ, and the smallest z*·SE among
accepted edits was 6.54e-05, 65× τ. This is the strongest available support for
expressing the gate in SE units, and it also finishes off the two deleted
statements.

**E3 — Rewrite splitting stage 3 as one gate.**
`11_Appendix`, `\section{Adaptive Splitting Oracle}` (≈553–651). Replace the
three named gates with the min-pairwise rule from C4, plus the note that
`sepScore` survives only as the `dasguptaDeltaNorm` diagnostic. Add the
measured counts: 129 of 373 proposal rows are min-pair rejections; 5682
min-pair rejections against 0 joint k-way across the repository's logs.

**E4 — State the real k selector.**
Same section. Ascending k = 2, 3, 4, first acceptance wins, no float tie-break
(which is what preserves determinism at a fixed split). `maxK = 4` is a cost
bound. Add `maxK` to the locked-parameter table in `7_Appendix` — it bounds the
loop directly, so it is a structural parameter, not a comment.

**E5 — Add the two undocumented eligibility gates.**
Same section: mass **and** ESS = mass²/Σw² must both reach 2·`minClusterSize`.
Under soft membership these differ, and the ESS gate can refuse a node the mass
gate admits.

**E6 — Retire the diffuse branch by arithmetic, not by omission.**
`11_Appendix` ≈379–381. The κ < 0.5 exclusion is unreachable at d = 256 for any
split-eligible node: eligibility needs n ≥ 110, shrinkage at n = 110 is
109/364 = 0.2995, so κ_final < 0.5 needs κ_ML < 1.670, i.e. r̄ < 0.0065. The
least concentrated node in the artifact has r̄ ≈ 0.167, 25× that. One sentence
retiring it beats deleting it silently.

**E7 — Demote the hold outcome from machinery to a measured property.**
`11_Appendix`, `\section{Trickle Routing}` (≈454–551). Replace the residual
subsection (D1) with two sentences inside the descent-gate paragraph: the gate
admits a hold outcome; at m = 0.12 it never fires (0 of 8299 construction
queries, 0.00% of held-out), because the measured worst-case gap between a
node's fitted direction and its children's resultant is 0.0486 on this run and
0.0647 across all 21 runs, so the margin is 1.85× the worst gap. Then remove the
residual clause from J's cell decomposition (≈657–661) — one cell per leaf,
full stop.

**E8 — Fix the path-abandonment constant.**
`11_Appendix` ≈521. `10^{-4}` → `10^{-30}`. The accompanying claim that it
"carries no membership semantics" is only true of the value actually used; at
10⁻⁴ the guard was doing selection work, which is why it moved.

**E9 — Replace the A1 claim with the honest statement.**
`11_Appendix` ≈450–452 (after D7). Two sentences: d = 256 is a fixed operating
point; it has not been ablated, and a future ablation would confound width with
the κ shrinkage factor and the EB blend weight (numbers from L5). If R-A runs,
this becomes a result instead — see Phase 3.

**E10 — Correct the certificate's tolerance attribution.**
`3_System_Architecture` ≈162–165. "All four terms are magnitudes tested against
τ" is wrong. Two test against τ; the two θ terms test against a separate
hardcoded 10⁻⁶, with the code's own reason (τ bounds a change in J; these bound
a change in the parameters that produce it). They coincide only because the
canonical τ happens to be 10⁻⁶.

**E11 — Restore the fourth certificate term in the results.**
`6_Results.tex` ≈993–997 narrates three of four terms and drops
`trickleDelta` (−3.33e-16) — the re-routing term, which the code singles out as
the one that "would miss the ungated routing step". Add it.

**E12 — Replace the R4 evidence sentence.**
`6_Results.tex` ≈1108–1110 and ≈1123. Drop "13.1× from p₁₀ to p₉₀" and
"4 of 52 structural edits at z < 1, the worst at z = 0.156" — the first
mislabels the statistic and the second describes a run with the gate off, which
by construction cannot be the frozen run. Replacement, all from the frozen
run's own `proposals.csv`:

> On the frozen construction the paired standard error of ΔJ varies 13.4×
> across the 69 accepted edits that move queries (3.27e-05 to 4.38e-04), and
> 4.0× between its 10th and 90th percentiles. The gate blocked eight distinct
> split sites whose ΔJ exceeded τ, four of them at z < 1 and the worst at
> z = 0.089 (ΔJ = 9.46e-06 against SE = 1.06e-04). A τ-only rule would have
> committed all eight.

**E13 — Upgrade the stopping-rule limitation from hypothetical to measured.**
`3_System_Architecture` limit 3 (≈220–247). The current text says "A
construction that cycles between two or more states, if the cycle is large
enough to move J, reports `CERTIFIED: false`". That is exactly what happens.
Replace the conditional with the measurement: 4 of 20 seeds are period-2 limit
cycles with `editsDelta` = 0 and `trickleDelta` alternating at constant
magnitude; `max rel Δκ` is bimodal across the sweep (16 at ~1e-13, 4 at ~1e-3);
and every run that stopped on the structural criterion failed the certificate
(3 of 3, Fisher exact one-tailed p = 0.0035) against 1 of 17 for the objective
criterion. Mirror the same in `6_Results.tex` where the sweep is reported.

**E14 — Correct the Newton–Raphson claim.**
`11_Appendix` ≈307–308: "convergence typically occurs within one or two steps"
→ two or three at d = 256, three at the artifact's leaf concentrations, and the
five-step cap is never reached anywhere in the domain of r̄. Fix the same claim
in the source comment at `StatisticsUtils.kt:31` while you are there.

**E15 — Fix `numIterations` and the footnote it sits under.**
`7_Appendix` lines 28 and 165: 35 → 50. The footnote claims the table's values
were "read from its run configuration"; they were not. Either verify every row
against `freeze_mcs55.toml` and keep the footnote, or drop it. Add `maxK = 4`
(E4) while the table is open.

**E16 — Withdraw the descentMargin cost claim.**
`7_Appendix` ≈58–63: "roughly five points of routing quality". The only
artifact that could support it gives 3.11 points (0.7747 vs 0.7436) and is
pre-`c381211`, at `minClusterSize = 30`, with a different model roster. Either
state it as unquantified pending R-C, or delete the number and keep the
direction.

**E17 — Report what coarsening actually did.**
`11_Appendix` Phase 5 (≈125–136) and `6_Results.tex`. Add the counts from L7:
2 of 70 accepted edits, both sole-child dissolutions, no fusion of any kind
fired, near-duplicate pre-filter admits 9 of 81 legal pairs at 0.90. Also add
the operator ordering, which is currently nowhere and is outcome-relevant
because each accepted edit becomes the next proposal's base:

> starved-leaf → sibling fusion → near-duplicate fusion → sole-child
> dissolution repeated to a fixed point → starved-leaf again.

**E18 — Say what `fusionSimilarityThreshold` filters.**
`7_Appendix` table row. It is a cosine pre-filter on the pair of node
directions, applied before the separation test, restricted to same-parent pairs
at depth > 1. At 0.90 it admits 9 of 81 pairs in the frozen tree; at the code's
default 0.92 it admits none.

**E19 — Fix the multi-membership contradiction.**
`11_Appendix` ≈797–800 says evaluation-time multi-leaf assignment "determines
which leaves a given query contributes comparisons to during the arena run". It
did not — only the primary leaf was filed for every reported run.
`12_Appendix_Numerics.tex:207-211` already states this correctly. Delete the
false sentence and cross-reference the correct one.

**E20 — Add the four reader-visible "DAG" fixes.**
`2_Literature.tex` ×1, `0_Appendix.tex` ×1, `7_Appendix` ×2. The construction
is a tree; say tree.

**E21 — Record the sweep's build provenance.**
`3_System_Architecture` ≈64–74 footnote. Seeds 1–19 were built from `c381211`
and seed 20 from `83ff7ba`. The change is gated on a config key that defaults
empty and is absent from every sweep config, so it is behaviourally inert — but
the sweep is a 19+1 build and nothing records that. One clause in the footnote.
Also soften the body sentence "identical in every parameter except the seed",
which the footnote two lines later already contradicts.

**E22 — Record the embedding model precisely.**
`3_System_Architecture` ≈104 and `11_Appendix` §MRL. The model is
Qwen3-Embedding-8B (4096 native dimensions, confirmed from the 16384-byte
float32 BLOBs in `embeddings_cache.db`), served via Ollama under the moving tag
`qwen3-embedding:latest`. State that the exact revision is not recoverable and
that the construction is instead reproducible against the cached vectors, all
11,773 of which are on disk. That second clause is what makes it a
reproducibility statement rather than a caveat.

## Phase 2 — Analysis-only additions (no construction run)

**E23 — Cross-seed agreement index.** Closes L9. The 20 sweep artifacts are on
disk with full leaf assignments. Compute pairwise adapted-Rand or a Jaccard
over leaf co-membership across seeds and report it. This is the single most
requested missing number in R3 and it needs no run.

**E24 — A flat 14-cell floor for J.** Closes L11. Score the canonical
category partition under the same J and put it next to 0.253129. Analysis only.

## Phase 3 — Edits that wait on a run

Each maps to a run spec in `docs/construction-open-items.md` §2. Leave a
clearly marked placeholder rather than a claim; the report must not assert what
has not been measured.

| unit | waits on | what it becomes |
|---|---|---|
| E9 → result | **R-A** (d ablation, 3 runs, ~45 min, 5-line patch) | A1 becomes a real row: leaf count, J, held-out Top-1, ECE, certificate status at d ∈ {128, 256, 512, 1024}. State the shrinkage/α confound alongside. |
| new, L10 | **R-E** (`acceptanceZ = 0` at the frozen config, 1 run, ~15 min) | Turns "the gate refused eight sites" into "the gate is worth X leaves and Y in J". Highest argumentative value per minute in the whole plan. |
| E16 → number | **R-C** (descentMargin ladder, 4 runs, ~60 min) | Replaces the withdrawn five-point claim with a one-factor curve at the frozen configuration, and locates the mode boundary. |
| `6_Results` ≈1100–1104 | **R-B** (seed-42 repeat, 1 run, ~15 min) | Names the two non-reproducible certificate fields, or deletes the sentence. Predicted: `trickleDelta` and `maxKappaRel`. Register the prediction first. |
| `7_Appendix` maxK note | **R-D** (maxK ∈ {2,6,8}, 3 runs, ~45 min) | Removes the "void as to values, qualitative finding stands" hedge. Lowest value of the five. |

## Execution order

```
Phase 0  deletions                     ~1 h    no dependencies
Phase 1  E1–E22, corrections           ~4 h    depends on Phase 0
         └─ compile checkpoint
Phase 2  E23–E24, analysis             ~2 h    independent; can run in parallel
         └─ compile checkpoint
Phase 3  after each run lands          per run  arena must be idle first
```

Phases 0–2 are 22 edit units plus two analyses and require no construction run,
so they can all be done while the arena is running. Phase 3 is five runs
totalling about 3 hours of machine time and one small patch.

## Definition of done for Phases 0–2

- [ ] No sentence in `report/` describes a gate, selector or subsystem that
      `TaxonomySplitter`, `TaxonomyTrickler`, `TaxonomyMerger` or
      `TaxonomyOperations` does not execute at the frozen configuration.
- [ ] The acceptance rule appears exactly once, with both branches.
- [ ] Every number in the construction sections traces to an artifact under
      `experiment_results/freeze_mcs55/seed_42/`, the 20-seed sweep, or
      `snapshots.db` — or is explicitly marked void, argued, or pending a
      named run.
- [ ] No claim sourced from a commit older than `c381211` survives unmarked.
- [ ] `grep -c residual` on `11_Appendix` returns single digits, all of them
      the descent gate's hold outcome.
- [ ] The report compiles.

---

## One thing this plan deliberately does not do

It does not soften L1, L2 or L11. The chance-correction blind spot, the
stopping rule's measured failure in 4 of 20 seeds, and the absence of a
no-taxonomy floor are the three things an examiner will press on, and the
plan's position is that all three read better stated with a number than
argued around. L2 in particular converts from an embarrassment to a finding
the moment the mechanism is named: a fixed-point certificate was built to
detect what the stopping rule cannot see, and in 4 of 20 runs it detected it.
