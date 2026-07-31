# Interpreting the 8-domain batch

Written 2026-07-31 against the settled 8-model RESOLVED batch (`ratings_r8_*.db`,
snapshot `20260727_042523_Headless_Run_Auto_ge`). Every number below either comes
from the verified batch table or was recomputed here from the databases; the
recomputation paths are named at each claim.

Read section 4 first if you only read one. The quantitative check it reports
changed what I think the batch is evidence for.

---

## 0. Three corrections to the premises, before anything else

These came out of reading the code and the snapshot rather than from the run, and
they change how sections 3 and 4 have to be written.

**0.1 The rubric is not induced from a 25-query representative pack.**
`TaxonomyJudgeService.generateJudgeForNode` (line 203) takes the leaf's *entire*
filtered construction pool, chunks it into batches of 25, induces per-batch
guidelines, and synthesises them. `k = 25` is a batch size, not a sample size. Across
the 52 cells the arena actually used, the induction pool runs 24 to 182 queries,
median 44. Only **one** cell has a pool under 25. The pre-registered check "are
leaves with fewer than 25 construction queries worse?" therefore has n = 1 and
cannot be run. It should be struck, not reported as a null.

**0.2 The construction/reserved separation is enforced on the rubric, not on the
tree.** The reserved filter lives in judge induction. The frozen tree's leaf
regions contain reserved-split material: of 9,141 leaf-region queries, 17.0% carry
a text flagged reserved-only in `eval_results` and a further 23.6% carry a text
flagged both ways. So the answer-key-blind claim covers *what the rubric was
written from*, and does not extend to *how the partition was drawn*. The thesis
should say which of the two it is claiming, because they are not the same claim
and only the first is enforced by the build-failing assertion.

**0.3 The split is enforced on question text, and the text space is dirty.**
`eval_results` holds 7,625 construction-only texts, 2,278 reserved-only texts, and
**2,746 texts that appear under both flags** — the id-space duplication already
recorded in `docs/`. Because the filter is a text-membership test, it removes any
text reserved under *any* id, which makes it conservative rather than leaky. I
verified the consequence directly: of the 1,569 distinct question texts the arena
judged, **0** appear in any leaf's induction pool. The answer-key-blind-at-induction
claim holds. State it as verified by measurement, not by the assertion alone.

---

## 1. What the batch establishes

**The arena recovers the model ordering wherever the key determines one.**
196/200 key-decidable pairs, 98.0%, one configuration, no per-domain tuning, eight
domains, zero crashes, zero 429s, rc = 0 everywhere. That is the headline and it
survives everything below.

**But 200 is not 200 independent facts.** I checked the ground-truth ordering the
arena is being scored against in each domain. It is the *same ordering* in seven of
eight domains; only law differs, and only by swapping Meta-Llama-3\_1-8B (0.207) and
Yi-6b-Chat (0.217). The roster was selected for a large global accuracy spread, so
the spread survives any subsample of the corpus. The batch therefore demonstrates
that the arena recovers *one* ordering, eight times, on eight disjoint question
samples. That is still a real replication — the samples are disjoint and the
verdicts independent — but it is a replication of one result, not eight results.
Write it that way.

**The per-verdict metrics are the ones with power, and they are internally
consistent.** Decomposing the batch to the 52 cells and re-aggregating reproduces
the published per-domain agreement rates exactly: 79.3 / 80.2 / 66.9 / 74.0 / 76.4 /
77.0 / 70.2 / 74.1. The aggregate table and the per-cell data are the same numbers.

**Judge-key agreement conditional on the judge committing is 86.1% pooled**, and
the per-domain range is 78.9 (law) to 90.3 (philosophy). This is the number to lead
with, for the reason in section 3.

**The induction/judging separation is verified, not merely asserted** (0.3 above).

## 2. What it does not establish

- **Nothing at cell level.** 1.6–5.0 comparisons per model pair against ~143
  needed; zero cells in any domain qualify; Cochran's Q is non-significant in every
  domain tested (0.064, 0.502, 0.682, 0.137). The per-cell reorderings are noise
  and the caterpillar in the figure plan is the right way to say so.
- **No claim about the partition.** Both arms use the same cells, the same
  questions and the same aggregation. Nothing in this batch varies the partition.
- **No usable arm contrast from ρ.** Saturated, grid step 0.0119, and two runs of
  one configuration differing only in scheduler seed moved it by six grid steps.
