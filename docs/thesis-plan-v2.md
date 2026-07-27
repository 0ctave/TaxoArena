# Thesis plan v2 — six chapters, four appendices

Status: **written 2026-07-27**, against branch `tree-only` @ `a92a3ed`.
No `.tex` file was edited in producing this plan.

**The instruction this plan implements** (supervisor, verbatim):

> "9 chapters is way too big... justify the construction mostly in appendix and just
> state what makes a good construction for my use, to then argument on my arena. The
> content is too big for a master thesis."

So: **six chapters**. The taxonomy construction is the *instrument*; the arena results
are the centre of gravity. This is not a demotion imposed from outside — the thesis
already says it at `report/03_Content/1_Introduction.tex:225-233` ("the induced taxonomy
is *not* the contribution of this thesis; it is the instrument"), and
`docs/prereg_discriminative_power.md:83-97` measured that an 11x change in granularity
and a +10.3% J routing correction both change discriminative power by **zero**. A
construction whose tuning has no measured evaluative consequence belongs in an appendix.

**Sources this plan is built on**, in order of authority:
`docs/arena-math-findings.md` (most current; contains self-corrections, later sections
supersede earlier), `docs/reconciled-argument.md` (code/docs/report reconciliation and
the 13-rung ladder), `docs/reframed-argument.md`, `docs/frozen-artifact.md`,
`docs/prereg_*.md`, `docs/void-results.md`, `docs/known-defects.md`,
`docs/transferable-findings.md`, `docs/measurement-discipline.md`, and the current
`report/**/*.tex`.

**Marking convention used throughout.** Every claim is **MEASURED** (there is data, and
it could have come out otherwise) or **ARGUED** (reasoning the thesis owes the reader, no
data behind it). The current report blurs these, and that is why its negatives read as
apologies rather than as findings. Any claim with no citable evidence is either marked
ARGUED and stated as motivation, or it is not in the plan.

---

# Part 0 — Structural decisions, and where this plan deviates from the target

## 0.1 The structure

| ch | title | pp | centre of gravity |
|---|---|---:|---|
| 1 | Introduction | 9 | the missing argument: a partition is worth building only if it changes what a judge can be told |
| 2 | Background | 11.5 | LLM-as-judge reliability; pairwise ranking; benchmark saturation |
| 3 | Method | 15 | §3.1 requirements on the partition (3pp) · §3.2 the arena (9pp) · §3.3 measurement discipline (2pp) |
| 4 | Experimental Design | 9 | corpus, two rosters, conditions, pre-registrations with dates |
| 5 | Results | 20 | §5.1 what the judge does (12pp) · §5.2 what the partition does (7pp) |
| 6 | Discussion and Conclusion | 11 | where the architecture binds; the measurement debt; what was demonstrated |
| | **main text total** | **75.5** | |

| app | title | pp | source |
|---|---|---:|---|
| A | Taxonomy construction formalism | 18 | `11_Appendix_DAGConstructionFormalism.tex`, corrected |
| B | Tuning protocol, numerics, metric definitions | 14 | `7_App` + `12_App` + `9_App`, merged and trimmed |
| C | Pre-registrations, reproduced with dates | 8 | `prereg_*.md` |
| D | Model roster and exclusion policy | 4 | `10_Appendix_ModelRoster.tex`, rebuilt |
| | **appendix total** | **44** | |

Page budgets assume ~38 lines of this project's `.tex` per typeset page. That conversion
is an **estimate**, not measured from a compiled PDF — `latexmk` is unusable in this
environment (no perl). See Part VI.

## 0.2 Three deviations from the target structure, each justified

**(a) Chapter 3 gains a third section, §3.3 "Measurement discipline" (2pp), funded by
cutting §3.2 from 11pp to 9pp.**
Reason: `docs/measurement-discipline.md` and `docs/transferable-findings.md` contain four
rules, each derived from a specific failure with a measurement attached — the 13.1x spread
in `SE(dJ)` (`transferable-findings.md:48-52`), the 0-of-613 vs 97-of-613 mixed-group
count (`:144-146`), the threshold-reuse instances (`:83-120`). These are the part of the
work useful to a reader who will never build a taxonomy, and three of the four did real
work in Chapter 5. Placing them in Chapter 3 pre-arms the reader; placing them in an
appendix loses them. §3.2 can afford the two pages because the state-machine material that
padded it describes code that does not exist (Part III, cut C7).

**(b) The polyhierarchy negative moves from Discussion into §5.2, at ~1.5pp.**
It is a *result about the partition* — an operator was built, measured, and retired — not
an interpretation. `7_Discussion.tex:21-110` is the best-written section in the current
thesis and it is the template every negative in this plan imitates. Keeping it in
Discussion in a 6-chapter thesis would leave §5.2 without its cleanest example of the
form. Its scoring formula (`7_Discussion.tex:46-51`) moves to Appendix A.

**(c) There is no Appendix E for transferable findings.**
The target names four appendices and this plan honours that. Finding 2 (calibrate against
the paired SE of your own objective) and finding 4 (report a join's overlap before its
result) go into §3.3; finding 1 (shared concentration) goes into Appendix A where the
routing rule lives; finding 3 (threshold reuse) goes into §3.3 and Appendix B.

## 0.3 The one structural tension this plan must resolve openly

**Chapter 4's roster and Chapter 5's roster are not the same roster, and the plan says so
rather than smoothing it over.**

- The arena run that Chapter 5 §5.1 reports used **8 models** on Math
  (`arena-math-findings.md:477-484`), four of which had `model_output` stored as the empty
  string across all 12,032 rows (`:491`).
- The roster the corrected exclusion policy produces is the **11-model band**
  (`reconciled-argument.md:143-186`): the report's own documented 12 minus
  `gemini-1.5-pro-002`, which is banned at `EvalIngestValidator.kt:327` for a bare answer
  on 35.4% of items. Post-backfill, 11 of the 12 are >= 99.8% substantive.
- Corpus-wide, the trace backfill took the corpus from 13 to 37 models with traces; one of
  those (`Meta-Llama-3-70B-Instruct`) sits in a different question-id space, so the
  **maximum valid roster is 36 models**.

Chapter 4 therefore specifies **two rosters**: the *pilot roster* (8, as run, with its
defect) and the *corrected roster* (11 band, as policy). Appendix D tabulates both. This
is the honest structure and it is also the strongest one, because the exclusion policy is
itself a result (§5.1.5) rather than a housekeeping decision.

---

# Part I — The main thesis, section by section

Format for every section: **(a)** purpose · **(b)** pages · **(c)** claims · **(d)**
evidence per claim, MEASURED or ARGUED, with a citation · **(e)** the caveat that bounds
it · **(f)** what existing `.tex` is reused / rewritten / cut.

---

## Chapter 1 — Introduction (9 pp)

### 1.1 The routing problem (2 pp)

**(a)** Establish, for a non-specialist, that a single score cannot tell you which model to
use for a particular task.
**(b)** 2 pp.
**(c)** C1.1 Agentic pipelines dispatch sub-tasks and need a capability map. C1.2 A scalar
leaderboard discards exactly the information a router needs.
**(d)** Both **ARGUED**. C1.1: `1_Introduction.tex:5-33`, already well written. C1.2:
`1_Introduction.tex:58-93` plus the worked micro-example at `:73-93`.
**(e)** The micro-example's numbers are synthetic and the current text declares them so
(`1_Introduction.tex:100-107`). **Keep that declaration** — it costs nothing and it is the
first signal to the examiner that this thesis distinguishes illustration from measurement.
**(f)** **Reuse** `1_Introduction.tex:1-110` nearly verbatim. Trim the "Static Benchmark
Problem" subsubsection (`:41-56`) by half; its second axis (fixed categories) is restated
better in §1.2.

### 1.2 The evaluation gap, and what a partition is for (3 pp) — **the section that does not exist**

**(a)** Write the argument the thesis is missing: a cell is not a reporting bucket, it is a
*scope for a rubric*.
**(b)** 3 pp.
**(c)** C1.3 Splitting a cell reduces the surface over which a judge must generalise; that
is the entire mechanism. C1.4 A judge asked about "Computer science" must hold one rubric
spanning operating systems, cryptography, group theory and time-series diagnostics; a judge
asked about "Time Series Model Diagnostics and Validation" can be told what a good answer
looks like *there*.
**(d)** Both **ARGUED**. `docs/reframed-argument.md:6-13`. The report knows this is
missing: there is a 22-line `TODO(author)` at `1_Introduction.tex:135-156` saying so in as
many words and calling it "large enough to warrant its own chapter". This plan gives it
three pages inside Chapter 1 rather than a chapter, because the supervisor's constraint is
fewer chapters, and because the argument is short once stated plainly.
**(e)** Stated this way the thesis's value proposition is a claim about **judging**, not
about partition quality. Say that explicitly — everything downstream follows from taking
it seriously, including why Chapter 5 leads with the judge.
**(f)** **Write new.** Delete the `TODO` block at `:135-156` and replace it. The three
things the TODO asks for map to: (1) → C1.4; (2) → §3.1's four requirements; (3) → §3.1's
"what it guarantees and what it does not" plus Appendix C's pre-registered bands.

### 1.3 The three links, and the research questions (2 pp)

**(a)** Decompose the claim into three separately falsifiable links and state the two
research questions the thesis actually answers.
**(b)** 2 pp.
**(c)** C1.5 The chain is `coherent cells -> specific rubrics -> better judgments ->
ranking closer to ground truth`, links 1/2/3. C1.6 **RQ1 (retained, reworded):** do
answer-key-blind, domain-conditioned pairwise LLM judgments recover per-domain capability
rankings, and *what decides the verdicts*? C1.7 **RQ2 (replaced):** does adapted grouping
enable **better judging**? — not "does it improve rank fidelity between cells".
**(d)** C1.5 **ARGUED**, `reframed-argument.md:15-25`; `prereg_rubric_specificity.md:9-14`.
C1.7 is forced by a **MEASURED** result: the premise under the old RQ2 does not hold on
this corpus (`prereg_discriminative_power.md:74-79`, `reframed-argument.md:26-46`), so a
per-cell `Δτ` measures a difference with no room to exist.
**(e)** The three-link decomposition was written **after** some of the results. Say so, in
one sentence. A reframing announced is a contribution; a reframing concealed is a
rationalisation (`reconciled-argument.md:771-773`).
**(f)** **Rewrite** `1_Introduction.tex:289-317`. **Cut** the old RQ2 wording at `:301-307`
and the five-metric DQ1 sentence at `:310-317`.

### 1.4 Contributions, scope, and thesis structure (2 pp)

**(a)** State what was demonstrated, and bound it before the reader has to ask.
**(b)** 2 pp.
**(c)** C1.8 Contribution 1: a measured account of **what an LLM judge actually decides on
a corpus with a verifiable answer key**, with four controls. C1.9 Contribution 2: a
construction method with three guarantees, presented as an instrument. C1.10 Contribution
3: a measured, pre-registered **negative result** about geometry-adapted evaluation
partitioning, scoped by power and by roster. C1.11 Contribution 4: the reframing itself.
C1.12 Scope: a selected-domain pilot at n=8 models on Math, with a named format defect.
**(d)** C1.8 **MEASURED**, forward-reference to §5.1. C1.9 **MEASURED**, §5.2.1. C1.10
**MEASURED**, `prereg_discriminative_power.md:171-181`. C1.11 **ARGUED**,
`reframed-argument.md:153-170`. C1.12 **MEASURED**, `arena-math-findings.md:468-558`.
**(e)** Contribution 1 is the one that changed: the thesis set out to validate a taxonomy
and ended up measuring a judge. Say that in the Introduction, not in the Conclusion.
**(f)** **Rewrite** `1_Introduction.tex:254-288` (contributions) and `:319-336` (scope).
**Reuse** the "Position of the taxonomy" paragraph at `:225-237` almost verbatim — it is
already correct and it now matches the structure. **Rewrite** `:337-360` (thesis structure)
for six chapters. **Cut** `:239-252`'s "Dynamic Domains" paragraph to two sentences.

---

## Chapter 2 — Background (11 pp)

### 2.1 Benchmark saturation and the limits of fixed corpora (2.5 pp)

**(a)** Establish that per-domain resolution is a real gap, not an invented one.
**(b)** 2.5 pp.
**(c)** C2.1 Aggregate leaderboards saturate and lose discriminative power. C2.2 Editorial
category structure is fixed at construction time.
**(d)** **ARGUED** from cited literature; `2_Literature.tex:21-154` already does this.
**(e)** None beyond normal.
**(f)** **Reuse** `2_Literature.tex:21-154`, trimmed by ~25%.

### 2.2 LLM-as-a-judge: what is known to go wrong (4 pp) — **expanded**

**(a)** Give the reader the biases and failure modes that Chapter 5 will measure, so §5.1
lands as a contribution to a live debate rather than as a surprise.
**(b)** 4 pp (up from the current 129 lines ≈ 3.4 pp; expand toward correctness-shortcut
and self-consistency work).
**(c)** C2.3 Positional bias. C2.4 Verbosity bias. C2.5 Guideline incompleteness. C2.6 The
open question this thesis answers empirically: on a corpus with a verifiable key, what does
the judge condition its verdict on?
**(d)** C2.3-C2.5 **ARGUED** from literature, `2_Literature.tex:413-541` plus
`1_Introduction.tex:124-133`. C2.6 is positioning, **ARGUED**, and it is the hinge: it
frames §5.1 as answering a question the field has, not as a diagnostic of this system.
**(e)** The thesis must be careful not to claim novelty for "LLM judges prefer longer
answers" — that is cited. The novel measurement is the *decomposition* in §5.1.
**(f)** **Reuse and expand** `2_Literature.tex:413-541`. This is the one place in Chapter 2
that grows.

### 2.3 Pairwise ranking and Bradley–Terry (2.5 pp)

**(a)** Give BT, MM estimation, and the identifiability issue, at the level Chapter 3 needs.
**(b)** 2.5 pp.
**(c)** C2.7 Pairwise comparison localises the judgment. C2.8 BT with MM (Hunter 2004) is
the standard estimator. C2.9 BT is identified only up to an additive constant per connected
component.
**(d)** **ARGUED** from literature; `2_Literature.tex:542-708` already covers it.
**(e)** None.
**(f)** **Reuse** `2_Literature.tex:542-708`, trimmed by ~30%.

### 2.4 Taxonomy induction — positioning only (1 pp)

**(a)** Say what family the construction belongs to and move on.
**(b)** **1 pp** — two paragraphs of positioning plus one short paragraph the polyhierarchy
result depends on.
**(c)** C2.10 The construction is hierarchical directional clustering with label seeding;
it is not compared against the HTC literature because no gold taxonomy exists for MMLU-Pro
and the supervised HTC baselines were removed as unimplemented. C2.11 Weighted
multi-membership with a responsibility floor is a **different claim** from polyhierarchy,
and this thesis retains the first and rejects the second.
**(d)** C2.10 **ARGUED**, with the second half **MEASURED-adjacent**: `5_Exp:246-256`
already records that HiAGM and HGCLR were removed as unimplemented, and `5_Exp:281-285`
records that reference-dependent metrics were dropped for want of a gold taxonomy. C2.11
**ARGUED**, `2_Literature.tex:282-302`.
**(e)** This is a *positioning* claim, and stating it as such is what licenses the cut. Do
not let it read as a literature review.
**(f)** **Partial cut** of `2_Literature.tex:155-412` — see Part III, C1, which was
**revised** after inspecting the section's seven subsections. Three of them are load-bearing
and cannot be cut wholesale: `:245-305` (overlapping / polyhierarchical taxonomies) sets up
the negative result and **forward-references `sec:poly-negative` at `:303-305`**, so cutting
it orphans §5.2.5; `:219-242` (vMF / spherical, with `\label{eq:vmf}` at `:227-231`) is what
§3.1 and Appendix A cite; `:307-341` (Matryoshka) justifies the fixed 256-d slice at every
depth and belongs in Appendix A.

### 2.5 Query routing as the target use case (1.5 pp)

**(a)** Close the loop back to Chapter 1's motivation.
**(b)** 1.5 pp.
**(c)** C2.11 Routing is the consumer of per-domain profiles; this thesis builds the
substrate, not the router.
**(d)** **ARGUED**; `2_Literature.tex:709-783` plus `1_Introduction.tex:29-33`.
**(e)** The thesis does not deploy a router and must not imply it does
(`1_Introduction.tex:33`).
**(f)** **Reuse** `2_Literature.tex:709-783`, trimmed by ~40%.

---

## Chapter 3 — Method (15 pp)

### 3.1 What a good partition needs — four requirements (3 pp) — **the key move**

**(a)** State, as *requirements* rather than derivations, what the partition must satisfy
for the arena to mean anything; show in one paragraph that they are met; give the evidence;
name the three limitations; point to Appendix A for the formalism.
**(b)** **3 pp, not thirty.**

**(c) The four requirements, stated before any construction detail:**

> **R1 — Coherence.** Cells must be homogeneous enough that a single rubric fits every
> query in the cell.
> **R2 — Support.** Cells must be large enough that per-cell judging is identifiable and
> per-cell reliability is not dominated by noise.
> **R3 — Stability.** The same corpus must produce the same cells; the construction must
> reach a state one further application of the operator would not change.
> **R4 — Verifiability.** It must be stated what the construction guarantees and what it
> does not, in advance of any result that depends on it.

**One paragraph on how they are met** (this is the entire construction summary in the main
text): anchors are seeded from the 14 MMLU-Pro labels; queries migrate by embedding
geometry; each anchor is recursively split under a chance-corrected separation score `J`;
a split is accepted only when every child pair clears a separation bar **and** the
improvement in `J` exceeds twice its own paired bootstrap standard error; the loop runs to
a certified fixed point. Full formalism: Appendix A.

**(d) Evidence that the requirements ARE met, one row per requirement:**

| req | evidence | mark | citation | caveat |
|---|---|---|---|---|
| R1 | Split accepted only when min-pair chance-corrected separation >= 0.025, positioned between two measured nulls: isotropic p95 spans 0.0055–0.0093 over n=75..900; within-node p50 ~0.033–0.063 | **MEASURED** | `frozen-artifact.md:129-136`; score at `StatisticsUtils.kt:193-219` | the within-node values were computed on the pre-`c381211` tree and are **void as to values**; method survives (`void-results.md:24`). **Work required** — re-derive on the frozen mcs=55 artifact before this sentence ships |
| R1 (independent) | Rubrics induced on these cells are cell-specific against a randomised null, p = 1.2e-6 | **MEASURED** | §5.2.2; `build/rubric_null/measures_all.json` | lexical only; see §5.2.2 |
| R2 | 87 leaves, median 88 queries, IQR [71, 118], min 54, max 396 | **MEASURED** | `reconciled-argument.md:404`, read from `snapshots.db` | `minClusterSize` is a **birth** constraint, not an invariant: 1 of 87 leaves ends below it (`frozen-artifact.md:150-155`) |
| R2 | Identification is reached at 7 pairs of 28 (a spanning tree) at 32.9–45 comparisons per cell, and the cost **varies** across cells | **MEASURED** | `arena-math-findings.md:341-348` | measured at 8 models; at 11 models it is 55 pairs, not recomputed (`reconciled-argument.md:1200-1202`) |
| R2 | Granularity is evaluatively flat over an 11x change, so cell count is free to choose on budget grounds | **MEASURED** | `prereg_discriminative_power.md:74-79, 118-123` | this is the licensing result for `minClusterSize = 55`; it has **not** been re-derived at the corrected roster (Part VI) |
| R3 | Certified fixed point at **iteration 10**: `edits delta 0`, `max 1-cos(mu) 1.11e-16`, `CERTIFIED true`; iterations 8/9/10 identical on every column | **MEASURED** | `frozen-artifact.md:27-39` | certifies *this artifact*, not that the loop terminates from an arbitrary start (`:47-50`); two of six fields are **bounded, not reproducible** (`known-defects.md:9-25`) |
| R4 | The acceptance gate is calibrated in units of its own objective's paired SE: `SE(dJ)` spans **13.1x** p10→p90; the uncalibrated rule accepted **4 of 52** edits below z=1, worst at z=0.156 | **MEASURED** | `frozen-artifact.md:95-101`; `transferable-findings.md:48-52` | the gate is defended on **coherence alone**; both empirical corroborations were tested and refuted (§3.3, §5.2.1) |

**Three named limitations, stated here and not buried:**
1. "Chance-corrected" means against **random relabelling into the same size profile**, not
   against anisotropy. A cut through a node's own elongation is not excluded by `J`
   (`TaxonomySplitter.kt:294-301`; `separation_null_by_size.md:193-200`). **MEASURED**
   consequence: 6 of 27 clean-null splits cannot be distinguished from such a cut, and
   19.7% of leaf-held queries sit under at least one such ancestor
   (`reframed-argument.md:149-151`) — **but those figures are void as to values**
   (`void-results.md:24`) and must be re-derived or dropped.
2. The floor is a **birth** constraint. Any sentence of the form "every leaf holds at least
   `minClusterSize` queries" is false as written (`frozen-artifact.md:150-155`).
3. The certificate tests **period 1** only. A tolerance-scale 2-cycle reads as
   `CERTIFIED: false` forever; `certify(period = p)` is not implemented
   (`known-defects.md:36-41`).

**(e)** The bounding caveat on the whole section: none of R1–R4 says the partition helps
the arena. That is links 2 and 3, and it is Chapter 5. Say so in the last sentence of §3.1.

**(f)** **CUT** `3_System_Architecture.tex:231-344` (construction pipeline + data model,
114 lines) down to this 3-page section; the material moves to Appendix A. **CUT** the
entire DQ1 metric vocabulary (Dendrogram Purity, Weighted Leaf Purity, Spherical
Silhouette, Total Dasgupta Cost, Sackin Index) from the main text — see Part III, cut C4.
**Reuse** nothing verbatim; this section is new prose over corrected numbers.

### 3.2 The arena (9 pp)

#### 3.2.1 Offline re-judging of stored responses (1 pp)

**(a)** State plainly what the system is, because the current chapter describes something
else.
**(c)** C3.1 The arena does not query models. It re-judges **precomputed traces** stored in
the eval corpus.
**(d)** **MEASURED** against code: `TaxonomyBenchmarkService.kt:906-920`;
`reconciled-argument.md:640-648` calls this "the single largest architectural divergence in
the thesis". `3_Arch:365-384`'s `LeafArenaState` and response cache do not exist; state is
`NodeBtState` + `List<NodePairStats>` (`TaxonomyBenchmarkService.kt:383-406`).
**(e)** This is also the fact that makes the trace-capture defect (§5.1.5) intelligible: a
model whose response text was never stored cannot be distinguished downstream from one
whose was, because `getRobustTrace` never returns empty
(`TaxonomyBenchmarkService.kt:1740-1752`).
**(f)** **CUT** `3_System_Architecture.tex:365-384`. **Write new.**

#### 3.2.2 Judge design: the prompt, and what it does and does not see (2.5 pp)

**(a)** Specify the judge exactly, including the two things the current report omits.
**(c)** C3.2 Per-cell rubric injected into the system prompt. C3.3 Rubrics are induced from
construction-set queries with reference answers; held-out queries never enter rubric
generation. C3.4 **The judge is prompt-blind to the answer key but NOT blind to the
answers**: the `[Question]` block includes the full multiple-choice options, and 94.8% of
traces state their own answer. C3.5 Dual-call with sides swapped; disagreement recorded as
a tie.
**(d)** C3.2 **MEASURED**: `TaxonomyArenaService.kt:895`, `:929-930`. C3.3 **MEASURED and
audited** — the reserved-text filter at `TaxonomyJudgeService.kt:161-163` is accompanied by
a `check{}` at `:172-180` that **fails the build** if the filter and the membership test
ever disagree; this is the strongest guarantee in the system and the current thesis
under-sells it (`reconciled-argument.md:681-686`). C3.4 **MEASURED**: options block built
at `TaxonomyArenaService.kt:655-658`; answer-key guard is real
(`require(!query.contains("Ground Truth Answer"))`, `:478-480`) and `gtAnswer` is never
read (`:599`). C3.5 **MEASURED**: `:523-524`, `:535-539`, `:544-553`.
**(e)** Four disclosures that must travel with C3.2–C3.5, none currently in the report:
(i) the shared template is **appended** after the persona, not prepended, contradicting
`3_Arch:518-520`; (ii) the verdict schema also carries a numeric `confidence` that is
load-bearing downstream (`TaxonomyArenaService.kt:151-163`); (iii) `finalConfidence` is
forced to 0.5 on a position flip and capped at 0.95 (`:571`); (iv) a post-hoc
`adjustForPositionBias` **rewrites a pair's win counts** when the order asymmetry exceeds
0.3 with n>=6 (`TaxonomyBenchmarkService.kt:1772-1791`). Also: an `INVALID` verdict is
**silently dropped** with no counter and no export row (`:92`, `:944`, `:1000`).
**(f)** **Reuse** `3_System_Architecture.tex:501-551` as the skeleton, corrected on all
four points. **Cut** the vestigial prompt instruction "If the ground truth answer is
provided..." (`TaxonomyArenaService.kt:945`) from any verbatim quotation — it refers to a
field that is never supplied.

#### 3.2.3 Bradley–Terry estimation (2.5 pp)

**(a)** Give the estimator that actually produced the numbers.
**(c)** C3.6 BT with the Hunter MM update. C3.7 A Jeffreys Beta(0.5,0.5) prior applied as a
phantom half-win in each direction, **only to pairs that already carry data**. C3.8
Standard errors from the full observed Fisher information, rank-completed. C3.9 Ties as
half-wins, no Davidson parameter.
**(d)** All **MEASURED against code**: C3.6 `BtMmFitter.kt:226-237`; C3.7 `:28`,
`:207-216`, `:366`; C3.8 `:355-372`, inversion `:313-343`, correction `:375-386`; C3.9
`:200-201`.
**(e)** **Five corrections the current text needs, one of which is load-bearing for every
CI in the thesis:**
- `4_Methodology.tex:84-88`'s MM equation is **wrong** — it writes the denominator as
  `Σ N_ij / σ(s_i − s_j)`, which expands to a different quantity
  (`reconciled-argument.md:428-435`).
- `:89` says the update is applied "cyclically" (Gauss-Seidel); the code is a simultaneous
  Jacobi sweep (`BtMmFitter.kt:224-245`).
- `:90-91` claims tol `1e-6` and a 500-iteration cap; the cap is **200**
  (`BtMmFitter.kt:132`) and the tolerance is `max(tol, 0.01·SE_lb)` (`:255-257`).
- `:96-99` says the SEs use "the pseudoinverse"; the code inverts the rank-completed
  `I + 11ᵀ` (`:375-386`) — and contradicts its own appendix `12_App:132-143`.
- **The variance correction was `1/K` and should be `1/K²`.** Fixed in code at commit
  `a92a3ed` (2026-07-27). The wrong constant over-subtracted `(K−1)/K²` — 0.109 at K=8 —
  which is larger than the variance itself at every realistic comparison count, so **every
  Bradley–Terry standard error the system ever reported was the clamp constant, not a
  measurement**. Correct values are 44–209x larger. `12_Appendix_Numerics.tex:137-139`
  documents the same wrong constant and needs the matching correction.
- `:100-104`'s "**guarantees** every pair receives at least one comparison" is an
  over-claim: the connectivity bootstrap works on **global** pair counts
  (`BtMatchScheduler.kt:417-433`), so per-leaf graphs can be disconnected. Delete the word
  "guarantees".
**(f)** **Rewrite** `4_Methodology.tex:73-104` completely. **Reuse** the identifiability
discussion at `:100-104` after the correction.

#### 3.2.4 Scheduling, stopping, and aggregation (2 pp)

**(a)** Describe the scheduler and the four real exits.
**(c)** C3.10 Composite utility with a maturity-decaying mixing parameter. C3.11 A pair
resolves on separation `|θ_i − θ_j| >= 3(σ_i + σ_j)`. C3.12 Domain-level scores come from
**pooling leaf-level counts and refitting**, never from averaging leaf parameters.
**(d)** C3.10 **MEASURED**: real but named `alpha`, maturity-driven via `1 − avgSE/10`
(`BtMatchScheduler.kt:483-485`, `:606`), with an undocumented tie-mask (`:592-595`) and
repeat discount (`:605`). C3.11 **MEASURED**: `BtStoppingPolicy.kt:123` — this is the one
predicate from the reported state machine that is real. C3.12 **ARGUED** and correct as
written at `4_Methodology.tex:172-182`.
**(e)** Three things must be corrected or cut: the named state machines
(`UNSEEN/INFORMATIVE/RESOLVED/EXHAUSTED`) and `U_min` do not exist in `src/`; the
`escaped = true` / `B_max` escape valve does not exist — the de-facto exit is
`round >= maxRounds` (`BtStoppingPolicy.kt:162`); query selection is a **persisted
round-robin offset** (`TaxonomyBenchmarkService.kt:377-381`), not descending cosine to the
leaf centroid. Also: the scheduler's over-sampling of uncertain pairs **biases win-rate**,
which is why §5.1 quotes BT and not win-rate (`arena-math-findings.md:178-188`).
**(f)** **CUT** `3_System_Architecture.tex:416-476` (state machines and the state diagram —
a figure of code that does not exist) and `4_Methodology.tex:143-171`'s escape-valve
sentence. **Reuse** `4_Methodology.tex:106-142` (scheduler utility) with the `alpha` naming
corrected, and `:172-191` (aggregation) minus the `1/k` sensitivity sentence (Part III, C8).

#### 3.2.5 What is *not* implemented (1 pp)

**(a)** A single honest inventory, so the reader never finds a gap the thesis did not name.
**(c)** C3.13 Six mechanisms described in the current report have no implementation.
**(d)** **MEASURED against code**, `reconciled-argument.md:640-668`: the `LeafArenaState`
response cache; `sigma` initialised to infinity (code uses 10.0); the named state machines
and `U_min`; the `escaped`/`B_max` valve; `1/k` query-level weighting; cosine-ordered query
selection. Add: judge Cohen's κ and `Δ_verbosity` (no `cohenKappa` symbol in `src/`;
"verbosity" appears once, as prompt text); temperature-scaling calibration.
**(e)** Framing matters. This is not a confession — it is the section that lets every other
claim in Chapter 3 be taken at face value. One paragraph, matter-of-fact.
**(f)** **Write new.** This section does not exist in the current thesis and is what makes
the cuts in Part III defensible rather than evasive.

