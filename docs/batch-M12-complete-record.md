# Batch record — eight domains on the twelve-model roster (M = 12)

> **SUPERSEDED as results, 2026-07-31. This batch is not a baseline.** Every run in
> it was scheduled by a bootstrap that counted its 66-pair floor over the whole
> domain and put every bootstrap match on the largest leaf, so exactly one cell per
> domain reached complete pair coverage and the rest sat at 4 to 33 pairs of 66.
> Three runs also had unequal arms, down to 0.833. Both defects were fixed and five
> domains were re-run; those runs are the results and live in
> `docs/newlogic-rerun-record.md`.
>
> This file is kept for two things: it is what every pre-registration in
> `docs/prereg_generic_judge_baseline.md` was written against, and it is the record
> of what the defects cost. Its numbers are correct for what they are. Do not quote
> them as current results, and do not quote any per-cell quantity from them at all.

**Frozen 2026-07-30, after the mathematics re-run closed.**

Everything below was recomputed from the ranking databases on 2026-07-30 with one
estimator and one script, so the rows are mutually comparable within this batch.
Nothing here is copied from an earlier draft. Cross-batch comparison — cost,
coverage, arm balance, key agreement — belongs in `docs/newlogic-rerun-record.md`
and is not repeated here.

## What this batch is

| | |
|---|---|
| roster | 12 models, 7 families, length band 486–1413 median chars |
| frozen snapshot | `20260727_042523_Headless_Run_Auto_ge` — 154 nodes, 87 leaves |
| held-out pool | 3,445 questions, `is_reserved = 1` |
| domains run | 8 of 14, both arms each |
| conditions | `MAIN` (per-leaf rubric) vs `C5` (generic, partition-free) |
| design | paired: both arms judge an identical question set |
| seed | 42 |
| dates | 2026-07-28 to 2026-07-30 |
| judge | Azure `Mistral-Large-3`, two calls per verdict (position swap) |

Roster: `gemini-3.1-pro_5-shots`, `iask_pro`, `arx_3`, `claude-3.5-sonnet`,
`gpt-4o-2024-08-06`, `deepseek-chat-v2_5`, `gpt-4o-mini`,
`claude-3-5-sonnet-20241022`, `Qwen1.5-72B-Chat`, `Meta-Llama-3-8B-Instruct`,
`Qwen1.5-14B-Chat`, `Meta-Llama-3-8B`.

**Estimator.** Unpenalised pooled Bradley–Terry MM fit over each arm's verdicts,
Spearman ρ against per-model ground-truth accuracy computed on that arm's own
question set. The run exports apply a Jeffreys prior and differ in absolute value;
contrasts are unaffected. `Δρ = ρ_MAIN − ρ_C5`, so **positive favours the per-leaf
arm**.

**Grid.** At M = 12 the Spearman statistic is quantised at 6/(12³−12) = 0.0034965.
Δρ is therefore reported in grid steps as well as raw — grid steps are the only
roster-invariant form, and the pre-registered decisive threshold is *two steps*.

## The batch

Ordered by screen p. Screen p is the twelve-model, 2000-draw, size-matched
permutation value from Addendum 3.

| domain | screen p | registration | Δρ half | Δρ drop | steps h/d | verdict |
|---|---|---|---|---|---|---|
| psychology | 0.000 | registered | +0.020979 | +0.020979 | +6.0 / +6.0 | met |
| physics | 0.004 | registered | +0.014011 | +0.014011 | +4.0 / +4.0 | met |
| history | 0.009 | replication | +0.010508 | +0.010508 | +3.0 / +3.0 | — |
| law | 0.011 | registered | +0.000000 | +0.020979 | +0.0 / +6.0 | met on drop only |
| philosophy | 0.053 | replication | +0.048951 | +0.041958 | +14.0 / +12.0 | — |
| **mathematics (re-run)** | 0.289 | registered null | **−0.080561** | **−0.101576** | −23.0 / −29.1 | **FAILED, negative** |
| mathematics (original) | 0.289 | registered null | −0.063703 | −0.006993 | −18.2 / −2.0 | failed, confounded |
| **computer science** | 0.751 | registered null | **+0.006993** | **+0.027972** | +2.0 / +8.0 | **FAILED, positive** |
| engineering | 0.817 | registered null | +0.003509 | −0.003509 | +1.0 / −1.0 | **met** (clean null) |