- **No accuracy effect from the rubric.** See section 3.
- **Not what the domain names say it is.** See section 4.4 — this is the one that
  surprised me.

---

## 3. RQ2, read correctly

### 3.1 The corrected decomposition, reproduced

Recomputed independently on the 2,788 shared key-decidable comparisons that also
carry an embedding (93.7% of the 2,976; the 188 dropped are questions whose text is
absent from the embedding cache). Every corrected statistic reproduces:

| | MAIN (rubric) | C5 (generic) |
|---|---|---|
| tie rate on key-decidable comparisons | 13.0% | 10.9% |
| domains where MAIN ties more | 8 / 8 | — |
| agreement, unconditional | 74.9% | 77.9% |
| **agreement, conditional on committing** | **86.1%** | **87.4%** |
| only-this-arm-tied | 212 | 154 |
| both tied | 150 | |
| discordant verdicts, both arms committed | 10 | 25 |

Sign test on the both-committed subset: n = 35, two-sided p = 0.017. 88% of the
unconditional discordance involves at least one arm tying.

### 3.2 What that means

**The generic prompt is more decisive, and only marginally more accurate.** The
robust effect is a 2.1-point tie-rate gap replicated in 8/8 domains. The accuracy
effect is 1.2 points, rests on n = 35, is significant in no single domain, and
reverses in engineering and philosophy. Do not write that the induced rubric
produces more wrong verdicts. It produces more abstentions.

**And the surviving effect is the one the arm bundle most plausibly explains.**
The two arms differ in four ways (`isC5` at `TaxonomyArenaService.kt:500`). Rank
them by how directly each could move a *tie rate*:

1. **Output format** — schema-enforced JSON with a tie field, against free text
   that must end in a literal `[[A]]`/`[[B]]`/`[[C]]` token. A structured tie field
   is a cheaper thing for a model to select than a `[[C]]` token at the end of a
   free-text critique. This is the most direct mechanical route to a tie-rate gap
   and it is entirely uncontrolled.
2. **User message** — a mandatory 4-step critique sequence, against "a short
   explanation". Working through four criteria gives more opportunity to conclude
   that both responses satisfy them.
3. **System prompt** — induced rubric, against MT-Bench. The variable of interest.
4. **Confidence** — judge-reported, against a hardcoded 0.85. Inert here, since
   `confidenceGate = 0.0` in both arms.

The scaffolding argument the thesis already makes still works and should be kept:
the arm with *more* scaffolding loses, so scaffolding-as-help is not the story. But
scaffolding-as-hesitation is exactly consistent with what is observed, and format
and confidence are uncontrolled. **The honest statement is that RQ2 shows no
measurable accuracy effect from the domain rubric, and a small decisiveness
difference that this design cannot attribute to the rubric rather than to the
format.**

### 3.3 The consequence for the negative control

The brief asked me to use "the criteria-free prompt beats the induced rubric" as a
negative control for rubric blindness. Under the correction it is a weaker control
than it looked — 87.4% against 86.1% is not a beating. It still does the job it was
asked to do, because the relevant fact is unchanged: **removing every domain
criterion from the prompt costs nothing measurable in accuracy.** Section 4 finds
the same thing from the other direction.

---

## 4. The construction/reserved constraint, and whether the rubric is blind

### 4.1 The check I ran

Four tests, in increasing order of power. All read-only. The geometry is cosine
distance on the 256-dimensional MRL prefix — the same slice the taxonomy routes on
(`sliceDim = 256` in every leaf) — against the mean direction of the cell's
induction pool, reconstructed exactly as the service builds it (region queries,
minus the `abs(hashCode) % 5 == 0` thinner, minus every reserved text). Sanity
check: the mean direction of a leaf's region reproduces its stored `vmfMu` at
cosine ≥ 0.9974, median 0.9997, so the reconstruction is the right geometry.

### 4.2 Test 1 — is the premise of the risk true? **Yes, and more so than assumed.**

Mean cosine distance to the induction-pool centroid, over the 52 cells the arena
used:

| | distance |
|---|---|
| construction query, in-sample (leave-one-out) | 0.3443 |
| construction query, **held out of the centroid fit** | 0.3534 |
| **held-out query, routed into this cell** | **0.5113** |
| held-out query, drawn at random | 0.6070 |

The second row is the control that matters. Splitting each induction pool in half,
fitting the centroid on one half and measuring the other, costs only 0.009 of
distance. So centroid overfitting explains almost none of the gap: routed held-out
queries really do sit 0.16 farther out than construction queries do, in 48 of 52
cells, paired Wilcoxon p = 1.3e-9.