### 3.3 Measurement discipline (2 pp)

**(a)** State four rules, each with the failure that produced it, so Chapter 5's negatives
are read against a standard the reader already holds.
**(b)** 2 pp.
**(c)** C3.14 A test that cannot fail is not a test. C3.15 Report a join's overlap before
its result. C3.16 Report a median with its IQR and claim only what the spread supports.
C3.17 A threshold derived for one quantity at one stage does not transfer.
**(d)** Each rule is **ARGUED**; each instance is **MEASURED**:
- C3.14: `TRACE_PRESENCE` has **no FAIL branch at all** (`EvalIngestValidator.kt:481`,
  `advisory = true` at `:487`) — a model with zero chain-of-thought is admitted. Six of the
  ten hardcoded exclusions are banned for exactly the condition it measures and refuses to
  act on (`reconciled-argument.md:631-638`). `measurement-discipline.md:12-48`.
- C3.15: mixed-group count was **0 of 613** before the fix and **97 of 613** after; the
  wrong "0 of 36 rescues" cost a reverted design change; the corrected join gives **3 in
  404** (`transferable-findings.md:124-157`). Also the id-space instance: `mmlu_pro.id` is
  not the eval `question_id`, and the numeric join produced a clean, wrong result — which
  is what collapsed law from 287 questions to 20 (`arena-math-findings.md:795-800`).