### Run geometry

`pairs` is coverage of the 66 possible model pairs at the **domain** level. `per-cell
pairs` is the same count inside each cell, MAIN arm, and is the defect that superseded
this batch: one complete cell per domain and the rest starved.

| domain | n MAIN | n C5 | arm balance | cells | pairs | per-cell pairs (MAIN) | questions | ties M/C5 |
|---|---|---|---|---|---|---|---|---|
| psychology | 3300 | 3288 | 0.996 | 8 | 66/66 | [23, 23, 23, 23, 23, 26, 26, 66] | 235 | 17.6 / 18.0 |
| physics | 1188 | 1055 | **0.888** | 10 | 66/66 | [7×7, 12, 23, 66] | 155 | 33.2 / 41.0 |
| history | 1448 | 1448 | 1.000 | 4 | 66/66 | [12, 12, 28, 66] | 128 | 17.6 / 16.5 |
| law | 2499 | 2479 | 0.992 | 6 | 66/66 | [17, 17, 18, 19, 19, 66] | 246 | 19.8 / 17.8 |
| philosophy | 1319 | 1188 | **0.901** | 3 | 66/66 | [16, 20, 66] | 126 | 22.3 / 21.1 |
| mathematics (re-run) | 2640 | 2640 | 1.000 | 11 | **66/66** | [18, 19×9, 66] | 248 | 24.0 / 30.3 |
| mathematics (original) | 2640 | 2638 | 0.999 | 11 | **20/66** | [20×11] | 250 | 22.0 / 26.6 |
| computer science | 1320 | 1320 | 1.000 | 6 | 66/66 | [8, 13, 15, 19, 25, 66] | 143 | 20.8 / 30.8 |
| engineering | 792 | 660 | **0.833** | 4 | 66/66 | [4, 11, 33, 66] | 113 | 23.5 / 31.4 |

### Absolute ρ per arm

Absolute ρ is **not** stable to three decimals across analysis conventions and
should not be quoted as a headline. Recorded here for completeness only.

| domain | MAIN half | MAIN drop | C5 half | C5 drop |
|---|---|---|---|---|
| psychology | 0.888112 | 0.888112 | 0.867133 | 0.867133 |
| physics | 0.963224 | 0.963224 | 0.949213 | 0.949213 |
| history | 0.795098 | 0.795098 | 0.784590 | 0.784590 |
| law | 0.951049 | 0.965035 | 0.951049 | 0.944056 |
| philosophy | 0.860140 | 0.860140 | 0.811189 | 0.818182 |
| mathematics (re-run) | 0.861648 | 0.833626 | 0.942208 | 0.935203 |
| mathematics (original) | 0.887346 | 0.916084 | 0.951049 | 0.923077 |
| computer science | 0.972028 | 0.986014 | 0.965035 | 0.958042 |
| engineering | 0.898251 | 0.891234 | 0.894742 | 0.894742 |

### Answer-key agreement

Secondary statistic: fraction of decisive comparisons (exactly one side correct)
where the judge picked the correct side.

| domain | MAIN | C5 |
|---|---|---|
| psychology | 85.2% | 84.3% |
| physics | 83.8% | 79.8% |
| history | 83.3% | 79.4% |
| law | 88.0% | 86.2% |
| philosophy | 92.9% | 94.2% |
| mathematics (re-run) | 93.1% | **94.3%** |
| mathematics (original) | 94.2% | 94.7% |
| computer science | 87.1% | 87.6% |
| engineering | 89.0% | 88.5% |

## Provenance