**Routing closes 38% of the distance between chance and construction-grade
proximity.** Per domain: law 103%, psychology 82%, history 67%, physics 21%,
philosophy 13%, math 12%, cs 10%, engineering 6%.

The counter-argument in the brief — routing is the same geometry that built the
cells, so a routed query should land near its cell's construction queries — is
therefore **true in three domains and false in five**. It should not be asserted in
the thesis without this number attached.

### 4.3 Test 2 — does the distance change what the judge does? **No, and I can bound it.**

Linear probability model with **cell fixed effects** over all 2,788 shared
key-decidable comparisons, so every comparison is measured against other
comparisons in the same cell under the same rubric. Effects are percentage points
per one within-cell standard deviation of distance (SD = 0.114):

| outcome | effect | 95% CI | p |
|---|---|---|---|
| rubric arm ties | +1.02 | −0.23 … +2.26 | 0.109 |
| **generic arm ties** (no domain criteria at all) | **+1.06** | −0.10 … +2.21 | 0.072 |
| **difference, within triple** | **−0.04** | −1.39 … +1.30 | 0.949 |
| rubric arm agrees with key | −1.73 | −3.33 … −0.13 | 0.034 |
| generic arm agrees with key | −1.62 | −3.15 … −0.10 | 0.037 |
| difference, within triple | −0.11 | −1.28 … +1.07 | 0.860 |

Read the second and third rows together. Questions far from the rubric's induction
pool do get tied slightly more often and agreed with slightly less often — and the
arm that was never shown a rubric moves by the same amount. The within-triple
difference, where the *only* thing that varies is the prompt, is zero to two
decimal places.

The abstention hypothesis the correction proposed — a rubric lacking criteria for a
held-out query makes the judge abstain rather than answer wrongly — is the right
hypothesis to have posed and it does not survive. **The rubric-specific component
of the distance-to-abstention effect is bounded to ±1.4 percentage points per
standard deviation.** At n = 2,788 the design detects |r| ≥ 0.053 at 80% power; the
observed within-triple r is −0.0012.

A supporting cut, same fixed effects: among triples where exactly one arm tied, the
far half of each cell splits 108 MAIN / 73 C5 and the near half 104 / 81 — Fisher
p = 0.526.

### 4.4 Test 3 — the reason the distance is so large, and why it matters more than the blindness question

The distance gap is not a subtle semantic drift. **Most of the questions the arena
judges are not from the cell's subject at all.**

Each cell is built out of one MMLU-Pro category — mean dominant-category purity
73.8% on the construction side. But of the 1,637 held-out questions the batch
routed and judged, only **609 (37.2%)** carry the category their cell is built from:

| run domain | on-subject | routed |
|---|---|---|
| law | 88.8% | 245 / 276 |
| psychology | 64.9% | 172 / 265 |
| history | 56.5% | 74 / 131 |
| physics | 16.6% | 38 / 229 |
| engineering | 14.6% | 23 / 158 |
| math | 11.7% | 34 / 291 |
| computer science | 8.2% | 13 / 158 |
| philosophy | 7.8% | 10 / 129 |

This is not a join artefact. I read the questions. In cell `n00000159`, *Extremal
and Enumerative Combinatorics in Graphs and Numbers*, whose rubric opens
"the answer must match the unique solution derived from the problem's constraints
… empty graphs, zero remainders, collinear points", the judged questions include
"The simplest alkene has", "What is the heat shock response?" and a Hardy-Weinberg
genetics problem. In `n00000121`, *Electrical Machine Performance Calculation*,
whose rubric asks for Faraday's Law and torque equations, the judged questions
include instalment-plan arithmetic and a property-conveyance problem. Law is clean:
`n00000201`, *Real Property Title Disputes and Estates*, received 45 law questions
and one engineering question.

Mechanism: each reserved question is routed and lands in exactly one cell across
the whole batch (verified — no question appears in two run domains, and none in two
cells of one domain). A domain run judges whatever landed in its subtree. For law,
nothing else looks like law and law looks like nothing else. For a broad
quantitative cell, a great deal of chemistry, biology and economics has some
placement there and nothing better competing for it inside the subtree.

**And the judge does not care.** Same cell fixed effects, comparing on-subject
against off-subject routed questions (n = 2,788, 42% on-subject):

