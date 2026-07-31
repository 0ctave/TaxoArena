# Pre-registration: MT-Bench-style general judge as a no-partition baseline

Written 2026-07-27, **before any comparison numbers exist**. The arms have not been
run. Recorded now because three results in this project inverted after the fact and
the reframings only held up where the reading had been fixed in advance.

## The question

Does judging inside induced cells, with cell-specific rubrics, produce model rankings
closer to ground truth than general-purpose pairwise judging over editorial domains?

This is the **no-taxonomy baseline** the examiner review flagged as missing. It is a
different control from `GENERIC_JUDGE`, and the difference matters:

| arm | partition | rubric | what it controls |
|---|---|---|---|
| `GENERIC_JUDGE` | shares MAIN's leaves | generic | rubric specificity |
| **`C5` / this prereg** | **none — editorial domains** | generic (MT-Bench form) | **the partition itself** |

`GENERIC_JUDGE` replays MAIN's leaf-scoped triples, so it shares the partition it
would need to be a control for. It cannot answer this question. C5 can.

## Design: paired, and that is a deliberate deviation

Both arms judge an **identical question set**, with the same models and the same judge
model. Only the grouping and the rubric differ.

MT-Bench as originally used samples independently, because it has no partition to
compare against. Here the partition is the treatment, so pairing is what isolates it.
Independent sampling would add variance orthogonal to the thing under test and buy
nothing but superficial fidelity to the original protocol.

**Write it up as:** *"Unlike the original MT-Bench protocol, both arms judge an
identical question set, so the comparison is paired and isolates the partition."*

## Comparability: what may and may not be compared

C5 (`GENERIC_PAIRV2`) uses `GenericPairwiseJudgePrompt` with `[[A]]/[[B]]/[[C]]`
parsing; MAIN uses the structured JSON schema. Three consequences:

**Comparable** — winners; the BT ordering derived from them; tie counts, PROVIDED ties
are defined identically on both sides (`[[C]]` on C5 against schema `TIE` on MAIN).

**NOT comparable** — confidence (C5 emits a flat 0.85; MAIN emits real values), and
parse-failure rate. The failure *modes* differ, not merely the rates: a malformed
structured response fails loudly, whereas a C5 response with no marker returns INVALID
silently via `lastIndexOf("[[A]]")`.

**Operational consequence, easy to miss:** `confidenceGate` must be **disabled for both
arms**. At a flat 0.85 it admits every C5 verdict while filtering MAIN's, so leaving it
on would silently change which verdicts enter each fit and the arms would no longer be
paired in the only place that matters.

## Matched sampling: the domain IS the union of its leaves

Sampling must be matched, not independent. If this system judges the questions its
leaves contain while the MT-Bench arm judges "random queries of each domain", the two
arms see different question sets and the comparison inherits sampling variance
orthogonal to the treatment.

Every leaf sits under exactly one depth-1 domain, so **the union of a domain's leaves'
questions IS that domain's question set**. Sample once per domain, judge that same set
both ways:

| | questions | rubric | BT fitted |
|---|---|---|---|
| this system | domain set | each question under ITS OWN leaf's rubric | per leaf, rolled up |
| MT-Bench arm | **same set** | generic, no rubric | directly at the domain |

Identical questions, identical models, identical judge model. The only difference is
whether the partition is used.

## Roll-up: pool sufficient statistics, fit once

The per-leaf arm must become one domain-level ranking. Three options, not equivalent:

- **pool sufficient statistics, fit once** (`aggregateLeafScores`) — CHOSEN
- average per-leaf theta — reintroduces the gauge problem, since each leaf centres its
  own scale
- inverse-variance weighting — better than averaging, still gauge-dependent

Pooling is chosen because it makes the two arms **identical in estimation**, so any
difference between them is attributable to the rubric rather than to the aggregation.
State this explicitly in the write-up: a reader will otherwise wonder whether the
roll-up is doing the work.

The consequence is worth naming — under pooling, the partition affects only WHICH
RUBRIC judged each verdict, not how scores combine.

*(To verify before launch: that `aggregateLeafScores` pools sufficient statistics
rather than combining fitted per-leaf scores. The choice above depends on it.)*

## What this arm tests — and what it does not

Narrower than "our system versus MT-Bench":

> Does judging a question under a rubric induced from its own leaf produce a better
> domain-level model ranking than judging it under a generic rubric?

It does **not** test whether the partition helps aggregation — pooling makes that
identical by construction. It does **not** test cell-level ranking structure — that is
the granularity screen, which is offline and already run. It tests **rubric
conditioning at matched everything-else**.