| domain | database | sha256 (16) | run date |
|---|---|---|---|
| psychology | `ratings_psychology_paired.db` | `fcb7885236b408b9` | 2026-07-29 |
| physics | `ratings_physics_paired.db` | `c8c9f50e12b8ef9b` | 2026-07-30 |
| history | `ratings_history_paired.db` | `4e62ce496a845c66` | 2026-07-29 |
| law | `ratings_law_paired.db` | `ba0b459441f67adc` | 2026-07-28 |
| philosophy | `ratings_philosophy_paired.db` | `5aeb577acb7eab5a` | 2026-07-29 |
| mathematics (re-run) | `math_rerun_secured/ratings_math_rerun.db.final` | `3b4e596d1b2c1db8` | 2026-07-30 |
| mathematics (original) | `ratings_math_paired.db.final` | `179256e8ab0483a1` | 2026-07-28 |
| computer science | `cs_secured/ratings_cs_paired.db.final` | `98b19142177e2536` | 2026-07-30 |
| engineering | `ratings_engineering_paired.db` | `0d97e9f60c027757` | 2026-07-30 |

Verdict CSVs and leaderboards for the two secured runs are under `cs_secured/` and
`math_rerun_secured/`; the other six are under `experiment_results/`.

## Caveats that apply to the whole batch

Each is a property of the batch, not of one domain. A later batch that changes any
of them is not directly comparable on absolute values, only on direction.

1. **The threshold is ambiguous at the third decimal.** The pre-registration says
   decisive at `|Δρ| ≥ 0.007, two steps of the Spearman grid`. Two steps is
   0.0069930 — seven millionths *below* the literal 0.007. Computer science landed
   at exactly +0.006993 and the original mathematics run at exactly −0.006993, so
   both sit in the gap between the rule's number and its stated meaning. **One
   ruling must cover both.** This is the strongest single argument for a larger
   roster: at M = 17 the grid is 2.85× finer and no result lands on the seam.

2. **Three runs have unequal arms.** engineering 0.833, physics 0.888, philosophy
   0.901; the rest 0.99–1.00. A thinner C5 arm has a noisier fit and could depress
   its ρ, inflating Δρ toward the thesis's own claim. Measured: correlation between
   C5 deficit and Δρ is +0.34 over all nine rows and +0.18 excluding the confounded
   mathematics original — weak, and engineering (most imbalanced) has the smallest
   effect, which is the opposite of what the confound predicts. So it is **not**
   visibly inflating the batch. Philosophy is the one to flag explicitly: the
   largest positive effect in the batch ran with C5 at 90% of MAIN.

3. **The stopping rule's statistical term was inert.** `budgetPerPair = 7`, while
   the Hoeffding bound needs n > ~20 before it can fire at all, so no pair was ever
   `resolved` — every pair terminated by budget exhaustion. Two further defects were
   found on 2026-07-30: a pair retired by the scheduler (`pairCustomBudgets` set to
   its current count) could never satisfy the stopping policy's global-budget test,
   so leaves containing one were permanently unconverged; and the round log computed
   convergence with the LEGACY branch while the stop decision used the MAIN branch.
   All logged `converged: X/Y` figures for this batch are therefore legacy-path
   numbers and should not be quoted.

4. **No Bradley–Terry interval exists for any row.** The variance computation was
   defective before a dated fix and intervals were never recomputed. The aggregate
   SE additionally came from a query bootstrap that collapses under separation; a
   guard detected the violation on **all eight runs** and substituted the
   inverse-variance value, so the substituted quantity was always what the scheduler
   consumed.

5. **Absolute ρ is not stable to three decimals** across defensible analysis
   conventions. Paired contrasts within a run are safe; absolutes are not.

6. **Cell counts are the anchor-subtree definition** — leaves beneath the domain's
   depth-1 anchor. A rival count (leaf assigned to its plurality MMLU-Pro category)
   gives different numbers and is not used. See
   `docs/prereg_generic_judge_baseline.md`, correction note of 2026-07-30.

7. **Per-cell coverage was broken in every run.** Added 2026-07-31, and the reason
   this batch is superseded. The bootstrap counted its 66-pair floor over the whole
   domain and scheduled every bootstrap match on the largest leaf, so the
   domain-level graph reached 66/66 while individual cells sat at 4 to 33 pairs of
   66 — see the `per-cell pairs` column above. Δρ is fitted on pooled domain
   verdicts and survives. **Every per-cell quantity in this file and in anything
   derived from it does not.** That includes the "8 of its 11 cells individually
   favouring C5" line below, computed on cells holding 18 or 19 pairs of 66, and the
   near-clone per-pair supports quoted in `report/03_Content/6_Results.tex`.