- C3.16: `SE(dJ)` spans 13.1x p10→p90 (`transferable-findings.md:48`); the CV rise
  14.3% → 15.7% is **mechanical from an additive mean shift** and must not be reported as
  degradation (`frozen-artifact.md:104-111`).
- C3.17: three instances — `separationEpsilon` across scales (~8.1° of angular tolerance at
  κ≈10–50 vs under **0.7°** at κ≈150–180), `proposalSeparationBar` (a LEVEL) vs
  `marginalEps` (a DIFFERENCE), and `tau = 1e-6` serving both a per-edit acceptance band
  and a per-iteration fixed-point tolerance (`transferable-findings.md:83-120`).
**(e)** These are rules the project adopted **after** violating them. Say so. A rule
presented as foresight is less credible than one presented with its scar.
**(f)** **Write new**, from `docs/measurement-discipline.md` and
`docs/transferable-findings.md`. Nothing in the current `.tex` corresponds to it.

---

## Chapter 4 — Experimental Design (9 pp)

### 4.1 Corpus, split, and the information-separation protocol (2 pp)

**(a)** Fix the corpus and the guarantee that makes "answer-key-blind" true.
**(c)** C4.1 MMLU-Pro, 12,000 questions, 14 domains. C4.2 A three-way construction /
tuning-validation / arena-test split. C4.3 No arena-test query is seen by any tuning gate.
**(d)** C4.1 **MEASURED**, corpus. C4.2 **partly ARGUED**: the intended 60/15/25 is *not*
what the runner does — its default is `testRatio = 0.3`, a 70/30 split, and the 15%
tuning-validation partition is enforced by scoring on construction-internal metrics rather
than as a materialised subsample. The current text already admits this at `5_Exp:117-126`;
**keep that admission**. C4.3 **MEASURED and audited**: `TaxonomyJudgeService.kt:161-163`
plus the build-failing `check{}` at `:172-180`.
**(e)** Two undisclosed details: `TaxonomyJudgeService.kt:157-159` additionally drops ~20%
of the induction pool by hash; and ~500 of 12,000 `mmlu_pro` rows (4.2%) have no eval link,
believed to be sentinel ids but **not confirmed** (`known-defects.md:81-87`). Report the
4.2% as unattributed.
**(f)** **Reuse** `5_Exp:79-134` and `:213-245` (the information-separation table) nearly
verbatim. **Correct** `\binom{12}{2}=66` → `\binom{11}{2}=55` at `:130`.

### 4.2 Two rosters, and the exclusion policy (2 pp)

**(a)** Specify the roster the reported run used and the roster the exclusion measurement
produced, without pretending they are the same.
**(c)** C4.4 The pilot roster is 8 models on Math; four had `model_output` stored as the
empty string across all 12,032 rows. C4.5 The corrected roster is the 11-model band, with
law coverage 287/287 and a 39.8-point accuracy spread. C4.6 Exclusion is enforced at roster
load by a hardcoded 10-name list that **throws**.
**(d)** C4.4 **MEASURED**, `arena-math-findings.md:477-491`. C4.5 **MEASURED**,
`reconciled-argument.md:143-186` (substantive-rate table) and `arena-math-findings.md:806`.
C4.6 **MEASURED**, `EvalIngestValidator.kt:312-338`, called from `validate()` at `:350`.
**(e)** The honest sentence, already drafted at `arena-math-findings.md:625-628`, adapted:
*response text was not persisted by the generation pipeline for four models, and three
further models emit a bare answer on more than a quarter of items; all are excluded, and the
format artifact is reported as the measurement that justifies the exclusion.* And the
limitation: `enforceNamedExclusions` is a **ratchet on known failures**, not a threshold —
it does not generalise to any new model (`reconciled-argument.md:631-638`).
**(f)** **Rewrite** `10_Appendix_ModelRoster.tex` into Appendix D and summarise here.
**Correct** every "12 models" to the appropriate roster (`5_Exp:100`, `:139`;
`6_Results:174,176`).

### 4.3 Conditions (1.5 pp)

**(a)** Reduce the condition set to the two arms that were actually run and that differ.
**(c)** C4.7 **C1 (MAIN)**: adapted partition, per-cell reference-informed rubric.
C4.8 **C3 (GENERIC_JUDGE)**: identical except the judge prompt is domain-agnostic.
C4.9 **C2 is cut** — it re-aggregates the C1 verdict set and answers only the deleted RQ2.
**(d)** C4.7/C4.8 **MEASURED** as run: 1736 verdicts per condition, complete overlap
(`arena-math-findings.md:158-165`). C4.9 **ARGUED from a MEASURED premise**:
`5_Exp:198-201` states C2 reuses the C1 verdict set; the question it answers was refuted at
its premise (`prereg_discriminative_power.md:171-181`).
**(e)** The precondition rule that came out of this and that belongs here rather than in
Results: **measure verdict agreement first**. It is one query and it decides whether an A/B
arm is worth 10,000 calls (`arena-math-findings.md:174-176`). C1 and C3 turned out to agree
on 99.4% of winners.
**(f)** **Rewrite** `5_Exp:161-212`. **Cut** the C2 row of Table `tab:arena-conditions` and
`:198-201`.

### 4.4 Pre-registration (2 pp)

**(a)** Reproduce, with dates, the decision rules and outcome bands that were fixed before
the data.
**(c)** C4.10 Three pre-registrations exist and each fixed its reading in advance.
**(d)** All **MEASURED as documents with commit dates**:
- `prereg_discriminative_power.md` — three outcomes named in advance (`:51-56`), and
  "observed rho is primary" fixed at `:38-42`. That rule is the only reason the conclusion
  was readable: the disattenuated column moves the **opposite** way and clips past 1.0
  (`:87-90`).
- `prereg_rubric_specificity.md` — four directional predictions with the confound direction
  named per measure (`:44-52`), and the within-arm thresholds at `:111-117` (evidence at
  median >= 0.05 with >= 75% of cells positive; no signal at <= 0.02).
- `prereg_arena_launch.md` — cost bands at `:17-19` with "no band is to be renegotiated
  after the number is seen" (`:21`), and the `<= 0.05` band at `:63`.
**(e)** One pre-registration is **stale and must be amended before it is quoted**:
`prereg_rubric_specificity.md:78-83` still says "Treatment arm only. No null. This is not
yet evidence." The null arm has since been run (`build/rubric_null/`, written 2026-07-27)
and was never written back. Amend the document, then reproduce it.
**(f)** **Write new** in the main text; full text in Appendix C. Nothing in the current
`.tex` corresponds.

### 4.5 Metrics and statistical protocol (1.5 pp)