**Honest prior, recorded before the run:** this likely comes back NULL with options
present. On Math, MAIN and GENERIC_JUDGE agreed on 99.4% of winners, and the 88.8%
GT-agreement was driven by correctness verification rather than by rubric application.
C5 uses a different generic template from GENERIC_JUDGE, so it is not literally the
same test — but it is close enough that a large difference would be surprising and
would need explaining rather than celebrating.

That is an argument for running this **options-blind** if budget allows, since
withholding the options is the only regime in which the rubric has been shown able to
matter. With options present, the judge can verify the answer and the rubric is
decorative.

## Scope condition: substantive-response models only

**The roster is restricted to models producing substantive responses. Answer-only
systems are out of scope for this evaluation design.**

Stated explicitly rather than left implicit, because it resolves an ambiguity that
would otherwise make the options-blind arm uninterpretable. A rubric — reasoning-based
or content-based — has nothing to grade in a response that carries no content.

Note what this is NOT. The four models in the original 8-model run were not terse by
style: `getRobustTrace` synthesised "The model selected option F: ..." because the
ingest had stored an empty `model_output`. That was a pipeline stub, not model output,
and the re-ingest fixed it — those models have real traces under `generated_text`. So
the bare-answer problem was a data defect that is now repaired, not a standing design
tension.

The 12-model length-matched band satisfies this condition by construction (median 486-
1413 chars), so for this run the tension does not arise.

## A mechanism for the prediction, worth registering separately

The predictions above are empirical: law should show a rubric advantage, math should
not. They currently have no stated mechanism.

**Candidate mechanism:** induced rubrics can encode CONTENT criteria, not only
REASONING criteria. A rubric induced on a history leaf may encode "cites the correct
period" or "names the right actor" — properties of the answer checkable without a
derivation. A rubric induced on a math leaf encodes derivation properties, because
that is what math content offers. Which kind a cell yields depends on what its content
supports.

**If that holds, it predicts which domains admit content-based criteria** — and it
would use the same predictor as the arena prediction, giving the empirical hope a
stated cause.

