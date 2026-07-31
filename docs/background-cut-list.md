# Chapter 2 (Background) — cut list

Target file: `report/03_Content/2_Literature.tex`, 712 lines, 75 citation
instances over 55 unique keys. Compiled span is pages 17–34 (Chapter 3 opens at
page 35), so 18 pages for 712 source lines: **~40 source lines = 1 page**. All
page estimates below use that ratio.

**Recoverable: ~230 lines ≈ 5.5–6 pages.** Chapter drops from 18 pages to ~12.

---

## Method used to establish "load-bearing"

Every citation key in Chapter 2 was extracted and grepped across all of
`report/` outside `2_Literature.tex`. Every named system and concept was grepped
separately (system names are often used without their key). Cross-references
into Chapter 2's labels were checked in both directions.

Two structural facts came out of this and drive most of the list:

1. **31 of 55 citation keys appear nowhere else in the thesis.** Not in
   Chapters 1, 3–8, not in any appendix, not in the abstract.
2. **Chapters 5, 6, 7 and 8 never reference Chapter 2.** The only inbound
   references are `1_Introduction.tex:25`, `:119`, `:269`, `:685` and
   `04_Appendix/11_Appendix_DAGConstructionFormalism.tex:438`. Sections
   `sec:ranking-models` and `sec:routing` have zero inbound references from
   anywhere.
   `5_Experimental_Design.tex` cites exactly two keys in the whole chapter
   (`wang2024mmlupro`, `zhang2015agnews`) and neither depends on Chapter 2.

Keys used again elsewhere (these anchor the LOAD-BEARING calls below):
`zheng2023judging`, `wang2024mmlupro`, `hendrycks2021measuring`,
`bradley1952rank`, `boubdir2024elo`, `frick2025p2l`, `raju2024constructing`
(all → Ch. 1); `banerjee2005vmf`, `hornik2014vmf`, `kusupati2022mrl`,
`dasgupta2016cost` (→ Ch. 3 / appendices); `deng2024contamination`,
`chen2024verbosity`, `panickssery2024llm`, `white2024livebench` (→ Ch. 7).

---

## Section 2.1 — LLM Evaluation Benchmarks (L13–135, 123 lines, pp. 17–19)