**(a)** Fix what is reported and how, including the two statistics that were being reported
wrongly.
**(c)** C4.11 Primary metric for judge behaviour is **GT-agreement**, a per-verdict
proportion, not ρ. C4.12 BT θ, not win-rate. C4.13 Disattenuation is **two-sided**,
`ρ_obs / r`, not `ρ_obs / √r`. C4.14 Bootstrap CIs, with the true resample counts.
**(d)** C4.11 **ARGUED from a MEASURED constraint**: Spearman at n=8 is quantised in steps
of `6/(n(n²−1)) = 0.0119`, so it burns 1736 comparisons for one number, whereas GT-agreement
has n=1160 on the discriminable subset with SE ~1.5% (`arena-math-findings.md:150-154`,
`:272-275`). C4.12 **MEASURED**: win-rate manufactured a 5/0 sign-test result (p=0.031)
that BT θ erases (5/2/4, p=0.227) (`:178-188`). C4.13 **MEASURED correction**: both sides
are attenuated per-cell rankings, so `r_A = r_B = r` and the correction is `ρ_obs / r`
(`:926-932`). C4.14 **MEASURED**: 2000 resamples in `ValidationService.kt:68`, but **50**
in `TaxonomyRankingService.kt:764-834` and **1** in the in-run trajectory
(`TaxonomyBenchmarkService.kt:1246`) — `5_Exp:307-310`'s blanket "2,000" is wrong.
**(e)** The reliability constant `r = n/(n+7.66)` is **3.04x too large**: Spearman-Brown
applied after the fit (×0.50) compounded with roster dependence (×0.66), giving **c = 2.52**
at the 11-model band (`arena-math-findings.md:896-926`). Consequences invert — at a
40.8-query cell, observed median ρ = 0.823 corrects to 0.978 under 7.66 and to **0.874**
under 2.52 (`:934-940`). `tools/analysis/cell_fidelity_and_a3.py:140` still hardcodes 7.66.
Two further citation rules travel with whatever value is used: the bootstrap interval
`[7.52, 7.66]` from 20k resamples of **three points** must **not** be quoted as a confidence
interval, because it does not propagate sampling uncertainty in the split-half estimates
(`measurement-discipline.md:204-206`); and the curve was fitted on **ground-truth** rankings,
noise-free per question, so arena reliability at n queries will be **below** it — it is a
**ceiling, not a prediction**, the same status as the discriminative-power result
(`measurement-discipline.md:207-211`).
**(f)** **Rewrite** `5_Exp:287-313`. **Cut** the Cohen's κ and `Δ_verbosity` sentence at
`:296-297` (Part III, C5), and the "mean ± sd over the three seeds" convention at `:302`
(Part III, C9).

---

## Chapter 5 — Results (20 pp)

Ordering is load-bearing: **the judge first**. It is the strongest result in the project,
it is what a reader will remember, and it is what makes §5.2's nulls interpretable rather
than disappointing. A reader who learns in §5.1 that the judge decides on correctness
already knows why the rubric contrast in §5.2 is flat.

### 5.0 What was run (0.5 pp)

**(a)** Fix the scope of everything that follows.
**(c)** C5.0 One arena run: `experiment_configs/arena_math_frozen.toml`, snapshot
`20260727_042523`, 87 leaves, 87/87 rubrics, 8 models, 11 Math cells, 241 judged reserved
questions, 1736 verdicts per condition, MAIN vs GENERIC_JUDGE, seed 42 only.
**(d)** **MEASURED**, `arena-math-findings.md:1-7`; data at
`experiment_results/arena_math_frozen/` and `ratings.db` under snapshot
`20260727_042523_{MAIN,GENERIC_JUDGE}` (`:324-325`).
**(e)** Seed 42 only. Do not report a three-seed convention (Part III, C9).
**(f)** **Write new.**

### 5.1 What the judge does (12 pp) — **the centre**

#### 5.1.1 The judge decides on answer correctness (2 pp)

**(c)** C5.1 On items where exactly one response is correct and the judge did not tie, it
picks the correct one **88.8%** of the time (MAIN, 914/1029) and **88.4%** (GENERIC,
913/1033). The rubric moves it by 0.4 points. C5.2 The tie rate triples exactly where the
key stops discriminating: ~11% when one response is correct, **38.0%** when both are,
**33.1%** when neither.
**(d)** Both **MEASURED**: `arena-math-findings.md:17-20` and `:26-33`.
**(e)** C5.2 was **not part of the hypothesis** — say so; it is corroboration arriving from
a direction nobody was looking. And C5.1 is qualified by §5.1.5: half its support is
format-decided.
**(f)** **Write new.** `6_Results.tex` has no corresponding content — the entire chapter is
placeholders (11 placeholder boxes, 6 `TODO(author)` blocks).

#### 5.1.2 Fidelity depends on the key being available (2 pp)

**(c)** C5.3 On the 576 rows where correctness cannot discriminate, ρ falls
0.9762 → **0.7619** (MAIN) and 0.9524 → **0.7381** (GENERIC), while the tie fraction
triples 0.11 → 0.34. C5.4 **Selection control**: the blind subset preserves the true
ordering perfectly, ρ(GT_blind, GT_full) = **+1.000**, and GT accuracy spread falls only
3.5% — so the drop is judgment, not range restriction.
**(d)** Both **MEASURED**: `arena-math-findings.md:54-61` and `:63-69`. The control was
pre-registered.
**(e)** At n=8 the Spearman grid is 0.0119, so 0.9762 → 0.7619 is ~18 grid steps — not
quantisation noise (`:84-85`). But: 170 questions against 241, and the subset is
self-selected by model agreement; the control addresses ranking compression, not whether
these items are harder in ways that affect judging beyond correctness (`:87-90`).
**(f)** **Write new.**

#### 5.1.3 Reasoning text makes the judge worse at matching the key (2 pp)

**(c)** C5.5 GT-agreement is **highest** where neither response carries a trace (92.9%
MAIN, 94.7% GENERIC) and **lowest** where both do (84.2%, 82.5%) — an 8.7-point gap at
~2.7 SE, same shape in both conditions. C5.6 Corroborated independently by tie counts: 74
ties in the no-trace stratum against 17 in the mixed one.
**(d)** Both **MEASURED**: `arena-math-findings.md:98-108` and `:117-119`.
**(e)** This **inverts the design assumption**, and it is exactly what verification
predicts with the prose as a distraction. It was not part of the hypothesis (`:121-122`).
The result **survives and strengthens** the capture-gap qualification of §5.1.4 — see C5.9.
**(f)** **Write new.**

#### 5.1.4 A defect found by an independent route: the capture gap (2.5 pp)

**(c)** C5.7 Four of eight roster models had `model_output` stored as the empty string
across all 12,032 rows — a capture gap in the eval pipeline, not model behaviour; the judge
was shown a 600–1200-character worked solution on one side and a synthesised one-line stub
on the other. C5.8 The judge picks the side with text **99.4%** of the time (SE 0.3%),
against 87.6% GT-correctness for that side — an excess preference of +11.8 pp. **Mixed
pairs were 868/1736 = 50% of all comparisons.** C5.9 **What survives**: at matched
capability gap (<20 pp) the inversion of §5.1.3 **strengthens** — bare-letter pairs 97.0%
against reasoning pairs 83.2%, a 13.8-point gap with capability controlled.
**(d)** All **MEASURED**: `arena-math-findings.md:468-495`, `:501-511`, `:529-539`.
**(e)** What this qualifies, stated plainly and immediately: the 88.8% aggregate (half its
support is format-decided), ρ = 0.95–0.98 (ranking all four traced models above all four
bare ones reproduces the GT top-4/bottom-4 split for free), and ρ_blind = 0.74–0.76
(`:514-522`). Unaffected: everything that uses ground-truth accuracy only and never touches
a verdict (`:546-547`).
**(f)** **Write new.** This is the section that demonstrates the measurement apparatus
catching its own error: the defect was found *while sizing the roster for a different
experiment* (`:470`).

#### 5.1.5 The two judges reach the same verdict (1.5 pp)

**(c)** C5.10 On identical (question, model-pair) comparisons with complete overlap:
identical verdict 1529/1736 = 88.1%; 207 disagreements of which 197 (95%) involve a TIE on
one side; **actual winner flips: 10 of 1736 = 99.4% agreement**. C5.11 The rubric **is**
read: rationale–rubric lexical overlap is 0.200 (IQR [0.115, 0.280]) under the rubric judge
against 0.138 (IQR [0.077, 0.200]) from a judge that never sees it — 45% above baseline
with offset IQRs.
**(d)** Both **MEASURED**: `arena-math-findings.md:158-165`, `:196-202`.
**(e)** **Rationale-conditioned, not rationale-driven**: for "applies the criteria and
coincidentally agrees" to hold, criteria-guided and criteria-free judges would have to reach
identical winners on 1726 of 1736 comparisons (`:204-208`). The simpler reading is that the
verdict is fixed before the rubric enters. **So the per-cell null is not evidence of parity
— it is a comparison whose arms barely differ**, and no amount of power fixes that
(`:169-173`). Caveat: lexical overlap shows **reproduction**, not **application**; the
rule-ID citation scheme would settle it and changes the verdict schema (`:212-216`).
**(f)** **Write new.**

#### 5.1.6 Cost, and what the arena can afford (1 pp)

