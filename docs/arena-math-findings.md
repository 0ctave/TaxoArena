# Math arena on the frozen construction — findings

Run: `experiment_configs/arena_math_frozen.toml`, snapshot `20260727_042523`
(87 leaves, certified, 87/87 rubrics). 8 models, 11 Math cells, 241 judged
reserved questions, 1736 verdicts per condition, MAIN vs GENERIC_JUDGE
(MT-Bench-style domain-agnostic judge). Completed, 0 errors beyond the known
`[ARENA-SE]` inverse-variance floor guard.

## Headline

Both judges recover the ground-truth ordering to within one adjacent
transposition. Aggregate rho ~0.95-0.98 (win-rate); the run's own BT-based
aggregate reports rho = 0.90, tau = 0.79.

**The arena cannot separate the two conditions at n = 8, and that is structural
rather than a power problem.** Spearman at n = 8 is quantised in steps of
6/(n(n^2-1)) = 0.0119, so the observed MAIN-GENERIC gap of 0.024 is exactly two
grid steps — one adjacent swap. Only more MODELS changes this; more judging
cannot.

## The per-cell comparison was underdetermined by construction

Paired on identical (question, model-pair) comparisons:

```
comparisons present in both conditions   1736  (complete overlap)
identical verdict                        1529 / 1736 = 88.1%
disagreements                             207, of which 197 (95%) involve a TIE
                                          on one side
actual winner flips                        10 of 1736  (99.4% agreement)
```

Two judges agreeing on 99.4% of winners cannot produce a detectable ranking
difference at any n, granularity, or domain count. So the per-cell null is NOT
evidence of parity — it is a comparison whose arms barely differ. Rule 0
arriving from a direction the pre-registration did not anticipate: the metric,
the reading, the decisive range and the confound were all fixed in advance, and
none of that protects against arms that are nearly the same treatment.

**Precondition for any future A/B arm: measure verdict agreement FIRST.** It is
one query, and it decides whether the arm is worth 10k calls.

## Win-rate is biased by the adaptive scheduler — use BT

| statistic | mean diff (MAIN - GENERIC) | pos/neg/tied | sign test |
|---|---:|---|---:|
| win-rate | +0.0143 | 5 / 0 / 6 | p = 0.031 |
| **BT theta** | **-0.0016** | **5 / 2 / 4** | **p = 0.227** |

The scheduler over-samples uncertain pairs, so mid-ranked models face harder
average opposition — exactly where an adjacent transposition lives. Win-rate
ignores opponent strength and manufactured a 5/0 result that BT erases. Quote
BT; win-rate is a coarse proxy here, not a substitute.

## The rubric is read, reproduced, and not decisive

Fraction of each rationale's vocabulary also present in that cell's induced
rubric. GENERIC_JUDGE never sees the rubric, so its value is the baseline —
topical coincidence between a Math rationale and a Math rubric:

| condition | rationale length | overlap with cell rubric |
|---|---:|---|
| GENERIC_JUDGE (baseline) | 49 words | 0.138  IQR [0.077, 0.200] |
| MAIN | 54 words | **0.200  IQR [0.115, 0.280]** |

MAIN is 45% above baseline with IQRs offset throughout. The judge ingests the
rubric and reflects it in the justification — and decides the same thing anyway.

**RATIONALE-CONDITIONED, NOT RATIONALE-DRIVEN.** For the alternative ("applies
the criteria and coincidentally agrees") to hold, criteria-guided and
criteria-free judges would have to reach identical winners on 1726 of 1736
comparisons. The simpler reading is that the verdict is determined before the
rubric enters, and the rubric shapes the justification afterwards.

That is a finding about LLM-as-judge methodology, not about this taxonomy.

Caveat: lexical overlap shows REPRODUCTION, not APPLICATION. The rule-ID
citation scheme settles it directly — a cited rule ID cannot arise from topical
coincidence — and it also answers, for free, how many verdicts cite no rule at
all, i.e. are decided on priors. **It changes the verdict schema, so it must
land BEFORE the full-corpus arena.**

## What was retired

The C3 inversion. An earlier validation gave MAIN 0.648 against GENERIC 0.701 —
backwards — on 4 leaves and 553 queries. At full width the ordering is not
inverted; that was a small-sample artifact.

## Scope limit on the mechanism test

The pre-registered prediction (MAIN-minus-GENERIC tracks reusable share, weakest
in enumerative cells) **cannot be tested on Math**. Math's minimum reusable share
is 0.080; the prediction turns on cells <= 0.067, which sit in Other, Health and
Psychology. The decisive range is ABSENT, not underpowered — more Math
comparisons cannot help. Observed slope rho = +0.511, p = 0.109, n = 11: right
direction, measured in the flat region.

## Where link 3 stands

```
coherent cells --causal, p=1.2e-6--> specific rubrics --read, not decisive--> judgments
```

Link 2 is established causally (`docs/prereg_rubric_specificity.md`). Link 3 now
has a MECHANISM for its null rather than an absence of effect.

## Next, in order

1. **Rule-ID citation** in the verdict schema. Distinguishes reproduction from
   application, and counts prior-decided verdicts. Must precede the full-corpus
   run because it changes the schema.
2. **OPTIONS-BLIND arm**, with the reading fixed in advance:

   | rho without options | tie rate | reading |
   |---|---|---|
   | collapses | SPIKES | judge can no longer decide — the task became impossible |
   | collapses | stable | judge was verifying the letter — it was solving |
   | holds ~0.9 | — | judge evaluates reasoning; the rubric null needs another explanation |

   Without the tie-rate control a collapse is uninterpretable. Log refusal and
   malformed-verdict rate too.
3. **Other or Health**, only if verdict agreement there shows the arms differ.

## Data and defects

Data: `experiment_results/arena_math_frozen/`, and `ratings.db` under snapshot
`20260727_042523_{MAIN,GENERIC_JUDGE}`.

`rank_history.csv` is half-wired: `scores` is `0.0000;...` in all 9,906 rows and
`comparisons` reads 0.0 for early rounds. The `ranking` string IS populated, so
per-round orderings and the last-ranking-change mark are recoverable; score
trajectories and ribbons are not. Same class as `iteration_metrics`' zeroed
counters and `wall_ms` — a column declared, written, structurally valid, empty.

`TaxonomyArenaService.compareModels` takes a bare question with no options and
has three callers: the REST controller, the TUI, and
`compareModelsWithAnswerExtraction` — the last builds its own options block, so
it is safe. The arena uses `evaluateWithPrecomputedTraces`, which does pass
options. A `require(...)` guard on the shared entry point would break the two
interactive callers; the fix is a separate entry point with the guard on the
arena-facing one.

## Identification cost, measured

`[ARENA-IDENT]` at 8 models: identification is reached at **7 pairs of 28** — a
spanning tree, as predicted — at 32.9 to 45 comparisons per cell. The cost
VARIES across cells, which clears the void condition in
`docs/prereg_arena_launch.md` (the earlier Math run's uniform 56 was a scheduler
allocation, not a cost). Minimum 32.9 sits in the `<= 40` band: leaf-level
judging is affordable, ~2,900-3,900 calls for 87 cells against a ~10,000 budget.
