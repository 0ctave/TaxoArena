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