**(c)** C5.12 Identification is reached at 7 pairs of 28 — a spanning tree, as predicted —
at 32.9 to 45 comparisons per cell, and **the cost varies across cells**, which clears the
void condition the pre-registration named. C5.13 The minimum sits in the pre-registered
`<= 40` band, so leaf-level judging is affordable: ~2,900–3,900 calls for 87 cells against
a ~10,000 budget.
**(d)** Both **MEASURED**: `arena-math-findings.md:341-348`; band fixed in advance at
`prereg_arena_launch.md:17-21`, with the void condition ("if the new number is also
constant, the scheduler is still capping") at `:33-35`.
**(e)** Measured at 8 models. At 11 models it is 55 pairs and the arithmetic was not redone
(`reconciled-argument.md:1200-1202`).
**(f)** **Write new.** **Cut** `5_Exp:148-159`'s "theoretical judge-call ceiling of 2,640ℓ"
down to one sentence — it is an upper bound for rate-limit provisioning and nothing depends
on it.

#### 5.1.7 What §5.1 establishes, and what it costs (1 pp)

**(c)** C5.14 The composite claim: the judge **decides on answer correctness**, **reads**
the leaf-specific rubric, **reproduces its vocabulary** in the justification, and **reaches
the same verdict as a rubric-free judge**; when correctness cannot discriminate, the tie
rate triples. Each component has a control that shares every confound except the treatment.
C5.15 Therefore: **on a multiple-choice corpus with a verifiable key, a capable judge can
shortcut to correctness and bypass the partition entirely.**
**(d)** C5.14 **MEASURED**, `arena-math-findings.md:35-46`. C5.15 **ARGUED** from
C5.1–C5.11, `:134-141`.
**(e)** C5.15 is an inference from a Math pilot at n=8 with a known format artifact. It is
a hypothesis with strong support, not a demonstration; the demonstration is the
options-blind arm, which has not been run (Part V).
**(f)** **Write new.**

### 5.2 What the partition does (7 pp)

#### 5.2.1 Link 1: the construction meets its requirements (1.5 pp)

**(c)** C5.16 The frozen artifact: 154 nodes, 87 leaves, maxDepth 6, J = 0.253129, mass
8299.00 conserved, 87/87 leaves labelled and carrying rubrics. C5.17 Certified fixed point
at iteration 10. C5.18 The z-gate is **stability-neutral and J-neutral**, and both were
measured rather than assumed.
**(d)** C5.16, C5.17 **MEASURED**, `frozen-artifact.md:9-19`, `:27-39`. C5.18 **MEASURED,
and both results are negative**: stability tightening did not occur — the gate's effect is
an additive ~4.4-leaf offset, `corr(reduction, seed deviation) = +0.006`, variance ratio
1.05 against F(4,4) critical 6.39; and J is not higher — 2 of 5 seeds, sign test p = 0.812,
median dJ −0.0001 (`frozen-artifact.md:102-114`).
**(e)** The defensible sentence, and it is more transferable than "the gate helped" would
have been: *a gate can be right because its units are right, without improving the number
it gates* (`frozen-artifact.md:115-117`). Also: the five-seed sweep's leaf counts are
pre-`c381211` and **void as to values** (`void-results.md:21`) — the *analysis design and
its two negative results* survive, the underlying counts need re-deriving.
**(f)** **Write new**, ~1.5 pp, replacing `6_Results.tex:14-115` (the DQ1 section, 101
lines of placeholders).

#### 5.2.2 Link 2: rubric specificity, against a randomised null (1.5 pp)

**(c)** C5.19 Rubrics induced on coherent cells are specific to their cells; rubrics induced
on size-matched random cells from the same corpus are not. Mann-Whitney U, one-sided,
87 leaf rubrics vs 13 random cells: **p = 1.21e-6**; medians 0.138 vs 0.012. C5.20 All four
pre-registered discriminators fire in the predicted directions. C5.21 The random arm's
0.012 falls inside the `<= 0.05` band fixed **in advance** as meaning "coherence IS the
cause".
**(d)** All **MEASURED**: `build/rubric_null/measures_all.json`, recomputed and reproduced
to three significant figures at `reconciled-argument.md:99-111`; robust across all three
`Q_i` definitions (1.2e-6 / 2.1e-6 / 7.6e-6). Discriminator table at `:116-121`: pairwise
Jaccard 0.0754 vs 0.1187 (leaf lower, as predicted); terms in >=90% of rubrics **0** vs
**6** (leaf ~0 and random > 0, as predicted); cells with positive specificity 81/87 (93%)
vs 7/13. Bands at `prereg_rubric_specificity.md:111-117`, `prereg_arena_launch.md:63`.
n-matched control: 13 leaf rubrics subsampled give 0.134, a 200-draw bootstrap gives 0.138
(`reconciled-argument.md:124-126`).
**(e)** Three caveats, all of which must travel with it: (i) the measure is **lexical
throughout** — it shows **reproduction** of cell vocabulary, not **application** of
criteria; (ii) the treatment bundles coherent membership with an informative topical label,
and the null cells are labelled `Cluster NN` by deliberate choice
(`rubric_specificity_null.py:157-161`), so the claim is really "coherent cell + its label
causes specificity"; (iii) 13 random cells against 87 leaves — the null arm is small.
**(f)** **Write new.** **Work required before citation**: the supporting artifacts
(`tools/analysis/rubric_specificity_null.py`, `src/test/kotlin/taxonomy/RandomCellRubricNullHarness.kt`)
are **untracked in git**. A result whose artifacts are untracked is one `git clean` from
being unsupported.

#### 5.2.3 Link 3's premise fails, and it was pre-registered (2 pp)

**(c)** C5.22 Observed Spearman between cells is **flat** across an 11x change in
granularity: 0.929 (14 domains, 91 pairs) / 0.922 (88 leaves, 3828) / 0.922 (87 leaves,
3741) / 0.905 (152 leaves, 11476), with overlapping IQRs. C5.23 Flat across **routers**
too: a routing correction worth +10.3% J changes discriminative power by zero. C5.24
Centring out each model's global mean leaves residuals of −0.119 / −0.024 / −0.024 / −0.024,
all within 1.5–3.6x of the **mechanical centring null** `−1/(C−1)`.
**(d)** All **MEASURED**, run after the pre-registration was fixed:
`prereg_discriminative_power.md:74-79`, `:92-97`, `:139-148`. Join exact, 11769/11769; all
8 roster models present in every cell of every tree; 0 cells dropped.
**(e)** Three bounds, all pre-registered: (i) **power, not proof** — per-model per-cell
accuracy has SE ~2.1 pp at 14 domains, 5.8 pp at 87 leaves, 6.9 pp at 152, so the null is
consistent with "no cell-specific signal" *and* with "a signal below ~6 pp at leaf
granularity" (`:150-169`); (ii) **roster** — 54.1 accuracy points of spread, so ρ ≈ 0.92 was
largely measuring "gpt-4o beats Llama-2-13b in every cell", and a roster within ~10 points
is untested and is the version that could still come out positive (`:113-114`); (iii)
**ceiling, not prediction** — measured on each cell's own constituent queries and on
ground-truth accuracy, never on routed held-out queries and never on verdicts (`:125-131`).
**(f)** **Write new.** This replaces the whole of `6_Results.tex:126-160` (RQ2 section) and
`7_Discussion.tex:10`. The pre-registered "observed rho is primary" rule
(`prereg_discriminative_power.md:38-42`) must be quoted here: the disattenuated column
moves the **opposite** way and clips past 1.0, so leading with it would have given the
opposite conclusion from the correction's arithmetic rather than from the data.

#### 5.2.4 The domain screen, and its two reversals (1.5 pp)

**(c)** C5.25 At the 11-model band: **law** n=287, ρ=0.955, **p=0.008**; **math** n=393,
ρ=**1.000**, p=1.000 — the band's models order identically in Math as they do globally, so
an arena there has nothing to detect. C5.26 The conclusion **reversed twice** before
settling, and both reversals had the same cause.
**(d)** C5.25 **MEASURED**, `arena-math-findings.md:802-816`, 1500-draw size-matched
permutation null, seed 42, under two roster policies. C5.26 **MEASURED**: at 8 models Math
looked indistinguishable from a random subset (p=0.217, `:435`) and the recommendation was
law; at 37 models Math became significant (p=0.001, `:745`) and the recommendation flipped;
that flip rested on an intersection poisoned by one id-space-mismatched model, which
collapsed law from 287 questions to 20 (`:795-800`).
**(e)** The lesson, and it is the most instructive methodological result in the project:
**both inversions came from evaluating a ranking statistic at a model count that did not
match the decision it was informing** (`:826-835`). The screen must be computed at the
roster the arena will actually use. **Report the reversals; they are the finding.**
Second caveat: both screens use MMLU-Pro's native category labels, not induced cells — they
**bound** what a partition could show, they do not show that induced cells separate
(`:461-464`, `:770-777`).
**(f)** **Write new.**

#### 5.2.5 Polyhierarchy: a measured negative (1.5 pp)

**(c)** C5.27 A cross-link operator was built, measured, and retired. Across 42 cross-link
proposals the capture fraction the operator uses to rank candidates was **uncorrelated**
with the objective it must satisfy: r(f, ΔJ) = **+0.085**, with complete distributional
overlap between accepted and rejected proposals (median f 0.802 accepted vs 0.818
rejected). Median ΔJ was 6.9e-5 for cross-links against 5.3e-4 for splits — an order of
magnitude apart. C5.28 The structural reason: **a partition objective is indifferent to
polyhierarchy**, so no threshold on such an objective can separate good cross-links from
bad ones. C5.29 The cost is named: the multi-leaf rate of held-out queries was 0.1549 with
cross-links and 0.1518 without, so the **query**-level multi-membership claim survives; what
is given up is the **concept**-level claim.
**(d)** All **MEASURED**, `7_Discussion.tex:61-92`.
**(e)** None needed — this section already states its own bound.
**(f)** **REUSE `7_Discussion.tex:21-110` NEARLY VERBATIM.** This is the best-written
section in the current thesis and it is the template for every negative in this plan:
*operator stated → measurement shown → structural reason given → decision recorded → cost of
the decision named → replacement invariant stated*. Move the scoring formula at `:46-51` to
Appendix A; keep everything else.

### 5.3 Chapter summary (0.5 pp)

**(a)** State, for each pre-specified criterion, whether it was met, at what effect size,
with what interval. No interpretation.
**(f)** **Reuse** the intent of the `TODO(author)` at `6_Results.tex:272-279`, reordered:
judge first, partition second.

---

## Chapter 6 — Discussion and Conclusion (11 pp)

### 6.1 Where the architecture binds (2 pp)

**(c)** C6.1 MMLU-Pro is multiple-choice with a verifiable key, so a capable judge can
shortcut to correctness and bypass the partition. The architecture can only bind where
correctness is **not** checkable — open-ended generation, agent traces, tasks with no key.
C6.2 MMLU-Pro grounds the comparison **and** is simultaneously the corpus where the judging
mechanism can bypass what the comparison is about. Both are true, and stating them together
is the thesis's most defensible sentence.
**(d)** C6.1 **ARGUED from §5.1**, `arena-math-findings.md:134-141`. It was always the
motivation; it is now the **measured** argument for it rather than a preamble.
**(e)** An inference from a pilot, not a demonstration. Name the demonstration:
options-blind (Part V).
**(f)** **Write new.**

### 6.2 What each negative means, link by link (2 pp)

**(c)** C6.3 "Cells do not have different true rankings" lands on link 3's **premise**;
"the rubric does not change the verdict" lands on link 3's **mechanism**; neither touches
links 1 or 2, which both came out positive. C6.4 A null under a pre-registered rule is a
finding; a null under a rule chosen afterwards is a shrug.
**(d)** C6.3 **ARGUED**, from §5.2.2 (positive), §5.2.3 (premise), §5.1.5 (mechanism).
C6.4 **ARGUED**, supported by the three dated pre-registrations of §4.4.
**(e)** Do not let a reader collapse "cells do not have different true rankings" into "the
taxonomy does not help the arena". The first is a property of MMLU-Pro's saturation for a
54-point-spread roster; the second is a claim about judge quality that this measurement
does not touch (`prereg_discriminative_power.md:192-196`).
**(f)** **Write new**, replacing `7_Discussion.tex:8-20`.

### 6.3 The apparatus caught its own errors (2 pp) — **the credibility argument**

**(c)** C6.5 Four errors were found by routes that were not looking for them: (i) the trace
capture gap, found while sizing the roster for a *different* experiment; (ii) the
`reason_code` side-channel in `arx_3`/`arx_0314`, found by a format check whose only
anomalous column was **newline count** (median 0 against 8–24 everywhere else) and which
predicts correctness at A → 83.2% / C → 36.5%; (iii) the reliability constant, caught twice
by two independent routes — a roster-size re-fit and a units check on the split-half length
mismatch — that compounded to the same 3.04x; (iv) the domain screen's two reversals, both
tracing to one cause.
**(d)** All **MEASURED**: `arena-math-findings.md:470`, `:637-662`, `:918-925`, `:826-835`.
**(e)** None of these was found by looking for it. That is the point: they are the strongest
available evidence that the results the apparatus did *not* overturn are sound.
**(f)** **Write new.**

### 6.4 Threats to validity, limitations, and the standing measurement debt (3 pp)

**(c)** C6.6 Every Bradley–Terry standard error reported before commit `a92a3ed` was the
clamp constant, not a measurement; correct values are 44–209x larger. C6.7 The reliability
constant was 3.04x too large and the disattenuation was one-sided when it should have been
two-sided. C6.8 The redundancy percentages ("72.2% redundant, 42.2% saturated") could not be
reproduced under either reading and are **unresolved** — do not restate them. C6.9 Comparisons
are not independent given the BT parameters; the Fisher SEs understate uncertainty. C6.10
`enforceNamedExclusions` is a ratchet on known failures, not a general guard.
**(d)** C6.6 **MEASURED**, commit `a92a3ed` message with the K=8/K=12 SE table. C6.7
**MEASURED**, `arena-math-findings.md:896-932`. C6.8 **NOT REPRODUCIBLE** — state it as
such. C6.9 **ARGUED**, and already correctly stated at `4_Methodology.tex:259-262`,
`:271-275`. C6.10 **MEASURED**, `EvalIngestValidator.kt:161`, `:477-491`.
**(e)** C6.6 and C6.7 are errors this thesis found in its own published numbers. Present
them under §6.3's frame, not apologetically — but do present the corrected values, and do
not report any CI that has not been recomputed post-`a92a3ed`.
**(f)** **Reuse** `7_Discussion.tex:112-237` as the skeleton for internal / external /
construct validity. **Cut** the `Δ_verbosity` and Cohen's κ limitations (they were never
measured, so they are not limitations — they are absences, and they belong in §3.2.5).

### 6.5 Conclusion (1.5 pp)

**(c)** C6.11 Restate the four contributions of §1.4 as *what was demonstrated*. C6.12 Say
plainly what the selected-domain scope does and does not license.
**(d)** Back-references only; no new claims.
**(f)** **Write new**, following the `TODO(author)` at `8_Conclusion.tex:5-10` but with the
research questions as reworded in §1.3.

### 6.6 Future work (0.5 pp)

**(c)** C6.13 Named, in priority order: (1) the **rule-ID citation scheme** in the verdict
schema — it distinguishes reproduction from application and counts prior-decided verdicts,
and it must precede any further arena run because it changes the schema; (2) the
**options-blind arm** on the same 241 questions, with its predictions already fixed in
writing; (3) the **law arena** on the 11-model band; (4) a roster clustered within ~10
accuracy points, which is the version of the granularity question that could still come out
positive; (5) generalisation to all 14 domains at matched power.
**(d)** (1) and (2) **ARGUED from MEASURED results**, `arena-math-findings.md:250-256`,
`:296-319`. (3) **MEASURED recommendation**, `:833-835`. (4) `prereg_discriminative_power.md:113-114`.
**(e)** (2) is **blocked**: without options *and* without stored reasoning, four of eight
models present a bare letter, so `no-trace × no-trace` would be uninterpretable rather than
a chance-level null (`arena-math-findings.md:549-558`). It needs the trace-complete roster
first.
**(f)** **Reuse** the item list in `8_Conclusion.tex:14-22`, reordered and extended.

---

# Part II — The appendices

## Appendix A — Taxonomy construction formalism (18 pp)