## What the batch says, stated once

- **Four flagged domains, all positive, no sign reversal.** psychology, physics,
  history, law. Magnitudes 3–6 grid steps.
- **Philosophy, unflagged at p = 0.053, gives the largest positive effect**
  (+14 / +12 steps). The screen missed it.
- **Engineering returns its registered null cleanly** (+1 / −1 step, sign flips).
- **Computer science fails its registered null in the positive direction**
  (+2 / +8 steps) on complete coverage and perfectly matched arms.
- **Mathematics fails its registered null in the negative direction, decisively**
  (−23 / −29 steps), on complete *domain-level* coverage and perfectly matched arms,
  corroborated by key agreement (93.1% MAIN vs 94.3% C5). It was also corroborated
  by "8 of its 11 cells individually favouring C5"; that line is **withdrawn** under
  caveat 7 — those cells held 18 or 19 pairs of 66.

So the screen misses in **both** directions on clean runs, and the partition
**costs** something in mathematics while gaining a little in the flagged domains.

## What was chosen, and what it costs

The revised-scheduler batch is reported as the results and this batch as superseded.
The reason is not that the new numbers are better. It is that the defects in this
batch are structural, identified, and fixed: one complete cell per domain with the
rest starved, and three runs with arms as unequal as 0.833. A batch scheduled that
way is not a baseline for anything.

Two costs come with that choice and neither can be argued away.

1. **The new batch is unregistered.** Every prediction in
   `docs/prereg_generic_judge_baseline.md` was written against this one. Promoting a
   second batch after two registered nulls failed here reads as fishing unless it is
   said plainly that no prediction covers the replacement. The fact that blunts the
   charge is that the two failures went in **opposite** directions — computer science
   failed positive at +2.00 / +8.00, mathematics failed negative at −23.04 / −29.05.
   Fishing does not produce failures that cancel. State this wherever the batches are
   compared.
2. **Engineering was the control and it moved.** It is the one clean registered null
   here (+1.00 / −1.00, sign flipping, MET). Under the revised scheduler it is +3.01
   under both conventions. Either the revised logic favours the per-leaf arm or this
   run was too broken to detect a real effect — arm balance 0.833, one cell at 4 of
   66 pairs. Nothing distinguishes the two. Engineering may not be presented as a
   clean positive in either batch.

**The mathematics runs must be reported together.** Addendum 4 fixed this in advance:
*"Reporting only the re-run and discarding the original would be unacceptable under
any outcome; both appear, with the reason for preferring one stated."* Three
mathematics runs now exist — original (20/66 domain pairs, −18.22 / −2.00), the
registered re-run (66/66 domain pairs, −23.04 / −29.05), and the revised-scheduler
run (66/66 in every cell, −2.00 / 0.00). Addendum 4's registered comparison is the
first two. The third is not covered by it.

## Comparability requirements for any future batch

To compare a new batch against this one on more than direction, hold constant:
the frozen snapshot, the held-out pool and its `is_reserved` flags, the paired
design (both arms on an identical question set), the Δρ sign convention
(MAIN − C5), and reporting under **both** tie conventions. Report Δρ in **grid
steps** — with a different roster size, raw Δρ and absolute ρ are not comparable,
and grid steps are.

The revised-scheduler batch holds all of those constant. It does **not** hold the
question set constant: it judges fewer questions per domain (philosophy 99 against
126 here, engineering 66 against 113). The two batches are comparable on Δρ in grid
steps and on sign. They are not comparable on absolute ρ, on key agreement, or on
anything computed per cell.

## Related

- `docs/newlogic-rerun-record.md` — the revised-scheduler batch, which is the results
- `docs/prereg_generic_judge_baseline.md` — body plus Addenda 2/3/4/6 and the
  2026-07-30 correction note
- `docs/math-run-original-record.md` — frozen record of the confounded original
- `docs/stale-results-audit.md` — where every number from this batch still sits in
  `report/`
- `report/03_Content/6_Results.tex` — `tab:c5-all-domains`, the thesis-side table