| outcome | on-subject minus off-subject | p |
|---|---|---|
| MAIN agrees with key | +0.48 pp | 0.840 |
| MAIN ties | −0.44 pp | 0.811 |
| MAIN-minus-C5 agreement | −0.72 pp | 0.680 |
| MAIN-minus-C5 tie | +0.85 pp | 0.669 |

Hand the judge a chemistry question under a combinatorics rubric and it agrees with
the answer key at the same rate as when the question is combinatorics. That is the
sharpest available evidence for the thesis's central finding, and it is far
stronger than the C5 contrast, because it varies the *material* rather than the
prompt.

### 4.5 Test 4 — the cell-level correlations, reported honestly

Across the 52 cells, judge-key agreement correlates **positively** with the
distance of the cell's routed questions from its rubric pack: r = +0.362, p = 0.008.
That is the wrong sign for the blindness hypothesis, and it is an artefact. Once
domain fixed effects are applied it falls to r = +0.206, p = 0.142. The raw
correlation is carried entirely by the between-domain contrast (r = +0.632 across
the eight domain means, p = 0.093): law routes on-subject and is the hardest domain
for the judge; math routes off-subject and is the easiest. Do not report the raw
number.

One cell-level result reached p < 0.05 and I am reporting it so it is on the record
rather than quietly dropped: within domains, the MAIN-minus-C5 *tie rate* per cell
correlates with routed-query distance at r = −0.280, p = 0.047. It has the wrong
sign for blindness (more distance, *less* excess abstention by the rubric arm), it
is one of roughly a dozen tests run here, and the query-level test of the same
quantity with 50× the power gives −0.04 pp with a CI straddling zero. It is noise.

### 4.6 What the check settles

- **The risk premise is confirmed as geometry.** Rubrics are applied to material
  well outside the pool they were induced from, and in five of eight domains
  mostly outside the *subject* they were induced from.
- **The risk has no measurable behavioural consequence, and the null is tight.**
  Bounded to ±1.4 pp per SD of distance for abstention and ±1.3 pp for agreement,
  within triple, with cell fixed effects.
- **This is consistent with the negative control and with the whole thesis.** A
  rubric cannot be blind in a way that matters if the rubric is not what decides
  the verdict. In RESOLVED mode, with option injection at 93.2–99.8% and ~95% of
  traces stating their own answer, the judge checks the answer. Three independent
  measurements now say so: the generic prompt matches the rubric (§3), off-subject
  questions score like on-subject ones (§4.4), and distance from the induction pool
  predicts nothing arm-specific (§4.3).
- **The boundary of that conclusion.** All of this holds where the judge can verify
  the answer. It says nothing about a corpus where it cannot, and there the rubric
  is the only signal and its coverage would be the whole game. Say this explicitly;
  it is the transferable part.

---

## 5. Limitations, ranked by threat to the thesis's claims

**1. The domain label does not describe the question population.** 62.8% of judged
questions come from a different subject than the cell they were judged in; five of
eight domains are above 83%. The thesis's premise is per-sub-domain ranking. A
"math ranking" computed on 34 math questions and 257 others is a ranking on a
quasi-random subsample of the reserved pool, which is also why the eight domains
recover one ordering (§1). This threatens the framing more than anything else in
the list, it is newly measured, and it is not currently in the text.

**2. The judge checks answers, not reasoning.** Already the thesis's central
finding. It bounds every rubric-related claim, including the one in §4.

**3. The roster is not length-matched.** 220–1494 median characters, 6.79×, against
2.91× deliberately held on the superseded 12-model roster. Verbosity now correlates
with capability and cannot be separated. The accuracy spread that made ρ usable
bought it with the verbosity control.

**4. Cells cannot resolve model pairs.** 1.6–5.0 comparisons per pair against ~143.
Structural. Every domain except psychology and cs stopped on budget exhaustion, not
convergence.

**5. The two arms differ in four ways, and the surviving effect is the one most
confounded.** §3.2. The decisiveness gap is at least as plausibly a JSON-tie-field
versus `[[C]]`-token artefact as a rubric effect.

**6. Eight domains are not eight independent tests.** Identical key ordering in
seven of eight. The 196/200 figure should be presented with that attached.

**7. Hyperparameters are fitted on the construction split, not confirmed on it**
(Constraint B). The construction side carries both tree induction and tuning, so
the 70/30 split protects the rubric and the evaluation but not the hyperparameters.
Nothing in this batch bounds that.