**(a)** Carry the full construction: routing, splitting, acceptance, coarsening, the
fixed-point certificate, and every parameter derivation. This is where the thirty pages
that §3.1 does not spend actually go.
**(b)** 18 pp.
**(f)** **Reuse** `11_Appendix_DAGConstructionFormalism.tex` (682 lines) as the base, but it
needs a careful correction pass before it can ship — the reconciliation found that it
**describes three mechanisms the code removed and omits four the code has**.

**Corrections required, each MEASURED against code:**

| `11_App` | current text | correct | citation |
|---|---|---|---|
| `:576-577` | joint k-way separation gate on the routed partition | **removed**; `sepScore` is computed (`:416`) and persisted (`:419`) but never compared to anything | `TaxonomySplitter.kt:462-474` deleted |
| `:577-578` | doubled `2·ε_sep` bar on small populations | **removed**; flat assignment. Logs: `bar=0.0500` appears **0** times, `bar=0.0250` 5628 times | `TaxonomySplitter.kt:324-332`; `known-defects.md:94-99` |
| `:578-580`, `:120` | per-child sibling distinctness post-condition | **removed, and it was vacuous** — it iterated `node.children` while the function returns unless `node.isLeaf` | `TaxonomySplitter.kt:480-489` deleted |
| absent | min-pair separation gate over all child pairs | **add** | `TaxonomySplitter.kt:433-441` |
| absent | two coarsening moves: floor-absorption and weak-pair merge at `requiredEps` | **add** | `:347-356`, `:357-385` |
| absent | k-fallback over `k ∈ 2..maxK` taking the first acceptance | **add** | `TaxonomyOperations.kt:212-220` |
| absent | ESS pre-gate `ess = mass²/Σw² >= 2·minClusterSize` | **add** — appears in no document at all | `TaxonomySplitter.kt:68-70` |
| `:616-624` | acceptance is lexicographic: `(dJ > τ) or (\|dJ\| <= τ and d\|V\| < 0)` | that is the `acceptanceZ == 0` **legacy** arm. The frozen rule is `dJ > max(τ, 2.0·SE_paired(dJ))`, one-sided, with `SE` a paired Dirichlet bootstrap over 200 replicates, fixed seed 987654321, resampling only queries whose cell assignment changed | `TaxonomyOperations.kt:55-69`, `:600-601`, `:710`; `JBootstrap.kt:101-119` |
| `:582` vs `:619` | `:582` says the split veto is `dJ > 0`, `:619` says `dJ > τ` | the appendix contradicts itself and the code is neither | — |
| `:477-478` | path cutoff `1e-4`, applied per path | **`ln(1e-30)`**, applied to a node's **summed** posterior after all incoming edges | `TaxonomyTrickler.kt:90`, `:332-341` |
| `:433` | descent gate states only `δ >= 0` | the gate is **clamped at zero** (`.coerceAtLeast(0.0)`), so any node with `r̄_v < 0.12` gets a bar of 0 and the parent's own dot drops out of the inequality | `TaxonomyTrickler.kt:190` |
| `:452-453` | "the query is retained as residual mass at v" | a residual is recorded only under `enableResidualRouting && depth >= 1 && !readOnly`; at depth 0 and on **every read-only held-out route** — the arena's routing path — the residual is dropped | `TaxonomyTrickler.kt:192-198` |
| `:482` | membership share denominator is over leaves | `TrickleResult.leaves()` filters on `isLeaf \|\| enableResidual`, and with residual routing on (the `DAG_MAX` default) it filters nothing — the denominator includes internal nodes | `TaxonomyTrickler.kt:65-68`, `:363-386` |
| `:314-321` | `ρ = d/n = 256/30 ≈ 8.5`, hence `α ≈ 0.82`, hence "leaf size is a calibrated parameter" | at the real frozen `n_min = 55`, `ρ = 4.65` and `α = 0.33`. **The passage's conclusion does not survive its own corrected input** and must be rewritten, not just renumbered | `reconciled-argument.md:393-399` |
| `:385-386`, `:591` | `n_min = 30`; `separationBar = 0.02` | **55**; **0.025** | `freeze_mcs55.toml:99`, `:100` |
| `:234` | uses the label "**C3**" for a construction invariant (residual-flagging) | **rename.** It collides with arena condition C3 (`5_Exp:190-193`), which is the generic-judge arm and is cited throughout Chapter 5 | naming collision, found in the `.tex` inventory |
| `:187` | defines `Δρ` as the primary RQ2 metric | **cut** with RQ2 (Part III, C2) | `reframed-argument.md:26-46` |

**Also add to Appendix A:**
- Transferable finding 1 — cross-node comparison in a hierarchical vMF model must use a
  **shared concentration**. General form plus both instances: the trickler's sibling
  competition (four ground-truth domains killed) and the splitter's routing-sustainability
  check at `c381211` (not-routing-sustainable rejections 750 → 42, −94%; leaves 84 → 152;
  J +20.4%, or +10.3% at matched granularity). Corollary: comparing *levels* by density is
  worse than comparing siblings, because κ's n-dependent shrinkage `(n−1)/(n+d−2)` makes
  parents always look sharper — measured, **56%** of the corpus mis-residualised at anchors
  under a density descent gate. `transferable-findings.md:10-37`.
- The polyhierarchy operator's scoring formula, moved from `7_Discussion.tex:46-51`.
- `κ̄` is **not inert**. `router-shared-kappa-correction.md:28-30` says it "cannot change
  the argmax — retained only so the two call sites read identically". True of the argmax,
  false of the output: `TaxonomyTrickler.kt:219-223` exponentiates these scores into
  per-level transition probabilities, so `κ̄` is the **inverse temperature** of the level
  softmax and directly scales the mass that must clear `membershipFloor`. The system's
  effective routing temperature is data-derived, not a parameter.

**Caveat that bounds Appendix A as a whole:** `TaxonomyTrickler.kt:23-26` (KDoc) and
`TaxonomyConfig.kt:139-142` both describe the beam as a *multiplicative responsibility
ratio*, with a worked example the implemented additive-cosine rule does not have. The file
disagrees with itself 180 lines apart. **Fix the KDoc before anyone quotes it into the
thesis.**

## Appendix B — Tuning protocol, numerics, and metric definitions (14 pp)

**(a)** The hyperparameter table with provenance, the ablation matrix, the numerical
methods, and the definitions of the metrics that are still reported.
**(b)** 14 pp.
**(f)** **Merge** `7_Appendix_TuningProtocol.tex` (267 lines) + `12_Appendix_Numerics.tex`
(151) + `9_Appendix_MetricDefinitions.tex` (142), then cut.

**Required corrections and cuts:**
- `12_App:137-139` documents the **`− 1/K`** variance correction. It is **`− 1/K²`**. Fix
  the appendix to match commit `a92a3ed`, and add the derivation from that commit message:
  `F_c = F + J` with `J = K·P`, `P = 11ᵀ/K`, so `F_c·1 = K·1` and
  `F_c⁻¹ = F⁺ + J/K²`. State the consequence explicitly: SEs reported before the fix were
  the clamp constant.
- `12_App:115-151` (Fisher information) is otherwise **CONFIRMED** against
  `BtMmFitter.kt:355-372` and `:313-343`. Keep it; it is one of the accurate parts of the
  report. Add the hard SE floor of 0.01 (`BtMmFitter.kt:431`), which `12_App:148-149`
  records but `4_Methodology.tex` does not.
- `7_App:18` says `minClusterSize = 30`, which matches **nothing in the repository**
  (config default 25, `application.yml` 25, frozen run **55**). `7_App:19` says
  `separationBar = 0.02`, the stale YAML value, not the frozen run's **0.025**.
- `7_App` has **no `acceptanceZ` row**, despite `frozen-artifact.md:89-117` devoting a whole
  section to justifying its value. **Add the row.**
- `7_App:27` says `numIterations = 50` and `:142` says 35. Pick one; and record that the
  frozen run converged at iteration **10**.
- `7_App:71-79` narrates a tunable `routingSoftmaxTau` as the selection protocol. That
  symbol has **zero occurrences in `src/`**. **Cut.**
- `7_App:120`'s gate `Routing ECE <= 0.25` is meaningful and was passed (0.2114) — but see
  the routing-ECE disposition below before keeping it.
- `9_App`: **cut** the definitions of Dendrogram Purity (`:102-118`), Weighted Leaf Purity
  (`:85-101`), Total Dasgupta Cost (`:34-57`) and Normalised Sackin Index (`:58-70`) — the
  DQ1 baseline runs that consume them do not exist and the metrics bear on none of the three
  links. **Keep** Spherical Silhouette (`:12-33`) only if §3.1's coherence requirement cites
  it; **keep** Average Match Count (`:71-84`).
- `9_App:119-142` (Routing ECE): the metric is **implemented and exported**, contradicting
  `known-defects.md:63-66` which says it has never been measured. Binned Guo-style ECE at
  `AdditionalMetrics.kt:172-216`; the frozen run exported **0.2114**
  (`experiment_results/freeze_mcs55/seed_42/validation/MAIN_routing_calibration.csv`).
  **But the exported number is not the metric the appendix defines**: `9_App:123-128` sums
  leaf membership onto domain ancestors, which is what `TaxonomyMetrics.kt:221-225` does,
  while the exported path takes `list.maxOf { it.second }` per domain
  (`BatchTrickleEvaluator.kt:195-196`). A max over leaves is not a distribution. **Disposition:
  demote routing ECE to a one-paragraph routing diagnostic in Appendix B, state that the
  exported aggregation is mis-specified, and either fix `BatchTrickleEvaluator.kt:196` and
  re-run or report the number with the discrepancy named. Do not make it a headline.**
  Amend `known-defects.md:63-66`, which is currently wrong in a way that would have caused
  the thesis to omit a metric it actually has.
- `9_App:138-140` invokes temperature-scaling calibration. Not implemented anywhere in
  `src/`. **Cut.**
- `8_Appendix_JudgeGeneration.tex:9-11` says rubric pack size `k = 5`. It is **25**
  (`TaxonomyJudgeService.kt:203`), which `prereg_rubric_specificity.md:33-35` also says.
  Fold this 41-line appendix into Appendix B rather than keeping a fifth appendix; keep the
  MapReduce procedure (**CONFIRMED** against `TaxonomyJudgeService.kt:212-253` and
  `JudgePrompts.kt:46-164`) and the build-failing hold-out audit.
- `7_App:179-227` (ablation matrix): keep only the rows with data. `marginalEps = 0` was
  measured and **rejected** — 83 leaves, J 0.230247 (`transferable-findings.md:107-109`).
  The maxK plateau and the k-fallback figures are **void as to values**
  (`void-results.md:19-20`); the qualitative finding (maxK was a structural determinant
  before the fallback) stands.
- `7_App:228-266` (optional secondary diagnostics: random-scheduler ablation C4, verbosity
  probe): **cut both.** Neither was run.

## Appendix C — Pre-registrations, reproduced with dates (8 pp)