### L17–29, MMLU + HELM description — DUPLICATED + SURVEY PADDING. Cut ~12.
`liang2022holistic` appears three times here and **nowhere else in the thesis**.
HELM is never contrasted against, never revisited, and supplies no term the
thesis uses. The whole HELM sentence set (L25–29, "HELM evaluated 30 models
across 42 scenarios and seven metrics…") goes, plus its callback at L43–44.
MMLU's own statistics (L22–25: 15 000 questions, 57 subjects, 43.9 % vs 89.8 %)
duplicate `1_Introduction.tex:111–113`, which already introduces MMLU and
MMLU-Pro as the corpus lineage.
Keep: MMLU as the named ancestor of MMLU-Pro.
**Save ~12 lines (0.3 pp).**

### L31–44, three failure modes — PARTLY DUPLICATED. Cut ~5.
`1_Introduction.tex:116–124` already states saturation and categorical
structure, and says explicitly that **only the second is this thesis's subject**
("It is a problem about *which questions* a benchmark asks, and harder questions
answer it"). Chapter 2's saturation paragraph (L33–36) therefore re-argues a
point Chapter 1 has already disowned.
Keep: contamination (`deng2024contamination` is reused at
`7_Discussion.tex:213`) and categorical brittleness (the thesis's actual
subject).
Cut: the saturation sub-paragraph.
**Save ~5 lines.**

### L48–54, BIG-Bench Hard — SURVEY PADDING. Cut all 6.
`suzgun2022bigbench` is cited twice, both here, and nowhere else. BBH is never
contrasted against, never used as a corpus, and the PaLM/human-rater anecdote
carries nothing forward. The "progressively harder benchmarks" line of argument
survives intact through MMLU-Pro alone.
**Save 6 lines.**

### L63–71, LiveBench and the freshness/coverage tension — SURVEY PADDING. Cut ~5.
`white2024livebench` is reused once, at `7_Discussion.tex:215`, but Chapter 7
uses it self-containedly in a single clause ("contamination-limited benchmark
designs exist precisely because the problem is pervasive") and does not depend
on Chapter 2's exposition. The freshness-vs-depth trade-off is never taken up
again.
Keep: L68–71 (the framework that fixes neither questions nor domains), which is
the positioning sentence.
**Save ~5 lines.**

### L75–86, Chatbot Arena — SCAFFOLDING, over-length. Cut ~5.
`chiang2024chatbotarena` is cited twice, both here, nowhere else. The platform
itself is load-bearing as the format the thesis adopts. The implementation
detail is not: the sandwich-standard-error clause and the adaptive-sampling
clause (L81–86) describe machinery this thesis does not use — its scheduler is
its own design (`4_Methodology.tex:320–350`) and it prints no Bradley–Terry
interval anywhere (`1_Introduction.tex:672–675`).
Minimum: two sentences — free-form prompt, two anonymous models, vote,
Bradley–Terry aggregation.
**Save ~5 lines.**

### L88–96, Singh et al. leaderboard critique — SURVEY PADDING. Cut ~7.
`singh2025leaderboard` appears once, here, and nowhere else. The closing stance
sentence ("A leaderboard's measurement properties must therefore be audited
independently…") is a claim the thesis makes for itself in Chapter 1 and in the
measurement-discipline section (`4_Methodology.tex`, `sec:meth-discipline`); it
does not need this citation to stand.
**Save ~7 lines.**

### L98–120, BenchBuilder — LOAD-BEARING. Keep.
`li2024benchbuilder` and `arena2025categories` appear only here, but this block
is where the thesis states what it differs from ("BenchBuilder's clusters serve
prompt filtering only: membership is hard, cluster coherence is never measured,
no split-or-stop statistic makes the partition auditable"). That contrast is
what R1 in `3_System_Architecture.tex:54–56` answers and what the Synthesis
(L688–695) depends on. No cut.

### L122–134, P2L — LOAD-BEARING. Keep.
`frick2025p2l` is reused at `1_Introduction.tex:424`, where the title term
"Query-Adaptive" is defined *by contrast with P2L*. The representational
difference stated here (amortised regression weights vs. discrete testable
cells) is the thesis's positioning claim. No cut.

**Section 2.1 total: ~40 lines ≈ 1 page.**

---

## Section 2.2 — Taxonomy Induction: Positioning (L137–278, 142 lines, pp. 20–22)

### L144–148, HiAGM / HiTIN — SURVEY PADDING. Cut all 5.
`zhou2020hiagm` and `zhu2023hitin` appear once each, here, nowhere else.
Supervised hierarchical classification is set aside in the first clause; the
Reuters/WoS editorial-artefact elaboration adds nothing.
Note: the clause "the two supervised baselines originally planned for this
thesis were removed as unimplemented" is a **project-state disclosure**, not
background. It belongs with the not-implemented inventory
(`4_Methodology.tex`, `sec:arch-not-implemented`, and
`Appendix~\ref{app:not-implemented}`), not in a literature chapter.
**Save 5 lines.**

### L149–153, Dasgupta cost — LOAD-BEARING. Keep.
`dasgupta2016cost` is used at `04_Appendix/9_Appendix_MetricDefinitions.tex:34`
(Total Dasgupta Cost is a reported metric) and at
`04_Appendix/11_Appendix_DAGConstructionFormalism.tex:670–673`, which states
explicitly that the acceptance score "is *not* a Dasgupta cost delta". The
disclaimer here is what those two passages lean on. No cut.

### L154–157, hF_β / Kosmopoulos — SURVEY PADDING. Cut ~3.
`kosmopoulos2015hmetrics` appears once. The metric is explicitly *not reported*.
One clause suffices to say reference-dependent hierarchy metrics need a gold
hierarchy that does not exist here.
**Save ~3 lines.**

### L159–173, TaxoGen and CoRel — SCAFFOLDING, heavily over-length. Cut ~11.
`zhang2018taxogen` and `huang2020corel` appear once each, nowhere else. This is
the only place the thesis positions itself against unsupervised taxonomy
induction, so it cannot go entirely. The full 15 lines are not needed: what is
load-bearing is (a) seed-guided starting point, differently treated, and (b)
term-level vs. query-level node model.
Minimum: 4 lines.
**Save ~11 lines.**

### L175–201, occupying systems and the narrowed claim — MIXED.
- L180–188 (TnT-LLM, Clio, TopicGPT): `wan2024tntllm`, `tamkin2024clio`,
  `pham2024topicgpt` each appear once, nowhere else. None is contrasted
  individually — the paragraph itself says "All three, like BenchBuilder, induce
  human-readable structure from a corpus and consume it for classification,
  monitoring, or curation," which is one sentence doing the work of nine lines.
  **SURVEY PADDING, save ~8 lines** (keep the three names in a list, drop the
  per-system descriptions).
- L188–201 (the (a)/(b) conjunction): **LOAD-BEARING.** This is the claim the
  Synthesis restates and that `3_System_Architecture.tex:45–108` (R1–R4)
  operationalises. Keep.

### L203–226, von Mises–Fisher — LOAD-BEARING but DUPLICATED. Cut ~17.
vMF is the node model, and `banerjee2005vmf` / `hornik2014vmf` are both reused
at `11_Appendix_DAGConstructionFormalism.tex:287–340`. But that appendix section
("von Mises–Fisher Density and MLE") restates the density **with the normalising
constant expanded**, gives the MLE for μ, the Banerjee closed form, the
Newton–Raphson refinement and the shrinkage factor. Chapter 2's `eq:vmf` is a
strict subset of it and is **referenced by nothing** (`\ref{eq:vmf}` has zero
hits thesis-wide).
Cut: the displayed equation, the Bessel-function clause, the EM/Bregman-
divergence sentence, and the high-κ numerical-stability sentence — all four are
appendix material and three of them are already in the appendix.
Minimum: ~5 lines naming vMF as the node model on the ℓ2-normalised sphere, with
both citations and the pointer to `app:dag-formalism`.
**Save ~17 lines (0.4 pp).**

### L228–237, Matryoshka Representation Learning — DUPLICATED (three copies). Cut ~8.
`kusupati2022mrl` appears in three places:
- here (L230–237),
- `3_System_Architecture.tex:121–137` — a *fuller* explanation, including why
  truncation is safe and why 256 is fixed at every depth,
- `11_Appendix_DAGConstructionFormalism.tex:432–470` — the formal version.

The Chapter 3 copy should survive: it is the one placed where the reader needs
it, and it is the only one that states the consequence for construction.
Chapter 2's copy is redundant.
**Caveat — one edit is mandatory if this is cut:**
`11_Appendix_DAGConstructionFormalism.tex:438` reads "Section~\ref
{sec:taxonomy-construction} gives the coarse-to-fine packing property this rests
on." That back-pointer must be retargeted to `3_System_Architecture.tex:121`
(`sec:arch-taxonomy`) or the appendix will point at deleted text.
**Save ~8 lines.**

### L244–253, fuzzy clustering and polyhierarchy literature — SURVEY PADDING. Cut ~7.
`fuzzyhc1969` and `polyhierarchy2006` appear once each, nowhere else. The
thermodynamics example (L242–244) and the tree-vs-DAG distinction are needed;
the citation-supported walk through soft hierarchical clustering and knowledge
organisation is not.
Minimum: 3 lines defining polyhierarchy as a DAG relaxation.
**Save ~7 lines.**

### L255–267, the two relaxations and which one was adopted — LOAD-BEARING. Keep.
This defines weighted multi-membership under a responsibility floor with an
argmax primary. Verified still accurate against
`11_Appendix_DAGConstructionFormalism.tex:590–606` (`membershipFloor`,
self-normalised, "the *primary* leaf is the argmax") and
`3_System_Architecture.tex:299`. The forward reference to `sec:poly-negative`
resolves (`6_Results.tex:1795`). No cut.

### L269–277, "three requirements" summary — DUPLICATED. Cut all 9.
This anticipates `3_System_Architecture.tex:45–108`, which states the operative
requirement list as R1–R4 with thresholds. Chapter 2's version has no thresholds
and is superseded four pages later. Chapter 2 does this **three times**
(here, L437–451, L592–604); at most one should survive, and the R1–R4 list is
the one the thesis actually uses.
**Save 9 lines.**

**Section 2.2 total: ~60 lines ≈ 1.5 pages.**

---

## Section 2.3 — LLM-as-a-Judge (L280–452, 173 lines, pp. 23–26)

This is the chapter's densest load-bearing section. It gives back the least.

### L288–298, pointwise vs. pairwise — LOAD-BEARING. Keep.
`zheng2023judging` is the most-reused key in the chapter and is cited three
times in `1_Introduction.tex:256–264`. This is the stated justification for the
pairwise format. No cut.

### L300–330, the three biases — LOAD-BEARING. Keep all three.
Dependent claims, verified:
- positional → `4_Methodology.tex:158–160` (dual call, order swapped, tie on
  disagreement) and `7_Discussion.tex:240–242`;
- verbosity (`chen2024verbosity`) → `7_Discussion.tex:243–247`;
- self-preference (`panickssery2024llm`) → `7_Discussion.tex:247–256`.
All three are answered directly in the discussion's residual-bias paragraph.
No cut.

### L332–340, mitigations and their tractability — SCAFFOLDING. Cut ~4.
The tractability ranking (positional most, self-preference least) is restated
almost verbatim in `7_Discussion.tex:240–256`, which is where it belongs because
that is where it is measured against what was actually implemented. Trim to the
list of mitigations.
**Save ~4 lines.**

### L342–378, the shortcut result — LOAD-BEARING. Keep in full.
`stephan2024calculation`, `tan2025judgebench`, `zeng2024llmbar`,
`lambert2024rewardbench` all appear only here, and this is the one place in the
list where "appears only in Chapter 2" does **not** mean cuttable. The
*concept* is reused in five places outside Chapter 2:
`e_Abstract.tex:106`, `1_Introduction.tex:98`, `6_Results.tex:968`,
`7_Discussion.tex:26–28`, and the whole of `sec:disc-rq1`. Chapter 7's central
inference ("On a multiple-choice corpus it has a shortcut, and it takes it")
reads as an extension of exactly this literature. If these four citations are
cut, Chapter 6's headline finding loses its prior art and reads as an
independent discovery — which L371–378 explicitly denies.
No cut. **This is the block I came closest to cutting on the citation-count
rule and did not.**

### L380–391, FLASK — SCAFFOLDING. Cut ~4.
`ye2024flask` appears once. FLASK is genuinely used: L414–415 contrasts the
thesis's distill-once protocol against FLASK's per-instance criteria, so it
cannot go. The 12-line build-up can.
Minimum: 3 lines — decomposing coarse judgments into fine criteria changes
scores and orderings, so criteria are part of the measurement.
**Save ~4 lines.**

### L393–407, MemAlign / Think-J / JudgeLRM — SURVEY PADDING. Cut ~10.
`databricks2026memalign` (flagged in-text as non-peer-reviewed),
`huang2025thinkj`, `chen2025judgelrm` each appear once, nowhere else. None is
contrasted against — the contrast in L409–420 is against the *reference-guided
mode* and *FLASK*, both of which survive. RL-trained reasoning judges are a
training-side family this thesis has no relationship to.
Keep: Zheng et al.'s reference-guided mode (L393–395), which L414 contrasts
against directly.
**Save ~10 lines.**

### L409–433, TaxoArena's protocol and the sharpened question — LOAD-BEARING but internally repetitive. Cut ~6.
L409–420 and L422–433 make the same point twice: the distill-once /
withhold-at-test protocol had not been tested against correctness strata, and
that is what Chapter 6 measures. The second paragraph re-states the first with
the strata enumerated. Merge; the enumeration of strata is the part worth
keeping.
**Save ~6 lines.**

### L435–451, closing constraints and tie handling — MIXED, and partly FALSE (see below). Cut ~5.
The tie-policy sentences (L444–451) are load-bearing —
`6_Results.tex:476` (`sec:res-tie-policy`) is the delivery, and every rank
correlation in Chapters 6 and 8 is reported under both conventions.
The three-constraint list (L437–441) is the third copy of the requirements
summary and contains a false claim (Issue 2 below).
**Save ~5 lines.**

**Section 2.3 total: ~29 lines ≈ 0.7 pages.**

---

## Section 2.4 — Pairwise Ranking Models (L454–605, 152 lines, pp. 27–29)

The largest concentration of dead weight in the chapter.

### L456–474, Elo — SCAFFOLDING, over-length. Cut ~15.
`elo1978rating` appears once, nowhere else. `boubdir2024elo` is reused, at
`1_Introduction.tex:131`, where Elo is already named as the scalar rating the
thesis rejects. `\ref{eq:elo-expected}` has **zero references** thesis-wide. The
thesis uses Bradley–Terry throughout and never fits an Elo rating; Elo needs to
appear only long enough to be dismissed.
Minimum: 4 lines — Elo as the chess-derived scalar, static skill, no
uncertainty, transitive by construction, non-transitivity documented in LLM
preferences.
**Save ~15 lines (0.4 pp).**

### L476–518, Bradley–Terry and connectivity — LOAD-BEARING. Keep.
The single most-depended-on block in the chapter:
- BT likelihood and MLE → `4_Methodology.tex:204` (`sec:meth-bt`),
  `1_Introduction.tex:373`;
- identifiability up to an additive constant per connected component →
  `4_Methodology.tex:311–318` verbatim ("the word 'guarantees' is not used of it
  here");
- connected comparison graph as a requirement → `3_System_Architecture.tex:58`
  (R2 — Support);
- pair-coverage reporting → `6_Results.tex:104–105`, `:122`, `:932–933`,
  `:1767`.
`\ref{eq:bt}` is unreferenced, but the equation is the definition the whole
arena rests on and Chapter 4 does not restate it. Keep.
**One caveat:** L508–511 is a result, not background — see Issue 1.

### L520–533, TrueSkill / OpenSkill / hierarchical BT — SURVEY PADDING. Cut ~10.
`herbrich2007trueskill`, `weng2011bayesian`, `cattelan2012paired` appear once
each, nowhere else. The block does one job — justifying BT-MLE over Bayesian
alternatives — and that is a two-sentence job. The partial-pooling sentence is
worth keeping as a stated non-choice (it is the natural refinement for sparse
cells, which the coverage results make relevant), but at one line, not five.
**Save ~10 lines.**

### L535–549, Jamieson & Nowak active ranking — SURVEY PADDING. Cut ~11.
`jamieson2011activeranking` appears once. The O(d log n) bound is never invoked
again; `4_Methodology.tex:320–350` specifies a composite-utility scheduler that
is not this algorithm and does not reference the bound. The claim at L546–549
("restricting the ranking problem to a semantically coherent sub-domain reduces
the effective intrinsic dimensionality") is asserted, never tested, and sits
awkwardly beside the granularity null.
Minimum: 3 lines — active ranking exists, it beats uniform sampling, the metric
assumption is an idealisation.
**Save ~11 lines.**

### L550–565, Heckel et al. finite-sample bounds — SURVEY PADDING. Cut ~14.
`heckel2019activeranking` is cited twice, both here, nowhere else. Two reasons
this is safe to remove almost entirely:
1. The rule it recommends — schedule the pair with the largest overlap in BT
   confidence intervals — is **not** what the thesis implements. The implemented
   utility is binary entropy of the win probability divided by combined variance
   (`4_Methodology.tex:325–338`).
2. There are no Bradley–Terry confidence intervals anywhere in this thesis
   (`1_Introduction.tex:672–675`, `4_Methodology.tex:296–306`), so the
   interval-overlap rule could not have been implemented.
The one sentence worth keeping is the general one that survives the closing
paragraph anyway (scheduling reads the estimator's variance, so scheduling
quality is downstream of variance correctness — L598–602).
**Save ~14 lines (0.35 pp).**

### L567–588, mELO and Blade–Chest — SURVEY PADDING. Cut ~16.
`balduzzi2018melo` (twice) and `chen2016bladechest` appear only here. Neither is
adopted — the text says so. The Hodge-decomposition and offence/defence
descriptions are six lines of machinery for a model the thesis explicitly
declines.
Minimum: 4 lines — cyclic dominance violates scalar transitivity, models exist
that represent it, they are not adopted, and whether they would have anything to
represent is an empirical precondition.
**Save ~16 lines (0.4 pp).**
**Defect found here:** L583–588 promises that
`Section~\ref{sec:res-c5}` "reports how far the per-cell rankings of this roster
depart from a single common ordering". `sec:res-c5` (`6_Results.tex:498`) is the
no-partition baseline and reports no such thing. The measurement described is
the granularity analysis (`sec:res-granularity`) / leaf-substructure null
(`sec:res-leaf-null`). **Retarget or drop the forward reference.**

### L590–604, "three requirements" closing — DUPLICATED. Cut ~10.
Third instance of the anticipatory requirements list. The scheduler-variance
dependency sentence (L598–602) is the only part not stated better elsewhere;
`4_Methodology.tex:296–318` covers the rest.
**Save ~10 lines.**

**Section 2.4 total: ~76 lines ≈ 1.9 pages. Largest single-section saving.**

---

## Section 2.5 — Query Routing as the Target Use Case (L607–684, 78 lines, pp. 30–32)

**No chapter after this one references it.** `sec:routing` has zero inbound
references. Every occurrence of "rout*" in Chapters 5–8 refers to routing a
*query into a leaf*, not routing to a model — checked line by line. The only
callback to the routing motivation anywhere downstream is
`7_Discussion.tex:24`, and it points at `sec:motivation` in **Chapter 1**, not
here.

This does not make the section deletable — it carries the gap claim, and the
gap claim is the thesis's positioning. It makes it compressible to roughly a
quarter of its length.

### L617–631, the routing problem and Raju et al. — SCAFFOLDING. Cut ~9.
`raju2024constructing` is reused at `1_Introduction.tex:134` and `:208`, and
Chapter 1 already builds the A/B crossing argument in full, with a table
(`tab:routing-example`), a figure (`fig:routing-slopegraph`) and real roster
numbers (L204–221). Chapter 2 reproduces the A-beats-B-on-maths argument in
prose.
Minimum: 3 lines — rankings are not stable across domains, per-domain scores
reduce mis-routing, existing work needs the taxonomy given.
**Save ~9 lines. DUPLICATED with `1_Introduction.tex:141–221`; the Chapter 1
copy survives (it has the figure).**

### L633–652, FrugalGPT / RouteLLM / EmbedLLM / UniRoute — SURVEY PADDING. Cut ~14.
`chen2023frugalgpt`, `ong2024routellm`, `zhuang2024embedllm`,
`jitkrittum2025uniroute` — none appears outside this section. None is a baseline
the thesis compares against; no routing experiment was run
(`8_Conclusion.tex:205` lists a held-out routing check as **future work**). The
paragraph's own closing sentence does all the work: "In all of these, the domain
structure over which models are profiled is either absent or predefined by the
benchmark that supplied the training set."
Minimum: 5 lines — the four names in a list plus that closing sentence.
**Save ~14 lines (0.35 pp).**

### L654–669, The Avengers / Avengers-Pro / RouterDC / RouterBench — SURVEY PADDING. Cut ~11.
`zhang2025avengers`, `zhang2025avengerspro`, `chen2024routerdc`,
`hu2024routerbench` — none appears outside this section. The honesty point
("Corpus-induced structure for routing is therefore occupied territory") is
load-bearing and is one sentence. RouterBench is named as making comparison
feasible — a comparison that was never run.
Minimum: 4 lines.
**Save ~11 lines.**

### L671–684, the (a)/(b)/(c) conjunction — DUPLICATED with the Synthesis. Cut ~12.
L671–684 and L688–695 state the same conjunction twelve lines apart, in the same
section, with the same three components and the same list of systems that occupy
one half. The Synthesis version (L686–695) is tighter and is the one Chapter 3's
R1–R4 answers.
Keep the Synthesis; cut the section-ending restatement.
**Save ~12 lines.**

**Section 2.5 total: ~46 lines ≈ 1.2 pages.**

---

## Chapter opener and Synthesis

- **L1–10, roadmap** — SCAFFOLDING. Reproduces the ordering the section headings
  already give. Cut to a two-line statement of the dependency order.
  **Save ~5 lines.** (Not counted in the total above; treat as a bonus.)
- **L686–695, Synthesis** — LOAD-BEARING. Keep.
- **L697–712, the two corpus properties** — LOAD-BEARING. Keep. This is the
  block that sets up Chapter 6's central reading (verifiable key makes the
  measurement possible *and* bounds it), and it maps directly onto
  `7_Discussion.tex:29–35`. Do not touch.

---

## Totals

| Section | Lines cut | Pages |
|---|---|---|
| 2.1 Benchmarks | ~40 | 1.0 |
| 2.2 Taxonomy induction | ~60 | 1.5 |
| 2.3 LLM-as-a-judge | ~29 | 0.7 |
| 2.4 Pairwise ranking | ~76 | 1.9 |
| 2.5 Routing | ~46 | 1.2 |
| **Total** | **~230** | **~5.8** |

Chapter 2 goes from 712 lines / 18 pages to ~480 lines / ~12 pages.
Citation count drops from 55 unique keys to roughly 33 — every key removed is
one that appears nowhere else in the thesis.

### Three largest single cuts

1. **§2.4.3 + §2.4.4 (active ranking and intransitivity), L535–588 — 41 lines,
   ~1 page.** Four citations, none used elsewhere, describing three algorithms
   none of which is implemented, one of which (interval-overlap scheduling)
   could not have been implemented because the thesis prints no BT intervals.
2. **§2.5 learned and cluster-based routers, L633–684 — 37 lines, ~0.9 pages.**
   Eight citations, none used elsewhere, describing baselines against which no
   experiment was run, ending in a conjunction restated ten lines later.
3. **The vMF equation block plus the MRL paragraph, L203–237 — 25 lines,
   ~0.6 pages.** Both are stated more completely in
   `11_Appendix_DAGConstructionFormalism.tex` and (for MRL) in
   `3_System_Architecture.tex:121–137`. `\ref{eq:vmf}` is referenced by nothing.

---

## Results stated in Chapter 2 that should not be there

The previous pass was mostly successful — no numeric result from Chapter 6
appears in Chapter 2, and the closing sentence at L708–710 explicitly disclaims
anticipation. Two things remain.

**Issue 1 — L508–511 states a defect of this implementation as general
background.**
> "a bootstrap that floors comparison counts globally rather than per leaf can
> leave individual leaves on a sparse graph while the aggregate looks well
> covered"

That is not a fact about Bradley–Terry. It is a description of this project's
own scheduler bug, stated word-for-word at `4_Methodology.tex:315–318` ("that
bootstrap operates on *global* pair counts rather than per-leaf ones") and
quantified at `6_Results.tex:104–105` and `:1767`. In Chapter 2 it reads as
prior knowledge, which lets Chapter 6's coverage disclosure look anticipated
rather than found. Cut the clause; the general point (sparse graphs destabilise
BT, coverage must be reported) survives without it.

**Issue 2 — L437–441 asserts a design the system does not have.**
> "explicit per-domain criteria that do not reward length against verbosity
> bias; judge rotation as the only remedy for self-preference. The
> guideline-generation mechanism built from these constraints is specified in
> Chapter 4."

`7_Discussion.tex:243–245` states the opposite: "Verbosity bias is **not**
mitigated: the rubric contains no length-normalisation criterion." And no judge
rotation exists — `7_Discussion.tex:248–255` records a single judge
(Mistral-Large-3) in every reported run, with the footnote saying self-preference
is avoided by accident of roster rather than by design ("no constraint enforces
that"). Chapter 2 claims a mechanism "built from these constraints" that was
built from one of the three. This is a **false claim as the chapter currently
stands**, independent of any cutting decision, and it should be fixed even if
nothing else on this list is actioned.

## Other claims that are false or outdated

**L583–588 points at the wrong section.** Described above under §2.4. The
promised measurement lives in `sec:res-granularity` / `sec:res-leaf-null`, not
`sec:res-c5`.

**L493–499 (Fisher-information standard errors) is correctly hedged.** L493–495
already says "Whether a given implementation realises that guarantee is a
separate question," which is the right posture given
`1_Introduction.tex:672–675`. No change needed. Flagging it only because it
looks like a problem and is not.

**L255–267 (multi-membership) verified accurate** against
`11_Appendix_DAGConstructionFormalism.tex:590–606` and
`3_System_Architecture.tex:299`. The floor is self-normalised, the argmax is the
primary. Still true on the current tree-only branch.

**L263–267 (polyhierarchy implemented and measured) verified accurate** —
`6_Results.tex:1795` (`sec:poly-negative`) delivers, and
`04_Appendix/7_Appendix_TuningProtocol.tex:40` confirms cross-linking is off in
the canonical configuration.

---

## Ordering, and whether anything should move to an appendix rather than be cut

**The ordering is correct and should not change.** Chapter 3 needs, in order:
the partition requirements (served by §2.2's vMF and MRL), the judge (§2.3), the
Bradley–Terry estimator (§2.4.2), and the scheduler (§2.4.3). Chapter 2's
2.2 → 2.3 → 2.4 sequence matches that exactly. The two sections at the ends —
§2.1 and §2.5 — are the two the later chapters use least, which is the right
place for them.

**One structural change is worth considering.** §2.5's surviving content, after
the cuts above, is roughly 20 lines: the routing problem, the four learned
routers, the four corpus-inducing routers, and the conjunction. All four of
those threads already have a home in §2.1, which introduces BenchBuilder and P2L
and states the gap in the same terms. Folding the residue of §2.5 into §2.1's
positioning material would remove a whole section heading and its page break —
worth perhaps another 0.3 pages beyond the line count — and would put the entire
gap claim in one place, immediately before the Synthesis restates it.

**Nothing here should move to an appendix.** An appendix costs the same pages a
body section does, and the only genuinely appendix-shaped material in Chapter 2
— the vMF density and the MRL slice argument — is *already in*
`11_Appendix_DAGConstructionFormalism.tex`, in fuller form. Moving would create
a fourth copy. Cut, do not relocate.

---

## What I could not establish

- Whether any figure planned for the freed pages needs a concept currently
  slated for cutting. I have no list of the pending figures.
- Whether the removed citations appear in the bibliography for reasons outside
  Chapter 2 (e.g. a proposal or a paper draft under `docs/`). I checked
  `report/` only; `05_Literature_and_Index/` was not scanned for orphan-entry
  side effects. Removing citations does not break the build either way — biblatex
  drops uncited entries — but if the .bib is shared with another document,
  confirm before pruning it.