**8. `arx_0314` answers bare on 21.4% of items** and is of unknown provenance,
sitting under the exclusion threshold rather than clear of it. It is rank 2 of 8, so
it participates in most decidable pairs.

**9. ρ is saturated** and has never discriminated between arms. One table, three
decimals, one sentence.

**10. One corpus, one judge model, one roster.** Nothing shows transfer.

Item 1 should be added to the limitations section. Items 2–5 are already there or
planned. Items 6 and 7 are currently missing and are cheap to state.

---

## 6. Visualisation plan

Read with `report/Figures/FIGURE_PLAN.md`. This revises that plan rather than
repeating it. Existing conventions hold: `make_<name>.py`, `matplotlib.use("Agg")`,
real data only, assert every published number before drawing, greyscale and hatch
only (the thesis prints monochrome), PDF beside the script.

### Changes to the existing plan

- **F2 `rubric_vs_generic` must be rebuilt, not regenerated.** Its stated claim —
  "the generic MT-Bench prompt beats the domain rubric 97 to 51" — is the
  unconditional statistic the correction retired. A slope chart of unconditional
  agreement now asserts something the data does not support. Replace it with V3
  below.
- **F4 `rank_recovery_grid` needs one annotation.** The grid is mostly white
  because the key ordering is the same in seven of eight domains. Say so in the
  caption or the figure argues for more than it shows.
- **F6 `judge_verdict_composition` — cut.** V3 carries the denominator point and
  the figure count is now heavier.
- **F1, F3, F5 stand as specified.**

### V1 — `routing_provenance` *(prototyped, builds, verified)*

**Claim.** Cells are built from one subject and then judged on another. Mean cell
construction purity 73.8%; on-subject share of judged questions 37.2% pooled, and
under 17% in five of eight domains.

**Encoding.** One horizontal row per run domain, sorted by on-subject share. A
full-width hatched bar is the routed set; a solid grey bar is its on-subject part,
labelled inside where it fits and outside where it does not. A hollow diamond on
the same 0–100% axis marks the cells' construction-side purity. A dashed rule marks
the pooled 37%.