**(a)** Reproduce the three pre-registration documents in full, with their commit dates, so
the reader can verify that every decision rule and outcome band predates its data.
**(b)** 8 pp.
**(c)** Contents, in order: `prereg_discriminative_power.md` (the three named outcomes at
`:51-56`; "observed rho is primary" at `:38-42`; the reporting rules at `:36-47`);
`prereg_rubric_specificity.md` (the four directional predictions with the confound direction
named per measure at `:44-52`; the amendment identifying measure 4's vocabulary-size
confound at `:87-99`; the within-arm thresholds at `:111-117`);
`prereg_arena_launch.md` (the cost bands at `:17-19` with "no band is to be renegotiated
after the number is seen" at `:21`; the two smoke-run checks that must **fire** at `:37-54`;
what a PARTIAL result would mean, at `:55-66`).
**(d)** All **MEASURED as artifacts** — they exist as dated commits.
**(e)** Three things must happen before this appendix is written. (0) **The two band sets
must be disambiguated.** `prereg_arena_launch.md:58-59` states the bands as
"<= 0.05 causal, >= 0.10 refuted, between = partial", while
`prereg_rubric_specificity.md:113-117` fixes "evidence at median >= 0.05 **and** >= 75% of
cells positive; inconclusive in (0.02, 0.05); no signal <= 0.02". These appear to describe
different quantities — the random-cell arm's absolute overlap versus the within-arm
specificity — but the documents do not say so. §5.2.2 cites both. Resolve which band
applies to which statistic **before** either is quoted, or the pre-registration's authority
is undercut by its own ambiguity. (i)
`prereg_rubric_specificity.md:78-83` is **stale** — it still says "Treatment arm only. No
null. This is not yet evidence." The null arm ran on 2026-07-27 and was never written back.
Amend it before reproducing it. (ii) The options-blind predictions at
`arena-math-findings.md:296-319` — including the **second possibility** for `trace × trace`
("landing near 84% unchanged would mean the judge was never using the key on traced pairs,
so the 88.8% aggregate is carried entirely by the untraced and mixed strata") — belong here
verbatim. Writing down the alternative outcome in advance, in a document with a commit date,
is the most defensible thing in this project.
**(f)** **Write new.** Nothing in the current `.tex` corresponds.

## Appendix D — Model roster and exclusion policy (4 pp)

**(a)** Both rosters, and the exclusion policy presented as a measurement.
**(b)** 4 pp.
**(c)** D1 The pilot roster (8 models, as run) with response format and Math GT accuracy.
D2 The corrected roster (11 models) with substantive-response rate. D3 The exclusion table:
10 named models with the measured reason for each. D4 The judge model, and the fact that it
appears nowhere in either roster — so there is no self-preference confound.
**(d)** D1 **MEASURED**, `arena-math-findings.md:477-484`. D2 **MEASURED**,
`reconciled-argument.md:148-162` — 11 of 12 at >= 99.8% substantive; only
`gemini-1.5-pro-002` banned, at 64.6% substantive (i.e. 35.4% bare), which matches its
recorded reason exactly. D3 **MEASURED**, `EvalIngestValidator.kt:312-329`, ten rows with
reasons: one id-space mismatch, six traceless archives, three mixed-format models. D4
**UNVERIFIED — see Part VI.**
**(e)** Two notes that must appear. (i) `Meta-Llama-3_1-70B-Instruct` (in the roster) is
**not** the banned `Meta-Llama-3-70B-Instruct` (`EvalIngestValidator.kt:313`); they are
different models and the roster's is clean. (ii) Six of the ten exclusions are for exactly
the condition `TRACE_PRESENCE` measures and refuses to act on — so the trace confound is
excluded by a curated string list, not by a threshold, and **it does not generalise to any
new model**. State that plainly rather than presenting the validator as solved. The general
guard (a FAIL branch on `TRACE_PRESENCE` at, say, 0.90) is future work with a one-line
implementation.
**(f)** **Rewrite** `10_Appendix_ModelRoster.tex` (35 lines) entirely; it loses its three
"12"s and gains a second table.

---

# Part III — The cut list

Reclaimed pages use the ~38 tex-lines-per-page estimate of §0.1.

| # | cut | reason | citation | pp reclaimed |
|---|---|---|---|---:|
| C1 | **The taxonomy-construction literature survey**, `2_Literature.tex:155-412` — **cut selectively, not wholesale** (revised; see below) | No gold taxonomy exists for MMLU-Pro, the supervised HTC baselines were removed as unimplemented (`5_Exp:246-256`), and reference-dependent metrics were dropped (`:281-285`). But three of the seven subsections are consumed downstream. | `5_Exp:246-256`, `:281-285` | **4.5** |
| C2 | **RQ2 as currently worded and every `Δτ` between adapted and canonical**: `1_Intro:301-307`, `4_Meth:192-204`, `5_Exp:31-36` (RQ2 row), `:98`, `:166`, `:188`, `:200`, `6_Results:126-160`, `7_Disc:10`, `11_App:187` (which defines `Δρ` as the primary RQ2 metric), `7_App:91`, `3_Arch:245` | Refuted at its premise, under pre-registration, **before the arena ran**. A per-cell `Δτ` measures a difference with no room to exist, so a null there is uninformative about the mechanism. Replaced by "does adapted grouping enable better judging?" | `reframed-argument.md:26-46`; `prereg_discriminative_power.md:171-181` | **2.0** |
| C3 | **Condition C2** (canonical re-aggregation): `5_Exp:185-189`, `:198-201` | It re-aggregates the C1 verdict set — it shares its whole verdict set with C1 and therefore cannot isolate anything — and it answers only the deleted RQ2. | `5_Exp:198-201` | **0.5** |
| C4 | **The DQ1 baseline table and its five-metric vocabulary**: `5_Exp:38-44`, `:246-285`, `:289-292`; `6_Results:35-115`; `9_App:34-118` | The *k*-means / HAC / random-null runs **do not exist**, and none of the six metrics bears on any of the three links. Replaced by one paragraph in §5.2.1 reporting the certificate and the separation nulls. | `6_Results:44-46` ("the baseline runs required to decide it have not yet been executed") | **3.3** main + 2.2 app |
| C5 | **Judge Cohen's κ and `Δ_verbosity`**: `5_Exp:296-297`; `6_Results:222-228`; `7_App:254-266` | No implementation exists — no `cohenKappa` symbol in `src/`, and "verbosity" appears once, as prompt text (`TaxonomyArenaService.kt:904`). Replaced by what *is* measured: dual-call agreement rate, tie rate by stratum, and the format analysis that produced the 99.4% result. | `reconciled-argument.md:266` (row AU) | **0.9** |
| C6 | **The state-machine arena description**: `3_System_Architecture.tex:365-460` (96 lines) incl. the state diagram | It describes live inference with a `LeafArenaState` response cache; the system re-judges **precomputed traces** and has no such type, no state enum, no `U_min`, and no `escaped`/`B_max` valve. The figure diagrams code that does not exist. Only the `RESOLVED` predicate is real (`BtStoppingPolicy.kt:123`). | `TaxonomyBenchmarkService.kt:383-406`, `:906-920`; `reconciled-argument.md:640-660` | **2.5** |
| C7 | **The construction pipeline and data-model sections**: `3_System_Architecture.tex:231-344` | Moves to Appendix A; §3.1 keeps a one-paragraph summary. | supervisor's instruction; `1_Introduction.tex:225-233` | **3.0** |
| C8 | **The `1/k` fractional-weight aggregation and its sensitivity section**: `4_Meth:183-190`; `6_Results:230-236` | Not implemented as specified — `queryToLeaves` only ever receives the **primary** leaf (`TaxonomyBenchmarkService.kt:320-322`) and `propagateOutcome` adds weight **1.0** (`:113`). The post-hoc analysis at `ValidationService.kt:682-690` computes membership posteriors `1 − Σ(secondary)`, which is a different quantity. The planned contrast compares two things, one of which is not what the methodology defines. | `reconciled-argument.md:660-666` | **0.5** |
| C9 | **Three seeds `{42, 137, 2048}` as a headline convention**: `5_Exp:68`, `:302`; `6_Results:9-12` and every figure caption | Only **seed 42** exists for the frozen artifact and for every arena result. Report single-seed honestly, with the seed-dispersion analysis as a separate, dated ablation. | `frozen-artifact.md:9-19`; `void-results.md:21` | **0.3** |
| C10 | **The scheduler-efficiency diagnostic and the budget-fidelity figure**: `5_Exp:48-52`; `4_Meth:219-222`; `6_Results:238-256`; `7_App:234-253` | Already demoted to optional; nothing depends on it; the figure has no data and the random-scheduler ablation (C4) was never run. | `6_Results:253-254` | **1.3** |
| C11 | **`routingSoftmaxTau` as the selection protocol**: `7_App:71-79` | Zero occurrences in `src/`. | `reconciled-argument.md:228` (row I) | **0.2** app |
| C12 | **Temperature-scaling calibration**: `9_App:138-140` | Not implemented anywhere in `src/`. | `reconciled-argument.md:268` (row AW) | **0.1** app |
| | **Main-text total reclaimed** | | | **~18.8 pp** |
| | **Appendix total reclaimed** | | | **~2.5 pp** |

Roughly 19 pages of main text come out. Chapter 5 grows from 279 lines of placeholders to
20 pages of prose; the arithmetic works.

### C1 in detail — which subsections go, and which cannot

`2_Literature.tex:155-412` has seven `\subsection*` blocks. Cutting the whole section would
orphan a forward reference and strip Appendix A of its citations.

| lines | subsection | disposition | why |
|---|---|---|---|
| 157–176 | Supervised HTC (HiAGM, HiTIN) | **CUT** | its own argument is that RCV1/WoS hierarchies are editorial artefacts, so the methods presuppose the taxonomy; the baselines were removed as unimplemented |
| 178–217 | Unsupervised induction (TaxoGen, CoRel) | **CUT to 1 paragraph** | keep only the differentiator at `:203-208` (MMLU-Pro labels *initialise* anchors and are then superseded by geometry, where CoRel encodes the skeleton permanently) |
| 219–242 | Spherical embeddings and vMF clustering | **KEEP, compressed to ~0.5 pp** | `\label{eq:vmf}` at `:227-231` is cited by §3.1 and Appendix A |
| 245–305 | Overlapping, polyhierarchical, cross-domain | **KEEP, compressed to ~0.4 pp** | `:282-302` states the design decision (soft weighted multi-membership + responsibility floor, strict tree topology) and `:303-305` **forward-references `sec:poly-negative`** — §5.2.5 depends on it |
| 307–341 | Multi-scale (Matryoshka) embeddings | **MOVE to Appendix A** | justifies the *fixed* 256-d slice at every depth rather than a per-depth schedule; it is construction detail, not background |
| 343–378 | Cost-based hierarchical splitting (Dasgupta) | **CUT** | `:371-378` already concedes Dasgupta gives no local stopping rule and that TaxoArena makes no Dasgupta optimality claim; Total Dasgupta Cost is cut with the DQ1 metrics (C4) |
| 380–394 | Evaluation metrics for hierarchies | **CUT** | reference-dependent metrics were dropped for want of a gold taxonomy (`5_Exp:281-285`); the reference-free metrics they motivate are cut in C4 |
| 396–409 | Synthesis paragraph | **KEEP, 3 sentences** | names the three requirements the construction needs |

## Numbers that must change wherever they appear

Carry this table into the writing as a checklist. Each is **MEASURED**.

| wrong | right | where |
|---|---|---|
| `minClusterSize = 30` | **55** | `7_App:18`; `11_App:314-321`, `:385-386`; `6_Results:89,92` |
| `separationBar = 0.02` | **0.025** | `7_App:19`; `11_App:591` |
| `α ≈ 0.82` from `ρ = 256/30` | **`α = 0.33`** from `ρ = 256/55` — **the passage's conclusion inverts** | `11_App:314-321` |
| `\binom{12}{2} = 66` | **`\binom{11}{2} = 55`** | `5_Exp:130`, `:304`; `6_Results:190` |
| 12 models | **11** (corrected roster) or **8** (pilot, as run) — say which | `5_Exp:100`, `:139`; `10_App:3,9,15`; `6_Results:174,176` |
| BT cap 500, tol `1e-6` | **200**, tol `max(tol, 0.01·SE_lb)` | `4_Meth:90-91` |
| "pseudoinverse" | rank-completed inverse of `I + 11ᵀ` | `4_Meth:96-99` |
| `− 1/K` variance correction | **`− 1/K²`** (code fixed at `a92a3ed`) | `12_App:137-139` |
| bootstrap "2,000 resamples" everywhere | 2000 in `ValidationService`, **50** in the ranking path, **1** in the trajectory | `5_Exp:307-310` |
| rubric pack size `k = 5` | **25** | `8_App:9-11` |
| path cutoff `1e-4`, per path | **`1e-30`**, on the summed node posterior | `11_App:477-478` |
| lexicographic acceptance | `dJ > max(τ, 2.0·SE(dJ))`; add an `acceptanceZ` row | `11_App:616-624`; `7_App:12-30` |
| `numIterations` 50 / 35 | pick one; the frozen run converged at iteration **10** | `7_App:27` vs `:142` |
| "guarantees every pair at every leaf" | bootstrap is on **global** pair counts — delete "guarantees" | `4_Meth:100-104`; `3_Arch:398-408` |
| `r = n/(n+7.66)` | **`c = 2.52`** at the 11-model band; disattenuation is `ρ_obs / r`, two-sided | everywhere; `cell_fidelity_and_a3.py:140` still hardcodes 7.66 |

---

# Part IV — Writing order

The order below is chosen so no section is written before its foundations exist. It
deliberately puts Chapter 2 and §3.2 **late**, because those are the two places this thesis
has historically bloated, and writing them after Chapter 5 means they can only contain what
the argument actually uses.

| # | write | why it comes here |
|---:|---|---|
| 1 | **The numbers ledger** — a single table of every wrong constant (Part III), checked off as fixed | Nothing else is safe to write until this exists. Four numbers currently invert the conclusions of passages that quote them. |
| 2 | **Appendix A** (construction formalism, corrected) | §3.1 cites it and cannot be written honestly until the formalism describes the code. This is also the largest single correction job. |
| 3 | **§3.1** — the four requirements | Falls straight out of Appendix A once A is right. Three pages. |
| 4 | **Appendix C** (pre-registrations, with the `prereg_rubric_specificity.md` amendment) | Chapter 5 calls things "pre-registered"; the reader must be able to check that. Amend before reproducing. |
| 5 | **Appendix D** + **§4.2** (rosters and exclusion policy) | §5.1.4's capture-gap result is unreadable without the roster tables. |
| 6 | **§5.1** — what the judge does | **The centre of gravity, written first among results.** Everything else in the thesis is read against it. |
| 7 | **§5.2** — what the partition does | Its nulls are only interpretable after §5.1. |
| 8 | **Chapter 6** — Discussion and Conclusion | Both results sections must exist. |
| 9 | **§3.2 and §3.3** — the arena method and measurement discipline | Written **after** §5.1, so §3.2 describes only the mechanisms §5.1 turned out to depend on. This is the anti-gold-plating step: writing §3.2 first is how the current Chapter 3 acquired a state machine for code that does not exist. |
| 10 | **Chapter 4** — remaining sections (corpus, conditions, metrics) | Depends on Appendices C and D and on §3.2's final scope. |
| 11 | **Chapter 2** — Background | Written last among chapters, so it cites only what the argument uses. §2.2 (LLM-as-judge) is sized to match §5.1's contribution; §2.4 is two paragraphs. |
| 12 | **Chapter 1** — Introduction, including §1.2 (the missing argument) | The Introduction promises; it should be written when the thesis knows what it delivers. |
| 13 | **Abstract** (English, then translate to German) | Per the existing `TODO` at `e_Abstract.tex:29-36`: do not write it before Chapter 5 carries numbers. |

**Mechanical prerequisites**, done once at step 1: `report/03_Content/0_Text.tex` (8 lines)
is an `\input` manifest listing chapters 1–8 and `report/04_Appendix/0_Appendix.tex` (6
lines) lists appendices 7–12. Both must be rewritten for the six-chapter / four-appendix
structure, and the chapter files renamed, before any cross-reference is trusted. Chapters 7
and 8 do not disappear — `7_Discussion.tex:120-237` (Limitations, real prose) folds into
§6.4 and `8_Conclusion.tex` becomes §6.5–§6.6.

**Two exceptions to the order**, both cheap and both unblocking: §5.2.5 (polyhierarchy) can
be lifted from `7_Discussion.tex:21-110` at any time, since it needs almost no editing; and
§3.2.5 ("what is not implemented") can be written immediately from
`reconciled-argument.md:640-668`, and doing so early makes every cut in Part III defensible.

---

# Part V — Work still required

Split into **blocking** (a section in this plan cannot be written honestly without it) and
**non-blocking** (the thesis ships without it, naming it as future work).

## Blocking

| # | work | why it blocks | citation |
|---:|---|---|---|
| B1 | **Recompute every Bradley–Terry standard error and confidence interval post-`a92a3ed`.** The verdicts are on disk, so this is a re-analysis, not a re-run — *but verify that `ratings.db` retains enough per-pair counts to refit without re-judging* (Part VI). | §5.1 and §5.2 quote BT θ; every SE ever reported was the clamp constant. Correct values are 44–209x larger. | commit `a92a3ed` |
| B2 | **Re-derive the within-node separation nulls on the frozen mcs=55 artifact.** | §3.1's R1 evidence — "the bar sits between two measured nulls" — currently rests on values computed on the pre-`c381211` 88-leaf tree, which are **void as to values**. The method survives; the numbers do not. | `void-results.md:24`; `frozen-artifact.md:137-138` |
| B3 | **Commit `tools/analysis/rubric_specificity_null.py` and `src/test/kotlin/taxonomy/RandomCellRubricNullHarness.kt`, and append the null-arm results to `prereg_rubric_specificity.md`.** | §5.2.2's p = 1.2e-6 is the thesis's cleanest positive result and its supporting artifacts are **untracked in git** — one `git clean` from being unsupported. Appendix C reproduces a pre-registration that currently says the opposite of what happened. | `reconciled-argument.md:94-98`, `:139-141` |
| B4 | **Re-derive discriminative flatness at the corrected 11-model roster, with the script committed.** | §3.1 cites granularity flatness as what licenses `minClusterSize = 55`. The 8-model figures are solid (`prereg_discriminative_power.md:76-79`); the 11-band figures **are nowhere in the repository**. | `reconciled-argument.md:187-204` |
| B5 | **Correct `11_App:314-321`.** At `n_min = 55`, `α = 0.33`, not 0.82, and the passage's conclusion ("leaf size is a calibrated parameter, not a free one") **inverts**. Rewrite the argument, do not just change the digit. | Appendix A ships with a false derivation otherwise. | `reconciled-argument.md:393-399` |
| B6 | **Resolve the judge model's identity against the run manifest.** `8_App:12-13` and `arena-math-findings.md:618` say `Mistral-Large-3`; `TaxonomyConfig.kt:59`'s default is `ministral-3:14b`. | Appendix D's "no self-preference confound" claim depends on it, and it appears in §4.5. | `reconciled-argument.md:1188-1191` |
| B7 | **Recompute the leaf-size figure** with the reference line at `n_min = 55` and the measured distribution (87 leaves, median 88, IQR [71,118], min 54, max 396, 1 below floor). | `6_Results:82`'s "median in the region of 90" is right; the `n_min = 30` line on the same figure is wrong. | `reconciled-argument.md:401-409` |
| B8 | **Decide the routing-ECE disposition.** Either fix `BatchTrickleEvaluator.kt:196` (`maxOf` → sum) and re-run, or report 0.2114 with the aggregation discrepancy named. Amend `known-defects.md:63-66` either way. | Appendix B and `7_App:120`'s gate both depend on it. Currently the appendix defines one metric and the export computes another. | `reconciled-argument.md:33-83` |
| B9 | **Report realised call counts and the run manifest for §5.0.** | §5.0 fixes the scope of everything in Chapter 5. | `5_Exp:75-77` |

## Non-blocking — name as future work, do not wait for

| # | work | disposition |
|---:|---|---|
| N1 | **The rule-ID citation scheme** in the verdict schema | Distinguishes rubric *reproduction* from *application* and counts prior-decided verdicts. Changes the schema, so it must precede any further arena run. §6.6 item 1. |
| N2 | **The OPTIONS-BLIND arm** | **Blocked** until the four traceless models are regenerated with output capture; otherwise `no-trace × no-trace` is uninterpretable rather than a chance-level null (`arena-math-findings.md:549-558`). Its predictions are already fixed in writing (`:296-319`) — reproduce them in Appendix C regardless, since a prediction written before a run that never happened is still evidence of discipline. |
| N3 | **The law arena on the 11-model band** | The domain where the partition has something to be right about (`arena-math-findings.md:833-835`). Without it, §5.2.4 reports the screen as a **bound** and §6.6 names the run as the test. |
| N4 | **Re-fit the reliability constant `c` against the arena rankings of the roster actually used** | `c = 2.52` was fitted at the 11-model band on **ground-truth** rankings, and `c` is explicitly not a property of the corpus (`arena-math-findings.md:881-883`). Also update `cell_fidelity_and_a3.py:140`, which still hardcodes 7.66. |
| N5 | **Re-derive the void results**: maxK plateau, k-fallback figures, five-seed sweep leaf counts, core/fringe, matched-k ARI, the λ₁ proxy, the six named marginal splits | `void-results.md:19-28`. **Rule for the write-up**: where a void number appears, do not delete the paragraph — replace the number, keep the reasoning, and say in one clause that it was re-measured after the router correction (`void-results.md:55-60`). |
| N6 | **A general `TRACE_PRESENCE` FAIL branch at ~0.90** | One line of code. Turns a curated exclusion list into a threshold that generalises. §6.6, and it makes Appendix D's limitation actionable rather than merely honest. |
| N7 | **The redundancy percentages** ("72.2% redundant, 42.2% saturated") | **Do not restate.** Not reproducible under either an observed-primary or a disattenuated reading, and the convention is underspecified in the pre-registration. If a redundancy claim is wanted, re-derive it at `c = 2.52` with the convention stated. |

---

# Part VI — What could not be verified

Stated explicitly so nothing in this plan is mistaken for checked.

1. **The page-count conversion.** All budgets assume ~38 tex lines per typeset page,
   inferred from file sizes, not measured from a compiled PDF. `latexmk` is unusable in
   this environment (no perl). Every page number in Parts I–III is an estimate and should be
   re-checked against a first compile.
2. **Whether `ratings.db` retains enough per-pair win/comparison counts to refit BT
   standard errors without re-judging.** B1's cost — a re-analysis versus a 1,736-comparison
   re-run per condition — turns entirely on this, and it was not checked.
3. **The 11-model-band discriminative flatness (0.973 / 0.936).** Not in any doc, script
   output, or artifact. `arena-math-findings.md:838-842` still says it has not been
   re-derived. Do not cite.
4. **The redundancy percentages.** Not reproducible under either convention.
5. **Whether the exported Routing ECE of 0.2114 survives the aggregation fix.** The
   `maxOf`→sum change will move it, and in a predictable direction (confidence rises, so
   apparent under-confidence falls), but by how much is unmeasured.
6. **Whether `c = 2.52` is right for the roster the arena will use.** It was fitted at the
   11-model band on ground-truth rankings, not arena rankings.
7. **`measurement-discipline.md:191`'s `c = 7.602` against `frozen-artifact.md:83`'s 7.66.**
   A 0.8% discrepancy with no stated cause, predating the 3.04x correction. Partially
   resolved: 7.602 is a refit on the three measured split-half values with `r1 = 0.1163`,
   and the bootstrap interval `[7.52, 7.66]` (`measurement-discipline.md:204`) contains
   both. But `frozen-artifact.md:84-87` flags 7.66 as **not re-derived anywhere in this
   repository** and as a fixed convention rather than a measured quantity, so which number
   the thesis should use is still open — and it is moot if B4/N4 re-fit at the real roster.
8. **Which pre-registered band set governs the rubric-specificity result.** See Appendix C,
   caveat (0). The two documents state different bands and neither says they measure
   different quantities.
9. **The judge model actually used in the frozen arena run.** See B6.
10. **The content of `2_Literature.tex`.** Its seven `\subsection*` blocks in `:155-412`
    were inspected structurally and the C1 disposition table reflects that, but the survey's
    prose quality was not read. Read it before executing the cut.
11. **`3_System_Architecture.tex:1-344`** was not audited against code in the reconciliation
    pass; only `:345-551` was. §3.2's plan assumes `:231-344` is a fair description of the
    construction pipeline, which is untested. Note that `:386-414` describes the
    connectivity bootstrap as covering all `C(M,2)` pairs and calls that "stronger than the
    M−1 spanning tree identifiability requires" — the code bootstraps on **global** pair
    counts, so per-leaf graphs can still be disconnected (§3.2.3).
12. **Whether the law run is affordable at 11 models.** Budget arithmetic exists for a
    10-model roster (`arena-math-findings.md:714-723`); at 11 models it is 55 pairs, not
    recomputed.
13. **Live credentials in the working tree.** `git diff config/application.yml` replaces two
    environment-variable placeholders with literal secrets — a HuggingFace token at line 23
    and an Azure AI endpoint plus API key at lines 55-56. The file is tracked. **Rotate both
    and restore `${...}` before anything is committed, pushed, or submitted.** Not a thesis
    matter, but it blocks submission.

---

# Part VII — How the negatives are presented

Six of this thesis's most important results are negative or self-corrected. Buried, they
read as a project that did not work. The device in every case is the same: **show that the
result could have come out the other way, and that the criterion for reading it was fixed
before the data.**

**The template**, taken from `7_Discussion.tex:21-110` and used for every negative in this
plan: *operator stated → measurement shown → structural reason given → decision recorded →
cost of the decision named → replacement invariant stated.* Six moves, ~90 lines, no
apology anywhere in it.

Applied:

| negative | how it is presented | where |
|---|---|---|
| Cells do not have different true rankings | Pre-registered with three named outcomes; the outcome that occurred was named in advance as "branch 2 — same signal, thinner"; the primary statistic was fixed in advance and the secondary one moves the opposite way | §5.2.3 |
| The rubric does not change the verdict | Not a parity finding — a comparison whose arms agree on 99.4% of winners. The methodological rule that follows (measure verdict agreement first; it is one query and it decides whether the arm is worth 10,000 calls) is a contribution | §5.1.5, §4.3 |
| The z-gate is stability-neutral and J-neutral | **Refuted corroborations are stronger than unrefuted ones.** The gate was adopted on coherence alone *after* both of its empirical supports were tested and failed. The transferable sentence — a gate can be right because its units are right, without improving the number it gates — is worth more than "the gate helped" | §5.2.1, §3.3 |
| The capture gap decided half the Math arena | Found while sizing the roster for a **different** experiment, and it qualified numbers already written down. What survives, survives *stronger*: 97.0% vs 83.2% at matched capability gap | §5.1.4, §6.3 |
| The BT standard errors and the reliability constant were wrong | Caught by independent routes — a units check and a roster re-fit compounding to the same 3.04x; a linear-algebra derivation for the variance. Presented under §6.3's frame, with corrected values | §6.4, §6.3 |
| Polyhierarchy | Already written to the template. Keep verbatim | §5.2.5 |

**And the one that relocates the claim.** The judge bypassing the partition on a
multiple-choice corpus is not a failure of the architecture; it is a **measurement of the
boundary of the architecture's applicability**, obtained on the corpus that makes the
comparison possible. That sentence is the thesis, and it is only available because the
negatives were measured rather than avoided.