**Proposed offline test, no arena calls:** classify the rules in the 87 leaf rubrics
(already on disk in the frozen snapshot's `judgeRubric` field) as derivation-property
versus content-property, via an LLM pass. Then correlate the content-property fraction
against each cell's hapax / reusable-term measure. Prediction: enumerative cells
produce content-heavy rubrics, conceptual cells produce reasoning-heavy ones.

**UNVERIFIED — source needed before this is registered as a prediction.** The hapax
figures motivating it (enumerative cells at >= 0.836 — Other, Health; Law at 0.580)
were supplied in discussion and I could not locate them in `docs/`. The only hapax
reference found is in `docs/measurement-discipline.md:79-81`, and it is a RETIRED
measurement: a rubric-to-cell vocabulary ratio that was withdrawn because it "was not
even commensurable — rubric vocabulary overlaps the cell's hapax terms, which the
denominator excludes by construction." If the 0.836/0.580 figures come from that
retired instrument, the mechanism needs a different predictor. Locate the source and
confirm it is not the withdrawn ratio before this becomes a registered prediction.

## Domains: four, chosen for a built-in control

`math` (393 reserved), `physics` (378), `chemistry` (338), `law` (287).

The span is deliberate. From the domain-reordering screen at the 11-model band
(offline, GT accuracy only, 2,000-draw size-matched permutation null):

```
math   rho = 1.000  p = 1.000   models do NOT reorder — identical to the global ranking
law    rho = 0.955  p = 0.008   models DO reorder — about 6 adjacent swaps vs ~1 for
                                a random same-size sample
```

## Predictions, fixed before the run

1. **On `math`: no difference between arms.** There is no cell structure for the
   partition to exploit, because math's own ranking is identical to the global one. A
   per-leaf advantage here would indicate an artifact, not a finding.
2. **On `law`: per-leaf beats per-domain**, if the partition helps at all.
3. `physics` and `chemistry` are intermediate and not predicted.

**What counts as "not flat" on math, fixed in advance.** At the 12-model roster the
Spearman grid is 0.0035, so the smallest representable difference is one grid step.
**A difference of two grid steps or more — |d rho| >= 0.007 — counts as a real
difference on math and therefore as a FAILED null.** Anything below that is one
quantisation step and is read as flat. Without this threshold a small math difference
could be argued either way after the fact, which would destroy the value of having the
null arm at all.

**Why the pair is stronger than "per-leaf wins overall":** a uniform advantage across
both math and law would suggest something other than the partition is driving it —
rubric verbosity, prompt length, schema effects. The math null is what makes a law
result attributable to the partition.

## Primary outcome, fixed before the run

**Primary: Spearman rho against GT accuracy, per domain.** This is the partition claim.
Bounded honestly: the 12-model roster gives a grid of 0.0035 (n=11 would be 0.0046), and math's GT ordering is
already rho = 1.000 against global, so math has little room to differ in EITHER
direction — which is exactly why it is the null arm rather than a second test.

**Secondary: GT-agreement per verdict.** A proportion with far more power (SE ~1%),
but it measures the JUDGE rather than the grouping, so it cannot carry the partition
claim. Reported alongside as the judge-side check.

### Disattenuation is mandatory, and its limits are stated in advance

Two-sided — `rho_obs / sqrt(r_A * r_B)`, i.e.
`rho_obs / r` when both arms share a cell size — at the corrected constant
**c = 2.52**, not the published 7.66. Domain cells (~250-390 questions) and leaf cells
(~27-53) differ by an order of magnitude in size, so a raw rho-against-rho comparison
between the two arms is invalid without it.

**Magnitudes at c = 2.52, so the corrected number is not over-interpreted either way:**

| cell n | r | correction (two-sided, 1/r) |
|---:|---:|---:|
| 27 (small leaf) | 0.9146 | +9.3% |
| 40 (median leaf) | 0.9407 | +6.3% |
| 300 (domain) | 0.9917 | +0.8% |

The domain arm's correction is nearly a no-op; the leaf arm's is ~6%. The differential
is about **5.5 points of relative adjustment**, which is good news for saturation risk
— under the old c = 7.66 the leaf correction was large enough to push values past 1.0,
which is exactly what forced the earlier discriminative analysis to reason around a
clipping column. But it also means **disattenuation will not rescue a large raw
difference**. If per-domain beats per-leaf by more than a few points raw, the
correction does not reverse it.

Note the two-sided form is `1/r`, not `1/sqrt(r)`: both sides of
`rho(arena ranking, GT ranking)` are estimated on the same n questions, so the GT
ranking is itself a finite-sample estimate rather than a fixed truth. The one-sided
figures (+3.1% at n=40) apply only when one measure is perfectly reliable, which is
not the case here.

**c = 2.52 is the 11-model-band value.** It is a property of the roster, not of the
corpus. If this run uses a different roster — including the 12-model set — the
constant must be REFITTED FIRST with `tools/analysis/reliability_constant.py`, which
takes a roster list. Skipping that step reintroduces precisely the dependency that
already invalidated three results in this project.

## Run conditions

- **Shuffled question sampling** (`BtMatchScheduler`, uniform over each cell's full
  pool). The centrality-ordered sampler used 66% of each leaf's pool and
  systematically omitted the least prototypical third; a baseline run under the old
  sampler would not be comparable to the re-run.
- Roster: the 12-model length-matched set (r(len,acc) = +0.286 against +0.597 for the
  full 36), so the format artifact is controlled by construction in both arms.
- Isolated ranking DB per arm. `match_history` is keyed by `(snapshot_id, condition)`
  and a re-run CLEARS the prior rows — this destroyed the frozen Math MAIN results once
  already.

## Order of work

1. Shuffled Math re-run, against the centrality baseline (66% pool utilisation,
   94.0% GT-agreement). **This must land first**: until it does, it is not known
   whether the baseline the C5 comparison would be measured against survives the
   sampling fix.
2. C5 on the four domains.
3. The two BT orderings side by side against GT accuracy.

## Void conditions

The comparison reports nothing if: the arms judge different question sets; the
`confidenceGate` is left on for either arm; the two arms use different question
samplers; or ties are defined differently between `[[C]]` and schema `TIE`.

---

# Addendum: the NO_KEY condition

Written 2026-07-28, **before the law results exist**, so the design is not shaped by
what law turns out to show.

## Why options-blind alone is insufficient

Withholding the options block does not remove the correctness channel, because
**94.8% of traces state their own answer** ("The answer is (C)", `\boxed{C}`,
"Answer: A"). A judge shown two stated answers and the question stem can still solve
and match. The stated answers must be stripped as well, and that is a second,
independent manipulation.

## Stage 0 — measure the channel before removing it

**(a) Per-model statement rate, 11-band. DONE.** Range 89.8% (Qwen1.5-72B-Chat) to
100.0% (arx_3), spread 10.2 points; post-strip median length falls ~1%, so no model is
gutted. The asymmetry is modest but non-zero.

Note the direction of the risk: a LOW detection rate means either no answer stated OR
an answer stated in a form the regex misses. Qwen1.5-72B at 89.8% is therefore the
model most likely to LEAK through an uncovered phrasing, not the one least likely to
state an answer.

**(b) Stem-only probe. NOT YET RUN.** Send the judge model the question stems alone —
no options, no responses — and measure accuracy. **This bounds the residual leak
directly and is the honest ceiling on the whole condition.** If the judge answers well
above chance from the stem, NO_KEY cannot fully remove the shortcut and the arm must
be read accordingly. 241 single calls; must run BEFORE the condition is built.

## Stage 1 — the strip

Applied at **prompt assembly, not at ingest**: the frozen corpus stays untouched and
the condition stays reversible. Identical regex to both traces.

Patterns: `the answer is (A)` / `the answer is A` / `Answer: A` / `answer is (A).` /
`**A**` / `so we get (C)` / `\boxed{A}` — case-insensitive, ALL occurrences, not only
terminal.

Replace with a neutral token `[ANSWER]` rather than deleting, so mid-derivation
mentions ("so we get (C), which means the ratio is...") stay grammatical and both
traces are altered identically.

**Validation gate, before any judging.** Sample 30 stripped traces and count how many
still name an answer. **Above a few percent, a null result means "the strip failed",
not "the rubric does not matter."** Log the residual rate as a run diagnostic so it is
visible rather than assumed.

## Stage 2 — the condition

`NO_KEY`: options block suppressed at the assembly site, both traces stripped, MAIN
rubric otherwise unchanged, same questions, `confidenceGate` disabled.

## Stage 3 — the reading, FIXED IN ADVANCE

Removing the channel also makes the task harder, so a rho drop alone is consistent
with two incompatible readings. The tie rate separates them:

| rho | tie rate | reading |
|---|---|---|
| collapses | **spikes** | the judge cannot decide — the task became impossible |
| collapses | **stable** | the judge decides differently — it WAS verifying |
| holds | — | reasoning carries the signal; the rubric null needs another explanation |

**The discriminator that matters: split-half reliability of the NO_KEY judge.** A judge
ranking systematically on quality stays self-consistent while diverging from GT; a
noisy judge diverges from itself too. No extra calls, and it separates "quality
judgment that imperfectly tracks accuracy" from "noise" — which a pre-registered target
range on rho cannot do.

**Primary: GT-agreement** (proportion, ~1,200 comparisons, SE ~0.7%).
**Secondary: rho, reported under BOTH tie policies** — half-weighted and ties-dropped
differ by up to 0.029 with inconsistent direction, which is larger than most effects
here.

## Scope

- **Roster: the 11-band only.** Answer-only systems are out of scope for this design.
- **Domain: law.** Math would return a null for reasons unrelated to the manipulation.
- **Arms: MAIN and NO_KEY on the same questions.** CROSS-CELL under NO_KEY is the
  natural third arm and the only regime where cross-cell means anything — cost it
  before committing.

## Order

Stage 0(b) first. The stem-only probe may show the ceiling is low enough that the whole
condition is worth less than it looks, and it costs 241 calls against a condition that
costs thousands.

## What must be preserved — and what must not be copied

**The corpus is NOT backed up for this condition, deliberately.** The strip happens at
prompt assembly, so `model_output` is never written. MAIN and NO_KEY read identical
rows and the manipulation exists only as a string passed to the LLM call. That is the
reason for stripping there rather than at ingest: one corpus, one frozen artifact,
conditions differing only in prompt construction. A corpus copy would preserve the
INPUT, not the manipulation, and would answer nothing.

**What must be preserved is per-verdict, not per-corpus.** Each NO_KEY verdict row must
carry:

- `strip_residual` — did the stripped trace STILL name an answer, after stripping?
- optionally a hash of the stripped text actually sent

Without this, a surprising NO_KEY result cannot be attributed: there is no way to tell
whether the strip worked *on those specific comparisons*. The corpus would not answer
it either, since it holds the unstripped text.

**Two things that DO warrant a backup, neither of them the traces:**

1. `ratings.db` — `node_bt_states`, `node_pair_stats` and `match_history` accumulate
   across runs, and NO_KEY adds rows under a new condition suffix. A wrong condition tag
   would contaminate the law baseline. Snapshot before the run, same discipline as
   `mmlu_pro_dataset_cache_v2.db.bak-before-trace-backfill`.
2. **The law `MAIN_verdicts.csv` export.** It is the baseline NO_KEY is measured
   against, and it is written once at end-of-condition rather than incrementally, so a
   later crash or overwrite in the same output directory loses it. Copy it out of the
   run directory as soon as law lands.

**If the strip were ever moved to ingest** — it should not be — it must write a NEW
column (`model_output_stripped`), never overwrite. The `generated_text` backfill is the
precedent for in-place modification with a sha256 fingerprint over every other column,
and that was justified because it was a REPAIR. A manipulation is different: both
versions must stay queryable side by side.

---

# Addendum 2 (2026-07-29, before either run): psychology and engineering

Registered BEFORE launch, after Math/law/philosophy/history completed. The
screen-predicts-arena pattern currently rests on one null point (Math). These
two runs make it a paired test on fresh domains:

- **Psychology** (238 reserved) — reorders under BOTH roster policies
  (p = 0.001 per-domain / p = 0.000 band). **Prediction: MAIN > C5 in
  direction under both tie conventions**, magnitude >= 0.007 under at least one.
- **Engineering** (267 reserved) — does NOT reorder under either policy
  (p = 0.962 / 0.706). **Prediction: no difference — |d rho| < 0.007 or
  inconsistent sign across conventions.** A per-leaf advantage here would
  indicate an artifact, exactly as the Math null clause stated.

Same design as Runs C-E: 12-model roster, both arms on shared questions,
bootstrap floor, per-(leaf,pair) shuffle, confidenceGate disabled, isolated DBs,
threshold 0.007, both tie conventions reported.

---

# Addendum 3 (2026-07-30, before either run): physics and computer science

Registered BEFORE launch, after math, law, philosophy, history, psychology and
engineering completed. These two close the two thinnest parts of the record: the
last untested screen-flagged domain, and a third clean null.

## The screen, recomputed at the roster the arena uses

An earlier generation of the screen ran at an 8-model and then an 11-model band.
Both are superseded. The classification below is computed at the 12-model Run-B
roster, which is the roster every paired arena run uses, 2000-draw size-matched
permutation null, seed 42:

    flagged (p < 0.05)     psychology 0.000, physics 0.004, history 0.009, law 0.011
    threshold region       business 0.052, philosophy 0.053, health 0.070
    clear (p > 0.15)       biology 0.173, chemistry 0.173, other 0.242,
                           economics 0.266, math 0.289, computer science 0.751,
                           engineering 0.817

Two facts about the existing record that this addendum must state rather than
smooth over. Philosophy sits at p = 0.053, OUTSIDE the flagged set, and produced
the largest per-leaf advantage of all six completed domains (+0.049 / +0.042).
And math, at p = 0.289, was registered as a null arm and instead returned a
verdict for the partition-free arm. The screen is therefore not a clean predictor
and is not claimed as one here.

## Physics

546 reserved questions, 12 leaves, median leaf 34. The only untested domain in
the flagged set, and the only domain besides math with double-digit leaf count.

**Prediction: MAIN > C5 in direction under both tie conventions**, magnitude
>= 0.007 under at least one. This is the same prediction that held in law,
philosophy, history and psychology.

Secondary, and registered because physics is the only test available of a
confound already identified: math has the most leaves (13) and the only leaf
pairs surviving Bonferroni correction for genuine ranking divergence. Whether
that reflects finer resolution or simply more pairs tested is not separable in
this corpus, because cell depth and cell size are confounded. **Physics at 12
leaves is the nearest comparison. No prediction is registered on it** — the
observation is recorded so that whatever physics shows cannot be presented
afterwards as though it had been anticipated.

## Computer science

208 reserved questions, 3 leaves, median leaf 49. The clearest untested null on
the screen and the cheapest run available.

**Prediction: no difference — |d rho| < 0.007, or inconsistent sign across the
two tie conventions.** A per-leaf advantage here would indicate an artifact
rather than a finding, exactly as registered for engineering in Addendum 2.

## Design

Unchanged from Runs C-H: 12-model Run-B roster, both arms on an identical
question set, mandatory 66-pair bootstrap floor, per-(leaf, pair) query
shuffling, confidenceGate disabled for both arms, decisive threshold
|d rho| >= 0.007 (grid 0.0035 at M = 12), both tie conventions reported,
isolated ranking database per run.

## What these runs cannot settle

Neither is expected to change the central findings. The judge decides on answer
correctness; the partition does not create evaluative diversity; the per-leaf
advantage is a rubric-precision effect on a shared ranking rather than
resolution of sub-domain specialisation. These two runs test the edges of the
screen's predictive claim, nothing more, and are registered on that basis.

---

# Addendum 4 (2026-07-30, before the run): mathematics re-run on a repaired scheduler

Registered BEFORE launch. This addendum exists because the thesis's one failed
pre-registered prediction is confounded with a scheduler defect that every other
paired run had fixed, and that was not noticed until after all seven other
domains had completed.

## The confound

Pair coverage across the paired runs, counting distinct model pairs with at
least one comparison out of the 66 possible on a 12-model roster:

    math          20 / 66      46 pairs never compared
    law           66 / 66
    philosophy    66 / 66
    history       66 / 66
    psychology    66 / 66
    engineering   66 / 66
    physics       66 / 66

Mathematics ran before commit `5e1be09` (mandatory 66-pair bootstrap floor with
an in-run coverage assertion) and before `a5c36fd` (per-(leaf, pair) question
shuffling). Its Bradley-Terry fit therefore rests on a leader-centric star of 20
pairs, with the top model appearing in 55 percent of all comparisons, while every
comparison domain has a complete comparison graph.

Both arms of the math run shared that structure, so the PAIRED contrast is not
invalid. What is not supported is the further step the thesis currently takes:
attributing math's negative result to a property of the domain, when the estimate
comes from a graph three times sparser than every domain it is compared against,
and sparse graphs are where Bradley-Terry estimates are least stable.

## What is being re-run

Mathematics, both arms, identical configuration to Runs C-J: 12-model Run-B
roster, both arms on an identical question set, mandatory 66-pair bootstrap
floor, per-(leaf, pair) query shuffling, confidenceGate disabled, decisive
threshold |d rho| >= 0.007, both tie conventions reported, isolated ranking
database. The original run is preserved at `ratings_math_paired.db.final` and is
not overwritten.

## Prediction, fixed before the run

The original registration made math the null arm: NO DIFFERENCE between arms,
because the screen places math at p = 0.289 at the 12-model roster and its models
do not reorder. That registration stands unchanged and is what this re-run tests.

**Predicted outcome: |d rho| < 0.007, or inconsistent sign across the two tie
conventions** -- the same criterion engineering met.

The original run returned -0.064 half-weighted and -0.007 with ties dropped, both
favouring the partition-free arm, which FAILED that registration.

## How each outcome will be read, fixed in advance

1. **The re-run reproduces a negative beyond threshold.** The failed null is a
   real property of mathematics and not a scheduler artifact. The confound is
   eliminated and the finding strengthens, because it now rests on a complete
   comparison graph.
2. **The re-run returns a null.** The original failure was an artifact of the
   sparse comparison graph. The thesis reports BOTH runs, states that the earlier
   one is superseded on the grounds recorded here, and the six-domain picture
   becomes four flagged domains positive and two cleared domains null.
3. **The re-run returns a positive beyond threshold.** Math would join the
   flagged domains despite the screen clearing it, which contradicts the screen
   in the opposite direction from philosophy. This would be recorded as a
   screen failure, not as support for the partition.

Outcome 2 is the one that most simplifies the thesis, which is precisely why the
reading is fixed here rather than after the numbers exist. Reporting only the
re-run and discarding the original would be unacceptable under any outcome; both
appear, with the reason for preferring one stated.

## What this cannot settle

A single re-run at one seed does not separate scheduler effect from run-to-run
variance. If outcomes 1 and 2 differ only marginally, the honest conclusion is
that math's result is not stable enough to carry the weight the thesis currently
places on it, and the failed-null framing should be weakened accordingly.

---

# Addendum 5 (2026-07-30) — the outcome table, and three things this document had not recorded

**Nothing above is edited.** This addendum is written after seven of the eight paired runs
have results. It records the outcomes against the predictions already registered, retires one
registered domain, fixes the status of two domains that were never registered prospectively,
and bounds the screen.

## The outcome table

`Delta rho` = MAIN - C5. Positive favours the per-leaf arm. Decisive threshold
`|Delta rho| >= 0.007`, two steps of the 0.0035 Spearman grid at M = 12. Both tie conventions
reported, always.

| domain | half | drop | screen p | registration | outcome |
|---|---:|---:|---:|---|---|
| psychology | +0.0210 | +0.0210 | 0.000 | registered (Add. 2) | met, both conventions |
| physics | +0.0140 | +0.0140 | 0.004 | registered (Add. 3) | met, both |
| history | +0.0105 | +0.0105 | 0.009 | replication | met, both |
| law | +0.000 | +0.021 | 0.011 | registered (body) | met on **drop only** |
| philosophy | +0.049 | +0.042 | 0.053 | replication | met, both — **and not flagged by the screen** |
| engineering | +0.0035 | -0.0035 | 0.817 | registered null (Add. 2) | **met**: clean null, sign flips between conventions |
| mathematics | -0.064 | -0.007 | 0.289 | registered null (body) | **failed**: verdict for C5 |
| computer science | — | — | 0.751 | registered null (Add. 3) | RUNNING |
| mathematics re-run | — | — | — | registered (Add. 4) | PENDING |

Secondary outcome, GT-agreement MAIN / C5: psychology 85.2 / 84.3, physics 83.8 / 79.8,
history 83.3 / 79.4, law 88.0 / 86.2, philosophy **92.9 / 94.2**, engineering 89.0 / 88.5,
mathematics 94.2 / 94.7.

Philosophy **dissociates** the two outcomes: the largest `Delta rho` in the corpus alongside a
GT-agreement that favours C5. The registration treats GT-agreement as the high-power secondary
and `Delta rho` as the low-power primary, so the primary stands — but the dissociation is a
result in its own right and belongs in the text.

## Retired: chemistry

Chemistry is registered in the body and was never run. It is retired here rather than left
open, so that the registered set and the run set can be reconciled. No prediction is claimed
either way.

## Philosophy and history were never registered prospectively

The body and Addenda 2 and 3 register psychology, physics, chemistry, law, engineering,
mathematics and computer science. **Philosophy and history are not in that set.** They ran
under the identical protocol and are reported as **replications**, not as registered
predictions. This document is the reason that distinction is checkable, so it is stated
explicitly here rather than inferred from the absence of an entry.

## The screen is not a clean predictor, and this document should not be read as claiming it is

Addendum 3 already says the screen is not claimed as a clean predictor. Three measurements now
bound it, and they are stronger than that sentence:

1. It predicts the **domain aggregate** — whether a domain's own ground-truth ranking departs
   from the corpus ranking. It does not predict **within-domain sub-structure**. The
   correlation between screen p and within-domain between-leaf agreement is **+0.072**, which
   is none.
2. It has a **false negative that matters**: philosophy, at p = 0.053, was not flagged and
   produced the largest advantage of any domain.
3. It has a **failed null**: mathematics, at p = 0.289, returned a verdict for C5.

So the screen is a coarse filter on the domain aggregate. It is not a test of whether cells
inside a domain differ, and no claim in the thesis may rest on it as one.

## What the body's superseded reasoning was, and why it does not transfer

Two passages in the body reason from a screen value of `rho = 1.000, p = 1.000` for
mathematics at the 11-model band: that there is "no cell structure for the partition to
exploit", and that math therefore "has little room to differ in either direction". Addendum 3
superseded that p-value (0.289 at 12 models) and math moved -0.064. The argument does not
transfer, and the body's sentence "the math null is what makes a law result attributable to
the partition" no longer holds as written — Addendum 4 supplies the reason.

The body's honest prior, that the comparison would likely come back null with options present,
is falsified in five of seven completed domains. It is left in place. Recording a prior that
did not hold is the point of recording it.

## One bound that must travel with every positive in this table

Per-leaf rankings are near-identical to the domain ranking. On law, leaf-vs-domain Spearman
runs 0.895 to 0.993, against 0.873 to 0.970 for ground truth against itself — the leaf
rankings agree with the domain ranking about as well as ground truth agrees with itself. A
positive `Delta rho` is therefore a **precision gain on one shared ranking**, not discovered
specialisation. Every positive row above is bounded by this, and the bound is not optional.

## Still open

* The reliability constant is fitted at the 11-model band (`c = 2.52`). The arena roster is
  12. The refit at 12 has not been run. The body's obligation to refit stands.
* No confidence interval may be reported anywhere. The Bradley-Terry variance correction used
  `1/K` instead of `1/K^2`; the intervals were never recomputed.

---

# Correction note (2026-07-30, after physics, during computer science)

Descriptive only. Nothing below changes a prediction, a threshold, or a reading
rule, and no text above this line has been altered.

## Addendum 3 quoted the wrong leaf counts

Addendum 3 describes physics as "546 reserved questions, 12 leaves, median leaf
34" and computer science as "208 reserved questions, 3 leaves, median leaf 49".
Those figures come from `reserved_leaf_assignments.csv` aggregated by assigning
each leaf to whichever MMLU-Pro category most of its routed questions carry, then
counting leaves per category. That is a statement about the label composition of
the tree. It is not the quantity the runs use.

The runs scope a domain by tree structure: a held-out question enters the run when
the anchor of its primary leaf is the target domain, irrespective of its MMLU-Pro
label (`TaxonomyBenchmarkService.kt:318-324`). A domain's cells are therefore the
leaves beneath its depth-1 anchor. Under that definition:

    domain            cells   pool     (Addendum 3 said)
    math                 11    334     13 leaves
    physics              10    338     12 leaves, 546 questions
    psychology            8    258
    computer science      6    191      3 leaves, 208 questions
    law                   6    280
    engineering           4    250
    history               4    133
    philosophy            3    167

The structural counts sum to 87 leaves and 3,445 held-out questions, and each one
was confirmed against the run that used it: every arena scheduled comparisons in
exactly that many cells.

## What survives and what does not

Both registered predictions turn on the sign and magnitude of `Delta rho`. Neither
references a leaf count, so both stand unchanged.

The secondary observation registered for physics survives unchanged. It was
registered as "math has the most leaves (13) ... physics at 12 leaves is the
nearest comparison". Under the structural count math has 11 and physics 10. Math
still has the most cells, physics still has the second most, and the gap is one
cell under either count, so the observation is unaffected. It remains registered
with no prediction attached.

## A second, undiagnosed disagreement

Reconciling the two counts surfaced a disagreement between two routing
implementations. The harness that writes `reserved_leaf_assignments.csv` routes
cached embeddings through `TaxonomyTrickler` and assigns all 3,445 held-out
questions. Each arena run re-routes live through `routeToLeavesSoft` and discards
561 as outliers matching no leaf — the same 561 in all eight runs. The remainder
does not shrink proportionally: physics goes 338 -> 237 while psychology goes
258 -> 265, so the paths disagree about composition and not only about coverage.

This is recorded as **NOT DIAGNOSED**. It does not touch the paired contrasts,
which compare two arms over one identical question set drawn by one path. It does
mean that any offline analysis reading the CSV and any arena run are working over
slightly different question sets, and analyses that compare the two directly
should say so.

## Where this is reported

Thesis Section "The Adapted Partition, and How Far It Moves"
(`6_Results.tex`), with the full fourteen-anchor table, the label-agreement
measurement, and this correction stated in the text. The registration above is
left as written.

---

# Addendum 6 (2026-07-31, after every registered run closed) — the batch is closed, and the reported results are not registered

**Nothing above this line is altered.** This addendum closes the two outcomes that
Addendum 5 left open, and records that the batch the thesis reports is a different
batch from the one every prediction above was written against.

## The two open outcomes, closed

| domain | half | drop | steps | registration | outcome |
|---|---:|---:|---:|---|---|
| computer science | +0.006993 | +0.027972 | +2.00 / +8.00 | registered null (Add. 3) | **FAILED, positive** |
| mathematics re-run | -0.080561 | -0.101576 | -23.04 / -29.05 | registered (Add. 4) | **FAILED, negative**, on complete domain-level coverage |

`cs_secured/ratings_cs_paired.db.final`, `math_rerun_secured/ratings_math_rerun.db.final`.
Answer-key agreement: computer science 87.1 / 87.6, mathematics re-run 93.1 / 94.3.

**Two registered predictions failed, not one**, and they failed in opposite directions.
Addendum 4's reading rule applies to the mathematics re-run: outcome 1, the negative
reproduces beyond threshold on a complete graph, so the failed null is not a sparse-graph
artifact and the finding strengthens. Both mathematics runs are reported together, as
Addendum 4 requires.

## The runs the thesis reports are not covered by anything above

After this batch closed, two scheduler defects were found in it. The bootstrap counted its
66-pair floor over the whole domain and put every bootstrap match on the largest leaf, so
one cell per domain reached complete pair coverage and the rest sat at 4 to 33 pairs of 66;
and three runs had unequal arms, down to 0.833. Both were fixed and five domains were
re-run. Those five are what the thesis reports:

    philosophy   +14.00 / +14.00      history      +4.00 / +4.00
    engineering   +3.01 /  +3.01      psychology   +2.00 / +2.00
    mathematics   -2.00 /   0.00

**No prediction in this document covers any of them.** The registrations were written
against the M = 12 configuration, and Addendum 4's registered mathematics re-run is
explicitly at "identical configuration to Runs C-J" — the old scheduler with the
domain-wide bootstrap floor. That run is `math_rerun_secured`, reported above. The
revised-scheduler mathematics run is a further run under a configuration nobody
registered, and it does **not** satisfy Addendum 4.

Two consequences, both of which belong in the thesis text rather than here:

1. Every result the thesis reports as primary is an unregistered replication of a
   registered batch. It agrees with the registered batch on the sign of `Delta rho` in
   every domain both cover, and disagrees on magnitude by 1 to 21 grid steps.
2. **Engineering was the control and it moved.** Its registered null was met cleanly here
   (+1.00 / -1.00, sign flipping). Under the revised scheduler it is +3.01 under both
   conventions. Either the revised logic favours the per-leaf arm, or the run that met the
   null was too broken to detect an effect — arm balance 0.833, one cell at 4 of 66 pairs.
   The registration's own logic says a positive on the control is the signature of an
   artifact. Nothing available distinguishes the two readings, and the text must say so.

No pre-registration can be written for the revised configuration yet: the code that
produced it is uncommitted, so there is no hash to name.

Numbers, provenance and the full caveat list: `docs/newlogic-rerun-record.md`. The
superseded batch: `docs/batch-M12-complete-record.md`.