**Why this and not a 14-category stacked bar.** Fourteen source categories cannot be
told apart in greyscale and the reader does not need them — the claim is binary
(the cell's own subject, or not). Putting purity and provenance on *one* axis makes
the contrast a length comparison inside each row instead of a comparison between two
charts, and the 74%-versus-37% gap is the entire finding.

**Data.** `snapshots.db` graph for leaf `queryIds`; `embeddings_cache.queries.
ground_truth_category` for the construction-side subject; `eval_results.category`
for the routed question's subject; `ratings_r8_*.db:match_history` for what was
judged where. **Placement:** `5_Results.tex` §5.1, or Experimental Design beside F5.
It reframes everything after it, so it should come early.

### V2 — `rubric_reach` *(prototyped, builds, verified)*

**Claim.** Two halves. (a) The rubric is applied well outside its induction pool —
routing closes 38% of the chance-to-construction gap, 6–21% in five domains.
(b) That distance moves the arm with no rubric exactly as much as the arm with one.

**Encoding.** Panel (a): one row per domain; a segment spanning from
construction-grade distance (0.353) to chance (0.607), with a filled dot where
routing actually lands. The segment is the range the answer could take and the dot
is the answer, so "law sits at the left end, engineering at the right" is a
position, not a number to decode. Panel (b): a six-row forest plot, percentage
points per SD of within-cell distance, with 95% CIs, zero rule, grouped tie-rate
and agreement, each group ending in the within-triple difference drawn as a filled
square.

**Why this and not a scatter of agreement against distance.** A scatter of a null
is unreadable — the reader cannot tell a null from an underpowered mess. The forest
plot shows the null *and* its precision, and putting the rubric arm directly above
the rubric-free arm makes "these are the same" a vertical alignment rather than a
p-value in prose. Panel (a) is what stops the null being dismissed as "you found
nothing because there was nothing to find": the exposure is real and large.

**Data.** As V1, plus `embeddings_cache.embeddings` (256-dim prefix) and both
conditions of `match_history`. **Placement:** the appendix section on the
construction/reserved split, or `5_Results.tex` after the verdict-mechanism figure.

### V3 — `rubric_decisiveness` (replaces F2)

**Claim.** The rubric arm abstains more and is not less accurate. Tie rate 13.0%
against 10.9%, same direction in 8/8 domains; agreement conditional on committing
86.1% against 87.4%; the both-committed sign test is 10 against 25 on n = 35.

**Encoding.** Two panels. (a) A slope chart of *tie rate on key-decidable
comparisons*, MAIN to C5, one line per domain — eight lines all sloping the same
way, which is the replication. (b) Paired dumbbells of agreement conditional on
committing, one row per domain plus pooled, with a binomial CI on the pooled row
only. Engineering and philosophy cross; leave them crossing and label them.

**Why this and not the original slope chart of unconditional agreement.** The
unconditional rate blends decisiveness and accuracy, which is precisely the
conflation the correction identified. Splitting it into the two panels makes the
claim structure visible: the consistent effect is on panel (a), the panel (b)
effect is small and two domains reverse. A reader who sees only panel (a) still
reaches a true conclusion.

**Data.** Both conditions of `ratings_r8_*.db`, joined on (`eval_question_id`,
`model_a`, `model_b`), restricted to key-decidable comparisons.
**Placement:** `5_Results.tex` §5.2.6 `sec:res-c5`, in place of F2. The section-title
fix that F2 flagged still applies, and now needs different wording: at rank level
the arms agree, at item level they differ in *decisiveness*.

### V4 — `arm_difference_ladder` (small, Experimental Design)

**Claim.** The RQ2 contrast varies four things, and they are not equally innocent.

**Encoding.** A four-row table-figure: system prompt / user message / output format
/ confidence, each row giving MAIN's value, C5's value, and a mark for whether it
could plausibly move a tie rate. Inline TikZ, following the Method chapter's
convention. Not a chart — the content is categorical and four rows deep, and a
chart would be decoration.

**Why at all.** It is the fastest way to stop a reviewer reading the decisiveness
gap as a rubric effect, and §3.2 shows the argument needs to be made structurally
rather than in a sentence. **Placement:** `4_Experimental_Design.tex`, adjacent to
F5, which already draws the shared triples.

### Priority

V1 → V3 → V2 → V4, then the existing F1 and F3. V1 first because it changes what
the rest of the chapter means.

---

## 7. What to run next

**Free, do it — reanalysis of verdicts already in hand.**

1. **Re-run every headline restricted to on-subject questions.** 609 comparisons
   pooled; law (245), psychology (172) and history (74) can each carry a per-domain
   agreement rate, and math/cs/philosophy/engineering cannot. If agreement and the
   arm contrast hold on the on-subject subset, limitation 1 is bounded and the
   thesis can say so; if they move, that is a finding. Cost: an hour. This is the
   highest value item on the list.
2. **Length-matched subsample of the roster.** Take the models within a ~3× median
   character band, refit, and report whether recovery and agreement survive. Bounds
   limitation 3 without any API call.
3. **State the key ordering across domains** (one table, already computed) and
   attach it to the 196/200.

**Cheap, worth it.**

4. **Re-run one domain with routing restricted to same-category questions.** Math
   or engineering, where the effect is largest. Confirms that the provenance issue
   is routing behaviour rather than a taxonomy defect, and gives an on-subject
   arena to compare against. Cost: one domain of judge calls.

**Expensive, and the only thing that would actually answer the rubric question.**

5. **An option-blind arm.** The rubric question is unanswerable while the judge can
   verify the answer. Removing option injection makes the rubric the only signal and
   is the one condition under which rubric coverage — and therefore rubric blindness
   — could matter. `arena_history_optionblind.toml` already exists. One domain,
   both arms. If the arms separate there and only there, the thesis gains its
   sharpest positive result. If they do not, the negative result becomes airtight.

**Do not.**

6. More seeds for ρ. It is saturated; more seeds measure the scheduler.
7. More budget per cell. 1.6–5.0 against ~143 is not a budget shortfall that any
   affordable run closes; it is structural and should be reported as such.

---

## Reproducing the numbers here

- §4.2, §4.3 and the geometry: `report/Figures/make_rubric_reach.py` recomputes all
  of it from the databases and asserts every published value before drawing.
- §4.4 routing provenance: `report/Figures/make_routing_provenance.py`, same
  convention.
- §3.1, §4.5 and the per-cell table: `.claude/tmp_abstention_distance.py` and
  `.claude/tmp_rubric_blindness.py` (scratch; read-only, no API).
- §0.3 leakage check and §1 key ordering: recomputed inline against
  `mmlu_pro_dataset_cache_v2.db` and the eight `ratings_r8_*.db`.
